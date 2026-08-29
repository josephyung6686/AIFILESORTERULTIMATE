# Council seat — what ships

Date: 2026-08-21 (overnight)
Seat: **engineering.** What each option costs to build, what it blocks, how reversible it is.
Not this seat: whether the design permits it (seat 1), or what goes wrong when it is wrong (seat 3).

I am allowed to prefer the cheap option and to say when the expensive one is not worth it. Where the
cheap option is cheap now and ruinous later, I say so; that asymmetry is the whole value of this
seat. **Nothing here is decided. Every recommendation names the strongest argument against itself.**

---

## Calibration — what a task costs here, measured

Everything below is estimated against these, not against intuition.

| Part | Tasks | Tests | Planned → green |
|---|---|---|---|
| P4 — evidence shape | 19 | 392 | 08-20 16:47 → 23:51 |
| P5 — extractors | 21 | 343 | 08-20 16:58 → 23:53 |
| P3 — scan | — | 167 | — |
| P2 — eval harness | — | 156 | — |
| Wave-2 caller | — | 22 | 08-21 01:38 |

Two numbers that matter more than the table:

- **The integration tail.** After P4 and P5 both went green at 23:5x, there were **eight fix commits
  between 00:07 and 02:21** — `config_fingerprint` computed twice, one content hash in two spellings,
  a published emit order that was uuid4 order, an empty `raw_value`, two dead paths. None of those
  were findable from unit tests. Budget **~35% of a part's build again** for the joins.
- **The suite is 1,237 tests in 9.93 seconds.** Trying a decision and reverting it costs ten seconds.
  This is the single most important fact about reversibility in this repo, and it means **almost
  nothing here is a one-way door because of code.** The one-way doors are one-way because of
  *stored data under §8.2's no-delete rule* and *vocabulary frozen into a join key*. Every time I
  call something one-way below, that is why.

So: **P6 (27 tasks) ≈ 1.3 × P5. P7 (22 tasks) ≈ 1.05 × P5.** Together ≈ 2.5 part-nights plus a
larger integration tail than P4/P5 had, because they join to more built surface.

**Both counts are low.** Round 2's *Missing tasks* table names **eight** things P6 must build that no
task covers (schema creation, `tests/p6/conftest.py`, the pass-record table, `ResolveResult`, the
privacy/model injection points, the §3.2 skeleton fixture, the writer check, the targeted-OCR entry
point) and **three** for P7. And Task 26 is three tasks, not one (see D5). Realistic:
**P6 ≈ 33–35 tasks, P7 ≈ 24–25.** Read every task count below against that.

---

## D1 — the field catalogue, how far open

### What exists

- P6 SPEC Done-means 2 closes the catalogue to the six §3.11 universal fields + `download_session` +
  the six §3.11 domain rows — ~37 fields — *"and no field outside them"*.
- `planning/domains/*.json`: **560 entries, 2,233 distinct field names**, mean 6.5 fields per entry.
  Provenance: **16 `design`, 115 `inference`, 429 `proposal`**. Three-quarters of the catalogue is
  explicitly *not derived from the design*.
- P6 Task 25 currently asserts *"catalogue 01 is not imported anywhere in `facts`"* — the closed
  reading actively forbids the catalogue at run time.
- Nothing in `src/` loads any of it. `src/facts/` does not exist.

### Cost per option

| Option | Tasks touched | Files | What has to be re-done |
|---|---|---|---|
| **(c) Keep closed, demote catalogue to routing aid** | Task 2 | `P6/SPEC.md` | **Not actually available as written.** Done-means 2 forbids `authored_by`, which Done-means 13 and 22 require, and forbids `capture date`, which Done-means 5 requires. The minimum edit to (c) *is* (b). |
| **(b) Narrowly open — §3.11 + §3.8's four + `capture date`** | **Task 2 only.** `FIELD_ROWS` grows ~37 → ~42 | `src/facts/fields.py` (unbuilt), one Done-means sentence | **Nothing.** P6 is unbuilt. Task 25's catalogue-exclusion guard stays true. |
| **(a) Fully open — §3.11 as seed, 560 domains as growth** | Task 2 (rewritten as a loader, not a literal), Task 13 (`DOMAIN_FIELDS` 6 keys → 560), Task 25 (the catalogue guard **inverts**) | + a generated `src/facts/catalogue.json` and a build step | Task 2's shape, Task 25's assertion. Also makes **D6 blocking** — you cannot load a catalogue that spells one concept two ways. |

The argument that (a) is cheaper than it looks, stated fairly: opening the catalogue does **not**
create 2,233 fields with no writer. Under §3.5/§3.6 a domain schema is an *allow-list for the LLM and
the validator*, not a set of slots something must fill. So (a) is one writer with a 2,233-entry
allow-list, and Task 13's *code* cost is flat — only its test cost grows.

The argument that (a) is more expensive than it looks: 429 of 560 entries are `provenance: proposal`.
Loading them as the §3.6 validator's allow-list ships 429 unratified domain decisions, and **a wrong
allow-list is a silent permission, not a failure** — it never produces a red test.

### One-way or two-way

**Two-way in the opening direction; one-way in the closing direction — which is the opposite of what
the SPEC assumes.**

Adding field rows later is additive: existing facts keep resolving, and the cost is Task 2's literal
plus Task 13's tests. Going the other way — 2,233 fields down to 42 — means every fact already
written against a removed field must be superseded or orphaned, and §8.2 forbids deleting them.

**Therefore start narrow and grow.** That is the rare case where the cheap option and the reversible
option are the same one.

### What it blocks

P6 Task 2 (second task in the part) and Task 13. Under option (a) it also blocks on D6 first.

### Recommendation

**(b), narrowly open.** Restate Done-means 2 as *"§3.11's universal set + `download_session` +
§3.11's six domain rows + §3.8's four role fields + `capture date`; extensible only by a ratified
edit to the authored table, never at run time."* The last clause preserves Done-means 3 under all
three options and is the part that actually matters.

Cost: one paragraph, before Task 1.

### Where my seat is weak on this one

The 560-domain catalogue is 7.4MB of authored, cited work with a passing `check.py` gate. Under (b)
it becomes a routing aid consumed by nobody until **P10** — four parts away — and artifacts consumed
by nobody rot. By the time P10's template menu (§5.3, *"one or more domain templates"*) needs it, its
citations will be stale against a design that has moved, and re-verifying 560 entries then costs far
more than wiring them now while they are fresh and their authors' reasoning is on the page.

I do not think that outweighs putting 429 unratified `proposal` domains behind the §3.6 validator.
But it is the real cost of my recommendation and it is not small.

---

## D2 — `sensitivity`: one record or three

### What exists

- `files.sensitivity_state` — column present in P1's `FILES_DDL`, **no writer anywhere in `src/`**.
- `bundle_file_entry.handling_class` — was being fed P1's `sensitivity_state`; now a literal `None`
  (`src/orchestrator.py:311`).
- Three spellings live: `sensitivity` (P7 SPEC), `sensitivity status` (§3.11, P6 universal field),
  `sensitivity_state` (P1's column).
- P7 Task 4 is **already written for the one-record answer**: a `SensitivityFacts` protocol, an
  injected `SensitivityStateWriter`, and `mirror_state`.

### Cost per option

| Option | P6 | P7 | P1 | Orchestrator |
|---|---|---|---|---|
| **(i) One record — P6's `file_facts` authoritative, P1's column a mirror, P2 reads P6** | **0 new tasks.** `sensitivity status` is already a §3.11 universal field, so Task 2 is unchanged; add one sentence saying P6 owns the row and does not write the value (round 1 F-2 already asks for exactly this) | **Task 4 as written. Zero delta.** | publish `set_sensitivity_state(...)` — a 4-line body, exact twin of `set_extraction_status` at `src/database_agent/files_table.py:147`. **~15 lines + 3 tests** | one line at `:311` reads from the gate |
| **(ii) Three records, reconciled** | +1 task | **+3 tasks** (three writers + a reconciliation rule with no design source) | same | every consumer — P2, P8, P9, P10, P11, P13 — must learn which to read |
| **(iii) Delete `files.sensitivity_state`** | 0 | Task 4 loses `mirror_state` | DDL edit + `FILES_COLUMNS` + P1 tests, ~1 hour | P2's `handling_class` still needs a source |

(ii) is the defect class `22-p1-p7-connection-contract.md` §3 names as the one that has cost this
project the most, reproduced deliberately. I would not build it.

### On the sequencing the brief asked about

**P6 shipping first does not force P6 to write the value.** The seam is a protocol
(`SensitivityFacts`, injected, no default) with a test double at `tests/p7/p6_fixture.py`. So
**21 of 22 P7 tasks build with P6 absent**, and P6 ships with `sensitivity status` in the catalogue
and no writer — exactly the discipline round 1 F-2 asks it to state plainly. The order of building is
free. What is *not* free is the **field key spelling**, and that lands in P6 Task 2.

### One-way or two-way

- **The record choice is close to one-way.** Classifications written against the wrong authority
  accumulate under §8.2's no-delete rule; reversing means superseding every one and re-deriving.
- **The spelling is two-way today and one-way the moment P6 Task 2 runs**, because `field_key`
  becomes the join key that P7, P8, P9, P10 and P13 all read.

### What it blocks

P6 Task 2's row for this field. P7 Task 4's protocol shape (but not P7's build).

### Recommendation

**(i).** Plus two things the plans do not currently say:

1. **`mirror_state` is a validator, not a translator** — `files.sensitivity_state` holds a
   `HANDLING_CLASSES` member verbatim. Round 3 A10 is right that a *translator* silently creates a
   fourth spelling. And P7 Task 22 must assert **the value**, not non-nullness: a non-null assertion
   is satisfied by restoring exactly the `handling_class = file_row["sensitivity_state"]` line that
   was removed on 08-21, which is the shortest edit that makes the test green.
2. **One field key: `sensitivity status`** (§3.11's, P6's, and the one already in the universal set).
   P1's column stays `sensitivity_state` because **SQL column names and field keys are different
   namespaces** — P1's columns are snake_case throughout — so this costs no migration.

### Where my seat is weak on this one

Point 2 is me letting two spellings survive on a namespace technicality, to avoid a migration. On a
pre-1.0 product with zero users that migration costs approximately nothing — a `db.py` DDL edit,
`FILES_COLUMNS`, and P1's tests, under an hour today. And the connection contract's own §6 check 5
says *"exactly one part writes each concept: one fingerprint, one hash spelling, one extractor name
per engine, one sensitivity record"* — a rule which arguably extends to spelling, and which exists
precisely because "they're different namespaces" is what people said the last four times.

If Joseph wants one spelling everywhere, **do it now.** It will never be cheaper than tonight.

---

## D3 — deletion versus append-only

### What exists, verified

- **`events` is append-only at the substrate.** Three triggers — `events_no_update`,
  `events_no_delete`, `events_no_replace` (`src/database_agent/db.py:148-154`) — and an authorizer
  hook that refuses `SQLITE_DROP_TRIGGER` on them (`:63-72`). This is enforced, not conventional.
- **`evidence` and `text_units` — the tables that actually hold a scanned passport's OCR text and its
  raw values — have no triggers and no delete path.** `grep "DELETE FROM" src/` returns **nothing**.
- Their entire reader surface is **one module**: `src/evidence_shape/store.py`, **10 SQL sites**.
- P6's `file_facts` already carries `active`, `preferred`, `supersedes` / `superseded_by`.

### Cost per option

| Option | P1 | P4 | P6 | P7 | P2 |
|---|---|---|---|---|---|
| **(A) Append-only wins; nothing deletes** | 0 | 0 | 0 | **0** — Task 15 already ships `delete_derived` raising `UnratifiedResolution`; it just becomes permanent | 0 |
| **(B) Tombstone derived projections; `events` append-only forever** | 0 | a tombstone column on `evidence` and `text_units` + filter at **10 sites in one module** + a blanking transform. Genuinely small **today** | ~free **if Task 4 builds the column in**; a migration + every fact reader after P6 ships | Task 15 implements instead of refusing — same task count | **unsolved, see below** |
| **(C) Real deletion of derived tables** | — | — | — | — | strictly worse than (B) — same work, and §8.2's reconstruction is lost. Ignore |

**The part nobody has costed.** `run_wave2` copies `text_units` into a sealed P2 bundle
(`src/orchestrator.py:317-318`). **A tombstone in P4 does not reach a sealed bundle.** So under (B),
`delete_derived` is a lie for any corpus that has ever been bundled — which is every corpus, because
bundling is unconditional in the caller. Either bundles are tombstoned too, or the right is
partial and must say so. P2 is built; this is retrofit work on a shipped part.

### One-way or two-way

- **(A) now, (B) later is two-way with a bill that grows linearly in parts shipped.** The tombstone
  costs one module today; one module + a P6 migration after P6; one module + P6 + P8/P9/P10's readers
  after those.
- **The genuinely one-way component is P2's sealed bundles.** Every bundle sealed before the answer
  is a copy of derived text that no later tombstone reaches. Bundles are being sealed **today**.
  So the cost of deferring D3 grows **with every scan anyone runs**, not with every part shipped.
  That is unusual and it is the reason this one cannot sit indefinitely.

### What it blocks

**P7 Task 15 only — 1 of 22.** Nothing in P6. The plan is honest about this and it is correct.

### Recommendation

**Ratify the direction now; defer the implementation.** Specifically: *"derived projections may be
tombstoned; `events` is append-only forever; a tombstone hides a row from every read and blanks its
`raw_value` / `text`."* Then add the column to P6 Task 4's `file_facts` DDL and to P4's `evidence` /
`text_units` **before P6 starts**, while P4's reader surface is still one module. Leave
`delete_derived`'s *behaviour* as Task 15's refusal until P13 exists to drive it.

That buys the cheap structural half now and defers the expensive semantic half — and it stops the
bundle problem getting worse while you decide.

### Where my seat is weak on this one

I am proposing to add a column nothing writes. That is the exact defect class this project has been
bitten by **five times** — `extraction_status_by_tier`, `extraction_routing`, `sensitivity_state`,
`Dispatched.sensitivity`, `runs_dataless` — and the connection contract §5 was written specifically
to forbid it.

The honest counter: **don't add the column.** Take the migration later, because a migration on a
product with no users is cheap, and a writer-less column is a proven liability that has cost this
repo real defects. If Joseph takes that argument, the answer is (A)-for-now with (B) ratified as the
direction and P7 Task 15 keeping its refusal — and I would not fight it. The one thing I would still
insist on either way is the P2 bundle question, because that one is being made worse by the day.

---

## D4 — jurisdiction at launch

### What the catalogues actually say, measured

- Of 560 entries, **29 carry a `jurisdiction` schema field**; **124 mention jurisdiction anywhere**.
  Concentrated: government 34, law 28, trades/property 24, finance 21, career 7.
- Country names across all 560 entries: England 8, UK 8, United Kingdom 7, EU 6, Canada 2, Ireland 2,
  **United States 1**, Scotland 1. **The catalogue is essentially jurisdiction-neutral** — it names
  structures, not statutes. (The UK-over-US skew is a fact about the authors, not the market.)
- The seven deferred gazetteers (`planning/deferred-catalogues/`, 329 rows — 115 tool producer
  strings, 80 archive markers, 70 screen resolutions, 37 camera filename patterns, 22 citation
  identifiers, 5 sensor ratios) are **entirely jurisdiction-free**: device and software facts.

### The structural point that decides the cost

**What varies by jurisdiction is values, not fields.** `jurisdiction = England & Wales` is a value.
§3.12: *"The system may create new values when it sees a new course, project, company, university, or
event, but it should not invent new fields automatically."* Values auto-create (P6 Task 3,
`ensure_value`); fields do not.

So the cost of one additional jurisdiction is:

| | Cost |
|---|---|
| Field catalogue | **0.** No new fields. |
| P6 code | **0.** Task 25 already forbids a gazetteer as a module-level constant in `facts`; every gazetteer is injected. A jurisdiction is a data file handed to an injected matcher. |
| Recognition | one new deferred catalogue, in the shape of the seven that exist — 22–115 rows, roughly one agent-session apiece. |

### One-way or two-way

**Two-way, and unusually cleanly so** — the design's own value/field split (§3.12) is what makes it
so. The only way to make it one-way is to put jurisdiction-specific names into the *field* catalogue
(a `w2_tax_year` field). The current catalogue has not done that, in any of 560 entries.

### What it blocks

**Nothing in P6 or P7.** It blocks the completeness of tax/legal/government *recognition* rules,
which are P6 Task 10's injected rule set — injected with no defaults, so P6 builds without them.

### Recommendation

**Do not decide the launch list. Ship one jurisdiction's gazetteers and state the rule.** Pick
whichever matches Joseph's own corpus. Record in the SPEC that `jurisdiction` is a value field and
that gazetteers are injected per deployment.

**One line to add now, and it is the only part that is urgent:** `jurisdiction` is never a
destination dimension. See below for why.

### Where my seat is weak on this one

"Values auto-create, so it's free" holds only while the *templates* don't branch on jurisdiction.
§5's folder templates (P10) may well want `jurisdiction` in a `dimension_order` — and a tree shape
that includes it for one launch jurisdiction and not another is a **tree-shape decision, which is
P10's one-way door**: a frozen tree is what P12 undoes. So D4 is two-way in P6 and potentially
one-way in P10. That is why the never-a-dimension line is worth writing tonight even though the
jurisdiction list is not.

---

## D5 — the `no_usable_facts` pass structure

I read `src/orchestrator.py`, `src/extractors/dispatch.py` and `src/extractors/ocr_policy.py`, and
I ran the change against the repo's own fixture. This section is evidence, not estimate.

### Verdict: it is an insertion, not a rewrite — and the insertion as specified is broken

### The insertion half — why it is genuinely small

- **`no_usable_facts` is consulted in exactly one place**: `ocr_policy.text_layer_state`
  (`src/extractors/ocr_policy.py:101`), reached only from `dispatch.extract`'s PDF branch
  (`src/extractors/dispatch.py:121-127`). `image_ocr_decision` never consults P6.
  `text_layer_absent` returns *before* the call. **One branch of one extractor family.** The plan's
  own claim — *"the split is narrower than it first looks"* — is correct and I verified it.
- **Loop 1 is today's loop verbatim.** Routing, `record_routing_decision`,
  `record_sensitivity_signals`, and stage 2b (dataless) are all untouched.
- **Loops 2 and 4 are calls into P6's own resolver** — P6-internal, not orchestrator work.
- **Loop 3 is ~25 new lines.**
- **Stage 4 (P2 bundle) is free**: it already iterates `written`, so loop 3's OCR runs land in the
  bundle provided loop 3 precedes it.
- **Test blast radius, counted:** `no_usable_facts` appears in **3 source files** and **4 test files**
  (`tests/p5/test_p5_ocr_policy.py` ×7, `tests/wave2/test_wave2_orchestrator.py` ×6,
  `tests/p5/test_p5_no_invention.py` ×2, `tests/p5/test_p5_dispatch.py` ×1). The suite finds a wrong
  guess in ten seconds.

### The broken half — five defects the plan does not name

**1. `FactPassNotRun` becomes `completeness = failed`. Executed.**

Task 26 says loop 1 injects a verdict that raises. `_extract_one` (`src/orchestrator.py:151-158`)
re-raises only the two `admit()` refusals and converts **everything else** into a `failed_result`.
I ran the repo's own Wave-2 corpus fixture (`syllabus.pdf`, text-bearing; `notes.md`) through
`run_wave2` with a raising verdict:

```
filesystem.record | filesystem | complete
filesystem.record | filesystem | complete
text.structured   | native     | complete
pdf.text          | native     | failed          <-- every text-bearing PDF

files.extraction_status_by_tier:
  notes.md      {"filesystem": "complete", "native": "complete"}
  syllabus.pdf  {"filesystem": "complete", "native": "failed"}
```

`run_wave2` returned normally and sealed a bundle. Nothing raised. §8.6's progress line now reports
every text-bearing PDF unreadable, and P7 Task 3 maps `failed` toward `unreadable_unclassified`, so
the gate denies the document corpus. **Task 26's own test — *"run a full corpus without it firing"* —
passes while this is happening**, because nothing escapes `run_wave2`.

Round 3 A1 reports the same defect. I reproduced it independently before reading A1; treat that as
two confirmations, not one.

*Cheapest correct fix:* loop 1 must not hand `extract()` an **armed** verdict at all — keep
`TARGETED_OCR_UNAVAILABLE`'s behaviour (a callable that structurally cannot say "broken") and put the
raise-on-unrecorded-pass guard in P6's `usable.py`, where loop 3 calls it directly. **Zero extra
lines in loop 1.** What changes is Task 26's *test strategy*, not its size: the mechanical proof
becomes a spy asserting the resolver's verdict object is never the one passed to loop 1.

**2. Loop 3 has no way to run OCR alone.** `_ocr` is module-private
(`src/extractors/dispatch.py:86`). Re-calling `extract()` with a true verdict re-runs `extract_pdf`
and produces a **second `pdf.text` run at an identical §3.4 cache key**. Fix: promote `_ocr` to a
public `extract_ocr_only(...)`. **~3 lines in `dispatch.py`** — which contradicts the plan's *"what
does not change: … `dispatch.py`"*.

**3. `set_extraction_status` replaces the whole map.** `src/database_agent/files_table.py:166-169` is
`UPDATE files SET extraction_status_by_tier = ?`. Loop 3 calling it with
`extraction_status_by_tier([ocr_run])` writes `{"ocr": …}` and **erases the `filesystem` and `native`
entries loop 1 wrote**. Fix: loop 3 recomputes over the file's full run set. `runs_for_content`
exists (`src/evidence_shape/store.py:85`) but returns `ExtractionRun` dataclasses while
`extraction_status_by_tier` indexes `run["analysis_tier"]`, so it needs a mapping adapter.
**~5 lines.** **Nobody has named this one.** If it ships wrong, `files.extraction_status_by_tier`
silently loses two tiers on exactly the files that needed OCR — a column that is wrong only on the
interesting rows.

**4. Two more, from round 2, which landed while I was writing this — and which I did not raise.**

- **B-14.** Task 26 says the Wave-2 test file *"stays green"*. It cannot: **three of its tests encode
  the pre-restructure contract** (`test_the_absent_p6_verdict_is_named_rather_than_faked`,
  `test_the_verdict_parameter_has_no_default`, `test_a_real_verdict_is_still_accepted`, at
  `tests/wave2/test_wave2_orchestrator.py:487-513`) and must be deleted or inverted — and
  `TARGETED_OCR_UNAVAILABLE` must be **deleted**, which its own docstring already instructs
  (*"When P6 lands this is deleted, not edited"*).
- **B-15.** The one line that closes the P7 seam — `handling_class=None` at
  `src/orchestrator.py:311` — sits inside the loop Task 26 declares *"unchanged"*, and **no task in
  either plan owns changing it.** P7 Task 22 *asserts* the change with only a test file in its
  `Files:` list.

### Honest total — revised upward

My first count was **1 task, ~50 lines**. Having read round 2, **that is too low and I am correcting
it.** Round 2's read is the better one, and it splits Task 26 three ways:

| | Work |
|---|---|
| **1. P5 surface** | a public native-only entry and a public targeted-OCR entry in `extractors.dispatch`; renegotiates the *"`dispatch.py` does not change"* constraint |
| **2. The rewire** | four loops, parameter swap, **tier-map merge**, the `signals` guard, the Wave-2 file's deletions and inversions, and the `handling_class` line |
| **3. The order proof** | `tests/p6/test_p6_pass_order.py` — including *"with `ocr_engine is None`, no duplicate runs"*, the assertion that would have caught defect 2 |

So: **3 tasks, not 1.** ~50 net new lines in `src/orchestrator.py` is still about right, plus ~15 in
`dispatch.py`, plus edits and three deletions across 4 test files. Against the P4/P5 calibration
(≈16–20 tests per task), that is **~50 tests, not ~15**.

It is still an **insertion, not a rewrite** — loop 1 is today's loop verbatim, and the diagnosis in
P6's preamble rule 5 is correct and well argued. What is under-specified is the *diff*, not the
decision. But it is an insertion whose **specified test strategy proves nothing**, and that is worse
than a rewrite whose tests are honest.

**Three independent reviews — round 2 (B-1, B-2), round 3 (A1), and my own execution — found the
same defects without seeing each other.** That convergence is itself the strongest evidence that the
four-pass *shape* is right and only the contract is missing.

### One-way or two-way

**The code is two-way; the data it produces is one-way.**

`run_wave2` is not a part, owns no vocabulary, has 22 tests, and the suite runs in ten seconds — the
loop can be reshaped again next week for nothing. But what it writes is `extraction_runs` rows and
`files.extraction_status_by_tier`, and a wrong shape produces the `native: failed` rows above, which
under §8.2's append-only discipline are not rewritable. **Do not run a real corpus through a
half-wired pass structure.** That is the entire risk in this decision.

### What it blocks

Nothing can start on it — Task 26 is last in P6 by design, and it is the one file P6 does not own. It
blocks *shipping* P6, not building it. It also collides with **P7 Task 22** (round 3 A17): both plans
edit `run_wave2` and neither mentions the other.

### Recommendation

**Take the four-pass structure. Reject its stated guard mechanism. Split the task three ways.**
Loop 1 keeps a structurally-safe verdict; the raising guard lives in P6 and is proven by a direct
unit test plus an orchestrator spy, not by "run a corpus and see nothing fire." Schedule Task 26's
three parts and P7 Task 22 as **one diff with one owner** against a green suite — and give
`src/orchestrator.py:311`'s `handling_class` line an owner in that diff, because today nobody has it.

### Where my seat is weak on this one

I am calling this small partly because `readers.ocr_engine is None` in every test today, so loops 3
and 4 are no-ops and the restructure is "provably free." **That is exactly the argument that made
§2.7's OCR path dead for a week** — a path no real image could reach, green in every test.

A change that is free because the code it adds never executes is not a change that has been tested.
The strongest counter to my "insertion" verdict: Task 26 ships four loops of which two have never
run, and the first real OCR deployment finds the defects. If Joseph wants that risk gone, the honest
scope is Task 26 **plus a fake OCR engine wired into the Wave-2 fixture** — another half-task nobody
has costed, and I think it is worth costing.

---

## D6 — field naming

### Measured across `planning/domains/*.json`

- 560 entries, **2,233 distinct field names**.
- **914 spaced · 959 snake_case · 360 single-word** (convention-neutral).
- A snake→spaced pass touches **272 of 560 entries in 7 of 13 files**: 959 distinct names,
  **1,346 field-slot edits**.
- **124 of those renames collide with an existing spaced name.** `record_type` meets `record type`
  (30 entries), `issue_date` meets `issue date` (5), `document_type` meets `document type` (3),
  `account_type` meets `account type`, and 120 more. **So the rename is not purely mechanical — it
  merges 124 pairs**, and someone must confirm each pair is one concept. I would size that at one to
  two hours. It is also the *point*: those 124 collisions are the proof that two conventions are
  naming the same concepts twice.

The named conflicts, quantified:

| | Count in entries |
|---|---|
| `subject` | 6 |
| `course` | 6 |
| `capture date` | 6 |
| `capture year` | 5 |
| `creation date` | **0** |
| `document type` / `application document type` | 3 / 4 |
| `artifact type` | 43 |
| `record type` | 30 |
| `project` | **78** — B6.5's "one project domain or four" question, quantified |

### Cost per option

**Now:** one script + 124 confirmations + re-run `planning/domains/check.py`. **Zero code cost** —
nothing in `src/` spells a domain field name, because `src/facts/` does not exist.

**After P6 ships:** P6 Task 2's `FIELD_ROWS` is a module-level Python literal, so the table edit is
trivial — but **`field_key` is the join column in `file_facts`**, read by P7 (`SensitivityFacts`),
P8 (Task 17's active-field allow-list), P9, P10's `dimension_order`, and P13. Calibrating from
P4/P5: renaming a vocabulary after a part is green is what `config_fingerprint` and the two OCR-name
spellings cost this project — **eight fix commits over 2h15m on the night of 08-21, all of them one
concept in two spellings.**

### One-way or two-way

**Two-way today. One-way the moment P6 Task 2 runs.** Not because a rename is hard, but because
`field_key` becomes a *stored join key under §8.2's no-delete rule*: facts written as `record_type`
cannot be deleted, only superseded, and a superseded fact whose field no longer exists is unreadable.

**This is the clearest one-way door of the six, and it is also the cheapest to close.**

### What it blocks

P6 Task 2 — the **second** task in the next part anyone builds. Also blocks D1 option (a) entirely.

### Recommendation

**Rule now, in one sentence, before Task 1:**

1. **Field keys are spaced lowercase.** §3.11's table is the design's own spelling and the design wins.
2. **SQL column names stay snake_case.** Different namespace; no conflict; no migration.
3. **Where prose and table disagree, prose wins for a fact name and the table wins for a domain row.**
   That resolves `capture date` (prose, worked example in §3.1 and §3.2) over `capture year` (table,
   one row) — and unblocks Done-means 5, which currently requires a field Done-means 2 forbids.

### Where my seat is weak on this one

**Clause 3 does not settle `subject` vs `course`, and I should not pretend it does.** The honest
count: prose §3.1 / §3.2 / §3.12 says `subject` (3 sections); prose §3.5 (*"becomes a **course**
fact"*) and §5.4's template `school → term → course → work type` say `course` — and so does §3.11's
table, and so does the entire Academic catalogue entry (`acad.course-enrollment`'s `design_cite`
quotes §3.5 directly). **The prose is not unanimous. It is 3–3.**

So this one is a genuine tie and **my seat cannot break it on cost, because both cost the same.**
What my seat *can* say: pick either, in the next sentence you write. The cost of picking is zero.
The cost of not picking compounds across 560 catalogue entries today and hardens into a stored join
key at P6 Task 2.

---

## The order to answer these in

### The blocking graph

```
D6 (naming)  ──blocks──>  D1 option (a)
             ──blocks──>  P6 Task 2          <- second task of the next part built
D2 (sensitivity) ─blocks─> P6 Task 2's row, P7 Task 4's protocol shape
D1 (catalogue)   ─blocks─> P6 Task 2, P6 Task 13
D3 (deletion)    ─blocks─> P7 Task 15 only (1 of 22)  ·  P6 Task 4's DDL is the cheap moment
D5 (passes)      ─blocks─> nothing to start; it is P6's LAST task
D4 (jurisdiction)─blocks─> nothing
```

### Answer in this order

1. **D6 — first, and it is one sentence.** Cheapest to answer, one-way door with the nearest
   deadline, and it gates D1's expensive option. **Answer this one even if you answer nothing else.**
   (Including the coin-flip on `subject` / `course` — the coin flip is the answer.)
2. **D2 — second.** It sets a field key, so it must follow D6, and it sets a protocol shape. It is
   the concept the connection contract names as this project's most expensive defect. One sentence:
   one record, P6 owns the row, P7 owns the value, P1 mirrors it as an identity.
3. **D1 — third.** Needs D6's rule to be expressible. Narrow-open now; that is the reversible
   direction as well as the cheap one.
4. **D3 — fourth, as a direction, not an implementation.** Ratify tombstone-derived /
   append-only-events so P6 Task 4 can build the column, and leave `delete_derived` refusing. If you
   would rather not build a writer-less column, say so — that answer costs nothing at all. But say
   *which*, because P6 Task 4 is early. And rule on P2's sealed bundles either way.
5. **D5 — fifth, and mostly not yours.** Take the four passes; the three corrections are engineering's
   to make. What *is* yours is one scheduling call: **P6 Task 26 and P7 Task 22 are one diff with one
   owner**, because both edit `run_wave2` and neither plan knows the other does.
6. **D4 — last.** Ship one jurisdiction's gazetteers, keep `jurisdiction` a value, and write the one
   line that matters tonight: it is never a destination dimension.

### What can safely be deferred, and for how long

| Decision | Defer until | Cost of deferring |
|---|---|---|
| **D4** | P10 is planned — four parts away | **Zero**, provided the never-a-dimension line is written now |
| **D3's implementation** | P13 exists to drive a delete | Zero — but its **direction** must land before P6 Task 4, and the P2 bundle question gets worse with every scan run |
| **D5** | P6's Task 26, i.e. the end of P6 | Zero to build. Non-zero to *run*: do not put a real corpus through a half-wired pass structure |
| **D1, D2, D6** | **Cannot be deferred past P6 Task 2** — the second task of the next thing anyone builds | All three become one-way doors the moment `field_key` becomes a stored join key |

### The one thing to take from this seat

The suite is **1,237 tests in 9.93 seconds**. Every decision here can be tried and reverted inside a
coffee break *as code*. What cannot be reverted is **data written under §8.2's append-only rule** and
**vocabulary frozen into a join key**.

Every one-way door in this list is a one-way door for one of those two reasons and no other. So the
practical rule: **answer the three that become join keys — D6, D2, D1 — and let the other three be
discovered by building.**

# P4 / P5 / catalogue recheck — after 2026-08-20 ratifications

Date: 2026-08-20 (evening)
Status: **Contracts mostly frozen. PLANs still contain superseded paragraphs that would ship the old world.** Catalogues are a serious v1 data pack, not stubs. They do not make a perfect database sorter by themselves.
Supersedes the execute-headline of [`15-p4-p5-plan-robustness.md`](15-p4-p5-plan-robustness.md). That file’s four original blockers are largely closed in the *task bodies*; this file is about what the edits missed.
Ran this session: `python3 -m pytest tests -q` → **468 passed**; `planning/deferred-catalogues/checks/run_all.sh` → **all PASS**.

Source of truth remains [`00-database-agent-product-design.md`](00-database-agent-product-design.md). Joseph’s 2026-08-20 answers live in the P4/P5 SPEC ratification tables. Those tables win over any PLAN Self-Review, any leftover Open-questions paragraph, and [`15-p4-p5-plan-robustness.md`](15-p4-p5-plan-robustness.md).

---

## Verdict

The product is still a **perfect-sorter design with a Wave-1 identity layer and a Wave-2 evidence contract**. P4/P5, after the answers, can freeze the *shape of seeing*. They cannot yet *sort*. Sorting is P6–P13 (facts, handling, grouping, placement). Catalogues make P5 see more without inventing; they do not create `subject = BUSIB 4300`.

| Surface | Freeze? | Execute? |
|---|---|---|
| P4 SPEC ratification table | Yes | — |
| P4 PLAN Tasks 2, 15 (OQ2 closed, hash owns the set, nine completeness values in `COMPLETENESS`) | Yes, these bodies match the answers | **Not yet** — Task 2’s `OPEN_QUESTIONS` and the Self-Review still assert the pre-answer world |
| P5 SPEC (B1 Apple Vision, B6 ship XLSX/PPTX, B7 no invented OCR threshold, C4 `dataless`) | Yes | — |
| P5 PLAN Tasks 1–21 | Shape-correct extractor package | **After P4 is in `src/evidence_shape/`**, and after the five hygiene items below |
| Seven catalogues | v1 data pack; checks green | Inject at P5/P6 wiring time. Do **not** `import` under `src/extractors/` |
| Perfect database sorter | No | Needs P6 gazetteers (course codes, dates, universities), P7 C2, orchestrator, real readers, Graphify |

**Do not execute P4 until `OPEN_QUESTIONS` is only `OQ4`.** An implementer who follows Task 2’s mapping plus Task 18’s Self-Review will ship eight completeness values, `file_id` in the observation-set digest, and four “still open” questions that Joseph already closed.

---

## What the answers actually closed (do not re-open)

Recorded so a later pass does not treat leftover PLAN prose as a live question.

| ID | Decision | Live evidence it already reached |
|---|---|---|
| **A1** | Rule 8 keys on **four** fields (hash, extractor name, version, config fingerprint) | P4 PLAN `REPLAY_KEY_FIELDS`; OQ2 dropped from `OPEN_QUESTIONS`; Task 15 compared set **excludes** `file_id` |
| **A2** | Filename span needs a `text_units` row | In SPEC table; PLAN fixture work already required this |
| **A3** | Zero-observation runs may keep text units | SPEC |
| **A4** | Routed-but-stopped run: `analysis_tier: native` | SPEC; fixture 19 |
| **B4** | Context window = P1 16th key **`evidence.context_window`** and in run `config` (fingerprinted). P4 holds no number | **Shipped:** `src/database_agent/budget.py` (16 keys), `tests/test_budget.py` |
| **B8** | Author missing-zone fixtures when P5 extracts those formats — do not invent now | Correctly still a named gap |
| **C1 / OQ3** | One reliability vocabulary; extractors only `direct` \| `possible` | SPEC table. **P6 SPEC OQ12 still asks P6 to confirm** — the one-line P6 must now *state*, not re-ask |
| **C2 / OQ4** | **Still open.** P7 decides. Direction: file-class default + observation override | Correctly remains in `OPEN_QUESTIONS` |
| **C3 / OQ5** | User corrects **facts**, never `raw_value` | SPEC table. PLAN Task 2 still lists OQ5 as open |
| **C4 / OQ6** | Ninth completeness = **`dataless`**. Zero observations. P2 count `runs_dataless` | **Shipped:** P2 `DATALESS_COMPLETENESS` / `runs_dataless`. P4 `COMPLETENESS` has nine. **P5 `admit()` still writes no row**; the catcher is unspecified as a task |
| **B6** | Spreadsheets and presentations **ship at launch** (`openpyxl`, `python-pptx`, plus xlrd/odfpy). Audio/video still metadata-only. `unsupported` = no extractor, not deferred-by-choice | SPEC. P5 PLAN still injects readers (correct) but Task 10 still talks as if launch coverage is an open question |
| **metadata_only** | Stopping extractor emits **zero** observations; file stays indexed via `filesystem` run (fixture 19 wins) | P4 Task 2 `ZERO_OBSERVATION_COMPLETENESS` includes `metadata_only`. P5 Task 2’s set **does not** |

---

## Finding class: the edits patched the task that would have shipped wrong, then left the surrounding pages asserting the old contract

This is the same defect class as finding 1 in file 15 (OQ2 closed in SPEC, open in PLAN). It happened again, for C1/C3/C4.

### 1. Blocking — P4 `OPEN_QUESTIONS` still has OQ3, OQ5, OQ6

`planning/parts/P4-evidence-shape/PLAN.md` Task 2:

- `COMPLETENESS` correctly has nine values ending in `dataless`.
- `ZERO_OBSERVATION_COMPLETENESS` correctly includes `metadata_only` and `dataless`.
- `OPEN_QUESTIONS` is still `{OQ3, OQ4, OQ5, OQ6}`.
- Task 18 still has a test that the set equals those four, **and** a test `test_oq6_closed_the_ninth_completeness_is_dataless`.

C1, C3, C4 are settled. A closed question is supposed to be **deleted** from the mapping (the PLAN’s own rule at Task 2). OQ4 stays.

The Self-Review (~line 6903) is fully stale:

- Claims OQ2 is still open and Task 15 **keeps `file_id` in the digest**.
- Claims `COMPLETENESS` is eight values and there is no ninth.
- Treats OQ3/OQ5 as unanswered.

An implementer who trusts Self-Review over Task 2 ships the world Joseph rejected.

**Patch before execute:** `OPEN_QUESTIONS = {OQ4}` only. Delete OQ3/OQ5/OQ6 from Task 18’s “held open” tests. Rewrite the Self-Review paragraph. Rewrite P4 SPEC *Open questions* 3, 5, and 6 so they point at the ratification table instead of still reading as unsettled (the numbered list currently sits *above* the table and still says “P4 does not invent a ninth value”).

### 2. Blocking — P4 SPEC still narrates OQ6 as open

`SPEC.md` Open question 6 still says none of the eight values fits and no run row is written. The ratification table ten lines later says `dataless`. Dual page. Same for OQ3 and OQ5. Readers of the numbered list will implement the old rule.

### 3. Blocking — P5 `ZERO_OBSERVATION_COMPLETENESS` is the old three-set

P4 Task 2:

```text
("unsupported", "deferred", "failed", "metadata_only", "dataless")
```

P5 Task 2 (~line 1186):

```text
("unsupported", "deferred", "failed")
```

If P5 is executed against that tuple, a `metadata_only` run is allowed to carry observations. That is the fixture-19 / rule-9 fight Joseph already settled: **zero from the stopping extractor**. Align P5’s set with P4’s before Task 1 of P5.

P5 Task 6 still contains a “P4 SPEC inconsistency, reported not resolved” block picking fixture 19. SPEC resolved it. Delete the conflict note.

### 4. Blocking-for-progress-line — C4’s catcher is not a task

SPEC C4: the gate still **raises** and writes nothing; whoever catches `DatalessRefused` (the router) writes `completeness=dataless`.

P5 Task 3 still: refusal writes no `extraction_runs` row; “until that caller exists, a dataless file is absent from §8.6.”

P2 already has `runs_dataless`. Without a named task that catches the exception and calls `record_run(..., completeness="dataless")`, the ninth value exists in the vocabulary and never appears in a real scan. P3 correctly still writes **no** run (P3 PLAN Global Constraints). P3’s leftover sentence that OQ6 is open should be struck; the detection duty did not change.

Recommend a P5 Task (or a one-page Wave-2 orchestrator SPEC) whose only job is: catch `DatalessRefused` / `ProtectedContainerRefused`, write the named run or write nothing, publish `source_scan_ref = scan_run_id`. Protected-container remains “no run, P3 exclusion is the record.” Dataless becomes a run.

### 5. Hygiene — P5 Task 17 mapping table vs code

`OUTCOME_BY_COMPLETENESS` already maps all nine, including `dataless → abstained`, `metadata_only → abstained`, `unreadable → abstained`. The prose table two screens above still marks those two rows **NEEDS JOSEPH**. Pick one: either the mapping is Joseph’s (then delete NEEDS JOSEPH) or it is not (then the dict is premature). As written, an implementer will stop and re-ask questions already encoded in the function.

`runs_dataless` is a **count**, not a fifth P2 `outcome`. Mapping `dataless → abstained` plus a separate count is consistent with C4’s “visible as unfinished, not as damaged.” Keep it; just stop labelling it unanswered.

---

## Stress-test: will this stack deal with the situations a sorter actually meets?

Situations, not APIs.

| Situation | What happens today / after P4+P5 as planned | Verdict |
|---|---|---|
| Two copies of the same PDF, different folders | A1/OQ2: observation set keyed by **content hash**, not `file_id`. Re-extract is per content version. Paths stay on the `files` row (P1/P3) | **Correct for a sorter.** Placement still later (P12). |
| Rename, same bytes | P1 identity is hash; P5 `inputs = (content_hash,)`. Free | **Correct** |
| Edit the file | New hash → new observation set. Old facts must not silently follow (P6’s problem, not P4’s) | Shape is ready; P6 must attach facts to hash |
| iCloud placeholder | P3 detects, does not hash. P5 `admit` raises. **No `dataless` run until a catcher exists** | Named, not wired. §8.6 line still lies until finding 4 |
| Encrypted / damaged PDF | `unreadable`, metadata rows allowed (M3) | Specified |
| Scanned PDF, no text layer | P5 injects `no_usable_facts`; **no default**, P6 owns the threshold (B7) | Honest. Until P6, OCR never auto-fires from a number P5 invented — good. Until P6, OCR also never auto-fires at all unless the caller injects a predicate |
| `Microsoft Word skills certificate` as Author | Catalogue 01 prefix + digit-tail rule. Checks assert it does **not** match `tps-microsoft-word` | **Correct** |
| `Microsoft Office 365 invoice` as Producer | Catalogue 01 known residual: prefix + a digit elsewhere still matches. Accepted in the JSON, not overlooked | **Imperfect, documented.** Do not silently “fix” without Joseph |
| `python-docx` / `Mozilla/5.0` as creator | Catalogue 01 live; P6 suppression, not P5 deletion of the observation | **Correct** — metadata stays as evidence, not as a person |
| `IMG_4821.JPG` | Catalogue 04: camera DCF, not screenshot. Checks document the cross-match | **Correct** |
| `Screenshot 2024-05-11 at 10.30.45.png` | Stem vs `splitext`: contract is on `file_row["filename"]` **with extension**. A caller that strips first loses seconds | **Trap named; P5 caller must not strip** |
| `BUSIB 4300` in a heading | Catalogue 06 **refuses** course codes (P6 gazetteer). Catalogue 04 refuses them as camera names. Until P6 authors the gazetteer, the sorter cannot make a subject fact | **By design, and the largest sorter gap** |
| DOI / ISBN-13 in body text | Catalogue 06, checksum-gated. Bare ISBN-13 still `uncertain` (FP risk) | **Good for labelled citations; weak for bare digit strings** |
| `Spring 2025` | Catalogue 06 matches nothing (dates are P6 §3.10). No date leaks in checks | **Correct deferral** |
| `1920×1080` image | Catalogue 02 exact-display **and** 16:9 sensor-shaped. Arbitration: 02 first. `false_positive_risk: high`. Video stills and camera 16:9 mode will be labelled screens | **Will mis-tag a class of photos.** Joseph should look at `unc-1920x1080-collision` before treating image facets as truth |
| `1919×1080` (one-pixel crop) | Misses 02 (exact), falls into 03’s 0.5 % 16:9 band → sensor-shaped | Named in `unc-near-miss-fallthrough`. Not a bug in the rule; a consequence of “exact” then “ratio” |
| `node_modules` | P3 §1.1 skip, **not** catalogue 05 | Correct split |
| `pyproject.toml` as skip-root | Uncertain. Adding it hides **all descendants** of every Python project | **Do not add** without an explicit yes |
| `.git` as skip-root | Catalogue 05 **refused** (catastrophic) | **Correct** |
| `package.json` | In **both** P3 exclusion-adjacent evidence and P5 markers — two jobs, two arrays | Checks assert this; do not collapse |
| Excel / PPTX at launch | B6: ship. Plan: injected `openpyxl` / `python-pptx`, no default, Task 10 still hedges launch | **Decision is ship; wiring is not a task that installs the libraries.** v1 will be `unsupported` for xlsx unless the caller injects readers |
| Audio / video | metadata-only v1 | Specified |
| Contacts `.vcf` / header-footer / annotations | No P4 fixture (B8). Extractor can still emit the zone; golden replay will not cover it | Named gap, not a freeze-blocker |
| Protected `.app` / iCloud Drive library | P3 does not descend; P5 `admit` raises; no extraction_runs | Specified |
| Re-scan after extractor version bump | Four-field replay key. Observation set changes → cache miss | **Correct** |
| User says “that OCR string is wrong” | C3: correct the **fact**, never `raw_value` | Specified. UI is P13. P4 must not grow an observation-editor |
| Two extractors on one file (`pdf.text` then `ocr.apple_vision`) | Two runs, two observation sets, same hash. Rule 8 four-field key | **Correct** |
| No scan→extract loop | P3 `scan()` still does not call P5. Wave 2 tests stay per-package until an orchestrator exists | **The sorter cannot run end-to-end** even if P4+P5 go green |

**Bottom line of the stress table:** identity, refusal, and “do not invent” are robust. **Seeing course codes, dates, institutions, and “this 1080p image is a lecture slide not a screenshot” is not robust**, and must not be papered over by executing P4/P5.

---

## Catalogue review

Location: `planning/deferred-catalogues/`. JSON is source of truth; Markdown is generated. `./checks/run_all.sh` passed this session.

### What is actually good

- Injection contract matches P5 Task 20: catalogues are **data the caller loads**. Importing them under `src/extractors/` would fail introspection. README states this clearly.
- Prefix ≠ starts-with (catalogue 01). Digit-tail stops `Microsoft Word skills certificate`. Residual `Microsoft Office 365 invoice` is documented.
- 02-then-03 arbitration is explicit. `4032×3024` is sensor (03), not a named display (02).
- Catalogue 05: **exactly four** `p3_exclusion_roots`. Checks fail if a fifth is smuggled in. `.git` refused in writing.
- Catalogue 06: no §3.10 dates, no PII patterns, no course-code gazetteer. Checksums self-verified for ISBN-13/10, ISSN, MOD 11-2.
- Catalogue 07 kinds are only `source-code manifest` \| `document name` — matches P5 `MARKER_KINDS`.
- Honest sourcing: **8 of 44 cited pages were actually opened**; the rest are search-summary grade. That sentence in the README is load-bearing. Do not treat the pack as vendor-verified.
- `example_false` semantics differ by catalogue and the README says so. Implementers who assume one meaning will write wrong tests.

### What is not “deal with all situations”

1. **42 uncertain items.** None blocks the check suite. Each one left open is a class of evidence the product cannot see, or a default judgement. First decision remains `unc-pyproject-as-exclusion` — default is **leave it out**.
2. **P5 PLAN does not point at these files** except B9 “author them.” An executor of P5 can go green on stubs (`dimension_signal=lambda …: None`) and never load the JSON. The catalogues then rot. Add a wiring note to P5 PLAN Task 5/E5 and E1 `find_structured_strings`: production caller loads these seven files; tests may inject fixtures, not the live JSON, unless a named integration test says otherwise.
3. **P6 does not point at catalogue 01.** C1 requires P6 to *state* one vocabulary; catalogue 01 is the suppression list that vocabulary will use. P6 SPEC OQ12 still asks for confirmation.
4. **Concurrency leftover:** `checks/04-alternate-version.json` exists because two agents collided. Live 04 is v1.1, 37 `fnp-*` entries. Do not merge the alternate by accident.
5. **High-FP rows that will embarrass a “perfect sorter” if treated as truth:** `unc-1920x1080-collision`; `cid-isbn13-bare`; 01 `Microsoft Office 365 invoice` residual; 03 crop shapes (`4:5` / `9:16` already matching sensor ratios).
6. **Nothing here is a university / course-code / academic-term gazetteer.** That is still P6 deferred. The sorter’s central worked example (`subject = BUSIB 4300`) is **explicitly unmatched** by catalogues 04 and 06. That is discipline, not a miss — but it means v1 extraction will not “just work” on a course folder.

### Catalogue execute rule

Joseph reviews and commits (README). This session did not commit. Do not let P5 Task 20’s “no gazetteer in the package” be satisfied by copying JSON into `src/extractors/catalogues.py`.

---

## Shipped Wave 1 vs leftover PLAN prose

| Claim in a PLAN | Live code |
|---|---|
| P4: context budget is caller-supplied forever | **False.** P1 `CEILING_KEYS` has `evidence.context_window`. Tests pin length 16 |
| P4 Self-Review: eight completeness values | **False.** Task 2 tuple has nine; P2 counts `runs_dataless` |
| P5: OQ6 open, no run row, dataless absent from §8.6 | Half true: no catcher. The *name* exists in P2 |
| P3: OQ6 open | **False.** Detection duty unchanged; the name is `dataless` |
| File 15: combined suite 462 | This session: **468** (P1/P2 grew for the 16th key and dataless counts) |

P4/P5 packages still do not exist (`src/evidence_shape/`, `src/extractors/`). Self-review pass counts (349 / 272 / 811) were not re-run; they cannot be, until the packages exist.

---

## Still unpaid (unchanged, still true)

- No scan → extract orchestrator. `source_scan_ref = scan_run_id` is a join waiting for a caller.
- No writer of `files.extraction_status_by_tier` (P1 column, nobody fills it).
- Graphify still unpaid.
- P7 must settle C2 before its schema (file-class default + observation override is the direction, not the schema).
- P6 must **state** C1 (one vocab; extractors `direct` \| `possible`) and consume catalogue 01. Do not leave OQ12 as a question.
- Real PDF/HEIC/OCR libraries remain injected. Apple Vision is the v1 OCR engine (B1); DPI starting value 200 (B2); four OCR/image §8.6 ceilings unset until the engine is wired (B3).
- Five P4 zones and `contacts` still have no golden fixture (B8).

---

## Punch list before anyone types `src/evidence_shape/`

1. P4 PLAN: `OPEN_QUESTIONS = {OQ4}` only. Task 18 guards follow. Self-Review rewritten. Global Constraints “context budget is caller-supplied” rewritten to B4 (16th key + fingerprinted `config`; P4 still holds no number).
2. P4 SPEC: Open questions 3, 5, 6 marked closed with pointers to the ratification table. Leave 4 open.
3. P5 PLAN: `ZERO_OBSERVATION_COMPLETENESS` matches P4 (five values). Delete Task 6’s unresolved-conflict note. Task 17: drop NEEDS JOSEPH on mappings already in `OUTCOME_BY_COMPLETENESS`. Task 10: B6 is ship XLSX/PPTX, not an open launch question.
4. Name the `DatalessRefused` catcher (P5 task or orchestrator page). Protected containers still write no run.
5. One sentence in P6 SPEC: C1 confirmed. Catalogue 01 is the suppression list, injected, never imported into P5.
6. One sentence in P5 PLAN (or a Wave-2 wiring note): production injects catalogues 02–07 from `planning/deferred-catalogues/`.
7. Joseph: decide `unc-pyproject-as-exclusion` (default no) and look at `unc-1920x1080-collision` if image facets will drive grouping.

After 1–2, **execute P4**. After P4 is importable and 3–6, **execute P5**. Catalogues commit when Joseph is satisfied; they are not a P4 dependency.

The perfect database sorter is P1–P13 plus gazetteers plus an orchestrator. P4/P5 plus these catalogues are the part that **sees without lying**. They are close to freeze. They are not close to “all situations,” and the leftover PLAN pages are currently the highest risk of shipping a sorter that lies.

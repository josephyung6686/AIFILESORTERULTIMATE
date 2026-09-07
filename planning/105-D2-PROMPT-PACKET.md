# 105 — D2 prompt packet: four unwired sites and the A_fact glossary, drafted, stressed and measured, for ratification

Date: 2026-09-06. Status: **drafts for the owner's ratification — nothing here is ratified and nothing here is wired.**
Protocol: `103` §28.1 (requirements traced to `00`; a traced draft; stress cases; a bakeoff of at least two candidates under both models; ratification with the numbers attached). Governing rulings: `104` §13.5 (model decides, rules validate), §13.6 (grounding hard, the rest shown), §13.7 (model names, user confirms), §13.8 (refinement allowed, removal constrained); `00` Amendments of 2026-09-05.

Every template id below carries `unratified` and its date. The ratified A_fact files are untouched; every new file sits beside them under `src/llm_harness/library/`. The bench is `tools/promptbench/` and every number in this document was produced by a command written next to it.

## 0. How to read this packet, and what changed on 2026-09-06

Three process additions from the coordinator, all honoured here: work is committed per unit (each requirements trace, each draft, each bakeoff run), anything that may run longer than three minutes runs in the background and is polled, and every local request sets `num_ctx` explicitly above the measured prompt length and records the value used — Ollama otherwise truncates silently to 2,048 tokens and answers anyway.

Sections 1 to 5 follow the site order `103` §28.1 fixes (C and D, then B, then E), with the A_fact glossary revision (fix-chain step 1, `104` §11.2) placed first because every other site's numbers are downstream of it. Each site section has the same six parts: requirements traced to `00`; research applied; the candidates, with the winner and the loser and their numbers; the stress-case table; contract gaps found; the ratification question.

**How every number here was produced.** From the worktree root:

```
python3 -m tools.promptbench run --site C_placement --candidates walk,eliminate --models cloud --out tools/promptbench/out/C_placement
python3 -m tools.promptbench run --site C_placement --candidates walk,eliminate --models local --out tools/promptbench/out/C_placement
python3 -m tools.promptbench score --out tools/promptbench/out/C_placement
```

and the same for `D_residual` (`ladder,shelves`), `B_group` (`four-questions,anchors-first`), `E_template` (`from-facts,what-a-person-opens`) and `A_fact` (`ratified-glossary,proposed-glossary`). `--dry-run` builds every dossier and prints its size and `num_ctx` without a call; `dossier --site S --case ID --candidate NAME` prints the exact model-visible bytes. Raw requests, responses, verdicts, latencies, tokens and `num_ctx` are one JSON per call under `tools/promptbench/out/<site>/calls/`, ignored by git (`tools/promptbench/.gitignore`); the per-site `summary.md` tables are copied into this document. The cloud call ledger is `tools/promptbench/out/cloud_ledger.json`, one file for the whole bakeoff, spent before each socket opens, cap 400. The cloud arm is `deepseek-chat` at temperature 0 (recorded per call; the product sets none, §7 G13) with no `response_format`; the local arm is `qwen3:8b` through `readers/model_ollama.py` with `think: false`, `num_ctx` set per call (16,384 for every case here) and `prompt_eval_count` recorded beside it, temperature 0, seed 1, `format: json`, `num_predict` 4,096. Every case is synthetic; no owner file, filename or dossier reached either model.

**One stated deviation from `103` §28.1 step 4.** Step 4 names `.groundtruth/corpus` as the labelled corpus for C and D. This packet ran no corpus arm: the owner's corpus is personal data, the coordinator's constraint for this wave was that no owner file, dossier or filename reaches a cloud model and the local model sees real dossiers only through the product's own gate, and the C and D builders do not yet emit the profiles the texts describe (G3), so a corpus request today would offer the model identifiers it cannot read. The synthetic suites carry the corpus's failure mechanisms instead (`104` §11.1: C14, C16, A01, A02, A04, B08, E03) and §9 item 3 is the path to the corpus arm once G3 exists in some form. Until it runs, no number here is a `SORTING exact` number.

## 1. A_fact — the `school` and `subject` glossary entries (fix-chain step 1)

### 1.1 Requirements, traced

The template is untouched: the text in force stays `a_fact.unratified.folder-levels.2026-09-04` and the ratified `a_fact_template.txt` beside it. What changes is two entries of the glossary the dossier carries under `field_glossary`, and only those two.

| # | Requirement | Source |
|---|---|---|
| A-R1 | `school`, for coursework's `holder_institution` role, means the institution that offers this course and term, not any school the person attended. | `104` §11.2 step 1 (owner text under D2's protocol); `00`:44 |
| A-R2 | A school merely mentioned is `authored_by`-class metadata and never a level. | `104` §11.2 step 1; `00`:44 ("authorship is usually metadata"), `00`:63 ("a university name alone should not create a group") |
| A-R3 | `subject` means the course as the course names itself, code or title. | `104` §11.2 step 1; `00`:37-38 (`subject = BUSIB 4300`) |
| A-R4 | A study guide, a textbook or a publisher is not a course. | `104` §11.2 step 1; `104` §11.1 (the CliffsNotes node) |
| A-R5 | Every other glossary entry is byte-identical to the ratified file; the proposal says it is unratified in its header and its status. | glossary convention (`tests/p8/test_p8_field_glossary.py`); `84` §1 |
| A-R6 | The meanings are transcribed, never authored, and name their source. | glossary convention; `tests/llm_harness/test_d2_glossary_proposal.py` |
| A-R7 | The measured effect must be the regression's reversal: the essays leave `Georgetown Prep`, the study guide's publisher is declined, and the correct-answer cases do not lose coverage. | `104` §11.2 step 1's test; `00`:223 metric |

### 1.2 The two candidates

- **ratified-glossary**: the incumbent — `field_glossary.json` as shipped. `school`: *"the institution the holder attends, attended, or teaches at - the person's own school, never the application target"*. `subject`: *"the course or study subject the material belongs to"*.
- **proposed-glossary**: `field_glossary_proposal_2026-09-06.json`. `school`: *"the institution that offers this course and term, not any school the person attended; a school merely mentioned is authored_by-class metadata and never a level"*. `subject`: *"the course as the course names itself (code or title); a study guide, textbook or publisher is not one"*. 53 of 55 entries byte-identical to the ratified file; the two differing entries cite `104` §11.2 step 1.

The bench builds each A case as a real P6 world (a file, its observations, `FactRequest`, the deployment's `normalize_for_model` and `contradicts_stronger`), shows the same folder-levels template under each glossary, and validates through `sites.dispatch` at A_fact with `apply_consequence=False`.

### 1.3 Results (cloud, deepseek-chat, 14 cases × 2 glossaries = 28 calls)

Two numbers matter here and they are not the same number. **What the model said** per field is the glossary's effect; **what the deployment accepted** is capped by `cli.normalize_for_model`, which returns `None` for every course title (`University Writing`, `AP World History`, `Introduction to Organic Chemistry`, `Machine Learning`), for `Michaelmas term`, and for any `work_type` outside its closed list (`Tutorial sheet`, `Final Exam`, `Study Guide`) — so `accepted_rate` is 0.0 under both glossaries and says nothing about them (G15).

Only `school` and `subject` differ between the arms, so they are the comparison; `term` and `work_type` carry the same meaning under both and are reported apart.

| arm | `school` wrong (said) | `subject` wrong (said) | responses destroyed* | schema-valid | grounding | accepted |
|---|---|---|---|---|---|---|
| ratified-glossary | 3 of 13 said (A01, A04, A13) | 5 of 13 said (A02, A03, A06, A07, A13) | 1 (A12) | 13 / 14 | 23 / 25 | 0 / 14 |
| proposed-glossary | 2 of 13 said (A04, A13) | 8 of 13 said (A01, A02, A03, A06, A07, A08, A13, A14) | 1 (A05) | 13 / 14 | 22 / 22 | 0 / 14 |

\* one malformed claim destroying the whole response (`SCHEMA_INVALID`, the ratified rule 11), in which nothing was said.

Apart, and the same under both arms: `term` was right wherever it was judged (A03, A05, A10); `work_type` was right in 5 of 10 judged fields under the ratified arm and 3 of 10 under the proposed one, but three of those "wrong" cells are declines on a syllabus, a lecture deck and a tutorial sheet, and the ratified glossary's own meaning for `work_type` is *"if the file IS the work product of a bounded engagement or course"* — a syllabus is not the student's work product, so the decline is arguably right and the label is arguably wrong. The `work_type` labels of A03, A06 and A10 are recorded as disputed and carry no weight here. This is a first measurement: one run, temperature 0, cloud only; `104` §13.4 asks for three runs and a median before any of it is read as more.

**The regression case is fixed by the proposal and the collector is not closed by it.** On A01 — the university essay that names the author's old school and a target university, the mechanism of `104` §11.1 — the ratified wording produced `school = "Georgetown Prep"` and the proposed wording produced a decline with the statement *"No released evidence names the institution offering the course."* That is the five essays leaving `Georgetown Prep`. But on the résumé (A04) both wordings answered `school = "Georgetown Preparatory School"`, and on the transcript (A13) the proposal answered `Columbia University`: a file that is not coursework, asked coursework's `school`, still yields a school. That is what `104` §11.2 says — step 1 is necessary and steps 2 (school as a group-level fact on the anchor) and 4 (per-branch situation, so a résumé is not asked `subject`) are what stop the collector.

**The proposed `subject` wording is worse, measurably.** "the course as the course names itself (code or title)" was read as the document's title: `University Writing - Essay 2`, `AP World History Study Guide - Unit 3`, `PHYS 2801 Final`, `CliffsNotes on The Great Gatsby`, `Chapter 5: Thermodynamics` (9 wrong against 6). The exclusion "a study guide, textbook or publisher is not one" did not hold under either wording: A02 gave `The Great Gatsby` (ratified) and `CliffsNotes on The Great Gatsby` (proposed); A07 gave `Thermodynamics` and `Chapter 5: Thermodynamics`. The word *title* invites the lift the ratified rule 4 forbids.

### 1.4 Stress cases

| case | ratified-glossary said | proposed-glossary said |
|---|---|---|
| A01 essay naming old school + target university | subject=`University Writing` ok; **school=`Georgetown Prep` X**; work_type=`Essay` ok | subject=`University Writing - Essay 2` X; **school=decline ok**; work_type=`Essay 2 Final Draft` X |
| A02 CliffsNotes study guide | subject=`The Great Gatsby` X; school=decline ok; work_type=decline ok | subject=`CliffsNotes on The Great Gatsby` X; school=decline ok; work_type=decline ok |
| A03 syllabus stating course, institution, term | subject=`PHYS 1401 - General Physics I` X; school=`Columbia University` ok; term=`Spring 2026` ok; work_type=decline X | same |
| A04 résumé listing schools attended | school=`Georgetown Preparatory School` X; subject, work_type decline ok | same |
| A05 homework with the code only | subject=`PHYS 1401` ok; school, term decline ok; work_type=`Homework 3` X | whole response `SCHEMA_INVALID` |
| A06 lecture slides, university footer | subject=`Rotational Dynamics` X; school=`Columbia University` ok; work_type=decline X | subject=`Lecture 08: Rotational Dynamics` X; school ok; work_type=decline X |
| A07 textbook chapter naming its publisher | subject=`Thermodynamics` X; school=decline ok | subject=`Chapter 5: Thermodynamics` X; school=decline ok |
| A08 study guide naming its course | subject=`AP World History` ok; school=decline ok | subject=`AP World History Study Guide - Unit 3` X; school=decline ok |
| A09 application essay to a target university | subject, school decline ok | same |
| A10 course named by title, Michaelmas term | subject ok; term ok; school=decline ok; work_type=decline X | same |
| A11 lab report mentioning the author's high school | subject=`PHYS 1401` ok; school=decline ok; work_type=`Lab Report` ok | same |
| A12 online course offered by a university | whole response `SCHEMA_INVALID` | subject=`Machine Learning` ok; school=`Stanford University` ok; work_type=decline X |
| A13 transcript, two institutions | subject=`PHYS 1401` X; school=`Georgetown Preparatory School` X | subject=`PHYS 1401 A` X; school=`Columbia University` X |
| A14 exam whose room number looks like a code | subject=`PHYS 2801` ok; work_type=`Final Exam` ok | subject=`PHYS 2801 Final` X; work_type=decline X |

Local (qwen3:8b) arm: not yet run for A at the time of writing — see §8.

### 1.5 Contract gaps found at A

G15 (new): `cli.normalize_for_model` returns `None` for every course title as `subject` and for any `work_type` outside `WORK_TYPE_VOCABULARY`, so a correct title is rejected `VALUE_NOT_NORMALIZABLE` — the closed-vocabulary rejection §13.7 reversed (`104` R-21) is still in force at the validator. Until it becomes "confirm this new value", no title-named course can be filed and the glossary's `(code or title)` cannot be measured through acceptance. G16: one malformed claim destroyed a whole response in 2 of 28 calls (ratified rule 11 at work); both were `payload.value` omissions. The two limits of `82` §0 (S1, S2) stand.

### 1.6 The ratification question

1. **Provisionally, the proposed `school` entry** — *"the institution that offers this course and term, not any school the person attended; a school merely mentioned is authored_by-class metadata and never a level"* — as fix-chain step 1's first half: on this one cloud run it reverses A01 and is neutral or better everywhere else, with A04/A13 recorded as what steps 2 and 4 must close. Ratification waits for the local arm and the three-run median (`103` §28.1 step 4, `104` §13.4); what the owner is asked now is whether this wording is the one to measure to that standard.
2. **Do not ratify the proposed `subject` entry as written.** Its measured effect is title-lifting. Put to the owner instead, unmeasured: *"the course's own name — a course code, or the name a syllabus would give the course — never the title of this document, its chapter, its book, its study guide or its publisher"*; measure it as a third arm before ratifying.
3. Decide G15: whether the normaliser's closed vocabularies for `subject`, `term` and `work_type` are replaced by the "confirm this new value" path before A is measured on the owner's corpus again.

### 1.7 The third `subject` wording, measured (cloud, 14 calls, 2026-09-06 evening)

`subject-v3-glossary` (`field_glossary_proposal_subject_2026-09-06.json`) is the proposal with `subject` alone changed to the §1.6 wording: *"the course's own name - a course code, or the name a syllabus would give the course - never the title of this document, its chapter, its book, its study guide or its publisher"*. The `school` entry is the proposal's, unchanged, so this arm is also a second run of that entry.

| arm | `subject` wrong (said) | `school` wrong (said) | responses destroyed | schema-valid | grounding |
|---|---|---|---|---|---|
| ratified-glossary | 5 of 13 (A02, A03, A06, A07, A13) | 3 of 13 (A01, A04, A13) | 1 (A12) | 13 / 14 | 23 / 25 |
| proposed-glossary | 8 of 13 | 2 of 13 (A04, A13) | 1 (A05) | 13 / 14 | 22 / 22 |
| subject-v3-glossary | **5 of 12** (A02, A03, A06, A07, A13) | **4 of 12** (A01, A04, A09, A13) | 1 (A11) | 13 / 14 | 23 / 23 |

**`subject`: the title-lifting is gone and the exclusion clause still does not hold.** A01, A08 and A14 return to the course name or code (`University Writing`, `AP World History`, `PHYS 2801`) that the proposal had turned into document titles; A05, A10 and A12 stay right. What the third wording does not do is decline: A02 still says `The Great Gatsby` (the book), A07 `Thermodynamics` (the chapter's topic), A03 `PHYS 1401 - General Physics I` (code and title), A06 `Lecture 08: Rotational Dynamics`, A13 `PHYS 1401 A`. Five wrong of twelve judged is the ratified wording's own rate; the third wording repairs the proposal's regression and improves nothing beyond the incumbent. The negative list in the entry ("never ... its book, its study guide or its publisher") did not make the model decline a study guide's subject; nothing measured here does, and `104` §11.2 steps 3 and 4 (no node from an unanchored single value; a study guide asked its own schema) remain what stops the CliffsNotes node.

**`school`: the A01 reversal did not reproduce.** Under an identical `school` entry, the proposed arm declined `school` on A01 and this arm answered `University of Chicago` — the essay's target university; on A09 (the application essay) it answered `Duke`, again the target, where both other arms declined. The wording says "not any school the person attended", and the model obeyed it by moving from `00`:44's first collector (the school attended) to its second (the application target). One run said the entry fixes A01; the next run, with the same entry and a different neighbour, said it does not. §10's second-run criterion for the `school` entry is therefore **failed on the first retry**, and the entry cannot be put forward as measured. A wording that names both exclusions ("not a school the person attended and not a school a document is addressed to") is the obvious next arm, unmeasured.

The rule-11 destruction (one malformed claim, whole response lost) landed on a different case in each arm — A12, A05, A11 — one in fourteen every time: a property of the shape, not of the wording.

### 1.8 A proposed `readings` dossier key for the authored `needs_llm` readings (R-08), measured

**Why.** The ratified A_fact text names fourteen dossier keys "and no others", `dossier._body` writes exactly those, and the plumbing now stops at that boundary with a test. So the 314 authored `needs_llm` rows of `recognition.json` (1,984 readings across 23 schemas; `academic` 12 rows, 69 readings), which `recognition.rules` carries as `deferred_readings` and `recognition.detector` attaches to every abstention "for P8 to pick up", can never reach a prompt (`104` R-08). What follows is the key, its shape, where it sits, what it changed on seven cases, and what the position is worth in tokens — measured, not argued. Nothing here is code the product runs: the bench emulates the key on top of the product's own bytes (`tools/promptbench/dossiers.py`, `readings_for`, `serialise_dossier`).

**Requirements, traced.**

| # | Requirement | Source |
|---|---|---|
| AR-R1 | The readings are the situation's `needs_llm` entries, verbatim, with the row they came from; transcribed, never authored, never rewritten for the model. | R-08; the glossary convention (`dossier.py`'s "authors no content"); `tests/tools/test_promptbench_readings.py` (byte-equal to `recognition.json`) |
| AR-R2 | A reading is guidance about a kind of file and never evidence: no part may be cited, a word or example that appears only there is not a value found. | `00`:39 ("cite the exact text ... that supports its conclusion"), `00`:42 (the validator checks the cited evidence exists); same rule as `field_glossary` |
| AR-R3 | A reading may change which field the model considers and whether it declines; it may not supply a value, change a value's spelling (ratified rules 4, 5) or add a third move. | `00`:39 ("must return unknown where support is insufficient"); the ratified A_fact text's two moves |
| AR-R4 | A question a reading raises about what the file is for is not answered at A_fact: A extracts fields under a situation already chosen; the situation question is `104` §11.2 step 4's per-branch call (R-37), which does not exist. | ratified A_fact text ("You are not deciding what the file is for"); `00`:39 (the LLM "may determine whether an extracted document appears to be an application essay ...", which is the situation call, not the field call) |
| AR-R5 | The readings are the same on every file of one situation and belong to the stable part of the prompt; the file's own keys come after them. | `00`:40 (the cache key carries the prompt fingerprint: readings in the dossier are covered by `dossier_id`), `00`:242 and 258 (model cost is budgeted and observable; a prefix the provider can cache is the lever) |
| AR-R6 | The count and byte size of the readings sent travel with every call record, because they are budget. | `00`:242 |

**The key.** Name: `readings`. Shape: a list, one object per reading, `{"row": "<recognition row id>", "text": "<the reading, verbatim>"}`, in the library's order, for the active schema row and the situation row (`academic`, `academic.coursework`: 11 readings, 3,076 bytes, about 640 tokens on this dossier). Position: in the situation frame, after `folder_levels` and before the file's own keys. **That position is not available by naming the key.** The product serialises the dossier with `canonical_json`, which sorts keys, so `readings` lands between `policy_version` and `reduction_rung` — after `conflicts`, `eligibility_reason` and `evidence_items`, which are the file's; and today's shared prefix is already only `allowed_vocabulary` and `call_site`, with `field_glossary` and `folder_levels` mid-dossier behind the file's bytes. The frame-first order is an assembler decision, recorded as **G18** in §7 — and **landed the same evening on the schema agent's branch** (`104` R-58, `worktree-agent-a88b7004ece56cbf1` at bdb2105): `dossier._body` now emits the fifteen keys in a documented constant, `_BODY_ORDER = _FRAME_KEYS + _FILE_KEYS` (call site, response schema, shaping policy, versions, ceiling, rung, eligibility, vocabulary, glossary, levels; then subject, conflicts, evidence items, released evidence), and `_ordered_body` refuses a mapping whose keys are not exactly those fifteen. Its own measurement on two coursework files: a shared prefix of 205 bytes became 7,806 of an 8,999-byte body, 48.3% to 93.0% of the model-visible bytes with the template counted — and 93.0% is the best case, two files with the same open field set. On a real corpus `model_facts.open_question` narrows `allowed_vocabulary`, `field_glossary` and `folder_levels` to each file's pending fields, so two files with different open sets share the frame only up to `allowed_vocabulary`; measured, that is 7,110 of 8,999 body bytes (79.0%) and 88.9% model-visible. The honest range is 88.9% to 93.0% against 48.3%, and the floor holds because `response_schema` (3,999 bytes) and `shaping_policy` (2,378) lead the frame deliberately, ahead of anything that varies per file. `readings`, constant per situation, closes the frame after `folder_levels` for the same reason. Two consequences for this key. First, adding `readings` to the template's key line alone makes every A_fact call refuse at the seam (`tests/p8/test_p8_dossier_frame_first.py::test_a_sixteenth_key_is_refused_rather_than_appended`); `_FRAME_KEYS` must gain `readings` in the same change, at the end of the frame after `folder_levels`, which is where the bench's emulation now puts it (`FRAME_KEYS` in `tools/promptbench/dossiers.py` follows `_BODY_ORDER` exactly). Second, `tests/integration/test_deferred_readings_reach_the_boundary.py::test_no_reading_reaches_the_bytes_the_model_is_shown` is the test that fails, and closes R-08, when both are done. The template that names the key is `a_fact.unratified.folder-levels-readings.2026-09-06`: the folder-levels text with `readings` in its key line and one paragraph, modelled on the glossary's, saying it is guidance and not evidence and that its situation question is not answered here.

**The seven cases**, each a kind of file one of the eleven readings describes, judged per field; the glossary is the ratified one on every arm, so only the readings differ. Three arms: `readings-control` (the folder-levels text, no key), `readings-canonical` (the key in the product's sorted order), `readings-frame-first` (the key in the frame-first order). 21 cloud calls, sequential in one process so that the provider's prefix cache sees each arm's calls in a row.

| case | persona | traces | expectation | proposed-glossary / cloud | ratified-glossary / cloud | readings-canonical / cloud | readings-control / cloud | readings-frame-first / cloud | subject-v3-glossary / cloud |
|---|---|---|---|---|---|---|---|---|---|
| AR01 — a course named in prose, with no code-shaped token | Priya | 00:39, reading:academic.coursework#3 | answer: `{"fields":{"subject":"Introductory Cell Biology","school":null,"term":null}}` | — | — | WRONG / reject SCHEMA_INVALID | correct / reject VALUE_NOT_NORMALIZABLE | correct / reject VALUE_NOT_NORMALIZABLE | — |
| AR02 — a syllabus in Spanish stating the code, the institution and the term | multi-life | 00:39, reading:academic.coursework#6 | answer: `{"fields":{"subject":"FIS 1401","school":"Universidad de Chile","term":"Semestre de oto...` | — | — | WRONG / reject VALUE_NOT_NORMALIZABLE | WRONG / reject VALUE_NOT_NORMALIZABLE | WRONG / reject VALUE_NOT_NORMALIZABLE | — |
| AR03 — one course code stated for two terms in one file | Priya | 00:63, reading:academic.coursework#4 | answer: `{"fields":{"subject":"PHYS 1401","term":null,"school":null}}` | — | — | correct / abstain | correct / abstain | correct / abstain | — |
| AR04 — a course whose name resembles the reading's own example and is not it | Priya | 76:R18, 00:42, reading:academic.coursework#3 | answer: `{"fields":{"subject":"Introductory Organic Synthesis","term":null,"school":null}}` | — | — | correct / reject VALUE_NOT_NORMALIZABLE | correct / reject VALUE_NOT_NORMALIZABLE | WRONG / reject SCHEMA_INVALID | — |
| AR05 — an unlabelled essay whose only academic signal is topic and register | multi-life | 00:39, reading:academic.coursework#1 | answer: `{"fields":{"subject":null,"school":null,"term":null,"work_type":"Essay"}}` | — | — | false abstain / abstain | WRONG / reject VALUE_NOT_NORMALIZABLE | false abstain / abstain | — |
| AR06 — an archive whose manifest mixes coursework and application documents | multi-life | 00:239, reading:academic.coursework#5 | abstain: `{"fields":{"subject":null,"school":null,"term":null,"work_type":null}}` | — | — | abstained / abstain | abstained / abstain | abstained / abstain | — |
| AR07 — OCR noise with a token that resembles a course number | multi-life | 00:239, 00:42, reading:academic.coursework#2 | abstain: `{"fields":{"subject":null,"work_type":null,"school":null}}` | — | — | abstained / abstain | abstained / abstain | abstained / abstain | — |

| case | what a reading may change | what it must not change | control said | canonical said | frame-first said |
|---|---|---|---|---|---|
| AR01 course named in prose | a decline into a cited `subject` | — | `Introductory Cell Biology` ok | whole response `SCHEMA_INVALID` | `Introductory Cell Biology` ok |
| AR02 Spanish syllabus | declines into cited `subject`, `school`, `term` | — | all three said; `subject` as code and title (`FIS 1401 - Fisica General I`, the minimal run is the code) | same | same |
| AR03 one code, two terms | `term` from a guess to a decline (`00`:63) | `subject` | `term` = `Spring 2025` X | `Spring 2025` X | `Spring 2025` X |
| AR04 resembles the reading's example | — | `subject` must be the file's spelling, never the reading's `Introduction to Organic Chemistry` | `Introductory Organic Synthesis` ok | ok | whole response `SCHEMA_INVALID` |
| AR05 essay, topic and register only | `work_type` cited from "In this essay" | no answer to "coursework or application essay" | `work_type` = `draft3` X (the title) | every field declined | every field declined |
| AR06 mixed archive manifest | — | no field from "shared purpose"; no course from a member's filename | all declined ok | all declined ok | all declined ok |
| AR07 OCR noise with a course-like token | — | no `subject` from `14O1` | all declined ok | all declined ok | all declined ok |

**What the readings changed: one answer, and not into the labelled one.** On AR05 the control lifted the file's title as `work_type` (`draft3`); both readings arms declined every field, including the `work_type` the text does support (`In this essay`). Everywhere else the three arms said the same thing: the course-in-prose case and the Spanish syllabus were already answered by the bare text, the two-terms reading did not stop `term`, the must-not-change cases held under all three (the reading's own example was never proposed, no reading was cited — 0 of 14 citations pointed anywhere but `released_evidence` — and no situation answer was produced on AR05 or AR06). Two responses were destroyed by rule 11 (AR01 canonical, AR04 frame-first), one in seven per readings arm, the same fragility §1.7 records. The eleven readings themselves split five to six: five describe a field the extractor can act on (a course named in prose, a code-shaped token without context terms, another language's term vocabulary — the readings whose cases the bare text already handled), and six describe what the file or the packet *is* (coursework or an application essay, one purpose or one course, one course-term or two), which is the situation question A_fact is forbidden to answer and the model correctly did not.

**What the position is worth, measured by the provider's own cache accounting** (`prompt_cache_hit_tokens` per call, recorded in every cloud record from this run on):

| arm | prompt tokens per call | cache-hit tokens, calls 3 to 7 | share of the prompt served from cache |
|---|---|---|---|
| readings-control (no key, sorted) | 4,089 to 4,477 | 1,792 | 41% (template, vocabulary, call site; then the file's bytes break the prefix) |
| readings-canonical (key, sorted) | 4,724 to 5,114 | 1,920 | 39% (the readings sit behind the file's bytes and are re-read every call) |
| readings-frame-first (key, frame first) | 4,721 to 5,118 | **4,480** | **90%** (only the file part, 241 to 517 tokens, is new) |

The frame-first layout puts 2,560 more tokens per call behind the cache than the product's order does, on a dossier of this size; the readings add about 640 tokens and, in the sorted order, all 640 are paid on every call. That is the whole case for G18, and it holds with or without `readings`: `field_glossary` and `folder_levels` were behind the file's bytes for the same reason until R-58. The frame-first arm here was measured with the bench's earlier within-frame order (vocabulary first); the cache figure does not depend on the order inside the frame, only on the frame preceding the file, and the emulation now matches `_BODY_ORDER` so the next run's bytes are the product's.

**One more gap the key runs into, from the schema agent's measurement (G19).** `recognition.rules._schema` flattens every `needs_llm` row of a schema into `SchemaRules.deferred_readings` and discards the `row` key that names the situation. So what `FactCallAuthorities.deferred_readings` holds for a coursework run is the *schema's* readings — `academic`'s 69, 14,491 characters, 3.6 times the whole 4,000-token dossier ceiling; `law_practice` would carry 67,167 — and not the situation's 11 (2,015 characters, which fits a stable prefix). The key as proposed here sends the situation's rows only (AR-R1), and that needs `row` preserved through `recognition/rules.py`, a change nobody has made. Until it is made, there is nothing of the right size to put under the key.

**The ratification question.** (0) The code path, stated once: the template's key line gains `readings` (sixteen keys), `dossier._FRAME_KEYS` gains it after `folder_levels`, and `recognition/rules.py` keeps `row` so the situation's readings can be selected; three one-line changes, none of them a prompt. (1) Ratify the key's name and shape (`readings`, `[{row, text}]`, verbatim, the situation's rows only) and the one paragraph of the folder-levels text that names it, so that a template may carry it — **and do not wire it at A_fact on this evidence**: on seven cases and 21 calls it changed one answer, into an over-decline, and the readings that carry information are the situation readings A cannot use. (2) Decide G18: the frame-first assembler order, which is a builder change with a measured 90%-against-39% cache return, independent of the readings. (3) Route the situation readings to the call that asks the situation question when it exists (`104` §11.2 step 4, R-37), where "coursework or application essay?" is the question and not a distraction; the key, the shape and the layout carry over unchanged.

## 2. C_placement

### 2.1 Requirements, traced

What the prompt must obtain, what it must refuse, and the line that says so. The validator column names the check in `llm_harness/placement_validation.py` that stands behind the requirement, where one does.

| # | Requirement | `00` line / ruling | Validator |
|---|---|---|---|
| C-R1 | Choose among the retrieved legal nodes only; never invent, compose or describe a folder. | `00`:106, 116 ("no system component may invent a new destination after freeze") | `INVENTED_NODE`, `NODE_NOT_IN_FROZEN_TREE` |
| C-R2 | Decide, with citations, whether the file belongs to one approved child node, one approved parent node, an approved scoped fallback, or no destination. | `00`:110 | destination or `none` → `ABSTAIN` |
| C-R3 | Reason hierarchically: a level supported by the file's text is direct, a level supported only by an accepted group is context; a level that cannot be supported is not filled and the shallower approved path is chosen; the scoped General under the meaningful parent when no child's level holds. | `00`:111 | `SLOT_FILLED_WITHOUT_EVIDENCE` (support "unsupported"); per-level support words |
| C-R4 | A stated term, institution, project or course that disagrees with a candidate's expected value rules that candidate out; the conflict flags are read and every one is echoed. | `00`:107 (Duke vs Columbia; Spring 2025 vs 2026), `00`:114; §13.6 (shown, the model reconciles) | `CONFLICT_IGNORED` |
| C-R5 | Shared material: prefer a shared branch; with none, do not choose one home arbitrarily — abstain so the person is asked. | `00`:113 | none (the prompt's) |
| C-R6 | A file connected only by a generic hub, a resemblance or a mere retrieval stays uncertain; a semantic neighbour alone is insufficient. | `00`:63, 109, 116 | `GENERIC_HUB_ONLY` (payload flag) |
| C-R7 | Every asserted level cites the evidence item it came from, quoted exactly; nothing outside `released_evidence` is citable. | `00`:42, 114 | `CITATION_*`, `UNCITED_CLAIM` |
| C-R8 | Correct abstention is a successful outcome and costs nothing; when the two are close, abstain. | `00`:114 | `ABSTAIN` recorded |
| C-R9 | The model decides; rules validate structure only. The unique direct match is the top-ranked candidate, not a bypass. | `00` Amendments (placement), §13.5 | — |
| C-R10 | Refinement (deeper inside the file's own folder) is the model's call; removal (out of the person's arrangement) is named so the product can surface it. | `00` Amendments (preserving structure), §13.8 | — (`refinement` key, read by the caller) |
| C-R11 | Two spellings of one thing — the file's and the person's label — are reconciled by the model, from the evidence, never by an alias table. | constitution 1; `104` §11.2 step 6 | — |
| C-R12 | Never fill a missing slot because a complete-looking path is preferable; never move an uncertain file because it resembles a folder. | `00`:111, 116 | — |
| C-R13 | The response is one JSON object, one claim, in the recorded shape; a malformed value destroys the answer. | `76` R15, R16 (inherited) | `SCHEMA_INVALID` |
| C-R14 | The contract's two numbers, `support` and `next_support`, must be present and pass the deployment's threshold and margin or the answer is `weak`. | `00`:114 two-condition rule as the validator applies it; in tension with §13.5 (see G6) | `BELOW_SUPPORT_THRESHOLD`, `INSUFFICIENT_MARGIN` |
| C-R15 | Nothing about the person: no inference about who they are or what they do. | ruling recorded at `privacy/vocabulary.py:161`, inherited from the ratified A_fact text | — |

### 2.2 The two candidates

Both texts share the dossier description, the shape, the rules and the abstention paragraph, and differ only in `HOW TO DECIDE`:

- **walk** (`c_placement.unratified.walk.2026-09-06`, 10,608 B): the `00`:111 procedure stated as a walk from the top of the tree down, one level at a time, stopping at the deepest supported level; disagreements and resemblances are named after the walk.
- **eliminate** (`c_placement.unratified.eliminate.2026-09-06`, 10,491 B): the same content ordered as elimination — strike contradicted candidates, strike resemblance-only candidates, take the deepest fully supported survivor, count survivors — with the tie rule expressed as "two standing is not a decision".

Both carry the same response schema (`c_placement_response_schema.json`) and shaping policy (`c_placement_shaping_policy.json`). The bench's C dossier carries each candidate as an evidence item of kind `candidate` whose `location` is the node's label chain with its expected values, and each accepted group as an `accepted_group` item; that shape is the builder change G3 asks for, and the text describes exactly those keys.

#### 2.2.1 The texts, traced by block (`103` §28.1 step 2)

The two texts are identical outside `HOW TO DECIDE`; the shared blocks are traced once, and the block that differs is traced per candidate. A block with no requirement behind it would be cut; none was found. The dossier key line is checked against `dossier._body`'s emitted keys by `tests/llm_harness/test_d2_draft_templates.py::test_the_text_is_a_constant_that_names_the_dossier_exactly`; the item kinds the text names (`candidate`, `accepted_group`, `excerpt`) are the bench's, and the live builder emits none of them (G3): the trace therefore holds for the dossier the text describes, not for the one `placement/pipeline.py` sends today.

| Block (both texts) | Sentences | Requirement |
|---|---|---|
| OUTPUT | one object, no fence, first `{` last `}` | C-R13; `76` R15 |
| WHAT YOU ARE DOING | choose among approved, frozen folders; cite | C-R1, C-R2, C-R7 |
| | not designing, naming, inventing; cannot describe a better one | C-R1 |
| | nothing about the person | C-R15 |
| WHAT THE DOSSIER CONTAINS | the key line | step 2 key check (test above) |
| | `allowed_vocabulary` complete; `none` always available | C-R1, C-R8 |
| | `candidate` item: label chain, expected values, "sits in that folder now" | C-R3 (levels), C-R10 (own folder), G3 |
| | `accepted_group` item: accepted vs merely retrieved; context support | C-R3 (context), C-R6 |
| | `excerpt` carries no text; `released_evidence` is the only text; no filename, no path | C-R7, `00`:42 |
| | `conflicts`: a flag is not a verdict; read, decide, echo every id | C-R4, §13.6 |
| | the rest is bookkeeping; no other files, no other answers | C-R15, `76` R2 |
| WHEN THE ANSWER IS "none" | correct, costs nothing; wrong placement stays, `none` is looked at; when close, `none` | C-R8 |
| | (walk only) the four `none` triggers enumerated | C-R5, C-R6, C-R7, C-R8; R2 (abstention specified) |
| | one sentence naming what was missing | C-R13 (`unknown` shape) |
| THE FILE'S OWN FOLDER | refinement vs out of own folder; both allowed; name which | C-R10, §13.8 |
| THE SHAPE | the two objects | C-R13, C-R14 (the two numbers) |
| Rule 1 | destination copied or `none`; a composed id is a folder that does not exist | C-R1 |
| Rule 2 | `direct` or `context`, no third word; an unfillable level is unfilled | C-R3, C-R12 |
| Rule 3 | value as the text spells it; context value from the group | C-R7, C-R11 |
| Rule 4 | citation shape; span copied; only `released_evidence` keys | C-R7 |
| Rule 5 | `why_it_supports` never empty; a sentence doing the text's work is no support | C-R7, C-R12 |
| Rule 6 | `support` / `next_support` as whole-number citation counts; equal means `none` | C-R14, G6 |
| Rule 7 | every conflict id echoed | C-R4 |
| Rule 8 | `refinement` closed set | C-R10 |
| Rule 9 | `unknown` present iff `none`; never false/null | C-R13 |
| Rule 10 | one malformed value destroys the answer | C-R13 |
| closing | rules check anchoring, not truth; do not shape to pass | C-R9, §13.5 |

| HOW TO DECIDE, eliminate | Requirement | HOW TO DECIDE, walk | Requirement |
|---|---|---|---|
| First: strike every contradicted candidate; a flag points, the text confirms | C-R4 | Walk top down, stop at the deepest supported level; direct / context / unfilled; deeper only if supported; scoped fallback | C-R3, C-R12 |
| Second: strike resemblance-only support (shared word, look-alike number, contained word, kind-resemblance, merely-retrieved group) | C-R6, C-R12, `00`:239 | Two spellings can be one thing; the model judges; if it cannot tell, not the same | C-R11 |
| Third: deepest fully supported survivor; direct / context / unfilled; shallower stands; scoped fallback | C-R3, C-R12 | A disagreement is a reason to stop; all disagree means `none` | C-R4 |
| Two spellings can be one thing | C-R11 | Some things look like support and are not (same list) | C-R6, C-R12 |
| Fourth: count what is left; two standing and no shared branch is `none` | C-R5, C-R8, C-R14 | | |

Requirements with no sentence of their own: C-R9 and C-R10 are carried by the closing and the own-folder block; C-R5's positive half ("prefer a shared branch") is stated only inside the count step, which is the C05 wording gap §2.3 measured.

### 2.3 Results (cloud, deepseek-chat, 16 cases × 2 candidates = 32 calls; local, qwen3:8b, eliminate 16 of 16 and walk 16 of 16)

| arm | schema-valid | validator ok | grounding | abstain on should-abstain | correct on should-answer | correct **and** accepted | false abstain | accepted | median s | tokens (prompt / completion) |
|---|---|---|---|---|---|---|---|---|---|---|
| walk / cloud | 16 / 16 | 16 / 16 | 20 / 22 (0.909) | **4 / 4** | **11 / 12** | 8 / 12 | 1 / 12 | 8 / 16 | 2.1 | 82,529 / 3,053 |
| eliminate / cloud | 16 / 16 | 16 / 16 | 19 / 20 (0.950) | **4 / 4** | **11 / 12** | 8 / 12 | 1 / 12 | 8 / 16 | 1.9 | 82,017 / 2,867 |
| eliminate / local | 14 / 16 | 14 / 16 | 22 / 31 (0.71) | **0 / 4** | 7 / 12 | 4 / 12 | 0 / 12 | 7 / 16 | 64.13 (load 1m 4.67 / 12.7 / 83.59) | 82,017 / 4,816 (`num_ctx` 16,384) |
| walk / local | 15 / 16 | 16 / 16 | 26 / 34 (0.765) | **0 / 4** | 8 / 12 | 3 / 12 | 0 / 12 | 6 / 16 | 76.41 (load 1m 3.14 / 4.4 / 5.33) | 82,497 / 5,207 (`num_ctx` 16,384) |

**A tie on the two metrics that matter, broken by what failed.** Both texts placed 11 of 12 answerable files correctly and abstained on all 4 should-abstain files (the generic hub, the invoice number, the noise OCR, the two-home transcript). Both false-abstained on the same case, C05 — the transcript with a shared branch on the list: each demanded that the file's own text name a university and did not treat two accepted-group memberships as support for the shared-material node. That is a wording gap in both, and the v2 sentence is known: *a shared branch is supported by the two groups the file belongs to*.

Where they differ is how a correct answer was lost at the validator. **walk** lost C02 and C13 to `CITATION_NOT_IN_DOSSIER`: its "context" support invited the model to cite the `accepted_group` item as a metadata field, which the text forbids and the model did anyway (2 of 16). **eliminate** lost C16 to `CITATION_SPAN_MISMATCH` (it cited the word `essay`, which the body sentence does not contain — an honest span error) and C07 to a self-declared tie (`support` 1, `next_support` 1 on the refinement case, the two-condition rule turning a right answer into `weak`, G6). Both lost C06 to `CONFLICT_IGNORED`, which is G1 and not the text's. The local arm is read separately below, because it fails in a different place.

**Winner: eliminate**, provisionally — equal on placement and abstention, ahead on grounding (0.950 vs 0.909), and its two losses are one span error and one honest tie rather than a rule the text states and the model breaks. The v2 to measure before ratification: eliminate's ordering, plus one sentence making the shared-branch case explicit and one making "a group is support, not a citation" unmissable.

**The local arm (qwen3:8b, thinking off, `num_ctx` 16,384, `prompt_eval_count` 5,137 to 5,222, `done_reason: stop` on every call) does not abstain, under either text.** On the complete eliminate run it answered all four should-abstain cases: it placed the two-home transcript (C04) in one packet by citing the `accepted_group` item as if it were evidence; it placed the generic-hub file (C09) in the essays node on the span `columbia.edu`; it placed the noise screenshot (C15) in a portal-records node on the span `2O26`; and it placed the invoice (C11) in the course folder because `Invoice 1401` "matches the PHYS1401 course code" — the look-alike number of `00`:239, taken as a code; that one was rejected on a span mismatch in its second citation, not on the reasoning. Two of those four (C09, C15) were **accepted by the validator** — the citations resolve and the spans are in the values — which is S1 exactly: a grounded, cited, wrong placement that only the person catches. On the twelve answerable cases it was right 7 times and 3 of those 7 were then rejected `CITATION_NOT_IN_DOSSIER` for citing a `candidate` or `accepted_group` item (8 such citations in 16 calls, against walk/cloud's 2), so correct-and-accepted is 4 of 12 against the cloud's 8 of 12. It got the refinement case (C07) wrong under both texts, choosing the course folder over the lecture child, and it wrote `refinement: deeper_in_own_folder` on 11 of 16 answers including cases where no candidate was marked as the file's folder. Two responses were `SCHEMA_INVALID` (C03, C06). Latency: eliminate's median 64 s at a one-minute load between 4.7 and 18 once the suite had finished (194 s for its first call at load 84); walk's median 76 s, its first seven calls made before the reboot at 219 to 453 s under loads above 200 (those seven predate the load recording and carry none) and its last nine at 62 to 152 s under a load of 3 to 5. The load is in every record made after the reboot, beside the latency.

What the local arm changes and does not change. It does not change the ranking — walk was right on 8 of 12 answerable cases and eliminate on 7, walk grounded 0.765 and eliminate 0.71, and both answered every should-abstain case, mostly the same way — and it does not change what the texts need (the group-is-not-a-citation sentence is now a local-arm necessity, not a polish). It does change what can be ratified for the local tier: on this evidence an 8B model without thinking cannot be trusted with C's abstention cases under any wording measured here, and `104` §12.2's condition for the local tier ("local reaches at least the cloud run's correct fields with 0 wrong placements") is not met at C. The honest options are the ones `104` R-18 already names: the local model with thinking on and a separated budget, measured again; a larger local model; or C on the cloud tier only.

### 2.4 Stress cases

Rendered by `python3 -m tools.promptbench tables --site C_placement --out tools/promptbench/out/C_placement`; the local arms and eliminate-v2 included.

| case | persona | traces | expectation | eliminate / cloud | eliminate / local | eliminate-v2 / cloud | walk / cloud | walk / local |
|---|---|---|---|---|---|---|---|---|
| C01 — a syllabus that uniquely matches one node | Priya | 00:110, 104:13.5 | answer: `{"destination":"n-02"}` | correct / acc_direct | correct / acc_direct | correct / acc_direct | correct / acc_direct | correct / acc_direct |
| C02 — a sparse homework file placed through its accepted group | Priya | 00:108, 00:111 | answer: `{"destination":"n-03"}` | correct / acc_direct | correct / reject CITATION_NOT_IN_DOSSIER | correct / acc_direct | correct / reject CITATION_NOT_IN_DOSSIER | correct / reject CITATION_NOT_IN_DOSSIER |
| C03 — a term the deeper node carries and the file contradicts | Priya | 00:111, 00:107 | answer: `{"destination":"n-03"}` | correct / acc_direct | WRONG / reject SCHEMA_INVALID | correct / acc_direct | correct / acc_direct | correct / reject CITATION_NOT_IN_DOSSIER |
| C04 — a transcript with two supported homes and no shared branch | multi-life | 00:113, 00:239 | abstain: `{"destination":"none"}` | abstained / abstain | ANSWERED / reject CITATION_NOT_IN_DOSSIER | abstained / abstain | abstained / abstain | ANSWERED / reject CITATION_NOT_IN_DOSSIER |
| C05 — the same transcript when a shared branch exists | multi-life | 00:113 | answer: `{"destination":"n-11"}` | false abstain / abstain | WRONG / reject CITATION_NOT_IN_DOSSIER | correct / weak INSUFFICIENT_MARGIN | false abstain / abstain | WRONG / reject CITATION_NOT_IN_DOSSIER |
| C06 — a Duke essay retrieved by a Columbia packet, with the conflict recorded | multi-life | 00:107, 00:112, 00:114 | answer: `{"destination":"n-13"}` | correct / reject CONFLICT_IGNORED | WRONG / reject SCHEMA_INVALID | correct / reject CONFLICT_IGNORED | correct / reject CONFLICT_IGNORED | WRONG / reject CONFLICT_IGNORED |
| C07 — refinement: a lecture sitting in its own course folder | multi-life | 104:13.8, 00:22 | answer: `{"destination":"n-15","refinement":"deeper_in_own_folder"}` | correct / weak INSUFFICIENT_MARGIN | WRONG / acc_direct | correct / acc_direct | correct / acc_direct | WRONG / acc_direct |
| C08 — removal: a report card in the folder its parent keeps it in | Tom | 104:13.8, 00:22, 68:F5 | answer: `{"destination":"n-17","refinement":"out_of_own_folder"}` | correct / acc_direct | correct / acc_direct | correct / acc_direct | correct / acc_direct | correct / acc_direct |
| C09 — a file linked only by a generic hub | multi-life | 00:63, 00:109 | abstain: `{"destination":"none"}` | abstained / abstain | ANSWERED / acc_direct | abstained / abstain | abstained / abstain | ANSWERED / acc_direct |
| C10 — MIT inside submit | Priya | 00:43, 00:239 | answer: `{"destination":"n-03"}` | correct / acc_direct | correct / reject CITATION_NOT_IN_DOSSIER | correct / acc_direct | correct / acc_direct | correct / reject CITATION_NOT_IN_DOSSIER,CITATION_SPAN_MISMATCH |
| C11 — a number that is an invoice, not a course | Tom | 00:239, 00:46 | abstain: `{"destination":"none"}` | abstained / abstain | ANSWERED / reject CITATION_SPAN_MISMATCH | abstained / abstain | abstained / abstain | ANSWERED / weak INSUFFICIENT_MARGIN |
| C12 — a course file with no recoverable kind of work | Priya | 00:99, 00:111 | answer: `{"destination":"n-05"}` | correct / acc_direct | WRONG / reject CITATION_NOT_IN_DOSSIER | correct / acc_direct | correct / acc_direct | WRONG / reject CITATION_NOT_IN_DOSSIER |
| C13 — a packet member placed inside its confirmed packet | multi-life | 00:112 | answer: `{"destination":"n-09"}` | correct / acc_direct | correct / reject CITATION_NOT_IN_DOSSIER | correct / acc_direct | correct / reject CITATION_NOT_IN_DOSSIER | correct / weak INSUFFICIENT_MARGIN |
| C14 — an essay naming the author's school and the target university | multi-life | 00:44, 104:11.1 | answer: `{"destination":"n-21"}` | correct / acc_direct | correct / acc_direct | correct / acc_direct | correct / acc_direct | correct / acc_direct |
| C15 — a screenshot whose OCR is noise | multi-life | 00:110, 00:125 | abstain: `{"destination":"none"}` | abstained / abstain | ANSWERED / acc_direct | abstained / abstain | abstained / abstain | ANSWERED / acc_direct |
| C16 — a university course essay whose own course node exists | multi-life | 104:11.1, 00:44 | answer: `{"destination":"n-23"}` | correct / reject CITATION_SPAN_MISMATCH | correct / acc_direct | correct / acc_direct | correct / acc_direct | correct / reject CITATION_SPAN_MISMATCH |

### 2.5 Contract gaps found at C

G1 (conflict ids keyed on the wire, compared raw — C06 measured), G2 (R-15, a real `project` value is "invented"), G3 (no node profiles, opaque ids — the bench supplies them), G6 (the two numbers — C07 measured), in §7.

### 2.6 The ratification question

Ratify **eliminate** (`c_placement.unratified.eliminate.2026-09-06`), its response schema and shaping policy, **conditional on**: (a) the builder change G3 (candidate profiles as `candidate` items; accepted groups as `accepted_group` items) that the text describes; (b) G1 fixed or C wired with `conflicts=()` until it is; (c) a decision on G6 — keep `support`/`next_support` as whole-number citation counts with the tie-means-none rule, or drop the two-condition rule from the model path. And authorise a v2 measurement (the shared-branch sentence and the group-is-not-a-citation sentence) before the text is installed. For the local tier, do not ratify any C text for `qwen3:8b` with thinking off: it abstained on 0 of 4 should-abstain cases under both texts and two of its wrong placements passed the validator; decide whether the local arm is re-measured with thinking on (`104` R-18) or C stays cloud-only.


**The two known limits, stated the way `82` §0 states S1 and S2.** S1, what the text cannot catch: a placement that is grounded, cited and wrong — the model choosing a sibling folder that the same quoted span also fits (C05's shared branch, C07's own-folder child). Nothing in the wording prevents it; only the person's confirmation does, and the text is written so that the model's `alternatives` and `refinement` name the case. S2, what the validator catches instead: an identifier not on the list, a citation that does not resolve or whose span is not in the value, a level marked with a third support word, an unechoed conflict id, a malformed object. G1 and G6 are the two places where the validator catches a correct answer.

### 2.7 eliminate-v2, measured (cloud, 16 calls)

The stated delta from eliminate: (1) a group is support for a level and never a citation; (2) a candidate described as a shared branch, serving two accepted groups the file belongs to, stands alone with its levels marked `context`; (3) `refinement` is `not_applicable` unless a candidate's description says the file sits in it now.

| arm | schema-valid | validator ok | grounding | abstain on should-abstain | correct on should-answer | correct **and** accepted | false abstain | accepted | median s | tokens |
|---|---|---|---|---|---|---|---|---|---|---|
| eliminate / cloud | 16 / 16 | 16 / 16 | 19 / 20 (0.950) | 4 / 4 | 11 / 12 | 8 / 12 | 1 / 12 | 8 / 16 | 1.9 | 82,017 / 2,867 |
| eliminate-v2 / cloud | 16 / 16 | 16 / 16 | **21 / 21 (1.0)** | 4 / 4 | **12 / 12** | **10 / 12** | **0 / 12** | 10 / 16 | 1.9 | 84,193 / 3,028 |

Every answerable case placed correctly and every should-abstain case abstained. C05, the shared-branch transcript both v1 texts false-abstained on, is now placed on the shared branch — and comes back `weak`, `INSUFFICIENT_MARGIN`: the model wrote `support` 1 and `next_support` 1, which is honest (each of the two groups supports the branch equally and the file's own text supports neither packet more) and is exactly the two-condition rule turning a right answer into a non-answer (G6, the third time). C06 is still G1. The C16 span error of v1 did not recur; on one run that is noise, not the sentence. On the cloud, v1 already wrote `not_applicable` where it should, so sentence (3) is for the local arm, where v1 wrote `deeper_in_own_folder` on 11 of 16 answers; it is unmeasured locally.

**eliminate-v2 is the C text put forward**, in place of eliminate, on this run: it loses nothing v1 had and gains the shared-branch case. The two losses that remain are both the validator's (G1, G6), not the text's.

## 3. D_residual

### 3.1 Requirements, traced

| # | Requirement | `00` line / ruling | Validator |
|---|---|---|---|
| D-R1 | Choose from the controlled action set of eight and nothing else; the model is not asked to invent a folder. | `00`:124 | `ACTION_NOT_IN_CONTROLLED_SET` |
| D-R2 | A target is an approved residual area or an approved broad parent branch already in the frozen tree; a path is a folder invented. | `00`:119-121 (the library prevents `Random PDF Things`, `Travel/Gate B12`), 126 | `DESTINATION_NOT_IN_FROZEN_TREE`, `INVENTED_FOLDER` |
| D-R3 | A credible connection to an accepted project, course, application, event or career group returns the file to the group-aware engine; it is never trapped in a residual folder. | `00`:125 (the Columbia confirmation), 126 | `STRONGER_RELATIONSHIP_OVERLOOKED` (flags echoed) |
| D-R4 | Reason from broad to narrow and stop as soon as the evidence is no longer strong enough; an isolated file stays high in the tree. | `00`:124 | — |
| D-R5 | A gate number does not identify a trip; the broad approved destination with an explanation, or the screenshot area, or leave in place. | `00`:125 | — |
| D-R6 | Recipe, product, quote, inspiration → Reference Clips if approved; unreadable screenshot → generic, in place or the screenshot inbox; the model must be allowed to conclude that no meaningful association exists. | `00`:125 | — |
| D-R7 | Every recommendation cites OCR text, extracted content, metadata or approved group context; the evidence must appear in the file's own record. | `00`:126 | `CITATION_*`, `EVIDENCE_NOT_IN_FILE_RECORD` |
| D-R8 | Sensitivity: protected material is marked, never filed; the model does not ignore a restriction. | `00`:120 (Protected Records), 126, 185 | `SENSITIVITY_RESTRICTION_IGNORED`; `mark_protected_or_unsupported` |
| D-R9 | Leave in place, Review Later and abstain are correct results, especially for screenshots and one-off images where the temptation to invent a narrative is high. | `00`:126 | `LEAVE_IN_PLACE`, `REVIEW_LATER`, `ABSTAIN` dispositions |
| D-R10 | Review-only and leave-in-place areas never move a file; the area's disposition is the person's. | `00`:121 | P10 node disposition (not the model's) |
| D-R11 | No numeric support keys: the two-condition rule is site C's only. | validator contract (`site_d_support_rule`) | `ValidationUnavailable` if both present |
| D-R12 | One JSON object, one claim, the recorded shape. | `76` R15, R16 (inherited) | `SCHEMA_INVALID` |
| D-R13 | Nothing about the person. | inherited | — |

### 3.2 The two candidates

- **ladder** (`d_residual.unratified.ladder.2026-09-06`, 10,748 B): `00`:124's broad-to-narrow rule as five rungs in fixed order — return, mark, area, broad parent, then the person decides — with "the higher the rung, the more you must be able to cite".
- **shelves** (`d_residual.unratified.shelves.2026-09-06`, 11,249 B): the approved areas as labelled shelves; two questions before the shelves (return; protected/unreadable), then the one shelf whose description the text satisfies, then what a description never says — the counter-examples of `00`:125 made explicit per shelf.

Both share `d_residual_response_schema.json` and `d_residual_shaping_policy.json`. In the bench dossier every approved area and every return branch is an evidence item (`residual_area`, `branch`) whose `location` carries the area's label chain, disposition and holds sentence — the "user-approved residual library" and "representative examples" of `00`:124 that the live builder does not yet carry (G3); a return's target is the branch node built from the group, because the validator requires a frozen node (G8); and every cited item's `location` is the subject ref (G5).

#### 3.2.1 The texts, traced by block

Shared blocks once; `HOW TO DECIDE` per candidate. Item kinds `residual_area` and `branch` are the bench's (G3, G8).

| Block (both texts) | Sentences | Requirement |
|---|---|---|
| OUTPUT | one object | D-R12 |
| WHAT YOU ARE DOING | one action of eight; name the home; cite | D-R1, D-R7 |
| | not naming, describing, inventing a folder; a home not on the list does not exist | D-R2 |
| | nothing about the person | D-R13 |
| WHAT THE DOSSIER CONTAINS | key line | step 2 key check |
| | `residual_area`: name, disposition, holds | D-R2, D-R6, D-R10 (disposition shown), G3 |
| | `branch`: built from a confirmed group or accepted packet, or a broad parent | D-R3, D-R2, G8 |
| | `released_evidence`: recognised, extracted, metadata, manifest; nothing else exists | D-R7 |
| | `conflicts` of kind `stronger_relationship`: read, decide, echo | D-R3 |
| THE EIGHT ACTIONS | each action with its target rule | D-R1; returns D-R3; destination and broad parent D-R2; mark D-R8; the three no-target actions D-R9 |
| WHEN THE ANSWER NAMES NO HOME | correct, costs nothing; wrong home is a folder to unpick; when close, none | D-R9 |
| THE SHAPE | two objects, no numeric keys | D-R12, D-R11 |
| Rule 1 | action copied; no ninth | D-R1 |
| Rule 2 | target rules per action; a slash is an invented folder | D-R2 (`Travel/Gate B12`) |
| Rule 3 | cite when a target is named; citation shape; only `released_evidence` | D-R7 |
| Rule 4 | `why_it_supports` never empty | D-R7 |
| Rule 5 | `stop_reason` required | D-R4 |
| Rule 6 | every flag echoed | D-R3 |
| Rules 7, 8 | `unknown` discipline; one malformed value | D-R12 |
| closing | anchoring, not truth | §13.5 |

| HOW TO DECIDE, ladder | Requirement | HOW TO DECIDE, shelves | Requirement |
|---|---|---|---|
| Rung 1: a group or packet named by the text is a return; never filed in a residual home | D-R3 | Before the shelves: named group or packet is a return | D-R3 |
| Rung 2: protected or unreadable; mark; nothing else chosen | D-R8 | Before the shelves: protected or unreadable | D-R8 |
| Rung 3: an approved area, with the five kinds `00`:125 names | D-R6 | The shelves: the one shelf whose description the text satisfies; two equally is review later | D-R6, D-R9 |
| Rung 4: broad parent only when no area fits | D-R2, D-R4 | No shelf but a broad branch plainly right | D-R2, D-R4 |
| Rung 5: review later / leave / abstain, each with its trigger | D-R9 | After the shelves: the three no-home answers with triggers | D-R9 |
| The higher the rung the more you cite; an isolated file stays high | D-R4, D-R7 | Per-shelf "holds / does not hold" including review-only never moves a file | D-R6, D-R10 |
| Looks like an association and is not: gate, seat, booking; a name is not an application; a date is not an event; a broad branch is not a home for a file that says nothing about it | D-R5, `00`:239 | What a description never says (same list) | D-R5 |

D-R10 (review-only areas never move a file) has a sentence in shelves and none in ladder; the disposition is the node's, enforced by P10, so the omission costs nothing at the validator, but a ladder v2 should carry it. D-R11 is satisfied by absence: neither shape has a numeric key.

### 3.3 Results (cloud, deepseek-chat, 15 cases × 2 candidates = 30 calls; local, qwen3:8b, 30 of 30)

| arm | schema-valid | validator ok | grounding | abstain on should-abstain | correct on should-answer | correct **and** accepted | false abstain | accepted | median s | tokens (prompt / completion) |
|---|---|---|---|---|---|---|---|---|---|---|
| ladder / cloud | 15 / 15 | 15 / 15 | 20 / 20 (1.0) | 1 / 2 | **12 / 13** | 11 / 13 | 1 / 13 | 12 / 15 | 2.2 | 78,469 / 2,752 |
| shelves / cloud | 15 / 15 | 15 / 15 | 21 / 21 (1.0) | 1 / 2 | 11 / 13 | 10 / 13 | 1 / 13 | 12 / 15 | 2.0 | 79,759 / 2,870 |
| ladder / local | 14 / 15 | 15 / 15 | 23 / 24 (0.958) | **0 / 2** | 10 / 13 | 8 / 13 | 0 / 13 | 13 / 15 | 47.6 (load 1m 2.9 / 4.2 / 4.8) | 77,952 / 3,474 (`num_ctx` 16,384) |
| shelves / local | 12 / 15 | 15 / 15 | 20 / 20 (1.0) | **0 / 2** | 11 / 13 | 9 / 13 | 0 / 13 | 13 / 15 | 59.2 (load 1m 3.5 / 5.1 / 7.0) | 79,197 / 3,438 (`num_ctx` 16,384) |

Every citation resolved and span-matched under both texts (41 of 41). The one case that separates them is D02, the boarding-gate screenshot when the person has approved `Personal > Travel > Confirmations`: **ladder** chose it, as `00`:125 says; **shelves** chose Receipts and Confirmations — its own shelf description ("does not hold a trip, because there is no trip shelf unless the person made one") was overridden by the transactional reading. Both returned the admissions confirmation to the Columbia branch (D01) and the course reading to the course branch (D10), both marked the encrypted archive unsupported and the redacted statement protected, both refused the unrelated broad parent (D15), both chose Reference Clips for the recipe and Reading Inbox for the DOI paper, and both left the gate screenshot at Temporary Screenshots when no travel area existed (D03).

The two "should-abstain" misses are the same under both and are worth reading: D14 (nothing readable) was marked `unsupported` rather than abstained — labelled as also acceptable, so it is a correct answer the abstention metric counts against; D05 (noise OCR, no context) was `abstain` where the label wanted "leave in place" or the screenshot area — the model treated unreadable OCR as nothing to read at all. D08 is G1: both texts echoed the flagged relationship id and were rejected `STRONGER_RELATIONSHIP_OVERLOOKED` for it.

**Ahead on the cloud run: ladder**, on D02 alone and on equal ground everywhere else — one case, one run.

**The local arm (qwen3:8b, thinking off, run 19:51 to 20:18 at a one-minute load of 2.9 to 7.0, 38 to 83 s per call) reverses the one case the cloud ranking rested on and adds a safety miss the validator cannot see.** On D02 both local texts chose Receipts and Confirmations for the gate screenshot, which is what shelves did on the cloud and ladder did not: ladder's cloud win on D02 does not reproduce under the local model. Both local texts placed the statement with a redacted account number (D13) in Receipts and Confirmations, **accepted by the validator** — a protected record filed as a transactional one, D-R8 failed under both wordings at the second rung. It was accepted because nothing could refuse it: the D13 dossier carries no sensitivity flag (the case is the redaction marker in the heading and nothing else), the bench supplies the validator's `sensitivity_policy` dependency as a stub that returns true, and the product's own composition passes it as `None` (`cli.py:4126`, the absent model path), so `SENSITIVITY_RESTRICTION_IGNORED` is a reason with no implementation behind it anywhere (G17). Until one exists this is S1 with nothing on the S2 side: a protected record filed into an approved area is caught by no one but the person. Neither abstained on either should-abstain case: D14 (nothing readable) went to the unsupported-material area under both, and D11 (the unclear spreadsheet) to Review Later's area rather than the `mark_review_later` action — the local model reaches for a `residual_area` target where the text offers a no-target action. ladder also mis-shelved the certificate (D12, to Receipts) and cited a `branch` item on D15 (`CITATION_NOT_IN_DOSSIER`); shelves returned D01 and D08 with no citations at all (`UNCITED_CLAIM`, 2 of 15), and its `json_schema_valid` is 12 of 15 to ladder's 14 of 15, both under Ollama's `format: json` grammar (R1). On correctness the local arm has shelves ahead, 11 of 13 to 10 of 13, and 9 to 8 once accepted.

Across both models the two texts are level: ladder 22 of 26 answerable cases right, shelves 22 of 26; both 1 of 4 on the should-abstain cases. The one-case cloud margin and the one-case local margin point opposite ways, which is what one run at temperature 0 can do and why `104` §13.4 asks for three. What the local arm does establish, on 30 calls under two wordings, is the same thing the C arm established: an 8B model with thinking off does not take the no-target actions, and files protected material into an approved area when a span fits.

### 3.4 Stress cases

Rendered by `python3 -m tools.promptbench tables --site D_residual --out tools/promptbench/out/D_residual` after the local arm.

| case | persona | traces | expectation | ladder / cloud | ladder / local | shelves / cloud | shelves / local |
|---|---|---|---|---|---|---|---|
| D01 — an admissions confirmation screenshot is not a generic screenshot | multi-life | 00:125, 00:126 | answer: `{"action_in":["return_to_accepted_graph_or_purpose_packet","return_to_confirmed_domain_...` | correct / acc_direct | correct / acc_direct | correct / acc_direct | correct / reject UNCITED_CLAIM |
| D02 — a boarding gate screenshot when a travel confirmations area is approved | multi-life | 00:125 | answer: `{"action":"choose_approved_residual_destination","target":"r-09"}` | correct / acc_direct | WRONG / acc_direct | WRONG / acc_direct | WRONG / acc_direct |
| D03 — the same gate screenshot with no travel area, Temporary Screenshots approved | multi-life | 00:125 | answer: `{"action":"choose_approved_residual_destination","target":"r-01","also_acceptable":[["l...` | correct / acc_direct | correct / acc_direct | correct / acc_direct | correct / acc_direct |
| D04 — a recipe screenshot | Tom | 00:125 | answer: `{"action":"choose_approved_residual_destination","target":"r-03"}` | correct / acc_direct | correct / acc_direct | correct / acc_direct | correct / acc_direct |
| D05 — a screenshot with unreadable OCR and no context | multi-life | 00:125, 00:239 | answer: `{"action":"leave_in_current_location","also_acceptable":[["choose_approved_residual_des...` | false abstain / abstain | correct / acc_direct | false abstain / abstain | correct / acc_direct |
| D06 — an encrypted archive | Mara | 00:31, 00:120 | answer: `{"action":"mark_protected_or_unsupported","target":"unsupported","also_acceptable":[["c...` | correct / acc_direct | correct / acc_direct | correct / acc_direct | correct / acc_direct |
| D07 — a boarding pass with no travel area and Receipts approved | multi-life | 00:120, 00:125 | answer: `{"action":"choose_approved_residual_destination","target":"r-05"}` | correct / acc_direct | correct / acc_direct | correct / acc_direct | correct / acc_direct |
| D08 — a figure with a stronger relationship the dossier flags | multi-life | 00:126, 00:63 | answer: `{"action_in":["return_to_accepted_graph_or_purpose_packet","return_to_confirmed_domain_...` | correct / reject STRONGER_RELATIONSHIP_OVERLOOKED | correct / reject STRONGER_RELATIONSHIP_OVERLOOKED | correct / reject STRONGER_RELATIONSHIP_OVERLOOKED | correct / reject UNCITED_CLAIM |
| D09 — a paper with a DOI and no course or project | Priya | 00:120 | answer: `{"action":"choose_approved_residual_destination","target":"r-06"}` | correct / acc_direct | correct / acc_direct | correct / acc_direct | correct / acc_direct |
| D10 — a paper the course lists as required reading | Priya | 00:126 | answer: `{"action_in":["return_to_confirmed_domain_group","return_to_accepted_graph_or_purpose_p...` | correct / acc_direct | correct / acc_direct | correct / acc_direct | correct / acc_direct |
| D11 — a spreadsheet whose purpose is unclear | Tom | 00:122, 00:124 | abstain: `{"action":"mark_review_later"}` | abstained / abstain | ANSWERED / acc_direct | abstained / abstain | ANSWERED / acc_direct |
| D12 — a standalone certificate | Tom | 00:120 | answer: `{"action":"choose_approved_residual_destination","target":"r-04"}` | correct / acc_direct | WRONG / acc_direct | correct / acc_direct | correct / acc_direct |
| D13 — a statement whose account number was redacted before release | Tom | 00:120, 00:185 | answer: `{"action":"mark_protected_or_unsupported","target":"protected"}` | correct / acc_direct | WRONG / acc_direct | correct / acc_direct | WRONG / acc_direct |
| D14 — nothing readable at all | Mara | 00:124, 00:126 | abstain: `{"action":"abstain","also_acceptable":[["mark_protected_or_unsupported","unsupported"]]}` | ANSWERED / acc_direct | ANSWERED / acc_direct | ANSWERED / acc_direct | ANSWERED / acc_direct |
| D15 — a gate screenshot offered an unrelated broad parent | multi-life | 00:124, 00:125 | answer: `{"action":"choose_approved_residual_destination","target":"r-01","also_acceptable":[["l...` | correct / acc_direct | correct / reject CITATION_NOT_IN_DOSSIER | correct / acc_direct | correct / acc_direct |

### 3.5 Contract gaps found at D

G1 (relationship ids keyed vs raw — D08 measured), G3 (no area profiles), G5 (same-file check is fail-open on keyed citations), G17 (the sensitivity check has no implementation — D13 measured), G7 (broad parent and residual destination collapse to one disposition; only the injected `residual_action_of` keeps them apart), G8 (a return's target must be a frozen node), in §7.

### 3.6 The ratification question

Ratify **ladder** (`d_residual.unratified.ladder.2026-09-06`), its response schema and shaping policy, conditional on the same builder change as C (area and branch profiles as items, G3), on G8's reading (a return names the branch built from the group), and on G1 being fixed or D wired with `conflicts=()`; and confirm that `residual_action_of` reads the eight actions from the response payload (G7). The ratification is of the cloud tier: under the local model the two texts are level and both filed a protected record into an approved area, so no D text is put forward for `qwen3:8b` with thinking off until a local run at a different setting (thinking on, `104` R-18) shows the second rung holding.


**The two known limits.** S1, what the text cannot catch: a wrong destination among valid ones when the text says nothing that distinguishes two approved areas (D02 is the measured instance: a boarding pass is both transactional and a travel confirmation, and the text can only say which reading `00`:125 prefers). S2, what the validator catches: a ninth action, a target off the list or containing a slash, an unresolved citation, an unechoed relationship id, a numeric support key, a malformed object. G1 and G5 are where the validator catches or fails to catch the wrong thing.

## 4. B_group

### 4.1 Requirements, traced

| # | Requirement | `00` line / ruling | Validator |
|---|---|---|---|
| B-R1 | Four constrained tasks: coherence, per-member inclusion, outliers and conflicts, and — only if coherent — a label and a category. | `00`:59 | `LABEL_WITHOUT_COHERENCE` |
| B-R2 | Direct anchors and context-supported candidates arrive apart and are judged apart: a group can be coherent while a member stays uncertain. | `00`:58, 60 | outcome `accept_context_supported` from cited bases |
| B-R3 | Members are only the files the dossier lists; the model invents none. | `00`:59 | `INVENTED_MEMBERSHIP` |
| B-R4 | Each membership decision carries an exact quote, a metadata field, a graph relationship or an explicit statement of insufficiency. | `00`:59 | citations; per-member `evidence_refs` (bench-checked) |
| B-R5 | No folder hierarchy, no inferred date, project or purpose. | `00`:59, 62 | `FOLDER_HIERARCHY_PROPOSED`, `INVENTED_DATE/PROJECT/PURPOSE` |
| B-R6 | A course code alone does not merge different terms. | `00`:63 | `TERM_MERGE_UNSUPPORTED` |
| B-R7 | An application packet does not absorb a document with a conflicting target institution. | `00`:62 | `CONFLICTING_TARGET_INSTITUTION` |
| B-R8 | A group bridged only by embeddings, one high-frequency entity or generic similarity is not formed; a university name alone is not a basis. | `00`:63 | `GENERIC_SIMILARITY_ONLY` |
| B-R9 | Purpose coherence needs direct application evidence; a download session alone is never sufficient. | `00`:61, 45 | — |
| B-R10 | A file may validly belong to more than one accepted group. | `00`:63, 113 | — |
| B-R11 | The label is a proposal the person confirms or renames; the category is one of the shown identifiers. | `00`:59; §13.7 (model names, user confirms) | — (category not validated: G4) |
| B-R12 | Abstention ("no", "insufficient") is a correct outcome and the group is not surfaced. | `00`:62, 63 | `WEAK`/`ABSTAIN` dispositions |
| B-R13 | One JSON object, one claim, the recorded shape; nothing about the person. | inherited | `SCHEMA_INVALID` |

### 4.2 The two candidates

- **four-questions** (`b_group.unratified.four-questions.2026-09-06`, 10,282 B): `00`:59's four tasks in order, each with its stop rule, then "what makes a group not a group".
- **anchors-first** (`b_group.unratified.anchors-first.2026-09-06`, 9,852 B): start from what the anchors state in common — that is the basis or there is none — admit candidates one at a time against it, then flags, then the label; counter-examples woven into "what a basis is not".

Both share `b_group_response_schema.json` and `b_group_shaping_policy.json`. The bench dossier carries the proposed basis, each member's anchor/candidate status and retrieval channel, and each excerpt's owning member as evidence-item text — three things `grouping/p8_seam.py` does not yet send (G9) — and defines `allowed_vocabulary` as the shipped situation ids, which the live product leaves undefined (G4).

#### 4.2.1 The texts, traced by block

Shared blocks once; the deciding block per candidate. Item kinds `proposed_basis`, `member` (with anchor/candidate status and channel) and `excerpt` (with its owning member) are the bench's (G9).

| Block (both texts) | Sentences | Requirement |
|---|---|---|
| OUTPUT | one object | B-R13 |
| WHAT YOU ARE DOING | holds, members, contradictions, label; cite each | B-R1, B-R4 |
| | not building, retrieving, designing, naming folders; no file added; no path | B-R3, B-R5 |
| | nothing about the person | B-R13 |
| WHAT THE DOSSIER CONTAINS | key line | step 2 key check |
| | `allowed_vocabulary` is the category list | B-R11, G4 |
| | `proposed_basis`; `member` anchor vs candidate, channel named | B-R2, `00`:57-58, G9 |
| | `excerpt` owned by a member; `released_evidence` the only text | B-R4, G9 |
| | `conflicts`: institution, code, term, project, purpose; a flag is not a verdict | B-R6, B-R7 |
| THE SHAPE | two objects; per-member decisions with `evidence_refs`; `outliers` with kind; `merge_terms` | B-R1, B-R4, B-R6 |
| Rule 1 | `coherent` three values; `basis` three values; generic-similarity is not a group | B-R2, B-R8, B-R12 |
| Rule 2 | file ids copied; every listed member gets a decision | B-R3 |
| Rule 3 | label and category only when `yes`; category copied | B-R1, B-R11 |
| Rule 4 | more than one term means two groups | B-R6 |
| Rule 5 | no key for folder, path, hierarchy, inferred date, project, purpose | B-R5 |
| Rule 6 | citation shape; only `released_evidence`; `evidence_refs` among citations | B-R4 |
| Rule 7 | `why` never empty; a sentence doing the text's work makes the decision `uncertain` | B-R4 |
| Rules 8, 9 | `unknown` discipline; one malformed value | B-R13 |

| anchors-first | Requirement | four-questions | Requirement |
|---|---|---|---|
| Start from the anchors and nothing else; what they state in common is the basis; nothing in common is `no`; too little is `insufficient` | B-R2, B-R8 (anchor rule), B-R12 | Q1 coherence: `yes` when anchors state it, `no` on incompatibility or a shared word / session / resemblance, `insufficient` otherwise; not surfaced is correct | B-R1, B-R8, B-R12 |
| Admit candidates one at a time: states the basis → include; contradicts → exclude and outlier; compatible and channel-connected but silent → uncertain; a contradicting anchor is excluded too | B-R2, B-R4, B-R7 | Q2 membership per member with a sentence; anchor included unless it contradicts; candidate include / uncertain / exclude; uncertain is not a failure | B-R2, B-R4 |
| Read every flag against the text; outliers account for them | B-R7 | Q3 outliers with kind; read every flag first | B-R7, B-R6 |
| Only if the basis holds: a short label from what the anchors state, one category; a proposal the person confirms | B-R1, B-R11 | Q4 label and category only if `yes`; a proposal | B-R1, B-R11 |
| What a basis is not: a university's name (three relationships), an email domain, a name, a shared word; a download session; a suffix; a code across two terms; a purpose only when declared | B-R8, B-R9, B-R6, `00`:239 | WHAT MAKES A GROUP NOT A GROUP: the same six, plus "a basis nobody states" | B-R8, B-R9, B-R7, B-R6, `00`:239 |

B-R10 (a file may belong to more than one accepted group) has no sentence in either text. Each dossier reviews one group, so an exclusion here says nothing about another group; the v2 should say that in one sentence, because a model that reads "exclude" as "belongs elsewhere" will refuse the shared transcript of C05's kind at B too. B03's measured false abstention is the one place the trace is thin: "a contradicting candidate is an outlier of a coherent group" is implied by the shape (an outlier list beside `coherent: yes`) and stated by neither text.

### 4.3 Results (cloud, deepseek-chat, 15 cases × 2 candidates = 30 calls)

| arm | schema-valid | validator ok | grounding | abstain on should-abstain | correct on should-answer | correct **and** accepted | false abstain | accepted | median s | tokens (prompt / completion) |
|---|---|---|---|---|---|---|---|---|---|---|
| four-questions / cloud | 14 / 15 | 14 / 15 | 31 / 31 (1.0) | 4 / 5 | 8 / 10 | 8 / 10 | 1 / 10 | 9 / 15 | 3.7 | 82,649 / 7,346 |
| anchors-first / cloud | **15 / 15** | **15 / 15** | 32 / 32 (1.0) | **5 / 5** | 8 / 10 | 8 / 10 | 1 / 10 | 9 / 15 | 3.8 | 81,419 / 6,904 |

Both texts got the same eight groups right with the right members and outliers (the Duke problem set excluded from PHYS1401, the screenshot excluded from the photo event, the student's own problem set excluded from the TA's materials, the version family, the litigator's matter, the purpose-coherent packet with all five members included), and both refused the two-term course, the email-domain hub, the download session and the suffix-only "family".

They differ on three cases. **four-questions** formed the group `00`:63 names as the one not to form: B08, three files whose only common word is *Columbia* (an essay addressed to it, a syllabus taught at it, a résumé naming it as employer) came back `coherent: yes`, label *"Columbia University application materials"*. anchors-first answered *"the anchors only share the word Columbia, which is not a basis; they state different relationships"*. four-questions also lost B01 to broken JSON (G13's shape effect: `"merge_terms":["Spring 2026"]}]`). anchors-first marked the research abstract in the UChicago packet `uncertain` where the label said `include` (B07) — defensible, since the abstract's own text does not name UChicago and the checklist does.

Both false-abstained on B03, the Duke essay inside the Columbia packet: each excluded the Duke essay and named it an outlier (4 of 4 member decisions right) and then answered `coherent: no` *because* a member conflicted. The intended reading — a contradicting candidate is an outlier of a coherent group, not a coherence failure — is stated by neither text plainly enough, and is the one v2 sentence for B.

**Ahead on this run: anchors-first** — every abstention including the `00`:63 case, no schema failure, equal placement. B08 and B01 are one case each on one cloud run; the same caveat as D applies.

### 4.4 Stress cases

Rendered by `python3 -m tools.promptbench tables --site B_group --out tools/promptbench/out/B_group`; v2, v3 and whatever of the local arm has been recorded included.

| case | persona | traces | expectation | anchors-first / cloud | anchors-first / local | anchors-first-v2 / cloud | anchors-first-v3 / cloud | four-questions / cloud |
|---|---|---|---|---|---|---|---|---|
| B01 — a course group with a direct syllabus anchor and a sparse homework candidate | Priya | 00:57, 00:60 | answer: `{"coherent":"yes","members":{"f-syl":"include","f-lec":"include","f-hw3":"uncertain|inc...` | correct / acc_direct | correct / reject INVENTED_MEMBERSHIP | correct / acc_direct | correct / acc_direct | WRONG / reject SCHEMA_INVALID |
| B02 — one course code, two terms | Priya | 00:63, 00:62 | abstain: `{"coherent_in":["no","insufficient"]}` | abstained / abstain | ANSWERED / reject UNCITED_CLAIM | abstained / abstain | abstained / abstain | abstained / abstain |
| B03 — a Duke essay inside a Columbia packet | multi-life | 00:58, 00:59, 00:62 | answer: `{"coherent":"yes","members":{"f-essay-col":"include","f-checklist":"include","f-transcr...` | false abstain / abstain | — | WRONG / reject SCHEMA_INVALID | false abstain / abstain | false abstain / abstain |
| B04 — files bridged only by a university email domain | multi-life | 00:63, 00:57 | abstain: `{"coherent_in":["no","insufficient"]}` | abstained / abstain | — | abstained / abstain | abstained / abstain | abstained / abstain |
| B05 — a purpose-coherent application submission packet | multi-life | 00:45, 00:61 | answer: `{"coherent":"yes","members":{"f-portal":"include","f-checklist":"include","f-transcript...` | correct / acc_direct | — | WRONG / reject SCHEMA_INVALID | correct / acc_direct | correct / acc_direct |
| B06 — a tight download session with no purpose evidence | Tom | 00:61, 00:45 | abstain: `{"coherent_in":["no","insufficient"]}` | abstained / abstain | — | abstained / abstain | abstained / abstain | abstained / abstain |
| B07 — a research abstract that also supports an application | multi-life | 00:63, 00:48 | answer: `{"coherent":"yes","members":{"f-checklist":"include","f-portal":"include","f-abstract":...` | WRONG / acc_direct | — | WRONG / acc_direct | WRONG / acc_direct | correct / acc_direct |
| B08 — a university name that is a target, a provider and an employer | multi-life | 00:63 | abstain: `{"coherent_in":["no","insufficient"]}` | abstained / abstain | — | abstained / abstain | abstained / abstain | ANSWERED / acc_direct |
| B09 — a coherent course group that needs a label | Priya | 00:59 | answer: `{"coherent":"yes","members":{"f-syl":"include","f-lec":"include","f-mid":"include"},"la...` | correct / acc_direct | — | correct / acc_direct | correct / acc_direct | correct / acc_direct |
| B10 — a conflicting course code among the candidates | Priya | 00:59, 00:62 | answer: `{"coherent":"yes","members":{"f-syl":"include","f-lec":"include","f-ps2801":"exclude"},...` | correct / acc_direct | — | WRONG / reject SCHEMA_INVALID | correct / acc_direct | correct / acc_direct |
| B11 — a photo event with a screenshot in the same hour | multi-life | 00:56, 00:32 | answer: `{"coherent":"yes","members":{"f-p1":"include","f-p2":"include","f-p3":"include","f-shot...` | correct / acc_direct | — | correct / acc_direct | correct / acc_direct | correct / acc_direct |
| B12 — a TA's solution set with the student's own problem set as a candidate | Priya | 68:F6, 00:59 | answer: `{"coherent":"yes","members":{"f-sol":"include","f-rubric":"include","f-ps1401":"exclude...` | correct / acc_direct | — | WRONG / reject SCHEMA_INVALID | correct / acc_direct | correct / acc_direct |
| B13 — versions of one essay | multi-life | 00:239, 00:56 | answer: `{"coherent":"yes","members":{"f-v1":"include","f-v2":"include","f-docx":"include"},"lab...` | correct / acc_direct | — | WRONG / reject SCHEMA_INVALID | correct / acc_direct | correct / acc_direct |
| B14 — a litigator's matter with an e-filing receipt | Mara | 68:2, 00:59 | answer: `{"coherent":"yes","members":{"f-motion":"include","f-depo":"include","f-log":"include",...` | correct / acc_direct | — | WRONG / reject SCHEMA_INVALID | correct / acc_direct | correct / acc_direct |
| B15 — duplicate suffixes on unrelated files | Tom | 00:239, 00:172 | abstain: `{"coherent_in":["no","insufficient"]}` | abstained / abstain | — | abstained / abstain | abstained / abstain | abstained / abstain |

### 4.5 Contract gaps found at B

G4 (no authorities constructed; `allowed_vocabulary` undefined), G9 (the seam carries no basis, no excerpt-to-member mapping, no retrieval channel), G11 (`apply_p8_verdict` drops label, category and per-member decisions — `104` R-16), G13 (broken JSON when the payload ends on a populated array — B01), in §7.

### 4.6 The ratification question

Ratify **anchors-first** (`b_group.unratified.anchors-first.2026-09-06`), its response schema and shaping policy, conditional on the seam change G9 that the text describes and on `allowed_vocabulary` being defined as the situation ids (G4); wire it observe-only until P9 reads the label, the category and the per-member decisions (G11). Authorise a v2 measurement carrying the B03 sentence and a payload whose last key is a scalar (G13).


**The two known limits.** S1, what the text cannot catch: a coherent-looking group whose anchors do state one thing in common that is nonetheless not how the person thinks of the files (a purpose-coherent packet the person keeps by course, or the reverse); the label is a proposal for exactly that reason, `00`:64. S2, what the validator catches: a file id not in the dossier, a label without coherence, a merged term, a folder or hierarchy key, an uncited member decision, a malformed object; and not the category (G4) or the per-member decisions once P9 drops them (G11).

### 4.7 anchors-first-v2 and v3, measured (cloud, 15 calls each)

v2's stated delta: a contradicting member is an outlier of a coherent group and does not make it incoherent; excluding a file here says nothing about other groups (B-R10). v3 is v2 with the payload reordered so `basis`, a word, is its last key.

| arm | schema-valid | validator ok | grounding | abstain on should-abstain | correct on should-answer | correct **and** accepted | false abstain | accepted | median s | tokens |
|---|---|---|---|---|---|---|---|---|---|---|
| anchors-first / cloud | 15 / 15 | 15 / 15 | 32 / 32 | 5 / 5 | 8 / 10 | 8 / 10 | 1 / 10 | 9 / 15 | 3.8 | 81,419 / 6,904 |
| anchors-first-v2 / cloud | **9 / 15** | 9 / 15 | 14 / 14 | 5 / 5 | 3 / 10 | 3 / 10 | 0 / 10 | 4 / 15 | 3.0 | 82,694 / 6,987 |
| anchors-first-v3 / cloud | 15 / 15 | 15 / 15 | 32 / 32 | 5 / 5 | 8 / 10 | 8 / 10 | 1 / 10 | 9 / 15 | 3.5 | 83,069 / 6,793 |

**v2 measured the shape defect, not the sentence.** Six of its fifteen responses were unusable: five closed the payload on `merge_terms` one bracket short (`"merge_terms":[]}],"citations"` — G13, and on an *empty* array, which corrects §5.3's note that an empty last array was safe), and one (B03) came wrapped in a code fence. The wording change did not cause the defect; at temperature 0 any change to the text reshuffles which responses hit it, and v1 hit it once (B01). v3 moved `basis` to the end and the defect vanished: 15 of 15 valid, the same eight groups right, the same five refusals including the `00`:63 Columbia group.

**The B03 sentence had no effect.** Under v3 the model included the Columbia essay and the checklist, excluded the Duke essay as an outlier — and answered `coherent: no` with the statement that the Duke essay "states a different target institution, so the group's basis is not coherent", the same reading as v1. Behind v2's fence, the same. Two wordings and three runs have now produced this reading; it is not a sentence the model missed but a judgement it makes, and the honest options are to accept it (a packet with a contradicting member is sent to the person as `no` with the outlier named, which loses nothing the person cannot recover) or to change the shape so that an outlier list beside `coherent: yes` is the only place a contradiction can go. B07's `uncertain` abstract is unchanged under all three.

**anchors-first-v3 is the B text put forward**, in place of anchors-first: identical numbers, with the bracket defect removed from the shape.

## 5. E_template

### 5.1 Requirements, traced

| # | Requirement | `00` line / ruling | Validator |
|---|---|---|---|
| E-R1 | Input: the group dossier, representative files, validated facts, the approved label, the existing destination vocabulary and the structural constraints. | `00`:97 | — (G10: no channel for the constraints) |
| E-R2 | Output: a strict-JSON schema with a domain name, allowed fields, recommended dimensions, field order, optional versus required levels, metadata-only fields, a sensitivity policy and example paths. | `00`:97 | P10 `template_schema_validator` (all `TEMPLATE_PAYLOAD_KEYS`) |
| E-R3 | Use existing field types wherever possible; a name outside the closure is a template-local label, never another schema's field key relabelled. | `00`:97; `43` §9 | closure check; W3 (`_LIVE_P6_FIELD_KEYS`) |
| E-R4 | Cite the file facts that justify each dimension and explain why each level improves retrieval. | `00`:97 | dimension `evidence_ref` ∈ citations; empty `retrieval_justification` → `WEAK` |
| E-R5 | Do not repeat a parent dimension, create one-child levels, exceed practical depth, use an author or organization as a collector, expose protected information, or produce empty branches. | `00`:97, 99, 44 | — (semantic; the person's canvas) |
| E-R6 | Document domains put subject/project/function before time; captures put time first. | `00`:95, 70 | — |
| E-R7 | May reference a published fragment by exact id and version; may not publish one. | `template_schema.py` (fragment boundary) | `FRAGMENT_NOT_PUBLISHED`, `FRAGMENT_PUBLICATION_ATTEMPTED` |
| E-R8 | Valid shape is not activation: the person reviews, edits and accepts or discards. | `00`:97 | — |
| E-R9 | Abstain when the evidence draws no distinction that passes the tests. | `00`:97 ("cannot invent unsupported facts") | `ABSTAIN` |
| E-R10 | One JSON object, one claim, the recorded shape; nothing about the person. | inherited | `SCHEMA_INVALID` |

### 5.2 The two candidates

- **from-facts** (`e_template.unratified.from-facts.2026-09-06`, 9,478 B): bottom-up — list the distinctions the text actually draws, pass each through the five tests, name, order, cap.
- **what-a-person-opens** (`e_template.unratified.what-a-person-opens.2026-09-06`, 9,504 B): top-down — what a person opens first a year from now, each imagined level put to the same five tests as questions with their failure named.

Both share `e_template_response_schema.json` and `e_template_shaping_policy.json`. `allowed_vocabulary` is P10's `allowed_vocabulary_for(catalogue, uses_schema)` and `field_glossary` explains it; the branch constraints travel as `branch_context` items (G10).

#### 5.2.1 The texts, traced by block

The `branch_context` item kind is the bench's (G10).

| Block (both texts) | Sentences | Requirement |
|---|---|---|
| OUTPUT | one object | E-R10 |
| WHAT YOU ARE DOING | levels, order, why each helps; cite | E-R1, E-R4 |
| | not creating folders or choosing a domain; canvas review; valid shape is not a good design | E-R8 |
| | nothing about the person | E-R10 |
| WHAT THE DOSSIER CONTAINS | key line | step 2 key check |
| | `allowed_vocabulary` as established field names; may be empty | E-R3 |
| | `field_glossary` is a definition, not evidence | E-R4 |
| | `branch_context`: kind, label, parent and what it expresses, sensitivity policy ref, depth limit | E-R1, E-R5 (parent, depth), G10 |
| | `excerpt` owned by a member; `released_evidence` the only text | E-R4 |
| HOW TO DESIGN (shared tail) | name with `schema-field` or a plain `template-local` word, never a borrowed key | E-R3 |
| | stop before the depth limit; fewer levels; `metadata_only` for a field worth search but not a folder | E-R5 (depth), E-R2 (metadata-only fields) |
| | nothing to open / no distinction passes → propose nothing | E-R9 |
| THE SHAPE | every `TEMPLATE_PAYLOAD_KEYS` member: domain, allowed_fields, fragment_refs, dimensions, levels, sensitivity_policy_ref, example_label_chains | E-R2 |
| Rule 1 | names copied or template-local; a borrowed key is refused | E-R3 |
| Rule 2 | `allowed_fields` once each | E-R2 |
| Rule 3 | every dimension cites; `order_index` unique from zero | E-R4, E-R2 (field order) |
| Rule 4 | levels name dimensions with a justification; metadata-only has no level | E-R4, E-R2 |
| Rule 5 | fragments referenced by id and version, never published | E-R7 |
| Rule 6 | sensitivity policy ref copied; label chains without slashes | E-R2 |
| Rules 7, 8 | citation shape; `why_it_supports` never empty | E-R4 |
| Rules 9, 10 | `unknown` discipline; one malformed value | E-R10 |
| closing | rules check anchoring, not design; the person judges | E-R8 |

| what-a-person-opens | Requirement | from-facts | Requirement |
|---|---|---|---|
| What a person opens first a year from now, then inside that; parent gives context; subject before time for documents; time first for captures | E-R6, E-R4 | List every distinction the text actually draws; a value in one file or the same in all is no distinction | E-R4, E-R5 (one child), E-R9 |
| Five questions per imagined level: splits what the parent has not; more than one child; not a person or organization; no name / id / account / diagnosis on a folder; every child has a file | E-R5 | Five tests: not the parent; splits the files; not an author or organization as collector; no protected information; a value for every child | E-R5 |
| | | Order survivors: parent gives context; subject / project / function before time; captures time first | E-R6 |

Both texts carry every E requirement; the difference is direction (top-down questions against bottom-up filtering), which is what the bakeoff measured. The measured failure (§5.3) is in neither text's design block: it is the shape's last key.

### 5.3 Results (cloud, deepseek-chat, 12 cases × 2 candidates = 24 calls)

| arm | JSON parses | schema-valid | validator ok | grounding | abstain on should-abstain | correct on should-answer | correct **and** accepted | accepted | median s | tokens (prompt / completion) |
|---|---|---|---|---|---|---|---|---|---|---|
| from-facts / cloud | 3 / 12 | 3 / 12 | 3 / 12 | 9 / 9 (1.0) | 1 / 1 | 2 / 11 | 2 / 11 | 2 / 12 | 4.4 | 67,281 / 5,997 |
| what-a-person-opens / cloud | 6 / 12 | 5 / 12 | 6 / 12 | 18 / 18 (1.0) | 1 / 1 | 3 / 11 | 3 / 11 | 5 / 12 | 4.2 | 67,353 / 6,690 |

**Neither is ratifiable, and the reason is the shape, not the design.** Fifteen of the 24 responses are not valid JSON: deepseek-chat closes the payload as `...]]}],"citations":[` — one bracket too many — every time the payload's last key is a populated array (`example_label_chains`, an array of arrays). The same defect took B01 (`"merge_terms":["Spring 2026"]}]`); C and D, whose payloads end on a scalar or an empty array, never produced it in 62 calls. Read as designs, the parsed answers are the right ones: the photo template time-first (`capture_year`, `location`, `event`), the research group without its parent's `project`, the consulting engagement by document kind and not by author, the household statements by institution and record type with no account holder, the D&D campaign by template-local `campaign` and `session`. Two of what-a-person-opens' accepted answers were wrong by `00`:97's one-child rule (a `project` level over one project, E06 and E12 — labels corrected after the run for the same rule, §5.4), and one parsed abstention at E10 carried an empty `dimensions` list instead of `domain: "none"`, valid to the validator and not to the draft's schema.

**Winner: what-a-person-opens**, on 3 of 11 against 2 of 11 and twice the schema-valid rate — and it is not put forward for ratification. The v2 is mechanical and measurable: move `example_label_chains` up and end the payload on `sensitivity_policy_ref` (a scalar), and, product-side, request `response_format: json_object` at the transport (G13), which DeepSeek documents for exactly this.

### 5.4 Stress cases

Rendered by `python3 -m tools.promptbench tables --site E_template --out tools/promptbench/out/E_template`. Three labels were corrected after the first run, by `00`:97's own rule that a level with one child is no level: E04, E06 and E12; the suite records the correction beside each case.

| case | persona | traces | expectation | from-facts / cloud | what-a-person-opens / cloud | what-a-person-opens-v2 / cloud |
|---|---|---|---|---|---|---|
| E01 — a trip's photos: time first, then the occasion | multi-life | 00:95, 00:70 | answer: `{"must_include":["capture_year","event"],"first":"capture_year","must_exclude":["people...` | WRONG / reject SCHEMA_INVALID | WRONG / reject SCHEMA_INVALID | correct / acc_direct |
| E02 — a research group whose parent already is the project | multi-life | 00:97, 00:99 | answer: `{"must_include":["artifact_type"],"must_exclude":["project","authored_by","lab"]}` | WRONG / reject SCHEMA_INVALID | correct / acc_direct | correct / acc_direct |
| E03 — consulting deliverables all prepared by the same person | Mara | 00:44, 00:97 | answer: `{"must_exclude":["authored_by","our_firm","subject_of_record"],"template_local_ok":true}` | WRONG / reject SCHEMA_INVALID | correct / acc_direct | correct / acc_direct |
| E04 — a course where every file shares one term | Priya | 00:97, 00:99 | answer: `{"must_include":["work_type"],"must_exclude":["term","instructor","subject"]}` | correct / acc_direct | WRONG / reject SCHEMA_INVALID | correct / acc_direct |
| E05 — a domain the library has no schema for | Tom | 00:97, 43:9 | answer: `{"min_template_local":1,"must_exclude":["project","event","subject"],"template_local_ok...` | WRONG / reject SCHEMA_INVALID | WRONG / reject SCHEMA_INVALID | correct / acc_direct |
| E06 — a recurring pattern that tempts publication | multi-life | 00:97, 43:9 | answer: `{"must_include":["artifact_type"],"must_exclude":["programming_language","authored_by",...` | WRONG / reject SCHEMA_INVALID | WRONG / acc_direct | WRONG / acc_direct |
| E07 — financial records where a person would be the collector | Tom | 00:97, 00:185 | answer: `{"must_include":["institution"],"must_exclude":["account_holder","subject_of_record","p...` | WRONG / reject SCHEMA_INVALID | WRONG / reject SCHEMA_INVALID | correct / acc_direct |
| E08 — evidence that supports more levels than a tree should have | multi-life | 00:97, 00:99 | answer: `{"must_include":["artifact_type"],"max_dimensions":4,"must_exclude":["authored_by"]}` | correct / acc_direct | WRONG / reject SCHEMA_INVALID | correct / acc_direct |
| E09 — a dimension no file has a value for | multi-life | 00:97 | answer: `{"must_include":["artifact_type"],"must_exclude":["venue","lab","authored_by"]}` | WRONG / reject SCHEMA_INVALID | correct / acc_direct | WRONG / reject SCHEMA_INVALID |
| E10 — a group with no recoverable facts | Tom | 00:97, 00:63 | abstain: `{"abstain":true}` | abstained / abstain | abstained / abstain | abstained / abstain |
| E11 — recruiting documents: the employer before the cycle | multi-life | 00:95, 00:70 | answer: `{"must_include":["target_employer"],"first":"target_employer","must_exclude":["authored...` | WRONG / reject SCHEMA_INVALID | WRONG / reject SCHEMA_INVALID | correct / acc_direct |
| E12 — a code project: repository, not language | multi-life | 00:30, 00:97 | answer: `{"must_include":["artifact_type"],"must_exclude":["programming_language","authored_by",...` | WRONG / reject SCHEMA_INVALID | WRONG / acc_direct | WRONG / acc_direct |

### 5.5 Contract gaps found at E

G10 (no channel for the schema id, the parent's expressed value, the sensitivity policy reference or the depth limit), G12 (no live caller: `routing.py`'s C3 refusal never becomes a request), G13 (broken JSON when the payload ends on a populated array — 15 of 24 here), in §7.

### 5.6 The ratification question

Not yet. Authorise a v2 of **what-a-person-opens** with the payload reordered to end on a scalar, measured on the same 12 cases, and decide G13 at the transport; E has no live caller (G12), so nothing is lost by the wait.


**The two known limits.** S1, what the text cannot catch: a design that passes the five tests and is still not how the person would look for a file; `00`:97 makes the canvas the judge and the text says so. S2, what the validator catches: a borrowed field key, a dimension without a citation, a level without a justification, a published fragment, a missing payload key, a malformed object; and not the one-child rule, the parent repetition or an author used as a collector, which are semantic (E-R5) and reach the person's canvas unflagged.

### 5.7 what-a-person-opens-v2, measured (cloud, 12 calls)

The stated delta: the payload ends on `sensitivity_policy_ref`, a string, instead of `example_label_chains`, a list of lists.

| arm | JSON parses | schema-valid | validator ok | grounding | abstain on should-abstain | correct on should-answer | correct **and** accepted | accepted | median s | tokens |
|---|---|---|---|---|---|---|---|---|---|---|
| what-a-person-opens / cloud | 6 / 12 | 5 / 12 | 6 / 12 | 18 / 18 | 1 / 1 | 3 / 11 | 3 / 11 | 5 / 12 | 4.2 | 67,353 / 6,690 |
| what-a-person-opens-v2 / cloud | **10 / 12** | 10 / 12 | 11 / 12 | 36 / 36 | 1 / 1 | **8 / 11** | 8 / 11 | 10 / 12 | 4.0 | 67,605 / 6,574 |

The shape was the reason: with the last key a string, the bracket defect went from 6 of 12 to 1 of 12 (E09, a differently malformed close), and the design comparison is now on eleven cases instead of five. Eight of the eleven are the labelled design: the photos time-first (`capture_year`, `location`, `event`, no people), the research group without its parent's `project`, the consulting engagement by document kind and not by author, the course by `work_type` alone, the campaign by two template-local words, the household statements by `institution` and `record_type` with no account holder, the recruiting documents employer-first, the workflow group under its four-level cap. The three misses are one defect: **the one-child rule** (`00`:97) — E06 proposed `project` and `repository` levels over one project and one repository, E12 a `repository` level over one repository; the text's second question ("would this level have more than one child?") is asked and not answered from the evidence. That is the E v3 to write: the one-child test stated as a count the model must make from `values` ("a dimension whose `values` list has one entry is not a level"), and the only E change worth a run.

**what-a-person-opens-v2 is the E text put forward** for ratification, conditional on the one-child sentence being measured first; E has no live caller (G12) so nothing waits on it.

## 6. Research applied across the five sites, with citations

What the literature and the two vendors' documentation say, and the one decision in these drafts that each finding governs. Each row is cited; a finding that governed nothing is not listed.

| # | Finding | Source | Where it lands in the drafts |
|---|---|---|---|
| R1 | **Format restriction degrades reasoning.** Grammar-constrained decoding and strict JSON output measurably lower task accuracy relative to free-form answers, and naive constrained decoding distorts the distribution toward "syntactically valid but semantically degraded" output. | Tam et al., *Let Me Speak Freely?* (arXiv 2408.02442); *The Structured Output Benchmark* (arXiv 2604.25359); JSONSchemaBench (arXiv 2501.10868) | Every draft keeps the ratified A_fact opening, "Think for as long as you need to before you answer", separating reasoning from the one object sent; the local transport's `format: json` is a product setting the bench keeps and reports as such, so the local schema-valid rates below are partly the grammar's, not the text's. The cloud arm sets no `response_format` (parity with `readers/model_deepseek.py`), so its schema-valid rate is the text's alone. |
| R2 | **Abstention is unsolved and reasoning models are worse at it.** Across 20 frontier models on 20 datasets, abstention on unanswerable, underspecified and false-premise questions does not improve with scale, and recent reasoning models abstain less. | AbstentionBench (arXiv 2506.09038, NeurIPS 2025); *Know Your Limits* survey (TACL, arXiv 2407.18418) | Abstention is a first-class, fully specified answer at every site (`"none"`, the three no-target D actions, `coherent: no/insufficient`, `domain: "none"`), each with its own shape shown, its cost stated ("costs nothing and is not counted against you") and its trigger conditions enumerated rather than left to judgment. The bench measures it directly (`abstain_rate_on_should_abstain`). Consistent with `104` R-18, both arms run non-reasoning configurations (deepseek-chat; qwen3 with thinking off). |
| R3 | **Option order and option-id tokens bias selection**, by 13% to 75% on multiple-choice benchmarks; the bias is strongest when the two best options sit first and last. | Zheng et al., *LLMs Are Not Robust Multiple Choice Selectors* (arXiv 2309.03882); Pezeshkpour & Hruschka (NAACL Findings 2024, arXiv 2308.11483) | Candidates, areas and members are never lettered or numbered; the text says "the order of the items carries no meaning"; and the bench shuffles the offered ids by a keyed hash per case so no arm can score by position (`suite_c._shuffled`, `suite_d._shuffled`). The live retrieval order is the engine's ranking (`00`:110); the shaping policies say so and say it is not an instruction. |
| R4 | **Relevant material in the middle of a long context is used worst**; the start and the end are used best. | Liu et al., *Lost in the Middle* (TACL 2024, arXiv 2307.03172) | Templates are one page, the dossier follows last, and the shaping policies order evidence "most placed first". The C/D/B dossiers measured 1.7 to 2.4 KB; the drafts are 9.5 to 11.2 KB. Nothing decisive sits mid-context. |
| R5 | **Quote first, then answer.** Extracting word-for-word quotes before concluding grounds long-document answers and reduces hallucination. | Anthropic, *Prompting best practices / long-context tips*; *Reduce hallucinations* (docs.anthropic.com, platform.claude.com) | The citation contract is the ratified A_fact one: every asserted value cites an `observation_key` and a `cited_span` copied exactly from the released value, and the validator span-matches it (`00`:42, 62, 114, 126). The drafts add the per-site version: "cite only keys that appear in released_evidence: a candidate, a group or a conflict is not evidence". |
| R6 | **Contrastive examples beat positive examples alone**: a negative example with the reason it fails improves instruction following and detection of the bad case. | Gao et al., *Contrastive In-Context Learning* (arXiv 2401.17390); *Failures Are the Stepping Stones* (arXiv 2507.23211) | Each draft carries a block of counter-examples in place of worked positives (`00`:239's list rendered as "some things look like support and are not": MIT inside submit, a gate number is not a trip, a university name is three relationships, a session proves nothing, a suffix is not a family). No worked example names a real field key or corpus value (`76` R18; `tests/llm_harness/test_d2_draft_templates.py`). |
| R7 | **DeepSeek: default temperature 1.0; 0.0 recommended for deterministic tasks; JSON mode wants the word "json" and an example in the prompt and a `max_tokens` high enough not to truncate; the API "may occasionally return empty content".** | api-docs.deepseek.com, *The Temperature Parameter*; *JSON Output* | The bench pins `temperature=0` for reproducibility and records it; `readers/model_deepseek.py` sets none, which is a recommendation in §7, not a change. Every draft says "JSON" and shows two shapes. `max_tokens` stays the product's 8,192. An empty answer is what the transport already refuses by name. |
| R8 | **Qwen3: thinking is disabled with `enable_thinking=False` (Ollama: `think: false`); greedy decoding is warned against in thinking mode; non-thinking sampling defaults are temperature 0.7, top-p 0.8; 32K native context.** Ollama silently truncates a prompt to the model's default context unless `num_ctx` is set. | huggingface.co/Qwen/Qwen3-8B model card; Ollama API reference (`think`, `num_ctx`, `prompt_eval_count`); the local-model agent's finding of 2026-09-06 | Local arm: `think: false`, `num_ctx` set per call from the measured prompt bytes (8,192 minimum, 32,768 maximum) and recorded with `prompt_eval_count`; temperature 0 and seed 1 kept from `readers/model_ollama.py` because `00`:203's replay needs determinism, with the model card's caveat noted. `num_predict` is bounded at 4,096 so a repetition loop ends. |
| R9 | **Hierarchical classification with an explicit "none of the above".** Benchmarks of uncertainty-aware classification treat "should abstain" as its own class and calibrate on should-refuse controls. | UA-Bench (arXiv 2604.17293); AbstentionBench as above | C is written as a walk down a chain of levels with a stop rule per level (`00`:111), and every should-abstain case in the suites is a positive control the bench scores separately from the should-answer cases. |

What was not adopted, and why: few-shot worked examples (R6 argues for contrastive ones, but a shared template cannot carry a domain's example without teaching the model that domain's spelling, `76` R18); asking for a confidence score (the ratified A_fact text forbids a third move, and `104` §13.5 makes numeric gating a rule's job, not the model's); letter-labelled options (R3).

## 7. Contract gaps register

Each row is something the site's contract cannot express or does wrongly, found while tracing the requirements or building the bench. None is worked around in a prompt. "Pinned by" names the test in `tests/llm_harness/test_d2_contract_gaps.py`; a strict xfail asserts the correct behaviour and turns green the day the fix lands.

| # | Site | What the contract cannot express or does wrongly | Where | Pinned by | Consequence for ratification |
|---|---|---|---|---|---|
| G1 | C, D | `dossier._body` keys every `conflict_id` with `wire_handle` before the model sees it, but `_placement_site` and `_residual_site` compare `conflicts_considered` / `relationships_considered` against the RAW ids. A model that echoes every flag it was shown is rejected `CONFLICT_IGNORED` / `STRONGER_RELATIONSHIP_OVERLOOKED`; the raw id, which passes, never reaches the model. Any C or D dossier that carries a conflict is unanswerable. | `llm_harness/dossier.py:245`, `placement_validation.py:229-236, 330-338` | `test_g1_*` (xfail ×2, control ×1) | The drafts instruct echoing the shown ids (the only honest instruction). Until the validator translates handles the way `validation._validate_claim` does for citations, C and D must be wired with `conflicts=()` or observe-only. Bench cases C06 and D08 measure the cost. |
| G2 | C | `_invented_dimension` checks per-level VALUES for `date`, `institution` and `project` against `allowed_vocabulary`, which at C is the node-id list, so any real project value is `INVENTED_PROJECT` (`104` R-15). | `placement_validation.py:185-197` | `test_g2_*` (xfail + control) | Research and code branches cannot report a `project` level until fixed; coursework and application branches are unaffected. |
| G3 | C, D | The live dossier carries `allowed_vocabulary = legal node ids` (minted, opaque) and nothing about them: no label chain, no expected values, no known document types, no "this is the file's own folder". `field_glossary` maps a node id to nothing and `Dossier` has no profile field. `00`:105-106 and 110 require each candidate's node profile. | `placement/pipeline.py:1345`, `Dossier` | `test_g3_*` (fact) | The bench carries each candidate as an evidence item of kind `candidate` (`residual_area` / `branch` at D) whose `location` is the label chain plus expected values, which is what the drafts describe. **Ratifying C or D ratifies that builder change**; without it the model chooses among identifiers it cannot read. |
| G4 | B | No module under `src/` constructs `P8Authorities`, so B's `allowed_vocabulary`, gate, client and dependencies are undefined in the live product (`104` R-04). | `grouping/pipeline.py:651` | `test_g4_*` (fact) | The bench defines `allowed_vocabulary` as the shipped situation ids (the category the label is filed under). The composition root must define it before B is wired; `INVENTED_DATE/PROJECT/PURPOSE` keys are avoided entirely by the draft's schema. |
| G5 | D | `_same_file_evidence` looks a citation up by raw key; the model cites the keyed handle; the lookup misses and the check passes everything (fail-open). | `placement_validation.py:283-299` | `test_g5_*` (xfail + control) | The D builder convention (cited items' `location` = subject ref) is honoured by the bench so the check would hold once translation lands; today it holds nothing. |
| G6 | C | The validator demands numeric `support` and `next_support` from the MODEL and applies `cli.SUPPORT_POLICY` (0.5 threshold, 0.2 margin on a 1.0 scale) to them; absent, the answer is `weak`. `104` §13.5 makes scores rank and shortlist, not veto. | `placement_validation.py:241-254` | `test_g6_*` (facts ×2) | The drafts define both as whole-number counts of citing items (destination vs strongest alternative) so a tie is the model's own "not decided" and no fabricated float gates a decision. **Ratification question**: keep the keys with that meaning, or remove the two-condition rule from the model path and let P11's deterministic scores fill them. |
| G7 | D | `choose_approved_broad_parent_branch` and `choose_approved_residual_destination` validate identically and both become `RESIDUAL_DESTINATION`; only the injected `residual_action_of` reads which was chosen. | `placement_validation.py:351-371` | `test_g7_*` (fact) | The draft's `action` key is what `residual_action_of` must read; the packet asks the owner to confirm the eight actions are read from the response payload, not the verdict. |
| G8 | D | A return's `target` is validated with `node_exists` and `approved_target_ids` like a destination, so a group id is `DESTINATION_NOT_IN_FROZEN_TREE`; the only target that validates is the branch node built from the group (`00`:107). | `placement_validation.py:318-325` | `test_g8_*` (fact) | The drafts say a return's target is that branch. The builder must offer such branches as items and include them in `approved_target_ids`. |
| G9 | B | `p8_seam` sends members as `(file_id, document_type, basis)` and excerpts as `(observation_key, zone)`: nothing links an excerpt to its member, nothing carries the proposed basis or the retrieval channel (`00`:57-58 require all three). | `grouping/p8_seam.py:123-156` | (bench construction; see suite_b) | The bench carries them in item `location` text. **Ratifying B ratifies that seam change.** |
| G10 | E | No channel for the branch constraints `00`:97 names: the schema id, the parent's expressed value, the sensitivity policy reference the payload must carry, the depth limit. | `tree_design/template_schema.py:299` | (bench construction; see suite_e) | The bench carries them as `branch_context` items. Same consequence as G9. |
| G11 | B | `apply_p8_verdict` writes no `display_label`, `group_category` or `coherence_verdict`, and collapses per-member include/exclude/uncertain to blanket memberships (`104` R-16). | `grouping/p8_seam.py:294-431` | `104` R-16 | The model's four answers are validated and then three of them are dropped. B must be observe-only until P9 reads them. |
| G12 | E | No live caller: `routing.py`'s C3 refusal never becomes an E request (`103` §28 table). | `tree_design/routing.py` | `103` §28 | E can be ratified and stay inert; the bakeoff is the only exercise it gets. |
| G13 | all | `readers/model_deepseek.py` sets no temperature and no `response_format`; the provider default is 1.0. The bench measured at temperature 0 and reports the setting per call. | `readers/model_deepseek.py:153-160` | (bench setting, recorded) | Recommendation, not a change: the composition root should pin temperature 0 for extraction sites, as `readers/model_ollama.py` already does, or the numbers here will not reproduce in the product. |
| G14 | local | Ollama truncates to the model's default context silently; `readers/model_ollama.py` sets no `num_ctx`. | `readers/model_ollama.py:79-80` | (coordinator finding; bench `num_ctx_for`) | Every bench call set `num_ctx` (16,384 for all 72 cases) and recorded `prompt_eval_count`. The product's local transport needs the same before any local site is wired. |
| G17 | D | `SENSITIVITY_RESTRICTION_IGNORED` (D-R8) rests on a `sensitivity_policy` dependency that nothing supplies: the product's composition passes `None` with the rest of the absent model path, and the bench stubs it to true. A protected record filed into an approved area is accepted (D13 under both texts on the local arm). | `placement_validation.py:328`, `cli.py:4126`, `tools/promptbench/judge.py:90` | (measured; no xfail yet) | The validator cannot stand behind D-R8 until a policy is composed; until then D's protected cases are caught by the text or by nobody, and the packet reports D13 as S1 with no S2. |
| G18 | all | `dossier._body` serialises through `canonical_json`, so keys are sorted and the file's own keys (`conflicts`, `eligibility_reason`, `evidence_items`) precede the situation frame's (`field_glossary`, `folder_levels`, and a `readings` key would follow `policy_version`). The prefix a provider can cache stops at `call_site`. Measured in §1.8: 41% of the prompt cached in the product's order, 90% with the frame serialised first, on the same bytes. | `llm_harness/dossier.py:239` (`canonical_json`), `records.assemble` | `tests/tools/test_promptbench_readings.py` (the two layouts pinned) | **Closing**: `104` R-58 on the schema agent's branch (bdb2105) emits `_BODY_ORDER`, frame then file, and refuses any other key set; its measurement is 48.3% → 88.9%–93.0% shared bytes (the floor when two files' open field sets differ). `readings` must be added to `_FRAME_KEYS` in the same change as the template line, or every A_fact call refuses at the seam. |
| G19 | A | `recognition.rules._schema` flattens a schema's `needs_llm` rows into `deferred_readings` and drops the `row` key, so the situation's readings cannot be selected; the schema's readings (69 for `academic`, 14,491 characters) are 3.6× the dossier ceiling and cannot be sent. | `recognition/rules.py:101-121` | (schema agent's measurement, 2026-09-06) | The key sends the situation's rows only (11 readings, 2,015 characters); `row` must survive `rules.py` first. |

## 8. Cloud calls used and tokens spent

From `tools/promptbench/out/cloud_ledger.json`, the one ledger spent before each socket opened:

| | calls | prompt tokens | completion tokens |
|---|---|---|---|
| cloud, deepseek-chat, temperature 0, no `response_format` | **237 of 400** | 1,220,736 | 75,716 |

Per site: A 42 (28 first wave, 14 the third subject wording), C 48 (32, then eliminate-v2 16; one of the 32 was the probe), D 30, B 60 (30, then v2 15 and v3 15), E 36 (24, then v2 12). The second wave spent 72 calls, 378,619 prompt and 26,530 completion tokens; the readings measurement (§1.8) 21 more, 99,290 prompt and 4,347 completion. Median latency 1.9 to 4.4 s per call once past the first; the first call of each process took 83 to 421 s on a machine whose load average stayed between 190 and 280 throughout (other agents' suites), and that first-call time is in the recorded latencies. No owner file, filename or dossier reached the model: every request is a synthetic case whose bytes are stored under `tools/promptbench/out/<site>/calls/`.

**Local arm (qwen3:8b): 62 of 144 calls recorded, at C and D** — C: eliminate 16 of 16 (run after the reboot, 19:15 to 19:37 on 2026-09-06) and walk 16 of 16 (seven before the reboot at loads of 190 to 280, the rest after); D: ladder and shelves 15 of 15 each (19:51 to 20:18, load 2.9 to 7.0). Every call set `num_ctx` 16,384 against a `prompt_eval_count` of 5,137 to 5,222, thinking off, `done_reason: stop`, no truncation; the one-minute load average is recorded before and after each call (`meta.settings.load_average_1m_before/after`) and summarised per arm as min / median / max. Median latency once the machine was quiet: 64 s (eliminate); the walk arm's median is dominated by its pre-reboot calls. The local arms for B, E and A were **not run**: at the measured 40 to 170 s per call the remaining 82 calls were one to four hours of a shared machine, and the coordinator asked for the packet to be closed on what had been produced. They resume past what is recorded with the same command per site (`python3 -m tools.promptbench run --site <site> --candidates <a>,<b> --models local --out tools/promptbench/out/<site>`, then `score` and `tables`); the bench skips recorded cases. Until they run, §4, §5 and §1 carry cloud numbers only and say so, and no ratification that names the local tier can rest on them.

## 9. What this wave did not do, and the next one should

1. The local arms for B, E and A (§8); and, given what the C and D local arms showed, a decision on whether the local tier is measured with thinking on before any more local calls are spent on wording.
2. ~~v2 texts~~ — measured (§2.7, §4.7, §5.7, §1.7). Next: E's one-child sentence; A's `school` wording with both exclusions; B's shape question for the B03 reading; C's G6 decision, which now costs the shared-branch case.
3. The one-real-file bench proof of `104` §7 Phase 0b, once the builder change G3 exists in some form.
4. Three runs per condition and a median (`104` §13.4) before any of these numbers is read as more than a first measurement.

## 10. Audit of this packet against `103` §28.1, step by step, and what a second run must show

Done on 2026-09-06 after the reboot that stopped the first wave. A step is called satisfied by the artefact, not by the section that claims it.

| Step | A_fact (glossary) | C_placement | D_residual | B_group | E_template |
|---|---|---|---|---|---|
| 1. Requirements traced to `00` and to the validator's checks | §1.1, 7 rows | §2.1, 15 rows with the validator column | §3.1, 13 rows | §4.1, 13 rows | §5.1, 10 rows |
| 2. The draft traced line by line; dossier keys checked by a test | the template is untouched; the two entries trace to `104` §11.2 step 1 (§1.2) | §2.2.1 | §3.2.1 | §4.2.1 | §5.2.1 |
| 3. At least 12 stress cases: `00`:239 plus the site's own failure modes | 14; §11.1 mechanisms at A01, A02, A04 | 16; two supported homes C04/C05, contradicted term C03, shared transcript C04/C05, MIT-inside-submit C10, §11.1 at C14/C16 | 15; gate screenshot never a trip D02/D03/D15, admissions confirmation returned D01 | 15; generic hub B04/B08, one code two terms B02, Duke essay inside a Columbia packet B03 | 12; parent dimension repeated E02, author as collector E03 |
| 4. Bakeoff, at least two candidates, both models | cloud 3 × 14; local LOCALA | cloud 3 × 16 (eliminate-v2 added); local 2 × 16 | cloud 2 × 15; local 2 × 15 | cloud 4 × 15 (v2, v3 added); local LOCALB | cloud 3 × 12 (v2 added); local LOCALE |
| 5. Ratification with the numbers and the two limits stated | §1.6; limits in §1.5 | §2.6; limits above §3 | §3.6; limits above §4 | §4.6; limits above §5 | §5.6; limits above §6 |
| 1.8 readings key (R-08) | traced AR-R1 to R6; 7 cases; 3 arms × 7 cloud calls; cache-hit tokens per arm; G18 | — | — | — | — |
| 6. Strict post-ratification test (bytes match the digest; keys match the builder) | not yet applicable: nothing is ratified. The pre-form exists for every draft: `test_the_manifest_digests_are_the_bytes_on_disk` and `test_the_text_is_a_constant_that_names_the_dossier_exactly` | same | same | same | same |

Three findings of the audit that the sections above do not state on their own:

- **Step 3, C:** `103` §28.1 names "a term the tree does not carry" as a C failure mode. C03 covers the contradiction direction (the file states a term a deeper node disagrees with); the other direction — the file states a term and no candidate carries a term level at all — has no case. It is a stress-suite addition for the next wave, not a reason to spend a call now.
- **Step 4, corpus:** stated in §0. No `SORTING exact` number exists in this packet; every outcome metric here is on synthetic cases.
- **Template ids and `104` §12.5:** that section says observe-only runs use a template id prefixed `draft.`; the ids here carry `unratified` and a date inside the id (`c_placement.unratified.eliminate.2026-09-06`). Both mark the fingerprint as non-ratified; they are not the same string rule. If the owner wants §12.5's prefix, the rename happens before any observe-only wiring, with a new manifest row and digest, never by editing a row a run has recorded.

**What one run supports, and what a second run has to show.** Every winner in this packet is a one-run, temperature-0, cloud-only ranking; `104` §13.4 asks for three runs and a median before a number is read as more. The second run is not a formality: for each site there is one measured case the ranking rests on, and if it does not reproduce, the ranking does not stand.

| Site | Ahead on this run | The ranking rests on | A second run must show | And it would not be enough if |
|---|---|---|---|---|
| A (`school`) | proposed `school` entry | A01 reversed (essay leaves `Georgetown Prep`); A04 and A13 unchanged | A01 declines again under the proposal and answers a school under the incumbent; no correct-answer case loses `school` | **Failed on the first retry (§1.7):** the third-wording arm carries the identical `school` entry and answered the target university on A01 and A09. The entry is not measured as a fix. |
| A (`subject`) | neither; the proposal is worse | 9 title-lifts against 6 | the third wording of §1.6 lifts fewer titles than both | **Measured (§1.7):** the third wording lifts no titles and equals the incumbent (5 wrong of 12); the exclusion clause did not make the model decline a book, a chapter or a study guide. |
| C | eliminate | grounding 0.950 vs 0.909, from walk's two `CITATION_NOT_IN_DOSSIER` losses (C02, C13) against eliminate's one span error (C16) and one tie (C07) | walk cites a group item again and eliminate does not, on C02 and C13 | both texts keep false-abstaining on C05; the v2 sentence is then the thing to measure, not the ordering |
| C (v2) | eliminate-v2 | C05 placed on the shared branch (weak, G6); 12 of 12 and 4 of 4 on one run | C05 placed again and no case lost; the C16 span error staying away would show it was noise | the local arm still cites group items under v2, which sentence (1) was written for and which is unmeasured locally |
| D | ladder on the cloud; shelves on the local arm; level across both | D02 alone on the cloud (gate screenshot to the approved travel area, not Receipts), and it did not reproduce locally, where both texts chose Receipts | a second cloud run on which ladder chooses the travel area on D02 again and shelves does not; without it the two texts are a tie and the ratification question becomes which text's failure is cheaper (ladder's mis-shelving, shelves' uncited returns) | D05 stays `abstain` under both on the cloud, since the ladder's fifth rung was written to prevent exactly that; and D13 stays in Receipts locally, which is a tier problem no wording fixed |
| B (v3) | anchors-first-v3 | the same eight right and five refused as v1, with 15 of 15 valid where v2 had 9 | 15 of 15 valid again on a run whose `coherent: yes` answers all carry a term (the case that broke v1's B01) | B03 stays `no` under v3, which it did on this run: the sentence is now measured as having no effect, and the decision is the shape or the acceptance of that reading |
| B | anchors-first | B08 (the `00`:63 Columbia group refused) and B01 (four-questions' broken JSON) | four-questions forms the Columbia group again; B01's JSON defect either recurs or is shown to be G13 by a run with `response_format: json_object` | B03 stays a false abstention under both, which makes the v2 sentence the decision, not the text |
| E (v2) | what-a-person-opens-v2 | 8 of 11 with 10 of 12 parseable, from 3 of 11 with 5 of 12 | the one-child sentence (E v3) turns E06 and E12 without losing the eight | the parse rate falls back under a text change, which would mean the last-key rule is necessary and not sufficient |
| E | what-a-person-opens, not put forward | 3 of 11 against 2 of 11 with 15 of 24 responses unparseable | the reordered payload (ending on a scalar) parses on the cases that failed, so that the design comparison is on 11 cases instead of 5 | the one-child rule keeps failing (E06, E12), which is a design defect no shape change fixes |

The local tier is a separate question from all of the above: on the two sites where it was measured, the texts scored within one case of each other and neither made the model take a no-target answer on any of the six should-abstain cases (§2.3, §3.3), and at D it filed a protected record into an approved area under both wordings. A second local run should be at a different setting (thinking on, `104` R-18) before it is a second run of the same thing.

## 11. Should-abstain, by site and by model: was abstention ever produced, and under which wording

The one table the owner needs to read the local model's fitness for placement. "Abstention" is the site's no-target answer: `destination: "none"` at C; `leave_in_current_location`, `mark_review_later` or `abstain` at D; `coherent: "no"` or `"insufficient"` at B; `domain: "none"` at E; a declined field at A. A count is abstentions on the cases labelled should-abstain; a false abstention is on a case labelled answerable.

| Site | Should-abstain cases | Cloud (deepseek-chat, temperature 0) | Local (qwen3:8b, thinking off, `num_ctx` 16,384) |
|---|---|---|---|
| C_placement | 4 (two-home transcript, generic hub, invoice number, noise OCR) | **Produced under every wording**: walk 4 / 4, eliminate 4 / 4, eliminate-v2 4 / 4. False abstentions: 1 / 12 under walk and eliminate (C05), 0 / 12 under eliminate-v2. | **Never produced**: walk 0 / 4, eliminate 0 / 4 (eliminate-v2 not run locally). Every should-abstain case was placed; two placements (generic hub, noise OCR) were accepted by the validator. False abstentions 0 / 12: the model never says `none`. |
| D_residual | 2 (unclear spreadsheet, nothing readable) | **Produced once under each wording**: ladder 1 / 2, shelves 1 / 2 (D11 `abstain`); D14 marked `unsupported`, which the label also accepts. D05 (noise OCR, labelled answerable) was `abstain` under both: 1 / 13 false abstention each. | **Never produced**: ladder 0 / 2, shelves 0 / 2. D11 went to the Review Later *area* rather than the `mark_review_later` action, D14 to the unsupported-material area rather than `abstain`; the model reaches for a target where the text offers a no-target action. False abstentions 0 / 13. |
| B_group | 5 (two terms, email-domain hub, download session, Columbia name, suffix family) | **Produced under every wording**: anchors-first 5 / 5, v2 5 / 5, v3 5 / 5; four-questions 4 / 5 (formed the Columbia group). False abstentions: B03 under all four (the Duke-essay reading). | LOCALB11 |
| E_template | 1 (no recoverable facts) | **Produced under every wording**: from-facts 1 / 1 (`domain: "none"`), what-a-person-opens 1 / 1 and v2 1 / 1 (an empty `dimensions` list, valid to the validator, not to the draft's schema). No false abstention. | LOCALE11 |
| A_fact (per field) | 5 cases with every asked field to decline (A02, A04, A07, A09, A13) | **Produced per field, never per response**: `school` declined on A02, A07, A09 under all three glossaries and on A01 under the proposal alone; `subject` declined on A04, A09 under all three; but no arm declined every field on any should-abstain case (A04 and A13 always yield a school; A02, A07 always a subject). | LOCALA11 |

What the table supports on 2026-09-06: on the two sites measured locally with 62 calls under four wordings, the local model produced no abstention of any kind on six should-abstain cases and no false abstention on twenty-five answerable ones. It is not a wording effect — the same texts produce 4 of 4 and 1 of 2 on the cloud — and it is the AbstentionBench finding (§6 R2) at 8B scale with thinking off. For placement, where a wrong placement moves a file into somebody's folder and stays there (`00`:114), a model that never says `none` is not fit under any text measured here; `104` R-18's setting (thinking on, a separated budget) is the next measurement, and it belongs to D1, not D2.

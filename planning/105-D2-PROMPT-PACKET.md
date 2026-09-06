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

### 2.3 Results (cloud, deepseek-chat, 16 cases × 2 candidates = 32 calls; local, qwen3:8b, 3 of 32 at the time of writing)

| arm | schema-valid | validator ok | grounding | abstain on should-abstain | correct on should-answer | correct **and** accepted | false abstain | accepted | median s | tokens (prompt / completion) |
|---|---|---|---|---|---|---|---|---|---|---|
| walk / cloud | 16 / 16 | 16 / 16 | 20 / 22 (0.909) | **4 / 4** | **11 / 12** | 8 / 12 | 1 / 12 | 8 / 16 | 2.1 | 82,529 / 3,053 |
| eliminate / cloud | 16 / 16 | 16 / 16 | 19 / 20 (0.950) | **4 / 4** | **11 / 12** | 8 / 12 | 1 / 12 | 8 / 16 | 1.9 | 82,017 / 2,867 |
| walk / local | 2 / 3 | 3 / 3 | 5 / 7 | — | 3 / 3 | 1 / 3 | 0 / 3 | 1 / 3 | 319 | 15,553 / 1,106 (`num_ctx` 16,384) |

**A tie on the two metrics that matter, broken by what failed.** Both texts placed 11 of 12 answerable files correctly and abstained on all 4 should-abstain files (the generic hub, the invoice number, the noise OCR, the two-home transcript). Both false-abstained on the same case, C05 — the transcript with a shared branch on the list: each demanded that the file's own text name a university and did not treat two accepted-group memberships as support for the shared-material node. That is a wording gap in both, and the v2 sentence is known: *a shared branch is supported by the two groups the file belongs to*.

Where they differ is how a correct answer was lost at the validator. **walk** lost C02 and C13 to `CITATION_NOT_IN_DOSSIER`: its "context" support invited the model to cite the `accepted_group` item as a metadata field, which the text forbids and the model did anyway (2 of 16). **eliminate** lost C16 to `CITATION_SPAN_MISMATCH` (it cited the word `essay`, which the body sentence does not contain — an honest span error) and C07 to a self-declared tie (`support` 1, `next_support` 1 on the refinement case, the two-condition rule turning a right answer into `weak`, G6). Both lost C06 to `CONFLICT_IGNORED`, which is G1 and not the text's. The local model (3 calls, 5 minutes each under a load average above 200) placed all 3 correctly and lost 2 to the same group-citation defect as walk.

**Winner: eliminate**, provisionally — equal on placement and abstention, ahead on grounding (0.950 vs 0.909), and its two losses are one span error and one honest tie rather than a rule the text states and the model breaks. The v2 to measure before ratification: eliminate's ordering, plus one sentence making the shared-branch case explicit and one making "a group is support, not a citation" unmissable.

### 2.4 Stress cases

| case | persona | traces | expectation | eliminate / cloud | walk / cloud | walk / local |
|---|---|---|---|---|---|---|
| C01 — a syllabus that uniquely matches one node | Priya | 00:110, 104:13.5 | n-02 | correct / acc_direct | correct / acc_direct | correct / acc_direct |
| C02 — a sparse homework file placed through its accepted group | Priya | 00:108, 00:111 | n-03 | correct / acc_direct | correct / reject CITATION_NOT_IN_DOSSIER | correct / reject CITATION_NOT_IN_DOSSIER |
| C03 — a term the deeper node carries and the file contradicts | Priya | 00:111, 00:107 | n-03 (the term-less path) | correct / acc_direct | correct / acc_direct | correct / reject CITATION_NOT_IN_DOSSIER |
| C04 — a transcript with two supported homes and no shared branch | multi-life | 00:113, 00:239 | none | abstained | abstained | ANSWERED / reject |
| C05 — the same transcript when a shared branch exists | multi-life | 00:113 | n-11 | **false abstain** | **false abstain** | — |
| C06 — a Duke essay retrieved by a Columbia packet, conflict recorded | multi-life | 00:107, 00:112, 00:114 | n-13 | correct / reject CONFLICT_IGNORED (G1) | correct / reject CONFLICT_IGNORED (G1) | — |
| C07 — refinement: a lecture sitting in its own course folder | multi-life | 104:13.8, 00:22 | n-15, deeper_in_own_folder | correct / weak INSUFFICIENT_MARGIN (G6) | correct / acc_direct | — |
| C08 — removal: a report card in the folder its parent keeps it in | Tom | 104:13.8, 00:22, 68:F5 | n-17, out_of_own_folder | correct / acc_direct | correct / acc_direct | — |
| C09 — a file linked only by a generic hub | multi-life | 00:63, 00:109 | none | abstained | abstained | — |
| C10 — MIT inside submit | Priya | 00:43, 00:239 | n-03 | correct / acc_direct | correct / acc_direct | — |
| C11 — a number that is an invoice, not a course | Tom | 00:239, 00:46 | none | abstained | abstained | — |
| C12 — a course file with no recoverable kind of work | Priya | 00:99, 00:111 | n-05 (scoped General) | correct / acc_direct | correct / acc_direct | — |
| C13 — a packet member placed inside its confirmed packet | multi-life | 00:112 | n-09 | correct / acc_direct | correct / reject CITATION_NOT_IN_DOSSIER | — |
| C14 — an essay naming the author's school and the target university | multi-life | 00:44, 104:11.1 | n-21 | correct / acc_direct | correct / acc_direct | — |
| C15 — a screenshot whose OCR is noise | multi-life | 00:110, 00:125 | none | abstained | abstained | — |
| C16 — a university course essay whose own course node exists | multi-life | 104:11.1, 00:44 | n-23 | correct / reject CITATION_SPAN_MISMATCH | correct / acc_direct | — |

### 2.5 Contract gaps found at C

G1 (conflict ids keyed on the wire, compared raw — C06 measured), G2 (R-15, a real `project` value is "invented"), G3 (no node profiles, opaque ids — the bench supplies them), G6 (the two numbers — C07 measured), in §7.

### 2.6 The ratification question

Ratify **eliminate** (`c_placement.unratified.eliminate.2026-09-06`), its response schema and shaping policy, **conditional on**: (a) the builder change G3 (candidate profiles as `candidate` items; accepted groups as `accepted_group` items) that the text describes; (b) G1 fixed or C wired with `conflicts=()` until it is; (c) a decision on G6 — keep `support`/`next_support` as whole-number citation counts with the tie-means-none rule, or drop the two-condition rule from the model path. And authorise a v2 measurement (the shared-branch sentence and the group-is-not-a-citation sentence) before the text is installed.

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

### 3.3 Results (cloud, deepseek-chat, 15 cases × 2 candidates = 30 calls)

| arm | schema-valid | validator ok | grounding | abstain on should-abstain | correct on should-answer | correct **and** accepted | false abstain | accepted | median s | tokens (prompt / completion) |
|---|---|---|---|---|---|---|---|---|---|---|
| ladder / cloud | 15 / 15 | 15 / 15 | 20 / 20 (1.0) | 1 / 2 | **12 / 13** | 11 / 13 | 1 / 13 | 12 / 15 | 2.2 | 78,469 / 2,752 |
| shelves / cloud | 15 / 15 | 15 / 15 | 21 / 21 (1.0) | 1 / 2 | 11 / 13 | 10 / 13 | 1 / 13 | 12 / 15 | 2.0 | 79,759 / 2,870 |

Every citation resolved and span-matched under both texts (41 of 41). The one case that separates them is D02, the boarding-gate screenshot when the person has approved `Personal > Travel > Confirmations`: **ladder** chose it, as `00`:125 says; **shelves** chose Receipts and Confirmations — its own shelf description ("does not hold a trip, because there is no trip shelf unless the person made one") was overridden by the transactional reading. Both returned the admissions confirmation to the Columbia branch (D01) and the course reading to the course branch (D10), both marked the encrypted archive unsupported and the redacted statement protected, both refused the unrelated broad parent (D15), both chose Reference Clips for the recipe and Reading Inbox for the DOI paper, and both left the gate screenshot at Temporary Screenshots when no travel area existed (D03).

The two "should-abstain" misses are the same under both and are worth reading: D14 (nothing readable) was marked `unsupported` rather than abstained — labelled as also acceptable, so it is a correct answer the abstention metric counts against; D05 (noise OCR, no context) was `abstain` where the label wanted "leave in place" or the screenshot area — the model treated unreadable OCR as nothing to read at all. D08 is G1: both texts echoed the flagged relationship id and were rejected `STRONGER_RELATIONSHIP_OVERLOOKED` for it.

**Ahead on this run: ladder**, on D02 alone and on equal ground everywhere else — one case, one run, cloud only; the local arm and the three-run median are owed before "winner" means more than that.

### 3.4 Stress cases

| case | persona | traces | expectation | ladder / cloud | shelves / cloud |
|---|---|---|---|---|---|
| D01 — admissions confirmation screenshot | multi-life | 00:125, 00:126 | return → b-01 | correct / acc_direct | correct / acc_direct |
| D02 — gate screenshot, travel confirmations approved | multi-life | 00:125 | choose r-09 | correct / acc_direct | **WRONG** (r-05) / acc_direct |
| D03 — gate screenshot, no travel area | multi-life | 00:125 | choose r-01 or leave | correct / acc_direct | correct / acc_direct |
| D04 — a recipe screenshot | Tom | 00:125 | choose r-03 | correct / acc_direct | correct / acc_direct |
| D05 — unreadable OCR, no context | multi-life | 00:125, 00:239 | leave or choose r-01 | false abstain (`abstain`) | false abstain (`abstain`) |
| D06 — an encrypted archive | Mara | 00:31, 00:120 | mark unsupported | correct / acc_direct | correct / acc_direct |
| D07 — boarding pass, no travel area, Receipts approved | multi-life | 00:120, 00:125 | choose r-05 | correct / acc_direct | correct / acc_direct |
| D08 — a figure with a flagged stronger relationship | multi-life | 00:126, 00:63 | return → b-03 | correct / reject (G1) | correct / reject (G1) |
| D09 — a paper with a DOI, no course or project | Priya | 00:120 | choose r-06 | correct / acc_direct | correct / acc_direct |
| D10 — a paper the course lists as required reading | Priya | 00:126 | return → b-02 | correct / acc_direct | correct / acc_direct |
| D11 — a spreadsheet whose purpose is unclear | Tom | 00:122, 00:124 | review later / abstain | abstained | abstained |
| D12 — a standalone certificate | Tom | 00:120 | choose r-04 | correct / acc_direct | correct / acc_direct |
| D13 — a statement with a redacted account number | Tom | 00:120, 00:185 | mark protected | correct / acc_direct | correct / acc_direct |
| D14 — nothing readable at all | Mara | 00:124, 00:126 | abstain (or mark unsupported) | mark unsupported (acceptable) | mark unsupported (acceptable) |
| D15 — gate screenshot offered an unrelated broad parent | multi-life | 00:124, 00:125 | choose r-01 or leave | correct / acc_direct | correct / acc_direct |

### 3.5 Contract gaps found at D

G1 (relationship ids keyed vs raw — D08 measured), G3 (no area profiles), G5 (same-file check is fail-open on keyed citations), G7 (broad parent and residual destination collapse to one disposition; only the injected `residual_action_of` keeps them apart), G8 (a return's target must be a frozen node), in §7.

### 3.6 The ratification question

Ratify **ladder** (`d_residual.unratified.ladder.2026-09-06`), its response schema and shaping policy, conditional on the same builder change as C (area and branch profiles as items, G3), on G8's reading (a return names the branch built from the group), and on G1 being fixed or D wired with `conflicts=()`; and confirm that `residual_action_of` reads the eight actions from the response payload (G7).

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

| case | persona | traces | expectation | anchors-first / cloud | four-questions / cloud |
|---|---|---|---|---|---|
| B01 — course group, syllabus and lecture anchors, sparse homework candidate | Priya | 00:57, 00:60 | yes; hw uncertain or include | correct / acc_direct | broken JSON / reject SCHEMA_INVALID |
| B02 — one course code, two terms | Priya | 00:63, 00:62 | no / insufficient | abstained (no: two terms) | abstained (no: two terms) |
| B03 — a Duke essay inside a Columbia packet | multi-life | 00:58, 00:59, 00:62 | yes; Duke essay excluded, outlier | false abstain (members 4/4 right) | false abstain (members 4/4 right) |
| B04 — files bridged only by an email domain | multi-life | 00:63, 00:57 | no / insufficient | abstained (generic-similarity) | abstained (generic-similarity) |
| B05 — a purpose-coherent submission packet | multi-life | 00:45, 00:61 | yes; all five included | correct / acc_direct | correct / acc_direct |
| B06 — a tight download session | Tom | 00:61, 00:45 | no / insufficient | abstained | abstained |
| B07 — a research abstract that also supports an application | multi-life | 00:63, 00:48 | yes; abstract included | abstract `uncertain` | correct / acc_direct |
| B08 — a university name that is target, provider and employer | multi-life | 00:63 | no / insufficient | abstained | **ANSWERED: a Columbia group** |
| B09 — a coherent course group that needs a label | Priya | 00:59 | yes; label | correct / acc_direct | correct / acc_direct |
| B10 — a conflicting course code among the candidates | Priya | 00:59, 00:62 | yes; PHYS 2801 excluded, outlier | correct / acc_direct | correct / acc_direct |
| B11 — a photo event with a screenshot in the same hour | multi-life | 00:56, 00:32 | yes; screenshot out | correct / acc_direct | correct / acc_direct |
| B12 — a TA's solution set with her own problem set as candidate | Priya | 68:F6, 00:59 | yes; PHYS 1401 set excluded | correct / acc_direct | correct / acc_direct |
| B13 — versions of one essay | multi-life | 00:239, 00:56 | yes; all included | correct / acc_direct | correct / acc_direct |
| B14 — a litigator's matter with an e-filing receipt | Mara | 68:2, 00:59 | yes | correct / acc_direct | correct / acc_direct |
| B15 — duplicate suffixes on unrelated files | Tom | 00:239, 00:172 | no / insufficient | abstained | abstained |

### 4.5 Contract gaps found at B

G4 (no authorities constructed; `allowed_vocabulary` undefined), G9 (the seam carries no basis, no excerpt-to-member mapping, no retrieval channel), G11 (`apply_p8_verdict` drops label, category and per-member decisions — `104` R-16), G13 (broken JSON when the payload ends on a populated array — B01), in §7.

### 4.6 The ratification question

Ratify **anchors-first** (`b_group.unratified.anchors-first.2026-09-06`), its response schema and shaping policy, conditional on the seam change G9 that the text describes and on `allowed_vocabulary` being defined as the situation ids (G4); wire it observe-only until P9 reads the label, the category and the per-member decisions (G11). Authorise a v2 measurement carrying the B03 sentence and a payload whose last key is a scalar (G13).

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

### 5.3 Results (cloud, deepseek-chat, 12 cases × 2 candidates = 24 calls)

| arm | JSON parses | schema-valid | validator ok | grounding | abstain on should-abstain | correct on should-answer | correct **and** accepted | accepted | median s | tokens (prompt / completion) |
|---|---|---|---|---|---|---|---|---|---|---|
| from-facts / cloud | 3 / 12 | 3 / 12 | 3 / 12 | 9 / 9 (1.0) | 1 / 1 | 2 / 11 | 2 / 11 | 2 / 12 | 4.4 | 67,281 / 5,997 |
| what-a-person-opens / cloud | 6 / 12 | 5 / 12 | 6 / 12 | 18 / 18 (1.0) | 1 / 1 | 3 / 11 | 3 / 11 | 5 / 12 | 4.2 | 67,353 / 6,690 |

**Neither is ratifiable, and the reason is the shape, not the design.** Fifteen of the 24 responses are not valid JSON: deepseek-chat closes the payload as `...]]}],"citations":[` — one bracket too many — every time the payload's last key is a populated array (`example_label_chains`, an array of arrays). The same defect took B01 (`"merge_terms":["Spring 2026"]}]`); C and D, whose payloads end on a scalar or an empty array, never produced it in 62 calls. Read as designs, the parsed answers are the right ones: the photo template time-first (`capture_year`, `location`, `event`), the research group without its parent's `project`, the consulting engagement by document kind and not by author, the household statements by institution and record type with no account holder, the D&D campaign by template-local `campaign` and `session`. Two of what-a-person-opens' accepted answers were wrong by `00`:97's one-child rule (a `project` level over one project, E06 and E12 — labels corrected after the run for the same rule, §5.4), and one parsed abstention at E10 carried an empty `dimensions` list instead of `domain: "none"`, valid to the validator and not to the draft's schema.

**Winner: what-a-person-opens**, on 3 of 11 against 2 of 11 and twice the schema-valid rate — and it is not put forward for ratification. The v2 is mechanical and measurable: move `example_label_chains` up and end the payload on `sensitivity_policy_ref` (a scalar), and, product-side, request `response_format: json_object` at the transport (G13), which DeepSeek documents for exactly this.

### 5.4 Stress cases

Three labels were corrected after the first run, by `00`:97's own rule that a level with one child is no level: E04 (every member is PHYS 1401, so `subject` is one-child and `work_type` alone is right), E06 and E12 (one repository and one project; only `artifact_type` splits the files). The suite records the correction beside each case; the numbers above are after it.

| case | persona | traces | expectation | from-facts / cloud | what-a-person-opens / cloud |
|---|---|---|---|---|---|
| E01 — a trip's photos: time first, then the occasion | multi-life | 00:95, 00:70 | capture_year first, event; no people | broken JSON (design right: year, location, event) | broken JSON (same) |
| E02 — a research group whose parent already is the project | multi-life | 00:97, 00:99 | artifact_type; no project | broken JSON (design right) | correct / acc_direct |
| E03 — consulting deliverables all by one author | Mara | 00:44, 00:97 | no authored_by / our_firm | broken JSON (design right: document kind) | correct / acc_direct |
| E04 — a course where every file shares one term | Priya | 00:97, 00:99 | work_type; no term, no subject | correct / acc_direct | broken JSON |
| E05 — a domain the library has no schema for | Tom | 00:97, 43:9 | ≥1 template-local; no borrowed keys | broken JSON (design right: campaign, document_type) | broken JSON (campaign, session) |
| E06 — a recurring pattern that tempts publication | multi-life | 00:97, 43:9 | artifact_type; no repository/project (one child) | broken JSON | WRONG (project level) / acc_direct |
| E07 — financial records with a person as collector | Tom | 00:97, 00:185 | institution; no account_holder | broken JSON (design right) | broken JSON |
| E08 — more levels than a tree should have | multi-life | 00:97, 00:99 | artifact_type; ≤ 4 | correct / acc_direct | broken JSON |
| E09 — a dimension no file has a value for | multi-life | 00:97 | artifact_type; no venue, no lab | broken JSON | correct / acc_direct |
| E10 — a group with no recoverable facts | Tom | 00:97, 00:63 | abstain | abstained (`domain: "none"`) | abstained (empty dimensions) |
| E11 — recruiting documents: employer before cycle | multi-life | 00:95, 00:70 | target_employer first | broken JSON (design right) | broken JSON |
| E12 — a code project: repository, not language | multi-life | 00:30, 00:97 | artifact_type; no language, no project | broken JSON | WRONG (project level) / acc_direct |

No fragment was ever published or referenced (0 `FRAGMENT_*` reasons), no live field key was relabelled template-local, and every citation that reached the validator resolved.

### 5.5 Contract gaps found at E

G10 (no channel for the schema id, the parent's expressed value, the sensitivity policy reference or the depth limit), G12 (no live caller: `routing.py`'s C3 refusal never becomes a request), G13 (broken JSON when the payload ends on a populated array — 15 of 24 here), in §7.

### 5.6 The ratification question

Not yet. Authorise a v2 of **what-a-person-opens** with the payload reordered to end on a scalar, measured on the same 12 cases, and decide G13 at the transport; E has no live caller (G12), so nothing is lost by the wait.

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

## 8. Cloud calls used and tokens spent

From `tools/promptbench/out/cloud_ledger.json`, the one ledger spent before each socket opened:

| | calls | prompt tokens | completion tokens |
|---|---|---|---|
| cloud, deepseek-chat, temperature 0, no `response_format` | **144 of 400** | 742,827 | 44,839 |

Per site: A 28, C 32 (one of them the probe), D 30, B 30, E 24. Median latency 1.9 to 4.4 s per call once past the first; the first call of each process took 83 to 421 s on a machine whose load average stayed between 190 and 280 throughout (other agents' suites), and that first-call time is in the recorded latencies. No owner file, filename or dossier reached the model: every request is a synthetic case whose bytes are stored under `tools/promptbench/out/<site>/calls/`.

**Local arm (qwen3:8b), when this wave paused: 4 of 144 calls recorded**, all at C (walk), 5 to 7 minutes each under that load (`prompt_eval_count` 5,167 to 5,200 against `num_ctx` 16,384, thinking off, `done_reason: stop`, no truncation). C01, C02 and C03 were placed correctly (C01 accepted; C02 and C03 lost to the same group-citation defect as walk on the cloud, `CITATION_NOT_IN_DOSSIER`); **C04, a should-abstain case, was answered** — the local model chose a home for the two-packet transcript, and the answer was rejected on its citation. Two more things the local run showed and nothing validates: on C01 it set `refinement: deeper_in_own_folder` with no candidate marked as the file's current folder (the v2 must make "not_applicable when no candidate is the current folder" unmissable), and its C01 answer was invalid against the draft's own schema while valid to the validator (a `per_dimension_support.value` outside the file's text). The chain was **stopped at the pause** so it would not keep a shared machine busy; it resumes past what is recorded with the same command (`zsh run_local_chain.sh`, or per site `python3 -m tools.promptbench run --site <site> --candidates <a>,<b> --models local --out tools/promptbench/out/<site>`). The local numbers are owed before any ratification that names both models, as `103` §28.1 step 4 requires.

## 9. What this wave did not do, and the next one should

1. The local arm, beyond 4 calls (above).
2. **v2 texts, each a stated delta and each measured on the same cases**: C — eliminate plus the shared-branch sentence and "a group is support, not a citation"; B — anchors-first plus "a contradicting candidate is an outlier of a coherent group"; E — what-a-person-opens with the payload ending on a scalar; A — the revised `subject` wording of §1.6. Each is one more run of 12 to 16 cloud calls per arm, inside the cap.
3. The one-real-file bench proof of `104` §7 Phase 0b, once the builder change G3 exists in some form.
4. Three runs per condition and a median (`104` §13.4) before any of these numbers is read as more than a first measurement.

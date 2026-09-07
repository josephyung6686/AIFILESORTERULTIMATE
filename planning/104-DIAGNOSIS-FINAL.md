# 104 — Diagnosis, final: three diagnoses reconciled into one issue register and one plan

**Written 2026-09-05 by Claude Fable 5.1 at the owner's instruction**, reconciling with a fresh
reading:

- **F** — `planning/103-FABLE-5.1-DIAGNOSIS.md` Parts I–III (this author, earlier today);
- **A** — `asrtra digniositce 2026-09-05.md` at the repo root (the other model's diagnosis;
  `docs/superpowers/plans/2026-09-05-diagnostic-reintegration-plan.md` is the same text, four
  lines apart);
- **K** — `planning/103-THE-CONSTITUTION-RUN.md` (the other session's four-commit scoreboard).

HEAD is `45b9f4e`. Since F was written, `3ac0c0b` committed the semantic channel, `3e4a64d` made
`work_type` a closed-membership value, and `45b9f4e` added K. The working tree is clean apart from
untracked diagnosis files.

**Method.** Every point where the three disagree was settled by running the product or reading
the code, not by preferring a document. Two new measurements were taken for this reconciliation:
a **cloud run over the owner's 199-file corpus on HEAD** (`tools.groundtruth --enable-cloud`,
`academic.coursework`, semantic channel off, scratchpad `gt-cloud/`), and the **full suite on
HEAD**: 8022 passed, 19 skipped, 28 xfailed. Nothing was committed; nothing in `src/` was edited.

Source of truth remains `00` (cited `00`:LINE) with `66`, `80`, `81` §14, `64`, `75` for
onboarding and customisation, the corrected purpose statement and the constitution as amendments.
Where they conflict the conflict is listed in §6, unresolved.

---

## 1. The verdict, merged

The three diagnoses agree on the shape of the failure and disagree on one number, and the number
mattered. **The skeleton is complete and the mutation half works** (F ran freeze, apply, stale
refusal and undo; A confirmed the paths are reachable). **The model decides almost nothing:** four
of five model sites are wired to `None` with no ratified prompt (F, A), and the one wired site is
refused by the privacy gate for most ordinary files (F). K reported that coverage had been fixed
("files blocked from the model: 114 → 19"). **Measured today on HEAD with cloud on: 42 of 199
files reached the model; 130 were refused at the gate (40 `no_safety_evidence`, 90
`unclassified`); 19 were withheld at the route; 8 had nothing releasable or pending and left no
record.** K counted only the route. **The human half of the design has no surface** (F, A): one
`--situation` per disk, groups auto-accepted by rules, nesting chosen first-pass, so the product
abstains on 30 of the 41 files whose right folder is known, and with the model on it now places 5
wrong and spills 17 files labelled as other domains into Coursework, up from 0 and 11 offline (§11 corrects the 5 that an earlier table carried).

Two things only one diagnosis found, both confirmed here: **A** found that the filename is admitted
by the gate as a reference and never serialised, so `e31c70f`'s "the model is shown the filename"
is false at the byte level; and that a whole DOCX body travels as a span-less container value, so
the nominal 4,000-token cap is not a bound. Today's cloud run confirms the second on the owner's
own files: **7 of 42 dossiers exceeded 16,000 bytes; the largest was 45,843 bytes.** **F** found
that a file edited between runs leaves a ghost version that is placed, frozen and blocks
`--reject`, that `--send-set` writes no review action, and everything in the onboarding and
customisation layer (Part II), which A and K did not examine.

**The corrections each diagnosis needs are in §8.** None of the three was wrong about the
architecture; F underestimated the whole-document leak, K mismeasured coverage, A listed one
ruled-out reader as a gap.

---

## 2. What each diagnosis did, and what only it could see

| | F (Fable 103) | A (astra) | K (constitution run) |
|---|---|---|---|
| Method | Read `00` + onboarding docs; traced `cli.main`; 11 gesture runs; freeze/apply/undo; one cloud run on 5 synthetic files; offline ground truth; suite | Read `00`; traced `cli.main`; probes calling real extractor, gate and dossier builder with canaries; no cloud, no transport | Four cloud runs over the owner's corpus across four commits; scoreboard deltas |
| Unique to it | Gate refusal chain and its date; ghost file version; `--send-set` unrecorded; `keep-as-it-is`; onboarding, role matcher, questions, review gestures; the strict xfail backlog | Filename never serialised; whole-DOCX release; dimension values validated against node ids (L3); group verdict application lossy (L1); packaging gaps; opaque-only folder terminal state | Field-fill and placement trajectory per commit; the six files one level short; `.pdf`-as-folder fix; the `E1006` vs `Python 1006` naming-authority argument |
| Its blind spot | Did not probe payload bytes, so under-rated the size leak (C7 as Medium) | Did not run a model or read a cloud database, so its coverage finding was reasoned rather than measured | Measured "blocked" at the route, not the gate; columns do not state whether the semantic channel was on, so its rows cannot be reproduced |

---

## 3. Contested claims, settled

| # | Claim | F | A | K | Settled by | Verdict |
|---|---|---|---|---|---|---|
| S1 | Ordinary files reach the cloud model | No: gate denies since `fd68cb6`; 5/5 synthetic refused | Reasoned: unclassified still denied after route permits (W14) | Yes: "114 → 19 blocked" | **Cloud run on HEAD:** 42 reached, 130 gate-refused, 19 route-withheld | **F and A right.** K's 19 is the route count; the gate refuses 130 more |
| S2 | The model is shown the filename (`e31c70f`) | Assumed true from the commit | No: `Filename` is `REFERENCE_ONLY`, never serialised (W7) | Yes | `privacy/gate.py:141` lists `Filename` in `REFERENCE_ONLY`; no filename bytes in `dossier.py`, `transport.py`, `release.py`, `resolve.py` | **A right.** The item passes the gate as a reference; no name reaches the model |
| S3 | The dossier is bounded | By count only; cap unmeasured (C7, Medium) | Not bounded: 90,139-byte DOCX dossier in a probe (W8, High) | silent | Cloud run: 7 of 42 dossiers over 16,000 bytes, max 45,843 | **A right, severity High.** Live on the owner's files today |
| S4 | The semantic channel changes outcomes | Committed now; edges written, placement identical (C22) | Neighbours never reach P11 (W4) | Removed 3 wrong and 3 flat placements, cost 4 abstentions, then fixed by `3e4a64d` | F's run with the channel on: byte-identical placement on 5 files; K's runs at 199 files | **Both true at different scales.** P9 grouping changes; P11 never reads `semantic_neighbours` |
| S5 | `subject` = 0 of 43 is a producer failure | Spelling mismatch with the owner's folder (C12) | not examined | Same: label follows the folder; an alias problem | Agreement | **Not a producer failure.** An alias between file spelling and folder name, which `00`:34 provides for and nothing populates |
| S6 | Coverage numbers in K's scoreboard | — | — | 15 fields correct, 0 wrong, 29/29 abstained after `3e4a64d` | Cloud run on HEAD, semantic off: 15 correct, **5 wrong**, 27/29 abstained, spillover 17 | **Partly reproduced.** Field fill matches; placement is worse than K's last column; K's per-column environment is unstated |
| S7 | EXIF reader is a missing capability | Ruled not to build (`94` F21): EXIF suppresses OCR | Listed as unbuilt U5 | — | `extractors/ocr_policy.py` trigger; `94` F21 | **Owner flag, not a gap.** Build only after the OCR trigger changes |
| S8 | Apply and undo work | Ran: move, stale refusal, byte-identical undo | Reachable, not run | — | F's runs R3–R5 | **Verified working** |
| S9 | A protected file is placed | 1 on the 4 Sep scorecard | — | — | HEAD offline and cloud runs: 0 placed, 1 unmarked, 8 extracted before classification | **Fixed between 4 Sep and HEAD** for placement; the extraction-order question stands |
| S10 | Release recorded on the frozen tree | First said no, then corrected | — | — | `FreezeRecord.catalogue_release_id` in `tree_design/freeze.py` | **Recorded.** `64` §5b–e still unbuilt |

---

## 4. The unified issue register

IDs are new and stable for this document. **Class:** M missing, D disconnected, W wired-wrong,
C design conflict, S safety, P process. **Severity:** Blocker (no model decision possible until
fixed), High (north-star or safety), Medium, Low. **Status:** run = confirmed by running,
code = confirmed by reading, ruled = owner decided, open = owner decision pending, latent =
confirmed but unreachable today. **Sources** name who found it. **Phase** is §7's.

### 4.1 The model as decision engine

| ID | Issue | Class | Sev | Status | Sources | Phase |
|---|---|---|---|---|---|---|
| R-01 | Gate denies every ordinary file a cloud call: basis `detector_no_safety_evidence` (41 files) and unclassified (95) refused; only basis `detector` (44) passes. Introduced `fd68cb6` 05 Sep 01:54 | W/C | Blocker | run; **ruled D1 = both** | F C1, A W14, K contradicted | 0, 1 |
| R-02 | `cli.model_route_permitted` permits what `Gate.release` denies; refusals land in `llm_refusal`, not `unresolved`, so K's scoreboard under-counted by 130 | W | High | run | F C3, A W14, K | 1 |
| R-03 | "Facts from a model: N written, from M files sent" counts gate refusals as sent | W | Medium | run | F C2 | 1 |
| R-04 | Sites B, C, D, E injected as `None` (`p8_run_call`, eight `PipelineInputs` fields, no E caller) | D | Blocker | run | F, A D1 D2 B1 | 1 |
| R-05 | No ratified prompt, response schema or shaping policy for B, C, D, E | M | Blocker | **ruled D2 = draft all four under the §28.1 protocol** | F, A U2 C7 | 1 |
| R-06 | Filename admitted as `REFERENCE_ONLY`, never serialised; `e31c70f`'s claim false at the byte level | W | High | code | A W7 B8 | 2 |
| R-07 | Whole DOCX body emitted span-less with no unit (`extractors/docx.py`), `is_whole_document` returns False on `unit_length=None`, so the full body is releasable; gate has no `measure_tokens`; `unreduced_fits=True` asserted; ledger ceiling 8 vs request 4000. **Live: 7 of 42 dossiers over 16,000 bytes today** | W/S | **High** | run + code | A W8 S1 S5 D7, F C7 | **1, before any cloud widening** |
| R-08 | 314 authored `needs_llm` readings loaded into `deferred_readings`, never reach a prompt | D | High | code | F, A D5 B10 | 1 |
| R-09 | P9 `active_schema_for` is a hand-kept tuple; a model fact outside four fields never seeds a group | W | High | code | F C6, A W5 | 1 |
| R-10 | With the model on: 22 `llm_supported` facts (20 `school`, 2 `subject`), 15/92 fields correct, exact still 0/41, **wrong 0 → 5, spillover 11 → 17** under one situation. Mechanism and fix chain in §11 | W | High | run | K (fill), F run (placement) | 1, 3 |
| R-11 | `cli.run.evidence_for`: every file offered every accepted group id; locators fabricated as `heading`, `(0, len)`, `direct-anchor`; first citation only; `semantic_neighbours=()`, `related_files=()`, all entity frequencies 1 | W | High | code + run | A W3 W4 B7, F C22 | 2 |
| R-12 | Semantic channel (`3ac0c0b`) writes edges P11 never reads; recogniser silent under 100 characters, which is the sparse file `00`:56 names | W | Medium | run | F C22, A W4, K | 2 |
| R-13 | Dossier rows dedupe by content; no prior-verdict lookup, so declined fields are re-asked and re-spent; no invalidation on prompt, model, schema or policy change | W | Medium | code | A W12 D7, F | 2 |
| R-14 | No `response_format` at the API; `actual_cost` is a constant, not observed usage | W | Low | code | A W13, F | 2 |
| R-15 | `_invented_dimension` checks date, institution and project **values** against the node-id vocabulary, so any real value is "invented" once C is wired | W | High | latent, code | A L3 | 3 |
| R-16 | `apply_p8_verdict` writes no `display_label`, `group_category` or `coherence_verdict`; per-member include/exclude/uncertain collapses to blanket memberships. **Closed (merge of 9b6eafc):** the group row is written once, after its author has spoken (`groups_never_overwritten` forbids a later write), with verdict, category, label and `label_source=LLM_PROPOSED`; excluded members are not members, uncertain ones carry review, unmentioned ones get no row. R-80 records what a second answer does. | W | High | latent, code | A L1 B9 | closed |
| R-17 | C/D dossier enumerates all legal node ids with no profiles or typed neighbours; snapshot derives from facts, fragile for sparse files. **Closed (merge of 9b6eafc):** C is offered the ranked shortlist, deterministic winner first, each entry a `candidate` item carrying label chain, role, expected values, document types seen, sibling count and "the file sits here now"; D is offered the approved residual areas plus retrieved branches; `basis_key_for` reads the ranked winner. The validator's two walls are unchanged. | W | Medium | latent, code | A L2 | closed |
| R-18 | Reasoning-tier trap: a thinking model spends the shared budget thinking (measured on DeepSeek); `qwen3:8b` must run with thinking off | P | Low | code (comment) | K, F §28 | 0 |

### 4.2 Deterministic deciders and design conflicts

| ID | Issue | Class | Sev | Status | Sources | Phase |
|---|---|---|---|---|---|---|
| R-19 | Unique direct match and score/margin place a file with no model (`needs_model_call`, `assess`) | C | High | **open** (`00`:110, 114 vs purpose) | A W1 B3 C3, F §9.3 | 3 |
| R-20 | Rule and direct facts outrank `llm_supported` (`contradicts_stronger`); rule-settled fields removed from the question | C | High | **open** (`00`:42) | A W10 B5 C1 C2, F §9.3 | 3 |
| R-21 | `WORK_TYPE_VOCABULARY`, `SUBJECT_RULE`, `DATE_PATTERNS` and fixed template levels decide folders; `3e4a64d` closed `work_type` to library membership, which tightens R-21 while it fixes `.pdf`-as-folder | C | High | **open** (`00`:41, §5.4 vs constitution 1) | F §9.4, A C5 B5, K | 3, 5 |
| R-22 | Preservation heuristics (`_a_folder_made_for_this_keeps_it`, `_without_kind_only_moves`, `_staying_put_wins_a_tie`) choose winners on inferred intent | C | Medium | **open** | A B6 C4 | 3 |
| R-23 | One `--situation` per disk; `review_and_accept` merges every group under `--label` as `RULES`-accepted `COHERENT`; `choose_option` first-pass; disclosed but not the interaction | W/C | High | run | F C4 C5, A W2 W11 B4 C8 S3 | 5 |
| R-24 | Opaque-only folder: `NothingToDesign`, exit 1, zero per-file decisions | W | Medium | run (reproduced today) | A W9 S4 B11 | 3 |

### 4.3 Mutation, records and screens

| ID | Issue | Class | Sev | Status | Sources | Phase |
|---|---|---|---|---|---|---|
| R-25 | File edited between runs leaves a `superseded_content` ghost that is placed, frozen (three `move_plans` rows) and makes `--reject` refuse with the same path listed twice | W | High | run, strict xfail ×2 | F C15 | 1 |
| R-26 | `--send-set` writes `residual_set_decisions` and no `review_actions`; `review_gestures.py` (added by `4fc44a6` to fix this) has no caller | D | Medium | run, strict xfail | F C16 | 1 |
| R-27 | `keep-as-it-is` silently makes every file in the branch unfilable; option text does not say so | W | Medium | run, strict xfail | F C17 | 1 |
| R-28 | Records claim user acts nobody made (`shallow-by-choice` first-person reason, `user_edited_label`) | W | Medium | code | F C8, A W11 | 3 |
| R-29 | Freeze, apply, stale-file refusal and byte-identical undo **work** | — | — | run | F R3–R5, A | verified |
| R-30 | Extensionless file vanishes from the freeze block; `readers.signatures` not wired into `_detect_format` | W | Medium | `94` F22 | F | 1 |
| R-31 | Protected: 8/8 extracted before classification (order extract → classify), 1 of 8 unmarked; 0 placed on HEAD | S | High → owner flag | run | F C9, scorecards | 6 |

### 4.4 Extraction and input

| ID | Issue | Class | Sev | Status | Sources | Phase |
|---|---|---|---|---|---|---|
| R-32 | Lexical recogniser leaves 95 of 199 unclassified and 41 on the weak basis; this starves the gate, not the model | W | High | run | F, A | 1 (via D1), 2 |
| R-33 | Readers: archive markers `lambda names: ()`; DOCX links and relationships not read; `.svg`, `.raw`, `.ris`, extensionless unread; Vision language list en-US only; EXIF ruled out until the OCR trigger changes | M | Medium | code | A U5 U6 U7, F | 2 |
| R-34 | `pyproject.toml` declares no `openai`, `python-docx`, `onnxruntime`; no console script; globally installed packages mask it | M | Low | code | A U9 | 4 |
| R-35 | Budgets never exhaust (`budget_exhausted=lambda: False`); P5 and P6 ceilings unseeded; no deferral sentence | D | Medium | code | F, A | 4 |

### 4.5 Onboarding, questions and customisation (F Part II; A U1, U3, D6, U8)

| ID | Issue | Class | Sev | Status | Sources | Phase |
|---|---|---|---|---|---|---|
| R-36 | Role matcher Option 2 unbuilt: `propose=None`, so `--describe-role` prints all 23 layouts shuffled; R3, R4 unmet | M | High | run | F C18 | 5 (needs the local model) |
| R-37 | Per-branch situation kind registered, trigger never fired, reader never read | D | High | code | F, A U3 | 5 |
| R-38 | Answer change opens no draft plan version; `draft_for_answer_change` has no caller | D | Medium | run | F | 1 |
| R-39 | Role moment fires on abstentions no role can resolve | W | Low | run | F C19 | 1 |
| R-40 | `home:*` answer cannot lift the unclassified hold, so the one question asked cannot deliver | W | Medium | run | F C21 | 3 |
| R-41 | Six approved P13 gestures, label overlay (`64`), household workflow, 114 unreachable `review_surface` mechanisms | M | High | code | F, A U1 D6 | 5 |
| R-42 | Residual sets two; dispositions one; automatic filing (`66` §7–11) unbuilt, correctly last | M | Medium | code | F, A U8 | 5 |
| R-43 | Contextual answers do not exist; structural/contextual boundary untested | M | Low | code | F | 5 |
| R-44 | Tied-reading question never observed firing on any corpus tried | P | Low | unverified | F | 2 |
| R-45 | 298 of 1,665 public mechanisms unreachable from `cli.main`, 112 modules | P | — | run | F | all |

### 4.6 Measurement and process

| ID | Issue | Class | Sev | Status | Sources | Phase |
|---|---|---|---|---|---|---|
| R-46 | K's scoreboard measured "blocked" at the route and omitted the gate; its columns do not state the semantic setting, so rows are not reproducible | P | High | run | F today | now |
| R-47 | Suite green (8022) while `tests/p7/test_p7_no_safety_evidence.py` asserts R-01 and the model half is exercised only by hand-built fixtures | P | High | run | F, A, `94` F15 | now |
| R-48 | Six files at "right parent, wrong leaf" across every run (`Python 1006` → `PYTHON1006/lecture`): `work_type=lecture` exists, the level exists, the file stops one short | W | High | run (K, F today) | K | 3 |
| R-49 | Ground-truth `--enable-cloud` runs send the owner's files with the R-07 leak open; the four K runs and today's run did so | S/P | High | run | F today | now |

---

## 5. Safety flags, merged and separated from ordinary bugs

| Flag | Evidence | Treatment |
|---|---|---|
| **SF-1 Whole-document release (R-07)** | Code path confirmed; A's probe: 90,139 bytes; today's live run: 7 dossiers over 16,000 bytes, max 45,843, on the owner's files | Close before D1's cloud half ships and before any further cloud ground-truth run; keep dossier payloads local |
| **SF-2 Contextual redaction unspecified (A S2)** | Gate `classifier=lambda: None`; excerpts are not scanned for identifiers | Ratify and implement the identifier classifier with canaries |
| **SF-3 Unreviewed group recorded as accepted and coherent (R-23, A S3)** | `review_and_accept`, `decided_by=RULES`, `COHERENT` | Keep draft state until B judges or a person reviews |
| **SF-4 No terminal state for an indexed file (R-24, A S4)** | Reproduced: exit 1, zero decisions | Per-file unresolved record without a tree |
| **SF-5 Ceiling not enforced (R-07)** | `measure_tokens=None`; ledger 8 vs 4000 | Measure the final request; defer when nothing fits |
| **SF-6 Protected material extracted before classification; one unmarked (R-31)** | Both scorecards | Owner flag: `00`:185 covers prompts and moves; whether local extraction order is a breach is yours |
| **SF-7 Screen truths (R-03, R-25)** | "5 files sent" with 0 sent; "name the one you mean by its path" with identical paths | Fix with the wiring |
| **SF-8 Ghost version frozen for moving (R-25)** | `move_plans` rows for `superseded_content` | Roster filter; the stale-plan check caught it at apply time, which is the last line, not the first |

Not found broken: no run moved a file without `--apply`; no overwrite; undo verified; protected
containers marked and counted (`94` F17); protected filenames summarised by default.

---

## 6. Owner decisions

**Ruled today (recorded in `103` §28):**

- **D1 = both.** Local model first (Ollama, `qwen3:8b`, thinking off) and the cloud denial lifted
  for files with releasable evidence. **Amended by this reconciliation:** the cloud half must not
  ship until SF-1 (R-07) is closed, or the lift sends whole documents to the provider. The local
  half has no such dependency and goes first.
- **D2 = draft all four prompts**, each through the `103` §28.1 protocol: requirements traced to
  `00`, a traced draft, stress cases, a measured bakeoff of at least two candidates on a labelled
  corpus under both models, ratification with numbers attached.

**Collected from all three documents, one question each. Q-A to Q-D were RULED on the evening of 2026-09-05 (see §13); Q-E to Q-J remain open:**

| Q | Question | Sources |
|---|---|---|
| Q-A | May score/margin and unique-direct-match place a file with no model, or do they only aim the question and gate an invalid answer? (`00`:110, 114) | A C3, F §9.3, R-19 |
| Q-B | Which contradiction checks are hard evidence-consistency constraints and which are rule vetoes the model must instead be shown? (`00`:42) | A C1 C2, F §9.3, R-20 |
| Q-C | Which of `work_type`, `subject`, `term` and the fixed template levels stay closed schemas, and how does a user add a label or alias without editing Python? (`00`:41, §5.4, constitution 1) | A C5, F §9.4, K, R-21 |
| Q-D | Which preservation heuristics are hard move-scope constraints and which become evidence for the model? | A C4, R-22 |
| Q-E | Filename, short heading, cell and OCR excerpts: what may be materialised for a model, under what redaction? (`00`:186 vs `00`:124) | A C6, R-06, SF-2 |
| Q-F | What explicit action accepts a group or a tree, and may unreviewed proposals appear as drafts? (`00`:64, 66) | A C8, F, R-23 |
| Q-G | Is local extraction of protected material before classification a breach of `00`:185? | F, R-31 |
| Q-H | Should `keep-as-it-is` still file into the kept branch? Should a `home:*` answer count as a classification act? | F, R-27, R-40 |
| Q-I | `75` §6 Q1–Q7: relationship vocabulary, role guidance wording, C2 narrowing, household workflow, draft-on-edit, revoked-name retention, approval of new question kinds | F Part II |
| Q-J | Instrumentation: extend `tools.groundtruth` with payload inspection and `--require-live`, or build A's `tools/reintegration.py` beside it? Recommendation: one instrument | A, F |

A's single framing question is the union of Q-A through Q-D: **do deterministic scores and
semantic-conflict rules remain hard post-model vetoes, or become evidence and review triggers,
with only provenance, schema, privacy, frozen tree and explicit user constraints as hard gates?**
It is the one answer that unblocks Phase 3.

---

## 7. The plan, merged and re-sequenced

Merges F's phases (`103` §10, §20, §26, §28) with A's (its §5), keeping A's two safeguards that F
lacked: **observe-only mode** for any newly wired site whose output application is known lossy
(R-16), and **no cloud widening while SF-1 is open**. Every step names a runnable pass test.

### Phase 0 — one real file, by hand, twice

- **0a. A_fact through the local model** (F `103` §10 with D1's local half). Wire
  `readers.model_ollama` for A_fact under `local_model`; thinking off. Pass on the five-file
  synthetic corpus: `llm_response ≥ 1`, `llm_verdict ≥ 1`, one `llm_supported` fact, the "sent"
  line true, audit row naming the local model. Then the owner's corpus locally: record `MODEL`
  and `SORTING` lines beside §9's numbers.
- **0b. C_placement bench on one real file** (A Phase 0). After the C draft exists under D2's
  protocol and a minimal fixture tree is approved: send one real C request for
  `.groundtruth/sample/Desktop/Python 1006/lecture01_introduction.ipynb` with two selected title
  and lecture spans; pass when the model's chosen node, cited to a resolvable lecture heading, is
  the node persisted and printed, with zero moves. This is a bench proof, not a repaired CLI.

### Phase 1 — wiring, not logic (order is dependency order)

1. **SF-1 first:** represent whole local text and releasable excerpts distinctly (`extract_docx`
   span-less body must not be a releasable container value); give `Gate` a `measure_tokens`;
   seed one ceiling equal to the request's; measure the final request and defer when nothing
   fits. Pass: a 60-observation file is refused `dossier_over_budget`; no dossier over the
   ceiling on the owner's corpus. **Only then** the D1 cloud half: `no_safety_evidence_denies`
   admits cloud for a file with releasable evidence; negative twin for a file with none;
   `tests/p7/test_p7_no_safety_evidence.py` rewritten; `96` §20 amended; D1's xfail marker off.
2. **R-02, R-03:** one answer to "may this file reach a model" shared by route and gate; the
   fact-pass sentence counts responses only.
3. **R-25, R-30, R-26, R-38, R-39:** retire the two absent states (`NOT IN (superseded_content, path_no_longer_exists)`; a positive `='included'` filter would retire live `pending` and `unscanned` files, see §14.2) in roster, names, rejections
   and freeze; `signatures.py` into `_detect_format`; `review_gestures` called from the send
   path; `draft_for_answer_change` from `apply_answers`; role moment narrowed. The three strict
   xfails go green and lose their markers.
4. **R-06:** materialise the filename through the gate as a released item with audit; pass when a
   filename canary appears in released bytes for an ordinary file and never for a protected one.
5. **R-09, R-08:** derive `active_schema_for` from `role_bindings`; send the situation's
   `deferred_readings` under a key the ratified template names, or route to D2.
6. **R-04 for B, C, D, E in observe-only mode:** inject the built authorities; record dossiers,
   responses and verdicts; apply nothing until Phase 3 fixes R-15 and R-16. Pass: a C dossier
   row for `HW 3.txt`; no accepted state written by B.
7. **R-12, R-11 (wiring half):** `evidence_for` reads P9's neighbours and per-file memberships.

### Phase 2 — the input side

Real locators and every citation in `evidence_for`; per-file memberships not the global set;
entity frequencies measured; short headings, cells and policy-approved OCR snippets releasable
without whole text; identifier classifier and redaction (SF-2); C/D profile shortlists with
parent and fallback, not every node id (R-17); reader gaps R-33 with unsupported formats keeping
an explicit status; cache identity covering file version, extractor, model, prompt, schema,
policy, plan, and abstentions (R-13); `response_format` where the provider supports it (R-14).
Pass: A's canary matrix (full body, path, protected never released; heading, cell, filename
released when permitted), unchanged second run makes zero new model calls, each changed key
dimension invalidates only its results.

### Phase 3 — the output side

Fix R-16 (typed B result with label, coherence, per-member outcomes) and R-15 (dimension values
validated against evidence values, destinations against frozen ids) before leaving observe-only;
apply model-chosen node and depth; per-file terminal record when there is no tree (R-24);
distinct reason codes for no model path, model refused, model abstained (F C14); records stop
claiming user acts (R-28); implement Q-A to Q-D as ruled. Pass: A's `model-over-rule` case (the
deterministic winner differs from the model's valid choice and the model's is recorded), the six
`Python 1006` files land in `PYTHON1006/lecture` (R-48), `SORTING exact` above 0 of 41, wrong not
above the offline baseline's 0, spillover not above 5.

### Phase 4 — scale

Owner's corpus and a 5,000-file folder, local and cloud; concurrency and in-flight caps;
interrupt and resume; budgets seeded and enforced with the deferral sentence (R-35); packaging
(R-34); sandbox move round-trip with collision, changed source and interrupted copy. Pass: file
count equals the union of terminal outcomes, zero silently absent files, no budget overshoot.

### Phase 5 — customisation, in `66` §22's order

Per-branch situation (R-37) and group review before design (R-23); role matcher Option 2 on the
local model (R-36) with R4 and R7 tests; label overlay keyed on `(schema, role_ref, field_ref)`
(R-41); the six approved P13 gestures with a collector and a receiver each; residual dispositions
and sets (R-42); household workflow after `75` Q1, Q3, Q4; versioned plan diffs on answer change;
automatic filing last, as a named dry-run-first policy.

### Instruments

- `tests/integration/test_103_diagnosis_backlog.py`: seven strict xfails (R-25 ×2, R-26, R-07 ×2,
  R-01, R-27). Add strict xfails for R-06 (filename canary), R-07's size (no dossier over the
  ceiling on a synthetic long DOCX), R-24 (per-file record with no tree), R-11 (locators match
  P4), R-16 and R-15 (fault-injection on the site validators) before fixing them.
- `tools.groundtruth` stays the scoreboard; add payload inspection (largest dossier, count over
  ceiling, canary scan) and a "blocked" line that counts gate refusals by reason as well as route
  withholding, so R-46 cannot recur. Whether A's separate driver is also built is Q-J.

---

## 8. Corrections each diagnosis needs

**F (`103`):** "uncommitted semantic patch" is now `3ac0c0b`; the protected "placed" cell in §10.1
should read 0 on HEAD; C7's severity is High, not Medium, and it is live on the owner's files; the
155 estimate is measured as 149 not reaching the model (130 gate, 19 route) plus 8 with no
question; `release_id` correction already applied in §22.

**K (`103-THE-CONSTITUTION-RUN`):** "files blocked from the model 114 → 19" counts the route
only; 130 more are refused at the gate on the same code. "The model is shown the filename" is not
true of the bytes. "29 of 29 abstained, 0 wrong" did not reproduce on HEAD with the semantic
channel off (27 of 29, 5 wrong); each column should state its environment. Its naming-authority
argument for `subject` and its six-files-one-level-short target are adopted here.

**A (`asrtra`):** U5 lists the EXIF reader as unbuilt; `94` F21 ruled it must not be built until
the OCR trigger changes, so it is an owner flag, not a gap. Its W14 was reasoned and is now
measured. Everything else it reported that was checked here held.

---

## 9. The numbers, in one place

| Measurement | 4 Sep offline | HEAD offline (F today) | HEAD cloud, semantic off (F today) |
|---|---|---|---|
| Reached a model | 0 | 0 | 42 of 199 |
| Refused at the gate | — | — | 130 (40 no safety evidence, 90 unclassified) |
| Withheld at the route | — | — | 19 (protected) |
| `llm_supported` facts | 0 | 0 | 22 (school 20, subject 2) |
| Fields filled correctly / wrong | 1 / 17 of 92 | not re-read | 15 / 11 of 92 |
| Sorting exact / right parent / wrong / not placed (41) | 0 / 5 / 1 / 35 | 0 / 6 / 0 / 32 | 0 / 6 / **5** / 30 |
| "Ask the person" wrong / not placed (29) | 1 / 28 | 0 / 29 | **2** / 27 |
| Spillover into Coursework | 5 | 11 | **17** |
| Protected unmarked / extracted / placed | 6 / 8 / 1 | 1 / 8 / 0 | 1 / 8 / 0 |
| Largest dossier bytes; over 16,000 | — | — | 45,843; 7 of 42 |
| Suite | — | 8021 pass, 21 xfail | 8022 pass, 28 xfail |

The cloud row is the product as it stands: the model answers for a fifth of the corpus, mostly
with `school`, and those answers make placement worse under a single situation. That is not an
argument against the model; it is the measured cost of R-01, R-07, R-09, R-11 and R-23 together.

---

## 10. Start here next session

1. Read §4 and §6 of this document; `103` §26–§28 remain valid where not amended above.
2. Do not run another cloud ground-truth pass until Phase 1 step 1 (SF-1) is closed.
3. Phase 0a, then Phase 1 in the order given; run the backlog file after every step.
4. Put Q-A to Q-D to the owner before Phase 3; nothing in Phase 3 can be finished without them.

*Written by Claude Fable 5.1. Nothing committed; no file in `src/` or `tests/` other than the
backlog file from `103` was added.*

---

## 11. The regression, engineered: why a correct model fact becomes a wrong folder, and the fix chain

Added after the owner asked what the solution is. Everything below was measured today unless
marked hypothesis; the scratch runs are under the scratchpad's `gt-cloud/`, `gt-head/` and
`exp1/`.

### 11.1 What actually happened, file by file

| Files | Wanted | Got (cloud run) | Mechanism |
|---|---|---|---|
| `Downloads/Essay 2 Final Draft.pdf`, `(1)`, `(2)`, `ESSAY 2 .docx`, `Essay 2 refelction.pdf` | `University Writing/essay` | `Coursework/Georgetown Prep/essay` | The A_fact glossary defines `school` as *"the institution the holder attends, attended, or teaches at - the person's own school"*, and the coursework template binds `school` to the folder role `holder_institution` labelled "My school". The essays mention the school the person attended. The model answered the question exactly as asked (20 `school` facts, mostly this value); P10 built a `Georgetown Prep` level from them; five essays from a university course filed under a high school. `00`:44 names this collector by name |
| `Downloads/076f5c…pdf` and its duplicate | leave in place ("ask the person") | `Coursework/Cliffs Notes/notes` | The glossary defines `subject` as *"the course or study subject the material belongs to"*; a CliffsNotes study guide was asked coursework's `subject` under the single situation and answered with its publisher; a course node was minted from one `llm_supported` value with no anchor (`00`:63 stop rule: no group without an anchor) |
| Spillover 11 → 17 | other situations | under `Coursework/<school>/…` | Same `school` collector: résumés and application material name schools attended (`00`:44's own example) |
| Six `Python 1006` files | `PYTHON1006/lecture` | `Python 1006` (their own folder) | **Hypothesis, not yet run:** `_without_kind_only_moves` refuses to carry a file out of its folder on `work_type` alone and `_staying_put_wins_a_tie` keeps it where it is; a move into a *child* of the file's own folder is refinement, not removal, and neither rule distinguishes the two |
| Three fewer placements when each file is offered only its own memberships (`exp1`) | — | — | **Measured:** R-11's fabricated group credit is a provenance defect, not the cause of the regression. Removing it changed 32 → 35 not placed, spillover unchanged at 11, wrong unchanged at 0 |

### 11.2 The fix chain, in dependency order, each with its test

1. **Ask the right question (D2 protocol, site A, before widening coverage).** The `school`
   glossary entry for the coursework `holder_institution` role must mean *the institution that
   offers this course and term*, not any school the person attended; a school merely mentioned is
   `authored_by`-class metadata (`00`:44) and never a level. `subject` must mean *the course as the
   course names itself (code or title)*, and a study guide, textbook or publisher is not one. This
   is owner text under D2's protocol; no rule is added. **Test:** re-run the cloud ground truth;
   the five essays leave `Georgetown Prep`; `wrong` returns to 0; spillover returns to ≤ 11.
2. **Make coursework's school and term group-level facts, not per-file facts.** `00`:57 puts the
   course's school and term on the syllabus anchor and has the group carry sparse members; per-file
   A_fact should propose only what a file states about itself. Route `holder_institution` and
   `cycle_period` to site B's dossier (anchor facts) once B is wired, and stop offering them per
   file. **Test:** an essay in a course group inherits the group's school; an essay outside any
   group gets no school level.
3. **No level from an unanchored single value.** P10 may not mint a `subject` or `school` node
   from one `llm_supported` value with no direct or validated anchor and no group; such a value is
   a candidate for review (`00`:42 "may remain a possible clue for review"). This is `00`'s own
   stop rule applied at the tree, not a new threshold. **Test:** `Cliffs Notes` is not a node; the
   two PDFs stay "ask the person".
4. **Per-branch situation (R-37) before per-file coverage widens.** Every file that reaches the
   model is asked the coursework schema today; a study guide, a résumé and an application essay
   should be asked their own. Until the horizontal pass exists, the interim guard is the detector's
   per-file schema candidates in place of `signal_evaluator_for=lambda domain: True`, so a file the
   recogniser reads as `career` is not asked `subject`. **Test:** spillover ≤ offline baseline
   with the model on.
5. **Refinement is not removal (Q-D, the six files).** Distinguish "move out of the person's
   folder" from "move into a child of it" in `_without_kind_only_moves` and
   `_staying_put_wins_a_tie`. **Test:** the six `Python 1006` files land in `PYTHON1006/lecture`;
   `SORTING exact` becomes 6 of 41. Run this before ruling Q-D; it may settle it.
6. **Only then widen coverage:** SF-1 closed, D1's cloud half, filename materialised, aliases
   between file spelling and the person's folder label offered as `CandidateLabel` items so the
   model can reconcile `E1006` with `Python 1006` (constitution 1: reconciliation is a model
   decision; `CandidateLabel` is already a gate item kind with no serialisation, the same gap as
   the filename). **Test:** `subject` correct rises from 0 of 43; every step reports the numbers
   table before and after.

The order matters: steps 1 to 4 make each additional model answer safe to act on; widening
coverage first (which is what the four constitution-run commits did) multiplies the collector.

### 11.3 What this changes in the register and the plan

- R-10 moves from "cost of five causes" to a **specific, measured** cause: the `school` and
  `subject` definitions the model is handed, plus a tree that materialises unanchored single
  values. Phase 1 gains step 1 and step 3 above ahead of any coverage change.
- R-11 stays a High provenance defect but is **not** a cause of the regression (measured).
- R-48 gains a concrete hypothesis and a one-run test (step 5).
- The offline HEAD spillover is 11, not 5; the 5 was the 4 September card. §9 is corrected.

*Section added by Claude Fable 5.1 after the `exp1`, `gt-head` and `gt-cloud` runs. Nothing
committed.*


---

## 12. Pre-flight before Phase 0 ("Phase −1"): what decides whether the next fix is the last

Added after a review of this document listed twenty gaps. Each is answered below with a value, a
rule or a measurement, or named as owed. Three were already closed by §11 and are cross-referenced.

### 12.1 Root cause of R-01, from the commit itself, not the symptom

`fd68cb6` is a **six-workstream commit** whose headline is a different fix ("the child's report card
stops landing in the parent's law-school semester"). The cloud denial rode inside it. Its intent is
stated in `privacy.denial.no_safety_evidence_denies`' docstring and in `96` §19–§20: **deliberate
safety tightening**, after `96` §19 found that 41 of 78 classified files had matched no safety term
and were reachable by a model only because they had acquired a class, "turning 41 silences into 41
confident negatives". Its written escape hatch is *"LOCAL IS PERMITTED"*. **No local model existed**,
so a rule meant to redirect ordinary files to an on-device model became a total cloud block. The
commit's own measurement table is headed "no model", so the cloud effect was never measured by the
commit that caused it. **Consequence for the fix:** D1's condition ("releasable evidence present")
preserves `96` §20's intent, because a file with no evidence still cannot become a confident
negative; and the local half restores the escape hatch the rule assumed. The fix is aimed at the
cause, not the symptom.

### 12.2 D1 exit criterion and evidentiary parity with D2 (RULED, see §13.2: bakeoff runs, the lift does not wait for it)

Cloud lift ships only when all three hold: SF-1 closed; a **local-model row exists in §9** on the
pinned corpus; local reaches at least the cloud run's 15 correct fields with 0 wrong placements, or
the owner accepts a stated gap. Before that, **D1 gets the same bar D2 imposes on prompts:** a
bakeoff of `qwen3:8b` (thinking off), `qwen2.5:3b` and `deepseek-chat` on the same corpus, same
dossiers, reporting grounding, abstention and correct fields. D1 was ruled without this; it is
flagged here rather than assumed.

### 12.3 Spillover attribution: what is verified and what is not

The seven `wrong` placements are attributed per file in §11.1 (five essays to the `school`
collector, two study guides to an unanchored `subject`). The +6 spillover (11 → 17) is attributed
to the same collector **by mechanism only**; a per-file join against `labels.json` was attempted
and is inconclusive because the label schema does not expose the situation for those rows in the
column read. **Owed:** extend `tools.groundtruth` to print the spillover file list with `got`, so
the attribution is a table, not an inference.

### 12.4 Cost and latency of the cloud run

Whole run 3.2 minutes; the 42 model responses arrived between 12:47:18 and 12:48:37, **79 seconds
for 42 sequential calls, about 1.9 s each**. Dollar cost is **not observable**: the transport returns
no usage (R-14) and `FACT_CALL_COST` is a unit. At list prices the input volume implies cents, not
dollars, and that sentence is an estimate. Instrument usage before Phase 4; do not quote a number
until the provider's own count is stored.

### 12.5 Observe-only artefacts and later ratification

Every fact row, verdict and cache key already carries the **prompt fingerprint** (`82` §1). Rule:
observe-only runs use a template id prefixed `draft.`; Phase 3's pass counts only verdicts whose
fingerprint is the ratified one; on ratification, draft-fingerprint verdicts are marked superseded
and never validated against. A stale-fingerprint verdict counted as evidence is a test failure.

### 12.6 Severity rubric, stated

Blocker: no model decision is possible until fixed. High: changes where a real file lands, or a
safety boundary, or the north star's multi-role case. Medium: a wrong record, screen or count.
Low: process. C7's upgrade to High is fact-based (seven live oversized dossiers on the owner's
files), not a judgement call. R-19 to R-22 carry the severity they would have **if the corrected
purpose stands**; if the owner rules the other way they are re-labelled, not deleted.

### 12.7 Non-determinism and tolerance

The transport sets no temperature (R-14), so repeat runs can differ. Protocol: **three runs per
condition, report min, median, max; pass criteria are judged on the median with a tolerance of
±1 file on `wrong` and ±2 on spillover.** Cloud repeats wait for SF-1; local repeats do not.

### 12.8 Provisional defaults for Q-A to Q-D (SUPERSEDED: all four ruled, see §13.5 to §13.8)

Until ruled: `00` as written stands, which means scores and margin remain hard gates, rule facts
outrank model facts, and the preservation heuristics stand. Each default is recorded as
**provisional and dated**, and every place it decides an outcome writes that word into the record.
If the questions are unruled when Phase 3 starts, work proceeds under these defaults and the owner
is told which files they decided. They are the conservative direction; they are not a ruling.

### 12.9 The suite at the transition

Measured now: **9 test files assert the all-`None` model state or `p8_run_call=None`; 13 construct
a `ModelClient` by hand.** Rule before wiring: those 13 remain as validator and transport contract
tests; the 9 are rewritten to assert refusal only where `None` remains a legal deployment; the
expected-red list is written down before the wiring commit, and every red not on it is a
regression. The seven strict xfails are expected to flip and lose their markers.

### 12.10 Definition of done, with numbers (RULED, see §13.1: exact ≥ 30 of 41, not 20)

Phase 3 done, on the pinned corpus, median of three runs: **exact ≥ 20 of 41; wrong 0; spillover 0
among placed files; 29 of 29 "ask the person" abstained; 0 files reach a model without a ratified
prompt; every readable unprotected file reaches a model or carries a named reason.** Release 1 done:
the same on the held-out corpus (12.17) plus Phase 4's scale gates. The design's 99% is the
long-run target, not this release's.

### 12.11 Stop-loss, decided now

Any commit whose measured `wrong` or spillover exceeds the previous recorded row is **reverted
before the next commit lands**. If Phase 3 ends worse than HEAD offline on either number, the
shipped default returns to offline and Phase 3 reopens. Every commit message carries the before and
after row.

### 12.12 Independent verification

Numbers come only from `tools.groundtruth`; nobody types a number. A "fixed" claim requires a fresh
run by a different session or a different day, diffed against this document's §9. Every column
states its environment: model, prompt fingerprint, semantic channel, situation. K's columns did not,
which is why they could not be reproduced.

### 12.13 The corpus is now pinned

The corpus and labels are **not in git** (0 tracked files under `.groundtruth/`) and had no
manifest, so drift was undetectable. Written today: `.groundtruth/MANIFEST.sha256`, 216 lines
(every corpus file plus `labels.json`), manifest digest **`a3a8f4ef4a04e5d4`**. Every future scorecard
must print the manifest digest it ran against; a mismatch is a different corpus.

### 12.14 Attribution when fixes interact

One seam per commit with its numbers (constitution 5), then a combined run at the end of each
phase; if the combined row differs from the last sequential row, bisect before proceeding. R-09 and
R-23 interact and are landed in the order §11.2 gives.

### 12.15 Local parity in the numbers table

The first deliverable of Phase 0a is a **local-only row in §9**. Until it exists, "final" has no
meaning for the path D1 ships first.

### 12.16 Scope boundary

**Release 1 is the engine: Phases 0 to 4.** Onboarding, the role matcher, the canvas, the six
gestures, the household workflow and automatic filing are **Release 2 (Phase 5)** and are outside
the meaning of "fixed" in this document.

### 12.17 A held-out corpus

Every diagnosis measured the same 199 files. Before Release 1 is called done, build a small
second corpus from `68-PERSONA-RERUN.md`'s four personas (student, litigant, householder, parent),
labelled by the owner, **never tuned against**, and run it once at the end of Phase 3. A fix that
passes only the tuned corpus is overfit.

*Section added by Claude Fable 5.1. The manifest is the only new file, and it stays out of git with the corpus it pins.*


---

## 13. Rulings of 2026-09-05, evening: the owner set the bars

Put to the owner by Claude Fable 5.1 in two rounds of four questions each, after §12 was committed
as `5c321a8`. Each ruling is final unless the owner reopens it. The provisional defaults in §12.8
are no longer needed for Q-A to Q-D. The same rulings are recorded as dated amendments at the end
of `00-database-agent-product-design.md`, so the design stays the source of truth and no session
has to choose between the two documents.

| # | Question | Ruling | What changes in the plan |
|---|---|---|---|
| 13.1 | Definition of done (§12.10) | **Stricter.** On the pinned corpus (manifest digest `a3a8f4ef4a04e5d4`), median of three runs: **exact ≥ 30 of 41; wrong 0; spillover 0 among placed files; 29 of 29 "ask the person" abstained; 0 files reach a model without a ratified prompt; every readable unprotected file reaches a model or carries a named reason.** | §12.10's "20" is replaced. Phase 3 cannot close at 20. Release 1 needs the same bar on the held-out corpus (§12.17) plus Phase 4's scale gates. |
| 13.2 | D1 exit criterion (§12.2) | **Bakeoff for the record; the cloud lift does not wait for it.** The cloud denial for basis `detector_no_safety_evidence` is lifted the moment SF-1 (R-07, whole-document release) is closed. | §12.2's third condition (a local row before the lift) is dropped. The bakeoff (`qwen3:8b` thinking off, `qwen2.5:3b`, `deepseek-chat`; same corpus, same dossiers; grounding, abstention, correct fields) still runs in Phase 0a and its row goes into §9. |
| 13.3 | Scope (§12.16) | **Release 1 is the engine, Phases 0 to 4.** Onboarding, the role matcher, the canvas, the six gestures, the household workflow and automatic filing are Release 2. | The gesture and onboarding halves of C15 to C21 and the §4.5 entries stay open and do not block "done". R-25, the `superseded_content` filter that is C15's engine half, is mutation safety and stays in Release 1 (Phase 1 step 3). Every open xfail stays strict until its fix lands. |
| 13.4 | Process (§12.7, §12.11, §12.12, §12.17) | **All four accepted as written.** | Three runs per condition, judged on the median with ±1 on `wrong` and ±2 on spillover; a commit that raises either is reverted before the next lands; a "fixed" claim needs a fresh session's run diffed against §9; a held-out persona corpus labelled by the owner, run once at the end of Phase 3, never tuned against. |
| 13.5 | Q-A, placement bypass (`00`:110, 114) | **Model decides, rules validate.** Every placement goes through the model. Scores rank and shortlist candidates; a rule may reject only a structurally invalid answer (node not in the frozen tree, cited fact not in evidence). A unique direct match is the top-ranked candidate the model is shown, not a bypass. Precondition: the §11 fix chain, because the model as wired today makes placement worse. Q-A governs whenever a model is configured; with no model configured the deterministic path remains the fallback, which is what §12.11's "returns to offline" means. | R-19 closes by implementation: P11's two-condition threshold and `needs_model_call` stop skipping site C for placeable files. Budget consequence: up to one C call per placeable file per run (42 calls took 79 s on 2026-09-05; 199 would take about 6 minutes on the cloud tier, longer locally). |
| 13.6 | Q-B, contradiction checks (`00`:42) | **Grounding hard, the rest shown.** A hard veto only when a model fact is not grounded in the file's own evidence (quote or metadata) or falls outside the derived schema. Every other check, including rule-fact precedence over model facts, is shown to the model as a flag with its evidence, and the model reconciles. | R-20. The `FactResolver` stage order (direct, rule, llm) stays as the order of collection, not of authority; a rule fact that disagrees with a grounded model fact becomes a flag in the next call's dossier, not a silent override. |
| 13.7 | Q-C, vocabularies (`00`:41-43, constitution 1) | **Model names, user confirms.** `work_type`, `subject`, `term` and user labels are model decisions grounded in evidence. A value the library has not seen is proposed once; the user confirms or renames it; it joins that user's vocabulary in the database. No alias tables or equivalence maps in code. Template levels stay fixed as structure. | R-21. Reverses the direction of `3e4a64d` for unseen values: a closed-vocabulary rejection becomes a "confirm this new value" question instead of a dropped fact. The ratified library remains the default vocabulary the model is shown first. |
| 13.8 | Q-D, preservation heuristics (`00`:22) | **Split: refinement allowed, removal constrained.** Moving a file deeper inside its own branch is the model's call. Moving it out of the person's existing arrangement stays a constraint surfaced to the user. | R-22. `_without_kind_only_moves` and `_staying_put_wins_a_tie` distinguish refinement from removal (§11 fix 5). The six `Python 1006` files placed one level short are the pass case. |

**What is still the owner's after these rulings, and when.** Ratifying each prompt at the end of its
bakeoff, with the numbers attached (D2 protocol, `103` §28.1); labelling the held-out corpus before
the end of Phase 3; accepting a stated gap in the bakeoff row if one appears. Nothing else blocks
Phase 0.

**13.9 The finish line (ruled 2026-09-06, after Wave 1 was dispatched).** Release 1 (§13.3) is sequencing, not the finish line. The work is finished only when every register entry in §4 (R-01 to R-49, Release 2 included) is closed with its test, and the product runs end to end and behaves as `00` describes. Whether it does is assessed the original two ways, both required: **user-based** (what a real person in each of the personas would want at every step, the north-star instruction) and **product-based** (line-by-line conformance to `00` and its amendments). The lead may adapt the remaining plan to what each wave actually delivered, but may not narrow this finish line.

**Build authorisation, same evening.** The owner authorised the build to start once ready, with
dynamic workflows and multiple agents, on the condition that every dispatched agent, and every
agent those agents dispatch, runs on Opus 5. The standing constraints do not move: protected
containers are marked and counted, never opened; the corpus never enters git; no cloud
ground-truth pass until SF-1 is closed; prompt text and vocabulary members are ratified by the
owner, never by an agent.

*Section added by Claude Fable 5.1.*


---

## 14. Wave 1 outcomes, corrections and new register entries (2026-09-06)

Written by the lead as the branches merged. Every number here came from a run; every correction names
the agent's measurement that forced it.

### 14.1 What merged, with its row

| Merge | Branch | Suite (passed / skipped / xfailed) | Offline coursework row (exact / rpwl / wrong / not placed; abstained; spillover) |
|---|---|---|---|
| baseline `995c94f` | — | 8022 / 19 / 28 | 0 / 6 / 0 / 32; 29 of 29; 11 |
| `178a951` sf1-gate | SF-1 closed, one measured ceiling, payload instrument, D1 lift narrowed | 8053 / 19 / 24 | 0 / 6 / 0 / 32; 29 of 29; 11 (identical, as an offline run must be for a gate-only change) |
| engine-fixes, local-a-fact | in verification at the time of writing; rows appended below as they land | | |

Instrument on the owner's 199 files, offline (`tools.groundtruth.payload`): whole documents released
**20 → 0**, largest dossier built **41,247 → 1,073 bytes**, built over the 4,000 ceiling **29 → 0** once
measured, gate admits **82** files (was 42), protected **19 of 19** still refused, `no_safety_evidence`
refusals **40 → 0** after the D1 lift. `f571d36` makes the documented pytest flag the default.

### 14.2 Corrections to this document, from measurement

- **§7 Phase 1 step 3 (R-25).** The fix is a negative filter, `NOT IN (superseded_content,
  path_no_longer_exists)`, not `scan_state='included'`: `pending` and `unscanned` are present files.
  Sites: `placement.groups.accepted_group_as_of`, `production.corpus_roster`, `cli.file_names`,
  `cli.apply_rejections`; `_move_frozen_files` reads through `file_names` and needed no change.
- **§11.1 row 6 (the six `Python 1006` files).** Does not reproduce offline. At `995c94f` and after the
  step 5 fix alike, the five lecture notebooks leave `Python 1006` for the `Coursework` root on a direct
  fact match (`auto_eligible`, margin 0.43); they do not stay put. Step 5 (refinement is not removal) is
  correct in code and inert on this corpus for a structural reason: every `tree_nodes` row has
  `parent_node_id = None`, so there is no child to refine into; no level divides because every placed
  file names the same term, subject and work type. The acceptance case needs a tree with a child, which
  needs the model (R-48 stays open; step 5 is pinned by 13 unit tests instead).
- **Labels.** Five files want `PYTHON1006/lecture`; the sixth, `Lecture three exercise .py`, wants
  `PYTHON1006/exercise`.
- **§11.2 step 4, eliminated by measurement.** `signal_evaluator_for` is checked callable and never
  called (P9); the live per-file gate is `ActivationSignal.activates` inside `cli.fact_call_authorities`.
  The lead's route (persist the detector's recognition as a file fact and key the gate on it) was measured
  before it was built: the detector answers *what a file is made of*, not *which situation it is part
  of*. Over the owner's `sample/Desktop`: a résumé is an `Abstention`, `ambiguous`, tied
  `career`/`college_applications`, so the guard never fires on the file it was written for; four of the
  five lecture notebooks are `Recognition(code)`, the only files that corpus places correctly, and the
  guard would strip `school`, `term`, `subject`, `instructor`, `work_type` from them and add
  `repository`. The guard fires six times on that corpus and helps nobody. Pinned as five strict tests in
  `tests/integration/test_step4_recognition_as_a_gate.py` over the real `Detector` and the real
  `active_field_allowlist`. **R-37 (per-branch situation, the model deciding from valid options) carries
  step 4**; no interim guard. The 57th field the fact route needed is the withheld `sensitivity_status`
  twin (NEEDS-JOSEPH C5) and is not added.
- **An inherited commit was red.** `72e3acf` committed a test that raised inside its own helper and never
  reached its assertion; its message claimed "tests: one added". Caught by the finisher's full-suite run.
  Rule restated: an agent's test claims are verified by the merge suite, never carried on trust.

### 14.3 New register entries

| # | Finding | Kind | Severity | Basis | Phase |
|---|---|---|---|---|---|
| R-50 | **No per-extraction time ceiling.** The extraction pool recovers from a worker that dies, not from one that never returns. Measured: three of seventeen scoreboard situations hung at 0% CPU; the sampled worker's main thread is in `-[VNRecognizeTextRequest …]` (Vision, via PyObjC, the OCR reader) → `-[CIContext render:toCVPixelBuffer:…]` → `_dispatch_sync_f_slow` / `__DISPATCH_WAIT_FOR_QUEUE__`, a deadlock inside Apple's frameworks; six workers idle in `sem_wait`; the parent waits in `result()`. `00`:257 says one file may not consume the run. | W | **Blocker** for measurement | run, sampled | 1 (assigned) |
| R-51 | **Token measure is a character upper bound.** `model_facts.dossier_tokens` counts characters as tokens (safe direction, about 4× tighter than the design's intent for English, honest for CJK). Replace with a provider-calibrated count (the cloud transport's usage field; Ollama's `prompt_eval_count`) before Phase 2 widens excerpts, or the ceiling throttles coverage. | W | Medium | code | 2 |
| R-52 | **Local latency levers.** Ollama reloads the model when `num_ctx` changes (283 s measured), so one window per run; a concurrent client with a different window forces reloads (62–87 s per call measured while the bench ran). A stable prompt PREFIX (template, folder levels, vocabulary first; the file's dossier last) is what lets the KV cache carry across files. Real smoke: 4 calls, 4,181–4,503 prompt tokens, `think: false`, `format: json`, no truncation, num_ctx 32,768. | P | Medium | run | 0a / D2 packet |
| R-53 | **Site C asserts its dossier fits.** `model_placement.py:283` hardcodes `unreduced_fits=True`, the twin of R-07 at the placement site; must be measured the way `2981c79` measures A. | W | High (latent until C is wired) | code | 1 (W2-D) |
| R-54 | **The local model repeats the `school` collector.** qwen3:8b answered `school = "PHYS 1401"` on the lecture and the syllabus: grounded, validated, and a course code. Same defect as §11.1's first row, different model; the D2 glossary revision is the fix and the packet's A-site bakeoff measures it. | M | High | run | D2 |

| R-55 | **The residual sensitivity check has no implementation.** `SENSITIVITY_RESTRICTION_IGNORED` rests on a `sensitivity_policy` dependency nothing supplies (`cli.py:4126` passes `None`; the bench stubs it true), so a protected record filed into an approved area is caught by nobody. Measured in the D2 bakeoff: both local D texts filed the redacted statement (D13) into Receipts and it was accepted. Packet G17. | S | **High** (safety flag SF-9) | run | 1 (wiring) |
| R-56 | **The local model does not abstain.** `qwen3:8b` (thinking off) produced zero abstentions on the six should-abstain cases at C and D under every wording tried, and the validator accepted two of its wrong placements (a generic hub on `columbia.edu`, OCR noise `2O26`). The cloud model abstained 4 of 4 at C and 1 of 2 at D. D1's local half is fit for A_fact and unfit as a placement decider until an abstention mechanism exists that does not depend on the model volunteering one (a structural "none of these" option scored by the validator, or the deterministic shortlist refusing an ungrounded choice). This is the §12.2 parity evidence the owner asked to have measured. | M | High | run (packet §10) | 3 |
| R-57 | **Site E is unratifiable as shaped.** 15 of 24 E responses were unparseable because the payload ends on a populated array (G13); a v2 with the payload reordered is in progress on the prompts branch. | M | Medium | run | D2 |

### 14.5 The first model-on row after Wave 1 (three runs; §12.7 satisfied)

**Local model, 7 Sep (qwen3:8b, `d409f58`, resumed after R-108's crash at `b778915`; `--shadow` scored at `88dcb62`).** One run, 2 h 20 min, every model call local; 0 cloud calls. Applied row **0 / 6 / 0 / 0 / 35**, wrong 0, 29 of 29 abstained, spillover 6 (offline 10). Shadow row identical: **0 labelled files carry a site-C verdict; site C was never asked** (R-118: under `local_model` mode P11 marks every file `LOCAL_ONLY` and assembles no dossier; 176 of 199 decisions `privacy_blocked`). A_fact 394 verdicts, 60 accepted (`subject` 50, `term` 9, `work_type` 1), 328 rejected: `VALUE_NOT_NORMALIZABLE` 240 (`term` 114, `work_type` 82, `subject` 44), `VALUE_NOT_IN_CITED_TEXT` 51, `SCHEMA_INVALID` 33 (all `citation_malformed`), 1 call failure recorded and the run continued (R-85). B_group: 1 dossier, 6 answers, 5 refused at the gate (`always_local_item` 4, `whole_document_requested` 1). One run, not three (R-96: ~100 s per call); no held-out corpus.

Runs 2 and 3 (head `aaeb666`, code identical for placement) agree with run 1 on every sorting number: exact 0, right parent wrong leaf 6, top folder only 0, wrong 0, not placed 35, abstained 29 of 29, spillover 10. Only the verdict counts vary (257 / 272 / 253), which is the model's non-determinism at the fact level not reaching placement. The median row is therefore the row below.


Cloud, `academic.coursework`, HEAD `17d05fa` (SF-1 closed, D1 lift, engine fixes, drafts unwired), semantic
channel off, prompt `a_fact.unratified.folder-levels.2026-09-04`, corpus manifest `a3a8f4ef4a04e5d4`.

| Measurement | HEAD cloud 5 Sep (the regression row) | `17d05fa` offline | `17d05fa` cloud |
|---|---|---|---|
| Reached a model | 42 of 199 | 0 | **83** |
| Refused at the gate | 130 (40 no safety evidence, 90 unclassified) | — | 90 (unclassified only) |
| Sorting exact / right parent / top folder only / wrong / not placed (41) | 0 / 6 / — / **5** / 30 | 0 / 6 / 3 / 0 / 32 | 0 / 6 / 0 / **0** / 35 |
| "Ask the person" abstained (29) | 27 (2 placed wrong) | 29 | **29** |
| Spillover (coursework run) | 17 | 10 | **10** |

Read plainly: the regression is gone (wrong 5 → 0, spillover 17 → 10, abstention restored) with twice
the coverage, and the model is not yet helping either: exact stays 0, and three files placed at their top
folder offline are not placed with the model on: the three `Essay 2 Final Draft` PDFs, §11.1's first row. Offline they sat at the Coursework root ("top folder only"); with the model on, its `school` fact now produces an abstention instead of a `Georgetown Prep` level, because §11.2 step 3 (no level from an unanchored single value) is merged. Honest, and the expected state before site C is wired and the A glossary is ratified; it is the row Phase 3 starts from.

| R-58 (merged) | **Dossier emitted frame first.** Sorted keys interleaved situation-constant material with per-file material: the shared byte run ended 205 into an 8,999-byte body. Frame first: 48.3% → 88.9–93.0% of the model-visible prompt shared; provider `prompt_cache_hit_tokens` 39% → 90%. One consequence outside the prefix: anything locating the dossier by its first key breaks (three tests did; fixed by splitting on the template's own last sentence). | W | closed | run | 1 |
| R-59 | **The P9 semantic channel never ran.** `cli._embedding_runtime.text_for` measured `len()` of the `(text, keys)` tuple `recognition.semantic.evidence_text` returns, so every file read as 2 characters and no vector was ever stored; dead on arrival (`d75dcb5` made the tuple before `3ac0c0b`). Every semantic-on row ever recorded measured recognition only. Corrects R-12's mechanism. | W | High | run (199 of 199) | 1 (w2b) |
| R-60 | **The eligible set was cut before ranking.** `versions_for` ignored its `seed` and cut the first ten files by hash order; `_bounded_versions` cut by sort order before any similarity was computed, so every seed was compared against the same nine files. Inverts `00`:257. Fixed on w2b: rank, then cap. | W | High | run | 1 (w2b) |
| R-61 | **`bridge_entity_ref` is NULL on every `shared-validated-fact` edge** (204 of 204), so §6.5's hub test had nothing to act on. Ruled: record the bridge on that channel, exempt the seed's own field=value (a group's own basis is never its hub), and measure the ceiling (9 is unmeasured; `photograph` appears in 11 files). | W | Medium | run | 1 (w2b) |
| R-62 | **The budget's unit is calls, not tokens.** `FACT_CALL_COST = 1`, `FACT_CALLS_PER_SCAN_CEILING = 200`; observed tokens are now recorded beside `reserved_cost` per call. A token-denominated ceiling is an owner question (Q-L): measured proposal about 5,000 prompt tokens per A_fact call, about 1,000,000 per 200-call scan; a wrong number throttles coverage (`00`:259). | P | owner | run | Q-L |
| R-63 | **R-13's own wording was wrong three ways** (measured): the reuse key cannot be `dossier_id` (it exists only after the gate mints a capability and the budget slot is spent), `policy_version` cannot be a dimension (`_persist` mints `policy-{uuid4}` every run), and the asked field set cannot be a dimension (run two's open set is run one's declined set). Built: identity computed before the gate from the inputs that determine the dossier; policy content hashed; the open set compared against the prior's abstentions. | W | closed | run | 2 |
| R-64 | **Local usage has no cache count.** Ollama's `/api/chat` reports `prompt_eval_count` and `eval_count` but no cache-hit count; the two cache columns are null on the local path by design, and the effect shows as a lower prompt count. Two structurally identical `Usage` records exist because `model_ollama` may import nothing from `src/`; a test binds both to `store.USAGE_COLUMNS`. | P | note | code | 2 |

**Owner questions added tonight.** Q-K: the two event names `model_call_reused` and `model_call_usage` (registration is a spec-level act); rows `llm_call_reuse` and `llm_call_usage` carry the provenance until ruled. Q-L: the token-denominated budget ceiling (R-62).

| R-65 | **The semantic channel is 70% cross-situation at threshold 0.30** (754 of 1,078 pairs on the owner's corpus) before any floor moves; every retrieval floor below 100 that admits a sparse file also admits a cross-situation neighbour. Floor stays 100 by sweep; the threshold is the owner's lever. §4.3's hub test has no live implementation on this corpus: the shared-fact channel can never raise a hub at any ceiling (a neighbourhood retrieved on the seed's fact contains that fact alone) and P11's corpus-wide count cannot fire at 200 when the commonest of 32 facts is stated by 11 files. Ceiling stays 9 by sweep. | P | owner | run (sweeps) | Q-N |
| R-66 (merged) | **The database locked under concurrent runs.** `BEGIN` was deferred so the lock was taken mid-body, and the busy timeout was Python's default. Now `BEGIN IMMEDIATE` at the boundary, a chosen 30 s timeout, bounded retry with the wait recorded. | W | closed | run | 1 |
| R-67 (merged) | **A re-derived edge joined instead of superseding.** After R-61 a re-run added newly-addressed shared-fact edges beside the old ones. Now superseded on (from, to, edge_type), never deleted, with the reason; `edges_for_group(include_superseded=False)`. | W | closed | run | 1 |
| R-68 (merged) | **An interrupted scan stranded what it had not reached.** Killed at its 83rd write over 200 files: 158 indexed without extraction and counted `reused` by every later run, for ever, every count consistent and wrong. Fixed by a third clause asking whether the content has a run by the extractor it is owed. | W | **Blocker** (was silent) | run | 4 (closed) |
| R-69 (merged) | **Packaging declared 4 of the 12 third-party names the readers import**; `python-docx`, `onnxruntime`, `tokenizers`, `numpy`, `pyobjc-framework-Cocoa`, `anthropic`, `openai` were missing. Now derived by a test from the readers' own imports; cloud SDKs in a separate `models` extra so an offline install pulls no client; every `except ImportError` in the readers must raise. | M | closed | run | 4 |
| R-70 | **R-32 measured.** 109 of 199 unclassified in the stored run (90 is the classified count): 60 matched no authored term (`no_evidence` is a misnomer; all 199 carry observations), 32 no corroboration, 20 ambiguous. The semantic classifier is live and is a PRECONDITION for the situation site: 60 files have no lexical candidate, so `--semantic-model` is required for the main bucket. Site built to its three walls in `src/model_situation.py`; the walls are owner questions (Q-M): seventh `CALL_SITES` member, a `local_model` classification basis, and what the cloud rung makes of "a model on this device read it and said ordinary" versus "no safety word matched"; plus the unit question (23 schemas versus 208 situations) which decides how many questions a person answers. | D | owner | run | Q-M |

| R-71 | **Site B's local calls record no `llm_call_usage` row.** P9's authority bundle deliberately carries no usage sink (`NOT_P9_AUTHORITIES`), so a B response has no usage row while A's rows match A's responses. Surfaced only when the observe-mode branch met the usage branch. Pinned as a strict xfail; Wave 3 passes the recorder at the group seam deliberately. | W | Medium **Closed (0a0e272):** the recorder is bound at the composition seam (`observe_group_authorities` partials `observed_run_call` with A's mailbox), the bundle unchanged; the strict xfail retired. | run | closed |
| R-72 | **Grouping and tree design are the wall at scale.** Synthetic 5,000 files: extraction completes clean and fully accounted (5,000 indexed = 5,000 terminal outcomes, 0 absent, 500 metadata-only, 0 capped, 171 MB), but at 35 minutes the run held 242 groups, 72 tree nodes and zero placements and was still moving. Invisible at 199 files; the whole run at 5,000. **Closed for the wall:** `retrieve_neighbors` read facts once per candidate (1.9 M of 2.3 M `facts_for_file` calls) and `supersede.chain` full-scanned `file_facts` because `record_id` is an unindexed projection; with an index and per-seed bulk reads P8-P11 at 1,000 files goes 107.8 s -> 29.3 s and 5,000 files completes in 14.8 min with 5,000 placements, plan rows byte-identical at 199 and 1,000. What remains is R-79. | P | High | run | closed |
| R-73 | **Per-file extraction duration is unobservable.** Every extraction run records `started_at == finished_at` (one stamp on the calling thread), so the elapsed time the design wants observable (`00`:245-259) exists only outside the process. **Closed (8b7cae0, merge of 626a541):** `finished_at` is taken when the result lands in `_consume`, from the caller's injected clock; 1,000 files median 22 ms, p95 35 ms, max 0.93 s. | W | Medium | run | closed |
| R-74 | **A protected file with a unique direct match abstains under model-decides where offline it places.** R-19 routes every placeable file to site C; the privacy gate refuses the dossier and the verdict is PRIVACY_BLOCKED. §13.5's Q-A clause says offline remains the fallback, so a gate-blocked file takes the deterministic placement rather than losing its home. Surfaced by units 1-2 (bf2b5f1). | W | High **Closed (0a0e272):** at both refusal points the question is "would offline have placed this?" (`needs_model_call(model_decides=False)`); yes takes the offline placement with the rules as actor and §8.4 named, no still abstains PRIVACY_BLOCKED. | code | closed |
| R-75 | **P11 never reads `verdict.requires_review`.** A model confirming the top node on a unique direct match keeps P11's exact-fact-match and auto-eligible even when P8 answered accept_context_supported. Reachable only since R-19. Rules validate the model's answer; they do not overwrite its review class. | W | Medium **Closed (0a0e272):** `requires_review` is OR'd from the verdict, never assigned, so the rules' own reasons survive. | code | closed |
| R-76 | **The two-condition codes at site C stay until the owner names what `support` and `next_support` mean (G6).** Under the drafts' whole-number citation counts, BELOW_SUPPORT_THRESHOLD and INSUFFICIENT_MARGIN fire only on zero support or a declared tie, so they transcribe "not decided" rather than veto a score. Removing them deletes two SITE_C_REASON_CODES entries. | C | Low | **open** (owner) | -- |
| R-77 | **§13.6's schema half has no channel at site C.** `folder_levels` is empty at C by design and `allowed_vocabulary` is node ids, so nothing tells the validator which levels exist; `dimension` is constrained only as a non-empty string. Grounding (R-15) is done; the schema half and the grounding of context-supported levels wait on R-17's node profiles, and until then one support word is a knowing fail-open. | W | Medium | code | 3 (unit 3, R-17) |
| R-78 | **The group graph was cut in a different order every run.** Observed as 511/510/510 edges over three from-empty runs of the owner's 199 files, first blamed on OCR (626a541's message; wrong). `grouping/graph._rank` sorted by `_edge_id`, a hash over two `uuid4` file ids minted at first index, so `max_graph_nodes = 10` kept a fresh draw of files each run; `retrieve_neighbors` and `_group_for` tied and sorted by uuid too. Extraction was reproducible throughout: `extraction_runs`, `evidence`, `text_units`, `file_facts`, `unresolved`, `memberships` byte-identical across the three runs; Vision OCR 0 unstable answers over 24 calls on clean and degraded images. **Closed (merge of 0c49042):** the cut ranks by anchor class then retrieval order, retrieval ties by `(content_hash, current_path)`; identical in every derived table across two runs, three hash seeds, serial vs seven workers, 34/63/263-file corpora; no plan row changed. | W | High | run | closed |
| R-79 | **`_divides_the_corpus` is the largest remaining P10 cost.** 588 calls make 175,892 `preferred_value_for` calls, O(folders x fields x N); 7.8 s of 34.5 s profiled at 1,000 files after R-72's fixes, and the term that grows fastest at 5,000 (P8-P11 804 s). Fix must stay byte-identical on plan rows. | P | Medium **Closed (merge of 1a0a8cb):** `preferred_of_slot` is the one decision, `read_surface.preferred_in_field` asks it of the corpus in two statements, `settled_values_by_directory` reads each field once for all folders. 1,000 files: 337,782 -> 2,205 statements, 3.87 s -> 0.05 s; statement growth 8.0x -> 2.6x. 26/26 tables byte-identical. | run | closed |
| R-80 | **A second, differing model answer about a group leaves the row as it stands.** Superseding needs a new `group_id` that no membership or `group_acceptance` row names; the seam refuses rather than overwrites. Mint a superseding group and carry the memberships, as `cli.review_and_accept` does for the person's label, or hold the first answer: owner's call. | C | Medium | **open** (owner) | -- |
| R-81 | **D is offered only the approved residual areas plus the retrieved branches.** `approved_target_ids` still carries every legal node, so what D may reach is unchanged; what it is shown is narrowed so every id the draft promises to describe is described. Whether D should instead see every legal node with a profile each (hundreds of lines on a real plan) is the owner's. | C | Low | **open** (owner) | -- |
| R-82 | **The person's own folder labels and expected values now cross the gate into model-visible bytes.** `candidate` items are the first such crossing; before, only library `RoleBinding` labels and glossary meanings did, though released file excerpts already crossed. `00`:105/110 require it and G3 says ratifying C ratifies the builder change; a change in kind, stated for the owner's explicit sign-off before any cloud site is ratified. | C | High | **open** (owner) | -- |
| R-83 | **A bare `P8Verdict` reaching `apply_p8_verdict` keeps the pre-R-16 blanket reading.** The live root always wraps a response, and that is pinned, but the coarse path still exists for a caller holding a verdict and no body. On the model path a non-verdict reaching the seam raises with the group row withheld, so a caller bug loses the row rather than writing a wrong one. | W | Low | code | later |
| R-84 | **An unrecognised `group_category` is dropped with no proposal record.** The `SCHEMA_IDS` gate keeps the label and drops the category, because P10 selects an applicability row by it; §13.7 says a value the library has not seen is proposed once and the person confirms, and no proposal row exists. | W | Medium **Closed (0a0e272):** `group_category_proposals`, P9's eighth table, `proposed_value` primary key; written only under a coherent verdict, so today (B unratified) no row is written; who confirms it is R-103. | code | closed |
| R-85 | **A refusal raised inside a model-site call ends the run.** Fresh-session walkthrough, local model on a 52-file synthetic corpus: the plain run died with a traceback after 37 minutes (`UnresolvableSpan`, a shared anchor fact citing another file's observation) and again after 48 (`MalformedRequest`, a dossier with no items). Both causes fixed in c6b97a4; the shape is not: a gate or harness refusal must be recorded by reason and the file must fall back to the offline path (`104` §7 step 6, R-46), and only a programming error may reach `main`. | W | High (blocker) **Closed (merge of d107d05):** `CallRefused` is an outcome; `run_call` catches the harness's refusal classes at the gate and around issue-and-validate, records a `call_refused` event with the class name and never the message, and each site falls through -- A to the next file, B to `model_call_refused:<class>`, C to the deterministic placement, D to `no_supported_destination`; `BaseException` still surfaces. The report prints "N refused: a part of this product declined to answer and the run went on without it". Left: a raise before `issue` still settles the reservation (over-charge, safe direction). | code | closed |
| R-86 | **`--answer home:.=Coursework` re-homed all 33 files, and freeze then froze nothing.** The question said "this decides where those 2 files are filed"; `cli.already_answered` applies the answer to the whole folder by design. The question's scope and the answer's scope must be the same sentence; which one is right is the owner's. | C | High | **open** (owner) | -- |
| R-87 | **A one-file folder the person made became a destination profile that beat the proposed node.** `PHYS1401 Problem Set 1.pdf` was ready to file into `old stuff` because that folder's single file made it "expect subject = PHYS1401, work_type = problem set". Q-D's refinement/removal split needs a floor on what an adopted folder may claim from one file. | C | High | **open** (owner, Q-D) | -- |
| R-88 | **One `--situation` per run is spillover by construction.** Two cover letters were frozen and applied under `Coursework/Summer2026/cover letter`; the report says so honestly. R-37 (per-branch situation, model deciding from valid options) is the plan's own fix and the walkthrough's single most-needed change. | C | High | design (R-37) | 3+ |
| R-89 | **Receipts, an order confirmation, a boarding pass and a screenshot are "protected material (§8.4)"** on a corpus where `00`:120 names Receipts and Confirmations as their destination. The always-local kinds and the protected kinds are being read as one list. | C | Medium | **open** (owner) | -- |
| R-90 | **The reading question ignores the typed situation.** "What kind of material is ECON2010? clinical_practice, construction_property, retail_hospitality ..." after `--situation academic.coursework`; answering `academic` three times moved ready from 7 to 10. Folds into R-37 with R-70's unclassified breakdown. | W | Medium **Closed (merge of d68276f):** `situation_schema_family` (the situation's own schema, schemas sharing its template, schemas of the same dotted name) orders the reading question; 194 of 208 situations reduce to one domain, 7 to two, 7 to three; the rest are one `--explain` away and every option is still accepted. | code (R-37) | closed |
| R-91 | **One course split into `CS3134` and `W3134`** (the syllabus says "COMS W3134"); Q-C says the model names and the user confirms, and the confirmation gesture does not exist yet. | C | Medium | code (Q-C) | later |
| R-92 | **"Would go into lecture, once you say what these are" with no `--answer` that reaches those files.** Five files told to wait on a gesture the product does not offer (R-32, R-70). | W | Medium **Closed (merge of d68276f):** a "once you say" group is split by the question that reaches it and prints that question's `--answer` lines; a group no question, `--send-set` or `--describe-role` reaches says so and points at `--list-residuals`; a walk test asserts every `--answer` a group prints is offered in the same report. Load-bearing on R-86: if the folder answer is ruled to cover the folder, `home:<folder>` must join what reaches every file in it. | code | closed |
| R-93 | **`RESIDUAL_REVIEW_BATCH = CEILING_VALUE` (8) is the placeholder a person sees** as "Not yet placed (1 of 4) ... (4 of 4)" and "3 review sets of it" on 52 files; nobody chose the number. | C | Medium | **open** (owner) | -- |
| R-94 | **Screen defects from the walkthrough, fixed or being fixed:** a locked archive marked in the record but generic on screen (R-D); two protected vocabularies on one screen (R-J); duplicates never called duplicates (R-K); CoreGraphics stderr noise before every report (R-L); section numbers on the person's screen (R-M); a cross-folder proposal shown without `--may-cross-folders` (R-N). | W | Low-Medium **Closed (merge of d107d05):** R-D counted on screen (`Password-protected containers: 1, never opened`, members listed not read); R-J one heading `Protected: N marked and counted`; R-K duplicate families named with "keeping one is probably what you want"; R-L Core Graphics' one fd-2 line silenced around `CGPDFDocumentCreateWithURL`; R-M 45 section references -> 0, the reference kept in the record; R-N the proposal screen applies P12's own cross-folder predicate. Left for the owner: whether a locked zip routes to Unsupported/Encrypted automatically (`00`:120), and R-74's `_explanation` string still cites §8.4 in the record. | code | closed |
| R-95 | **Every model fact the local run wrote was a `school`, and most were filenames** (`todo.txt`, `IMG_4822.jpg`, `submission_backup.zip`): 38 `llm_supported` rows on 52 files, offline wrote none. R-54 on a third corpus, worse; fix-chain step 1 (owner text, D2 protocol) and step 2 (group-level school and term, units 6-9) are the cure, and the A_fact text is the owner's to change. | W | High | run + owner text | 3 (step 2), owner (step 1) |
| R-96 | **Local A_fact costs 48 to 100 s and 4.7 to 5.8 k prompt tokens per call**; 37 to 48 minutes for the fact pass on 52 files, one call hit the 600 s ceiling. On the owner's 215-file corpus the local pass is measured at ~100 s per call. Q-L's budget ceiling and the frame-first prompt-cache layout (105 G18) both bear on it. | P | Medium | run | later |
| R-97 | **`AnchorFact` carries one observation key for the whole group** (the first stating file's); c6b97a4 narrows the B dossier to the file's own excerpts, and the deeper fix is one observation key per stating file on the anchor. | W | Medium **Closed with R-105.** | code | closed |
| R-98 | **The model answers `subject` with the course title; the rule accepts only a code.** Cloud run, 23 coursework files reached: 10 subject answers, 10 refused VALUE_NOT_NORMALIZABLE, every one a 1-6 word title with no code. Under Q-A a title is not structurally invalid and under Q-C the model names and the person confirms, so a title-shaped subject must reach the review path, never a folder until confirmed. | W | High **Closed (merge of 07b3f06):** `cli.normalize_for_review` (1-6 words, one lower-case letter, no identifier, not a term) accepts a title as `ACCEPT_CONTEXT_SUPPORTED` with `requires_review`, stored `possible` -- the one state `PROPOSAL_ELIGIBLE_STATES` excludes, so it is never a level until confirmed; `normalize_for_model` and `SUBJECT_RULE` unchanged, the fifteen `76` §7 stress cases unmoved. All-caps and non-ASCII titles are still refused; `work_type` untouched (its members are ratified). | code | closed |
| R-99 | **16 of 83 cloud A_fact responses are SCHEMA_INVALID:** 7 break as JSON in the last bytes (G13's shape at site A) and 9 parse yet fail the schema. Each needs a precise recorded reason; a repair only where provably unambiguous. **Local run evidence:** the instrument works; 33 of 34 schema failures are `claim-0:citation_malformed`, one is `claim-0`. | W | Medium **Closed for the record (merge of 07b3f06):** one `decode_response` for every site; a decode failure keeps its reason code and gains the byte address on `claim_ref` (`schema:json_decode@byte-N`); the only repair is a complete document followed by one surplus closing bracket, which cannot open or extend anything; the mid-document mis-closes `105` measured stay refused. A parsed-but-invalid response names the template rule it broke on the address. The nine on the owner's run are not yet named (hypothesis: `payload_value_missing`, G16); the next run's `claim_ref` column settles it. Contract gaps R-106, R-107. | code | closed |
| R-100 | **60 of 83 A_fact calls went to files that are not coursework.** One situation per run asks the coursework schema of every file; the refused `work_type` words (abstract, proposed scope, application, annual report ...) are the validator correctly refusing answers about files the question should not have reached. R-37's row, measured in calls. **Local run evidence:** 82 `work_type` values refused, and the answers say what the files are (`application/pdf`, `notebook`, `image`, `survey`, `Research Paper`, `logo`): the coursework question asked of files that are not coursework. | P | High | design (R-37) | 3+ |
| R-101 | **`cycle_period` is not routed to the group,** because `cli._merge_reviewed_groups` writes one group per `--label`, so two semesters under one label disagree and the group value is `None`; enabling it costs two `Semester` folders on a two-course corpus. Turns on with per-course grain (B ratified and writing per-course acceptances, or the label merge retired). **Local run evidence (d409f58, qwen3:8b):** 114 `term` values refused `VALUE_NOT_NORMALIZABLE`; the recurring shapes are `2023-2024 Term 1` (15), `2023-2024` (13), `S2026` (5), and bare years and dates on files that are not coursework. The first two are a two-term academic year's own spelling; `S2026` is ambiguous between Spring and Summer and a refusal is right. | C | Medium | **open** (owner) | -- |
| R-102 | **Nothing writes a `school` fact any more.** Step 2 withdrew `holder_institution` from the per-file question and routed it to B's anchor facts; B is observe-only, no rule reads the syllabus, so the coursework tree has no school level on any corpus. Correct by `00`:42 (a weak reading is not a folder) and not the correct level. Who extracts the syllabus's school -- A on anchors only, a rule, or B -- is the owner's. | C | High | **open** (owner) | -- |
| R-103 | **Who confirms a `group_category_proposals` row** and the `user_confirmed`-vs-group precedence at a group-level dimension (today the group wins and nothing says it should). Both are gestures on a Release 2 surface. | C | Medium | **open** (owner) | later |
| R-104 | **`leave_in_current_location` at site D has the unscored fall-through `abstain` had:** `_residual_site` returns `None` for it, so a model asking for the file to stay is recorded `accept_direct / residual_destination`. "Leave it here" is a decision, not an abstention. | W | Medium **Closed (merge of e58b556):** `_residual_disposition` records `leave_in_place` for `leave_in_current_location`, outcome as the citations earned, `may_propose` false; P11's ladder already used the word. `mark_protected_or_unsupported` has the same fall-through and needs a P8 disposition the vocabulary lacks (owner). | code | closed |
| R-105 | **Two files that share a line share a P4 observation key,** and P7's `_consent_reference` resolves the key to one file; when that file is outside the request's targets the release refuses (`UnresolvableSpan`). c6b97a4 narrows B's dossier to the file's own excerpts, which avoids it at B; the key's shape (content-addressed, one file) remains and can refuse any site whose dossier spans files. | W | Medium **Closed (merge of e58b556):** `AnchorFact.observation_keys`, one per stating file in `file_ids` order, `key_for(file_id)`; a two-file anchor with one key is refused at construction; the dossier offers each file only its own key. Content address unchanged. The two-run identity test now carries two files sharing a line. No migration: a pre-change multi-file anchor row is refused loudly. | code | closed |
| R-106 | **The ratified A_fact schema and the template disagree in both directions.** Template rule 8 ("never two claims about one field: destroys the whole answer") has no schema form, so the validator destroys what the schema accepts; and the schema closes five objects (`additionalProperties: false` on root, claim, payload, citation, unknown) that the template never closes, so `claim_ref` -- forbidden by the schema, optional in `validation.py`'s docstring, read by `_validate_claim`, sent by this repo's own fixtures -- is legal to the code and illegal to the ratified text. One of the three has to move; the owner says which. | C | High | **open** (owner) | -- |
| R-107 | **A claim that declines and also asserts is recorded as an abstention.** `sites._proposal` returns at the first `unknown`, so a decline that also cites, or also carries a value, or whose statement is empty, loses the assertion; the schema's `oneOf` and template rule 10 refuse all three, and honest refusal runs through rule 11 (one malformed claim destroys the response, 1 in 14 measured). Three strict xfails hold the shape; trading abstentions for destroyed answers is a ruling. A repaired tail (R-99) also leaves no row saying it was repaired. | C | Medium | **open** (owner) | -- |
| R-108 | **A refused fact proposal whose citation is the wire handle crashes the run.** Local run over the owner's 199 files, 120th fact call, two hours in: the model cited by the `handle:` reference it was shown, the validator refused the value, and `llm_seam.refuse` -> `write_unresolved` forwarded the raw reference into `evidence_refs`, where M14 demands a `sha256:` observation key and raises `ValueError`. The accept path translates handles; the refusal path did not. A `ValueError` is a programming error and rightly escapes R-85's catch, so the fix is at the cause. Until fixed, no local run reaches grouping and the shadow row cannot be measured. | W | High (blocker) **Corrected and closed (merge of f9ce280):** an issued handle translates on both paths already; what crashed was a handle the release never issued (hallucinated or truncated), which survives translation, fails check 2, and was forwarded raw. `llm_seam.refuse` now writes only observation keys and takes check 2's reason when any reference was not one; the verdict still carries the raw reference in `citations_checked`. Seven tests, one reproducing the traceback verbatim. | run | closed |
| R-109 | **A resumed run repeats every model call it already paid for.** After R-108's crash the same database was re-run at d409f58: extraction resumed from its records (444 runs, one new), but the fact pass began again from the first file -- `llm_call_reuse` stayed at 0 and 120 recorded responses were not consulted, so the two hours of local calls are spent twice and a cloud rerun would be billed twice. `00` §8 (evidence extracted once and reused) reads onto model answers too: an identical request (same dossier digest, same prompt fingerprint, same model) must be answered from the record. **Closed:** `model_facts` reused a prior only when every open field was in `abstained_fields`, and `store.abstained_fields` selected `outcome = 'abstain'` alone; a `reject` left the field open and the identical question was bought again. Now `answered_fields` reads every non-superseded verdict under the prior dossier whatever its outcome, and an identical identity with a verdict on every open field spends no slot, no release and no call; refusals, call failures and `ValidationUnavailable` still record no identity and are re-asked; a malformed response re-asks through the field-subset check because its `claim_ref` is not a field. No dimension carries a run id, a timestamp or a path (two runs of one checkout over unchanged files: two identity ids, both stable). Eight tests in `tests/integration/test_a_fact_reuse_after_a_verdict.py`; four red on the unfixed code. No migration: the next run over the d409f58 database reuses at once. | W | High | run | closed |
| R-110 | **`group_level_value` is now the largest P10 cost, O(members²) per accepted group.** `pipeline.group_value_for_member` recomputes a (group, field) answer once per member: 1,000 calls make 1,003,000 `preferred_value_for` calls, 47.9 of 77.8 profiled seconds at 1,000 files; at 5,000 files P8-P11 is 2,365.6 s where it was 804 s before step 2 (0a0e272). Compute once per group; read per member. | P | High **Closed (merge of 02c4e61):** `group_level_values` reads the field once through `preferred_in_field` and answers every group from it; `group_level_reader` binds the per-member lookup per branch. Growth harness 20/60 members: 4,000/36,000 statements -> 4/4. 1,000 files P8-P11 92.1 -> 33.4 s; 5,000 files 2,365.6 -> 850.4 s; 26/26 identical. | run | closed |
| R-111 | **`placement_decisions.payload.graph_anchors` is not reproducible run to run** under real ids: 870 of 1,000 rows differ between two base runs of the same corpus, on corpora with large duplicate families. An R-78 residual in what the record says about a placement, not in the placement. **Closed:** `placement.graph.build_node_local_graph` cut §8.6's two ceilings over `sorted(kept, key=(-weight, to_file_id))`, and `cli.typed_edges_of` gives every edge `weight = 1.0` because P9 stores none -- so which files reached the graph, and which edges survived, was decided entirely by comparing two `uuid4`s. The seam now reads `group_edges` in the other end's `(content_hash, current_path)` order -- R-78's own key, `ORDER BY rowid` before it -- and the cut is a stable sort on weight alone, so content decides and a real weight would still dominate. Two runs: 870/1,000 -> 0/1,000 at 1,000 files and 24/36 -> 0/36 on R-78's corpus, over three hash seeds and serial vs seven workers; every other derived table byte-identical, and against base only `graph_anchors` moved -- no plan row, no index entry, no group plan. The two-run identity guard now covers all three P11 tables. | W | Medium | run | closed |
| R-112 | **Vision OCR flakes on one PNG in about half of runs on this machine**, and a cold Vision path costs 620 s against 20 s warm; it invalidated two 263-file identity comparisons until runs were paired by identical extraction. R-50's ceiling holds; the flake itself is R-50 territory and not yet understood. **Closed.** Reproduced 1 run in 11 over the pinned 263-file corpus, on content hash `782ff3d1...`: `image.metadata failed` naming the 600 s ceiling, no `ocr.apple_vision` row, run 626.4 s against 20-26 s. THERE IS NO 620 s COLD LOAD -- 626.4 s IS the 600 s ceiling plus a 26 s run. Sampled at the wedge: the worker's main thread in `-[VNImageRequestHandler performRequests:]` -> `-[CIContext render:toCVPixelBuffer:]` -> `CI::ProgramNode::mainProgram` -> `__DISPATCH_WAIT_FOR_QUEUE__`, waiting on `CI::KernelCompileQueue`, which was blocked in `flock()` inside `MTLCompilerFSCache::openSync` -- the Metal shader compiler's machine-wide on-disk cache lock. Six of seven workers took it and released in ~3 s; the seventh never returned. A parent-side warm-up does not prevent it (measured: parent's Vision call at t=0.29 s, workers wedged at t=3.15 s) and seven racing first calls do not reliably reproduce it (0 of 10 trials), so no warm-up was built. Fixed where the evidence points: the ceiling now rebuilds and retries the file ONCE, alone, in the same run, and only a second wedge is failed -- with `twice` in the row. Injected-wedge runs of the whole product: base `image.metadata failed`, 24 OCR rows; fixed `image.metadata complete` + `ocr.apple_vision complete`, 25 OCR rows. | P | Medium | run | closed |
| R-113 | **A placement with a destination and a blocked policy is in no review set,** so `--send-set` cannot address it and the residual review does not reach the files "nothing on this screen says what these are" now names. Measured on the verifier's corpus after `--residual`. The review's reach and the screen's promise must meet. | C | Medium | **open** (owner, design) | -- |
| R-114 | **The plain-run screen says the same paragraph up to six times.** Fresh offline walkthrough of main at 88dcb62 on the 52-file corpus: 430 lines, of which the eight-line "Nothing on this screen says what these are" explanation is printed once per group in that state (six times), and "Held for review as ... This plan has nowhere to put them yet: enable an area" once per group (eight times), each followed by the same list of review sets. Honest, and a person stops reading by the third repeat. A shared explanation is said once, in full, and each later group refers to it in one line. **Closed:** a block is printed in full the first time it applies on a screen and every later group in the same state gets one line pointing at it, keyed on the rendered block so two groups held for different reasons both print in full; the answer lines a question reaches a group with are never folded; the per-heading count of review sets travels with the pointer line. Fixture: three groups in one state, 12 repeated lines to 4. Known limit: the handle is the destination when the group has one, so two groups sharing a destination can make the pointer read past the wrong one. | C | Medium | code | closed |
| R-115 | **Review sets are eight-file chunks, and `00` §residual says they are divided by a reliable characteristic.** The screen already knows the reason per group (nothing readable came out; privacy settings allow no model; not yet classified; readings disagree; no folder matched; protected), and then holds the same files as "Not yet placed (1 of 4) ... (4 of 4)", so a group of six files is told "3 review sets of it have files under this heading" and which set is whose is not on the screen. `00` names the sets by what they share ("screenshots with no accepted project", "encrypted, unreadable, or unsupported", "multiple plausible destinations", "no extractable text"). Divide by the reason the screen already prints; the cap within a set stays R-93's number until the owner rules. | C | Medium | code | later |
| R-116 | **"Where should the files in Downloads go?" offers sixteen folders in no order a person can follow** (Coursework, Spring2026, CS3134, ECON2010/lecture, PHYS1401/lecture, W3134/lecture, cover letter, ECON2010, ...). The list is the tree; print it in the tree's order. **Closed:** `_every_destination` walks `frozen.nodes` pre-order, the same walk the folder picture is drawn with, and `for_folder` filters that walk instead of appending the current folder last; a node the walk never reaches is appended, never dropped; `skip` stays last. | C | Low | code | closed |
| R-117 | **The apply and undo listings come out in a different order run to run** (same ten files, byte-identical outcome, listing order differs between 0152167 and 88dcb62 on the same corpus). A person comparing two runs, or reading the undo list against the apply list, wants one stable order: destination, then name. **Closed:** `apply_run.run.plans_under` orders by the resolved destination path (destination then name), so the moves are made and listed in one order and `halt_on`/`not_attempted` stop varying; the undo listing is sorted at the print because `undo_order` must stay newest-first so a nested folder is removed inner-first. | W | Low | code | closed |
| R-118 | **Under a local model, P11 never assembles a dossier for any file.** Local run at d409f58 on the owner's corpus (qwen3:8b): 199 placement decisions, 176 `abstain privacy_blocked`, 0 site-C dossiers, so the `--shadow` row equals the applied row by construction. `placement/privacy.privacy_state_for` derives `local_only` from `mode_forbids(operation_mode, CLOUD)` and only ever asks about `cloud` ("`cloud` is the only locality P11 asks about"), so under `local_model` mode every file is `LOCAL_ONLY`, and `may_assemble_dossier` refuses `LOCAL_ONLY` outright without knowing the target is local. §8.4's own words in `privacy/denial.mode_forbids`: "A LOCAL model is permitted under both". Of the 176: 71 `personal_non_sensitive` (blocked by the mode alone; a local model may see them), 19 `sensitive_personal` and protected (stay blocked: shown to no model), 86 `unreadable_unclassified` (open question 5, owner's; default deny). The 71 are the files a local run can observe C on today and does not. **Closed:** `PrivacyState` now records WHY a file is local-only (`mode_forbids_cloud`, `unclassified`, `protected`; closed vocabulary in `placement/vocabulary.py`), and `may_assemble_dossier(state, *, target_locality)` reads the reasons against the locality of the model that would be asked: not local-only, yes; no target or a cloud target, no; a local target, yes only when every reason permits it (the mode alone always does; protected never; unclassified under the pinned `LOCAL_CALLS_ON_UNCLASSIFIED = False`); a local-only state with no recorded reason (rows written before this field) is blocked for every target. `PipelineInputs.model_target` carries the target. Note: the CLI runs a local model under `offline` mode (cloud consent absent), not `local_model`, so the fix covers both on P7's own authority. The gate is untouched. The 71 mode-only files reach site C; the 19 protected and 86 unclassified do not. Not yet measured on the owner's corpus; the local run is resumed after this merge. | W | High | code | closed |
| R-119 | **The model's empty answer is scored as a rejection, not an abstention.** Local run: 19 verdicts (`term` 10, `work_type` 9) rejected `VALUE_NOT_NORMALIZABLE` where the value was the empty string. An empty value is the model declining the field; recording it as `reject` re-asks the same question on the next run (R-109 reuses abstentions, not rejections) and counts a decline as a wrong answer in VERDICTS BY SITE. A rule, not a prompt change: an empty or whitespace-only value is the `abstain` outcome for that field. **Closed:** `fact_validation._declined_the_field` (empty, whitespace-only, `""`, or a quote pair around whitespace; a lone quote and a non-string are not) takes the `abstain` outcome after checks 1 and 2 with an explicit abstention's disposition, so `abstained_fields` reads it and R-109 stops the re-ask; the consequence writer is handed a declined proposal so P6 records `model_returned_unknown` with no value row. **For the owner:** the ratified `a_fact_response_schema.json` puts `minLength: 1` on the value, so the schema forbids the shape the validator now treats as a decline; the schema is untouched and the disagreement is written beside the matrix row in `tests/p8/test_p8_a_fact_schema_failures.py`. | W | Low | code | closed |
| R-120 | **A file that died once and wedged once is reported as if it had done the same thing twice.** R-112 made the ceiling path and the death path share one `attempts` counter in `extraction_pool`, which bounds a file at two attempts however they end, but the failure reason names the mode of the last attempt ("killed both times" for segfault then wedge, "died twice" for wedge then segfault). Name each attempt's end rather than one mode; the test that asserts the word `twice` moves with it. | W | Low | code | later |
| R-121 | **Open question 5 is answered two ways in the tree.** `cli.py` pins `UNCLASSIFIED_PERMITS_LOCAL = True`, documented as read by both the gate and the route "so they cannot answer differently"; P11 (`placement/privacy.py`) pins `LOCAL_CALLS_ON_UNCLASSIFIED = False`. Under the first answer the 86 unclassified files in the local run would clear P11 and the gate would admit them for a local model; under the second they are blocked before the gate. R-02's shape again: one question, one name, one answer, and the owner's. Also for the ruling: `sensitive_personal` WITHOUT the protected flag follows the flag (P7's rule: consume the flag, never infer from the class), so such a file reaches a local model when the mode is its only reason; zero files in the run were in that state (all 19 were flagged). | W | Medium | **open (owner)** | later |
| R-122 | **After R-114 the 52-file screen is 412 lines, not 430: the block that still repeats is "Held for review as ... This plan has nowhere to put them yet: enable an area with `--residual`", eight times.** R-114 folds a block only when it is word-for-word the same, and this one differs per group by the set's name and the list of sets, so it never folds. Two parts, two fixes: the set name is R-115's (one set per reason, so the list of other sets goes away), and the closing sentence about enabling an area is one fact about the plan, said once, under the first held group, with each later group's one-line pointer. Remeasure on the 52-file corpus after both. | C | Medium | code | later |
| R-28 (corrected) | Most of R-28 was closed before `daca470` (`94` F11); two live `shallow-by-choice` reasons in the person's voice fixed; the `user_edited_label` half is a real gesture (`--label` is typed by the person) and is kept and defended by a test. | W | closed | run | 3 |
| R-53 (closed) | Site C's request is reference-only by design, so `unreduced_fits` cannot be measured before the gate resolves it; the ceiling is enforced at the gate on the resolved view (SF-5's `measure_tokens`), which C shares with A. The assertion stays as the reduction-shape claim its docstring makes. | — | closed | code | — |

### 14.4 Process facts worth keeping

- **`tests/integration/test_the_product_survives_a_real_run.py` enforces a 300 s ceiling on a real run** and errors out (5 errors) whenever two or more agent suites run beside the merge chain; alone it passes in 14 s. Read a chain's 5 errors there as load, rerun the file alone, and never count them as the merge's.

- The session scratchpad is shared with the wave's agents; the lead's baseline scorecards there were
  deleted mid-wave. Lead artefacts now live outside it (`~/.graph-agent/lead/`); the baseline survives in
  §9 and §14.1.
- The scoreboard's load ceiling (8.0) refuses to start while agents run suites; the runs read placement
  outcomes only, so `--force` is used with the note that no timing is read from such a run.
- A machine reboot killed one wave of agents; every branch survived because agents commit per
  deliverable. That rule stays.

*Section added by Claude Fable 5.1.*

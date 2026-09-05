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
| R-16 | `apply_p8_verdict` writes no `display_label`, `group_category` or `coherence_verdict`; per-member include/exclude/uncertain collapses to blanket memberships | W | High | latent, code | A L1 B9 | 3 |
| R-17 | C/D dossier enumerates all legal node ids with no profiles or typed neighbours; snapshot derives from facts, fragile for sparse files | W | Medium | latent, code | A L2 | 2 |
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
3. **R-25, R-30, R-26, R-38, R-39:** `scan_state='included'` filter in roster, names, rejections
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
| 13.3 | Scope (§12.16) | **Release 1 is the engine, Phases 0 to 4.** Onboarding, the role matcher, the canvas, the six gestures, the household workflow and automatic filing are Release 2. | C15 to C21 and the §4.5 onboarding entries stay open and do not block "done". Their xfails stay strict. |
| 13.4 | Process (§12.7, §12.11, §12.12, §12.17) | **All four accepted as written.** | Three runs per condition, judged on the median with ±1 on `wrong` and ±2 on spillover; a commit that raises either is reverted before the next lands; a "fixed" claim needs a fresh session's run diffed against §9; a held-out persona corpus labelled by the owner, run once at the end of Phase 3, never tuned against. |
| 13.5 | Q-A, placement bypass (`00`:110, 114) | **Model decides, rules validate.** Every placement goes through the model. Scores rank and shortlist candidates; a rule may reject only a structurally invalid answer (node not in the frozen tree, cited fact not in evidence). A unique direct match is the top-ranked candidate the model is shown, not a bypass. Precondition: the §11 fix chain, because the model as wired today makes placement worse. | R-19 closes by implementation: P11's two-condition threshold and `needs_model_call` stop skipping site C for placeable files. Budget consequence: up to one C call per placeable file per run (42 calls took 79 s on 2026-09-05; 199 would take about 6 minutes on the cloud tier, longer locally). |
| 13.6 | Q-B, contradiction checks (`00`:42) | **Grounding hard, the rest shown.** A hard veto only when a model fact is not grounded in the file's own evidence (quote or metadata) or falls outside the derived schema. Every other check, including rule-fact precedence over model facts, is shown to the model as a flag with its evidence, and the model reconciles. | R-20. The `FactResolver` stage order (direct, rule, llm) stays as the order of collection, not of authority; a rule fact that disagrees with a grounded model fact becomes a flag in the next call's dossier, not a silent override. |
| 13.7 | Q-C, vocabularies (`00`:41-43, constitution 1) | **Model names, user confirms.** `work_type`, `subject`, `term` and user labels are model decisions grounded in evidence. A value the library has not seen is proposed once; the user confirms or renames it; it joins that user's vocabulary in the database. No alias tables or equivalence maps in code. Template levels stay fixed as structure. | R-21. Reverses the direction of `3e4a64d` for unseen values: a closed-vocabulary rejection becomes a "confirm this new value" question instead of a dropped fact. The ratified library remains the default vocabulary the model is shown first. |
| 13.8 | Q-D, preservation heuristics (`00`:22) | **Split: refinement allowed, removal constrained.** Moving a file deeper inside its own branch is the model's call. Moving it out of the person's existing arrangement stays a constraint surfaced to the user. | R-22. `_without_kind_only_moves` and `_staying_put_wins_a_tie` distinguish refinement from removal (§11 fix 5). The six `Python 1006` files placed one level short are the pass case. |

**What is still the owner's after these rulings, and when.** Ratifying each prompt at the end of its
bakeoff, with the numbers attached (D2 protocol, `103` §28.1); labelling the held-out corpus before
the end of Phase 3; accepting a stated gap in the bakeoff row if one appears. Nothing else blocks
Phase 0.

**Build authorisation, same evening.** The owner authorised the build to start once ready, with
dynamic workflows and multiple agents, on the condition that every dispatched agent, and every
agent those agents dispatch, runs on Opus 5. The standing constraints do not move: protected
containers are marked and counted, never opened; the corpus never enters git; no cloud
ground-truth pass until SF-1 is closed; prompt text and vocabulary members are ratified by the
owner, never by an agent.

*Section added by Claude Fable 5.1.*

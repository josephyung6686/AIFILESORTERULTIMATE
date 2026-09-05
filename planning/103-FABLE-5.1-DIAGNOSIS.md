# 103 — Full diagnosis and reintegration plan

**Diagnosis by Claude Fable 5.1 (Anthropic), 2026-09-05, as a second opinion.**
Session: https://claude.ai/code/session_01MAH6kRZW1VEPpTjMc58g8f
Branch: `build/p6-p7-first-packages`, HEAD `9351788`, plus the uncommitted semantic-recognition
patch in `src/cli.py` (270 lines) and `tests/integration/test_p9_embedding_pipeline.py`.

**Source of truth for this document:** `planning/00-database-agent-product-design.md`, cited as
`00`:LINE. Section numbers (§) are `01-product-design-structured.md`'s. The owner's corrected
purpose statement (the LLM is the decision engine; code feeds it inputs or applies its outputs)
and the product constitution of 2026-09-05 are treated as amendments; where they conflict with
`00`, the conflict is flagged in §9 and NOT resolved here.

**Nothing in the repo was changed by this diagnosis.** Everything below was produced by reading
the design, tracing `cli.main` forward call by call, and running the product. Every number is
from a run made today unless marked otherwise. Code is cited by function name because the working
tree's `cli.py` line numbers differ from HEAD.

---

## 0. The verdict in one paragraph

The pipeline skeleton is complete and the mutation half is real: on a synthetic four-file folder
the product proposed a tree, froze it, moved a file, refused to move a file edited after the
freeze, and put the moved file back byte-identical. What does not work is the middle of the
design, where either a model or a person decides. Four of the five model call sites (group
coherence, placement judge, residual review, custom templates) are built and tested and wired to
`None`. The fifth, site A (facts), is wired but the privacy gate refuses its every release for
ordinary files: since `fd68cb6` (2026-09-05 01:54) a file the detector classified by finding no
safety vocabulary is denied a cloud call, and unclassified files were already denied. On the
owner's 199-file corpus today, 155 of 199 files cannot reach the model at all; on my five
synthetic files, 5 of 5 were refused, and the screen said "5 files sent". The test suite is green
at 8021 passing, and one of those tests asserts the very denial that blocks the product's only
model site. Meanwhile the human stages the design puts in the loop (review groups, choose
top-level areas, answer per branch) have no surface, so the product runs one `--situation` over a
whole disk, auto-accepts every group under one label, picks the first nesting that passes, and
abstains on 32 of the 41 files whose right folder is known. Nothing guesses; nothing decides
either.

---

## 1. What was read, what was run, what was not verified

**Read in full:** `00` (all 286 lines), memory files, `84-HANDOFF`, `83`, `86`, `94`, `85` (§1-4,
§9-20), `101`, `102`, `82` §0, `02` head, `.planning/codebase/ARCHITECTURE.md`; `cli.main`,
`cli.run` and its closures, `cli.model_route`, `cli.fact_call_authorities`,
`cli.model_fact_resolver`, `cli._direct_stage`/`_rule_stage`/`_media_type_stage`,
`cli.review_and_accept`, `cli.choose_option`/`nesting_chooser`, `cli._print_fact_pass`,
`cli._raise_blocked_questions`, `cli.folders_nothing_could_be_read_from`; `model_facts.py` whole;
`model_placement.py` head; `production.folder_levels_for`, `run_production_p8_p11`;
`grouping.pipeline` head and model seam; `placement.pipeline.place_file`, `_judge_with_model`,
`PipelineInputs`; `placement.scoring`; `facts.resolver.FactResolver.resolve`;
`facts.domains.active_field_allowlist`; `recognition.rules`; `privacy.gate.release` (the denial
ladder), `privacy.denial.no_safety_evidence_denies`; `llm_harness.harness.run_call` skeleton,
`eligibility.assess_call`; the ratified A_fact template and response schema;
`tools/groundtruth/*`; both ground-truth scorecards.

**Run:**

| # | Command / action | Result |
|---|---|---|
| R1 | `pytest tests/integration/test_composition_root.py -rx` | 6 passed, 3 xfailed: renaming overlay has no writer; per-branch situation question called at neither end; ~235 public mechanisms unreachable from `cli.main` |
| R2 | Offline run, 4 synthetic `.txt` files, `--situation academic.coursework --label Coursework` | Tree `Coursework/{essay,lecture,syllabus}`; 3 ready to file, `HW 3.txt` "waiting for you to say what these are" |
| R3 | `--freeze`, then `--apply Coursework/syllabus` | File moved into `Coursework/syllabus/` |
| R4 | `--undo Coursework/syllabus` | Restored to original path, same SHA-1 before and after; product-made folders removed |
| R5 | Append a line to `Lecture 08.txt` after freeze, then `--apply Coursework/lecture` | Refused: "This file changed after the preview." Nothing moved |
| R6 | Cloud run, 5 synthetic files, `--enable-cloud`, real key | "Facts from a model: 0 written, from 5 files sent to deepseek-chat. 5 refused: the gate refused the release." `llm_dossier=0`, `llm_response=0`, `llm_refusal=5`. Nothing left the device, zero spend |
| R7 | Full suite `pytest tests/ -p no:randomly` | 8021 passed, 19 skipped, 21 xfailed in 4:47 |
| R8 | `tools.groundtruth` offline, `academic.coursework`, owner's 199-file corpus, on HEAD | See §10.1 |
| R9 | `classifications` by `basis` on the R8 database and on the 4 Sep database | See §10.3 |

**Not verified, stated so nobody reads it as verified:** whether a field the model declined is
re-asked and re-spent on every run (the verdict path was never reached, see §7); any cloud
behaviour on the owner's own files (none were sent); the `--semantic-model` channel (weights and
`onnxruntime` are present on this machine, the `cli.py` half is uncommitted, not exercised);
anything at scale beyond 199 files.

---

## 2. Target architecture summary, extracted from `00`

1. **Stages in order.** Select sources and roots with exclusions applied first; roots are context,
   not permission (`00`:19-22). One reusable extraction pass per content version, stat-cached,
   emitting one evidence shape with location, context and reliability (`00`:23-35). Facts: direct
   facts from explicit sources; rule-validated facts only with context checks, word boundaries,
   positional weighting, score and margin; LLM-supported facts from a compact dossier, validated
   before they become active (`00`:37-51). Grouping: rules find anchors, the graph assembles a
   bounded neighbourhood, the LLM answers four constrained questions with citations and may
   abstain, a validator checks every citation, the user decides (`00`:55-64). Tree design: the
   engine proposes a small set of top-level areas from accepted groups, domains and existing
   folders; the user accepts, renames, merges, defers; then branch by branch the engine offers
   nesting options with counts and warnings; uneven depth; freeze closes the destination set
   (`00`:66-102). Placement against the frozen tree: node profiles, retrieval, node-local graph,
   deterministic when a unique direct match, LLM as hierarchical judge otherwise, two-condition
   validation, a structured decision with evidence type and review policy (`00`:104-116).
   Residual: a surfacing screen by sets, a user decision per set, then the LLM chooses from a
   controlled action set inside the approved residual library (`00`:118-129). Apply: plan with
   full preconditions, recheck, move, verify, conditional undo (`00`:155-175).
2. **Where the LLM is called and what it gets.** Site A facts: compact evidence packet, returns
   schema-bound facts with exact citations or `unknown` (`00`:39-42). Site B groups: the candidate
   group dossier with anchors, candidates, typed edges and conflicts; returns coherence,
   membership, outliers, a label (`00`:58-59). Site C placement: the placement dossier with the
   file's facts, excerpts, group memberships, top legal candidates with profiles and deterministic
   scores; returns child, parent, scoped fallback or nothing (`00`:110-111). Site D residual:
   filename, type, dates, text, metadata, sensitivity, the approved residual library; returns one
   of eight actions (`00`:124). Site E template: the group dossier and constraints; returns a
   strict-JSON template (`00`:97).
3. **Where deterministic code stops.** It extracts, shapes evidence, writes direct and
   context-checked facts, detects duplicates, parses dates narrowly, retrieves and suppresses
   candidates, validates model output, applies stop rules, enforces budgets, and moves files
   safely. `00` also lets it override: a stronger direct or rule-validated fact contradicts a model
   fact (`00`:42) and the two-condition rule sits after the model's verdict (`00`:114).
4. **Confident, unsure, cannot.** Unique direct match: deterministic, no model (`00`:110). Several
   plausible nodes: the model. Below support or margin: abstain into review, a scoped General, or
   stay put (`00`:99, 111, 114). Never fill a slot for a tidier path. Correct abstention is a
   success.
5. **Maximum customizability, concretely.** Sources, roots, cross-folder permission; accept,
   rename, merge, split, defer, create branches; choose nesting order and depth per branch; keep
   existing folders untouched or adopt them; save custom templates; enable, rename, relocate
   residual areas and choose physical, review-only or leave-in-place; reject and correct facts with
   scope; versioned plans with diffs; four privacy modes and per-file reclassification
   (`00`:20, 67-70, 97, 100, 121, 127, 185, 261-264, 280).
6. **Non-negotiable safety rules.** No move without a plan and review; never overwrite; conditional
   undo; never guess; protected material never in cloud prompts and never auto-moved without an
   explicit policy; never silently drop a file; budget exhaustion never becomes lower-quality
   automatic classification; no fuzzy dates; word-boundary matching; existing folders never
   silently reorganised (`00`:100, 155-175, 185, 239, 257-259).

---

## 3. The built flow, traced from the entry point

`cli.main` → parses flags; `--situation` and `--label` are required for a run → opens the database
outside the corpus → `model_route` builds three DeepSeek clients from `.env` (or prints why not) →
`announce_cloud_posture` → `run`.

`cli.run` → loads the template catalogue, resolves the situation to one schema and its folder
levels (`production.folder_levels_for`) → builds the lexical `recognition.Detector` (optionally
wrapped by `SemanticRecogniser`, uncommitted) → `run_production_corpus`:

1. `orchestrator.run_p1_p7`, per file: P3 scan → P5 extract (pdfium, python-docx, Apple Vision
   OCR, zip manifests, text documents) → P4 evidence → P6 `FactResolver` with stages
   `direct` (`DIRECT_SLOTS` is empty) and `rule` (`SUBJECT_RULE` regex plus academic context
   terms; `date_facts` for `term`; `kind_facts` for `work_type` from a 4,031-term vocabulary;
   `media_type` for images) → P7 `classify`.
2. `cli.run.downstream`: `_family_pass` (byte-identical duplicates only) → `_model_fact_pass`
   (site A, only if a key is configured AND this folder's stored consent is `hybrid`) → print
   protected containers, set-aside files, candidate roots.
3. `production.run_production_p8_p11`: P9 `group_subject` with `p8_run_call=None` (deterministic
   groups on shared validated facts in the hardcoded `active_schema_for` tuple) →
   `cli.review_and_accept` merges every group into one named `--label`, `decided_by=RULES` → P10
   `design_tree` with `nesting_chooser` recording a question and `choose_option` taking the first
   passing option → `approve_plan`, `set_privacy_policy` → destination index → P11 `run_corpus`
   with `placement_inputs` carrying `gate=None, model_client=None, prompt=None,
   call_dependencies=None, model_call_request=None, chosen_node_of=None, residual_action_of=None,
   sensitivity_policy=None` → per file `place_file`: retrieval, suppression, deterministic
   `assess`; if `needs_model_call` then, because `model_path_available()` is false, fall through to
   abstention.
4. `_raise_blocked_questions` (tied readings only) → `report` → optionally `freeze` →
   on a later invocation `_move_frozen_files` → `apply_run.run` → `mutation.*`.

**What actually decides a file's folder today:** the situation's folder levels from the library,
the three rule producers, deterministic scoring with threshold 0.50 and margin 0.20
(`SUPPORT_POLICY`), and the person's own existing folders. No model, no person at a screen.

---

## 4. Inventory A: designed but unbuilt

| Design item | Evidence that nothing implements it |
|---|---|
| §5.1-5.2 horizontal pass: engine proposes top-level areas with counts, user accepts/renames/merges/defers | `cli.main` requires `--situation` and `--label`; `cli.run` applies one situation to every file and `DEFAULTED_DECISIONS` says so on screen; `questions.triggers.question_for_situation` and `questions.store.selected_situation` are called by nothing (R1 xfail) |
| §4.10 step 5, §5 opening sentence: the person reviews group suggestions before design | `cli.review_and_accept`: "the review screen, non-interactively: keep everything, as one named group" |
| §5.7 LLM-generated custom template (site E) | `tree_design.template_schema` builds a request nothing calls; `tree_design.routing` raises `CompositionConflict(C3)` when no template fits |
| §7.5 residual review sets by kind, with type distribution, age range, evidence availability | `cli.run.residual_partition`: two sets, split on protection only, `file_type_distribution=()`, `age_range=()` |
| §7.4 residual dispositions review-only and leave-in-place | `ResidualChoice` is always `PHYSICAL_DESTINATION`; "leave all my screenshots where they are" cannot be said |
| §5.11 tree health view; §8.8 meaningful plan diff | `tree_design.health`, `tree_design.diff` unreachable from a run; every run mints a fresh plan version |
| §8.6 budgets and legible deferral | `budget_exhausted=lambda ceiling: False` in `cli._resolver` and `cli.model_fact_resolver`; `_bootstrap` seeds only `placement.config.CEILINGS`, all at `CEILING_VALUE=8`; P5 OCR ceilings and P6 ceilings seeded by nothing; `extractors.budgets.extraction_counts` unreached |
| §8.4 local-model mode | No local client is ever constructed; `readers.model_ollama` and `readers.model_anthropic` are imported by nobody. This matters because the gate's own remedy for its most common refusal is `use_local_model` |
| §4.2 embeddings as a retrieval channel | Committed `cli.run` passes `EmbeddingsOff()` and `RetrievalKnowledge(similarity=None)`; the MiniLM channel exists only in the uncommitted diff behind `--semantic-model DIR` with no default |
| §8.4 consent requests, redaction, default local-first policy | `privacy.consent.*`, `privacy.redaction`, `privacy.defaults.effective_policy` have no caller; `cli.fact_call_authorities` gives the gate `classifier=lambda ...: None` and `transform=lambda ...: "[redacted]"` |
| §2.6, §3.11 version families, near-duplicates, photo events, sessions | Rules unruled (`97`, `98`); `_family_pass` binds only byte-identical `duplicate_family` and `near_match=lambda: False` |
| §8.5 replay scoring, adversarial suite, shadow mode | `--record`/`--replay` exist but nothing authors labels, so a replay asserts nothing; `eval_harness.adversarial`, `shadow` unreached |
| §2.9 formats | `.svg`, `.raw`, `.ris`, `.rlt`, `.code-workspace`, extensionless: 0 read on the owner's corpus; `readers.signatures` (magic numbers) exists and is not wired into `cli._detect_format` |

---

## 5. Inventory B: built but disconnected

| Mechanism | Where the path stops |
|---|---|
| Site B group judgement: `grouping.p8_seam.build_dossier_request`, `apply_p8_verdict`, `llm_harness.group_validation` | `cli.run.downstream` passes `p8_run_call=None, p8_authorities=None`; `grouping.pipeline` returns `not_implemented_reason=no_model_call_configured` |
| Sites C and D: `model_placement.PlacementCallAuthorities`, `model_path_injections`; `placement.pipeline._judge_with_model`; `llm_harness.placement_validation` (fifteen checks) | `model_placement.py` has no importer in `src/`; `cli.run.placement_inputs` passes eight `None`s; `model_path_available()` has been false on every run ever made |
| Site E: `tree_design.template_schema`, `llm_harness.template_validation` | No caller |
| The 314 authored `needs_llm` readings, one per situation, saying in prose what the model must decide | `recognition.compile` emits them, `recognition.rules` loads them into `SchemaRules.deferred_readings`, `Detector` carries them; read nowhere outside `src/recognition/`; never in any dossier |
| P13 review surface (30 modules in `review_surface/`), `review_gestures.py` | `cli` imports only `review_surface.schema`; `review_gestures` has no importer; `apply_run.approval` reaches `review_surface.approvals` for the freeze approval only |
| Extensionless-file detection `readers.signatures` | Not called by `cli._detect_format` |
| `grouping.store.record_stop_rule_outcome` | `grouping.pipeline` returns the outcome and never records it; `stop_rule_outcomes` table has never held a row |
| `readers.model_ollama`, `readers.model_anthropic` | Imported by nobody |
| `privacy.consent.open_consent_request` path, `remedy_options` on every denial | Remedies are computed and shown to no one; `86` §5.1 recorded this and it stands |
| `tree_design.templates.BranchTemplateBinding`, `provenance.record_template_application` | `template_context_for=lambda ...: None` in `cli.run.design_authorities` |
| ~235 further public mechanisms across ~97 modules | The live list is printed by `tests/integration/test_composition_root.py::test_every_public_mechanism_in_the_source_is_reachable_from_the_entry_point` |

---

## 6. Inventory C: built, wired, and wrong

| # | Behaviour | Mechanism | What it breaks |
|---|---|---|---|
| C1 | **The only wired model site is refused by the privacy gate for ordinary files.** | `privacy.gate.Gate.release` denies a cloud release when the file's classification basis is `detector_no_safety_evidence` (`privacy.denial.no_safety_evidence_denies`, introduced in `fd68cb6`, 2026-09-05 01:54) and when the file is unclassified (`unclassified_denies`), and for protected files. `recognition.Detector` writes `detector_no_safety_evidence` for every ordinary file that matched no safety work-type term anywhere. Owner's corpus today: 44 files with basis `detector` could pass, 41 `detector_no_safety_evidence` denied, 19 protected denied, 95 unclassified denied: **155 of 199 cannot reach the model**. Synthetic corpus: 5 of 5 refused. The rule is inverted: a file that brushes safety vocabulary is admitted, a purely ordinary one is not. `101`'s cloud measurement (78 dossiers, 4 Sep 22:18) predates this commit. | `00`:39 (the model receives the ambiguous files); constitution rule 2 |
| C2 | **The screen says files were sent when none were.** R6 printed "from 5 files sent to deepseek-chat" with zero dossiers. | `cli._print_fact_pass` counts every outcome, including `Refusal`, as "sent" | `84` §6 second rule: what the screen says must be true |
| C3 | **Two parts answer one question oppositely.** `9351788` widened `cli.model_route_permitted` so unclassified files reach the route; the gate still denies them. Net effect: five refusal rows instead of five `privacy_withheld` rows. | `cli.model_route_permitted` vs `Gate.release` | `00`:259 legible deferral |
| C4 | **Every group is auto-accepted and merged under `--label`.** | `cli.review_and_accept`, `decided_by=RULES`, `label_source=USER_EDITED` | `00`:64 the user makes the final decision; flattens a multi-role disk into one category |
| C5 | **Nesting is chosen first-that-passes; the question is printed afterwards and applies next run.** | `cli.choose_option`, `cli.nesting_chooser` | `00`:95 counts shown before committing |
| C6 | **A model-written fact outside four fields can never seed a group.** | `cli.run` `active_schema_for=lambda ...: (DIRECT_SLOTS fields) + (term, media_type, work_type)`; P9 groups only on these; the library's `role_bindings` already state the real per-situation schema (`102` §3) | `00`:56 seeds from validated shared facts |
| C7 | **The dossier token cap is asserted, never measured.** | `model_facts._call_dependencies` hardcodes `unreduced_fits=True, summarized_fits=False, anchors_fit=False`; `cli.fact_call_authorities` builds `Gate` without `measure_tokens`, so `over_dossier_ceiling` never runs; `_bootstrap` stores `model.max_dossier_tokens_per_call = 8` while requests carry `GROUPING_LIMITS.max_dossier_tokens = 4000` | `00`:251, 257 |
| C8 | **Records claim decisions nobody made.** | `cli.refinement_for` writes `shallow-by-choice` with a first-person reason; `cli.run.approve_plan` writes `user_edited_label=label`; `surface=SURFACE_UNATTENDED` fixes the where, not the who (`94` F11) | `00`:284 reconstruct what the user approved |
| C9 | **One protected file placed; eight extracted before classification.** Owner's corpus, both scorecards: `Covid -19 vaccination record (1).pdf` placed; 8 of 8 protected files have text units. | `orchestrator.run_p1_p7` order is extract → resolve facts → classify; `cli.run.design_authorities` isolates protected files only after that | `00`:185 "should enter a protected state immediately... should not be moved automatically" (the placement is a clear breach; the extraction order is a §9 question) |
| C10 | **Software-project exclusion fires under every situation**, setting aside 16 of the owner's files before reading, including under `code.notebooks-experiments`. | `scan_agent.exclusion` never consults the situation | `00`:22 vs `101` "what this does not excuse" |
| C11 | **`work_type` vocabulary is the union of four schemas**, so `resume` becomes a folder under Coursework. | `cli._work_type_vocabulary` | north star; `102` §5 |
| C12 | **`subject` values are the right course under the wrong spelling**: 8 produced, 0 of 43 correct against the labels (`E1006` vs the owner's folder `Python 1006`). | `cli.SUBJECT_RULE`; `values.aliases`/`merged_into` populated by nothing | `00`:34 raw vs normalized vs display renderings |
| C13 | **A file can vanish from the freeze block** (extensionless file, `94` F22). | `apply_run.freeze` produces neither a plan nor a hold for some outcomes | standing rule: never silently omitted |
| C14 | **Abstention reasons hide that no model ran.** With consent on, a file that needed a judgement reports `low_margin`; with consent off it reports "§8.4 did not clear this file" (`94` F3). | `placement.pipeline.place_file` falls through to step 9 with no reason of its own when `model_path_available()` is false | `00`:259 |

---

## 7. LLM-bypass findings (Step 2), each tagged

Buckets: **(a)** legitimate deterministic pre-filter; **(b)** rule masquerading as a decision.
Tags: **wiring bug** / **design mismatch** / **missing piece** / **owner decision**.

1. **Hardcoded mappings that decide without a model.**
   - `cli.WORK_TYPE_VOCABULARY` → the `work_type` folder level. Bucket (b). Sanctioned by `00`:41
     as a validated fact; forbidden by constitution rule 1. **Design mismatch, flagged §9.4.**
   - `cli.SUBJECT_RULE` regex plus context terms → `subject` level. Bucket (b). Same sanction, same
     conflict. Measured 0 of 43 correct. **Design mismatch, flagged §9.4.**
   - `cli.DATE_PATTERNS` → `term` level. Bucket (b) for the folder; (a) for the parse (`00`:46
     demands exactly this narrowness). **Design mismatch on the folder half, flagged §9.4.**
   - `production.folder_levels_for(situation)` → the tree's dimensions and their order, from a
     208-row library. Bucket (b) under the corrected purpose ("tree structure is a model
     decision"); §5.4 designs templates as controlled schemas. **Design mismatch, flagged §9.4.**
   - `recognition.Detector` term lists → schema and handling class. Bucket (a) for the protection
     verdict (a pre-filter the design wants at `00`:185); bucket (b) for the domain verdict when it
     is the only thing deciding coverage. **Design mismatch at the gate, §9.1.**
2. **A model call exists but is never invoked.**
   - Sites B, C, D, E: injections are `None`. **Wiring bug**, compounded by an **owner decision**
     (no ratified prompt text for any of the four; `run_call` refuses an empty template).
   - Site A: invoked only under `--enable-cloud`, then refused by the gate (C1). **Wiring bug**
     between `cli.model_route_permitted` and `Gate.release`, resting on the §9.1 conflict.
3. **Model output discarded, ignored or overridden.**
   - A site-A fact outside the `active_schema_for` tuple never groups (C6). **Wiring bug.**
   - `cli.contradicts_stronger` lets rule and direct facts outrank `llm_supported` facts.
     Design-sanctioned (`00`:42). **Flagged §9.3.**
   - The site-A ask is now correctly narrowed to the situation's open folder-level fields
     (`model_facts.open_question`, constitution rule 3). Correct, and unmeasured since it landed.
4. **Extraction and schema built for a rules-engine consumer.**
   - Closed `facts.domains.DOMAIN_FIELDS`, the fixed template levels, `WORK_TYPE_VOCABULARY`.
     **Design mismatch, §9.4.**
   - The authored `needs_llm` prose exists precisely to steer a model and is never sent.
     **Wiring bug.**
5. **Null decisions: neither rule, nor model, nor person.**
   - `--situation` and `--label` are required human input applied to the whole disk.
     **Missing piece** (the horizontal pass, §5.1).
   - 32 of 41 known-answer files end "Waiting for you to say what these are" with no gesture that
     says it (`94` F4); with cloud on the sentence changes to `low_margin` (C14). **Wiring bug** in
     reason codes; the abstention itself is the design's correct outcome.
   - On the offline run `HW 3.txt` reports "not classified, so it was not shown to a model" when
     no model exists for any file. Same family.

---

## 8. Input and output audit (Step 3)

- **Is the evidence sent to the model bounded?** By count, yes: `FACT_CALL_MAX_RELEASED_OBSERVATIONS
  = 12`; `model_facts.releasable_observations` excludes `path`, `filename` and `ocr` zones,
  P5-flagged sensitive keys, and any span covering a whole text unit; the filename now arrives
  through the `privacy.items.Filename` door (`e31c70f`). By tokens, no: C7. A single long body
  observation short of its whole unit passes untrimmed.
- **Is there caching?** Extraction: yes, P3 stat cache plus content-hash-keyed extraction runs;
  a second run over an unchanged folder submits nothing to the pool. Facts: settled fields are not
  re-asked (`model_facts.pending_fields_for`), and a user rejection suppresses the equivalent call
  (`eligibility.suppressed_by_learning`). **Unverified:** whether a field the model declined is
  re-asked and re-spent on every run. `llm_dossier.dossier_id` is a content-addressed primary key
  and `llm_harness.store` mentions `IntegrityError` out of `run_call`, so a repeat may crash rather
  than dedupe. Test in Phase 2.
- **Is the output constrained?** Yes, and this is the best-built part of the model path: a closed
  `allowed_vocabulary` narrowed to the situation's open folder levels, a JSON response schema,
  mandatory citations with exact spans, and a validator checking field membership, citation
  existence, span match, value-in-cited-text (`value_grounding`), normalisation and contradiction.
  The transport sends no `response_format`, so JSON is enforced by parsing after the fact and one
  malformed claim voids the whole answer (ratified rule 11).
- **Silent extraction failures?** Not silent: unsupported (16), failed (3), capped (4) are recorded
  and printed by format. The starvation that matters is upstream of the gate, not of the model:
  95 of 199 files get no classification from the lexical detector, and 41 more get the basis the
  gate refuses. Extraction on the owner's corpus recovered text from 162 of 199 and prose from 151.

---

## 9. Conflicts and safety flags awaiting the owner (Step 5)

Listed separately and unresolved. Each changes what the repair plan may do.

1. **D1, blocks Phase 0.** `96` §20 (2026-09-04) ruled that "no safety evidence found" does not
   satisfy §8.4's precondition for a cloud call; the constitution (2026-09-05) says a gate that
   excludes readable files from the engine is a defect. Both are the owner's, a day apart. The gate
   itself names the three remedies: (a) rule that basis `detector_no_safety_evidence` admits a
   cloud call; (b) wire a local model, which `00`:189-193 names as a mode, `readers.model_ollama`
   already exists, `unclassified_permits_local=True` is already set, and the gate permits local on
   both denial reasons; (c) a user-set classification (`basis='user'`), which has no CLI gesture
   today. **Not chosen here.**
2. **D2.** Sites B, C, D and E have no ratified prompt text, and `84` §1 forbids an agent authoring
   one. Until ratified, the LLM cannot decide grouping, placement, residuals or templates, whatever
   is wired.
3. **Rules that can outrank the model.** `00`:42 and `cli.contradicts_stronger` let direct and
   rule-validated facts contradict an LLM fact; `00`:43 requires score and margin before a facet
   fills; `00`:114 applies the two-condition rule after the model's verdict; `00`:110 keeps unique
   direct matches away from the model. The corrected purpose statement says the model decides.
   These are `00`'s own words, so they are kept active and flagged, not resolved.
4. **Deterministic fact producers and fixed template levels as deciders.** `WORK_TYPE_VOCABULARY`,
   `SUBJECT_RULE`, `DATE_PATTERNS` and `folder_levels_for` are sanctioned by `00`:41 and §5.4 and
   forbidden by constitution rule 1 ("no sorting rules"). Which wins decides whether Phase 1 keeps
   them as pre-filters that narrow the model's question, or demotes them to `possible` clues.
5. **Safety-rule breaches, different severity from ordinary bugs.** (i) One protected vaccination
   record was placed on the owner's corpus in both scorecards. (ii) Eight protected files are
   extracted before classification; `00`:185 protects against cloud prompts and automatic moves,
   and the standing "never read" rule names containers, so whether local extraction before
   classification is a breach is yours to say. (iii) An extensionless file vanishes from the
   freeze block (`94` F22). (iv) The "5 files sent" sentence (C2) is a consent-screen untruth.
6. **Single situation per corpus.** `--situation` and `--label` are required input for the whole
   folder; `00`:67 has the engine propose areas. Minimal human input and `00` agree; fixing it
   changes the CLI contract and is a phase, not a patch.
7. **The semantic-recognition patch is uncommitted** in the shared working tree and its thresholds
   are measured numbers (`SEMANTIC_FLOORS`, `SEMANTIC_SIMILARITY_THRESHOLD`). Commit, keep as
   machine state, or drop is a decision this diagnosis did not take.

---

## 10. Phased repair plan (Step 4)

Dependency-ordered. Each phase has a test a person can run and watch. "Should work" is never a
completion criterion.

### Phase 0: one file all the way through, by hand

**Blocked on D1.** The pass test is the same whichever remedy is chosen.
Files: `privacy/denial.py`, `privacy/gate.py`, `cli.fact_call_authorities`, `cli._print_fact_pass`.

```
mkdir -p /tmp/p0/corpus && cd /tmp/p0/corpus
printf 'PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee.\n' > 'PHYS 1401 syllabus.txt'
printf 'Introduction to Organic Chemistry\nTutorial sheet 4, Michaelmas term\n' > tutorial4.txt
cd "/Users/jy/GRAPH AGENT"
python3 src/cli.py /tmp/p0/corpus --situation academic.coursework --label Coursework \
  --database /tmp/p0/plan.sqlite --enable-cloud
sqlite3 /tmp/p0/plan.sqlite "select count(*) from llm_response; select count(*) from llm_verdict;
  select field_key, reliability_state from file_facts where reliability_state='llm_supported';"
```

Pass: `llm_response >= 1`, `llm_verdict >= 1`, at least one `llm_supported` fact on a named file,
and the "Facts from a model" line prints the true sent count. Fail: any `llm_refusal` row for a
classified ordinary file, or the sentence counting refusals as sent.

### Phase 1: fix wiring, not logic

| Item | Files and functions | Pass/fail test |
|---|---|---|
| 1a. Derive P9's `active_schema_for` from the situation's `role_bindings` via `production.folder_levels_for` | `cli.run.downstream` (`GroupingKnowledge`), `production.py` | A synthetic file whose only fact is a model-written `project` seeds a P9 group (`groups` table has a row with `field=project`) |
| 1b. Send the situation's `deferred_readings` in the site-A dossier under a key the ratified template lists, or route to D2 if it needs a new key | `model_facts.build_fact_request`, `llm_harness.dossier`, `recognition.rules` | The stored `llm_dossier` payload for `academic.coursework` contains the "programme or module name" reading verbatim |
| 1c. Inject sites C and D from `model_placement.model_path_injections` in `cli.run.placement_inputs`; inject site B via `grouping.ModelCallAuthorities` in `downstream` (needs D2) | `cli.run`, `model_placement.py`, `grouping/p8_seam.py` | With a ratified prompt, `HW 3.txt` (homework with no course code beside a syllabus that has one) produces an `llm_dossier` row with `call_site='C_placement'`, not `no_supported_destination` |
| 1d. Wire `readers.signatures` into `cli._detect_format` | `cli._detect_format` | An extensionless plain-text file is routed, read, and appears in the freeze block |
| 1e. Make `_print_fact_pass` count only outcomes that carry a response | `cli._print_fact_pass` | The R6 corpus prints "0 files sent" under refusal and "N files sent" only when `llm_response` has N rows |
| 1f. Make `cli.model_route_permitted` and `Gate.release` agree on who is withheld and why | `cli.py`, `privacy/gate.py` | A withheld file shows one reason on screen and one `unresolved` row, never a refusal that a permit contradicts |
| 1g. Record stop-rule outcomes | `grouping.pipeline` → `grouping.store.record_stop_rule_outcome` | A corpus with a seed conflict writes one `stop_rule_outcomes` row |

### Phase 2: fix the input side

- Give `Gate` a `measure_tokens` callable and seed `model.max_dossier_tokens_per_call` with one
  value equal to the request's (`cli._bootstrap`, `cli.fact_call_authorities`). Test: a synthetic
  file with 60 long observations is refused `dossier_over_budget` above the ceiling and released
  below it; the refusal names the measured count.
- Replace `unreduced_fits=True` in `model_facts._call_dependencies` with a measured answer, or
  record that the ladder has one rung. Test: `reduction_rung` on the stored dossier is `unreduced`
  only when the measured count fits.
- Verify repeat-run spend. Test: run Phase 0 twice on an unchanged folder; `llm_response` count
  must not double for a file whose fields were all declined, and the run must not crash on the
  dossier primary key.
- Run `python3 -m tools.groundtruth --corpus .groundtruth/corpus --labels .groundtruth/labels.json
  --out <dir> --situation academic.coursework` with the `cloud` word once D1 is settled. Pass:
  the `MODEL` line shows `dossier` equal to the number of readable, unprotected files, and every
  file without a dossier has a named pre-call abstention. Record the number beside §10.1.

### Phase 3: fix the output side

- Prove a site-A fact reaches a folder: after Phase 1a, re-run ground truth cloud and require
  `FIELDS filled correctly` above 1 of 92 and `SORTING exact` above 0 of 41. Record both numbers.
- Prove a site-C verdict changes an outcome: the `HW 3.txt` case places into `Coursework/PHYS1401`
  or its parent with `confidence_class=context_supported_group_match` and `requires_review=true`.
- Replace `refinement_for`'s first-person reason and `approve_plan`'s `user_edited_label` with
  provenance that names `SURFACE_UNATTENDED`. Test: no row in `tree_nodes` or the acceptance table
  claims a user act on an unattended run.
- Fix C14: add a reason code for "model path not supplied" and "model refused" so the abstention
  sentence names which one happened. Test: the same file under consent off, consent on with no
  key, and consent on with a refusal prints three different reasons.

### Phase 4: re-widen to the full pipeline

- Run the 208-situation loop of `tools.groundtruth` and one 5,000-file folder with cloud on.
- Seed P5 and P6 ceilings in `_bootstrap`; bind `budget_exhausted` in both resolvers to
  `llm_harness.budgets`; wire `extractors.budgets.extraction_counts` into the report.
  Test: a run capped at 20 calls prints "N files deferred after the model limit", those files carry
  `budget_deferred` with a `deferred_stage`, and none receives a cheaper placement.
- Measure wall time, database size and call count per 1,000 files; record them beside
  `PDF_PAGE_CEILING` and `SPREADSHEET_CELL_CEILING`'s existing measurements.

### Phase 5: customizability pass

- Build the horizontal pass: per-branch situation proposal from the detector's per-file candidates
  feeding `questions.triggers.question_for_situation`; group review before design
  (`review_and_accept` becomes a surface, not a merge); the two missing residual dispositions.
  Test: the owner's corpus run with no `--situation` prints candidate top-level areas with file
  counts; `--answer branch:<name>=<situation>` changes only that branch's levels on the next run
  and the report shows a diff; `--residual "Temporary Screenshots"=leave-in-place` moves nothing
  and says so in the freeze block.
- Only after Phase 3's numbers exist, decide §9.4 with measurement: run with the three rule
  producers demoted to `possible` and compare `SORTING exact` against the rule-first run.

---

## 11. Measurements appendix

### 10.1 Ground truth, `academic.coursework`, owner's 199-file corpus, offline

| Line | 2026-09-04 21:51 (`.groundtruth/after-fields`) | 2026-09-05 today, HEAD (`scratchpad/gt-head`) |
|---|---|---|
| Protected not marked / opened / placed | 6 / 8 / 1 | 1 / 8 / 0 (corrected in `104` §8) |
| Sorting, 41 known-answer files: exact | 0 (0.0%) | 0 (0.0%) |
| right parent, wrong leaf | 5 (12.2%) | 6 (14.6%) |
| wrong | 1 | 0 |
| not placed | 35 (85.4%) | 32 (78.0%) |
| 29 "ask the person" files not placed | 28 | 29 |
| Fields filled correctly / wrong / not filled | 1 / 17 / 74 of 92 | not re-read |
| Classified / unclassified | 90 / 109 | 104 / 95 |
| Model calls | 0 (offline) | 0 (offline) |

The tokeniser fix in `a6502ef` is the visible change: protected marking improved from 2 of 8 to 7
of 8. Placement did not move.

### 10.2 Synthetic runs (scratchpad, this session)

- Offline, 4 files: `Coursework/{essay,lecture,syllabus}`; `Columbia Essay.txt` filed under
  `Coursework/essay` by `work_type` (a college-application essay under Coursework, the
  single-situation defect in miniature); `HW 3.txt` abstained.
- Freeze → apply → undo: moved, restored, SHA-1 `6fe5da74...` identical before and after.
- Stale precondition: a file edited after freeze was refused with "This file changed after the
  preview."
- Cloud, 5 files: 0 dossiers, 5 refusals. Refusal text for the four classified files:
  "carry the handling class 'personal_non_sensitive' on a basis of 'detector_no_safety_evidence':
  the detector recognised the file from its own words and matched no term for finance, identity,
  medical or legal material anywhere in it. Finding no safety evidence is not the same as
  establishing that there is none"; remedies offered by the gate: `use_local_model`, `classify`,
  `review`. For the unclassified file: reason `unclassified`, remedies `classify`, `defer`,
  `review`. None of the remedies reaches the screen.

### 10.3 Classification basis on the owner's corpus

| basis | 2026-09-04 DB | today's DB |
|---|---|---|
| `detector` (passes the cloud gate) | 78 | 44 |
| `detector_no_safety_evidence` (denied) | did not exist | 41 |
| `safety_domain`, protected (denied) | 12 | 19 |
| unclassified (denied) | 109 | 95 |

### 10.4 Suite

`python3 -m pytest tests/ -q -p no:randomly`: 8021 passed, 19 skipped, 21 xfailed, 286.8 s.
`tests/p7/test_p7_no_safety_evidence.py` asserts the denial in C1.
`tests/integration/test_cli_cloud_announcement.py` asserts the consent sentence, not a call.
No test drives `cli.main` through a model response; the model half is exercised only by fixtures
that construct `ModelClient` and `PipelineInputs` by hand (`94` F15 still holds).

---

## 12. Corrections to earlier planning documents

- `84` §2b "the model is wired": true of the transport and site A's injections; false of
  reachability since `fd68cb6`. The route exists; the gate closes it.
- `101` "the model was never wired up: it is wired and it works": measured before `fd68cb6`; no
  longer reproducible on HEAD.
- `102` §4 "harness shipped and wired; asked for the wrong fields": the wrong-fields half was fixed
  by `9351788` (constitution rule 3); the wired half is now refused at the gate.
- `85` §9 "no model transport": expired (as `85` §15 itself records); the live reason is D1 plus D2.
- `94` §0 item 1 "`--apply` and `--undo` over a real move were not run": run today (R3-R5), both
  work, stale detection works.
- `86` §6.1 "the product proposes a move and can never make one": closed; P12 is reachable and
  moves files.
- `94` F1 (one protected file locks the whole branch): not reproduced today on a corpus without a
  protected member; not re-tested with one, so it stands as reported.

---

*End of diagnosis. Produced by Claude Fable 5.1. No file in `src/`, `tests/` or `planning/` other
than this one was written, and nothing was committed.*

---
---

# PART II — Onboarding, structural questions, and the customisation gestures

**Added 2026-09-05 by Claude Fable 5.1, same method as Part I: read the governing design, trace
every gesture from the flag to the record to the consumer, run each gesture on a synthetic corpus,
read the database afterwards.** The design for this area is not in `00`; it is
`66-FIND-FILE-AND-ONBOARDING.md` Parts II-V (§7-§23), amended by `80` (role matcher ruling),
`81` §14 (review-action ownership ruling), `64` (user-edit overlay) and planned in `75`. `00`:261-281
(§8.7 correction learning, §8.8 versioned plans) is the part of `00` these extend.

## 13. What was read and run for Part II

Read: `66` §7-§23 in full; `75` §1-§2 and §6-§7; `80` §1, §3-§5, §7; `81` §1, §4, §13-§14; `64` §1-§5;
`src/questions/` (registry, triggers, store, effects, explanation, roles, proposal, role_report,
vocabulary, records); `review_gestures.py`; `review_surface/vocabulary.py`; `review_run/`;
`cli.apply_answers`, `cli.apply_rejections`, `cli._raise_blocked_questions`,
`cli.folders_nothing_could_be_read_from`, `cli.nesting_chooser`, `cli.main`'s gesture branches.

Run (all offline, synthetic corpora in the scratchpad, database read back after each):

| # | Gesture | What happened |
|---|---|---|
| G1 | `--answer branch:Coursework=keep-as-it-is` | Tree collapsed to one node; every previously "ready to file" file became "waiting for you to say what these are". The option text says "Nothing moves and nothing is created"; it does not say the branch stops accepting placements |
| G2 | `--explain branch:Coursework` | Printed what it controls, where it applies, when supplied, "you confirmed it", and the four ways to change it. Correct |
| G3 | `--describe-role 'me=I teach one course and I am doing my own PhD'` | Sentence stored; the full closed list of 23 layouts printed in random order. No shortlist: nothing read the sentence |
| G4 | `--declare-role me=academic` | Recorded, shown in the role panel with change and revoke lines. Placement outcome unchanged (as `94` F5 measured) |
| G5/G9 | `--reject 'Lecture 08.txt:work_type=lecture'` | **Refused: "names 2 files in this plan"**, listing the same path twice. The file had been edited between runs; P3 kept the old version as `scan_state=superseded_content` and the gesture matched both |
| G6/G10 | `--residual "Review Later" --send-set "Not yet placed=Review Later" --freeze` | `residual_set_decisions` gained a row; `review_actions` stayed at **0 rows**; the one file in the set (unclassified) was not filed and the freeze held it as "nothing has looked inside this one yet" |
| G7 | Corpus with an unreadable subfolder (`scans/*.bin`) | The unreadable-folder question fired with three destinations including "leave in scans"; the role moment printed the `--describe-role` invitation |
| G8 | `--answer branch:Coursework=revoke` | Printed "What changing branch:Coursework does to this plan" with three consequences marked "Not worked out here" (placement, protected area, filing policy). No draft plan version was opened |
| G11 | `--answer home:scans=Coursework --freeze` | The two unreadable files moved to "Would go into Coursework, once you say what these are": the answer reached P11's `chosen_by_user` but the unclassified hold still outranks it, so nothing froze |
| G12 | Corpus mixing academic and research vocabulary with a course code | No tied-reading question fired; only the nesting question. The `reading.organization` kind remains unobserved on a live run (also unobserved by `94` §0) |
| DB | `files` after G5 | Two rows for `Lecture 08.txt`: one `included`, one `superseded_content`; **the superseded one was placed and frozen in every freeze** (`move_plans` holds three plans for it) |

## 14. Target design for this area, extracted from `66`, `80`, `81`, `64`

1. **Onboarding is not a questionnaire** (`66` §12, §20). First run indexes and finds; it asks
   nothing personal. A question is asked only when a specific decision is blocked, names the
   decision it unlocks and what it will not change, offers skip and not-applicable, records its
   scope, and stays editable and revocable.
2. **Structural versus contextual** (`66` §13). A structural answer may activate a schema, gate a
   template, resolve the person's role, allow or prohibit a category of folder label, or require
   review. A contextual answer may affect only ordering, examples and wording. A contextual answer
   that changes a folder, a placement, a privacy state or a move is a defect.
3. **Ask only when needed** (`66` §14): the question names the visible context ("We found files
   connected to Columbia") and the precise consequence, with "not about me" and "skip" first-class.
4. **Other people** (`66` §15): names only inside an explicit protected household workflow with a
   user-selected relationship; person-named folders for self and dependants only; never for
   clients, patients, employees, candidates, students.
5. **The role matcher** (`66` §16, `80`): multiple roles, each with scope and period; free text maps
   to the closed schema list cautiously; four outcomes (exact, multiple, unmatched, skipped); raw
   wording stored. `80` rules Option 2: a **local** model proposes a shortlist that reads as having
   heard the whole sentence (R4), the person confirms once (R2), triggered by the first genuinely
   ambiguous file and never at first run (R1), one box not a form (R3), "none of these" is normal
   (R5), roles are an editable panel (R6), no presentation may re-introduce ranking (R7). Option 1
   (the bare closed list) is the fallback when no local model exists.
6. **Re-running answers** (`66` §17, `00`:280): editing a structural answer creates a draft plan
   version and shows a meaningful diff; nothing renames, reclassifies or moves as a consequence.
7. **Corrections and learning** (`00`:261-264, §8.7): every review gesture becomes a scoped local
   learning record with negative feedback stored beside its evidence; `81` §14 rules that P13 owns
   the name of every gesture and its eighteen must grow to cover the six the design names.
8. **User edits outlive the catalogue** (`64`): a rename is keyed on `(schema, role_ref, field_ref)`,
   applied after routing and gating, never overwritten by a library upgrade; a frozen tree records
   the release that built it.
9. **Automatic filing** (`66` §7-§11, §19): a named policy binding source, destinations, eligibility,
   evidence standard, cadence, exclusions, collision, undo period and revocation; first run always a
   dry run; distinct refusal sentences; ships last.

## 15. The built gesture layer, traced

| Flag | Function | Record written | Consumer that reads it |
|---|---|---|---|
| `--answer Q=OPT\|skip\|revoke` | `cli.apply_answers` → `questions.store.record_answer`; refuses an unknown question id | `structural_answers` | `branch:*` → `store.gated_template` → `cli.nesting_chooser`; `home:*` → `store.chosen_destination` → `placement_inputs.chosen_by_user`; `reading.organization:*` and `role:*` → `store.activated_schemas` → `Detector(settled_by_user)` (tie-break only) |
| `--explain Q` | `questions.explanation.explain_question`, `render_explanation` | none | screen |
| `--describe-role NAME=WORDS` | `roles.apply_descriptions` (free-text answer on `role:NAME`), then `proposal.propose_roles(propose=None)` | `structural_answers` (raw wording kept) | screen only: the full 23-item list, shuffled (`cli._unranked`). Nothing reads the sentence |
| `--declare-role NAME=LAYOUT\|not_listed\|skip` | `roles.apply_declarations` → `declare_role`/`skip_role` | `structural_answers`, role panel | `activated_schemas` → detector tie-break |
| `--reject FILE:FIELD=VALUE` | `cli.apply_rejections` → `facts.learning.reject_claim` | `file_facts` rejected row | P9, P11 and `cli.run.evidence_for` skip `rejected`; P8 `assess_call` suppresses an equivalent call |
| `--residual NAME` | `cli._validate_residuals` → `ResidualChoice(PHYSICAL_DESTINATION)` | tree node | P11 |
| `--send-set SET=AREA` | `placement.residual.act_on_residual_sets` | `residual_set_decisions`, `placement_decisions` | freeze. **No `review_action` is written** |
| `--freeze` | `apply_run.freeze` + `apply_run.approval.approval_writer` → `review_surface.approvals` | `move_plans`, `review_approval` | `--apply` |
| Questions raised | `cli._raise_blocked_questions` (tied readings), `cli.nesting_chooser` (branch), `cli.run._home_questions` (unreadable folder), `role_report.role_declaration_is_due` (the role moment) | `structural_questions` | the report |

Five question kinds are registered (`questions.registry`): reading, nesting, situation, role,
home. Four are asked on a live run. **`SITUATION_KIND` is registered with a reader nobody calls
and a trigger nobody fires.**

## 16. Inventory A: designed but unbuilt (this area)

| Design item | Evidence |
|---|---|
| `80` Option 2: a local model reads the self-description and proposes a shortlist (R4) | `cli.main` passes `propose=None` to `proposal.propose_roles`; no local model client exists in `src/`; G3 printed all 23 layouts unranked, which is Option 1, the fallback |
| `80` R6: an editable role panel | The panel prints; editing is re-typing `--declare-role NAME=...`; there is no P13 surface |
| `66` §13 consequence 3, per-branch situation (`75` B1/B2) | `question_for_situation` and `selected_situation` exist; neither is called (R1 xfail). `--situation` stays one string per disk |
| `66` §13 consequence 4, permitted person label (`75` C1-C6) | `permits_person_label` appears nowhere in `src/`; held on owner questions Q1, Q3, Q4 |
| `66` §13 consequence 5, require review | Deliberately absent until P13 has a queue (`75` B3) |
| `66` §15 protected household workflow and relationship vocabulary | Not built; held on `75` Q1 |
| `66` §17 / `00`:280: an answer change opens a draft plan version with a diff (`75` A4/A5) | `questions.effects.draft_for_answer_change` has no caller outside its module; G8 printed a diff-shaped block with three of its consequences "Not worked out here" and opened no draft |
| `64` label overlay and upgrade contract | `record_user_level_edit` has no writer (R1 xfail); `tree_design/records.py` carries no `release_id`; a rename cannot survive a re-route |
| `66` §7-§11, §19 automatic filing ("Keep this folder organized") | No `FilingPolicy`, no policy schema, no dry-run driver anywhere in `src/`. Correctly last by `66` §22; noted so nobody reads `--apply` as it |
| `66` §14's worked question ("Which describes your relationship to Columbia?") | The reading question exists in code but needs a `subject` value and a detector tie; it did not fire on any corpus tried here or in `94` |
| `81` §14: P13's eighteen must grow by six approved names | `review_surface.vocabulary` already carries the six (`exclude_from_packet`, `rename`, `merge`, `split`, `reorder`, `set_refinement_disposition`, plus `create_custom_template`); no surface collects any of them |

## 17. Inventory B: built but disconnected (this area)

| Mechanism | Where the path stops |
|---|---|
| `review_gestures.py` (P13's write side for `--send-set`, added in `4fc44a6` whose message says the gesture "recorded nothing") | Imported by nobody; measured: `review_actions` has 0 rows after a real `--send-set`. The fix shipped as a module with no caller |
| `review_surface.collect`, `store.record_action`, `routing.route` | Reached only from other unreached P13 modules (`bulk`, `consent_surface`, `learning_view`, `move_permission`, `versions_view`) |
| `questions.effects.draft_for_answer_change` | No caller; `changed_answer` and `diff_for_answer_change` are called by `cli._print_answer_effects`, the draft is not opened |
| `questions.triggers.question_for_situation`, `store.selected_situation` | Registered kind, no trigger, no reader in `cli` |
| `questions.proposal.SelfDescriptionSending`, `sending_notice` | `80` §8's suspension path; nothing to send to |
| `database_agent.learning.reset_preferences` | Its caller is P13's `reset_learning` gesture, which has no surface |
| `review_run.learning`, `review_run.progress`, `review_run.review` (the screens a person reads) | Only `review_run.structure` is imported (by `apply_run.freeze`) |

## 18. Inventory C: built, wired, and wrong (this area)

| # | Behaviour | Mechanism | What it breaks |
|---|---|---|---|
| C15 | **A file edited between runs leaves a ghost that is placed, frozen and blocks gestures.** `files` holds both versions; the `superseded_content` row was placed and frozen in every later freeze (three `move_plans` rows for it), the report counted "4 files" in a 4-file folder with one unfiled, and `--reject` refused with "names 2 files", printing the identical path twice as the way to disambiguate | `cli.run` (`corpus_roster`/`file_names`), `cli.apply_rejections`, `apply_run.freeze` read `files` without filtering `scan_state`; P3 sets `superseded_content` and nothing downstream honours it | `00`:135 (new content is a new version), `84` §6 (what the screen tells a person to type has to be true: the disambiguation offered is impossible) |
| C16 | **`--send-set` records no review action.** The design's audit trail for a person's gesture (`81` §1, `00`:136) is empty | `placement.residual.act_on_residual_sets` writes P11's row; `review_gestures` is unreached | `00`:284 reconstruct what the user approved; `81` §14 |
| C17 | **A `keep-as-it-is` answer silently makes every file in the branch unfilable**, and its option text does not say so | `cli.choose_option`'s no-split option leaves the branch stating no values, so P11's direct-fact channel cannot reach it | `66` §13: a structural answer must show what it controls; the `--explain` output says "Nothing moves and nothing is created" and omits "and nothing can be filed here" |
| C18 | **The description gesture reads as a shortlist and is a directory listing.** 23 options in random order after a sentence the person typed; R3 and R4 are not met and the screen does not say a model was absent | `cli.main` `propose=None`, `_unranked` | `80` R3, R4, R5 |
| C19 | **The role moment fires on abstentions that no role can resolve**, while `94` F5 measured that a declared role changes nothing for them | `role_report.role_declaration_is_due` (any open non-branch question) vs `triggers.py`'s own docstring | `80` R1 "genuinely ambiguous file" |
| C20 | **The nesting question's counts drop the first level of the chain** and the verb does not agree ("1 file sit") | `questions.triggers.question_for_nesting`, `cli._nesting_choices` | `66` §14, `00`:95 |
| C21 | **An answer on an unreadable folder cannot take effect** while the unclassified hold outranks it (G11): the person answered the one question the product asked and the files still do not freeze | `placement.pipeline.place_file` `_user_chose` vs the P7 `blocked_pending_user` hold in freeze | `66` §12 "explain the exact decision it unlocks"; the question promised a filing it cannot deliver |

## 19. Null decisions in this area, tagged

- **The person's role is decided by nobody.** `--situation` is typed once per disk (missing piece);
  the role matcher's model half does not exist (missing piece, needs a local model, D1's remedy (b)
  would supply it); a declared role only breaks detector ties (wiring: consequence 3 unbuilt).
- **The residual set decision (`66` §7.6, `00`:123) is one gesture with one disposition**; the two
  other answers cannot be given (design mismatch with `00`:121).
- **Learning from corrections** (`00`:261-264) is limited to `--reject` on a fact; group, label,
  destination and residual corrections have no gesture and no record (missing piece; P13).
- **Contextual answers do not exist**, so the structural/contextual boundary is untested: every
  answer is structural (`CONTEXTUAL` is declared in `questions.vocabulary` and never assigned).

## 20. Plan additions for Part II

Slot into Part I's phases; each has a runnable test.

- **Phase 1 additions (wiring).**
  1. Filter `scan_state='included'` in `production.corpus_roster`, `cli.file_names`,
     `cli.apply_rejections` and `apply_run.freeze`. Test: edit a file between two runs; `--reject`
     by filename succeeds, the freeze block counts the folder's real file count, `move_plans` holds
     no row for a `superseded_content` file.
  2. Call `review_gestures` from the `--send-set` path. Test: one `--send-set` writes one
     `review_actions` row with `surface=residual_set`, `action=accept_bulk`.
  3. Call `questions.effects.draft_for_answer_change` from `cli.apply_answers`. Test: changing a
     confirmed answer writes a `plan_versions` row in `draft` state and the report names it.
  4. Make the `keep-as-it-is` option text state its consequence, or make the no-split branch state
     its shared values as the split branch does. Test: G1's corpus keeps "3 ready to file" under
     `keep-as-it-is`, or the option reads "and nothing can be filed into it".
  5. Resolve C19 one way: either the role moment fires only when an open question names a role
     consequence, or the abstention sentence stops saying the person is waited on.
- **Phase 3 addition.** Let a `home:*` answer satisfy the unclassified hold, or print at the
  question that it cannot. Test: G11 freezes the two files or the question says why it will not.
- **Phase 5 additions (customisability, in `66` §22's order).**
  1. Per-branch situation: fire `question_for_situation` from the detector's per-file candidates
     and read `selected_situation` in `cli.run` per branch. Test: the owner's corpus with a
     `code.*` subfolder gets two situations without two runs.
  2. Role matcher Option 2 once a local model exists (D1 remedy (b)): pass `propose=` a local
     client; test R4 with the sentence in G3 producing a shortlist containing both `academic` and
     `research`, and R7 with a randomised order test.
  3. Label overlay (`64`): key on `(schema, role_ref, field_ref)`, apply after routing; record
     `release_id` on the frozen tree. Test: rename `Course` to `Class`, re-run, the label survives.
  4. The six approved P13 gestures get a collecting surface and a receiver each (`81` §14). Test:
     each writes a `review_actions` row and its receiver's `apply_review_action` accepts it.
  5. `66` §15 household workflow, after `75` Q1/Q3/Q4 are ruled.
  6. Automatic filing last, and only as `66` §19 specifies: a named policy, dry run first.

## 21. Owner decisions for Part II (unresolved)

- `75` §6 Q1-Q7 stand unanswered: the relationship vocabulary; the role-declaration guidance
  (`80` §6 keeps the shortlist wording and the confirmation sentence as prompt-adjacent text the
  owner approves); whether an answer may narrow gate C2 per branch; what "deliberate household
  workflow" means on a command line; whether an edited answer opens a draft automatically; how
  long a revoked name is kept; whether a new question kind needs approval.
- `80` §8's suspension of the always-local rule for self-descriptions expires "before anyone who
  is not Joseph uses this"; nothing enforces the expiry.
- Whether `keep-as-it-is` should mean "keep the branch and still file into it" (a shape decision
  about `00`:99's "keep this branch as it is").
- Whether an unreadable-folder answer (`home:*`) is a classification act for §8.4's purposes, so
  that the person's explicit answer can lift the unclassified hold (C21).

## 22. Corrections to earlier documents from Part II

- `4fc44a6` "the gesture the report tells a person to type recorded nothing": still true after the
  commit; the writer it added has no caller.
- `84` §2b "the role matcher became reachable": the flags and records are reachable; the matcher
  (a model proposing from the sentence) is not built, so what runs is `80`'s Option 1 fallback.
- `85` §4.2 "§5a, recording the release, landed": **confirmed, and my first draft of this line
  was wrong.** The release is carried as `FreezeRecord.catalogue_release_id` in
  `tree_design/freeze.py`, not on `records.py`. `64` §5b-§5e (the upgrade contract) remain unbuilt.
- `94` F5's conclusion (a declared role changes nothing for abstentions) is confirmed and extends to
  the description gesture.

*End of Part II. Produced by Claude Fable 5.1. Still nothing committed; the only file written in
the repo is this one.*

---
---

# PART III — Start here next session

**Added 2026-09-05 by Claude Fable 5.1 after Parts I and II.** This part exists so the next
session spends its first ten minutes on decisions and its remaining time on fixes, rather than
re-deriving either.

## 23. Three more measurements taken after Part II

1. **The uncommitted on-device semantic channel runs and changes nothing a person sees.** With
   `--semantic-model ~/.graph-agent/models/minilm` on the five-file corpus: 2.5 s wall, 3 groups
   and 14 `group_edges` written, placement outcome byte-identical to the run without it. Cause:
   `cli.run.evidence_for` hands P11 `semantic_neighbours=()` and `related_files=()`, so the
   neighbours P9 retrieves never reach the placement dossier or the node-local graph (`00`:107-109
   names full-text and OCR embeddings as a retrieval channel for sparse files). Record as **C22,
   wiring bug**. Also `HW 3.txt` is below `SEMANTIC_MIN_CHARS` (100), so the recogniser is silent
   on exactly the sparse file `00`:56 uses as its example.
2. **The reachability census today:** 298 public mechanisms unreachable from `cli.main` across 112
   modules, population 1,665. By package: `review_surface` 114, `facts` 26, `mutation` 26 (ten in
   `retention`), `eval_harness` 22, `tree_design` 22, `privacy` 16, `llm_harness` 13, `grouping` 10.
   The count rises as parts land; re-measure with the script in `85` §1.
3. **Dossier dedupe:** `llm_harness.store.record_dossier` now dedupes identical bytes onto one row,
   so a repeat run no longer crashes on the primary key. Whether the transport is still paid a second
   time for a dossier already answered remains unmeasured; `run_call` does no verdict lookup before
   `transport.issue`, so read it as "probably re-spent" until Phase 2's test says otherwise.

## 24. What this session left in the repo

- `planning/103-FABLE-5.1-DIAGNOSIS.md` (this file).
- `tests/integration/test_103_diagnosis_backlog.py`: **seven strict xfails**, each watched failing
  for the reason its marker states, none erroring:
  C15 twice (ghost version blocks `--reject`; ghost version receives a move plan), C16 (`--send-set`
  writes no review action), C7 twice (stored ceiling 8 vs 4000; gate has no `measure_tokens`),
  C1/D1 (the no-safety-evidence cloud denial), C17 (`keep-as-it-is` un-files the branch). Run:

```
python3 -m pytest tests/integration/test_103_diagnosis_backlog.py -q -p no:randomly -rxX
```

  A test that starts passing turns the suite red; remove its marker in the commit that fixes it and
  strike the finding here. Not written as tests, because they need a network or a decision: C2 (the
  "N files sent" sentence), C3, C6, C14, C18-C21, C22.
- The memory file `graph-agent-resume-point.md` points here.
- Nothing committed. Untouched: the uncommitted semantic patch in `src/cli.py`.

## 25. The two decisions that gate everything, put plainly

**D1: how does an ordinary file reach the model?** The gate names three doors. Whichever is chosen,
Phase 0's test in §10 is the pass criterion.

| Option | What changes | Cost | Consistent with |
|---|---|---|---|
| (a) Rule that basis `detector_no_safety_evidence` satisfies §8.4's precondition for a cloud call when the file has releasable evidence | `privacy.denial.no_safety_evidence_denies` returns False for cloud; `tests/p7/test_p7_no_safety_evidence.py` is rewritten | one function, one test | constitution 2; reverses `96` §20 |
| (b) Wire a local model, which the gate already permits on both denial reasons | a local `ModelClient` from `readers.model_ollama` routed for A_fact under `local_model` mode; `unclassified_permits_local` is already True | a running local model on the machine; `83` routing gains a locality | `00`:189-193, `96` §20, `80` (the role matcher needs the same local model) |
| (c) A user-set classification (`basis='user'`) | a CLI gesture that reclassifies a file or folder | a new question kind, per file or folder | `00`:185, but re-introduces per-file human input |

Recommendation, held separately from the evidence: (b) satisfies every ruling at once and unblocks
the role matcher too, but only if a local model of usable quality exists on this machine; if not,
(a) with the evidence condition is the smallest change that honours constitution 2 without
touching protected material.

**D2: prompt text for sites B, C, D and E.** Until ratified, the LLM cannot decide grouping,
placement, residual review or templates however much is wired. `82` §0 records how A_fact was
ratified; the same route is open for the other four.

## 26. Order of work for the next session, with the measurement at each step

1. Put D1 and D2 to the owner first. Nothing below Phase 0 moves without D1.
2. Phase 0 (§10) on the five-file corpus. Pass: `llm_response ≥ 1`, one `llm_supported` fact, the
   "sent" count true. Then the same on `.groundtruth/corpus` with the `cloud` word and record the
   `MODEL` line beside §10.1's zeros.
3. Phase 1 wiring items, in this order because each is one seam and each has a red test or a
   one-line check: C15 (roster filter), C16 (`review_gestures` caller), C7 (one ceiling,
   `measure_tokens`), C2 (the sentence), C6 (`active_schema_for` from `role_bindings`), C22
   (`evidence_for` reads P9's neighbours), the `needs_llm` readings into the dossier.
4. Re-run `tools.groundtruth` offline and cloud; require `SORTING exact` above 0 of 41 and
   `FIELDS filled correctly` above 1 of 92 before touching anything in Phase 4 or 5.
5. Only then the customisation work in §20, in `66` §22's order.

## 27. Two rules for whoever picks this up

- Every claim in this document that matters was made by running the product and reading the
  database. Do the same before changing it: `84` §5 and constitution rule 4 both say so, and Part II
  §22 records one place where I broke that rule myself and had to correct it.
- The seven xfails are the contract. Do not delete a marker to make the suite green; delete it when
  the behaviour changed and say which finding closed.

*End of Part III. Produced by Claude Fable 5.1.*

---

## 28. RULINGS, 2026-09-05 — the owner answered D1 and D2

Asked and answered in the session that produced this document. Recorded here verbatim so the
next session starts from decisions, not from §25's table.

**D1 — "Both: local first, cloud allowed too."** An ordinary file (no safety vocabulary found,
real evidence present) reaches a LOCAL model by default, and the cloud denial is lifted for such
files as well so `--enable-cloud` can be compared against it. This reverses `96` §20 for the cloud
half and keeps protected material exactly where it was: marked, counted, never sent.

What it unblocks, as tasks with tests:

1. **Local route.** `readers.model_ollama` becomes a real client for A_fact under `local_model`
   mode. On this machine Ollama is installed with `qwen3:8b` (5.2 GB) and `qwen2.5:3b`; `qwen3`
   must run with thinking OFF or it spends its budget the way the DeepSeek reasoner did
   (`cli.TIER_OF_CALL_SITE`'s comment records that measurement). `readers.model_routing` gains a
   local locality and `83` gets an amendment naming it; `cli.model_route` builds the local client
   when Ollama answers and the mode is `local_model` or `hybrid`; `unclassified_permits_local=True`
   is already set, and `privacy.denial.no_safety_evidence_denies` already returns False for local.
   Test: Phase 0's pass criterion (§10) with `--semantic-model` absent and no `--enable-cloud`:
   `llm_response ≥ 1`, one `llm_supported` fact, and the audit row names the local model.
2. **Cloud half.** `privacy.denial.no_safety_evidence_denies` returns False for `locality="cloud"`
   when the file has releasable evidence (the gate holds `rows`; read completeness or the evidence
   count, never the class). `tests/p7/test_p7_no_safety_evidence.py` is rewritten to assert the
   new rule and its negative twin (a file with NO evidence still denied). `96` §20 gets a dated
   amendment pointing here. `announce_cloud_posture` says ordinary files may now be sent.
   Test: `test_103_diagnosis_backlog.py::test_an_ordinary_file_with_no_safety_vocabulary_may_reach_a_cloud_model`
   goes green; remove its marker in the same commit.
3. **Measure both.** `tools.groundtruth` over `.groundtruth/corpus` once local-only and once with
   `cloud`; record the two `MODEL` and `SORTING` lines beside §10.1.

**D2 — "Draft all four now."** Prompt text for sites B (group), C (placement), D (residual) and
E (template) is to be drafted in one round by the route A_fact took — `76` requirements, `82`-style
draft with every line traced, `90`-style bakeoff — for the owner's ratification. An agent drafts;
only the owner ratifies; nothing is installed until ratified (`84` §1 stands).

What each draft needs before it can be ratified, from `84` §3's own blocker list:

| Site | Consumer already built | Also needs authoring |
|---|---|---|
| B group | `grouping/p8_seam.py`, `llm_harness/group_validation.py` (the four questions of `00`:59) | template bytes, `response_schema_bytes`, `shaping_policy_bytes`; the dossier keys `grouping/dossier.py` emits |
| C placement | `model_placement.py`, `placement/pipeline._judge_with_model`, `llm_harness/placement_validation.py` (fifteen checks) | the same three, plus `chosen_node_of` reading the response shape |
| D residual | same wiring as C, `residual_authorities`, the eight actions of `00`:124 | the same three, plus `residual_action_of` |
| E template | `tree_design/template_schema.py`, `llm_harness/template_validation.py`; no live path until `routing.py`'s C3 refusal becomes a request | the same three, plus the strict JSON template schema of `00`:97 |

Order recommended for the drafting session: C and D first (they share wiring and decide where
files go), B next, E last. Every draft is inert until the owner ratifies it, and the tier for
each stays as `cli.TIER_OF_CALL_SITE` records.

*Rulings recorded by Claude Fable 5.1 at the owner's instruction. Nothing implemented yet.*

### 28.1 D2's condition, added by the owner in the same sitting — binding

**"Make sure we do sufficient research and testing for each prompt, to make sure it is the most
optimised for our design."** No site's text is put to the owner for ratification until it has been
through every step the A_fact text went through, and the measurements are attached to the draft:

1. **Requirements first, per site,** in a `76`-style document: every instruction traced to the `00`
   lines that govern that site (B: `00`:55-64; C: `00`:104-116; D: `00`:118-129; E: `00`:97), to the
   site validator's checks (`group_validation`, `placement_validation`'s fifteen,
   `template_validation`), and to the corrected purpose statement. A line with no trace is cut.
2. **The draft traced line by line,** `82`-style: the text, its response schema, its shaping policy,
   and for each sentence the requirement it satisfies. Dossier keys named in the text must be the
   keys the site's builder actually emits (`grouping/dossier.py`, `placement/pipeline._judge_with_model`,
   `tree_design/template_schema.py`), checked by a test, because A_fact's ratified text went stale
   the day a `folder_levels` key was added (`cli.a_fact_prompt`'s docstring records it).
3. **Stress cases before any bakeoff,** `86`-style: the adversarial list at `00`:239 plus the site's
   own failure modes: for B, a group bridged only by a generic hub, two terms of one course, a Duke
   essay inside a Columbia packet; for C, a file with two supported homes, a term the tree does not
   carry, a shared transcript; for D, a boarding-gate screenshot that must not become
   `Travel/Gate B12`, an admissions confirmation that must be returned to the main engine; for E,
   a template that repeats its parent dimension or uses an author as a collector.
4. **A bakeoff of at least two candidate texts,** `90`-style, measured and not argued: on a labelled
   corpus (`.groundtruth/corpus` for C and D; a hand-built multi-course, multi-purpose corpus for B),
   with the local model AND the cloud model under D1, recording per candidate: citation resolution,
   value-in-cited-text, abstention where evidence is insufficient (the `00`:223 metric), the
   site's outcome metric (`SORTING exact` for C, correct membership and outlier detection for B,
   no invented destination for D, no rejected template for E), and cost per call.
5. **Ratification with the numbers attached,** and the two known limits stated the way `82` §0
   states S1 and S2: what the text cannot catch, and what the validator catches instead.
6. **After ratification, a strict test per site** that the installed bytes match the ratified digest
   and that the dossier keys the text names are the keys the builder emits.

Order stays C and D, then B, then E. "Most optimised" is measured at step 4 and nowhere else; a
candidate that reads better but scores worse loses.

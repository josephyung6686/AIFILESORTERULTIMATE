# asrtra digniositce — 2026-09-05

## 1. Target architecture summary

The source of truth is [00 — Database Agent Product Design](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:1>), read end to end. Your corrected purpose statement takes precedence over its historical rules-first passages:

**An LLM is the decision engine that sorts files, with minimal human input and maximum customizability.**

This is not permission to discard provenance checks, privacy controls, user choices, or the frozen tree. It changes who makes semantic category, naming, membership, and placement decisions.

### The target architecture, named for reference below

| Stage | Intended responsibility and boundary |
|---|---|
| **TA1 — Select and extract** | The user selects sources, candidate roots, exclusions, and cross-folder permissions. Roots are context, not move permission. Read supported files once per content version into common, located evidence in local SQLite. Preserve existing curated structures. Extraction records what is present; it does not decide a destination. |
| **TA2 — Interpret file evidence** | Deterministic parsing supplies observations, explicit identifiers, dates, duplicates, and plausible domain candidates. **A_fact** receives a bounded, privacy-approved evidence packet, relevant schema/field meanings, and existing evidence/conflicts. It returns cited structured facts or unknown. Under the corrected purpose, candidate-domain detection must not become an unreviewable final semantic category. |
| **TA3 — Interpret groups** | Retrieve a small anchored neighbourhood and construct typed graph relationships. **B_group** receives the grouping basis, anchor files, candidate members, located excerpts, facts, graph relationships, and conflicts. It returns coherence/purpose, a separate include/exclude/uncertain decision for each member, outliers, and—only with supported coherence—a display label/category. Validate and present reviewable groups; context does not become a fabricated direct fact. |
| **TA4 — Design and approve the tree** | Build a shallow horizontal canvas from accepted groups, existing folders, and user-created labels. Then refine branches vertically using data-backed templates. The user can rename, merge, split, nest, reorder, omit dimensions, choose uneven depth, define residual/shared-material policies, and preserve existing folders. An optional **custom-template model call** proposes a strict-schema template, not an already-authorized filesystem mutation. Freeze the approved tree into the only legal destinations. |
| **TA5 — Decide placement** | Retrieve a few frozen destination profiles and relevant file/group/graph evidence. **C_placement** receives those profiles, their meanings and constraints, the target's evidence, alternatives and conflicts. Under your corrected purpose, the model chooses child, parent, approved fallback, or abstention; deterministic scores may aim the question but may not silently answer it. Return a structured decision with evidence, depth, alternatives, confidence/review class and exact legal destination. |
| **TA6 — Resolve residuals and apply safely** | Surface unplaced files as understandable review sets. The user opts into residual AI before **D_residual** receives a bounded packet plus the approved residual library and policy. It may return to a group/node, select an approved broad destination, leave in place, defer, mark protected/unsupported, or abstain. Only separately authorized move plans reach hash/freshness checks, no-overwrite mutation, journaling and conditional undo. No automatic deletion or expiry. |

Design references: [selection and extraction](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:20>), [facts](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:37>), [group dossiers and outputs](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:58>), [tree canvas](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:66>), [post-freeze placement](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:104>), [residual workflow](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:118>).

**Confidence and failure behavior.** Supported direct decisions can become suggestions or policy-authorized move plans. Context-supported conclusions remain distinguishable and may require review. Weak, conflicting or unsupported conclusions stop at a supported parent, remain unknown, or enter visible review/abstention. An unavailable model, withheld evidence, extraction failure and exhausted budget must be distinguishable from a model that considered the evidence and abstained. Confidence does not create permission to move.

**Concrete customizability.** Roots and movement scope; branch names and hierarchy; template selection, order, optional dimensions and depth; canonical values versus display aliases; shared-material policy; user-defined residual areas, placement/keep/review-only behavior and retention-review preferences; privacy/model modes and consent; corrections and their scope/reset; adopted version changes. These are user choices or versioned data, not source edits. The design proposes six fully supported initial organization domains and four safety domains, not a requirement to finish every eventual specialist template before a working launch. [Customization](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:95>), [launch scope](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:52>).

**Non-negotiable safety.** Local-first evidence; protected-content handling and consent; no invented citations/facts/destinations; no silent reorganization of curated structures; uncertainty stays visible; selected roots and tree proposals are not move permission; source/destination freshness and hash verification; no overwrite; append-only provenance and versioning; conditional, verified undo; no automatic deletion. The design does **not** literally prohibit every automatic move: it permits policy-authorized cases. I have not replaced that with a new “review every file” rule. [Mutation safety](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:153>), [privacy](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:177>), [budgets and correction learning](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:242>).

Historical rules-first/override passages remain unresolved in Section 6; they are not silently incorporated into TA2/TA5.

## 2. Ground truth and the three inventories

### Audit boundary and actual execution evidence

Final source reference: **45b9f4e10b148c6086b4f55c3a9360b0b482490e**, September 5, 2026. Source links below refer to that checked-out revision. The workspace changed during investigation; I retained the initial snapshot and then copied the updated source to **/private/tmp/graph-agent-reintegration-final.rkGAPm** and repeated the mixed-folder trace.

In particular, **3ac0c0b now wires optional P9 semantic retrieval when --semantic-model is supplied**, and **3e4a64d adds work_type vocabulary validation**. They are credited here, not reported as still missing. The semantic channel still does not enable B/C/D model judgments.

No production source was edited, no API credential was read, no provider request was issued, and no user file was moved. Diagnostic CLI runs used synthetic files and scratch databases with dotenv loading and cloud credentials disabled. A real target-corpus notebook was inspected locally to specify Phase 0. Historical model-run claims in other documents were not treated as independent live verification.

The supported source-tree invocation is:

~~~sh
PYTHONPATH=src python3 src/cli.py DIRECTORY --situation academic.coursework --label Coursework --database PLAN.sqlite
~~~

DIRECTORY and PLAN.sqlite above describe the existing interface, not a command I executed verbatim. The exact reproductions below are executable as written.

**Actual forward trace, not an inferred module diagram:**

~~~text
cli.main
  -> cli.run
     -> production.run_production_corpus
        -> production.run_production_p1_p7
           -> compose_p1_p7 / orchestrator.run_p1_p7
              -> scanner/cache -> extract_initial -> evidence writes
              -> FactResolver.resolve (native/rule; targeted OCR where required)
              -> classification
        -> cli.run.downstream
           -> _family_pass
           -> _model_fact_pass, only if routing + cloud consent/mode permit
              -> model_fact_resolver -> fact_call_stage -> run_call -> Gate -> issue
           -> production.run_production_p8_p11
              -> _group_corpus -> grouping.pipeline.group_subject
                 -> engine_proposal -> assemble_group_dossier
                 -> STOP B: p8_run_call / p8_authorities are None
              -> cli.review_and_accept (rules-authored aggregate)
              -> tree_design.pipeline.design_tree
              -> approve_plan / privacy policy / build_destination_index
              -> placement.pipeline.run_corpus
                 -> place_group -> place_file
                    -> retrieve / graph / heuristic filters / assess
                    -> STOP C/D: PipelineInputs has no model path
                    -> deterministic place, or abstention
              -> residual surfacing
  -> cli.report -> "Nothing was moved."
~~~

Entry and composition: [cli.main](</Users/jy/GRAPH AGENT/src/cli.py:6106>), [cli.run](</Users/jy/GRAPH AGENT/src/cli.py:3428>), [run_production_corpus](</Users/jy/GRAPH AGENT/src/production.py:843>), [run_p1_p7](</Users/jy/GRAPH AGENT/src/orchestrator.py:544>), [run_production_p8_p11](</Users/jy/GRAPH AGENT/src/production.py:739>).

Separate explicit freeze/apply/undo commands reach real mutation code: [cli._move_frozen_files](</Users/jy/GRAPH AGENT/src/cli.py:5844>) → [apply_selected](</Users/jy/GRAPH AGENT/src/apply_run/run.py:229>) → [apply_plan](</Users/jy/GRAPH AGENT/src/mutation/execute.py:367>); [take_back](</Users/jy/GRAPH AGENT/src/apply_run/run.py:329>) → [undo](</Users/jy/GRAPH AGENT/src/mutation/undo.py:236>). Those are **built and reachable**, not missing.

| Executed probe | Observable result |
|---|---|
| One synthetic syllabus, actual CLI | Exit 0; 1 file “ready to file”; placement = place, accept_direct, auto_eligible; 0 llm_dossier and 0 llm_verdict rows. No model decision caused this placement. |
| Same file and same database, second run | Extraction stayed at 2 run records and 7 evidence records; extract_initial was not called. A second placement was written. Extraction reuse works; this does not prove model-response reuse. |
| Two course syllabi + a résumé + an opaque text file | Reproduced on final revision: 4 placement decisions; 2 place, 2 privacy_blocked abstentions; 0 model dossiers/verdicts. All four files were offered the same accepted group ID, including the opaque file with zero facts. Related-files and semantic-neighbour inputs were empty. |
| Opaque text file alone | Exit 1; 1 indexed file, 5 evidence rows, 0 facts, **0 placement decisions**. design_tree raised NothingToDesign. The CLI printed the failure; this was not silently hidden, but no persistent per-file final review/abstention decision was produced. |
| Real DOCX extractor + real gate + real dossier builder on synthetic large prose | Gate returned Released. A 90,139-byte dossier contained the entire 79,030-character body and all 1,000 body canaries, despite max_dossier_tokens = 4000. Filename was requested but absent from the dossier. Transport was deliberately never invoked. |

Exact retained reproductions:

~~~sh
cd /private/tmp/graph-agent-diagnostic.0VNMDe
python3 probe.py one
python3 probe.py empty-evidence
cd /private/tmp/graph-agent-reintegration-final.rkGAPm
python3 probe.py mixed
python3 payload_probe.py
~~~

These scripts are diagnostic instrumentation, not replacement production engines. They call the real CLI/extractor or real gate/builder. Re-running a CLI probe against its existing database appends new plan decisions, so total placement-row counts increase. They do not use mocked model responses to claim end-to-end success. Scratch snapshots are temporary; this report preserves the observed results and source revision.

### Inventory A — Designed but unbuilt

“No implementation” below applies to the named capability, not to every adjacent abstraction. The last column identifies the nearest actual seam; there cannot be a truthful function citation to a function that does not exist.

| ID | Missing capability against target | Exact boundary / existing neighbour |
|---|---|---|
| U1 | **TA3/TA4/TA6 product interface:** group review, horizontal/vertical tree canvas, residual review and editable previews. The repository has backend records and collection APIs, not the designed running application UI. | [cli.report](</Users/jy/GRAPH AGENT/src/cli.py:5297>) is the current text surface; [review_surface.collect.collect](</Users/jy/GRAPH AGENT/src/review_surface/collect.py:63>) is an action backend, not a rendered canvas. |
| U2 | **Production B_group, C_placement, D_residual and custom-template prompt packages/call-site assembly.** A transport and validators are not the missing authored prompts. | [WIRED_CALL_SITES](</Users/jy/GRAPH AGENT/src/cli.py:528>) contains only A_fact; [a_fact_prompt](</Users/jy/GRAPH AGENT/src/cli.py:2133>); [model_placement module](</Users/jy/GRAPH AGENT/src/model_placement.py:1>); [template_validation](</Users/jy/GRAPH AGENT/src/llm_harness/template_validation.py:1>). |
| U3 | **TA2/TA4 heterogeneous-file situation selection and semantic role/alias resolution as a product flow.** There is no live replacement for applying one required --situation to the whole folder. Recognition exists, but does not supply an independently interpreted situation per file/group to this flow. | [fact_call_authorities](</Users/jy/GRAPH AGENT/src/cli.py:2238>) activates one supplied schema; [run](</Users/jy/GRAPH AGENT/src/cli.py:3428>), [review_and_accept](</Users/jy/GRAPH AGENT/src/cli.py:2688>). |
| U4 | **Concrete span-level identifier classification for contextual redaction.** The release facade and redaction framework exist; the deployment's classifier never identifies a class. This limits safe, useful excerpts. | [fact_call_authorities](</Users/jy/GRAPH AGENT/src/cli.py:2238>) passes classifier=lambda ...: None and a generic transform into [Gate](</Users/jy/GRAPH AGENT/src/privacy/gate.py:149>). |
| U5 | **TA1 native photo evidence:** EXIF/camera/GPS/capture metadata, perceptual hashes and explicit HEIC metadata decoding in the deployed image reader. OCR availability is a separate question. | [header_image_reader](</Users/jy/GRAPH AGENT/src/readers/image_headers.py:186>) reads basic format/dimensions; [macos_readers](</Users/jy/GRAPH AGENT/src/readers/deployment.py:76>) wires it. Existing photo/near-duplicate algorithms cannot manufacture these inputs. |
| U6 | **Archive-marker interpretation adapter.** Manifests are read, but recognizable source/project/package markers are never produced by this deployment. | [macos_readers](</Users/jy/GRAPH AGENT/src/readers/deployment.py:76>) supplies recognize_markers=lambda names: (); [extract_archive](</Users/jy/GRAPH AGENT/src/extractors/archive.py:109>) consumes the missing result. |
| U7 | **DOCX hyperlinks/document relationships reader.** Output slots exist; reader traversal for these fields is explicitly absent. | [python_docx_reader module](</Users/jy/GRAPH AGENT/src/readers/docx_python_docx.py:1>); [extract_docx](</Users/jy/GRAPH AGENT/src/extractors/docx.py:111>) iterates links/relationships the reader does not populate. |
| U8 | **User-configurable time-based residual review scheduling.** The design's “review old temporary screenshots / Reading Inbox periodically” behavior has no located scheduler or cadence evaluator. This is review scheduling, never expiry/deletion. | Design [residual lifecycle](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:128>); nearest built surface [residual_screen](</Users/jy/GRAPH AGENT/src/review_surface/residual.py:177>). |
| U9 | **Turnkey install/launch contract.** No project console-script entry is declared; runtime imports depend on packages absent from the declared runtime/reader extras, including python-docx and the cloud SDK. Optional embedding dependencies also need a declared deployment extra. | [pyproject.toml](</Users/jy/GRAPH AGENT/pyproject.toml:1>), [cli.main](</Users/jy/GRAPH AGENT/src/cli.py:6106>), [docx reader import](</Users/jy/GRAPH AGENT/src/readers/docx_python_docx.py:44>), [DeepSeek._send](</Users/jy/GRAPH AGENT/src/readers/model_deepseek.py:130>). Existing globally installed packages mask this gap. |

Additional format readers are not all implemented: for example XLS, PPT, MSG, ODS, ODP, Numbers and MP3 remain outside the deployed long-tail reader's supported dispatch. [stdlib_long_tail_reader](</Users/jy/GRAPH AGENT/src/readers/long_tail_stdlib.py:1236>). **This is not automatically a launch bug:** 00 permits explicit indexed-but-unreadable handling for unsupported initial formats. Phase 2 must prove that status, rather than demand every eventual format before fixing placement.

### Inventory B — Built but disconnected from the relevant live path

The inventory unit is a designed capability and its responsible function cluster, not each helper inside that cluster. Test helpers, replay-only utilities and intentionally unselected provider alternatives are not counted as independent product defects.

| ID | Existing code that the product path does not reach/use | Exact disconnect; target |
|---|---|---|
| D1 | [grouping.p8_seam.build_dossier_request](</Users/jy/GRAPH AGENT/src/grouping/p8_seam.py:182>), [apply_p8_verdict](</Users/jy/GRAPH AGENT/src/grouping/p8_seam.py:294>), B validation/harness | [cli.run.downstream](</Users/jy/GRAPH AGENT/src/cli.py:4383>) passes p8_run_call=None and p8_authorities=None. [group_subject:612](</Users/jy/GRAPH AGENT/src/grouping/pipeline.py:612>) returns no-model-configured before reaching the seam. **TA3.** |
| D2 | [PlacementCallAuthorities](</Users/jy/GRAPH AGENT/src/model_placement.py:71>), [model_path_injections](</Users/jy/GRAPH AGENT/src/model_placement.py:297>), [call_placement](</Users/jy/GRAPH AGENT/src/placement/p8_seam.py:199>) | [cli.run.placement_inputs:4124](</Users/jy/GRAPH AGENT/src/cli.py:4124>) passes all eight model-related inputs as None. The adapter is not invoked here. **TA5/TA6.** |
| D3 | [ollama_invoke](</Users/jy/GRAPH AGENT/src/readers/model_ollama.py:63>) and target-bound model routing | The ordinary CLI configures cloud routing; [_model_fact_pass](</Users/jy/GRAPH AGENT/src/cli.py:4138>) returns unless mode is hybrid. Permitting unclassified local calls inside Gate does not make a local call reachable. **TA2 and local-first operation.** |
| D4 | [version_family](</Users/jy/GRAPH AGENT/src/facts/families.py:340>), [photo_events](</Users/jy/GRAPH AGENT/src/facts/photo_event.py:173>), [bounded_sessions](</Users/jy/GRAPH AGENT/src/facts/session.py:181>) | No production callers found for these producers. CLI _family_pass uses duplicate_family with near_match always False; media_type is wired, photo_events is not. These should supply bounded retrieval evidence, not autonomous semantic groups. **TA1/TA3.** |
| D5 | Authored needs_llm recognition rows, loaded into [SchemaRules.deferred_readings](</Users/jy/GRAPH AGENT/src/recognition/rules.py:28>) by [_schema](</Users/jy/GRAPH AGENT/src/recognition/rules.py:84>) | Loaded data has no live consumer that constructs those interpretation questions. Optional semantic recognition is a separate similarity path, not execution of these deferred language instructions. **TA2.** |
| D6 | [record_user_level_edit](</Users/jy/GRAPH AGENT/src/tree_design/user_edits.py:147>), [set_display_label](</Users/jy/GRAPH AGENT/src/facts/values.py:173>), [merge_values](</Users/jy/GRAPH AGENT/src/facts/values.py:191>), [apply_review_action](</Users/jy/GRAPH AGENT/src/tree_design/store.py:462>) | Persistence/application backends exist, but the CLI does not expose the designed general editing/alias/merge gestures. Reading a saved overlay is not a way for a user to create one. **TA4/customizability.** |
| D7 | Gate token-measurement hook, dossier reduction ladder, [fact_cache_key](</Users/jy/GRAPH AGENT/src/facts/cache.py:93>) / [is_stale](</Users/jy/GRAPH AGENT/src/facts/cache.py:119>) | The fact deployment injects no token measurer; [_call_dependencies](</Users/jy/GRAPH AGENT/src/model_facts.py:454>) asserts unreduced_fits=True. Fact cache identities exist, but there is no complete pre-call reusable-decision lookup covering model/prompt/schema/policy changes and abstentions. **TA1/TA2/TA5 efficiency.** |

**Latent defects in disconnected code—not findings observed on the ordinary live path:**

- **L1 (D1):** **Latent B:** one aggregate verdict cannot transport group label/category and per-member decisions. apply_p8_verdict writes memberships by iterating all candidates/anchors and does not update group coherence/label. [P8Verdict](</Users/jy/GRAPH AGENT/src/llm_harness/records.py:448>), [worst_outcome](</Users/jy/GRAPH AGENT/src/llm_harness/harness.py:339>), [apply_p8_verdict](</Users/jy/GRAPH AGENT/src/grouping/p8_seam.py:294>). **TA3 exact output.** Raw stored responses do not make this application step happen.
- **L2 (D2):** **Latent C/D:** _judge_with_model offers all legal node IDs, not a capped, profile-rich shortlist. Generic dossier serialization has no destination-profile or typed-neighbour packet. Its evidence snapshot derives from facts, making sparse no-fact cases especially fragile. [_judge_with_model](</Users/jy/GRAPH AGENT/src/placement/pipeline.py:1259>), [_body](</Users/jy/GRAPH AGENT/src/llm_harness/dossier.py:212>), [_model_call_request_builder](</Users/jy/GRAPH AGENT/src/model_placement.py:210>). **TA5/TA6.**
- **L3 (D2):** **Latent C:** date/institution/project support values are checked against the same vocabulary used for destination node IDs. A supported dimension value can therefore be rejected as invented merely because it is not a node ID. [_invented_dimension](</Users/jy/GRAPH AGENT/src/llm_harness/placement_validation.py:185>), [_placement_site](</Users/jy/GRAPH AGENT/src/llm_harness/placement_validation.py:200>). **TA5 validation contract.**

**Not still disconnected:** extraction readers, shipped template loading, A_fact, ordinary CLI review/reporting, explicit apply/undo, exact duplicates, screenshot heuristics, and optional P9 embeddings now have callers. A subject fact can reach folder construction via [folder_levels_for](</Users/jy/GRAPH AGENT/src/production.py:301>); the remaining subject-field omission below is specifically the P9 grouping allowlist.

### Inventory C — Built and wired, but wrong

These functions are wired into the ordinary CLI path, although optional cloud/semantic branches run only under their stated configuration. L1–L3 above are kept out of this inventory because B/C/D are currently disconnected.

| ID | Actual behavior | Exact file/function; target violation |
|---|---|---|
| W1 | Automatic placement can be authored entirely by deterministic support/margin rules. Model absence does not prevent a supported rule winner from being placed. | [needs_model_call](</Users/jy/GRAPH AGENT/src/placement/scoring.py:328>), [place_file:847](</Users/jy/GRAPH AGENT/src/placement/pipeline.py:847>), [place_file:882](</Users/jy/GRAPH AGENT/src/placement/pipeline.py:882>). **TA5 corrected authority.** Reproduced. |
| W2 | Groups receive rule-generated meaning; CLI merges non-halted proposals under the global situation/label and records a coherent, accepted rules-authored aggregate with pending review. That is not B's coherence verdict or the user's reviewed acceptance. | [engine_proposal](</Users/jy/GRAPH AGENT/src/grouping/naming.py:128>), [group_subject:590](</Users/jy/GRAPH AGENT/src/grouping/pipeline.py:590>), [review_and_accept](</Users/jy/GRAPH AGENT/src/cli.py:2688>). **TA3/TA4.** |
| W3 | Every file is offered all accepted group IDs, not its own accepted memberships. The résumé and zero-fact opaque file received the syllabus aggregate ID. | [cli.run.evidence_for](</Users/jy/GRAPH AGENT/src/cli.py:3787>), specifically [group_ids:3824](</Users/jy/GRAPH AGENT/src/cli.py:3824>). **TA5 provenance.** Reproduced. |
| W4 | Evidence metadata is reconstructed as location=heading, span=(0,len(canonical_value)), basis=direct-anchor regardless of actual source. Only the first citation survives; related_files and semantic_neighbours are empty; all entity frequencies are 1. | [evidence_for](</Users/jy/GRAPH AGENT/src/cli.py:3787>). **TA5 located evidence and graph context.** Optional P9 vectors do not fill this placement input. |
| W5 | P9's active fields are a handwritten subset: DIRECT_SLOTS plus term/media_type/work_type. Subject and other interpreted fields are absent. conflicts_for returns (), and signal_evaluator_for always returns True for the supplied domain. | [cli.run.downstream:4376](</Users/jy/GRAPH AGENT/src/cli.py:4376>). **TA2/TA3.** The omission is not a missing template-library release. |
| W6 | Whole local text units—short headings/cells included—are excluded from fact excerpts, while metadata and regex fragments survive. OCR-zone observations are globally excluded. The model can be deprived of the very language it must interpret. | [releasable_observations](</Users/jy/GRAPH AGENT/src/model_facts.py:290>), [ALWAYS_LOCAL_ZONES](</Users/jy/GRAPH AGENT/src/privacy/vocabulary.py:214>). **TA2/TA6.** Opaque/résumé probes offered only extension/MIME. |
| W7 | Filename is requested as an ID-only object but never materialized or serialized as a filename. Recent comments claiming the model now sees it stop at construction, not actual bytes. | [build_fact_request](</Users/jy/GRAPH AGENT/src/model_facts.py:381>), [Gate.REFERENCE_ONLY](</Users/jy/GRAPH AGENT/src/privacy/gate.py:141>), [_released_evidence](</Users/jy/GRAPH AGENT/src/llm_harness/dossier.py:103>), [_body](</Users/jy/GRAPH AGENT/src/llm_harness/dossier.py:212>). **TA2/TA6.** Reproduced with filename canary. |
| W8 | DOCX prose is emitted as one spanless body with no backing text unit. “No unit” is treated as a releasable container value, allowing the complete body into a dossier. The declared token maximum is not enforced. | [extract_docx:210](</Users/jy/GRAPH AGENT/src/extractors/docx.py:210>), [releasable_observations](</Users/jy/GRAPH AGENT/src/model_facts.py:290>), [materialise](</Users/jy/GRAPH AGENT/src/privacy/resolve.py:242>), [is_whole_document](</Users/jy/GRAPH AGENT/src/privacy/items.py:364>), [Gate.release:387](</Users/jy/GRAPH AGENT/src/privacy/gate.py:387>). **TA1/TA2 privacy and boundedness.** Reproduced without transport. |
| W9 | No usable group can terminate the whole run before per-file placement/residual decisions. User label input does not rescue the empty branch candidate set because design_tree supplies user_labels=(). | [design_tree:689](</Users/jy/GRAPH AGENT/src/tree_design/pipeline.py:689>), exact break [NothingToDesign:696](</Users/jy/GRAPH AGENT/src/tree_design/pipeline.py:696>). **TA4/TA6 visible accounting.** CLI error visible; persistent final decision absent. |
| W10 | Rule-settled semantic fields are removed from model questions; the stronger-fact oracle can veto model alternatives; subject normalization demands a course-code pattern rather than accepting every supported user-facing subject name. | [open_question](</Users/jy/GRAPH AGENT/src/model_facts.py:163>), [pending_fields_for](</Users/jy/GRAPH AGENT/src/model_facts.py:269>), [normalize_for_model](</Users/jy/GRAPH AGENT/src/cli.py:1806>), [contradicts_stronger](</Users/jy/GRAPH AGENT/src/cli.py:1897>). **TA2 corrected authority; owner policy decision required.** |
| W11 | First usable nesting and count-derived refinement are substituted for high-leverage user design choices. The CLI discloses these defaults, but disclosure is not the TA4 interaction or approval. | [choose_option](</Users/jy/GRAPH AGENT/src/cli.py:2812>), [nesting_chooser](</Users/jy/GRAPH AGENT/src/cli.py:2895>), [refinement_for](</Users/jy/GRAPH AGENT/src/cli.py:2932>). **TA4.** |
| W12 | Extraction cache is real, but pending-field suppression is not a full model cache. Unresolved answers can be asked again; settled fields are suppressed without a full model/prompt invalidation check before deciding whether to ask. | [FactResolver.resolve](</Users/jy/GRAPH AGENT/src/facts/resolver.py:154>), [pending_fields_for](</Users/jy/GRAPH AGENT/src/model_facts.py:269>), [fact_call_stage](</Users/jy/GRAPH AGENT/src/model_facts.py:494>), [run_call](</Users/jy/GRAPH AGENT/src/llm_harness/harness.py:395>). **TA2 cost and freshness.** Static finding; no repeated paid calls were made. |
| W13 | Prompt contains a schema, but the cloud request does not request provider-enforced structured output. Accounting settles a fixed configured cost, not observed provider token/spend usage. | [DeepSeek._send](</Users/jy/GRAPH AGENT/src/readers/model_deepseek.py:130>), [fact_call_authorities](</Users/jy/GRAPH AGENT/src/cli.py:2238>), [FACT_CALL_COST](</Users/jy/GRAPH AGENT/src/cli.py:567>). **TA2 output reliability/budget observability.** |
| W14 | Unknown classification remains a cloud privacy denial even after the earlier route gate permits the file. The deployment also has no selected local reasoning route. Thus “allowed past route” is not “model saw evidence.” | [model_route_permitted](</Users/jy/GRAPH AGENT/src/cli.py:2170>), [Gate.release](</Users/jy/GRAPH AGENT/src/privacy/gate.py:188>), [unclassified_denies](</Users/jy/GRAPH AGENT/src/privacy/denial.py:185>). **TA2/TA6.** Preserve the cloud safety default; provide the intended local/review alternative. |

### Why this became “built” without becoming the product

There are three distinct causes, not one missing API key:

1. **A historical architecture was implemented faithfully in places.** Rule winners and rule-over-model precedence are written into 00 and subsequent contracts. They conflict with the purpose you have now made authoritative. These require an explicit policy migration, not a claim that every contributor ignored its specification.
2. **Component completion was mistaken for composition completion.** Callers must supply policies, prompts and adapters; several callers supply None, empty tuples, always-True predicates or global user inputs. Those values satisfy many local contracts while removing the product's intelligence. [facts.llm_seam](</Users/jy/GRAPH AGENT/src/facts/llm_seam.py:24>) documents the historical “each part hands checking to the other” ownership gap.
3. **Boundary tests do not assert the product outcome.** [test_model_placement](</Users/jy/GRAPH AGENT/tests/integration/test_model_placement.py:1>) explicitly says it does not assert that a call is made; its first test validates the all-None state. That is a useful refusal test, not evidence of a functioning placement engine. Other local invariants cannot detect a filename requested-but-never-serialized or a model label stored-but-never-applied unless the test follows the bytes and consequences.

The new embedding and work-type repairs improve particular symptoms, but neither closes the missing decision calls or repairs the group-output contract.

## 3. LLM-bypass findings

| ID / tag | Where the model ceased to be the decision-maker | Classification of deterministic behavior |
|---|---|---|
| B1 — **wiring bug** | D1/D2: B_group and C/D receive None from the actual composition root, even when A_fact cloud routing is available. | Not a legitimate pre-filter; the semantic decision stage is absent. |
| B2 — **missing piece** | U2: B/C/D/custom-template production prompts and complete call-site assembly were not delivered. | Enabling a key or feature flag cannot create them. |
| B3 — **design mismatch** | W1: score/margin + unique-direct-match path chooses a legal destination without an LLM verdict. | Ranking is a legitimate pre-filter **until** it authorizes place. That final branch contradicts TA5. |
| B4 — **design mismatch** | W2/W11: engine_proposal, global --situation/--label aggregation, first nesting and automatic coherence/acceptance stand in for model and high-leverage human judgments. | A user-chosen label is valid for the scope actually chosen, not evidence that every mixed-folder file has that purpose. |
| B5 — **design mismatch** | W10: word/regex rules write validated semantic work_type/subject; pending_fields_for treats them as closed; contradicts_stronger can veto the model. | Parsing an explicit identifier/date is legitimate evidence preparation. Semantic category finalization or immutable rule priority is not merely preparation. |
| B6 — **design mismatch** | [_a_folder_made_for_this_keeps_it](</Users/jy/GRAPH AGENT/src/placement/pipeline.py:320>), [_without_kind_only_moves](</Users/jy/GRAPH AGENT/src/placement/pipeline.py:232>), [_staying_put_wins_a_tie](</Users/jy/GRAPH AGENT/src/placement/scoring.py:132>) can remove candidates or choose a current folder based on semantic preservation assumptions. | Rejecting outside-root, forbidden or nonexistent nodes is legitimate. Inferring “this folder was made for this” and deciding the winner is a semantic policy conflict. Keep-as-is by explicit user instruction is different and legitimate. |
| B7 — **wiring bug** | W3/W4/W5: actual memberships, neighbors, conflict data and schema fields are not transcribed into the intended downstream inputs. | Not a model failure: the model either is not called or could not see the missing evidence. |
| B8 — **wiring bug** | W7: Filename is constructed, then classified as reference-only and disappears before serialization. | Requested input is not delivered input. The defect survives tests that only assert object construction. |
| B9 — **design mismatch** | L1: rich B interpretation is collapsed into aggregate severity; individual membership/outlier/name content does not reach its intended records. | Validation is legitimate; losing accepted semantic output and substituting blanket memberships is not application of that output. |
| B10 — **wiring bug** | D5/D3/W14: deferred interpretation instructions have no consumer, and permissive local policy has no live local client route. | A safety refusal is legitimate. Failing to provide a local or visible review route is missing product composition, not evidence that a cloud privacy restriction should be removed. |
| B11 — **wiring bug** | W9: no group means no tree, hence no per-file terminal decision. | No model or human made a placement decision. The top-level printed error is useful but does not satisfy TA6's persistent accounting. |
| B12 — **design mismatch** | W6/W8/L2/L3: the model-facing protocol is simultaneously starved of useful context, inadequately bounded, and unable to express/check the designed placement support correctly. | Closed schemas and legal candidate lists are legitimate. Confusing node IDs with fact values, stripping all useful snippets or omitting profile meanings is not. |

**Deterministic paths that should be preserved:** filesystem exclusions and protected-container handling; stat/hash identity; native parsing and OCR dispatch; exact duplicate evidence; local vector retrieval and caps; legal-root/frozen-node checks; citation resolution; schema validation; privacy denial; user-selected keep/place actions; hash/no-overwrite mutation and undo. A hard constraint can reject an unsafe model output without becoming a competing semantic sorter.

Do not report a nonexistent C overwrite bug: [transcribe](</Users/jy/GRAPH AGENT/src/placement/p8_seam.py:172>) handles accepted model verdicts before its fallback to the old assessment. The substantiated failures are that C is unreachable, its future input contract is incomplete, and B's rich output is not applied.

## 4. Input/output audit

### Is the input bounded?

**Not end to end.** There are real file/candidate/extraction limits, a 12-observation fact-selection limit, and a nominal 4,000-token dossier setting. These are not equivalent to measuring and capping the final request.

The decisive chain is:

~~~text
cli.fact_call_authorities: Gate(... no measure_tokens ...)
model_facts._call_dependencies: unreduced_fits=True
Gate.release: compare token count only when measurer is present
dossier._body: serialize max_dossier_tokens as data, without measuring
~~~

The DOCX probe demonstrates why “12 observations” is not a size bound: one observation held 79,030 characters. The resulting dossier was 90,139 bytes; no token-over-budget denial occurred. This establishes absent enforcement, not a provider-token measurement. No transport was invoked.

The C/D builder also enumerates all legal destination IDs instead of sending only the retrieved shortlist with bounded profiles. The archive deployment explicitly uses an uncapped manifest reader. Local full-text extraction is desirable; **local extraction size and model-release size are separate budgets**.

There are useful existing extraction limits—e.g. PDF page ceiling and spreadsheet cell ceiling—but the default Vision language list is only en-US. Appropriate CJK coverage and OCR page/time limits require a corpus-specific verification pass. [deployment configuration](</Users/jy/GRAPH AGENT/src/readers/deployment.py:53>), [CLI PDF ceiling](</Users/jy/GRAPH AGENT/src/cli.py:612>).

### Is there caching?

**Extraction: yes, observed.** The repeat syllabus run reused evidence and did not call extract_initial. [orchestrator._extraction_is_stale](</Users/jy/GRAPH AGENT/src/orchestrator.py:158>) and scan/cache logic are real.

**Model decisions: incomplete.** Cache-key machinery exists and fact rows retain lineage, but fact_call_stage does not first look up a reusable result for the complete current decision identity. It suppresses fields already regarded as settled. That can avoid some calls, repeat unresolved questions unnecessarily, and fail to re-ask after a prompt/model/schema change. Recording a content-addressed dossier is deduplication of a record, not reuse of its prior validated answer.

A repaired cache must distinguish file/evidence version, extractor/config version, model, prompt, schema/allowed options, privacy policy, and—for B/C/D—membership/frozen-plan context. Reusing an answer does not reuse an old privacy release capability. Abstention/failed-call retry policy must be explicit.

### Is the output constrained?

**Partially, and there is real useful code.** A_fact has a JSON schema, allowed fields, field glossary, folder-level context, parser, citation validation, value normalization, persisted response/verdict records and privacy-bound transport. It is not merely an unbounded natural-language answer parsed with hope.

However:

- DeepSeek receives a user-message prompt without response_format/json_schema in the actual request. Output token limits do not guarantee schema compliance. The local Ollama adapter requests JSON, but is not selected by the ordinary CLI.
- B's semantic result type/application loses the designed label/coherence/member distinctions.
- C's node-ID vocabulary lacks profile meanings and is wrongly reused to validate semantic dimension values.
- Prompt-field closure is valid; using a fixed lexical vocabulary as an unchangeable semantic authority is the separate owner conflict in Section 6.
- Configured “actual cost” is a constant accounting charge, not independently observed provider usage.

### Are there starved or misleading inputs?

**Yes, with different failure classes:**

| Input failure | What downstream sees instead | Required distinction |
|---|---|---|
| Whole-unit exclusion removes short headings/cells; OCR zone excluded | Metadata and structured regex scraps, sometimes just MIME/extension | Extracted successfully is not equivalent to model received useful evidence. |
| Filename reference not materialized | An opaque subject handle and no identifying filename | Requested item count is not delivered content. |
| DOCX spanless whole body accepted | Too much prose, including content meant to remain local | A readable observation is not automatically a bounded, releasable excerpt. |
| Global group IDs / fake heading spans / empty neighbors | False support, incorrect provenance, absent context | Database facts need faithful transcription, not synthesized locator metadata. |
| One global situation and limited P9 active fields | Relevant alternative schemas/roles may never be considered | Candidate narrowing must preserve plausible alternatives for interpretation. |
| No branch from an opaque-only folder | No placement/residual rows for an indexed file | A run-level error is not a terminal per-file review state. |

The actual target corpus includes PDFs, DOCX/DOC, PNG/JPEG, notebooks/source code, text/HTML/Markdown, XLSX/CSV and ZIPs, including multilingual material. Phase 2 must sample those real families. A syllabus-only fixture suite cannot stand in for that corpus.

**Failure visibility is mixed, not universally broken.** Extraction statuses, model failure records, privacy blocks and CLI explanations exist. The opaque-only dead end is visible at the top level. The model-fact stage also returns () when there is no pending/releasable question without writing a per-file unresolved record; metadata-only input can still count as a nonempty question. Repair the specific accounting gaps rather than asserting that all errors are swallowed.

## 5. Dependency-ordered repair plan

This is a repair of existing components, not a new architecture. **No phase below has been implemented or passed as part of this diagnostic.** The plan is held behind the unresolved authority/privacy decisions in Section 6.

The writing-plans discipline is used for named files, dependencies and observable gates. Your requested diagnostic format takes precedence over generating speculative replacement implementation code.

### Acceptance tooling contract

**Proposed new diagnostic driver:** tools/reintegration.py. It must only orchestrate/instrument the existing production functions, never contain its own classifier, scorer, placement engine or fake model answer. Its subcommands below are specifications to implement, **not currently available commands**. Every command returns nonzero on a failed assertion and prints per-file records plus a compact JSON summary.

**Proposed regression suite:** tests/reintegration/. Test selectors named below define the required cases. Unit/fault-injection tests complement, never replace, the real-model runs.

Common driver requirements:

- Fresh scratch workspace by default; refuse to overwrite an existing run.
- Raw user corpus read-only. Never call apply/undo except the explicit sandbox move-roundtrip case.
- Require a real configured provider for --require-live. Refuse mocks, missing models, cached-only runs, fallback rule winners and unavailable transport as proof of a live call.
- Log the actual prompt/dossier fingerprint, call site, provider/model identity, request/response linkage, citations, selected node/depth and final disposition locally. Do not log secrets.
- A transport counter must be observed at llm_harness.transport.issue, and the placement must reference its validated result. Merely constructing ModelClient does not count.
- Privacy permission remains mandatory. Phase 0 uses a local model and short non-sensitive evidence. Do not turn cloud on to test the known whole-DOCX leak.
- Before implementation, add failing regression cases for the measured defects. Make one seam change at a time; keep production and diagnostic paths using the same functions.

### Phase 0 — Prove one real file can go all the way through, by hand

**Goal:** one actual target-corpus file, extraction → bounded evidence → real local model judgment → validated final placement decision printed. No batch processing, UI or filesystem move.

**Existing files/functions:** orchestrator.run_p1_p7; extractors.dispatch.extract_initial; evidence_shape store/locators; privacy.gate.Gate.release; readers.model_ollama.ollama_invoke; llm_harness.harness.run_call; llm_harness.transport.issue; tree_design.freeze.freeze; placement.p8_seam.call_placement/transcribe; placement decision persistence.

**New assets:** tools/reintegration.py; tests/reintegration/fixtures/phase0-tree.json; tests/reintegration/test_live_one.py. The fixture declares only an explicitly approved Coursework root with Lecture material and Practice work leaves. It is a diagnostic user-authored tree, not a model-invented production taxonomy.

Use the real notebook **.groundtruth/sample/Desktop/Python 1006/lecture01_introduction.ipynb**. Its first cells explicitly contain “ENGI E1006” and “Lecture 1: Course Overview / Introduction”. Do not send its email/address-bearing cells. Manually select the small located title/lecture excerpt. The local model's installed identity must be supplied through REINTEGRATION_LOCAL_MODEL; no default provider/model substitution.

Sequence:

- [ ] Author and approve the minimum C prompt/schema, with candidate labels/IDs and cited choice/abstention output. This closes only the U2 slice required for the bench trace.
- [ ] Build the tiny approved tree using existing node/freeze APIs.
- [ ] Run real extraction; inspect and manually select the two title/lecture evidence spans through the existing privacy door.
- [ ] Send one real C request and carry its validated selected node into a persisted/printed decision. Do not use the deterministic winner as the answer.
- [ ] Print the trace and record zero mutation calls. This is a bench proof, **not yet proof the ordinary CLI is repaired**.

**Exact acceptance command after implementing the driver:**

~~~sh
PYTHONPATH=src python3 tools/reintegration.py one --file '.groundtruth/sample/Desktop/Python 1006/lecture01_introduction.ipynb' --tree tests/reintegration/fixtures/phase0-tree.json --provider ollama --model-from-env REINTEGRATION_LOCAL_MODEL --require-live --no-moves
~~~

**Pass:** a real C_placement call is recorded; the model selects the fixture's Lecture material leaf with a resolvable lecture-heading citation; that same node appears in the saved decision and on screen; moves=0; source hash unchanged. Missing model, mock response, rule-selected destination, uncited answer or wrong leaf is failure. A legitimate abstention is recorded honestly but does not pass this intentionally unambiguous positive case.

### Phase 1 — Fix wiring, not internals

**Goal:** complete the existing production call sequence and expose every disconnected capability through the real application/CLI adapters. Leave latent B/C semantic application in an observation-only mode until Phase 3 fixes its contracts; a successful call is not permission to activate a known-wrong consequence.

**Files:** src/cli.py, src/production.py, src/model_facts.py, src/model_placement.py, existing grouping/placement seams, existing review/edit adapters. Add the missing approved B/C/D/custom prompt definitions under src/llm_harness/library and bind them through src/llm_harness/prompt_library.py. Do not scatter alternate prompts through transports.

| Task | Wiring work, with existing functions | Exact driver case and pass criterion |
|---|---|---|
| P1.1 | Connect cli.downstream to grouping.group_subject → build_dossier_request → run_call; replace missing B authorities. | wiring --case b-group: actual B call linked to its group dossier; no-model-configured absent; accepted state unchanged until reviewed/Phase 3. |
| P1.2 | Call model_path_injections from cli.placement_inputs; bind C and D clients, requests, policies and result accessors. | wiring --case c-placement: model_path_available=true and a C issue event from the production place_file path. |
| P1.3 | Bind existing review_residual_sets/run_residual_file only after the user's residual opt-in. | wiring --case d-residual: zero D calls before opt-in, a real D call after, no mutation in either case. |
| P1.4 | Expose local/cloud/offline routing through the same model_fact_resolver and Gate, instead of a hybrid-only early return. | wiring --case local-routing: local issue event on eligible unclassified evidence; cloud remains denied absent proper safety/consent; missing local service visibly refuses. |
| P1.5 | Connect version_family, photo_events and bounded_sessions to corpus preparation; preserve their evidence-only/possible semantics. Connect near-duplicate comparison only when actual perceptual evidence exists. | wiring --case family-producers: each producer reached on its fixture; records reflect its existing contract; insufficient metadata yields explicit no-result, not an invented family or group. U5 input completion follows in Phase 2. |
| P1.6 | Give SchemaRules.deferred_readings a consumer that forms relevant interpretation questions for the existing harness. | wiring --case deferred-readings: one authored needs_llm row can be traced into one permitted question; irrelevant domains are not all activated. |
| P1.7 | Expose record_user_level_edit, set_display_label, merge_values and apply_review_action through narrow explicit user-action adapters; keep using their current transaction/versioning behavior. | wiring --case user-edits: an explicit edit goes through the production adapter, persists, and is read on the next design; unrequested edits write nothing. The full canvas is Phase 5. |
| P1.8 | Bind Gate.measure_tokens, reduction measurements and existing stale-key/cache lookups through one deployment authority. | wiring --case budget-cache-hooks: spies show the real hooks run; Phase 2 establishes accurate bounds and reuse semantics. |
| P1.9 | Connect custom-template validation to its approved generation call and review action path. | wiring --case custom-template: real proposal reaches existing validator, remains an unapproved draft, creates no directories. |
| P1.10 | Declare runtime/optional provider and embedding dependencies and a console entry for cli.main. Keep optional heavyweight imports lazy. | wiring --case installation: a clean environment using declared extras can launch help and the local diagnostic without inheriting globally installed packages. |

**Exact batch gate:**

~~~sh
PYTHONPATH=src python3 tools/reintegration.py wiring --cases b-group,c-placement,d-residual,local-routing,family-producers,deferred-readings,user-edits,budget-cache-hooks,custom-template,installation --provider ollama --model-from-env REINTEGRATION_LOCAL_MODEL --require-live --observe-only --no-moves
~~~

**Pass:** each named case prints PASS plus the stated event/record evidence; no missing configuration is disguised as a successful judgment; no accepted production semantic state is created from the still-lossy B adapter. Failure of any item prevents Phase 2 sign-off.

### Phase 2 — Fix the input side

**Goal:** model inputs are useful, faithfully located, privacy-approved, and bounded across the actual corpus; repeated questions reuse valid results.

**Files/functions:** model_facts.releasable_observations/build_fact_request/_call_dependencies; extractors.docx.extract_docx; readers.docx_python_docx.python_docx_reader; readers.image_headers.header_image_reader/deployment; privacy.items.is_whole_document; privacy.resolve.materialise; Gate.release; llm_harness.dossier._body/build_dossier; cli.evidence_for/downstream; grouping.p8_seam.build_dossier_request; placement.pipeline._judge_with_model; facts.cache; orchestrator._extraction_is_stale.

Dependency order:

- [ ] Close the full-DOCX release hole first. Represent full local text and short releasable snippets distinctly using the existing evidence contract. A missing backing unit must not turn whole prose into an unrestricted cell value.
- [ ] Materialize permitted Filename/CandidateLabel content through the privacy gate with accurate audit and release binding. Do not bypass the gate to append paths to the prompt.
- [ ] Permit useful short headings/cells and policy-approved OCR snippets without sending complete text or globally releasing OCR. Implement the agreed identifier classifier/redaction policy; preserve current protected defaults.
- [ ] Measure the **final provider-bound request**, including prompt/schema/profile overhead. Enforce a configured input ceiling, reserve output capacity, run real summarize/preserve-anchors/split choices, and persist deferred-budget states when no valid packet fits.
- [ ] Populate actual locators, all necessary citations, current-version facts, per-file accepted memberships, neighbors, conflicts and measured entity frequencies. Replace the P9 handwritten field subset with the applicable schema/library data.
- [ ] Serialize bounded, structured B anchor/candidate/edge packets and C/D profile shortlists. A node's ID alone is not its meaning. Include the legal parent/approved fallback and meaningful competitors without transmitting the entire tree.
- [ ] Complete required photo/HEIC metadata and DOCX relationship reading; wire archive marker data; test language-appropriate OCR and caps. Unsupported initial formats retain an explicit status. Do not postpone the known input correctness gaps to scale testing.
- [ ] Use existing versioned cache identities for both successful and abstaining model results; invalidate on the relevant file/evidence/model/prompt/schema/policy/plan change. A fresh release is required for any new transmission.

**New test files:** tests/reintegration/test_input_contract.py; test_privacy_payload.py; test_cache_identity.py; test_corpus_readers.py. Add synthetic full-body, sensitive-identifier, filename, heading, table and OCR canaries plus a selection manifest drawn from the real corpus.

**Exact commands:**

~~~sh
PYTHONPATH=src python3 tools/reintegration.py inputs --corpus .groundtruth/corpus --families pdf,docx,doc,png,jpeg,ipynb,py,txt,html,md,xlsx,csv,zip --include-canaries --inspect-payloads --no-send --no-moves
python3 -m pytest tests/reintegration/test_input_contract.py tests/reintegration/test_privacy_payload.py tests/reintegration/test_cache_identity.py tests/reintegration/test_corpus_readers.py -v
PYTHONPATH=src python3 tools/reintegration.py inputs --case cache-roundtrip --provider ollama --model-from-env REINTEGRATION_LOCAL_MODEL --require-live --no-moves
~~~

**Pass:** every selected file prints extracted/partial/unsupported/protected status and usable-evidence status separately. Every sendable packet has meaningful, resolvable evidence and a measured count within the ceiling. Full-body/path/protected canaries never appear in released bytes; permitted short heading/cell/filename canaries do. Large payloads shrink safely or visibly defer. Unchanged second run makes zero new extraction/model calls for reusable decisions; changing each key dimension invalidates only affected results. No provenance is fabricated to make a check pass.

If a family is absent from the current corpus, the driver reports “absent from corpus” and uses an explicit synthetic reader fixture; it must not count a zero-file selection as coverage.

### Phase 3 — Fix the output side

**Goal:** validated model semantics—not a stale rule winner—become the actual reviewable records. Every file has a terminal outcome even when grouping/tree design cannot proceed.

**Files/functions:** llm_harness.records.P8Verdict and related site result types; harness._validate_and_record/worst_outcome; grouping.p8_seam.apply_p8_verdict; grouping.store/acceptance; cli.review_and_accept; placement.pipeline.place_file/_judge_with_model/run_residual_file; scoring.needs_model_call; p8_seam.transcribe; placement_validation._placement_site/_invented_dimension; tree_design.pipeline.design_tree.

- [ ] Preserve the existing validated claim records but deliver a typed site result containing B coherence, label/category and each member's own include/exclude/uncertain/outlier/citation result. Aggregate severity can remain a summary; it cannot substitute for semantic payload.
- [ ] Supersede group records consistently and update membership/acceptance references. Remove blanket membership transcription and rules-authored coherence/acceptance in the unattended CLI.
- [ ] Implement the owner's decisions on rule-first placement, strong-rule precedence and preservation heuristics. Safety constraints stay hard; semantic scores/candidates feed the model. An invalid or unavailable model response becomes visible review/abstention, never permission to fall back to the rule winner.
- [ ] Validate destination IDs against frozen IDs, dimension values against supplied supported profile/evidence values, and citations against the released dossier. They are different domains.
- [ ] Apply the selected node/depth and D action from the validated model result. Respect shared-material and residual opt-in; no node creation after freeze.
- [ ] Route the NothingToDesign case to persistent per-file unresolved/keep/review states and optional user-authored branch creation. Do not fabricate a branch or a semantic label.
- [ ] Keep high-confidence, context-supported, unsure, rejected, unavailable, protected and budget-deferred cases distinct in records and UI output.

**New tests:** tests/reintegration/test_decision_authority.py; test_group_result_application.py; test_terminal_accounting.py; test_residual_actions.py.

**Exact commands:**

~~~sh
python3 -m pytest tests/reintegration/test_decision_authority.py tests/reintegration/test_group_result_application.py tests/reintegration/test_terminal_accounting.py tests/reintegration/test_residual_actions.py -v
PYTHONPATH=src python3 tools/reintegration.py outputs --cases model-over-rule,group-members,model-label,parent-only,shared-material,residual-opt-in,empty-evidence,invalid-citation,invented-node,model-unavailable --provider ollama --model-from-env REINTEGRATION_LOCAL_MODEL --require-live --no-moves
~~~

**Pass:** the supported positive case deliberately ranks a different node first deterministically, while the valid model-selected node is what is recorded. Each B member keeps its own outcome; excluded members are not bulk-included; label/coherence match the model result and stay reviewable. Unsupported specificity stops at a supported parent. Uncertain or invalid decisions do not become moves. The opaque-only case produces one persistent terminal outcome per indexed file, not zero. D is never called before opt-in.

Fault-injection tests may supply invalid or contradictory responses to exercise validation. The separate --require-live cases must still demonstrate a real model deciding and that same result reaching persistence.

### Phase 4 — Re-widen to the full pipeline

**Goal:** now test folder-scale orchestration, latency, cost accounting, bounded concurrency, cancellation, resume and safe mutation—not discover basic semantic correctness for the first time.

**Files/functions:** cli.run; production.run_production_corpus; orchestrator.run_p1_p7; existing extraction_pool; grouping.embeddings/retrieval; llm_harness.budgets/harness/transport; readers.model_deepseek/_ollama; placement.run_corpus; existing evaluation and tools/groundtruth; apply_run.apply_selected/take_back; mutation.apply_plan/undo.

- [ ] Run the same verified path against the real target folder in no-move mode. Make optional semantic weights explicit and include their identity in evidence/cache records.
- [ ] Enforce configured worker/in-flight/request limits; measure actual model usage where the provider supplies it, and label estimates separately.
- [ ] Exercise rate limits, timeouts, interruption and restart. Persist each unfinished file's state; reuse completed work. Do not silently downgrade the model tier.
- [ ] Compare every selected file with human ground truth, preserving the difference between wrong leaf, correct parent, correct abstention and no decision. A correctness regression sends work back to Phase 2 or 3.
- [ ] Exercise freeze/apply/undo on a disposable sandbox copy only. Hash-compare files before/after/undo; refuse collisions and changed sources/destinations. No source-corpus mutation.

**Exact commands:**

~~~sh
PYTHONPATH=src python3 tools/reintegration.py folder --corpus .groundtruth/corpus --labels .groundtruth/labels.json --provider ollama --model-from-env REINTEGRATION_LOCAL_MODEL --require-live --workers 4 --max-inflight-model 2 --repeat 2 --interrupt-after 10 --resume --no-moves
PYTHONPATH=src python3 tools/reintegration.py move-roundtrip --sandbox-copy --cases normal,collision,changed-source,changed-destination,interrupted-copy --require-explicit-review
~~~

**Pass:** selected-file count equals the union of mutually exclusive terminal outcomes; zero silently absent files; no concurrency/budget overshoot; interruption resumes without losing or double-applying decisions; cache hits and actual/estimated usage are observable. Unchanged repeat reuses valid work. Every actual place decision points to an approved node and a model/user decision authority. The sandbox move restores identical content and original locations on verified undo; collision/change cases preserve both existing objects and report refusal.

No arbitrary accuracy target is invented here. Before the run, retain the owner's labeled expectations and abstention requirements. A lower wrong-placement count achieved by silently dropping files is failure.

### Phase 5 — Customizability pass

**Goal:** deliver the actual designed product surface over the now-working engine; users change organization without source edits.

**Existing files/functions:** review_surface.collect/presentation/items/residual/versions_view; tree_design.store.apply_review_action/open_draft; tree_design.user_edits.record_user_level_edit; facts.values.set_display_label/merge_values and plan-version display overlays; tree_design.catalogue/templates/freeze; privacy.policy; existing correction-learning store/gates; cli.apply_answers/apply_rejections.

**New UI and configuration work:** implement the missing TA4/TA6 canvas using the repository's existing review/action records as its backend. Add versioned user configuration and residual-review scheduling where no implementation exists; do not build a second placement engine.

- [ ] Expose the already-wired Phase 1 editing adapters as horizontal then vertical design gestures.
- [ ] Allow naming/alias changes separately from canonical evidence identity, dimension reorder/omit, branch split/merge/nest and deliberately uneven depth.
- [ ] Support heterogeneous groups without requiring one folder-wide situation assertion.
- [ ] Offer an approved custom-template proposal, plus editable user-defined residual destinations with keep/review-only/physical policy.
- [ ] Expose privacy/local/cloud mode, residual opt-in, shared-material policy and scoped correction/reset.
- [ ] Add non-destructive time-based residual review suggestions; no deletion or automatic expiry.
- [ ] Display meaningful version diffs; adopt explicitly and revalidate affected decisions. Preserve curated structures and unrelated branches.

**Exact commands:**

~~~sh
PYTHONPATH=src python3 tools/reintegration.py customize --scenario academic-to-personal --cases rename,alias,merge,split,nest,reorder,omit,uneven-depth,custom-template,user-residual,keep-only,privacy-mode,correction-reset,version-adoption,review-cadence --launch-review --no-moves
python3 -m pytest tests/reintegration/test_customization_roundtrip.py -v
~~~

**Pass, personally observable:** the user renames Academics to My study, merges two course-label aliases, changes term/course order, omits an optional level in only one branch, adds Things to Read as review-only, and leaves temporary screenshots in place. After closing and reopening the application, those choices persist; the next model dossier uses the approved names/options/policies; source files under src remain unchanged. Version diff/adoption is explicit. A custom proposal remains a draft until approved. Correction reset changes only its stated scope. A review-cadence event surfaces a suggestion and performs no file deletion or movement.

### Phase dependency summary

~~~text
Owner resolves Section 6 boundaries
  -> Phase 0: one real local-model bench decision
  -> Phase 1: production seams called, observation-only where still unsafe
  -> Phase 2: correct bounded inputs + privacy + cache
  -> Phase 3: correct semantic result application + per-file accounting
  -> Phase 4: real-folder scale + sandbox apply/undo
  -> Phase 5: full user customization surface
~~~

This ordering is deliberate: **do not wire the current lossy B result into active acceptance, or enable cloud against the current DOCX release shape, just to claim Phase 1 connectivity.**

## 6. Purpose/design conflicts and safety flags — unresolved

### Purpose/design conflicts requiring the owner’s decision

Your corrected purpose already establishes model authority. The unresolved decisions are the exact treatment of old contracts and safety-versus-semantic boundaries, not whether to ignore your instruction.

| Flag | Conflicting design/code | Decision needed; no resolution applied |
|---|---|---|
| C1 — Rules-first semantic extraction | [00:39](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:39>) and [00:41](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:41>) reserve LLM interpretation for ambiguity; [pending_fields_for](</Users/jy/GRAPH AGENT/src/model_facts.py:269>) suppresses rule-settled fields. | Confirm which existing semantic rules become candidate evidence instead of settled answers. Keep literal parsing, hashes and explicit user choices distinguishable from semantic classification. |
| C2 — Rule/fact precedence over model | [00:42](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:42>), [00:62](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:62>), cli.contradicts_stronger, facts.llm_seam. | Which contradiction checks are hard evidence-consistency constraints, and which are historical semantic rule vetoes that must instead be shown to the model/reviewer? |
| C3 — Model-free placement and numerical vetoes | [00:110](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:110>), [00:114](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:114>), placement.scoring.assess/needs_model_call and placement_validation._placement_site. | Retain support/margin as retrieval diagnostics/review triggers, or also as hard post-model rejection gates? Either way, automatic rule-only semantic placement conflicts with your corrected purpose. |
| C4 — Current-folder preservation heuristics | [00 curated-folder behavior](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:100>), _a_folder_made_for_this_keeps_it, _without_kind_only_moves, _staying_put_wins_a_tie. | Preserve explicit user “keep here” as authority. Decide which inferred preservation rules are hard move-scope constraints and which must become evidence/preferences supplied to the model. |
| C5 — Fixed semantic vocabulary and code-only normalization | cli.normalize_for_model, WORK_TYPE_VOCABULARY, empty normalizers mapping, one global situation. The recent work_type fix prevents .pdf being a folder, but closes vocabulary using the library's terms. | Which vocabularies remain closed schemas, and how can users add valid labels/aliases/types without editing Python? Do not remove schema validation to solve customization. |
| C6 — Privacy versus useful filename/OCR/profile context | [00 privacy](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:186>) keeps full text/raw OCR/local paths private while [00 residual dossier](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:124>) requires bounded filename/OCR/context. Filename is reference-only; OCR zone globally excluded. | Ratify the precise short-excerpt/filename/candidate-label materialization and consent/redaction policy. No blanket path or OCR release. Protected cloud defaults remain unchanged. |
| C7 — Missing prompt ratification | model_placement says C/D prompts are not ratified; only A_fact is marked wired. | Approve B, C, D and custom-template output contracts/prompts before enabling their live production consequence paths. This audit did not author or silently ratify them. |
| C8 — Automatic proposal/acceptance versus high-leverage review | [00:66](</Users/jy/GRAPH AGENT/planning/00-database-agent-product-design.md:66>) requires reviewed groups before tree design; cli.review_and_accept/choose_option substitute unattended defaults. | Define whether unreviewed outputs may appear as drafts, and what explicit action accepts groups/tree. Do not equate a rules-authored ACCEPTED row with user approval. |

### Safety/behavior flags, separate from ordinary bugs

| Severity / flag | Evidence and scope | Required treatment |
|---|---|---|
| **High — S1: full local DOCX body crosses the intended release boundary** | W8 was reproduced through the real extractor, Gate and dossier builder. Local-target gate returned Released; full body was serialized. The same observation/materialization shape feeds the cloud fact route. **No actual cloud disclosure was tested or caused.** | Block cloud rollout on this path until whole-text versus bounded-excerpt representation and final-request caps are verified. Keep evidence and diagnostic payloads local. |
| **High — S2: insufficiently specified contextual redaction** | The configured identifier classifier always returns None. Existing file-level/sensitive-observation gates help but do not establish that a selected ordinary excerpt cannot contain a sensitive identifier. | Ratify/implement the missing classifier and test identifier canaries. This is a demonstrated missing safeguard, not a claim that every identifier leaked. |
| **High behavioral — S3: unreviewed semantic group becomes “accepted/coherent”** | W2: no B judgment and no user review produced those semantics. This violates the designed review/provenance boundary. | Preserve draft/proposed state until appropriate model validation and explicit review. **No unapproved physical move was observed.** |
| **Medium — S4: indexed file lacks final persistent disposition** | W9: opaque-only run printed NothingToDesign, exited 1, and stored no placement decision. | Record visible per-file unresolved/review state even without a tree; do not fabricate a destination. |
| **High operational — S5: declared request ceiling is not enforced** | W8/D7: final payload unmeasured; one observation defeats the count cap. | Reject/defer safely before transport when bounded reduction cannot fit, with a recorded reason. |

**Safety mechanisms not found broken by this audit:** ordinary plan generation did not move files; explicit apply/undo paths and no-overwrite/freshness machinery are present; residual opt-in/keep semantics exist; protected-container handling is not interchangeable with unclassified status. They still require Phase 4 mutation verification before a production-success claim.

### Owner decision requested

Before implementation, please decide **whether existing score/margin and semantic-conflict rules should remain hard post-model vetoes, or become evidence/review triggers while only provenance, schema, privacy, frozen-tree and explicit user constraints remain hard gates**. C1–C8 identify the corresponding documents and functions to update together.

No conflict has been silently deleted, retained as newly approved policy, or resolved in favor of existing code. The diagnostic is complete; the product is not repaired.

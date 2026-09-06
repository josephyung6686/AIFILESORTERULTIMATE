# 105 — D2 prompt packet: four unwired sites and the A_fact glossary, drafted, stressed and measured, for ratification

Date: 2026-09-06. Status: **drafts for the owner's ratification — nothing here is ratified and nothing here is wired.**
Protocol: `103` §28.1 (requirements traced to `00`; a traced draft; stress cases; a bakeoff of at least two candidates under both models; ratification with the numbers attached). Governing rulings: `104` §13.5 (model decides, rules validate), §13.6 (grounding hard, the rest shown), §13.7 (model names, user confirms), §13.8 (refinement allowed, removal constrained); `00` Amendments of 2026-09-05.

Every template id below carries `unratified` and its date. The ratified A_fact files are untouched; every new file sits beside them under `src/llm_harness/library/`. The bench is `tools/promptbench/` and every number in this document was produced by a command written next to it.

## 0. How to read this packet, and what changed on 2026-09-06

Three process additions from the coordinator, all honoured here: work is committed per unit (each requirements trace, each draft, each bakeoff run), anything that may run longer than three minutes runs in the background and is polled, and every local request sets `num_ctx` explicitly above the measured prompt length and records the value used — Ollama otherwise truncates silently to 2,048 tokens and answers anyway.

Sections 1 to 5 follow the site order `103` §28.1 fixes (C and D, then B, then E), with the A_fact glossary revision (fix-chain step 1, `104` §11.2) placed first because every other site's numbers are downstream of it. Each site section has the same six parts: requirements traced to `00`; research applied; the candidates, with the winner and the loser and their numbers; the stress-case table; contract gaps found; the ratification question.

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

### 1.3 Results

*(pending the bakeoff)*

### 1.4 Stress cases

*(pending the bakeoff)*

### 1.5 Contract gaps found at A

None new. The two limits the ratified text already states stand (`82` §0 S1, S2): the value's minimal-substring rule is enforced only where the deployment has a normaliser, and the model's own spelling becomes the stored value identity.

### 1.6 The ratification question

*(pending the bakeoff)*

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

### 2.3 Results

*(pending the bakeoff)*

### 2.4 Stress cases

*(pending the bakeoff)*

### 2.5 Contract gaps found at C

G1 (conflict ids keyed on the wire, compared raw), G2 (R-15, a real `project` value is "invented"), G3 (no node profiles, opaque ids), G6 (the two numbers), in §7.

### 2.6 The ratification question

*(pending the bakeoff)*

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

### 3.3 Results

*(pending the bakeoff)*

### 3.4 Stress cases

*(pending the bakeoff)*

### 3.5 Contract gaps found at D

G1 (relationship ids keyed vs raw), G3 (no area profiles), G5 (same-file check is fail-open on keyed citations), G7 (broad parent and residual destination collapse to one disposition; only the injected `residual_action_of` keeps them apart), G8 (a return's target must be a frozen node), in §7.

### 3.6 The ratification question

*(pending the bakeoff)*

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

### 4.3 Results

*(pending the bakeoff)*

### 4.4 Stress cases

*(pending the bakeoff)*

### 4.5 Contract gaps found at B

G4 (no authorities constructed; `allowed_vocabulary` undefined), G9 (the seam carries no basis, no excerpt-to-member mapping, no retrieval channel), G11 (`apply_p8_verdict` drops label, category and per-member decisions — `104` R-16), in §7.

### 4.6 The ratification question

*(pending the bakeoff)*

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

### 5.3 Results

*(pending the bakeoff)*

### 5.4 Stress cases

*(pending the bakeoff)*

### 5.5 Contract gaps found at E

G10 (no channel for the schema id, the parent's expressed value, the sensitivity policy reference or the depth limit), G12 (no live caller: `routing.py`'s C3 refusal never becomes a request), in §7.

### 5.6 The ratification question

*(pending the bakeoff)*

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

| # | Site | What the contract cannot express or does wrongly | Where | Pinned by | Consequence for ratification |
|---|---|---|---|---|---|
| *(pending)* | | | | | |

## 8. Cloud calls used and tokens spent

*(pending — the bench ledger is the source; the cap is 400 calls.)*

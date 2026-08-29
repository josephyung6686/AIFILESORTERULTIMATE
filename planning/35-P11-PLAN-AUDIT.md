# P11 plan gap audit

Date: 2026-08-27
Scope: `planning/parts/P11-placement-residual/PLAN.md` (158 lines) audited against
`planning/parts/P11-placement-residual/SPEC.md` (838 lines), the live P8 surface under
`src/llm_harness/`, the live P9 surface under `src/grouping/`, `planning/parts/P10-tree-design-freeze/SPEC.md`,
`planning/30-p8-p9-connection-contract.md`, `planning/parts/_PLAN-AUTHORING-BRIEF.md`, and
`planning/parts/P9-grouping/PLAN.md` as the quality bar.

Every quotation below was confirmed with `grep -n` before it was written. Where I could not find a
string I say so rather than paraphrasing it as a quote.

---

## 0. The structural finding that frames everything else

P11's PLAN is not the same *kind* of document as P9's. Measured, not impressionistic:

| Metric | `P9-grouping/PLAN.md` | `P11-placement-residual/PLAN.md` |
|---|---|---|
| `**Files:**` blocks (create/modify/test paths per task) | 15 | **0** |
| `**Produces:**` / `**Consumes:**` interface blocks | 15+ | **0** |
| fenced ```python blocks (complete runnable code) | 17 | **0** |
| numbered `- [ ] **Step N: ...**` steps | ~70 | **0** |
| explicit RED step ("Run … Expected: FAIL because …") | 13 | **0** |
| `Done-means` references | present (P9 L1043 coverage map) | **0** |
| total checkboxes | — | 53 (all prose bullets) |
| fenced blocks of any language | many | **2** (the one `text` file-structure block, PLAN:28 and PLAN:49) |

`_PLAN-AUTHORING-BRIEF.md:42-53` states the required shape:

> Every task you write needs:
> - `**Files:**` — exact create / modify / test paths
> - `**Interfaces:**` — `Consumes:` and `Produces:` with exact signatures
> - `**Done-means:**` — which numbered Done-means items this task satisfies
> - Numbered `- [ ] **Step N: ...**` steps, each 2–5 minutes
> - **Complete runnable test code** in a fenced `python` block
> - A step that RUNS the test and states the expected **FAILURE**
> - **Complete implementation code** in a fenced `python` block
> - A step that runs it again and states **PASS**
> - A commit step with the exact `git commit -m` line

(verified: `grep -n "Complete runnable test code" planning/parts/_PLAN-AUTHORING-BRIEF.md` → line 48.)

P11's PLAN satisfies **one** of those nine bullets (the commit line, and only as inline prose, e.g.
PLAN:56 `Commit \`feat(p11): add append-only placement decision contract\``, not as a `bash` block).
`_PLAN-AUTHORING-BRIEF.md:54-56` is explicit about the consequence:

> **NO PLACEHOLDERS, EVER.** No stubs, no ellipses, no "similar to Task N", no "add appropriate error
> handling". A task that cannot be written out in full was decomposed wrong

Every one of P11's 53 bullets is at the altitude of "similar to Task N". PLAN:53 is representative:
*"Write failing round-trip tests for one `PlacementDecision` shape covering normal and residual
origins, all eight residual actions, node-only destinations, evidence/conflicts/alternatives,
privacy/review, two-condition data, `returned_from`, and `supersedes`/`superseded_by`/`supersede_reason`."*
That is a **summary of a task**, not a task. It names no field types, no test function, no assertion.

This is not a stylistic complaint. It is the reason Section A below has so many MISSING rows: a plan
written at this altitude cannot be checked for coverage, because a bullet like PLAN:53 can be read as
covering any field you name and no field you name.

**Quantified evidence that the record shape was never enumerated.** Grepping the whole PLAN for the
contract field names the SPEC publishes:

```
PlacementDependencies        0     decision_depth               0
ResidualDependencies         0     unsupported_levels           0
SiteDependencies             0     evidence_type                0
CallDependencies             0     node_role                    0
record_cd_verdict            0     marked_state                 0
evidence_snapshot_id         0     ask_user                     0
allowed_vocabulary           0     mark_state                   0
revalidate_for_plan          0     abstention_reason            0
EvidenceItem                 0     two_condition                0
Conflict                     0     handling_class               0
ModelCallRequest             0     model_eligibility            0
residual_set                 0     consent_audit_ref            0
set_decision                 0     lifecycle_policy_ref         0
reason_not_placed            0     excluded_outliers            0
shared_parent_node_id        0     expected_values              0
root_anchor                  0     existing_path                0
refinement_disposition       0     "6.12"                       0
"Done means"                 0     blocked_pending_user         0
```

(command: `for s in …; do grep -c -- "$s" planning/parts/P11-placement-residual/PLAN.md; done`)

---

## A. SPEC-to-PLAN coverage

Legend: **C** = covered, **P** = partial (named in prose, contract not pinned), **M** = missing (no task).

### A.1 — §6 obligations (SPEC "Design slice owned", SPEC:36-50)

| SPEC requirement | PLAN task | Verdict |
|---|---|---|
| SPEC:40 §6.2 destination-node retrieval index over P10's profiles; retrieval returns approved nodes only; inventing `Math Stuff` forbidden | Task 2, PLAN:61-62; Task 3, PLAN:69 | **C** |
| SPEC:41 §6.3 retrieval driven by direct facts, accepted membership, graph relationships, structural relationships, full-text/OCR embeddings, curated folders and user labels; **conflicting evidence actively suppresses nodes** | Task 3, PLAN:67-68 | **P** — the six drivers are listed as fixture names, never as a contract naming which P4/P6/P9 read surface supplies each. P9's PLAN:41 names its P6 surfaces by symbol (`proposal_eligible`, `event_facts`, `session_facts`, `family_facts`, `active_allowlist_for`, `evidence_chain`); P11's names none |
| SPEC:42 §6.4 **node-local evidence graph** per file/group — compare the target against the node's approved community, not against a folder name | — | **M** — no task, and no module in PLAN:29-48 builds one. `src/placement/retrieval.py` (PLAN:34) is described as "bounded candidates, conflicts, shallow fallback"; there is no graph module. Done-means 5 (SPEC:627-630) requires "Placement builds a node-local evidence graph with typed edges" |
| SPEC:43 §6.5 local clustering only; **never whole-corpus reclustering**; typed relationships; a semantic embedding alone is insufficient; a file connected only by generic similarity or one high-frequency entity stays uncertain | Task 3, PLAN:69 ("Embeddings remain retrieval-only"); Task 4, PLAN:77 | **P** — the embeddings half is covered. The "never whole-corpus reclustering or renumbering" guarantee (Done-means 5, SPEC:628) has no task and no guard in Task 12's guard list (PLAN:133). "One high-frequency entity" has no fixture |
| SPEC:44 §6.6 LLM as hierarchical destination judge; never called for direct unique matches; bounded placement dossier, never the whole tree | Task 4, PLAN:75; Task 5, PLAN:82 | **C** |
| SPEC:45 §6.7 reason broad→narrow; prefer an approved shallower path or approved scoped `General`; **never fill a missing slot because a complete-looking path is aesthetically preferable** | Task 3, PLAN:69 | **P** — "never fill unsupported dimensions" is there. `decision_depth` / `node_depth` / `supported_depth` / `unsupported_levels[]` (SPEC:331-334) appear **zero times**, so the record cannot say *which* levels were deliberately left unfilled, which is exactly what Done-means 7 (SPEC:634-638) asserts |
| SPEC:46 §6.8 group-level placement first-class; confirm shared parent, then classify members; one coherent group plan; outliers excluded and explained | Task 6, PLAN:89-90 | **P** — ordering and outliers are stated. The `group_plan` record's four fields (SPEC:509-518: `shared_parent_node_id`, `member_decisions[]`, `excluded_outliers[]{file_id, conflicting_fact, evidence_ref, routed_to}`) are never named |
| SPEC:47 §6.9 multi-home: shared branch / primary-home / alias / mandatory review; with no shared branch **abstain or ask** — never arbitrarily pick one institution | Task 6, PLAN:91 | **P**, with a deviation. PLAN:91 says *"If no shared branch or ratified ask/abstain selector exists, fail closed"*. The SPEC's outcome is `abstain` **or** `ask_user` (SPEC:437-439, SPEC:643-645). `ask_user` appears zero times in the PLAN. "Fail closed" is a third behaviour the SPEC does not authorise and is not obviously the same as emitting an `abstain` record |
| SPEC:48 §6.10 two-condition acceptance rule; correct abstention as success | Task 4, PLAN:74-77 | **C** for the rule. "Correct abstention is a successful outcome" survives only as UX prose at PLAN:134 |
| SPEC:49 §6.11 the structured placement decision record | Task 1, PLAN:53-55 | **P** — see A.5, which itemises it. Roughly 10 of ~45 fields are named |
| SPEC:50 §6.12 the nine-step post-tree pipeline | — | **M** — `grep -n "6.12" PLAN.md` returns nothing. Note the SPEC is also at fault here: SPEC:50 says the pipeline is "(reproduced under [Done means](#done-means))" and SPEC:607 says "The nine-step §6.12 pipeline runs end to end", but the SPEC never enumerates the nine steps. They exist at `planning/01-product-design-structured.md:1295-1306` and are reproduced in section D below |

### A.2 — §7 obligations (SPEC:52-64)

| SPEC requirement | PLAN task | Verdict |
|---|---|---|
| SPEC:56 §7.1 residual is a separate stage that runs **only after** normal classification; no global `Misc`/`Other`/`Unsorted` | Task 8, PLAN:103 | **C** |
| SPEC:57 §7.5 residual surfacing screen — a visible summary divided into understandable review sets | Task 8, PLAN:103 | **P** — the `residual_set` record (SPEC:526-534) has seven published fields. PLAN:103 paraphrases five as "type/age/evidence/sensitivity/weak-neighbor metadata" and omits **`reason_not_placed`** (SPEC:533-534, "why the normal pipeline could not safely place these files") entirely — grep count 0 |
| SPEC:58 §7.6 set-level decisions before any per-file model review | Task 8, PLAN:104 | **C** for the gate. **M** for the record: `residual_set_decision.choice`'s four values (SPEC:538-542) — `leave_in_place`, `review_with_model_against_approved_residual_folders`, `send_to_approved_node(node_id)`, `create_custom_branch` — are never enumerated; PLAN:104 names one and PLAN:105 alludes to another |
| SPEC:59 §7.7 the eight-action controlled action set | Task 9, PLAN:110 | **P** — all eight are listed in English at PLAN:110. Neither the outcome+qualifier mapping (SPEC:390-399) nor P8's machine spellings (`llm_harness/vocabulary.py:52-61`) are named. See B and E |
| SPEC:60 §7.8 worked examples (Columbia screenshot returns to §6; `Gate B12` must not produce `Travel/Flight Gate B12`) | Task 9, PLAN:111; Task 3, PLAN:69 | **C** |
| SPEC:61 §7.9 residual validation and the loop back to §6 | Task 9, PLAN:111 | **P** — `returned_from` is named (PLAN:111, PLAN:112). SPEC:443-445's "**Both records persist** … the residual finding is never discarded because placement later succeeded" has no task and no test |
| SPEC:62 §7.10 editable recommendations, **bulk decisions**, learned preferences, **negative examples** | Task 10, PLAN:117-118 | **P** — "bulk" appears once (PLAN:118) as an action name. `action = accept_bulk`, `bulk_member_refs[]`, `bulk_basis` (SPEC:240-241) are absent. §7.10's required behaviour at SPEC:756-758 — PDFs rejected out of Receipts and Confirmations "must route future similar files back toward Academic or Applications review" — has no task and no fixture |
| SPEC:63 §7.11 non-destructive time-aware lifecycle; never delete, never auto-expire | Task 1, PLAN:54 ("no path/deletion/expiry fields"); Task 12, PLAN:133 | **P** — the prohibition is covered. `residual.lifecycle_policy_ref` (SPEC:383, "a review policy — never a deletion or expiry") is never named |
| SPEC:64 §7.12 residual completes the philosophy: exceptions must not pollute the main tree | — | **M** as a distinct assertion; arguably subsumed by §7.1's task |

### A.3 — Contract in

| SPEC requirement | PLAN task | Verdict |
|---|---|---|
| SPEC:115-128 fifteen P10 node fields | Task 2, PLAN:61 | **P** — PLAN:61 lists "node_id, role, disposition, expected values, parent/child context, labels, accepted groups, anchor excerpts, exclusions, privacy restrictions, user edits", which **conflates the node record (SPEC:117-128) with the §6.1 profile (SPEC:139-143)** — "anchor excerpts", "exclusions" and "user edits" are profile fields, not node fields. Omitted node fields: `node_type`, `root_anchor`, `ordinal`, `template_context`, `dimension`, `explanation`, `handling_class` |
| SPEC:130-137 `accepts_placement`; **node existence is not legality**; legal set is `{node_id : plan_version = frozen version, accepts_placement = true}` | Task 2, PLAN:61-62 | **C** |
| SPEC:139-145 the §6.1 profile arrives from P10; P11 builds none | Task 2, PLAN:62 | **C** |
| SPEC:147-150 residual nodes arrive as ordinary nodes carrying template identity + `disposition`; `review-only`/`leave-in-place` are still legal destinations for a *decision* | Task 8, PLAN:105 | **P** — PLAN:105 says P11 "may name only frozen residual node IDs" but never states that `disposition` decides whether a mutation follows (SPEC:396, SPEC:559) |
| SPEC:152-153 shared-material policy carried on the tree | Task 2, PLAN:60; Task 6, PLAN:91 | **C** |
| SPEC:155-158 no filesystem paths from P10 **other than `existing_path` on an `existing` node** | Task 12, PLAN:133 (AST guard vs "path strings") | **P** — `existing_path` is never named (grep 0). A blanket guard against path strings will trip on the one legal path-bearing field P10 publishes (`P10 SPEC` node table row `existing_path`) |
| SPEC:160-161 freeze is a precondition | Task 2, PLAN:60 | **C** |
| SPEC:165-166 P9 group id, label, category, members with **all three** `Membership.basis` kinds, identified outliers, recorded conflicts | Task 6, PLAN:89 | **P** — the three bases are named. `Group.group_category`, `Group.display_label`, `Membership.outlier_flag`, `Membership.conflicts` are not; nor is the fact that "accepted" is resolved from `GroupAcceptance` as-of a plan version. See C |
| SPEC:176-178 two `user-attached` constraints (never `validated`, never `auto_eligible`) | Task 1, PLAN:54; Task 4, PLAN:77 | **C** — the one place the PLAN is precise |
| SPEC:185-186 P6 `file_facts` rows with reliability state and evidence reference | Task 3, PLAN:67 | **P** — "fixtures for direct/validated facts"; no P6 read surface named by symbol |
| SPEC:193-200 M14: cite `observation_key`, never `observation_id` | Task 1, PLAN:54 | **C** |
| SPEC:202-206 M5: surrounding context is **three** fields (`context_before`, `context_after`, `context_truncated`), not §2.8's one | — | **M** — grep count 0 for all three. P8 already carries them on `ReleasedEvidence` (`src/llm_harness/records.py:255-257`), so this is a live shape P11 must reproduce |
| SPEC:210-212 P7 gate is passed **before any dossier is assembled**, not after | Task 7, PLAN:96; Task 5, PLAN:82 | **P**, and mis-ordered — see D. PLAN:82 forbids P11 calling `Gate.release`, but `run_call` takes `gate: Gate` as a required keyword (`src/llm_harness/harness.py:328`), so P11 must hold and pass one. No task says who supplies it |
| SPEC:220-224 placement dossier contents — eleven literal items | Task 5, PLAN:82 | **P** — PLAN:82 names five ("target file/group, legal candidate profiles, evidence keys, conflicts, bounded deterministic scores"). Missing: relevant extracted excerpts or OCR, accepted group memberships, graph anchor evidence, representative files already accepted in those nodes, missing fields |
| SPEC:226-229 residual dossier contents — ten literal items | — | **M** — no task builds a Site D request. Task 9 maps eight actions into the record but never issues or receives a residual model call |
| SPEC:233-234 P1 identity/path history/event log; **P2's replay-bundle interface into which P11's stage assertions are registered (§8.5)** | Task 11 partially | **M** for the replay-bundle registration; the PLAN never names it |
| SPEC:238-244 P13 `review_action` in full on four surfaces, `subject_ref` ∈ {`decision_id`, `group_plan_id`, `set_id`}, carrying `bulk_member_refs[]`, `bulk_basis`, `correction_scope`, `presented_state_ref`; **all eight §7.7 actions arrive on this record**; P11 authors the decision (M8) | — | **M** — no receiver task and no receiver module. Compare P9's PLAN, which gave this a whole task (P9 PLAN:765 "Task 11: Receive P13 group actions through a fixture-only back-edge") plus a named fixture file (P9 PLAN:86 `tests/p9/p13_fixtures.py`) and a named gate (P9 PLAN:52 G-P13). P11's PLAN declares gate **G-P13** at PLAN:24 and then no task consumes it |

### A.4 — Contract out, P2 stage_output (SPEC:248-288)

| SPEC requirement | PLAN task | Verdict |
|---|---|---|
| SPEC:255-256 exactly two `stage_id`s: `candidate_node_retrieval`, `placement_scoring` | Task 11, PLAN:124 | **C** — and both are live in P2's closed set (`src/eval_harness/vocabulary.py:27-28`) |
| SPEC:261-263 each envelope carries `inputs[]` = the `subject_ref`s of the `grouping`, `tree_design` and `factual_validation` stage outputs it consumed | Task 11, PLAN:124 ("exact inputs") | **P** — the three upstream stages are never named |
| SPEC:266-288 envelope vocabulary is P2's, record vocabulary is P11's; the five-row mapping table; a budget deferral is `deferred`+`ceiling_reached` and **never** `abstained` | Task 11, PLAN:125 | **C** |
| SPEC:583-585 two stage assertions matching §8.5's literal metric names (*Placement quality*, *Residual quality*); a correct abstention **passes** both | Task 11 | **M** — those are P2 **dimensions**, not stages (`src/eval_harness/vocabulary.py:41-42`), delivered through `record_stage_output(..., dimension_values=…)` (`src/eval_harness/stage_output.py:100`). The PLAN never names `dimension_values`, `placement`, or `residual`. Note `residual` is a dimension with **no same-named stage** (`src/eval_harness/vocabulary.py:6-7`), so which of P11's two stages carries it is an unresolved question the PLAN does not raise |
| PLAN:124 asserts the envelope carries "plan version, thresholds, and provenance" | — | **factually wrong**: `record_stage_output`'s signature (`src/eval_harness/stage_output.py:96-100`) is `(conn, *, run_id, stage_id, subject_ref, outcome, payload, version_tuple_ref, inputs, budget_state, dimension_values)`. There is no `plan_version` or `thresholds` parameter; those can only ride in the opaque `payload` |

### A.5 — Contract out §1, the placement decision record (SPEC:290-486)

This is the SPEC's central deliverable — SPEC:19 calls publishing the single record shape "this part's
primary obligation". Field by field:

| Field (SPEC line) | PLAN | Verdict |
|---|---|---|
| `decision_id`, `plan_version` (SPEC:299-300) | PLAN:54 "plan version required" | **C** |
| `supersedes` / `superseded_by` / `supersede_reason` (SPEC:301-304) | PLAN:53 | **C** |
| `origin_stage ∈ placement \| residual` (SPEC:306) | — | **M** (grep 0) |
| `returned_from` (SPEC:307-308) | PLAN:53, PLAN:111 | **C** |
| `subject{kind ∈ file\|group, file_id, content_hash, group_id, member_file_ids}` (SPEC:310-313) | — | **M** — no field named |
| `group_plan_id` (SPEC:314) | PLAN:89 ("one `group_plan_id`") | **C** |
| `outcome`, seven values (SPEC:316-318) | PLAN:110, PLAN:111 | **P** — `place`, `return_to_placement`, `leave_in_place` appear; `mark_review_later`, `mark_state`, `ask_user`, `abstain` do not (grep 0 for the first three) |
| `destination{node_id, node_role}` (SPEC:319-323) | PLAN:54, PLAN:61 | **P** — `node_role` never named (grep 0); PLAN:61 says "role" |
| `return_target{kind ∈ confirmed_domain_group \| accepted_graph_or_purpose_packet, id}` (SPEC:324-327) | — | **M** |
| `marked_state ∈ protected \| unsupported \| null` (SPEC:328) | — | **M** |
| `ask {question, options[]}` (SPEC:329) | — | **M** |
| `decision_depth{node_depth, supported_depth, unsupported_levels[]}` (SPEC:331-334) | — | **M** — and this is the field SPEC:414-417 says replaced the deleted `destination.kind`, so its absence deletes the child-vs-broad-parent distinction from the record |
| `evidence_type`, six values (SPEC:335-336) | — | **M** |
| `confidence_class`, four values (SPEC:337-340) | PLAN:75 (one value: `"exact fact match"`) | **P** |
| `matching_facts[]{file_fact_id, field, value, reliability, evidence_ref}` (SPEC:342-343) | PLAN:53 ("evidence") | **P** |
| `group_support{group_id, membership}` (SPEC:344-347) | PLAN:89 | **P** |
| `graph_anchors[]{edge_type, from, to, anchor_file_id}` (SPEC:348) | — | **M** — consistent with §6.4's missing graph |
| `conflicts_considered[]{kind, conflicting_value, suppressed_node_ids[], evidence_ref}` (SPEC:349-350) | PLAN:68 | **P** — named, shape unpinned. See B for the collision with P8's own `Conflict` |
| `alternatives[]{node_id, support_score, rank}` (SPEC:351) | PLAN:75 | **P** |
| `two_condition{support_score, support_threshold, meets_threshold, margin_over_next, margin_threshold, meets_margin, verdict, requires_review}` (SPEC:353-363) | PLAN:74-76 | **P** — `margin_over_next`, `meets_margin`, `true_vacuous` are named exactly (PLAN:76). `support_threshold`, `margin_threshold`, `meets_threshold`, `verdict`, `requires_review` are not, and `two_condition` as a block name has grep count 0 |
| `abstention_reason`, eight values + null (SPEC:364-367) | — | **M** (grep 0) |
| `deferred_stage` (SPEC:368-370) | PLAN:125 | **C** |
| `privacy{handling_class, model_eligibility, consent_audit_ref}` (SPEC:372-375) | PLAN:96 (prose) | **P** — all three field names have grep count 0 |
| `review_policy`, three values (SPEC:376-377) | PLAN:97 | **P** — `blocked_pending_user` never named |
| `explanation` — must state the actual basis, must not claim evidence the file does not carry (SPEC:378-379) | PLAN:98, PLAN:134 | **C** |
| `residual{set_id, set_decision, lifecycle_policy_ref}` (SPEC:381-383) | — | **M** |
| SPEC:386-399 the §7.7 action → outcome+qualifier mapping table | PLAN:110 | **P** — the eight actions are listed; the mapping is not |
| SPEC:401-406 the §6 outcome mapping (child → `place`/`ordinary`; broad parent → `place`/`ordinary` + `unsupported_levels[]`; scoped fallback → `scoped-general`; shared branch → `shared-material`; none → `abstain`) | — | **M** |
| SPEC:437-439 `ask_user` is emitted **only** on the placement path, under §6.9 | — | **M** |
| SPEC:441-445 `return_to_placement` is emitted **only** on the residual path; both records persist | PLAN:111 | **P** |
| SPEC:447-486 B8(b) the one-legal-candidate rule; `meets_margin` is `true` by vacuity not measurement; a file clearing no threshold abstains **even when only one destination exists** | PLAN:76 | **C** — the plan's strongest task |
| SPEC:462-475 the verdict vocabulary is P8's, carried unchanged; **a deterministic exact-fact match issues no model call and still records a verdict in this vocabulary** | — | **M** — PLAN:75 records `confidence_class` on the deterministic path but never a `verdict`. This is the sentence that makes P8's `OUTCOMES` a P11 field rather than a P8 return value |

### A.6 — Contract out §2-§6

| SPEC requirement | PLAN task | Verdict |
|---|---|---|
| SPEC:496-500 index-entry fields, literal from §6.2 (template fields, accepted group labels, user-approved display name, representative member files, anchor excerpts, known document types, parent and child context, explicit user edits); keyed to one `node_id`; built only where `accepts_placement = true` | Task 2, PLAN:61-62 | **C** |
| SPEC:502-504 retrieval returns approved nodes only; conflicting evidence **suppresses** and the suppression is recorded | Task 3, PLAN:68 | **C** |
| SPEC:508-521 the `group_plan` record | Task 6, PLAN:89-90 | **P** — fields unnamed |
| SPEC:526-542 `residual_set` and `residual_set_decision` records | Task 8, PLAN:103-105 | **P** — fields unnamed, four `choice` values unnamed |
| SPEC:545-547 **Ordering is contractual**: no per-file residual model call until that set has a `residual_set_decision`; `leave_in_place` produces **zero** model calls | Task 8, PLAN:104 | **C** |
| SPEC:551-567 **P12 consumes only `outcome = place`**; the seven-outcome table; "six outcomes, not five" | Task 12, PLAN:132 (a seam test exists) | **P** — the seven-row behaviour table has no task; SPEC:565-567's note that `abstain` is the sixth is not carried |
| SPEC:569-571 a `place` record whose `review_policy` is `review_required`/`blocked_pending_user` is not yet a plan; `deferred_stage` never becomes a plan | Task 7, PLAN:97; Task 11, PLAN:126 | **P** |
| SPEC:573-579 P11 supplies `destination.node_id`, **the subject's expected content hash**, and the reason-and-evidence summary; P11 supplies "Requested destination node" and never "Resolved destination path" | PLAN:133 (guard) | **P** — "expected content hash" and "reason-and-evidence summary" are never named |

### A.7 — Done means (SPEC:605-671)

No task in the PLAN references a Done-means number (`grep -c "Done-means"` → 0). The PLAN's
Coverage table (PLAN:149-158) has **8 rows** against the SPEC's **16 numbered Done-means plus 10b**.
Items with no traceable task:

| Done-means | PLAN | Verdict |
|---|---|---|
| 1 (SPEC:610-612) one record, two paths; all eight actions round-trip; no ninth | PLAN:53, PLAN:110 | **C** |
| 2 (SPEC:614-619) unknown node fails **and** `accepts_placement = false` fails; **both tests run** | PLAN:54, PLAN:62 | **C** |
| 3 (SPEC:620-622) **index entries exist before matching** — every profile indexed before the first file is placed | — | **M** — an ordering assertion; no task states it |
| 4 (SPEC:623-626) conflicts suppress (Duke/Columbia, Spring 2025/2026) | PLAN:67-68 | **C** |
| 5 (SPEC:627-630) node-local, not global; **never triggers whole-corpus reclustering or renumbering** | — | **M** |
| 6 (SPEC:631-633) LLM not called for direct unique matches; zero model calls | PLAN:75 | **C** |
| 7 (SPEC:634-638) shallow beats invented; `decision_depth.unsupported_levels` records the level not filled | PLAN:69 | **P** — the field is absent |
| 8 (SPEC:639-642) group plans coherent; outlier excluded with its conflicting fact, routed to a legal branch or the review queue | PLAN:89-90 | **P** — `routed_to: node_id \| review_queue` absent |
| 9 (SPEC:643-645) multi-home never arbitrary; `abstain` **or** `ask_user` | PLAN:91 | **P** — see A.1 §6.9 |
| 10 (SPEC:646-649) two-condition recorded, not just applied | PLAN:74-77 | **C** |
| 10b (SPEC:650-655) degenerate case does not become a funnel; **a fixture asserts both halves** | PLAN:76 | **C** |
| 11 (SPEC:656-657) abstention is a **pass** in P2's assertions | — | **M** |
| 12 (SPEC:658-660) residual runs second; no per-file call before its set decision | PLAN:103-104 | **C** |
| 13 (SPEC:661-664) the §7.9 loop closes; Columbia → `return_to_placement`, both records persist; `Gate B12` → approved broad destination **or leave-in-place** | PLAN:111 | **P** — "both records persist" and the leave-in-place alternative are absent |
| 14 (SPEC:665-667) budget exhaustion visibly different from abstention | PLAN:125-126 | **C** |
| 15 (SPEC:668-669) nothing is destroyed; the record shape **cannot express** deletion/expiry | PLAN:54, PLAN:133 | **C** |
| 16 (SPEC:670-671) a new plan version never silently reclassifies | PLAN:119 | **C** |

### A.8 — Cross-cutting answers (SPEC:675-787)

| SPEC requirement | PLAN task | Verdict |
|---|---|---|
| SPEC:683-693 eight §8.2 event appends (index entry built; candidate retrieval performed; placement recommendation emitted, **including `abstain`**; group plan emitted; residual set surfaced + set decision; residual recommendation; return-to-placement issued and linked; user decision) | — | **M — and this is a hard build blocker.** `src/database_agent/events.py:106-133` rejects any unregistered `event_type` (`UnregisteredEventType`), and `events.py:62-65` says of P11's eight: *"P11's eight typed specializations of "placement recommendation" belong here and are ABSENT ON PURPOSE … When P11 prints the eight, add them here with base="placement recommendation"."* Registration is import-time and there is no runtime call (`events.py:39-41`). No P11 task edits `src/database_agent/events.py`, and PLAN:29-48's file structure contains no P1 file. **P11 cannot append a single event as planned** |
| SPEC:695-697 each event carries the §8.2 required fields incl. model version and prompt fingerprint | — | **M** |
| SPEC:699-710 never overwrites; M1's three columns; the chain is followable **forward** | Task 1, PLAN:53 | **C** |
| SPEC:714-717 seven §8.6 ceilings owned by P11 (max retrieved neighbors; max local graph neighborhood; max candidate cluster size; max residual files per batch; max dossier tokens; max LLM calls per thousand files; max model cost per scan) | Task 3, PLAN:68 ("injected ceilings") | **P** — none of the seven is enumerated. P9's PLAN named its ceiling adapter by module (`src/grouping/config.py`, P9 PLAN:70) |
| SPEC:719-722 degradation order: deterministic first, graph retrieval only for meaningful incomplete evidence, LLM reserved for bounded ambiguity | Tasks 4→5 implicitly | **P** — never stated as a rule |
| SPEC:724-727 a dossier over token budget must not truncate silently: summarize, preserve anchor excerpts, split, or defer | Task 11, PLAN:126 ("no silent truncation of decisive evidence") | **P** — this is P8's reduction ladder (`llm_harness/vocabulary.py:67-75`, `REDUCTION_RUNGS`), supplied through `CallDependencies.unreduced_fits / summarized_fits / anchors_fit / split_shard_fits / split_shards` (`src/llm_harness/harness.py:95-99`). P11 must author those five predicates; no task does |
| SPEC:729-734 budget exhausted → `abstain` + `budget_deferred` + `deferred_stage`; never a cheaper rule | Task 11, PLAN:125-126 | **C** |
| SPEC:738-743 thirteen recorded correction actions | Task 10, PLAN:118 (seven) | **P** |
| SPEC:745-749 scope explicit on every record (file/group/node/template/domain/corpus); §8.7's transcript example is the governing test | Task 10, PLAN:117 | **P** — the six scopes are live at `src/database_agent/events.py:99-101` and never named |
| SPEC:751-758 negative examples first-class; **before emitting `outcome = place` P11 queries P1 `learning_records`** for `placement`/`(subject_id, node_id)` or `residual`/`(file_id, residual_node_id)`; a matching unrescinded reject skips that node | Task 10, PLAN:117 | **P**, and mis-ordered (see D). PLAN:117 also mis-describes the API: `learning_records(conn, scope, subject_id)` (`src/database_agent/learning.py:46-47`) takes **only** scope and subject; `proposal_class` and `basis_key` are columns on the returned rows, filtered by the caller — the pattern P8 uses in `llm_harness/eligibility.suppressed_by_learning` |
| SPEC:761-763 a user creating a custom folder is a **tree edit** routed to P10 → new plan version | Task 8, PLAN:105 | **C** |
| SPEC:767-770 what belongs to a plan version (every decision, every group plan, the whole §6.2 index, residual set decisions, placement policy settings) | Task 1, PLAN:55 | **P** — the tables are created without saying which are plan-scoped and which are shared |
| SPEC:777-780 what belongs to the shared evidence database, unchanged across versions | — | **M** |
| SPEC:782-787 on a new plan version P11 re-projects; removed-node decisions marked for renewed review; never silently remapped; learned preferences filtered by node existence | Task 10, PLAN:119 | **P** — the last clause (preferences filtered by whether the node still exists) is absent |

### A.9 — MISSING tally

Counting rows marked **M** across A.1–A.8:

A.1: §6.4, §6.12 → **2**
A.2: §7.12 → **1**
A.3: M5 three context fields; residual dossier contents; P2 replay-bundle registration; P13 `review_action` receiver → **4**
A.4: §8.5 dimension values → **1**
A.5: `origin_stage`; `subject{}`; `return_target`; `marked_state`; `ask`; `decision_depth`; `evidence_type`; `graph_anchors[]`; `abstention_reason`; `residual{}`; the §6 outcome mapping; `ask_user` placement-only rule; the deterministic-path verdict → **13**
A.6: (none fully missing) → **0**
A.7: Done-means 3, 5, 11 → **3**
A.8: the eight §8.2 event appends; the §8.2 required event fields; the shared-evidence-database split → **3**

**Total MISSING: 27.** Plus 44 PARTIAL and 26 COVERED.

---

## B. What P8 already built for P11

Read in full: `src/llm_harness/placement_validation.py` (630 lines) and
`tests/p8/test_p8_placement_validation.py` (638 lines).

### B.1 — The two dependency records P11 must supply

```python
# src/llm_harness/placement_validation.py:80-86
@dataclass(frozen=True, slots=True)
class PlacementDependencies:
    node_exists: Callable[[str, str], bool]
    support_threshold: object
    margin_predicate: Callable[[object, object], bool]
    sensitivity_policy: Callable[[Dossier, Mapping[str, object]], bool]

# src/llm_harness/placement_validation.py:88-92
@dataclass(frozen=True, slots=True)
class ResidualDependencies:
    node_exists: Callable[[str, str], bool]
    sensitivity_policy: Callable[[Dossier, Mapping[str, object]], bool]
    approved_target_ids: tuple[str, ...]
```

Semantics, read off the call sites:

- `node_exists(node_id, plan_version) -> bool` — called at `:222` and `:322`. **This is exactly
  SPEC:134-137's legality membership test**, and P11 owns it: `{node_id : plan_version = frozen
  version, accepts_placement = true}`. Note that P8 passes `dossier.plan_version or ""` (`:209`,
  `:317`), so an empty plan version reaches the oracle as `""`.
- `support_threshold: object` — compared as `float(support) < float(dependencies.support_threshold)`
  at `:246`. P8 supplies no default; this is SPEC Open question 1 (SPEC:802-804), still open.
- `margin_predicate(support, next_support) -> bool` at `:253`. Also unset by design.
- `sensitivity_policy(dossier, payload) -> bool` at `:237` and `:328`. A `False` return is a
  `REJECT` with `SENSITIVITY_POLICY_VIOLATION` (Site C) or `SENSITIVITY_RESTRICTION_IGNORED` (Site D).
- `approved_target_ids: tuple[str, ...]` — Site D only, checked at `:321-325`.

A `None` in any field is detected by `_missing_placement` (`:156-163`) / `_missing_residual`
(`:166-171`) and returns `ValidationUnavailable(missing=(…))` before any validation runs; the tests
pin this at `:384-421`. Note `_missing_residual`'s name list at `:167` is `("node_exists",
"sensitivity_policy", "approved_target_ids")` and the test at `:421` asserts `"residual_actions" not
in result.missing` — i.e. the controlled action set is P8's, not an injection.

**How they reach P8.** Not directly. `run_call` takes `validation_dependencies` (`harness.py:331`),
a `CallDependencies` (`harness.py:84-104`), whose `site_dependencies` field is a
`SiteDependencies` (`sites.py:82-104`):

```python
SiteDependencies(fact=None, placement=PlacementDependencies(...), residual=None, template=None)
```

`dispatch` (`sites.py:264-277`) routes on `dossier.call_site` and returns
`ValidationUnavailable(missing=("placement_dependencies",))` if the bundle for that site is `None`.

> **Seam gap.** Neither `SiteDependencies`, `PlacementDependencies`, `ResidualDependencies` nor
> `CallDependencies` is exported from `src/llm_harness/__init__.py`, whose `__all__` is the eight
> names `planning/30-p8-p9-connection-contract.md:24-31` froze. P11 must import from
> `llm_harness.sites` and `llm_harness.placement_validation` — module paths the frozen contract does
> not name. `planning/30-p8-p9-connection-contract.md:74-76` records the same problem for P9
> ("P9 passes `llm_harness.sites.SiteDependencies`") without amending the export list.

### B.2 — Every validation P8 already performs at Site C, in order

From `_placement_site` (`placement_validation.py:200-264`), in execution order. P11 must not
re-implement any of these:

| # | Check | Line | Result |
|---|---|---|---|
| 1 | `destination in (None, "none")` | :210 | `ABSTAIN` / disposition `no_supported_destination`, no reasons |
| 2 | `destination not in dossier.allowed_vocabulary` | :220 | `REJECT` / `INVENTED_NODE` |
| 3 | `not node_exists(destination, plan_version)` | :222 | `REJECT` / `NODE_NOT_IN_FROZEN_TREE` |
| 4 | invented dimension value not in vocabulary, by `dimension` field | :185-197, :224 | `REJECT` / `INVENTED_DATE` \| `INVENTED_INSTITUTION` \| `INVENTED_PROJECT` |
| 5 | any `per_dimension_support[].support == "unsupported"` | :227 | `REJECT` / `SLOT_FILLED_WITHOUT_EVIDENCE` |
| 6 | any `dossier.conflicts[].conflict_id` absent from `payload["conflicts_considered"]` | :229-236 | `REJECT` / `CONFLICT_IGNORED` |
| 7 | `sensitivity_policy(...)` false | :237 | `REJECT` / `SENSITIVITY_POLICY_VIOLATION` |
| 8 | `payload["generic_hub"] is True` **or `destination == "node-hub"`** | :239 | `WEAK` / `GENERIC_HUB_ONLY` |
| 9 | `"support"` absent from payload | :241 | `WEAK` / `BELOW_SUPPORT_THRESHOLD` |
| 10 | `support` not a real number (bool excluded, `:181-182`) | :244 | `REJECT` / `SCHEMA_INVALID` |
| 11 | `support < support_threshold` | :246 | `WEAK` / `BELOW_SUPPORT_THRESHOLD` |
| 12 | `"next_support"` absent | :248 | `WEAK` / `INSUFFICIENT_MARGIN` |
| 13 | `next_support` not a real number | :251 | `REJECT` / `SCHEMA_INVALID` |
| 14 | `not margin_predicate(support, next_support)` | :253 | `WEAK` / `INSUFFICIENT_MARGIN` |
| 15 | `payload["weak_retrieval"] is True` | :255 | `WEAK`, no reason code |

Plus, universally, `validate_response` runs citation checks before the site validator (schema,
uncited claim, citation not in dossier / not found / span mismatch, contradicted-by-stronger —
`llm_harness/vocabulary.py:155-177`), and `_placement_disposition` (`:267-280`) then stamps the
disposition: `accept_direct → move_plan_eligible`, `accept_context_supported → valid_review_required`,
`weak → unresolved`, `reject → no_destination`, `abstain → no_supported_destination`.

Two invariants P8 enforces in `_rewrite` (`:117-121`): `accept_context_supported` always sets
`requires_review=True`; `weak` always sets `may_propose=False`. `P8Verdict.__post_init__`
(`records.py:418-423`) raises `MalformedVerdict` if either is violated.

**Checks 9-15 are §6.10's two-condition rule, already implemented.** P11's `two_condition` block
(SPEC:353-363) is therefore a *transcription* of P8's verdict, not a second evaluator — which is
exactly what SPEC:831-835 (resolution O7) says. The PLAN's Task 4 (PLAN:72-78) reads as if P11
computes the gate itself; it must instead compute `support` / `next_support` (as "deterministic
scores", SPEC:224) for the dossier, supply the threshold and predicate as authorities, and read the
verdict back.

### B.3 — Every validation P8 already performs at Site D

From `_residual_site` (`:302-348`):

| # | Check | Line | Result |
|---|---|---|---|
| 1 | payload carries **both** `"support"` and `"next_support"` | :309 | `ValidationUnavailable(missing=("site_d_support_rule",))` — Q3's rule is Site C only (`:4-5`, and `planning/30-p8-p9-connection-contract.md:114-115`) |
| 2 | `action not in RESIDUAL_ACTIONS` | :312 | `REJECT` / `ACTION_NOT_IN_CONTROLLED_SET` |
| 3 | `"/" in target` | :315 | `REJECT` / `INVENTED_FOLDER` — this is §7.8's `Travel/Flight Gate B12` guard, already built |
| 4 | target-bearing action with empty/non-str target | :318-320 | `REJECT` / `DESTINATION_NOT_IN_FROZEN_TREE` |
| 5 | `not node_exists(target, plan_version)` | :322 | `REJECT` / `DESTINATION_NOT_IN_FROZEN_TREE` |
| 6 | target in neither `approved_target_ids` nor `dossier.allowed_vocabulary` | :324 | `REJECT` / `DESTINATION_NOT_IN_FROZEN_TREE` |
| 7 | a citation resolves to an evidence item whose `location != dossier.subject_ref` | :283-299, :326 | `REJECT` / `EVIDENCE_NOT_IN_FILE_RECORD` |
| 8 | `sensitivity_policy(...)` false | :328 | `REJECT` / `SENSITIVITY_RESTRICTION_IGNORED` |
| 9 | a `dossier.conflicts` item with `kind == "stronger_relationship"` absent from `payload["relationships_considered"]` | :330-338 | `REJECT` / `STRONGER_RELATIONSHIP_OVERLOOKED`, **disposition `return_to_placement`** |
| 10 | `action == mark_review_later` | :339 | `WEAK` / `review_later` |

`_TARGET_ACTIONS` (`:64-69`) is `{return_to_confirmed_domain_group,
return_to_accepted_graph_or_purpose_packet, choose_approved_residual_destination,
choose_approved_broad_parent_branch}` — the four of the eight that carry a target.

`_residual_disposition` (`:351-371`) then stamps: `accept_direct` + a return action →
`return_to_placement`, otherwise `residual_destination`; `accept_context_supported` →
`residual_destination_review`; `weak` → `review_later` or `leave_in_place`; `reject` → `rejected`;
`abstain` → `leave_in_place`.

**Check 9 is §7.9's loop, already implemented in P8.** P11 does not decide that a stronger
relationship exists; it supplies the `Conflict` and reads `disposition == return_to_placement`.

### B.4 — `record_cd_verdict`'s requirements

```python
# src/llm_harness/placement_validation.py:465-478
def record_cd_verdict(conn, verdict, *, evidence_snapshot_id, model_id,
                      prompt_fingerprint, release_audit_id, observed_at) -> str:
    if not evidence_snapshot_id:
        raise ValueError("evidence_snapshot_id is required for C/D verdicts")
    if not verdict.plan_version:
        raise ValueError("C/D verdicts require plan_version")
```

(`grep -n "evidence_snapshot_id is required for C/D verdicts" src/llm_harness/placement_validation.py`
→ line 476.)

Requirements P11 must satisfy:

1. **A non-empty `evidence_snapshot_id`.** P11's SPEC never mentions one. `DossierRequest` carries
   `evidence_snapshot_id: str | None` (`records.py:185`); the fixtures carry a per-pair value
   (`tests/p8/test_p8_placement_validation.py:427` asserts `pair.evidence_snapshot_id`). **Who mints
   it for a real placement call is unstated anywhere I could find.** See B.5.
2. **A non-empty `verdict.plan_version`.** Enforced twice more: `SITES_REQUIRING_PLAN_VERSION`
   (`vocabulary.py:147-149`) is `{C_placement, D_residual, E_template}`, and
   `DossierRequest.__post_init__` calls `_require_plan_version` (`records.py:195`).
3. **All three provenance keywords with no defaults.** `model_id`, `prompt_fingerprint`,
   `release_audit_id` are keyword-only with no default, and
   `test_record_cd_verdict_requires_provenance_with_no_defaults`
   (`tests/p8/test_p8_placement_validation.py:452-456`) asserts it by `inspect.signature`.
   `release_audit_id: int` — not optional here, unlike `validate_placement_response`'s
   `release_audit_id: int | None` (`:391`).
4. **Both writes are one transaction** (`:485-498`), so a P11 caller cannot observe a verdict row
   without its plan/snapshot identity; the rollback is tested at `:459-485`.
5. **Plan-version change → new verdict + supersession, never migration.** `revalidate_for_plan`
   (`:528-630`) returns the stored verdict unchanged when plan and snapshot both match (`:561-565`),
   otherwise re-validates, mints
   `f"{previous_verdict_id}::{current_plan_version}::{current_evidence_snapshot_id}"` (`:608-611`),
   records it, and supersedes with `reason="plan_or_snapshot_changed"` (`:622-628`). This is the
   machinery behind P11 SPEC Done-means 16 (SPEC:670-671) and SPEC:782-787 — **P11 must call it, not
   re-implement it.** The PLAN's Task 10 (PLAN:115-120) implements plan-version re-projection with no
   reference to it (`revalidate_for_plan` grep count 0).

### B.5 — What P8 expects from P11 with no obvious producer

1. **`evidence_snapshot_id`.** Required by `record_cd_verdict` (`:475-476`) and carried on
   `DossierRequest` (`records.py:185`). It appears nowhere in P11's SPEC, P10's SPEC, or the P8/P9
   connection contract as something a part *mints*. Consumer with no producer.
2. **`prompt: PromptDefinition`.** `run_call` requires it (`harness.py:330`) and
   `PromptDefinition.__post_init__` (`records.py:85-98`) rejects empty `template_bytes`,
   `response_schema_bytes` and `shaping_policy_bytes` with *"there is no default prompt"*. P11's PLAN
   defers prompts (PLAN:145) and Task 12 guards **against** them (PLAN:133). So the Site C/D model
   path is unbuildable and nothing in the plan says who authors the two prompt definitions.
3. **`gate: Gate` and `model_client: ModelClient`.** Both required by `run_call`
   (`harness.py:328-329`). PLAN:82 says P11 "must not … call `Gate.release`, or import a model
   client" — correct about `release`, but P11 must still hold and pass both objects, and no task
   names their source. This is a genuine internal contradiction in the plan.
4. **The five reduction predicates.** `CallDependencies.unreduced_fits`, `summarized_fits`,
   `anchors_fit`, `split_shard_fits`, `split_shards` (`harness.py:95-99`). `_BOOL_FLAGS`
   (`harness.py:78`) means the first three must be literal `True`/`False`, not truthy. These are
   SPEC:724-727's "summarizes deterministic facts, preserves anchor excerpts, splits the task, or
   defers", and no task authors them.
5. **`allowed_vocabulary`.** `CallDependencies.allowed_vocabulary` (`harness.py:103`) becomes
   `Dossier.allowed_vocabulary` (`records.py:335`), and Site C check 2 (`:220`) rejects any
   destination outside it as `INVENTED_NODE`. This is P11's candidate node-id set — the single most
   load-bearing thing P11 hands P8 — and it appears **zero times** in the PLAN.
6. **`Conflict` shape collision.** P8's `Conflict` is `(conflict_id: str, kind: str)`
   (`records.py:269-276`). P11's `conflicts_considered[]` is
   `{kind, conflicting_value, suppressed_node_ids[], evidence_ref}` (SPEC:349-350). Two shapes, one
   word, and P11 must build both — P8's to be checked against, its own to publish. The PLAN
   reconciles nothing.
7. **Two unnamed string vocabularies P11 must spell by hand.**
   `"stronger_relationship"` is a bare literal at `placement_validation.py:335` and appears in
   `fixtures.py:534`; it is **not** in `llm_harness/vocabulary.py`. Likewise `EvidenceItem.kind`
   values (`"excerpt"`, `"member"` — `fixtures.py:102,113`, `group_validation.py:86`) are not
   validated against any closed set in `EvidenceItem.__post_init__` (`records.py:228-239` checks only
   `reliability_state` and `basis`).
8. **A live P8 defect that constrains P11's node ids.** `placement_validation.py:239` reads
   `if payload.get("generic_hub") is True or destination == "node-hub":`. `"node-hub"` is a **fixture
   id** (`fixtures.py:346`, `_C_VOCAB`) hardcoded into production Site C logic. Any real frozen node
   whose `node_id` is `node-hub` can never be accepted. Worth reporting to P8's owner; for P11 it is
   a naming constraint nobody has written down.
9. **`P8Verdict.scope` is fixed per site, not chosen.** `_SCOPE_BY_SITE` (`harness.py:70-76`) maps
   `C_placement → "node"` and `D_residual → "file"`. P11's `correction_scope` on learning records
   (SPEC:745) must agree with that or the two stores disagree about what a placement decision is
   *about*. Neither SPEC nor PLAN mentions it.

---

## C. Upstream seams

### C.1 — From P9

**What the SPEC asks for** (SPEC:165-166): *"Group id, label, category, member files each with P9's
`Membership.basis` — **all three** kinds, `direct-anchor`, `context-supported` and `user-attached`
(§4.3, §4.8, §4.9) — identified outliers, and recorded conflicts."*

**What P9 actually publishes.** `src/grouping/records.py`:

- `Group` (`:149-173`) — 24 fields including `group_id`, `seed_ref`, `seed_kind`, `proposed_basis`,
  `anchor_facts: tuple[AnchorFact, ...]`, `group_category: str | None`, `display_label: str | None`,
  `label_source`, `conflicts: tuple[Conflict, ...]`, `stop_rule_hits`, `state`, `sensitivity_state`,
  `supersedes` / `superseded_by` / `supersede_reason`.
- `Membership` (`:218-235`) — `membership_id`, `group_id`, `file_id`, `content_hash`, `basis`,
  `decision`, `decision_source`, `support: tuple[Support, ...]`, `insufficient_evidence`,
  `insufficiency_statement`, `conflicts`, **`outlier_flag`**, `validation_verdict_ref`.
- `Conflict` (`:128-133`) — `(kind, competing_values: tuple[str, ...], file_ids: tuple[str, ...])`.
  **A third `Conflict` shape**, different again from P8's `(conflict_id, kind)` and from P11's
  `conflicts_considered[]`.
- `AnchorFact` (`:79-90`) — `(field, value, file_ids, reliability_state, observation_key)`. This is
  what SPEC:348's `graph_anchors[]` should be built from.
- `GroupAcceptance` (`:346-362`) — `(acceptance_id, plan_version_id, group_id, membership_id,
  acceptance, review_state, user_edited_label, aliases, review_decision_ref, decided_by, …)`.

**Three concrete findings the PLAN misses:**

1. **"Accepted group" is not a field on `Group`.** `src/grouping/vocabulary.py:31-35` is explicit:
   *"The two values `group_state_as_of` adds at read time. Never stored."* — `PLAN_VERSIONED_STATES =
   ("accepted", "rejected")`. Acceptance is resolved from the `group_acceptance` table
   (`src/grouping/schema.py:140`) **as of a plan version**. P11 must therefore join on
   `plan_version_id`, and the plan version it joins on must be P10's frozen version. PLAN:89's
   "Confirm a shared parent before member placement" says nothing about how a group becomes accepted.
2. **Outliers are a field, not a list.** SPEC:166 says "identified outliers"; P9 publishes
   `Membership.outlier_flag ∈ {engine-flagged, model-flagged, both, none}`
   (`vocabulary.py:70-77`). P11's `excluded_outliers[]` (SPEC:516-518) must be derived from it. The
   PLAN names neither.
3. **P9 is only half-built, and the half P11 needs is the missing half.** `src/grouping/` contains
   `config.py`, `embeddings.py`, `fixtures.py`, `records.py`, `retrieval.py`, `schema.py`,
   `seeds.py`, `vocabulary.py`. There is **no `store.py`, no `acceptance.py`, no `groups.py`, no
   `p8_seam.py`** — i.e. P9's PLAN Tasks 9-15 are unbuilt, so there is no published read surface that
   returns an accepted group at a plan version. P11's PLAN declares no P9 gate at all: PLAN:24 lists
   **G-P10, G-P8, G-P13, G-KNOWLEDGE, G-P12** and no G-P9, and PLAN:20 says only *"P9 owns accepted
   groups and memberships; P11 never re-groups."*

**Verdict on C for P9: prose only.** No record shape, no symbol, no table, no plan-version join.

### C.2 — From P10

**What P10 publishes** (`P10 SPEC` Contract out §1, the node record table): 21 fields.
**What P11's SPEC Contract-in table lists** (SPEC:117-128): 15.

Five P10 node fields P11's own SPEC never receives, and one that matters:

| P10 field | P11 SPEC | Why it matters |
|---|---|---|
| `plan_version_id` | absent from SPEC:117-128 (though `plan_version` is on the decision record, SPEC:300) | the legality set is keyed on it (SPEC:135-136) |
| `dimension_role` | absent | §5.4/§5.5's semantic role of the level |
| `existing_path` | absent | the one legal path string (SPEC:155-156 mentions it in prose only) |
| **`refinement_disposition ∈ refined \| shallow-by-choice \| refine-later`** | absent | **this is the field that distinguishes an intentionally shallow branch from an unfinished one.** §6.7's "prefer an approved shallower path … never fill a missing slot" (SPEC:45) and `decision_depth.unsupported_levels[]` (SPEC:334) are decisions about exactly that, and P10 already publishes the user's answer. P11 plans to re-derive it |
| `refinement_reason` | absent | the user/evidence explanation behind the above |

**What P11's PLAN says about the seam:** Task 2, PLAN:60-62. PLAN:61 lists eleven items in prose and,
as noted in A.3, mixes node fields with profile fields. `root_anchor`, `expected_values`,
`existing_path`, `refinement_disposition` all have grep count 0.

**Verdict on C for P10: prose only.** PLAN:61's `build_destination_index(frozen_plan)` is the single
signature in the whole document, and `frozen_plan` is an untyped word — there is no record shape for
what a frozen plan *is*, no freeze-record fields (P10 SPEC §4), and no statement of which of P10's
21 node fields P11 reads.

### C.3 — For contrast, how P9's plan did it

P9's PLAN:34-47 is a **Prerequisite / Current evidence / Plan treatment** table with one row per
upstream part, naming live symbols (`vector_arrays(subject_key PRIMARY KEY, array_bytes,
producer_version)`, `proposal_eligible`, `event_facts`, `session_facts`, `family_facts`,
`active_allowlist_for`, `evidence_chain`), and PLAN:48-55 defines five named dependency gates with
the exact exception each raises. P11's PLAN:24 declares five gate names in one sentence and defines
none of them.

---

## D. Ordering

**The PLAN states no ordering.** There is no "Required execution order" section — compare P9's
PLAN:56-58, which reads *"Execute Tasks 1–8, then **Task 9 before Task 10**. Task 10 is a hard
dependency gate: it must not begin until Task 9's `record_context_review_pending` is green and P8's
frozen public surface exists."* P11's PLAN:24 names five gates and then never says which task each
gate blocks.

Worse, the plan's numeric order contains **three inversions** against data dependencies stated in the
SPEC:

1. **Task 7 (privacy) must precede Task 5 (P8 seam).** SPEC:210-212: *"**The gate is passed before
   any dossier is assembled for a model**, not after (§8.4)."* Task 5 (PLAN:80-85) builds the
   `DossierRequest`; Task 7 (PLAN:94-99) establishes the handling class, operation mode and consent
   state that decide whether a dossier may be built at all. As numbered, the seam is built before the
   gate that governs it.
2. **Task 10's first bullet must precede Task 4's first `place`.** SPEC:753-755: *"**Before emitting
   `outcome = place` (or a residual equivalent), P11 queries P1 `learning_records`** … A matching
   unresected reject skips that node — never auto-place."* Task 4 (PLAN:72-78) is the first task that
   emits `place`; the learning query is PLAN:117, six tasks later. Every fixture written for Tasks
   4-9 will therefore be written against a code path that skips a required step.
3. **P1 event-type registration must precede Task 1.** `src/database_agent/events.py:42-66` has no
   runtime registration and rejects unknown types at the writer. Nothing in P11 may append an event
   until the eight names are added there. No task does this at all (A.8).

### Proposed ordering, derived from the SPEC's own dependencies

The design's §6.12 pipeline (`planning/01-product-design-structured.md:1295-1306`) is the spine, and
the SPEC never reproduces it despite SPEC:50 claiming it does:

> 1. The user freezes an approved destination tree.
> 2. The system turns each node into an evidence-backed destination profile.
> 3. Each unplaced file or accepted file packet retrieves a small set of legal candidate nodes.
> 4. The engine builds a local graph around those nodes using facts, accepted groups, structural
>    relationships, representative files, and semantic retrieval.
> 5. Deterministic rules remove impossible or conflicting nodes.
> 6. Local clustering and group context identify whether the target joins a child node, parent node,
>    fallback node, or no node.
> 7. The LLM judges ambiguous candidates hierarchically from a bounded placement dossier.
> 8. The validator checks all evidence and destination constraints.
> 9. The product produces a reviewable plan of exact placements, shallow placements, scoped
>    fallbacks, and abstentions.

Steps 1-2 are P10's; step 8 is P8's. Steps 3-7 and 9 are P11's, and **step 4 is the node-local
evidence graph the PLAN has no task for** (A.1, §6.4).

Recommended order with explicit gates:

| Order | Task | Gate — X before Y, and why |
|---|---|---|
| 0 | **NEW: register P11's eight §8.2 event types** in `src/database_agent/events.py` | before every task, because `append_event` raises `UnregisteredEventType` and registration is import-time (`events.py:39-41`) |
| 1 | Task 1 vocabulary + records + schema | before all; every later task writes one of these rows. Split it: a `vocabulary.py` publishing every closed set as **named constants** (see E) must land before any module spells a value |
| 2 | Task 2 P10 adapter + index | before Task 3, because retrieval reads the index; and Done-means 3 (SPEC:620-622) requires the index to exist **before the first file is placed**, which is an ordering assertion the plan must test |
| 3 | Task 7 privacy | **moved up**, before Task 5 — SPEC:210-212, the gate precedes dossier assembly |
| 4 | Task 10a: `learning_records` negative-example query only | **moved up**, before Task 4 — SPEC:753-755, queried before any `place` |
| 5 | Task 3 bounded retrieval + conflict suppression | after 2; produces the candidate set and the suppressed set that become `allowed_vocabulary` and `conflicts_considered` |
| 5b | **NEW: node-local evidence graph (§6.4/§6.5, pipeline step 4)** | after 5, before 6 — `graph_anchors[]` (SPEC:348) and Done-means 5 (SPEC:627-630) have no other home |
| 6 | Task 4 deterministic match + two-condition record | after 5b; §6.6 requires the deterministic path to decide first so that "zero model calls" is provable (Done-means 6) |
| 7 | Task 5 P8 seam | after 3, 4, 5b: the dossier carries the candidate profiles (5), the deterministic scores (6), the conflicts (5) and the anchors (5b), and cannot be assembled before any of them |
| 8 | Task 6 group placement | after 7, because a member placement may need a model call, and §6.8 requires the shared parent confirmed first |
| 9 | Task 8 residual sets + set gating | after 6 — §7.1 (SPEC:56) requires the whole §6 pass attempted first; Done-means 12 (SPEC:658-660) tests it |
| 10 | Task 9 eight actions + return loop | after 8 (§7.6's set decision gates the call) and after 3+4 (the returned file re-enters retrieval and scoring) |
| 11 | Task 10b store user actions + plan-version re-projection | after 1 (supersession), 2 (index), 9 (the actions to store); and it must call `revalidate_for_plan` (B.4) rather than re-implement it |
| 12 | Task 11 P2 stage output | after 4 and 8, because it maps decision outcomes into envelope outcomes |
| 13 | Task 12 fixtures + guards, Task 13 final verification | last |

---

## E. Vocabulary

Every closed vocabulary the SPEC defines for P11, with exact values, the SPEC line, and whether P8
already names the value. Where P8 names it, **P11 must import the constant, not re-spell the string** —
`_PLAN-AUTHORING-BRIEF.md:232-235` states this as the ruling that follows from the project's
most expensive defect class:

> **Task 1 publishes the six states BOTH ways: `STATES: tuple[str, ...]` for iteration and
> membership, AND one named constant per state … Every other module imports the NAMED CONSTANT.**
> Never a bare string, never an index.

and `_PLAN-AUTHORING-BRIEF.md:242-243`: *"The same rule applies to every closed vocabulary either
part publishes."*

| # | Vocabulary | Values | SPEC | Already named in P8 / elsewhere |
|---|---|---|---|---|
| 1 | `origin_stage` | `placement`, `residual` | SPEC:306 | No. Nearest is `C_PLACEMENT = "C_placement"` / `D_RESIDUAL = "D_residual"` (`llm_harness/vocabulary.py:22-23`) — different strings, different concept (call site) |
| 2 | `subject.kind` | `file`, `group` | SPEC:311 | **Yes.** `SCOPE_FILE = "file"` (`llm_harness/vocabulary.py:285`), `SCOPE_GROUP = "group"` (`:286`). Also P1's `CORRECTION_SCOPES` (`database_agent/events.py:99-101`) |
| 3 | `outcome` | `place`, `return_to_placement`, `mark_review_later`, `leave_in_place`, `mark_state`, `ask_user`, `abstain` | SPEC:316-318 | **Four of seven collide with P8 strings, in a different vocabulary.** `RETURN_TO_PLACEMENT = "return_to_placement"` (`:313`) and `LEAVE_IN_PLACE = "leave_in_place"` (`:317`) are P8 **dispositions**; `MARK_REVIEW_LATER = "mark_review_later"` (`:48`) is a P8 residual **action**; `ABSTAIN = "abstain"` (`:38`) is a P8 **outcome**. Same spellings, four different axes. This needs a written ruling before anyone types a string |
| 4 | `destination.node_role` | `ordinary`, `scoped-general`, `residual`, `shared-material` | SPEC:321-323 | No — P10's, carried verbatim (SPEC:322-323, P10 SPEC node table). Not in P8 |
| 5 | `return_target.kind` | `confirmed_domain_group`, `accepted_graph_or_purpose_packet` | SPEC:325-326 | **Near-collision.** P8's action names are `RETURN_CONFIRMED_GROUP = "return_to_confirmed_domain_group"` (`:44`) and `RETURN_ACCEPTED_PACKET = "return_to_accepted_graph_or_purpose_packet"` (`:45`) — the same concept with a `return_to_` prefix. Two spellings of one thing |
| 6 | `marked_state` | `protected`, `unsupported`, `null` | SPEC:328 | Partly: P8's single action `MARK_PROTECTED_OR_UNSUPPORTED = "mark_protected_or_unsupported"` (`:50`) covers both without distinguishing them, so P11 must split it and record which |
| 7 | `evidence_type` | `user-confirmed`, `direct`, `validated`, `llm-supported`, `context-supported`, `possible` | SPEC:335-336 | **Spelling conflict.** The live reliability states are **snake_case**: `RELIABILITY_STATES = ("user_confirmed", "direct", "validated", "llm_supported", "possible", "rejected")` (`evidence_shape/vocabulary.py:53-55`), with named constants at `facts/states.py:43-48`. P11's SPEC hyphenates two of them. `context-supported` **is** already named twice, hyphenated: `grouping/vocabulary.py:52` and `llm_harness/vocabulary.py:282`. So P11's list mixes two conventions |
| 8 | `confidence_class` | `exact fact match`, `context-supported group match`, `shared-material decision`, `abstain: no supported destination` | SPEC:337-340 | No. Note SPEC Open question 3 (SPEC:809-811) asks whether the list is closed at all — *"§6.11 gives four labels by example ("might be labeled"), not as an enumeration"* |
| 9 | `group_support.membership` | `direct-anchor`, `context-supported`, `user-attached` | SPEC:345-347 | **Yes, and there is a live 2-vs-3 mismatch.** P9 publishes all three: `MEMBERSHIP_BASES` (`grouping/vocabulary.py:51-55`). P8 publishes only two: `EVIDENCE_BASES = (DIRECT_ANCHOR, CONTEXT_SUPPORTED)` (`llm_harness/vocabulary.py:281-283`), and `EvidenceItem.__post_init__` **rejects** `user-attached` (`records.py:239`). P11's SPEC:176-178 makes `user-attached` a first-class input, so a `user-attached` member can never be an `EvidenceItem` in a dossier. Nobody has written that down |
| 10 | `conflicts_considered[].kind` | not enumerated | SPEC:349-350 | P8 requires `"stronger_relationship"` at Site D (`placement_validation.py:335`) and `"target_institution"` at Site B (`group_validation.py:113`), **neither of which is in `llm_harness/vocabulary.py`** |
| 11 | `two_condition.meets_margin` | `true`, `true_vacuous`, `false` | SPEC:357-359 | No — P11's own, and correctly so (B8(b), SPEC:447-460) |
| 12 | `two_condition.verdict` | `accept_direct`, `accept_context_supported`, `weak`, `reject`, `abstain` | SPEC:360-362 | **Yes, exactly.** `OUTCOMES = (ACCEPT_DIRECT, ACCEPT_CONTEXT_SUPPORTED, WEAK, REJECT, ABSTAIN)` (`llm_harness/vocabulary.py:34-42`). SPEC:462 says so: *"The verdict vocabulary is P8's (MINOR 7)"* |
| 13 | `abstention_reason` | `no_supported_destination`, `low_margin`, `semantic_only`, `generic_hub_only`, `conflicting_facts`, `no_shared_branch`, `budget_deferred`, `privacy_blocked`, `null` | SPEC:364-367 | **One exact match:** `NO_SUPPORTED_DESTINATION = "no_supported_destination"` (`llm_harness/vocabulary.py:312`). Three near-collisions with P8 **reason codes** (uppercase, different axis): `INSUFFICIENT_MARGIN` (`:220`) vs `low_margin`; `GENERIC_HUB_ONLY = "GENERIC_HUB_ONLY"` (`:221`) vs `generic_hub_only`; `GENERIC_SIMILARITY_ONLY` (`:198`) vs `semantic_only`. SPEC Open question 4 (SPEC:812-813) asks whether the set is closed |
| 14 | `privacy.model_eligibility` | `local_only`, `dossier_permitted`, `redacted` | SPEC:374 | **No producer.** `grep -rn "local_only\|dossier_permitted" src/privacy/` finds nothing; P7 publishes `OPERATION_MODES = ("offline", "local_model", "hybrid", "cloud_assisted")` (`privacy/vocabulary.py:112-114`) and `CONSENT_OPTIONS = ("local_model", "cloud_model", "redacted_prompt", "no_model_use")` (`:195-197`). `redacted` collides with `REDACTED = "redacted"` (`privacy/vocabulary.py:217`), a **display-facet** value. Consumer with no producer, plus a collision |
| 15 | `review_policy` | `auto_eligible`, `review_required`, `blocked_pending_user` | SPEC:376-377 | No. Related but distinct: P8's `VALID_REVIEW_REQUIRED = "valid_review_required"` (`:310`) and `P8Verdict.requires_review` (`records.py:396`) |
| 16 | `privacy.handling_class` | five values | SPEC:373 | **Yes.** `HANDLING_CLASSES` (`privacy/vocabulary.py:86-92`) |
| 17 | The §7.7 eight actions | `return to a confirmed domain group`, `return it to an accepted graph or purpose packet`, `choose one approved residual destination`, `choose an approved broad parent branch`, `mark it for Review Later`, `leave it in its current location`, `mark it as protected or unsupported`, `abstain` | SPEC:86-93 | **Yes — P8 owns the machine spelling.** `RESIDUAL_ACTIONS` (`llm_harness/vocabulary.py:52-61`) is the eight: `return_to_confirmed_domain_group`, `return_to_accepted_graph_or_purpose_packet`, `choose_approved_residual_destination`, `choose_approved_broad_parent_branch`, `mark_review_later`, `leave_in_current_location`, `mark_protected_or_unsupported`, `abstain`. **Note action 6 is `leave_in_current_location`, while P11's outcome is `leave_in_place` and P8's disposition is also `leave_in_place`** — three spellings across two axes |
| 18 | `residual_set_decision.choice` | `leave_in_place`, `review_with_model_against_approved_residual_folders`, `send_to_approved_node(node_id)`, `create_custom_branch` | SPEC:538-542 | No |
| 19 | `excluded_outliers[].routed_to` | `node_id`, `review_queue` | SPEC:517-518 | No |
| 20 | P2 envelope `outcome` / `budget_state` | `produced\|abstained\|deferred\|not_implemented\|error`; `within_ceiling\|ceiling_reached` | SPEC:266-267 | **Yes, live.** `eval_harness/vocabulary.py:52-53` |
| 21 | `stage_id` | `candidate_node_retrieval`, `placement_scoring` | SPEC:255-256 | **Yes, live.** `eval_harness/vocabulary.py:27-28` |
| 22 | P2 dimensions P11 feeds | `placement`, `residual` | SPEC:583-585 | **Yes, live.** `eval_harness/vocabulary.py:41-42` |
| 23 | `correction_scope` | `file`, `group`, `node`, `template`, `domain`, `corpus` | SPEC:745 | **Yes, live.** `CORRECTION_SCOPES` (`database_agent/events.py:99-101`), re-exported as `learning.SCOPES` (`database_agent/learning.py:23`). Also P8's `VERDICT_SCOPES` (`llm_harness/vocabulary.py:292-294`) — the same six |
| 24 | `node_type` (read, not written) | `existing`, `proposed`, `user-created`, `protected`, `ignored` | SPEC:120 | P10's |
| 25 | `disposition` on residual nodes (read) | `physical-destination`, `review-only`, `leave-in-place` | SPEC:126 | P10's. Note `leave-in-place` (hyphen) here vs `leave_in_place` (underscore) at #3/#17 — a fourth spelling of the same words |

**The vocabulary finding in one sentence.** P11 sits at the junction of four published vocabularies
(P8's outcomes/actions/dispositions/reason codes, P9's membership bases, P10's node roles and
dispositions, P7's handling classes) and must define ~19 of its own, and **the PLAN publishes no
vocabulary module contract at all** — PLAN:29 lists `src/placement/vocabulary.py  outcomes,
evidence/review/abstention vocabularies` and no task enumerates a single value of any of them. Given
that `leave_in_place` / `leave_in_current_location` / `leave-in-place` already exist as three
spellings across P8 and P10, that is the highest-probability defect in the whole part.

---

## Summary of the three most serious gaps

1. **The record the part exists to publish is never specified.** SPEC:19 — *"Publishing that single
   shape is this part's primary obligation."* Of the ~45 fields in SPEC:298-384, thirteen are
   entirely absent from the PLAN (`origin_stage`, `subject{}`, `return_target`, `marked_state`,
   `ask`, `decision_depth`, `evidence_type`, `graph_anchors[]`, `abstention_reason`, `residual{}`,
   and three mapping rules), and no field anywhere has a declared type. `decision_depth` is the worst
   loss: SPEC:414-417 says it is what replaced the deleted `destination.kind`, so without it the
   record cannot distinguish a fully-supported child from a deliberately shallow parent — which is
   §6.7's whole subject and Done-means 7.

2. **P8 already implements ~25 of the validations Tasks 4, 5 and 9 propose to build, and the PLAN
   does not know it.** `PlacementDependencies`, `ResidualDependencies`, `SiteDependencies`,
   `CallDependencies`, `record_cd_verdict`, `revalidate_for_plan`, `allowed_vocabulary` and
   `evidence_snapshot_id` each appear **zero times** in the PLAN. The two-condition gate, the
   frozen-tree membership test, the `Travel/Flight Gate B12` guard, the §7.9 return-to-placement
   trigger, and plan-version re-validation with supersession are all shipped and tested in
   `src/llm_harness/placement_validation.py`. P11's job at those points is to supply four/three
   authorities and transcribe the verdict; the PLAN describes building a second implementation.

3. **Three hard blockers with no task at all.** (a) P11's eight §8.2 event types are not registered
   in `src/database_agent/events.py`, whose comment at `:62-65` says they are *"ABSENT ON PURPOSE …
   When P11 prints the eight, add them here"* — and `append_event` rejects unregistered types, so
   nothing in SPEC:683-693 can be logged. (b) The §6.4 node-local evidence graph — pipeline step 4,
   Done-means 5, the source of `graph_anchors[]` — has no task and no module. (c) The P13
   `review_action` receiver has no task, no module and no fixture, even though PLAN:24 declares gate
   **G-P13** and SPEC:241-243 says *"**All eight §7.7 actions arrive on this record**"* and
   *"**P11 authors the placement or residual decision each action produces** (M8)"*. Without it
   Task 9's eight actions have no input.

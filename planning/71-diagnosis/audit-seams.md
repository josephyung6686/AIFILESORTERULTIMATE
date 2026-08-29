# Audit — the seam between the built engine and the unbuilt product

Read-only diagnostic. No repo file under `src/` or `tests/` was changed. Every function
signature below was confirmed by live introspection
(`PYTHONPATH=src python3 -c "import inspect; ..."`), not read off a SPEC. Every schema
claim was confirmed against the DDL string in the module that owns the table.

The question this audit answers: **`66` designs Find, File, and the onboarding question
registry with no part number and no code. What does the built engine (P1–P11) already
publish that those three would consume, and what would they each have to invent?**

---

## 1. The six states of `66` §3 — the lead finding

`66`:126-133 defines six distinct states one search result must be able to show. Four are
answerable today from published readers. Two are not, and one of those two is answerable
for a *destination* but not for a *file*, which is the more dangerous kind of gap because
a builder will find a function with almost the right name.

| # | `66` §3 state | Answerable today? | The exact read, or what is missing |
|---|---|---|---|
| 1 | **Current location** — "The actual path where the file exists now" | **Yes** | `database_agent.files_table.get_file(conn, file_id) -> sqlite3.Row` (`files_table.py:286`); the column is `files.current_path`, `db.py:175`. Indexed: `files_current_path`, `db.py:208`. |
| 2 | **Filed home** — "A user-approved physical destination in the active organization plan" | **Partly — no path exists** | `placement.store.current_decision(conn, *, plan_version, subject_ref) -> PlacementDecision \| None` (`store.py:152`); `subject_ref` from `placement.store.subject_ref_of(subject)` (`store.py:35`). The decision's `destination` is `Destination(node_id, node_role)` (`records.py:92`) — **"A node in the frozen tree. Never a path string (§5.12, B3)"**. The human-readable chain comes from `placement.index.entry_for(conn, *, plan_version, node_id) -> IndexEntry \| None` (`index.py:620`), whose `ancestor_labels` field (`index.py:47`) is the label chain. **A filesystem path for a node does not exist anywhere in `src/`** — path resolution is P12 Contract out §3 (`P12-apply-undo/SPEC.md:315`), unbuilt. So "filed home" renders today only as `Career › Stripe`, never as a path. That is exactly what `66`:143 asks for, so this is adequate — but a builder who expects a path will not find one. |
| 3 | **Also related to** — "An accepted group, project, course, packet, event…" | **No — the read does not exist** | This is the file→group direction. P9 publishes only the group→file direction: `grouping.store.memberships_for_group(conn, group_id) -> tuple[Membership, ...]` (`store.py:309`). Every `SELECT` against `memberships` in `src/` is by `membership_id` or `group_id` (`store.py:248`, `:302`, `:314`) — verified exhaustively by `grep -rn "FROM memberships" src`. **The index for the missing read already exists**: `CREATE INDEX memberships_file ON memberships (file_id, content_hash)` (`grouping/schema.py:84`), and no code in `src/` uses it. The acceptance filter is published — `grouping.acceptance.group_state_as_of(conn, *, group_id, plan_version_id) -> str` (`acceptance.py:290`) — but it too takes a `group_id` you must already have. **Find cannot ask "which accepted groups is this file in?" today.** |
| 4 | **Shared-material relationship** — "used by several packets or branches under an approved shared-material policy" | **Policy yes, membership no** | The policy is published on the frozen bundle: `FrozenTree.shared_material_policy` / `.shared_material_policy_scope` (`tree_design/freeze.py:116`), reachable via `tree_design.freeze.frozen_tree(conn, *, plan_version) -> FrozenTree` (`freeze.py:503`). The *decision* that a file is shared material is `placement.groups.resolve_multi_home(...)` (`groups.py:234`), which returns `(outcome, payload)` and **is never persisted as a shared-material relationship** — its outcome lands on the single `PlacementDecision`. There is no record saying "this file serves packets A and B." Rendering state 4 requires state 3 first, and state 3 does not exist. |
| 5 | **Historical location** — "A prior path recorded in provenance" | **Yes** | `database_agent.files_table.file_path_history(conn, file_id) -> list[sqlite3.Row]` (`files_table.py:486`), a projection over `events` returning `(path, volume_id, observed_at, event_id)`. Note the docstring's own caveat: `volume_id` is published as literal `NULL` — "unknown, never a value a consumer could mistake for the volume this path was observed on" (`files_table.py:491`). A Find UI showing "was on an external drive" would be inventing that. |
| 6 | **Possible placement** — "A candidate that has not been accepted or lacks sufficient evidence" | **Yes for files; no for residuals** | For a file with a decision: `PlacementDecision.alternatives: tuple[Alternative, ...]` where `Alternative(node_id, support_score, rank)` (`records.py:266`), plus `two_condition` (`records.py:280`) carrying both thresholds and `requires_review`. Cross-version history: `placement.store.decision_history(conn, *, subject_ref) -> tuple[PlacementDecision, ...]` (`store.py:161`). **For a file that reached no decision at all, nothing is readable.** `placement.residual.surface_residual_sets(...)` (`residual.py:133`) `INSERT`s into `residual_sets` (`residual.py:193`) and there is **no `SELECT` against that table anywhere in `src/`** — verified by `grep -rn "residual_sets" src`. A second process (Find, or P13) cannot read residual sets back; it can only re-run the function that produces them, which requires injected `unplaced`, `partition`, and `limits`. |

**Score: 3 of 6 are cleanly answerable (1, 5, 6-for-decided-files). 1 is answerable in the
form `66` wants but not the form a builder will expect (2). 2 are not answerable at all
(3, 4).**

The single most consequential row is **#3**. It is the row `66`:143 uses in its worked
example (`Also related to: 2026 Job Search`), the row the design says must not be
"described as a confidence failure," and the row for which P9 built the index and never
built the reader.

---

## 2. What the engine already publishes that Find would consume

Inventory of published readers, by part. All signatures live-verified.

### P1 — file record, path history, identity

- `database_agent.files_table.get_file(conn, file_id) -> sqlite3.Row` — `files_table.py:286`.
  Columns available: `current_path`, `filename`, `normalized_filename`, `extension`,
  `directory_position`, `volume_id`, `content_hash`, `observed_size`,
  `observed_timestamps`, `mime_type`, `detected_format`, `scan_state`,
  `extraction_status_by_tier`, `sensitivity_state` (`db.py:173-201`).
- `database_agent.files_table.file_path_history(conn, file_id) -> list[sqlite3.Row]` — `files_table.py:486`.
- `database_agent.identity.hash_file(path, *, materialized) -> str` — `identity.py:49`.
- `database_agent.vectors.get_embedding(conn, subject_key) -> bytes | None` — `vectors.py:33`.
  The module docstring is decisive for §4 below: **"P1 exposes no similarity function, no
  index, and no nearest-neighbour query"** (`vectors.py:1-5`).

There is **no reader that enumerates files** — no `all_files(conn)`, no
`files_in_scope(...)`. Every consumer that needs a corpus supplies its own. `privacy.display.summarize_protected`
makes this explicit by taking `files_in_scope` as a required injected callable with no
default (`display.py:141`).

### P4 — evidence and text

- `evidence_shape.store.runs_for_file(conn, file_id) -> list[ExtractionRun]` — `store.py:81`.
- `evidence_shape.store.runs_for_content(conn, content_hash) -> list[ExtractionRun]` — `store.py:87`.
- `evidence_shape.store.observations_for_file(conn, file_id) -> list[Observation]` — `store.py:201`.
- `evidence_shape.store.observations_by_key(conn, observation_key) -> list[Observation]` — `store.py:206`, M14's citation resolver.
- `evidence_shape.store.text_units_for_run(conn, run_id) -> list[TextUnit]` — `store.py:237`.
- `evidence_shape.store.authoritative_result(conn, *, file_id, content_hash, extractor_name, extractor_version, analysis_tier) -> PersistedExtractionResult | None` — `store.py:272`.
- `evidence_shape.store.supersede_chain(conn, observation_id) -> list[sqlite3.Row]` — `store.py:335`.

`TextUnit(run_id, container_path, text, truncated)` (`text_units.py:46`) is where the
document text lives. It is reachable **only by `run_id`**, never by content. See §4.

### P6 — facts, the read surface built for exactly this

`facts/read_surface.py` is the closest thing in the engine to a product-facing API, and
its own docstring names its consumers: *"the only shape P9, P10, P11, P13, P2 and the
review UI see"* (`read_surface.py:2`).

- `facts_for(conn, *, file_id, content_hash, states=None, domain=None) -> list[sqlite3.Row]` — `:108`
- `proposal_eligible(conn, *, file_id, content_hash) -> list[sqlite3.Row]` — `:150`
- `active_allowlist_for(conn, *, file_id, content_hash, activation_signals) -> tuple[str, ...]` — `:172`
- `values_with_counts(conn, *, field_key) -> list[tuple[str, int]]` — `:183`
- `evidence_chain(conn, *, fact_id) -> list[Observation]` — `:236`
- `history(conn, *, file_id, field_key) -> list[sqlite3.Row]` — `:261`
- `unresolved_for(conn, *, file_id, content_hash, field_key=None, reason=None) -> list[sqlite3.Row]` — `:272`
- `session_facts` `:291`, `event_facts` `:284`, `family_facts` `:300`, `is_destination_eligible` `:307`

`values_with_counts` is a **corpus-wide aggregate keyed by field** — the one existing read
that answers a question about the whole corpus rather than one file. It is the natural
backbone of a faceted filter ("every `course` value and how many files carry it"), and
nothing else in the engine does anything like it.

### P7 — classification and policy

- `privacy.classification_store.ClassificationStore(conn)` with `.current(file_id, content_hash) -> ClassificationRecord | None` (`classification_store.py:154`) and `.history(file_id)` (`:178`).
- `ClassificationRecord(file_id, content_hash, handling_class, protected, basis, evidence_refs, reliability_state, observed_at)` — `classification.py:106`. **`protected` is a boolean field on the record**, which is what state-4-of-`66`-§4 keys on.
- `privacy.classification.resolve_class(record | None) -> str` — `classification.py:170`. `None` resolves to `unreadable_unclassified`, never to `public_low`.
- `privacy.display.display_policy(conn, *, plan_version) -> RedactionSettings` — `display.py:88`. Five facets: `names, previews, thumbnails, ocr_text, location_data` (`display.py:44`). This is precisely the policy `66`:167 says must govern how much a protected result reveals.
- `privacy.display.summarize_protected(conn, scope, *, store, files_in_scope) -> ProtectedSummary` — `display.py:124`, returning `ProtectedSummary(count, scope_total, class_breakdown)` (`display.py:61`).
- `privacy.resolve.materialise(conn, item) -> Materialised` — `resolve.py:179`; `privacy.resolve.current_location(conn, observation_key) -> CurrentLocation` — `resolve.py:88`, "with no content".
- `privacy.items.check_item(...)` — `items.py:262`, the release-time item rules.
- `scan_agent.exclusion.is_protected_container(path, *, extra=None) -> bool` — `exclusion.py:69`, path-based only, opens nothing.

The production classifier is real: `recognition.detector.Detector.__call__` returns a
`ClassificationRecord` carrying `protected` from its handling table
(`detector.py:392-404`), and `cli.py:393` wires it as P7's producer with no fallback
(`cli.py:352-377` documents the removal of the old over-protecting stub).

### P9 — groups, memberships, acceptance

- `grouping.store.current_group(conn, group_id) -> Group` — `store.py:218`. `Group` carries `display_label`, `label_source`, `group_category`, `proposed_basis`, `anchor_facts`, `conflicts`, `state`, `sensitivity_state` (`records.py:149`).
- `grouping.store.memberships_for_group(conn, group_id) -> tuple[Membership, ...]` — `store.py:309`. `Membership` carries `support: tuple[Support, ...]` where `Support(support_kind, observation_key, quote_or_field, location, edge_ref)` (`records.py:104`) — **this is the "why did this appear?" explanation `66`:100 asks for, already structured.**
- `grouping.store.edges_for_group(conn, group_id) -> tuple[TypedEdge, ...]` — `store.py:370`.
- `grouping.acceptance.group_state_as_of(conn, *, group_id, plan_version_id) -> str` — `acceptance.py:290`.
- `grouping.acceptance.membership_review_state_as_of(conn, *, membership_id, plan_version_id) -> str` — `acceptance.py:315`.
- `grouping.store.stored_dossier(conn, dossier_id) -> CandidateGroupDossier` — `store.py:463`.
- `grouping.retrieval.retrieve_neighbors(conn, *, seed, limits, knowledge, embeddings_enabled) -> Neighborhood` — `retrieval.py:361`. **`seed` is a file, not a query.**

### P10 — the frozen tree

- `tree_design.freeze.frozen_tree(conn, *, plan_version) -> FrozenTree` — `freeze.py:503`. `FrozenTree(plan_version_id, freeze_record, nodes, profiles, shared_material_policy, shared_material_policy_scope)` (`freeze.py:116`).
- `tree_design.freeze.legal_destination_ids(record) -> frozenset[str]` — `freeze.py:145`; `is_legal_destination(record, node_id) -> bool` — `freeze.py:150`.
- `tree_design.freeze.catalogue_release(tree) -> str` — `freeze.py:133`.
- `tree_design.store.nodes_for_version(conn, plan_version_id) -> tuple[Node, ...]` — `store.py:239`. `Node` carries `display_label`, `parent_node_id`, `root_anchor`, `node_role`, `accepts_placement`, `handling_class`, `existing_path`, `disposition` (`records.py:136`).
- `tree_design.diff.diff_versions(conn, *, before, after) -> tuple[NodeDiffEntry, ...]` — `diff.py:50`. This is `66` §17's "meaningful diff", already built for nodes.
- `tree_design.user_edits.user_level_edits(conn, *, schemas=None) -> tuple[UserLevelEdit, ...]` — `user_edits.py:175`.
- `facts.plan_versions.display_label(conn, *, value_id, plan_version) -> str` — `plan_versions.py:130`.
- `tree_design.profiles.redacted_for_egress(profile, *, protected_handling_classes) -> DestinationProfile` — `profiles.py:194`.

### P11 — placement decisions and residuals

- `placement.store.current_decision(conn, *, plan_version, subject_ref)` — `store.py:152`
- `placement.store.decision_history(conn, *, subject_ref)` — `store.py:161`
- `placement.store.decisions_for_plan(conn, *, plan_version)` — `store.py:171`
- `placement.store.placed_node_ids(conn, *, plan_version) -> tuple[str, ...]` — `store.py:180`
- `placement.index.entry_for(conn, *, plan_version, node_id) -> IndexEntry | None` — `index.py:620`
- `placement.index.entries_for_plan(conn, *, plan_version) -> tuple[IndexEntry, ...]` — `index.py:629`
- `placement.index.legal_node_ids(conn, *, plan_version) -> frozenset[str]` — `index.py:585`
- `placement.index.reachable_entries(conn, *, plan_version, pairs, group_ids, labels, node_ids, name_limit) -> Reachable` — `index.py:282`
- `placement.groups.accepted_group_as_of(conn, *, group_id, plan_version) -> AcceptedGroup` — `groups.py:99`
- `placement.privacy.privacy_state_for(conn, *, file_id, content_hash, plan_version) -> PrivacyState` — `privacy.py:98`
- `placement.privacy.automatic_move_permitted_for(conn, *, file_id, plan_version) -> bool` — `privacy.py:153`

`PlacementDecision` (`records.py:365`) is the single richest product record in the engine.
It already carries `explanation`, `confidence_class`, `evidence_type`, `matching_facts[]`
each with an `evidence_ref`, `graph_anchors[]`, `conflicts_considered[]` (what was
suppressed *and* how many), `alternatives[]`, `two_condition` with both thresholds,
`abstention_reason`, `deferred_stage`, `privacy`, and `review_policy`. Find's
"explanation instead of a score" (`66`:96-101) is largely already computed; it is not
reachable by any query except by subject.

---

## 3. `66` §5's four counts

`66`:194-198 prints four numbers. Here is what answers each.

| `66` §5 line | Answerable? | Table and column, or what is missing |
|---|---|---|
| **"18,432 indexed files"** | **Per scan run only** | `scan_agent.summary.scan_run_summary(conn, scan_run_id) -> dict` (`summary.py:25`) returns `files_indexed`, computed as `count(DISTINCT file_id) FROM stat_cache_verdicts WHERE scan_run_id = ?` (`summary.py:27-30`). It is scoped to one run. A corpus-wide count is `SELECT count(*) FROM files` and **no function in `src/` performs it** — the only `COUNT(*)` over `files`-adjacent tables is `cli.py:585`, which counts `plan_versions` and `tree_nodes` to mint ids. |
| **"89 still processing"** | **No live reader** | The data is `extraction_runs.completeness` (`evidence_shape/schema.py:51`), values `deferred` and `capped` (`eval_harness/counts.py:17`). The only function that buckets them is `eval_harness.counts.bundle_counts(conn, bundle_id)` (`counts.py:31`), which reads **`bundle_extraction_run`** (`counts.py:45`) — a P2 replay-bundle table, not the live `extraction_runs`. **No production code counts over the live table.** Per file, `files.extraction_status_by_tier` (`db.py:188`) holds the map, but nothing aggregates it. |
| **"14 protected items hidden"** | **Yes, with an injected scope** | `privacy.display.summarize_protected(conn, scope, *, store, files_in_scope) -> ProtectedSummary` (`display.py:124`). `count` follows the `protected` flag, `scope_total` is the denominator, `class_breakdown` covers every file by resolved class. `files_in_scope` has no default because "Open question 3 leaves 'corpus area' unnamed" (`display.py:142`). Find must supply the enumeration the engine does not have (see §2, P1). |
| **"27 unreadable or unsupported"** | **No live reader; and the prior audit's premise needs correcting** | Same bundle-only path as "still processing": `UNREADABLE_COMPLETENESS = {"unreadable", "failed"}` (`counts.py:20`), consumed only by `bundle_counts`. |

**Correction to the prior audit's claim about `unreadable`.** The claim that
`completeness = "unreadable"` is never written by a production extractor is **not
correct**. Two production paths write it:

1. `extractors/router.py:184` — `UNROUTED_COMPLETENESS = {"design_creative": "unreadable", "opaque_binary": "metadata_only"}`, applied at `router.py:229` for any file with no handler. Any unhandled design/creative format lands at `unreadable`.
2. `extractors/archive.py:172` — an archive whose `manifest.unreadable_reason` is set (encrypted, or otherwise not openable) gets `completeness = "unreadable"` with a `failure_reason`, deliberately keeping the metadata rows: *"section 2.9 / M3: indexed-but-unreadable, never zero rows"* (`archive.py:169-176`).

The general read-failure path is **`failed`** (`extractors/failure.py:99`) and the
no-extractor path is **`unsupported`** (`failure.py:77`). So `unreadable` alone is narrow
and would under-report — which is exactly why P5's published mapping pairs it with
`failed` (`counts.py:20`) and P13's SPEC restates that reasoning verbatim:
*"Taking P5's mapping rather than `unreadable` alone is what stops a `failed` run from
appearing in no entry at all"* (`P13-review-approval-surface/SPEC.md:344-347`).

**Net for §5: one of four counts (protected) has a production reader. The other three
exist only as replay-bundle aggregates over P2's mirror tables.**

---

## 4. What Find needs that is a new capability, not a new reader

### There is no text index. At all.

- `grep -rE "fts5|FTS5| MATCH " src --include="*.py"` returns **zero** hits against any table. The only `tokeniz` hits are three docstrings saying P7 deliberately owns no tokenizer (`privacy/denial.py:219`, `privacy/gate.py:88`, `privacy/fixtures.py:272`).
- Document text lives in `text_units` (`evidence_shape/schema.py:115`) and is reachable only through `text_units_for_run(conn, run_id)` (`store.py:237`) or `text_unit_at(conn, run_id, container_path)` (`store.py:305`) — **both keyed by run, never by content**. The table carries `no_delete` and `no_rewrite` triggers (`schema.py:125-129`) but no content index.
- Observations are reachable by `file_id`, `run_id`, `observation_id`, or `observation_key` — never by `raw_value`.
- Vectors: `vector_arrays(subject_key, array_bytes, producer_version)` (`vectors.py:11-17`), and P1's docstring states outright that it exposes **"no similarity function, no index, and no nearest-neighbour query"** (`vectors.py:4-5`).
- The semantic channel that does exist, `grouping.retrieval._semantic_neighbors` (`retrieval.py:293`), is **file-to-file**: it fetches the *seed file's own* vector (`retrieval.py:317`), and returns `[]` if the seed has none. `similarity` and `similarity_threshold` are injected by the caller — P9 "authors no similarity measure and no threshold" (`retrieval.py:348-352`). **There is no path from a typed string to a vector.**

So `66` §2's "one retrieval model, not two rankings" is a constraint the engine cannot
currently satisfy in the direction Find needs: the existing retrieval model has no query
side. Find must add a query encoder plus either an inverted index over `text_units.text`
or a vector scan — and whichever it adds *is* the second ranking system unless it is
deliberately unified with `grouping.retrieval`'s channels.

### `placement_index_terms` is destination-only and cannot be reused

`placement_index_terms(record_id, plan_version, node_id, source_field, term_key,
term_value, ordinal, created_at)` — `placement/schema.py:64-73`.

It indexes **destination nodes, not files**. `source_field` "names the `IndexEntry` FIELD
the term was projected from" (`schema.py:60-61`), and `IndexEntry` (`index.py:47`) is one
row per legal node: `display_label`, `ancestor_labels`, `template_fields`,
`expected_values`, `group_labels`, `known_document_types`, `parent_context`,
`child_context`. Its two indexes are `(plan_version, source_field, term_key, term_value)`
and `(plan_version, source_field, node_id, term_key)` (`schema.py:142-151`) — both scoped
to a plan version.

Its purpose is stated in the schema comment: *"the engine retrieves the few most relevant
approved destination nodes, RATHER THAN SEARCHING THE ENTIRE FILESYSTEM"*
(`schema.py:56-58`). It is the narrowing that makes placement sub-quadratic; it is not a
corpus index. **Find could reuse it to search *folders*, and could not use it to search
*files*.** It also disappears when no tree is frozen — and `66`:81 says a user "must never
be required to build a destination tree" to search.

---

## 5. The shared structures — the explicit interface list

What each unbuilt piece consumes from the built engine, and what it must publish. **The
rows marked ⚠ are records that two unbuilt pieces both need. Those are the ones worth
naming now, because they are the ones two builders would each assume the other owns.**

### Find

**Consumes (all exist):** `get_file` · `file_path_history` · `facts.read_surface.*` ·
`observations_by_key` · `text_units_for_run` · `ClassificationStore.current` ·
`resolve_class` · `display_policy` · `summarize_protected` · `current_group` ·
`memberships_for_group` · `group_state_as_of` · `frozen_tree` · `entry_for` ·
`current_decision` · `decision_history` · `is_protected_container`.

**Must publish (none exist):**

1. ⚠ **`corpus_enumeration`** — an ordered, scoped iteration over indexed files. Needed by Find, by `summarize_protected`'s `files_in_scope` parameter, and by any corpus-wide count. Today every caller injects its own.
2. ⚠ **`text_search_index`** — the inverted index or vector index over `text_units.text` plus `files.filename`/`normalized_filename`. New capability, §4.
3. ⚠ **`memberships_for_file(conn, *, file_id, content_hash) -> tuple[Membership, ...]`** — the missing P9 reader for state 3. The index exists (`grouping/schema.py:84`); this belongs in `grouping/store.py` beside `memberships_for_group`, **not** in a Find module.
4. **`search_result`** — the projection carrying the six §3 states plus the match explanation. Its explanation fields should be `Support` (`grouping/records.py:104`) and `MatchingFact` (`placement/records.py:173`) verbatim, not a new shape.
5. **`search_scope`** — `66`:206-212's visible, editable active scope. No analogue exists.
6. **`protected_search_unlock`** — the local re-authentication state of `66`:174. P7 has consent (`privacy/consent.py`) and revocation (`privacy/revocation.py`) but no session unlock.

### P12 (apply/undo)

**Consumes (all exist):** `current_decision` (only `outcome = place`) · `frozen_tree` /
`legal_destination_ids` · `FreezeRecord.cross_folder_moves` · `privacy_state_for` ·
`get_file` · `hash_file` · `volume_id_for` · the `events` writer.

**Must publish:** the move plan record with all thirteen §8.3 fields
(`P12-.../SPEC.md:252-266`); ⚠ **the node→path resolution record** (`SPEC.md:315`);
precondition verdict with the five staleness triggers (`SPEC.md:293`); collision
resolution record; execution record with V1–V4 (`SPEC.md:414`); ⚠ **the journal entry**
(`SPEC.md:501`); undo verdict (`SPEC.md:520`).

### P13 (review surface)

**Consumes (all exist except two):** the whole of `PlacementDecision` · `GroupPlan`
(`placement/groups.py:145`) · `frozen_tree` + `nodes_for_version` + `diff_versions` ·
`display_policy` + `Gate` · `evidence_chain` + `observations_by_key` ·
`scan_run_summary`. **Does not exist:** a read-back of `residual_sets` (§1 row 6), and any
live-DB completeness count (§3).

**Must publish:** `review_item` (`P13-.../SPEC.md:176`) · `review_action`
(`SPEC.md:242`) · ⚠ **`progress_line`** (`SPEC.md:317`) · **`review_approval`**
(`SPEC.md:353`) · the `NeedsConsent` surface (`SPEC.md:382`).

### Onboarding question registry (`66` §12–§17)

**Consumes (exists):** `facts.domains.ActivationSignal(schema_id, activates)` and
`ActivationSignals(signals)` (`domains.py:90`, `:112`) — **this is the schema-activation
seam already built, and it is injected: "No default: P6 authors none of these."**
Also `active_domains` (`domains.py:124`), `schema_fields` (`domains.py:179`),
`user_level_edits` (`tree_design/user_edits.py:175`), `diff_versions`.

**Must publish (none exist):** ⚠ **`structural_answer`** — raw wording, proposed mappings,
confirmation state, scope, plan version, inferred-vs-confirmed flag, and the explanation
of what it activates (`66`:462, `66`:562). A `contextual_answer` record that is
structurally *unable* to reach placement. A `relationship_record` for §15's person
categories with the label-permission table. And ⚠ **`answer_revision_diff`** — §17's
"which schemas become active, which templates affected, which proposals become invalid."

### The collisions — records two unbuilt pieces both need

| ⚠ Shared record | Who needs it | Why catching it now matters |
|---|---|---|
| **`progress_line` / the completeness counts** | **Find §5** and **P13 §3** | This is the sharpest instance of the failure class in the brief. `66`:194 prints four numbers; `P13-.../SPEC.md:317-350` specifies the same numbers as a record P13 owns, with assembly rules, a source field per entry, and the rule that *"no indexed file may be absent from every entry."* Built separately, Find gets a banner and P13 gets a progress line, and they will disagree — because P13's rules are written down and Find's are not. **P13's `progress_line` should be built first, in a part both can read, and Find should render it.** |
| **`corpus_enumeration`** | **Find**, **P13's `progress_line`**, **`summarize_protected`**, any File policy's source scope | Four consumers, zero implementations, and one existing parameter (`files_in_scope`, `display.py:141`) that documents the absence as an open question. |
| **`memberships_for_file`** | **Find** (state 3), **P13**'s group plan item, **File** policy exclusion "files with unresolved multiple homes" (`66`:307) | Belongs to P9. Index built, reader not. If Find writes its own `SELECT ... WHERE file_id`, it bypasses `group_state_as_of` and will show rejected groups as relationships. |
| **`text_search_index`** | **Find** (§4), and **File** policy evidence standards that reference document text | The only genuinely new subsystem on this list. |
| **node → filesystem path resolution** | **P12** (Contract out §3), **Find** state 2 if it ever shows a path, **File**'s dry-run preview | P12 owns it. Find must be built to render `ancestor_labels` and never a path, or it will need P12 to exist first. |
| **`journal entry` / move history** | **P12** (§6), **File**'s activity list (`66`:337), **Find** state 5 after P12 ships | `66`:337 asks for source path, destination, evidence summary, authorizing policy, collision behaviour, time, status, undo availability. P12's journal has all of it except *the authorizing policy*, which does not exist because filing policies do not exist. **P12's journal needs a nullable `filing_policy_ref` from day one**, or File will need a parallel log. |
| **`structural_answer`** | **onboarding**, **P10** (gates a template), **P6** (`ActivationSignals`), **P13** (§17's diff surface) | The registry has three readers and no writer. `ActivationSignals` is the injection point already built for it. |
| **plan-version diff** | **onboarding §17**, **P13** `plan_version` surface, **File**'s "plan is stale" | `tree_design.diff.diff_versions` (`diff.py:50`) exists and covers nodes only. §17 also needs schema/template/proposal deltas, which nothing produces. |

---

## 6. Summary of findings

1. **3 of `66` §3's six states are cleanly answerable today**; one more (filed home) is answerable as a label chain but not as a path, which is what the design asks for and not what a builder will expect; two (also-related-to, shared-material) are not answerable at all.
2. **The file→group reader is the single highest-value missing read.** P9 built the index (`grouping/schema.py:84`) and never the function. It blocks §3 states 3 and 4, P13's group plan item, and File's multi-home exclusion.
3. **The biggest missing capability is a text index.** Nothing in `src/` matches a phrase against document text; `text_units` is addressable only by `run_id`; vectors have no query side and P1's docstring says so explicitly. `placement_index_terms` is destination-only and vanishes without a frozen tree.
4. **Three of `66` §5's four counts have no production reader.** They exist only as `eval_harness.counts.bundle_counts` over P2's `bundle_*` replay tables. The prior audit's claim that `unreadable` is never written in production is wrong on two paths (`router.py:184`, `archive.py:172`), but its conclusion holds for a different reason: `unreadable` alone under-reports, which is why P5's mapping pairs it with `failed`.
5. **`residual_sets` is INSERT-only.** `surface_residual_sets` writes it (`residual.py:193`) and nothing reads it back. P13's residual screen and Find's "possible placement" for undecided files both depend on a read that does not exist.
6. **The named shared interface is `progress_line`.** `66` §5 and `P13-.../SPEC.md:317` specify the same record; only P13's version has assembly rules. Build it once, in P13, and let Find render it.

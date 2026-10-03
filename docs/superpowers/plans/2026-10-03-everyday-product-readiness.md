# Everyday Product Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the non-UI product reliable for daily use over a real local file library, with correct search, safe assistant behavior, consistent relationships, durable file actions, trustworthy memory, installable packaging, recovery, and optional external integrations.

**Scope:** This plan intentionally excludes the graphical UI. The supported product surface during this work is the installed CLI plus the local database and assistant runtime. No task should create a GUI or require one for acceptance.

**Architecture:** Keep the filesystem as the source of truth and SQLite as derived working memory. Introduce explicit freshness, operation, relationship, and release states instead of relying on implicit ordering. Route every assistant tool through one policy boundary; route every filesystem mutation through one journaled state machine; expose only evidence-backed, human-approved relationships and plans.

**Tech Stack:** Python 3.12, SQLite/WAL, FTS5, existing vector adapter, pytest, wheel builds, temporary-directory integration tests, macOS FSEvents with polling fallback, optional BYOK OpenAI-compatible/Anthropic clients.

---

## Release contract

The product can enter supervised daily use only when all of these are true:

1. A clean wheel installs and loads every packaged profile, prompt, and entry point.
2. Search converges after create, edit, rename, move, delete, restart, and watcher downtime.
3. No answer or citation uses a deleted, stale, protected, or unverified item.
4. Every cloud or local-model request has an explicit provider, endpoint, trust policy, byte count, and ledger record.
5. No relationship becomes approved without a human-bound approval record.
6. No move can overwrite bytes, escape an allowed root, move a held item, or lose recovery state after process death.
7. Undo refuses to move bytes whose identity no longer matches the journal.
8. Memory steering is disabled unless a version-bound evaluation artifact passes precision, coverage, provenance, and regression gates.
9. Graph, Board, Timeline, deadline, nudge, and assistant relationship queries project the same canonical relationship state.
10. Backup, restore, migration, integrity check, and interrupted-run recovery are documented and tested.
11. Live Gmail/Calendar remain opt-in and transactional; fixture mode never masquerades as live mode.
12. The full release command passes from a clean checkout and clean environment without network access unless a test explicitly opts into a live provider.

## Dependency order

```text
T1 packaging/provider contracts ─┬─> T2 index identity and freshness ─> T3 retrieval quality
                                └─> T4 assistant policy boundary ────┐
T5 relationship transaction model ───────────────────────────────────┼─> T8 daily-use pilot
T6 move journal and recovery ────────────────────────────────────────┤
T7 memory provenance and gate ────────────────────────────────────────┤
T9 backup/migration/privacy ──────────────────────────────────────────┘
T10 fixture/live integration boundary ────────────────────────────────┘
T11 release harness and operational runbook
```

Each task below is independently testable. Do not enable later behavior behind a feature flag until the preceding task's exit tests pass.

### Task 1: Make the installed artifact and provider route deterministic

**Files:**
- Modify: `pyproject.toml`
- Modify: `src/items/profiles/` package data declaration
- Modify: `src/assistant/provider.py`
- Modify: `src/assistant/trust.py`
- Test: `tests/test_packaging_install.py`
- Test: `tests/assistant/test_provider_resolution.py`

- [ ] Write a failing wheel test that builds a wheel in a temporary directory, installs it into a second temporary environment, and asserts `load_profile("student")`, `load_profile("files_only")`, and `load_profile("job_seeker")` succeed.
- [ ] Write provider matrix tests for exactly these environments: DeepSeek only, OpenAI only, Anthropic only, explicit provider with missing key, multiple keys with explicit provider, and no keys.
- [ ] Make provider selection explicit: an explicit `ASSISTANT_PROVIDER` selects only that provider; an OpenAI key defaults to the OpenAI endpoint/model; a DeepSeek key defaults to DeepSeek; ambiguous multiple-key configuration refuses with an actionable message.
- [ ] Add package data for `items/profiles/*.json`, assistant prompt resources, and any runtime fixtures required by the installed command.
- [ ] Add a clean-environment test that runs `database-agent --help`, `database-agent ask --show-local-capability`, and profile loading without repository `PYTHONPATH`.
- [ ] Run `python3 -m pytest tests/test_packaging_install.py tests/assistant/test_provider_resolution.py -q`; expected: all pass.
- [ ] Build with `python3 -m build --wheel --no-isolation` and inspect the archive contents; expected: profiles and entry point present.
- [ ] Commit as `fix: make wheel contents and provider routing deterministic`.

### Task 2: Define item identity and freshness state

**Files:**
- Modify: `src/items/identity.py`
- Modify: `src/items/file_identity.py`
- Modify: `src/items/schema.py`
- Modify: `src/database_agent/db.py`
- Create: `src/items/freshness.py`
- Test: `tests/items/test_identity_lifecycle.py`
- Test: `tests/items/test_freshness_state.py`

- [ ] Add durable fields for `content_hash`, `size`, `mtime_ns`, `st_dev`, `st_ino`, `last_seen_at`, `last_indexed_hash`, and `freshness_state` (`fresh`, `dirty`, `missing`, `conflicted`, `indexing`, `error`).
- [ ] Write failing lifecycle tests for create, content edit, rename with same inode, delete, replacement at same path, and edit while offline.
- [ ] Make reconcile compare inode/file identity first, then hash and metadata; a path match with a changed hash must create a dirty version rather than silently reuse old evidence.
- [ ] Mark missing items missing immediately during reconciliation; do not leave them searchable as live.
- [ ] Record an append-only identity event for every state transition so a stale search can be diagnosed.
- [ ] Make schema migration idempotent and test migration from every checked-in prior schema version.
- [ ] Run lifecycle tests twice in randomized order; expected: no order-dependent state.
- [ ] Commit as `feat: add durable item freshness and identity states`.

### Task 3: Make index refresh complete, incremental, and restart-safe

**Files:**
- Modify: `src/items/hot_index.py`
- Modify: `src/items/path_watch.py`
- Modify: `src/items/fsevents_feed.py`
- Modify: `src/items/fsevents_live.py`
- Create: `src/items/index_refresh.py`
- Test: `tests/items/test_index_freshness.py`
- Test: `tests/items/test_path_watch_recovery.py`
- Test: `tests/items/test_index_concurrency.py`

- [ ] Write failing tests proving that an edit, rename, delete, and offline change are reflected in search before the next query returns.
- [ ] Replace “rebuild only when FTS is empty” with an explicit refresh queue keyed by item ID and content hash.
- [ ] On watcher startup, run a bounded reconciliation pass before declaring the index ready; expose `index_state` (`starting`, `catching_up`, `ready`, `degraded`) and counts.
- [ ] Debounce by stable file identity, not only path and mtime; retain the latest event and re-read metadata/hash immediately before indexing.
- [ ] Use a monotonic event cursor or durable scan watermark so a restart cannot skip events.
- [ ] Make two roots use independent watcher state while sharing one refresh queue; avoid full-index rebuild on every idle tick.
- [ ] Ensure refresh failures leave the item dirty and retryable with a recorded error, rather than silently serving old evidence as current.
- [ ] Add tests for rapid edits, rename-plus-edit, watcher downtime, duplicate event delivery, and process restart.
- [ ] Run `pytest tests/items/test_index_freshness.py tests/items/test_path_watch_recovery.py tests/items/test_index_concurrency.py -q`; expected: all pass.
- [ ] Commit as `feat: make index refresh durable and restart-safe`.

### Task 4: Implement real chunk retrieval and honest search evaluation

**Files:**
- Modify: `src/items/hot_index.py`
- Modify: `src/items/bakeoff.py`
- Modify: `tools/run_embedding_bakeoff.py`
- Create: `tests/fixtures/search_golden_real.json`
- Create: `tools/evaluate_search.py`
- Test: `tests/items/test_chunk_retrieval.py`
- Test: `tests/items/test_search_quality_gate.py`

- [ ] Write a failing test with a marker after character 4,000; search must find the file and cite the matching chunk.
- [ ] Search `item_chunks` directly for FTS candidates, aggregate chunk ranks to item ranks, and retain the best matching chunk/source ID.
- [ ] Store versioned chunk embeddings and search them by chunk, then aggregate to item cards. Fall back to FTS only when the embedding model is unavailable.
- [ ] Separate filename/path, evidence, and chunk citations in result cards; never claim a body match when only a filename matched.
- [ ] Build a real labeled golden set with paraphrases, aliases, OCR noise, long-document late evidence, English, Traditional Chinese, mixed-language, and negative queries. Do not generate labels from the same filename stems used as queries.
- [ ] Evaluate Recall@10, MRR, nDCG@10, abstention, and citation correctness with bootstrap confidence intervals.
- [ ] Require hybrid retrieval to beat FTS-only on paraphrase queries without regressing CJK literal recall; otherwise ship FTS-only and record that decision.
- [ ] Add a quality gate that fails if a deleted/missing item is returned or if a citation points to stale evidence.
- [ ] Run the quality gate against a real copied corpus and a synthetic adversarial corpus; expected: both pass.
- [ ] Commit as `feat: retrieve indexed chunks and add honest search quality gate`.

### Task 5: Centralize assistant policy, trust, citations, and egress

**Files:**
- Modify: `src/assistant/tools.py`
- Modify: `src/assistant/organize_tools.py`
- Modify: `src/assistant/chat.py`
- Modify: `src/assistant/egress.py`
- Modify: `src/assistant/provider.py`
- Create: `src/assistant/policy.py`
- Test: `tests/assistant/test_policy_boundary.py`
- Test: `tests/assistant/test_egress_accounting.py`
- Test: `tests/assistant/test_deferred_tools_security.py`

- [ ] Write failing tests showing every base and deferred tool passes through one policy function.
- [ ] Add one policy result type with `allowed`, `reason`, `protected`, `untrusted`, `bytes_in`, `bytes_out`, `citations`, and `egress_class`.
- [ ] Refuse `extract_one` for held/protected items and remove protected paths from all tool payloads, not only `read_item`.
- [ ] Mark event titles, email subjects, labels, basenames, snippets, and all file-derived fields as untrusted data.
- [ ] Validate all tool arguments against schemas before dispatch; reject non-integer limits, unknown fields, path strings, and free-form destinations.
- [ ] Make deferred tool schemas appear only after explicit `request_tools`, and ensure the model receives the exact schema it can call.
- [ ] Compute egress bytes from the serialized request envelope and response envelope, with one ledger row per provider request and session summary derived from those rows.
- [ ] Validate citations against returned item IDs and source IDs; refuse invented citations rather than printing them.
- [ ] Restrict local-only generation to an explicitly configured local transport and label remote local-compatible endpoints as cloud/provider egress.
- [ ] Run all injection fixtures three times plus new held/deferred/citation/accounting tests; expected: zero write calls from file text and zero protected bytes in request fixtures.
- [ ] Commit as `security: enforce one assistant policy boundary for every tool`.

### Task 6: Make relationship approval and projections canonical

**Files:**
- Modify: `src/items/relationships.py`
- Modify: `src/items/decisions.py`
- Modify: `src/items/connector.py`
- Modify: `src/items/views.py`
- Modify: `src/items/deadline_view.py`
- Modify: `src/items/nudge.py`
- Modify: `src/items/people.py`
- Create: `src/items/relationship_service.py`
- Test: `tests/items/test_relationship_approval.py`
- Test: `tests/items/test_relationship_projections.py`
- Test: `tests/items/test_people_merge_migration.py`

- [ ] Define one canonical relationship state machine: `proposed -> approved|rejected`, `approved -> superseded`, with immutable decision records.
- [ ] Require approval to bind `relationship_id`, evidence IDs, item content versions, actor/session ID, timestamp, and approval hash.
- [ ] Make `accept_link`, person merge, and bulk relationship actions call this service; direct SQL state changes are prohibited by tests.
- [ ] On item version change, supersede or revalidate relationships whose evidence depended on the old version.
- [ ] On person merge, migrate relationships and decisions from the dropped ID to the kept ID transactionally, preserving provenance.
- [ ] Make Graph, Board, deadlines, nudges, and assistant `list_related` query the same canonical projection helper.
- [ ] Exclude cancelled/declined events and unrelated future events from nudges; include evidence for the selected event.
- [ ] Make fixture imports atomic: invalid input rolls back the whole fixture, and account/calendar IDs participate in event identity.
- [ ] Test approved inferred links, rejected links, duplicate invalidation, person merges, cancelled events, multiple calendars, and partial imports.
- [ ] Commit as `feat: canonicalize relationship approval and projections`.

### Task 7: Make apply, undo, and crash recovery transactional

**Files:**
- Modify: `src/assistant/apply.py`
- Modify: `src/assistant/undo.py`
- Modify: `src/assistant/journal.py`
- Modify: `src/assistant/plans.py`
- Modify: `src/assistant/place_preview.py`
- Create: `src/assistant/recovery.py`
- Test: `tests/assistant/test_apply_atomicity.py`
- Test: `tests/assistant/test_crash_recovery.py`
- Test: `tests/assistant/test_no_clobber_and_hash.py`

- [ ] Write failing subprocess tests that terminate before move, after journal insert, after move, and before applied-state update.
- [ ] Use explicit journal states: `planned`, `moving`, `moved_uncommitted`, `applied`, `undo_planned`, `undone`, `conflicted`, `failed`.
- [ ] Persist the operation and source identity before touching the filesystem; update state with a durable commit after the filesystem operation.
- [ ] On startup, scan nonterminal journal states and classify them from source/destination existence, inode, and hash; never blindly retry.
- [ ] Require non-null content hash, file ID, root scope, and protected-state snapshot for every plan operation.
- [ ] Revalidate all of those immediately before moving; reject changed sources, held items, symlink escapes, out-of-root destinations, and destination races.
- [ ] Use no-clobber atomic destination creation; never rely on an existence check followed by `shutil.move`.
- [ ] Undo only when the destination hash matches the journaled moved content; otherwise mark conflict and leave bytes untouched.
- [ ] Prevent apply after undo unless a new approval is created for a new plan hash.
- [ ] Update item paths, file identity, index freshness, and events after successful apply/undo through one transaction boundary.
- [ ] Run crash, race, hash, symlink, held-file, collision, and apply-undo-apply tests; expected: no data loss and explicit conflicts.
- [ ] Commit as `feat: make file actions crash-safe and content-identity-safe`.

### Task 8: Connect correction memory to real user decisions, but keep steering dark

**Files:**
- Modify: `src/assistant/memory_l0.py`
- Modify: `src/assistant/memory_v1.py`
- Modify: `src/assistant/memory_v2.py`
- Modify: `src/assistant/playbook_rollups.py`
- Modify: `src/items/decisions.py`
- Create: `src/assistant/memory_release.py`
- Test: `tests/assistant/test_memory_capture_integration.py`
- Test: `tests/assistant/test_memory_release_binding.py`
- Create: `tests/fixtures/memory_gate_realistic.json`

- [ ] Capture a DiffEvent for every user reject, edit, accept-correction, relationship decision, and plan correction, including item versions and session trust flags.
- [ ] Make source IDs resolvable foreign references; reject atoms whose source DiffEvents do not exist or whose items have changed versions.
- [ ] Keep v1 explicit rules available only as visible user rules; keep v2 atoms dark until a release artifact passes.
- [ ] Replace static “willing/gold” arithmetic with recorded proposal predictions, abstentions, labels, model version, corpus version, and rule baseline.
- [ ] Require precision >= 0.95, coverage >= 0.20, beat rules-only, minimum sample count, no safety-hold regressions, and a clean regression set.
- [ ] Bind atom steering to gate ID, corpus hash, evaluator version, model fingerprint, and atom source IDs. A new atom or changed model invalidates steering.
- [ ] Add an explicit `memory release` command that prints the gate evidence and requires a deliberate enable action; default remains dark.
- [ ] Test dirty sessions, orphan source IDs, stale gate records, contradictory atoms, safety holds, and newly added atoms after a previous pass.
- [ ] Commit as `feat: wire correction capture and version-bound memory releases`.

### Task 9: Add database backup, restore, integrity, and migration operations

**Files:**
- Modify: `src/database_agent/db.py`
- Create: `src/database_agent/maintenance.py`
- Modify: `src/cli.py`
- Test: `tests/test_database_maintenance.py`
- Test: `tests/test_database_migrations.py`

- [ ] Add commands: `database-agent db check`, `database-agent db backup PATH`, `database-agent db restore PATH`, and `database-agent db rebuild-index`.
- [ ] `check` must run SQLite integrity checks, verify schema versions, count dirty/missing/indexing items, and report unapplied journal states.
- [ ] `backup` must use SQLite backup API while writers are coordinated; include schema version and content manifest.
- [ ] `restore` must restore into a new path, validate integrity, and require an explicit target before replacement.
- [ ] Test every migration from checked-in schema fixtures and verify data preservation, event history, relationships, plans, memory, and index rebuildability.
- [ ] Test interruption during backup, restore, migration, and index rebuild; expected: original database remains usable.
- [ ] Commit as `ops: add backup restore integrity and migration commands`.

### Task 10: Harden privacy at rest and explicit external-data boundaries

**Files:**
- Modify: `src/assistant/trust.py`
- Modify: `src/database_agent/db.py`
- Modify: `src/items/mailbox.py`
- Modify: `src/items/commands.py`
- Create: `src/database_agent/privacy.py`
- Test: `tests/test_privacy_at_rest.py`
- Test: `tests/items/test_fixture_transactionality.py`

- [ ] Document exactly which metadata, excerpts, paths, email headers, and event fields are stored locally.
- [ ] Add encrypted database/index support using a platform key store where available; fail closed or clearly warn when protected data would be stored unencrypted.
- [ ] Keep raw bodies and attachment bytes out of the database; test fixture payloads containing secrets.
- [ ] Gate opening held/protected details behind local authorization and keep cloud egress impossible even after authorization unless separately approved.
- [ ] Make fixture imports all-or-nothing and record account scope, consent, source, and sync cursor.
- [ ] Add explicit data deletion/export commands with an audit event and tests that verify deletion from primary tables, FTS, chunks, vectors, and backups according to the declared policy.
- [ ] Commit as `security: enforce local privacy and external-data boundaries`.

Task 11: cut by owner 2026-10-03 — Gmail/Calendar removed from the product.

### Task 12: Build the no-UI release and daily-use harness

**Files:**
- Modify: `tools/run_assistant_gates.sh`
- Create: `tools/run_release_gates.sh`
- Create: `tools/run_daily_use_pilot.py`
- Create: `docs/operations/everyday-product-runbook.md`
- Create: `docs/operations/release-checklist.md`
- Test: `tests/test_release_gates.py`

- [ ] Make the release harness run from a clean temporary virtual environment and installed wheel.
- [ ] Run packaging, provider, schema migration, freshness, retrieval quality, injection, privacy, relationship, memory, action recovery, backup, and connector contract suites.
- [ ] Run against a copied real corpus with cloud disabled; report item count, dirty/missing count, stale-index count, search metrics, relationship counts, and unresolved recovery states.
- [ ] Add a supervised pilot script that exercises: initial scan, restart, edit, rename, delete, search, explain, relationship proposal, rejection, plan preview, approval, apply, crash recovery, undo, backup, restore, and fixture sync.
- [ ] Produce a machine-readable report with pass/fail, artifact hashes, environment, schema version, model/provider configuration, and all skipped tests with reasons.
- [ ] Define pilot thresholds: zero stale/deleted search results, zero protected egress, zero unapproved writes, zero data-loss incidents, zero unresolved journal states, and 100% installed-profile loading.
- [ ] Document incident recovery and the command to disable cloud, disable memory steering, disable apply, rebuild the index, and restore a backup.
- [ ] Run `bash tools/run_release_gates.sh` from a clean checkout; expected: all gates pass and report is written.
- [ ] Commit as `test: add reproducible non-UI release and daily-use gates`.

## Final verification sequence

Run these only after all tasks are complete:

```bash
python3 -m pytest -q tests/test_packaging_install.py tests/assistant tests/items
python3 -m pytest -q tests/test_database_maintenance.py tests/test_database_migrations.py
python3 -m pytest -q tests/assistant/test_crash_recovery.py tests/assistant/test_no_clobber_and_hash.py
python3 -m pytest -q tests/test_release_gates.py
bash tools/run_release_gates.sh
```

Then run the daily-use pilot against a copied corpus with:

```bash
python3 tools/run_daily_use_pilot.py \
  --database /tmp/everyday-pilot.sqlite \
  --copy /tmp/everyday-pilot-copy \
  --cloud off \
  --memory-steering off \
  --apply off
```

The product is ready for a supervised non-UI pilot only when the final report contains no failures, no unresolved warnings in the journal or freshness queue, and no skipped safety test. It is ready for unsupervised daily use only after a multi-day pilot produces zero data-loss, stale-answer, protected-egress, or unapproved-action incidents.

## Plan self-review

- Packaging and provider routing: Task 1.
- File identity, freshness, watchers, stale search, chunks, and retrieval quality: Tasks 2–4.
- Assistant privacy, injection, citations, egress, and deferred tools: Task 5.
- Graph, relationships, people, deadlines, nudges, and connectors: Task 6 and Task 11.
- Apply, undo, collision, crash recovery, and journal repair: Task 7.
- Correction capture, evaluation, provenance, and dark steering: Task 8.
- Backup, restore, migration, integrity, and privacy at rest: Tasks 9–10.
- Release automation, operational runbook, and daily-use evidence: Task 12.
- UI is intentionally excluded from every task and every release gate.

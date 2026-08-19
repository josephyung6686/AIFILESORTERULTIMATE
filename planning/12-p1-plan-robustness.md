# P1 plan robustness

Date: 2026-08-19
Status: **do not execute as written** — the TDD package is strong; three tasks would poison provenance
Scope: live [`parts/P1-storage-identity-provenance/PLAN.md`](parts/P1-storage-identity-provenance/PLAN.md) against the live P1 [`SPEC.md`](parts/P1-storage-identity-provenance/SPEC.md), [`01-product-design-structured.md`](01-product-design-structured.md) §0 / §8.2, [`02-segmentation-map.md`](02-segmentation-map.md), Graphify's honesty rules, and the later bindings [`09`](09-plan-spec-critique.md) / [`10`](10-i4-learning-ops.md) / [`11`](11-ops-runtime.md)
Source of truth: [`00-database-agent-product-design.md`](00-database-agent-product-design.md)

Prior reviews were treated as evidence, then re-checked against live plan and spec text rather than trusted as current.

**Verdict:** The plan is not perfect. It is a complete pytest-first work package for a substrate, not a freeze-ready implementation of the P1 contract. Identity (I1) and SHA-256 (I2) are now ratified in the SPEC and correctly rewritten in Task 6 — [`09`](09-plan-spec-critique.md) is stale on those two. What remains would land a provenance lie, a runtime-minted event type, and an unstable volume identifier in the database every later part foreign-keys. Rewrite Tasks 6, 8, and 9 first. Tasks 1–5, 7, 10–12 are executable only after P1 stops authoring events and the registry is frozen from the SPECs.

| Count | What |
|---|---|
| 13 | Tasks in the plan |
| 16 | Done-means in the live SPEC |
| 13 / 16 | Done-means the plan actually covers |
| 3 | Tasks that must not execute as written (6, 8, 9) |
| 1 | Published Contract-out surface with no task (§10) |

A P1 plan is robust if a later part can be built against it without inheriting a foreign-key lie, a provenance lie, or a silently answered open question. Completeness of pytest steps is not the test. The structure map is explicit: freeze contracts, then walk a skeleton, then deepen. This plan already writes runnable substrate while three authorship rules and one published surface are still wrong.

---

## What 09 got wrong by going stale

If you re-read [`09`](09-plan-spec-critique.md) today it will tell you not to execute Task 6 because two live copies collapse into one `current_path`, and that the plan pins `blake2b-256`. Both are fixed in the live text. Trust grep, not that document, for I1 and I2.

| 09 finding | Live status |
|---|---|
| **I1** identity still open; PLAN collapses duplicates | **Settled in SPEC** (ratified 2026-08-19). Task 6 tests keep two live copies as two rows sharing a hash; a gone original is a move. |
| **I2** hash algorithm open; PLAN vs P4 disagree | **Settled in SPEC.** `HASH_ALGORITHM = "sha256"`, streamed, 64 hex chars. Matches P4's `observation_key`. |
| **I3** `st_dev` persisted | **Still true.** Task 2 comments that `st_dev` is within-session only; Task 3 stores it on every `files` row. OQ9 remains open. |
| **I4** analysis tiers unnamed | Closed at the contract layer by [`10`](10-i4-learning-ops.md). P1 still stores the map opaquely — correct. The plan does not need to name the four keys. |
| Product-ops holes (form factor, FSEvents, dataless iCloud, crash, concurrency, DB location, learning reads) | Owned by [`11`](11-ops-runtime.md) and [`10`](10-i4-learning-ops.md). They are no longer unowned. They are also **not in the P1 PLAN**, so executing the plan still ignores them. |

Task 6 is no longer the I1 failure. It is now an authorship failure. Do not recycle the old reason.

---

## Against the structure map

| Map rule | Plan status |
|---|---|
| SPECs freeze before plans decide identity | I1 and I2 now closed in SPEC, then mirrored in Task 6. Order recovered. |
| P1 publishes `files` + append-only `events`; P3 authors scan events | `observe_path` and `verify_content` author `hashing` / `stat observation` as `subsystem="P1"`. |
| Walking skeleton: hash, file row, discovery by P3 fixture | Task 13 does that, but only after `observe_path` has already appended a hashing event as P1. |
| From P1 onward, graphify path-checks seams before code | No `graphify-out/`, no hook, no update step, no path query in the plan. |

**Graphify honesty, applied to P1.** Graphify refuses to invent an edge, refuses to stamp a file that produced no output, and refuses to shrink a good graph. The P1 plan is trying to be the same kind of substrate for files. Three of its own honesty rules are currently violated in the published code:

1. Registration is specified as a spec-level act, then implemented as a process-local dict that Task 9 mutates to mint `preference reset`.
2. Volume id is documented as within-session only, then persisted on every `files` row via `st_dev`.
3. P1 "appends no event on its own initiative," then `observe_path`, `verify_content`, and `reset_preferences` all append as `subsystem="P1"`.

---

## Contract-out coverage

The plan's self-review claims every Contract-out section has a task and maps Done-means 1–15. The live SPEC has **ten** surfaces and **sixteen** Done-means.

| Contract out | SPEC claim | Plan task | Fit |
|---|---|---|---|
| §1 Identity R1–R6 | SHA-256; two live copies are two rows | T2 + T6 | Tests match I1/I2; volume id still OQ9 |
| §2 `files` + five histories | path history includes `volume_id` | T3 + T6 | Four histories deferred (correct); path history drops `volume_id` |
| §3 events + registration | Spec-level union; P1 originates none of the scan types | T4 + T5 | Triggers are strong; registry is runtime and in-memory |
| §4 supersede columns | old row never mutated | T7 | Value preserved; link columns `UPDATE` the old row |
| §5 V1–V4 | `hashing` event authored by P12, subsystem P1 as performer | T8 | Records as `stat observation`, subsystem P1 |
| §6 database handle | one SQLite, transactional, inspectable | T1 | WAL + FULL + FK pragma; no migrate path; `open_database` does not call `create_schema` |
| §7 learning store | exact scope; reset honoured on later reads | T9 | subject stuffed into `file_id`; reset is a no-op filter |
| §8 fifteen ceilings | hold, do not enforce | T10 | Matches |
| §9 vector arrays | opaque bytes, no similarity | T11 | Matches |
| §10 `scan_resource_usage` | Done-means 16; six counters | none | Missing entirely |

---

## Do not execute these as written

Each of these would land in the database every later part foreign-keys or audits. Fixing them after P3/P12 exist means rewriting history.

### B1 — P1 authors events it does not own

**Where:** Task 6 `observe_path`, Task 8 `verify_content`, Task 13 skeleton.

**What the plan does:** appends `hashing` / `stat observation` with `subsystem="P1"`.

**Why it is blocking.** SPEC Contract-in: P1 originates none of those types. M8: the acting part authors; P1 writes. Scan types belong to P3. V1–V4 hashing belongs to P12 with P1 named as performer. A log that says P1 discovered the file cannot satisfy §8.2 reconstruction ("what it knew, what it proposed, what the user approved, what changed on disk, and why").

### B2 — event types minted at runtime

**Where:** Task 5 `register_event_type`, Task 9 `reset_preferences`.

**What the plan does:** in-memory `_REGISTRY`. Task 9 writes `_REGISTRY["preference reset"] = None` at runtime, with `user_id="reset"` so the row passes the `user_id IS NOT NULL` filter.

**Why it is blocking.** SPEC rule 4: registration is a spec-level act; a part cannot mint a type at run time. `preference reset` is not one of the reserved nineteen and not in P13's three types. P13 already specified reset as `review_action` with `surface = learning` / `action = reset_learning`. After process restart the extra types vanish and appends start failing. Direct mutation of `_REGISTRY` also bypasses `register_event_type`'s reserved-name check.

### B3 — unstable volume id persisted

**Where:** Task 2 `volume_id_for` → Task 3 `files.volume_id`.

**What the plan does:** comment says `st_dev` is not stable across remount, rename, or cloud re-sync, so do not persist a cross-session decision until OQ9 is closed. Code returns `str(os.stat(path).st_dev)` and `record_file` stores it as `NOT NULL`.

**Why it is blocking.** OQ9 is still open and threatens P12. macOS remount changes `st_dev`, so §8.3's cross-volume copy-and-delete will misfire. The plan documents the danger and then stores the value anyway.

---

## Plan quietly answering the SPEC, or ignoring it

| Issue | SPEC | PLAN | Risk |
|---|---|---|---|
| Events with no file (OQ3) | Still open. `destination-tree edit` / `template application` / `graph-edge creation` are not per-file. | `events.file_id` is nullable. `learning_records` still keys every scope through `file_id`. | Domain/corpus learning cannot be addressed without stuffing a non-file subject into a file column. Threatens P9, P10, P13. [`10`](10-i4-learning-ops.md) now requires those parts to *query* this store before proposing — a wrong subject column makes every read a miss. |
| Reset honours later reads | Reset appends; later reads honour it; history stays inspectable. | `learning_records` returns every `user_id IS NOT NULL` row, including the reset, with no cutoff. | Reset is inspectable and operationally a no-op. Same hole 09 named, now worse because 10 made the reads real. |
| Scope spelling | Event column: `file \| group \| node \| …`. Prose in Contract-out §7: `destination node`. | `SCOPES = (…, "node", …)` | P13 uses the short form. P11 prose uses destination node. One spelling must be the stored value before any correction is appended. |
| V1–V4 event type | Verification writes a `hashing` event, authored by P12, subsystem names P1 as performer. | `verify_content` appends `event_type="stat observation"`, `subsystem="P1"`. | Fixity checks will be unqueryable as hashing. P2 per-stage replay will look at the wrong type. |
| MIME / scan_state invented in P1 | P3 supplies MIME, detected format, scan state. P1 stores them opaquely. | `record_file` guesses MIME from extension, sets `detected_format=None`, `scan_state="recorded"`. | P1 starts interpreting files. Done-means 8 will not catch `"recorded"` because it is not on the forbidden list. |
| Path history shape | `file_path_history` → `(path, volume_id, observed_at, event_id)` | `SELECT COALESCE(new_path, old_path) AS path, observed_at, event_id` | P12's expected source volume cannot be reconstructed from the published read surface. |
| Deleted-then-redownloaded heuristic | R2: same content at a new path is the same version when the old path is no longer live. | First matching hash whose path `.exists()` is false is treated as a move. | User deletes a file, later downloads the same bytes elsewhere: history of the old life is attached to the new one. Two deleted copies: oldest `rowid` wins. Not tested. |
| Content-change mutation unexplained | No mutation of `files` is accepted without the authoring part's event. | Prior row is `UPDATE`d to `scan_state=superseded_content` with no event on that `file_id`. | The version that facts still point at has no provenance explaining why it was superseded. |
| Done-means 7 completeness | Every non-optional field populated, including `component_version`. | `_minimal()` omits `component_version`; the test only checks columns exist. | The eleven-field check is weaker than the contract it claims to prove. |
| Supersede "never mutated" | A superseded row is never deleted and never mutated. | `mark_superseded` `UPDATE`s `superseded_by` and `supersede_reason` on the old row. Test only checks the value column. | Reasonable interpretation (links vs evidence), but it is an interpretation. Neighbouring parts will copy it. |
| [`11`](11-ops-runtime.md) database location | SQLite lives at `~/Library/Application Support/<bundle-id>/agent.sqlite`. Never inside a scan root. | `open_database(path)` takes a caller path. No default, no exclusion, no rebuild statement. | Task 1 will happily create the DB inside a fixture corpus. 11 closed OQ11 at runtime; the plan does not bind 11. |
| Dataless iCloud | 11: P3 detects dataless **before** hashing; do not materialize. | `hash_file` opens bytes. | Safe only if every caller is P3 and P3 never passes a dataless path. `observe_path` hashes unconditionally, so a test or a future caller bypasses 11. |

---

## Published and still absent from the plan

| Gap | Required by | Why it cannot wait |
|---|---|---|
| Contract out §10 `scan_resource_usage` / Done-means 16 | P1 SPEC, P3 SPEC (already cites P1 §10), P13 `progress_line` | P3 is the next part. If P1 ships without the row, P3 has nowhere to write the six §8.6 counters and will invent a second store. |
| Frozen event registry compiled from SPECs | P1 registration rule 4 | Need the reserved 19 plus P7×8, P8×5, P11×8, P13×3 loaded at schema init. Not a function neighbours call in tests. |
| Graphify hook + update + path check | 02 standing rule | The map's whole point is that seam questions stop being readable at code scale. This pass is already doing the 6,000-line read the map forbids. `graphify-out/graph.json` is absent. |
| Bind [`11`](11-ops-runtime.md) | OQ11, dataless hashing, WAL concurrency | 11 is now the runtime contract. P1 PLAN still reads as if those questions were open or unowned. |
| Schema migration | `SCHEMA_VERSION = 1` written every open | `user_version` is stamped, never compared. The first neighbouring table cannot land without an ad-hoc migration story. |
| `create_schema` not called from `open_database` | Task 1 vs Task 3 split | Every caller must remember both. Skeleton and neighbours will open a handle with no tables. |
| `invalidate_extraction_state` listed, never defined | Task 6 interface line | The `UPDATE` is inlined in `observe_path`. Neighbours that need R3 without going through `observe_path` have no published function. |
| Subject column for learning | 10: P6/P7/P8/P9/P10/P11 query `learning_records(scope, subject_id)` | `file_id` cannot be the subject for group / node / template / domain / corpus. OQ3 is the same hole. |

**Correctly deferred — do not invent these to look finished.** `file_facts_history`, `group_memberships_history`, `placement_history` (need P6/P9/P11 tables). `text_units` (P4 owns the shape). Delete-versus-append (I6, deferred to P7; PLAN correctly refuses to `DELETE` events). Ceiling values. Analysis-tier *completeness* values (keys are now known from 10; P1 still must not interpret them).

---

## Already sound — do not re-litigate

The plan got the hard identity decisions right after the freeze critique, and the TDD skeleton is real. Re-opening these will waste the next edit pass.

| What holds | Evidence in the live PLAN |
|---|---|
| I1 two live copies | `test_two_live_copies_are_two_records_sharing_one_hash`. Move case unlinks the original first. |
| I2 SHA-256 | `HASH_ALGORITHM = "sha256"`, streamed 1 MiB chunks, 64 hex chars. Matches P4 `observation_key`. |
| Append-only by trigger, not convention | `events_no_update` / `events_no_delete` `RAISE(ABORT)`. A neighbouring bug cannot `UPDATE` history. |
| `preferred` is not P1's column | `test_no_preferred_column_on_p1_tables` and `SUPERSEDE_COLUMNS` exactly the three shared names. |
| No vectors in `files`/`events` | Separate `vector_arrays` table; grep-style test forbids similarity/knn exports. |
| Fifteen ceiling keys, namespaced, unenforced | `grouping.*` and `placement.*` resolve independently; P1 rejects no operation. |
| No interpretation of facts/domains/classes | Task 12 forbidden-term scan. Ceiling keys and reserved event names allowed because the design states them. |
| Walking-skeleton P1 step exists | Task 13 is deterministic, no model, no cloud, no embeddings. That is the map's P1 slice. |
| Stdlib only, Python 3.12 pin, one module per surface | Matches §0 inspectability. A reviewer can reject one Contract-out section without touching neighbours. |
| I6 not silently closed | PLAN refuses to `DELETE` from `events`. Matches the 09/SPEC instruction not to foreclose tombstones. |

---

## Edit order if you want this plan executable

Nothing below is a redesign. Each item is a named decision or a surgery on one task.

| Order | Change | Unblocks |
|---|---|---|
| 1 | Stop P1 from authoring events. `observe_path` / `verify_content` accept an authoring `subsystem`, or become write-only helpers P3/P12 call after they append. | T6, T8, T13, M8 |
| 2 | Replace `register_event_type` with a frozen union compiled from the SPECs. Declare P1's reset as the P13 `review_action` it already is, or add the type to P1 SPEC before minting. | T5, T9, rule 4 |
| 3 | Do not persist `st_dev` until OQ9 closes. Store `volume_id` as nullable / session-tagged, or pick a stable identifier in the SPEC first. | T2, T3, P12 |
| 4 | Add Task 14: `scan_resource_usage`. Give `learning_records` a subject column that is not `file_id`. Honour reset as a cutoff. Bind [`11`](11-ops-runtime.md) for DB location and "P3 hashes, P1 does not open dataless files." | Done-means 16, P3, P13, 10's read path |
| 5 | Install graphify on the planning corpus, then path-check `files.file_id` → P3 `discovery` and `events.event_type` → P12 `hashing` before writing code. | Map standing rule |

Execute Tasks 1–5, 7, 10–12 only after 1 and 2. Do not execute Tasks 6, 8, or 9 until they are rewritten. Task 13 stays last and must not depend on P1-authored `hashing` events.

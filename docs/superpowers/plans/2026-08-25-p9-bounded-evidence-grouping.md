# P9 Bounded Evidence Grouping Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build P9 so validated P6 anchors produce bounded, privacy-safe, reviewable groups whose memberships remain evidence-backed, replayable, append-only, and incapable of being established by embeddings alone.

**North-star user experience:** P9 proposes only what it can explain. Every suggestion
must show the strongest independent evidence, its source location, uncertainty, and
the next safe action. Users can accept, edit, reject, defer, or undo a proposal; no
proposal silently becomes an irreversible organization decision. The default view is
small and decision-focused, with layered detail for evidence, provenance, conflicts,
and history. Missing knowledge or weak evidence produces a comprehensible candidate
or review state—not a confident-looking guess.

**Architecture:** P9 is a deterministic seed, retrieval, graph, stop-rule, and dossier layer around one injected P8 group-evaluation seam. Shared evidence (`Group`, `Membership`, dossiers, edges, failures, embeddings) is stored once; only `group_acceptance` is plan-versioned. Unfinished domain knowledge, compatibility tables, thresholds, embedding settings, prompt content, P8, and P13 are required injected inputs or dependency gates—never defaults.

**Tech Stack:** Python 3.12, stdlib `sqlite3`, frozen dataclasses, P1 append-only provenance, P2 replay/stage outputs, P4 observation keys, P6 read surfaces, P7 classification/gate records, pytest, Graphify.

---

## Authority and current-state ledger

Read in this order before executing a task:

1. `planning/00-database-agent-product-design.md` — original mission and §4 behavior.
2. `planning/04-resolutions.md` — S2/G2, M7, M12, M15.
3. `planning/parts/P9-grouping/SPEC.md` — P9 contract.
4. `docs/superpowers/specs/2026-08-25-p8-p9-planning-design.md` — P8/P9 ownership and fail-closed rules.
5. `planning/30-p8-p9-connection-contract.md` — frozen cross-part names and ownership.
6. Live P1–P7 source — exact callable and record names outrank old construction plans.

No repository-root `CLAUDE.md` exists as of 2026-08-25. Do not substitute a `CLAUDE.md` from another checkout or from `.claude/worktrees/`.

| Prerequisite | Current evidence | Plan treatment |
|---|---|---|
| P1 identity, events, learning | Implemented in `src/database_agent/`; P9 event names are already reserved §8.2 names | Consume directly |
| P1 vector storage | `vector_arrays(subject_key PRIMARY KEY, array_bytes, producer_version)` overwrites with `ON CONFLICT DO UPDATE`; it lacks file version, scope, model id/version, dimension, created time, and supersession history | Task 1 adds a versioned P1 surface; P9 is forbidden from using the legacy overwrite API |
| P2 stage vocabulary/writer | Implemented; `retrieval`, `graph_construction`, and `grouping` already exist | Consume only in replay/shadow/adversarial runs; there is no live run kind |
| P3 corpus/exclusion/folder context | Implemented | Read selected scan/corpus inputs; excluded files never enter P9 |
| P4 observations | Implemented; `observation_key` is the durable citation handle | Every excerpt/support citation uses `observation_key`, never `observation_id` |
| P6 facts | Implemented read surfaces: `proposal_eligible`, `event_facts`, `session_facts`, `family_facts`, `active_allowlist_for`, `evidence_chain`; `proposal_eligible` includes `llm_supported`, `validated`, `direct`, and `user_confirmed` | P9 filters seeds/anchors to `direct` or `validated`; `user_confirmed` is deliberately not an automatic anchor and needs an explicit user seed; `llm_supported`, possible family rows, and session facts are retrieval-only |
| P6 domain content | Domain/catalogue work is incomplete and concurrently owned | Inject active schemas, compatibility rules, and per-domain signal evaluators; absent knowledge refuses the affected path |
| P7 classification/gate | Implemented mechanism; classifier/detector knowledge is incomplete | Require current classification before any dossier request; unclassified or missing policy fails closed |
| P8 group validator | Not implemented; public names are frozen by `planning/30-p8-p9-connection-contract.md` | Deterministic P9 tasks use content-free recorded fixtures; live Task 10 imports `run_call`, reference-only `DossierRequest`, `P8Verdict`, `Refusal`, `CallFailed`, `ValidationUnavailable`, and exact re-exported `NeedsConsent`; P8 alone constructs materialized `Dossier` |
| P13 review actions | Specification only; event registration and test fixtures exist, but no producer | Task 11 uses a test-only fixture and names the exact swap boundary; no source stub impersonates P13 |
| P10/P11 consumers | Not implemented | Publish fixtures and read APIs only; no tree, node, destination, or placement concept enters `src/grouping/` |

### Dependency gates

- **G-P1V:** Task 1 must be green before semantic retrieval is enabled. Until then, `embeddings_enabled=True` raises `VersionedVectorStoreRequired`; it never falls back to `put_embedding(subject_key, ...)`. Task 5 must also have an injected encoder configuration before P9 can produce a vector.
- **G-P8:** Tasks 2–9 and 11–13 can build deterministically against content-free recorded P8-shaped fixtures. Task 10's live adapter and the model-backed branch wait for P8's frozen public types and sole callable, `llm_harness.run_call`.
- **G-P13:** Task 11 builds the P9 receiver against `tests/p9/p13_fixtures.py`. Replacing the fixture import with P13's public record is a required integration test when P13 ships.
- **G-KNOWLEDGE:** Missing domain schema, document compatibility, per-domain signal evaluator, gazetteer/entity-role input, or numeric limit produces `ConfigurationRequired` or an explicit deferred/abstained record. It never selects a built-in value.
- **G-OPEN:** P9 SPEC open questions 5, 9, 10, and 12 remain open. The implementation stores no guessed cross-P11 edge enum, protected-record destination, tentative-discovery visibility policy, or member-role field.

### Required execution order

Execute Tasks 1–8, then **Task 9 before Task 10**. Task 10 is a hard dependency gate: it must not begin until Task 9's `record_context_review_pending` is green and P8's frozen public surface exists. Continue with Tasks 11–15 afterward. The physical placement of Task 10 beside its dossier predecessor is for seam readability and does not relax this gate.

## File structure

```text
src/database_agent/vector_versions.py       P1-owned append/supersede vector records
src/database_agent/db.py                    includes the additive P1 vector-version DDL
src/grouping/__init__.py                     narrow P9 public exports
src/grouping/vocabulary.py                   P9 closed vocabularies and named constants
src/grouping/schema.py                       P9-owned SQLite tables
src/grouping/records.py                      frozen Group/Membership/CandidateGroupDossier/Edge records
src/grouping/store.py                        append, supersede, history, current reads
src/grouping/config.py                       P1-ceiling adapter and injected OQ1/knowledge protocols
src/grouping/seeds.py                        four seed kinds from P6/user inputs
src/grouping/embeddings.py                   injected encoder → versioned P1 vector records
src/grouping/retrieval.py                    six bounded retrieval channels
src/grouping/graph.py                        typed edges, hub suppression, stop rules
src/grouping/dossier.py                      bounded reference-only group dossier assembly
src/grouping/p8_seam.py                      consumes P8 outcome; owns no validator vocabulary
src/grouping/acceptance.py                   per-plan acceptance and derived review reads
src/grouping/learning.py                     SR6 and scoped user-decision recording
src/grouping/stage_output.py                 P9→P2 replay envelope mapping
src/grouping/failure_points.py               append-only retrieval/interpretation/label failures
src/grouping/pipeline.py                     deterministic P9 orchestration
src/grouping/fixtures.py                     golden P9 fixtures for later parts

tests/p9/conftest.py                         real P1–P7 database fixture
tests/p9/p8_fixtures.py                      recorded P8 contract fixture, tests only
tests/p9/p13_fixtures.py                     P13 review_action fixture, tests only
tests/p9/test_p9_*.py                        focused TDD suites
tests/integration/test_p9_p8_group_seam.py   live P8 dependency gate and adapter
tests/integration/test_p9_p2_replay.py       replay-only stage outputs
tests/integration/test_p9_walking_skeleton.py deterministic P6→P9→later fixture path
```

No task edits `planning/domains/`, deferred catalogues, prompts, or `.superpowers/`.

### Evidence and review UX contract

This is a P9 requirement, not a later interface polish task. The implementation must
preserve the information needed for a trustworthy review surface:

- Every edge, seed, candidate member, omission, stop rule, and membership proposal
  carries typed evidence references (`observation_key` plus exact span/structure
  locator where applicable), source file/version identity, and the producing
  extractor/plan version.
- A candidate group exposes separate `direct_anchor`, `context_supported`, and
  `semantic_support` evidence. Semantic support can improve recall but can never be
  the sole reason for an accepted membership.
- Uncertainty is explicit: `unknown`, `ambiguous`, `conflicting`, `insufficient`,
  and `deferred` are distinct from rejection and from consent pending. No empty
  citation list is treated as support.
- Review records include a concise reason, strongest evidence channels, conflicts,
  affected files, and the safe next action. Detailed provenance is available on
  demand; the default payload does not dump raw file content.
- User actions are append-only and reversible at the P9 decision layer: accept,
  edit, reject, defer, restore/reconsider, and reset-suggestion operations retain
  their basis and scope. P9 does not delete or move source files.
- Bulk review is permitted only for equivalent low-risk proposals with visible
  counts and exceptions; context-supported or conflicting proposals remain
  individually reviewable.

These requirements keep P9 aligned with the original product design and with the
privacy/review boundary: P9 prepares explainable proposals, P8 validates model
interpretation, P7 controls release, and later parts own destination/placement.

---

### Task 1: Add P1's versioned vector record without breaking the legacy store

**Files:**
- Create: `src/database_agent/vector_versions.py`
- Modify: `src/database_agent/db.py`
- Test: `tests/test_vector_versions.py`
- Test: `tests/test_vectors.py`

**Produces:**

```python
@dataclass(frozen=True)
class EmbeddingRecord:
    embedding_id: str
    file_id: str
    content_hash: str
    scope: str
    embedding_model_id: str
    embedding_version: str
    dimension: int
    encoding: str
    array_bytes: bytes
    created_at: str
    supersedes: str | None
    superseded_by: str | None
    supersede_reason: str | None

def record_embedding(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                     scope: str, embedding_model_id: str,
                     embedding_version: str, dimension: int, encoding: str,
                     array_bytes: bytes,
                     created_at: str,
                     supersede_reason: str | None = None) -> str: ...

def current_embedding(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                      scope: str, embedding_model_id: str,
                      embedding_version: str) -> EmbeddingRecord | None: ...

def embedding_history(conn: sqlite3.Connection, *, file_id: str,
                      content_hash: str, scope: str) -> tuple[EmbeddingRecord, ...]: ...

class AmbiguousCurrentEmbedding(RuntimeError): ...
```

- [ ] **Step 1: Write failing history and metadata tests**

```python
def test_recompute_supersedes_without_overwriting(conn):
    first = record_embedding(
        conn, file_id="f1", content_hash="h1", scope="extracted_text",
        embedding_model_id="fixture-model", embedding_version="1",
        dimension=2, encoding="fixture-bytes", array_bytes=b"first",
        created_at="2026-08-25T00:00:00Z")
    second = record_embedding(
        conn, file_id="f1", content_hash="h1", scope="extracted_text",
        embedding_model_id="fixture-model", embedding_version="1",
        dimension=2, encoding="fixture-bytes", array_bytes=b"second",
        created_at="2026-08-25T00:01:00Z",
        supersede_reason="recomputed after extractor upgrade")
    rows = embedding_history(conn, file_id="f1", content_hash="h1",
                             scope="extracted_text")
    assert [row.array_bytes for row in rows] == [b"first", b"second"]
    assert rows[0].superseded_by == second
    assert current_embedding(
        conn, file_id="f1", content_hash="h1", scope="extracted_text",
        embedding_model_id="fixture-model", embedding_version="1").embedding_id == second
```

Also assert content hash, scope, model id/version, encoding, positive dimension, and created time are required; a new content hash never returns the prior vector; and the original `put_embedding`/`get_embedding` tests remain green.

Add concurrency/current-invariant tests:

```python
def test_exact_vector_identity_has_at_most_one_current_row(conn):
    record_embedding(conn, file_id="f1", content_hash="h1", scope="extracted_text",
                     embedding_model_id="m", embedding_version="1", dimension=2,
                     encoding="fixture-bytes", array_bytes=b"one", created_at=T0)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO vector_embeddings "
            "(embedding_id,file_id,content_hash,scope,embedding_model_id,"
            "embedding_version,dimension,encoding,array_bytes,created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            ("illegal-second-current", "f1", "h1", "extracted_text", "m", "1",
             2, "fixture-bytes", b"two", T1))

def test_ambiguous_legacy_current_state_is_rejected_before_write(conn):
    conn.execute("DROP INDEX one_current_vector_embedding")
    for embedding_id, payload in (("bad-1", b"one"), ("bad-2", b"two")):
        conn.execute(
            "INSERT INTO vector_embeddings "
            "(embedding_id,file_id,content_hash,scope,embedding_model_id,"
            "embedding_version,dimension,encoding,array_bytes,created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (embedding_id, "f1", "h1", "extracted_text", "m", "1", 2,
             "fixture-bytes", payload, T0))
    with pytest.raises(AmbiguousCurrentEmbedding):
        record_embedding(conn, file_id="f1", content_hash="h1", scope="extracted_text",
                         embedding_model_id="m", embedding_version="1", dimension=2,
                         encoding="fixture-bytes", array_bytes=b"three", created_at=T2,
                         supersede_reason="repair attempt")
```

The ambiguity test drops the guard index only inside its isolated temporary database to simulate a malformed pre-index store. Production code exposes no index-disabling helper.

- [ ] **Step 2: Run the tests and verify RED**

Run: `python3.12 -m pytest -q tests/test_vector_versions.py tests/test_vectors.py`

Expected: FAIL because `database_agent.vector_versions` does not exist.

- [ ] **Step 3: Add an additive table and append/supersede implementation**

Use a new `vector_embeddings` table. Do not mutate or reinterpret legacy `vector_arrays` rows because they lack the metadata required to do so safely. Add partial unique index `one_current_vector_embedding` over `(file_id, content_hash, scope, embedding_model_id, embedding_version) WHERE superseded_by IS NULL`.

`record_embedding` runs one immediate transaction that queries the exact current identity before inserting. Zero current rows inserts normally. One current row requires a non-empty `supersede_reason`; the function mints the successor id, marks that exact predecessor as superseded by the minted id, then inserts the successor before committing. If insertion fails, the transaction rolls back the predecessor update. More than one current row raises `AmbiguousCurrentEmbedding` before any write. The partial index is the final race guard: a second current row cannot commit. Vector bytes are never updated in place and the caller cannot choose an arbitrary predecessor.

P1 remains an opaque-byte store. It validates that `dimension > 0` and that model, version, scope, and encoding identifiers are non-empty, but it does **not** infer a codec or claim byte-length-to-dimension correctness. P9's injected encoder owns serialization correctness in Task 5. This preserves §0's P1 boundary without inventing a closed codec catalogue.

- [ ] **Step 4: Verify P1 and schema compatibility**

Run: `python3.12 -m pytest -q tests/test_vector_versions.py tests/test_vectors.py tests/test_db.py tests/test_supersede.py`

Expected: PASS; both vector tables remain outside `files` and `events`, and P1 still exposes no similarity query.

- [ ] **Step 5: Commit**

```bash
git add src/database_agent/vector_versions.py src/database_agent/db.py tests/test_vector_versions.py tests/test_vectors.py
git commit -m "feat(p1): add versioned embedding records"
```

### Task 2: Create P9 vocabularies, records, and schema

**Files:**
- Create: `src/grouping/__init__.py`
- Create: `src/grouping/vocabulary.py`
- Create: `src/grouping/records.py`
- Create: `src/grouping/schema.py`
- Create: `tests/p9/conftest.py`
- Create: `tests/p9/test_p9_schema.py`
- Create: `tests/p9/test_p9_vocabulary.py`

**Produces:** `create_grouping_schema(conn)`, frozen `Group`, `Membership`, `Support`, `TypedEdge`, `CandidateGroupDossier`, `StopRuleOutcome`, `FailurePoint`, `GroupAcceptance` records, and named constants for every closed P9 value.

- [ ] **Step 1: Write failing schema/record tests**

Assert:

```python
assert GROUP_STATES == (CANDIDATE, SUPPORTED, TENTATIVE_DISCOVERY, UNRESOLVED)
assert MEMBERSHIP_BASES == (DIRECT_ANCHOR, CONTEXT_SUPPORTED, USER_ATTACHED)
assert MEMBERSHIP_DECISIONS == (INCLUDED, EXCLUDED, UNCERTAIN)
assert "plan_version_id" not in {f.name for f in fields(Group)}
assert "plan_version_id" not in {f.name for f in fields(Membership)}
assert "review_state" not in {f.name for f in fields(Membership)}
assert "destination" not in repr(Group.__annotations__).lower()
```

Check the P9 tables are `groups`, `memberships`, `group_dossiers`, `group_edges`, `stop_rule_outcomes`, `group_failure_points`, and `group_acceptance`; only `group_acceptance` has `plan_version_id`.

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p9/test_p9_schema.py tests/p9/test_p9_vocabulary.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'grouping'`.

- [ ] **Step 3: Implement the frozen records and idempotent schema**

Use `file_id + content_hash` on every membership. Store list/map fields as canonical JSON. Store `display_label` and `group_category` as SQL NULL unless coherence is `coherent`. Give every supersedable table explicit `supersedes`, `superseded_by`, and `supersede_reason` columns.

The `Membership` type deliberately omits `review_state`. That line in the SPEC's displayed Membership shape conflicts with M15 and with the sentence beside it (“resolved AS OF a plan version … not stored here”). Task 9 publishes the derived accessor.

- [ ] **Step 4: Run and verify GREEN**

Run: `python3.12 -m pytest -q tests/p9/test_p9_schema.py tests/p9/test_p9_vocabulary.py`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/grouping tests/p9/conftest.py tests/p9/test_p9_schema.py tests/p9/test_p9_vocabulary.py
git commit -m "feat(p9): define grouping records and schema"
```

### Task 3: Publish golden dossiers and fixture-mediated neighbor contracts

**Files:**
- Create: `src/grouping/fixtures.py`
- Create: `tests/p9/p8_fixtures.py`
- Create: `tests/p9/p13_fixtures.py`
- Create: `tests/p9/test_p9_fixtures.py`

**Produces:** `course_dossier_fixture()`, `application_dossier_fixture()`, recorded P8 group verdict fixtures, and a test-only P13 `ReviewActionFixture`.

- [ ] **Step 1: Write failing conformance tests**

The course fixture contains direct anchors for `Lecture 08.pdf` and `Midterm Practice.pdf`; `HW 3.pdf` remains a candidate with context support. The application fixture contains direct Columbia evidence and a conflicting Duke essay. Every excerpt must resolve to a P4 observation seeded into the test database.

```python
assert {x.basis for x in course.anchor_files} == {DIRECT_ANCHOR}
assert [x.file_id for x in course.candidate_files] == ["hw-3"]
assert course.candidate_files[0].basis == CONTEXT_SUPPORTED
assert all(observations_by_key(conn, excerpt.observation_key)
           for excerpt in course.excerpts)
```

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p9/test_p9_fixtures.py`

Expected: FAIL because the fixture modules do not exist.

- [ ] **Step 3: Implement fixtures without runtime authorities**

`src/grouping/fixtures.py` publishes P9-owned records for P8/P10/P11 consumers. `tests/p9/p8_fixtures.py` and `tests/p9/p13_fixtures.py` remain under tests and must never be imported by `src/grouping/`. The P8 fixture mirrors SPEC fields (`outcome`, `reasons`, `may_propose`, `requires_review`, `citations_checked`) but owns no alternate verdict enum.

- [ ] **Step 4: Verify GREEN and fixture isolation**

Run: `python3.12 -m pytest -q tests/p9/test_p9_fixtures.py`

Expected: PASS, and an AST assertion proves `src/grouping` imports neither fixture module.

- [ ] **Step 5: Commit**

```bash
git add src/grouping/fixtures.py tests/p9/p8_fixtures.py tests/p9/p13_fixtures.py tests/p9/test_p9_fixtures.py
git commit -m "test(p9): publish grouping contract fixtures"
```

### Task 4: Derive only legal deterministic seeds

**Files:**
- Create: `src/grouping/config.py`
- Create: `src/grouping/seeds.py`
- Create: `tests/p9/test_p9_seeds.py`

**Produces:**

```python
class ConfigurationRequired(RuntimeError): ...

@dataclass(frozen=True)
class GroupingLimits:
    max_retrieved_neighbors: int
    max_graph_nodes: int
    max_candidate_members: int
    max_dossier_tokens: int
    generic_hub_frequency: int
    minimum_independent_anchors: int

def grouping_limits(conn: sqlite3.Connection, *, generic_hub_frequency: int,
                    minimum_independent_anchors: int) -> GroupingLimits: ...

def seeds_for_file(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                   user_seed_for: Callable[[str, str], UserSeed | None]) -> tuple[Seed, ...]: ...
```

- [ ] **Step 1: Write failing tests for all four seed kinds and negatives**

Prove strongly identified `direct`/`validated` facts, validated shared facts, duplicate/version families whose qualifying anchor row is direct/validated, P6 photo-event facts, and explicit user-created starts can seed. Prove `possible`, `llm_supported`, `user_confirmed` without an explicit user seed, bounded-session, rejected, filename-only, and semantic-neighbor inputs cannot seed. This deliberately keeps `user_confirmed` out of automatic anchoring: user intent enters through the explicit user-seed channel, not by silently widening the evidence bar.

Also test `grouping_limits`: it reads exactly `grouping.max_retrieved_neighbors`, `grouping.max_local_graph_neighborhood`, `grouping.max_candidate_cluster_size`, and `model.max_dossier_tokens_per_call` through `database_agent.budget.get_ceiling`. Any `None`, non-positive value, or missing injected OQ1 value (`generic_hub_frequency`, `minimum_independent_anchors`) raises `ConfigurationRequired`; P9 ships no numeric fallback.

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p9/test_p9_seeds.py`

Expected: FAIL because `grouping.seeds` does not exist.

- [ ] **Step 3: Implement only against P6 public reads**

Use `proposal_eligible`, `event_facts`, and `family_facts`. Apply P9's explicit `reliability in {direct, validated}` seed filter after the public reads: `proposal_eligible` is a candidate read surface, not the anchor authority. Filter family rows by the same bar before they seed; possible family/session facts may be retrieved later but never anchor. `llm_supported` remains P6 proposal-eligible and P9 retrieval-eligible, but never an anchor. A `user_confirmed` fact also does not automatically anchor; a caller must provide the explicit user-seed record. Do not query P6 tables directly and do not spell domain field names in P9.

Implement `grouping_limits` as a narrow adapter over P1 `get_ceiling`. Map the four live keys to the four structural limits; keep the two OQ1 values as mandatory injected arguments. Do not add a fifth ceiling key or default.

- [ ] **Step 4: Verify GREEN**

Run: `python3.12 -m pytest -q tests/p9/test_p9_seeds.py tests/p6/test_p6_read_surface.py`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/grouping/config.py src/grouping/seeds.py tests/p9/test_p9_seeds.py
git commit -m "feat(p9): derive evidence-backed group seeds"
```

### Task 5: Compute explicitly configured file-version embeddings

**Files:**
- Create: `src/grouping/embeddings.py`
- Create: `tests/p9/test_p9_embeddings.py`

**Consumes:** Task 1 `record_embedding`/`current_embedding`, P4/P5 stored extracted text selected by an injected scope reader, and a caller-supplied encoder.

**Produces:**

```python
@dataclass(frozen=True)
class EmbeddingConfig:
    model_id: str
    model_version: str
    scope: str
    encoding: str
    dimension: int

@dataclass(frozen=True)
class EncodedVector:
    array_bytes: bytes
    dimension: int
    encoding: str

Encoder = Callable[[str, EmbeddingConfig], EncodedVector]
EmbeddingTextFor = Callable[[sqlite3.Connection, str, str, str], str | None]

@dataclass(frozen=True)
class FileVersionRef:
    file_id: str
    content_hash: str

EligibleEmbeddingVersions = Callable[
    [sqlite3.Connection, Seed, int], Sequence[FileVersionRef]
]

@dataclass(frozen=True)
class EmbeddingsOff:
    enabled: Literal[False] = False

@dataclass(frozen=True)
class EmbeddingsOn:
    config: EmbeddingConfig
    encoder: Encoder
    embedding_text_for: EmbeddingTextFor
    eligible_versions_for: EligibleEmbeddingVersions
    enabled: Literal[True] = True

EmbeddingRuntime = EmbeddingsOff | EmbeddingsOn

def ensure_file_embedding(conn: sqlite3.Connection, *, file_id: str,
                          content_hash: str, config: EmbeddingConfig | None,
                          encoder: Encoder | None,
                          embedding_text_for: EmbeddingTextFor | None,
                          embeddings_enabled: bool, created_at: str) -> EmbeddingRecord | None: ...
```

- [ ] **Step 1: Write failing producer, invalidation, and off-mode tests**

```python
def test_embeddings_off_never_reads_text_calls_encoder_or_writes(conn):
    result = ensure_file_embedding(
        conn, file_id="f1", content_hash="h1", config=None, encoder=None,
        embedding_text_for=None, embeddings_enabled=False, created_at=T0)
    assert result is None
    assert conn.execute("SELECT count(*) FROM vector_embeddings").fetchone()[0] == 0

def test_content_version_change_never_reuses_the_prior_vector(conn, encoder, text_for):
    old = ensure_file_embedding(
        conn, file_id="f1", content_hash="h1", config=CONFIG, encoder=encoder,
        embedding_text_for=text_for, embeddings_enabled=True, created_at=T0)
    new = ensure_file_embedding(
        conn, file_id="f1", content_hash="h2", config=CONFIG, encoder=encoder,
        embedding_text_for=text_for, embeddings_enabled=True, created_at=T1)
    assert old.embedding_id != new.embedding_id
    assert old.content_hash == "h1" and new.content_hash == "h2"
    assert current_embedding(conn, file_id="f1", content_hash="h1", **IDENTITY) == old
    assert current_embedding(conn, file_id="f1", content_hash="h2", **IDENTITY) == new
```

Also prove enabled mode refuses missing config/encoder/text reader, an empty text scope records no vector and an explicit omission, configuration requires non-empty model/scope/version/encoding and positive dimension, and an encoder result whose dimension or encoding differs from configuration raises `EncoderContractViolation` before P1 writes. `EmbeddingsOn.__post_init__` rejects non-callable dependencies and invalid configuration, so an incomplete enabled runtime cannot reach retrieval.

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p9/test_p9_embeddings.py`

Expected: FAIL because `grouping.embeddings` does not exist.

- [ ] **Step 3: Implement the injected producer boundary**

When disabled, return before touching text, encoder, or P1. When enabled, require all three injected inputs. Select text only through `embedding_text_for(conn, file_id, content_hash, config.scope)`; P9 defines no default scope and does not concatenate the whole file implicitly. Call the encoder, verify its declared dimension/encoding exactly match `EmbeddingConfig`, then call P1 `record_embedding` with the complete file-version/model/scope identity.

If an exact current record already exists, return it without re-encoding. Re-encoding the exact identity is allowed only through an explicit recompute operation that supplies a supersede reason; P1 automatically finds and transactionally supersedes the exact predecessor. P9 never calls legacy `put_embedding`.

- [ ] **Step 4: Verify GREEN with P1 history tests**

Run: `python3.12 -m pytest -q tests/p9/test_p9_embeddings.py tests/test_vector_versions.py tests/test_vectors.py`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/grouping/embeddings.py tests/p9/test_p9_embeddings.py
git commit -m "feat(p9): compute configured file embeddings"
```

### Task 6: Retrieve a bounded neighborhood through six non-authoritative channels

**Files:**
- Create: `src/grouping/retrieval.py`
- Create: `tests/p9/test_p9_retrieval.py`
- Modify: `src/grouping/config.py`

**Consumes:** P3 corpus/folder context, P6 facts/sessions/families, Task 5 current embeddings, and injected `document_compatible(domain, left_type, right_type)` plus an injected similarity function.

- [ ] **Step 1: Write failing channel, bound, and fail-closed tests**

```python
with pytest.raises(ConfigurationRequired):
    retrieve_neighbors(conn, seed=seed, limits=None, knowledge=knowledge,
                       embeddings_enabled=False)

result = retrieve_neighbors(conn, seed=seed, limits=limits,
                            knowledge=knowledge, embeddings_enabled=False)
assert len(result.neighbors) <= limits.max_retrieved_neighbors
assert all(n.channel != MUTUAL_SEMANTIC_RETRIEVAL for n in result.neighbors)
```

Add one named test for each of the six channels: (1) shared P6 facts, (2) duplicate/version `family_facts`, including possible rows as retrieval-only, (3) injected `document_compatible`, (4) P3 related-folder context, (5) bounded `session_facts`, and (6) mutual semantic neighbours. Prove channels 2 and 5 never set an anchor flag merely because they retrieved a file. Also prove excluded P3 files never enter, one-way semantic similarity is insufficient, both directions are required, semantic results carry no anchor flag, and requesting semantic retrieval without a complete P1 vector identity `(scope, model_id, model_version)` plus an injected similarity function raises `ConfigurationRequired`. Encoder configuration is validated earlier by Task 5 and again at the pipeline boundary; retrieval never owns or calls an encoder.

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p9/test_p9_retrieval.py`

Expected: FAIL because `grouping.retrieval` does not exist.

- [ ] **Step 3: Implement deterministic ranking and explicit omissions**

Rank by injected channel weight, then stable `(content_hash, file_id)` tie-break. Numeric values come only from `GroupingLimits`; channel weights come only from an injected mapping. A missing compatibility predicate omits that channel and records `missing_document_compatibility`, rather than treating every document type as compatible. Semantic retrieval reads only `current_embedding` and never the legacy vector API.

- [ ] **Step 4: Verify GREEN and G-P1V**

Run: `python3.12 -m pytest -q tests/p9/test_p9_retrieval.py tests/test_vector_versions.py`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/grouping/config.py src/grouping/retrieval.py tests/p9/test_p9_retrieval.py
git commit -m "feat(p9): add bounded evidence retrieval"
```

### Task 7: Build typed edges, suppress hubs, and enforce the five pre-P8 stop rules

**Files:**
- Create: `src/grouping/graph.py`
- Create: `tests/p9/test_p9_graph.py`
- Create: `tests/p9/test_p9_stop_rules.py`

**Produces:** `build_graph(...) -> LocalEvidenceGraph`, `evaluate_stop_rules(...) -> StopRuleOutcome`.

- [ ] **Step 1: Write the pre-P8 stop-rule fixtures**

One test each for SR1–SR4 and SR6. SR2 must prove an embedding-only connected graph produces `no-group` even when the recorded P8 fixture says coherent. SR3's frequency comes from the required injected `GroupingLimits.generic_hub_frequency`; no email/domain heuristic is embedded in P9. SR4 receives an injected `conflicts_for(files)`. SR6 queries P1 `learning_records` using `proposal_class + basis_key` before surfacing. Assert these five can return before dossier construction and before `run_call`.

Add an explicit negative asserting SR5 is absent from the pre-model evaluator. SR5 means that P8 could not explain the group with valid citations; it can only be mapped after `run_call` returns a non-accepting P8 result.

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p9/test_p9_graph.py tests/p9/test_p9_stop_rules.py`

Expected: FAIL because `grouping.graph` does not exist.

- [ ] **Step 3: Implement stable edges and pre-model refusal**

Edges store their evidence reference and bridge entity separately. Apply `max_graph_nodes` by retaining direct anchors first, then highest-ranked evidence edges, then stable tie-breaks. A fired SR1–SR4 or SR6 returns before dossier construction. SR5 is evaluated only in Task 10 from P8's validated result. `tentative-discovery` is representable but not surfaced in v1 because open question 10 has no visibility policy; P10 must not render it until that policy is ratified.

- [ ] **Step 4: Verify GREEN**

Run: `python3.12 -m pytest -q tests/p9/test_p9_graph.py tests/p9/test_p9_stop_rules.py tests/test_learning.py`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/grouping/graph.py tests/p9/test_p9_graph.py tests/p9/test_p9_stop_rules.py
git commit -m "feat(p9): enforce bounded graph stop rules"
```

### Task 8: Assemble a bounded, reference-only, privacy-first dossier

**Files:**
- Create: `src/grouping/dossier.py`
- Create: `tests/p9/test_p9_dossier.py`

**Produces:**

```python
def assemble_group_dossier(conn: sqlite3.Connection, *, group: Group,
                           graph: LocalEvidenceGraph,
                           active_schema_for: ActiveSchemaFor,
                           signal_evaluator_for: SignalEvaluatorFor,
                           classification_store: ClassificationStore) -> CandidateGroupDossier: ...
```

- [ ] **Step 1: Write failing separation, citation, budget, and privacy tests**

Prove anchor and candidate arrays remain separate, excerpts are short observation-addressed references, no full file appears, all files have a current P7 classification before a `DossierRequest` can be built, and missing classification fails closed. The result is reference-only and contains no materialized P8 `Dossier`, `ModelCallRequest`, released span, prompt, token estimate, split, summarized replacement, or model client. `NeedsConsent` can arise only later from P8 `run_call`; dossier assembly does not construct or coerce it.

Add the SPEC Done-means 6 purpose-packet fixture: ID, transcript, resume, statement, certificate, and portal screenshot are purpose-coherent only when the packet carries direct application evidence. The same artefacts connected only by a tight download session produce no accepted purpose. Purpose evidence is a measurable reference set in `CandidateGroupDossier`, never an inferred label or prompt authored by P9.

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p9/test_p9_dossier.py`

Expected: FAIL because `grouping.dossier` does not exist.

- [ ] **Step 3: Implement reference-only content selection**

Select bounded references using the already bounded graph and candidate ceiling. Record every omitted reference and reason; never trim decisive anchors silently. `active_schema_for` and `signal_evaluator_for` are required; missing domain knowledge returns `ConfigurationRequired` and creates no label/category. P9 does not measure dossier tokens, summarize facts, preserve/drop excerpts by a token ladder, split a request, or create a budget-deferred decision. M9's summarize → preserve anchors → split/defer ladder belongs only to P8 `run_call`, using P1's `model.max_dossier_tokens_per_call` ceiling. If P8 later returns a budget-deferred result, P9 records `DossierDeferred` without rerunning the ladder.

`build_dossier_request` in Task 10 converts this P9 record into P8's reference-only `DossierRequest`. P8 alone materializes released evidence through P7 and constructs `Dossier`. `src/grouping/dossier.py` must not import `Dossier`, `privacy.gate`, `privacy.release.ModelCallRequest`, or any model transport.

- [ ] **Step 4: Verify GREEN with P7**

Run: `python3.12 -m pytest -q tests/p9/test_p9_dossier.py tests/p7/test_p7_release.py tests/p7/test_p7_transport.py`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/grouping/dossier.py tests/p9/test_p9_dossier.py
git commit -m "feat(p9): assemble privacy-safe group dossiers"
```

### Task 10: Consume the real P8 group verdict without creating a second validator

> **Dependency gate G-P8:** Begin this task only after Task 9 is green and P8 publishes the exact public surface frozen in `planning/30-p8-p9-connection-contract.md`. Recorded fixtures are insufficient for marking this task complete.

**Files:**
- Create: `src/grouping/p8_seam.py`
- Create: `src/grouping/store.py`
- Create: `tests/p9/test_p9_membership.py`
- Create: `tests/integration/test_p9_p8_group_seam.py`

**Produces:**

```python
def build_dossier_request(dossier: CandidateGroupDossier) -> DossierRequest: ...
def apply_p8_verdict(conn: sqlite3.Connection, *, group: Group,
                     dossier: CandidateGroupDossier,
                     result: P8Verdict | Refusal | NeedsConsent |
                             ValidationUnavailable | CallFailed,
                     plan_version_id: str) -> GroupDecision | NeedsConsent: ...
```

- [ ] **Step 1: Write failing mapping tests against the real P8 exports**

Import the exact frozen exports from `llm_harness`: `run_call`, `DossierRequest`, `P8Verdict`, `Refusal`, `CallFailed`, `ValidationUnavailable`, and re-exported `NeedsConsent`. Assert the adapter calls only `run_call` with the reference-only `DossierRequest`; `src/grouping/` imports neither materialized `Dossier`, `Gate.release`, nor a model client. Assert `accept_direct` writes an included direct-anchor membership; `accept_context_supported` writes an uncertain context-supported membership **and a current `group_acceptance` membership row for the supplied plan version with `acceptance = pending-review` and `review_state = pending-review` in the same transaction**; weak/reject/abstain/refusal/unavailable/call-failed outcomes cannot create a supported group. `CallFailed` records the interpretation-stage failure without membership or acceptance. `NeedsConsent` is the exact same object returned unchanged and writes no verdict, membership decision, acceptance row, failure point, or P2 stage row.

Test SR5 here, after P8: a P8 non-accept result whose reasons state that the group cannot be explained with valid citations maps to the SR5 no-group outcome. P9 does not inspect citations or reproduce P8 validation; it maps the authoritative result/reasons only. A P8 budget-deferred result maps to `DossierDeferred`; P9 does not run M9's ladder.

- [ ] **Step 2: Run and verify the dependency failure**

Run: `python3.12 -m pytest -q tests/integration/test_p9_p8_group_seam.py`

Expected before P8 ships: FAIL at import of the documented P8 public API. Do not replace it with a source stub.

- [ ] **Step 3: Implement only P9's disposition mapping**

Import only the frozen P8 public surface; use qualified `DossierRequest`, `P8Verdict`, and `CallFailed`, never a bare `Verdict`. P9 defines no `P8GroupResult`, `BuildModelCallRequest`, `EvaluateGroup`, result enum, citation checker, schema checker, contradiction checker, normalization authority, gate call, transport, or model call. `build_dossier_request` performs a reference-shape conversion only and never constructs P8's materialized `Dossier`. The pipeline's only evaluation dependency is `run_call` (or a thin injected spy with that exact signature in unit tests).

Before writing any membership, verify the P8 result's `may_propose` flag and outcome/basis invariant. For context-supported output, require `plan_version_id` and atomically write the shared membership plus Task 9's plan-versioned pending-review row; a membership must never become visible without the review obligation that makes it safe. Append the reserved `group membership proposal` event with `validation_verdict_ref` in its explanation/evidence payload.

- [ ] **Step 4: Verify G-P8 GREEN**

Run: `python3.12 -m pytest -q tests/p9/test_p9_membership.py tests/integration/test_p9_p8_group_seam.py`

Expected: PASS with the live P8 implementation and no model/network call in tests.

- [ ] **Step 5: Commit**

```bash
git add src/grouping/p8_seam.py src/grouping/store.py tests/p9/test_p9_membership.py tests/integration/test_p9_p8_group_seam.py
git commit -m "feat(p9): consume validated group verdicts"
```

### Task 9: Store acceptance per plan version and derive review state

**Files:**
- Create: `src/grouping/acceptance.py`
- Create: `tests/p9/test_p9_acceptance.py`

**Produces:**

```python
def record_acceptance(conn: sqlite3.Connection, record: GroupAcceptance) -> str: ...
def group_state_as_of(conn: sqlite3.Connection, *, group_id: str,
                      plan_version_id: str) -> str: ...
def membership_review_state_as_of(conn: sqlite3.Connection, *, membership_id: str,
                                  plan_version_id: str) -> str: ...

class AcceptanceStateAbsent(LookupError): ...
```

- [ ] **Step 1: Write failing M15 tests**

Store one shared group and membership, accept it in plan version 2, reject it in version 3, and assert there is still one group, one membership, one dossier, and one edge set. Assert `group_state_as_of` returns `accepted`/`rejected`; `membership_review_state_as_of` returns the per-version state.

Prove absence is not a state:

```python
with pytest.raises(AcceptanceStateAbsent):
    membership_review_state_as_of(
        conn, membership_id="membership-context", plan_version_id="plan-4")
```

Also cover the fallback required by the SPEC: if no plan-version acceptance row exists for a group, `group_state_as_of` returns only the shared lifecycle state (`candidate`, `supported`, `tentative-discovery`, or `unresolved`). It never returns `pending-review` or `deferred` as `Group.state`. A membership accessor has no such fallback and raises `AcceptanceStateAbsent`.

Then use the context-proposal helper consumed by Task 10 and assert it materializes the exact pending-review acceptance row for every plan version in which the proposal is introduced. Calling the accessor before that write must fail; it must never invent `pending-review` from `Membership.basis`.

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p9/test_p9_acceptance.py`

Expected: FAIL because `grouping.acceptance` does not exist.

- [ ] **Step 3: Implement append/supersede acceptance rows**

The current row is unique per `(plan_version_id, group_id, membership_id)` among unsuperseded rows. Revisions insert and supersede. Publish `record_context_review_pending(conn, *, plan_version_id, group_id, membership_id, created_at)`, used by Task 10 inside the membership-write transaction. `membership_review_state_as_of` reads a current row or raises `AcceptanceStateAbsent`; it performs no basis-derived fallback. `group_state_as_of` returns a current accepted/rejected plan decision when present and otherwise returns the stored shared lifecycle state. `pending-review` and `deferred` do not become shared group lifecycle states. User-edited labels live only here; `Group.display_label` retains the engine/model proposal.

- [ ] **Step 4: Verify GREEN**

Run: `python3.12 -m pytest -q tests/p9/test_p9_acceptance.py tests/p9/test_p9_schema.py`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/grouping/acceptance.py tests/p9/test_p9_acceptance.py
git commit -m "feat(p9): version group acceptance state"
```

### Task 11: Receive P13 group actions through a fixture-only back-edge

**Files:**
- Create: `src/grouping/learning.py`
- Create: `tests/p9/test_p9_learning.py`
- Modify: `tests/p9/p13_fixtures.py`

**Produces:** `apply_review_action(conn, action) -> tuple[str, ...]` over a structural action protocol matching P13's published fields.

- [ ] **Step 1: Write failing action-routing tests**

Cover accept, reject, rename, merge, split, exclude-one-member, and manual attach. Require `surface == "group_plan"`, explicit `plan_version`, `correction_scope`, `presented_state_ref`, and `user_id`. A missing scope raises; P9 never infers `corpus`. Bulk actions enumerate exact members.

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p9/test_p9_learning.py`

Expected: FAIL because `grouping.learning` does not exist.

- [ ] **Step 3: Implement decisions, provenance, and SR6 learning records**

Append `user group decision` with P9 as subsystem, the explicit user id, correction scope/subject, polarity, proposal class, and basis key. Apply plan-version state through Task 9. Manual attachment is the only path that may write `USER_ATTACHED` for unreadable files, and it infers no purpose.

The runtime function accepts a protocol-shaped value and imports no test fixture. When P13 ships, replace only the test factory with P13's public `ReviewAction`; keep this receiver and add an exact field/signature conformance test.

- [ ] **Step 4: Verify GREEN and back-edge isolation**

Run: `python3.12 -m pytest -q tests/p9/test_p9_learning.py tests/test_learning.py tests/test_events.py`

Expected: PASS; no `src/grouping` import references P13 or `tests.p9.p13_fixtures`.

- [ ] **Step 5: Commit**

```bash
git add src/grouping/learning.py tests/p9/test_p9_learning.py tests/p9/p13_fixtures.py
git commit -m "feat(p9): record reviewed group decisions"
```

### Task 12: Map P9 records into P2 replay stage outputs

**Files:**
- Create: `src/grouping/stage_output.py`
- Create: `src/grouping/failure_points.py`
- Create: `tests/integration/test_p9_p2_replay.py`
- Create: `tests/p9/test_p9_failure_points.py`

**Produces:** `emit_retrieval_stage`, `emit_graph_stage`, `emit_grouping_stage` adapters over P2 `record_stage_output`, plus `record_failure_point(...)` for the append-only P9 failure log.

- [ ] **Step 1: Write failing mapping tests**

Pin exactly:

```python
assert map_result(RECORD_WRITTEN) == ("produced", "within_ceiling")
assert map_result(EVIDENCE_REFUSAL) == ("abstained", "within_ceiling")
assert map_result(BUDGET_DEFERRED) == ("deferred", "ceiling_reached")
```

Assert P9 emits only `retrieval`, `graph_construction`, and `grouping`; P8 alone emits `llm_interpretation`. `NeedsConsent` produces no stage output. Stage payload is opaque canonical JSON, and inputs use stable subject refs.

Add the SPEC Done-means 8 three-stage test. Cause the same candidate to fail independently at retrieval, interpretation, and label/disposition, and assert three append-only `FailurePoint` rows with distinct `stage` values and stable subject/evidence references. They must not collapse into one error class. Interpretation failure records a reference to P8's result/failure identity; P9 does not emit the P2 `llm_interpretation` stage.

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/integration/test_p9_p2_replay.py`

Expected: FAIL because `grouping.stage_output` and `grouping.failure_points` do not exist.

- [ ] **Step 3: Implement replay-only adapters**

Require an existing P2 run id. Do not add a `live` run kind and do not emit from ordinary ingestion. Retrieval supplies dimension `retrieval`, graph construction supplies `graph`, and grouping supplies `grouping` only where the P2 contract permits that measurement.

Implement `record_failure_point` as an append-only writer over the Task 2 `group_failure_points` table. Require a closed stage from `(retrieval, interpretation, label)`, a stable subject reference, reason code, evidence/result reference where the stage has one, and created time. Never update a failure row in place. Consent is not a failure point.

- [ ] **Step 4: Verify GREEN with P2**

Run: `python3.12 -m pytest -q tests/integration/test_p9_p2_replay.py tests/p9/test_p9_failure_points.py tests/eval/test_stage_output.py tests/eval/test_vocabulary.py`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/grouping/stage_output.py src/grouping/failure_points.py tests/integration/test_p9_p2_replay.py tests/p9/test_p9_failure_points.py
git commit -m "feat(p9): emit grouping replay stages"
```

### Task 13: Assemble the deterministic pipeline and walking skeleton

**Files:**
- Create: `src/grouping/pipeline.py`
- Create: `tests/integration/test_p9_walking_skeleton.py`
- Create: `tests/integration/test_p9_embedding_pipeline.py`
- Create: `tests/p9/test_p9_pipeline.py`

**Produces:**

```python
def group_subject(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                  plan_version_id: str, limits: GroupingLimits,
                  knowledge: GroupingKnowledge,
                  user_seed_for: UserSeedFor,
                  p8_run_call: Callable[..., P8Verdict | Refusal | NeedsConsent |
                                          ValidationUnavailable | CallFailed] | None,
                  embeddings: EmbeddingRuntime) -> GroupingResult: ...
```

- [ ] **Step 1: Write the failing deterministic skeleton**

With no model, cloud, or embeddings, call `group_subject(..., embeddings=EmbeddingsOff())`, seed one P6 direct fact, and form a group of one with a direct-anchor membership. Publish it through `src/grouping/fixtures.py` so P10 can freeze from it and P11 can later match against it. Assert no destination/tree/placement field exists anywhere in the result.

- [ ] **Step 2: Add adversarial pipeline tests**

Prove semantic-only connectivity cannot establish a group; a different-term course conflict refuses; a university name without a role-qualified target does not create a group; unreadable files require manual attach; multi-membership is allowed; a budget ceiling leaves anchors in a candidate group with no coherence or label; and rerunning with identical evidence produces stable fingerprints without overwriting history.

- [ ] **Step 3: Add failing live embedding-path integration tests**

Use spies plus real Task 1 storage:

```python
result = group_subject(
    conn, file_id=anchor.file_id, content_hash=anchor.content_hash,
    plan_version_id="plan-1", limits=limits, knowledge=knowledge,
    user_seed_for=no_user_seed, p8_run_call=recorded_run_call,
    embeddings=EmbeddingsOn(
        config=CONFIG, encoder=spy_encoder,
        embedding_text_for=bounded_text_for,
        eligible_versions_for=eligible_versions_for))

assert encoder_calls == [anchor.version_ref, sparse.version_ref]
assert current_embedding(conn, file_id=anchor.file_id,
                         content_hash=anchor.content_hash, **IDENTITY)
assert current_embedding(conn, file_id=sparse.file_id,
                         content_hash=sparse.content_hash, **IDENTITY)
assert result.graph.has_edge(anchor.file_id, sparse.file_id,
                             MUTUAL_SEMANTIC_RETRIEVAL)
```

The similarity fixture must require both directions, proving the path is encoder → versioned P1 records → P1 reads → mutual semantic retrieval, not a direct encoder-result shortcut.

Add two negatives:

```python
group_subject(..., embeddings=EmbeddingsOff())
assert text_calls == encoder_calls == []
assert conn.execute("SELECT count(*) FROM vector_embeddings").fetchone()[0] == 0

with pytest.raises(ConfigurationRequired):
    group_subject(..., embeddings=malformed_enabled_runtime)
assert retrieval_calls == []
```

Construct `malformed_enabled_runtime` with `object.__new__(EmbeddingsOn)` only inside the test to prove the pipeline revalidates the boundary even if a deserializer bypassed `__post_init__`; production code exposes no partial constructor.

Also return more than `limits.max_graph_nodes` entries from `eligible_versions_for` and assert only a bounded set is read/encoded. The seed consumes one slot; at most `max(0, limits.max_graph_nodes - 1)` additional eligible versions survive. Excluded P3 versions and duplicate references are removed before applying the stable `(content_hash, file_id)` order and cap. P9 never eagerly embeds the corpus.

- [ ] **Step 4: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p9/test_p9_pipeline.py tests/integration/test_p9_walking_skeleton.py tests/integration/test_p9_embedding_pipeline.py`

Expected: FAIL because `grouping.pipeline` does not exist.

- [ ] **Step 5: Implement the five-stage P9 sequence**

Sequence: seeds → prepare embeddings for the bounded eligible set → bounded retrieval from P1 → graph/pre-P8 stop rules → reference-only dossier → P8 `run_call` when eligible → SR5/result mapping → validated disposition/acceptance.

After deterministic seeds exist and immediately before retrieval, pattern-match `EmbeddingRuntime`. `EmbeddingsOff` bypasses candidate enumeration, text reads, encoding, and vector writes. `EmbeddingsOn` is revalidated, calls `eligible_versions_for(conn, seed, limits.max_graph_nodes)`, removes excluded/duplicate versions, reserves one graph slot for the seed, applies a stable `(content_hash, file_id)` order, retains at most `max(0, limits.max_graph_nodes - 1)` additional versions, calls `ensure_file_embedding` for that bounded set and the seed, and then invokes retrieval. Retrieval receives no encoder outputs; it reads current versioned records back from P1. Any incomplete/invalid enabled runtime raises `ConfigurationRequired` before candidate enumeration or retrieval.

If `p8_run_call is None`, only the deterministic group-of-one direct-anchor skeleton may complete; any judgement-requiring candidate remains `candidate` with an explicit `not_implemented`/deferred reason. The callable is a unit-test injection point with the exact frozen `llm_harness.run_call` contract, not a new `EvaluateGroup` protocol or authority. Production composition passes `llm_harness.run_call`. P9 never calls `Gate.release`, a transport, or a model client and never synthesizes a coherent verdict.

- [ ] **Step 6: Verify GREEN**

Run: `python3.12 -m pytest -q tests/p9/test_p9_pipeline.py tests/integration/test_p9_walking_skeleton.py tests/integration/test_p9_embedding_pipeline.py`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/grouping/pipeline.py tests/p9/test_p9_pipeline.py tests/integration/test_p9_walking_skeleton.py tests/integration/test_p9_embedding_pipeline.py
git commit -m "feat(p9): assemble bounded grouping pipeline"
```

### Task 14: Enforce no-invention, connection, and mission guards

**Files:**
- Create: `tests/p9/test_p9_no_invention.py`
- Create: `tests/p9/test_p9_connections.py`

- [ ] **Step 1: Add AST and schema guards**

Assert `src/grouping/` contains no prompt text, domain names, fixed numeric thresholds, gazetteer entries, identifier detection rules, document compatibility table, folder/path/destination/node schema, legacy vector API use, P8 validator logic, materialized `llm_harness.Dossier` import/construction, `P8GroupResult`, `BuildModelCallRequest`, `EvaluateGroup`, `Gate.release`, model-client/transport calls, or test-fixture imports. Permit the frozen reference-only `DossierRequest` import only in `grouping/p8_seam.py`; permit P9's closed vocabularies only in `grouping/vocabulary.py`.

- [ ] **Step 2: Add seam guards**

Assert P6 reads are through public surfaces and the direct/validated seed filter is visible; P7 classification is checked before every P8 dossier request; `llm_harness.run_call` is the only evaluation seam; P9 never materializes evidence or calls the privacy gate; P2 stage ids are exact; P13 remains fixture-mediated; P10/P11 consume fixture records without imports back into P9; embeddings can create only semantic support/edges and never anchors.

Add north-star UX assertions: every surfaced proposal has at least one typed
non-semantic evidence reference or is explicitly marked semantic-only/candidate;
direct, context-supported, semantic-support, conflict, abstention, consent-pending,
and deferred states remain distinguishable; review records expose reason, uncertainty,
source identity, and reversible user-action scope; and no P9 record contains a
destination, destructive action, or irreversible side effect.

- [ ] **Step 3: Run focused verification**

Run:

```bash
python3.12 -m pytest -q tests/p9 tests/integration/test_p9_p8_group_seam.py tests/integration/test_p9_p2_replay.py tests/integration/test_p9_walking_skeleton.py tests/integration/test_p9_embedding_pipeline.py
```

Expected: PASS after G-P8 is satisfied. Before P8 ships, the P8 integration test must remain an explicit dependency failure, not be skipped or replaced by a source stub.

- [ ] **Step 4: Commit**

```bash
git add tests/p9/test_p9_no_invention.py tests/p9/test_p9_connections.py
git commit -m "test(p9): enforce grouping architecture boundaries"
```

### Task 15: Final verification and connection review

**Files:**
- Modify only if verification finds a P9-owned defect: files introduced by Tasks 1–14

- [ ] **Step 1: Run compilation and the complete suite**

```bash
python3.12 -m compileall -q src tests
python3.12 -m pytest -q
```

Expected after **G-P8 is satisfied**: exit 0 and zero test failures. While G-P8 remains open, run:

```bash
python3.12 -m pytest -q --ignore=tests/integration/test_p9_p8_group_seam.py
python3.12 -m pytest -q tests/integration/test_p9_p8_group_seam.py
```

The first command must be green. The second must fail at its documented missing P8 import. Do not mark the milestone green, skip the dependency silently, or replace P8 with a source stub. Run native macOS reader tests outside a restricted sandbox if Vision access is denied.

- [ ] **Step 2: Refresh and diagnose Graphify**

```bash
graphify update .
graphify diagnose multigraph --json --max-examples 20
```

Expected after G-P8: the fresh **runtime** graph contains P6→P9, P7→P9, P8→P9, and P9→P1/P2. Before G-P8, P8→P9 exists only as a test-fixture/type-conformance seam and must not be reported as live.

P10/P11 are unbuilt. Their current P9 connections are deliberately **fixture publication paths** from `src/grouping/fixtures.py` into future consumer tests/spec conformance, not runtime imports and not proof that P10/P11 consume P9 today. When each later part ships, replace its fixture consumer with that part's public import/read path and require Graphify to show a live P9→P10 or P9→P11 edge. In all states, no P9 runtime import points to test fixtures, prompts, domains, P10, P11, or P13.

- [ ] **Step 3: Inspect diffs and working-tree ownership**

```bash
git diff --check
git status --short
```

Expected: no whitespace errors. Preserve unrelated concurrent changes, especially `planning/domains/`, deferred catalogues, prompts, `.superpowers/`, and P1–P7 audit/assembly work.

- [ ] **Step 4: Re-read the original mission and audit every P9 outcome**

Confirm with test names and database rows that:

- the graph supplies context but never writes a fact;
- embeddings retrieve but never establish;
- direct and context-supported membership remain distinguishable;
- privacy is applied before any model egress;
- abstention, consent pending, budget deferral, validation rejection, and stage failure remain distinct;
- no accepted/rejected state is duplicated into shared `Group` or `Membership` rows;
- no unfinished knowledge source gained an implementation default.

Only after all checks pass may P9 be described as complete. If G-P8 or G-P13 is still open, report the corresponding integration as dependency-blocked while retaining the green deterministic core.

---

## Requirement coverage map

| P9 requirement | Tasks |
|---|---|
| Four seed kinds; direct/validated automatic anchor bar; explicit user seed; llm-supported/family/session retrieval-only | 4 |
| Explicit embedding production, metadata, content-version invalidation, and live pipeline wiring | 1, 5, 13 |
| Six individually tested retrieval channels; bounded ranking; embeddings boundary | 1, 5, 6 |
| Typed local graph; hub suppression; SR1–SR4/SR6 before P8 and SR5 after P8 | 7, 10 |
| Course/application golden dossiers; direct/context separation; Done-means 6 purpose packet | 3, 8 |
| Four constrained group judgments through frozen P8 `run_call` | 10 |
| Group and membership shared evidence, append/supersede | 2, 10 |
| Per-plan acceptance, lifecycle fallback, and materialized review state | 9 |
| P13 user actions and §8.7 suppression | 11 |
| P2 retrieval/graph/grouping attribution; Done-means 8 three-stage failure log | 2, 12 |
| Deterministic walking skeleton, multi-membership, degradation | 13 |
| Evidence provenance, explicit uncertainty, explainable/reversible review proposals | 2, 9, 10, 12, 14 |
| No invention and original mission fidelity | 14, 15 |

## Explicitly unresolved after this plan

- Numeric thresholds and channel weights require P2 measurement; the plan defines required injection points, not values.
- Domain schemas, signal sets, document compatibility, gazetteers, and detector knowledge remain externally authored and incomplete.
- Embedding model, scope, version, encoding, and dimension require explicit configuration before semantic retrieval.
- P8 must publish the frozen live group evaluation surface before Task 10 can pass.
- P13 must publish `ReviewAction` before the fixture-mediated back-edge becomes a live typed import.
- P9/P11 edge vocabulary alignment, protected-record surfacing, tentative-discovery visibility, and intra-packet member roles remain the SPEC's open questions 5, 9, 10, and 12.

These are dependency gates, not invitations to invent defaults.

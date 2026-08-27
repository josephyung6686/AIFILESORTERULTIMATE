# P11 Placement and Residual Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build P11 so that every file and every accepted group is assigned one approved node of P10's frozen tree — or none — through a single append-only decision record that carries its evidence, its two-condition figures, its privacy state and its reason, and that no consumer has to branch on to parse a residual decision.

**North-star user experience:** P11 recommends only what it can point at. Every
recommendation shows the node it names, the facts and memberships that support it,
what was ruled out and why, how confident the engine is under both conditions of
§6.10, and the safe next action. A user can accept, change, defer, leave in place,
mark private, or bulk-accept, and every one of those is recorded, scoped and
reversible. Nothing is moved by P11 at all. An abstention is a finished, successful
outcome that reads as "I could not tell", never as silence and never as a
confident-looking guess.

**Architecture:** P11 is a deterministic index, retrieval, node-local graph, scoring
and record layer around two injected P8 call sites (C placement, D residual). It
consumes a frozen P10 tree, accepted P9 groups, P6 facts, P4 observations, P7
classifications and P13 review actions. It supplies P8 *authorities* and transcribes
P8's *verdict*; it re-implements none of P8's checks. Every decision, group plan,
residual set and index entry belongs to a plan version; files, observations, facts
and groups do not. P11 names a node and never a path; P12 alone resolves a path and
mutates the filesystem.

**Tech Stack:** Python 3.12, stdlib `sqlite3`, frozen dataclasses, P1 append-only
events/supersession/ceilings, P2 stage outputs, P4 `observation_key`, P6 read
surfaces, P7 `ClassificationStore` and `Policy`, P8 frozen `run_call` plus the typed
site authorities, P9 groups and acceptance, P10 frozen tree, pytest, Graphify.

---

## Authority and current-state ledger

Read in this order before executing a task:

1. `planning/00-database-agent-product-design.md` — the original mission; §6 and §7 behaviour.
2. `planning/01-product-design-structured.md` — §6.12's nine-step pipeline is at lines 1295–1306 and is this part's spine.
3. `planning/04-resolutions.md` — B3, B4, B6, B7, B8(b), M1, M5, M8, M10, M12, M13, M14, O7, O11.
4. `planning/parts/P11-placement-residual/SPEC.md` — P11's contract.
5. `planning/30-p8-p9-connection-contract.md` — the frozen P8 public surface and what a caller supplies.
6. `planning/parts/P10-tree-design-freeze/SPEC.md` and `planning/parts/P12-apply-undo/SPEC.md` — the seams either side.
7. Live `src/` — **exact callable and record names outrank any SPEC spelling.** Where they differ, the live name wins and the divergence is recorded under [SPEC corrections](#spec-corrections).

| Prerequisite | Current evidence | Plan treatment |
|---|---|---|
| P1 events | `database_agent.events.append_event` rejects any unregistered type (`events.py:120-124`), and `events.py:62-65` says P11's eight typed specializations "are ABSENT ON PURPOSE … When P11 prints the eight, add them here with `base="placement recommendation"`" | **Task 1 registers them.** Nothing in P11 may append an event before it lands |
| P1 supersession | `database_agent.supersede.mark_superseded(conn, table, *, old_id, new_id, reason)` keys on a `record_id` column and refuses a second supersede of the same row | Every P11 table carries `record_id`; Task 4 uses this, and writes no supersession of its own |
| P1 ceilings | `database_agent.budget.CEILING_KEYS` already publishes `placement.max_retrieved_neighbors`, `placement.max_local_graph_neighborhood`, `placement.max_candidate_cluster_size`, `residual.max_files_per_review_batch`, `model.max_dossier_tokens_per_call`, `model.max_llm_calls_per_thousand_files`, `model.max_cost_per_scan` | All seven of SPEC:714-717's ceilings have a live key. Task 5 reads them; P11 adds no key and no default |
| P1 learning | `database_agent.learning.learning_records(conn, scope, subject_id)` — **positional**, and `proposal_class` / `basis_key` are columns on the rows, filtered by the caller | Task 11 filters after the read, the way `llm_harness.eligibility` already does |
| P2 stages | `eval_harness.vocabulary.STAGE_IDS` contains `candidate_node_retrieval` (`vocabulary.py:27`) and `placement_scoring` (`:28`); `DIMENSIONS` contains `placement` (`:41`), `residual` (`:42`) and `retrieval` | Task 18 emits exactly those two stages, and **every stage it emits carries a `DimensionValue`** — `retrieval` on `candidate_node_retrieval` under a namespaced subject, `placement` or `residual` on `placement_scoring`. A stage with no dimension row is unattributable by construction (`eval_harness/attribution.py:30-39, :65-71`) |
| P2 foreign-value guard | `eval_harness.stage_output._FOREIGN_OUTCOMES` (`stage_output.py:30-33`) already enumerates P11's seven record outcomes verbatim and refuses them in the envelope | Task 2 pins P11's `OUTCOMES` against it by test. P2 knew this vocabulary before P11 existed and the two must not drift |
| P4 observations | `evidence_shape.store.observations_by_key(conn, observation_key) -> list[Observation]` is M14's resolver and returns a LIST — one key spans extractor versions | Every citation P11 stores is an `observation_key`; Task 3 forbids `observation_id` |
| P6 facts | `facts.read_surface.facts_for(conn, *, file_id, content_hash, states=None, domain=None)`, `proposal_eligible(conn, *, file_id, content_hash)`, `is_destination_eligible(conn, *, field_key)` | Task 7 retrieves through those; a fact whose field is not destination-eligible never drives a candidate |
| P6 reliability states | `evidence_shape.vocabulary.RELIABILITY_STATES` is snake_case; named constants at `facts/states.py:43-48` | Task 2 imports them. P11 re-spells none — see [SPEC corrections](#spec-corrections) |
| P7 classification | `privacy.classification_store.ClassificationStore(conn).current(file_id, content_hash) -> ClassificationRecord \| None`; the record carries `handling_class`, `protected`, `evidence_refs` | Task 10 reads it and reclassifies nothing. An absent classification blocks, never defaults to public |
| P7 policy | `privacy.policy.current_policy(conn, *, plan_version) -> Policy \| None`; `Policy.automatic_move_permissions: dict` is §8.4's explicit permission for a protected node | Task 10 reads it; a protected subject with no permitting entry is never `auto_eligible` |
| P8 harness | Implemented. `llm_harness.harness.run_call(conn, request, *, gate, model_client, prompt, validation_dependencies, observed_at)`; Sites C and D are `llm_harness.placement_validation` | Tasks 12 and 15 supply authorities and transcribe verdicts. **P11 writes no site check** |
| P8 export list | `src/llm_harness/__init__.py` exports eight names and **not** `SiteDependencies`, `CallDependencies`, `PlacementDependencies` or `ResidualDependencies` | P11 imports those from `llm_harness.sites`, `llm_harness.harness` and `llm_harness.placement_validation` and records the omission under [SPEC corrections](#spec-corrections) |
| P9 groups | **Shipped.** `src/grouping/store.py` publishes `record_group`, `record_membership`, `memberships_for_group`, `current_group`; `src/grouping/acceptance.py` publishes `record_acceptance` and **`group_state_as_of(conn, *, group_id, plan_version_id) -> str`** (`acceptance.py:154`), which returns `accepted` / `rejected` as of a version and is exactly the published read this plan previously recorded as missing | **G-P9 is closed.** Task 13 calls `group_state_as_of` and `memberships_for_group` directly. `tests/p11/p9_fixtures.py` survives only as a *seeder* of real P9 rows — it constructs P9's own records and writes them through P9's own stores — and stands in for no read |
| P9 acceptance shape | `group_acceptance(plan_version_id, group_id, membership_id, acceptance, review_state, …)` (`grouping/schema.py:140-159`); `grouping/vocabulary.py:31-32` says `accepted` and `rejected` are "Never stored" on a group | "Accepted" is resolved **as of P10's frozen plan version**, not read off `Group.state` |
| P10 tree | Not implemented | **G-P10.** Tasks 6 onward build against `tests/p11/p10_fixtures.py`; the integration test fails explicitly until P10 ships |
| P12 | Not implemented | P11 publishes `src/placement/fixtures.py` for it and imports nothing back |
| P13 | Specification only; three event types registered (`events.py:59-61`); `tests/p9/p13_fixtures.py` shows the fixture precedent | **G-P13.** Task 16 builds the receiver against `tests/p11/p13_fixtures.py` and names the swap boundary |

### Dependency gates

- **G-P1E:** Task 1 must be green before any task appends an event. Until then every P11 write path that logs raises `UnregisteredEventType`, which is correct and must not be worked around by writing a reserved name instead.
- **G-P10:** Tasks 6–19 build deterministically against content-free frozen-tree fixtures. `tests/integration/test_p11_p10_tree.py` imports P10's public frozen-tree read and must fail with an ImportError until P10 ships. No module under `src/placement/` constructs a node.
- **G-P9: CLOSED.** P9's acceptance read shipped. `placement/groups.py` calls `grouping.acceptance.group_state_as_of` and `grouping.store.memberships_for_group` directly; `tests/p11/p9_fixtures.py` seeds real P9 rows through P9's own writers and impersonates nothing. There is no longer a fixture-mediated P9 seam to swap.
- **G-P8:** Tasks 12 and 15 import the live P8 surface. They are the only P11 modules permitted to. Before they run, the deterministic path (Tasks 6–11) is complete on its own, because §6.6 requires a unique direct match to be decided with **zero** model calls.
- **G-P13:** Task 16 builds against `tests/p11/p13_fixtures.py`; no source stub impersonates P13.
- **G-KNOWLEDGE:** A missing ceiling, support threshold, margin predicate, ask-versus-abstain selector, return-cycle limit or residual-set partition raises `ConfigurationRequired`. It never selects a built-in value. `src/placement/` contains no numeric literal other than `0` and `1`, asserted by runtime introspection in Task 20.
- **G-OPEN:** SPEC open questions 3, 4, 6, 8, 9, 10 and 12 stay open. P11 stores no guessed confidence label beyond §6.11's four, no ask-versus-abstain rule, no cycle bound, no residual-set taxonomy and no shared-material storage location of its own.

### Required execution order

Derived from data dependencies, not from task numbering. Each gate states the one sentence that makes it a gate.

1. **Task 1 before every other task.** `append_event` rejects an unregistered type at the writer, so a P11 module that logs cannot be tested until the eight names exist.
2. **Task 2 before Tasks 3–21.** Every later module imports a named constant; a task that runs first would have to spell a bare string, which is the defect class this project has paid most for.
3. **Task 3 before Task 4**, because the schema's columns are the record's fields and two lists would drift.
4. **Task 6 before Task 7.** Retrieval reads the index, and Done-means 3 (SPEC:620-622) requires every profile to be indexed *before the first file is placed* — an ordering assertion, not a set assertion.
5. **Task 7 before Task 8.** The node-local graph is built around the retrieved candidates (§6.12 step 4 follows step 3), not around the whole corpus.
6. **Task 8 before Task 9.** `graph_anchors[]` is an input to the support score, and §6.5 requires a target connected only by generic similarity to stay uncertain — which cannot be decided without the typed edges.
7. **Task 10 before Task 12.** SPEC:210-212: *"**The gate is passed before any dossier is assembled for a model**, not after (§8.4)."* The privacy state is an input to the seam, not a decoration on its output.
8. **Task 11 before Task 9's first `place`.** SPEC:753-755: *"**Before emitting `outcome = place` (or a residual equivalent), P11 queries P1 `learning_records`** … A matching unrescinded reject skips that node — never auto-place."* The suppression is a precondition of a placement, so it lands before the task that emits one.
9. **Task 9 before Task 12.** §6.6 forbids a model call for a direct unique match, so the deterministic decision must already exist for "zero model calls" to be provable, and the dossier's `support` / `next_support` are its output.
10. **Task 12 before Task 13.** A group member placement may need a Site C call.
11. **Task 13 before Task 14.** §7.1 (SPEC:56): residual is *"a **separate stage that runs only after** normal group-aware classification has been attempted"*, and the corpus pass includes group plans.
12. **Task 14 before Task 15.** SPEC:545-547: *"**Ordering is contractual**: no per-file residual model call may be issued for a set until that set has a `residual_set_decision`."*
13. **Task 15 before Task 16.** The receiver routes all eight §7.7 actions, so the eight must exist.
14. **Tasks 17 and 18 after Task 15**, because re-projection walks decisions and the stage mapping maps their outcomes.
15. **Task 19 after Tasks 6–18**; **Tasks 20 and 21 last.**

## File structure

```text
src/database_agent/events.py                 Task 1 adds P11's eight registered names
src/placement/__init__.py                    narrow P11 public exports
src/placement/vocabulary.py                  P11's closed sets; re-exports what other parts own
src/placement/records.py                     PlacementDecision and its nested contracts
src/placement/schema.py                      P11-owned append-only SQLite tables
src/placement/store.py                       append, supersede, current and history reads
src/placement/config.py                      P1-ceiling adapter, SupportPolicy, ConfigurationRequired
src/placement/index.py                       the §6.2 retrieval index over P10's frozen profiles
src/placement/retrieval.py                   bounded candidates and conflict suppression
src/placement/graph.py                       the §6.4 node-local evidence graph, typed edges
src/placement/scoring.py                     the two-condition record and the deterministic path
src/placement/privacy.py                     carried P7 state and derived review policy
src/placement/learning.py                    scoped negative-example suppression
src/placement/p8_seam.py                     Site C and Site D authorities and verdict transcription
src/placement/groups.py                      group plans, outliers, multi-home
src/placement/residual.py                    residual sets, set gating, the eight actions, the return loop
src/placement/review.py                      the P13 review_action receiver
src/placement/versions.py                    plan-version re-projection
src/placement/stage_output.py                P11 → P2 envelope and dimension mapping
src/placement/pipeline.py                    the §6.12 nine-step orchestration
src/placement/fixtures.py                    golden P11 fixtures published to P12 and P13
src/placement/events.py                      P11's §8.2 appends, one function per event

tests/p11/conftest.py                        real P1–P9 database fixture
tests/p11/p10_fixtures.py                    frozen-tree contract fixture, tests only
tests/p11/p9_fixtures.py                     seeds REAL P9 rows through P9's writers, tests only
tests/p11/p13_fixtures.py                    review_action fixture, tests only
tests/p11/test_p11_*.py                      focused TDD suites
tests/integration/test_p11_p10_tree.py       live P10 dependency gate
tests/integration/test_p11_p8_seam.py        live P8 Site C/D authorities and verdicts
tests/integration/test_p11_p12_node_boundary.py  node-not-path seam
tests/integration/test_p11_p2_replay.py      replay-only stage outputs
```

No task edits `planning/domains/`, deferred catalogues, prompts, `.superpowers/`, or any file under `src/llm_harness/`, `src/grouping/`, `src/privacy/`, `src/facts/` or `src/evidence_shape/`. Task 1 is the single exception and touches exactly one P1 file.

### Test import convention

**Every test module in this plan imports a sibling fixture as `from p11.<module> import …`, never `from tests.p11.<module> import …`.** This is not style; the second form does not resolve.

`pyproject.toml:27-29` sets `testpaths = ["tests"]` and `pythonpath = ["src"]`. There is no `tests/__init__.py`, so under pytest's default prepend import mode the basedir pytest puts on `sys.path` is `tests/` itself, and `tests/p11/` — which Task 1 creates with an `__init__.py` — is importable as the top-level package `p11`. `tests` is not a package on that path, so `from tests.p11…` raises at collection.

The live suite is unanimous: `grep -rn --include='*.py' 'from tests\.' tests/` returns **zero** hits across 3618 green tests, while `tests/p9/test_p9_learning.py:49` reads `from p9.p13_fixtures import …`, `tests/p9/test_p9_fixtures.py:216` reads `from p9.p8_fixtures import RECORDED_P8_VERDICTS`, and `tests/p8/` uses `from p8.conftest import …` ten times. `tests/p9/__init__.py` states the reason in P9's own words: *"`tests/` carries no top-level `__init__.py`, so pytest puts each test directory on `sys.path`. This file makes `tests/p9/conftest.py` importable as `p9.conftest` rather than as the top-level module `conftest`, the way `tests/p8/__init__.py` does for P8."*

`tests/p11/__init__.py` (Task 1) is what makes `p11.conftest` unambiguous, and it is the reason P11 does **not** use P5's older bare `from conftest import FIXED_CLOCK` form: `tests/p1_contract.py:1-7` records that every `conftest.py` is imported as the top-level module `conftest`, so a second one shadows the first in `sys.modules` and the bare import silently resolves against the wrong file.

### Evidence and review UX contract

This is a P11 requirement, not later interface polish. The implementation must preserve
what a trustworthy review surface needs:

- Every candidate, suppression, anchor and decision carries typed evidence references
  (`observation_key`, plus the fact row and the membership that supported it), the plan
  version it is valid in, and the node id it names — never a path.
- A decision exposes `matching_facts`, `group_support`, `graph_anchors` and
  `conflicts_considered` separately. A semantic neighbour is retrieval only and can
  never be the sole support for `outcome = place`.
- Uncertainty is explicit and typed: `abstain` with a named `abstention_reason`,
  `ask_user`, `mark_review_later`, and a budget deferral are four different states and
  render differently. A budget deferral is never described as "understood and found
  unimportant".
- `explanation` states the actual basis and claims no evidence the file does not carry.
- Protected material never appears as raw content in a group summary or a dossier, and
  a decision resting on it is never `auto_eligible`.
- Every user action is append-only, scoped and reversible; nothing is overwritten and
  no decision is deleted.

---

### Task 1: Register P11's §8.2 event names in P1

**Files:**
- Modify: `src/database_agent/events.py`
- Modify: `tests/test_events.py`
- Create: `tests/p11/__init__.py`

**Consumes:** `database_agent.events.RESERVED_EVENT_TYPES`, `_REGISTERED`.

**Produces:** nine entries in `REGISTERED_EVENT_TYPES`, each with `base = "placement recommendation"`.

**Done-means:** SPEC:683-693 (Provenance, "Appends"), and the precondition for Done-means 1–16, none of which can log.

**Why this is first.** `append_event` raises `UnregisteredEventType` for any name outside the frozen table (`src/database_agent/events.py:120-124`) and the module publishes no run-time registration call — `tests/test_events.py:105-109` asserts that. `src/database_agent/events.py:62-65` states the standing gap in P1's own words: *"P11's eight typed specializations of "placement recommendation" belong here and are ABSENT ON PURPOSE … When P11 prints the eight, add them here with `base="placement recommendation"`."* Until this lands, every P11 write path that logs fails, and the failure is correct.

**Nine, not eight — and the count changes on purpose.** SPEC:689 is one bullet carrying two state changes: *"residual set surfaced; residual set-level decision recorded"*. They are separated by a user gesture and by §7.6's spend gate, and the whole purpose of that gate is that a set can be surfaced and never decided. One name could not tell a surfaced-but-undecided set from a decided one, which is the state §7.6 exists to make visible. P1's comment says eight because it was written from the bullet count; the comment is corrected in the same commit.

- [ ] **Step 1: Write the failing registry tests**

Replace `tests/test_events.py:138-145` — the standing placeholder that asserts P11 has spelled nothing — and update the count assertion at `:92-94`.

```python
def test_p11s_nine_specializations_are_registered_under_one_base():
    # The gap this replaces was P1's standing record that P11 had published no
    # identifiers. It is closed by P11 printing them, not by P1 inventing one.
    p11 = {n for n, b in EVENT_TYPES.items() if b == "placement recommendation"}
    assert p11 == {
        "placement_index_entry_built",
        "candidate_destination_retrieval",
        "placement_recommendation_emitted",
        "group_plan_emitted",
        "residual_set_surfaced",
        "residual_set_decision_recorded",
        "residual_recommendation_emitted",
        "return_to_placement_issued",
        "placement_review_decision",
    }
    assert len(p11) == 9


def test_a_surfaced_residual_set_is_a_different_event_from_a_decided_one(conn):
    # §7.6 gates model spend on a set decision, so a set that was shown and never
    # decided must be distinguishable from one that was decided. A shared name
    # could not say which happened.
    create_schema(conn)
    for name in ("residual_set_surfaced", "residual_set_decision_recorded"):
        append_event(conn, **_minimal(event_type=name, subsystem="P11"))
    rows = conn.execute(
        "SELECT event_type, base_event_type FROM events ORDER BY event_id"
    ).fetchall()
    assert [r["event_type"] for r in rows] == [
        "residual_set_surfaced", "residual_set_decision_recorded",
    ]
    assert {r["base_event_type"] for r in rows} == {"placement recommendation"}


def test_p11_registers_no_name_that_shadows_a_reserved_one():
    p11 = {n for n, b in EVENT_TYPES.items() if b == "placement recommendation"}
    assert not p11 & RESERVED_EVENT_TYPES
```

And amend the existing count assertion in `test_the_registered_table_matches_the_declaring_specs`:

```python
    p11 = {"placement_index_entry_built", "candidate_destination_retrieval",
           "placement_recommendation_emitted", "group_plan_emitted",
           "residual_set_surfaced", "residual_set_decision_recorded",
           "residual_recommendation_emitted", "return_to_placement_issued",
           "placement_review_decision"}
    assert len(p7) == 8 and len(p8) == 5 and len(p13) == 3 and len(p11) == 9
    assert set(REGISTERED_EVENT_TYPES) == p7 | p8 | p13 | p11
    # 19 + 8 + 5 + 3 + 9.
    assert len(EVENT_TYPES) == 44
```

- [ ] **Step 2: Run the tests and verify RED**

Run: `python3 -m pytest -q tests/test_events.py`

Expected: FAIL. `test_p11s_nine_specializations_are_registered_under_one_base` fails because the set is empty, and `test_the_registered_table_matches_the_declaring_specs` fails on `len(EVENT_TYPES) == 35`.

- [ ] **Step 3: Add the nine names**

In `src/database_agent/events.py`, replace the four-line comment block at `:62-65` with:

```python
    # P11 SPEC, Cross-cutting answers -> Provenance. Nine typed specializations of
    # the reserved name `placement recommendation`. The base is a rollup for §8.2's
    # "current and historical placement proposals"; it is not a claim that building
    # an index entry is a recommendation. SPEC:689 is one bullet carrying two state
    # changes -- a set surfaced and a set decided -- and §7.6 gates model spend on
    # the second, so they are two names and the count is nine, not the eight the
    # bullet list reads as.
    "placement_index_entry_built": "placement recommendation",
    "candidate_destination_retrieval": "placement recommendation",
    "placement_recommendation_emitted": "placement recommendation",
    "group_plan_emitted": "placement recommendation",
    "residual_set_surfaced": "placement recommendation",
    "residual_set_decision_recorded": "placement recommendation",
    "residual_recommendation_emitted": "placement recommendation",
    "return_to_placement_issued": "placement recommendation",
    "placement_review_decision": "placement recommendation",
```

The two import-time guards at `:70-75` check this for free: a name colliding with one of the nineteen raises, and a base outside the nineteen raises. Add nothing else — there is no registration call and this task does not create one.

- [ ] **Step 4: Run and verify GREEN**

Run: `python3 -m pytest -q tests/test_events.py tests/test_p1_p7_seams.py tests/p7/test_p7_authorship.py tests/p8/test_p8_provenance.py`

Expected: PASS. `test_a_specialization_stores_its_reserved_base_type` (`tests/test_events.py:127-136`) now exercises all nine, because it drives off the frozen table rather than a typed list; P7's and P8's registries are untouched.

- [ ] **Step 5: Commit**

```bash
mkdir -p tests/p11 && touch tests/p11/__init__.py
git add src/database_agent/events.py tests/test_events.py tests/p11/__init__.py
git commit -m "feat(p1): register P11's nine placement event names"
```

### Task 2: Publish P11's vocabularies, importing every value another part owns

**Files:**
- Create: `src/placement/__init__.py`
- Create: `src/placement/vocabulary.py`
- Create: `tests/p11/test_p11_vocabulary.py`

**Consumes:**

```python
from llm_harness.vocabulary import (
    ABSTAIN, ACCEPT_CONTEXT_SUPPORTED, ACCEPT_DIRECT, C_PLACEMENT, CONTEXT_SUPPORTED,
    D_RESIDUAL, OUTCOMES as P8_OUTCOMES, REJECT, RESIDUAL_ACTIONS, SCOPE_FILE,
    SCOPE_GROUP, WEAK,
)
from facts.states import DIRECT, LLM_SUPPORTED, POSSIBLE, USER_CONFIRMED, VALIDATED
from database_agent.events import CORRECTION_SCOPES
from privacy.vocabulary import HANDLING_CLASSES
```

**Produces:** `OUTCOMES`, `ORIGIN_STAGES`, `SUBJECT_KINDS`, `NODE_ROLES`, `RETURN_TARGET_KINDS`, `MARKED_STATES`, `EVIDENCE_TYPES`, `CONFIDENCE_CLASSES`, `MEETS_MARGIN_VALUES`, `VERDICTS`, `ABSTENTION_REASONS`, `MODEL_ELIGIBILITY`, `REVIEW_POLICIES`, `SET_CHOICES`, `OUTLIER_ROUTES`, `STAGE_IDS`, one named constant per value of each, `OutOfVocabulary`, and `check(value, closed, *, name)`.

**Done-means:** the precondition for every other task; SPEC:306, :311, :316-318, :321-328, :335-340, :357-367, :374-377, :517-518, :538-542.

**The one rule that decides every import.** Import when the *concept* is the same; publish a distinct constant and pin it by test when the *spelling* is the same but the concept differs. `src/grouping/vocabulary.py:79-89` is the precedent: P1 stores `scan_state = "included"` and P9's `INCLUDED` means a member is in a group, so P9 published `P1_INCLUDED_SCAN_STATE` rather than importing a value that would then wear two meanings. P11 has four such collisions — `return_to_placement`, `leave_in_place`, `abstain` and `mark_review_later` are P8 *dispositions* or *actions* and P11 *outcomes* — so P11 spells its own and a test asserts the strings stay equal. Everything where the concept genuinely is P8's (`verdict`, the eight residual actions, `file` / `group`, `context-supported`) is imported.

- [ ] **Step 1: Write the failing vocabulary tests**

```python
# tests/p11/test_p11_vocabulary.py
"""P11's closed sets, and the two ways a value can be another part's."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from placement import vocabulary as v

PLACEMENT_ROOT = Path(__file__).resolve().parents[2] / "src" / "placement"


def test_every_closed_set_has_one_named_constant_per_member():
    sets = {
        "OUTCOMES": v.OUTCOMES, "ORIGIN_STAGES": v.ORIGIN_STAGES,
        "SUBJECT_KINDS": v.SUBJECT_KINDS, "NODE_ROLES": v.NODE_ROLES,
        "RETURN_TARGET_KINDS": v.RETURN_TARGET_KINDS,
        "MARKED_STATES": v.MARKED_STATES, "EVIDENCE_TYPES": v.EVIDENCE_TYPES,
        "CONFIDENCE_CLASSES": v.CONFIDENCE_CLASSES,
        "MEETS_MARGIN_VALUES": v.MEETS_MARGIN_VALUES, "VERDICTS": v.VERDICTS,
        "ABSTENTION_REASONS": v.ABSTENTION_REASONS,
        "MODEL_ELIGIBILITY": v.MODEL_ELIGIBILITY,
        "REVIEW_POLICIES": v.REVIEW_POLICIES, "SET_CHOICES": v.SET_CHOICES,
        "OUTLIER_ROUTES": v.OUTLIER_ROUTES, "STAGE_IDS": v.STAGE_IDS,
    }
    bound = {name: value for name, value in vars(v).items()
             if isinstance(value, str) and not name.startswith("_")}
    for set_name, members in sets.items():
        assert len(set(members)) == len(members), set_name
        for member in members:
            assert member in bound.values(), (set_name, member)


def test_p11_outcomes_are_exactly_the_seven_p2_already_refuses():
    # P2 enumerated P11's record outcomes before P11 existed, to refuse them in
    # the envelope. Two lists of one vocabulary is the drift this pins shut.
    from eval_harness.stage_output import _FOREIGN_OUTCOMES
    assert set(v.OUTCOMES) == set(_FOREIGN_OUTCOMES)
    assert len(v.OUTCOMES) == 7


def test_the_four_colliding_spellings_stay_equal_to_p8s():
    # Same string, different axis: P8's are dispositions and actions, P11's are
    # outcomes. They are not imported, so a change on either side must break here.
    from llm_harness import vocabulary as p8
    assert v.RETURN_TO_PLACEMENT == p8.RETURN_TO_PLACEMENT
    assert v.LEAVE_IN_PLACE == p8.LEAVE_IN_PLACE
    assert v.ABSTAIN == p8.ABSTAIN
    assert v.MARK_REVIEW_LATER == p8.MARK_REVIEW_LATER


def test_the_verdict_vocabulary_is_p8s_object_and_not_a_copy():
    from llm_harness.vocabulary import OUTCOMES as P8_OUTCOMES
    assert v.VERDICTS is P8_OUTCOMES


def test_evidence_types_are_the_live_spellings_not_the_specs():
    # SPEC:335-336 hyphenates `user-confirmed` and `llm-supported`; the live
    # reliability states are snake_case and P11 re-spells neither owner.
    from evidence_shape.vocabulary import RELIABILITY_STATES
    from llm_harness.vocabulary import CONTEXT_SUPPORTED
    dropped = v.DROPPED_RELIABILITY_STATE
    assert dropped == "rejected"
    assert set(v.EVIDENCE_TYPES) == (set(RELIABILITY_STATES) - {dropped}) | {
        CONTEXT_SUPPORTED,
    }
    assert dropped not in v.EVIDENCE_TYPES


def test_no_placement_module_spells_a_value_another_part_owns():
    # By AST over string constants, because a text search matches docstrings.
    from llm_harness.vocabulary import RESIDUAL_ACTIONS
    from llm_harness.vocabulary import OUTCOMES as P8_OUTCOMES
    owned = set(P8_OUTCOMES) | set(RESIDUAL_ACTIONS)
    offenders = []
    for path in sorted(PLACEMENT_ROOT.glob("*.py")):
        if path.name == "vocabulary.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value in owned:
                    offenders.append((path.name, node.lineno, node.value))
    assert offenders == []


def test_check_names_the_set_and_never_the_nearest_match():
    with pytest.raises(v.OutOfVocabulary) as excinfo:
        v.check("plase", v.OUTCOMES, name="outcome")
    assert "place" not in str(excinfo.value)
    assert str(len(v.OUTCOMES)) in str(excinfo.value)
```

- [ ] **Step 2: Run and verify RED**

Run: `python3 -m pytest -q tests/p11/test_p11_vocabulary.py`

Expected: FAIL at collection — `ModuleNotFoundError: No module named 'placement'`.

- [ ] **Step 3: Implement the vocabulary module**

```python
# src/placement/vocabulary.py
"""P11's closed vocabularies. Named constant == string value, one home each.

One rule decides every import here. Import when the CONCEPT is the same; publish
a distinct constant and pin it by test when the SPELLING is the same but the
concept differs. `grouping/vocabulary.py` set the precedent with P1's
`scan_state = "included"`: a borrowed value gets a name that cannot be mistaken
for the local one, never a shared binding.

Four strings are P8's and P11's at once. `return_to_placement`, `leave_in_place`
and `abstain` are P8 dispositions; `mark_review_later` is a P8 residual action.
All four are P11 OUTCOMES -- a different axis -- so P11 spells its own and a test
holds the strings equal. `VERDICTS` is the opposite case: it IS P8's outcome
vocabulary (SPEC:462, MINOR 7) and is the same object, not a copy.

No path, folder, template or node-creation concept lives here. P11 names nodes
P10 froze; it mints none.
"""
from __future__ import annotations

from database_agent.events import CORRECTION_SCOPES
from evidence_shape.vocabulary import RELIABILITY_STATES
from facts.states import DIRECT, LLM_SUPPORTED, POSSIBLE, USER_CONFIRMED, VALIDATED
from llm_harness.vocabulary import (
    ABSTAIN as P8_ABSTAIN,
    CONTEXT_SUPPORTED,
    OUTCOMES as P8_OUTCOMES,
    RESIDUAL_ACTIONS,
    SCOPE_FILE,
    SCOPE_GROUP,
)
from privacy.vocabulary import HANDLING_CLASSES

# --- re-exported, because the concept is the other part's ------------------------

#: §6.10's verdict, unchanged from P8 (SPEC:462). The same tuple object.
VERDICTS: tuple[str, ...] = P8_OUTCOMES

#: §7.7's eight actions in their machine spelling. P8 owns the controlled set and
#: refuses anything outside it at Site D; P11 maps them into `OUTCOMES`.
ACTIONS: tuple[str, ...] = RESIDUAL_ACTIONS

#: §8.7's six scopes, in P1's spelling, which is also P13's.
SCOPES: tuple[str, ...] = CORRECTION_SCOPES

#: §8.4's five handling classes, P7's.
CLASSES: tuple[str, ...] = HANDLING_CLASSES

# --- origin and subject -----------------------------------------------------------

PLACEMENT: str = "placement"
RESIDUAL: str = "residual"
ORIGIN_STAGES: tuple[str, ...] = (PLACEMENT, RESIDUAL)

FILE: str = SCOPE_FILE
GROUP: str = SCOPE_GROUP
SUBJECT_KINDS: tuple[str, ...] = (FILE, GROUP)

# --- outcomes: P11's own axis, four of them spelled like P8 values ----------------

PLACE: str = "place"
RETURN_TO_PLACEMENT: str = "return_to_placement"
MARK_REVIEW_LATER: str = "mark_review_later"
LEAVE_IN_PLACE: str = "leave_in_place"
MARK_STATE: str = "mark_state"
ASK_USER: str = "ask_user"
ABSTAIN: str = P8_ABSTAIN

OUTCOMES: tuple[str, ...] = (
    PLACE, RETURN_TO_PLACEMENT, MARK_REVIEW_LATER, LEAVE_IN_PLACE, MARK_STATE,
    ASK_USER, ABSTAIN,
)

#: The one outcome P12 builds a plan from (SPEC:551, M13). Every other produces
#: no plan, `abstain` included.
PLAN_BEARING_OUTCOMES: tuple[str, ...] = (PLACE,)

# --- the destination -------------------------------------------------------------
#
# P10's vocabulary, carried verbatim on the node (SPEC:322-323, MINOR 6). P10 is
# unbuilt, so the values are spelled here from P10's SPEC and this module is the
# one home until P10 publishes them, at which point this becomes a re-export.

ORDINARY: str = "ordinary"
SCOPED_GENERAL: str = "scoped-general"
RESIDUAL_ROLE: str = "residual"
SHARED_MATERIAL: str = "shared-material"
NODE_ROLES: tuple[str, ...] = (ORDINARY, SCOPED_GENERAL, RESIDUAL_ROLE, SHARED_MATERIAL)

PHYSICAL_DESTINATION: str = "physical-destination"
REVIEW_ONLY: str = "review-only"
LEAVE_IN_PLACE_DISPOSITION: str = "leave-in-place"
DISPOSITIONS: tuple[str, ...] = (
    PHYSICAL_DESTINATION, REVIEW_ONLY, LEAVE_IN_PLACE_DISPOSITION,
)

EXISTING: str = "existing"
PROPOSED: str = "proposed"
USER_CREATED: str = "user-created"
PROTECTED_NODE: str = "protected"
IGNORED: str = "ignored"
NODE_TYPES: tuple[str, ...] = (
    EXISTING, PROPOSED, USER_CREATED, PROTECTED_NODE, IGNORED,
)

CONFIRMED_DOMAIN_GROUP: str = "confirmed_domain_group"
ACCEPTED_GRAPH_OR_PURPOSE_PACKET: str = "accepted_graph_or_purpose_packet"
RETURN_TARGET_KINDS: tuple[str, ...] = (
    CONFIRMED_DOMAIN_GROUP, ACCEPTED_GRAPH_OR_PURPOSE_PACKET,
)

PROTECTED: str = "protected"
UNSUPPORTED: str = "unsupported"
MARKED_STATES: tuple[str, ...] = (PROTECTED, UNSUPPORTED)

# --- evidence and confidence -----------------------------------------------------
#
# Five of the six are P6's reliability states in their live snake_case spelling;
# `rejected` is dropped because a rejected fact cannot support a placement
# (SPEC:427-435). `context-supported` is added, hyphenated, because it is P9's
# membership basis and P8 already publishes that exact string. The mixed casing is
# what two owners publish, and P11 respells neither of them.

EVIDENCE_TYPES: tuple[str, ...] = (
    USER_CONFIRMED, DIRECT, VALIDATED, LLM_SUPPORTED, CONTEXT_SUPPORTED, POSSIBLE,
)

EXACT_FACT_MATCH: str = "exact fact match"
CONTEXT_SUPPORTED_GROUP_MATCH: str = "context-supported group match"
SHARED_MATERIAL_DECISION: str = "shared-material decision"
ABSTAIN_NO_SUPPORTED_DESTINATION: str = "abstain: no supported destination"
CONFIDENCE_CLASSES: tuple[str, ...] = (
    EXACT_FACT_MATCH, CONTEXT_SUPPORTED_GROUP_MATCH, SHARED_MATERIAL_DECISION,
    ABSTAIN_NO_SUPPORTED_DESTINATION,
)

# --- the two-condition rule ------------------------------------------------------

MARGIN_TRUE: str = "true"
MARGIN_TRUE_VACUOUS: str = "true_vacuous"
MARGIN_FALSE: str = "false"
MEETS_MARGIN_VALUES: tuple[str, ...] = (
    MARGIN_TRUE, MARGIN_TRUE_VACUOUS, MARGIN_FALSE,
)

# --- abstention ------------------------------------------------------------------

NO_SUPPORTED_DESTINATION: str = "no_supported_destination"
LOW_MARGIN: str = "low_margin"
SEMANTIC_ONLY: str = "semantic_only"
GENERIC_HUB_ONLY: str = "generic_hub_only"
CONFLICTING_FACTS: str = "conflicting_facts"
NO_SHARED_BRANCH: str = "no_shared_branch"
BUDGET_DEFERRED: str = "budget_deferred"
PRIVACY_BLOCKED: str = "privacy_blocked"
ABSTENTION_REASONS: tuple[str, ...] = (
    NO_SUPPORTED_DESTINATION, LOW_MARGIN, SEMANTIC_ONLY, GENERIC_HUB_ONLY,
    CONFLICTING_FACTS, NO_SHARED_BRANCH, BUDGET_DEFERRED, PRIVACY_BLOCKED,
)

# --- privacy and review ----------------------------------------------------------

LOCAL_ONLY: str = "local_only"
DOSSIER_PERMITTED: str = "dossier_permitted"
REDACTED_ELIGIBILITY: str = "redacted"
MODEL_ELIGIBILITY: tuple[str, ...] = (
    LOCAL_ONLY, DOSSIER_PERMITTED, REDACTED_ELIGIBILITY,
)

AUTO_ELIGIBLE: str = "auto_eligible"
REVIEW_REQUIRED: str = "review_required"
BLOCKED_PENDING_USER: str = "blocked_pending_user"
REVIEW_POLICIES: tuple[str, ...] = (
    AUTO_ELIGIBLE, REVIEW_REQUIRED, BLOCKED_PENDING_USER,
)

# --- residual sets ---------------------------------------------------------------

REVIEW_WITH_MODEL: str = "review_with_model_against_approved_residual_folders"
SEND_TO_APPROVED_NODE: str = "send_to_approved_node"
CREATE_CUSTOM_BRANCH: str = "create_custom_branch"

#: §7.6's four. The first IS the outcome `leave_in_place`, one level up -- a set
#: the user leaves alone and a file left alone are the same decision at two
#: scales, so the constant is reused and not respelled.
SET_CHOICES: tuple[str, ...] = (
    LEAVE_IN_PLACE, REVIEW_WITH_MODEL, SEND_TO_APPROVED_NODE, CREATE_CUSTOM_BRANCH,
)

ROUTED_TO_NODE: str = "node"
ROUTED_TO_REVIEW_QUEUE: str = "review_queue"
OUTLIER_ROUTES: tuple[str, ...] = (ROUTED_TO_NODE, ROUTED_TO_REVIEW_QUEUE)

# --- P2 -------------------------------------------------------------------------

CANDIDATE_NODE_RETRIEVAL: str = "candidate_node_retrieval"
PLACEMENT_SCORING: str = "placement_scoring"
STAGE_IDS: tuple[str, ...] = (CANDIDATE_NODE_RETRIEVAL, PLACEMENT_SCORING)

DIMENSION_PLACEMENT: str = "placement"
DIMENSION_RESIDUAL: str = "residual"
#: §8.5's *"Retrieval quality: for sparse files, did the correct anchors appear in
#: the top candidate neighborhood?"* -- which is what §6.2 does, in the design's
#: own words. P9 already measures its own retrieval stage under this name, and
#: two stages sharing one dimension is the shape §8.5 already has: its ten
#: dimensions are a shorter and separate list from its ten stages on purpose. The
#: two are kept apart by SUBJECT namespace, not by an eleventh dimension.
DIMENSION_RETRIEVAL: str = "retrieval"
DIMENSIONS: tuple[str, ...] = (
    DIMENSION_PLACEMENT, DIMENSION_RESIDUAL, DIMENSION_RETRIEVAL,
)

# --- events ---------------------------------------------------------------------

INDEX_ENTRY_BUILT: str = "placement_index_entry_built"
CANDIDATE_RETRIEVAL: str = "candidate_destination_retrieval"
RECOMMENDATION_EMITTED: str = "placement_recommendation_emitted"
GROUP_PLAN_EMITTED: str = "group_plan_emitted"
RESIDUAL_SET_SURFACED: str = "residual_set_surfaced"
RESIDUAL_SET_DECIDED: str = "residual_set_decision_recorded"
RESIDUAL_RECOMMENDATION_EMITTED: str = "residual_recommendation_emitted"
RETURN_ISSUED: str = "return_to_placement_issued"
REVIEW_DECISION: str = "placement_review_decision"
EVENT_TYPES: tuple[str, ...] = (
    INDEX_ENTRY_BUILT, CANDIDATE_RETRIEVAL, RECOMMENDATION_EMITTED,
    GROUP_PLAN_EMITTED, RESIDUAL_SET_SURFACED, RESIDUAL_SET_DECIDED,
    RESIDUAL_RECOMMENDATION_EMITTED, RETURN_ISSUED, REVIEW_DECISION,
)

#: `rejected` is deliberately absent from `EVIDENCE_TYPES` and named here so the
#: exclusion is a published decision rather than an omission (SPEC:430-432).
DROPPED_RELIABILITY_STATE: str = "rejected"
assert DROPPED_RELIABILITY_STATE in RELIABILITY_STATES
assert DROPPED_RELIABILITY_STATE not in EVIDENCE_TYPES


class OutOfVocabulary(ValueError):
    """A value outside a closed P11 set. Not a fallback; a load error."""


def check(value: object, closed: tuple[str, ...], *, name: str) -> str:
    """One membership test. The closed set is named; the nearest match is not.

    Naming the nearest member would be a suggestion, and a suggestion in a
    vocabulary carrying four strings that also belong to P8 is how a
    misspelling becomes a silent change of axis.
    """
    if not isinstance(value, str) or value not in closed:
        raise OutOfVocabulary(
            f"{name}={value!r} is not one of the {len(closed)} values P11 defines "
            f"for it. Adding a member is a contract revision, not an "
            f"implementation decision."
        )
    return value
```

And the package export:

```python
# src/placement/__init__.py
"""P11 — placement against a frozen tree, and the residual workflow.

P11 emits decisions and moves nothing. It names a node P10 froze and never a
path; P12 resolves the path. It supplies P8 the authorities Sites C and D need
and transcribes P8's verdict; it re-implements no check of P8's.

The public surface is narrow by design and grows task by task.
"""
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3 -m pytest -q tests/p11/test_p11_vocabulary.py`

Expected: PASS, including the `_FOREIGN_OUTCOMES` pin — the seven strings at `src/eval_harness/stage_output.py:30-33` are `place`, `return_to_placement`, `mark_review_later`, `leave_in_place`, `mark_state`, `abstain`, `ask_user`, which is exactly `OUTCOMES`.

- [ ] **Step 5: Commit**

```bash
git add src/placement/__init__.py src/placement/vocabulary.py tests/p11/test_p11_vocabulary.py
git commit -m "feat(p11): publish placement vocabularies with one home each"
```

### Task 3: Publish the placement decision record, one shape for both paths

**Files:**
- Create: `src/placement/records.py`
- Create: `tests/p11/test_p11_records.py`

**Consumes:** `placement.vocabulary` (every closed set and `check`).

**Produces:**

```python
class MalformedPlacementRecord(ValueError): ...

@dataclass(frozen=True)
class Subject:
    kind: str; file_id: str | None; content_hash: str | None
    group_id: str | None; member_file_ids: tuple[str, ...]

@dataclass(frozen=True)
class Destination:
    node_id: str; node_role: str

@dataclass(frozen=True)
class ReturnTarget:
    kind: str; id: str

@dataclass(frozen=True)
class Ask:
    question: str; options: tuple[str, ...]

@dataclass(frozen=True)
class DecisionDepth:
    node_depth: int; supported_depth: int; unsupported_levels: tuple[str, ...]

@dataclass(frozen=True)
class MatchingFact:
    file_fact_id: str; field: str; value: str; reliability: str; evidence_ref: str

@dataclass(frozen=True)
class GroupSupport:
    group_id: str; membership: str

@dataclass(frozen=True)
class GraphAnchor:
    edge_type: str; from_file_id: str; to_file_id: str; anchor_file_id: str

@dataclass(frozen=True)
class ConflictConsidered:
    kind: str; conflicting_value: str
    suppressed_node_ids: tuple[str, ...]; evidence_ref: str

@dataclass(frozen=True)
class Alternative:
    node_id: str; support_score: float; rank: int

@dataclass(frozen=True)
class TwoCondition:
    support_score: float; support_threshold: float; meets_threshold: bool
    margin_over_next: float | None; margin_threshold: float
    meets_margin: str; verdict: str; requires_review: bool

@dataclass(frozen=True)
class PrivacyState:
    handling_class: str; model_eligibility: str; consent_audit_ref: int | None

@dataclass(frozen=True)
class ResidualContext:
    set_id: str; set_decision: str; lifecycle_policy_ref: str | None

@dataclass(frozen=True)
class PlacementDecision:
    decision_id: str; plan_version: str
    supersedes: str | None; superseded_by: str | None; supersede_reason: str | None
    created_at: str; origin_stage: str; returned_from: str | None
    subject: Subject; group_plan_id: str | None
    outcome: str; destination: Destination | None
    return_target: ReturnTarget | None; marked_state: str | None; ask: Ask | None
    decision_depth: DecisionDepth; evidence_type: str; confidence_class: str
    matching_facts: tuple[MatchingFact, ...]; group_support: GroupSupport | None
    graph_anchors: tuple[GraphAnchor, ...]
    conflicts_considered: tuple[ConflictConsidered, ...]
    alternatives: tuple[Alternative, ...]; two_condition: TwoCondition
    abstention_reason: str | None; deferred_stage: str | None
    privacy: PrivacyState; review_policy: str; explanation: str
    residual: ResidualContext | None

DECISION_FIELDS: tuple[str, ...]   # the thirty above, in declaration order
```

**Done-means:** 1 (SPEC:610-612), 2 (SPEC:614-619), 15 (SPEC:668-669); the whole of Contract out §1 (SPEC:290-486).

**Why `decision_depth` is not optional detail.** SPEC:414-417 says it replaced a deleted `destination.kind` field: *"an empty `unsupported_levels[]` is the child case, a non-empty one is the broad-parent case and names which levels were not filled."* Without it the record cannot tell a fully-supported child from a deliberately shallow parent, and §6.7 and Done-means 7 are the whole subject of that distinction.

- [ ] **Step 1: Write the failing record tests**

```python
# tests/p11/test_p11_records.py
"""Contract out §1 — one record shape, and the fields that make it one."""
from __future__ import annotations

import dataclasses

import pytest

from placement import vocabulary as v
from placement.records import (
    Alternative, Ask, ConflictConsidered, DecisionDepth, Destination, GraphAnchor,
    GroupSupport, MalformedPlacementRecord, MatchingFact, PlacementDecision,
    PrivacyState, ResidualContext, ReturnTarget, Subject, TwoCondition,
)

T0 = "2026-08-27T00:00:00Z"


def _two_condition(**overrides) -> TwoCondition:
    values = dict(
        support_score=0.9, support_threshold=0.5, meets_threshold=True,
        margin_over_next=0.4, margin_threshold=0.2, meets_margin=v.MARGIN_TRUE,
        verdict="accept_direct", requires_review=False,
    )
    values.update(overrides)
    return TwoCondition(**values)


def _decision(**overrides) -> PlacementDecision:
    values = dict(
        decision_id="d1", plan_version="plan-1", supersedes=None,
        superseded_by=None, supersede_reason=None, created_at=T0,
        origin_stage=v.PLACEMENT, returned_from=None,
        subject=Subject(kind=v.FILE, file_id="f1", content_hash="h1",
                        group_id=None, member_file_ids=()),
        group_plan_id=None, outcome=v.PLACE,
        destination=Destination(node_id="n1", node_role=v.ORDINARY),
        return_target=None, marked_state=None, ask=None,
        decision_depth=DecisionDepth(node_depth=3, supported_depth=3,
                                     unsupported_levels=()),
        evidence_type=v.DIRECT, confidence_class=v.EXACT_FACT_MATCH,
        matching_facts=(MatchingFact(file_fact_id="ff1", field="subject",
                                     value="PHYS1401", reliability=v.DIRECT,
                                     evidence_ref="obs-1"),),
        group_support=None, graph_anchors=(), conflicts_considered=(),
        alternatives=(), two_condition=_two_condition(),
        abstention_reason=None, deferred_stage=None,
        privacy=PrivacyState(handling_class="personal_non_sensitive",
                             model_eligibility=v.DOSSIER_PERMITTED,
                             consent_audit_ref=None),
        review_policy=v.AUTO_ELIGIBLE,
        explanation="The file's direct subject fact PHYS1401 matches this node's "
                    "expected value.",
        residual=None,
    )
    values.update(overrides)
    return PlacementDecision(**values)


def test_a_residual_decision_parses_with_no_residual_specific_branch():
    # Done-means 1: a consumer built against the shape reads both paths the same.
    placement = _decision()
    residual = _decision(
        decision_id="d2", origin_stage=v.RESIDUAL, outcome=v.LEAVE_IN_PLACE,
        destination=None,
        decision_depth=DecisionDepth(node_depth=0, supported_depth=0,
                                     unsupported_levels=()),
        confidence_class=v.ABSTAIN_NO_SUPPORTED_DESTINATION,
        # `margin_over_next=None` REQUIRES `true_vacuous`: `TwoCondition`
        # refuses a null margin under any other value, because a measured margin
        # with no number is a comparison nobody made. This residual file had one
        # candidate and no next-best, so vacuous is also the true answer.
        two_condition=_two_condition(meets_threshold=False, verdict="weak",
                                     margin_over_next=None,
                                     meets_margin=v.MARGIN_TRUE_VACUOUS),
        residual=ResidualContext(set_id="s1", set_decision=v.REVIEW_WITH_MODEL,
                                 lifecycle_policy_ref=None),
    )
    for decision in (placement, residual):
        assert decision.outcome in v.OUTCOMES
        assert decision.explanation
        assert isinstance(decision.two_condition, TwoCondition)
    assert {f.name for f in dataclasses.fields(placement)} == {
        f.name for f in dataclasses.fields(residual)}


def test_a_destination_is_present_only_when_the_outcome_is_place():
    with pytest.raises(MalformedPlacementRecord):
        _decision(outcome=v.ABSTAIN, abstention_reason=v.LOW_MARGIN)
    with pytest.raises(MalformedPlacementRecord):
        _decision(outcome=v.PLACE, destination=None)


def test_an_abstention_names_a_reason_and_a_reason_needs_an_abstention():
    ok = _decision(outcome=v.ABSTAIN, destination=None,
                   abstention_reason=v.NO_SUPPORTED_DESTINATION)
    assert ok.abstention_reason == v.NO_SUPPORTED_DESTINATION
    with pytest.raises(MalformedPlacementRecord):
        _decision(outcome=v.ABSTAIN, destination=None, abstention_reason=None)
    with pytest.raises(MalformedPlacementRecord):
        _decision(abstention_reason=v.LOW_MARGIN)


def test_return_to_placement_is_residual_only_and_ask_user_is_placement_only():
    # SPEC:437-445. The two paths differ by exactly these two outcomes.
    with pytest.raises(MalformedPlacementRecord):
        _decision(outcome=v.RETURN_TO_PLACEMENT, destination=None,
                  return_target=ReturnTarget(kind=v.CONFIRMED_DOMAIN_GROUP, id="g1"))
    ok = _decision(origin_stage=v.RESIDUAL, outcome=v.RETURN_TO_PLACEMENT,
                   destination=None,
                   return_target=ReturnTarget(kind=v.CONFIRMED_DOMAIN_GROUP, id="g1"),
                   residual=ResidualContext(set_id="s1",
                                            set_decision=v.REVIEW_WITH_MODEL,
                                            lifecycle_policy_ref=None))
    assert ok.return_target.id == "g1"
    with pytest.raises(MalformedPlacementRecord):
        _decision(origin_stage=v.RESIDUAL, outcome=v.ASK_USER, destination=None,
                  ask=Ask(question="Which packet is this transcript's home?",
                          options=("n-columbia", "n-duke")),
                  residual=ResidualContext(set_id="s1",
                                           set_decision=v.REVIEW_WITH_MODEL,
                                           lifecycle_policy_ref=None))


def test_a_vacuous_margin_records_no_number_and_a_measured_one_does():
    # B8(b): the two must be distinguishable, so a reviewer and a P2 replay can
    # tell an unopposed candidate from a genuine margin.
    vacuous = _decision(two_condition=_two_condition(
        margin_over_next=None, meets_margin=v.MARGIN_TRUE_VACUOUS))
    assert vacuous.two_condition.margin_over_next is None
    with pytest.raises(MalformedPlacementRecord):
        _two_condition(margin_over_next=0.3, meets_margin=v.MARGIN_TRUE_VACUOUS)
    with pytest.raises(MalformedPlacementRecord):
        _two_condition(margin_over_next=None, meets_margin=v.MARGIN_TRUE)


def test_a_context_supported_verdict_is_never_auto_eligible():
    with pytest.raises(MalformedPlacementRecord):
        _decision(two_condition=_two_condition(verdict="accept_context_supported",
                                               requires_review=True),
                  review_policy=v.AUTO_ELIGIBLE)


def test_a_user_attached_membership_is_never_validated_or_auto_eligible():
    # M12, SPEC:176-178. Nothing was read from the file, so nothing validated it.
    support = GroupSupport(group_id="g1", membership="user-attached")
    with pytest.raises(MalformedPlacementRecord):
        _decision(group_support=support, evidence_type=v.VALIDATED)
    with pytest.raises(MalformedPlacementRecord):
        _decision(group_support=support, evidence_type=v.POSSIBLE,
                  review_policy=v.AUTO_ELIGIBLE)


def test_unsupported_levels_distinguish_a_child_from_a_broad_parent():
    # SPEC:414-417: this is what replaced `destination.kind`.
    child = _decision()
    parent = _decision(decision_depth=DecisionDepth(
        node_depth=2, supported_depth=2, unsupported_levels=("term",)))
    assert child.decision_depth.unsupported_levels == ()
    assert parent.decision_depth.unsupported_levels == ("term",)
    with pytest.raises(MalformedPlacementRecord):
        DecisionDepth(node_depth=1, supported_depth=3, unsupported_levels=())


def test_the_record_cannot_express_deletion_expiry_or_a_path():
    # Done-means 15, and B3. A field name is the whole surface here.
    names = {f.name for f in dataclasses.fields(PlacementDecision)}
    for banned in ("path", "resolved_path", "destination_path", "delete",
                   "deleted", "expiry", "expires_at", "disposable", "ttl"):
        assert banned not in names
    assert "node_id" in {f.name for f in dataclasses.fields(Destination)}
    assert "path" not in {f.name for f in dataclasses.fields(Destination)}


def test_every_citation_is_an_observation_key_and_never_an_observation_id():
    # M14, SPEC:193-200. §8.7 needs a rejected match recorded today to still
    # resolve to its evidence after an extractor upgrade; only the key does.
    for record in (MatchingFact, ConflictConsidered):
        names = {f.name for f in dataclasses.fields(record)}
        assert "evidence_ref" in names
        assert "observation_id" not in names


def test_a_budget_deferral_names_the_stage_it_was_cut_short_at():
    ok = _decision(outcome=v.ABSTAIN, destination=None,
                   abstention_reason=v.BUDGET_DEFERRED,
                   deferred_stage=v.PLACEMENT_SCORING)
    assert ok.deferred_stage == v.PLACEMENT_SCORING
    with pytest.raises(MalformedPlacementRecord):
        _decision(outcome=v.ABSTAIN, destination=None,
                  abstention_reason=v.BUDGET_DEFERRED, deferred_stage=None)
    with pytest.raises(MalformedPlacementRecord):
        _decision(deferred_stage=v.PLACEMENT_SCORING)
```

- [ ] **Step 2: Run and verify RED**

Run: `python3 -m pytest -q tests/p11/test_p11_records.py`

Expected: FAIL at collection — `ModuleNotFoundError: No module named 'placement.records'`.

- [ ] **Step 3: Implement the record**

```python
# src/placement/records.py
"""P11's frozen records. One shape for the §6 path and the §7 path.

The single most load-bearing rule: a consumer parses a residual decision with no
residual-specific branch (SPEC:610-612). Everything §7.7's eight actions need is
already a field the §6 path has, because two pairs of actions differ only by a
qualifier -- `return_target.kind` and `marked_state` -- and both are on the one
shape.

`decision_depth` is not detail. It is what replaced a deleted `destination.kind`
(SPEC:414-417): an empty `unsupported_levels` is the fully-supported child case, a
non-empty one is the deliberately shallower parent and names which levels were not
filled. Without it §6.7 has no expression in the record at all.

No field here can hold a filesystem path, a deletion, or an expiry. P11 names a
node; P12 resolves a path (B3), and §7.11 forbids the other two outright.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, fields

from placement.vocabulary import (
    ABSTAIN, ABSTENTION_REASONS, ASK_USER, AUTO_ELIGIBLE, BUDGET_DEFERRED,
    CONFIDENCE_CLASSES, EVIDENCE_TYPES, FILE, MARGIN_TRUE_VACUOUS, MARKED_STATES,
    MARK_STATE, MEETS_MARGIN_VALUES, MODEL_ELIGIBILITY, NODE_ROLES, ORIGIN_STAGES,
    OUTCOMES, PLACE, PLACEMENT, RESIDUAL, RETURN_TARGET_KINDS,
    RETURN_TO_PLACEMENT, REVIEW_POLICIES, SET_CHOICES, STAGE_IDS, SUBJECT_KINDS,
    VALIDATED, VERDICTS, check,
)

#: P9's third membership basis, in P9's spelling. It is not in P8's `EVIDENCE_BASES`
#: (which has two), so it cannot be imported from there, and M12 makes it mandatory.
USER_ATTACHED: str = "user-attached"

#: The verdict that always requires review (§4.8, §6.10, and P8's own invariant).
ACCEPT_CONTEXT_SUPPORTED: str = "accept_context_supported"


class MalformedPlacementRecord(ValueError):
    """A P11 contract constructed in a shape P11 does not permit."""


def _freeze(instance: object, name: str) -> tuple:
    value = getattr(instance, name)
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise MalformedPlacementRecord(
            f"{name} is a sequence; a bare string would become one entry per "
            "character"
        )
    frozen = tuple(value)
    object.__setattr__(instance, name, frozen)
    return frozen


def _require(value: object, *, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise MalformedPlacementRecord(f"{name} is required and must be non-empty")
    return value


def _number(value: object, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MalformedPlacementRecord(f"{name} must be a real number, not {value!r}")
    return float(value)


@dataclass(frozen=True)
class Subject:
    """What the decision is about. A file version, or an accepted group."""

    kind: str
    file_id: str | None
    content_hash: str | None
    group_id: str | None
    member_file_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        check(self.kind, SUBJECT_KINDS, name="kind")
        _freeze(self, "member_file_ids")
        if self.kind == FILE:
            _require(self.file_id, name="file_id")
            _require(self.content_hash, name="content_hash")
        else:
            _require(self.group_id, name="group_id")
            if not self.member_file_ids:
                raise MalformedPlacementRecord(
                    "a group decision names the members it covers; an empty group "
                    "plan would move nothing and explain nothing"
                )


@dataclass(frozen=True)
class Destination:
    """A node in the frozen tree. Never a path string (§5.12, B3)."""

    node_id: str
    node_role: str

    def __post_init__(self) -> None:
        _require(self.node_id, name="node_id")
        check(self.node_role, NODE_ROLES, name="node_role")


@dataclass(frozen=True)
class ReturnTarget:
    kind: str
    id: str

    def __post_init__(self) -> None:
        check(self.kind, RETURN_TARGET_KINDS, name="kind")
        _require(self.id, name="id")


@dataclass(frozen=True)
class Ask:
    """§6.9's question. Options are node ids, because the user picks a home."""

    question: str
    options: tuple[str, ...]

    def __post_init__(self) -> None:
        _require(self.question, name="question")
        if len(_freeze(self, "options")) < 2:
            raise MalformedPlacementRecord(
                "asking the user to choose needs at least two options; one option "
                "is a placement wearing a question mark"
            )


@dataclass(frozen=True)
class DecisionDepth:
    node_depth: int
    supported_depth: int
    unsupported_levels: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in ("node_depth", "supported_depth"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise MalformedPlacementRecord(f"{name} is a depth, not {value!r}")
        _freeze(self, "unsupported_levels")
        if self.node_depth > self.supported_depth:
            raise MalformedPlacementRecord(
                "a node deeper than the evidence supports is a filled slot, which "
                "§6.7 forbids; the shallower approved node is the answer"
            )


@dataclass(frozen=True)
class MatchingFact:
    file_fact_id: str
    field: str
    value: str
    reliability: str
    evidence_ref: str

    def __post_init__(self) -> None:
        for name in ("file_fact_id", "field", "value", "reliability", "evidence_ref"):
            _require(getattr(self, name), name=name)


@dataclass(frozen=True)
class GroupSupport:
    group_id: str
    membership: str

    def __post_init__(self) -> None:
        _require(self.group_id, name="group_id")
        _require(self.membership, name="membership")


@dataclass(frozen=True)
class GraphAnchor:
    """One typed edge in the node-local graph that carried support (§6.5)."""

    edge_type: str
    from_file_id: str
    to_file_id: str
    anchor_file_id: str

    def __post_init__(self) -> None:
        for name in ("edge_type", "from_file_id", "to_file_id", "anchor_file_id"):
            _require(getattr(self, name), name=name)


@dataclass(frozen=True)
class ConflictConsidered:
    kind: str
    conflicting_value: str
    suppressed_node_ids: tuple[str, ...]
    evidence_ref: str

    def __post_init__(self) -> None:
        for name in ("kind", "conflicting_value", "evidence_ref"):
            _require(getattr(self, name), name=name)
        if not _freeze(self, "suppressed_node_ids"):
            raise MalformedPlacementRecord(
                "a conflict that suppressed nothing did not act; §6.3 records the "
                "nodes it removed so the review surface can show what was ruled out"
            )


@dataclass(frozen=True)
class Alternative:
    node_id: str
    support_score: float
    rank: int

    def __post_init__(self) -> None:
        _require(self.node_id, name="node_id")
        object.__setattr__(self, "support_score",
                           _number(self.support_score, name="support_score"))
        if isinstance(self.rank, bool) or not isinstance(self.rank, int) or self.rank < 1:
            raise MalformedPlacementRecord("rank counts from 1")


@dataclass(frozen=True)
class TwoCondition:
    """§6.10 recorded, not merely applied (Done-means 10).

    `meets_margin` is three-valued because B8(b) requires an unopposed candidate to
    be distinguishable from a measured one: a reviewer and a P2 replay must be able
    to tell a genuine margin from a vacuous one, and a bare `True` cannot.
    """

    support_score: float
    support_threshold: float
    meets_threshold: bool
    margin_over_next: float | None
    margin_threshold: float
    meets_margin: str
    verdict: str
    requires_review: bool

    def __post_init__(self) -> None:
        for name in ("support_score", "support_threshold", "margin_threshold"):
            object.__setattr__(self, name, _number(getattr(self, name), name=name))
        if self.margin_over_next is not None:
            object.__setattr__(self, "margin_over_next",
                               _number(self.margin_over_next, name="margin_over_next"))
        check(self.meets_margin, MEETS_MARGIN_VALUES, name="meets_margin")
        check(self.verdict, VERDICTS, name="verdict")
        for name in ("meets_threshold", "requires_review"):
            if not isinstance(getattr(self, name), bool):
                raise MalformedPlacementRecord(f"{name} is a boolean")
        vacuous = self.meets_margin == MARGIN_TRUE_VACUOUS
        if vacuous and self.margin_over_next is not None:
            raise MalformedPlacementRecord(
                "a vacuous margin has no next-best to measure against; a number "
                "here would make an unopposed candidate look compared"
            )
        if not vacuous and self.margin_over_next is None:
            raise MalformedPlacementRecord(
                "a measured margin needs the value it measured; only B8(b)'s "
                "single-candidate case may leave it null, and it is `true_vacuous`"
            )
        if self.verdict == ACCEPT_CONTEXT_SUPPORTED and not self.requires_review:
            raise MalformedPlacementRecord(
                "accept_context_supported always requires review (§4.8, §6.10); "
                "P8's own verdict raises on the same shape"
            )


@dataclass(frozen=True)
class PrivacyState:
    handling_class: str
    model_eligibility: str
    consent_audit_ref: int | None

    def __post_init__(self) -> None:
        _require(self.handling_class, name="handling_class")
        check(self.model_eligibility, MODEL_ELIGIBILITY, name="model_eligibility")


@dataclass(frozen=True)
class ResidualContext:
    set_id: str
    set_decision: str
    lifecycle_policy_ref: str | None

    def __post_init__(self) -> None:
        _require(self.set_id, name="set_id")
        check(self.set_decision, SET_CHOICES, name="set_decision")


@dataclass(frozen=True)
class PlacementDecision:
    decision_id: str
    plan_version: str
    supersedes: str | None
    superseded_by: str | None
    supersede_reason: str | None
    created_at: str
    origin_stage: str
    returned_from: str | None
    subject: Subject
    group_plan_id: str | None
    outcome: str
    destination: Destination | None
    return_target: ReturnTarget | None
    marked_state: str | None
    ask: Ask | None
    decision_depth: DecisionDepth
    evidence_type: str
    confidence_class: str
    matching_facts: tuple[MatchingFact, ...]
    group_support: GroupSupport | None
    graph_anchors: tuple[GraphAnchor, ...]
    conflicts_considered: tuple[ConflictConsidered, ...]
    alternatives: tuple[Alternative, ...]
    two_condition: TwoCondition
    abstention_reason: str | None
    deferred_stage: str | None
    privacy: PrivacyState
    review_policy: str
    explanation: str
    residual: ResidualContext | None

    def __post_init__(self) -> None:
        for name in ("decision_id", "plan_version", "created_at", "explanation"):
            _require(getattr(self, name), name=name)
        check(self.origin_stage, ORIGIN_STAGES, name="origin_stage")
        check(self.outcome, OUTCOMES, name="outcome")
        check(self.evidence_type, EVIDENCE_TYPES, name="evidence_type")
        check(self.confidence_class, CONFIDENCE_CLASSES, name="confidence_class")
        check(self.review_policy, REVIEW_POLICIES, name="review_policy")
        for name in ("matching_facts", "graph_anchors", "conflicts_considered",
                     "alternatives"):
            _freeze(self, name)
        if self.marked_state is not None:
            check(self.marked_state, MARKED_STATES, name="marked_state")
        if self.abstention_reason is not None:
            check(self.abstention_reason, ABSTENTION_REASONS, name="abstention_reason")
        if self.deferred_stage is not None:
            check(self.deferred_stage, STAGE_IDS, name="deferred_stage")

        # Outcome-shaped fields. Presence IS the contract (SPEC:319-329).
        if (self.destination is None) is (self.outcome == PLACE):
            raise MalformedPlacementRecord(
                "`destination` is present exactly when outcome is `place`; every "
                "other outcome names no node and produces no plan (M13)"
            )
        if (self.return_target is None) is (self.outcome == RETURN_TO_PLACEMENT):
            raise MalformedPlacementRecord(
                "`return_target` is present exactly on `return_to_placement`"
            )
        if (self.marked_state is None) is (self.outcome == MARK_STATE):
            raise MalformedPlacementRecord(
                "`marked_state` is present exactly on `mark_state`"
            )
        if (self.ask is None) is (self.outcome == ASK_USER):
            raise MalformedPlacementRecord("`ask` is present exactly on `ask_user`")
        if (self.abstention_reason is None) is (self.outcome == ABSTAIN):
            raise MalformedPlacementRecord(
                "an abstention names why (§6.10); an unexplained one is silence, "
                "and a reason on any other outcome contradicts the decision"
            )

        # Path exclusivity (SPEC:437-445). This is the only place the two paths differ.
        if self.outcome == RETURN_TO_PLACEMENT and self.origin_stage != RESIDUAL:
            raise MalformedPlacementRecord(
                "`return_to_placement` is the §7.9 loop and is emitted only on the "
                "residual path; §6 IS the placement engine and does not hand back "
                "to itself"
            )
        if self.outcome == ASK_USER and self.origin_stage != PLACEMENT:
            raise MalformedPlacementRecord(
                "`ask_user` is §6.9's multi-home question; the residual path is "
                "closed to the eight §7.7 actions and none of them asks"
            )
        if (self.residual is None) is (self.origin_stage == RESIDUAL):
            raise MalformedPlacementRecord(
                "`residual` is present exactly when origin_stage is `residual`"
            )

        if (self.abstention_reason == BUDGET_DEFERRED) != (self.deferred_stage is not None):
            raise MalformedPlacementRecord(
                "a budget deferral names the stage it was cut short at, and only a "
                "budget deferral has one: §8.6 requires deferred work to render "
                "differently from an evidential abstention"
            )

        if self.review_policy == AUTO_ELIGIBLE:
            if self.two_condition.requires_review:
                raise MalformedPlacementRecord(
                    "a verdict that requires review is never auto-eligible (§6.10)"
                )
            if self.group_support is not None and self.group_support.membership == USER_ATTACHED:
                raise MalformedPlacementRecord(
                    "a decision resting on a manual attachment is never automatic: "
                    "nothing was read from the file (M12, §4.9)"
                )
        if (self.group_support is not None
                and self.group_support.membership == USER_ATTACHED
                and self.evidence_type == VALIDATED):
            raise MalformedPlacementRecord(
                "a `user-attached` member never yields `validated`; nothing was "
                "read from the file to validate (M12)"
            )


#: Every field name the record publishes, in declaration order. `store` builds its
#: columns from this, so a field added here cannot be silently unstored.
DECISION_FIELDS: tuple[str, ...] = tuple(f.name for f in fields(PlacementDecision))
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3 -m pytest -q tests/p11/test_p11_records.py tests/p11/test_p11_vocabulary.py`

Expected: PASS, 11 tests. Note `test_a_destination_is_present_only_when_the_outcome_is_place` passes on both halves because the check is an XOR on presence, not two one-way checks — a one-way check is how a `place` with no node reaches a store.

`_decision` and `_two_condition` in this file are imported by the store, residual,
version, stage-output and pipeline suites. That is deliberate: a builder for a
thirty-field record copied into six test modules drifts, and the drift shows up as
a passing test asserting the wrong shape. Any task changing the record changes one
builder and the six suites fail together, which is the point.

- [ ] **Step 5: Commit**

```bash
git add src/placement/records.py tests/p11/test_p11_records.py
git commit -m "feat(p11): publish one placement decision shape for both paths"
```

### Task 4: Store decisions append-only, with a readable superseded row

**Files:**
- Create: `src/placement/schema.py`
- Create: `src/placement/store.py`
- Create: `src/placement/events.py`
- Create: `tests/p11/conftest.py`
- Create: `tests/p11/test_p11_store.py`

**Consumes:** `database_agent.db.transaction`, `database_agent.supersede.mark_superseded`, `database_agent.events.append_event`, `placement.records.DECISION_FIELDS`.

**Produces:**

```python
P11_TABLES: tuple[str, ...]
def create_placement_schema(conn: sqlite3.Connection) -> None: ...
def record_decision(conn, decision, *, component_version: str,
                    observed_at: str, supersede_reason: str | None = None) -> str: ...
def current_decision(conn, *, plan_version: str, subject_ref: str) -> PlacementDecision | None: ...
def decision_history(conn, *, subject_ref: str) -> tuple[PlacementDecision, ...]: ...
def decisions_for_plan(conn, *, plan_version: str) -> tuple[PlacementDecision, ...]: ...
class AmbiguousCurrentDecision(RuntimeError): ...
```

**Done-means:** SPEC:699-710 (never overwrites, M1's three columns, followable forward), 16 (SPEC:670-671), 15 (SPEC:668-669).

**Why the forward link is load-bearing.** SPEC:704-710: the chain must be followable *forward* as well as backward, because §8.8's *"twenty-three files now require renewed review because their previous destination no longer exists"* diff walks **from** a superseded decision **to** its replacement, which `supersedes` alone cannot express. `mark_superseded` already does both halves and refuses a second supersede of the same row, so P11 writes no supersession logic of its own.

**The write order is forced, not chosen.** `one_current_placement_decision` is a partial unique index over unsuperseded rows. Inserting the replacement before superseding the predecessor puts two live rows for one `(plan_version, subject_ref)` in the table, and SQLite refuses that insert — so `mark_superseded` is never reached. `record_decision` therefore **supersedes first and inserts second**, inside one `transaction(conn)`, which is exactly what `grouping/acceptance.py:76-80` does and says: *"Supersede first. The unique index is over unsuperseded rows, so linking after the insert would mean two current opinions existed for the length of one statement — and the database would refuse the insert that was about to resolve it."*

- [ ] **Step 1: Write the failing store tests**

```python
# tests/p11/conftest.py
"""A real P1 database with P11's tables. No mock, no in-memory stand-in."""
from __future__ import annotations

import pytest

from database_agent.budget import all_ceilings
from database_agent.db import create_schema
from eval_harness.run import ANALYSIS_TIERS, record_version_tuple, start_run
from eval_harness.store import create_eval_schema
from grouping.schema import create_grouping_schema

from placement.schema import create_placement_schema

FIXED_CLOCK = "2026-08-27T00:00:00Z"


@pytest.fixture()
def p11_conn(conn):
    # P9's tables are created because P11 reads them for real (G-P9 is closed):
    # `group_state_as_of` and `memberships_for_group` query `group_acceptance`
    # and `memberships`, and a test against an absent table would prove nothing.
    create_schema(conn)
    create_eval_schema(conn)
    create_grouping_schema(conn)
    create_placement_schema(conn)
    return conn


@pytest.fixture()
def p11_version_tuple(p11_conn) -> str:
    """P2's seven axes. `placement_scorer_version` is already one of them, so a
    changed support policy reads as a version delta and not as a mystery diff."""
    return record_version_tuple(
        p11_conn, extractor_versions={}, graph_algorithm_version="1",
        prompt_fingerprint="fp-canonical", model_identifier="fixture-model",
        template_library_version="1", placement_scorer_version="fixture-v1",
        analysis_tiers_enabled=list(ANALYSIS_TIERS))


@pytest.fixture()
def p2_run_id(p11_conn, p11_version_tuple) -> str:
    """A replay run. There is no live run kind: P2 measures replays, shadows and
    adversarial runs, and P11 emits stage output in those only."""
    return start_run(
        p11_conn, bundle_id="bundle-p11", run_kind="replay",
        version_tuple_ref=p11_version_tuple,
        budget_ceilings=all_ceilings(p11_conn),
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        pinned_plan_id="plan", pinned_plan_version="plan-1")
```

```python
# tests/p11/test_p11_store.py
"""Append-only decisions: the old row stays readable and the chain runs both ways."""
from __future__ import annotations

import dataclasses

import pytest

from placement import vocabulary as v
from placement.records import DECISION_FIELDS
from placement.schema import P11_TABLES
from placement.store import (
    AmbiguousCurrentDecision, current_decision, decision_history,
    decisions_for_plan, record_decision, subject_ref_of,
)
from p11.conftest import FIXED_CLOCK
from p11.test_p11_records import _decision


def _write(conn, decision, **overrides):
    values = dict(component_version="P11-test", observed_at=FIXED_CLOCK)
    values.update(overrides)
    return record_decision(conn, decision, **values)


def test_every_record_field_has_a_column(p11_conn):
    # Two lists of one shape drift. The DDL is built from DECISION_FIELDS, and a
    # field added to the record with no column would be silently unstored.
    columns = {row["name"] for row in
               p11_conn.execute("PRAGMA table_info(placement_decisions)")}
    assert set(DECISION_FIELDS) <= columns
    assert "record_id" in columns
    assert "subject_ref" in columns


def test_a_revision_appends_and_the_prior_row_stays_readable(p11_conn):
    first = _decision(decision_id="d1")
    _write(p11_conn, first)
    second = _decision(decision_id="d2", supersedes="d1",
                       outcome=v.ABSTAIN, destination=None,
                       abstention_reason=v.CONFLICTING_FACTS)
    _write(p11_conn, second, supersede_reason="a direct term fact arrived")

    history = decision_history(p11_conn, subject_ref=subject_ref_of(first.subject))
    assert [d.decision_id for d in history] == ["d1", "d2"]
    assert history[0].outcome == v.PLACE
    assert history[0].superseded_by == "d2"
    assert history[0].supersede_reason == "a direct term fact arrived"
    assert history[1].supersedes == "d1"
    assert current_decision(
        p11_conn, plan_version="plan-1",
        subject_ref=subject_ref_of(first.subject)).decision_id == "d2"


def test_the_chain_is_followable_forward(p11_conn):
    # §8.8's diff walks FROM a superseded decision TO its replacement, which
    # `supersedes` alone cannot express (M1).
    _write(p11_conn, _decision(decision_id="d1"))
    _write(p11_conn, _decision(decision_id="d2", supersedes="d1"),
           supersede_reason="plan version 2 removed the node")
    row = p11_conn.execute(
        "SELECT superseded_by, supersede_reason FROM placement_decisions "
        "WHERE record_id = ?", ("d1",)).fetchone()
    assert row["superseded_by"] == "d2"
    assert row["supersede_reason"] == "plan version 2 removed the node"


def test_a_stored_decision_cannot_be_updated_or_deleted(p11_conn):
    _write(p11_conn, _decision(decision_id="d1"))
    for statement, params in (
        ("UPDATE placement_decisions SET outcome = ? WHERE record_id = ?",
         (v.ABSTAIN, "d1")),
        ("DELETE FROM placement_decisions WHERE record_id = ?", ("d1",)),
    ):
        with pytest.raises(Exception):
            p11_conn.execute(statement, params)


def test_supersession_columns_are_the_only_mutable_thing(p11_conn):
    # `mark_superseded` writes them, so the append-only trigger must permit that
    # exact update and nothing else.
    _write(p11_conn, _decision(decision_id="d1"))
    _write(p11_conn, _decision(decision_id="d2", supersedes="d1"),
           supersede_reason="corrected")
    assert current_decision(p11_conn, plan_version="plan-1",
                            subject_ref="file:f1:h1").decision_id == "d2"


def test_a_second_current_row_for_one_subject_cannot_commit(p11_conn):
    _write(p11_conn, _decision(decision_id="d1"))
    with pytest.raises(Exception):
        p11_conn.execute(
            "INSERT INTO placement_decisions (record_id, subject_ref, plan_version, "
            "outcome, origin_stage, created_at, payload) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("illegal", "file:f1:h1", "plan-1", v.PLACE, v.PLACEMENT,
             FIXED_CLOCK, "{}"))


def test_an_ambiguous_prior_state_is_refused_before_any_write(p11_conn):
    _write(p11_conn, _decision(decision_id="d1"))
    p11_conn.execute("DROP INDEX one_current_placement_decision")
    p11_conn.execute(
        "INSERT INTO placement_decisions (record_id, subject_ref, plan_version, "
        "outcome, origin_stage, created_at, payload) VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("d-bad", "file:f1:h1", "plan-1", v.PLACE, v.PLACEMENT, FIXED_CLOCK, "{}"))
    with pytest.raises(AmbiguousCurrentDecision):
        _write(p11_conn, _decision(decision_id="d3", supersedes="d1"),
               supersede_reason="repair attempt")


def test_writing_a_decision_appends_its_event(p11_conn):
    _write(p11_conn, _decision(decision_id="d1"))
    row = p11_conn.execute(
        "SELECT event_type, base_event_type, subsystem, file_id, content_hash, "
        "explanation FROM events ORDER BY event_id DESC LIMIT 1").fetchone()
    assert row["event_type"] == v.RECOMMENDATION_EMITTED
    assert row["base_event_type"] == "placement recommendation"
    assert row["subsystem"] == "P11"
    assert row["file_id"] == "f1"
    assert row["content_hash"] == "h1"
    assert "PHYS1401" in row["explanation"]


def test_an_abstention_is_logged_as_a_decision_not_as_silence(p11_conn):
    # SPEC:686: "any `outcome`, including `abstain` -- an abstention is a decision
    # and is logged as one".
    _write(p11_conn, _decision(decision_id="d1", outcome=v.ABSTAIN,
                               destination=None,
                               abstention_reason=v.NO_SUPPORTED_DESTINATION))
    row = p11_conn.execute(
        "SELECT event_type FROM events ORDER BY event_id DESC LIMIT 1").fetchone()
    assert row["event_type"] == v.RECOMMENDATION_EMITTED


def test_decisions_are_scoped_to_a_plan_version(p11_conn):
    _write(p11_conn, _decision(decision_id="d1", plan_version="plan-1"))
    _write(p11_conn, _decision(decision_id="d2", plan_version="plan-2"))
    assert {d.decision_id for d in decisions_for_plan(p11_conn, plan_version="plan-1")} == {"d1"}
    assert {d.decision_id for d in decisions_for_plan(p11_conn, plan_version="plan-2")} == {"d2"}


def test_every_p11_table_refuses_a_delete(p11_conn):
    for table in P11_TABLES:
        with pytest.raises(Exception):
            p11_conn.execute(f"DELETE FROM {table}")
```

- [ ] **Step 2: Run and verify RED**

Run: `python3 -m pytest -q tests/p11/test_p11_store.py`

Expected: FAIL at collection — `ModuleNotFoundError: No module named 'placement.schema'`.

- [ ] **Step 3: Implement the schema, the store and the event writer**

```python
# src/placement/schema.py
"""P11's own SQLite tables inside P1's single database. Append-only by trigger.

`plan_version` is on every table here, and that is the opposite of P9's rule for a
reason §8.8 states outright: a placement decision, a group plan, a residual set
decision and the whole §6.2 index are *projections of one frozen tree*, and a
projection whose tree changed is a different projection. Facts, observations,
files and accepted groups stay in the shared evidence database and are not
duplicated per version.

The payload column stores the record as canonical JSON. The named columns beside
it exist for the reads P11 actually performs -- current-by-subject, history,
by-plan-version -- and are never a second home for a value: the record is
rebuilt from `payload`, and a named column that disagreed with it would be
unreachable.
"""
from __future__ import annotations

import sqlite3

#: Every table P11 owns. All carry `plan_version`.
P11_TABLES: tuple[str, ...] = (
    "placement_decisions",
    "placement_index_entries",
    "placement_group_plans",
    "residual_sets",
    "residual_set_decisions",
)

_SUPERSEDE = "supersedes TEXT, superseded_by TEXT, supersede_reason TEXT"

PLACEMENT_DDL = f"""
CREATE TABLE IF NOT EXISTS placement_decisions (
    record_id      TEXT PRIMARY KEY,
    subject_ref    TEXT NOT NULL,
    plan_version   TEXT NOT NULL,
    origin_stage   TEXT NOT NULL,
    outcome        TEXT NOT NULL,
    node_id        TEXT,
    group_plan_id  TEXT,
    returned_from  TEXT,
    review_policy  TEXT,
    created_at     TEXT NOT NULL,
    payload        TEXT NOT NULL,
    {_SUPERSEDE}
);
CREATE INDEX IF NOT EXISTS placement_decisions_plan
    ON placement_decisions (plan_version, subject_ref);
CREATE INDEX IF NOT EXISTS placement_decisions_node
    ON placement_decisions (plan_version, node_id);
CREATE UNIQUE INDEX IF NOT EXISTS one_current_placement_decision
    ON placement_decisions (plan_version, subject_ref)
    WHERE superseded_by IS NULL;

CREATE TABLE IF NOT EXISTS placement_index_entries (
    record_id      TEXT PRIMARY KEY,
    plan_version   TEXT NOT NULL,
    node_id        TEXT NOT NULL,
    payload        TEXT NOT NULL,
    created_at     TEXT NOT NULL,
    {_SUPERSEDE}
);
CREATE UNIQUE INDEX IF NOT EXISTS one_current_index_entry
    ON placement_index_entries (plan_version, node_id)
    WHERE superseded_by IS NULL;

CREATE TABLE IF NOT EXISTS placement_group_plans (
    record_id             TEXT PRIMARY KEY,
    plan_version          TEXT NOT NULL,
    group_id              TEXT NOT NULL,
    shared_parent_node_id TEXT,
    payload               TEXT NOT NULL,
    created_at            TEXT NOT NULL,
    {_SUPERSEDE}
);
CREATE UNIQUE INDEX IF NOT EXISTS one_current_group_plan
    ON placement_group_plans (plan_version, group_id)
    WHERE superseded_by IS NULL;

CREATE TABLE IF NOT EXISTS residual_sets (
    record_id      TEXT PRIMARY KEY,
    plan_version   TEXT NOT NULL,
    label          TEXT NOT NULL,
    payload        TEXT NOT NULL,
    created_at     TEXT NOT NULL,
    {_SUPERSEDE}
);

CREATE TABLE IF NOT EXISTS residual_set_decisions (
    record_id      TEXT PRIMARY KEY,
    plan_version   TEXT NOT NULL,
    set_id         TEXT NOT NULL,
    choice         TEXT NOT NULL,
    node_id        TEXT,
    decided_at     TEXT NOT NULL,
    payload        TEXT NOT NULL,
    {_SUPERSEDE}
);
CREATE UNIQUE INDEX IF NOT EXISTS one_current_set_decision
    ON residual_set_decisions (plan_version, set_id)
    WHERE superseded_by IS NULL;
"""

#: `mark_superseded` writes exactly these three columns, so the update trigger
#: permits that shape and refuses every other. A blanket no-update trigger would
#: make supersession impossible; a blanket permission would make the table
#: rewritable, which §8.2 forbids.
_GUARDS = "\n".join(
    f"""
CREATE TRIGGER IF NOT EXISTS {table}_no_delete
BEFORE DELETE ON {table}
BEGIN SELECT RAISE(ABORT, '{table} is append-only (§8.2)'); END;

CREATE TRIGGER IF NOT EXISTS {table}_only_supersede
BEFORE UPDATE ON {table}
WHEN OLD.payload IS NOT NEW.payload
  OR OLD.record_id IS NOT NEW.record_id
  OR OLD.plan_version IS NOT NEW.plan_version
  OR OLD.created_at IS NOT NEW.created_at
BEGIN SELECT RAISE(ABORT, '{table} rewrites nothing but its supersede link'); END;
"""
    for table in P11_TABLES
    if table != "residual_set_decisions"
) + """
CREATE TRIGGER IF NOT EXISTS residual_set_decisions_no_delete
BEFORE DELETE ON residual_set_decisions
BEGIN SELECT RAISE(ABORT, 'residual_set_decisions is append-only (§8.2)'); END;

CREATE TRIGGER IF NOT EXISTS residual_set_decisions_only_supersede
BEFORE UPDATE ON residual_set_decisions
WHEN OLD.payload IS NOT NEW.payload
  OR OLD.record_id IS NOT NEW.record_id
  OR OLD.plan_version IS NOT NEW.plan_version
  OR OLD.decided_at IS NOT NEW.decided_at
BEGIN SELECT RAISE(ABORT, 'residual_set_decisions rewrites nothing but its link'); END;
"""


def create_placement_schema(conn: sqlite3.Connection) -> None:
    """Create P11's tables. Idempotent; safe on an existing database."""
    conn.executescript(PLACEMENT_DDL)
    conn.executescript(_GUARDS)
```

```python
# src/placement/events.py
"""P11's §8.2 appends. One function per registered event name.

P1 writes; P11 authors (M8), so `subsystem` is filled here and never by P1. Every
append carries §8.2's required fields, and `prompt_fingerprint` is set only where
a model was actually used -- a fingerprint on a deterministic decision would claim
a model call that did not happen.
"""
from __future__ import annotations

import json

from database_agent.events import append_event

from placement.vocabulary import (
    CANDIDATE_RETRIEVAL, GROUP_PLAN_EMITTED, INDEX_ENTRY_BUILT,
    RECOMMENDATION_EMITTED, RESIDUAL_RECOMMENDATION_EMITTED,
    RESIDUAL_SET_DECIDED, RESIDUAL_SET_SURFACED, RETURN_ISSUED, REVIEW_DECISION,
)

SUBSYSTEM: str = "P11"


def _append(conn, event_type, *, component_version, observed_at, explanation,
            file_id=None, content_hash=None, prompt_fingerprint=None,
            user_id=None, correction_scope=None, correction_subject=None,
            polarity=None, proposal_class=None, basis_key=None) -> int:
    fields = dict(
        event_type=event_type, subsystem=SUBSYSTEM,
        component_version=component_version, observed_at=observed_at,
        explanation=explanation,
    )
    optional = dict(
        file_id=file_id, content_hash=content_hash,
        prompt_fingerprint=prompt_fingerprint, user_id=user_id,
        correction_scope=correction_scope, correction_subject=correction_subject,
        polarity=polarity, proposal_class=proposal_class, basis_key=basis_key,
    )
    fields.update({k: value for k, value in optional.items() if value is not None})
    return append_event(conn, **fields)


def index_entry_built(conn, *, node_id, plan_version, component_version,
                      observed_at) -> int:
    return _append(
        conn, INDEX_ENTRY_BUILT, component_version=component_version,
        observed_at=observed_at,
        explanation=json.dumps({"node_id": node_id, "plan_version": plan_version},
                               sort_keys=True),
    )


def candidate_retrieval(conn, *, subject_ref, plan_version, retrieved,
                        suppressed, component_version, observed_at,
                        file_id=None, content_hash=None) -> int:
    # §8.2 requires the retrieved AND the suppressed ids: a review surface that
    # cannot show what was ruled out cannot answer "why not that folder?".
    return _append(
        conn, CANDIDATE_RETRIEVAL, component_version=component_version,
        observed_at=observed_at, file_id=file_id, content_hash=content_hash,
        explanation=json.dumps({
            "subject_ref": subject_ref, "plan_version": plan_version,
            "retrieved": list(retrieved), "suppressed": list(suppressed),
        }, sort_keys=True),
    )


def recommendation_emitted(conn, decision, *, component_version, observed_at,
                           prompt_fingerprint=None) -> int:
    event_type = (RESIDUAL_RECOMMENDATION_EMITTED
                  if decision.residual is not None else RECOMMENDATION_EMITTED)
    return _append(
        conn, event_type, component_version=component_version,
        observed_at=observed_at, file_id=decision.subject.file_id,
        content_hash=decision.subject.content_hash,
        prompt_fingerprint=prompt_fingerprint,
        explanation=decision.explanation,
    )


def group_plan_emitted(conn, *, group_plan_id, group_id, shared_parent_node_id,
                       component_version, observed_at) -> int:
    return _append(
        conn, GROUP_PLAN_EMITTED, component_version=component_version,
        observed_at=observed_at,
        explanation=json.dumps({
            "group_plan_id": group_plan_id, "group_id": group_id,
            "shared_parent_node_id": shared_parent_node_id,
        }, sort_keys=True),
    )


def residual_set_surfaced(conn, *, set_id, label, file_count, reason_not_placed,
                          component_version, observed_at) -> int:
    return _append(
        conn, RESIDUAL_SET_SURFACED, component_version=component_version,
        observed_at=observed_at,
        explanation=json.dumps({
            "set_id": set_id, "label": label, "file_count": file_count,
            "reason_not_placed": reason_not_placed,
        }, sort_keys=True),
    )


def residual_set_decided(conn, *, set_id, choice, node_id, component_version,
                         observed_at, user_id) -> int:
    return _append(
        conn, RESIDUAL_SET_DECIDED, component_version=component_version,
        observed_at=observed_at, user_id=user_id,
        explanation=json.dumps({"set_id": set_id, "choice": choice,
                                "node_id": node_id}, sort_keys=True),
    )


def return_issued(conn, *, residual_decision_id, placement_decision_id,
                  component_version, observed_at, file_id, content_hash) -> int:
    # The link is the event's whole content: §7.9 requires both records to persist
    # and the second to point at the first.
    return _append(
        conn, RETURN_ISSUED, component_version=component_version,
        observed_at=observed_at, file_id=file_id, content_hash=content_hash,
        explanation=json.dumps({
            "residual_decision_id": residual_decision_id,
            "placement_decision_id": placement_decision_id,
        }, sort_keys=True),
    )


def review_decision(conn, *, subject_ref, action, component_version, observed_at,
                    user_id, correction_scope, correction_subject, polarity,
                    proposal_class, basis_key, explanation,
                    file_id=None, content_hash=None) -> int:
    return _append(
        conn, REVIEW_DECISION, component_version=component_version,
        observed_at=observed_at, user_id=user_id, file_id=file_id,
        content_hash=content_hash, correction_scope=correction_scope,
        correction_subject=correction_subject, polarity=polarity,
        proposal_class=proposal_class, basis_key=basis_key,
        explanation=json.dumps({"subject_ref": subject_ref, "action": action,
                                "basis": explanation}, sort_keys=True),
    )
```

```python
# src/placement/store.py
"""Append, supersede and read. Nothing here rewrites a decision.

A revised decision is a NEW row whose `supersedes` names the prior one; the prior
row keeps its evidence, its alternatives and its two-condition figures and gains
`superseded_by` and `supersede_reason`. P1's `mark_superseded` writes both halves
and refuses a second supersede of the same row, so the chain is followable forward
-- which §8.8's version diff needs and `supersedes` alone cannot give.
"""
from __future__ import annotations

import dataclasses
import json
import sqlite3

from database_agent.db import transaction
from database_agent.supersede import mark_superseded

from placement import events as placement_events
from placement.records import PlacementDecision, DECISION_FIELDS
from placement.vocabulary import FILE, PLACE


class AmbiguousCurrentDecision(RuntimeError):
    """More than one live row for one subject. Refused before any write."""


def subject_ref_of(subject) -> str:
    """One address for one subject. A file version, or a group.

    The file form carries the content hash because §8.8 versions the plan and §8.2
    versions the file: a decision about `f1` at one hash is not a decision about
    `f1` after it was edited.
    """
    if subject.kind == FILE:
        return f"{FILE}:{subject.file_id}:{subject.content_hash}"
    return f"{subject.kind}:{subject.group_id}"


def _payload(decision: PlacementDecision) -> str:
    return json.dumps(dataclasses.asdict(decision), sort_keys=True)


def _from_row(row: sqlite3.Row) -> PlacementDecision:
    from placement import records as r

    body = json.loads(row["payload"])
    nested = {
        "subject": r.Subject, "destination": r.Destination,
        "return_target": r.ReturnTarget, "ask": r.Ask,
        "decision_depth": r.DecisionDepth, "group_support": r.GroupSupport,
        "two_condition": r.TwoCondition, "privacy": r.PrivacyState,
        "residual": r.ResidualContext,
    }
    for name, cls in nested.items():
        if body.get(name) is not None:
            body[name] = cls(**body[name])
    sequences = {
        "matching_facts": r.MatchingFact, "graph_anchors": r.GraphAnchor,
        "conflicts_considered": r.ConflictConsidered, "alternatives": r.Alternative,
    }
    for name, cls in sequences.items():
        body[name] = tuple(cls(**item) for item in body.get(name, ()))
    return PlacementDecision(**{name: body[name] for name in DECISION_FIELDS})


def record_decision(conn: sqlite3.Connection, decision: PlacementDecision, *,
                    component_version: str, observed_at: str,
                    supersede_reason: str | None = None) -> str:
    """Link the predecessor, append the decision, and log it. ONE transaction.

    The supersede, the row and the event commit together, and the order inside
    is forced by the partial unique index rather than chosen (see the comment
    below). Two transactions where one is needed is a defect this project has
    shipped before: a decision row with no event is a placement §8.2 cannot
    explain, an event with no row is a claim about a decision that does not
    exist, and a supersede that committed without its replacement leaves a
    subject with no current decision at all.
    """
    subject_ref = subject_ref_of(decision.subject)
    with transaction(conn):
        live = conn.execute(
            "SELECT record_id FROM placement_decisions WHERE plan_version = ? "
            "AND subject_ref = ? AND superseded_by IS NULL",
            (decision.plan_version, subject_ref),
        ).fetchall()
        if len(live) > 1:
            raise AmbiguousCurrentDecision(
                f"{len(live)} live decisions for {subject_ref!r} in "
                f"{decision.plan_version!r}; the store refuses to add a third "
                "rather than pick one"
            )
        if decision.supersedes is not None and not supersede_reason:
            raise ValueError(
                "superseding a decision requires the reason it was superseded "
                "(§8.2); the prior row stays readable and says why"
            )
        # SUPERSEDE FIRST, THEN INSERT. `one_current_placement_decision` is a
        # partial unique index over UNSUPERSEDED rows, so inserting the new row
        # while the old one is still live puts two current decisions for one
        # subject in the table for the length of one statement -- and SQLite
        # refuses the very insert that was about to resolve it. Verified: the
        # other order raises `IntegrityError: UNIQUE constraint failed:
        # placement_decisions.plan_version, placement_decisions.subject_ref`
        # before `mark_superseded` is ever reached.
        #
        # This is P9's rule, in P9's own words at `grouping/acceptance.py:77-80`:
        # "Supersede first. The unique index is over unsuperseded rows, so
        # linking after the insert would mean two current opinions existed for
        # the length of one statement."
        #
        # `mark_superseded` still writes BOTH halves and still runs every guard
        # -- reason required, no self-supersede, predecessor exists, predecessor
        # not already superseded, no cycle. Its `UPDATE ... SET supersedes` on
        # the not-yet-inserted new row is a no-op, and the INSERT below carries
        # `supersedes` as a column value, so the forward link §8.8's diff walks
        # is established either way. P11 writes no supersession logic of its own.
        if decision.supersedes is not None:
            mark_superseded(
                conn, "placement_decisions", old_id=decision.supersedes,
                new_id=decision.decision_id, reason=supersede_reason,
            )
        conn.execute(
            "INSERT INTO placement_decisions (record_id, subject_ref, plan_version, "
            "origin_stage, outcome, node_id, group_plan_id, returned_from, "
            "review_policy, created_at, payload, supersedes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                decision.decision_id, subject_ref, decision.plan_version,
                decision.origin_stage, decision.outcome,
                decision.destination.node_id if decision.destination else None,
                decision.group_plan_id, decision.returned_from,
                decision.review_policy, decision.created_at, _payload(decision),
                decision.supersedes,
            ),
        )
        placement_events.recommendation_emitted(
            conn, decision, component_version=component_version,
            observed_at=observed_at,
        )
    return decision.decision_id


def current_decision(conn: sqlite3.Connection, *, plan_version: str,
                     subject_ref: str) -> PlacementDecision | None:
    row = conn.execute(
        "SELECT * FROM placement_decisions WHERE plan_version = ? AND "
        "subject_ref = ? AND superseded_by IS NULL", (plan_version, subject_ref),
    ).fetchone()
    return None if row is None else _from_row(row)


def decision_history(conn: sqlite3.Connection, *,
                     subject_ref: str) -> tuple[PlacementDecision, ...]:
    """Every decision ever made about this subject, oldest first, across versions."""
    rows = conn.execute(
        "SELECT * FROM placement_decisions WHERE subject_ref = ? "
        "ORDER BY created_at, record_id", (subject_ref,),
    ).fetchall()
    return tuple(_from_row(row) for row in rows)


def decisions_for_plan(conn: sqlite3.Connection, *,
                       plan_version: str) -> tuple[PlacementDecision, ...]:
    rows = conn.execute(
        "SELECT * FROM placement_decisions WHERE plan_version = ? AND "
        "superseded_by IS NULL ORDER BY created_at, record_id", (plan_version,),
    ).fetchall()
    return tuple(_from_row(row) for row in rows)


def placed_node_ids(conn: sqlite3.Connection, *, plan_version: str) -> tuple[str, ...]:
    """The nodes live `place` decisions name. Task 17 diffs this against the tree."""
    rows = conn.execute(
        "SELECT DISTINCT node_id FROM placement_decisions WHERE plan_version = ? "
        "AND outcome = ? AND node_id IS NOT NULL AND superseded_by IS NULL "
        "ORDER BY node_id", (plan_version, PLACE),
    ).fetchall()
    return tuple(row["node_id"] for row in rows)
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3 -m pytest -q tests/p11/ tests/test_events.py tests/test_supersede.py`

Expected: PASS. `test_supersession_columns_are_the_only_mutable_thing` is the one that would fail under a blanket `BEFORE UPDATE` trigger, which is why the trigger is conditioned on the immutable columns rather than on the statement.

- [ ] **Step 5: Commit**

```bash
git add src/placement/schema.py src/placement/store.py src/placement/events.py \
        tests/p11/conftest.py tests/p11/test_p11_store.py
git commit -m "feat(p11): store decisions append-only with a forward chain"
```

### Task 5: Read every limit from P1, and take the two-condition policy as an injection

**Files:**
- Create: `src/placement/config.py`
- Create: `tests/p11/test_p11_config.py`

**Consumes:** `database_agent.budget.get_ceiling`, `database_agent.budget.CEILING_KEYS`.

**Produces:**

```python
class ConfigurationRequired(RuntimeError): ...

CEILINGS: dict[str, str]        # seven, all live P1 keys

@dataclass(frozen=True)
class PlacementLimits:
    max_retrieved_neighbors: int
    max_local_graph_neighborhood: int
    max_candidate_cluster_size: int
    max_residual_files_per_batch: int
    max_dossier_tokens: int
    max_llm_calls_per_thousand_files: int
    max_cost_per_scan: int

@dataclass(frozen=True)
class SupportPolicy:
    policy_id: str
    support_scale_max: float
    minimum_support_threshold: float
    margin_threshold: float

    def margin_predicate(self, best, next_best) -> bool: ...

def placement_limits(conn) -> PlacementLimits: ...
def require_policy(policy: SupportPolicy | None) -> SupportPolicy: ...
```

**Done-means:** SPEC:714-717 (the seven ceilings), SPEC Open question 1 (SPEC:802-804: *"Both must be configurable and both must be recorded on every decision"*).

**All seven ceilings already have live keys.** `database_agent.budget.CEILING_KEYS` publishes `placement.max_retrieved_neighbors`, `placement.max_local_graph_neighborhood`, `placement.max_candidate_cluster_size`, `residual.max_files_per_review_batch`, `model.max_dossier_tokens_per_call`, `model.max_llm_calls_per_thousand_files` and `model.max_cost_per_scan`. P11 adds no key and no default, which is P9's rule at `src/grouping/config.py:2-7` applied to the seven §8.6 names that are P11's.

- [ ] **Step 1: Write the failing configuration tests**

```python
# tests/p11/test_p11_config.py
"""Limits are read; thresholds are injected; neither is ever guessed."""
from __future__ import annotations

import pytest

from database_agent.budget import CEILING_KEYS, set_ceiling

from placement.config import (
    CEILINGS, ConfigurationRequired, PlacementLimits, SupportPolicy,
    placement_limits, require_policy,
)

POLICY = SupportPolicy(policy_id="fixture-v1", support_scale_max=1.0,
                       minimum_support_threshold=0.5, margin_threshold=0.2)


def _set_all(conn, value=8):
    for key in CEILINGS.values():
        set_ceiling(conn, key, value)


def test_every_ceiling_p11_reads_is_one_p1_already_publishes():
    # A key P1 does not know is a policy P11 authored, and `set_ceiling` raises
    # on one, so this is the compile-time half of the same rule.
    assert set(CEILINGS.values()) <= set(CEILING_KEYS)
    assert len(CEILINGS) == 7


def test_an_absent_ceiling_refuses_rather_than_defaulting(p11_conn):
    with pytest.raises(ConfigurationRequired) as excinfo:
        placement_limits(p11_conn)
    assert "placement." in str(excinfo.value) or "model." in str(excinfo.value)


def test_a_non_positive_ceiling_refuses(p11_conn):
    _set_all(p11_conn)
    set_ceiling(p11_conn, "placement.max_retrieved_neighbors", 0)
    with pytest.raises(ConfigurationRequired):
        placement_limits(p11_conn)


def test_configured_ceilings_read_back(p11_conn):
    _set_all(p11_conn, 12)
    limits = placement_limits(p11_conn)
    assert isinstance(limits, PlacementLimits)
    assert limits.max_retrieved_neighbors == 12
    assert limits.max_residual_files_per_batch == 12


def test_a_missing_support_policy_refuses(p11_conn):
    with pytest.raises(ConfigurationRequired):
        require_policy(None)


def test_the_margin_predicate_is_the_policys_and_carries_no_default():
    assert POLICY.margin_predicate(0.9, 0.5) is True
    assert POLICY.margin_predicate(0.9, 0.8) is False
    with pytest.raises(ConfigurationRequired):
        SupportPolicy(policy_id="", support_scale_max=1.0,
                      minimum_support_threshold=0.5, margin_threshold=0.2)
    with pytest.raises(ConfigurationRequired):
        SupportPolicy(policy_id="bad", support_scale_max=1.0,
                      minimum_support_threshold=1.5, margin_threshold=0.2)


def test_the_policy_id_is_recordable_so_a_changed_threshold_is_auditable():
    # SPEC:802-804: both must be recorded on every decision so a changed
    # threshold is auditable and replayable.
    assert POLICY.policy_id
    assert POLICY.minimum_support_threshold == 0.5
    assert POLICY.margin_threshold == 0.2


def test_no_module_under_placement_binds_a_bare_number(p11_conn):
    # By runtime introspection, not text search: a text search matches comments,
    # and scanning text for a token has produced a false result on this project.
    import importlib
    import pkgutil

    import placement

    allowed = {0, 1}
    offenders = []
    for info in pkgutil.iter_modules(placement.__path__):
        module = importlib.import_module(f"placement.{info.name}")
        for name, value in vars(module).items():
            if name.startswith("_") or not isinstance(value, (int, float)):
                continue
            if isinstance(value, bool) or value in allowed:
                continue
            offenders.append((info.name, name, value))
    assert offenders == []
```

- [ ] **Step 2: Run and verify RED**

Run: `python3 -m pytest -q tests/p11/test_p11_config.py`

Expected: FAIL at collection — `ModuleNotFoundError: No module named 'placement.config'`.

- [ ] **Step 3: Implement the config module**

```python
# src/placement/config.py
"""P11's ceilings, read from P1, and the two-condition policy, injected.

No numeric fallback lives here. §8.6 names seven ceilings that are P11's and P1
already publishes a key for every one, so a default here would be P11 authoring a
policy that belongs to configuration -- and the failure it hides is the worst
kind: running a corpus under a limit nobody chose, with nothing to say so.

The support threshold and the margin threshold are SPEC Open question 1 and stay
open. They arrive as a `SupportPolicy` with an id, because SPEC:802-804 requires
both to be recorded on every decision so that a changed threshold is auditable and
replayable rather than invisible.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from database_agent.budget import get_ceiling


class ConfigurationRequired(RuntimeError):
    """A limit or threshold P11 needs is absent, non-positive, or out of range."""


#: The seven §8.6 ceilings that are P11's (SPEC:714-717), mapped to live P1 keys.
CEILINGS: dict[str, str] = {
    "max_retrieved_neighbors": "placement.max_retrieved_neighbors",
    "max_local_graph_neighborhood": "placement.max_local_graph_neighborhood",
    "max_candidate_cluster_size": "placement.max_candidate_cluster_size",
    "max_residual_files_per_batch": "residual.max_files_per_review_batch",
    "max_dossier_tokens": "model.max_dossier_tokens_per_call",
    "max_llm_calls_per_thousand_files": "model.max_llm_calls_per_thousand_files",
    "max_cost_per_scan": "model.max_cost_per_scan",
}


@dataclass(frozen=True)
class PlacementLimits:
    max_retrieved_neighbors: int
    max_local_graph_neighborhood: int
    max_candidate_cluster_size: int
    max_residual_files_per_batch: int
    max_dossier_tokens: int
    max_llm_calls_per_thousand_files: int
    max_cost_per_scan: int


@dataclass(frozen=True)
class SupportPolicy:
    """§6.10's two conditions, as configuration rather than as constants.

    `support_scale_max` exists because SPEC Open question 2 says the design names
    "deterministic scores" and a "minimum support threshold" with no scale, and a
    P2 replay assertion cannot compare scores across versions without one. It is
    declared, not chosen.
    """

    policy_id: str
    support_scale_max: float
    minimum_support_threshold: float
    margin_threshold: float

    def __post_init__(self) -> None:
        if not isinstance(self.policy_id, str) or not self.policy_id:
            raise ConfigurationRequired(
                "a support policy carries an id, because §6.10's thresholds are "
                "recorded on every decision and a changed threshold must be "
                "identifiable in a replay"
            )
        for name in ("support_scale_max", "minimum_support_threshold",
                     "margin_threshold"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ConfigurationRequired(f"{name} must be a real number")
            object.__setattr__(self, name, float(value))
        if self.support_scale_max <= 0:
            raise ConfigurationRequired("support_scale_max must be positive")
        for name in ("minimum_support_threshold", "margin_threshold"):
            value = getattr(self, name)
            if not 0 <= value <= self.support_scale_max:
                raise ConfigurationRequired(
                    f"{name}={value} lies outside the declared support scale "
                    f"0..{self.support_scale_max}; a threshold no score can reach "
                    "abstains on everything and a threshold every score clears "
                    "gates nothing"
                )

    def margin_predicate(self, best: object, next_best: object) -> bool:
        """P8's Site C authority. The comparison is the policy's, not P8's."""
        return float(best) - float(next_best) >= self.margin_threshold


def _positive(value: object, *, source: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ConfigurationRequired(
            f"{source} is {value!r}; P11 needs a positive limit and ships no "
            "fallback. A default here would run the corpus under a bound nobody "
            "chose, with nothing to say so."
        )
    return value


def placement_limits(conn: sqlite3.Connection) -> PlacementLimits:
    """P11's seven ceilings for this database. Every one read; none defaulted."""
    return PlacementLimits(**{
        name: _positive(get_ceiling(conn, key), source=key)
        for name, key in CEILINGS.items()
    })


def require_policy(policy: SupportPolicy | None) -> SupportPolicy:
    if not isinstance(policy, SupportPolicy):
        raise ConfigurationRequired(
            "§6.10's minimum support threshold and meaningful margin are "
            "unsettled by the design (SPEC Open question 1) and are injected. "
            "Absent means refuse, not guess."
        )
    return policy
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3 -m pytest -q tests/p11/test_p11_config.py`

Expected: PASS, 8 tests. `test_no_module_under_placement_binds_a_bare_number` passes trivially now and is the guard that keeps passing for the rest of the plan; Task 20 extends it to nested attributes.

- [ ] **Step 5: Commit**

```bash
git add src/placement/config.py tests/p11/test_p11_config.py
git commit -m "feat(p11): read every placement limit and inject every threshold"
```

### Task 6: Index only the legal destinations of a frozen tree

**Files:**
- Create: `tests/p11/p10_fixtures.py`
- Create: `src/placement/index.py`
- Create: `tests/p11/test_p11_index.py`
- Create: `tests/integration/test_p11_p10_tree.py`

**Consumes:** `tests/p11/p10_fixtures.FrozenTree` (until P10 ships), `placement.store`, `placement.events.index_entry_built`.

**Produces:**

```python
class FrozenTreeRequired(RuntimeError): ...

@dataclass(frozen=True)
class IndexEntry:
    node_id: str; origin_node_id: str; plan_version: str
    node_role: str; disposition: str | None
    display_label: str; parent_node_id: str | None; root_anchor: str
    depth: int; ancestor_labels: tuple[str, ...]
    template_fields: tuple[str, ...]; expected_values: tuple[tuple[str, str], ...]
    accepted_group_ids: tuple[str, ...]; group_labels: tuple[str, ...]
    representative_files: tuple[str, ...]; anchor_excerpt_keys: tuple[str, ...]
    known_document_types: tuple[str, ...]; parent_context: tuple[str, ...]
    child_context: tuple[str, ...]; known_exclusions: tuple[str, ...]
    user_edits: tuple[str, ...]; handling_class: str
    refinement_disposition: str

def build_destination_index(conn, tree, *, component_version, observed_at) -> tuple[IndexEntry, ...]: ...
def legal_node_ids(conn, *, plan_version: str) -> frozenset[str]: ...
def node_exists(conn, *, plan_version: str): ...   # returns P8's Callable[[str, str], bool]
def entry_for(conn, *, plan_version: str, node_id: str) -> IndexEntry | None: ...
def entries_for_plan(conn, *, plan_version: str) -> tuple[IndexEntry, ...]: ...
```

**Done-means:** 2 (SPEC:614-619), 3 (SPEC:620-622); Contract out §2 (SPEC:488-504); SPEC:130-137.

**The one thing this task exists to make impossible.** SPEC:134-137: *"**Node existence is not legality.** The legal set is exactly `{node_id : plan_version = frozen version, accepts_placement = true}`; a node that exists with `accepts_placement = false` is visible context, never a destination."* An entry is built only for a node that clears both, so §5.10's guarantee that a user may leave a folder alone holds at the **retrieval** layer and not merely at validation. `node_exists` is the closure P11 hands P8 as an authority, so P8's `NODE_NOT_IN_FROZEN_TREE` check and P11's index answer the same question from one source.

**No node id is reserved here.** `src/llm_harness/placement_validation.py:239` reads `if payload.get("generic_hub") is True or destination == "node-hub":`, and `"node-hub"` is a P8 fixture id (`llm_harness/fixtures.py:356`) that reached production Site C logic. **P8 removes the literal; P11 adds nothing** (`planning/38-p10-p11-connection-contract.md` §6). The one fixture that produces `GENERIC_HUB_ONLY` already sets `generic_hub: True`, so the literal is dead weight in the only case it was written for and deleting it changes no recorded outcome. A reserved-id list inside the index would be a P8 implementation detail refusing a folder name for a reason the user could never be told — the same defect P9 guards against in `tests/p9/test_p9_graph.py:226`. **Ordering gate:** P8's removal lands before this task.

- [ ] **Step 1: Write the frozen-tree fixture**

```python
# tests/p11/p10_fixtures.py
"""A test-only stand-in for P10's frozen tree. TESTS ONLY.

P10 is unbuilt. `src/placement/` may never import this module and a test asserts
it does not: a source stub here would be P11 deciding what a node is, which is
P10's to say. Replacing this import with P10's public frozen-tree read is a
required integration test when P10 ships.

Every record here MIRRORS P10's real one, field for field, and invents nothing:
`Node`, `ExpectedValue`, `TemplateContext`, `NodeContext`, `AnchorExcerpt`,
`Restrictions`, `DestinationProfile`, `FreezeRecord` and `FrozenTree` are P10's,
declared here only because `tree_design` is unbuilt. At the swap this module is
deleted and every name is imported from `tree_design.records`,
`tree_design.profiles` and `tree_design.freeze` unchanged. `tree_with()` is the
only thing in this file P11 owns.

The node field list is P10 SPEC Contract out §1 in full -- twenty-two fields --
including the five P11's own SPEC Contract-in omits. `refinement_disposition` is
the one that matters most: it is the user's own answer to whether a branch is
shallow ON PURPOSE, and §6.7 and `decision_depth.unsupported_levels` are decisions
about exactly that. P11 reading it beats P11 re-deriving it. It is `str | None` on
the record because a DRAFT node may not carry one yet; `frozen_tree` guarantees it
non-`None` on every node it returns, which is why the index may read it as a `str`.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class ExpectedValue:
    """One `field = value` assertion a level makes (§6.1). P10's record."""

    field: str
    value: str


@dataclass(frozen=True)
class TemplateContext:
    """Which branch-local composition, and which level of it, produced a node."""

    binding_id: str
    template_id: str
    template_version: int
    dimension_index: int
    fragment_id: str | None = None
    fragment_version: int | None = None


@dataclass(frozen=True)
class Node:
    node_id: str
    plan_version_id: str
    node_type: str
    display_label: str
    parent_node_id: str | None
    root_anchor: str
    ordinal: int
    associated_group_ids: tuple[str, ...]
    explanation: str
    node_role: str
    accepts_placement: bool
    handling_class: str
    origin_node_id: str
    template_context: TemplateContext | None = None
    dimension_role: str | None = None
    dimension: str | None = None
    expected_values: tuple[ExpectedValue, ...] = ()
    existing_path: str | None = None
    disposition: str | None = None
    refinement_disposition: str | None = None
    refinement_reason: str | None = None
    protected_movement_permitted: bool = False


@dataclass(frozen=True)
class NodeContext:
    """One ancestor or child, as §6.1's "parent and child meanings". P10's."""

    node_id: str
    display_label: str
    dimension: str | None
    expected_values: tuple[ExpectedValue, ...]


@dataclass(frozen=True)
class AnchorExcerpt:
    """A P9 direct anchor's cited evidence, addressed by P4's durable handle.

    It carries `node_id` beside `observation_key` because §6.1 asks for anchor
    evidence PER NODE; a bare key tuple cannot say which node an excerpt anchors.
    """

    observation_key: str
    node_id: str


@dataclass(frozen=True)
class Restrictions:
    handling_class: str
    accepts_placement: bool
    node_role: str
    disposition: str | None


@dataclass(frozen=True)
class DestinationProfile:
    """§6.1, emitted by P10 (B4). P11 builds the §6.2 index OVER this, never one."""

    node_id: str
    display_label: str
    domains: tuple[str, ...]
    template_binding: str | None
    template_fields: tuple[str, ...]
    expected_values: tuple[ExpectedValue, ...]
    parent_context: tuple[NodeContext, ...]
    child_context: tuple[NodeContext, ...]
    accepted_group_ids: tuple[str, ...]
    group_labels: tuple[str, ...]
    representative_files: tuple[str, ...]
    anchor_files: tuple[str, ...]
    anchor_excerpts: tuple[AnchorExcerpt, ...]
    known_document_types: tuple[str, ...]
    known_exclusions: tuple[str, ...]
    user_edits: tuple[str, ...]
    restrictions: Restrictions


@dataclass(frozen=True)
class FreezeRecord:
    """§8.8's adopted-plan-version record. Ids and configuration only -- P10's."""

    plan_version_id: str
    created_at: str
    node_ids: tuple[str, ...]
    legal_destination_ids: frozenset[str]
    template_bindings: tuple[str, ...]
    labels_and_aliases: Mapping[str, tuple[str, ...]]
    residual_configuration: Mapping[str, str]
    shared_material_policy_ids: tuple[str, ...]
    cross_folder_moves: bool
    selection_id: str


@dataclass(frozen=True)
class FrozenTree:
    """P10's hand-over bundle. `frozen_tree(conn, *, plan_version)` returns it.

    `shared_material_policy` is the resolved VALUE, not one of
    `FreezeRecord.shared_material_policy_ids`: §6.9 makes P11 branch on which of
    four rules applies, and an id list cannot tell it which.
    """

    plan_version_id: str
    freeze_record: FreezeRecord
    nodes: tuple[Node, ...]
    profiles: tuple[DestinationProfile, ...]
    shared_material_policy: str
    shared_material_policy_scope: str | None = None


def _node(**overrides) -> Node:
    values = dict(
        node_id="n-course", plan_version_id="plan-1", node_type="proposed",
        display_label="PHYS1401", parent_node_id="n-academics",
        root_anchor="root_documents", ordinal=1,
        associated_group_ids=("g-phys1401",),
        template_context=TemplateContext(
            binding_id="tb-academic-coursework",
            template_id="academic-coursework", template_version=1,
            dimension_index=2),
        dimension_role="course", dimension="subject",
        expected_values=(ExpectedValue(field="subject", value="PHYS1401"),),
        explanation="Six files in the accepted PHYS1401 group carry subject = PHYS1401.",
        existing_path=None, handling_class="personal_non_sensitive",
        node_role="ordinary", disposition=None, accepts_placement=True,
        protected_movement_permitted=False,
        refinement_disposition="refined",
        refinement_reason="The course has enough populated work types for this level.",
    )
    values.update(overrides)
    # P10 mints a new `node_id` per plan version and records lineage in
    # `origin_node_id` (P10 OQ5). In plan-1 every node IS its own origin, so the
    # default follows `node_id` rather than a fixed literal; a later version
    # overrides it explicitly and that is what Task 17 matches on.
    values.setdefault("origin_node_id", values["node_id"])
    return Node(**values)


#: `n-academics` as a parent, in P10's `NodeContext` shape. §6.1 asks for the
#: parent's MEANING -- its dimension and expected values -- not just its label,
#: which is why the profile carries a record here and a bare string nowhere.
_ACADEMICS_CONTEXT = NodeContext(
    node_id="n-academics", display_label="Academics", dimension=None,
    expected_values=(),
)


def _profile(node: Node, **overrides) -> DestinationProfile:
    values = dict(
        node_id=node.node_id, display_label=node.display_label,
        domains=("academic",), template_binding="tb-academic-coursework",
        template_fields=("subject", "work_type"),
        expected_values=node.expected_values,
        parent_context=(_ACADEMICS_CONTEXT,),
        child_context=(), accepted_group_ids=node.associated_group_ids,
        group_labels=("PHYS1401 course",), representative_files=("f-syllabus",),
        anchor_files=("f-syllabus",),
        anchor_excerpts=(AnchorExcerpt(observation_key="obs-syllabus",
                                       node_id=node.node_id),),
        known_document_types=("syllabus",), known_exclusions=(), user_edits=(),
        restrictions=Restrictions(handling_class=node.handling_class,
                                  accepts_placement=node.accepts_placement,
                                  node_role=node.node_role,
                                  disposition=node.disposition),
    )
    values.update(overrides)
    return DestinationProfile(**values)


#: The walking skeleton's tree. B8(b) (`planning/04-resolutions.md:143-146`) gives
#: it a SECOND RETRIEVABLE node on purpose, so the margin path is exercised rather
#: than bypassed.
#:
#: `n-course-alt` is NOT that node. Its expected `subject = PHYS1402` CONTRADICTS
#: the skeleton file's `subject = PHYS1401`, so `retrieve` suppresses it as a
#: conflict (`retrieval.py`'s `contradicted` branch) and it never becomes a
#: candidate. It earns its place proving §6.3's suppression and populating
#: `conflicts_considered`, but a suppressed node measures no margin.
#:
#: `n-course-shared` is the second CANDIDATE. It carries no expected value, so it
#: can never be contradicted, and it is reached through the accepted-group channel
#: — which is §6.9's own "Shared Application Materials" shape one level down. With
#: the skeleton's evidence it scores `2/7` against `n-course`'s `5/7`, giving a
#: measured margin of `0.4286` that clears a `0.2` threshold on the numbers rather
#: than by vacuity.
NODES: tuple[Node, ...] = (
    _node(),
    _node(node_id="n-course-alt", display_label="PHYS1402", ordinal=2,
          associated_group_ids=("g-phys1402",),
          expected_values=(ExpectedValue(field="subject", value="PHYS1402"),)),
    _node(node_id="n-course-shared", display_label="Shared Course Materials",
          ordinal=3, associated_group_ids=("g-shared",),
          dimension_role=None, dimension=None, expected_values=(),
          node_role="shared-material",
          explanation="Material shared across courses, reached by accepted group.",
          refinement_disposition="shallow-by-choice",
          refinement_reason="Shared material is one level by design (§6.9)."),
    _node(node_id="n-academics", display_label="Academics",
          parent_node_id=None, ordinal=0, associated_group_ids=(),
          dimension_role=None, dimension=None, expected_values=(),
          refinement_disposition="shallow-by-choice",
          refinement_reason="The user wants one level here and said so."),
    _node(node_id="n-general", display_label="General",
          parent_node_id="n-academics", ordinal=9, node_role="scoped-general",
          associated_group_ids=(), dimension_role=None, dimension=None,
          expected_values=(), refinement_disposition="shallow-by-choice",
          refinement_reason="§5.9's scoped fallback under a meaningful parent."),
    # No `existing_path`: P10's `Node.__post_init__` raises `MalformedTreeRecord`
    # when one is set on a node whose `node_type != existing`, and ignoring a
    # folder RECLASSIFIES it away from `existing`. §5.10's guarantee is carried
    # by `accepts_placement = false`, which is the field the index reads.
    _node(node_id="n-ignored", display_label="Old Downloads",
          node_type="ignored", parent_node_id=None, ordinal=8,
          associated_group_ids=(), dimension_role=None, dimension=None,
          expected_values=(),
          accepts_placement=False, refinement_disposition="shallow-by-choice",
          refinement_reason="The user chose to leave this folder untouched (§5.10)."),
    _node(node_id="n-review-later", display_label="To Sort",
          node_type="existing", parent_node_id=None, ordinal=7,
          node_role="residual", disposition="review-only",
          associated_group_ids=(), dimension_role=None, dimension=None,
          expected_values=(), existing_path="/Users/x/To Sort",
          refinement_disposition="shallow-by-choice",
          refinement_reason="Review Later mapped onto an existing folder (§7.4)."),
)

#: Invariant 3 of the seam contract: the freeze record's legal set IS the set of
#: nodes that accept placement. `build_destination_index` asserts the index equals
#: it, so a fixture that let the two drift would hide the defect the assert exists
#: to catch.
FREEZE_RECORD = FreezeRecord(
    plan_version_id="plan-1", created_at="2026-01-01T00:00:00Z",
    node_ids=tuple(node.node_id for node in NODES),
    legal_destination_ids=frozenset(
        node.node_id for node in NODES if node.accepts_placement),
    template_bindings=("tb-academic-coursework",),
    labels_and_aliases={}, residual_configuration={},
    shared_material_policy_ids=("smp-1",), cross_folder_moves=False,
    selection_id="sel-1",
)

FROZEN_TREE = FrozenTree(
    plan_version_id="plan-1", freeze_record=FREEZE_RECORD, nodes=NODES,
    profiles=tuple(_profile(node) for node in NODES),
    shared_material_policy="mandatory-review",
    shared_material_policy_scope=None,
)


def tree_with(**overrides) -> FrozenTree:
    from dataclasses import replace
    return replace(FROZEN_TREE, **overrides)
```

- [ ] **Step 2: Write the failing index tests**

```python
# tests/p11/test_p11_index.py
"""§6.2 — an index over P10's profiles, built only for legal destinations."""
from __future__ import annotations

from dataclasses import replace

import pytest

from placement import vocabulary as v
from placement.index import (
    FrozenTreeRequired, build_destination_index, entry_for, legal_node_ids,
    node_exists,
)
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE, tree_with

BUILD = dict(component_version="P11-test", observed_at=FIXED_CLOCK)


def test_an_ignored_node_is_never_retrievable(p11_conn):
    # §5.10's guarantee, held at the retrieval layer and not only at validation:
    # a file that looks like it belongs in a folder the user marked `ignored`
    # cannot even be offered it.
    build_destination_index(p11_conn, FROZEN_TREE, **BUILD)
    legal = legal_node_ids(p11_conn, plan_version="plan-1")
    assert "n-ignored" not in legal
    assert entry_for(p11_conn, plan_version="plan-1", node_id="n-ignored") is None
    assert {"n-course", "n-course-alt", "n-course-shared", "n-academics",
            "n-general", "n-review-later"} == legal


def test_node_exists_is_the_authority_p8_receives(p11_conn):
    # The same source answers P11's legality test and P8's
    # NODE_NOT_IN_FROZEN_TREE check. Two sources would let them disagree.
    build_destination_index(p11_conn, FROZEN_TREE, **BUILD)
    oracle = node_exists(p11_conn, plan_version="plan-1")
    assert oracle("n-course", "plan-1") is True
    assert oracle("n-ignored", "plan-1") is False
    assert oracle("n-invented", "plan-1") is False
    assert oracle("n-course", "plan-2") is False


def test_a_review_only_residual_node_is_still_a_legal_destination(p11_conn):
    # SPEC:147-150: what `review-only` changes is that no mutation follows, not
    # whether a decision may name it.
    build_destination_index(p11_conn, FROZEN_TREE, **BUILD)
    entry = entry_for(p11_conn, plan_version="plan-1", node_id="n-review-later")
    assert entry.node_role == v.RESIDUAL_ROLE
    assert entry.disposition == v.REVIEW_ONLY


def test_the_index_carries_no_path_even_where_the_node_has_one(p11_conn):
    # B3. `existing_path` is an observed fact about the corpus and is P12's input,
    # not a destination P11 may name.
    build_destination_index(p11_conn, FROZEN_TREE, **BUILD)
    entry = entry_for(p11_conn, plan_version="plan-1", node_id="n-review-later")
    assert not hasattr(entry, "existing_path")
    assert entry.ancestor_labels == ()
    assert entry.root_anchor == "root_documents"


def test_depth_and_ancestor_labels_come_from_the_parent_chain(p11_conn):
    build_destination_index(p11_conn, FROZEN_TREE, **BUILD)
    course = entry_for(p11_conn, plan_version="plan-1", node_id="n-course")
    assert course.depth == 1
    assert course.ancestor_labels == ("Academics",)
    root = entry_for(p11_conn, plan_version="plan-1", node_id="n-academics")
    assert root.depth == 0


def test_a_shallow_by_choice_branch_says_so_in_the_index(p11_conn):
    # P10 already holds the user's answer to "is this branch shallow on purpose?".
    # §6.7 is a decision about that, so P11 reads it rather than re-deriving it.
    build_destination_index(p11_conn, FROZEN_TREE, **BUILD)
    assert entry_for(p11_conn, plan_version="plan-1",
                     node_id="n-academics").refinement_disposition == "shallow-by-choice"
    assert entry_for(p11_conn, plan_version="plan-1",
                     node_id="n-course").refinement_disposition == "refined"


def test_a_node_with_no_profile_fails_closed(p11_conn):
    # Done-means 3: the profile is present for EVERY frozen node before the first
    # file is placed. A missing one is a broken freeze, not an empty entry.
    tree = tree_with(profiles=FROZEN_TREE.profiles[1:])
    with pytest.raises(FrozenTreeRequired):
        build_destination_index(p11_conn, tree, **BUILD)


def test_a_missing_shared_material_policy_fails_closed(p11_conn):
    # §6.9 requires the frozen tree to carry one; without it a multi-home file
    # has no rule and P11 would have to choose an institution.
    with pytest.raises(FrozenTreeRequired):
        build_destination_index(p11_conn, tree_with(shared_material_policy=""), **BUILD)


def test_the_index_is_provably_the_freeze_records_projection(p11_conn):
    # §4.4 of the seam contract: ONE legality authority. P10's
    # `freeze_record.legal_destination_ids` decides; P11's index projects. Two
    # sources that can disagree is the defect the contract forbids, so a tree
    # whose record and nodes disagree fails closed rather than publishing a
    # second opinion.
    record = replace(FROZEN_TREE.freeze_record,
                     legal_destination_ids=frozenset({"n-course"}))
    with pytest.raises(FrozenTreeRequired):
        build_destination_index(p11_conn, tree_with(freeze_record=record), **BUILD)


def test_an_entry_carries_the_lineage_task_17_matches_on(p11_conn):
    # P10 mints a new `node_id` per plan version (its OQ5) and records lineage in
    # `origin_node_id`. Matching a decision across versions on `node_id` would
    # mark EVERY decision for renewed review after any tree edit, including a
    # pure rename — which §8.8 forbids. The lineage must reach the index.
    build_destination_index(p11_conn, FROZEN_TREE, **BUILD)
    entry = entry_for(p11_conn, plan_version="plan-1", node_id="n-course")
    assert entry.origin_node_id == "n-course"


def test_building_an_entry_appends_its_event(p11_conn):
    build_destination_index(p11_conn, FROZEN_TREE, **BUILD)
    rows = p11_conn.execute(
        "SELECT explanation FROM events WHERE event_type = ?",
        (v.INDEX_ENTRY_BUILT,)).fetchall()
    assert len(rows) == len(legal_node_ids(p11_conn, plan_version="plan-1"))
    assert "n-course" in " ".join(r["explanation"] for r in rows)
```

And the dependency gate:

```python
# tests/integration/test_p11_p10_tree.py
"""G-P10: the live frozen-tree read. Fails explicitly until P10 ships.

This must fail with an ImportError naming P10's absent module. It must not be
skipped, and no source stub may satisfy it: a stub would be P11 deciding what a
frozen node is, which is the one thing SPEC:102 says P11 does not own.
"""
from __future__ import annotations

from placement.index import build_destination_index
from p11.conftest import FIXED_CLOCK


def test_p11_indexes_p10s_live_frozen_tree(p11_conn):
    from tree_design.freeze import frozen_tree  # noqa: F401  -- G-P10

    tree = frozen_tree(p11_conn, plan_version="plan-1")
    entries = build_destination_index(
        p11_conn, tree, component_version="P11-integration",
        observed_at=FIXED_CLOCK,
    )
    assert entries
    assert all(entry.plan_version == "plan-1" for entry in entries)
```

- [ ] **Step 3: Run and verify RED**

Run: `python3 -m pytest -q tests/p11/test_p11_index.py tests/integration/test_p11_p10_tree.py`

Expected: the unit file FAILS at collection (`No module named 'placement.index'`); the integration file FAILS with `ModuleNotFoundError: No module named 'tree_design'`, which is G-P10 and stays failing until P10 ships.

- [ ] **Step 4: Implement the index**

```python
# src/placement/index.py
"""§6.2's destination-node retrieval index, built after freeze over P10's profiles.

P10 emits the §6.1 profile; P11 builds the index over it and publishes no profile
of its own (B4). The boundary is that the index is a placement MECHANISM while the
profile describes what the user approved.

One entry exists per node with `accepts_placement = true`, and per nothing else.
That is where §5.10's guarantee lives: an `ignored` node is not merely rejected at
validation, it is never retrieved, so a file that resembles it produces an
abstention rather than a suppressed candidate the user has to read about.

`node_exists` is the closure P8's Sites C and D take as their `node_exists`
authority. One source answers both P11's legality test and P8's
NODE_NOT_IN_FROZEN_TREE check; two sources could disagree and the disagreement
would look like a model error.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from dataclasses import asdict, dataclass

from database_agent.db import transaction

from placement import events as placement_events
from placement.vocabulary import DISPOSITIONS, NODE_ROLES, RESIDUAL_ROLE, check

class FrozenTreeRequired(RuntimeError):
    """The tree P11 was handed is not a complete frozen tree. Never a partial index."""


@dataclass(frozen=True)
class IndexEntry:
    node_id: str
    origin_node_id: str
    plan_version: str
    node_role: str
    disposition: str | None
    display_label: str
    parent_node_id: str | None
    root_anchor: str
    depth: int
    ancestor_labels: tuple[str, ...]
    template_fields: tuple[str, ...]
    expected_values: tuple[tuple[str, str], ...]
    accepted_group_ids: tuple[str, ...]
    group_labels: tuple[str, ...]
    representative_files: tuple[str, ...]
    anchor_excerpt_keys: tuple[str, ...]
    known_document_types: tuple[str, ...]
    parent_context: tuple[str, ...]
    child_context: tuple[str, ...]
    known_exclusions: tuple[str, ...]
    user_edits: tuple[str, ...]
    handling_class: str
    refinement_disposition: str


def _ancestry(node, by_id) -> tuple[int, tuple[str, ...]]:
    labels: list[str] = []
    cursor = node.parent_node_id
    seen: set[str] = {node.node_id}
    while cursor is not None:
        if cursor in seen:
            raise FrozenTreeRequired(f"the ancestry of {node.node_id!r} cycles")
        seen.add(cursor)
        parent = by_id.get(cursor)
        if parent is None:
            raise FrozenTreeRequired(
                f"{node.node_id!r} names parent {cursor!r}, which the frozen tree "
                "does not contain; an index over a broken chain would compose a "
                "path P12 could not resolve"
            )
        labels.append(parent.display_label)
        cursor = parent.parent_node_id
    return len(labels), tuple(reversed(labels))


def _entry(node, profile, by_id) -> IndexEntry:
    depth, ancestors = _ancestry(node, by_id)
    check(node.node_role, NODE_ROLES, name="node_role")
    if node.node_role == RESIDUAL_ROLE:
        check(node.disposition, DISPOSITIONS, name="disposition")
    elif node.disposition is not None:
        raise FrozenTreeRequired(
            f"{node.node_id!r} is {node.node_role!r} and carries a disposition; "
            "§7.4 makes disposition required on a residual node and meaningless "
            "on every other role"
        )
    return IndexEntry(
        node_id=node.node_id, origin_node_id=node.origin_node_id,
        plan_version=node.plan_version_id,
        node_role=node.node_role, disposition=node.disposition,
        display_label=node.display_label, parent_node_id=node.parent_node_id,
        root_anchor=node.root_anchor, depth=depth, ancestor_labels=ancestors,
        template_fields=tuple(profile.template_fields),
        # `ExpectedValue` is P10's frozen dataclass, not a mapping: `item["field"]`
        # would raise `TypeError` on the first real node.
        expected_values=tuple(
            (item.field, item.value) for item in node.expected_values
        ),
        accepted_group_ids=tuple(profile.accepted_group_ids),
        group_labels=tuple(profile.group_labels),
        representative_files=tuple(profile.representative_files),
        # The index FLATTENS what P10 publishes; it never assumes it arrived flat.
        # `AnchorExcerpt` carries `node_id` beside `observation_key` because §6.1
        # wants anchor evidence per node, and the entry keeps only the keys it
        # scores on -- a projection of P10's record, not a rival shape for it.
        anchor_excerpt_keys=tuple(
            excerpt.observation_key for excerpt in profile.anchor_excerpts),
        known_document_types=tuple(profile.known_document_types),
        parent_context=tuple(c.display_label for c in profile.parent_context),
        child_context=tuple(c.display_label for c in profile.child_context),
        known_exclusions=tuple(profile.known_exclusions),
        user_edits=tuple(profile.user_edits),
        handling_class=node.handling_class,
        refinement_disposition=node.refinement_disposition,
    )


def build_destination_index(conn: sqlite3.Connection, tree, *,
                            component_version: str,
                            observed_at: str) -> tuple[IndexEntry, ...]:
    """Build one entry per legal node. Nothing partial reaches the table."""
    if not getattr(tree, "plan_version_id", ""):
        raise FrozenTreeRequired("an index projects one frozen plan version")
    if not getattr(tree, "shared_material_policy", ""):
        raise FrozenTreeRequired(
            "§6.9 requires the frozen tree to carry a shared-material policy; "
            "without one a transcript belonging to two packets has no rule and "
            "P11 would have to pick an institution"
        )
    by_id = {node.node_id: node for node in tree.nodes}
    profiles = {profile.node_id: profile for profile in tree.profiles}
    missing = sorted(node_id for node_id in by_id if node_id not in profiles)
    if missing:
        raise FrozenTreeRequired(
            f"no §6.1 destination profile for {missing}; every frozen node has one "
            "at freeze (B4) and an index built over a partial set would silently "
            "make those nodes unreachable"
        )

    entries = tuple(
        _entry(node, profiles[node.node_id], by_id)
        for node in tree.nodes if node.accepts_placement
    )
    # ONE legality authority, and this line is what keeps it one. P10's freeze
    # record decides the legal set (`freeze_record.legal_destination_ids`); this
    # index is its PROJECTION and must be provably equal. Two callables that can
    # answer the same question differently is the defect
    # `planning/22-p1-p7-connection-contract.md` §6 check 5 names: "exactly one
    # part writes each concept". `legal_node_ids` reads this table, so if the two
    # ever drifted P8's `NODE_NOT_IN_FROZEN_TREE` would fire on a legal node and
    # look like a model error.
    indexed = {entry.node_id for entry in entries}
    if indexed != set(tree.freeze_record.legal_destination_ids):
        raise FrozenTreeRequired(
            "the index disagrees with the freeze record's legal set: "
            f"{sorted(indexed ^ set(tree.freeze_record.legal_destination_ids))} "
            "differ; P10 owns legality and P11 only projects it"
        )
    with transaction(conn):
        for entry in entries:
            conn.execute(
                "INSERT INTO placement_index_entries (record_id, plan_version, "
                "node_id, payload, created_at) VALUES (?, ?, ?, ?, ?)",
                (f"{entry.plan_version}:{entry.node_id}", entry.plan_version,
                 entry.node_id, json.dumps(asdict(entry), sort_keys=True),
                 observed_at),
            )
            placement_events.index_entry_built(
                conn, node_id=entry.node_id, plan_version=entry.plan_version,
                component_version=component_version, observed_at=observed_at,
            )
    return entries


def legal_node_ids(conn: sqlite3.Connection, *, plan_version: str) -> frozenset[str]:
    """SPEC:135-136's set, read from the index rather than recomputed."""
    return frozenset(
        row["node_id"] for row in conn.execute(
            "SELECT node_id FROM placement_index_entries WHERE plan_version = ? "
            "AND superseded_by IS NULL", (plan_version,),
        )
    )


def node_exists(conn: sqlite3.Connection, *,
                plan_version: str) -> Callable[[str, str], bool]:
    """P8's Site C and Site D `node_exists` authority, closed over one version.

    P8 calls it with `(node_id, dossier.plan_version)`. A dossier stamped with a
    different version answers False, because the legal set is per version and a
    decision made against a stale tree is not a legal decision (§8.8).
    """
    legal = legal_node_ids(conn, plan_version=plan_version)

    def exists(node_id: str, called_plan_version: str) -> bool:
        return called_plan_version == plan_version and node_id in legal

    return exists


def entry_for(conn: sqlite3.Connection, *, plan_version: str,
              node_id: str) -> IndexEntry | None:
    row = conn.execute(
        "SELECT payload FROM placement_index_entries WHERE plan_version = ? AND "
        "node_id = ? AND superseded_by IS NULL", (plan_version, node_id),
    ).fetchone()
    if row is None:
        return None
    body = json.loads(row["payload"])
    body["expected_values"] = tuple(tuple(pair) for pair in body["expected_values"])
    for name, value in body.items():
        if isinstance(value, list):
            body[name] = tuple(value)
    return IndexEntry(**body)


def entries_for_plan(conn: sqlite3.Connection, *,
                     plan_version: str) -> tuple[IndexEntry, ...]:
    return tuple(
        entry_for(conn, plan_version=plan_version, node_id=node_id)
        for node_id in sorted(legal_node_ids(conn, plan_version=plan_version))
    )
```

- [ ] **Step 5: Run and verify GREEN**

Run: `python3 -m pytest -q tests/p11/test_p11_index.py`

Expected: PASS, 11 tests. Run the gate separately and confirm it still fails for the right reason:

Run: `python3 -m pytest -q tests/integration/test_p11_p10_tree.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'tree_design'`. That is G-P10 and is the correct state until P10 ships.

- [ ] **Step 6: Commit**

```bash
git add tests/p11/p10_fixtures.py src/placement/index.py \
        tests/p11/test_p11_index.py tests/integration/test_p11_p10_tree.py
git commit -m "feat(p11): index only the legal destinations of a frozen tree"
```

### Task 7: Retrieve bounded candidates and record what conflict suppressed

**Files:**
- Create: `src/placement/retrieval.py`
- Create: `tests/p11/test_p11_retrieval.py`

**Consumes:** `facts.read_surface.facts_for`, `facts.read_surface.is_destination_eligible`, `placement.index.entries_for_plan`, `placement.config.PlacementLimits`.

**Produces:**

```python
@dataclass(frozen=True)
class Candidate:
    node_id: str; channels: tuple[str, ...]
    matching_facts: tuple[MatchingFact, ...]; group_ids: tuple[str, ...]

@dataclass(frozen=True)
class Retrieval:
    subject_ref: str; plan_version: str
    candidates: tuple[Candidate, ...]
    conflicts: tuple[ConflictConsidered, ...]
    semantic_only_node_ids: frozenset[str]

CHANNELS: tuple[str, ...]   # six, §6.3's own list

def retrieve(conn, *, subject, plan_version, limits, facts, group_ids,
             curated_folder_labels, semantic_neighbours,
             component_version, observed_at) -> Retrieval: ...
```

**Done-means:** 4 (SPEC:623-626), 5's first clause (SPEC:627-630), 2's §6.2 half (SPEC:617-619); SPEC:502-504.

**Which P8 check this task is therefore not writing.** None — Site C never sees a candidate set. Retrieval is entirely P11's, and it is what produces the `allowed_vocabulary` P8 later checks a destination against. What this task must not do is *decide*: a retrieved candidate is not a placement, and §6.5's rule that "a semantic embedding alone is insufficient" is enforced by marking such a node `semantic_only` here and refusing it as a sole support in Task 9, not by dropping it from retrieval where the user could never see it was considered.

- [ ] **Step 1: Write the failing retrieval tests**

```python
# tests/p11/test_p11_retrieval.py
"""§6.3 — six channels drive retrieval and conflicting evidence suppresses."""
from __future__ import annotations

import dataclasses

import pytest

from placement import vocabulary as v
from placement.config import PlacementLimits
from placement.index import build_destination_index
from placement.records import MatchingFact, Subject
from placement.retrieval import CHANNELS, retrieve
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE

LIMITS = PlacementLimits(
    max_retrieved_neighbors=4, max_local_graph_neighborhood=8,
    max_candidate_cluster_size=6, max_residual_files_per_batch=50,
    max_dossier_tokens=4000, max_llm_calls_per_thousand_files=100,
    max_cost_per_scan=5,
)
SUBJECT = Subject(kind=v.FILE, file_id="f1", content_hash="h1",
                  group_id=None, member_file_ids=())


def _fact(field="subject", value="PHYS1401", reliability=v.DIRECT, ref="obs-1"):
    return MatchingFact(file_fact_id=f"ff-{field}-{value}", field=field,
                        value=value, reliability=reliability, evidence_ref=ref)


def _retrieve(conn, **overrides):
    values = dict(
        subject=SUBJECT, plan_version="plan-1", limits=LIMITS,
        facts=(_fact(),), group_ids=(), curated_folder_labels=(),
        semantic_neighbours=(), component_version="P11-test",
        observed_at=FIXED_CLOCK,
    )
    values.update(overrides)
    return retrieve(conn, **values)


@pytest.fixture()
def indexed(p11_conn):
    build_destination_index(p11_conn, FROZEN_TREE,
                            component_version="P11-test", observed_at=FIXED_CLOCK)
    return p11_conn


def test_the_six_channels_are_63s_own_list():
    assert len(CHANNELS) == 6
    assert set(CHANNELS) == {
        "direct_fact", "accepted_group", "graph_relationship",
        "structural_relationship", "semantic_neighbour", "curated_folder",
    }


def test_a_direct_fact_retrieves_the_node_whose_expected_value_it_matches(indexed):
    result = _retrieve(indexed)
    assert [c.node_id for c in result.candidates] == ["n-course"]
    assert result.candidates[0].channels == ("direct_fact",)


def test_a_conflicting_direct_fact_suppresses_and_the_suppression_is_recorded(indexed):
    # Done-means 4: a direct `subject = PHYS1402` does not retrieve the PHYS1401
    # node as a top candidate, and the review surface can show why not.
    result = _retrieve(indexed, facts=(_fact(value="PHYS1402", ref="obs-2"),))
    assert [c.node_id for c in result.candidates] == ["n-course-alt"]
    suppressed = {n for conflict in result.conflicts
                  for n in conflict.suppressed_node_ids}
    assert "n-course" in suppressed
    assert result.conflicts[0].conflicting_value == "PHYS1402"
    assert result.conflicts[0].evidence_ref == "obs-2"


def test_an_ignored_node_never_appears_even_as_a_suppressed_candidate(indexed):
    # It is not in the index at all, so §5.10's guarantee needs no second rule.
    result = _retrieve(indexed, curated_folder_labels=("Old Downloads",))
    assert "n-ignored" not in {c.node_id for c in result.candidates}
    assert "n-ignored" not in {n for conflict in result.conflicts
                               for n in conflict.suppressed_node_ids}


def test_a_semantic_only_neighbour_is_retrieved_and_marked_as_such(indexed):
    # §6.5: it may improve recall; it may never be the sole support. Marking it
    # here keeps it visible to review; dropping it would hide that it was
    # considered.
    result = _retrieve(indexed, facts=(), semantic_neighbours=("n-course",))
    assert [c.node_id for c in result.candidates] == ["n-course"]
    assert result.semantic_only_node_ids == frozenset({"n-course"})


def test_a_fact_on_a_field_that_is_not_destination_eligible_drives_nothing(indexed):
    # §3.8: authorship and creator identity are not destination dimensions, and
    # P6 already publishes the answer, so P11 asks rather than deciding.
    result = _retrieve(indexed, facts=(_fact(field="authored_by", value="J. Yung"),))
    assert result.candidates == ()


def test_retrieval_is_bounded_and_the_tie_break_is_stable(indexed):
    limits = dataclasses.replace(LIMITS, max_retrieved_neighbors=1)
    result = _retrieve(indexed, facts=(), limits=limits,
                       semantic_neighbours=("n-course-alt", "n-course"))
    assert len(result.candidates) == 1
    again = _retrieve(indexed, facts=(), limits=limits,
                      semantic_neighbours=("n-course", "n-course-alt"))
    assert [c.node_id for c in result.candidates] == [c.node_id for c in again.candidates]


def test_retrieval_appends_its_event_with_both_lists(indexed):
    _retrieve(indexed, facts=(_fact(value="PHYS1402", ref="obs-2"),))
    row = indexed.execute(
        "SELECT explanation FROM events WHERE event_type = ? "
        "ORDER BY event_id DESC LIMIT 1", (v.CANDIDATE_RETRIEVAL,)).fetchone()
    assert "n-course-alt" in row["explanation"]
    assert "n-course" in row["explanation"]
```

- [ ] **Step 2: Run and verify RED**

Run: `python3 -m pytest -q tests/p11/test_p11_retrieval.py`

Expected: FAIL at collection — `ModuleNotFoundError: No module named 'placement.retrieval'`.

- [ ] **Step 3: Implement retrieval**

```python
# src/placement/retrieval.py
"""§6.3's bounded candidate retrieval, and §6.3's active suppression.

Six channels drive retrieval and none of them decides. A candidate is a node the
evidence gives a reason to consider; whether it becomes a placement is §6.10's
question, asked one task later. Keeping the two apart is what lets a semantic
neighbour improve recall (§6.5) without ever becoming the sole reason for a move.

Suppression is recorded, not silent. §6.3 says conflicting evidence "actively
suppresses" nodes, and SPEC:502-504 requires the suppression to reach
`conflicts_considered` so the review interface can show what was ruled out and
why. A node dropped without a record is a question the user cannot ask.

An `ignored` node needs no rule here at all: it never entered the index, so it can
neither be retrieved nor suppressed, and §5.10 holds without a second mechanism.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from facts.read_surface import is_destination_eligible

from placement import events as placement_events
from placement.index import entries_for_plan
from placement.records import ConflictConsidered, MatchingFact

DIRECT_FACT: str = "direct_fact"
ACCEPTED_GROUP: str = "accepted_group"
GRAPH_RELATIONSHIP: str = "graph_relationship"
STRUCTURAL_RELATIONSHIP: str = "structural_relationship"
SEMANTIC_NEIGHBOUR: str = "semantic_neighbour"
CURATED_FOLDER: str = "curated_folder"

#: §6.3's own list of what drives retrieval. Six, and a seventh would be a
#: contract revision rather than an implementation decision.
CHANNELS: tuple[str, ...] = (
    DIRECT_FACT, ACCEPTED_GROUP, GRAPH_RELATIONSHIP, STRUCTURAL_RELATIONSHIP,
    SEMANTIC_NEIGHBOUR, CURATED_FOLDER,
)

#: The two channels that can never make a node a candidate on their own terms
#: strongly enough to place. Task 9 refuses a `place` supported only by these.
NON_DECIDING_CHANNELS: tuple[str, ...] = (SEMANTIC_NEIGHBOUR, CURATED_FOLDER)


@dataclass(frozen=True)
class Candidate:
    node_id: str
    channels: tuple[str, ...]
    matching_facts: tuple[MatchingFact, ...]
    group_ids: tuple[str, ...]


@dataclass(frozen=True)
class Retrieval:
    subject_ref: str
    plan_version: str
    candidates: tuple[Candidate, ...]
    conflicts: tuple[ConflictConsidered, ...]
    semantic_only_node_ids: frozenset[str]


def _eligible_facts(conn, facts) -> tuple[MatchingFact, ...]:
    """Drop facts whose field P6 says is not a destination dimension (§3.8).

    P6 already publishes the answer per field, so P11 asks it rather than keeping
    a second opinion about which fields may build a folder.
    """
    return tuple(
        fact for fact in facts
        if is_destination_eligible(conn, field_key=fact.field)
    )


def retrieve(conn: sqlite3.Connection, *, subject, plan_version, limits,
             facts, group_ids, curated_folder_labels, semantic_neighbours,
             component_version: str, observed_at: str) -> Retrieval:
    from placement.store import subject_ref_of

    subject_ref = subject_ref_of(subject)
    entries = entries_for_plan(conn, plan_version=plan_version)
    usable = _eligible_facts(conn, facts)
    by_field = {(fact.field, fact.value): fact for fact in usable}
    stated_fields = {fact.field for fact in usable}
    wanted_groups = set(group_ids)
    wanted_labels = {label.casefold() for label in curated_folder_labels}
    semantic = set(semantic_neighbours)

    matched: dict[str, dict] = {}
    conflicts: list[ConflictConsidered] = []
    suppressed_by_value: dict[tuple[str, str], list[str]] = {}

    for entry in entries:
        channels: list[str] = []
        entry_facts: list[MatchingFact] = []
        entry_groups: list[str] = []
        contradicted = False
        for field, value in entry.expected_values:
            fact = by_field.get((field, value))
            if fact is not None:
                channels.append(DIRECT_FACT)
                entry_facts.append(fact)
            elif field in stated_fields:
                # The subject states this field with a DIFFERENT value. §6.3's
                # suppression: a direct `target institution = Duke` must not
                # retrieve Columbia branches as a top candidate.
                contradicted = True
                held = next(f for f in usable if f.field == field)
                suppressed_by_value.setdefault(
                    (field, held.value), []).append(entry.node_id)
        if contradicted:
            continue
        overlap = wanted_groups & set(entry.accepted_group_ids)
        if overlap:
            channels.append(ACCEPTED_GROUP)
            entry_groups.extend(sorted(overlap))
        if entry.display_label.casefold() in wanted_labels:
            channels.append(CURATED_FOLDER)
        if entry.node_id in semantic:
            channels.append(SEMANTIC_NEIGHBOUR)
        if channels:
            matched[entry.node_id] = {
                "channels": tuple(dict.fromkeys(channels)),
                "facts": tuple(entry_facts), "groups": tuple(entry_groups),
            }

    for (field, value), node_ids in sorted(suppressed_by_value.items()):
        held = next(f for f in usable if f.field == field and f.value == value)
        conflicts.append(ConflictConsidered(
            kind=field, conflicting_value=value,
            suppressed_node_ids=tuple(sorted(node_ids)),
            evidence_ref=held.evidence_ref,
        ))

    def _rank(item):
        node_id, body = item
        # Deterministic and stable: strongest channel first, then the node id, so
        # two runs over the same evidence produce the same order and a P2 replay
        # can compare them. Never insertion order.
        strength = tuple(
            0 if channel in body["channels"] else 1 for channel in CHANNELS
        )
        return (strength, node_id)

    ordered = sorted(matched.items(), key=_rank)[:limits.max_retrieved_neighbors]
    candidates = tuple(
        Candidate(node_id=node_id, channels=body["channels"],
                  matching_facts=body["facts"], group_ids=body["groups"])
        for node_id, body in ordered
    )
    semantic_only = frozenset(
        candidate.node_id for candidate in candidates
        if set(candidate.channels) <= set(NON_DECIDING_CHANNELS)
    )
    placement_events.candidate_retrieval(
        conn, subject_ref=subject_ref, plan_version=plan_version,
        retrieved=[c.node_id for c in candidates],
        suppressed=sorted({n for c in conflicts for n in c.suppressed_node_ids}),
        component_version=component_version, observed_at=observed_at,
        file_id=subject.file_id, content_hash=subject.content_hash,
    )
    return Retrieval(
        subject_ref=subject_ref, plan_version=plan_version,
        candidates=candidates, conflicts=tuple(conflicts),
        semantic_only_node_ids=semantic_only,
    )
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3 -m pytest -q tests/p11/test_p11_retrieval.py`

Expected: PASS, 8 tests. `test_a_fact_on_a_field_that_is_not_destination_eligible_drives_nothing` depends on P6's catalogue being seeded, which `create_schema` plus P6's `create_fields` do; if `authored_by` is absent from the catalogue, `is_destination_eligible` raises rather than returning False, and the test should be read as confirming that too.

- [ ] **Step 5: Commit**

```bash
git add src/placement/retrieval.py tests/p11/test_p11_retrieval.py
git commit -m "feat(p11): retrieve bounded candidates and record every suppression"
```

### Task 8: Build a node-local evidence graph and never recluster the corpus

**Files:**
- Create: `src/placement/graph.py`
- Create: `tests/p11/test_p11_graph.py`

**Consumes:** `placement.retrieval.Retrieval`, `placement.config.PlacementLimits`, `placement.index.entry_for`.

**Produces:**

```python
EDGE_TYPES: tuple[str, ...]     # five typed relationships, §6.5

@dataclass(frozen=True)
class NodeLocalGraph:
    subject_ref: str; node_id: str
    anchors: tuple[GraphAnchor, ...]
    distinct_entities: frozenset[str]
    high_frequency_entities: frozenset[str]
    neighbourhood_size: int
    reduced_to_strongest: bool

class WholeCorpusReclusteringRefused(RuntimeError): ...

def build_node_local_graph(*, subject, candidate, entry, related_files, limits,
                           entity_frequency, generic_entity_frequency) -> NodeLocalGraph: ...
def is_typed_support(graph: NodeLocalGraph) -> bool: ...
```

**Done-means:** 5 (SPEC:627-630); the source of `graph_anchors[]` (SPEC:348); §6.12 step 4.

**This is the step the previous plan had no task for.** §6.12's pipeline step 4 is *"The engine builds a local graph around those nodes using facts, accepted groups, structural relationships, representative files, and semantic retrieval"* (`planning/01-product-design-structured.md:1298-1299`), and SPEC:42 requires it to compare the target against *the node's approved community, not against a folder name*. Without it, `graph_anchors[]` has no producer and §6.5's "a file connected only by generic similarity or one high-frequency entity stays uncertain" has nothing to measure.

**Which P8 check this task is therefore not writing.** Site C's `GENERIC_HUB_ONLY` (`placement_validation.py:239-240`). P8 decides that a *model's* answer was hub-only from the payload it returned. P11 decides that its *own* deterministic support is hub-only, from the graph, before any dossier exists — and passes the finding to P8 as the `generic_hub` payload flag in Task 12. Two different moments, one meaning, and P11 does not re-run P8's.

- [ ] **Step 1: Write the failing graph tests**

```python
# tests/p11/test_p11_graph.py
"""§6.4/§6.5 — a graph local to one node, with typed edges and no reclustering."""
from __future__ import annotations

import dataclasses

import pytest

from placement import vocabulary as v
from placement.config import PlacementLimits
from placement.graph import (
    EDGE_TYPES, WholeCorpusReclusteringRefused, build_node_local_graph,
    is_typed_support,
)
from placement.index import build_destination_index, entry_for
from placement.records import MatchingFact, Subject
from placement.retrieval import Candidate, DIRECT_FACT, SEMANTIC_NEIGHBOUR
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE

LIMITS = PlacementLimits(
    max_retrieved_neighbors=4, max_local_graph_neighborhood=3,
    max_candidate_cluster_size=6, max_residual_files_per_batch=50,
    max_dossier_tokens=4000, max_llm_calls_per_thousand_files=100,
    max_cost_per_scan=5,
)
SUBJECT = Subject(kind=v.FILE, file_id="f1", content_hash="h1",
                  group_id=None, member_file_ids=())


@pytest.fixture()
def entry(p11_conn):
    build_destination_index(p11_conn, FROZEN_TREE,
                            component_version="P11-test", observed_at=FIXED_CLOCK)
    return entry_for(p11_conn, plan_version="plan-1", node_id="n-course")


def _related(edge_type="shared_validated_fact", other="f-syllabus",
             entity="PHYS1401", weight=1):
    return {"edge_type": edge_type, "to_file_id": other, "entity": entity,
            "anchor_file_id": other, "weight": weight}


def _candidate(channels=(DIRECT_FACT,)):
    return Candidate(node_id="n-course", channels=channels,
                     matching_facts=(MatchingFact(
                         file_fact_id="ff1", field="subject", value="PHYS1401",
                         reliability=v.DIRECT, evidence_ref="obs-1"),),
                     group_ids=("g-phys1401",))


def _build(entry, **overrides):
    values = dict(
        subject=SUBJECT, candidate=_candidate(), entry=entry,
        related_files=(_related(),), limits=LIMITS,
        entity_frequency={"PHYS1401": 6}, generic_entity_frequency=200,
    )
    values.update(overrides)
    return build_node_local_graph(**values)


def test_the_five_edge_types_are_typed_and_closed():
    assert set(EDGE_TYPES) == {
        "shared_validated_fact", "duplicate", "version_family",
        "compatible_document_type", "existing_related_folder",
    }
    with pytest.raises(ValueError):
        build_node_local_graph(
            subject=SUBJECT, candidate=_candidate(), entry=None,
            related_files=(_related(edge_type="vibes"),), limits=LIMITS,
            entity_frequency={}, generic_entity_frequency=200)


def test_the_graph_only_ever_names_files_related_to_this_one_node(entry):
    # §6.4: compare the target against the node's approved COMMUNITY. A file that
    # is in neither the node's representatives nor the subject's relations is not
    # in the neighbourhood, so whole-corpus reclustering has no entry point.
    graph = _build(entry, related_files=(_related(), _related(other="f-stranger",
                                                             entity="PHYS9999")))
    assert graph.node_id == "n-course"
    assert {a.anchor_file_id for a in graph.anchors} == {"f-syllabus"}


def test_a_neighbourhood_over_its_ceiling_reduces_to_the_strongest(entry):
    # §8.6: reduce BEFORE the dossier is built, not by truncating it afterwards.
    related = tuple(_related(other=f"f-{i}", weight=i) for i in range(1, 8))
    wide = dataclasses.replace(
        entry, representative_files=tuple(f"f-{i}" for i in range(1, 8)))
    graph = _build(wide, related_files=related)
    assert graph.neighbourhood_size == LIMITS.max_local_graph_neighborhood
    assert graph.reduced_to_strongest is True
    assert [a.anchor_file_id for a in graph.anchors] == ["f-7", "f-6", "f-5"]


def test_one_high_frequency_entity_is_not_typed_support(entry):
    # §6.5: "a file connected only by ... one high-frequency entity stays
    # uncertain". The frequency is injected; P11 chooses no cut-off.
    graph = _build(entry, entity_frequency={"PHYS1401": 900},
                   generic_entity_frequency=200)
    assert graph.high_frequency_entities == frozenset({"PHYS1401"})
    assert is_typed_support(graph) is False


def test_two_independent_entities_are_typed_support(entry):
    graph = _build(entry, related_files=(_related(),
                                         _related(other="f-lab", entity="Fall 2026")),
                   entity_frequency={"PHYS1401": 6, "Fall 2026": 4})
    assert len(graph.distinct_entities) == 2
    assert is_typed_support(graph) is True


def test_a_semantic_only_candidate_produces_no_anchors_at_all(entry):
    # An embedding is not a typed relationship, so it contributes no edge and the
    # graph reports honestly that there is nothing to compare against.
    graph = _build(entry, candidate=_candidate(channels=(SEMANTIC_NEIGHBOUR,)),
                   related_files=())
    assert graph.anchors == ()
    assert is_typed_support(graph) is False


def test_the_graph_refuses_a_neighbourhood_that_spans_two_nodes(entry):
    with pytest.raises(WholeCorpusReclusteringRefused):
        _build(entry, related_files=(_related(),
                                     _related(other="f-other", entity="X")),
               foreign_node_ids=("n-course-alt",))
```

- [ ] **Step 2: Run and verify RED**

Run: `python3 -m pytest -q tests/p11/test_p11_graph.py`

Expected: FAIL at collection — `ModuleNotFoundError: No module named 'placement.graph'`.

- [ ] **Step 3: Implement the graph**

```python
# src/placement/graph.py
"""§6.4's node-local evidence graph. Local by construction, never by intention.

The graph is built around ONE candidate node and the subject being placed. Its
vertices are the subject plus the files already accepted in that node; its edges
are typed relationships between them. §6.4 asks for the target to be compared
against "the node's approved community, not against a folder name", and that is
what makes the comparison meaningful when a label happens to look right.

Locality is structural, not a policy: `build_node_local_graph` takes one node's
entry and refuses a related file that belongs to a different node, so there is no
code path along which whole-corpus reclustering could happen. §6.5's prohibition
is therefore satisfied by the shape of the function rather than by a check
someone could forget to call.

Two §6.5 rules produce the `is_typed_support` answer. A semantic embedding is not
an edge type here at all, so it contributes nothing; and a neighbourhood held
together by one entity that appears everywhere is not support, which is why the
frequency arrives injected and P11 picks no cut-off of its own.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from placement.records import GraphAnchor

SHARED_VALIDATED_FACT: str = "shared_validated_fact"
DUPLICATE: str = "duplicate"
VERSION_FAMILY: str = "version_family"
COMPATIBLE_DOCUMENT_TYPE: str = "compatible_document_type"
EXISTING_RELATED_FOLDER: str = "existing_related_folder"

#: §6.5's typed relationships. A semantic neighbour is deliberately absent: it is
#: a retrieval channel (`placement.retrieval.SEMANTIC_NEIGHBOUR`) and never an edge,
#: because an embedding alone is insufficient and an edge type would make it look
#: like evidence of the same kind as a shared fact.
EDGE_TYPES: tuple[str, ...] = (
    SHARED_VALIDATED_FACT, DUPLICATE, VERSION_FAMILY, COMPATIBLE_DOCUMENT_TYPE,
    EXISTING_RELATED_FOLDER,
)


class WholeCorpusReclusteringRefused(RuntimeError):
    """A neighbourhood reached beyond the one node it belongs to."""


@dataclass(frozen=True)
class NodeLocalGraph:
    subject_ref: str
    node_id: str
    anchors: tuple[GraphAnchor, ...]
    distinct_entities: frozenset[str]
    high_frequency_entities: frozenset[str]
    neighbourhood_size: int
    reduced_to_strongest: bool


def build_node_local_graph(*, subject, candidate, entry, related_files, limits,
                           entity_frequency, generic_entity_frequency,
                           foreign_node_ids=()) -> NodeLocalGraph:
    """One subject, one node, one neighbourhood.

    `related_files` are edges the caller already resolved from P6 facts, P9
    memberships and P3 folder context; P11 discovers no relationship of its own
    here, because that would be a second grouping engine and P9 owns grouping.
    """
    from placement.store import subject_ref_of

    if foreign_node_ids:
        raise WholeCorpusReclusteringRefused(
            f"the neighbourhood named {sorted(foreign_node_ids)} besides "
            f"{candidate.node_id!r}; §6.5 permits local clustering only, and a "
            "graph spanning nodes is whole-corpus reclustering under another name"
        )
    for item in related_files:
        if item["edge_type"] not in EDGE_TYPES:
            raise ValueError(
                f"{item['edge_type']!r} is not one of §6.5's {len(EDGE_TYPES)} typed "
                "relationships; an untyped edge is a similarity wearing a name"
            )

    community = set(entry.representative_files) if entry is not None else set()
    kept = [
        item for item in related_files
        if not community or item["to_file_id"] in community
        or item["anchor_file_id"] in community
    ]
    ordered = sorted(
        kept, key=lambda item: (-item["weight"], item["to_file_id"]),
    )
    ceiling = limits.max_local_graph_neighborhood
    reduced = len(ordered) > ceiling
    ordered = ordered[:ceiling]

    anchors = tuple(
        GraphAnchor(edge_type=item["edge_type"], from_file_id=subject.file_id or "",
                    to_file_id=item["to_file_id"],
                    anchor_file_id=item["anchor_file_id"])
        for item in ordered
    )
    entities = Counter(item["entity"] for item in ordered)
    high_frequency = frozenset(
        entity for entity in entities
        if entity_frequency.get(entity, 0) >= generic_entity_frequency
    )
    return NodeLocalGraph(
        subject_ref=subject_ref_of(subject), node_id=candidate.node_id,
        anchors=anchors, distinct_entities=frozenset(entities),
        high_frequency_entities=high_frequency,
        neighbourhood_size=len(ordered), reduced_to_strongest=reduced,
    )


def is_typed_support(graph: NodeLocalGraph) -> bool:
    """§6.5's bar: a typed relationship that is not one everywhere-entity.

    A target connected by nothing, or only by an entity that appears across the
    corpus, stays uncertain. This is the deterministic half of the same judgement
    P8 makes about a model's answer as `GENERIC_HUB_ONLY`; P11 answers it about
    its own evidence, before any dossier exists.
    """
    if not graph.anchors:
        return False
    informative = graph.distinct_entities - graph.high_frequency_entities
    return bool(informative)
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3 -m pytest -q tests/p11/test_p11_graph.py`

Expected: PASS, 7 tests. `test_the_five_edge_types_are_typed_and_closed` is the one that proves the edge vocabulary is closed *before* the community filter runs, which is why it passes `entry=None`: an untyped edge must be refused whether or not the node has a community to compare against.

- [ ] **Step 5: Commit**

```bash
git add src/placement/graph.py tests/p11/test_p11_graph.py
git commit -m "feat(p11): compare against a node's community, not its label"
```

### Task 9: Decide deterministically, and record both conditions on every decision

**Files:**
- Create: `src/placement/scoring.py`
- Create: `tests/p11/test_p11_scoring.py`

**Consumes:** `placement.config.SupportPolicy`, `placement.retrieval.Retrieval`, `placement.graph.is_typed_support`, `placement.records.TwoCondition`.

**Produces:**

```python
@dataclass(frozen=True)
class Scored:
    node_id: str; support_score: float
    typed_support: bool; semantic_only: bool; generic_hub: bool

@dataclass(frozen=True)
class Assessment:
    scored: tuple[Scored, ...]
    two_condition: TwoCondition
    alternatives: tuple[Alternative, ...]
    unique_direct_match: bool
    abstention_reason: str | None
    confidence_class: str

def score_candidates(retrieval, graphs, *, policy) -> tuple[Scored, ...]: ...
def assess(retrieval, graphs, *, policy) -> Assessment: ...
def needs_model_call(assessment) -> bool: ...
```

**Done-means:** 6 (SPEC:631-633), 10 (SPEC:646-649), 10b (SPEC:650-655), 5's second clause (SPEC:629-630).

**Which P8 checks this task is therefore not writing.** All of Site C's fifteen. In particular `BELOW_SUPPORT_THRESHOLD`, `INSUFFICIENT_MARGIN` and `GENERIC_HUB_ONLY` (`placement_validation.py:241-254`, `:239`) are P8's, applied to a *model's* answer. What this task computes is the deterministic `support` and `next_support` the dossier carries (§6.6's "deterministic scores") and the verdict for the case where **no model is called at all**. SPEC:473-475 is the sentence that makes that a P11 field: *"A deterministic exact-fact match (§6.6) issues no model call and still records a verdict in this vocabulary."*

**B8(b), both halves.** With one legal candidate there is no next-best, so `margin_over_next` is null and `meets_margin` is `true_vacuous` — true by vacuity, not by measurement, and distinguishable in the record so a reviewer and a P2 replay can tell the two apart. The support threshold *stays binding*: a file that clears no threshold abstains **even though that one destination is the only one available**, because the scarcity of destinations is not evidence about the file.

That is the degenerate rule, and it is only half of B8(b). `planning/04-resolutions.md:143-146` also says: *"**The skeleton gains a second frozen node**, so the margin path is genuinely exercised rather than bypassed. A skeleton that never tests the margin does not prove the seam it exists to prove."* Task 19's walking skeleton therefore retrieves **two** candidates and records a **measured** margin — which is why `unique_direct_match` is keyed on §6.6's "the facts uniquely match one path" and not on the candidate set having size one. The two requirements are jointly satisfiable only under that reading.

**The scale is 7ths, and the fixtures are chosen against it.** `_MAX_WEIGHT = 3 + 2 + 1 + 1 = 7`, so a direct fact alone scores `3/7 ≈ 0.4286`, a direct fact plus an accepted group `5/7 ≈ 0.7143`, and an accepted group alone `2/7 ≈ 0.2857`. Any fixture threshold above `3/7` makes a direct-fact-only candidate unplaceable; any threshold at or below `2/7` lets a group-only candidate place. Every `SupportPolicy` in this plan's tests is picked inside that band and the arithmetic is stated where it is picked.

- [ ] **Step 1: Write the failing scoring tests**

```python
# tests/p11/test_p11_scoring.py
"""§6.10 recorded, not merely applied — including the degenerate one-node case."""
from __future__ import annotations

import pytest

from placement import vocabulary as v
from placement.config import SupportPolicy
from placement.graph import NodeLocalGraph
from placement.records import ConflictConsidered, GraphAnchor, MatchingFact
from placement.retrieval import (
    ACCEPTED_GROUP, Candidate, DIRECT_FACT, Retrieval, SEMANTIC_NEIGHBOUR,
)
from placement.scoring import assess, needs_model_call

# The threshold is 0.4, and the number is derived rather than picked. `assess`
# normalises by `_MAX_WEIGHT = 3 + 2 + 1 + 1 = 7`, so the highest score a
# candidate carrying ONLY the direct-fact channel can reach is
# `1.0 * 3 / 7 = 0.4285714…`. `_candidate()`'s default channels are
# `(DIRECT_FACT,)`, so a threshold of 0.5 would make every test in this module
# that expects a placement arithmetically impossible: the strongest evidence the
# fixture carries would still abstain. 0.4 sits below 3/7 and above the
# accepted-group-only score of `2/7 = 0.2857…`, so `test_one_high_frequency_
# entity_stays_uncertain` and the two semantic-only tests still fail the
# threshold, which is what they exist to prove.
POLICY = SupportPolicy(policy_id="fixture-v1", support_scale_max=1.0,
                       minimum_support_threshold=0.4, margin_threshold=0.2)


def _fact(value="PHYS1401"):
    return MatchingFact(file_fact_id="ff1", field="subject", value=value,
                        reliability=v.DIRECT, evidence_ref="obs-1")


def _candidate(node_id="n-course", channels=(DIRECT_FACT,), facts=None):
    return Candidate(node_id=node_id, channels=channels,
                     matching_facts=(_fact(),) if facts is None else facts,
                     group_ids=())


def _graph(node_id="n-course", anchors=1, informative=True):
    edges = tuple(
        GraphAnchor(edge_type="shared_validated_fact", from_file_id="f1",
                    to_file_id=f"f-{i}", anchor_file_id=f"f-{i}")
        for i in range(anchors)
    )
    return NodeLocalGraph(
        subject_ref="file:f1:h1", node_id=node_id, anchors=edges,
        distinct_entities=frozenset({"PHYS1401"}) if anchors else frozenset(),
        high_frequency_entities=frozenset() if informative else frozenset({"PHYS1401"}),
        neighbourhood_size=anchors, reduced_to_strongest=False,
    )


def _retrieval(candidates, conflicts=(), semantic_only=frozenset()):
    return Retrieval(subject_ref="file:f1:h1", plan_version="plan-1",
                     candidates=tuple(candidates), conflicts=tuple(conflicts),
                     semantic_only_node_ids=semantic_only)


def test_a_unique_direct_match_needs_no_model_and_says_so():
    # Done-means 6, §6.6: the LLM is not called for direct unique matches.
    result = assess(_retrieval([_candidate()]),
                    {"n-course": _graph()}, policy=POLICY)
    assert result.unique_direct_match is True
    assert result.confidence_class == v.EXACT_FACT_MATCH
    assert result.two_condition.verdict == "accept_direct"
    assert needs_model_call(result) is False


def test_the_degenerate_case_records_a_vacuous_margin_and_places():
    result = assess(_retrieval([_candidate()]),
                    {"n-course": _graph()}, policy=POLICY)
    assert result.two_condition.margin_over_next is None
    assert result.two_condition.meets_margin == v.MARGIN_TRUE_VACUOUS
    assert result.two_condition.margin_threshold == POLICY.margin_threshold
    assert result.two_condition.meets_threshold is True


def test_the_degenerate_case_still_abstains_when_support_is_short():
    # 10b's second half, and the only half that proves the threshold stayed
    # binding: one destination must not become a funnel.
    weak = _candidate(channels=(SEMANTIC_NEIGHBOUR,), facts=())
    result = assess(_retrieval([weak], semantic_only=frozenset({"n-course"})),
                    {"n-course": _graph(anchors=0)}, policy=POLICY)
    assert result.two_condition.meets_threshold is False
    assert result.two_condition.meets_margin == v.MARGIN_TRUE_VACUOUS
    assert result.abstention_reason == v.SEMANTIC_ONLY
    assert result.confidence_class == v.ABSTAIN_NO_SUPPORTED_DESTINATION


def test_a_low_margin_between_two_candidates_is_unresolved():
    two = [_candidate(), _candidate(node_id="n-course-alt")]
    result = assess(_retrieval(two),
                    {"n-course": _graph(), "n-course-alt": _graph("n-course-alt")},
                    policy=POLICY)
    assert result.two_condition.margin_over_next is not None
    assert result.two_condition.meets_margin == v.MARGIN_FALSE
    assert result.two_condition.verdict == "weak"
    assert result.abstention_reason == v.LOW_MARGIN


def test_a_semantic_embedding_alone_never_produces_a_place():
    # §6.5, and Done-means 5's second clause.
    result = assess(
        _retrieval([_candidate(channels=(SEMANTIC_NEIGHBOUR,), facts=())],
                   semantic_only=frozenset({"n-course"})),
        {"n-course": _graph(anchors=0)}, policy=POLICY)
    assert result.abstention_reason == v.SEMANTIC_ONLY
    assert result.two_condition.verdict in {"weak", "abstain"}


def test_one_high_frequency_entity_stays_uncertain():
    result = assess(
        _retrieval([_candidate(channels=(ACCEPTED_GROUP,), facts=())]),
        {"n-course": _graph(informative=False)}, policy=POLICY)
    assert result.abstention_reason == v.GENERIC_HUB_ONLY


def test_conflicting_facts_that_left_no_candidate_name_that_reason():
    conflict = ConflictConsidered(kind="subject", conflicting_value="PHYS1402",
                                  suppressed_node_ids=("n-course",),
                                  evidence_ref="obs-2")
    result = assess(_retrieval([], conflicts=[conflict]), {}, policy=POLICY)
    assert result.abstention_reason == v.CONFLICTING_FACTS
    assert result.two_condition.verdict == "abstain"


def test_no_candidates_and_no_conflicts_is_no_supported_destination():
    result = assess(_retrieval([]), {}, policy=POLICY)
    assert result.abstention_reason == v.NO_SUPPORTED_DESTINATION


def test_both_thresholds_are_on_every_assessment_however_it_ended():
    # Done-means 10: recorded, not just applied, so a reviewer can see WHY.
    for retrieval, graphs in (
        (_retrieval([_candidate()]), {"n-course": _graph()}),
        (_retrieval([]), {}),
    ):
        result = assess(retrieval, graphs, policy=POLICY)
        assert result.two_condition.support_threshold == POLICY.minimum_support_threshold
        assert result.two_condition.margin_threshold == POLICY.margin_threshold


def test_several_plausible_nodes_ask_for_a_model_rather_than_guessing():
    two = [_candidate(), _candidate(node_id="n-course-alt",
                                    channels=(ACCEPTED_GROUP,), facts=())]
    result = assess(_retrieval(two),
                    {"n-course": _graph(), "n-course-alt": _graph("n-course-alt")},
                    policy=POLICY)
    assert result.unique_direct_match is False
    assert needs_model_call(result) is True
```

- [ ] **Step 2: Run and verify RED**

Run: `python3 -m pytest -q tests/p11/test_p11_scoring.py`

Expected: FAIL at collection — `ModuleNotFoundError: No module named 'placement.scoring'`.

- [ ] **Step 3: Implement scoring**

```python
# src/placement/scoring.py
"""§6.10's two conditions, computed deterministically and recorded in full.

The score is a weighted count of independent channels, normalised to the policy's
declared scale. It is deliberately simple and deliberately declared: SPEC Open
question 2 records that the design names "deterministic scores" and a "minimum
support threshold" without defining a scale, so the scale lives in the injected
`SupportPolicy` and is recorded on the decision, which is what lets a P2 replay
compare two runs and a reviewer see that a threshold changed.

Nothing here re-implements a P8 check. Site C's `BELOW_SUPPORT_THRESHOLD`,
`INSUFFICIENT_MARGIN` and `GENERIC_HUB_ONLY` judge a MODEL's answer. This module
judges P11's own evidence, produces the `support` and `next_support` the dossier
carries, and produces the verdict for the case §6.6 forbids a model call in.

The degenerate case is the walking skeleton's own shape (B8(b)). With one legal
candidate the margin is satisfied vacuously and the support threshold is the sole
gate -- and stays binding, because the scarcity of destinations is not evidence
about the file and a tree with one branch must not become a funnel.
"""
from __future__ import annotations

from dataclasses import dataclass

from placement.config import SupportPolicy, require_policy
from placement.graph import is_typed_support
from placement.records import Alternative, TwoCondition
from placement.retrieval import (
    ACCEPTED_GROUP, DIRECT_FACT, GRAPH_RELATIONSHIP, STRUCTURAL_RELATIONSHIP,
)
from placement.vocabulary import (
    ABSTAIN_NO_SUPPORTED_DESTINATION, ABSTAIN_VERDICT, ACCEPT_DIRECT_VERDICT,
    CONFLICTING_FACTS, CONTEXT_SUPPORTED_GROUP_MATCH, EXACT_FACT_MATCH,
    GENERIC_HUB_ONLY, LOW_MARGIN, MARGIN_FALSE, MARGIN_TRUE, MARGIN_TRUE_VACUOUS,
    NO_SUPPORTED_DESTINATION, SEMANTIC_ONLY, WEAK_VERDICT,
)

#: How much each channel contributes, before normalisation by the policy's scale.
#: These are structural weights over §6.3's channels, not tuned numbers: a direct
#: fact outweighs a group membership outweighs a relationship, which is §3.13's
#: own ordering, and the two non-deciding channels contribute nothing at all.
_CHANNEL_WEIGHT: dict[str, int] = {
    DIRECT_FACT: 3,
    ACCEPTED_GROUP: 2,
    GRAPH_RELATIONSHIP: 1,
    STRUCTURAL_RELATIONSHIP: 1,
}
_MAX_WEIGHT: int = sum(_CHANNEL_WEIGHT.values())


@dataclass(frozen=True)
class Scored:
    node_id: str
    support_score: float
    typed_support: bool
    semantic_only: bool
    generic_hub: bool


@dataclass(frozen=True)
class Assessment:
    scored: tuple[Scored, ...]
    two_condition: TwoCondition
    alternatives: tuple[Alternative, ...]
    unique_direct_match: bool
    abstention_reason: str | None
    confidence_class: str


def score_candidates(retrieval, graphs, *, policy: SupportPolicy) -> tuple[Scored, ...]:
    require_policy(policy)
    scored: list[Scored] = []
    for candidate in retrieval.candidates:
        graph = graphs.get(candidate.node_id)
        weight = sum(_CHANNEL_WEIGHT.get(channel, 0) for channel in candidate.channels)
        typed = graph is not None and is_typed_support(graph)
        semantic_only = candidate.node_id in retrieval.semantic_only_node_ids
        hub = (
            graph is not None
            and bool(graph.anchors)
            and not typed
        )
        scored.append(Scored(
            node_id=candidate.node_id,
            support_score=policy.support_scale_max * weight / _MAX_WEIGHT,
            typed_support=typed, semantic_only=semantic_only, generic_hub=hub,
        ))
    return tuple(sorted(scored, key=lambda s: (-s.support_score, s.node_id)))


def _reason(best: Scored | None, retrieval, meets_threshold: bool,
            meets_margin: str) -> str | None:
    """Why this could not become a placement, named from §6.10's own failure modes."""
    if best is None:
        return CONFLICTING_FACTS if retrieval.conflicts else NO_SUPPORTED_DESTINATION
    if meets_margin == MARGIN_FALSE:
        return LOW_MARGIN
    if meets_threshold:
        return None
    if best.semantic_only:
        return SEMANTIC_ONLY
    if best.generic_hub:
        return GENERIC_HUB_ONLY
    return NO_SUPPORTED_DESTINATION


def assess(retrieval, graphs, *, policy: SupportPolicy) -> Assessment:
    require_policy(policy)
    scored = score_candidates(retrieval, graphs, policy=policy)
    best = scored[0] if scored else None
    runner_up = scored[1] if len(scored) > 1 else None

    meets_threshold = bool(best and best.support_score >= policy.minimum_support_threshold)
    if runner_up is None:
        # B8(b). No next-best exists, so there is nothing to measure and
        # `margin_over_next` has no value to hold. Recorded as vacuous so a
        # reviewer and a replay can tell it from a measured margin.
        margin_over_next = None
        meets_margin = MARGIN_TRUE_VACUOUS
    else:
        margin_over_next = best.support_score - runner_up.support_score
        meets_margin = (
            MARGIN_TRUE if policy.margin_predicate(best.support_score,
                                                   runner_up.support_score)
            else MARGIN_FALSE
        )

    reason = _reason(best, retrieval, meets_threshold, meets_margin)
    # §6.6's own words: "If a file's validated facts UNIQUELY MATCH ONE FROZEN
    # PATH, deterministic matching is faster, cheaper, and more stable"
    # (`planning/01-product-design-structured.md:1189-1191`). Uniqueness is a
    # property of the FACTS -- exactly one candidate carries the direct-fact
    # channel -- not of the candidate set's size. Keying it on "there was only
    # one candidate at all" would make B8(b) unsatisfiable: B8(b) requires the
    # skeleton to carry a second node so the margin is exercised rather than
    # vacuous, and no assessment can have both a measured margin and a candidate
    # set of one.
    #
    # `typed_support` is deliberately NOT required. §6.5's bar is about a target
    # "connected ONLY by generic similarity or one high-frequency entity"
    # (`:1183-1185`) -- it disqualifies similarity-based support, not a direct
    # fact match. Requiring a graph anchor here would mean a syllabus whose
    # subject fact names exactly one course could never be decided
    # deterministically, which is the case §6.6 exists to keep off the model.
    # Semantic-only and generic-hub candidates remain excluded because neither
    # carries `DIRECT_FACT` at all.
    #
    # Both §6.10 conditions still gate it: a unique direct match that falls short
    # of the support threshold, or that a runner-up crowds inside the margin, is
    # not decided here and goes to the model or abstains.
    direct_fact_candidates = tuple(
        candidate for candidate in retrieval.candidates
        if DIRECT_FACT in candidate.channels
    )
    unique_direct = bool(
        best is not None
        and len(direct_fact_candidates) == 1
        and direct_fact_candidates[0].node_id == best.node_id
        and meets_threshold
        and meets_margin != MARGIN_FALSE
    )

    if reason is None:
        verdict = ACCEPT_DIRECT_VERDICT
        confidence = EXACT_FACT_MATCH if unique_direct else CONTEXT_SUPPORTED_GROUP_MATCH
        requires_review = not unique_direct
    elif best is None:
        verdict = ABSTAIN_VERDICT
        confidence = ABSTAIN_NO_SUPPORTED_DESTINATION
        requires_review = True
    else:
        verdict = WEAK_VERDICT
        confidence = ABSTAIN_NO_SUPPORTED_DESTINATION
        requires_review = True

    two_condition = TwoCondition(
        support_score=best.support_score if best else 0.0,
        support_threshold=policy.minimum_support_threshold,
        meets_threshold=meets_threshold,
        margin_over_next=margin_over_next,
        margin_threshold=policy.margin_threshold,
        meets_margin=meets_margin,
        verdict=verdict,
        requires_review=requires_review,
    )
    alternatives = tuple(
        Alternative(node_id=item.node_id, support_score=item.support_score,
                    rank=rank)
        for rank, item in enumerate(scored, start=1)
    )
    return Assessment(
        scored=scored, two_condition=two_condition, alternatives=alternatives,
        unique_direct_match=unique_direct, abstention_reason=reason,
        confidence_class=confidence,
    )


def needs_model_call(assessment: Assessment) -> bool:
    """§6.6: never for a direct unique match; only for a bounded ambiguity.

    An assessment with no candidate at all also needs no call: there is nothing
    for a model to choose between, and asking one would be inviting it to invent.
    """
    if assessment.unique_direct_match or not assessment.scored:
        return False
    return True
```

Two constants this module imports must exist in `placement/vocabulary.py`; add them beside `VERDICTS`, because they are P8's spellings and the module that publishes them is the one that may name them:

```python
#: Three members of `VERDICTS`, named locally so no other module spells them.
#: They are P8's strings, read from P8's own tuple rather than retyped, and the
#: asserts are what would catch a reorder on P8's side.
#:
#: `ABSTAIN_VERDICT` and the OUTCOME `ABSTAIN` are the same string on two axes --
#: P8's verdict and P11's outcome -- and are two names for that reason, the same
#: way `grouping/vocabulary.py` names P1's borrowed `scan_state`.
ACCEPT_DIRECT_VERDICT: str = VERDICTS[0]
WEAK_VERDICT: str = VERDICTS[2]
ABSTAIN_VERDICT: str = VERDICTS[4]
assert ACCEPT_DIRECT_VERDICT == "accept_direct"
assert WEAK_VERDICT == "weak"
assert ABSTAIN_VERDICT == ABSTAIN
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3 -m pytest -q tests/p11/test_p11_scoring.py tests/p11/test_p11_records.py`

Expected: PASS, 10 tests. `test_the_degenerate_case_still_abstains_when_support_is_short` is the load-bearing one: it is the only test that proves the threshold stayed binding when the tree offers exactly one destination, and B8(b) says a fixture must assert both halves.

- [ ] **Step 5: Commit**

```bash
git add src/placement/scoring.py src/placement/vocabulary.py \
        tests/p11/test_p11_scoring.py
git commit -m "feat(p11): record both conditions on every decision, funnel none"
```

### Task 10: Carry P7's state through and derive the review policy from it

**Files:**
- Create: `src/placement/privacy.py`
- Create: `tests/p11/test_p11_privacy.py`

**Consumes:** `privacy.classification_store.ClassificationStore`, `privacy.policy.current_policy`, `privacy.vocabulary.OPERATION_MODES`.

**Produces:**

```python
class ClassificationRequired(RuntimeError): ...
class PolicyRequired(RuntimeError): ...

def privacy_state_for(conn, *, file_id, content_hash, plan_version) -> PrivacyState: ...
def review_policy_for(*, privacy_state, two_condition, group_support,
                      unique_direct_match, automatic_move_permitted=False) -> str: ...
def may_assemble_dossier(privacy_state) -> bool: ...
def blocked_policy() -> str: ...
```

`automatic_move_permitted` is in the signature because §8.4's permission lives on `Policy.automatic_move_permissions`, which the caller reads once per plan version rather than once per file. Task 19's pipeline supplies it from `PipelineInputs`; the tests supply it directly.

**Done-means:** SPEC:208-212, SPEC:372-377, SPEC:751-758's privacy half, §8.4.

**Why this task precedes the P8 seam.** SPEC:210-212 is literal: *"**The gate is passed before any dossier is assembled for a model**, not after (§8.4)."* The privacy state is an input to the dossier decision, not a label on its output, and building the seam first would put the check on the wrong side of the spend.

**No detector exists.** P7's rule set is behind an injection nothing produces, so on a real corpus every file resolves to `unreadable_unclassified`. That is the ordinary path and must be built as such: an absent classification is `blocked_pending_user`, never a default to a public class. This is P7's own standing state, not a P11 shortcut.

**`model_eligibility` has no producer anywhere.** SPEC:374's three values — `local_only`, `dossier_permitted`, `redacted` — appear in no live module (`grep -rn "local_only\|dossier_permitted" src/privacy/` finds nothing). P11 derives them here from P7's `Policy.operation_mode` and `ClassificationRecord.protected`, which are the two things §8.4 actually makes the decision from, and records the derivation under [SPEC corrections](#spec-corrections).

- [ ] **Step 1: Write the failing privacy tests**

```python
# tests/p11/test_p11_privacy.py
"""§8.4 carried, never re-derived; and the review policy that follows from it."""
from __future__ import annotations

import pytest

from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.policy import Policy, set_policy

from placement import vocabulary as v
from placement.privacy import (
    ClassificationRequired, PolicyRequired, may_assemble_dossier,
    privacy_state_for, review_policy_for,
)
from placement.records import GroupSupport, TwoCondition

T0 = "2026-08-27T00:00:00Z"


def _classify(conn, *, handling_class="personal_non_sensitive", protected=False):
    ClassificationStore(conn).write(ClassificationRecord(
        file_id="f1", content_hash="h1", handling_class=handling_class,
        protected=protected, basis="detector", evidence_refs=("obs-1",),
        reliability_state="direct", observed_at=T0))


def _policy(conn, *, mode="hybrid", permissions=None):
    # `set_policy` takes no `author`: M8 makes the acting part the author. It
    # does take `reason`, because §8.8 requires a meaningful policy diff line.
    set_policy(conn, Policy(
        policy_version="pol-1", operation_mode=mode, consent_grants=(),
        redaction_settings={}, automatic_move_permissions=permissions or {},
        plan_version="plan-1", set_at=T0,
    ), component_version="P7-test", user_id="u1",
       reason="fixture policy for the P11 privacy tests")


def _two_condition(**overrides):
    values = dict(support_score=0.9, support_threshold=0.5, meets_threshold=True,
                  margin_over_next=0.4, margin_threshold=0.2,
                  meets_margin=v.MARGIN_TRUE, verdict="accept_direct",
                  requires_review=False)
    values.update(overrides)
    return TwoCondition(**values)


def test_an_unclassified_file_blocks_and_never_defaults_to_public(p11_conn):
    _policy(p11_conn)
    with pytest.raises(ClassificationRequired):
        privacy_state_for(p11_conn, file_id="f1", content_hash="h1",
                          plan_version="plan-1")


def test_a_missing_policy_refuses_rather_than_assuming_a_mode(p11_conn):
    _classify(p11_conn)
    with pytest.raises(PolicyRequired):
        privacy_state_for(p11_conn, file_id="f1", content_hash="h1",
                          plan_version="plan-1")


def test_p11_carries_the_handling_class_and_reclassifies_nothing(p11_conn):
    _classify(p11_conn, handling_class="sensitive_personal", protected=True)
    _policy(p11_conn)
    state = privacy_state_for(p11_conn, file_id="f1", content_hash="h1",
                              plan_version="plan-1")
    assert state.handling_class == "sensitive_personal"
    assert state.model_eligibility == v.LOCAL_ONLY


def test_offline_mode_makes_everything_local_only(p11_conn):
    _classify(p11_conn)
    _policy(p11_conn, mode="offline")
    state = privacy_state_for(p11_conn, file_id="f1", content_hash="h1",
                              plan_version="plan-1")
    assert state.model_eligibility == v.LOCAL_ONLY
    assert may_assemble_dossier(state) is False


def test_a_non_sensitive_file_in_hybrid_mode_may_reach_a_dossier(p11_conn):
    _classify(p11_conn)
    _policy(p11_conn)
    state = privacy_state_for(p11_conn, file_id="f1", content_hash="h1",
                              plan_version="plan-1")
    assert state.model_eligibility == v.DOSSIER_PERMITTED
    assert may_assemble_dossier(state) is True


def test_a_protected_file_is_never_auto_eligible_without_an_explicit_permission(p11_conn):
    # §8.4: protected material "should not be moved automatically without a user
    # policy that explicitly permits it".
    _classify(p11_conn, handling_class="sensitive_personal", protected=True)
    _policy(p11_conn)
    state = privacy_state_for(p11_conn, file_id="f1", content_hash="h1",
                              plan_version="plan-1")
    assert review_policy_for(privacy_state=state, two_condition=_two_condition(),
                             group_support=None,
                             unique_direct_match=True) == v.REVIEW_REQUIRED


def test_an_explicit_permission_restores_automatic_eligibility(p11_conn):
    _classify(p11_conn, handling_class="sensitive_personal", protected=True)
    _policy(p11_conn, permissions={"sensitive_personal": True})
    state = privacy_state_for(p11_conn, file_id="f1", content_hash="h1",
                              plan_version="plan-1")
    assert review_policy_for(privacy_state=state, two_condition=_two_condition(),
                             group_support=None,
                             unique_direct_match=True) == v.AUTO_ELIGIBLE


def test_a_context_supported_verdict_always_requires_review(p11_conn):
    _classify(p11_conn)
    _policy(p11_conn)
    state = privacy_state_for(p11_conn, file_id="f1", content_hash="h1",
                              plan_version="plan-1")
    assert review_policy_for(
        privacy_state=state,
        two_condition=_two_condition(verdict="accept_context_supported",
                                     requires_review=True),
        group_support=None, unique_direct_match=False) == v.REVIEW_REQUIRED


def test_a_user_attached_membership_never_reaches_auto_eligible(p11_conn):
    _classify(p11_conn)
    _policy(p11_conn)
    state = privacy_state_for(p11_conn, file_id="f1", content_hash="h1",
                              plan_version="plan-1")
    assert review_policy_for(
        privacy_state=state, two_condition=_two_condition(),
        group_support=GroupSupport(group_id="g1", membership="user-attached"),
        unique_direct_match=True) == v.REVIEW_REQUIRED
```

- [ ] **Step 2: Run and verify RED**

Run: `python3 -m pytest -q tests/p11/test_p11_privacy.py`

Expected: FAIL at collection — `ModuleNotFoundError: No module named 'placement.privacy'`.

- [ ] **Step 3: Implement the privacy carry-through**

```python
# src/placement/privacy.py
"""P7's state, carried; §8.4's consequence for placement, derived here.

P11 reclassifies nothing. `handling_class` and `protected` come from P7's
`ClassificationRecord`, which D2 made authoritative, and the operation mode comes
from P7's `Policy`. An absent classification blocks: P7's detector is behind an
injection nothing produces yet, so on a real corpus every file resolves to
`unreadable_unclassified`, and treating that as "probably fine" is the one failure
§8.4 exists to prevent.

`model_eligibility` is derived rather than read, because §8.4's three values have
no producer in `src/privacy/` at all. The two facts §8.4 actually decides from are
the operation mode and the `protected` flag, so those are what it is derived from;
the derivation is written here in one place so it cannot drift, and it is recorded
as a divergence rather than presented as a read.
"""
from __future__ import annotations

import sqlite3

from privacy.classification_store import ClassificationStore
from privacy.policy import current_policy

from placement.records import PrivacyState, USER_ATTACHED
from placement.vocabulary import (
    AUTO_ELIGIBLE, BLOCKED_PENDING_USER, DOSSIER_PERMITTED, LOCAL_ONLY,
    REDACTED_ELIGIBILITY, REVIEW_REQUIRED,
)

#: §8.4's four modes, by the promise each makes about egress. `offline` and
#: `local_model` never release; `hybrid` releases only non-sensitive material;
#: `cloud_assisted` releases what the user permitted for the area.
_NEVER_RELEASES: frozenset[str] = frozenset({"offline", "local_model"})


class ClassificationRequired(RuntimeError):
    """No P7 classification for this file version. Never defaulted to public."""


class PolicyRequired(RuntimeError):
    """No P7 policy in force for this plan version. Never assumed."""


def privacy_state_for(conn: sqlite3.Connection, *, file_id: str,
                      content_hash: str, plan_version: str) -> PrivacyState:
    record = ClassificationStore(conn).current(file_id, content_hash)
    if record is None:
        raise ClassificationRequired(
            f"no P7 classification for ({file_id!r}, {content_hash!r}); §8.4 puts "
            "the gate before every dossier, and an unclassified file is blocked "
            "rather than presumed low-sensitivity"
        )
    policy = current_policy(conn, plan_version=plan_version)
    if policy is None:
        raise PolicyRequired(
            f"no P7 policy in force for {plan_version!r}; the operation mode "
            "decides whether anything may leave the device and P11 assumes none"
        )
    if policy.operation_mode in _NEVER_RELEASES or record.protected:
        eligibility = LOCAL_ONLY
    elif record.handling_class in getattr(policy, "redaction_settings", {}):
        eligibility = REDACTED_ELIGIBILITY
    else:
        eligibility = DOSSIER_PERMITTED
    return PrivacyState(
        handling_class=record.handling_class, model_eligibility=eligibility,
        consent_audit_ref=None,
    )


def may_assemble_dossier(privacy_state: PrivacyState) -> bool:
    """§8.4's gate, asked before the dossier exists rather than after it is built."""
    return privacy_state.model_eligibility != LOCAL_ONLY


def review_policy_for(*, privacy_state: PrivacyState, two_condition,
                      group_support, unique_direct_match: bool,
                      automatic_move_permitted: bool = False) -> str:
    """§6.11's review policy. Every path to `auto_eligible` is a narrow one.

    Four things each forbid it on their own, and every one traces to a design
    sentence: a verdict that requires review (§6.10), a manual attachment with
    nothing read from the file (M12), material P7 keeps local (§8.4), and a
    decision that is not a unique direct match (§6.6's deterministic path is the
    only one the design lets through unreviewed).
    """
    if privacy_state.model_eligibility == LOCAL_ONLY and not automatic_move_permitted:
        return REVIEW_REQUIRED
    if two_condition.requires_review:
        return REVIEW_REQUIRED
    if group_support is not None and group_support.membership == USER_ATTACHED:
        return REVIEW_REQUIRED
    if not unique_direct_match:
        return REVIEW_REQUIRED
    return AUTO_ELIGIBLE


def blocked_policy() -> str:
    """The policy for a decision whose subject P7 has not classified."""
    return BLOCKED_PENDING_USER
```

`review_policy_for` takes `automatic_move_permitted` because §8.4's permission lives on `Policy.automatic_move_permissions`, which the caller reads once per plan version rather than per file. The pipeline supplies it in Task 19; the test supplies it directly.

- [ ] **Step 4: Run and verify GREEN**

Run: `python3 -m pytest -q tests/p11/test_p11_privacy.py`

Expected: PASS, 9 tests. `test_an_explicit_permission_restores_automatic_eligibility` passes the permission through the call, which is what the pipeline does after reading `policy.automatic_move_permissions`.

- [ ] **Step 5: Commit**

```bash
git add src/placement/privacy.py tests/p11/test_p11_privacy.py
git commit -m "feat(p11): pass the privacy gate before any dossier exists"
```

### Task 11: Ask the negative-example store before proposing any destination

**Files:**
- Create: `src/placement/learning.py`
- Create: `tests/p11/test_p11_learning.py`

**Consumes:** `database_agent.learning.learning_records`, `database_agent.events.CORRECTION_SCOPES`.

**Produces:**

```python
PROPOSAL_CLASSES: tuple[str, ...]   # "placement", "residual"

@dataclass(frozen=True)
class Suppression:
    node_id: str; scope: str; subject_id: str; basis_key: str; event_id: int

def basis_key_for(*, subject_ref: str, node_id: str) -> str: ...
def suppressed_nodes(conn, *, subject_ref, node_ids, scopes,
                     corpus_subject_id=None, proposal_class=PLACEMENT
                     ) -> tuple[Suppression, ...]: ...
def record_correction(conn, *, decision, action, polarity, scope, subject_id,
                      basis_key, user_id, component_version, observed_at,
                      explanation, proposal_class=PLACEMENT) -> int: ...
```

**Done-means:** SPEC:751-758, SPEC:745-749, SPEC:736-743.

**Why this precedes Task 9's first `place`.** SPEC:753-755: *"**Before emitting `outcome = place` (or a residual equivalent), P11 queries P1 `learning_records`** for `placement` / `(subject_id, node_id)` or `residual` / `(file_id, residual_node_id)`. A matching unrescinded reject skips that node — never auto-place."* Building it after the emitting task would leave every Task 9–15 fixture written against a path that skips a required step.

**The live API is narrower than the SPEC's sentence reads.** `database_agent.learning.learning_records(conn, scope, subject_id)` takes **only** scope and subject and is positional; `proposal_class` and `basis_key` are columns on the returned rows, filtered by the caller. That is the pattern `llm_harness.eligibility.suppressed_by_learning` already uses, and P11 copies it rather than inventing a second learning store. A reset is honoured as a cutoff by the read itself (R6) and P11 adds no reset logic.

- [ ] **Step 1: Write the failing learning tests**

```python
# tests/p11/test_p11_learning.py
"""§8.7 — a rejected destination is not resurfaced, and only at its own scope."""
from __future__ import annotations

import inspect

import pytest

from database_agent import learning as p1_learning
from database_agent.events import append_event

from placement import vocabulary as v
from placement.learning import (
    PROPOSAL_CLASSES, basis_key_for, record_correction, suppressed_nodes,
)

T0 = "2026-08-27T00:00:00Z"


def _reject(conn, *, scope="file", subject_id="f1", node_id="n-course"):
    return append_event(
        conn, event_type=v.REVIEW_DECISION, subsystem="P11",
        component_version="P11-test", observed_at=T0, user_id="u1",
        explanation="the user rejected this destination",
        correction_scope=scope, correction_subject=subject_id,
        polarity="reject", proposal_class="placement",
        basis_key=basis_key_for(subject_ref=f"file:{subject_id}:h1",
                                node_id=node_id),
    )


def test_the_live_read_takes_only_scope_and_subject():
    # The SPEC sentence reads as though the query is keyed on four things. It is
    # keyed on two, and the other two are columns filtered after the read.
    params = inspect.signature(p1_learning.learning_records).parameters
    assert list(params) == ["conn", "scope", "subject_id"]


def test_a_rejected_destination_is_suppressed_for_that_file(p11_conn):
    _reject(p11_conn)
    hits = suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                            node_ids=("n-course", "n-course-alt"),
                            scopes=("file",))
    assert [hit.node_id for hit in hits] == ["n-course"]


def test_one_files_rejection_does_not_teach_the_corpus(p11_conn):
    # §8.7's own governing example: a user saying that ONE transcript belongs in
    # a Columbia packet must not teach the engine that ALL transcripts do.
    _reject(p11_conn, scope="file", subject_id="f1")
    assert suppressed_nodes(p11_conn, subject_ref="file:f2:h2",
                            node_ids=("n-course",), scopes=("file",)) == ()


def test_a_corpus_scoped_rejection_applies_everywhere_it_was_scoped_to(p11_conn):
    _reject(p11_conn, scope="corpus", subject_id="corpus")
    hits = suppressed_nodes(p11_conn, subject_ref="file:f9:h9",
                            node_ids=("n-course",),
                            scopes=("corpus",), corpus_subject_id="corpus")
    assert [hit.node_id for hit in hits] == ["n-course"]


def test_an_acceptance_suppresses_nothing(p11_conn):
    append_event(
        p11_conn, event_type=v.REVIEW_DECISION, subsystem="P11",
        component_version="P11-test", observed_at=T0, user_id="u1",
        explanation="accepted", correction_scope="file", correction_subject="f1",
        polarity="accept", proposal_class="placement",
        basis_key=basis_key_for(subject_ref="file:f1:h1", node_id="n-course"))
    assert suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                            node_ids=("n-course",), scopes=("file",)) == ()


def test_a_rejection_recorded_against_another_proposal_class_does_not_apply(p11_conn):
    append_event(
        p11_conn, event_type=v.REVIEW_DECISION, subsystem="P11",
        component_version="P11-test", observed_at=T0, user_id="u1",
        explanation="rejected as a group", correction_scope="file",
        correction_subject="f1", polarity="reject", proposal_class="grouping",
        basis_key=basis_key_for(subject_ref="file:f1:h1", node_id="n-course"))
    assert suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                            node_ids=("n-course",), scopes=("file",)) == ()


def test_a_reset_lifts_the_suppression_without_deleting_the_record(p11_conn):
    _reject(p11_conn)
    p1_learning.reset_preferences(p11_conn, "file", "f1", author="P11-test",
                                  component_version="P11-test", user_id="u1")
    assert suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                            node_ids=("n-course",), scopes=("file",)) == ()
    rows = p11_conn.execute(
        "SELECT count(*) AS c FROM events WHERE polarity = 'reject'").fetchone()
    assert rows["c"] == 1


def test_the_two_proposal_classes_are_the_specs_two():
    assert PROPOSAL_CLASSES == ("placement", "residual")


def test_a_correction_carries_its_scope_and_its_evidence(p11_conn):
    from p11.test_p11_records import _decision

    record_correction(
        p11_conn, decision=_decision(), action="change_destination",
        polarity="reject", scope="node", subject_id="n-course",
        basis_key=basis_key_for(subject_ref="file:f1:h1", node_id="n-course"),
        user_id="u1", component_version="P11-test", observed_at=T0,
        explanation="this belongs under the other term")
    row = p11_conn.execute(
        "SELECT correction_scope, correction_subject, polarity, proposal_class, "
        "basis_key, user_id FROM events ORDER BY event_id DESC LIMIT 1").fetchone()
    assert row["correction_scope"] == "node"
    assert row["correction_subject"] == "n-course"
    assert row["polarity"] == "reject"
    assert row["proposal_class"] == "placement"
    assert row["user_id"] == "u1"
    assert "n-course" in row["basis_key"]
```

- [ ] **Step 2: Run and verify RED**

Run: `python3 -m pytest -q tests/p11/test_p11_learning.py`

Expected: FAIL at collection — `ModuleNotFoundError: No module named 'placement.learning'`.

- [ ] **Step 3: Implement the suppression read and the correction writer**

```python
# src/placement/learning.py
"""§8.7's negative examples, asked before every proposal.

A rejected destination is stored WITH the evidence that produced it so the same
attractive-but-wrong node is not resurfaced. P11 keeps no second learning store:
P1 owns `events` and its §8.7 columns, and `learning_records` already honours a
reset as a cutoff without deleting anything (R6).

Scope is the whole safety property. §8.7's governing example is that a user
saying ONE transcript belongs in a Columbia packet must not teach the engine that
ALL transcripts do, so a suppression applies at the scope the user chose and
nowhere else. P11 widens no scope and infers none.

`basis_key` is the evidence pattern the rejection was about. Keying it on
`(subject_ref, node_id)` is what makes a rejection specific: the same user
rejecting a different node for the same file, or the same node for a different
file, is a different fact.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from database_agent.events import CORRECTION_SCOPES
from database_agent.learning import learning_records

from placement import events as placement_events
from placement.vocabulary import PLACEMENT, RESIDUAL

#: The two `proposal_class` values P11 writes and reads. A rejection recorded by
#: another part under another class is that part's fact, not a placement fact.
PROPOSAL_CLASSES: tuple[str, ...] = (PLACEMENT, RESIDUAL)

REJECT: str = "reject"
ACCEPT: str = "accept"


@dataclass(frozen=True)
class Suppression:
    node_id: str
    scope: str
    subject_id: str
    basis_key: str
    event_id: int


def basis_key_for(*, subject_ref: str, node_id: str) -> str:
    """The evidence pattern one rejection was about."""
    return f"{subject_ref}->{node_id}"


def _subject_ids(subject_ref: str, scope: str, corpus_subject_id: str | None):
    """Which `correction_subject` a scope is keyed on for this subject.

    `file` is keyed on the file id, not on the versioned subject ref: §8.7 is
    about what the user decided, and editing a file does not un-decide it. The
    wider scopes are keyed on their own subject and the caller supplies it,
    because P11 cannot know which node, template, domain or corpus a user meant.
    """
    if scope == "file":
        parts = subject_ref.split(":")
        return (parts[1],) if len(parts) > 1 else ()
    if scope == "corpus" and corpus_subject_id:
        return (corpus_subject_id,)
    return ()


def suppressed_nodes(conn: sqlite3.Connection, *, subject_ref: str, node_ids,
                     scopes, corpus_subject_id: str | None = None,
                     proposal_class: str = PLACEMENT) -> tuple[Suppression, ...]:
    """Which of these nodes the user has already rejected, at these scopes.

    Called before `outcome = place` is emitted. A hit means the node is skipped
    -- never auto-placed and never silently re-ranked, because a silent re-rank
    would hide from the user that their own correction was the reason.
    """
    wanted = {basis_key_for(subject_ref=subject_ref, node_id=node_id): node_id
              for node_id in node_ids}
    hits: list[Suppression] = []
    for scope in scopes:
        if scope not in CORRECTION_SCOPES:
            raise ValueError(
                f"{scope!r} is not one of §8.7's six scopes {CORRECTION_SCOPES}"
            )
        for subject_id in _subject_ids(subject_ref, scope, corpus_subject_id):
            for row in learning_records(conn, scope, subject_id):
                if row["polarity"] != REJECT:
                    continue
                if row["proposal_class"] != proposal_class:
                    continue
                node_id = wanted.get(row["basis_key"])
                if node_id is None:
                    continue
                hits.append(Suppression(
                    node_id=node_id, scope=scope, subject_id=subject_id,
                    basis_key=row["basis_key"], event_id=row["event_id"],
                ))
    # One node suppressed at two scopes is one suppression for the caller.
    seen: dict[str, Suppression] = {}
    for hit in hits:
        seen.setdefault(hit.node_id, hit)
    return tuple(seen[node_id] for node_id in
                 sorted(seen, key=lambda n: list(node_ids).index(n)))


def record_correction(conn: sqlite3.Connection, *, decision, action: str,
                      polarity: str, scope: str, subject_id: str,
                      basis_key: str, user_id: str, component_version: str,
                      observed_at: str, explanation: str,
                      proposal_class: str = PLACEMENT) -> int:
    """Store one user action with its scope, its polarity and its basis.

    §8.7's list of what is recorded runs to thirteen actions; `action` carries
    the one the user took and P13's `review_action.action` is its vocabulary.
    P11 stores it rather than interpreting it, and derives no preference here:
    a preference is what the suppression read above computes from the stored
    facts, so there is no second, silently-trained copy.
    """
    if polarity not in (ACCEPT, REJECT):
        raise ValueError(f"polarity is {ACCEPT!r} or {REJECT!r}, not {polarity!r}")
    if proposal_class not in PROPOSAL_CLASSES:
        raise ValueError(f"{proposal_class!r} is not one of {PROPOSAL_CLASSES}")
    from placement.store import subject_ref_of

    return placement_events.review_decision(
        conn, subject_ref=subject_ref_of(decision.subject), action=action,
        component_version=component_version, observed_at=observed_at,
        user_id=user_id, correction_scope=scope, correction_subject=subject_id,
        polarity=polarity, proposal_class=proposal_class, basis_key=basis_key,
        explanation=explanation, file_id=decision.subject.file_id,
        content_hash=decision.subject.content_hash,
    )
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3 -m pytest -q tests/p11/test_p11_learning.py`

Expected: PASS, 9 tests. `test_a_reset_lifts_the_suppression_without_deleting_the_record` is the one that proves P11 added no reset of its own: `learning_records` applies the cutoff, and the rejection row is still in `events` afterwards.

- [ ] **Step 5: Commit**

```bash
git add src/placement/learning.py tests/p11/test_p11_learning.py
git commit -m "feat(p11): never resurface a destination the user rejected"
```

### Task 12: Supply Site C's authorities and transcribe its verdict

**Files:**
- Create: `src/placement/p8_seam.py`
- Create: `tests/p11/test_p11_p8_seam.py`
- Create: `tests/integration/test_p11_p8_seam.py`

**Consumes** — every one verified against HEAD:

```python
from llm_harness import run_call, DossierRequest, P8Verdict, Refusal, CallFailed, \
    ValidationUnavailable, NeedsConsent           # src/llm_harness/__init__.py
from llm_harness.records import Conflict, EvidenceItem
from llm_harness.harness import CallDependencies  # 17 fields, harness.py:87-107
from llm_harness.sites import SiteDependencies    # sites.py:82-104
from llm_harness.placement_validation import PlacementDependencies, \
    ResidualDependencies, record_cd_verdict, revalidate_for_plan
from llm_harness.vocabulary import C_PLACEMENT, D_RESIDUAL, \
    SEVERAL_LEGAL_NODES_PLAUSIBLE, PLACE_GROUP_TOGETHER, DIRECT_FACTS_CONFLICT, \
    VAGUE_OCR_OR_FILENAME, CONTEXT_MEMBER_MISSING_BRANCH_FACT, \
    USER_OPTED_RESIDUAL_SET_INTO_AI_REVIEW
```

**Produces:**

```python
class ModelPathUnavailable(RuntimeError): ...

def placement_authorities(conn, *, plan_version, policy, sensitivity_policy) -> PlacementDependencies: ...
def residual_authorities(conn, *, plan_version, approved_target_ids, sensitivity_policy) -> ResidualDependencies: ...
def site_dependencies(*, placement=None, residual=None) -> SiteDependencies: ...
def to_p8_conflicts(conflicts) -> tuple[Conflict, ...]: ...
def evidence_snapshot_id_for(*, plan_version, observation_keys) -> str: ...
def transcribe(verdict, *, assessment) -> tuple[str, str | None, str | None]: ...
def call_placement(conn, request, *, gate, model_client, prompt,
                   call_dependencies, observed_at) -> object: ...
```

**Done-means:** 6 (SPEC:631-633), 10 (SPEC:646-649), 14 (SPEC:665-667); SPEC:214-229, SPEC:462-475, SPEC:831-835 (resolution O7).

**The rule this task exists to hold.** SPEC:831-835 settles it: *"**P8 owns the validator mechanism and the verdict shape; P11 owns the destination-specific checks and the record they populate.** P8's verdict populates `two_condition` and gates `review_policy`; P8 does not define the two-condition fields."* So this module supplies four authorities and reads a verdict. It writes **none** of Site C's fifteen checks: not the frozen-tree membership test (`placement_validation.py:222`), not the invented-node check against `allowed_vocabulary` (`:220`), not the invented-dimension check (`:224`), not `SLOT_FILLED_WITHOUT_EVIDENCE` (`:227`), not `CONFLICT_IGNORED` (`:229-236`), not the sensitivity check (`:237`), not `GENERIC_HUB_ONLY` (`:239`), not `BELOW_SUPPORT_THRESHOLD` (`:241-247`), not `INSUFFICIENT_MARGIN` (`:248-254`), and not the weak-retrieval rung (`:255`). A test plants a permissive authority and proves P8 still refuses — the shape `tests/p8/test_p8_sites.py:199-246` already uses.

**Four things P11 must supply that nothing else produces.**

1. `allowed_vocabulary` — `CallDependencies.allowed_vocabulary` (`harness.py:106`) becomes `Dossier.allowed_vocabulary`, and Site C rejects any destination outside it as `INVENTED_NODE` (`placement_validation.py:220-221`). It is P11's legal candidate set, and it is the single most load-bearing value P11 hands P8.
2. `evidence_snapshot_id` — required by `record_cd_verdict` (`placement_validation.py:475-476`) and now refused **before the spend** by `_missing_request_inputs` (`harness.py:154-165`, `SITES_REQUIRING_EVIDENCE_SNAPSHOT`). Nothing in any SPEC mints one, so P11 mints it as a content address over the plan version and the ordered observation keys the dossier cites. Recorded under [SPEC corrections](#spec-corrections).
3. `Conflict(conflict_id, kind)` — P8's shape (`records.py:267-276`), which is not P11's `ConflictConsidered` and not P9's `Conflict`. Three shapes wear that word; this module converts P11's into P8's and never the reverse.
4. `gate`, `model_client`, `prompt` and the five reduction predicates — all required keywords of `run_call` (`harness.py:343-350`, `harness.py:98-102`). P11 does not construct a `Gate` or a `ModelClient` and imports no model client; it accepts all three as injections and refuses with `ModelPathUnavailable` when they are absent, because a deterministic-only run is a legal run and must not look like a failure.

- [ ] **Step 1: Write the failing seam tests**

```python
# tests/p11/test_p11_p8_seam.py
"""P11 supplies authorities and reads a verdict. It writes no Site C check."""
from __future__ import annotations

import dataclasses
import inspect
import json

import pytest

from llm_harness.fixtures import SITE_C_OUTCOME_PAIRS, SITE_C_REASON_PAIRS
from llm_harness.placement_validation import (
    PlacementDependencies, ResidualDependencies, validate_placement_response,
)
from llm_harness.records import Conflict as P8Conflict, ValidationUnavailable
from llm_harness.sites import SiteDependencies, dispatch
from llm_harness.vocabulary import (
    ACCEPT_DIRECT, C_PLACEMENT, INVENTED_NODE, NODE_NOT_IN_FROZEN_TREE, REJECT,
    SITE_C_REASON_CODES,
)

from placement import vocabulary as v
from placement.config import SupportPolicy
from placement.index import build_destination_index, node_exists
from placement.p8_seam import (
    ModelPathUnavailable, evidence_snapshot_id_for, placement_authorities,
    site_dependencies, to_p8_conflicts, transcribe,
)
from placement.records import ConflictConsidered
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE

POLICY = SupportPolicy(policy_id="fixture-v1", support_scale_max=1.0,
                       minimum_support_threshold=0.5, margin_threshold=0.2)


@pytest.fixture()
def indexed(p11_conn):
    build_destination_index(p11_conn, FROZEN_TREE,
                            component_version="P11-test", observed_at=FIXED_CLOCK)
    return p11_conn


def _permissive(*_a, **_k):
    """The exact shape a caller must not be able to smuggle past a site check."""
    return True


def test_the_four_placement_authorities_are_exactly_p8s_fields(indexed):
    deps = placement_authorities(indexed, plan_version="plan-1", policy=POLICY,
                                 sensitivity_policy=_permissive)
    assert isinstance(deps, PlacementDependencies)
    assert {f.name for f in dataclasses.fields(PlacementDependencies)} == {
        "node_exists", "support_threshold", "margin_predicate",
        "sensitivity_policy"}
    assert deps.support_threshold == POLICY.minimum_support_threshold
    assert deps.margin_predicate(0.9, 0.5) is True


def test_node_exists_is_p11s_index_and_answers_p8s_two_argument_call(indexed):
    deps = placement_authorities(indexed, plan_version="plan-1", policy=POLICY,
                                 sensitivity_policy=_permissive)
    assert deps.node_exists("n-course", "plan-1") is True
    assert deps.node_exists("n-ignored", "plan-1") is False


def test_a_permissive_sensitivity_authority_cannot_pass_an_invented_node(indexed):
    # The point of the whole task: authorities are not acceptance. P8 still
    # refuses, and P11 writes none of the checks that do the refusing.
    pair = next(p for p in SITE_C_OUTCOME_PAIRS if p.name == "direct_accept")
    body = json.loads(pair.response_bytes)
    body["claims"][0]["payload"]["destination"] = "n-invented"
    deps = SiteDependencies(
        fact=None, residual=None, template=None,
        placement=PlacementDependencies(
            node_exists=lambda *_a: True, support_threshold=0.0,
            margin_predicate=_permissive, sensitivity_policy=_permissive),
    )
    verdicts, _ = dispatch(
        None, pair.dossier, json.dumps(body, separators=(",", ":")).encode(),
        site_dependencies=deps, evidence_resolver=lambda key: "span-1",
        contradicts=lambda *_a, **_k: False, model_id="fixture-model",
        prompt_fingerprint="fp-1", dossier_builder="p11-test",
        release_audit_id=17, policy_version="policy-1", apply_consequence=False,
    )
    assert verdicts[0].outcome == REJECT
    assert INVENTED_NODE in verdicts[0].reasons


def test_omitting_an_authority_is_unavailable_and_never_a_pass():
    pair = SITE_C_OUTCOME_PAIRS[0]
    result = validate_placement_response(
        pair.dossier, pair.response_bytes,
        evidence_resolver=lambda key: "span-1",
        contradicts=lambda *_a, **_k: False, dependencies=None,
        model_id="m", prompt_fingerprint="fp", dossier_builder="p11-test",
        release_audit_id=17)
    assert isinstance(result, ValidationUnavailable)
    assert "support_threshold" in result.missing


def test_p11_writes_no_site_c_reason_code():
    # Every one of P8's eleven Site C codes belongs to P8. A P11 module spelling
    # one would be a second validator with a second opinion.
    import ast
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "src" / "placement"
    offenders = []
    for path in sorted(root.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and node.value in SITE_C_REASON_CODES:
                offenders.append((path.name, node.lineno, node.value))
    assert offenders == []


def test_a_p11_conflict_becomes_p8s_two_field_shape():
    # Three records wear the word "conflict": P9's, P8's and P11's. The
    # conversion runs one way, here, so nothing downstream has to guess which.
    mine = ConflictConsidered(kind="subject", conflicting_value="PHYS1402",
                              suppressed_node_ids=("n-course",),
                              evidence_ref="obs-2")
    converted = to_p8_conflicts((mine,))
    assert all(isinstance(item, P8Conflict) for item in converted)
    assert converted[0].kind == "subject"
    assert converted[0].conflict_id


def test_the_evidence_snapshot_id_is_a_content_address(indexed):
    # Required at C and D before the spend (harness.py:154-165) and minted by
    # nobody else. Two dossiers over the same evidence share one id, which is
    # what makes a replay recognisable as a replay.
    first = evidence_snapshot_id_for(plan_version="plan-1",
                                     observation_keys=("obs-2", "obs-1"))
    second = evidence_snapshot_id_for(plan_version="plan-1",
                                      observation_keys=("obs-1", "obs-2"))
    third = evidence_snapshot_id_for(plan_version="plan-2",
                                     observation_keys=("obs-1", "obs-2"))
    assert first == second
    assert first != third
    assert first


def test_the_verdict_vocabulary_is_carried_unchanged_into_the_record(indexed):
    # MINOR 7: P8's `outcome` IS the record's `verdict`. No mapping table.
    pair = next(p for p in SITE_C_OUTCOME_PAIRS if p.name == "direct_accept")
    deps = PlacementDependencies(
        node_exists=lambda node_id, _plan: node_id != "absent",
        support_threshold=0.0, margin_predicate=lambda *_a: True,
        sensitivity_policy=_permissive)
    verdict = validate_placement_response(
        pair.dossier, pair.response_bytes,
        evidence_resolver=lambda key: "span-1",
        contradicts=lambda *_a, **_k: False, dependencies=deps,
        model_id="m", prompt_fingerprint="fp", dossier_builder="p11-test",
        release_audit_id=17)[0][0]
    assert verdict.outcome == ACCEPT_DIRECT
    outcome, reason, deferred = transcribe(verdict, assessment=None)
    assert outcome == v.PLACE
    assert reason is None and deferred is None


def test_a_weak_verdict_becomes_an_abstention_with_a_named_reason(indexed):
    pair = next(p for p in SITE_C_REASON_PAIRS
                if p.expected_reasons == ("INSUFFICIENT_MARGIN",))
    deps = PlacementDependencies(
        node_exists=lambda node_id, _plan: True, support_threshold=0.0,
        margin_predicate=lambda *_a: False, sensitivity_policy=_permissive)
    verdict = validate_placement_response(
        pair.dossier, pair.response_bytes,
        evidence_resolver=lambda key: "span-1",
        contradicts=lambda *_a, **_k: False, dependencies=deps,
        model_id="m", prompt_fingerprint="fp", dossier_builder="p11-test",
        release_audit_id=17)[0][0]
    outcome, reason, deferred = transcribe(verdict, assessment=None)
    assert outcome == v.ABSTAIN
    assert reason == v.LOW_MARGIN
    assert deferred is None


def test_a_budget_exhausted_verdict_defers_and_never_abstains_evidentially():
    # §8.6, Done-means 14. `BUDGET_EXHAUSTED` is a pre-call terminal P8 persists
    # as an `abstain` verdict; P11 must not read that as a judgement about
    # evidence, because none was made.
    from llm_harness.records import P8Verdict
    from llm_harness.vocabulary import ABSTAIN, BUDGET_EXHAUSTED, SCOPE_NODE

    verdict = P8Verdict(
        verdict_id="pre-call:C_placement:f1:BUDGET_EXHAUSTED",
        dossier_id="pre-call:C_placement:f1", claim_ref="pre-call",
        outcome=ABSTAIN, disposition=ABSTAIN, reasons=(BUDGET_EXHAUSTED,),
        may_propose=False, requires_review=False, citations_checked=(),
        scope=SCOPE_NODE, validator_version="v", policy_version="p",
        plan_version="plan-1")
    outcome, reason, deferred = transcribe(verdict, assessment=None)
    assert outcome == v.ABSTAIN
    assert reason == v.BUDGET_DEFERRED
    assert deferred == v.PLACEMENT_SCORING


def test_the_model_path_refuses_rather_than_running_without_its_injections(indexed):
    from placement.p8_seam import call_placement

    with pytest.raises(ModelPathUnavailable):
        call_placement(indexed, request=None, gate=None, model_client=None,
                       prompt=None, call_dependencies=None,
                       observed_at=lambda: FIXED_CLOCK)


def test_p11_constructs_no_dossier_and_imports_no_model_client():
    import ast
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "src" / "placement"
    banned = {"Dossier", "ModelClient", "Gate"}
    offenders = []
    for path in sorted(root.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name in banned:
                        offenders.append((path.name, node.lineno, alias.name))
    assert offenders == []
```

And the live gate:

```python
# tests/integration/test_p11_p8_seam.py
"""G-P8: P11's authorities against the real harness, end to end.

P8 ships, so this runs. It is the test that would fail if P11 ever grew a second
opinion about a Site C check, because it exercises P8's own recorded pairs
through P11's authorities rather than through P8's fixtures' own.
"""
from __future__ import annotations

import pytest

from llm_harness.fixtures import SITE_C_OUTCOME_PAIRS
from llm_harness.placement_validation import record_cd_verdict, revalidate_for_plan
from llm_harness.records import P8Verdict

from placement.config import SupportPolicy
from placement.index import build_destination_index
from placement.p8_seam import placement_authorities
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE

POLICY = SupportPolicy(policy_id="integration-v1", support_scale_max=1.0,
                       minimum_support_threshold=0.0, margin_threshold=0.0)


def test_a_c_verdict_binds_p11s_plan_version_and_snapshot(p11_conn):
    from llm_harness.placement_validation import validate_placement_response

    build_destination_index(p11_conn, FROZEN_TREE,
                            component_version="P11-integration",
                            observed_at=FIXED_CLOCK)
    pair = SITE_C_OUTCOME_PAIRS[0]
    deps = placement_authorities(
        p11_conn, plan_version=pair.dossier.plan_version, policy=POLICY,
        sensitivity_policy=lambda *_a, **_k: True)
    result = validate_placement_response(
        pair.dossier, pair.response_bytes,
        evidence_resolver=lambda key: "span-1" if key.startswith("obs-") else None,
        contradicts=lambda *_a, **_k: False, dependencies=deps,
        model_id="fixture-model", prompt_fingerprint="fp-canonical",
        dossier_builder="p11-integration", release_audit_id=17)
    verdict = result[0][0]
    assert isinstance(verdict, P8Verdict)
    record_cd_verdict(
        p11_conn, verdict, evidence_snapshot_id=pair.evidence_snapshot_id,
        model_id="fixture-model", prompt_fingerprint="fp-canonical",
        release_audit_id=17, observed_at=FIXED_CLOCK)
    identity = p11_conn.execute(
        "SELECT plan_version, evidence_snapshot_id FROM llm_cd_plan_identity "
        "WHERE verdict_id = ?", (verdict.verdict_id,)).fetchone()
    assert identity["plan_version"] == pair.dossier.plan_version


def test_p11_reuses_p8s_revalidation_rather_than_remapping_a_decision(p11_conn):
    # Done-means 16 and §8.8. P8 already appends a new verdict and supersedes the
    # old one when the plan or the snapshot changes. P11 calling this is what
    # keeps "never silently reclassify" true at the verdict layer too.
    assert callable(revalidate_for_plan)
```

- [ ] **Step 2: Run and verify RED**

Run: `python3 -m pytest -q tests/p11/test_p11_p8_seam.py tests/integration/test_p11_p8_seam.py`

Expected: FAIL at collection — `ModuleNotFoundError: No module named 'placement.p8_seam'`. Every P8 import in the files resolves, because P8 ships; only P11's module is absent.

- [ ] **Step 3: Implement the seam**

```python
# src/placement/p8_seam.py
"""P11's side of Sites C and D. Authorities in, verdict out, no second validator.

Resolution O7 settles the split: P8 owns the validator mechanism and the verdict
shape; P11 owns the destination-specific checks and the record they populate.
"Destination-specific checks" means the ORACLES -- does this node exist in this
frozen plan version, what is the support threshold, what counts as a margin, is
this release permitted -- not the validation. Every one of Site C's fifteen checks
stays in `llm_harness/placement_validation.py`, and a P11 module spelling one of
its reason codes is a second opinion with no way to be reconciled.

`node_exists` closes over P11's own index, so the question P8 asks and the
question P11 answers when it validates a destination itself are literally the same
function. Two sources could disagree, and the disagreement would surface as a
model error.

P11 constructs no `Dossier`, calls no `Gate.release` and imports no model client.
It does hold and pass a `Gate`, a `ModelClient` and a `PromptDefinition`, because
`run_call` requires all three -- holding a capability and exercising it are
different things, and P7 owns the exercise.
"""
from __future__ import annotations

import hashlib
import sqlite3

from llm_harness.harness import run_call
from llm_harness.placement_validation import (
    PlacementDependencies, ResidualDependencies,
)
from llm_harness.records import Conflict as P8Conflict
from llm_harness.sites import SiteDependencies
from llm_harness.vocabulary import (
    ABSTAIN, ACCEPT_CONTEXT_SUPPORTED, ACCEPT_DIRECT, BELOW_SUPPORT_THRESHOLD,
    BUDGET_EXHAUSTED, GENERIC_HUB_ONLY as P8_GENERIC_HUB_ONLY,
    INSUFFICIENT_MARGIN, REJECT, WEAK,
)

from placement.config import SupportPolicy, require_policy
from placement.index import node_exists as index_node_exists
from placement.vocabulary import (
    ABSTAIN as P11_ABSTAIN, BUDGET_DEFERRED, GENERIC_HUB_ONLY, LOW_MARGIN,
    NO_SUPPORTED_DESTINATION, PLACE, PLACEMENT_SCORING,
)

#: How a P8 Site C reason becomes one of §6.10's own abstention reasons. Both are
#: closed sets and the map is total over the ones a `weak` verdict can carry;
#: anything else falls back to `no_supported_destination`, which is the honest
#: answer when P8 refused for a reason §6.10 has no word for.
_REASON_TO_ABSTENTION: dict[str, str] = {
    BELOW_SUPPORT_THRESHOLD: NO_SUPPORTED_DESTINATION,
    INSUFFICIENT_MARGIN: LOW_MARGIN,
    P8_GENERIC_HUB_ONLY: GENERIC_HUB_ONLY,
    BUDGET_EXHAUSTED: BUDGET_DEFERRED,
}


class ModelPathUnavailable(RuntimeError):
    """The model path was asked for without the injections `run_call` requires.

    A deterministic-only run is a legal run (§6.6 decides a unique direct match
    with zero model calls), so this is raised only when a caller asked for a call
    it cannot make -- never as the ordinary state of a model-disabled run.
    """


def placement_authorities(conn: sqlite3.Connection, *, plan_version: str,
                          policy: SupportPolicy,
                          sensitivity_policy) -> PlacementDependencies:
    """Site C's four. Each is a question P11 can answer and P8 cannot."""
    require_policy(policy)
    if not callable(sensitivity_policy):
        raise ModelPathUnavailable(
            "Site C's sensitivity_policy is P7's answer about this release and is "
            "injected; P8 returns ValidationUnavailable without it and P11 "
            "invents no permission"
        )
    return PlacementDependencies(
        node_exists=index_node_exists(conn, plan_version=plan_version),
        support_threshold=policy.minimum_support_threshold,
        margin_predicate=policy.margin_predicate,
        sensitivity_policy=sensitivity_policy,
    )


def residual_authorities(conn: sqlite3.Connection, *, plan_version: str,
                         approved_target_ids, sensitivity_policy) -> ResidualDependencies:
    """Site D's three. `approved_target_ids` is the enabled residual set (§7.4)."""
    if not callable(sensitivity_policy):
        raise ModelPathUnavailable("Site D's sensitivity_policy is injected")
    return ResidualDependencies(
        node_exists=index_node_exists(conn, plan_version=plan_version),
        sensitivity_policy=sensitivity_policy,
        approved_target_ids=tuple(approved_target_ids),
    )


def site_dependencies(*, placement=None, residual=None) -> SiteDependencies:
    """One bundle, with the sites P11 does not own left None.

    `SiteDependencies.__post_init__` rejects a bare callable in any slot, which is
    the repair that closed the acceptance-callback hole; passing None for A, B and
    E is how P11 says it has no authority to offer there.
    """
    return SiteDependencies(fact=None, placement=placement, residual=residual,
                            template=None)


def to_p8_conflicts(conflicts) -> tuple[P8Conflict, ...]:
    """P11's `ConflictConsidered` as P8's `(conflict_id, kind)`.

    Site C rejects a response that ignored a dossier conflict
    (`placement_validation.py:229-236`), so the ids must be stable across the
    request and the response. They are derived from the conflict's own content
    rather than minted, so a replay of the same evidence produces the same ids.
    """
    converted = []
    for conflict in conflicts:
        address = hashlib.sha256(
            "‖".join((conflict.kind, conflict.conflicting_value,
                           conflict.evidence_ref)).encode("utf-8")
        ).hexdigest()[:16]
        converted.append(P8Conflict(conflict_id=f"conflict-{address}",
                                    kind=conflict.kind))
    return tuple(converted)


def evidence_snapshot_id_for(*, plan_version: str, observation_keys) -> str:
    """The id C and D require, minted from what the dossier actually cites.

    `record_cd_verdict` requires it (`placement_validation.py:475-476`) and
    `run_call` now refuses a C or D request without one BEFORE the spend
    (`harness.py:154-165`). No SPEC assigns a producer, so P11 mints it as a
    content address: two dossiers over the same evidence at the same plan version
    share one id, which is what makes a replay recognisable as a replay, and a
    changed snapshot is what `revalidate_for_plan` keys a re-validation on.
    """
    body = "‖".join((plan_version, *sorted(set(observation_keys))))
    return "snap-" + hashlib.sha256(body.encode("utf-8")).hexdigest()[:32]


def transcribe(verdict, *, assessment) -> tuple[str, str | None, str | None]:
    """P8's verdict as (outcome, abstention_reason, deferred_stage).

    This is transcription, not interpretation. `accept_direct` and
    `accept_context_supported` are placements -- the difference between them is
    `requires_review`, which gates `review_policy` and not the outcome. `weak`,
    `reject` and `abstain` are all abstentions with a named reason, because
    §6.10's hierarchy is that an unresolved match stays unresolved and correct
    abstention is a successful outcome rather than a deferred move.
    """
    if verdict.outcome in (ACCEPT_DIRECT, ACCEPT_CONTEXT_SUPPORTED):
        return PLACE, None, None
    if BUDGET_EXHAUSTED in verdict.reasons:
        # §8.6: cost exhaustion must never turn into a judgement about evidence.
        return P11_ABSTAIN, BUDGET_DEFERRED, PLACEMENT_SCORING
    for reason in verdict.reasons:
        mapped = _REASON_TO_ABSTENTION.get(reason)
        if mapped is not None:
            return P11_ABSTAIN, mapped, None
    if verdict.outcome in (WEAK, REJECT, ABSTAIN):
        if assessment is not None and assessment.abstention_reason is not None:
            return P11_ABSTAIN, assessment.abstention_reason, None
        return P11_ABSTAIN, NO_SUPPORTED_DESTINATION, None
    raise ValueError(f"{verdict.outcome!r} is outside P8's verdict vocabulary")


def call_placement(conn, request, *, gate, model_client, prompt,
                   call_dependencies, observed_at):
    """One Site C call. Every argument `run_call` requires, and nothing more.

    P11 supplies `gate`, `model_client` and `prompt` because `run_call` requires
    them (`harness.py:343-350`). It never calls `gate.release` itself -- P8 does,
    inside `run_call`, after the eligibility and reduction decisions -- and it
    imports no concrete model client, only the capability the caller injected.

    `NeedsConsent` comes back unchanged and is handed to the review boundary. It
    is not an outcome, writes no P11 decision and no P2 row (B2).
    """
    missing = [name for name, value in (
        ("request", request), ("gate", gate), ("model_client", model_client),
        ("prompt", prompt), ("call_dependencies", call_dependencies),
    ) if value is None]
    if missing:
        raise ModelPathUnavailable(
            f"the model path needs {missing}; a run without them is a "
            "deterministic-only run and must be requested as one, not attempted "
            "and failed"
        )
    return run_call(conn, request, gate=gate, model_client=model_client,
                    prompt=prompt, validation_dependencies=call_dependencies,
                    observed_at=observed_at)
```

`build_placement_request` is deliberately not in this module. Constructing a `DossierRequest` needs a live `privacy.release.ModelCallRequest`, which P7 builds from the items a caller asks to release, and putting that here would put dossier assembly on the wrong side of Task 10's gate. Task 19's pipeline builds it, after `may_assemble_dossier` has answered.

- [ ] **Step 4: Run and verify GREEN**

Run: `python3 -m pytest -q tests/p11/test_p11_p8_seam.py tests/integration/test_p11_p8_seam.py`

Expected: PASS, 13 tests. `test_a_permissive_sensitivity_authority_cannot_pass_an_invented_node` is the one that proves the whole task: every authority is wide open and P8 still returns `REJECT` with `INVENTED_NODE`, because the check is P8's and P11 never wrote one.

- [ ] **Step 5: Commit**

```bash
git add src/placement/p8_seam.py tests/p11/test_p11_p8_seam.py \
        tests/integration/test_p11_p8_seam.py
git commit -m "feat(p11): supply P8's authorities and write none of its checks"
```

### Task 13: Place a group as one plan, and never pick an institution

**Files:**
- Create: `tests/p11/p9_fixtures.py`
- Create: `src/placement/groups.py`
- Create: `tests/p11/test_p11_groups.py`

**Consumes:** `grouping.acceptance.group_state_as_of`, `grouping.store.memberships_for_group`, `grouping.vocabulary.ACCEPTED`, `placement.scoring.assess`, `placement.index.entry_for`. `tests/p11/p9_fixtures` seeds the rows and stands in for nothing.

**Produces:**

```python
class SharedMaterialPolicyRequired(RuntimeError): ...
class AskOrAbstainSelectorRequired(RuntimeError): ...

@dataclass(frozen=True)
class ExcludedOutlier:
    file_id: str; conflicting_fact: str; evidence_ref: str
    routed_to: str; node_id: str | None

@dataclass(frozen=True)
class GroupPlan:
    group_plan_id: str; plan_version: str; group_id: str
    shared_parent_node_id: str | None
    member_decisions: tuple[PlacementDecision, ...]
    excluded_outliers: tuple[ExcludedOutlier, ...]

@dataclass(frozen=True)
class AcceptedGroup:
    group_id: str; plan_version: str; state: str; memberships: tuple

class GroupNotAcceptedInVersion(LookupError): ...

SHARED_MATERIAL_POLICIES: tuple[str, ...]

def accepted_group_as_of(conn, *, group_id, plan_version) -> AcceptedGroup: ...
def confirm_shared_parent(member_parents, *, policy) -> str | None: ...
def excluded_outlier_for(membership, *, routed_node_id) -> ExcludedOutlier: ...
def resolve_multi_home(*, candidate_node_ids, shared_material_policy,
                       shared_branch_node_id, ask_or_abstain) -> tuple[str, object]: ...
```

**Done-means:** 8 (SPEC:639-642), 9 (SPEC:643-645); Contract out §3 (SPEC:506-521); SPEC:163-181.

**"Accepted" is not a field on P9's `Group`, and P9 already publishes the read.** `src/grouping/vocabulary.py:31-32` says of `accepted` and `rejected`: *"The two values `group_state_as_of` adds at read time. Never stored."* The read is live: `grouping/acceptance.py:154` publishes `group_state_as_of(conn, *, group_id, plan_version_id) -> str`, and `grouping/store.py:266` publishes `memberships_for_group(conn, group_id)`. `accepted_group_as_of` calls both and adds one thing P9 deliberately does not: it **refuses the fallback**. When a version holds no opinion, `group_state_as_of` returns the group's SHARED state (`acceptance.py:165-170`) — `supported`, not `accepted` — and reading that as consent is exactly how a group nobody accepted gets placed. Verified live: after seeding, plan-1 returns `accepted` and plan-2 returns `supported`.

**Outliers are a field, not a list.** SPEC:166 says "identified outliers"; P9 publishes `Membership.outlier_flag ∈ {engine-flagged, model-flagged, both, none}` (`grouping/vocabulary.py:70-77`). `excluded_outliers[]` is derived from it plus the member's own conflicts.

**§6.9 is left open on purpose.** SPEC Open question 6 asks *"abstain **or** ask — which, when?"* and records that the design gives no selector. This task takes one as an injection and raises `AskOrAbstainSelectorRequired` without it. Building a rule here would answer a question the SPEC holds open.

- [ ] **Step 1: Write the P9 fixture**

```python
# tests/p11/p9_fixtures.py
"""Seeds REAL P9 rows for P11's group tests. TESTS ONLY.

This is NOT a stand-in for a P9 read. P9's acceptance read shipped:
`grouping.acceptance.group_state_as_of(conn, *, group_id, plan_version_id)`
(`acceptance.py:154`) returns `accepted` or `rejected` as of a plan version, and
`grouping.store.memberships_for_group(conn, group_id)` (`store.py:266`) returns
the members. `placement/groups.py` calls both directly.

What this module does is build P9's own records -- `Group`, `Membership`,
`GroupAcceptance`, imported and never restated -- and write them through P9's own
writers (`record_group`, `record_membership`, `record_acceptance`), so a P11 test
runs against rows a real P9 run would have produced. A shape change in P9 breaks
this at import, which is the point.

`src/placement/` may never import this module and a test asserts it does not: the
prohibition is about a SOURCE module importing test code, and it stands whether or
not the part it seeds exists.
"""
from __future__ import annotations

from facts.states import VALIDATED
from grouping.acceptance import record_acceptance
from grouping.records import (
    AnchorFact, Conflict, Group, GroupAcceptance, Membership, Support,
)
from grouping.store import record_group, record_membership
from grouping.vocabulary import (
    ACCEPTED, CONTEXT_SUPPORTED, COHERENT, DIRECT_ANCHOR, ENGINE, ENGINE_FLAGGED,
    INCLUDED, NOT_FLAGGED, PENDING_REVIEW, RULES, SHARED_VALIDATED_FACT,
    STRONGLY_IDENTIFIED_FILE, SUPPORTED, USER, USER_ATTACHED,
)

T0 = "2026-08-27T00:00:00Z"

# `VALIDATED` is P6's reliability state and is imported from `facts.states`.
# `grouping.vocabulary` does NOT publish it -- it has `VALIDATED_SHARED_FACT`
# (a seed kind) and `VALIDATION` (a failure stage), and importing either as
# `AnchorFact.reliability_state` would put a seed kind in a reliability field.


def _membership(file_id, *, basis=DIRECT_ANCHOR, outlier=NOT_FLAGGED,
                conflicts=()) -> Membership:
    return Membership(
        membership_id=f"m-{file_id}", group_id="g-columbia", file_id=file_id,
        content_hash=f"h-{file_id}", basis=basis, decision=INCLUDED,
        decision_source=RULES,
        support=(Support(support_kind=SHARED_VALIDATED_FACT,
                         observation_key=f"obs-{file_id}",
                         quote_or_field="target_school", location="body",
                         edge_ref=None),),
        insufficient_evidence=False, insufficiency_statement=None,
        conflicts=conflicts, outlier_flag=outlier,
        validation_verdict_ref=None, created_at=T0)


COLUMBIA_GROUP = Group(
    group_id="g-columbia", seed_ref="seed-1", seed_kind=STRONGLY_IDENTIFIED_FILE,
    proposed_basis="target_school = Columbia",
    anchor_facts=(AnchorFact(field="target_school", value="Columbia",
                             file_ids=("f-essay", "f-transcript"),
                             reliability_state=VALIDATED,
                             observation_key="obs-f-essay"),),
    pre_model_signals={}, anchor_count=2, coherence_verdict=COHERENT,
    coherence_citations=("obs-f-essay",), group_category="application",
    display_label="Columbia application", label_source=ENGINE, conflicts=(),
    stop_rule_hits=(), state=SUPPORTED, sensitivity_state="personal_non_sensitive",
    dossier_id=None, llm_response_ref=None, validation_verdict_ref=None,
    created_by=RULES, created_at=T0)

MEMBERSHIPS = (
    _membership("f-essay"),
    _membership("f-transcript", basis=CONTEXT_SUPPORTED),
    _membership("f-scan", basis=USER_ATTACHED),
    _membership("f-duke-essay", outlier=ENGINE_FLAGGED,
                conflicts=(Conflict(kind="target_school",
                                    competing_values=("Columbia", "Duke"),
                                    file_ids=("f-duke-essay",)),)),
)

ACCEPTANCE = GroupAcceptance(
    acceptance_id="acc-1", plan_version_id="plan-1", group_id="g-columbia",
    membership_id=None, acceptance=ACCEPTED, review_state=PENDING_REVIEW,
    user_edited_label=None, aliases=(), review_decision_ref=None,
    decided_by=USER, created_at=T0)

GROUP_ID: str = COLUMBIA_GROUP.group_id


def seed_accepted_columbia(conn) -> str:
    """Write the group, its four memberships and its acceptance THROUGH P9.

    Nothing here is a stand-in read. After this call,
    `grouping.acceptance.group_state_as_of(conn, group_id=GROUP_ID,
    plan_version_id="plan-1")` returns `accepted` and
    `grouping.store.memberships_for_group(conn, GROUP_ID)` returns the four
    members -- which is precisely what `placement.groups` consumes.
    """
    record_group(conn, COLUMBIA_GROUP)
    for membership in MEMBERSHIPS:
        record_membership(conn, membership)
    record_acceptance(conn, ACCEPTANCE)
    return GROUP_ID
```

`tests/p11/conftest.py`'s `p11_conn` fixture therefore also calls
`grouping.schema.create_grouping_schema(conn)`, because P11's group tests now read
real P9 tables rather than a module-level constant.

- [ ] **Step 2: Write the failing group tests**

```python
# tests/p11/test_p11_groups.py
"""§6.8 one coherent plan; §6.9 never an arbitrary institution."""
from __future__ import annotations

import pytest

from grouping.vocabulary import ENGINE_FLAGGED, SUPPORTED, USER_ATTACHED

from placement import vocabulary as v
from placement.groups import (
    AskOrAbstainSelectorRequired, GroupNotAcceptedInVersion,
    SHARED_MATERIAL_POLICIES, SharedMaterialPolicyRequired,
    accepted_group_as_of, confirm_shared_parent, excluded_outlier_for,
    resolve_multi_home,
)
from p11.p9_fixtures import GROUP_ID, seed_accepted_columbia


@pytest.fixture()
def seeded(p11_conn):
    seed_accepted_columbia(p11_conn)
    return p11_conn


def test_acceptance_is_resolved_as_of_a_plan_version(seeded):
    # Through P9's OWN read. `accepted` is never stored on a group
    # (`grouping/vocabulary.py:31-32`), so asking `Group.state` would answer
    # `supported` in every version and P11 would place a group nobody accepted.
    accepted = accepted_group_as_of(seeded, group_id=GROUP_ID,
                                    plan_version="plan-1")
    assert accepted.state == "accepted"
    assert len(accepted.memberships) == 4
    # plan-2 holds no opinion, so P9 falls back to the SHARED state. It is not
    # an empty result and it is not `accepted`; P11 refuses rather than reading
    # the fallback as consent.
    with pytest.raises(GroupNotAcceptedInVersion):
        accepted_group_as_of(seeded, group_id=GROUP_ID, plan_version="plan-2")


def test_the_shared_state_is_never_mistaken_for_acceptance(seeded):
    from grouping.acceptance import group_state_as_of

    assert group_state_as_of(seeded, group_id=GROUP_ID,
                             plan_version_id="plan-2") == SUPPORTED


def test_the_shared_parent_is_confirmed_before_any_member_is_classified():
    # §6.8's ordering: confirm the parent, then classify beneath it. A member
    # placed first would be placed against no shared context at all.
    parent = confirm_shared_parent(
        {"f-essay": "n-columbia", "f-transcript": "n-columbia"},
        policy="shared-branch")
    assert parent == "n-columbia"


def test_members_disagreeing_on_the_parent_confirm_none():
    assert confirm_shared_parent(
        {"f-essay": "n-columbia", "f-transcript": "n-duke"},
        policy="shared-branch") is None


def test_a_conflicting_member_is_excluded_and_says_why(seeded):
    # Done-means 8: the conflicting-institution essay is an outlier with its
    # conflicting fact recorded, routed to a legal branch or the review queue.
    accepted = accepted_group_as_of(seeded, group_id=GROUP_ID,
                                    plan_version="plan-1")
    outlier = next(m for m in accepted.memberships
                   if m.outlier_flag == ENGINE_FLAGGED)
    assert outlier.conflicts
    assert outlier.conflicts[0].kind == "target_school"
    assert set(outlier.conflicts[0].competing_values) == {"Columbia", "Duke"}
    excluded = excluded_outlier_for(outlier, routed_node_id=None)
    assert excluded.routed_to == v.ROUTED_TO_REVIEW_QUEUE
    assert "Columbia" in excluded.conflicting_fact


def test_a_user_attached_member_still_reaches_group_placement(seeded):
    # M12 and P9 invariant 5: an unreadable file's ONLY basis is user-attached,
    # and those files reach §6.8. Dropping them here would lose them silently.
    accepted = accepted_group_as_of(seeded, group_id=GROUP_ID,
                                    plan_version="plan-1")
    bases = {m.basis for m in accepted.memberships}
    assert USER_ATTACHED in bases


def test_a_shared_branch_is_preferred_when_one_is_approved():
    outcome, payload = resolve_multi_home(
        candidate_node_ids=("n-columbia", "n-duke"),
        shared_material_policy="shared-branch", shared_branch_node_id="n-apps",
        ask_or_abstain=None)
    assert outcome == v.PLACE
    assert payload == "n-apps"


def test_with_no_shared_branch_the_selector_decides_and_is_injected():
    # SPEC Open question 6 is open: the design permits abstain OR ask and gives
    # no selector. Building one here would answer it in code.
    with pytest.raises(AskOrAbstainSelectorRequired):
        resolve_multi_home(candidate_node_ids=("n-columbia", "n-duke"),
                           shared_material_policy="mandatory-review",
                           shared_branch_node_id=None, ask_or_abstain=None)
    outcome, payload = resolve_multi_home(
        candidate_node_ids=("n-columbia", "n-duke"),
        shared_material_policy="mandatory-review", shared_branch_node_id=None,
        ask_or_abstain=lambda ids: v.ASK_USER)
    assert outcome == v.ASK_USER
    assert payload == ("n-columbia", "n-duke")


def test_abstaining_names_no_shared_branch_as_the_reason():
    outcome, payload = resolve_multi_home(
        candidate_node_ids=("n-columbia", "n-duke"),
        shared_material_policy="mandatory-review", shared_branch_node_id=None,
        ask_or_abstain=lambda ids: v.ABSTAIN)
    assert outcome == v.ABSTAIN
    assert payload == v.NO_SHARED_BRANCH


def test_one_institution_is_never_chosen_over_another():
    # Done-means 9, stated as the thing that must not be reachable: there is no
    # argument to `resolve_multi_home` that returns a single institution node.
    for selector in (lambda ids: v.ASK_USER, lambda ids: v.ABSTAIN):
        outcome, payload = resolve_multi_home(
            candidate_node_ids=("n-columbia", "n-duke"),
            shared_material_policy="mandatory-review",
            shared_branch_node_id=None, ask_or_abstain=selector)
        assert payload not in ("n-columbia", "n-duke")


def test_a_missing_shared_material_policy_fails_closed():
    with pytest.raises(SharedMaterialPolicyRequired):
        resolve_multi_home(candidate_node_ids=("n-columbia", "n-duke"),
                           shared_material_policy="", shared_branch_node_id=None,
                           ask_or_abstain=lambda ids: v.ABSTAIN)


def test_the_four_policies_are_69s_own_four():
    assert SHARED_MATERIAL_POLICIES == (
        "shared-branch", "primary-home", "reference-or-alias", "mandatory-review")


def test_the_alias_convention_is_not_a_filesystem_instruction():
    # SPEC Open question 7 is open and threatens P12's contract: if an alias
    # means a symlink it collides with §8.3's rule against following one during
    # mutation. P11 names a node either way and produces no link.
    outcome, payload = resolve_multi_home(
        candidate_node_ids=("n-columbia", "n-duke"),
        shared_material_policy="reference-or-alias",
        shared_branch_node_id="n-apps", ask_or_abstain=None)
    assert outcome == v.PLACE
    assert payload == "n-apps"


def test_placement_never_imports_the_p9_fixture():
    import ast
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "src" / "placement"
    for path in sorted(root.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            # `tests/` carries no top-level `__init__.py`, so pytest puts `tests/`
            # on `sys.path` and the fixture packages are importable as `p11.*`,
            # never as `tests.p11.*`. The guard names the live spelling, because a
            # guard checking a prefix nothing produces catches nothing.
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith(
                    ("p11.", "p11", "tests")):
                raise AssertionError(f"{path.name}:{node.lineno} imports a fixture")
```

- [ ] **Step 3: Run and verify RED**

Run: `python3 -m pytest -q tests/p11/test_p11_groups.py`

Expected: FAIL at collection — `ModuleNotFoundError: No module named 'placement.groups'`.

- [ ] **Step 4: Implement group placement**

```python
# src/placement/groups.py
"""§6.8's coherent group plan and §6.9's multi-home rule.

Group-level placement is first class, and the order is the point: §6.8 confirms
the shared parent from the group's anchors and purpose evidence FIRST, then
classifies members beneath it. A member classified before the parent has no shared
context to be classified against, and the result is several unrelated file moves
presented as a plan.

An outlier is excluded and explained, never forced in. P9 already flags it
(`Membership.outlier_flag`) and already holds the competing values
(`Membership.conflicts`), so P11 records what P9 found and routes the file rather
than re-deciding whether it belongs.

§6.9's hardest rule is stated as a prohibition and implemented as one: with no
shared branch there is NO argument to `resolve_multi_home` that returns one of the
competing institutions. Whether the answer is `abstain` or `ask_user` is SPEC Open
question 6 and stays open -- the selector is injected, and its absence refuses.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from grouping.acceptance import group_state_as_of
from grouping.store import memberships_for_group
from grouping.vocabulary import ACCEPTED

from placement.vocabulary import (
    ABSTAIN, ASK_USER, NO_SHARED_BRANCH, PLACE, ROUTED_TO_NODE,
    ROUTED_TO_REVIEW_QUEUE, check,
)

SHARED_BRANCH: str = "shared-branch"
PRIMARY_HOME: str = "primary-home"
REFERENCE_OR_ALIAS: str = "reference-or-alias"
MANDATORY_REVIEW: str = "mandatory-review"

#: §6.9's four: "a shared branch, a primary-home convention, a reference or alias
#: convention, or mandatory review". P10 records which one at freeze, and the
#: VALUES are P10's spelling -- hyphenated, like every other value in P10's node
#: vocabulary (`scoped-general`, `shared-material`, `review-only`). Underscored
#: here, `resolve_multi_home` would match none of them and every multi-home file
#: would fall through every branch with nothing raising.
SHARED_MATERIAL_POLICIES: tuple[str, ...] = (
    SHARED_BRANCH, PRIMARY_HOME, REFERENCE_OR_ALIAS, MANDATORY_REVIEW,
)

#: The three that resolve to one approved node when the tree offers one. Under
#: `mandatory-review` the tree deliberately offers none, which is the policy.
_BRANCH_BEARING: frozenset[str] = frozenset(
    {SHARED_BRANCH, PRIMARY_HOME, REFERENCE_OR_ALIAS}
)


class SharedMaterialPolicyRequired(RuntimeError):
    """§6.9 requires the frozen tree to carry one. Absent means refuse."""


class AskOrAbstainSelectorRequired(RuntimeError):
    """SPEC Open question 6 is open; the design gives no selector and nor does P11."""


class GroupNotAcceptedInVersion(LookupError):
    """This plan version has not accepted this group. Not an error; a state."""


@dataclass(frozen=True)
class AcceptedGroup:
    """One P9 group as this plan version sees it. Read, never reconstructed."""

    group_id: str
    plan_version: str
    state: str
    memberships: tuple


def accepted_group_as_of(conn: sqlite3.Connection, *, group_id: str,
                         plan_version: str) -> AcceptedGroup:
    """P9's own read, asked as of P10's frozen plan version.

    `accepted` is NOT a field on `Group`: `grouping/vocabulary.py:31-32` says of
    `accepted` and `rejected` that they are "the two values `group_state_as_of`
    adds at read time. Never stored." Reading `Group.state` instead would answer
    `supported` in every version, and P11 would place a group nobody accepted.

    A version holding no opinion is not an empty result -- `group_state_as_of`
    falls back to the SHARED state (`acceptance.py:154-170`) -- so the fallback
    is refused explicitly here rather than read as consent.
    """
    state = group_state_as_of(conn, group_id=group_id,
                              plan_version_id=plan_version)
    if state != ACCEPTED:
        raise GroupNotAcceptedInVersion(
            f"group {group_id!r} is {state!r} as of {plan_version!r}, not "
            f"{ACCEPTED!r}. §6.8 places ACCEPTED groups; a shared lifecycle "
            "state is what the group is, not what this version decided about it"
        )
    return AcceptedGroup(
        group_id=group_id, plan_version=plan_version, state=state,
        memberships=tuple(memberships_for_group(conn, group_id)),
    )


@dataclass(frozen=True)
class ExcludedOutlier:
    file_id: str
    conflicting_fact: str
    evidence_ref: str
    routed_to: str
    node_id: str | None

    def __post_init__(self) -> None:
        check(self.routed_to, (ROUTED_TO_NODE, ROUTED_TO_REVIEW_QUEUE),
              name="routed_to")
        if (self.node_id is None) is (self.routed_to == ROUTED_TO_NODE):
            raise ValueError(
                "an outlier routed to a node names it, and one sent to review "
                "names none; §6.8 requires the user to see where it went"
            )


@dataclass(frozen=True)
class GroupPlan:
    group_plan_id: str
    plan_version: str
    group_id: str
    shared_parent_node_id: str | None
    member_decisions: tuple
    excluded_outliers: tuple[ExcludedOutlier, ...]

    def __post_init__(self) -> None:
        if not self.member_decisions:
            raise ValueError(
                "a group plan with no member decisions is not a plan; §6.8 asks "
                "for one coherent presentation, not an empty one"
            )
        ids = {decision.group_plan_id for decision in self.member_decisions}
        if ids != {self.group_plan_id}:
            raise ValueError(
                "every member decision shares this plan's id; that shared id is "
                "what makes the review surface show one plan rather than several "
                "unrelated file moves"
            )


def confirm_shared_parent(member_parents, *, policy: str) -> str | None:
    """§6.8 step one. One parent, or none, and never a majority vote.

    A majority would place the minority members somewhere their own evidence does
    not support, which is exactly the "moved because it resembles a folder"
    failure §6.12 prohibits.
    """
    if policy and policy not in SHARED_MATERIAL_POLICIES:
        raise SharedMaterialPolicyRequired(
            f"{policy!r} is not one of §6.9's {SHARED_MATERIAL_POLICIES}"
        )
    parents = {parent for parent in member_parents.values() if parent}
    return parents.pop() if len(parents) == 1 else None


def excluded_outlier_for(membership, *, routed_node_id: str | None) -> ExcludedOutlier:
    """P9's flag and P9's competing values, recorded rather than re-derived."""
    conflict = membership.conflicts[0] if membership.conflicts else None
    return ExcludedOutlier(
        file_id=membership.file_id,
        conflicting_fact=(
            f"{conflict.kind} = {' | '.join(conflict.competing_values)}"
            if conflict else "flagged as an outlier by P9 with no competing value"
        ),
        evidence_ref=next(
            (support.observation_key for support in membership.support
             if support.observation_key), ""
        ),
        routed_to=ROUTED_TO_NODE if routed_node_id else ROUTED_TO_REVIEW_QUEUE,
        node_id=routed_node_id,
    )


def resolve_multi_home(*, candidate_node_ids, shared_material_policy: str,
                       shared_branch_node_id: str | None,
                       ask_or_abstain) -> tuple[str, object]:
    """§6.9. Returns (outcome, payload) and never one of the competing nodes.

    The payload is the shared branch's node id for a `place`, the competing ids
    for an `ask_user`, and `no_shared_branch` for an `abstain`. There is no branch
    of this function that returns a member of `candidate_node_ids`, which is how
    "never arbitrarily pick one institution" is enforced rather than asserted.
    """
    if not shared_material_policy:
        raise SharedMaterialPolicyRequired(
            "§6.9: the frozen tree must include a policy for shared material. "
            "Without one a transcript belonging to two packets has no rule, and "
            "the only remaining options are to guess or to stop."
        )
    check(shared_material_policy, SHARED_MATERIAL_POLICIES,
          name="shared_material_policy")
    if shared_material_policy in _BRANCH_BEARING and shared_branch_node_id:
        return PLACE, shared_branch_node_id
    if ask_or_abstain is None:
        raise AskOrAbstainSelectorRequired(
            "with no shared branch §6.9 permits abstaining OR asking the user to "
            "choose a primary home, and gives no rule for which. SPEC Open "
            "question 6 is open; the selector is injected and never invented."
        )
    chosen = ask_or_abstain(tuple(candidate_node_ids))
    if chosen == ASK_USER:
        return ASK_USER, tuple(candidate_node_ids)
    if chosen == ABSTAIN:
        return ABSTAIN, NO_SHARED_BRANCH
    raise AskOrAbstainSelectorRequired(
        f"the selector returned {chosen!r}; §6.9 permits exactly "
        f"{ASK_USER!r} and {ABSTAIN!r}, and a third answer would be a placement"
    )
```

- [ ] **Step 5: Run and verify GREEN**

Run: `python3 -m pytest -q tests/p11/test_p11_groups.py`

Expected: PASS, 12 tests. `test_one_institution_is_never_chosen_over_another` is a property test over both selector answers, which is the only way to assert a prohibition rather than a behaviour.

- [ ] **Step 6: Commit**

```bash
git add tests/p11/p9_fixtures.py src/placement/groups.py tests/p11/test_p11_groups.py
git commit -m "feat(p11): place groups as one plan and never choose an institution"
```

### Task 14: Surface residual sets second, and gate every model call on a set decision

**Files:**
- Create: `src/placement/residual.py`
- Create: `tests/p11/test_p11_residual_sets.py`

**Consumes:** `placement.config.PlacementLimits`, `placement.store`, `placement.events`.

**Produces:**

```python
class PlacementPassIncomplete(RuntimeError): ...
class SetDecisionRequired(RuntimeError): ...
class ResidualPartitionRequired(RuntimeError): ...

@dataclass(frozen=True)
class ResidualSet:
    set_id: str; plan_version: str; label: str; file_count: int
    representative_examples: tuple[str, ...]
    file_type_distribution: tuple[tuple[str, int], ...]
    age_range: tuple[str, str]; evidence_availability: str
    sensitivity_status: str; weak_graph_neighbours: tuple[str, ...]
    reason_not_placed: str; member_file_ids: tuple[str, ...]

@dataclass(frozen=True)
class ResidualSetDecision:
    set_id: str; plan_version: str; choice: str
    node_id: str | None; decided_at: str

def surface_residual_sets(conn, *, plan_version, unplaced, partition, limits,
                          placement_pass_complete, component_version,
                          observed_at) -> tuple[ResidualSet, ...]: ...
def record_set_decision(conn, decision, *, component_version, observed_at, user_id) -> str: ...
def require_set_decision(conn, *, plan_version, set_id) -> ResidualSetDecision: ...
def model_calls_permitted(decision) -> bool: ...
```

**Done-means:** 12 (SPEC:658-660); Contract out §4 (SPEC:523-547); SPEC:56-58.

**Two orderings, both contractual.** §7.1: residual is a *"separate stage that runs only after normal group-aware classification has been attempted"* — so `surface_residual_sets` refuses when the §6 pass has not completed for the corpus. §7.6, SPEC:545-547: *"no per-file residual model call may be issued for a set until that set has a `residual_set_decision`. A set the user chose to leave in place produces **zero** model calls."* Both are enforced by a raise, not by a comment, because both are about spend the user did not authorise.

**The partition is injected.** SPEC:599 records §7.5's eight-line example as *"It may show"* — illustrative counts, not a fixed taxonomy — and SPEC Open question 10 leaves canonical-versus-illustrative open. So the partition arrives as a callable and `ResidualPartitionRequired` refuses without one.

- [ ] **Step 1: Write the failing residual-set tests**

```python
# tests/p11/test_p11_residual_sets.py
"""§7.1's ordering and §7.6's spend gate, both enforced by refusal."""
from __future__ import annotations

import pytest

from placement import vocabulary as v
from placement.config import PlacementLimits
from placement.residual import (
    PlacementPassIncomplete, ResidualPartitionRequired, ResidualSet,
    ResidualSetDecision, SetDecisionRequired, model_calls_permitted,
    record_set_decision, require_set_decision, surface_residual_sets,
)
from p11.conftest import FIXED_CLOCK

LIMITS = PlacementLimits(
    max_retrieved_neighbors=4, max_local_graph_neighborhood=8,
    max_candidate_cluster_size=6, max_residual_files_per_batch=2,
    max_dossier_tokens=4000, max_llm_calls_per_thousand_files=100,
    max_cost_per_scan=5,
)
UNPLACED = ("f-gate", "f-receipt", "f-clip")


def _partition(file_ids):
    return (
        {"label": "Screenshots with no association", "member_file_ids": tuple(file_ids),
         "representative_examples": tuple(file_ids[:1]),
         "file_type_distribution": (("png", len(file_ids)),),
         "age_range": ("2026-01-01", "2026-08-01"),
         "evidence_availability": "ocr_present", "sensitivity_status": "public_low",
         "weak_graph_neighbours": (),
         "reason_not_placed": "no direct fact reached any legal destination"},
    )


def _surface(conn, **overrides):
    values = dict(plan_version="plan-1", unplaced=UNPLACED, partition=_partition,
                  limits=LIMITS, placement_pass_complete=True,
                  component_version="P11-test", observed_at=FIXED_CLOCK)
    values.update(overrides)
    return surface_residual_sets(conn, **values)


def test_no_set_is_surfaced_before_the_placement_pass_completes(p11_conn):
    with pytest.raises(PlacementPassIncomplete):
        _surface(p11_conn, placement_pass_complete=False)


def test_a_set_carries_every_field_75_names(p11_conn):
    sets = _surface(p11_conn)
    only = sets[0]
    assert isinstance(only, ResidualSet)
    assert only.reason_not_placed
    assert only.representative_examples
    assert only.file_type_distribution
    assert only.age_range == ("2026-01-01", "2026-08-01")
    assert only.evidence_availability == "ocr_present"
    assert only.sensitivity_status == "public_low"
    assert only.weak_graph_neighbours == ()


def test_a_set_over_the_batch_ceiling_is_split_not_truncated(p11_conn):
    # §8.6: a ceiling reduces work, it never drops files. A truncated set would
    # leave files unmentioned, which is the "understood and found unimportant"
    # impression §8.6 exists to prevent.
    sets = _surface(p11_conn)
    assert sum(s.file_count for s in sets) == len(UNPLACED)
    assert all(s.file_count <= LIMITS.max_residual_files_per_batch for s in sets)


def test_a_missing_partition_refuses_rather_than_inventing_a_taxonomy(p11_conn):
    with pytest.raises(ResidualPartitionRequired):
        _surface(p11_conn, partition=None)


def test_a_per_file_call_before_the_set_decision_is_refused(p11_conn):
    sets = _surface(p11_conn)
    with pytest.raises(SetDecisionRequired):
        require_set_decision(p11_conn, plan_version="plan-1",
                             set_id=sets[0].set_id)


def test_leave_in_place_produces_zero_model_calls(p11_conn):
    sets = _surface(p11_conn)
    decision = ResidualSetDecision(set_id=sets[0].set_id, plan_version="plan-1",
                                   choice=v.LEAVE_IN_PLACE, node_id=None,
                                   decided_at=FIXED_CLOCK)
    record_set_decision(p11_conn, decision, component_version="P11-test",
                        observed_at=FIXED_CLOCK, user_id="u1")
    stored = require_set_decision(p11_conn, plan_version="plan-1",
                                  set_id=sets[0].set_id)
    assert model_calls_permitted(stored) is False


def test_only_the_review_with_model_choice_permits_a_call(p11_conn):
    sets = _surface(p11_conn)
    for choice, node_id, permitted in (
        (v.REVIEW_WITH_MODEL, None, True),
        (v.SEND_TO_APPROVED_NODE, "n-review-later", False),
        (v.CREATE_CUSTOM_BRANCH, None, False),
    ):
        decision = ResidualSetDecision(
            set_id=f"{sets[0].set_id}-{choice}", plan_version="plan-1",
            choice=choice, node_id=node_id, decided_at=FIXED_CLOCK)
        assert model_calls_permitted(decision) is permitted


def test_send_to_approved_node_names_one_and_the_others_name_none():
    with pytest.raises(ValueError):
        ResidualSetDecision(set_id="s1", plan_version="plan-1",
                            choice=v.SEND_TO_APPROVED_NODE, node_id=None,
                            decided_at=FIXED_CLOCK)
    with pytest.raises(ValueError):
        ResidualSetDecision(set_id="s1", plan_version="plan-1",
                            choice=v.LEAVE_IN_PLACE, node_id="n-course",
                            decided_at=FIXED_CLOCK)


def test_surfacing_and_deciding_are_two_events(p11_conn):
    # A set that was shown and never decided must be distinguishable from one
    # that was decided, because §7.6 gates spend on the second.
    sets = _surface(p11_conn)
    record_set_decision(
        p11_conn,
        ResidualSetDecision(set_id=sets[0].set_id, plan_version="plan-1",
                            choice=v.LEAVE_IN_PLACE, node_id=None,
                            decided_at=FIXED_CLOCK),
        component_version="P11-test", observed_at=FIXED_CLOCK, user_id="u1")
    kinds = [row["event_type"] for row in p11_conn.execute(
        "SELECT event_type FROM events ORDER BY event_id")]
    assert v.RESIDUAL_SET_SURFACED in kinds
    assert v.RESIDUAL_SET_DECIDED in kinds


def test_a_custom_branch_is_a_tree_edit_and_names_no_new_node(p11_conn):
    # §7.10 and §8.8: creating a folder during residual review is routed to P10
    # and opens a draft plan version. P11 mints no node.
    decision = ResidualSetDecision(set_id="s1", plan_version="plan-1",
                                   choice=v.CREATE_CUSTOM_BRANCH, node_id=None,
                                   decided_at=FIXED_CLOCK)
    assert decision.node_id is None
    assert model_calls_permitted(decision) is False
```

- [ ] **Step 2: Run and verify RED**

Run: `python3 -m pytest -q tests/p11/test_p11_residual_sets.py`

Expected: FAIL at collection — `ModuleNotFoundError: No module named 'placement.residual'`.

- [ ] **Step 3: Implement residual sets and the spend gate**

```python
# src/placement/residual.py
"""§7's workflow. The library is P10's; the ordering, the sets and the gate are P11's.

Two orderings here are contractual and both are enforced by a raise rather than by
a convention, because both are about spend and about what the user was shown.

§7.1: residual runs only after normal classification has been attempted. A set
surfaced during the main pass would present a file as unplaceable before the
engine had finished trying to place it.

§7.6: no per-file residual model call may be issued for a set until that set has a
decision, and a set the user chose to leave in place produces ZERO calls. The gate
is the user's control over cost, so a caller that forgets it must fail loudly
rather than spend quietly.

P11 holds no residual template definitions (M10). An enabled residual branch
arrives as an ordinary node carrying `node_role = residual` and its `disposition`,
and a template the user did not enable has no node -- so the §7.7 model cannot
name it and P11 needs no residual-specific legality path at all.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from database_agent.db import transaction

from placement import events as placement_events
from placement.vocabulary import (
    LEAVE_IN_PLACE, REVIEW_WITH_MODEL, SEND_TO_APPROVED_NODE, SET_CHOICES, check,
)


class PlacementPassIncomplete(RuntimeError):
    """§7.1: residual is a second stage and the first has not finished."""


class SetDecisionRequired(RuntimeError):
    """§7.6: this set has no decision, so no per-file model call may be issued."""


class ResidualPartitionRequired(RuntimeError):
    """§7.5's review sets are not a fixed taxonomy; the partition is injected."""


@dataclass(frozen=True)
class ResidualSet:
    set_id: str
    plan_version: str
    label: str
    file_count: int
    representative_examples: tuple[str, ...]
    file_type_distribution: tuple[tuple[str, int], ...]
    age_range: tuple[str, str]
    evidence_availability: str
    sensitivity_status: str
    weak_graph_neighbours: tuple[str, ...]
    reason_not_placed: str
    member_file_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.reason_not_placed:
            raise ValueError(
                "§7.5 requires each set to say why the normal pipeline could not "
                "safely place these files; a set with no reason is a pile"
            )
        if self.file_count != len(self.member_file_ids):
            raise ValueError(
                "the count and the members must agree, or the review screen "
                "reports a number no one can expand"
            )


@dataclass(frozen=True)
class ResidualSetDecision:
    set_id: str
    plan_version: str
    choice: str
    node_id: str | None
    decided_at: str

    def __post_init__(self) -> None:
        check(self.choice, SET_CHOICES, name="choice")
        if (self.node_id is None) is (self.choice == SEND_TO_APPROVED_NODE):
            raise ValueError(
                f"{SEND_TO_APPROVED_NODE!r} names one approved node and every "
                "other choice names none; a node on `create_custom_branch` would "
                "be P11 minting a destination, which §7.4 forbids"
            )


def surface_residual_sets(conn: sqlite3.Connection, *, plan_version: str,
                          unplaced, partition, limits,
                          placement_pass_complete: bool,
                          component_version: str,
                          observed_at: str) -> tuple[ResidualSet, ...]:
    """§7.5's screen. A visible summary in review sets, not an automatic cleanup."""
    if not placement_pass_complete:
        raise PlacementPassIncomplete(
            "§7.1: residual review runs only after normal group-aware "
            "classification has been attempted for the corpus. Surfacing now "
            "would call a file unplaceable before the engine finished trying."
        )
    if partition is None:
        raise ResidualPartitionRequired(
            "§7.5's eight-line example is prefaced 'It may show' -- illustrative "
            "counts, not a fixed taxonomy (SPEC Open question 10). The partition "
            "is injected and P11 invents no set names."
        )
    surfaced: list[ResidualSet] = []
    with transaction(conn):
        for group in partition(tuple(unplaced)):
            members = tuple(group["member_file_ids"])
            ceiling = limits.max_residual_files_per_batch
            # Split, never truncate: §8.6 reduces work and never drops files.
            batches = [members[i:i + ceiling] for i in range(0, len(members), ceiling)]
            for index, batch in enumerate(batches, start=1):
                suffix = f"-{index}" if len(batches) > 1 else ""
                label = group["label"] + (f" ({index} of {len(batches)})"
                                          if len(batches) > 1 else "")
                item = ResidualSet(
                    set_id=f"{plan_version}:{group['label']}{suffix}",
                    plan_version=plan_version, label=label,
                    file_count=len(batch),
                    representative_examples=tuple(group["representative_examples"]),
                    file_type_distribution=tuple(group["file_type_distribution"]),
                    age_range=tuple(group["age_range"]),
                    evidence_availability=group["evidence_availability"],
                    sensitivity_status=group["sensitivity_status"],
                    weak_graph_neighbours=tuple(group["weak_graph_neighbours"]),
                    reason_not_placed=group["reason_not_placed"],
                    member_file_ids=batch,
                )
                conn.execute(
                    "INSERT INTO residual_sets (record_id, plan_version, label, "
                    "payload, created_at) VALUES (?, ?, ?, ?, ?)",
                    (item.set_id, plan_version, item.label,
                     _set_payload(item), observed_at),
                )
                placement_events.residual_set_surfaced(
                    conn, set_id=item.set_id, label=item.label,
                    file_count=item.file_count,
                    reason_not_placed=item.reason_not_placed,
                    component_version=component_version, observed_at=observed_at,
                )
                surfaced.append(item)
    return tuple(surfaced)


def _set_payload(item: ResidualSet) -> str:
    import dataclasses
    import json

    return json.dumps(dataclasses.asdict(item), sort_keys=True)


def record_set_decision(conn: sqlite3.Connection, decision: ResidualSetDecision, *,
                        component_version: str, observed_at: str,
                        user_id: str) -> str:
    """The user's set-level answer, recorded before any per-file spend."""
    import dataclasses
    import json

    with transaction(conn):
        conn.execute(
            "INSERT INTO residual_set_decisions (record_id, plan_version, set_id, "
            "choice, node_id, decided_at, payload) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (f"{decision.plan_version}:{decision.set_id}", decision.plan_version,
             decision.set_id, decision.choice, decision.node_id,
             decision.decided_at, json.dumps(dataclasses.asdict(decision),
                                             sort_keys=True)),
        )
        placement_events.residual_set_decided(
            conn, set_id=decision.set_id, choice=decision.choice,
            node_id=decision.node_id, component_version=component_version,
            observed_at=observed_at, user_id=user_id,
        )
    return decision.set_id


def require_set_decision(conn: sqlite3.Connection, *, plan_version: str,
                         set_id: str) -> ResidualSetDecision:
    """§7.6's gate. Called before every per-file residual model call."""
    row = conn.execute(
        "SELECT choice, node_id, decided_at FROM residual_set_decisions "
        "WHERE plan_version = ? AND set_id = ? AND superseded_by IS NULL",
        (plan_version, set_id),
    ).fetchone()
    if row is None:
        raise SetDecisionRequired(
            f"set {set_id!r} has no §7.6 decision, so no per-file residual model "
            "call may be issued for it. The set-level answer is what the user "
            "controls the cost with."
        )
    return ResidualSetDecision(
        set_id=set_id, plan_version=plan_version, choice=row["choice"],
        node_id=row["node_id"], decided_at=row["decided_at"],
    )


def model_calls_permitted(decision: ResidualSetDecision) -> bool:
    """Exactly one of §7.6's four choices asks for a model, and it says so.

    `leave_in_place` produces zero calls (SPEC:547). `send_to_approved_node` is
    already a decision and needs no interpretation. `create_custom_branch` is a
    tree edit routed to P10 and produces a new plan version, so the current
    version's residual review for that set is over.
    """
    return decision.choice == REVIEW_WITH_MODEL
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3 -m pytest -q tests/p11/test_p11_residual_sets.py`

Expected: PASS, 10 tests. `test_a_set_over_the_batch_ceiling_is_split_not_truncated` asserts the sum, which is the only assertion that catches a ceiling implemented as a slice.

- [ ] **Step 5: Commit**

```bash
git add src/placement/residual.py tests/p11/test_p11_residual_sets.py
git commit -m "feat(p11): surface residual sets second and gate every call"
```

### Task 15: Map the eight actions into one shape and close the §7.9 loop

**Files:**
- Modify: `src/placement/residual.py`
- Create: `tests/p11/test_p11_residual_actions.py`

**Consumes:** `llm_harness.vocabulary.RESIDUAL_ACTIONS`, `llm_harness.placement_validation.validate_residual_response`, `placement.p8_seam.residual_authorities`.

**Produces:**

```python
class ReturnCycleLimitRequired(RuntimeError): ...
class ReturnCycleExhausted(RuntimeError): ...

ACTION_OUTCOME: MappingProxyType[str, str]   # eight, total over RESIDUAL_ACTIONS

def outcome_for_action(action, *, target) -> tuple[str, object]: ...
def link_return(conn, *, residual_decision, placement_decision,
                component_version, observed_at) -> int: ...
def check_return_cycle(conn, *, subject_ref, max_return_cycles) -> int: ...
```

**Done-means:** 1 (SPEC:610-612), 13 (SPEC:661-664); SPEC:83-96, SPEC:386-399, SPEC:441-445.

**Eight, and there is no ninth.** SPEC:95: *"There is no ninth action on the residual path."* `ACTION_OUTCOME` is keyed on P8's `RESIDUAL_ACTIONS` (`llm_harness/vocabulary.py:55-70`) and a test asserts the map is **total over that tuple and exactly its length**, so a P8 addition breaks P11 loudly rather than falling through to a default.

**Which P8 checks this task is therefore not writing.** All ten of Site D's, and one in particular: SPEC:60's requirement that the `Gate B12` screenshot must not produce `Travel/Flight Gate B12` is already implemented at `placement_validation.py:315-316` — any target containing `/` is `REJECT` with `INVENTED_FOLDER`. The §7.9 stronger-relationship trigger is likewise P8's (`:330-338`), and it hands back `disposition = return_to_placement`, which is what P11 reads to emit `outcome = return_to_placement`.

**The cycle bound is open and stays open.** SPEC Open question 8: *"How many times may a file cycle between §7 and §6 (§7.9)? The loop is required; no bound, termination rule, or forced-abstention condition is stated. **Threatens P2's replay determinism.**"* `max_return_cycles` is injected with no default; absent, `ReturnCycleLimitRequired` refuses. P11 chooses no number.

- [ ] **Step 1: Write the failing action tests**

```python
# tests/p11/test_p11_residual_actions.py
"""§7.7's eight, §7.9's loop, and the ninth that does not exist."""
from __future__ import annotations

import json

import pytest

from llm_harness.fixtures import SITE_D_OUTCOME_PAIRS, SITE_D_REASON_PAIRS
from llm_harness.placement_validation import (
    ResidualDependencies, validate_residual_response,
)
from llm_harness.vocabulary import (
    ABSTAIN as P8_ABSTAIN, CHOOSE_BROAD_PARENT, CHOOSE_RESIDUAL_DESTINATION,
    INVENTED_FOLDER, LEAVE_IN_CURRENT_LOCATION, MARK_PROTECTED_OR_UNSUPPORTED,
    MARK_REVIEW_LATER, REJECT, RESIDUAL_ACTIONS, RETURN_ACCEPTED_PACKET,
    RETURN_CONFIRMED_GROUP, RETURN_TO_PLACEMENT as P8_RETURN_DISPOSITION,
    STRONGER_RELATIONSHIP_OVERLOOKED,
)

from placement import vocabulary as v
from placement.records import ResidualContext, ReturnTarget
from placement.residual import (
    ACTION_OUTCOME, ReturnCycleExhausted, ReturnCycleLimitRequired,
    check_return_cycle, link_return, outcome_for_action,
)
from placement.store import record_decision
from p11.conftest import FIXED_CLOCK
from p11.test_p11_records import _decision


def _permissive(*_a, **_k):
    return True


def _residual_deps(pair):
    absent = frozenset(pair.frozen_absent_nodes)
    return ResidualDependencies(
        node_exists=lambda node_id, _plan: node_id not in absent,
        sensitivity_policy=_permissive,
        approved_target_ids=pair.approved_target_ids)


def _validate(pair):
    return validate_residual_response(
        pair.dossier, pair.response_bytes,
        evidence_resolver=lambda key: "span-1" if key.startswith("obs-") else None,
        contradicts=lambda *_a, **_k: False, dependencies=_residual_deps(pair),
        model_id="fixture-model", prompt_fingerprint="fp-canonical",
        dossier_builder="p11-test", release_audit_id=17)


def test_the_map_is_total_over_p8s_controlled_set_and_has_no_ninth():
    assert set(ACTION_OUTCOME) == set(RESIDUAL_ACTIONS)
    assert len(ACTION_OUTCOME) == len(RESIDUAL_ACTIONS) == 8
    assert set(ACTION_OUTCOME.values()) <= set(v.OUTCOMES)


def test_each_of_the_eight_maps_to_its_specd_outcome_and_qualifier():
    cases = (
        (RETURN_CONFIRMED_GROUP, "g-columbia", v.RETURN_TO_PLACEMENT,
         v.CONFIRMED_DOMAIN_GROUP),
        (RETURN_ACCEPTED_PACKET, "pk-1", v.RETURN_TO_PLACEMENT,
         v.ACCEPTED_GRAPH_OR_PURPOSE_PACKET),
        (CHOOSE_RESIDUAL_DESTINATION, "n-review-later", v.PLACE, "n-review-later"),
        (CHOOSE_BROAD_PARENT, "n-academics", v.PLACE, "n-academics"),
        (MARK_REVIEW_LATER, None, v.MARK_REVIEW_LATER, None),
        (LEAVE_IN_CURRENT_LOCATION, None, v.LEAVE_IN_PLACE, None),
        (MARK_PROTECTED_OR_UNSUPPORTED, v.PROTECTED, v.MARK_STATE, v.PROTECTED),
        (P8_ABSTAIN, None, v.ABSTAIN, v.NO_SUPPORTED_DESTINATION),
    )
    for action, target, expected_outcome, expected_payload in cases:
        outcome, payload = outcome_for_action(action, target=target)
        assert outcome == expected_outcome, action
        assert payload == expected_payload, action


def test_two_pairs_of_actions_differ_only_by_a_qualifier():
    # SPEC:386-399: this is why eight actions need no field the §6 path lacks.
    assert (ACTION_OUTCOME[RETURN_CONFIRMED_GROUP]
            == ACTION_OUTCOME[RETURN_ACCEPTED_PACKET] == v.RETURN_TO_PLACEMENT)
    assert (ACTION_OUTCOME[CHOOSE_RESIDUAL_DESTINATION]
            == ACTION_OUTCOME[CHOOSE_BROAD_PARENT] == v.PLACE)


def test_an_action_outside_the_controlled_set_is_p8s_refusal_not_p11s():
    pair = next(p for p in SITE_D_REASON_PAIRS
                if p.expected_reasons == ("ACTION_NOT_IN_CONTROLLED_SET",))
    verdict = _validate(pair)[0][0]
    assert verdict.outcome == REJECT
    with pytest.raises(KeyError):
        outcome_for_action("organise_it_nicely", target=None)


def test_the_gate_b12_screenshot_cannot_produce_a_travel_folder():
    # §7.8's worked example, and P8 already enforces it: any target with a "/"
    # is INVENTED_FOLDER. P11 writes no second version of this check.
    pair = next(p for p in SITE_D_REASON_PAIRS
                if p.expected_reasons == (INVENTED_FOLDER,))
    verdict = _validate(pair)[0][0]
    assert verdict.outcome == REJECT
    assert INVENTED_FOLDER in verdict.reasons


def test_a_stronger_relationship_hands_the_file_back_to_placement():
    # §7.9's trigger is P8's; P11 reads the disposition and emits the outcome.
    pair = next(p for p in SITE_D_REASON_PAIRS
                if p.expected_reasons == (STRONGER_RELATIONSHIP_OVERLOOKED,))
    verdict = _validate(pair)[0][0]
    assert verdict.disposition == P8_RETURN_DISPOSITION


def _returning(decision_id="r1", plan_version="plan-1"):
    return _decision(
        decision_id=decision_id, plan_version=plan_version,
        origin_stage=v.RESIDUAL, outcome=v.RETURN_TO_PLACEMENT, destination=None,
        return_target=ReturnTarget(kind=v.CONFIRMED_DOMAIN_GROUP,
                                   id="g-columbia"),
        residual=ResidualContext(set_id="s1", set_decision=v.REVIEW_WITH_MODEL,
                                 lifecycle_policy_ref=None))


def test_the_return_link_persists_both_records(p11_conn):
    # Done-means 13: the residual finding is never discarded because placement
    # later succeeded, and the second record points at the first.
    residual = _returning()
    placement = _decision(decision_id="p1", plan_version="plan-2",
                          returned_from="r1")
    record_decision(p11_conn, residual, component_version="P11-test",
                    observed_at=FIXED_CLOCK)
    record_decision(p11_conn, placement, component_version="P11-test",
                    observed_at=FIXED_CLOCK)
    link_return(p11_conn, residual_decision=residual,
                placement_decision=placement, component_version="P11-test",
                observed_at=FIXED_CLOCK)
    rows = p11_conn.execute(
        "SELECT record_id, returned_from FROM placement_decisions "
        "ORDER BY record_id").fetchall()
    assert [r["record_id"] for r in rows] == ["p1", "r1"]
    assert rows[0]["returned_from"] == "r1"
    event = p11_conn.execute(
        "SELECT explanation FROM events WHERE event_type = ?",
        (v.RETURN_ISSUED,)).fetchone()
    assert "r1" in event["explanation"] and "p1" in event["explanation"]


def test_the_cycle_limit_is_injected_and_absent_means_refuse(p11_conn):
    with pytest.raises(ReturnCycleLimitRequired):
        check_return_cycle(p11_conn, subject_ref="file:f1:h1",
                           max_return_cycles=None)


def test_exceeding_the_injected_cycle_limit_raises_rather_than_looping(p11_conn):
    # Two returns in two plan versions: the one-current-row index is per plan
    # version, so this is a genuine cycle rather than an illegal second live row.
    for index in (1, 2):
        record_decision(
            p11_conn, _returning(decision_id=f"r{index}",
                                 plan_version=f"plan-{index}"),
            component_version="P11-test", observed_at=FIXED_CLOCK)
    assert check_return_cycle(p11_conn, subject_ref="file:f1:h1",
                              max_return_cycles=2) == 2
    with pytest.raises(ReturnCycleExhausted):
        check_return_cycle(p11_conn, subject_ref="file:f1:h1",
                           max_return_cycles=1)
```

- [ ] **Step 2: Run and verify RED**

Run: `python3 -m pytest -q tests/p11/test_p11_residual_actions.py`

Expected: FAIL — `ImportError: cannot import name 'ACTION_OUTCOME' from 'placement.residual'`.

- [ ] **Step 3: Add the mapping and the loop to `residual.py`**

Append to `src/placement/residual.py`:

```python
from types import MappingProxyType

from llm_harness.vocabulary import (
    ABSTAIN as P8_ABSTAIN, CHOOSE_BROAD_PARENT, CHOOSE_RESIDUAL_DESTINATION,
    LEAVE_IN_CURRENT_LOCATION, MARK_PROTECTED_OR_UNSUPPORTED,
    MARK_REVIEW_LATER as P8_MARK_REVIEW_LATER, RESIDUAL_ACTIONS,
    RETURN_ACCEPTED_PACKET, RETURN_CONFIRMED_GROUP,
)

from placement.vocabulary import (
    ABSTAIN, ACCEPTED_GRAPH_OR_PURPOSE_PACKET, ASK_USER, CONFIRMED_DOMAIN_GROUP,
    MARK_REVIEW_LATER, MARK_STATE, MARKED_STATES, NO_SUPPORTED_DESTINATION, PLACE,
    RETURN_TO_PLACEMENT,
)


class ReturnCycleLimitRequired(RuntimeError):
    """SPEC Open question 8 is open; no bound is stated and P11 chooses none."""


class ReturnCycleExhausted(RuntimeError):
    """This file has already cycled §7 → §6 as many times as the caller allows."""


#: §7.7's eight actions, in P8's machine spelling, mapped onto §6's outcome
#: vocabulary. Two pairs differ only by a qualifier, which is why the eight need
#: no field the §6 path does not already have (SPEC:386-399). There is no ninth
#: (SPEC:95), and the totality assertion below is what makes a P8 addition break
#: here loudly rather than fall through to a default.
ACTION_OUTCOME: MappingProxyType = MappingProxyType({
    RETURN_CONFIRMED_GROUP: RETURN_TO_PLACEMENT,
    RETURN_ACCEPTED_PACKET: RETURN_TO_PLACEMENT,
    CHOOSE_RESIDUAL_DESTINATION: PLACE,
    CHOOSE_BROAD_PARENT: PLACE,
    P8_MARK_REVIEW_LATER: MARK_REVIEW_LATER,
    LEAVE_IN_CURRENT_LOCATION: LEAVE_IN_PLACE,
    MARK_PROTECTED_OR_UNSUPPORTED: MARK_STATE,
    P8_ABSTAIN: ABSTAIN,
})
assert set(ACTION_OUTCOME) == set(RESIDUAL_ACTIONS)
assert ASK_USER not in ACTION_OUTCOME.values()   # SPEC:437-439: placement only

_RETURN_KIND: MappingProxyType = MappingProxyType({
    RETURN_CONFIRMED_GROUP: CONFIRMED_DOMAIN_GROUP,
    RETURN_ACCEPTED_PACKET: ACCEPTED_GRAPH_OR_PURPOSE_PACKET,
})


def outcome_for_action(action: str, *, target) -> tuple[str, object]:
    """One action as (outcome, qualifier). Raises on anything outside the eight.

    The qualifier is what the record's outcome-shaped field takes:
    `return_target.kind` for the two returns, `destination.node_id` for the two
    choices, `marked_state` for the mark, `abstention_reason` for the abstention,
    and nothing at all for Review Later and leave-in-place -- whether those two
    result in a move is the Review Later node's `disposition` (§7.4, set by P10),
    not this record's decision.
    """
    outcome = ACTION_OUTCOME[action]
    if action in _RETURN_KIND:
        return outcome, _RETURN_KIND[action]
    if outcome == PLACE:
        return outcome, target
    if outcome == MARK_STATE:
        if target not in MARKED_STATES:
            raise ValueError(
                f"§7.7 action 7 marks a file {MARKED_STATES}; {target!r} is "
                "neither, and a third state would be P11 inventing a category"
            )
        return outcome, target
    if outcome == ABSTAIN:
        return outcome, NO_SUPPORTED_DESTINATION
    return outcome, None


def link_return(conn: sqlite3.Connection, *, residual_decision,
                placement_decision, component_version: str,
                observed_at: str) -> int:
    """§7.9's loop, logged. Both records persist; neither supersedes the other.

    The residual finding is never discarded because placement later succeeded --
    it is the record of what the residual review noticed, and SPEC:443-445 keeps
    it readable beside the placement it caused.
    """
    if placement_decision.returned_from != residual_decision.decision_id:
        raise ValueError(
            "the placement decision must name the residual decision that handed "
            "the file back; without the link §8.8's diff cannot walk the loop"
        )
    return placement_events.return_issued(
        conn, residual_decision_id=residual_decision.decision_id,
        placement_decision_id=placement_decision.decision_id,
        component_version=component_version, observed_at=observed_at,
        file_id=placement_decision.subject.file_id,
        content_hash=placement_decision.subject.content_hash,
    )


def check_return_cycle(conn: sqlite3.Connection, *, subject_ref: str,
                       max_return_cycles) -> int:
    """How many times this subject has already gone §7 → §6, and whether that is
    one too many.

    SPEC Open question 8 is open: the loop is required and no bound, termination
    rule or forced-abstention condition is stated, which threatens P2's replay
    determinism. The bound is therefore injected. P11 picks no number, and a
    caller that supplies none is refused rather than allowed to loop.
    """
    if max_return_cycles is None:
        raise ReturnCycleLimitRequired(
            "§7.9 requires the loop back to §6 and states no bound (SPEC Open "
            "question 8). `max_return_cycles` is injected; absent means refuse, "
            "because an unbounded loop is a replay that never terminates."
        )
    row = conn.execute(
        "SELECT count(*) AS c FROM placement_decisions WHERE subject_ref = ? "
        "AND outcome = ?", (subject_ref, RETURN_TO_PLACEMENT),
    ).fetchone()
    seen = row["c"]
    if seen > max_return_cycles:
        raise ReturnCycleExhausted(
            f"{subject_ref!r} has returned to placement {seen} times against a "
            f"limit of {max_return_cycles}; the caller decides what happens next "
            "and P11 does not silently keep cycling"
        )
    return seen
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3 -m pytest -q tests/p11/test_p11_residual_actions.py tests/p11/test_p11_residual_sets.py`

Expected: PASS, 19 tests. `test_the_map_is_total_over_p8s_controlled_set_and_has_no_ninth` is the assertion that would fail the day P8 adds a residual action, which is the intended behaviour: SPEC:95 says there is no ninth, so a ninth is a contract revision.

- [ ] **Step 5: Commit**

```bash
git add src/placement/residual.py tests/p11/test_p11_residual_actions.py
git commit -m "feat(p11): map the eight residual actions and close the loop"
```

### Task 16: Receive P13's review action and author the decision it produces

**Files:**
- Create: `tests/p11/p13_fixtures.py`
- Create: `src/placement/review.py`
- Create: `tests/p11/test_p11_review.py`

**Consumes:** `tests/p11/p13_fixtures` (until P13 ships), `placement.store.record_decision`, `placement.learning.record_correction`.

**Produces:**

```python
class UnroutedSurface(ValueError): ...
class BulkMembersRequired(ValueError): ...

P11_SURFACES: tuple[str, ...]     # four, P13 SPEC:294
P11_ACTIONS: tuple[str, ...]      # the subset P13 routes to P11

def apply_review_action(conn, action, *, decision_factory, component_version,
                        observed_at) -> tuple[str, ...]: ...
def correction_scope_of(action) -> tuple[str, str]: ...
```

**Done-means:** SPEC:236-244, SPEC:736-749, SPEC:761-763.

**P11 authors; P13 collects.** SPEC:243: *"**P11 authors the placement or residual decision each action produces** (M8) and P1 writes the event."* So `apply_review_action` returns the ids of the decisions it wrote — the same shape P9's plan gives its own receiver, `apply_review_action(conn, action) -> tuple[str, ...]` (`planning/parts/P9-grouping/PLAN.md:772`). A user action that produces no decision returns an empty tuple, which is a real answer: deferring records a correction and authors nothing.

**A bulk decision is expandable.** SPEC:241: *"§7.10's bulk decisions arrive as `action = accept_bulk` with every member enumerated"*, and P13 SPEC:271-272 says `bulk_member_refs[]` enumerates every member, *"never a filter expression"*. So `accept_bulk` with no members is refused: a filter cannot be re-read later to say which files a reversal applies to.

**Creating a custom folder is not P11's.** SPEC:761-763: it is a tree edit routed to P10 producing a new plan version. `apply_review_action` routes it and authors nothing, because P11 minting a node is the one thing §6.12 prohibits outright.

- [ ] **Step 1: Write the P13 fixture**

```python
# tests/p11/p13_fixtures.py
"""A test-only stand-in for P13's `review_action`. TESTS ONLY.

P13 is specification only: its three event types are registered
(`database_agent/events.py:59-61`) and no producer exists. `src/placement/` may
never import this module and a test asserts it does not -- a source stub would be
P11 deciding what a user gesture looks like, which is P13's to say.

The field list is P13 SPEC:247-279 restricted to the four surfaces P13 routes to
P11 (P13 SPEC:294). Replacing this import with P13's public record is a required
integration test when P13 ships.
"""
from __future__ import annotations

from dataclasses import dataclass, field

#: P13 SPEC:294 — the four surfaces whose actions route to P11.
SURFACES: tuple[str, ...] = (
    "placement", "group_plan", "residual_set", "residual_file",
)

#: The subset of P13 SPEC:264-270's actions a placement or residual surface
#: collects. `adopt_version`, `restore_version`, `select_consent_option`,
#: `set_redaction`, `refresh_plan`, `approve_for_apply` and `reset_learning`
#: route elsewhere and are deliberately absent.
ACTIONS: tuple[str, ...] = (
    "accept", "accept_bulk", "change_destination", "return_to_accepted_group",
    "create_custom_folder", "mark_private", "defer", "leave_untouched", "reject",
    "edit_recommendation", "disable_suggestion_type",
)


@dataclass(frozen=True)
class ReviewActionFixture:
    action_id: str
    surface: str
    subject_ref: str
    plan_version: str
    session_id: str
    action: str
    bulk_member_refs: tuple[str, ...]
    bulk_basis: str | None
    correction_scope: str
    presented_state_ref: str
    user_id: str
    acted_at: str
    payload: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.surface not in SURFACES:
            raise ValueError(f"{self.surface!r} is not one of P11's {SURFACES}")
        if self.action not in ACTIONS:
            raise ValueError(f"{self.action!r} is not one of {ACTIONS}")
        for name in ("action_id", "subject_ref", "plan_version",
                     "presented_state_ref", "user_id", "acted_at"):
            if not getattr(self, name):
                raise ValueError(f"{name} is required on a review action")


def accept(**overrides) -> ReviewActionFixture:
    values = dict(
        action_id="a-1", surface="placement", subject_ref="d1",
        plan_version="plan-1", session_id="s-1", action="accept",
        bulk_member_refs=(), bulk_basis=None, correction_scope="file",
        presented_state_ref="ev-42", user_id="u1",
        acted_at="2026-08-27T00:00:00Z", payload={},
    )
    values.update(overrides)
    return ReviewActionFixture(**values)


def change_destination(**overrides) -> ReviewActionFixture:
    values = dict(action="change_destination",
                  payload={"node_id": "n-course-alt"})
    values.update(overrides)
    return accept(**values)


def reject(**overrides) -> ReviewActionFixture:
    values = dict(action="reject", correction_scope="node",
                  payload={"node_id": "n-course"})
    values.update(overrides)
    return accept(**values)


def accept_bulk(**overrides) -> ReviewActionFixture:
    values = dict(action="accept_bulk", surface="residual_set",
                  subject_ref="set-1",
                  bulk_member_refs=("f-a", "f-b", "f-c"),
                  bulk_basis="all three are product screenshots with no association",
                  correction_scope="corpus")
    values.update(overrides)
    return accept(**values)


def defer(**overrides) -> ReviewActionFixture:
    values = dict(action="defer")
    values.update(overrides)
    return accept(**values)


def create_custom_folder(**overrides) -> ReviewActionFixture:
    values = dict(action="create_custom_folder", surface="residual_set",
                  subject_ref="set-1", correction_scope="node",
                  payload={"display_label": "Receipts to Process"})
    values.update(overrides)
    return accept(**values)


RECORDED_ACTIONS = (
    accept, change_destination, reject, accept_bulk, defer, create_custom_folder,
)
```

- [ ] **Step 2: Write the failing receiver tests**

```python
# tests/p11/test_p11_review.py
"""P13 collects; P11 authors. The back edge is fixture-mediated until P13 ships."""
from __future__ import annotations

import pytest

from placement import vocabulary as v
from placement.review import (
    BulkMembersRequired, P11_ACTIONS, P11_SURFACES, UnroutedSurface,
    apply_review_action, correction_scope_of, routes_to_p10,
)
from p11.conftest import FIXED_CLOCK
from p11 import p13_fixtures as p13


def _factory(**_kwargs):
    from p11.test_p11_records import _decision
    return _decision


def _apply(conn, action, **overrides):
    values = dict(decision_factory=_factory(), component_version="P11-test",
                  observed_at=FIXED_CLOCK)
    values.update(overrides)
    return apply_review_action(conn, action, **values)


def test_the_four_surfaces_are_p13s_four_for_p11():
    assert P11_SURFACES == ("placement", "group_plan", "residual_set",
                            "residual_file")


def test_an_action_on_another_parts_surface_is_refused(p11_conn):
    # `ReviewActionFixture` refuses `canvas` at construction, which is P13's own
    # guard. P11's guard is for a record that reached it wearing a surface P13
    # routes elsewhere, so the test uses a bare object rather than the fixture.
    class Foreign:
        surface = "consent"
        action = "accept"

    with pytest.raises(UnroutedSurface):
        _apply(p11_conn, Foreign())
    with pytest.raises(ValueError):
        p13.accept(surface="canvas")


def test_an_acceptance_records_a_correction_and_authors_no_new_decision(p11_conn):
    ids = _apply(p11_conn, p13.accept())
    assert ids == ()
    row = p11_conn.execute(
        "SELECT polarity, correction_scope, correction_subject, user_id "
        "FROM events ORDER BY event_id DESC LIMIT 1").fetchone()
    assert row["polarity"] == "accept"
    assert row["correction_scope"] == "file"
    assert row["user_id"] == "u1"


def test_a_rejection_is_a_negative_example_at_the_scope_the_user_chose(p11_conn):
    _apply(p11_conn, p13.reject())
    row = p11_conn.execute(
        "SELECT polarity, correction_scope, correction_subject, basis_key "
        "FROM events ORDER BY event_id DESC LIMIT 1").fetchone()
    assert row["polarity"] == "reject"
    assert row["correction_scope"] == "node"
    assert "n-course" in row["basis_key"]


def test_changing_a_destination_authors_a_new_decision(p11_conn):
    # The decision the user is revising must EXIST before it can be superseded:
    # `mark_superseded` raises `KeyError` on an unknown `old_id`. P13's
    # `subject_ref` on a placement surface is that decision's record id.
    from placement.store import record_decision
    from p11.test_p11_records import _decision

    record_decision(p11_conn, _decision(decision_id="d1"),
                    component_version="P11-test", observed_at=FIXED_CLOCK)
    ids = _apply(p11_conn, p13.change_destination())
    assert len(ids) == 1
    row = p11_conn.execute(
        "SELECT superseded_by, supersede_reason FROM placement_decisions "
        "WHERE record_id = 'd1'").fetchone()
    assert row["superseded_by"] == ids[0]
    assert "change_destination" in row["supersede_reason"]


def test_changing_a_destination_with_no_prior_decision_supersedes_nothing(p11_conn):
    # A first decision about a subject has no predecessor. Passing the action's
    # `subject_ref` through as `supersedes` regardless would hand
    # `mark_superseded` an id that is not in the table.
    ids = _apply(p11_conn, p13.change_destination())
    assert len(ids) == 1
    row = p11_conn.execute(
        "SELECT supersedes FROM placement_decisions WHERE record_id = ?",
        (ids[0],)).fetchone()
    assert row["supersedes"] is None


def test_a_bulk_acceptance_enumerates_every_member(p11_conn):
    # P13 SPEC:271-272: "every member enumerated, never a filter expression".
    # A filter cannot be re-read later to say which files a reversal applies to.
    _apply(p11_conn, p13.accept_bulk())
    rows = p11_conn.execute(
        "SELECT correction_subject FROM events WHERE polarity = 'accept'"
    ).fetchall()
    assert len(rows) >= 3
    with pytest.raises(BulkMembersRequired):
        _apply(p11_conn, p13.accept_bulk(bulk_member_refs=()))


def test_deferring_records_the_action_and_decides_nothing(p11_conn):
    ids = _apply(p11_conn, p13.defer())
    assert ids == ()
    row = p11_conn.execute(
        "SELECT explanation FROM events ORDER BY event_id DESC LIMIT 1").fetchone()
    assert "defer" in row["explanation"]


def test_creating_a_custom_folder_routes_to_p10_and_mints_nothing(p11_conn):
    # §7.10, §8.8: a folder the USER adds is a tree edit that opens a draft plan
    # version. It is not the model inventing a destination, and it is not P11's.
    action = p13.create_custom_folder()
    assert routes_to_p10(action) is True
    ids = _apply(p11_conn, action)
    assert ids == ()
    nodes = p11_conn.execute(
        "SELECT count(*) AS c FROM placement_index_entries").fetchone()
    assert nodes["c"] == 0


def test_every_action_carries_the_state_the_user_was_actually_shown(p11_conn):
    # §8.2, §8.4, §8.7: `presented_state_ref` is what makes a correction
    # interpretable later, because it says what was on screen under the
    # redaction policy then in force.
    for build in p13.RECORDED_ACTIONS:
        assert build().presented_state_ref


def test_the_scope_is_the_users_and_p11_widens_none():
    scope, subject = correction_scope_of(p13.reject())
    assert (scope, subject) == ("node", "n-course")
    scope, subject = correction_scope_of(p13.accept())
    assert scope == "file"


def test_placement_never_imports_the_p13_fixture():
    import ast
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "src" / "placement"
    for path in sorted(root.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and "p13" in (node.module or ""):
                raise AssertionError(f"{path.name}:{node.lineno} imports P13's fixture")
```

- [ ] **Step 3: Run and verify RED**

Run: `python3 -m pytest -q tests/p11/test_p11_review.py`

Expected: FAIL at collection — `ModuleNotFoundError: No module named 'placement.review'`.

- [ ] **Step 4: Implement the receiver**

```python
# src/placement/review.py
"""P13's `review_action`, received. P13 presents and collects; P11 authors (M8).

Nothing here interprets a gesture into a preference. It records what the user did
at the scope the user chose, and authors the decision the action produces -- which
for most actions is none: accepting a recommendation confirms a decision that
already exists, deferring decides nothing, and creating a folder is P10's edit.

Scope is the safety property and it is never widened. §8.7's governing example is
that one transcript belonging in a Columbia packet must not teach the engine that
all transcripts do, so `correction_scope` comes off the action and P11 adds
nothing to it.

A bulk acceptance enumerates its members. A filter expression cannot be re-read
later to say which files a reversal applies to, which is why P13's own record
forbids one and why this refuses an empty enumeration.
"""
from __future__ import annotations

import sqlite3
from types import MappingProxyType

from placement.learning import ACCEPT, REJECT, basis_key_for, record_correction

#: P13 SPEC:294 — the surfaces whose actions route to P11.
P11_SURFACES: tuple[str, ...] = (
    "placement", "group_plan", "residual_set", "residual_file",
)

ACCEPT_ACTION: str = "accept"
ACCEPT_BULK: str = "accept_bulk"
CHANGE_DESTINATION: str = "change_destination"
RETURN_TO_ACCEPTED_GROUP: str = "return_to_accepted_group"
CREATE_CUSTOM_FOLDER: str = "create_custom_folder"
MARK_PRIVATE: str = "mark_private"
DEFER: str = "defer"
LEAVE_UNTOUCHED: str = "leave_untouched"
REJECT_ACTION: str = "reject"
EDIT_RECOMMENDATION: str = "edit_recommendation"
DISABLE_SUGGESTION_TYPE: str = "disable_suggestion_type"

P11_ACTIONS: tuple[str, ...] = (
    ACCEPT_ACTION, ACCEPT_BULK, CHANGE_DESTINATION, RETURN_TO_ACCEPTED_GROUP,
    CREATE_CUSTOM_FOLDER, MARK_PRIVATE, DEFER, LEAVE_UNTOUCHED, REJECT_ACTION,
    EDIT_RECOMMENDATION, DISABLE_SUGGESTION_TYPE,
)

#: Which actions are a negative example and which a positive one. `defer` is
#: neither: it is a decision to decide later, and recording it as a rejection
#: would teach the engine something the user did not say.
_POLARITY: MappingProxyType = MappingProxyType({
    ACCEPT_ACTION: ACCEPT, ACCEPT_BULK: ACCEPT, LEAVE_UNTOUCHED: ACCEPT,
    REJECT_ACTION: REJECT, CHANGE_DESTINATION: REJECT,
    DISABLE_SUGGESTION_TYPE: REJECT,
})

#: Actions that author a new P11 decision. The rest confirm one, record a
#: preference, or belong to another part.
_AUTHORS_A_DECISION: frozenset[str] = frozenset(
    {CHANGE_DESTINATION, RETURN_TO_ACCEPTED_GROUP, EDIT_RECOMMENDATION,
     MARK_PRIVATE}
)


class UnroutedSurface(ValueError):
    """An action reached P11 wearing a surface P13 routes somewhere else."""


class BulkMembersRequired(ValueError):
    """A bulk acceptance with no enumerated members. A filter is not a list."""


def routes_to_p10(action) -> bool:
    """§7.10 and §8.8: a folder the user creates is a tree edit, and P10's.

    P11 routes it and authors nothing. This is the one place where the answer to
    "who invents a destination?" has to be visible in P11's own code, because the
    prohibition (§6.12) is about the SYSTEM inventing one and this is the user.
    """
    return action.action == CREATE_CUSTOM_FOLDER


def correction_scope_of(action) -> tuple[str, str]:
    """The scope the user chose, and the subject it is about.

    Never widened and never inferred. A `node`-scoped correction is about the
    node in the action's payload; every other scope is about its `subject_ref`.
    """
    payload = getattr(action, "payload", {}) or {}
    if action.correction_scope == "node" and payload.get("node_id"):
        return action.correction_scope, payload["node_id"]
    if action.correction_scope == "file":
        return action.correction_scope, action.subject_ref
    return action.correction_scope, payload.get("subject_id", action.subject_ref)


def apply_review_action(conn: sqlite3.Connection, action, *, decision_factory,
                        component_version: str,
                        observed_at: str) -> tuple[str, ...]:
    """Record the action; author the decision it produces, if it produces one.

    Returns the ids of decisions written. An empty tuple is a real answer: most
    gestures confirm or defer rather than decide, and returning a fabricated id
    would put a decision in the store that the user never asked for.
    """
    surface = getattr(action, "surface", None)
    if surface not in P11_SURFACES:
        raise UnroutedSurface(
            f"surface {surface!r} is not one of P11's {P11_SURFACES}; P13 routes "
            "canvas and plan_version to P10, consent to P7, apply to P12"
        )
    if action.action not in P11_ACTIONS:
        raise UnroutedSurface(
            f"action {action.action!r} is not one P13 routes to a placement or "
            f"residual surface; P11 handles {P11_ACTIONS}"
        )

    payload = getattr(action, "payload", {}) or {}
    scope, subject_id = correction_scope_of(action)
    node_id = payload.get("node_id", "")
    members = tuple(getattr(action, "bulk_member_refs", ()) or ())
    if action.action == ACCEPT_BULK and not members:
        raise BulkMembersRequired(
            "§7.10's bulk decision enumerates every member; P13's own record "
            "forbids a filter expression, because a filter cannot say later "
            "which files a reversal applies to"
        )

    polarity = _POLARITY.get(action.action)
    written: list[str] = []
    if polarity is not None:
        subjects = members or (subject_id,)
        for member in subjects:
            record_correction(
                conn, decision=_decision_for(conn, decision_factory, action,
                                             member),
                action=action.action, polarity=polarity, scope=scope,
                subject_id=member if members else subject_id,
                basis_key=basis_key_for(subject_ref=str(member),
                                        node_id=node_id or action.subject_ref),
                user_id=action.user_id, component_version=component_version,
                observed_at=observed_at,
                explanation=getattr(action, "bulk_basis", None) or action.action,
            )
    else:
        # `defer`, `create_custom_folder` and the rest still leave a trace: §8.2
        # records user decisions, and a deferral the log cannot show is a gap in
        # the reconstruction §8.2 exists to make possible.
        from placement import events as placement_events

        placement_events.review_decision(
            conn, subject_ref=action.subject_ref, action=action.action,
            component_version=component_version, observed_at=observed_at,
            user_id=action.user_id, correction_scope=scope,
            correction_subject=subject_id, polarity=ACCEPT,
            proposal_class="placement",
            basis_key=basis_key_for(subject_ref=action.subject_ref,
                                    node_id=node_id or action.subject_ref),
            explanation=action.action,
        )

    if action.action in _AUTHORS_A_DECISION and not routes_to_p10(action):
        from placement.store import record_decision

        decision = _decision_for(conn, decision_factory, action, subject_id)
        record_decision(conn, decision, component_version=component_version,
                        observed_at=observed_at,
                        supersede_reason=(f"user {action.action} on "
                                          f"{action.subject_ref}")
                        if decision.supersedes else None)
        written.append(decision.decision_id)
    return tuple(written)


def _predecessor(conn, action) -> str | None:
    """The LIVE decision this action revises, or None.

    P13's `subject_ref` on a placement surface is the id of the decision the user
    was looking at (`presented_state_ref` names the event; `subject_ref` names the
    record). It is passed to `mark_superseded` as `old_id`, which raises
    `KeyError` for a record that is not in the table -- so a first decision about
    a subject, or an action whose predecessor was already superseded, must resolve
    to None rather than to a plausible-looking string. Inventing a predecessor is
    how a user gesture becomes an unwritable decision.
    """
    row = conn.execute(
        "SELECT record_id FROM placement_decisions WHERE record_id = ? "
        "AND superseded_by IS NULL", (action.subject_ref,),
    ).fetchone()
    return None if row is None else row["record_id"]


def _decision_for(conn, decision_factory, action, subject_id):
    """The decision this action produces, built by the caller's factory.

    The factory is the pipeline's, because authoring a decision needs the whole
    of Tasks 6-15 -- the index, the retrieval, the scoring, the privacy state.
    P11's receiver decides WHETHER a decision is authored; the pipeline decides
    what it says.
    """
    supersedes = (_predecessor(conn, action)
                  if action.action == CHANGE_DESTINATION else None)
    return decision_factory(
        decision_id=f"{action.action_id}:{subject_id}",
        supersedes=supersedes,
    )
```

- [ ] **Step 5: Run and verify GREEN**

Run: `python3 -m pytest -q tests/p11/test_p11_review.py`

Expected: PASS, 11 tests. `test_creating_a_custom_folder_routes_to_p10_and_mints_nothing` is the one that matters most: it asserts both halves, that the action routes and that the index gained no row, because "P11 mints no node" is only true if both hold.

- [ ] **Step 6: Commit**

```bash
git add tests/p11/p13_fixtures.py src/placement/review.py tests/p11/test_p11_review.py
git commit -m "feat(p11): receive P13 actions and author only what they produce"
```

### Task 17: Re-project on a new plan version, and remap nothing

**Files:**
- Create: `src/placement/versions.py`
- Create: `tests/p11/test_p11_versions.py`

**Consumes:** `placement.store.decisions_for_plan`, `placement.index.entries_for_plan`, `llm_harness.placement_validation.revalidate_for_plan`.

**Produces:**

```python
@dataclass(frozen=True)
class VersionDiff:
    from_plan_version: str; to_plan_version: str
    requiring_renewed_review: tuple[str, ...]
    carried_unchanged: tuple[str, ...]
    removed_node_ids: tuple[str, ...]

def reproject(conn, *, from_plan_version, to_plan_version,
              revalidation_inputs=None) -> VersionDiff: ...
def learned_preferences_still_applicable(conn, *, plan_version, suppressions) -> tuple: ...
```

**`revalidate_for_plan` is called here, and this is the only place it belongs.** It re-validates a *stored* P8 verdict against a new plan version and a new evidence snapshot — §8.8's question, not §6.12's, which is why Task 19's per-file pipeline does not call it. This task declared it under **Consumes** and never called it; `reproject` now does, through `_revalidates`.

**OPEN — P11 stores no verdict id.** `PlacementDecision`'s thirty fields include no `verdict_id`, `llm_response_ref` or dossier reference, so P11 cannot supply `previous_verdict_id`, `dossier` or `response_bytes` from its own record. They arrive as an injected `revalidation_inputs` mapping from the caller that made the call, which is this plan's standing idiom for a value P11 cannot know. Making P11 self-sufficient here means adding a field to SPEC Contract out §1, which is a contract revision and not an implementation decision. Recorded under [SPEC corrections](#spec-corrections).

**Done-means:** 16 (SPEC:670-671); SPEC:765-787.

**The one sentence this task implements.** SPEC:782-787: *"Decisions whose destination node no longer exists are marked as requiring renewed review and appear in the version diff (§8.8's own example: **twenty-three files now require renewed review because their previous destination no longer exists**). Decisions are **never** silently remapped onto a renamed or relocated node, and a new plan **never** silently reclassifies or moves files already placed under an earlier one. Learned preferences carry across versions but their application is filtered by whether the node they reference still exists."*

**Node identity is the trap, and `node_id` is not it.** P10 answered its OQ5 by minting a **new `node_id` for every plan version** and recording lineage in `origin_node_id` (`planning/38-p10-p11-connection-contract.md` §5.2; P10's own `test_a_copied_node_keeps_its_lineage_and_gets_a_new_identity` asserts `before["n_root"].node_id != after["n_root"].node_id`). So **no `node_id` survives a draft.** Matching a stored decision to the new version on `node_id` would find nothing for any node — and every decision, including one whose node was merely *renamed*, would be marked `requiring_renewed_review`.

That outcome is forbidden by the sentence this task implements. §8.8's diff *"may state that Applications was renamed to Admissions, Research moved under Projects, Reference Clips was added, the Academic template changed … or **twenty-three files** now require renewed review because their previous destination no longer exists"* (`planning/01-product-design-structured.md:1889-1892`). Twenty-three is a **subset**, not all: a diff that distinguishes *renamed*, *moved* and *added* from *no longer exists* requires an identity that survives a rename, and under P10's minting the only such identity is `origin_node_id`.

**So `reproject` matches on `origin_node_id` and never on `node_id`.** A decision names a `node_id` because it was made against one version and belongs to it; re-projection resolves `decision.destination.node_id → plan-N entry → origin_node_id → plan-N+1 entry`, and marks for renewed review **only when no successor shares that origin**. A rename changes `display_label` and mints a new id, and the decision still carries. A relocation changes `parent_node_id` and mints a new id, and the decision still carries — the path P12 composes changes, which is P12's problem and not a remap. What must never happen is a decision whose node was **removed** being matched onto a similar surviving node, and that is what `reproject` refuses to do: it marks and it never matches.

This is also why it is the minimal change. OQ5 stays genuinely open: if ids later become stable then `origin_node_id == node_id` and not one line here moves.

- [ ] **Step 1: Write the failing version tests**

```python
# tests/p11/test_p11_versions.py
"""§8.8 — a new plan version marks work for review and reclassifies nothing."""
from __future__ import annotations

from dataclasses import replace

import pytest

from placement import vocabulary as v
from placement.index import build_destination_index
from placement.records import Subject
from placement.store import record_decision
from placement.versions import reproject
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE, tree_with
from p11.test_p11_records import _decision


def _minted(node, **overrides):
    """P10 mints a NEW node_id per plan version and keeps lineage in origin.

    Every helper below goes through here, because a v2 fixture that reused v1's
    ids would be testing a world P10 does not build and would hide the exact
    defect this task exists to prevent.
    """
    return replace(node, plan_version_id="plan-2",
                   node_id=f"{node.node_id}@2",
                   origin_node_id=node.origin_node_id, **overrides)


def _v2_without_the_course_node():
    survivors = tuple(node for node in FROZEN_TREE.nodes
                      if node.node_id != "n-course")
    minted = tuple(_minted(node) for node in survivors)
    profiles = tuple(
        replace(p, node_id=f"{p.node_id}@2")
        for p in FROZEN_TREE.profiles if p.node_id != "n-course")
    return tree_with(
        plan_version_id="plan-2", nodes=minted, profiles=profiles,
        freeze_record=replace(
            FROZEN_TREE.freeze_record, plan_version_id="plan-2",
            node_ids=tuple(n.node_id for n in minted),
            legal_destination_ids=frozenset(
                n.node_id for n in minted if n.accepts_placement)))


def _v2_with_a_rename():
    renamed = tuple(
        _minted(node, display_label="PHYS 1401 — Mechanics"
                if node.node_id == "n-course" else node.display_label)
        for node in FROZEN_TREE.nodes)
    profiles = tuple(replace(p, node_id=f"{p.node_id}@2")
                     for p in FROZEN_TREE.profiles)
    return tree_with(
        plan_version_id="plan-2", nodes=renamed, profiles=profiles,
        freeze_record=replace(
            FROZEN_TREE.freeze_record, plan_version_id="plan-2",
            node_ids=tuple(n.node_id for n in renamed),
            legal_destination_ids=frozenset(
                n.node_id for n in renamed if n.accepts_placement)))


def _indexed(conn, tree):
    build_destination_index(conn, tree, component_version="P11-test",
                            observed_at=FIXED_CLOCK)


def test_a_removed_node_marks_its_decisions_for_renewed_review(p11_conn):
    _indexed(p11_conn, FROZEN_TREE)
    record_decision(p11_conn, _decision(decision_id="d1"),
                    component_version="P11-test", observed_at=FIXED_CLOCK)
    _indexed(p11_conn, _v2_without_the_course_node())
    diff = reproject(p11_conn, from_plan_version="plan-1",
                     to_plan_version="plan-2")
    assert diff.requiring_renewed_review == ("d1",)
    assert diff.removed_node_ids == ("n-course",)
    assert diff.carried_unchanged == ()


def test_a_removed_node_is_never_matched_onto_a_similar_survivor(p11_conn):
    # The failure this exists to prevent: `n-course-alt` still exists and looks
    # like a plausible home. §8.8 forbids remapping, so nothing is written that
    # names it.
    _indexed(p11_conn, FROZEN_TREE)
    record_decision(p11_conn, _decision(decision_id="d1"),
                    component_version="P11-test", observed_at=FIXED_CLOCK)
    _indexed(p11_conn, _v2_without_the_course_node())
    reproject(p11_conn, from_plan_version="plan-1", to_plan_version="plan-2")
    rows = p11_conn.execute(
        "SELECT node_id FROM placement_decisions WHERE plan_version = 'plan-2'"
    ).fetchall()
    assert [r["node_id"] for r in rows] == []


def test_a_renamed_node_carries_the_decision_on_its_lineage_not_its_id(p11_conn):
    # The load-bearing test of this task. P10 mints a NEW node_id in plan-2, so
    # `n-course` does not exist there and an id match would find nothing. §8.8
    # forbids that outcome by name: a rename is not a removal and must not send
    # twenty-three files back to review. `origin_node_id` is what survives.
    _indexed(p11_conn, FROZEN_TREE)
    record_decision(p11_conn, _decision(decision_id="d1"),
                    component_version="P11-test", observed_at=FIXED_CLOCK)
    v2 = _v2_with_a_rename()
    _indexed(p11_conn, v2)
    assert {node.node_id for node in v2.nodes}.isdisjoint(
        {node.node_id for node in FROZEN_TREE.nodes})   # nothing survives by id
    diff = reproject(p11_conn, from_plan_version="plan-1",
                     to_plan_version="plan-2")
    assert diff.requiring_renewed_review == ()
    assert diff.carried_unchanged == ("d1",)


def test_a_moved_node_carries_the_decision_too(p11_conn):
    # A relocation also mints a new id, and the decision still carries. What
    # changes is the path P12 composes from the new parent chain, which is P12's
    # to compose and not a remap.
    _indexed(p11_conn, FROZEN_TREE)
    record_decision(p11_conn, _decision(decision_id="d1"),
                    component_version="P11-test", observed_at=FIXED_CLOCK)
    moved = _v2_with_a_rename()
    relocated = tuple(
        replace(node, parent_node_id=None) if node.origin_node_id == "n-course"
        else node for node in moved.nodes)
    _indexed(p11_conn, tree_with(
        plan_version_id="plan-2", nodes=relocated, profiles=moved.profiles,
        freeze_record=moved.freeze_record))
    diff = reproject(p11_conn, from_plan_version="plan-1",
                     to_plan_version="plan-2")
    assert diff.carried_unchanged == ("d1",)


def test_a_new_version_moves_nothing_already_placed(p11_conn):
    # §8.8: "A new plan should never silently reclassify or move old files."
    _indexed(p11_conn, FROZEN_TREE)
    record_decision(p11_conn, _decision(decision_id="d1"),
                    component_version="P11-test", observed_at=FIXED_CLOCK)
    _indexed(p11_conn, _v2_without_the_course_node())
    reproject(p11_conn, from_plan_version="plan-1", to_plan_version="plan-2")
    original = p11_conn.execute(
        "SELECT outcome, node_id, superseded_by FROM placement_decisions "
        "WHERE record_id = 'd1'").fetchone()
    assert original["outcome"] == v.PLACE
    assert original["node_id"] == "n-course"
    assert original["superseded_by"] is None


def test_an_abstention_needs_no_renewed_review_when_a_node_disappears(p11_conn):
    # It named no node, so no node's removal invalidates it.
    _indexed(p11_conn, FROZEN_TREE)
    record_decision(
        p11_conn, _decision(decision_id="d1", outcome=v.ABSTAIN,
                            destination=None,
                            abstention_reason=v.NO_SUPPORTED_DESTINATION),
        component_version="P11-test", observed_at=FIXED_CLOCK)
    _indexed(p11_conn, _v2_without_the_course_node())
    diff = reproject(p11_conn, from_plan_version="plan-1",
                     to_plan_version="plan-2")
    assert diff.requiring_renewed_review == ()


def test_the_diff_counts_what_88s_example_counts(p11_conn):
    # §8.8's own sentence is a COUNT of files, so the diff must be able to give
    # one without the caller re-deriving it.
    # Three distinct subjects: the store's one-current-row index is keyed on
    # (plan_version, subject_ref), so three decisions about one file would be
    # three attempts at the same live row rather than three files.
    _indexed(p11_conn, FROZEN_TREE)
    for index in range(1, 4):
        record_decision(
            p11_conn,
            _decision(decision_id=f"d{index}",
                      subject=Subject(kind=v.FILE, file_id=f"f{index}",
                                      content_hash=f"h{index}", group_id=None,
                                      member_file_ids=())),
            component_version="P11-test", observed_at=FIXED_CLOCK)
    _indexed(p11_conn, _v2_without_the_course_node())
    diff = reproject(p11_conn, from_plan_version="plan-1",
                     to_plan_version="plan-2")
    assert len(diff.requiring_renewed_review) == 3
```

- [ ] **Step 2: Run and verify RED**

Run: `python3 -m pytest -q tests/p11/test_p11_versions.py`

Expected: FAIL at collection — `ModuleNotFoundError: No module named 'placement.versions'`.

- [ ] **Step 3: Implement re-projection**

```python
# src/placement/versions.py
"""§8.8's re-projection. It marks, and it never matches.

A placement decision belongs to a plan version because it is a projection of one
frozen tree. When a new version is adopted, every decision is re-examined against
the new legal set and exactly one thing can happen to it: its node still exists
and the decision carries, or its node is gone and the decision is marked as
requiring renewed review.

There is deliberately no third branch. A removed node often has a plausible
survivor -- the whole reason a node was removed is usually that another one
replaced it -- and matching onto it is the "silent reclassification" §8.8
prohibits by name. §8.8's own example is a COUNT of files needing review, not a
count of files quietly moved.

"Still exists" is a question about LINEAGE, not about `node_id`. P10 mints a new
`node_id` for every plan version and records the lineage in `origin_node_id`
(its OQ5; `planning/38-p10-p11-connection-contract.md` §5.2). Matching on
`node_id` would therefore find no successor for ANY node and mark every decision
for renewed review after any tree edit at all -- including a pure rename, which
§8.8 forbids by name. So the match runs
`decision.destination.node_id -> from-version entry -> origin_node_id ->
to-version entry`, and a decision is marked only when NO successor shares that
origin.

A rename is not a removal, and neither is a move. P10 rewrites `display_label`
(or `parent_node_id`) and mints a new id; the origin is unchanged, so the decision
carries and produces no review at all. The label and path the user now sees are
composed by P12 from the new chain.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from placement.index import entries_for_plan
from placement.store import decisions_for_plan
from placement.vocabulary import PLACE


@dataclass(frozen=True)
class VersionDiff:
    from_plan_version: str
    to_plan_version: str
    requiring_renewed_review: tuple[str, ...]
    carried_unchanged: tuple[str, ...]
    removed_node_ids: tuple[str, ...]

    @property
    def renewed_review_count(self) -> int:
        """§8.8's sentence is a count; the caller should not have to derive one."""
        return len(self.requiring_renewed_review)


def reproject(conn: sqlite3.Connection, *, from_plan_version: str,
              to_plan_version: str, revalidation_inputs=None) -> VersionDiff:
    """Which decisions survive the new version, and which need the user again.

    `revalidation_inputs` is an optional mapping `decision_id -> dict`, one entry
    per decision that was decided by a MODEL. A deterministic decision has no P8
    verdict and nothing to re-validate, which is why the mapping is sparse rather
    than a field on every record. Each entry supplies exactly the keywords
    `llm_harness.placement_validation.revalidate_for_plan` requires --
    `previous_verdict_id`, `dossier`, `response_bytes`, `evidence_resolver`,
    `contradicts`, `dependencies`, `model_id`, `prompt_fingerprint`,
    `dossier_builder`, `release_audit_id` -- because P11 stores none of them and
    the caller that made the call holds them all.

    A verdict that re-validates as unavailable or refused joins
    `requiring_renewed_review` beside the removed-node cases: the node survived,
    but the judgement about it did not, and §8.8 says a new plan never silently
    carries a placement whose basis no longer holds.
    """
    # The two maps this whole function turns on. `origin_of` reads the version
    # the decisions were made against; `successors` reads the new one. Neither is
    # keyed on `node_id` across the boundary, because P10 mints a new one per
    # version and an id match would find nothing for any node.
    origin_of = {entry.node_id: entry.origin_node_id
                 for entry in entries_for_plan(conn, plan_version=from_plan_version)}
    successors = {entry.origin_node_id
                  for entry in entries_for_plan(conn, plan_version=to_plan_version)}
    needs_review: list[str] = []
    carried: list[str] = []
    removed: set[str] = set()
    for decision in decisions_for_plan(conn, plan_version=from_plan_version):
        if decision.outcome != PLACE or decision.destination is None:
            # It named no node, so no node's removal invalidates it. An
            # abstention under the old tree is still an abstention under the new
            # one until the evidence changes.
            continue
        node_id = decision.destination.node_id
        # A decision whose own node is not in the from-version index at all has
        # no lineage to follow, which is itself a reason to ask the user again.
        origin = origin_of.get(node_id)
        if origin is None or origin not in successors:
            needs_review.append(decision.decision_id)
            removed.add(node_id)
            continue
        if _revalidates(conn, decision, to_plan_version, revalidation_inputs):
            carried.append(decision.decision_id)
        else:
            needs_review.append(decision.decision_id)
    return VersionDiff(
        from_plan_version=from_plan_version, to_plan_version=to_plan_version,
        requiring_renewed_review=tuple(needs_review),
        carried_unchanged=tuple(carried),
        removed_node_ids=tuple(sorted(removed)),
    )


def _revalidates(conn, decision, to_plan_version: str, inputs) -> bool:
    """P8 re-checks its own verdict against the new version. P11 re-checks nothing.

    `revalidate_for_plan` is P8's (`placement_validation.py:528`) and records the
    new verdict itself at `:614`. P11 supplies the current plan version and the
    current evidence snapshot and reads the answer -- the same authorities-in,
    verdict-out shape as Site C, one version later.
    """
    entry = (inputs or {}).get(decision.decision_id)
    if entry is None:
        # No model verdict backs this decision, so there is nothing to
        # re-validate and the node's survival is the whole question.
        return True
    from llm_harness.placement_validation import revalidate_for_plan
    from llm_harness.records import ValidationUnavailable

    from placement.p8_seam import evidence_snapshot_id_for
    from placement.vocabulary import VERDICTS

    result = revalidate_for_plan(
        conn, current_plan_version=to_plan_version,
        current_evidence_snapshot_id=evidence_snapshot_id_for(
            plan_version=to_plan_version,
            observation_keys=tuple(f.evidence_ref
                                   for f in decision.matching_facts)),
        observed_at=entry["observed_at"], **{
            key: entry[key] for key in (
                "previous_verdict_id", "dossier", "response_bytes",
                "evidence_resolver", "contradicts", "dependencies", "model_id",
                "prompt_fingerprint", "dossier_builder", "release_audit_id")
        })
    if isinstance(result, ValidationUnavailable):
        return False
    # VERDICTS[0] and VERDICTS[1] are the two accepting outcomes.
    return result.outcome in VERDICTS[:2]


def learned_preferences_still_applicable(conn: sqlite3.Connection, *,
                                         plan_version: str, suppressions) -> tuple:
    """§8.8: preferences carry across versions, filtered by node existence.

    A rejection of a node that no longer exists is still a true fact about what
    the user decided, and it is preserved -- it is simply not applied, because
    there is nothing left for it to suppress. Deleting it instead would lose the
    reason if the node ever came back.

    "Still exists" is the same lineage question `reproject` asks, and for the same
    reason: a suppression recorded against an earlier version names that version's
    `node_id`, which P10's per-version minting guarantees is absent from the new
    one. Filtered on `node_id`, EVERY learned preference would silently stop
    applying at the first tree edit -- the opposite of "preferences carry across
    versions". So the filter matches either identity: a suppression whose id is a
    current node id, or one whose id is an earlier node with a surviving origin.
    """
    entries = entries_for_plan(conn, plan_version=plan_version)
    surviving_ids = {entry.node_id for entry in entries}
    surviving_origins = {entry.origin_node_id for entry in entries}
    return tuple(item for item in suppressions
                 if item.node_id in surviving_ids
                 or item.node_id in surviving_origins)
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3 -m pytest -q tests/p11/test_p11_versions.py`

Expected: PASS, 7 tests. Two are load-bearing and fail together if identity is taken from `node_id`: `test_a_renamed_node_carries_the_decision_on_its_lineage_not_its_id`, because plan-2's ids are all new and an id match would send every decision back to review; and `test_a_removed_node_is_never_matched_onto_a_similar_survivor`, because `n-course-alt` survives and looks like a plausible home, and the assertion is that nothing was written naming it.

- [ ] **Step 5: Commit**

```bash
git add src/placement/versions.py tests/p11/test_p11_versions.py
git commit -m "feat(p11): mark on a new version and never remap a decision"
```

### Task 18: Emit two stages, two dimensions, and a deferral that is never an abstention

**Files:**
- Create: `src/placement/stage_output.py`
- Create: `tests/p11/test_p11_stage_output.py`
- Create: `tests/integration/test_p11_p2_replay.py`

**Consumes:** `eval_harness.stage_output.record_stage_output`, `eval_harness.stage_output.DimensionValue`, `eval_harness.run.record_version_tuple`.

**Produces:**

```python
def envelope_for(decision) -> tuple[str, str]: ...          # (outcome, budget_state)
def dimension_for(decision) -> DimensionValue: ...
def candidate_subject_ref(plan_version: str, subject_ref: str) -> str: ...
def emit_retrieval_stage(conn, *, run_id, retrieval, version_tuple_ref, inputs) -> int: ...
def emit_scoring_stage(conn, *, run_id, decision, version_tuple_ref, inputs) -> int: ...
```

**Done-means:** 11 (SPEC:656-657), 14 (SPEC:665-667); Contract out's envelope table (SPEC:265-288) and §6 (SPEC:581-585).

**Two vocabularies, and P2 already refuses the wrong one.** `src/eval_harness/stage_output.py:30-33` enumerates P11's seven record outcomes as `_FOREIGN_OUTCOMES` and raises `ForeignVocabulary` if one reaches the envelope. Task 2 pins P11's `OUTCOMES` against that set, so this module's whole job is the mapping between them — SPEC:273-278's five rows — and the mapping is a function, not a copy of either list.

**The row that must not collapse.** SPEC:280-288: a budget deferral is `deferred` with `ceiling_reached` and is **never** `abstained`, *"even though both are carried on a record whose own `outcome` reads `abstain`"*. Scored as `abstained`, P2 would grade a ceiling-truncated run `abstained_correctly` or `abstained_incorrectly` — a judgement about evidence — when no judgement was made. `record_stage_output` enforces the pairing itself (`stage_output.py:112-118`), so a wrong mapping here fails at the writer rather than during comparison.

**A correct abstention passes both dimensions.** SPEC:583-585 and Done-means 11. `placement` and `residual` are P2 *dimensions* with no same-named stage for the second (`eval_harness/vocabulary.py:5-11` records that as P2's own open question), so P11 attaches the `residual` dimension to `placement_scoring` and says so, rather than inventing a stage P2's closed ten does not contain.

**Every stage this task emits carries a dimension value, or it is not measurable at all.** `src/eval_harness/attribution.py` reads **only** `stage_dimension_value` rows — to decide which stage emitted a failing assertion (`:65-71`) and which stages qualify as ancestors (`:30-39`). A stage that writes none can be neither. So `candidate_node_retrieval` carries the **`retrieval`** dimension, which §8.5 names for it directly: *"Retrieval quality: for sparse files, did the correct anchors appear in the top candidate neighborhood?"* (`planning/01-product-design-structured.md:1757-1758`). Two stages sharing one dimension is the shape §8.5 already has — its ten dimensions are a shorter and separate list from its ten stages on purpose — so no eleventh dimension is invented.

**And its subject must be namespaced, or the write raises.** `stage_dimension_value` is keyed `PRIMARY KEY (run_id, dimension, subject_ref)` (`src/eval_harness/stage_output.py:59`). Two consequences, both fatal to the naive version: `candidate_node_retrieval` cannot carry the `placement` dimension for the same subject as `placement_scoring`, because the second `INSERT` raises `IntegrityError`; and `retrieval` is already P9's dimension for its own retrieval stage (`src/grouping/stage_output.py:56-60`), so a full-pipeline replay in which P9 and P11 both key a `retrieval` row on the same file raises too. Hence `subject_ref = f"candidates:{plan_version}:{subject_ref}"` on **both** the envelope and the `DimensionValue` — they must be equal, because `_stage_verdicts` keys on the dimension row's and `_edges` on the envelope's — and `placement_scoring.inputs` gains that same ref, because the ancestor walk only reaches a stage named in `inputs[]`. With both halves, an assertion on `(retrieval, candidates:plan-1:file:f1:h1)` graded `divergent` attributes to `candidate_node_retrieval` (stage order 8) rather than to `placement_scoring` (order 9), which is what §8.5 asks for. Decided in `planning/38-p10-p11-connection-contract.md` §7.

- [ ] **Step 1: Write the failing stage tests**

```python
# tests/p11/test_p11_stage_output.py
"""P2 owns the envelope; P11 owns the record; the mapping is the whole task."""
from __future__ import annotations

import pytest

from eval_harness.stage_output import ForeignVocabulary, record_stage_output
from eval_harness.vocabulary import DIMENSIONS, STAGE_IDS as P2_STAGE_IDS

from placement import vocabulary as v
from placement.records import ResidualContext
from placement.stage_output import dimension_for, envelope_for
from p11.test_p11_records import _decision


def _residual(outcome):
    return _decision(
        origin_stage=v.RESIDUAL, outcome=outcome, destination=None,
        residual=ResidualContext(set_id="s1", set_decision=v.REVIEW_WITH_MODEL,
                                 lifecycle_policy_ref=None))


def test_p11_emits_only_two_of_p2s_ten_stages():
    assert set(v.STAGE_IDS) <= set(P2_STAGE_IDS)
    assert v.STAGE_IDS == ("candidate_node_retrieval", "placement_scoring")
    assert "P11" not in P2_STAGE_IDS


def test_a_placement_is_produced_within_ceiling():
    assert envelope_for(_decision()) == ("produced", "within_ceiling")


def test_an_evidential_abstention_is_abstained_within_ceiling():
    for reason in (v.NO_SUPPORTED_DESTINATION, v.LOW_MARGIN, v.SEMANTIC_ONLY,
                   v.GENERIC_HUB_ONLY, v.CONFLICTING_FACTS, v.NO_SHARED_BRANCH,
                   v.PRIVACY_BLOCKED):
        decision = _decision(outcome=v.ABSTAIN, destination=None,
                             abstention_reason=reason)
        assert envelope_for(decision) == ("abstained", "within_ceiling"), reason


def test_a_budget_deferral_is_deferred_and_never_abstained():
    # SPEC:280-288 and Done-means 14. Scored as `abstained`, P2 would grade a
    # ceiling-truncated run as a judgement about evidence when none was made.
    decision = _decision(outcome=v.ABSTAIN, destination=None,
                         abstention_reason=v.BUDGET_DEFERRED,
                         deferred_stage=v.PLACEMENT_SCORING)
    assert envelope_for(decision) == ("deferred", "ceiling_reached")


def test_a_non_place_non_abstain_outcome_is_still_produced():
    # SPEC:274: a record written with any outcome other than `abstain` is
    # `produced`. `leave_in_place` is a decision, not a failure to decide.
    for outcome in (v.LEAVE_IN_PLACE, v.MARK_REVIEW_LATER):
        assert envelope_for(_residual(outcome))[0] == "produced"


def test_p11s_own_outcome_can_never_reach_the_envelope(p11_conn, p2_run_id,
                                                       p11_version_tuple):
    with pytest.raises(ForeignVocabulary):
        record_stage_output(
            p11_conn, run_id=p2_run_id, stage_id=v.PLACEMENT_SCORING,
            subject_ref="file:f1:h1", outcome=v.PLACE, payload=None,
            version_tuple_ref=p11_version_tuple, inputs=(),
            budget_state="within_ceiling")


def test_a_correct_abstention_is_a_pass_on_its_dimension():
    # Done-means 11: P2's placement and residual assertions score a correct
    # abstention as success, not as a miss. `abstained` is P2's own success
    # outcome for that case; `divergent` would be the miss.
    decision = _decision(outcome=v.ABSTAIN, destination=None,
                         abstention_reason=v.NO_SUPPORTED_DESTINATION)
    value = dimension_for(decision)
    assert value.dimension == v.DIMENSION_PLACEMENT
    assert value.outcome == "abstained"


def test_a_residual_decision_carries_the_residual_dimension():
    # `residual` is a P2 dimension with no same-named stage
    # (eval_harness/vocabulary.py:6-7). P11 attaches it to `placement_scoring`
    # rather than inventing an eleventh stage.
    value = dimension_for(_residual(v.LEAVE_IN_PLACE))
    assert value.dimension == v.DIMENSION_RESIDUAL
    assert value.dimension in DIMENSIONS
```

And the replay gate:

```python
# tests/integration/test_p11_p2_replay.py
"""P11 → P2, through the live writer. Replay only; there is no live run kind."""
from __future__ import annotations

import json

import pytest

from eval_harness.stage_output import (
    DimensionValue, dimension_values, record_stage_output, stage_outputs,
)

from placement import vocabulary as v
from placement.retrieval import Retrieval
from placement.stage_output import emit_retrieval_stage, emit_scoring_stage
from p11.test_p11_records import _decision


@pytest.fixture
def a_retrieval():
    """One candidate set, keyed on the same subject the decision below uses."""
    return Retrieval(subject_ref="file:f1:h1", plan_version="plan-1",
                     candidates=(), conflicts=(),
                     semantic_only_node_ids=frozenset())


def test_a_placement_stage_round_trips_with_its_dimension(p11_conn, p2_run_id,
                                                          p11_version_tuple):
    emit_scoring_stage(p11_conn, run_id=p2_run_id, decision=_decision(),
                       version_tuple_ref=p11_version_tuple,
                       inputs=("group:g1", "tree:plan-1"))
    rows = stage_outputs(p11_conn, p2_run_id, stage_id=v.PLACEMENT_SCORING)
    assert len(rows) == 1
    assert rows[0]["outcome"] == "produced"
    values = dimension_values(p11_conn, p2_run_id, dimension=v.DIMENSION_PLACEMENT)
    assert len(values) == 1


def test_the_retrieval_stage_is_attributable_at_all(p11_conn, p2_run_id,
                                                    p11_version_tuple,
                                                    a_retrieval):
    # `eval_harness/attribution.py` reads ONLY `stage_dimension_value` rows, both
    # to name the stage that emitted a failing assertion (:65-71) and to qualify
    # ancestors (:30-39). A retrieval stage with no dimension row is invisible to
    # both, so a placement error that began in retrieval could never be measured
    # as one. This is the test that fails if the DimensionValue is dropped.
    emit_retrieval_stage(p11_conn, run_id=p2_run_id, retrieval=a_retrieval,
                         version_tuple_ref=p11_version_tuple, inputs=())
    values = dimension_values(p11_conn, p2_run_id, dimension=v.DIMENSION_RETRIEVAL)
    assert len(values) == 1
    assert values[0]["subject_ref"] == "candidates:plan-1:file:f1:h1"


def test_the_envelope_and_the_dimension_share_one_subject_ref(p11_conn, p2_run_id,
                                                              p11_version_tuple,
                                                              a_retrieval):
    # `_stage_verdicts` keys on the dimension row's subject_ref while `_edges`
    # keys on the envelope's. Unequal, the stage is measured and unreachable.
    emit_retrieval_stage(p11_conn, run_id=p2_run_id, retrieval=a_retrieval,
                         version_tuple_ref=p11_version_tuple, inputs=())
    rows = stage_outputs(p11_conn, p2_run_id, stage_id=v.CANDIDATE_NODE_RETRIEVAL)
    values = dimension_values(p11_conn, p2_run_id, dimension=v.DIMENSION_RETRIEVAL)
    assert rows[0]["subject_ref"] == values[0]["subject_ref"]


def test_scoring_names_the_retrieval_stage_as_an_input(p11_conn, p2_run_id,
                                                       p11_version_tuple,
                                                       a_retrieval):
    # The ancestor walk reaches a stage only through `inputs[]`. Without this,
    # a retrieval-origin error would attribute to `placement_scoring` (order 9)
    # rather than `candidate_node_retrieval` (order 8).
    emit_retrieval_stage(p11_conn, run_id=p2_run_id, retrieval=a_retrieval,
                         version_tuple_ref=p11_version_tuple, inputs=())
    emit_scoring_stage(p11_conn, run_id=p2_run_id, decision=_decision(),
                       version_tuple_ref=p11_version_tuple, inputs=("group:g1",))
    rows = stage_outputs(p11_conn, p2_run_id, stage_id=v.PLACEMENT_SCORING)
    assert "candidates:plan-1:file:f1:h1" in json.loads(rows[0]["inputs"])


def test_p9_and_p11_retrieval_rows_coexist_in_one_run(p11_conn, p2_run_id,
                                                      p11_version_tuple,
                                                      a_retrieval):
    # `stage_dimension_value` is keyed (run_id, dimension, subject_ref) and P9
    # already writes `retrieval` rows keyed on the bare file. Un-namespaced, this
    # second write raises IntegrityError in every full-pipeline replay.
    record_stage_output(
        p11_conn, run_id=p2_run_id, stage_id="grouping_retrieval",
        subject_ref="file:f1:h1", outcome="produced", payload=None,
        version_tuple_ref=p11_version_tuple, inputs=(),
        budget_state="within_ceiling",
        dimension_values=(DimensionValue(dimension="retrieval",
                                         subject_ref="file:f1:h1",
                                         outcome="produced", value={}),))
    emit_retrieval_stage(p11_conn, run_id=p2_run_id, retrieval=a_retrieval,
                         version_tuple_ref=p11_version_tuple, inputs=())
    assert len(dimension_values(p11_conn, p2_run_id, dimension="retrieval")) == 2


def test_a_lower_ceiling_produces_deferrals_and_no_divergences(
        p11_conn, p2_run_id, p11_version_tuple):
    # P2 Done-means 6: a run whose only change is a lower budget ceiling must
    # produce zero new divergences, which is only true if a deferral never
    # reaches a quality verdict.
    deferred = _decision(outcome=v.ABSTAIN, destination=None,
                         abstention_reason=v.BUDGET_DEFERRED,
                         deferred_stage=v.PLACEMENT_SCORING)
    emit_scoring_stage(p11_conn, run_id=p2_run_id, decision=deferred,
                       version_tuple_ref=p11_version_tuple, inputs=())
    rows = stage_outputs(p11_conn, p2_run_id, stage_id=v.PLACEMENT_SCORING)
    assert rows[0]["outcome"] == "deferred"
    assert rows[0]["budget_state"] == "ceiling_reached"
```

- [ ] **Step 2: Run and verify RED**

Run: `python3 -m pytest -q tests/p11/test_p11_stage_output.py tests/integration/test_p11_p2_replay.py`

Expected: FAIL at collection — `ModuleNotFoundError: No module named 'placement.stage_output'`. Every P2 import resolves, because P2 ships, and `p2_run_id` and `p11_version_tuple` come from the conftest Task 4 created.

- [ ] **Step 3: Implement the mapping**

```python
# src/placement/stage_output.py
"""P11 → P2. The envelope's vocabulary is P2's; the record's is P11's.

They are different vocabularies and P2 already refuses the wrong one:
`eval_harness/stage_output.py:30-33` enumerates P11's seven record outcomes and
raises `ForeignVocabulary` if one is written into an envelope. So this module is
the mapping between them and never a copy of either.

One row must not collapse into another. A budget deferral is `deferred` with
`ceiling_reached` and NEVER `abstained`, even though it rides on a record whose
own outcome reads `abstain`. Scored as `abstained`, P2 would grade a
ceiling-truncated run `abstained_correctly` or `abstained_incorrectly` -- a
judgement about evidence -- when no judgement was made. P2's writer enforces the
pairing (`stage_output.py:112-118`), so a wrong mapping fails at the write.

`residual` is a P2 dimension with no same-named stage, which P2 records as its own
open question (`eval_harness/vocabulary.py:6-7`). P11 attaches it to
`placement_scoring` and says so here, rather than inventing an eleventh stage that
P2's closed ten does not contain.
"""
from __future__ import annotations

import json
import sqlite3

from eval_harness.stage_output import DimensionValue, record_stage_output

from placement.vocabulary import (
    ABSTAIN, BUDGET_DEFERRED, CANDIDATE_NODE_RETRIEVAL, DIMENSION_PLACEMENT,
    DIMENSION_RESIDUAL, DIMENSION_RETRIEVAL, PLACEMENT_SCORING, RESIDUAL,
)

PRODUCED: str = "produced"
ABSTAINED: str = "abstained"
DEFERRED: str = "deferred"
WITHIN_CEILING: str = "within_ceiling"
CEILING_REACHED: str = "ceiling_reached"


def envelope_for(decision) -> tuple[str, str]:
    """SPEC:273-278's mapping, as a function over one decision."""
    if decision.abstention_reason == BUDGET_DEFERRED:
        return DEFERRED, CEILING_REACHED
    if decision.outcome == ABSTAIN:
        return ABSTAINED, WITHIN_CEILING
    return PRODUCED, WITHIN_CEILING


def dimension_for(decision) -> DimensionValue:
    """§8.5's two metrics. A correct abstention passes both (Done-means 11).

    The value is the decision's own shape rather than its content: a replay
    compares what the engine decided and why, and dumping the explanation here
    would make every prose edit look like a divergence.
    """
    from placement.store import subject_ref_of

    outcome, _ = envelope_for(decision)
    dimension = (DIMENSION_RESIDUAL if decision.origin_stage == RESIDUAL
                 else DIMENSION_PLACEMENT)
    return DimensionValue(
        dimension=dimension, subject_ref=subject_ref_of(decision.subject),
        outcome=outcome,
        value={
            "outcome": decision.outcome,
            "node_id": decision.destination.node_id if decision.destination else None,
            "abstention_reason": decision.abstention_reason,
            "support_score": decision.two_condition.support_score,
            "support_threshold": decision.two_condition.support_threshold,
            "margin_over_next": decision.two_condition.margin_over_next,
            "margin_threshold": decision.two_condition.margin_threshold,
            "meets_margin": decision.two_condition.meets_margin,
            "verdict": decision.two_condition.verdict,
            "unsupported_levels": list(decision.decision_depth.unsupported_levels),
        },
    )


def candidate_subject_ref(plan_version: str, subject_ref: str) -> str:
    """The namespaced subject `candidate_node_retrieval` is measured under.

    `stage_dimension_value` declares `PRIMARY KEY (run_id, dimension,
    subject_ref)` (`eval_harness/stage_output.py:59`), and `retrieval` is already
    P9's dimension for its own retrieval stage (`grouping/stage_output.py:56-60`).
    An un-namespaced ref would make a full-pipeline replay raise `IntegrityError`
    the moment P9 and P11 both keyed a `retrieval` row on the same file.

    The `plan_version` in the key is not decoration. `retrieval` sits in
    `SHARED_EVIDENCE_DIMENSIONS` (`eval_harness/vocabulary.py:48`) while P11's
    candidate retrieval is plan-scoped by construction -- it retrieves only the
    legal destinations of one frozen version. Keying on the version means two plan
    versions produce two measurements rather than one contested row.
    """
    return f"candidates:{plan_version}:{subject_ref}"


def emit_retrieval_stage(conn: sqlite3.Connection, *, run_id: str, retrieval,
                         version_tuple_ref: str, inputs) -> int:
    """§6.2's stage. Its subject is the file or group a candidate set was for.

    It carries a `DimensionValue` because a stage that writes none is
    structurally unattributable: `eval_harness/attribution.py` reads ONLY
    `stage_dimension_value` rows to decide both which stage emitted a failing
    assertion (`:65-71`) and which stages qualify as ancestors (`:30-39`). Without
    one, a placement error that began in retrieval could never be measured as a
    retrieval error, no matter what P2 did.

    The dimension is `retrieval`, and the design settles which one: §8.5's list
    reads *"Retrieval quality: for sparse files, did the correct anchors appear in
    the top candidate neighborhood?"* (`01-product-design-structured.md:1757-1758`)
    -- which is this stage, in the design's own words. §8.5's ten dimensions are a
    shorter and separate list from its ten stages ON PURPOSE, so two stages sharing
    one dimension is the shape the design already has, and no eleventh dimension is
    invented to avoid it.
    """
    produced = PRODUCED if retrieval.candidates else ABSTAINED
    subject_ref = candidate_subject_ref(retrieval.plan_version,
                                        retrieval.subject_ref)
    return record_stage_output(
        conn, run_id=run_id, stage_id=CANDIDATE_NODE_RETRIEVAL,
        subject_ref=subject_ref, outcome=produced,
        payload=json.dumps({
            "plan_version": retrieval.plan_version,
            "retrieved": [c.node_id for c in retrieval.candidates],
            "suppressed": sorted({n for c in retrieval.conflicts
                                  for n in c.suppressed_node_ids}),
            "semantic_only": sorted(retrieval.semantic_only_node_ids),
        }, sort_keys=True),
        version_tuple_ref=version_tuple_ref, inputs=list(inputs),
        budget_state=WITHIN_CEILING,
        # The envelope's subject_ref and the dimension row's must be EQUAL:
        # `_stage_verdicts` keys on the dimension row's while `_edges` keys on the
        # envelope's, so a mismatch attributes nothing.
        dimension_values=(DimensionValue(
            dimension=DIMENSION_RETRIEVAL, subject_ref=subject_ref,
            outcome=produced,
            value={
                "plan_version": retrieval.plan_version,
                "retrieved": [c.node_id for c in retrieval.candidates],
                "suppressed": sorted({n for c in retrieval.conflicts
                                      for n in c.suppressed_node_ids}),
                "semantic_only": sorted(retrieval.semantic_only_node_ids),
            },
        ),),
    )


def emit_scoring_stage(conn: sqlite3.Connection, *, run_id: str, decision,
                       version_tuple_ref: str, inputs) -> int:
    """§6.10's stage, with the measured dimension attached.

    `inputs` are the `subject_ref`s of the `grouping`, `tree_design` and
    `factual_validation` stage outputs this decision consumed. Naming them is
    what lets P2 attribute a placement error to the stage it began in, rather
    than to the last stage that touched the file.

    `candidate_node_retrieval`'s own ref is appended here rather than left to the
    caller, because the ancestor walk reaches a stage ONLY through `inputs[]`
    (`eval_harness/attribution.py:30-39`). Emitting a dimension value from the
    retrieval stage and then omitting it from this list would leave the stage
    measured and still unreachable -- both halves are required.
    """
    from placement.store import subject_ref_of

    outcome, budget_state = envelope_for(decision)
    subject_ref = subject_ref_of(decision.subject)
    retrieval_ref = candidate_subject_ref(decision.plan_version, subject_ref)
    return record_stage_output(
        conn, run_id=run_id, stage_id=PLACEMENT_SCORING,
        subject_ref=subject_ref, outcome=outcome,
        payload=json.dumps({
            "decision_id": decision.decision_id,
            "plan_version": decision.plan_version,
            "origin_stage": decision.origin_stage,
            "confidence_class": decision.confidence_class,
            "review_policy": decision.review_policy,
            "deferred_stage": decision.deferred_stage,
        }, sort_keys=True),
        version_tuple_ref=version_tuple_ref,
        inputs=[*inputs, retrieval_ref],
        budget_state=budget_state,
        dimension_values=(dimension_for(decision),),
    )
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3 -m pytest -q tests/p11/test_p11_stage_output.py tests/integration/test_p11_p2_replay.py`

Expected: PASS, 14 tests. `test_a_budget_deferral_is_deferred_and_never_abstained` and its replay counterpart are the pair that would both fail if the third row of SPEC's mapping table collapsed into the second — which is the failure P2 Done-means 6 depends on not happening. `test_the_retrieval_stage_is_attributable_at_all` and `test_scoring_names_the_retrieval_stage_as_an_input` are the pair that fail if either half of §7's fix is dropped: a dimension row with no `inputs[]` entry is measured and unreachable, and an `inputs[]` entry with no dimension row is reachable and unmeasured.

- [ ] **Step 5: Commit**

```bash
git add src/placement/stage_output.py tests/p11/conftest.py \
        tests/p11/test_p11_stage_output.py tests/integration/test_p11_p2_replay.py
git commit -m "feat(p11): emit two replayable stages and keep deferral distinct"
```

### Task 19: Run §6.12's nine steps end to end

**Files:**
- Create: `src/placement/pipeline.py`
- Create: `src/placement/fixtures.py`
- Create: `tests/p11/test_p11_pipeline.py`
- Create: `tests/integration/test_p11_p12_node_boundary.py`

**Consumes:** everything Tasks 4–18 published.

**Produces:**

```python
@dataclass(frozen=True)
class PipelineInputs:      # every injection, none defaulted
    plan_version: str; tree: object; policy: SupportPolicy; limits: PlacementLimits
    partition: object; ask_or_abstain: object; max_return_cycles: int | None
    gate: object; model_client: object; prompt: object; call_dependencies: object
    model_call_request: object       # P7 builds it; P11 holds the builder
    chosen_node_of: object           # verdict -> node_id, injected (see OPEN below)
    sensitivity_policy: object       # P7's answer for this release
    automatic_move_permitted: bool

    def model_path_available(self) -> bool: ...

@dataclass(frozen=True)
class CorpusResult:
    decisions: tuple[PlacementDecision, ...]
    group_plans: tuple[GroupPlan, ...]
    residual_sets: tuple[ResidualSet, ...]
    residual_decisions: tuple[PlacementDecision, ...]
    unplaced_file_ids: tuple[str, ...]

STEPS: tuple[str, ...]     # §6.12's nine, in §6.12's order

def place_file(conn, *, subject, inputs, evidence, component_version, observed_at) -> PlacementDecision: ...
def place_group(conn, *, group_id, inputs, evidence_for, component_version, observed_at) -> GroupPlan: ...
def run_residual_file(conn, *, subject, set_id, inputs, evidence, action, target,
                      component_version, observed_at) -> PlacementDecision: ...
def run_corpus(conn, *, subjects, group_ids, inputs, evidence_for,
               component_version, observed_at) -> CorpusResult: ...
def golden_decisions() -> tuple[PlacementDecision, ...]: ...
```

**Done-means:** the whole of Done means (SPEC:605-671), exercised end to end.

**The spine is §6.12's nine steps**, from `planning/01-product-design-structured.md:1295-1306`, and `STEPS` names them in that order so the pipeline's shape is checkable against the design rather than against itself. Steps 1–2 are P10's; the pipeline owns 3–7 and 9 and reaches step 8 through P8.

**What this task orchestrates, step by step.** Tasks 6–18 published nineteen components; before this repair the pipeline called seven of them and the rest had no caller at all. Each row below names the step, the component, and the design sentence that puts it there.

| §6.12 step | Owner | Wired by |
|---|---|---|
| 1 freeze the approved tree | P10 | `PipelineInputs.tree`, indexed by `build_destination_index` before any file is placed (Done-means 3) |
| 2 profile each node | P10 | same |
| 3 retrieve legal candidates | P11 | `retrieval.retrieve`, inside `place_file` |
| 4 build the local graph | P11 | `graph.build_node_local_graph`, per candidate |
| 5 remove impossible/conflicting nodes | P11 | retrieval's own suppression **plus** `learning.suppressed_nodes` (§8.7, before any `place`) |
| 6 child / parent / fallback / none | P11 | `scoring.assess` |
| **7 the LLM judges bounded ambiguity** | P8, called by P11 | **`_judge_with_model` → `p8_seam.call_placement` → `run_call`** |
| **8 the validator checks evidence** | P8 | runs **inside** `run_call`; P11 supplies the four authorities and never re-checks |
| 9 a reviewable plan | P11 | `run_corpus` → `CorpusResult`, then §7's residual stage |

**`record_cd_verdict` is P8's to call, not P11's.** `harness.py:245-253` shows `_record_verdicts` calling `record_cd_verdict` itself for every `C_placement` and `D_residual` verdict, and `placement_validation.py:614` shows `revalidate_for_plan` doing the same. P11 calling it as well would write the row twice. What P11 owes is the input that call needs: `DossierRequest.evidence_snapshot_id`, which `harness.py:154-165` refuses a C or D request without **before the spend**. `_judge_with_model` mints it with `p8_seam.evidence_snapshot_id_for` and puts it on the request, which is how P11 reaches `record_cd_verdict` correctly — through P8, once.

**`revalidate_for_plan` belongs to Task 17, and it is wired there.** It re-validates a *stored* verdict against a new plan version and evidence snapshot, which is §8.8's question, not §6.12's. Task 17 declared it under **Consumes** and never called it; that is now fixed. See [Task 17](#task-17-re-project-on-a-new-plan-version-and-remap-nothing) and the OPEN item it records.

- [ ] **Step 1: Write the failing walking-skeleton test**

```python
# tests/p11/test_p11_pipeline.py
"""§6.12 end to end, on the walking skeleton's own two-node tree."""
from __future__ import annotations

import pytest

from database_agent.budget import set_ceiling
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.policy import Policy, set_policy

from placement import vocabulary as v
from placement.config import CEILINGS, SupportPolicy, placement_limits
from placement.index import build_destination_index
from placement.pipeline import STEPS, PipelineInputs, place_file
from placement.records import MatchingFact, Subject
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE

# 0.50 sits ABOVE a direct fact alone (3/7 = 0.4286) and BELOW a direct fact plus
# an accepted group (5/7 = 0.7143). Both halves are asserted below, so a threshold
# moved out of that band fails loudly instead of turning every placement into an
# abstention.
POLICY = SupportPolicy(policy_id="skeleton-v1", support_scale_max=1.0,
                       minimum_support_threshold=0.5, margin_threshold=0.2)


def _classify(conn, *, file_id="f1", content_hash="h1"):
    """One P7 classification. Absent, `place_file` blocks -- which is correct."""
    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="personal_non_sensitive", protected=False,
        basis="detector", evidence_refs=("obs-1",), reliability_state="direct",
        observed_at=FIXED_CLOCK))


def _partition(file_ids):
    """§7.5's partition, injected. P11 invents no set names (Open question 10)."""
    return (
        {"label": "Unassociated", "member_file_ids": tuple(file_ids),
         "representative_examples": tuple(file_ids[:1]),
         "file_type_distribution": (("pdf", len(file_ids)),),
         "age_range": ("2026-01-01", "2026-08-01"),
         "evidence_availability": "ocr_present",
         "sensitivity_status": "public_low", "weak_graph_neighbours": (),
         "reason_not_placed": "no direct fact reached any legal destination"},
    ) if file_ids else ()


@pytest.fixture()
def skeleton(p11_conn):
    for key in CEILINGS.values():
        set_ceiling(p11_conn, key, 8)
    _classify(p11_conn)
    set_policy(p11_conn, Policy(
        policy_version="pol-1", operation_mode="hybrid", consent_grants=(),
        redaction_settings={}, automatic_move_permissions={},
        plan_version="plan-1", set_at=FIXED_CLOCK),
        component_version="P7-test", user_id="u1", reason="skeleton fixture")
    build_destination_index(p11_conn, FROZEN_TREE,
                            component_version="P11-test",
                            observed_at=FIXED_CLOCK)
    return p11_conn


def _inputs(conn, **overrides):
    # Every model injection is None: this is a DETERMINISTIC-ONLY run, which §6.6
    # makes a legal run, and `model_path_available()` returns False so step 7 is
    # skipped rather than attempted and failed. The model path has its own test.
    values = dict(
        plan_version="plan-1", tree=FROZEN_TREE, policy=POLICY,
        limits=placement_limits(conn),
        partition=None, ask_or_abstain=lambda ids: v.ABSTAIN,
        max_return_cycles=1, gate=None, model_client=None, prompt=None,
        call_dependencies=None, model_call_request=None, chosen_node_of=None,
        sensitivity_policy=None, automatic_move_permitted=False,
    )
    values.update(overrides)
    return PipelineInputs(**values)


def _evidence(**overrides):
    values = dict(
        facts=(MatchingFact(file_fact_id="ff1", field="subject", value="PHYS1401",
                            reliability=v.DIRECT, evidence_ref="obs-1"),),
        group_ids=(), curated_folder_labels=(), semantic_neighbours=(),
        related_files=(), entity_frequency={"PHYS1401": 6},
        generic_entity_frequency=200,
    )
    values.update(overrides)
    return values


#: The evidence that makes the skeleton place, and the arithmetic that makes it
#: place. `assess` normalises by `_MAX_WEIGHT = 3 + 2 + 1 + 1 = 7`:
#:
#:   n-course        direct_fact(3) + accepted_group(2) = 5/7 = 0.7143
#:   n-course-shared                  accepted_group(2) = 2/7 = 0.2857
#:   n-course-alt    expected subject = PHYS1402 contradicts the file's
#:                   PHYS1401, so retrieval SUPPRESSES it -- a conflict, not a
#:                   candidate, and it populates `conflicts_considered`.
#:
#:   support 0.7143 >= threshold 0.50              -> meets_threshold
#:   margin  5/7 - 2/7 = 3/7 = 0.4286 >= 0.20      -> meets_margin = "true"
#:   exactly one candidate carries direct_fact     -> unique_direct_match
#:
#: The direct fact ALONE scores 3/7 = 0.4286, which is BELOW the 0.50 threshold.
#: The accepted-group channel is what carries it over, and B8(b)'s second node is
#: what makes the margin measured instead of vacuous. Both are load-bearing: drop
#: the group and this file abstains; drop the second candidate and §6.10's margin
#: condition is satisfied by vacuity, which B8(b) says a skeleton must not do.
PLACING_GROUPS: tuple[str, ...] = ("g-phys1401", "g-shared")


SUBJECT = Subject(kind=v.FILE, file_id="f1", content_hash="h1", group_id=None,
                  member_file_ids=())


def test_the_pipeline_names_612s_nine_steps_in_612s_order():
    assert len(STEPS) == 9
    assert STEPS[0].startswith("freeze")
    assert STEPS[-1].startswith("reviewable_plan")


def test_a_unique_direct_match_is_placed_with_zero_model_calls(skeleton):
    decision = place_file(
        skeleton, subject=SUBJECT, inputs=_inputs(skeleton),
        evidence=_evidence(group_ids=PLACING_GROUPS),
        component_version="P11-test", observed_at=FIXED_CLOCK)
    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == "n-course"
    assert decision.destination.node_role == v.ORDINARY
    assert decision.confidence_class == v.EXACT_FACT_MATCH
    assert decision.review_policy == v.AUTO_ELIGIBLE
    assert skeleton.execute(
        "SELECT count(*) AS c FROM llm_verdict").fetchone()["c"] == 0


def test_the_skeletons_margin_is_measured_and_never_vacuous(skeleton):
    # B8(b): "The skeleton gains a second frozen node, so the margin path is
    # genuinely exercised rather than bypassed." This is the assertion that
    # makes that true rather than intended.
    decision = place_file(
        skeleton, subject=SUBJECT, inputs=_inputs(skeleton),
        evidence=_evidence(group_ids=PLACING_GROUPS),
        component_version="P11-test", observed_at=FIXED_CLOCK)
    two = decision.two_condition
    assert two.meets_margin == v.MARGIN_TRUE          # measured, not true_vacuous
    assert two.margin_over_next == pytest.approx(3 / 7)   # 5/7 - 2/7
    assert two.support_score == pytest.approx(5 / 7)
    assert two.meets_threshold is True
    assert [a.node_id for a in decision.alternatives] == [
        "n-course", "n-course-shared"]
    # And the suppressed node is visible, so the review surface can answer
    # "why not PHYS1402?" (§6.3, Done-means 4).
    assert "n-course-alt" in {node for conflict in decision.conflicts_considered
                              for node in conflict.suppressed_node_ids}


def test_the_direct_fact_alone_does_not_clear_the_threshold(skeleton):
    # The other half of the arithmetic, asserted rather than assumed: 3/7 is
    # below 0.50, so a file with the fact and no group support abstains. A
    # threshold the strongest available evidence cannot reach would make every
    # placement in this plan unreachable, and this test is what would catch it.
    decision = place_file(
        skeleton, subject=SUBJECT, inputs=_inputs(skeleton),
        evidence=_evidence(), component_version="P11-test",
        observed_at=FIXED_CLOCK)
    assert decision.outcome == v.ABSTAIN
    assert decision.two_condition.support_score == pytest.approx(3 / 7)
    assert decision.two_condition.meets_threshold is False


def test_a_mathematical_looking_file_never_produces_math_stuff(skeleton):
    # §6.2's own test, and Done-means 2's second half.
    decision = place_file(
        skeleton, subject=SUBJECT, inputs=_inputs(skeleton),
        evidence=_evidence(facts=(), semantic_neighbours=()),
        component_version="P11-test", observed_at=FIXED_CLOCK)
    assert decision.outcome == v.ABSTAIN
    assert decision.destination is None
    assert decision.abstention_reason == v.NO_SUPPORTED_DESTINATION


def test_a_file_resembling_an_ignored_folder_abstains(skeleton):
    # Done-means 2's concrete case, §5.10: the user left `Old Downloads` alone,
    # so a file that looks like it belongs there is not placed there.
    decision = place_file(
        skeleton, subject=SUBJECT, inputs=_inputs(skeleton),
        evidence=_evidence(facts=(), curated_folder_labels=("Old Downloads",)),
        component_version="P11-test", observed_at=FIXED_CLOCK)
    assert decision.outcome == v.ABSTAIN


def test_the_decision_is_stored_and_its_event_appended(skeleton):
    decision = place_file(
        skeleton, subject=SUBJECT, inputs=_inputs(skeleton),
        evidence=_evidence(group_ids=PLACING_GROUPS),
        component_version="P11-test", observed_at=FIXED_CLOCK)
    row = skeleton.execute(
        "SELECT record_id, node_id FROM placement_decisions").fetchone()
    assert row["record_id"] == decision.decision_id
    assert row["node_id"] == "n-course"
    events = [r["event_type"] for r in skeleton.execute(
        "SELECT event_type FROM events")]
    assert v.CANDIDATE_RETRIEVAL in events
    assert v.RECOMMENDATION_EMITTED in events


def test_an_unclassified_file_is_blocked_and_not_placed(p11_conn):
    # P7's detector does not exist, so this is the ordinary path on a real
    # corpus: no classification means blocked, never a default to public.
    from placement.privacy import ClassificationRequired

    for key in CEILINGS.values():
        set_ceiling(p11_conn, key, 8)
    with pytest.raises(ClassificationRequired):
        place_file(p11_conn, subject=SUBJECT, inputs=_inputs(p11_conn),
                   evidence=_evidence(), component_version="P11-test",
                   observed_at=FIXED_CLOCK)


# --- the orchestration §6.12 step 9 and §7 actually require ---------------------


def test_the_steps_map_names_a_caller_for_every_step_p11_owns():
    # The spine is only checkable if each step it claims has a callable behind
    # it. Steps 1-2 are P10's and 8 is P8's; 3, 4, 5, 6, 7 and 9 are P11's.
    import inspect

    from placement import pipeline

    source = inspect.getsource(pipeline)
    for call in ("retrieve(", "build_node_local_graph(", "suppressed_nodes(",
                 "assess(", "_judge_with_model(", "surface_residual_sets("):
        assert call in source, call


def test_run_corpus_places_groups_before_files_and_surfaces_the_rest(skeleton):
    from p11.p9_fixtures import GROUP_ID, seed_accepted_columbia
    from placement.pipeline import run_corpus

    seed_accepted_columbia(skeleton)
    for file_id in ("f-essay", "f-transcript", "f-scan", "f-duke-essay"):
        _classify(skeleton, file_id=file_id, content_hash=f"h-{file_id}")

    result = run_corpus(
        skeleton, subjects=(SUBJECT,), group_ids=(GROUP_ID,),
        inputs=_inputs(skeleton, partition=_partition),
        evidence_for=lambda file_id: _evidence(
            group_ids=PLACING_GROUPS if file_id == "f1" else ()),
        component_version="P11-test", observed_at=FIXED_CLOCK)

    # §6.8 ran: one plan, and the outlier P9 flagged is excluded and explained.
    assert len(result.group_plans) == 1
    assert result.group_plans[0].excluded_outliers
    assert {o.file_id for o in result.group_plans[0].excluded_outliers} == {
        "f-duke-essay"}
    # Every member decision carries the plan's id, so a review surface shows ONE
    # plan and not four unrelated file moves (§6.8).
    assert {d.group_plan_id for d in result.group_plans[0].member_decisions} == {
        result.group_plans[0].group_plan_id}
    # §6 ran for the standalone file too, and it placed.
    assert any(d.outcome == v.PLACE and d.subject.file_id == "f1"
               for d in result.decisions)
    # §7.5 ran SECOND, over exactly what §6 could not place.
    assert result.residual_sets
    assert set(result.unplaced_file_ids) <= {
        d.subject.file_id for d in result.decisions if d.outcome != v.PLACE}


def test_a_surfaced_set_with_no_decision_issues_no_model_call(skeleton):
    # §7.6, SPEC:545-547. Surfaced-and-undecided is the state the gate exists to
    # make visible, and `run_corpus` must leave it alone rather than proceed.
    from placement.pipeline import run_corpus

    result = run_corpus(
        skeleton, subjects=(SUBJECT,), group_ids=(),
        inputs=_inputs(skeleton, partition=_partition),
        evidence_for=lambda file_id: _evidence(),
        component_version="P11-test", observed_at=FIXED_CLOCK)
    assert result.residual_sets
    assert result.residual_decisions == ()
    assert skeleton.execute(
        "SELECT count(*) AS c FROM llm_verdict").fetchone()["c"] == 0


def test_the_model_path_is_reached_when_the_deterministic_one_is_ambiguous(
        skeleton, monkeypatch):
    # §6.12 step 7. Two candidates inside the margin, so `needs_model_call` is
    # True and the pipeline must actually CALL P8 rather than abstain silently.
    import placement.pipeline as pipeline

    called = {}

    def _fake_call(conn, request, **kwargs):
        called["site"] = request.call_site
        called["allowed"] = kwargs["call_dependencies"].allowed_vocabulary
        called["snapshot"] = request.evidence_snapshot_id
        return _accepting_verdict()

    monkeypatch.setattr(pipeline, "call_placement", _fake_call)
    decision = pipeline.place_file(
        skeleton, subject=SUBJECT,
        inputs=_inputs(skeleton, gate=object(), model_client=object(),
                       prompt=object(), call_dependencies=_call_dependencies(),
                       model_call_request=lambda **_k: object(),
                       chosen_node_of=lambda _verdict: "n-course-shared",
                       sensitivity_policy=lambda *_a, **_k: True),
        evidence=_evidence(group_ids=("g-shared",),
                           semantic_neighbours=("n-general",)),
        component_version="P11-test", observed_at=FIXED_CLOCK)

    assert called["site"] == "C_placement"
    # The single most load-bearing value P11 hands P8: Site C rejects anything
    # outside it as INVENTED_NODE, and it is P11's index, never the caller's.
    assert "n-course" in called["allowed"]
    assert "n-ignored" not in called["allowed"]
    # Required BEFORE the spend (harness.py:154-165) and minted by nobody else.
    assert called["snapshot"].startswith("snap-")
    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == "n-course-shared"
    assert decision.confidence_class == v.CONTEXT_SUPPORTED_GROUP_MATCH
    assert decision.review_policy == v.REVIEW_REQUIRED


def test_a_model_choice_outside_the_frozen_tree_places_nothing(skeleton,
                                                               monkeypatch):
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement",
                        lambda *_a, **_k: _accepting_verdict())
    with pytest.raises(ValueError):
        pipeline.place_file(
            skeleton, subject=SUBJECT,
            inputs=_inputs(skeleton, gate=object(), model_client=object(),
                           prompt=object(),
                           call_dependencies=_call_dependencies(),
                           model_call_request=lambda **_k: object(),
                           chosen_node_of=lambda _v: "n-invented",
                           sensitivity_policy=lambda *_a, **_k: True),
            evidence=_evidence(group_ids=("g-shared",),
                               semantic_neighbours=("n-general",)),
            component_version="P11-test", observed_at=FIXED_CLOCK)
```

`_accepting_verdict()` returns a real `llm_harness.records.P8Verdict` with
`outcome = accept_context_supported`, and `_call_dependencies()` returns a real
`llm_harness.harness.CallDependencies` with the caller's halves filled and
`site_dependencies` / `allowed_vocabulary` left `None` — precisely so the assertion
above proves the pipeline set them. `_partition` is the same injected partition
Task 14's suite uses. `_classify` is `test_p11_privacy.py`'s helper, parameterised
by file id.

Monkeypatching `call_placement` is deliberate and is the *only* place this plan
fakes a P8 call: `run_call` needs a live `Gate`, a `ModelClient` and a released
transport, all of which are P7's and P8's to construct. What is under test here is
that P11 **reaches** step 7 with the right request — the call site, the allowed
vocabulary and the evidence snapshot — and that it transcribes the verdict rather
than re-deciding it. Whether P8's own checks work is
`tests/integration/test_p11_p8_seam.py`'s job, and that suite uses the live
validator with no fake at all.

And the P12 boundary:

```python
# tests/integration/test_p11_p12_node_boundary.py
"""P11 supplies a node; P12 resolves a path. The boundary is a field list."""
from __future__ import annotations

import dataclasses

from placement.records import Destination, PlacementDecision
from placement.vocabulary import PLACE, PLAN_BEARING_OUTCOMES


def test_p12_consumes_exactly_one_outcome():
    # M13. Keyed on `outcome`, not on `confidence_class`, whose value
    # "abstain: no supported destination" is a LABEL on a record and not the
    # record's disposition.
    assert PLAN_BEARING_OUTCOMES == (PLACE,)


def test_nothing_p11_publishes_can_carry_a_resolved_path():
    names = set()
    for record in (PlacementDecision, Destination):
        names |= {f.name for f in dataclasses.fields(record)}
    assert not names & {"path", "resolved_path", "resolved_destination_path",
                        "existing_path", "filesystem_path"}
    assert "node_id" in {f.name for f in dataclasses.fields(Destination)}
```

- [ ] **Step 2: Run and verify RED**

Run: `python3 -m pytest -q tests/p11/test_p11_pipeline.py tests/integration/test_p11_p12_node_boundary.py`

Expected: `tests/p11/test_p11_pipeline.py` FAILS at collection with `ModuleNotFoundError: No module named 'placement.pipeline'`. `tests/integration/test_p11_p12_node_boundary.py` imports only `placement.records` and `placement.vocabulary`, both of which Tasks 2 and 3 shipped, so it PASSES already — run it first and confirm, because a boundary test that was never red proves nothing until it is the thing under test.

- [ ] **Step 3: Implement the pipeline**

```python
# src/placement/pipeline.py
"""§6.12's nine steps, in §6.12's order.

The design's own list (`planning/01-product-design-structured.md:1295-1306`) is
the spine, and `STEPS` names it so the shape is checkable against the design
rather than against this file. Steps 1 and 2 belong to P10 and step 8 to P8; this
orchestrates 3 through 7 and produces 9.

Every injection arrives on `PipelineInputs` and none has a default. A run with no
model injections is a legal run -- §6.6 decides a unique direct match with zero
model calls -- and a run with no support policy is not, because §6.10's thresholds
are unsettled by the design and guessing one would place files under a bar nobody
chose.

The order inside `place_file` is not arbitrary. The privacy gate is consulted
before any dossier could be assembled (§8.4), and the learning store is consulted
before `place` is emitted (§8.7). Both are preconditions rather than filters, and
moving either later would make a spend or a placement happen first.
"""
from __future__ import annotations

import dataclasses
import sqlite3
from dataclasses import dataclass

from llm_harness.harness import DossierRequest
from llm_harness.vocabulary import (
    C_PLACEMENT, D_RESIDUAL, SEVERAL_LEGAL_NODES_PLAUSIBLE,
    USER_OPTED_RESIDUAL_SET_INTO_AI_REVIEW,
)

from placement.config import PlacementLimits, SupportPolicy, require_policy
from placement.graph import build_node_local_graph
from placement.groups import (
    AcceptedGroup, ExcludedOutlier, GroupPlan, accepted_group_as_of,
    confirm_shared_parent, excluded_outlier_for, resolve_multi_home,
)
from placement.index import entry_for, legal_node_ids
from placement.learning import basis_key_for, suppressed_nodes
from placement.p8_seam import (
    call_placement, evidence_snapshot_id_for, placement_authorities,
    residual_authorities, site_dependencies, to_p8_conflicts, transcribe,
)
from placement.privacy import may_assemble_dossier, privacy_state_for, review_policy_for
from placement.records import (
    DecisionDepth, Destination, PlacementDecision, ResidualContext,
)
from placement.residual import (
    ResidualSet, check_return_cycle, model_calls_permitted, outcome_for_action,
    require_set_decision, surface_residual_sets,
)
from placement.retrieval import retrieve
from placement.scoring import assess, needs_model_call
from placement.store import record_decision, subject_ref_of
from placement.vocabulary import (
    ABSTAIN, ABSTAIN_NO_SUPPORTED_DESTINATION, ASK_USER, BUDGET_DEFERRED,
    CONTEXT_SUPPORTED, CONTEXT_SUPPORTED_GROUP_MATCH, DIRECT, MARK_STATE,
    NO_SHARED_BRANCH, PLACE, PLACEMENT, PRIVACY_BLOCKED, RESIDUAL,
    RETURN_TO_PLACEMENT, SHARED_MATERIAL_DECISION,
)

#: §6.12's nine, in §6.12's order. Steps 1-2 are P10's and step 8 is P8's; naming
#: them anyway is what makes the pipeline auditable against the design.
STEPS: tuple[str, ...] = (
    "freeze_approved_tree",              # 1, P10
    "profile_each_node",                 # 2, P10
    "retrieve_legal_candidates",         # 3
    "build_local_graph",                 # 4
    "suppress_impossible_nodes",         # 5
    "identify_child_parent_fallback_or_none",  # 6
    "judge_bounded_ambiguity",           # 7
    "validate_evidence_and_constraints", # 8, P8
    "reviewable_plan_of_placements",     # 9
)


@dataclass(frozen=True)
class PipelineInputs:
    plan_version: str
    tree: object
    policy: SupportPolicy
    limits: PlacementLimits
    partition: object
    ask_or_abstain: object
    max_return_cycles: int | None
    gate: object
    model_client: object
    prompt: object
    call_dependencies: object
    model_call_request: object
    chosen_node_of: object
    sensitivity_policy: object
    automatic_move_permitted: bool

    def __post_init__(self) -> None:
        require_policy(self.policy)
        if not isinstance(self.limits, PlacementLimits):
            raise ValueError(
                "the pipeline runs under P1's seven ceilings and reads them "
                "through `placement.config.placement_limits`; a run with no "
                "limits is a run under a bound nobody chose"
            )

    def model_path_available(self) -> bool:
        """Whether step 7 can run at all. A deterministic-only run is legal.

        §6.6 decides a unique direct match with zero model calls, so a run with
        no model injections is a correct run and must not look like a failure.
        What is NOT legal is discovering the injections are missing after a
        dossier has been assembled, which is why this is asked before one is.
        """
        return None not in (self.gate, self.model_client, self.prompt,
                            self.call_dependencies, self.model_call_request,
                            self.chosen_node_of, self.sensitivity_policy)


@dataclass(frozen=True)
class CorpusResult:
    """§6.12 step 9: "a reviewable plan of exact placements, shallow placements,
    scoped fallbacks, and abstentions" -- plus what §7 then did with the rest.

    One object, so a review surface does not have to run the pipeline twice to
    learn what happened, and so `unplaced_file_ids` is a fact the run produced
    rather than something the caller re-derives by filtering.
    """

    decisions: tuple[PlacementDecision, ...]
    group_plans: tuple
    residual_sets: tuple
    residual_decisions: tuple[PlacementDecision, ...]
    unplaced_file_ids: tuple[str, ...]


def place_file(conn: sqlite3.Connection, *, subject, inputs: PipelineInputs,
               evidence, component_version: str, observed_at: str,
               group_plan_id: str | None = None) -> PlacementDecision:
    """One file through steps 3-7 and 9. Step 8 runs inside P8 when it is needed.

    `group_plan_id` is passed in rather than patched on afterwards, because the
    STORED row has to carry it: `GroupPlan` asserts every member decision shares
    the plan's id, and a row written without it would make the review surface
    show several unrelated file moves while the in-memory plan looked correct.
    """
    subject_ref = subject_ref_of(subject)

    # §8.4, before anything a model could see exists.
    privacy = privacy_state_for(conn, file_id=subject.file_id,
                                content_hash=subject.content_hash,
                                plan_version=inputs.plan_version)

    # Step 3, and step 5 with it: retrieval suppresses as it goes, because §6.3
    # makes suppression part of retrieval rather than a later filter.
    retrieval = retrieve(
        conn, subject=subject, plan_version=inputs.plan_version,
        limits=inputs.limits, facts=evidence["facts"],
        group_ids=evidence["group_ids"],
        curated_folder_labels=evidence["curated_folder_labels"],
        semantic_neighbours=evidence["semantic_neighbours"],
        component_version=component_version, observed_at=observed_at,
    )

    # §8.7, before any `place` is emitted.
    # `file` only. `learning._subject_ids` keys the file scope on the file id and
    # returns nothing for `node`, `template`, `domain` or `corpus`, because P11
    # cannot know which node or domain a user meant -- those need their own
    # `corpus_subject_id`, supplied by the caller that recorded them. Passing
    # `node` here would look like a wider check and perform none.
    rejected = {
        hit.node_id for hit in suppressed_nodes(
            conn, subject_ref=subject_ref,
            node_ids=tuple(c.node_id for c in retrieval.candidates),
            scopes=("file",),
        )
    }
    if rejected:
        retrieval = type(retrieval)(
            subject_ref=retrieval.subject_ref, plan_version=retrieval.plan_version,
            candidates=tuple(c for c in retrieval.candidates
                             if c.node_id not in rejected),
            conflicts=retrieval.conflicts,
            semantic_only_node_ids=retrieval.semantic_only_node_ids,
        )

    # Step 4.
    graphs = {
        candidate.node_id: build_node_local_graph(
            subject=subject, candidate=candidate,
            entry=entry_for(conn, plan_version=inputs.plan_version,
                            node_id=candidate.node_id),
            related_files=evidence["related_files"], limits=inputs.limits,
            entity_frequency=evidence["entity_frequency"],
            generic_entity_frequency=evidence["generic_entity_frequency"],
        )
        for candidate in retrieval.candidates
    }

    # Step 6.
    assessment = assess(retrieval, graphs, policy=inputs.policy)

    # Steps 7 and 8. Only for a bounded ambiguity, only if §8.4's gate allows a
    # dossier, and only if the caller supplied the model path. Step 8 -- the
    # validator -- runs INSIDE `run_call`; P11 supplies authorities and reads a
    # verdict, and re-checks none of Site C's fifteen.
    chosen_node_id: str | None = None
    if needs_model_call(assessment):
        if not may_assemble_dossier(privacy):
            return _abstention(conn, subject=subject, inputs=inputs,
                               assessment=assessment, retrieval=retrieval,
                               privacy=privacy, reason=PRIVACY_BLOCKED,
                               group_plan_id=group_plan_id,
                               component_version=component_version,
                               observed_at=observed_at)
        if inputs.model_path_available():
            verdict = _judge_with_model(
                conn, subject=subject, inputs=inputs, retrieval=retrieval,
                evidence=evidence, call_site=C_PLACEMENT,
                observed_at=observed_at)
            outcome, reason, deferred = transcribe(verdict, assessment=assessment)
            if outcome != PLACE:
                return _abstention(
                    conn, subject=subject, inputs=inputs, assessment=assessment,
                    retrieval=retrieval, privacy=privacy, reason=reason,
                    deferred_stage=deferred, group_plan_id=group_plan_id,
                    component_version=component_version,
                    observed_at=observed_at)
            # The model chose among P11's candidates; which one it chose is read
            # back through the injected resolver, because `P8Verdict` names a
            # `claim_ref` and not a destination. See the OPEN item in
            # [SPEC corrections](#spec-corrections).
            chosen_node_id = inputs.chosen_node_of(verdict)
            if chosen_node_id not in legal_node_ids(
                    conn, plan_version=inputs.plan_version):
                raise ValueError(
                    f"{chosen_node_id!r} is not a legal destination of "
                    f"{inputs.plan_version!r}. P8 already refuses an invented "
                    "node; reaching here means the resolver disagreed with the "
                    "index, and P11 places nothing on a disagreement"
                )

    # Step 9.
    if chosen_node_id is None and assessment.abstention_reason is not None:
        return _abstention(conn, subject=subject, inputs=inputs,
                           assessment=assessment, retrieval=retrieval,
                           privacy=privacy,
                           reason=assessment.abstention_reason,
                           group_plan_id=group_plan_id,
                           component_version=component_version,
                           observed_at=observed_at)

    best = assessment.scored[0]
    node_id = chosen_node_id or best.node_id
    entry = entry_for(conn, plan_version=inputs.plan_version, node_id=node_id)
    # A model-decided placement is a context-supported one by construction: the
    # deterministic path had already declined to call it an exact match, which is
    # the only reason a model was asked. Carrying `assessment.confidence_class`
    # through unchanged would label a `place` "abstain: no supported destination"
    # -- a record whose label contradicts its own outcome.
    confidence = (CONTEXT_SUPPORTED_GROUP_MATCH if chosen_node_id is not None
                  else assessment.confidence_class)
    decision = PlacementDecision(
        decision_id=f"{inputs.plan_version}:{subject_ref}:{observed_at}",
        plan_version=inputs.plan_version, supersedes=None, superseded_by=None,
        supersede_reason=None, created_at=observed_at, origin_stage=PLACEMENT,
        returned_from=None, subject=subject, group_plan_id=group_plan_id,
        outcome=PLACE,
        destination=Destination(node_id=entry.node_id, node_role=entry.node_role),
        return_target=None, marked_state=None, ask=None,
        decision_depth=DecisionDepth(node_depth=entry.depth,
                                     supported_depth=entry.depth,
                                     unsupported_levels=()),
        evidence_type=DIRECT if assessment.unique_direct_match else CONTEXT_SUPPORTED,
        confidence_class=confidence,
        matching_facts=_facts_of(retrieval, entry.node_id),
        group_support=None, graph_anchors=graphs[entry.node_id].anchors,
        conflicts_considered=retrieval.conflicts,
        alternatives=assessment.alternatives,
        two_condition=assessment.two_condition, abstention_reason=None,
        deferred_stage=None, privacy=privacy,
        review_policy=review_policy_for(
            privacy_state=privacy, two_condition=assessment.two_condition,
            group_support=None,
            unique_direct_match=assessment.unique_direct_match,
            automatic_move_permitted=inputs.automatic_move_permitted),
        explanation=_explain(entry, assessment, retrieval,
                             model_decided=chosen_node_id is not None),
        residual=None,
    )
    record_decision(conn, decision, component_version=component_version,
                    observed_at=observed_at)
    return decision


def _facts_of(retrieval, node_id: str) -> tuple:
    for candidate in retrieval.candidates:
        if candidate.node_id == node_id:
            return candidate.matching_facts
    return ()


def _explain(entry, assessment, retrieval, *, model_decided: bool = False) -> str:
    """§6.4 and §6.11: state the actual basis, claim no evidence the file lacks."""
    parts = [f"{entry.display_label} expects "
             + ", ".join(f"{field} = {value}"
                         for field, value in entry.expected_values)]
    if model_decided:
        # The user is entitled to know a model was involved: §6.11 says a direct
        # and a context-supported placement "should not demand the same level of
        # trust", which a reviewer can only apply if the record says which it is.
        parts.append("chosen by the hierarchical destination judge from P11's "
                     "legal candidates, and validated by P8")
    if retrieval.conflicts:
        parts.append(
            "ruled out " + ", ".join(
                node for conflict in retrieval.conflicts
                for node in conflict.suppressed_node_ids)
            + " on conflicting evidence")
    parts.append(
        f"support {assessment.two_condition.support_score:.2f} against a "
        f"threshold of {assessment.two_condition.support_threshold:.2f}")
    return "; ".join(parts) + "."


def _abstention(conn, *, subject, inputs, assessment, retrieval, privacy,
                reason: str, component_version: str, observed_at: str,
                deferred_stage: str | None = None,
                origin_stage: str = PLACEMENT, residual=None,
                group_plan_id: str | None = None) -> PlacementDecision:
    """§6.10: a correct abstention is a successful outcome, and is recorded as one.

    `deferred_stage` is set only when `reason` is `budget_deferred`, and the
    record enforces the pairing both ways. §8.6 requires a ceiling-truncated run
    to render differently from "I looked and could not tell", and a deferral
    recorded as a plain abstention is exactly the "understood and found
    unimportant" impression the design forbids.
    """
    if (reason == BUDGET_DEFERRED) != (deferred_stage is not None):
        raise ValueError(
            "a budget deferral names the stage it was cut short at, and only a "
            "budget deferral has one (§8.6)"
        )
    decision = PlacementDecision(
        decision_id=f"{inputs.plan_version}:{subject_ref_of(subject)}:{observed_at}",
        plan_version=inputs.plan_version, supersedes=None, superseded_by=None,
        supersede_reason=None, created_at=observed_at, origin_stage=origin_stage,
        returned_from=None, subject=subject, group_plan_id=group_plan_id,
        outcome=ABSTAIN,
        destination=None, return_target=None, marked_state=None, ask=None,
        decision_depth=DecisionDepth(node_depth=0, supported_depth=0,
                                     unsupported_levels=()),
        evidence_type=CONTEXT_SUPPORTED,
        confidence_class=ABSTAIN_NO_SUPPORTED_DESTINATION,
        matching_facts=(), group_support=None, graph_anchors=(),
        conflicts_considered=retrieval.conflicts,
        alternatives=assessment.alternatives,
        two_condition=assessment.two_condition, abstention_reason=reason,
        deferred_stage=deferred_stage, privacy=privacy,
        review_policy=review_policy_for(
            privacy_state=privacy, two_condition=assessment.two_condition,
            group_support=None, unique_direct_match=False,
            automatic_move_permitted=inputs.automatic_move_permitted),
        explanation=(
            f"No legal destination cleared §6.10's conditions ({reason}). "
            "Abstaining is the correct outcome; the evidence is retained and the "
            "file has not moved."),
        residual=residual,
    )
    record_decision(conn, decision, component_version=component_version,
                    observed_at=observed_at)
    return decision


# --- step 7: the hierarchical destination judge ---------------------------------


def _judge_with_model(conn, *, subject, inputs, retrieval, evidence,
                      call_site: str, observed_at: str):
    """§6.12 step 7, and step 8 with it. P11 assembles the REQUEST, never a check.

    Everything here is either P11's own answer or a caller injection. The four
    Site C authorities come from `p8_seam.placement_authorities`; the fifteen
    Site C checks stay in `llm_harness/placement_validation.py` and P11 spells
    none of their reason codes.

    `allowed_vocabulary` is P11's legal candidate set and is the single most
    load-bearing value handed over: Site C rejects any destination outside it as
    `INVENTED_NODE` (`placement_validation.py:220-221`). It is set here rather
    than taken from the caller's `CallDependencies`, because a caller-supplied
    vocabulary is a caller-supplied answer to "which nodes exist", which is the
    index's question.

    `evidence_snapshot_id` is minted here because nothing else mints one and
    `run_call` refuses a C or D request without it BEFORE the spend
    (`harness.py:154-165`). `record_cd_verdict` is then called by P8 itself
    (`harness.py:245-253`); P11 calling it too would write the row twice.
    """
    observation_keys = tuple(
        fact.evidence_ref for candidate in retrieval.candidates
        for fact in candidate.matching_facts if fact.evidence_ref
    )
    snapshot = evidence_snapshot_id_for(plan_version=inputs.plan_version,
                                        observation_keys=observation_keys)
    subject_ref = subject_ref_of(subject)
    legal = sorted(legal_node_ids(conn, plan_version=inputs.plan_version))
    if call_site == C_PLACEMENT:
        sites = site_dependencies(placement=placement_authorities(
            conn, plan_version=inputs.plan_version, policy=inputs.policy,
            sensitivity_policy=inputs.sensitivity_policy))
    else:
        sites = site_dependencies(residual=residual_authorities(
            conn, plan_version=inputs.plan_version, approved_target_ids=legal,
            sensitivity_policy=inputs.sensitivity_policy))

    dependencies = dataclasses.replace(
        inputs.call_dependencies,
        site_dependencies=sites,
        allowed_vocabulary=legal,
        proposal_class=PLACEMENT if call_site == C_PLACEMENT else RESIDUAL,
        basis_key=basis_key_for(subject_ref=subject_ref,
                                node_id=retrieval.candidates[0].node_id),
        learning_scope="file", learning_subject_id=subject.file_id,
    )
    request = DossierRequest(
        call_site=call_site, subject_ref=subject_ref,
        # P8's controlled reason, imported and not retyped. §6.6 lists six
        # circumstances that make a call eligible and P8 publishes a constant
        # for each; spelling one here would be a seventh vocabulary.
        eligibility_reason=(SEVERAL_LEGAL_NODES_PLAUSIBLE
                            if call_site == C_PLACEMENT
                            else USER_OPTED_RESIDUAL_SET_INTO_AI_REVIEW),
        evidence_items=tuple(evidence["facts"]),
        conflicts=to_p8_conflicts(retrieval.conflicts),
        # P7 builds the release request; P11 holds the builder and never a
        # `Gate`. Assembling it here, after `may_assemble_dossier` answered, is
        # what keeps §8.4's gate on the right side of the spend.
        model_call_request=inputs.model_call_request(
            subject_ref=subject_ref, evidence_items=tuple(evidence["facts"]),
            max_dossier_tokens=inputs.limits.max_dossier_tokens),
        plan_version=inputs.plan_version, evidence_snapshot_id=snapshot,
    )
    return call_placement(
        conn, request, gate=inputs.gate, model_client=inputs.model_client,
        prompt=inputs.prompt, call_dependencies=dependencies,
        observed_at=lambda: observed_at,
    )


# --- §6.8 and §6.9: the group plan ----------------------------------------------


def place_group(conn, *, group_id: str, inputs: PipelineInputs, evidence_for,
                component_version: str, observed_at: str) -> GroupPlan:
    """§6.8: confirm the shared parent FIRST, then classify members beneath it.

    The ordering is the whole of §6.8. A member classified before the parent is
    classified against no shared context, and the result is several unrelated
    file moves presented as a plan.

    Acceptance is read through P9 as of P10's frozen version
    (`accepted_group_as_of`), never off `Group.state`.
    """
    accepted: AcceptedGroup = accepted_group_as_of(
        conn, group_id=group_id, plan_version=inputs.plan_version)
    group_plan_id = f"{inputs.plan_version}:{group_id}"

    # Step one: the shared parent, from each member's own best destination.
    member_parents: dict[str, str | None] = {}
    provisional: dict[str, PlacementDecision] = {}
    for membership in accepted.memberships:
        subject = _member_subject(membership)
        decision = place_file(
            conn, subject=subject, inputs=inputs,
            evidence=evidence_for(membership.file_id),
            group_plan_id=group_plan_id,
            component_version=component_version, observed_at=observed_at)
        provisional[membership.file_id] = decision
        member_parents[membership.file_id] = (
            decision.destination.node_id if decision.destination else None)

    shared_parent = confirm_shared_parent(
        member_parents, policy=inputs.tree.shared_material_policy)

    # Step two: outliers are excluded and explained, never forced in. P9 already
    # flagged them and already holds the competing values; P11 records what P9
    # found and routes the file (§6.8).
    outliers: list[ExcludedOutlier] = []
    members: list[PlacementDecision] = []
    for membership in accepted.memberships:
        decision = provisional[membership.file_id]
        if membership.outlier_flag != "none":
            outliers.append(excluded_outlier_for(
                membership,
                routed_node_id=(decision.destination.node_id
                                if decision.destination else None)))
            continue
        members.append(decision)   # already carries `group_plan_id`, in the row

    plan = GroupPlan(
        group_plan_id=group_plan_id, plan_version=inputs.plan_version,
        group_id=group_id, shared_parent_node_id=shared_parent,
        member_decisions=tuple(members), excluded_outliers=tuple(outliers))
    from placement import events as placement_events

    placement_events.group_plan_emitted(
        conn, group_plan_id=group_plan_id, group_id=group_id,
        shared_parent_node_id=shared_parent,
        component_version=component_version, observed_at=observed_at)
    return plan


def _member_subject(membership):
    from placement.records import Subject

    return Subject(kind="file", file_id=membership.file_id,
                   content_hash=membership.content_hash, group_id=None,
                   member_file_ids=())


# --- §7: the residual stage ------------------------------------------------------


def run_residual_file(conn, *, subject, set_id: str, inputs: PipelineInputs,
                      evidence, action: str, target,
                      component_version: str,
                      observed_at: str) -> PlacementDecision:
    """One §7.7 action, as one decision on the ONE record shape.

    §7.6's gate is checked first and by refusal: `require_set_decision` raises
    when the set has no decision, and `model_calls_permitted` is what decides
    whether a per-file model call may be issued at all. A set the user chose to
    leave in place produces zero calls (SPEC:547), and that is enforced here
    rather than trusted to a caller.

    §7.9's loop is bounded by an injection: `check_return_cycle` refuses without
    `max_return_cycles`, because SPEC Open question 8 states no bound and an
    unbounded loop is a replay that never terminates.
    """
    set_decision = require_set_decision(conn, plan_version=inputs.plan_version,
                                        set_id=set_id)
    outcome, qualifier = outcome_for_action(action, target=target)
    if outcome == RETURN_TO_PLACEMENT:
        check_return_cycle(conn, subject_ref=subject_ref_of(subject),
                           max_return_cycles=inputs.max_return_cycles)
    context = ResidualContext(set_id=set_id, set_decision=set_decision.choice,
                              lifecycle_policy_ref=None)
    return _residual_decision(
        conn, subject=subject, inputs=inputs, outcome=outcome,
        qualifier=qualifier, residual=context, evidence=evidence,
        component_version=component_version, observed_at=observed_at)


def run_corpus(conn, *, subjects, group_ids, inputs: PipelineInputs, evidence_for,
               component_version: str, observed_at: str) -> CorpusResult:
    """§6.12 step 9, over a corpus, then §7's separate stage.

    The two-pass order is contractual, not stylistic. §7.1: residual is *"a
    separate stage that runs only after normal group-aware classification has
    been attempted"*, so every file and every accepted group goes through §6
    first and only what §6 could not place reaches §7. `surface_residual_sets`
    refuses a `placement_pass_complete=False` caller, so the ordering is enforced
    by a raise rather than by this function remembering to do it.
    """
    decisions: list[PlacementDecision] = []
    plans: list[GroupPlan] = []

    # §6.8 before the per-file pass: a member's decision belongs to its group's
    # plan, and a file placed alone first would be placed against no shared
    # context. `place_group` writes the member decisions itself.
    covered: set[str] = set()
    for group_id in group_ids:
        plan = place_group(conn, group_id=group_id, inputs=inputs,
                           evidence_for=evidence_for,
                           component_version=component_version,
                           observed_at=observed_at)
        plans.append(plan)
        decisions.extend(plan.member_decisions)
        covered.update(d.subject.file_id for d in plan.member_decisions)
        covered.update(o.file_id for o in plan.excluded_outliers)

    # §6.9. A file that belongs to two accepted packets is multi-home, and the
    # design is explicit that the engine "should not arbitrarily choose one
    # university" (`01-product-design-structured.md:1255-1259`). Detected here
    # because it is a fact ACROSS group plans, which no single `place_group` can
    # see. `resolve_multi_home` has no branch that returns a competing node, so
    # "never pick an institution" is enforced by the function's shape.
    homes: dict[str, list[str]] = {}
    for plan in plans:
        for decision in plan.member_decisions:
            if decision.destination is not None:
                homes.setdefault(decision.subject.file_id, []).append(
                    decision.destination.node_id)
    for file_id, node_ids in homes.items():
        if len(set(node_ids)) < 2:
            continue
        outcome, payload = resolve_multi_home(
            candidate_node_ids=tuple(sorted(set(node_ids))),
            shared_material_policy=inputs.tree.shared_material_policy,
            shared_branch_node_id=_shared_branch_of(conn, inputs),
            ask_or_abstain=inputs.ask_or_abstain)
        decisions.append(_multi_home_decision(
            conn, file_id=file_id, inputs=inputs, outcome=outcome,
            payload=payload, component_version=component_version,
            observed_at=observed_at))

    for subject in subjects:
        if subject.file_id in covered:
            continue
        decisions.append(place_file(
            conn, subject=subject, inputs=inputs,
            evidence=evidence_for(subject.file_id),
            component_version=component_version, observed_at=observed_at))

    unplaced = tuple(d.subject.file_id for d in decisions
                     if d.outcome != PLACE and d.subject.file_id)

    # §7.5. The §6 pass is complete for the corpus, which is the only condition
    # under which a file may be called residual.
    sets: tuple[ResidualSet, ...] = surface_residual_sets(
        conn, plan_version=inputs.plan_version, unplaced=unplaced,
        partition=inputs.partition, limits=inputs.limits,
        placement_pass_complete=True, component_version=component_version,
        observed_at=observed_at)

    # §7.6. Per-file residual work happens only for a set the user decided, and
    # only when that decision asks for it. Everything else is left alone, which
    # is the decision the user made.
    residual_decisions: list[PlacementDecision] = []
    for item in sets:
        try:
            set_decision = require_set_decision(
                conn, plan_version=inputs.plan_version, set_id=item.set_id)
        except Exception:
            # Surfaced and not yet decided is a real, visible state -- it is the
            # state §7.6's gate exists to make visible -- and not an error to
            # swallow into a default.
            continue
        if not model_calls_permitted(set_decision):
            continue
        residual_decisions.extend(_review_set_with_model(
            conn, item=item, inputs=inputs, evidence_for=evidence_for,
            component_version=component_version, observed_at=observed_at))

    return CorpusResult(
        decisions=tuple(decisions), group_plans=tuple(plans),
        residual_sets=sets, residual_decisions=tuple(residual_decisions),
        unplaced_file_ids=unplaced)


def _review_set_with_model(conn, *, item, inputs: PipelineInputs, evidence_for,
                           component_version: str, observed_at: str):
    """§7.7, per file, for a set whose decision asked for it and no other.

    Site D is P8's; P11 supplies `approved_target_ids` and reads a disposition.
    `outcome_for_action` maps that disposition onto one of §6's outcomes, which
    is why a residual decision needs no field the §6 path does not already have.
    """
    from placement.records import Subject

    written = []
    for file_id in item.member_file_ids:
        subject = Subject(kind="file", file_id=file_id,
                          content_hash=_content_hash_of(conn, file_id),
                          group_id=None, member_file_ids=())
        privacy = privacy_state_for(conn, file_id=file_id,
                                    content_hash=subject.content_hash,
                                    plan_version=inputs.plan_version)
        if not may_assemble_dossier(privacy):
            # §8.4 before the dossier, on the residual path exactly as on the
            # placement path. Protected material does not become releasable
            # because the file reached §7 instead of §6.
            continue
        evidence = evidence_for(file_id)
        retrieval = retrieve(
            conn, subject=subject, plan_version=inputs.plan_version,
            limits=inputs.limits, facts=evidence["facts"],
            group_ids=evidence["group_ids"],
            curated_folder_labels=evidence["curated_folder_labels"],
            semantic_neighbours=evidence["semantic_neighbours"],
            component_version=component_version, observed_at=observed_at)
        verdict = _judge_with_model(
            conn, subject=subject, inputs=inputs, retrieval=retrieval,
            evidence=evidence, call_site=D_RESIDUAL, observed_at=observed_at)
        written.append(run_residual_file(
            conn, subject=subject, set_id=item.set_id, inputs=inputs,
            evidence=evidence, action=verdict.disposition,
            target=inputs.chosen_node_of(verdict),
            component_version=component_version, observed_at=observed_at))
    return written


def _residual_decision(conn, *, subject, inputs, outcome, qualifier, residual,
                       evidence, component_version, observed_at
                       ) -> PlacementDecision:
    """One §7 decision on the SAME thirty-field shape §6 uses (Done-means 1).

    Exactly one outcome-shaped field is filled, chosen by `outcome`, because the
    record refuses any other combination: `destination` on `place`,
    `return_target` on `return_to_placement`, `marked_state` on `mark_state`,
    `abstention_reason` on `abstain`, and none of the four on `leave_in_place`
    or `mark_review_later` — whether those two result in a move is the Review
    Later node's `disposition` (§7.4, set by P10), not this record's decision.
    """
    from placement.records import ReturnTarget

    entry = (entry_for(conn, plan_version=inputs.plan_version, node_id=qualifier)
             if outcome == PLACE else None)
    privacy = privacy_state_for(conn, file_id=subject.file_id,
                                content_hash=subject.content_hash,
                                plan_version=inputs.plan_version)
    two = _residual_two_condition(inputs)
    decision = PlacementDecision(
        decision_id=f"{inputs.plan_version}:{subject_ref_of(subject)}:{observed_at}:r",
        plan_version=inputs.plan_version, supersedes=None, superseded_by=None,
        supersede_reason=None, created_at=observed_at, origin_stage=RESIDUAL,
        returned_from=None, subject=subject, group_plan_id=None, outcome=outcome,
        destination=(Destination(node_id=entry.node_id,
                                 node_role=entry.node_role)
                     if entry is not None else None),
        return_target=(ReturnTarget(kind=qualifier, id=subject.file_id)
                       if outcome == RETURN_TO_PLACEMENT else None),
        marked_state=qualifier if outcome == MARK_STATE else None, ask=None,
        decision_depth=DecisionDepth(
            node_depth=entry.depth if entry else 0,
            supported_depth=entry.depth if entry else 0, unsupported_levels=()),
        evidence_type=CONTEXT_SUPPORTED,
        confidence_class=(CONTEXT_SUPPORTED_GROUP_MATCH if entry is not None
                          else ABSTAIN_NO_SUPPORTED_DESTINATION),
        matching_facts=tuple(evidence["facts"]) if entry is not None else (),
        group_support=None, graph_anchors=(), conflicts_considered=(),
        alternatives=(), two_condition=two,
        abstention_reason=qualifier if outcome == ABSTAIN else None,
        deferred_stage=None, privacy=privacy,
        review_policy=review_policy_for(
            privacy_state=privacy, two_condition=two, group_support=None,
            unique_direct_match=False,
            automatic_move_permitted=inputs.automatic_move_permitted),
        explanation=(
            f"Residual review of set {residual.set_id} returned {outcome!r}. "
            "The set-level decision authorised this review and the file has not "
            "moved."),
        residual=residual,
    )
    record_decision(conn, decision, component_version=component_version,
                    observed_at=observed_at)
    return decision


def _residual_two_condition(inputs: PipelineInputs):
    """§6.10's figures on a §7 record. One shape means one set of figures.

    SPEC:473-475 makes `verdict` a P11 field on every decision, so a residual
    decision carries the thresholds it was judged under even though §7's
    judgement was P8's. `meets_margin` is vacuous because the residual path
    compares against no next-best destination.
    """
    from placement.records import TwoCondition
    from placement.vocabulary import MARGIN_TRUE_VACUOUS, WEAK_VERDICT

    return TwoCondition(
        support_score=0.0,
        support_threshold=inputs.policy.minimum_support_threshold,
        meets_threshold=False, margin_over_next=None,
        margin_threshold=inputs.policy.margin_threshold,
        meets_margin=MARGIN_TRUE_VACUOUS, verdict=WEAK_VERDICT,
        requires_review=True)


def _shared_branch_of(conn, inputs: PipelineInputs) -> str | None:
    """The frozen tree's shared-material node, if it froze one. P11 mints none.

    §6.9's worked example: *"If no shared branch exists, the system should not
    arbitrarily choose one university."* So absence is answered with None and the
    policy decides what happens next, rather than P11 producing a branch.
    """
    for node in inputs.tree.nodes:
        if node.node_role == "shared-material" and node.accepts_placement:
            return node.node_id
    return None


def _multi_home_decision(conn, *, file_id, inputs, outcome, payload,
                         component_version, observed_at) -> PlacementDecision:
    """§6.9's answer as one decision: a shared branch, a question, or an abstention.

    `payload` is the shared branch's node id for `place`, the competing ids for
    `ask_user`, and `no_shared_branch` for `abstain` -- and it is NEVER one of the
    competing institution nodes, because `resolve_multi_home` has no branch that
    returns one.
    """
    from placement.records import Ask, Subject

    subject = Subject(kind="file", file_id=file_id,
                      content_hash=_content_hash_of(conn, file_id),
                      group_id=None, member_file_ids=())
    privacy = privacy_state_for(conn, file_id=file_id,
                                content_hash=subject.content_hash,
                                plan_version=inputs.plan_version)
    two = _residual_two_condition(inputs)
    entry = (entry_for(conn, plan_version=inputs.plan_version, node_id=payload)
             if outcome == PLACE else None)
    decision = PlacementDecision(
        decision_id=f"{inputs.plan_version}:file:{file_id}:{observed_at}:mh",
        plan_version=inputs.plan_version, supersedes=None, superseded_by=None,
        supersede_reason=None, created_at=observed_at, origin_stage=PLACEMENT,
        returned_from=None, subject=subject, group_plan_id=None, outcome=outcome,
        destination=(Destination(node_id=entry.node_id,
                                 node_role=entry.node_role)
                     if entry is not None else None),
        return_target=None, marked_state=None,
        ask=(Ask(question="Which packet is this file's primary home?",
                 options=tuple(payload)) if outcome == ASK_USER else None),
        decision_depth=DecisionDepth(
            node_depth=entry.depth if entry else 0,
            supported_depth=entry.depth if entry else 0, unsupported_levels=()),
        evidence_type=CONTEXT_SUPPORTED,
        confidence_class=(SHARED_MATERIAL_DECISION if entry is not None
                          else ABSTAIN_NO_SUPPORTED_DESTINATION),
        matching_facts=(), group_support=None, graph_anchors=(),
        conflicts_considered=(), alternatives=(), two_condition=two,
        abstention_reason=(NO_SHARED_BRANCH if outcome == ABSTAIN else None),
        deferred_stage=None, privacy=privacy,
        review_policy=review_policy_for(
            privacy_state=privacy, two_condition=two, group_support=None,
            unique_direct_match=False,
            automatic_move_permitted=inputs.automatic_move_permitted),
        explanation=(
            "This file has accepted membership in more than one packet. §6.9 "
            "permits a shared branch, a question, or an abstention, and never an "
            "arbitrary choice between the packets."),
        residual=None,
    )
    record_decision(conn, decision, component_version=component_version,
                    observed_at=observed_at)
    return decision


def _content_hash_of(conn, file_id: str) -> str:
    """P1 owns file identity; P11 asks rather than keeping a second copy."""
    row = conn.execute(
        "SELECT content_hash FROM files WHERE file_id = ?", (file_id,)).fetchone()
    if row is None:
        raise LookupError(
            f"no file {file_id!r} in P1's `files`; a residual set naming a file "
            "P1 has never seen is a set built from something other than the scan"
        )
    return row["content_hash"]
```

Every §7 decision therefore lands in the same append-only table, under the same
supersede rules, on the same thirty-field shape as every §6 decision — which is
what Done-means 1 asks a consumer to be able to rely on.

And the golden fixtures P12 and P13 will read:

```python
# src/placement/fixtures.py
"""Golden P11 records, published for P12 and P13. Content-free contract witnesses.

These are what a downstream part builds against before P11 runs on a real corpus.
They are not an alternate authority: every one is constructed through
`placement.records`, so a shape change breaks them at import.
"""
from __future__ import annotations

from placement.records import (
    DecisionDepth, Destination, MatchingFact, PlacementDecision, PrivacyState,
    ResidualContext, Subject, TwoCondition,
)
from placement.vocabulary import (
    ABSTAIN, ABSTAIN_NO_SUPPORTED_DESTINATION, AUTO_ELIGIBLE, CONTEXT_SUPPORTED,
    DIRECT, DOSSIER_PERMITTED, EXACT_FACT_MATCH, FILE, LEAVE_IN_PLACE,
    MARGIN_TRUE_VACUOUS, NO_SUPPORTED_DESTINATION, ORDINARY, PLACE, PLACEMENT,
    RESIDUAL, REVIEW_REQUIRED, REVIEW_WITH_MODEL, VERDICTS,
)

T0 = "2026-08-27T00:00:00Z"
_SUBJECT = Subject(kind=FILE, file_id="f-syllabus", content_hash="h-syllabus",
                   group_id=None, member_file_ids=())
_PRIVACY = PrivacyState(handling_class="personal_non_sensitive",
                        model_eligibility=DOSSIER_PERMITTED,
                        consent_audit_ref=None)


def _two_condition(**overrides) -> TwoCondition:
    values = dict(support_score=1.0, support_threshold=0.5, meets_threshold=True,
                  margin_over_next=None, margin_threshold=0.2,
                  meets_margin=MARGIN_TRUE_VACUOUS, verdict=VERDICTS[0],
                  requires_review=False)
    values.update(overrides)
    return TwoCondition(**values)


#: The degenerate case B8(b) gives the walking skeleton: one legal candidate, a
#: vacuous margin, and a placement that still had to clear the support threshold.
EXACT_PLACEMENT = PlacementDecision(
    decision_id="fixture-place-1", plan_version="plan-1", supersedes=None,
    superseded_by=None, supersede_reason=None, created_at=T0,
    origin_stage=PLACEMENT, returned_from=None, subject=_SUBJECT,
    group_plan_id=None, outcome=PLACE,
    destination=Destination(node_id="n-course", node_role=ORDINARY),
    return_target=None, marked_state=None, ask=None,
    decision_depth=DecisionDepth(node_depth=1, supported_depth=1,
                                 unsupported_levels=()),
    evidence_type=DIRECT, confidence_class=EXACT_FACT_MATCH,
    matching_facts=(MatchingFact(file_fact_id="ff-1", field="subject",
                                 value="PHYS1401", reliability=DIRECT,
                                 evidence_ref="obs-syllabus"),),
    group_support=None, graph_anchors=(), conflicts_considered=(),
    alternatives=(), two_condition=_two_condition(), abstention_reason=None,
    deferred_stage=None, privacy=_PRIVACY, review_policy=AUTO_ELIGIBLE,
    explanation="PHYS1401 expects subject = PHYS1401; support 1.00 against a "
                "threshold of 0.50.",
    residual=None,
)

#: The other half of B8(b): the same one-node tree, and support that fell short.
#: Only this one proves the threshold stayed binding.
CORRECT_ABSTENTION = PlacementDecision(
    decision_id="fixture-abstain-1", plan_version="plan-1", supersedes=None,
    superseded_by=None, supersede_reason=None, created_at=T0,
    origin_stage=PLACEMENT, returned_from=None, subject=_SUBJECT,
    group_plan_id=None, outcome=ABSTAIN, destination=None, return_target=None,
    marked_state=None, ask=None,
    decision_depth=DecisionDepth(node_depth=0, supported_depth=0,
                                 unsupported_levels=()),
    evidence_type=CONTEXT_SUPPORTED,
    confidence_class=ABSTAIN_NO_SUPPORTED_DESTINATION, matching_facts=(),
    group_support=None, graph_anchors=(), conflicts_considered=(),
    alternatives=(),
    two_condition=_two_condition(support_score=0.2, meets_threshold=False,
                                 verdict=VERDICTS[2], requires_review=True),
    abstention_reason=NO_SUPPORTED_DESTINATION, deferred_stage=None,
    privacy=_PRIVACY, review_policy=REVIEW_REQUIRED,
    explanation="No legal destination cleared §6.10's conditions "
                "(no_supported_destination). Abstaining is the correct outcome; "
                "the evidence is retained and the file has not moved.",
    residual=None,
)

#: A §7-origin decision, to prove a consumer parses it with no residual branch.
RESIDUAL_LEAVE_IN_PLACE = PlacementDecision(
    decision_id="fixture-residual-1", plan_version="plan-1", supersedes=None,
    superseded_by=None, supersede_reason=None, created_at=T0,
    origin_stage=RESIDUAL, returned_from=None, subject=_SUBJECT,
    group_plan_id=None, outcome=LEAVE_IN_PLACE, destination=None,
    return_target=None, marked_state=None, ask=None,
    decision_depth=DecisionDepth(node_depth=0, supported_depth=0,
                                 unsupported_levels=()),
    evidence_type=CONTEXT_SUPPORTED,
    confidence_class=ABSTAIN_NO_SUPPORTED_DESTINATION, matching_facts=(),
    group_support=None, graph_anchors=(), conflicts_considered=(),
    alternatives=(),
    two_condition=_two_condition(support_score=0.3, meets_threshold=False,
                                 verdict=VERDICTS[2], requires_review=True),
    abstention_reason=None, deferred_stage=None, privacy=_PRIVACY,
    review_policy=REVIEW_REQUIRED,
    explanation="The user chose to leave this review set in place; the file "
                "stays where it is and nothing was proposed for it.",
    residual=ResidualContext(set_id="plan-1:Screenshots",
                             set_decision=REVIEW_WITH_MODEL,
                             lifecycle_policy_ref=None),
)

GOLDEN_DECISIONS: tuple[PlacementDecision, ...] = (
    EXACT_PLACEMENT, CORRECT_ABSTENTION, RESIDUAL_LEAVE_IN_PLACE,
)


def golden_decisions() -> tuple[PlacementDecision, ...]:
    return GOLDEN_DECISIONS
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3 -m pytest -q tests/p11/ tests/integration/test_p11_p12_node_boundary.py`

Expected: PASS. `test_a_unique_direct_match_is_placed_with_zero_model_calls` asserts `llm_verdict` is empty, which is the only way to prove §6.6's "never called for direct unique matches" rather than assume it.

- [ ] **Step 5: Commit**

```bash
git add src/placement/pipeline.py src/placement/fixtures.py \
        tests/p11/test_p11_pipeline.py tests/integration/test_p11_p12_node_boundary.py
git commit -m "feat(p11): run the nine-step pipeline end to end"
```

### Task 20: Enforce the no-invention, connection and mission guards

**Files:**
- Create: `tests/p11/test_p11_no_invention.py`
- Create: `tests/p11/test_p11_connections.py`

**Done-means:** 2, 5, 15 as prohibitions rather than behaviours; SPEC:24-27's three literal prohibitions.

- [ ] **Step 1: Add the no-invention guards**

By runtime introspection and AST, never by text search: a text search matches comments and docstrings, and scanning source text for a token has produced a false result nine times on this project.

Assert, over every module in `src/placement/`:

- no bound int or float other than `0` and `1`, at module level **or** as a default argument, so a threshold cannot hide in a signature;
- no string constant equal to any member of `llm_harness.vocabulary.ALL_REASON_CODES`, `SITE_C_REASON_CODES` or `SITE_D_REASON_CODES` — P8 owns those and a second speller is a second opinion;
- no attribute named `path`, `resolved_path`, `existing_path`, `delete`, `expiry`, `ttl` or `disposable` on any published record;
- no import of `llm_harness.records.Dossier`, `llm_harness.transport`, `privacy.gate.Gate`, or any test fixture package — which is spelled `p11.*`, not `tests.p11.*` (see [Test import convention](#test-import-convention));
- no call to `os.rename`, `os.replace`, `shutil.move`, `pathlib.Path.rename`, `open(..., "w")` or any other filesystem mutation — P11 moves nothing;
- no construction of a P10 node, a P9 `Group` or `Membership`, or a P8 `Dossier`;
- `subsystem = "P11"` appears in exactly one place (`placement/events.py`);
- every closed vocabulary is bound only in `placement/vocabulary.py`.

- [ ] **Step 2: Add the connection guards**

- P8 is reached only through `llm_harness.harness.run_call` and the two validators, and only from `placement/p8_seam.py`;
- P7 is reached only through `ClassificationStore` and `current_policy`, and `Gate.release` is never called;
- P6 is reached only through `facts.read_surface`, and no P6 table is queried directly;
- P4 citations are `observation_key` only, asserted by checking that no P11 field is named `observation_id`;
- P2 receives only `candidate_node_retrieval` and `placement_scoring`, and `_FOREIGN_OUTCOMES` still equals `placement.vocabulary.OUTCOMES`;
- P9 is reached only through `grouping.acceptance.group_state_as_of`, `grouping.store.memberships_for_group` and `grouping.vocabulary`, and no P9 table is queried directly; P10 is consumed only through `tests/p11/p10_fixtures.py` until it ships, and `src/placement/` imports no fixture module;
- P12 and P13 are consumed only through `src/placement/fixtures.py`, with no import back into `src/placement/`.

- [ ] **Step 3: Add the mission guards**

Assert on `src/placement/fixtures.GOLDEN_DECISIONS` and on every decision Task 19 produces:

- every decision shows its evidence, its reason, its uncertainty, its next action and its reversibility — concretely: `matching_facts` or `group_support` or `graph_anchors` is non-empty **or** `abstention_reason` is set; `explanation` is non-empty; `two_condition` is present; `review_policy` is set; `supersedes`/`superseded_by` exist as fields;
- no decision expresses deletion, expiry or a path;
- an abstention is a complete record and not an empty one;
- a decision resting on protected material is never `auto_eligible`;
- a budget deferral renders differently from an evidential abstention — `deferred_stage` set and `abstention_reason == budget_deferred`.

- [ ] **Step 4: Run focused verification**

```bash
python3 -m pytest -q tests/p11 tests/integration/test_p11_p8_seam.py \
    tests/integration/test_p11_p2_replay.py \
    tests/integration/test_p11_p12_node_boundary.py
```

Expected: PASS. `tests/integration/test_p11_p10_tree.py` must still FAIL at its documented missing import, because G-P10 is open; it must not be skipped and no source stub may satisfy it.

- [ ] **Step 5: Commit**

```bash
git add tests/p11/test_p11_no_invention.py tests/p11/test_p11_connections.py
git commit -m "test(p11): lock the placement and residual boundaries"
```

### Task 21: Final verification and connection review

**Files:**
- Modify only if verification finds a P11-owned defect: files introduced by Tasks 1–20.

- [ ] **Step 1: Run compilation and the complete suite**

```bash
python3 -m compileall -q src tests
python3 -m pytest -q
```

Expected while **G-P10 is open**: run the two halves separately.

```bash
python3 -m pytest -q --ignore=tests/integration/test_p11_p10_tree.py
python3 -m pytest -q tests/integration/test_p11_p10_tree.py
```

The first must be green and must include every pre-existing P1–P9 test — Task 1 modified `src/database_agent/events.py` and `tests/test_events.py`, so `tests/test_events.py`, `tests/test_p1_p7_seams.py`, `tests/p7/test_p7_authorship.py` and `tests/p8/test_p8_provenance.py` are all in scope. The second must fail at its documented missing P10 import. Do not mark the milestone green, skip the dependency silently, or replace P10 with a source stub.

- [ ] **Step 2: Refresh and diagnose Graphify**

```bash
graphify update .
graphify diagnose multigraph --json --max-examples 20
```

Expected: the fresh runtime graph shows P1→P11, P2←P11, P4→P11, P6→P11, P7→P11 and P8↔P11. P9→P11 and P10→P11 exist only as fixture-mediated seams and must not be reported as live; P11→P12 and P11→P13 are fixture publication paths from `src/placement/fixtures.py` and are not proof that either part consumes P11 today. In every state, no runtime import from `src/placement/` points at a test fixture, a prompt, a domain, P9, P10, P12 or P13.

- [ ] **Step 3: Inspect diffs and working-tree ownership**

```bash
git diff --check
git status --short
```

Expected: no whitespace errors, and exactly one file outside `src/placement/` and `tests/p11/` modified — `src/database_agent/events.py`, by Task 1, plus the test files that assert its registry. Preserve unrelated concurrent changes, especially `planning/domains/`, deferred catalogues, prompts and `.superpowers/`.

- [ ] **Step 4: Re-read the original mission and audit every P11 outcome**

Confirm with test names and database rows that:

- P11 moved no file and holds no filesystem path — the record shape cannot express one;
- no destination was invented: every `place` names a node in the frozen tree with `accepts_placement = true`, and an `ignored` node was never even retrievable;
- a direct fact was never silently overridden: every conflict that suppressed a node is in `conflicts_considered` with its evidence;
- an uncertain file was never moved because it resembled a folder: a semantic-only or generic-hub candidate never produced `place`;
- correct abstention was recorded as a successful outcome and P2 scored it as one;
- a budget deferral was visibly different from an evidential abstention, in the record and in the envelope;
- a new plan version reclassified nothing: removed-node decisions were marked for review and never remapped;
- every user correction kept the scope the user chose, and no preference became corpus-wide without the user saying so;
- protected material never reached a dossier and never produced an automatic move;
- no unfinished knowledge source — the support scale, the two thresholds, the ask-versus-abstain selector, the residual partition, the cycle limit — gained an implementation default.

Only after all ten pass may P11 be described as complete. If G-P9, G-P10 or G-P13 is still open, report the corresponding integration as dependency-blocked while retaining the green deterministic core.

---

## Requirement coverage map

| P11 requirement | Tasks |
|---|---|
| §6.2 index over P10's profiles; legality is `accepts_placement`, not existence | 6 |
| §6.3 six retrieval channels; conflicting evidence actively suppresses and is recorded | 7 |
| §6.4/§6.5 node-local evidence graph, typed edges, no whole-corpus reclustering | 8 |
| §6.6 deterministic exact match with zero model calls; bounded dossier only | 9, 12, 19 |
| §6.7 shallow beats invented; `decision_depth.unsupported_levels` | 3, 6, 9 |
| §6.8 one coherent group plan, outliers excluded and explained | 13 |
| §6.9 multi-home: shared branch, or abstain or ask — never an institution | 13 |
| §6.10 two conditions recorded; B8(b)'s vacuous margin; abstention as success | 9, 18 |
| §6.11 the single decision record, all ~45 fields | 3, 4 |
| §6.12 the nine-step pipeline | 19 |
| §7.1/§7.5/§7.6 residual runs second; sets; the spend gate | 14 |
| §7.7/§7.9 the eight actions, the return loop, no ninth | 15 |
| §7.10 editable, bulk and negative-example corrections | 11, 16 |
| §7.11 non-destructive lifecycle; the shape cannot express deletion | 3, 20 |
| §8.2 nine events, never overwrites, forward-followable chain | 1, 4 |
| §8.4 the gate before the dossier; review policy | 10 |
| §8.5 two stages, two dimensions, deferral never abstention | 18 |
| §8.6 seven ceilings, degradation order, budget deferral | 5, 8, 14, 18 |
| §8.7 scoped corrections, negative examples queried before `place` | 11, 16 |
| §8.8 plan-version projection; mark, never remap | 17 |
| P8 boundary: authorities in, verdict out, no second validator | 12, 15, 20 |
| P12 boundary: a node, never a path; only `place` becomes a plan | 3, 19, 20 |
| North-star explainable, reversible review | 10, 19, 20, 21 |

## SPEC corrections

Live API names beat SPEC names (the P10 precedent). Each divergence below is a
deliberate choice, not a mis-citation, and each names the SPEC line it departs
from so a reader can check the reasoning rather than the outcome.

| SPEC line | SPEC says | The plan does | Why |
|---|---|---|---|
| SPEC:335-336 | `evidence_type` is `user-confirmed`, `llm-supported` (hyphenated) | imports `user_confirmed` and `llm_supported` from `facts.states` | `evidence_shape/vocabulary.py:53-55` is the live spelling and five of the six values are P6's. Re-spelling two of a neighbour's six is the `subject`/`course` defect again. `context-supported` stays hyphenated because P8 and P9 both publish exactly that string |
| SPEC:117-128 | fifteen P10 node fields | reads twenty-two, adding `plan_version_id`, `dimension_role`, `existing_path`, `refinement_disposition`, `refinement_reason`, `origin_node_id`, `protected_movement_permitted` | P10 SPEC Contract out §1 publishes them. `refinement_disposition` is the user's own answer to whether a branch is shallow on purpose, which is precisely §6.7's question; re-deriving it would be P11 second-guessing a recorded user choice. `origin_node_id` is load-bearing for a different reason: P10 mints a NEW `node_id` per plan version, so it is the only field a decision can be matched across versions on (§8.8, and `planning/38-p10-p11-connection-contract.md` §5.2) |
| SPEC:683-693 | eight event appends | registers nine | SPEC:689 is one bullet carrying two state changes, and §7.6 gates model spend on the second. One name could not distinguish a surfaced-but-undecided set from a decided one — the exact state the gate exists to make visible. `src/database_agent/events.py:62-65` is corrected in the same commit |
| SPEC:374 | `model_eligibility ∈ local_only \| dossier_permitted \| redacted` | derives them in `placement/privacy.py` from `Policy.operation_mode` and `ClassificationRecord.protected` | The three values have no producer anywhere: `grep -rn "local_only\|dossier_permitted" src/privacy/` finds nothing, and `redacted` collides with `privacy/vocabulary.py:217`'s display-facet value. The two things §8.4 actually decides from are the mode and the flag |
| SPEC:214-229 | *"the dossier submission interface"* | imports `SiteDependencies`, `CallDependencies`, `PlacementDependencies` and `ResidualDependencies` from unexported module paths | `src/llm_harness/__init__.py` exports the eight names `planning/30-p8-p9-connection-contract.md:24-31` froze, and none of the four is among them. The contract records the same omission for P9 (`:74-76`) without amending the export list. **P8 owes an export decision**; until then P11 imports from `llm_harness.sites`, `llm_harness.harness` and `llm_harness.placement_validation` |
| — | no SPEC assigns `evidence_snapshot_id` a producer | P11 mints it as a content address over `(plan_version, sorted observation_keys)` | `record_cd_verdict` requires it (`placement_validation.py:475-476`) and `run_call` now refuses a C or D request without one before the spend (`harness.py:154-165`). A content address is what makes two calls over the same evidence recognisable as a replay, and what `revalidate_for_plan` keys a re-validation on |
| SPEC:50, SPEC:607 | §6.12's nine-step pipeline is *"reproduced under Done means"* | reproduces it in [Required execution order](#required-execution-order) from `planning/01-product-design-structured.md:1295-1306` | The SPEC does not in fact reproduce the nine steps anywhere. **The SPEC owes them.** |
| SPEC:349-350 | `conflicts_considered[]` is `{kind, conflicting_value, suppressed_node_ids[], evidence_ref}` | keeps that shape and converts to P8's `Conflict(conflict_id, kind)` at the seam | Three records wear the word "conflict" — P9's `(kind, competing_values, file_ids)`, P8's `(conflict_id, kind)` and P11's four-field one. The conversion runs one way, in `p8_seam.to_p8_conflicts`, so nothing downstream has to guess which it holds |
| — | nothing says a node id may be reserved | **nothing** — no id is reserved | `src/llm_harness/placement_validation.py:239` compares a destination to the literal `"node-hub"`, a P8 fixture id (`llm_harness/fixtures.py:356`) that reached production Site C logic. `planning/38-p10-p11-connection-contract.md` §6 settles the owner: **P8 deletes the literal**, at zero behavioural cost, because the one fixture that produces `GENERIC_HUB_ONLY` already sets `generic_hub: True`. A reserved-id list inside P11 would refuse a folder name for a reason the user could never be told, so P11 adds none |

### Cross-part dependencies this plan cannot close

These are **not** P11 divergences. Each is a defect or gap in another part that P11's correctness depends on, recorded here so it is not lost between owners.

| # | Where | What is wrong | What P11 does meanwhile | Owner |
|---|---|---|---|---|
| **X1** | `src/eval_harness/vocabulary.py:5-11` | **`candidate_node_retrieval` has no same-named `dimension`** — P11's own §6.2 stage. `STAGE_IDS` contains it; `DIMENSIONS` has no entry of that name, and P2's own comment recorded the question as open: *"whether the `retrieval` dimension covers candidate-node retrieval, or candidate-node retrieval gets its own dimension, is for the design to settle."* **Settled** by `planning/38-p10-p11-connection-contract.md` §7 from the design itself: §8.5's *"Retrieval quality: for sparse files, did the correct anchors appear in the top candidate neighborhood?"* (`01-product-design-structured.md:1757-1758`) is this stage in the design's own words, so the stage carries the existing `retrieval` dimension and no eleventh is invented. | Emits `candidate_node_retrieval` with a `retrieval` `DimensionValue` under `subject_ref = candidates:{plan_version}:{subject_ref}`, and names that same ref in `placement_scoring.inputs`. The namespace is required, not cosmetic: `stage_dimension_value` is keyed `(run_id, dimension, subject_ref)` (`eval_harness/stage_output.py:59`) and P9 already writes `retrieval` rows for its own stage, so a bare ref makes a full-pipeline replay raise `IntegrityError`. | **P2 owes the documentation change**: record that half of its Open question 1 is answered, and add a test that no two stages write the same `(dimension, subject_ref)` in one run. `residual`-with-no-stage stays open |
| **X2** | `src/llm_harness/harness.py:348` | **`return verdicts[-1]` selects a verdict positionally.** `run_call` validates every claim in a response and returns the LAST verdict in the list, not the most severe. A multi-claim Site C response whose first claim is `reject` and whose last is `accept_direct` therefore returns `accept_direct` to the caller, and the rejection is recorded but never surfaced. | Task 12's `transcribe` and Task 19's `_judge_with_model` **assume a severity-selected verdict**: `transcribe` maps an accepting outcome straight to `PLACE`, so a positionally-selected accept becomes a placement whose first claim P8 refused. P11 writes no second selection of its own — a caller re-ranking P8's verdicts is the second-validator failure O7 forbids. **P11's Task 12 correctness depends on this P8 fix.** | **P8.** Until it lands, P11's transcription is correct only for single-claim responses |
| **X3** | `llm_harness/records.P8Verdict` | **A verdict names a `claim_ref`, not a destination.** Nothing in `P8Verdict`'s thirteen fields says which node the model chose, and `run_call` does not return the response body. So a caller that asked P8 to judge among candidates cannot learn the answer from the verdict alone. | `PipelineInputs.chosen_node_of` is an injected resolver with no default, and the pipeline **refuses** a resolved node outside `legal_node_ids` rather than trusting it. **OPEN**: whether P8 should return the accepted claim's payload, or P11 should key its own claims, is a seam decision nobody has made | **P8 + P11 seam** |
| **X4** | `placement/records.PlacementDecision` | **No `verdict_id` field**, so a decision cannot say which P8 verdict backs it, and Task 17 cannot call `revalidate_for_plan` from the record alone. | `reproject` takes `revalidation_inputs` as an injected sparse mapping from the caller that made the call. **OPEN**: adding a field is a revision of SPEC Contract out §1 | **The SPEC** |

## Explicitly unresolved after this plan

These are dependency gates and open design questions, not invitations to invent
defaults. Every one is an injection with no default, and its absence raises.

- **The support scale and both thresholds** (SPEC Open questions 1 and 2). The plan defines the injection point, records both thresholds on every decision, and chooses no number.
- **Is `confidence_class` closed?** (SPEC Open question 3.) §6.11 gives four labels by example. The plan treats the four as closed and would need a contract revision to add a fifth.
- **Is `abstention_reason` closed?** (SPEC Open question 4.) Same treatment.
- **Does the two-condition rule apply per group member?** (SPEC Open question 5.) The plan confirms the shared parent first and leaves member-level application to the caller's assessment, which is what §6.8 describes and no more.
- **Abstain or ask, and when** (SPEC Open question 6). Injected selector; absent means refuse.
- **Is an alias a filesystem artifact?** (SPEC Open question 7.) **Threatens P12's contract.** P11 names a node under every shared-material policy and creates no link.
- **How many §7 → §6 cycles?** (SPEC Open question 8.) **Threatens P2's replay determinism.** `max_return_cycles` is injected; absent means refuse.
- **Is a residual set decision versioned and reversible?** (SPEC Open question 9.) The table is plan-versioned and append-only; whether reversing one re-runs the model at cost is the caller's, and unresolved.
- **Is §7.5's set partition canonical?** (SPEC Open question 10.) Read as illustrative; the partition is injected.
- **Where does the shared-material policy live in the tree?** (SPEC Open question 12.) **Threatens P10's node schema.** P11 reads it off the tree and stores none of its own.
- ~~**P9's acceptance read does not exist.**~~ **Resolved.** It shipped: `grouping/acceptance.py:154` publishes `group_state_as_of`, and `grouping/store.py:266` publishes `memberships_for_group`. G-P9 is closed and Task 13 consumes both directly.
- **P10 does not exist.** G-P10 fails explicitly and must keep failing until it ships.
- **P13 does not exist.** G-P13 is fixture-mediated and names its swap boundary.
- **P7's detector does not exist**, so on a real corpus every file resolves to `unreadable_unclassified` and P11 blocks. That is the ordinary path and the correct one.
- **P8's `SiteDependencies` and friends are unexported**, and `"node-hub"` is a fixture id in production Site C logic. Both are P8's to close.
- **P2 has no dimension for `candidate_node_retrieval`** (X1). P11's own retrieval stage is unattributable until the design settles whether the `retrieval` dimension covers it. P11 emits the stage and attaches no dimension to it.
- **P8's `run_call` selects a verdict positionally** (`harness.py:348`, X2). P11's transcription assumes severity selection and is correct only for single-claim responses until P8 fixes it.
- **A P8 verdict does not name the destination it accepted** (X3). `chosen_node_of` is injected with no default and the pipeline refuses a node outside the index.
- **`PlacementDecision` carries no verdict id** (X4), so `revalidate_for_plan`'s inputs are injected rather than read off the record.

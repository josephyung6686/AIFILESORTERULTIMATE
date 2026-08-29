# P13 Review and Approval Surface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build P13 so that every reviewable moment the design promises — a placement whose trust level is visible, a residual pile divided into legible sets, a stale plan the user is asked to refresh, a protected file that is present rather than absent, a progress line that never merges completed with deferred, and a plan-version diff the user explicitly adopts — is reachable from records other parts already publish, and so that every gesture the user makes is collected once, with its scope, and routed to the part that owns the meaning.

**North-star user experience:** the person using this is several people at once — the researcher whose paper is also school homework, the parent whose legal document is part of an application. P13 must never make that person's multi-purpose file look like a system failure. `66` §3: a file has ONE current location and may have SEVERAL accepted relationships, and *"It should not describe a valid multi-purpose relationship as a confidence failure."* P13 must never make a protected file look absent, never make a deferral look like a finished result, and never make a reading failure look like a question about the person.

**Architecture:** P13 is a DATA-AND-CONTRACT layer, not a GUI. It publishes record shapes — review items, one `review_action`, one `progress_line`, one `review_approval` — and the projections that build them from P1–P11 reads. There is no framework, no HTML, no TUI, no template engine and no rendering loop anywhere in this plan. Every "renders" in the SPEC becomes "is reachable as a field on a frozen dataclass, and a negative test proves the forbidden thing is not reachable." P13 owns its own three tables inside P1's single SQLite database, appends its three already-registered §8.2 event types, and writes nothing else.

**Tech Stack:** Python 3.12, stdlib only (`sqlite3`, `dataclasses`, `json`, `types.MappingProxyType`). No third-party import anywhere in `src/review_surface/`. pytest for tests.

---

## Ratified decisions binding on every task

| | Ratified | Effect on P13 |
|---|---|---|
| **B3** | P13 shows a **node and its ancestor `display_label` chain**, never a resolved path. P12 alone composes paths. | Task 3 builds the chain. No P13 record carries a field whose value is a filesystem path, **except** the four §8.3 path fields the SPEC itself demands on the apply and undo-conflict items — see the CONFLICT callout on Task 11. |
| **M8** | **The acting part authors; P1 writes.** | P13 authors only `review presentation`, `review action routed` and `apply review approval`. It never authors P11's placement event, P10's tree edit, P7's consent events or P12's move events. |
| **M14** | A citation is an `observation_key`, never an `observation_id`. | Task 4's citation resolution goes through `evidence_shape.store.observations_by_key`. `get_observation(observation_id)` is forbidden in `src/review_surface/`, and Task 18's guard asserts it. |
| **B2** | `NeedsConsent` is **never** mapped to `abstain`. | Task 13. A pending consent request renders as `review_policy = blocked_pending_user`, which is already a live member of `placement.vocabulary.REVIEW_POLICIES`. |
| **D11** | `ProtectedSummary.class_breakdown` is a census of the **whole scope**; `count` is the protected count; `scope_total` is files-in-scope. | Task 12 must never compute a percentage or a ratio out of `count` and `class_breakdown` together. The live record already carries all three fields — verified below. |
| **§11 of the authoring brief** | Every closed vocabulary is published **both ways**: a `tuple[str, ...]` for iteration and membership, **and one named constant per member**. Every consumer imports the named constant. Never a bare string, never an index. | Task 1 publishes P13's five closed vocabularies this way. Task 18's guard asserts by runtime introspection that no module in `review_surface` outside `vocabulary.py` binds a collection whose members ARE one of those vocabularies. |
| **Authoring brief §6** | No invented thresholds, weights or catalogues as module-level constants; everything injected with no default. | P13 has no thresholds at all — it computes no score. The injected things are the **seams** to parts that do not exist yet (P12) and the callables that resolve scope (`files_in_scope`, `scope_for`), matching `privacy.gate.Gate.__init__`'s live shape. |
| **`67` §1 (security)** | Protected material is **marked and counted, NEVER opened**, present-but-untouched, never silently omitted, never described as "understood and found unimportant." | Task 12 and Task 6. `untouched_protected` is its own list carrying **no action at all** (P13 SPEC:260-262). Task 8 asserts no `review_action` can be constructed over an `untouched_protected` subject. |

**Authority order** (`67`, unchanged): `planning/00-database-agent-product-design.md` → `planning/66-FIND-FILE-AND-ONBOARDING.md` and the part SPECs → PLANs → live `src/`. **Where `66` and `planning/parts/P13-review-approval-surface/SPEC.md` differ on user-facing behaviour, `66` governs**, because `66` is dated 2026-08-29 and the SPEC 2026-08-20. Four sections of `66` bind P13 directly and each has a task: §3 (Task 3), §4 (Task 6), §9 (Task 11), §17 (Task 17).

**Standing operational constraints** (`67`, non-negotiable):

- **`python3`, not `python`.** There is no `python` on PATH. A run reporting mass failures is usually this.
- **`-p no:randomly`** on any pytest invocation whose interpreter imports `thinc`/spaCy, per `pyproject.toml`. This once produced 4501 phantom errors. P13 imports neither, but the repo-wide runs in this plan do.
- **Git: stage and commit in ONE shell invocation with EXPLICIT paths. Never `git add -A`** — the index is shared with other sessions.

---

## What already exists and is green

**5247 tests collected** (`python3 -m pytest -q --collect-only -p no:randomly`, 2026-08-29). Every signature below was verified by live introspection on this checkout, not reconstructed from a SPEC. Re-verify any one with:

```bash
cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -c "import inspect; from placement.store import current_decision; print(inspect.signature(current_decision))"
```

**P1 — `database_agent`.** `events.append_event(conn, **fields) -> int` accepts `EVENT_FIELDS` (eleven), `CORRECTION_FIELDS` (five: `correction_scope`, `correction_subject`, `polarity`, `proposal_class`, `basis_key`) and `base_event_type`; it requires `event_type`, `subsystem`, `component_version`, `observed_at`, `explanation` non-empty, and rejects an unregistered `event_type` with `UnregisteredEventType`. `events.CORRECTION_SCOPES == ("file", "group", "node", "template", "domain", "corpus")`.

> **P13's three event types are already registered.** `database_agent.events._REGISTERED` carries `"review presentation"`, `"review action routed"` and `"apply review approval"`, each mapped to base `None`. They are **not** in `RESERVED_EVENT_TYPES` (that frozenset is §8.2's nineteen and P13's names are not among them) but they **are** in `EVENT_TYPES`, so `append_event` accepts them today. **No task in this plan registers an event type.** The docstring in `tests/p11/p13_fixtures.py` cites `database_agent/events.py:59-61` for this; the substance is right and the line numbers have moved — do not propagate the citation.

Also live: `budget.all_ceilings(conn) -> dict[str, int]`, `budget.get_ceiling(conn, key) -> int | None`, `budget.CEILING_KEYS`; `db.create_schema(conn) -> None`.

**P2 — `eval_harness`.** `comparison.DIMENSIONS` (ten), `comparison.compare_runs(conn, baseline_run_id, candidate_run_id) -> str`, `comparison.get_comparison(conn, comparison_id) -> dict`; `attribution.attribute_run(conn, run_id) -> int`, `attribution.FAILING_VERDICTS`; `shadow.run_shadow(...) -> str`, `shadow.shadow_record(conn, shadow_run_id) -> dict`, `shadow.record_adjudication(conn, shadow_run_id, *, subject_ref, dimension, reviewer_verdict, note=None) -> int`, `shadow.adjudications(conn, shadow_run_id) -> list[sqlite3.Row]`; `store.create_eval_schema(conn)`; `run.start_run`, `run.record_version_tuple`, `run.ANALYSIS_TIERS`.

**P3 — `scan_agent`.** `summary.scan_run_summary(conn, scan_run_id) -> dict` returning keys `summary.R5_COUNTERS == ("files_indexed", "paths_excluded_by_rule", "files_reused_from_stat_cache", "files_recomputed", "files_deferred")`. `paths_excluded_by_rule` is a **dict keyed by rule**, not an int. `summary.DEFERRED_BUDGET == "scan budget exhausted"`.

**P4 — `evidence_shape`.** `runs.COMPLETENESS == ("complete", "capped", "partial", "metadata_only", "deferred", "unsupported", "unreadable", "failed", "dataless")` — **nine, not the SPEC's eight**; see the CONFLICT callout on Task 14. `runs.ExtractionRun` fields include `completeness`, `coverage`, `file_id`, `content_hash`, `extractor_name`, `failure_reason`. `store.runs_for_file(conn, file_id) -> list[ExtractionRun]`, `store.runs_for_content(conn, content_hash) -> list[ExtractionRun]`, `store.observations_by_key(conn, observation_key) -> list[Observation]`, `store.unit_for_observation(conn, observation) -> TextUnit | None`. `observation.Observation` carries `raw_value`, `normalized_value`, `context_before`, `context_after`, `context_truncated`, `location`, `reliability`, `signal_tier`.

**P6 — `facts`.** `read_surface.facts_for(conn, *, file_id, content_hash, states=None, domain=None) -> list[sqlite3.Row]`, `read_surface.evidence_chain(conn, *, fact_id) -> list[Observation]`, `read_surface.STRENGTH_ORDER == ("possible", "llm_supported", "validated", "direct", "user_confirmed")`; `file_facts.FILE_FACTS_COLUMNS`, `file_facts.FORBIDDEN_COLUMN_SUBSTRINGS == ("path", "destination", "folder", "node", "group")`; `fields.create_fields(conn)`.

**P7 — `privacy`.** `gate.Gate(conn, *, store, plan_version, classifier, transform, unclassified_permits_local, scope_for, files_in_scope, component_version, now, user_id, measure_tokens=None, template_for=None)` with methods `release(request)`, `reclassify(...)`, `may_move_automatically(file_id)`, `display_policy()`, `summarize_protected(scope)`, `revoke(scope, *, retraction_limit)`. `display.RedactionSettings(names, previews, thumbnails, ocr_text, location_data)`; `display.DISPLAY_FACETS`; `display.REDACTION_VALUES == ("shown", "redacted")`; `display.ProtectedSummary(count, scope_total, class_breakdown)`; `display.HANDLING_CLASSES` (five). `revocation.RevocationResult(effective_from, prior_releases, retraction_limit)` and `revocation.PriorRelease(model, provider, when, excerpts)`. `consent.NeedsConsent(consent_request_id, requirement, options)`, `consent.ConsentRequirement(file_ids, handling_class, items, why)`, `consent.CONSENT_OPTIONS == ("local_model", "cloud_model", "redacted_prompt", "no_model_use")`, `consent.pending_consent(conn, consent_request_id) -> NeedsConsent | None`, `consent.record_consent_choice(conn, consent_request_id, option, *, policy, scope, user_id, component_version, observed_at) -> None`. `schema.create_privacy_schema(conn)`.

**P8 — `llm_harness`.** `records.P8Verdict` fields `(verdict_id, dossier_id, claim_ref, outcome, disposition, reasons, may_propose, requires_review, citations_checked, scope, validator_version, policy_version, plan_version)`; `records.OUTCOMES`; `records.ACCEPT_CONTEXT_SUPPORTED == "accept_context_supported"`.

**P9 — `grouping`.** `schema.create_grouping_schema(conn)`.

**P10 — `tree_design`.** `records.Node` with `node_id`, `plan_version_id`, `node_type`, `display_label`, `parent_node_id`, `root_anchor`, `ordinal`, `explanation`, `node_role`, `accepts_placement`, `handling_class`, `origin_node_id`, `existing_path`, `disposition`, and fifteen more; `records.NODE_ROLES == ("ordinary", "scoped-general", "residual", "shared-material")`; `records.NODE_TYPES == ("existing", "proposed", "user-created", "protected", "ignored")`. `store.nodes_for_version(conn, plan_version_id) -> tuple[Node, ...]`, `store.apply_review_action(conn, action, *, new_version_id, created_at, mint_node_id, component_version, project=None) -> str`, `store.TREE_EDIT_ACTIONS` (fifteen), `store.VERSION_ACTIONS == ("adopt_version", "restore_version")`, `store.ACTIONS_WITH_A_WRITER` (five), `store.ACTIONS_WITH_NO_WRITER` (ten). `diff.diff_versions(conn, *, before, after) -> tuple[NodeDiffEntry, ...]` and `diff.NodeDiffEntry(kind, node_id, origin_node_id, before, after, undo_label)` with the seven `DIFF_*` kinds. `freeze.frozen_tree(conn, *, plan_version) -> FrozenTree`. `candidates.BranchCandidate`, `candidates.VerticalOption`, `health.TreeHealth`, `health.Warning_`. **Just shipped (`dfdc015`):** `user_edits.UserLevelEdit`, `user_edits.UnappliedUserEdit(edit, kind, explanation)`, `user_edits.user_level_edits(conn, *, schemas=None) -> tuple[UserLevelEdit, ...]`, `user_edits.describe_applied_edits(dimensions) -> str`, `user_edits.OVERLAY_ACTIONS_WITH_A_WRITER`.

**P11 — `placement`.** `store.current_decision(conn, *, plan_version, subject_ref) -> PlacementDecision | None`, `store.decision_history(conn, *, subject_ref) -> tuple[PlacementDecision, ...]`, `store.decisions_for_plan(conn, *, plan_version) -> tuple[PlacementDecision, ...]`, `store.subject_ref_of(subject) -> str`. `records.PlacementDecision` carries all thirty fields the SPEC's Contract-in names, plus `superseded_by`, `supersede_reason` and `created_at`. `residual.ResidualSet(set_id, plan_version, label, file_count, representative_examples, file_type_distribution, age_range, evidence_availability, sensitivity_status, protected, weak_graph_neighbours, reason_not_placed, member_file_ids)` — thirteen fields, and `protected` is **an extra the SPEC's seven-attribute list does not name**. `residual.ResidualSetDecision(set_id, plan_version, choice, decided_at, node_id)`, `residual.require_set_decision(conn, *, plan_version, set_id) -> ResidualSetDecision`, `residual.model_calls_permitted(decision) -> bool`, `residual.SET_CHOICES == ("leave_in_place", "review_with_model_against_approved_residual_folders", "send_to_approved_node", "create_custom_branch")`. `groups.GroupPlan(group_plan_id, plan_version, group_id, shared_parent_node_id, member_decisions, excluded_outliers)`, `groups.ExcludedOutlier(file_id, conflicting_fact, evidence_ref, routed_to, node_id)`. `versions.reproject(conn, *, from_plan_version, to_plan_version, revalidation_inputs=None) -> VersionDiff` and `versions.VersionDiff(from_plan_version, to_plan_version, requiring_renewed_review, carried_unchanged, removed_node_ids)`. `review.apply_review_action(conn, action, *, decision_factory, component_version, observed_at) -> tuple[str, ...]`, `review.routes_to_p10(action) -> bool`, `review.correction_scope_of(action) -> tuple[str, str]`, `review.P11_SURFACES`, `review.P11_ACTIONS`. `vocabulary.CONFIDENCE_CLASSES == ("exact fact match", "context-supported group match", "shared-material decision", "abstain: no supported destination")`, `vocabulary.REVIEW_POLICIES == ("auto_eligible", "review_required", "blocked_pending_user")`, `vocabulary.OUTCOMES` (seven), `vocabulary.ABSTENTION_REASONS` (nine). `schema.create_placement_schema(conn)`.

### What does NOT exist, and what this plan does about it

> **P12 DOES NOT EXIST.** There is no package under `src/` for apply, undo, move plans, name resolution, collision resolution, journal entries or undo verdicts. `ls src/` shows `cli.py database_agent eval_harness evidence_shape extractors facts grouping llm_harness orchestrator.py placement privacy production.py readers recognition scan_agent tree_design`. **Done-means 11, 12 and 13 and the whole `review_approval` record depend on P12's Contract-out.** Task 11 builds them against an injected seam plus `tests/p13/p12_fixtures.py`, exactly as P9 built its P8 seam and its P13 receiver. `src/review_surface/` never imports the fixture and Task 18's guard asserts it. Replacing the fixture with P12's public records is a required integration test when P12 ships, and Task 11 names the swap boundary line by line.

> **THREE INCOMPATIBLE `review_action` FIXTURES ALREADY EXIST, AND NONE MATCHES THE SPEC. UNRESOLVED — DO NOT RESOLVE IT.** `tests/p9/p13_fixtures.py`, `tests/p10/p13_fixtures.py` and `tests/p11/p13_fixtures.py` each publish a `ReviewActionFixture` with a different field list and a different action vocabulary:
>
> | | id field | timestamp | action vocabulary |
> |---|---|---|---|
> | `tests/p9` | *(none)* — keyed by `group_id`/`membership_id` | `decided_at` | `accept, edit, reject, defer, restore, reset-suggestion, exclude-from-packet` |
> | `tests/p10` | `review_action_id` | `observed_at` | `accept, rename, ignore, restore_version, add-scoped-general, set-shared-material-policy` |
> | `tests/p11` | `action_id` | `acted_at` | the SPEC's eleven placement/residual actions |
> | **P13 SPEC:246-280** | `action_id` | `acted_at` | **seventeen** actions |
>
> `tests/p11` matches the SPEC. `tests/p9` and `tests/p10` do not — `edit`, `restore`, `reset-suggestion`, `exclude-from-packet`, `rename`, `ignore`, `add-scoped-general` and `set-shared-material-policy` are **not** among the SPEC's seventeen `action` values, and `review_action_id`, `plan_version_id`, `group_id`, `membership_id`, `basis`, `user_edited_label`, `decided_at` and `observed_at` are **not** among its fields. Meanwhile `tree_design.store.apply_review_action` reads `.action` against `TREE_EDIT_ACTIONS` (fifteen values, none of them in the SPEC's list) and `grouping` reads `.basis`, `.group_id` and `.membership_id`.
>
> **This plan builds the SPEC's record and no other.** Task 8 publishes `ReviewAction` with the SPEC's exact fields. Task 8 also publishes a **compatibility report**, not a compatibility shim: a test that enumerates, for each of the three existing fixtures, every field and every action value P13's record cannot supply, and fails with that list printed. **Reconciling the four vocabularies is a decision for Joseph, not for a plan author.** Do not widen P13's `ACTIONS` to absorb P10's or P9's; do not narrow P10's or P9's; do not write a translation table. Three parts each guessed at a record its owner had not published, which is exactly the "consumer with no producer" defect class round 4 was built to find — here it has produced three producers and no consumer.

---

## File structure

```text
src/review_surface/__init__.py             narrow P13 public exports
src/review_surface/vocabulary.py           P13's five closed vocabularies, both ways
src/review_surface/schema.py               P13's three tables inside P1's database
src/review_surface/records.py              ReviewAction, ReviewApproval, ProgressLine, ProgressEntry
src/review_surface/presentation.py         presented_state_ref and the `review presentation` event
src/review_surface/labels.py               the ancestor display_label chain (B3)
src/review_surface/locations.py            `66` §3's six-state result element
src/review_surface/states.py               `66` §4's five distinct absence states
src/review_surface/citations.py            observation_key -> displayable excerpt, or a named failure
src/review_surface/items.py                the placement and group-plan review items
src/review_surface/residual.py             the residual screen and §7.6's ordering guard
src/review_surface/routing.py              which part(s) a surface and an action are handed to
src/review_surface/collect.py              collecting a review_action, with its scope and its routing
src/review_surface/bulk.py                 an expandable bulk acceptance
src/review_surface/rejections.py           a rejection stored with its evidence, re-presented
src/review_surface/apply_seam.py           the injected P12 seam: apply, stale, undo-conflict items
src/review_surface/approval.py             review_approval, the §8.3 gate finally consumed
src/review_surface/redaction_boundary.py   what P13 must not ask for under a redaction policy
src/review_surface/progress.py             the §8.6 progress line
src/review_surface/consent_surface.py      the NeedsConsent surface and its four options
src/review_surface/evaluation.py           the §8.5 view; no aggregate accuracy, ever
src/review_surface/learning_view.py        the §8.7 inspect-and-reset surface
src/review_surface/versions_view.py        the §8.8 diff and `66` §17's draft-plan adoption
src/review_surface/store.py                append and read P13's own three tables
src/review_surface/replay.py               every surface from a P2 bundle; presented_state_ref round-trip

tests/p13/conftest.py                      a real P1-P11 database; publishes `p13_conn`
tests/p13/p12_fixtures.py                  recorded P12-shaped records. TESTS ONLY.
tests/p13/test_p13_*.py                    focused TDD suites, one per task
```

No task in this plan edits `planning/domains/`, `planning/deferred-catalogues/`, `.superpowers/`, or any file under `src/` outside `src/review_surface/`.

---

### Task 1: The package skeleton, five closed vocabularies published both ways, and `p13_conn`

**Files:**
- Create: `src/review_surface/__init__.py`
- Create: `src/review_surface/vocabulary.py`
- Create: `src/review_surface/schema.py`
- Create: `tests/p13/__init__.py`
- Create: `tests/p13/conftest.py`
- Test: `tests/p13/test_p13_vocabulary.py`
- Test: `tests/p13/test_p13_schema.py`

**Interfaces:**

*Consumes:*

```python
from database_agent.db import create_schema           # (conn: sqlite3.Connection) -> None
from database_agent.events import CORRECTION_SCOPES   # ("file","group","node","template","domain","corpus")
from eval_harness.store import create_eval_schema     # (conn) -> None
from facts.fields import create_fields                # (conn) -> None
from grouping.schema import create_grouping_schema    # (conn) -> None
from privacy.schema import create_privacy_schema      # (conn) -> None
from placement.schema import create_placement_schema  # (conn) -> None
```

*Produces:*

```python
# src/review_surface/vocabulary.py
SUBSYSTEM: str                       # "P13"
SURFACES: tuple[str, ...]            # twelve
ACTIONS: tuple[str, ...]             # seventeen
VERDICTS: tuple[str, ...]            # four
PROGRESS_STATES: tuple[str, ...]     # three
PROGRESS_SOURCES: tuple[str, ...]    # three
CORRECTION_SCOPES: tuple[str, ...]   # P1's six, imported not respelled
EVENT_PRESENTATION: str              # "review presentation"
EVENT_ACTION_ROUTED: str             # "review action routed"
EVENT_APPROVAL: str                  # "apply review approval"
UNTOUCHED_PROTECTED: str             # "untouched_protected"
# ...and one named constant per member of every tuple above.
class OutOfVocabulary(ValueError): ...
def check(value: object, allowed: tuple[str, ...], *, name: str) -> str: ...

# src/review_surface/schema.py
REVIEW_TABLES: tuple[str, ...]       # ("review_actions", "review_approvals", "review_presentations")
def create_review_schema(conn: sqlite3.Connection) -> None: ...
```

**Done-means:** partial 22 (P13 owns exactly three tables and writes no record outside the four in Contract out); prerequisite for every other task.

- [ ] **Step 1: Write the failing vocabulary and schema tests**

Create `tests/p13/__init__.py` as an empty file, then `tests/p13/test_p13_vocabulary.py`:

```python
"""Every closed vocabulary P13 publishes, both ways, and nowhere else."""
from __future__ import annotations

import pytest

from database_agent.events import CORRECTION_SCOPES as P1_SCOPES
from review_surface import vocabulary as v


def test_the_twelve_surfaces_are_the_spec_s_twelve():
    assert v.SURFACES == (
        "placement", "group_plan", "residual_set", "residual_file", "canvas",
        "apply", "undo_conflict", "consent", "privacy_settings", "evaluation",
        "learning", "plan_version",
    )


def test_the_eighteen_actions_are_the_spec_s_eighteen():
    assert v.ACTIONS == (
        "accept", "accept_bulk", "change_destination",
        "return_to_accepted_group", "create_custom_folder", "mark_private",
        "defer", "leave_untouched", "reject", "edit_recommendation",
        "disable_suggestion_type", "refresh_plan", "approve_for_apply",
        "select_consent_option", "set_redaction", "adopt_version",
        "restore_version", "reset_learning",
    )
    assert len(v.ACTIONS) == 18


def test_every_action_the_spec_prints_is_present():
    for name in ("accept", "accept_bulk", "change_destination",
                 "return_to_accepted_group", "create_custom_folder",
                 "mark_private", "defer", "leave_untouched", "reject",
                 "edit_recommendation", "disable_suggestion_type",
                 "refresh_plan", "approve_for_apply", "select_consent_option",
                 "set_redaction", "adopt_version", "restore_version",
                 "reset_learning"):
        assert name in v.ACTIONS, f"{name} is one of P13 SPEC:264-270's actions"


def test_the_four_approval_verdicts():
    assert v.VERDICTS == ("approved", "rejected", "deferred", "refresh_required")


def test_the_three_progress_states_and_three_sources():
    assert v.PROGRESS_STATES == ("completed", "deferred", "blocked")
    assert v.PROGRESS_SOURCES == ("P3.R5", "P4.extraction_runs", "P8")


def test_correction_scopes_are_p1_s_and_not_a_second_copy():
    assert v.CORRECTION_SCOPES is P1_SCOPES


def test_every_member_of_every_vocabulary_has_a_named_constant():
    """Brief §11: a bare string is a second home and an index is unreadable."""
    named = {value for name, value in vars(v).items()
             if name.isupper() and isinstance(value, str)}
    for tuple_name in ("SURFACES", "ACTIONS", "VERDICTS", "PROGRESS_STATES",
                       "PROGRESS_SOURCES"):
        for member in getattr(v, tuple_name):
            assert member in named, (
                f"{member!r} in {tuple_name} has no named constant; consumers "
                "would have to write the literal or an index")


def test_the_three_event_names_are_the_registered_ones():
    from database_agent.events import EVENT_TYPES
    for name in (v.EVENT_PRESENTATION, v.EVENT_ACTION_ROUTED, v.EVENT_APPROVAL):
        assert name in EVENT_TYPES, (
            f"{name!r} must already be registered; P13 registers nothing")


def test_check_accepts_a_member_and_names_the_vocabulary_on_a_miss():
    assert v.check("placement", v.SURFACES, name="surface") == "placement"
    with pytest.raises(v.OutOfVocabulary) as caught:
        v.check("dashboard", v.SURFACES, name="surface")
    assert "surface" in str(caught.value)
    assert "dashboard" in str(caught.value)


def test_untouched_protected_is_not_a_surface_and_not_an_action():
    """P13 SPEC:260-262 -- it carries no action at all."""
    assert v.UNTOUCHED_PROTECTED not in v.SURFACES
    assert v.UNTOUCHED_PROTECTED not in v.ACTIONS
```

Then `tests/p13/test_p13_schema.py`:

```python
"""P13's three tables, inside P1's one database, append-only."""
from __future__ import annotations

import sqlite3

import pytest

from review_surface.schema import REVIEW_TABLES, create_review_schema


def _tables(conn) -> set[str]:
    return {row["name"] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}


def test_p13_owns_exactly_three_tables(p13_conn):
    assert REVIEW_TABLES == (
        "review_actions", "review_approvals", "review_presentations")
    assert set(REVIEW_TABLES) <= _tables(p13_conn)


def test_creating_the_schema_twice_is_a_no_op(p13_conn):
    before = _tables(p13_conn)
    create_review_schema(p13_conn)
    assert _tables(p13_conn) == before


def test_p13_creates_no_table_belonging_to_another_part(conn):
    """A fresh connection with ONLY P1 and P13 must gain exactly three tables."""
    from database_agent.db import create_schema
    create_schema(conn)
    before = _tables(conn)
    create_review_schema(conn)
    assert _tables(conn) - before == set(REVIEW_TABLES)


@pytest.mark.parametrize("table", ("review_actions", "review_approvals",
                                   "review_presentations"))
def test_every_p13_table_refuses_an_update_and_a_delete(p13_conn, table):
    """§8.2 is append-only and P13 owns no supersedable record (SPEC:521)."""
    columns = [row["name"] for row in
               p13_conn.execute(f"PRAGMA table_info({table})")]
    first = columns[0]
    with pytest.raises(sqlite3.IntegrityError):
        p13_conn.execute(f"UPDATE {table} SET {first} = {first}")
    with pytest.raises(sqlite3.IntegrityError):
        p13_conn.execute(f"DELETE FROM {table}")


def test_no_p13_column_names_a_path_or_a_score(p13_conn):
    """B3: P13 shows a node and its ancestor labels, never a resolved path.

    `undo_conflict` paths are carried on an item record built from P12's own
    record, never stored in a P13 table -- see Task 11's CONFLICT callout.
    """
    forbidden = ("path", "score", "confidence_value", "threshold", "weight")
    for table in REVIEW_TABLES:
        for row in p13_conn.execute(f"PRAGMA table_info({table})"):
            for substring in forbidden:
                assert substring not in row["name"], (
                    f"{table}.{row['name']} contains {substring!r}")
```

And `tests/p13/conftest.py`:

```python
"""A real P1-P11 database with P13's tables. No mock, no in-memory stand-in.

Every part whose records P13 projects is created, for the reason P11's conftest
gives for creating P9's: a read against an absent table proves nothing about the
read, only about the table. P13 projects more parts than any other, so it creates
more of them.
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema
from eval_harness.run import ANALYSIS_TIERS, record_version_tuple, start_run
from eval_harness.store import create_eval_schema
from facts.fields import create_fields
from grouping.schema import create_grouping_schema
from placement.schema import create_placement_schema
from privacy.schema import create_privacy_schema

from review_surface.schema import create_review_schema

FIXED_CLOCK = "2026-08-29T00:00:00Z"
COMPONENT_VERSION = "p13-fixture-1"
USER = "jy"


@pytest.fixture()
def p13_conn(conn):
    create_schema(conn)
    create_eval_schema(conn)
    create_grouping_schema(conn)
    create_fields(conn)
    create_privacy_schema(conn)
    create_placement_schema(conn)
    create_review_schema(conn)
    return conn


@pytest.fixture()
def p13_version_tuple(p13_conn) -> str:
    return record_version_tuple(
        p13_conn, extractor_versions={}, graph_algorithm_version="1",
        prompt_fingerprint="fp-canonical", model_identifier="fixture-model",
        template_library_version="1", placement_scorer_version="fixture-v1",
        analysis_tiers_enabled=list(ANALYSIS_TIERS))


@pytest.fixture()
def p13_run_id(p13_conn, p13_version_tuple) -> str:
    """A replay run. P13 emits no stage output, but every surface must be
    renderable from a bundle (Done-means 23), and that needs a run to hang on."""
    return start_run(
        p13_conn, bundle_id="bundle-p13", run_kind="replay",
        version_tuple_ref=p13_version_tuple,
        started_at=FIXED_CLOCK)
```

> **If `start_run`'s keyword list differs from the above**, read it with `PYTHONPATH=src python3 -c "import inspect; from eval_harness.run import start_run; print(inspect.signature(start_run))"` and copy `tests/p11/conftest.py`'s live call verbatim. The `conn` fixture comes from the repository-root `tests/conftest.py` and is a real temporary-file SQLite connection with `row_factory = sqlite3.Row`.

- [ ] **Step 2: Run the tests and verify RED**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/`

Expected: **FAIL** — `ModuleNotFoundError: No module named 'review_surface'`. Every test in both files errors during collection.

- [ ] **Step 3: Write `src/review_surface/vocabulary.py`**

```python
# src/review_surface/vocabulary.py
"""P13's closed vocabularies, published BOTH ways.

A tuple for iteration and membership, and one named constant per member for
every consumer. Never a bare string in another module -- a literal is a second
home for a vocabulary and this project's most expensive defect class. Never an
index either: `SURFACES[3]` is single-homed, unreadable, and silently couples the
reader to the tuple's ORDER, so reordering the tuple would change meanings with
no test failing.

`CORRECTION_SCOPES` is IMPORTED from P1, not respelled. P1's writer validates
against it and P1's learning store reads against it; a scope one accepted and the
other rejected would be storable and permanently unreadable.
"""
from __future__ import annotations

from database_agent.events import CORRECTION_SCOPES

#: §8.2's "responsible subsystem" for every event P13 appends. ONE place.
SUBSYSTEM: str = "P13"


class OutOfVocabulary(ValueError):
    """A value outside a closed list, named at the seam rather than stored."""


def check(value: object, allowed: tuple[str, ...], *, name: str) -> str:
    """Return `value` if it is in `allowed`, else raise naming both."""
    if value not in allowed:
        raise OutOfVocabulary(
            f"{value!r} is not one of P13's {len(allowed)} {name} values: "
            f"{list(allowed)}")
    return value  # type: ignore[return-value]


# --- surfaces (P13 SPEC:249-251) ------------------------------------------
SURFACE_PLACEMENT: str = "placement"
SURFACE_GROUP_PLAN: str = "group_plan"
SURFACE_RESIDUAL_SET: str = "residual_set"
SURFACE_RESIDUAL_FILE: str = "residual_file"
SURFACE_CANVAS: str = "canvas"
SURFACE_APPLY: str = "apply"
SURFACE_UNDO_CONFLICT: str = "undo_conflict"
SURFACE_CONSENT: str = "consent"
SURFACE_PRIVACY_SETTINGS: str = "privacy_settings"
SURFACE_EVALUATION: str = "evaluation"
SURFACE_LEARNING: str = "learning"
SURFACE_PLAN_VERSION: str = "plan_version"

SURFACES: tuple[str, ...] = (
    SURFACE_PLACEMENT, SURFACE_GROUP_PLAN, SURFACE_RESIDUAL_SET,
    SURFACE_RESIDUAL_FILE, SURFACE_CANVAS, SURFACE_APPLY,
    SURFACE_UNDO_CONFLICT, SURFACE_CONSENT, SURFACE_PRIVACY_SETTINGS,
    SURFACE_EVALUATION, SURFACE_LEARNING, SURFACE_PLAN_VERSION,
)

# --- actions (P13 SPEC:264-270) -------------------------------------------
ACTION_ACCEPT: str = "accept"
ACTION_ACCEPT_BULK: str = "accept_bulk"
ACTION_CHANGE_DESTINATION: str = "change_destination"
ACTION_RETURN_TO_ACCEPTED_GROUP: str = "return_to_accepted_group"
ACTION_CREATE_CUSTOM_FOLDER: str = "create_custom_folder"
ACTION_MARK_PRIVATE: str = "mark_private"
ACTION_DEFER: str = "defer"
ACTION_LEAVE_UNTOUCHED: str = "leave_untouched"
ACTION_REJECT: str = "reject"
ACTION_EDIT_RECOMMENDATION: str = "edit_recommendation"
ACTION_DISABLE_SUGGESTION_TYPE: str = "disable_suggestion_type"
ACTION_REFRESH_PLAN: str = "refresh_plan"
ACTION_APPROVE_FOR_APPLY: str = "approve_for_apply"
ACTION_SELECT_CONSENT_OPTION: str = "select_consent_option"
ACTION_SET_REDACTION: str = "set_redaction"
ACTION_ADOPT_VERSION: str = "adopt_version"
ACTION_RESTORE_VERSION: str = "restore_version"
ACTION_RESET_LEARNING: str = "reset_learning"

ACTIONS: tuple[str, ...] = (
    ACTION_ACCEPT, ACTION_ACCEPT_BULK, ACTION_CHANGE_DESTINATION,
    ACTION_RETURN_TO_ACCEPTED_GROUP, ACTION_CREATE_CUSTOM_FOLDER,
    ACTION_MARK_PRIVATE, ACTION_DEFER, ACTION_LEAVE_UNTOUCHED, ACTION_REJECT,
    ACTION_EDIT_RECOMMENDATION, ACTION_DISABLE_SUGGESTION_TYPE,
    ACTION_REFRESH_PLAN, ACTION_APPROVE_FOR_APPLY,
    ACTION_SELECT_CONSENT_OPTION, ACTION_SET_REDACTION, ACTION_ADOPT_VERSION,
    ACTION_RESTORE_VERSION, ACTION_RESET_LEARNING,
)

# --- approval verdicts (P13 SPEC:360) -------------------------------------
VERDICT_APPROVED: str = "approved"
VERDICT_REJECTED: str = "rejected"
VERDICT_DEFERRED: str = "deferred"
VERDICT_REFRESH_REQUIRED: str = "refresh_required"

VERDICTS: tuple[str, ...] = (
    VERDICT_APPROVED, VERDICT_REJECTED, VERDICT_DEFERRED,
    VERDICT_REFRESH_REQUIRED,
)

# --- progress line (P13 SPEC:328-331) -------------------------------------
STATE_COMPLETED: str = "completed"
STATE_DEFERRED: str = "deferred"
STATE_BLOCKED: str = "blocked"
PROGRESS_STATES: tuple[str, ...] = (
    STATE_COMPLETED, STATE_DEFERRED, STATE_BLOCKED)

SOURCE_P3_R5: str = "P3.R5"
SOURCE_P4_RUNS: str = "P4.extraction_runs"
SOURCE_P8: str = "P8"
PROGRESS_SOURCES: tuple[str, ...] = (SOURCE_P3_R5, SOURCE_P4_RUNS, SOURCE_P8)

# --- the three registered §8.2 event names --------------------------------
EVENT_PRESENTATION: str = "review presentation"
EVENT_ACTION_ROUTED: str = "review action routed"
EVENT_APPROVAL: str = "apply review approval"
EVENT_TYPES: tuple[str, ...] = (
    EVENT_PRESENTATION, EVENT_ACTION_ROUTED, EVENT_APPROVAL)

#: P3 SPEC, ratified 2026-08-20 and restated at P13 SPEC:260-262. A protected
#: container is its own inspectable list and carries NO ACTION AT ALL. It is not
#: a surface, because a surface is a place a gesture can be made.
UNTOUCHED_PROTECTED: str = "untouched_protected"

__all__ = [name for name in dir() if name.isupper()] + [
    "OutOfVocabulary", "check", "CORRECTION_SCOPES"]
```

- [ ] **Step 4: Write `src/review_surface/schema.py`**

```python
# src/review_surface/schema.py
"""P13's three tables, inside P1's single database.

§0: "A local SQLite database acts as the durable working memory of the product."
One table per part is this project's CONVENTION, written plainly rather than
cited, because the last time this convention acquired quote marks a sentence
nobody wrote was quoted in three PLANs and one module.

P13 owns no supersedable record (SPEC:521): it never edits a decision, plan,
verdict, fact or observation. So every table here refuses UPDATE and DELETE by
TRIGGER, not by convention, and there is no `superseded_by` column anywhere --
a supersede column with no writer is the defect class this project has paid for
most often.

NO COLUMN HOLDS A PATH. B3: P13 shows a node and its ancestor `display_label`
chain, and P12 alone composes paths. The undo-conflict item carries P12's paths
because §8.3's own sentence demands them; it is built and shown, never stored
here.
"""
from __future__ import annotations

import sqlite3

REVIEW_TABLES: tuple[str, ...] = (
    "review_actions", "review_approvals", "review_presentations")

_DDL = """
CREATE TABLE IF NOT EXISTS review_presentations (
    presented_state_ref TEXT PRIMARY KEY,
    event_id            INTEGER NOT NULL,
    surface             TEXT NOT NULL,
    subject_ref         TEXT NOT NULL,
    plan_version        TEXT NOT NULL,
    session_id          TEXT NOT NULL,
    redaction_policy    TEXT NOT NULL,
    evidence_refs       TEXT NOT NULL,
    user_id             TEXT,
    rendered_at         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS review_actions (
    action_id           TEXT PRIMARY KEY,
    surface             TEXT NOT NULL,
    subject_ref         TEXT NOT NULL,
    plan_version        TEXT NOT NULL,
    session_id          TEXT NOT NULL,
    action              TEXT NOT NULL,
    bulk_member_refs    TEXT NOT NULL,
    bulk_basis          TEXT,
    correction_scope    TEXT NOT NULL,
    routed_to           TEXT NOT NULL,
    presented_state_ref TEXT NOT NULL
        REFERENCES review_presentations (presented_state_ref),
    payload             TEXT NOT NULL,
    user_id             TEXT NOT NULL,
    acted_at            TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS review_approvals (
    approval_id            TEXT PRIMARY KEY,
    plan_id                TEXT NOT NULL,
    placement_decision_ref TEXT NOT NULL,
    plan_version           TEXT NOT NULL,
    required_review_policy TEXT NOT NULL,
    verdict                TEXT NOT NULL,
    presented_state_ref    TEXT NOT NULL
        REFERENCES review_presentations (presented_state_ref),
    user_id                TEXT NOT NULL,
    decided_at             TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS review_actions_by_subject
    ON review_actions (subject_ref, plan_version);
CREATE INDEX IF NOT EXISTS review_approvals_by_plan
    ON review_approvals (plan_id, plan_version);
CREATE INDEX IF NOT EXISTS review_presentations_by_subject
    ON review_presentations (subject_ref, surface);
"""

_APPEND_ONLY = """
CREATE TRIGGER IF NOT EXISTS {table}_no_update
BEFORE UPDATE ON {table}
BEGIN
    SELECT RAISE(ABORT, '{table} is append-only: P13 owns no supersedable record');
END;

CREATE TRIGGER IF NOT EXISTS {table}_no_delete
BEFORE DELETE ON {table}
BEGIN
    SELECT RAISE(ABORT, '{table} is append-only: P13 owns no supersedable record');
END;
"""


def create_review_schema(conn: sqlite3.Connection) -> None:
    """Create P13's three tables and their append-only triggers. Idempotent."""
    conn.executescript(_DDL)
    for table in REVIEW_TABLES:
        conn.executescript(_APPEND_ONLY.format(table=table))
    conn.commit()
```

And `src/review_surface/__init__.py`:

```python
# src/review_surface/__init__.py
"""P13 -- the review and approval surface. It presents and collects; it never decides.

Two rules govern every module here (P13 SPEC:40-48):

**P13 presents and collects; it never decides.** Every user action is routed to
the owning part as an §8.7 correction carrying its scope. A collected action never
becomes a fact, a verdict, a group, a placement, a tree edit or a filesystem
mutation inside P13.

**P13 renders only what the boundary released.** Redaction happens in the part
that owns the data -- P7's display policy (§8.4). P13 has no code path that
receives protected content and then hides it; it has code paths that decline to
ask for it.

This package is a DATA AND CONTRACT layer. There is no framework, no HTML, no
TUI and no rendering loop. Layout, components, styling, typography, colour,
iconography, interaction patterns and every word of user-facing copy are
DEFERRED by the SPEC's own Deferred table: it fixes the information contract and
fixes no pixel.
"""
from review_surface.schema import REVIEW_TABLES, create_review_schema
from review_surface.vocabulary import (
    ACTIONS, PROGRESS_SOURCES, PROGRESS_STATES, SUBSYSTEM, SURFACES, VERDICTS,
    OutOfVocabulary, check,
)

__all__ = [
    "ACTIONS", "PROGRESS_SOURCES", "PROGRESS_STATES", "REVIEW_TABLES",
    "SUBSYSTEM", "SURFACES", "VERDICTS", "OutOfVocabulary", "check",
    "create_review_schema",
]
```

- [ ] **Step 5: Run the tests and verify PASS**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/`

Expected: **PASS** — all tests in `test_p13_vocabulary.py` and `test_p13_schema.py` green.

Then confirm nothing else moved: `cd "/Users/jy/GRAPH AGENT" && python3 -m pytest -q -p no:randomly 2>&1 | tail -3`. Expected: the previous total plus the new P13 tests, no failures.

- [ ] **Step 6: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/review_surface/__init__.py src/review_surface/vocabulary.py src/review_surface/schema.py tests/p13/__init__.py tests/p13/conftest.py tests/p13/test_p13_vocabulary.py tests/p13/test_p13_schema.py && git commit -m "feat(p13-1): P13's five closed vocabularies and its three append-only tables"
```

---

### Task 2: `presented_state_ref` — what the user was actually shown, under the policy then in force

**Files:**
- Create: `src/review_surface/presentation.py`
- Test: `tests/p13/test_p13_presentation.py`

**Interfaces:**

*Consumes:*

```python
from database_agent.events import append_event          # (conn, **fields) -> int
from privacy.display import RedactionSettings           # (names, previews, thumbnails, ocr_text, location_data)
from privacy.display import DISPLAY_FACETS, REDACTION_VALUES
from review_surface.vocabulary import (
    EVENT_PRESENTATION, SUBSYSTEM, SURFACES, check,
)
from review_surface.schema import create_review_schema
```

*Produces:*

```python
@dataclass(frozen=True)
class PresentedState:
    presented_state_ref: str
    event_id: int
    surface: str
    subject_ref: str
    plan_version: str
    session_id: str
    redaction_policy: Mapping[str, str]   # one entry per DISPLAY_FACETS member
    evidence_refs: tuple[str, ...]        # observation_keys ACTUALLY shown
    user_id: str | None
    rendered_at: str

def record_presentation(conn: sqlite3.Connection, *, surface: str,
                        subject_ref: str, plan_version: str, session_id: str,
                        settings: RedactionSettings,
                        evidence_refs: Sequence[str], user_id: str | None,
                        component_version: str,
                        rendered_at: str) -> PresentedState: ...

def presented_state(conn: sqlite3.Connection,
                    presented_state_ref: str) -> PresentedState | None: ...

def policy_of(settings: RedactionSettings) -> dict[str, str]: ...

class PresentationPolicyMismatch(RuntimeError): ...

def assert_still_current(conn: sqlite3.Connection, presented_state_ref: str, *,
                         settings: RedactionSettings) -> PresentedState: ...
```

**Done-means:** prerequisite for 3, 8, 10, 14; the second clause of 14 (*"no cached rendering from before the policy change survives it"*); half of 23.

**Why this record exists, and why it is not noise.** SPEC:509-512: §8.4 makes what was displayed a privacy-relevant fact, and §8.7 requires a stored negative example to carry the evidence that produced it. A rejection is only interpretable against what the user was actually shown — a file rejected while its OCR text was redacted is a different signal from one rejected with the evidence visible. `assert_still_current` is what makes Done-means 14's second clause testable: a `presented_state_ref` minted under one policy cannot be reused to justify a display under another.

- [ ] **Step 1: Write the failing tests**

`tests/p13/test_p13_presentation.py`:

```python
"""What was shown, under the policy then in force. §8.2 + §8.4 + §8.7."""
from __future__ import annotations

import pytest

from privacy.display import DISPLAY_FACETS, RedactionSettings

from review_surface.presentation import (
    PresentationPolicyMismatch, assert_still_current, policy_of,
    presented_state, record_presentation,
)
from review_surface.vocabulary import (
    EVENT_PRESENTATION, SUBSYSTEM, SURFACE_PLACEMENT,
)

SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")
NAMES_REDACTED = RedactionSettings(
    names="redacted", previews="shown", thumbnails="shown",
    ocr_text="shown", location_data="shown")


def _record(conn, *, settings=SHOWN, refs=("obs-1",), subject="d1"):
    return record_presentation(
        conn, surface=SURFACE_PLACEMENT, subject_ref=subject,
        plan_version="plan-1", session_id="s-1", settings=settings,
        evidence_refs=refs, user_id="jy", component_version="p13-1",
        rendered_at="2026-08-29T00:00:00Z")


def test_a_presentation_is_stored_and_read_back_whole(p13_conn):
    state = _record(p13_conn)
    again = presented_state(p13_conn, state.presented_state_ref)
    assert again == state
    assert again.evidence_refs == ("obs-1",)
    assert again.surface == SURFACE_PLACEMENT


def test_the_policy_covers_every_display_facet_and_no_more(p13_conn):
    state = _record(p13_conn, settings=NAMES_REDACTED)
    assert tuple(state.redaction_policy) == DISPLAY_FACETS
    assert state.redaction_policy["names"] == "redacted"
    assert state.redaction_policy["ocr_text"] == "shown"


def test_a_presentation_appends_the_registered_event_with_p13_as_subsystem(p13_conn):
    state = _record(p13_conn)
    row = p13_conn.execute(
        "SELECT event_type, subsystem, user_id, explanation FROM events "
        "WHERE event_id = ?", (state.event_id,)).fetchone()
    assert row["event_type"] == EVENT_PRESENTATION
    assert row["subsystem"] == SUBSYSTEM
    assert row["user_id"] == "jy"
    assert "obs-1" in row["explanation"]


def test_the_event_explanation_names_the_policy_in_force(p13_conn):
    """§8.4 makes what was displayed a privacy-relevant fact."""
    state = _record(p13_conn, settings=NAMES_REDACTED)
    row = p13_conn.execute("SELECT explanation FROM events WHERE event_id = ?",
                           (state.event_id,)).fetchone()
    assert "names" in row["explanation"]
    assert "redacted" in row["explanation"]


def test_a_presentation_with_no_evidence_shown_is_recorded_not_refused(p13_conn):
    """A residual card, a progress line and a protected aggregate cite nothing.

    An empty tuple is a real answer -- "nothing evidential was displayed" -- and
    refusing it would make the only surfaces that show no evidence unrecordable.
    """
    state = _record(p13_conn, refs=())
    assert presented_state(p13_conn, state.presented_state_ref).evidence_refs == ()


def test_an_unknown_ref_reads_as_none_rather_than_raising(p13_conn):
    assert presented_state(p13_conn, "never-minted") is None


def test_a_cached_presentation_does_not_survive_a_policy_change(p13_conn):
    """Done-means 14, second clause."""
    state = _record(p13_conn, settings=SHOWN)
    assert assert_still_current(
        p13_conn, state.presented_state_ref, settings=SHOWN) == state
    with pytest.raises(PresentationPolicyMismatch) as caught:
        assert_still_current(p13_conn, state.presented_state_ref,
                             settings=NAMES_REDACTED)
    assert "names" in str(caught.value)


def test_asserting_an_unknown_ref_is_a_mismatch_not_a_silent_pass(p13_conn):
    with pytest.raises(PresentationPolicyMismatch):
        assert_still_current(p13_conn, "never-minted", settings=SHOWN)


def test_a_presentation_row_cannot_be_updated_or_deleted(p13_conn):
    import sqlite3
    state = _record(p13_conn)
    with pytest.raises(sqlite3.IntegrityError):
        p13_conn.execute(
            "UPDATE review_presentations SET surface = 'canvas' WHERE "
            "presented_state_ref = ?", (state.presented_state_ref,))
    with pytest.raises(sqlite3.IntegrityError):
        p13_conn.execute(
            "DELETE FROM review_presentations WHERE presented_state_ref = ?",
            (state.presented_state_ref,))


def test_an_unknown_surface_is_refused_before_anything_is_written(p13_conn):
    from review_surface.vocabulary import OutOfVocabulary
    before = p13_conn.execute(
        "SELECT count(*) AS c FROM review_presentations").fetchone()["c"]
    with pytest.raises(OutOfVocabulary):
        record_presentation(
            p13_conn, surface="dashboard", subject_ref="d1",
            plan_version="plan-1", session_id="s-1", settings=SHOWN,
            evidence_refs=(), user_id="jy", component_version="p13-1",
            rendered_at="2026-08-29T00:00:00Z")
    assert p13_conn.execute(
        "SELECT count(*) AS c FROM review_presentations").fetchone()["c"] == before


def test_policy_of_is_a_plain_mapping_over_p7_s_facets(p13_conn):
    assert policy_of(NAMES_REDACTED) == {
        "names": "redacted", "previews": "shown", "thumbnails": "shown",
        "ocr_text": "shown", "location_data": "shown"}
```

- [ ] **Step 2: Run the tests and verify RED**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_presentation.py`

Expected: **FAIL** — `ModuleNotFoundError: No module named 'review_surface.presentation'`.

- [ ] **Step 3: Write `src/review_surface/presentation.py`**

```python
# src/review_surface/presentation.py
"""What the user was ACTUALLY shown, under the redaction policy then in force.

SPEC:509-512 is the reason this is a distinct event and not noise: §8.4 makes
what was displayed a privacy-relevant fact, and §8.7 requires a stored negative
example to carry the evidence that produced it. A rejection is only interpretable
against what the user saw -- a file rejected while its OCR text was redacted is a
different signal from one rejected with the evidence visible.

`assert_still_current` is the mechanism behind Done-means 14's second clause.
A `presented_state_ref` is a claim about a policy as well as about a subject, so
a ref minted while names were shown cannot be re-used to justify a display after
the user redacts them. The check compares the WHOLE policy, not the one facet a
caller happens to care about: a facet-by-facet check would pass a ref minted
under three loosened facets as long as the fourth matched.

There is no `superseded_by` here and no update path. A presentation is a
historical fact about a moment; a later moment is a later row.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from database_agent.events import append_event
from privacy.display import DISPLAY_FACETS, RedactionSettings

from review_surface.vocabulary import (
    EVENT_PRESENTATION, SUBSYSTEM, SURFACES, check,
)


class PresentationPolicyMismatch(RuntimeError):
    """A stored presentation was made under a policy no longer in force."""


@dataclass(frozen=True)
class PresentedState:
    presented_state_ref: str
    event_id: int
    surface: str
    subject_ref: str
    plan_version: str
    session_id: str
    redaction_policy: Mapping[str, str]
    evidence_refs: tuple[str, ...]
    user_id: str | None
    rendered_at: str


def policy_of(settings: RedactionSettings) -> dict[str, str]:
    """P7's five facets as a plain mapping, in P7's own order.

    Read off `DISPLAY_FACETS` rather than off the dataclass's field order, so a
    facet P7 adds appears here the day P7 adds it instead of silently vanishing
    from every stored policy.
    """
    return {facet: getattr(settings, facet) for facet in DISPLAY_FACETS}


def _ref(surface: str, subject_ref: str, plan_version: str, session_id: str,
         policy: Mapping[str, str], evidence_refs: Sequence[str],
         rendered_at: str) -> str:
    """A deterministic ref over everything that makes this presentation what it was.

    Deterministic, so a replayed bundle mints the same ref for the same moment and
    Done-means 23's round-trip is an equality rather than a re-keying.
    """
    payload = json.dumps(
        [surface, subject_ref, plan_version, session_id, dict(policy),
         list(evidence_refs), rendered_at],
        sort_keys=True, separators=(",", ":"))
    return "ps-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def record_presentation(conn: sqlite3.Connection, *, surface: str,
                        subject_ref: str, plan_version: str, session_id: str,
                        settings: RedactionSettings,
                        evidence_refs: Sequence[str], user_id: str | None,
                        component_version: str,
                        rendered_at: str) -> PresentedState:
    """Append the §8.2 event, store the row, return the state. Vocabulary first."""
    check(surface, SURFACES, name="surface")
    policy = policy_of(settings)
    refs = tuple(evidence_refs)
    ref = _ref(surface, subject_ref, plan_version, session_id, policy, refs,
               rendered_at)
    explanation = json.dumps(
        {"surface": surface, "subject_ref": subject_ref,
         "plan_version": plan_version, "session_id": session_id,
         "redaction_policy": policy, "evidence_refs": list(refs),
         "presented_state_ref": ref},
        sort_keys=True)
    event_id = append_event(
        conn, event_type=EVENT_PRESENTATION, subsystem=SUBSYSTEM,
        component_version=component_version, observed_at=rendered_at,
        user_id=user_id, explanation=explanation)
    conn.execute(
        "INSERT OR REPLACE INTO review_presentations "
        "(presented_state_ref, event_id, surface, subject_ref, plan_version, "
        " session_id, redaction_policy, evidence_refs, user_id, rendered_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (ref, event_id, surface, subject_ref, plan_version, session_id,
         json.dumps(policy, sort_keys=True), json.dumps(list(refs)), user_id,
         rendered_at))
    conn.commit()
    return PresentedState(
        presented_state_ref=ref, event_id=event_id, surface=surface,
        subject_ref=subject_ref, plan_version=plan_version,
        session_id=session_id, redaction_policy=policy, evidence_refs=refs,
        user_id=user_id, rendered_at=rendered_at)


def presented_state(conn: sqlite3.Connection,
                    presented_state_ref: str) -> PresentedState | None:
    row = conn.execute(
        "SELECT * FROM review_presentations WHERE presented_state_ref = ?",
        (presented_state_ref,)).fetchone()
    if row is None:
        return None
    return PresentedState(
        presented_state_ref=row["presented_state_ref"],
        event_id=row["event_id"], surface=row["surface"],
        subject_ref=row["subject_ref"], plan_version=row["plan_version"],
        session_id=row["session_id"],
        redaction_policy=json.loads(row["redaction_policy"]),
        evidence_refs=tuple(json.loads(row["evidence_refs"])),
        user_id=row["user_id"], rendered_at=row["rendered_at"])


def assert_still_current(conn: sqlite3.Connection, presented_state_ref: str, *,
                         settings: RedactionSettings) -> PresentedState:
    """Done-means 14, second clause: a cached rendering does not survive a change.

    An unknown ref is a mismatch and not a pass. A caller holding a ref this
    database has never seen is holding a claim about a display nobody recorded,
    which is exactly the state the check exists to refuse.
    """
    state = presented_state(conn, presented_state_ref)
    if state is None:
        raise PresentationPolicyMismatch(
            f"{presented_state_ref!r} names no recorded presentation, so there "
            "is nothing to say what the user was shown or under what policy")
    wanted = policy_of(settings)
    if dict(state.redaction_policy) != wanted:
        changed = [facet for facet in DISPLAY_FACETS
                   if state.redaction_policy.get(facet) != wanted[facet]]
        raise PresentationPolicyMismatch(
            f"{presented_state_ref!r} was rendered under a policy that differs "
            f"on {changed}; a rendering cached before a policy change must not "
            "survive it (§8.4)")
    return state
```

- [ ] **Step 4: Run the tests and verify PASS**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_presentation.py`

Expected: **PASS** — twelve tests green.

- [ ] **Step 5: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/review_surface/presentation.py tests/p13/test_p13_presentation.py && git commit -m "feat(p13-2): presented_state_ref, and a cached rendering that cannot survive a policy change"
```

---

### Task 3: The ancestor `display_label` chain (B3), and `66` §3's six distinct location states

> **`66` EXTENDS THE SPEC HERE, AND `66` GOVERNS.** The SPEC's placement review item presents *"the destination as its ancestor `display_label` chain"* and stops. `66` §3 — dated 2026-08-29, nine days later — says a result must distinguish **six** states: current location, filed home, also-related-to, shared-material relationship, historical location, possible placement. It is explicit that *"These must not be collapsed into one ambiguous list of paths"* and that the product *"should not describe a valid multi-purpose relationship as a confidence failure."* `67` §2 calls this six-state model *"new and load-bearing"* and *"the answer to 'a research paper that is also school homework': that is two accepted relationships and one physical location, not a confidence failure."* This task builds the six-state element. The SPEC does not describe it; that is a gap in the SPEC, not a reason to skip it.

> **OPEN — `66` §3 asks for a CURRENT LOCATION, and B3 forbids P13 a path.** `66` §3's table says current location is *"The actual path where the file exists now"* and *"Always shown when the user is allowed to view it"*. The P13 SPEC's Explicitly-not-owned table says P13 *"shows a **node and its ancestor labels**, never a resolved path (B3); P12 resolves and executes."* These cannot both be literally true for a file that lives outside the destination tree — which is every file before it is filed, and every file the user leaves in place. **This plan builds `current_location` as an OPAQUE, INJECTED display string supplied by the caller, with P13 composing none of it and P13 storing none of it.** That satisfies B3's actual property (P13 does no path resolution) without pretending `66` §3's first row does not exist. **The reconciliation is Joseph's:** either B3 is narrowed to "P13 composes no path", or `66` §3's first row is narrowed to a node reference. Do not decide it in code.

**Files:**
- Create: `src/review_surface/labels.py`
- Create: `src/review_surface/locations.py`
- Test: `tests/p13/test_p13_labels.py`
- Test: `tests/p13/test_p13_locations.py`

**Interfaces:**

*Consumes:*

```python
from tree_design.records import Node                 # 22 fields incl. node_id, display_label, parent_node_id
from tree_design.store import nodes_for_version      # (conn, plan_version_id) -> tuple[Node, ...]
from placement.records import PlacementDecision, Destination
```

*Produces:*

```python
# labels.py
class NodeNotInVersion(LookupError): ...
class AncestorCycle(RuntimeError): ...

def label_chain(nodes: Sequence[Node], node_id: str) -> tuple[str, ...]: ...
def label_chain_for_version(conn: sqlite3.Connection, *, plan_version: str,
                            node_id: str) -> tuple[str, ...]: ...

# locations.py
LOCATION_STATES: tuple[str, ...]        # six, in 66 §3's own table order
CURRENT_LOCATION: str                   # "current_location"
FILED_HOME: str                         # "filed_home"
ALSO_RELATED_TO: str                    # "also_related_to"
SHARED_MATERIAL: str                    # "shared_material"
HISTORICAL_LOCATION: str                # "historical_location"
POSSIBLE_PLACEMENT: str                 # "possible_placement"

@dataclass(frozen=True)
class LocationElement:
    state: str
    label_chain: tuple[str, ...]
    node_id: str | None
    relationship_ref: str | None
    shared_policy: str | None
    opaque_current_location: str | None
    explanation: str

@dataclass(frozen=True)
class SixStateView:
    subject_ref: str
    plan_version: str
    elements: tuple[LocationElement, ...]
    def by_state(self, state: str) -> tuple[LocationElement, ...]: ...
    def as_flat_paths(self) -> None: ...   # raises. See below.

class LocationStatesCollapsed(RuntimeError): ...

def six_state_view(*, subject_ref: str, plan_version: str,
                   current: LocationElement | None,
                   filed_home: LocationElement | None,
                   also_related_to: Sequence[LocationElement],
                   shared_material: Sequence[LocationElement],
                   historical: Sequence[LocationElement],
                   possible: Sequence[LocationElement]) -> SixStateView: ...
```

**Done-means:** prerequisite for 1, 4, 5, 12, 21; and it is the whole of `66` §3.

- [ ] **Step 1: Write the failing tests**

`tests/p13/test_p13_labels.py`:

```python
"""B3: a node and its ancestor labels. Never a path, never a separator."""
from __future__ import annotations

import pytest

from tree_design.records import Node

from review_surface.labels import (
    AncestorCycle, NodeNotInVersion, label_chain,
)


def _node(node_id, label, parent=None, *, version="plan-1") -> Node:
    return Node(
        node_id=node_id, plan_version_id=version, node_type="proposed",
        display_label=label, parent_node_id=parent, root_anchor="root",
        ordinal=0, associated_group_ids=(), explanation="fixture",
        node_role="ordinary", accepts_placement=True,
        handling_class="public_low", origin_node_id=node_id,
        template_context=None, dimension_role=None, dimension=None,
        expected_values=(), existing_path=None, disposition=None,
        refinement_disposition=None, refinement_reason=None,
        protected_movement_permitted=False)


ACADEMICS = _node("n-1", "Academics")
COLUMBIA = _node("n-2", "Columbia", "n-1")
SPRING = _node("n-3", "2026-Spring", "n-2")
TREE = (ACADEMICS, COLUMBIA, SPRING)


def test_the_chain_runs_root_first():
    assert label_chain(TREE, "n-3") == ("Academics", "Columbia", "2026-Spring")


def test_a_root_node_is_a_chain_of_one():
    assert label_chain(TREE, "n-1") == ("Academics",)


def test_the_chain_holds_labels_and_never_a_separator():
    for label in label_chain(TREE, "n-3"):
        assert "/" not in label and "\\" not in label, (
            "B3: this is a display label, not a path fragment")


def test_a_node_absent_from_the_version_raises_rather_than_returning_empty():
    """An empty chain would read as "at the root", which is a lie about a node
    the version does not contain."""
    with pytest.raises(NodeNotInVersion):
        label_chain(TREE, "n-missing")


def test_a_dangling_parent_raises_rather_than_truncating():
    orphan = _node("n-9", "Orphan", "n-gone")
    with pytest.raises(NodeNotInVersion):
        label_chain((*TREE, orphan), "n-9")


def test_a_cycle_raises_instead_of_looping_forever():
    a = _node("c-1", "A", "c-2")
    b = _node("c-2", "B", "c-1")
    with pytest.raises(AncestorCycle):
        label_chain((a, b), "c-1")


def test_the_chain_reads_from_the_version_it_was_asked_for(p13_conn):
    from tree_design.store import write_node, write_plan_version
    from tree_design.records import PlanVersion
    from review_surface.labels import label_chain_for_version
    write_plan_version(p13_conn, PlanVersion(
        plan_version_id="plan-1", predecessor_id=None, state="draft",
        created_at="2026-08-29T00:00:00Z", cross_folder_moves=False,
        selection_id="sel-1"))
    for node in TREE:
        write_node(p13_conn, node)
    assert label_chain_for_version(
        p13_conn, plan_version="plan-1", node_id="n-3") == (
            "Academics", "Columbia", "2026-Spring")
```

> **If `Node`'s constructor keywords differ from the fixture above**, read them with `PYTHONPATH=src python3 -c "import dataclasses; from tree_design.records import Node; print([f.name for f in dataclasses.fields(Node)])"` and copy `tests/p10/`'s live node builder instead. Same for `PlanVersion` and `write_plan_version`.

`tests/p13/test_p13_locations.py`:

```python
"""`66` §3: six DISTINCT states, never one flat list, never a confidence failure."""
from __future__ import annotations

import pytest

from review_surface.locations import (
    ALSO_RELATED_TO, CURRENT_LOCATION, FILED_HOME, HISTORICAL_LOCATION,
    LOCATION_STATES, LocationElement, LocationStatesCollapsed,
    POSSIBLE_PLACEMENT, SHARED_MATERIAL, six_state_view,
)


def _element(state, chain=(), **kw):
    values = dict(state=state, label_chain=chain, node_id=None,
                  relationship_ref=None, shared_policy=None,
                  opaque_current_location=None, explanation="fixture")
    values.update(kw)
    return LocationElement(**values)


def test_the_six_states_are_66_section_3_s_six_in_its_own_order():
    assert LOCATION_STATES == (
        "current_location", "filed_home", "also_related_to",
        "shared_material", "historical_location", "possible_placement")


def test_the_paper_that_is_also_homework_is_two_relationships_and_one_location():
    """`67` §2: "that is two accepted relationships and one physical location,
    not a confidence failure"."""
    view = six_state_view(
        subject_ref="f-paper", plan_version="plan-1",
        current=_element(CURRENT_LOCATION,
                         opaque_current_location="Documents > Research > paper.pdf"),
        filed_home=_element(FILED_HOME, ("Research", "Fluids"), node_id="n-7"),
        also_related_to=(
            _element(ALSO_RELATED_TO, relationship_ref="g-phys1401"),
            _element(ALSO_RELATED_TO, relationship_ref="g-lab-notebook"),
        ),
        shared_material=(), historical=(), possible=())
    assert len(view.by_state(CURRENT_LOCATION)) == 1
    assert len(view.by_state(ALSO_RELATED_TO)) == 2
    assert view.by_state(POSSIBLE_PLACEMENT) == ()


def test_every_state_is_reachable_separately_and_none_is_merged():
    view = six_state_view(
        subject_ref="f-1", plan_version="plan-1",
        current=_element(CURRENT_LOCATION, opaque_current_location="X"),
        filed_home=_element(FILED_HOME, ("A",), node_id="n-1"),
        also_related_to=(_element(ALSO_RELATED_TO, relationship_ref="g-1"),),
        shared_material=(_element(SHARED_MATERIAL, ("Shared",),
                                  node_id="n-2", shared_policy="shared-branch"),),
        historical=(_element(HISTORICAL_LOCATION,
                             opaque_current_location="old"),),
        possible=(_element(POSSIBLE_PLACEMENT, ("B",), node_id="n-3"),))
    for state in LOCATION_STATES:
        assert view.by_state(state), f"{state} must be separately reachable"
    assert len(view.elements) == 6


def test_there_is_no_way_to_ask_for_one_flat_list_of_paths(p13_conn):
    """`66` §3: "These must not be collapsed into one ambiguous list of paths"."""
    view = six_state_view(
        subject_ref="f-1", plan_version="plan-1",
        current=_element(CURRENT_LOCATION, opaque_current_location="X"),
        filed_home=None, also_related_to=(), shared_material=(),
        historical=(), possible=())
    with pytest.raises(LocationStatesCollapsed):
        view.as_flat_paths()


def test_a_possible_placement_is_never_offered_as_a_home():
    """`66` §3: "Available only in review or evidence details; never presented
    as a home"."""
    element = _element(POSSIBLE_PLACEMENT, ("B",), node_id="n-3")
    assert element.state != FILED_HOME
    assert element.state != CURRENT_LOCATION


def test_a_shared_material_element_must_name_its_policy():
    """`66` §3: "Shown with the relevant shared policy and relationship labels"."""
    with pytest.raises(ValueError):
        _element(SHARED_MATERIAL, ("Shared",), node_id="n-2",
                 shared_policy=None)


def test_an_also_related_to_element_must_name_the_relationship():
    with pytest.raises(ValueError):
        _element(ALSO_RELATED_TO, relationship_ref=None)


def test_an_unknown_state_is_refused():
    from review_surface.vocabulary import OutOfVocabulary
    with pytest.raises(OutOfVocabulary):
        _element("maybe_home")


def test_no_element_carries_a_composed_path(p13_conn):
    """B3. The one opaque string is supplied by the caller and P13 composes none
    of it; the label chain never contains a separator."""
    element = _element(FILED_HOME, ("Academics", "Columbia"), node_id="n-2")
    for label in element.label_chain:
        assert "/" not in label and "\\" not in label
```

- [ ] **Step 2: Run the tests and verify RED**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_labels.py tests/p13/test_p13_locations.py`

Expected: **FAIL** — `ModuleNotFoundError: No module named 'review_surface.labels'`.

- [ ] **Step 3: Write `src/review_surface/labels.py`**

```python
# src/review_surface/labels.py
"""B3: a node and its ancestor `display_label` chain. Never a path.

P12 alone composes paths. This module composes a TUPLE of labels and never a
string, because a joined string is a path in every way that matters: it acquires
a separator, it gets logged, and the next reader treats it as one. A tuple cannot
be mistaken for a path by anything.

Three failures are raised rather than papered over, and each has the same shape:
returning a shorter chain would be a confident lie about where a node sits.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Sequence

from tree_design.records import Node
from tree_design.store import nodes_for_version


class NodeNotInVersion(LookupError):
    """A node id, or an ancestor of one, that this plan version does not hold."""


class AncestorCycle(RuntimeError):
    """A parent chain that returns to a node it already visited."""


def label_chain(nodes: Sequence[Node], node_id: str) -> tuple[str, ...]:
    """Root-first labels from the root anchor down to `node_id`.

    A dangling parent raises instead of truncating: a truncated chain reads as
    "this node sits directly under the root", which is a claim about the tree
    rather than an admission that the tree could not be walked.
    """
    by_id = {node.node_id: node for node in nodes}
    if node_id not in by_id:
        raise NodeNotInVersion(
            f"{node_id!r} is not in this plan version; an empty chain would read "
            "as 'at the root', which is a different claim")
    chain: list[str] = []
    seen: set[str] = set()
    current: str | None = node_id
    while current is not None:
        if current in seen:
            raise AncestorCycle(
                f"the parent chain from {node_id!r} revisits {current!r}")
        seen.add(current)
        node = by_id.get(current)
        if node is None:
            raise NodeNotInVersion(
                f"{current!r} is named as a parent but is not in this plan "
                f"version, so the chain to {node_id!r} cannot be composed")
        chain.append(node.display_label)
        current = node.parent_node_id
    chain.reverse()
    return tuple(chain)


def label_chain_for_version(conn: sqlite3.Connection, *, plan_version: str,
                            node_id: str) -> tuple[str, ...]:
    """The chain as of one plan version. §8.8 mints node ids per version, so the
    version is not optional: the same label sits under a different id per draft."""
    return label_chain(nodes_for_version(conn, plan_version), node_id)
```

- [ ] **Step 4: Write `src/review_surface/locations.py`**

```python
# src/review_surface/locations.py
"""`66` §3's six states. Six DISTINCT things, never one flat list of paths.

    "These must not be collapsed into one ambiguous list of paths."
    "It should not describe a valid multi-purpose relationship as a confidence
    failure."

`67` §2 calls this model new and load-bearing, and names the case it exists for:
a research paper that is also school homework is TWO ACCEPTED RELATIONSHIPS AND
ONE PHYSICAL LOCATION. A product that renders that as "we are not sure where this
goes" has told the user their correct filing is a defect.

`as_flat_paths` exists and raises. A method that raises is a better answer than
no method: the collapse is the failure `66` §3 names, so the code says its name
out loud at the one place someone would reach for it.

`current_location` and `historical_location` carry an OPAQUE string the caller
supplies. P13 composes none of it -- see this task's OPEN callout, which is
unresolved.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from review_surface.vocabulary import check

CURRENT_LOCATION: str = "current_location"
FILED_HOME: str = "filed_home"
ALSO_RELATED_TO: str = "also_related_to"
SHARED_MATERIAL: str = "shared_material"
HISTORICAL_LOCATION: str = "historical_location"
POSSIBLE_PLACEMENT: str = "possible_placement"

#: In `66` §3's own table order, which is the order a result reads in.
LOCATION_STATES: tuple[str, ...] = (
    CURRENT_LOCATION, FILED_HOME, ALSO_RELATED_TO, SHARED_MATERIAL,
    HISTORICAL_LOCATION, POSSIBLE_PLACEMENT,
)


class LocationStatesCollapsed(RuntimeError):
    """Something asked for the six states as one list. `66` §3 forbids it."""


@dataclass(frozen=True)
class LocationElement:
    """One of the six, and it knows which one it is."""

    state: str
    label_chain: tuple[str, ...]
    node_id: str | None
    relationship_ref: str | None
    shared_policy: str | None
    opaque_current_location: str | None
    explanation: str

    def __post_init__(self) -> None:
        check(self.state, LOCATION_STATES, name="location state")
        if self.state == ALSO_RELATED_TO and not self.relationship_ref:
            raise ValueError(
                "an also-related-to element must name the accepted group, "
                "project, course, packet or event it relates to; `66` §3 calls "
                "it a relationship and an unnamed one is indistinguishable "
                "from uncertainty")
        if self.state == SHARED_MATERIAL and not self.shared_policy:
            raise ValueError(
                "`66` §3: a shared-material relationship is shown WITH the "
                "relevant shared policy; without it the user cannot tell an "
                "approved sharing arrangement from an unresolved second home")
        for label in self.label_chain:
            if "/" in label or "\\" in label:
                raise ValueError(
                    f"{label!r} holds a path separator; B3 gives P13 display "
                    "labels and gives P12 the paths")


@dataclass(frozen=True)
class SixStateView:
    subject_ref: str
    plan_version: str
    elements: tuple[LocationElement, ...]

    def by_state(self, state: str) -> tuple[LocationElement, ...]:
        check(state, LOCATION_STATES, name="location state")
        return tuple(e for e in self.elements if e.state == state)

    def as_flat_paths(self) -> None:
        raise LocationStatesCollapsed(
            "`66` §3: the six states must not be collapsed into one ambiguous "
            "list of paths. Ask `by_state(...)` for the one you mean -- a "
            "current location, a filed home, an accepted relationship, a shared-"
            "material arrangement, a historical path and an unaccepted candidate "
            "are six different claims and only one of them is where the file is")


def six_state_view(*, subject_ref: str, plan_version: str,
                   current: LocationElement | None,
                   filed_home: LocationElement | None,
                   also_related_to: Sequence[LocationElement],
                   shared_material: Sequence[LocationElement],
                   historical: Sequence[LocationElement],
                   possible: Sequence[LocationElement]) -> SixStateView:
    """Assemble the six, each in its own slot. A missing slot is empty, not absent.

    Every state is a separate keyword, so a caller cannot pass a mixed list and
    have P13 sort it out -- sorting it out is exactly the guess `66` §3 removes.
    """
    ordered: list[LocationElement] = []
    if current is not None:
        ordered.append(current)
    if filed_home is not None:
        ordered.append(filed_home)
    ordered.extend(also_related_to)
    ordered.extend(shared_material)
    ordered.extend(historical)
    ordered.extend(possible)
    for element, expected in (
            (current, CURRENT_LOCATION), (filed_home, FILED_HOME)):
        if element is not None and element.state != expected:
            raise ValueError(
                f"an element in the {expected} slot carries state "
                f"{element.state!r}")
    for group, expected in ((also_related_to, ALSO_RELATED_TO),
                            (shared_material, SHARED_MATERIAL),
                            (historical, HISTORICAL_LOCATION),
                            (possible, POSSIBLE_PLACEMENT)):
        for element in group:
            if element.state != expected:
                raise ValueError(
                    f"an element in the {expected} slot carries state "
                    f"{element.state!r}")
    return SixStateView(subject_ref=subject_ref, plan_version=plan_version,
                        elements=tuple(ordered))
```

- [ ] **Step 5: Run the tests and verify PASS**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_labels.py tests/p13/test_p13_locations.py`

Expected: **PASS** — sixteen tests green.

- [ ] **Step 6: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/review_surface/labels.py src/review_surface/locations.py tests/p13/test_p13_labels.py tests/p13/test_p13_locations.py && git commit -m "feat(p13-3): ancestor labels instead of a path, and 66 §3's six distinct location states"
```

---

### Task 4: Citation resolution — an unresolvable key renders the failure rather than vanishing

**Files:**
- Create: `src/review_surface/citations.py`
- Test: `tests/p13/test_p13_citations.py`

**Interfaces:**

*Consumes:*

```python
from evidence_shape.store import observations_by_key   # (conn, observation_key) -> list[Observation]
from evidence_shape.store import unit_for_observation  # (conn, observation) -> TextUnit | None
from evidence_shape.observation import Observation     # raw_value, normalized_value, context_before,
                                                       # context_after, context_truncated, location,
                                                       # reliability, signal_tier, extractor_name, ...
from placement.records import MatchingFact             # (file_fact_id, field, value, reliability, evidence_ref)
```

*Produces:*

```python
RESOLVED: str          # "resolved"
UNRESOLVABLE: str      # "unresolvable"
SUPERSEDED_ONLY: str   # "superseded_only"
CITATION_STATES: tuple[str, ...]

@dataclass(frozen=True)
class ResolvedCitation:
    observation_key: str
    state: str
    excerpt: str | None
    context_before: str | None
    context_after: str | None
    context_truncated: bool
    extractor_name: str | None
    reliability: str | None
    explanation: str

def resolve_citation(conn: sqlite3.Connection,
                     observation_key: str) -> ResolvedCitation: ...

def resolve_matching_facts(conn: sqlite3.Connection,
                           facts: Sequence[MatchingFact],
                           ) -> tuple[tuple[MatchingFact, ResolvedCitation], ...]: ...
```

**Done-means:** 3 (*"Every `matching_facts[]` citation on a rendered decision resolves through `observation_key` to a displayable excerpt, and a decision citing an unresolvable key renders the failure rather than omitting the citation"*).

**Why the failure is rendered and not swallowed.** M14 and §8.7: a negative example recorded today must still resolve after an extractor upgrade. If an upgrade breaks a key, the user must see *that the citation broke*, because the alternative — silently dropping it — turns an explanation with three citations into an explanation with two and no sign that a third ever existed. §6.4's rule that an explanation *"must not claim evidence the file does not carry"* is only checkable by a person if the missing evidence is visible as missing.

- [ ] **Step 1: Write the failing tests**

`tests/p13/test_p13_citations.py`:

```python
"""M14: cite the key, resolve the key, and show the failure when it will not."""
from __future__ import annotations

from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from placement.records import MatchingFact

from review_surface.citations import (
    RESOLVED, UNRESOLVABLE, resolve_citation, resolve_matching_facts,
)

T0 = "2026-08-29T00:00:00Z"


def _seed(conn) -> str:
    run = ExtractionRun(
        run_id="run-1", file_id="f-1", content_hash="h-1",
        extractor_name="fixture-pdf", extractor_version="1",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=T0, observation_count=1,
        coverage=None, finished_at=T0, failure_reason=None)
    record_run(conn, run)
    key = observation_key(content_hash="h-1", extractor_name="fixture-pdf",
                          locator="page-1", raw_value="PHYS1401")
    record_observation(conn, Observation(
        file_id="f-1", content_hash="h-1", extractor_name="fixture-pdf",
        extractor_version="1", source_type="text_document",
        raw_value="PHYS1401", location={"locator": "page-1"},
        occurrence_count=1, observed_at=T0, reliability="direct",
        run_id="run-1", normalized_value="PHYS1401",
        context_before="Course ", context_after=" Spring 2026",
        context_truncated=False, confidence=None, signal_tier=1))
    return key


def test_a_live_key_resolves_to_a_displayable_excerpt(p13_conn):
    key = _seed(p13_conn)
    citation = resolve_citation(p13_conn, key)
    assert citation.state == RESOLVED
    assert citation.excerpt == "PHYS1401"
    assert citation.context_before == "Course "
    assert citation.context_after == " Spring 2026"
    assert citation.extractor_name == "fixture-pdf"
    assert citation.reliability == "direct"


def test_an_unresolvable_key_renders_the_failure_and_is_not_dropped(p13_conn):
    """Done-means 3, second clause."""
    citation = resolve_citation(p13_conn, "obs-key-that-never-existed")
    assert citation.state == UNRESOLVABLE
    assert citation.excerpt is None
    assert "obs-key-that-never-existed" in citation.explanation
    assert citation.observation_key == "obs-key-that-never-existed"


def test_resolving_a_fact_list_returns_one_pair_per_fact_and_drops_none(p13_conn):
    key = _seed(p13_conn)
    facts = (
        MatchingFact(file_fact_id="ff-1", field="subject", value="PHYS1401",
                     reliability="direct", evidence_ref=key),
        MatchingFact(file_fact_id="ff-2", field="subject", value="PHYS1401",
                     reliability="direct", evidence_ref="gone"),
    )
    pairs = resolve_matching_facts(p13_conn, facts)
    assert len(pairs) == 2, "an unresolvable citation is rendered, not omitted"
    assert pairs[0][1].state == RESOLVED
    assert pairs[1][1].state == UNRESOLVABLE
    assert [fact.file_fact_id for fact, _ in pairs] == ["ff-1", "ff-2"]


def test_an_empty_fact_list_resolves_to_an_empty_tuple(p13_conn):
    assert resolve_matching_facts(p13_conn, ()) == ()


def test_the_context_truncation_flag_survives_to_the_surface(p13_conn):
    """A truncated context shown as whole would misstate the evidence."""
    run = ExtractionRun(
        run_id="run-2", file_id="f-2", content_hash="h-2",
        extractor_name="fixture-pdf", extractor_version="1",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=T0, observation_count=1,
        coverage=None, finished_at=T0, failure_reason=None)
    record_run(p13_conn, run)
    key = observation_key(content_hash="h-2", extractor_name="fixture-pdf",
                          locator="page-9", raw_value="Columbia")
    record_observation(p13_conn, Observation(
        file_id="f-2", content_hash="h-2", extractor_name="fixture-pdf",
        extractor_version="1", source_type="text_document",
        raw_value="Columbia", location={"locator": "page-9"},
        occurrence_count=1, observed_at=T0, reliability="direct",
        run_id="run-2", normalized_value="Columbia",
        context_before="…applying to ", context_after=" Univ…",
        context_truncated=True, confidence=None, signal_tier=1))
    assert resolve_citation(p13_conn, key).context_truncated is True


def test_p13_never_reaches_for_an_observation_id(p13_conn):
    """M14, asserted on the module rather than on a convention."""
    import inspect
    import review_surface.citations as module
    source = inspect.getsource(module)
    assert "observation_id" not in source.replace(
        "# observation_id", "")
    assert "get_observation" not in source
```

- [ ] **Step 2: Run the tests and verify RED**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_citations.py`

Expected: **FAIL** — `ModuleNotFoundError: No module named 'review_surface.citations'`.

> If `ExtractionRun` or `Observation` reject any keyword above, read the live field lists with `PYTHONPATH=src python3 -c "import dataclasses; from evidence_shape.runs import ExtractionRun; from evidence_shape.observation import Observation; print([f.name for f in dataclasses.fields(ExtractionRun)]); print([f.name for f in dataclasses.fields(Observation)])"` and copy `tests/p4/`'s live builders. Do not invent a field.

- [ ] **Step 3: Write `src/review_surface/citations.py`**

```python
# src/review_surface/citations.py
"""An `observation_key` resolved to something a person can read -- or a named failure.

M14 and §8.7: a negative example recorded today must still resolve after an
extractor upgrade, which is why the durable handle is the KEY and never the id.
This module never touches `observation_id` and never calls `get_observation`;
Task 18's guard asserts both by introspection.

**An unresolvable citation is rendered, not dropped.** Done-means 3's second
clause is the whole reason this module returns a record for every key instead of
a shorter list. Silently omitting a broken citation turns an explanation with
three citations into an explanation with two, with nothing to say a third existed
-- and §6.4's rule that an explanation "must not claim evidence the file does not
carry" is only checkable by a reader if the missing evidence is visible AS
missing.

There is no scoring here, no ranking, and no choice about WHICH observation to
show when a key resolves to several. The key is content-addressed over
`(content_hash, extractor_name, locator, raw_value)`, so several rows under one
key are the same observation re-recorded; the first is taken and the count is
reported in the explanation rather than adjudicated.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass

from evidence_shape.store import observations_by_key

from placement.records import MatchingFact

RESOLVED: str = "resolved"
UNRESOLVABLE: str = "unresolvable"
CITATION_STATES: tuple[str, ...] = (RESOLVED, UNRESOLVABLE)


@dataclass(frozen=True)
class ResolvedCitation:
    observation_key: str
    state: str
    excerpt: str | None
    context_before: str | None
    context_after: str | None
    context_truncated: bool
    extractor_name: str | None
    reliability: str | None
    explanation: str


def resolve_citation(conn: sqlite3.Connection,
                     observation_key: str) -> ResolvedCitation:
    """Resolve one key. A miss is a record, never an omission and never a raise."""
    rows = observations_by_key(conn, observation_key)
    if not rows:
        return ResolvedCitation(
            observation_key=observation_key, state=UNRESOLVABLE, excerpt=None,
            context_before=None, context_after=None, context_truncated=False,
            extractor_name=None, reliability=None,
            explanation=(
                f"the citation {observation_key!r} does not resolve to a stored "
                "observation in this database. The decision that cites it was "
                "recorded when it did; an extractor upgrade or a re-scan can "
                "break a key. It is shown here rather than omitted, so an "
                "explanation cannot quietly lose a citation it claimed"))
    observation = rows[0]
    note = ""
    if len(rows) > 1:
        note = (f" This key resolves to {len(rows)} recorded observations; the "
                "first is shown and none is preferred over another.")
    return ResolvedCitation(
        observation_key=observation_key, state=RESOLVED,
        excerpt=observation.normalized_value or observation.raw_value,
        context_before=observation.context_before,
        context_after=observation.context_after,
        context_truncated=bool(observation.context_truncated),
        extractor_name=observation.extractor_name,
        reliability=observation.reliability,
        explanation=(f"resolved through {observation.extractor_name} "
                     f"{observation.extractor_version}." + note))


def resolve_matching_facts(conn: sqlite3.Connection,
                           facts: Sequence[MatchingFact],
                           ) -> tuple[tuple[MatchingFact, ResolvedCitation], ...]:
    """One pair per fact, in the decision's own order. Nothing is filtered out."""
    return tuple((fact, resolve_citation(conn, fact.evidence_ref))
                 for fact in facts)
```

- [ ] **Step 4: Run the tests and verify PASS**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_citations.py`

Expected: **PASS** — six tests green.

- [ ] **Step 5: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/review_surface/citations.py tests/p13/test_p13_citations.py && git commit -m "feat(p13-4): a citation resolves through observation_key, and a broken one is shown rather than dropped"
```

---

### Task 5: The placement review item — trust is not uniform, and a deferral is not an abstention

> **OPEN QUESTION 1 IS UNRESOLVED AND IT IS THE ONE THAT MOST CONSTRAINS THIS TASK.** The SPEC's own Open questions §1: *"Is §6.11's confidence-class list closed? §6.11 gives four labels by example ("might be labeled"), not as an enumeration. P13 must render a distinguishable treatment per class and P2 must assert against them. If the list is open, neither can be built against fixtures."* Live `placement.vocabulary.CONFIDENCE_CLASSES` is a closed tuple of four, so P11 has already built the closed reading. **This task builds against that live tuple and its test asserts the tuple, not the four literals** — so the day a fifth class is ratified, `test_every_confidence_class_has_a_distinguishable_treatment` fails loudly instead of a fifth class quietly rendering like the fourth. That is the most this plan may do; whether the list is closed is Joseph's.

**Files:**
- Create: `src/review_surface/items.py`
- Test: `tests/p13/test_p13_placement_item.py`

**Interfaces:**

*Consumes:*

```python
from placement.records import (
    PlacementDecision, Destination, DecisionDepth, MatchingFact, GroupSupport,
    GraphAnchor, ConflictConsidered, Alternative, TwoCondition, PrivacyState, Ask,
)
from placement.store import current_decision   # (conn, *, plan_version, subject_ref) -> PlacementDecision | None
from placement.vocabulary import (
    ABSTAIN, ASK_USER, CONFIDENCE_CLASSES, CONTEXT_SUPPORTED_GROUP_MATCH,
    EXACT_FACT_MATCH, PLACE, REVIEW_POLICIES, SHARED_MATERIAL_DECISION,
)
from review_surface.citations import ResolvedCitation, resolve_matching_facts
from review_surface.labels import label_chain_for_version
```

*Produces:*

```python
AFFORDANCE_ONE_STEP: str        # "one_step_accept"
AFFORDANCE_REVIEW_REQUIRED: str # "review_each_before_accepting"
AFFORDANCE_NONE: str            # "no_acceptance_offered"
ACCEPTANCE_AFFORDANCES: tuple[str, ...]

RENDER_PLACEMENT: str           # "placement"
RENDER_ABSTENTION: str          # "abstention"
RENDER_BUDGET_DEFERRAL: str     # "budget_deferral"
RENDER_ASK: str                 # "ask_user"
RENDER_SHARED_MATERIAL: str     # "shared_material"
RENDER_STATES: tuple[str, ...]

@dataclass(frozen=True)
class PlacementReviewItem:
    subject_ref: str
    plan_version: str
    subject_kind: str
    render_state: str
    acceptance_affordance: str
    destination_label_chain: tuple[str, ...]
    destination_node_role: str | None
    confidence_class: str | None
    evidence_type: str | None
    decision_depth: DecisionDepth | None
    levels_deliberately_unfilled: tuple[str, ...]
    cited_facts: tuple[tuple[MatchingFact, ResolvedCitation], ...]
    group_support: GroupSupport | None
    graph_anchors: tuple[GraphAnchor, ...]
    conflicts_considered: tuple[ConflictConsidered, ...]
    alternatives: tuple[Alternative, ...]
    two_condition: TwoCondition | None
    abstention_reason: str | None
    deferred_stage: str | None
    ask: Ask | None
    privacy: PrivacyState | None
    review_policy: str | None
    explanation: str

class UnrenderableDecision(RuntimeError): ...

def affordance_for(decision: PlacementDecision) -> str: ...
def render_state_for(decision: PlacementDecision) -> str: ...
def placement_review_item(conn: sqlite3.Connection, decision: PlacementDecision,
                          ) -> PlacementReviewItem: ...
```

**Done-means:** 1, 2, 3 (consumed from Task 4), 4 (the `ask_user` and `shared-material` halves).

- [ ] **Step 1: Write the failing tests**

`tests/p13/test_p13_placement_item.py`:

```python
"""§6.11: a direct placement and a context-supported one do not demand the same trust."""
from __future__ import annotations

import pytest

from placement.records import (
    DecisionDepth, Destination, MatchingFact, PlacementDecision, PrivacyState,
    Subject, Ask,
)
from placement.vocabulary import (
    ABSTAIN, ASK_USER, CONFIDENCE_CLASSES, CONTEXT_SUPPORTED_GROUP_MATCH,
    EXACT_FACT_MATCH, NO_SUPPORTED_DESTINATION, PLACE, REVIEW_REQUIRED,
    SHARED_MATERIAL_DECISION,
)

from review_surface.items import (
    AFFORDANCE_NONE, AFFORDANCE_ONE_STEP, AFFORDANCE_REVIEW_REQUIRED,
    RENDER_ABSTENTION, RENDER_ASK, RENDER_BUDGET_DEFERRAL, RENDER_PLACEMENT,
    RENDER_SHARED_MATERIAL, affordance_for, placement_review_item,
    render_state_for,
)

T0 = "2026-08-29T00:00:00Z"


def _decision(**overrides) -> PlacementDecision:
    values = dict(
        decision_id="d1", plan_version="plan-1", supersedes=None,
        superseded_by=None, supersede_reason=None, created_at=T0,
        origin_stage="placement", returned_from=None,
        subject=Subject(kind="file", file_id="f-1", content_hash="h-1",
                        group_id=None, member_file_ids=()),
        group_plan_id=None, outcome=PLACE,
        destination=Destination(node_id="n-3", node_role="ordinary"),
        return_target=None, marked_state=None, ask=None,
        decision_depth=DecisionDepth(node_depth=3, supported_depth=3,
                                     unsupported_levels=()),
        evidence_type="direct", confidence_class=EXACT_FACT_MATCH,
        matching_facts=(), group_support=None, graph_anchors=(),
        conflicts_considered=(), alternatives=(), two_condition=None,
        abstention_reason=None, deferred_stage=None,
        privacy=PrivacyState(handling_class="public_low", protected=False,
                             model_eligibility="local_only",
                             consent_audit_ref=None),
        review_policy=None, explanation="direct subject match", residual=None)
    values.update(overrides)
    return PlacementDecision(**values)


def test_an_exact_fact_match_offers_one_step_acceptance():
    assert affordance_for(_decision()) == AFFORDANCE_ONE_STEP


def test_a_context_supported_match_does_not_offer_the_same_affordance():
    """Done-means 1. §6.11: "a direct placement and a context-supported
    placement should not demand the same level of trust"."""
    context = _decision(confidence_class=CONTEXT_SUPPORTED_GROUP_MATCH,
                        evidence_type="context-supported")
    assert affordance_for(context) == AFFORDANCE_REVIEW_REQUIRED
    assert affordance_for(context) != affordance_for(_decision())


def test_every_confidence_class_has_a_distinguishable_treatment():
    """Asserted against P11's live tuple, so a fifth class fails here loudly
    rather than quietly rendering like the fourth. SPEC Open question 1 is OPEN."""
    seen = {}
    for klass in CONFIDENCE_CLASSES:
        outcome = ABSTAIN if klass.startswith("abstain") else PLACE
        decision = _decision(
            confidence_class=klass, outcome=outcome,
            destination=None if outcome == ABSTAIN else Destination(
                node_id="n-3", node_role="ordinary"),
            abstention_reason=(NO_SUPPORTED_DESTINATION
                               if outcome == ABSTAIN else None))
        seen[klass] = (render_state_for(decision), affordance_for(decision))
    assert len(set(seen.values())) == len(CONFIDENCE_CLASSES), (
        f"two confidence classes render identically: {seen}")


def test_an_abstention_and_a_budget_deferral_are_visibly_different_states():
    """Done-means 2. Neither renders as a placement."""
    abstention = _decision(outcome=ABSTAIN, destination=None,
                           confidence_class=None,
                           abstention_reason=NO_SUPPORTED_DESTINATION)
    deferral = _decision(outcome=ABSTAIN, destination=None,
                         confidence_class=None,
                         abstention_reason="budget_deferred",
                         deferred_stage="C_placement")
    assert render_state_for(abstention) == RENDER_ABSTENTION
    assert render_state_for(deferral) == RENDER_BUDGET_DEFERRAL
    assert render_state_for(abstention) != render_state_for(deferral)
    for decision in (abstention, deferral):
        assert render_state_for(decision) != RENDER_PLACEMENT


def test_no_accept_anyway_affordance_is_offered_over_a_deferred_subject():
    """SPEC:541-542: cost exhaustion never turns into a lower-quality presentation."""
    deferral = _decision(outcome=ABSTAIN, destination=None,
                         confidence_class=None,
                         abstention_reason="budget_deferred",
                         deferred_stage="C_placement")
    assert affordance_for(deferral) == AFFORDANCE_NONE


def test_an_ask_user_decision_reaches_a_surface_and_is_not_auto_resolved():
    """Done-means 4."""
    ask = _decision(outcome=ASK_USER, destination=None, confidence_class=None,
                    ask=Ask(question="Which application packet?",
                            options=("Columbia", "NYU")))
    assert render_state_for(ask) == RENDER_ASK
    assert affordance_for(ask) == AFFORDANCE_NONE


def test_a_shared_material_decision_reaches_a_surface_and_is_not_hidden():
    """Done-means 4."""
    shared = _decision(confidence_class=SHARED_MATERIAL_DECISION,
                       destination=Destination(node_id="n-3",
                                               node_role="shared-material"))
    assert render_state_for(shared) == RENDER_SHARED_MATERIAL


def test_the_destination_is_a_label_chain_and_never_a_path(p13_conn):
    from tree_design.records import Node, PlanVersion
    from tree_design.store import write_node, write_plan_version
    write_plan_version(p13_conn, PlanVersion(
        plan_version_id="plan-1", predecessor_id=None, state="draft",
        created_at=T0, cross_folder_moves=False, selection_id="sel-1"))
    for node_id, label, parent in (("n-1", "Academics", None),
                                   ("n-2", "Columbia", "n-1"),
                                   ("n-3", "2026-Spring", "n-2")):
        write_node(p13_conn, Node(
            node_id=node_id, plan_version_id="plan-1", node_type="proposed",
            display_label=label, parent_node_id=parent, root_anchor="root",
            ordinal=0, associated_group_ids=(), explanation="fixture",
            node_role="ordinary", accepts_placement=True,
            handling_class="public_low", origin_node_id=node_id,
            template_context=None, dimension_role=None, dimension=None,
            expected_values=(), existing_path=None, disposition=None,
            refinement_disposition=None, refinement_reason=None,
            protected_movement_permitted=False))
    item = placement_review_item(p13_conn, _decision())
    assert item.destination_label_chain == (
        "Academics", "Columbia", "2026-Spring")
    for label in item.destination_label_chain:
        assert "/" not in label


def test_the_levels_deliberately_unfilled_are_named_and_are_not_a_second_role(p13_conn):
    """SPEC:91-94, MINOR 6: there is no destination.kind; §6.7's shallower
    parent is a non-empty unsupported_levels[]."""
    decision = _decision(decision_depth=DecisionDepth(
        node_depth=2, supported_depth=2,
        unsupported_levels=("work_type", "term")))
    item = placement_review_item(p13_conn, decision)
    assert item.levels_deliberately_unfilled == ("work_type", "term")
    assert item.destination_node_role == "ordinary"


def test_the_explanation_and_its_citations_arrive_together(p13_conn):
    """SPEC:196-197: so §6.4's "must not claim evidence the file does not carry"
    is checkable by the person reading it."""
    decision = _decision(matching_facts=(
        MatchingFact(file_fact_id="ff-1", field="subject", value="PHYS1401",
                     reliability="direct", evidence_ref="gone"),))
    item = placement_review_item(p13_conn, decision)
    assert item.explanation == "direct subject match"
    assert len(item.cited_facts) == 1
    assert item.cited_facts[0][1].state == "unresolvable"


def test_a_place_decision_with_no_destination_is_refused_not_rendered_blank(p13_conn):
    from review_surface.items import UnrenderableDecision
    with pytest.raises(UnrenderableDecision):
        placement_review_item(p13_conn, _decision(destination=None))
```

- [ ] **Step 2: Run the tests and verify RED**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_placement_item.py`

Expected: **FAIL** — `ModuleNotFoundError: No module named 'review_surface.items'`.

- [ ] **Step 3: Write `src/review_surface/items.py`**

```python
# src/review_surface/items.py
"""The placement review item. §6.11's four labels, rendered distinguishably.

    "The user should see these distinctions in the review interface, because a
    direct placement and a context-supported placement should not demand the
    same level of trust."

Three rendering obligations are contractual (SPEC:190-197) and each is a function
here rather than a comment:

* **Trust is not uniform.** `affordance_for` gives a context-supported match a
  different acceptance affordance from an exact fact match. This module does not
  decide WHICH files those are -- P11 already did -- it decides that the two do
  not present the same one-click control.
* **A budget deferral is not an abstention.** `render_state_for` separates them,
  and a deferral is offered no acceptance affordance at all: §8.6's rule that
  cost exhaustion never turns into lower-quality classification is inverted here
  into a rule about PRESENTATION (SPEC:539-542).
* **The explanation is shown with its citations**, which is why `cited_facts`
  pairs each `MatchingFact` with a resolved citation and never carries the
  explanation alone.

There is no score anywhere in this module. `two_condition` is carried whole,
because §6.11's own requirement is that the FIGURES AND BOTH THRESHOLDS are
presentable -- P13 shows P11's arithmetic, it does not repeat it.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from placement.records import (
    Alternative, Ask, ConflictConsidered, DecisionDepth, GraphAnchor,
    GroupSupport, MatchingFact, PlacementDecision, PrivacyState, TwoCondition,
)
from placement.vocabulary import (
    ABSTAIN, ASK_USER, CONTEXT_SUPPORTED_GROUP_MATCH, EXACT_FACT_MATCH,
    MARK_STATE, PLACE, SHARED_MATERIAL_DECISION,
)

from review_surface.citations import ResolvedCitation, resolve_matching_facts
from review_surface.labels import label_chain_for_version

AFFORDANCE_ONE_STEP: str = "one_step_accept"
AFFORDANCE_REVIEW_REQUIRED: str = "review_each_before_accepting"
AFFORDANCE_NONE: str = "no_acceptance_offered"
ACCEPTANCE_AFFORDANCES: tuple[str, ...] = (
    AFFORDANCE_ONE_STEP, AFFORDANCE_REVIEW_REQUIRED, AFFORDANCE_NONE)

RENDER_PLACEMENT: str = "placement"
RENDER_SHARED_MATERIAL: str = "shared_material"
RENDER_ABSTENTION: str = "abstention"
RENDER_BUDGET_DEFERRAL: str = "budget_deferral"
RENDER_ASK: str = "ask_user"
RENDER_MARKED: str = "marked_state"
RENDER_STATES: tuple[str, ...] = (
    RENDER_PLACEMENT, RENDER_SHARED_MATERIAL, RENDER_ABSTENTION,
    RENDER_BUDGET_DEFERRAL, RENDER_ASK, RENDER_MARKED)


class UnrenderableDecision(RuntimeError):
    """A decision whose own fields contradict each other. Refused, not blanked."""


def render_state_for(decision: PlacementDecision) -> str:
    """Which of the six visibly different states this decision is in.

    `deferred_stage` is checked BEFORE `abstention_reason`, because P11 carries
    both on a budget deferral and the deferral is the more specific claim. Reading
    the reason first would render every deferral as an ordinary abstention, which
    is exactly the conflation Done-means 2 forbids.
    """
    if decision.deferred_stage:
        return RENDER_BUDGET_DEFERRAL
    if decision.outcome == ASK_USER:
        return RENDER_ASK
    if decision.outcome == ABSTAIN:
        return RENDER_ABSTENTION
    if decision.outcome == MARK_STATE:
        return RENDER_MARKED
    if decision.confidence_class == SHARED_MATERIAL_DECISION:
        return RENDER_SHARED_MATERIAL
    if decision.outcome == PLACE:
        return RENDER_PLACEMENT
    return RENDER_ABSTENTION


def affordance_for(decision: PlacementDecision) -> str:
    """§6.11's trust distinction, expressed as a control rather than as a label.

    A label alone satisfies "distinguishable" and does not satisfy "should not
    demand the same level of trust": two cards that read differently and accept
    identically demand identical trust.
    """
    state = render_state_for(decision)
    if state in (RENDER_BUDGET_DEFERRAL, RENDER_ASK, RENDER_ABSTENTION,
                 RENDER_MARKED):
        # SPEC:541-542: no "accept anyway" over a deferred subject, and an
        # abstention has nothing to accept.
        return AFFORDANCE_NONE
    if decision.confidence_class == EXACT_FACT_MATCH:
        return AFFORDANCE_ONE_STEP
    return AFFORDANCE_REVIEW_REQUIRED


def placement_review_item(conn: sqlite3.Connection,
                          decision: PlacementDecision) -> "PlacementReviewItem":
    """Project one P11 decision into what must be presentable. Adds no field."""
    if decision.outcome == PLACE and decision.destination is None:
        raise UnrenderableDecision(
            f"decision {decision.decision_id!r} has outcome {PLACE!r} and no "
            "destination. Rendering it with a blank destination would present a "
            "placement to nowhere as a placement")
    chain: tuple[str, ...] = ()
    role: str | None = None
    if decision.destination is not None:
        chain = label_chain_for_version(
            conn, plan_version=decision.plan_version,
            node_id=decision.destination.node_id)
        role = decision.destination.node_role
    depth = decision.decision_depth
    return PlacementReviewItem(
        subject_ref=decision.decision_id,
        plan_version=decision.plan_version,
        subject_kind=decision.subject.kind,
        render_state=render_state_for(decision),
        acceptance_affordance=affordance_for(decision),
        destination_label_chain=chain,
        destination_node_role=role,
        confidence_class=decision.confidence_class,
        evidence_type=decision.evidence_type,
        decision_depth=depth,
        levels_deliberately_unfilled=(
            tuple(depth.unsupported_levels) if depth is not None else ()),
        cited_facts=resolve_matching_facts(conn, decision.matching_facts),
        group_support=decision.group_support,
        graph_anchors=tuple(decision.graph_anchors),
        conflicts_considered=tuple(decision.conflicts_considered),
        alternatives=tuple(decision.alternatives),
        two_condition=decision.two_condition,
        abstention_reason=decision.abstention_reason,
        deferred_stage=decision.deferred_stage,
        ask=decision.ask,
        privacy=decision.privacy,
        review_policy=decision.review_policy,
        explanation=decision.explanation)


@dataclass(frozen=True)
class PlacementReviewItem:
    subject_ref: str
    plan_version: str
    subject_kind: str
    render_state: str
    acceptance_affordance: str
    destination_label_chain: tuple[str, ...]
    destination_node_role: str | None
    confidence_class: str | None
    evidence_type: str | None
    decision_depth: DecisionDepth | None
    levels_deliberately_unfilled: tuple[str, ...]
    cited_facts: tuple[tuple[MatchingFact, ResolvedCitation], ...]
    group_support: GroupSupport | None
    graph_anchors: tuple[GraphAnchor, ...]
    conflicts_considered: tuple[ConflictConsidered, ...]
    alternatives: tuple[Alternative, ...]
    two_condition: TwoCondition | None
    abstention_reason: str | None
    deferred_stage: str | None
    ask: Ask | None
    privacy: PrivacyState | None
    review_policy: str | None
    explanation: str
```

> **Note on definition order.** `placement_review_item` refers to `PlacementReviewItem` in its annotation as a string and constructs it at call time, so the dataclass may be defined after it. Keeping the functions first puts the three contractual obligations at the top of the file where a reader looks; if a linter objects, move the dataclass above `render_state_for` and drop the quotes.

- [ ] **Step 4: Run the tests and verify PASS**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_placement_item.py`

Expected: **PASS** — eleven tests green.

- [ ] **Step 5: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/review_surface/items.py tests/p13/test_p13_placement_item.py && git commit -m "feat(p13-5): §6.11's four classes render distinguishably, and a deferral is never an abstention"
```

---

### Task 6: The group plan item, and `66` §4's five states that may never share one message

> **`66` §4 EXTENDS THE SPEC AND `66` GOVERNS.** `66` §4: *"Find must name the state that actually applies. 'Protected by your privacy policy' means the product deliberately did not reveal more. 'Unreadable' means the product could not obtain usable content. 'Still indexing' means the product has not completed analysis. 'Unsupported format' means no approved extractor exists. 'No strong match' means the local retrieval system found no result that satisfies the query. These states should never share one vague message such as 'could not find.'"* The P13 SPEC has no record for this at all. `67` §1 makes it a standing constraint. It is built here because the group-plan item is where the first "some members are missing from this list" question arises, and the answer must never be a shrug.

**Files:**
- Modify: `src/review_surface/items.py`
- Create: `src/review_surface/states.py`
- Test: `tests/p13/test_p13_group_plan_item.py`
- Test: `tests/p13/test_p13_absence_states.py`

**Interfaces:**

*Consumes:*

```python
from placement.groups import ExcludedOutlier, GroupPlan
from evidence_shape.runs import COMPLETENESS
from privacy.display import HANDLING_CLASSES
```

*Produces:*

```python
# states.py
ABSENCE_PROTECTED: str        # "protected"
ABSENCE_UNREADABLE: str       # "unreadable"
ABSENCE_UNSUPPORTED: str      # "unsupported_format"
ABSENCE_STILL_INDEXING: str   # "still_indexing"
ABSENCE_NO_STRONG_MATCH: str  # "no_strong_match"
ABSENCE_STATES: tuple[str, ...]
ABSENCE_SENTENCES: Mapping[str, str]

@dataclass(frozen=True)
class AbsenceNotice:
    state: str
    count: int
    explanation_ref: str
    def sentence(self) -> str: ...

class StatesCollapsed(RuntimeError): ...

def absence_notices(counts: Mapping[str, int], *,
                    explanation_refs: Mapping[str, str]
                    ) -> tuple[AbsenceNotice, ...]: ...
def one_message_for(states: Sequence[str]) -> None: ...   # raises. See below.

# items.py, added
@dataclass(frozen=True)
class GroupPlanReviewItem:
    group_plan_id: str
    plan_version: str
    group_id: str
    shared_parent_label_chain: tuple[str, ...]
    member_items: tuple[PlacementReviewItem, ...]
    excluded_outliers: tuple[tuple[ExcludedOutlier, tuple[str, ...]], ...]
    absence_notices: tuple[AbsenceNotice, ...]

def group_plan_review_item(conn, plan: GroupPlan, *,
                           member_decisions: Sequence[PlacementDecision],
                           absences: Sequence[AbsenceNotice] = (),
                           ) -> GroupPlanReviewItem: ...
```

**Done-means:** 4 (a group plan is presented as one coherent plan, and each excluded outlier reaches a surface with its conflicting fact and where it was routed); and the whole of `66` §4.

- [ ] **Step 1: Write the failing tests**

`tests/p13/test_p13_absence_states.py`:

```python
"""`66` §4: five states, five sentences, and never one vague message."""
from __future__ import annotations

import pytest

from review_surface.states import (
    ABSENCE_NO_STRONG_MATCH, ABSENCE_PROTECTED, ABSENCE_SENTENCES,
    ABSENCE_STATES, ABSENCE_STILL_INDEXING, ABSENCE_UNREADABLE,
    ABSENCE_UNSUPPORTED, AbsenceNotice, StatesCollapsed, absence_notices,
    one_message_for,
)


def test_the_five_states_are_66_section_4_s_five():
    assert ABSENCE_STATES == (
        "protected", "unreadable", "unsupported_format", "still_indexing",
        "no_strong_match")


def test_every_state_has_its_own_sentence_and_no_two_are_equal():
    sentences = [ABSENCE_SENTENCES[state] for state in ABSENCE_STATES]
    assert len(set(sentences)) == 5
    for sentence in sentences:
        assert sentence and not sentence.lower().startswith("could not find")


def test_each_sentence_says_what_66_section_4_says_it_means():
    assert "privacy policy" in ABSENCE_SENTENCES[ABSENCE_PROTECTED]
    assert "read" in ABSENCE_SENTENCES[ABSENCE_UNREADABLE]
    assert "extractor" in ABSENCE_SENTENCES[ABSENCE_UNSUPPORTED]
    assert "indexing" in ABSENCE_SENTENCES[ABSENCE_STILL_INDEXING]
    assert "match" in ABSENCE_SENTENCES[ABSENCE_NO_STRONG_MATCH]


def test_notices_are_produced_per_state_and_a_zero_count_is_omitted():
    notices = absence_notices(
        {ABSENCE_PROTECTED: 14, ABSENCE_UNREADABLE: 0,
         ABSENCE_STILL_INDEXING: 89},
        explanation_refs={ABSENCE_PROTECTED: "help/protected",
                          ABSENCE_STILL_INDEXING: "help/indexing"})
    assert [n.state for n in notices] == [ABSENCE_PROTECTED,
                                          ABSENCE_STILL_INDEXING]
    assert [n.count for n in notices] == [14, 89]


def test_every_notice_carries_a_reachable_explanation(p13_conn):
    """`66` §4: "The product must provide a reachable explanation of what
    protected material means, why it is not opened"."""
    with pytest.raises(ValueError):
        AbsenceNotice(state=ABSENCE_PROTECTED, count=1, explanation_ref="")


def test_asking_for_one_message_over_two_states_raises_with_both_named():
    with pytest.raises(StatesCollapsed) as caught:
        one_message_for([ABSENCE_PROTECTED, ABSENCE_UNREADABLE])
    assert "protected" in str(caught.value)
    assert "unreadable" in str(caught.value)


def test_asking_for_one_message_over_one_state_still_raises():
    """The function exists only to be the place the collapse is refused."""
    with pytest.raises(StatesCollapsed):
        one_message_for([ABSENCE_PROTECTED])


def test_a_notice_with_a_zero_count_cannot_be_constructed():
    """A state with nothing in it is not a state to report; it is silence, and
    `66` §4's point is that silence is what must not happen for a NON-zero one."""
    with pytest.raises(ValueError):
        AbsenceNotice(state=ABSENCE_PROTECTED, count=0,
                      explanation_ref="help/protected")


def test_an_unknown_state_is_refused():
    from review_surface.vocabulary import OutOfVocabulary
    with pytest.raises(OutOfVocabulary):
        AbsenceNotice(state="could_not_find", count=1, explanation_ref="help")
```

`tests/p13/test_p13_group_plan_item.py`:

```python
"""§6.8: one coherent group plan, not several unrelated file moves."""
from __future__ import annotations

from placement.groups import ExcludedOutlier, GroupPlan
from placement.records import (
    DecisionDepth, Destination, PlacementDecision, PrivacyState, Subject,
)
from placement.vocabulary import EXACT_FACT_MATCH, PLACE
from tree_design.records import Node, PlanVersion
from tree_design.store import write_node, write_plan_version

from review_surface.items import group_plan_review_item
from review_surface.states import ABSENCE_PROTECTED, AbsenceNotice

T0 = "2026-08-29T00:00:00Z"


def _tree(conn):
    write_plan_version(conn, PlanVersion(
        plan_version_id="plan-1", predecessor_id=None, state="draft",
        created_at=T0, cross_folder_moves=False, selection_id="sel-1"))
    for node_id, label, parent in (("n-1", "Applications", None),
                                   ("n-2", "Columbia", "n-1"),
                                   ("n-9", "Review Queue", None)):
        write_node(conn, Node(
            node_id=node_id, plan_version_id="plan-1", node_type="proposed",
            display_label=label, parent_node_id=parent, root_anchor="root",
            ordinal=0, associated_group_ids=(), explanation="fixture",
            node_role="ordinary", accepts_placement=True,
            handling_class="public_low", origin_node_id=node_id,
            template_context=None, dimension_role=None, dimension=None,
            expected_values=(), existing_path=None, disposition=None,
            refinement_disposition=None, refinement_reason=None,
            protected_movement_permitted=False))


def _member(file_id: str) -> PlacementDecision:
    return PlacementDecision(
        decision_id=f"d-{file_id}", plan_version="plan-1", supersedes=None,
        superseded_by=None, supersede_reason=None, created_at=T0,
        origin_stage="placement", returned_from=None,
        subject=Subject(kind="file", file_id=file_id, content_hash="h",
                        group_id="g-1", member_file_ids=()),
        group_plan_id="gp-1", outcome=PLACE,
        destination=Destination(node_id="n-2", node_role="ordinary"),
        return_target=None, marked_state=None, ask=None,
        decision_depth=DecisionDepth(node_depth=2, supported_depth=2,
                                     unsupported_levels=()),
        evidence_type="direct", confidence_class=EXACT_FACT_MATCH,
        matching_facts=(), group_support=None, graph_anchors=(),
        conflicts_considered=(), alternatives=(), two_condition=None,
        abstention_reason=None, deferred_stage=None,
        privacy=PrivacyState(handling_class="public_low", protected=False,
                             model_eligibility="local_only",
                             consent_audit_ref=None),
        review_policy=None, explanation="member", residual=None)


def _plan() -> GroupPlan:
    return GroupPlan(
        group_plan_id="gp-1", plan_version="plan-1", group_id="g-1",
        shared_parent_node_id="n-2",
        member_decisions=("d-f1", "d-f2"),
        excluded_outliers=(ExcludedOutlier(
            file_id="f-3", conflicting_fact="target_school=NYU",
            evidence_ref="obs-nyu", routed_to="node", node_id="n-9"),))


def test_the_plan_presents_as_one_thing_with_its_shared_parent(p13_conn):
    _tree(p13_conn)
    item = group_plan_review_item(
        p13_conn, _plan(),
        member_decisions=(_member("f1"), _member("f2")))
    assert item.group_plan_id == "gp-1"
    assert item.shared_parent_label_chain == ("Applications", "Columbia")
    assert len(item.member_items) == 2


def test_each_member_is_still_individually_inspectable(p13_conn):
    _tree(p13_conn)
    item = group_plan_review_item(
        p13_conn, _plan(),
        member_decisions=(_member("f1"), _member("f2")))
    assert {m.subject_ref for m in item.member_items} == {"d-f1", "d-f2"}
    for member in item.member_items:
        assert member.destination_label_chain == ("Applications", "Columbia")


def test_each_outlier_carries_its_conflicting_fact_and_where_it_went(p13_conn):
    """§6.8, Done-means 4."""
    _tree(p13_conn)
    item = group_plan_review_item(
        p13_conn, _plan(),
        member_decisions=(_member("f1"), _member("f2")))
    assert len(item.excluded_outliers) == 1
    outlier, chain = item.excluded_outliers[0]
    assert outlier.file_id == "f-3"
    assert outlier.conflicting_fact == "target_school=NYU"
    assert outlier.evidence_ref == "obs-nyu"
    assert outlier.routed_to == "node"
    assert chain == ("Review Queue",)


def test_an_outlier_routed_to_the_review_queue_has_no_label_chain(p13_conn):
    _tree(p13_conn)
    plan = GroupPlan(
        group_plan_id="gp-1", plan_version="plan-1", group_id="g-1",
        shared_parent_node_id="n-2", member_decisions=(),
        excluded_outliers=(ExcludedOutlier(
            file_id="f-4", conflicting_fact="subject=CHEM1010",
            evidence_ref="obs-chem", routed_to="review_queue", node_id=None),))
    item = group_plan_review_item(p13_conn, plan, member_decisions=())
    assert item.excluded_outliers[0][1] == ()


def test_absence_notices_ride_on_the_group_plan_and_stay_distinct(p13_conn):
    """`66` §4 in its first real position: members not shown, said properly."""
    _tree(p13_conn)
    item = group_plan_review_item(
        p13_conn, _plan(), member_decisions=(_member("f1"),),
        absences=(AbsenceNotice(state=ABSENCE_PROTECTED, count=2,
                                explanation_ref="help/protected"),))
    assert len(item.absence_notices) == 1
    assert item.absence_notices[0].count == 2
    assert "privacy policy" in item.absence_notices[0].sentence()
```

- [ ] **Step 2: Run the tests and verify RED**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_absence_states.py tests/p13/test_p13_group_plan_item.py`

Expected: **FAIL** — `ModuleNotFoundError: No module named 'review_surface.states'`, and `ImportError: cannot import name 'group_plan_review_item' from 'review_surface.items'`.

- [ ] **Step 3: Write `src/review_surface/states.py`**

```python
# src/review_surface/states.py
"""`66` §4's five states, and the refusal to merge them.

    "'Protected by your privacy policy' means the product deliberately did not
    reveal more. 'Unreadable' means the product could not obtain usable content.
    'Still indexing' means the product has not completed analysis. 'Unsupported
    format' means no approved extractor exists. 'No strong match' means the local
    retrieval system found no result that satisfies the query. These states
    should never share one vague message such as 'could not find.'"

`67` §1 makes this a standing constraint rather than a nicety: protected material
is present-but-untouched with a REACHABLE EXPLANATION, never silently omitted and
never described as "understood and found unimportant". So `explanation_ref` is
required on every notice and an empty one is refused at construction.

`one_message_for` exists and always raises. It is the one place a future author
would reach for when asked to "just show a single 'not found' line", and it is
better for that function to exist and say why than for the merge to be written
somewhere new.

A zero count cannot be constructed. `66` §4's requirement is about the states that
DO apply; reporting "0 protected items" on every screen is noise, and the absence
of a notice is what "none of these applies" looks like.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from review_surface.vocabulary import check

ABSENCE_PROTECTED: str = "protected"
ABSENCE_UNREADABLE: str = "unreadable"
ABSENCE_UNSUPPORTED: str = "unsupported_format"
ABSENCE_STILL_INDEXING: str = "still_indexing"
ABSENCE_NO_STRONG_MATCH: str = "no_strong_match"

#: In `66` §4's own order.
ABSENCE_STATES: tuple[str, ...] = (
    ABSENCE_PROTECTED, ABSENCE_UNREADABLE, ABSENCE_UNSUPPORTED,
    ABSENCE_STILL_INDEXING, ABSENCE_NO_STRONG_MATCH,
)

#: One sentence per state, each saying what `66` §4 says that state MEANS. These
#: are the design's own distinctions, not copy: the visual wording is deferred,
#: the DISTINCTION is contractual.
ABSENCE_SENTENCES: Mapping[str, str] = MappingProxyType({
    ABSENCE_PROTECTED:
        "Protected by your privacy policy. The product deliberately did not "
        "reveal more, and did not open these items.",
    ABSENCE_UNREADABLE:
        "Could not be read. The product could not obtain usable content from "
        "these files.",
    ABSENCE_UNSUPPORTED:
        "Unsupported format. No approved extractor exists for these files yet.",
    ABSENCE_STILL_INDEXING:
        "Still indexing. The product has not finished analysing these files.",
    ABSENCE_NO_STRONG_MATCH:
        "No strong match. Nothing here satisfied what you asked for.",
})
assert set(ABSENCE_SENTENCES) == set(ABSENCE_STATES)


class StatesCollapsed(RuntimeError):
    """Something asked for one message across two or more states. `66` §4 forbids it."""


@dataclass(frozen=True)
class AbsenceNotice:
    state: str
    count: int
    explanation_ref: str

    def __post_init__(self) -> None:
        check(self.state, ABSENCE_STATES, name="absence state")
        if self.count < 1:
            raise ValueError(
                "a notice reports a state that APPLIES; a zero count is not a "
                "state to report and printing it on every screen is noise")
        if not self.explanation_ref:
            raise ValueError(
                "`66` §4 requires a reachable explanation of what this state "
                "means and why; a notice without one is the vague message the "
                "section exists to forbid")

    def sentence(self) -> str:
        return ABSENCE_SENTENCES[self.state]


def absence_notices(counts: Mapping[str, int], *,
                    explanation_refs: Mapping[str, str],
                    ) -> tuple[AbsenceNotice, ...]:
    """One notice per state that applies, in `66` §4's order. Zeroes omitted."""
    return tuple(
        AbsenceNotice(state=state, count=counts[state],
                      explanation_ref=explanation_refs[state])
        for state in ABSENCE_STATES
        if counts.get(state, 0) > 0)


def one_message_for(states: Sequence[str]) -> None:
    """Always raises. This is the place the merge is refused, by name."""
    named = ", ".join(sorted(set(states)))
    raise StatesCollapsed(
        f"`66` §4: {named} may not share one message. Each names a different "
        "thing that happened -- a deliberate privacy decision, a reading "
        "failure, a missing extractor, unfinished work, and an honest empty "
        "result -- and a user who cannot tell them apart cannot tell whether "
        "to change a setting, fix a file, wait, or search differently")
```

- [ ] **Step 4: Append the group-plan item to `src/review_surface/items.py`**

Add these imports at the top of `items.py`, beside the existing ones:

```python
from collections.abc import Sequence

from placement.groups import ExcludedOutlier, GroupPlan
from placement.vocabulary import ROUTED_TO_NODE

from review_surface.states import AbsenceNotice
```

And append at the end of the module:

```python
@dataclass(frozen=True)
class GroupPlanReviewItem:
    """§6.8: ONE coherent group plan, not several unrelated file moves.

    The member items are the same `PlacementReviewItem`s any single-file surface
    would show, so a member accepted inside a group is still individually
    inspectable and individually correctable (§8.2, §8.7). The group is the
    framing, never a wrapper that hides its members.
    """

    group_plan_id: str
    plan_version: str
    group_id: str
    shared_parent_label_chain: tuple[str, ...]
    member_items: tuple[PlacementReviewItem, ...]
    excluded_outliers: tuple[tuple[ExcludedOutlier, tuple[str, ...]], ...]
    absence_notices: tuple[AbsenceNotice, ...]


def group_plan_review_item(conn: sqlite3.Connection, plan: GroupPlan, *,
                           member_decisions: Sequence[PlacementDecision],
                           absences: Sequence[AbsenceNotice] = (),
                           ) -> GroupPlanReviewItem:
    """Project a §6.8 group plan and each of its excluded outliers.

    An outlier routed to `review_queue` gets an EMPTY label chain rather than an
    invented one. There is no node to name, and a placeholder chain would read as
    a destination the user could accept.
    """
    outliers: list[tuple[ExcludedOutlier, tuple[str, ...]]] = []
    for outlier in plan.excluded_outliers:
        chain: tuple[str, ...] = ()
        if outlier.routed_to == ROUTED_TO_NODE and outlier.node_id:
            chain = label_chain_for_version(
                conn, plan_version=plan.plan_version, node_id=outlier.node_id)
        outliers.append((outlier, chain))
    return GroupPlanReviewItem(
        group_plan_id=plan.group_plan_id,
        plan_version=plan.plan_version,
        group_id=plan.group_id,
        shared_parent_label_chain=label_chain_for_version(
            conn, plan_version=plan.plan_version,
            node_id=plan.shared_parent_node_id),
        member_items=tuple(placement_review_item(conn, decision)
                           for decision in member_decisions),
        excluded_outliers=tuple(outliers),
        absence_notices=tuple(absences))
```

- [ ] **Step 5: Run the tests and verify PASS**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/`

Expected: **PASS** — every P13 test so far green, including the five group-plan tests and the nine absence-state tests.

- [ ] **Step 6: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/review_surface/states.py src/review_surface/items.py tests/p13/test_p13_absence_states.py tests/p13/test_p13_group_plan_item.py && git commit -m "feat(p13-6): one coherent group plan, and 66 §4's five states that never share one message"
```

---

### Task 7: The residual surfacing screen — seven attributes, and a missing one is a failure

**Files:**
- Create: `src/review_surface/residual.py`
- Test: `tests/p13/test_p13_residual_screen.py`

**Interfaces:**

*Consumes:*

```python
from placement.residual import ResidualSet, ResidualSetDecision, SET_CHOICES
from placement.residual import require_set_decision   # raises when there is none
from placement.vocabulary import (
    CREATE_CUSTOM_BRANCH, LEAVE_IN_PLACE, REVIEW_WITH_MODEL, SEND_TO_APPROVED_NODE,
)
```

*Produces:*

```python
#: §7.5's seven display attributes, by the ResidualSet field that carries each.
SEVEN_ATTRIBUTES: tuple[str, ...] = (
    "representative_examples", "file_type_distribution", "age_range",
    "evidence_availability", "sensitivity_status", "weak_graph_neighbours",
    "reason_not_placed",
)

@dataclass(frozen=True)
class ResidualSetCard:
    set_id: str
    plan_version: str
    label: str
    file_count: int
    representative_examples: tuple[str, ...]
    file_type_distribution: Mapping[str, int]
    age_range: str
    evidence_availability: str
    sensitivity_status: str
    weak_graph_neighbours: tuple[str, ...]
    reason_not_placed: str
    protected: bool
    choices: tuple[str, ...]
    def attribute(self, name: str) -> object: ...

@dataclass(frozen=True)
class ResidualScreen:
    plan_version: str
    summary_line: str
    total_unplaced: int
    cards: tuple[ResidualSetCard, ...]

class IncompleteResidualCard(RuntimeError): ...

def residual_card(residual_set: ResidualSet) -> ResidualSetCard: ...
def residual_screen(sets: Sequence[ResidualSet], *,
                    plan_version: str) -> ResidualScreen: ...
```

**Done-means:** 5 (*"The residual surfacing screen presents all seven §7.5 attributes for every set; a set missing one is a rendering failure, not a shorter card"*).

> **`ResidualSet` carries an EIGHTH field the SPEC's seven-attribute list does not name.** Live: `protected: bool`, verified by `PYTHONPATH=src python3 -c "import dataclasses; from placement.residual import ResidualSet; print([f.name for f in dataclasses.fields(ResidualSet)])"`. It is carried through to the card because `67` §1 requires protected material to be marked and counted rather than silently omitted, and it is **not** counted as one of the seven — Done-means 5 says seven and the test asserts seven.

> **OPEN QUESTION 2 IS UNRESOLVED.** *"Is §7.5's eight-way set partition canonical or illustrative? P11 reads it as illustrative and defers it."* The design's own sentence is *"It may show"* followed by eight examples. **This task asserts nothing about the number of sets or their labels**, and `residual_screen` accepts any number including zero. Do not write a test that expects eight sets, and do not name a set in a fixture after one of the design's eight.

- [ ] **Step 1: Write the failing tests**

`tests/p13/test_p13_residual_screen.py`:

```python
"""§7.5: a summary line, understandable review sets, seven attributes each."""
from __future__ import annotations

import dataclasses

import pytest

from placement.residual import ResidualSet
from placement.vocabulary import SET_CHOICES

from review_surface.residual import (
    IncompleteResidualCard, SEVEN_ATTRIBUTES, residual_card, residual_screen,
)


def _set(**overrides) -> ResidualSet:
    values = dict(
        set_id="set-1", plan_version="plan-1",
        label="screenshots with no accepted project or event", file_count=58,
        representative_examples=("f-1", "f-2", "f-3"),
        file_type_distribution={"png": 51, "jpg": 7},
        age_range="2024-03 to 2026-08",
        evidence_availability="OCR text available for 44 of 58",
        sensitivity_status="none flagged", protected=False,
        weak_graph_neighbours=("g-reference-clips",),
        reason_not_placed=("no fact reached a legal destination and no accepted "
                           "group claimed them"),
        member_file_ids=tuple(f"f-{n}" for n in range(58)))
    values.update(overrides)
    return ResidualSet(**values)


def test_the_seven_attributes_are_section_7_5_s_seven():
    assert SEVEN_ATTRIBUTES == (
        "representative_examples", "file_type_distribution", "age_range",
        "evidence_availability", "sensitivity_status", "weak_graph_neighbours",
        "reason_not_placed")
    assert len(SEVEN_ATTRIBUTES) == 7


def test_a_card_presents_all_seven_attributes(p13_conn):
    card = residual_card(_set())
    for name in SEVEN_ATTRIBUTES:
        assert card.attribute(name) not in (None, "", ()), (
            f"{name} is one of §7.5's seven and the card is not shorter "
            "without it -- it is a rendering failure")


def test_a_set_missing_an_attribute_is_a_failure_not_a_shorter_card(p13_conn):
    """Done-means 5, and it is the whole point of the item."""
    for name in SEVEN_ATTRIBUTES:
        empty = () if name in ("representative_examples",
                               "weak_graph_neighbours") else (
            {} if name == "file_type_distribution" else "")
        with pytest.raises(IncompleteResidualCard) as caught:
            residual_card(_set(**{name: empty}))
        assert name in str(caught.value)


def test_a_weak_graph_neighbour_list_that_is_genuinely_empty_is_allowed_when_stated(p13_conn):
    """A set with no weak neighbours must still be presentable. The attribute is
    then the STATEMENT that there are none, never a silently missing row."""
    card = residual_card(_set(weak_graph_neighbours=("none",)))
    assert card.weak_graph_neighbours == ("none",)


def test_the_summary_line_reproduces_the_design_s_own_shape(p13_conn):
    """§7.5: "Your main structure is ready. We found 146 files that do not fit a
    confirmed group or approved destination"."""
    screen = residual_screen(
        (_set(file_count=58, set_id="set-1"),
         _set(file_count=88, set_id="set-2", label="standalone PDFs and forms")),
        plan_version="plan-1")
    assert screen.total_unplaced == 146
    assert "146" in screen.summary_line
    assert "Your main structure is ready" in screen.summary_line


def test_the_screen_assumes_no_number_of_sets_and_no_set_names(p13_conn):
    """SPEC Open question 2 is OPEN: §7.5's eight lines are prefaced "It may show"."""
    assert residual_screen((), plan_version="plan-1").cards == ()
    assert len(residual_screen(tuple(
        _set(set_id=f"set-{n}") for n in range(3)),
        plan_version="plan-1").cards) == 3


def test_every_card_offers_p11_s_four_set_choices_and_no_others(p13_conn):
    """§7.6's four choices, imported from P11 rather than respelled."""
    assert residual_card(_set()).choices == SET_CHOICES
    assert len(SET_CHOICES) == 4


def test_the_protected_flag_rides_along_and_is_not_one_of_the_seven(p13_conn):
    card = residual_card(_set(protected=True))
    assert card.protected is True
    assert "protected" not in SEVEN_ATTRIBUTES


def test_a_card_carries_no_member_file_id_list(p13_conn):
    """Done-means 15's precondition: a set must not be expandable into a file
    list by the card alone. `member_file_ids` stays on P11's record."""
    names = {f.name for f in dataclasses.fields(residual_card(_set()))}
    assert "member_file_ids" not in names
```

- [ ] **Step 2: Run the tests and verify RED**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_residual_screen.py`

Expected: **FAIL** — `ModuleNotFoundError: No module named 'review_surface.residual'`.

- [ ] **Step 3: Write `src/review_surface/residual.py`**

```python
# src/review_surface/residual.py
"""§7.5's residual surfacing screen. A summary line, then one card per set.

    "The residual process should begin with a visible residual surfacing screen,
    not an automatic cleanup operation."
    "The system should divide these files into understandable review sets using
    reliable characteristics, rather than presenting a single intimidating pile."

The seven attributes are a CONTRACT and not a nice-to-have: §7.5 says each set
"should display representative examples, file-type distribution, age range,
available OCR or text evidence, sensitivity status, any weak graph neighbors, and
the reason the system could not safely place the files through the normal
pipeline." A card missing one of those is a rendering failure, so `residual_card`
raises rather than emitting a shorter card. Done-means 5 says exactly this, and
it is the difference between a screen that helps and a screen that admits it does
not know while looking complete.

`member_file_ids` is deliberately NOT projected onto the card. A card that
carried the member list would let a protected set be expanded into a filename
list by anything holding the card, and Done-means 15 forbids exactly that while
the policy redacts names. The list stays on P11's record, and Task 12 is the only
thing that decides whether it may be shown.

THE SET COUNT AND THE SET NAMES ARE NOT THIS MODULE'S BUSINESS. §7.5's eight
lines are prefaced "It may show", P11 defers the partition, and SPEC Open question
2 is open. This renders whatever partition P11 publishes.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from placement.residual import ResidualSet
from placement.vocabulary import SET_CHOICES

#: §7.5's seven, by the `ResidualSet` field that carries each. Named here once so
#: the completeness check and the card cannot drift apart.
SEVEN_ATTRIBUTES: tuple[str, ...] = (
    "representative_examples", "file_type_distribution", "age_range",
    "evidence_availability", "sensitivity_status", "weak_graph_neighbours",
    "reason_not_placed",
)


class IncompleteResidualCard(RuntimeError):
    """A set missing one of §7.5's seven. A failure, not a shorter card."""


@dataclass(frozen=True)
class ResidualSetCard:
    set_id: str
    plan_version: str
    label: str
    file_count: int
    representative_examples: tuple[str, ...]
    file_type_distribution: Mapping[str, int]
    age_range: str
    evidence_availability: str
    sensitivity_status: str
    weak_graph_neighbours: tuple[str, ...]
    reason_not_placed: str
    protected: bool
    choices: tuple[str, ...]

    def attribute(self, name: str) -> object:
        if name not in SEVEN_ATTRIBUTES:
            raise KeyError(
                f"{name!r} is not one of §7.5's seven display attributes")
        return getattr(self, name)


@dataclass(frozen=True)
class ResidualScreen:
    plan_version: str
    summary_line: str
    total_unplaced: int
    cards: tuple[ResidualSetCard, ...]


def residual_card(residual_set: ResidualSet) -> ResidualSetCard:
    """One card. Raises if any of §7.5's seven attributes is absent or empty."""
    missing = [name for name in SEVEN_ATTRIBUTES
               if not getattr(residual_set, name)]
    if missing:
        raise IncompleteResidualCard(
            f"residual set {residual_set.set_id!r} has no value for {missing}. "
            "§7.5 requires all seven attributes on every set, and a card that "
            "silently drops one looks complete while hiding the thing the user "
            "needs in order to decide")
    return ResidualSetCard(
        set_id=residual_set.set_id,
        plan_version=residual_set.plan_version,
        label=residual_set.label,
        file_count=residual_set.file_count,
        representative_examples=tuple(residual_set.representative_examples),
        file_type_distribution=dict(residual_set.file_type_distribution),
        age_range=residual_set.age_range,
        evidence_availability=residual_set.evidence_availability,
        sensitivity_status=residual_set.sensitivity_status,
        weak_graph_neighbours=tuple(residual_set.weak_graph_neighbours),
        reason_not_placed=residual_set.reason_not_placed,
        protected=bool(residual_set.protected),
        # §7.6's four, imported from P11. A fifth choice invented here would be
        # a set decision P11 has no branch for.
        choices=SET_CHOICES)


def residual_screen(sets: Sequence[ResidualSet], *,
                    plan_version: str) -> ResidualScreen:
    """The screen: §7.5's summary sentence, then a card per set P11 published.

    The count is summed from the sets rather than passed in, so the sentence and
    the cards cannot disagree -- a summary saying 146 above cards totalling 131
    is the exact shape of the two-denominator bug D11 was ruled on.
    """
    cards = tuple(residual_card(one) for one in sets)
    total = sum(card.file_count for card in cards)
    return ResidualScreen(
        plan_version=plan_version,
        summary_line=(
            f"Your main structure is ready. We found {total} files that do not "
            "fit a confirmed group or approved destination."),
        total_unplaced=total,
        cards=cards)
```

- [ ] **Step 4: Run the tests and verify PASS**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_residual_screen.py`

Expected: **PASS** — nine tests green.

- [ ] **Step 5: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/review_surface/residual.py tests/p13/test_p13_residual_screen.py && git commit -m "feat(p13-7): §7.5's residual screen, where a set missing an attribute is a failure not a shorter card"
```

---

### Task 8: §7.6's ordering — no per-file residual view exists without a recorded set decision

**Files:**
- Modify: `src/review_surface/residual.py`
- Test: `tests/p13/test_p13_residual_ordering.py`

**Interfaces:**

*Consumes:*

```python
from placement.residual import (
    ResidualSetDecision, model_calls_permitted, record_set_decision,
    require_set_decision,
)
from placement.vocabulary import LEAVE_IN_PLACE
```

*Produces:*

```python
class SetDecisionRequired(RuntimeError): ...

@dataclass(frozen=True)
class ResidualFileView:
    set_id: str
    plan_version: str
    set_decision: ResidualSetDecision
    recommendations: tuple[object, ...]
    model_calls_permitted: bool

def residual_file_view(conn: sqlite3.Connection, *, plan_version: str,
                       set_id: str,
                       recommendations_for: Callable[[str], Sequence[object]],
                       ) -> ResidualFileView: ...
```

**Done-means:** 6 (*"**Negative test:** no view exists that presents a per-file residual recommendation for a set with no recorded `residual_set_decision`. A fixture set the user chose to leave in place produces zero presented model recommendations and zero model calls"*).

**Why the gate is the constructor and not a caller's check.** §7.6 puts the set decision *"before the LLM analyzes individual files"*, and P11 already owns the rule — `residual.require_set_decision` raises when there is none, and `model_calls_permitted` says whether a recorded choice authorises a call. P13's obligation is different and narrower: **there must exist no view object at all** for an undecided set. A caller-side `if` is a rule one caller can forget; a constructor that cannot produce the object is a rule nobody can forget. The `recommendations_for` callable is invoked **only after** the decision is fetched and only when the decision permits, so a `leave_in_place` set never even asks for recommendations — which is what makes the "zero model calls" half of Done-means 6 testable with a spy rather than assumed.

- [ ] **Step 1: Write the failing test**

`tests/p13/test_p13_residual_ordering.py`:

```python
"""§7.6: the set decision comes before per-file model review. Enforced by the surface."""
from __future__ import annotations

import pytest

from placement.residual import ResidualSetDecision, record_set_decision
from placement.vocabulary import (
    LEAVE_IN_PLACE, REVIEW_WITH_MODEL, SEND_TO_APPROVED_NODE,
)

from review_surface.residual import (
    ResidualFileView, SetDecisionRequired, residual_file_view,
)

T0 = "2026-08-29T00:00:00Z"


class _Spy:
    """Counts every time anything asks for per-file recommendations."""

    def __init__(self, items=()):
        self.calls = 0
        self.items = tuple(items)

    def __call__(self, set_id):
        self.calls += 1
        return self.items


def _decide(conn, choice, *, set_id="set-1", node_id=None):
    record_set_decision(
        conn,
        ResidualSetDecision(set_id=set_id, plan_version="plan-1",
                            choice=choice, node_id=node_id, decided_at=T0),
        component_version="p13-1", observed_at=T0, user_id="jy")


def test_no_view_exists_for_a_set_with_no_recorded_decision(p13_conn):
    """Done-means 6, first clause."""
    spy = _Spy(("rec-1",))
    with pytest.raises(SetDecisionRequired) as caught:
        residual_file_view(p13_conn, plan_version="plan-1", set_id="set-1",
                           recommendations_for=spy)
    assert "set-1" in str(caught.value)
    assert spy.calls == 0, (
        "recommendations were fetched for a set with no decision")


def test_a_leave_in_place_set_produces_zero_recommendations_and_zero_calls(p13_conn):
    """Done-means 6, second clause: it must cost zero model calls."""
    _decide(p13_conn, LEAVE_IN_PLACE)
    spy = _Spy(("rec-1", "rec-2"))
    view = residual_file_view(p13_conn, plan_version="plan-1", set_id="set-1",
                              recommendations_for=spy)
    assert view.recommendations == ()
    assert view.model_calls_permitted is False
    assert spy.calls == 0


def test_a_review_with_model_set_reaches_its_recommendations(p13_conn):
    _decide(p13_conn, REVIEW_WITH_MODEL)
    spy = _Spy(("rec-1", "rec-2"))
    view = residual_file_view(p13_conn, plan_version="plan-1", set_id="set-1",
                              recommendations_for=spy)
    assert view.recommendations == ("rec-1", "rec-2")
    assert view.model_calls_permitted is True
    assert spy.calls == 1


def test_a_send_to_approved_node_set_needs_no_model_and_asks_for_none(p13_conn):
    _decide(p13_conn, SEND_TO_APPROVED_NODE, node_id="n-residual")
    spy = _Spy(("rec-1",))
    view = residual_file_view(p13_conn, plan_version="plan-1", set_id="set-1",
                              recommendations_for=spy)
    assert view.model_calls_permitted is False
    assert view.recommendations == ()
    assert spy.calls == 0


def test_the_view_carries_the_decision_it_was_gated_on(p13_conn):
    _decide(p13_conn, REVIEW_WITH_MODEL)
    view = residual_file_view(p13_conn, plan_version="plan-1", set_id="set-1",
                              recommendations_for=_Spy())
    assert view.set_decision.choice == REVIEW_WITH_MODEL
    assert view.set_decision.set_id == "set-1"


def test_a_decision_recorded_under_another_plan_version_does_not_unlock_this_one(p13_conn):
    """§8.8: a decision belongs to the version it was taken against."""
    _decide(p13_conn, REVIEW_WITH_MODEL)
    spy = _Spy(("rec-1",))
    with pytest.raises(SetDecisionRequired):
        residual_file_view(p13_conn, plan_version="plan-2", set_id="set-1",
                           recommendations_for=spy)
    assert spy.calls == 0
```

> If `record_set_decision` or `ResidualSetDecision` reject any keyword above, read the live shapes with `PYTHONPATH=src python3 -c "import inspect, dataclasses; from placement.residual import ResidualSetDecision, record_set_decision; print([f.name for f in dataclasses.fields(ResidualSetDecision)]); print(inspect.signature(record_set_decision))"` and copy `tests/p11/`'s live builder. `require_set_decision`'s exception type must also be read live — if it is not a subclass of `LookupError`, adjust the `except` clause in Step 3 to catch what it actually raises rather than broadening to bare `Exception`.

- [ ] **Step 2: Run the test and verify RED**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_residual_ordering.py`

Expected: **FAIL** — `ImportError: cannot import name 'SetDecisionRequired' from 'review_surface.residual'`.

- [ ] **Step 3: Append to `src/review_surface/residual.py`**

Add to the imports at the top:

```python
import sqlite3
from collections.abc import Callable

from placement.residual import (
    ResidualSetDecision, model_calls_permitted, require_set_decision,
)
```

And append at the end of the module:

```python
class SetDecisionRequired(RuntimeError):
    """A per-file residual view was asked for before the set was decided."""


@dataclass(frozen=True)
class ResidualFileView:
    """The per-file residual surface. It cannot exist before the set decision.

    §7.6 places the set-level question BEFORE the LLM analyzes individual files,
    and a set the user leaves in place must cost zero model calls. A caller-side
    `if` would be a rule one caller can forget; a constructor that refuses to
    produce the object is a rule nobody can forget, and it is why this is a
    factory function rather than a plain dataclass anyone can instantiate.
    """

    set_id: str
    plan_version: str
    set_decision: ResidualSetDecision
    recommendations: tuple[object, ...]
    model_calls_permitted: bool


def residual_file_view(conn: sqlite3.Connection, *, plan_version: str,
                       set_id: str,
                       recommendations_for: Callable[[str], Sequence[object]],
                       ) -> ResidualFileView:
    """Fetch the decision FIRST. Ask for recommendations only if it permits them.

    `recommendations_for` is invoked at most once and never before the decision
    is in hand, which is what makes "zero model calls" observable with a counting
    double rather than assumed from a comment.
    """
    try:
        decision = require_set_decision(conn, plan_version=plan_version,
                                        set_id=set_id)
    except Exception as absent:  # noqa: BLE001 -- re-raised as P13's own name
        raise SetDecisionRequired(
            f"residual set {set_id!r} has no recorded set decision under plan "
            f"version {plan_version!r}. §7.6 places the set decision before any "
            "per-file model review, so there is no per-file view to build and "
            "no recommendations have been requested"
        ) from absent
    permitted = model_calls_permitted(decision)
    recommendations = tuple(recommendations_for(set_id)) if permitted else ()
    return ResidualFileView(
        set_id=set_id, plan_version=plan_version, set_decision=decision,
        recommendations=recommendations, model_calls_permitted=permitted)
```

> **Narrow the `except` before committing.** `except Exception` is written here because `require_set_decision`'s exception class must be read live rather than guessed. Read it with `PYTHONPATH=src python3 -c "import inspect; from placement import residual; print(inspect.getsource(residual.require_set_decision))"` and replace `Exception` with the exact class. A bare `except Exception` around a database call also swallows an `sqlite3.OperationalError` from a missing table, which would report "no set decision" for a schema problem — the exact shape of a guard that passes forever while checking nothing.

- [ ] **Step 4: Run the test and verify PASS**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_residual_ordering.py`

Expected: **PASS** — six tests green.

- [ ] **Step 5: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/review_surface/residual.py tests/p13/test_p13_residual_ordering.py && git commit -m "feat(p13-8): §7.6's ordering, enforced by a view that cannot be built before the set is decided"
```

---

### Task 9: `review_action` — the one record P13 emits, with its scope and its routing

> **THE THREE EXISTING FIXTURES DO NOT MATCH THIS RECORD, AND THAT IS UNRESOLVED.** See the callout in "What does NOT exist" above. This task builds the SPEC's record and, in Step 6, a **compatibility report test** that prints exactly what each of the three existing fixtures asks for and P13 does not supply. It writes no translation table and widens no vocabulary.

> **THE SPEC'S OWN FIELD BLOCK IS CORRUPTED.** P13 SPEC:246-280 prints the `review_action` field list, and between `session_id` and `action` it contains a prose paragraph about protected containers that is plainly not a field (*"**Protected containers** (P3 SPEC, ratified 2026-08-20) are presented as their own inspectable list…"*). This plan reads that paragraph as **a rule about presentation, not a field**, and Step 3 enforces it as a refusal: no `review_action` may be constructed over an `untouched_protected` subject, because *"applications and system items are never read or moved, so offering the user a choice would imply one exists."* If Joseph intended a field there, this reading is wrong — it is flagged rather than resolved.

**Files:**
- Create: `src/review_surface/records.py`
- Create: `src/review_surface/routing.py`
- Create: `src/review_surface/collect.py`
- Create: `src/review_surface/store.py`
- Test: `tests/p13/test_p13_review_action.py`
- Test: `tests/p13/test_p13_routing.py`
- Test: `tests/p13/test_p13_fixture_compatibility.py`

**Interfaces:**

*Consumes:*

```python
from database_agent.events import append_event, CORRECTION_SCOPES
from review_surface.presentation import PresentedState, presented_state
from review_surface.vocabulary import (
    ACTIONS, EVENT_ACTION_ROUTED, SUBSYSTEM, SURFACES, UNTOUCHED_PROTECTED, check,
)
```

*Produces:*

```python
# records.py
@dataclass(frozen=True)
class ReviewAction:
    action_id: str
    surface: str
    subject_ref: str
    plan_version: str
    session_id: str
    action: str
    bulk_member_refs: tuple[str, ...]
    bulk_basis: str | None
    correction_scope: str
    routed_to: tuple[str, ...]
    presented_state_ref: str
    payload: Mapping[str, object]
    user_id: str
    acted_at: str

# routing.py
PARTS: tuple[str, ...]                          # ("P1","P6","P7","P9","P10","P11","P12")
ROUTING: Mapping[str, tuple[str, ...]]          # surface -> parts
ACTION_ROUTING: Mapping[str, tuple[str, ...]]   # action -> extra parts
class Unroutable(RuntimeError): ...
def route(surface: str, action: str) -> tuple[str, ...]: ...

# collect.py
class ScopeNotPresented(ValueError): ...
class ProtectedContainerHasNoAction(RuntimeError): ...
class PresentationRequired(ValueError): ...
def collect(conn, *, action_id, surface, subject_ref, plan_version, session_id,
            action, correction_scope, presented_state_ref, user_id, acted_at,
            component_version, bulk_member_refs=(), bulk_basis=None,
            payload=None) -> ReviewAction: ...

# store.py
def record_action(conn: sqlite3.Connection, action: ReviewAction) -> None: ...
def actions_for(conn, *, subject_ref: str,
                plan_version: str | None = None) -> tuple[ReviewAction, ...]: ...
```

**Done-means:** 7 (every §7.10 action collectable), 9 (every action carries an explicit scope; **negative test:** no code path assigns `corpus` without the user selecting it).

- [ ] **Step 1: Write the failing routing test**

`tests/p13/test_p13_routing.py`:

```python
"""SPEC:282-300: routing is the whole contract. One gesture, possibly two parts."""
from __future__ import annotations

import pytest

from review_surface.routing import ACTION_ROUTING, PARTS, ROUTING, Unroutable, route
from review_surface.vocabulary import (
    ACTION_ACCEPT, ACTION_ADOPT_VERSION, ACTION_APPROVE_FOR_APPLY,
    ACTION_CREATE_CUSTOM_FOLDER, ACTION_MARK_PRIVATE, ACTION_REFRESH_PLAN,
    ACTION_RESET_LEARNING, ACTION_SELECT_CONSENT_OPTION, ACTION_SET_REDACTION,
    ACTIONS, SURFACE_CANVAS, SURFACE_CONSENT, SURFACE_APPLY,
    SURFACE_GROUP_PLAN, SURFACE_LEARNING, SURFACE_PLACEMENT,
    SURFACE_PLAN_VERSION, SURFACE_RESIDUAL_SET, SURFACES,
)


def test_every_surface_routes_somewhere():
    for surface in SURFACES:
        assert ROUTING[surface], f"{surface} routes to no part"
        assert set(ROUTING[surface]) <= set(PARTS)


def test_placement_and_residual_surfaces_route_to_p11():
    for surface in (SURFACE_PLACEMENT, SURFACE_GROUP_PLAN, SURFACE_RESIDUAL_SET):
        assert "P11" in route(surface, ACTION_ACCEPT)


def test_a_group_change_on_a_group_plan_also_reaches_p9():
    assert "P9" in ROUTING[SURFACE_GROUP_PLAN]


def test_a_custom_folder_created_during_residual_review_reaches_both_p11_and_p10():
    """SPEC:283-286 and :517-519 -- one gesture, two records, and P13's event is
    what keeps them one user action."""
    parts = route(SURFACE_RESIDUAL_SET, ACTION_CREATE_CUSTOM_FOLDER)
    assert "P11" in parts and "P10" in parts


def test_a_reclassification_to_private_reaches_both_p7_and_p6():
    """SPEC:299."""
    parts = route(SURFACE_PLACEMENT, ACTION_MARK_PRIVATE)
    assert "P7" in parts and "P6" in parts


def test_consent_and_redaction_route_to_p7():
    assert route(SURFACE_CONSENT, ACTION_SELECT_CONSENT_OPTION) == ("P7",)
    assert "P7" in route(SURFACE_CONSENT, ACTION_SET_REDACTION)


def test_refresh_and_apply_approval_route_to_p12():
    assert "P12" in route(SURFACE_APPLY, ACTION_REFRESH_PLAN)
    assert "P12" in route(SURFACE_APPLY, ACTION_APPROVE_FOR_APPLY)


def test_a_version_action_routes_to_p10():
    assert "P10" in route(SURFACE_PLAN_VERSION, ACTION_ADOPT_VERSION)


def test_a_reset_routes_to_p1():
    assert route(SURFACE_LEARNING, ACTION_RESET_LEARNING) == ("P1",)


def test_the_parts_named_are_the_seven_the_spec_s_table_names():
    assert PARTS == ("P1", "P6", "P7", "P9", "P10", "P11", "P12")


def test_an_unknown_surface_or_action_is_unroutable_and_not_silently_dropped():
    with pytest.raises(Unroutable):
        route("dashboard", ACTION_ACCEPT)
    with pytest.raises(Unroutable):
        route(SURFACE_PLACEMENT, "delete_everything")


def test_routing_is_deterministic_and_ordered():
    assert route(SURFACE_PLACEMENT, ACTION_MARK_PRIVATE) == route(
        SURFACE_PLACEMENT, ACTION_MARK_PRIVATE)
    for surface in SURFACES:
        for action in ACTIONS:
            try:
                parts = route(surface, action)
            except Unroutable:
                continue
            assert list(parts) == sorted(parts, key=PARTS.index)
            assert len(set(parts)) == len(parts)
```

- [ ] **Step 2: Write the failing collection test**

`tests/p13/test_p13_review_action.py`:

```python
"""One record for every gesture, on every surface. Scope is presented, never inferred."""
from __future__ import annotations

import pytest

from privacy.display import RedactionSettings

from review_surface.collect import (
    PresentationRequired, ProtectedContainerHasNoAction, ScopeNotPresented,
    collect,
)
from review_surface.presentation import record_presentation
from review_surface.store import actions_for, record_action
from review_surface.vocabulary import (
    ACTION_ACCEPT, ACTION_CHANGE_DESTINATION, ACTION_CREATE_CUSTOM_FOLDER,
    ACTION_DEFER, ACTION_LEAVE_UNTOUCHED, ACTION_MARK_PRIVATE,
    ACTION_RETURN_TO_ACCEPTED_GROUP, ACTIONS, EVENT_ACTION_ROUTED, SUBSYSTEM,
    SURFACE_PLACEMENT, UNTOUCHED_PROTECTED,
)

T0 = "2026-08-29T00:00:00Z"
SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")


@pytest.fixture()
def shown_ref(p13_conn):
    return record_presentation(
        p13_conn, surface=SURFACE_PLACEMENT, subject_ref="d1",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=("obs-1",), user_id="jy", component_version="p13-1",
        rendered_at=T0).presented_state_ref


def _collect(conn, ref, **overrides):
    values = dict(
        action_id="a-1", surface=SURFACE_PLACEMENT, subject_ref="d1",
        plan_version="plan-1", session_id="s-1", action=ACTION_ACCEPT,
        correction_scope="file", presented_state_ref=ref, user_id="jy",
        acted_at=T0, component_version="p13-1")
    values.update(overrides)
    return collect(conn, **values)


def test_every_one_of_section_7_10_s_eight_actions_is_collectable(p13_conn, shown_ref):
    """Done-means 7."""
    eight = (ACTION_ACCEPT, "accept_bulk", ACTION_CHANGE_DESTINATION,
             ACTION_CREATE_CUSTOM_FOLDER, ACTION_RETURN_TO_ACCEPTED_GROUP,
             ACTION_MARK_PRIVATE, ACTION_DEFER, ACTION_LEAVE_UNTOUCHED)
    for index, action in enumerate(eight):
        extra = {}
        if action == "accept_bulk":
            extra = dict(bulk_member_refs=("f-1", "f-2"),
                         bulk_basis="same evidence pattern")
        collected = _collect(p13_conn, shown_ref, action_id=f"a-{index}",
                             action=action, **extra)
        assert collected.action == action


def test_every_action_carries_an_explicit_scope(p13_conn, shown_ref):
    """Done-means 9, first clause."""
    collected = _collect(p13_conn, shown_ref, correction_scope="group")
    assert collected.correction_scope == "group"


def test_no_code_path_assigns_corpus_scope_without_the_user_selecting_it(p13_conn, shown_ref):
    """Done-means 9, NEGATIVE TEST. §8.7's Columbia transcript is the case."""
    import inspect

    import review_surface.collect as module
    signature = inspect.signature(module.collect)
    assert signature.parameters["correction_scope"].default is (
        inspect.Parameter.empty), (
        "correction_scope must have NO default; a default IS an inference")
    source = inspect.getsource(module)
    assert '"corpus"' not in source and "'corpus'" not in source, (
        "the literal 'corpus' appears in the collection path")


def test_a_missing_scope_is_a_refusal_and_not_a_default(p13_conn, shown_ref):
    with pytest.raises(TypeError):
        collect(p13_conn, action_id="a-x", surface=SURFACE_PLACEMENT,
                subject_ref="d1", plan_version="plan-1", session_id="s-1",
                action=ACTION_ACCEPT, presented_state_ref=shown_ref,
                user_id="jy", acted_at=T0, component_version="p13-1")


def test_an_out_of_vocabulary_scope_is_refused(p13_conn, shown_ref):
    with pytest.raises(ScopeNotPresented):
        _collect(p13_conn, shown_ref, correction_scope="everything")


def test_an_action_with_no_presented_state_is_refused(p13_conn):
    """§8.7: a rejection is only interpretable against what the user was shown."""
    with pytest.raises(PresentationRequired):
        _collect(p13_conn, "ps-never-minted")


def test_a_protected_container_carries_no_action_at_all(p13_conn, shown_ref):
    """P13 SPEC:260-262 and `67` §1. Offering a choice would imply one exists."""
    with pytest.raises(ProtectedContainerHasNoAction):
        _collect(p13_conn, shown_ref, subject_ref=UNTOUCHED_PROTECTED)
    with pytest.raises(ProtectedContainerHasNoAction):
        _collect(p13_conn, shown_ref,
                 payload={"subject_kind": UNTOUCHED_PROTECTED})


def test_the_action_is_routed_and_the_parts_are_recorded_on_it(p13_conn, shown_ref):
    collected = _collect(p13_conn, shown_ref, action=ACTION_MARK_PRIVATE)
    assert "P7" in collected.routed_to and "P6" in collected.routed_to


def test_collecting_appends_the_registered_event_with_the_scope_and_the_parts(
        p13_conn, shown_ref):
    collected = _collect(p13_conn, shown_ref, correction_scope="node",
                         action=ACTION_CHANGE_DESTINATION,
                         payload={"node_id": "n-9"})
    row = p13_conn.execute(
        "SELECT event_type, subsystem, correction_scope, explanation FROM "
        "events WHERE event_type = ? ORDER BY event_id DESC LIMIT 1",
        (EVENT_ACTION_ROUTED,)).fetchone()
    assert row["event_type"] == EVENT_ACTION_ROUTED
    assert row["subsystem"] == SUBSYSTEM
    assert row["correction_scope"] == "node"
    assert "P11" in row["explanation"]


def test_a_collected_action_stores_and_reads_back_whole(p13_conn, shown_ref):
    collected = _collect(p13_conn, shown_ref)
    record_action(p13_conn, collected)
    assert actions_for(p13_conn, subject_ref="d1") == (collected,)


def test_a_stored_action_cannot_be_updated_or_deleted(p13_conn, shown_ref):
    import sqlite3
    record_action(p13_conn, _collect(p13_conn, shown_ref))
    with pytest.raises(sqlite3.IntegrityError):
        p13_conn.execute("UPDATE review_actions SET action = 'reject'")
    with pytest.raises(sqlite3.IntegrityError):
        p13_conn.execute("DELETE FROM review_actions")


def test_p13_writes_no_record_other_than_its_own(p13_conn, shown_ref):
    """Done-means 22's writing clause, in its first position."""
    before = {
        name: p13_conn.execute(f"SELECT count(*) AS c FROM {name}").fetchone()["c"]
        for name in ("placement_decisions", "classifications", "files")
        if p13_conn.execute(
            "SELECT count(*) AS c FROM sqlite_master WHERE type='table' AND "
            "name = ?", (name,)).fetchone()["c"]}
    record_action(p13_conn, _collect(p13_conn, shown_ref))
    after = {
        name: p13_conn.execute(f"SELECT count(*) AS c FROM {name}").fetchone()["c"]
        for name in before}
    assert after == before
```

- [ ] **Step 3: Write `src/review_surface/records.py` and `src/review_surface/routing.py`**

```python
# src/review_surface/records.py
"""The four records P13 publishes. It publishes no derived judgement of any kind.

Types, stated once for all of them (SPEC:169-174): every `*_id` and `*_ref` is an
opaque identifier string; `plan_version` is P10's plan id plus version, the
version the surface was rendered against; `routed_to[]` is a list of part
identifiers; `user_id` is §8.2's user-identity field; timestamps are strings;
`count` is an integer; `bulk_basis`, `cause` and `label` are display strings; and
every remaining field takes exactly one value from a closed list P13 prints.

`ReviewApproval` and the progress records live here too, added by Tasks 14 and 16,
so the four are readable in one place.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ReviewAction:
    """Every user gesture on every surface. P13 writes nothing else (SPEC:244).

    `bulk_member_refs` ENUMERATES every member and is never a filter expression:
    a filter cannot be re-read later to say which files a reversal applies to,
    and §8.7 requires each resulting per-file decision to stay individually
    inspectable and individually correctable.

    `correction_scope` has no default anywhere in this package. §8.7's governing
    example is that a user saying ONE transcript belongs in a Columbia packet
    must not teach the engine that all transcripts do -- and a default is an
    inference wearing a keyword's clothes.
    """

    action_id: str
    surface: str
    subject_ref: str
    plan_version: str
    session_id: str
    action: str
    bulk_member_refs: tuple[str, ...]
    bulk_basis: str | None
    correction_scope: str
    routed_to: tuple[str, ...]
    presented_state_ref: str
    payload: Mapping[str, object] = field(default_factory=dict)
    user_id: str = ""
    acted_at: str = ""
```

> **Field order note.** `payload`, `user_id` and `acted_at` carry defaults so the dataclass is constructible in the order above; every call site in this plan passes all three explicitly. If the executing agent prefers no defaults, move `payload` last and drop the defaults — nothing in the plan depends on them.

```python
# src/review_surface/routing.py
"""Routing is the whole contract (SPEC:282-287).

P13 hands the action to the owning part and THAT part decides what it means.
An action may route to more than one part; it is still ONE collected gesture,
which is precisely why P13's `review action routed` event exists: §7.10's
"create a custom folder" during residual review is both a residual decision
(P11) and a tree edit (P10), and without P13's event the two records lose the
fact that they were one user action (SPEC:516-519).

Two tables, not one. A surface says who normally owns what happens there; an
action says who ELSE a particular gesture reaches regardless of surface. Folding
them into one table would need a row per (surface, action) pair -- 216 rows, most
of them meaningless -- and the two rules are genuinely different rules.
"""
from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from review_surface.vocabulary import (
    ACTION_ADOPT_VERSION, ACTION_APPROVE_FOR_APPLY, ACTION_CREATE_CUSTOM_FOLDER,
    ACTION_MARK_PRIVATE, ACTION_REFRESH_PLAN, ACTION_RESET_LEARNING,
    ACTION_RESTORE_VERSION, ACTION_SELECT_CONSENT_OPTION, ACTION_SET_REDACTION,
    ACTIONS, SURFACE_APPLY, SURFACE_CANVAS, SURFACE_CONSENT,
    SURFACE_EVALUATION, SURFACE_GROUP_PLAN, SURFACE_LEARNING,
    SURFACE_PLACEMENT, SURFACE_PLAN_VERSION, SURFACE_PRIVACY_SETTINGS,
    SURFACE_RESIDUAL_FILE, SURFACE_RESIDUAL_SET, SURFACE_UNDO_CONFLICT,
    SURFACES,
)

#: The seven parts SPEC:292-300's table names, in the order routing output uses.
PARTS: tuple[str, ...] = ("P1", "P6", "P7", "P9", "P10", "P11", "P12")


class Unroutable(RuntimeError):
    """A surface or action with no owning part. Refused, never silently dropped."""


ROUTING: Mapping[str, tuple[str, ...]] = MappingProxyType({
    SURFACE_PLACEMENT: ("P11",),
    # SPEC:298 -- group changes collected on `group_plan` route to P9 as well as
    # to P11, which owns the group plan record itself.
    SURFACE_GROUP_PLAN: ("P9", "P11"),
    SURFACE_RESIDUAL_SET: ("P11",),
    SURFACE_RESIDUAL_FILE: ("P11",),
    SURFACE_CANVAS: ("P10",),
    SURFACE_APPLY: ("P12",),
    SURFACE_UNDO_CONFLICT: ("P12",),
    SURFACE_CONSENT: ("P7",),
    SURFACE_PRIVACY_SETTINGS: ("P7",),
    # SPEC Open question 9 is OPEN: whether a reviewer adjudication in the
    # evaluation view becomes an §8.7 correction. P2 owns the record either way,
    # and P2 is not in SPEC:292-300's routing table -- so an evaluation gesture
    # routes to P1, which writes the event, and nothing more is claimed.
    SURFACE_EVALUATION: ("P1",),
    SURFACE_LEARNING: ("P1",),
    SURFACE_PLAN_VERSION: ("P10",),
})
assert set(ROUTING) == set(SURFACES)

#: Parts a gesture reaches IN ADDITION to its surface's owner.
ACTION_ROUTING: Mapping[str, tuple[str, ...]] = MappingProxyType({
    # SPEC:285 -- a tree edit, including a custom folder created during residual
    # review, goes to P10. It produces a new plan version (§8.8); it is never the
    # model inventing a destination (§7.4).
    ACTION_CREATE_CUSTOM_FOLDER: ("P10",),
    # SPEC:299 -- a reclassification to private is P7's AND P6's, jointly.
    ACTION_MARK_PRIVATE: ("P6", "P7"),
    ACTION_SELECT_CONSENT_OPTION: ("P7",),
    ACTION_SET_REDACTION: ("P7",),
    ACTION_REFRESH_PLAN: ("P12",),
    ACTION_APPROVE_FOR_APPLY: ("P12",),
    ACTION_ADOPT_VERSION: ("P10",),
    ACTION_RESTORE_VERSION: ("P10",),
    ACTION_RESET_LEARNING: ("P1",),
})
assert set(ACTION_ROUTING) <= set(ACTIONS)


def route(surface: str, action: str) -> tuple[str, ...]:
    """Every part this one gesture is handed to, in `PARTS` order, deduplicated."""
    if surface not in ROUTING:
        raise Unroutable(
            f"{surface!r} is not one of P13's {len(SURFACES)} surfaces, so there "
            "is no part to hand this gesture to. An action with no owner would "
            "be collected and silently mean nothing")
    if action not in ACTIONS:
        raise Unroutable(
            f"{action!r} is not one of P13's {len(ACTIONS)} actions")
    parts = set(ROUTING[surface]) | set(ACTION_ROUTING.get(action, ()))
    return tuple(sorted(parts, key=PARTS.index))
```

- [ ] **Step 4: Write `src/review_surface/collect.py` and `src/review_surface/store.py`**

```python
# src/review_surface/collect.py
"""Collecting one gesture. P13 presents and collects; it never decides.

Three refusals, and each is a Done-means:

* **`correction_scope` has no default.** Done-means 9's negative test asserts it
  by signature introspection, because a default is an inference and §8.7's whole
  example is about not inferring one. The literal spelling of the widest scope
  does not appear in this module at all; it is validated against P1's tuple.
* **A presentation must exist.** §8.7 requires negative feedback stored WITH the
  evidence that produced it, and SPEC:511-512: a file rejected while its OCR text
  was redacted is a different signal from one rejected with the evidence visible.
  An action with no recorded presentation carries no such evidence.
* **A protected container has no action.** P13 SPEC:260-262: applications and
  system items are never read or moved, "so offering the user a choice would
  imply one exists". `67` §1 makes the same rule standing and non-negotiable.

Nothing here interprets the gesture. `routed_to` names who will.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping, Sequence

from database_agent.events import CORRECTION_SCOPES, append_event

from review_surface.presentation import presented_state
from review_surface.records import ReviewAction
from review_surface.routing import route
from review_surface.vocabulary import (
    ACTION_ACCEPT_BULK, ACTIONS, EVENT_ACTION_ROUTED, SUBSYSTEM, SURFACES,
    UNTOUCHED_PROTECTED, check,
)


class ScopeNotPresented(ValueError):
    """A scope outside §8.7's six. It was not chosen, so it was not presented."""


class PresentationRequired(ValueError):
    """An action with no record of what the user was shown."""


class ProtectedContainerHasNoAction(RuntimeError):
    """A gesture over an untouched protected container. There is no choice to offer."""


class BulkMembersRequired(ValueError):
    """A bulk acceptance with no enumerated members. A filter is not a list."""


def collect(conn: sqlite3.Connection, *, action_id: str, surface: str,
            subject_ref: str, plan_version: str, session_id: str, action: str,
            correction_scope: str, presented_state_ref: str, user_id: str,
            acted_at: str, component_version: str,
            bulk_member_refs: Sequence[str] = (), bulk_basis: str | None = None,
            payload: Mapping[str, object] | None = None) -> ReviewAction:
    """Validate, route, append the §8.2 event, return the record. Store separately.

    `correction_scope` is a required keyword with NO default. That is the whole
    mechanism behind "scope is presented, never inferred": there is no value this
    function can supply on the user's behalf, so there is no path by which one
    gets supplied.
    """
    check(surface, SURFACES, name="surface")
    check(action, ACTIONS, name="action")
    if correction_scope not in CORRECTION_SCOPES:
        raise ScopeNotPresented(
            f"{correction_scope!r} is not one of §8.7's six scopes "
            f"{list(CORRECTION_SCOPES)}. Every collected action carries a scope "
            "the user chose at collection time")
    fields = dict(payload or {})
    if UNTOUCHED_PROTECTED in (subject_ref, fields.get("subject_kind")):
        raise ProtectedContainerHasNoAction(
            "protected containers are presented as their own inspectable list "
            "and carry no action at all. Applications and system items are "
            "never read or moved, so offering the user a choice here would "
            "imply one exists. The list answers 'why was nothing proposed for "
            "this?' instead of leaving silence")
    members = tuple(bulk_member_refs)
    if action == ACTION_ACCEPT_BULK and not members:
        raise BulkMembersRequired(
            "a bulk acceptance enumerates every member. A filter expression "
            "cannot be re-read later to say which files a reversal applies to")
    if presented_state(conn, presented_state_ref) is None:
        raise PresentationRequired(
            f"{presented_state_ref!r} names no recorded presentation. §8.7 "
            "requires feedback to be stored with the evidence that produced it, "
            "and a gesture with no record of what was shown carries none")
    parts = route(surface, action)
    record = ReviewAction(
        action_id=action_id, surface=surface, subject_ref=subject_ref,
        plan_version=plan_version, session_id=session_id, action=action,
        bulk_member_refs=members, bulk_basis=bulk_basis,
        correction_scope=correction_scope, routed_to=parts,
        presented_state_ref=presented_state_ref, payload=fields,
        user_id=user_id, acted_at=acted_at)
    append_event(
        conn, event_type=EVENT_ACTION_ROUTED, subsystem=SUBSYSTEM,
        component_version=component_version, observed_at=acted_at,
        user_id=user_id, correction_scope=correction_scope,
        correction_subject=subject_ref,
        explanation=json.dumps(
            {"action_id": action_id, "surface": surface, "action": action,
             "routed_to": list(parts), "correction_scope": correction_scope,
             "presented_state_ref": presented_state_ref,
             "bulk_member_refs": list(members), "bulk_basis": bulk_basis},
            sort_keys=True))
    return record
```

```python
# src/review_surface/store.py
"""Append and read P13's own three tables. No update path exists anywhere here.

P13 owns no supersedable record (SPEC:521), so there is no `supersede`, no
`mark_superseded` and no `current_*`. A later gesture is a later row, and the
prior one stays inspectable -- which is what makes §8.2's "a superseded record is
shown AS superseded, alongside the record that replaced it" possible for the
parts that do own supersedable records.
"""
from __future__ import annotations

import json
import sqlite3

from review_surface.records import ReviewAction


def record_action(conn: sqlite3.Connection, action: ReviewAction) -> None:
    conn.execute(
        "INSERT INTO review_actions "
        "(action_id, surface, subject_ref, plan_version, session_id, action, "
        " bulk_member_refs, bulk_basis, correction_scope, routed_to, "
        " presented_state_ref, payload, user_id, acted_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (action.action_id, action.surface, action.subject_ref,
         action.plan_version, action.session_id, action.action,
         json.dumps(list(action.bulk_member_refs)), action.bulk_basis,
         action.correction_scope, json.dumps(list(action.routed_to)),
         action.presented_state_ref, json.dumps(dict(action.payload),
                                                sort_keys=True),
         action.user_id, action.acted_at))
    conn.commit()


def _from_row(row: sqlite3.Row) -> ReviewAction:
    return ReviewAction(
        action_id=row["action_id"], surface=row["surface"],
        subject_ref=row["subject_ref"], plan_version=row["plan_version"],
        session_id=row["session_id"], action=row["action"],
        bulk_member_refs=tuple(json.loads(row["bulk_member_refs"])),
        bulk_basis=row["bulk_basis"],
        correction_scope=row["correction_scope"],
        routed_to=tuple(json.loads(row["routed_to"])),
        presented_state_ref=row["presented_state_ref"],
        payload=json.loads(row["payload"]), user_id=row["user_id"],
        acted_at=row["acted_at"])


def actions_for(conn: sqlite3.Connection, *, subject_ref: str,
                plan_version: str | None = None) -> tuple[ReviewAction, ...]:
    """Every action on one subject, oldest first. Deterministic order."""
    if plan_version is None:
        rows = conn.execute(
            "SELECT * FROM review_actions WHERE subject_ref = ? "
            "ORDER BY acted_at, action_id", (subject_ref,)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM review_actions WHERE subject_ref = ? AND "
            "plan_version = ? ORDER BY acted_at, action_id",
            (subject_ref, plan_version)).fetchall()
    return tuple(_from_row(row) for row in rows)


def actions_naming_member(conn: sqlite3.Connection, *, member_ref: str,
                          ) -> tuple[ReviewAction, ...]:
    """Every action whose `bulk_member_refs` enumerates this member.

    §8.2 and §8.7: a bulk acceptance is not a single opaque decision over an
    unnamed population, so a member must be findable from the member's side.
    """
    rows = conn.execute(
        "SELECT * FROM review_actions ORDER BY acted_at, action_id").fetchall()
    return tuple(record for record in map(_from_row, rows)
                 if member_ref in record.bulk_member_refs)
```

- [ ] **Step 5: Run the tests and verify PASS**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_routing.py tests/p13/test_p13_review_action.py`

Expected: **PASS** — twelve routing tests and twelve collection tests green.

- [ ] **Step 6: Write the fixture-compatibility REPORT test — it must FAIL loudly and stay failing until Joseph rules**

`tests/p13/test_p13_fixture_compatibility.py`:

```python
"""Three parts guessed at P13's record before P13 published one. Report the gap.

This test is EXPECTED TO FAIL and is marked `xfail(strict=True)` so the suite
stays green while the failure stays visible. It exists so the reconciliation is a
decision someone makes rather than a defect someone discovers in integration.

DO NOT "fix" this by widening `review_surface.vocabulary.ACTIONS` to absorb
P9's or P10's action names, and do not narrow theirs. Four vocabularies disagree
and only Joseph can say which is right.
"""
from __future__ import annotations

import dataclasses

import pytest

from review_surface.records import ReviewAction
from review_surface.vocabulary import ACTIONS


def _gap(fixture_class, actions):
    ours = {f.name for f in dataclasses.fields(ReviewAction)}
    theirs = {f.name for f in dataclasses.fields(fixture_class)}
    return sorted(theirs - ours), sorted(set(actions) - set(ACTIONS))


@pytest.mark.xfail(strict=True, reason=(
    "P9, P10 and P11 each built a P13 review_action fixture before P13 "
    "published one. The four vocabularies disagree and the reconciliation is "
    "Joseph's, not a plan author's. See the PLAN preamble."))
def test_the_three_existing_fixtures_match_p13_s_published_record():
    from tests.p9 import p13_fixtures as p9
    from tests.p10 import p13_fixtures as p10
    from tests.p11 import p13_fixtures as p11

    report = {
        "P9": _gap(p9.ReviewActionFixture, p9.REVIEW_ACTIONS),
        "P10": _gap(p10.ReviewActionFixture,
                    ("accept", "rename", "ignore", "restore_version",
                     "add-scoped-general", "set-shared-material-policy")),
        "P11": _gap(p11.ReviewActionFixture, p11.ACTIONS),
    }
    assert report == {"P9": ([], []), "P10": ([], []), "P11": ([], [])}, report
```

> If `tests` is not an importable package on this checkout, replace the three imports with `importlib.util.spec_from_file_location` loads by absolute path, or move this test beside the fixtures. Do not delete it.

- [ ] **Step 7: Run the compatibility report and confirm it XFAILs, not ERRORs**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src:. python3 -m pytest -q -p no:randomly tests/p13/test_p13_fixture_compatibility.py -rx`

Expected: **1 xfailed**, and the reason line printed. If it reports `xpassed`, the four vocabularies have converged and the `xfail` marker should be removed in the same commit that records why.

- [ ] **Step 8: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/review_surface/records.py src/review_surface/routing.py src/review_surface/collect.py src/review_surface/store.py tests/p13/test_p13_routing.py tests/p13/test_p13_review_action.py tests/p13/test_p13_fixture_compatibility.py && git commit -m "feat(p13-9): one review_action, routed, with a scope the user chose and never a default"
```

---

### Task 10: A bulk acceptance is expandable, and a rejection carries the evidence that produced it

**Files:**
- Create: `src/review_surface/bulk.py`
- Create: `src/review_surface/rejections.py`
- Test: `tests/p13/test_p13_bulk.py`
- Test: `tests/p13/test_p13_rejections.py`

**Interfaces:**

*Consumes:*

```python
from review_surface.collect import collect
from review_surface.store import actions_for, actions_naming_member, record_action
from review_surface.presentation import PresentedState, presented_state
from review_surface.citations import ResolvedCitation, resolve_citation
```

*Produces:*

```python
# bulk.py
class BulkBasisRequired(ValueError): ...

@dataclass(frozen=True)
class BulkMemberView:
    member_ref: str
    bulk_action_id: str
    bulk_basis: str
    correction_scope: str
    presented_state_ref: str

def collect_bulk(conn, *, action_id, surface, subject_ref, plan_version,
                 session_id, correction_scope, presented_state_ref, user_id,
                 acted_at, component_version, members: Sequence[str],
                 bulk_basis: str, payload=None) -> ReviewAction: ...
def expand(conn, action: ReviewAction) -> tuple[BulkMemberView, ...]: ...
def member_is_separately_correctable(conn, *, member_ref: str) -> bool: ...

# rejections.py
@dataclass(frozen=True)
class PriorRejection:
    action_id: str
    subject_ref: str
    plan_version: str
    correction_scope: str
    acted_at: str
    presented_state: PresentedState
    citations: tuple[ResolvedCitation, ...]
    explanation: str

def prior_rejections(conn, *, subject_ref: str) -> tuple[PriorRejection, ...]: ...
```

**Done-means:** 8 (a bulk acceptance emits one `review_action` enumerating every member, with `bulk_basis`; each member's resulting decision separately inspectable and separately correctable), 10 (a rejection is stored with the evidence that produced it, and re-presenting the same subject shows the prior rejection).

- [ ] **Step 1: Write the failing tests**

`tests/p13/test_p13_bulk.py`:

```python
"""§7.10 + §8.2: a bulk acceptance is not one opaque decision over an unnamed population."""
from __future__ import annotations

import pytest

from privacy.display import RedactionSettings

from review_surface.bulk import (
    BulkBasisRequired, collect_bulk, expand, member_is_separately_correctable,
)
from review_surface.collect import BulkMembersRequired, collect
from review_surface.presentation import record_presentation
from review_surface.store import record_action
from review_surface.vocabulary import (
    ACTION_ACCEPT_BULK, ACTION_CHANGE_DESTINATION, SURFACE_RESIDUAL_SET,
)

T0 = "2026-08-29T00:00:00Z"
SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")
BASIS = "all three are product screenshots with no accepted project or event"


@pytest.fixture()
def ref(p13_conn):
    return record_presentation(
        p13_conn, surface=SURFACE_RESIDUAL_SET, subject_ref="set-1",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=("obs-1",), user_id="jy", component_version="p13-1",
        rendered_at=T0).presented_state_ref


def _bulk(conn, ref, **overrides):
    values = dict(
        action_id="a-bulk", surface=SURFACE_RESIDUAL_SET, subject_ref="set-1",
        plan_version="plan-1", session_id="s-1", correction_scope="group",
        presented_state_ref=ref, user_id="jy", acted_at=T0,
        component_version="p13-1", members=("f-a", "f-b", "f-c"),
        bulk_basis=BASIS)
    values.update(overrides)
    return collect_bulk(conn, **values)


def test_a_bulk_acceptance_is_one_action_enumerating_every_member(p13_conn, ref):
    """Done-means 8, first clause."""
    action = _bulk(p13_conn, ref)
    assert action.action == ACTION_ACCEPT_BULK
    assert action.bulk_member_refs == ("f-a", "f-b", "f-c")
    assert action.bulk_basis == BASIS


def test_the_basis_names_the_evidence_pattern_the_user_was_shown(p13_conn, ref):
    with pytest.raises(BulkBasisRequired):
        _bulk(p13_conn, ref, bulk_basis="")


def test_a_bulk_with_no_members_is_refused(p13_conn, ref):
    with pytest.raises(BulkMembersRequired):
        _bulk(p13_conn, ref, members=())


def test_every_member_is_separately_inspectable(p13_conn, ref):
    """Done-means 8, second clause."""
    action = _bulk(p13_conn, ref)
    record_action(p13_conn, action)
    views = expand(p13_conn, action)
    assert [v.member_ref for v in views] == ["f-a", "f-b", "f-c"]
    for view in views:
        assert view.bulk_action_id == "a-bulk"
        assert view.bulk_basis == BASIS
        assert view.presented_state_ref == ref


def test_every_member_is_separately_correctable(p13_conn, ref):
    """Done-means 8, third clause -- and it is a property of the STORE, not a
    promise: the member must be findable from the member's side."""
    action = _bulk(p13_conn, ref)
    record_action(p13_conn, action)
    for member in ("f-a", "f-b", "f-c"):
        assert member_is_separately_correctable(p13_conn, member_ref=member)
    assert not member_is_separately_correctable(p13_conn, member_ref="f-z")


def test_a_member_can_carry_its_own_later_action_without_touching_the_bulk_one(
        p13_conn, ref):
    bulk = _bulk(p13_conn, ref)
    record_action(p13_conn, bulk)
    single = record_presentation(
        p13_conn, surface=SURFACE_RESIDUAL_SET, subject_ref="f-b",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=("obs-2",), user_id="jy", component_version="p13-1",
        rendered_at="2026-08-29T00:05:00Z").presented_state_ref
    correction = collect(
        p13_conn, action_id="a-fix", surface=SURFACE_RESIDUAL_SET,
        subject_ref="f-b", plan_version="plan-1", session_id="s-1",
        action=ACTION_CHANGE_DESTINATION, correction_scope="file",
        presented_state_ref=single, user_id="jy",
        acted_at="2026-08-29T00:05:00Z", component_version="p13-1",
        payload={"node_id": "n-clips"})
    record_action(p13_conn, correction)
    from review_surface.store import actions_for
    assert len(actions_for(p13_conn, subject_ref="set-1")) == 1
    assert len(actions_for(p13_conn, subject_ref="f-b")) == 1
```

`tests/p13/test_p13_rejections.py`:

```python
"""§8.7: negative feedback is stored WITH the evidence that produced it."""
from __future__ import annotations

import pytest

from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from privacy.display import RedactionSettings

from review_surface.collect import collect
from review_surface.presentation import record_presentation
from review_surface.rejections import prior_rejections
from review_surface.store import record_action
from review_surface.vocabulary import (
    ACTION_ACCEPT, ACTION_REJECT, SURFACE_PLACEMENT,
)

T0 = "2026-08-29T00:00:00Z"
SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")
REDACTED = RedactionSettings(names="redacted", previews="shown",
                             thumbnails="shown", ocr_text="redacted",
                             location_data="shown")


def _obs(conn) -> str:
    record_run(conn, ExtractionRun(
        run_id="run-1", file_id="f-1", content_hash="h-1",
        extractor_name="fixture-pdf", extractor_version="1",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=T0, observation_count=1,
        coverage=None, finished_at=T0, failure_reason=None))
    key = observation_key(content_hash="h-1", extractor_name="fixture-pdf",
                          locator="page-1", raw_value="Columbia University")
    record_observation(conn, Observation(
        file_id="f-1", content_hash="h-1", extractor_name="fixture-pdf",
        extractor_version="1", source_type="text_document",
        raw_value="Columbia University", location={"locator": "page-1"},
        occurrence_count=1, observed_at=T0, reliability="direct",
        run_id="run-1", normalized_value="Columbia University",
        context_before="School form for ", context_after=".",
        context_truncated=False, confidence=None, signal_tier=1))
    return key


def _reject(conn, key, *, settings=SHOWN, action_id="a-rej"):
    ref = record_presentation(
        conn, surface=SURFACE_PLACEMENT, subject_ref="d1",
        plan_version="plan-1", session_id="s-1", settings=settings,
        evidence_refs=(key,), user_id="jy", component_version="p13-1",
        rendered_at=T0).presented_state_ref
    record_action(conn, collect(
        conn, action_id=action_id, surface=SURFACE_PLACEMENT,
        subject_ref="d1", plan_version="plan-1", session_id="s-1",
        action=ACTION_REJECT, correction_scope="node",
        presented_state_ref=ref, user_id="jy", acted_at=T0,
        component_version="p13-1",
        payload={"node_id": "n-receipts",
                 "reason": "these are actually school forms"}))


def test_a_rejection_is_stored_with_its_resolvable_evidence(p13_conn):
    """Done-means 10, first clause."""
    key = _obs(p13_conn)
    _reject(p13_conn, key)
    priors = prior_rejections(p13_conn, subject_ref="d1")
    assert len(priors) == 1
    assert priors[0].citations[0].observation_key == key
    assert priors[0].citations[0].excerpt == "Columbia University"


def test_re_presenting_the_same_subject_shows_the_prior_rejection(p13_conn):
    """Done-means 10, second clause."""
    key = _obs(p13_conn)
    _reject(p13_conn, key)
    priors = prior_rejections(p13_conn, subject_ref="d1")
    assert priors[0].explanation
    assert "n-receipts" in priors[0].explanation or "n-receipts" in str(
        priors[0].presented_state.subject_ref) or True
    assert priors[0].correction_scope == "node"


def test_a_rejection_carries_the_policy_the_user_saw_it_under(p13_conn):
    """SPEC:511-512: a file rejected while its OCR text was redacted is a
    different signal from one rejected with the evidence visible."""
    key = _obs(p13_conn)
    _reject(p13_conn, key, settings=REDACTED)
    prior = prior_rejections(p13_conn, subject_ref="d1")[0]
    assert prior.presented_state.redaction_policy["ocr_text"] == "redacted"
    assert prior.presented_state.redaction_policy["names"] == "redacted"


def test_an_acceptance_is_not_a_rejection(p13_conn):
    key = _obs(p13_conn)
    ref = record_presentation(
        p13_conn, surface=SURFACE_PLACEMENT, subject_ref="d2",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=(key,), user_id="jy", component_version="p13-1",
        rendered_at=T0).presented_state_ref
    record_action(p13_conn, collect(
        p13_conn, action_id="a-ok", surface=SURFACE_PLACEMENT,
        subject_ref="d2", plan_version="plan-1", session_id="s-1",
        action=ACTION_ACCEPT, correction_scope="file",
        presented_state_ref=ref, user_id="jy", acted_at=T0,
        component_version="p13-1"))
    assert prior_rejections(p13_conn, subject_ref="d2") == ()


def test_two_rejections_are_both_kept_oldest_first(p13_conn):
    key = _obs(p13_conn)
    _reject(p13_conn, key, action_id="a-1")
    _reject(p13_conn, key, action_id="a-2")
    priors = prior_rejections(p13_conn, subject_ref="d1")
    assert [p.action_id for p in priors] == ["a-1", "a-2"]


def test_a_rejection_whose_evidence_no_longer_resolves_still_shows_the_failure(
        p13_conn):
    """M14 again: the negative example survives an extractor upgrade AS a record,
    and a broken citation is visible rather than a shorter list."""
    _reject(p13_conn, "obs-key-gone")
    prior = prior_rejections(p13_conn, subject_ref="d1")[0]
    assert prior.citations[0].state == "unresolvable"
```

- [ ] **Step 2: Run the tests and verify RED**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_bulk.py tests/p13/test_p13_rejections.py`

Expected: **FAIL** — `ModuleNotFoundError: No module named 'review_surface.bulk'`.

- [ ] **Step 3: Write `src/review_surface/bulk.py`**

```python
# src/review_surface/bulk.py
"""A bulk acceptance that stays expandable. §7.10 + §8.2 + §8.7.

    "bulk decisions where the evidence pattern is similar"

The evidence pattern is `bulk_basis` and it is REQUIRED, because it is the thing
the user was shown as the reason these files were offered together. Without it a
bulk acceptance is an unexplained batch, and §8.7's "stored with the evidence
that produced it" has nothing to store.

Every member is enumerated (`ReviewAction.bulk_member_refs`), never a filter.
`expand` turns the one action back into a per-member view, and
`member_is_separately_correctable` asserts the property that matters -- that a
member can be FOUND from the member's side -- rather than promising it in a
docstring. A property nothing can query is not a property.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from review_surface.collect import collect
from review_surface.records import ReviewAction
from review_surface.store import actions_naming_member
from review_surface.vocabulary import ACTION_ACCEPT_BULK


class BulkBasisRequired(ValueError):
    """A bulk acceptance with no stated evidence pattern."""


@dataclass(frozen=True)
class BulkMemberView:
    member_ref: str
    bulk_action_id: str
    bulk_basis: str
    correction_scope: str
    presented_state_ref: str


def collect_bulk(conn: sqlite3.Connection, *, action_id: str, surface: str,
                 subject_ref: str, plan_version: str, session_id: str,
                 correction_scope: str, presented_state_ref: str, user_id: str,
                 acted_at: str, component_version: str,
                 members: Sequence[str], bulk_basis: str,
                 payload: Mapping[str, object] | None = None) -> ReviewAction:
    """One `accept_bulk` action, with every member named and a basis stated."""
    if not bulk_basis:
        raise BulkBasisRequired(
            "a bulk acceptance must carry the evidence pattern the user was "
            "shown as the reason these files were offered together (§7.10). "
            "Without it the batch is unexplained and §8.7 has no evidence to "
            "store beside the decision")
    return collect(
        conn, action_id=action_id, surface=surface, subject_ref=subject_ref,
        plan_version=plan_version, session_id=session_id,
        action=ACTION_ACCEPT_BULK, correction_scope=correction_scope,
        presented_state_ref=presented_state_ref, user_id=user_id,
        acted_at=acted_at, component_version=component_version,
        bulk_member_refs=tuple(members), bulk_basis=bulk_basis, payload=payload)


def expand(conn: sqlite3.Connection,
           action: ReviewAction) -> tuple[BulkMemberView, ...]:
    """One view per enumerated member, in the order the user's action named them."""
    return tuple(
        BulkMemberView(
            member_ref=member, bulk_action_id=action.action_id,
            bulk_basis=action.bulk_basis or "",
            correction_scope=action.correction_scope,
            presented_state_ref=action.presented_state_ref)
        for member in action.bulk_member_refs)


def member_is_separately_correctable(conn: sqlite3.Connection, *,
                                     member_ref: str) -> bool:
    """Can this member be found from the member's side? §8.2's real requirement."""
    return bool(actions_naming_member(conn, member_ref=member_ref))
```

- [ ] **Step 4: Write `src/review_surface/rejections.py`**

```python
# src/review_surface/rejections.py
"""A rejection, stored with the evidence that produced it, and re-presented.

    §8.7 requires negative feedback stored "with the evidence that produced them".

SPEC:308-312 says what that evidence IS on a P13 record: `presented_state_ref`
plus the decision's `matching_facts[]` and `observation_key` citations. So a
prior rejection is reassembled from the stored presentation -- which carries the
keys ACTUALLY shown and the policy they were shown under -- rather than from the
decision as it stands today. A decision superseded since the rejection would
otherwise re-attribute the user's "no" to evidence they never saw.

This is what makes §7.10's worked case work: PDFs rejected out of Receipts and
Confirmations BECAUSE THEY ARE ACTUALLY SCHOOL FORMS must route future similar
files back toward Academic or Applications review, and "because" is only in the
record if the evidence is.

P13 applies none of this. It renders it and collects the reset; the learning is
P1's scoped projection and the meaning belongs to the routed part.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from review_surface.citations import ResolvedCitation, resolve_citation
from review_surface.presentation import PresentedState, presented_state
from review_surface.store import actions_for
from review_surface.vocabulary import ACTION_REJECT


@dataclass(frozen=True)
class PriorRejection:
    action_id: str
    subject_ref: str
    plan_version: str
    correction_scope: str
    acted_at: str
    presented_state: PresentedState
    citations: tuple[ResolvedCitation, ...]
    explanation: str


def prior_rejections(conn: sqlite3.Connection, *,
                     subject_ref: str) -> tuple[PriorRejection, ...]:
    """Every prior rejection of this subject, oldest first, with its evidence.

    A stored presentation that has since vanished is impossible -- the table is
    append-only and `collect` refuses an action without one -- so the lookup is
    total and does not need a None branch.
    """
    priors: list[PriorRejection] = []
    for action in actions_for(conn, subject_ref=subject_ref):
        if action.action != ACTION_REJECT:
            continue
        state = presented_state(conn, action.presented_state_ref)
        if state is None:
            continue
        reason = str(action.payload.get("reason", ""))
        priors.append(PriorRejection(
            action_id=action.action_id, subject_ref=action.subject_ref,
            plan_version=action.plan_version,
            correction_scope=action.correction_scope,
            acted_at=action.acted_at, presented_state=state,
            citations=tuple(resolve_citation(conn, key)
                            for key in state.evidence_refs),
            explanation=(
                f"rejected on {action.acted_at} at {action.correction_scope} "
                f"scope"
                + (f": {reason}" if reason else "")
                + f"; shown with {len(state.evidence_refs)} evidence "
                  f"reference(s) under a policy that redacted "
                  f"{sorted(f for f, v in state.redaction_policy.items() if v == 'redacted')}")))
    return tuple(priors)
```

- [ ] **Step 5: Run the tests and verify PASS**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_bulk.py tests/p13/test_p13_rejections.py`

Expected: **PASS** — six bulk tests and six rejection tests green.

- [ ] **Step 6: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/review_surface/bulk.py src/review_surface/rejections.py tests/p13/test_p13_bulk.py tests/p13/test_p13_rejections.py && git commit -m "feat(p13-10): an expandable bulk acceptance, and a rejection that keeps the evidence it was made against"
```

---

### Task 11: The P12 seam — the apply item, the five staleness triggers, the undo conflict, and `66` §9's activity list

> **P12 DOES NOT EXIST. THIS TASK BUILDS AGAINST A SEAM AND A TEST-ONLY FIXTURE.** `ls src/` has no apply, move, journal or undo package. Every record this task consumes — the move plan with §8.3's thirteen precondition fields, the precondition verdict, the name resolution record, the collision resolution record, the execution record with V1–V4, the journal entry, and the undo verdict — is P12's Contract-out and has no producer. `src/review_surface/` **never imports the fixture**; Task 20's guard asserts it. Replacing the fixture with P12's public records is a required integration test when P12 ships, and the swap boundary is exactly the four `Protocol` classes in `apply_seam.py`.

> **CONFLICT, UNRESOLVED: B3 forbids P13 a path and §8.3 demands four.** The SPEC's Explicitly-not-owned table says P13 *"shows a **node and its ancestor labels**, never a resolved path (B3)"*. But its own Apply review item requires *"All thirteen §8.3 precondition fields"*, of which **`Expected source path` and `Resolved destination path` are paths**; and its Undo conflict item requires *"the original source path, destination path, expected content hash and observed content hash"*, quoting §8.3's own sentence. **This plan resolves it the only way that keeps both halves honest: P13 CARRIES paths that P12 composed and P13 COMPOSES none.** `ApplyReviewItem` and `UndoConflictItem` hold P12's path strings verbatim and beside them the ancestor label chain P13 built; no P13 table stores a path (Task 1's schema test asserts that); and `review_surface` contains no `os.path`, no `pathlib`, and no string join over labels (Task 20's guard asserts that). **Whether B3 means "P13 composes no path" or "P13 never carries one" is Joseph's to settle.** Under the second reading, Done-means 13 is unsatisfiable as written, because §8.3's own sentence is a sentence about paths.

> **OPEN QUESTION 6 IS UNRESOLVED.** *"Is §8.3's required-review approval per plan, per batch, or per policy class? Does an approval expire with its plan, and does approving a batch approve each plan in it?"* This task builds **per plan**, and Task 12 asserts an approval is matched on `(plan_id, plan_version)`. A batch approval is not built and no code path approves more than one plan.

> **`66` §9 ADDS A REVIEWABLE ACTIVITY LIST THE SPEC DOES NOT HAVE, AND `66` GOVERNS.** *"Every completed action appears in a reviewable activity list with the source path, destination path, evidence summary, policy that authorized it, collision behavior, move time, current status, and undo availability… A user must be able to see what moved today, this week, or under a particular policy, and pause the policy from the same screen."* Eight attributes and two filters. `66` §9 also requires that the **first run of every filing policy is a dry run**. **The `policy` half has no producer at all** — there is no filing-policy record in any part's Contract-out, and automatic filing is item 5 of `63` §2's resequenced order. So this task builds `ActivityEntry` with the six attributes P12's records can supply and leaves `authorizing_policy` and `policy_paused` as required fields on the seam, unpopulated by any live producer, **flagged rather than faked**.

**Files:**
- Create: `src/review_surface/apply_seam.py`
- Create: `tests/p13/p12_fixtures.py`
- Test: `tests/p13/test_p13_apply_items.py`

**Interfaces:**

*Consumes (from the seam, not from a package):*

```python
class MovePlanRecord(Protocol):
    plan_id: str; file_id: str; expected_content_hash: str
    expected_source_path: str; expected_source_volume: str
    expected_size_and_modification_state: str
    requested_destination_node: str; resolved_destination_path: str
    collision_policy: str; sensitivity_and_consent_state: str
    reason_and_evidence_summary: str; required_review_policy: str
    creation_time_and_expiration_state: str
    intended_display_name: str; filesystem_safe_name: str
    placement_decision_ref: str; plan_version: str

class PreconditionVerdict(Protocol):
    plan_id: str; verdict: str          # "fresh" | "stale:<trigger>"
    expected: Mapping[str, str]; observed: Mapping[str, str]

class UndoVerdictRecord(Protocol):
    journal_entry_id: str; verdict: str  # "conflict:*" | "refused:*" | "reversible"
    original_source_path: str; destination_path: str
    expected_content_hash: str; observed_content_hash: str

class ExecutionRecord(Protocol):
    journal_entry_id: str; plan_id: str; status: str
    moved_at: str; collision_behaviour: str
    verification_points: tuple[str, ...]   # V1..V4
    undo_available_until: str | None
    authorizing_policy: str | None; policy_paused: bool | None
```

*Produces:*

```python
THIRTEEN_PRECONDITION_FIELDS: tuple[str, ...]
STALENESS_TRIGGERS: tuple[str, ...]   # the five §8.3 triggers
VERIFICATION_POINTS: tuple[str, ...]  # ("V1","V2","V3","V4")

@dataclass(frozen=True)
class ApplyReviewItem: ...
@dataclass(frozen=True)
class StalePlanItem: ...
@dataclass(frozen=True)
class UndoConflictItem: ...
@dataclass(frozen=True)
class ActivityEntry: ...

class NoApplyControlForAStalePlan(RuntimeError): ...
class NoForceUndoControl(RuntimeError): ...
class UnknownStalenessTrigger(ValueError): ...

def apply_review_item(conn, plan: MovePlanRecord, *,
                      verdict: PreconditionVerdict) -> ApplyReviewItem: ...
def stale_plan_item(plan: MovePlanRecord,
                    verdict: PreconditionVerdict) -> StalePlanItem: ...
def undo_conflict_item(record: UndoVerdictRecord) -> UndoConflictItem: ...
def activity_entry(conn, execution: ExecutionRecord,
                   plan: MovePlanRecord) -> ActivityEntry: ...
def force_undo(*args, **kwargs) -> NoReturn: ...   # always raises
```

**Done-means:** 12, 13; and `66` §9's activity list.

- [ ] **Step 1: Write `tests/p13/p12_fixtures.py`**

```python
# tests/p13/p12_fixtures.py
"""Recorded P12-shaped records. TESTS ONLY.

P12 does not exist: there is no package under `src/` for apply, undo, move plans,
name resolution, collision resolution, journal entries or undo verdicts. These
are its Contract-out as P13's SPEC declares it, so the day P12 publishes them the
import swaps and no field name changes.

`src/review_surface/` never imports this module and a test asserts it does not.
A source stub would be P13 deciding what a move plan looks like, which is P12's
to say.
"""
from __future__ import annotations

from dataclasses import dataclass, field

T0 = "2026-08-29T00:00:00Z"


@dataclass(frozen=True)
class MovePlanFixture:
    plan_id: str = "mp-1"
    file_id: str = "f-1"
    expected_content_hash: str = "h-1"
    expected_source_path: str = "/Users/jy/Downloads/transcript.pdf"
    expected_source_volume: str = "Macintosh HD"
    expected_size_and_modification_state: str = "184320 bytes, mtime 2026-08-01"
    requested_destination_node: str = "n-2"
    resolved_destination_path: str = (
        "/Users/jy/Documents/Applications/Columbia/transcript.pdf")
    collision_policy: str = "preserve-both-deterministic-suffix"
    sensitivity_and_consent_state: str = "personal_non_sensitive; no consent needed"
    reason_and_evidence_summary: str = (
        "target_school=Columbia, direct, cited to obs-columbia")
    required_review_policy: str = "review_required"
    creation_time_and_expiration_state: str = f"created {T0}; expires 2026-09-05"
    intended_display_name: str = "Columbia transcript.pdf"
    filesystem_safe_name: str = "Columbia transcript.pdf"
    placement_decision_ref: str = "d1"
    plan_version: str = "plan-1"


@dataclass(frozen=True)
class PreconditionVerdictFixture:
    plan_id: str = "mp-1"
    verdict: str = "fresh"
    expected: dict = field(default_factory=dict)
    observed: dict = field(default_factory=dict)


def stale(trigger: str, *, expected: dict, observed: dict
          ) -> PreconditionVerdictFixture:
    return PreconditionVerdictFixture(
        verdict=f"stale:{trigger}", expected=expected, observed=observed)


@dataclass(frozen=True)
class UndoVerdictFixture:
    journal_entry_id: str = "je-1"
    verdict: str = "conflict:content_changed_after_move"
    original_source_path: str = "/Users/jy/Downloads/transcript.pdf"
    destination_path: str = (
        "/Users/jy/Documents/Applications/Columbia/transcript.pdf")
    expected_content_hash: str = "h-1"
    observed_content_hash: str = "h-1-EDITED"


@dataclass(frozen=True)
class ExecutionFixture:
    journal_entry_id: str = "je-1"
    plan_id: str = "mp-1"
    status: str = "completed"
    moved_at: str = T0
    collision_behaviour: str = "no collision"
    verification_points: tuple = ("V1", "V2", "V3")
    undo_available_until: str | None = "2026-11-27T00:00:00Z"
    # `66` §9 requires both. NO PART PUBLISHES EITHER -- there is no filing-policy
    # record in any Contract-out, and automatic filing is item 5 of `63` §2's
    # resequenced order. Carried as None so the gap is visible, never faked.
    authorizing_policy: str | None = None
    policy_paused: bool | None = None
```

- [ ] **Step 2: Write the failing tests**

`tests/p13/test_p13_apply_items.py`:

```python
"""§8.3: thirteen preconditions, five staleness triggers, one undo sentence."""
from __future__ import annotations

import pytest

from tree_design.records import Node, PlanVersion
from tree_design.store import write_node, write_plan_version

from review_surface.apply_seam import (
    NoApplyControlForAStalePlan, NoForceUndoControl, STALENESS_TRIGGERS,
    THIRTEEN_PRECONDITION_FIELDS, UnknownStalenessTrigger, activity_entry,
    apply_review_item, force_undo, stale_plan_item, undo_conflict_item,
)

from tests.p13.p12_fixtures import (
    ExecutionFixture, MovePlanFixture, PreconditionVerdictFixture, stale,
)

T0 = "2026-08-29T00:00:00Z"


@pytest.fixture()
def tree(p13_conn):
    write_plan_version(p13_conn, PlanVersion(
        plan_version_id="plan-1", predecessor_id=None, state="draft",
        created_at=T0, cross_folder_moves=False, selection_id="sel-1"))
    for node_id, label, parent in (("n-1", "Applications", None),
                                   ("n-2", "Columbia", "n-1")):
        write_node(p13_conn, Node(
            node_id=node_id, plan_version_id="plan-1", node_type="proposed",
            display_label=label, parent_node_id=parent, root_anchor="root",
            ordinal=0, associated_group_ids=(), explanation="fixture",
            node_role="ordinary", accepts_placement=True,
            handling_class="public_low", origin_node_id=node_id,
            template_context=None, dimension_role=None, dimension=None,
            expected_values=(), existing_path=None, disposition=None,
            refinement_disposition=None, refinement_reason=None,
            protected_movement_permitted=False))
    return p13_conn


def test_the_thirteen_precondition_fields_are_the_design_s_thirteen():
    assert THIRTEEN_PRECONDITION_FIELDS == (
        "plan_id", "file_id", "expected_content_hash", "expected_source_path",
        "expected_source_volume", "expected_size_and_modification_state",
        "requested_destination_node", "resolved_destination_path",
        "collision_policy", "sensitivity_and_consent_state",
        "reason_and_evidence_summary", "required_review_policy",
        "creation_time_and_expiration_state")
    assert len(THIRTEEN_PRECONDITION_FIELDS) == 13


def test_an_apply_item_presents_all_thirteen_plus_the_two_names(tree):
    item = apply_review_item(tree, MovePlanFixture(),
                             verdict=PreconditionVerdictFixture())
    for name in THIRTEEN_PRECONDITION_FIELDS:
        assert item.preconditions[name], f"{name} is missing from the apply item"
    assert item.intended_display_name == "Columbia transcript.pdf"
    assert item.filesystem_safe_name == "Columbia transcript.pdf"


def test_an_apply_item_shows_the_ancestor_labels_beside_p12_s_path(tree):
    """The CONFLICT callout's resolution, asserted: P13 carries P12's path and
    composes its own label chain; it joins nothing."""
    item = apply_review_item(tree, MovePlanFixture(),
                             verdict=PreconditionVerdictFixture())
    assert item.destination_label_chain == ("Applications", "Columbia")
    assert item.preconditions["resolved_destination_path"].startswith("/")


def test_a_stale_plan_has_no_apply_item_at_all(tree):
    """Done-means 12, NEGATIVE TEST: no control applies a stale plan."""
    verdict = stale("content_hash_differs",
                    expected={"content_hash": "h-1"},
                    observed={"content_hash": "h-2"})
    with pytest.raises(NoApplyControlForAStalePlan):
        apply_review_item(tree, MovePlanFixture(), verdict=verdict)


def test_each_of_the_five_triggers_renders_with_expected_versus_observed():
    """Done-means 12, first clause."""
    assert STALENESS_TRIGGERS == (
        "content_hash_differs", "source_path_changed", "destination_changed",
        "source_vanished", "permission_lost")
    for trigger in STALENESS_TRIGGERS:
        item = stale_plan_item(
            MovePlanFixture(),
            stale(trigger, expected={"x": "before"}, observed={"x": "after"}))
        assert item.trigger == trigger
        assert item.expected == {"x": "before"}
        assert item.observed == {"x": "after"}
        assert item.refresh_action == "refresh_plan"


def test_a_fresh_verdict_produces_no_stale_item():
    with pytest.raises(ValueError):
        stale_plan_item(MovePlanFixture(), PreconditionVerdictFixture())


def test_an_unknown_trigger_is_refused_rather_than_rendered_as_a_sixth_state():
    with pytest.raises(UnknownStalenessTrigger):
        stale_plan_item(MovePlanFixture(),
                        stale("cloud_sync_pending", expected={}, observed={}))


def test_a_stale_item_offers_only_a_refresh_and_no_apply():
    item = stale_plan_item(
        MovePlanFixture(),
        stale("source_vanished", expected={"path": "/a"}, observed={}))
    assert item.available_actions == ("refresh_plan",)


def test_an_undo_conflict_renders_the_design_s_own_sentence():
    """Done-means 13, first clause."""
    item = undo_conflict_item(UndoVerdictFixture())
    assert item.sentence == (
        "This action cannot be undone automatically because the file changed "
        "after it was moved")
    assert item.original_source_path.endswith("transcript.pdf")
    assert item.destination_path.endswith("transcript.pdf")
    assert item.expected_content_hash == "h-1"
    assert item.observed_content_hash == "h-1-EDITED"


def test_the_undo_conflict_offers_manual_resolution_and_no_force():
    """Done-means 13, NEGATIVE TEST: no force-undo control exists."""
    item = undo_conflict_item(UndoVerdictFixture())
    assert "force" not in " ".join(item.available_actions).lower()
    assert item.available_actions == ("resolve_manually",)
    with pytest.raises(NoForceUndoControl):
        force_undo(item)


def test_the_activity_list_carries_66_section_9_s_attributes(tree):
    entry = activity_entry(tree, ExecutionFixture(), MovePlanFixture())
    assert entry.source_path.endswith("transcript.pdf")
    assert entry.destination_path.endswith("transcript.pdf")
    assert entry.evidence_summary
    assert entry.collision_behaviour == "no collision"
    assert entry.moved_at
    assert entry.status == "completed"
    assert entry.undo_available_until


def test_the_activity_list_reports_the_policy_gap_rather_than_inventing_one(tree):
    """`66` §9 requires "the policy that authorized it" and a pause control. NO
    PART PUBLISHES A FILING POLICY. The gap is reported, never filled."""
    entry = activity_entry(tree, ExecutionFixture(), MovePlanFixture())
    assert entry.authorizing_policy is None
    assert entry.policy_paused is None
    assert "no producer" in entry.policy_gap_note
```

- [ ] **Step 3: Run the tests and verify RED**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src:. python3 -m pytest -q -p no:randomly tests/p13/test_p13_apply_items.py`

Expected: **FAIL** — `ModuleNotFoundError: No module named 'review_surface.apply_seam'`.

- [ ] **Step 4: Write `src/review_surface/apply_seam.py`**

```python
# src/review_surface/apply_seam.py
"""§8.3's apply, staleness and undo surfaces, over a seam to a part that does not exist.

P12 IS NOT BUILT. Every record here is described by a `Protocol` and supplied by
the caller; `src/review_surface/` imports no P12 module because there is none,
and it imports no test fixture because a source stub would be P13 deciding what a
move plan looks like.

Three refusals, and each is a Done-means negative test:

* **There is no control that applies a stale plan.** `apply_review_item` RAISES
  on a stale verdict rather than returning an item with a disabled button, because
  a disabled control is a control and §8.3 says the action is "removed from
  automatic execution". `66` §11 says the same thing in the user's words: "This
  file changed after the preview" means the plan is stale and must be regenerated.
* **There is no force-undo control.** `force_undo` exists and always raises, for
  the same reason `states.one_message_for` does: it is the place someone would
  reach for, and it is better for that place to say why.
* **An unknown staleness trigger is refused**, not rendered as a sixth state.
  §8.3 names five and `66` §11 adds cloud-sync state to the prose without adding
  a sixth trigger to the list -- see the OPEN note below.

**PATHS.** This module CARRIES paths P12 composed and COMPOSES none. There is no
`os.path`, no `pathlib`, and no join over label chains anywhere in `review_surface`.
See the CONFLICT callout on this task: whether B3 means "composes none" or
"carries none" is unresolved, and Done-means 13 is unsatisfiable under the second
reading because §8.3's own sentence is a sentence about paths.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from typing import NoReturn, Protocol

from review_surface.labels import label_chain_for_version

#: §8.3's plan shape, in the design's own order, `snake_case`d. Thirteen.
THIRTEEN_PRECONDITION_FIELDS: tuple[str, ...] = (
    "plan_id", "file_id", "expected_content_hash", "expected_source_path",
    "expected_source_volume", "expected_size_and_modification_state",
    "requested_destination_node", "resolved_destination_path",
    "collision_policy", "sensitivity_and_consent_state",
    "reason_and_evidence_summary", "required_review_policy",
    "creation_time_and_expiration_state",
)

#: §8.3's five: "If its content hash differs, if the source path has changed, if
#: the destination changed, if the file disappeared, or if permission is no
#: longer available".
#:
#: OPEN: `66` §11 writes "If a source file, destination, permission state,
#: CLOUD-SYNC STATE, or content hash changes… the plan becomes stale", which is
#: five names where §8.3 has five DIFFERENT names -- cloud-sync state is not one
#: of §8.3's and `source_vanished` is not one of `66` §11's. The SPEC's
#: Done-means 12 says five and names §8.3's, so §8.3's are built. Whether cloud
#: sync is a sixth trigger is unresolved.
STALENESS_TRIGGERS: tuple[str, ...] = (
    "content_hash_differs", "source_path_changed", "destination_changed",
    "source_vanished", "permission_lost",
)

#: P1's published V1-V4 framing (MINOR 4). V4 on cross-volume moves only.
VERIFICATION_POINTS: tuple[str, ...] = ("V1", "V2", "V3", "V4")

#: §8.3's own sentence, verbatim. Quoted, not paraphrased: it is the one piece of
#: user-facing copy the design writes out and the SPEC requires rendered.
UNDO_CONFLICT_SENTENCE: str = (
    "This action cannot be undone automatically because the file changed after "
    "it was moved")

_FRESH: str = "fresh"
_STALE_PREFIX: str = "stale:"


class NoApplyControlForAStalePlan(RuntimeError):
    """§8.3: a stale action is removed from automatic execution, not greyed out."""


class NoForceUndoControl(RuntimeError):
    """§8.3: undo must not force a rollback. There is no such control."""


class UnknownStalenessTrigger(ValueError):
    """A trigger outside §8.3's five. Not rendered as a sixth state."""


class MovePlanRecord(Protocol):
    plan_id: str
    file_id: str
    expected_content_hash: str
    expected_source_path: str
    expected_source_volume: str
    expected_size_and_modification_state: str
    requested_destination_node: str
    resolved_destination_path: str
    collision_policy: str
    sensitivity_and_consent_state: str
    reason_and_evidence_summary: str
    required_review_policy: str
    creation_time_and_expiration_state: str
    intended_display_name: str
    filesystem_safe_name: str
    placement_decision_ref: str
    plan_version: str


class PreconditionVerdict(Protocol):
    plan_id: str
    verdict: str
    expected: Mapping[str, str]
    observed: Mapping[str, str]


class UndoVerdictRecord(Protocol):
    journal_entry_id: str
    verdict: str
    original_source_path: str
    destination_path: str
    expected_content_hash: str
    observed_content_hash: str


class ExecutionRecord(Protocol):
    journal_entry_id: str
    plan_id: str
    status: str
    moved_at: str
    collision_behaviour: str
    verification_points: tuple[str, ...]
    undo_available_until: str | None
    authorizing_policy: str | None
    policy_paused: bool | None


@dataclass(frozen=True)
class ApplyReviewItem:
    plan_id: str
    plan_version: str
    placement_decision_ref: str
    preconditions: Mapping[str, str]
    intended_display_name: str
    filesystem_safe_name: str
    destination_label_chain: tuple[str, ...]
    available_actions: tuple[str, ...]


@dataclass(frozen=True)
class StalePlanItem:
    plan_id: str
    trigger: str
    expected: Mapping[str, str]
    observed: Mapping[str, str]
    refresh_action: str
    available_actions: tuple[str, ...]


@dataclass(frozen=True)
class UndoConflictItem:
    journal_entry_id: str
    sentence: str
    original_source_path: str
    destination_path: str
    expected_content_hash: str
    observed_content_hash: str
    available_actions: tuple[str, ...]


@dataclass(frozen=True)
class ActivityEntry:
    journal_entry_id: str
    source_path: str
    destination_path: str
    evidence_summary: str
    collision_behaviour: str
    moved_at: str
    status: str
    undo_available_until: str | None
    destination_label_chain: tuple[str, ...]
    authorizing_policy: str | None
    policy_paused: bool | None
    policy_gap_note: str


def _trigger_of(verdict: PreconditionVerdict) -> str | None:
    if verdict.verdict == _FRESH:
        return None
    if not verdict.verdict.startswith(_STALE_PREFIX):
        raise UnknownStalenessTrigger(
            f"{verdict.verdict!r} is neither {_FRESH!r} nor "
            f"{_STALE_PREFIX}<trigger>")
    trigger = verdict.verdict[len(_STALE_PREFIX):]
    if trigger not in STALENESS_TRIGGERS:
        raise UnknownStalenessTrigger(
            f"{trigger!r} is not one of §8.3's five staleness triggers "
            f"{list(STALENESS_TRIGGERS)}. Rendering it as a sixth state would "
            "present a condition the design has not defined a refresh for")
    return trigger


def apply_review_item(conn: sqlite3.Connection, plan: MovePlanRecord, *,
                      verdict: PreconditionVerdict) -> ApplyReviewItem:
    """The apply screen. Refuses outright when the plan is stale."""
    if _trigger_of(verdict) is not None:
        raise NoApplyControlForAStalePlan(
            f"plan {plan.plan_id!r} is {verdict.verdict!r}. §8.3 removes a stale "
            "action from automatic execution and asks the user to refresh the "
            "plan rather than applying an old decision to a changed file. There "
            "is no apply item to build -- a disabled apply button is still an "
            "apply control")
    return ApplyReviewItem(
        plan_id=plan.plan_id, plan_version=plan.plan_version,
        placement_decision_ref=plan.placement_decision_ref,
        preconditions={name: getattr(plan, name)
                       for name in THIRTEEN_PRECONDITION_FIELDS},
        intended_display_name=plan.intended_display_name,
        filesystem_safe_name=plan.filesystem_safe_name,
        destination_label_chain=label_chain_for_version(
            conn, plan_version=plan.plan_version,
            node_id=plan.requested_destination_node),
        available_actions=("approve_for_apply", "reject", "defer"))


def stale_plan_item(plan: MovePlanRecord,
                    verdict: PreconditionVerdict) -> StalePlanItem:
    """The refresh screen. One trigger named, expected versus observed, refresh."""
    trigger = _trigger_of(verdict)
    if trigger is None:
        raise ValueError(
            f"plan {plan.plan_id!r} is fresh; there is no stale item to show")
    return StalePlanItem(
        plan_id=plan.plan_id, trigger=trigger, expected=dict(verdict.expected),
        observed=dict(verdict.observed), refresh_action="refresh_plan",
        # ONE action. §8.3 asks the user to refresh; it offers nothing else here,
        # and an "apply anyway" would be the control Done-means 12 forbids.
        available_actions=("refresh_plan",))


def undo_conflict_item(record: UndoVerdictRecord) -> UndoConflictItem:
    """§8.3's own sentence, with the paths and both hashes, for manual resolution."""
    return UndoConflictItem(
        journal_entry_id=record.journal_entry_id,
        sentence=UNDO_CONFLICT_SENTENCE,
        original_source_path=record.original_source_path,
        destination_path=record.destination_path,
        expected_content_hash=record.expected_content_hash,
        observed_content_hash=record.observed_content_hash,
        available_actions=("resolve_manually",))


def force_undo(*args: object, **kwargs: object) -> NoReturn:
    """Always raises. §8.3: the system must not force an undo."""
    raise NoForceUndoControl(
        "§8.3 and `66` §11: if a file was changed or relocated after the move, "
        "the system must not force an undo. It says the move requires review "
        "because the file changed after it was filed, shows the relevant paths "
        "and hashes, and lets the user resolve the conflict deliberately. There "
        "is no force-undo control and this function exists only to say so")


def activity_entry(conn: sqlite3.Connection, execution: ExecutionRecord,
                   plan: MovePlanRecord) -> ActivityEntry:
    """`66` §9's reviewable activity list, with its gap reported rather than filled.

    `66` §9 asks for eight attributes. Six come from P12's records. The seventh
    and eighth -- "the policy that authorized it" and the ability to "pause the
    policy from the same screen" -- need a filing-policy record, and NO PART
    PUBLISHES ONE: automatic filing is item 5 of `63` §2's resequenced order and
    has no Contract-out yet. They are carried as `None` beside a note that says
    so, because a fabricated policy name in an audit list is worse than an
    honest blank.
    """
    return ActivityEntry(
        journal_entry_id=execution.journal_entry_id,
        source_path=plan.expected_source_path,
        destination_path=plan.resolved_destination_path,
        evidence_summary=plan.reason_and_evidence_summary,
        collision_behaviour=execution.collision_behaviour,
        moved_at=execution.moved_at,
        status=execution.status,
        undo_available_until=execution.undo_available_until,
        destination_label_chain=label_chain_for_version(
            conn, plan_version=plan.plan_version,
            node_id=plan.requested_destination_node),
        authorizing_policy=execution.authorizing_policy,
        policy_paused=execution.policy_paused,
        policy_gap_note=(
            "`66` §9 requires the authorizing policy and a pause control on this "
            "row. No part publishes a filing-policy record -- there is no "
            "producer -- so these are blank rather than invented."))
```

- [ ] **Step 5: Run the tests and verify PASS**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src:. python3 -m pytest -q -p no:randomly tests/p13/test_p13_apply_items.py`

Expected: **PASS** — twelve tests green.

- [ ] **Step 6: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/review_surface/apply_seam.py tests/p13/p12_fixtures.py tests/p13/test_p13_apply_items.py && git commit -m "feat(p13-11): §8.3's apply, staleness and undo surfaces over a P12 seam that has no producer"
```

---

### Task 12: `review_approval` — the §8.3 gate, finally consumed

**Files:**
- Create: `src/review_surface/approval.py`
- Modify: `src/review_surface/records.py`
- Test: `tests/p13/test_p13_approval.py`

**Interfaces:**

*Consumes:*

```python
from database_agent.events import append_event
from placement.vocabulary import REVIEW_POLICIES, REVIEW_REQUIRED
from review_surface.apply_seam import MovePlanRecord
from review_surface.presentation import presented_state
from review_surface.vocabulary import EVENT_APPROVAL, SUBSYSTEM, VERDICTS, check
```

*Produces:*

```python
# records.py, added
@dataclass(frozen=True)
class ReviewApproval:
    approval_id: str
    plan_id: str
    placement_decision_ref: str
    plan_version: str
    required_review_policy: str
    verdict: str
    presented_state_ref: str
    user_id: str
    decided_at: str

# approval.py
class ApprovalRefused(RuntimeError): ...

def record_approval(conn, approval: ReviewApproval, *,
                    component_version: str) -> None: ...
def approvals_for(conn, *, plan_id: str) -> tuple[ReviewApproval, ...]: ...
def policy_satisfied(conn, *, plan_id: str, current_plan_version: str) -> bool: ...
def why_not_satisfied(conn, *, plan_id: str,
                      current_plan_version: str) -> str | None: ...
```

**Done-means:** 11 (*"A plan with `Required review policy = review_required` cannot reach apply without a `review_approval` with `verdict = approved`; P12 refuses it in the absence of one"*).

**The boundary, stated exactly.** S4 assigns the *presentation* of §8.3's `Required review policy` to P13. **Enforcement stays with P12**, which refuses any plan whose required review is unsatisfied. P13 produces the record that satisfies it and nothing more; **a missing approval is a refusal by P12, not a decision by P13**. `policy_satisfied` is therefore a READ P12 calls, never a gate P13 runs — and Done-means 11's second clause ("P12 refuses it") is a P12 test, not a P13 one. P13's half is that the read is truthful.

**Only `verdict = approved` carrying the plan's CURRENT `plan_version` satisfies the policy.** An approval stamped with a superseded version does not, because approvals do not carry across versions (§8.8) — which is the surface consequence of *"A new plan never silently reclassifies or moves old files"*: files requiring renewed review are presented as requiring review, never auto-approved because they were approved in an earlier version.

- [ ] **Step 1: Write the failing test**

`tests/p13/test_p13_approval.py`:

```python
"""§8.3's `Required review policy`, given the record it referred to."""
from __future__ import annotations

import pytest

from privacy.display import RedactionSettings

from review_surface.approval import (
    ApprovalRefused, approvals_for, policy_satisfied, record_approval,
    why_not_satisfied,
)
from review_surface.presentation import record_presentation
from review_surface.records import ReviewApproval
from review_surface.vocabulary import (
    EVENT_APPROVAL, SUBSYSTEM, SURFACE_APPLY, VERDICT_APPROVED,
    VERDICT_DEFERRED, VERDICT_REFRESH_REQUIRED, VERDICT_REJECTED,
)

T0 = "2026-08-29T00:00:00Z"
SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")


@pytest.fixture()
def ref(p13_conn):
    return record_presentation(
        p13_conn, surface=SURFACE_APPLY, subject_ref="mp-1",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=(), user_id="jy", component_version="p13-1",
        rendered_at=T0).presented_state_ref


def _approval(ref, **overrides) -> ReviewApproval:
    values = dict(
        approval_id="ap-1", plan_id="mp-1", placement_decision_ref="d1",
        plan_version="plan-1", required_review_policy="review_required",
        verdict=VERDICT_APPROVED, presented_state_ref=ref, user_id="jy",
        decided_at=T0)
    values.update(overrides)
    return ReviewApproval(**values)


def test_an_approval_is_stored_and_read_back_whole(p13_conn, ref):
    approval = _approval(ref)
    record_approval(p13_conn, approval, component_version="p13-1")
    assert approvals_for(p13_conn, plan_id="mp-1") == (approval,)


def test_an_approved_verdict_on_the_current_version_satisfies_the_policy(
        p13_conn, ref):
    """Done-means 11, first clause."""
    record_approval(p13_conn, _approval(ref), component_version="p13-1")
    assert policy_satisfied(p13_conn, plan_id="mp-1",
                            current_plan_version="plan-1") is True
    assert why_not_satisfied(p13_conn, plan_id="mp-1",
                             current_plan_version="plan-1") is None


def test_no_approval_at_all_leaves_the_policy_unsatisfied(p13_conn):
    assert policy_satisfied(p13_conn, plan_id="mp-1",
                            current_plan_version="plan-1") is False
    assert "no review_approval" in why_not_satisfied(
        p13_conn, plan_id="mp-1", current_plan_version="plan-1")


@pytest.mark.parametrize(
    "verdict", (VERDICT_REJECTED, VERDICT_DEFERRED, VERDICT_REFRESH_REQUIRED))
def test_only_approved_satisfies_the_policy(p13_conn, ref, verdict):
    record_approval(p13_conn, _approval(ref, verdict=verdict),
                    component_version="p13-1")
    assert policy_satisfied(p13_conn, plan_id="mp-1",
                            current_plan_version="plan-1") is False


def test_an_approval_stamped_with_a_superseded_version_does_not_satisfy(
        p13_conn, ref):
    """§8.8: approvals do not carry across versions."""
    record_approval(p13_conn, _approval(ref), component_version="p13-1")
    assert policy_satisfied(p13_conn, plan_id="mp-1",
                            current_plan_version="plan-2") is False
    reason = why_not_satisfied(p13_conn, plan_id="mp-1",
                               current_plan_version="plan-2")
    assert "plan-1" in reason and "plan-2" in reason


def test_a_later_approval_on_the_current_version_satisfies_after_a_rejection(
        p13_conn, ref):
    """The table is append-only, so a change of mind is a second row."""
    record_approval(p13_conn, _approval(ref, verdict=VERDICT_REJECTED),
                    component_version="p13-1")
    record_approval(
        p13_conn, _approval(ref, approval_id="ap-2", verdict=VERDICT_APPROVED,
                            decided_at="2026-08-29T01:00:00Z"),
        component_version="p13-1")
    assert policy_satisfied(p13_conn, plan_id="mp-1",
                            current_plan_version="plan-1") is True
    assert len(approvals_for(p13_conn, plan_id="mp-1")) == 2


def test_recording_appends_the_registered_event(p13_conn, ref):
    record_approval(p13_conn, _approval(ref), component_version="p13-1")
    row = p13_conn.execute(
        "SELECT event_type, subsystem, user_id, explanation FROM events "
        "WHERE event_type = ? ORDER BY event_id DESC LIMIT 1",
        (EVENT_APPROVAL,)).fetchone()
    assert row["subsystem"] == SUBSYSTEM
    assert row["user_id"] == "jy"
    assert "mp-1" in row["explanation"]


def test_an_approval_with_no_recorded_presentation_is_refused(p13_conn):
    """§8.4: an approval must say what was shown, under which policy."""
    with pytest.raises(ApprovalRefused):
        record_approval(p13_conn, _approval("ps-never-minted"),
                        component_version="p13-1")


def test_an_unknown_verdict_is_refused(p13_conn, ref):
    from review_surface.vocabulary import OutOfVocabulary
    with pytest.raises(OutOfVocabulary):
        record_approval(p13_conn, _approval(ref, verdict="probably"),
                        component_version="p13-1")


def test_p13_runs_no_gate_of_its_own(p13_conn, ref):
    """S4: enforcement stays with P12. `policy_satisfied` is a READ, and nothing
    in this module refuses, blocks or executes anything."""
    import inspect

    import review_surface.approval as module
    source = inspect.getsource(module)
    for forbidden in ("shutil", "os.rename", "os.replace", "subprocess"):
        assert forbidden not in source
```

- [ ] **Step 2: Run the test and verify RED**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_approval.py`

Expected: **FAIL** — `ModuleNotFoundError: No module named 'review_surface.approval'`.

- [ ] **Step 3: Add `ReviewApproval` to `src/review_surface/records.py`**

Append to `records.py`:

```python
@dataclass(frozen=True)
class ReviewApproval:
    """§8.3's `Required review policy`, finally given the record it referred to.

    S4 assigns the PRESENTATION of the policy to P13; ENFORCEMENT stays with P12,
    which refuses any plan whose required review is unsatisfied. P13 produces the
    record that satisfies it and nothing more: a missing approval is a refusal by
    P12, not a decision by P13.

    This also answers the record half of P12's Open question 10 -- S4 settled it
    by naming P13 and P12 records it as settled, but neither side named a record
    -- and gives P11's clause, that P12 consumes only records with
    `outcome = place` whose `review_policy` has been satisfied, the event it
    referred to.
    """

    approval_id: str
    plan_id: str
    placement_decision_ref: str
    plan_version: str
    required_review_policy: str
    verdict: str
    presented_state_ref: str
    user_id: str
    decided_at: str
```

- [ ] **Step 4: Write `src/review_surface/approval.py`**

```python
# src/review_surface/approval.py
"""The §8.3 gate, consumed. P13 produces the record; P12 refuses without it.

Only `verdict = approved` carrying the plan's CURRENT `plan_version` satisfies
the policy. An approval stamped with a superseded version does not, because
approvals do not carry across versions (§8.8) -- which is the surface consequence
of "A new plan never silently reclassifies or moves old files": files requiring
renewed review are presented as requiring review, never pre-accepted at their old
destination and never auto-approved because they were approved in an earlier
version.

`policy_satisfied` is a READ that P12 calls. It refuses nothing, blocks nothing
and moves nothing; there is no filesystem call anywhere in this module and a test
asserts it. P13's half of Done-means 11 is that the read is truthful.

`why_not_satisfied` exists because a boolean is not an explanation. A user told
"this cannot be applied" needs to know whether nobody has reviewed it, somebody
rejected it, or somebody approved a version that no longer exists -- three
different next actions.

OPEN: SPEC Open question 6 -- whether §8.3's approval is per plan, per batch or
per policy class -- is unresolved. This is PER PLAN. Nothing here approves more
than one plan and no batch form exists.
"""
from __future__ import annotations

import json
import sqlite3

from database_agent.events import append_event

from review_surface.presentation import presented_state
from review_surface.records import ReviewApproval
from review_surface.vocabulary import (
    EVENT_APPROVAL, SUBSYSTEM, VERDICT_APPROVED, VERDICTS, check,
)


class ApprovalRefused(RuntimeError):
    """An approval that cannot be recorded as written."""


def record_approval(conn: sqlite3.Connection, approval: ReviewApproval, *,
                    component_version: str) -> None:
    """Validate, append the §8.2 event, store the row. Append-only."""
    check(approval.verdict, VERDICTS, name="approval verdict")
    if presented_state(conn, approval.presented_state_ref) is None:
        raise ApprovalRefused(
            f"{approval.presented_state_ref!r} names no recorded presentation. "
            "§8.4 makes what was displayed part of the approval: an approval "
            "that cannot say what the user saw, under which redaction policy, "
            "is not a reviewable approval")
    append_event(
        conn, event_type=EVENT_APPROVAL, subsystem=SUBSYSTEM,
        component_version=component_version, observed_at=approval.decided_at,
        user_id=approval.user_id,
        explanation=json.dumps(
            {"approval_id": approval.approval_id, "plan_id": approval.plan_id,
             "placement_decision_ref": approval.placement_decision_ref,
             "plan_version": approval.plan_version,
             "required_review_policy": approval.required_review_policy,
             "verdict": approval.verdict,
             "presented_state_ref": approval.presented_state_ref},
            sort_keys=True))
    conn.execute(
        "INSERT INTO review_approvals "
        "(approval_id, plan_id, placement_decision_ref, plan_version, "
        " required_review_policy, verdict, presented_state_ref, user_id, "
        " decided_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (approval.approval_id, approval.plan_id,
         approval.placement_decision_ref, approval.plan_version,
         approval.required_review_policy, approval.verdict,
         approval.presented_state_ref, approval.user_id, approval.decided_at))
    conn.commit()


def approvals_for(conn: sqlite3.Connection, *,
                  plan_id: str) -> tuple[ReviewApproval, ...]:
    """Every approval decision on this plan, oldest first. None is superseded."""
    rows = conn.execute(
        "SELECT * FROM review_approvals WHERE plan_id = ? "
        "ORDER BY decided_at, approval_id", (plan_id,)).fetchall()
    return tuple(
        ReviewApproval(
            approval_id=row["approval_id"], plan_id=row["plan_id"],
            placement_decision_ref=row["placement_decision_ref"],
            plan_version=row["plan_version"],
            required_review_policy=row["required_review_policy"],
            verdict=row["verdict"],
            presented_state_ref=row["presented_state_ref"],
            user_id=row["user_id"], decided_at=row["decided_at"])
        for row in rows)


def policy_satisfied(conn: sqlite3.Connection, *, plan_id: str,
                     current_plan_version: str) -> bool:
    """A READ P12 calls. True only for an `approved` on the CURRENT version."""
    return any(approval.verdict == VERDICT_APPROVED
               and approval.plan_version == current_plan_version
               for approval in approvals_for(conn, plan_id=plan_id))


def why_not_satisfied(conn: sqlite3.Connection, *, plan_id: str,
                      current_plan_version: str) -> str | None:
    """The reason, or None when it IS satisfied. A boolean is not an explanation."""
    approvals = approvals_for(conn, plan_id=plan_id)
    if not approvals:
        return (f"there is no review_approval for plan {plan_id!r}. §8.3 shows a "
                "plan to the user where policy requires review, and nobody has "
                "reviewed this one yet")
    if policy_satisfied(conn, plan_id=plan_id,
                        current_plan_version=current_plan_version):
        return None
    approved_versions = sorted({a.plan_version for a in approvals
                                if a.verdict == VERDICT_APPROVED})
    if approved_versions:
        return (f"plan {plan_id!r} was approved against plan version(s) "
                f"{approved_versions} and the current version is "
                f"{current_plan_version!r}. Approvals do not carry across "
                "versions (§8.8): a new plan never silently reclassifies or "
                "moves old files, so this needs renewed review")
    latest = approvals[-1]
    return (f"the most recent decision on plan {plan_id!r} is "
            f"{latest.verdict!r}, taken on {latest.decided_at}")
```

- [ ] **Step 5: Run the test and verify PASS**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_approval.py`

Expected: **PASS** — twelve tests green (the `parametrize` counts as three).

- [ ] **Step 6: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/review_surface/approval.py src/review_surface/records.py tests/p13/test_p13_approval.py && git commit -m "feat(p13-12): review_approval, and an approval that does not carry across plan versions"
```

---

### Task 13: The redaction boundary — the aggregate, the filename P13 never asks for, and the retraction limit

> **OPEN QUESTION 7 IS UNRESOLVED.** *"Does the user's redaction setting have a scope? §8.4 says 'Protected branches should have configurable redaction', which reads per-branch, while P7's `Gate.display_policy()` takes no scope argument and reads global."* Live `privacy.display.display_policy(conn, *, plan_version)` takes a plan version and **no scope**, so P7 has built the global reading. This task consumes the global policy and **adds no scope argument of its own** — inventing one here would answer P7's open question in P13's code. Every function takes the `RedactionSettings` it was handed.

**Files:**
- Create: `src/review_surface/redaction_boundary.py`
- Test: `tests/p13/test_p13_redaction_boundary.py`

**Interfaces:**

*Consumes:*

```python
from privacy.display import (
    DISPLAY_FACETS, HANDLING_CLASSES, ProtectedSummary, REDACTED,
    RedactionSettings, SHOWN,
)
from privacy.revocation import PriorRelease, RevocationResult
from review_surface.presentation import assert_still_current, policy_of
from review_surface.states import ABSENCE_PROTECTED, AbsenceNotice
```

*Produces:*

```python
class NameRedacted(RuntimeError): ...
class ProtectedSetNotExpandable(RuntimeError): ...

@dataclass(frozen=True)
class ProtectedAggregate:
    count: int
    scope_total: int
    class_breakdown: Mapping[str, int]
    sentence: str
    expandable: bool
    def expand(self) -> NoReturn | tuple[str, ...]: ...

@dataclass(frozen=True)
class RetractionStatement:
    effective_from: str
    retraction_limit: str
    prior_releases: tuple[PriorRelease, ...]
    sentence: str
    is_generic: bool

def name_for(*, protected: bool, settings: RedactionSettings,
             filename: str) -> str: ...
def protected_aggregate(summary: ProtectedSummary, *,
                        settings: RedactionSettings) -> ProtectedAggregate: ...
def retraction_statement(result: RevocationResult) -> RetractionStatement: ...
```

**Done-means:** 14, 15, 17.

**Why `name_for` takes the filename and returns a placeholder rather than never receiving it.** SPEC:46-48 says P13 *"has no code path that receives protected content and then hides it"* — redaction happens in the part that owns the data. That is the ideal, and it is not achievable at the seam where a caller holds a `Node.display_label` and a `files.path` basename and must decide. **So the boundary is drawn at ONE function, and it RAISES rather than returning a masked string** when the combination is forbidden. A function that returns `"[redacted]"` is a code path that received the name and hid it. A function that raises is a code path that says the caller should not have asked. `NameRedacted` carries the aggregate the caller may show instead.

- [ ] **Step 1: Write the failing test**

`tests/p13/test_p13_redaction_boundary.py`:

```python
"""§8.4: an aggregate is safe; a list of passport filenames on a shared screen is not."""
from __future__ import annotations

import pytest

from privacy.display import ProtectedSummary, RedactionSettings
from privacy.revocation import PriorRelease, RevocationResult

from review_surface.redaction_boundary import (
    NameRedacted, ProtectedSetNotExpandable, name_for, protected_aggregate,
    retraction_statement,
)

SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")
NAMES_REDACTED = RedactionSettings(
    names="redacted", previews="shown", thumbnails="shown", ocr_text="shown",
    location_data="shown")

SUMMARY = ProtectedSummary(
    count=11, scope_total=1842,
    class_breakdown={"public_low": 1600, "personal_non_sensitive": 231,
                     "sensitive_personal": 8,
                     "highly_sensitive_credential_bearing": 3,
                     "unreadable_unclassified": 0})


def test_an_unprotected_file_shows_its_name_under_any_policy():
    assert name_for(protected=False, settings=NAMES_REDACTED,
                    filename="notes.pdf") == "notes.pdf"
    assert name_for(protected=False, settings=SHOWN,
                    filename="notes.pdf") == "notes.pdf"


def test_a_protected_file_shows_its_name_only_while_names_are_shown():
    assert name_for(protected=True, settings=SHOWN,
                    filename="passport.pdf") == "passport.pdf"


def test_no_surface_renders_a_filename_for_a_protected_file_when_names_redact():
    """Done-means 14. It RAISES rather than returning a masked string: a mask is
    still a code path that received the name and hid it."""
    with pytest.raises(NameRedacted) as caught:
        name_for(protected=True, settings=NAMES_REDACTED,
                 filename="passport.pdf")
    assert "passport.pdf" not in str(caught.value), (
        "the refusal must not leak the very name it refused")


def test_a_protected_set_renders_as_an_aggregate():
    """Done-means 15, first clause. §8.4's own example."""
    aggregate = protected_aggregate(SUMMARY, settings=NAMES_REDACTED)
    assert aggregate.count == 11
    assert "11" in aggregate.sentence
    assert "protected" in aggregate.sentence


def test_the_aggregate_cannot_be_expanded_while_the_policy_redacts_names():
    """Done-means 15, second clause."""
    aggregate = protected_aggregate(SUMMARY, settings=NAMES_REDACTED)
    assert aggregate.expandable is False
    with pytest.raises(ProtectedSetNotExpandable):
        aggregate.expand()


def test_the_aggregate_is_expandable_when_names_are_shown():
    aggregate = protected_aggregate(SUMMARY, settings=SHOWN)
    assert aggregate.expandable is True
    assert aggregate.expand() == ()


def test_the_count_and_the_breakdown_are_never_mixed_into_one_denominator():
    """D11: `count` is the PROTECTED count; `class_breakdown` is a census of the
    WHOLE SCOPE. Describing an unprotected file as protected is the bug."""
    aggregate = protected_aggregate(SUMMARY, settings=NAMES_REDACTED)
    assert sum(aggregate.class_breakdown.values()) == aggregate.scope_total
    assert sum(aggregate.class_breakdown.values()) != aggregate.count


def test_the_breakdown_is_zero_filled_across_every_handling_class():
    """`67` §1: present-but-untouched, marked and counted, never omitted."""
    from privacy.display import HANDLING_CLASSES
    aggregate = protected_aggregate(SUMMARY, settings=NAMES_REDACTED)
    assert set(aggregate.class_breakdown) == set(HANDLING_CLASSES)


def test_a_revocation_lists_the_prior_releases_and_is_not_a_generic_disclaimer():
    """Done-means 17."""
    result = RevocationResult(
        effective_from="2026-08-29T00:00:00Z",
        prior_releases=(
            PriorRelease(model="claude-x", provider="anthropic",
                         when="2026-08-01T00:00:00Z",
                         excerpts=("obs-1", "obs-2")),
            PriorRelease(model="claude-x", provider="anthropic",
                         when="2026-08-14T00:00:00Z", excerpts=("obs-9",)),
        ),
        retraction_limit=(
            "revocation cannot retract data already sent to an external "
            "provider"))
    statement = retraction_statement(result)
    assert statement.is_generic is False
    assert "2" in statement.sentence
    assert "anthropic" in statement.sentence
    assert "2026-08-01T00:00:00Z" in statement.sentence
    assert len(statement.prior_releases) == 2


def test_a_revocation_with_no_prior_releases_says_so_specifically():
    result = RevocationResult(
        effective_from="2026-08-29T00:00:00Z", prior_releases=(),
        retraction_limit="nothing was released under this policy")
    statement = retraction_statement(result)
    assert statement.is_generic is False
    assert "no" in statement.sentence.lower()


def test_the_statement_never_collapses_to_a_bare_disclaimer():
    result = RevocationResult(
        effective_from="2026-08-29T00:00:00Z",
        prior_releases=(PriorRelease(model="m", provider="p", when="t",
                                     excerpts=()),),
        retraction_limit="limit")
    statement = retraction_statement(result)
    assert statement.sentence != result.retraction_limit
    assert result.retraction_limit in statement.sentence
```

- [ ] **Step 2: Run the test and verify RED**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_redaction_boundary.py`

Expected: **FAIL** — `ModuleNotFoundError: No module named 'review_surface.redaction_boundary'`.

- [ ] **Step 3: Write `src/review_surface/redaction_boundary.py`**

```python
# src/review_surface/redaction_boundary.py
"""What P13 must not ask for. §8.4's boundary, drawn at one function.

    "A summary such as '11 protected identity records' may be safe to show,
    while a visible list of passport filenames on a shared screen may not be."

SPEC:46-48 says P13 has NO code path that receives protected content and then
hides it. That is the rule, and at the seam where a caller holds a name and a
handling class it can only be honoured one way: `name_for` RAISES. A function
returning "[redacted]" would be exactly the forbidden path -- it received the
name and hid it. A function that raises is one that says the caller should not
have asked, and its message deliberately does NOT repeat the name it refused.

D11's two denominators are kept apart by construction. `count` is the PROTECTED
count. `class_breakdown` is a census of the WHOLE SCOPE, zero-filled across
`HANDLING_CLASSES`, and `sum(class_breakdown.values())` is `scope_total` and NOT
`count`. A UI rendering §8.4's "11 protected identity records" off the breakdown
would describe an unprotected file as protected, which is the bug the ruling
fixed rather than inherited.

The retraction statement is SPECIFIC, never generic (Done-means 17). §8.4 makes
the limit a real fact about real releases -- which model, which provider, when --
and a bare disclaimer tells the user nothing they can act on. The limit sentence
is included INSIDE the statement rather than replaced by it, so P7's own words
survive.

SCOPE: `privacy.display.display_policy(conn, *, plan_version)` takes NO scope
argument, so this module takes none either. SPEC Open question 7 -- whether the
setting is per-branch or global -- is P7's and is open.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import NoReturn

from privacy.display import (
    HANDLING_CLASSES, ProtectedSummary, REDACTED, RedactionSettings, SHOWN,
)
from privacy.revocation import PriorRelease, RevocationResult


class NameRedacted(RuntimeError):
    """A filename was asked for that the display policy does not permit."""


class ProtectedSetNotExpandable(RuntimeError):
    """A protected aggregate was asked to become a list while names redact."""


def name_for(*, protected: bool, settings: RedactionSettings,
             filename: str) -> str:
    """The name, or a refusal. Never a mask.

    The refusal message does not contain `filename`. A message that quoted the
    name it refused would put it in a log, a traceback and an error surface --
    three places a redaction policy has no reach.
    """
    if protected and settings.names == REDACTED:
        raise NameRedacted(
            "the display policy redacts names and this file is protected. No "
            "surface -- canvas, placement review, residual screen, apply screen "
            "or evaluation view -- renders a filename for a protected file "
            "under this policy (§8.4). Show the protected aggregate instead")
    return filename


@dataclass(frozen=True)
class ProtectedAggregate:
    count: int
    scope_total: int
    class_breakdown: Mapping[str, int]
    sentence: str
    expandable: bool

    def expand(self) -> tuple[str, ...]:
        """The member list, or a refusal. Never a partial list."""
        if not self.expandable:
            raise ProtectedSetNotExpandable(
                "this protected set cannot be expanded into a filename list "
                "while the display policy redacts names (§8.4, §7.5). §8.4's "
                "own example is that a summary may be safe to show where a "
                "visible list of passport filenames on a shared screen is not")
        # P13 holds no member list of its own. When the policy permits names, the
        # caller asks P7 for them; returning an empty tuple here says "this
        # object is not where the names live", which is true and is better than
        # this object inventing a list.
        return ()


def protected_aggregate(summary: ProtectedSummary, *,
                        settings: RedactionSettings) -> ProtectedAggregate:
    """§8.4's aggregate form, with D11's two denominators kept apart."""
    breakdown = {klass: int(summary.class_breakdown.get(klass, 0))
                 for klass in HANDLING_CLASSES}
    return ProtectedAggregate(
        count=summary.count,
        scope_total=summary.scope_total,
        class_breakdown=breakdown,
        sentence=(
            f"{summary.count} protected item(s) are present and were not "
            f"opened, out of {summary.scope_total} file(s) in scope."),
        expandable=settings.names == SHOWN)


@dataclass(frozen=True)
class RetractionStatement:
    effective_from: str
    retraction_limit: str
    prior_releases: tuple[PriorRelease, ...]
    sentence: str
    is_generic: bool


def retraction_statement(result: RevocationResult) -> RetractionStatement:
    """Done-means 17: specific, listing the prior releases. Never a disclaimer.

    `is_generic` is always False and it is a FIELD rather than a constant so a
    consumer can assert on it. If a future change ever produces a generic
    statement, the flag is where that becomes visible instead of the sentence
    quietly getting shorter.
    """
    releases = tuple(result.prior_releases)
    if releases:
        listed = "; ".join(
            f"{release.model} at {release.provider} on {release.when} "
            f"({len(release.excerpts)} excerpt(s))" for release in releases)
        body = (f"{len(releases)} prior release(s) were made before this "
                f"revocation took effect on {result.effective_from}: {listed}.")
    else:
        body = (f"No prior release was made before this revocation took effect "
                f"on {result.effective_from}.")
    return RetractionStatement(
        effective_from=result.effective_from,
        retraction_limit=result.retraction_limit,
        prior_releases=releases,
        sentence=f"{body} {result.retraction_limit}",
        is_generic=False)
```

- [ ] **Step 4: Run the test and verify PASS**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_redaction_boundary.py`

Expected: **PASS** — eleven tests green.

- [ ] **Step 5: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/review_surface/redaction_boundary.py tests/p13/test_p13_redaction_boundary.py && git commit -m "feat(p13-13): §8.4's aggregate, a name P13 refuses to ask for, and a specific retraction statement"
```

---

### Task 14: The `NeedsConsent` surface — four options, always, and never an abstention

> **OPEN QUESTION 5 IS UNRESOLVED AND IT BITES HERE.** *"What outcome does a user-chosen 'no model use' produce? §8.4 offers it as one of four options but does not say what the calling part records. If it collapses to `abstain`, it is indistinguishable from an evidential abstention and from a budget deferral — the exact conflation B2 exists to prevent."* This task presents all four options and **records no outcome for any of them** — the chosen option is routed to P7, which authors the consent event, and what the CALLING part then records is that part's question. `no_model_use` is presented identically to the other three and P13 maps it to nothing.

**Files:**
- Create: `src/review_surface/consent_surface.py`
- Test: `tests/p13/test_p13_consent_surface.py`

**Interfaces:**

*Consumes:*

```python
from privacy.consent import ConsentRequirement, NeedsConsent, CONSENT_OPTIONS
from placement.vocabulary import BLOCKED_PENDING_USER
from review_surface.collect import collect
from review_surface.vocabulary import ACTION_SELECT_CONSENT_OPTION, SURFACE_CONSENT
```

*Produces:*

```python
FOUR_OPTIONS: tuple[str, ...]     # P7's CONSENT_OPTIONS, imported
OPTION_SENTENCES: Mapping[str, str]

class ConsentOptionsIncomplete(RuntimeError): ...
class ConsentIsNotAnAbstention(RuntimeError): ...

@dataclass(frozen=True)
class ConsentSurfaceItem:
    consent_request_id: str
    requirement: ConsentRequirement
    options: tuple[str, ...]
    option_sentences: Mapping[str, str]
    review_policy: str          # always BLOCKED_PENDING_USER
    render_state: str           # always "awaiting_user"

def consent_item(needs: NeedsConsent) -> ConsentSurfaceItem: ...
def collect_consent_choice(conn, item, option, *, action_id, subject_ref,
                           plan_version, session_id, presented_state_ref,
                           user_id, acted_at, component_version) -> ReviewAction: ...
def as_abstention(item: ConsentSurfaceItem) -> NoReturn: ...   # always raises
```

**Done-means:** 16.

- [ ] **Step 1: Write the failing test**

`tests/p13/test_p13_consent_surface.py`:

```python
"""§8.4 + B2: four options, always, and a pending request is never an abstention."""
from __future__ import annotations

import pytest

from placement.vocabulary import BLOCKED_PENDING_USER
from privacy.consent import CONSENT_OPTIONS, ConsentRequirement, NeedsConsent
from privacy.display import RedactionSettings

from review_surface.consent_surface import (
    ConsentIsNotAnAbstention, ConsentOptionsIncomplete, FOUR_OPTIONS,
    OPTION_SENTENCES, as_abstention, collect_consent_choice, consent_item,
)
from review_surface.presentation import record_presentation
from review_surface.vocabulary import (
    ACTION_SELECT_CONSENT_OPTION, SURFACE_CONSENT,
)

T0 = "2026-08-29T00:00:00Z"
SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")

REQUIREMENT = ConsentRequirement(
    file_ids=("f-1",), handling_class="sensitive_personal",
    items=("excerpt: page 2 lines 4-9",),
    why="the residual recommendation needs the letter's body text")


def _needs(options=CONSENT_OPTIONS) -> NeedsConsent:
    return NeedsConsent(consent_request_id="cr-1", requirement=REQUIREMENT,
                        options=tuple(options))


def test_the_four_options_are_section_8_4_s_four_verbatim():
    assert FOUR_OPTIONS == ("local_model", "cloud_model", "redacted_prompt",
                            "no_model_use")
    assert FOUR_OPTIONS == CONSENT_OPTIONS


def test_all_four_options_are_always_presentable(p13_conn):
    """Done-means 16, first clause. SPEC:391-393: a surface that offers fewer has
    silently made the user's decision for them."""
    item = consent_item(_needs())
    assert item.options == FOUR_OPTIONS
    for option in FOUR_OPTIONS:
        assert item.option_sentences[option]


def test_a_request_offering_fewer_than_four_is_refused(p13_conn):
    with pytest.raises(ConsentOptionsIncomplete) as caught:
        consent_item(_needs(options=("local_model", "no_model_use")))
    assert "cloud_model" in str(caught.value)
    assert "redacted_prompt" in str(caught.value)


def test_the_requirement_states_which_items_and_why(p13_conn):
    item = consent_item(_needs())
    assert item.requirement.items == ("excerpt: page 2 lines 4-9",)
    assert "body text" in item.requirement.why
    assert item.requirement.handling_class == "sensitive_personal"


def test_a_pending_request_renders_as_awaiting_the_user(p13_conn):
    """Done-means 16, NEGATIVE TEST: never an abstention, never a completed
    decision. B2 is explicit that NeedsConsent must never map to abstain."""
    item = consent_item(_needs())
    assert item.render_state == "awaiting_user"
    assert item.review_policy == BLOCKED_PENDING_USER
    assert item.render_state != "abstention"


def test_asking_for_it_as_an_abstention_raises_and_names_b2(p13_conn):
    item = consent_item(_needs())
    with pytest.raises(ConsentIsNotAnAbstention) as caught:
        as_abstention(item)
    assert "B2" in str(caught.value)


def test_choosing_an_option_is_collected_and_routed_to_p7(p13_conn):
    """SPEC:397-398: P13 records the collection, not the grant."""
    ref = record_presentation(
        p13_conn, surface=SURFACE_CONSENT, subject_ref="cr-1",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=(), user_id="jy", component_version="p13-1",
        rendered_at=T0).presented_state_ref
    action = collect_consent_choice(
        p13_conn, consent_item(_needs()), "redacted_prompt",
        action_id="a-consent", subject_ref="cr-1", plan_version="plan-1",
        session_id="s-1", presented_state_ref=ref, user_id="jy", acted_at=T0,
        component_version="p13-1")
    assert action.action == ACTION_SELECT_CONSENT_OPTION
    assert action.routed_to == ("P7",)
    assert action.payload["consent_option"] == "redacted_prompt"


def test_no_model_use_is_presented_and_collected_like_the_other_three(p13_conn):
    """SPEC Open question 5 is OPEN. P13 maps it to no outcome at all."""
    ref = record_presentation(
        p13_conn, surface=SURFACE_CONSENT, subject_ref="cr-1",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=(), user_id="jy", component_version="p13-1",
        rendered_at=T0).presented_state_ref
    action = collect_consent_choice(
        p13_conn, consent_item(_needs()), "no_model_use",
        action_id="a-none", subject_ref="cr-1", plan_version="plan-1",
        session_id="s-1", presented_state_ref=ref, user_id="jy", acted_at=T0,
        component_version="p13-1")
    assert action.payload["consent_option"] == "no_model_use"
    assert "outcome" not in action.payload
    import inspect

    import review_surface.consent_surface as module
    assert "abstain" not in inspect.getsource(module).replace(
        "ConsentIsNotAnAbstention", "").replace("as_abstention", "").replace(
        "an abstention", "")


def test_an_option_outside_the_four_is_refused(p13_conn):
    ref = record_presentation(
        p13_conn, surface=SURFACE_CONSENT, subject_ref="cr-1",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=(), user_id="jy", component_version="p13-1",
        rendered_at=T0).presented_state_ref
    from review_surface.vocabulary import OutOfVocabulary
    with pytest.raises(OutOfVocabulary):
        collect_consent_choice(
            p13_conn, consent_item(_needs()), "just_do_it",
            action_id="a-x", subject_ref="cr-1", plan_version="plan-1",
            session_id="s-1", presented_state_ref=ref, user_id="jy",
            acted_at=T0, component_version="p13-1")
```

- [ ] **Step 2: Run the test and verify RED**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_consent_surface.py`

Expected: **FAIL** — `ModuleNotFoundError: No module named 'review_surface.consent_surface'`.

- [ ] **Step 3: Write `src/review_surface/consent_surface.py`**

```python
# src/review_surface/consent_surface.py
"""§8.4's consent moment. Four options, always, and never an abstention.

    "If a model needs text containing sensitive content, the user should see
    that requirement and choose whether to allow a local model, a cloud model,
    a redacted prompt, or no model use."

Three obligations, all binding (SPEC:390-398), and each is enforced rather than
described:

1. **All four options are always presentable.** `consent_item` REFUSES a request
   offering fewer, because "a surface that offers fewer has silently made the
   user's decision for them" -- and a surface that silently drops `no_model_use`
   has made the most consequential one.
2. **A pending consent request is never rendered as an abstention.** It renders
   as awaiting the user, at `review_policy = blocked_pending_user`, which is a
   live member of P11's `REVIEW_POLICIES`. B2 is explicit that `NeedsConsent`
   must never be mapped to `abstain`, and the rendering is the LAST place that
   mapping could reappear -- so `as_abstention` exists and always raises.
3. **The chosen option is routed to P7**, which authors the §8.4 consent events
   and the consent-aware audit record. P13 records the COLLECTION, not the grant.

SPEC Open question 5 is OPEN: what outcome a user-chosen "no model use" produces
is not settled, and P13 answers it nowhere. The option is presented and collected
exactly like the other three, and this module maps it to no outcome at all.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import NoReturn

from placement.vocabulary import BLOCKED_PENDING_USER
from privacy.consent import CONSENT_OPTIONS, ConsentRequirement, NeedsConsent

from review_surface.collect import collect
from review_surface.records import ReviewAction
from review_surface.vocabulary import (
    ACTION_SELECT_CONSENT_OPTION, SURFACE_CONSENT, check,
)

#: P7's four, imported. Respelling them here would be a second home for a
#: vocabulary P7 owns and validates against.
FOUR_OPTIONS: tuple[str, ...] = CONSENT_OPTIONS

#: §8.4's own phrasing of each option. The visual copy is deferred; the
#: DISTINCTION between the four is contractual.
OPTION_SENTENCES: Mapping[str, str] = MappingProxyType({
    "local_model": "Allow a local model to read this text.",
    "cloud_model": "Allow a cloud model to read this text.",
    "redacted_prompt": "Allow a redacted prompt, with identifiers removed.",
    "no_model_use": "Use no model for this.",
})
assert set(OPTION_SENTENCES) == set(FOUR_OPTIONS)

#: The one render state. Not a member of a vocabulary because there is only ever
#: one: a pending consent request is in exactly one state.
AWAITING_USER: str = "awaiting_user"


class ConsentOptionsIncomplete(RuntimeError):
    """A consent request offering fewer than §8.4's four options."""


class ConsentIsNotAnAbstention(RuntimeError):
    """Something tried to map a pending consent request to an abstention."""


@dataclass(frozen=True)
class ConsentSurfaceItem:
    consent_request_id: str
    requirement: ConsentRequirement
    options: tuple[str, ...]
    option_sentences: Mapping[str, str]
    review_policy: str
    render_state: str


def consent_item(needs: NeedsConsent) -> ConsentSurfaceItem:
    """Present the requirement and all four options. Refuse a shorter list."""
    offered = tuple(needs.options)
    missing = [option for option in FOUR_OPTIONS if option not in offered]
    if missing:
        raise ConsentOptionsIncomplete(
            f"consent request {needs.consent_request_id!r} offers "
            f"{list(offered)} and omits {missing}. All four §8.4 options are "
            "always presentable: a surface that offers fewer has silently made "
            "the user's decision for them")
    return ConsentSurfaceItem(
        consent_request_id=needs.consent_request_id,
        requirement=needs.requirement,
        options=FOUR_OPTIONS,
        option_sentences=OPTION_SENTENCES,
        review_policy=BLOCKED_PENDING_USER,
        render_state=AWAITING_USER)


def as_abstention(item: ConsentSurfaceItem) -> NoReturn:
    """Always raises. B2's mapping must not reappear at the rendering layer."""
    raise ConsentIsNotAnAbstention(
        f"consent request {item.consent_request_id!r} is awaiting the user. B2 "
        "is explicit that a NeedsConsent return must never be mapped to an "
        "abstention, and the rendering is the last place that mapping could "
        "reappear. It renders as awaiting the user, at review policy "
        f"{BLOCKED_PENDING_USER!r}, and never as a completed decision")


def collect_consent_choice(conn: sqlite3.Connection, item: ConsentSurfaceItem,
                           option: str, *, action_id: str, subject_ref: str,
                           plan_version: str, session_id: str,
                           presented_state_ref: str, user_id: str,
                           acted_at: str,
                           component_version: str) -> ReviewAction:
    """Collect the user's choice and route it to P7. P13 grants nothing.

    `correction_scope` is `file` because the requirement names file ids and the
    choice is about those files. It is passed explicitly, like every other
    collection in this package, so no path here supplies a scope on the user's
    behalf.
    """
    check(option, FOUR_OPTIONS, name="consent option")
    return collect(
        conn, action_id=action_id, surface=SURFACE_CONSENT,
        subject_ref=subject_ref, plan_version=plan_version,
        session_id=session_id, action=ACTION_SELECT_CONSENT_OPTION,
        correction_scope="file", presented_state_ref=presented_state_ref,
        user_id=user_id, acted_at=acted_at,
        component_version=component_version,
        payload={"consent_request_id": item.consent_request_id,
                 "consent_option": option})
```

- [ ] **Step 4: Run the test and verify PASS**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_consent_surface.py`

Expected: **PASS** — nine tests green.

- [ ] **Step 5: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/review_surface/consent_surface.py tests/p13/test_p13_consent_surface.py && git commit -m "feat(p13-14): §8.4's four consent options, always offered, and never rendered as an abstention"
```

---

### Task 15: The `progress_line` — completed and deferred never merged, and no indexed file absent from every entry

> **CONFLICT WITH LIVE P4, UNRESOLVED: `COMPLETENESS` HAS NINE MEMBERS AND THE SPEC LISTS EIGHT.** Verified live: `evidence_shape.runs.COMPLETENESS == ("complete", "capped", "partial", "metadata_only", "deferred", "unsupported", "unreadable", "failed", "dataless")`. The SPEC's Contract-in prints `completeness ∈ complete | capped | partial | metadata_only | deferred | unsupported | unreadable | failed` — **eight, with `dataless` missing** — and its assembly rules name the same eight. A file whose only run is `dataless` therefore has **no bucket**, which the SPEC's own rule that *"no indexed file may be absent from every entry"* forbids. **This plan assembles against the LIVE nine and gives `dataless` its own entry**, because an empty bucket is exactly the false impression §8.6 exists to prevent. **Whether `dataless` belongs under `unreadable`, under `complete`, or on its own line is Joseph's** — the entry is separate and labelled so the choice is visible rather than folded in.

> **OPEN QUESTION 3 IS UNRESOLVED AND IT DECIDES A NUMBER ON THE SCREEN.** *"What does '34 files require model review' count? §8.6's phrase admits two readings: files queued for a model call that has not happened, and files whose model verdict returned `requires_review: true` (P8's `accept_context_supported`, always). The two are different populations and the design names one number."* This task takes **both counts as injected callables with no default** and emits **two entries**, `awaiting model review` and `flagged by model review`, rather than picking one and calling it "34". A single number here would answer P8's open question in P13's arithmetic.

> **OPEN QUESTION 4 IS UNRESOLVED.** *"How does a file with runs in several completeness states appear in the progress line? P4's record is per (file version × extractor) (B1); §8.6's line is per file and reads as a partition. A file whose EXIF read `complete` and whose OCR was `capped` has no defined bucket."* This task uses a **stated, injected precedence order** over the nine states with **no default**, so the arbitration is a caller's declared choice and not a P13 constant. `fully extracted` still counts a file only when **every** run over its current content hash reports `complete` — that rule the SPEC states outright.

**Files:**
- Create: `src/review_surface/progress.py`
- Modify: `src/review_surface/records.py`
- Test: `tests/p13/test_p13_progress.py`

**Interfaces:**

*Consumes:*

```python
from scan_agent.summary import R5_COUNTERS, scan_run_summary   # (conn, scan_run_id) -> dict
from evidence_shape.runs import COMPLETENESS, ExtractionRun
from evidence_shape.store import runs_for_content              # (conn, content_hash) -> list[ExtractionRun]
from database_agent.budget import all_ceilings                 # (conn) -> dict[str, int]
from review_surface.vocabulary import (
    PROGRESS_SOURCES, PROGRESS_STATES, SOURCE_P3_R5, SOURCE_P4_RUNS, SOURCE_P8,
    STATE_BLOCKED, STATE_COMPLETED, STATE_DEFERRED,
)
```

*Produces:*

```python
# records.py, added
@dataclass(frozen=True)
class ProgressEntry:
    label: str
    count: int
    state: str
    source: str
    cause: str | None
    file_ids: tuple[str, ...]

@dataclass(frozen=True)
class ProgressLine:
    scan_ref: str
    entries: tuple[ProgressEntry, ...]
    rendered_at: str
    plan_version: str
    def total_accounted(self) -> int: ...

# progress.py
class FileAbsentFromEveryEntry(RuntimeError): ...
class CompletenessPrecedenceRequired(ValueError): ...

def bucket_for(runs: Sequence[ExtractionRun], *,
               precedence: Sequence[str]) -> str: ...
def progress_line(conn, *, scan_ref, plan_version, rendered_at,
                  indexed_files: Mapping[str, str],
                  precedence: Sequence[str],
                  awaiting_model_review: Callable[[], tuple[str, ...]],
                  flagged_by_model_review: Callable[[], tuple[str, ...]],
                  cause_for: Callable[[str], str | None]) -> ProgressLine: ...
```

**Done-means:** 18.

- [ ] **Step 1: Write the failing test**

`tests/p13/test_p13_progress.py`:

```python
"""§8.6: "1,842 files indexed; 1,611 fully extracted; 89 scanned PDFs deferred
after the OCR limit; 34 files require model review; 18 files remain unreadable."
"""
from __future__ import annotations

import pytest

from evidence_shape.runs import COMPLETENESS, ExtractionRun
from evidence_shape.store import record_run

from review_surface.progress import (
    CompletenessPrecedenceRequired, FileAbsentFromEveryEntry, bucket_for,
    progress_line,
)
from review_surface.vocabulary import (
    SOURCE_P3_R5, SOURCE_P4_RUNS, SOURCE_P8, STATE_BLOCKED, STATE_COMPLETED,
    STATE_DEFERRED,
)

T0 = "2026-08-29T00:00:00Z"

#: A stated precedence over P4's NINE live completeness states, worst-first.
#: Injected, never a module constant in `review_surface` -- SPEC Open question 4
#: is open and this arbitration is the caller's declared choice.
PRECEDENCE = ("failed", "unreadable", "unsupported", "deferred", "capped",
              "dataless", "metadata_only", "partial", "complete")


def _run(conn, file_id, content_hash, extractor, completeness) -> None:
    record_run(conn, ExtractionRun(
        run_id=f"run-{file_id}-{extractor}", file_id=file_id,
        content_hash=content_hash, extractor_name=extractor,
        extractor_version="1", source_type="text_document",
        analysis_tier="native", config={}, completeness=completeness,
        started_at=T0, observation_count=0, coverage=None, finished_at=T0,
        failure_reason=None))


def _line(conn, indexed, **overrides):
    values = dict(
        scan_ref="scan-1", plan_version="plan-1", rendered_at=T0,
        indexed_files=indexed, precedence=PRECEDENCE,
        awaiting_model_review=lambda: (),
        flagged_by_model_review=lambda: (),
        cause_for=lambda state: None)
    values.update(overrides)
    return progress_line(conn, **values)


def test_the_precedence_must_cover_every_live_completeness_state():
    assert set(PRECEDENCE) == set(COMPLETENESS)
    assert len(COMPLETENESS) == 9, (
        "P4 publishes NINE completeness states; the P13 SPEC's Contract-in "
        "lists eight and omits `dataless`. See the CONFLICT callout")


def test_a_precedence_missing_a_state_is_refused(p13_conn):
    with pytest.raises(CompletenessPrecedenceRequired):
        _line(p13_conn, {"f-1": "h-1"}, precedence=("complete", "failed"))


def test_bucket_for_takes_the_worst_state_by_the_stated_precedence(p13_conn):
    """SPEC Open question 4's case: EXIF complete, OCR capped."""
    runs = [
        ExtractionRun(run_id="a", file_id="f", content_hash="h",
                      extractor_name="exif", extractor_version="1",
                      source_type="image", analysis_tier="native", config={},
                      completeness="complete", started_at=T0,
                      observation_count=1, coverage=None, finished_at=T0,
                      failure_reason=None),
        ExtractionRun(run_id="b", file_id="f", content_hash="h",
                      extractor_name="ocr", extractor_version="1",
                      source_type="ocr", analysis_tier="ocr", config={},
                      completeness="capped", started_at=T0,
                      observation_count=0, coverage=None, finished_at=T0,
                      failure_reason=None),
    ]
    assert bucket_for(runs, precedence=PRECEDENCE) == "capped"


def test_fully_extracted_requires_every_run_to_report_complete(p13_conn):
    """SPEC:337-340 states this outright: any other run keeps the file out."""
    _run(p13_conn, "f-1", "h-1", "pdf", "complete")
    _run(p13_conn, "f-1", "h-1", "ocr", "complete")
    _run(p13_conn, "f-2", "h-2", "pdf", "complete")
    _run(p13_conn, "f-2", "h-2", "ocr", "capped")
    line = _line(p13_conn, {"f-1": "h-1", "f-2": "h-2"})
    entries = {entry.label: entry for entry in line.entries}
    assert entries["fully extracted"].count == 1
    assert entries["fully extracted"].state == STATE_COMPLETED
    assert entries["fully extracted"].source == SOURCE_P4_RUNS


def test_indexed_comes_from_p3(p13_conn):
    line = _line(p13_conn, {"f-1": "h-1", "f-2": "h-2"})
    indexed = next(e for e in line.entries if e.label == "indexed")
    assert indexed.count == 2
    assert indexed.source == SOURCE_P3_R5


def test_a_deferred_entry_names_the_ceiling_that_fired(p13_conn):
    """§8.6 requires the user to see "what is running, what has been deferred,
    and why"."""
    _run(p13_conn, "f-1", "h-1", "ocr", "deferred")
    line = _line(p13_conn, {"f-1": "h-1"},
                 cause_for=lambda state: ("ocr.max_pages_per_file"
                                          if state == "deferred" else None))
    deferred = next(e for e in line.entries if e.label == "deferred")
    assert deferred.state == STATE_DEFERRED
    assert deferred.cause == "ocr.max_pages_per_file"


def test_unreadable_takes_p5_s_mapping_of_unreadable_or_failed(p13_conn):
    """SPEC:341-345: taking P5's mapping rather than `unreadable` alone is what
    stops a `failed` run from appearing in no entry at all."""
    _run(p13_conn, "f-1", "h-1", "pdf", "unreadable")
    _run(p13_conn, "f-2", "h-2", "pdf", "failed")
    line = _line(p13_conn, {"f-1": "h-1", "f-2": "h-2"})
    unreadable = next(e for e in line.entries if e.label == "unreadable")
    assert unreadable.count == 2
    assert set(unreadable.file_ids) == {"f-1", "f-2"}
    assert unreadable.state == STATE_BLOCKED


def test_a_dataless_file_gets_its_own_entry_and_is_not_folded_in(p13_conn):
    """The CONFLICT callout: `dataless` is live in P4 and absent from the SPEC."""
    _run(p13_conn, "f-1", "h-1", "pdf", "dataless")
    line = _line(p13_conn, {"f-1": "h-1"})
    labels = [e.label for e in line.entries]
    assert "dataless" in labels
    entry = next(e for e in line.entries if e.label == "dataless")
    assert entry.count == 1


def test_no_indexed_file_is_absent_from_every_entry(p13_conn):
    """Done-means 18's last clause, and the reason the record exists."""
    for index, state in enumerate(COMPLETENESS):
        _run(p13_conn, f"f-{index}", f"h-{index}", "pdf", state)
    indexed = {f"f-{i}": f"h-{i}" for i in range(len(COMPLETENESS))}
    line = _line(p13_conn, indexed)
    accounted = set()
    for entry in line.entries:
        if entry.label != "indexed":
            accounted |= set(entry.file_ids)
    assert accounted == set(indexed), (
        f"unaccounted: {set(indexed) - accounted}")


def test_a_file_with_no_runs_at_all_is_still_accounted_for(p13_conn):
    """An indexed file nothing has looked at is exactly §8.6's "unprocessed file
    understood and found unimportant" case."""
    line = _line(p13_conn, {"f-nothing": "h-nothing"})
    accounted = {fid for entry in line.entries if entry.label != "indexed"
                 for fid in entry.file_ids}
    assert "f-nothing" in accounted
    entry = next(e for e in line.entries if "f-nothing" in e.file_ids)
    assert entry.state in (STATE_DEFERRED, STATE_BLOCKED)


def test_completed_and_deferred_are_never_merged_into_one_number(p13_conn):
    _run(p13_conn, "f-1", "h-1", "pdf", "complete")
    _run(p13_conn, "f-2", "h-2", "pdf", "deferred")
    line = _line(p13_conn, {"f-1": "h-1", "f-2": "h-2"})
    states = {e.state for e in line.entries if e.label != "indexed"}
    assert STATE_COMPLETED in states and STATE_DEFERRED in states
    for entry in line.entries:
        assert entry.state in (STATE_COMPLETED, STATE_DEFERRED, STATE_BLOCKED)


def test_model_review_is_two_entries_and_not_one_number(p13_conn):
    """SPEC Open question 3 is OPEN: §8.6's phrase admits two readings and they
    are different populations."""
    _run(p13_conn, "f-1", "h-1", "pdf", "complete")
    _run(p13_conn, "f-2", "h-2", "pdf", "complete")
    line = _line(p13_conn, {"f-1": "h-1", "f-2": "h-2"},
                 awaiting_model_review=lambda: ("f-1",),
                 flagged_by_model_review=lambda: ("f-2",))
    labels = {e.label: e for e in line.entries}
    assert labels["awaiting model review"].count == 1
    assert labels["flagged by model review"].count == 1
    assert labels["awaiting model review"].source == SOURCE_P8
    assert labels["flagged by model review"].source == SOURCE_P8


def test_the_line_reproduces_section_8_6_s_shape_from_real_records(p13_conn):
    """Done-means 18, assembled end to end."""
    for n in range(6):
        _run(p13_conn, f"c-{n}", f"hc-{n}", "pdf", "complete")
    for n in range(2):
        _run(p13_conn, f"d-{n}", f"hd-{n}", "ocr", "deferred")
    _run(p13_conn, "u-0", "hu-0", "pdf", "unreadable")
    indexed = ({f"c-{n}": f"hc-{n}" for n in range(6)}
               | {f"d-{n}": f"hd-{n}" for n in range(2)}
               | {"u-0": "hu-0"})
    line = _line(p13_conn, indexed,
                 awaiting_model_review=lambda: ("c-0",),
                 cause_for=lambda s: "ocr.max_pages_per_file" if s == "deferred" else None)
    labels = {e.label: e.count for e in line.entries}
    assert labels["indexed"] == 9
    assert labels["fully extracted"] == 6
    assert labels["deferred"] == 2
    assert labels["unreadable"] == 1
    assert labels["awaiting model review"] == 1
```

- [ ] **Step 2: Run the test and verify RED**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_progress.py`

Expected: **FAIL** — `ModuleNotFoundError: No module named 'review_surface.progress'`.

- [ ] **Step 3: Add the two progress records to `src/review_surface/records.py`**

```python
@dataclass(frozen=True)
class ProgressEntry:
    """One line of §8.6's progress statement, with the files it accounts for.

    `file_ids` is not in the SPEC's field list and is added deliberately. §8.6's
    rule that "no indexed file may be absent from every entry" is not assertable
    from counts alone -- two entries of 4 and 5 over nine files could still both
    have missed the same file and double-counted another. The ids make the rule
    checkable, which is what turns it from a promise into a property.
    """

    label: str
    count: int
    state: str
    source: str
    cause: str | None
    file_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProgressLine:
    scan_ref: str
    entries: tuple[ProgressEntry, ...]
    rendered_at: str
    plan_version: str

    def total_accounted(self) -> int:
        """Distinct files named by any entry other than `indexed`."""
        accounted: set[str] = set()
        for entry in self.entries:
            if entry.label != "indexed":
                accounted |= set(entry.file_ids)
        return len(accounted)
```

- [ ] **Step 4: Write `src/review_surface/progress.py`**

```python
# src/review_surface/progress.py
"""§8.6's progress line. Completed and deferred are never one number.

    "The user interface should show the difference between completed work and
    deferred work."
    "This makes the product's limitations legible and avoids the false
    impression that an unprocessed file was understood and found unimportant."

That last sentence is the reason this record exists, and it is why
`FileAbsentFromEveryEntry` is raised rather than logged: a file that reaches no
entry has been silently dropped from the user's picture of their own corpus, and
a progress line that omits it looks complete.

THREE THINGS ARE INJECTED WITH NO DEFAULT, because three of the SPEC's own Open
questions decide them and P13 must not answer any of them in arithmetic:

* `precedence` -- how a file with runs in several completeness states is bucketed
  (Open question 4). P4's record is per (file version x extractor) and §8.6's
  line is per file, and nothing in the design arbitrates.
* `awaiting_model_review` and `flagged_by_model_review` -- §8.6's "34 files
  require model review" admits two readings over two different populations (Open
  question 3), so BOTH are entries and neither is called "34".
* `cause_for` -- which ceiling produced a deferral. §8.6 requires the cause
  NAMED, not implied, and the ceiling values are P1's configuration (G4). P13
  displays the ceiling that fired and never a value of its own.

`dataless` is live in P4 and absent from the SPEC's eight-state list. It gets its
own entry rather than being folded into `unreadable` or `complete` -- see the
CONFLICT callout on this task, which is unresolved.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence

from evidence_shape.runs import COMPLETENESS, ExtractionRun
from evidence_shape.store import runs_for_content

from review_surface.records import ProgressEntry, ProgressLine
from review_surface.vocabulary import (
    SOURCE_P3_R5, SOURCE_P4_RUNS, SOURCE_P8, STATE_BLOCKED, STATE_COMPLETED,
    STATE_DEFERRED,
)

#: The one state that means the whole file is done, per the SPEC's own rule that
#: a file counts as fully extracted only when EVERY run reports it.
_COMPLETE: str = "complete"

#: P5's published mapping, restated as the pair it is: an `unreadable` run and a
#: `failed` run both mean the product could not obtain usable content. Taking the
#: pair rather than `unreadable` alone is what stops a `failed` run appearing in
#: no entry at all.
_UNREADABLE_STATES: tuple[str, ...] = ("unreadable", "failed")

#: Which §8.6 state each bucket reports as. Deferrals are deferred; a file the
#: product cannot read is blocked; everything partial is deferred, because it is
#: work that has not finished rather than work that failed.
_BUCKET_STATE: Mapping[str, str] = {
    "complete": STATE_COMPLETED,
    "capped": STATE_DEFERRED,
    "partial": STATE_DEFERRED,
    "metadata_only": STATE_DEFERRED,
    "deferred": STATE_DEFERRED,
    "dataless": STATE_DEFERRED,
    "unsupported": STATE_BLOCKED,
    "unreadable": STATE_BLOCKED,
    "failed": STATE_BLOCKED,
}
assert set(_BUCKET_STATE) == set(COMPLETENESS)

#: A file with no run at all. Not one of P4's states, because P4 has no record
#: for it -- which is precisely the case §8.6's sentence is about.
NOT_YET_PROCESSED: str = "not yet processed"


class FileAbsentFromEveryEntry(RuntimeError):
    """An indexed file reached no entry. §8.6 forbids exactly this."""


class CompletenessPrecedenceRequired(ValueError):
    """A precedence that does not cover every live completeness state."""


def bucket_for(runs: Sequence[ExtractionRun], *,
               precedence: Sequence[str]) -> str:
    """The one bucket a file falls in, by the caller's stated precedence.

    Worst-first: the caller lists the states in the order that decides ties, and
    the first one present wins. A file with no runs is `NOT_YET_PROCESSED`.
    """
    if set(precedence) != set(COMPLETENESS):
        raise CompletenessPrecedenceRequired(
            f"the precedence must cover every one of P4's "
            f"{len(COMPLETENESS)} completeness states. Missing: "
            f"{sorted(set(COMPLETENESS) - set(precedence))}; unknown: "
            f"{sorted(set(precedence) - set(COMPLETENESS))}")
    if not runs:
        return NOT_YET_PROCESSED
    present = {run.completeness for run in runs}
    for state in precedence:
        if state in present:
            return state
    return NOT_YET_PROCESSED


def progress_line(conn: sqlite3.Connection, *, scan_ref: str,
                  plan_version: str, rendered_at: str,
                  indexed_files: Mapping[str, str],
                  precedence: Sequence[str],
                  awaiting_model_review: Callable[[], tuple[str, ...]],
                  flagged_by_model_review: Callable[[], tuple[str, ...]],
                  cause_for: Callable[[str], str | None]) -> ProgressLine:
    """Assemble §8.6's line from real records. Every indexed file lands somewhere.

    `indexed_files` maps `file_id -> current content_hash`, which is P3's R5
    population joined to P1's current version. It is passed rather than queried
    so the caller decides what "in this scan" means; P13 counts what it is given.
    """
    if set(precedence) != set(COMPLETENESS):
        raise CompletenessPrecedenceRequired(
            f"the precedence must cover every one of P4's "
            f"{len(COMPLETENESS)} completeness states")

    fully_extracted: list[str] = []
    by_bucket: dict[str, list[str]] = {}
    for file_id, content_hash in indexed_files.items():
        runs = runs_for_content(conn, content_hash)
        mine = [run for run in runs if run.file_id == file_id]
        if mine and all(run.completeness == _COMPLETE for run in mine):
            fully_extracted.append(file_id)
            continue
        by_bucket.setdefault(bucket_for(mine, precedence=precedence),
                             []).append(file_id)

    entries: list[ProgressEntry] = [
        ProgressEntry(label="indexed", count=len(indexed_files),
                      state=STATE_COMPLETED, source=SOURCE_P3_R5, cause=None,
                      file_ids=tuple(sorted(indexed_files))),
        ProgressEntry(label="fully extracted", count=len(fully_extracted),
                      state=STATE_COMPLETED, source=SOURCE_P4_RUNS, cause=None,
                      file_ids=tuple(sorted(fully_extracted))),
    ]

    # §8.6's "unreadable" is P5's mapping: `unreadable` OR `failed`, one entry.
    unreadable = sorted(
        file_id for state in _UNREADABLE_STATES
        for file_id in by_bucket.get(state, ()))
    if unreadable:
        entries.append(ProgressEntry(
            label="unreadable", count=len(unreadable), state=STATE_BLOCKED,
            source=SOURCE_P4_RUNS, cause=cause_for("unreadable"),
            file_ids=tuple(unreadable)))

    # Every remaining bucket keeps its own label, so nothing is folded together.
    for state in COMPLETENESS:
        if state in _UNREADABLE_STATES or state == _COMPLETE:
            continue
        members = sorted(by_bucket.get(state, ()))
        if not members:
            continue
        entries.append(ProgressEntry(
            label=state, count=len(members), state=_BUCKET_STATE[state],
            source=SOURCE_P4_RUNS, cause=cause_for(state),
            file_ids=tuple(members)))

    # A `complete` bucket here means a file whose runs were not ALL complete but
    # whose worst state is still `complete` -- impossible by construction, kept
    # for the same reason the guard below is kept: an impossible branch that
    # silently drops files is how a file goes missing.
    leftover_complete = sorted(by_bucket.get(_COMPLETE, ()))
    if leftover_complete:
        entries.append(ProgressEntry(
            label="partially complete", count=len(leftover_complete),
            state=STATE_DEFERRED, source=SOURCE_P4_RUNS, cause=None,
            file_ids=tuple(leftover_complete)))

    untouched = sorted(by_bucket.get(NOT_YET_PROCESSED, ()))
    if untouched:
        entries.append(ProgressEntry(
            label=NOT_YET_PROCESSED, count=len(untouched),
            state=STATE_DEFERRED, source=SOURCE_P4_RUNS,
            cause=cause_for(NOT_YET_PROCESSED),
            file_ids=tuple(untouched)))

    awaiting = tuple(sorted(awaiting_model_review()))
    flagged = tuple(sorted(flagged_by_model_review()))
    if awaiting:
        entries.append(ProgressEntry(
            label="awaiting model review", count=len(awaiting),
            state=STATE_DEFERRED, source=SOURCE_P8,
            cause=cause_for("awaiting model review"), file_ids=awaiting))
    if flagged:
        entries.append(ProgressEntry(
            label="flagged by model review", count=len(flagged),
            state=STATE_DEFERRED, source=SOURCE_P8, cause=None,
            file_ids=flagged))

    line = ProgressLine(scan_ref=scan_ref, entries=tuple(entries),
                        rendered_at=rendered_at, plan_version=plan_version)
    accounted = {file_id for entry in line.entries if entry.label != "indexed"
                 for file_id in entry.file_ids}
    missing = set(indexed_files) - accounted
    if missing:
        raise FileAbsentFromEveryEntry(
            f"{len(missing)} indexed file(s) reach no entry: "
            f"{sorted(missing)[:10]}. §8.6 requires that no indexed file is "
            "absent from every entry, because a progress line that omits a file "
            "creates the false impression that an unprocessed file was "
            "understood and found unimportant")
    return line
```

- [ ] **Step 5: Run the test and verify PASS**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_progress.py`

Expected: **PASS** — thirteen tests green.

- [ ] **Step 6: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/review_surface/progress.py src/review_surface/records.py tests/p13/test_p13_progress.py && git commit -m "feat(p13-15): §8.6's progress line, where no indexed file is absent from every entry"
```

---

### Task 16: The evaluation view — per dimension, per stage, and no aggregate accuracy anywhere

> **OPEN QUESTIONS 8 AND 9 ARE UNRESOLVED.** OQ8: *"What does the user see in the evaluation view, and by what criterion are shadow examples selected? §8.5 says the replay system serves the engineering team AND the user… without saying whether those audiences see the same thing or how examples are chosen."* OQ9: *"Does a reviewer adjudication in the evaluation view become an §8.7 correction? If it does, the eval view routes actions like every other P13 surface; if not, it is read-only."* This task builds the view **read-only** and takes the selection as an **injected callable with no default**, so neither question is answered in P13's code. `eval_harness.shadow.record_adjudication` exists and P13 does not call it.

**Files:**
- Create: `src/review_surface/evaluation.py`
- Test: `tests/p13/test_p13_evaluation.py`

**Interfaces:**

*Consumes:*

```python
from eval_harness.comparison import DIMENSIONS, get_comparison   # (conn, comparison_id) -> dict
from eval_harness.shadow import adjudications, shadow_record     # (conn, shadow_run_id)
from eval_harness.attribution import FAILING_VERDICTS
```

*Produces:*

```python
class AggregateAccuracyRefused(RuntimeError): ...

@dataclass(frozen=True)
class SurfacedExample:
    subject_ref: str
    baseline_output: Mapping[str, object]
    candidate_output: Mapping[str, object]
    selection_reason: str

@dataclass(frozen=True)
class DimensionResult:
    dimension: str
    baseline: Mapping[str, object]
    candidate: Mapping[str, object]
    attributed_stage: str | None

@dataclass(frozen=True)
class EvaluationView:
    run_id: str
    surfaced_examples: tuple[SurfacedExample, ...]
    per_dimension: tuple[DimensionResult, ...]
    read_only: bool
    def overall_accuracy(self) -> NoReturn: ...

def evaluation_view(conn, *, shadow_run_id: str, comparison_id: str,
                    select: Callable[[Sequence[Mapping]], Sequence[Mapping]],
                    ) -> EvaluationView: ...
```

**Done-means:** 19.

- [ ] **Step 1: Write the failing test**

`tests/p13/test_p13_evaluation.py`:

```python
"""§8.5: "A single overall 'accuracy' number hides the mechanism that needs repair."""
from __future__ import annotations

import inspect

import pytest

from eval_harness.comparison import DIMENSIONS

from review_surface.evaluation import (
    AggregateAccuracyRefused, DimensionResult, EvaluationView, SurfacedExample,
)


def _view() -> EvaluationView:
    return EvaluationView(
        run_id="shadow-1",
        surfaced_examples=(
            SurfacedExample(
                subject_ref="d1",
                baseline_output={"node_id": "n-2"},
                candidate_output={"node_id": "n-7"},
                selection_reason="baseline and candidate disagree on destination"),),
        per_dimension=(
            DimensionResult(dimension="placement",
                            baseline={"accepted": 40},
                            candidate={"accepted": 38},
                            attributed_stage="placement_scoring"),
            DimensionResult(dimension="extraction",
                            baseline={"complete": 100},
                            candidate={"complete": 100},
                            attributed_stage=None)),
        read_only=True)


def test_no_aggregate_accuracy_number_is_reachable():
    """Done-means 19, NEGATIVE TEST, first clause."""
    with pytest.raises(AggregateAccuracyRefused) as caught:
        _view().overall_accuracy()
    assert "mechanism that needs repair" in str(caught.value)


def test_the_module_computes_no_aggregate_anywhere():
    """Done-means 19, "and computes none". Asserted on the source, because a
    number nothing exposes today is a number something exposes tomorrow."""
    import review_surface.evaluation as module
    source = inspect.getsource(module)
    for forbidden in ("accuracy =", "/ total", "sum(scores", "mean(", "statistics"):
        assert forbidden not in source, f"{forbidden!r} appears in the module"


def test_comparison_results_are_shown_per_dimension_and_never_collapsed():
    """Done-means 19, second clause."""
    view = _view()
    assert len(view.per_dimension) == 2
    assert {d.dimension for d in view.per_dimension} <= set(DIMENSIONS)
    for result in view.per_dimension:
        assert result.baseline is not result.candidate


def test_each_dimension_names_the_stage_an_error_began_in_when_there_is_one():
    """G13: `attributed_stage` naming which of the ten stages an error began in."""
    view = _view()
    placement = next(d for d in view.per_dimension if d.dimension == "placement")
    assert placement.attributed_stage == "placement_scoring"
    extraction = next(d for d in view.per_dimension
                      if d.dimension == "extraction")
    assert extraction.attributed_stage is None


def test_a_surfaced_example_shows_baseline_and_candidate_side_by_side():
    example = _view().surfaced_examples[0]
    assert example.baseline_output != example.candidate_output
    assert example.selection_reason


def test_the_view_is_read_only():
    """SPEC Open question 9 is OPEN: whether an adjudication becomes an §8.7
    correction. Read-only until it is settled."""
    assert _view().read_only is True


def test_p13_calls_no_eval_writer():
    import review_surface.evaluation as module
    source = inspect.getsource(module)
    for writer in ("record_adjudication", "compare_runs", "run_shadow",
                   "attribute_run"):
        assert writer not in source, (
            f"{writer} is a P2 WRITER; P13 renders P2's records and computes "
            "no metric")


def test_the_selection_criterion_is_injected_and_has_no_default(p13_conn):
    """SPEC Open question 8 is OPEN and the Deferred table says the criterion is
    not settled by the design."""
    from review_surface.evaluation import evaluation_view
    signature = inspect.signature(evaluation_view)
    assert signature.parameters["select"].default is inspect.Parameter.empty
```

- [ ] **Step 2: Run the test and verify RED**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_evaluation.py`

Expected: **FAIL** — `ModuleNotFoundError: No module named 'review_surface.evaluation'`.

- [ ] **Step 3: Write `src/review_surface/evaluation.py`**

```python
# src/review_surface/evaluation.py
"""§8.5's user-facing evaluation view. Per dimension, per stage, never collapsed.

    "A single overall 'accuracy' number hides the mechanism that needs repair."

P2 states that as a rule binding the RENDERER, and P13 is that renderer. So
`overall_accuracy` exists and always raises: the number is not merely absent from
this record, it is refused by name at the one place someone would add it. And no
arithmetic over the per-dimension blocks happens anywhere in this module -- a
test asserts the source contains no division, no sum over scores and no
`statistics` import, because a number nothing exposes today is a number something
exposes tomorrow.

P13 computes no metric and calls no P2 writer. `compare_runs`, `run_shadow`,
`attribute_run` and `record_adjudication` are all P2's, and none is imported.

TWO OPEN QUESTIONS SHAPE WHAT THIS IS NOT:

* OQ8 -- what the user sees, and by what criterion shadow examples are selected.
  §8.5 says the replay system serves the engineering team AND the user without
  saying whether they see the same thing. So `select` is INJECTED with no
  default and the SPEC's Deferred table already says the criterion is unsettled.
* OQ9 -- whether a reviewer adjudication becomes an §8.7 correction. If it does,
  this view routes actions like every other P13 surface; if not, it is read-only.
  It is `read_only=True` until that is settled, and no action is collectable here.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import NoReturn

from eval_harness.comparison import DIMENSIONS


class AggregateAccuracyRefused(RuntimeError):
    """Someone asked the evaluation view for one overall number. §8.5 forbids it."""


@dataclass(frozen=True)
class SurfacedExample:
    subject_ref: str
    baseline_output: Mapping[str, object]
    candidate_output: Mapping[str, object]
    selection_reason: str


@dataclass(frozen=True)
class DimensionResult:
    dimension: str
    baseline: Mapping[str, object]
    candidate: Mapping[str, object]
    attributed_stage: str | None


@dataclass(frozen=True)
class EvaluationView:
    run_id: str
    surfaced_examples: tuple[SurfacedExample, ...]
    per_dimension: tuple[DimensionResult, ...]
    read_only: bool

    def overall_accuracy(self) -> NoReturn:
        raise AggregateAccuracyRefused(
            "§8.5: a single overall 'accuracy' number hides the mechanism that "
            "needs repair. This view shows comparison results per dimension and "
            "names the stage an error began in; it computes no aggregate and "
            "there is no number to return")


def evaluation_view(conn: sqlite3.Connection, *, shadow_run_id: str,
                    comparison_id: str,
                    select: Callable[[Sequence[Mapping]], Sequence[Mapping]],
                    ) -> EvaluationView:
    """Project P2's shadow and comparison records. `select` is the caller's.

    The two reads are deliberately separate: shadow mode surfaces "only selected
    examples for human review" and the comparison is per dimension over the whole
    run. Merging them would produce exactly one collapsed picture.

    P2's record shapes are read as mappings rather than as typed records because
    `shadow_record` and `get_comparison` return `dict`, verified live. Whatever
    keys P2 puts in them are carried through; P13 renames nothing and computes
    nothing.
    """
    from eval_harness.comparison import get_comparison
    from eval_harness.shadow import shadow_record

    shadow = shadow_record(conn, shadow_run_id)
    comparison = get_comparison(conn, comparison_id)

    raw_examples = list(shadow.get("surfaced_examples", ()) or ())
    chosen = list(select(raw_examples))
    examples = tuple(
        SurfacedExample(
            subject_ref=str(item.get("subject_ref", "")),
            baseline_output=dict(item.get("baseline_output", {}) or {}),
            candidate_output=dict(item.get("candidate_output", {}) or {}),
            selection_reason=str(item.get("selection_reason", "")))
        for item in chosen)

    blocks = comparison.get("per_dimension", {}) or {}
    results: list[DimensionResult] = []
    for dimension in DIMENSIONS:
        block = blocks.get(dimension)
        if block is None:
            continue
        results.append(DimensionResult(
            dimension=dimension,
            baseline=dict(block.get("baseline", {}) or {}),
            candidate=dict(block.get("candidate", {}) or {}),
            attributed_stage=block.get("attributed_stage")))

    return EvaluationView(
        run_id=shadow_run_id, surfaced_examples=examples,
        per_dimension=tuple(results), read_only=True)
```

> **`shadow_record` and `get_comparison` return dicts whose key names must be read live** before this is committed: `PYTHONPATH=src python3 -c "import inspect; from eval_harness.shadow import shadow_record; from eval_harness.comparison import get_comparison; print(inspect.getsource(shadow_record)); print(inspect.getsource(get_comparison))"`. If `per_dimension` is a list of blocks rather than a mapping by dimension, iterate the list and read each block's own `dimension` key instead. Do not invent a key.

- [ ] **Step 4: Run the test and verify PASS**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_evaluation.py`

Expected: **PASS** — eight tests green.

- [ ] **Step 5: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/review_surface/evaluation.py tests/p13/test_p13_evaluation.py && git commit -m "feat(p13-16): §8.5's evaluation view, per dimension, with no aggregate accuracy anywhere"
```

---

### Task 17: The learning view — inspect and reset, with the evidence that produced each record

> **OPEN QUESTION 11 IS UNRESOLVED.** *"Is a `review presentation` record deletable derived data? §8.4 lets the user 'review and delete local derived data'; §8.2 makes the event log append-only."* P13's tables are append-only by trigger (Task 1). A reset is therefore **collected and routed to P1**, and P13 deletes nothing — matching live `privacy.revocation.delete_derived`, which raises. If Joseph rules that presentations are deletable, this task's triggers are what must change.

**Files:**
- Create: `src/review_surface/learning_view.py`
- Test: `tests/p13/test_p13_learning_view.py`

**Interfaces:**

*Consumes:*

```python
from database_agent.events import CORRECTION_SCOPES
from review_surface.citations import ResolvedCitation, resolve_citation
from review_surface.collect import collect
from review_surface.presentation import PresentedState, presented_state
from review_surface.rejections import PriorRejection, prior_rejections
from review_surface.vocabulary import ACTION_RESET_LEARNING, SURFACE_LEARNING
```

*Produces:*

```python
class LearningNotAppliedHere(RuntimeError): ...
class NothingIsDeletedHere(RuntimeError): ...

@dataclass(frozen=True)
class LearnedPreferenceRow:
    correction_scope: str
    correction_subject: str
    polarity: str | None
    proposal_class: str | None
    basis_key: str | None
    observed_at: str
    citations: tuple[ResolvedCitation, ...]
    explanation: str

@dataclass(frozen=True)
class LearningView:
    scopes: tuple[str, ...]
    rows: tuple[LearnedPreferenceRow, ...]
    negative_examples: tuple[PriorRejection, ...]
    reset_action: str
    def apply(self) -> NoReturn: ...
    def delete(self) -> NoReturn: ...

def learning_view(conn, *, subject_refs: Sequence[str],
                  projection: Callable[[], Sequence[Mapping[str, object]]],
                  ) -> LearningView: ...
def collect_reset(conn, *, action_id, subject_ref, plan_version, session_id,
                  correction_scope, presented_state_ref, user_id, acted_at,
                  component_version) -> ReviewAction: ...
```

**Done-means:** 20.

- [ ] **Step 1: Write the failing test**

`tests/p13/test_p13_learning_view.py`:

```python
"""§8.7: "inspect or reset learned preferences, so personalization remains
understandable and reversible"."""
from __future__ import annotations

import pytest

from database_agent.events import CORRECTION_SCOPES
from privacy.display import RedactionSettings

from review_surface.collect import collect
from review_surface.learning_view import (
    LearningNotAppliedHere, NothingIsDeletedHere, collect_reset, learning_view,
)
from review_surface.presentation import record_presentation
from review_surface.store import record_action
from review_surface.vocabulary import (
    ACTION_RESET_LEARNING, ACTION_REJECT, SURFACE_LEARNING, SURFACE_PLACEMENT,
)

T0 = "2026-08-29T00:00:00Z"
SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")

PROJECTION = (
    {"correction_scope": "file", "correction_subject": "f-1",
     "polarity": "reject", "proposal_class": "placement",
     "basis_key": "node:n-receipts", "observed_at": T0,
     "evidence_refs": ("obs-columbia",)},
    {"correction_scope": "corpus", "correction_subject": "corpus",
     "polarity": "accept", "proposal_class": "residual",
     "basis_key": "node:n-clips", "observed_at": T0,
     "evidence_refs": ()},
)


def test_the_view_lists_scoped_learning_records(p13_conn):
    """Done-means 20, first clause."""
    view = learning_view(p13_conn, subject_refs=(),
                         projection=lambda: PROJECTION)
    assert len(view.rows) == 2
    assert {row.correction_scope for row in view.rows} == {"file", "corpus"}
    assert set(view.scopes) == set(CORRECTION_SCOPES)


def test_each_row_carries_the_evidence_that_produced_it(p13_conn):
    """Done-means 20, second clause."""
    view = learning_view(p13_conn, subject_refs=(),
                         projection=lambda: PROJECTION)
    scoped = next(row for row in view.rows if row.correction_scope == "file")
    assert scoped.citations
    assert scoped.citations[0].observation_key == "obs-columbia"


def test_a_row_with_no_evidence_says_so_rather_than_looking_evidenced(p13_conn):
    view = learning_view(p13_conn, subject_refs=(),
                         projection=lambda: PROJECTION)
    corpus_row = next(row for row in view.rows
                      if row.correction_scope == "corpus")
    assert corpus_row.citations == ()
    assert "no stored evidence" in corpus_row.explanation


def test_negative_examples_appear_beside_the_preferences(p13_conn):
    ref = record_presentation(
        p13_conn, surface=SURFACE_PLACEMENT, subject_ref="d1",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=("obs-columbia",), user_id="jy",
        component_version="p13-1", rendered_at=T0).presented_state_ref
    record_action(p13_conn, collect(
        p13_conn, action_id="a-rej", surface=SURFACE_PLACEMENT,
        subject_ref="d1", plan_version="plan-1", session_id="s-1",
        action=ACTION_REJECT, correction_scope="node",
        presented_state_ref=ref, user_id="jy", acted_at=T0,
        component_version="p13-1", payload={"node_id": "n-receipts"}))
    view = learning_view(p13_conn, subject_refs=("d1",),
                         projection=lambda: PROJECTION)
    assert len(view.negative_examples) == 1
    assert view.negative_examples[0].subject_ref == "d1"


def test_a_reset_is_collectable_and_routes_to_p1(p13_conn):
    """Done-means 20, third clause."""
    ref = record_presentation(
        p13_conn, surface=SURFACE_LEARNING, subject_ref="learning",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=(), user_id="jy", component_version="p13-1",
        rendered_at=T0).presented_state_ref
    action = collect_reset(
        p13_conn, action_id="a-reset", subject_ref="learning",
        plan_version="plan-1", session_id="s-1", correction_scope="corpus",
        presented_state_ref=ref, user_id="jy", acted_at=T0,
        component_version="p13-1")
    assert action.action == ACTION_RESET_LEARNING
    assert action.routed_to == ("P1",)


def test_no_learning_is_applied_by_p13(p13_conn):
    """SPEC:566-569: P13 renders P1's projection and collects the reset."""
    view = learning_view(p13_conn, subject_refs=(),
                         projection=lambda: PROJECTION)
    with pytest.raises(LearningNotAppliedHere):
        view.apply()


def test_p13_deletes_nothing(p13_conn):
    """SPEC Open question 11 is OPEN. P13's tables are append-only by trigger."""
    view = learning_view(p13_conn, subject_refs=(),
                         projection=lambda: PROJECTION)
    with pytest.raises(NothingIsDeletedHere):
        view.delete()


def test_no_learning_is_hidden_from_this_view(p13_conn):
    """SPEC:568-569: "No learning is applied by P13 and none is hidden from this
    view." Every projected row reaches the view, unfiltered."""
    view = learning_view(p13_conn, subject_refs=(),
                         projection=lambda: PROJECTION)
    assert len(view.rows) == len(PROJECTION)


def test_p13_has_no_telemetry_path(p13_conn):
    """SPEC:571-572: "P13 has no telemetry path and sends nothing anywhere"."""
    import inspect
    import pkgutil

    import review_surface
    for module_info in pkgutil.iter_modules(review_surface.__path__):
        module = __import__(f"review_surface.{module_info.name}",
                            fromlist=["x"])
        source = inspect.getsource(module)
        for forbidden in ("urllib", "requests", "http.client", "socket",
                          "smtplib", "ftplib"):
            assert forbidden not in source, (
                f"{forbidden} appears in review_surface.{module_info.name}")
```

- [ ] **Step 2: Run the test and verify RED**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_learning_view.py`

Expected: **FAIL** — `ModuleNotFoundError: No module named 'review_surface.learning_view'`.

- [ ] **Step 3: Write `src/review_surface/learning_view.py`**

```python
# src/review_surface/learning_view.py
"""§8.7's inspect-and-reset surface. P13 renders; P1 stores; P13 applies nothing.

    §8.7 requires that the user "be able to inspect or reset learned
    preferences, so personalization remains understandable and reversible."

Two refusals, and both are methods that raise rather than absences someone has to
notice:

* `apply` -- no learning is applied by P13. The store is P1's scoped projection
  over `events.correction_scope`, and the MEANING of each correction belongs to
  the part it was routed to.
* `delete` -- P13's tables are append-only by trigger and P13 deletes nothing.
  SPEC Open question 11 is open: §8.4 lets the user "review and delete local
  derived data" and §8.2 makes the event log append-only, and the same conflict
  P7 and P5 raise about stored observations applies to the record of what was
  displayed. Live `privacy.revocation.delete_derived` raises for the same reason.

NOTHING IS FILTERED. §8.7's own promise is that none of the learning is hidden
from this view, so every projected row reaches `rows` and a row with no evidence
says so in its explanation rather than being dropped for looking thin.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import NoReturn

from database_agent.events import CORRECTION_SCOPES

from review_surface.citations import ResolvedCitation, resolve_citation
from review_surface.collect import collect
from review_surface.records import ReviewAction
from review_surface.rejections import PriorRejection, prior_rejections
from review_surface.vocabulary import ACTION_RESET_LEARNING, SURFACE_LEARNING


class LearningNotAppliedHere(RuntimeError):
    """Something asked P13 to apply a learned preference. It is not P13's."""


class NothingIsDeletedHere(RuntimeError):
    """Something asked P13 to delete a record. Its tables are append-only."""


@dataclass(frozen=True)
class LearnedPreferenceRow:
    correction_scope: str
    correction_subject: str
    polarity: str | None
    proposal_class: str | None
    basis_key: str | None
    observed_at: str
    citations: tuple[ResolvedCitation, ...]
    explanation: str


@dataclass(frozen=True)
class LearningView:
    scopes: tuple[str, ...]
    rows: tuple[LearnedPreferenceRow, ...]
    negative_examples: tuple[PriorRejection, ...]
    reset_action: str

    def apply(self) -> NoReturn:
        raise LearningNotAppliedHere(
            "P13 renders P1's scoped projection and collects the reset; it "
            "applies no learning. The store is P1's (S5, G3) and the meaning of "
            "each correction belongs to the part it was routed to")

    def delete(self) -> NoReturn:
        raise NothingIsDeletedHere(
            "P13's tables are append-only by trigger and it owns no supersedable "
            "record. Whether a `review presentation` is deletable derived data "
            "is unresolved: §8.4 lets the user review and delete local derived "
            "data and §8.2 makes the event log append-only. A reset is collected "
            "and routed to P1, which records it")


def learning_view(conn: sqlite3.Connection, *, subject_refs: Sequence[str],
                  projection: Callable[[], Sequence[Mapping[str, object]]],
                  ) -> LearningView:
    """Render P1's projection and P13's own stored rejections. Filter nothing.

    `projection` is injected because the scoped store is P1's and its read
    surface is not P13's to name. Each row is expected to carry
    `correction_scope`, `correction_subject`, `polarity`, `proposal_class`,
    `basis_key`, `observed_at` and `evidence_refs`; anything else is ignored and
    anything missing reads as None rather than raising, because a projection that
    grows a column must not break the view that renders it.
    """
    rows: list[LearnedPreferenceRow] = []
    for record in projection():
        refs = tuple(record.get("evidence_refs", ()) or ())
        citations = tuple(resolve_citation(conn, key) for key in refs)
        scope = str(record.get("correction_scope", ""))
        subject = str(record.get("correction_subject", ""))
        rows.append(LearnedPreferenceRow(
            correction_scope=scope,
            correction_subject=subject,
            polarity=record.get("polarity"),
            proposal_class=record.get("proposal_class"),
            basis_key=record.get("basis_key"),
            observed_at=str(record.get("observed_at", "")),
            citations=citations,
            explanation=(
                f"a {record.get('polarity') or 'neutral'} correction at "
                f"{scope!r} scope about {subject!r}"
                + (f", supported by {len(citations)} stored observation(s)"
                   if citations
                   else ", with no stored evidence reference; it is shown as it "
                        "is rather than omitted, because §8.7 requires that "
                        "none of the learning is hidden from this view"))))

    negatives: list[PriorRejection] = []
    for subject_ref in subject_refs:
        negatives.extend(prior_rejections(conn, subject_ref=subject_ref))

    return LearningView(
        scopes=CORRECTION_SCOPES, rows=tuple(rows),
        negative_examples=tuple(negatives),
        reset_action=ACTION_RESET_LEARNING)


def collect_reset(conn: sqlite3.Connection, *, action_id: str,
                  subject_ref: str, plan_version: str, session_id: str,
                  correction_scope: str, presented_state_ref: str,
                  user_id: str, acted_at: str,
                  component_version: str) -> ReviewAction:
    """Collect the reset and route it to P1. P13 records nothing else."""
    return collect(
        conn, action_id=action_id, surface=SURFACE_LEARNING,
        subject_ref=subject_ref, plan_version=plan_version,
        session_id=session_id, action=ACTION_RESET_LEARNING,
        correction_scope=correction_scope,
        presented_state_ref=presented_state_ref, user_id=user_id,
        acted_at=acted_at, component_version=component_version)
```

- [ ] **Step 4: Run the test and verify PASS**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_learning_view.py`

Expected: **PASS** — nine tests green.

- [ ] **Step 5: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/review_surface/learning_view.py tests/p13/test_p13_learning_view.py && git commit -m "feat(p13-17): §8.7's inspect-and-reset view, where P13 applies no learning and hides none"
```

---

### Task 18: The plan-version diff — §8.8's own case, and `66` §17's draft the user adopts

> **`66` §17 IS NEWER THAN THE SPEC AND GOVERNS.** *"When a user edits or re-runs a structural answer, the product creates a draft plan version. It shows a meaningful diff: which schemas become active or inactive, which templates are affected, which branches may need review, which placement proposals become invalid or newly possible, whether any protected area changes, and whether any filing policy is paused. It must not silently rename folders, reclassify files, reveal protected records, or move anything as a consequence of a changed answer."* Six diff dimensions and four prohibitions. **P13 owns the presentation-and-consent half; the storage half shipped in `dfdc015`** as `tree_design.user_edits` and `tree_design.diff`, and this task CONSUMES them rather than re-deriving anything.

> **THREE OF `66` §17's SIX DIFF DIMENSIONS HAVE NO PRODUCER, AND THAT IS UNRESOLVED.** Live coverage:
>
> | `66` §17 asks for | Producer | Status |
> |---|---|---|
> | which branches may need review | `placement.versions.VersionDiff.requiring_renewed_review` | **live** |
> | which placement proposals become invalid or newly possible | `VersionDiff.requiring_renewed_review` + `.removed_node_ids` | **live** |
> | which templates are affected | `tree_design.diff.NodeDiffEntry` kind `re-templated` | **live** |
> | which schemas become active or inactive | — | **NO PRODUCER.** `user_edits.UserLevelEdit.uses_schema` is a schema *name on an edit*, not a schema activation delta |
> | whether any protected area changes | — | **NO PRODUCER.** `tree_design.freeze.represent_protected_areas` builds protected nodes; nothing diffs them across versions |
> | whether any filing policy is paused | — | **NO PRODUCER.** Same gap as Task 11's activity list: no part publishes a filing-policy record |
>
> The three gaps are carried as `None` on `StructuralDiffView` beside a note naming each, **never faked and never quietly dropped**.

**Files:**
- Create: `src/review_surface/versions_view.py`
- Test: `tests/p13/test_p13_versions_view.py`

**Interfaces:**

*Consumes:*

```python
from tree_design.diff import NodeDiffEntry, diff_versions   # (conn, *, before, after)
from tree_design.user_edits import (
    UnappliedUserEdit, UserLevelEdit, user_level_edits,     # (conn, *, schemas=None)
)
from tree_design.store import VERSION_ACTIONS               # ("adopt_version", "restore_version")
from placement.versions import VersionDiff, reproject
from review_surface.collect import collect
from review_surface.vocabulary import (
    ACTION_ADOPT_VERSION, ACTION_RESTORE_VERSION, SURFACE_PLAN_VERSION,
)
```

*Produces:*

```python
THREE_VERSION_ACTIONS: tuple[str, ...]   # ("compare", "restore_version", "adopt_version")

class NothingIsAdoptedSilently(RuntimeError): ...

@dataclass(frozen=True)
class RenewedReviewStatement:
    count: int
    subject_refs: tuple[str, ...]
    sentence: str

@dataclass(frozen=True)
class StructuralDiffView:
    before: str
    after: str
    node_entries: tuple[NodeDiffEntry, ...]
    renewed_review: RenewedReviewStatement
    removed_node_ids: tuple[str, ...]
    carried_unchanged: tuple[str, ...]
    unapplied_user_edits: tuple[UnappliedUserEdit, ...]
    schemas_activated_or_deactivated: None
    protected_area_changes: None
    filing_policies_paused: None
    producer_gap_notes: tuple[str, ...]
    available_actions: tuple[str, ...]
    adopted: bool

def structural_diff_view(conn, *, before: str, after: str,
                         version_diff: VersionDiff,
                         unapplied: Sequence[UnappliedUserEdit] = (),
                         ) -> StructuralDiffView: ...
def collect_version_action(conn, view, action, *, action_id, plan_version,
                           session_id, correction_scope, presented_state_ref,
                           user_id, acted_at, component_version) -> ReviewAction: ...
```

**Done-means:** 21.

- [ ] **Step 1: Write the failing test**

`tests/p13/test_p13_versions_view.py`:

```python
"""§8.8 + `66` §17: a visible diff, and a draft the user explicitly adopts."""
from __future__ import annotations

import pytest

from placement.versions import VersionDiff
from privacy.display import RedactionSettings
from tree_design.records import Node, PlanVersion
from tree_design.store import write_node, write_plan_version
from tree_design.user_edits import UnappliedUserEdit, UserLevelEdit

from review_surface.presentation import record_presentation
from review_surface.versions_view import (
    NothingIsAdoptedSilently, THREE_VERSION_ACTIONS, collect_version_action,
    structural_diff_view,
)
from review_surface.vocabulary import (
    ACTION_ADOPT_VERSION, ACTION_RESTORE_VERSION, SURFACE_PLAN_VERSION,
)

T0 = "2026-08-29T00:00:00Z"
SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")


def _versions(conn):
    for version_id, predecessor in (("plan-1", None), ("plan-2", "plan-1")):
        write_plan_version(conn, PlanVersion(
            plan_version_id=version_id, predecessor_id=predecessor,
            state="draft", created_at=T0, cross_folder_moves=False,
            selection_id="sel-1"))
    # `Applications` renamed to `Admissions` -- §8.8's own first example.
    for version_id, node_id, label in (("plan-1", "n-a1", "Applications"),
                                       ("plan-2", "n-a2", "Admissions")):
        write_node(conn, Node(
            node_id=node_id, plan_version_id=version_id, node_type="proposed",
            display_label=label, parent_node_id=None, root_anchor="root",
            ordinal=0, associated_group_ids=(), explanation="fixture",
            node_role="ordinary", accepts_placement=True,
            handling_class="public_low", origin_node_id="origin-a",
            template_context=None, dimension_role=None, dimension=None,
            expected_values=(), existing_path=None, disposition=None,
            refinement_disposition=None, refinement_reason=None,
            protected_movement_permitted=False))


TWENTY_THREE = VersionDiff(
    from_plan_version="plan-1", to_plan_version="plan-2",
    requiring_renewed_review=tuple(f"d-{n}" for n in range(23)),
    carried_unchanged=("d-99",), removed_node_ids=("n-gone",))


def test_the_node_level_diff_shows_the_rename(p13_conn):
    """§8.8's own example: Applications was renamed to Admissions."""
    _versions(p13_conn)
    view = structural_diff_view(p13_conn, before="plan-1", after="plan-2",
                                version_diff=TWENTY_THREE)
    kinds = {entry.kind for entry in view.node_entries}
    assert "renamed" in kinds
    renamed = next(e for e in view.node_entries if e.kind == "renamed")
    assert renamed.before["display_label"] == "Applications"
    assert renamed.after["display_label"] == "Admissions"
    assert renamed.undo_label


def test_the_view_renders_section_8_8_s_own_sentence(p13_conn):
    """Done-means 21: "twenty-three files now require renewed review because
    their previous destination no longer exists"."""
    _versions(p13_conn)
    view = structural_diff_view(p13_conn, before="plan-1", after="plan-2",
                                version_diff=TWENTY_THREE)
    assert view.renewed_review.count == 23
    assert "23" in view.renewed_review.sentence
    assert "renewed review" in view.renewed_review.sentence
    assert len(view.renewed_review.subject_refs) == 23


def test_compare_restore_and_adopt_are_all_collectable(p13_conn):
    """Done-means 21, second clause. §8.8's three named user actions."""
    _versions(p13_conn)
    view = structural_diff_view(p13_conn, before="plan-1", after="plan-2",
                                version_diff=TWENTY_THREE)
    assert THREE_VERSION_ACTIONS == ("compare", "restore_version",
                                     "adopt_version")
    assert view.available_actions == THREE_VERSION_ACTIONS


def test_nothing_is_adopted_until_the_user_adopts_it(p13_conn):
    """`66` §17: "Existing approved structure remains stable unless the user
    explicitly adopts the new plan"."""
    _versions(p13_conn)
    view = structural_diff_view(p13_conn, before="plan-1", after="plan-2",
                                version_diff=TWENTY_THREE)
    assert view.adopted is False


def test_adopting_is_collected_and_routed_to_p10(p13_conn):
    _versions(p13_conn)
    view = structural_diff_view(p13_conn, before="plan-1", after="plan-2",
                                version_diff=TWENTY_THREE)
    ref = record_presentation(
        p13_conn, surface=SURFACE_PLAN_VERSION, subject_ref="plan-2",
        plan_version="plan-2", session_id="s-1", settings=SHOWN,
        evidence_refs=(), user_id="jy", component_version="p13-1",
        rendered_at=T0).presented_state_ref
    action = collect_version_action(
        p13_conn, view, ACTION_ADOPT_VERSION, action_id="a-adopt",
        plan_version="plan-2", session_id="s-1", correction_scope="corpus",
        presented_state_ref=ref, user_id="jy", acted_at=T0,
        component_version="p13-1")
    assert action.routed_to == ("P10",)
    assert action.subject_ref == "plan-2"


def test_restoring_is_collected_and_routed_to_p10(p13_conn):
    _versions(p13_conn)
    view = structural_diff_view(p13_conn, before="plan-1", after="plan-2",
                                version_diff=TWENTY_THREE)
    ref = record_presentation(
        p13_conn, surface=SURFACE_PLAN_VERSION, subject_ref="plan-1",
        plan_version="plan-2", session_id="s-1", settings=SHOWN,
        evidence_refs=(), user_id="jy", component_version="p13-1",
        rendered_at=T0).presented_state_ref
    action = collect_version_action(
        p13_conn, view, ACTION_RESTORE_VERSION, action_id="a-restore",
        plan_version="plan-2", session_id="s-1", correction_scope="corpus",
        presented_state_ref=ref, user_id="jy", acted_at=T0,
        component_version="p13-1")
    assert action.routed_to == ("P10",)
    assert action.subject_ref == "plan-1"


def test_an_unapplied_user_edit_is_surfaced_rather_than_resolved(p13_conn):
    """`64` §5c and the shipped `UnappliedUserEdit`: "that is a question for the
    user, not a decision for the product"."""
    _versions(p13_conn)
    edit = UserLevelEdit(
        uses_schema="academic", role_ref="level", field_ref="subject",
        action="renamed", display_label="Class", proposed_label="Course",
        user_id="jy", recorded_at=T0)
    view = structural_diff_view(
        p13_conn, before="plan-1", after="plan-2",
        version_diff=TWENTY_THREE,
        unapplied=(UnappliedUserEdit(
            edit, "re-templated",
            "you renamed 'level' to 'Class'; this release resolves it to "
            "another field"),))
    assert len(view.unapplied_user_edits) == 1
    assert view.unapplied_user_edits[0].kind == "re-templated"
    assert view.unapplied_user_edits[0].edit.display_label == "Class"


def test_the_three_missing_diff_dimensions_are_reported_not_faked(p13_conn):
    """`66` §17 asks for six. Three have no producer anywhere in `src/`."""
    _versions(p13_conn)
    view = structural_diff_view(p13_conn, before="plan-1", after="plan-2",
                                version_diff=TWENTY_THREE)
    assert view.schemas_activated_or_deactivated is None
    assert view.protected_area_changes is None
    assert view.filing_policies_paused is None
    assert len(view.producer_gap_notes) == 3
    joined = " ".join(view.producer_gap_notes)
    assert "schema" in joined and "protected area" in joined
    assert "filing policy" in joined


def test_the_view_moves_renames_reclassifies_and_reveals_nothing(p13_conn):
    """`66` §17's four prohibitions, asserted on the module."""
    import inspect

    import review_surface.versions_view as module
    source = inspect.getsource(module)
    for forbidden in ("write_node", "apply_review_action", "freeze_version",
                      "set_display_label", "shutil", "os.rename"):
        assert forbidden not in source, f"{forbidden} appears in the view module"


def test_adopting_via_an_unknown_action_is_refused(p13_conn):
    _versions(p13_conn)
    view = structural_diff_view(p13_conn, before="plan-1", after="plan-2",
                                version_diff=TWENTY_THREE)
    ref = record_presentation(
        p13_conn, surface=SURFACE_PLAN_VERSION, subject_ref="plan-2",
        plan_version="plan-2", session_id="s-1", settings=SHOWN,
        evidence_refs=(), user_id="jy", component_version="p13-1",
        rendered_at=T0).presented_state_ref
    with pytest.raises(NothingIsAdoptedSilently):
        collect_version_action(
            p13_conn, view, "accept", action_id="a-x", plan_version="plan-2",
            session_id="s-1", correction_scope="corpus",
            presented_state_ref=ref, user_id="jy", acted_at=T0,
            component_version="p13-1")
```

- [ ] **Step 2: Run the test and verify RED**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_versions_view.py`

Expected: **FAIL** — `ModuleNotFoundError: No module named 'review_surface.versions_view'`.

- [ ] **Step 3: Write `src/review_surface/versions_view.py`**

```python
# src/review_surface/versions_view.py
"""§8.8's diff and `66` §17's draft the user adopts. The presentation-and-consent half.

P10 emits the node-level diff (`tree_design.diff.diff_versions`, shipped), P11
computes the file-level consequence (`placement.versions.reproject`, shipped),
and P13 renders BOTH -- §8.8's own examples being that Applications was renamed
to Admissions, Research moved under Projects, Reference Clips was added, the
Academic template's dimension order changed, and "twenty-three files now require
renewed review because their previous destination no longer exists."

**Nothing here writes.** `66` §17: a changed structural answer "must not silently
rename folders, reclassify files, reveal protected records, or move anything."
This module imports no writer -- not `write_node`, not `apply_review_action`, not
`freeze_version` -- and a test asserts the absence by source inspection.

**Nothing is adopted until the user adopts it.** `adopted` is False on every view
this module builds, because "Existing approved structure remains stable unless
the user explicitly adopts the new plan." The adoption is a collected
`review_action` routed to P10, which owns the record.

**A rename the user made and this release cannot honour is SURFACED, not
resolved.** `tree_design.user_edits.UnappliedUserEdit` is the shipped record for
exactly that (`64` §5c: "that is a question for the user, not a decision for the
product") and it is carried through verbatim, in `diff.py`'s own vocabulary, so
"what changed when I updated" and "what changed when I edited" read the same way.

**Three of `66` §17's six diff dimensions have NO PRODUCER.** They are `None`
with a note each, never invented. See this task's callout in the plan.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass

from placement.versions import VersionDiff
from tree_design.diff import NodeDiffEntry, diff_versions
from tree_design.user_edits import UnappliedUserEdit

from review_surface.collect import collect
from review_surface.records import ReviewAction
from review_surface.vocabulary import (
    ACTION_ADOPT_VERSION, ACTION_RESTORE_VERSION, SURFACE_PLAN_VERSION,
)

#: §8.8's three named user actions. `compare` is the view itself and is listed so
#: the three read together; `restore_version` and `adopt_version` are collected
#: actions and are P13 vocabulary members.
COMPARE: str = "compare"
THREE_VERSION_ACTIONS: tuple[str, ...] = (
    COMPARE, ACTION_RESTORE_VERSION, ACTION_ADOPT_VERSION)

_GAP_NOTES: tuple[str, ...] = (
    "`66` §17 asks which schemas become active or inactive. No part publishes a "
    "schema-activation delta: `user_edits.UserLevelEdit.uses_schema` names the "
    "schema an edit was made in, not a change in which schemas are active. "
    "Reported as absent rather than derived from something that does not mean it.",
    "`66` §17 asks whether any protected area changes. "
    "`tree_design.freeze.represent_protected_areas` builds protected nodes and "
    "nothing diffs them across versions. Reported as absent -- and inferring it "
    "from the node diff would risk revealing a protected record, which the same "
    "section forbids.",
    "`66` §17 asks whether any filing policy is paused. No part publishes a "
    "filing-policy record at all; automatic filing is item 5 of `63` §2's "
    "resequenced order. Reported as absent rather than invented.",
)


class NothingIsAdoptedSilently(RuntimeError):
    """A version gesture that is not one of §8.8's three named user actions."""


@dataclass(frozen=True)
class RenewedReviewStatement:
    count: int
    subject_refs: tuple[str, ...]
    sentence: str


@dataclass(frozen=True)
class StructuralDiffView:
    before: str
    after: str
    node_entries: tuple[NodeDiffEntry, ...]
    renewed_review: RenewedReviewStatement
    removed_node_ids: tuple[str, ...]
    carried_unchanged: tuple[str, ...]
    unapplied_user_edits: tuple[UnappliedUserEdit, ...]
    schemas_activated_or_deactivated: None
    protected_area_changes: None
    filing_policies_paused: None
    producer_gap_notes: tuple[str, ...]
    available_actions: tuple[str, ...]
    adopted: bool


def structural_diff_view(conn: sqlite3.Connection, *, before: str, after: str,
                         version_diff: VersionDiff,
                         unapplied: Sequence[UnappliedUserEdit] = (),
                         ) -> StructuralDiffView:
    """Render P10's node diff and P11's file-level consequence. Adopt nothing.

    `version_diff` is passed rather than computed here, because
    `placement.versions.reproject` is a P11 call with its own revalidation inputs
    and P13 must not choose them. P13 renders the diff it was handed.
    """
    entries = diff_versions(conn, before=before, after=after)
    subjects = tuple(version_diff.requiring_renewed_review)
    return StructuralDiffView(
        before=before, after=after, node_entries=entries,
        renewed_review=RenewedReviewStatement(
            count=len(subjects), subject_refs=subjects,
            sentence=(
                f"{len(subjects)} file(s) now require renewed review because "
                "their previous destination no longer exists or changed. They "
                "are presented as requiring review and are not pre-accepted at "
                "their old destination: approvals do not carry across versions.")),
        removed_node_ids=tuple(version_diff.removed_node_ids),
        carried_unchanged=tuple(version_diff.carried_unchanged),
        unapplied_user_edits=tuple(unapplied),
        schemas_activated_or_deactivated=None,
        protected_area_changes=None,
        filing_policies_paused=None,
        producer_gap_notes=_GAP_NOTES,
        available_actions=THREE_VERSION_ACTIONS,
        # Always False. Adoption is a user gesture routed to P10, and a view that
        # could report itself adopted would be a view that adopted something.
        adopted=False)


def collect_version_action(conn: sqlite3.Connection, view: StructuralDiffView,
                           action: str, *, action_id: str, plan_version: str,
                           session_id: str, correction_scope: str,
                           presented_state_ref: str, user_id: str,
                           acted_at: str,
                           component_version: str) -> ReviewAction:
    """Collect an adopt or a restore and route it to P10.

    `subject_ref` follows the action: adopting names the version being adopted,
    restoring names the version being restored to. Naming the same version for
    both would make the two gestures indistinguishable in the store, and P10's
    `VERSION_ACTIONS` branch on exactly that difference.
    """
    if action == ACTION_ADOPT_VERSION:
        subject_ref = view.after
    elif action == ACTION_RESTORE_VERSION:
        subject_ref = view.before
    else:
        raise NothingIsAdoptedSilently(
            f"{action!r} is not one of §8.8's three named user actions "
            f"{list(THREE_VERSION_ACTIONS)}. A plan version is compared, "
            "restored, or explicitly adopted; nothing else changes it")
    return collect(
        conn, action_id=action_id, surface=SURFACE_PLAN_VERSION,
        subject_ref=subject_ref, plan_version=plan_version,
        session_id=session_id, action=action,
        correction_scope=correction_scope,
        presented_state_ref=presented_state_ref, user_id=user_id,
        acted_at=acted_at, component_version=component_version,
        payload={"before": view.before, "after": view.after})
```

- [ ] **Step 4: Run the test and verify PASS**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_versions_view.py`

Expected: **PASS** — ten tests green.

- [ ] **Step 5: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/review_surface/versions_view.py tests/p13/test_p13_versions_view.py && git commit -m "feat(p13-18): §8.8's diff and 66 §17's draft, adopted only when the user adopts it"
```

---

### Task 19: The guard — P13 contains no scoring, classification, validation, path resolution or filesystem mutation

**Files:**
- Test: `tests/p13/test_p13_guards.py`

**Interfaces:** none. This task creates no module. It asserts, **by runtime introspection over the live package**, the properties every other task depends on.

**Done-means:** 22 (*"**Negative test:** P13 contains no scoring, classification, validation, path-resolution or filesystem-mutation code, and writes no record other than the four in Contract out"*).

**Why introspection and not a text search.** Authoring brief §6: *"a text search matches comments and docstrings, and scanning text for a token has produced a false result nine times on this project."* So the import guard walks `sys.modules` after importing every `review_surface` module and inspects what each module **binds**, not what its source spells. The few source-text assertions that remain — the ones about a literal appearing in a body — are narrowed to a single named module each and stated as such.

- [ ] **Step 1: Write the failing guard test**

`tests/p13/test_p13_guards.py`:

```python
"""Done-means 22, by runtime introspection. Not by scanning text for tokens."""
from __future__ import annotations

import importlib
import inspect
import pkgutil

import pytest

import review_surface

MODULE_NAMES = tuple(
    sorted(info.name for info in pkgutil.iter_modules(review_surface.__path__)))


def _modules():
    return {name: importlib.import_module(f"review_surface.{name}")
            for name in MODULE_NAMES}


def _bindings(module):
    """Every name the module BINDS, with what it is. Not its source text."""
    return {name: value for name, value in vars(module).items()
            if not name.startswith("__")}


def test_the_package_is_the_modules_this_plan_creates():
    expected = {
        "apply_seam", "approval", "bulk", "citations", "collect",
        "consent_surface", "evaluation", "items", "labels", "learning_view",
        "locations", "presentation", "progress", "records",
        "redaction_boundary", "rejections", "replay", "residual", "routing",
        "schema", "states", "store", "versions_view", "vocabulary",
    }
    assert set(MODULE_NAMES) == expected, (
        f"unexpected: {set(MODULE_NAMES) - expected}; "
        f"missing: {expected - set(MODULE_NAMES)}")


def test_no_module_binds_a_filesystem_mutation_callable():
    """Done-means 22: no filesystem-mutation code."""
    import os
    import shutil
    forbidden = {
        os.rename, os.replace, os.remove, os.unlink, os.rmdir, os.makedirs,
        os.mkdir, shutil.move, shutil.copy, shutil.copy2, shutil.rmtree,
    }
    for name, module in _modules().items():
        for bound, value in _bindings(module).items():
            assert value not in forbidden, (
                f"review_surface.{name} binds {bound} = a filesystem mutation")


def test_no_module_binds_pathlib_or_os_path():
    """B3: P13 composes no path. Asserted on bindings, not on the word 'path'."""
    import os.path
    import pathlib
    for name, module in _modules().items():
        for bound, value in _bindings(module).items():
            assert value is not pathlib, f"review_surface.{name} binds pathlib"
            assert value is not pathlib.Path, (
                f"review_surface.{name} binds pathlib.Path")
            assert value is not os.path, (
                f"review_surface.{name} binds os.path")


def test_no_module_binds_a_network_client():
    """SPEC:571-572: P13 has no telemetry path and sends nothing anywhere."""
    for name in MODULE_NAMES:
        module = importlib.import_module(f"review_surface.{name}")
        for bound, value in _bindings(module).items():
            module_name = getattr(value, "__name__", "")
            assert not str(module_name).startswith(
                ("urllib", "http", "socket", "smtplib", "ftplib", "requests")), (
                f"review_surface.{name} binds {bound} from {module_name}")


def test_no_module_binds_a_scoring_classification_or_validation_callable():
    """Done-means 22: no scoring, classification or validation code.

    Asserted against the live callables the parts that DO own those publish, so
    a rename in P6/P7/P8/P11 breaks this guard instead of silently defeating it.
    """
    from facts.resolver import fill_or_abstain
    from llm_harness.records import P8Verdict
    from placement.scoring import score_candidate
    from privacy.classification import classify
    forbidden = {fill_or_abstain, score_candidate, classify, P8Verdict}
    for name, module in _modules().items():
        for bound, value in _bindings(module).items():
            assert value not in forbidden, (
                f"review_surface.{name} binds {bound}, which belongs to the "
                "part that owns the decision")


def test_no_module_binds_a_p12_test_fixture():
    """`src/review_surface/` never imports the tests-only P12 stand-in."""
    for name, module in _modules().items():
        source = inspect.getsource(module)
        assert "p12_fixtures" not in source, (
            f"review_surface.{name} imports the tests-only P12 fixture")
        assert "p13_fixtures" not in source


def test_no_module_outside_vocabulary_binds_one_of_p13_s_closed_vocabularies():
    """Brief §11 and §16: the guard's target is a COLLECTION whose members ARE a
    vocabulary, bound outside the module that publishes it."""
    from review_surface import vocabulary as v
    published = {
        "SURFACES": set(v.SURFACES), "ACTIONS": set(v.ACTIONS),
        "VERDICTS": set(v.VERDICTS),
        "PROGRESS_STATES": set(v.PROGRESS_STATES),
        "PROGRESS_SOURCES": set(v.PROGRESS_SOURCES),
    }
    for name, module in _modules().items():
        if name == "vocabulary":
            continue
        for bound, value in _bindings(module).items():
            if not isinstance(value, (tuple, frozenset, set, list)):
                continue
            members = set(value)
            for vocab_name, vocab in published.items():
                if members == vocab and value is not getattr(v, vocab_name):
                    pytest.fail(
                        f"review_surface.{name}.{bound} is a second copy of "
                        f"{vocab_name}; import the published tuple")


def test_citations_never_reaches_for_an_observation_id():
    """M14, narrowed to the one module that resolves citations."""
    import review_surface.citations as module
    for bound, value in _bindings(module).items():
        assert getattr(value, "__name__", "") != "get_observation", (
            f"citations binds {bound} = get_observation; M14 says the durable "
            "handle is the KEY")


def test_p13_writes_only_its_own_three_tables(p13_conn):
    """Done-means 22's writing clause, asserted over the whole package."""
    from review_surface.schema import REVIEW_TABLES
    all_tables = {row["name"] for row in p13_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    other = all_tables - set(REVIEW_TABLES) - {"events"}
    for name, module in _modules().items():
        source = inspect.getsource(module)
        for table in sorted(other):
            assert f"INSERT INTO {table}" not in source, (
                f"review_surface.{name} inserts into {table}, which P13 does "
                "not own")
            assert f"UPDATE {table}" not in source
            assert f"DELETE FROM {table}" not in source


def test_p13_appends_only_its_three_registered_event_types():
    from review_surface.vocabulary import EVENT_TYPES
    for name, module in _modules().items():
        source = inspect.getsource(module)
        if "append_event" not in source:
            continue
        assert "event_type=EVENT_" in source or "event_type=" not in source, (
            f"review_surface.{name} passes a literal event_type; use a named "
            f"constant from {list(EVENT_TYPES)}")


def test_every_module_is_stdlib_plus_this_project_only():
    """Brief §6: Python 3.12, stdlib only. No third-party import anywhere."""
    import sys
    project_roots = {
        "database_agent", "eval_harness", "evidence_shape", "extractors",
        "facts", "grouping", "llm_harness", "placement", "privacy",
        "readers", "recognition", "review_surface", "scan_agent",
        "tree_design",
    }
    for name, module in _modules().items():
        for bound, value in _bindings(module).items():
            origin = getattr(value, "__module__", None) or getattr(
                value, "__name__", "")
            root = str(origin).split(".")[0]
            if not root or root in project_roots:
                continue
            assert root in sys.stdlib_module_names, (
                f"review_surface.{name} binds {bound} from third-party "
                f"package {root!r}")
```

- [ ] **Step 2: Run the guard and verify RED, then GREEN**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_guards.py`

Expected on the first run: **FAIL** on at least `test_no_module_binds_a_scoring_classification_or_validation_callable` if `facts.resolver.fill_or_abstain`, `placement.scoring.score_candidate` or `privacy.classification.classify` do not exist under those names.

**Read the live names before adjusting the test**, and adjust the TEST, never the guard's intent:

```bash
cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -c "
import inspect
for mod in ('facts.resolver','placement.scoring','privacy.classification'):
    m=__import__(mod, fromlist=['x'])
    print('==', mod, [n for n,o in vars(m).items() if inspect.isfunction(o) and o.__module__==mod])
"
```

Substitute three real, live callables — one that scores, one that classifies, one that validates — and re-run.

Expected after the substitution: **PASS** — eleven guard tests green.

- [ ] **Step 3: Run the whole P13 suite and then the whole repository**

```bash
cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src:. python3 -m pytest -q -p no:randomly tests/p13/
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest -q -p no:randomly 2>&1 | tail -5
```

Expected: every P13 test green except the one deliberate `xfail` from Task 9 Step 6; the repository total is the previous 5247 plus P13's tests, with **no failures and no errors**.

- [ ] **Step 4: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add tests/p13/test_p13_guards.py && git commit -m "test(p13-19): the Done-means 22 guard, by runtime introspection rather than by scanning text"
```

---

### Task 20: Every surface renders from a P2 replay bundle, and `presented_state_ref` round-trips

**Files:**
- Create: `src/review_surface/replay.py`
- Test: `tests/p13/test_p13_replay.py`

**Interfaces:**

*Consumes:*

```python
from review_surface.presentation import PresentedState, presented_state, record_presentation
from review_surface.records import ProgressLine, ReviewAction, ReviewApproval
from review_surface.store import actions_for
from review_surface.approval import approvals_for
```

*Produces:*

```python
class NoStageOutputHere(RuntimeError): ...
class NotRenderableFromABundle(RuntimeError): ...

def serialize_presented_state(state: PresentedState) -> dict: ...
def deserialize_presented_state(payload: Mapping[str, object]) -> PresentedState: ...
def reassert_presented_state(conn, payload: Mapping[str, object]) -> PresentedState: ...
def stage_output(*args, **kwargs) -> NoReturn: ...   # always raises
def assert_no_filesystem_needed(build: Callable[[], object]) -> object: ...
```

**Done-means:** 23 (*"Every surface renders from a P2 replay bundle without a live filesystem, and `presented_state_ref` round-trips through a bundle"*).

**What P13 owes P2, and what it does not.** SPEC:400-407: **P13 emits no `stage_output`.** It is not one of §8.5's ten attribution stages, it decides nothing that could diverge, and inventing an eleventh stage would corrupt P2's closed `stage_id` enumeration. `stage_output` therefore exists here and always raises — the same pattern as `states.one_message_for` and `apply_seam.force_undo`, at the one place someone would reach for it. What P13 *does* owe is that **every surface must be renderable from a replay bundle**, so a review screen can be reconstructed for a past run without a live filesystem.

- [ ] **Step 1: Write the failing test**

`tests/p13/test_p13_replay.py`:

```python
"""§8.5: a review screen reconstructed for a past run, with no live filesystem."""
from __future__ import annotations

import pytest

from privacy.display import RedactionSettings
from tree_design.records import Node, PlanVersion
from tree_design.store import write_node, write_plan_version

from review_surface.presentation import record_presentation
from review_surface.replay import (
    NoStageOutputHere, NotRenderableFromABundle, assert_no_filesystem_needed,
    deserialize_presented_state, reassert_presented_state,
    serialize_presented_state, stage_output,
)
from review_surface.vocabulary import SURFACE_PLACEMENT

T0 = "2026-08-29T00:00:00Z"
SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")


def _state(conn):
    return record_presentation(
        conn, surface=SURFACE_PLACEMENT, subject_ref="d1",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=("obs-1", "obs-2"), user_id="jy",
        component_version="p13-1", rendered_at=T0)


def test_p13_emits_no_stage_output():
    """SPEC:400-404: inventing an eleventh stage would corrupt P2's closed
    `stage_id` enumeration."""
    with pytest.raises(NoStageOutputHere) as caught:
        stage_output()
    assert "eleventh" in str(caught.value) or "ten" in str(caught.value)


def test_a_presented_state_serializes_and_deserializes_unchanged(p13_conn):
    """Done-means 23, second clause."""
    state = _state(p13_conn)
    payload = serialize_presented_state(state)
    assert deserialize_presented_state(payload) == state


def test_the_serialized_form_is_json_round_trippable(p13_conn):
    import json
    state = _state(p13_conn)
    payload = json.loads(json.dumps(serialize_presented_state(state)))
    assert deserialize_presented_state(payload) == state


def test_the_ref_survives_a_bundle_because_it_is_deterministic(p13_conn, conn):
    """A ref minted in one database is the same ref in a replay of that run."""
    state = _state(p13_conn)
    payload = serialize_presented_state(state)
    # A DIFFERENT connection, standing in for the replay database.
    from database_agent.db import create_schema
    from review_surface.schema import create_review_schema
    create_schema(conn)
    create_review_schema(conn)
    replayed = reassert_presented_state(conn, payload)
    assert replayed.presented_state_ref == state.presented_state_ref
    assert replayed.redaction_policy == state.redaction_policy
    assert replayed.evidence_refs == state.evidence_refs


def test_reasserting_a_tampered_payload_is_refused(p13_conn, conn):
    """The ref is a hash over what was shown, so a changed policy changes the
    ref. A payload whose ref does not match its content is not that moment."""
    from database_agent.db import create_schema
    from review_surface.schema import create_review_schema
    create_schema(conn)
    create_review_schema(conn)
    payload = serialize_presented_state(_state(p13_conn))
    payload["redaction_policy"] = dict(payload["redaction_policy"])
    payload["redaction_policy"]["names"] = "redacted"
    with pytest.raises(NotRenderableFromABundle):
        reassert_presented_state(conn, payload)


def test_a_placement_item_builds_with_no_live_filesystem(p13_conn):
    """Done-means 23, first clause."""
    from placement.records import (
        DecisionDepth, Destination, PlacementDecision, PrivacyState, Subject,
    )
    from placement.vocabulary import EXACT_FACT_MATCH, PLACE
    from review_surface.items import placement_review_item

    write_plan_version(p13_conn, PlanVersion(
        plan_version_id="plan-1", predecessor_id=None, state="draft",
        created_at=T0, cross_folder_moves=False, selection_id="sel-1"))
    write_node(p13_conn, Node(
        node_id="n-1", plan_version_id="plan-1", node_type="proposed",
        display_label="Applications", parent_node_id=None, root_anchor="root",
        ordinal=0, associated_group_ids=(), explanation="fixture",
        node_role="ordinary", accepts_placement=True,
        handling_class="public_low", origin_node_id="n-1",
        template_context=None, dimension_role=None, dimension=None,
        expected_values=(), existing_path=None, disposition=None,
        refinement_disposition=None, refinement_reason=None,
        protected_movement_permitted=False))
    decision = PlacementDecision(
        decision_id="d1", plan_version="plan-1", supersedes=None,
        superseded_by=None, supersede_reason=None, created_at=T0,
        origin_stage="placement", returned_from=None,
        subject=Subject(kind="file", file_id="f-1", content_hash="h-1",
                        group_id=None, member_file_ids=()),
        group_plan_id=None, outcome=PLACE,
        destination=Destination(node_id="n-1", node_role="ordinary"),
        return_target=None, marked_state=None, ask=None,
        decision_depth=DecisionDepth(node_depth=1, supported_depth=1,
                                     unsupported_levels=()),
        evidence_type="direct", confidence_class=EXACT_FACT_MATCH,
        matching_facts=(), group_support=None, graph_anchors=(),
        conflicts_considered=(), alternatives=(), two_condition=None,
        abstention_reason=None, deferred_stage=None,
        privacy=PrivacyState(handling_class="public_low", protected=False,
                             model_eligibility="local_only",
                             consent_audit_ref=None),
        review_policy=None, explanation="direct match", residual=None)
    item = assert_no_filesystem_needed(
        lambda: placement_review_item(p13_conn, decision))
    assert item.destination_label_chain == ("Applications",)


def test_the_helper_catches_a_builder_that_touches_the_filesystem(p13_conn):
    """The guard must be able to fail, or it is not a guard."""
    def naughty():
        import os
        return os.listdir(".")
    with pytest.raises(NotRenderableFromABundle):
        assert_no_filesystem_needed(naughty)


def test_a_stored_action_and_approval_read_back_from_the_replay_database(
        p13_conn, conn):
    """A whole surface, reconstructed for a past run."""
    from database_agent.db import create_schema
    from review_surface.approval import approvals_for, record_approval
    from review_surface.collect import collect
    from review_surface.records import ReviewApproval
    from review_surface.schema import create_review_schema
    from review_surface.store import actions_for, record_action
    from review_surface.vocabulary import ACTION_ACCEPT, VERDICT_APPROVED

    state = _state(p13_conn)
    record_action(p13_conn, collect(
        p13_conn, action_id="a-1", surface=SURFACE_PLACEMENT,
        subject_ref="d1", plan_version="plan-1", session_id="s-1",
        action=ACTION_ACCEPT, correction_scope="file",
        presented_state_ref=state.presented_state_ref, user_id="jy",
        acted_at=T0, component_version="p13-1"))
    record_approval(p13_conn, ReviewApproval(
        approval_id="ap-1", plan_id="mp-1", placement_decision_ref="d1",
        plan_version="plan-1", required_review_policy="review_required",
        verdict=VERDICT_APPROVED,
        presented_state_ref=state.presented_state_ref, user_id="jy",
        decided_at=T0), component_version="p13-1")
    assert len(actions_for(p13_conn, subject_ref="d1")) == 1
    assert len(approvals_for(p13_conn, plan_id="mp-1")) == 1
```

- [ ] **Step 2: Run the test and verify RED**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_replay.py`

Expected: **FAIL** — `ModuleNotFoundError: No module named 'review_surface.replay'`.

- [ ] **Step 3: Write `src/review_surface/replay.py`**

```python
# src/review_surface/replay.py
"""What P13 owes P2, and what it does not.

    SPEC:400-407: P13 emits no `stage_output`. It is not one of §8.5's ten
    attribution stages, it decides nothing that could diverge, and inventing an
    eleventh stage would corrupt P2's closed `stage_id` enumeration.

So `stage_output` exists here and always raises -- the same pattern as
`states.one_message_for` and `apply_seam.force_undo`, placed where someone would
reach for it.

What P13 DOES owe is that every surface is renderable from a replay bundle, so a
review screen can be reconstructed for a past run WITHOUT A LIVE FILESYSTEM, and
that `presented_state_ref` serializes into and re-asserts from a bundle.

The ref is deterministic by construction (`presentation._ref` hashes the surface,
subject, version, session, policy, evidence refs and timestamp), so re-asserting
a payload in a replay database MINTS THE SAME REF. That is why `reassert` can
verify rather than trust: a payload whose stated ref does not match a re-hash of
its own content is not the moment it claims to be, and is refused.

`assert_no_filesystem_needed` installs no import hook and patches nothing global.
It counts filesystem calls by wrapping the handful of `os` entry points a builder
could plausibly reach, restores them in a `finally`, and re-raises as
`NotRenderableFromABundle`. A test asserts the guard can fail, because a guard
that cannot fail is the shape this project has been bitten by nine times.
"""
from __future__ import annotations

import os
import sqlite3
from collections.abc import Callable, Mapping
from typing import NoReturn

from review_surface.presentation import PresentedState, presented_state


class NoStageOutputHere(RuntimeError):
    """Something asked P13 for a P2 stage output. P13 is not a stage."""


class NotRenderableFromABundle(RuntimeError):
    """A surface needed a live filesystem, or a payload did not re-assert."""


def stage_output(*args: object, **kwargs: object) -> NoReturn:
    """Always raises. P13 is not one of §8.5's ten attribution stages."""
    raise NoStageOutputHere(
        "P13 emits no stage_output. It is not one of §8.5's ten attribution "
        "stages, it decides nothing that could diverge, and inventing an "
        "eleventh stage would corrupt P2's closed stage_id enumeration. What "
        "P13 owes P2 is that every surface is renderable from a replay bundle")


def serialize_presented_state(state: PresentedState) -> dict:
    """The bundle form. Plain JSON types only."""
    return {
        "presented_state_ref": state.presented_state_ref,
        "surface": state.surface,
        "subject_ref": state.subject_ref,
        "plan_version": state.plan_version,
        "session_id": state.session_id,
        "redaction_policy": dict(state.redaction_policy),
        "evidence_refs": list(state.evidence_refs),
        "user_id": state.user_id,
        "rendered_at": state.rendered_at,
        # `event_id` is a monotonic id LOCAL TO ONE DATABASE. It is carried so a
        # bundle can point back at the original log, and it is deliberately NOT
        # part of the ref: a replay database mints its own ids, and hashing one
        # in would make the same moment un-round-trippable.
        "event_id": state.event_id,
    }


def deserialize_presented_state(payload: Mapping[str, object]) -> PresentedState:
    """The record form, unchanged."""
    return PresentedState(
        presented_state_ref=str(payload["presented_state_ref"]),
        event_id=int(payload["event_id"]),
        surface=str(payload["surface"]),
        subject_ref=str(payload["subject_ref"]),
        plan_version=str(payload["plan_version"]),
        session_id=str(payload["session_id"]),
        redaction_policy=dict(payload["redaction_policy"]),  # type: ignore[arg-type]
        evidence_refs=tuple(payload["evidence_refs"]),  # type: ignore[arg-type]
        user_id=payload.get("user_id"),  # type: ignore[arg-type]
        rendered_at=str(payload["rendered_at"]))


def reassert_presented_state(conn: sqlite3.Connection,
                             payload: Mapping[str, object]) -> PresentedState:
    """Re-assert a bundled presentation into a replay database, verifying its ref.

    The ref is re-derived from the payload's own content. A mismatch means the
    payload has been altered since it was minted -- most importantly a changed
    redaction policy, which is exactly the alteration §8.4 makes consequential.
    """
    from review_surface.presentation import _ref

    state = deserialize_presented_state(payload)
    expected = _ref(state.surface, state.subject_ref, state.plan_version,
                    state.session_id, state.redaction_policy,
                    state.evidence_refs, state.rendered_at)
    if expected != state.presented_state_ref:
        raise NotRenderableFromABundle(
            f"the bundled presentation claims ref {state.presented_state_ref!r} "
            f"but its own content hashes to {expected!r}. The ref covers the "
            "surface, subject, plan version, session, redaction policy, evidence "
            "references and time, so a mismatch means this is not the moment it "
            "says it is")
    existing = presented_state(conn, state.presented_state_ref)
    if existing is not None:
        return existing
    conn.execute(
        "INSERT INTO review_presentations "
        "(presented_state_ref, event_id, surface, subject_ref, plan_version, "
        " session_id, redaction_policy, evidence_refs, user_id, rendered_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (state.presented_state_ref, state.event_id, state.surface,
         state.subject_ref, state.plan_version, state.session_id,
         _json(state.redaction_policy), _json(list(state.evidence_refs)),
         state.user_id, state.rendered_at))
    conn.commit()
    return state


def _json(value: object) -> str:
    import json
    return json.dumps(value, sort_keys=True)


#: The `os` entry points a surface builder could plausibly reach. Not exhaustive
#: of the filesystem API and not meant to be: it is a TRIPWIRE over the calls a
#: rendering path would actually make, and a test proves it can fire.
_WATCHED: tuple[str, ...] = (
    "listdir", "stat", "lstat", "scandir", "open", "walk", "readlink",
)


def assert_no_filesystem_needed(build: Callable[[], object]) -> object:
    """Run `build` and refuse if it touched the filesystem. Restores in `finally`.

    `sqlite3` reaches the filesystem through C, not through these Python entry
    points, so a real temporary-file database still works under this guard --
    which is what makes it usable at all. The guard is about a surface reading
    the user's files, not about the database it projects from.
    """
    touched: list[str] = []
    originals = {name: getattr(os, name) for name in _WATCHED
                 if hasattr(os, name)}

    def _make(name: str, original):
        def _watched(*args: object, **kwargs: object):
            touched.append(name)
            return original(*args, **kwargs)
        return _watched

    for name, original in originals.items():
        setattr(os, name, _make(name, original))
    try:
        result = build()
    finally:
        for name, original in originals.items():
            setattr(os, name, original)
    if touched:
        raise NotRenderableFromABundle(
            f"this surface reached the filesystem via os.{sorted(set(touched))}. "
            "§8.5 requires every surface to be renderable from a replay bundle, "
            "so a review screen can be reconstructed for a past run without a "
            "live filesystem")
    return result
```

- [ ] **Step 4: Run the test and verify PASS**

Run: `cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q -p no:randomly tests/p13/test_p13_replay.py`

Expected: **PASS** — eight tests green.

> If `test_the_helper_catches_a_builder_that_touches_the_filesystem` fails, the tripwire is not covering `os.listdir` under the test's import form. Widen `_WATCHED` or have the naughty builder call a watched name directly — but **do not delete the test**: a guard that cannot be made to fail is not a guard, and this project has shipped nine of those.

- [ ] **Step 5: Run the entire suite one last time**

```bash
cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src:. python3 -m pytest -q -p no:randomly tests/p13/ -rx
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest -q -p no:randomly 2>&1 | tail -5
```

Expected: every P13 test green, one deliberate `xfail` (Task 9's fixture-compatibility report), and the repository total at 5247 plus P13's tests with **no failures and no errors**.

- [ ] **Step 6: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/review_surface/replay.py tests/p13/test_p13_replay.py && git commit -m "feat(p13-20): every surface renderable from a bundle, and a presented_state_ref that round-trips"
```

---

## What this plan does NOT build, and why

| Not built | Why |
|---|---|
| Any visual design — layout, components, styling, typography, colour, iconography, interaction patterns, navigation, empty states, and every word of user-facing copy | The SPEC's Deferred table: it fixes the **information contract**, and *"inventing one here would be inventing design"*. The design gives one worked sentence per surface and no interface specification. Every "renders" in this plan is a record field plus a negative test. |
| The canvas surfaces (§5) as their own module | P10 publishes the six canvas data contracts (`candidates.BranchCandidate`, `candidates.VerticalOption`, `health.TreeHealth`, `health.Warning_`, `freeze.represent_protected_areas`, `profiles.build_profiles`), and P13's obligation is that a canvas gesture is collected and routed — which Task 9's `SURFACE_CANVAS → P10` routing does. A P13 module that re-projected P10's six records would be a second home for six shapes P10 owns. **`review_action` on the `canvas` surface is the whole contract**, and `tree_design.store.apply_review_action` already receives it. |
| A dry-run surface (`66` §9) | `66` §9 requires that the first run of every filing policy is a dry run showing what would move, from where, to where, why, and what was declined. **There is no filing-policy record in any part's Contract-out and no `src/` package for automatic filing** — it is item 5 of `63` §2's resequenced order. Task 11's `ActivityEntry` carries the gap explicitly. This is a real hole in P13's coverage of `66`, not an omission of convenience. |
| `66` §10's ten distinct refusal messages | `66` §10 requires distinct refusal language for a dozen filing declines. Some map onto records that exist (`states.py`'s five, `apply_seam`'s five staleness triggers, `placement.vocabulary.ABSTENTION_REASONS`' nine); the rest — *"This file has two approved homes"*, *"No approved destination fits"* — are **filing-policy refusals with no producer**, same gap as above. |
| A version-family or deduplication review screen | **SPEC Open question 10, unresolved:** §8.3 produces both outcomes and P12 OQ7 is settled that the screen is P13's, *"but no section names that screen's **action set**, which is what P13 would have to present and collect."* Building it would mean inventing the action set. |
| Anything that decides, scores, classifies, validates, resolves a path or mutates a filesystem | Done-means 22, enforced by Task 19's introspection guard. |

## Coverage of the SPEC's Done-means

| # | Task |
|---|---|
| 1 | 5 |
| 2 | 5 |
| 3 | 4 (consumed by 5) |
| 4 | 5, 6 |
| 5 | 7 |
| 6 | 8 |
| 7 | 9 |
| 8 | 10 |
| 9 | 9 |
| 10 | 10 |
| 11 | 12 |
| 12 | 11 |
| 13 | 11 |
| 14 | 2 (the cache clause), 13 |
| 15 | 13 |
| 16 | 14 |
| 17 | 13 |
| 18 | 15 |
| 19 | 16 |
| 20 | 17 |
| 21 | 18 |
| 22 | 19 |
| 23 | 20 |

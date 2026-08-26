# P10 Tree Design and Freeze Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build P10 so accepted P9 groups, validated P6 facts and the user's existing folders become one frozen destination tree — closed, explainable, versioned, and holding no filesystem path — that P11 may place into and no component may add to.

**North-star user experience:** The user is never asked to design a whole taxonomy before getting value. P10 proposes a small shallow scaffold, the user accepts or reshapes it, and only then does any branch get refined — one branch at a time, with the counts, examples, unresolved files and privacy effects of a change shown before it is committed. Every proposal states the facts that produced it in prose; no surface shows a confidence score. "Not refined yet" and "shallow by design" are both valid resting states, and both are freezeable. Freeze is a view over the evidence, never a rewrite of it: the user can rearrange the same facts into a different tree tomorrow without losing a single observation.

**Architecture:** P10 is a proposal-and-freeze layer over records it owns. It reads P9 groups, P6 fields, P3 folders and roots, and P7 handling classes; it writes nodes, destination profiles, template records, branch bindings, residual configuration, diffs and freeze state into its own tables inside P1's single database. Shared template library records are keyed by library release plus record version; only bindings and tree state are keyed by plan version. P10 moves no file, composes no path, classifies no sensitivity, and mutates no fact. Every candidate is inert until an explicit user approval is recorded, and every draft-altering action appends a §8.2 event through P1.

**Tech Stack:** Python 3.12, stdlib `sqlite3`/`dataclasses`/`json`, P1 append-only events, learning records and budget ceilings, P2 stage outputs, P3 selection and directory inventory, P6 field catalogue and read surfaces, P7 handling classes and operation modes, P8's frozen `run_call` and `TemplateDependencies`, P9 group records, pytest, Graphify.

---

## Authority and current-state ledger

Read in this order before executing a task:

1. `planning/00-database-agent-product-design.md` — original mission and §5/§6.1/§7.2–§7.4 behaviour.
2. `planning/04-resolutions.md` — B3, B4, B6, B7, B8, G9, M8, M10, M12, O11, O12, S3.
3. `planning/parts/P10-tree-design-freeze/SPEC.md` — the P10 contract.
4. `docs/superpowers/specs/2026-08-26-composable-template-scaffolding-design.md` — the composable-template seam.
5. `planning/domains/TEMPLATE-BUILDING-HANDOFF.md` — what the later library pass owes P10 and what P10 owes it.
6. `planning/30-p8-p9-connection-contract.md` — frozen P8 names.
7. Live P1–P9 source. **Exact callable and record names outrank the SPEC's prose names**; where they differ, this plan uses the live name and records the divergence under [SPEC corrections](#spec-corrections).

| Prerequisite | Current evidence | Plan treatment |
|---|---|---|
| P1 events | `database_agent.events.append_event(conn, **fields)`; `"template application"` and `"destination-tree edit"` are already reserved at `src/database_agent/events.py:33-34`; writable fields are `EVENT_FIELDS` + `CORRECTION_FIELDS` (`:11-22`); required are `event_type, subsystem, component_version, observed_at, explanation` (`:103`) | Task 5 is the sole P10 writer. Two reserved names with no producer is this project's named defect class |
| P1 learning | `database_agent.learning.learning_records(conn, scope, subject_id)` (`src/database_agent/learning.py:46-47`), honouring `reset_cutoff` (`:35-43`) | Task 5 publishes the branch-suppression read; Task 10 consults it before proposing |
| P1 ceilings | `database_agent.budget.get_ceiling(conn, key)` (`src/database_agent/budget.py:64-67`); `tree.max_folder_proposals_and_depth` is live at `:27`; `model.max_dossier_tokens_per_call` at `:19` | Task 3 reads both. No other key, no default |
| P1 plan versions | **Do not exist.** `grep -rn plan_version src/database_agent/*.py` returns nothing; §0's "destination nodes" are unimplemented | Task 2 creates `plan_versions` inside P1's database as a P10-owned table, the way P9 owns `group_acceptance` |
| P2 stages | `eval_harness.stage_output.record_stage_output(...)` (`src/eval_harness/stage_output.py:96-100`) with **required** `inputs` and `budget_state`; `template_generation` and `tree_design` live at `src/eval_harness/vocabulary.py:25-26`; `template` and `tree` dimensions at `:39-40` | Task 14 passes both required keywords and emits `DimensionValue` rows for `template` and `tree` |
| P3 selection | `scan_agent.selection.record_selection(conn, *, sources, candidate_roots, cross_folder_moves, selected_by)` (`src/scan_agent/selection.py:40-44`); readers `selection_candidate_roots` (`:79`), `get_selection` (`:68`) | Task 4 reads the roots and the permission; Task 14 stores the permission in the freeze record |
| P3 folder inventory | `scan_agent.inventory.directory_inventory(conn, scan_run_id)` (`src/scan_agent/inventory.py:88`); `CURATION_SIGNAL_VALUES` is **three** values, not two (`:20-25`), and `curation_signal` returns `undetermined` for every directory today (`:42-53`) | Task 4 carries all three verbatim. `undetermined` is a real value; P10 never rounds it to `incidental` |
| P6 fields | `facts.fields.get_field(conn, field_key)` (`src/facts/fields.py:281`), `facts.read_surface.is_destination_eligible(conn, *, field_key)` (`src/facts/read_surface.py:290`) | C2 resolves every semantic role through these two. P10 mints no field |
| P7 privacy | `privacy.vocabulary.HANDLING_CLASSES` (`src/privacy/vocabulary.py:86-92`) and `OPERATION_MODES` (`:112-114`) | Task 1 **imports** both; P10 re-spells neither and coins no display variant |
| P8 harness | `llm_harness.harness.run_call(conn, request, *, gate, model_client, prompt, validation_dependencies, observed_at)` (`src/llm_harness/harness.py:351-362`); Site E at `llm_harness.template_validation.validate_template_response(...)` (`src/llm_harness/template_validation.py:153-164`); `TemplateDependencies(schema_validator)` (`:26-27`) | Task 7 builds the `schema_validator` P10 owes P8. Task 6 builds the `DossierRequest`. P10 never touches transport or the gate |
| P8 Site E vocabulary | `E_TEMPLATE = "E_template"` (`src/llm_harness/vocabulary.py:24`); `TEMPLATE_ELIGIBILITY = ("accepted_group_fits_no_existing_template",)` (`:140`); `E_TEMPLATE` is in `SITES_REQUIRING_PLAN_VERSION` (`:158-160`) | Task 6 imports these. A Site-E request without a `plan_version` is refused by P8's own record |
| P9 grouping | Partially built: `src/grouping/` has `config, embeddings, fixtures, records, retrieval, schema, seeds, vocabulary`. `store.py`, `acceptance.py` and the accepted-group read surface **do not exist yet** | Tasks 1–13 run against `tests/p10/p9_fixtures.py`, a content-free fixture over the live `Group`/`Membership`/`GroupAcceptance` records. Task 15 names the swap |
| P11/P12/P13 | Not implemented | P10 publishes fixtures and read APIs only. No placement, path, or review-runtime concept enters `src/tree_design/` |

### Dependency gates

- **G-P9:** Tasks 1–13 build against `tests/p10/p9_fixtures.py`, which constructs **live** `grouping.records.Group`, `Membership` and `GroupAcceptance` objects. When `grouping.store` ships, Task 4's `AcceptedGroupReader` protocol is satisfied by it and the fixture is deleted from the production path. A production freeze requires real accepted groups; the fixture never reaches one.
- **G-P8:** Template generation calls P8's frozen `run_call` and nothing else. P10 supplies the `DossierRequest`, the `allowed_vocabulary` closure and the `TemplateDependencies.schema_validator`; P8 owns transport, release and the verdict. P10 never calls `privacy.gate.Gate.release` and constructs no `Dossier`.
- **G-P13:** Tree edits arrive as `tests/p10/p13_fixtures.py` review actions until P13 publishes its record. The fixture lives under `tests/` and `src/tree_design/` never imports it.
- **G-KNOWLEDGE:** A missing domain schema, applicability binding, fragment version, role-to-P6-field mapping, depth limit, §5.9 threshold or residual slot value raises `ConfigurationRequired` or produces a review candidate. It never selects a built-in value. This is how SPEC open questions 1 and 2 arrive: as absent configuration, not as a number this plan invents.
- **G-OPEN:** SPEC open questions 3, 5, 8, 9 and 10 remain open. The implementation stores no guessed answer: `protected` is carried as the §5.12 enum member **and** a separate `handling_class` (OQ3); `node_id` is minted per plan version with an explicit `origin_node_id` lineage column and no code depends on cross-version identity (OQ5); the scoped `General` is opt-in per parent and never auto-added (OQ8); the shared-material policy is stored with an explicit `policy_scope` naming which branch it covers, `None` meaning tree-global (OQ9); redaction axes beyond §5.2's filename default are injected configuration with no default (OQ10).
- **G-LIBRARY:** the authored 200–300 template library is `docs/superpowers/plans/2026-08-26-composable-template-library.md` and is gated behind this plan. Tasks 6–8 build the runtime contracts and deterministic fixtures; they import no domain research and author no domain content.

### Required execution order

Execute Tasks 1–5 in order; each is a substrate the rest import.

- **Task 1 before everything.** Every closed value in P10 has exactly one home, and a module written before the vocabulary exists will spell one as a literal — the defect that has cost this project the most (`planning/parts/_PLAN-AUTHORING-BRIEF.md:216-243`).
- **Task 3 before Tasks 8, 10 and 11.** V3's depth ceiling and §5.9's four thresholds are read, never chosen; a check written before the reader exists will hard-code a number.
- **Task 5 before Tasks 10 and 12.** `SPEC.md:882-885` requires the learning query to run *before* a branch candidate is proposed, and `SPEC.md:818-821` requires every draft-altering action to append an event. Building candidates or edits first produces a proposal path with no record of itself, which is unrecoverable after the fact.
- **Task 6 before Tasks 7, 8 and 10.** `SPEC.md:499` — "Composition gates precede V1–V6." A candidate cannot be materialised, validated or previewed before its composition resolves.
- **Task 6 before Task 7**, because the `schema_validator` rejects a proposal naming a fragment id/version the published catalogue does not contain, and it needs the catalogue reader to ask.
- **Task 9 before Task 14.** `SPEC.md:66-67` — P10 "cannot freeze a *complete* tree without the library that produces those nodes."
- **Task 10 before Task 11.** Health counts are computed over proposed nodes; there is nothing to count first.
- **Task 12 before Tasks 13 and 14.** A profile is emitted for a node in a version, and freeze validates a version; both need the versioned store.
- **Task 15 last.** It is the only task permitted to observe the whole package at once.

## File structure

```text
src/tree_design/__init__.py            narrow P10 public exports
src/tree_design/vocabulary.py          every closed P10 value; borrowed sets imported, never respelled
src/tree_design/records.py             frozen Node, DestinationProfile, template records, FreezeRecord, NodeDiff
src/tree_design/schema.py              P10-owned SQLite tables inside P1's database
src/tree_design/config.py              ConfigurationRequired; ceilings from P1; injected §5.9 thresholds
src/tree_design/upstream.py            P9/P6/P3/P7 read adapters; the only place another part's names appear
src/tree_design/provenance.py          §8.2 event writers and the §8.7 branch-suppression read
src/tree_design/catalogue.py           packaged template-library loader (the compiler's consumer)
src/tree_design/templates.py           fragment/definition/applicability records and the import graph
src/tree_design/routing.py             many-to-many applicability routing and composition gates C1–C8
src/tree_design/template_schema.py     the strict Site-E response schema and P10's schema_validator
src/tree_design/validation.py          the six §5.7 engine checks V1–V6
src/tree_design/residuals.py           nine residual definitions, eight slots, enablement projection
src/tree_design/candidates.py          horizontal scaffold and vertical branch proposals
src/tree_design/health.py              live counts, §5.9 warnings, tree health
src/tree_design/store.py               versioned writes, current reads, supersession
src/tree_design/diff.py                node-level diffs between two plan versions
src/tree_design/profiles.py            the §6.1 destination profile
src/tree_design/freeze.py              freeze validation and the ID-only legality projection
src/tree_design/stage_output.py        P10 → P2 template_generation / tree_design envelopes
src/tree_design/fixtures.py            frozen-tree and library fixtures P11/P12 build against

tests/p10/conftest.py                  real P1 database plus a seeded P6 field catalogue
tests/p10/p9_fixtures.py               live-record P9 accepted groups, tests only
tests/p10/p13_fixtures.py              review_action fixture, tests only
tests/p10/test_p10_*.py                focused TDD suites
tests/integration/test_p10_p9_tree.py  P9 groups → P10 scaffold
tests/integration/test_p10_p8_template.py  P10 schema_validator → P8 Site E
tests/integration/test_p10_p2_replay.py    P10 → P2 stage outputs
```

No task edits `planning/domains/`, `planning/deferred-catalogues/`, prompts, or any file under `src/` outside `src/tree_design/`.

---

### Task 1: Publish every closed P10 value, once

**Files:**
- Create: `src/tree_design/__init__.py`
- Create: `src/tree_design/vocabulary.py`
- Create: `tests/p10/__init__.py`
- Create: `tests/p10/conftest.py`
- Create: `tests/p10/test_p10_vocabulary.py`

**Interfaces:**

*Consumes:* `grouping.vocabulary.MEMBERSHIP_BASES`, `privacy.vocabulary.HANDLING_CLASSES` / `OPERATION_MODES`, `eval_harness.vocabulary.STAGE_IDS` / `DIMENSIONS` / `OUTCOMES` / `BUDGET_STATES`, `database_agent.events.CORRECTION_SCOPES` / `RESERVED_EVENT_TYPES`, `scan_agent.inventory.CURATION_SIGNAL_VALUES`, `llm_harness.vocabulary.E_TEMPLATE` / `TEMPLATE_ELIGIBILITY`.

*Produces:* one named constant per value **and** a tuple per set, for twenty-three P10-owned sets, plus eleven borrowed sets re-exported under P10 names that cannot be mistaken for a P10 definition; `OutOfVocabulary`; `check(value, closed, *, name) -> str`.

**Done-means:** groundwork for all seventeen. Directly: DM1 (records cannot round-trip a value the vocabulary does not define).

- [ ] **Step 1: Write the failing vocabulary test**

`tests/p10/conftest.py`:

```python
# tests/p10/conftest.py
"""A real P1 database with P6's field catalogue seeded.

P10 resolves every semantic role to a live P6 field, so a test database without
`fields` cannot exercise C2 at all. `open_database` already creates P1's tables.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from database_agent.db import open_database
from facts.fields import create_fields


@pytest.fixture()
def conn(tmp_path: Path):
    c = open_database(tmp_path / "agent.sqlite")
    create_fields(c)
    yield c
    c.close()
```

`tests/p10/test_p10_vocabulary.py`:

```python
# tests/p10/test_p10_vocabulary.py
"""P10 Task 1 — one home per closed value.

Two rules are load-bearing here. First, a borrowed vocabulary is IMPORTED, never
respelled: `handling_class` and `operation_mode` are P7's, and a second copy that
P7 later widens becomes a value P10 rejects and P7 accepts. Second, `draft` means
two different things in P10 — a template's publication lifecycle and a branch
binding's workflow state — so neither is spelled `DRAFT`.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from database_agent.events import CORRECTION_SCOPES, RESERVED_EVENT_TYPES
from eval_harness.vocabulary import BUDGET_STATES, DIMENSIONS, OUTCOMES, STAGE_IDS
from grouping.vocabulary import MEMBERSHIP_BASES
from llm_harness.vocabulary import E_TEMPLATE
from privacy.vocabulary import HANDLING_CLASSES, OPERATION_MODES
from scan_agent.inventory import CURATION_SIGNAL_VALUES
from tree_design import vocabulary as v

SRC = Path(__file__).resolve().parents[2] / "src" / "tree_design"


def test_every_p10_set_is_published_both_ways():
    """A tuple for membership, a named constant for every member (BRIEF:232-234)."""
    for name, closed in v.P10_CLOSED_SETS.items():
        assert isinstance(closed, tuple) and closed, name
        assert len(set(closed)) == len(closed), f"{name} repeats a value"
        for value in closed:
            constants = [
                k for k, obj in vars(v).items()
                if isinstance(obj, str) and obj == value and k.isupper()
            ]
            assert constants, f"{value!r} in {name} has no named constant"


def test_the_five_node_types_are_512s_five_in_512s_order():
    assert v.NODE_TYPES == (
        v.EXISTING, v.PROPOSED, v.USER_CREATED, v.PROTECTED, v.IGNORED,
    )
    assert v.NODE_TYPES == (
        "existing", "proposed", "user-created", "protected", "ignored",
    )


def test_the_four_node_roles_and_three_dispositions():
    assert v.NODE_ROLES == (
        v.ORDINARY, v.SCOPED_GENERAL, v.RESIDUAL, v.SHARED_MATERIAL,
    )
    assert v.RESIDUAL_DISPOSITIONS == (
        "physical-destination", "review-only", "leave-in-place",
    )


def test_draft_is_never_a_bare_name_because_it_means_two_things():
    """`publication_state = draft` is a library lifecycle; `state = draft` is a
    branch's workflow. Same word, different owners, so neither gets `DRAFT`."""
    assert not hasattr(v, "DRAFT")
    assert v.PUBLICATION_DRAFT == "draft"
    assert v.WORKFLOW_DRAFT == "draft"
    assert v.PUBLICATION_STATES == ("draft", "published", "retired")
    assert v.BINDING_STATES == ("draft", "reviewed", "approved")


def test_the_nine_residual_names_and_eight_slots_are_73s_lists():
    assert v.RESIDUAL_TEMPLATE_NAMES == (
        "Temporary Screenshots", "One-Off Images", "Reference Clips",
        "Independent Records", "Receipts and Confirmations", "Reading Inbox",
        "Review Later", "Unsupported or Encrypted", "Protected Records",
    )
    assert v.RESIDUAL_SLOTS == (
        "display_name", "default_parent_location", "accepted_evidence_patterns",
        "expected_file_types", "sensitivity_restrictions",
        "optional_shallow_subfolders", "max_permitted_depth", "treatment",
    )


def test_gates_and_checks_are_two_separate_eight_and_six_item_lists():
    assert v.COMPOSITION_GATES == ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8")
    assert v.TEMPLATE_CHECKS == ("V1", "V2", "V3", "V4", "V5", "V6")
    # P1's V1-V4 are §8.2 checksum points and share nothing but the letter.
    assert v.TEMPLATE_CHECK_MEANINGS["V4"].startswith("author or organization")


def test_borrowed_sets_are_the_owners_objects_not_copies():
    assert v.MEMBERSHIP_BASES is MEMBERSHIP_BASES
    assert v.HANDLING_CLASSES is HANDLING_CLASSES
    assert v.OPERATION_MODES is OPERATION_MODES
    assert v.CORRECTION_SCOPES is CORRECTION_SCOPES
    assert v.CURATION_SIGNAL_VALUES is CURATION_SIGNAL_VALUES
    assert v.P2_OUTCOMES is OUTCOMES
    assert v.P2_BUDGET_STATES is BUDGET_STATES


def test_p10s_two_stages_and_two_dimensions_belong_to_p2s_closed_lists():
    assert v.P10_STAGE_IDS == ("template_generation", "tree_design")
    assert all(stage in STAGE_IDS for stage in v.P10_STAGE_IDS)
    assert v.P10_DIMENSIONS == ("template", "tree")
    assert all(dimension in DIMENSIONS for dimension in v.P10_DIMENSIONS)
    assert "P10" not in STAGE_IDS


def test_p10s_two_event_names_are_82_reserved_names():
    assert v.TEMPLATE_APPLICATION in RESERVED_EVENT_TYPES
    assert v.DESTINATION_TREE_EDIT in RESERVED_EVENT_TYPES
    assert v.P10_EVENT_TYPES == (v.TEMPLATE_APPLICATION, v.DESTINATION_TREE_EDIT)


def test_the_site_p10_calls_is_p8s_named_one():
    assert v.CALL_SITE_TEMPLATE is E_TEMPLATE


def test_check_names_the_closed_set_and_refuses_a_near_miss():
    assert v.check("proposed", v.NODE_TYPES, name="node_type") == "proposed"
    with pytest.raises(v.OutOfVocabulary) as excinfo:
        v.check("propose", v.NODE_TYPES, name="node_type")
    assert "node_type" in str(excinfo.value)
    assert "propose" not in str(excinfo.value).replace("'propose'", "")


def test_no_module_outside_the_vocabulary_spells_a_closed_value():
    """A second home for a closed value is the defect this project keeps hitting.

    The check is over parsed string literals, not source text, because a text
    search matches comments and docstrings and has produced a false result on
    this project nine times.
    """
    every_value = {value for closed in v.P10_CLOSED_SETS.values() for value in closed}
    # Single characters and pure identifiers are excluded: `C1` and `V1` are also
    # plausible local names, and a dict key spelling a slot name is the record
    # field itself, not a second home for the vocabulary.
    guarded = {value for value in every_value if " " in value or "-" in value}
    offenders = []
    for path in sorted(SRC.glob("*.py")):
        if path.name == "vocabulary.py":
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Constant) and node.value in guarded:
                offenders.append(f"{path.name}:{node.lineno} {node.value!r}")
    assert offenders == []
```

- [ ] **Step 2: Run the test and verify RED**

Run: `python3.12 -m pytest -q tests/p10/test_p10_vocabulary.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'tree_design'`. Nothing under `src/tree_design/` exists yet, so the import of `tree_design.vocabulary` is the first thing to break.

- [ ] **Step 3: Write the vocabulary module**

`src/tree_design/__init__.py`:

```python
# src/tree_design/__init__.py
"""P10 — tree design and freeze.

P10 turns accepted groups, validated facts and existing folders into one frozen
destination tree and publishes it as the closed set of legal destinations. It
moves no file, composes no filesystem path, classifies no sensitivity and writes
no fact. The public surface grows task by task and is narrow by design.
"""
```

`src/tree_design/vocabulary.py`:

```python
# src/tree_design/vocabulary.py
"""P10's closed vocabularies. Named constant == string value, one home each.

Three collisions are handled by naming rather than by hoping:

* `draft` is a template's PUBLICATION lifecycle and also a branch binding's
  WORKFLOW state. Neither is `DRAFT`; both carry their axis in the name.
* `template`, `node`, `group`, `domain` and `corpus` are §8.7 correction scopes
  AND ordinary P10 nouns. The scopes are imported from P1, never respelled.
* P10's V1-V6 are §5.7's template design checks. P1's V1-V4 are §8.2's checksum
  verification points. They share the letter and nothing else.

Every set another part owns is IMPORTED. A second copy of P7's handling classes
would silently disagree with P7 the day P7 adds one, and the disagreement would
look like a P10 load error on a file P7 had classified correctly.
"""
from __future__ import annotations

from types import MappingProxyType

from database_agent.events import CORRECTION_SCOPES, RESERVED_EVENT_TYPES
from eval_harness.vocabulary import (
    BUDGET_STATES as _P2_BUDGET_STATES,
    OUTCOMES as _P2_OUTCOMES,
)
from grouping.vocabulary import MEMBERSHIP_BASES
from llm_harness.vocabulary import E_TEMPLATE, TEMPLATE_ELIGIBILITY
from privacy.vocabulary import HANDLING_CLASSES, OPERATION_MODES
from scan_agent.inventory import CURATION_SIGNAL_VALUES

# --- node identity (§5.12) ------------------------------------------------------

EXISTING: str = "existing"
PROPOSED: str = "proposed"
USER_CREATED: str = "user-created"
PROTECTED: str = "protected"
IGNORED: str = "ignored"

#: §5.12's five, in §5.12's order. Whether `protected` is a type or an orthogonal
#: flag is SPEC open question 3; this carries the enum literally AND a separate
#: `handling_class` so the answer can go either way without a migration.
NODE_TYPES: tuple[str, ...] = (EXISTING, PROPOSED, USER_CREATED, PROTECTED, IGNORED)

ORDINARY: str = "ordinary"
SCOPED_GENERAL: str = "scoped-general"
RESIDUAL: str = "residual"
SHARED_MATERIAL: str = "shared-material"

#: MINOR 6: P10 owns the tree, so P10 names its node kinds. P11 carries these
#: verbatim and publishes no parallel vocabulary.
NODE_ROLES: tuple[str, ...] = (ORDINARY, SCOPED_GENERAL, RESIDUAL, SHARED_MATERIAL)

PHYSICAL_DESTINATION: str = "physical-destination"
REVIEW_ONLY: str = "review-only"
LEAVE_IN_PLACE: str = "leave-in-place"

#: §7.4. Required on a `residual` node, meaningless on every other role.
RESIDUAL_DISPOSITIONS: tuple[str, ...] = (
    PHYSICAL_DESTINATION, REVIEW_ONLY, LEAVE_IN_PLACE,
)

REFINED: str = "refined"
SHALLOW_BY_CHOICE: str = "shallow-by-choice"
REFINE_LATER: str = "refine-later"

#: §5.8 + §8.8. `shallow-by-choice` and `refine-later` are different answers, and
#: collapsing them would make a deliberate design look like unfinished work.
REFINEMENT_DISPOSITIONS: tuple[str, ...] = (REFINED, SHALLOW_BY_CHOICE, REFINE_LATER)

# --- template records (§5.4, §5.7) ----------------------------------------------

BUILT_IN: str = "built-in"
LLM_GENERATED: str = "llm-generated"
USER_AUTHORED: str = "user-authored"

#: WHO authored the recipe. Three axes are kept apart deliberately: authorship,
#: scope and lifecycle answer three different questions, and "user-saved" used to
#: stand in for two of them.
ORIGIN_KINDS: tuple[str, ...] = (BUILT_IN, LLM_GENERATED, USER_AUTHORED)

DOMAIN_FOCUSED: str = "domain-focused"
CROSS_DOMAIN: str = "cross-domain"
PURPOSE_FOCUSED: str = "purpose-focused"
PERSONAL: str = "personal"

#: WHAT the recipe spans.
SCOPE_KINDS: tuple[str, ...] = (
    DOMAIN_FOCUSED, CROSS_DOMAIN, PURPOSE_FOCUSED, PERSONAL,
)

PUBLICATION_DRAFT: str = "draft"
PUBLISHED: str = "published"
RETIRED: str = "retired"

#: WHERE the recipe is in its library lifecycle. Saving a draft definition does
#: not activate it and publishing a newer record does not migrate a prior binding.
PUBLICATION_STATES: tuple[str, ...] = (PUBLICATION_DRAFT, PUBLISHED, RETIRED)

REQUIRED: str = "required"
OPTIONAL: str = "optional"

DIMENSION_REQUIREMENTS: tuple[str, ...] = (REQUIRED, OPTIONAL)

WORKFLOW_DRAFT: str = "draft"
WORKFLOW_REVIEWED: str = "reviewed"
WORKFLOW_APPROVED: str = "approved"

#: A branch binding's workflow state. The SPEC's example binding shows only
#: `approved`; the closed set is the composable-template design's.
BINDING_STATES: tuple[str, ...] = (
    WORKFLOW_DRAFT, WORKFLOW_REVIEWED, WORKFLOW_APPROVED,
)

ACTION_SELECTED: str = "selected"
ACTION_OMITTED: str = "omitted"
ACTION_REORDERED: str = "reordered"
ACTION_FLATTENED: str = "flattened"
ACTION_RENAMED: str = "renamed"
ACTION_ADDED: str = "added"

#: What the user did to one dimension of a routed recipe, recorded per branch.
#: Six, not four: `renamed` and `added` are legal edits and an unrepresentable
#: edit is an edit the diff cannot explain.
DIMENSION_ACTIONS: tuple[str, ...] = (
    ACTION_SELECTED, ACTION_OMITTED, ACTION_REORDERED, ACTION_FLATTENED,
    ACTION_RENAMED, ACTION_ADDED,
)

# --- the two check families -----------------------------------------------------

COMPOSITION_GATES: tuple[str, ...] = ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8")

COMPOSITION_GATE_MEANINGS: MappingProxyType = MappingProxyType({
    "C1": "every referenced template, fragment, applicability and version exists",
    "C2": "every resolved dimension maps to a live P6 field",
    "C3": "the branch's accepted groups and facts satisfy the selected binding",
    "C4": "a required role resolves exactly once",
    "C5": "combined relative-order constraints are acyclic",
    "C6": "the composition loses no group or file silently",
    "C7": "combined privacy is no weaker than any included restriction",
    "C8": "a valid preview stays inert until branch-specific approval",
})

TEMPLATE_CHECKS: tuple[str, ...] = ("V1", "V2", "V3", "V4", "V5", "V6")

#: §5.7's six, run by P10 over the materialised candidate. P8 enforces the
#: response shape and returns a verdict; it runs none of these.
TEMPLATE_CHECK_MEANINGS: MappingProxyType = MappingProxyType({
    "V1": "repeats a parent dimension",
    "V2": "creates meaningless one-child levels",
    "V3": "exceeds practical depth limits",
    "V4": "author or organization used merely as a collector",
    "V5": "exposes protected information",
    "V6": "produces empty branches against the accepted group",
})

# --- the residual library (§7.2, §7.3, §7.4) ------------------------------------

#: §7.3's nine, in §7.3's order. Fixed names; their slot VALUES are deferred and
#: none is invented here.
RESIDUAL_TEMPLATE_NAMES: tuple[str, ...] = (
    "Temporary Screenshots",
    "One-Off Images",
    "Reference Clips",
    "Independent Records",
    "Receipts and Confirmations",
    "Reading Inbox",
    "Review Later",
    "Unsupported or Encrypted",
    "Protected Records",
)

#: §7.3 states a default parent for the first four only. The remaining five have
#: none stated, and an invented default would be P10 authoring §7.3.
RESIDUAL_DEFAULT_PARENTS: MappingProxyType = MappingProxyType({
    "Temporary Screenshots": ("Photos", "Temporary Screenshots"),
    "One-Off Images": ("Photos", "One-Off Images"),
    "Reference Clips": ("Personal", "Reference Clips"),
    "Independent Records": ("Personal", "Independent Records"),
})

#: §7.2's eight attribute slots. Every residual template defines all eight.
RESIDUAL_SLOTS: tuple[str, ...] = (
    "display_name",
    "default_parent_location",
    "accepted_evidence_patterns",
    "expected_file_types",
    "sensitivity_restrictions",
    "optional_shallow_subfolders",
    "max_permitted_depth",
    "treatment",
)

TREATMENT_REVIEWED: str = "reviewed"
TREATMENT_RETAINED: str = "retained"
TREATMENT_KEPT_SEARCHABLE: str = "merely kept searchable"

RESIDUAL_TREATMENTS: tuple[str, ...] = (
    TREATMENT_REVIEWED, TREATMENT_RETAINED, TREATMENT_KEPT_SEARCHABLE,
)

ENABLE: str = "enable"
DISABLE: str = "disable"
RENAME_RESIDUAL: str = "rename"
RELOCATE: str = "relocate"
MERGE_RESIDUAL: str = "merge"
REPLACE_WITH_EXISTING: str = "replace-with-existing"

#: §7.4's six. A template the user did not enable has no node, which is the whole
#: enforcement mechanism: no model can return a destination that does not exist.
RESIDUAL_ACTIONS: tuple[str, ...] = (
    ENABLE, DISABLE, RENAME_RESIDUAL, RELOCATE, MERGE_RESIDUAL,
    REPLACE_WITH_EXISTING,
)

# --- tree-level policies --------------------------------------------------------

SHARED_BRANCH: str = "shared-branch"
PRIMARY_HOME: str = "primary-home"
REFERENCE_OR_ALIAS: str = "reference-or-alias"
MANDATORY_REVIEW: str = "mandatory-review"

#: §6.9. Without one of these recorded, P11 must abstain on a file that belongs
#: to two packets rather than pick one. Whether the policy is tree-global or
#: per-branch is SPEC open question 9, so the record carries an explicit
#: `policy_scope` and this vocabulary answers only WHICH policy.
SHARED_MATERIAL_POLICIES: tuple[str, ...] = (
    SHARED_BRANCH, PRIMARY_HOME, REFERENCE_OR_ALIAS, MANDATORY_REVIEW,
)

# --- user actions ---------------------------------------------------------------

ACCEPT: str = "accept"
RENAME: str = "rename"
MERGE: str = "merge"
MOVE_UNDER_ROOT: str = "move-under-root"
DEFER: str = "defer"
CREATE_MANUALLY: str = "create-manually"
ADD: str = "add"
REMOVE: str = "remove"
SPLIT: str = "split"
NEST: str = "nest"
REORDER: str = "reorder"
IGNORE: str = "ignore"
DRAG_GROUP_INTO_BRANCH: str = "drag-group-into-branch"
DELETE_SUGGESTED_AREA: str = "delete-suggested-area"

#: Everything §5.1, §5.2 and §5's opening give the user on a branch candidate.
BRANCH_ACTIONS: tuple[str, ...] = (
    ACCEPT, RENAME, MERGE, MOVE_UNDER_ROOT, DEFER, CREATE_MANUALLY,
    ADD, REMOVE, SPLIT, NEST, REORDER, IGNORE,
    DRAG_GROUP_INTO_BRANCH, DELETE_SUGGESTED_AREA,
)

PRESERVE: str = "preserve"
ADOPT_AS_BRANCH: str = "adopt-as-branch"
MERGE_WITH_PROPOSAL: str = "merge-with-proposal"
ATTACH_BENEATH: str = "attach-beneath"
RENAME_PROPOSAL_TO_MATCH: str = "rename-proposal-to-match"
LEAVE_UNTOUCHED: str = "leave-untouched"

#: §5.10's six. Every one is an explicit user action; §5.10 forbids reaching any
#: of these outcomes because a template would have produced a different shape.
EXISTING_FOLDER_ACTIONS: tuple[str, ...] = (
    PRESERVE, ADOPT_AS_BRANCH, MERGE_WITH_PROPOSAL, ATTACH_BENEATH,
    RENAME_PROPOSAL_TO_MATCH, LEAVE_UNTOUCHED,
)

REPARENT: str = "re-parent"
DELETE: str = "delete"
ADOPT_EXISTING: str = "adopt-existing"
ADD_SCOPED_GENERAL: str = "add-scoped-general"
SET_SHARED_MATERIAL_POLICY: str = "set-shared-material-policy"
ENABLE_RESIDUAL: str = "enable-residual"
DISABLE_RESIDUAL: str = "disable-residual"

#: §8.2: every canvas action that alters the draft tree appends one
#: `destination-tree edit` event carrying one of these.
TREE_EDIT_ACTIONS: tuple[str, ...] = (
    ACCEPT, RENAME, MERGE, SPLIT, NEST, REPARENT, REORDER, IGNORE, DELETE,
    CREATE_MANUALLY, ADOPT_EXISTING, ENABLE_RESIDUAL, DISABLE_RESIDUAL,
    ADD_SCOPED_GENERAL, SET_SHARED_MATERIAL_POLICY,
)

ADOPT_VERSION: str = "adopt_version"
RESTORE_VERSION: str = "restore_version"

#: §8.8's two version actions, in P13's spelling. They act on a plan version
#: rather than on a node, so they are not `destination-tree edit` actions.
VERSION_ACTIONS: tuple[str, ...] = (ADOPT_VERSION, RESTORE_VERSION)

# --- diffs and warnings ---------------------------------------------------------

DIFF_ADDED: str = "added"
DIFF_REMOVED: str = "removed"
DIFF_RENAMED: str = "renamed"
DIFF_REPARENTED: str = "re-parented"
DIFF_RETEMPLATED: str = "re-templated"
DIFF_REORDERED: str = "re-ordered"
DIFF_TYPE_CHANGED: str = "type-changed"

#: §8.8's seven node-level changes. P11 computes the file-level consequence from
#: this diff; P10 does not, because P10 holds no placement decision.
DIFF_KINDS: tuple[str, ...] = (
    DIFF_ADDED, DIFF_REMOVED, DIFF_RENAMED, DIFF_REPARENTED, DIFF_RETEMPLATED,
    DIFF_REORDERED, DIFF_TYPE_CHANGED,
)

WARN_ONE_CHILD: str = "one-child-level"
WARN_REPEATED_PARENT: str = "repeated-parent-concept"
WARN_EXCESSIVE_DEPTH: str = "excessive-depth"
WARN_TINY_FOLDERS: str = "tiny-folder-distribution"
RECOMMEND_FLATTEN: str = "flatten-recommendation"

#: §5.9's four warnings plus its flattening recommendation. Every one needs a
#: threshold the design deliberately does not set, so none can fire without
#: configuration (SPEC open question 2).
WARNING_KINDS: tuple[str, ...] = (
    WARN_ONE_CHILD, WARN_REPEATED_PARENT, WARN_EXCESSIVE_DEPTH,
    WARN_TINY_FOLDERS, RECOMMEND_FLATTEN,
)

# --- borrowed values, named because they collide or because they have no name ----
#
# §8.2 reserves these two names as bare strings inside a frozenset; P1 publishes
# no named constant for either. P10 gives each one home rather than a literal at
# every call site, and asserts membership so a rename upstream fails here loudly.

TEMPLATE_APPLICATION: str = "template application"
DESTINATION_TREE_EDIT: str = "destination-tree edit"

P10_EVENT_TYPES: tuple[str, ...] = (TEMPLATE_APPLICATION, DESTINATION_TREE_EDIT)

for _name in P10_EVENT_TYPES:
    if _name not in RESERVED_EVENT_TYPES:  # pragma: no cover - import-time guard
        raise ImportError(
            f"{_name!r} is no longer one of §8.2's reserved event names; P10 "
            "appends only names P1 reserves and mints none of its own"
        )

#: P2's two P10 stages. `P10` is not a stage id: a part name in that field would
#: leave two of §8.5's ten stages with no producer.
TEMPLATE_GENERATION: str = "template_generation"
TREE_DESIGN: str = "tree_design"
P10_STAGE_IDS: tuple[str, ...] = (TEMPLATE_GENERATION, TREE_DESIGN)

#: P2's two P10 dimensions. Two lists, not one: `template_generation` is a stage
#: and `template` is a dimension, and P2 derives no mapping between them.
DIMENSION_TEMPLATE: str = "template"
DIMENSION_TREE: str = "tree"
P10_DIMENSIONS: tuple[str, ...] = (DIMENSION_TEMPLATE, DIMENSION_TREE)

#: P2's envelope vocabulary, imported. P10 maps its own results into these and
#: restates neither set in words of its own.
P2_OUTCOMES: tuple[str, ...] = _P2_OUTCOMES
P2_BUDGET_STATES: tuple[str, ...] = _P2_BUDGET_STATES

#: P8's call site and its single eligibility reason, imported.
CALL_SITE_TEMPLATE: str = E_TEMPLATE
TEMPLATE_ELIGIBILITY_REASONS: tuple[str, ...] = TEMPLATE_ELIGIBILITY

#: P13 collects tree edits on one of two surfaces (§5, §8.8). P13 is unbuilt and
#: publishes no constant, so P10 names them here and Task 15 replaces this block
#: with P13's import.
SURFACE_CANVAS: str = "canvas"
SURFACE_PLAN_VERSION: str = "plan_version"
REVIEW_SURFACES: tuple[str, ...] = (SURFACE_CANVAS, SURFACE_PLAN_VERSION)

# --- the registry ---------------------------------------------------------------

#: Every closed set P10 defines or carries, by the record field it governs. The
#: guard test walks this, so a set added without an entry is a set with no test.
P10_CLOSED_SETS: MappingProxyType = MappingProxyType({
    "node_type": NODE_TYPES,
    "node_role": NODE_ROLES,
    "disposition": RESIDUAL_DISPOSITIONS,
    "refinement_disposition": REFINEMENT_DISPOSITIONS,
    "origin_kind": ORIGIN_KINDS,
    "scope_kind": SCOPE_KINDS,
    "publication_state": PUBLICATION_STATES,
    "requirement": DIMENSION_REQUIREMENTS,
    "binding_state": BINDING_STATES,
    "dimension_action": DIMENSION_ACTIONS,
    "composition_gate": COMPOSITION_GATES,
    "template_check": TEMPLATE_CHECKS,
    "residual_template_name": RESIDUAL_TEMPLATE_NAMES,
    "residual_slot": RESIDUAL_SLOTS,
    "treatment": RESIDUAL_TREATMENTS,
    "residual_action": RESIDUAL_ACTIONS,
    "shared_material_policy": SHARED_MATERIAL_POLICIES,
    "branch_action": BRANCH_ACTIONS,
    "existing_folder_action": EXISTING_FOLDER_ACTIONS,
    "tree_edit_action": TREE_EDIT_ACTIONS,
    "version_action": VERSION_ACTIONS,
    "diff_kind": DIFF_KINDS,
    "warning_kind": WARNING_KINDS,
    "event_type": P10_EVENT_TYPES,
    "stage_id": P10_STAGE_IDS,
    "dimension": P10_DIMENSIONS,
    "outcome": P2_OUTCOMES,
    "budget_state": P2_BUDGET_STATES,
    "membership_basis": MEMBERSHIP_BASES,
    "handling_class": HANDLING_CLASSES,
    "operation_mode": OPERATION_MODES,
    "correction_scope": CORRECTION_SCOPES,
    "curation_signal": CURATION_SIGNAL_VALUES,
    "eligibility_reason": TEMPLATE_ELIGIBILITY_REASONS,
    "surface": REVIEW_SURFACES,
})


class OutOfVocabulary(ValueError):
    """A value outside a closed P10 set. Not a fallback; a load error."""


def check(value: object, closed: tuple[str, ...], *, name: str) -> str:
    """One membership test. The closed set is named; the nearest match is not.

    Naming a nearest match would be a suggestion, and a suggestion in a
    vocabulary this size is how a misspelling becomes a silent downgrade.
    """
    if not isinstance(value, str) or value not in closed:
        raise OutOfVocabulary(
            f"{name} is not one of the {len(closed)} values P10 defines for it. "
            "Adding a member is a contract revision, not an implementation "
            "decision."
        )
    return value
```

- [ ] **Step 4: Run the test and verify GREEN**

Run: `python3.12 -m pytest -q tests/p10/test_p10_vocabulary.py`

Expected: PASS, eleven tests. `test_no_module_outside_the_vocabulary_spells_a_closed_value` passes trivially today because `vocabulary.py` is the only module; it becomes load-bearing from Task 2 onward and must never be weakened.

- [ ] **Step 5: Commit**

```bash
git add src/tree_design/__init__.py src/tree_design/vocabulary.py \
        tests/p10/__init__.py tests/p10/conftest.py tests/p10/test_p10_vocabulary.py
git commit -m "feat(p10): publish closed tree-design vocabularies"
```

### Task 2: Frozen node records and the P10 schema

**Files:**
- Create: `src/tree_design/records.py`
- Create: `src/tree_design/schema.py`
- Create: `tests/p10/test_p10_records.py`

**Interfaces:**

*Consumes:* `tree_design.vocabulary` (`NODE_TYPES`, `NODE_ROLES`, `RESIDUAL_DISPOSITIONS`, `REFINEMENT_DISPOSITIONS`, `HANDLING_CLASSES`, `SHARED_MATERIAL_POLICIES`, `check`), `evidence_shape.canonical.canonical_json`.

*Produces:*

```python
class MalformedTreeRecord(ValueError): ...

@dataclass(frozen=True)
class ExpectedValue:
    field: str
    value: str

@dataclass(frozen=True)
class TemplateContext:
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

@dataclass(frozen=True)
class SharedMaterialPolicy:
    policy_id: str
    plan_version_id: str
    policy: str
    policy_scope: str | None
    reason: str

@dataclass(frozen=True)
class PlanVersion:
    plan_version_id: str
    predecessor_id: str | None
    state: str
    created_at: str
    cross_folder_moves: bool
    selection_id: str

def derive_accepts_placement(node_type: str, *,
                             protected_movement_permitted: bool) -> bool: ...
def create_tree_schema(conn: sqlite3.Connection) -> None: ...
P10_TABLES: tuple[str, ...]
```

**Done-means:** DM1 (records round-trip), DM11 (no published node carries a filesystem path other than `existing_path`), and the storage half of DM3 and DM17.

- [ ] **Step 1: Write the failing record and schema tests**

```python
# tests/p10/test_p10_records.py
"""P10 Task 2 — the node record, the plan version, and P10's own tables.

Two shape rules carry the most weight.

`accepts_placement` is DERIVED and then STORED, and the record refuses a stored
value that disagrees with the derivation. P11 needs one flag rather than a case
analysis (resolution B6), but a flag nobody can re-derive is a flag that drifts.

No node holds a composed path. `root_anchor` plus the ancestor `display_label`
chain is what P10 publishes; P12 composes the path and applies §8.3's
case-sensitivity, Unicode and length rules. A plan-versioned tree holding
platform-specific strings would resolve differently on a case-sensitive and a
case-insensitive volume, and the same frozen tree must resolve on both.
"""
from __future__ import annotations

import dataclasses
import json

import pytest

from tree_design.records import (
    ExpectedValue,
    MalformedTreeRecord,
    Node,
    PlanVersion,
    SharedMaterialPolicy,
    TemplateContext,
    derive_accepts_placement,
)
from tree_design.schema import P10_TABLES, create_tree_schema
from tree_design.vocabulary import (
    EXISTING,
    IGNORED,
    ORDINARY,
    PHYSICAL_DESTINATION,
    PRIMARY_HOME,
    PROPOSED,
    PROTECTED,
    REFINED,
    RESIDUAL,
    SHALLOW_BY_CHOICE,
    USER_CREATED,
)

BASE = dict(
    node_id="n_1", plan_version_id="plan_1", node_type=PROPOSED,
    display_label="Homework", parent_node_id="n_0", root_anchor="root_documents",
    ordinal=2, associated_group_ids=("g_phys1401",),
    explanation="Six files in the accepted PHYS1401 group carry work type = Homework.",
    node_role=ORDINARY, accepts_placement=True,
    handling_class="personal_non_sensitive", origin_node_id="n_1",
)


def test_a_node_round_trips_through_canonical_json():
    node = Node(
        **BASE,
        template_context=TemplateContext(
            binding_id="btb_1", template_id="academic-coursework",
            template_version=1, dimension_index=3,
            fragment_id="artifact-kind", fragment_version=1,
        ),
        dimension_role="artifact_kind",
        dimension="work_type",
        expected_values=(ExpectedValue(field="work_type", value="Homework"),),
        refinement_disposition=REFINED,
        refinement_reason="The course has enough populated work types to help retrieval.",
    )
    encoded = json.dumps(dataclasses.asdict(node), sort_keys=True)
    restored = json.loads(encoded)
    assert restored["template_context"]["fragment_version"] == 1
    assert restored["expected_values"] == [{"field": "work_type", "value": "Homework"}]
    assert restored["dimension_role"] == "artifact_kind"
    assert restored["dimension"] == "work_type"


def test_accepts_placement_is_derived_from_type_and_policy_only():
    for node_type in (EXISTING, PROPOSED, USER_CREATED):
        assert derive_accepts_placement(node_type, protected_movement_permitted=False)
    # §5.10 lets the user leave an existing folder untouched; an ignored node is
    # visible context, never a destination.
    assert not derive_accepts_placement(IGNORED, protected_movement_permitted=True)
    # §8.4: protected material "should not be moved automatically without a user
    # policy that explicitly permits it".
    assert not derive_accepts_placement(PROTECTED, protected_movement_permitted=False)
    assert derive_accepts_placement(PROTECTED, protected_movement_permitted=True)


def test_a_stored_flag_that_contradicts_the_derivation_is_refused():
    with pytest.raises(MalformedTreeRecord) as excinfo:
        Node(**{**BASE, "node_type": IGNORED, "accepts_placement": True})
    assert "ignored" in str(excinfo.value)


def test_no_node_field_but_existing_path_may_hold_a_separator():
    with pytest.raises(MalformedTreeRecord):
        Node(**{**BASE, "display_label": "Academics/Columbia"})
    with pytest.raises(MalformedTreeRecord):
        Node(**{**BASE, "display_label": "Academics\\Columbia"})
    observed = Node(**{
        **BASE, "node_type": EXISTING, "display_label": "To Sort",
        "existing_path": "/Users/jy/Documents/To Sort",
    })
    assert observed.existing_path == "/Users/jy/Documents/To Sort"


def test_existing_path_belongs_only_to_an_existing_node():
    with pytest.raises(MalformedTreeRecord) as excinfo:
        Node(**{**BASE, "existing_path": "/Users/jy/Documents/Homework"})
    assert "existing" in str(excinfo.value)


def test_every_node_carries_a_non_empty_prose_explanation():
    with pytest.raises(MalformedTreeRecord):
        Node(**{**BASE, "explanation": ""})
    with pytest.raises(MalformedTreeRecord):
        Node(**{**BASE, "explanation": "   "})


def test_disposition_is_required_on_a_residual_node_and_refused_elsewhere():
    residual = Node(**{
        **BASE, "node_role": RESIDUAL, "disposition": PHYSICAL_DESTINATION,
    })
    assert residual.disposition == PHYSICAL_DESTINATION
    with pytest.raises(MalformedTreeRecord):
        Node(**{**BASE, "node_role": RESIDUAL})
    with pytest.raises(MalformedTreeRecord):
        Node(**{**BASE, "disposition": PHYSICAL_DESTINATION})


def test_a_refinement_disposition_always_carries_its_reason():
    """§5.8: an intentionally shallow branch and an unfinished one are different
    states, and only the reason distinguishes them."""
    with pytest.raises(MalformedTreeRecord):
        Node(**{**BASE, "refinement_disposition": SHALLOW_BY_CHOICE})
    node = Node(**{
        **BASE, "refinement_disposition": SHALLOW_BY_CHOICE,
        "refinement_reason": "Twelve receipts do not need a per-vendor level.",
    })
    assert node.refinement_disposition == SHALLOW_BY_CHOICE


def test_a_top_level_branch_has_a_null_parent_but_always_a_root_anchor():
    top = Node(**{**BASE, "parent_node_id": None})
    assert top.parent_node_id is None
    with pytest.raises(MalformedTreeRecord):
        Node(**{**BASE, "root_anchor": ""})


def test_unknown_vocabulary_values_are_load_errors_not_fallbacks():
    for field, bad in (
        ("node_type", "suggested"),
        ("node_role", "catch-all"),
        ("handling_class", "Public or low sensitivity"),
    ):
        with pytest.raises(Exception):
            Node(**{**BASE, field: bad})


def test_a_shared_material_policy_records_which_branch_it_covers():
    """SPEC open question 9 is open: §6.9 reads global, its example reads
    branch-local. `policy_scope = None` means tree-global and is a value, not a
    missing one, so the answer can land either way without a migration."""
    policy = SharedMaterialPolicy(
        policy_id="smp_1", plan_version_id="plan_1", policy=PRIMARY_HOME,
        policy_scope=None,
        reason="One packet is the primary home; the other references it.",
    )
    assert policy.policy_scope is None
    branch_local = dataclasses.replace(policy, policy_scope="n_applications")
    assert branch_local.policy_scope == "n_applications"


def test_the_schema_is_idempotent_and_owns_only_p10_tables(conn):
    create_tree_schema(conn)
    create_tree_schema(conn)
    names = {
        row["name"] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    assert set(P10_TABLES) <= names
    assert "events" in names  # P1's, untouched


def test_a_plan_version_carries_p3s_cross_folder_permission(conn):
    """§1.1's "whether files may move across high-level folders" is recorded by
    P3 as `cross_folder_moves` and STORED by P10 at freeze under §8.8's placement
    policy settings. P12 enforces it at mutation time."""
    create_tree_schema(conn)
    version = PlanVersion(
        plan_version_id="plan_1", predecessor_id=None, state="draft",
        created_at="2026-08-27T00:00:00Z", cross_folder_moves=False,
        selection_id="sel_1",
    )
    conn.execute(
        "INSERT INTO plan_versions (plan_version_id, predecessor_id, state, "
        "created_at, cross_folder_moves, selection_id) VALUES (?, ?, ?, ?, ?, ?)",
        (version.plan_version_id, version.predecessor_id, version.state,
         version.created_at, int(version.cross_folder_moves), version.selection_id),
    )
    row = conn.execute("SELECT * FROM plan_versions").fetchone()
    assert row["cross_folder_moves"] == 0
    assert row["selection_id"] == "sel_1"
```

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p10/test_p10_records.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'tree_design.records'`.

- [ ] **Step 3: Write the records**

```python
# src/tree_design/records.py
"""P10's frozen records. Construction is where a malformed tree is refused.

Two invariants live here rather than in a validator, because a record that can
be built wrong is a record that will be stored wrong:

1. `accepts_placement` is derived and then checked against the stored value.
   P11 reads one flag (resolution B6); the derivation stays visible so the flag
   cannot drift from the rule that produced it.
2. No field but `existing_path` may hold a path separator. `existing_path` is an
   observed fact about the corpus (§5.10); every other location is `root_anchor`
   plus the ancestor label chain, which P12 composes.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from tree_design.vocabulary import (
    EXISTING,
    HANDLING_CLASSES,
    IGNORED,
    NODE_ROLES,
    NODE_TYPES,
    PROPOSED,
    PROTECTED,
    REFINEMENT_DISPOSITIONS,
    RESIDUAL,
    RESIDUAL_DISPOSITIONS,
    SHARED_MATERIAL_POLICIES,
    USER_CREATED,
    check,
)

_SEPARATORS = frozenset({"/", "\\", os.sep, os.altsep or "/"})


class MalformedTreeRecord(ValueError):
    """A record that cannot be built is a tree that cannot be stored wrong."""


def _require(value: object, *, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MalformedTreeRecord(f"{name} is required and cannot be empty")
    return value


def _no_separator(value: str, *, name: str) -> str:
    if any(sep in value for sep in _SEPARATORS):
        raise MalformedTreeRecord(
            f"{name} holds a path separator. P10 publishes root_anchor plus the "
            "ancestor label chain; P12 composes the path and applies §8.3's "
            "case-sensitivity, Unicode and length rules (resolution B3)."
        )
    return value


def derive_accepts_placement(node_type: str, *,
                             protected_movement_permitted: bool) -> bool:
    """The §5.12/§5.10/§8.4 rule, in one place.

    `ignored` is false because §5.10 guarantees a user may leave an existing
    folder untouched. `protected` is true only under an explicit user policy,
    because §8.4 says protected material "should not be moved automatically
    without a user policy that explicitly permits it".
    """
    check(node_type, NODE_TYPES, name="node_type")
    if node_type == IGNORED:
        return False
    if node_type == PROTECTED:
        return bool(protected_movement_permitted)
    return True


@dataclass(frozen=True)
class ExpectedValue:
    """One `field = value` assertion a level makes (§6.1)."""

    field: str
    value: str

    def __post_init__(self) -> None:
        _require(self.field, name="ExpectedValue.field")
        _require(self.value, name="ExpectedValue.value")


@dataclass(frozen=True)
class TemplateContext:
    """Which branch-local composition, and which level of it, produced a node.

    Exact versions are pinned so no library update can retroactively alter a
    frozen tree (§8.8, "Template versions and ordering choices").
    """

    binding_id: str
    template_id: str
    template_version: int
    dimension_index: int
    fragment_id: str | None = None
    fragment_version: int | None = None

    def __post_init__(self) -> None:
        for name in ("binding_id", "template_id"):
            _require(getattr(self, name), name=f"TemplateContext.{name}")
        for name in ("template_version", "dimension_index"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise MalformedTreeRecord(
                    f"TemplateContext.{name} is a non-negative integer version")
        if (self.fragment_id is None) != (self.fragment_version is None):
            raise MalformedTreeRecord(
                "a fragment reference is an id AND an exact version; half a "
                "reference cannot identify what supplied this level"
            )


@dataclass(frozen=True)
class Node:
    """§5.12's node, with §6.1's and §8.8's additions.

    `origin_node_id` exists because SPEC open question 5 is open: whether a
    `node_id` is stable across plan versions or minted per version is unsettled,
    and it decides whether a pending move survives a tree edit (§8.3). P10 mints
    per version and records the lineage, so neither answer needs a migration and
    no code depends on cross-version identity until the question is closed.
    """

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

    def __post_init__(self) -> None:
        for name in ("node_id", "plan_version_id", "root_anchor", "origin_node_id"):
            _require(getattr(self, name), name=f"Node.{name}")
        check(self.node_type, NODE_TYPES, name="node_type")
        check(self.node_role, NODE_ROLES, name="node_role")
        check(self.handling_class, HANDLING_CLASSES, name="handling_class")
        _no_separator(_require(self.display_label, name="Node.display_label"),
                      name="Node.display_label")
        if not isinstance(self.ordinal, int) or isinstance(self.ordinal, bool):
            raise MalformedTreeRecord("Node.ordinal is the sibling order, an integer")
        if not self.explanation or not self.explanation.strip():
            raise MalformedTreeRecord(
                "every node states the facts or accepted groups that caused it to "
                "appear (§5.12); an unexplained node is one the user cannot judge"
            )
        object.__setattr__(self, "associated_group_ids",
                           tuple(self.associated_group_ids))
        object.__setattr__(self, "expected_values", tuple(self.expected_values))

        derived = derive_accepts_placement(
            self.node_type,
            protected_movement_permitted=self.protected_movement_permitted,
        )
        if bool(self.accepts_placement) is not derived:
            raise MalformedTreeRecord(
                f"accepts_placement={self.accepts_placement!r} contradicts the "
                f"derivation for node_type={self.node_type!r}, which is {derived!r}. "
                "P11 reads the flag and re-derives nothing, so a flag that "
                "disagrees with the rule is a destination nobody chose."
            )

        if self.existing_path is not None and self.node_type != EXISTING:
            raise MalformedTreeRecord(
                "existing_path is present only on an `existing` node; it is an "
                "observed fact about the corpus, never a composition"
            )
        if self.node_role == RESIDUAL:
            check(self.disposition, RESIDUAL_DISPOSITIONS, name="disposition")
        elif self.disposition is not None:
            raise MalformedTreeRecord(
                "disposition is meaningless on a role other than `residual`")
        if self.refinement_disposition is not None:
            check(self.refinement_disposition, REFINEMENT_DISPOSITIONS,
                  name="refinement_disposition")
            if not (self.refinement_reason or "").strip():
                raise MalformedTreeRecord(
                    "a refinement disposition without a reason cannot tell an "
                    "intentionally shallow branch from an unfinished one (§5.8)"
                )
        elif self.refinement_reason is not None:
            raise MalformedTreeRecord(
                "a refinement reason belongs to a refinement disposition")
        if (self.dimension_role is None) != (self.dimension is None):
            raise MalformedTreeRecord(
                "a level realising a semantic role also records the live P6 field "
                "that role resolved to, and vice versa (C2)"
            )


@dataclass(frozen=True)
class SharedMaterialPolicy:
    """§6.9's policy for a file that belongs in two places.

    Without one recorded, §6.9 requires P11 to abstain on a transcript belonging
    to two application packets rather than pick a university.
    """

    policy_id: str
    plan_version_id: str
    policy: str
    policy_scope: str | None
    reason: str

    def __post_init__(self) -> None:
        for name in ("policy_id", "plan_version_id", "reason"):
            _require(getattr(self, name), name=f"SharedMaterialPolicy.{name}")
        check(self.policy, SHARED_MATERIAL_POLICIES, name="policy")


@dataclass(frozen=True)
class PlanVersion:
    """§8.8's plan version. `cross_folder_moves` is P3's value, stored by P10.

    P3 records the user's §1.1 choice; P10 stores it in the freeze record under
    "Placement policy settings"; P12 enforces it at mutation time. Three parts,
    one value, and the reason it is stored here is that P12 reads a frozen plan,
    not a scan selection.
    """

    plan_version_id: str
    predecessor_id: str | None
    state: str
    created_at: str
    cross_folder_moves: bool
    selection_id: str

    def __post_init__(self) -> None:
        for name in ("plan_version_id", "state", "created_at", "selection_id"):
            _require(getattr(self, name), name=f"PlanVersion.{name}")
        if self.state not in ("draft", "frozen", "superseded"):
            raise MalformedTreeRecord(
                f"plan version state {self.state!r} is not draft, frozen or "
                "superseded; a frozen version is immutable and an edit opens a "
                "draft (§8.8)"
            )
        if not isinstance(self.cross_folder_moves, bool):
            raise MalformedTreeRecord(
                "cross_folder_moves is P3's boolean permission, carried verbatim")
```

- [ ] **Step 4: Write the schema**

```python
# src/tree_design/schema.py
"""P10's own SQLite tables, inside P1's single database. Idempotent and additive.

`plan_version_id` appears on tree state and on branch bindings, and NOWHERE on
the shared template library. A fragment, a definition and an applicability row
are release-keyed records shared across plans; copying them per version would
make a library update look like a tree edit and would let two versions of one
recipe drift apart silently.

No column here holds a composed filesystem path. `nodes.existing_path` is the one
observed path, and it is an observation about the corpus, not a destination.
"""
from __future__ import annotations

import sqlite3

#: Every table P10 owns. The first four are tree state; the rest arrive with the
#: tasks that need them and are listed here so one module names the whole set.
P10_TABLES: tuple[str, ...] = (
    "plan_versions",
    "tree_nodes",
    "shared_material_policies",
    "node_expected_values",
)

TREE_DDL = """
CREATE TABLE IF NOT EXISTS plan_versions (
    plan_version_id     TEXT PRIMARY KEY,
    predecessor_id      TEXT REFERENCES plan_versions (plan_version_id),
    state               TEXT NOT NULL CHECK (state IN ('draft','frozen','superseded')),
    created_at          TEXT NOT NULL,
    -- §1.1, recorded by P3 as `cross_folder_moves`, stored here under §8.8's
    -- "Placement policy settings", enforced by P12 at mutation time.
    cross_folder_moves  INTEGER NOT NULL CHECK (cross_folder_moves IN (0, 1)),
    selection_id        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tree_nodes (
    node_id                      TEXT NOT NULL,
    plan_version_id              TEXT NOT NULL
                                 REFERENCES plan_versions (plan_version_id),
    -- Minted per version; `origin_node_id` carries the lineage. SPEC open
    -- question 5 decides whether these ever become the same value.
    origin_node_id               TEXT NOT NULL,
    node_type                    TEXT NOT NULL,
    display_label                TEXT NOT NULL,
    parent_node_id               TEXT,
    root_anchor                  TEXT NOT NULL,
    ordinal                      INTEGER NOT NULL,
    associated_group_ids         TEXT NOT NULL,   -- canonical JSON
    explanation                  TEXT NOT NULL,
    node_role                    TEXT NOT NULL,
    accepts_placement            INTEGER NOT NULL CHECK (accepts_placement IN (0, 1)),
    protected_movement_permitted INTEGER NOT NULL DEFAULT 0,
    handling_class               TEXT NOT NULL,
    template_context             TEXT,            -- canonical JSON or NULL
    dimension_role               TEXT,
    dimension                    TEXT,
    existing_path                TEXT,            -- only when node_type='existing'
    disposition                  TEXT,            -- only when node_role='residual'
    refinement_disposition       TEXT,
    refinement_reason            TEXT,
    PRIMARY KEY (plan_version_id, node_id),
    CHECK (existing_path IS NULL OR node_type = 'existing'),
    CHECK ((disposition IS NULL) = (node_role <> 'residual')),
    CHECK ((refinement_disposition IS NULL) = (refinement_reason IS NULL)),
    CHECK ((dimension_role IS NULL) = (dimension IS NULL))
);

CREATE INDEX IF NOT EXISTS tree_nodes_parent
    ON tree_nodes (plan_version_id, parent_node_id, ordinal);

CREATE INDEX IF NOT EXISTS tree_nodes_legal
    ON tree_nodes (plan_version_id, accepts_placement);

CREATE INDEX IF NOT EXISTS tree_nodes_lineage
    ON tree_nodes (origin_node_id);

CREATE TABLE IF NOT EXISTS node_expected_values (
    plan_version_id TEXT NOT NULL,
    node_id         TEXT NOT NULL,
    field_key       TEXT NOT NULL,
    value           TEXT NOT NULL,
    PRIMARY KEY (plan_version_id, node_id, field_key, value),
    FOREIGN KEY (plan_version_id, node_id)
        REFERENCES tree_nodes (plan_version_id, node_id)
);

CREATE TABLE IF NOT EXISTS shared_material_policies (
    policy_id       TEXT PRIMARY KEY,
    plan_version_id TEXT NOT NULL REFERENCES plan_versions (plan_version_id),
    policy          TEXT NOT NULL,
    -- NULL means tree-global. SPEC open question 9 is open; the column answers
    -- it per record instead of forcing one reading into the schema.
    policy_scope    TEXT,
    reason          TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS one_global_shared_material_policy
    ON shared_material_policies (plan_version_id)
    WHERE policy_scope IS NULL;
"""


def create_tree_schema(conn: sqlite3.Connection) -> None:
    """Create every P10-owned table. Idempotent; touches no P1 table."""
    conn.executescript(TREE_DDL)
```

- [ ] **Step 5: Run and verify GREEN**

Run: `python3.12 -m pytest -q tests/p10/test_p10_records.py tests/p10/test_p10_vocabulary.py`

Expected: PASS. The vocabulary guard now has a second module to walk, so it is doing real work from here on.

- [ ] **Step 6: Commit**

```bash
git add src/tree_design/records.py src/tree_design/schema.py tests/p10/test_p10_records.py
git commit -m "feat(p10): add frozen node records and the P10 schema"
```

### Task 3: Read every limit; choose none

**Files:**
- Create: `src/tree_design/config.py`
- Create: `tests/p10/test_p10_config.py`

**Interfaces:**

*Consumes:* `database_agent.budget.get_ceiling(conn, key)`.

*Produces:*

```python
class ConfigurationRequired(RuntimeError): ...

@dataclass(frozen=True)
class TreeLimits:
    max_folder_proposals_and_depth: int
    max_dossier_tokens: int
    excessive_depth_warning: int
    tiny_folder_max_files: int
    tiny_folder_count_warning: int
    materially_improves_retrieval: Callable[[object], bool | None]

def tree_limits(conn: sqlite3.Connection, *, excessive_depth_warning: int,
                tiny_folder_max_files: int, tiny_folder_count_warning: int,
                materially_improves_retrieval: Callable[[object], bool | None],
                ) -> TreeLimits: ...
CEILINGS: dict[str, str]
```

**Done-means:** DM9 (thresholds read from configuration rather than hard-coded), and the enabling half of DM13's V3 fixture.

- [ ] **Step 1: Write the failing configuration tests**

```python
# tests/p10/test_p10_config.py
"""P10 Task 3 — every limit is read or injected; none is chosen here.

SPEC open questions 1 and 2 are open on purpose: §5.7 forbids exceeding
"practical depth limits" and §5.9 asks for a warning on "a large number of tiny
folders", and the design states no number for either. A default here would run a
user's corpus under a bound nobody chose, with nothing to say so.
"""
from __future__ import annotations

import pytest

from database_agent.budget import set_ceiling
from tree_design.config import CEILINGS, ConfigurationRequired, tree_limits

INJECTED = dict(
    excessive_depth_warning=6,
    tiny_folder_max_files=3,
    tiny_folder_count_warning=12,
    materially_improves_retrieval=lambda preview: None,
)


def test_the_two_ceilings_come_from_p1s_published_keys(conn):
    set_ceiling(conn, "tree.max_folder_proposals_and_depth", 9)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    limits = tree_limits(conn, **INJECTED)
    assert limits.max_folder_proposals_and_depth == 9
    assert limits.max_dossier_tokens == 4000
    assert set(CEILINGS.values()) == {
        "tree.max_folder_proposals_and_depth", "model.max_dossier_tokens_per_call",
    }


def test_an_absent_ceiling_refuses_rather_than_defaulting(conn):
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    with pytest.raises(ConfigurationRequired) as excinfo:
        tree_limits(conn, **INJECTED)
    assert "tree.max_folder_proposals_and_depth" in str(excinfo.value)


def test_a_non_positive_ceiling_is_refused(conn):
    set_ceiling(conn, "tree.max_folder_proposals_and_depth", 0)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    with pytest.raises(ConfigurationRequired):
        tree_limits(conn, **INJECTED)


def test_every_59_threshold_is_mandatory_and_has_no_default(conn):
    set_ceiling(conn, "tree.max_folder_proposals_and_depth", 9)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    for missing in ("excessive_depth_warning", "tiny_folder_max_files",
                    "tiny_folder_count_warning"):
        supplied = {**INJECTED, missing: None}
        with pytest.raises(ConfigurationRequired) as excinfo:
            tree_limits(conn, **supplied)
        assert missing in str(excinfo.value)


def test_the_retrieval_gain_test_is_injected_and_may_answer_unknown(conn):
    """§5.9 wants a flattening recommendation "when a dimension does not
    materially improve retrieval" and states no test. `None` is the honest
    answer until one is authored, and it must not round to False."""
    set_ceiling(conn, "tree.max_folder_proposals_and_depth", 9)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    with pytest.raises(ConfigurationRequired):
        tree_limits(conn, **{**INJECTED, "materially_improves_retrieval": None})
    limits = tree_limits(conn, **INJECTED)
    assert limits.materially_improves_retrieval(object()) is None


def test_no_module_in_the_package_holds_a_numeric_literal_beyond_zero_and_one():
    """P9's precedent, applied to P10: a threshold in source is a policy an
    author chose. Introspection, not text search — a text search matches
    comments and docstrings and has produced a false result nine times here."""
    import ast
    from pathlib import Path

    src = Path(__file__).resolve().parents[2] / "src" / "tree_design"
    offenders = []
    for path in sorted(src.glob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant):
                continue
            if isinstance(node.value, bool) or not isinstance(node.value, int):
                continue
            if node.value in (0, 1):
                continue
            offenders.append(f"{path.name}:{node.lineno} {node.value}")
    assert offenders == []
```

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p10/test_p10_config.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'tree_design.config'`.

- [ ] **Step 3: Write the configuration reader**

```python
# src/tree_design/config.py
"""P10's limits, read from P1 or injected by the caller. No number lives here.

§8.6's configurable list contains one ceiling that is P10's outright — "Maximum
folder proposals and maximum depth" — and P1 publishes it as ONE key,
`tree.max_folder_proposals_and_depth`. §8.6 describes two numbers; P1 stores one.
P10 reads what P1 publishes and uses the single value for both the proposal
ceiling and the depth ceiling. Splitting it is a change to `database_agent.budget`
and to §8.6, not a P10 default, and this comment is where a reader finds that out.

The §5.9 thresholds have no ceiling key at all, so they are mandatory injected
arguments. Same rule, different mechanism: absent means refuse, never guess.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass

from database_agent.budget import get_ceiling


class ConfigurationRequired(RuntimeError):
    """A limit P10 needs is absent or non-positive. Never a default."""


#: The two live P1 ceiling keys P10 reads. `CEILING_KEYS` in
#: `database_agent.budget` is the authority for the spellings.
CEILINGS: dict[str, str] = {
    "max_folder_proposals_and_depth": "tree.max_folder_proposals_and_depth",
    "max_dossier_tokens": "model.max_dossier_tokens_per_call",
}


@dataclass(frozen=True)
class TreeLimits:
    max_folder_proposals_and_depth: int
    max_dossier_tokens: int
    excessive_depth_warning: int
    tiny_folder_max_files: int
    tiny_folder_count_warning: int
    #: Returns True, False, or None for "no authored test decides this yet".
    #: None must never round to False: a flattening recommendation the product
    #: cannot justify is worse than none.
    materially_improves_retrieval: Callable[[object], bool | None]


def _positive(value: object, *, source: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ConfigurationRequired(
            f"{source} is {value!r}; P10 needs a positive limit and ships no "
            "fallback. §5.7 and §5.9 deliberately state no number, so a default "
            "here would be P10 authoring the design."
        )
    return value


def tree_limits(
    conn: sqlite3.Connection,
    *,
    excessive_depth_warning: int,
    tiny_folder_max_files: int,
    tiny_folder_count_warning: int,
    materially_improves_retrieval: Callable[[object], bool | None],
) -> TreeLimits:
    """P10's limits for this database. Every one is read or injected."""
    read = {
        name: _positive(get_ceiling(conn, key), source=key)
        for name, key in CEILINGS.items()
    }
    if not callable(materially_improves_retrieval):
        raise ConfigurationRequired(
            "materially_improves_retrieval is the §5.9 test for whether a "
            "dimension earns its level. The design states none, so the caller "
            "supplies one; a built-in test would be an invented threshold."
        )
    return TreeLimits(
        **read,
        excessive_depth_warning=_positive(
            excessive_depth_warning, source="excessive_depth_warning"),
        tiny_folder_max_files=_positive(
            tiny_folder_max_files, source="tiny_folder_max_files"),
        tiny_folder_count_warning=_positive(
            tiny_folder_count_warning, source="tiny_folder_count_warning"),
        materially_improves_retrieval=materially_improves_retrieval,
    )
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3.12 -m pytest -q tests/p10/test_p10_config.py`

Expected: PASS, six tests. `test_no_module_in_the_package_holds_a_numeric_literal_beyond_zero_and_one` is the guard that keeps every later task honest and must not be relaxed for convenience.

- [ ] **Step 5: Commit**

```bash
git add src/tree_design/config.py tests/p10/test_p10_config.py
git commit -m "feat(p10): read tree limits from configuration"
```

### Task 4: Read upstream parts by their live names

**Files:**
- Create: `src/tree_design/upstream.py`
- Create: `tests/p10/p9_fixtures.py`
- Create: `tests/p10/test_p10_upstream.py`

**Interfaces:**

*Consumes:* `grouping.records.Group` / `Membership` / `GroupAcceptance`, `grouping.vocabulary.MEMBERSHIP_BASES` / `EXCLUDED` / `ACCEPTED` / `REJECTED`, `facts.fields.get_field(conn, field_key)`, `facts.read_surface.is_destination_eligible(conn, *, field_key)`, `scan_agent.selection.selection_candidate_roots(conn, selection_id)` / `get_selection(conn, selection_id)`, `scan_agent.inventory.directory_inventory(conn, scan_run_id)` / `CURATION_SIGNAL_VALUES`, `privacy.classification_store.ClassificationStore(conn).current(file_id, content_hash)`.

*Produces:*

```python
class UpstreamUnavailable(RuntimeError): ...

@dataclass(frozen=True)
class AcceptedGroup:
    group_id: str
    label: str
    domain: str | None
    members: tuple[GroupMember, ...]
    anchor_facts: tuple[str, ...]
    excluded_members: tuple[str, ...]

@dataclass(frozen=True)
class GroupMember:
    file_id: str
    content_hash: str
    basis: str

@dataclass(frozen=True)
class ExistingFolder:
    directory_path: str
    parent_directory: str | None
    file_count: int
    curation_signal: str

class AcceptedGroupReader(Protocol):
    def accepted(self, plan_version_id: str) -> Sequence[object]: ...
    def group(self, group_id: str) -> object: ...
    def memberships(self, group_id: str) -> Sequence[object]: ...

def accepted_groups(reader: AcceptedGroupReader, *,
                    plan_version_id: str) -> tuple[AcceptedGroup, ...]: ...
def rejected_group_ids(reader: AcceptedGroupReader, *,
                       plan_version_id: str) -> frozenset[str]: ...
def resolve_role_to_field(conn: sqlite3.Connection, *, role_ref: str,
                          field_ref: str) -> str: ...
def existing_folders(conn: sqlite3.Connection, *,
                     scan_run_id: str) -> tuple[ExistingFolder, ...]: ...
def candidate_roots(conn: sqlite3.Connection, *,
                    selection_id: str) -> tuple[str, ...]: ...
def cross_folder_moves(conn: sqlite3.Connection, *, selection_id: str) -> bool: ...
def handling_class_for(store, *, file_id: str, content_hash: str) -> str: ...
```

**Done-means:** the input half of DM2, DM5 and DM14. This is the only module in `src/tree_design/` permitted to name another part's symbols.

- [ ] **Step 1: Write the P9 fixture over LIVE records**

`tests/p10/p9_fixtures.py`:

```python
# tests/p10/p9_fixtures.py
"""Accepted P9 groups, built from P9's LIVE records. Tests only.

`grouping.store` does not exist yet, so P10 cannot ask P9 for accepted groups.
What it can do is refuse to invent their shape: every object here is a real
`grouping.records` instance, so the day P9 publishes a reader this fixture is
replaced and nothing about the shape changes.

Three names in P10's SPEC do not exist in P9's live code and are corrected here:
the user-approved label is `GroupAcceptance.user_edited_label` falling back to
`Group.display_label`, the membership axis is `Membership.basis`, and rejection
is `GroupAcceptance.acceptance`, never `Group.state`.
"""
from __future__ import annotations

from grouping.records import AnchorFact, Group, GroupAcceptance, Membership
from grouping.vocabulary import (
    ACCEPTED,
    COHERENT,
    CONTEXT_SUPPORTED,
    DIRECT_ANCHOR,
    ENGINE,
    EXCLUDED,
    INCLUDED,
    NOT_FLAGGED,
    REJECTED,
    RULES,
    STRONGLY_IDENTIFIED_FILE,
    USER,
    USER_ACCEPTED,
    VALIDATED_SHARED_FACT,
)

T0 = "2026-08-27T00:00:00Z"


def _group(group_id: str, label: str, category: str, seed_kind: str) -> Group:
    return Group(
        group_id=group_id, seed_ref=f"seed_{group_id}", seed_kind=seed_kind,
        proposed_basis="two validated shared facts across five files",
        anchor_facts=(AnchorFact(
            fact_id=f"fact_{group_id}", field_key="subject", value="PHYS1401",
            reliability_state="validated", observation_key=f"obs_{group_id}",
        ),),
        pre_model_signals={}, anchor_count=1, coherence_verdict=COHERENT,
        coherence_citations=(f"obs_{group_id}",), group_category=category,
        display_label=label, label_source=ENGINE, conflicts=(),
        stop_rule_hits=(), state="supported", sensitivity_state="personal_non_sensitive",
        dossier_id=None, llm_response_ref=None, validation_verdict_ref=None,
        created_by=RULES, created_at=T0,
    )


def _membership(group_id: str, file_id: str, basis: str, decision: str) -> Membership:
    return Membership(
        membership_id=f"m_{group_id}_{file_id}", group_id=group_id, file_id=file_id,
        content_hash=f"h_{file_id}", basis=basis, decision=decision,
        decision_source=RULES, support=(), insufficient_evidence=False,
        insufficiency_statement=None, conflicts=(), outlier_flag=NOT_FLAGGED,
    )


def _acceptance(group_id: str, plan_version_id: str, acceptance: str,
                label: str | None) -> GroupAcceptance:
    return GroupAcceptance(
        acceptance_id=f"acc_{group_id}", plan_version_id=plan_version_id,
        group_id=group_id, membership_id=None, acceptance=acceptance,
        review_state=USER_ACCEPTED, user_edited_label=label, aliases=(),
        review_decision_ref=None, decided_by=USER, created_at=T0,
    )


class FixtureGroupReader:
    """Satisfies `upstream.AcceptedGroupReader` with recorded live records."""

    def __init__(self, plan_version_id: str = "plan_1") -> None:
        self.plan_version_id = plan_version_id
        self._groups = {
            "g_phys1401": _group(
                "g_phys1401", "PHYS 1401", "academic", VALIDATED_SHARED_FACT),
            "g_columbia_app": _group(
                "g_columbia_app", "Columbia application",
                "college_applications", STRONGLY_IDENTIFIED_FILE),
            "g_random": _group(
                "g_random", "Screenshots from March", "photos",
                STRONGLY_IDENTIFIED_FILE),
        }
        self._memberships = {
            "g_phys1401": (
                _membership("g_phys1401", "lecture-08", DIRECT_ANCHOR, INCLUDED),
                _membership("g_phys1401", "hw-3", CONTEXT_SUPPORTED, INCLUDED),
                _membership("g_phys1401", "duke-essay", DIRECT_ANCHOR, EXCLUDED),
            ),
            "g_columbia_app": (
                # The same transcript is a legal member of two accepted groups
                # (§4.9); the tree must not force it to one branch.
                _membership("g_columbia_app", "transcript", DIRECT_ANCHOR, INCLUDED),
            ),
            "g_random": (
                _membership("g_random", "shot-1", DIRECT_ANCHOR, INCLUDED),
            ),
        }
        self._acceptances = (
            _acceptance("g_phys1401", plan_version_id, ACCEPTED, "PHYS 1401 course"),
            _acceptance("g_columbia_app", plan_version_id, ACCEPTED, None),
            _acceptance("g_random", plan_version_id, REJECTED, None),
        )

    def accepted(self, plan_version_id: str):
        return tuple(
            a for a in self._acceptances if a.plan_version_id == plan_version_id
        )

    def group(self, group_id: str):
        return self._groups[group_id]

    def memberships(self, group_id: str):
        return self._memberships[group_id]
```

- [ ] **Step 2: Write the failing upstream tests**

```python
# tests/p10/test_p10_upstream.py
"""P10 Task 4 — the one module allowed to name another part's symbols.

Everything else in `src/tree_design/` reads P10 records. Concentrating the seam
here means a rename upstream breaks one module with a clear error, rather than
seven modules with seven different ones.
"""
from __future__ import annotations

import pytest

from database_agent.db import open_database
from p9_fixtures import FixtureGroupReader
from scan_agent.selection import record_selection
from tree_design.upstream import (
    UpstreamUnavailable,
    accepted_groups,
    candidate_roots,
    cross_folder_moves,
    handling_class_for,
    rejected_group_ids,
    resolve_role_to_field,
)
from tree_design.vocabulary import CONTEXT_SUPPORTED, DIRECT_ANCHOR


def test_the_user_approved_label_is_the_acceptances_edit_then_the_groups_label():
    reader = FixtureGroupReader()
    groups = {g.group_id: g for g in accepted_groups(reader, plan_version_id="plan_1")}
    # `GroupAcceptance.user_edited_label` wins where the user set one.
    assert groups["g_phys1401"].label == "PHYS 1401 course"
    # Otherwise `Group.display_label`. P10's SPEC calls this field `label`; P9
    # has no such field, and reading one would raise AttributeError at runtime.
    assert groups["g_columbia_app"].label == "Columbia application"


def test_the_domain_is_p9s_group_category_and_p10_requests_no_second_field():
    reader = FixtureGroupReader()
    groups = {g.group_id: g for g in accepted_groups(reader, plan_version_id="plan_1")}
    assert groups["g_phys1401"].domain == "academic"
    assert groups["g_columbia_app"].domain == "college_applications"


def test_membership_basis_is_p9s_axis_and_carries_all_three_values():
    reader = FixtureGroupReader()
    groups = {g.group_id: g for g in accepted_groups(reader, plan_version_id="plan_1")}
    bases = {m.file_id: m.basis for m in groups["g_phys1401"].members}
    assert bases == {"lecture-08": DIRECT_ANCHOR, "hw-3": CONTEXT_SUPPORTED}


def test_excluded_members_are_derived_not_requested():
    reader = FixtureGroupReader()
    groups = {g.group_id: g for g in accepted_groups(reader, plan_version_id="plan_1")}
    assert groups["g_phys1401"].excluded_members == ("duke-essay",)
    assert "duke-essay" not in {m.file_id for m in groups["g_phys1401"].members}


def test_rejection_is_resolved_from_acceptance_never_from_group_state():
    """P10's SPEC derives rejected proposals from `Group.state = rejected`. That
    value cannot exist: `grouping.records.Group.__post_init__` checks `state`
    against `GROUP_STATES`, which is (candidate, supported, tentative-discovery,
    unresolved), and `grouping/vocabulary.py:20` says `rejected` is "never stored
    on a group"."""
    reader = FixtureGroupReader()
    assert rejected_group_ids(reader, plan_version_id="plan_1") == frozenset({"g_random"})
    assert "g_random" not in {
        g.group_id for g in accepted_groups(reader, plan_version_id="plan_1")
    }


def test_a_file_may_belong_to_two_accepted_groups():
    """§4.9. The tree must not force a group to a single branch to make
    membership single-valued."""
    reader = FixtureGroupReader()
    groups = accepted_groups(reader, plan_version_id="plan_1")
    homes = [g.group_id for g in groups
             if any(m.file_id == "transcript" for m in g.members)]
    assert homes == ["g_columbia_app"]
    # And the reader imposes no uniqueness that would prevent a second home.
    assert accepted_groups(reader, plan_version_id="plan_1") == groups


def test_a_role_resolves_only_to_a_live_destination_eligible_p6_field(conn):
    assert resolve_role_to_field(conn, role_ref="subject", field_ref="subject") == "subject"
    with pytest.raises(UpstreamUnavailable) as excinfo:
        resolve_role_to_field(conn, role_ref="artifact_kind", field_ref="not_a_field")
    assert "not_a_field" in str(excinfo.value)
    assert "P6" in str(excinfo.value)


def test_a_role_may_not_mint_a_field(conn):
    """§3.12: the system "should not invent new fields automatically". A template
    references fields P6 already defines; a semantic role is an organization-layer
    slot, not a new fact."""
    with pytest.raises(UpstreamUnavailable):
        resolve_role_to_field(conn, role_ref="vibe", field_ref="vibe")


def test_the_cross_folder_permission_and_roots_come_from_p3(tmp_path):
    conn = open_database(tmp_path / "agent.sqlite")
    selection_id = record_selection(
        conn, sources=[tmp_path / "corpus"],
        candidate_roots=[tmp_path / "corpus" / "Documents"],
        cross_folder_moves=False, selected_by="jy")
    assert cross_folder_moves(conn, selection_id=selection_id) is False
    assert candidate_roots(conn, selection_id=selection_id) == (
        str(tmp_path / "corpus" / "Documents"),
    )
    conn.close()


def test_an_unclassified_file_reads_as_the_gate_outcome_and_is_never_written(conn):
    """D2: `Unreadable or unclassified` is a gate outcome, not a file fact. P7's
    store refuses to write it, so P10 must map an absent record to it for
    display without ever handing it back to P7."""
    from privacy.classification_store import ClassificationStore

    store = ClassificationStore(conn)
    assert handling_class_for(
        store, file_id="never-seen", content_hash="h") == "unreadable_unclassified"
```

- [ ] **Step 3: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p10/test_p10_upstream.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'tree_design.upstream'`. If it instead fails on `import p9_fixtures`, add `tests/p10` to `pytest`'s `rootdir` path the way `tests/p9` does — the fixture module is a sibling import, not a package import.

- [ ] **Step 4: Write the upstream adapters**

```python
# src/tree_design/upstream.py
"""The only module in P10 that names another part's symbols.

Concentrating the seam here has one purpose: when P9 publishes its reader, or P7
adds a handling class, or P3 renames a column, exactly one module breaks and the
error says which upstream name moved. Seven modules importing seven upstream
names produce seven unrelated failures and one long afternoon.

Three of P10's SPEC field names do not exist upstream, and the live name wins:

* the user-approved label is `GroupAcceptance.user_edited_label`, falling back to
  `Group.display_label`; there is no `Group.label`.
* the membership axis is `Membership.basis` over `MEMBERSHIP_BASES`; there is no
  `membership_kind`.
* rejection is `GroupAcceptance.acceptance`, resolved as of a plan version.
  `Group.state = rejected` is impossible — the record checks `state` against
  `GROUP_STATES`, which does not contain it.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from facts.fields import get_field
from facts.read_surface import is_destination_eligible
from grouping.vocabulary import ACCEPTED, EXCLUDED, INCLUDED, MEMBERSHIP_BASES, REJECTED
from scan_agent.inventory import CURATION_SIGNAL_VALUES, directory_inventory
from scan_agent.selection import get_selection, selection_candidate_roots
from tree_design.vocabulary import HANDLING_CLASSES, check

#: D2: absent is a gate outcome, not a file fact. P7's store refuses to write it,
#: so P10 renders it and never hands it back.
UNCLASSIFIED = "unreadable_unclassified"


class UpstreamUnavailable(RuntimeError):
    """An upstream value P10 needs is missing, ineligible, or not P6's."""


@dataclass(frozen=True)
class GroupMember:
    file_id: str
    content_hash: str
    basis: str


@dataclass(frozen=True)
class AcceptedGroup:
    """P10's view of one accepted P9 group, in P10's field names.

    `domain` is P9's `group_category` (resolution M12): domain and category are
    one field, not two, so P10 requests no separate `domain`.
    """

    group_id: str
    label: str
    domain: str | None
    members: tuple[GroupMember, ...]
    anchor_facts: tuple[str, ...]
    excluded_members: tuple[str, ...]


@dataclass(frozen=True)
class ExistingFolder:
    directory_path: str
    parent_directory: str | None
    file_count: int
    curation_signal: str


class AcceptedGroupReader(Protocol):
    """What P10 needs from P9. `grouping.store` will satisfy this unchanged."""

    def accepted(self, plan_version_id: str) -> Sequence[object]: ...
    def group(self, group_id: str) -> object: ...
    def memberships(self, group_id: str) -> Sequence[object]: ...


def _label(acceptance: object, group: object) -> str:
    edited = getattr(acceptance, "user_edited_label", None)
    if edited:
        return edited
    display = getattr(group, "display_label", None)
    if not display:
        raise UpstreamUnavailable(
            f"group {getattr(group, 'group_id', '?')!r} carries no label. P9 sets "
            "`display_label` only when `coherence_verdict` is 'coherent', so an "
            "unlabelled accepted group is a real state and a branch cannot be "
            "named from it."
        )
    return display


def accepted_groups(reader: AcceptedGroupReader, *,
                    plan_version_id: str) -> tuple[AcceptedGroup, ...]:
    """Every group this plan version accepted, with its members and exclusions."""
    result = []
    for acceptance in reader.accepted(plan_version_id):
        if acceptance.acceptance != ACCEPTED:
            continue
        group = reader.group(acceptance.group_id)
        memberships = reader.memberships(acceptance.group_id)
        members = []
        excluded = []
        for membership in memberships:
            check(membership.basis, MEMBERSHIP_BASES, name="membership.basis")
            if membership.decision == INCLUDED:
                members.append(GroupMember(
                    file_id=membership.file_id,
                    content_hash=membership.content_hash,
                    basis=membership.basis,
                ))
            elif membership.decision == EXCLUDED:
                excluded.append(membership.file_id)
        result.append(AcceptedGroup(
            group_id=group.group_id,
            label=_label(acceptance, group),
            domain=group.group_category,
            members=tuple(members),
            anchor_facts=tuple(f.fact_id for f in group.anchor_facts),
            excluded_members=tuple(excluded),
        ))
    return tuple(result)


def rejected_group_ids(reader: AcceptedGroupReader, *,
                       plan_version_id: str) -> frozenset[str]:
    """§4.9 and §8.7: a rejected proposal must not resurface as a candidate."""
    return frozenset(
        acceptance.group_id
        for acceptance in reader.accepted(plan_version_id)
        if acceptance.acceptance == REJECTED
    )


def resolve_role_to_field(conn: sqlite3.Connection, *, role_ref: str,
                          field_ref: str) -> str:
    """C2: an organization-layer role resolves to a LIVE, destination-eligible
    P6 field, or the composition fails closed.

    §3.12 forbids inventing a field, and §5.7 asks templates to "use existing
    field types wherever possible". A role that resolves to nothing is a
    configuration gap, never a new fact.
    """
    try:
        row = get_field(conn, field_ref)
    except Exception as exc:  # P6 raises its own lookup error
        raise UpstreamUnavailable(
            f"role {role_ref!r} maps to {field_ref!r}, which P6's field catalogue "
            "does not define. A template may not mint a field (§3.12)."
        ) from exc
    if row is None:
        raise UpstreamUnavailable(
            f"role {role_ref!r} maps to {field_ref!r}, which P6's field catalogue "
            "does not define. A template may not mint a field (§3.12)."
        )
    if not is_destination_eligible(conn, field_key=field_ref):
        raise UpstreamUnavailable(
            f"role {role_ref!r} maps to {field_ref!r}, which P6 marks not "
            "destination-eligible. §3.8 keeps an authoring role out of the tree; "
            "it is supporting evidence, not a folder level."
        )
    return field_ref


def existing_folders(conn: sqlite3.Connection, *,
                     scan_run_id: str) -> tuple[ExistingFolder, ...]:
    """§5.10's inventory, with P3's curation signal carried verbatim.

    `CURATION_SIGNAL_VALUES` is THREE values, not §5.10's two: P3 publishes
    `undetermined` and today returns it for every directory, because §1.1 gives
    one worked case and no threshold. P10 renders it and never rounds it to
    `incidental` — §8.6 requires leaving something in review rather than guessing.
    """
    folders = []
    for row in directory_inventory(conn, scan_run_id):
        signal = row["curation_signal"]
        if signal not in CURATION_SIGNAL_VALUES:
            raise UpstreamUnavailable(
                f"curation signal {signal!r} is not one of P3's "
                f"{CURATION_SIGNAL_VALUES}; P10 renders this signal and derives "
                "none of it (resolution G9)"
            )
        folders.append(ExistingFolder(
            directory_path=row["directory_path"],
            parent_directory=row["parent_directory"],
            file_count=row["file_count"],
            curation_signal=signal,
        ))
    return tuple(folders)


def candidate_roots(conn: sqlite3.Connection, *,
                    selection_id: str) -> tuple[str, ...]:
    """§1.1's high-level locations. Every node's `root_anchor` names one."""
    return tuple(str(path) for path in selection_candidate_roots(conn, selection_id))


def cross_folder_moves(conn: sqlite3.Connection, *, selection_id: str) -> bool:
    """§1.1's "whether files may move across high-level folders".

    P3 records it, P10 stores it in the freeze record under §8.8's placement
    policy settings, P12 enforces it at mutation time. P10 neither derives nor
    overrides it.
    """
    row = get_selection(conn, selection_id)
    if row is None:
        raise UpstreamUnavailable(
            f"corpus selection {selection_id!r} does not exist; §1.1's roots and "
            "movement permission are the user's choices and P10 supplies neither"
        )
    return bool(row["cross_folder_moves"])


def handling_class_for(store, *, file_id: str, content_hash: str) -> str:
    """P7's class for one file version, carried, never re-derived (§8.4).

    An absent record reads as the gate outcome. P10 does not classify: §5.2 and
    §8.4 make sensitivity an evidence-backed, user-revisable class that P7 owns.
    """
    record = store.current(file_id, content_hash)
    if record is None:
        return UNCLASSIFIED
    return check(record.handling_class, HANDLING_CLASSES, name="handling_class")
```

- [ ] **Step 5: Run and verify GREEN**

Run: `python3.12 -m pytest -q tests/p10/test_p10_upstream.py`

Expected: PASS, ten tests. If `test_a_role_resolves_only_to_a_live_destination_eligible_p6_field` fails on `subject`, confirm the seeded catalogue with `python3 -c "import sqlite3"`-free introspection: `PYTHONPATH=src python3 -c "import inspect; from facts.read_surface import is_destination_eligible; print(inspect.signature(is_destination_eligible))"`. Plan against the live signature, never a reconstructed one.

- [ ] **Step 6: Commit**

```bash
git add src/tree_design/upstream.py tests/p10/p9_fixtures.py tests/p10/test_p10_upstream.py
git commit -m "feat(p10): read P9, P6, P3 and P7 through one named seam"
```

### Task 5: Append the two §8.2 events and read §8.7's rejections

**Files:**
- Create: `src/tree_design/provenance.py`
- Create: `tests/p10/test_p10_provenance.py`

**Interfaces:**

*Consumes:* `database_agent.events.append_event(conn, **fields)`, `database_agent.learning.learning_records(conn, scope, subject_id)`, `evidence_shape.canonical.canonical_json`.

*Produces:*

```python
SUBSYSTEM: str            # "P10", spelled in exactly one place
PROPOSAL_CLASS_BRANCH: str
ROOT_SUBJECT: str

def record_tree_edit(conn, *, action: str, node_id: str, plan_version_id: str,
                     before: object, after: object, explanation: str,
                     observed_at: str, user_id: str,
                     correction_scope: str, correction_subject: str,
                     polarity: str, basis_key: str | None = None,
                     component_version: str) -> int: ...

def record_template_application(conn, *, node_id: str, plan_version_id: str,
                                template_id: str, template_version: int,
                                binding_id: str, explanation: str,
                                observed_at: str, user_id: str,
                                component_version: str,
                                model_identifier: str | None = None,
                                prompt_fingerprint: str | None = None) -> int: ...

def record_plan_version_adoption(conn, *, plan_version_id: str, action: str,
                                 explanation: str, observed_at: str,
                                 user_id: str, component_version: str) -> int: ...

def branch_basis_key(*, parent_node_id: str | None, dimension_or_label: str) -> str: ...

def suppressed_branch_basis_keys(conn, *,
                                 parent_node_id: str | None) -> frozenset[str]: ...
```

**Done-means:** the §8.2 and §8.7 halves of DM5 and DM6, and the precondition for DM17's version history.

- [ ] **Step 1: Write the failing provenance tests**

```python
# tests/p10/test_p10_provenance.py
"""P10 Task 5 — the two events P10 appends, and the rejections it must honour.

`template application` and `destination-tree edit` are §8.2 reserved names that
have had no producer since P1 shipped. A reserved name with no writer is this
project's named defect class: the column exists, the audit reads it, and it is
always empty. This task is the writer.

The §8.7 read is the other half. §8.7: "Rejected groups, rejected destination
matches, rejected labels, and rejected residual recommendations must be stored
with the evidence that produced them. Otherwise the system will repeatedly
resurface the same attractive but incorrect grouping."
"""
from __future__ import annotations

import json

import pytest

from database_agent.events import MalformedEvent, UnregisteredEventType
from database_agent.learning import reset_preferences
from tree_design.provenance import (
    PROPOSAL_CLASS_BRANCH,
    SUBSYSTEM,
    branch_basis_key,
    record_plan_version_adoption,
    record_template_application,
    record_tree_edit,
    suppressed_branch_basis_keys,
)
from tree_design.vocabulary import (
    DESTINATION_TREE_EDIT,
    RENAME,
    TEMPLATE_APPLICATION,
)

T0 = "2026-08-27T00:00:00Z"
COMMON = dict(observed_at=T0, user_id="jy", component_version="p10-1")


def _events(conn, event_type):
    return conn.execute(
        "SELECT * FROM events WHERE event_type = ? ORDER BY event_id",
        (event_type,)).fetchall()


def test_a_tree_edit_appends_82s_reserved_name_with_before_and_after(conn):
    record_tree_edit(
        conn, action=RENAME, node_id="n_1", plan_version_id="plan_1",
        before={"display_label": "Uni"}, after={"display_label": "Academics"},
        explanation="User renamed the branch to their own vocabulary.",
        correction_scope="node", correction_subject="n_1", polarity="accept",
        **COMMON)
    row = _events(conn, DESTINATION_TREE_EDIT)[0]
    assert row["subsystem"] == SUBSYSTEM == "P10"
    payload = json.loads(row["explanation"].split("\n", 1)[1])
    assert payload["action"] == RENAME
    assert payload["before"] == {"display_label": "Uni"}
    assert payload["after"] == {"display_label": "Academics"}
    assert row["correction_scope"] == "node"
    assert row["correction_subject"] == "n_1"


def test_an_edit_with_no_explanation_is_refused_by_p1(conn):
    with pytest.raises(MalformedEvent):
        record_tree_edit(
            conn, action=RENAME, node_id="n_1", plan_version_id="plan_1",
            before={}, after={}, explanation="",
            correction_scope="node", correction_subject="n_1", polarity="accept",
            **COMMON)


def test_an_action_outside_the_tree_edit_set_never_reaches_p1(conn):
    with pytest.raises(Exception):
        record_tree_edit(
            conn, action="reticulate", node_id="n_1", plan_version_id="plan_1",
            before={}, after={}, explanation="x",
            correction_scope="node", correction_subject="n_1", polarity="accept",
            **COMMON)
    assert _events(conn, DESTINATION_TREE_EDIT) == []


def test_a_template_application_carries_template_id_and_exact_version(conn):
    record_template_application(
        conn, node_id="n_1", plan_version_id="plan_1",
        template_id="academic-coursework", template_version=1,
        binding_id="btb_1",
        explanation="Applied the academic coursework recipe to this branch.",
        **COMMON)
    row = _events(conn, TEMPLATE_APPLICATION)[0]
    payload = json.loads(row["explanation"].split("\n", 1)[1])
    assert payload["template_id"] == "academic-coursework"
    assert payload["template_version"] == 1
    assert payload["binding_id"] == "btb_1"
    assert row["prompt_fingerprint"] is None


def test_an_llm_generated_template_additionally_carries_model_and_fingerprint(conn):
    """§8.2 and §3.4. Without both, two runs at different model versions look
    identical to replay, which is a silent wrong answer."""
    record_template_application(
        conn, node_id="n_1", plan_version_id="plan_1",
        template_id="custom-1", template_version=1, binding_id="btb_2",
        explanation="Applied a model-proposed recipe after user approval.",
        model_identifier="fixture-model", prompt_fingerprint="fp-canonical",
        **COMMON)
    row = _events(conn, TEMPLATE_APPLICATION)[0]
    assert row["prompt_fingerprint"] == "fp-canonical"
    payload = json.loads(row["explanation"].split("\n", 1)[1])
    assert payload["model_identifier"] == "fixture-model"


def test_a_model_generated_template_without_a_fingerprint_is_refused(conn):
    with pytest.raises(ValueError):
        record_template_application(
            conn, node_id="n_1", plan_version_id="plan_1",
            template_id="custom-1", template_version=1, binding_id="btb_2",
            explanation="x", model_identifier="fixture-model", **COMMON)


def test_freeze_appends_a_plan_version_adoption_record(conn):
    event_id = record_plan_version_adoption(
        conn, plan_version_id="plan_1", action="adopt_version",
        explanation="User froze the tree.", **COMMON)
    row = conn.execute(
        "SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
    assert row["event_type"] == DESTINATION_TREE_EDIT
    assert row["correction_scope"] == "corpus"
    assert row["correction_subject"] == "plan_1"


def test_a_rejected_branch_is_suppressed_by_parent_and_label(conn):
    """§8.7 and 10-i4-learning-ops: before proposing a branch candidate, P10
    queries `learning_records` for `proposal_class = branch` and
    `basis_key = (parent_node_id, dimension_or_label)`."""
    key = branch_basis_key(parent_node_id=None, dimension_or_label="Math Stuff")
    record_tree_edit(
        conn, action="delete-suggested-area", node_id="n_math",
        plan_version_id="plan_1", before={"display_label": "Math Stuff"},
        after={}, explanation="User deleted the suggested Math Stuff area.",
        correction_scope="node", correction_subject="__root__",
        polarity="reject", basis_key=key,
        **{**COMMON, "component_version": "p10-1"})
    assert suppressed_branch_basis_keys(conn, parent_node_id=None) == frozenset({key})
    other = branch_basis_key(parent_node_id="n_academics",
                             dimension_or_label="Math Stuff")
    assert suppressed_branch_basis_keys(conn, parent_node_id="n_academics") == frozenset()
    assert other != key


def test_an_accepted_branch_is_not_suppressed(conn):
    key = branch_basis_key(parent_node_id=None, dimension_or_label="Academics")
    record_tree_edit(
        conn, action="accept", node_id="n_academics", plan_version_id="plan_1",
        before={}, after={"display_label": "Academics"},
        explanation="User accepted the Academics branch.",
        correction_scope="node", correction_subject="__root__",
        polarity="accept", basis_key=key, **COMMON)
    assert suppressed_branch_basis_keys(conn, parent_node_id=None) == frozenset()


def test_a_reset_lifts_the_suppression_without_deleting_the_record(conn):
    """§8.7: learned preferences are inspectable and resettable, and R6 keeps
    every record. A reset is a cutoff, not a delete."""
    key = branch_basis_key(parent_node_id=None, dimension_or_label="Math Stuff")
    record_tree_edit(
        conn, action="delete-suggested-area", node_id="n_math",
        plan_version_id="plan_1", before={"display_label": "Math Stuff"},
        after={}, explanation="User deleted the suggested Math Stuff area.",
        correction_scope="node", correction_subject="__root__",
        polarity="reject", basis_key=key, **COMMON)
    assert suppressed_branch_basis_keys(conn, parent_node_id=None) == frozenset({key})
    reset_preferences(conn, "node", "__root__", author="P13",
                      component_version="p13-1", user_id="jy")
    assert suppressed_branch_basis_keys(conn, parent_node_id=None) == frozenset()
    surviving = conn.execute(
        "SELECT count(*) AS n FROM events WHERE basis_key = ?", (key,)).fetchone()
    assert surviving["n"] == 1


def test_p10_appends_no_event_type_it_does_not_own(conn):
    with pytest.raises(UnregisteredEventType):
        from database_agent.events import append_event
        append_event(conn, event_type="tree freeze", subsystem=SUBSYSTEM,
                     component_version="p10-1", observed_at=T0,
                     explanation="not a reserved name")
```

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p10/test_p10_provenance.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'tree_design.provenance'`.

- [ ] **Step 3: Write the provenance module**

```python
# src/tree_design/provenance.py
"""P10's §8.2 writers and its §8.7 reader.

§8.2's literal list contains two names that are P10's: `template application` and
`destination-tree edit`. Both have been reserved in `database_agent.events` since
P1 shipped and neither has had a producer. This module is the producer, and it is
the ONLY place in P10 that appends an event.

The structured payload rides in `explanation`, after a human sentence and a
newline. §8.2 requires "the acting user, the time, the node identifier, the
before and after state, and the evidence reference or user intent behind it", and
P1's event columns hold five of those; the rest is canonical JSON so replay reads
one form per value. P1 stores it opaquely and interprets none of it, which is the
same discipline P1 applies to `polarity`, `proposal_class` and `basis_key`.
"""
from __future__ import annotations

import sqlite3

from database_agent.events import append_event
from database_agent.learning import learning_records
from evidence_shape.canonical import canonical_json
from tree_design.vocabulary import (
    CORRECTION_SCOPES,
    DESTINATION_TREE_EDIT,
    TEMPLATE_APPLICATION,
    TREE_EDIT_ACTIONS,
    VERSION_ACTIONS,
    check,
)

#: §8.2's "responsible subsystem". Spelled in exactly one place, as P6's brief
#: requires of every part, so a rename is one edit and not a grep.
SUBSYSTEM: str = "P10"

#: §8.7's opaque `proposal_class` for a branch candidate. P1 stores it and
#: interprets nothing; the suppression rule is P10's, applied in P10.
PROPOSAL_CLASS_BRANCH: str = "branch"

#: A top-level branch has no parent, and `correction_subject` cannot be NULL when
#: `correction_subject` is required beside a scope. The root gets a name rather
#: than an empty string, because an empty subject would collide with every other
#: absent subject in the log.
ROOT_SUBJECT: str = "__root__"

POLARITIES: tuple[str, ...] = ("accept", "reject")


def _explanation(sentence: str, payload: dict) -> str:
    if not sentence or not sentence.strip():
        raise ValueError(
            "every P10 event states in prose what the user did; §8.2 requires a "
            "structured explanation and a payload alone is not one"
        )
    return f"{sentence}\n{canonical_json(payload)}"


def record_tree_edit(conn: sqlite3.Connection, *, action: str, node_id: str,
                     plan_version_id: str, before: object, after: object,
                     explanation: str, observed_at: str, user_id: str,
                     correction_scope: str, correction_subject: str,
                     polarity: str, component_version: str,
                     basis_key: str | None = None) -> int:
    """One `destination-tree edit`. Every canvas action that alters the draft.

    §8.2 requires the before and after node state, so a rename keeps its prior
    label and a deleted candidate keeps the evidence that produced it — which is
    exactly what §8.7's no-resurfacing rule reads back.
    """
    check(action, TREE_EDIT_ACTIONS, name="tree edit action")
    check(correction_scope, CORRECTION_SCOPES, name="correction_scope")
    check(polarity, POLARITIES, name="polarity")
    payload = {
        "action": action,
        "node_id": node_id,
        "plan_version_id": plan_version_id,
        "before": before,
        "after": after,
    }
    return append_event(
        conn,
        event_type=DESTINATION_TREE_EDIT,
        subsystem=SUBSYSTEM,
        component_version=component_version,
        observed_at=observed_at,
        explanation=_explanation(explanation, payload),
        user_id=user_id,
        correction_scope=correction_scope,
        correction_subject=correction_subject,
        polarity=polarity,
        proposal_class=PROPOSAL_CLASS_BRANCH,
        basis_key=basis_key,
    )


def record_template_application(conn: sqlite3.Connection, *, node_id: str,
                                plan_version_id: str, template_id: str,
                                template_version: int, binding_id: str,
                                explanation: str, observed_at: str,
                                user_id: str, component_version: str,
                                model_identifier: str | None = None,
                                prompt_fingerprint: str | None = None) -> int:
    """One `template application`, carrying the exact template id and version.

    §8.2 and §3.4: a model-generated template additionally carries the model
    version and the prompt fingerprint. Without both, two runs under different
    prompts look identical to §8.5's replay, and a regression has no cause.
    """
    if model_identifier is not None and not prompt_fingerprint:
        raise ValueError(
            "a model-generated template application records the model version "
            "AND the prompt fingerprint (§8.2, §3.4); one without the other "
            "makes a replay divergence unattributable"
        )
    payload = {
        "node_id": node_id,
        "plan_version_id": plan_version_id,
        "template_id": template_id,
        "template_version": template_version,
        "binding_id": binding_id,
        "model_identifier": model_identifier,
    }
    return append_event(
        conn,
        event_type=TEMPLATE_APPLICATION,
        subsystem=SUBSYSTEM,
        component_version=component_version,
        observed_at=observed_at,
        explanation=_explanation(explanation, payload),
        user_id=user_id,
        prompt_fingerprint=prompt_fingerprint,
        correction_scope="template",
        correction_subject=template_id,
        polarity="accept",
        proposal_class="template",
    )


def record_plan_version_adoption(conn: sqlite3.Connection, *,
                                 plan_version_id: str, action: str,
                                 explanation: str, observed_at: str,
                                 user_id: str, component_version: str) -> int:
    """§8.8's adoption record, appended at freeze and at every restore.

    P1 reserves no separate name for it, and coining one would be P10 registering
    an event type outside its SPEC. It is a `destination-tree edit` whose subject
    is the plan version rather than a node, at corpus scope.
    """
    check(action, VERSION_ACTIONS, name="version action")
    payload = {"plan_version_id": plan_version_id, "action": action}
    return append_event(
        conn,
        event_type=DESTINATION_TREE_EDIT,
        subsystem=SUBSYSTEM,
        component_version=component_version,
        observed_at=observed_at,
        explanation=_explanation(explanation, payload),
        user_id=user_id,
        correction_scope="corpus",
        correction_subject=plan_version_id,
        polarity="accept",
        proposal_class="plan_version",
    )


def branch_basis_key(*, parent_node_id: str | None,
                     dimension_or_label: str) -> str:
    """§8.7's `basis_key` for a branch proposal: (parent, dimension or label).

    The parent is part of the key because rejecting `General` under one course
    says nothing about `General` under another. A key that dropped the parent
    would turn one local correction into a corpus-wide ban.
    """
    return canonical_json([parent_node_id, dimension_or_label])


def suppressed_branch_basis_keys(conn: sqlite3.Connection, *,
                                 parent_node_id: str | None) -> frozenset[str]:
    """The branch proposals this user has already rejected under this parent.

    §8.7: "Otherwise the system will repeatedly resurface the same attractive but
    incorrect grouping." `learning_records` honours a reset as a cutoff and
    deletes nothing (R6), so a reset lifts the suppression while the record and
    the evidence behind it survive.
    """
    subject = ROOT_SUBJECT if parent_node_id is None else parent_node_id
    return frozenset(
        row["basis_key"]
        for row in learning_records(conn, "node", subject)
        if row["proposal_class"] == PROPOSAL_CLASS_BRANCH
        and row["polarity"] == "reject"
        and row["basis_key"]
    )
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3.12 -m pytest -q tests/p10/test_p10_provenance.py tests/test_events.py tests/test_learning.py`

Expected: PASS. P1's own event and learning suites are included because this task is the first P10 code to write into P1's tables, and a P10 write that breaks a P1 invariant must fail here rather than at integration.

- [ ] **Step 5: Commit**

```bash
git add src/tree_design/provenance.py tests/p10/test_p10_provenance.py
git commit -m "feat(p10): append tree-edit and template-application events"
```

### Task 6: Four template records and the packaged catalogue

**Files:**
- Create: `src/tree_design/templates.py`
- Create: `src/tree_design/catalogue.py`
- Create: `tests/p10/test_p10_templates.py`

**Interfaces:**

*Consumes:* `tree_design.vocabulary` (`ORIGIN_KINDS`, `SCOPE_KINDS`, `PUBLICATION_STATES`, `BINDING_STATES`, `DIMENSION_ACTIONS`, `DIMENSION_REQUIREMENTS`, `REFINEMENT_DISPOSITIONS`, `check`), `tree_design.config.ConfigurationRequired`, `evidence_shape.canonical.canonical_json`.

*Produces:*

```python
class MalformedTemplateRecord(ValueError): ...
class CompositionConflict(RuntimeError):
    gate: str
    conflicting: tuple[str, ...]
    choices: tuple[str, ...]

@dataclass(frozen=True)
class FragmentRef:      fragment_id: str; fragment_version: int
@dataclass(frozen=True)
class ApplicabilityRef: applicability_id: str; applicability_version: int
@dataclass(frozen=True)
class PurposeProfileRef: purpose_profile_id: str; purpose_profile_version: int
@dataclass(frozen=True)
class TemplateFragment: ...
@dataclass(frozen=True)
class TemplateDimension: ...
@dataclass(frozen=True)
class TemplateDefinition: ...
@dataclass(frozen=True)
class RoleBinding:      role_ref: str; field_ref: str
@dataclass(frozen=True)
class TemplateApplicability: ...
@dataclass(frozen=True)
class ResolvedDimension: ...
@dataclass(frozen=True)
class BranchTemplateBinding: ...

@dataclass(frozen=True)
class TemplateCatalogue:
    release_id: str
    fragments: Mapping[tuple[str, int], TemplateFragment]
    definitions: Mapping[tuple[str, int], TemplateDefinition]
    applicabilities: Mapping[tuple[str, int], TemplateApplicability]
    def fragment(self, ref: FragmentRef) -> TemplateFragment: ...
    def has_fragment(self, fragment_id: str, fragment_version: int) -> bool: ...

def load_catalogue(read_manifest: Callable[[], str]) -> TemplateCatalogue: ...
def resolve_fragment_imports(catalogue, ref: FragmentRef) -> tuple[TemplateFragment, ...]: ...
def merge_fragment_constraints(fragments, *,
                               privacy_rank: Callable[[str], int]) -> MergedConstraints: ...
```

**Done-means:** DM1 (all four template records round-trip), and the identity half of DM13's C1 and the isolation half of DM16.

- [ ] **Step 1: Write the failing template-record tests**

```python
# tests/p10/test_p10_templates.py
"""P10 Task 6 — four records that must not collapse into one.

The composable-template design is explicit: "P10 must not collapse these objects
into a single 'template' row." A fragment is reusable organization logic with no
values and no field mappings. A definition composes exact fragment versions. An
applicability row maps roles to live P6 fields for exactly ONE `uses_schema`. A
branch binding records what one branch in one draft actually chose.

Applicability is never nested inside a definition, because nesting is what turns
"one recipe, two domains" into two copies that drift.
"""
from __future__ import annotations

import dataclasses
import json

import pytest

from tree_design.catalogue import load_catalogue
from tree_design.templates import (
    ApplicabilityRef,
    BranchTemplateBinding,
    CompositionConflict,
    FragmentRef,
    MalformedTemplateRecord,
    PurposeProfileRef,
    ResolvedDimension,
    RoleBinding,
    TemplateApplicability,
    TemplateDefinition,
    TemplateDimension,
    TemplateFragment,
    merge_fragment_constraints,
    resolve_fragment_imports,
)
from tree_design.vocabulary import (
    ACTION_ADDED,
    ACTION_RENAMED,
    ACTION_SELECTED,
    BUILT_IN,
    CROSS_DOMAIN,
    DOMAIN_FOCUSED,
    OPTIONAL,
    PUBLICATION_DRAFT,
    PUBLISHED,
    REFINED,
    REQUIRED,
    WORKFLOW_APPROVED,
    WORKFLOW_DRAFT,
)

ARTIFACT_KIND = TemplateFragment(
    fragment_id="artifact-kind", fragment_version=1, roles=("artifact_kind",),
    relative_order=(), imports=(), optional_roles=(), metadata_only_roles=(),
    allowed_values={}, privacy_floor="policy.public", provenance=("row:academic-01",),
)
SUBJECT_STAGE = TemplateFragment(
    fragment_id="subject-stage", fragment_version=1,
    roles=("subject", "lifecycle_stage"),
    relative_order=(("subject", "lifecycle_stage"),), imports=(),
    optional_roles=("lifecycle_stage",), metadata_only_roles=(),
    allowed_values={}, privacy_floor="policy.public", provenance=("row:research-02",),
)


def _catalogue(*extra):
    manifest = {
        "release_id": "rel-1",
        "fragments": [dataclasses.asdict(f) for f in (ARTIFACT_KIND, SUBJECT_STAGE, *extra)],
        "definitions": [],
        "applicabilities": [],
    }
    return load_catalogue(lambda: json.dumps(manifest))


def test_a_fragment_carries_no_user_value_and_no_field_mapping():
    with pytest.raises(TypeError):
        TemplateFragment(
            fragment_id="bad", fragment_version=1, roles=("subject",),
            relative_order=(), imports=(), optional_roles=(),
            metadata_only_roles=(), allowed_values={}, privacy_floor="policy.public",
            provenance=(), field_bindings=(("subject", "subject"),),
        )


def test_a_definition_pins_exact_fragment_versions_and_never_nests_applicability():
    definition = TemplateDefinition(
        template_id="academic-coursework", template_version=1,
        origin_kind=BUILT_IN, scope_kind=DOMAIN_FOCUSED,
        publication_state=PUBLISHED,
        fragment_refs=(FragmentRef("artifact-kind", 1),),
        dimensions=(TemplateDimension(
            role_ref="subject", order_index=0, requirement=REQUIRED,
            metadata_only=False,
            retrieval_rationale="The course is the level users search by.",
        ),),
        optional_branch_patterns=(), sensitivity_policy_ref="policy.public",
        validation_constraints=(),
        example_label_chains=(("Academics", "Columbia", "PHYS1401"),),
    )
    assert definition.fragment_refs[0].fragment_version == 1
    assert not hasattr(definition, "uses_schema")
    assert not hasattr(definition, "role_bindings")
    assert not hasattr(definition, "applicability")


def test_a_definition_may_not_carry_branch_specific_justification():
    """§5.7's `justification_fact_refs` belong to the validation report and the
    branch binding. In an immutable reusable definition they would be one
    branch's evidence presented as the recipe's own."""
    assert "justification_fact_refs" not in {
        f.name for f in dataclasses.fields(TemplateDefinition)
    }
    assert "justification_fact_refs" in {
        f.name for f in dataclasses.fields(BranchTemplateBinding)
    }


def test_an_example_label_chain_is_labels_and_never_a_path():
    with pytest.raises(MalformedTemplateRecord) as excinfo:
        TemplateDefinition(
            template_id="t", template_version=1, origin_kind=BUILT_IN,
            scope_kind=DOMAIN_FOCUSED, publication_state=PUBLISHED,
            fragment_refs=(), dimensions=(), optional_branch_patterns=(),
            sensitivity_policy_ref="policy.public", validation_constraints=(),
            example_label_chains=(("Academics/Columbia",),),
        )
    assert "separator" in str(excinfo.value)


def test_an_applicability_row_names_exactly_one_schema_and_carries_provenance():
    row = TemplateApplicability(
        applicability_id="academic-coursework--academic", applicability_version=1,
        template_id="academic-coursework", template_version=1,
        uses_schema="academic", purpose_profile_ref=None,
        allowed_fields=("subject", "work_type"),
        detection_signal_refs=("signal.syllabus_header",),
        role_bindings=(RoleBinding("subject", "subject"),
                       RoleBinding("artifact_kind", "work_type")),
        exclusions=(), provenance=("row:academic-01", "memo:academic-reuse"),
    )
    assert row.uses_schema == "academic"
    assert row.provenance
    with pytest.raises(MalformedTemplateRecord):
        dataclasses.replace(row, uses_schema="")
    with pytest.raises(MalformedTemplateRecord) as excinfo:
        dataclasses.replace(row, provenance=())
    assert "provenance" in str(excinfo.value)


def test_a_role_binding_must_target_a_field_the_row_allows():
    with pytest.raises(MalformedTemplateRecord):
        TemplateApplicability(
            applicability_id="a", applicability_version=1, template_id="t",
            template_version=1, uses_schema="academic", purpose_profile_ref=None,
            allowed_fields=("subject",), detection_signal_refs=(),
            role_bindings=(RoleBinding("artifact_kind", "work_type"),),
            exclusions=(), provenance=("row:x",),
        )


def test_a_purpose_profile_ref_is_authored_and_versioned():
    """It is neither P6's Applications-only `purpose` field nor a runtime P9
    group id, and it creates no universal purpose taxonomy."""
    ref = PurposeProfileRef(purpose_profile_id="pp.grad-application",
                            purpose_profile_version=1)
    row = TemplateApplicability(
        applicability_id="a", applicability_version=1, template_id="t",
        template_version=1, uses_schema="college_applications",
        purpose_profile_ref=ref, allowed_fields=("target_school",),
        detection_signal_refs=(), role_bindings=(RoleBinding("counterpart", "target_school"),),
        exclusions=(), provenance=("row:apps-01",),
    )
    assert row.purpose_profile_ref.purpose_profile_version == 1
    with pytest.raises(MalformedTemplateRecord):
        dataclasses.replace(row, purpose_profile_ref="g_columbia_app")


def test_a_branch_binding_records_all_six_dimension_actions():
    binding = BranchTemplateBinding(
        binding_id="btb_1", plan_version_id="plan_1", branch_node_id="n_academics",
        applicability_refs=(ApplicabilityRef("academic-coursework--academic", 1),),
        resolved_dimensions=(
            ResolvedDimension(role_ref="subject", field_ref="subject",
                              action=ACTION_SELECTED, order_index=0,
                              display_label=None),
            ResolvedDimension(role_ref="artifact_kind", field_ref="work_type",
                              action=ACTION_RENAMED, order_index=1,
                              display_label="Assignments"),
            ResolvedDimension(role_ref="term", field_ref="term",
                              action=ACTION_ADDED, order_index=2,
                              display_label=None),
        ),
        accepted_group_ids=("g_phys1401",), state=WORKFLOW_APPROVED,
        depth_disposition=REFINED,
        refinement_reason="The accepted course groups justify the split.",
        validation_report_ref="vr_1", approval_action_ref="ra_1",
        justification_fact_refs=("fact_g_phys1401",),
    )
    assert {d.action for d in binding.resolved_dimensions} == {
        ACTION_SELECTED, ACTION_RENAMED, ACTION_ADDED,
    }


def test_an_approved_binding_requires_a_recorded_user_action():
    """C8 and §5.7: validity is not activation. A binding that reached
    `approved` without an approval action is a template that activated itself."""
    common = dict(
        binding_id="btb_1", plan_version_id="plan_1", branch_node_id="n_1",
        applicability_refs=(ApplicabilityRef("a", 1),), resolved_dimensions=(),
        accepted_group_ids=("g_1",), depth_disposition=REFINED,
        refinement_reason="reason", validation_report_ref="vr_1",
        justification_fact_refs=("f_1",),
    )
    with pytest.raises(MalformedTemplateRecord) as excinfo:
        BranchTemplateBinding(**common, state=WORKFLOW_APPROVED,
                              approval_action_ref=None)
    assert "approval" in str(excinfo.value)
    draft = BranchTemplateBinding(**common, state=WORKFLOW_DRAFT,
                                  approval_action_ref=None)
    assert draft.state == WORKFLOW_DRAFT


def test_fragment_imports_resolve_as_an_acyclic_exact_version_graph():
    composed = TemplateFragment(
        fragment_id="course-work", fragment_version=1, roles=("term",),
        relative_order=(("term", "artifact_kind"),),
        imports=(FragmentRef("artifact-kind", 1), FragmentRef("subject-stage", 1)),
        optional_roles=(), metadata_only_roles=(), allowed_values={},
        privacy_floor="policy.public", provenance=("row:academic-01",),
    )
    catalogue = _catalogue(composed)
    resolved = resolve_fragment_imports(catalogue, FragmentRef("course-work", 1))
    assert [f.fragment_id for f in resolved] == [
        "artifact-kind", "subject-stage", "course-work",
    ]


def test_a_cyclic_import_is_a_reported_conflict_not_a_recursion_error():
    left = dataclasses.replace(ARTIFACT_KIND, imports=(FragmentRef("subject-stage", 1),))
    right = dataclasses.replace(SUBJECT_STAGE, imports=(FragmentRef("artifact-kind", 1),))
    manifest = {
        "release_id": "rel-1",
        "fragments": [dataclasses.asdict(left), dataclasses.asdict(right)],
        "definitions": [], "applicabilities": [],
    }
    catalogue = load_catalogue(lambda: json.dumps(manifest))
    with pytest.raises(CompositionConflict) as excinfo:
        resolve_fragment_imports(catalogue, FragmentRef("artifact-kind", 1))
    assert excinfo.value.gate == "C1"
    assert "artifact-kind" in " ".join(excinfo.value.conflicting)


def test_an_unresolvable_fragment_version_fails_closed_at_c1():
    catalogue = _catalogue()
    with pytest.raises(CompositionConflict) as excinfo:
        resolve_fragment_imports(catalogue, FragmentRef("artifact-kind", 2))
    assert excinfo.value.gate == "C1"


def test_allowed_values_merge_by_intersection_and_an_empty_result_is_a_conflict():
    left = dataclasses.replace(
        ARTIFACT_KIND, allowed_values={"artifact_kind": ["Homework", "Exam"]})
    right = dataclasses.replace(
        ARTIFACT_KIND, fragment_id="artifact-kind-narrow",
        allowed_values={"artifact_kind": ["Exam"]})
    merged = merge_fragment_constraints(
        (left, right), privacy_rank=lambda ref: 0)
    assert merged.allowed_values["artifact_kind"] == ("Exam",)

    disjoint = dataclasses.replace(
        ARTIFACT_KIND, fragment_id="artifact-kind-other",
        allowed_values={"artifact_kind": ["Photo"]})
    with pytest.raises(CompositionConflict) as excinfo:
        merge_fragment_constraints((left, disjoint), privacy_rank=lambda ref: 0)
    assert excinfo.value.gate == "C5"
    assert "omit one fragment" in " ".join(excinfo.value.choices)


def test_privacy_merges_to_the_strongest_included_restriction():
    strict = dataclasses.replace(ARTIFACT_KIND, privacy_floor="policy.sensitive")
    rank = {"policy.public": 0, "policy.sensitive": 1}.__getitem__
    merged = merge_fragment_constraints((ARTIFACT_KIND, strict), privacy_rank=rank)
    assert merged.privacy_floor == "policy.sensitive"


def test_an_unrankable_privacy_ref_refuses_rather_than_guessing():
    """G-KNOWLEDGE. A privacy ordering P10 invented would silently pick a weaker
    floor than an included fragment requires, which is C7's whole failure mode."""
    from tree_design.config import ConfigurationRequired

    def rank(ref):
        raise KeyError(ref)

    with pytest.raises(ConfigurationRequired):
        merge_fragment_constraints((ARTIFACT_KIND,), privacy_rank=rank)


def test_the_catalogue_loads_through_an_injected_reader_and_scans_nothing():
    import ast
    from pathlib import Path

    source = (Path(__file__).resolve().parents[2]
              / "src" / "tree_design" / "catalogue.py").read_text()
    imported = {
        node.module for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert not any(name.startswith("planning") for name in imported)
    assert "pathlib" not in imported and "glob" not in imported
```

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p10/test_p10_templates.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'tree_design.templates'`.

- [ ] **Step 3: Write the template records**

```python
# src/tree_design/templates.py
"""The four template records, kept apart on purpose.

`TemplateFragment` is reusable organization logic: semantic roles, recommended
order, optionality, safety constraints, its own identity and version. It holds no
user value and no field mapping, and it creates no node.

`TemplateDefinition` composes exact fragment versions plus template-local
dimensions. P10 publishes no ambiguous generic `Template` record beside it.

`TemplateApplicability` maps roles to live P6 fields for exactly ONE
`uses_schema`. Several rows may reference one definition and one schema may have
several rows; that is the many-to-many seam, and it never widens a P6 allow-list
because every individual row still resolves against one schema.

`BranchTemplateBinding` is what one branch in one draft chose. Applying or
editing a recipe in one branch cannot change another branch that started from the
same definition, and a newer definition, fragment or applicability version is a
new candidate rather than an automatic migration.
"""
from __future__ import annotations

import os
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field

from tree_design.config import ConfigurationRequired
from tree_design.vocabulary import (
    BINDING_STATES,
    DIMENSION_ACTIONS,
    DIMENSION_REQUIREMENTS,
    ORIGIN_KINDS,
    PUBLICATION_STATES,
    REFINEMENT_DISPOSITIONS,
    SCOPE_KINDS,
    WORKFLOW_APPROVED,
    check,
)

_SEPARATORS = frozenset({"/", "\\", os.sep, os.altsep or "/"})


class MalformedTemplateRecord(ValueError):
    """A template record that cannot be built is one that cannot mislead."""


class CompositionConflict(RuntimeError):
    """A gate refused. The report names the inputs and the user's choices.

    Conflict handling is fail-closed and explanatory: the composable-template
    design fixes the offered choices as "omit one fragment, change the order,
    flatten a level, keep the branch shallow, or defer". There is no hidden
    precedence rule and no last-writer-wins.
    """

    CHOICES: tuple[str, ...] = (
        "omit one fragment",
        "change the order",
        "flatten a level",
        "keep the branch shallow",
        "defer",
    )

    def __init__(self, gate: str, conflicting: Sequence[str], detail: str) -> None:
        self.gate = gate
        self.conflicting = tuple(conflicting)
        self.choices = self.CHOICES
        super().__init__(
            f"{gate}: {detail}. Conflicting inputs: {', '.join(self.conflicting)}. "
            f"Available choices: {'; '.join(self.CHOICES)}."
        )


def _require(value: object, *, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MalformedTemplateRecord(f"{name} is required and cannot be empty")
    return value


def _version(value: object, *, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise MalformedTemplateRecord(
            f"{name} is an exact positive version. Reuse is by stable id and "
            "exact version, never by copied JSON and never by a range."
        )
    return value


@dataclass(frozen=True)
class FragmentRef:
    fragment_id: str
    fragment_version: int

    def __post_init__(self) -> None:
        _require(self.fragment_id, name="FragmentRef.fragment_id")
        _version(self.fragment_version, name="FragmentRef.fragment_version")

    def key(self) -> tuple[str, int]:
        return (self.fragment_id, self.fragment_version)


@dataclass(frozen=True)
class ApplicabilityRef:
    applicability_id: str
    applicability_version: int

    def __post_init__(self) -> None:
        _require(self.applicability_id, name="ApplicabilityRef.applicability_id")
        _version(self.applicability_version,
                 name="ApplicabilityRef.applicability_version")

    def key(self) -> tuple[str, int]:
        return (self.applicability_id, self.applicability_version)


@dataclass(frozen=True)
class PurposeProfileRef:
    purpose_profile_id: str
    purpose_profile_version: int

    def __post_init__(self) -> None:
        _require(self.purpose_profile_id, name="PurposeProfileRef.purpose_profile_id")
        _version(self.purpose_profile_version,
                 name="PurposeProfileRef.purpose_profile_version")


@dataclass(frozen=True)
class TemplateFragment:
    """A reusable organization recipe. No values, no field mappings, no nodes."""

    fragment_id: str
    fragment_version: int
    roles: tuple[str, ...]
    relative_order: tuple[tuple[str, str], ...]
    imports: tuple[FragmentRef, ...]
    optional_roles: tuple[str, ...]
    metadata_only_roles: tuple[str, ...]
    allowed_values: Mapping[str, Sequence[str]]
    privacy_floor: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        _require(self.fragment_id, name="TemplateFragment.fragment_id")
        _version(self.fragment_version, name="TemplateFragment.fragment_version")
        _require(self.privacy_floor, name="TemplateFragment.privacy_floor")
        if not self.roles:
            raise MalformedTemplateRecord(
                "a fragment with no semantic role organizes nothing")
        for name in ("roles", "relative_order", "imports", "optional_roles",
                     "metadata_only_roles", "provenance"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        object.__setattr__(self, "allowed_values",
                           {k: tuple(v) for k, v in dict(self.allowed_values).items()})
        unknown = set(self.optional_roles) | set(self.metadata_only_roles)
        stray = unknown - set(self.roles)
        if stray:
            raise MalformedTemplateRecord(
                f"{sorted(stray)} are marked optional or metadata-only but are not "
                "roles this fragment defines"
            )
        if not self.provenance:
            raise MalformedTemplateRecord(
                "a fragment records which reviewed contexts produced it; without "
                "provenance nobody can check that at least two independent "
                "contexts justified extracting it"
            )


@dataclass(frozen=True)
class TemplateDimension:
    role_ref: str
    order_index: int
    requirement: str
    metadata_only: bool
    retrieval_rationale: str

    def __post_init__(self) -> None:
        _require(self.role_ref, name="TemplateDimension.role_ref")
        check(self.requirement, DIMENSION_REQUIREMENTS, name="requirement")
        if not isinstance(self.order_index, int) or isinstance(self.order_index, bool):
            raise MalformedTemplateRecord("order_index is an integer position")
        _require(self.retrieval_rationale,
                 name="TemplateDimension.retrieval_rationale")


@dataclass(frozen=True)
class TemplateDefinition:
    template_id: str
    template_version: int
    origin_kind: str
    scope_kind: str
    publication_state: str
    fragment_refs: tuple[FragmentRef, ...]
    dimensions: tuple[TemplateDimension, ...]
    optional_branch_patterns: tuple[str, ...]
    sensitivity_policy_ref: str
    validation_constraints: tuple[str, ...]
    example_label_chains: tuple[tuple[str, ...], ...]

    def __post_init__(self) -> None:
        _require(self.template_id, name="TemplateDefinition.template_id")
        _version(self.template_version, name="TemplateDefinition.template_version")
        check(self.origin_kind, ORIGIN_KINDS, name="origin_kind")
        check(self.scope_kind, SCOPE_KINDS, name="scope_kind")
        check(self.publication_state, PUBLICATION_STATES, name="publication_state")
        _require(self.sensitivity_policy_ref,
                 name="TemplateDefinition.sensitivity_policy_ref")
        for name in ("fragment_refs", "dimensions", "optional_branch_patterns",
                     "validation_constraints"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        object.__setattr__(
            self, "example_label_chains",
            tuple(tuple(chain) for chain in self.example_label_chains))
        for chain in self.example_label_chains:
            for label in chain:
                if any(sep in label for sep in _SEPARATORS):
                    raise MalformedTemplateRecord(
                        f"example label {label!r} holds a path separator. Example "
                        "chains are nested display labels used to review a recipe; "
                        "they are not destinations and P12 alone composes paths."
                    )
        indices = [d.order_index for d in self.dimensions]
        if len(set(indices)) != len(indices):
            raise MalformedTemplateRecord(
                "two dimensions claim one order_index; the recommended order must "
                "be one order, even though the user may reverse or flatten it"
            )


@dataclass(frozen=True)
class RoleBinding:
    role_ref: str
    field_ref: str

    def __post_init__(self) -> None:
        _require(self.role_ref, name="RoleBinding.role_ref")
        _require(self.field_ref, name="RoleBinding.field_ref")


@dataclass(frozen=True)
class TemplateApplicability:
    """The join row. Exactly one `uses_schema`; provenance is mandatory.

    The composable-template design and the domain handoff both require every row
    to carry "provenance back to ratified domain rows and research evidence".
    P10's SPEC omits the field from its example JSON; it is required here,
    because a compiled row nobody can trace back to the domain research that
    justified it cannot be reviewed or retired.
    """

    applicability_id: str
    applicability_version: int
    template_id: str
    template_version: int
    uses_schema: str
    purpose_profile_ref: PurposeProfileRef | None
    allowed_fields: tuple[str, ...]
    detection_signal_refs: tuple[str, ...]
    role_bindings: tuple[RoleBinding, ...]
    exclusions: tuple[str, ...]
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        _require(self.applicability_id, name="TemplateApplicability.applicability_id")
        _version(self.applicability_version, name="applicability_version")
        _require(self.template_id, name="TemplateApplicability.template_id")
        _version(self.template_version, name="template_version")
        _require(self.uses_schema, name="TemplateApplicability.uses_schema")
        for name in ("allowed_fields", "detection_signal_refs", "role_bindings",
                     "exclusions", "provenance"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        if self.purpose_profile_ref is not None and not isinstance(
                self.purpose_profile_ref, PurposeProfileRef):
            raise MalformedTemplateRecord(
                "purpose_profile_ref is an authored, versioned identifier. It is "
                "not a P6 `purpose` value and not a runtime P9 group id; the "
                "branch binding pins the actual accepted groups and C3 proves the "
                "evidence match."
            )
        outside = [b.field_ref for b in self.role_bindings
                   if b.field_ref not in self.allowed_fields]
        if outside:
            raise MalformedTemplateRecord(
                f"role bindings target {sorted(outside)}, which this row does not "
                "allow. A row that binds outside its own allow-list is how reuse "
                "turns a per-schema fact allow-list into a cross-domain union."
            )
        if not self.provenance:
            raise MalformedTemplateRecord(
                "provenance back to the ratified domain rows and research evidence "
                "is required; a row with none cannot be reviewed or retired"
            )


@dataclass(frozen=True)
class ResolvedDimension:
    role_ref: str
    field_ref: str | None
    action: str
    order_index: int
    display_label: str | None

    def __post_init__(self) -> None:
        _require(self.role_ref, name="ResolvedDimension.role_ref")
        check(self.action, DIMENSION_ACTIONS, name="dimension action")
        if self.display_label is not None:
            if any(sep in self.display_label for sep in _SEPARATORS):
                raise MalformedTemplateRecord(
                    "a renamed level is a display label, never a path fragment")


@dataclass(frozen=True)
class BranchTemplateBinding:
    binding_id: str
    plan_version_id: str
    branch_node_id: str
    applicability_refs: tuple[ApplicabilityRef, ...]
    resolved_dimensions: tuple[ResolvedDimension, ...]
    accepted_group_ids: tuple[str, ...]
    state: str
    depth_disposition: str
    refinement_reason: str
    validation_report_ref: str
    approval_action_ref: str | None
    justification_fact_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in ("binding_id", "plan_version_id", "branch_node_id",
                     "refinement_reason", "validation_report_ref"):
            _require(getattr(self, name), name=f"BranchTemplateBinding.{name}")
        check(self.state, BINDING_STATES, name="binding state")
        check(self.depth_disposition, REFINEMENT_DISPOSITIONS,
              name="depth_disposition")
        for name in ("applicability_refs", "resolved_dimensions",
                     "accepted_group_ids", "justification_fact_refs"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        if not self.applicability_refs:
            raise MalformedTemplateRecord(
                "a binding names the exact applicability rows it resolved; without "
                "them the branch cannot say which recipe produced it"
            )
        if self.state == WORKFLOW_APPROVED and not self.approval_action_ref:
            raise MalformedTemplateRecord(
                "an approved binding names the recorded user approval. §5.7: a "
                "template does not "
                "become active merely because it is syntactically valid, so a "
                "binding that approved itself is the exact failure C8 prevents."
            )


@dataclass(frozen=True)
class MergedConstraints:
    roles: tuple[str, ...]
    relative_order: tuple[tuple[str, str], ...]
    optional_roles: frozenset[str]
    metadata_only_roles: frozenset[str]
    allowed_values: Mapping[str, tuple[str, ...]]
    privacy_floor: str


def _topological(nodes: Sequence[str],
                 edges: Sequence[tuple[str, str]]) -> list[str] | None:
    """Kahn's algorithm. Returns None when the graph has a cycle."""
    incoming = {node: 0 for node in nodes}
    outgoing: dict[str, list[str]] = {node: [] for node in nodes}
    for before, after in edges:
        if before not in incoming or after not in incoming:
            continue
        outgoing[before].append(after)
        incoming[after] += 1
    ready = [node for node in nodes if incoming[node] == 0]
    order: list[str] = []
    while ready:
        node = ready.pop(0)
        order.append(node)
        for nxt in outgoing[node]:
            incoming[nxt] -= 1
            if incoming[nxt] == 0:
                ready.append(nxt)
    return order if len(order) == len(nodes) else None


def resolve_fragment_imports(catalogue, ref: FragmentRef) -> tuple[TemplateFragment, ...]:
    """C1: every referenced fragment and exact version exists, and the import
    graph is acyclic. Imports come before the fragment that imports them."""
    resolved: list[TemplateFragment] = []
    seen: set[tuple[str, int]] = set()
    path: list[tuple[str, int]] = []

    def visit(current: FragmentRef) -> None:
        key = current.key()
        if key in path:
            cycle = [f"{fid}@{ver}" for fid, ver in (*path, key)]
            raise CompositionConflict(
                "C1", cycle, "fragment imports form a cycle")
        if key in seen:
            return
        if not catalogue.has_fragment(*key):
            raise CompositionConflict(
                "C1", [f"{key[0]}@{key[1]}"],
                "the packaged release does not contain this fragment version")
        fragment = catalogue.fragment(current)
        path.append(key)
        for imported in fragment.imports:
            visit(imported)
        path.pop()
        seen.add(key)
        resolved.append(fragment)

    visit(ref)
    return tuple(resolved)


def merge_fragment_constraints(
    fragments: Sequence[TemplateFragment],
    *,
    privacy_rank: Callable[[str], int],
) -> MergedConstraints:
    """Combine semantic constraints. Intersection, union, strongest — never
    last-writer-wins.

    Allowed-value sets narrow by intersection, because two fragments that both
    constrain a role both mean it. Relative order unions and is then checked for
    a cycle, because two compatible partial orders may still disagree. Privacy
    takes the strongest included restriction, because a composition that relaxed
    one fragment's floor would release material that fragment protects.
    """
    roles: list[str] = []
    edges: list[tuple[str, str]] = []
    optional: set[str] = set()
    metadata_only: set[str] = set()
    allowed: dict[str, tuple[str, ...]] = {}
    floors: list[str] = []

    for fragment in fragments:
        for role in fragment.roles:
            if role not in roles:
                roles.append(role)
        edges.extend(fragment.relative_order)
        metadata_only |= set(fragment.metadata_only_roles)
        floors.append(fragment.privacy_floor)
        for role, values in fragment.allowed_values.items():
            if role in allowed:
                narrowed = tuple(v for v in allowed[role] if v in set(values))
                if not narrowed:
                    raise CompositionConflict(
                        "C5", [role, *(f.fragment_id for f in fragments)],
                        f"the allowed values for {role!r} intersect to nothing")
                allowed[role] = narrowed
            else:
                allowed[role] = tuple(values)

    # A role is optional only where EVERY fragment that defines it says so. One
    # fragment requiring it is a requirement the composition must honour.
    for role in roles:
        definers = [f for f in fragments if role in f.roles]
        if definers and all(role in f.optional_roles for f in definers):
            optional.add(role)

    if _topological(roles, edges) is None:
        raise CompositionConflict(
            "C5", [f"{a}->{b}" for a, b in edges],
            "the combined relative-order constraints contain a cycle")

    try:
        floor = max(floors, key=privacy_rank)
    except Exception as exc:
        raise ConfigurationRequired(
            f"no ordering is available for the privacy floors {sorted(set(floors))}. "
            "C7 keeps the strongest included restriction, and an ordering P10 "
            "invented could silently choose a weaker floor than an included "
            "fragment requires."
        ) from exc

    return MergedConstraints(
        roles=tuple(roles),
        relative_order=tuple(dict.fromkeys(edges)),
        optional_roles=frozenset(optional),
        metadata_only_roles=frozenset(metadata_only),
        allowed_values=allowed,
        privacy_floor=floor,
    )
```

- [ ] **Step 4: Write the catalogue loader**

```python
# src/tree_design/catalogue.py
"""The packaged template library, loaded through an injected reader.

`planning/domains/` is a research and authorship surface, not a runtime import
target. A later deterministic compiler consumes ratified catalogue records and
emits a versioned manifest with provenance and validation-report hashes; this
module reads that manifest and nothing else. It does not import planning code,
does not touch the filesystem, and does not fall back to an empty catalogue —
an empty release would make C1 pass by having nothing to resolve.
"""
from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from tree_design.config import ConfigurationRequired
from tree_design.templates import (
    ApplicabilityRef,
    FragmentRef,
    PurposeProfileRef,
    RoleBinding,
    TemplateApplicability,
    TemplateDefinition,
    TemplateDimension,
    TemplateFragment,
)


@dataclass(frozen=True)
class TemplateCatalogue:
    release_id: str
    fragments: Mapping[tuple[str, int], TemplateFragment]
    definitions: Mapping[tuple[str, int], TemplateDefinition]
    applicabilities: Mapping[tuple[str, int], TemplateApplicability]

    def has_fragment(self, fragment_id: str, fragment_version: int) -> bool:
        return (fragment_id, fragment_version) in self.fragments

    def fragment(self, ref: FragmentRef) -> TemplateFragment:
        return self.fragments[ref.key()]

    def applicability(self, ref: ApplicabilityRef) -> TemplateApplicability:
        return self.applicabilities[ref.key()]

    def rows_for_schema(self, uses_schema: str) -> tuple[TemplateApplicability, ...]:
        """Every row that makes a recipe eligible in this one schema context.

        A schema may have several rows and a definition may be referenced by rows
        for several schemas. That is the whole many-to-many seam, and it stays
        safe because each row still resolves against exactly one schema.
        """
        return tuple(
            row for row in self.applicabilities.values()
            if row.uses_schema == uses_schema
        )


def _fragment(raw: dict) -> TemplateFragment:
    return TemplateFragment(
        fragment_id=raw["fragment_id"],
        fragment_version=raw["fragment_version"],
        roles=tuple(raw["roles"]),
        relative_order=tuple(tuple(pair) for pair in raw["relative_order"]),
        imports=tuple(FragmentRef(**ref) for ref in raw["imports"]),
        optional_roles=tuple(raw["optional_roles"]),
        metadata_only_roles=tuple(raw["metadata_only_roles"]),
        allowed_values=raw["allowed_values"],
        privacy_floor=raw["privacy_floor"],
        provenance=tuple(raw["provenance"]),
    )


def _definition(raw: dict) -> TemplateDefinition:
    return TemplateDefinition(
        template_id=raw["template_id"],
        template_version=raw["template_version"],
        origin_kind=raw["origin_kind"],
        scope_kind=raw["scope_kind"],
        publication_state=raw["publication_state"],
        fragment_refs=tuple(FragmentRef(**ref) for ref in raw["fragment_refs"]),
        dimensions=tuple(TemplateDimension(**d) for d in raw["dimensions"]),
        optional_branch_patterns=tuple(raw["optional_branch_patterns"]),
        sensitivity_policy_ref=raw["sensitivity_policy_ref"],
        validation_constraints=tuple(raw["validation_constraints"]),
        example_label_chains=tuple(tuple(c) for c in raw["example_label_chains"]),
    )


def _applicability(raw: dict) -> TemplateApplicability:
    profile = raw.get("purpose_profile_ref")
    return TemplateApplicability(
        applicability_id=raw["applicability_id"],
        applicability_version=raw["applicability_version"],
        template_id=raw["template_id"],
        template_version=raw["template_version"],
        uses_schema=raw["uses_schema"],
        purpose_profile_ref=None if profile is None else PurposeProfileRef(**profile),
        allowed_fields=tuple(raw["allowed_fields"]),
        detection_signal_refs=tuple(raw["detection_signal_refs"]),
        role_bindings=tuple(RoleBinding(**b) for b in raw["role_bindings"]),
        exclusions=tuple(raw["exclusions"]),
        provenance=tuple(raw["provenance"]),
    )


def load_catalogue(read_manifest: Callable[[], str]) -> TemplateCatalogue:
    """Parse one compiled release. The caller supplies the bytes.

    An injected reader rather than a path keeps this module out of the
    filesystem entirely, which is what makes the "no repository scanning" guard
    checkable by import inspection rather than by hope.
    """
    if not callable(read_manifest):
        raise ConfigurationRequired(
            "the packaged template catalogue is supplied by the caller; P10 does "
            "not locate it, scan for it, or default to an empty release"
        )
    manifest = json.loads(read_manifest())
    release_id = manifest.get("release_id")
    if not release_id:
        raise ConfigurationRequired(
            "a compiled catalogue carries a release identity; without one, two "
            "different libraries are indistinguishable in a frozen tree"
        )
    fragments = {}
    for raw in manifest["fragments"]:
        record = _fragment(raw)
        fragments[(record.fragment_id, record.fragment_version)] = record
    definitions = {}
    for raw in manifest["definitions"]:
        record = _definition(raw)
        definitions[(record.template_id, record.template_version)] = record
    applicabilities = {}
    for raw in manifest["applicabilities"]:
        record = _applicability(raw)
        applicabilities[
            (record.applicability_id, record.applicability_version)] = record
    return TemplateCatalogue(
        release_id=release_id,
        fragments=fragments,
        definitions=definitions,
        applicabilities=applicabilities,
    )
```

- [ ] **Step 5: Run and verify GREEN**

Run: `python3.12 -m pytest -q tests/p10/test_p10_templates.py`

Expected: PASS, fifteen tests. `test_a_fragment_carries_no_user_value_and_no_field_mapping` passes because `TemplateFragment` has no `field_bindings` parameter at all, so the constructor raises `TypeError` — the shape refuses it rather than a validator rejecting it.

- [ ] **Step 6: Commit**

```bash
git add src/tree_design/templates.py src/tree_design/catalogue.py \
        tests/p10/test_p10_templates.py
git commit -m "feat(p10): define composable template records and the catalogue loader"
```

### Task 7: Route many-to-many and gate the composition C1–C8

**Files:**
- Create: `src/tree_design/routing.py`
- Create: `tests/p10/test_p10_routing.py`

**Interfaces:**

*Consumes:* `tree_design.catalogue.TemplateCatalogue`, `tree_design.templates` (`resolve_fragment_imports`, `merge_fragment_constraints`, `CompositionConflict`, `ResolvedDimension`), `tree_design.upstream` (`AcceptedGroup`, `resolve_role_to_field`, `UpstreamUnavailable`), `tree_design.config.TreeLimits`.

*Produces:*

```python
@dataclass(frozen=True)
class BranchContext:
    branch_node_id: str
    domains: tuple[str, ...]
    accepted_groups: tuple[AcceptedGroup, ...]
    member_file_ids: frozenset[str]
    handling_classes: frozenset[str]
    purpose_profile_refs: tuple[PurposeProfileRef, ...]

@dataclass(frozen=True)
class CompositionCandidate:
    applicability_refs: tuple[ApplicabilityRef, ...]
    resolved_dimensions: tuple[ResolvedDimension, ...]
    privacy_floor: str
    covered_file_ids: frozenset[str]
    gates_passed: tuple[str, ...]
    explanation: str

@dataclass(frozen=True)
class RoutingReport:
    candidates: tuple[CompositionCandidate, ...]
    conflicts: tuple[CompositionConflict, ...]
    deferred: int

def eligible_rows(catalogue, context: BranchContext) -> tuple[TemplateApplicability, ...]: ...
def evaluate_composition(conn, catalogue, context, rows, *, privacy_rank,
                         satisfies_purpose_profile) -> CompositionCandidate: ...
def route_branch(conn, catalogue, context, *, limits: TreeLimits, privacy_rank,
                 satisfies_purpose_profile, rank_candidates) -> RoutingReport: ...
```

**Done-means:** DM13 (C1–C8 independently falsifiable), DM14 (many-to-many reuse), DM15 (purpose composition preserves heterogeneity), DM16 (branch choices isolated).

- [ ] **Step 1: Write one failing fixture per gate**

```python
# tests/p10/test_p10_routing.py
"""P10 Task 7 — the eight composition gates, one falsifying fixture each.

Domain is one applicability signal, never a one-template ownership key. One
definition may serve two domains through two independent one-schema rows; one
domain may offer two structurally different recipes; a purpose packet may
combine compatible fragments across domains without unioning anyone's fact
allow-list. Every one of those is a test below, because each is a failure case
the design names explicitly.
"""
from __future__ import annotations

import dataclasses
import json

import pytest

from tree_design.catalogue import load_catalogue
from tree_design.config import tree_limits
from tree_design.routing import BranchContext, eligible_rows, evaluate_composition, route_branch
from tree_design.templates import (
    ApplicabilityRef,
    CompositionConflict,
    FragmentRef,
    PurposeProfileRef,
    RoleBinding,
    TemplateApplicability,
    TemplateDefinition,
    TemplateDimension,
    TemplateFragment,
)
from tree_design.upstream import AcceptedGroup, GroupMember
from tree_design.vocabulary import ACTION_SELECTED, BUILT_IN, CROSS_DOMAIN, PUBLISHED, REQUIRED

RANK = {"policy.public": 0, "policy.sensitive": 1}.__getitem__
ALWAYS = lambda profile, groups: True
NEVER = lambda profile, groups: False
FIRST = lambda candidates: candidates


def _fragment(fragment_id, roles, order=(), floor="policy.public", imports=()):
    return TemplateFragment(
        fragment_id=fragment_id, fragment_version=1, roles=tuple(roles),
        relative_order=tuple(order), imports=tuple(imports), optional_roles=(),
        metadata_only_roles=(), allowed_values={}, privacy_floor=floor,
        provenance=("row:fixture",),
    )


def _definition(template_id, fragment_refs, dimensions, scope=CROSS_DOMAIN):
    return TemplateDefinition(
        template_id=template_id, template_version=1, origin_kind=BUILT_IN,
        scope_kind=scope, publication_state=PUBLISHED,
        fragment_refs=tuple(fragment_refs),
        dimensions=tuple(dimensions), optional_branch_patterns=(),
        sensitivity_policy_ref="policy.public", validation_constraints=(),
        example_label_chains=(),
    )


def _row(applicability_id, template_id, schema, bindings, profile=None):
    return TemplateApplicability(
        applicability_id=applicability_id, applicability_version=1,
        template_id=template_id, template_version=1, uses_schema=schema,
        purpose_profile_ref=profile,
        allowed_fields=tuple(field for _, field in bindings),
        detection_signal_refs=("signal.fixture",),
        role_bindings=tuple(RoleBinding(role, field) for role, field in bindings),
        exclusions=(), provenance=("row:fixture",),
    )


def _catalogue(fragments, definitions, rows):
    manifest = {
        "release_id": "rel-1",
        "fragments": [dataclasses.asdict(f) for f in fragments],
        "definitions": [dataclasses.asdict(d) for d in definitions],
        "applicabilities": [dataclasses.asdict(r) for r in rows],
    }
    return load_catalogue(lambda: json.dumps(manifest))


def _group(group_id, domain, files):
    return AcceptedGroup(
        group_id=group_id, label=group_id, domain=domain,
        members=tuple(GroupMember(f, f"h_{f}", "direct-anchor") for f in files),
        anchor_facts=(f"fact_{group_id}",), excluded_members=(),
    )


def _context(domains, groups, classes=frozenset({"personal_non_sensitive"}),
             profiles=()):
    files = frozenset(m.file_id for g in groups for m in g.members)
    return BranchContext(
        branch_node_id="n_branch", domains=tuple(domains),
        accepted_groups=tuple(groups), member_file_ids=files,
        handling_classes=classes, purpose_profile_refs=tuple(profiles),
    )


SUBJECT = _fragment("subject", ("subject",))
KIND = _fragment("artifact-kind", ("artifact_kind",))
COURSEWORK = _definition(
    "coursework", (FragmentRef("subject", 1), FragmentRef("artifact-kind", 1)),
    (TemplateDimension("subject", 0, REQUIRED, False, "Users search by course."),
     TemplateDimension("artifact_kind", 1, REQUIRED, False, "Homework vs exam.")),
)


def test_c1_an_unresolvable_version_creates_no_node(conn):
    catalogue = _catalogue((SUBJECT,), (COURSEWORK,), (
        _row("a1", "coursework", "academic",
             (("subject", "subject"), ("artifact_kind", "work_type"))),
    ))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    with pytest.raises(CompositionConflict) as excinfo:
        evaluate_composition(
            conn, catalogue, context, catalogue.rows_for_schema("academic"),
            privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
    assert excinfo.value.gate == "C1"
    assert "artifact-kind@1" in " ".join(excinfo.value.conflicting)


def test_c2_a_role_that_maps_to_no_live_p6_field_fails_closed(conn):
    catalogue = _catalogue((SUBJECT, KIND), (COURSEWORK,), (
        _row("a1", "coursework", "academic",
             (("subject", "subject"), ("artifact_kind", "not_a_field"))),
    ))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    with pytest.raises(CompositionConflict) as excinfo:
        evaluate_composition(
            conn, catalogue, context, catalogue.rows_for_schema("academic"),
            privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
    assert excinfo.value.gate == "C2"


def test_c3_a_domain_label_alone_does_not_satisfy_a_purpose_binding(conn):
    profile = PurposeProfileRef("pp.grad-application", 1)
    catalogue = _catalogue((SUBJECT,), (_definition("apps", (FragmentRef("subject", 1),),
        (TemplateDimension("subject", 0, REQUIRED, False, "Institution first."),)),), (
        _row("a1", "apps", "academic", (("subject", "subject"),), profile=profile),
    ))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    with pytest.raises(CompositionConflict) as excinfo:
        evaluate_composition(
            conn, catalogue, context, catalogue.rows_for_schema("academic"),
            privacy_rank=RANK, satisfies_purpose_profile=NEVER)
    assert excinfo.value.gate == "C3"
    assert "pp.grad-application" in " ".join(excinfo.value.conflicting)


def test_c4_two_rows_binding_one_role_to_two_fields_is_surfaced_not_picked(conn):
    catalogue = _catalogue((SUBJECT,), (_definition("t", (FragmentRef("subject", 1),),
        (TemplateDimension("subject", 0, REQUIRED, False, "why"),)),), (
        _row("a1", "t", "academic", (("subject", "subject"),)),
        _row("a2", "t", "academic", (("subject", "term"),)),
    ))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    with pytest.raises(CompositionConflict) as excinfo:
        evaluate_composition(
            conn, catalogue, context, catalogue.rows_for_schema("academic"),
            privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
    assert excinfo.value.gate == "C4"
    assert "subject" in " ".join(excinfo.value.conflicting)


def test_c5_two_fragments_with_opposite_order_are_a_cycle(conn):
    left = _fragment("l", ("subject", "artifact_kind"), (("subject", "artifact_kind"),))
    right = _fragment("r", ("subject", "artifact_kind"), (("artifact_kind", "subject"),))
    definition = _definition("t", (FragmentRef("l", 1), FragmentRef("r", 1)),
        (TemplateDimension("subject", 0, REQUIRED, False, "why"),
         TemplateDimension("artifact_kind", 1, REQUIRED, False, "why")))
    catalogue = _catalogue((left, right), (definition,), (
        _row("a1", "t", "academic",
             (("subject", "subject"), ("artifact_kind", "work_type"))),
    ))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    with pytest.raises(CompositionConflict) as excinfo:
        evaluate_composition(
            conn, catalogue, context, catalogue.rows_for_schema("academic"),
            privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
    assert excinfo.value.gate == "C5"


def test_c6_a_composition_that_would_drop_a_member_is_refused(conn):
    """"Hiding dropped or unresolved files in a 'successful' preview" is a
    failure case the design names outright."""
    catalogue = _catalogue((SUBJECT,), (_definition("t", (FragmentRef("subject", 1),),
        (TemplateDimension("subject", 0, REQUIRED, False, "why"),)),), (
        _row("a1", "t", "academic", (("subject", "subject"),)),
    ))
    academic = _group("g1", "academic", ("f1",))
    photos = _group("g2", "photos", ("f2",))
    context = _context(("academic", "photos"), (academic, photos))
    with pytest.raises(CompositionConflict) as excinfo:
        evaluate_composition(
            conn, catalogue, context, catalogue.rows_for_schema("academic"),
            privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
    assert excinfo.value.gate == "C6"
    assert "f2" in " ".join(excinfo.value.conflicting)


def test_c7_the_combined_floor_is_never_weaker_than_an_included_one(conn):
    strict = _fragment("strict", ("artifact_kind",), floor="policy.sensitive")
    definition = _definition("t", (FragmentRef("subject", 1), FragmentRef("strict", 1)),
        (TemplateDimension("subject", 0, REQUIRED, False, "why"),
         TemplateDimension("artifact_kind", 1, REQUIRED, False, "why")))
    catalogue = _catalogue((SUBJECT, strict), (definition,), (
        _row("a1", "t", "academic",
             (("subject", "subject"), ("artifact_kind", "work_type"))),
    ))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    candidate = evaluate_composition(
        conn, catalogue, context, catalogue.rows_for_schema("academic"),
        privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
    assert candidate.privacy_floor == "policy.sensitive"
    assert "C7" in candidate.gates_passed


def test_c8_a_passing_candidate_creates_no_node(conn):
    catalogue = _catalogue((SUBJECT, KIND), (COURSEWORK,), (
        _row("a1", "coursework", "academic",
             (("subject", "subject"), ("artifact_kind", "work_type"))),
    ))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    candidate = evaluate_composition(
        conn, catalogue, context, catalogue.rows_for_schema("academic"),
        privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
    assert candidate.gates_passed == ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8")
    assert not hasattr(candidate, "nodes")
    assert conn.execute(
        "SELECT count(*) AS n FROM sqlite_master WHERE name = 'tree_nodes'"
    ).fetchone()["n"] in (0, 1)


def test_one_definition_serves_two_domains_without_duplication(conn):
    catalogue = _catalogue((SUBJECT, KIND), (COURSEWORK,), (
        _row("a-academic", "coursework", "academic",
             (("subject", "subject"), ("artifact_kind", "work_type"))),
        _row("a-research", "coursework", "research",
             (("subject", "subject"), ("artifact_kind", "artifact_type"))),
    ))
    assert len(catalogue.definitions) == 1
    for schema, expected in (("academic", "work_type"), ("research", "artifact_type")):
        context = _context((schema,), (_group("g", schema, ("f1",)),))
        candidate = evaluate_composition(
            conn, catalogue, context, catalogue.rows_for_schema(schema),
            privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
        resolved = {d.role_ref: d.field_ref for d in candidate.resolved_dimensions}
        assert resolved["artifact_kind"] == expected


def test_one_domain_offers_two_structurally_different_recipes(conn):
    flat = _definition("flat", (FragmentRef("subject", 1),),
        (TemplateDimension("subject", 0, REQUIRED, False, "Course only."),))
    catalogue = _catalogue((SUBJECT, KIND), (COURSEWORK, flat), (
        _row("a-deep", "coursework", "academic",
             (("subject", "subject"), ("artifact_kind", "work_type"))),
        _row("a-flat", "flat", "academic", (("subject", "subject"),)),
    ))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    rows = eligible_rows(catalogue, context)
    assert {row.template_id for row in rows} == {"coursework", "flat"}


def test_a_mixed_domain_purpose_packet_keeps_every_member_and_both_schemas(conn):
    profile = PurposeProfileRef("pp.grad-application", 1)
    counterpart = _fragment("counterpart", ("counterpart",))
    definition = _definition("packet", (FragmentRef("counterpart", 1),),
        (TemplateDimension("counterpart", 0, REQUIRED, False, "Institution."),))
    catalogue = _catalogue((counterpart,), (definition,), (
        _row("a-apps", "packet", "college_applications",
             (("counterpart", "target_school"),), profile=profile),
        _row("a-academic", "packet", "academic",
             (("counterpart", "subject"),), profile=profile),
    ))
    apps = _group("g_apps", "college_applications", ("transcript",))
    academic = _group("g_academic", "academic", ("recommendation",))
    context = _context(("college_applications", "academic"), (apps, academic),
                       profiles=(profile,))
    rows = catalogue.rows_for_schema("college_applications") + \
        catalogue.rows_for_schema("academic")
    candidate = evaluate_composition(
        conn, catalogue, context, rows,
        privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
    assert candidate.covered_file_ids == {"transcript", "recommendation"}
    # Two rows, two schemas, no union: each row still allows only its own fields.
    assert len(candidate.applicability_refs) == 2
    allowed = [set(catalogue.applicability(ref).allowed_fields)
               for ref in candidate.applicability_refs]
    assert allowed[0] != allowed[1]


def test_the_router_returns_a_bounded_ranked_set_not_every_match(conn):
    """The composable-template design: "The router returns a small explained
    candidate set, not every superficially matching template. Candidate ceilings
    and ranking weights remain injected configuration."
    """
    from database_agent.budget import set_ceiling

    set_ceiling(conn, "tree.max_folder_proposals_and_depth", 1)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    limits = tree_limits(
        conn, excessive_depth_warning=6, tiny_folder_max_files=3,
        tiny_folder_count_warning=12,
        materially_improves_retrieval=lambda preview: None)
    flat = _definition("flat", (FragmentRef("subject", 1),),
        (TemplateDimension("subject", 0, REQUIRED, False, "Course only."),))
    catalogue = _catalogue((SUBJECT, KIND), (COURSEWORK, flat), (
        _row("a-deep", "coursework", "academic",
             (("subject", "subject"), ("artifact_kind", "work_type"))),
        _row("a-flat", "flat", "academic", (("subject", "subject"),)),
    ))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    report = route_branch(
        conn, catalogue, context, limits=limits, privacy_rank=RANK,
        satisfies_purpose_profile=ALWAYS, rank_candidates=FIRST)
    assert len(report.candidates) == 1
    assert report.deferred == 1


def test_a_missing_binding_produces_a_conflict_not_a_generic_fallback(conn):
    catalogue = _catalogue((SUBJECT,), (COURSEWORK,), ())
    context = _context(("finance",), (_group("g1", "finance", ("f1",)),))
    report = route_branch(
        conn, catalogue, context,
        limits=None, privacy_rank=RANK, satisfies_purpose_profile=ALWAYS,
        rank_candidates=FIRST)
    assert report.candidates == ()
    assert report.conflicts
    assert report.conflicts[0].gate == "C3"
```

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p10/test_p10_routing.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'tree_design.routing'`.

- [ ] **Step 3: Write the router**

```python
# src/tree_design/routing.py
"""Branch evidence in; a small explained candidate set out. No nodes.

The route is deterministic and evidence-bound:

    accepted scaffold branch
      -> branch context (groups, domains, facts, purpose, privacy)
      -> eligible applicability rows
      -> candidate compositions
      -> C1-C8 against the branch's actual evidence
      -> a bounded, ranked, INERT candidate set

Domain is one applicability signal, never a one-template ownership key. A row
makes a recipe eligible to PREVIEW; nothing here activates one, and nothing here
writes a node. C8 is the gate that says so, and it is the last one because every
earlier gate can still turn a plausible recipe into a refusal.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from tree_design.catalogue import TemplateCatalogue
from tree_design.config import TreeLimits
from tree_design.templates import (
    ApplicabilityRef,
    CompositionConflict,
    FragmentRef,
    PurposeProfileRef,
    ResolvedDimension,
    TemplateApplicability,
    merge_fragment_constraints,
    resolve_fragment_imports,
)
from tree_design.upstream import AcceptedGroup, UpstreamUnavailable, resolve_role_to_field
from tree_design.vocabulary import ACTION_SELECTED

#: The gates, in the only order they may run. C1 before C2 because a role cannot
#: be resolved before the fragment defining it is found; C8 last because it is
#: the statement that nothing before it activated anything.
GATE_ORDER: tuple[str, ...] = ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8")


@dataclass(frozen=True)
class BranchContext:
    """Everything the router may consider. Nothing here is a domain label alone."""

    branch_node_id: str
    domains: tuple[str, ...]
    accepted_groups: tuple[AcceptedGroup, ...]
    member_file_ids: frozenset[str]
    handling_classes: frozenset[str]
    purpose_profile_refs: tuple[PurposeProfileRef, ...] = ()


@dataclass(frozen=True)
class CompositionCandidate:
    applicability_refs: tuple[ApplicabilityRef, ...]
    resolved_dimensions: tuple[ResolvedDimension, ...]
    privacy_floor: str
    covered_file_ids: frozenset[str]
    gates_passed: tuple[str, ...]
    explanation: str


@dataclass(frozen=True)
class RoutingReport:
    candidates: tuple[CompositionCandidate, ...]
    conflicts: tuple[CompositionConflict, ...]
    deferred: int


def eligible_rows(catalogue: TemplateCatalogue,
                  context: BranchContext) -> tuple[TemplateApplicability, ...]:
    """Every row whose schema is one of this branch's domains.

    Eligibility is not selection. A row here has done nothing but earn the right
    to be checked against the branch's actual evidence by C3.
    """
    rows: list[TemplateApplicability] = []
    for domain in context.domains:
        rows.extend(catalogue.rows_for_schema(domain))
    return tuple(rows)


def evaluate_composition(
    conn: sqlite3.Connection,
    catalogue: TemplateCatalogue,
    context: BranchContext,
    rows: Sequence[TemplateApplicability],
    *,
    privacy_rank: Callable[[str], int],
    satisfies_purpose_profile: Callable[[PurposeProfileRef, Sequence[AcceptedGroup]], bool],
) -> CompositionCandidate:
    """Run C1-C8 over one candidate set of rows. Raise or return; never both."""
    if not rows:
        raise CompositionConflict(
            "C3", [*context.domains],
            "no applicability row makes any recipe eligible for this branch's "
            "domains, and there is no generic fallback to invent")

    passed: list[str] = []

    # C1 — identity. Every template, fragment and version the rows name exists.
    fragments = []
    for row in rows:
        definition = catalogue.definitions.get((row.template_id, row.template_version))
        if definition is None:
            raise CompositionConflict(
                "C1", [f"{row.template_id}@{row.template_version}"],
                "the packaged release does not contain this definition version")
        for ref in definition.fragment_refs:
            fragments.extend(resolve_fragment_imports(catalogue, ref))
    # Deduplicate by exact identity, preserving import order.
    seen: set[tuple[str, int]] = set()
    ordered = []
    for fragment in fragments:
        key = (fragment.fragment_id, fragment.fragment_version)
        if key not in seen:
            seen.add(key)
            ordered.append(fragment)
    passed.append("C1")

    # C3 — applicability from evidence, not from a domain label. Run before C2
    # so a branch that was never eligible does not spend field lookups.
    for row in rows:
        if row.purpose_profile_ref is None:
            continue
        if not satisfies_purpose_profile(row.purpose_profile_ref,
                                         context.accepted_groups):
            raise CompositionConflict(
                "C3", [row.purpose_profile_ref.purpose_profile_id, row.applicability_id],
                "the branch's accepted groups do not satisfy this authored purpose "
                "profile; a domain name alone is insufficient")

    # C4 — a required role resolves once. Competing mappings are surfaced.
    bindings: dict[str, set[str]] = {}
    for row in rows:
        for binding in row.role_bindings:
            bindings.setdefault(binding.role_ref, set()).add(binding.field_ref)
    ambiguous = sorted(role for role, fields in bindings.items() if len(fields) > 1)
    if ambiguous:
        detail = "; ".join(
            f"{role} -> {sorted(bindings[role])}" for role in ambiguous)
        raise CompositionConflict(
            "C4", ambiguous,
            f"a role resolves to more than one field ({detail}) and P10 picks "
            "none silently")

    # C2 — every resolved role maps to a live, destination-eligible P6 field.
    resolved: list[ResolvedDimension] = []
    for role, fields in sorted(bindings.items()):
        field_ref = next(iter(fields))
        try:
            resolve_role_to_field(conn, role_ref=role, field_ref=field_ref)
        except UpstreamUnavailable as exc:
            raise CompositionConflict(
                "C2", [role, field_ref], str(exc)) from exc
    passed.extend(["C2", "C3", "C4"])

    # C5 — combined order is acyclic, and the merge is intersection, not
    # last-writer-wins. `merge_fragment_constraints` raises C5 on either failure.
    merged = merge_fragment_constraints(ordered, privacy_rank=privacy_rank)
    order_position = {role: index for index, role in
                      enumerate(_ordered_roles(merged))}
    for role in sorted(bindings, key=lambda r: order_position.get(r, len(order_position))):
        resolved.append(ResolvedDimension(
            role_ref=role, field_ref=next(iter(bindings[role])),
            action=ACTION_SELECTED,
            order_index=order_position.get(role, len(order_position)),
            display_label=None,
        ))
    passed.append("C5")

    # C6 — coverage. Every member of every accepted group in this branch is
    # reachable through one of the selected rows' schemas.
    schemas = {row.uses_schema for row in rows}
    covered: set[str] = set()
    dropped: list[str] = []
    for group in context.accepted_groups:
        if group.domain in schemas:
            covered.update(member.file_id for member in group.members)
        else:
            dropped.extend(member.file_id for member in group.members)
    if dropped:
        raise CompositionConflict(
            "C6", sorted(dropped),
            "this composition covers no schema for these members, so a preview "
            "would silently drop them")
    passed.append("C6")

    # C7 — the strongest included restriction survives the merge.
    floor = merged.privacy_floor
    passed.append("C7")

    # C8 — activation. Reaching here produces a preview and nothing else.
    passed.append("C8")

    explanation = (
        f"{len(rows)} applicability row(s) across {sorted(schemas)} resolve "
        f"{len(resolved)} dimension(s) from this branch's accepted groups; the "
        f"combined privacy floor is {floor}."
    )
    return CompositionCandidate(
        applicability_refs=tuple(
            ApplicabilityRef(row.applicability_id, row.applicability_version)
            for row in rows),
        resolved_dimensions=tuple(resolved),
        privacy_floor=floor,
        covered_file_ids=frozenset(covered),
        gates_passed=tuple(GATE_ORDER),
        explanation=explanation,
    )


def _ordered_roles(merged) -> tuple[str, ...]:
    """The one explicit preview order C5 produced, roles first-seen otherwise."""
    position = {role: index for index, role in enumerate(merged.roles)}
    for before, after in merged.relative_order:
        if before in position and after in position:
            if position[before] > position[after]:
                position[before], position[after] = position[after], position[before]
    return tuple(sorted(position, key=position.__getitem__))


def route_branch(
    conn: sqlite3.Connection,
    catalogue: TemplateCatalogue,
    context: BranchContext,
    *,
    limits: TreeLimits | None,
    privacy_rank: Callable[[str], int],
    satisfies_purpose_profile: Callable[[PurposeProfileRef, Sequence[AcceptedGroup]], bool],
    rank_candidates: Callable[[Sequence[CompositionCandidate]], Sequence[CompositionCandidate]],
) -> RoutingReport:
    """One template's worth of candidates per eligible definition, bounded.

    Ranking is injected because the design fixes no weights, and the ceiling is
    P1's `tree.max_folder_proposals_and_depth`. Surplus candidates are DEFERRED
    and counted, never silently dropped: §8.6 requires the interface to "show the
    difference between completed work and deferred work".
    """
    candidates: list[CompositionCandidate] = []
    conflicts: list[CompositionConflict] = []

    rows = eligible_rows(catalogue, context)
    by_template: dict[tuple[str, int], list[TemplateApplicability]] = {}
    for row in rows:
        by_template.setdefault((row.template_id, row.template_version), []).append(row)

    if not by_template:
        conflicts.append(CompositionConflict(
            "C3", [*context.domains],
            "no applicability row makes any recipe eligible for this branch's "
            "domains, and there is no generic fallback to invent"))

    for group in by_template.values():
        try:
            candidates.append(evaluate_composition(
                conn, catalogue, context, group, privacy_rank=privacy_rank,
                satisfies_purpose_profile=satisfies_purpose_profile))
        except CompositionConflict as conflict:
            conflicts.append(conflict)

    ranked = list(rank_candidates(candidates))
    deferred = 0
    if limits is not None and len(ranked) > limits.max_folder_proposals_and_depth:
        deferred = len(ranked) - limits.max_folder_proposals_and_depth
        ranked = ranked[:limits.max_folder_proposals_and_depth]

    return RoutingReport(
        candidates=tuple(ranked),
        conflicts=tuple(conflicts),
        deferred=deferred,
    )
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3.12 -m pytest -q tests/p10/test_p10_routing.py`

Expected: PASS, thirteen tests — one falsifying fixture for each of C1 through C8, plus the four many-to-many cases and the candidate ceiling. If `test_c2_a_role_that_maps_to_no_live_p6_field_fails_closed` passes for the wrong reason, check that `conftest.py` really seeded `create_fields`: without the catalogue, every role fails C2 and the test would pass while proving nothing.

- [ ] **Step 5: Commit**

```bash
git add src/tree_design/routing.py tests/p10/test_p10_routing.py
git commit -m "feat(p10): route composable templates by branch evidence"
```

### Task 8: The Site-E schema validator, and the fragment boundary P10 owns

**Files:**
- Create: `src/tree_design/template_schema.py`
- Create: `tests/p10/test_p10_template_schema.py`
- Create: `tests/integration/test_p10_p8_template.py`

**Interfaces:**

*Consumes:* `llm_harness.template_validation.TemplateDependencies` / `validate_template_response`, `llm_harness.records.DossierRequest` / `EvidenceItem` / `Conflict`, `llm_harness.vocabulary.E_TEMPLATE` / `ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE`, `privacy.release.ModelCallRequest`, `tree_design.catalogue.TemplateCatalogue`.

*Produces:*

```python
TEMPLATE_PAYLOAD_KEYS: tuple[str, ...]
FORBIDDEN_PUBLISHING_KEYS: tuple[str, ...]

def template_schema_validator(catalogue: TemplateCatalogue) -> Callable[[object], bool]: ...
def template_dependencies(catalogue: TemplateCatalogue) -> TemplateDependencies: ...
def allowed_vocabulary_for(catalogue: TemplateCatalogue, *,
                           uses_schema: str) -> tuple[str, ...]: ...
def build_template_request(*, subject_ref: str, plan_version: str,
                           evidence_items, conflicts,
                           model_call_request) -> DossierRequest: ...
```

**Why this task exists.** `grep -rn "fragment" src/` returns exactly one hit today, in
`src/facts/session.py:34`, and it is about filesystem path fragments. Site E validates schema
shape, vocabulary closure, per-dimension citation and per-level justification, and has no notion
of a fragment at all — so the boundary the domain handoff states, that a Site-E proposal "may
reference published fragments by exact ID/version" but "cannot publish or propose a new canonical
fragment", is enforced nowhere. The library plan assigns it to a pass gated behind P10, which
cannot run until P10 ships. P10 owns it, because P10 owns the published catalogue and is the only
part that can answer whether a named fragment exists.

**Done-means:** DM8 (a valid template is inert until approved — the schema is the first gate, not the last), and the P8 half of DM14.

- [ ] **Step 1: Write the failing schema-validator tests**

```python
# tests/p10/test_p10_template_schema.py
"""P10 Task 8 — the strict Site-E response schema, and the fragment boundary.

P8 owns the harness: structured-output enforcement, the citation check, the
verdict. P10 owns what "the required template shape" MEANS, and hands P8 the
callable that decides it. Everything below is P10's half.

The load-bearing rule: a model proposal may reference a published fragment by
exact id and version, and may add template-LOCAL semantic dimensions, but it may
not publish or propose a new canonical fragment. Repeated local dimensions become
fragment candidates only in a later human-reviewed synthesis pass.
"""
from __future__ import annotations

import dataclasses
import json

import pytest

from tree_design.catalogue import load_catalogue
from tree_design.template_schema import (
    FORBIDDEN_PUBLISHING_KEYS,
    TEMPLATE_PAYLOAD_KEYS,
    allowed_vocabulary_for,
    template_dependencies,
    template_schema_validator,
)
from tree_design.templates import RoleBinding, TemplateApplicability, TemplateFragment

PUBLISHED_FRAGMENT = TemplateFragment(
    fragment_id="event-capture-time", fragment_version=1,
    roles=("event", "capture_time"),
    relative_order=(("event", "capture_time"),), imports=(),
    optional_roles=(), metadata_only_roles=(), allowed_values={},
    privacy_floor="policy.public", provenance=("row:photos-01",),
)
ROW = TemplateApplicability(
    applicability_id="photos--photos", applicability_version=1,
    template_id="photo-event", template_version=1, uses_schema="photos",
    purpose_profile_ref=None, allowed_fields=("event", "capture_year"),
    detection_signal_refs=("signal.exif",),
    role_bindings=(RoleBinding("event", "event"),
                   RoleBinding("capture_time", "capture_year")),
    exclusions=(), provenance=("row:photos-01",),
)
CATALOGUE = load_catalogue(lambda: json.dumps({
    "release_id": "rel-1",
    "fragments": [dataclasses.asdict(PUBLISHED_FRAGMENT)],
    "definitions": [],
    "applicabilities": [dataclasses.asdict(ROW)],
}))


def _payload(**overrides) -> dict:
    payload = {
        "domain": "photos",
        "allowed_fields": ["event", "capture_year"],
        "fragment_refs": [
            {"fragment_id": "event-capture-time", "fragment_version": 1}],
        "dimensions": [
            {"name": "event", "evidence_ref": "obs-1", "requirement": "required",
             "metadata_only": False, "order_index": 0},
            {"name": "capture_year", "evidence_ref": "obs-1",
             "requirement": "optional", "metadata_only": False, "order_index": 1},
        ],
        "levels": [
            {"dimension": "event",
             "retrieval_justification": "Users look for a trip, not a date."},
            {"dimension": "capture_year",
             "retrieval_justification": "Capture date defines this material."},
        ],
        "sensitivity_policy_ref": "policy.public",
        "example_label_chains": [["Photos", "Iceland 2026"]],
    }
    payload.update(overrides)
    return payload


def test_a_well_formed_proposal_referencing_a_published_fragment_passes():
    validator = template_schema_validator(CATALOGUE)
    assert validator(_payload()) is True


def test_a_proposal_naming_an_unpublished_fragment_is_rejected():
    validator = template_schema_validator(CATALOGUE)
    assert validator(_payload(fragment_refs=[
        {"fragment_id": "counterpart-cycle", "fragment_version": 1}])) is False


def test_a_proposal_naming_a_published_id_at_an_unpublished_version_is_rejected():
    """"Exact id AND exact version" is the whole point: version 2 of a fragment
    is a different recipe, and accepting it because the id is familiar would let
    a model activate logic nobody reviewed."""
    validator = template_schema_validator(CATALOGUE)
    assert validator(_payload(fragment_refs=[
        {"fragment_id": "event-capture-time", "fragment_version": 2}]) ) is False


def test_a_proposal_that_tries_to_publish_a_fragment_is_rejected():
    validator = template_schema_validator(CATALOGUE)
    for key in FORBIDDEN_PUBLISHING_KEYS:
        assert validator(_payload(**{key: [{"fragment_id": "new", "roles": ["x"]}]})) is False


def test_template_local_dimensions_are_allowed_and_are_not_fragments():
    """A local dimension is the model saying "this branch also splits by lens".
    That is a proposal about ONE branch. It becomes a canonical fragment only in
    the later human-reviewed synthesis pass, never here."""
    validator = template_schema_validator(CATALOGUE)
    payload = _payload()
    payload["dimensions"].append({
        "name": "lens", "evidence_ref": "obs-1", "requirement": "optional",
        "metadata_only": True, "order_index": 2,
    })
    payload["levels"].append({
        "dimension": "lens",
        "retrieval_justification": "Two shoots differ only by lens.",
    })
    payload["allowed_fields"].append("lens")
    assert validator(payload) is True


def test_a_payload_missing_any_required_key_is_rejected():
    validator = template_schema_validator(CATALOGUE)
    for key in TEMPLATE_PAYLOAD_KEYS:
        payload = _payload()
        del payload[key]
        assert validator(payload) is False, key


def test_a_dimension_that_is_not_in_allowed_fields_is_rejected():
    """§5.7: a generated template "cannot invent unsupported facts". A dimension
    the row does not allow is a field the model minted."""
    validator = template_schema_validator(CATALOGUE)
    payload = _payload()
    payload["dimensions"][0]["name"] = "mood"
    assert validator(payload) is False


def test_a_list_of_domains_is_rejected_because_a_model_may_not_create_one():
    """§5.7: a generated template may not "silently create new high-level
    domains". One proposal, one schema context."""
    validator = template_schema_validator(CATALOGUE)
    assert validator(_payload(domain=["photos", "travel"])) is False
    assert validator(_payload(domain="")) is False


def test_an_example_label_chain_holding_a_separator_is_rejected():
    validator = template_schema_validator(CATALOGUE)
    assert validator(_payload(
        example_label_chains=[["Photos/Iceland 2026"]])) is False


def test_two_dimensions_claiming_one_order_index_are_rejected():
    validator = template_schema_validator(CATALOGUE)
    payload = _payload()
    payload["dimensions"][1]["order_index"] = 0
    assert validator(payload) is False


def test_a_non_mapping_payload_is_rejected_without_raising():
    validator = template_schema_validator(CATALOGUE)
    for value in (None, [], "dimensions", 0):
        assert validator(value) is False


def test_the_allowed_vocabulary_is_the_rows_fields_and_nothing_wider():
    """P8's Site E rejects any dimension whose `name` is outside
    `Dossier.allowed_vocabulary`. P10 populates that closure, so a union across
    schemas here would widen a P6 allow-list at the dossier boundary."""
    assert allowed_vocabulary_for(CATALOGUE, uses_schema="photos") == (
        "capture_year", "event")
    assert allowed_vocabulary_for(CATALOGUE, uses_schema="academic") == ()


def test_dependencies_are_p8s_record_with_p10s_callable():
    from llm_harness.template_validation import TemplateDependencies

    deps = template_dependencies(CATALOGUE)
    assert isinstance(deps, TemplateDependencies)
    assert deps.schema_validator(_payload()) is True
```

- [ ] **Step 2: Write the failing P8 integration test**

```python
# tests/integration/test_p10_p8_template.py
"""P10 -> P8 Site E. P10 supplies the schema; P8 owns the verdict.

This is the seam the prior audit found unenforced: `grep -rn "fragment" src/`
returns one hit and it is about paths. With P10's validator injected, a proposal
naming an unpublished fragment now comes back REJECT with SCHEMA_INVALID from
P8's own machinery — no new refusal type, no second validator vocabulary.
"""
from __future__ import annotations

import json

from llm_harness.fixtures import SITE_E_OUTCOME_PAIRS
from llm_harness.template_validation import validate_template_response
from llm_harness.vocabulary import ACCEPT_DIRECT, E_TEMPLATE, REJECT, SCOPE_TEMPLATE
from tree_design.template_schema import template_dependencies

from tests.p10.test_p10_template_schema import CATALOGUE, _payload  # noqa: F401

RELEASED = "span-1"


def _resolver(observation_key: str) -> str | None:
    return RELEASED if observation_key.startswith("obs-") else None


def _never_contradicts(*_a, **_k) -> bool:
    return False


def _response(payload: dict) -> bytes:
    claim = {
        "claim_ref": "c1",
        "payload": payload,
        "citations": [{
            "evidence_ref": "obs-1",
            "cited_span": RELEASED,
            "why_it_supports": "supports the recorded claim",
        }],
    }
    return json.dumps({"claims": [claim]}, separators=(",", ":")).encode("utf-8")


def _validate(dossier, payload):
    return validate_template_response(
        dossier, _response(payload), evidence_resolver=_resolver,
        contradicts=_never_contradicts, dependencies=template_dependencies(CATALOGUE),
        model_id="fixture-model", prompt_fingerprint="fp-canonical",
        dossier_builder="p10", release_audit_id=17)


def _dossier():
    import dataclasses

    pair = next(p for p in SITE_E_OUTCOME_PAIRS if p.name == "direct_accept")
    assert pair.dossier.call_site == E_TEMPLATE
    # P10 supplies the closure; the fixture's is P8's own two-word vocabulary.
    return dataclasses.replace(
        pair.dossier, allowed_vocabulary=("event", "capture_year"))


def test_a_published_fragment_reference_reaches_an_accept_verdict():
    verdicts, _report = _validate(_dossier(), _payload())
    assert verdicts[0].outcome == ACCEPT_DIRECT
    assert verdicts[0].scope == SCOPE_TEMPLATE


def test_an_unpublished_fragment_reference_is_schema_invalid_at_p8():
    payload = _payload(fragment_refs=[
        {"fragment_id": "counterpart-cycle", "fragment_version": 1}])
    verdicts, report = _validate(_dossier(), payload)
    assert verdicts[0].outcome == REJECT
    assert "SCHEMA_INVALID" in verdicts[0].reasons
    assert report.reasons_histogram["SCHEMA_INVALID"] == 1


def test_p10_supplies_no_transport_gate_or_verdict():
    """P8 owns the only model invocation and the only verdict. If P10 ever grows
    an import of the gate or the transport, this fails and says why."""
    import ast
    from pathlib import Path

    src = Path(__file__).resolve().parents[2] / "src" / "tree_design"
    forbidden = {"privacy.gate", "llm_harness.transport", "llm_harness.harness"}
    offenders = []
    for path in sorted(src.glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.ImportFrom) and node.module in forbidden:
                offenders.append(f"{path.name} imports {node.module}")
    assert offenders == []
```

- [ ] **Step 3: Run both and verify RED**

Run: `python3.12 -m pytest -q tests/p10/test_p10_template_schema.py tests/integration/test_p10_p8_template.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'tree_design.template_schema'`.

- [ ] **Step 4: Write the schema module**

```python
# src/tree_design/template_schema.py
"""P10's half of §5.7: what "the required template shape" means.

§5.7: "Structured output constraints and schema validation should enforce the
required template shape." P8 enforces; P10 defines. The callable this
module builds is handed to P8 as `TemplateDependencies.schema_validator`, and P8
turns a False into its own REJECT / SCHEMA_INVALID verdict. P10 coins no refusal
type and reads no model response itself.

The fragment boundary lives here and nowhere else. A proposal may REFERENCE a
published fragment by exact id and version, and may add template-local semantic
dimensions. It may not publish or propose a canonical fragment, because a
fragment is shared organization logic and sharing it is a human review decision
made once, not a side effect of one branch's model call. P10 owns the boundary
because P10 owns the published catalogue and is the only part that can answer
whether a named fragment exists.
"""
from __future__ import annotations

import os
from collections.abc import Callable, Mapping, Sequence

from llm_harness.records import Conflict, DossierRequest, EvidenceItem
from llm_harness.template_validation import TemplateDependencies
from llm_harness.vocabulary import (
    ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE,
    E_TEMPLATE,
)
from tree_design.catalogue import TemplateCatalogue
from tree_design.vocabulary import DIMENSION_REQUIREMENTS

_SEPARATORS = frozenset({"/", "\\", os.sep, os.altsep or "/"})

#: Every key §5.7 names for a generated template: "a domain name, allowed fields,
#: recommended folder dimensions, field order, optional versus required levels,
#: metadata-only fields, sensitivity policy, and example paths". `fragment_refs`
#: is the ninth, and it is what makes reuse expressible without copying.
TEMPLATE_PAYLOAD_KEYS: tuple[str, ...] = (
    "domain",
    "allowed_fields",
    "fragment_refs",
    "dimensions",
    "levels",
    "sensitivity_policy_ref",
    "example_label_chains",
)

#: A payload carrying any of these is trying to publish shared logic from inside
#: one branch's model call. Rejected on sight, before any content is read.
FORBIDDEN_PUBLISHING_KEYS: tuple[str, ...] = (
    "fragment_definitions",
    "new_fragments",
    "publish_fragment",
    "canonical_fragments",
    "definitions",
    "applicabilities",
)


def _is_sequence(value: object) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes))


def _fragment_refs_are_published(payload: Mapping[str, object],
                                 catalogue: TemplateCatalogue) -> bool:
    refs = payload.get("fragment_refs")
    if not _is_sequence(refs):
        return False
    for ref in refs:
        if not isinstance(ref, Mapping):
            return False
        fragment_id = ref.get("fragment_id")
        fragment_version = ref.get("fragment_version")
        if not isinstance(fragment_id, str) or not fragment_id:
            return False
        if not isinstance(fragment_version, int) or isinstance(fragment_version, bool):
            return False
        if not catalogue.has_fragment(fragment_id, fragment_version):
            return False
    return True


def _dimensions_are_well_formed(payload: Mapping[str, object]) -> bool:
    dimensions = payload.get("dimensions")
    if not _is_sequence(dimensions) or not dimensions:
        return False
    allowed = payload.get("allowed_fields")
    if not _is_sequence(allowed) or not allowed:
        return False
    allowed_names = {name for name in allowed if isinstance(name, str)}
    if len(allowed_names) != len(list(allowed)):
        return False
    indices: list[int] = []
    for item in dimensions:
        if not isinstance(item, Mapping):
            return False
        name = item.get("name")
        if not isinstance(name, str) or name not in allowed_names:
            return False
        if not item.get("evidence_ref"):
            return False
        if item.get("requirement") not in DIMENSION_REQUIREMENTS:
            return False
        if not isinstance(item.get("metadata_only"), bool):
            return False
        index = item.get("order_index")
        if not isinstance(index, int) or isinstance(index, bool) or index < 0:
            return False
        indices.append(index)
    return len(set(indices)) == len(indices)


def _levels_are_well_formed(payload: Mapping[str, object]) -> bool:
    """P10 requires the KEY; P8's Site E judges its content.

    Site E downgrades a level with a falsy `retrieval_justification` to WEAK.
    Duplicating that judgement here would give one rule two homes and let the
    two disagree about the same response.
    """
    levels = payload.get("levels")
    if not _is_sequence(levels) or not levels:
        return False
    for level in levels:
        if not isinstance(level, Mapping):
            return False
        if "retrieval_justification" not in level:
            return False
        if not isinstance(level.get("dimension"), str):
            return False
    return True


def _examples_are_labels(payload: Mapping[str, object]) -> bool:
    chains = payload.get("example_label_chains")
    if not _is_sequence(chains):
        return False
    for chain in chains:
        if not _is_sequence(chain):
            return False
        for label in chain:
            if not isinstance(label, str) or not label:
                return False
            if any(sep in label for sep in _SEPARATORS):
                return False
    return True


def template_schema_validator(
        catalogue: TemplateCatalogue) -> Callable[[object], bool]:
    """The callable P8 calls. True means "this shape is legal", nothing more.

    A True here is not an approval, not an activation, and not a claim that the
    design is good. §5.7 is explicit that a technically valid template can still
    be a poor organization design, so semantic validation (V1-V6) and user
    approval both still stand between this and a node.
    """

    def validate(payload: object) -> bool:
        if not isinstance(payload, Mapping):
            return False
        if any(key in payload for key in FORBIDDEN_PUBLISHING_KEYS):
            return False
        if any(key not in payload for key in TEMPLATE_PAYLOAD_KEYS):
            return False
        domain = payload.get("domain")
        if not isinstance(domain, str) or not domain:
            return False
        if not isinstance(payload.get("sensitivity_policy_ref"), str):
            return False
        if not payload.get("sensitivity_policy_ref"):
            return False
        if not _fragment_refs_are_published(payload, catalogue):
            return False
        if not _dimensions_are_well_formed(payload):
            return False
        if not _levels_are_well_formed(payload):
            return False
        return _examples_are_labels(payload)

    return validate


def template_dependencies(catalogue: TemplateCatalogue) -> TemplateDependencies:
    """P8's record, carrying P10's callable. P10 constructs nothing else of P8's."""
    return TemplateDependencies(schema_validator=template_schema_validator(catalogue))


def allowed_vocabulary_for(catalogue: TemplateCatalogue, *,
                           uses_schema: str) -> tuple[str, ...]:
    """The closure P8's Site E checks every proposed dimension name against.

    It is the union of the allowed fields of the rows for ONE schema. Unioning
    across schemas here would widen a P6 allow-list at the dossier boundary,
    which is the one thing the one-row-one-schema rule exists to prevent.
    """
    fields: set[str] = set()
    for row in catalogue.rows_for_schema(uses_schema):
        fields.update(row.allowed_fields)
    return tuple(sorted(fields))


def build_template_request(*, subject_ref: str, plan_version: str,
                           evidence_items: Sequence[EvidenceItem],
                           conflicts: Sequence[Conflict],
                           model_call_request) -> DossierRequest:
    """The reference-only Site-E request. P10 builds this; P8 materialises.

    `E_template` is in P8's `SITES_REQUIRING_PLAN_VERSION`, so a request without
    one is refused by P8's own record — which is correct: §8.8 captures template
    versions and ordering choices per plan version, and a template call outside a
    version has nothing to attribute its result to.
    """
    return DossierRequest(
        call_site=E_TEMPLATE,
        subject_ref=subject_ref,
        eligibility_reason=ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE,
        evidence_items=tuple(evidence_items),
        conflicts=tuple(conflicts),
        model_call_request=model_call_request,
        plan_version=plan_version,
        evidence_snapshot_id=None,
        budget_context=None,
    )
```

- [ ] **Step 5: Run both and verify GREEN**

Run: `python3.12 -m pytest -q tests/p10/test_p10_template_schema.py tests/integration/test_p10_p8_template.py tests/p8/test_p8_template_validation.py`

Expected: PASS. P8's own Site-E suite is included because this task injects a stricter validator than P8's fixtures use, and P8's recorded pairs must keep passing with P8's own validator — the two are different callables for different purposes and neither may quietly become the other.

- [ ] **Step 6: Commit**

```bash
git add src/tree_design/template_schema.py tests/p10/test_p10_template_schema.py \
        tests/integration/test_p10_p8_template.py
git commit -m "feat(p10): own the Site E template schema and fragment boundary"
```

### Task 9: The six §5.7 engine checks, over real branch evidence

**Files:**
- Create: `src/tree_design/validation.py`
- Create: `tests/p10/test_p10_validation.py`

**Interfaces:**

*Consumes:* `tree_design.config.TreeLimits` / `ConfigurationRequired`, `tree_design.vocabulary.TEMPLATE_CHECKS`.

*Produces:*

```python
@dataclass(frozen=True)
class MaterialisedLevel:
    dimension_role: str
    field_ref: str
    order_index: int
    metadata_only: bool
    values: tuple[str, ...]
    members_by_value: Mapping[str, int]
    handling_classes_by_value: Mapping[str, frozenset[str]]

@dataclass(frozen=True)
class MaterialisedCandidate:
    branch_node_id: str
    ancestor_field_refs: tuple[str, ...]
    ancestor_depth: int
    levels: tuple[MaterialisedLevel, ...]
    member_file_ids: frozenset[str]

@dataclass(frozen=True)
class CheckFailure:
    check: str
    reason: str
    affected: tuple[str, ...]

@dataclass(frozen=True)
class ValidationReport:
    report_id: str
    passed: tuple[str, ...]
    failures: tuple[CheckFailure, ...]
    @property
    def accepted(self) -> bool: ...

def run_checks(candidate: MaterialisedCandidate, *, report_id: str,
               limits: TreeLimits, collector_field_keys: frozenset[str],
               protected_handling_classes: frozenset[str]) -> ValidationReport: ...
```

**Done-means:** the V1–V6 half of DM2(c) and the whole of DM7 (uneven depth passes) and DM5's data-backed explanations.

- [ ] **Step 1: Write one failing fixture per check**

```python
# tests/p10/test_p10_validation.py
"""P10 Task 9 — one failing fixture per §5.7 check, over a materialised branch.

These are P10's V1-V6. P1's V1-V4 are §8.2's checksum verification points and
share nothing with these but the letter.

The checks run over a candidate MATERIALISED against the branch's real values,
which is why they are P10's and not P8's: §5.7 places them on "the engine" that
validates a generated template against the accepted group, and the accepted
group is material only P10 holds.
"""
from __future__ import annotations

import pytest

from database_agent.budget import set_ceiling
from tree_design.config import ConfigurationRequired, tree_limits
from tree_design.validation import (
    MaterialisedCandidate,
    MaterialisedLevel,
    run_checks,
)


@pytest.fixture()
def limits(conn):
    set_ceiling(conn, "tree.max_folder_proposals_and_depth", 4)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    return tree_limits(
        conn, excessive_depth_warning=3, tiny_folder_max_files=2,
        tiny_folder_count_warning=8,
        materially_improves_retrieval=lambda preview: None)


def _level(role, field, index, values, counts=None, classes=None,
           metadata_only=False):
    return MaterialisedLevel(
        dimension_role=role, field_ref=field, order_index=index,
        values=tuple(values), metadata_only=metadata_only,
        members_by_value=dict(counts or {v: len(values) + 1 for v in values}),
        handling_classes_by_value=dict(
            classes or {v: frozenset({"personal_non_sensitive"}) for v in values}),
    )


def _candidate(levels, *, ancestors=(), depth=0, members=("f1", "f2", "f3")):
    return MaterialisedCandidate(
        branch_node_id="n_branch", ancestor_field_refs=tuple(ancestors),
        ancestor_depth=depth, levels=tuple(levels),
        member_file_ids=frozenset(members),
    )


CHECK_ARGS = dict(
    collector_field_keys=frozenset({"target_school", "client", "authored_by"}),
    protected_handling_classes=frozenset({
        "sensitive_personal", "highly_sensitive_credential_bearing"}),
)


def test_a_healthy_candidate_passes_all_six(limits):
    candidate = _candidate([
        _level("subject", "subject", 0, ("PHYS1401", "CHEM1101")),
        _level("artifact_kind", "work_type", 1, ("Homework", "Exam")),
    ])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert report.accepted
    assert report.passed == ("V1", "V2", "V3", "V4", "V5", "V6")


def test_v1_a_level_repeating_a_parent_dimension_fails(limits):
    candidate = _candidate(
        [_level("subject", "subject", 0, ("PHYS1401", "CHEM1101"))],
        ancestors=("subject",), depth=1)
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert not report.accepted
    assert [f.check for f in report.failures] == ["V1"]
    assert "subject" in report.failures[0].affected


def test_v1_also_catches_a_repeat_within_the_candidate_itself(limits):
    candidate = _candidate([
        _level("subject", "subject", 0, ("PHYS1401", "CHEM1101")),
        _level("course", "subject", 1, ("PHYS1401", "CHEM1101")),
    ])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert [f.check for f in report.failures] == ["V1"]


def test_v2_a_level_producing_exactly_one_child_is_meaningless(limits):
    candidate = _candidate([_level("subject", "subject", 0, ("PHYS1401",))])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert [f.check for f in report.failures] == ["V2"]
    assert "PHYS1401" in report.failures[0].reason


def test_v3_depth_is_measured_against_configuration_never_a_constant(limits):
    levels = [_level(f"r{i}", f"f{i}", i, (f"a{i}", f"b{i}")) for i in range(4)]
    candidate = _candidate(levels, ancestors=("root",), depth=2)
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert [f.check for f in report.failures] == ["V3"]
    assert str(limits.max_folder_proposals_and_depth) in report.failures[0].reason


def test_v3_cannot_run_without_a_configured_depth(conn):
    """SPEC open question 1: §5.7 forbids exceeding "practical depth limits" and
    no value is given. The check is unimplementable until one is set, and this
    is what "unimplementable" looks like — a refusal, not a guess."""
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    with pytest.raises(ConfigurationRequired):
        tree_limits(conn, excessive_depth_warning=3, tiny_folder_max_files=2,
                    tiny_folder_count_warning=8,
                    materially_improves_retrieval=lambda p: None)


def test_v4_an_organization_used_merely_as_a_collector_fails(limits):
    """§3.8: "A folder should not become a collection point for everything
    produced by the same person or organization." A branch whose only level is
    such a role is exactly that collection point."""
    candidate = _candidate(
        [_level("counterpart", "target_school", 0, ("Columbia", "Duke"))])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert [f.check for f in report.failures] == ["V4"]


def test_v4_permits_a_collector_role_that_is_not_the_whole_branch(limits):
    candidate = _candidate([
        _level("counterpart", "target_school", 0, ("Columbia", "Duke")),
        _level("document_kind", "application_document_type", 1,
               ("Essay", "Transcript")),
    ])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert report.accepted


def test_v4_needs_the_collector_set_and_invents_none(limits):
    candidate = _candidate(
        [_level("counterpart", "target_school", 0, ("Columbia", "Duke"))])
    with pytest.raises(ConfigurationRequired):
        run_checks(candidate, report_id="vr_1", limits=limits,
                   collector_field_keys=frozenset(),
                   protected_handling_classes=CHECK_ARGS["protected_handling_classes"])


def test_v5_a_folder_level_built_from_protected_values_fails(limits):
    candidate = _candidate([
        _level("subject", "subject", 0, ("PHYS1401", "CHEM1101")),
        _level("account", "account_identifier", 1, ("4471", "9920"), classes={
            "4471": frozenset({"highly_sensitive_credential_bearing"}),
            "9920": frozenset({"personal_non_sensitive"}),
        }),
    ])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert [f.check for f in report.failures] == ["V5"]
    assert "4471" in report.failures[0].affected


def test_v5_permits_a_metadata_only_role_over_the_same_values(limits):
    """§5.4: a metadata-only role never becomes a folder level, so it cannot put
    a protected value in a folder name."""
    candidate = _candidate([
        _level("subject", "subject", 0, ("PHYS1401", "CHEM1101")),
        _level("account", "account_identifier", 1, ("4471",), metadata_only=True,
               classes={"4471": frozenset({"highly_sensitive_credential_bearing"})}),
    ])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert report.accepted


def test_v6_a_value_with_no_member_is_an_empty_branch(limits):
    candidate = _candidate([
        _level("subject", "subject", 0, ("PHYS1401", "CHEM1101", "BIOL2000"),
               counts={"PHYS1401": 4, "CHEM1101": 2, "BIOL2000": 0}),
    ])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert [f.check for f in report.failures] == ["V6"]
    assert report.failures[0].affected == ("BIOL2000",)


def test_uneven_depth_is_never_a_failure(limits):
    """§5.8: no validation rule may require sibling subtrees to have equal
    depth, and no branch is required to realise every dimension of its
    template."""
    shallow = _candidate([_level("subject", "subject", 0, ("PHYS1401", "CHEM1101"))])
    deep = _candidate([
        _level("subject", "subject", 0, ("PHYS1401", "CHEM1101")),
        _level("artifact_kind", "work_type", 1, ("Homework", "Exam")),
    ])
    assert run_checks(shallow, report_id="a", limits=limits, **CHECK_ARGS).accepted
    assert run_checks(deep, report_id="b", limits=limits, **CHECK_ARGS).accepted


def test_internal_heterogeneity_alone_is_never_a_rejection(limits):
    """§5.6: "The template is a recommendation mechanism, not a rule that erases
    purposeful heterogeneity." A purpose packet holding a transcript, an ID, an
    essay and a certificate is a valid branch."""
    candidate = _candidate([
        _level("document_kind", "application_document_type", 0,
               ("Transcript", "ID", "Personal statement", "Certificate")),
    ], members=("t", "i", "p", "c"))
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert report.accepted


def test_every_failure_names_its_evidence_and_carries_no_score(limits):
    candidate = _candidate([_level("subject", "subject", 0, ("PHYS1401",))])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    failure = report.failures[0]
    assert failure.reason and failure.affected
    assert not any(
        token in failure.reason.lower()
        for token in ("confidence", "score", "probability", "%")
    )
```

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p10/test_p10_validation.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'tree_design.validation'`.

- [ ] **Step 3: Write the checks**

```python
# src/tree_design/validation.py
"""§5.7's six engine checks, run against the branch's actual values.

These are design-quality checks, not shape checks. P8 already enforced the
response shape and returned a verdict; §5.7 is explicit that a template "cannot
... become active merely because it is syntactically valid", so a clean P8
verdict arrives here and can still fail.

Each check answers one question about the tree the candidate WOULD produce, and
each failure names the values that produced it. No check returns a score: §5.2
requires an explanation "rather than a technical confidence score", and a check
that reported 0.72 would be exactly that.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from tree_design.config import ConfigurationRequired, TreeLimits
from tree_design.vocabulary import TEMPLATE_CHECKS


@dataclass(frozen=True)
class MaterialisedLevel:
    """One proposed level, with the real values the branch's evidence supplies."""

    dimension_role: str
    field_ref: str
    order_index: int
    metadata_only: bool
    values: tuple[str, ...]
    members_by_value: Mapping[str, int]
    handling_classes_by_value: Mapping[str, frozenset[str]]


@dataclass(frozen=True)
class MaterialisedCandidate:
    branch_node_id: str
    ancestor_field_refs: tuple[str, ...]
    ancestor_depth: int
    levels: tuple[MaterialisedLevel, ...]
    member_file_ids: frozenset[str]


@dataclass(frozen=True)
class CheckFailure:
    check: str
    reason: str
    affected: tuple[str, ...]


@dataclass(frozen=True)
class ValidationReport:
    report_id: str
    passed: tuple[str, ...]
    failures: tuple[CheckFailure, ...]

    @property
    def accepted(self) -> bool:
        return not self.failures


def _v1(candidate: MaterialisedCandidate) -> CheckFailure | None:
    """Repeats a parent dimension.

    The comparison is on `field_ref`, not on the role name: two roles that
    resolve to one field produce one level's worth of meaning twice, and the
    role names would hide it.
    """
    seen = list(candidate.ancestor_field_refs)
    for level in candidate.levels:
        if level.metadata_only:
            continue
        if level.field_ref in seen:
            return CheckFailure(
                "V1",
                f"level {level.dimension_role!r} splits by {level.field_ref!r}, "
                "which an ancestor or an earlier level already expresses; the "
                "second level adds a folder and no meaning",
                (level.field_ref,),
            )
        seen.append(level.field_ref)
    return None


def _v2(candidate: MaterialisedCandidate) -> CheckFailure | None:
    """Creates meaningless one-child levels."""
    for level in candidate.levels:
        if level.metadata_only:
            continue
        if len(level.values) == 1:
            only = level.values[0]
            return CheckFailure(
                "V2",
                f"level {level.dimension_role!r} produces one child, {only!r}; a "
                "level with a single child is a folder the user opens to find one "
                "folder",
                (only,),
            )
    return None


def _v3(candidate: MaterialisedCandidate,
        limits: TreeLimits) -> CheckFailure | None:
    """Exceeds practical depth limits.

    The number is `tree.max_folder_proposals_and_depth`, read from P1. §5.7 and
    §8.6 both decline to state one, so there is nothing to hard-code.
    """
    folder_levels = [level for level in candidate.levels if not level.metadata_only]
    depth = candidate.ancestor_depth + len(folder_levels)
    if depth > limits.max_folder_proposals_and_depth:
        return CheckFailure(
            "V3",
            f"the candidate reaches depth {depth}, above the configured "
            f"{limits.max_folder_proposals_and_depth}",
            tuple(level.dimension_role for level in folder_levels),
        )
    return None


def _v4(candidate: MaterialisedCandidate,
        collector_field_keys: frozenset[str]) -> CheckFailure | None:
    """Uses an author or organization merely as a collector.

    §3.8: "A folder should not become a collection point for everything produced
    by the same person or organization." A collector role beside another level is
    fine — `Applications/Columbia/Essays` is useful. A branch whose ONLY level is
    a collector is the failure.
    """
    if not collector_field_keys:
        raise ConfigurationRequired(
            "V4 needs §3.8's set of author/organization field keys. P6 owns "
            "which fields those are, and a set P10 guessed would either miss a "
            "collector or reject a legitimate counterpart level."
        )
    folder_levels = [level for level in candidate.levels if not level.metadata_only]
    if len(folder_levels) == 1 and folder_levels[0].field_ref in collector_field_keys:
        level = folder_levels[0]
        return CheckFailure(
            "V4",
            f"the branch's only level is {level.field_ref!r}, an author or "
            "organization role; the branch would collect everything from the same "
            "counterpart with no further meaning",
            (level.field_ref,),
        )
    return None


def _v5(candidate: MaterialisedCandidate,
        protected_handling_classes: frozenset[str]) -> CheckFailure | None:
    """Exposes protected information.

    A folder name is visible in the filesystem and in every prompt that names a
    destination, so a level whose values come from protected material publishes
    that material. A metadata-only role over the same values does not, which is
    exactly what §5.4's `metadata_only` is for.
    """
    if not protected_handling_classes:
        raise ConfigurationRequired(
            "V5 needs the set of handling classes that count as protected. P7 "
            "supplies `protected` and does not derive it from the class, and "
            "whether protected is exactly the top two classes is P7's own open "
            "question."
        )
    exposed: list[str] = []
    for level in candidate.levels:
        if level.metadata_only:
            continue
        for value in level.values:
            classes = level.handling_classes_by_value.get(value, frozenset())
            if classes & protected_handling_classes:
                exposed.append(value)
    if exposed:
        return CheckFailure(
            "V5",
            "these values would become folder names while carrying a protected "
            "handling class; a folder name is visible material",
            tuple(exposed),
        )
    return None


def _v6(candidate: MaterialisedCandidate) -> CheckFailure | None:
    """Produces empty branches when tested against the accepted group."""
    empty = [
        value
        for level in candidate.levels if not level.metadata_only
        for value in level.values
        if level.members_by_value.get(value, 0) == 0
    ]
    if empty:
        return CheckFailure(
            "V6",
            "these levels have no member in the accepted group, so the branch "
            "would be created empty",
            tuple(empty),
        )
    return None


def run_checks(candidate: MaterialisedCandidate, *, report_id: str,
               limits: TreeLimits, collector_field_keys: frozenset[str],
               protected_handling_classes: frozenset[str]) -> ValidationReport:
    """All six, in order, collecting every failure rather than stopping at one.

    Stopping at the first failure would make the user fix one problem, re-run,
    and find the next — which is how a review surface teaches someone that the
    product cannot be trusted to tell them what is wrong.
    """
    outcomes = {
        "V1": _v1(candidate),
        "V2": _v2(candidate),
        "V3": _v3(candidate, limits),
        "V4": _v4(candidate, collector_field_keys),
        "V5": _v5(candidate, protected_handling_classes),
        "V6": _v6(candidate),
    }
    failures = tuple(
        outcomes[check] for check in TEMPLATE_CHECKS if outcomes[check] is not None
    )
    passed = tuple(check for check in TEMPLATE_CHECKS if outcomes[check] is None)
    return ValidationReport(report_id=report_id, passed=passed, failures=failures)
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3.12 -m pytest -q tests/p10/test_p10_validation.py`

Expected: PASS, fifteen tests. Note that `test_v1_a_level_repeating_a_parent_dimension_fails` asserts exactly `["V1"]` — the other five must pass on that fixture, which is what makes each check independently falsifiable rather than a single combined verdict.

- [ ] **Step 5: Commit**

```bash
git add src/tree_design/validation.py tests/p10/test_p10_validation.py
git commit -m "feat(p10): run the six template design checks over real evidence"
```

### Task 10: The residual library, and the nodes it does not create

**Files:**
- Create: `src/tree_design/residuals.py`
- Create: `tests/p10/test_p10_residuals.py`

**Interfaces:**

*Consumes:* `tree_design.vocabulary` (`RESIDUAL_TEMPLATE_NAMES`, `RESIDUAL_DEFAULT_PARENTS`, `RESIDUAL_SLOTS`, `RESIDUAL_TREATMENTS`, `RESIDUAL_ACTIONS`, `RESIDUAL_DISPOSITIONS`, `RESIDUAL`), `tree_design.records.Node`, `tree_design.config.ConfigurationRequired`.

*Produces:*

```python
@dataclass(frozen=True)
class ResidualTemplate:
    template_name: str
    display_name: str
    default_parent_location: tuple[str, ...] | None
    accepted_evidence_patterns: tuple[str, ...]
    expected_file_types: tuple[str, ...]
    sensitivity_restrictions: tuple[str, ...]
    optional_shallow_subfolders: tuple[str, ...]
    max_permitted_depth: int
    treatment: str
    user_defined: bool

@dataclass(frozen=True)
class ResidualChoice:
    template_name: str
    action: str
    disposition: str | None
    display_label: str | None
    parent_node_id: str | None
    root_anchor: str | None
    merge_into: str | None
    replaces_node_id: str | None

def build_library(slot_values: Mapping[str, Mapping[str, object]], *,
                  user_defined: Sequence[ResidualTemplate] = ()) -> Mapping[str, ResidualTemplate]: ...
def project_residual_nodes(library, choices, *, plan_version_id: str,
                           handling_class_for_template, mint_node_id,
                           existing_nodes) -> tuple[Node, ...]: ...
```

**Done-means:** DM2(e) (the residual-library fixture), DM12 (a disabled residual template is unreachable), and the residual half of DM1.

- [ ] **Step 1: Write the failing residual tests**

```python
# tests/p10/test_p10_residuals.py
"""P10 Task 10 — nine fixed names, eight slots, and the nodes that never exist.

§7.2 names the failure this library prevents: the LLM creating arbitrary folders
such as `Random PDF Things`, `Important Screenshot`, `Miscellaneous Documents`,
or `Travel/Gate B12`, which "may sound plausible but would fragment the user's
filesystem and create unmaintainable structure". A residual template is a
CONSTRAINT on the model's choices, not a suggestion.

The enforcement mechanism is a single sentence long: a template the user did not
enable has no node, so no placement decision can name it and no model can return
it. Everything else here is bookkeeping around that.
"""
from __future__ import annotations

import pytest

from tree_design.config import ConfigurationRequired
from tree_design.records import Node
from tree_design.residuals import (
    ResidualChoice,
    ResidualTemplate,
    build_library,
    project_residual_nodes,
)
from tree_design.vocabulary import (
    DISABLE,
    ENABLE,
    LEAVE_IN_PLACE,
    MERGE_RESIDUAL,
    PHYSICAL_DESTINATION,
    RELOCATE,
    RENAME_RESIDUAL,
    REPLACE_WITH_EXISTING,
    RESIDUAL,
    RESIDUAL_DEFAULT_PARENTS,
    RESIDUAL_SLOTS,
    RESIDUAL_TEMPLATE_NAMES,
    REVIEW_ONLY,
    TREATMENT_RETAINED,
    TREATMENT_REVIEWED,
)

SLOTS = {
    name: {
        "display_name": name,
        "default_parent_location": RESIDUAL_DEFAULT_PARENTS.get(name),
        "accepted_evidence_patterns": ("pattern.fixture",),
        "expected_file_types": ("image/png",),
        "sensitivity_restrictions": (),
        "optional_shallow_subfolders": (),
        "max_permitted_depth": 1,
        "treatment": TREATMENT_REVIEWED,
    }
    for name in RESIDUAL_TEMPLATE_NAMES
}


def _ids():
    counter = iter(range(len(RESIDUAL_TEMPLATE_NAMES) * 2))
    return lambda: f"n_res_{next(counter)}"


def _classes(name):
    return "sensitive_personal" if name == "Protected Records" else "personal_non_sensitive"


def test_the_library_holds_exactly_the_nine_and_every_one_defines_eight_slots():
    library = build_library(SLOTS)
    assert tuple(library) == RESIDUAL_TEMPLATE_NAMES
    for template in library.values():
        for slot in RESIDUAL_SLOTS:
            assert hasattr(template, slot), slot


def test_only_the_first_four_have_a_stated_default_parent():
    """§7.3 states a default parent location for four templates. The remaining
    five have none stated, and inventing one would be P10 authoring §7.3."""
    library = build_library(SLOTS)
    stated = {n for n, t in library.items() if t.default_parent_location is not None}
    assert stated == {
        "Temporary Screenshots", "One-Off Images", "Reference Clips",
        "Independent Records",
    }
    assert library["Review Later"].default_parent_location is None


def test_a_default_parent_is_a_label_chain_and_never_a_path():
    library = build_library(SLOTS)
    assert library["Temporary Screenshots"].default_parent_location == (
        "Photos", "Temporary Screenshots")
    for template in library.values():
        for label in template.default_parent_location or ():
            assert "/" not in label and "\\" not in label


def test_a_missing_slot_value_refuses_rather_than_defaulting():
    for slot in RESIDUAL_SLOTS:
        if slot == "default_parent_location":
            continue  # None is a real value for five of the nine
        broken = {name: dict(values) for name, values in SLOTS.items()}
        del broken["Review Later"][slot]
        with pytest.raises(ConfigurationRequired) as excinfo:
            build_library(broken)
        assert slot in str(excinfo.value)


def test_the_product_ships_no_user_defined_residual_area():
    """§7.3 requires the library to SUPPORT user-defined areas such as Things to
    Read, Ideas, Shopping Research, Memes, Travel, Receipts to Process, Clips or
    Stuff to Sort, "because residual organization is highly personal and should
    not be dictated by a universal taxonomy". Those are illustrations of user
    freedom; the product ships none of them."""
    library = build_library(SLOTS)
    assert not any(t.user_defined for t in library.values())
    for illustration in ("Things to Read", "Ideas", "Shopping Research", "Memes",
                         "Travel", "Receipts to Process", "Clips", "Stuff to Sort"):
        assert illustration not in library


def test_a_user_defined_area_joins_the_library_with_the_same_eight_slots():
    mine = ResidualTemplate(
        template_name="Shopping Research", display_name="Shopping Research",
        default_parent_location=None, accepted_evidence_patterns=("pattern.user",),
        expected_file_types=("text/html",), sensitivity_restrictions=(),
        optional_shallow_subfolders=(), max_permitted_depth=1,
        treatment=TREATMENT_RETAINED, user_defined=True,
    )
    library = build_library(SLOTS, user_defined=(mine,))
    assert library["Shopping Research"].user_defined
    assert len(library) == len(RESIDUAL_TEMPLATE_NAMES) + 1


def test_a_disabled_template_creates_no_node(conn):
    library = build_library(SLOTS)
    choices = tuple(
        ResidualChoice(template_name=name, action=DISABLE, disposition=None,
                       display_label=None, parent_node_id=None, root_anchor=None,
                       merge_into=None, replaces_node_id=None)
        for name in RESIDUAL_TEMPLATE_NAMES
    )
    nodes = project_residual_nodes(
        library, choices, plan_version_id="plan_1",
        handling_class_for_template=_classes, mint_node_id=_ids(),
        existing_nodes={})
    assert nodes == ()


def test_an_enabled_template_becomes_an_ordinary_residual_node(conn):
    library = build_library(SLOTS)
    choices = (ResidualChoice(
        template_name="Review Later", action=ENABLE,
        disposition=PHYSICAL_DESTINATION, display_label=None,
        parent_node_id=None, root_anchor="root_documents", merge_into=None,
        replaces_node_id=None),)
    node, = project_residual_nodes(
        library, choices, plan_version_id="plan_1",
        handling_class_for_template=_classes, mint_node_id=_ids(),
        existing_nodes={})
    assert isinstance(node, Node)
    assert node.node_role == RESIDUAL
    assert node.disposition == PHYSICAL_DESTINATION
    assert node.accepts_placement is True
    assert node.display_label == "Review Later"
    assert node.existing_path is None


def test_rename_changes_the_label_and_not_the_template_identity(conn):
    library = build_library(SLOTS)
    choices = (ResidualChoice(
        template_name="Review Later", action=RENAME_RESIDUAL,
        disposition=REVIEW_ONLY, display_label="To Triage",
        parent_node_id=None, root_anchor="root_documents", merge_into=None,
        replaces_node_id=None),)
    node, = project_residual_nodes(
        library, choices, plan_version_id="plan_1",
        handling_class_for_template=_classes, mint_node_id=_ids(),
        existing_nodes={})
    assert node.display_label == "To Triage"
    assert library["Review Later"].template_name == "Review Later"


def test_relocate_moves_the_node_off_the_templates_default_parent(conn):
    library = build_library(SLOTS)
    choices = (ResidualChoice(
        template_name="Temporary Screenshots", action=RELOCATE,
        disposition=PHYSICAL_DESTINATION, display_label=None,
        parent_node_id="n_desktop", root_anchor="root_desktop", merge_into=None,
        replaces_node_id=None),)
    node, = project_residual_nodes(
        library, choices, plan_version_id="plan_1",
        handling_class_for_template=_classes, mint_node_id=_ids(),
        existing_nodes={})
    assert node.parent_node_id == "n_desktop"
    assert node.root_anchor == "root_desktop"


def test_two_merged_templates_resolve_to_one_node(conn):
    library = build_library(SLOTS)
    choices = (
        ResidualChoice(template_name="Reading Inbox", action=ENABLE,
                       disposition=REVIEW_ONLY, display_label=None,
                       parent_node_id=None, root_anchor="root_documents",
                       merge_into=None, replaces_node_id=None),
        ResidualChoice(template_name="Review Later", action=MERGE_RESIDUAL,
                       disposition=REVIEW_ONLY, display_label=None,
                       parent_node_id=None, root_anchor="root_documents",
                       merge_into="Reading Inbox", replaces_node_id=None),
    )
    nodes = project_residual_nodes(
        library, choices, plan_version_id="plan_1",
        handling_class_for_template=_classes, mint_node_id=_ids(),
        existing_nodes={})
    assert len(nodes) == 1
    assert nodes[0].display_label == "Reading Inbox"


def test_replace_with_existing_maps_review_later_onto_an_existing_to_sort(conn):
    """§7.4's own case: a user who "already has an existing `To Sort` folder"
    gets Review Later mapped onto it "rather than inventing a new one"."""
    library = build_library(SLOTS)
    existing = Node(
        node_id="n_to_sort", plan_version_id="plan_1", node_type="existing",
        display_label="To Sort", parent_node_id=None,
        root_anchor="root_documents", ordinal=0, associated_group_ids=(),
        explanation="An existing folder the scan found, with 42 files.",
        node_role="ordinary", accepts_placement=True,
        handling_class="personal_non_sensitive", origin_node_id="n_to_sort",
        existing_path="/Users/jy/Documents/To Sort",
    )
    choices = (ResidualChoice(
        template_name="Review Later", action=REPLACE_WITH_EXISTING,
        disposition=PHYSICAL_DESTINATION, display_label=None,
        parent_node_id=None, root_anchor=None, merge_into=None,
        replaces_node_id="n_to_sort"),)
    node, = project_residual_nodes(
        library, choices, plan_version_id="plan_1",
        handling_class_for_template=_classes, mint_node_id=_ids(),
        existing_nodes={"n_to_sort": existing})
    assert node.node_id == "n_to_sort"
    assert node.node_type == "existing"
    assert node.node_role == RESIDUAL
    assert node.existing_path == "/Users/jy/Documents/To Sort"


def test_all_three_dispositions_reach_a_node(conn):
    library = build_library(SLOTS)
    choices = (
        ResidualChoice("Receipts and Confirmations", ENABLE, PHYSICAL_DESTINATION,
                       None, None, "root_documents", None, None),
        ResidualChoice("Reading Inbox", ENABLE, REVIEW_ONLY, None, None,
                       "root_documents", None, None),
        ResidualChoice("Unsupported or Encrypted", ENABLE, LEAVE_IN_PLACE, None,
                       None, "root_documents", None, None),
    )
    nodes = project_residual_nodes(
        library, choices, plan_version_id="plan_1",
        handling_class_for_template=_classes, mint_node_id=_ids(),
        existing_nodes={})
    assert {n.disposition for n in nodes} == {
        PHYSICAL_DESTINATION, REVIEW_ONLY, LEAVE_IN_PLACE}


def test_an_enabled_template_without_a_disposition_is_refused(conn):
    library = build_library(SLOTS)
    choices = (ResidualChoice("Review Later", ENABLE, None, None, None,
                              "root_documents", None, None),)
    with pytest.raises(ConfigurationRequired):
        project_residual_nodes(
            library, choices, plan_version_id="plan_1",
            handling_class_for_template=_classes, mint_node_id=_ids(),
            existing_nodes={})


def test_protected_records_carries_its_class_onto_the_node(conn):
    """§7.3 and §8.4: Protected Records "should normally remain local-only and
    must not cause filenames or content to be exposed in model prompts". That is
    expressed through the node's handling class, not through special-casing in
    P11."""
    library = build_library(SLOTS)
    choices = (ResidualChoice("Protected Records", ENABLE, REVIEW_ONLY, None,
                              None, "root_documents", None, None),)
    node, = project_residual_nodes(
        library, choices, plan_version_id="plan_1",
        handling_class_for_template=_classes, mint_node_id=_ids(),
        existing_nodes={})
    assert node.handling_class == "sensitive_personal"


def test_a_choice_naming_a_template_the_library_does_not_hold_is_refused(conn):
    library = build_library(SLOTS)
    choices = (ResidualChoice("Random PDF Things", ENABLE, PHYSICAL_DESTINATION,
                              None, None, "root_documents", None, None),)
    with pytest.raises(ConfigurationRequired) as excinfo:
        project_residual_nodes(
            library, choices, plan_version_id="plan_1",
            handling_class_for_template=_classes, mint_node_id=_ids(),
            existing_nodes={})
    assert "Random PDF Things" in str(excinfo.value)
```

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p10/test_p10_residuals.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'tree_design.residuals'`.

- [ ] **Step 3: Write the residual library**

```python
# src/tree_design/residuals.py
"""§7.2-§7.4: the definitions and the enablement model. P11 runs the workflow.

A residual template is not a domain template. A domain template builds a deep
meaningful hierarchy for a recurring area of life; a residual template provides a
"safe, intentionally broad destination" for a file with no reliable deeper
association. §7.2 names the failure it prevents by example: `Random PDF Things`,
`Important Screenshot`, `Miscellaneous Documents`, `Travel/Gate B12`.

The nine names are fixed. Their slot VALUES are deferred and arrive injected: the
accepted evidence patterns, expected file types, sensitivity restrictions,
optional shallow subfolders and maximum depth per template, plus the five default
parent locations §7.3 leaves unstated. None is invented here.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from tree_design.config import ConfigurationRequired
from tree_design.records import Node
from tree_design.vocabulary import (
    DISABLE,
    ENABLE,
    MERGE_RESIDUAL,
    RELOCATE,
    RENAME_RESIDUAL,
    REPLACE_WITH_EXISTING,
    RESIDUAL,
    RESIDUAL_ACTIONS,
    RESIDUAL_DEFAULT_PARENTS,
    RESIDUAL_DISPOSITIONS,
    RESIDUAL_SLOTS,
    RESIDUAL_TEMPLATE_NAMES,
    RESIDUAL_TREATMENTS,
    check,
)

#: The five actions that put a node in the tree. `disable` is the sixth and is
#: the whole enforcement mechanism: no node, so nothing can name it.
_CREATING_ACTIONS: frozenset[str] = frozenset({
    ENABLE, RENAME_RESIDUAL, RELOCATE, MERGE_RESIDUAL, REPLACE_WITH_EXISTING,
})


@dataclass(frozen=True)
class ResidualTemplate:
    """§7.2's eight attribute slots, all eight, for one template."""

    template_name: str
    display_name: str
    default_parent_location: tuple[str, ...] | None
    accepted_evidence_patterns: tuple[str, ...]
    expected_file_types: tuple[str, ...]
    sensitivity_restrictions: tuple[str, ...]
    optional_shallow_subfolders: tuple[str, ...]
    max_permitted_depth: int
    treatment: str
    user_defined: bool

    def __post_init__(self) -> None:
        check(self.treatment, RESIDUAL_TREATMENTS, name="treatment")
        if not self.display_name:
            raise ConfigurationRequired(
                f"{self.template_name!r} has no display name; §7.2 makes the "
                "recommended display name one of the eight slots"
            )
        for label in self.default_parent_location or ():
            if "/" in label or "\\" in label:
                raise ConfigurationRequired(
                    "a default parent location is a `display_label` chain — a "
                    "recommended placement in the TREE, not on disk (resolution "
                    "B3). Nothing about a residual node makes it path-bearing."
                )


@dataclass(frozen=True)
class ResidualChoice:
    """One §7.4 decision the user made about one template."""

    template_name: str
    action: str
    disposition: str | None
    display_label: str | None
    parent_node_id: str | None
    root_anchor: str | None
    merge_into: str | None
    replaces_node_id: str | None

    def __post_init__(self) -> None:
        check(self.action, RESIDUAL_ACTIONS, name="residual action")


def build_library(
    slot_values: Mapping[str, Mapping[str, object]],
    *,
    user_defined: Sequence[ResidualTemplate] = (),
) -> Mapping[str, ResidualTemplate]:
    """The nine, plus whatever residual areas this user authored.

    `default_parent_location` is the one slot whose absence is legal: §7.3 states
    a default for four templates and leaves five unstated, so `None` is a value
    rather than a gap. Every other slot missing is a configuration gap.
    """
    library: dict[str, ResidualTemplate] = {}
    for name in RESIDUAL_TEMPLATE_NAMES:
        values = slot_values.get(name)
        if values is None:
            raise ConfigurationRequired(
                f"the residual library has no slot values for {name!r}. §7.3 fixes "
                "the nine names; their contents are authored and none is invented."
            )
        missing = [
            slot for slot in RESIDUAL_SLOTS
            if slot != "default_parent_location" and slot not in values
        ]
        if missing:
            raise ConfigurationRequired(
                f"{name!r} is missing the slot value(s) {sorted(missing)}. §7.2 "
                "defines eight attributes per template and P10 authors none of "
                "their contents."
            )
        parent = values.get("default_parent_location",
                            RESIDUAL_DEFAULT_PARENTS.get(name))
        library[name] = ResidualTemplate(
            template_name=name,
            display_name=str(values["display_name"]),
            default_parent_location=None if parent is None else tuple(parent),
            accepted_evidence_patterns=tuple(values["accepted_evidence_patterns"]),
            expected_file_types=tuple(values["expected_file_types"]),
            sensitivity_restrictions=tuple(values["sensitivity_restrictions"]),
            optional_shallow_subfolders=tuple(values["optional_shallow_subfolders"]),
            max_permitted_depth=int(values["max_permitted_depth"]),
            treatment=str(values["treatment"]),
            user_defined=False,
        )
    for template in user_defined:
        if not template.user_defined:
            raise ConfigurationRequired(
                f"{template.template_name!r} is offered as a user-defined area but "
                "is not marked as one; the product ships none of §7.3's example "
                "areas and the flag is how a shipped template is told from an "
                "authored one"
            )
        library[template.template_name] = template
    return library


def project_residual_nodes(
    library: Mapping[str, ResidualTemplate],
    choices: Sequence[ResidualChoice],
    *,
    plan_version_id: str,
    handling_class_for_template: Callable[[str], str],
    mint_node_id: Callable[[], str],
    existing_nodes: Mapping[str, Node],
) -> tuple[Node, ...]:
    """Turn the user's §7.4 decisions into nodes. Disabled decisions into none.

    §7.4: "Once the user approves the desired residual branches, those branches
    become legal nodes in the frozen destination tree. The LLM may choose among
    them later, but it may not create additional generic destinations." An
    enabled residual branch is an ordinary member of the legal set through the
    ordinary `accepts_placement` derivation — P11 needs no residual-specific
    legality path — and a template the user did not enable has no node at all.
    """
    nodes: list[Node] = []
    by_name: dict[str, Node] = {}
    ordinal = 0

    for choice in choices:
        template = library.get(choice.template_name)
        if template is None:
            raise ConfigurationRequired(
                f"{choice.template_name!r} is not in the residual library. §7.2 "
                "exists to stop exactly this: a plausible-sounding destination "
                "nobody defined."
            )
        if choice.action == DISABLE:
            continue
        if choice.action not in _CREATING_ACTIONS:
            continue
        if choice.disposition is None:
            raise ConfigurationRequired(
                f"{choice.template_name!r} is enabled without a disposition. §7.4 "
                "makes the user decide whether a residual template is a real "
                "physical destination, a review-only category, or a policy to "
                "leave files in place, and the three behave differently in P11."
            )
        check(choice.disposition, RESIDUAL_DISPOSITIONS, name="disposition")

        if choice.action == MERGE_RESIDUAL:
            target = by_name.get(choice.merge_into or "")
            if target is None:
                raise ConfigurationRequired(
                    f"{choice.template_name!r} merges into "
                    f"{choice.merge_into!r}, which is not an enabled residual "
                    "branch in this plan version"
                )
            by_name[choice.template_name] = target
            continue

        label = choice.display_label or template.display_name
        handling_class = handling_class_for_template(choice.template_name)

        if choice.action == REPLACE_WITH_EXISTING:
            existing = existing_nodes.get(choice.replaces_node_id or "")
            if existing is None:
                raise ConfigurationRequired(
                    f"{choice.template_name!r} replaces node "
                    f"{choice.replaces_node_id!r}, which is not an existing node "
                    "in this plan version"
                )
            node = Node(
                node_id=existing.node_id,
                plan_version_id=plan_version_id,
                node_type=existing.node_type,
                display_label=choice.display_label or existing.display_label,
                parent_node_id=existing.parent_node_id,
                root_anchor=existing.root_anchor,
                ordinal=existing.ordinal,
                associated_group_ids=existing.associated_group_ids,
                explanation=(
                    f"The user mapped the {choice.template_name!r} residual "
                    f"template onto their existing {existing.display_label!r} "
                    "folder rather than creating a new one."
                ),
                node_role=RESIDUAL,
                accepts_placement=existing.accepts_placement,
                handling_class=existing.handling_class,
                origin_node_id=existing.origin_node_id,
                existing_path=existing.existing_path,
                disposition=choice.disposition,
                protected_movement_permitted=existing.protected_movement_permitted,
            )
        else:
            parent_labels = template.default_parent_location or ()
            node = Node(
                node_id=mint_node_id(),
                plan_version_id=plan_version_id,
                node_type="user-created",
                display_label=label,
                parent_node_id=choice.parent_node_id,
                root_anchor=choice.root_anchor or "",
                ordinal=ordinal,
                associated_group_ids=(),
                explanation=(
                    f"The user enabled the {choice.template_name!r} residual "
                    f"template as a {choice.disposition} destination"
                    + (f", recommended under {' / '.join(parent_labels)}."
                       if parent_labels else ".")
                ),
                node_role=RESIDUAL,
                accepts_placement=True,
                handling_class=handling_class,
                origin_node_id="",
                disposition=choice.disposition,
            )
            node = _with_origin(node)
            ordinal += 1

        nodes.append(node)
        by_name[choice.template_name] = node

    return tuple(nodes)


def _with_origin(node: Node) -> Node:
    """A freshly minted node is its own lineage origin (SPEC open question 5)."""
    import dataclasses

    return dataclasses.replace(node, origin_node_id=node.node_id)
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3.12 -m pytest -q tests/p10/test_p10_residuals.py`

Expected: PASS, sixteen tests. `test_a_disabled_template_creates_no_node` is the one that matters most: it is DM12 in a single assertion, and it is why P11 needs no residual-specific legality path.

- [ ] **Step 5: Commit**

```bash
git add src/tree_design/residuals.py tests/p10/test_p10_residuals.py
git commit -m "feat(p10): publish the residual library and its enablement model"
```

### Task 11: Horizontal scaffold first, then one branch at a time

**Files:**
- Create: `src/tree_design/candidates.py`
- Create: `tests/p10/test_p10_candidates.py`

**Interfaces:**

*Consumes:* `tree_design.upstream` (`AcceptedGroup`, `ExistingFolder`), `tree_design.provenance.suppressed_branch_basis_keys` / `branch_basis_key`, `tree_design.routing` (`RoutingReport`, `CompositionCandidate`), `tree_design.validation.ValidationReport`.

*Produces:*

```python
@dataclass(frozen=True)
class BranchCandidate:
    subject_id: str
    display_label: str
    why_suggested: str
    supporting_file_count: int
    accepted_group_ids: tuple[str, ...]
    representative_group_labels: tuple[str, ...]
    resembling_existing_folders: tuple[str, ...]
    sensitive_content_present: bool
    source: str
    available_actions: tuple[str, ...]

@dataclass(frozen=True)
class VerticalOption:
    option_id: str
    kind: str                     # complete-template | fragment-composition | no-split
    resulting_child_counts: Mapping[str, int]
    total_child_branches: int
    example_members: tuple[str, ...]
    unresolved_file_ids: tuple[str, ...]
    summary: str
    validation: ValidationReport | None

def horizontal_candidates(conn, *, accepted, existing_folders, user_labels,
                          active_domains) -> tuple[BranchCandidate, ...]: ...
def vertical_options(report: RoutingReport, *, branch_members,
                     materialise, validate) -> tuple[VerticalOption, ...]: ...
```

**Done-means:** DM5 (every node carries an explanation, no surface exposes a confidence score), the proposal half of DM2(b), and the §5.6 purpose-packet guarantee.

- [ ] **Step 1: Write the failing candidate tests**

```python
# tests/p10/test_p10_candidates.py
"""P10 Task 11 — a small derived scaffold, then one branch at a time.

§5.1's nine example names — Academics, Applications, Research, Career, Personal
Records, Finance and Administration, Photos and Captures, Code and Projects,
Media or Miscellaneous Personal Material — are what "a typical initial canvas
might include". They are illustrative. Shipping them as a fixed set would be the
"universal corporate taxonomy" §5.1 says labels should NOT reflect, and this
suite asserts they are absent from the source.
"""
from __future__ import annotations

import pytest

from tree_design.candidates import (
    NO_SPLIT,
    BranchCandidate,
    horizontal_candidates,
    vertical_options,
)
from tree_design.provenance import branch_basis_key, record_tree_edit
from tree_design.routing import RoutingReport
from tree_design.upstream import AcceptedGroup, ExistingFolder, GroupMember
from tree_design.vocabulary import ACCEPT, DEFER, MERGE, RENAME

T0 = "2026-08-27T00:00:00Z"


def _group(group_id, label, domain, files, classes=("personal_non_sensitive",)):
    return AcceptedGroup(
        group_id=group_id, label=label, domain=domain,
        members=tuple(GroupMember(f, f"h_{f}", "direct-anchor") for f in files),
        anchor_facts=(f"fact_{group_id}",), excluded_members=(),
    )


ACADEMIC = _group("g_phys", "PHYS 1401", "academic", ("lecture", "hw"))
APPS = _group("g_apps", "Columbia application", "college_applications",
              ("transcript", "essay"))
FOLDER = ExistingFolder(
    directory_path="/Users/jy/Documents/School", parent_directory="/Users/jy/Documents",
    file_count=31, curation_signal="curated")


def _call(conn, **overrides):
    kwargs = dict(
        accepted=(ACADEMIC, APPS), existing_folders=(FOLDER,), user_labels=(),
        active_domains=("academic", "college_applications"),
        sensitive_group_ids=frozenset(),
    )
    kwargs.update(overrides)
    return horizontal_candidates(conn, **kwargs)


def test_a_candidate_is_derived_from_a_group_and_names_its_evidence(conn):
    candidates = {c.display_label: c for c in _call(conn)}
    academic = candidates["PHYS 1401"]
    assert academic.accepted_group_ids == ("g_phys",)
    assert academic.supporting_file_count == 2
    assert "PHYS 1401" in academic.why_suggested
    assert academic.subject_id == "g_phys"


def test_no_candidate_carries_a_confidence_score(conn):
    """§5.2: a concise explanation "rather than a technical confidence score".
    Internal scores may exist (§3.13) but they are not this surface."""
    for candidate in _call(conn):
        assert not any(
            token in candidate.why_suggested.lower()
            for token in ("confidence", "score", "probability", "%")
        )
        assert not any(
            field.startswith(("score", "confidence"))
            for field in candidate.__dataclass_fields__
        )


def test_a_curated_existing_folder_becomes_its_own_candidate(conn):
    """§5.10: a curated folder "should be treated as a strong expression of user
    intent"."""
    candidates = {c.display_label: c for c in _call(conn)}
    assert "School" in candidates
    assert candidates["School"].source == "existing-folder"
    assert candidates["School"].resembling_existing_folders == (
        "/Users/jy/Documents/School",)


def test_an_undetermined_folder_is_not_promoted_to_curated(conn):
    """P3 returns `undetermined` for every directory today, and §8.6 requires
    leaving something in review rather than guessing. An undetermined folder is
    still shown, and it is not treated as a strong expression of intent."""
    undetermined = ExistingFolder(
        directory_path="/Users/jy/Downloads", parent_directory="/Users/jy",
        file_count=904, curation_signal="undetermined")
    candidates = {c.display_label: c for c in _call(conn, existing_folders=(undetermined,))}
    assert "Downloads" in candidates
    assert candidates["Downloads"].source == "existing-folder-undetermined"


def test_a_rejected_branch_does_not_resurface(conn):
    """§8.7 and §4.9. The query is P1's `learning_records`, keyed on the parent
    and the label, and it runs BEFORE the candidate reaches the canvas."""
    key = branch_basis_key(parent_node_id=None, dimension_or_label="PHYS 1401")
    record_tree_edit(
        conn, action="delete-suggested-area", node_id="n_phys",
        plan_version_id="plan_1", before={"display_label": "PHYS 1401"}, after={},
        explanation="User deleted the suggested PHYS 1401 area.",
        observed_at=T0, user_id="jy", component_version="p10-1",
        correction_scope="node", correction_subject="__root__",
        polarity="reject", basis_key=key)
    labels = {c.display_label for c in _call(conn)}
    assert "PHYS 1401" not in labels
    assert "Columbia application" in labels


def test_the_nine_51_example_names_are_not_shipped_as_a_fixed_set(conn):
    import ast
    from pathlib import Path

    source = (Path(__file__).resolve().parents[2]
              / "src" / "tree_design" / "candidates.py").read_text()
    literals = {
        node.value for node in ast.walk(ast.parse(source))
        if isinstance(node.__class__, type) and isinstance(node, ast.Constant)
        and isinstance(node.value, str)
    }
    for illustration in ("Academics", "Applications", "Research", "Career",
                         "Personal Records", "Finance and Administration",
                         "Photos and Captures", "Code and Projects",
                         "Media or Miscellaneous Personal Material"):
        assert illustration not in literals
    # And the derived candidates come only from the evidence supplied.
    assert {c.display_label for c in _call(conn)} == {
        "PHYS 1401", "Columbia application", "School"}


def test_a_user_label_is_a_candidate_source_in_its_own_right(conn):
    candidates = {c.display_label: c for c in _call(conn, user_labels=("Taxes",))}
    assert candidates["Taxes"].source == "user-label"
    assert candidates["Taxes"].accepted_group_ids == ()


def test_a_sensitive_group_is_flagged_without_naming_a_file(conn):
    """§5.2: a Finance or Identity proposal "may be visible as a protected area,
    but the product should avoid showing sensitive filenames"."""
    candidates = {c.display_label: c for c in _call(
        conn, sensitive_group_ids=frozenset({"g_apps"}))}
    assert candidates["Columbia application"].sensitive_content_present is True
    text = candidates["Columbia application"].why_suggested
    assert "transcript" not in text and "essay" not in text


def test_every_candidate_offers_52s_actions(conn):
    for candidate in _call(conn):
        assert {ACCEPT, RENAME, MERGE, DEFER} <= set(candidate.available_actions)


def test_a_purpose_packet_stays_one_candidate_and_is_not_split_by_institution(conn):
    """§5.6: the canvas must be able to present a purpose-coherent,
    content-incoherent packet "as a preserved or proposed branch alongside
    institution-based organization"."""
    packet = _group("g_packet", "Grad school packet", "college_applications",
                    ("transcript", "id", "statement", "resume", "certificate"))
    candidates = {c.display_label: c for c in _call(conn, accepted=(packet,))}
    assert set(candidates) >= {"Grad school packet"}
    assert candidates["Grad school packet"].supporting_file_count == 5


def test_the_vertical_pass_always_offers_the_no_split_option():
    """§5.3: a candidate may be "a complete reusable template, a compatible
    composition of reusable fragments, or NO SPLIT." Keeping the branch shallow
    is a first-class answer, not a refusal to answer."""
    report = RoutingReport(candidates=(), conflicts=(), deferred=0)
    options = vertical_options(
        report, branch_members=("f1", "f2"),
        materialise=lambda candidate: None, validate=lambda materialised: None)
    assert [o.kind for o in options] == [NO_SPLIT]
    assert options[0].total_child_branches == 0
    assert options[0].unresolved_file_ids == ()


def test_a_whole_option_preview_states_what_each_option_would_create():
    """§5.5 wants the comparison, not just the per-level counts: Option A "would
    create three schools, five terms, and twelve course branches"; Option C "is
    shallower but leaves more files together"."""
    from tree_design.routing import CompositionCandidate
    from tree_design.templates import ApplicabilityRef, ResolvedDimension
    from tree_design.validation import ValidationReport
    from tree_design.vocabulary import ACTION_SELECTED

    candidate = CompositionCandidate(
        applicability_refs=(ApplicabilityRef("a1", 1),),
        resolved_dimensions=(
            ResolvedDimension("school", "school", ACTION_SELECTED, 0, None),
            ResolvedDimension("term", "term", ACTION_SELECTED, 1, None),
            ResolvedDimension("subject", "subject", ACTION_SELECTED, 2, None),
        ),
        privacy_floor="policy.public",
        covered_file_ids=frozenset({"f1", "f2"}),
        gates_passed=("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"),
        explanation="one row resolves three dimensions",
    )
    report = RoutingReport(candidates=(candidate,), conflicts=(), deferred=0)

    def materialise(_candidate):
        return {"school": 3, "term": 5, "subject": 12}

    def validate(_materialised):
        return ValidationReport(report_id="vr_1",
                                passed=("V1", "V2", "V3", "V4", "V5", "V6"),
                                failures=())

    options = vertical_options(report, branch_members=("f1", "f2", "f3"),
                               materialise=materialise, validate=validate)
    split = options[0]
    assert split.resulting_child_counts == {"school": 3, "term": 5, "subject": 12}
    assert split.total_child_branches == 12
    assert "3 school" in split.summary and "12 subject" in split.summary
    assert split.unresolved_file_ids == ("f3",)
    assert options[-1].kind == NO_SPLIT


def test_a_conflicted_route_yields_no_option_and_no_invented_branch():
    from tree_design.templates import CompositionConflict

    conflict = CompositionConflict("C3", ["finance"], "no row is eligible")
    report = RoutingReport(candidates=(), conflicts=(conflict,), deferred=0)
    options = vertical_options(
        report, branch_members=("f1",), materialise=lambda c: None,
        validate=lambda m: None)
    assert [o.kind for o in options] == [NO_SPLIT]
    assert "no applicable recipe" in options[0].summary


def test_a_failed_validation_keeps_the_option_visible_and_unusable():
    """§8.6 requires showing "the difference between completed work and deferred
    work". An option that failed V1-V6 is shown with its reason, not hidden —
    hiding it teaches the user the product simply had no idea."""
    from tree_design.routing import CompositionCandidate
    from tree_design.templates import ApplicabilityRef, ResolvedDimension
    from tree_design.validation import CheckFailure, ValidationReport
    from tree_design.vocabulary import ACTION_SELECTED

    candidate = CompositionCandidate(
        applicability_refs=(ApplicabilityRef("a1", 1),),
        resolved_dimensions=(
            ResolvedDimension("subject", "subject", ACTION_SELECTED, 0, None),),
        privacy_floor="policy.public", covered_file_ids=frozenset({"f1"}),
        gates_passed=("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"),
        explanation="one row resolves one dimension",
    )
    report = RoutingReport(candidates=(candidate,), conflicts=(), deferred=0)
    failing = ValidationReport(
        report_id="vr_1", passed=("V1", "V3", "V4", "V5", "V6"),
        failures=(CheckFailure("V2", "one child, PHYS1401", ("PHYS1401",)),))
    options = vertical_options(
        report, branch_members=("f1",), materialise=lambda c: {"subject": 1},
        validate=lambda m: failing)
    assert options[0].validation.failures
    assert "V2" in options[0].summary
```

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p10/test_p10_candidates.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'tree_design.candidates'`.

- [ ] **Step 3: Write the candidate passes**

```python
# src/tree_design/candidates.py
"""§5.1's horizontal pass and §5.3's vertical pass. Two passes, one rule.

The rule is that a candidate is DERIVED. It comes from an accepted group, an
active domain membership, an existing folder the scan found, or a label the user
typed. §5.1 wants labels that "reflect the user's vocabulary rather than a
universal corporate taxonomy", so this module ships no branch names at all — the
nine §5.1 lists are what a typical canvas "might include" and are illustrative.

The horizontal pass runs first and stays shallow and template-independent. The
composable-template design is explicit: "Top-level branches are derived before
template routing. A template cannot silently create a new high-level domain or
replace the user's vocabulary."
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from tree_design.provenance import branch_basis_key, suppressed_branch_basis_keys
from tree_design.routing import CompositionCandidate, RoutingReport
from tree_design.upstream import AcceptedGroup, ExistingFolder
from tree_design.validation import ValidationReport
from tree_design.vocabulary import (
    ACCEPT,
    CREATE_MANUALLY,
    DEFER,
    DRAG_GROUP_INTO_BRANCH,
    IGNORE,
    MERGE,
    MOVE_UNDER_ROOT,
    RENAME,
)

#: The option that keeps the branch as it is. §5.3 lists it beside a complete
#: template and a fragment composition, so it is an answer and not a fallback.
NO_SPLIT: str = "no-split"
COMPLETE_TEMPLATE: str = "complete-template"
FRAGMENT_COMPOSITION: str = "fragment-composition"

#: P3's curation signal has three values, and only one of them is §5.10's "strong
#: expression of user intent". `undetermined` gets its own source so the canvas
#: can show the folder without claiming the user curated it.
_CURATED = "curated"

_BRANCH_ACTIONS: tuple[str, ...] = (
    ACCEPT, RENAME, MERGE, MOVE_UNDER_ROOT, DEFER, CREATE_MANUALLY,
    DRAG_GROUP_INTO_BRANCH, IGNORE,
)


@dataclass(frozen=True)
class BranchCandidate:
    """§5.1 and §5.2's card, as data. No layout, no score."""

    subject_id: str
    display_label: str
    why_suggested: str
    supporting_file_count: int
    accepted_group_ids: tuple[str, ...]
    representative_group_labels: tuple[str, ...]
    resembling_existing_folders: tuple[str, ...]
    sensitive_content_present: bool
    source: str
    available_actions: tuple[str, ...]


@dataclass(frozen=True)
class VerticalOption:
    option_id: str
    kind: str
    resulting_child_counts: Mapping[str, int]
    total_child_branches: int
    example_members: tuple[str, ...]
    unresolved_file_ids: tuple[str, ...]
    summary: str
    validation: ValidationReport | None


def _folder_label(directory_path: str) -> str:
    """The last segment, as a display label. Never the path."""
    cleaned = directory_path.rstrip("/\\")
    for separator in ("/", "\\"):
        if separator in cleaned:
            cleaned = cleaned.rsplit(separator, 1)[-1]
    return cleaned


def horizontal_candidates(
    conn: sqlite3.Connection,
    *,
    accepted: Sequence[AcceptedGroup],
    existing_folders: Sequence[ExistingFolder],
    user_labels: Sequence[str],
    active_domains: Sequence[str],
    sensitive_group_ids: frozenset[str],
) -> tuple[BranchCandidate, ...]:
    """A small candidate set of top-level branches, each with its evidence.

    The learning query runs first. §8.7: "Rejected groups, rejected destination
    matches, rejected labels, and rejected residual recommendations must be
    stored with the evidence that produced them. Otherwise the system will
    repeatedly resurface the same attractive but incorrect grouping."
    """
    suppressed = suppressed_branch_basis_keys(conn, parent_node_id=None)
    candidates: list[BranchCandidate] = []

    def suppressed_label(label: str) -> bool:
        return branch_basis_key(
            parent_node_id=None, dimension_or_label=label) in suppressed

    folders_by_label = {
        _folder_label(folder.directory_path): folder for folder in existing_folders
    }

    for group in accepted:
        if group.domain is not None and group.domain not in active_domains:
            continue
        if suppressed_label(group.label):
            continue
        resembling = tuple(
            folder.directory_path for label, folder in folders_by_label.items()
            if label.lower() in group.label.lower()
            or group.label.lower() in label.lower()
        )
        sensitive = group.group_id in sensitive_group_ids
        detail = (
            f"{len(group.members)} file(s) in the accepted group "
            f"{group.label!r} share validated facts"
        )
        if group.domain:
            detail += f" in the {group.domain} schema"
        if sensitive:
            detail += "; this area holds sensitive material and is shown without filenames"
        candidates.append(BranchCandidate(
            subject_id=group.group_id,
            display_label=group.label,
            why_suggested=detail + ".",
            supporting_file_count=len(group.members),
            accepted_group_ids=(group.group_id,),
            representative_group_labels=(group.label,),
            resembling_existing_folders=resembling,
            sensitive_content_present=sensitive,
            source="accepted-group",
            available_actions=_BRANCH_ACTIONS,
        ))

    for label, folder in folders_by_label.items():
        if suppressed_label(label):
            continue
        curated = folder.curation_signal == _CURATED
        candidates.append(BranchCandidate(
            subject_id=folder.directory_path,
            display_label=label,
            why_suggested=(
                f"An existing folder holding {folder.file_count} file(s). "
                + ("The scan reads it as curated, which is a strong expression of "
                   "your intent."
                   if curated else
                   "The scan could not tell whether it is curated or incidental, "
                   "so it is shown as it is and nothing is assumed.")
            ),
            supporting_file_count=folder.file_count,
            accepted_group_ids=(),
            representative_group_labels=(),
            resembling_existing_folders=(folder.directory_path,),
            sensitive_content_present=False,
            source="existing-folder" if curated else "existing-folder-undetermined",
            available_actions=_BRANCH_ACTIONS,
        ))

    for label in user_labels:
        if suppressed_label(label):
            continue
        candidates.append(BranchCandidate(
            subject_id=f"user-label:{label}",
            display_label=label,
            why_suggested="You created this branch by name.",
            supporting_file_count=0,
            accepted_group_ids=(),
            representative_group_labels=(),
            resembling_existing_folders=(),
            sensitive_content_present=False,
            source="user-label",
            available_actions=_BRANCH_ACTIONS,
        ))

    return tuple(candidates)


def _summarise(counts: Mapping[str, int]) -> str:
    """§5.5's whole-option sentence: "three schools, five terms, twelve courses"."""
    parts = [f"{count} {role}" for role, count in counts.items()]
    if not parts:
        return "no child branches"
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + f", and {parts[-1]}"


def vertical_options(
    report: RoutingReport,
    *,
    branch_members: Sequence[str],
    materialise: Callable[[CompositionCandidate], Mapping[str, int] | None],
    validate: Callable[[object], ValidationReport | None],
) -> tuple[VerticalOption, ...]:
    """One option per routed candidate, plus no-split, always last and always there.

    Each option states what it WOULD create from the branch's actual facts, which
    files it leaves unresolved, and whether it passed V1-V6. An option that failed
    validation stays visible with its reason: §8.6 requires showing the
    difference between completed work and deferred work, and a silently dropped
    option looks to the user like the product having no idea.
    """
    members = tuple(branch_members)
    options: list[VerticalOption] = []

    for index, candidate in enumerate(report.candidates):
        counts = materialise(candidate) or {}
        validation = validate(candidate)
        unresolved = tuple(
            file_id for file_id in members
            if file_id not in candidate.covered_file_ids
        )
        kind = (COMPLETE_TEMPLATE if len(candidate.applicability_refs) == 1
                else FRAGMENT_COMPOSITION)
        summary = f"This option would create {_summarise(counts)}."
        if unresolved:
            summary += (
                f" {len(unresolved)} file(s) would stay unresolved and visible.")
        if validation is not None and validation.failures:
            failed = ", ".join(
                f"{failure.check} ({failure.reason})"
                for failure in validation.failures)
            summary += f" It does not pass {failed}."
        options.append(VerticalOption(
            option_id=f"opt_{index}",
            kind=kind,
            resulting_child_counts=dict(counts),
            total_child_branches=max(counts.values()) if counts else 0,
            example_members=members[:len(members)],
            unresolved_file_ids=unresolved,
            summary=summary,
            validation=validation,
        ))

    no_split_summary = (
        "Keep this branch as it is. Nothing moves and nothing is created."
    )
    if not report.candidates:
        no_split_summary = (
            "Keep this branch as it is: no applicable recipe resolved against "
            "this branch's evidence, and nothing is invented to fill the gap."
        )
    if report.deferred:
        no_split_summary += (
            f" {report.deferred} further option(s) were deferred by the proposal "
            "ceiling and are not judgements about your evidence."
        )
    options.append(VerticalOption(
        option_id="opt_no_split",
        kind=NO_SPLIT,
        resulting_child_counts={},
        total_child_branches=0,
        example_members=members,
        unresolved_file_ids=(),
        summary=no_split_summary,
        validation=None,
    ))
    return tuple(options)
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3.12 -m pytest -q tests/p10/test_p10_candidates.py`

Expected: PASS, fourteen tests. `test_the_nine_51_example_names_are_not_shipped_as_a_fixed_set` is the guard that keeps the product from becoming the corporate taxonomy §5.1 warns against; it parses the module rather than searching its text.

- [ ] **Step 5: Commit**

```bash
git add src/tree_design/candidates.py tests/p10/test_p10_candidates.py
git commit -m "feat(p10): derive explainable branch candidates"
```

### Task 12: Live counts, §5.9 warnings, and tree health

**Files:**
- Create: `src/tree_design/health.py`
- Create: `tests/p10/test_p10_health.py`

**Interfaces:**

*Consumes:* `tree_design.config.TreeLimits`, `tree_design.records.Node`, `tree_design.vocabulary.WARNING_KINDS`.

*Produces:*

```python
@dataclass(frozen=True)
class BranchCounts:
    node_id: str
    child_count: int
    descendant_count: int
    member_count: int
    example_members: tuple[str, ...]
    unresolved_file_ids: tuple[str, ...]
    evidence_gap_file_ids: tuple[str, ...]
    sensitive_isolated: bool
    stale: bool

@dataclass(frozen=True)
class Warning_:
    kind: str
    node_id: str
    reason: str
    evidence: tuple[str, ...]

@dataclass(frozen=True)
class TreeHealth:
    group_coverage: Mapping[str, float]
    files_with_enough_facts: int
    unresolved_node_ids: tuple[str, ...]
    context_supported_node_ids: tuple[str, ...]
    sensitive_isolated_node_ids: tuple[str, ...]
    nodes_needing_decisions: tuple[str, ...]

def branch_counts(nodes, *, node_id, members_by_node, unresolved_by_node,
                  evidence_gaps_by_node, sensitive_node_ids, stale=False) -> BranchCounts: ...
def warnings_for(nodes, counts_by_node, *, limits: TreeLimits,
                 parent_concepts) -> tuple[Warning_, ...]: ...
def tree_health(nodes, *, members_by_group, placed_by_group,
                files_with_enough_facts, unresolved_node_ids,
                context_supported_node_ids, sensitive_isolated_node_ids,
                nodes_needing_decisions) -> TreeHealth: ...
```

**Done-means:** DM9 (every §5.9 warning fires from published data, thresholds from configuration), and the preview half of DM5.

- [ ] **Step 1: Write the failing health tests**

```python
# tests/p10/test_p10_health.py
"""P10 Task 12 — counts before commit, warnings from data, health without blame.

§5.11 constrains the framing as much as the content: tree health "should not
imply that the system must account for every file immediately ... The goal is to
give the user a good enough structural gist of the corpus so that only a limited
number of high-leverage changes remain."

Every warning carries the data that fired it. None carries a number the design
did not state: §5.9 deliberately sets no threshold for "excessive" depth or "a
large number of tiny folders", so those arrive from configuration and cannot
fire without it.
"""
from __future__ import annotations

import pytest

from database_agent.budget import set_ceiling
from tree_design.config import tree_limits
from tree_design.health import branch_counts, tree_health, warnings_for
from tree_design.records import Node
from tree_design.vocabulary import (
    RECOMMEND_FLATTEN,
    WARN_EXCESSIVE_DEPTH,
    WARN_ONE_CHILD,
    WARN_REPEATED_PARENT,
    WARN_TINY_FOLDERS,
)


@pytest.fixture()
def limits(conn):
    set_ceiling(conn, "tree.max_folder_proposals_and_depth", 6)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    return tree_limits(
        conn, excessive_depth_warning=3, tiny_folder_max_files=2,
        tiny_folder_count_warning=3,
        materially_improves_retrieval=lambda preview: None)


def _node(node_id, parent, label, *, role="ordinary", dimension=None,
          dimension_role=None):
    return Node(
        node_id=node_id, plan_version_id="plan_1", node_type="proposed",
        display_label=label, parent_node_id=parent, root_anchor="root_documents",
        ordinal=0, associated_group_ids=(),
        explanation=f"{label} appeared from the accepted groups beneath it.",
        node_role=role, accepts_placement=True,
        handling_class="personal_non_sensitive", origin_node_id=node_id,
        dimension=dimension, dimension_role=dimension_role,
    )


def test_counts_report_children_descendants_and_members():
    nodes = (
        _node("n_root", None, "Academics"),
        _node("n_a", "n_root", "Columbia"),
        _node("n_b", "n_root", "NYU"),
        _node("n_a1", "n_a", "PHYS1401"),
    )
    counts = branch_counts(
        nodes, node_id="n_root",
        members_by_node={"n_root": ("f1", "f2", "f3")},
        unresolved_by_node={"n_root": ("f9",)},
        evidence_gaps_by_node={"n_root": ("f8",)},
        sensitive_node_ids=frozenset())
    assert counts.child_count == 2
    assert counts.descendant_count == 3
    assert counts.member_count == 3
    assert counts.example_members == ("f1", "f2", "f3")
    assert counts.unresolved_file_ids == ("f9",)
    assert counts.evidence_gap_file_ids == ("f8",)
    assert counts.stale is False


def test_counts_can_report_themselves_stale_while_recomputing():
    """The composable-template design requires "explicit stale/loading state
    while counts recompute". A stale count shown as fresh is a number the user
    will act on."""
    counts = branch_counts(
        (_node("n_root", None, "Academics"),), node_id="n_root",
        members_by_node={}, unresolved_by_node={}, evidence_gaps_by_node={},
        sensitive_node_ids=frozenset(), stale=True)
    assert counts.stale is True


def test_a_one_child_level_warns(limits):
    nodes = (_node("n_root", None, "Academics"), _node("n_a", "n_root", "Columbia"))
    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=frozenset()) for n in nodes}
    fired = warnings_for(nodes, counts, limits=limits, parent_concepts={})
    assert [w.kind for w in fired] == [WARN_ONE_CHILD]
    assert fired[0].node_id == "n_root"


def test_a_level_repeating_a_parent_concept_warns(limits):
    nodes = (
        _node("n_root", None, "Academics", dimension="subject",
              dimension_role="subject"),
        _node("n_a", "n_root", "PHYS1401", dimension="subject",
              dimension_role="course"),
        _node("n_b", "n_root", "CHEM1101", dimension="subject",
              dimension_role="course"),
    )
    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=frozenset()) for n in nodes}
    fired = warnings_for(nodes, counts, limits=limits,
                         parent_concepts={"n_a": ("subject",), "n_b": ("subject",)})
    assert WARN_REPEATED_PARENT in {w.kind for w in fired}


def test_excessive_depth_uses_the_injected_threshold_not_the_hard_ceiling(limits):
    chain = [_node("n_0", None, "L0")]
    for depth in range(1, 5):
        chain.append(_node(f"n_{depth}", f"n_{depth - 1}", f"L{depth}"))
    nodes = tuple(chain)
    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=frozenset()) for n in nodes}
    fired = warnings_for(nodes, counts, limits=limits, parent_concepts={})
    depth_warnings = [w for w in fired if w.kind == WARN_EXCESSIVE_DEPTH]
    assert depth_warnings
    assert str(limits.excessive_depth_warning) in depth_warnings[0].reason


def test_a_large_number_of_tiny_folders_warns(limits):
    nodes = (_node("n_root", None, "Receipts"),) + tuple(
        _node(f"n_{i}", "n_root", f"Vendor {i}") for i in range(4))
    counts = {}
    for node in nodes:
        members = () if node.node_id == "n_root" else ("f",)
        counts[node.node_id] = branch_counts(
            nodes, node_id=node.node_id,
            members_by_node={node.node_id: members}, unresolved_by_node={},
            evidence_gaps_by_node={}, sensitive_node_ids=frozenset())
    fired = warnings_for(nodes, counts, limits=limits, parent_concepts={})
    assert WARN_TINY_FOLDERS in {w.kind for w in fired}


def test_the_flatten_recommendation_stays_silent_while_the_test_is_unauthored(limits):
    """§5.9 asks for a recommendation "when a dimension does not materially
    improve retrieval" and states no test. `None` means unknown, and unknown must
    not become a recommendation."""
    nodes = (
        _node("n_root", None, "Academics"),
        _node("n_a", "n_root", "2026"),
        _node("n_b", "n_root", "2025"),
    )
    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=frozenset()) for n in nodes}
    fired = warnings_for(nodes, counts, limits=limits, parent_concepts={})
    assert RECOMMEND_FLATTEN not in {w.kind for w in fired}


def test_the_flatten_recommendation_fires_once_a_test_says_no(conn):
    set_ceiling(conn, "tree.max_folder_proposals_and_depth", 6)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    limits = tree_limits(
        conn, excessive_depth_warning=3, tiny_folder_max_files=2,
        tiny_folder_count_warning=3,
        materially_improves_retrieval=lambda preview: False)
    nodes = (
        _node("n_root", None, "Academics"),
        _node("n_a", "n_root", "2026", dimension="term", dimension_role="term"),
        _node("n_b", "n_root", "2025", dimension="term", dimension_role="term"),
    )
    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=frozenset()) for n in nodes}
    fired = warnings_for(nodes, counts, limits=limits, parent_concepts={})
    assert RECOMMEND_FLATTEN in {w.kind for w in fired}


def test_every_warning_is_data_backed_and_carries_no_score(limits):
    nodes = (_node("n_root", None, "Academics"), _node("n_a", "n_root", "Columbia"))
    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=frozenset()) for n in nodes}
    for warning in warnings_for(nodes, counts, limits=limits, parent_concepts={}):
        assert warning.evidence
        assert not any(
            token in warning.reason.lower()
            for token in ("confidence", "score", "probability"))


def test_uneven_depth_produces_no_warning_of_its_own(limits):
    """§5.8. Sibling parity is not a health property, and a warning that fired on
    it would push the user toward the symmetrical tree the design rejects."""
    nodes = (
        _node("n_root", None, "Academics"),
        _node("n_a", "n_root", "Columbia"),
        _node("n_b", "n_root", "Reading"),
        _node("n_a1", "n_a", "PHYS1401"),
        _node("n_a2", "n_a", "CHEM1101"),
    )
    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=frozenset()) for n in nodes}
    fired = warnings_for(nodes, counts, limits=limits, parent_concepts={})
    assert WARN_EXCESSIVE_DEPTH not in {w.kind for w in fired}
    assert all(w.kind != "uneven-depth" for w in fired)


def test_health_reports_coverage_without_demanding_every_file():
    nodes = (_node("n_root", None, "Academics"), _node("n_a", "n_root", "Columbia"))
    health = tree_health(
        nodes,
        members_by_group={"g_phys": ("lecture", "hw", "quiz")},
        placed_by_group={"g_phys": ("lecture", "hw")},
        files_with_enough_facts=2,
        unresolved_node_ids=("n_a",),
        context_supported_node_ids=(),
        sensitive_isolated_node_ids=(),
        nodes_needing_decisions=("n_a",),
    )
    assert health.group_coverage == {"g_phys": 2 / 3}
    assert health.nodes_needing_decisions == ("n_a",)
    assert not hasattr(health, "completeness_score")


def test_canonical_counts_are_reported_once_across_aliases():
    """The composable-template design: "Aliases and alternate views point to
    canonical node/item identities and do not duplicate counts or facts."
    """
    nodes = (
        _node("n_root", None, "Academics"),
        _node("n_a", "n_root", "Columbia"),
    )
    counts = branch_counts(
        nodes, node_id="n_root",
        members_by_node={"n_root": ("f1", "f1", "f2")},
        unresolved_by_node={}, evidence_gaps_by_node={},
        sensitive_node_ids=frozenset())
    assert counts.member_count == 2
```

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p10/test_p10_health.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'tree_design.health'`.

- [ ] **Step 3: Write the health module**

```python
# src/tree_design/health.py
"""§5.5's live counts, §5.9's warnings, §5.11's tree health.

All three are computed from local facts and involve no model call, which is why
§8.6 can leave them out of the ceilings: they are cheap by construction.

Two framing rules carry as much weight as the arithmetic. §5.2 requires an
explanation "rather than a technical confidence score", so nothing here returns a
number the user is meant to read as certainty. §5.11 says health "should not
imply that the system must account for every file immediately", so there is no
completeness score and no percentage presented as a grade.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from tree_design.config import TreeLimits
from tree_design.records import Node
from tree_design.vocabulary import (
    RECOMMEND_FLATTEN,
    WARN_EXCESSIVE_DEPTH,
    WARN_ONE_CHILD,
    WARN_REPEATED_PARENT,
    WARN_TINY_FOLDERS,
)


@dataclass(frozen=True)
class BranchCounts:
    node_id: str
    child_count: int
    descendant_count: int
    member_count: int
    example_members: tuple[str, ...]
    unresolved_file_ids: tuple[str, ...]
    evidence_gap_file_ids: tuple[str, ...]
    sensitive_isolated: bool
    stale: bool


@dataclass(frozen=True)
class Warning_:
    kind: str
    node_id: str
    reason: str
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class TreeHealth:
    group_coverage: Mapping[str, float]
    files_with_enough_facts: int
    unresolved_node_ids: tuple[str, ...]
    context_supported_node_ids: tuple[str, ...]
    sensitive_isolated_node_ids: tuple[str, ...]
    nodes_needing_decisions: tuple[str, ...]


def _children(nodes: Sequence[Node], node_id: str) -> tuple[Node, ...]:
    return tuple(node for node in nodes if node.parent_node_id == node_id)


def _descendants(nodes: Sequence[Node], node_id: str) -> tuple[Node, ...]:
    found: list[Node] = []
    frontier = [node_id]
    while frontier:
        current = frontier.pop()
        for child in _children(nodes, current):
            found.append(child)
            frontier.append(child.node_id)
    return tuple(found)


def _depth(nodes: Sequence[Node], node_id: str) -> int:
    by_id = {node.node_id: node for node in nodes}
    depth = 0
    current = by_id.get(node_id)
    while current is not None and current.parent_node_id is not None:
        depth += 1
        current = by_id.get(current.parent_node_id)
    return depth


def branch_counts(
    nodes: Sequence[Node],
    *,
    node_id: str,
    members_by_node: Mapping[str, Sequence[str]],
    unresolved_by_node: Mapping[str, Sequence[str]],
    evidence_gaps_by_node: Mapping[str, Sequence[str]],
    sensitive_node_ids: frozenset[str],
    stale: bool = False,
) -> BranchCounts:
    """§5.5's numbers, before a split is committed.

    Members are counted by CANONICAL file identity. An alias or an alternate view
    points at the same file, and counting it twice would tell the user a branch
    holds more than it does.
    """
    members = tuple(dict.fromkeys(members_by_node.get(node_id, ())))
    return BranchCounts(
        node_id=node_id,
        child_count=len(_children(nodes, node_id)),
        descendant_count=len(_descendants(nodes, node_id)),
        member_count=len(members),
        example_members=members,
        unresolved_file_ids=tuple(unresolved_by_node.get(node_id, ())),
        evidence_gap_file_ids=tuple(evidence_gaps_by_node.get(node_id, ())),
        sensitive_isolated=node_id in sensitive_node_ids,
        stale=stale,
    )


def warnings_for(
    nodes: Sequence[Node],
    counts_by_node: Mapping[str, BranchCounts],
    *,
    limits: TreeLimits,
    parent_concepts: Mapping[str, Sequence[str]],
) -> tuple[Warning_, ...]:
    """§5.9's four warnings and its flattening recommendation.

    Every threshold arrives from `limits`. There is no warning for uneven depth,
    because §5.8 makes uneven depth a REQUIREMENT and a warning against it would
    push the user toward the symmetrical tree the design rejects.
    """
    fired: list[Warning_] = []

    for node in nodes:
        counts = counts_by_node.get(node.node_id)
        if counts is None:
            continue

        if counts.child_count == 1:
            only = _children(nodes, node.node_id)[0]
            fired.append(Warning_(
                WARN_ONE_CHILD, node.node_id,
                f"this level produces one child, {only.display_label!r}; opening "
                "it shows a single folder",
                (only.node_id,),
            ))

        repeated = [
            concept for concept in parent_concepts.get(node.node_id, ())
            if node.dimension is not None and concept == node.dimension
        ]
        if repeated:
            fired.append(Warning_(
                WARN_REPEATED_PARENT, node.node_id,
                f"this level splits by {node.dimension!r}, which a parent already "
                "expresses",
                tuple(repeated),
            ))

        depth = _depth(nodes, node.node_id)
        if depth > limits.excessive_depth_warning:
            fired.append(Warning_(
                WARN_EXCESSIVE_DEPTH, node.node_id,
                f"this node sits at depth {depth}, past the configured warning "
                f"depth of {limits.excessive_depth_warning}",
                (node.node_id,),
            ))

        children = _children(nodes, node.node_id)
        tiny = [
            child.node_id for child in children
            if counts_by_node.get(child.node_id) is not None
            and counts_by_node[child.node_id].member_count
            <= limits.tiny_folder_max_files
        ]
        if len(tiny) >= limits.tiny_folder_count_warning:
            fired.append(Warning_(
                WARN_TINY_FOLDERS, node.node_id,
                f"{len(tiny)} of this level's children hold "
                f"{limits.tiny_folder_max_files} file(s) or fewer",
                tuple(tiny),
            ))

        if node.dimension is not None:
            verdict = limits.materially_improves_retrieval(counts)
            if verdict is False:
                fired.append(Warning_(
                    RECOMMEND_FLATTEN, node.node_id,
                    f"the configured retrieval test says {node.dimension!r} does "
                    "not earn its level here; flattening it keeps the files "
                    "together",
                    (node.dimension,),
                ))

    return tuple(fired)


def tree_health(
    nodes: Sequence[Node],
    *,
    members_by_group: Mapping[str, Sequence[str]],
    placed_by_group: Mapping[str, Sequence[str]],
    files_with_enough_facts: int,
    unresolved_node_ids: Sequence[str],
    context_supported_node_ids: Sequence[str],
    sensitive_isolated_node_ids: Sequence[str],
    nodes_needing_decisions: Sequence[str],
) -> TreeHealth:
    """§5.11's six measures. No completeness score, on purpose.

    §5.11: health "should not imply that the system must account for every file
    immediately ... The goal is to give the user a good enough structural gist of
    the corpus so that only a limited number of high-leverage changes remain." A
    single number would be read as a grade to raise, which is the opposite.
    """
    coverage = {}
    for group_id, members in members_by_group.items():
        total = len(set(members))
        placed = len(set(placed_by_group.get(group_id, ())) & set(members))
        coverage[group_id] = 0.0 if total == 0 else placed / total
    return TreeHealth(
        group_coverage=coverage,
        files_with_enough_facts=files_with_enough_facts,
        unresolved_node_ids=tuple(unresolved_node_ids),
        context_supported_node_ids=tuple(context_supported_node_ids),
        sensitive_isolated_node_ids=tuple(sensitive_isolated_node_ids),
        nodes_needing_decisions=tuple(nodes_needing_decisions),
    )
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3.12 -m pytest -q tests/p10/test_p10_health.py`

Expected: PASS, twelve tests.

- [ ] **Step 5: Commit**

```bash
git add src/tree_design/health.py tests/p10/test_p10_health.py
git commit -m "feat(p10): compute live counts, warnings and tree health"
```

### Task 13: Versioned writes, user edits, and the node-level diff

**Files:**
- Create: `src/tree_design/store.py`
- Create: `src/tree_design/diff.py`
- Create: `tests/p10/p13_fixtures.py`
- Create: `tests/p10/test_p10_versions.py`

**Interfaces:**

*Consumes:* `tree_design.schema.create_tree_schema`, `tree_design.records` (`Node`, `PlanVersion`, `SharedMaterialPolicy`), `tree_design.provenance` (`record_tree_edit`, `record_plan_version_adoption`), `evidence_shape.canonical.canonical_json`.

*Produces:*

```python
class FrozenVersionImmutable(RuntimeError): ...

def write_plan_version(conn, version: PlanVersion) -> None: ...
def write_node(conn, node: Node) -> None: ...
def nodes_for_version(conn, plan_version_id: str) -> tuple[Node, ...]: ...
def open_draft(conn, *, from_version: str, new_version_id: str, created_at: str,
               mint_node_id) -> PlanVersion: ...
def apply_review_action(conn, action, *, new_version_id: str, created_at: str,
                        mint_node_id, component_version: str) -> str: ...
def set_shared_material_policy(conn, policy: SharedMaterialPolicy) -> None: ...
def freeze_version(conn, plan_version_id: str) -> None: ...

@dataclass(frozen=True)
class NodeDiffEntry:
    kind: str
    node_id: str
    origin_node_id: str
    before: Mapping[str, object] | None
    after: Mapping[str, object] | None
    undo_label: str

def diff_versions(conn, *, before: str, after: str) -> tuple[NodeDiffEntry, ...]: ...
```

**Done-means:** DM4 (freeze mutates no evidence), DM6 (existing folders survive), DM17 (a partial-depth design can be complete and later refinement creates a new version), and the versioning half of DM1.

- [ ] **Step 1: Write the P13 review-action fixture**

```python
# tests/p10/p13_fixtures.py
"""P13's `review_action`, as P13's SPEC publishes its fields. Tests only.

P13 is specification only: its three event names are registered in
`database_agent.events` and it has no producer. This fixture is a structural
stand-in with P13's exact field names, so the day P13 publishes its record the
import swaps and no field name changes. `src/tree_design/` never imports it.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewActionFixture:
    review_action_id: str
    surface: str            # canvas | plan_version
    subject_ref: str        # a node_id, or a plan_version_id for a version action
    plan_version: str
    action: str
    correction_scope: str
    presented_state_ref: str
    user_id: str
    observed_at: str
    payload: dict


def rename(node_id: str, *, plan_version: str, new_label: str) -> ReviewActionFixture:
    return ReviewActionFixture(
        review_action_id=f"ra_rename_{node_id}", surface="canvas",
        subject_ref=node_id, plan_version=plan_version, action="rename",
        correction_scope="node", presented_state_ref=f"ps_{node_id}",
        user_id="jy", observed_at="2026-08-27T00:00:00Z",
        payload={"display_label": new_label},
    )


def ignore_existing(node_id: str, *, plan_version: str) -> ReviewActionFixture:
    return ReviewActionFixture(
        review_action_id=f"ra_ignore_{node_id}", surface="canvas",
        subject_ref=node_id, plan_version=plan_version, action="ignore",
        correction_scope="node", presented_state_ref=f"ps_{node_id}",
        user_id="jy", observed_at="2026-08-27T00:01:00Z", payload={},
    )


def restore(plan_version: str, *, target: str) -> ReviewActionFixture:
    return ReviewActionFixture(
        review_action_id=f"ra_restore_{target}", surface="plan_version",
        subject_ref=target, plan_version=plan_version, action="restore_version",
        correction_scope="corpus", presented_state_ref=f"ps_{target}",
        user_id="jy", observed_at="2026-08-27T00:02:00Z", payload={},
    )
```

- [ ] **Step 2: Write the failing version and diff tests**

```python
# tests/p10/test_p10_versions.py
"""P10 Task 13 — a frozen version is immutable and an edit opens a draft.

§8.8: "When the user edits the tree, the product should create a draft plan
version and show a meaningful diff." And: "A new plan should never silently
reclassify or move old files."

§5.12 states the other half from the user's side: "The facts and accepted groups
remain separate from the tree, so the user can change the visual organization
without destroying the underlying evidence." The evidence test below is
byte-for-byte, because "unchanged" checked loosely is how evidence loss ships.
"""
from __future__ import annotations

import json

import pytest

import p13_fixtures
from tree_design.diff import diff_versions
from tree_design.records import Node, PlanVersion, SharedMaterialPolicy
from tree_design.schema import create_tree_schema
from tree_design.store import (
    FrozenVersionImmutable,
    apply_review_action,
    freeze_version,
    nodes_for_version,
    open_draft,
    set_shared_material_policy,
    write_node,
    write_plan_version,
)
from tree_design.vocabulary import (
    DIFF_ADDED,
    DIFF_REMOVED,
    DIFF_RENAMED,
    DIFF_REPARENTED,
    DIFF_TYPE_CHANGED,
    PRIMARY_HOME,
)

T0 = "2026-08-27T00:00:00Z"
T1 = "2026-08-27T01:00:00Z"


def _ids(prefix="n"):
    counter = iter(range(1000))
    return lambda: f"{prefix}_{next(counter)}"


def _node(node_id, label, *, parent=None, node_type="proposed", role="ordinary",
          version="plan_1", origin=None, ordinal=0):
    return Node(
        node_id=node_id, plan_version_id=version, node_type=node_type,
        display_label=label, parent_node_id=parent, root_anchor="root_documents",
        ordinal=ordinal, associated_group_ids=(),
        explanation=f"{label} appeared from the accepted groups beneath it.",
        node_role=role,
        accepts_placement=node_type != "ignored",
        handling_class="personal_non_sensitive",
        origin_node_id=origin or node_id,
        existing_path="/Users/jy/Documents/School" if node_type == "existing" else None,
    )


@pytest.fixture()
def seeded(conn):
    create_tree_schema(conn)
    write_plan_version(conn, PlanVersion(
        plan_version_id="plan_1", predecessor_id=None, state="draft",
        created_at=T0, cross_folder_moves=False, selection_id="sel_1"))
    write_node(conn, _node("n_root", "Academics"))
    write_node(conn, _node("n_a", "Columbia", parent="n_root"))
    write_node(conn, _node("n_school", "School", node_type="existing", ordinal=1))
    return conn


def test_nodes_round_trip_through_the_store(seeded):
    nodes = {n.node_id: n for n in nodes_for_version(seeded, "plan_1")}
    assert nodes["n_a"].parent_node_id == "n_root"
    assert nodes["n_school"].existing_path == "/Users/jy/Documents/School"
    assert nodes["n_root"].accepts_placement is True


def test_a_frozen_version_refuses_every_further_write(seeded):
    freeze_version(seeded, "plan_1")
    with pytest.raises(FrozenVersionImmutable):
        write_node(seeded, _node("n_new", "Late addition"))


def test_an_edit_opens_a_draft_and_leaves_the_frozen_version_intact(seeded):
    freeze_version(seeded, "plan_1")
    draft = open_draft(seeded, from_version="plan_1", new_version_id="plan_2",
                       created_at=T1, mint_node_id=_ids("n2"))
    assert draft.predecessor_id == "plan_1"
    assert draft.state == "draft"
    assert len(nodes_for_version(seeded, "plan_1")) == 3
    assert len(nodes_for_version(seeded, "plan_2")) == 3
    # §1.1's permission travels with the version it was frozen under.
    assert draft.cross_folder_moves is False


def test_a_copied_node_keeps_its_lineage_and_gets_a_new_identity(seeded):
    freeze_version(seeded, "plan_1")
    open_draft(seeded, from_version="plan_1", new_version_id="plan_2",
               created_at=T1, mint_node_id=_ids("n2"))
    before = {n.origin_node_id: n for n in nodes_for_version(seeded, "plan_1")}
    after = {n.origin_node_id: n for n in nodes_for_version(seeded, "plan_2")}
    assert set(before) == set(after)
    assert before["n_root"].node_id != after["n_root"].node_id
    assert after["n_a"].parent_node_id == after["n_root"].node_id


def test_a_rename_produces_a_new_version_and_a_renamed_diff_entry(seeded):
    freeze_version(seeded, "plan_1")
    action = p13_fixtures.rename("n_root", plan_version="plan_1",
                                 new_label="School work")
    new_version = apply_review_action(
        seeded, action, new_version_id="plan_2", created_at=T1,
        mint_node_id=_ids("n2"), component_version="p10-1")
    entries = diff_versions(seeded, before="plan_1", after=new_version)
    renamed = [e for e in entries if e.kind == DIFF_RENAMED]
    assert len(renamed) == 1
    assert renamed[0].before["display_label"] == "Academics"
    assert renamed[0].after["display_label"] == "School work"
    assert renamed[0].undo_label == 'Undo rename of "Academics"'


def test_a_rename_changes_no_fact_and_no_expected_value(seeded):
    """§2.8 and §3.14: renaming a node rewrites `display_label` only. The
    underlying expected values and the evidence behind them are untouched."""
    freeze_version(seeded, "plan_1")
    facts_before = seeded.execute(
        "SELECT count(*) AS n FROM events").fetchone()["n"]
    action = p13_fixtures.rename("n_root", plan_version="plan_1",
                                 new_label="School work")
    apply_review_action(seeded, action, new_version_id="plan_2", created_at=T1,
                        mint_node_id=_ids("n2"), component_version="p10-1")
    # One new event: the edit itself. No fact table exists to change, and the
    # node's expected values travel unmodified.
    facts_after = seeded.execute("SELECT count(*) AS n FROM events").fetchone()["n"]
    assert facts_after == facts_before + 1


def test_ignoring_an_existing_folder_flips_legality_and_nothing_else(seeded):
    """§5.10 lets the user leave an existing folder untouched. The node stays
    visible as context; `accepts_placement` is what stops P11 placing into it."""
    freeze_version(seeded, "plan_1")
    action = p13_fixtures.ignore_existing("n_school", plan_version="plan_1")
    new_version = apply_review_action(
        seeded, action, new_version_id="plan_2", created_at=T1,
        mint_node_id=_ids("n2"), component_version="p10-1")
    after = {n.origin_node_id: n for n in nodes_for_version(seeded, new_version)}
    assert after["n_school"].node_type == "ignored"
    assert after["n_school"].accepts_placement is False
    assert after["n_school"].existing_path is None  # ignored is no longer `existing`
    entries = diff_versions(seeded, before="plan_1", after=new_version)
    assert DIFF_TYPE_CHANGED in {e.kind for e in entries}


def test_no_code_path_renames_an_existing_node_without_a_recorded_action(seeded):
    """§5.10's hard prohibition: "Existing folders must not be automatically
    flattened, renamed, or reorganized simply because a template would produce a
    different structure."
    """
    freeze_version(seeded, "plan_1")
    open_draft(seeded, from_version="plan_1", new_version_id="plan_2",
               created_at=T1, mint_node_id=_ids("n2"))
    after = {n.origin_node_id: n for n in nodes_for_version(seeded, "plan_2")}
    assert after["n_school"].display_label == "School"
    assert after["n_school"].node_type == "existing"
    assert after["n_school"].existing_path == "/Users/jy/Documents/School"


def test_the_diff_reports_all_seven_kinds_it_can_observe(seeded):
    freeze_version(seeded, "plan_1")
    open_draft(seeded, from_version="plan_1", new_version_id="plan_2",
               created_at=T1, mint_node_id=_ids("n2"))
    nodes = {n.origin_node_id: n for n in nodes_for_version(seeded, "plan_2")}
    seeded.execute("DELETE FROM tree_nodes WHERE plan_version_id = ? AND node_id = ?",
                   ("plan_2", nodes["n_a"].node_id))
    write_node(seeded, Node(
        node_id="n2_extra", plan_version_id="plan_2", node_type="user-created",
        display_label="Reading", parent_node_id=nodes["n_root"].node_id,
        root_anchor="root_documents", ordinal=2, associated_group_ids=(),
        explanation="The user created this branch by name.",
        node_role="ordinary", accepts_placement=True,
        handling_class="personal_non_sensitive", origin_node_id="n2_extra"))
    entries = diff_versions(seeded, before="plan_1", after="plan_2")
    kinds = {e.kind for e in entries}
    assert DIFF_REMOVED in kinds
    assert DIFF_ADDED in kinds


def test_a_shared_material_policy_is_recorded_per_version(seeded):
    set_shared_material_policy(seeded, SharedMaterialPolicy(
        policy_id="smp_1", plan_version_id="plan_1", policy=PRIMARY_HOME,
        policy_scope=None,
        reason="A transcript lives in one packet and is referenced from the other."))
    row = seeded.execute("SELECT * FROM shared_material_policies").fetchone()
    assert row["policy"] == PRIMARY_HOME
    assert row["policy_scope"] is None


def test_two_global_shared_material_policies_in_one_version_are_refused(seeded):
    import sqlite3

    set_shared_material_policy(seeded, SharedMaterialPolicy(
        policy_id="smp_1", plan_version_id="plan_1", policy=PRIMARY_HOME,
        policy_scope=None, reason="first"))
    with pytest.raises(sqlite3.IntegrityError):
        set_shared_material_policy(seeded, SharedMaterialPolicy(
            policy_id="smp_2", plan_version_id="plan_1", policy=PRIMARY_HOME,
            policy_scope=None, reason="second"))


def test_restoring_an_earlier_version_creates_a_new_draft_and_deletes_nothing(seeded):
    freeze_version(seeded, "plan_1")
    action = p13_fixtures.rename("n_root", plan_version="plan_1",
                                 new_label="School work")
    apply_review_action(seeded, action, new_version_id="plan_2", created_at=T1,
                        mint_node_id=_ids("n2"), component_version="p10-1")
    freeze_version(seeded, "plan_2")
    restore = p13_fixtures.restore("plan_2", target="plan_1")
    third = apply_review_action(
        seeded, restore, new_version_id="plan_3", created_at=T1,
        mint_node_id=_ids("n3"), component_version="p10-1")
    labels = {n.origin_node_id: n.display_label
              for n in nodes_for_version(seeded, third)}
    assert labels["n_root"] == "Academics"
    assert len(nodes_for_version(seeded, "plan_2")) == 3
    assert len(nodes_for_version(seeded, "plan_1")) == 3


def test_a_partial_depth_design_survives_a_round_trip(seeded):
    """DM17: one refined, one shallow-by-choice, one refine-later branch, each
    with a reason, all in one version."""
    for node_id, disposition, reason in (
        ("n_r", "refined", "The course groups justify the split."),
        ("n_s", "shallow-by-choice", "Twelve receipts need no vendor level."),
        ("n_l", "refine-later", "Not enough validated facts yet."),
    ):
        write_node(seeded, Node(
            node_id=node_id, plan_version_id="plan_1", node_type="proposed",
            display_label=node_id, parent_node_id=None,
            root_anchor="root_documents", ordinal=9, associated_group_ids=(),
            explanation="A branch the user approved at the top level.",
            node_role="ordinary", accepts_placement=True,
            handling_class="personal_non_sensitive", origin_node_id=node_id,
            refinement_disposition=disposition, refinement_reason=reason))
    stored = {n.node_id: n for n in nodes_for_version(seeded, "plan_1")}
    assert {stored[n].refinement_disposition for n in ("n_r", "n_s", "n_l")} == {
        "refined", "shallow-by-choice", "refine-later"}
    assert all(stored[n].refinement_reason for n in ("n_r", "n_s", "n_l"))
```

- [ ] **Step 3: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p10/test_p10_versions.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'tree_design.store'`.

- [ ] **Step 4: Write the store**

```python
# src/tree_design/store.py
"""Versioned writes and current reads. A frozen version is immutable.

§8.8 is the whole contract: an edit opens a draft, the draft is comparable to its
predecessor by a node-level diff, the user may restore an earlier version or
adopt the new one, and adoption "never silently reclassifies or moves old files".

Node identity is minted per version, with `origin_node_id` carrying the lineage,
because SPEC open question 5 is open. That choice is deliberately the reversible
one: if node ids turn out to be stable across versions, `origin_node_id` becomes
`node_id` and nothing else changes; the other choice cannot be undone.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable

from evidence_shape.canonical import canonical_json
from tree_design.records import (
    ExpectedValue,
    Node,
    PlanVersion,
    SharedMaterialPolicy,
    TemplateContext,
    derive_accepts_placement,
)
from tree_design.provenance import record_plan_version_adoption, record_tree_edit
from tree_design.vocabulary import (
    ADOPT_VERSION,
    IGNORE,
    RENAME,
    RESTORE_VERSION,
)

_NODE_COLUMNS = (
    "node_id", "plan_version_id", "origin_node_id", "node_type", "display_label",
    "parent_node_id", "root_anchor", "ordinal", "associated_group_ids",
    "explanation", "node_role", "accepts_placement",
    "protected_movement_permitted", "handling_class", "template_context",
    "dimension_role", "dimension", "existing_path", "disposition",
    "refinement_disposition", "refinement_reason",
)


class FrozenVersionImmutable(RuntimeError):
    """§8.8: a frozen version is never amended in place. An edit opens a draft."""


def _state(conn: sqlite3.Connection, plan_version_id: str) -> str | None:
    row = conn.execute(
        "SELECT state FROM plan_versions WHERE plan_version_id = ?",
        (plan_version_id,)).fetchone()
    return None if row is None else row["state"]


def write_plan_version(conn: sqlite3.Connection, version: PlanVersion) -> None:
    conn.execute(
        "INSERT INTO plan_versions (plan_version_id, predecessor_id, state, "
        "created_at, cross_folder_moves, selection_id) VALUES (?, ?, ?, ?, ?, ?)",
        (version.plan_version_id, version.predecessor_id, version.state,
         version.created_at, int(version.cross_folder_moves), version.selection_id),
    )


def write_node(conn: sqlite3.Connection, node: Node) -> None:
    if _state(conn, node.plan_version_id) == "frozen":
        raise FrozenVersionImmutable(
            f"plan version {node.plan_version_id!r} is frozen. §8.8 requires an "
            "edit to open a DRAFT version and show a diff; amending a frozen "
            "version in place would change what the user already approved."
        )
    values = (
        node.node_id, node.plan_version_id, node.origin_node_id, node.node_type,
        node.display_label, node.parent_node_id, node.root_anchor, node.ordinal,
        canonical_json(list(node.associated_group_ids)), node.explanation,
        node.node_role, int(node.accepts_placement),
        int(node.protected_movement_permitted), node.handling_class,
        None if node.template_context is None else canonical_json({
            "binding_id": node.template_context.binding_id,
            "template_id": node.template_context.template_id,
            "template_version": node.template_context.template_version,
            "dimension_index": node.template_context.dimension_index,
            "fragment_id": node.template_context.fragment_id,
            "fragment_version": node.template_context.fragment_version,
        }),
        node.dimension_role, node.dimension, node.existing_path, node.disposition,
        node.refinement_disposition, node.refinement_reason,
    )
    conn.execute(
        f"INSERT OR REPLACE INTO tree_nodes ({','.join(_NODE_COLUMNS)}) "
        f"VALUES ({','.join('?' * len(_NODE_COLUMNS))})",
        values,
    )
    for expected in node.expected_values:
        conn.execute(
            "INSERT OR IGNORE INTO node_expected_values "
            "(plan_version_id, node_id, field_key, value) VALUES (?, ?, ?, ?)",
            (node.plan_version_id, node.node_id, expected.field, expected.value),
        )


def _row_to_node(conn: sqlite3.Connection, row: sqlite3.Row) -> Node:
    import json

    context = row["template_context"]
    expected = conn.execute(
        "SELECT field_key, value FROM node_expected_values "
        "WHERE plan_version_id = ? AND node_id = ? ORDER BY field_key, value",
        (row["plan_version_id"], row["node_id"])).fetchall()
    return Node(
        node_id=row["node_id"],
        plan_version_id=row["plan_version_id"],
        origin_node_id=row["origin_node_id"],
        node_type=row["node_type"],
        display_label=row["display_label"],
        parent_node_id=row["parent_node_id"],
        root_anchor=row["root_anchor"],
        ordinal=row["ordinal"],
        associated_group_ids=tuple(json.loads(row["associated_group_ids"])),
        explanation=row["explanation"],
        node_role=row["node_role"],
        accepts_placement=bool(row["accepts_placement"]),
        protected_movement_permitted=bool(row["protected_movement_permitted"]),
        handling_class=row["handling_class"],
        template_context=None if context is None else TemplateContext(
            **json.loads(context)),
        dimension_role=row["dimension_role"],
        dimension=row["dimension"],
        expected_values=tuple(
            ExpectedValue(field=e["field_key"], value=e["value"]) for e in expected),
        existing_path=row["existing_path"],
        disposition=row["disposition"],
        refinement_disposition=row["refinement_disposition"],
        refinement_reason=row["refinement_reason"],
    )


def nodes_for_version(conn: sqlite3.Connection,
                      plan_version_id: str) -> tuple[Node, ...]:
    rows = conn.execute(
        "SELECT * FROM tree_nodes WHERE plan_version_id = ? "
        "ORDER BY ordinal, node_id", (plan_version_id,)).fetchall()
    return tuple(_row_to_node(conn, row) for row in rows)


def freeze_version(conn: sqlite3.Connection, plan_version_id: str) -> None:
    """Mark a version frozen. Task 15 owns the validation that precedes this."""
    conn.execute(
        "UPDATE plan_versions SET state = 'frozen' WHERE plan_version_id = ?",
        (plan_version_id,))


def set_shared_material_policy(conn: sqlite3.Connection,
                               policy: SharedMaterialPolicy) -> None:
    """§6.9's policy. `policy_scope IS NULL` means tree-global, and the schema's
    partial unique index allows exactly one of those per version."""
    conn.execute(
        "INSERT INTO shared_material_policies "
        "(policy_id, plan_version_id, policy, policy_scope, reason) "
        "VALUES (?, ?, ?, ?, ?)",
        (policy.policy_id, policy.plan_version_id, policy.policy,
         policy.policy_scope, policy.reason),
    )


def open_draft(conn: sqlite3.Connection, *, from_version: str,
               new_version_id: str, created_at: str,
               mint_node_id: Callable[[], str]) -> PlanVersion:
    """Copy a version's tree into a new draft, preserving lineage and shape."""
    row = conn.execute(
        "SELECT * FROM plan_versions WHERE plan_version_id = ?",
        (from_version,)).fetchone()
    if row is None:
        raise FrozenVersionImmutable(
            f"plan version {from_version!r} does not exist; a draft is opened "
            "FROM something")
    draft = PlanVersion(
        plan_version_id=new_version_id, predecessor_id=from_version,
        state="draft", created_at=created_at,
        cross_folder_moves=bool(row["cross_folder_moves"]),
        selection_id=row["selection_id"],
    )
    write_plan_version(conn, draft)

    source = nodes_for_version(conn, from_version)
    remap = {node.node_id: mint_node_id() for node in source}
    for node in source:
        import dataclasses

        copied = dataclasses.replace(
            node,
            node_id=remap[node.node_id],
            plan_version_id=new_version_id,
            parent_node_id=(None if node.parent_node_id is None
                            else remap[node.parent_node_id]),
        )
        write_node(conn, copied)
    return draft


def apply_review_action(conn: sqlite3.Connection, action, *,
                        new_version_id: str, created_at: str,
                        mint_node_id: Callable[[], str],
                        component_version: str) -> str:
    """One accepted edit, one new plan version (M8, §8.8).

    P13 presents and collects; it decides nothing. P10 authors the edit, the edit
    produces a version, and P1 writes the event.
    """
    if action.action in (ADOPT_VERSION, RESTORE_VERSION):
        draft = open_draft(conn, from_version=action.subject_ref,
                           new_version_id=new_version_id, created_at=created_at,
                           mint_node_id=mint_node_id)
        record_plan_version_adoption(
            conn, plan_version_id=draft.plan_version_id, action=action.action,
            explanation=(
                f"The user chose to {action.action.replace('_', ' ')} "
                f"{action.subject_ref!r}, which opens a new draft."),
            observed_at=action.observed_at, user_id=action.user_id,
            component_version=component_version)
        return draft.plan_version_id

    draft = open_draft(conn, from_version=action.plan_version,
                       new_version_id=new_version_id, created_at=created_at,
                       mint_node_id=mint_node_id)
    target = next(
        (node for node in nodes_for_version(conn, draft.plan_version_id)
         if node.origin_node_id == action.subject_ref), None)
    if target is None:
        raise FrozenVersionImmutable(
            f"review action {action.review_action_id!r} names node "
            f"{action.subject_ref!r}, which this version does not contain")

    import dataclasses

    before = {"display_label": target.display_label, "node_type": target.node_type}
    if action.action == RENAME:
        edited = dataclasses.replace(
            target, display_label=action.payload["display_label"])
    elif action.action == IGNORE:
        edited = dataclasses.replace(
            target, node_type="ignored", accepts_placement=False,
            existing_path=None)
    else:
        raise FrozenVersionImmutable(
            f"action {action.action!r} has no writer in this task; every tree edit "
            "action gets one, and an unhandled action must not silently no-op")
    write_node(conn, edited)
    record_tree_edit(
        conn, action=action.action, node_id=edited.node_id,
        plan_version_id=draft.plan_version_id, before=before,
        after={"display_label": edited.display_label,
               "node_type": edited.node_type},
        explanation=(
            f"The user applied {action.action!r} to "
            f"{before['display_label']!r} on the {action.surface} surface."),
        observed_at=action.observed_at, user_id=action.user_id,
        component_version=component_version,
        correction_scope=action.correction_scope,
        correction_subject=action.subject_ref, polarity="accept")
    return draft.plan_version_id
```

- [ ] **Step 5: Write the diff**

```python
# src/tree_design/diff.py
"""§8.8's node-level diff, keyed by lineage rather than by identity.

P10 emits nodes added, removed, renamed, re-parented, re-templated, re-ordered
and type-changed. §8.8's file-level consequence — "twenty-three files now require
renewed review because their previous destination no longer exists" — is computed
by P11 from this diff against its own placement decisions. P10 holds no placement
decision and computes none of it.

Every entry carries a semantic undo label, because a diff the user cannot act on
is a report rather than a control.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass

from tree_design.records import Node
from tree_design.store import nodes_for_version
from tree_design.vocabulary import (
    DIFF_ADDED,
    DIFF_REMOVED,
    DIFF_RENAMED,
    DIFF_REORDERED,
    DIFF_REPARENTED,
    DIFF_RETEMPLATED,
    DIFF_TYPE_CHANGED,
)


@dataclass(frozen=True)
class NodeDiffEntry:
    kind: str
    node_id: str
    origin_node_id: str
    before: Mapping[str, object] | None
    after: Mapping[str, object] | None
    undo_label: str


def _template_key(node: Node) -> tuple | None:
    context = node.template_context
    if context is None:
        return None
    return (context.binding_id, context.template_id, context.template_version,
            context.fragment_id, context.fragment_version, context.dimension_index)


def diff_versions(conn: sqlite3.Connection, *, before: str,
                  after: str) -> tuple[NodeDiffEntry, ...]:
    """Compare two versions by `origin_node_id`, which is what survives a copy."""
    old = {node.origin_node_id: node for node in nodes_for_version(conn, before)}
    new = {node.origin_node_id: node for node in nodes_for_version(conn, after)}
    entries: list[NodeDiffEntry] = []

    for origin, node in sorted(new.items()):
        if origin not in old:
            entries.append(NodeDiffEntry(
                DIFF_ADDED, node.node_id, origin, None,
                {"display_label": node.display_label, "node_type": node.node_type},
                f'Undo adding "{node.display_label}"'))
            continue
        previous = old[origin]
        if previous.display_label != node.display_label:
            entries.append(NodeDiffEntry(
                DIFF_RENAMED, node.node_id, origin,
                {"display_label": previous.display_label},
                {"display_label": node.display_label},
                f'Undo rename of "{previous.display_label}"'))
        if previous.node_type != node.node_type:
            entries.append(NodeDiffEntry(
                DIFF_TYPE_CHANGED, node.node_id, origin,
                {"node_type": previous.node_type},
                {"node_type": node.node_type},
                f'Undo changing "{node.display_label}" to {node.node_type}'))
        old_parent = old.get(previous.origin_node_id)
        previous_parent_origin = _parent_origin(old, previous)
        current_parent_origin = _parent_origin(new, node)
        if previous_parent_origin != current_parent_origin:
            entries.append(NodeDiffEntry(
                DIFF_REPARENTED, node.node_id, origin,
                {"parent_origin": previous_parent_origin},
                {"parent_origin": current_parent_origin},
                f'Undo moving "{node.display_label}"'))
        if previous.ordinal != node.ordinal:
            entries.append(NodeDiffEntry(
                DIFF_REORDERED, node.node_id, origin,
                {"ordinal": previous.ordinal}, {"ordinal": node.ordinal},
                f'Undo reordering "{node.display_label}"'))
        if _template_key(previous) != _template_key(node):
            entries.append(NodeDiffEntry(
                DIFF_RETEMPLATED, node.node_id, origin,
                {"template_context": _template_key(previous)},
                {"template_context": _template_key(node)},
                f'Undo the recipe change on "{node.display_label}"'))

    for origin, node in sorted(old.items()):
        if origin not in new:
            entries.append(NodeDiffEntry(
                DIFF_REMOVED, node.node_id, origin,
                {"display_label": node.display_label, "node_type": node.node_type},
                None, f'Undo removing "{node.display_label}"'))

    return tuple(entries)


def _parent_origin(by_origin: Mapping[str, Node], node: Node) -> str | None:
    """The parent's LINEAGE id, so a version copy is not read as a re-parenting."""
    if node.parent_node_id is None:
        return None
    for candidate in by_origin.values():
        if candidate.node_id == node.parent_node_id:
            return candidate.origin_node_id
    return node.parent_node_id
```

- [ ] **Step 6: Run and verify GREEN**

Run: `python3.12 -m pytest -q tests/p10/test_p10_versions.py`

Expected: PASS, thirteen tests. `test_a_copied_node_keeps_its_lineage_and_gets_a_new_identity` is the one that proves the diff can work at all: a diff keyed on `node_id` would report every node of every draft as added and every node of its predecessor as removed.

- [ ] **Step 7: Commit**

```bash
git add src/tree_design/store.py src/tree_design/diff.py \
        tests/p10/p13_fixtures.py tests/p10/test_p10_versions.py
git commit -m "feat(p10): version user tree edits without rewriting evidence"
```

### Task 14: The §6.1 destination profile, redacted at the boundary

**Files:**
- Create: `src/tree_design/profiles.py`
- Create: `tests/p10/test_p10_profiles.py`

**Interfaces:**

*Consumes:* `tree_design.records.Node`, `tree_design.store.nodes_for_version`, `tree_design.upstream.AcceptedGroup`, `tree_design.vocabulary.HANDLING_CLASSES`.

*Produces:*

```python
@dataclass(frozen=True)
class DestinationProfile:
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
class AnchorExcerpt:
    observation_key: str
    node_id: str

def build_profiles(conn, *, plan_version_id, groups_by_id, document_types_by_node,
                   user_edits_by_node, node_scoped_rejections) -> tuple[DestinationProfile, ...]: ...
def redacted_for_egress(profile, *, protected_handling_classes) -> DestinationProfile: ...
```

**Done-means:** DM1 (the profile round-trips), and the profile half of the P10 → P11 seam.

- [ ] **Step 1: Write the failing profile tests**

```python
# tests/p10/test_p10_profiles.py
"""P10 Task 14 — the profile is P10's alone (resolution B4).

Every §6.1 ingredient — template, expected field values, accepted group
memberships, user-selected label, known exclusions, privacy restrictions — is a
value P10 already holds at freeze. None is produced by placement. P11 receives
the profile, builds the §6.2 retrieval index over it, and carries no profiles in
its own plan-version state.

Excerpts are cited by `observation_key`, which is P4's durable citation handle.
`observation_id` is not it: an id that changes between runs cannot bind a
citation to what was actually released.
"""
from __future__ import annotations

import pytest

from tree_design.profiles import build_profiles, redacted_for_egress
from tree_design.records import ExpectedValue, Node, PlanVersion, TemplateContext
from tree_design.schema import create_tree_schema
from tree_design.store import write_node, write_plan_version
from tree_design.upstream import AcceptedGroup, GroupMember

T0 = "2026-08-27T00:00:00Z"
GROUP = AcceptedGroup(
    group_id="g_phys", label="PHYS 1401 course", domain="academic",
    members=(GroupMember("lecture", "h_lecture", "direct-anchor"),
             GroupMember("hw", "h_hw", "context-supported")),
    anchor_facts=("fact_g_phys",), excluded_members=("duke-essay",),
)


@pytest.fixture()
def seeded(conn):
    create_tree_schema(conn)
    write_plan_version(conn, PlanVersion(
        plan_version_id="plan_1", predecessor_id=None, state="draft",
        created_at=T0, cross_folder_moves=False, selection_id="sel_1"))
    write_node(conn, Node(
        node_id="n_root", plan_version_id="plan_1", node_type="proposed",
        display_label="Academics", parent_node_id=None,
        root_anchor="root_documents", ordinal=0,
        associated_group_ids=("g_phys",),
        explanation="The accepted PHYS 1401 group lives beneath this branch.",
        node_role="ordinary", accepts_placement=True,
        handling_class="personal_non_sensitive", origin_node_id="n_root"))
    write_node(conn, Node(
        node_id="n_hw", plan_version_id="plan_1", node_type="proposed",
        display_label="Homework", parent_node_id="n_root",
        root_anchor="root_documents", ordinal=1,
        associated_group_ids=("g_phys",),
        explanation="Six files in the accepted group carry work type = Homework.",
        node_role="ordinary", accepts_placement=True,
        handling_class="personal_non_sensitive", origin_node_id="n_hw",
        dimension_role="artifact_kind", dimension="work_type",
        expected_values=(ExpectedValue("work_type", "Homework"),),
        template_context=TemplateContext(
            binding_id="btb_1", template_id="academic-coursework",
            template_version=1, dimension_index=1,
            fragment_id="artifact-kind", fragment_version=1)))
    return conn


def _build(conn, **overrides):
    kwargs = dict(
        plan_version_id="plan_1", groups_by_id={"g_phys": GROUP},
        document_types_by_node={"n_hw": ("Homework", "Problem set")},
        anchor_excerpts_by_node={"n_hw": ("obs-1", "obs-2")},
        user_edits_by_node={"n_hw": ("ra_rename_n_hw",)},
        node_scoped_rejections={"n_hw": ("quiz-2",)},
    )
    kwargs.update(overrides)
    return {p.node_id: p for p in build_profiles(conn, **kwargs)}


def test_a_profile_carries_every_61_ingredient(seeded):
    profile = _build(seeded)["n_hw"]
    assert profile.display_label == "Homework"
    assert profile.domains == ("academic",)
    assert profile.template_binding == "btb_1"
    assert profile.template_fields == ("work_type",)
    assert profile.expected_values == (ExpectedValue("work_type", "Homework"),)
    assert profile.accepted_group_ids == ("g_phys",)
    assert profile.group_labels == ("PHYS 1401 course",)
    assert profile.representative_files == ("hw", "lecture")
    assert profile.anchor_files == ("lecture",)
    assert profile.known_document_types == ("Homework", "Problem set")
    assert profile.user_edits == ("ra_rename_n_hw",)


def test_parent_and_child_context_carry_labels_dimensions_and_values(seeded):
    profiles = _build(seeded)
    child = profiles["n_hw"]
    assert [c.display_label for c in child.parent_context] == ["Academics"]
    parent = profiles["n_root"]
    assert [c.display_label for c in parent.child_context] == ["Homework"]
    assert parent.child_context[0].dimension == "work_type"
    assert parent.child_context[0].expected_values == (
        ExpectedValue("work_type", "Homework"),)


def test_exclusions_union_the_groups_and_the_nodes_own_rejections(seeded):
    """§6.1 and §8.7: `known_exclusions[]` is P9's derived `excluded_members[]`
    together with the rejections the user recorded against THIS node."""
    profile = _build(seeded)["n_hw"]
    assert set(profile.known_exclusions) == {"duke-essay", "quiz-2"}


def test_anchor_excerpts_are_cited_by_observation_key(seeded):
    profile = _build(seeded)["n_hw"]
    assert [e.observation_key for e in profile.anchor_excerpts] == ["obs-1", "obs-2"]
    assert all(hasattr(e, "observation_key") for e in profile.anchor_excerpts)
    assert not any(hasattr(e, "observation_id") for e in profile.anchor_excerpts)


def test_restrictions_carry_the_five_fields_p11_reads(seeded):
    """Resolution B6: P11 consumes `accepts_placement`, `node_role`,
    `disposition`, `expected_values[]` and `handling_class` rather than
    re-deriving any of them."""
    profile = _build(seeded)["n_hw"]
    assert profile.restrictions.accepts_placement is True
    assert profile.restrictions.node_role == "ordinary"
    assert profile.restrictions.disposition is None
    assert profile.restrictions.handling_class == "personal_non_sensitive"
    assert profile.expected_values


def test_a_purpose_branch_carries_several_domains_and_invents_no_primary(seeded):
    """§5.6 and §6.1: a mixed purpose branch carries `domains[]` plus the
    binding, rather than being forced to name one primary domain."""
    apps = AcceptedGroup(
        group_id="g_apps", label="Columbia application",
        domain="college_applications",
        members=(GroupMember("transcript", "h_t", "direct-anchor"),),
        anchor_facts=("fact_g_apps",), excluded_members=())
    write_node(seeded, Node(
        node_id="n_packet", plan_version_id="plan_1", node_type="proposed",
        display_label="Grad school packet", parent_node_id=None,
        root_anchor="root_documents", ordinal=2,
        associated_group_ids=("g_phys", "g_apps"),
        explanation="A purpose-coherent packet spanning two schemas.",
        node_role="ordinary", accepts_placement=True,
        handling_class="personal_non_sensitive", origin_node_id="n_packet"))
    profile = _build(seeded, groups_by_id={"g_phys": GROUP, "g_apps": apps})["n_packet"]
    assert profile.domains == ("academic", "college_applications")


def test_a_protected_profile_carries_no_filename_or_excerpt_to_egress(seeded):
    """§8.4 and §5.2: redaction happens at the BOUNDARY, not in the renderer. A
    renderer that redacts is one code path away from a prompt builder that does
    not."""
    write_node(seeded, Node(
        node_id="n_ident", plan_version_id="plan_1", node_type="protected",
        display_label="Identity", parent_node_id=None,
        root_anchor="root_documents", ordinal=3, associated_group_ids=("g_phys",),
        explanation="Files carrying identity documents were isolated here.",
        node_role="ordinary", accepts_placement=False,
        handling_class="highly_sensitive_credential_bearing",
        origin_node_id="n_ident"))
    profile = _build(seeded)["n_ident"]
    assert profile.representative_files
    safe = redacted_for_egress(profile, protected_handling_classes=frozenset({
        "sensitive_personal", "highly_sensitive_credential_bearing"}))
    assert safe.representative_files == ()
    assert safe.anchor_files == ()
    assert safe.anchor_excerpts == ()
    assert safe.known_exclusions == ()
    assert safe.display_label == "Identity"       # the label the user chose stays
    assert safe.restrictions.handling_class == "highly_sensitive_credential_bearing"


def test_an_unprotected_profile_passes_the_boundary_unchanged(seeded):
    profile = _build(seeded)["n_hw"]
    safe = redacted_for_egress(profile, protected_handling_classes=frozenset({
        "sensitive_personal", "highly_sensitive_credential_bearing"}))
    assert safe == profile


def test_a_profile_holds_no_filesystem_path(seeded):
    import dataclasses

    profile = _build(seeded)["n_hw"]
    serialised = repr(dataclasses.asdict(profile))
    assert "/" not in serialised.replace("//", "")
```

- [ ] **Step 2: Run and verify RED**

Run: `python3.12 -m pytest -q tests/p10/test_p10_profiles.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'tree_design.profiles'`.

- [ ] **Step 3: Write the profile builder**

```python
# src/tree_design/profiles.py
"""§6.1's destination profile. P10 emits it; P11 indexes it.

The split matters: the §6.2 retrieval index is a placement MECHANISM, and the
profile is a DESCRIPTION of what the user approved. Resolution B4 puts the
profile here because every ingredient is a value P10 already holds at freeze —
template, expected field values, group memberships, the user-selected label,
known exclusions, privacy restrictions. None of it is produced by placement.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace

from tree_design.records import ExpectedValue, Node
from tree_design.store import nodes_for_version
from tree_design.upstream import AcceptedGroup


@dataclass(frozen=True)
class NodeContext:
    """One ancestor or child, as §6.1's "parent and child meanings"."""

    node_id: str
    display_label: str
    dimension: str | None
    expected_values: tuple[ExpectedValue, ...]


@dataclass(frozen=True)
class AnchorExcerpt:
    """A P9 direct anchor's cited evidence, addressed by P4's durable handle."""

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


def _context(node: Node) -> NodeContext:
    return NodeContext(
        node_id=node.node_id, display_label=node.display_label,
        dimension=node.dimension, expected_values=node.expected_values,
    )


def build_profiles(
    conn: sqlite3.Connection,
    *,
    plan_version_id: str,
    groups_by_id: Mapping[str, AcceptedGroup],
    document_types_by_node: Mapping[str, Sequence[str]],
    anchor_excerpts_by_node: Mapping[str, Sequence[str]],
    user_edits_by_node: Mapping[str, Sequence[str]],
    node_scoped_rejections: Mapping[str, Sequence[str]],
) -> tuple[DestinationProfile, ...]:
    """One profile per node in this version. Every field from a value P10 holds."""
    nodes = nodes_for_version(conn, plan_version_id)
    by_id = {node.node_id: node for node in nodes}
    profiles: list[DestinationProfile] = []

    for node in nodes:
        groups = [groups_by_id[gid] for gid in node.associated_group_ids
                  if gid in groups_by_id]
        ancestors: list[NodeContext] = []
        current = by_id.get(node.parent_node_id or "")
        while current is not None:
            ancestors.append(_context(current))
            current = by_id.get(current.parent_node_id or "")
        children = tuple(
            _context(child) for child in nodes if child.parent_node_id == node.node_id
        )
        members = sorted({m.file_id for g in groups for m in g.members})
        anchors = sorted({
            m.file_id for g in groups for m in g.members
            if m.basis == "direct-anchor"
        })
        exclusions = sorted(
            {excluded for g in groups for excluded in g.excluded_members}
            | set(node_scoped_rejections.get(node.node_id, ()))
        )
        context = node.template_context
        profiles.append(DestinationProfile(
            node_id=node.node_id,
            display_label=node.display_label,
            domains=tuple(sorted({g.domain for g in groups if g.domain})),
            template_binding=None if context is None else context.binding_id,
            template_fields=() if node.dimension is None else (node.dimension,),
            expected_values=node.expected_values,
            parent_context=tuple(ancestors),
            child_context=children,
            accepted_group_ids=tuple(g.group_id for g in groups),
            group_labels=tuple(g.label for g in groups),
            representative_files=tuple(members),
            anchor_files=tuple(anchors),
            anchor_excerpts=tuple(
                AnchorExcerpt(observation_key=key, node_id=node.node_id)
                for key in anchor_excerpts_by_node.get(node.node_id, ())),
            known_document_types=tuple(document_types_by_node.get(node.node_id, ())),
            known_exclusions=tuple(exclusions),
            user_edits=tuple(user_edits_by_node.get(node.node_id, ())),
            restrictions=Restrictions(
                handling_class=node.handling_class,
                accepts_placement=node.accepts_placement,
                node_role=node.node_role,
                disposition=node.disposition,
            ),
        ))
    return tuple(profiles)


def redacted_for_egress(profile: DestinationProfile, *,
                        protected_handling_classes: frozenset[str]
                        ) -> DestinationProfile:
    """§8.4 and §5.2, enforced at the boundary rather than at the renderer.

    A profile whose handling class is protected must not carry raw filenames or
    content into anything bound for a cloud prompt. Doing this in the renderer
    would leave every other consumer — the dossier builder above all — one code
    path away from sending exactly what §5.2 says not to send.

    The display label survives, because the user chose it and it is not evidence.
    """
    if profile.restrictions.handling_class not in protected_handling_classes:
        return profile
    return replace(
        profile,
        representative_files=(),
        anchor_files=(),
        anchor_excerpts=(),
        known_exclusions=(),
        known_document_types=(),
    )
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python3.12 -m pytest -q tests/p10/test_p10_profiles.py`

Expected: PASS, nine tests.

- [ ] **Step 5: Commit**

```bash
git add src/tree_design/profiles.py tests/p10/test_p10_profiles.py
git commit -m "feat(p10): publish closed destination profiles"
```

### Task 15: Freeze, the legality projection, and the two P2 envelopes

**Files:**
- Create: `src/tree_design/freeze.py`
- Create: `src/tree_design/stage_output.py`
- Create: `tests/p10/test_p10_freeze.py`
- Create: `tests/integration/test_p10_p2_replay.py`

**Interfaces:**

*Consumes:* `tree_design.store` (`nodes_for_version`, `freeze_version`), `tree_design.provenance.record_plan_version_adoption`, `eval_harness.stage_output.record_stage_output` / `DimensionValue`, `eval_harness.run.VERSION_TUPLE_FIELDS`.

*Produces:*

```python
class FreezeRefused(RuntimeError):
    reasons: tuple[str, ...]

@dataclass(frozen=True)
class FreezeRecord:
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

def validate_for_freeze(conn, *, plan_version_id, residual_configuration,
                        approved_branch_ids) -> tuple[str, ...]: ...
def freeze(conn, *, plan_version_id, created_at, user_id, component_version,
           residual_configuration, approved_branch_ids) -> FreezeRecord: ...
def legal_destination_ids(record: FreezeRecord) -> frozenset[str]: ...
def is_legal_destination(record: FreezeRecord, node_id: str) -> bool: ...

def emit_tree_design_stage(conn, *, run_id, subject_ref, outcome, budget_state,
                           inputs, version_tuple_ref, payload, dimension_value) -> int: ...
def emit_template_generation_stage(conn, *, run_id, subject_ref, outcome,
                                   budget_state, inputs, version_tuple_ref,
                                   payload, dimension_value) -> int: ...
```

**Done-means:** DM3 (freeze enforceable by ID lookup alone), DM10 (P2 can replay and score tree and template quality), DM11 (no published node carries a path), DM12 (a disabled residual template is unreachable), DM17.

- [ ] **Step 1: Write the failing freeze tests**

```python
# tests/p10/test_p10_freeze.py
"""P10 Task 15 — the freeze guarantee, stated as a set membership test.

§5.12: "Freeze records the approved hierarchy and prevents later systems from
inventing new destinations outside it." §6.2 states the same negatively: the
engine "is not allowed to invent a new `Math Stuff` folder merely because the
file looks mathematical."

The legal set is exactly `{node_id : plan_version = frozen version,
accepts_placement = true}`. Validating a destination is an ID membership test —
no facts, no templates, no filesystem — which is what makes it cheap enough for
P11 to run on every candidate and impossible for P11 to get wrong.
"""
from __future__ import annotations

import json

import pytest

from tree_design.freeze import (
    FreezeRefused,
    freeze,
    is_legal_destination,
    legal_destination_ids,
    validate_for_freeze,
)
from tree_design.records import Node, PlanVersion
from tree_design.schema import create_tree_schema
from tree_design.store import nodes_for_version, write_node, write_plan_version

T0 = "2026-08-27T00:00:00Z"
COMMON = dict(created_at=T0, user_id="jy", component_version="p10-1")


def _node(node_id, label, *, node_type="proposed", role="ordinary", parent=None,
          disposition=None, refinement=("refined", "The groups justify it.")):
    return Node(
        node_id=node_id, plan_version_id="plan_1", node_type=node_type,
        display_label=label, parent_node_id=parent, root_anchor="root_documents",
        ordinal=0, associated_group_ids=(),
        explanation=f"{label} appeared from the accepted groups beneath it.",
        node_role=role, accepts_placement=node_type != "ignored",
        handling_class="personal_non_sensitive", origin_node_id=node_id,
        disposition=disposition,
        refinement_disposition=refinement[0], refinement_reason=refinement[1],
    )


@pytest.fixture()
def seeded(conn):
    create_tree_schema(conn)
    write_plan_version(conn, PlanVersion(
        plan_version_id="plan_1", predecessor_id=None, state="draft",
        created_at=T0, cross_folder_moves=False, selection_id="sel_1"))
    write_node(conn, _node("n_root", "Academics"))
    write_node(conn, _node("n_a", "Columbia", parent="n_root"))
    write_node(conn, _node("n_ignored", "Downloads", node_type="ignored"))
    write_node(conn, _node("n_res", "Review Later", role="residual",
                           disposition="physical-destination"))
    return conn


def _freeze(conn, **overrides):
    kwargs = dict(
        plan_version_id="plan_1",
        residual_configuration={"Review Later": "enable", "Reading Inbox": "disable"},
        approved_branch_ids=("n_root", "n_a", "n_ignored", "n_res"),
    )
    kwargs.update(overrides)
    return freeze(conn, **kwargs, **COMMON)


def test_the_legal_set_is_exactly_the_placeable_nodes(seeded):
    record = _freeze(seeded)
    assert legal_destination_ids(record) == {"n_root", "n_a", "n_res"}
    assert "n_ignored" not in legal_destination_ids(record)


def test_legality_is_decided_without_facts_templates_or_the_filesystem(seeded):
    """DM3. The record is a value; the test is set membership. A caller holding
    only the record can decide an arbitrary string."""
    record = _freeze(seeded)
    assert is_legal_destination(record, "n_a") is True
    assert is_legal_destination(record, "n_ignored") is False
    assert is_legal_destination(record, "Math Stuff") is False
    assert is_legal_destination(record, "") is False


def test_an_ignored_node_is_visible_context_and_not_a_destination(seeded):
    record = _freeze(seeded)
    assert "n_ignored" in record.node_ids
    assert "n_ignored" not in record.legal_destination_ids


def test_a_disabled_residual_template_has_no_node_and_no_legality(seeded):
    record = _freeze(seeded)
    assert "Reading Inbox" in record.residual_configuration
    assert record.residual_configuration["Reading Inbox"] == "disable"
    labels = {n.display_label for n in nodes_for_version(seeded, "plan_1")}
    assert "Reading Inbox" not in labels


def test_freeze_requires_an_explicit_action_and_never_auto_completes(seeded):
    """§8.6: "Cost exhaustion must never turn into lower-quality automatic
    classification", and §5.12 gives freeze to the user: "When the user is
    satisfied, they freeze the tree."""
    before = seeded.execute(
        "SELECT state FROM plan_versions WHERE plan_version_id = 'plan_1'"
    ).fetchone()["state"]
    assert before == "draft"
    _freeze(seeded)
    after = seeded.execute(
        "SELECT state FROM plan_versions WHERE plan_version_id = 'plan_1'"
    ).fetchone()["state"]
    assert after == "frozen"


def test_an_unexplained_node_blocks_freeze(seeded):
    seeded.execute(
        "UPDATE tree_nodes SET explanation = ' ' WHERE node_id = 'n_a'")
    reasons = validate_for_freeze(
        seeded, plan_version_id="plan_1",
        residual_configuration={}, approved_branch_ids=("n_root", "n_a"))
    assert any("explanation" in reason for reason in reasons)


def test_an_approved_branch_without_a_depth_disposition_blocks_freeze(seeded):
    seeded.execute(
        "UPDATE tree_nodes SET refinement_disposition = NULL, "
        "refinement_reason = NULL WHERE node_id = 'n_root'")
    with pytest.raises(FreezeRefused) as excinfo:
        _freeze(seeded)
    assert any("n_root" in reason for reason in excinfo.value.reasons)


def test_a_cycle_or_dangling_parent_blocks_freeze(seeded):
    seeded.execute(
        "UPDATE tree_nodes SET parent_node_id = 'n_missing' WHERE node_id = 'n_a'")
    with pytest.raises(FreezeRefused) as excinfo:
        _freeze(seeded)
    assert any("n_missing" in reason for reason in excinfo.value.reasons)


def test_a_residual_node_without_a_disposition_blocks_freeze(seeded):
    seeded.execute(
        "UPDATE tree_nodes SET disposition = NULL WHERE node_id = 'n_res'")
    with pytest.raises(FreezeRefused) as excinfo:
        _freeze(seeded)
    assert any("disposition" in reason for reason in excinfo.value.reasons)


def test_a_useful_shallow_scaffold_freezes(seeded):
    """DM17: one refined, one shallow-by-choice, one refine-later branch, each
    with a reason, freeze together. Completeness does not require equal depth."""
    write_node(seeded, _node("n_s", "Receipts",
                             refinement=("shallow-by-choice",
                                         "Twelve receipts need no vendor level.")))
    write_node(seeded, _node("n_l", "Media",
                             refinement=("refine-later",
                                         "Not enough validated facts yet.")))
    record = _freeze(seeded, approved_branch_ids=(
        "n_root", "n_a", "n_ignored", "n_res", "n_s", "n_l"))
    assert {"n_s", "n_l"} <= set(record.node_ids)


def test_the_freeze_record_carries_p3s_cross_folder_permission(seeded):
    """§8.8's "Placement policy settings". P3 records it, P10 stores it here,
    P12 enforces it at mutation time."""
    record = _freeze(seeded)
    assert record.cross_folder_moves is False
    assert record.selection_id == "sel_1"


def test_a_serialised_frozen_tree_holds_no_separator_composed_destination(seeded):
    """DM11. `existing_path` on an `existing` node is the one observed path, and
    there is none in this fixture."""
    import dataclasses

    record = _freeze(seeded)
    serialised = json.dumps(
        {k: sorted(v) if isinstance(v, (set, frozenset)) else v
         for k, v in dataclasses.asdict(record).items()},
        default=list)
    assert "/" not in serialised
    assert "\\\\" not in serialised


def test_freeze_appends_a_plan_version_adoption_record(seeded):
    _freeze(seeded)
    rows = seeded.execute(
        "SELECT * FROM events WHERE event_type = 'destination-tree edit' "
        "AND correction_scope = 'corpus'").fetchall()
    assert len(rows) == 1
    assert json.loads(rows[0]["explanation"].split("\n", 1)[1])["action"] == (
        "adopt_version")
```

- [ ] **Step 2: Write the failing P2 replay test**

```python
# tests/integration/test_p10_p2_replay.py
"""P10 -> P2. The envelope's vocabulary is P2's, and P10 maps into it.

`record_stage_output` takes `inputs` and `budget_state` as REQUIRED keywords. A
caller that omits either raises TypeError, and a P10 that guessed at them would
break P2 Done-means 6: a run whose only change is a lower ceiling must produce
zero new divergences, which is only true if a deferral never reaches a quality
verdict.
"""
from __future__ import annotations

from dataclasses import dataclass

import pytest

from eval_harness.vocabulary import DIMENSIONS, STAGE_IDS
from tree_design.stage_output import (
    emit_template_generation_stage,
    emit_tree_design_stage,
)


@dataclass(frozen=True)
class RunIdentity:
    run_id: str
    version_tuple_ref: str


@pytest.fixture()
def run(conn):
    """The minimal P2 run identity these envelopes attach to.

    Built against the LIVE signatures: `record_version_tuple(conn, **fields)`
    takes exactly `VERSION_TUPLE_FIELDS` (seven), and `start_run` returns a
    `run_id` string rather than an object. Reconstructing either from memory is
    the defect this project keeps paying for.
    """
    from database_agent.budget import all_ceilings
    from eval_harness.run import VERSION_TUPLE_FIELDS, record_version_tuple, start_run

    fields = {name: "fixture" for name in VERSION_TUPLE_FIELDS}
    fields["extractor_versions"] = {}
    fields["analysis_tiers_enabled"] = ["filesystem"]
    version_tuple_ref = record_version_tuple(conn, **fields)
    run_id = start_run(
        conn, bundle_id="bundle-1", run_kind="replay",
        version_tuple_ref=version_tuple_ref,
        budget_ceilings=all_ceilings(conn),
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        pinned_plan_id=None, pinned_plan_version=None)
    return RunIdentity(run_id=run_id, version_tuple_ref=version_tuple_ref)


def test_p10_emits_only_p2s_two_stage_ids(conn, run):
    """`P10` is not a stage id. A part name in that field would leave two of
    §8.5's ten stages with no producer and P2's `attributed_stage` unable to
    name where a tree error began."""
    assert "P10" not in STAGE_IDS
    assert "template_generation" in STAGE_IDS and "tree_design" in STAGE_IDS


def test_a_produced_branch_carries_its_inputs_and_a_tree_dimension_value(conn, run):
    stage_output_id = emit_tree_design_stage(
        conn, run_id=run.run_id, subject_ref="n_root", outcome="produced",
        budget_state="within_ceiling",
        inputs=("grouping:g_phys", "factual_validation:lecture"),
        version_tuple_ref=run.version_tuple_ref,
        payload={"display_label": "Academics"},
        dimension_value={"accepted": True})
    row = conn.execute(
        "SELECT * FROM stage_output WHERE stage_output_id = ?",
        (stage_output_id,)).fetchone()
    assert row["stage_id"] == "tree_design"
    assert "grouping:g_phys" in row["inputs"]
    assert row["budget_state"] == "within_ceiling"
    values = conn.execute(
        "SELECT * FROM stage_dimension_value WHERE stage_output_id = ?",
        (stage_output_id,)).fetchall()
    assert [v["dimension"] for v in values] == ["tree"]
    assert "tree" in DIMENSIONS


def test_a_rejected_template_abstains_within_the_ceiling(conn, run):
    """A candidate template rejected by V1-V6 is an evidential abstention. It is
    a design judgement and belongs in the quality score."""
    stage_output_id = emit_template_generation_stage(
        conn, run_id=run.run_id, subject_ref="n_root", outcome="abstained",
        budget_state="within_ceiling", inputs=("grouping:g_phys",),
        version_tuple_ref=run.version_tuple_ref,
        payload={"failed": ["V2"]}, dimension_value={"accepted": False})
    row = conn.execute(
        "SELECT * FROM stage_output WHERE stage_output_id = ?",
        (stage_output_id,)).fetchone()
    assert row["outcome"] == "abstained"
    assert row["budget_state"] == "within_ceiling"


def test_a_template_deferred_branch_is_deferred_and_never_abstained(conn, run):
    """§8.6 and P2 Done-means 6. A ceiling-truncated pass must never be scored as
    a design judgement, so P2 refuses the wrong pairing at the writer."""
    stage_output_id = emit_template_generation_stage(
        conn, run_id=run.run_id, subject_ref="n_root", outcome="deferred",
        budget_state="ceiling_reached", inputs=("grouping:g_phys",),
        version_tuple_ref=run.version_tuple_ref,
        payload={"reason": "template-deferred"}, dimension_value=None)
    row = conn.execute(
        "SELECT * FROM stage_output WHERE stage_output_id = ?",
        (stage_output_id,)).fetchone()
    assert (row["outcome"], row["budget_state"]) == ("deferred", "ceiling_reached")

    with pytest.raises(ValueError):
        emit_template_generation_stage(
            conn, run_id=run.run_id, subject_ref="n_other", outcome="abstained",
            budget_state="ceiling_reached", inputs=(),
            version_tuple_ref=run.version_tuple_ref, payload={},
            dimension_value=None)


def test_a_foreign_outcome_is_refused_by_p2s_own_writer(conn, run):
    with pytest.raises(Exception):
        emit_tree_design_stage(
            conn, run_id=run.run_id, subject_ref="n_root", outcome="template-deferred",
            budget_state="within_ceiling", inputs=(),
            version_tuple_ref=run.version_tuple_ref, payload={},
            dimension_value=None)
```

- [ ] **Step 3: Run both and verify RED**

Run: `python3.12 -m pytest -q tests/p10/test_p10_freeze.py tests/integration/test_p10_p2_replay.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'tree_design.freeze'`. The `run` fixture is written against the live `eval_harness.run` surface — `record_version_tuple(conn, **VERSION_TUPLE_FIELDS)` and `start_run(conn, *, bundle_id, run_kind, version_tuple_ref, budget_ceilings, run_settings, pinned_plan_id, pinned_plan_version) -> str`. Before running, re-confirm both with `PYTHONPATH=src python3 -c "import inspect; from eval_harness.run import start_run, record_version_tuple; print(inspect.signature(start_run))"`; if P2 has moved, fix the TEST, never `src/tree_design/`.

- [ ] **Step 4: Write freeze**

```python
# src/tree_design/freeze.py
"""Freeze: the moment the destination set becomes closed.

§5.12: "Freeze records the approved hierarchy and prevents later systems from
inventing new destinations outside it." The mechanism is not a rule anybody has
to obey; it is a set. `legal_destination_ids` is exactly
`{node_id : plan_version = frozen version, accepts_placement = true}`, and a
destination outside it has no legal expression — P11 abstains, and §6.10 calls
correct abstention a successful outcome.

Freeze records no facts, no evidence and no accepted-group evidence. §5.12: "The
facts and accepted groups remain separate from the tree." §8.8: "The evidence
database remains shared across plan versions." That is what lets the user
rearrange the same corpus tomorrow without losing an observation.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from tree_design.provenance import record_plan_version_adoption
from tree_design.store import freeze_version, nodes_for_version
from tree_design.vocabulary import ADOPT_VERSION, RESIDUAL


class FreezeRefused(RuntimeError):
    """Freeze validation failed. Every reason, not the first one."""

    def __init__(self, reasons: Sequence[str]) -> None:
        self.reasons = tuple(reasons)
        super().__init__(
            "the tree cannot be frozen yet:\n- " + "\n- ".join(self.reasons))


@dataclass(frozen=True)
class FreezeRecord:
    """§8.8's list, restricted to the rows P10 owns."""

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


def validate_for_freeze(conn: sqlite3.Connection, *, plan_version_id: str,
                        residual_configuration: Mapping[str, str],
                        approved_branch_ids: Sequence[str]) -> tuple[str, ...]:
    """Every reason this version is not freezeable, collected.

    "Complete" means every included node is legal, explainable, validated and
    approved, and every unresolved branch is explicitly marked for later
    refinement or shallow by choice. It does NOT mean every branch realises every
    template dimension, and no check here requires sibling parity.
    """
    nodes = nodes_for_version(conn, plan_version_id)
    by_id = {node.node_id: node for node in nodes}
    reasons: list[str] = []

    if not nodes:
        reasons.append("the version contains no node; there is nothing to freeze")

    seen: set[str] = set()
    for node in nodes:
        if node.node_id in seen:
            reasons.append(f"node id {node.node_id!r} appears more than once")
        seen.add(node.node_id)
        if not node.explanation.strip():
            reasons.append(
                f"node {node.node_id!r} has no explanation; §5.12 requires every "
                "node to state the facts or accepted groups that caused it")
        if node.parent_node_id is not None and node.parent_node_id not in by_id:
            reasons.append(
                f"node {node.node_id!r} names parent {node.parent_node_id!r}, "
                "which this version does not contain")
        if node.node_role == RESIDUAL and node.disposition is None:
            reasons.append(
                f"residual node {node.node_id!r} has no disposition; §7.4 makes "
                "the user choose physical destination, review-only, or "
                "leave-in-place, and the three behave differently downstream")
        if node.node_id in approved_branch_ids and node.refinement_disposition is None:
            reasons.append(
                f"approved branch {node.node_id!r} has no depth disposition; "
                "§5.8 needs an explicit `refined`, `shallow-by-choice` or "
                "`refine-later` with a reason to tell a deliberate design from "
                "unfinished work")

    # Cycle detection by walking upward from every node.
    for node in nodes:
        walked: set[str] = set()
        current = node
        while current is not None and current.parent_node_id is not None:
            if current.node_id in walked:
                reasons.append(
                    f"the ancestry of node {node.node_id!r} contains a cycle")
                break
            walked.add(current.node_id)
            current = by_id.get(current.parent_node_id)

    return tuple(dict.fromkeys(reasons))


def freeze(conn: sqlite3.Connection, *, plan_version_id: str, created_at: str,
           user_id: str, component_version: str,
           residual_configuration: Mapping[str, str],
           approved_branch_ids: Sequence[str]) -> FreezeRecord:
    """Validate, mark frozen, append the §8.8 adoption record, return the record.

    Freeze is never auto-completed. §5.12 gives the action to the user — "When
    the user is satisfied, they freeze the tree" — and §8.6 forbids a budget from
    ever standing in for that decision.
    """
    reasons = validate_for_freeze(
        conn, plan_version_id=plan_version_id,
        residual_configuration=residual_configuration,
        approved_branch_ids=approved_branch_ids)
    if reasons:
        raise FreezeRefused(reasons)

    nodes = nodes_for_version(conn, plan_version_id)
    version = conn.execute(
        "SELECT * FROM plan_versions WHERE plan_version_id = ?",
        (plan_version_id,)).fetchone()
    policies = conn.execute(
        "SELECT policy_id FROM shared_material_policies WHERE plan_version_id = ? "
        "ORDER BY policy_id", (plan_version_id,)).fetchall()

    freeze_version(conn, plan_version_id)
    record_plan_version_adoption(
        conn, plan_version_id=plan_version_id, action=ADOPT_VERSION,
        explanation="The user froze the destination tree for this plan version.",
        observed_at=created_at, user_id=user_id,
        component_version=component_version)

    return FreezeRecord(
        plan_version_id=plan_version_id,
        created_at=created_at,
        node_ids=tuple(node.node_id for node in nodes),
        legal_destination_ids=frozenset(
            node.node_id for node in nodes if node.accepts_placement),
        template_bindings=tuple(sorted({
            node.template_context.binding_id for node in nodes
            if node.template_context is not None})),
        labels_and_aliases={node.node_id: (node.display_label,) for node in nodes},
        residual_configuration=dict(residual_configuration),
        shared_material_policy_ids=tuple(row["policy_id"] for row in policies),
        cross_folder_moves=bool(version["cross_folder_moves"]),
        selection_id=version["selection_id"],
    )


def legal_destination_ids(record: FreezeRecord) -> frozenset[str]:
    """The closed set. Nothing outside it has a legal expression."""
    return record.legal_destination_ids


def is_legal_destination(record: FreezeRecord, node_id: str) -> bool:
    """An ID membership test. No facts, no templates, no filesystem access.

    §6.10: the validator "confirms that the selected node exists in the frozen
    tree". Node existence is not legality — a node with
    `accepts_placement = false` is visible context, never a destination.
    """
    return node_id in record.legal_destination_ids
```

- [ ] **Step 5: Write the P2 adapters**

```python
# src/tree_design/stage_output.py
"""P10 -> P2. Two stage ids, P2's outcome vocabulary, both required keywords.

The envelope's vocabulary is P2's, not P10's. P10 maps its own results into
`produced | abstained | deferred | not_implemented | error` and
`within_ceiling | ceiling_reached` rather than restating the separation in words
of its own:

| P10 result                                   | outcome  | budget_state    |
|----------------------------------------------|----------|-----------------|
| a template applied, or a node proposed       | produced | within_ceiling  |
| nothing proposed on the evidence (V1-V6, §5.1)| abstained| within_ceiling  |
| an §8.6 ceiling stopped the work             | deferred | ceiling_reached |

The evidential abstention and the budget deferral are two values, not one value
described twice. P2 Done-means 6 depends on exactly that: a run whose only change
is a lower ceiling must produce zero new divergences.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Sequence

from eval_harness.stage_output import DimensionValue, record_stage_output
from evidence_shape.canonical import canonical_json
from tree_design.vocabulary import (
    DIMENSION_TEMPLATE,
    DIMENSION_TREE,
    TEMPLATE_GENERATION,
    TREE_DESIGN,
)


def _emit(conn: sqlite3.Connection, *, stage_id: str, dimension: str, run_id: str,
          subject_ref: str, outcome: str, budget_state: str,
          inputs: Sequence[str], version_tuple_ref: str, payload,
          dimension_value) -> int:
    """One envelope. `inputs` and `budget_state` are required by P2's writer.

    `inputs[]` carries the `subject_ref`s of the `grouping` and
    `factual_validation` stage outputs this decision consumed, which is what lets
    P2's `attributed_stage` name where a tree error actually began rather than
    blaming the stage that surfaced it.
    """
    values = ()
    if dimension_value is not None:
        values = (DimensionValue(
            dimension=dimension, subject_ref=subject_ref, outcome=outcome,
            value=dimension_value),)
    return record_stage_output(
        conn,
        run_id=run_id,
        stage_id=stage_id,
        subject_ref=subject_ref,
        outcome=outcome,
        payload=None if payload is None else canonical_json(payload),
        version_tuple_ref=version_tuple_ref,
        inputs=tuple(inputs),
        budget_state=budget_state,
        dimension_values=values,
    )


def emit_tree_design_stage(conn: sqlite3.Connection, *, run_id: str,
                           subject_ref: str, outcome: str, budget_state: str,
                           inputs: Sequence[str], version_tuple_ref: str,
                           payload, dimension_value) -> int:
    """§8.5's `tree_design`. The subject is the branch candidate or node."""
    return _emit(conn, stage_id=TREE_DESIGN, dimension=DIMENSION_TREE,
                 run_id=run_id, subject_ref=subject_ref, outcome=outcome,
                 budget_state=budget_state, inputs=inputs,
                 version_tuple_ref=version_tuple_ref, payload=payload,
                 dimension_value=dimension_value)


def emit_template_generation_stage(conn: sqlite3.Connection, *, run_id: str,
                                   subject_ref: str, outcome: str,
                                   budget_state: str, inputs: Sequence[str],
                                   version_tuple_ref: str, payload,
                                   dimension_value) -> int:
    """§8.5's `template_generation`. The subject is the branch it was for."""
    return _emit(conn, stage_id=TEMPLATE_GENERATION, dimension=DIMENSION_TEMPLATE,
                 run_id=run_id, subject_ref=subject_ref, outcome=outcome,
                 budget_state=budget_state, inputs=inputs,
                 version_tuple_ref=version_tuple_ref, payload=payload,
                 dimension_value=dimension_value)
```

- [ ] **Step 6: Run both and verify GREEN**

Run: `python3.12 -m pytest -q tests/p10/test_p10_freeze.py tests/integration/test_p10_p2_replay.py`

Expected: PASS. `all_ceilings(conn)` returns whatever this database holds, which is legal: `start_run` validates ceiling KEYS against P1's list and validates no value, because §8.6's ceilings are hand-authored and P2 holds keys, never numbers.

- [ ] **Step 7: Commit**

```bash
git add src/tree_design/freeze.py src/tree_design/stage_output.py \
        tests/p10/test_p10_freeze.py tests/integration/test_p10_p2_replay.py
git commit -m "feat(p10): freeze the closed tree and emit replay stages"
```

### Task 16: Fixtures P11 can build against, and the no-invention guards

**Files:**
- Create: `src/tree_design/fixtures.py`
- Create: `tests/p10/test_p10_fixtures.py`
- Create: `tests/p10/test_p10_no_invention.py`
- Create: `tests/integration/test_p10_p9_tree.py`

**Interfaces:**

*Produces:*

```python
def walking_skeleton_tree() -> tuple[Node, ...]: ...
def realistic_tree() -> tuple[Node, ...]: ...
def residual_library_fixture() -> tuple[Mapping[str, ResidualTemplate], tuple[ResidualChoice, ...]]: ...
def template_library_fixture() -> TemplateCatalogue: ...
def two_version_pair() -> tuple[tuple[Node, ...], tuple[Node, ...]]: ...
def frozen_tree_fixture() -> FreezeRecord: ...
```

**Done-means:** DM2 (a)–(e) in full, DM6, DM11, and the guard half of DM4.

- [ ] **Step 1: Write the failing fixture tests**

```python
# tests/p10/test_p10_fixtures.py
"""P10 Task 16 — what P11 builds against before P10 has a pipeline.

The walking skeleton is TWO nodes, not one. Resolution B8(b): the skeleton must
exercise §6.10's margin condition rather than bypass it, and a one-node tree
leaves `margin_over_next` with no value to hold.
"""
from __future__ import annotations

import pytest

from tree_design.fixtures import (
    frozen_tree_fixture,
    realistic_tree,
    residual_library_fixture,
    template_library_fixture,
    two_version_pair,
    walking_skeleton_tree,
)
from tree_design.freeze import is_legal_destination
from tree_design.residuals import project_residual_nodes
from tree_design.vocabulary import (
    EXISTING,
    IGNORED,
    LEAVE_IN_PLACE,
    NODE_TYPES,
    PHYSICAL_DESTINATION,
    PROPOSED,
    PROTECTED,
    RESIDUAL,
    RESIDUAL_TEMPLATE_NAMES,
    REVIEW_ONLY,
    SCOPED_GENERAL,
    SHARED_MATERIAL,
    USER_CREATED,
)


def test_the_walking_skeleton_is_two_nodes_with_no_template_and_no_group():
    nodes = walking_skeleton_tree()
    assert len(nodes) == 2
    assert all(node.template_context is None for node in nodes)
    assert all(node.associated_group_ids == () for node in nodes)
    assert all(node.accepts_placement for node in nodes)


def test_the_realistic_tree_exercises_all_five_node_types():
    nodes = realistic_tree()
    assert {node.node_type for node in nodes} == set(NODE_TYPES)


def test_the_realistic_tree_has_uneven_depth_by_design():
    nodes = realistic_tree()
    by_id = {node.node_id: node for node in nodes}

    def depth(node):
        count = 0
        current = node
        while current.parent_node_id is not None:
            count += 1
            current = by_id[current.parent_node_id]
        return count

    leaves = [n for n in nodes if not any(c.parent_node_id == n.node_id for c in nodes)]
    assert len({depth(leaf) for leaf in leaves}) > 1


def test_the_realistic_tree_carries_a_scoped_general_and_a_shared_material_node():
    roles = {node.node_role for node in realistic_tree()}
    assert SCOPED_GENERAL in roles
    assert SHARED_MATERIAL in roles
    assert RESIDUAL in roles


def test_the_realistic_tree_carries_all_three_residual_dispositions():
    dispositions = {
        node.disposition for node in realistic_tree() if node.node_role == RESIDUAL
    }
    assert dispositions == {PHYSICAL_DESTINATION, REVIEW_ONLY, LEAVE_IN_PLACE}


def test_the_protected_branch_is_visible_and_not_automatically_placeable():
    protected = [n for n in realistic_tree() if n.node_type == PROTECTED]
    assert protected
    assert all(not n.accepts_placement for n in protected)


def test_the_residual_fixture_covers_every_74_action(conn):
    library, choices = residual_library_fixture()
    assert set(library) >= set(RESIDUAL_TEMPLATE_NAMES)
    actions = {choice.action for choice in choices}
    assert {"enable", "disable", "rename", "relocate", "merge",
            "replace-with-existing"} <= actions
    disabled = {c.template_name for c in choices if c.action == "disable"}
    assert disabled


def test_a_disabled_template_in_the_fixture_produces_no_node(conn):
    library, choices = residual_library_fixture()
    existing = {n.node_id: n for n in realistic_tree() if n.node_type == EXISTING}
    counter = iter(range(100))
    nodes = project_residual_nodes(
        library, choices, plan_version_id="plan_1",
        handling_class_for_template=lambda name: "personal_non_sensitive",
        mint_node_id=lambda: f"n_res_{next(counter)}",
        existing_nodes=existing)
    produced = {n.display_label for n in nodes}
    disabled = {c.template_name for c in choices if c.action == "disable"}
    assert not (produced & disabled)


def test_the_template_library_fixture_covers_the_composable_cases():
    catalogue = template_library_fixture()
    assert catalogue.fragments
    origins = {d.origin_kind for d in catalogue.definitions.values()}
    assert {"built-in", "llm-generated"} <= origins
    schemas = {row.uses_schema for row in catalogue.applicabilities.values()}
    assert len(schemas) > 1
    # One definition, two schemas, no duplication.
    by_template = {}
    for row in catalogue.applicabilities.values():
        by_template.setdefault(row.template_id, set()).add(row.uses_schema)
    assert any(len(s) > 1 for s in by_template.values())


def test_the_two_version_pair_differs_by_a_meaningful_edit():
    before, after = two_version_pair()
    before_labels = {n.origin_node_id: n.display_label for n in before}
    after_labels = {n.origin_node_id: n.display_label for n in after}
    assert before_labels != after_labels
    assert set(before_labels) & set(after_labels)


def test_the_frozen_fixture_decides_legality_by_id_alone():
    record = frozen_tree_fixture()
    assert record.legal_destination_ids
    assert is_legal_destination(record, next(iter(record.legal_destination_ids)))
    assert is_legal_destination(record, "Math Stuff") is False


def test_every_fixture_node_states_its_reason_and_shows_no_score():
    for node in (*walking_skeleton_tree(), *realistic_tree()):
        assert node.explanation.strip()
        assert not any(
            token in node.explanation.lower()
            for token in ("confidence", "score", "probability", "%"))
```

- [ ] **Step 2: Write the failing no-invention guards**

```python
# tests/p10/test_p10_no_invention.py
"""P10 Task 16 — the boundaries, checked by parsing rather than by grepping.

Every guard here is over the parsed AST. A text search matches comments and
docstrings, and it has produced a false result on this project nine times.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src" / "tree_design"
MODULES = sorted(SRC.glob("*.py"))


def _trees():
    return [(path, ast.parse(path.read_text())) for path in MODULES]


def test_no_module_imports_planning_prompts_or_domain_research():
    """`planning/domains/` is a research and authorship surface, not a runtime
    import target. A later deterministic compiler consumes ratified records and
    emits a versioned manifest; `tree_design.catalogue` reads that manifest."""
    offenders = []
    for path, tree in _trees():
        for node in ast.walk(tree):
            modules = []
            if isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)
            elif isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            for module in modules:
                if module.split(".")[0] in {"planning", "prompts", "domains"}:
                    offenders.append(f"{path.name}:{node.lineno} {module}")
    assert offenders == []


def test_no_module_imports_p11_p12_or_p13():
    """P10 publishes; it consumes nothing downstream. A runtime edge the other
    way would make P10 depend on the parts that consume its own output."""
    offenders = []
    for path, tree in _trees():
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".")[0]
                if root in {"placement", "apply_undo", "review_surface"}:
                    offenders.append(f"{path.name}:{node.lineno} {node.module}")
    assert offenders == []


def test_no_module_touches_the_filesystem():
    """P10 composes no path and reads no directory. `os.sep` is used to REJECT a
    separator, never to build one, so the check is on the modules that perform
    filesystem operations rather than on the constant."""
    forbidden_modules = {"pathlib", "shutil", "glob", "tempfile"}
    forbidden_calls = {"open", "listdir", "walk", "scandir", "mkdir", "rename",
                       "remove", "rmdir", "makedirs"}
    offenders = []
    for path, tree in _trees():
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in forbidden_modules:
                        offenders.append(f"{path.name}:{node.lineno} {alias.name}")
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module.split(".")[0] in forbidden_modules:
                    offenders.append(f"{path.name}:{node.lineno} {node.module}")
            if isinstance(node, ast.Call):
                name = getattr(node.func, "attr", getattr(node.func, "id", None))
                if name in forbidden_calls:
                    offenders.append(f"{path.name}:{node.lineno} {name}()")
    assert offenders == []


def test_no_module_composes_a_path_by_joining_labels():
    """DM11. `root_anchor` plus the ancestor label chain is what P10 publishes;
    P12 composes the path and applies §8.3's rules."""
    offenders = []
    for path, tree in _trees():
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = getattr(node.func, "attr", None)
                if name == "join" and isinstance(node.func.value, ast.Constant):
                    if node.func.value.value in ("/", "\\\\"):
                        offenders.append(f"{path.name}:{node.lineno}")
    assert offenders == []


def test_no_module_writes_a_fact_a_classification_or_a_group():
    """§3.14 and §5.12: the tree is a separate VIEW over the evidence. P10 reads
    facts, groups and classifications and writes none of them."""
    forbidden = {"facts.file_facts", "facts.values", "privacy.classification_store",
                 "grouping.store"}
    offenders = []
    for path, tree in _trees():
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module in forbidden:
                offenders.append(f"{path.name}:{node.lineno} {node.module}")
    assert offenders == []


def test_only_the_provenance_module_appends_an_event():
    offenders = []
    for path, tree in _trees():
        if path.name == "provenance.py":
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "database_agent.events":
                offenders.append(f"{path.name}:{node.lineno}")
    assert offenders == []


def test_only_the_upstream_module_names_another_parts_records():
    """One seam, one failure when an upstream name moves."""
    allowed = {"upstream.py", "template_schema.py", "stage_output.py",
               "provenance.py", "vocabulary.py", "config.py"}
    foreign_roots = {"grouping", "facts", "privacy", "scan_agent", "llm_harness",
                     "eval_harness", "database_agent"}
    offenders = []
    for path, tree in _trees():
        if path.name in allowed:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module.split(".")[0] in foreign_roots:
                    # `evidence_shape.canonical` is a shared serialisation
                    # helper, not another part's record vocabulary.
                    if node.module == "evidence_shape.canonical":
                        continue
                    offenders.append(f"{path.name}:{node.lineno} {node.module}")
    assert offenders == []


def test_no_module_holds_a_numeric_literal_beyond_zero_and_one():
    offenders = []
    for path, tree in _trees():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant):
                continue
            if isinstance(node.value, bool) or not isinstance(node.value, int):
                continue
            if node.value in (0, 1):
                continue
            offenders.append(f"{path.name}:{node.lineno} {node.value}")
    assert offenders == []
```

- [ ] **Step 3: Write the failing P9 integration test**

```python
# tests/integration/test_p10_p9_tree.py
"""P9 accepted groups -> P10 scaffold. The seam, end to end, on fixtures.

`grouping.store` does not exist yet, so the reader is `tests/p10/p9_fixtures.py`
over LIVE `grouping.records` objects. When P9 publishes a store that satisfies
`upstream.AcceptedGroupReader`, this test's first two lines change and nothing
else does. That is the swap boundary, and it is named here so nobody has to find
it later.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "p10"))

from p9_fixtures import FixtureGroupReader  # noqa: E402

from tree_design.candidates import horizontal_candidates  # noqa: E402
from tree_design.upstream import accepted_groups, rejected_group_ids  # noqa: E402


def test_accepted_groups_become_candidates_and_rejected_ones_do_not(conn):
    reader = FixtureGroupReader()
    groups = accepted_groups(reader, plan_version_id="plan_1")
    rejected = rejected_group_ids(reader, plan_version_id="plan_1")
    candidates = horizontal_candidates(
        conn, accepted=groups, existing_folders=(), user_labels=(),
        active_domains=("academic", "college_applications", "photos"),
        sensitive_group_ids=frozenset())
    subjects = {c.subject_id for c in candidates}
    assert subjects == {g.group_id for g in groups}
    assert not (subjects & rejected)


def test_the_swap_boundary_is_one_import(conn):
    """The fixture is a test module. `src/tree_design/` must never import it."""
    import ast

    src = Path(__file__).resolve().parents[2] / "src" / "tree_design"
    offenders = []
    for path in sorted(src.glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.ImportFrom) and node.module:
                if "fixtures" in node.module and node.module.startswith("p"):
                    offenders.append(f"{path.name}:{node.lineno} {node.module}")
    assert offenders == []
```

- [ ] **Step 4: Run all three and verify RED**

Run: `python3.12 -m pytest -q tests/p10/test_p10_fixtures.py tests/p10/test_p10_no_invention.py tests/integration/test_p10_p9_tree.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'tree_design.fixtures'`. The no-invention suite will already pass on the modules built so far, which is correct — it is a ratchet, not a milestone.

- [ ] **Step 5: Write the fixtures**

```python
# src/tree_design/fixtures.py
"""Golden P10 fixtures. P11 and P12 build against these before P10 runs.

Everything here is hand-authored and deterministic. Nothing reads a database,
scans a directory, or calls a model. A fixture that needed the pipeline to exist
would not be usable by the parts that are waiting for it.
"""
from __future__ import annotations

from collections.abc import Mapping

from tree_design.catalogue import TemplateCatalogue, load_catalogue
from tree_design.freeze import FreezeRecord
from tree_design.records import ExpectedValue, Node, TemplateContext
from tree_design.residuals import ResidualChoice, ResidualTemplate, build_library
from tree_design.vocabulary import (
    DISABLE,
    ENABLE,
    EXISTING,
    IGNORED,
    LEAVE_IN_PLACE,
    MERGE_RESIDUAL,
    ORDINARY,
    PHYSICAL_DESTINATION,
    PROPOSED,
    PROTECTED,
    REFINE_LATER,
    REFINED,
    RELOCATE,
    RENAME_RESIDUAL,
    REPLACE_WITH_EXISTING,
    RESIDUAL,
    RESIDUAL_DEFAULT_PARENTS,
    RESIDUAL_TEMPLATE_NAMES,
    REVIEW_ONLY,
    SCOPED_GENERAL,
    SHALLOW_BY_CHOICE,
    SHARED_MATERIAL,
    TREATMENT_RETAINED,
    TREATMENT_REVIEWED,
    USER_CREATED,
)

PLAN_1 = "plan_1"
PLAN_2 = "plan_2"
ROOT = "root_documents"


def _node(node_id, label, *, node_type=PROPOSED, role=ORDINARY, parent=None,
          ordinal=0, version=PLAN_1, explanation=None, **extra) -> Node:
    return Node(
        node_id=node_id, plan_version_id=version, node_type=node_type,
        display_label=label, parent_node_id=parent, root_anchor=ROOT,
        ordinal=ordinal,
        associated_group_ids=extra.pop("associated_group_ids", ()),
        explanation=explanation or (
            f"{label} appeared because the accepted groups beneath it share "
            "validated facts."),
        node_role=role,
        accepts_placement=extra.pop(
            "accepts_placement", node_type not in (IGNORED, PROTECTED)),
        handling_class=extra.pop("handling_class", "personal_non_sensitive"),
        origin_node_id=extra.pop("origin_node_id", node_id),
        **extra,
    )


def walking_skeleton_tree() -> tuple[Node, ...]:
    """DM2(a). TWO hand-authored frozen nodes, no template, no groups.

    Two, not one: resolution B8(b) requires the skeleton to exercise §6.10's
    margin condition rather than bypass it, and a one-node tree leaves
    `margin_over_next` with no value to hold.
    """
    return (
        _node("n_sk_a", "Documents",
              explanation="A hand-authored skeleton branch with no evidence behind it."),
        _node("n_sk_b", "Pictures", ordinal=1,
              explanation="A second skeleton branch, so a placement has a runner-up."),
    )


def realistic_tree() -> tuple[Node, ...]:
    """DM2(b). Uneven depth, all five node types, scoped General, a residual node
    with each disposition, a shared-material node, and a protected branch."""
    return (
        _node("n_academics", "Academics",
              refinement_disposition=REFINED,
              refinement_reason="Three accepted course groups justify the split."),
        _node("n_columbia", "Columbia", parent="n_academics",
              associated_group_ids=("g_phys1401",),
              dimension_role="institution", dimension="school",
              expected_values=(ExpectedValue("school", "Columbia"),),
              template_context=TemplateContext(
                  binding_id="btb_1", template_id="academic-coursework",
                  template_version=1, dimension_index=0,
                  fragment_id="subject-stage", fragment_version=1)),
        _node("n_phys", "PHYS1401", parent="n_columbia",
              associated_group_ids=("g_phys1401",),
              dimension_role="subject", dimension="subject",
              expected_values=(ExpectedValue("subject", "PHYS1401"),)),
        _node("n_general", "General", parent="n_columbia", role=SCOPED_GENERAL,
              ordinal=1,
              explanation=(
                  "Files that belong to this course area but carry no work type "
                  "yet. Scoped to Columbia, not a global catch-all.")),
        _node("n_reading", "Reading", node_type=USER_CREATED, ordinal=1,
              refinement_disposition=SHALLOW_BY_CHOICE,
              refinement_reason="Eleven articles do not need a per-topic level."),
        _node("n_school", "School", node_type=EXISTING, ordinal=2,
              existing_path="/Users/jy/Documents/School",
              explanation=(
                  "An existing folder holding 31 files; the scan reads it as "
                  "curated, which is a strong expression of your intent.")),
        _node("n_downloads", "Downloads", node_type=IGNORED, ordinal=3,
              accepts_placement=False,
              explanation="You chose to leave this folder untouched."),
        _node("n_identity", "Identity", node_type=PROTECTED, ordinal=4,
              accepts_placement=False,
              handling_class="highly_sensitive_credential_bearing",
              explanation=(
                  "Files carrying identity documents were isolated here. Names "
                  "are not shown and contents are not sent to a cloud model."),
              refinement_disposition=REFINE_LATER,
              refinement_reason="Not enough validated facts to split this yet."),
        _node("n_shared", "Shared Application Materials", role=SHARED_MATERIAL,
              ordinal=5,
              explanation=(
                  "A transcript belongs to two application packets; this branch "
                  "is the primary home the policy names.")),
        _node("n_res_sort", "Review Later", role=RESIDUAL, node_type=USER_CREATED,
              ordinal=6, disposition=PHYSICAL_DESTINATION,
              explanation="You enabled Review Later as a real destination."),
        _node("n_res_inbox", "Reading Inbox", role=RESIDUAL, node_type=USER_CREATED,
              ordinal=7, disposition=REVIEW_ONLY,
              explanation="You enabled Reading Inbox as a review-only category."),
        _node("n_res_locked", "Unsupported or Encrypted", role=RESIDUAL,
              node_type=USER_CREATED, ordinal=8, disposition=LEAVE_IN_PLACE,
              explanation=(
                  "Unreadable files are recorded here and left where they are.")),
    )


def _slots() -> Mapping[str, Mapping[str, object]]:
    return {
        name: {
            "display_name": name,
            "default_parent_location": RESIDUAL_DEFAULT_PARENTS.get(name),
            "accepted_evidence_patterns": ("fixture.pattern",),
            "expected_file_types": ("application/pdf",),
            "sensitivity_restrictions": (
                ("local-only",) if name == "Protected Records" else ()),
            "optional_shallow_subfolders": (),
            "max_permitted_depth": 1,
            "treatment": (
                TREATMENT_RETAINED if name == "Unsupported or Encrypted"
                else TREATMENT_REVIEWED),
        }
        for name in RESIDUAL_TEMPLATE_NAMES
    }


def residual_library_fixture():
    """DM2(e). All nine present, a subset enabled, one renamed, one relocated,
    one replaced by an existing `To Sort` folder, the rest disabled."""
    library = build_library(_slots())
    choices = (
        ResidualChoice("Temporary Screenshots", ENABLE, PHYSICAL_DESTINATION,
                       None, None, ROOT, None, None),
        ResidualChoice("One-Off Images", RELOCATE, PHYSICAL_DESTINATION, None,
                       "n_academics", ROOT, None, None),
        ResidualChoice("Reference Clips", RENAME_RESIDUAL, REVIEW_ONLY,
                       "Clips to keep", None, ROOT, None, None),
        ResidualChoice("Reading Inbox", ENABLE, REVIEW_ONLY, None, None, ROOT,
                       None, None),
        ResidualChoice("Independent Records", MERGE_RESIDUAL, REVIEW_ONLY, None,
                       None, ROOT, "Reading Inbox", None),
        ResidualChoice("Review Later", REPLACE_WITH_EXISTING, PHYSICAL_DESTINATION,
                       None, None, None, None, "n_school"),
        ResidualChoice("Receipts and Confirmations", DISABLE, None, None, None,
                       None, None, None),
        ResidualChoice("Unsupported or Encrypted", DISABLE, None, None, None,
                       None, None, None),
        ResidualChoice("Protected Records", DISABLE, None, None, None, None,
                       None, None),
    )
    return library, choices


def template_library_fixture() -> TemplateCatalogue:
    """DM2(c). One reusable fragment, a built-in and an llm-generated definition,
    standalone one-schema applicability rows, and one definition bound twice."""
    manifest = {
        "release_id": "rel-fixture-1",
        "fragments": [{
            "fragment_id": "subject-stage", "fragment_version": 1,
            "roles": ["subject", "lifecycle_stage"],
            "relative_order": [["subject", "lifecycle_stage"]],
            "imports": [], "optional_roles": ["lifecycle_stage"],
            "metadata_only_roles": [], "allowed_values": {},
            "privacy_floor": "policy.public",
            "provenance": ["row:academic-01", "row:research-02"],
        }],
        "definitions": [
            {
                "template_id": "subject-work", "template_version": 1,
                "origin_kind": "built-in", "scope_kind": "cross-domain",
                "publication_state": "published",
                "fragment_refs": [
                    {"fragment_id": "subject-stage", "fragment_version": 1}],
                "dimensions": [{
                    "role_ref": "subject", "order_index": 0,
                    "requirement": "required", "metadata_only": False,
                    "retrieval_rationale": "Users search by subject first.",
                }],
                "optional_branch_patterns": [],
                "sensitivity_policy_ref": "policy.public",
                "validation_constraints": [],
                "example_label_chains": [["Academics", "Columbia", "PHYS1401"]],
            },
            {
                "template_id": "packet-by-counterpart", "template_version": 1,
                "origin_kind": "llm-generated", "scope_kind": "purpose-focused",
                "publication_state": "published",
                "fragment_refs": [],
                "dimensions": [{
                    "role_ref": "counterpart", "order_index": 0,
                    "requirement": "required", "metadata_only": False,
                    "retrieval_rationale": "The institution names the packet.",
                }],
                "optional_branch_patterns": [],
                "sensitivity_policy_ref": "policy.public",
                "validation_constraints": [],
                "example_label_chains": [["Applications", "Columbia"]],
            },
        ],
        "applicabilities": [
            {
                "applicability_id": "subject-work--academic",
                "applicability_version": 1, "template_id": "subject-work",
                "template_version": 1, "uses_schema": "academic",
                "purpose_profile_ref": None,
                "allowed_fields": ["subject"],
                "detection_signal_refs": ["signal.syllabus_header"],
                "role_bindings": [{"role_ref": "subject", "field_ref": "subject"}],
                "exclusions": [], "provenance": ["row:academic-01"],
            },
            {
                "applicability_id": "subject-work--research",
                "applicability_version": 1, "template_id": "subject-work",
                "template_version": 1, "uses_schema": "research",
                "purpose_profile_ref": None,
                "allowed_fields": ["subject"],
                "detection_signal_refs": ["signal.project_readme"],
                "role_bindings": [{"role_ref": "subject", "field_ref": "subject"}],
                "exclusions": [], "provenance": ["row:research-02"],
            },
            {
                "applicability_id": "packet--applications",
                "applicability_version": 1,
                "template_id": "packet-by-counterpart", "template_version": 1,
                "uses_schema": "college_applications",
                "purpose_profile_ref": {
                    "purpose_profile_id": "pp.grad-application",
                    "purpose_profile_version": 1},
                "allowed_fields": ["target_school"],
                "detection_signal_refs": ["signal.application_portal"],
                "role_bindings": [
                    {"role_ref": "counterpart", "field_ref": "target_school"}],
                "exclusions": [], "provenance": ["row:apps-01"],
            },
        ],
    }
    import json

    return load_catalogue(lambda: json.dumps(manifest))


def two_version_pair() -> tuple[tuple[Node, ...], tuple[Node, ...]]:
    """DM2(d). Two versions of one tree, differing by a rename and an addition."""
    import dataclasses

    before = realistic_tree()
    after = []
    for node in before:
        copied = dataclasses.replace(
            node, plan_version_id=PLAN_2,
            node_id=f"{node.node_id}_v2",
            parent_node_id=(None if node.parent_node_id is None
                            else f"{node.parent_node_id}_v2"),
            origin_node_id=node.origin_node_id)
        if node.origin_node_id == "n_academics":
            copied = dataclasses.replace(copied, display_label="School work")
        after.append(copied)
    after.append(_node("n_media_v2", "Media", node_type=USER_CREATED, ordinal=9,
                       version=PLAN_2, origin_node_id="n_media",
                       explanation="You created this branch by name."))
    return before, tuple(after)


def frozen_tree_fixture() -> FreezeRecord:
    """DM3. A frozen record a caller can decide legality against, alone."""
    nodes = realistic_tree()
    return FreezeRecord(
        plan_version_id=PLAN_1,
        created_at="2026-08-27T00:00:00Z",
        node_ids=tuple(node.node_id for node in nodes),
        legal_destination_ids=frozenset(
            node.node_id for node in nodes if node.accepts_placement),
        template_bindings=("btb_1",),
        labels_and_aliases={node.node_id: (node.display_label,) for node in nodes},
        residual_configuration={
            "Review Later": ENABLE, "Reading Inbox": ENABLE,
            "Unsupported or Encrypted": ENABLE,
            "Receipts and Confirmations": DISABLE,
            "Protected Records": DISABLE,
        },
        shared_material_policy_ids=("smp_fixture_1",),
        cross_folder_moves=False,
        selection_id="sel_fixture_1",
    )
```

- [ ] **Step 6: Run all three and verify GREEN**

Run: `python3.12 -m pytest -q tests/p10 tests/integration/test_p10_p9_tree.py`

Expected: PASS. If `test_no_module_holds_a_numeric_literal_beyond_zero_and_one` fails on `fixtures.py`, the fixture is carrying a threshold rather than a shape — move the number into the test that needs it.

- [ ] **Step 7: Commit**

```bash
git add src/tree_design/fixtures.py tests/p10/test_p10_fixtures.py \
        tests/p10/test_p10_no_invention.py tests/integration/test_p10_p9_tree.py
git commit -m "test(p10): publish tree fixtures and lock the P10 boundaries"
```

### Task 17: Final verification against the original design

**Files:** none created. This task changes nothing and is allowed to fail loudly.

- [ ] **Step 1: Compile and run everything**

```bash
cd "/Users/jy/GRAPH AGENT"
python3.12 -m compileall -q src tests
python3.12 -m pytest -q
git diff --check
```

Expected: the full suite green, including every P1–P9 suite. P10 adds tables to P1's database and writes two of P1's event types, so a P1 regression here is a P10 defect and must not be triaged as unrelated.

- [ ] **Step 2: Confirm the two seams that did not exist before**

```bash
cd "/Users/jy/GRAPH AGENT"
# The two reserved §8.2 event names now have a producer.
grep -rn "TEMPLATE_APPLICATION\|DESTINATION_TREE_EDIT" src/tree_design/provenance.py
# The word `fragment` now appears in src/ for the reason it should.
grep -rln "fragment" src/ | sort
```

Expected: `provenance.py` names both events; `grep -rln fragment src/` lists
`src/tree_design/templates.py`, `catalogue.py`, `routing.py`, `template_schema.py`
and `fixtures.py` alongside the pre-existing `src/facts/session.py`. Before this
plan, that grep returned one file and it was about filesystem paths.

- [ ] **Step 3: Confirm the graph shows the seams and no forbidden edge**

```bash
cd "/Users/jy/GRAPH AGENT"
graphify update .
graphify diagnose multigraph --json --max-examples 20
graphify path "accepted_groups" "legal_destination_ids"
```

Expected: a P9 → P10 path exists through `upstream.accepted_groups`; a P10 → P8
edge exists through `template_schema.template_dependencies`; and no
P10 → P11/P12 runtime edge exists, because those parts are not built and P10
consumes nothing downstream.

- [ ] **Step 4: Re-read the design and confirm the five promises**

Open `planning/00-database-agent-product-design.md` and confirm by reading, not by
memory, that the built part keeps these:

1. **Facts stay separate.** §5.12: "The facts and accepted groups remain separate from the tree, so the user can change the visual organization without destroying the underlying evidence." — `test_a_rename_changes_no_fact_and_no_expected_value`, and the no-invention guard that forbids importing a fact writer.
2. **Existing folders are not silently changed.** §5.10: "Existing folders must not be automatically flattened, renamed, or reorganized simply because a template would produce a different structure." — `test_no_code_path_renames_an_existing_node_without_a_recorded_action`.
3. **Destinations are closed after freeze.** §5.12: "Freeze records the approved hierarchy and prevents later systems from inventing new destinations outside it." — `test_legality_is_decided_without_facts_templates_or_the_filesystem`.
4. **The user can revise the view without data loss.** §8.8: "A new plan should never silently reclassify or move old files." — `test_restoring_an_earlier_version_creates_a_new_draft_and_deletes_nothing`.
5. **No P10 path can move a file.** §5.12: "The tree does not yet move or classify files." — `test_no_module_touches_the_filesystem` and `test_no_module_composes_a_path_by_joining_labels`.

Each numbered promise must map to a named passing test. A promise with no test is
not kept; say so rather than closing the task.

- [ ] **Step 5: Commit the verification**

```bash
git commit --allow-empty -m "test(p10): verify tree design and freeze against the original design"
```

## Requirement coverage map

Every one of the SPEC's seventeen Done-means, and the task that satisfies it.

| Done-means | Tasks |
|---|---|
| 1. Every P10 record serialises and round-trips; shared library records are release/version keyed, only bindings and tree state are plan-version keyed | 2, 6, 10, 13, 14, 15 |
| 2. Fixtures P11 can build against — (a) two-node skeleton, (b) realistic uneven tree, (c) fragments/definitions/applicability/bindings and one failing fixture per V1–V6, (d) two-version diff pair, (e) residual library | 9, 13, 16 |
| 3. Freeze is enforceable by ID lookup alone | 15 |
| 4. Freeze mutates no evidence | 13, 16 |
| 5. Every node carries a non-empty explanation; no surface exposes a confidence score | 2, 9, 11, 12, 16 |
| 6. Existing folders survive; nothing renames or re-parents one without a recorded user action | 13, 16 |
| 7. Uneven depth passes validation; no rule requires sibling parity | 9, 12 |
| 8. A valid template is inert until approved | 6, 7, 8 |
| 9. Every §5.9 warning fires from published data, thresholds from configuration | 3, 12 |
| 10. P2 can replay a tree version and score tree quality and template quality | 15 |
| 11. No published node carries a filesystem path other than `existing_path` | 2, 15, 16 |
| 12. A disabled residual template is unreachable | 10, 15, 16 |
| 13. C1–C8 are independently falsifiable; C2/C5 replace no V-check | 7, 9 |
| 14. Many-to-many reuse is real and schema-safe | 6, 7, 8, 16 |
| 15. Purpose composition preserves heterogeneity and binds an authored purpose profile through C3 | 6, 7, 9, 14 |
| 16. Branch choices are isolated and immutable; no version migrates a binding | 6, 7 |
| 17. A partial-depth design can be complete | 9, 13, 15 |

And the cross-cutting sections the SPEC's Done-means do not number:

| Cross-cutting requirement | Tasks |
|---|---|
| §8.2 provenance — the two events P10 appends, before/after state, model version and prompt fingerprint | 5, 13, 15 |
| §8.6 budgets — the ceiling P10 owns, `template-deferred`, surplus shown as deferred, freeze never auto-completed | 3, 7, 15 |
| §8.7 correction learning — negative feedback stored, the `learning_records` query before a candidate is proposed, six explicit scopes | 5, 11 |
| §8.8 plan versioning — immutable frozen versions, draft on edit, node-level diff, restore and adopt | 13 |
| §6.1 destination profile — every ingredient, redacted at the boundary | 14 |
| §7.2–§7.4 residual library — nine names, eight slots, six actions, three dispositions | 10 |
| §5.1–§5.11 canvas data contracts | 11, 12 |
| The composable-template seam — four records, many-to-many routing, C1–C8, the Site E fragment boundary | 6, 7, 8 |

## SPEC corrections

Where the SPEC's prose name and the live code disagree, this plan uses the LIVE
name. The SPEC remains authoritative for intent; the live API is authoritative for
names. Each row below is a change the SPEC should absorb.

| # | SPEC says | Live code says | Evidence |
|---|---|---|---|
| 1 | Contract-in from P9 requests `label` (`SPEC.md:84`) | `Group.display_label`, with the user's edit in `GroupAcceptance.user_edited_label` | `src/grouping/records.py:160`, `:355` |
| 2 | `members[]` each with `membership_kind` (`SPEC.md:86`) | `Membership.basis`, over `MEMBERSHIP_BASES` | `src/grouping/records.py:223`; `src/grouping/vocabulary.py:51-55` |
| 3 | `rejected_proposals[]` derived from `Group.state = rejected` (`SPEC.md:106-107`) | **Impossible.** `Group.__post_init__` checks `state` against `GROUP_STATES = (candidate, supported, tentative-discovery, unresolved)`; rejection is `GroupAcceptance.acceptance`, resolved as of a plan version | `src/grouping/records.py:181`; `src/grouping/vocabulary.py:20`, `:27-35` |
| 4 | "a curated-versus-incidental signal per existing folder" — two values (`SPEC.md:124-126`) | **Three.** `CURATION_SIGNAL_VALUES = (curated, incidental, undetermined)`, and `curation_signal()` returns `undetermined` for every directory until a threshold is authored | `src/scan_agent/inventory.py:20-25`, `:42-53` |
| 5 | "the cross-root movement permission" (`SPEC.md:121-122`, `:537`, `:894`) | `cross_folder_moves`, a required keyword on `record_selection`. P12's SPEC already uses the live name and says P10 stores it | `src/scan_agent/selection.py:22`, `:43`; `planning/parts/P12-apply-undo/SPEC.md:154-156` |
| 6 | The `TemplateApplicability` JSON has no `provenance` key (`SPEC.md:402-418`) | The handoff requires "provenance back to ratified domain rows and research evidence" and the composable design lists "provenance and version" among the row's contents. This plan makes it **required** | `planning/domains/TEMPLATE-BUILDING-HANDOFF.md:92`; `docs/superpowers/specs/2026-08-26-composable-template-scaffolding-design.md:110` |
| 7 | `BranchTemplateBinding.state` is shown only as `"approved"` (`SPEC.md:432`) | The closed set is `draft \| reviewed \| approved`, from the composable design. Adopted here | `docs/superpowers/specs/2026-08-26-composable-template-scaffolding-design.md:128` |
| 8 | `resolved_dimensions[].action` is shown only as `"selected"` (`SPEC.md:429`) | The closed set is `selected \| omitted \| reordered \| flattened \| renamed \| added`, from the composable design. All six adopted here; four would leave two legal user edits unrepresentable | `docs/superpowers/specs/2026-08-26-composable-template-scaffolding-design.md:125` |
| 9 | §8.6's ceiling reads as two numbers, "Maximum folder proposals and maximum depth" (`SPEC.md:836-838`) | P1 publishes **one** key, `tree.max_folder_proposals_and_depth`. P10 reads one value and uses it for both; splitting it is a `database_agent.budget` change, not a P10 default | `src/database_agent/budget.py:27` |
| 10 | The P2 envelope carries `inputs[]` and a budget value (`SPEC.md:181`, `:185-195`) | `record_stage_output` takes `inputs` and `budget_state` as **required** keywords and enforces the deferred/ceiling pairing itself | `src/eval_harness/stage_output.py:96-118` |
| 11 | Contract-in from P1 lists "durable plan-version and node records" (`SPEC.md:152-155`) | P1 has **no** plan-version table. P10 creates `plan_versions` as a P10-owned table inside P1's database, the way P9 owns `group_acceptance` | `grep -rn plan_version src/database_agent/*.py` returns nothing |
| 12 | Done-means 10 says P2 scores "tree quality and template quality" (`SPEC.md:787-788`) | Those are the `tree` and `template` **dimensions**, emitted as `DimensionValue` rows alongside the envelope — a separate list from the stage ids | `src/eval_harness/vocabulary.py:32-43` |

Four fields this plan **adds** to the SPEC's records, each carrying an open
question so the answer needs no migration:

| Field | Record | Open question it carries |
|---|---|---|
| `origin_node_id` | `Node` | OQ5, node identity across plan versions (`SPEC.md:940-943`). Ids are minted per version and lineage is recorded; if ids turn out to be stable, `origin_node_id` becomes `node_id` and nothing else changes |
| `protected_movement_permitted` | `Node` | OQ3, whether `protected` is a type or a flag (`SPEC.md:928-932`). The §5.12 enum is carried literally AND the policy input to `accepts_placement` is explicit |
| `policy_scope` | `SharedMaterialPolicy` | OQ9, tree-global versus per-branch (`SPEC.md:954-956`). `None` means global; the schema's partial unique index allows one global policy per version |
| `user_defined` | `ResidualTemplate` | §7.3's user-defined residual areas. The flag is how a shipped template is told from an authored one, and it is what lets a test assert the product ships none of §7.3's eight examples |

One ownership move this plan makes, on the lead's ruling: **P10 owns Site E's
fragment boundary** (Task 8). `docs/superpowers/plans/2026-08-26-composable-template-library.md:170-173`
assigns it to a pass gated behind `G-P10`, which cannot run until P10 ships;
`grep -rn "fragment" src/` currently returns one hit, in `src/facts/session.py:34`,
about filesystem paths. P10 owns the published catalogue and is therefore the only
part that can answer whether a named fragment exists.

## Explicitly unresolved after this plan

- **The depth limit and the §5.9 thresholds** (SPEC open questions 1 and 2). V3 and every warning read them from configuration and refuse without them. This plan defines the injection points, not the values.
- **Whether `protected` is a node type or an orthogonal flag** (OQ3). Carried both ways; affects P11 directly.
- **Whether a `node_id` is stable across plan versions** (OQ5). Minted per version with `origin_node_id` lineage; affects P11 and P12, and decides whether a pending move survives a tree edit.
- **Whether the scoped `General` is auto-proposed or opt-in per parent** (OQ8). Opt-in here, never auto-added, because the reversible choice is the one that does not put a folder in the user's tree they did not ask for.
- **Whether the shared-material policy is tree-global or per-branch** (OQ9). `policy_scope` records the answer per policy; affects P11's abstention behaviour.
- **Default redaction settings for protected branches beyond §5.2's filename rule** (OQ10). §8.4 makes names, previews, thumbnails, OCR text and location data configurable and sets no defaults; `redacted_for_egress` takes the protected class set as an argument and ships none.
- **The 200–300 domain template contents, the reusable-fragment catalogue, and the compiler that publishes them.** `docs/superpowers/plans/2026-08-26-composable-template-library.md` owns all three and is gated behind this plan. `tree_design.catalogue` reads a compiled manifest through an injected reader and never locates one.
- **P9's accepted-group reader.** `grouping.store` does not exist. `upstream.AcceptedGroupReader` is the protocol it must satisfy, and `tests/p10/p9_fixtures.py` is the swap boundary.
- **P13's `review_action` record.** Specification only. `tests/p10/p13_fixtures.py` carries P13's exact field names so the swap is one import.
- **§3.8's collector field set and P7's protected class set.** V4 and V5 are unimplementable without them and raise `ConfigurationRequired`; P6 and P7 own the answers.
- **The privacy ordering C7 merges by.** `privacy_rank` is injected with no default, because an ordering P10 invented could silently choose a weaker floor than an included fragment requires.

These are dependency gates, not invitations to invent defaults.

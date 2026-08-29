# P10/P11 Connection Contract

Date: 2026-08-27

Status: planning contract only. It freezes names, shapes and ownership across the
P10 → P11 seam; it implements no runtime behaviour and edits no plan. A later pass
applies [§10 Corrections to apply](#10-corrections-to-apply) mechanically.

Third seam contract, after `planning/22-p1-p7-connection-contract.md` and
`planning/30-p8-p9-connection-contract.md`, and it follows their discipline: one
canonical name per record, one owner per field, every decision cited to the design,
a SPEC line, or a live `file:line`.

> **This contract cites the two PLANs by grep anchor, never by line number.** Both
> files were modified by another session twice while it was being written —
> `git status` shows `M docs/superpowers/plans/2026-08-25-p10-tree-design-freeze.md`
> and `M docs/superpowers/plans/2026-08-25-p11-placement-residual.md`, and P11 grew
> 8276 → 8291 lines mid-pass while P10 grew 10013 → 10092, shifting every line number
> under it. SPEC and `src/` line numbers **are** stable and are cited numerically. A
> `PLAN, grep X` citation means: run `grep -n 'X' <that PLAN>` to find it now.

## Authority and boundary

Authority order: `planning/00-database-agent-product-design.md` (canonical, wins on
conflict) → the two part SPECs → the two PLANs → live `src/` for exact
unchanged-meaning names → `planning/02-segmentation-map.md` for the cut.

**Neither part is built.** `ls src/` returns `database_agent eval_harness
evidence_shape extractors facts grouping llm_harness privacy readers scan_agent` and
no `tree_design` or `placement`; `graphify query "FrozenTree FreezeRecord
DestinationProfile"` returns `No matching nodes found`. Every name below is therefore
*decided*, not observed — except where it borrows a live upstream name, which is
marked.

P10 owns the tree: node identity, node kinds, template context, the destination
profile, the residual-library definitions (§7.2–§7.4, moved to P10 by
`02-segmentation-map.md`'s M10 note), the freeze record, and the plan-version diff.
P11 owns placement: the retrieval index over P10's profiles, the placement decision
record, the residual *workflow* (§7.5–§7.11), and the P8 Site C/D authorities. P11
mints no node, builds no profile, publishes no parallel node vocabulary, and composes
no filesystem path.

---

## 1. The defect this contract fixes

Verified by command, not asserted:

```
$ grep -c 'FrozenTree\|FrozenNode' planning/parts/P11-placement-residual/PLAN.md   -> 21
$ grep -c 'FrozenTree\|FrozenNode' planning/parts/P10-tree-design-freeze/PLAN.md   ->  0
$ grep -c 'FreezeRecord'           planning/parts/P10-tree-design-freeze/PLAN.md   -> 14
$ grep -c 'FreezeRecord'           planning/parts/P11-placement-residual/PLAN.md   ->  0
```

Zero vocabulary overlap on the record that connects the two parts. P11's dependency
gate imports a callable P10 does not plan to write (`P11 PLAN`, grep `from tree_design.freeze import frozen_tree`):

```python
    from tree_design.freeze import frozen_tree  # noqa: F401  -- G-P10
```

P10 publishes `frozen_tree_fixture() -> FreezeRecord` (`P10 PLAN`, grep `def frozen_tree_fixture`) and no `frozen_tree`. Today P11's gate fails
`ModuleNotFoundError`, which its plan calls correct. The day P10 ships it becomes a
permanent `ImportError`.

**The naming is not the worst of it.** Six shape mismatches would import cleanly and
then fail at runtime, and one — node identity across plan versions — would silently
destroy §8.8's promise while every test stayed green. §4 and §5.

---

## 2. Frozen names

Canonical name | Owner | Module path | Consumed by | Replaces these spellings
---|---|---|---|---
`Node` | P10 | `tree_design.records` | P11 Tasks 6, 7, 13, 17 | P11's `FrozenNode` (`P11 PLAN`, grep `class FrozenNode`)
`ExpectedValue` | P10 | `tree_design.records` | P11 Task 6 | P11's `expected_values: tuple[dict, ...]` and its `item["field"]` subscript (`P11 PLAN`, grep `item["field"]`)
`TemplateContext` | P10 | `tree_design.records` | P11 Task 6 | P11's `template_context: dict \| None` (`P11 PLAN`, grep `template_context: dict`)
`DestinationProfile` | P10 | `tree_design.profiles` | P11 Task 6 | P11's own `DestinationProfile` (`P11 PLAN`, grep `class DestinationProfile`) — same name, different fields; P10's shape wins
`NodeContext` | P10 | `tree_design.profiles` | P11 Task 6 | P11's bare `tuple[str, ...]` for `parent_context` / `child_context`
`AnchorExcerpt` | P10 | `tree_design.profiles` | P11 Task 6 | P11's `anchor_excerpt_keys: tuple[str, ...]`
`Restrictions` | P10 | `tree_design.profiles` | P11 Task 6 | P11's `restrictions: dict`
`FreezeRecord` | P10 | `tree_design.freeze` | P11 Task 6, through `FrozenTree` | — (P11 has no equivalent)
`FrozenTree` | **P10** | `tree_design.freeze` | P11 Tasks 6, 13, 17 | P11's test-only `FrozenTree` (`P11 PLAN`, grep `class FrozenTree`), which becomes a consumer of P10's
`frozen_tree(conn, *, plan_version) -> FrozenTree` | **P10** | `tree_design.freeze` | P11's G-P10 gate | P10's `fixtures.frozen_tree_fixture()`, which stays a fixture and stops being the seam
`legal_destination_ids(record) -> frozenset[str]` | P10 | `tree_design.freeze` | P11 Task 6 | P11's `legal_node_ids` becomes a *projection*, not a second authority
`IndexEntry` | P11 | `placement.index` | P11 only | — (P10 must not publish one)
`node_exists(node_id, plan_version) -> bool` | P11 | `placement.index` | P8 Sites C and D | — (live P8 call site, `src/llm_harness/placement_validation.py:222`)

### Why `Node` and not `FrozenNode`

The canonical design names the record and calls it a node
(`planning/00-database-agent-product-design.md:102`):

> The output of this stage is a proposed destination tree: an editable hierarchy of
> existing folders, user-created folders, and evidence-backed proposed branches.
> **Each node has a type**—existing, proposed, user-created, protected, or
> ignored—a display label, a parent, associated groups, a template context where
> relevant, and an explanation of the facts or accepted groups that caused it to
> appear.

The same record exists *before* freeze — the user edits it, reorders it, renames it,
and P10 stores it under a `draft` version. `FrozenNode` names a lifecycle state as if
it were a type, which is the "capability used as an identity" defect this project
keeps shipping. `frozen` belongs on the plan version, and already lives there:
`PlanVersion.state` is checked against `("draft", "frozen", "superseded")`
(`P10 PLAN`, grep `if self.state not in`). One `Node` row is draft in one version and frozen in the next.
P10 SPEC's Contract-out §1 heading is "The node record" (`P10 SPEC:204`).

### Why `FrozenTree` survives, as P10's

`FreezeRecord` and `FrozenTree` are **two records, not two names for one**, and each
plan wrote one and omitted the other.

`FreezeRecord` is §8.8's adopted-plan-version record — what freeze *records*. P10's
shape (`P10 PLAN`, grep `class FreezeRecord`) is ids and configuration only: `plan_version_id`,
`created_at`, `node_ids`, `legal_destination_ids`, `template_bindings`,
`labels_and_aliases`, `residual_configuration`, `shared_material_policy_ids`,
`cross_folder_moves`, `selection_id`. That is exactly right for DM3 — *"Given a
frozen tree fixture and an arbitrary destination string, a caller can decide legality
without consulting facts, templates or the filesystem"* (`P10 SPEC:772-775`).

But it cannot feed P11. `build_destination_index(conn, tree, ...)` reads
`tree.nodes`, `tree.profiles`, `tree.plan_version` and `tree.shared_material_policy`
(`P11 PLAN`, grep `def build_destination_index`). An id list has none of them. So the hand-over bundle is a
real, separate record; the design names it in prose — *"A later placement system may
use **the frozen tree** as its only allowed destination set"* (`00:102`) — and **P10
owns it**, because every field in it is P10's.

---

## 3. `FrozenTree` — the hand-over record

```python
# src/tree_design/freeze.py
@dataclass(frozen=True)
class FrozenTree:
    plan_version_id: str                       # NOT `plan_version`; see §5.1
    freeze_record: FreezeRecord
    nodes: tuple[Node, ...]                    # every node, legal or not
    profiles: tuple[DestinationProfile, ...]   # one per node, resolution B4
    shared_material_policy: str                # the VALUE, not an id; see §5.3
    shared_material_policy_scope: str | None   # None = tree-global (P10 OQ9)

def frozen_tree(conn, *, plan_version: str) -> FrozenTree: ...
```

Invariants — P10's to enforce, P11's to rely on:

1. `frozen_tree` raises unless the version's `state == "frozen"`. `P11 SPEC:160`:
   *"Freeze is a precondition. P11 does not start until a frozen tree exists at a
   known plan version."*
2. `len(profiles) == len(nodes)` and the `node_id` sets are equal. P11 currently
   refuses a partial set itself (`P11 PLAN`, grep `no §6.1 destination profile for`); with P10 owning the bundle
   that becomes a P10 invariant and P11's check becomes a cheap assertion.
3. `freeze_record.legal_destination_ids == {n.node_id for n in nodes if
   n.accepts_placement}` — the single legality authority (§4.4).
4. `nodes` includes nodes with `accepts_placement = false`. `P10 SPEC:235-240` makes
   an `ignored` node *"visible context, not a destination"*; P11 needs to see it to
   explain a non-placement, and `_ancestry` needs it to resolve a parent chain that
   passes through one.
5. Every node has a non-`None` `refinement_disposition` and `refinement_reason`
   (§5.5).

**`shared_material_policy` is not optional.** §6.9 requires it and P11 fails closed
without it (`P11 PLAN`, grep `requires the frozen tree to carry a shared-material policy`); `P10 SPEC:542-545` records it as a freeze-time
tree-level policy.

---

## 4. The crossing records, field by field

### 4.1 `Node` — 22 fields, `tree_design.records.Node`

`P10 PLAN`, grep `class Node:` — it appears twice, in Task 2's Interfaces block and in
the `records.py` implementation, and the two agree.

Field | Type | Writer | P11 may | P11's `FrozenNode` (`P11 PLAN`, grep `class FrozenNode`)
---|---|---|---|---
`node_id` | `str` | P10 | read | same
`plan_version_id` | `str` | P10 | read | same
`node_type` | `str` ∈ `NODE_TYPES` | P10 | read | same
`display_label` | `str` | P10 | read | same
`parent_node_id` | `str \| None` | P10 | read | same
`root_anchor` | `str` | P10 | read | same
`ordinal` | `int` | P10 | read | same
`associated_group_ids` | `tuple[str, ...]` | P10 | read | same
`explanation` | `str` | P10 | read | same
`node_role` | `str` ∈ `NODE_ROLES` | P10 | read | same
`accepts_placement` | `bool`, derived | P10 | read, **never re-derive** | same
`handling_class` | `str` ∈ live `privacy.vocabulary.HANDLING_CLASSES` | P7 → P10 | read | same
**`origin_node_id`** | `str` | P10 | read; **match versions on this** | **ABSENT** — §5.2
**`protected_movement_permitted`** | `bool` | P10 | read | **ABSENT**
`template_context` | `TemplateContext \| None` | P10 | read | `dict \| None`
`dimension_role` | `str \| None` | P10 | read | same
`dimension` | `str \| None` | P10 | read | same
`expected_values` | `tuple[ExpectedValue, ...]` | P10 | read | `tuple[dict, ...]`
`existing_path` | `str \| None`, only when `node_type = existing` | P3 → P10 | read | same, but P11's fixture violates the rule — §5.4
`disposition` | `str \| None`, required iff `node_role = residual` | P10 | read | same
`refinement_disposition` | `str \| None` on `Node`, non-`None` in `FrozenTree` | P10 | read | `str` — §5.5
`refinement_reason` | `str \| None` on `Node`, non-`None` in `FrozenTree` | P10 | read | `str`

`accepts_placement` is derived by `derive_accepts_placement(node_type, *,
protected_movement_permitted)` (`P10 PLAN`, grep `def derive_accepts_placement`) and `Node.__post_init__` refuses a
stored value that disagrees with the derivation (`P10 PLAN`, grep `contradicts the`). `P10 SPEC:256-262`,
resolution B6: P11 *"consumes rather than re-derives"* it.

### 4.2 `DestinationProfile` — P10's shape wins

`P10 PLAN`, grep `class DestinationProfile`, `class NodeContext`, `class AnchorExcerpt`,
`class Restrictions`.

```python
@dataclass(frozen=True)
class NodeContext:                       # §6.1's "parent and child meanings"
    node_id: str
    display_label: str
    dimension: str | None
    expected_values: tuple[ExpectedValue, ...]

@dataclass(frozen=True)
class AnchorExcerpt:
    observation_key: str                 # P4's durable handle, resolution M14
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
```

Five differences from P11's fixture, each a runtime break rather than a rename:

Field | P10 publishes | P11 reads | Consequence
---|---|---|---
`anchor_excerpts` | `tuple[AnchorExcerpt, ...]` | `profile.anchor_excerpt_keys` (`P11 PLAN`, grep `anchor_excerpt_keys=tuple(profile`) | `AttributeError`
`anchor_files` | `tuple[str, ...]` | — | P11 loses §6.1's *"rich anchor files"* entirely
`parent_context` / `child_context` | `tuple[NodeContext, ...]` | `tuple[str, ...]` (`P11 PLAN`, grep `parent_context=tuple(profile`) | `IndexEntry` declares `tuple[str, ...]`, `asdict` serialises dicts, `entry_for` round-trips dicts back — a silently wrong type
`template_binding` | `str \| None` | — | P11's fixture omits it
`restrictions` | `Restrictions` | `dict` of three keys, no `node_role` | `restrictions["node_role"]` unavailable

**P10's shape wins on every row**, on resolution B4 (`P10 SPEC:316`, `P11 SPEC:139`):
*"P10 emits the profile; P11 does not build one."* A consumer does not get to reshape
a record it does not own. `anchor_excerpt_keys` loses specifically because
`AnchorExcerpt` carries `node_id` alongside `observation_key` and §6.1 asks for
anchor evidence *per node*; a bare key tuple cannot say which node an excerpt anchors.

P11's `IndexEntry` is P11's own and may flatten these however retrieval needs — it is
a placement mechanism, and `P10 SPEC:312-314` draws exactly that line. What it may not
do is assume the profile arrived flat.

### 4.3 `ExpectedValue` — the subscript that would not run

P10: `ExpectedValue(field: str, value: str)`, a frozen dataclass (`P10 PLAN`, grep `class ExpectedValue`).
P11 (`P11 PLAN`, grep `item["field"]`):

```python
        expected_values=tuple(
            (item["field"], item["value"]) for item in node.expected_values
        ),
```

A frozen dataclass is not subscriptable; `item["field"]` raises `TypeError` on the
first real node. P10's record wins; P11 reads `item.field, item.value`.

### 4.4 The legality projection — one authority, one projection

Two callables answer one question today:

- **P10 Task 15** (`P10 PLAN`, grep `def legal_destination_ids`): `legal_destination_ids(record: FreezeRecord)
  -> frozenset[str]` and `is_legal_destination(record, node_id) -> bool` — pure, in
  memory, over the freeze record.
- **P11 Task 6** (`P11 PLAN`, grep `def legal_node_ids`): `legal_node_ids(conn, *, plan_version) ->
  frozenset[str]` — a `SELECT` over P11's own `placement_index_entries`.

**Decision: P10's is the authority; P11's is a projection and must be provably
equal.** `build_destination_index` asserts
`{e.node_id for e in entries} == tree.freeze_record.legal_destination_ids` and raises
`FrozenTreeRequired` otherwise. Two sources that can disagree is the defect
`22-p1-p7-connection-contract.md` §6 check 5 forbids: *"Exactly one part writes each
concept."*

`node_exists` stays P11's, closed over the index, and remains the single authority
P8's Sites C and D call — `if not dependencies.node_exists(destination, plan_version)`
(`src/llm_harness/placement_validation.py:222`). That is correct *because* the index
is now provably the freeze record's projection rather than a second opinion.

---

## 5. Six shape decisions the plans do not agree on

### 5.1 `plan_version` vs `plan_version_id`

P10 uses `plan_version_id` on `Node`, `PlanVersion`, `SharedMaterialPolicy` and
`FreezeRecord`. P11 uses `plan_version` on its tree, `IndexEntry`, its schema columns
and its P8 calls, and converts across the two (`P11 PLAN`, grep `plan_version=node.plan_version_id`:
`plan_version=node.plan_version_id`).

**Decision: `plan_version_id` on every P10 record; `plan_version` stays P11's column
and keyword name.** P11's spelling is already live at the P8 seam —
`dossier.plan_version` (`src/llm_harness/placement_validation.py:209`) and
`node_exists(node_id, plan_version)` (`:222`) are shipped — and renaming a keyword in
a green part for cosmetic symmetry is not worth it. The conversion happens once, at
`_entry`, and this contract records it rather than pretending it is absent.

### 5.2 Node identity across plan versions — the one that breaks §8.8 silently

P10 answered its OQ5 by minting a new `node_id` per plan version and recording lineage
in `origin_node_id` (`P10 PLAN`, grep `**G-OPEN:**`). Its own test asserts the mint
(`P10 PLAN`, grep `test_a_copied_node_keeps_its_lineage`):

```python
def test_a_copied_node_keeps_its_lineage_and_gets_a_new_identity(seeded):
    ...
    assert before["n_root"].node_id != after["n_root"].node_id
```

P11 Task 17 assumes the opposite (`P11 PLAN`, grep `**Renaming is the trap.**`):

> **Renaming is the trap.** A renamed node keeps its `node_id` (P10 SPEC: *"Renaming
> a node rewrites `display_label` only"*), so a rename correctly carries the decision.

and its fixture keeps `node_id="n-course"` while moving to `plan-2`
(`P11 PLAN`, grep `def _v2_with_a_rename`); `reproject` matches decisions to nodes by `node_id`
(`P11 PLAN`, grep `def reproject(conn`). Under P10's minting, **no** `node_id` survives a draft, so *every*
decision would be marked `requiring_renewed_review` on any tree edit — including a
pure rename.

The design forbids that outcome (`planning/01-product-design-structured.md:1889-1892`,
§8.8):

> The diff may state that Applications was renamed to Admissions, Research moved under
> Projects, Reference Clips was added, the Academic template changed from school →
> term → course → work type to course → term → work type, or twenty-three files now
> require renewed review because their previous destination no longer exists.

A diff that distinguishes *renamed*, *moved* and *added* from *no longer exists*
requires an identity that survives a rename. **"Twenty-three" is a subset, not all.**

**Decision, and it does not close OQ5:** `origin_node_id` is a **required field on the
crossing `Node`** and on P11's `IndexEntry`, and **P11 matches across plan versions on
`origin_node_id`, never on `node_id`.** P10 keeps minting; P11 stops assuming
stability. This is the minimal change: OQ5 stays genuinely open (if ids later become
stable then `origin_node_id == node_id` and nothing else moves — P10's own
SPEC-corrections row says exactly that), and `reproject` is correct under either
answer.

`PlacementDecision.destination` continues to name a `node_id`: a decision is made
against one version and belongs to it. `reproject` resolves
`decision.destination → plan-N entry → origin_node_id → plan-N+1 entry`, and marks
for renewed review only when no successor shares that origin.

### 5.3 `SHARED_MATERIAL_POLICIES` — four values, two spellings

```
$ grep -n 'SHARED_BRANCH: str\|PRIMARY_HOME: str\|REFERENCE_OR_ALIAS: str\|MANDATORY_REVIEW: str' planning/parts/P10-tree-design-freeze/PLAN.md
573:SHARED_BRANCH: str = "shared-branch"
574:PRIMARY_HOME: str = "primary-home"
575:REFERENCE_OR_ALIAS: str = "reference-or-alias"
576:MANDATORY_REVIEW: str = "mandatory-review"

$ sed -n '5471,5473p' planning/parts/P11-placement-residual/PLAN.md
def test_the_four_policies_are_69s_own_four():
    assert SHARED_MATERIAL_POLICIES == (
        "shared_branch", "primary_home", "reference_or_alias", "mandatory_review")
```

P10 hyphenates; P11 underscores. `resolve_multi_home` (`P11 PLAN`, grep `def resolve_multi_home`) compares the
tree's value against P11's tuple, so **every multi-home file would fall through every
branch** and §6.9 would be unenforced in the one case it exists for. Nothing raises.

**Decision: hyphenated, P10's spelling.** P10 owns the policy (`P10 SPEC:542-545`,
freeze-time tree policy), and P10's node vocabulary is hyphenated throughout —
`scoped-general`, `shared-material`, `physical-destination`, `review-only`,
`leave-in-place`, `user-created`, `shallow-by-choice` — all of which P11 already
matches exactly (`P11 PLAN`, grep `NODE_ROLES: tuple`). Four underscored values inside an otherwise
hyphenated P10 vocabulary are the outlier.

The `FrozenTree` carries the **value**, not `FreezeRecord.shared_material_policy_ids`.
P11 must branch on which of §6.9's four rules applies; an id list cannot tell it. P10
resolves the id to its value when building the bundle.

### 5.4 `existing_path` on an `ignored` node

`Node.__post_init__` raises `MalformedTreeRecord` when `existing_path` is set on a
node whose `node_type != existing` (`P10 PLAN`, grep `existing_path is not None and self.node_type`), and P10's own test asserts
the consequence (`P10 PLAN`, grep `ignored is no longer`):

```python
    assert after["n_school"].existing_path is None  # ignored is no longer `existing`
```

P11's fixture builds `n-ignored` with `node_type="ignored"` **and**
`existing_path="/Users/x/Old Downloads"` (`P11 PLAN`, grep `node_id="n-ignored"`). Against P10's real
record that node is unconstructible.

**Decision: P10's rule holds.** `existing_path` is an observed fact about a folder the
corpus *has* (`P10 SPEC:250-254`); ignoring a folder is a decision about placement,
and §5.10's guarantee is already carried by `accepts_placement = false`. P11's fixture
drops the path.

### 5.5 `refinement_disposition` optionality

P10: `refinement_disposition: str | None = None` (`P10 PLAN`, grep `refinement_disposition: str | None`). P11:
`refinement_disposition: str`, required on both the node and the `IndexEntry`
(`P11 PLAN`, grep `refinement_disposition: str` (fixture and `IndexEntry`)).

`P10 SPEC:230` says it is *"required on an approved branch"*, and freeze
validates approval. **Decision: the field stays `str | None` on `Node` — a draft node
may not have one yet — and `frozen_tree` guarantees it non-`None` on every node it
returns.** The guarantee belongs to the bundle, which is the record that only exists
after freeze. `validate_for_freeze` refuses a version with a `None` on an approved
branch.

### 5.6 `scoped_general_parents`

P11's tree carries `scoped_general_parents: tuple[str, ...]` (`P11 PLAN`, grep `scoped_general_parents`,
default `()`). P10 produces nothing of that name, and nothing in P11 reads it — a grep
finds only the field and its one construction site.

**Decision: drop it.** It is exactly
`{n.parent_node_id for n in nodes if n.node_role == "scoped-general"}`, and an unread
denormalisation is a second source for a fact the nodes already carry.

---

## 6. The `node-hub` collision — P8 owns the fix

### Verified in live code

```
$ grep -rn 'node-hub' src/ tests/
src/llm_harness/placement_validation.py:239:    if payload.get("generic_hub") is True or destination == "node-hub":
src/llm_harness/fixtures.py:356:_C_VOCAB = ("node-legal", "node-alt", "node-hub", "date-2026", "inst-1", "proj-1")
src/llm_harness/fixtures.py:453:        payload=_c_payload(destination="node-hub", generic_hub=True),
tests/p8/test_p8_sites.py:57:            "node-legal", "node-alt", "node-hub",
```

The claim is true: a P8 **fixture** id reached production Site C logic, and any real
frozen node minted with that id would score `weak` on every call, forever.

### The deciding evidence

The one fixture that produces `GENERIC_HUB_ONLY` already sets the flag:

```
$ python3 -c "import sys, json; sys.path.insert(0,'src')
from llm_harness import fixtures as F
for p in F.SITE_C_REASON_PAIRS:
    if p.name == 'GENERIC_HUB_ONLY': print(json.loads(p.response_bytes))"
{'claims': [{'claim_ref': 'c1', 'payload': {'destination': 'node-hub',
 'per_dimension_support': [...], 'alternatives': ['node-alt'],
 'conflicts_considered': [], 'support': 0.9, 'next_support': 0.1,
 'generic_hub': True}, 'citations': [...]}]}
```

`generic_hub: True` is present, so the literal `or destination == "node-hub"` is
**dead weight in the only case it was written for**: removing it changes no recorded
outcome, because the payload flag already fires the same branch.

### Decision: P8 removes the literal. P10 and P11 add nothing.

- **P8 owns it** because P8 wrote it and can delete it at zero behavioural cost. One
  line, `src/llm_harness/placement_validation.py:239` →
  `if payload.get("generic_hub") is True:`. `src/llm_harness/fixtures.py:356` and
  `tests/p8/test_p8_sites.py:57` keep `node-hub` as a *fixture vocabulary* member,
  which is fine — a fixture node id is not a production rule.
- **P10 must not refuse to mint it.** A reserved-id list inside the tree owner is a P8
  implementation detail leaking into the record that defines the user's folders. P10
  would be refusing a folder name for a reason it cannot state to the user.
- **P11's `NodeIdReserved` is deleted** — the stub (`P11 PLAN`, grep `class NodeIdReserved`), the class
  (`P11 PLAN`, grep `class NodeIdReserved(ValueError):`), `RESERVED_NODE_IDS` (`P11 PLAN`, grep `RESERVED_NODE_IDS`) and the raise site. P11's
  plan already says the refusal *"is removed when P8's line is"*; this contract
  removes P8's line, so the refusal never ships.

P9 has already paid for this defect class once and guarded against it:
`tests/p9/test_p9_graph.py:226` is `test_no_generic_hub_literal_is_written_into_p9`,
whose docstring reads *"The rule is a frequency, not a list of domains. A hard-coded
`.edu` or a mail provider would be P9 authoring a policy that belongs to
configuration."* The same principle: **a hub is a property of the evidence, not of an
id.**

**Ordering gate:** P8's removal lands before P10 Task 2 (node minting) and before P11
Task 6. Until then the collision is documented here and nothing else guards it — which
is correct, because no `tree_design` module exists to mint an id.

---

## 7. The P2 stage gap — `candidate_node_retrieval` is unattributable

### The mechanism, verified

`src/eval_harness/attribution.py` reads **only** `stage_dimension_value` rows to
decide both which stage emitted a failing assertion (`attribution.py:65-71`) and which
stages qualify as ancestors (`:30-39`). A stage that writes no `stage_dimension_value`
row can be neither.

P11's `emit_scoring_stage` passes `dimension_values=(dimension_for(decision),)`
(`P11 PLAN`, grep `def emit_scoring_stage(conn: sqlite3`). `emit_retrieval_stage` passes **no `dimension_values` argument
at all** (`P11 PLAN`, grep `def emit_retrieval_stage(conn: sqlite3`). So `candidate_node_retrieval` writes zero dimension
rows and is structurally unattributable, no matter what P2 does.

P11's own ledger already contradicts its implementation (`P11 PLAN`, grep `| P2 stages |`): *"Task 18
emits exactly those two stages and hands **both dimensions** over as
`DimensionValue`s."* Only one is handed over.

`src/eval_harness/vocabulary.py:5-8` records the design question honestly:

> `factual_validation` and `candidate_node_retrieval` are stages with no same-named
> dimension; `residual` is a dimension with no same-named stage. That is SPEC Open
> question 1, and it is open.

### Decision: `candidate_node_retrieval` carries the `retrieval` dimension

The design settles it. §8.5's dimension list contains
(`planning/01-product-design-structured.md:1757-1758`):

> **Retrieval quality:**
> For sparse files, did the correct anchors appear in the top candidate neighborhood?

That is what P11's §6.2 candidate-node retrieval does, in §8.5's own words. §8.5's ten
dimensions are a shorter and separate list from its ten stages *on purpose*, so two
stages sharing one dimension is the shape the design already has. No eleventh
dimension is added.

### But the subject_ref must be namespaced, or the write raises

`stage_dimension_value` declares `PRIMARY KEY (run_id, dimension, subject_ref)`
(`src/eval_harness/stage_output.py:59`). Two consequences:

1. `candidate_node_retrieval` **cannot** carry the `placement` dimension for the same
   subject as `placement_scoring` — the second `INSERT` raises `IntegrityError`.
2. `retrieval` is already P9's dimension for its own retrieval stage
   (`src/grouping/stage_output.py:56-60`), and a P9 `Seed` is keyed
   `(file_id, content_hash)` (`src/grouping/seeds.py:70-77`). A full-pipeline replay
   in which P9 and P11 both key a `retrieval` row on the same file raises.

**Decision:** P11's `candidate_node_retrieval` uses
`subject_ref = f"candidates:{plan_version}:{subject_ref}"` for **both** the
`stage_output` envelope and its `DimensionValue`, and `placement_scoring.inputs` gains
that ref. Both halves are required: `_stage_verdicts` keys on the dimension row's
`subject_ref` while `_edges` keys on the envelope's, so they must be equal; and the
ancestor walk only reaches a stage named in `inputs[]`.

The `plan_version` in the key is not decoration. `retrieval` sits in
`SHARED_EVIDENCE_DIMENSIONS` (`src/eval_harness/vocabulary.py:48`) while P11's
candidate retrieval is plan-scoped by construction — it retrieves only the legal
destinations of one frozen version. Keying the subject on the version means two plan
versions produce two measurements rather than one contested row.

With that, an assertion on `(retrieval, candidates:plan-1:file:f1:h1)` graded
`divergent` attributes to `candidate_node_retrieval` (stage order 8) rather than to
`placement_scoring` (order 9) — which is what §8.5 asks for.

### Owners

- **P11** adds the `DimensionValue`, the namespaced subject, and the `inputs[]` entry.
  Three edits inside `src/placement/stage_output.py`, Task 18. No P2 code change is
  required for attribution to work.
- **P2** owes one documentation change and one test: record that its Open question 1 is
  answered for `candidate_node_retrieval` — it shares the `retrieval` dimension,
  distinguished by subject namespace — and add a test that no two stages write the same
  `(dimension, subject_ref)` in one run. `residual`-with-no-stage stays open and is
  unaffected; P11 already attaches it to `placement_scoring` and says so
  (`P11 PLAN`, grep `A correct abstention passes both dimensions`).

### `llm_grounding` — P8's, and P11 must not produce one

```
$ grep -rn 'DimensionValue' src/
src/grouping/stage_output.py:116     (P9 emits)
src/facts/stage_output.py:90         (P6 emits)
src/eval_harness/...                 (P2's own definition and replay)
```

Only P6 and P9 emit dimension values. `src/llm_harness/stage_output.py` calls
`record_stage_output` at `:122` with no `dimension_values`, so **`llm_interpretation`
is equally unattributable and `llm_grounding` has no producer** — one defect, not two.

`llm_grounding` measures *"Did every cited excerpt exist? Did the model return unknown
when evidence was insufficient?"* — the citation check and the abstention, both inside
P8's validator. `planning/30-p8-p9-connection-contract.md` freezes that P8 *"owns the
only model invocation and the only deterministic validator for sites A–E."*

**P11 does not produce `llm_grounding` and must not.** P11 supplies Site C and D
authorities and transcribes verdicts (`P11 PLAN`, grep `### Task 12: Supply Site C`, Task 12); it validates no
citation. A second emitter would double-count every model call — the same reason P9
publishes no `llm_interpretation` emitter and asserts it in
`tests/integration/test_p9_p2_replay.py:131`,
`test_p9_publishes_no_emitter_for_the_model_call_stage`. **Owner: P8.**

---

## 8. The Site-E fragment boundary — P8 changes, P10 supplies

### What P10 Task 8 currently does

`template_dependencies(catalogue)` returns
`TemplateDependencies(schema_validator=template_schema_validator(catalogue))`
(`P10 PLAN`, grep `def template_dependencies(catalogue`), and the fragment boundary is folded inside that single
callable: a `FORBIDDEN_PUBLISHING_KEYS` scan (`P10 PLAN`, grep `key in payload for key in FORBIDDEN_PUBLISHING_KEYS`) and
`_fragment_refs_are_published(payload, catalogue)` (`P10 PLAN`, grep `_fragment_refs_are_published(payload`).

### Why that is not sufficient

Live `TemplateDependencies` has exactly one field
(`src/llm_harness/template_validation.py:26-27`):

```python
class TemplateDependencies:
    schema_validator: Callable[[object], bool]
```

and `validate_template_response` returns
`ValidationUnavailable(missing=("schema_validator",))` only when the whole validator
is absent (`:166`). Three consequences:

1. **Any caller that does not route through P10 gets silence, not
   `ValidationUnavailable`.** `tests/p8/test_p8_sites.py:84` already constructs
   `schema_validator=lambda payload: True`; a payload publishing a canonical fragment
   passes every check. The boundary would hold by convention, which is exactly what
   `planning/33-P8-COMPLETION-AUDIT.md:116-120` asked it not to do:

   > This is legitimately deferred — P10 does not exist, and the published-fragment
   > registry that a check would consult is P10's to publish. It was not written down
   > as deferred anywhere, which is the only thing wrong with it. When P10 ships,
   > `TemplateDependencies` gains a published-fragment authority and a missing one is
   > `ValidationUnavailable` like every other.

2. **Two different defects report one reason code.** A malformed payload and a
   reference to an unpublished fragment both come back as `SCHEMA_INVALID`. P8's own
   Site C already keeps this pair apart — `INVENTED_NODE` for a destination outside
   the dossier vocabulary (`src/llm_harness/placement_validation.py:221`) and
   `NODE_NOT_IN_FROZEN_TREE` for one the frozen tree does not contain (`:223`). Site E
   should mirror it.

3. A *distinct authority* can be absent, and absence is reportable. A folded check can
   only be silent.

### Decision: **P8 changes.** P10 supplies the callable.

```python
# src/llm_harness/template_validation.py
@dataclass(frozen=True, slots=True)
class TemplateDependencies:
    schema_validator: Callable[[object], bool]
    published_fragment: Callable[[str, int], bool]   # (fragment_id, fragment_version)
```

- `validate_template_response` returns
  `ValidationUnavailable(missing=("published_fragment",))` when it is `None`, exactly
  as it already does for `schema_validator` (`template_validation.py:166`).
- Two new reason codes in `llm_harness.vocabulary`, mirroring the Site C pair:
  `FRAGMENT_NOT_PUBLISHED` (the response references an id/version the catalogue does
  not contain → `REJECT`) and `FRAGMENT_PUBLICATION_ATTEMPTED` (the payload carries
  one of `FORBIDDEN_PUBLISHING_KEYS` → `REJECT`).
- P10's `template_dependencies(catalogue)` fills both fields. The
  `FORBIDDEN_PUBLISHING_KEYS` scan and `_fragment_refs_are_published` move out of
  `template_schema_validator` and into the new authority, so `schema_validator` goes
  back to meaning only *"is this shape legal"* — which is what its docstring already
  claims (`P10 PLAN`, grep `True means "this shape is legal"`: *"True means 'this shape is legal', nothing more."*).

**Ordering gate:** P8's `TemplateDependencies` change lands before P10 Task 8. It is
additive to a green part and breaks only callers that construct the dataclass
positionally; `tests/p8/test_p8_sites.py:84` is the one such site and gains a second
keyword.

---

## 9. The ordering gate — what must exist in P10 before each P11 task starts

P11 Tasks 1–5 depend on nothing from P10 and are unchanged.

P11 task | Needs from P10 | P10 task
---|---|---
6 — index the legal destinations | `Node`; `DestinationProfile` + `NodeContext` / `AnchorExcerpt` / `Restrictions`; `FrozenTree`; `frozen_tree()`; `FreezeRecord.legal_destination_ids` | 2, 14, 15
7 — bounded retrieval | the index only | (via 6)
8–11 — graph, scoring, privacy, learning | `handling_class`, `expected_values`, `node_role` on the entry | (via 6)
12 — Site C authorities | `node_exists` over the index; **P8's `node-hub` line removed** | (via 6) + P8
13 — group plans, multi-home | `FrozenTree.shared_material_policy` (the value) and `shared_material_policy_scope` | 2, 15
14–15 — residual sets and the eight actions | `node_role = residual` + `disposition` on real nodes | 10, 15
16 — the P13 receiver | nothing new | —
17 — re-project on a new version | **`origin_node_id`** on `Node` and `IndexEntry`; `diff_versions` semantics | 2, 13
18 — the two P2 stages | nothing from P10 | —
19–21 — pipeline, guards, verification | everything above | —

**The single hard gate.** P11 Tasks 6–19 build against `tests/p11/p10_fixtures.py`,
which this contract redefines as **a mirror of P10's real records**, not an independent
invention. Replacing that import with `tree_design.freeze.frozen_tree` is
`tests/integration/test_p11_p10_tree.py`, which must keep failing `ModuleNotFoundError`
until P10 ships and must never be satisfied by a source stub (`P11 PLAN`, grep `G-P10: the live frozen-tree read`).

P10 Task 16's `frozen_tree_fixture()` changes return type from `FreezeRecord` to
`FrozenTree`, so the fixture and the live read return the same shape and the swap is
one import.

---

## 10. Corrections to apply

Mechanical and reviewable, applied by a later pass. **Nothing here edits code, and no
task in this contract commits.** Because both PLAN files are being edited
concurrently, **the grep anchor is authoritative and the line number is advisory.**

### 10.1 P11 — `planning/parts/P11-placement-residual/PLAN.md`

# | Grep anchor (authoritative) | Change
---|---|---
1 | `class FrozenNode` | rename to `Node`, imported from `tree_design.records`; the fixture mirrors P10's 22 fields
2 | `class DestinationProfile` (in `p10_fixtures`) | replace the field list with P10's 17-field shape (§4.2)
3 | `anchor_excerpt_keys` | → `anchor_excerpts: tuple[AnchorExcerpt, ...]`; `IndexEntry` derives its own key tuple
4 | `parent_context: tuple[str, ...]` on the **profile** | → `tuple[NodeContext, ...]`; `IndexEntry` may still flatten to labels
5 | `restrictions: dict` | → `restrictions: Restrictions`
6 | `(item["field"], item["value"])` | → `(item.field, item.value)`
7 | `template_context: dict \| None` | → `TemplateContext \| None`
8 | `class FrozenTree` | import P10's; keep only `tree_with()` as a test helper
9 | `plan_version: str` on the tree | → `plan_version_id: str` (the `IndexEntry.plan_version` **column** name is unchanged)
10 | `"mandatory_review"`, `"shared_branch"`, `"primary_home"`, `"reference_or_alias"` | → `"mandatory-review"`, `"shared-branch"`, `"primary-home"`, `"reference-or-alias"`
11 | `scoped_general_parents` | delete the field and its construction; derive from `node_role == "scoped-general"`
12 | `_node(node_id="n-ignored"` | drop `existing_path` — P10 refuses it on a non-`existing` node
13 | `NodeIdReserved`, `RESERVED_NODE_IDS` | delete the stub, the class, the constant and the raise site; P8 removes its literal instead (§6)
14 | `class FrozenNode` field list | add `origin_node_id: str` and `protected_movement_permitted: bool`; add `origin_node_id` to `IndexEntry`
15 | `**Renaming is the trap.**` | rewrite to P10's minting reality; `reproject` matches on `origin_node_id`, never `node_id` (§5.2)
16 | `def emit_retrieval_stage(conn: sqlite3.Connection` | add `dimension_values=(DimensionValue(dimension="retrieval", ...),)` and namespace the subject as `candidates:{plan_version}:{subject_ref}` (§7)
17 | `def emit_scoring_stage(conn: sqlite3.Connection` | add the `candidate_node_retrieval` subject_ref to `inputs`
18 | `def build_destination_index(conn: sqlite3.Connection` | assert `{e.node_id for e in entries} == tree.freeze_record.legal_destination_ids` (§4.4)
19 | `from tree_design.freeze import frozen_tree` | **unchanged** — P10 adopts this exact spelling

**19 corrections**, concentrated in Tasks 6, 17 and 18 plus the vocabulary spellings
in Task 13.

### 10.2 P10 — `planning/parts/P10-tree-design-freeze/PLAN.md`

# | Grep anchor (authoritative) | Change
---|---|---
1 | `def frozen_tree_fixture() -> FreezeRecord` | → `-> FrozenTree`, returning nodes + profiles + policy
2 | `### Task 15: Freeze, the legality projection` | **add** `FrozenTree` and `frozen_tree(conn, *, plan_version)` to the Produces block and implement them
3 | `shared_material_policy_ids` | keep on `FreezeRecord`; `FrozenTree` additionally carries the resolved **value** and its scope
4 | `RESIDUAL_ACTIONS` | rename to `RESIDUAL_LIBRARY_ACTIONS` — `llm_harness.vocabulary.RESIDUAL_ACTIONS` is §7.7's eight *review* actions, which P11 imports; same name, two closed sets
5 | `def template_schema_validator(` (implementation) | move the `FORBIDDEN_PUBLISHING_KEYS` scan and `_fragment_refs_are_published` into a distinct `published_fragment` authority on `TemplateDependencies` (§8)
6 | `refinement_disposition: str \| None = None` | keep optional on `Node`; add the `validate_for_freeze` check and state the `FrozenTree` non-`None` guarantee
7 | `**Done-means:** DM2 (a)–(e) in full` | add the `FrozenTree` round-trip as the named P11 swap boundary

**7 corrections**, of which #2 and #5 add implementation rather than rename.

### 10.3 P8 — three amendments to a shipped part

# | File:line | Change
---|---|---
1 | `src/llm_harness/placement_validation.py:239` | `if payload.get("generic_hub") is True or destination == "node-hub":` → `if payload.get("generic_hub") is True:` (§6; verified to change no recorded fixture outcome)
2 | `src/llm_harness/template_validation.py:26-27`, `:166`; `src/llm_harness/vocabulary.py` | add `published_fragment` to `TemplateDependencies`, its `ValidationUnavailable` guard, and the two reason codes (§8)
3 | `src/llm_harness/stage_output.py:122` | emit a `DimensionValue(dimension="llm_grounding", ...)` so `llm_interpretation` becomes attributable (§7). Not P11's to fix; recorded here because P11's audit surfaced it

### 10.4 P2 — one documentation change and one test

`src/eval_harness/vocabulary.py:5-11` records SPEC Open question 1 as open. Half of it
is now answered: `candidate_node_retrieval` shares the `retrieval` dimension,
distinguished by subject namespace. `residual`-with-no-stage stays open. Add a test
asserting that no two stages write the same `(dimension, subject_ref)` in one run.

---

## 11. Shared invariants

1. **P10 names every node kind; P11 publishes no parallel vocabulary.** MINOR 6,
   `P10 SPEC:263-266`. `NODE_TYPES`, `NODE_ROLES` and `RESIDUAL_DISPOSITIONS` are
   P10's; P11 re-exports them, and their *values* are already identical
   (`P10 PLAN` grep `NODE_ROLES: tuple` vs `P11 PLAN` grep `NODE_ROLES: tuple`). Only the constant names differ
   (`RESIDUAL` / `RESIDUAL_ROLE`, `LEAVE_IN_PLACE` / `LEAVE_IN_PLACE_DISPOSITION`),
   which is legitimate: P11's spelling disambiguates its own collisions.
2. **P11 mints no node.** A destination the user creates after freeze routes to P10,
   opens a draft plan version, and appears in the node-level diff (`P10 SPEC:573-582`).
   §7.6's `create_custom_branch` is a *request*, not a mint.
3. **No filesystem path crosses the seam** except `existing_path` on an `existing`
   node. Resolution B3, `P10 SPEC:245`, `P11 SPEC:155`. P12 composes every path from
   `root_anchor` plus the ancestor `display_label` chain.
4. **Node existence is not legality.** `P11 SPEC:134-137`. The legal set is
   `freeze_record.legal_destination_ids`; P11's index is its projection.
5. **P11 never re-classifies sensitivity.** `handling_class` arrives from P7 through
   P10 and is carried, never derived (`P11 SPEC:120`).
6. **Every excerpt citation is an `observation_key`**, never an `observation_id`.
   Resolution M14, `P11 SPEC:190-198`, and `AnchorExcerpt.observation_key` on P10's
   side.
7. **Fixtures are contract witnesses, not authorities.** `tests/p11/p10_fixtures.py`
   mirrors P10's records exactly and is deleted at the swap; no module under
   `src/placement/` constructs a node.
8. **A frozen plan version is immutable.** Every edit opens a draft
   (`P10 SPEC:566-572`, §8.8). P11 re-projects; it never remaps.

---

## Open questions — not settled here

Genuinely undecided by the design. No answer is invented to make this document look
finished.

1. **Can a `protected` node without a movement policy be a destination at all?**
   Both SPECs derive `accepts_placement = false` for it (`P10 SPEC:235-240`,
   `P11 SPEC:130-133`), and P11 indexes only `accepts_placement = true` nodes
   (`P11 PLAN`, grep `for node in tree.nodes if node.accepts_placement`), so such a node is never retrieved and never placed into.
   But `P10 SPEC:239-240` also says *"Absent that policy the node is a legal
   destination for a **reviewed** placement only."* Those cannot both hold. §8.4's
   phrase is *"should not be moved automatically without a user policy that explicitly
   permits it"* — which is about the **move**, not the destination's legality, and
   would favour making `accepts_placement` false for `ignored` alone and expressing
   the protected rule as `review_policy`. Two SPECs agree on the current derivation,
   so this contract does not overturn them. **For Joseph.**

2. **Is a `node_id` stable across plan versions?** P10's OQ5. §5.2 makes the seam
   correct under either answer by matching on `origin_node_id`, but the question is
   still open, and it also decides whether a *pending* P12 move survives a tree edit —
   which no part has answered.

3. **Is the shared-material policy tree-global or per-branch?** P10's OQ9 and P11's
   OQ12. `FrozenTree` carries `shared_material_policy_scope` so either answer fits,
   but P11's behaviour on a file spanning two branches carrying *different* policies
   is undefined by both SPECs.

4. **Does `retrieval` remain a `SHARED_EVIDENCE_DIMENSION` once P11 emits into it?**
   `src/eval_harness/vocabulary.py:47-48` partitions the ten dimensions into
   plan-scoped and shared-evidence, and P11's candidate retrieval is plan-scoped by
   construction. Nothing consumes the partition today — a grep finds only the
   definition and one vocabulary test — so nothing breaks, but the partition now
   asserts something false. **P2's to resolve.**

5. **Does §7 residual handling get its own attribution stage?** The other half of P2's
   Open question 1. P11 attaches the `residual` dimension to `placement_scoring` and
   says so (`P11 PLAN`, grep `A correct abstention passes both dimensions`), which is defensible but means a residual error attributes
   to a placement stage.

6. **What is `template_binding` for, at the P11 end?** P10 publishes
   `template_binding: str | None` on the profile; P11's fixture omits it and its
   `IndexEntry` carries `template_fields` only. Whether retrieval should score on the
   binding identity — two branches sharing one recipe — or only on the fields is not
   decided by §6.2, which lists *"template fields"* and not the binding.

7. **Does an alias convention produce a filesystem artefact?** P11's OQ7, which its own
   plan marks as *"Threatens P12's contract."* P11 names a node under all four
   shared-material policies and creates no link; P12 has not said whether it must.

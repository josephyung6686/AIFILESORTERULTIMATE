# P10 — Tree design and freeze

Owns: §5, §6.1, §7.2–§7.4
Status: contract draft

## Purpose

P10 turns everything the corpus is now understood to contain — validated facts (§3), accepted
groups (§4), existing curated folders (§1.1, §5.10) — into **one artefact: the frozen destination
tree**, and publishes it as the closed set of legal destinations that §6 is permitted to place
into.

Two properties make this the most consequential contract in the system:

1. **After freeze, no component may invent a destination.** §5.12: "Freeze records the approved
   hierarchy and prevents later systems from inventing new destinations outside it." §6.2 states
   the same negatively: the engine "is **not** allowed to invent a new `Math Stuff` folder merely
   because the file looks mathematical." Every destination P11 may name, and every destination path
   P12 may create, exists in the artefact P10 publishes — or the placement abstains (§6.10).
2. **Freeze is a view, not a rewrite.** §5.12: "The facts and accepted groups remain separate from
   the tree, so the user can change the visual organization without destroying the underlying
   evidence." §3.14 makes the same guarantee from the other side: the same facts may be arranged as
   `Academics/Columbia/2026-Spring/BUSIB 4300/Syllabus` or `Academics/BUSIB 4300/Spring 2026/
   Syllabus` — "The facts have not changed; only the user's preferred organization view has
   changed."

P10 is also the one heavily user-facing part (§5 opening: "the most important user-facing stage of
the pre-sorting system"). What this spec fixes about the interface is the **data each surface must
be able to render** and the constraints the design imposes on it — explanations rather than
confidence scores (§5.2), existing structure visually distinct from proposals (§5.10), sensitive
material shown as a protected area without filenames (§5.2). Visual design is deferred (below).

P10 also owns the **residual template library** (§7.2–§7.4) and the **destination profile** (§6.1).
Both sit here for the same reason: they are constituents of the frozen artefact, not consumers of
it. §7.4 makes an approved residual branch "a legal node in the frozen destination tree," so a tree
frozen without the library is incomplete; and every ingredient of §6.1's profile is a value P10
already holds at freeze. The residual *workflow* (§7.5–§7.11) and the §6.2 retrieval index remain
P11's (resolutions M10, B4).

P10 does not move, copy, rename, or classify a single file. §5.12: "The tree does not yet move or
classify files."

## Design slice owned

| § | What P10 owns |
|---|---|
| §5.1 | Horizontal pass — deriving a small candidate set of top-level branches from accepted groups, domain memberships, existing curated folders, user-approved labels |
| §5.2 | The branch candidate card, the six branch actions, protected-area presentation, existing folders as adoptable user-created structure |
| §5.3 | Vertical pass — branch by branch, never the whole corpus at once |
| §5.4 | Templates as controlled schemas: dimensions, recommended order, optional, metadata-only, safety/usability constraints |
| §5.5 | Live branch counts before commit; parent-provides-context-for-child; subject-before-time with photos as the exception |
| §5.6 | Purpose-defined packets coexisting with institution-based organisation |
| §5.7 | Template library structure; the LLM-generated custom-template JSON schema and its six engine validation checks |
| §5.8 | Uneven depth as a requirement |
| §5.9 | Live structural feedback; warnings; the scoped `General` branch; no global catch-all default |
| §5.10 | Existing folders visible throughout; never silently reorganised |
| §5.11 | Tree health |
| §5.12 | Node types; the proposed destination tree; freeze; the facts-stay-separate guarantee |
| §6.1 | The destination profile every frozen node becomes — its contents and its emission |
| §7.2 | The residual template library: its purpose, and the eight attribute slots every residual template defines |
| §7.3 | The initial library — the nine template names, and support for user-defined residual areas |
| §7.4 | Residual branches are opt-in: enable / disable / rename / relocate / merge / replace-with-existing; the three dispositions; approved residual branches become legal nodes in the frozen tree |

**Why §7.2–§7.4 are P10's** (resolution M10). §7.4 is literal that "once the user approves the
desired residual branches, those branches become legal nodes in the frozen destination tree." A
residual branch is therefore a node in the artefact P10 freezes, and P10 cannot freeze a *complete*
tree without the library that produces those nodes. Holding the definitions in P11 made P10 depend
on the part that consumes P10's own output. The residual **workflow** — surfacing, set-level
decisions, the eight-action review, bulk decisions, the non-destructive lifecycle (§7.5–§7.11) — is
P11's and is not touched here.

Adjacent sections P10 **serves but does not own**: §6.2 (the destination-node retrieval index built
over the profile — P11), §7.5–§7.11 (the residual workflow — P11), §3.11 (fact schemas — P6), §8.4
(handling classes — P7), §5.7's model call mechanics (P8).

## Contract in

### From P9 — accepted groups (§4)

Per accepted group:

| Field | § |
|---|---|
| `group_id`, user-approved `label` | §4.5 task 4 |
| `group_category` | §3.11, §3.15, §4.5 |
| `members[]` each with `membership_kind` ∈ {`direct-anchor`, `context-supported`, `user-attached`} | §4.3, §4.8, §4.9 |
| `anchor_facts[]` — the validated facts that justify the group | §4.2, §4.4 |

**`group_category` is the domain** (resolution M12). P9's `group_category` draws on the §3.11 /
§3.15 domain vocabulary, so domain and category are one field, not two; P10 does not request a
separate `domain`. Template *applicability* reads it (§5.3, §5.4), but it is not a one-template
ownership key: one template may be valid in several domains, one domain may offer several templates,
and a purpose-coherent branch may compose compatible fragments across domains. The many-to-many
routing contract is `docs/superpowers/specs/2026-08-26-composable-template-scaffolding-design.md`.

**Three membership kinds** (M12). The third, `user-attached`, is §4.9's manual attachment — the
route by which a file whose contents could not be read still joins a group. It is a legal
membership and a tree branch may be justified by it, but P10 must not present a `user-attached`
member as evidence-derived in an `explanation` (§5.12, §5.2).

**Two lists P10 derives rather than requests** (M12):

- `excluded_members[]` — derived from `Membership.decision = excluded` and the conflict recorded
  against it. Feeds the branch candidate card and the profile's `known_exclusions[]` (§4.5 task 3,
  §4.8, §6.1).
- `rejected_proposals[]` — derived from `Group.state = rejected`. A rejected proposal must not be
  resurfaced as a branch candidate (§4.9, §8.7).

Consequence P10 must honour: a file may validly belong to more than one accepted group (§4.9) — the
tree must not force a group to a single branch to make membership single-valued.

### From P6 — facts (§3)

`fields` / `values` / `file_facts` with the six reliability states (§3.12, §3.13); per-file active
domain memberships (§3.11); value normalisation and user aliases (§2.8, §3.12). P10 reads facts; it
never writes them (§3.14). P10 may not introduce a new **field** (§3.12: the system "should not
invent new fields automatically"); a template may only reference fields P6 already defines.

### From P3 — corpus and existing structure (§1.1, §1.2)

Candidate roots the user selected, the cross-root movement permission (§1.1: "whether files may
move across high-level folders"), the exclusion decisions (§1.1), and the existing-folder inventory
with per-folder file counts and directory position (§1.2). §5.10 additionally requires a
curated-versus-incidental signal per existing folder; **P3 computes it** as an observation over the
directory inventory it already publishes (resolution G9). P10 renders it and treats a curated folder
as a strong expression of user intent (§5.10); it does not re-derive the signal.

### From P7 — privacy (§8.4)

Per-file handling class (`Public or low sensitivity` … `Unreadable or unclassified`) and the active
operation mode, one of P7's four closed §8.4 values spelled P7's way: `offline`, `local_model`,
`hybrid`, `cloud_assisted`. P7 owns that vocabulary — *"a value outside this set is a load
error, not a fallback"* — so P10 carries the literals verbatim and coins no display variants of them.
P10 does not classify sensitivity; it renders and enforces it (§5.2, §8.4).

### From P8 — the model call (§5.7, §3.6)

P10 supplies a custom-template dossier and receives a cited structured response plus a validation
verdict. P8 owns bounded-dossier → cited response → verdict; P10 owns the template JSON schema and
the six semantic checks of §5.7 — stated outright under [Contract out §3](#3-the-template-schema-54-57)
and closing P8's former Q9 (05-minor-resolutions). Dossier contents are fixed by §5.7: "the group dossier,
representative files, validated facts, the user-approved group label, existing destination
vocabulary, and structural constraints."

### From P11 — nothing at tree-design time

P11 consumes the frozen tree; it supplies nothing to it. The residual template definitions that
previously appeared here are P10's own (§7.2–§7.4, resolution M10) and are published under
[Contract out](#contract-out). This removes the only P10 → P11 dependency; the seam is now
one-directional, P10 → P11.

### From P1 — storage (§0, §8.2)

Append-only event log; durable plan-version and node records (§0 lists "destination nodes" and
"taxonomy aliases" among the SQLite contents).

### From P13 — collected tree edits (§5, §8.8)

Tree edits arrive as P13's `review_action` in full, collected on `surface = canvas | plan_version`
with `subject_ref` a `node_id`, and carrying `plan_version`, `action` — including §8.8's
`adopt_version` and `restore_version`, and a custom folder created during residual review — plus
`correction_scope` (§8.7) and `presented_state_ref`. P13 presents and collects; it decides nothing.
**P10 authors the edit, and an accepted edit produces a new plan version** (M8, §8.8); P1 writes the
event.

## Contract out

Six artefacts. (1)–(3) and (6) are what P11 builds against; (4) is what P12 and §8.8 build against;
(5) is what P2 measures.

**Emits P2 `stage_output` for the two §8.5 stages P10 owns** (§8.5, resolution B7) — one per subject
it decides about:

| `stage_id` | §8.5 name | P10's subject |
|---|---|---|
| `template_generation` | template generation (§5.4, §5.7) | the branch a template was generated for or applied to |
| `tree_design` | tree design (§5) | the branch candidate or node the design pass decided about |

Both values are drawn from P2's **closed** ten-value enumeration and P10 emits no other. `P10` is
not a `stage_id`; a part name in that field would leave two of §8.5's ten stages with no producer and
P2's `attributed_stage` unable to name where a tree error began. Each envelope carries `inputs[]` —
the `subject_ref`s of the `grouping` and `factual_validation` stage outputs it consumed — an explicit
abstention value, a distinct budget-deferral value, and the version tuple.

**The envelope's vocabulary is P2's, not P10's.** P2 owns `outcome ∈ produced | abstained | deferred
| not_implemented | error` and `budget_state ∈ within_ceiling | ceiling_reached`; P10 maps its own
results into those values rather than restating the separation in words of its own:

| P10 result | `outcome` | `budget_state` |
|---|---|---|
| a template was generated or applied, or a branch candidate / node was proposed | `produced` | `within_ceiling` |
| nothing was proposed on the evidence — a candidate template rejected by V1–V6, or a branch the design pass declined to propose (§5.7, §5.1) | `abstained` | `within_ceiling` |
| an §8.6 ceiling stopped the work — a `template-deferred` branch, or surplus candidates shown as deferred | `deferred` | `ceiling_reached` |
| the stage failed | `error` | — |
| P10 not built yet | `not_implemented` | — |

The evidential abstention and the budget deferral are two envelope values, not one value described
twice. A `template-deferred` branch and a deferred surplus candidate — both described under
[Budgets and degradation](#budgets-and-degradation-86) — are `deferred` with `ceiling_reached` and
are **never** `abstained`, so a ceiling-truncated pass is never scored as a design judgement. P2
Done-means 6 depends on exactly this: `deferred` is reported separately from `divergent` for every
dimension, so a run whose only change is a lower budget ceiling produces zero new divergences.

### 1. The node record — the frozen tree (§5.12)

§5.12 fixes the mandatory fields: "Each node has a type — existing, proposed, user-created,
protected, or ignored — a display label, a parent, associated groups, a template context where
relevant, and an explanation of the facts or accepted groups that caused it to appear."

| Field | Meaning | § |
|---|---|---|
| `node_id` | stable identifier; the tree is addressed by ID, never by path string | §8.8 ("node identifiers"), §8.3 ("Requested destination node" is distinct from "Resolved destination path") |
| `plan_version_id` | the plan version this node belongs to | §8.8 |
| `node_type` | `existing` \| `proposed` \| `user-created` \| `protected` \| `ignored` | §5.12 |
| `display_label` | the intended display name; may be a user alias over a normalised value | §5.12, §2.8, §8.8 ("User labels and aliases") |
| `parent_node_id` | null for a top-level branch | §5.12 |
| `root_anchor` | which §1.1 candidate root this subtree hangs beneath | §1.1, §5.2 ("move it under an existing root such as Documents") |
| `ordinal` | sibling order as the user arranged it | §5 ("reorder") |
| `associated_group_ids[]` | accepted groups that live beneath this node | §5.1, §5.12 |
| `template_context` | `{binding_id, template_id, template_version, fragment_id?, fragment_version?, dimension_index}` where relevant; exact versions identify the branch-local composition and the source of this level | §5.12, §8.8 |
| `dimension_role` | the organization-layer semantic role this level realises, if any; never a fact key | §5.4, §5.5 |
| `dimension` | the live P6 field to which `dimension_role` resolved for this branch, if any | §3.12, §5.4, §5.5 |
| `expected_values[]` | `field = value` this level asserts, e.g. `course = PHYS1401` | §6.1 ("expected field values") |
| `explanation` | the facts or accepted groups that caused it to appear — prose, not a score | §5.12, §5.2 |
| `existing_path` | present only when `node_type = existing` | §5.10 |
| `handling_class` | carried from P7, not re-derived | §8.4 |
| `node_role` | `ordinary` \| `scoped-general` \| `residual` \| `shared-material` | §5.9, §7.4, §6.9 |
| `disposition` | required on `residual` nodes: `physical-destination` \| `review-only` \| `leave-in-place` | §7.4 |
| `accepts_placement` | derived; see rule below | §5.12, §5.10, §8.4 |
| `refinement_disposition` | `refined` \| `shallow-by-choice` \| `refine-later`; required on an approved branch | §5.3, §5.8, §8.8 |
| `refinement_reason` | user/evidence-backed explanation distinguishing intentional shallowness from unfinished work | §5.2, §5.8, §8.8 |

**`accepts_placement` derivation** — P11 needs one flag, not a case analysis:

- `existing`, `proposed`, `user-created` → `true`.
- `ignored` → `false`. §5.10/§5.2 permit the user to leave an existing folder untouched; an ignored
  node is visible context, not a destination.
- `protected` → `true` only where an explicit user policy permits automatic movement. §8.4:
  protected material "should not be moved automatically without a user policy that explicitly
  permits it." Absent that policy the node is a legal destination for a **reviewed** placement only.

**Label changes never change facts.** Renaming a node rewrites `display_label` only; the underlying
`expected_values` and the evidence behind them are untouched (§2.8, §3.14, §5.12).

**P10 holds no filesystem path strings** (resolution B3). §8.3's plan record carries "Requested
destination node" and "Resolved destination path" as two separate fields; P10 owns the first and
**P12 owns the second**. What P10 publishes for a destination is `root_anchor` plus the ancestor
`display_label` chain reachable through `parent_node_id`; P12 composes those into a path and applies
§8.3's case-sensitivity, Unicode-normalization, reserved-name and path-length rules, recording the
intended display name separately from the filesystem-safe name. The one exception is `existing_path`
on a `node_type = existing` node, which is an observed fact about the corpus (§5.10), not a
composition. The reason is not tidiness: a plan-versioned tree that held platform-specific strings
would resolve differently on a case-sensitive and a case-insensitive volume, and the same frozen
tree must resolve correctly on both (§8.3, §8.8).

**The five fields P11 reads to decide legality** (resolution B6). P10 publishes, and P11 consumes
rather than re-derives, `accepts_placement`, `node_role`, `disposition`, `expected_values[]` and
`handling_class`. `accepts_placement` in particular exists for exactly one purpose — to stop P11
placing into an `ignored` node, which is §5.10's guarantee that a user may leave an existing folder
untouched — and `handling_class` carries §8.4's protected-node rule down to the placement layer
without P11 re-classifying sensitivity.

**`node_role` is the single vocabulary for a node's kind** (MINOR 6). P10 owns the tree, so P10 names
its node kinds; P11 carries `node_role` verbatim on the destination it names and publishes no parallel
vocabulary of its own. The `shared-material` value is what lets a placement say "this is §6.9's shared
branch" structurally rather than through a confidence label.

**Uneven depth is legal by construction** (§5.8). No validation rule may require sibling subtrees to
have equal depth, and no branch is required to realise every dimension of its template: "each branch
should offer the dimensions that are actually present in its member groups."

Example node:

```json
{
  "node_id": "n_7f2a",
  "plan_version_id": "plan_3",
  "node_type": "proposed",
  "display_label": "Homework",
  "parent_node_id": "n_7f29",
  "root_anchor": "root_documents",
  "ordinal": 2,
  "associated_group_ids": ["g_phys1401_course"],
  "template_context": {
    "binding_id": "btb_academic_columbia_v1",
    "template_id": "academic-coursework",
    "template_version": 1,
    "fragment_id": "artifact-kind",
    "fragment_version": 1,
    "dimension_index": 3
  },
  "dimension_role": "artifact_kind",
  "dimension": "work_type",
  "expected_values": [{"field": "work_type", "value": "Homework"}],
  "explanation": "Six files in the accepted PHYS1401 course group carry work type = Homework, validated from filename and document structure.",
  "handling_class": "personal_non_sensitive",
  "node_role": "ordinary",
  "refinement_disposition": "refined",
  "refinement_reason": "The course has enough populated work types for this level to improve retrieval.",
  "accepts_placement": true
}
```

### 2. The destination profile (§6.1, §6.2)

§6.1: every frozen node "should become an active destination profile … Its profile contains the
branch's domain, template, expected field values, parent and child meanings, accepted group
memberships, user-selected label, known exclusions, representative files, rich anchor files, and any
privacy or policy restrictions." §6.2 adds "anchor excerpts, known document types, parent and child
context, and explicit user edits."

P10 **emits the profile**; P11 **builds the retrieval index over it** (§6.2: "The system should build
a destination-node retrieval index after the tree is frozen"). The split matters because the index is
a placement mechanism; the profile is a description of what the user approved.

**The profile is P10's alone** (resolution B4). Every §6.1 ingredient — template, expected field
values, accepted group memberships, user-selected label, known exclusions, privacy restrictions — is
a value P10 already holds at freeze; none is produced by placement. P11 receives the profile in its
Contract-in from P10, does not build one, and does not carry profiles in its plan-version state.
02's own *Publishes* column for P10 reads "node types **and destination profiles**".

| Profile field | Source | § |
|---|---|---|
| `node_id`, `display_label` | node record | §6.1 ("user-selected label") |
| `domains[]`, `template_binding`, `template_fields[]` | branch-local template context; a single-domain branch has one domain, while a purpose branch may preserve several one-schema applicability bindings | §3.11, §5.6, §6.1, §6.2 |
| `expected_values[]` | node record | §6.1 |
| `parent_context[]`, `child_context[]` | ancestor + child labels, dimensions and expected values | §6.1 ("parent and child meanings"), §6.2 |
| `accepted_group_ids[]`, `group_labels[]` | P9 via node | §6.1, §6.2 |
| `representative_files[]` | accepted-group members resolved to this node | §6.1, §6.2 |
| `anchor_files[]`, `anchor_excerpts[]` | P9 direct anchors + their cited evidence, each excerpt cited by **`observation_key`** | §6.1, §6.2, §8.7 |
| `known_document_types[]` | work/document-type facts present among members | §6.2 |
| `known_exclusions[]` | `excluded_members[]` (derived, above) ∪ node-scoped user rejections | §6.1, §4.5, §8.7 |
| `user_edits[]` | the tree edits that shaped this node | §6.2 ("explicit user edits") |
| `restrictions` | handling class, consent policy, `accepts_placement`, `disposition` | §6.1 ("privacy or policy restrictions"), §8.4, §7.4 |

Protected profiles are redacted at the boundary, not at the renderer: a profile whose handling class
is sensitive must not carry raw filenames or content into anything bound for a cloud prompt (§8.4,
§5.2).

### 3. The template schema (§5.4, §5.7)

One closed record family governs built-in templates, LLM-generated custom templates, and saved personal templates
(§5.7: the user "either accepts it as a one-off structure or saves it as a reusable personal
template"). §5.7 fixes the library-template fields — "the domain's allowed fact fields, detection
signals, recommended folder dimensions, preferred dimension order, optional branch patterns, privacy
rules, and validation constraints" — and the generated-template fields — "a domain name, allowed
fields, recommended folder dimensions, field order, optional versus required levels, metadata-only
fields, sensitivity policy, and example paths."

The schema is composable, not domain-owned. Four records stay distinct:

1. `TemplateFragment` is a versioned reusable sequence of semantic dimension roles and constraints.
2. `TemplateDefinition` composes exact fragment versions plus any template-local roles and
   constraints. P10 publishes no ambiguous generic `Template` record alongside it.
3. `TemplateApplicability` maps those roles to live P6 fields for exactly one `uses_schema` domain.
   Several records may reference one template, and several records may share a purpose context; the
   rows together form the many-to-many domain/template seam without weakening P6's allow-list.
4. `BranchTemplateBinding` records the resolved, edited, branch-local choice in one plan version.

Neither a fragment nor a valid template creates nodes. Only a branch-local binding that passes the
composition checks, materialises successfully against the branch's actual evidence, passes V1–V6,
and receives explicit user approval may contribute nodes to a draft tree. Exact versions are pinned;
a newer library version never migrates an approved branch automatically.

The four records have four schemas; applicability is never nested inside a definition:

```json
{
  "fragment_id": "artifact-kind",
  "fragment_version": 1,
  "roles": ["artifact_kind"],
  "relative_order": [],
  "privacy_floor": "policy_ref",
  "provenance": {"source_refs": ["source_ref"]}
}
```

```json
{
  "template_id": "academic-coursework",
  "template_version": 1,
  "origin_kind": "built-in | llm-generated | user-authored",
  "scope_kind": "domain-focused | cross-domain | purpose-focused | personal",
  "publication_state": "draft | published | retired",
  "fragment_refs": [{"fragment_id": "artifact-kind", "fragment_version": 1}],
  "dimensions": [
    {
      "role_ref": "subject",
      "order_index": 0,
      "requirement": "required | optional",
      "metadata_only": false,
      "retrieval_rationale": "why this level improves retrieval"
    }
  ],
  "optional_branch_patterns": [],
  "sensitivity_policy": {"policy_ref": "policy_ref"},
  "validation_constraints": [],
  "example_label_chains": [["Academics", "Columbia", "2026-Spring", "PHYS1401", "Homework"]]
}
```

```json
{
  "applicability_id": "academic-coursework--academic",
  "applicability_version": 1,
  "template_id": "academic-coursework",
  "template_version": 1,
  "uses_schema": "academic",
  "purpose_profile_ref": null,
  "allowed_fields": ["subject", "work_type"],
  "detection_signal_refs": ["signal_ref"],
  "role_bindings": [
    {"role_ref": "subject", "field_ref": "subject"},
    {"role_ref": "artifact_kind", "field_ref": "work_type"}
  ],
  "exclusions": []
}
```

```json
{
  "binding_id": "btb_academic_columbia_v1",
  "plan_version_id": "plan_3",
  "branch_node_id": "n_academics",
  "applicability_refs": [
    {"applicability_id": "academic-coursework--academic", "applicability_version": 1}
  ],
  "resolved_dimensions": [
    {"role_ref": "subject", "field_ref": "subject", "action": "selected"}
  ],
  "accepted_group_ids": ["g_phys1401_course"],
  "state": "approved",
  "depth_disposition": "refined",
  "refinement_reason": "The accepted course groups justify the selected split.",
  "validation_report_ref": "validation_report_id",
  "approval_action_ref": "review_action_id"
}
```

Rules the schema carries:

- Every applicability `allowed_fields` entry and role-binding `field_ref` must resolve to a P6 field
  (§3.12, §5.7: "use existing field types wherever possible"). Semantic roles are organization-layer
  slots, not new facts; a template may not mint a field.
- Applicability is many-to-many through join rows. Each row names exactly one `uses_schema`, preserving
  the domain catalogue's current contract; the same template/fragment identity may have rows for
  several domains, and one domain may expose several templates. Reuse is by stable ID/version, never
  copied JSON.
- `purpose_profile_ref`, when present, is an authored `{purpose_profile_id,
  purpose_profile_version}` in the applicability registry. It is not a P6 field/value and not a P9
  runtime `group_id`. `BranchTemplateBinding.accepted_group_ids[]` names the actual accepted groups;
  C3 proves from their evidence that the authored purpose profile applies. P10 invents no universal
  purpose taxonomy and never unions the rows' schema allow-lists.
- Fragment imports form an acyclic graph and pin exact versions. Semantic constraints combine by
  intersection; an empty allowed set, incompatible value type, impossible cardinality, ambiguous
  role binding, or cyclic order is a reported conflict rather than last-writer-wins.
- `metadata_only: true` means the role's resolved field belongs to every selected applicability
  context but may never become a folder level (§5.4: "which ones are metadata only").
- `dimensions` are ordered by `order_index`; the order is a **recommendation** — "the user can
  reverse, remove, add, or flatten dimensions" (§5.5).
- **Values are never invented.** §5.4: "The system does not invent `PHYS1401`, `UChicago`,
  `Spring 2026`, or `PVA/RDP`; those names emerge from validated facts, user-confirmed groups, and
  accepted labels. The template simply determines how those real values could be arranged as
  branches."
- `retrieval_rationale` belongs to the reusable definition. The branch/dossier-specific
  `justification_fact_refs` §5.7 requires of an LLM proposal belong in its validation report and the
  resulting `BranchTemplateBinding`, never in the immutable reusable definition.
- `example_label_chains` are nested display labels used only to review a recipe. They are not path
  strings, do not contain separators, and cannot be resolved or emitted as destinations; P12 alone
  composes filesystem paths.

**Ordering doctrine** (§5.5), applied when a template's recommended order is computed or reviewed:

1. "A parent dimension should provide the context required to understand the child." `Homework 3` is
   meaningful only after the course is known; a course code may need school or term to disambiguate.
2. For document and record domains, project / function / subject precedes time, "because putting year
   first scatters related work across calendar folders."
3. Photos and capture-based media are the **explicit exception**: "time often belongs first because
   capture date is a defining aspect of the material."

**The six engine validation checks** (§5.7) — **P10 runs all six** (closes P8's former Q9, 05-minor-resolutions).
§5.7 places them on "the engine" that validates a generated template *against the accepted group*, which
is freeze-time work over material only P10 holds. P8 enforces the other half of §5.7's sentence —
"Structured output constraints and schema validation should enforce the required template shape" — and
returns its verdict; it runs none of the six. A candidate template is rejected if it:

| # | Check | § |
|---|---|---|
| V1 | repeats a parent dimension | §5.7 |
| V2 | creates meaningless one-child levels | §5.7, §5.9 |
| V3 | exceeds practical depth limits | §5.7, §8.6 (limit value: open question) |
| V4 | uses an author or organization merely as a collector | §5.7, §3.8 ("A folder should not become a collection point for everything produced by the same person or organization") |
| V5 | exposes protected information | §5.7, §8.4 |
| V6 | produces empty branches when tested against the accepted group | §5.7 |

These six labels are P10's template checks and have no relation to P1's separately numbered V1–V4,
which are §8.2's checksum verification points.

**Composition gates precede V1–V6.** C1 resolves every exact template, fragment, applicability, and
version identity. C2 resolves every selected role to a live P6 field. C3 verifies applicability from
the branch's accepted groups and facts rather than domain label alone. C4 rejects ambiguous role
bindings. C5 rejects cyclic or incoherent combined ordering. C6 proves that the preview silently
drops no group or file. C7 preserves the strongest included privacy restriction. C8 keeps every valid
result inert until branch-specific user approval. A failure returns a deterministic report naming the
conflicting inputs and creates no nodes.

Plus the gates that precede them: strict JSON-schema conformance (P8's), every cited fact actually
present in the evidence database (§3.6, §4.8), and — decisively — **validity is not activation**. §5.7: a
generated template "cannot invent unsupported facts, silently create new high-level domains, or
become active merely because it is syntactically valid … semantic validation and user approval remain
necessary, because a technically valid LLM-generated template can still be a poor organization
design." A template with a clean verdict is a proposal on the canvas, nothing more.

**Purpose-defined packets are not a template failure** (§5.6). Where an accepted group is
purpose-coherent and content-incoherent — a packet holding a transcript, ID, personal statement,
resume, certificate and research abstract — the canvas must be able to present it "as a preserved or
proposed branch alongside institution-based organization," and support keeping it flat, nesting it,
splitting it by institution, or a hybrid. §5.6: "The template is a recommendation mechanism, not a
rule that erases purposeful heterogeneity." No validation check may reject a branch for internal
heterogeneity alone.

### 4. The freeze record (§5.12, §8.8)

Freeze produces an adopted plan version. §8.8 fixes its contents; the rows below are that list,
attributed to owners:

| Recorded | Owner | § |
|---|---|---|
| Plan ID and version, creation time | P10 | §8.8 |
| Destination tree and node identifiers | **P10** | §8.8 |
| Existing versus proposed versus user-created nodes | **P10** | §8.8, §5.12 |
| Template versions and ordering choices | **P10** | §8.8, §5.4 |
| Accepted and rejected group memberships | P9, referenced | §8.8 |
| User labels and aliases | **P10** | §8.8 |
| Residual-library configuration | **P10** — definitions and enable/disable/rename/relocate/merge/replace choices alike (M10, O11, O12) | §8.8, §7.2–§7.4 |
| Privacy and model-consent policies | P7, referenced | §8.8 |
| Placement policy settings | P11, plus §1.1 cross-root movement permission and §6.9 shared-material policy recorded by P10 | §8.8, §1.1, §6.9 |
| Associated review decisions | P11, referenced | §8.8 |

Two tree-level policies P10 must capture at freeze because the design places them in the tree:

- **Shared material** (§6.9): "The user's frozen tree should therefore include a policy for shared
  material: a shared branch, a primary-home convention, a reference or alias convention, or mandatory
  review." Without it, §6.9 requires P11 to abstain on a transcript belonging to two application
  packets rather than pick a university.
- **Scoped fallback** (§5.9): which meaningful parents carry a `General` / `Other` child. §5.9 permits
  `Academics/Columbia/2026-Spring/General` and forbids the global alternative: "A global catch-all
  folder should not become the product's default answer to ambiguity."

What freeze **does not** record: facts, evidence, or accepted-group evidence. §5.12: "The facts and
accepted groups remain separate from the tree." §8.8: "The evidence database remains shared across
plan versions."

**The freeze guarantee, stated for P11 and P12:** the set of legal destinations is exactly
`{node_id : plan_version = frozen version, accepts_placement = true}`. Validating a proposed
destination is an ID membership test (§6.10: the validator "confirms that the selected node exists in
the frozen tree"). A destination that is not in the set has no legal expression — P11 abstains
(§6.10: "Correct abstention is a successful outcome").

**A useful shallow scaffold is freezeable.** “Complete” means that every included node is legal,
explainable, validated, and approved, and every unresolved branch is explicitly marked for later
refinement or shallow by choice. It does not require every branch to realise every template dimension.
Refining an explicitly deferred or shallow branch after freeze follows the ordinary new-draft and
new-version path below.

**Editing after freeze** (§8.8): a frozen version is immutable. An edit opens a **draft** version and
must show a diff. P10 emits the node-level diff — nodes added, removed, renamed, re-parented,
re-templated, re-ordered, type-changed. §8.8's file-level consequence ("twenty-three files now require
renewed review because their previous destination no longer exists") is computed by P11 from that diff
against its placement decisions. Adoption is explicit and earlier versions are restorable; §8.8: "A
new plan should never silently reclassify or move old files."

**The user may create a folder after freeze** (closes OQ4). A destination the *user* adds after freeze
— including the "create a custom folder" action §7.10 gives them during residual review — is an ordinary
tree edit: it is routed to P10, opens a **draft** plan version, and appears in the node-level diff like
any other edit (§8.8: "When the user edits the tree, the product should create a draft plan version and
show a meaningful diff"). It never amends the frozen version in place. It is also not what §5.12 and
§6.12 prohibit: that prohibition is on the *system* inventing a destination after freeze, not on the
user editing their own tree. P11 mints no node — it routes the request here and consumes the resulting
version (§7.6's `create_custom_branch`, §7.10).

### 5. Canvas data contracts (§5.1, §5.2, §5.5, §5.9, §5.10, §5.11)

The surfaces below are contracts over data, not layouts. Each must be renderable from published
fields alone.

**Branch candidate** (§5.1, §5.2) — per candidate top-level branch: why it was suggested, supporting
file count, whether an existing folder already resembles it, which accepted groups would live beneath
it, whether sensitive content is present, representative groups, existing related folders, and a
concise explanation. §5.2 forbids the obvious alternative: a concise explanation "rather than a
technical confidence score." Internal scores may exist (§3.13) but are not this surface.

Candidate branches are **derived**, not enumerated. §5.1: labels "should reflect the user's vocabulary
rather than a universal corporate taxonomy"; the nine names §5.1 lists (Academics, Applications,
Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects,
Media or Miscellaneous Personal Material) are what "a typical initial canvas might include" — they are
illustrative and must not be shipped as a fixed set.

Actions available: accept, rename, merge into another branch, move under an existing root, defer,
create manually (§5.2); add, remove, rename, merge, split, nest, reorder, ignore (§5 opening); drag an
accepted group into a branch, delete a suggested area (§5.1).

**Protected areas** (§5.2, §8.4) — a Finance or Identity proposal "may be visible as a protected area,
but the product should avoid showing sensitive filenames or sending their contents to cloud services by
default." §8.4 adds that protected branches carry configurable redaction across names, previews,
thumbnails, OCR text and location data.

**Existing folders** (§5.2, §5.10) — visible throughout, showing filesystem position, file count,
overlapping facts and accepted groups, and whether the folder appears curated or incidental. A curated
folder "should be treated as a strong expression of user intent." Available actions: preserve, adopt as
a branch, merge with a proposal, attach a proposed branch beneath it, rename the proposal to match it,
or leave it untouched. The hard prohibition (§5.10): "Existing folders must not be automatically
flattened, renamed, or reorganized simply because a template would produce a different structure." The
canvas must make existing structure and proposed structure visually distinct (§5.10).

**Vertical pass** (§5.3) — one branch at a time, never the whole corpus at once. Opening an accepted
branch proposes one or more domain templates "based on the groups and facts that already belong inside
it." The user retains a compact top-level context, current path, sibling branches, and refinement
state while working inside the branch. Candidates may be a complete reusable template, a compatible
composition of reusable fragments, or no split. Each candidate states its source/version,
applicability evidence, assumptions, and conflicts. The user may apply only part of it and may keep
the branch shallow without making the plan invalid.

**Live structural feedback** (§5.5, §5.9) — before a split is committed: resulting number of child
branches, number of files under each child, example members, unresolved files, evidence gaps. §5.5
requires the whole-option preview too: that Option A "would create three schools, five terms, and twelve
course branches"; that Option B "would merge material across schools when course codes collide"; that
Option C "is shallower but leaves more files together."

Warnings (§5.9): a level producing only one child; a level repeating a concept already expressed in the
parent; excessive depth; a large number of tiny folders. Plus a flattening recommendation "when a
dimension does not materially improve retrieval." The design deliberately does not set the numeric
thresholds — see Open questions.

**Tree health** (§5.11) — how much of each accepted group the proposed structure represents, how many
files have enough facts to populate a branch, where the tree contains unresolved or context-supported
members, where sensitive material has been isolated, which branches need user decisions. §5.11 also
constrains the framing: it "should not imply that the system must account for every file immediately …
The goal is to give the user a good enough structural gist of the corpus so that only a limited number
of high-leverage changes remain."

### 6. The residual template library (§7.2, §7.3, §7.4)

Moved here from P11 by resolution M10, because §7.4 makes an approved residual branch a legal node
in the tree P10 freezes. P10 publishes the **definitions and the enablement model**; P11 runs the
**workflow** that consumes them (§7.5–§7.11).

**What the library is for** (§7.2). Residual templates are not domain templates. A domain template
builds a deep meaningful hierarchy for a recurring area of life; a residual template provides a
"safe, intentionally broad destination" for a file with no reliable deeper association. The library
exists to prevent one specific failure — §7.2 names it literally: the LLM creating arbitrary folders
such as `Random PDF Things`, `Important Screenshot`, `Miscellaneous Documents`, or `Travel/Gate B12`,
which "may sound plausible but would fragment the user's filesystem and create unmaintainable
structure." A residual template is therefore a *constraint on the model's choices*, not a suggestion.

**The eight attribute slots** every residual template defines (§7.2, literal):

| Slot | § |
|---|---|
| `display_name` — recommended display name | §7.2 |
| `default_parent_location` — recommended default parent | §7.2, §7.3 |
| `accepted_evidence_patterns[]` | §7.2 |
| `expected_file_types[]` | §7.2 |
| `sensitivity_restrictions` | §7.2, §8.4 |
| `optional_shallow_subfolders[]` | §7.2 |
| `max_permitted_depth` | §7.2 |
| `treatment` — reviewed \| retained \| merely kept searchable | §7.2 |

**The nine template names** (§7.3). These are fixed; their slot *values* are deferred (below).
§7.3 states a default parent location for only the first four — the remaining five have none stated
and none is invented here.

| # | Template | Default parent location (§7.3) |
|---|---|---|
| 1 | Temporary Screenshots | `Photos/Temporary Screenshots` |
| 2 | One-Off Images | `Photos/One-Off Images` |
| 3 | Reference Clips | `Personal/Reference Clips` |
| 4 | Independent Records | `Personal/Independent Records` |
| 5 | Receipts and Confirmations | — |
| 6 | Reading Inbox | — |
| 7 | Review Later | — |
| 8 | Unsupported or Encrypted | — |
| 9 | Protected Records | — |

Plus **user-defined residual areas** (§7.3, literal: "the library must support user-defined residual
areas such as Things to Read, Ideas, Shopping Research, Memes, Travel, Receipts to Process, Clips, or
Stuff to Sort, because residual organization is highly personal and should not be dictated by a
universal taxonomy"). Those examples are illustrations of user freedom; the product ships none of
them as templates.

Two of the nine carry a constraint the design states outright and P10 must carry into the node it
freezes: **Unsupported or Encrypted** may "more safely, represent without moving" (§7.3), and
**Protected Records** "should normally remain local-only and must not cause filenames or content to
be exposed in model prompts" (§7.3, §8.4). Both are expressed through `disposition` and
`handling_class` on the resulting node, not through special-casing in P11.

**`default_parent_location` is not a filesystem path** (resolution B3). The four locations §7.3
states are `display_label` chains — a recommended placement in the *tree*, not on disk. When the
user enables a residual branch, it becomes an ordinary node carrying `root_anchor`,
`parent_node_id`, `display_label` and `ordinal` like every other node, and P12 composes its path the
same way. Nothing about a residual node makes it path-bearing.

**The enablement model** (§7.4). Residual templates "are not automatically created." During
tree design the canvas shows the library as an optional set of controlled branches, and the user may:

| Action | Effect on the frozen tree | § |
|---|---|---|
| enable | a node with `node_role = residual` is created | §7.4 |
| disable | no node; the template is not a destination in this plan version | §7.4 |
| rename | `display_label` changes; the template identity does not | §7.4, §5.12 |
| relocate | `parent_node_id` / `root_anchor` change from the template default | §7.4 |
| merge | two enabled templates resolve to one node | §7.4 |
| replace with an existing folder | the template maps onto an `existing` node — §7.4's own case: a user who "already has an existing `To Sort` folder" gets Review Later mapped onto it "rather than inventing a new one" | §7.4, §5.10 |

Every one of these is a `destination-tree edit` event (§8.2) and a §8.7 learning record at node
scope. Enablement choices are **plan-version state** — the "Residual-library configuration" §8.8
lists, owned outright by P10 (resolution O11).

**The three dispositions** (§7.4, literal: the user "can also decide whether a residual template is
a real physical destination, a review-only category that never moves files automatically, or a
policy that tells the system to leave files in place"). These populate `disposition` on the node:

| `disposition` | Meaning | Consequence for P11/P12 |
|---|---|---|
| `physical-destination` | a real folder files are moved into | `place` decisions here reach P12 as moves |
| `review-only` | a category that never moves files automatically | a decision naming it produces no filesystem mutation |
| `leave-in-place` | a policy, not a folder | the file stays where it is; the node records the classification only |

`disposition` is required on every `residual` node and is meaningless on the other roles.

**The freeze consequence** (§7.4, literal): "Once the user approves the desired residual branches,
those branches become legal nodes in the frozen destination tree. The LLM may choose among them
later, but it may not create additional generic destinations." An enabled residual branch is
therefore an ordinary member of `{node_id : plan_version = frozen version, accepts_placement =
true}` — P11 needs no residual-specific legality path — and a residual template the user did not
enable has **no node**, so no model can name it. That is the whole enforcement mechanism.

## Deferred — manual design required

| Deferred item | § that defines it | Note |
|---|---|---|
| **The 200–300 domain-specific templates' contents** | §5.7 | The single largest deferred item in the project. §5.7 describes a library "covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections," each defining allowed fact fields, detection signals, recommended dimensions, preferred order, optional branch patterns, privacy rules and validation constraints. **This spec defines the schema those templates must conform to; it authors none of them.** §5.7 explicitly permits this: "The product does not need to fully implement every template at launch; it can begin with the core domains." |
| Template dimensions beyond the five §5.4 names | §5.4 | §5.4 states dimensions for exactly five: Academic (school → term → course → work type), Applications (target institution → application cycle → document type), Research (project → stage → artifact type), Career (company → role or recruiting cycle → document type), Photos (year → event). No further template dimensions are authored here. §3.15 names six launch domains, so Code — and Finance as a safety domain — have fact schemas (§3.11) but no design-stated dimensions; see Open questions. |
| Domain fact-schema fields beyond §3.11's literal table | §3.11 | P6 owns. Templates reference fields; they do not define them (§3.12). |
| Gazetteer contents | §3.7 ("validated gazetteers") | P6 owns; P10 consumes resolved values only. |
| **Residual template slot values** — the eight §7.2 attributes for each of the nine templates | §7.2, §7.3 | **P10 owns** (M10), and Contract out §6 fixes the nine names, the eight slots, the enablement model and the three dispositions. What is deferred is the *contents* of those slots: accepted evidence patterns, expected file types, sensitivity restrictions, optional shallow subfolders and maximum depth per template, plus the five default parent locations §7.3 leaves unstated. None is invented here. User-defined residual areas (§7.3) are authored by the user, not shipped. |
| All prompt text | §5.7, §3.6, §8.2 (prompt fingerprint) | P8 owns wording; P10 owns the dossier's required contents (§5.7) and the response schema. |
| Canvas visual design | §5.10 | The design fixes one visual requirement — existing nodes in one style, uncommitted suggestions in another (§5.10) — and the data each surface renders. Layout, typography, interaction affordances and the drag model are hand-designed. |
| Default warning copy and explanation phrasing | §5.2, §5.9 | §5.2 fixes the form (explanation, not confidence score) and gives two example cards; the phrasing set is hand-authored. |

## Done means

1. **Every P10 record serialises and round-trips**: node record, destination profile,
   `TemplateFragment`, `TemplateDefinition`, `TemplateApplicability`, `BranchTemplateBinding`, freeze
   record, node-level diff, and residual template library. Shared library records are release/version
   keyed; only bindings and tree state are plan-version keyed.
2. **Fixtures exist that P11 can build against before P10 has any implementation**:
   - (a) the walking-skeleton tree — **two** hand-authored frozen nodes, no template, no groups
     (segmentation map, walking skeleton step P10). Two, not one: resolution B8(b) requires the
     skeleton to exercise §6.10's margin condition rather than bypass it, and a one-node tree
     leaves `margin_over_next` with no value to hold;
   - (b) a realistic tree exercising uneven depth (§5.8), all five node types (§5.12), a
     `scoped-general` node (§5.9), an enabled residual node with each of the three dispositions
     (§7.4), a shared-material policy (§6.9), and a protected branch (§5.2, §8.4);
   - (c) one reusable fragment, one built-in definition, one llm-generated definition with a clean
     verdict, one rejected definition, standalone applicability rows, branch bindings, and **one
     failing fixture per check V1–V6** (§5.7);
   - (d) a two-version pair with its node-level diff (§8.8);
   - (e) a residual-library fixture: all nine §7.3 names present as definitions, a subset enabled,
     one renamed, one relocated off its default parent, one replaced by an existing `To Sort`
     folder, and the rest disabled — with the disabled ones producing **no node** (§7.3, §7.4).
3. **Freeze is enforceable by ID lookup alone.** Given a frozen tree fixture and an arbitrary
   destination string, a caller can decide legality without consulting facts, templates or the
   filesystem (§5.12, §6.10).
4. **Freeze mutates no evidence.** Running design + freeze over a corpus leaves `file_facts`,
   `values` and accepted-group records unchanged, byte for byte (§3.14, §5.12).
5. **Every node carries a non-empty `explanation`, and no canvas surface exposes a confidence
   score** (§5.12, §5.2).
6. **Existing folders survive.** No code path renames, flattens, re-parents or reorganises an
   `existing` node without an explicit user action recorded as such (§5.10).
7. **Uneven depth passes validation**; no rule requires sibling parity (§5.8).
8. **A valid template is inert until approved** — the accept path requires a recorded user action
   (§5.7).
9. **Every §5.9 warning fires from published data** (child count, parent-concept repetition, depth,
   folder-size distribution), with thresholds read from configuration rather than hard-coded — the
   values themselves being an open question.
10. **P2 can replay a tree version and score tree quality and template quality** from the emitted
    user-action log (§8.5).
11. **No published node carries a filesystem path** other than `existing_path` on an `existing`
    node. A grep over a serialised frozen tree finds no separator-composed destination string;
    P12 composes every path from `root_anchor` + the `display_label` chain (§8.3, resolution B3).
12. **A disabled residual template is unreachable.** Given a tree where a residual template was
    not enabled, no node exists for it, so no placement decision can name it and no model can
    return it (§7.4). Conversely, an enabled residual node satisfies `accepts_placement = true`
    through the ordinary derivation — P11 needs no residual-specific legality path.
13. **C1–C8 are independently falsifiable.** One failing fixture per composition gate creates an
    explained validation report and no nodes; C2/C5 do not replace any V1–V6 check.
14. **Many-to-many reuse is real and schema-safe.** One definition serves two domains through two
    exact one-schema applicability rows; one domain offers two definitions; neither case duplicates a
    definition or widens a P6 allow-list.
15. **Purpose composition preserves heterogeneity.** A mixed-domain purpose packet composes exact
    applicability/fragment versions, preserves every member, and binds an authored/versioned purpose
    profile to actual accepted P9 group IDs through C3. It neither invents a purpose taxonomy nor
    unions schema allow-lists.
16. **Branch choices are isolated and immutable.** Applying/editing a shared recipe in one branch
    changes no sibling. New template, fragment, or applicability versions never migrate an approved
    binding; adoption requires a new draft and explicit approval.
17. **A partial-depth design can be complete.** The user can freeze a legal top-level scaffold with
    one `refined`, one `shallow-by-choice`, and one `refine-later` branch, each with a reason. Later
    refinement creates a new plan version, while facts, groups, and the earlier freeze remain intact.

## Cross-cutting answers

### Provenance (§8.2)

**Events P10 appends** — §8.2's literal list contains two that are P10's: `template application` and
`destination-tree edit`. Every canvas action that alters the draft tree appends a
`destination-tree edit` event: accept, rename, merge, split, nest, re-parent, reorder, ignore, delete,
create-manually, adopt-existing, enable/disable residual branch, add scoped `General`, set
shared-material policy. Each carries the acting user, time, node ID, before/after node state, and the
evidence reference or user intent behind it (§8.2's required event fields). Applying or changing a
template on a branch appends `template application`, carrying template ID and version. An
LLM-generated template additionally carries the model version and prompt fingerprint (§8.2, §3.4).
Freeze appends a plan-version adoption record (§8.8); §8.2's per-file events are unaffected because
freeze touches no file.

**What P10 never overwrites**: facts, values, evidence, and accepted-group records — the tree is a
separate view over them (§3.14, §5.12). A superseding edit retains its predecessor: §8.2 requires that
"a newer result should supersede an earlier result while retaining the old observation and the reason
it was superseded," so a renamed branch keeps its prior label and the rename's reason, and a rejected
branch candidate keeps the evidence that produced it (§8.7). Frozen plan versions are never mutated;
edits create a new draft (§8.8).

### Budgets and degradation (§8.6)

**Ceilings P10 owns** — §8.6's configurable list contains one that is P10's outright:
`Maximum folder proposals and maximum depth`. Custom-template generation additionally consumes the
shared model ceilings — `Maximum LLM calls per thousand files`, `Maximum model cost per scan`,
`Maximum dossier tokens per model call` — enforced by P8. Live structural feedback (§5.9) and tree
health (§5.11) are computed from local facts and are cheap by construction; they involve no model call.
Numeric values are configuration, not contract (Open questions).

**On exhaustion.** §8.6: "If the budget is exhausted, the product should retain extracted evidence,
mark the deferred stage, and leave the file or group in review rather than guessing … **Cost exhaustion
must never turn into lower-quality automatic classification.**" For P10 specifically:

- Custom-template budget exhausted → **no template is generated**. The branch is marked
  `template-deferred` and stays in review. The user may still hand-author the branch or apply a
  built-in template. The system does not substitute a cheaper auto-generated structure.
- Proposal or depth ceiling reached → surplus candidates are shown as deferred, not silently dropped.
  §8.6 requires the interface to "show the difference between completed work and deferred work" so an
  unprocessed item is never mistaken for one judged unimportant.
- **Freeze is never auto-completed.** Freeze requires an explicit user action under every budget
  condition (§5.12: "When the user is satisfied, they freeze the tree"). A partially designed tree may
  be frozen — §5.11 allows a branch to be accepted with files still unresolved — but only because the
  user chose to, never because a budget ran out.
- A dossier that exceeds its token budget is handled per §8.6: summarise deterministic facts, preserve
  anchor excerpts, split the task, or defer — never silent truncation.

### Correction learning (§8.7)

**Actions P10 records** — §8.7's list names five that occur in this stage: "renaming a branch, merging
or splitting groups, changing template order, creating a custom template, choosing a shallow fallback."
P10 additionally records: accepting/deferring/deleting a branch candidate, adopting or ignoring an
existing folder, re-parenting a group, enabling/disabling/relocating a residual branch, adding a scoped
`General`, and flattening a dimension against the recommendation.

**Scope is explicit on every record** — one of file / group / node / template / domain / corpus (§8.7).
The stage's characteristic scopes:

| Action | Typical scope | § |
|---|---|---|
| Rename a branch | node (and an alias at corpus scope if the user renames the vocabulary itself) | §8.7, §8.8 |
| Change template order / flatten a dimension | template, or domain if repeated | §8.7 |
| Adopt an existing folder over a proposal | node | §5.10, §8.7 |
| Reject a branch candidate | node, with the evidence that produced it | §8.7, §4.9 |
| Repeatedly prefer subject-before-time (or the reverse) | domain or corpus | §8.7, §5.5 |

**Negative feedback is stored, not discarded.** §8.7: "Rejected groups, rejected destination matches,
rejected labels, and rejected residual recommendations must be stored with the evidence that produced
them. Otherwise the system will repeatedly resurface the same attractive but incorrect grouping." A
deleted branch candidate must not reappear on the next pass. **Before proposing a branch candidate,
P10 queries P1 `learning_records`** for `proposal_class = branch` and
`basis_key = (parent_node_id, dimension_or_label)`; a matching unresected reject omits the candidate
from the canvas ([`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md)). Learned preferences
are inspectable and resettable (§8.7), and nothing here trains a global model (§8.7).

### Plan versioning (§8.8)

**Belongs to the plan version** (§8.8's list, P10's rows): the destination tree and its node
identifiers; the existing/proposed/user-created classification of every node; template versions and
ordering choices; user labels and aliases; the residual-library configuration — definitions **and**
enablement choices, both P10's (M10, O11); and the two tree-level policies P10 records — shared
material (§6.9) and cross-root movement (§1.1).

**Belongs to the shared evidence database, not the plan version**: files, evidence, fields, values,
file_facts, and accepted-group evidence. §8.8: "The evidence database remains shared across plan
versions, but the destination tree and user policy define which projections are valid in each version."
§5.12 states the same guarantee from the user's side — changing the view must not destroy the evidence.

**Behaviour**: a frozen version is immutable; an edit opens a draft; the draft is comparable to its
predecessor by the node-level diff (§8.8); the user may restore an earlier draft or explicitly adopt
the new plan; adoption never silently reclassifies or moves old files — it produces new placement
recommendations subject to review (§8.8). Branch bindings pin exact `{template_id,
template_version}`, every `{fragment_id, fragment_version}`, and every `{applicability_id,
applicability_version}` so no library update can retroactively alter a frozen tree (§8.8: "Template
versions and ordering choices").

## Open questions

**Closed by 04-resolutions and recorded here, not repeated below:** who owns the residual-library
configuration in the plan version (O11 → P10) and who owns the residual template definitions
(O12 → P10, via M10's move); who owns the §6.1 destination profile (B4 → P10); who resolves a node
to a filesystem path (B3 → P12); who computes curated-versus-incidental (G9 → P3, was OQ6); and
whether Code and Finance ship template dimensions at launch (S3 → deferred, was OQ7).

**Closed by 05-minor-resolutions:** whether the user may create a folder after freeze (yes — as a tree
edit producing a new plan version; was OQ4, struck through below); and who runs §5.7's six
template-validation checks (P8's former Q9 → **P10**, stated under
[Contract out §3](#3-the-template-schema-54-57)).

1. **Depth limit.** §5.7 forbids exceeding "practical depth limits" and §8.6 lists "Maximum folder
   proposals and maximum depth" as configurable, but no value is given. Check V3 cannot be implemented
   until it is set.
2. **§5.9 thresholds.** What count of children constitutes "a large number of tiny folders," what depth
   is "excessive," and what test decides that a dimension does not "materially improve retrieval."
   Unstated by design; the warnings cannot fire without them.
3. **Is `protected` a node type or an orthogonal flag?** §5.12 lists it inside a single enum with
   `existing` / `proposed` / `user-created` / `ignored`, but a protected branch is also one of those
   three. §8.4 treats sensitivity as an evidence-backed, user-revisable per-file class. This spec
   carries the §5.12 enum literally **and** a separate `handling_class` so P11 can key off sensitivity
   either way — but the intended relationship should be settled. **Affects P11 directly.**
4. ~~**May the user add a node after freeze, and does that re-freeze?**~~ **Settled by
   05-minor-resolutions: yes — as a tree edit routed to P10, producing a new plan version.** §8.8
   already answers it ("When the user edits the tree, the product should create a draft plan version
   and show a meaningful diff"), and §5.12/§6.12 are not violated because the *user* editing the tree
   is not the *system* inventing a destination. The frozen version itself is never amended in place.
   Recorded under [Contract out §4](#4-the-freeze-record-512-88); P11 had already stated the same
   reading.
5. **Node identity across plan versions.** §8.8 requires diffs and restorable earlier drafts. Is a
   `node_id` stable across versions (so a rename is one node with two labels) or minted per version
   with a mapping? §8.3's plan precondition stores a "Requested destination node," so the answer
   determines whether a pending move survives a tree edit. **Affects P11 and P12.**
6. ~~**Who computes curated-versus-incidental for existing folders?**~~ **Settled by resolution
   G9: P3 computes it**, as an observation over the directory inventory it already publishes. P10
   renders the signal and does not derive it. Recorded in [Contract in — From P3](#from-p3--corpus-and-existing-structure-11-12).
7. ~~**Code and Finance templates at launch.**~~ **Settled by scope decision S3: deferred.** §3.11's
   Career/recruiting fact schema and the §5.4 Code and Finance template dimensions are a hole in the
   design, not a spec defect — Joseph authors them when those parts come up. P10 ships the schema
   they must conform to and authors none of them.
8. **Is the scoped `General` branch auto-proposed or opt-in per parent?** §5.9 requires support for it
   and forbids a global catch-all default, but does not say whether the canvas offers one under every
   meaningful parent by default or only on request.
9. **Is the shared-material policy (§6.9) tree-global or per-branch?** §6.9 says "the user's frozen tree
   should therefore include a policy," which reads global, but its example — `Applications/Shared
   Application Materials` — is branch-local. **Affects P11's abstention behaviour.**
10. **Default redaction settings for protected branches.** §5.2 fixes the filename default (do not show,
    do not send to cloud). §8.4 makes names, previews, thumbnails, OCR text and location data
    configurable but sets no defaults for the other four.
11. ~~**Are personal saved templates (§5.7) plan-versioned or library-scoped?**~~ **Settled by the
    2026-08-26 composable-template clarification:** a published personal `TemplateDefinition`, its
    fragments, and applicability rows are immutable library-release records shared across plans; the
    exact branch binding and ordering choices are plan-versioned. Saving a draft definition does not
    activate it, and publishing a newer record does not migrate a prior binding.

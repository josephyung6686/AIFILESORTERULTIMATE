# P11 — Placement and residual

Owns: §6 except §6.1 (P10), §7 except §7.2–§7.4 (P10)
Status: contract draft

## Purpose

P11 decides, for every file and every accepted group, **which approved destination node it belongs
to — or that it belongs to none**. It is the only part that reads the frozen tree as a closed set of
legal destinations (§6) and the only part that runs the residual workflow for what the main pass
could not place (§7.5–§7.11). The residual *library* those branches come from is P10's (§7.2–§7.4,
resolution M10), as is the §6.1 destination profile (resolution B4).

§6 and §7 are one part because §7.9 requires that when residual review finds a credible connection
to an accepted project, course, application, photo event, or career group, **the file is returned to
the standard node-aware placement engine rather than being trapped in a generic residual folder**.
That is a loop back into §6, not a hand-off out of it. Both paths must also present one review
surface, so both emit **one record shape** — the placement decision record (§6.11), specified in
[Contract out](#contract-out). Publishing that single shape is this part's primary obligation.

P11 moves nothing. It emits decisions; P12 turns accepted decisions into filesystem transactions
(§8.3).

Three prohibitions govern everything below, all literal (§6.12):

> No system component may invent a new destination after freeze, silently override a direct fact, or
> move an uncertain file simply because it resembles an existing folder.

And one success redefinition (§6.10): **correct abstention is a successful outcome**, because the
goal is reliable organization, not maximum file movement.

---

## Design slice owned

### §6 — Group-aware classification against the frozen destination tree

| § | Obligation |
|---|---|
| §6.2 | A **destination-node retrieval index** built after freeze over P10's §6.1 profiles; retrieval returns only approved nodes; inventing `Math Stuff` for a mathematical-looking file is forbidden |
| §6.3 | Retrieval driven by direct facts, accepted group membership, graph relationships, structural relationships, full-text/OCR embeddings, and existing curated folders and user labels; **conflicting evidence actively suppresses nodes** |
| §6.4 | **Node-local evidence graph** per file/group — compare the target against the node's approved community, not against a folder name |
| §6.5 | Local clustering only; never whole-corpus reclustering; typed relationships; **a semantic embedding alone is insufficient**; a file connected only by generic similarity or one high-frequency entity stays uncertain |
| §6.6 | The LLM as **hierarchical destination judge** — never called for direct unique matches; receives a bounded placement dossier, never the whole tree |
| §6.7 | Reason broad→narrow; prefer an approved **shallower** path or an approved scoped `General` fallback over inventing a level; **never fill a missing slot because a complete-looking path is aesthetically preferable** |
| §6.8 | **Group-level placement is first-class**: confirm the shared parent, then classify members, and show it as **one coherent group plan** with outliers excluded and explained |
| §6.9 | **Multi-home files**: shared branch / primary-home / alias convention / mandatory review; with no shared branch, abstain or ask — **never arbitrarily pick one institution** |
| §6.10 | The **two-condition acceptance rule** and correct abstention as success |
| §6.11 | The **structured placement decision record** |
| §6.12 | The nine-step post-tree pipeline (reproduced under [Done means](#done-means)) |

### §7 — Residual files, controlled miscellaneous templates, final review

| § | Obligation |
|---|---|
| §7.1 | Residual is a **separate stage that runs only after** normal group-aware classification has been attempted; no global `Misc`/`Other`/`Unsorted` folder |
| §7.5 | The **residual surfacing screen** — a visible summary divided into understandable review sets, not an automatic cleanup |
| §7.6 | **Set-level decisions before any per-file model review** |
| §7.7 | The **eight-action controlled action set** (reproduced verbatim below) |
| §7.8 | Worked examples: the Columbia-submission screenshot returns to §6; the `Gate B12` screenshot must not produce `Travel/Flight Gate B12` |
| §7.9 | Residual validation, and **the loop back to §6** |
| §7.10 | Editable recommendations, **bulk decisions**, learned preferences, **negative examples** |
| §7.11 | **Non-destructive time-aware lifecycle** — never delete, never auto-expire |
| §7.12 | Residual completes the philosophy: exceptions must not pollute the main tree |

**§7.2–§7.4 are P10's, not P11's** (resolution M10). The residual library's *definitions* — the nine
template names, the eight attribute slots each defines, and the enable / disable / rename / relocate
/ merge / replace-with-existing model with its three dispositions — moved to P10, because §7.4 makes
an approved residual branch **a legal node in the frozen destination tree**. A part that cannot
freeze a complete tree without the library must own the library; holding it here made P10 depend on
the part that consumes P10's own output, which was a genuine cycle rather than an ordering
preference. P11 retains the residual **workflow**: §7.1's ordering guarantee, §7.5's surfacing
screen, §7.6's set-level decisions, §7.7's eight-action review, §7.8's worked examples, §7.9's
validation and loop back to §6, §7.10's editable and bulk decisions, §7.11's non-destructive
lifecycle, and §7.12.

What P11 consumes instead is the *frozen result* of those definitions: an enabled residual branch
arrives as an ordinary node carrying `node_role = residual`, its residual-template identity, and its
`disposition` — see [Contract in — From P10](#from-p10--the-frozen-tree-512-61-74). A residual
template the user did not enable has **no node**, so the §7.7 model cannot name it. P11 therefore
needs no residual-specific legality path and holds no template definitions of its own.

**The eight §7.7 actions**, verbatim. The model receives a residual dossier and is asked to choose
from a controlled action set:

1. return the file to a confirmed domain group;
2. return it to an accepted graph or purpose packet;
3. choose one approved residual destination;
4. choose an approved broad parent branch;
5. mark it for Review Later;
6. leave it in its current location;
7. mark it as protected or unsupported;
8. abstain.

There is no ninth action on the residual path. Every one of the eight is expressible in the single
record shape — the mapping is given in [Contract out](#contract-out).

### Explicitly not owned

| Not owned | Owner | Why the boundary sits here |
|---|---|---|
| The frozen tree, node types, the **§6.1 destination profile**, the **residual-library definitions** (§7.2–§7.4) and their enablement, shared-material policy selection | P10 (§5.12, §6.1, §7.2–§7.4) | P11 consumes an already-frozen tree; it never edits one. Every §6.1 profile ingredient is a value P10 holds at freeze (B4); every residual definition produces a node P10 freezes (M10). P11 owns only the §6.2 **index** built over the profiles |
| Dossier → cited response → validation **mechanism** | P8 (§3.3, §3.6, §4.8, §6.10, §7.9) | P11 supplies dossier *contents* and destination-specific *checks*; P8 owns the harness and verdict machinery. §6.10 and §7.9 are jointly cited by both specs — see [Open questions](#open-questions) |
| Accepted groups, anchor vs context-supported membership, group labels, outliers | P9 (§4) | P11 consumes memberships; it never re-groups |
| Facts, values, reliability states, gazetteers | P6 (§3) | |
| Handling classes, operation modes, consent audit record | P7 (§8.4) | |
| Path resolution, collision policy, filesystem-safe naming, the move, undo | P12 (§8.3) | P11 names a **node**; P12 resolves the **path** |

---

## Contract in

### From P10 — the frozen tree (§5.12, §6.1, §7.4)

**Per node**, from P10's node record (§5.12):

| Field | Why P11 needs it | § |
|---|---|---|
| `node_id` | the only thing a `destination` may name | §5.12, §6.2 |
| `node_type` | existing / proposed / user-created / protected / ignored | §5.12 |
| `display_label`, `parent_node_id`, `root_anchor`, `ordinal` | ancestry, and the label chain P12 later composes into a path | §5.12, §8.3 |
| `associated_group_ids[]`, `template_context`, `dimension` | group and template context for retrieval | §5.12, §6.2 |
| `explanation` | the facts or groups that caused the node to appear | §5.12 |
| **`accepts_placement`** | the legality flag — see below | §5.12, §5.10, §8.4 |
| **`node_role`** | `ordinary` \| `scoped-general` \| `residual` \| `shared-material` | §5.9, §6.9, §7.4 |
| **`disposition`** | on `residual` nodes: `physical-destination` \| `review-only` \| `leave-in-place` | §7.4 |
| **`expected_values[]`** | the `field = value` assertions a node makes, matched against `matching_facts` | §6.1, §6.3 |
| **`handling_class`** | carried from P7 through P10; P11 never re-classifies sensitivity | §8.4 |

The five fields in bold are the ones resolution **B6** adds. `accepts_placement` matters most:
it is the single field P10 built to stop P11 placing into an `ignored` node — §5.10's guarantee that
a user may leave an existing folder untouched — and it carries §8.4's protected-node rule, under
which a `protected` node accepts automatic movement only where an explicit user policy permits it.
**Node existence is not legality.** The legal set is exactly
`{node_id : plan_version = frozen version, accepts_placement = true}`; a node that exists with
`accepts_placement = false` is visible context, never a destination. Validating a destination is an
ID membership test against that set (§6.10).

**The §6.1 destination profile, per node** (resolution B4). P10 emits the profile; P11 does not build
one. It arrives with the branch's domain, template, expected field values, parent and child meanings,
accepted group memberships, user-selected label, known exclusions, representative files, rich anchor
files with their `observation_key` citations, and any privacy or policy restrictions (§6.1), plus
§6.2's anchor excerpts, known document types, parent and child context, and explicit user edits.
P11's own artefact is the **retrieval index built over these profiles** (§6.2) — see
[Contract out §2](#2-the-retrieval-index-entry-62).

**Residual nodes** the user enabled during tree design arrive as ordinary nodes additionally carrying
their residual-template identity and their `disposition` (§7.4). A `review-only` or `leave-in-place`
residual node is still a legal destination for a *decision*; what differs is that no filesystem
mutation follows. P11 receives no residual template **definitions** — those are P10's (M10).

The tree must also carry the **shared-material policy** (§6.9): shared branch, primary-home
convention, reference or alias convention, or mandatory review.

**No filesystem paths arrive from P10** (resolution B3), other than `existing_path` on an `existing`
node. P11 names a node; P12 composes and normalizes the path from `root_anchor` plus the ancestor
`display_label` chain, under §8.3's case-sensitivity, Unicode-normalization, reserved-name and
length rules.

Freeze is a precondition. P11 does not start until a frozen tree exists at a known plan version
(§5.12, §8.8).

### From P9 — accepted groups (§4)

Group id, label, category, member files each with P9's `Membership.basis` — **all three** kinds,
`direct-anchor`, `context-supported` and `user-attached` (§4.3, §4.8, §4.9) — identified outliers,
and recorded conflicts.

**The third kind is not optional** (resolution M12). `user-attached` is §4.9's manual
attachment: *"Unreadable, encrypted, corrupted, or unsupported files should retain basic metadata and
remain eligible for manual attachment to a user-created group."* P9 invariant 5 makes it the **only**
basis such a file may receive, and those files reach §6.8 group placement, so a record that could
express two kinds would have to record them as `context-supported` — routing an unreadable file to
review as though evidence existed. Two constraints follow, and P11 enforces both:

- a `user-attached` member never yields `evidence_type = validated`, because nothing was read from
  the file to validate;
- a decision resting on a `user-attached` membership is never `review_policy = auto_eligible`.

This is the placement-layer half of P10's constraint that a `user-attached` member must not be
presented as evidence-derived (§5.12, §5.2).

### From P6 — facts (§3.12, §3.13)

`file_facts` rows joining file → field → value, each with its reliability state (user-confirmed /
direct / validated / LLM-supported / possible / rejected) and its evidence reference.

### From P4/P5 — observations (§2.8)

Observation records used as citable excerpts (extracted text, OCR regions, metadata fields) in
dossiers and in the record's citations. P11 never re-extracts.

**P11 cites `observation_key`, not `observation_id`** (resolution M14). P4 publishes both:
`observation_id` is a per-row uuid that dies when an extractor is upgraded and the row is re-emitted;
`observation_key` is content-addressed (`sha256(content_hash ‖ extractor_name ‖ locator ‖
raw_value)`) and is deliberately version-independent. §8.7 requires that a rejected destination match
recorded today still resolve to its evidence afterwards — otherwise every stored negative example
decays and the same attractive-but-wrong destination is resurfaced, which is the exact failure §8.7
exists to prevent. Only the key satisfies that. Every `evidence_ref` in the placement decision record
is an `observation_key`.

**Surrounding context arrives as three fields, not one** (resolution M5). §2.8's single "surrounding
context" line is split by P4 into `context_before`, `context_after` and `context_truncated`. P11
reproduces P4's three, not §2.8's one. The split is load-bearing rather than cosmetic: §8.4 must be
able to redact a value while keeping the context that justified it, which a single concatenated
string cannot express.

### From P7 — privacy gate (§8.4)

Per-file handling class, the active operation mode, and consent state. **The gate is passed before
any dossier is assembled for a model**, not after (§8.4). Protected material must not be included in
cloud-model prompts by default and must not appear as raw content in group summaries.

### From P8 — the harness (§3.6, §4.8, §6.10, §7.9)

The dossier submission interface, the cited-response shape, and the validation verdict. P11 supplies
two dossier types (contents below) and the destination-specific checks; P8 returns the verdict that
populates `two_condition` and gates `review_policy`.

**Placement dossier contents** (§6.6, literal): the target file's direct and validated facts,
relevant extracted excerpts or OCR, accepted group memberships, graph anchor evidence, the small set
of top legal destination candidates, each candidate's node profile, representative files already
accepted in those nodes, known conflicts, missing fields, and deterministic scores. It does **not**
contain the whole folder tree or a free-form request to organize the file.

**Residual dossier contents** (§7.7, literal): filename, file type, creation date, extracted text or
OCR, metadata, sensitivity state, any weak graph relationships, the user-approved residual library,
existing relevant folders, representative examples from approved residual destinations, and the
user's residual-placement policy.

### From P1 and P2

P1: file identity by content hash, path history, and the append-only event log (§8.2). P2: the
replay-bundle interface into which P11's stage assertions are registered (§8.5).

### From P13 — collected placement and residual review actions (§6.11, §7.10)

P13's `review_action` in full, collected on `surface = placement | group_plan | residual_set |
residual_file` with `subject_ref` a `decision_id`, `group_plan_id` or `set_id`, and carrying
`plan_version`, `action`, `bulk_member_refs[]`, `bulk_basis`, `correction_scope` (§8.7) and
`presented_state_ref`. **All eight §7.7 actions arrive on this record**, and §7.10's bulk decisions
arrive as `action = accept_bulk` with every member enumerated. P13 presents and collects; it decides
nothing. **P11 authors the placement or residual decision each action produces** (M8) and P1 writes
the event.

---

## Contract out

**Emits P2 `stage_output` for the two §8.5 stages P11 owns** (§8.5, resolution B7) — one per subject
it decides about:

| `stage_id` | §8.5 name | P11's subject |
|---|---|---|
| `candidate_node_retrieval` | candidate-node retrieval (§6.2) | the file or group a candidate set was retrieved for |
| `placement_scoring` | placement scoring (§6.10) | the file or group a placement decision was scored for |

Both values are drawn from P2's **closed** ten-value enumeration and P11 emits no other. `P11` is not
a `stage_id`; a part name in that field would leave two of §8.5's ten stages with no producer and
P2's `attributed_stage` unable to name where a placement error began. Each envelope carries
`inputs[]` — the `subject_ref`s of the `grouping`, `tree_design` and `factual_validation` stage
outputs it consumed — an explicit abstention value, a distinct budget-deferral value, and the version
tuple.

**The envelope's vocabulary is P2's; the record's vocabulary is P11's, and they are different
vocabularies.** P2 owns `outcome ∈ produced | abstained | deferred | not_implemented | error` and
`budget_state ∈ within_ceiling | ceiling_reached`. `place`, `abstain`, `deferred_stage` and
`abstention_reason = budget_deferred` are values of **`placement_decision`**, this part's own record
(Contract out §1) — none of them is an envelope value, and none may be written into `stage_output`.
The mapping between them is:

| P11 result | `outcome` | `budget_state` |
|---|---|---|
| a candidate set was retrieved, or a decision record was written with any `outcome` other than `abstain` | `produced` | `within_ceiling` |
| retrieval returned no legal candidate, or the record carries `outcome = abstain` with a **non-budget** `abstention_reason` (`no_supported_destination`, `low_margin`, `semantic_only`, `generic_hub_only`, `conflicting_facts`, `no_shared_branch`, `privacy_blocked`) | `abstained` | `within_ceiling` |
| an §8.6 ceiling stopped the work — the record carries `abstention_reason = budget_deferred` with `deferred_stage` set | `deferred` | `ceiling_reached` |
| the stage failed | `error` | — |
| P11 not built yet | `not_implemented` | — |

The third row is the one that must not collapse into the second. A budget deferral is `deferred` with
`ceiling_reached` and is **never** `abstained`, even though both are carried on a record whose own
`outcome` reads `abstain`: scored as `abstained`, P2 would grade a ceiling-truncated run
`abstained_correctly` or `abstained_incorrectly` — a judgement about evidence — when no judgement was
made. P2 Done-means 6 depends on the distinction: `deferred` is reported separately from `divergent`
for every dimension, so a run whose only change is a lower budget ceiling produces zero new
divergences. It is the same separation §8.6 demands of the interface — *cost exhaustion must never
turn into lower-quality automatic classification* — asserted one layer up, in P2's words rather than
P11's.

### 1. The placement decision record — one shape, both paths

§6.11 is literal that the output is *not simply a path string*. The record below is that structure.
Field names are contract names; every field traces to a §. The same shape is emitted by the §6
placement pass and by the §7 residual pass — a consumer parses residual decisions with **no
residual-specific branch**.

```text
placement_decision
  decision_id
  plan_version                  the plan version this decision is valid in        §8.8
  supersedes                    prior decision_id, or null — never overwritten    §8.2
  superseded_by                 inverse link: the decision_id that replaced this
                                one, or null — the old row stays readable         §8.2, M1
  supersede_reason              why it was superseded, on the superseded row      §8.2, M1
  created_at
  origin_stage                  placement | residual                              §6 / §7
  returned_from                 decision_id of the residual decision that
                                handed this file back, or null                    §7.9

  subject
    kind                        file | group                                      §6.11, §6.8
    file_id, content_hash                                                         §8.2
    group_id, member_file_ids                                                     §6.8, §4
  group_plan_id                 shared by all members of one group plan, or null  §6.8

  outcome                       place | return_to_placement | mark_review_later
                                | leave_in_place | mark_state | ask_user
                                | abstain                                         §7.7, §6.7, §6.9, §6.10
  destination                   present only when outcome = place
    node_id                     a node in the frozen tree — never a path string   §5.12, §6.2
    node_role                   ordinary | scoped-general | residual
                                | shared-material — P10's vocabulary, carried
                                verbatim from the node, never re-derived          §5.9, §6.9, §7.4
  return_target                 present only when outcome = return_to_placement
    kind                        confirmed_domain_group
                                | accepted_graph_or_purpose_packet                §7.7
    id                                                                            §7.9
  marked_state                  protected | unsupported | null                    §7.7, §7.3
  ask                           { question, options[] } | null                    §6.9

  decision_depth                                                                  §6.11, §6.7
    node_depth                  depth of the chosen node
    supported_depth             deepest level the evidence actually supports
    unsupported_levels[]        levels deliberately not filled
  evidence_type                 user-confirmed | direct | validated
                                | llm-supported | context-supported | possible    §6.11, §3.13
  confidence_class              exact fact match
                                | context-supported group match
                                | shared-material decision
                                | abstain: no supported destination               §6.11

  matching_facts[]              { file_fact_id, field, value,
                                  reliability, evidence_ref }                     §6.11, §3.12
  group_support                 { group_id,
                                  membership: direct-anchor
                                            | context-supported
                                            | user-attached }                     §6.11, §4.3, §4.8, §4.9
  graph_anchors[]               { edge_type, from, to, anchor_file_id }           §6.11, §6.5
  conflicts_considered[]        { kind, conflicting_value,
                                  suppressed_node_ids[], evidence_ref }           §6.11, §6.3
  alternatives[]                { node_id, support_score, rank }                  §6.11

  two_condition                                                                   §6.10
    support_score, support_threshold, meets_threshold
    margin_over_next             null when only one legal candidate exists        §6.10, B8(b)
    margin_threshold
    meets_margin                 true | true_vacuous | false — `true_vacuous`
                                 marks an unopposed candidate, never a
                                 measured margin                                  §6.10, B8(b)
    verdict                     accept_direct | accept_context_supported
                                | weak | reject | abstain — P8's outcome
                                vocabulary, carried unchanged                     §6.10, §4.8, MINOR 7
    requires_review             true on every accept_context_supported            §6.10, §4.8
  abstention_reason             no_supported_destination | low_margin
                                | semantic_only | generic_hub_only
                                | conflicting_facts | no_shared_branch
                                | budget_deferred | privacy_blocked | null        §6.10, §6.5, §6.3, §6.9, §8.6, §8.4
  deferred_stage                set when the decision was cut short by budget,
                                never by evidence — must render differently
                                from an evidential abstention                     §8.6

  privacy                                                                         §8.4
    handling_class
    model_eligibility           local_only | dossier_permitted | redacted
    consent_audit_ref
  review_policy                 auto_eligible | review_required
                                | blocked_pending_user                            §6.11, §8.4
  explanation                   human-readable; must state the actual basis and
                                must not claim evidence the file does not carry   §6.4, §6.11

  residual                      present only when origin_stage = residual
    set_id, set_decision                                                          §7.5, §7.6
    lifecycle_policy_ref        a review policy — never a deletion or expiry      §7.11
```

**How the §7.7 eight actions map into it.** No action needs a field the §6 path does not already
have; the eight collapse into the shared outcome vocabulary because two pairs differ only by a
qualifier:

| §7.7 action | `outcome` | qualifier |
|---|---|---|
| 1. return to a confirmed domain group | `return_to_placement` | `return_target.kind = confirmed_domain_group` |
| 2. return to an accepted graph or purpose packet | `return_to_placement` | `return_target.kind = accepted_graph_or_purpose_packet` |
| 3. choose one approved residual destination | `place` | `destination.node_role = residual` |
| 4. choose an approved broad parent branch | `place` | `destination.node_role = ordinary`, with the levels deliberately not filled listed in `decision_depth.unsupported_levels[]` (§6.7) |
| 5. mark it for Review Later | `mark_review_later` | whether this results in a move is the Review Later node's `disposition` (§7.4, set by P10), not this record's decision |
| 6. leave it in its current location | `leave_in_place` | — |
| 7. mark it as protected or unsupported | `mark_state` | `marked_state = protected \| unsupported` |
| 8. abstain | `abstain` | `abstention_reason` |

**How the §6 outcomes map into it.** Approved child node → `place`, `node_role = ordinary`, with
`decision_depth.unsupported_levels[]` empty; approved **broad parent** node → `place`,
`node_role = ordinary`, with the levels deliberately not filled listed in
`decision_depth.unsupported_levels[]` (§6.7); approved scoped fallback such as `General` → `place`,
`node_role = scoped-general` (§6.7, §5.9); an approved shared branch → `place`,
`node_role = shared-material` (§6.9); no destination at all → `abstain` (§6.6, §6.10).

**Why there is no `destination.kind`** (MINOR 6). An earlier draft carried
`kind ∈ approved_child | approved_parent | scoped_fallback | approved_residual` alongside P10's
`node_role`. Two vocabularies for one concept is what MINOR 7 rules out — *"one vocabulary for one
concept"* — and P10 owns the tree, so `node_role` is the vocabulary and P11 carries it verbatim.
Nothing is lost. `scoped_fallback` and
`approved_residual` **are** `node_role` values (`scoped-general`, `residual`). The one genuinely
orthogonal thing the old field said — a fully supported child level versus a deliberately shallower
parent (§6.7) — is already published, and published more precisely, by `decision_depth`: an empty
`unsupported_levels[]` is the child case, a non-empty one is the broad-parent case and names which
levels were not filled. And `node_role = shared-material` now gives §6.9's shared branch a structural
expression, which the record previously had only as a confidence label.

**`confidence_class` is unchanged.** Its four values are §6.11's own literal examples — `exact fact
match`, `context-supported group match`, `shared-material decision`, `abstain: no supported
destination` — and remain the labels the review interface shows, because §6.11 requires the user to
see them. `node_role` says which kind of node was chosen; `confidence_class` says how much trust the
placement demands. Two questions, both required; `node_role` relieves `confidence_class` of carrying
the shared-branch fact, it does not replace it.

**`evidence_type` is P11's own vocabulary and deliberately diverges from §3.13.** §6.11 requires the
record to carry "the evidence type" and enumerates no values, so P11 defines the six above; the
§3.13 citation beside the field marks where five of them come from, not a list §3.13 contains. Two
divergences, both intentional. §3.13's `rejected` is **dropped**: a rejected fact cannot support a
placement, so a record resting on one would be a contradiction rather than a low-confidence
decision — the correct expression is `outcome = abstain`. And `context-supported` is **added**: it
is §4.8's membership basis rather than a reliability state, and a placement justified by group
membership rather than by a fact on the file itself has no §3.13 value that says so. Stated here so
the divergence is a declared choice rather than a mis-citation.

`ask_user` is emitted **only** on the placement path, and only under §6.9 — a multi-home file with
no shared branch, where the design permits abstaining *or* asking the user to choose a primary home.
The residual path is closed to the eight actions above.

`return_to_placement` is emitted **only** on the residual path, because §6 *is* the placement
engine. This is the §7.9 loop: the residual decision records the credible connection it found and
hands the file back; the placement pass then emits a second record whose `returned_from` points at
the first. Both records persist (§8.2) — the residual finding is never discarded because placement
later succeeded.

**The two-condition rule with exactly one legal candidate** (resolution B8(b)). §6.10 requires the
best legal destination to reach a minimum support threshold **and** exceed the next-best by a
meaningful margin. Where the frozen tree offers only one legal candidate — the whole tree contains
one placeable node, or conflict suppression (§6.3) and `accepts_placement` have reduced the
candidate set to one — there is no next-best and `margin_over_next` has no value to hold. The rule
in that case is:

> **The margin condition is satisfied vacuously. The minimum-support threshold remains binding and
> is the sole gate.**

On such a record `margin_over_next` is null, `margin_threshold` is recorded unchanged, and
`meets_margin` is `true` **by vacuity, not by measurement** — the two must be distinguishable in the
record, so a reviewer and a P2 replay can tell a genuine margin from an unopposed one. `verdict` is
then decided by `meets_threshold` alone.

**The verdict vocabulary is P8's** (MINOR 7). An earlier draft used `accept | review | unresolved`,
whose middle value had no counterpart anywhere in P8's verdict record. P8's representation is adopted
unchanged: `accept` → `accept_direct`; `review` → **`accept_context_supported` with
`requires_review: true`**, which is how §4.8 ("records it as a context-supported membership and sends
it to user review") and §6.10 ("may be valid but still require review") are already expressed
everywhere else in the system; `unresolved` → `weak`, which is exactly what P8's site-C column calls a
low-margin, weak-retrieval or generic-hub match. `reject` and `abstain` complete the vocabulary and
pair with `outcome = abstain` plus a named `abstention_reason` on this record. `requires_review` is
what gates `review_policy`: a decision whose verdict is `accept_context_supported` is never
`auto_eligible`.

A deterministic exact-fact match (§6.6) issues no model call and still records a verdict in this
vocabulary. The vocabulary describes the result of §6.10's two-condition gate, not the involvement of
a model.

This does **not** weaken §6.10. A file that clears no support threshold **abstains even when only
one destination exists**, with `abstention_reason = no_supported_destination`. The scarcity of
destinations is not evidence about the file, and a tree with one branch must not become a funnel
that everything falls into. §6.10's own hierarchy is unchanged: a match based only on weak
retrieval, a generic hub, or a low-margin comparison stays unresolved, and correct abstention is a
successful outcome.

The degenerate case is not hypothetical — it is the walking skeleton's own shape, which is why
B8(b) additionally gives the skeleton a **second** frozen node, so the margin path is genuinely
exercised rather than bypassed.

### 2. The retrieval index entry (§6.2)

**The §6.1 destination profile is not P11's** (resolution B4). P10 emits it; P11 receives it (see
[Contract in — From P10](#from-p10--the-frozen-tree-512-61-74)) and builds the index over it. The
boundary is that §6.2's index is a *placement mechanism* while §6.1's profile is a *description of
what the user approved at freeze* — every ingredient of which P10 already holds. P11 publishes no
profile table and holds no profiles in its plan-version state.

Index-entry fields, literal from §6.2: template fields, accepted group labels, user-approved display
name, representative member files, anchor excerpts, known document types, parent and child context,
and explicit user edits. Each entry keys to one `node_id` and is built only for nodes with
`accepts_placement = true` — an `ignored` node is never retrievable, so §5.10's guarantee holds at
the retrieval layer and not merely at the validation layer.

Retrieval returns approved nodes only. Conflicting evidence **suppresses** nodes and the suppression
is recorded in `conflicts_considered` so the review interface can show what was ruled out and why
(§6.3).

### 3. The group plan (§6.8)

```text
group_plan
  group_plan_id, plan_version
  group_id                          the accepted group being placed          §4
  shared_parent_node_id             confirmed first, from the group's
                                    anchors and purpose evidence             §6.8
  member_decisions[]                one placement_decision per member,
                                    all sharing this group_plan_id           §6.8
  excluded_outliers[]               { file_id, conflicting_fact,
                                      evidence_ref, routed_to:
                                        node_id | review_queue }             §6.8
```

Presented as **one coherent group plan**, not several unrelated file moves (§6.8).

### 4. The residual set (§7.5) and set decision (§7.6)

```text
residual_set
  set_id, plan_version, label, file_count
  representative_examples[]                                                  §7.5
  file_type_distribution, age_range                                          §7.5
  evidence_availability            OCR / text present or absent              §7.5
  sensitivity_status                                                         §7.5, §8.4
  weak_graph_neighbours[]                                                    §7.5
  reason_not_placed                why the normal pipeline could not
                                   safely place these files                  §7.5

residual_set_decision
  set_id, decided_at
  choice                           leave_in_place
                                   | review_with_model_against_approved_residual_folders
                                   | send_to_approved_node(node_id)
                                   | create_custom_branch → tree edit,
                                     routed to P10, new plan version         §7.6, §8.8
```

**Ordering is contractual**: no per-file residual model call may be issued for a set until that set
has a `residual_set_decision` (§7.6). A set the user chose to leave in place produces **zero** model
calls.

### 5. To P12 (§8.3)

**P12 consumes only `outcome = place`** (resolution M13). That is the whole filter, and it is keyed
on `outcome` — not on `confidence_class`, whose value `abstain: no supported destination` is a
*label on a record*, not the record's disposition. Every other outcome produces **no plan**:

| `outcome` | What P12 does | Why |
|---|---|---|
| `place` | builds a plan, once `review_policy` is satisfied | the only outcome naming a destination |
| `return_to_placement` | nothing — waits for the §6 record this hands back to | §7.9; the eventual placement record is the one that may become a plan |
| `mark_review_later` | nothing | whether a move follows is the Review Later node's `disposition`, expressed as a later `place` record |
| `leave_in_place` | nothing — the file does not move, by decision | §7.7 action 6 |
| `mark_state` | nothing — records `protected` or `unsupported` | §7.7 action 7 |
| `ask_user` | nothing — pending a user answer | §6.9 |
| `abstain` | nothing | §6.10: correct abstention is a successful outcome, not a deferred move |

Six outcomes, not five. Resolution M13's "five non-`place` outcomes" enumerates the five P12 had no
stated behaviour for; `abstain` was already refused, so it is the sixth and behaves identically —
no plan. Recorded here so the count does not read as a discrepancy later.

A `place` record whose `review_policy` is `review_required` or `blocked_pending_user` is **not** yet
a plan; P12 waits for the recorded approval. `deferred_stage` never becomes a plan under any
outcome — §8.6 forbids budget exhaustion turning into a move.

For a plan, P11 supplies `destination.node_id`, the subject's expected content hash, and the
reason-and-evidence summary. **P12 resolves the node to a filesystem path** (resolution B3),
composing it from P10's `root_anchor` and ancestor `display_label` chain and applying §8.3's
case-sensitivity, Unicode-normalization, reserved-name and path-length rules, plus collision policy
and the transaction. §8.3's plan record carries "Requested destination node" and "Resolved
destination path" as two separate fields; P11 supplies the first and never the second.
**P11 performs no filesystem mutation.**

### 6. To P2 (§8.5)

Two stage assertions, matching §8.5's literal metric names — *Placement quality*: did the engine
choose the correct frozen node, an appropriate shallow fallback, or abstain? *Residual quality*: did
the system avoid inventing associations for isolated files? A correct abstention **passes** both.

---

## Deferred — manual design required

Structure is specified here; contents are hand-authored later. Nothing below is invented.

| Deferred | Defined by | Note |
|---|---|---|
| The 200–300 domain template library | §5.7 | P10's surface, not P11's. P11 consumes whatever templates the frozen tree carries as node context |
| Domain fact-schema fields beyond §3.11's literal six-domain table | §3.11 | P6's. P11 reads `matching_facts` generically and must not hard-code field names |
| Gazetteer contents | §3.7 | P6's |
| The residual template library — nine names, eight attribute slots, their values, the enablement model, and the user-defined residual areas | §7.2, §7.3, §7.4 | **No longer P11's** (resolution M10). P10 owns the definitions and publishes them; what remains deferred there is the per-template slot *values* and the five default parent locations §7.3 leaves unstated. P11 consumes only the frozen nodes that result |
| The canonical partition of residual files into review sets | §7.5 | §7.5's eight-line example is prefaced "It may show" — illustrative counts, not a fixed taxonomy |
| Default lifecycle review policies | §7.11 | §7.11's examples ("older than 30 days", "every two weeks") are things *the user may define*, not defaults |
| Scoring functions behind `support_score` and `margin_over_next` | §6.6, §6.10 | The design names "deterministic scores" and a "minimum support threshold" without defining a scale — see [Open questions](#open-questions) |

---

## Done means

The nine-step §6.12 pipeline runs end to end, and each of the following is demonstrable against
fixtures without any other part being finished:

1. **One record, two paths.** A consumer built against the record shape parses §7-origin decisions
   with no residual-specific branch. All eight §7.7 actions round-trip through the mapping table;
   there is no ninth. (§6.11, §7.7)
2. **Destination invention is structurally impossible, and existence is not legality.** A record
   whose `destination.node_id` is unknown to the frozen tree fails validation — **and so does one
   naming a node whose `accepts_placement` is `false`** (resolution B6). Both tests run; passing the
   first is not sufficient. The concrete case §5.10 protects: a file that looks like it belongs in an
   existing folder the user marked `ignored` produces an abstention, never a placement. The §6.2
   test: a mathematical-looking file never produces a `Math Stuff` destination — it produces an
   approved node or an abstention. (§5.10, §5.12, §6.2, §7.4, §8.4)
3. **Index entries exist before matching.** P10's §6.1 profile is present for every frozen node,
   and P11 has built a §6.2 index entry over every profile whose node has `accepts_placement = true`,
   before the first file is placed. P11 builds no profile of its own (resolution B4).
4. **Conflicts suppress.** A file with direct `target institution = Duke` does not retrieve Columbia
   application branches as a top candidate; the suppression appears in `conflicts_considered`. A
   direct Spring 2025 term fact does not reach a Spring 2026 node without a user-approved reason.
   (§6.3)
5. **Node-local, not global.** Placement builds a node-local evidence graph with typed edges and
   never triggers whole-corpus reclustering or renumbering. A target connected only by generic
   similarity, or by one high-frequency entity, stays uncertain — a semantic embedding alone never
   produces a `place`. (§6.4, §6.5)
6. **The LLM is not called for direct unique matches.** A file whose validated facts uniquely match
   one frozen path is decided deterministically, with `confidence_class = exact fact match` and zero
   model calls. (§6.6)
7. **Shallow beats invented.** Given Spring 2025/Spring 2026 ambiguity and an approved shallower path,
   the record names the shallower node and `decision_depth.unsupported_levels` records the level that
   was deliberately not filled. Where only a deeper path exists that would require inventing a term,
   the outcome is a scoped `General` fallback under the meaningful parent, or abstention — never a
   filled slot. (§6.7)
8. **Group plans are coherent.** An accepted application packet produces one `group_plan` with the
   shared parent confirmed first and members classified beneath it; a conflicting-institution essay is
   excluded as an outlier with its conflicting fact recorded and is routed to a separate legal branch
   or the review queue. (§6.8)
9. **Multi-home is never arbitrary.** With a shared branch approved, it is retrieved and preferred.
   With no shared branch, the outcome is `abstain` or `ask_user` — never one institution chosen over
   another. (§6.9)
10. **The two-condition rule is recorded, not just applied.** Every record carries both conditions,
    their thresholds, and the verdict, so a reviewer can see *why* something was accepted, sent to
    review, or left unresolved. A weak-retrieval, generic-hub, or low-margin match is never
    `auto_eligible`. (§6.10)
10b. **The degenerate case does not become a funnel** (resolution B8(b)). Against a tree with exactly
    one legal candidate, a file whose support clears the threshold is placed with `margin_over_next`
    null and `meets_margin` recorded as vacuous; a file whose support does **not** clear the
    threshold abstains with `abstention_reason = no_supported_destination` — even though that one
    destination is the only one available. A fixture asserts both halves, because only the second
    proves the threshold stayed binding. (§6.10)
11. **Abstention is a pass.** P2's placement and residual assertions score a correct abstention as
    success, not as a miss. (§6.10, §8.5)
12. **Residual runs second.** No residual set is surfaced until the §6 pass has attempted normal
    classification for the corpus. No per-file residual model call precedes its set-level decision.
    (§7.1, §7.6)
13. **The §7.9 loop closes.** A screenshot whose OCR reads that a Columbia application has been
    submitted emits `return_to_placement`; the subsequent placement decision carries `returned_from`
    pointing at it; both records persist. The `Gate B12` screenshot produces an approved broad
    destination or leave-in-place — never `Travel/Flight Gate B12`. (§7.8, §7.9)
14. **Budget exhaustion is visibly different from abstention.** A decision cut short by budget sets
    `deferred_stage` and renders as deferred work, never as "understood and found unimportant".
    (§8.6)
15. **Nothing is destroyed.** The record shape cannot express deletion, expiry, or disposability;
    lifecycle policies are review triggers only. (§7.11)
16. **A new plan version never silently reclassifies.** When a plan version removes a node, decisions
    that named it are marked as requiring renewed review rather than being remapped. (§8.8)

---

## Cross-cutting answers

### Provenance (§8.2)

**Appends.** §8.2's literal event list already contains `placement recommendation`; P11 appends that
event plus the following, which are this part's specializations of it and of §8.2's "current and
historical placement proposals" and "current and historical user decisions":

- §6.2 retrieval index entry built for a node (after freeze) — the §6.1 profile it is built over is
  emitted by P10, which logs that (B4)
- candidate destination retrieval performed, with the retrieved and the suppressed node ids
- placement recommendation emitted (any `outcome`, including `abstain` — an abstention is a decision
  and is logged as one)
- group plan emitted
- residual set surfaced; residual set-level decision recorded
- residual recommendation emitted
- return-to-placement issued and the resulting placement decision linked
- user decision on a placement or residual recommendation (accept / change / defer / leave / mark
  private / bulk-accept)

Each event carries the §8.2 required fields: event type, file ID, content hash, responsible
subsystem, model version and prompt fingerprint where a model was used, user identity for explicit
user actions, observation time, and a structured explanation or evidence reference.

**Never overwrites.** A revised decision — from the §7.9 loop, a user correction, a new plan version,
or an improved extractor — is written as a **new** record whose `supersedes` names the prior one. The
prior record, its cited evidence, its alternatives, and its two-condition figures remain inspectable,
together with the reason it was superseded (§8.2). P11 never mutates a decision in place, and never
rewrites the evidence record because a later model answered differently. The link is carried by all
three of P1's shared columns, not by `supersedes` alone (M1): the newer record names its predecessor
in `supersedes`, and the superseded record carries `superseded_by` and `supersede_reason`. P1's rule
governs how — superseding *"leaves the old row readable"* and populates the reason — so no decision
content is rewritten, and the chain is followable **forward** as well as backward. That direction is
load-bearing: §8.8's *"twenty-three files now require renewed review because their previous
destination no longer exists"* diff and [Done means 16](#done-means) both walk from a superseded
decision to its replacement, which `supersedes` alone cannot express.

### Budgets and degradation (§8.6)

**Ceilings owned by P11**, from §8.6's literal list: maximum retrieved neighbors per target file;
maximum local graph neighborhood size; maximum candidate cluster size; maximum residual files in one
review batch; maximum dossier tokens per model call; maximum LLM calls per thousand files; maximum
model cost per scan. (Values are configurable and not fixed by the design.)

**Degradation order**, from §8.6: deterministic node matching runs first because it is cheap and
stable (§6.6). Graph retrieval activates only for files with meaningful incomplete evidence and a
plausible anchor. LLM placement and residual calls are reserved for bounded ambiguities, group
coherence, and residual interpretation.

**When a ceiling is hit.** A local graph over its neighborhood limit reduces to the strongest anchors
and highest-quality edges *before* the dossier is built. A dossier over its token budget must not
truncate silently in a way that removes the decisive evidence: P11 summarizes deterministic facts,
preserves anchor excerpts, splits the task, or defers.

**When the budget is exhausted.** P11 emits a decision with `outcome = abstain`,
`abstention_reason = budget_deferred`, and `deferred_stage` set. Extracted evidence is retained and
the file or group is left in review. It is **never** placed by a cheaper, lower-confidence rule.
§8.6 is literal: *cost exhaustion must never turn into lower-quality automatic classification*.
`deferred_stage` exists specifically so the interface can distinguish deferred work from completed
work and avoid the false impression that an unprocessed file was understood and found unimportant.

### Correction learning (§8.7)

**Actions recorded**, drawn from §8.7 and §7.10: accepting a proposed destination; accepting the same
destination for a batch (bulk decision); rejecting a destination match; changing a destination;
returning a file to a different accepted group; excluding one member from a group plan; choosing a
shallow fallback over a deeper node; keeping a file in place; moving a residual file to a custom
location; creating a custom folder; marking a file private; deferring; disabling a type of
suggestion.

**Scope is explicit on every record** (§8.7): file / group / destination node / template / domain /
corpus. §8.7's own example is the governing test — a user saying that *one* transcript belongs in a
Columbia packet must not teach the engine that *all* transcripts belong there, while a user
repeatedly placing product screenshots under Reference Clips may become a corpus-level preference
(§7.10).

**Negative examples are first-class** (§8.7, §7.10). Rejected destination matches, rejected residual
recommendations, and rejected labels are stored **with the evidence that produced them**, so the same
attractive-but-wrong destination is not resurfaced. **Before emitting `outcome = place` (or a residual
equivalent), P11 queries P1 `learning_records`** for `placement` / `(subject_id, node_id)` or
`residual` / `(file_id, residual_node_id)`. A matching unresected reject skips that node — never
auto-place ([`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md)). §7.10's example is a
required behaviour: PDFs rejected out of Receipts and Confirmations because they are actually school
forms must route future similar files back toward Academic or Applications review.

Preferences and negative examples are local, inspectable, and resettable; no silent global training
(§8.7). Note that a user creating a custom folder during residual review is a **tree edit**, routed
to P10 and producing a new plan version (§8.8) — it is never the model inventing a destination
(§7.4).

### Plan versioning (§8.8)

**Belongs to a plan version**, not to the shared evidence database: every placement decision record,
every group plan, the whole §6.2 retrieval index (a projection of one frozen tree), residual set
decisions, and placement policy settings. §8.8 lists "placement policy settings" and "associated
review decisions" among a plan version's contents.

**Not P11's plan-version state**, though §8.8 lists both among a plan version's contents: the §6.1
**destination profiles** are P10's (resolution B4) and the **residual-library configuration** — the
definitions and the user's enable / rename / relocate choices alike — is P10's (M10, O11). P11 reads
both at their frozen version and versions neither.

**Belongs to the shared evidence database**, unchanged across versions: files, observations, facts,
values, accepted groups, and the correction/negative-example store. §8.8 is literal — *the evidence
database remains shared across plan versions, but the destination tree and user policy define which
projections are valid in each version*.

**On a new plan version**: P11 re-projects. Decisions whose destination node no longer exists are
marked as requiring renewed review and appear in the version diff (§8.8's own example: *twenty-three
files now require renewed review because their previous destination no longer exists*). Decisions are
**never** silently remapped onto a renamed or relocated node, and a new plan **never** silently
reclassifies or moves files already placed under an earlier one. Learned preferences carry across
versions but their application is filtered by whether the node they reference still exists.

---

## Open questions

Unsettled by the design. Not answered here.

**Closed by 04-resolutions and recorded here, not repeated below:** who owns the residual-library
configuration in the plan version (O11 → P10) and the residual template definitions (O12 → P10, via
M10's move); who owns the §6.1 destination profile (B4 → P10); who resolves a node to a filesystem
path (B3 → P12); the two-condition rule with one legal candidate (B8(b) — stated under
[Contract out §1](#1-the-placement-decision-record--one-shape-both-paths), not left open); and the
§6.10/§7.9 ownership split that was OQ11 below.

1. **The two-condition thresholds (§6.10).** The design fixes neither the *minimum support
   threshold* nor the *meaningful margin*. Explicitly not chosen here. Both must be configurable and
   both must be recorded on every decision so a changed threshold is auditable and replayable (§8.5).
2. **What the support score is computed over (§6.6, §6.10).** §6.6 says the dossier carries
   "deterministic scores" and §6.10 requires a "minimum support threshold", but no scale, range, or
   combination rule over facts / group support / graph anchors / retrieval is defined. Threatens P2:
   a replay assertion cannot compare scores across versions without a defined scale.
3. **Is the §6.11 confidence-class list closed?** §6.11 gives four labels by example ("might be
   labeled"), not as an enumeration. If it is open, the review interface and P2's assertions need to
   know what else may appear. **This threatens P2 and any review surface built against fixtures.**
4. **Is the `abstention_reason` vocabulary closed?** Each value above traces to a named design
   failure mode (§6.3, §6.5, §6.9, §6.10, §8.4, §8.6), but the design never enumerates them as a set.
5. **Does the two-condition rule apply per member inside a group plan, or only to the shared parent?**
   §6.8 confirms the shared parent first and then classifies members; §6.10 is stated for "the best
   legal destination" without saying whether a member placement inside an already-confirmed parent is
   independently subject to both conditions. Affects how many group members land in review.
6. **§6.9: abstain *or* ask — which, when?** The design permits both for a multi-home file with no
   shared branch and gives no selector.
7. **Is the "reference or alias convention" (§6.9) a filesystem artifact?** If an alias means a
   symlink or hardlink, it collides with §8.3's safe default to *avoid following symbolic links during
   mutation*. **This threatens P12's contract** — P12 must know whether it will ever be asked to
   create a link, and P10 must know whether the alias policy produces a second node.
8. **How many times may a file cycle between §7 and §6 (§7.9)?** The loop is required; no bound,
   termination rule, or forced-abstention condition is stated. **Threatens P2's replay determinism.**
9. **Is a residual set-level decision (§7.6) itself versioned and reversible?** §8.8 lists
   "associated review decisions" in a plan version, but §7.6's set decisions gate model spend, so
   whether reversing one re-runs the model at cost is unstated.
10. **Is §7.5's eight-way set partition canonical or illustrative?** Read as illustrative here and
    deferred; if it is canonical, the set taxonomy becomes a contract P2 must assert against.
11. ~~**Joint ownership of §6.10 and §7.9.**~~ **Settled by resolution O7**, confirming the split
    both specs already proposed: **P8 owns the validator mechanism and the verdict shape; P11 owns
    the destination-specific checks and the record they populate.** P8's verdict populates
    `two_condition` and gates `review_policy`; P8 does not define the two-condition fields, so the
    drift this question anticipated cannot occur.
12. **Where does the shared-material policy (§6.9) live in the frozen tree?** §6.9 requires the tree
    to "include a policy for shared material" but does not say whether it is a tree-level setting, a
    per-branch setting, or a node type. **Threatens P10's node schema.**

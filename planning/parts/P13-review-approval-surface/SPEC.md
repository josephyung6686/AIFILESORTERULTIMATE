# P13 — Review and approval surface

Owns: the review and approval surface — §6.11, §7.5–§7.6, §7.10, §8.3, §8.4, §8.5, §8.6,
**presentation and collection only**. The decision logic, the records and their semantics stay with
their owners: §6.11, §7.5–§7.6 and §7.10 are P11's; §8.3 is P12's; §8.4 is P7's; §8.5 is P2's. The
qualifier applies to all seven sections equally — P13 renders what those parts publish and collects
what the user does, and writes no record any of them owns.
Status: contract draft

## Purpose

P13 is the surface on which the user sees what the system decided and says what should happen
instead. It **renders records other parts publish and collects user actions**. It decides nothing,
validates nothing, and mutates nothing.

It exists because eight obligations in the design describe a user-facing moment that no other part
owns (S4, G10, G13, G14):

- §6.11 — *"The user should see these distinctions in the review interface, because a direct
  placement and a context-supported placement should not demand the same level of trust."*
- §7.5 — *"a visible residual surfacing screen, not an automatic cleanup operation"*, divided into
  understandable review sets *"rather than presenting a single intimidating pile."*
- §7.6 — a set-level decision *"before the LLM analyzes individual files."*
- §7.10 — every recommendation editable, *"bulk decisions where the evidence pattern is similar"*,
  and the learning that follows from both.
- §8.3 — *"show it to the user where policy requires review"*; ask the user to refresh a stale plan
  *"rather than applying an old decision to a changed file"*; and say *"This action cannot be undone
  automatically because the file changed after it was moved"* with the relevant paths and hashes.
- §8.4 — configurable redaction in the canvas and review screens, and the moment a model needs
  sensitive text: *"the user should see that requirement and choose whether to allow a local model,
  a cloud model, a redacted prompt, or no model use."*
- §8.5 — the replay system serves *"the engineering team **and the user**."*
- §8.6 — *"The user interface should show the difference between completed work and deferred work."*

Without P13, §8.3's `Required review policy` field has no consumer: a plan can be marked
review-required and nothing exists to review it, and P11's contract that P12 *"consumes only records
with `outcome = place` whose `review_policy` has been satisfied"* has no event that satisfies it.

Two rules govern everything below.

**P13 presents and collects; it never decides.** Every user action it collects is routed to the
owning part as an §8.7 correction carrying its scope. A collected action never becomes a fact, a
verdict, a group, a placement, a tree edit or a filesystem mutation inside P13.

**P13 renders only what the boundary released.** Redaction happens in the part that owns the data —
P7's display policy (§8.4) and P10's rule that *"protected profiles are redacted at the boundary, not
at the renderer"*. P13 has no code path that receives protected content and then hides it.

---

## Design slice owned

| § | Obligation P13 owns |
|---|---|
| §6.11 | Rendering the structured placement decision so its four named labels — `exact fact match`, `context-supported group match`, `shared-material decision`, `abstain: no supported destination` — are distinguishable, and a direct placement does not present the same affordance as a context-supported one |
| §7.5 | The residual surfacing screen: the summary line, the division into review sets, and the seven display attributes §7.5 requires of every set |
| §7.6 | Presenting the set-level question and collecting the choice **before** any per-file model review is presentable |
| §7.10 | Every recommendation editable; bulk decisions where the evidence pattern is similar; the eight user actions §7.10 enumerates — accept for one file, accept for a small batch, change the destination, create a custom folder, return the file to a different accepted group, mark private, defer, leave untouched |
| §8.3 | Presenting a plan where policy requires review; surfacing a **stale** plan for refresh; surfacing an **undo conflict** with its paths and hashes |
| §8.4 | Configurable redaction across names, previews, thumbnails, OCR text and location data; the aggregate-safe form (*"11 protected identity records"*); and the `NeedsConsent` moment with §8.4's four options |
| §8.5 | The user-facing evaluation view — surfaced shadow examples, per-dimension comparison, per-stage attribution (G13) |
| §8.6 | The progress line: completed versus deferred work, assembled from P3, P4/P5 and P8 counts (G14) |
| §8.7 | The **presentation half** only: presenting the scope choice on every correction, and the inspect/reset surface §8.7 requires. The store is P1's (S5) |
| §8.8 | Presenting the plan-version diff and collecting compare / restore / adopt (§8.8's three named user actions) |

### Explicitly not owned

| Not owned | Owner | Why the boundary sits here |
|---|---|---|
| The §5.x canvas **data contract** — branch candidates, protected areas, existing folders, the vertical pass, live structural feedback, tree health | P10 (§5.1–§5.11) | P10 publishes the fields; P13 renders them and collects the tree edits, routing them to P10 |
| The residual **set computation** and the semantics of a set decision, including §7.6's gating rule | P11 (§7.5, §7.6) | P11 computes `residual_set` and owns the contract that no per-file model call precedes a `residual_set_decision`. P13 owns the screen and the collection |
| Any decision, score, threshold, verdict, or abstention | P6, P8, P9, P10, P11 | P13 has no scoring or classification code at all |
| Redaction, handling classes, consent policy, the gate | P7 (§8.4) | P13 presents the four options and the settings; P7 decides and records |
| Path resolution, collision policy, the move, undo execution | P12 (§8.3) | P13 shows a **node and its ancestor labels**, never a resolved path (B3); P12 resolves and executes |
| The §8.7 learning-record store | P1 (S5, G3) | P13 renders the projection and collects a reset |
| The replay harness, bundles, assertions, comparisons, shadow runs | P2 (§8.5) | P13 renders P2's records; it computes no metric |

---

## Contract in

### From P11 — placement and residual (§6.11, §6.8, §7.5, §7.6)

- The **placement decision record** in full: `decision_id`, `plan_version`, `supersedes`,
  `origin_stage`, `returned_from`, `subject`, `group_plan_id`, `outcome`, `destination {node_id,
  node_role}`, `return_target`, `marked_state`, `ask`, `decision_depth {node_depth, supported_depth,
  unsupported_levels[]}`, `evidence_type`, `confidence_class`, `matching_facts[]`, `group_support`,
  `graph_anchors[]`, `conflicts_considered[]`, `alternatives[]`, `two_condition`,
  `abstention_reason`, `deferred_stage`, `privacy`, `review_policy`, `explanation`, `residual`.
  `destination.node_role` is P10's vocabulary — `ordinary | scoped-general | residual |
  shared-material` — carried verbatim by P11. **There is no `destination.kind`** (MINOR 6); the
  deliberately shallower parent (§6.7) is a non-empty `decision_depth.unsupported_levels[]` naming
  the levels left unfilled, not a second role value, and that is what P13 renders as *"the levels
  deliberately left unfilled"*.
- The **group plan** (§6.8): `shared_parent_node_id`, `member_decisions[]`, `excluded_outliers[]`
  with the conflicting fact and where each outlier was routed.
- The **residual set** (§7.5): `label`, `file_count`, `representative_examples[]`,
  `file_type_distribution`, `age_range`, `evidence_availability`, `sensitivity_status`,
  `weak_graph_neighbours[]`, `reason_not_placed`.
- The **residual set decision** shape (§7.6) and its four choices, so P13 can present them.

### From P10 — the frozen tree and the canvas (§5, §6.1, §8.8)

Node records (`node_id`, `node_type`, `display_label`, `parent_node_id`, `root_anchor`, `ordinal`,
`explanation`, `node_role`, `disposition`, `handling_class`, `accepts_placement`); the ancestor
`display_label` chain, which is what P13 shows in place of a path (B3); destination profiles (§6.1);
the freeze record and the node-level **diff** (§8.8); and the six canvas data contracts P10
publishes (§5.1–§5.2 branch candidates, §5.2/§8.4 protected areas, §5.2/§5.10 existing folders, §5.3
the vertical pass, §5.5/§5.9 live structural feedback and warnings, §5.11 tree health).

### From P7 — privacy (§8.4)

`Gate.display_policy() -> RedactionSettings` over the five facets (names, previews, thumbnails,
OCR text, location data); `Gate.summarize_protected(scope) -> {count, class_breakdown}`; the five
handling classes and the `protected` flag; `Gate.may_move_automatically(...)`; `RevocationResult`
including `retraction_limit`; and, from any part whose gate call returned it, `NeedsConsent
{requirement, options}` — the four options being exactly `local_model | cloud_model |
redacted_prompt | no_model_use`.

### From P12 — apply and undo (§8.3)

The move plan record with all thirteen §8.3 precondition fields plus the intended display name,
filesystem-safe name and placement-decision reference; the precondition verdict `fresh |
stale:<trigger>` over §8.3's five triggers; the name resolution record; the collision resolution
record; the execution record with its four §8.2 verification points in P1's published V1–V4 framing
(MINOR 4) — V1 before preparing the action, V2 immediately before the move or copy, V3 after
completion, and V4 the cross-volume destination confirmation before the source may be removed, V4 on
cross-volume moves only; the journal entry; and the undo verdict, including the four `conflict:*` /
`refused:*` values.

### From P3, P4/P5, P8 — the §8.6 counts

- P3 R5: `files indexed`, `paths excluded by rule`, `files deferred (scan budget exhausted)`.
- P4 `extraction_runs`: `completeness ∈ complete | capped | partial | metadata_only | deferred |
  unsupported | unreadable | failed` and `coverage {units, processed, total}`, one row per
  *(file version × extractor)* (B1), with P5 supplying which ceiling caused a `capped` or `deferred`
  run (§2.7, §8.6).
- P8: the count of files awaiting or flagged for model review — `Verdict.requires_review = true`,
  and calls the harness has deferred under a §8.6 ceiling.

### From P2 — evaluation (§8.5)

`run_manifest`, the per-stage `assertion` record with its seven verdicts and `attributed_stage`, the
`comparison` record's `per_dimension[]` blocks, and shadow mode's `surfaced_examples[]` and
`review_adjudication[]`.

### From P1 — provenance and learning (§8.2, §8.7)

The append-only `events` writer; the event history for any subject P13 displays; the scoped
projection over `events.correction_scope` that is the §8.7 learning-record store (S5); and the §8.6
budget configuration object, so a ceiling can be named in the progress line (G4).

### From P4/P6 — citation resolution (§2.8, §3.12, M14)

`observation_key` resolution to a displayable excerpt, and `file_facts` with their reliability state.
**P13 cites `observation_key`, never `observation_id`** — a negative example recorded today must
still resolve after an extractor upgrade (M14, §8.7).

---

## Contract out

P13 publishes four things: what must be presentable, one action record, one progress record, and one
approval record. It publishes no derived judgement of any kind.

**The field names below are the names a consuming part declares in its own Contract-in** (N-1).
Types, stated once for all three records: every `*_id` and `*_ref` is an opaque identifier string,
and `subject_ref`, `presented_state_ref`, `placement_decision_ref`, `bulk_member_refs[]` and
`scan_ref` are foreign keys to the record named beside them; `plan_version` is P10's plan id plus
version, the version the surface was rendered against; `routed_to[]` is a list of part identifiers;
`user_id` is §8.2's user-identity field; `acted_at`, `decided_at` and `rendered_at` are timestamps;
`count` is an integer; `bulk_basis`, `cause` and `label` are display strings; every remaining field
takes exactly one value from the closed list printed with it, and P13 adds no value to any list it
did not print.

### 1. The review item — what must be presentable

A **review item** is a rendering projection over one subject. It adds no field. Its contract is that
every listed element is reachable from published records and none may be omitted from the surface;
how it is laid out is deferred.

**Placement review item (§6.11).** Must present: the subject (file or group); the destination as its
**ancestor `display_label` chain**, never a path string; `confidence_class` rendered as one of §6.11's
four labels; `evidence_type`; `decision_depth` including the levels deliberately left unfilled;
`matching_facts[]` each with its resolvable citation; `group_support` with its membership kind
(`direct-anchor` vs `context-supported`); `graph_anchors[]`; `conflicts_considered[]` — what was
suppressed and why (§6.3); `alternatives[]`; the `two_condition` figures with both thresholds;
`explanation`; `review_policy`; and the privacy block.

Three rendering obligations follow from the design and are contractual:

- **Trust is not uniform.** A `place` decision whose `confidence_class` is `context-supported group
  match` must not present the same one-click affordance as `exact fact match` (§6.11).
- **A budget deferral is not an abstention.** `deferred_stage` set must render differently from an
  evidential `abstain` (§8.6, P11's own reason for carrying the field).
- **The explanation is shown with its citations**, so P11's rule that an explanation *"must not claim
  evidence the file does not carry"* is checkable by the person reading it (§6.4, §6.11).

**Group plan review item (§6.8).** Presented as **one coherent group plan**, not several unrelated
file moves: the shared parent, the member decisions beneath it, and each excluded outlier with its
conflicting fact and where it was routed.

**Residual surfacing screen (§7.5).** The summary line (*"Your main structure is ready. We found 146
files that do not fit a confirmed group or approved destination."*), then one card per
`residual_set` presenting all seven §7.5 attributes: representative examples, file-type
distribution, age range, available OCR or text evidence, sensitivity status, weak graph neighbours,
and the reason the normal pipeline could not safely place the files.

**Set decision (§7.6).** The set question with its four choices from `residual_set_decision`.
**Ordering is enforced by the surface**: P13 has no view that presents a per-file residual
recommendation for a set with no recorded set decision, because §7.6 places the set decision before
per-file model review and a set the user leaves in place must cost zero model calls.

**Apply review item (§8.3).** All thirteen §8.3 precondition fields, plus the intended display name
beside the filesystem-safe name, the collision policy, the sensitivity and consent state, the reason
and evidence summary, and the plan's expiration state.

**Stale plan item (§8.3).** Which of the five triggers fired (`content_hash_differs`,
`source_path_changed`, `destination_changed`, `source_vanished`, `permission_lost`), the expected
versus observed values, and a **refresh** action. There is no control that applies a stale plan.

**Undo conflict item (§8.3).** The design's own sentence — *"This action cannot be undone
automatically because the file changed after it was moved"* — with the original source path,
destination path, expected content hash and observed content hash, for manual resolution. There is
no force-undo control: §8.3 says undo must not force a rollback.

**Evaluation view (§8.5, G13).** Shadow-surfaced examples with the baseline and candidate outputs
side by side; comparison results **per dimension, never collapsed**; and `attributed_stage` naming
which of the ten stages an error began in. **No aggregate accuracy number is displayed or computed**
— §8.5: *"A single overall 'accuracy' number hides the mechanism that needs repair."* P2 states this
as a rule binding the renderer; P13 is that renderer.

**Learning view (§8.7).** The scoped learning records and stored negative examples from P1's
projection, each with the evidence that produced it, and a reset action — §8.7 requires that the user
*"be able to inspect or reset learned preferences, so personalization remains understandable and
reversible."*

**Canvas surfaces (§5).** P10's six canvas data contracts, rendered under the same redaction policy
as every other surface (§8.4 names *"the canvas and review screens"* together), with existing
structure visually distinct from proposed structure (§5.10).

### 2. `review_action` — the one record P13 emits

Every user gesture on every surface is collected as this record and routed. P13 writes nothing else.

```text
review_action
  action_id
  surface              placement | group_plan | residual_set | residual_file | canvas
                       | apply | undo_conflict | consent | privacy_settings
                       | evaluation | learning | plan_version                    §6.11, §7.5, §7.6, §7.10, §8.3, §8.4, §8.5, §8.7, §8.8
  subject_ref          decision_id | group_plan_id | set_id | node_id | plan_id
                       | journal_entry_id | consent_request_id | run_id
  plan_version         the version the surface was rendered against              §8.8
  action               accept | accept_bulk | change_destination
                       | return_to_accepted_group | create_custom_folder
                       | mark_private | defer | leave_untouched | reject
                       | edit_recommendation | disable_suggestion_type
                       | refresh_plan | approve_for_apply | select_consent_option
                       | set_redaction | adopt_version | restore_version
                       | reset_learning                                          §7.10, §8.3, §8.4, §8.7, §8.8
  bulk_member_refs[]   present only when action = accept_bulk; every member
                       enumerated, never a filter expression                     §7.10
  bulk_basis           the evidence pattern the user was shown as the reason
                       these files were offered together                         §7.10
  correction_scope     file | group | node | template | domain | corpus          §8.7
  routed_to[]          the owning part(s) this action is handed to
  presented_state_ref  the review_presentation event for what the user was
                       actually shown, under the redaction policy then in force  §8.2, §8.4, §8.7
  user_id, acted_at                                                              §8.2
```

**Routing is the whole contract.** P13 hands the action to the owning part and that part decides what
it means: placement and residual actions to P11; tree edits, including a custom folder created during
residual review, to P10 (a tree edit produces a new plan version, §8.8 — it is never the model
inventing a destination, §7.4); consent choices and redaction settings to P7; refresh and apply
approval to P12; group changes to P9; a reclassification to private to P7 and P6; a reset to P1.
An action may route to more than one part; it is still **one** collected gesture.

**What each receiving part declares** (N-1). One record shape, many surfaces. A part's Contract-in
needs one row of this table plus the field list above; no part is asked to change a record it owns.

| Part | Surfaces routed to it | What it accepts from P13 |
|---|---|---|
| P11 | `placement`, `group_plan`, `residual_set`, `residual_file` | `review_action` in full; `subject_ref` is a `decision_id`, `group_plan_id` or `set_id` |
| P10 | `canvas`, `plan_version`, and a custom folder created during residual review | `review_action` in full; `subject_ref` is a `node_id`; §8.8's compare, restore and adopt arrive as `action = adopt_version \| restore_version` |
| P7 | `consent`, `privacy_settings` | `review_action` in full; `subject_ref` is a `consent_request_id`; `action = select_consent_option \| set_redaction \| mark_private` |
| P12 | `apply`, `undo_conflict` | `review_action` with `action = refresh_plan \| approve_for_apply`, **and** `review_approval` in full — the record that satisfies §8.3's `Required review policy` |
| P9 | group changes collected on `group_plan` | `review_action` in full |
| P6 | a reclassification to private, jointly with P7 | `review_action` with `action = mark_private` |
| P1 | `learning` | `review_action` with `action = reset_learning`, and P13's three registered event types (see Provenance) |

**Scope is presented, never inferred.** §8.7's governing example is the acceptance test: a user saying
that *one* transcript belongs in a Columbia packet must not teach the engine that all transcripts
belong there. P13 presents the scope choice with the action and records what the user chose. It never
silently defaults a correction to `corpus`.

**Rejections carry their evidence.** §8.7 requires negative feedback stored *with the evidence that
produced it*; `presented_state_ref` plus the decision's `matching_facts[]` and `observation_key`
citations are that evidence, and they are what makes §7.10's worked case work — PDFs rejected out of
Receipts and Confirmations *because they are actually school forms* must route future similar files
back toward Academic or Applications review.

**A bulk action is expandable.** `bulk_member_refs[]` enumerates every member, so each resulting
per-file decision remains individually inspectable and individually correctable (§8.2, §8.7). A bulk
acceptance is not a single opaque decision over an unnamed population.

### 3. `progress_line` — §8.6 legibility (G14)

§8.6's own example is the acceptance case: *"1,842 files indexed; 1,611 fully extracted; 89 scanned
PDFs deferred after the OCR limit; 34 files require model review; 18 files remain unreadable."*

```text
progress_line
  scan_ref
  entries[]
    label            what this count means, in the user's terms
    count
    state            completed | deferred | blocked                          §8.6
    source           P3.R5 | P4.extraction_runs | P8                         §8.6
    cause            the §8.6 ceiling or condition that produced a deferral
                     — named, not implied                                    §8.6, G4
  rendered_at, plan_version
```

Assembly rules, each traced:

- `indexed` is P3's `files indexed` (R5).
- `fully extracted` counts a file only when **every** extractor run over its current content hash
  reports `complete` (B1). Any `capped`, `partial`, `metadata_only`, `deferred`, `unsupported`,
  `unreadable` or `failed` run keeps the file out of that count.
- `deferred` counts come from P4's `deferred` and `capped` runs, and each entry names the ceiling
  responsible — §8.6 requires the user to see *"what is running, what has been deferred, and why."*
- `unreadable` is P5's published mapping — runs at `unreadable` **or** `failed` — which under M3
  still carries the §2.9 metadata-level observations. It is displayed as **indexed but unreadable**,
  never as empty. Taking P5's mapping rather than `unreadable` alone is what stops a `failed` run
  from appearing in no entry at all, which the rule below forbids.
- `require model review` comes from P8. See Open questions — §8.6's phrase admits two readings.

**Completed and deferred are never merged into one number**, and no indexed file may be absent from
every entry. §8.6: this *"avoids the false impression that an unprocessed file was understood and
found unimportant."* That sentence is the reason this record exists.

### 4. `review_approval` — the §8.3 gate, finally consumed

```text
review_approval
  approval_id
  plan_id                   the §8.3 move plan reviewed
  placement_decision_ref    §6.11
  plan_version              §8.8
  required_review_policy    the value on the plan that demanded review        §8.3
  verdict                   approved | rejected | deferred | refresh_required
  presented_state_ref       what was shown, under the redaction policy        §8.4
  user_id, decided_at
```

S4 assigns the *presentation* of §8.3's `Required review policy` to P13. **Enforcement stays with
P12**, which refuses any plan whose required review is unsatisfied. P13 produces the record that
satisfies it and nothing more; a missing approval is a refusal by P12, not a decision by P13. This
answers the record half of P12's Open question 10 — S4 settled it by naming P13 and P12 records it as
settled, but neither side named a record — and gives P11's clause — *"P12 consumes only records with
`outcome = place` whose `review_policy` has been satisfied"* — the event it referred to.

**The shape P12 declares** (N-1). `approval_id` opaque id; `plan_id` P12's §8.3 move plan;
`placement_decision_ref` P11's `decision_id`; `plan_version` P10's plan id plus version;
`required_review_policy` the value P11 put on that decision's `review_policy`; `verdict ∈ approved |
rejected | deferred | refresh_required`; `presented_state_ref` the `review presentation` event;
`user_id`; `decided_at`. Only `verdict = approved` carrying the plan's **current** `plan_version`
satisfies the policy — an approval stamped with a superseded version does not, because approvals do
not carry across versions (§8.8).

### 5. The `NeedsConsent` surface (§8.4, B2)

When any part's `Gate.release` returns `NeedsConsent`, control returns to that part and P13 presents:

- `requirement` — which items require sensitive text, and why;
- the four options **verbatim from §8.4**: allow a local model, allow a cloud model, allow a redacted
  prompt, or no model use.

Three obligations, all binding:

1. **All four options are always presentable.** A surface that offers fewer has silently made the
   user's decision for them.
2. **A pending consent request is never rendered as an abstention.** It renders as awaiting the
   user — P11's `review_policy = blocked_pending_user`. B2 is explicit that `NeedsConsent` must never
   be mapped to `abstain`; the rendering is the last place that mapping could reappear.
3. **The chosen option is routed to P7**, which authors the §8.4 consent events and the consent-aware
   audit record. P13 records the collection, not the grant.

### 6. To P2 (§8.5)

P13 emits no `stage_output`. It is not one of §8.5's ten attribution stages, it decides nothing that
could diverge, and inventing an eleventh stage would corrupt P2's closed `stage_id` enumeration.
What P13 owes P2 is different: **every surface must be renderable from a replay bundle**, so a review
screen can be reconstructed for a past run without a live filesystem, and `presented_state_ref` must
serialize into and re-assert from a bundle.

---

## Deferred — manual design required

| Deferred item | Defined by | Note |
|---|---|---|
| **All visual design** — layout, components, styling, typography, colour, iconography, interaction patterns, navigation, empty states, and every word of user-facing copy | — | This spec fixes the **information contract**: what must be presentable and what must be collectable. It fixes no pixel. §5.2's card, §7.5's list and §8.6's line are quoted as *content* requirements, not as layouts. The design gives one worked sentence per surface and no interface specification; inventing one here would be inventing design |
| The 200–300 domain template library | §5.7 | P10's surface; P13 renders whatever the frozen tree carries |
| Domain fact fields beyond §3.11's literal six-row table, including Career (§3.15) | §3.11, S3 | P13 renders `matching_facts[]` generically and hard-codes no field name |
| Gazetteer contents | §3.7 | P6's |
| The contents of the nine residual templates — the values for §7.2's eight attribute slots | §7.2, §7.3, M10 | M10 moved §7.2–§7.4 from P11 to **P10**, and the slot values are deferred there. P13 renders the enabled library as P10 froze it |
| The canonical partition of residual files into review sets | §7.5 | §7.5's eight lines are prefaced *"It may show"*. P11 defers the partition; P13 renders whatever partition P11 publishes and must not assume eight sets or these eight names |
| Default lifecycle review policies | §7.11 | §7.11's *"older than 30 days"* and *"every two weeks"* are things the user may define, not defaults |
| The §8.6 ceiling values | §8.6, G4 | Configuration owned by P1; P13 displays the ceiling that fired, never a value of its own |
| Default redaction settings and the install-default operation mode | §8.4 | P7's deferred items; P13 presents whatever P7 publishes |
| Selection criterion for which shadow examples reach the user | §8.5 | P2 states the criterion is not settled by the design — see Open questions |

---

## Done means

1. A placement decision with `confidence_class = exact fact match` and one with `context-supported
   group match` render distinguishably, and the context-supported one does not offer the same
   one-step acceptance affordance (§6.11).
2. A decision with `outcome = abstain`, `abstention_reason = no_supported_destination` and a decision
   with `deferred_stage` set render as visibly different states; neither renders as a placement
   (§6.10, §8.6).
3. Every `matching_facts[]` citation on a rendered decision resolves through `observation_key` to a
   displayable excerpt, and a decision citing an unresolvable key renders the failure rather than
   omitting the citation (M14, §8.7).
4. A `shared-material decision` (§6.9) and an `ask_user` decision both reach a surface; neither is
   auto-resolved and neither is hidden.
5. The residual surfacing screen presents all seven §7.5 attributes for every set; a set missing one
   is a rendering failure, not a shorter card.
6. **Negative test:** no view exists that presents a per-file residual recommendation for a set with
   no recorded `residual_set_decision`. A fixture set the user chose to leave in place produces zero
   presented model recommendations and zero model calls (§7.6).
7. Every recommendation is editable and every §7.10 action is collectable: accept one, accept a
   batch, change the destination, create a custom folder, return the file to a different accepted
   group, mark private, defer, leave untouched.
8. A bulk acceptance emits one `review_action` enumerating every member, with `bulk_basis` naming the
   evidence pattern the user was shown; each member's resulting decision is separately inspectable
   and separately correctable (§7.10, §8.2).
9. Every collected action carries an explicit `correction_scope` chosen at collection time. **Negative
   test:** no code path assigns `corpus` scope without the user selecting it (§8.7).
10. A rejection is stored with the evidence that produced it, and re-presenting the same subject shows
    the prior rejection (§8.7, §7.10).
11. A plan with `Required review policy = review_required` cannot reach apply without a
    `review_approval` with `verdict = approved`; P12 refuses it in the absence of one (§8.3).
12. Each of §8.3's five staleness triggers renders as a refresh item naming the trigger and the
    expected-versus-observed values. **Negative test:** no control applies a stale plan (§8.3).
13. An undo conflict renders the design's own sentence with the original source path, destination
    path and both content hashes. **Negative test:** no force-undo control exists (§8.3).
14. With the display policy set to redact names, no surface — canvas, placement review, residual
    screen, apply screen or evaluation view — renders a filename for a protected file, and no cached
    rendering from before the policy change survives it (§8.4).
15. A protected set renders as an aggregate (*"11 protected identity records"*) and cannot be expanded
    into a filename list while the policy redacts names (§8.4, §7.5).
16. A `NeedsConsent` return presents all four §8.4 options with the requirement statement. **Negative
    test:** the pending subject renders as awaiting the user, never as an abstention and never as a
    completed decision (§8.4, B2).
17. A revocation renders `retraction_limit` — that revocation cannot necessarily retract data already
    sent to an external provider — as a specific statement listing the prior releases, not a generic
    disclaimer (§8.4).
18. The progress line reproduces §8.6's example from real records: indexed from P3, fully-extracted
    from P4 `complete` runs, deferred entries each naming the ceiling that fired, model review from
    P8, unreadable from P4. No indexed file is absent from every entry (§8.6, G14).
19. **Negative test:** the evaluation view displays no aggregate accuracy number and computes none;
    comparison results are shown per dimension (§8.5).
20. The learning view lists scoped learning records and negative examples with their evidence, and a
    reset is collectable (§8.7).
21. A plan-version diff renders §8.8's own case — *"twenty-three files now require renewed review
    because their previous destination no longer exists"* — and compare, restore and adopt are all
    collectable (§8.8).
22. **Negative test:** P13 contains no scoring, classification, validation, path-resolution or
    filesystem-mutation code, and writes no record other than the four in Contract out.
23. Every surface renders from a P2 replay bundle without a live filesystem, and
    `presented_state_ref` round-trips through a bundle (§8.5).

---

## Cross-cutting answers

### Provenance (§8.2)

**Events P13 appends**, registered under P1's registration rule (B5). The nineteen §8.2 names are
reserved and none is redefined here.

```text
review presentation      a reviewable record was rendered, naming the subject, the redaction
                         policy in force, and the evidence references actually shown
review action routed     a user gesture was collected, with its correction_scope and the
                         part(s) it was handed to
apply review approval    the §8.3 required-review policy was satisfied, rejected, deferred,
                         or found to need a refresh, for a named plan
```

Each carries §8.2's required fields: event type, file ID, content hash, responsible subsystem, user
identity (always present — every P13 event records an explicit user action or what preceded one),
time of observation, and a structured explanation or evidence reference.

**Why `review presentation` is a distinct event and not noise.** §8.4 makes what was displayed a
privacy-relevant fact, and §8.7 requires a stored negative example to carry the evidence that produced
it. A rejection is only interpretable against what the user was actually shown — a file rejected while
its OCR text was redacted is a different signal from one rejected with the evidence visible.

**Why `review action routed` does not duplicate P11's user-decision event.** The **acting part
authors; P1 writes** (M8). P11 authors the placement or residual user decision, P10 authors the tree
edit, P7 authors the consent events, P12 authors the move events. P13 authors only the fact that one
gesture was collected and where it went — which matters because a single gesture may route to two
parts. §7.10's "create a custom folder" during residual review is both a residual decision (P11) and
a tree edit (P10); without P13's event, the two records lose the fact that they were one user action.

**What P13 never overwrites:** nothing, because P13 owns no supersedable record. It never edits a
decision, plan, verdict, fact or observation, and it never re-renders history: a superseded record is
shown **as** superseded, with its reason, alongside the record that replaced it (§8.2). A user
correction produces a new record authored by the owning part; the prior one stays inspectable.

### Budgets and degradation (§8.6)

**P13 owns no ceiling from §8.6's list of twelve.** It issues no model call, runs no extraction and
performs no retrieval; the ceilings it renders belong to P5 (OCR and image analysis), P8 (calls,
cost, dossier tokens), P9 and P11 (neighbours, graph size, cluster size, residual batch size) and
P10 (folder proposals and depth). P13 consumes the §8.6 configuration object (P1, G4) only to **name**
the ceiling that produced a deferral.

**P13 is the surface §8.6's legibility clause requires**, so its degradation answer is inverted
relative to every other part: what other parts do when a budget is exhausted, P13 must make visible.

- A deferral is rendered as deferred, with its cause named — never as a completed result and never
  omitted (§8.6).
- **Cost exhaustion never turns into lower-quality automatic classification**, and it never turns
  into a lower-quality *presentation* either: P13 does not present a `deferred_stage` decision as a
  weaker recommendation, does not fill a missing value with a plausible one, and offers no "accept
  anyway" affordance over a deferred subject.
- §8.6's maximum residual files in one review batch is P11's ceiling; P13 renders the batch P11
  publishes and shows how much of the set remains unreviewed, so a truncated batch never reads as a
  finished one.

### Correction learning (§8.7)

**P13 is the collection point for almost every action §8.7 enumerates** — accepting or rejecting a
group, excluding one member from a packet, renaming a branch, merging or splitting groups, changing
template order, creating a custom template, moving a residual file to a custom location, choosing a
shallow fallback, keeping a file in place, marking a file private, disabling a type of suggestion —
and for none of the *learning*. The store is P1's scoped projection over `events.correction_scope`
(S5, G3); the meaning of each correction belongs to the part it is routed to.

**Scope is a presented choice, not a default.** Every `review_action` carries one of §8.7's six
scopes, selected at collection time and recorded. This is the mechanism behind §8.7's own example and
its converse: one transcript in a Columbia packet is a `file` correction; repeatedly placing product
screenshots under Reference Clips may be offered as a `corpus` preference — offered, and only applied
if the user chooses it.

**Negative feedback is first-class.** Rejected groups, destination matches, labels and residual
recommendations are collected as actions with `action = reject`, carrying `presented_state_ref` and
the decision's citations, so §8.7's requirement that they be *"stored with the evidence that produced
them"* is satisfied by the record shape rather than by a convention.

**Inspect and reset is a P13 surface.** §8.7 requires the user to be able to inspect or reset learned
preferences. P13 renders P1's projection and collects the reset; P1 records it. No learning is applied
by P13 and none is hidden from this view.

**No silent global training** (§8.7): P13 has no telemetry path and sends nothing anywhere. Every
surface it renders and every action it collects stays local.

### Plan versioning (§8.8)

**P13 holds no plan-version state.** It has no state of its own at all beyond the events it appends;
every surface is a projection of records that already belong to a version or to the shared evidence
database.

**Every surface names the version it is rendered against.** `review_action.plan_version` and
`review_approval.plan_version` record it, so an action collected against a superseded version can be
identified rather than silently applied to the current one.

**The diff is P13's to present** (§8.8): P10 emits the node-level diff, P11 computes the file-level
consequence, and P13 renders both — §8.8's own examples being that Applications was renamed to
Admissions, Research moved under Projects, Reference Clips was added, the Academic template's
dimension order changed, and *"twenty-three files now require renewed review because their previous
destination no longer exists."* §8.8's three user actions — compare versions, restore an earlier
draft, explicitly adopt the new plan — are collected as `review_action` and routed to P10.

**A new plan never silently reclassifies or moves old files** (§8.8). The surface consequence: files
requiring renewed review are presented as requiring review, never pre-accepted at their old
destination and never auto-approved because they were approved in an earlier version. Approvals do not
carry across versions.

**Redaction settings and consent policy** are §8.8 plan-version state (*"Privacy and model-consent
policies"*); P13 collects changes to them and routes them to P7, which owns the record.

---

## Open questions

Unsettled by the design. Not answered here. A settled entry keeps its original number so existing
citations still resolve, and records what settled it — P1's convention.

1. **Is §6.11's confidence-class list closed?** §6.11 gives four labels by example (*"might be
   labeled"*), not as an enumeration. P13 must render a distinguishable treatment per class and P2
   must assert against them. If the list is open, neither can be built against fixtures. *Threatens
   P11 and P2* — this is P11 OQ3 seen from the surface, and it is the single question that most
   constrains P13.
2. **Is §7.5's eight-way set partition canonical or illustrative?** P11 reads it as illustrative and
   defers it. If it is canonical, the residual screen's set taxonomy becomes a contract. *Threatens
   P11 and P2.*
3. **What does "34 files require model review" count?** §8.6's phrase admits two readings: files
   queued for a model call that has not happened, and files whose model verdict returned
   `requires_review: true` (P8's `accept_context_supported`, always). The two are different
   populations and the design names one number. *Threatens P8.*
4. **How does a file with runs in several completeness states appear in the progress line?** P4's
   record is per *(file version × extractor)* (B1); §8.6's line is per file and reads as a partition.
   A file whose EXIF read `complete` and whose OCR was `capped` has no defined bucket. *Threatens P4
   and P5.*
5. **What outcome does a user-chosen "no model use" produce?** §8.4 offers it as one of four options
   but does not say what the calling part records. If it collapses to `abstain`, it is
   indistinguishable from an evidential abstention and from a budget deferral — the exact conflation
   B2 exists to prevent. *Threatens P8 and P11.*
6. **Is §8.3's required-review approval per plan, per batch, or per policy class?** §8.3 says "show it
   to the user where policy requires review" and separately gives a plan an "expiration state". Does
   an approval expire with its plan, and does approving a batch approve each plan in it? *Threatens
   P12.*
7. **Does the user's redaction setting have a scope?** §8.4 says *"Protected branches should have
   configurable redaction"*, which reads per-branch, while P7's `Gate.display_policy()` takes no scope
   argument and reads global. *Threatens P7.*
8. **What does the user see in the evaluation view, and by what criterion are shadow examples
   selected?** §8.5 says the replay system serves the engineering team *and the user* and that shadow
   mode surfaces *"only selected examples for human review"*, without saying whether those audiences
   see the same thing or how examples are chosen. S4 assigns the surface to P13; it does not settle
   the content. *P2 OQ12, unresolved.*
9. **Does a reviewer adjudication in the evaluation view become an §8.7 correction?** If it does, the
   eval view routes actions like every other P13 surface; if not, it is read-only. §8.5 and §8.7 do
   not connect. *P2 OQ10, unresolved. Threatens P2.*
10. **Where do version-family and deduplication review surface?** §8.3 produces both outcomes
    (`retain_newer_older_to_version_family_review`, `content_hash_match` supporting deduplication
    review) and G5 makes both universal facts, and P12 OQ7 is settled — the screen is P13 and the
    version-family fact is P6's — but no section names that screen's **action set**, which is what
    P13 would have to present and collect. *Threatens P6 and P11.*
11. **Is a `review presentation` record deletable derived data?** §8.4 lets the user *"review and
    delete local derived data"*; §8.2 makes the event log append-only. The same conflict P7 and P5
    raise about stored observations applies to the record of what was displayed. *Threatens P1 and P7.*
12. **Settled — MINOR 10.** `user_id` is kept, nullable, and populated only on an explicit user
    action; P1 OQ14 records the same closure. The consequence for P13: every P13 event records an
    explicit user action or what preceded one, so P13 is the one part on which the field is always
    populated. Nothing here is open.

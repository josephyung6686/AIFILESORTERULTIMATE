# P12 — Apply and undo

Owns: §8.3
Status: contract draft

## Purpose

P12 is the only part that mutates the filesystem. Every other part produces proposals; P12 turns an
approved placement decision into a change on disk, or refuses. Its purpose is the §8.3 guarantee:
every filesystem mutation is a transaction with preconditions, execution steps, verification, and a
reversible journal entry — and *"no file should move merely because a placement score is high"* (§8.3).

Its second purpose is conditional undo (§8.3): reversal is offered only when the disk still matches
what the journal recorded, and surfaces a **conflict** rather than forcing a rollback when it does not.

P12 has no opinion about where a file belongs. It receives a destination and either applies it under
verification or parks it for the user.

## Design slice owned

Owns **§8.3 in full**:

- the transaction discipline — plan → review where policy requires → currency validation → apply one
  action at a time or in a safely bounded batch → verify resulting state → record enough to undo
- the move plan record and its **complete expected precondition** (§8.3's field list, reproduced verbatim below)
- the immediate-pre-apply recheck and the five staleness triggers
- filename collision policy and the four user-approved collision behaviours
- filesystem-difference normalization; intended display name recorded separately from filesystem-safe name
- **resolution of a destination node to a filesystem path.** §8.3's plan record carries `Requested
  destination node` *and* `Resolved destination path` as separate fields, so resolution is a step of
  the mutation transaction and P12 owns it. P10's frozen tree stays platform-neutral — it is addressed
  by ID, never by path string (§8.3, §8.8) — and P12 composes the path from P10's `root_anchor` and the
  ancestor `display_label` chain under §8.3's case-sensitivity, Unicode-normalization, reserved-name,
  prohibited-character and path-length rules. The same frozen tree must therefore resolve correctly on
  a case-sensitive volume and on a case-insensitive one.
- creation of the intermediate directories a resolved path requires, and their conditional removal on
  undo — §5.1 and §5.12 leave frozen nodes as designed structure rather than folders on disk
- enforcement of §1.1's cross-folder movement permission at mutation time, alongside the volume check
- defined behaviour for special filesystem objects and volumes
- conditional undo, the undo entry, and the CONFLICT outcome

Owns from **§8.2** (P1 owns the rest of §8.2): the four checksum verification points, named in P1's
published framing **V1–V4** (MINOR 4) — V1 before preparing a filesystem action, V2 immediately before
executing a move or copy, V3 after completing the action, V4 the cross-volume copy-and-delete
confirmation before the source may be removed. V1–V3 run on every action and are §8.2's stated minimum;
V4 runs only on a cross-volume move. That conditionality is why this spec previously counted "three
points plus cross-volume fixity" — the same four things under a different name, now dropped in favour of
P1's. P1 performs and records each hash comparison; P12 calls them and owns what a mismatch means.

Does **not** own: destination choice (§6, P11), the tree and its nodes (§5, P10), sensitivity
classification (§8.4, P7), the file record and event-log schema (§8.2, P1).

Two capabilities the design withholds from P12, stated so no neighbour assumes them:

- **No delete operation for user files** (§7.11: the product "must not delete files, mark them
  disposable, or move them out of a protected area without explicit user action"). The single removal
  the design authorizes is removal of the **source** after a cross-volume copy whose destination hash
  has been confirmed (§8.2).
- **No semantic renaming.** The only permitted name changes are filesystem-safety normalization and a
  deterministic collision suffix (§8.3). "Rename" in §5.10, §8.7, and §8.8 refers to tree branches, not
  to files; the design grants file renaming nowhere.

## Contract in

### From P11 — the placement decision record (§6.11)

Read against **P11's published field names**, not §6.11's prose.

```text
outcome                       the only value P12 consumes is  place
destination.node_id           the frozen-tree node — never a path string   §5.12, §6.2
destination.node_role         ordinary | scoped-general | residual
                              | shared-material — P10's vocabulary,
                              carried through P11 (MINOR 6)                §5.9, §6.9, §7.4
subject.kind                  file | group
subject.file_id, content_hash the expected content hash of the plan        §8.2
subject.group_id, member_file_ids                                          §6.8
group_plan_id                 shared by all members of one group plan      §6.8
plan_version                  the organization plan version the decision
                              is valid in                                  §8.8
decision_id, supersedes       the decision this plan executes, and what
                              it replaced                                  §8.2
explanation, evidence_type,
matching_facts[], group_support, decision_depth
                              carried into `Reason and evidence summary`   §8.3, §6.11
confidence_class              descriptive only — never a refusal condition §6.11
privacy.handling_class,
privacy.model_eligibility,
privacy.consent_audit_ref     carried into `Sensitivity and consent state` §8.4
review_policy                 auto_eligible | review_required
                              | blocked_pending_user                       §6.11, §8.4
```

**Only `outcome = place` produces a plan.** The other six values of P11's `outcome` —
`return_to_placement`, `mark_review_later`, `leave_in_place`, `mark_state`, `ask_user` and `abstain` —
**produce no plan at all**. They are not refusals and they never reach the transaction: `abstain` is a
successful outcome (§6.10), `leave_in_place` and `mark_state` are decisions not to move (§7.7),
`mark_review_later` moves only if the Review Later node's §7.4 disposition says so and then arrives as
a later `place`, `return_to_placement` hands the file back to the §6 placement pass (§7.9), and
`ask_user` is a question to the user (§6.9). P12 records none of these as a refusal class, because a
refusal class describes a plan that could not execute and here no plan exists.

`abstain: no supported destination` is a value of `confidence_class`, not of `outcome`; P12 branches
on `outcome` only.

P12 **refuses to build a plan** for an `outcome = place` decision when:

- `destination.node_id` is not a node of the frozen tree of the referenced `plan_version`
  (§5.12; §6.12: "No system component may invent a new destination after freeze")
- the node's `accepts_placement` is `false`, or its `node_role = residual` with
  `disposition = review-only` or `leave-in-place` (§7.4). P10 states the freeze guarantee for P11 *and*
  P12: the legal destination set is exactly `{node_id : plan_version = frozen version,
  accepts_placement = true}`
- §1.1's cross-folder movement permission forbids the move (see the P10 contract below)

**`review_policy` is deliberately not in that list.** §8.3 fixes the order — the product must
*"first create a plan, show it to the user where policy requires review, validate that the plan is
still current, apply one action at a time"* — so a decision whose `review_policy` is
`review_required` or `blocked_pending_user` **does produce a plan**, and that plan carries the value
in its `Required review policy` field (Contract out §1). What P12 refuses is to **execute** it. The
refusal class is `review_policy_unsatisfied` (Contract out §2), and the record that lifts it is
P13's `review_approval` (Contract in, below). Refusing to build would leave §8.3's review step with
nothing to show and P13 with nothing to render.

**Group decisions expand one-to-one.** P11's `group_plan` carries `member_decisions[]` — one
`placement_decision` per member, all sharing a `group_plan_id` (§6.8). P12 builds one move plan per
member decision, each with its own preconditions, verification and journal entry (§8.3), and carries
`group_plan_id` so the set is presented as one coherent group plan rather than several unrelated moves
(§6.8). `excluded_outliers[]` carry no decision and produce no plan.

### From P10 — the frozen tree (§5.12)

P10 publishes no paths for designed structure, and P12 asks for none. What P12 consumes is what
resolution needs:

```text
node_id, node_type            existing | proposed | user-created
                              | protected | ignored                        §5.12
display_label                 the intended display name for this level     §5.12, §8.8
parent_node_id                walked upward to build the ancestor chain     §5.12
root_anchor                   which §1.1 candidate root the subtree hangs
                              beneath, and the existing folder it names     §1.1, §5.2
existing_path                 present only when node_type = existing        §5.10
accepts_placement             the legality flag                             §5.12, §5.10, §8.4
node_role, disposition        residual nodes: physical-destination
                              | review-only | leave-in-place                §7.4, §5.9, §6.9
handling_class                carried from P7, not re-derived               §8.4
```

plus two freeze-record policies (§8.8):

- the **shared-material policy** for multi-home files — shared branch, primary-home convention,
  reference or alias convention, or mandatory review (§6.9)
- the **cross-folder movement permission** — §1.1's "whether files may move across high-level folders",
  recorded by P3 as `cross_folder_moves` and stored by P10 at freeze under Placement policy settings
  (§1.1, §8.8). P3 records it and P10 stores it; **P12 is where it is enforced**, at mutation time,
  alongside the volume check. A plan whose destination `root_anchor` names a different high-level
  folder from the one the source file currently lives under is refused when the permission is off —
  §1.1's own case: a file in Downloads may go to a Personal Projects folder on Desktop, or it may
  "remain within Downloads as a separately organized file".

A `root_anchor` names a §1.1 candidate root — a folder the **user selected because it already
exists** — so it has a real path that is not part of the designed tree. That is the one concrete
anchor; everything below it is composed by P12 (Contract out §3). The §7.3 residual templates resolve
by the same rule: once enabled they "become legal nodes in the frozen destination tree" (§7.4), so the
five templates with no default location create no dependency for P12 — their column in §7.3 is a
suggestion shown at tree design, never a path handed to P12.

### From P7 — sensitivity and consent (§8.4)

Handling class (one of §8.4's five literal classes), operation mode, and whether policy explicitly
permits automatic movement. §8.4: protected material "should not be moved automatically without a user
policy that explicitly permits it" — so a protected handling class forces `Required review policy` to
explicit user approval and bars automatic execution.

### From P13 — the review approval (§8.3, S4)

**`review_approval` is the record that satisfies `Required review policy`.** P11 sets the policy on
the decision, P7 can force it to explicit approval, and P13 collects the user's answer; without a
typed record from P13, P12's precondition has an enforcement rule and no input.

```text
approval_id                    the approval itself
plan_id                        the §8.3 move plan reviewed — joins on Contract out §1's
                               `Plan ID`                                             §8.3
placement_decision_ref         §6.11 — `decision_id`, so an approval cannot drift onto
                               a superseded decision                                 §8.2
plan_version                   §8.8 — the version the approval was collected under
required_review_policy         the value on the plan that demanded review            §8.3
verdict                        approved | rejected | deferred | refresh_required
presented_state_ref            what was shown, under the redaction policy in force   §8.4
user_id, decided_at                                                                  §8.2
```

Four rules, all enforced by P12 and none of them decided by P13:

1. **Only `verdict = approved` satisfies the policy.** `rejected`, `deferred` and
   `refresh_required` leave the plan unexecuted; `refresh_required` additionally routes to the same
   staleness path as §8.3's five triggers, and P12 re-validates rather than applying the old
   decision to a changed file.
2. **The approval must match the plan it is presented against** — same `plan_id`, same
   `placement_decision_ref` as the plan's `Placement decision reference`, same `plan_version`. A
   mismatch on any of the three is `review_policy_unsatisfied`, not an approval of a neighbouring
   plan. This is what keeps an approval collected under one plan version from authorizing a move
   under another (§8.8).
3. **An approval never overrides another refusal.** It lifts `review_policy_unsatisfied` and nothing
   else: a plan that is also stale, protected without policy, or bound for a node that refuses
   placement stays refused with that class. §8.4's "should not be moved automatically without a user
   policy that explicitly permits it" is a policy question, not an approval question.
4. **P12 verifies; it does not present.** P12 reads the record, checks `verdict` and the three
   identifiers, and appends its own §8.2 events. Rendering the plan, collecting the gesture and
   appending `apply review approval` are P13's (M8, S4).

**Absence is a refusal, never a default.** No approval record means `review_policy_unsatisfied`.
There is no timeout that ripens into consent and no configuration that skips the check for a plan
whose `Required review policy` demands one.

### From P1 — identity and file record (§8.2)

Internal file ID, content hash and hash algorithm, current path, observed size and timestamps, and the
**filesystem volume or root identifier**. Comparing source and destination volume decides atomic rename
vs copy-and-delete (§8.2). The size-and-modification comparison uses the same stat semantics as the
scan cache — size and modification time, with change in either direction treated as change (§1.2).

P1 also performs the hash comparison itself: it publishes `verify_content(file_id, expected_hash)`,
which P12 calls at **V1–V4**. P1 returns match or mismatch and decides nothing about what a mismatch
means; the staleness verdict (V1/V2), the failed-action verdict (V3), the pre-removal refusal (V4) and
the undo precondition are all P12's (§8.2, §8.3).

### From P2 — replay (§8.5)

Plan construction and precondition evaluation must be runnable without touching a live filesystem
(§8.5: replay evaluates changes "without touching a live filesystem"). Execution runs only against a
real root, which in test is a fixture root. A replay bundle carries the plan set, the fixture disk
state, and the expected transaction outcomes.

### Fixtures P12 publishes so neighbours can build before it exists

One plan-record fixture per outcome class (applied, stale, collision-suffixed, refused, paused, failed);
one journal-entry fixture and one undo-verdict fixture per undo outcome (reversed, each conflict class);
and a fixture directory containing the §8.3 hazards — a case-insensitive and a case-sensitive
destination volume, an NFC/NFD name pair, an over-length path, a reserved name, a symlink, a package
bundle, a two-volume pair, and a cloud-style conflict copy. For resolution (Contract out §3): a
four-level node chain whose second level is `existing`, a sibling pair whose distinct labels normalize
to one name, and a source-and-destination pair sitting under two different §1.1 high-level folders, so
P10 and P11 can see exactly what a `root_anchor` and label chain must supply.

## Contract out

### 1. The move plan record

§8.3's field list, reproduced exactly:

```text
Plan ID
File ID
Expected content hash
Expected source path
Expected source volume
Expected size and modification state
Requested destination node
Resolved destination path
Collision policy
Sensitivity and consent state
Reason and evidence summary
Required review policy
Creation time and expiration state
```

Carried alongside, each traced:

```text
Organization plan version        §8.8 — the version whose frozen tree resolved this destination
Placement decision reference     §6.11 — the decision this plan executes; `decision_id`
Group plan reference             §6.8 — `group_plan_id`, present for a group member, else null
Intended display name            §8.3 — "record the intended display name separately from
Filesystem-safe name             §8.3    the final filesystem-safe name"
Expected destination volume      §8.2 — decides atomic rename vs copy-and-delete
Path resolution reference        §8.3 — the resolution record that produced
                                 `Resolved destination path` (Contract out §3)
Destination root anchor          §1.1 — the high-level folder the destination hangs beneath
Source high-level folder         §1.1 — the source's own root, for the cross-folder check
Cross-folder movement permission §1.1, §8.8 — as recorded by P10 at freeze
```

`Resolved destination path` is produced by **P12's own resolution** (Contract out §3) from the node
identifier in `Requested destination node`; no upstream part supplies it. The two fields are separate
in §8.3 precisely because the request is an ID and the resolution is platform-specific.

A plan is a proposal. Creating one mutates nothing. A plan missing any of the thirteen §8.3 fields is
rejected at construction rather than executed with a gap.

### 2. Precondition verdict

Evaluated twice: when the action is prepared (§8.2 checkpoint 1) and immediately before the move or
copy (§8.3's recheck, which is also §8.2 checkpoint 2). The staleness triggers are exactly §8.3's five:

```text
content_hash_differs
source_path_changed
destination_changed
source_vanished
permission_lost
```

Verdict is `fresh` or `stale:<trigger>`. Stale removes the action from automatic execution and asks the
user to refresh the plan rather than applying an old decision to a changed file (§8.3). The stale plan
is never edited in place: a refreshed plan is a new plan record that **supersedes** it, with the old one
and its trigger retained (§8.2).

`destination_changed` covers both a destination path now occupied by a different object and a
destination node that no longer exists in the current organization plan version — §8.8's diff case
where files "require renewed review because their previous destination no longer exists".

### 3. Name resolution record

Produced **before an action is planned** — §8.3 requires long paths, invalid filename characters,
reserved names, prohibited characters, and platform path-length limits to "all be normalized before an
action is planned". Resolution has two halves, both recorded: the **destination directory**, composed
from the frozen tree, and the **file name** within it.

**Destination path resolution** (§8.3's `Requested destination node` → `Resolved destination path`):

```text
Requested destination node        P10 node_id — the tree is addressed by ID,
                                  never by a path string                       §8.3, §8.8
Root anchor                       the §1.1 candidate root and its existing path §1.1
Ancestor chain                    { node_id, node_type, display_label } from
                                  the root anchor down to the node             §5.12
Nearest existing ancestor         its `existing_path`, used verbatim            §5.10
Segments composed                 one per proposed / user-created ancestor,
                                  each normalized as a path component          §8.3
Resolved destination directory
Directories that must be created  §5.1, §5.12 — frozen nodes are designed
                                  structure, not folders on disk
Target volume and root identifier §8.2 — also decides rename vs copy-and-delete
Cross-folder verdict              within_root | cross_root_permitted
                                  | cross_root_refused                          §1.1
```

Five rules govern it:

1. **The anchor is the only path P12 is given.** Resolution walks `parent_node_id` from the node up to
   its `root_anchor`, then composes downward. The anchor is an existing user-selected folder (§1.1), so
   it carries a real path; nothing below it does.
2. **An `existing` ancestor short-circuits the composition.** Its `existing_path` is used verbatim and
   is never recomposed from its `display_label` — §5.10 preserves existing folders as they are, and a
   user alias over an existing folder must not silently retarget the write.
3. **Every composed segment is normalized as a path component** under the same §8.3 rules as a file
   name — Unicode form, invalid and prohibited characters, reserved names, length — and each segment
   keeps its intended `display_label` beside its filesystem-safe form, so a normalization change stays
   explainable at any level of the path, not only the last (§8.3).
4. **Resolution is evaluated against the *target* volume**, whose case sensitivity and path-length
   limit are properties of the destination, not of the tree. This is why the frozen tree holds no
   paths: the identical frozen node resolves on a case-sensitive and a case-insensitive volume, and
   only the collision outcome differs.
5. **Two sibling nodes whose distinct labels normalize to one filesystem name are refused, never
   merged.** Merging would silently collapse two frozen nodes into one destination — a destination the
   user never approved, which §6.12 forbids ("No system component may invent a new destination after
   freeze") and which the freeze guarantee contradicts, since the legal destination set is the set of
   frozen nodes (§5.12). §8.3's rule that normalization must be explainable rather than silent points
   the same way. The refusal is `refused:node_path_collision`; it surfaces both labels and the colliding
   name so the user can rename one at tree design (§8.3, §5.12, §6.12).

Resolution runs against the **current** organization plan version. A node that no longer exists, or
whose `accepts_placement` has become `false`, yields `destination_changed` (Contract out §2) rather
than a re-resolved path — §8.8's "previous destination no longer exists" case.

**File-name resolution:**

```text
Intended display name
Filesystem-safe name
Normalizations applied      unicode normalization form, case-folding decision,
                            invalid/prohibited character substitution,
                            reserved-name avoidance, length truncation
Target filesystem case sensitivity
Target filesystem path-length limit
```

Case sensitivity is a property of the **target** volume and is what decides whether `Resume.pdf` and
`resume.pdf` are one path or two (§8.3). Names are compared for collision under a single Unicode
normalization form, because normalization differs across operating systems and cloud services and makes
visually identical names potentially collide (§8.3). The intended display name survives every
transformation, so a collision or normalization change stays explainable (§8.3).

### 4. Collision resolution record

The engine must never silently overwrite an existing file (§8.3). The permitted behaviours are exactly
the four user-approved ones:

```text
preserve_both_deterministic_suffix
merge_only_if_hashes_identical
retain_newer_older_to_version_family_review
stop_and_ask
```

```text
Colliding destination path
Collision kind          name_only | content_hash_match
Incumbent content hash
Incoming content hash
Behaviour applied
Outcome                 suffixed path | merged, no write | older sent to version-family review
                        | halted awaiting user
```

`content_hash_match` supports **deduplication review**; `name_only` does not (§8.3). The
`merge_only_if_hashes_identical` behaviour may be selected only when the two hashes are equal — the
collision rule must distinguish exact duplicates from different files that happen to share a filename
(§8.3).

### 5. Execution record

The transaction result, carrying the results of P1's four verification points (§8.2):

```text
Plan ID
Mode                              atomic_rename | cross_volume_copy_and_delete
Hash at preparation               V1 — before preparing a filesystem action (§8.2)
Hash immediately before move      V2 — immediately before executing a move or copy (§8.2)
Hash after completion             V3 — after completing the action (§8.2)
Destination confirmed pre-removal V4 — cross-volume only (§8.2)
Result                            applied | refused:<class> | stale:<trigger>
                                  | paused:<reason> | failed:<class>
Final destination path
Directories created by this action
Timestamps
```

`refused:<class>` uses one vocabulary in two places. The destination checks — frozen-tree membership,
`accepts_placement`, residual `disposition`, node path collision, cross-folder permission — are
evaluated **at plan construction**, where they refuse to produce a plan at all, and again at the
pre-apply recheck, where the plan version or the user's settings may have changed since; a refusal
there lands on the execution record. **`review_policy_unsatisfied` is evaluated at the pre-apply
recheck only**, because §8.3 requires the plan to be built so it can be shown (Contract in → From
P11, From P13); it therefore always lands on the execution record and never suppresses a plan. What
never appears in this vocabulary is a non-`place` P11 outcome: it produces no plan and no refusal
(Contract in). The classes are exactly the refusals stated in this spec:

```text
node_not_in_frozen_tree          §5.12, §6.12
node_refuses_placement           accepts_placement = false, or a review-only /
                                 leave-in-place residual disposition      §5.10, §7.4, §8.4
node_path_collision              two sibling labels normalize to one name §8.3, §6.12
cross_folder_not_permitted       §1.1's permission is off and the
                                 destination root anchor differs          §1.1
review_policy_unsatisfied        no P13 `review_approval` with `verdict = approved`
                                 for this plan, decision and plan version §8.3, S4
protected_without_policy         §8.4
source_or_destination_unavailable  §8.3 — unmounted volume, detached storage
symlink_not_followed             §8.3 safe default
package_bundle_unapproved        §8.3 safe default
hash_unverifiable                a checkpoint hash could not be computed;
                                 refused rather than applied unverified   §8.2, §8.6
```

**The cross-folder check runs with the volume check, before any mutation.** With `cross_folder_moves`
off, a plan whose destination `root_anchor` names a high-level folder other than the one the source
currently lives under is refused as `cross_folder_not_permitted`, and the refusal names §1.1's
permission so the user can see it was their own setting and not a placement failure. With the
permission on, the verdict is `cross_root_permitted` and the move proceeds under the ordinary volume
rule — the permission is about the user's folder landscape, the volume check is about atomic rename
versus copy-and-delete, and neither substitutes for the other.

For a cross-volume move, the destination copy **must be hashed and confirmed before the source can be
removed** — this is V4 (§8.2). A mismatch leaves the source in place and yields `failed`; this is file fixity — the
system can show that the file at its destination is byte-identical to the file it intended to move
(§8.2). Directory creation for a frozen node's path is itself a mutation and runs under the same
transaction discipline (§8.3), since §5.1 and §5.12 leave frozen nodes as designed structure rather
than real folders.

### 6. Journal entry — the undo record

§8.3's required contents:

```text
Original source path
Destination path
Content hash at the time of movement
Collision behaviour
Post-move verification result
```

plus what reversal needs:

```text
Journal entry ID
Plan ID and organization plan version              §8.8
File ID and hash algorithm                         §8.2
Source volume, destination volume, execution mode  §8.2
Directories created by this action
Intended display name and filesystem-safe name     §8.3
Time of execution
```

The journal is append-only: an undo appends a reversal entry; it never edits or removes the original
(§8.2).

### 7. Undo verdict

Undo is **conditional, not destructive** (§8.3). Before reversing, the system confirms the file at the
destination is still the expected content and that restoring it will not overwrite a newer or unrelated
file.

```text
reversed
conflict:destination_content_changed
conflict:destination_missing_or_moved
conflict:source_path_occupied
refused:source_or_destination_unavailable
```

A conflict performs no mutation and reports the relevant paths and hashes for manual resolution, in the
design's own terms: *"This action cannot be undone automatically because the file changed after it was
moved."* (§8.3). Undo never forces a rollback (§8.3). Reversal is itself a mutation and runs the full
discipline — preconditions, V1–V3 (and V4 where the reversal crosses volumes), and its own appended
journal entry.

**Directories P12 created are reversed on the same conditional terms.** §8.3 requires every mutation to
be reversible, and creating a directory for a frozen node is a mutation P12 performed, recorded in the
journal's `Directories created by this action`. On undo, a created directory is removed **only** when
all three hold: this journal entry recorded creating it, it is still empty, and no other journal entry
that is still applied moved a file into it or beneath it. Removal proceeds deepest-first through the
chain this entry created and stops at the first directory that fails a condition. Otherwise the
directory is **retained** and the retention and its reason are recorded on the reversal entry — a
retained directory is never a conflict, because the file reversal itself succeeded. Nothing here can
remove a user file: §7.11's prohibition is untouched, an empty directory contains none, and a directory
P12 did not create is never a candidate.

```text
Directory reversal outcome    removed | retained:not_empty
                              | retained:referenced_by_other_entry
                              | retained:not_created_by_this_entry
```

### 8. Events appended to P1's log (§8.2)

P12 **authors** these six §8.2 event types; **P1 writes them** — the acting part is the author, P1 is
the writer of the log:

```text
planned move
executed move
failed move
filename-collision resolution
external modification detection
undo
```

Each carries §8.2's event record fields: event type, file ID, content hash, old and new paths where
applicable, responsible subsystem, model or extractor version where applicable, user identity for
explicit user actions, time of observation, and a structured explanation or evidence reference.
`external modification detection` is appended whenever a staleness trigger fires or a cloud sync
conflict is observed — the observation is recorded even though no mutation occurs. That type has **two
authors**: P12 detects it at §8.3's pre-apply recheck, and P3 detects it at §1.2's re-scan. P12 claims
authorship of its own detections only, never sole authorship of the type.

### 9. Special-object and volume behaviour — settled defaults only

| Object or condition | Behaviour, as settled by the design |
|---|---|
| Symbolic link | Do not follow during mutation (§8.3 safe default) |
| macOS package / application bundle | Do not move unless explicitly approved (§8.3) |
| Source or destination unavailable | Refuse the move (§8.3) — covers an unmounted network volume or detached removable storage |
| Cloud-synchronized path (iCloud Drive, Dropbox, Google Drive, OneDrive) | Treat as externally mutable: verify immediately before and after the action; pause when a sync conflict appears (§8.3) |
| Permission no longer available | `stale:permission_lost` (§8.3's fifth trigger), not a failure |
| Protected or highly sensitive handling class | No automatic movement without a policy that explicitly permits it (§8.4) |
| Destination in a different high-level folder, `cross_folder_moves` off | Refuse — `cross_folder_not_permitted` (§1.1), checked at mutation time alongside the volume check |
| Resolved destination directory does not exist on disk | Create it under the same transaction discipline and record it in `Directories created by this action` (§8.3; §5.1, §5.12 leave frozen nodes as designed structure) |

Locked files, files currently open in another application, aliases, and shortcuts: §8.3 requires
defined behaviour and does not supply it — see Open questions.

### 10. Batch contract

§8.3 permits applying "one action at a time or in a safely bounded batch, verify the resulting state".
Each file's move is one transaction with its own verification and its own journal entry; a batch is a
bounded **sequence** of transactions, not one atomic unit — an all-or-nothing automatic rollback would
contradict undo being conditional and per-entry (§8.3). A sync conflict pauses the run (§8.3). Batch
size and the general halt rule are unsettled — see Open questions.

## Deferred — manual design required

Nothing here is invented; each item is named with the § that defines it and its relation to P12.

- **The 200–300 domain template library (§5.7).** Not on P12's path. P12 never reads a template; it
  receives a destination `node_id` and resolves the path itself from `root_anchor` and the ancestor
  `display_label` chain (§5.12, §8.3). `template_context` is not among the node fields P12 consumes.
  Recorded so the reviewer can confirm P12 carries no dependency on it.
- **Domain fact-schema fields beyond §3.11's literal table.** Not on P12's path. P12 reads no facts —
  only the placement decision's reason and evidence summary (§6.11).
- **Gazetteer contents (§3.7).** Not on P12's path.
- **Residual library contents beyond the nine §7.3 names (§7.2, §7.3).** Not a dependency for P12.
  Once the user enables a residual branch it "become[s a] legal node[] in the frozen destination tree"
  (§7.4), and P12 resolves it from `root_anchor` plus the ancestor `display_label` chain exactly like
  any other node (Contract out §3). The `Default location` column in §7.3 is a suggestion shown at tree
  design; the five templates that carry none therefore create no gap. What P12 does read is the node's
  `disposition` — a `review-only` or `leave-in-place` residual node is refused as a write target.
- **Per-filesystem constraint tables.** §8.3 names the categories that must be handled — invalid
  filename characters, reserved names, prohibited characters on particular filesystems, platform-specific
  path-length limits — but enumerates no values. These are platform facts to be authored as a data
  asset, not design decisions. P12's contract is that a name resolution record exists and records which
  constraint applied, whatever the table contains.

## Done means

1. The walking-skeleton line passes end to end: resolve node → plan → verify preconditions → create
   any missing directories → move → verify hash → undo → verify restored.
2. A plan record carries all thirteen §8.3 precondition fields; one missing field rejects the plan at
   construction rather than executing with a gap.
3. Each of the five staleness triggers is independently reproducible against a fixture and yields
   `stale:<trigger>`, no mutation, an `external modification detection` event, and a refresh prompt —
   never an automatic apply (§8.3).
4. V1, V2 and V3 are recorded for every applied action, and V4 additionally for every cross-volume
   one (§8.2). An action whose V3 hash differs from the expected hash reports `failed`, never
   `applied`.
5. A two-volume fixture proves the destination is hashed and confirmed before source removal, and that
   a mismatch leaves the source in place (§8.2).
6. All four collision behaviours are exercised: a name-only collision does not receive deduplication
   treatment; a hash-identical collision does; `retain_newer` emits a version-family review item;
   `stop_and_ask` halts with no mutation (§8.3). No path exists through the code that overwrites an
   existing file.
7. `Resume.pdf` and `resume.pdf` collide on a case-insensitive destination volume and coexist on a
   case-sensitive one, with the name resolution record explaining both outcomes (§8.3).
8. Two names differing only by Unicode normalization form are detected as a collision, not written as
   two files (§8.3).
9. A name exceeding the target path-length limit, containing a prohibited character, or matching a
   reserved name is normalized **before** the plan is created, with the intended display name preserved
   separately (§8.3).
10. Symlink and package-bundle fixtures are refused by default; an unavailable source or destination is
    refused (§8.3).
11. A cloud-synced fixture carrying a sync conflict copy pauses instead of applying (§8.3).
12. Undo of an untouched move restores byte-identical content to the original path with the hash
    verified. Undo where the destination file was edited returns `conflict:destination_content_changed`
    with both paths and both hashes and mutates nothing. Undo where the original source path is now
    occupied by an unrelated file returns a conflict rather than overwriting it (§8.3).
13. Every applied, refused, stale, paused, and undone action appended its §8.2 events, and no event,
    plan record, or journal entry was edited or removed by a later action.
14. No operation exists that deletes a user file (§7.11); the only source removal is the verified
    cross-volume case (§8.2).
15. Plan construction and precondition evaluation run under P2's replay against a fixture root without
    touching a live filesystem (§8.5).
16. A node three levels below its nearest `existing` ancestor resolves to that ancestor's
    `existing_path` followed by one normalized segment per intervening `display_label`, with every
    segment's intended label retained beside its filesystem-safe form. The same frozen node resolves to
    the same directory on a case-sensitive and a case-insensitive fixture volume; only the collision
    outcome differs (§8.3).
17. Two sibling nodes whose distinct labels normalize to one filesystem name yield
    `refused:node_path_collision` naming both labels — never one merged directory (§8.3, §6.12).
18. A `place` decision whose node is absent from the frozen tree, or whose `accepts_placement` is
    `false`, or whose residual `disposition` is `review-only` or `leave-in-place`, produces no
    mutation (§5.12, §7.4, §8.4). Each of P11's six non-`place` outcomes produces **no plan record at
    all** — not a refused one.
19. With `cross_folder_moves` off, a plan whose destination `root_anchor` names a different high-level
    folder from the source's is refused before any mutation, and the refusal cites §1.1's permission.
    With it on, the same plan applies (§1.1).
20. Directories created by an action appear on both the execution record and the journal entry. Undo
    removes one only when it is still empty and unreferenced by another applied entry; a directory that
    has since received another file is retained with the reason recorded, and the file reversal still
    reports `reversed` (§8.3, §7.11).
21. **Review approval.** A decision with `review_policy = review_required` **produces a plan** carrying
    `Required review policy` — a plan is built, not withheld (§8.3). With no P13 `review_approval`
    present, applying it yields `review_policy_unsatisfied` and mutates nothing. With an approval whose
    `verdict = approved` and whose `plan_id`, `placement_decision_ref` and `plan_version` all match the
    plan, the same plan applies end to end, and P13's `apply review approval` event stands beside
    P12's `planned move` and `executed move` events for the same `Plan ID` (§8.2, M8).
    **Negative tests, each independently reproducible:** `verdict = rejected`, `deferred` and
    `refresh_required` each leave the plan unexecuted, and `refresh_required` re-validates on the
    staleness path rather than applying; an approval matching on `plan_id` but naming a different
    `plan_version` or a superseded `placement_decision_ref` is refused, not accepted; and an approved
    plan that is also stale, protected without policy, or bound for a node refusing placement stays
    refused under **that** class, never applied (§8.3, §8.4, §8.8, S4). The same fixture pair proves
    `blocked_pending_user` behaves identically to `review_required`.

## Cross-cutting answers

### Provenance (§8.2)

**Authors** (P1 writes them): `planned move`, `executed move`, `failed move`,
`filename-collision resolution`, `external modification detection`, `undo`, with §8.2's event record
fields. P12 is the author of these six, and the **only** author of five of them;
`external modification detection` is co-authored with P3, which detects the same condition at §1.2's
re-scan.

**Never overwrites:** a plan record (a refreshed plan supersedes it; the stale plan and its trigger are
retained); a journal entry (an undo appends a reversal entry); path history (P1 retains it — P12 supplies
old and new paths on the `executed move` event); any earlier checkpoint hash. A later result may
supersede an earlier one, never replace it (§8.2).

**Verification points:** P12 is the only caller of V1–V4 and the only writer of their recorded
results — the V1/V2/V3 checkpoint hashes and V4's cross-volume pre-removal confirmation (§8.2).

### Budgets and degradation (§8.6)

§8.6 defines no ceiling for mutation. The only bound the design gives P12 is §8.3's "safely bounded
batch", whose size it does not state (Open questions). §8.6's nearest listed ceiling — maximum residual
files in one review batch — governs review, not movement, and is not repurposed here.

Degradation rule in P12's terms: **cost or time exhaustion never becomes a lower-quality automatic
move** (§8.6). A plan that cannot be verified is parked for review, never applied best-effort. §8.2's
V1–V3 are a stated minimum and may not be skipped to save time on a large file, nor may V4 on a
cross-volume move; if hashing cannot complete, the action is refused rather than applied unverified.

Legibility (§8.6): an apply run reports applied / refused / stale / paused / failed counts, so deferred
work is visible rather than presented as completed.

### Correction learning (§8.7)

**Records, with scope:** approving a plan, refusing or skipping one, choosing a collision behaviour when
asked, keeping a file in place (§8.7 lists this explicitly), moving a residual file to a custom location
(§8.7 lists this explicitly), and undoing an applied move.

**Scope defaults to `file`.** A wider scope — group, node, template, domain, corpus — is set only by
explicit user action, never inferred by P12; §8.7's own example is that one transcript belonging in a
Columbia packet must not teach that all transcripts do.

**Negative feedback (§8.7):** a refused or undone plan is stored together with the placement decision's
evidence summary, so the association that produced it can be down-weighted rather than resurfaced.

P12 does not learn. It emits correction records; the consumers are the proposing parts (P9, P10, P11).
Whether an undo constitutes negative feedback, and at what scope, is an Open question — §8.7's list of
user actions does not include it.

### Plan versioning (§8.8)

Two different objects are both called a "plan" and both carry a "Plan ID": §8.3's **move plan** for one
file, and §8.8's **organization plan version** (destination tree plus policies). Every move plan records
the organization plan version whose frozen tree resolved its destination.

**Belongs to the plan version:** the set of pending move plans, their resolved destination paths, the
collision policy settings, residual-node policies, review policies, and §1.1's cross-folder movement
permission — §8.8's "Placement policy settings" and "Residual-library configuration". A resolved path
is a function of one frozen tree, so it belongs to that version and is **re-resolved**, never carried,
when a new version is adopted.

**Belongs to the shared durable store, not to any version:** the journal and the provenance events. They
record what physically happened on disk, which is not a projection of a plan; §8.8 keeps the evidence
database shared across plan versions.

**Rule:** adopting a new plan version does not carry pending move plans into automatic execution. They
are re-derived and re-reviewed under the new version — §8.8: "A new plan should never silently
reclassify or move old files," and the diff case where files "require renewed review because their
previous destination no longer exists," which surfaces here as `destination_changed`.

## Open questions

1. **Deterministic suffix format.** §8.3 requires a "deterministic suffix" and specifies no form. P2's
   fixtures and any P11 preview of a resolved destination path depend on the exact string.
2. **Settled by P11's published record.** P11's `group_plan` carries `member_decisions[]` — one
   `placement_decision` per member, all sharing a `group_plan_id` (§6.8). P12 builds one move plan per
   member decision and carries the `group_plan_id`; no group-level expansion is required of P12. See
   Contract in, from P11.
3. **Undefined special-object behaviour.** §8.3 requires "defined behavior for locked files, files
   currently open in another application, ... aliases, shortcuts" but supplies defaults only for symbolic
   links, package bundles, and unavailable source or destination. Locked, open-in-another-application,
   alias, and shortcut behaviour is undefined. (Permission failure is covered by the fifth staleness
   trigger.)
4. **Batch bound and halt rule.** §8.3's "safely bounded batch" has no stated size, and only a sync
   conflict is named as pause-worthy. Does any other refusal or failure halt the remainder of a batch?
5. **Settled by B3 (04-resolutions).** Path resolution is P12's, so directory creation is part of
   resolution and its removal is part of conditional undo. Creation runs under the transaction
   discipline and is recorded in `Directories created by this action`; undo removes a created directory
   only when it is still empty and unreferenced by another applied entry, and otherwise retains it with
   the reason recorded. See Contract out §3, §5 and §7.
6. **Unverified destination copy after a failed cross-volume move.** §8.2 forbids removing the source
   until the destination hash is confirmed; §7.11 forbids deleting files. What becomes of the partial or
   hash-mismatched destination copy?
7. **Settled by S4 and G5 (04-resolutions).** The reviewing surface is **P13**, the review and approval
   surface; the version-family fact itself is **P6**'s (§3.11). P12 emits the review item and holds no
   opinion about how it is displayed.
8. **Alias or reference convention for multi-home files.** Narrowed: P10 now records which §6.9
   convention the tree adopted (shared branch, primary-home, reference-or-alias, or mandatory review),
   so P12 receives the choice. What remains unstated is whether the alias convention requires P12 to
   **create** a link, and whether link creation is a mutation P12 may perform — §8.3 only says not to
   **follow** symbolic links during mutation.
9. **Journal and undo lifetime.** §8.3 gives a move plan an "expiration state" but says nothing about the
   journal expiring. Does elapsed time, or adopting a new plan version, end the ability to undo an
   earlier applied move?
10. **Settled by S4 (04-resolutions), and now typed.** The review and approval surface is **P13**.
    P12 enforces the gate — it **builds** the plan, because §8.3 requires one to show, and executes
    nothing while P11's `review_policy` is `review_required` or `blocked_pending_user` and no approval
    matches. P13 is where the user satisfies it, and the record that does so is P13's
    **`review_approval`** with `verdict = approved` (Contract in → From P13). The seam is that record
    joined to the plan's `Plan ID`, `Placement decision reference` and plan version — not the
    `Required review policy` field alone, which states the requirement without carrying its answer.

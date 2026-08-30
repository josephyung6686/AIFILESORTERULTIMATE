# 81 — What a person can do on a review screen, and whether it gets recorded truthfully

Date: 2026-08-31
Status: **Decision brief. No code, no test, no manifest and no vocabulary was changed by this
document.** `74` §8 Q2 has been open since `74` was written and blocks P13 Wave B's canvas routing,
P9's integration swap, and `74` §8 Q4 alongside it.
Reads: `planning/74-PLAN-P12-P13.md`, `planning/69-HANDOFF.md`,
`planning/01-product-design-structured.md`, `planning/parts/P13-review-approval-surface/SPEC.md`,
`planning/parts/P9-grouping/SPEC.md`, `src/`, `tests/`, the strict-xfail compatibility report, and
four probe runs that handed P13's real record to each of the three live receivers.

Every factual claim about behaviour carries a file and line and was checked by reading the code or by
running it. Where a claim is a reading rather than a fact it says so. Judgement is in §9 and nowhere
else.

---

## 1. The question, in one paragraph

A `review_action` is the record of a gesture a person made on a review screen. One record, one
gesture, and the record is what the product later reads back to say *why* a folder exists and to stop
proposing something the person already refused. Four parts have written down what that record looks
like, and they disagree — about what the fields are called, and about which gestures exist at all.
`74` §8 Q2 frames this as a tidying problem between modules: widen one list, narrow two, or write a
translation table. **It is not a tidying problem.** Three of the four lists were each derived from a
different part of the design's own prose, all three readings are defensible, and the union of them is
larger than any one. The real question underneath is not which module wins. It is: **what are the
things a person can actually do on a review screen, and does every one of them get recorded
truthfully?** On the evidence below, the answer today is that six gestures the design names in its
own words have nowhere to be recorded at all, and one gesture is spelled two ways in two live
vocabularies.

---

## 2. The four vocabularies, in full

The brief that commissioned this asked for all four enumerated rather than summarised, because "four
vocabularies" is abstract and four concrete lists are not. These are copied from the files, not
paraphrased.

### 2.1 P13 — `src/review_surface/` (the SPEC's own record, and the only one in `src/` that P13 owns)

Fields, `src/review_surface/records.py:38-51` — fourteen:

```
action_id  surface  subject_ref  plan_version  session_id  action
bulk_member_refs  bulk_basis  correction_scope  routed_to
presented_state_ref  payload  user_id  acted_at
```

Actions, `src/review_surface/vocabulary.py:76-84` — **eighteen**, not seventeen:

```
accept              accept_bulk            change_destination
return_to_accepted_group                   create_custom_folder
mark_private        defer                  leave_untouched
reject              edit_recommendation    disable_suggestion_type
refresh_plan        approve_for_apply      select_consent_option
set_redaction       adopt_version          restore_version
reset_learning
```

`74` §8 Q2 says "the P13 SPEC's seventeen actions". The SPEC's own block
(`planning/parts/P13-review-approval-surface/SPEC.md:266-273`) lists eighteen, the code publishes
eighteen, and `tests/p13/test_p13_vocabulary.py:36` is named
`test_the_eighteen_actions_are_the_spec_s_eighteen`. The count in Q2 is off by one. Nothing else in
Q2 depends on it.

Twelve surfaces, `src/review_surface/vocabulary.py:49-55`: `placement`, `group_plan`,
`residual_set`, `residual_file`, `canvas`, `apply`, `undo_conflict`, `consent`, `privacy_settings`,
`evaluation`, `learning`, `plan_version`.

### 2.2 P9 — `tests/p9/p13_fixtures.py`

Fields, `tests/p9/p13_fixtures.py:50-60` — eleven:

```
action  plan_version_id  group_id  membership_id  basis
user_edited_label  decided_at  user_id  correction_scope
presented_state_ref  surface (defaulted to "group_plan")
```

Actions, `tests/p9/p13_fixtures.py:18-26` — seven:

```
accept  edit  reject  defer  restore  reset-suggestion  exclude-from-packet
```

**This one has a live receiver in `src/`.** `src/grouping/learning.py:58-68` holds the same seven
names as a hardcoded dict mapping each to an acceptance state, a review state and a learning
polarity, and `apply_review_action` (`src/grouping/learning.py:103-175`) requires
`plan_version_id`, `group_id`, `decided_at` and `basis` by name.

### 2.3 P10 — `tests/p10/p13_fixtures.py`, and a second copy inside `src/`

Fields, `tests/p10/p13_fixtures.py:15-24` — ten:

```
review_action_id  surface  subject_ref  plan_version  action
correction_scope  presented_state_ref  user_id  observed_at  payload
```

The fixture publishes no action tuple at all; its names live only as keyword literals inside its six
factory functions, which is why the compatibility report reads them out of the source with `ast`
(`tests/p13/test_p13_fixture_compatibility.py:46-63`). The six it exercises are `accept`, `rename`,
`ignore`, `restore_version`, `add-scoped-general`, `set-shared-material-policy`.

**But the fixture is a sample, not the vocabulary.** P10's real user-action vocabulary is in `src/`
and is far larger — `src/tree_design/vocabulary.py`:

| tuple | line | members |
|---|---|---|
| `BRANCH_ACTIONS` (14) | 387-391 | `accept` `rename` `merge` `move-under-root` `defer` `create-manually` `add` `remove` `split` `nest` `reorder` `ignore` `drag-group-into-branch` `delete-suggested-area` |
| `EXISTING_FOLDER_ACTIONS` (6) | 402-405 | `preserve` `adopt-as-branch` `merge-with-proposal` `attach-beneath` `rename-proposal-to-match` `leave-untouched` |
| `TREE_EDIT_ACTIONS` (15) | 423-427 | `accept` `rename` `merge` `split` `nest` `re-parent` `reorder` `ignore` `delete` `create-manually` `adopt-existing` `enable-residual` `disable-residual` `add-scoped-general` `set-shared-material-policy` |
| `VERSION_ACTIONS` (2) | 434 | `adopt_version` `restore_version` |
| `RESIDUAL_LIBRARY_ACTIONS` (6) | 336-339 | `enable` `disable` `rename` `relocate` `merge` `replace-with-existing` |
| `DIMENSION_ACTIONS` (6) | 140-141 | `selected` `omitted` `reordered` `flattened` `renamed` `added` |

The union of the first four is **29 distinct names**, of which exactly four are also P13's: `accept`,
`defer`, `adopt_version`, `restore_version`.

P10 also publishes its own three-member surface list, `tree_design.provenance.REVIEW_SURFACES` =
`canvas`, `plan_version`, `unattended`. The third is not one of P13's twelve, deliberately — §5.

And the field shape is duplicated in `src/`: `src/tree_design/pipeline.py:439-457` defines a private
`_Action` dataclass whose docstring says *"P13's `review_action`, as P13's SPEC publishes its fields
… `tests/p10/p13_fixtures.py` declares the same shape for the same reason; this is `src/`'s copy
because a source module may not import a test one."* It carries `review_action_id` and `observed_at`,
which are not the SPEC's names. **This is the point at which the disagreement stops being test-only.**

### 2.4 P11 — `tests/p11/p13_fixtures.py`

Fields, `tests/p11/p13_fixtures.py:33-46` — thirteen, and they are P13's fourteen minus `routed_to`
(which `routing.route` fills, so a fixture must not carry it):

```
action_id  surface  subject_ref  plan_version  session_id  action
bulk_member_refs  bulk_basis  correction_scope  presented_state_ref
user_id  acted_at  payload
```

Actions, `tests/p11/p13_fixtures.py:25-29` — eleven, a declared **subset** of P13's eighteen with the
seven omissions named in the comment above them:

```
accept  accept_bulk  change_destination  return_to_accepted_group
create_custom_folder  mark_private  defer  leave_untouched  reject
edit_recommendation  disable_suggestion_type
```

The same eleven are in `src/placement/vocabulary.py:322-328` as `REVIEW_ACTIONS`, and
`src/placement/review.py:48-49` imports them rather than respelling them.

### 2.5 One line each

- **P13** — 14 fields, 18 actions, 12 surfaces. The SPEC's record; the only one that owns `session_id`, `bulk_member_refs`, `bulk_basis` and `routed_to`.
- **P9** — 11 fields, 7 actions, 1 surface. Names the identity by *what was acted on* (`group_id` + `membership_id`) rather than by a `subject_ref`, and carries `basis` and `user_edited_label` that no other list has.
- **P10** — 10 fields in the fixture, 29 action names across four live tuples in `src/`. Overlaps P13 on four names, spells one of them differently, and has no `session_id`, `bulk_member_refs` or `bulk_basis` at all.
- **P11** — 13 fields, 11 actions. A strict subset of P13 with `routed_to` correctly absent. It is the only one that matches.

---

## 3. Where each came from, and why they differ

These have different implications and they do differ per fixture. `69` §3a already tabulated the
three identity fields and three timestamps; what follows is the part `69` did not establish — whether
each was an invention, a good-faith reading, or a real requirement the SPEC then failed to cover.

### 3.1 P11 — a faithful transcription, and it says so

`tests/p11/p13_fixtures.py:1-11` cites `P13 SPEC:247-279` for the field list and `P13 SPEC:294` for
the four surfaces, and the omitted-actions comment (`:22-24`) names the seven that route elsewhere.
It was written on 2026-08-28 (`1458c24`), after the P13 SPEC existed. There is nothing to reconcile
here; P11 is the control case.

### 3.2 P9 — an invention, and it contradicts P9's own SPEC as well as P13's

This is the finding that most changes the shape of Q2.

**P9's own SPEC already publishes P13's field names.** `planning/parts/P9-grouping/SPEC.md:125-129`,
Contract-in, reads: *"Those gestures reach P9 as P13's `review_action` in full, collected on
`surface = group_plan` with `subject_ref` a `group_plan_id`, and carrying `plan_version`, `action`,
`bulk_member_refs[]`, `bulk_basis`, `correction_scope` (§8.7) and `presented_state_ref`."* That is
P13's spelling, in P9's SPEC, including `bulk_member_refs` and `bulk_basis`.

The fixture ignores it. `plan_version_id`, `group_id`, `membership_id`, `basis`, `decided_at` and
`user_edited_label` appear in neither P9's SPEC nor P13's, and `subject_ref`, `session_id`,
`bulk_member_refs` and `bulk_basis` are all absent. The fixture was frozen on 2026-08-26 (`7d5aae8`,
"P9 Task 3 … the two stand-ins"), before P13's SPEC record was published.

**The action names are a third list again.** P9's SPEC names the gestures at
`planning/parts/P9-grouping/SPEC.md:123`: *"Accept, reject, rename, merge, split, exclude-one-member,
manually attach."* The fixture publishes `accept, edit, reject, defer, restore, reset-suggestion,
exclude-from-packet` — `rename` became `edit`, `exclude-one-member` became `exclude-from-packet`, and
`merge`, `split` and `manually attach` are simply not there, while `defer`, `restore` and
`reset-suggestion` appear from nowhere in either SPEC. Of those three, `defer` has an obvious home
(P9's own `deferred` acceptance state, SPEC:154) and `restore` and `reset-suggestion` do not; I could
find no design sentence for either, and I read §7.10, §8.7 and §8.8. **Inference:** `restore` is
`restore_version` applied at group scope and `reset-suggestion` is a group-level cousin of
`reset_learning`; I could not confirm this from any document.

**The divergence was known and recorded at the time.** The commit that built P9's receiver
(`1a869ec`, 2026-08-27) says in its own message: *"The plan's Step 1 also names merge, split and
manual attach; the fixture publishes seven actions and none of those three is among them, so they are
not implemented here and the discrepancy is between the plan's prose and the contract Task 3 froze."*
So P9 is an invention that was noticed, written down, and built on anyway — which is exactly how a
frozen fixture becomes a de facto contract.

### 3.3 P10 — a good-faith reading of design prose that the P13 SPEC does not cover

P10's fixture names are not invented. Every one traces to a sentence:

| P10 name | design sentence |
|---|---|
| `accept`, `rename`, `merge`, `move-under-root`, `defer`, `create-manually` | `01`:856-857 — *"The user can choose to accept a proposed branch, rename it, merge it into another branch, move it under an existing root such as Documents, defer it, or create a new branch manually."* |
| `drag-group-into-branch`, `delete-suggested-area` | `01`:837-839 — *"The user can drag an accepted group into a top-level branch, merge Applications with Career … or delete a suggested top-level area entirely."* |
| `preserve`, `adopt-as-branch`, `merge-with-proposal`, `attach-beneath`, `rename-proposal-to-match`, `leave-untouched` | `01`:864-865 and `01`:1037-1039 — the six things a person may do to an existing folder |
| `add-scoped-general` | `00`:99, quoted in full at `tests/p10/p13_fixtures.py:69-82` |
| `set-shared-material-policy` | §6.9, the file that belongs in two places |

**And the P13 SPEC does not cover any of them.** It lists `canvas` as one of its twelve surfaces
(SPEC:249) and routes canvas actions to P10 (SPEC:295, the N-1 table row for P10), but its
eighteen-action list contains no canvas gesture whatsoever — the P10 row says only that *"§8.8's
compare, restore and adopt arrive as `action = adopt_version | restore_version`."* The SPEC is
**silent** on what a person does on the canvas beyond accepting. It is not that P10 read the SPEC
wrongly; there was nothing there to read.

`74` already half-knows this. §8 Q4 asks the same question about `EXISTING_FOLDER_ACTIONS` versus
`TREE_EDIT_ACTIONS` and `74`:290-292 says *"`TREE_EDIT_ACTIONS` has fifteen members and none of them
is one of the six, so P13's canvas surface cannot today route a `leave-untouched` anywhere."* **Q2
and Q4 are one question.** Ruling on Q2 without Q4 leaves the canvas half unresolved either way.

### 3.4 The one that is a plain misspelling

P10's `leave-untouched` (`src/tree_design/vocabulary.py:398`) and P13's `leave_untouched`
(`src/review_surface/vocabulary.py:64`) are the same gesture, hyphen against underscore, in two live
`src/` vocabularies, both green. This is the `scan_state` defect (`69`:68-73) exactly — two parts, two
spellings of one thing, each correct in its own vocabulary — and it is the only member of the
disagreement that is unambiguously a defect rather than a decision.

---

## 4. What actually breaks today

Honest answer first: **nothing a person can see today breaks, because no `review_action` P13 collects
reaches any receiver.** That matters for urgency and it is stated plainly. What is *already* wrong is
narrower and further upstream than the vocabulary argument suggests.

### 4.1 P13 routes to a name, never to a function

`src/review_surface/routing.py:101-113` — `route(surface, action)` returns a tuple of part
identifiers (`"P9"`, `"P10"`, …). `collect` (`src/review_surface/collect.py:102-110`) stamps that
tuple onto `routed_to` and appends the `review action routed` event. Nothing in `src/review_surface/`
imports `grouping`, `tree_design` or `placement`, and nothing calls their `apply_review_action`. The
delivery seam does not exist. This is deliberate — the SPEC's routing table is a contract about
ownership, not a dispatch table — but it means the disagreement is currently costless at run time.

### 4.2 What happens the moment it does exist — run, not asserted

I built P13's real `ReviewAction` and handed it to each of the three live receivers
(`/private/tmp/.../scratchpad/seam_probe.py`, read-only, no repo file touched):

```
P9   grouping.learning.apply_review_action(group_plan/accept)
     -> ReviewActionRefused: plan_version_id is required on a review action and P9
        supplies no default.

P10  tree_design.store.apply_review_action(canvas/accept, project=None)
     -> AttributeError: 'ReviewAction' object has no attribute 'review_action_id'

P10  tree_design.store.apply_review_action(canvas/edit_recommendation)
     -> OutOfVocabulary: tree edit action is not one of the 15 values P10 defines
        for it. Adding a member is a contract revision, not an implementation decision.

P11  placement.review.apply_review_action(placement/accept)
     -> reached the function body; both gates passed. (The probe then failed inside
        my own stub decision factory, which is the probe's fault, not P11's.)
```

P9 refuses with a named class. P10 raises a **bare `AttributeError`** — not a refusal, not a message
a person or a log could act on. P11 accepts it. That is the xfail's `([], [])` result made concrete.

And the block is symmetric: `review_surface.vocabulary.check` refuses `rename`, `ignore`,
`add-scoped-general`, `set-shared-material-policy`, `edit`, `restore`, `reset-suggestion` and
`exclude-from-packet` with `OutOfVocabulary`, so P13 cannot *emit* the gestures P10 and P9 can
*apply*, and P10 cannot apply the gestures P13 can emit. The canvas seam is closed in both directions.

### 4.3 What is already reaching a real run, and it is not nothing

`src/production.py:712` calls `design_tree`, which is on the live `cli.py` path. Inside it,
`src/tree_design/pipeline.py:872-878` **manufactures** an `_Action` — `review_action_id=f"ra_accept_{…}"`,
`action=ACCEPT` — and passes it to `apply_review_action`, which writes a `destination-tree edit`
event. So every real run today writes review-action-shaped provenance for a gesture no person made.

P10 handles that honestly and the handling is worth the owner seeing, because it is a partial answer
to this whole question already in the repo. `src/tree_design/provenance.py:62-77`, `actor_phrase`:

> *"Every §8.2 sentence P10 writes opened with 'The user', because until P13 ships there was no way to
> say otherwise. On `SURFACE_UNATTENDED` that is false — nobody was shown the tree and nobody approved
> anything — and the sentence goes into a permanent log beside the real login name `--user` supplied.
> 'The rules' is what actually decided."*

That is the north star being served without a ruling: a gesture with no screen is recorded as made by
the rules, on an `unattended` surface, rather than attributed to a person who was not there.

### 4.4 The cost that is real today, and is not about modules

Six gestures the design names in §8.7 as things it must learn from — `01`:1843-1846, *"accepting or
rejecting a group, excluding one member from a packet, renaming a branch, merging or splitting
groups, changing template order, creating a custom template, moving a residual file to a custom
location, choosing a shallow fallback, keeping a file in place, marking a file private, or disabling a
type of suggestion"* — have **no P13 action to be collected as**:

| §8.7 gesture | P13 action |
|---|---|
| accepting / rejecting a group | `accept` / `reject` ✓ |
| **excluding one member from a packet** | **none** (P9 has `exclude-from-packet`) |
| **renaming a branch** | **none** (P10 has `rename`) |
| **merging or splitting groups** | **none** (P10 has `merge`, `split`) |
| **changing template order** | **none** (P10 has `reorder`) |
| **creating a custom template** | **none** (P10 has `create-manually`; `create_custom_folder` is a node, not a template) |
| moving a residual file to a custom location | `change_destination` / `create_custom_folder` ✓ |
| **choosing a shallow fallback** | **none** — and `src/tree_design/pipeline.py:460-472` says so outright: *"there is no `set-refinement-disposition` review action"* |
| keeping a file in place | `leave_untouched` ✓ |
| marking a file private | `mark_private` ✓ |
| disabling a type of suggestion | `disable_suggestion_type` ✓ |

The last column's "none" entries are the answer to the brief's real question. **P13's eighteen is not
the complete list of what a person can do; it is §7.10's residual-review sentence
(`01`:1501-1503, which supplies eight of the eighteen almost verbatim) plus the §8.3/§8.4/§8.8
machinery actions.** It is a faithful reading of one paragraph, and the design has three other
paragraphs of gestures — §5.1, §5.2, §5.10 for the canvas and §8.7 for the correction list — that it
does not cover.

The P13 SPEC's own Open question 10 (SPEC:641-645) concedes the same shape for a different screen:
*"no section names that screen's **action set**, which is what P13 would have to present and
collect."* It does not raise the canvas equivalent. **That omission is, in my reading, the actual
defect behind Q2** — and I mark it as a reading, not a fact.

### 4.5 What is *not* broken

- The compatibility report is doing its job. `tests/p13/test_p13_fixture_compatibility.py` is a strict xfail with two live twins: widening or narrowing makes it XPASS (which fails a strict xfail), deleting the fixtures makes it ERROR (which also fails). Verified by running it.
- P11 needs no change under any option.
- `correction_scope` is imported from P1 by all of them and is not part of this disagreement (`src/review_surface/vocabulary.py:16`).
- The suite is green: 6135 tests collect, and the report xfails as designed.

---

## 5. The three resolutions `74` names, costed

`74` §8 Q2 asserts these are "three different products". Concretely, here is why.

### Option A — Widen P13's eighteen to absorb P9's and P10's names

**What moves.** `src/review_surface/vocabulary.py:56-84` gains members and one named constant each.
`tests/p13/test_p13_vocabulary.py:36` (`test_the_eighteen_actions_are_the_spec_s_eighteen`) and `:47`
(`test_every_action_the_spec_prints_is_present`) both fail by construction, because they assert
against the SPEC's printed list — so the **SPEC block itself must be edited**, which is a contract
revision. `src/review_surface/routing.py:82-97` needs an `ACTION_ROUTING` row per new member or the
gesture routes only by surface. The compatibility xfail XPASSes and must be retired.

**What has to be re-tested.** `tests/p13/` — 21 collect tests, 14 routing, 11 vocabulary — plus every
`no_invention` guard that walks the vocabulary.

**What becomes impossible.** Nothing structurally. But the eighteen stop being "§7.10's sentence plus
the machinery" and become a union of whatever each receiver happened to name, including `edit` and
`rename` as two names for the same gesture and `restore`/`restore_version` as two more. It also
imports P9's inventions — `reset-suggestion` and `restore` — into the SPEC, which is the one thing
no evidence supports.

**What a person would notice.** Nothing directly. Indirectly, the review screen's action list is what
a person is *offered*, and a union list offers `rename` and `edit` as separate choices.

### Option B — Narrow P9's and P10's to P13's eighteen

**What moves.** P9: `src/grouping/learning.py:58-68` (seven mappings), `:103-175` (six required field
names), `tests/p9/p13_fixtures.py` deleted or replaced, ~15 fixture call sites across
`tests/p9/test_p9_learning.py` (23 tests) and `tests/p9/test_p9_fixtures.py` (25 tests). P10:
four tuples in `src/tree_design/vocabulary.py`, `src/tree_design/store.py:462-611` (eight attribute
names and two vocabulary gates), `src/tree_design/pipeline.py:439-457` (`_Action`) and its three
construction sites, `tests/p10/test_p10_versions.py` (41 tests, 25 fixture call sites), plus
`tests/integration/test_p10_p11_live_seam.py` and `test_p10_p6_materialise.py`.

**What has to be re-tested.** P9's and P10's whole receiver surface plus two integration seams — on
the order of 130 tests directly, and the live `production.py` path, which is where `_Action` is built.

**What becomes impossible.** This is the decisive cost and it is not a refactor: **narrowing deletes
gestures that have no P13 equivalent.** `exclude-from-packet` is §8.7's *"excluding one member from a
packet"*, named verbatim in the design. `rename`, `merge`, `split`, `reorder` and `create-manually`
are §5.1/§5.2/§8.7's, named verbatim. Narrowing to eighteen would mean a person **cannot rename a
branch**, and there would be no record of the gesture even if they could. That is not a vocabulary
change; it is a product decision to remove functions the design promises.

**What a person would notice.** If narrowing is done literally, the canvas loses most of what §5.1
and §5.2 say it does. If it is done by first widening P13 to cover them, it is Option D.

### Option C — A translation table

**What moves.** A new module mapping each part's names onto P13's, plus a symmetric field-name map.
Every receiver's front door reads through it. `74`:490 already rules this out at plan level — the
"not building" table says an `review_actions` translation shim across the four vocabularies is
exactly what Wave A4 declined, *"a failing **report**, not a shim that hides the disagreement."*

**What has to be re-tested.** All three receivers plus the table's own guards.

**What becomes impossible.** Nothing — that is the objection. A table makes both spellings correct
forever, so `leave-untouched`/`leave_untouched` never gets fixed, it gets institutionalised. It also
gives every future gesture two homes, which is this project's most expensive named defect class
(`src/review_surface/vocabulary.py:4-6`: *"Never a bare string in another module — a literal is a
second home for a vocabulary and this project's most expensive defect class."*)

**What a person would notice.** Nothing, until two spellings drift in meaning and a correction stored
under one is never read back under the other — the `scan_state` failure, where five thousand passing
tests agreed with a production path that could not work (`69`:68-73).

---

## 6. Options nobody has written down

The brief asked whether there is a fourth. There are three, and one of them is already shipped
practice in this repo.

### Option D — The SPEC's action list is incomplete; derive it once from the design, then narrow

Not "widen P13 to absorb P9's and P10's spellings" (Option A) but: **go back to §5.1, §5.2, §5.10,
§7.10 and §8.7, derive the complete list of gestures the design names, publish that as P13's action
vocabulary, and then Option B follows mechanically** — because after the derivation there is nothing
left in P9's or P10's sets that P13 cannot express.

The evidence for treating this as a defect repair rather than a preference: §4.4's table shows six
§8.7 gestures with no home; §3.3 shows P13's canvas surface has no canvas gesture; SPEC Open question
10 already concedes the same failure for the version-family screen. Under this reading the eighteen
is not *the* list, it is §7.10's paragraph.

**Cost.** Everything Option B costs, plus a SPEC amendment, plus resolving Q4 in the same motion —
which is a saving, not an extra, since Q4 cannot be closed without it. It would also settle `restore`
and `reset-suggestion`: neither survives a derivation from the design, because no design sentence
names them.

**What becomes impossible.** Nothing the design promises. It closes the door on `edit`
(§8.7 says "renaming a branch", so `rename` wins) and on P9's identity fields (the design never names
them; P9's own SPEC already uses P13's).

### Option E — Payload-carried sub-gestures, which P13 already does

`src/review_surface/move_permission.py:30-34` faced exactly this question three weeks of commits ago
and answered it without a ruling:

> *"The gesture is collected as `mark_private`, which is P13's one action about a file's privacy
> standing and which already routes to P7 and P6 jointly. Minting a nineteenth action would be a
> SPEC-level act: the eighteen are the SPEC's own list and adding a member to a closed vocabulary
> requires owner approval recorded at the member. The action's payload says which way the permission
> was set."*

Generalised: a canvas edit is collected as one `edit_recommendation` (or a new single
`tree_edit` member) whose `payload` names which of P10's twenty-nine it was, and P10 validates the
payload against its own vocabulary — which it already owns and already publishes.

**Cost.** Small: `payload` is already a free `Mapping` and P10's tuples stay where they are. One new
member at most.

**What becomes impossible.** Routing by action stops working for canvas gestures —
`routing.ACTION_ROUTING` (`src/review_surface/routing.py:82-97`) dispatches on the action *name*, so
a payload-hidden gesture routes only by surface, and §7.10's create-a-custom-folder-during-residual-
review case (the one the routing docstring opens with, `routing.py:5-9`) is precisely a gesture that
must route by action to two parts at once. It also weakens the §8.7 learning story: a `payload` key is
not a closed vocabulary, and *"the same attractive but incorrect conclusion"* is suppressed by
matching on what the user did.

**What a person would notice.** Nothing on the screen. On the learning surface (§8.7's inspect-and-
reset view, which P13 builds at `src/review_surface/learning_view.py`), corrections would be listed by
an action name that does not say what they did.

### Option F — The null option: rule nothing, keep the report

`74` §8 Q2's own disposition — *"Wave A4 ships the report; the fix waits"* — is a real option and
should be priced. The report is a genuine two-way negative twin (§4.5) and the seam it guards does not
exist yet (§4.1). Nothing regresses if this stays open.

**Cost.** P13 Wave B's canvas routing cannot be built, `74` §8 Q4 stays open with it, and
`src/cli.py`'s defaulted existing-folder decision stays defaulted (`74`:430). P9's integration swap —
*"a required integration test when P13 ships"*, `tests/p9/p13_fixtures.py:9-11` — cannot be written.
And `leave-untouched`/`leave_untouched` stays shipped in two spellings.

---

## 7. What is fixed, and what is genuinely open

**Fixed. A ruling has to live inside these.**

- Adding a member to a closed vocabulary requires owner approval recorded at the member (`src/review_surface/move_permission.py:33-34`; the same sentence in `src/grouping/vocabulary.py:270`, `src/tree_design/vocabulary.py:613-617`, `src/placement/vocabulary.py:432`). Options A, D and E all require it; B and C do not.
- `correction_scope` is P1's, imported and never respelled (`src/review_surface/vocabulary.py:16`). Untouched by every option.
- A protected container carries **no action at all** — not a surface, not an action (`src/review_surface/vocabulary.py:118-122`, enforced at `collect.py:85-92`). No option may give it one.
- Bulk actions enumerate members and never carry a filter (SPEC:274-276; `collect.py:91-96`; `review.py:237-242`). Any narrowing that drops `bulk_member_refs` from P9's or P10's shape re-opens this.
- P13 decides nothing; the receiving part decides what a gesture means (SPEC:282-287). A translation table sitting inside P13 would violate this; one sitting at each receiver's front door would not.

**Open, and this document does not fill it.**

- Whether §5.1/§5.2/§5.10's canvas gestures are `review_action`s at all, or a separate collection surface. `74` §8 Q4 asks this and neither SPEC answers it.
- Whether `restore` and `reset-suggestion` (P9) name anything the design has. I found no sentence for either.
- Whether "creating a custom template" (§8.7) and `create_custom_folder` (§7.10) are one gesture or two. They read as two; the SPEC does not say.
- What `session_id` means for a gesture P9 or P10 receives — neither part has the concept, and the SPEC defines it only as *"the sitting this action belongs to"* (SPEC:255).

---

## 8. The questions the owner must answer

**Q1 is the ruling. The rest are what an implementer needs immediately after it.**

**Q1. Is P13's eighteen the complete list of things a person can do, or is it §7.10's paragraph
written down?**
This decides everything else. "Complete" selects Option B or C and accepts that six gestures §8.7
names go unrecorded. "Incomplete" selects Option D and makes this a SPEC amendment rather than a
module reconciliation.

**Q2. May a person rename a branch on the canvas, and if so, what is that gesture called?**
`01`:856 says they may. P13 has no action for it, P10 has `rename`, P9 has `edit`. One name, chosen
once, settles the largest single overlap. Answering this alone unblocks most of Wave B.

**Q3. Do canvas gestures travel as `review_action`s, or is the canvas a second collection surface?**
This is `74` §8 Q4 restated, and it cannot be separated from Q1 — ruling on one without the other
leaves the canvas half open either way. If they are `review_action`s, P13's list must grow by roughly
twenty-nine names or adopt Option E's payload.

**Q4. `leave-untouched` or `leave_untouched`?**
The one plain defect. It needs no product judgement, only a pick, and the loser's spelling is deleted.

**Q5. Are `restore` and `reset-suggestion` (P9) real gestures?**
If they name nothing in the design, they are deleted with P9's fixture. If they are real, they need a
design sentence recorded at the member. I could not find one.

**Q6. Does `exclude-from-packet` survive?**
§8.7 names it verbatim. It is the clearest case of a gesture P9 got right and P13 does not carry, and
it is the test of whether "narrow P9" is a rename or a removal.

**Q7. When the seam is built, may P9 keep its own field names behind a translation at its own front
door, or must `src/grouping/learning.py` read P13's record directly?**
The difference is roughly 130 tests and whether `basis` and `user_edited_label` survive. Note that
P9's *own SPEC* already says the record arrives in P13's spelling
(`planning/parts/P9-grouping/SPEC.md:125-129`), so a translation here contradicts P9's contract, not
just P13's.

---

## 9. My judgement, kept separate from the evidence above

The owner asked for the decision to be made easy, not made. Nothing below is a ruling and nothing
below was applied to any file.

**The strongest option on the evidence is D — treat P13's eighteen as an incomplete reading of §7.10,
derive the complete gesture list from §5.1, §5.2, §5.10, §7.10 and §8.7 once, and let the narrowing of
P9 and P10 follow from it.** Four reasons.

First, it is the only option under which §4.4's table has no "none" rows. Every other option leaves at
least six gestures the design names in its own words with nowhere to be recorded, and the north star
here is not which module wins — it is whether a gesture a person made gets recorded truthfully. A
gesture with no action name is not recorded at all.

Second, it explains the disagreement instead of arbitrating it. P9 invented (§3.2, and the commit
message admits it). P10 read the design correctly and found the SPEC silent (§3.3). P11 transcribed
the SPEC (§3.1). Those are three different situations and Options A, B and C treat them as one.
Widening absorbs P9's inventions along with P10's legitimate readings; narrowing deletes P10's
legitimate readings along with P9's inventions.

Third, it closes `74` §8 Q4 in the same motion, which no other option does, and Q4 cannot be closed
separately — `74`:290-292 already established that the six existing-folder gestures have no writer
because P13's canvas surface cannot route them.

Fourth, it is the option that leaves one home per vocabulary. C institutionalises two. E hides the
second home inside a `payload` key that is not a closed vocabulary and breaks routing-by-action, which
is the SPEC's stated whole contract (`routing.py:1-9`).

**What I would not do.** I would not take Option A as stated in `74` §8 Q2 — "widen P13's set" reads
as absorbing the other two lists, and P9's `restore` and `reset-suggestion` have no design sentence
behind them, so absorbing them would put two invented members into a closed vocabulary by the same
mechanism that produced this problem.

**What I am least sure of.** Whether the canvas belongs in `review_action` at all (Q3). P10's
`unattended` surface and its `actor_phrase` ruling (§4.3) suggest a part that has already built a
truthful provenance story for canvas edits without P13, and it is possible the right answer is that
the canvas is P10's own collection surface and P13 collects only the twelve-surface review flow. I
found no evidence either way and did not build the case, because Option D and that reading diverge
only after Q3 is answered.

**Urgency.** Low today (§4.1: nothing user-visible breaks) and rising sharply at one specific moment:
the first time anything calls a receiver's `apply_review_action` with P13's record. Two of the three
receivers refuse it, and one of those two refuses with a bare `AttributeError` (§4.2). If P13 Wave B
builds the canvas routing before this is ruled, that is the moment.

---

## 10. What this document did not do

- It did not change any vocabulary, test, manifest or source file. The only file written is this one.
- It did not run the full 6135-test suite; it collected it, and ran `tests/p13/test_p13_fixture_compatibility.py` (2 xfail, 2 pass) plus four read-only probes against the three receivers.
- It did not enumerate P10's `RESIDUAL_LIBRARY_ACTIONS` (6) or `DIMENSION_ACTIONS` (6) as part of the reconciliation. Both are P10-internal — a library edit before freeze and a catalogue-level rename — and neither claims to be a `review_action`. If Q3 answers that the canvas is a `review_action` surface, they should be re-checked; I did not.
- It did not investigate P7's or P12's ends of the routing table. The SPEC's N-1 rows for both (SPEC:296-297) name only actions P13 already has, so neither is part of this disagreement, but I did not verify their receivers the way I verified P9's, P10's and P11's.
- It did not answer any of §8's questions.

---

# Second pass — 2026-08-31, after P13 Wave B landed

Sections 1-10 were written and committed (`fdb8b3a`) before Wave B completed its fourteen tasks and
before `build-p12-waveG` began the P12↔P13 seam. Two things now exist that did not, and both bear
directly on §4 and on the fourth option §6 was asked to look for. **Nothing in §1-§10 is retracted;
§11 and §12 add to it and §13 replaces §9.**

---

## 11. The rule this project already has, and never applied to an action name

This is the finding that most changes the question, and it is the same move `80` §2 made: the answer
is implied by the rest of the design, and the project has been treating a **scope gap in an existing
rule** as though it were a new rule needing invention.

### 11.1 MINOR 6 and MINOR 7 are ratified, and they answer a four-way disagreement by construction

**MINOR 7 — *"one vocabulary for one concept"*** (quoted at
`planning/parts/P11-placement-residual/SPEC.md:410-411`).

**MINOR 6 — the owning part names it; everyone else carries it verbatim.**
`planning/parts/P10-tree-design-freeze/SPEC.md:263-265`:

> *"`node_role` is the single vocabulary for a node's kind (MINOR 6). P10 owns the tree, so P10 names
> its node kinds; P11 carries `node_role` verbatim on the destination it names and publishes no
> parallel vocabulary of its own."*

`74` §8 Q2 asks which of four vocabularies for one record should win. **MINOR 7 already forbids the
question from having four answers, and MINOR 6 already supplies the tie-breaker: ownership, not
seniority and not majority.** Neither is cited anywhere in `74` §8, in the P13 SPEC's `review_action`
block, or in any of the three fixtures.

### 11.2 The rule has already been applied to this exact pair of parts, through this exact lifecycle

`src/placement/vocabulary.py:124-141` is the same problem, already solved, and it records its own
history:

> *"P10's vocabulary, carried verbatim on the node (SPEC:322-323, MINOR 6) … **This block spelled the
> values from P10's SPEC while P10 was unbuilt, and said in this comment that it would become a
> re-export the day P10 published them. P10 has, so it is one.***
>
> *The three closed sets are P10's OBJECTS, not tuples that agree with P10's. A tuple that merely
> agrees is one P10 edit away from disagreeing … A distinct name bound to P10's object is carrying; a
> distinct name bound to a fresh string is the parallel vocabulary MINOR 6 forbids."*

That is a five-step lifecycle the project has already run to completion:

1. Part B needs Part A's vocabulary before Part A exists.
2. Part B spells it locally, **with a comment saying it will become a re-export**.
3. Part A ships and publishes.
4. Part B's local spelling becomes a re-export of Part A's objects.
5. A distinct *name* bound to the owner's *object* is legitimate; a distinct name bound to a fresh
   string is not.

**The three `p13_fixtures.py` files are step 2, frozen past step 3.** P13 published on 2026-08-30
(`95d0ee5`). Nothing has taken step 4.

### 11.3 And one part is now at step 3 with a fresh-string copy still in place — verified today

`src/placement/review.py:46-49` says:

> *"P13 SPEC:294 — the surfaces whose actions route to P11. Imported, not re-spelled:
> `placement/vocabulary.py` is the one home for a value P13 owns and **has not yet published**, and
> two copies of one vocabulary is how a surface P13 renames becomes a surface P11 silently refuses."*

The clause "has not yet published" was true when written and is false now. `src/placement/vocabulary.py:305-328`
still defines eleven `ACTION_*` constants as **fresh strings** and assembles them into `REVIEW_ACTIONS`,
and `src/placement/review.py:37-45` imports them from there rather than from `review_surface.vocabulary`.
Verified: no module under `src/placement/`, `src/grouping/` or `src/tree_design/` imports
`review_surface` at all.

The values still agree (checked: P11's eleven actions and four surfaces are both proper subsets of
P13's eighteen and twelve). **They agree the way `scan_state` agreed until it did not** — and
`src/placement/vocabulary.py:130-133` makes the argument against itself, two hundred lines above the
offending block: *"A tuple that merely agrees is one P10 edit away from disagreeing."*

This is a live instance of the defect, in `src/`, on the one part everybody agrees got it right. It
was not in §1-§10 because it did not exist in the same form before Wave B; it is reported here rather
than fixed, because P11's eleven are a closed vocabulary and this document changes none.

### 11.4 What MINOR 6 implies here — and the one thing it does not settle

Applying MINOR 6 to actions requires knowing who owns the concept *an action name*, and **the design
supports two readings.** Both are stated; neither is adopted.

**Reading (i): P13 owns every action name, because `review_action` is P13's record.** P9, P10 and P11
carry verbatim. This makes §5's Option B mechanical for P11 (already a subset) and forces §6's Option
D for P9 and P10, because P13's eighteen cannot express `rename` or `exclude-from-packet` (§4.4).

**Reading (ii): the part that APPLIES the gesture owns its name, and P13 carries verbatim.** The SPEC
says so in its own words at `planning/parts/P13-review-approval-surface/SPEC.md:282-283`: *"P13 hands
the action to the owning part and **that part decides what it means**."* Under (ii) a `rename` is
P10's word because P10 is the part that renames, and P13's `ACTIONS` becomes an assembly of imports:
P11's eleven, P10's canvas names, P9's group names — **each imported from its owner, none invented by
anybody.**

Reading (ii) is mechanically available today. P13 already imports `placement.vocabulary`,
`tree_design.records`, `tree_design.store`, `tree_design.diff` and `tree_design.user_edits`
(verified by grep over `src/review_surface/`), and no part imports `review_surface` back, so the
carry direction is the established one and creates no cycle. I confirmed all four vocabulary modules
import together in one interpreter.

**What decides between (i) and (ii) is not in any document I read.** MINOR 6 says the owner of the
concept names it; it does not say whether the concept behind `rename` is *"a gesture collected on a
review surface"* (P13's) or *"an edit to the tree"* (P10's). That is the owner's, and it is now Q1'
in §13.

---

## 12. The fourth option, and it is already shipped and green

`74` Wave G1 says *"Re-point P13's `apply_seam` at the real P12 records and delete
`tests/p13/p12_fixtures.py`"* (`74`:393). The reasoning generalises, and it generalises further than
expected, because of one fact:

**`tests/p13/p12_fixtures.py` never existed.** `git log --all -- tests/p13/p12_fixtures.py` returns
nothing, and `tests/p13/` contains no fixture module. It was not deleted; **it was never needed.**

### 12.1 What P12 and P13 did instead, and it worked

Two dataclasses, one per part, each declaring the SPEC's field list in the SPEC's spelling:

- `src/review_surface/records.py:98` — P13's `ReviewApproval`, the record it produces.
- `src/mutation/approval.py:77-95` — P12's `ReviewApproval`, whose docstring reads: *"P13's record, as
  P12 reads it (SPEC, Contract in -> From P13). P12 never constructs one in production … The
  dataclass exists here because P12 must be able to state what it requires of the record."*

**Their field lists are identical — nine fields, same names, same order — and I verified it by
reflection, not by eye.** Neither module imports the other (verified). They match because both were
derived from the same SPEC block, independently.

And the seam is proven by running the real chain, not by a fixture.
`tests/integration/test_p12_p13_seam.py:285-315`,
`test_an_approval_p13_recorded_is_what_p12s_gate_reads`, says so in its own docstring: *"Not a fixture
and not a hand-built `ReviewApproval`: the record is collected through P13's own writer, stored in
P13's own table, read back through P13's own reader, and handed to P12's gate."*

### 12.2 Stated as an option

**Option G — the receiver declares what it requires; the producer produces the SPEC's record; an
integration test running the real chain is what holds them together.** No fixture, no shim, no
translation table, and no central vocabulary merge. The three `p13_fixtures.py` files are deleted when
the seam is built, exactly as `74` Wave G1 intends for a file that turned out never to be necessary.

**What moves.** For P11: nothing but the deletion (§2.4 — its fixture is already the SPEC's shape, and
§11.3's fresh-string copy would become a re-export). For P9 and P10: the receivers keep their own
typed declaration of what they require, and it is written **from the SPEC** rather than from the
frozen fixture — which is the whole of the work, because P9's declaration currently contradicts P9's
own SPEC (§3.2).

**What has to be re-tested.** One new integration test per seam, of the kind
`test_p12_p13_seam.py:285` already is. The ~130 unit tests in §5's Option B still move, because they
construct fixtures.

**What it does NOT solve, and this is the honest limit.** Option G is a mechanism for making two
parts agree about a record *whose field list the SPEC states*. It settles every field-name
disagreement in §2 at a stroke — P9's `plan_version_id`/`decided_at`/`basis` lose, because the SPEC
and P9's own SPEC both say otherwise. **It settles nothing about the action names**, because P12 and
P13 converged only where the SPEC spoke, and for the canvas the SPEC does not speak (§3.3). Option G
plus a silent SPEC reproduces exactly today's situation one layer down.

### 12.3 What the P12 seam proves about the cause of the disagreement

Three independent derivations, three outcomes, and the pattern is clean:

| | derived from | outcome |
|---|---|---|
| P12's `ReviewApproval` | the SPEC | matches P13 exactly, nine of nine fields |
| P11's `p13_fixtures.py` | the SPEC, cited by line | matches P13 exactly |
| P9's `p13_fixtures.py` | neither SPEC; frozen at Task 3 | eleven fields, four of them in no SPEC |
| P10's `p13_fixtures.py` | `01` §5.1/§5.2/§5.10, faithfully | matches nothing, because the SPEC is silent there |

**Where the SPEC speaks, independent derivation converges — twice, with no coordination.** So this is
not a four-way disagreement with four defensible sides. It is **two defects with two different
causes**: one part invented (P9), and one part had nothing to read (P10). They need different repairs,
and §5's three options all apply one repair to both.

---

## 13. Revised questions and judgement

§11 and §12 change what the owner has to decide. **§13.1 replaces §8 and §13.3 replaces §9.** §8's
Q4-Q7 survive as consequences and are marked below where they stop being separate decisions.

First, one claim from §4 re-checked against the current tree, because Wave B landed after it was
written: **§4.1 still holds.** P13 now imports P10's and P11's *readers and records* in eleven modules
(`labels.py`, `items.py`, `versions_view.py`, `residual.py`, `citations.py`, `approvals.py` and
others), all in the read direction. Nothing under `src/review_surface/` calls any receiver's
`apply_review_action`. The `review_action` delivery seam still does not exist, and the disagreement
still costs nothing at run time. What Wave B added is the *`review_approval`* seam (§12), which is a
different record.

### 13.1 The questions, reduced to one and its consequences

**Q1′ — the ruling. Who owns the name of a gesture: the part that COLLECTS it, or the part that
APPLIES it?**

This is `74` §8 Q2 restated as the question MINOR 6 is actually waiting on, and it is the only thing
here that requires judgement rather than bookkeeping. Reading (i) — P13 owns it, because
`review_action` is P13's record. Reading (ii) — the applying part owns it, because
`P13 SPEC:282-283` says *"that part decides what it means."* Everything below follows from the answer.

**Consequences of (i), which are then not separate decisions:**
- P13's eighteen must grow to cover §8.7's six unhomed gestures and §5's canvas (§4.4) — i.e. §6's Option D — because a vocabulary that owns every name must have a name for everything a person can do.
- P9's and P10's sets become re-exports of P13's. §8 Q2 ("may a person rename a branch, and what is it called") is answered by whatever the derivation produces.
- The owner-approval gate stays in one module, which is this reading's real strength.

**Consequences of (ii), which are then not separate decisions:**
- P13's `ACTIONS` becomes an assembly of imports from P9, P10 and P11. Nobody invents a name; the ~40-member union already exists in `src/` and is already traceable to design sentences (§3.3).
- §8 Q1 ("is the eighteen complete?") dissolves — it was never meant to be complete, it is the collection vocabulary for the surfaces P13 itself owns.
- §8 Q2 is answered `rename`, because P10 renames.
- §8 Q5 ("are `restore` and `reset-suggestion` real?") is answered no under *both* readings: P9 owns group gestures, and neither is in P9's SPEC either (§3.2).

**Q2′ — does P11's fresh-string copy get repaired as housekeeping, or does it wait for Q1′?**
`src/placement/vocabulary.py:305-328` duplicates a now-published P13 vocabulary and its own
neighbouring comment forbids it (§11.3). This is `80` §2's shape exactly: not a new rule, a list that
needs a housekeeping update after something shipped. It is also a *restriction* — it removes a second
home rather than adding a member — which by `80` §2's own reasoning is recordable without a fresh
ratification round. It can be done before Q1′ and does not depend on it.

**Q3′ — the one thing MINOR 6 makes worse, and it needs an explicit answer.**
Under reading (ii), P13's closed vocabulary grows whenever P10 edits a tuple in
`src/tree_design/vocabulary.py`. That collides head-on with the standing rule that *"adding a member
to a closed vocabulary requires owner approval recorded at the member"*
(`src/review_surface/move_permission.py:33-34`). Either the approval gate moves to the owning part —
so P10's tuple is where a canvas gesture gets approved — or reading (ii) is refused on that ground.
**This is the strongest argument for reading (i) and it is not answered anywhere.**

**Q4′ — `leave-untouched` or `leave_untouched`?**
§8 Q4 stands, but it stops being a coin-flip: under either reading of Q1′ the answer is mechanical.
Under (i) P13's `leave_untouched` wins; under (ii) P10's `leave-untouched` wins, because leaving an
existing folder alone is a tree outcome (`01`:1037-1039). Pick Q1′ and this is decided.

**Q5′ — is the canvas a `review_action` surface at all?**
§8 Q3 and `74` §8 Q4, unchanged and still open. §12's Option G does not touch it. It remains the
question I am least able to answer from evidence.

### 13.2 What is now settled by evidence rather than by choice

Recorded here so the owner does not re-decide them:

- **The field-name disagreement needs no ruling.** §12 shows two parts deriving the SPEC's record independently and matching nine of nine. P9's `plan_version_id`, `decided_at`, `basis` and `group_id` lose to P9's own SPEC (`planning/parts/P9-grouping/SPEC.md:125-129`), not to P13's.
- **No fixture is needed for any of the three seams.** `tests/p13/p12_fixtures.py` never existed and the seam it was planned for is green.
- **A translation table (§5's Option C) is refused twice over**, now: by `74`:490 and by MINOR 7.
- **This is two defects, not a four-way tie** (§12.3).

### 13.3 My judgement, kept separate

Nothing below is a ruling and nothing below was applied to any file.

**§9 recommended Option D. I am revising that.** D was the right answer to the question as `74` §8 Q2
framed it, and §11 shows the framing was wrong: the project already has the rule, and what is missing
is one ownership ruling, not a derivation exercise. **What I would now put to the owner is Q1′ alone,
with Option G (§12) as the mechanism regardless of how Q1′ goes** — because G is already shipped,
already green, and settles the entire field-name half without anybody choosing anything.

On Q1′ itself I lean to **reading (ii)**, for three reasons, and I hold the strongest objection to it
in the same breath.

First, it is the only reading under which nobody invents a name. Every member of the ~40-name union
already traces to a design sentence (§3.3's table); P13's eighteen does not cover them (§4.4); so
reading (i) requires someone to author names for six gestures the design describes but never spells.
This project's standing position is that authoring is where defects come from.

Second, it matches what the SPEC says out loud — *"that part decides what it means"* — and it matches
what MINOR 6 already did for node kinds between the same two parts (§11.2). Reading (i) would make
`review_action` the one record in the system where the collector, rather than the owner, names the
vocabulary.

Third, it makes §4.4's six unhomed gestures stop being unhomed without a SPEC amendment, which is the
only outcome under which a person can rename a branch *and* the rename is recorded truthfully — which
is the question this brief was asked.

**And the objection I cannot answer: Q3′.** Reading (ii) disperses the owner-approval gate across four
parts. The rule that a closed vocabulary's membership carries its own approval is one of the few this
project enforces at four separate sites, and reading (ii) makes it four times harder to hold. If the
owner values that gate above the invention-avoidance argument, reading (i) is correct and Option D
comes back with it. **I do not think that trade is mine to make**, and it is the substance of Q1′.

**Urgency, revised.** §9 said low and rising at the first receiver call. That is still true, and the
horizon is now nearer: `build-p12-waveG` is working the seam next door, `src/placement/vocabulary.py`
is holding a duplicate of a published vocabulary today (§11.3), and each further wave built on the
frozen fixtures is more call sites to move. Q2′ is repairable now and independent of the ruling.

### 13.4 What this second pass did not do

- It changed no vocabulary, and specifically did not repair §11.3, which is a closed vocabulary and not this document's to edit.
- It did not re-run the probes of §4.2 against the post-Wave-B tree. The receivers' signatures are unchanged in `git log`, but the probe output in §4.2 is from before Wave B and is labelled as such.
- It did not check whether P7's or P12's `review_action` ends acquired vocabularies during Wave B. §10's caveat stands.
- It did not answer Q1′, Q3′ or Q5′.

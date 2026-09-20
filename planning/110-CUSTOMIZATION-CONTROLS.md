# 110 — The customization controls: what exists, what to build first, and how a change is shown

Written 19 Sep 2026 against `beadca11`, from the code. Every line number below
was read today at that commit. Nothing here is built; this is a proposal for the
owner to ratify, and the decisions only they can make are numbered at the end.

`107` §"Customization model" lists twelve controls a person must have BEFORE
FREEZE. The brief for this document says "essentially none of this is built"
and "today the only way to change anything is to re-run with different flags".
**Both sentences are wrong in ways that change the plan**, and §0 says how.

---

## 0. The diagnosis — three places the brief does not match the code

### 0.1 Five of the twelve are built or nearly built

The brief's claim was the lead's reading, not a measurement. The measurement:

| control (`107`) | what already exists | where |
| --- | --- | --- |
| Rename branch — at the LEVEL | `--rename-level SCHEMA:ROLE:FIELD=NAME`, durable, keyed to the vocabulary not the node, applied as routing's last step, survives re-derivation and library upgrades | `cli.apply_level_relabels` (`src/cli.py:21585`), `tree_design/user_edits.py`, applied at `routing.py:520` |
| Change split order — among the library's shapes | the NESTING question *"How should X be organised?"*, one option per routed candidate, answered with `--answer branch:<label>=<chain>` and read back by `gated_template` | `cli.nesting_chooser` (`src/cli.py:11924-11940`), `questions/triggers.question_for_nesting` (`:226`), `questions/store.gated_template` |
| Set residual behaviour | `--residual`, `--define-residual NAME=retained/reviewed/merely kept searchable`, `--residual-library disable/rename/relocate/merge/replace-with-existing:AREA`, `--send-set`, `--leave-set`, `--review-set` | `cli._parse_library_actions` (`:12246`), `residual_library_choices` (`:5188`), `residual_configuration` built at `:17081-17096` |
| Set privacy | `--enable-cloud` / `--disable-cloud` (per folder, remembered), `--file-held`, `--release`, `--show-protected` | argparse block `src/cli.py:25453-25650` |
| Set placement policy | `--stop-after gate/facts/tree`, `--freeze`, `--apply BRANCH`, `--apply-everything`, `--undo`, `--may-cross-folders` | `src/cli.py:25658-25693`, `cross_folder_moves` stored on `plan_versions` |
| Adopt existing folder — half | an existing folder is a branch source, the nesting question offers `keep-as-it-is` for it, and `00`:100's "never flattened without asking" is enforced at `cli.py:11927` (`candidate.source in EXISTING_FOLDER_SOURCES`) | `nesting_chooser`; `node_key.EXISTING_PREFIX` |

And there is a **text file the person edits**, which is the settings-file question
the brief asks about, already answered: `--structure-out` writes the proposed tree
as an outline with `[n]` markers; `--structure FILE` hands the edited copy back;
`structure_edits` (`src/cli.py:23886`) translates each edit into a gesture that
already exists (`Renamed` → `--rename`, `Removed` → `--reject` per file, `Added
... situation: <id>` → `--declare-role`, `situation:` under a top folder →
`--answer situation:...`) and **refuses by name** the two edits no gesture
expresses: `Moved` (`:23967`) and renaming a root or template-owned level
(`claim_of`, `:23942`). It stamps the plan version it was written from and
refuses a stale file (`:23907`). This is `00` amendment 2 of 14 Sep, built.

### 0.2 The tree diff exists end to end and is wired to nothing

The brief says *"that mechanism does not exist"*. It does, in three parts that
nobody calls:

* `tree_design/diff.py::diff_versions` — node-level diff by `origin_node_id`:
  added / removed / renamed / re-parented / re-ordered / re-templated /
  type-changed, each with an undo label.
* `tree_design/node_key.py` — since SPEC open question 5 was answered,
  `origin_node_id` is a KEY spelled from the node's claim (`branch:<label>`,
  `existing:<path>`, `<parent>/<field>=<value>`, `residual:<name>`), so two RUNS
  that build the same folder write the same origin, and `diff_versions` works
  across runs, not only across copies.
* `placement/versions.py::reproject` — the file-level consequence (§8.8's
  "twenty-three files now require renewed review because their previous
  destination no longer exists"), returning `requiring_renewed_review` and
  `removed_node_ids`.
* `review_surface/versions_view.py::structural_diff_view` — P13's rendering of
  both halves, with `unapplied_user_edits` and the three producer gaps named.

`grep -rn "structural_diff_view(\|reproject(" src` finds **no production caller**.
`diff.py` is the seam, not a false friend — with one caveat in §3.2 about what a
split-order change looks like through it.

The only diff a person can reach today is `_print_answer_effects`
(`src/cli.py:21958`): an OPTION-level diff of a changed `--answer` (schemas
turned on/off, templates affected). It never opens the tree.

### 0.3 The lead's v1 guess names two things that are done and one that is not what it sounds like

* **Rename** at the level is done (`--rename-level`). Rename of a LIFE
  (`Education → School`) is not: a life branch's `display_name` IS the life
  string from `lives.json` (`branch_situation.py:814`), `--label` names only the
  default branch (`:792`), and `--structure` refuses a root rename. The `RENAME`
  tree-edit action has a writer (`store.py:669`) that the pipeline never calls
  (`pipeline.py` calls `_apply` for `ACCEPT`, `ADD_SCOPED_GENERAL`,
  `SET_SHARED_MATERIAL_POLICY` only — `:909`, `:971`, `:1205`).
* **Change depth**, as `107` states it — *"keep all receipts directly under
  2026, or split by purpose"* — is **omitting one level of one branch**, which
  is `ACTION_OMITTED`/`ACTION_FLATTENED` in the dimension vocabulary
  (`vocabulary.py:149-151`). It is NOT the ceiling `TREE_LIMITS.max_depth=5`,
  which is a module constant at `src/cli.py:628` with no flag. The overlay was
  shaped to hold an omission (`user_edits.py` docstring, `64` §6) and its writer
  refuses everything but `renamed` (`OVERLAY_ACTIONS_WITH_A_WRITER`).
* **Disable a template**: the `IGNORE` tree-edit action has a writer
  (`store.py:673` — node becomes `ignored`, `accepts_placement=False`) and no
  gesture reaches it per branch. The `--structure` "delete the line" path is not
  disable: it issues `--reject FILE:FIELD=VALUE` for **every file under the
  folder** (`:24015`), retracting a FACT to hide a FOLDER — the same line `00`
  amendment 24 draws between a preference and a fact, crossed by the person's own edit; Decision 3 settles it.
* **Change split order** has THREE half-seams, none joined: 36 of 63
  definitions carry more than one `candidate_orders` entry (measured today) and
  `routing._recommended_order` reads only `default_order` (`routing.py:279-300`);
  `BranchTemplateBinding.chosen_order_id` exists to record which order a branch
  took (`templates.py:632`) and is constructed nowhere outside `health.py`;
  `CompositionOverride.role_order` — "the nesting the user picked" — is
  read at `routing.py:425` and constructed by no production caller outside `routing.py` (`routing.py:98-115`).

---

## 1. Which controls are v1

Ranking by value to the person ÷ cost against the seams that exist. "Cost" is
against `beadca11`; "seam" names the function a builder attaches to.

| # | control | state | seam | cost | v1? |
| --- | --- | --- | --- | --- | --- |
| 1 | **Set residual behaviour — make it persist** | built, but `residual_configuration` is rebuilt from the command line every run (`cli.py:17081-17096`), so `--residual-library "rename:Review Later=To Sort"` must be retyped on every run including `--freeze` | record each `ResidualChoice` as an answer under a new `residual:` question kind in the `questions` store, read by `residual_library_choices` when the flag is absent | **cheap** — one kind in `questions/registry.py`, one reader | **yes** |
| 2 | **Change split order — among the library's own orders** | half: nesting question exists but offers one option per routed CANDIDATE (`candidates.vertical_options:640`), never the definition's alternative `candidate_orders` | `routing.route_branch` emits one candidate per `candidate_orders` entry of an eligible definition (not only `default_order`); the nesting question then already lists both shapes with counts; the answer already lands in `gated_template`; write `chosen_order_id` on the binding | **medium** — routing change plus the binding writer; no new gesture, no new vocabulary | **yes** |
| 3 | **Disable a branch** | half: `IGNORE` writer exists (`store.py:673`), nothing calls it | a `--ignore-branch NAME` gesture (or `--structure` line form, §2.3) that collects a `review_action` then applies `IGNORE` through `pipeline._apply`; the node stays in the tree as `ignored`, its files go to the residual home the person already has, and the diff reports it | **cheap-to-medium** — the writer is there; the argument is what happens to the files (Decision 3) | **yes** |
| 4 | **Change depth — omit one level of one branch** | half: `ACTION_OMITTED` in vocabulary, overlay shaped for it, writer refuses it | `OVERLAY_ACTIONS_WITH_A_WRITER += (ACTION_OMITTED,)`; `apply_user_level_edits` drops the dimension; the level's value is carried onto its parent exactly as `106` §B.2's fold already does | **medium** — the fold code path exists; the test is that `--rename-level`'s key form (`SCHEMA:ROLE:FIELD`) names the level | **yes** |
| 5 | **Rename a life** | unbuilt: `display_name = life` from `lives.json` | a per-owner life alias table read where `life_of` is read (`branch_situation.py:814`), NOT a `lives.json` edit (`00` 12a(ii): no library change) | **cheap to write, expensive to key** — `node_key.branch_key` is `branch:` + label, so the rename re-keys the root and every learned preference and answer filed under the old label; amendment 28's rule (old key read as fallback, never migrated silently) must be applied a second time | v1 **only with Decision 4** |
| 6 | **Adopt existing folder — finish it** | half: `keep-as-it-is` exists; `ADOPT_EXISTING` has no writer; `--could-live-in` shows the landscape but "THIS IS NOT PERMISSION" | `ADOPT_EXISTING` writer mapping a proposed node onto an `existing:` key | medium | v1.5 |
| 7 | **Enable a template the corpus did not activate** | half: `--declare-role NAME=LAYOUT` turns on a schema; `--structure` `Added` line does the same | already the seam; what is missing is that the added branch has no files until facts route there | cheap for the gesture; the files are P11's | v1.5 (exists, needs the screen to say so) |
| 8 | **Set placement policy** | built: `--stop-after`, `--freeze`, `--apply`, `--undo`, `--may-cross-folders` | — | done | — |
| 9 | **Set privacy** | built at folder and file scope; NOT per branch | per-branch protection is a `src/privacy/**` edit and widens nothing only if it can only narrow — out of scope for this document by standing order | milestone | no |
| 10 | **Relocate a branch** | unbuilt; `REPARENT` no writer; `--structure` refuses `Moved` | `node_key` composes a level's key from its parent, so relocating re-keys every node beneath; a parent-independent level key is a schema migration | **milestone** | no |
| 11 | **Merge / split branches** | unbuilt; `MERGE`/`SPLIT` no writer; merging two LIVES is a change to the partition key (`partition_by_branch` keys on `life_of`) | a life alias table (item 5) can express "Career and Work are one life" as two kinds → one alias, which is a merge without a merge writer; a split is a new life the library never imagined (12a(ii)) | merge: **cheap once item 5 exists**; split: milestone | merge v1.5 |
| 12 | **Choose person labels** | no seam at all: no person-name dimension, no producer, nothing in `tree_design` mentions a pseudonym policy | belongs with amendment 19's `school` fact and the Family/Health rows (amendment 21) — a level that does not exist cannot be labelled | milestone, blocked on unratified rows | no |

**The lead's guess tested.** *Change split order, change depth, rename, disable
a template* — right on three, wrong on one, and it misses the cheapest item:

* Split order: right, but only as "choose among the definition's own
  `candidate_orders`" (reuse) — never a free-form reorder (invent, and
  `CompositionOverride.role_order` would be a second spelling of the same thing).
* Depth: right, but it is the per-branch omission, not the `max_depth` constant.
* Rename: **already done** at the level; the life rename is a key migration and
  needs Decision 4 before it is v1.
* Disable: right; the writer exists.
* Missing: **residual persistence** (item 1) — the owner already has the control
  and loses it every run, and it is the smallest change on the list.

**Recommended v1: items 1, 2, 3, 4.** Item 5 joins v1 if the owner takes
Decision 4; item 11's merge comes with it for free.

---

## 2. Where they live

Three layers already exist, and every v1 control attaches to one of them. No
new file, no new settings format.

### 2.1 Per-branch structural questions, answered with `--answer` (split order, disable)

Freeze is the same command with `--freeze` added (`src/cli.py:26164` runs the
pipeline, `:26434` freezes its result), so "before freeze" already means "on the
run whose screen you are reading". A structural question printed by run *n* and
answered on run *n+1* is the product's own shape for a pre-freeze control.

* **Split order** — no new question. `question_for_nesting`
  (`triggers.py:226`) already prints one option per shape with child counts and
  warnings; the answer is `--answer branch:<label>=<chain>` and `gated_template`
  returns it to `nesting_chooser` (`cli.py:11924`). The change is upstream:
  `route_branch` (`routing.py:561`) emits a candidate per `candidate_orders`
  entry, so a definition with `ord.project-function-period` and
  `ord.project-period-function` produces two options. `_recommended_order`
  (`:273`) keeps breaking ties with the default. When the answer is recorded,
  the binding's `chosen_order_id` is written from the option — this is the ONE
  place `107`'s "versioned plan" is missing a value today.
  *Do not* add a `--split-order` flag: an order the library does not carry is a
  library edit, and `CompositionOverride.role_order` is a third spelling.

* **Disable** — a new gesture `--ignore-branch NAME`, named exactly as
  `--apply` names a branch (`branches_named`, called at `cli.py:25062`, refuses ambiguity).
  It follows `apply_level_relabels`' order (`81` §13.1): collect a
  `review_action` FIRST, then `pipeline._apply(... action=IGNORE)`. Persisted as
  a `review_action` row, so the next run reads it through
  `learned_preferences_still_applicable` (origin-keyed, survives re-runs).

### 2.2 The vocabulary-keyed overlay (`user_level_edits`) — rename level (done), omit level (v1)

`64` §6 says reorder and omission "should be designed to hold them rather than
retrofitted per action"; the table and the record already hold any of
`DIMENSION_ACTIONS`. v1 adds ONE writer member:

```
OVERLAY_ACTIONS_WITH_A_WRITER = (ACTION_RENAMED, ACTION_OMITTED)
```

Gesture: `--omit-level SCHEMA:ROLE:FIELD`, the same key `--rename-level` takes
and the report already prints. `apply_user_level_edits` (`user_edits.py:184`)
removes the dimension; the value is carried onto the parent as an expected value,
which is what `106` §B.2's fold already writes, so a person reading
`node_expected_values` sees the same shape either way. The library's proposal is
kept beside it (`proposed_label`), so an upgrade can say *"this release would
have built a Purpose level here; you omitted it."*

Not `ACTION_REORDERED` in v1: a reorder inside the overlay would be the fourth
spelling of split order.

### 2.3 The structure file — the non-JSON front end, extended one line-shape at a time

`--structure` is the owner's own 14 Sep design and it already translates edits
into gestures. The controls above become line-shapes it recognises, so a person
who never types a flag can still do all of v1:

| edit in the outline | today | proposed |
| --- | --- | --- |
| rename a value-named folder | `--rename` | unchanged |
| delete a line | `--reject` on every file beneath | **becomes `--ignore-branch`** for a root line; stays `--reject` for a value-named level (Decision 3) |
| rename a template-owned level | refused (`claim_of`) | → `--rename-level` (the triple is on the node's `template_context`) |
| a line ending `omit` on a template-owned level | — | → `--omit-level` |
| `shape: <chain>` under a root | — | → `--answer branch:<label>=<chain>` |
| move a line | refused | **stays refused** (item 10) |

Every one of these is a new refusal or a new translation inside
`structure_edits`; none is a second path into the plan tables, which is the
rule that function's docstring states.

**Why not a settings file.** `--structure` IS one, with three properties a
YAML/JSON file would have to re-invent: it is written by the run it describes,
it stamps the plan version and refuses a stale copy, and it is read through the
gestures rather than beside them. A second file would be `109`'s two-spellings
defect on the largest surface the product has.

### 2.4 Residual persistence (item 1)

`residual_library_choices` runs on flags alone. Proposed: each `ResidualChoice`
is recorded as an answer to a `residual:<area>` question (a sixth `QuestionKind`
in `questions/registry.py`, `consequence_field` = a new `residual_action` on
`QuestionOption`, reader = a `residual_choice(conn, scope=...)` in
`questions/store.py`), and `cli.py:17082` reads stored choices for every area
the flags did not name this run. `--explain residual:Review Later` then works
for free, and `=revoke` un-enables. **The area names and action words are
already closed vocabulary (`RESIDUAL_LIBRARY_ACTIONS`); no new member.**

---

## 3. What happens to answers and plans when a control changes

### 3.1 What is preserved, by construction

* **Answers** live in `structural_questions`/`structural_answers`, keyed by
  question id and scope, never by plan version. A changed control does not touch
  them; a re-run reads them (`apply_answers` is applied first, `cli.py:21685`).
* **Level renames** live in `user_level_edits`, keyed by vocabulary. A split
  order change moves the level; the rename follows it (that is `64` §3's whole
  point).
* **Learned preferences** (rejections, `--reject`) are filtered by
  `learned_preferences_still_applicable` on origin lineage
  (`placement/versions.py:441`), which the stable `node_key` made work across
  runs.
* **Residual choices** — today, nothing (item 1).

### 3.2 The diff: wire what exists, and say what it cannot yet say

**Mechanism.** On every run where `latest_plan_version(conn)` differs from the
newest FROZEN version (`frozen_plans`, `apply_run/freeze.py`), compute
`reproject(conn, from_plan_version=frozen, to_plan_version=new)` and
`structural_diff_view(conn, before=frozen, after=new, version_diff=...)`, and
print it BEFORE the freeze invitation at `cli.py:24869`, under a heading that
names both versions. A `--freeze` on such a run prints the same diff and then
freezes. Nothing is diffed on a first proposal (no frozen version), matching
`_print_answer_effects`' rule that a first answer is not a change.

**What the person is shown**, in `versions_view`'s existing fields: nodes added
/ removed / renamed / re-parented with their undo labels; `carried_unchanged`;
`requiring_renewed_review` — the files whose frozen destination no longer
exists; `unapplied_user_edits` — the renames this shape could not honour, in
`diff.py`'s words; and the three producer gaps named, not omitted.

**The caveat, stated so it is not discovered later.** A level's origin key is
`<parent-key>/<field>=<value>` (`node_key.level_key`). A split-order change
(`term→course` to `course→term`) re-keys every node beneath the branch, so
`diff_versions` reports it as *every level removed and every level added*, and
`DIFF_REORDERED` — which compares sibling `ordinal` — never fires. That is
honest (those folders really are different paths) and unreadable at two
hundred files. The cheap fix once `chosen_order_id` is written (item 2): one
headline line per branch — *"Coursework re-shaped: term → course became course
→ term; N files keep a folder of the same name, M change folder"* — computed
from the two bindings' `chosen_order_id`, above the node list. The expensive
fix — a level key independent of its parent — is a schema migration of
`origin_node_id` and is a milestone of its own.

### 3.3 The defect a control change after freeze meets today

`plan_versions.state` admits `'superseded'` (`schema.py:32`) and **nothing
writes it** — no `UPDATE ... state='superseded'` exists in `tree_design`.
`--apply` reads `frozen_plans(conn)` and unions the nodes of EVERY frozen
version (`cli.py:25052-25053`). So: freeze, change a control, freeze again,
`--apply-everything` — and both trees are live at once. The owner's own database
already holds two frozen plans (`109` A4's usage note on `measure.py`). This is
not a diff question; it is which plan governs, and it is Decision 5.

---

## 4. Cheap versus milestone, in one list

**Cheap (days, existing seams):** residual persistence (2.4); `--ignore-branch`
through the existing `IGNORE` writer; `--omit-level` through the overlay; the
diff printed at `cli.py:24869` from the four functions that already exist;
`--structure` line-shapes for each.

**Medium (a phase):** `route_branch` emitting alternative `candidate_orders` as
nesting options and writing `chosen_order_id`; the per-branch re-shape headline.
**One thing NOT verified for item 2:** `_recommended_order`'s docstring says an
order recommendation "cannot override an edge a fragment states". Whether every
non-default `candidate_orders` entry is already validated against the
definition's fragment partial orders (the definition checks its orders at
`templates.py:373-384`; what it checks them against was not read) decides
whether item 2 is medium or medium plus a C5 gate. Read that before costing it.

**Milestone of their own:** relocate (parent-independent level keys); life
rename and life merge (key migration under amendment 28's fallback rule);
per-branch privacy (`src/privacy/**`); person labels (blocked on amendments 19
and 21); a life the library never imagined, added by the person (12a(ii)); the
`superseded` state and one governing plan.

---

## 5. Decisions only the owner can make

1. **The v1 set.** Items 1–4 (residual persistence, split order among the
   library's orders, disable a branch, omit a level). Yes, or a different four.
2. **Two gesture names and one line-shape are new closed vocabulary**:
   `--ignore-branch`, `--omit-level`, and `shape: <chain>` / `omit` in the
   structure file. Names are yours; the mechanisms behind them are not new.
3. **What "disable" does to the files.** They go to the residual home you have
   enabled (`98 Review and Unsorted` is a root since amendment 13), or they stay
   exactly where they are and are merely kept searchable. Today the only
   disable-shaped gesture retracts a fact on every file, which amendment 24
   forbids; it will be removed from the root-line case once you choose.
4. **Life rename now, or after the key migration.** Renaming `Education` re-keys
   `branch:Education` and every answer and preference under it. Either the old
   key is read as a fallback (amendment 28's rule, a second time) and rename
   ships in v1, or rename waits for a branch key that is not a display string.
5. **Which plan governs after a second freeze.** Supersede the earlier frozen
   version on freeze (and `--apply` reads one plan), or refuse to freeze while an
   earlier frozen plan has unapplied moves. Today both are live and `--apply`
   unions them.
6. **The `max_depth` constant.** `TREE_LIMITS.max_depth=5` at `cli.py:628` has
   no flag. Leave it (per-branch omission is the control `107` actually
   describes), or expose it as the eighteenth P1 ceiling with a flag.

---

## 5. The one thing §4 left unverified, now read — item 2 is medium PLUS a C5 gate

§4 said: *"One thing NOT verified for item 2: `_recommended_order`'s docstring
says an order recommendation 'cannot override an edge a fragment states'. Whether
every non-default `candidate_orders` entry is already validated against the
definition's fragment partial orders ... decides whether item 2 is medium or
medium plus a C5 gate. Read that before costing it."* It has been read.

**IT IS NOT VALIDATED. Only the default order ever meets C5.**

Three reads, and they agree:

1. `_recommended_order` (`src/tree_design/routing.py:275`) builds its sequence
   from `definition.default_order.dimensions` — **the default order and nothing
   else**. `candidate_orders` is iterated nowhere in that function.
2. `merge_fragment_constraints` is called **once per branch**
   (`routing.py:423-431`), with `preferred_order=_recommended_order(...)`. C5 is
   raised from inside it, so C5 sees exactly one order: the recommended one.
3. `TemplateDefinition._check_orders` (`src/tree_design/templates.py:372-423`) is
   the only other thing that inspects `candidate_orders`, and it checks four
   things — at least one order, unique `order_id`s, exactly one `is_default`, the
   same role set across all of them, plus the `sole_order_attestation` rule. **It
   never looks at a fragment edge.** It cannot: a fragment's constraints are
   merged at routing time from the fragments actually in play, and the definition
   record does not have them.

**WHY THIS IS NOT A TECHNICALITY.** `templates.py:309-311` draws the distinction
itself: a template-local pair *"cannot reorder what a fragment constrains. A pair
contradicting a fragment edge makes the combined graph cyclic and C5 refuses it,
which is the difference between a recipe's recommendation and a fragment's
rule."* A fragment edge is a **safety-and-meaning constraint**, not a preference.
So the moment item 2 offers a non-default order to the person as a nesting
choice, it is offering an order that **nothing has checked against the rules** —
and the person picking it is the first thing in the system to assert it is legal.

**THE COST, CORRECTED.** Item 2 is *medium plus a C5 gate*: every entry the
branch offers has to go through `merge_fragment_constraints` before it is shown,
and an entry that cycles is not offered rather than offered and later refused.
`84` §6 again — a choice the screen presents has to be one the person can
actually take.

**WHAT IS NOT WRONG TODAY.** Nothing ships a non-default order to anyone, because
`routing.py` reads only `default_order` — `_recommended_order`'s own docstring
says the whole mechanism *"was built, tested, and wired to nothing"*. This is a
cost discovered before the build, not a defect in the product. It is recorded
here so item 2 is not quoted at its §4 price.

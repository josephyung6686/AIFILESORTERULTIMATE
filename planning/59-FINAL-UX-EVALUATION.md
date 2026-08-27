# 59 — Final UX Evaluation

**Status:** analysis for the owner. Nothing in `src/`, `tests/`, or `planning/domains/` was touched.
**Question it answers:** would a real person, with a real disk, be well served by this?
**Canonical authority:** `00-database-agent-product-design.md`. Where I disagree with `00`, I say so
and mark it as mine — §6 is that section and it is the one to read if you read one.
**Verified against the tree at commit `b7c6e8f` + working changes.** Suite at the time of writing:
`4636 passed, 19 skipped, 2 xfailed`. The gated scale suite (`SCALE_STRESS=1`) is `14 failed,
5 passed` — those failures are deliberate, they assert defects.

---

## 0. What I am actually evaluating, stated before anything else

**There is no user experience yet. There is a specification of one, encoded in record shapes and
refusals, and it is unreachable.**

- `src/production.py:1-6` composes P1 through P7 and says so: *"P8 is deliberately absent."*
- `horizontal_candidates`, `vertical_options` (`src/tree_design/candidates.py`) and
  `run_corpus` (`src/placement/pipeline.py`) have **no caller anywhere in `src/`** — only tests.
  `src/orchestrator.py` and `src/production.py` import nothing from `tree_design`, `placement`,
  or `grouping`.
- `pyproject.toml` declares no `[project.scripts]`. There is no CLI, no canvas, no window.
- Every user decision in P10/P11 is expressed as a **`RuntimeError`**: `FreezeRefused`,
  `ConfigurationRequired`, `SharedMaterialPolicyRequired`, `ResidualPartitionRequired`,
  `ClassificationRequired`, `AskOrAbstainSelectorRequired`, `ReturnCycleLimitRequired`,
  `SetDecisionRequired`. Eighteen such classes across the two packages. There is no function
  anywhere in `src/tree_design/` or `src/placement/` that *offers* a choice — `grep` for a
  producer of questions returns `_node_in_question` (`src/placement/review.py:176`), a helper.

This is a defensible library design and I am not calling it a bug. It is the reason this document
cannot report what a person sees. **It reports what the record shapes commit the person to see**,
which is the next best thing and is genuinely evaluable, because the shapes are strict.

One consequence must be stated plainly and carried through every section below: **the product's
questions are currently error messages.** `00`:99 wants live structural feedback *before* a split;
`00`:123 wants a high-level decision about each residual set *before* the model runs. Both exist —
as strings inside exceptions raised when the caller failed to supply the answer. The information
architecture is right. The direction of the conversation is inverted: the system does not ask, it
refuses until told.

---

## 1. Three people, walked end to end

### 1a. Mara, litigator — 40,000 files, ~80% of them one practice

**Scan.** Works. This is the strongest part of the product and it deserves its one line: identity is
content-hash-based with path history, extraction is cached per content version, exclusions run before
the scan, and `files.current_path` now carries an index (`src/database_agent/db.py:128`). She would
get a real evidence database.

**Groups.** Partly works, and the part that fails is the part that matters. `law_practice` **does not
exist at runtime.** `SCHEMA_IDS` (`src/facts/domains.py:52-53`) is ten flat ids:
`academic, college_applications, research, career, photos, code, finance, identity, medical, legal`.
No sub-domains, no `law_practice`, no `.discovery`, no `.trial-preparation`. Four of the ten
(`career, identity, medical, legal`) carry zero field rows (`src/facts/domains.py:66-67`). So of
Mara's disk: the `legal` half activates a schema that contributes nothing, and the practice-apparatus
half activates nothing at all. Her groups, if the categoriser forms any, arrive at tree design with
`AcceptedGroup.domain = None` or `"legal"`.

**Tree design.** This is where it ends. `AcceptedGroup.domain` is a single `str | None`
(`src/tree_design/upstream.py:72`), and C6 (`src/tree_design/routing.py:397-412`) drops every member
of a group whose domain is not in the candidate template's schema set, then raises
`CompositionConflict(C6, …)` — a **non-overridable** refusal (`routing.py:81-95`). A `legal` group
matches no template with dimensions, because `legal` declares none. Mara gets no composition.

**Freeze.** She is asked for a §6.9 shared-material policy she has no branches to apply it to
(`src/tree_design/freeze.py:187-206`), nine residual enablement decisions
(`freeze.py:200-204`), and a refinement disposition per approved branch she does not have.

**Placement.** Every file raises `ClassificationRequired` (`src/placement/pipeline.py:277`) because
`src/privacy/classification.py:32-38` states outright that *"until a detector is supplied, every real
file resolves to `Denied(unclassified)`"* and no detector ships. With one injected: her pleadings,
being `legal`, retrieve no node (no `legal` field is in any node's `expected_values`) and abstain
with `NO_SUPPORTED_DESTINATION` (`src/placement/scoring.py:90`).

**Review.** She lands in the residual library with four folder names — `Personal / Independent
Records`, `Photos / Temporary Screenshots`, `Protected Records`, `Reading Inbox` — of which two are
hard-coded under `Photos/` and `Personal/` parents (`src/tree_design/vocabulary.py:272-278`). Her
e-filing confirmation screenshot, which is her proof of timely filing, routes to the folder whose
name means disposable. And `surface_residual_sets` raises `ResidualPartitionRequired`
(`src/placement/residual.py:145-150`) because no partition producer exists in `src/`.

**Verdict:** the product does not serve her at any stage after extraction. 53 F1 and 55 rank-2 both
called this; both are **still true** and I re-derived the schema counts rather than trusting them.

### 1b. Priya, PhD student who TAs the course she takes — `00`'s own persona, plus one twist

**Scan, groups, tree.** This is the persona the product was built for and it largely works. All six
field-declaring schemas — `photos`(6), `research`(6), `academic`(5), `college_applications`(5),
`code`(4), `finance`(4) — are hers. Her PHYS1401 syllabus anchors a course group; her sparse
`HW 3.pdf` arrives as a context-supported member; `00`'s worked example runs.

**The twist breaks it silently, which is worse than breaking it loudly.** She takes PHYS1401 and TAs
PHYS2801. `canonical_fields.json:88-97` defines `school` as *"the institution the holder attends,
attended, **or teaches at**"* — the take/teach inversion is collapsed into one key **on purpose**.
`academic.teaching` exists in `planning/domains/nodes/` with `fields: []`, `proposed_fields: []`,
`role_split: []`, and **zero occurrences in `src/`**. Her own problem sets and the solution sets she
wrote for her students carry identical `subject`, `term`, `work_type` evidence. They land in one
folder.

That is a marking-integrity problem, not a tidiness problem. She will find it the first time she
looks for a solution set and finds a student's submission next to it.

**The dimension picker.** When she is asked how to organise Academics, the string the interface has
is the key. `VerticalOption.summary` (`src/tree_design/candidates.py:446`) is built by `_summarise`
(`:306-313`) over `child_counts`, keyed by `field_ref or dimension_role`
(`src/tree_design/materialise.py:280-295`). The sentence reads: *"This option would create 3 subject,
5 term, and 12 work_type."* The authored human label exists — `RoleBinding.label`
(`src/tree_design/templates.py:441-471`), carried to `ResolvedDimension.display_label`
(`routing.py:387`) and `LevelEvidence.dimension_label` (`materialise.py:83`) — and reaches **exactly
one** consumer, `_label_of` (`materialise.py:240-253`), used at **one** call site: the node's §5.12
explanation string (`materialise.py:445-451`). The picker never sees it. See §5c — this is worse than
53 F4 reported, and I have the number.

**Verdict:** served, until she has a second life. Then served wrongly and told nothing.

### 1c. Tom, two-child household — the persona nobody designed for

**Scan.** Works.

**Groups.** `medical` and `legal` activate and contribute no fields. `academic` activates on the
children's school material — and there is **no field anywhere that names the child**. `people` exists
(`src/facts/fields.py:209`) and is `destination_eligible=False`. Ada's report card and Sam's report
card are, to this system, two academic files with the same school and the same term.

**Tree design.** `Academics / <school> / <year> / <work type>` — with both children's work
interleaved at every leaf. He will rearrange this the first time he opens it. 53 F5 called it, the
corpus said it four separate times, and it is **still true**.

**Freeze.** He is asked nine questions about residual templates
(`src/tree_design/freeze.py:200-204`) — a fixed cost regardless of corpus size — plus the §6.9
policy, plus a mandatory free-text `reason` for that policy (`src/tree_design/store.py:344-350`),
before freeze will accept anything.

**His lease, his will, his insurance dispute papers** have no destination in the main tree at all.
`legal` is `launch: safety` with `fields: []`, correctly per `00` §3.15. They land under `Protected
Records`. He asked for a folder; he got a posture, under a name no household has ever said.

**Verdict:** recognition and protection, no structure, and one sorting failure he will notice within
a minute.

---

## 2. The multi-life person — the case every persona document assumed away

**Answer: the system has no notion of it, and the one layer that does have it destroys it at the
next hop.**

Multiplicity exists at exactly one place. `active_domains` (`src/facts/domains.py:108`) is keyed on
`(file_id, content_hash)`, several schemas may be true at once, and the docstring is exactly right:
*"Activation adds; it never chooses."* Then:

| hop | what collapses | where |
|---|---|---|
| group | `AcceptedGroup.domain: str \| None` — one domain per group | `src/tree_design/upstream.py:72` |
| template | *"The join row. Exactly one `uses_schema`"* | `src/tree_design/templates.py:475,488` |
| routing | rows bucketed `by_template`; each template becomes a **competing** candidate | `src/tree_design/routing.py:466-476` |
| composition | C6 drops members whose group domain is outside the template's schema set, then refuses — **non-overridable** | `src/tree_design/routing.py:397-412`, `:81-95` |

So a branch holding a `law_practice` group beside an `academic` group beside a
`medical.dependant-child-health` group is not a two-branch outcome. It is a **hard error on every
candidate**, unless one single template ships applicability rows in all three schemas — and no
catalogue with `role_bindings` ships anywhere in the repo (§5c).

`TemplateApplicability` (`src/tree_design/templates.py:474-546`) conditions on `uses_schema`,
`purpose_profile_ref`, `allowed_fields`, `detection_signal_refs`, `role_bindings`, `exclusions`,
`provenance`, `privacy_floor`. **No volume, share, or proportion input.** There is no persona, no
life-area, no corpus-share concept anywhere in `src/` — I grepped. Depth is a flat configured ceiling
(`src/tree_design/validation.py:130`) reading a single P1 key that also caps the *number* of
proposals (`src/tree_design/config.py:30`).

**The one mechanism that exists to ask the user anything is pointed at the wrong axis.**
`_check_orders` (`src/tree_design/templates.py:392-399`) still requires every candidate order to
cover the same roles — only ORDER may vary, never the dimension SET. (The related rule was relaxed:
`templates.py:409-419` now accepts `≥2 orders` **or** a `sole_order_attestation`, which retires 53
F7's over-application complaint. The set-invariance stands.) Every split a multi-life person needs —
their courses vs the courses they teach, their lease vs their client's, their child Ada vs their
child Sam — is a split in the dimension set or in eligibility. **None of them can be offered.**

**This is the single most consequential finding in the document**, and it is upstream of almost every
other one. §6.1 argues the fix.

---

## 3. The four nuance cases the owner named, through the live code

### 3a. A research paper that is also school homework — **PARTIAL, and it fails quietly**

Retrieval returns both `Academics/…/PHYS1401/Homework` and `Research/PVA-RDP/Drafts`. Suppression
(`src/placement/retrieval.py:104-113`) requires the *same field* with a *different value*; `subject`
and `project` are different fields, so neither node is suppressed — correct. Both score
`DIRECT_FACT(3) + ACCEPTED_GROUP(2) / _MAX_WEIGHT(7) ≈ 0.714` (`src/placement/scoring.py:41-46`).
Exactly tied.

The two-condition rule (`scoring.py:111-124`) then does the right thing: margin `0.0 < 0.2` →
`MARGIN_FALSE` → verdict `WEAK`, `requires_review=True`. **But `_reason` checks margin before
threshold** (`scoring.py:91-92`), so the file is reported as `LOW_MARGIN` — an evidence-quality
complaint — when the truth is *this file has two correct homes*. Those are different sentences and
the user needs the second one.

Then the multi-home path. `run_corpus` (`src/placement/pipeline.py:1095-1104`) does detect the file
as multi-home and skips it from both group plans (`:1114`). But at `:1126` it requires
`len(parents) >= 2`, where each `parent` comes from `confirm_shared_parent`
(`src/placement/groups.py:191-200`), which returns a node **only if every remaining member of that
group landed on the same node id**. A PHYS1401 group whose members spread across `Homework`,
`Lectures` and `Syllabus` — the normal shape of a course group — returns `None`. `parents` collapses
below 2, and the file falls through to ordinary `place_file`, where the LLM judge picks a side
(`pipeline.py:358-403`) and the loser is listed in `alternatives`.

**What the person experiences:** a review item saying "low margin", on a file that has two right
answers, with one of them silently chosen. The `Ask` exists — `"Which packet is this file's primary
home?"` (`pipeline.py:834-835`) — and is reachable only on the unanimous-groups path.

### 3b. Legal documents for an application vs for a deal — **PARTIAL, asymmetric for the wrong reason**

`legal` declares no fields and recommends no dimensions (`planning/domains/nodes/legal.json`:
`launch: "safety"`, `fields: []`). The live catalogue (`src/facts/fields.py:102-223`, 37 rows) has
**no legal-scoped field at all**.

- **A lease inside a visa/college application packet** gets a destination — by borrowing
  `college_applications`' dimensions. If it carries a matching `purpose`/`target_school` it scores
  0.714 and is placed. If it carries **only** group membership, it scores `2/7 ≈ 0.286`, below the
  0.4 support threshold, and abstains.
- **A lease that is the subject matter of a deal** has nothing to match on. `client` is
  destination-eligible (`src/facts/fields.py:132`) but no active schema declares a `client`
  dimension, so no frozen node carries it in `expected_values`. Retrieval returns empty →
  `NO_SUPPORTED_DESTINATION` → abstain → residual → `ResidualPartitionRequired`.

The asymmetry is real and its cause is wrong. One lease is filed and one is not, **not because one is
more legal, but because one happened to be swept into a group whose branch was built from a different
domain's dimensions.** A user cannot learn a rule from that.

### 3c. A passport inside a visa packet — **the branch survives; the passport does not get an answer**

The fix that landed is real and I confirmed it: `src/tree_design/materialise.py:161-168` computes
`protected` as a set, members stay in `by_value`, stay counted, stay in `member_file_ids`; V5 no
longer reads `handling_classes_by_value` (`materialise.py:141-145`). 55's rank-1 finding — *"a
protected file destroys the branch that needs it"* — is **FIXED**. The visa packet is built.

Three things remain, and the third is the one the user feels:

1. `protected_file_ids` is exposed as a bare frozenset (`materialise.py:236` →
   `candidates.py:433,468`). **No count or sentence is composed anywhere.** "This branch holds one
   protected file and it will not be moved" is a docstring promise (`candidates.py:108-112`) with no
   producer.
2. "Protected areas present-but-untouched, excluded from placement" is confirmed
   (`candidates.py:130-215`, `freeze.py:154-176`, `index.py:159-177`) — but it is bounded by
   `candidates.py:152-160` to P3's `RULE_PROTECTED_CONTAINER`, and that code says so explicitly:
   *"sensitive personal material is not the same thing as `Numbers.app`."* **A passport is never one
   of these nodes.**
3. The passport itself: `marked_state` is written in exactly one place, `pipeline.py:933`, reachable
   only through §7.7 residual action 7 — after the file has gone unplaced, been partitioned, and had
   its set decided. Inside a branch, nothing marks it. If it needs a model call it abstains with
   `PRIVACY_BLOCKED` and the explanation string reads *"No legal destination cleared §6.10's
   conditions (privacy_blocked)"* (`pipeline.py:537-540`) — **which reads as an evidence failure,
   not as "this is your passport and it stayed put deliberately."**

That last sentence is the whole finding. The safety behaviour is correct. The account of it given to
the person is wrong, and a person who is told their passport failed to place will conclude the
product is broken rather than careful.

### 3d. Two accepted homes, no shared branch — **the rule is excellent and three defects sit on it**

`resolve_multi_home` (`src/placement/groups.py:234-279`) has **no branch that can return one of the
competitors.** It raises `InstitutionalDestinationRefused` if the offered shared branch *is* a
competitor (*"placing there IS choosing between them"*, `:256-262`); it raises
`AskOrAbstainSelectorRequired` when no branch exists and nothing was injected (`:266-271`);
`_shared_branch_of` returns `None` rather than minting one (`pipeline.py:777-787`); and
`Ask.__post_init__` refuses fewer than two options — *"one option is a placement wearing a question
mark"* (`src/placement/records.py:121-127`). **This is the best-written code I read this session.**

The defects:

- **Scope leak.** `_shared_branch_of` (`pipeline.py:784-787`) returns the **first** `SHARED_MATERIAL`
  node anywhere in the tree. But `_write_overlap_answer` creates that node *scoped to a parent*
  (`src/tree_design/store.py:322-331,374-380`), precisely because *"a global catch-all folder is what
  the design refuses."* A Shared Material branch under `Academics` will be returned for an
  Academics-vs-Research competition, is not one of the candidates so `:256` does not fire, and the
  file goes to the academic side. **That is the arbitrary choice, laundered through a legal node.**
- **`primary-home` is treated as branch-bearing** (`groups.py:263-265`, `store.py:354-372`). Under a
  policy whose name means *pick the primary home*, the file is placed in a shared branch — the one
  place that is by construction neither home.
- **§6.8's stated ordering is inverted.** `place_group`'s docstring (`pipeline.py:664-668`) claims
  *"confirm the shared parent FIRST, then classify members beneath it."* The code classifies every
  member independently (`:692-700`) then derives the parent from decisions already made (`:702-703`).
  No member is ever classified against the shared context, and `shared_parent_node_id` influences
  nothing. `00`:112's whole argument for group-level placement is that related files explain one
  another — that benefit is not being taken.

---

## 4. The experience: how many decisions, and are they the right ones

**Count, derived from the code, not estimated.**

```
Total = B + K + Amb_C4 + Amb_C5 + A + (9 + 3·E) + 1 + 1
```

| term | what | where |
|---|---|---|
| `B` | one card per top-level candidate | `candidates.py:231,263,287` |
| `K` | one split choice per branch entering the vertical pass | `candidates.py:400-497` |
| `Amb_C4` | one field choice per role resolving to >1 field | `routing.py:296-306` |
| `Amb_C5` | one nesting-order choice per cyclic merge | `routing.py:322-326` |
| `A` | one refinement disposition per approved branch (3 options) | `freeze.py:147-153` |
| `9 + 3·E` | nine residual enablement decisions (6 options each) + disposition, anchor, label per enabled | `freeze.py:200-204`, `residuals.py:82,192-220` |
| `+1` | §6.9 shared-material policy (4 options) **+ a mandatory free-text reason** | `freeze.py:187-206`, `store.py:344-350` |
| `+1` | adopt | `freeze.py:428-435` |

**Floor: 14 decisions to freeze a single-branch tree.** A realistic corpus — 12 candidates, 8
accepted branches, 4 residuals enabled — is **51 decisions before a single file moves.**

**Are they the right decisions?** Four problems, in order of how much they cost.

**4a. Nine of the floor's fourteen are residual-library questions, asked at the worst possible
moment.** A user with one branch still answers nine questions about `Reference Clips` and `Unsupported
or Encrypted` before freeze will accept. `00`:123 puts the residual conversation *after* the main
structure is built and after the engine has counted the residue — *"We found 58 ungrouped
screenshots"* — because that is when the question is answerable. The implementation front-loads all
nine into freeze as a blocking gate with no counts attached. **Nine abstract questions before you have
seen your files is a wall; nine questions with "58 screenshots" attached is a conversation.** This is
a sequencing error against `00`, and it is the single worst thing about the flow as specified.

**4b. Five of the eight actions on every branch card cannot be executed.** `_BRANCH_ACTIONS`
(`candidates.py:58-61`) offers `accept, rename, merge, move-under-root, defer, create-manually,
drag-group-into-branch, ignore`. `store.apply_review_action` can apply **three** —
`ACTIONS_WITH_A_WRITER` is accept/rename/ignore (`store.py:95-97`). `merge` and `create-manually` are
refused by name (`store.py:109-112`); `move-under-root`, `defer` and `drag-group-into-branch` are not
in `TREE_EDIT_ACTIONS` at all (`vocabulary.py:413-417`) and raise `OutOfVocabulary`
(`store.py:460`). Separately, `EXISTING_FOLDER_ACTIONS` — `00` §5.10's six gestures for existing
folders (`vocabulary.py:392-395`) — has **no producer and no consumer anywhere in `src/`**.

`00`:96 is explicit that existing folders must be adoptable, mergeable, and leavable-alone, and
`00`:88 lists deferral and merge as first-class. **The three most important editing gestures on the
canvas — merge, defer, drag a group somewhere else — are advertised on every card and are not
implemented.**

**4c. `00`:99's structural feedback is 4 of 5, and the fifth is documented as impossible.**
`vertical_options` (`candidates.py:400-498`) delivers: child-branch count ✅, files-per-child ✅
(`ChildPreview.file_count:92`), unresolved files ✅ (`:440-443`, with the prose *"{n} file(s) would
stay unresolved and visible."*). Two problems:

- **Example members ⚠️** — `example_members=members[:len(members)]` (`:463`) is a no-op slice. It is
  the *entire* member list, and it is the **parent's** members. `ChildPreview` has no example field
  at all (`:90-92`), so there are no per-child examples — the one thing that actually tells a person
  what a folder will contain.
- **Evidence gaps ❌** — `evidence_gaps_by_node={}` is hard-wired (`candidates.py:367`) and
  self-documented at `:346-348`: *"nothing in `src/` produces an evidence gap."*

All five warnings exist with human-readable `reason` strings (`health.py:156-232`) — that is good and
it is 53's F-list moving. But **every threshold is an injected value with no default**
(`config.py:39-45`), and `materially_improves_retrieval` is a mandatory injected callable with **no
implementation shipped** (`config.py:42-45,71-76`). The flatten recommendation — `00`'s most
opinionated warning — cannot fire.

And the warnings are not folded into `VerticalOption.summary` (`candidates.py:448-454` mentions only
unresolved counts and validation failures). A surface that renders `summary` shows the user nothing.

**4d. The questions the person most needs to be asked are never asked.** Not "which order?" but:
*is this course one you take or one you teach? is this lease yours or your client's? whose child is
this?* §2 established that none of them can be expressed. What the product does ask is 51 questions
about folder shape, and what it cannot ask is the 3 questions that would let it get the folders right.

---

## 5. Where the implementation quietly diverges from what was reported fixed

Six of the seven claimed fixes are **confirmed in code**. I am not re-litigating them. Three carry
residual user-visible gaps sharp enough to matter, and one is materially different from its headline.

**5a. Confirmed and good, in one line each.** Protected file marked-not-removed
(`materialise.py:161-168`) — the 55 rank-1 regression is retired. Composer orders levels by
`order_index`, not list position (`materialise.py:171`). §6.9 asked at freeze
(`freeze.py:187-206`). `run_corpus` detects multi-home before placing (`pipeline.py:1095-1104`).
Protected areas present-but-untouched and out of the legal set
(`candidates.py:130-215`, `index.py:159-177`).

**5b. §6.9 at freeze is a refusal, not a question.** Nothing in `src/` offers the four
`SHARED_MATERIAL_POLICIES` (`vocabulary.py:342`) as a choice. And a **per-scope** policy row does not
satisfy the gate — only the tree-global row does (`freeze.py:346-355`). A user who answers "shared
branch, but only for the application packets" is refused. §6.3 argues this is `00`'s error, not the
code's.

**5c. Dimension labels: the mechanism landed, the data was never authored, and the number is worse
than 53 reported.** I re-derived it:

- `src/facts/fields.py` has **37 field rows, each with a `display_name` slot.** Nineteen of them are
  **byte-identical to the key** (`authored_by`, `target_school`, `our_firm`, `client`, `school`,
  `term`, `subject`, `instructor`, `purpose`, `project`, `stage`, `lab`, `venue`, `institution`,
  `event`, `location`, `people`, `repository`, `language`). The other eighteen are the key with the
  underscore replaced by a space (`work_type` → `"work type"`, `artifact_type` → `"artifact type"`,
  `media_type` → `"media type"`). **Zero of 37 differ from the key by anything else.**
- `RoleBinding.label` (`templates.py:441-471`) is required and non-empty — the right design, with the
  right rationale written at `:442-454`. **There is exactly one `RoleBinding` in the entire
  repository**: the fixture at `src/tree_design/fixtures.py:380-381`, `subject`→`subject`, label
  `"Course"`. No catalogue JSON with `role_bindings` ships anywhere.

So: the slot exists at four layers, is required at one, and in shipped data **the human name of every
dimension is the engine's key**. 53's F4 is not fixed; it has been converted from a missing field
into an unauthored one, which is progress in structure and none at all for the person.

**5d. Residual display names are now unauthored rather than wrong.** `TEMPORARY_SCREENSHOTS =
"Temporary Screenshots"` (`vocabulary.py:246`) is now the internal `template_name`; the shipped
`display_name` is a required authored slot (`residuals.py:105-118`) and user overrides win
(`residuals.py:212`). **No slot values ship, so nothing displays at all today.** The nine names and
the hard-coded `Photos/` and `Personal/` parents (`vocabulary.py:246-278`) are unchanged and are
still wrong for four of six personas.

**5e. Scale.** `files.current_path` is indexed (`db.py:128`) — 58's #1a is fixed. Everything else on
58's list is **still true**: retrieval is O(files × nodes) (`index.py:236-241` +
`retrieval.py:80-91`); `health._children` is a linear scan called per node inside `warnings_for`
(`health.py:60-61,176,206`) and `_descendants` is itself O(n²) called for every node
(`health.py:64-72,146`); `example_members` is uncapped; nothing caps split width
(`routing.py:487-489` caps candidate *count*, `validation.py:130` caps *depth*, nothing caps
breadth). The gated suite reports 14 of 19 failing.

---

## 6. Where `00` itself is wrong or silent about a real person

This is the section I was asked for and it is the one I would act on.

### 6.1 `00` never asks the user who they are, and at least four of the hardest cases are one question, not any amount of evidence

`00` derives everything from files. §5.1 is emphatic and right that labels *"should reflect the
user's vocabulary rather than a universal corporate taxonomy"*, and §4's stop rules correctly say to
abstain where a role is unevidenced. But look at what is unevidenced:

- Is this course one you take or one you teach? (`00` has no answer; `canonical_fields.json:88-97`
  collapses both into `school` deliberately)
- Is this lease yours or your client's?
- Is this résumé yours or a candidate's? (the corpus flags the wrong answer as a **privacy** failure,
  not a tidiness one)
- Which of your two children is this about?

Every one is a fact about the **person**, not the file. Every one is answerable in one question.
`00` provides no place to ask and no place to store the answer, so the product abstains on the entire
professional and multi-life half of a real disk — correctly, by its own rules, and uselessly.

53 §3 reached a narrower version of this (a corpus-share threshold to flip `legal` between a drawer
and a matter tree) and 53 §7.6 proposed it as a first-run question. **The general form is stronger
and cheaper**: `00` needs a short **role declaration** before the horizontal canvas — not a taxonomy,
not a persona picker, three or four questions whose answers become *facts about the corpus* that
schema activation and dimension eligibility may read. "I practise law." "I teach." "These are my
children: Ada, Sam." That is the missing input, and it also happens to be the input that makes
`subject_of_record`/`about_person` safe to make destination-eligible for Tom and unsafe for Mara —
which is exactly the decision `49` §2.4 correctly refused to make unilaterally.

**Recommendation:** add a §4.5 to `00` — *Corpus role declaration* — sitting between grouping and
tree design, producing user-confirmed corpus-level facts, explicitly bounded so it cannot invent
schemas or dimensions, only resolve role inversions and eligibility. This is upstream of §2's
finding and it is the highest-value change in this document.

### 6.2 `00` builds a search index and never lets the user search

§6.2 specifies a destination-node retrieval index; §3 specifies a `files`/`evidence`/`fields`/
`values`/`file_facts` model with full text, OCR and provenance. All of that is built so that files can
be **moved**. **Search appears in `00` exactly three times and never as a surface** — `00`:48
(*"several additional fields used only for search, privacy protection, explanation, or later
review"*), `00`:119 (*"whether the file should be reviewed, retained, or merely kept searchable"*),
`00`:127 (*"their preferred policy is searchability without movement"*). All three are properties of
a fact or a file. The only other occurrence, `00`:106, is a **prohibition** on the engine
(*"rather than searching the entire filesystem"*). There is no user-facing query anywhere in the
design.

For Mara, Tom, and the creator persona, the thing that would change their week is *find it again* —
and `00` §0 has already promised that the filesystem stays the system of record and nothing is
virtual, which means a read-only answer is **zero-risk**. The product is one query surface away from
being useful on day one, before a single decision is made, before freeze, before any move. `00` never
proposes it because `00` frames organisation as the goal and retrieval as the justification. For at
least half of real users that is backwards.

**Recommendation:** `00` should name a read-only retrieval surface over the evidence database as a
first-class deliverable available **before** tree design. It costs no new machinery. It is also the
only thing in this document that could ship to a real person this month.

### 6.3 §6.9's shared-material policy is tree-global, and the right answer is per-material

`00`:113 — *"The user's frozen tree should therefore include **a** policy for shared material."* One
answer for the whole tree, and `freeze.py:346-355` faithfully enforces exactly that (a per-scope row
does not satisfy the gate).

But a transcript in two application packets wants `shared-branch`; a CAD drawing that is both a design
revision and a trial exhibit wants `reference-or-alias`, because a revision that changes the design
must not change the exhibit; a passport in a visa packet wants `mandatory-review`. These are three
different right answers on one disk, and `00` permits one.

55 found the deeper hole and it stands: §6.9's worked example is a transcript that *"contains no
institution-specific fact"* — **factually neutral** shared material. The commoner and harder shape is
material that carries **both** claims, where an accepted membership in each packet wrote an addressee
each. That file is not neutral, it is doubly-claimed, and §6.9 has no policy for it.

**Recommendation:** make the policy per-branch with a tree-level default, and add a fifth value for
doubly-claimed material. `store.py` already carries `policy_scope`; only the freeze gate insists on
global.

### 6.4 `00` specifies five warnings and zero numbers

§5.9 lists one-child, repeats-parent, excessive-depth, many-tiny-folders, and *"recommend flattening
when a dimension does not materially improve retrieval."* It never defines "excessive", "tiny", or
"materially". The implementation is honest about the consequence —
`materially_improves_retrieval` is a mandatory injected callable with no implementation
(`config.py:42-45,71-76`), every threshold is injected with no default (`config.py:39-45`) — and 58
found that the only exercised value of the depth threshold **flags `00`'s own worked example** as too
deep.

A warning without a number is not a feature. **`00` should carry defaults**, argued from its own
examples, and should say what `materially improves retrieval` means operationally (my read: a level
earns its place if it reduces the largest sibling's file count below the point where a person scans
rather than reads — roughly 20 — and produces at least two children with more than one file each).

### 6.5 `00`'s residual library was authored from one disk

The nine names, and §7.3's own list of user-defined extensions — *Things to Read, Ideas, Shopping
Research, Memes, Travel, Receipts to Process, Clips, Stuff to Sort* — do not contain a single
professional residual. There is no "unfiled correspondence", no "closed matters", no "supplier
paperwork I haven't matched to a job". `vocabulary.py:272-278` then hard-codes `Photos/` and
`Personal/` as parents, which puts professional work under a personal parent for four of six personas.

And `00` §7.4's promise that the library is *"an optional set of controlled branches that the user can
enable, disable, rename, relocate, merge, or replace"* is exactly the promise that is currently
delivered as **nine blocking questions at freeze** (§4a).

**Recommendation:** the library is not the problem; its authorship is. `00` should state that residual
names are **per-corpus**, seeded from the role declaration of §6.1, with the nine current names as
the household/student seed rather than the universal set.

### 6.6 `00` designs the first hour and skips the next year

`00` is a single pass: pick corpus → extract → group → design tree → freeze → place → residuals. The
ops layer has versioned plans (§8.7) and a time-aware residual lifecycle (§7.9), but **nowhere does
`00` describe the second run.** What happens on Tuesday when forty files land in Downloads? Which of
the 51 decisions get asked again? Does a new course create a branch, or wait for a tree edit? §8.7
says a new plan version *"creates a new set of placement recommendations subject to review"* — that is
the mechanism, and it is not an experience.

The thing a person actually does with a file organiser is use it every week, and the weekly
experience is the one that decides whether they keep it. `00`'s one-shot framing is also what makes
the 51-decision freeze gate feel acceptable in the document and unacceptable in practice: you can ask
someone 51 questions once. You cannot ask them nine residual questions every Tuesday.

**Recommendation:** `00` needs a §9 — *the steady state*. What the product does with new files against
a frozen tree, what it asks and what it does not, and which decisions are sticky.

---

## 7. Where the product is genuinely good — stated once

The refusal discipline is real and it is rare. `resolve_multi_home` refuses to place a shared file in
one of the competitors and says why (`groups.py:256-262`). `Ask` refuses a single-option question —
*"one option is a placement wearing a question mark"* (`records.py:121-127`). Freeze refuses a
protected node that accepts placement and refuses a marked area with no node (`freeze.py:154-176`).
`horizontal_candidates` derives every candidate from the user's own accepted groups and labels, and a
test asserts `00`'s nine example top-level names appear nowhere in the source. `_check_orders` refuses
to let an ordering choice silently change what a branch organises by. Extraction, identity and
provenance are solid. **Nothing in this system fakes an answer**, and that is the property that is
hardest to add later.

---

## 8. The honest verdict

**Would I recommend a real person run this on their actual disk today? No — and not because of any
finding above.** Because there is nothing to run. P10 and P11 are complete, correct, well-tested
libraries with no caller, no interface, and no shipped catalogue data (§0, §5c).

Ranked, what stands between here and a person being well served:

| # | What | Severity | Evidence |
|---|---|---|---|
| **1** | **Nothing is wired.** P8/P10/P11 have no caller in `src/`; no CLI; no classification detector, so every file raises `ClassificationRequired` | **Blocks everything** | `production.py:1-6`; `pipeline.py:277`; `classification.py:32-38` |
| **2** | **No catalogue data ships.** One `RoleBinding` exists, in a fixture. No residual `display_name` slot values. No `materially_improves_retrieval`. No residual partition producer | **Blocks tree design and residuals** | `fixtures.py:380-381`; `residuals.py:105-118`; `config.py:42-45`; `residual.py:145-150` |
| **3** | **The multi-life person is a hard error, not a two-branch outcome.** C6 is non-overridable; one domain per group; the ask-mechanism can only vary order | **Breaks 5 of 6 personas** | `routing.py:397-412,81-95`; `upstream.py:72`; `templates.py:392-399` |
| **4** | **13 of 23 schemas have no runtime identity; 4 of the 10 that do carry no fields** | **Breaks every professional persona** | `facts/domains.py:52-53,66-67` |
| **5** | **Every dimension label a person sees is the engine's key** — 37 of 37 field display names are the key | **Every persona, every screen** | `facts/fields.py:102-223` (re-derived) |
| **6** | **Five of eight canvas actions are unimplemented**, including merge and defer; §5.10's six existing-folder gestures have no producer at all | **The canvas is not editable as specified** | `candidates.py:58-61` vs `store.py:95-112`, `vocabulary.py:392-395,413-417` |
| **7** | **Nine residual questions block freeze, asked before the counts exist** — `00`:123 puts them after, with counts | **Nobody finishes** | `freeze.py:200-204` vs `00`:123 |
| **8** | **Scale**: retrieval O(files × nodes), health O(n²), no width cap, uncapped example lists | Fails on a real disk | `index.py:236-241`; `health.py:60-72,146`; `routing.py:487-489` |
| **9** | **The passport's abstention message misdescribes itself** as an evidence failure | Destroys trust at the sharpest moment | `pipeline.py:537-540` |

### The shortest path to yes

Not the full list. The shortest path, in order, and I would stop after step 3 and put it in front of a
real person:

1. **Ship the read-only half first (§6.2).** Wire `production.py`'s P1–P7 to a query surface over the
   evidence database. No tree, no freeze, no moves, no decisions. It is zero-risk by `00` §0's own
   promise, it needs no catalogue data, and it is the only thing here that a lawyer, a parent and a
   student would all use on day one. Everything below is easier to judge once someone has run it.
2. **Author the data that already has slots.** One `RoleBinding` per live dimension with a human
   label; nine residual `display_name` values; one `materially_improves_retrieval`; threshold
   defaults. This is authoring, not engineering, and it converts §5c and §5d from "unfixed" to
   "fixed" without touching a line of logic.
3. **Ask three questions before the canvas (§6.1).** Do you practise law / teach / have children whose
   records are here. Store the answers as corpus facts. This is the smallest change that turns §2's
   hard error into a two-branch outcome, and it is the prerequisite for making `about_person`
   eligible for Tom and ineligible for Mara.
4. Then: wire P10/P11, move the nine residual questions out of freeze to `00`:123's position with
   counts attached, implement merge/defer/drag, and fix the two O(n²) hot paths.

**The design is better than the state of the build, and `00` is better than both — except in the six
places named in §6, where it is silent about the person in ways the corpus has been telling us about
for 358 rows.** The most valuable thing in this document is §6.1 and §6.2: ask the user who they are,
and let them search before you make them decide.

**What I did not do:** touch `src/`, `tests/`, or `planning/domains/`. Every finding above was
re-derived against the working tree, and every count in it was recomputed rather than quoted.

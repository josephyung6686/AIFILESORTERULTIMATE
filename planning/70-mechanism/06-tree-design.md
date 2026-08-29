# 6. Tree design and freezing — proposing the folders (P10)

P10 is where the product stops describing the corpus and starts proposing a shape for it. It takes
accepted groups (P9), validated facts (P6), the existing-folder inventory and the protected-container
verdicts (P3), and per-file handling classes (P7), and produces **one artefact: a frozen destination
tree** — a closed set of node identifiers that every later part is permitted to place into and
nothing may add to. It moves no file, composes no filesystem path, and writes no fact.

Twenty-four modules under `src/tree_design/`, about 9,100 lines. The chain that runs them in order is
`src/tree_design/pipeline.py:493` (`design_tree`), and its eleven named steps are
`src/tree_design/pipeline.py:76-88`.

---

## 6.1 The template catalogue

### What the four records are

The library is not a list of folder shapes. It is four record kinds kept deliberately apart
(`src/tree_design/templates.py:1-32`):

| Record | What it is | Holds |
|---|---|---|
| `TemplateFragment` (`templates.py:184`) | reusable organisation logic | semantic **roles**, relative order, optionality, metadata-only roles, allowed values, a privacy floor, provenance |
| `TemplateDefinition` (`templates.py:292`) | a recipe composing exact fragment versions | fragment refs, **candidate orders**, sensitivity policy ref, example label chains |
| `TemplateApplicability` (`templates.py:474`) | the join row — one recipe, **exactly one** schema | `uses_schema`, allowed fields, **detection signal refs**, **role bindings**, provenance |
| `BranchTemplateBinding` (`templates.py:602`) | what one branch in one draft chose | resolved dimensions, accepted group ids, state, chosen order id, validation report ref, approval action ref |

Nothing about a fragment or a definition names a user's data. A fragment says "there is a level
called `subject`"; the applicability row says "in an `academic` context, `subject` resolves to the P6
field `subject` and is called *Course*"; only materialisation turns that into `PHYS1401`.

**A role binding carries a label, and the label is required** (`templates.py:441-470`). It lives on
the applicability row rather than the definition because "one role reads differently per audience,
and the audience is what a `TemplateApplicability` row selects" — `work_type` is *"homework, exams,
labs"* to a student and *"figures, drafts, protocols"* to a researcher.

**Ordering is a runtime choice, enforced structurally.** A definition carries `candidate_orders`, not
a single `dimensions` tuple, and must mark exactly one default (`templates.py:379-391`). A recipe
with more than one dimension must offer at least two orders **or** record prose in
`sole_order_attestation` saying its corpora attest only one (`templates.py:404-425`). The reasoning
is recorded at the record: enforcing a two-order floor with no exit "manufactured its own defect:
alternative orders authored to satisfy the record rather than argued from a corpus … An invented
alternative is worse than an absent one, because the user cannot tell it is invented"
(`templates.py:319-325`).

### The shipped library

Loaded through an injected reader, never by scanning (`src/tree_design/catalogue.py:122`). The seven
packaged files are named in `src/production.py:144-152`; `shipped_catalogue_manifest`
(`production.py:183`) joins them, **refuses a record that appears in two files** rather than merging
(`production.py:210-216`), and derives `release_id` as a SHA-256 digest of exactly the bytes read, in
file order — "a library that changed moves the id, and one that did not cannot"
(`production.py:189-192`). `load_catalogue` refuses a manifest with no `release_id` because "two
different libraries are indistinguishable in a frozen tree" (`catalogue.py:136-140`).

Counted from `src/tree_design/library/`:

| | count |
|---|---|
| fragments | **22** |
| definitions | **63** |
| applicability rows | **208** |
| distinct `uses_schema` values | **19** |
| rows citing **no** detection signal | **0** |
| distinct detection signals | **208** |

The last two lines matter. Every row cites exactly one signal, and no two rows share one — so the
mapping from **situation → row** is 1:1, and `--list-situations` (`src/cli.py:1021-1026`) printing
208 names is printing the row set under another name.

### What a "situation" is, and how it selects a recipe

A situation is a compiled recognition row, referenced as `recognition:{row_id}` — e.g.
`recognition:academic.coursework` beside `recognition:academic.study-abroad`
(`src/tree_design/routing.py:78-92`). `eligible_rows` (`routing.py:179`) selects a row when **both**
hold: its `uses_schema` is one of the branch's domains, **and** the branch's evidence carried one of
its detection signals.

The asymmetry is deliberate and documented (`routing.py:207-217`): a row that cites signals is
selected only on a match; a row citing **none** stays eligible on schema alone, because an empty list
is the row saying *"wherever this schema is, I apply"*, and reading it as "nothing recognises me"
"would silently retire every such row, which is a library change made by a router". In the shipped
library that branch is dead — zero rows cite no signal.

The reason schema alone was the wrong grain is recorded with numbers
(`routing.py:187-205`): eleven of the launch library's rows are `academic` and five share one
definition; collecting on schema handed all five to one composition, whose rows called `school`
*"My school"*, *"Course provider"*, *"Course platform"* and *"Host university"* — four correct names
for four audiences, "merged into one recipe that necessarily refused at C4. Twenty-nine of the
shipped library's fifty-four rows sat inside such a refusal."

**Nothing in `src/` produces a row-level signal.** `src/recognition/library/recognition.json` reports
`compiled_rows: 358` and `refused_rows: 44`, but its usable index is `schemas` — 23 entries — because
`compile_rules` unions every row's terms per schema. `pipeline.py:150-160` says so outright: "the
vocabulary exists upstream and the row-level producer does not; P10 reads the answer and writes no
rule of its own." The shipped CLI closes the gap with a person: `--situation` is a **required**
argument (`cli.py:1030-1036`), validated against the catalogue's own signal set
(`cli.py:537-551`), and then injected as a constant —
`detection_signals_for=lambda group: frozenset({signal})` (`cli.py:591`). Every group in the run is
declared to be in the same situation.

---

## 6.2 Routing and its gates C1–C8

Routing is `evaluate_composition` (`routing.py:294`) wrapped by `route_branch` (`routing.py:537`).
It takes a `BranchContext` (`routing.py:68`) — groups, domains, member file ids, handling classes,
purpose profile refs, detection signals — and returns a `RoutingReport` of **inert** candidates plus
the conflicts. It writes no node.

### The eight gates

| Gate | Refuses when | Consequence |
|---|---|---|
| **C1** | a referenced definition, fragment or version is not in the release; fragment imports cycle | `refuse` |
| **C2** | a resolved role's field is not a live, **destination-eligible** P6 field | `refuse` |
| **C3** | the branch's evidence does not satisfy the row's authored purpose profile; or no row is eligible at all | `refuse` |
| **C4** | one role resolves to two fields, **or** one (role, field) pair carries two labels | `warn` |
| **C5** | combined relative orders cycle; leave roles unordered; or allowed-value sets intersect to nothing | `warn` |
| **C6** | a member of an accepted group would be silently dropped from the preview | `refuse` |
| **C7** | (intended) the combined privacy floor is weaker than an included fragment's | `refuse` |
| **C8** | (intended) a valid composition activates without branch-specific approval | `refuse` |

The meanings are in `src/tree_design/vocabulary.py:170-179`; the consequence map is
`vocabulary.py:206-215`, and `NON_OVERRIDABLE_GATES` / `OVERRIDABLE_GATES` are **derived** from it
(`vocabulary.py:225-232`) rather than listed beside it, "because a hand-written second list is the
copy that goes stale the day a gate changes class."

The split is an owner ruling, stated at `vocabulary.py:184-205`: making the eight uniform "is wrong
in both directions — a uniform refusal makes the product unusable on an ambiguous library, and a
uniform warning makes privacy overridable by a click."

### `CompositionConflict` — what a refusal is

`CompositionConflict` (`templates.py:74`) is the one refusal object. Three properties matter:

1. **It reads its own class.** `self.consequence = COMPOSITION_GATE_CONSEQUENCE[gate]` and
   `self.overridable = self.consequence == GATE_WARN` (`templates.py:98-99`). Neither is passed in:
   "A conflict that could be told which it was would eventually be told wrong."
2. **It always offers the same five ways out** (`templates.py:88-94`): *omit one fragment, change the
   order, flatten a level, keep the branch shallow, defer.*
3. **The message names the conflicting inputs** and the choices, so a surface can render it without
   consulting anything else (`templates.py:100-104`).

`RoutingReport` then splits the conflicts into `refusals` and `resolvable` by reading each conflict's
own `overridable` (`routing.py:167-176`) — "so a surface can offer the user the choices and only the
choices."

### What a person would see

A branch whose situation nothing recognises gets a **named** C3, and the code distinguishes two
absences that would otherwise read alike (`routing.py:576-599`): *"this library holds nothing for
finance"* versus *"this library holds eighteen finance recipes and this branch's evidence recognises
none of their situations"* — "one message for both would send them to the wrong one half the time."

A branch spanning two lives is not a refusal. `route_branch` composes **one candidate per coverage**
(`routing.py:606-631`): each recipe is asked only about the groups its schemas reach, and material no
recipe reaches becomes its own C6, "named by file, non-overridable, and — unlike before — it no
longer annihilates the candidates that do cover the rest of the branch" (`routing.py:648-660`). The
history behind it is quoted at `routing.py:607-612`: a branch holding "a practice beside a degree
beside a child's health records … is a HARD ERROR on every candidate".

### Overrides

`CompositionOverride` (`routing.py:98`) **cannot be constructed for a refuse-class gate** — its
`__post_init__` raises a `CompositionConflict` if the gate is not in `OVERRIDABLE_GATES`
(`routing.py:118-124`). The reasoning is that "a record that CAN hold `gate="C7"` is one click from
honouring it". It also requires `approved_by`, "because an override with no recorded action is the
same defect C8 exists to prevent, one gate earlier" (`routing.py:125-130`). Two overrides answering
one gate is itself a conflict — "a question with two answers has none" (`routing.py:222-229`).

C4's override must name a field one of the rows actually offered; anything else is refused as "a
second door into a field no row allows" (`routing.py:387-395`). C5's override is only recorded as an
override when the derived order was a genuine **cycle**; an under-determined merge the user answered
is §5.3's runtime choice working, not a gate waved through (`templates.py:900-905`).

### The gates do not run in their numbered order

Actual execution order in `evaluate_composition`: **C1** (`routing.py:322`) → **C3**
(`routing.py:341`) → **C4** (`routing.py:353`) → **C2** (`routing.py:398`) → **C5**
(`routing.py:405`) → **C6** (`routing.py:480`) → C7 (`routing.py:496`) → C8 (`routing.py:499`).
C3 runs before C2 "so a branch that was never eligible does not spend field lookups"
(`routing.py:341-342`); C4 runs before C2 because C2 needs to know which field won.

C2 delegates to `upstream.resolve_role_to_field` (`src/tree_design/upstream.py:203`), which refuses
both an undefined field and a field P6 marks **not destination-eligible** — "§3.8 keeps an authoring
role out of the tree; it is supporting evidence, not a folder level" (`upstream.py:224-231`).

---

## 6.3 Horizontal candidates and vertical options

Two passes answer two different questions. **Horizontal**: which top-level branches should exist.
**Vertical**: how should this one branch be split.

### Horizontal (`candidates.py:217`)

A `BranchCandidate` (`candidates.py:71`) is §5.1/§5.2's card as data: label, why it was suggested,
supporting file count, accepted group ids, representative group labels, resembling existing folders,
whether sensitive content is present, source, and the actions available. **No score.**

Candidates are derived from three sources, never from a shipped list of branch names — the module
"ships no branch names at all" (`candidates.py:1-14`):

1. **accepted groups** — one card per group;
2. **existing folders** — carrying P3's curation signal verbatim, with `curated` and `undetermined`
   producing *different* `source` values and different sentences, because the scan "could not tell
   whether it is curated or incidental, so it is shown as it is and nothing is assumed"
   (`candidates.py:300-321`);
3. **user labels** — passed in.

**The only thing that removes a candidate is a recorded rejection** (`candidates.py:240`,
`provenance.py:191`). A group whose domain did not activate is still offered, with the card saying
so. The comment records why: dropping it "is how a multi-life person loses a whole life — P9
categorises their matters `law_practice`, activation does not name that schema, and every matter they
own disappears from the canvas with nothing to click and nothing to read"
(`candidates.py:255-268`).

### Vertical (`candidates.py:436`)

One `VerticalOption` (`candidates.py:102`) per routed candidate, **plus `opt_no_split`, always last
and always present**. Each option carries:

| Field | §5.5 question it answers |
|---|---|
| `resulting_child_counts` | how many branches each **level** makes |
| `total_child_branches` | how many folders in total this option creates |
| `children` (`ChildPreview`, `candidates.py:87`) | label chain + **file count** per child |
| `example_members` + `member_count` | a sample, and the true total |
| `unresolved_file_ids` | files this option gives no folder |
| `warnings` | §5.9's four warnings and the flattening recommendation |
| `validation` | the V1–V6 report |
| `protected_file_ids` | protected members — present and counted, never removed |
| `summary` | §5.5's sentence: *"This option would create three schools, five terms, and twelve courses."* |

`_summarise` (`candidates.py:342`) is that sentence. `unresolved` is the **union** of two different
absences — files routing never covered (C6) and files a level settled no value for
(`candidates.py:492-497`) — because "Both are 'unresolved' to the user, and only the first was
reported."

**A failing option stays on the canvas with its reason.** The summary appends *"It does not pass
V2 (…)"* (`candidates.py:504-509`), and the preview underneath it is built under a provisional
accepted report (`pipeline.py:399-412`) so the counts exist to show — while "Nothing is written from
a preview; the build path below uses the REAL report and is refused by it."

**Sampling.** `example_members` is `members[:sample_size(limits)]` (`candidates.py:519`). The prior
form was `members[:len(members)]` — "a slice that truncates nothing written in the shape of a
truncation, so every option carried its own copy of the branch's whole membership: at 20,000 files
that is the corpus, once per option" (`candidates.py:106-113`).

**Deferral is visible.** When `route_branch` cuts surplus candidates at
`limits.max_folder_proposals` (`routing.py:667-669`), the no-split option's summary says how many
were deferred and adds that they "are not judgements about your evidence"
(`candidates.py:530-534`).

### How an option is chosen — and that the shipped command chooses non-interactively

`vertical_options` decides nothing. The choice is `TreeDesignDecisions.choose_option`, a callable
receiving the candidate and every option (`pipeline.py:198-204`) — "a callable rather than a mapping
because the options do not exist until the chain has computed them, and a caller naming `opt_0` in
advance has chosen nothing."

The shipped CLI supplies `choose_option` at `src/cli.py:490`, and **says so in its own docstring**:

> "§5.5, non-interactively: the first nesting §5.7's checks say may be built. Stated rather than
> hidden, because it IS a choice and a person at a review screen would make a different one."

It takes the first option with children whose validation passes, and falls back to the last option —
always `no-split` — rather than raising. There is no review screen; the entire vertical surface is
computed, rendered into records, and then answered by four lines of code.

---

## 6.4 Materialisation and V1–V6

`materialise_branch` (`materialise.py:106`) is the one place evidence becomes structure. For each
resolved dimension it collects the **distinct settled values the branch's own files carry**, in P6's
spelling, via `preferred_value_for`. A file with no settled value at a level is unresolved at that
level and produces no branch. Nesting is by **shared files**, so the counts are intersections and not
products — "§5.5's 'three schools, five terms, and twelve course branches' is twelve real
combinations, not one hundred and eighty cells" (`materialise.py:15-19`).

One pass produces two views (`materialise.py:20-24`): `MaterialisedCandidate` for the checks,
`BranchEvidence` for the projection, "because a validator that saw a different shape from the builder
would pass a tree that cannot be built, or refuse one that can."

**Protected members are marked, not removed** (`materialise.py:126-146`, `materialise.py:164-166`).
They stay members, stay under their value, stay in every count, and are named in
`protected_file_ids` — "a file dropped out of the evidence is uncounted, and uncounted is worse than
present-but-untouched."

### The six checks (`src/tree_design/validation.py`)

All six run, and `run_checks` collects **every** failure rather than stopping at the first — "which
is how a review surface teaches someone that the product cannot be trusted to tell them what is
wrong" (`validation.py:249-254`). No check returns a score.

| Check | Refuses | Notes |
|---|---|---|
| **V1** (`validation.py:80`) | a level repeating a concept an ancestor or earlier level already expresses | compares on `field_ref`, falling back to the **role** for a template-local level, because comparing those on `field_ref` compared every local level against `None` and "every two-level novel-domain branch failed V1 on a difference the check could not see" (`validation.py:65-77`) |
| **V2** (`validation.py:104`) | a level producing exactly one child | *"a folder the user opens to find one folder"* |
| **V3** (`validation.py:121`) | `ancestor_depth + folder levels > limits.max_depth` | reads `tree.max_depth`; nothing is hard-coded |
| **V4** (`validation.py:145`) | a branch whose **only** level is an author/organisation field | `Applications/Columbia/Essays` is fine; a branch that is only `Columbia` is not. **Raises `ConfigurationRequired` if the collector field set is empty** — P6 owns which fields those are |
| **V5** (`validation.py:173`) | a level whose **values** would disclose protected material as folder names | asks about the **value string**, not the files under it |
| **V6** (`validation.py:227`) | a level value with no member in the accepted group | |

**V5 is the one a critic should read closely.** It previously read `handling_classes_by_value`, the
union of member classes, which meant "one passport scan under `Columbia` gave the string 'Columbia' a
protected class and V5 refused the branch. A university's name is not protected material; the
passport is. The user lost the organisation and kept none of the protection"
(`validation.py:190-196`). It now asks an **injected** predicate about the value string, and refuses
to run without one, because "P6 classifies fields and P7 classifies files, and neither classifies the
string a folder is named after" (`validation.py:202-209`).

**The ones a person actually hits are V2 and V6.** A corpus where most files carry one value at a
level produces one child (V2); a level defined for a field most members lack produces values with
zero members (V6). V3 fires only on a deliberately deep recipe, V4 only on a single-level
organisation branch, and V5 fires **never** under the shipped deployment, whose disclosure predicate
answers `False` for every value (`cli.py:600-603`).

### Date coarsening

`narrow_wide_date_levels` (`materialise.py:513`) is the one width control, applied before previews,
counts and warnings so "no number the user sees can disagree with the tree beside it"
(`candidates.py:465-471`). A level whose values are **all** whole days (or all whole months) and
wider than `max_folder_proposals` is coarsened by dropping the last hyphen component — day → month →
year — which is a **prefix of the value the fact already carries**, so no label is invented and no
file leaves the branch.

Only dates. The reasoning is at `materialise.py:526-536`: capping a level of 400 courses "means
either dropping 300 courses, which is the silent omission the standing rule forbids, or merging them
by something the evidence never said, which is invention. There is no third option for values with no
structure." The trigger was a real run: "A capture-date split on a real photo library proposed 337
folders with that ceiling set to six."

---

## 6.5 The depth and breadth ceilings

Until **2026-08-29** P1 published one key, `tree.max_folder_proposals_and_depth`, for the two numbers
`00`:256 names on one line ("Maximum folder proposals and maximum depth"). P10 read that single value
for **four** questions (`src/tree_design/config.py:6-13`):

1. how many **options** the picker offers (`routing.route_branch`);
2. how **deep** a candidate may go (`validation._v3`);
3. how **wide** a date level may be before coarsening (`materialise.narrow_wide_date_levels`);
4. the **sample size** of the printed lists (`health.sample_size`).

The first two want opposite values and no P10 change could reconcile them: `00`:78's own recommended
tree, `Academics/Columbia/2026-Spring/PHYS1401/Homework`, is five levels deep, "and a picker offering
five options per branch is not a picker" (`config.py:14-18`). The failure was standing evidence, not
an argument — `test_one_ceiling_can_serve_both_the_picker_and_the_depth_limit`.

Since 2026-08-29 P1 publishes both (`src/database_agent/budget.py:41-42`, with the ruling recorded at
`budget.py:28-40`):

| key | controls | read by |
|---|---|---|
| `tree.max_folder_proposals` | **breadth of what the interface shows at once** — options offered per branch, width of a date level before coarsening, sample size of every printed list | `routing.py:667`, `candidates.py:472`, `health.py:53` |
| `tree.max_depth` | **how deep a candidate may nest** | `validation.py:135`, and nothing else |

`config.py:22-25` is honest that this is not fully clean: "That is still three questions on one
number, and it is the reading §8.6's words plainly carry: all three are 'how many things does the
interface put in front of the user at once'. Depth was never that question, which is why it is the
one that left."

§5.9's own thresholds — excessive depth, tiny-folder size, tiny-folder count, and the
materially-improves-retrieval test — have **no ceiling key at all** and are mandatory injected
arguments (`config.py:78-106`). Absent, or non-positive, raises `ConfigurationRequired`: "a default
here would be P10 authoring the design" (`config.py:70-74`).

---

## 6.6 Health and warnings

`warnings_for` (`health.py:287`) is the single implementation of §5.9, used both for the live preview
of an unchosen option (`candidates.py:416-434`) and for a built tree — "a second copy of §5.9 is a
second copy that drifts."

Five findings:

| kind | fires when |
|---|---|
| `one-child-level` | a level has exactly one child **and nothing below it divides**, and its parent is not itself single-child |
| `repeated-parent-concept` | this level's `dimension` equals one an ancestor already expresses |
| `excessive-depth` | depth > `excessive_depth_warning` **and** the levels above express fewer distinct concepts than the depth |
| `tiny-folder-distribution` | ≥ `tiny_folder_count_warning` children hold ≤ `tiny_folder_max_files` files |
| `flatten-recommendation` | the injected retrieval test returns `False` — `None` never rounds to `False` (`config.py:62-65`) |

**Two of these used to measure the wrong thing and fired on the design's own recommended path**
(`health.py:300-326`). `Academics/Columbia/2026-Spring` is three single-child levels in a row, and
`00` recommends it, because each supplies context for the work-type folders that *do* divide beneath.
So one-child now asks whether anything below divides, and fires **once for the whole run** rather than
once per level. And excessive depth is no longer a second absolute-depth rule — V3 is the absolute
one, and refuses; the warning asks whether the path is deeper than the number of distinct concepts it
expresses. There is deliberately **no** uneven-depth warning: §5.8 makes uneven depth a requirement.

### Ranking, sample size, and the 2,991

Recorded history: a 3,200-node tree produced **2,991 warnings**, one node per sentence, unranked
(`health.py:328-329`; measured in `planning/58-SCALE-STRESS.md:393`, where the ratio climbs to 1.18
warnings per node at 12,800 — more warnings than folders). §5.11 asks for "a good enough structural
gist … so that only a LIMITED NUMBER of high-leverage changes remain", and "a warning that fires on a
correct tree spends that budget on nothing and teaches the user to skip the list, which is worse than
having no list at all" (`health.py:13-17`).

`_ranked_and_summarised` (`health.py:426`) sorts by **subtree size** — "a fact already computed and
not a score: fixing the level that holds nine hundred folders is worth more than fixing the one that
holds two" — then, per kind, keeps `sample_size(limits)` and replaces the rest with one counted line.
Post-repair: **21 warnings, ranked** (`planning/63-IMPLEMENTATION-PLAN.md:222`).

**One exemption, and it is the standing rule.** A warning on a `protected` node or an
isolated-sensitive one sorts first and is **never** summarised away, because "a shortened list that
dropped the line saying 'this area was protected and not opened' would be that omission arriving as a
usability improvement" (`health.py:330-334`).

The `_TreeIndex` (`health.py:87`) computes children, depth, distinct ancestor concepts, descendant
counts and "does anything divide below" in one O(n) pass; the previous shape took 3.3s at 3,200 nodes
and projected to fourteen minutes at 50,000. A node the breadth-first walk never reaches sits under a
cycle — `tree_nodes.parent_node_id` carries no foreign key — and is refused by name rather than
hanging the canvas (`health.py:144-151`, `health.py:219-230`).

`tree_health` (`health.py:480`) returns §5.11's six measures — per-group coverage, files with enough
facts, unresolved nodes, context-supported nodes, sensitive-isolated nodes, nodes needing decisions —
and deliberately **no completeness score**: "A single number would be read as a grade to raise, which
is the opposite."

---

## 6.7 Freezing

### What a freeze record contains

`FreezeRecord` (`freeze.py:86`) is §8.8's adopted-version row — **ids and configuration only**:

`plan_version_id` · `created_at` · `node_ids` · **`legal_destination_ids`** · `template_bindings` ·
`labels_and_aliases` · `residual_configuration` · `shared_material_policy_ids` ·
`cross_folder_moves` · `selection_id` · **`catalogue_release_id`** · **`template_versions`**.

`legal_destination_ids` is a frozenset, and legality is a set-membership test —
`is_legal_destination` (`freeze.py:150`) is one line. That shape is the whole design: "an answer that
needed a join could disagree with itself the day the join changed" (`freeze.py:4-8`). The set is
read off `node.accepts_placement` and re-derives nothing (`freeze.py:459-464`).

`FrozenTree` (`freeze.py:117`) is what freeze **hands over**: the record plus the nodes plus the
§6.1 profiles plus the resolved shared-material policy **value** (not an id list, "because §6.9 makes
P11 branch on which of four rules applies, and an id list cannot tell it which"). The bundle is
written once, as canonical JSON, inside one transaction with the version flip and the adoption event
(`freeze.py:484-499`) — rebuilding profiles at read time "would consult all three, against a P9/P4/P6
state that has moved on since the user adopted this plan."

### `catalogue_release_id`

`planning/64-USER-EDITS-AND-CATALOGUE-UPGRADE.md:37` named this the fourth hole: "A frozen tree does
not record which catalogue release built it. A library upgrade is therefore not merely unhandled — it
is *undetectable*." The value already existed — `load_shipped_catalogue` derives it as a digest — and
was simply not carried onto the tree (`freeze.py:99-107`).

`catalogue_release` (`freeze.py:133`) **refuses rather than reporting `None`**: "Reporting `None` as
the release would be worse than refusing — two different libraries would compare equal."
`template_versions` sits beside it as the deduplicated `(template_id, template_version)` set the tree
actually used, "so an upgrade that republished one definition can be told from one that republished
all of them" (`freeze.py:109-113`).

### What freeze refuses

`validate_for_freeze` (`freeze.py:155`) returns **every** reason at once, not the first: "a user who
fixes one and is handed the next has no idea how many remain" (`freeze.py:57-61`). The reasons:

1. the version holds no node;
2. a named approved branch is not in this version;
3. **a node that is a legal destination carries no `refinement_disposition`** — checked on
   `accepts_placement`, not only on what the caller names, because P11's index "raises
   `FrozenTreeRequired` on any legal node with a falsy `refinement_disposition`, so a version that
   froze without one broke at the consumer — where the user cannot act on it — instead of here"
   (`freeze.py:189-202`);
4. a `protected` node that accepts placement;
5. **a protected area the scan marked with no node in this version** — matched on `display_label`,
   which is the only identifier a protected node can carry, and the limit is reported rather than
   papered over (`freeze.py:208-224`);
6. **no §6.9 shared-material policy** (below);
7. a residual template with no recorded enablement state.

### The shared-material policy (§6.9) and why freeze refuses without one

§6.9's four answers are `shared-branch`, `primary-home`, `reference-or-alias`, `mandatory-review`
(`vocabulary.py:352-354`). Three of the four resolve to a destination; `mandatory-review` deliberately
does not, "so a branch created for it would answer the question the policy exists to keep open"
(`vocabulary.py:356-367`).

The gate is **unconditional**, and that is argued rather than assumed (`freeze.py:226-237`): whether
any file will turn out to belong in two homes is computed during *placement*, from retrieval, "so
whether any file will turn out to belong in two homes is not knowable at freeze by anyone. The
question is never contentless — it is 'what should happen IF'". Without the gate "the user designs a
tree, reviews it, approves it, presses freeze, IT FREEZES — and `build_destination_index` refuses at
the next stage, phrased as a contract violation about a policy nobody asked them to choose."

The policy is stored with an explicit `policy_scope` column, `NULL` meaning tree-global, with a
partial unique index allowing exactly one global row per version (`schema.py:91-103`) — SPEC open
question 9 (global or per-branch) is answered **per record** rather than settled by the schema.
`_carry_shared_material` (`store.py:268`) copies it onto every new draft with a fresh `policy_id`,
because previously a draft lost it and "A user who chose `primary-home` and then renamed one folder
was told they had chosen nothing."

### Refinement dispositions

`refined` / `shallow-by-choice` / `refine-later` (`vocabulary.py:78-84`) — three, not two, because
"collapsing them would make a deliberate design look like unfinished work". A disposition without a
`refinement_reason` is refused at construction (`records.py:226-236`).

The field is optional on `Node` and required in a `FrozenTree`, deliberately: "a draft node has not
been approved yet — a required field would make the state the user is actually in while editing
unstorable" (`records.py:166-173`). Nothing in P10 wrote it until `_with_refinement`
(`pipeline.py:444`) — "every tree P10 actually built carried `None` on every node, and
`build_destination_index` refuses such a tree WHOLE." The answer arrives injected as
`decisions.refinement_for`, applied at the one place that writes, and only to nodes that accept
placement.

### Residual enablement decisions

The nine §7.3 names are fixed (`vocabulary.py:268-278`); the eight §7.2 slots are enumerated
(`vocabulary.py:299-308`); §7.3's four stated default parents are recorded and the other five are
**not invented** (`vocabulary.py:282-287`). `build_library` (`residuals.py:85`) refuses a template
missing any slot but `default_parent_location`, which is the one slot whose absence is legal.

The six §7.4 actions (`vocabulary.py:336-339`) are named `RESIDUAL_LIBRARY_ACTIONS`, not
`RESIDUAL_ACTIONS`, because `llm_harness.vocabulary.RESIDUAL_ACTIONS` is already live and holds
§7.7's **eight review actions** — "Two different closed sets under one name in one pipeline is a
misspelling waiting to become a silent downgrade" (`vocabulary.py:328-335`).

`project_residual_nodes` (`residuals.py:140`) turns the choices into nodes. `disable` is the only
action producing none, and that is the whole enforcement mechanism: "a template the user did not
enable has no node, so no placement decision can name it and no model can return it"
(`residuals.py:179-191`). Enabling without a disposition is refused; enabling without a root anchor is
refused, "so the anchor is the user's to choose and P10 has none to fall back on"
(`residuals.py:214-219`); two decisions for one template are refused because they "produced two
branches with the same display name and nothing said which one P11 would place into".

`derive_accepts_placement` (`records.py:64`) **deliberately does not read the disposition**
(`records.py:73-84`): all three dispositions produce legal nodes; the disposition governs what happens
*when* a node is chosen, not whether it can be.

**The shipped CLI enables none of them.** `RESIDUAL_LIBRARY = {}` (`cli.py:222`), with the reason
stated: this deployment "enables NONE rather than inventing slot values: an unplaced file still
reaches §7.5's review set with its reason, so it is counted and explained … without a folder nobody
designed."

---

## 6.8 User edits and catalogue upgrades

### The overlay key

`user_level_edits` is keyed on **`(uses_schema, role_ref, field_ref)`** and on nothing else
(`schema.py:125-139`, `user_edits.py:10-29`). Two obvious keys fail:

- **`node_id` fails.** §8.8 mints a new one per plan version — "exactly the bug the seam pass found in
  `learned_preferences_still_applicable`: filtering on `node_id` made every learned preference
  silently stop applying at the first tree edit."
- **`template_id@version` fails.** "It is the PACKAGING, and packaging is precisely what a library
  upgrade changes."
- **The triple holds** because it is the **vocabulary**: *"whatever level shows my `subject` field in
  an `academic` context, I call it Class"* stays true across a re-route, a re-version and an upgrade.

It is **per-schema, not global**: renaming *Course* to *Class* in an academic context renames nothing
in a research one — the same reason `RoleBinding.label` lives on the applicability row.

`basis` is P7's `USER` constant, imported rather than respelled (`vocabulary.py:145-151`), and a
record with any other basis is refused: "an inferred basis here would be the system overruling the
person on their own words" (`user_edits.py:111-115`). A path separator in `display_label` is refused
at construction, before storage (`user_edits.py:120-125`).

### It applies at the END of routing

`apply_user_level_edits` (`user_edits.py:194`) is called as the last statement of
`evaluate_composition`, after every gate (`routing.py:502-508`). The reason is stated in both places:
"two rows that name one role two ways is a C4 refusal, and a rename applied first would collapse them
into the user's single name and let a composition C4 exists to refuse ship as valid."

Only `display_label`, `action` and `proposed_label` move; `field_ref`, `order_index` and `scope` are
untouched, "because a rename that changed any of those would be a structural edit wearing a label's
clothes" (`user_edits.py:207-212`). The release's own proposed name is preserved as `proposed_label`
so an upgrade can say *"the library called this Course when you renamed it to Class; it now calls it
Module"* (`user_edits.py:80-85`).

An edit naming a level this composition does not have is **surfaced, not resolved**, as an
`UnappliedUserEdit` (`user_edits.py:132`) carrying one of `diff.py`'s own words — `re-templated` if
the role exists under another field, `removed` if the level is gone — so "'what changed when I
updated' and 'what changed when I edited' read the same way". Two of the user's own edits disagreeing
across two schemas in one composition raises `UserEditRefused`: "One question with two answers has
none" (`user_edits.py:244-254`).

### Only a rename has a writer

The record can hold any of the six `DIMENSION_ACTIONS`, so the overlay is shaped to carry a reorder or
an omission the day one is built. The **writer** refuses everything but `renamed`, before storing
anything (`user_edits.py:155-163`): "an edit nothing can apply is a silent no-op that survives every
future session, and the user would see their edit accepted and never honoured."
`OVERLAY_ACTIONS_WITH_A_WRITER` is a one-element tuple (`user_edits.py:64`) and is "where that list
grows, one action at a time."

### The diff (`src/tree_design/diff.py`)

`diff_versions` (`diff.py:50`) compares two versions **by `origin_node_id`**, "which is what survives
a copy", and emits §8.8's seven kinds — added, removed, renamed, re-parented, re-ordered,
re-templated, type-changed — each with a semantic undo label, "because a diff the user cannot act on
is a report rather than a control" (`diff.py:10-11`).

`_PARENT_NOT_IN_VERSION` (`diff.py:118`) is a sentinel distinct from `None`: reporting a dangling
parent as `None` would say the node moved to the top level, and reporting the raw `parent_node_id`
"is worse still — that id is minted PER VERSION (§8.8), so the two sides can never compare equal and
every child of a removed node reads as re-parented."

### What `66` §17 requires and what is not built

`planning/66-FIND-FILE-AND-ONBOARDING.md:576-580` requires that when a user edits or re-runs a
**structural answer**, "the product creates a draft plan version. It shows a meaningful diff: which
schemas become active or inactive, which templates are affected, which branches may need review,
which placement proposals become invalid or newly possible, whether any protected area changes, and
whether any filing policy is paused."

**The storage half is built. The consent-and-presentation half is P13 and is not built.** The overlay
persists; the diff computes; `apply_review_action` opens the draft. But nothing in `src/` calls
`diff_versions`, and the surface that would present a diff and collect an adoption is P13 —
specification only, with `pipeline._Action` (`pipeline.py:423`) standing in as `src/`'s copy of P13's
`review_action` "because a source module may not import a test one, and the day P13 ships both are
replaced by its record."

---

## 6.9 Protected areas in the tree

The standing rule is quoted verbatim in the code (`candidates.py:150-153`): *"reports, apps and system
files MUST NOT BE MOVED OR READ OR ANYTHING SYSTEM OR SENSITIVE IN THAT SENSE."* A protected container
is **marked and counted, never opened**, present-but-untouched with a reachable explanation, never
silently omitted.

The mechanism is four independent pieces that agree:

1. **P3 marks it.** `upstream.protected_areas` (`upstream.py:283`) selects on
   `rule == RULE_PROTECTED_CONTAINER`, not on the display label — "Selecting on the display string
   would make a presentation change silently alter which areas the tree represents."
2. **P10 builds a node for it.** `protected_area_nodes` (`candidates.py:143`) mints one
   `node_type=PROTECTED` node per area, with an explanation stating that the scan "marked and counted
   it and never opened it … It is shown here so that it is accounted for rather than missing."
   There is deliberately **no** `protected_movement_permitted` parameter: §8.4 contemplates a user
   policy permitting movement for other protected material, but P3's rule for applications and system
   items is stronger and says "no policy, approval, or user gesture makes them movable"
   (`candidates.py:168-180`). The scope bound is explicit — this producer is for P3's containers and
   nothing else; "sensitive personal material is not the same thing as `Numbers.app`."
3. **The flag derives to `False`.** `derive_accepts_placement` returns
   `bool(protected_movement_permitted)` for a protected node (`records.py:89-90`), and
   `Node.__post_init__` refuses a stored flag that disagrees with the derivation
   (`records.py:197-207`). So the node is in the tree and is **not a legal destination**.
4. **Freeze refuses to lose it.** `validate_for_freeze` refuses a protected node that accepts
   placement, and refuses a version missing any area the scan marked (`freeze.py:203-224`).

`represent_protected_areas` (`freeze.py:257`) is the join, and it runs **before** the profiles are
built, "not inside `freeze`", because §6.1 requires a profile for every frozen node and "nodes written
after the profiles were computed would be nodes P11's index refuses to build over". The history is
recorded: for a while nothing in `src/` connected `upstream.protected_areas` to
`candidates.protected_area_nodes`, "so a protected container was pruned by the scan and then absent
from the tree — silently omitted, the one outcome the owner's standing rule names."

Two other places carry the same rule. `materialise_branch` marks protected members rather than
removing them (§6.4 above). `profiles.redacted_for_egress` (`profiles.py:194`) drops file
identifiers and excerpt handles from a protected profile and **nothing else** — "Dropping the profile
entirely would be the omission; dropping only what reads or exposes contents is the rule."

---

## What looks wrong here

**1. C7 and C8 never refuse anything.** Every other gate raises `CompositionConflict` with its own
constant; C7 is `floor = merged.privacy_floor` (`routing.py:496-497`) and C8 is a comment
(`routing.py:499`). A grep for `CompositionConflict(C7` or `CompositionConflict(C8` finds nothing in
`src/`. Yet every returned candidate sets `gates_passed=tuple(COMPOSITION_GATES)`
(`routing.py:528`) — asserting all eight passed. C7's actual behaviour is `max(floors,
key=privacy_rank)` inside `merge_fragment_constraints` (`templates.py:920`), which cannot fail as
long as `privacy_rank` totally orders the floors; if it does not, the code raises
`ConfigurationRequired`, not a C7 conflict. "C1–C8 are independently falsifiable" is P10 SPEC Done-means
13; two of the eight have no failure path at all.

**2. No production caller can construct an override, so the two warn-class gates behave as refusals.**
`CompositionOverride` is referenced only inside `routing.py`. Neither `pipeline.design_tree` nor
`cli.py` builds one, and `route_branch`'s `overrides` parameter defaults to `()`. A C4 or C5 conflict
therefore ends the candidate exactly as a C1 does, and the "resolvable" half of `RoutingReport` is
always empty in a real run. The distinction the vocabulary carefully derives has no consumer.

**3. §8.7's negative-feedback loop reads a record nothing writes.** `suppressed_branch_basis_keys`
(`provenance.py:191`) filters on `polarity == REJECT_POLARITY`. All three `record_tree_edit` call
sites pass `polarity="accept"` (`store.py:452`, `:558`, `:601`), and no other P10 code writes a
learning record. A deleted branch candidate therefore cannot be suppressed — the SPEC's "A deleted
branch candidate must not reappear on the next pass" has a reader, a key function, and no writer.

**4. Five whole modules are inert.** No caller in `src/` outside their own file:
`diff.diff_versions` (§8.8's node-level diff), `health.tree_health` (§5.11's six measures),
`profiles.redacted_for_egress`, `stage_output.emit_tree_design_stage` and
`emit_template_generation_stage` (so **P2 receives no envelope from either of P10's two §8.5
stages**), `provenance.record_template_application` (so §8.2's `template application` event is never
appended), `user_edits.record_user_level_edit` (the overlay has a reader and no writer),
`freeze.catalogue_release`, `freeze.is_legal_destination`, `templates.branch_dimension_roles`, and
`upstream.rejected_group_ids` / `renders_as_branch`. Tests exercise most of them; production does not.

**5. `BranchTemplateBinding` is never constructed in `src/`.** The record that is supposed to be the
one thing that may contribute nodes to a tree — "Only a branch-local binding that passes the
composition checks … and receives explicit user approval may contribute nodes" (SPEC) — exists only
as a class. `chosen_order_id`, `state`, `approval_action_ref` and `validation_report_ref` are written
by nothing. Consequently `branch_dimension_roles`, its "only reader", reads nothing, and the C8
promise that approval is recorded is enforced by no code path that runs.

**6. No node in a real run carries a `template_context`.** The CLI injects
`template_context_for=lambda field_ref, order_index: None` (`cli.py:604`). So
`FreezeRecord.template_bindings` is always empty, `DestinationProfile.template_binding` is always
`None`, and `diff._template_key` always compares `None` to `None` — the "re-templated" diff kind
cannot fire.

**7. The CLI's ceilings and its `TreeLimits` disagree.** `_bootstrap` writes `CEILING_VALUE = 8` to
**every** key including `tree.max_folder_proposals` and `tree.max_depth` (`cli.py:123`, `:533`), then
the run uses a hand-built `TREE_LIMITS` with `max_folder_proposals=4, max_depth=5` (`cli.py:131`).
`config.tree_limits` — the function whose entire purpose is to read those keys and refuse an absent
one — has **no caller in `src/`**. The stored ceilings are decoration.

**8. Stale counts in three docstrings.** `store.apply_review_action` says "this function writes three"
and "The other twelve are named in `ACTIONS_WITH_NO_WRITER`" (`store.py:484-491`); the sets are
actually five and ten (`store.py:93-108`). The comment at `store.py:583` repeats "`ACTIONS_WITH_A_WRITER`
has three members". `user_edits.py:35` says `apply_review_action` "refuses its twelve".
`health.py:316` says V3 "uses §8.6's published `tree.max_folder_proposals`" — it reads `tree.max_depth`
(`validation.py:135`). `records.py:171` says "`freeze` refuses to hand over a bundle carrying a `None`
anywhere"; `validate_for_freeze` checks only approved-or-legal nodes, so a protected or ignored node
with `None` freezes fine.

**9. Ordinals collide.** `_write_overlap_answer` gives a new child `ordinal=parent.ordinal + 1`
(`store.py:428`) — the parent's own sibling index, applied to a child. `project_residual_nodes`
numbers residual nodes from 0 across all parents (`residuals.py:160`, `:281`), and
`_project` numbers each level's children from 0 (`materialise.py:427`). Two nodes under one parent can
share an ordinal, and `ordinal` is what §5.12 calls "sibling order as the user arranged it".

**10. `residual_refinement` can produce an unfreezeable tree.** `_enable_residual_library`
(`pipeline.py:745`) applies `decisions.residual_refinement` to every residual node. If that is `None`
— which is exactly what the CLI passes (`cli.py:615`) — an enabled residual node accepts placement,
carries no disposition, and `validate_for_freeze` refuses the whole version. The CLI escapes only
because `residual_choices=()`.

**11. The situation detector does not exist, and the CLI substitutes a single global answer.**
`recognition.json` compiles at schema grain (23 schemas), the template library keys on 208 row-level
signals, and nothing bridges them. The CLI asks a human for one `--situation` and asserts it for every
group in the corpus (`cli.py:591`). For the north-star multi-role person — whose disk holds coursework
*and* a legal practice *and* a child's records — this is precisely the case the per-coverage routing
in `route_branch` was built to handle, and the shipped entry point makes it unreachable.

**12. `protected` node role vs. type is still ambiguous, and the code carries both.**
`protected_area_nodes` sets `node_type=PROTECTED` **and** `node_role=ORDINARY`
(`candidates.py:196`, `:208`), while `handling_class` carries P7's answer separately. SPEC open question 3
is open. `health._protected` (`health.py:417`) therefore has to check *two* records to decide whether
a warning may be summarised away — and a protected area with a non-protected `handling_class` and no
`sensitive_isolated` count would fall through both.

**13. `validate_for_freeze` matches protected areas by `display_label`.** Two protected bundles with
the same basename in different directories are indistinguishable, and the code says so
(`freeze.py:212-216`) rather than fixing it. A user with `~/Projects/build/Numbers.app` and
`~/Archive/Numbers.app` gets one node and a freeze that believes both are represented.

**14. `health._INDEX_CACHE` holds exactly one entry and clears on every miss** (`health.py:172-184`).
`warnings_for` and `branch_counts` are called per node with the whole tree, so alternating between two
trees — a preview and the built tree, which `vertical_options` does per option — thrashes the cache
back to O(n²). Nothing measures it.

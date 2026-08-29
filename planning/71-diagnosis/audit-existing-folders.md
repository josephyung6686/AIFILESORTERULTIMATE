# Audit — does the product use the folders the person already made?

Read-only diagnosis. Nothing under `src/` or `tests/` was changed. Every claim is cited to a
line; the numbers come from two live runs of the shipped command over a corpus built for this
audit outside the repo.

---

## Verdict

**The library reads the person's existing folders and offers every one as a top-level branch
card. The shipped command discards all of them, unread, one line later. And no code anywhere in
`src/` can write a node of type `existing`, so even a chosen folder would enter the tree as a
fresh proposal wearing the folder's name — not as the folder.**

The failure class the critique describes is present here, but the mechanism is not the
one that was guessed. `src/cli.py` does **not** pass an empty tuple. The parameter is
genuinely populated from the scan: 8 real directories in, 8 branch cards out. The loss
happens at the selection filter immediately after, and it is total.

Measured on a corpus with four levels of real nested structure:

| | nested corpus | flat control |
|---|---|---|
| directories on disk | 8 | 1 |
| files | 10 | 10 |
| files living inside a folder the person made | 8 of 10 | 0 of 10 |
| existing folders P3 recorded | 8 | 1 |
| branch candidates derived from them | 8 | 1 |
| **branch candidates chosen** | **0** | **0** |
| nodes in the proposed tree | 1 | 1 |
| nodes of type `existing` | 0 | 0 |

**The two proposed trees are identical.** One folder, named `Coursework`, which is the
string the operator typed at `--label`. Flattening a four-level hierarchy into a single
directory changed the proposal not at all. That is the sharpest statement of the finding:
on the shipped path, the tree is invariant to the user's existing structure.

---

## 1. What the design says, quoted rather than paraphrased

The canonical sentence is quoted verbatim inside a refusal, `src/tree_design/pipeline.py:521-525`:

> `"none of {sorted(decisions.branch_group_ids)} is a top-level branch candidate for {decisions.from_plan_version!r}. §5.3 builds the top level out of accepted groups, existing folders and user labels, and a tree with no branch is not a design the user approved"`

The design it cites, `planning/00-database-agent-product-design.md:67`:

> "The engine aggregates the accepted groups, domain memberships, existing curated folders, and user-approved labels into a small set of proposed major areas."

`:100` adds the six gestures and the rule that "Existing folders must not be automatically
flattened, renamed, or reorganized simply because a template would produce a different
structure", and calls a curated folder "a strong expression of user intent".

`:102`: "The output of this stage is a proposed destination tree: an editable hierarchy of
existing folders, user-created folders, and evidence-backed proposed branches. Each node has a
type—existing, proposed, user-created, protected, or ignored". So the design is unambiguous:
the person's folders are supposed to be *nodes in the tree*, of a distinct type.

---

## 2. Question 1 — does `src/` use existing folders as a source of proposed folders?

### It reads them. Really.

`src/tree_design/pipeline.py:277-282` (`_upstream`) reads all four upstream sources,
including `existing_folders(conn, scan_run_id=authorities.scan_run_id)` at line 279.
`src/tree_design/upstream.py:233-257` runs P3's `directory_inventory` and returns one
`ExistingFolder` per directory, carrying `directory_path`, `parent_directory`,
`file_count` and `curation_signal`.

`src/tree_design/pipeline.py:515-517` passes them straight into the horizontal pass:

```
    candidates = horizontal_candidates(
        conn, accepted=groups, existing_folders=folders, user_labels=(),
```

**`existing_folders` is not an empty tuple on the shipped path.** The audit brief's
hypothesis is wrong on this point, and the truth is worse-shaped rather than better: the
data arrives, is turned into product surface, and is then thrown away.

`src/tree_design/candidates.py:300-322` builds one `BranchCandidate` per folder, with a
real explanation ("An existing folder holding N file(s)"), the folder's file count as
`supporting_file_count`, and the full `_BRANCH_ACTIONS` set. This code is correct and
does what §5.3 asks.

### Then it discards every one of them.

`src/tree_design/pipeline.py:518-519`:

```
    chosen = tuple(candidate for candidate in candidates
                   if candidate.subject_id in set(decisions.branch_group_ids))
```

The `subject_id` of a group candidate is the group id (`candidates.py:287`). The
`subject_id` of a folder candidate is the **directory path** (`candidates.py:304`). A user
label's is `f"user-label:{label}"` (`candidates.py:333`).

What the shipped deployment puts in `branch_group_ids`:

* `src/cli.py:626` — `branch_group_ids=tuple(accepted)`
* `src/production.py:587` — `accepted = tuple(decisions.accept_groups(conn, grouping) or ())`
* `src/cli.py:652-655` — `accept_groups` delegates to `review_and_accept`
* `src/cli.py:450` — `merged_id = f"{PLAN_VERSION}:{label}"`
* `src/cli.py:478` — `return (merged_id,)`

So `branch_group_ids` is a one-element tuple holding a synthetic group id built from the
`--label` string. It is never a directory path, and it never can be. **Every
folder-derived candidate fails the filter by construction.**

Confirmed by direct probe against the run's own database, replaying
`horizontal_candidates` with exactly the arguments the chain gave it:

```
existing folders P3 recorded: 8
candidates derived from those folders: 8
  source=existing-folder-undetermined  label=PHYS1401   files=3  subject_id=.../corpus/Uni/PHYS1401
  source=existing-folder-undetermined  label=MATH2010   files=2  subject_id=.../corpus/Uni/MATH2010
  source=existing-folder-undetermined  label=2026       files=2  subject_id=.../corpus/Taxes/2026
  ... 5 more (corpus, Photos, Taxes, Uni, 2025-Trip), all `existing-folder-undetermined`

branch_group_ids the CLI passes: ['plan_0:Coursework']
any folder candidate whose subject_id is in that list?  False
```

Eight cards built. Eight cards dropped. Nothing records that they were dropped.

### Four further blocks, each independently sufficient

Even if a caller selected a folder candidate, four separate things stop it becoming the
person's folder:

**(a) The node type is hardcoded.** `src/tree_design/pipeline.py:472-473` — `_top_level_node`
constructs `Node(..., node_type=PROPOSED, ...)` for *every* candidate regardless of source,
and never sets `existing_path`. A folder adopted as a branch becomes a **proposed** node
that borrows the folder's display label.

**(b) Nothing in production writes `existing_path`.** The column exists
(`src/tree_design/schema.py:61`, `CHECK (existing_path IS NULL OR node_type = 'existing')` at
`:66`), the record enforces it (`records.py:164, 209-211`), the store persists it
(`store.py:61, 187, 232`). The only non-`None` assignment in the repo is
`src/tree_design/fixtures.py:199`, a test fixture; every production site passes `None`
(`candidates.py:212`, `store.py:588`). The `existing` node type is reachable only from fixtures.

**(c) `adopt-existing` is refused by name.** `ADOPT_EXISTING` (`vocabulary.py:409`) is a member
of `ACTIONS_WITH_NO_WRITER` (`store.py:109-112`) and `apply_review_action` refuses it before any
lookup (`store.py:510-517`): "is one of the ... tree edit actions P10 defines and has not built a
writer for". The refusal is honest and well-placed. It is also the whole feature.

**(d) §5.10's six actions have no consumer.** `EXISTING_FOLDER_ACTIONS` — `PRESERVE,
ADOPT_AS_BRANCH, MERGE_WITH_PROPOSAL, ATTACH_BENEATH, RENAME_PROPOSAL_TO_MATCH,
LEAVE_UNTOUCHED` — is declared at `vocabulary.py:398-405` and registered at `:547`. Grepping
`src/` and `tests/` returns those two lines and nothing else. **No code dispatches on any of
the six.** They are the gestures §5.10 gives the person for their own folders; all six are
vocabulary only.

**(e) The residual "map onto my existing To Sort folder" path is dead by construction.**
`residuals.py:221-249` handles `REPLACE_WITH_EXISTING` by looking the target up in
`existing_nodes` and raising `ConfigurationRequired` when absent. Nothing writes an `existing`
node, so the map is always empty and the branch is unreachable — although design doc `:121`
names this exact case.

**(f) The curation signal is permanently `undetermined`.** `src/scan_agent/inventory.py:42-53`
— `curation_signal()` returns `CURATION_UNDETERMINED` for every directory, deliberately and
with the reason stated (§1.1 gives no threshold). So at `candidates.py:302, 319` the `curated`
branch — the one that would say "a strong expression of your intent" — can never be taken.
Every folder card today reads `source="existing-folder-undetermined"`; measured 8 of 8. The
design sentence at `00:100` has no code path that can fire.

### Where the library does honour it

`tests/p10/test_p10_multi_life.py:448-467` proves the chain does not *crash* on a folder
candidate — a real repair, correctly made. But it asserts
`node.associated_group_ids == ()`, `branch.routing.candidates == ()`, and
`[c.gate for c in branch.routing.conflicts] == ["C3"]`. A folder names no accepted group, so
it carries no `group_category`, so it is eligible for no applicability row and C3 refuses it.
A bare labelled node with nothing beneath it and a recorded conflict is the *ceiling* of what
adopting a folder can produce today.

---

## 3. Question 2 — where else does existing structure enter?

It enters in three real places, and every one of them is upstream of the tree. None of them
reaches it.

**P1/P3 record it.** `parent_folder_context(path)` at `src/scan_agent/basic_record.py:26`,
attached at `:80`, stored in the `directory_position` column (`database_agent/db.py:179`,
`database_agent/files_table.py:232, 242, 275`; `:243` notes the column name is not §2.9's
published name, "parent-folder context").

**P4 emits it as an observation.** `src/extractors/filesystem.py:79-89` publishes the parent
folder as a `possible`-reliability observation in the `path` zone — evidence about a *file*,
never structure. **P6 uses it as a session boundary**: `src/facts/session.py:98` declares
`require_same_parent_folder_context`, `:162-165` enforces it.

**P9 uses it as retrieval channel 4.** `src/grouping/retrieval.py:264-292`,
`_related_folder_neighbors`, whose docstring at `:267` says exactly the right thing:

> `"Channel 4. An existing curated folder is the user's own grouping."`

It is the only channel that publishes a `bridge_entity` (`:288`), so §4.3's hub suppression
can fire on a `~/Downloads` that bridges half a corpus. It is wired in at `:397`.

**This channel is demonstrably live and demonstrably structure-sensitive.** Edge counts from
the two runs:

| `group_edges.edge_type` | nested corpus | flat control |
|---|---|---|
| `existing-related-folder` | 9 edges, 0 hub-suppressed | 54 edges, **all 54** hub-suppressed |
| `shared-validated-fact` | 14 | 14 |

The nested corpus's real folders produced nine useful neighbour edges. Flattening the same
ten files into one directory produced fifty-four edges and the hub suppressor correctly
killed every one — §4.3 working exactly as designed.

**And the two runs still produced identical trees and identical groups.** So the answer to
question 2 is precise: existing structure influences the neighbourhood and only the
neighbourhood. It changes which files are considered related; it never changes a node in the
proposed tree.

---

## 4. Question 3 — what a real run actually produces

Corpus built under the scratchpad (outside the repo), with genuinely nested user structure:

```
corpus/
  Uni/PHYS1401/     lecture-01-kinematics.txt, problem-set-02.txt, lab-report-friction.txt
  Uni/MATH2010/     assignment-1.txt, notes-eigenvalues.txt
  Taxes/2026/       return-2026.txt, receipts-summary.txt
  Photos/2025-Trip/ itinerary.txt
  loose-syllabus-PHYS1401.txt
  loose-invoice.txt
```

Eight directories. Ten files. Eight of the ten already sit in a folder the person made, two
are loose. This is a person who has organised most of their disk already.

Command:

```
python3 src/cli.py <corpus> --situation academic.coursework --label Coursework \
    --database <scratchpad>/plan.sqlite
```

Output, in full for the part that matters:

```
Protected containers: 0 marked, none opened

Proposed folders: 1. 1 of them is somewhere a file can go.
  Coursework

Files: 10 decided, 0 ready to file
```

Then ten files across three "Waiting for you to say what these are" buckets, and:

```
Nothing was moved.
Plan version: version_2
```

### What was on disk versus what was proposed

| already on disk | in the proposal |
|---|---|
| `Uni`, `Uni/PHYS1401` (3), `Uni/MATH2010` (2) | absent |
| `Taxes`, `Taxes/2026` (2) | absent |
| `Photos`, `Photos/2025-Trip` (1) | absent |
| — | `Coursework` (the `--label` string) |

The database agrees. `directory_inventory` holds all eight directories with their true file
counts. `tree_nodes` holds two rows across the two plan versions, both
`node_type='proposed'`, both `display_label='Coursework'`, both `existing_path` NULL.

In passing: P9 *did* discover `PHYS1401` and `MATH2010` as coherent groups (`groups` table) —
from filenames and text, not from folder names. Neither survived into the tree either, because
`review_and_accept` (`src/cli.py:446-478`) collapses every discovered group into one merged
group named after `--label`. A separate finding for whoever audits the CLI review stage, but it
compounds this one: the shipped command can produce a tree of exactly one node, and does.

### The control

The same ten files, copied flat into a single directory, same command, fresh database:

```
Proposed folders: 1. 1 of them is somewhere a file can go.
  Coursework
```

`tree_nodes`: two rows, `proposed`, `Coursework`, `existing_path` NULL. Identical.

**Destroying four levels of the person's structure changed the product's proposal by
nothing.** That is the measurement the critique asks for, and it is unambiguous.

---

## 5. Question 4 — what this means for a person

**Nothing is destroyed.** There is no `shutil`, no `os.rename`, no `os.replace`, no `.move(`
anywhere in `src/`. The run is advisory and the report says so: "Nothing was moved." A person
who runs this today loses nothing.

**But nothing is preserved either, and that is the harm.** Consider someone who has already
filed half their disk — `Uni/PHYS1401/` is exactly right, they built it over a semester, they
can find things in it.

The engine sees the folder, builds it a card reading "An existing folder holding 3 file(s)"
(`candidates.py:307-315`), filters the card out at `pipeline.py:518`, and freezes a tree whose
only legal destination is `Coursework`. Design doc `:102` and `:104` make the frozen tree the
*closed* destination set — it "prevents later systems from inventing new destinations outside
it". So for each already-correctly-filed file the product has exactly two representable
outcomes: abstain, or propose moving it into `Coursework`.

There is no third outcome meaning **"this file is already where it belongs."** The field that
would carry it is `Node.node_type='existing'` with `existing_path` set, and no production code
writes it. `LEAVE_UNTOUCHED` (`vocabulary.py:398`) is the gesture that would say it and has no
consumer. `PRESERVE` (`vocabulary.py:394`) likewise.

**So yes — every run is a from-scratch proposal.** The person's own work is not adopted, not
merged with, not renamed to match, not left untouched; it is simply not in the picture. The
strongest evidence is the control run: the product cannot tell the difference between someone
who has organised nothing and someone who has organised everything.

One real mitigation: because nothing moves and the report is advisory, the person's structure
survives on disk regardless. The product is currently *safe* for a half-organised disk. It is
just not *useful* to one — and because it will propose moving already-filed files into a new
tree, it is likely to read as insulting to someone who has done the work.

---

## 6. Question 5 — consistency with `planning/66-FIND-FILE-AND-ONBOARDING.md`

### §3, "current location" as a first-class state (`66:110-136`)

§3 defines six distinct result elements. `66:124` — "| Current location | The actual path
where the file exists now | Always shown when the user is allowed to view it |"; `66:125` —
"| Filed home | A user-approved physical destination in the active organization plan | ... |";
governed by `66:120`: "These must not be collapsed into one ambiguous list of paths."

**Status in code: not built, with one exception.** There is no Find or search module in `src/`
at all. "Current location" survives as `files.directory_position` and is what the CLI report
prints to identify each file, but it is not a modelled state distinguished from a filed home.
Nothing in `src/` represents `Filed home`, `Historical location`, or `Possible placement`.

The one exception is honest and documented: `src/grouping/pipeline.py:471-478` cites §3 by name
while fixing the fact that `record_edges` had no caller — "`66` §3 makes 'also related to' a
state a person is shown ... and a relationship whose typed edge exists only in memory cannot be
shown, reviewed or replayed." So `Also related to` has persisted typed edges behind it. The
other five states do not.

**Consistency verdict for §3:** not contradicted, but only because almost none of it is
implemented — and a latent contradiction is waiting. §3 presumes the plan can hold a *Filed
home* that differs from a *current location* and that the difference is meaningful. Today the
plan holds only proposed nodes, so every file's filed home is by definition somewhere other
than where it is. §3's distinction degenerates when the tree can never contain the folder the
file is already in.

### §17, "existing approved structure remains stable" (`66:568-588`)

`66:583`: "Existing approved structure remains stable unless the user explicitly adopts the
new plan. New answers generate new proposals subject to review." And `66:580-582`: the product
"must not silently rename folders, reclassify files, reveal protected records, or move
anything as a consequence of a changed answer."

**Status in code: honoured in the negative, unreachable in the positive.**

The negative half is genuinely enforced: nothing moves, the version chain is real
(`pipeline.py:498-504`; `apply_review_action` opens a draft and mints new node ids per edit;
the run produced `version_0` → `version_2` with the freeze last), and adoption is an explicit
action (`ADOPT_VERSION`, `vocabulary.py:432-436`).

The positive half is vacuous. "Existing approved structure" presupposes the plan *contains*
the person's existing structure; it cannot. The set §17 promises to keep stable is always
empty. `test_ignoring_an_existing_folder_flips_legality_and_nothing_else`
(`tests/p10/test_p10_versions.py:149-166`) exercises §5.10's "leave untouched" over an
`existing` node — and can only do so because the fixture hand-wrote one.

**Consistency verdict for §17:** not violated. Not satisfiable either. §17 is written for a
product where the person's folders are nodes; the code is a product where they are not.

---

## 7. Summary of findings, flagged not fixed

| # | Finding | Evidence | Severity |
|---|---|---|---|
| 1 | Existing-folder branch candidates are built and then silently discarded by the selection filter | `pipeline.py:515-519`, `cli.py:626`, `cli.py:450/478`; probe: 8 built, 0 chosen | **critical** |
| 2 | No production code can write `node_type='existing'` or a non-null `existing_path`; only `fixtures.py:199` does | `pipeline.py:472-473`, `candidates.py:212`, `store.py:588`, `schema.py:61,66` | **critical** |
| 3 | The proposed tree is byte-identical for a 4-level nested corpus and a flat one | two live runs, `tree_nodes` in both databases | **critical** |
| 4 | §5.10's six existing-folder actions have zero consumers in `src/` or `tests/` | `vocabulary.py:398-405, 547` | high |
| 5 | `adopt-existing` refused by name, no writer | `store.py:109-112, 510-517` | high |
| 6 | `curation_signal()` returns `undetermined` for every directory, so "curated = strong intent" is unreachable | `scan_agent/inventory.py:42-53`; 8/8 undetermined in the run | high |
| 7 | The residual `replace-with-existing` mapping is dead: it needs an `existing` node that nothing writes | `residuals.py:221-232` | medium |
| 8 | No product state means "this file is already where it belongs"; every run is a from-scratch proposal | absence of `existing` nodes + closed-destination rule at `00:102, 104` | high |
| 9 | `66` §3's six-state result model is unimplemented except `also related to` | no find/search module; `grouping/pipeline.py:471-478` | medium |
| 10 | `66` §17's "existing approved structure remains stable" is trivially true over an always-empty set | `pipeline.py:498-504` vs finding 2 | medium |

**In one line:** the engine reads the person's folders, builds them a card each, and throws the cards away
before anyone sees them — and even if it kept one, it has no node type in which to put the
person's folder, only a new proposal wearing its name.

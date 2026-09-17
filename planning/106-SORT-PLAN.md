# The Sort: Reaching the Reference Tree — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax.
>
> **NOTHING IN THIS PLAN HAS BEEN EXECUTED.** The owner's instruction of 17 Sep: *"please plan the sort but not execute it yet."* This file is the plan they asked for. Do not start Phase 1 without their word.
>
> **One builder at a time on this machine.** Six read-only agents alone stretched a 72-second test run to fifty minutes on 17 Sep, and two whole-suite runs have been killed for memory. Never run a builder while a corpus run is live.

**Goal:** Make the proposed tree reach the level of the owner's *Ideal Multi-Role Personal File Tree* — a top level named after the person's own lives, drawn from their own files; branches whose depth comes from real facts; leftovers given typed homes rather than piles; and a person who edits the tree itself through screens the run stops at.

**Architecture:** Nothing here is greenfield. `src/tree_design/` is 11,099 lines and already holds 63 branch templates whose dimension orders spell the reference's own columns — `def.subject-work-record` declares `holder_institution > cycle_period > subject_anchor > artifact_kind`, which is the reference's Education column, written months ago. `src/grouping/`, `src/placement/`, `src/apply_run/` and `src/structure_file.py` are built and tested. The gap, diagnosed in `104` §18.100 from six read-only analyses, is in four specific places. Each phase moves one and is measured on the owner's corpus before the next begins.

**Tech stack:** Python 3.12, SQLite, pytest (`-p no:randomly`, targeted files, `nice -n 15`). No new dependencies.

---

## The four things that are actually wrong

1. **The partition key is the file's KIND.** `partition_by_branch` names each branch `label=schema_id` (`src/branch_situation.py:465`), so `nonprofit`, `photos`, `research` are internal identifiers worn as folders.
2. **There is no vocabulary of lives to key on instead.** Verified: no area name exists anywhere in the template or recognition libraries; `example_label_chains` are all `[]`. **Undesigned, not unbuilt.**
3. **The facts the folder levels are made of are produced for almost no file.** 221 of 371 carry none. Levels build only where facts divide (`materialise.py:94`), so templates that already spell the reference collapse for want of values.
4. **The person edits FACTS, not the TREE, and is asked nothing until the run is over.** A folder is *"where the facts about the files under it put it"* (`cli.py:22405`). Two of the reference's five verbs exist, both indirect. There is no `input()` anywhere in `src/`.

---

## The measurement every phase is judged against

`~/.graph-agent/lead/corpus2-gate1/run12.sqlite`, 371 files, read-only, aggregates only. **Never `scan.sqlite`** — it is an empty shell, and reading it produced the first, wrong version of this table (`104` §18.100).

| destination-eligible fields on one file | files |
| --- | --- |
| none | **221** |
| one | 121 |
| two | 22 |
| three | 6 |
| four | **1** |

`media_type` 48, `work_type` 46, `subject` 35, `institution` 17, `term` 7, `target_school` 7, `school` 6, `artifact_type` 6, `project` 6, `employer` **0**. Origins: `llm_interpretation` 472, `rule` 232, `deterministic_extractor` 135 — **the model, not the rules, is this product's main fact producer.**

Groups: 49, all `supported` and `coherent`, anchored on `duplicate_family` 102, `media_type` 36, `work_type` 23, `subject` 12, `term` 3 — **161 of 176 anchors are duplicates, file format or kind; 15 are about what the work was for.** `memberships` covers **133 of 371 files**; 238 are in no group. Every one of the 266 memberships is `decision_source='rules'` — **no model has ever accepted or rejected a group member.**

Judge quality, run 22's own facts against the owner's key (`104` §18.103): first choice **86.9 %**, key-in-what-it-said **97.7 %**, agreeing with the replay's 97.4 %. **The classifier is not the bottleneck. The sort is.**

---

## The owner's rulings of 17 September

All four given in session; recorded as `00` amendments 12, 12a, 13, 14, 15.

| ruling | what it unblocks |
| --- | --- |
| **Lives, from the reference's list** | Phases 3, 4 |
| **…but as a MENU, not a tree** (amendment 12a) | shapes Phases 3, 4 — see below |
| **Root-level `98 Review and Unsorted` / `99 Archive`** | Phase 7 |
| **Site D ratified — per-file control of leftovers** | Phases 6, 7 |
| **Close the no-situation arm's group-level questions** | Phase 0 |

### Amendment 12a is the one that shapes everything

The owner, correcting the lead before it was built: *"it's kind of based on what we have but also generic stuff — based on the guy's or girl's files?? it's not really like a set thing, it really depends."*

- **A life appears only where the person's own files put it.** The sixteen are the menu the product may choose from, never the tree it builds. A student gets Education, Career, Photos and Media — not an empty `Vehicles/`.
- **The person may rename, merge, split, remove, and ADD a life the library never imagined.** A congregation, a band, a family business. Without a library change.
- **Closed to the MODEL, open to the PERSON.** The judge picks only from the library's lives (an invented life is an invented folder); the person's addition is a user-confirmed fact, which already outranks any model.

**What this forbids:** shipping sixteen folders as a skeleton every corpus is poured into. On the owner's own files the lead expects far fewer than sixteen, and a phase that produces sixteen has failed its gate.

---

## Roadmap

| phase | goal | gate — how we know it worked |
| --- | --- | --- |
| **0** | Honour the rulings that need no new machinery | The no-situation arm strips group-level fields; site D's text is before the owner |
| **1** | Measure before building | A grouping number exists against the owner's own group labels |
| **2** | Make the situation facts readable | An unsettled branch stops going flat; the level answer becomes a fact |
| **3** | Partition on a life, not a schema | Root names on the owner's corpus are lives, and **fewer than sixteen** |
| **4** | Fold branches into areas | 49 groups become a small set of areas, not 49 root siblings |
| **5** | Stable node keys, then phase gates | An edit survives a re-run; three screens the person answers mid-flow |
| **6** | Fact producers | The 221 drops |
| **7** | Depth, flatten, residual homes | Uneven depth matching the reference; every leftover set has an offered home |

**Phases 0 and 1 are written in full below.** Phases 2–7 carry their goal, their seam, their gate and their risk — enough to start, not enough to skip the thinking. **Write each phase's full task list when its predecessor's gate is met**, never before: a plan written ahead of its predecessor's measurement is the failure mode this repository keeps paying for (`104` §18.99).

---

# Phase 0 — Honour the rulings

Small, unblocked, and two of them are the owner's explicit word. Do these first because Phase 6 depends on the site-D text existing and because the open arm is a live privacy question.

### Task 0.1: Strip group-level fields in the no-situation arm

**Ruling:** amendment 15 — *"Close it — respect the withdrawal."*

**Files:** `src/model_facts.py` (`open_question`, ~line 271, the `folder_levels is None` branch) · `src/cli.py:15712` (`anchor_level_fields`) · Test: `tests/p6/` beside the existing allowlist tests.

**The evidence this exists:** `target_school` is a folder level in **0 of 208 situations**, so no per-situation door can ask for it — and 7 files carry it. They can only have come through this arm.

- [ ] **Step 1: Write the failing test.** A file with an academic-active schema and NO situation named must not be offered `school` or any other member of `GROUP_LEVEL_ROLES` in its pending vocabulary. Assert on the question's vocabulary, not on the prompt text — prose is what is guarding it today and prose is what failed.
- [ ] **Step 2: Run it, confirm it fails,** and confirm it fails because the field IS offered (not because the fixture is wrong).
- [ ] **Step 3: Strip them.** In the `folder_levels is None` branch, subtract `GROUP_LEVEL_ROLES`' fields exactly as the per-situation branch already does. One expression, same source of truth — do not restate the role list.
- [ ] **Step 4: Run the test and `tests/p6`.** Expect green.
- [ ] **Step 5: Commit.** `fix(00 amendment 15): the no-situation arm strips group-level fields too`

### Task 0.2: Put site D's text in front of the owner

**Ruling:** amendment 14 — *"Ratify site D — give me per-file control."* The standing rule is that the lead shows the text before it acts on anything and an unratified text never crosses the internet.

- [ ] **Step 1:** Write the current `d_residual` template, its schema and its policy to `~/.graph-agent/lead/corpus2-gate1/review/` with a plain-language note saying what ratifying it will let the product do, and what it will then send where.
- [ ] **Step 2:** Tell the owner it is there. **Do not flip the row.** Ratification is theirs; amendment 14 is their intent, and the text itself still needs their eyes.
- [ ] **Step 3:** On their word, add a NEW manifest row with `status: ratified` — never edit a recorded row — and record what it replaced.

**Gate:** `grep -rn "GROUP_LEVEL_ROLES" src/model_facts.py` shows the strip in both arms; site D's text is in the review folder.

---

# Phase 1 — Measure before building

**Why first.** `grouping/` has never been graded. `tools/groundtruth/labels.py` has carried a hand-keyed `group` per file since 11 September and `tools/groundtruth/score.py` has never read it. Every claim about grouping quality — the lead's included — rests on nothing, and Phases 3 and 4 both change what a group becomes.

### Task 1.1: The run's groups reach the scorecard

**Files:** `tools/groundtruth/measure.py` (`Observation`, line 153, and its reader) · `tools/groundtruth/score.py` (new `group_cohesion`, beside `family_cohesion` at line 376) · `tools/groundtruth/report.py` · Test: `tests/tools/test_groundtruth_group_score.py` (new)

**Read first.** `family_cohesion` (`score.py:376-399`) is the model: takes `labels` and `observations`, keys on a label attribute, returns `(kept together, considered, scattered)`.

**`Observation` carries no group field today**, which is why this is not the five-line wire-up it was reported as.

- [ ] **Step 1: Write the failing test.**

```python
# tests/tools/test_groundtruth_group_score.py
"""`104` §18.100: the grouping stage has never been graded.

WHAT THIS MEASURES, and it is not placement. Two files the owner put in one group
belong in one group whatever folder the run chooses; a run that splits them has
failed at grouping even if it files both correctly, and `score_sorting` cannot
see that because each file is `exact` on its own. So the number is over the
owner's own groups and never touches `destination`.
"""
from __future__ import annotations

from tools.groundtruth.score import group_cohesion


class _Label:
    def __init__(self, group, protected=False):
        self.group = group
        self.protected = protected


class _Obs:
    def __init__(self, group_ids):
        self.group_ids = tuple(group_ids)


def test_two_files_the_owner_grouped_and_the_run_grouped_are_kept_together():
    labels = {"a": _Label("g1"), "b": _Label("g1")}
    observations = {"a": _Obs(["run-7"]), "b": _Obs(["run-7"])}
    assert group_cohesion(labels, observations) == (1, 1, ())


def test_two_files_the_owner_grouped_and_the_run_split_are_counted_split():
    labels = {"a": _Label("g1"), "b": _Label("g1")}
    observations = {"a": _Obs(["run-7"]), "b": _Obs(["run-9"])}
    assert group_cohesion(labels, observations) == (0, 1, ("g1",))


def test_a_group_the_run_never_formed_is_counted_and_not_skipped():
    """`00`:259 one stage earlier: a group nobody formed must not read as a group
    there was nothing to say about. SABOTAGE: `if not obs.group_ids: continue` --
    then a run with an empty `groups` table scores 0 of 0 and prints as perfect."""
    labels = {"a": _Label("g1"), "b": _Label("g1")}
    observations = {"a": _Obs([]), "b": _Obs([])}
    assert group_cohesion(labels, observations) == (0, 1, ("g1",))


def test_a_one_member_group_says_nothing_and_is_not_counted():
    labels = {"a": _Label("g1"), "b": _Label("g2")}
    observations = {"a": _Obs(["run-7"]), "b": _Obs(["run-9"])}
    assert group_cohesion(labels, observations) == (0, 0, ())


def test_protected_files_are_not_graded_on_grouping():
    """Protected material is counted, never opened, never filed automatically --
    so it is not evidence about the grouping stage."""
    labels = {"a": _Label("g1", protected=True), "b": _Label("g1", protected=True)}
    observations = {"a": _Obs(["run-7"]), "b": _Obs(["run-9"])}
    assert group_cohesion(labels, observations) == (0, 0, ())
```

- [ ] **Step 2: Run it.** `nice -n 15 python3 -m pytest tests/tools/test_groundtruth_group_score.py -p no:randomly -q` → `ImportError: cannot import name 'group_cohesion'`. Any other failure means the test is wrong; fix it first.

- [ ] **Step 3: Write `group_cohesion`,** immediately after `family_cohesion`:

```python
def group_cohesion(labels: Mapping[str, Label],
                   observations: Mapping[str, object],
                   ) -> tuple[int, int, tuple[str, ...]]:
    """`(kept together, the owner's groups with two or more files, the split)`.

    `104` §18.100: the grouping stage had no grade. This is it, and it is
    deliberately NOT about folders -- see the test module for why.

    A group the run never formed stays in the denominator. `00`:259 forbids the
    opposite: a group nobody formed must not read as a group there was nothing to
    say about. A run with an empty `groups` table therefore scores zero, which is
    the truth about it.
    """
    wanted: dict[str, list[tuple[str, ...]]] = {}
    for path, label in labels.items():
        if not label.group or label.protected:
            continue
        observation = observations.get(path)
        wanted.setdefault(label.group, []).append(
            tuple(sorted(getattr(observation, "group_ids", ()) or ()))
            if observation is not None else ())
    considered = {name: seen for name, seen in wanted.items() if len(seen) > 1}
    split = tuple(sorted(
        name for name, seen in considered.items()
        # Intersection, not equality: `00`:63 permits a file in more than one
        # accepted group, so two files sharing one group and differing on a
        # second have still been kept together.
        if not set.intersection(*(set(s) for s in seen))))
    return len(considered) - len(split), len(considered), split
```

- [ ] **Step 4: Run the test.** Expect `5 passed`.

- [ ] **Step 5: Give `Observation` its `group_ids`,** last and defaulted, following `review_policy`'s stated convention:

```python
    #: `104` §18.100: the groups the RUN put this file in, ids only. Last and
    #: defaulted for `review_policy`'s reason -- a database written before these
    #: tables existed leaves it empty, which is the truth about such a run.
    group_ids: tuple[str, ...] = ()
```

- [ ] **Step 6: Read them out of the database.** The columns are **confirmed** on the owner's database — do not re-derive them:

```python
    # `104` §18.100. ONE QUERY FOR THE WHOLE RUN, not one per file.
    #
    # `memberships` AND NOT `group_edges`. The edge table is the similarity GRAPH
    # -- `from_file_id`, `to_file_id`, `edge_type` -- and carries no `group_id` at
    # all. An excluded or uncertain member is not a member: `decision` is
    # filtered, not assumed, because counting a file the model excluded would
    # score the product on a judgement it made in the other direction.
    memberships: dict[str, list[str]] = {}
    try:
        for row in _rows(connection,
                         "select file_id, group_id from memberships "
                         "where superseded_by is null and decision = 'included'"):
            memberships.setdefault(row["file_id"], []).append(row["group_id"])
    except sqlite3.OperationalError:
        memberships = {}
```

then pass `group_ids=tuple(sorted(memberships.get(file_id, ())))` into `Observation(...)`.

**What right looks like on the owner's corpus:** 266 live rows, 49 groups, **133 of 371 files**. A grading run far from 133 means the query is wrong, not the product.

- [ ] **Step 7: Print it** beside the family-cohesion line in `report.py`, in that file's own idiom. No percentage presented as a grade (`00`:101).
- [ ] **Step 8: `nice -n 15 python3 -m pytest tests/tools -p no:randomly -q`.** A red older-database test means the reader change broke a path — fix the reader, never the fixture.
- [ ] **Step 9: Take the number (lead only), on `run12.sqlite`.** This is Phase 1's gate and the baseline Phases 3 and 4 are judged against.
- [ ] **Step 10: Commit.**

### Task 1.2 and 1.3: two screens that claim more than the run supports

Both found by the residual analysis; both identical in kind to `104` §18.96 and §18.102.

- [ ] **1.2** `PROTECTED_REVIEW_SET_WORDS` (`cli.py:15042`) says protected files are *"counted and named here"*; the card withholds the names, and the standing rule says protected filenames reach the plain report through no path. **The words are wrong** — change them, and update the pin at `tests/test_cli_report_at_scale.py:53`.
- [x] **1.2 DONE** (17 Sep). `PROTECTED_REVIEW_SET_WORDS` said protected files are "counted and named here" while `_review_note` withholds every example on a protected card. The words now say counted and NOT named, and point at the command without spelling it — `test_the_flag_is_named_only_on_the_line_that_is_the_command` caught the first attempt, which named `--show-protected` in prose: a person or script searching the report for what to type must not land on backticked prose four lines above the real command. `tests/test_cli_report_at_scale.py`: 25 passed.

- [ ] **1.3 SCOPED, NOT STARTED.** `PLACEMENT_WORDS[REVIEW_REQUIRED]` is *"Ready for you to approve, then file into {where}"* (`cli.py:20814`). A send into a residual area whose treatment is `reviewed` records `REVIEW_REQUIRED` and `not moves_files` (`placement/privacy.py:336`), and `mutation/plan.py:189` refuses that write at apply — **and most shipped areas take this path**, so the screen routinely promises a filing that cannot happen.

  **The seam, found and not yet threaded.** The heading is chosen at `cli.py:22999` from `policy` alone; the destination's DISPOSITION is not in scope there, which is the whole of the work. The precedent to copy sits four lines below: `104` R-92 already adjusts a heading conditionally when a promise cannot be kept — *"'Once you say what these are' is a promise, and it is kept only where the screen carries a gesture that reaches these files."* Same shape, same reason, one more input.

  **Test both directions** or the fix becomes a heading that under-promises everywhere: a moving area must still say it will file.

**Phase 1 gate:** a grouping number exists and is in `104`; `grep -rn "counted and named here" src/` returns nothing; no heading promises a move that `mutation/plan.py` refuses. Then the chunked suite, on a quiet machine.

---

# Phases 2–7

### Phase 2 — Make the situation facts readable

`situation` and `situation_alternative` were written on 16 Sep and have **zero readers** in `src/` outside their writer and the catalogue. Amendment 11's *"the sort reads both"* is designed, written and unread.

Two jobs. **(a)** `_signals_for_branch` (`cli.py:16015`) emits one `recognition:{situation}` per BRANCH, or nothing when the branch is unsettled, and an empty signal set selects no template row → C3 conflict → no recipe → flat root. Make detection signals per FILE, read from the `situation` fact, with `situation_alternative` as tie-break. **(b)** Fix the gap grading found (`104` §18.103): the `situation` fact stores the KIND (`academic`), not the situation (`academic.coursework`), and the level stage's finer answer is written as no fact at all because `record_the_situation` is called on the kind path only. Call it on the level path too, correct the catalogue row's note, and add a `situation_level` field or reuse `situation` with the finer value — **decide by asking which the sort needs, not by which is easier.**

**Gate:** an unsettled branch stops going flat; the count of branches receiving a recipe rises on run 22's database; the level answer is a fact.
**Risk:** (b) changes what an existing field means. Supersede, never overwrite; a run written under the old meaning must stay readable.

### Phase 3 — Partition on a life, not a schema

Add a `life` attribute to the recognition library's situation rows, carry it onto the applicability row, and key `partition_by_branch` on `life_of(situation)` read from the per-file fact, with alternatives as tie-break. Amendment 9 holds: the situation still never becomes a folder name; the life is a template attribute the situation points at, exactly as `folder_levels_for` already points at levels. **The discriminator: it alters the partition KEY, not a label.**

**Amendment 12a governs this phase.** The sixteen are a menu. A life is emitted only where the corpus puts files under it; the person can rename, merge, split, remove, and add one the library lacks; the model chooses only from the library's list.

**Gate:** root names on the owner's corpus are lives, **and there are fewer than sixteen** — a run that emits all sixteen has failed. The Phase 1 grouping number has not fallen.
**Risk:** the biggest single change in the plan. It must not regress placement; run the full suite and the grade before and after.

### Phase 4 — Fold branches into areas

`horizontal_candidates` (`candidates.py:259`) emits one root card per accepted group plus one per directory; `00`:67's *"aggregates into a small set of proposed major areas"* has no producer, so the owner's 49 groups would be 49 root siblings. Add one function between `horizontal_candidates` and `design_tree`'s chosen filter that folds group cards by life into a `BranchCandidate` with plural `accepted_group_ids` — **the pipeline already handles plural** (`pipeline.py:1039`) — labelled from the life and renameable. No new node type.

**Gate:** a small set of areas, not a flat forest; no file loses a home in the fold.

### Phase 5 — Stable node keys, then phase gates

The outline's positional `[n]` markers are invalidated every run by the `# plan:` guard, so an edited file cannot survive a re-run and a step-by-step conversation becomes N full re-runs. **Replace the positional marker with a stable node key first** — everything else here is unusable without it. Then extend `STOP_AFTER_STAGES` (`cli.py:15727`) with `groups` / `tree` / `placement` on the `accept_drafts` stop-print-return pattern that already exists: three cross-invocation gates, no new machinery, and emphatically **not** an interactive prompt — building `input()` into a 24k-line CLI is a larger job than the sort.

**Gate:** an edit survives a re-run; the person is asked three questions they can answer in the file.
**This is the phase the owner's "step by step process that involves user input" actually names.**

### Phase 6 — Fact producers

221 of 371 files carry no destination-eligible fact, and depth is bounded by that everywhere. Cheapest first: **(a)** wire `facts/photo_event.py:173 photo_events` into `_rule_stage` — it has a writer nothing calls, so `event` gains a producer in ~5 lines. **(b)** Take `SCHOOL_ANCHOR_KINDS` membership from `work_type` settled by ANY producer, not only the naming-zone regex, so a syllabus not named "syllabus" can still anchor. **(c)** Let a one-anchor `school` land `possible` for the person to confirm — P10's `AnchorAgreement` wants two independent anchors sharing one subject, so **a course with one syllabus can never get a school level today, structurally.** Also note `DIRECT_SLOTS = DirectSlots(slots=())`: the deterministic slot table is empty, so `direct_facts` runs and claims nothing.

**Gate:** the 221 drops, measured on `run12.sqlite`.
**Honest limit:** this is the only phase that raises depth, and its ceiling is unknown until measured. A photograph with no text and no folder path has no `school` for any producer to find.

### Phase 7 — Depth, flatten, residual homes

**(a)** Add `max_useful_depth` to `TemplateDefinition` (`templates.py:292`), parse in `catalogue._definition`, read in `validation._v3` before the global `max_depth=5` — the pattern `_residual_library` already uses for `max_permitted_depth`. Author the reference's per-branch depth numbers into `definitions.json`. **(b)** Replace `materially_improves_retrieval=lambda option: True` (`cli.py:634`) with a real measure, so the flatten recommendation can fire for the first time. **(c)** Under amendment 13, build root-level `98 Review and Unsorted` and `99 Archive`, with the characteristic sets named inside them, a suggestion table mapping each set to a home, auto-enabled when non-empty; add the reference's missing characteristics (unsupported or encrypted, possible duplicates and versions, deferred decisions). Under amendment 14, per-file accept/reject on each.

**Gate:** uneven depth matching the reference's column; every leftover set has an offered home rather than a flag the person must type; a leftover can be decided one file at a time.

---

## What this plan does not claim

- **Only Phase 6 raises depth**, and its ceiling is unmeasured. Phases 3 and 4 fix what branches are called and how many there are; they add no level to any branch. Say so on any screen reporting progress.
- **The 87 files the gate refused are not a bug** (`104` §18.102) and no phase here recovers them. They need a run with a local model, or the owner's release.
- **The classifier is done for now** at 97.7 % key-in-what-it-said. Further prompt work is not where the remaining value is.
- **Sixteen lives is a menu, not a target.** A tree that shows sixteen has failed amendment 12a.

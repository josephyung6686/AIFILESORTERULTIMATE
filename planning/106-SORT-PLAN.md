# The Sort: Reaching the Reference Tree — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking. **One builder at a time on this machine** — six read-only agents alone stretched a 72-second test run to fifty minutes on 17 Sep, and two whole-suite runs have been killed for memory. Never run a builder while a corpus run is live.

**Goal:** Make the product's proposed tree reach the level of the owner's "Ideal Multi-Role Personal File Tree" — a top level named after the person's *lives*, branches whose depth comes from real facts, residual material given typed homes rather than piles, and a person who edits the tree itself through screens the run stops at.

**Architecture:** Nothing here is greenfield. `src/tree_design/` (11,099 lines) already holds 63 branch templates whose dimension orders spell the reference's own columns; `src/grouping/`, `src/placement/`, `src/apply_run/` and `src/structure_file.py` are built and tested. The gap, diagnosed in `104` §18.100, is in four specific places: the partition key is the file's KIND, there is no vocabulary of lives to key on instead, the facts the folder levels are made of are produced for few files, and the person edits FACTS rather than the TREE with no gate until the run is over. Each phase below moves one of those and is measurable on the owner's corpus before the next begins.

**Tech stack:** Python 3.12, SQLite, pytest (`-p no:randomly`, targeted files, `nice -n 15`). No new dependencies.

---

## The measurement every phase is judged against

`~/.graph-agent/lead/corpus2-gate1/run12.sqlite`, 371 files, read-only, aggregates only:

| destination-eligible fields on one file | files |
| --- | --- |
| none | 221 |
| one | 121 |
| two | 22 |
| three | 6 |
| four | 1 |

`media_type` 48, `work_type` 46, `subject` 35, `institution` 17, `term` 7, `target_school` 7, `school` 6, `artifact_type` 6, `project` 6. `employer` 0. Origins: `llm_interpretation` 472, `rule` 232, `deterministic_extractor` 135.

49 groups, all `supported` and `coherent`, anchored on `duplicate_family` 102, `media_type` 36, `work_type` 23, `subject` 12, `term` 3 — **161 of 176 anchors are duplicates, format or kind; 15 are about what the work was for.**

**Measure against `run12.sqlite`, never `scan.sqlite`** — the latter is an empty shell and reading it is what produced the first, wrong version of this table (`104` §18.100).

---

## Three rulings the owner owes, and what each blocks

| ruling | blocks | proposed draft |
| --- | --- | --- |
| **(a) A `life` vocabulary in the library** — new closed vocabulary, the owner's alone to ratify | Phase 3, Phase 4 | The reference's own top level: Personal, Family and Household, Work, Career, Education, Teaching, Finance and Taxes, Home and Property, Health, Legal and Insurance, Vehicles, Travel, Photos and Media, Creative and Hobbies, Technology, Reference Library |
| **(b) Root-level `98 Review and Unsorted` / `99 Archive`**, against `00`:99's *"a global catch-all should not become the product's default answer to ambiguity"* | Phase 7 | The reference wants them; `00` forbids them. On a corpus 60 % of which has no facts, this decides the shape of the majority |
| **(c) Site D ratification** (R-102 also sits here) | Phase 6, Phase 7's per-file residual gesture | Without it `--review-set` records a choice and applies nothing |

Phases 1, 2 and 5 need no ruling and are where work starts.

---

## Roadmap

| phase | goal | gate | needs |
| --- | --- | --- | --- |
| **1** | Measure before building; stop two screens overstating | A grouping number exists against the owner's own labels; no screen in the residual/protected path claims more than the run did | — |
| **2** | Make the situation facts readable | An unsettled branch stops going flat; measured on run 22's database | — |
| **3** | Partition on a life, not a schema | Root names on the owner's corpus are lives | ruling (a) |
| **4** | Fold branches into areas | 49 groups become a small set of areas, not 49 root siblings | ruling (a) |
| **5** | Stable node keys, then phase gates | An edit survives a re-run; three screens the person answers mid-flow | — |
| **6** | Fact producers | The 221 drops | ruling (c) |
| **7** | Depth, flatten, residual homes | Uneven depth matching the reference's column; every residual set has an offered home | rulings (b), (c) |

Phases 2–7 are one paragraph each below. **Phase 1 is written in full.** Write `107` with Phase 2 in full when Phase 1 lands — a plan written before its predecessor's measurement is the failure mode this repository keeps paying for.

---

# Phase 1 — Measure before building

**Why first.** `grouping/` has never been graded. `tools/groundtruth/labels.py` has carried a hand-keyed `group` per file since 11 September and `tools/groundtruth/score.py` has never read it. Every claim about grouping quality to date — the lead's included — is unmeasured, and Phases 3 and 4 both change what groups become. Grading first is the owner's own standing rule and `104` §18.99's first failure mode.

**Two parts.** Task 1 makes the number exist. Tasks 2 and 3 close the two screens that claim more than the run supports, found by the residual analyst and identical in kind to `104` §18.96.

---

### Task 1: The run's groups reach the scorecard

**Files:**
- Modify: `tools/groundtruth/measure.py` — `Observation` (line 153), and the reader that builds it
- Modify: `tools/groundtruth/score.py` — new `group_cohesion`, beside `family_cohesion` (line 376)
- Modify: `tools/groundtruth/report.py` — one block, where the family line is printed
- Test: `tests/tools/test_groundtruth_group_score.py` (new)

**Read first.** `family_cohesion` (`score.py:376-399`) is the model: it takes `labels` and `observations`, keys on a label attribute, and returns `(kept together, considered, scattered)`. `group_cohesion` is the same shape with two differences — it keys on `label.group`, and it compares against the run's OWN groups rather than against destinations, so it answers "did the product put these files in one group" and not "did it file them together".

**`Observation` carries no group field today** (checked: no `group` in `measure.py`'s dataclass). That is why this task is not the five-line wire-up it was reported as.

- [ ] **Step 1: Write the failing test**

Create `tests/tools/test_groundtruth_group_score.py`:

```python
# tests/tools/test_groundtruth_group_score.py
"""`104` §18.100: the grouping stage has never been graded.

`labels.py` has carried a hand-keyed `group` per file since 11 September and
`score.py` has never read it, so every statement about grouping quality in this
repository -- including the lead's -- rests on nothing. Phases 3 and 4 of `106`
both change what a group becomes, and changing an ungraded thing is how `104`
§18.99's first failure mode happens again.

WHAT THIS MEASURES, and it is not placement. Two files the owner put in one group
belong in one group whatever folder the run chooses for them; a run that splits
them has failed at grouping even if it files both correctly, and a run that
merges two of the owner's groups has failed even if every file lands well. So the
number is pairwise over the owner's own groups and never touches `destination`.
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
    """The whole claim, at its smallest.

    SABOTAGE: make `group_cohesion` compare `destination` instead of
    `group_ids`. This still passes on a run that files both files in one folder
    without grouping them, which is the number the scorecard must not report.
    """
    labels = {"a": _Label("g1"), "b": _Label("g1")}
    observations = {"a": _Obs(["run-7"]), "b": _Obs(["run-7"])}

    together, considered, split = group_cohesion(labels, observations)

    assert (together, considered, split) == (1, 1, ())


def test_two_files_the_owner_grouped_and_the_run_split_are_counted_split():
    """SABOTAGE: return `considered` for `together` unconditionally. Red here."""
    labels = {"a": _Label("g1"), "b": _Label("g1")}
    observations = {"a": _Obs(["run-7"]), "b": _Obs(["run-9"])}

    together, considered, split = group_cohesion(labels, observations)

    assert (together, considered, split) == (0, 1, ("g1",))


def test_a_group_the_run_never_formed_is_counted_and_not_skipped():
    """A file in no group of the run's is not a file the run got right.

    `00`:259's standing rule read one stage earlier: a group the product never
    formed must not vanish from the denominator, or the scorecard flatters a run
    that grouped nothing at all.

    SABOTAGE: `if not observation.group_ids: continue`. Then a run with an empty
    `groups` table scores 0 of 0 and prints as perfect.
    """
    labels = {"a": _Label("g1"), "b": _Label("g1")}
    observations = {"a": _Obs([]), "b": _Obs([])}

    together, considered, split = group_cohesion(labels, observations)

    assert (together, considered, split) == (0, 1, ("g1",))


def test_a_one_member_group_says_nothing_and_is_not_counted():
    """`family_cohesion`'s own rule, and for its reason: a group with one placed
    member cannot demonstrate keeping things together either way.

    SABOTAGE: drop the `len(...) > 1` filter. `considered` inflates with
    singletons and the rate stops meaning anything.
    """
    labels = {"a": _Label("g1"), "b": _Label("g2")}
    observations = {"a": _Obs(["run-7"]), "b": _Obs(["run-9"])}

    together, considered, split = group_cohesion(labels, observations)

    assert (together, considered, split) == (0, 0, ())


def test_protected_files_are_not_graded_on_grouping():
    """The standing rule: protected material is counted, never opened, never
    filed automatically -- so it is not evidence about the grouping stage.

    SABOTAGE: drop the `label.protected` guard. The scorecard then grades the
    product on files it is forbidden to group.
    """
    labels = {"a": _Label("g1", protected=True), "b": _Label("g1", protected=True)}
    observations = {"a": _Obs(["run-7"]), "b": _Obs(["run-9"])}

    together, considered, split = group_cohesion(labels, observations)

    assert (together, considered, split) == (0, 0, ())
```

- [ ] **Step 2: Run it and watch it fail for the right reason**

```
cd "/Users/jy/GRAPH AGENT" && nice -n 15 python3 -m pytest tests/tools/test_groundtruth_group_score.py -p no:randomly -q
```

Expected: `ImportError: cannot import name 'group_cohesion' from 'tools.groundtruth.score'`. Any other failure means the test file itself is wrong — fix it before writing code.

- [ ] **Step 3: Write `group_cohesion`**

In `tools/groundtruth/score.py`, immediately after `family_cohesion` (which ends at line 399):

```python
def group_cohesion(labels: Mapping[str, Label],
                   observations: Mapping[str, object],
                   ) -> tuple[int, int, tuple[str, ...]]:
    """`(kept together, the owner's groups with two or more files, the split)`.

    `104` §18.100: the grouping stage had no grade. This is it, and it is
    deliberately NOT about folders. Two files the owner put in one group belong
    in one group whatever destination the run picks; a run that files both
    correctly and groups them apart has failed at grouping, and `score_sorting`
    cannot see that because each file is `exact` on its own -- exactly the blind
    spot `family_cohesion` was written for, one stage earlier.

    A group the run never formed stays in the denominator. `00`:259 forbids the
    opposite: a file nobody decided about must not read as a file understood and
    found unimportant, and a group nobody formed must not read as a group there
    was nothing to say about. A run with an empty `groups` table therefore scores
    zero, which is the truth about it.
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
        # Together means every member shares at least one of the run's groups.
        # Intersection and not equality: `00`:63 permits a file to belong to
        # more than one accepted group, so two files that share one group and
        # differ on a second have still been kept together.
        if not set.intersection(*(set(s) for s in seen))))
    return len(considered) - len(split), len(considered), split
```

- [ ] **Step 4: Run the test again**

```
cd "/Users/jy/GRAPH AGENT" && nice -n 15 python3 -m pytest tests/tools/test_groundtruth_group_score.py -p no:randomly -q
```

Expected: `5 passed`.

- [ ] **Step 5: Give `Observation` its `group_ids`**

In `tools/groundtruth/measure.py`, add to the `Observation` dataclass (after `review_policy`, keeping the file's own convention that new fields go last and carry a default so every existing construction keeps working):

```python
    #: `104` §18.100: the groups the RUN put this file in, ids only. Last and
    #: defaulted for `review_policy`'s stated reason -- a database written before
    #: the grouping tables existed leaves it empty, which is the truth about such
    #: a run: it formed no groups, so this file is in none of them.
    group_ids: tuple[str, ...] = ()
```

- [ ] **Step 6: Read them out of the database**

Find where `measure.py` builds each `Observation` and add, beside the other per-file reads, a membership map built once for the whole run rather than per file:

```python
    # `104` §18.100. ONE QUERY FOR THE WHOLE RUN, not one per file: the scorecard
    # walks every file and a per-file query here would be N round trips for a
    # mapping that does not change. Read defensively -- a database written before
    # these tables existed has neither, and that is a run with no groups rather
    # than an unreadable one.
    memberships: dict[str, list[str]] = {}
    try:
        for row in _rows(connection,
                         "select file_id, group_id from group_edges "
                         "where superseded_by is null"):
            memberships.setdefault(row["file_id"], []).append(row["group_id"])
    except sqlite3.OperationalError:
        memberships = {}
```

then pass `group_ids=tuple(sorted(memberships.get(file_id, ())))` into the `Observation(...)` construction.

**Before writing this step, confirm `group_edges` has a `file_id` and a `group_id` column on the owner's database** — a first look found no `group_id` there, so the membership may live on another table. Run, read-only:

```
python3 -c "
import sqlite3
c=sqlite3.connect('file:$HOME/.graph-agent/lead/corpus2-gate1/run12.sqlite?immutable=1',uri=True)
for t in ('group_edges','groups','group_acceptance','bundle_accepted_group'):
    print(t, [r[1] for r in c.execute('PRAGMA table_info(%s)' % t)])
"
```

and key the query on whatever columns that prints. **Do not guess the column names into the code.**

- [ ] **Step 7: Print it on the scorecard**

In `tools/groundtruth/report.py`, beside the family-cohesion line, add a line of the same shape naming both numbers and the split groups by the owner's own label. Follow the file's existing wording conventions; do not invent a percentage presented as a grade (`00`:101).

- [ ] **Step 8: Run the ground-truth tool tests**

```
cd "/Users/jy/GRAPH AGENT" && nice -n 15 python3 -m pytest tests/tools -p no:randomly -q
```

Expected: all pass. A red test in `tests/tools/test_groundtruth_*` means the reader change broke an older database's path — fix the reader, never the fixture.

- [ ] **Step 9: Take the number (lead only)**

Only the lead runs this, on the owner's corpus, and reports aggregates:

```
cd "/Users/jy/GRAPH AGENT" && GRAPH_AGENT_NO_DOTENV=1 PYTHONPATH=src python3 -m tools.groundtruth ...
```

with the invocation the existing scorecard uses. **This number is Phase 1's gate and the baseline Phases 3 and 4 are judged against.**

- [ ] **Step 10: Commit**

```bash
cd "/Users/jy/GRAPH AGENT"
git add tools/groundtruth/measure.py tools/groundtruth/score.py \
        tools/groundtruth/report.py tests/tools/test_groundtruth_group_score.py
git commit -m "feat(104 §18.100): the grouping stage has a grade, against the owner's own group labels"
```

---

### Task 2: The protected review set stops claiming it names files

**Files:**
- Modify: `src/cli.py:15042-15046` (`PROTECTED_REVIEW_SET_WORDS`)
- Test: `tests/test_cli_report_at_scale.py:53` pins the current wording and must change with it

- [ ] **Step 1: Read both sides and confirm the contradiction**

```
cd "/Users/jy/GRAPH AGENT" && sed -n 15042,15047p src/cli.py && grep -n "card.protected" src/cli.py | head -3
```

The words say files are *"counted and named here"*; the card skips its examples when `card.protected`. One of the two is wrong, and the standing rule says which: protected filenames never reach the plain report, only `--show-protected`. **The words are wrong.**

- [ ] **Step 2: Change the words**

```python
PROTECTED_REVIEW_SET_WORDS: tuple[str, str] = (
    "Protected, and not filed in bulk",
    "these are protected material, so they are counted here and not named, and "
    "nothing was assembled about them. They are not filed in one gesture with "
    "everything else; each one is yours to decide, and `--show-protected` names "
    "them when you ask.",
)
```

- [ ] **Step 3: Update the test's pin to the new words**

In `tests/test_cli_report_at_scale.py:53`, replace the pinned string with the new one and add one line of reason above it naming `104` §18.100 and the rule that protected filenames reach the plain report through no path.

- [ ] **Step 4: Run**

```
cd "/Users/jy/GRAPH AGENT" && nice -n 15 python3 -m pytest tests/test_cli_report_at_scale.py -p no:randomly -q
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/cli.py tests/test_cli_report_at_scale.py
git commit -m "fix(104 §18.100): the protected review set is counted and not named, and its words say so"
```

---

### Task 3: A review-only area stops promising to file

**Files:**
- Modify: `src/cli.py:~20746` (the heading printed for a residual send)
- Read: `src/placement/privacy.py:336`, `src/mutation/plan.py:189`
- Test: whichever test pins that heading — find it with `grep -rn "then file into" tests/`

- [ ] **Step 1: Confirm the contradiction with the code that refuses**

```
cd "/Users/jy/GRAPH AGENT" && sed -n 20740,20752p src/cli.py && sed -n 330,340p src/placement/privacy.py && sed -n 185,195p src/mutation/plan.py
```

A send into an area whose treatment is `reviewed` records `REVIEW_REQUIRED` and `not moves_files`; `mutation/plan.py` refuses that write at apply. The heading promises the opposite, and most shipped areas take this path.

- [ ] **Step 2: Gate the heading on whether the area actually moves files**

Print the "Ready for you to approve, then file into {where}" heading only when the destination area moves files, and otherwise a heading that says what will happen: the files are gathered under that name for you to read, and nothing is moved. Read the area's own `moves_files` (the attribute `privacy.py:336` tests) rather than re-deriving it.

- [ ] **Step 3: Write a test that a review-only area is not promised a move**

Place it beside the existing residual report tests. It must assert both directions — a moving area still says it will file, and a review-only area does not — or the fix becomes a heading that under-promises everywhere, which is the mirror of the defect.

- [ ] **Step 4: Run the residual and report tests**

```
cd "/Users/jy/GRAPH AGENT" && nice -n 15 python3 -m pytest tests/test_cli_report_at_scale.py tests/apply -p no:randomly -q
```

- [ ] **Step 5: Commit**

```bash
git add src/cli.py tests/
git commit -m "fix(104 §18.100): a send into a review-only area no longer says it will be filed"
```

---

### Phase 1 gate

Before Phase 2 starts, all three must hold:

1. A grouping number exists for the owner's corpus and is recorded in `104`.
2. `grep -rn "counted and named here" src/` returns nothing.
3. No heading promises a move that `mutation/plan.py` refuses.

Then run the suite in chunks (`scratchpad/suite_chunks.sh`) on a quiet machine — not while a corpus run is live — and record the result.

---

# Phases 2–7

**Phase 2 — Make the situation facts readable.** `situation` and `situation_alternative` were written on 16 September and have zero readers in `src/` outside their writer and the catalogue; `00` amendment 11's "the sort reads both" is designed, written and unread. `_signals_for_branch` emits one `recognition:{situation}` per BRANCH, or nothing when the branch is unsettled, and an empty signal set selects no template row and drops the branch to flat. Change the detection signals to be read per FILE from the `situation` fact, with `situation_alternative` as tie-break. **Gate:** on run 22's database, an unsettled branch stops going flat, and the count of branches that receive a template recipe rises. This is the prerequisite of Phase 3, not its rival — it changes which recipe a branch gets, not what the branch is called.

**Phase 3 — Partition on a life, not a schema.** `partition_by_branch` names each branch `label=schema_id` (`branch_situation.py:465`), which is why `nonprofit`, `photos` and `research` appear as folders. Add a `life` attribute to the recognition library's situation rows, carry it onto the applicability row, and key the partition on `life_of(situation)` read from the per-file fact. `00` amendment 9 holds unbroken: the situation still never becomes a folder name; the life is a template attribute the situation points at, exactly as `folder_levels_for` already points at levels. The discriminator that makes this the right change rather than a rename: it alters the partition KEY, not its label. **Needs ruling (a).** **Gate:** root names on the owner's corpus are lives, and the Phase 1 grouping number has not fallen.

**Phase 4 — Fold branches into areas.** `horizontal_candidates` emits one root card per accepted group plus one per directory, so the owner's 49 groups would be 49 root siblings; `00`:67's "aggregates into a small set of proposed major areas" has no producer. Add one function between `horizontal_candidates` and `design_tree`'s chosen filter that folds group cards by life into a `BranchCandidate` with plural `accepted_group_ids` — the pipeline already handles plural — labelled from the life and renameable by the person. No new node type. **Needs ruling (a).** **Gate:** a small set of areas rather than a flat forest, and no file loses a home in the fold.

**Phase 5 — Stable node keys, then phase gates.** The outline's positional `[n]` markers are invalidated every run by the `# plan:` guard, so an edited file cannot survive a re-run and a step-by-step conversation becomes N full re-runs. Replace the positional marker with a stable node key. Only then extend `STOP_AFTER_STAGES` with `groups` / `tree` / `placement`, following the `accept_drafts` stop-print-return pattern that already exists — three cross-invocation gates, no new machinery, and emphatically **not** an interactive prompt: building `input()` into a 24k-line CLI is a larger job than the sort. **Gate:** an edit survives a re-run, and the person is asked three questions they can answer in the file.

**Phase 6 — Fact producers.** 221 files of 371 carry no destination-eligible fact, and depth is bounded by that everywhere. Three concrete moves, cheapest first: wire `facts/photo_event.py:173 photo_events` into `_rule_stage` (it has a writer nothing calls — `event` gains a producer in about five lines); take `SCHOOL_ANCHOR_KINDS` membership from `work_type` settled by ANY producer rather than only the naming-zone regex, so a syllabus not named "syllabus" can still anchor; and let a one-anchor `school` land `possible` for the person to confirm, since P10's `AnchorAgreement` currently wants two independent anchors and a course with one syllabus can therefore never get a school level — structural, not a bug. **Needs ruling (c) / R-102.** **Gate:** the 221 drops, measured on `run12.sqlite`.

**Phase 7 — Depth, flatten, residual homes.** Add `max_useful_depth` to `TemplateDefinition` and read it in validation before the global `max_depth=5`, following the pattern `_residual_library` already uses for `max_permitted_depth`; author the reference's per-branch depth numbers into `definitions.json`. Replace `materially_improves_retrieval=lambda option: True` (`cli.py:634`) with a real measure so `00`'s flatten recommendation can fire for the first time. Add a characteristic→template suggestion table so each residual set is offered a home under its card and auto-enables when non-empty, and add the reference's missing characteristics (unsupported or encrypted, possible duplicates and versions, deferred decisions). **Needs rulings (b) and (c).** **Gate:** uneven depth matching the reference's column, and every residual set has an offered home rather than a flag the person must type.

---

## What this plan does not claim

It does not claim the reference is reachable in seven phases on this corpus. Phase 6 is the only phase that raises depth, and the honest ceiling there is unknown until it is measured: a photograph with no text and no folder path has no `school` for any producer to find. Phases 3 and 4 fix what the tree's branches are called and how many there are; they add no level to any branch. Say so on every screen that reports progress against this plan.

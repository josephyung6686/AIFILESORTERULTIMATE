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

# Phase 2 — Make the situation facts readable — **DONE, 17-18 Sep**

**2(a)** `19d39aa3`: `signals_for_branch` gives an unsettled branch the situations
its own files were judged to be, instead of `frozenset()`. An empty signal set
selected no applicability row, which is a C3 conflict, which is no recipe, which
is a flat root.

**2(b)** `c562f834`: the level stage's answer is written down. `record_the_
situation` had one call site, on the KIND path, running before the level stage was
called -- so the store held `academic` for a file the judge had named
`academic.coursework`. The finer value wins, because the router matches on
SITUATION ids and `schema_for_situation` recovers the kind while nothing recovers
the situation. Plus the guard `104` §18.108 records: a replayed answer does not
take the pointer back, or a second run leaves both rows superseded and the file's
situation unreadable.

**Its gate is NOT yet met and is not claimed.** "The count of branches receiving a
recipe rises on run 22's database" needs a SORT, and runs 22 and 23 both stop
after facts. It waits on run 23 finishing and a sort after it.

**Owed (`104` §18.108):** the level path writes `alternatives=()`, and `00`
amendment 11 says the sort reads both. And `grade_gate1.py`'s bridge assumes the
fact holds the KIND -- the 97.7 % may not be re-claimed until the grader prefers
the fact's own value where it is already a situation id.

---

# Phases 3–7 — the full task lists

**Drafted 18 Sep by four Fable analysts, one per area, each briefed to read `00`
first, to verify every `file.py:line` by opening it, and to refuse the brief where
the code contradicted it. Three of them did refuse it, and they were right** --
the corrections are at the head of each part and are recorded in `104` §18.109.

**These are drafts the lead has not executed.** They are written to `106`'s task
style -- TDD order, exact paths, full test bodies with SABOTAGE notes, no
placeholders -- so that each can be executed as written. The lead has verified the
premises the parts turn on (the branch-level fold at `cli.py:10946`/`:10990`, the
partition key at `branch_situation.py:465`, the refusal table behind Phase 6) and
has NOT line-checked every citation inside them. **Check a citation before acting
on it.**

**Ordering, from the drafts' own findings:** Phase 3 was gated on Phase 2(b),
which is now green. Phase 4 must follow Phase 3, because it folds on the life
Phase 3 creates. Phase 6 is independent of both and is the highest-value work in
the plan (`104` §18.109). Parts of Phase 7 are unblocked today -- see its §G.

---

# Phases 3 and 4 — THE LIFE PARTITION and THE AREA FOLD (draft for `106`)

> Drafted 17 Sep 2026 against `build/p6-p7-first-packages`. **Every `file.py:line` was re-verified on 18 Sep against `git show HEAD` (`64dcd13e`), each beside its anchor text so it can be re-found by grep.** HEAD moved twice during drafting (the lead's Phase 2 commits shifted `cli.py` by ~30 lines and `production.py` by ~37), which is why every citation carries its anchor: grep the anchor if a number has moved again. Nothing here has been run. No file outside this draft was written. `.groundtruth/`, `labels.json`, `.env` and `run12.sqlite`'s contents were not read; the one touch of the owner's run folder was `ls` and `.tables`, and the WAL was being written while this was drafted — the lead's run is live, so every query in §D is for after it finishes.

## 0. Two things in the brief the code contradicts — read these first

**1. "49 groups → 49 root siblings" is not what the code does, and Phase 4 is needed for a different reason.** `draft_for_review` (`cli.py:10817`) already buckets every P9 group by branch (`_grouped_by_branch`, `cli.py:10946`) and merges each bucket into ONE draft (`_draft_as_one`, `cli.py:10990`: `merged_id = f"{PLAN_VERSION}:{group_category}:{label}:{digest}"`, `display_label=label`, `group_category=branch.schema`). `--accept-groups` accepts those merged drafts (`accept_drafted_groups`, def at `cli.py:11173`, called at `cli.py:16349`), `horizontal_candidates` emits one root card per accepted group, so the 7 roots on the owner's corpus are the 7 branches, not 49 groups. The fold already exists — one level upstream of where the brief looked, keyed on the branch.

The reason Phase 4 is still needed: `eligible_rows` (`routing.py:193-240`) admits an applicability row only when `row.uses_schema ∈ context.domains`, and `context.domains` is the `group_category` of each accepted group under the branch (`pipeline.py:386-413`). A merged draft carries exactly one `group_category`. A life that spans two schemas — Education holds `academic.coursework` beside `applications.undergraduate-packet`, `academic` beside `college_applications` — therefore needs **one draft per (life, schema)**, both labelled with the life, and then **one fold of same-label cards into one candidate with plural `accepted_group_ids`** so `_route` sees plural domains and composes per coverage (`routing.py:561-680`, "a branch holding two lives"). Phase 3 produces the per-(life, schema) drafts; Phase 4 folds them. Without Phase 4 the owner's tree shows "Education" twice.

**2. Phase 3 cannot start until Phase 2(b) lands.** `record_the_situation` has one call site, `cli.py:9594`, on the KIND path: the variable it passes as `situation=` is the same one passed as `schema_id=` at `cli.py:9619`, so the `situation` fact reads `academic`, not `academic.coursework`. `life_of` is defined on a situation (the applicability row is per situation) and returns nothing for a kind. The untracked `tests/integration/test_the_level_answer_is_written_down.py` is the lead's own Phase 2(b) and its first test (`test_the_society_files_carry_the_situation_and_not_only_the_kind`) is the precondition of every task in §C. **Gate into Phase 3: that file is green.**

One more, smaller: the recognition library (`src/recognition/library/recognition.json`) is keyed per SCHEMA — 23 entries of context terms — and carries no per-situation row, so the plan's "recognition library's situation rows" cannot be where `life` goes. See §A.

---

## A. Where the `life` attribute lives

**The applicability row** — `src/tree_design/library/{applicabilities,wave2_commerce,wave2_industrial,wave2_organisational,wave2_practice}.json` — parsed by `tree_design/catalogue._applicability` (`catalogue.py:104-120`) into `tree_design/templates.TemplateApplicability` (`templates.py:474`).

**Why that row and no other.** Measured over the shipped release: 208 rows, all `applicability_version: 1`, every row carries exactly one `detection_signal_refs` entry, no situation is carried by two rows — the applicability row IS the situation, one to one. It is the row `folder_levels_for` (`production.py:547`) reads the levels off, `schema_for_situation` (`production.py:268`) reads the schema off, and `template_id_for_situation` (`production.py:511`) reads the template off. Amendment 12 says the life is "an attribute of the template the situation points at, exactly as `folder_levels_for` already points a situation at its levels" — this is that row. The definition (`def.subject-work-record`) is the wrong grain: it is shared by `academic`, `code` and `research` (`production.py:326`), which are three lives. The recognition library is the wrong grain the other way (per schema, §0).

**The precedent to copy is `privacy_floor`** (`templates.py:495-507`, "Amendment C"): a defaulted `str | None` on the record, `raw.get("privacy_floor")` in the loader, `None` meaning "this row states none". `life` is the same shape.

**Not a new versioned row beside the old one, and here is the measurement that forbids it.** `folder_levels_for`, `schema_for_situation` and `template_id_for_situation` each REFUSE when two rows carry one situation (`production.py:583-591`, `:299-304`, `:498-503` — "which folders these files should be filed under is the person's answer to give rather than this module's to pick"). A `v2` row beside a `v1` row for `academic.coursework` makes every read of `academic.coursework` a `ConfigurationRequired` at the first command a person types. `tests/p10/test_library_rows.py:108` pins 54 `(id, version)` pairs in `applicabilities.json`; `:113` pins `list(doc) == ["applicabilities"]`, so no new top-level section in that file either. The repository's own precedent for changing a library row is `fe7e24a7` (15 Sep): `wave2_organisational.json` edited in place, `+6` lines, with `tests/p10/test_library_organisational.py` updated beside it. The version that moves is `release_id`: `shipped_catalogue_manifest` derives it as the digest of the bytes read (`production.py:215-253`, "a library that changed moves the id, and one that did not cannot"), and `freeze` writes it onto every frozen tree (`pipeline.py:1013`). So: **the key is added to each row in place, `applicability_version` stays 1, `provenance` gains one entry naming the amendment.**

**The value is the owner's word, verbatim.** `"life": "Education"`, not an id plus a label table. `uses_schema` is already a closed vocabulary of 23 strings on the same row with no side table; the sixteen are the same kind of thing. The branch label is the value. A test (§C 3.2) pins every shipped value to the sixteen.

**What "closed to the model" means here, structurally.** The judge never chooses a life. Site G chooses a SITUATION from the library's list (`00` amendment 7); the row maps it. A life can enter the tree only through a situation the library carries, so 12a(iii) is satisfied by construction, with no menu shown to any model and no new prompt row.

### The proposed row, in full (`applicabilities.json`, `ap.academic.coursework`)

```json
{
 "applicability_id": "ap.academic.coursework",
 "applicability_version": 1,
 "template_id": "def.subject-work-record",
 "template_version": 1,
 "uses_schema": "academic",
 "purpose_profile_ref": null,
 "allowed_fields": ["school", "term", "subject", "work_type"],
 "detection_signal_refs": ["recognition:academic.coursework"],
 "role_bindings": [
  {"role_ref": "holder_institution", "field_ref": "school", "label": "My school"},
  {"role_ref": "cycle_period", "field_ref": "term", "label": "Semester"},
  {"role_ref": "subject_anchor", "field_ref": "subject", "label": "Course"},
  {"role_ref": "artifact_kind", "field_ref": "work_type", "label": "Kind of work"}
 ],
 "exclusions": [],
 "provenance": [
  "row:academic.coursework",
  "memo:planning/domains/nodes/academic.coursework.research.md",
  "51-LAUNCH-TEMPLATE-DRAFT.md §5.1",
  "53-HUMAN-SENSE-CHECK.md §4 — the name-out-loud test, which every label on this row answers",
  "00 amendment 12 (17 Sep 2026): life"
 ],
 "privacy_floor": null,
 "life": "Education"
}
```

Every other row: the same two additions (`"life"`, one `provenance` entry), nothing else touched.

### The 208-row mapping — proposed, NOT ratified

Amendment 12 ratifies the sixteen NAMES. It does not ratify which of the 208 situations is which life; that is authoring, exactly as the 123 `RoleBinding.label`s were authoring, and it is owed the owner's eyes before the rows change. The lead applies it as the owner's word or the owner's corrections. The table is per-schema default with the exceptions listed; every situation not listed as an exception takes its schema's default. All sixteen lives appear at least once, so the library's menu is the full sixteen and the corpus alone decides which show (12a(i)).

| schema (rows) | default life | exceptions |
| --- | --- | --- |
| `academic` (11) | Education | `academic.teaching` → Teaching · `academic.recommendation-letters-written` → Teaching · `academic.k12-schooling`, `academic.homeschool`, `academic.iep-accommodation-plans` → Family and Household |
| `college_applications` (5) | Education | — |
| `research` (8) | Work | `research.thesis-dissertation` → Education · `research.reading-library` → Reference Library |
| `career` (3) | Career | — (`career.employer-side-hiring` is arguably Work; left under Career so the schema is life-unanimous, see §B arm 3) |
| `code` (3) | Technology | — |
| `creative` (28) | Creative and Hobbies | client-facing practice → Work: `creative.client-engagement`, `creative.deliverable-handoff`, `creative.ad-campaign`, `creative.brand-identity`, `creative.content-marketing`, `creative.commissioned-shoot` |
| `finance` (18) | Finance and Taxes | `finance.household-property`, `finance.hoa-residents-association` → Home and Property · `finance.insurance-healthcare` → Health · `finance.insurance-personal` → Legal and Insurance · `finance.insurance-corporate`, `finance.cap-table-equity`, `finance.small-business-bookkeeping` → Work · `finance.vehicle-records` → Vehicles · `finance.student-financial-aid` → Education · `travel.bookings-confirmations` → Travel |
| `photos` (9) | Photos and Media | `travel.trip-photos` → Travel |
| `nonprofit` (2) | Personal | — (the student organisation of amendment 7; a person who RUNS a nonprofit merges it into Work — 12a(ii)) |
| `business_operations` (8), `engineering` (15), `hr` (6), `government` (3), `logistics` (6), `manufacturing` (15), `resource_operations` (8), `retail_hospitality` (12), `construction_property` (22) | Work | — |
| `law_practice` (26) | Work | — (these are a PRACTICE's casework rows; a person's own legal matters are `finance.insurance-personal`'s neighbours and there is no `legal.*` situation today — a gap for the owner, not for this phase) |

Where "it really depends" bites hardest — `creative`, `research`, `nonprofit` — the default is the one a person is likelier to rename than to be surprised by, and 12a(ii)'s gestures (rename, merge) are what carry the other case.

### The reader, beside `folder_levels_for` (`src/production.py`, after line 604)

```python
def life_of(catalogue: TemplateCatalogue, situation: str) -> str | None:
    """WHICH LIFE this situation is part of, ASKED of the library. `None` when
    the row states none.

    `00` amendment 12: the life is an attribute of the template the situation
    points at, exactly as `folder_levels_for` reads the levels off the same row.
    A situation never becomes a folder name (amendment 9); its LIFE may, because
    the life is the library's word and not the file's kind.

    Refused when the release carries no row for the situation, for
    `folder_levels_for`'s reason. `None` rather than a refusal when the row
    carries no `life`: that is a row the library has not placed in a life, which
    12a permits, and the partition says what it does with such a file.
    """
    ref = f"recognition:{situation}"
    rows = [row for row in catalogue.applicabilities.values()
            if ref in row.detection_signal_refs]
    if not rows:
        raise ConfigurationRequired(
            f"{situation!r} names no situation in template release "
            f"{catalogue.release_id}, so there is no row to read a life from")
    if len(rows) > 1:
        raise ConfigurationRequired(
            f"{situation!r} is carried by {len(rows)} applicability rows, and which "
            "life these files belong to is the person's answer to give rather than "
            "this module's to pick")
    return rows[0].life
```

---

## B. The partition key change

### What changes in `Branch` (`branch_situation.py:104`)

```python
@dataclass(frozen=True)
class Branch:
    """One proposed top-level branch: a LIFE the corpus put files under, or the
    folder's own default branch."""

    label: str
    #: `00` amendment 12: the life this branch IS, read off the library rows of
    #: its files' situations. `None` only for a default branch whose situation
    #: nothing has settled. It is the partition KEY and the root's label; a
    #: situation is never one (amendment 9).
    life: str | None
    #: Every kind its files belong to, first-seen order. PLURAL since amendment
    #: 12: Education holds `academic.coursework` beside
    #: `applications.undergraduate-packet`, and those are two schemas.
    #: `_grouped_by_branch` drafts one group per member of this tuple.
    schemas: tuple[str, ...]
    #: The situations its files' `situation` facts carry, distinct, first-seen
    #: order. Empty on the partition that runs before the judge.
    situations: tuple[str, ...]
    #: `None` while unsettled. A life branch is settled only when `situations`
    #: holds exactly one and every file carries it (`_settled_by_the_judge`), or
    #: the person answered at this branch's scope.
    situation: str | None
    is_default: bool
    anchor_file_ids: tuple[str, ...]
    file_ids: tuple[str, ...]
    candidate_situations: tuple[str, ...] = ()
```

`schema: str` is REMOVED, not kept beside `schemas`; two spellings of one fact is the drift `single_owner_terms`' docstring warns about. Every reader is listed in §C 3.5.

### What changes in `partition_by_branch` (`branch_situation.py:249`)

Three new parameters, all callables or tables so the module still "reads no database and imports nothing from the composition root":

```python
        life_of: Callable[[str], str | None],
        situation_fact_of: Callable[[str], str | None],
        alternatives_of: Callable[[str], Sequence[str]],
```

`life_of` is `production.life_of` bound to the catalogue. `situation_fact_of(file_id)` is the `situation` fact through `preferred_fact` (the read `cli._situations_of` already makes at `cli.py:16133-16143` — a `user_confirmed` row wins there outright, which is how the person's answer outranks the judge, `00` §3.13). `alternatives_of(file_id)` is the live `situation_alternative` rows' values — "a reader takes the rows, not the pointer" (`llm_seam.py:451`). It is read as a SET: `facts_for_file` orders by canonical value (`file_facts.py:308`), so the judge's ranking is not recoverable from the store and this draft does not pretend it is.

**The reach is unchanged.** Every line of `partition_by_branch` up to `under` — G's name first, then the anchor, then the schema's own field, then the recogniser's reading — still decides which KIND each file is. What changes is the last step: kinds are folded into lives before branches are built.

**The life of one file, four arms, none of them a pick:**

1. `life_of(situation_fact_of(f))` — the judge's first choice, or the person's confirmed answer.
2. Failing that, the alternatives: `{life_of(a) for a in alternatives_of(f)} - {None}` — exactly one distinct life among them is that life; two is nothing. The tie-break the brief asks for, order-free.
3. Failing that (no situation fact — the 87 gate-refused files, and a file the judge declined), THE LIBRARY'S OWN UNANIMITY over the file's kind `S`: `{life_of(s) for s in situations_of(S)} - {None}` — exactly one is an answer and not a choice, `the_one_situation`'s first arm one level up. Every `career.*`, `code.*`, `college_applications`, `hr.*` … row shares one life under the §A table, so a gate-refused résumé anchored `career` lands in Career.
4. Failing that, THE CORPUS'S OWN UNANIMITY: the one life the judge named for every judged file of kind `S` in this roster — `_settled_by_the_judge`'s rule (unanimous, over every judged file) applied to lives. A gate-refused syllabus anchored `academic`, in a folder whose every judged academic file is coursework, lands in Education.
5. Otherwise the file has no life.

**Which branch a file is under:**

- **A typed run keeps its own life at home.** When the person typed `--situation` (the `default_situation` parameter is not `None`), `default_life = life_of(default_situation)` and **a file whose life equals it stays in the default branch**, under the label they typed. This is the byte pin: `--situation academic.coursework --label Coursework` over an all-coursework folder gives every file the life Education, which is the default's, and the partition is one branch — `test_r37_single_branch_is_byte_identical` unchanged.
- **An untyped run puts every lived file in its life.** With nothing typed there is no word of the person's for the folder to be, so the top level is lives (amendment 12) and the default branch holds only the residue: files with no life. `default_life` is still computed when `_default()` settles the default (the person's answer at its scope, or the library's one situation) and is what P11 reads for its root (§C 3.5); it does not pull files back.
- A file with a life other than the default's is under the branch of that life; `label=life`.
- A file with no life is under the default branch. This is R-140 read at the life grain ("a file NO branch reaches is the DEFAULT branch's; coverage is sacred"), and it is where the 87 sit if arms 3-4 do not reach them.

**The default branch's label on an untyped run is NOT the kind.** `cli.py:17870` reads `default_label = default_schema if label is None else label`, so today an untyped run's default root is called `academic` — amendment 12's own "schema identifiers worn as folders", and §D would fail on it for a reason this draft caused. The rule (§C 3.5): the person's `--label` if typed; else the scanned folder's own name, `candidates.folder_label(directory)` (already imported at `cli.py:420`), which is the honest name of "the rest of this folder" until Phase 7 makes it `98 Review and Unsorted` under amendment 13. If that folder happens to be named exactly as a life the corpus reaches, two branches would share a label; `BranchPartition.__post_init__` gains the check (risk #13) and the person types `--label`.

**Single-ness is decided AFTER the fold, not before it.** `partition_by_branch` today returns early when only one KIND opened (`branch_situation.py:397-404`, `if len(schemas) == 1`). That return fires before any life is computed, and under amendment 12 one kind spans several lives — Priya's `academic` folder is Education and Teaching. **The early return is deleted.** The reach loop with one schema puts every file in the one bucket and holds nothing, the fold then yields zero or more life branches, and `BranchPartition.single` (`len(branches) == 1 and not held`) is true exactly when the fold yielded none — which is what keeps the byte pin a real test of the rule above rather than of a shortcut that never reached it.

**What this trades, named.** Today a fact-less file of kind `S` sits in a kind branch labelled `S`, and `_settled_by_the_judge` can settle that branch. Under lives a fact-less file that arms 3-4 do not reach sits in the default branch with no question recorded for it (its kind branch no longer exists to ask about), and `_the_situation_this_file_is_under` returns `None` for it exactly as it does today for "a file of a named kind with no situation yet" (`cli.py:17765-17772`) — asked nothing, P11 abstains `situation_unanswered`. It is not silently omitted: it is counted in the default branch's `file_ids` and it is Phase 7's `98 Review and Unsorted` file under amendment 13, decided one at a time under amendment 14. What is lost is the identifier-menu question for it, which the owner refused on 14 Sep.

**A situation with no life mapped** (`life_of` → `None`): the file falls through arms 2-4 like a file with no fact. On the shipped release after §A there is none; a later row shipped without a `life` is what the §C 3.2 test catches before it ships.

**A life the corpus does not have** is simply never a key: a branch exists only for a life some file's arms reached (12a(i)). `Vehicles/` cannot appear on a corpus with no `finance.vehicle-records` file. The §D gate checks the converse too — no root the facts do not support.

**Settling a life branch.** `_situation_for` is the default branch's rule and stays. For a life branch: the person's answer at `branch:<life>` if it is among the branch's `situations`; else `_settled_by_the_judge(file_ids, situations)` — one situation named for every file; else `None` with `candidate_situations=()`. `()` on purpose: "which situation is Education?" is not a question when Education holds coursework AND a thesis, and `_ask_which_situation_each_branch_is` skips a branch with nothing to choose from (§C 3.5). The branch stays unsettled and `signals_for_branch`'s third arm (Phase 2(a)) hands the router every situation its files carry, which is exactly what a life root needs.

**One branch per life, never two sharing a label.** `Branch.label` is an identity at `branch:<label>` (question scope, `cli.py:17920`), `nesting_chooser`'s scope (`branch:{display_label}`), `_grouped_by_branch`'s dict keys (`cli.py:10975`), `votes_cell` (`cli.py:18336`) and P11's root map (`cli.py:17510`). A life spanning two schemas is one `Branch` with two `schemas`, and the split into per-schema drafts happens in `_grouped_by_branch` (§C 3.4), where the category is the group's and not the branch's.

### The function, written out (the tail of `partition_by_branch`, replacing everything from `branches: list[Branch] = []` at `branch_situation.py:435`)

```python
    def _life_of_file(file_id: str, kind: str | None) -> str | None:
        """Four arms, none a pick. See the module docstring's 'The life'.

        `kind` is `None` for a file NO branch reached -- R-140 put it in the
        default bucket, and that bucket's schema is not evidence about the file,
        so arms 3 and 4 (which read the kind) do not run for it.
        """
        fact = situation_fact_of(file_id)
        if fact is not None and life_of(fact) is not None:
            return life_of(fact)
        named = {life_of(a) for a in alternatives_of(file_id)} - {None}
        if len(named) == 1:
            return next(iter(named))
        if kind is None:
            return None
        librarys = {life_of(s) for s in situations_of(kind)} - {None}
        if len(librarys) == 1:
            return next(iter(librarys))
        judged = {life for other, other_kind in kind_of.items()
                  if other_kind == kind
                  for life in (_first_arm_life(other),) if life is not None}
        if len(judged) == 1:
            return next(iter(judged))
        return None

    def _first_arm_life(file_id: str) -> str | None:
        fact = situation_fact_of(file_id)
        return None if fact is None else life_of(fact)

    default_situation_settled, default_candidates = _default()
    default_life = (None if default_situation_settled is None
                    else life_of(default_situation_settled))
    #: The person's own word for the folder keeps its life at home; with nothing
    #: typed the top level is lives and the default holds the residue (§B).
    typed = default_situation is not None

    #: file -> the KIND the reach put it under (the loop above, unchanged but
    #: for one line: its `elif not reached:` arm also records the file in
    #: `fell_through`, because R-140's default bucket is not a kind the file
    #: was reached to). `None` for those.
    kind_of: dict[str, str | None] = {
        file_id: (None if file_id in fell_through else schema_id)
        for schema_id, files in under.items() for file_id in files}
    lives: dict[str, list[str]] = {}
    default_files: list[str] = []
    for file_id, _hash in roster:
        if file_id in kind_of:
            life = _life_of_file(file_id, kind_of[file_id])
            if life is None or (typed and life == default_life):
                default_files.append(file_id)
            else:
                lives.setdefault(life, []).append(file_id)

    def _situations_carried(file_ids: Sequence[str]) -> tuple[str, ...]:
        return tuple(dict.fromkeys(
            fact for fact in (situation_fact_of(f) for f in file_ids)
            if fact is not None))

    def _schemas_carried(file_ids: Sequence[str]) -> tuple[str, ...]:
        return tuple(dict.fromkeys(
            kind for kind in (kind_of[f] for f in file_ids) if kind is not None))

    branches: list[Branch] = [Branch(
        label=default_label, life=default_life,
        schemas=tuple(dict.fromkeys([default_schema, *_schemas_carried(default_files)])),
        situations=_situations_carried(default_files),
        situation=default_situation_settled, is_default=True,
        anchor_file_ids=tuple(anchors_of.get(default_schema, ())),
        file_ids=tuple(default_files),
        candidate_situations=default_candidates)]
    for life in sorted(lives):
        files = lives[life]
        carried = _situations_carried(files)
        chosen = chosen_situation(f"{SCOPE_BRANCH}:{life}")
        situation = (chosen if chosen is not None and chosen in carried
                     else _settled_by_the_judge(files, carried))
        branches.append(Branch(
            label=life, life=life, schemas=_schemas_carried(files),
            situations=carried, situation=situation, is_default=False,
            anchor_file_ids=tuple(f for f in files if f in anchored_to),
            file_ids=tuple(files), candidate_situations=()))
    return BranchPartition(branches=tuple(branches), held=tuple(held))
```

`_settled_by_the_judge` keeps its signature and is fed `situation_fact_of` instead of `situations_named_by_the_model` (the fact is the same answer, written down — and it carries the person's `user_confirmed` override, which the in-memory pass cannot). `situations_named_by_the_model` stays a parameter for the pass-order reason its docstring gives and is read nowhere else after this change; §C 3.3 retires it once the tests are green, one commit later, so the rename is its own diff.

The single-branch early return at `branch_situation.py:397-404` (`if len(schemas) == 1:`) is DELETED, for the reason §B gives: it is keyed on kinds, and one kind spans several lives. The tail above is the only place branches are built.

### What the composition root binds (`cli.py:17872`, `_the_branches`)

```python
            life_of=lambda situation: life_of(catalogue, situation),
            situation_fact_of=_situation_fact_of,
            alternatives_of=_alternatives_of,
```

with, beside `_situations_of` at `cli.py:16122`:

```python
    def _situation_fact_of(file_id: str) -> str | None:
        """This file's `situation` fact as a reader sees it -- `preferred_fact`,
        so a `user_confirmed` row wins and an unresolvable slot answers `None`."""
        row = preferred_fact(conn, file_id=file_id, field_key=SITUATION_FIELD)
        return None if row is None else _situation_values().get(row["value_id"])

    def _alternatives_of(file_id: str) -> tuple[str, ...]:
        """Every live `situation_alternative` row's value. A set, not a rank:
        the store does not keep the judge's order (`file_facts.py:308`)."""
        return tuple(sorted({
            row["canonical_value"] for row in conn.execute(
                'SELECT v.canonical_value FROM file_facts ff '
                'JOIN "values" v USING (value_id) '
                'WHERE ff.file_id = ? AND ff.field_key = ? '
                'AND ff.superseded_by IS NULL',
                (file_id, SITUATION_ALTERNATIVE_FIELD))}))
```

`SITUATION_ALTERNATIVE_FIELD` is imported from `facts.llm_seam` beside `SITUATION_FIELD`.

---

## C. Phase 3 — full task list

Order: 3.1 → 3.2 → 3.3 → 3.4 → 3.5 → 3.6, each red-then-green-then-commit. Every command is `nice -n 15 python3 -m pytest <file> -p no:randomly -q` with `GRAPH_AGENT_NO_DOTENV=1` exported. **Precondition:** `tests/integration/test_the_level_answer_is_written_down.py` green (§0 item 2).

### Task 3.1: the row carries a life and the library answers `life_of`

**Files:** Modify `src/tree_design/templates.py` (`TemplateApplicability`, after `privacy_floor` at line ~500) · Modify `src/tree_design/catalogue.py` (`_applicability`, line 104) · Modify `src/production.py` (new `life_of` after `folder_levels_for`, line ~604) · Test `tests/p10/test_p10_life_attribute.py` (new)

- [ ] **Step 1: Write the failing test.**

```python
# tests/p10/test_p10_life_attribute.py
"""`00` amendment 12: the applicability row carries the LIFE its situation is
part of, and `production.life_of` reads it exactly as `folder_levels_for` reads
the levels -- off the one row that IS the situation.

Amendment 9 is the line these tests hold: the life is an attribute of the
template the situation points at, never a name derived from the situation.
`life_of("academic.coursework")` answers "Education" because the ROW says so,
and a row that says nothing answers `None` rather than "academic".
"""
from __future__ import annotations

import json

import pytest

from production import life_of
from tree_design.catalogue import load_catalogue
from tree_design.config import ConfigurationRequired
from tree_design.templates import TemplateApplicability


def _row(situation: str, schema: str, life: str | None):
    raw = dict(
        applicability_id=f"ap.{situation}", applicability_version=1,
        template_id="def.fixture", template_version=1, uses_schema=schema,
        purpose_profile_ref=None, allowed_fields=[], detection_signal_refs=[
            f"recognition:{situation}"], role_bindings=[], exclusions=[],
        provenance=["row:fixture"], privacy_floor=None)
    if life is not None:
        raw["life"] = life
    return raw


def _catalogue(*rows):
    manifest = {"release_id": "rel-lives", "fragments": [], "definitions": [],
                "applicabilities": list(rows)}
    return load_catalogue(lambda: json.dumps(manifest))


def test_a_row_that_states_a_life_loads_it_and_life_of_reads_it():
    """SABOTAGE: derive the life from the situation's dotted prefix. This stays
    green for `academic.coursework` -> some spelling of academic, and RED here,
    because the row says Education and the prefix does not."""
    catalogue = _catalogue(_row("academic.coursework", "academic", "Education"))

    assert catalogue.applicabilities[("ap.academic.coursework", 1)].life == "Education"
    assert life_of(catalogue, "academic.coursework") == "Education"


def test_a_row_that_states_no_life_answers_none_and_not_its_kind():
    """12a: a row the library has not placed in a life is a row with no life.
    SABOTAGE: fall back to `uses_schema`. Then a kind is a life, which is the
    taxonomy of kinds `104` §18.100 measured and amendment 12 removed."""
    catalogue = _catalogue(_row("academic.coursework", "academic", None))

    assert catalogue.applicabilities[("ap.academic.coursework", 1)].life is None
    assert life_of(catalogue, "academic.coursework") is None


def test_a_situation_the_library_does_not_carry_is_refused_not_guessed():
    """`folder_levels_for`'s posture, for the same reason."""
    catalogue = _catalogue(_row("academic.coursework", "academic", "Education"))

    with pytest.raises(ConfigurationRequired):
        life_of(catalogue, "academic.courswork")


def test_the_record_defaults_life_to_none_so_older_manifests_still_load():
    """The `privacy_floor` precedent: a row written before the attribute existed
    is a row that states none. SABOTAGE: make `life` required. Every fixture
    catalogue in `tests/p10` stops loading, and so does a frozen tree's
    manifest from before 17 Sep."""
    row = TemplateApplicability(
        applicability_id="ap.x", applicability_version=1, template_id="def.x",
        template_version=1, uses_schema="academic", purpose_profile_ref=None,
        allowed_fields=(), detection_signal_refs=("recognition:x",),
        role_bindings=(), exclusions=(), provenance=("row:fixture",))

    assert row.life is None
```

- [ ] **Step 2: Run it.** `nice -n 15 python3 -m pytest tests/p10/test_p10_life_attribute.py -p no:randomly -q` → `ImportError: cannot import name 'life_of'`. Any other failure is the test's.
- [ ] **Step 3: Implement.** `templates.py`: after `privacy_floor: str | None = None` add

```python
    #: `00` amendment 12 (17 Sep 2026). WHICH LIFE this situation is part of, in
    #: the owner's own words, one of the sixteen the reference tree names -- and
    #: none of the sixteen is spelled in `src/`, by `tests/p10/test_library_lives.py`'s
    #: pin. The partition keys on it and the root node wears it; the situation
    #: itself never does (amendment 9).
    #:
    #: `None` is the `privacy_floor` marker one field up: this row states none.
    #: 12a permits a row outside every life; the partition says what it does
    #: with such a file, and `tests/p10/test_library_lives.py` says whether the
    #: shipped release has any.
    life: str | None = None
```

`catalogue.py:118`: add `life=raw.get("life"),` beside `privacy_floor=raw.get("privacy_floor"),`. `production.py`: the `life_of` of §A.

- [ ] **Step 4: Run it.** Expect `4 passed`. Then `tests/p10/test_p10_templates.py tests/p10/test_p10_privacy_floor.py tests/p10/test_library_rows.py` — a defaulted field breaks none of them; `dataclasses.asdict` in `test_p10_routing._catalogue` carries the new key through.
- [ ] **Step 5: Commit.** `feat(00 amendment 12): the applicability row carries a life, and the library answers life_of`

### Task 3.2: the shipped rows carry a life from the owner's sixteen

**Files:** Modify the five `src/tree_design/library/*.json` files (the lead, applying §A's table as the owner ratifies it) · Test `tests/p10/test_library_lives.py` (new)

- [ ] **Step 1: Write the failing test.**

```python
# tests/p10/test_library_lives.py
"""`00` amendment 12 with 12a: every shipped situation is placed in one of the
owner's sixteen lives, and the sixteen are a MENU.

The sixteen are spelled here in the owner's words because they are the owner's
ratified vocabulary (`00` amendment 12, 17 Sep 2026: "use my reference's
list"). They are NOT spelled anywhere in `src/`: the product reads lives off
the rows and never off a list, which is how a life the library never imagined
can be added by the person without a library change (12a(ii)).
"""
from __future__ import annotations

import pytest

from production import life_of, load_shipped_catalogue, read_packaged_library_file, shipped_situations

THE_OWNERS_SIXTEEN = frozenset({
    "Personal", "Family and Household", "Work", "Career", "Education",
    "Teaching", "Finance and Taxes", "Home and Property", "Health",
    "Legal and Insurance", "Vehicles", "Travel", "Photos and Media",
    "Creative and Hobbies", "Technology", "Reference Library",
})


@pytest.fixture(scope="module")
def catalogue():
    return load_shipped_catalogue(read_packaged_library_file)


def test_every_shipped_situation_is_placed_in_a_life(catalogue):
    """SABOTAGE: ship one row without `life`. Its files fall through to the
    default branch on every corpus, with nothing on any screen saying why."""
    missing = sorted(row.name for row in shipped_situations(catalogue)
                     if life_of(catalogue, row.name) is None)
    assert missing == [], missing


def test_every_life_a_row_names_is_one_of_the_owners_sixteen(catalogue):
    """Closed to the model (12a(iii)): the judge reaches a life only through a
    row, so the rows may name only the ratified words. SABOTAGE: a row with
    `"life": "Academics"`. A seventeenth root appears that nobody ratified."""
    named = {row.life for row in catalogue.applicabilities.values()
             if row.life is not None}
    assert named <= THE_OWNERS_SIXTEEN, sorted(named - THE_OWNERS_SIXTEEN)


def test_no_life_is_spelled_in_src():
    """The menu lives in the rows, not in code. A list in `src/` would be the
    skeleton 12a forbids one step from being poured over every corpus."""
    import pathlib
    src = pathlib.Path(__file__).resolve().parents[2] / "src"
    offenders = [path for path in src.rglob("*.py")
                 if "Finance and Taxes" in path.read_text(encoding="utf-8")]
    assert offenders == [], offenders


def test_the_library_alone_does_not_decide_how_many_lives_a_tree_shows(catalogue):
    """12a(i) stated as a property of the READER: `life_of` is per situation,
    so a corpus of coursework alone reaches Education and nothing else. This
    is the pin against a producer that emits every life the library names.
    SABOTAGE: have `partition_by_branch` open a branch per distinct `life` in
    the catalogue -- this test cannot see that, which is why §D's gate exists
    and why `test_branch_situation_lives.py` pins it on the partition."""
    reached = {life_of(catalogue, "academic.coursework")}
    assert reached == {"Education"}
    assert len({row.life for row in catalogue.applicabilities.values()}) > 1
```

- [ ] **Step 2: Run it.** First test red with all 208 names listed; the fourth red (`None != "Education"`).
- [ ] **Step 3: Apply the rows** (lead, on the owner's word): add `"life"` and the provenance line to each of the 208 rows per §A's table. `python3 -c` over the five files is fine for the mechanical edit as long as the script is WRITTEN and reviewed, not derived (`run-scripts-are-written-not-derived`), and the diff is read before commit: 208 rows × 2 added keys, nothing else.
- [ ] **Step 4: Run it**, then `tests/p10/test_library_rows.py tests/p10/test_library_organisational.py tests/p10/test_library_practice.py tests/p10/test_library_industrial.py tests/p10/test_library_commerce.py tests/p10/test_library_definitions.py` — the row-count and label pins must still hold; only `release_id` moves.
- [ ] **Step 5: Commit.** `feat(00 amendment 12): 208 situations placed in the owner's sixteen lives` — the commit body carries the owner's ratification word or the date it is still owed.

### Task 3.3: `partition_by_branch` keys on the life

**Files:** Modify `src/branch_situation.py` (`Branch` at 104, `partition_by_branch` 249-478, `_settled_by_the_judge` 341) · Test `tests/test_branch_situation_lives.py` (new) · Modify `tests/test_branch_situation.py` (`_partition` helper gains the three parameters; assertions on `.schema` become `.schemas`) · Modify `tests/p6/test_p6_an_unsettled_branch_names_its_files_situations.py:35` (`Branch(schema=...)` → `schemas=(...,), life=..., situations=()`)

- [ ] **Step 1: Write the failing test.**

```python
# tests/test_branch_situation_lives.py
"""`00` amendment 12 with 12a: the partition keys on the LIFE a file's situation
points at, and a life appears only where the person's own files put it.

Every signal is a table, as in `test_branch_situation.py`, so a rule that moves
is caught by name. `LIVES` is a fixture mapping and not the shipped library:
these tests are about the KEY, and `test_library_lives.py` is about the rows.
"""
from __future__ import annotations

import pytest

from branch_situation import partition_by_branch
from facts.fields import DOMAIN_FIELDS


class _Verdict:
    def __init__(self, schema_id=None, tied=()):
        self.schema_id = schema_id
        self.tied_schema_ids = tuple(tied)


OWNERS = {"syllabus": "academic", "resume": "career"}
SITUATIONS = {"academic": ("academic.coursework", "academic.teaching"),
              "career": ("career.employment-records", "career.recruiting"),
              "college_applications": ("applications.undergraduate-packet",),
              "finance": ("finance.tax-filings", "finance.vehicle-records")}
LIVES = {"academic.coursework": "Education", "academic.teaching": "Teaching",
         "career.employment-records": "Career", "career.recruiting": "Career",
         "applications.undergraduate-packet": "Education",
         "finance.tax-filings": "Finance and Taxes",
         "finance.vehicle-records": "Vehicles"}


def _partition(files, *, named=None, facts=None, alternatives=None, anchors=None,
               chosen=None, default_situation="academic.coursework",
               default_label="Coursework", lives=LIVES):
    named = named or {}
    facts = facts or {}
    alternatives = alternatives or {}
    anchors = anchors or {}
    chosen = chosen or {}
    return partition_by_branch(
        roster=tuple((name, "h" * 64) for name in files),
        default_label=default_label, default_situation=default_situation,
        default_schema="academic",
        anchor_facts_of=lambda file_id, _hash: anchors.get(file_id, ()),
        owner_of_term=OWNERS,
        fields_of_schema=lambda schema_id: DOMAIN_FIELDS.get(schema_id, ()),
        verdict_of=lambda file_id, _hash: _Verdict(),
        situations_of=lambda schema_id: SITUATIONS.get(schema_id, ()),
        chosen_situation=lambda scope: chosen.get(scope),
        named_by_the_model=named,
        situations_named_by_the_model=facts,
        life_of=lambda situation: lives.get(situation),
        situation_fact_of=lambda file_id: facts.get(file_id),
        alternatives_of=lambda file_id: alternatives.get(file_id, ()))


def test_two_kinds_in_one_life_are_one_branch_labelled_with_the_life():
    """THE KEY. A coursework file and an application packet are two schemas
    and one life. SABOTAGE: key on the schema as before -- two branches
    `academic` and `college_applications`, the taxonomy of kinds."""
    partition = _partition(
        ["notes", "packet"], default_situation=None,
        named={"notes": "academic", "packet": "college_applications"},
        facts={"notes": "academic.coursework",
               "packet": "applications.undergraduate-packet"})

    education = partition.by_label("Education")
    assert education is not None
    assert education.life == "Education"
    assert set(education.file_ids) == {"notes", "packet"}
    assert education.schemas == ("academic", "college_applications")
    assert education.situations == ("academic.coursework",
                                    "applications.undergraduate-packet")
    assert partition.by_label("college_applications") is None


def test_a_life_no_file_reaches_is_not_a_branch():
    """12a(i): the menu is not the tree. `LIVES` names Vehicles; nothing here
    is a vehicle record. SABOTAGE: open a branch per distinct value of `LIVES`
    -- the sixteen-folder skeleton amendment 12a forbids."""
    partition = _partition(["notes"], default_situation=None,
                           named={"notes": "academic"},
                           facts={"notes": "academic.coursework"})

    # The default is unsettled (two academic situations, none typed), so it has
    # no life and the coursework file leaves it for Education; nothing else
    # opens. Two branches, and neither is a life the file did not reach.
    assert [branch.label for branch in partition.branches] == ["Coursework", "Education"]
    assert partition.by_label("Vehicles") is None


def test_a_typed_runs_own_life_stays_in_the_default_branch():
    """THE BYTE PIN (`test_r37_single_branch_is_byte_identical`): a typed
    `--situation academic.coursework` over coursework is ONE branch, exactly as
    before. SABOTAGE: put every lived file in a life branch -- a second root
    named Education beside `Coursework`, and the pin's fixture breaks.
    SABOTAGE 2: keep the `len(schemas) == 1` early return. This stays green
    without the rule ever running -- which is why the untyped test below exists."""
    partition = _partition(["a", "b"], named={"a": "academic", "b": "academic"},
                           facts={"a": "academic.coursework",
                                  "b": "academic.coursework"})

    assert partition.single
    assert partition.default.life == "Education"
    assert set(partition.default.file_ids) == {"a", "b"}


def test_an_untyped_run_keeps_only_the_residue_in_the_default_branch():
    """With nothing typed the top level is lives, and the folder's own branch
    holds what has none. Here the person even answered the default's question
    (coursework) -- that settles the DEFAULT's situation for P11's root map and
    pulls no file back: `Downloads` is not a life. SABOTAGE: apply the typed
    rule untyped. The coursework files sit under `Downloads` and the root that
    reads as a life is empty."""
    partition = _partition(["a", "z"], default_situation=None,
                           default_label="Downloads",
                           named={"a": "academic"},
                           facts={"a": "academic.coursework"},
                           chosen={"branch:Downloads": "academic.coursework"})

    assert partition.default.situation == "academic.coursework"
    assert partition.default.life == "Education"
    assert partition.default.file_ids == ("z",)
    assert partition.by_label("Education").file_ids == ("a",)


def test_a_file_of_another_life_leaves_the_default_branch():
    """Priya teaches. `68` F6's graduate student: her teaching material was
    filed as coursework because the command line took one situation for the
    disk. Under amendment 12 it is under Teaching."""
    partition = _partition(["hw", "rubric"],
                           named={"hw": "academic", "rubric": "academic"},
                           facts={"hw": "academic.coursework",
                                  "rubric": "academic.teaching"})

    assert partition.default.file_ids == ("hw",)
    assert partition.by_label("Teaching").file_ids == ("rubric",)


def test_the_alternatives_decide_only_when_they_agree_on_one_life():
    """The tie-break. No first choice; two alternatives in one life is that
    life; two alternatives in two lives is nothing (and the default holds it).
    SABOTAGE: take the first alternative. `sorted()` order decides a life."""
    agree = _partition(["x"], default_situation=None, named={"x": "career"},
                       alternatives={"x": ("career.recruiting",
                                           "career.employment-records")})
    disagree = _partition(["y"], default_situation=None, named={"y": "finance"},
                          alternatives={"y": ("finance.tax-filings",
                                              "finance.vehicle-records")})

    assert agree.by_label("Career").file_ids == ("x",)
    assert disagree.default.file_ids == ("y",)


def test_a_file_with_no_situation_takes_the_librarys_one_life_for_its_kind():
    """Arm 3: the gate-refused résumé. No judge reached it; its `resume` anchor
    is career's, and every career situation is Career. SABOTAGE: drop the arm.
    The 87 files the gate refused all fall to the default branch, and a résumé
    is placed under the run's coursework levels -- R-23 again."""
    partition = _partition(["cv"], default_situation=None,
                           anchors={"cv": (("work_type", "resume"),)})

    assert partition.by_label("Career").file_ids == ("cv",)
    assert partition.by_label("Career").situation is None


def test_a_file_with_no_situation_takes_the_corpus_one_life_for_its_kind():
    """Arm 4: the gate-refused syllabus. `academic` spans Education and
    Teaching in the library, so arm 3 says nothing; every judged academic file
    in THIS folder is coursework, so the corpus says Education. SABOTAGE:
    drop the arm. The syllabus sits in the default branch with no question."""
    partition = _partition(
        ["s", "a", "b"], default_situation=None,
        named={"a": "academic", "b": "academic"},
        facts={"a": "academic.coursework", "b": "academic.coursework"},
        anchors={"s": (("work_type", "syllabus"),)})

    assert set(partition.by_label("Education").file_ids) == {"s", "a", "b"}


def test_a_kind_the_corpus_and_library_both_split_leaves_the_file_in_the_default():
    """Arms 3 and 4 both silent: `academic` spans two lives and the folder's
    judged academic files span both. The file has no life; R-140 puts it under
    the default branch and NOTHING picks. SABOTAGE: majority vote over arm 4 --
    `this module choosing a situation on the person's behalf`, one level up."""
    partition = _partition(
        ["s", "a", "b"], default_situation=None,
        named={"a": "academic", "b": "academic"},
        facts={"a": "academic.coursework", "b": "academic.teaching"},
        anchors={"s": (("work_type", "syllabus"),)})

    assert partition.default.file_ids == ("s",)


def test_a_life_branch_holding_two_situations_is_unsettled_and_asks_nothing():
    """"Which situation is Education?" is not a question when Education holds
    coursework and a thesis. Unsettled, no candidates: Phase 2(a)'s third arm
    hands the router every situation its files carry."""
    partition = _partition(["n", "p"], default_situation=None,
                           named={"n": "academic", "p": "college_applications"},
                           facts={"n": "academic.coursework",
                                  "p": "applications.undergraduate-packet"})

    education = partition.by_label("Education")
    assert education.situation is None
    assert education.candidate_situations == ()


def test_a_life_branch_the_judge_named_one_situation_for_is_settled_by_it():
    """`_settled_by_the_judge`, unchanged: unanimous over every file."""
    partition = _partition(["n", "m"], default_situation=None,
                           named={"n": "academic", "m": "academic"},
                           facts={"n": "academic.coursework",
                                  "m": "academic.coursework"})

    assert partition.by_label("Education").situation == "academic.coursework"


def test_the_persons_answer_at_the_lifes_scope_settles_it():
    partition = _partition(["n", "p"], default_situation=None,
                           named={"n": "academic", "p": "academic"},
                           facts={"n": "academic.coursework",
                                  "p": "academic.teaching"},
                           chosen={"branch:Teaching": "academic.teaching"})

    assert partition.by_label("Teaching").situation == "academic.teaching"
    assert partition.by_label("Education").situation == "academic.coursework"


def test_no_file_is_lost_in_the_fold():
    """Coverage is sacred. Every rostered file is under exactly one branch or
    held -- `BranchPartition.__post_init__` refuses two places, this refuses
    none."""
    files = ["a", "b", "c", "d", "e"]
    partition = _partition(
        files, default_situation=None,
        named={"a": "academic", "b": "career", "c": "finance"},
        facts={"a": "academic.coursework", "b": "career.recruiting",
               "c": "finance.tax-filings"},
        anchors={"d": (("work_type", "resume"),)})

    placed = [f for branch in partition.branches for f in branch.file_ids]
    assert sorted(placed + list(partition.held)) == sorted(files)
```

- [ ] **Step 2: Run it.** `nice -n 15 python3 -m pytest tests/test_branch_situation_lives.py -p no:randomly -q` → `TypeError: partition_by_branch() got an unexpected keyword argument 'life_of'`.
- [ ] **Step 3: Implement** §B's `Branch` and the tail of `partition_by_branch`: delete the `if len(schemas) == 1:` early return (`branch_situation.py:397-404`); add `fell_through: set[str] = set()` beside `held` and `fell_through.add(file_id)` in the reach loop's `elif not reached:` arm; replace everything from `branches: list[Branch] = []` with §B's tail. Update the module docstring's "A branch's situation" paragraph with §B's four arms and the typed/untyped rule. `_settled_by_the_judge` reads `situation_fact_of`.
- [ ] **Step 4: Run it, then `tests/test_branch_situation.py`.** The old file's `_partition` helper gains `life_of=lambda s: None, situation_fact_of=lambda f: None, alternatives_of=lambda f: ()` — with no lives every file's life is `None`, every file falls to the default branch, and **eleven of its eighteen tests go red on purpose**: `test_an_anchor_of_another_schema_opens_a_second_branch`, `test_a_fact_on_the_schemas_own_field_reaches_and_a_bridge_does_not`, `test_a_fact_outranks_the_recognisers_reading`, `test_the_recognisers_reading_reaches_a_branch_that_exists_and_opens_none`, `test_a_file_two_branches_reach_is_held_not_guessed`, `test_an_anchors_own_reading_never_moves_it`, `test_a_branch_with_one_shipped_situation_is_settled_and_otherwise_asked`, `test_the_persons_answer_settles_the_branch_and_only_that_branch`, `test_an_answer_naming_a_situation_of_another_schema_settles_nothing`, `test_a_schema_site_g_named_opens_its_own_branch_and_takes_its_file`, `test_a_branch_site_g_opened_is_unsettled_like_every_other_branch`, `test_a_branch_site_g_opened_is_settled_by_the_librarys_one_situation`. Each is a pin on a KIND being a branch. Rewrite each against a `LIVES` table where its two kinds are two lives (`academic` → Education, `career` → Career, `code` → Technology) and its assertions read `by_label("Career")` where they read `by_label("career")`. `test_a_file_two_branches_reach_is_held_not_guessed` is unchanged in meaning: `held` is computed before the fold. Do not delete a test; a pin that no longer holds is rewritten to say what holds now.
- [ ] **Step 5: `tests/p6/test_p6_an_unsettled_branch_names_its_files_situations.py`** — the `_branch` helper: `Branch(label="Education", life="Education", schemas=("academic",), situations=(), situation=situation, is_default=False, anchor_file_ids=(), file_ids=file_ids)`. Four tests, unchanged in meaning.
- [ ] **Step 6: Commit.** `feat(00 amendment 12): partition_by_branch keys on the life a file's situation points at`

### Task 3.4: one draft per (life, schema), labelled with the life

**Files:** Modify `src/cli.py` (`_grouped_by_branch` 10919-10957, `draft_for_review` 10787) · Test `tests/test_cli_lives_drafts.py` (new)

**Why.** `_draft_as_one` writes one `group_category` per draft and `eligible_rows` reads it as the branch's domain (§0). A life with two schemas needs two drafts. The category is the GROUP's — the schema its members' situations resolve to — not the branch's.

**The trade, for the lead to see.** A P9 group whose members' schemas TIE (a group of one coursework file and one application packet, both under Education) has no one category, and this draft sends it to the DEFAULT branch under the default's first schema — it leaves its life because its category tied, even though every member sits under Education. That is "a tie decides nothing" applied one field over, and the alternative — splitting the group by schema — is this module deciding P9's membership. On the owner's corpus 161 of 176 anchors are duplicates, file format or kind (`106`), so a group straddling two schemas is rare; §D's `decided == len(roster)` counts such files either way. If the number is not small, the fix is in P9's grouping (Phase 6), not here.

- [ ] **Step 1: Write the failing test.**

```python
# tests/test_cli_lives_drafts.py
"""`00` amendment 12: a life spanning two schemas is drafted as two groups,
both labelled with the life, so `routing.eligible_rows` -- which admits a row
only for a domain the branch's groups carry -- can compose per coverage.

Driven through `_grouped_by_branch` with its one store read patched, as
`tests/test_branch_situation.py` drives the partition: the bucketing rule is
what is pinned, and a corpus would pin the screen instead.
"""
from __future__ import annotations

from types import SimpleNamespace

import cli
from branch_situation import Branch


def _branch(label, life, schemas, files, default=False):
    return Branch(label=label, life=life, schemas=tuple(schemas), situations=(),
                  situation=None, is_default=default, anchor_file_ids=(),
                  file_ids=tuple(files))


def _result(group_id):
    return SimpleNamespace(group=SimpleNamespace(group_id=group_id),
                           stop_rule_outcome=None)


def _members(table):
    return lambda conn, group_id: [SimpleNamespace(file_id=f) for f in table[group_id]]


def test_a_life_holding_two_schemas_yields_two_buckets_wearing_one_label(monkeypatch):
    """SABOTAGE: bucket by `branch.label` alone, category `branch.schemas[0]`.
    One draft, category `academic`; the packet's `college_applications` rows are
    never eligible and the application files sit at Education's root with no
    levels."""
    education = _branch("Education", "Education", ("academic", "college_applications"),
                        ("n1", "n2", "p1"))
    default = _branch("Downloads", None, ("academic",), (), default=True)
    monkeypatch.setattr(cli, "memberships_for_group",
                        _members({"g_notes": ["n1", "n2"], "g_packet": ["p1"]}))
    schema_of = {"n1": "academic", "n2": "academic", "p1": "college_applications"}

    buckets = cli._grouped_by_branch(
        None, [_result("g_notes"), _result("g_packet")],
        branch_for=lambda f: education, default=default,
        schema_of_file=schema_of.get)

    assert [(label, category, [r.group.group_id for r in bucket])
            for _branch_, category, label, bucket in buckets] == [
        ("Education", "academic", ["g_notes"]),
        ("Education", "college_applications", ["g_packet"])]


def test_a_group_whose_members_span_two_schemas_is_the_defaults(monkeypatch):
    """A tie decides nothing -- `_grouped_by_branch`'s own rule for branches,
    applied to the category. SABOTAGE: majority. This module picks a kind."""
    education = _branch("Education", "Education", ("academic", "college_applications"),
                        ("n1", "p1"))
    default = _branch("Downloads", None, ("academic",), (), default=True)
    monkeypatch.setattr(cli, "memberships_for_group", _members({"g_mixed": ["n1", "p1"]}))

    buckets = cli._grouped_by_branch(
        None, [_result("g_mixed")], branch_for=lambda f: education,
        default=default, schema_of_file={"n1": "academic",
                                         "p1": "college_applications"}.get)

    assert [(label, category) for _b, category, label, _k in buckets] == [
        ("Downloads", "academic")]


def test_a_single_schema_branch_drafts_exactly_as_before(monkeypatch):
    """The r37 case: one kind, one draft, the category the branch carries."""
    coursework = _branch("Coursework", "Education", ("academic",), ("a", "b"), default=True)
    monkeypatch.setattr(cli, "memberships_for_group", _members({"g1": ["a", "b"]}))

    buckets = cli._grouped_by_branch(
        None, [_result("g1")], branch_for=lambda f: coursework,
        default=coursework, schema_of_file=lambda f: "academic")

    assert [(label, category) for _b, category, label, _k in buckets] == [
        ("Coursework", "academic")]
```

- [ ] **Step 2: Run it.** `TypeError: _grouped_by_branch() got an unexpected keyword argument 'schema_of_file'`.
- [ ] **Step 3: Implement.** `_grouped_by_branch(conn, grouped, branch_for, default, schema_of_file)`: the vote over members' branches is unchanged; beside it, vote the members' schemas through `schema_of_file` — exactly one leader is the group's category; a tie or no member with a schema falls back to the branch's only schema when `len(branch.schemas) == 1`, else the group is the DEFAULT's under the default's first schema (the same "a tie decides nothing" the branch vote already applies). Bucket key becomes `(chosen.label, category)`; the returned tuple is unchanged in shape `(branch, category, label, bucket)`; ordering `(not is_default, label, category)`. `draft_for_review` gains `schema_of_file` and passes it through; its caller at `cli.py:16344` binds `lambda f: (lambda s: None if s is None else schema_for_situation(catalogue, s))(_situation_fact_of(f))`, spelled as a named closure `_schema_of_file` beside `_situation_fact_of`. `_draft_as_one` is untouched: the category in `merged_id` keeps the two Education drafts distinct addresses.
- [ ] **Step 4: Run it**, then `tests/test_cli.py -k "draft or branch or group"`.
- [ ] **Step 5: Commit.** `feat(00 amendment 12): a life spanning two schemas is drafted per schema and labelled once`

### Task 3.5: every reader of `Branch.schema` and of a branch's situation

**Files:** Modify `src/cli.py` at the lines below · Test: the tests named beside each.

No new test file: each line has a pin already, and the change at each is mechanical. Run the named test after each edit.

- [ ] `cli.py:16041` `active_domains`: `tuple(dict.fromkeys(schema for branch in branches for schema in branch.schemas)) or (said().schema,)`. Pin: `tests/p10/test_p10_multi_life.py::test_the_whole_chain_still_designs_every_life_when_one_domain_is_inactive`.
- [ ] `cli.py:18170-18182` the per-branch resolver: a settled branch has one situation and therefore one schema — `schema = schema_for_situation(catalogue, branch.situation)` and use it in `evidence_activation(schema)` and `rules.schemas[schema]`. Pin: `tests/integration/test_template_levels_wiring.py`.
- [ ] `cli.py:17611` `_the_situation_the_person_chose(schema_id)`: the scope is the branch the FILE is in, not `branch:<schema>` — signature becomes `(file_id, schema_id)`, reads `partition_cell[0].branch_of(file_id)` and its `.scope`, checks the answer against `_situations_of(schema_id)` as now. Pin: `tests/integration/test_a_situation_is_never_the_first_of_twenty_six.py`.
- [ ] `cli.py:17918` `_ask_which_situation_each_branch_is`: `if branch.settled or not branch.candidate_situations or (not branch.file_ids and not branch.is_default): continue` — a life branch with `()` asks nothing (§B). Pin: `tests/integration/test_the_level_answer_is_written_down.py::test_the_run_still_does_not_ask_the_person_about_that_branch`.
- [ ] `cli.py:17510` and `cli.py:17505` — **P11 compares at the life grain.** `placement/pipeline.py:1905` abstains `SITUATION_UNANSWERED` only when `the_situation_each_branch_carries` is non-empty and `situation_of(file)` is `None`; `_only_this_files_own_branch` (def at `:682`, called at `:1838`) drops a candidate whose root carries another value. Both are built from SETTLED branches only, and a life root holding two situations is unsettled — so after 3.3 the map empties on the owner's corpus and both guards go inert: unanswered files get placed into whatever tree, a paper is retrieved against Education's coursework folders. P11 never inspects these strings; it compares them (`:725`, `:1905`, `:1943`). So the composition root hands it the same grain on both sides and P11 is untouched:

```python
            situation_of=lambda file_id: (
                lambda s: None if s is None else life_of(catalogue, s))(
                    _the_situation_this_file_is_under(file_id)),
            the_situation_each_branch_carries={
                branch.label: branch.life
                for branch in (partition_cell[0].branches if partition_cell else ())
                if branch.life is not None},
```

  spelled as a named closure `_the_life_this_file_is_under`, with a comment saying P11's field names say "situation" and the grain is now the life. Pin: `tests/p11/test_p11_pipeline.py` (unchanged — P11 is not edited) and `tests/integration/test_p10_p11_live_seam.py`. What this does NOT guard, said plainly: spillover BETWEEN situations inside one life (a thesis into a coursework folder). The root-level guard never guarded inside a situation either; that is Phase 7's depth work.
- [ ] `cli.py:17870` the untyped default label: `default_label = label if label is not None else folder_label(str(directory))` — the scanned folder's own name, never `default_schema` (§B). Pin: `tests/integration/test_a_situation_is_never_the_first_of_twenty_six.py` and `tests/test_cli.py -k "untyped or no_situation"`; the closing screen's branch question reads `Which of these is Downloads?` instead of `... is academic?`, which is the sentence the owner refused on 14 Sep read one word closer to theirs.
- [ ] `cli.py:10986` is Task 3.4's. `cli.py:18336` `votes_cell` and `branch_votes` are keyed by label and need nothing.
- [ ] Commit. `feat(00 amendment 12): every reader of a branch reads its lives and schemas`

### Task 3.6: retire `situations_named_by_the_model` from the partition

- [ ] After 3.3-3.5 are green: remove the parameter from `partition_by_branch` and its binding at `cli.py:17890`; `_settled_by_the_judge` already reads the fact. `tests/test_branch_situation.py` drops the kwarg. One-purpose commit: `refactor(106 Phase 3): the partition reads the judge's answer as the fact it is, not the pass object`.

**Phase 3 gate:** `tests/test_branch_situation.py tests/test_branch_situation_lives.py tests/p6 tests/p10 tests/p11 tests/integration/test_r37_single_branch_is_byte_identical.py tests/integration/test_the_level_answer_is_written_down.py` green on a quiet machine; then the chunked suite; then the sort run and §D. The Phase 1 grouping number has not fallen — §D prints it beside the roots.

---

## D. The "fewer than sixteen" gate, as the query the lead runs

**After** the next sort run finishes (the WAL on `run12.sqlite` was live at 23:43 on 17 Sep). Read-only, aggregates only, no filename printed. Run from the repository root with `GRAPH_AGENT_NO_DOTENV=1`.

```python
# gate_lives.py -- §D of the Phase 3/4 draft. Prints numbers, names no file.
import sqlite3, sys
sys.path.insert(0, "src")
from collections import Counter
from facts.llm_seam import SITUATION_FIELD
from facts.supersede import preferred_fact
from production import life_of, load_shipped_catalogue, read_packaged_library_file

DB = sys.argv[1]
conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row
catalogue = load_shipped_catalogue(read_packaged_library_file)
shipped_lives = {row.life for row in catalogue.applicabilities.values() if row.life}

# 1. What the FACTS say: the life of every file's situation.
value_of = {r["value_id"]: r["canonical_value"] for r in conn.execute(
    'select value_id, canonical_value from "values" where field_key = ?', (SITUATION_FIELD,))}
roster = [r["file_id"] for r in conn.execute("select file_id from files")]
lives_in_facts, unmapped, no_fact = Counter(), 0, 0
for file_id in roster:
    fact = preferred_fact(conn, file_id=file_id, field_key=SITUATION_FIELD)
    if fact is None:
        no_fact += 1
        continue
    life = life_of(catalogue, value_of[fact["value_id"]])
    if life is None:
        unmapped += 1
    else:
        lives_in_facts[life] += 1

# 2. What the TREE says: the roots of the latest frozen plan.
plan = conn.execute("select plan_version_id from frozen_trees order by created_at desc limit 1").fetchone()[0]
roots = [r["display_label"] for r in conn.execute(
    "select display_label from tree_nodes where plan_version_id = ? and parent_node_id is null "
    "and node_type = 'proposed' order by ordinal", (plan,))]
life_roots = [r for r in roots if r in shipped_lives]

# 3. What PLACEMENT says: no file lost.
decided = conn.execute(
    "select count(distinct subject_ref) from placement_decisions "
    "where plan_version = ? and superseded_by is null", (plan,)).fetchone()[0]

print(f"files {len(roster)}  with a situation fact {len(roster) - no_fact}  "
      f"mapped to a life {sum(lives_in_facts.values())}  unmapped {unmapped}")
print(f"lives the facts name: {len(lives_in_facts)} of {len(shipped_lives)} shipped -> "
      + ", ".join(f"{life} {n}" for life, n in lives_in_facts.most_common()))
print(f"proposed roots: {len(roots)}; of them lives: {len(life_roots)} -> {life_roots}")
print(f"files with a current placement decision: {decided} of {len(roster)}")

# THE GATE, falsifiable in both directions.
assert 0 < len(life_roots) < 16, "no life root, or the sixteen-folder skeleton"
assert set(life_roots) <= set(lives_in_facts), "a root no file's situation supports (an empty Vehicles/)"
assert unmapped == 0, "a situation the library has not placed in a life"
assert decided == len(roster), "a file with no placement decision at all"
```

**Narrow versus broken, and how the numbers tell them apart:**

| reading | verdict |
| --- | --- |
| `lives the facts name` is small AND `proposed roots: lives` equals it | few lives because the CORPUS is narrow — the gate passes |
| `lives the facts name` > `lives` among roots | files carry lives the tree does not show: the fold (Phase 4) or the partition dropped a life — broken |
| `lives the facts name` = 0 with hundreds of situation facts | `life_of` reads nothing: the rows were not applied or the fact still holds the KIND (§0 item 2) — broken |
| `unmapped` > 0 | a shipped row without `life`; 3.2's test should have caught it |
| roots that are not lives and not the person's folders | a kind is still a root label: `_grouped_by_branch` or a branch label leaked — broken |

Beside it, the Phase 1 grouping number from `tools/groundtruth/report.py`, taken the same way as the baseline; a fall is a Phase 3 regression whatever the roots say.

---

## E. Phase 4 — the area fold

**What exists.** `route_branch` composes per coverage over a branch's plural groups (`routing.py:626-676`); `BranchCandidate.accepted_group_ids` is already plural (`candidates.py:103`), built today as a one-tuple (`candidates.py:340`) and empty for a directory card (`candidates.py:365`) — the fold changes the first and must leave the second alone; `_design_one_branch` iterates it (`pipeline.py:870-871`, def at `:1039`), so does the composition root (`production.py:1086`), and it is frozen and thawed as a list (`freeze.py:313`, `:353`), so a folded card survives a freeze; `test_p10_multi_life.py::test_a_branch_designed_from_several_groups_counts_every_one_of_their_files` already merges two lives into one candidate by `dataclasses.replace(candidate, accepted_group_ids=(A, B))` and proves every file is counted. Phase 4 computes that merge from the label instead of by hand.

**Where.** Inside `horizontal_candidates` (`candidates.py:259`), over the ACCEPTED GROUPS before cards are built — not over cards after. A card carries `supporting_file_count` and not member ids, and `00`:63 lets one file be in two groups, so a fold over cards would count a shared file twice on the card and in `_with_refinement`'s `file_count`. The fold is one function, `same_label_areas(accepted)`, and the loop iterates its result. It keys on `display_label`: "two accepted groups wearing one label are one area" is true whether the label came from the life (Phase 3) or from the person renaming two drafts to one word (12a(ii)) — no life is read here, so the fold works for a life the library never imagined.

**The card's identity.** A label with ONE group keeps `subject_id = group_id` (every existing pin holds). A label with two or more gets `subject_id = f"area:{label}"` and `accepted_group_ids` = every group's id in accepted order. `design_tree`'s chosen filter (`pipeline.py:838`) admits a card when its `subject_id` OR ANY of its `accepted_group_ids` is in `decisions.branch_group_ids` — `cli.py:16230` passes every accepted id, so a folded area is chosen when any of its drafts was. Phase 5's stable node key is the right place for `area:` to become a durable id; here it only has to be chosen.

**12a(ii), the door.** Rename: `RENAME` on the root node (`store.py:617`, `user_level_edits`). Remove: `suppressed_branch_basis_keys` (`candidates.py:282`). Merge/split: rename two drafts to one label, or one draft's groups to two — the fold follows the label. **Add a life the library never imagined:** `horizontal_candidates(user_labels=...)` already emits a `"user-label"` card ("You created this branch by name", `candidates.py:373-389`) and `pipeline.py:835` passes `user_labels=()` — wired to nothing. That is the seam; it is named here and not built in Phase 4, because a person's label with no gesture to put a group under it (`DRAG_GROUP_INTO_BRANCH`, `vocabulary.py:413`, also unwired) is a folder with nothing in it. Both belong to Phase 5's edit surface.

### Task 4.1: two accepted groups wearing one label are one area

**Files:** Modify `src/tree_design/candidates.py` (`horizontal_candidates`, loop at 300; new `same_label_areas` above it) · Test `tests/p10/test_p10_area_fold.py` (new)

- [ ] **Step 1: Write the failing test.**

```python
# tests/p10/test_p10_area_fold.py
"""`00`:67 -- "aggregates ... into a small set of proposed major areas" -- had
no producer: one root card per accepted group. After amendment 12 a life that
spans two schemas is two drafts wearing one label, and this is the fold that
makes them one area with plural `accepted_group_ids`. No new node type; the
plural field `_design_one_branch` already reads.
"""
from __future__ import annotations

from tree_design.candidates import horizontal_candidates, same_label_areas
from tree_design.schema import create_tree_schema
from tree_design.upstream import AcceptedGroup, GroupMember


def _group(group_id, label, domain, files):
    return AcceptedGroup(
        group_id=group_id, label=label, domain=domain,
        members=tuple(GroupMember(f, f"h_{f}", "direct-anchor") for f in files),
        anchor_facts=(f"fact_{group_id}",), excluded_members=())


NOTES = _group("v1:academic:Education:aaaa", "Education", "academic", ["n1", "n2"])
PACKET = _group("v1:college_applications:Education:bbbb", "Education",
                "college_applications", ["p1", "n2"])
CV = _group("v1:career:Career:cccc", "Career", "career", ["c1"])


def test_same_label_groups_fold_and_different_labels_do_not():
    areas = same_label_areas((NOTES, PACKET, CV))

    assert [[g.group_id for g in area] for area in areas] == [
        [NOTES.group_id, PACKET.group_id], [CV.group_id]]


def test_a_folded_area_is_one_card_naming_every_group_and_counting_every_file_once(conn):
    """SABOTAGE: sum the two counts. `n2` is in both groups (`00`:63) and the
    card says 5 files over 4. SABOTAGE: fold the cards after they are built --
    the same double count, because a card carries no member ids."""
    create_tree_schema(conn)
    cards = horizontal_candidates(
        conn, accepted=(NOTES, PACKET, CV), existing_folders=(), user_labels=(),
        active_domains=("academic", "college_applications", "career"),
        sensitive_group_ids=frozenset())

    education = next(c for c in cards if c.display_label == "Education")
    assert education.subject_id == "area:Education"
    assert education.accepted_group_ids == (NOTES.group_id, PACKET.group_id)
    assert education.supporting_file_count == 4
    assert education.source == "accepted-group"
    career = next(c for c in cards if c.display_label == "Career")
    assert career.subject_id == CV.group_id
    assert career.accepted_group_ids == (CV.group_id,)


def test_no_group_is_lost_in_the_fold(conn):
    """Every accepted group is named by exactly one card."""
    create_tree_schema(conn)
    cards = horizontal_candidates(
        conn, accepted=(NOTES, PACKET, CV), existing_folders=(), user_labels=(),
        active_domains=("academic",), sensitive_group_ids=frozenset())

    named = [g for c in cards for g in c.accepted_group_ids]
    assert sorted(named) == sorted([NOTES.group_id, PACKET.group_id, CV.group_id])
    assert len(named) == len(set(named))


def test_a_sensitive_group_makes_the_whole_area_sensitive(conn):
    """Marked and counted: one protected draft under a life marks the area,
    never the reverse. SABOTAGE: `all(...)` instead of `any(...)`."""
    create_tree_schema(conn)
    cards = horizontal_candidates(
        conn, accepted=(NOTES, PACKET), existing_folders=(), user_labels=(),
        active_domains=("academic",), sensitive_group_ids=frozenset({PACKET.group_id}))

    assert next(c for c in cards if c.display_label == "Education").sensitive_content_present
```

- [ ] **Step 2: Run it.** `ImportError: cannot import name 'same_label_areas'`.
- [ ] **Step 3: Implement.**

```python
def same_label_areas(accepted: Sequence[AcceptedGroup],
                     ) -> tuple[tuple[AcceptedGroup, ...], ...]:
    """`00`:67's aggregation, keyed on the LABEL the drafts wear.

    Two accepted groups wearing one label are one area, whether the label is a
    life (`00` amendment 12: `_grouped_by_branch` drafts a life once per schema
    it spans) or the person's own word on two drafts (12a(ii)). No life is read
    here, so a life the library never imagined folds like any other.

    Accepted order kept, first-seen order of labels kept, nothing dropped.
    """
    areas: dict[str, list[AcceptedGroup]] = {}
    for group in accepted:
        areas.setdefault(group.label, []).append(group)
    return tuple(tuple(groups) for groups in areas.values())
```

In `horizontal_candidates`, `for group in accepted:` becomes `for area in same_label_areas(accepted):` with `first = area[0]`; `members = {m.file_id for g in area for m in g.members}` (the count is `len(members)`); `subject_id = first.group_id if len(area) == 1 else f"area:{first.label}"`; `accepted_group_ids = tuple(g.group_id for g in area)`; `representative_group_labels = (first.label,)`; `sensitive = any(g.group_id in sensitive_group_ids for g in area)`; `inactive` is per group and the detail sentence names each inactive schema; `resembling` uses `first.label`. The detail sentence for a folded area: `f"{len(members)} file(s) in {len(area)} accepted groups labelled {label!r} share validated facts in the {', '.join(domains)} schemas"`.
- [ ] **Step 4: Run it**, then `tests/p10/test_p10_candidates.py tests/p10/test_p10_multi_life.py tests/p10/test_p10_existing_folders.py` — every existing pin builds one group per label, so `subject_id == group_id` holds throughout.
- [ ] **Step 5: Commit.** `feat(00:67): two accepted groups wearing one label are one proposed area`

### Task 4.2: a folded area is chosen when any of its drafts was

**Files:** Modify `src/tree_design/pipeline.py:838` · Test `tests/p10/test_p10_area_fold.py` (append)

- [ ] **Step 1: Append the failing test.**

```python
def test_a_folded_area_is_designed_once_and_every_file_of_both_lives_is_under_it(corpus):
    """THE GATE: no file loses a home in the fold. Through `design_tree` on the
    three-life corpus with the practice and the degree relabelled to one word by
    the person, exactly as 12a(ii) lets them.

    SABOTAGE: leave the chosen filter on `subject_id` alone. `area:Work` is in
    no `branch_group_ids`, `NothingToDesign` is raised, and two accepted lives
    have no node at all -- the silent omission the standing rule forbids.
    """
    import dataclasses

    from p10.multi_life_corpus import ACADEMIC_GROUP, LAW_GROUP, MEDICAL_GROUP
    from p10.test_p10_multi_life import authorities, decisions, design

    class _Relabelled:
        """The person renamed two drafts to one word; the store is untouched."""
        def __init__(self, inner):
            self._inner = inner
        def __getattr__(self, name):
            return getattr(self._inner, name)
        def group(self, group_id):
            group = self._inner.group(group_id)
            if group_id in (ACADEMIC_GROUP, LAW_GROUP):
                return dataclasses.replace(group, display_label="Work")
            return group

    result = design(corpus, auth=authorities(corpus, group_reader=_Relabelled(corpus.reader())))

    work = next(b for b in result.branches if b.candidate.display_label == "Work")
    assert set(work.candidate.accepted_group_ids) == {ACADEMIC_GROUP, LAW_GROUP}
    every_file = corpus.group_file_ids(ACADEMIC_GROUP) | corpus.group_file_ids(LAW_GROUP)
    assert work.options[0].member_count == len(every_file)
    covered = frozenset().union(*(frozenset(c.covered_file_ids)
                                  for c in work.routing.candidates))
    assert covered == every_file
    roots = [n for n in result.tree.nodes if n.parent_node_id is None
             and n.node_type == "proposed"]
    assert [n.display_label for n in roots].count("Work") == 1
    associated = {g for n in result.tree.nodes for g in n.associated_group_ids}
    assert {ACADEMIC_GROUP, LAW_GROUP, MEDICAL_GROUP} <= associated
```

(`corpus` is `test_p10_multi_life.py`'s fixture; import it via `from p10.test_p10_multi_life import corpus  # noqa: F401` at the top of the file, as that module's own fixtures are module-scoped functions.)

- [ ] **Step 2: Run it.** `NothingToDesign`.
- [ ] **Step 3: Implement.** `pipeline.py:838`:

```python
    wanted = set(decisions.branch_group_ids)
    chosen = tuple(candidate for candidate in candidates
                   if candidate.subject_id in wanted
                   or any(group_id in wanted
                          for group_id in candidate.accepted_group_ids))
```

with a comment: an area folded from several accepted drafts is chosen when any of them was; `cli.design_decisions` names every accepted draft.
- [ ] **Step 4: Run it**, then `tests/p10/test_p10_pipeline.py tests/p10/test_p10_multi_life.py`.
- [ ] **Step 5: Commit.** `feat(00:67): a folded area is chosen when any of its drafts was`

**Phase 4 gate:** §D's `proposed roots` is a small set of lives plus the person's own folders, never two roots wearing one life; `test_a_folded_area_is_designed_once_...` green; `decided == len(roster)`.

**Said plainly about depth inside an area.** `nesting_chooser` (`cli.py`, `theirs = ... sum(1 for option in options if would_build(option)) > 1`) returns `None` when a branch offers two buildable shapes, and a folded area with two coverages offers exactly two — one per recipe. So on the owner's corpus a multi-schema area is presented with its root node and both options, and its levels are built when the person answers `--answer` at `branch:<label>`. Every file is under the root (the gate holds); the depth inside waits on the person. That is `104` R-92's own behaviour and Phase 5's "three screens", not a defect of the fold; but it is why Phases 3-4 add no level, as `106`'s closing section already says. A later change could apply disjoint coverages without asking, since they contend for no file; that is a `_design_one_branch` change and is not in this phase.

---

## F. The risk register

| # | what Phase 3 could regress | the pin that catches it | rollback |
| --- | --- | --- | --- |
| 1 | **Single-branch runs stop being byte-identical.** Lived files leave the default branch. | `tests/integration/test_r37_single_branch_is_byte_identical.py`; §C 3.3's `test_a_typed_runs_own_life_stays_in_the_default_branch` is the unit pin, and `test_an_untyped_run_keeps_only_the_residue_in_the_default_branch` proves the rule ran | the typed `default_life` rule (§B); if the fixture still moves for a reason that is not R-37's, read the diff before recapturing |
| 2 | **The 87 gate-refused files fall to the default branch** and lose the kind branch `_settled_by_the_judge` could settle. | `test_a_file_with_no_situation_takes_the_librarys_one_life_for_its_kind`, `..._the_corpus_one_life_for_its_kind`; §D's `decided == len(roster)` | arms 3-4 of §B; the residue is Phase 7's `98` under amendment 13 |
| 3 | **A résumé placed under coursework levels** (R-23) if a fact-less file lands in the default and the default is settled. | `_the_situation_this_file_is_under` returns `None` for a named kind with no situation (`cli.py:17765`); `tests/integration/test_a_situation_is_never_the_first_of_twenty_six.py`; `test_p11_pipeline.py` `SITUATION_UNANSWERED` cases | unchanged code path; if it regresses the fault is in 3.5's `_the_situation_the_person_chose` scope change |
| 4 | **P11's two guards go inert** when the root map is built from settled branches only (§C 3.5). | `tests/integration/test_p10_p11_live_seam.py`; `tests/p11/test_p11_pipeline.py::` the `TWO_SITUATIONS` cases (P11 untouched) | the life-grain binding in 3.5; rollback is the old two lines at `cli.py:17505-17514` |
| 5 | **A life spanning two schemas loses one schema's recipes** if drafting stays per branch. | `tests/test_cli_lives_drafts.py`; `test_p10_multi_life.py::test_each_life_is_split_by_its_own_recipe_and_by_no_other` | 3.4; without it the second schema's files sit at the life's root with no levels — visible, not lost |
| 6 | **Two roots wearing one life** until Phase 4. | §D's `count("Work") == 1` in 4.2's test | ship 3 and 4 in one PR |
| 7 | **`test_groups_of_different_categories_get_different_top_level_branches`** (`tests/test_cli.py:2187`, `xfail(strict=True)`) XPASSES: the claim (`law_practice` → Work) and the review (`hr` → Work) leave `Coursework`. | it fails the suite by design "the day per-category drafting lands" | take the marker off in 3.4's commit and keep the assertion; it is now the pin |
| 8 | **`Branch.schema` readers** (`cli.py:10986`, `16041`, `18177`, `18182`) and constructors (`tests/p6/test_p6_an_unsettled_branch_names_its_files_situations.py:35`) break at import or at runtime. | `tests/p6`, `tests/test_cli.py`, `tests/integration/test_template_levels_wiring.py` | 3.5 lists every line; `grep -n "\.schema\b" src/cli.py` must return nothing that is not `said().schema` |
| 9 | **The branch question stops being recorded** for a life branch (`candidate_situations=()`), and a person who answered `--answer situation:academic=...` last run has an answer at a scope that no longer exists (`branch:academic` → `branch:Education`). | `test_the_persons_answer_at_the_lifes_scope_settles_it`; `tests/integration/test_the_level_answer_is_written_down.py::test_the_run_still_does_not_ask_the_person_about_that_branch` | answers are `structural_answers` rows and stay readable; the run's closing screen prints the new scope. Say so in the commit body: an answer given under a kind label is not carried to the life label |
| 10 | **The Phase 1 grouping number falls.** Grouping runs BEFORE the partition is read (`draft_for_review` is after `_grouped_by_branch`), so P9's groups are unchanged; only the merged drafts' shape changes. | `tools/groundtruth/report.py` beside §D | if it moves, the change is in `_grouped_by_branch`'s vote, not in P9 |
| 11 | **`release_id` moves** and a tree frozen under the old library is compared against the new. | `freeze` writes `catalogue_release_id` (`pipeline.py:1013`); `tests/p10/test_p10_pipeline.py` | intended; the digest is the version |
| 12 | **A 12a violation ships unseen**: sixteen roots. | §D's `0 < len(life_roots) < 16` and `set(life_roots) <= set(lives_in_facts)` | there is no code path that emits a life no file reached; if the gate fails, `_grouped_by_branch` or a user label leaked |
| 13 | **Two branches share a label** — the scanned folder is named exactly as a life its files reach (`Education/` scanned untyped), and the label is an identity in five places (§B). | new check in `BranchPartition.__post_init__`: `raise ValueError` on a repeated label, pinned by one test beside `test_the_partition_refuses_a_file_in_two_places` | the person types `--label`; the refusal names the collision and says so |
| 14 | **The early return's deletion changes a typed single-kind run's work**, not its result: the reach loop now runs over every file. | `test_r37_single_branch_is_byte_identical` (same records), `tests/integration/test_scale_stress.py` (time) | the loop is O(files); if the stress test moves, the cost is `situation_fact_of` per file — read the slot once per run as `_situation_values` already does for values |

**Rollback for the whole phase:** every task is one commit on the existing seams; `git revert` in reverse order restores the kind partition, and the library rows' `life` key is inert under the reverted reader (`raw.get` on a key nothing reads). The rows can stay.

**What this draft does not claim.** It adds no level to any branch (`106`, "What this plan does not claim"). It does not build the add-a-life gesture (§E, the door). It does not ratify the 208-row mapping (§A). And it has not been run: every test above is written against signatures read today at the line numbers cited, and the first red run is where the lead finds what this draft got wrong about them.

---

# Phase 5 — The person's input and customisation system

> Draft for `planning/106-SORT-PLAN.md` Phase 5. Written 17 Sep 2026 from the code on
> `build/p6-p7-first-packages` at `19d39aa3`, the product design `00` with its
> amendments through 17 Sep, and plan `106`. Nothing here has been executed. Every
> `file.py:line` was read, not recalled. Aggregates only; nothing from the owner's
> corpus appears.

**Goal of the phase:** the person can say what they mean about their files and their
tree at the moment it matters, in a form the product keeps, and a re-run never
silently loses what they said.

**What this draft found that the brief did not say.** The person has **twenty-six**
input points today, not five (§B). `--structure` already lets them edit the tree as
an outline — rename, delete, add, declare a branch's situation (`cli.py:22517-22668`)
— so gap 2 is half wrong: the person *does* edit the tree; what they cannot do is
*move* a folder or rename a template-owned one, and nobody has told them why. Every
**fact-keyed** edit already survives a re-run (`--confirm`, `--reject`, `--rename`,
`--rename-level`, `--answer`, `--release`, `--file-held`, `--accept-groups`); what dies
is everything **node-keyed**: the outline's `[n]` markers (`cli.py:22537`), node-scoped
review actions, the per-version review-set gestures. Two of the three mid-run gates
already exist under other names (§C.2). And P10's own node-level `rename`/`ignore`
writer (`tree_design/store.py:604-632`) is reachable from no gesture at all — its one
caller is the pipeline's internal `_apply` (`tree_design/pipeline.py:1222`).

---

## A. The input model, stated plainly — the deal

This is the page the product owes the person. It belongs in the outline's header
(`structure_file.py:169-197`), which is the one place they read with nothing else in
front of them, and in `--help`.

> **What you are changing, and when.**
>
> The product reads your files and writes down what it believes about each one — the
> course it belongs to, the term, what kind of document it is, which of your lives it
> is part of. Those beliefs are *facts*, each one tied to the file it came from and to
> the evidence in that file. The folders are built from the facts: a folder exists
> because some of your files carry the value it is named by, and it is named by that
> value. **That is the deal: you correct what the product believes, and the folders
> follow.**
>
> So when you rename a folder in the outline, you are saying *"the value these files
> carry is called this"* (`--rename`, `cli.py:20325`). When you delete a folder, you
> are saying *"these files do not carry that value"* (`--reject`, `cli.py:20163`). When
> you add a folder and say which of your lives it is, you are declaring a life you
> hold (`--declare-role`, `questions/roles.py:363`). Every one of these is written as
> **your** fact, at the strength `user_confirmed`, which outranks anything a rule or a
> model says about that file (`facts/states.py:53-59`; `facts/supersede.py:272-276`
> refuses to let a weaker row take the pointer back; `facts/llm_seam.py:463-468`
> refuses to let a re-run overrule you). It is remembered by file and by value, not by
> the folder that happened to be on the screen, which is why it is still true after a
> re-run, a re-shaped tree, or a library update.
>
> **Why facts rather than folders.** If you renamed *a folder*, the product would have
> to guess which of the facts under it you meant, and on the next run — when a new file
> arrives and the folder is rebuilt — it would have nothing to attach your word to. A
> value is the thing that survives.
>
> **The two things that are not facts, and how you edit them.** Some names in the tree
> are the *library's* words, not your files' — the name of a level (*Course* vs
> *Class*) and, from Phase 3, the name of a life (*Education*). You rename those
> directly, and the rename is kept against the level's or the life's *meaning*
> (`--rename-level`, `tree_design/user_edits.py:52-64`; §F for lives), so it too
> survives.
>
> **What you cannot do, and why.** You cannot drag a folder under a different parent.
> A folder is *where the facts about the files under it put it* (`cli.py:22568-22571`);
> to move the files, say what is true of them. You cannot rename the top of a branch in
> the outline (`cli.py:22578-22583`) — today that name is a kind or your `--label`;
> from Phase 3 it is a life, and §F gives you its verbs.
>
> **When you are asked.** Three moments, each a screen the run stops at and a command
> you type back: after the files are read and grouped (*are these groups right?* —
> `--accept-groups`), after the tree is proposed and before any file is placed into it
> (*is this the structure?* — the outline, `--structure`; Phase 5 makes the run stop
> here), and after placement and before anything moves (*shall I?* — `--freeze`, then
> `--apply`). Nothing moves until the third. Held files are put to you separately,
> with two answers (`--file-held`, `--release`).
>
> **What happens to what you said.** Every answer is appended, never overwritten; you
> can see it (`--explain`, `--trail`), change it (say it again), or take it back
> (`--answer Q=revoke`). The product never re-asks a question you answered or skipped.

**Is facts-not-folders the right design?** Yes, for levels — and the argument is the
one the code already makes: a fact is keyed on the file and the value, and that key
survives every event a node id does not (`user_edits.py:44-64` states it for level
names; `questions/records.py:491-498` learned it the hard way for destinations, which
were node ids and "silently stopped meaning anything"). Where it is *wrong* is that the
person is never told, and that the one tree-level edit they need — the top of a
branch — has no gesture; Phase 3 turns that top into a life, and §F gives the life its
verbs. The design stands; the deal needs writing down, and one class of edit needs to
stop dying at re-run (§E).

---

## B. Every input point, today

"Survives" means: made on run N, still in force on run N+1 with nothing retyped.
Flags are defined at `cli.py:24024-24343`; appliers run in `main` at
`cli.py:24437-24720`, **before** `run`, so an answer takes effect on the run that
supplies it (`cli.py:24592-24594`).

| # | gesture | writes | table | state / basis | survives a re-run |
|---|---|---|---|---|---|
| 1 | `--answer Q=OPT\|skip\|revoke` (`cli.py:24077`) | one answer row superseding the live one, plus an `events` row (`cli.py:20475-20583`) | `structural_answers`, `events` | `confirmed`/`skipped`/`revoked` (`questions/vocabulary.py:232-236`) | **yes** — keyed `(question_id, scope)`; `record_question` is idempotent on re-ask (`questions/store.py:482-510`); a revoked answer reopens the question (`store.py:627-643`) |
| 2 | `--file-held FILE_ID` (`cli.py:24084`) | one move permission on the policy in force, and a `user` classification row `protected=True` where the file was not already protected (`cli.py:20590-20668`) | privacy policy at `PLAN_VERSION` (`"plan_0"`, `cli.py:4185`); classification store | basis `user`, `user_confirmed` | **yes** — the policy is carried forward; a user classification row is never retired by the rules (`cli.py:20643-20647`) |
| 3 | `--release FILE_ID` (`cli.py:24091`) | one `user` classification row, ordinary, superseding the hold (`cli.py:20671-20745`) | classification store | basis `user`, `user_confirmed` | **yes**; the cloud door opens on the next run by itself (`cli.py:20706-20709`); refused for a file nothing holds |
| 4 | `--describe-role NAME=WORDS` (`cli.py:24104`) | a `FREE_TEXT` declaration, scope `corpus` (`questions/roles.py:427-460`) | `structural_questions`/`structural_answers` | activates nothing by construction (`vocabulary.py:252-257`) | **yes**, keyed on the name |
| 5 | `--declare-role NAME=LAYOUT\|not_listed\|skip` (`cli.py:24113`) | a declaration choosing a schema (`roles.py:363-404`) | same | `confirmed`; activates that schema (`store.py:695-706`) | **yes**; the same name again supersedes |
| 6 | `--reject FILE:FIELD=VALUE` (`cli.py:24120`) | the standing fact → `rejected`, plus a correction event (`cli.py:20163-20244`; `facts/learning.py:229`) | `file_facts`, `events` | `rejected` (an exclusion, never ranked — `states.py:61-79`) | **yes, unless the file's bytes change** — keyed on `content_hash` (`learning.py:363-383`) |
| 7 | `--confirm FILE:FIELD=VALUE` (`cli.py:24127`) | a `user_confirmed` row superseding the proposal, same evidence, same cache key (`learning.py:385-455`) | `file_facts` | `user_confirmed`, origin `user_correction` | **yes, unless bytes change**; wins the slot outright (`supersede.py:374-377`) |
| 8 | `--rename FILE:FIELD=OLD>NEW` (`cli.py:24135`) | merges two value rows and confirms the survivor (`learning.py:456`; `cli.py:20325-20372`) | `values`, `file_facts` | `user_confirmed` | **yes** — the spelling reaches every later proposal via `confirmed_spellings` |
| 9 | `--rename-level SCHEMA:ROLE:FIELD=NAME` (`cli.py:24143`) | a `review_action` (canvas, `rename`) then one overlay row (`cli.py:20375-20463`; `user_edits.py:147-172`) | `review_actions`, `user_level_edits` | basis `user`, action `renamed` | **yes** — keyed on the vocabulary triple, applied at the end of routing (`routing.py:520`); an upgrade that loses the level reports it rather than dropping it (`user_edits.py:133-145`). Refused for a triple no run has shown (`review_gestures.py:401-408`) |
| 10 | `--structure FILE` (`cli.py:24188`) | **nothing itself** — becomes rows 1, 6, 8, 5 (`cli.py:24597-24617`) | — | — | **the file does not**: `[n]` is a position in one plan's walk and an outline stamped with an older `# plan:` is refused (`cli.py:22537-22545`; `structure_file.py:57-62`). The gestures it becomes do. |
| 11 | `--structure-out FILE` (`cli.py:24181`) | where the outline is written (`cli.py:24907, 25007`) | file on disk | — | rewritten every run |
| 12 | `--accept-groups` (`cli.py:24209`) | a bulk `review_action` and P9's acceptance at `PLAN_VERSION` for every draft of this run (`cli.py:11143-11240`, `16319-16324`) | `review_actions`, group acceptance | accepted, decided by the user | **yes, under the same `--label`** — a draft's id is content-addressed, `plan_0:<category>:<label>:<digest>` (`cli.py:10989`), so the same members re-draft to the same id and `group_state_as_of` finds the acceptance (`grouping/acceptance.py:290-303`); a different `--label` mints a different id and the accept has to be given again |
| 13 | `--send-set SET=AREA` (`cli.py:24218`) | a `review_action` and a placement for the set (`cli.py:19422-19513`) | `review_actions`, placement | — | **no, by design** — "it applies to the run that prints it, because a plan version's review sets are its own" (`cli.py:24222-24224`) |
| 14 | `--leave-set SET`, `--review-set SET` (`cli.py:24225, 24232`) | as 13; `--review-set` records a choice and applies nothing until site D's text is ratified (amendment 14) | same | — | **no, by design** (same sentence) |
| 15 | `--residual NAME`, `--residual-library ACTION:NAME=ARG`, `--define-residual NAME=DOES` (`cli.py:24156-24180`) | **nothing durable** — parsed into `residual_library_choices` in memory (`cli.py:5078`, no connection) and handed to the design (`cli.py:16188-16194`) | — | — | **no** — retyped every run. `enable-residual`/`disable-residual` are tree-edit actions with no writer (`store.py:114-117`) |
| 16 | `--situation ID`, `--label NAME` (`cli.py:24026, 24034`) | nothing; `--label` becomes the default branch's `display_label` for that version (`cli.py:15769`, `pipeline.py:667`) | — | — | **no** — no table holds either (`tree_design/schema.py` carries `display_label` per node and nothing else); the integration harness passes both on every run (`tests/integration/test_the_editable_structure.py:90-92`) |
| 17 | `--may-cross-folders` (`cli.py:24061`) | `plan_versions.cross_folder_moves` (`tree_design/schema.py:36`) | `plan_versions` | — | per version, retyped |
| 18 | `--enable-cloud` / `--disable-cloud` (`cli.py:24259, 24266`) | one consent row per source folder (`cli.py:24561-24573`; `database_agent/cloud_consent.py:176`) | cloud consent | — | **yes**, per folder; absence is refusal (`cli.py:24574-24579`) |
| 19 | `--show-protected` (`cli.py:24198`) | nothing; names instead of counts on this screen | — | — | n/a |
| 20 | `--stop-after gate\|facts` (`cli.py:24276`) | nothing; ends the run at a stage (`cli.py:15789-15791`, `18209-18213`, `19339-19345`) | — | — | n/a; refuses `--freeze`, `--apply`, `--accept-groups`, `--record` beside it (`cli.py:24403-24425`) |
| 21 | `--freeze` (`cli.py:24285`) | the version frozen and its bundle (`tree_design/freeze.py:419`; `frozen_trees`) | `plan_versions`, `frozen_trees` | frozen = approved (amendment of 9 Sep) | **yes** — it *is* the durable plan |
| 22 | `--apply BRANCH`, `--apply-everything`, `--undo …` (`cli.py:24290-24309`) | moves and their undo records, off the frozen plan, no pipeline (`cli.py:23643`) | mutation records | — | **yes** |
| 23 | `--explain Q`, `--trail FILE`, `--list-situations`, `--list-residuals` (`cli.py:24240-24258, 24075`) | nothing; read-only | — | — | n/a |
| 24 | `--record NAME`, `--replay BUNDLE` (`cli.py:24310, 24343`) | a sealed bundle; a replay of one | bundles | — | yes; not an edit |
| 25 | `--semantic-model DIR`, `--entity-model DIR`, `--also-read`, `--could-live-in`, `--user`, `--database` (`cli.py:24040-24074, 24325-24342`) | run configuration; nothing durable | — | — | retyped |
| 26 | the outline's own four edits — rename a line, delete a line, add `NAME situation: ID`, `situation: ID` under a top folder (`structure_file.py:210-297`) | rows 8, 6, 5, 1 respectively (`cli.py:22599-22668`) | as those rows | as those rows | as those rows — **but the file itself dies (row 10)** |

Two things the table makes visible. **There is no `input()` anywhere in `src/`**
(`106` "four things wrong" #4): every gesture is a flag on the *next* invocation, and
the product's own precedent for a mid-run stop is stop-print-return (`cli.py:19339-
19345`, `19731-19735`). **The only writer of a person's word about a single file's
*situation* is the branch-scoped `--answer situation:<branch>=…`** — a per-file
`user_confirmed` situation row has a reader (`llm_seam.py:463-468`) and no writer, and
the run's own resolver reads the pass object, not the store (`cli.py:17650-17669`,
`17671-17745`).

---

## C. The gaps, ranked

**C.1 — A node-addressed edit dies at the next run.** Every fresh run mints
`node_{run_token}_{n}` and sets `origin_node_id=node_id` (`cli.py:16076`;
`materialise.py:690, 717`; `pipeline.py:664, 694`; `candidates.py:236, 253`;
`residuals.py:325-330`; `store.py:450-459`). Lineage is carried only by `open_draft`
(`store.py:326-358`), i.e. between a version and a draft opened *from* it — never
between run N and run N+1. So `diff_versions` (`diff.py:52-54`), `reproject`
(`versions.py:107-112`), `learned_preferences_still_applicable` (`versions.py:474-481`)
and `apply_review_action`'s target lookup (`store.py:604-609`) all see a re-run as
"everything removed, everything added", and the outline refuses its own file
(`cli.py:22537-2545`). *Seam:* the five mint sites above; the origin becomes a key.
*Smallest change:* §E — no schema change, no reader changes. Phase 5 Task 5.1.

**C.2 — There is no stop between the tree and placement.** `run_production_p8_p11`
goes `design_tree` → `approve_plan` → `set_privacy_policy` → `build_destination_index`
→ `run_corpus` in one call (`production.py:1028-1061`), and placement spends a model
call per file (constitution; `00` 2026-09-05 "every placement goes through the
model"). The groups gate exists: a run without `--accept-groups` prints the drafts and
stops before design (`cli.py:19700-19735`, "run the same command again with
--accept-groups"). The placement gate exists: `--freeze` is the approval and moves
nothing (`cli.py:24285-24289`). The **tree** gate — amendment 2 of 14 Sep's "shown to
the person as something they edit … *before any file is placed under it*" — does not.
*Seam:* `production.py:1028` (after `design_tree`, before `placement_inputs`), and
`STOP_AFTER_STAGES` (`cli.py:15791`). *Smallest change:* one stage name, one boolean
through the composition, the outline printed from the design. Task 5.3. **Do not add
`groups` or `placement` stage names**: they would be second spellings of gestures that
exist, and `84` §6 refuses two answers to one question.

**C.3 — The person cannot correct one file's situation.** Amendment 5 of 15 Sep
promises *"the person corrects it in one structure edit"*; amendment 11 makes the
situation the sort's input. The only writer is branch-scoped (`--answer
situation:<branch>=…`, read by `_situation_for`, `branch_situation.py:309-330`). Per
file there is nothing: `--confirm FILE:situation=X` would need a standing row at that
value (`learning.py:415-422`) — true for the judge's first choice, and for an
alternative it would land on `situation_alternative`, which the partition does not
read. *Seam:* `record_the_situation`'s skip (`llm_seam.py:463-468`) is the reader; the
level stage's settled arm (`cli.py:8910`) is per schema and needs a per-file twin.
Task 5.4.

**C.4 — Amendment 12a's five verbs have no mechanism.** No `life` exists yet (Phase 3
builds `life_of(situation)` on the applicability row). The overlay shape exists —
`user_level_edits` (`tree_design/schema.py:125-138`) is a vocabulary-keyed, user-basis
overlay applied at the end of routing — and is the model to copy. *Seam:* Phase 3's
`partition_by_branch` key. Task 5.5, **sequenced after Phase 3's gate**.

**C.5 — The deal is unwritten.** The outline header (`structure_file.py:178-193`)
tells the person *how* to edit and not *what an edit is*; `_print_structure`
(`cli.py:22447-22468`) says "rename a folder" where the product will record "rename
the value". The refusal texts are right (`cli.py:22568-22583`) but arrive after the
person has already edited. *Smallest change:* §A's text in the header. Task 5.2.

**C.6 — `--label`, `--situation`, the residual choices are retyped every run** (rows
15, 16). Real, small, and not Phase 5's: `--situation` is optional since 11 Sep and
the run reads the corpus; `--label` becomes a life name under Phase 3 and §F's
`rename`; the residual library gets its writer under Phase 7's `98`/`99` work.
Recorded here so it is not lost.

**Not a gap:** rows 13-14 are per-version by the design's own sentence; row 9's
refusal of an unshown triple is §8.7 working.

---

## D. Phase 5 — the task list

**Order:** 5.1 (identity) → 5.2 (the outline survives; the deal in the header) → 5.3
(the tree gate) → 5.4 (per-file situation) → 5.5 (lives, after Phase 3). Each task:
test, watch it fail, implement, watch it pass, commit. Every command below runs with
`GRAPH_AGENT_NO_DOTENV=1 nice -n 15 python3 -m pytest … -p no:randomly -q`, one
session at a time, never beside a corpus run.

### Task 5.1: A node's origin is its key, so a re-run reads as the same tree

**Files:** Create `src/tree_design/node_key.py` · Modify `src/tree_design/pipeline.py`
(`_top_level_node`, line 637-698), `src/tree_design/materialise.py` (`_project`, line
690-717), `src/tree_design/candidates.py` (line 236-256), `src/tree_design/residuals.py`
(line 325-332), `src/tree_design/store.py` (`_write_overlap_answer` line 450-459;
`write_node` line 171) · Modify `tests/p10/test_p10_materialise.py:486-503` · Test:
`tests/p10/test_p10_node_key.py` (new).

**Read first.** `store.py:8-11` — "if node ids turn out to be stable across versions,
`origin_node_id` becomes `node_id` and nothing else changes". `diff.py:52`,
`versions.py:103-112`, `versions.py:451-457`, `store.py:604-609`: every cross-version
reader already keys on `origin_node_id`. `cli._node_claim` (`cli.py:22334-22341`):
what a folder is *named by* is the last `ExpectedValue` on it.

- [ ] **Step 1: Write the failing test.**

```python
# tests/p10/test_p10_node_key.py
"""SPEC open question 5, answered: a node's `origin_node_id` is its KEY.

`store.py`'s docstring offered the reversible move -- "if node ids turn out to be
stable across versions, `origin_node_id` becomes `node_id` and nothing else
changes". This is the other half: `node_id` stays minted per version and
`origin_node_id` stops being the fresh mint's own id and becomes what the node IS,
spelled from what it already carries. Every reader that compares versions by
origin (`diff.diff_versions`, `placement.versions.reproject`,
`learned_preferences_still_applicable`, `store.apply_review_action`) then works
across RUNS with no change of its own -- which is the whole of why this is the
smallest change and not a new column.

`106` Phase 5's gate: an edit survives a re-run. It cannot while two runs over
one corpus disagree about which node is which.
"""
from __future__ import annotations

import pytest

from tree_design.node_key import (
    branch_key, general_key, level_key, protected_key, residual_key,
)
from tree_design.records import PlanVersion
from tree_design.schema import create_tree_schema
from tree_design.store import DuplicateNodeKey, write_node, write_plan_version

from p10.test_p10_materialise import (
    ACCEPTED, ALWAYS_ORDINARY, NO_CONTEXT, ONE_CLASS, PROTECTED_CLASSES,
    _candidate, _ids, _parent, seeded,  # noqa: F401
)
from tree_design.fixtures import CREATED_AT, SELECTION_ID, _node
from tree_design.materialise import materialise_branch, project_branch_nodes


def test_two_runs_over_one_branch_mint_different_ids_and_the_same_origins(seeded):
    """THE GATE. SABOTAGE: put `origin_node_id=node_id` back at
    `materialise.py:717` -- every origin below differs between the two runs, and
    `diff_versions` reads a re-run as everything removed and everything added."""
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("subject", "subject"), ("work_type", "work_type")),
        branch_node_id="n_academics",
        members=seeded.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
    first = project_branch_nodes(
        evidence, ACCEPTED, parent=_parent(), plan_version_id="plan_1",
        mint_node_id=_ids(), handling_class_for=ALWAYS_ORDINARY,
        template_context_for=NO_CONTEXT)
    counter = iter(range(5000, 9000))
    second = project_branch_nodes(
        evidence, ACCEPTED, parent=_parent(), plan_version_id="plan_2",
        mint_node_id=lambda: f"other_{next(counter)}",
        handling_class_for=ALWAYS_ORDINARY, template_context_for=NO_CONTEXT)
    assert [n.node_id for n in first] != [n.node_id for n in second]
    assert [n.origin_node_id for n in first] == [n.origin_node_id for n in second]
    assert all(n.origin_node_id != n.node_id for n in first)


def test_a_level_key_is_the_parents_key_and_the_value_the_folder_is_named_by():
    """The same pair `cli._node_claim` reads: a folder named by `subject =
    PHYS1401` under the coursework branch has one spelling wherever it appears."""
    root = branch_key(display_label="Coursework", existing_path=None)
    assert root == "branch:Coursework"
    assert level_key(root, field="subject", value="PHYS1401", role="subject_anchor") \
        == "branch:Coursework/subject=PHYS1401"
    # A template-local level has no P6 field (`materialise.py:697-700`), so its
    # role names it -- and the two cannot collide, because a role is never a
    # field of the same name in one recipe.
    assert level_key(root, field=None, value="Matter 12", role="matter_number") \
        == "branch:Coursework/matter_number=Matter 12"


def test_an_adopted_folder_is_keyed_by_the_path_that_was_observed():
    """`pipeline.py:661-663`: an adopted card's `subject_id` IS the directory.
    Two runs that adopt the same folder must agree, and two folders with one name
    in two places must not."""
    assert branch_key(display_label="PHYS1401", existing_path="Uni/PHYS1401") \
        == "existing:Uni/PHYS1401"
    assert branch_key(display_label="PHYS1401", existing_path="Old/PHYS1401") \
        != branch_key(display_label="PHYS1401", existing_path="Uni/PHYS1401")


def test_the_other_three_kinds_of_node_have_their_own_prefix():
    assert residual_key("Reading Inbox") == "residual:Reading Inbox"
    assert protected_key("Keychain") == "protected:Keychain"
    assert general_key("branch:Coursework") == "branch:Coursework/general"


def test_two_nodes_with_one_key_in_one_version_are_refused_at_the_write():
    """C4's shape (`user_edits.py:242-250`): one question with two answers has
    none. SABOTAGE: drop the guard -- `reproject` then matches a pending move to
    whichever of the two rows sorts first, silently."""
    import sqlite3
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_tree_schema(conn)
    write_plan_version(conn, PlanVersion(
        plan_version_id="plan_1", predecessor_id=None, state="draft",
        created_at=CREATED_AT, cross_folder_moves=False,
        selection_id=SELECTION_ID))
    write_node(conn, _node("n_1", "Coursework", origin="branch:Coursework"))
    # The SAME row again is a rewrite, not a clash: `apply_review_action` writes
    # an edited node back under its own id (`store.py:632`).
    write_node(conn, _node("n_1", "Course work", origin="branch:Coursework"))
    with pytest.raises(DuplicateNodeKey):
        write_node(conn, _node("n_2", "Coursework", ordinal=1,
                               origin="branch:Coursework"))
```

- [ ] **Step 2: Run it.** `… tests/p10/test_p10_node_key.py` →
`ModuleNotFoundError: No module named 'tree_design.node_key'`. Any other failure
means the fixture import is wrong; fix it before touching `src/`.

- [ ] **Step 3: Write the module.**

```python
# src/tree_design/node_key.py
"""§8.8's node identity ACROSS RUNS -- SPEC open question 5, answered.

`store.py`'s docstring named the reversible move: "if node ids turn out to be
stable across versions, `origin_node_id` becomes `node_id` and nothing else
changes". This module is the other half. `node_id` is still minted per version;
`origin_node_id` is no longer the fresh mint's own id but the node's KEY, spelled
from what the node already carries. Two runs that build the same folder write
the same origin, and every reader that already compares versions by origin --
`diff.diff_versions`, `placement.versions.reproject`,
`placement.versions.learned_preferences_still_applicable`,
`store.apply_review_action` -- starts working across runs with no change.

WHAT A KEY IS MADE OF, and nothing else:
* a proposed top-level branch   `branch:` + the card's display label. Today that
  is the schema id or the person's `--label` (`pipeline.py:667`); under `106`
  Phase 3 it is the LIFE, which is the one moment this key changes and Phase 3
  says so. It is the label and not the group ids because a group is re-drafted
  per run and a label is what the person recognises.
* an adopted existing folder    `existing:` + the observed path. Two folders
  with one name in two places are two folders.
* a level a value produced      the parent's key + `/` + `field=value`, the same
  pair `cli._node_claim` reads to say what a folder is NAMED BY.
* a template-local level        the parent's key + `/` + `role=label` -- it has
  no P6 field (`materialise.py:697-700`), so its role names it.
* a residual area               `residual:` + the template name.
* a protected area              `protected:` + its display label.
* the scoped General            the parent's key + `/general`.

Path-shaped rather than `canonical_json`, deliberately: this string is what a
person may one day read beside a folder, and equality is all the readers need.
A `/` inside a value cannot make two different chains equal, because the field
name precedes every value and a field never contains one.
"""
from __future__ import annotations

BRANCH_PREFIX: str = "branch:"
EXISTING_PREFIX: str = "existing:"
RESIDUAL_PREFIX: str = "residual:"
PROTECTED_PREFIX: str = "protected:"
GENERAL: str = "general"
SEPARATOR: str = "/"


def branch_key(*, display_label: str, existing_path: str | None) -> str:
    """A top-level card's key: the observed path for an adopted folder, the label
    for a proposal."""
    if existing_path is not None:
        return EXISTING_PREFIX + existing_path
    return BRANCH_PREFIX + display_label


def level_key(parent_key: str, *, field: str | None, value: str,
              role: str) -> str:
    """One level beneath `parent_key`, named by `field=value` -- or by
    `role=label` for a template-local level with no field."""
    return f"{parent_key}{SEPARATOR}{field if field is not None else role}={value}"


def residual_key(template_name: str) -> str:
    return RESIDUAL_PREFIX + template_name


def protected_key(display_label: str) -> str:
    return PROTECTED_PREFIX + display_label


def general_key(parent_key: str) -> str:
    return f"{parent_key}{SEPARATOR}{GENERAL}"
```

- [ ] **Step 4: Thread it through the five mint sites.** Each is one argument.

`materialise.py:717` — in `_project`, the node built from a level value:

```python
            origin_node_id=level_key(parent.origin_node_id, field=level.field_ref,
                                     value=value, role=level.dimension_role),
```

`pipeline.py:694` — in `_top_level_node`, after `adopted` is computed at line 664:

```python
        origin_node_id=branch_key(
            display_label=candidate.display_label,
            existing_path=candidate.subject_id if adopted else None))
```

`candidates.py:253` — the protected-area node: `origin_node_id=protected_key(area.display_label),`.

`residuals.py:330` — the fresh residual node: `origin_node_id=residual_key(choice.template_name),`. Line 298 (a residual template mapped onto an *existing* node) already carries `existing.origin_node_id` and is untouched.

`store.py:459` — the scoped General in `_write_overlap_answer`: `origin_node_id=general_key(parent.origin_node_id),`.

- [ ] **Step 5: The guard.** In `store.py`, beside `FrozenVersionImmutable`:

```python
class DuplicateNodeKey(ValueError):
    """Two nodes in one version claim one origin. C4's shape: one question with
    two answers has none, and `reproject` would otherwise match a pending move to
    whichever row sorts first."""
```

and as the first statement of `write_node` after the frozen check (`store.py:172-177`):

```python
    clash = conn.execute(
        "SELECT node_id FROM tree_nodes WHERE plan_version_id = ? "
        "AND origin_node_id = ? AND node_id <> ?",
        (node.plan_version_id, node.origin_node_id, node.node_id)).fetchone()
    if clash is not None:
        raise DuplicateNodeKey(
            f"{node.origin_node_id!r} already names node {clash['node_id']!r} in "
            f"version {node.plan_version_id!r}; a second node under one key would "
            "make every cross-version reader guess which one an edit meant")
```

`open_draft` (`store.py:346-357`) copies origins one-to-one into a new version, so it
cannot trip this; `apply_review_action` writes an edited node back under its own
`node_id` (`store.py:632`), which the `node_id <> ?` clause admits.

- [ ] **Step 6: Retire the pin that asserted the old answer.**
`tests/p10/test_p10_materialise.py:486-503`, `test_a_projected_node_is_its_own_lineage_origin`,
pins `origin_node_id == node_id`. Replace its first assertion with the new fact and
rename it:

```python
def test_a_projected_node_carries_its_key_as_origin_and_a_fresh_id(seeded):
    """OQ5 is CLOSED (`106` Phase 5): ids are minted per version and the origin is
    the node's key, so a re-run reads as the same tree. `Node.__post_init__` still
    rejects an empty `origin_node_id`, so it is bound at construction."""
    ...
    assert all(n.origin_node_id != n.node_id for n in nodes)
    assert all(n.origin_node_id.startswith("n_academics/") for n in nodes)
```

(the parent fixture's origin is `"n_academics"`, `test_p10_materialise.py:73`).

- [ ] **Step 7: Run** `tests/p10/test_p10_node_key.py`, then `tests/p10`, then
`tests/p11 tests/p13 tests/p15` (the cross-version readers). A red test that pins
`origin_node_id == node_id` anywhere is the old answer; update it to the new one, never
the code. A red test about a *duplicate* origin is a real collision — read which two
nodes share a key before deciding; the likely one is two accepted groups drafted under
one label, and the answer there is the label, not the guard.

- [ ] **Step 8: Commit.** `feat(106 Phase 5.1): a node's origin is its key, so a re-run reads as the same tree (SPEC OQ5 closed)`

### Task 5.2: The outline survives a re-run, and its header states the deal

**Files:** Modify `src/cli.py` (`structure_edits`, line 22517-22547) ·
`src/structure_file.py` (`render`, line 169-197) · Test:
`tests/integration/test_the_editable_structure.py` (extend, beside `_edited`).

**Read first.** `cli.py:22531-22545`: the `# plan:` refusal. `structure_file.py:57-62`
says why the marker is a position. With 5.1, every node in `written_from` has an
`origin_node_id` that the current version's node for the same folder shares — so the
marker can be resolved against the plan it was written from and the edit carried by
origin. The stamp stays; the refusal becomes a resolution.

- [ ] **Step 1: Write the failing test** at the end of the integration file:

```python
def test_an_outline_from_the_previous_run_still_applies_after_a_re_run(proposed):
    """`106` Phase 5's gate, in the person's terms: they edit the outline, life
    happens, they run the command once more without it, and only THEN hand the
    edit back. Before 5.1 and this task the third run refused the file by name
    (`cli.py:22537`); the person's edit was lost unless they re-did it.

    SABOTAGE: resolve the markers against the CURRENT version instead of the one
    the file names -- the rename lands on whichever folder now stands at that
    position, and this test's label assertion holds only by luck of ordering.
    """
    marker, was = _a_folder_named_by_a_value(proposed)
    edited = _edited(proposed, lambda lines: [
        line.replace(f"{was}  [{marker}]", f"Renamed by hand  [{marker}]")
        for line in lines])
    # A run in between, with no structure handed back: a new plan version.
    code, said = _once(proposed)
    assert code == 0, said
    code, said = _once(proposed, "--structure", edited)
    assert code == 0, said
    assert "Renamed by hand" in _labels(proposed), said
    assert was not in _labels(proposed), said
```

- [ ] **Step 2: Run it.** Expect the refusal text "this outline was written from
proposal" in `said` and `code == 2`.

- [ ] **Step 3: Resolve instead of refuse.** Replace `cli.py:22536-22548` with:

```python
    # THE PROPOSAL THIS FILE WAS WRITTEN FROM. A marker is a POSITION in one
    # plan's walk, so it is resolved against THAT plan -- and carried to the
    # current one by `origin_node_id`, which `106` Phase 5.1 made the node's
    # key. An outline from a run the person has since re-run therefore still
    # says what they meant; a folder the current plan no longer builds is named
    # in the refusal below rather than silently skipped.
    written_from = structure_plan_in(text) or plan_version
    then = {marker: node for marker, _depth, node in _outline_walk(
        nodes_for_version(conn, written_from))}
    now_by_origin = {node.origin_node_id: node
                     for node in nodes_for_version(conn, plan_version)}
    nodes: dict[int, object] = {}
    gone: list[str] = []
    for marker, node in then.items():
        carried = now_by_origin.get(node.origin_node_id)
        if carried is None:
            gone.append(node.display_label)
        else:
            nodes[marker] = carried
    if gone:
        raise StructureGestures(
            f"this outline was written from proposal {written_from!r}, and the "
            f"current plan {plan_version!r} no longer builds "
            f"{', '.join(repr(label) for label in sorted(gone))}. Run the "
            f"command without `--structure` to get the current outline and make "
            f"your edits in that; nothing from this file was applied.")
    # WHAT THE FILE WAS COMPARED AGAINST IS WHAT THE FILE WAS WRITTEN FROM.
    # `labels` and `parents` come from the THEN walk: a line the person left
    # alone must produce no edit (`structure_file.py:278-279`), and if the run in
    # between renamed or re-parented a folder, comparing their untouched line
    # against the CURRENT label would read it as a rename back, or a move.
    # `nodes` -- the carried, current rows -- is used only for what an edit
    # ACTS ON: the claim (`claim_of`) and the files under it (`under`).
    labels = {marker: node.display_label for marker, node in then.items()}
    parents = {marker: None for marker in then}
    place = {node.node_id: marker for marker, node in then.items()}
    for marker, node in then.items():
        parents[marker] = place.get(node.parent_node_id)
```

The existing `parents`/`place` lines at `cli.py:22549-22553` are replaced by the four
above, and `structure_read(text, labels={marker: node.display_label …})` at
`cli.py:22591-22593` is handed this `labels`. **Limit of the test in Step 1:** run 2
changes nothing, so it cannot catch a then/now mix-up; the comment above is what
guards it, and Phase 4's fold — which *will* rename roots between runs — is where a
second case belongs.

- [ ] **Step 4: The deal in the header.** In `structure_file.render`
(`structure_file.py:178-193`), after the `# Edit this file …` line, the four rules are
rewritten so each says what is *recorded*:

```python
        "# Rename a folder: change the words in front of its [n]. What is",
        "# recorded is that the VALUE these files carry is called this, so",
        "# it is still true after the next run, and on every file that carries it.",
        "# Leave a folder out: delete its whole line. What is recorded is that",
        "# its files do NOT carry that value.",
        f"# Add a folder: write a new line under the one it belongs under, "
        f"indented two spaces further, ending `{SITUATION_PREFIX} <id>`. What is",
        "# recorded is a life you hold; the folder is built from your files.",
        f"# Say which of your lives a branch is: put `{SITUATION_PREFIX} <id>` "
        f"on a line of its own under it.",
        "#",
        "# A folder cannot be moved under another: it sits where the facts",
        "# about its files put it. To move the files, say what is true of them.",
        "# The top of a branch is a life; its own commands are --life.",
```

The pin at `tests/integration/test_the_editable_structure.py` that reads the header
(search `"# The [n] is how the product finds the folder again"`) is unchanged; add one
assertion in the same test that `"What is recorded is that the VALUE"` is in the file.

- [ ] **Step 5: Run** the integration file, then `tests/test_cli.py`. **Step 6:
Commit.** `feat(106 Phase 5.2): an edited outline still applies after a re-run, and its header says what an edit records`

### Task 5.3: `--stop-after tree` — the run stops at the proposal, before any file is placed

**Files:** Modify `src/production.py` (`ProductionRun`, line 880-894;
`run_production_p8_p11`, line 970-1061) · `src/cli.py` (`STOP_AFTER_STAGES`, line
15789-15791; `run` signature, line 15864; the composition call, line 19347-19352; the
outline, line 22380-22435 and 24905-25010; the refusal at 24403-24425; a new
`_print_stopped_after_tree` beside `_print_stopped_after_facts`, line 13683) · Modify
`tests/test_cli_stop_after_facts.py:63` · Test: `tests/test_cli_stop_after_tree.py` (new).

**Read first.** `production.py:1028-1061`: after `design_tree`, `approve_plan` and
`set_privacy_policy` are cheap writes *about the version*; `placement_inputs`,
`build_destination_index` and `run_corpus` are the placement. `cli.py:22405-22412`:
the outline's counts and its `situation:` line both come from
`result.placement.decisions`. `cli.py:19706-19708`: `memberships_for_group` is how the
run already counts a group's files without placement. `cli.py:24403-24425`: `--accept-
groups` is refused beside any `--stop-after` — for `tree` it is *required*, because a
run with nothing accepted stops before the tree anyway (`cli.py:19731`;
`production.py:1003` is where the accepted ids enter the design).

- [ ] **Step 1: Write the failing test.**

```python
# tests/test_cli_stop_after_tree.py
"""`--stop-after tree`: propose the structure, write the outline, place nothing.

`00` amendment 2 of 14 Sep, the owner's flow: the tree is "shown to the person as
something they edit ... BEFORE any file is placed under it". Until `106` Phase 5
the product could not stop there: `run_production_p8_p11` designs and places in
one call, and placement spends a model call per file on a tree the person is
about to edit.

The groups gate already exists (a run without `--accept-groups` stops before the
tree, `cli.py:19731`) and so does the placement gate (`--freeze`). This is the one
between them. It REQUIRES `--accept-groups`, because a tree is built from accepted
groups and nothing else (`production.py:1003`).
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402
from placement.store import decisions_for_plan  # noqa: E402
from tree_design.store import latest_plan_version, nodes_for_version  # noqa: E402

from test_cli_stop_after_facts import _corpus  # noqa: E402


def _stopped_at_the_tree(tmp_path, *extra):
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Papers", "--user", "jy",
                     "--database", str(database), "--accept-groups",
                     "--stop-after", cli.STOP_AFTER_TREE, *extra], out=out)
    return code, out.getvalue(), database


def test_the_stages_are_the_gate_the_facts_and_the_tree_in_the_runs_own_order():
    assert cli.STOP_AFTER_STAGES == (
        cli.STOP_AFTER_GATE, cli.STOP_AFTER_FACTS, cli.STOP_AFTER_TREE)


def test_a_run_stopped_at_the_tree_writes_the_tree_and_places_nothing(tmp_path):
    """SABOTAGE: return from `run_production_p8_p11` AFTER `run_corpus` instead of
    before it -- the count of decisions below becomes non-zero, and the person's
    model budget was spent on a tree they had not yet read."""
    code, printed, database = _stopped_at_the_tree(tmp_path)
    assert code == 0, printed
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        version = latest_plan_version(conn)
        assert version is not None, printed
        assert nodes_for_version(conn, version), "no tree was written"
        assert not list(decisions_for_plan(conn, plan_version=version)), (
            "the run placed files it was told to stop before placing")
    finally:
        conn.close()


def test_a_run_stopped_at_the_tree_says_so_and_writes_the_outline(tmp_path):
    """What tells a person their run ended early is that it SAYS so
    (`_print_stopped_after_facts`'s rule), and the outline is what they were
    stopped for. SABOTAGE: print the outline and not the sentence -- a screen
    that stops after an outline is indistinguishable from one that crashed
    before placement."""
    code, printed, database = _stopped_at_the_tree(tmp_path)
    assert code == 0, printed
    assert "Stopped at the proposed structure" in printed, printed
    assert "The structure being proposed, and yours to change:" in printed, printed
    outline = database.parent / cli.STRUCTURE_FILENAME
    assert outline.exists(), printed
    assert "# plan:" in outline.read_text(encoding="utf-8")


def test_the_tree_stop_still_refuses_a_freeze_beside_it(tmp_path):
    """`cli.py:24403-24425`'s rule is kept for the gestures that need placement;
    only `--accept-groups` is let through, because this stage needs it."""
    code, printed, _ = _stopped_at_the_tree(tmp_path, "--freeze")
    assert code == 2, printed
    assert "two things at once" in printed, printed
```

- [ ] **Step 2: Run it.** `AttributeError: module 'cli' has no attribute 'STOP_AFTER_TREE'`.

- [ ] **Step 3: The stage name**, `cli.py:15789-15791`:

```python
STOP_AFTER_GATE: str = "gate"
STOP_AFTER_FACTS: str = "facts"
#: `106` Phase 5. The run ends with the proposed tree written and the outline on
#: the screen, before a single placement call is spent. `00` amendment 2 of 14
#: Sep: the structure is edited "before any file is placed under it".
STOP_AFTER_TREE: str = "tree"
STOP_AFTER_STAGES: tuple[str, ...] = (STOP_AFTER_GATE, STOP_AFTER_FACTS,
                                      STOP_AFTER_TREE)
```

and the pin at `tests/test_cli_stop_after_facts.py:63` becomes the three-member tuple.

- [ ] **Step 4: The composition.** `ProductionRun.placement` (`production.py:890`)
becomes `placement: CorpusResult | None` with the comment
`#: None only under --stop-after tree: the tree was designed and nothing was placed.`
and `destinations: tuple[Any, ...]` stays, empty. In `run_production_p8_p11` add the
keyword `stop_after_design: bool = False` and, immediately after
`decisions.set_privacy_policy(conn, plan_version)` (`production.py:1031`):

```python
    if stop_after_design:
        # `106` Phase 5: the tree is the proposal, and it is shown before a
        # placement call is spent on it. The version is complete -- approved
        # acceptance and policy are about the version, not about placement --
        # so `--structure` on the next run reads it exactly as it reads any other.
        return ProductionRun(p1_p7=p1_p7, grouping=grouping, tree=tree,
                             destinations=(), placement=None, evaluation=None)
```

In `cli.run`, the call at `cli.py:19347-19352` gains
`stop_after_design=(stop_after == STOP_AFTER_TREE)`, **and `run` returns right
after it**:

```python
    if stop_after == STOP_AFTER_TREE:
        # `106` Phase 5.3. Everything below this line reads `result.placement`
        # (`residual_sets` at 19485-19516, the set gestures at 19542) and a
        # stopped run has none. The `situations` mailbox is already full: it is
        # written per roster file at `cli.py:19144`, inside `downstream`, before
        # the composition is called -- verify that loop covers EVERY roster file
        # and not only the answered ones before relying on it for the outline.
        return result
```

The early returns at `cli.py:19339-19345` are untouched: `tree` passes them because
it is neither. This is one early return plus an audit, not one boolean: grep
`result.placement` and `result.destinations` between `cli.py:24830` and `25010` —
today `24897` and `25005` — and guard each with `result.placement is not None`.

- [ ] **Step 5: The outline without placement.** `structure_rows`
(`cli.py:22380-22435`) computes `holds` from `result.placement.decisions`, and its
docstring's rule is that it "composes an outline and holds no vocabulary" and no
connection (`cli.py:22395-22398`). Keep that rule: `holds` becomes an argument, and
`main` computes it either way. In `structure_rows`, replace the `holds` loop with the
parameter `holds: Mapping[str, Sequence[str]]`; in `main`, before the call at
`cli.py:24908`:

```python
    holds: dict[str, list[str]] = {}
    if result.placement is not None:
        for decision in result.placement.decisions:
            if decision.destination is not None:
                holds.setdefault(decision.destination.node_id, []).extend(
                    _files_of(decision))
    else:
        # `--stop-after tree`: nothing is placed yet, so a top folder is
        # described by the files of the groups it was built from -- the same
        # reader `accept_drafted_groups` counts with (`cli.py:19706`). Levels
        # beneath it say nothing about counts, because saying which files a
        # LEVEL holds is placement's answer and this run was told not to give it.
        for node in result.tree.tree.nodes:
            if node.parent_node_id is None:
                holds[node.node_id] = [
                    membership.file_id
                    for group_id in node.associated_group_ids
                    for membership in memberships_for_group(conn, group_id)
                    if membership.decision == INCLUDED]
    outline = structure_rows(result, holds=holds, situations=situations,
                             words_of=situation_words)
```

The `situation:` line and `note` at `cli.py:22421-22427` then work unchanged, because
`_the_one_situation_under` reads the `situations` mailbox, which `run` fills from
`_the_situation_this_file_is_under` (`cli.py:19144`) before any placement.

- [ ] **Step 6: The screen.** Beside `_print_stopped_after_facts` (`cli.py:13683`):

```python
def _print_stopped_after_tree(result: ProductionRun, *, out) -> None:
    """The last thing a `--stop-after tree` run says. Said, not inferred: a
    screen that ends after an outline is otherwise indistinguishable from one
    that crashed before placement (`_print_stopped_after_facts`'s rule)."""
    # `PROTECTED` joins the `tree_design.vocabulary` import at `cli.py:527`;
    # a protected area is marked and counted, never a folder proposed.
    folders = sum(1 for node in result.tree.tree.nodes
                  if node.node_type != PROTECTED)
    print("", file=out)
    print(_wrapped(
        f"Stopped at the proposed structure, as --stop-after {STOP_AFTER_TREE} "
        f"asked: {folders} {'folder is' if folders == 1 else 'folders are'} "
        f"proposed above and written to the file beside the database, and no "
        f"file was placed into any of them -- no model was asked where a file "
        f"goes, no plan was frozen, and nothing moved. Edit the file and hand it "
        f"back with --structure, or run again without --stop-after to see where "
        f"each file would go.", indent=""), file=out)
```

In `main`, where the report is printed after `run` returns (`cli.py:24905-25010`), the
`report(...)` call is skipped when `result.placement is None` and replaced by
`_print_structure(outline, path=structure_path, out=out)` followed by
`_print_stopped_after_tree(result, out=out)`; the `structure_render` write at
`cli.py:25007` runs in both cases (it already does).

- [ ] **Step 7: The refusal list.** `cli.py:24403-24425`: `--accept-groups` is refused
beside every stage but this one:

```python
            ("--accept-groups", args.accept_groups
                                 and args.stop_after != STOP_AFTER_TREE),
```

and the help text for `--stop-after` (`cli.py:24276-24284`) gains one sentence:
`"`tree` proposes the folders, writes the outline you edit, and stops before any file is placed; it needs --accept-groups, because the folders are built from the groups."`

- [ ] **Step 8: Run** `tests/test_cli_stop_after_tree.py`, `tests/test_cli_stop_after_facts.py`,
`tests/test_cli.py`, `tests/integration/test_the_editable_structure.py`. **Step 9:
Commit.** `feat(106 Phase 5.3): --stop-after tree -- the structure is shown and edited before a placement call is spent`

### Task 5.4: `--situation-of FILE=SITUATION` — the person's word about one file's situation

**Files:** Modify `src/facts/learning.py` (new `assert_situation`, after `rename_claim`,
line 456) · `src/cli.py` (new `apply_situations_of` beside `apply_confirmations`, line
20280; a per-file settled arm in `ask_the_situation`, line 9600-9622; the flag beside
`--confirm`, line 24127; the applier in `main` beside `--confirm`, line 24693) · Test:
`tests/p6/test_p6_situation_of.py` (new), `tests/test_cli_situation_of.py` (new).

**Read first.** `llm_seam.py:463-468`: the reader that already refuses to overrule a
`USER_CONFIRMED` situation row. `learning.py:385-455`: `confirm_claim` requires a
standing row at that value — a file the judge gave the wrong first choice *and* the
wrong alternatives has none, and an alternative would be confirmed on the wrong field.
`cli.py:9601-9603, 8910`: `settled_situation_of` is per **schema**. `cli.py:17650-
17669`: the run reads the situation off the pass, so the pass must carry the person's
word or the branch will never see it.

- [ ] **Step 1: Write the failing P6 test.**

```python
# tests/p6/test_p6_situation_of.py
"""`00` amendment 5 of 15 Sep: "the person corrects it in one structure edit".

The reader existed and nothing wrote to it. `record_the_situation` skips a
`USER_CONFIRMED` row rather than superseding it (`llm_seam.py:463-468`), so a
person's word about one file's situation would outlive every re-run -- if
anything could put one there. `--confirm` cannot: it needs a standing row at that
value (`learning.py:415-422`), and the judge's alternative lands on
`situation_alternative`, which the partition does not read.
"""
from __future__ import annotations

import pytest

from facts.file_facts import USER_CORRECTION
from facts.learning import assert_situation
from facts.llm_seam import SITUATION_FIELD, record_the_situation
from facts.states import USER_CONFIRMED
from facts.supersede import preferred_fact

# `p6_conn` is `tests/p6/conftest.py`'s; `subject_file` is the llm-seam suite's own
# one-file, one-observation fixture (`test_p6_llm_seam.py:109-117`), imported by
# name the way the integration suite imports `dark_level_stage`.
from test_p6_llm_seam import subject_file  # noqa: F401

T0 = "2026-09-17T00:00:00Z"


def _value_of(conn, row):
    return conn.execute('select canonical_value from "values" where value_id = ?',
                        (row["value_id"],)).fetchone()[0]


def test_the_persons_situation_is_written_user_confirmed_and_preferred(
        p6_conn, subject_file):
    file_id, content_hash, key = subject_file
    record_the_situation(p6_conn, file_id=file_id, content_hash=content_hash,
                         situation="academic.coursework", alternatives=(),
                         evidence_refs=(key,), cache_key="call_1")
    assert_situation(p6_conn, file_id=file_id, content_hash=content_hash,
                     situation="academic.teaching", user_id="t", observed_at=T0)
    row = preferred_fact(p6_conn, file_id=file_id, field_key=SITUATION_FIELD)
    assert row["reliability_state"] == USER_CONFIRMED
    assert row["origin"] == USER_CORRECTION
    assert _value_of(p6_conn, row) == "academic.teaching"


def test_a_re_run_does_not_take_the_persons_situation_back(p6_conn, subject_file):
    """SABOTAGE: write the person's row `llm_supported` instead of
    `user_confirmed` -- the next `record_the_situation` supersedes it as it
    supersedes any model row, and the person's correction lasts one run."""
    file_id, content_hash, key = subject_file
    assert_situation(p6_conn, file_id=file_id, content_hash=content_hash,
                     situation="academic.teaching", user_id="t", observed_at=T0)
    record_the_situation(p6_conn, file_id=file_id, content_hash=content_hash,
                         situation="academic.coursework", alternatives=(),
                         evidence_refs=(key,), cache_key="call_2")
    row = preferred_fact(p6_conn, file_id=file_id, field_key=SITUATION_FIELD)
    assert _value_of(p6_conn, row) == "academic.teaching"


def test_saying_it_again_is_the_same_word_not_a_second_one(p6_conn, subject_file):
    file_id, content_hash, _key = subject_file
    first = assert_situation(p6_conn, file_id=file_id, content_hash=content_hash,
                             situation="academic.teaching", user_id="t",
                             observed_at=T0)
    again = assert_situation(p6_conn, file_id=file_id, content_hash=content_hash,
                             situation="academic.teaching", user_id="t",
                             observed_at="2026-09-17T00:00:01Z")
    assert first == again


def test_changing_their_mind_retires_the_earlier_word_and_the_slot_still_reads(
        p6_conn, subject_file):
    """THE TRACE THAT BROKE THE FIRST DRAFT OF THIS WRITER. Run 1: the person says
    X (U1). Run 2: the judge writes M beside it and leaves U1 alone
    (`llm_seam.py:463-468`). Run 3: the person says Y. If the writer retired M
    and left U1, the slot holds two live `user_confirmed` rows with two values,
    `preferred_of_slot` finds no pointer, and the person's own correction makes
    the file's situation unreadable. SABOTAGE: skip `user_confirmed` rows in the
    retirement loop -- `preferred_fact` below answers `None`."""
    file_id, content_hash, key = subject_file
    first = assert_situation(p6_conn, file_id=file_id, content_hash=content_hash,
                             situation="academic.teaching", user_id="t",
                             observed_at=T0)
    record_the_situation(p6_conn, file_id=file_id, content_hash=content_hash,
                         situation="academic.coursework", alternatives=(),
                         evidence_refs=(key,), cache_key="call_3")
    second = assert_situation(p6_conn, file_id=file_id, content_hash=content_hash,
                              situation="academic.k12", user_id="t",
                              observed_at="2026-09-17T00:00:02Z")
    row = preferred_fact(p6_conn, file_id=file_id, field_key=SITUATION_FIELD)
    assert row is not None and row["fact_id"] == second
    old = p6_conn.execute("SELECT superseded_by FROM file_facts WHERE fact_id = ?",
                          (first,)).fetchone()
    assert old["superseded_by"] == second
```

- [ ] **Step 2: Run it.** `ImportError: cannot import name 'assert_situation'`.

- [ ] **Step 3: The writer**, in `facts/learning.py` after `rename_claim`:

```python
def assert_situation(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                     situation: str, user_id: str, observed_at: str) -> str:
    """The person's own word about which situation ONE file is part of.

    `00` amendment 5 of 15 Sep: where the judge names the plainest member of a
    kind, "the person corrects it in one structure edit". This is that edit's
    writer. It is NOT `confirm_claim`: a confirmation needs a standing proposal
    at that value, and the case this exists for is the file whose right answer
    the judge never listed -- or listed as an alternative, which sits on
    `situation_alternative` and is not the slot the partition reads.

    `USER_CONFIRMED` at origin `USER_CORRECTION`, superseding every standing row
    that is not already the person's, with the reason kept (§8.2). Idempotent on
    the same value: `write_fact` hands back the existing row's id, and saying it
    again is the same word. `record_the_situation` then leaves this row alone
    (`llm_seam.py:463-468`), which is what makes it outlive a re-run.

    No evidence ref: the person's word is not a reading of the file (`confirm_
    claim`'s rule), and `cache_key` names the gesture rather than a call.
    """
    value_id = ensure_value(conn, field_key=SITUATION_FIELD,
                            canonical_value=situation, first_evidence_ref=None,
                            origin=VALUE_ORIGINS[1])
    # THE ONE ROW THIS MAY RETIRE IS THE PERSON'S OWN EARLIER WORD. Model rows
    # are left standing: `preferred_of_slot` keeps only the confirmed rows the
    # moment one exists (`supersede.py:374-377`), so they are already outranked
    # and retiring them here would be a second rule for the pointer -- and
    # retiring two of them by one new row is the fork `SupersedeMerge` refuses
    # (`supersede.py:277-281`). What MUST be retired is a prior `user_confirmed`
    # row naming another value: two live confirmed rows with two values leave
    # the slot with no pointer and `preferred_fact` answering `None`, which is
    # the person's own correction making their file unreadable.
    theirs = [row for row in conn.execute(
        "SELECT fact_id, value_id FROM file_facts "
        "WHERE file_id = ? AND content_hash = ? AND field_key = ? "
        "AND reliability_state = ? AND superseded_by IS NULL",
        (file_id, content_hash, SITUATION_FIELD, USER_CONFIRMED))]
    if any(row["value_id"] == value_id for row in theirs):
        return next(row["fact_id"] for row in theirs if row["value_id"] == value_id)
    written = write_fact(
        conn, file_id=file_id, content_hash=content_hash,
        field_key=SITUATION_FIELD, value_id=value_id,
        reliability_state=USER_CONFIRMED, origin=USER_CORRECTION,
        evidence_refs=(), cache_key=f"situation-of:{file_id}:{situation}",
        active=True)
    for row in theirs:
        supersede_fact(conn, old_fact_id=row["fact_id"], new_fact_id=written,
                       reason=f"the person said {file_id!r} is {situation} "
                              f"(--situation-of), replacing their earlier word")
    return written
```

`supersede_fact`'s `PreferredNeverReverses` (`supersede.py:272-276`) admits this write:
both rows are `user_confirmed`. If `theirs` ever holds two rows — it cannot after this
function has run once, but a database written before it could — the second
`supersede_fact` raises `SupersedeMerge`; chain them (`old → written`, then the other
`old → written` is refused) by superseding the older into the newer first, which is the
"chain, which P1 does represent" `supersede.py:196-198` names.

with `SITUATION_FIELD` imported from `facts.llm_seam`, `VALUE_ORIGINS` and
`ensure_value` from `facts.values`, `write_fact`/`USER_CORRECTION` from
`facts.file_facts`, `supersede_fact` from `facts.supersede`. If `learning.py` importing
`llm_seam` is a cycle at load, move `SITUATION_FIELD`'s spelling to `facts/fields.py`
and have both import it — one home, as `states.py:93-101` did for the same reason.

- [ ] **Step 4: The flag and applier.** `cli.py`, beside `--confirm` (line 24127):

```python
    parser.add_argument(
        "--situation-of", action="append", default=[], metavar="FILE=SITUATION",
        help="say which situation one file is part of, e.g. --situation-of "
             "'week 3.pdf=academic.teaching'. This is your word about THAT file: "
             "it outranks what the model said, it is not asked again, and the "
             "folder the file goes to follows from it on this run. Name the "
             "situation as `--list-situations` prints it. Can be given more than "
             "once.")
```

Beside `apply_confirmations` (line 20280):

```python
class SituationOfRefused(NotConfigured):
    """`--situation-of` named a file this plan has not recorded, or a situation
    the library does not carry."""


def apply_situations_of(conn: sqlite3.Connection, catalogue: TemplateCatalogue,
                        situations_of: Sequence[str], *, user_id: str,
                        observed_at: str) -> None:
    """`--situation-of FILE=SITUATION`: the person's word about one file.

    The file is found by `_named_file`'s rule (every row P1 has not retired, and
    two of one name are refused with both paths); the situation by
    `_validate_situation`, which is the one place a typed situation is checked
    and offers "Did you mean". The write is P6's (`facts.learning.
    assert_situation`); this turns one string into three words.
    """
    for raw in situations_of:
        filename, sep, situation = raw.partition("=")
        if not sep or not filename or not situation:
            raise SituationOfRefused(
                f"{raw!r} is not a situation. The form is "
                "`--situation-of <file>=<situation>`, for example "
                "`--situation-of 'week 3.pdf=academic.teaching'`.")
        _validate_situation(catalogue, situation)
        row = _named_file(conn, filename, "--situation-of")
        assert_situation(conn, file_id=row["file_id"],
                         content_hash=row["content_hash"], situation=situation,
                         user_id=user_id, observed_at=observed_at)
```

and in `main`, after the `--rename` block (`cli.py:24697-24700`):

```python
        if args.situation_of:
            _bootstrap(conn)
            apply_situations_of(conn, catalogue, args.situation_of,
                                user_id=args.user, observed_at=now())
```

(`catalogue` is already in scope at `cli.py:24356`; a `SituationOfRefused` is a
`NotConfigured` and lands in the handler at `cli.py:24818` like every other refusal.)

- [ ] **Step 5: The pass reads it.** In `ask_the_situation`, before the per-file loop
that sets `situations[file_id] = answered.situation` (`cli.py:9600-9622`), read the
corpus's confirmed situations **once** — `106` Task 1.1's rule, one query for the whole
run, and the read `read_surface.preferred_in_field` exists for (`read_surface.py:400-
411`, "reads one field's slots once"):

```python
    # THE PERSON'S OWN WORD ABOUT A FILE (`--situation-of`), read once for the
    # corpus. `preferred_in_field` asks `preferred_of_slot` per slot, so a
    # confirmed row wins here exactly as it wins for every other reader.
    theirs = {file_id: row for file_id, row in preferred_in_field(
                  conn, field_key=SITUATION_FIELD).items()
              if row["reliability_state"] == USER_CONFIRMED}
```

and at the top of the per-file body, before `_ask_which_situation_of_the_kind`:

```python
        if file_id in theirs:
            # Not asked: `104` §17.9, the model's answer is a refinement of the
            # person's and never a replacement, so a call whose answer is
            # outranked before it is made is a call spent to be discarded.
            situations[file_id] = value_of[theirs[file_id]["value_id"]]
            not_asked_their_situation += 1
            continue
```

`value_of` is the run's value-id map (`_situation_values`, `cli.py:16081`); pass it
into `ask_the_situation` the way `situations_of` is passed (`cli.py:18237-18267`),
rather than reaching for the closure.

- [ ] **Step 6: The CLI test**, `tests/test_cli_situation_of.py`, in
`test_cli_stop_after_facts.py`'s harness: one `--stop-after facts` run over `_corpus`;
then the same command with `--situation-of 'PHYS 1401 homework 3.txt=academic.teaching'`;
assert the run's `situation` row for that file reads `academic.teaching` at
`user_confirmed` through `preferred_fact`, and that a third plain run leaves it so.
SABOTAGE note in the docstring: drop Step 5 and the fact is written and the branch
never sees it — the store test stays green while the product ignores the person.

- [ ] **Step 7: Run** `tests/p6/test_p6_situation_of.py`, `tests/p6`,
`tests/test_cli_situation_of.py`, `tests/integration/test_the_level_answer_is_written_down.py`.
**Step 8: Commit.** `feat(106 Phase 5.4): --situation-of -- the person's word about one file's situation, written where the re-run already refuses to overrule it`

### Task 5.5: The person's lives — rename, merge, split, remove, add (after Phase 3)

**Depends on Phase 3's gate:** `life_of(situation)` exists on the applicability row and
`partition_by_branch` keys on it. Written now so Phase 3 builds the seam this needs;
executed only after Phase 3's number is in `104`.

**Files:** Create `src/tree_design/user_lives.py` · Modify `src/tree_design/schema.py`
(one table, added to `P10_TABLES` line 18-25 and `TREE_DDL`) · `src/branch_situation.py`
(`partition_by_branch`, the key — Phase 3's line) · `src/cli.py` (two flags beside
`--rename-level`; appliers beside `apply_level_relabels`, line 20375) · Test:
`tests/p10/test_p10_user_lives.py` (new).

**Read first.** `user_edits.py:1-44`: the overlay is keyed on the vocabulary, holds
only user-basis rows, one key one answer, applied at the *end* of routing. This copies
it exactly. Amendment 12a(iii): the judge's menu reads the library; the overlay is
applied only in the partition, after the judge's answer is a fact — closed to the
model structurally, not by prose.

- [ ] **Step 1: Write the failing test.**

```python
# tests/p10/test_p10_user_lives.py
"""`00` amendment 12a(ii): the person may rename, merge, split, remove and ADD a
life, without a library change. 12a(iii): closed to the MODEL, open to the PERSON.

One overlay, the shape of `user_level_edits` (`64` §3: keyed on the VOCABULARY,
never on a node or a version), read in one place -- the partition key -- and
never by the judge's menu.
"""
from __future__ import annotations

import sqlite3

import pytest

from tree_design.schema import create_tree_schema
from tree_design.user_lives import (
    LifeEditRefused, life_overlay, record_life_edit,
)

T0 = "2026-09-17T00:00:00Z"


@pytest.fixture
def conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_tree_schema(conn)
    return conn


def _library(situation: str) -> str | None:
    """Phase 3's `life_of`, stubbed: what the LIBRARY says a situation's life is."""
    return {"academic.coursework": "education", "academic.k12": "education",
            "academic.teaching": "teaching"}.get(situation)


def test_with_no_edits_the_overlay_answers_exactly_what_the_library_does(conn):
    overlay = life_overlay(conn)
    assert overlay.life_for("academic.coursework", library=_library) == "education"
    assert overlay.label_of("education") is None


def test_rename_changes_the_name_and_not_the_key(conn):
    record_life_edit(conn, action="rename", life="education",
                     display_label="School", user_id="t", recorded_at=T0)
    overlay = life_overlay(conn)
    assert overlay.life_for("academic.coursework", library=_library) == "education"
    assert overlay.label_of("education") == "School"


def test_merge_sends_one_lifes_situations_to_another(conn):
    record_life_edit(conn, action="merge", life="teaching", into="education",
                     user_id="t", recorded_at=T0)
    assert life_overlay(conn).life_for("academic.teaching", library=_library) \
        == "education"


def test_split_is_one_situation_pointed_at_a_life_of_the_persons_own(conn):
    """Add a life the library never imagined, then point one situation at it.
    SABOTAGE: let `life_for` read the library AFTER the overlay -- the split
    is silently undone on every run, and the person's life stays empty."""
    record_life_edit(conn, action="add", life="school-days",
                     display_label="School Days", user_id="t", recorded_at=T0)
    record_life_edit(conn, action="assign", situation="academic.k12",
                     into="school-days", user_id="t", recorded_at=T0)
    overlay = life_overlay(conn)
    assert overlay.life_for("academic.k12", library=_library) == "school-days"
    assert overlay.life_for("academic.coursework", library=_library) == "education"
    assert overlay.label_of("school-days") == "School Days"


def test_remove_leaves_a_situation_with_no_life_rather_than_a_guessed_one(conn):
    """Amendment 13: a file no branch can hold goes to `98`, and is offered a
    home. A removed life's files are exactly that, and the partition's `None`
    is how they get there. SABOTAGE: fall back to the library's life -- the
    removal is a no-op the person was told succeeded."""
    record_life_edit(conn, action="remove", life="teaching", user_id="t",
                     recorded_at=T0)
    assert life_overlay(conn).life_for("academic.teaching", library=_library) is None


def test_the_overlay_never_reaches_the_judges_menu():
    """12a(iii), pinned the way `supersede.py:151-152` pins `preferred` out of
    the strength paths: by parsing the source. The judge's menu is built where
    `schema_names` is (`cli.py:18237`) and in `model_facts`; neither may import
    this module. SABOTAGE: add `from tree_design.user_lives import …` to
    `model_facts.py` to "let the judge see the person's lives" -- an invented
    life becomes an invented folder, which is `00` amendment 7's whole discipline."""
    import ast
    from pathlib import Path
    src = Path(__file__).resolve().parents[2] / "src"
    for module in ("model_facts.py", "facts/llm_seam.py"):
        tree = ast.parse((src / module).read_text(encoding="utf-8"))
        imported = {node.module for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom)}
        assert "tree_design.user_lives" not in imported, module


def test_an_add_that_collides_with_a_library_life_is_refused(conn):
    with pytest.raises(LifeEditRefused):
        record_life_edit(conn, action="add", life="education",
                         display_label="Education", user_id="t", recorded_at=T0,
                         library_lives=("education", "teaching"))


def test_a_merge_into_a_life_nobody_has_is_refused(conn):
    with pytest.raises(LifeEditRefused):
        record_life_edit(conn, action="merge", life="teaching", into="band",
                         user_id="t", recorded_at=T0,
                         library_lives=("education", "teaching"))
```

- [ ] **Step 2: Run it.** `ModuleNotFoundError: tree_design.user_lives`.

- [ ] **Step 3: The table**, appended to `TREE_DDL` and to `P10_TABLES`:

```sql
-- `106` Phase 5.5, `00` amendment 12a(ii). The person's edits to their LIVES,
-- the shape of `user_level_edits` above and for its reasons: keyed on the
-- vocabulary (a life id, a situation id), never on a node or a version; user
-- basis only; one key, one answer. `add` rows are the lives the library never
-- imagined. 12a(iii): read by the partition and by nothing that builds a
-- model's menu.
CREATE TABLE IF NOT EXISTS user_life_edits (
    subject_kind   TEXT NOT NULL CHECK (subject_kind IN ('life', 'situation')),
    subject        TEXT NOT NULL,
    action         TEXT NOT NULL
                   CHECK (action IN ('add', 'rename', 'merge', 'remove', 'assign')),
    into_life      TEXT,
    display_label  TEXT,
    basis          TEXT NOT NULL CHECK (basis = 'user'),
    user_id        TEXT NOT NULL,
    recorded_at    TEXT NOT NULL,
    PRIMARY KEY (subject_kind, subject, action)
);
```

The primary key includes `action` so a life can be both renamed and, later, merged
without the rename being lost: `label_of` still answers for a life that has been
merged away, which is what lets the screen say *"Teaching (now in Education)"*.

- [ ] **Step 4: The module.**

```python
# src/tree_design/user_lives.py
"""The person's own edits to their lives (`00` amendment 12a), kept where
re-derivation cannot reach them. `user_edits.py`'s overlay, one level up.

Five verbs, one table, one reader. `record_life_edit` writes; `life_overlay`
reads once per run; `LifeOverlay.life_for` is called by the partition key and by
nothing else. It deliberately has no method that LISTS lives: 12a(iii) keeps the
menu closed to the model, and a reader that cannot enumerate cannot be handed
to a menu builder by accident.

The library's answer is the argument, not the import: `life_for(situation,
library=life_of)` so this module holds no catalogue and the partition passes
the one it already has.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from tree_design.vocabulary import BASIS_USER

ADD, RENAME, MERGE, REMOVE, ASSIGN = "add", "rename", "merge", "remove", "assign"
LIFE_ACTIONS: tuple[str, ...] = (ADD, RENAME, MERGE, REMOVE, ASSIGN)


class LifeEditRefused(RuntimeError):
    """An edit that names a life nobody has, or invents one somebody has."""


@dataclass(frozen=True)
class LifeOverlay:
    added: frozenset[str]
    labels: dict[str, str] = field(default_factory=dict)
    merged_into: dict[str, str] = field(default_factory=dict)
    removed: frozenset[str] = frozenset()
    assigned: dict[str, str] = field(default_factory=dict)

    def life_for(self, situation: str, *,
                 library: Callable[[str], str | None]) -> str | None:
        """The life this situation's files go under: the person's assignment,
        else the library's -- then merges followed, removals honoured."""
        life = self.assigned.get(situation) or library(situation)
        seen: set[str] = set()
        while life is not None and life in self.merged_into and life not in seen:
            seen.add(life)
            life = self.merged_into[life]
        if life in self.removed:
            return None
        return life

    def label_of(self, life: str) -> str | None:
        return self.labels.get(life)


def life_overlay(conn: sqlite3.Connection) -> LifeOverlay:
    rows = conn.execute("SELECT * FROM user_life_edits "
                        "ORDER BY subject_kind, subject, action").fetchall()
    added, labels, merged, removed, assigned = set(), {}, {}, set(), {}
    for row in rows:
        if row["action"] == ADD:
            added.add(row["subject"]); labels[row["subject"]] = row["display_label"]
        elif row["action"] == RENAME:
            labels[row["subject"]] = row["display_label"]
        elif row["action"] == MERGE:
            merged[row["subject"]] = row["into_life"]
        elif row["action"] == REMOVE:
            removed.add(row["subject"])
        elif row["action"] == ASSIGN:
            assigned[row["subject"]] = row["into_life"]
    return LifeOverlay(added=frozenset(added), labels=labels, merged_into=merged,
                       removed=frozenset(removed), assigned=assigned)


def record_life_edit(conn: sqlite3.Connection, *, action: str, user_id: str,
                     recorded_at: str, life: str | None = None,
                     situation: str | None = None, into: str | None = None,
                     display_label: str | None = None,
                     library_lives: Sequence[str] = ()) -> None:
    """One verb. `library_lives` is what the release carries, passed in so an
    `add` cannot shadow one and a `merge`/`assign` cannot point at nothing."""
    if action not in LIFE_ACTIONS:
        raise LifeEditRefused(f"{action!r} is not one of {LIFE_ACTIONS}")
    known = set(library_lives) | life_overlay(conn).added
    if action == ADD:
        if not life or not display_label:
            raise LifeEditRefused("`add` needs a life id and what to call it")
        if life in library_lives:
            raise LifeEditRefused(
                f"{life!r} is a life this library already carries; rename it "
                "instead, or add one under another name")
    elif action in (MERGE, ASSIGN):
        if into not in known:
            raise LifeEditRefused(
                f"{into!r} is not a life you have; add it first with "
                "`--life add:<id>=<name>`")
    if action in (RENAME, MERGE, REMOVE) and life not in known:
        raise LifeEditRefused(f"{life!r} is not a life you have")
    if action == ASSIGN and not situation:
        raise LifeEditRefused("`assign` names a situation")
    conn.execute(
        "INSERT OR REPLACE INTO user_life_edits (subject_kind, subject, action, "
        "into_life, display_label, basis, user_id, recorded_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("situation" if action == ASSIGN else "life",
         situation if action == ASSIGN else life, action, into, display_label,
         BASIS_USER, user_id, recorded_at))
    conn.commit()
```

- [ ] **Step 5: The partition reads it.** At Phase 3's key in `partition_by_branch`
(`branch_situation.py`, where `life_of(situation)` will be read), the call becomes
`overlay.life_for(situation, library=life_of)`, with `overlay = life_overlay(conn)`
read once at the top of the function; a `None` here is the amendment 13 case and the
file joins the `98` set the way an unsettled file does today. The root's
`display_label` becomes `overlay.label_of(life) or library_label(life)`. The judge's
menu (`cli.py:18237`, `schema_names`) is not touched, and
`test_the_overlay_never_answers_for_the_judges_menu` is what keeps it so.

- [ ] **Step 6: The flags**, beside `--rename-level` (`cli.py:24143`), in
`--residual-library`'s `ACTION:NAME=ARG` shape (`cli.py:24163`):

```python
    parser.add_argument(
        "--life", action="append", default=[], metavar="ACTION:LIFE[=ARG]",
        help="change one of your lives -- the folders at the top of the tree. "
             "`add:<id>=<name>` adds one the product never imagined (a band, a "
             "congregation); `rename:<id>=<name>` calls it something else; "
             "`merge:<id>=<other>` folds it into another; `remove:<id>` takes it "
             "out, and its files are offered a home under 98 Review and "
             "Unsorted. Your word outlives the run and every library update. "
             "Can be given more than once.")
    parser.add_argument(
        "--life-of", action="append", default=[], metavar="SITUATION=LIFE",
        help="say which of your lives a situation belongs to, e.g. --life-of "
             "academic.k12=school-days. This is how a life is split: add the "
             "new one, then point the situations that belong there at it. For "
             "one file rather than a situation, --situation-of.")
```

with `apply_life_edits(conn, args.life, args.life_of, library_lives=…, user_id, recorded_at)`
beside `apply_level_relabels`, parsing exactly as `_parse_library_actions`
(`cli.py:11723`) does and calling `record_life_edit` once per string; refusals are
`LifeEditRefused` re-raised as `NotConfigured` so `main` prints them as every other
refusal (`cli.py:24818`).

- [ ] **Step 7: Run** `tests/p10/test_p10_user_lives.py`, `tests/p10`,
`tests/test_branch_situation.py`. **Step 8: Commit.** `feat(106 Phase 5.5 × 00 12a): the person's five verbs over their lives, one overlay keyed on the vocabulary`

**Phase 5 gate:** `tests/p10/test_p10_node_key.py`'s first test green (same origins
across runs); the integration test of 5.2 green (an outline from run N applies on run
N+2); `--stop-after tree` writes a tree and zero placement decisions; `--situation-of`
survives a plain re-run; after Phase 3, the five verbs green. Then the chunked suite on
a quiet machine.

---

## E. Stable node identity — SPEC open question 5, answered

**The stable key** is the node's *claim*, spelled from what the node already carries
(§D Task 5.1, `node_key.py`): the branch's identity at the root (`existing:` + path
for an adopted folder, `branch:` + label for a proposal — the life, after Phase 3),
then one `field=value` per level, which is exactly the pair `cli._node_claim`
(`cli.py:22334-22341`) already reads to say what a folder is named by, and the chain
`questions/records.py:491-498` already chose for `chooses_destination` after node ids
failed it. `node_id` stays minted per version; **`origin_node_id` becomes the key.**
That is the move `store.py:8-11` reserved as reversible, and it is the smallest one
because every reader that compares versions already compares origins:
`diff.py:52-54`, `versions.py:107-112`, `versions.py:474-481`, `store.py:604-609`.
No reader changes. No column is added.

**What happens when the thing it named no longer exists.** The record is *kept and
reported, never deleted and never applied to something else* — the rule
`learned_preferences_still_applicable` states (`versions.py:446-449`: "a rejection of a
node that no longer exists is still a true fact … it is simply not applied") and
`UnappliedUserEdit` implements for levels (`user_edits.py:133-145`). Concretely: an
outline naming a folder the current plan does not build is refused by the folder's
name with nothing applied (Task 5.2 Step 3); a suppression or a pending move against
a vanished origin stays on disk and re-applies the day the key reappears — which it
now can, because the key is the claim and a claim recurs.

**What happens when two versions disagree.** Two cases, and they are different.
*Two nodes in one version claim one key:* refused at the write (`DuplicateNodeKey`,
Task 5.1 Step 5) — C4's shape, one question with two answers has none. *Two edits, one
older and one newer, name one key:* the person's newer word wins and the older is
superseded with the reason, which is what every user store here already does
(`user_level_edits` is `INSERT OR REPLACE` on its key, `user_edits.py:147-172`;
`structural_answers` supersede by id, `store.py:530-557`); a model-side re-derivation
never wins against either (`64` §2, `user_edits.py:4-9`). *A version written before
5.1 and one after:* the old version's origins are its old fresh ids, so a draft opened
*from* it carries them (`open_draft`, `store.py:346-357`) and the two lineages simply
never meet; nothing is backfilled.

**The migration.** None to the schema: `origin_node_id` exists, is `NOT NULL`, is
indexed (`tree_design/schema.py:43-47, 73-74`). The one-line docstring at
`store.py:8-11` is rewritten to say OQ5 is closed and how. The `DuplicateNodeKey`
guard is a check in the writer rather than a `UNIQUE` index, for a stated reason: a
unique index would be created on every existing database at `_bootstrap`, and whether
any pre-5.1 version already holds two rows with one origin has not been measured —
`residuals.py:282-298` deliberately re-uses an existing node's `node_id` *and* its
origin (it is a rewrite of that node as a residual area), and a guard that excludes
the same `node_id` admits that case; a unique index would too, but the guard says why. If the lead
wants the index, measure `SELECT plan_version_id, origin_node_id, COUNT(*) FROM
tree_nodes GROUP BY 1, 2 HAVING COUNT(*) > 1` on `run12.sqlite` first (read-only,
aggregate), then add `CREATE UNIQUE INDEX IF NOT EXISTS tree_nodes_one_key_per_version
ON tree_nodes (plan_version_id, origin_node_id)` to `TREE_DDL` — one line, in a
separate commit, after the number is in `104`.

**The one thing this does not do.** It does not make the outline's `[n]` a stable
handle — `[n]` stays a position, readable by a person, and Task 5.2 resolves it against
the plan the file names. Printing the key beside each line was considered and
rejected: `branch:academic/subject=PHYS1401/work_type=Homework` is not something a
person should have to leave alone in a file they are editing.

---

## F. Amendment 12a's five verbs, for lives

**The rule that shapes all five.** After Phase 3 a file's life is a function of its
situation: `life_of(situation)` on the applicability row, read per file from the
`situation` fact (amendment 12; `106` Phase 3). The judge chooses a situation from the
library (amendment 1 of 14 Sep); the life follows. So the person's verbs act on two
things and never on a folder: the **vocabulary of lives** (names, existence) and the
**mapping** situation → life. Both are user-basis rows in one overlay
(`user_life_edits`, Task 5.5), keyed on a life id or a situation id — the vocabulary,
never a node or a version (`64` §3) — and applied in exactly one place, the partition
key. The judge's menu is built from the library and reads the overlay never; the
overlay has no method that lists lives, so it *cannot* be handed to a menu builder
(Task 5.5 test 6). That is 12a(iii) as structure, not as prose.

A life that has no situation pointing at it and no file under it is not built —
12a(i), and today's rule one level down (`materialise.py:94`, levels build only where
facts divide). An empty added life is reported on the screen as *"added and empty;
point a situation at it with `--life-of`, or a file with `--situation-of`"* and
produces no folder.

| verb | what the person types | what is written | how the next run reads it |
|---|---|---|---|
| **rename** | `--life rename:education=School` | `user_life_edits (life, education, rename, display_label=School)` | the root node for the life is labelled `overlay.label_of("education")`; the key (`branch:education`, §E) is unchanged, so every edit under it survives the rename |
| **merge** | `--life merge:teaching=education` | `(life, teaching, merge, into_life=education)` | `life_for` follows `merged_into` after the library's answer; every situation whose life was `teaching` partitions under `education`; the `teaching` root is not built; the screen prints *"Teaching (now in Education)"* once |
| **split** | `--life add:school-days=School Days` then `--life-of academic.k12=school-days` | `(life, school-days, add, display_label)` and `(situation, academic.k12, assign, into_life=school-days)` | `assigned` is consulted *before* the library, so `academic.k12` partitions under `school-days` and `academic.coursework` stays under `education`. For one file rather than one situation, `--situation-of FILE=academic.k12` (Task 5.4) — the file's own `user_confirmed` situation, which the partition reads per file |
| **remove** | `--life remove:vehicles` | `(life, vehicles, remove)` | `life_for` answers `None` for its situations; those files have no branch and join `98 Review and Unsorted`'s *deferred decisions* set (amendment 13), where per-file control (amendment 14, site D) offers them a home. The screen names the two ways back: `--life merge:vehicles=<other>` or re-run without the removal. Removal is never a silent fallback to the library's life — that would be a no-op the person was told succeeded |
| **add** | `--life add:band=The Band` | `(life, band, add, display_label=The Band)`; refused if `band` is a library life | it exists as a destination for `--life-of` and `--situation-of`; it is built only when something points at it (12a(i)); the model never sees it (12a(iii)) — a file the judge puts in `academic.coursework` lands in the band only because the *person* said `--situation-of` or `--life-of`, and that word is `user_confirmed`, which outranks the judge (`states.py:53-59`) |

**Why `--life-of` is per situation and not per folder.** The reference's "split" —
*Education* into *School Days* and *University* — is a statement about which
situations belong where, and a situation is the unit the sort already keys on. A
per-folder split would have to guess which situations the folder's files carry; a
per-situation one says it. The per-file case is a different sentence and has its own
gesture (Task 5.4), which is the same distinction `--rename-level` (a level's meaning)
and `--rename` (a file's value) already draw.

**What survives.** Every row is keyed on a life id or a situation id; a re-run, a
re-shaped tree and a library update change none of those (`64` §3's argument, verbatim
from `user_edits.py:44-64`). A library update that *drops* a life the person merged
into or assigned to is the `UnappliedUserEdit` case: reported on the screen with the
row intact, applied to nothing, and reversible with one word.

---

## What this draft does not claim

- The `groups` and `placement` stops are not built and should not be: they exist as
`--accept-groups`'s refusal (`cli.py:19731`) and `--freeze`. Adding stage names for them
would be two spellings of one gesture.
- Nothing here raises depth or changes what a level is named by; `106` says only Phase 6
does.
- Task 5.5 cannot be executed before Phase 3's gate and is written so Phase 3 builds the
seam it needs (`life_of` as a callable the partition passes, not an import).
- The `DuplicateNodeKey` guard's premise — that no pre-5.1 version holds two rows with
one origin — is stated, not measured; §E names the read-only query that measures it.
- The owner's personal-data folders and the answer key were not opened; no filename,
folder or content from the owner's corpus appears here.

---

# Phase 6 — Fact producers (draft for `106`)

> Drafted 17 Sep 2026 from the code on `build/p6-p7-first-packages` at `19d39aa3`, the
> shipped template library, and the aggregate numbers the lead measured. No file under
> `.groundtruth/` was read; every count below is either the lead's, the library's, or a
> bound derived from those two. Where the code alone cannot say how many files a cause
> covers, the query the lead should run is written out instead of a guess.

**Goal (unchanged from `106`):** the facts the folder levels are made of exist on enough
files for the branches to have somewhere to nest.

**What this draft found that changes the phase's shape** — stated first because each
one moves a task:

1. **`subject` is a folder level in 7 of the library's 208 situations**, every one of them
   `academic.*`. It already has two producers. It is not the field to attack.
2. **The fields that ARE the library's levels have no producer at all.** `project` is a
   level in 94 situations (first level in 77, required in 67), `record_type` in 64,
   `artifact_type` in 47, `stage` in 30, `capture_year` in 8 — and of those five,
   `capture_year` has **no writer anywhere in `src/`**, `artifact_type` and
   `record_type` are wired to the ranked producer in a *test* and not in production
   (`facts/kind.py` module docstring, "WHY ONLY ONE IS WIRED"), and `project` and `stage`
   are answerable by nothing but a model reading a folder name or a person.
3. **Coursework's levels are `school / term / subject / work_type`, not
   `institution / term / subject`.** `institution` is a level of `finance` (13 of its 14
   uses) and of one `nonprofit` row (`fields.py:340`, `:699`). The 17 `institution` facts
   on the corpus are therefore facts on a field that is a level of no situation those
   files are likely to be in — see §A.3 for where they came from.
4. **`106`'s item (a), "wire `photo_events` in ~5 lines", is not five lines.**
   `PhotoEventClustering` (`facts/photo_event.py:104`) needs a `same_event` predicate (a
   time window, a GPS radius, a camera-identity test) and `minimum_members`; none exists
   in `cli.py` and every one is the owner's number. It is an owner item, not a task.
5. **`106`'s item (c), "let a one-anchor `school` land `possible`", cannot work as
   written.** `PROPOSAL_ELIGIBLE_STATES = STRENGTH_ORDER[1:]` (`facts/states.py`, last
   line) excludes `possible` from every folder proposal by construction, and
   `tests/p6/test_p6_read_surface.py:186-187` pins it. What (c) actually is: the one
   document that names a school is shown to the person, whose `--confirm` writes
   `user_confirmed`, which `_group_level_agreed` already admits alone
   (`tree_design/upstream.py:664`, "the person's own answer stands alone"). Task 6.4.

---

## A. Why the facts are thin — traced in code

### A.0 First: the measurement's provenance, and two queries before any task

`106` names `run12.sqlite` as the phase's database. Run 12 predates `record_the_situation`
(16 Sep, `facts/llm_seam.py:391`) and the ratification of `SITUATION_LEVEL_ROW` (15 Sep,
`cli.py:1284`), yet the lead's table carries `situation 222` — so the table is run 22's,
or a merge. That matters here more than anywhere, because before the level stage was
live `the_one_situation` (`branch_situation.py:190`) returned `None` for every schema with
more than one situation (that is all 19 that have any), every such file fell to the
no-levels arm, and that arm's measured output is exactly `file_type`, `authored_by`,
`creation_date` and **zero** `subject` (the comment inside `open_question`,
`model_facts.py:~360`). A `file_type 249` on a run-12 database is that arm; on run 22 it
may be stale. Nothing in `src/` writes `file_type` deterministically — the only
`file_type` code is the normaliser at `cli.py:5331` and `:5412` — so its origin has to
be read, not asserted.

Two queries, on **both** databases, aggregates only:

```sql
-- who produced what, per field
select field_key, origin, reliability_state, count(distinct file_id)
from file_facts where active = 1 and superseded_by is null
group by 1, 2, 3 order by 4 desc;

-- what was refused, per field and reason (`model_returned_unknown` is the decline rate)
select field_key, reason, count(distinct file_id)
from unresolved where superseded_by is null
group by 1, 2 order by 3 desc;
```

and one more, which is section B's missing axis:

```sql
-- which situations the corpus is in (finer value only after Phase 2(b))
select v.canonical_value, count(*) from file_facts ff join "values" v using (value_id)
where ff.field_key = 'situation' and ff.active = 1 and ff.superseded_by is null
group by 1 order by 2 desc;
```

If `file_type` is `llm_interpretation` on ~249 files on run 22, the flat arm is still the
first thing to fix (§A.3); if it is not, §A.1 and §A.2 are the whole phase.

### A.1 The library builds folders from fields nothing produces

Computed over the shipped release through `production.folder_levels_for`
(`production.py:510`), which is the function the router and site A both read, so this
is the library as a run sees it and not as a document describes it. 208 situations; depth
1/2/3/4/5 in 28/84/79/15/2 of them.

| field | situations using it as a level | required | **first** level | producer in `src/` today |
| --- | --- | --- | --- | --- |
| `project` | 94 | 67 | 77 | none; model only (per-situation arm) |
| `record_type` | 64 | 45 | 6 | **none** — `kind_facts` wired for `work_type` alone (`kind.py` docstring; `cli.py:6434`) |
| `work_type` | 48 | 30 | 4 | `kind_facts` over naming zones (`cli.py:6434`) + model |
| `artifact_type` | 47 | 8 | 1 | **none** — proven only in `tests/p6/test_p6_kind.py:466` |
| `stage` | 30 | 3 | 0 | none; model only |
| `site` | 30 | 12 | 29 | none; model only |
| `record_period` | 25 | 6 | 1 | none |
| `event` | 18 | 13 | 4 | `photo_events` (`photo_event.py:173`) — **no caller** |
| `institution` | 14 | 13 | 13 | model only (finance's level) |
| `capture_year` | 8 | 6 | 6 | **none** — no writer in `src/` |
| `school` | 7 | 3 | 7 | model, anchors only (`model_facts.py:476`), then two-anchor rule at P10 |
| `subject` | 7 | 7 | 1 | `SUBJECT_RULE` (`cli.py:4942`) + model rule 13 |
| `term` | 6 | 3 | 3 | `date_facts` (`cli.py:6422`) + model rule 14 |
| `media_type` | 3 | 2 | 2 | `_media_type_stage` (`cli.py:6442`), images only |

For the schemas a student's Downloads folder is made of, the levels are:

```
academic.coursework              school(G) > term > subject* > work_type*
research.reading-library         project* > artifact_type*
research.manuscript-publication  project* > venue > stage*
research.conference-presentation venue* > project > artifact_type*
code.notebooks-experiments       project* > artifact_type*
photos.camera-events             capture_year* > event
photos.screenshot-captures       media_type* > capture_year
career.recruiting                target_employer* > job_title > recruiting_cycle > work_type*
nonprofit.member-association     record_period*
```
(`*` required, `(G)` filled from the group — `production.group_level_fields_for`,
`:420`.)

Read against the lead's fact table: the fields the corpus carries on many files —
`file_type` 249, `duplicate_family` 84, `media_type` 48, `creation_date` 47,
`version_family` 39, `authored_by` 34, `language` 15 — are levels of **three
situations between them** (`media_type`, all `photos.*`) and are declared
`destination_eligible=False` on the key for the rest (`fields.py:140-149`, `:221`). The
fields the corpus is built from — `project`, `artifact_type`, `capture_year`,
`record_type`, `stage`, `event` — appear in the table at 6, 6, 0, 0, 0, 0. **That is the
whole of the diagnosis: the producers that exist fill fields that are not levels, and the
fields that are levels have no producers.** `materialise.py:94` (`divides`) then does the
only thing it can with a level that has no values, which is not build it.

### A.2 Why each missing producer is missing — the seam for each

**`capture_year` (photos' first level, required in 7 of 10 photo situations).**
The image reader publishes `DateTimeOriginal` on every camera photograph
(`readers/image_headers.py:426`), the extractor records it as an observation at
`metadata:field=DateTimeOriginal` (`extractors/image.py:88`), `facts/fields.py:368`
declares the key, and `DIRECT_SLOTS = DirectSlots(slots=())` at `cli.py:4980` is the seam
it was meant to come through — §3.5's own example of a direct fact is "an EXIF
timestamp", and `tests/p6/test_p6_direct.py:121` already declares the slot. The comment
above `DIRECT_SLOTS` says the empty set is "honest -- a slot with a real location to name
can be added without re-deciding the composition". This is that slot. The model cannot
substitute: every EXIF observation is signalled `POTENTIALLY_SENSITIVE`
(`extractors/image.py:83`, `EXIF_BASIS`), and a signalled observation is refused for
release to every target (`model_facts.py:~1735`), so no model has ever seen a capture
time. Bound on files affected: the 48 files carrying `media_type` are images by
construction (`_media_type_stage` runs on `image/*` only, `cli.py:6442`); how many carry
EXIF is `select count(distinct file_id) from evidence where locator like
'metadata:field=DateTimeOriginal%'` — the lead's to run.

**`artifact_type` and `record_type` (research, code, creative, engineering; finance and
the operations schemas).** `facts/kind.py` is one mechanism for three keys and says so
in its first paragraph; the recognition manifest ships `work_type_terms` per schema (107
for `research`, 34 for `code`, 287 for `finance`); `tests/p6/test_p6_kind.py:437-478`
runs it for `artifact_type` and proves "binding a second key is a CALL, not a change".
The recorded reason it was never bound: *"the schema is not known when the producer
runs -- `run_p1_p7` resolves facts BEFORE it classifies"* (`kind.py` docstring;
`cli.py:5813`). **That reason is no longer true.** Since amendment 7(c) site G names a
schema per file before the fact pass walks the roster, and `_model_fact_pass` builds one
resolver per schema by `dataclasses.replace` (`cli.py:18144`, `:18357`, `:18377`,
`:18415`). Each of those resolvers is `model_fact_resolver`, whose stages are
`{"direct": None, "rule": None, "llm": ...}` (`cli.py:10160`). The seam is the `None`
under `"rule"`. `FactResolver.resolve_steps` runs the rule stage before the model stage
for the same file (`facts/resolver.py:298`), so a value the rule writes at `validated`
reaches site A as a settled field with a flag (gap 1) in the same call.

**`event`.** `photo_events` has a writer and no caller, and its injected
`PhotoEventClustering` has no production instance. Its numbers are Deferred by the
design and the owner's to give. Not a task.

**`project` and `stage`.** Neither is printed in the document it describes: a paper does
not say which project the person read it for, and a draft does not say it is a draft.
The A_fact contract can fill only what a released reading prints verbatim — template
rules 4 and 5 (`a_fact_template_folder_levels.v5.txt`), `value_grounding.value_is_grounded`
(a whole-token run of a cited value), within `FACT_CALL_MAX_RELEASED_OBSERVATIONS = 12`
readings (`cli.py:2532`). The one reading that can name a project is the person's own
folder: `extractors/filesystem.py:97` writes one `path`-zone observation per file, and
`RELEASED_TO_EVERY_TARGET = {"path", "ocr"}` (`privacy/vocabulary.py:294`) releases it to
the cloud too. So the model CAN answer `project` where the person already has a folder
called `NeurIPS 2026` — and cannot on a flat folder of 365 loose files, which `00`
amendment 11 of 16 Sep records is what the owner's corpus is. On that corpus `project`
comes from the group stage naming a group (site B, never yet run on a member —
"every one of the 266 memberships is `decision_source='rules'`") or from the person
(Phase 5's screens). **Owner item, not a Phase 6 task**, and the honest sentence for the
gate: `research.*` branches will not gain their first level from anything in this phase.

### A.3 The no-situation arm, and where the 17 `institution` facts came from

`open_question` (`model_facts.py:271`) has two arms. With a situation, the vocabulary is
`(pending ∪ settled) ∩ {the situation's own level fields}` — a coursework file is asked
`term`, `subject`, `work_type` and nothing else. With `folder_levels=None`, it is the
whole active allowlist less the group-level fields (amendment 15). A file takes the second
arm when a schema is known and no situation resolves for it:
`_the_situation_this_file_is_under` (`cli.py:17671`) → `the_one_situation` refuses
(`branch_situation.py:190`, every shipped schema has 2-28 situations) → the judge's
level answer is absent → `resolver_for` returns `no_levels_by_schema[named]`
(`cli.py:18425-18440`).

`research`'s allowlist is `project, stage, artifact_type, lab, venue, institution`
(`fields.py:673`, `institution` added by `60` H9) plus the universal rows. A research
file in the flat arm is offered `institution`, which is a level of no `research.*`
situation, and a paper's affiliation block prints one. Seventeen files carry it. Two
readings fit that number and this draft cannot tell them apart: the flat arm on research
papers, or `finance.*` files (bank statements) answering their own first required level
correctly. The third query of §A.0 joined to `institution`'s rows settles it —
`institution` on a file whose situation is `finance.*` is right; on `research.*` it is
the flat arm. Likewise the count of files that took the flat arm on run 22 is the first
query's `origin='llm_interpretation'` rows on `file_type`, `authored_by`,
`creation_date` and `language`, fields no per-situation arm can offer.

### A.4 `subject`, specifically, since the brief asked

- Level of 7 situations, all `academic.*`; required in all 7.
- Producers: `SUBJECT_RULE` (`cli.py:4942`) — a course-code shape beside one of
  `SUBJECT_CONTEXT_TERMS`, measured 3 of 3 real courses on 11 files, 0 false positives
  in 101 candidates; and the model under A_fact v5 rule 13 (a course TITLE stands where
  no code is in view; replay 4 → 13 of 107). Both run on every academic file: the rule in
  `_rule_stage`, the model in the per-situation arm (it is a level) and in the flat arm.
- What limits it is the corpus, not a seam: a homework sheet that prints neither a
  code nor a title has no `subject` for any producer, and R-135's neighbour context
  (`anchor_context_for`, `cli.py:7329`) is the mechanism for that and is live. The split
  between "asked and declined" and "never asked" is the second query's `subject` rows:
  `model_returned_unknown` against `privacy_withheld` and `no_candidate_evidence`.
- 35 files is therefore plausibly close to the number of academic files whose own text
  names the course. Raising it is prompt work the owner has declared done for now
  (`106`, "the classifier is done for now"). Not a task.

### A.5 `school` (6 files) and `term` (7 files)

`school` is never asked of an ordinary file (`00`:11.2 step 2); it is asked of an anchor
whose *settled* `work_type` is in `SCHOOL_ANCHOR_KINDS` (`cli.py:6241`), settled meaning
`validated`/`direct`/`user_confirmed` (`model_facts.py:499`, `_settled_kind` reads
`existing_facts`), i.e. the naming-zone regex found `syllabus` in the filename or title.
Then P10 needs two independent anchors in one scope (`upstream.py:664`) or the person's
word. A course with one syllabus has no school level, structurally, and nobody is told
the syllabus named one. Task 6.4 is the telling.

`term` needs a season-and-year form on the first page (`date_facts`, `cli.py:6422`;
rule 14 declines a bare year). Nothing cheap here; not a task.

---

## B. Which fields matter — ranked

Weight = (situations that build a level from the field, from §A.1) × (files whose
situation uses it, which is the third query's answer, not known to this draft). Ranked
provisionally on the library axis and on which cell is empty today:

| rank | field | why it is at the top | reachable today | Phase 6 |
| --- | --- | --- | --- | --- |
| 1 | `capture_year` | first AND required level of every `photos.*` situation but two; the corpus has ≥48 images; the producer is a §3.5 slot with a test already written | 0 files | **Task 6.1** |
| 2 | `artifact_type` | required first-or-second level of 6 of 8 `research.*` and 2 of 3 `code.*`; the producer exists and is proven; the blocker was removed by amendment 7(c) | 6 files | **Task 6.2, 6.3** |
| 3 | `record_type` | 64 situations; same producer as 2; finance's second level | 0 files | **Task 6.2, 6.3** |
| 4 | `school` | coursework's first level; the anchor's answer exists and dies at the two-anchor rule | 6 files | **Task 6.4** |
| 5 | `project` | 77 situations' first level; on a flat folder no producer in this product can answer it | 6 files | owner item (§G) |
| 6 | `event` | photos' second level; producer written, thresholds unauthored | 0 files | owner item (§G) |
| — | `subject`, `term`, `work_type` | producers exist; the ceiling is prompt text and the corpus | 35 / 7 / 46 | no task |
| — | `file_type`, `authored_by`, `creation_date`, `language`, `institution` | not levels of these files' situations | 249 / 34 / 47 / 15 / 17 | stop asking (falls out of Phase 2 resolving situations; measure with query 1) |

---

## C. The producers that should exist

Constitution: the model is the judge; code packages the data. Two of the four below are
deterministic, and that is not a departure: §3.5 names the EXIF timestamp as the design's
own example of a fact no model should be asked for, and `60` H6 names the type keys as one
closed vocabulary the library ships — the model is asked the same field in the same call,
with the rule's value flagged, and reconciles (`00`:42 amendment).

| field | source | seam | why this source |
| --- | --- | --- | --- |
| `capture_year` | filesystem/EXIF, direct slot | `cli.DIRECT_SLOTS` (`cli.py:4980`) → `_direct_stage` → runs in `run_p1_p7` for every file, protected ones included, on this machine | the only reader that has ever seen the tag; no threshold, no prompt; §3.5's canonical example |
| `artifact_type` / `record_type` | ranked rule over the schema's own terms, AFTER site G names the schema; then the model, flagged | `model_fact_resolver(..., rule=type_key_rule(schema))` at the five build sites in `_model_fact_pass` | `kind.py`'s recorded blocker is gone; the vocabulary is the library's; per-schema, never the union (H6.3) |
| same two, the model's spelling | `normalize_for_model` | `cli.py:5376`, beside the `work_type` branch at `:5443` | "the model's value is canonicalised by the SAME rule the deterministic path uses" — today `Poster` and `poster` are two folders |
| `school`, one anchor | the person, shown what one document said | a block after `_print_values_to_confirm` in `_model_fact_pass`; `--confirm` already writes `user_confirmed`; `_group_level_agreed` already admits it alone | (c) as it can actually work under the ladder |

**Rejected — `106` item (b)**, "take `SCHOOL_ANCHOR_KINDS` membership from a `work_type`
settled by ANY producer". It contradicts two recorded rules stated in the code:
`AnchorOnlyLevels`' docstring ("a model's own guess about what a file is can never open
the question about it") and `_schema_reached_by_the_facts` (`cli.py:6330`, "letting one
of those widen the allowlist would let a model author its own next question"). It would
also not fire in the call it is computed for: `anchor_only_levels` reads the request
already built, and the model's `work_type` arrives in that same answer. If the owner
wants it, the compromise is an `llm_supported` kind admitted only when its citation does
not rest on the filename alone (`rests_on_a_name_alone`, `cli.py:6255`), and it is an
owner decision, recorded in §G.

---

## D. Phase 6 — full task list

Every task: test first, watch it fail for the stated reason, implement, watch it pass,
`nice -n 15 python3 -m pytest <file> -p no:randomly -q`, commit. No task edits
`src/llm_harness/library/**` or `src/privacy/**`.

### Task 6.0: The measurement — how many files reach a level of their own situation

The phase's gate has to exist before the phase, or every producer below is graded on a
number nobody can reproduce. `106` Phase 1 built `group_cohesion` for exactly this reason.

**Files:**
- Create: `tools/groundtruth/level_reach.py`
- Test: `tests/tools/test_groundtruth_level_reach.py`
- Modify: nothing else (printing it in `report.py` is one line in that file's idiom, after
  the GROUPS block at `report.py:695`, and is left to the lead because the report's
  fixtures need the owner's database).

**Depends on Phase 2(b)** (the untracked `tests/integration/test_the_level_answer_is_written_down.py`):
`folder_levels_for` raises `ConfigurationRequired` on a schema id, so a `situation`
fact holding `academic` rather than `academic.coursework` counts as *unresolvable* here.
On a database written before 2(b) the number is honest and low; that is the baseline.

- [ ] **Step 1: the failing test.**

```python
# tests/tools/test_groundtruth_level_reach.py
"""`106` Phase 6's gate: a file has a level to nest under, or it does not.

WHAT THIS MEASURES. Not placement and not fact count. A file reaches a level when it
carries, at a state a folder proposal may rest on (`PROPOSAL_ELIGIBLE_STATES`), a fact
on a `destination_eligible` field that its OWN situation builds a folder from
(`production.folder_levels_for`). `file_type` on 249 files reaches nothing, because no
situation those files are in has a `file_type` level. A file with no situation fact is
in the denominator: a file the judge never placed is a file this phase did not help.
"""
from __future__ import annotations

import json
from pathlib import Path

from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file
from evidence_shape.schema import create_evidence_schema
from facts.fields import create_fields
from facts.file_facts import RULE, write_fact
from facts.llm_seam import SITUATION_FIELD
from facts.states import LLM_SUPPORTED, POSSIBLE, VALIDATED
from facts.values import VALUE_ORIGINS, ensure_value
from production import load_shipped_catalogue, read_packaged_library_file
from tools.groundtruth.level_reach import level_reach

COURSEWORK = "academic.coursework"
CAMERA = "photos.camera-events"

#: `write_fact` refuses a non-`user_confirmed` fact with no citation and checks the
#: SHAPE of the key (`file_facts._checked_refs`: `sha256:` + 64 hex), never that it
#: resolves. The gate reads states and fields and walks no evidence, so a well-formed
#: key that points at nothing is the honest fixture here.
CITED = "sha256:" + "0" * 64


def _file(conn, tmp_path, name):
    path = tmp_path / name
    path.write_bytes(b"bytes")
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=5,
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _fact(conn, file_id, content_hash, field_key, value, state):
    value_id = ensure_value(conn, field_key=field_key, canonical_value=value,
                            first_evidence_ref=CITED, origin=VALUE_ORIGINS[0])
    return write_fact(conn, file_id=file_id, content_hash=content_hash,
                      field_key=field_key, value_id=value_id,
                      reliability_state=state, origin=RULE, evidence_refs=(CITED,),
                      cache_key=f"test:{file_id}:{field_key}", active=True)


def _store(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    return load_shipped_catalogue(read_packaged_library_file)


def test_a_coursework_file_with_a_subject_reaches_a_level(conn, tmp_path):
    catalogue = _store(conn)
    file_id, content_hash = _file(conn, tmp_path, "hw3.pdf")
    _fact(conn, file_id, content_hash, SITUATION_FIELD, COURSEWORK, LLM_SUPPORTED)
    _fact(conn, file_id, content_hash, "subject", "PHYS1401", VALIDATED)
    reach = level_reach(conn, catalogue)
    assert (reach.files, reach.with_situation, reach.reached) == (1, 1, 1)
    assert reach.by_field == {"subject": 1}


def test_a_file_type_fact_reaches_nothing(conn, tmp_path):
    """The 249. SABOTAGE: count every destination-eligible fact, or every fact at
    all -- then `file_type` on a coursework file scores as a level and the gate reads
    as already met on a tree that is flat."""
    catalogue = _store(conn)
    file_id, content_hash = _file(conn, tmp_path, "hw3.pdf")
    _fact(conn, file_id, content_hash, SITUATION_FIELD, COURSEWORK, LLM_SUPPORTED)
    _fact(conn, file_id, content_hash, "file_type", "pdf", VALIDATED)
    reach = level_reach(conn, catalogue)
    assert (reach.files, reach.with_situation, reach.reached) == (1, 1, 0)


def test_a_possible_fact_reaches_nothing(conn, tmp_path):
    """`PROPOSAL_ELIGIBLE_STATES` excludes `possible`; a proposal the person has not
    answered is not a level. SABOTAGE: drop the state filter."""
    catalogue = _store(conn)
    file_id, content_hash = _file(conn, tmp_path, "hw3.pdf")
    _fact(conn, file_id, content_hash, SITUATION_FIELD, COURSEWORK, LLM_SUPPORTED)
    _fact(conn, file_id, content_hash, "subject", "PHYS1401", POSSIBLE)
    assert level_reach(conn, catalogue).reached == 0


def test_a_file_with_no_situation_is_in_the_denominator(conn, tmp_path):
    """SABOTAGE: `if situation is None: continue` -- then a run whose judge placed
    nobody scores 0 of 0 and prints as perfect. `00`:259 one stage earlier."""
    catalogue = _store(conn)
    file_id, content_hash = _file(conn, tmp_path, "IMG_1.jpg")
    _fact(conn, file_id, content_hash, "capture_year", "2024", VALIDATED)
    reach = level_reach(conn, catalogue)
    assert (reach.files, reach.with_situation, reach.reached) == (1, 0, 0)


def test_a_situation_that_is_only_a_schema_id_is_unresolvable_not_reached(conn, tmp_path):
    """Before Phase 2(b) the `situation` fact holds `academic`; `folder_levels_for`
    refuses it and so must this. Counted, named, never guessed at."""
    catalogue = _store(conn)
    file_id, content_hash = _file(conn, tmp_path, "hw3.pdf")
    _fact(conn, file_id, content_hash, SITUATION_FIELD, "academic", LLM_SUPPORTED)
    _fact(conn, file_id, content_hash, "subject", "PHYS1401", VALIDATED)
    reach = level_reach(conn, catalogue)
    assert (reach.with_situation, reach.unresolvable, reach.reached) == (1, 1, 0)


def test_a_level_of_another_situation_does_not_count(conn, tmp_path):
    """`capture_year` is photos' level and not coursework's. SABOTAGE: test
    destination eligibility alone -- then any eligible fact anywhere reaches."""
    catalogue = _store(conn)
    file_id, content_hash = _file(conn, tmp_path, "hw3.pdf")
    _fact(conn, file_id, content_hash, SITUATION_FIELD, COURSEWORK, LLM_SUPPORTED)
    _fact(conn, file_id, content_hash, "capture_year", "2024", VALIDATED)
    assert level_reach(conn, catalogue).reached == 0
    photo, photo_hash = _file(conn, tmp_path, "IMG_2.jpg")
    _fact(conn, photo, photo_hash, SITUATION_FIELD, CAMERA, LLM_SUPPORTED)
    _fact(conn, photo, photo_hash, "capture_year", "2024", VALIDATED)
    assert level_reach(conn, catalogue).reached == 1
```

- [ ] **Step 2: run it.** `nice -n 15 python3 -m pytest tests/tools/test_groundtruth_level_reach.py -p no:randomly -q` → `ModuleNotFoundError: tools.groundtruth.level_reach`.

- [ ] **Step 3: write the module.**

```python
# tools/groundtruth/level_reach.py
"""`106` Phase 6's gate: files that carry a level of their OWN situation.

Not `score_fields` (that grades against the owner's labels) and not a fact count.
The question is the one `materialise.py`'s `divides` asks one stage later: is there
a value under this file the template can nest it by. Read directly off the database
so it runs on `run12.sqlite` and `run22.sqlite` alike, aggregates only.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field

from facts.llm_seam import SITUATION_FIELD
from facts.states import PROPOSAL_ELIGIBLE_STATES
from production import folder_levels_for
from tree_design.config import ConfigurationRequired


@dataclass(frozen=True)
class LevelReach:
    files: int
    with_situation: int
    #: Files whose `situation` fact names nothing `folder_levels_for` resolves --
    #: a bare schema id written before `106` Phase 2(b), or several live values.
    unresolvable: int
    reached: int
    by_field: dict[str, int] = field(default_factory=dict)


def level_reach(conn: sqlite3.Connection, catalogue) -> LevelReach:
    eligible = {row[0] for row in conn.execute(
        "select field_key from fields where destination_eligible = 1")}
    situations: dict[str, set[str]] = {}
    facts: dict[str, set[tuple[str, str]]] = {}
    for row in conn.execute(
            'select ff.file_id, ff.field_key, ff.reliability_state, v.canonical_value '
            'from file_facts ff join "values" v using (value_id) '
            'where ff.active = 1 and ff.superseded_by is null'):
        file_id, key, state, value = row
        if key == SITUATION_FIELD:
            situations.setdefault(file_id, set()).add(value)
        elif key in eligible and state in PROPOSAL_ELIGIBLE_STATES:
            facts.setdefault(file_id, set()).add((key, state))
    files = {row[0] for row in conn.execute("select file_id from files")}
    unresolvable = reached = 0
    by_field: dict[str, int] = {}
    for file_id in files:
        named = situations.get(file_id, set())
        if len(named) != 1:
            unresolvable += bool(named)
            continue
        try:
            levels = {level.field for level in
                      folder_levels_for(catalogue, next(iter(named)))}
        except ConfigurationRequired:
            unresolvable += 1
            continue
        hit = sorted({key for key, _state in facts.get(file_id, ()) if key in levels})
        if not hit:
            continue
        reached += 1
        for key in hit:
            by_field[key] = by_field.get(key, 0) + 1
    return LevelReach(files=len(files), with_situation=len(situations),
                      unresolvable=unresolvable, reached=reached, by_field=by_field)
```

`ConfigurationRequired` is the exception `folder_levels_for` raises (`production.py:531`),
imported there from `tree_design.config` (`production.py:59`).

- [ ] **Step 4: run the test.** Expect `6 passed`.
- [ ] **Step 5: take the number (lead only)** on run 22's database — that is the
  baseline every task below is measured against — and once more on run 12 so the
  provenance question in §A.0 is answered by the same instrument.
- [ ] **Step 6: commit.** `feat(106 Phase 6.0): the gate exists before the producers -- files that reach a level of their own situation`

### Task 6.1: `capture_year` — the EXIF capture time becomes a direct fact

**Files:**
- Modify: `src/cli.py` (the `DIRECT_SLOTS` declaration at `:4980` and the comment above it)
- Test: `tests/p6/test_p6_capture_year_slot.py` (new)

- [ ] **Step 1: the failing test.**

```python
# tests/p6/test_p6_capture_year_slot.py
"""`106` Phase 6 Task 6.1: the EXIF capture time becomes `capture_year`.

`capture_year` is the FIRST level of eight of the library's ten photo situations and
required in seven (`production.folder_levels_for`), and no producer in `src/` has ever
written it. The image reader publishes `DateTimeOriginal` on every camera photograph,
the extractor records it at `metadata:field=DateTimeOriginal`, `facts.fields` declares
the key, and `cli.DIRECT_SLOTS` shipped empty. §3.5 names "an EXIF timestamp" as the
design's own example of a direct fact. The model is no substitute: every EXIF
observation is signalled sensitive and never released to any target.

The slot is the composition root's, exactly as `tests/p6/test_p6_direct.py:121`
declares one -- `facts.direct` spells no tag name and this test spells only the
reader's.
"""
from __future__ import annotations

import json
from pathlib import Path

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from facts.file_facts import facts_for_file
from facts.states import DIRECT

import cli

CLOCK = "2026-09-18T00:00:00+00:00"


def _photo(conn, tmp_path, name="IMG_4821.heic"):
    path = tmp_path / name
    path.write_bytes(b"\x00photo-bytes")
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=12,
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Photos", mime_type="image/heic",
        detected_format="heic", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _exif(conn, *, run_id, file_id, content_hash, tag, raw):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="image.exif", extractor_version="1.0.0",
        source_type="image", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    record_observation(conn, Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="image.exif",
        extractor_version="1.0.0", source_type="image", raw_value=raw,
        location=Location("metadata", (Segment("field", label=tag),)),
        occurrence_count=1, observed_at=CLOCK, reliability="direct", run_id=run_id))


def _years(conn, file_id, content_hash):
    return [(row["canonical_value"], row["reliability_state"])
            for row in facts_for_file(conn, file_id, content_hash)
            if row["field_key"] == cli.CAPTURE_YEAR_FIELD and row["active"]]


def test_a_camera_photograph_gets_its_capture_year_as_a_direct_fact(p6_conn, tmp_path):
    """SABOTAGE: `DIRECT_SLOTS = DirectSlots(slots=())` -- the stage runs, claims
    nothing, and every photo situation's first level stays empty, silently."""
    file_id, content_hash = _photo(p6_conn, tmp_path)
    _exif(p6_conn, run_id="run-1", file_id=file_id, content_hash=content_hash,
          tag=cli.CAPTURE_TIME_TAG, raw="2024:07:17 14:03:22")
    written = cli._direct_stage(p6_conn, file_id, content_hash)
    assert len(written) == 1
    assert _years(p6_conn, file_id, content_hash) == [("2024", DIRECT)]


def test_a_camera_with_no_clock_writes_no_year(p6_conn, tmp_path):
    """Cameras with an unset clock write `0000:00:00 00:00:00`. SABOTAGE: drop
    `matches` -- `0000` becomes a folder."""
    file_id, content_hash = _photo(p6_conn, tmp_path)
    _exif(p6_conn, run_id="run-1", file_id=file_id, content_hash=content_hash,
          tag=cli.CAPTURE_TIME_TAG, raw="0000:00:00 00:00:00")
    assert cli._direct_stage(p6_conn, file_id, content_hash) == ()
    assert _years(p6_conn, file_id, content_hash) == []


def test_the_files_last_edit_is_not_its_capture_year(p6_conn, tmp_path):
    """`DateTime` is when the file was last written; `DateTimeDigitized` is when a
    scan was made. Neither is when the picture was taken. SABOTAGE: match
    `"DateTime" in locator`."""
    file_id, content_hash = _photo(p6_conn, tmp_path)
    _exif(p6_conn, run_id="run-1", file_id=file_id, content_hash=content_hash,
          tag="DateTime", raw="2026:01:01 09:00:00")
    _exif(p6_conn, run_id="run-2", file_id=file_id, content_hash=content_hash,
          tag="DateTimeDigitized", raw="2025:01:01 09:00:00")
    assert cli._direct_stage(p6_conn, file_id, content_hash) == ()


def test_the_models_year_is_canonicalised_by_the_same_rule():
    """`normalize_for_model` applies the slot's own `matches` and `canonical` to a
    model's value. A grounded, bare year must survive; a month or a phrase must
    not. SABOTAGE: make `matches` accept only the EXIF form -- a correct model
    answer of `2024` from a scanned document's own text is refused as
    unnormalizable."""
    assert cli.normalize_for_model(cli.CAPTURE_YEAR_FIELD, "2024") == "2024"
    assert cli.normalize_for_model(cli.CAPTURE_YEAR_FIELD, "2024:07:17 14:03:22") == "2024"
    assert cli.normalize_for_model(cli.CAPTURE_YEAR_FIELD, "July 2024") is None
    assert cli.normalize_for_model(cli.CAPTURE_YEAR_FIELD, "0000") is None
```

- [ ] **Step 2: run it.** `nice -n 15 python3 -m pytest tests/p6/test_p6_capture_year_slot.py -p no:randomly -q` → `AttributeError: module 'cli' has no attribute 'CAPTURE_YEAR_FIELD'`. Any other failure is the test's.

- [ ] **Step 3: implement.** Replace `DIRECT_SLOTS = DirectSlots(slots=())` at `cli.py:4980`
  with the block below, and amend the comment above it (its sentence "THIS DEPLOYMENT NOW
  SHIPS NONE" becomes false and must say what replaced it).

```python
#: §3.11's Photos time dimension: the first folder level of eight of the library's
#: ten photo situations and required in seven (`production.folder_levels_for`).
#: `106` Phase 6.1: NOTHING WROTE IT. The catalogue declared the key
#: (`facts.fields._PHOTOS`), the image reader published the tag on every camera
#: photograph, and the slot that joins them was declared in `tests/p6/test_p6_direct.py`
#: and nowhere else. §3.5's own example of a direct fact is "an EXIF timestamp".
CAPTURE_YEAR_FIELD = "capture_year"

#: The reader's own tag name (`readers.image_headers`: `kCGImagePropertyExifDateTimeOriginal`),
#: on the locator as `metadata:field=DateTimeOriginal` (`extractors.image`). Spelled
#: HERE and not in `facts.direct`, which is the injection that module's docstring asks
#: for. `DateTime` (last edit) and `DateTimeDigitized` (when a scan was made) are not
#: claimed: neither is when the picture was taken.
CAPTURE_TIME_TAG = "DateTimeOriginal"

#: A year, alone or opening EXIF's `YYYY:MM:DD HH:MM:SS`. A reading that does not
#: open with a plausible year is refused rather than sliced: a camera with an unset
#: clock writes `0000:00:00 00:00:00`, and `0000` as a folder is worse than none.
#: The bare form is for `normalize_for_model`, which runs a model's value through
#: this same slot; a grounded `2024` off a scanned document's own text is a year.
_CAPTURE_YEAR = re.compile(r"(?P<year>[12]\d{3})(?::\d{2}:\d{2}(?:\s.*)?)?$")

CAPTURE_YEAR_SLOT = DirectSlot(
    slot_id="exif-capture-year", field_key=CAPTURE_YEAR_FIELD,
    names=lambda locator: locator.endswith(f"field={CAPTURE_TIME_TAG}"),
    matches=lambda raw: _CAPTURE_YEAR.match(raw.strip()) is not None,
    canonical=lambda raw: _CAPTURE_YEAR.match(raw.strip()).group("year"))

DIRECT_SLOTS = DirectSlots(slots=(CAPTURE_YEAR_SLOT,))
```

`re` and `DirectSlot` are already imported in `cli.py` (`:40`, `:93`). The screen
(`METADATA_SCREEN`) is consulted by `direct_facts` before the canonicaliser, and §2.3's
demotion would confine a demoted property to `AUTHORSHIP_FIELDS`; checked on the shipped
capture catalogue, `readers.capture.metadata_property_names()` carries 20 names and none
with `Date` or `Time` in it, so the tag is neither suppressed nor demoted and the first
test proves it against the real screen.

Tests that read `DIRECT_SLOTS` today and stay green: `tests/p5/test_p5_structured_text.py:235`,
`:411`, `:517` assert no slot claims a structured-text locator (this one claims
`metadata:field=DateTimeOriginal` and nothing else); `tests/integration/test_p9_active_schema_slot_retired.py`
reads the slot tuple only in its docstring's history and asserts on other things.

- [ ] **Step 4: run the test file, then `tests/p6/test_p6_direct.py` and
  `tests/test_cli_a_value_the_library_has_not_seen.py`** (the second exercises
  `normalize_for_model`'s slot branch). Expect green. A red `test_p6_subject_slot.py`
  means a guard there pins "no slot ships" — read its reason before changing it; the
  reason it records is about the TEXT slot and does not reach a metadata one.
- [ ] **Step 5: take the number** (`level_reach.by_field["capture_year"]`) — the
  first time it is non-zero on the owner's corpus.
- [ ] **Step 6: commit.** `feat(106 Phase 6.1): the EXIF capture time is a direct fact, and photos gain their first level`

### Task 6.2: `artifact_type` and `record_type` — the type-key rule, routed by the schema site G named

**Files:**
- Modify: `src/cli.py` — `ARTIFACT_TYPE_FIELD`, `RECORD_TYPE_FIELD`, `TYPE_KEYS` beside
  `WORK_TYPE_FIELD` (`:5773`); `FIELDS_THAT_CANNOT_ANCHOR_A_MOVE` (`:5794`) widened; new
  `type_key_for`, `type_key_rule` beside `_rule_stage` (`:6394`); `model_fact_resolver`
  (`:10160`) gains `rule=None`; the five `model_fact_resolver(` calls in
  `_model_fact_pass` (`:18132`, `:18144`, `:18357`, `:18377`, `:18415`) pass it.
- Modify: `src/branch_situation.py:95` — `BRIDGES_THAT_DO_NOT_REACH` widened to match
  (`tests/test_branch_situation.py:55` pins the two sets equal).
- Test: `tests/p6/test_p6_type_key_routed_by_the_schema.py` (new)

**Why the bridge sets widen, and it is not optional.** A `validated` fact on a schema's
own field is schema evidence in two readers: `_schema_reached_by_the_facts`
(`cli.py:6326`, `own = DOMAIN_FIELDS[schema] - BRIDGES_THAT_DO_NOT_REACH`) activates
every schema whose field the file carries, and `partition_by_branch`
(`branch_situation.py:409`) carries an un-named file into every branch whose field it
carries. `artifact_type` is declared by five schemas and `record_type` by seven, so a
`validated` `poster` on a research file would activate `code`, `creative` and
`engineering` and widen its question — which is exactly why `work_type` and `term` are
bridges today: `FIELDS_THAT_CANNOT_ANCHOR_A_MOVE`'s own comment says it is "the list of
FIELDS this catalogue can actually fill with [a what-or-when]... The day either changes,
this set is where it changes." This is that day. `capture_year` is deliberately NOT
added: it is declared by `photos` alone, and a file carrying an EXIF capture time
reaching the `photos` schema is the truth about the file, exactly as `media_type`
reaches it today.

- [ ] **Step 1: the failing test.**

```python
# tests/p6/test_p6_type_key_routed_by_the_schema.py
"""`106` Phase 6.2: the type keys `60` H6 named are produced, routed by the schema.

`facts.kind` is ONE mechanism for `work_type`, `artifact_type` and `record_type`, and
the recognition manifest ships the terms per schema. The production root wired
`work_type` alone, and its recorded reason was that the schema "is not known when the
producer runs -- `run_p1_p7` resolves facts BEFORE it classifies". Since `00` amendment
7(c) site G names a schema per file before the fact pass walks the roster, and
`_model_fact_pass` builds one resolver per schema. This binds the rule there.

H6.2, kept whole: the ACTIVE SCHEMA chooses the key, a file is never re-routed to the
nearest declared key, and a schema declaring `work_type` has already had its type
question answered corpus-wide. H6.3, kept whole: the vocabulary is the schema's OWN and
never the union -- `research`'s `protocol` must not be found in a `finance` file.
"""
from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from facts.fields import DOMAIN_FIELDS
from facts.file_facts import facts_for_file
from facts.states import VALIDATED

import cli

CLOCK = "2026-09-18T00:00:00+00:00"


def _record(conn, tmp_path, *, name):
    path = tmp_path / name
    path.write_bytes(b"corpus")
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=6,
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _named(conn, *, file_id, content_hash, raw):
    record_run(conn, ExtractionRun(
        run_id="run-name", file_id=file_id, content_hash=content_hash,
        extractor_name="filesystem.record", extractor_version="1.0.0",
        source_type="filesystem", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    record_observation(conn, Observation(
        file_id=file_id, content_hash=content_hash,
        extractor_name="filesystem.record", extractor_version="1.0.0",
        source_type="filesystem", raw_value=raw,
        location=Location("filename", ()), occurrence_count=1,
        observed_at=CLOCK, reliability="possible", run_id="run-name"))


def _typed(conn, file_id, content_hash, field_key):
    return [(row["canonical_value"], row["reliability_state"])
            for row in facts_for_file(conn, file_id, content_hash)
            if row["field_key"] == field_key and row["active"]]


def test_a_research_file_named_poster_gets_an_artifact_type(p6_conn, tmp_path):
    """SABOTAGE: return `None` from `type_key_rule` for every schema -- nothing is
    written, and every `research.*` branch's required `artifact_type` stays empty."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="NeurIPS poster final.pdf")
    _named(p6_conn, file_id=file_id, content_hash=content_hash,
           raw="NeurIPS poster final.pdf")
    stage = cli.type_key_rule("research")
    assert stage is not None
    assert len(stage(p6_conn, file_id, content_hash)) == 1
    assert _typed(p6_conn, file_id, content_hash, "artifact_type") == [("poster", VALIDATED)]
    assert _typed(p6_conn, file_id, content_hash, "work_type") == []


def test_a_finance_file_named_bank_statement_gets_a_record_type(p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="bank statement march.pdf")
    _named(p6_conn, file_id=file_id, content_hash=content_hash,
           raw="bank statement march.pdf")
    stage = cli.type_key_rule("finance")
    assert stage is not None
    stage(p6_conn, file_id, content_hash)
    assert _typed(p6_conn, file_id, content_hash, "record_type") == [("bank statement", VALIDATED)]


def test_the_vocabulary_is_the_schemas_own_and_never_the_union(p6_conn, tmp_path):
    """H6.3. SABOTAGE: compile the union over every schema -- `bank statement` is
    found in a research file and written under `artifact_type`."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="bank statement march.pdf")
    _named(p6_conn, file_id=file_id, content_hash=content_hash,
           raw="bank statement march.pdf")
    cli.type_key_rule("research")(p6_conn, file_id, content_hash)
    assert _typed(p6_conn, file_id, content_hash, "artifact_type") == []


def test_a_schema_that_declares_work_type_routes_no_second_key():
    """`_rule_stage` already filled `work_type` for every file. SABOTAGE: route
    `record_type` for `career` -- `resume` lands under two keys on one file, which is
    the H6.3 collision `facts.kind` measured on 15 files."""
    for schema_id, fields in DOMAIN_FIELDS.items():
        if cli.WORK_TYPE_FIELD in fields:
            assert cli.type_key_for(schema_id) is None, schema_id
            assert cli.type_key_rule(schema_id) is None, schema_id


def test_every_routed_key_is_declared_by_its_schema():
    """H6.2: never re-routed to the nearest declared key."""
    routed = {schema_id: cli.type_key_for(schema_id) for schema_id in DOMAIN_FIELDS}
    assert any(routed.values()), "nothing routes -- the rule is dead"
    for schema_id, key in routed.items():
        assert key is None or key in DOMAIN_FIELDS[schema_id], (schema_id, key)
        assert key != cli.WORK_TYPE_FIELD


def test_a_schema_the_catalogue_carries_no_fields_for_routes_nothing():
    for schema_id in ("identity", "medical", "legal"):
        assert cli.type_key_rule(schema_id) is None


def test_a_type_key_carries_no_file_into_a_branch_and_anchors_no_move():
    """`artifact_type` is declared by five schemas and `record_type` by seven. A
    `validated` one is the same kind of claim as `work_type` -- what the file IS --
    and `work_type` is a bridge for that reason. SABOTAGE: leave the sets as they
    were -- a `poster` on a research file activates `code`, `creative` and
    `engineering` (`_schema_reached_by_the_facts`) and, un-named, is held between
    four branches (`partition_by_branch`)."""
    from branch_situation import BRIDGES_THAT_DO_NOT_REACH
    for key in (cli.ARTIFACT_TYPE_FIELD, cli.RECORD_TYPE_FIELD):
        assert key in cli.FIELDS_THAT_CANNOT_ANCHOR_A_MOVE
        assert key in BRIDGES_THAT_DO_NOT_REACH
    assert cli.CAPTURE_YEAR_FIELD not in BRIDGES_THAT_DO_NOT_REACH, (
        "a capture time reaching `photos` is the truth about the file")


def test_every_resolver_the_fact_pass_builds_carries_the_rule():
    """The wiring, read off the code and not off a comment. `_model_fact_pass` is a
    closure inside `main`, so the whole module is parsed and every call of
    `model_fact_resolver` in it is the set -- the five build sites and no others.
    SABOTAGE: drop `rule=` at one of the five -- files of that schema get no type
    key, and nothing on the screen says which schema was left out."""
    tree = ast.parse(inspect.getsource(cli))
    builds = [node for node in ast.walk(tree)
              if isinstance(node, ast.Call)
              and getattr(node.func, "id", None) == "model_fact_resolver"]
    assert len(builds) == 5, [ast.dump(call.func) for call in builds]
    for call in builds:
        assert any(keyword.arg == "rule" for keyword in call.keywords), ast.dump(call)
```

- [ ] **Step 2: run it.** → `AttributeError: module 'cli' has no attribute 'type_key_rule'`.

- [ ] **Step 3: implement.** In `cli.py`, beside `WORK_TYPE_FIELD` (`:5773`):

```python
#: `60` H6.1's other two type keys. ONE mechanism (`facts.kind`), three keys, routed by
#: the schema that declares them (H6.2). `work_type` is filled corpus-wide by
#: `_rule_stage` before anything has named a schema; these two could not be, because
#: their vocabularies collide across schemas (H6.3: `resume` under two keys on 15
#: files) and the schema was unknown when the producer ran. IT IS KNOWN NOW: `00`
#: amendment 7(c) has site G name it per file before the fact pass walks the roster,
#: and `_model_fact_pass` builds one resolver per schema. `type_key_rule` below
#: `_rule_stage` is that resolver's `rule` stage. `106` Phase 6.2.
ARTIFACT_TYPE_FIELD = "artifact_type"
RECORD_TYPE_FIELD = "record_type"
TYPE_KEYS: tuple[str, ...] = (WORK_TYPE_FIELD, ARTIFACT_TYPE_FIELD, RECORD_TYPE_FIELD)
```

then `FIELDS_THAT_CANNOT_ANCHOR_A_MOVE` at `:5794` becomes the three type keys plus the
term — its comment's own "the day either changes, this set is where it changes":

```python
FIELDS_THAT_CANNOT_ANCHOR_A_MOVE = frozenset({*TYPE_KEYS, TERM_FIELD})
```

and `branch_situation.py:95`, which spells the same set without importing `cli`:

```python
BRIDGES_THAT_DO_NOT_REACH: frozenset[str] = frozenset(
    {"work_type", "artifact_type", "record_type", "term"})
```

Then, directly after `_rule_stage` (`:6440`):

```python
def type_key_for(schema_id: str) -> str | None:
    """The ONE type key a schema-routed rule may fill for this schema, or `None`.

    H6.2: "a file whose routed type key is not declared by the active schema returns
    unknown; it is never re-routed to the nearest declared type key." A schema that
    declares `work_type` routes nothing here -- `_rule_stage` already answered its
    type question for every file, and `career` declaring both `work_type` and
    `record_type` is exactly the collision H6.3 measured. A schema declaring two of
    the remaining keys (none today) gets neither: choosing would be this function
    deciding what kind of thing a file is.
    """
    declared = [key for key in TYPE_KEYS if key in DOMAIN_FIELDS.get(schema_id, ())]
    if len(declared) != 1 or declared[0] == WORK_TYPE_FIELD:
        return None
    return declared[0]


_TYPE_KEY_VOCABULARIES: dict[str, KindVocabulary] = {}


def _type_key_vocabulary(schema_id: str) -> KindVocabulary:
    """This schema's OWN shipped terms, compiled once. Per schema and never the union,
    for H6.3's reason: values are schema-qualified, and `research`'s `protocol` must
    not be found in a `finance` file."""
    if schema_id not in _TYPE_KEY_VOCABULARIES:
        schemas = json.loads(_RECOGNITION_MANIFEST.read_text())["schemas"]
        _TYPE_KEY_VOCABULARIES[schema_id] = compile_vocabulary(
            schemas.get(schema_id, {}).get("work_type_terms", ()))
    return _TYPE_KEY_VOCABULARIES[schema_id]


def type_key_rule(schema_id: str):
    """`FactResolver`'s `rule` stage for a file site G named `schema_id` for, or
    `None` where the schema routes no key -- `None` being `FactResolver`'s own word
    for a stage that does not exist, so nothing is barred and no row is written.

    The four §3.7 numbers, the naming zones and the first page are `_rule_stage`'s
    own, unchanged: a syllabus and a poster are the same kind of claim about what a
    file IS, and a term in body prose is a document mentioning some other document.
    """
    field_key = type_key_for(schema_id)
    if field_key is None:
        return None
    vocabulary = _type_key_vocabulary(schema_id)

    def stage(conn, file_id: str, content_hash: str) -> tuple[str, ...]:
        return kind_facts(
            conn, file_id=file_id, content_hash=content_hash,
            field_key=field_key, vocabulary=vocabulary,
            naming_zones=WORK_TYPE_NAMING_ZONES, first_page=FIRST_PAGE,
            zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT,
            minimum_score=MINIMUM_SCORE, minimum_margin=MINIMUM_MARGIN)
    return stage
```

`KindVocabulary` joins the existing `from facts.kind import compile_vocabulary, kind_facts`
at `cli.py:146`. `compile_vocabulary` raises `EmptyVocabulary` on a schema with no terms;
every schema in the shipped manifest carries terms, and one that routes no key is never
compiled.

Then `model_fact_resolver` (`cli.py:10160`):

```python
def model_fact_resolver(conn: sqlite3.Connection, *,
                        authorities: FactCallAuthorities,
                        rule=None) -> FactResolver:
    """P6 again: the model producer, and since `106` Phase 6.2 the type-key rule the
    schema routes, run before it for the same file so its value reaches the model as
    a settled field with a flag (`104` §18.2 gap 1) in the same call.
    ...(the rest of the docstring stands)...
    """
    return FactResolver(
        stages={"direct": None, "rule": rule,
                "llm": fact_call_stage(authorities)},
```

and at the five build sites in `_model_fact_pass`, one keyword each:

```python
        # :18132 -- the run's own situation
        else {said().situation: model_fact_resolver(
            conn, authorities=authorities, rule=type_key_rule(pass_schema))})
        # :18144 -- a settled branch
                by_situation[branch.situation] = model_fact_resolver(
                    conn, rule=type_key_rule(branch.schema), authorities=...)
        # :18357, :18377, :18415 -- site G's schemas
                by_situation[situation] = model_fact_resolver(
                    conn, rule=type_key_rule(schema_id), authorities=...)
            no_levels_by_schema[schema_id] = model_fact_resolver(
                conn, rule=type_key_rule(schema_id), authorities=...)
            by_situation[resolved] = model_fact_resolver(
                conn, rule=type_key_rule(schema_id), authorities=...)
```

What this does NOT reach, stated: a protected record leaves `_walked` before
`resolver_for` (`cli.py:18512`, "filed by the person"), and a file nobody named a schema
for has no resolver. Both are the standing rules and this task keeps them.

- [ ] **Step 4: run the test file, then `tests/p6/test_p6_kind.py`,
  `tests/test_branch_situation.py`, `tests/integration/test_local_model_fact_pass.py` and
  `tests/integration/test_the_rules_answer_reaches_the_model.py`.** The last one is the
  one to watch: a rule-written `artifact_type` is a settled level and must arrive at the
  model as a flag, not vanish from the question. `test_branch_situation.py:55` pins the
  two bridge sets equal and goes red if only one was widened.
- [ ] **Step 5: take the number** — `by_field["artifact_type"]`, `by_field["record_type"]`.
- [ ] **Step 6: commit.** `feat(106 Phase 6.2): artifact_type and record_type are produced, routed by the schema the judge named`

### Task 6.3: The model's spelling of a type key is the library's

**Files:**
- Modify: `src/cli.py` — `normalize_for_model` (`:5376`), the `work_type` branch at `:5443`;
  `_work_type_vocabulary` (`:5813`) generalised.
- Test: `tests/p6/test_p6_type_key_routed_by_the_schema.py` (append)

- [ ] **Step 1: the failing test.** Append:

```python
def test_the_models_spelling_of_a_type_key_is_the_librarys(p6_conn):
    """`normalize_for_model`'s promise: "the model's value is canonicalised by the
    SAME rule the deterministic path uses for that field". `work_type` had that
    branch and the other two keys fell to "whitespace collapsed and nothing else",
    so `Poster` and `poster` were two values and would be two folders.
    SABOTAGE: drop the branch."""
    assert cli.normalize_for_model("artifact_type", "  POSTER ") == "poster"
    assert cli.normalize_for_model("record_type", "Bank  Statement") == "bank statement"


def test_a_type_value_the_library_has_not_seen_is_kept_as_the_model_wrote_it():
    """Unchanged behaviour for an unseen value: it is not refused here, because
    `normalize_for_review` answers for three fields and these are not among them
    (`REVIEW_NORMALISED_FIELDS`, an owner decision). Folding members to the library's
    spelling must not start rejecting non-members. SABOTAGE: return `None` on a miss."""
    assert cli.normalize_for_model("artifact_type", "Reading Copy") == "Reading Copy"
```

- [ ] **Step 2: run it.** The first fails: `"POSTER"` comes back as `"POSTER"`.

- [ ] **Step 3: implement.** Generalise the vocabulary builder at `cli.py:5813`:

```python
def _type_key_vocabulary_across_schemas(field_key: str) -> KindVocabulary:
    """The shipped terms of every schema that declares `field_key`. Read once.

    For `work_type` this is what `_work_type_vocabulary` was. For the other two keys
    it is the normaliser's seed only -- the PRODUCER reads one schema at a time
    (`type_key_rule`), and this union exists so a model's spelling of a member can
    be folded to the library's whatever schema authored it: the value is the same
    value either way, which is the argument `WORK_TYPE_VOCABULARY` already makes.
    """
    schemas = json.loads(_RECOGNITION_MANIFEST.read_text())["schemas"]
    return compile_vocabulary(
        term
        for schema_id, fields in DOMAIN_FIELDS.items()
        if field_key in fields
        for term in schemas.get(schema_id, {}).get("work_type_terms", ()))


WORK_TYPE_VOCABULARY = _type_key_vocabulary_across_schemas(WORK_TYPE_FIELD)
ROUTED_TYPE_KEY_VOCABULARY: Mapping[str, KindVocabulary] = MappingProxyType({
    ARTIFACT_TYPE_FIELD: _type_key_vocabulary_across_schemas(ARTIFACT_TYPE_FIELD),
    RECORD_TYPE_FIELD: _type_key_vocabulary_across_schemas(RECORD_TYPE_FIELD),
})
```

(`ARTIFACT_TYPE_FIELD` and `RECORD_TYPE_FIELD` sit beside `WORK_TYPE_FIELD` since Task
6.2, above this point in the file.) Then in `normalize_for_model`, directly after the
`work_type` branch's `return`:

```python
        if field_key in ROUTED_TYPE_KEY_VOCABULARY:
            # `106` Phase 6.3. The other two type keys, held to the same promise as
            # `work_type` above: a member is returned in the LIBRARY's spelling. A
            # non-member is returned as written, which is what this field did before
            # -- `normalize_for_review` answers for three fields and an owner decision
            # keeps it there, so refusing here would end an unseen value's life at
            # `VALUE_NOT_NORMALIZABLE` with nobody shown it.
            return ROUTED_TYPE_KEY_VOCABULARY[field_key].terms.get(
                kind_tokens(text), text)
```

- [ ] **Step 4: run the test file and `tests/test_cli_a_value_the_library_has_not_seen.py`.**
- [ ] **Step 5: commit.** `fix(106 Phase 6.3): a model's artifact_type or record_type is spelled as the library spells it`

### Task 6.4: The one document that names a school is shown to the person

**Ruling:** `106` Phase 6(c), as it can work under the ladder (see the fifth finding at the
top). `_group_level_agreed` (`upstream.py:664`) admits a `user_confirmed` school alone;
`--confirm FILE:FIELD=VALUE` (`cli.py:24128`, `apply_confirmations` `:20300`) writes one;
what is missing is the sentence that tells the person a syllabus named a school and a
second document would have made it a folder.

**Decision the lead must carry to the owner before Step 3:** `REVIEW_NORMALISED_FIELDS`'
comment (`cli.py:5836`) records `school` as excluded *"because opening a field nobody
ruled on would be this file deciding which of a person's values are theirs to name"*.
Phase 6(c) in `106` is that ruling if the owner's "go" on `106` covers it; if not, this
task waits.

**Files:**
- Modify: `src/cli.py` — new `_print_schools_one_document_names` beside
  `_print_values_to_confirm` (`:5945`); one call after it in `_model_fact_pass` (`:18618`).
- Test: `tests/test_cli_one_syllabus_names_a_school.py` (new)

- [ ] **Step 1: the failing test.**

```python
# tests/test_cli_one_syllabus_names_a_school.py
"""`106` Phase 6.4: a school one anchor names is put to the person.

`105` §14.4 makes a school level from two independent anchors in one scope, and
`_group_level_agreed` says what a course with one syllabus gets: "a school on that
syllabus and no school level". Nobody was told. The person's own answer stands alone
under the same rule, and `--confirm` already writes it -- so the whole of this is
the sentence that shows them what the one document said and what to type.
"""
from __future__ import annotations

import io
import json
from pathlib import Path

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from facts.evidence import cite
from facts.file_facts import LLM_INTERPRETATION, RULE, write_fact
from facts.states import LLM_SUPPORTED, USER_CONFIRMED, VALIDATED
from facts.values import VALUE_ORIGINS, ensure_value

import cli

CLOCK = "2026-09-18T00:00:00+00:00"
SYLLABUS = "PHYS 1401 syllabus.pdf"


def _file(conn, tmp_path, name):
    path = tmp_path / name
    path.write_bytes(b"syllabus")
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=8,
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _reading(conn, *, file_id, content_hash, raw):
    record_run(conn, ExtractionRun(
        run_id="run-1", file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location("title", ()), occurrence_count=1,
        observed_at=CLOCK, reliability="possible", run_id="run-1")
    record_observation(conn, observation)
    return observation


def _fact(conn, file_id, content_hash, field_key, value, state, origin, refs=()):
    value_id = ensure_value(conn, field_key=field_key, canonical_value=value,
                            first_evidence_ref=refs[0] if refs else None,
                            origin=VALUE_ORIGINS[0])
    return write_fact(conn, file_id=file_id, content_hash=content_hash,
                      field_key=field_key, value_id=value_id,
                      reliability_state=state, origin=origin,
                      evidence_refs=refs,
                      # The state is in `write_fact`'s identity already; it is in the
                      # key too so two writes of one value at two states cannot be
                      # read as one conclusion by anyone.
                      cache_key=f"t:{file_id}:{field_key}:{state}",
                      active=True)


def _one_syllabus(conn, tmp_path):
    file_id, content_hash = _file(conn, tmp_path, SYLLABUS)
    line = _reading(conn, file_id=file_id, content_hash=content_hash,
                    raw="PHYS 1401 Syllabus - Columbia University, Spring 2026")
    _fact(conn, file_id, content_hash, cli.WORK_TYPE_FIELD, "syllabus",
          VALIDATED, RULE, (cite(line),))
    _fact(conn, file_id, content_hash, "school", "Columbia University",
          LLM_SUPPORTED, LLM_INTERPRETATION, (cite(line),))
    return file_id, content_hash


def test_a_school_one_syllabus_names_is_put_to_the_person(p6_conn, tmp_path):
    """SABOTAGE: print nothing -- the syllabus's school dies at the two-anchor rule
    and the person never learns a single `--confirm` would have built the level."""
    _one_syllabus(p6_conn, tmp_path)
    out = io.StringIO()
    cli._print_schools_one_document_names(p6_conn, out)
    text = out.getvalue()
    assert "Columbia University" in text
    assert f"--confirm '{SYLLABUS}:school=Columbia University'" in text
    assert "Spring 2026" in text, "the line the model read is beside the value"


def test_a_school_on_a_file_that_is_not_an_anchor_is_not_offered(p6_conn, tmp_path):
    """`105` §14.4: only an anchor's own text establishes the relationship.
    SABOTAGE: drop the `work_type` test -- every `school` the model ever wrote off
    a header is offered as a folder, which is `104` §11.1's five essays under a
    high school."""
    file_id, content_hash = _file(p6_conn, tmp_path, "essay.pdf")
    line = _reading(p6_conn, file_id=file_id, content_hash=content_hash,
                    raw="Columbia University essay")
    _fact(p6_conn, file_id, content_hash, cli.WORK_TYPE_FIELD, "essay",
          VALIDATED, RULE, (cite(line),))
    _fact(p6_conn, file_id, content_hash, "school", "Columbia University",
          LLM_SUPPORTED, LLM_INTERPRETATION, (cite(line),))
    out = io.StringIO()
    cli._print_schools_one_document_names(p6_conn, out)
    assert out.getvalue() == ""


def test_a_school_the_person_already_confirmed_is_not_asked_again(p6_conn, tmp_path):
    """`00`:298 -- proposed once. SABOTAGE: read every state."""
    file_id, content_hash = _one_syllabus(p6_conn, tmp_path)
    _fact(p6_conn, file_id, content_hash, "school", "Columbia University",
          USER_CONFIRMED, RULE)
    out = io.StringIO()
    cli._print_schools_one_document_names(p6_conn, out)
    assert out.getvalue() == ""


def test_the_confirm_line_writes_the_answer_the_two_anchor_rule_admits_alone(
        p6_conn, tmp_path):
    """The gesture already exists; this pins that the line the screen prints is the
    line the gesture accepts."""
    file_id, content_hash = _one_syllabus(p6_conn, tmp_path)
    cli.apply_confirmations(
        p6_conn, [f"{SYLLABUS}:school=Columbia University"],
        user_id="owner", observed_at=CLOCK)
    states = {row["reliability_state"] for row in cli.facts_for_file(
        p6_conn, file_id, content_hash) if row["field_key"] == "school" and row["active"]}
    assert USER_CONFIRMED in states
```

`cli.facts_for_file` is `cli.py:136`'s import; `apply_confirmations(conn, confirmations,
*, user_id, observed_at)` is `cli.py:20310`, which the last test calls as written.

- [ ] **Step 2: run it.** → `AttributeError: module 'cli' has no attribute '_print_schools_one_document_names'`.

- [ ] **Step 3: implement.** Beside `_print_values_to_confirm` (`cli.py:5945`):

```python
def _print_schools_one_document_names(conn: sqlite3.Connection, out, *,
                                      show_protected: bool = False) -> None:
    """`106` Phase 6.4: a school ONE anchor names, put to the person.

    `105` §14.4 builds a school level from two independent anchors in one scope, and
    `tree_design.upstream._group_level_agreed` says what a course with one syllabus
    gets: "a school on that syllabus and no school level". The person's own answer
    is admitted alone by that same function, and `--confirm` already writes it. This
    is the sentence between the two: what the one document said, and what to type.

    ANCHORS ONLY, by the file's own settled kind (`SCHOOL_ANCHOR_KINDS`), which is
    the same admission `anchor_only_levels` makes before site A is asked -- a
    `school` the model wrote off an essay's header is not offered, because §14.4's
    reason is that only an anchor's own text establishes the relationship.

    ONE STATE, `llm_supported`: it is the state P8 gives a checked citation and the
    one the two-anchor rule counts. A `possible` school is below the ladder and its
    review path is the owner's open question at `REVIEW_NORMALISED_FIELDS`; a
    stronger one is settled and asks nothing. A file carrying a `user_confirmed`
    school is skipped whatever else it carries (`00`:298, once).
    """
    rows_by_field = versions_in_fields(conn, field_keys=(WORK_TYPE_FIELD, "school"))
    kinds: dict[str, str] = {}
    schools: dict[str, list[sqlite3.Row]] = {}
    confirmed: set[str] = set()
    for rows in rows_by_field.values():
        for row in rows:
            if not row["active"] or row["superseded_by"] is not None:
                continue
            if row["field_key"] == WORK_TYPE_FIELD:
                if strength(row["reliability_state"]) > strength(LLM_SUPPORTED_STATE):
                    kinds[row["file_id"]] = row["canonical_value"]
                continue
            if row["reliability_state"] == USER_CONFIRMED:
                confirmed.add(row["file_id"])
            elif row["reliability_state"] == LLM_SUPPORTED_STATE:
                schools.setdefault(row["file_id"], []).append(row)
    withheld = set() if show_protected else _protected_file_ids(conn)
    offered = [(file_id, rows) for file_id, rows in sorted(schools.items())
               if kinds.get(file_id) in SCHOOL_ANCHOR_KINDS
               and file_id not in confirmed and file_id not in withheld]
    if not offered:
        return
    print("\nA school one document names, waiting on you:", file=out)
    print(_wrapped(
        "A school becomes a folder when two independent documents of a course agree "
        "on it, or when you say so. Each line below is one document naming one "
        "school and no second document to agree with it. Nothing is filed under a "
        "school until it is confirmed.", indent="  "), file=out)
    for file_id, rows in offered:
        filename = get_file(conn, file_id)["filename"]
        for row in rows:
            cited = evidence_chain(conn, fact_id=row["fact_id"])
            print(f"\n  {filename} ({kinds[file_id]}) names "
                  f"{row['canonical_value']!r}", file=out)
            if cited:
                print(_wrapped(f"the line it read: {cited[0].raw_value}",
                               indent="    "), file=out)
            print(f"    --confirm '{filename}:school={row['canonical_value']}'",
                  file=out)
```

`versions_in_fields` and `evidence_chain` (`cli.py:133-134`), `strength`,
`LLM_SUPPORTED_STATE` and `USER_CONFIRMED` (`cli.py:137-144`), `_protected_file_ids`
(`:12935`), `get_file` and `_wrapped` (`:21262`) are already in `cli.py`'s namespace;
`versions_in_fields`' rows carry `fact_id`, `file_id`, `canonical_value`,
`reliability_state`, `active` and `superseded_by` (`read_surface.py:257`). Then one call
in `_model_fact_pass`, directly after `_print_values_to_confirm(...)` at `:18618`:

```python
        _print_schools_one_document_names(conn, out, show_protected=show_protected)
```

- [ ] **Step 4: run the test file, `tests/test_cli_a_value_the_library_has_not_seen.py`,
  `tests/p10/test_p10_school_two_anchors.py`.** The P10 file must be untouched by this:
  no rule at P10 changes, one syllabus still makes no level.
- [ ] **Step 5: commit.** `feat(106 Phase 6.4): a school one syllabus names is put to the person, whose word the two-anchor rule already admits alone`

### Then

- [ ] Run the chunked suite on a quiet machine (never beside a corpus run).
- [ ] `graphify update .`
- [ ] The lead re-runs the owner's corpus and takes `level_reach` again — that is §E.

---

## E. The gate

`106` says "the 221 drops". Sharpened into one number the instrument in Task 6.0 prints:

> **`level_reach.reached` on the owner's corpus rises from its Task 6.0 baseline, and the
> rise is at least the number of files that carry a `DateTimeOriginal` observation and
> a `photos.*` situation** — a number known BEFORE the phase runs, from the run's own
> database:

```sql
-- `evidence.location` is the serialised locator (`evidence_shape/locator.py:134`):
-- zone, ':', then `kind=label` segments -- `metadata:field=DateTimeOriginal`.
select count(distinct e.file_id)
from evidence e
join file_facts ff on ff.file_id = e.file_id and ff.content_hash = e.content_hash
join "values" v on v.value_id = ff.value_id
where e.superseded_by is null
  and e.location like 'metadata:field=DateTimeOriginal%'
  and ff.field_key = 'situation' and ff.active = 1 and ff.superseded_by is null
  and v.canonical_value like 'photos.%';
```

That is the falsifiable half: it is known in advance and Task 6.1 either delivers every
one of those files as `by_field["capture_year"]` or it does not. The second half is
reported, not promised: `by_field["artifact_type"]` and `by_field["record_type"]` on the
same database, with the `unresolved` query's `no_candidate_evidence` count for those two
keys beside it, so the ceiling of a naming-zone rule on this corpus is a measured number
and not an estimate.

**And the Phase 1 grouping number is taken again after 6.1 and 6.2.** `grouping/seeds.py:49`
seeds a group on any `direct` or `validated` fact, field-independent, so every
`capture_year`, `artifact_type` and `record_type` this phase writes is a new seed. The
plan judges every phase against the gates before it; `group_cohesion` on the same
database is the check that new seeds joined photographs by year and did not split a
course.

What the gate must NOT count, and the tests in Task 6.0 pin: `file_type`, a `possible`
proposal, a level of another situation, a file with no situation.

What this phase will not move, said on the screen (`106`, "What this plan does not
claim"): the 87 files the gate refused; `research.*`'s `project` on a flat folder;
`event`.

---

## F. What this must not break, and the tests that pin each

| rule | why this phase touches it | pin |
| --- | --- | --- |
| Amendment 9 — the situation is never a folder level | Task 6.0 reads the `situation` fact to find a file's levels; it must never count it as one | `tests/p6/test_p6_fields.py:44-46` (both situation keys `destination_eligible=False`); `tests/integration/test_template_levels_wiring.py:439` (`test_the_model_is_never_offered_a_field_that_cannot_become_a_folder`); Task 6.0's `test_a_file_type_fact_reaches_nothing` reads eligibility off the `fields` table, which is where amendment 9 is written down |
| Privacy routing — protected material reaches the local model only, never the cloud | Task 6.1 cites an EXIF observation (signalled sensitive); Task 6.2 adds a stage to the model pass's resolver | `tests/integration/test_per_file_model_route.py:188`; `tests/integration/test_local_model_fact_pass.py:790` (`test_a_protected_file_is_asked_of_no_model_and_its_route_stays_local`); `tests/p7/test_p7_release.py:1058`. The EXIF slot writes a fact on this machine and releases nothing: `direct_facts` sends nothing, and the fact's value (`2024`) reaches a model only as a flag naming the field (`test_the_flag_carries_no_value_and_no_identifier_in_the_clear`, `tests/integration/test_the_rules_answer_reaches_the_model.py:346`) |
| `PROPOSAL_ELIGIBLE_STATES` — `possible` never becomes a folder | Task 6.4 exists because of it; Task 6.0 filters on it | `tests/p6/test_p6_read_surface.py:186-187`; `tests/p10/test_p10_unanchored_single_value.py:166` (`test_a_lone_model_supported_value_with_no_anchor_builds_no_level`); Task 6.0's `test_a_possible_fact_reaches_nothing` |
| `00`:11.2 step 2 / amendment 15 — `school` is never asked of one file | Task 6.4 shows a school; it must not ask one | `tests/integration/test_local_model_fact_pass.py:722` (`test_site_a_is_never_asked_the_school_of_one_file`); `tests/p6/test_p6_no_situation_arm_withholds_group_levels.py`; `tests/p10/test_p10_school_two_anchors.py:162` (`test_one_syllabus_alone_makes_no_level`) — Task 6.4 changes nothing at P10 and that test must stay green |
| H6.2 / H6.3 — one type key per file, chosen by the schema, never the union | Task 6.2 | `tests/p6/test_p6_kind.py:481` (`test_the_vocabularies_of_the_three_type_keys_are_nearly_disjoint`); Task 6.2's own `test_a_schema_that_declares_work_type_routes_no_second_key` |
| §3.5 — dates from text are never `direct` | Task 6.1 adds a direct slot | `tests/p6/test_p6_subject_slot.py` (the text-slot guard); the slot's `names` predicate is a `metadata:` locator and cannot match a text zone |
| A what-kind fact reaches no schema and anchors no move on its own; a group seed is field-independent | Tasks 6.1 and 6.2 write `validated`/`direct` facts, which `_schema_reached_by_the_facts` (`cli.py:6326`), `partition_by_branch` (`branch_situation.py:409`) and `grouping/seeds.py:49` all read | `tests/test_branch_situation.py:55` (the two bridge sets are one set); Task 6.2's `test_a_type_key_carries_no_file_into_a_branch_and_anchors_no_move`; `tests/integration/test_p9_active_schema_slot_retired.py:106` (a run still forms the same group); the Phase 1 `group_cohesion` number re-taken (§E) |

---

## G. Owner items this draft raises (not tasks)

1. **`project` on a flat folder.** The first level of 77 situations and of 6 of 8
   `research.*` rows. No producer in this product can answer it from a paper's own text;
   the folder path answers it where the person has folders (and is released to every
   target, `privacy/vocabulary.py:294`). On a flat Downloads it is the group stage's
   name or the person's. This belongs with Phase 4/5, not 6, and the depth of every
   research branch is bounded by it whatever Phase 6 does.
2. **`event`.** `photo_events` needs `same_event` and `minimum_members` — a time window,
   a GPS radius, a camera-identity test. The owner's numbers; nothing to build until
   they exist.
3. **`106` item (b)** — rejected in §C; if wanted, the compromise is the filename guard.
4. **Glossary rows** (library text; new versioned rows, never edits): `artifact_type`'s
   sentence is `"if it is an OUTPUT OF A MAKING PROCESS -> artifact_type"` and
   `record_type`'s is a fragment of the same discriminator — neither reads as a
   definition of the field to a model that has never seen `work_type`'s half of it. A
   rule for the two keys beside v5's rules 12-14, which are academic-only, is the same
   kind of row. Measured by replay before ratification, as texts 5-11 were.
5. **`REVIEW_NORMALISED_FIELDS`** — whether `artifact_type`, `record_type` (Task 6.3's
   non-member case) and `school` (Task 6.4) join the review screen's read is recorded
   at `cli.py:5836` as the owner's decision.

---

## Contradictions with the brief, for the lead

- "The template says a coursework file's folders are built from `institution / term /
  subject`" — it says `school(G) / term / subject / work_type`. `institution` is finance's.
- "There is nothing to write in the folders" is true and the reason is not that `subject`
  reaches 35 files; it is that `capture_year`, `artifact_type`, `record_type`, `project`
  and `stage` reach 0, 6, 0, 6 and 0, and those are the levels.
- "The one fact that reaches nearly everything is a file format" — its origin is not
  determinable from the code (no deterministic writer exists); query 1 of §A.0 says
  whether it is the flat arm, and on which run.
- `106` (a) is not ~5 lines and (c) cannot land at `possible`; both re-shaped above.

---

# Phase 7 — DEPTH, FLATTEN, AND RESIDUAL HOMES (draft for `106`)

> Drafted 17 Sep 2026 against `build/p6-p7-first-packages` at `19d39aa3`. Every
> `file.py:line` below was read with `cat -n` on that tip, not recalled. Nothing
> here has been executed; no file outside this draft was written.
>
> **Two things in this draft contradict the Phase 7 sketch in `106`, and they
> are stated up front.** (1) The sketch's `max_useful_depth` authored into
> `definitions.json` is a number the design does not state, and the package
> already refuses exactly that: `config.py:2-28` ("No number lives here"),
> `tests/p10/test_p10_no_invention.py:176-195` (no integer literal but 0 and 1
> anywhere in `tree_design/`). Depth is already uneven from facts
> (`materialise.py:119`); what is missing is two collapses at the projection
> seam, and they supersede the authored number rather than sit beside it. (2)
> The single-file root is not a `tree_design/` defect. It is produced at the
> composition root (`cli.py:16120-16182`) and by P3's inventory
> (`traversal.py:117-135`), and one of its three producers is a protected
> bundle that must stay at the root by the standing rule.

---

## A. What depth should be, and why uneven is correct

**The design's own words.** `00`:98: *"The canvas must support uneven depth
because real file trees are not and should not be perfectly symmetrical. One
branch may require four levels, while another should remain flat.
`Academics/Columbia/2026-Spring/PHYS1401/Homework` may be useful because it
contains many files with strong facts. `Academics/Georgetown Prep` may remain
shallow because it contains only a handful of files. `Applications/UChicago/2026`
may split into essays, forms, and supporting materials, while a two-file
application packet may remain a single folder."* `00`:95: *"a parent dimension
should provide the context required to understand the child."* `00`:99: *"warn
when a level produces only one child ... It should recommend flattening when a
dimension does not materially improve retrieval."*

**What decides depth today, and it is already fact-driven.** A level exists in
a branch only where its values DIVIDE the branch's files — `LevelEvidence.divides`
is `len(self.values) > 1` (`materialise.py:93-119`), a value one file offers on a
model's word alone is struck before that (`_unanchored_single_values`,
`materialise.py:337-385`), and `_project` nests children by SHARED FILES
(`materialise.py:645-763`): a value becomes a child of a parent value only when
the same files carry both, a level with nothing to say under a parent is skipped
and the next level tried (`:735-763`), and a date level wider than the proposal
ceiling is coarsened to a prefix of its own value (`narrow_wide_date_levels`,
`:801-843`). So a branch whose files carry `institution / term / subject` gets
three levels and a branch whose files carry `subject` alone gets one. That is
`00`:98's unevenness, and it is why the plan's own measurement table explains
the flat tree: `subject` on 35 of 371 files and `institution` on 17 means there
is nothing for the levels to divide (`104`:2785-2800). **Phase 6 raises the
numbers. Phase 7 does not, and must not claim to.**

**The rule, stated so it holds before and after Phase 6.** A folder level
exists under a parent exactly where it SEPARATES that parent's files:

1. It yields more than one child — otherwise the person opens a folder to find
   one folder (`00`:97, `00`:99). *Exception that the design itself names:* a
   run of single children is kept when something beneath it divides, because
   each supplies the context the child needs (`00`:95; `00`:78's own path
   `Academics/Columbia/2026-Spring/PHYS1401/{Homework, Lectures, Syllabus}` is
   three single-child levels over a level that divides — `health.py:303-311`
   already reasons exactly this for `WARN_ONE_CHILD`).
2. It yields fewer children than the files it would file — a folder per file
   separates nothing a filename does not already separate (`00`:98's "a
   two-file application packet may remain a single folder").

Both bounds are the two degenerate ends of a partition, not tuned numbers: one
part, or as many parts as elements. Neither needs an integer literal above 1,
which is what keeps them inside `test_p10_no_invention`'s rule.

**Why "one value for every file" and "a distinct value per file" are both
noise**, in the product's own terms. The tree is a destination index a fact
reaches (`00`:110; `branch_expectations`, `materialise.py:445-490`). A level
whose one value every file shares adds no `ExpectedValue` a file could fail to
match — it discriminates nothing and costs a click. A level with one file per
value adds one folder per `ExpectedValue`, which is the filename restated as a
directory: retrieval by fact already reaches the parent, and the folder adds a
name the person must open to see one thing.

**The seam that applies the rule.** `materialise._project` (`:645-763`) is where
a level becomes nodes under one parent, and `project_branch_preview`
(`:591-642`) is where the walk's product becomes the preview every count,
warning and sentence reads (`candidates.py:570-574`: "the preview, the counts
and §5.9 all read the SAME evidence afterwards, so no number the user sees can
disagree with the tree beside it"). Rule 2 belongs in `_project` at the moment
the children of one parent are known; rule 1's chain fold belongs in
`project_branch_preview` after the walk, because "nothing beneath divides" is a
fact about a subtree the walk has not finished when it visits the top of the
chain. `_TreeIndex.divides_below` (`health.py:156-162`) is already that measure,
computed post-order, and is reused rather than restated.

**Where the rule must NOT reach.** The branch root. Under a built node, a file
whose level is folded stays reachable: the node's `expected_values` chain
(`materialise.py:697-698, 721`) is what the placement index matches, and a fold
appends the folded value to that chain (section B). At the ROOT there is no
chain to append to when the children differ (rule 2 at the root: three one-file
courses under `Coursework`), and a branch that states no value is one P11's
direct-fact channel cannot reach — the cost `104` Q-H measured for
`keep-as-it-is` (`candidates.py:640-660`). So rule 2 is applied only beneath a
built node; at the root the folder-per-file split stays and `WARN_TINY_FOLDERS`
(`health.py:388-401`) speaks, as it does today. Rule 1 at the root is already
the existing `divides` test — a value every file shares is never a level, and
`branch_expectations` states it on the branch (`materialise.py:629-638`).

**What this supersedes.** `106` Phase 7(a)'s `max_useful_depth` on
`TemplateDefinition` (`templates.py:292-330` has no such field) is not built.
Depth per branch is what the facts divide, bounded above by `_v3`'s
`tree.max_depth` (`validation.py:145-166`) which the design leaves configured,
not authored.

---

## B. The flatten rule

Two collapses, both in the projection, both said to the person.

### B.1 Folder-per-file under a built node (rule 2)

**Precisely.** In `_project`, for a level `L` under a parent node `P` with
eligible member set `E`: compute the children `C = {(v, m_v)}` where
`m_v = members_by_value[v] & E` is non-empty and `m_v` is not carried by
protected material alone (the existing skip at `materialise.py:666-689`). If
`len(C) > 1` and every `m_v` has exactly one member, no child is built at `L`
for `P`: the walk falls through to level `L+1` with `E` unchanged, exactly as
the `ordinal == 0` skip already does (`:735-763`). The files stay members of
`P` (`members_out[P]` was set when `P` was built, `:725`).

**Only beneath a built node.** `P` must be a node the walk minted (`level_index
> 0` and `parent` is not the branch's own node). At the root the split is kept
(section A, last paragraph).

**Consequences checked against the record.** `unsupported_levels` stays empty
for a file placed on `P`: `_levels_not_filled` (`placement/pipeline.py:299-329`)
fills it only from a deeper leaf the rules built and the model struck, and no
leaf was built — so no scoped General is demanded by a fold
(`versions.py:291-301`). `_nesting_key` (`cli.py:11298-11309`) reads
`resulting_child_counts`, which stays every level's distinct-value count
(`candidates.py:600-606` explains why that dict may not change); only the
sentence and the built tree change.

### B.2 A run of single children that never divides (rule 1)

**Precisely.** After `_project` returns, in `project_branch_preview`: for each
built node `T` with exactly one child `c1`, where `members[c1] == members[T]`
(every file under `T` carries `c1`'s value), follow the chain
`c1 → c2 → … → ck` while each has exactly one child holding all of its parent's
files; if `ck` has no children (nothing beneath the run divides — the walk
built nothing below because rule 2 or `ordinal == 0` left it empty), remove
`c1..ck` from `nodes` and `members_by_node`, and append their `ExpectedValue`s
to `T.expected_values` in chain order. A file's fact still reaches `T`
directly (`00`:110), and the next term's file under the same school would
divide the level and un-fold it on the next run, which is the re-run this
product already makes for every edit.

**Why `members[c1] == members[T]`.** A single child holding a strict subset IS
a division — the files with the value and the files without — and folding it
would make `T` claim a value some of its files do not carry. That case stays a
folder plus loose files, and `WARN_ONE_CHILD` (`health.py:345-361`) is the
advice about it.

**Why not at the root.** A branch root with one child holding everything cannot
occur through `divides` (that level is not built); the one route is the
protected-only skip at `:666-689` leaving a single sibling, and there
`branch_expectations` (`:629-638`) already speaks. Left alone.

### B.3 What the person is told

Silence here is the product deciding something and not saying so. Three
carriers, all existing:

1. **The option's sentence** (`candidates.py:598-612`). Today it is composed
   from `_summarise(counts)` over `child_counts`, which counts a level's
   distinct values whether or not the walk built them — after B.1/B.2 it would
   promise "3 work_type" and build none. It becomes: the counts of what was
   BUILT (`Counter(node.dimension_role for node in built.nodes)`), followed by
   one clause per fold — *"kind of work was not made a folder under PHYS1401:
   each of its 3 files would have had a folder of its own"* / *"term 2024-Fall
   and course ENG101 were not made folders under Georgetown Prep: every file
   there carries both, so each would be a folder you open to find one folder."*
   `BranchPreview` gains `folded: tuple[FoldedLevel, ...]` to carry the fact
   as data; the sentence is composed once, in `vertical_options`.
2. **The node's explanation** (`Node.explanation`, `records.py:155`; §5.12 makes
   it mandatory). `T`'s explanation gains the same clause, so the frozen tree
   carries the reason and P13's canvas can show it.
3. **The outline** (`structure_rows`, `cli.py:22380-22429`). The row's `words`
   gains the folded values, read off `expected_values` beyond the node's own
   dimension — *"also every file's term 2024-Fall and course ENG101"* — so a
   person editing the file sees what is inside the folder without a level for
   it. `_node_claim` (`cli.py:22334-22341`) reads `expected[-1]` as the
   folder's own claim; with folded values appended it must read the value of
   the node's own `dimension` instead (Task 7.4).

**Where it belongs.** `src/tree_design/materialise.py` (both rules and
`FoldedLevel`), `src/tree_design/candidates.py` (the sentence), `src/cli.py`
(the outline). `validation._v2` (`validation.py:112-142`) stays as it is: its
`len(level.values) == 1` branch at `:131-133` is unreachable after `not
level.divides: continue`, which its own comment records as deliberate — the
one-child rule lives in `divides`, not in V2, and this phase does not move it.

### B.4 The flatten RECOMMENDATION gets its measure

`cli.py:634` supplies `materially_improves_retrieval=lambda option: True`, so
`RECOMMEND_FLATTEN` (`health.py:403-412`) has never fired on a real run, and
`tests/p10/test_p10_health.py:616-663` is the strict xfail that names the
carrier: a field containing "retrieval" on `BranchCounts` (`health.py:56-66`).
The measure is rule 2 read off a tree the projection did not fold — the
person's own adopted folders, whose children the walk never touched, and any
earlier version: `BranchCounts.retrieval_partition: tuple[int, ...]`, the
member counts of this node's children, sorted descending; and
`health.separates_files(counts) -> bool | None`: `None` for a node with no
children (nothing to judge), `False` when the partition is one part or every
part is one file, `True` otherwise. `cli.py:634` passes `separates_files`. The
xfail marker comes off in the same task or the suite goes red (it is
`strict=True`). Rule 1's warning is already `WARN_ONE_CHILD`; nothing is added
for it.

---

## C. A single file must never become a top-level folder

**The lead's measurement:** seven roots, five of them `label=schema_id`
(`branch_situation.py:464-469`, Phase 3's), one a directory card, one a single
file's own name. **Three producers write a node with `parent_node_id=None`, and
`_outline_walk` (`cli.py:22320-22331`) prints every one of them as a top-level
folder.** Traced:

**Producer 1 — the drafted group per branch.** `accept_groups`
(`cli.py:16282-16316`) drafts ONE merged group per `Branch` through
`draft_for_review` (`cli.py:10787-10913`) and `_grouped_by_branch`
(`:10916-10957`), labelled `branch.label`; the merged id goes into
`branch_group_ids` (`cli.py:16200`) and becomes a `proposed` root through
`horizontal_candidates` (`candidates.py:300-346`) and `_top_level_node`
(`pipeline.py:637-694`). Its label is a schema id or the person's `--label`
(`cli.py:17835-17841`); it cannot be a filename. Not this producer.

**Producer 2 — every directory the scan read.** `adopted_folders`
(`cli.py:16120-16182`) offers EVERY row of `directory_inventory` whose
`parent_directory` is not null, that is not inside a protected container, and
not inside a candidate root — with NO floor on what the directory holds
(`:16171-16182`). `horizontal_candidates` builds one card per folder
(`candidates.py:348-371`, label = last path segment, `folder_label`
`:169-182`), `design_tree` keeps it because its `subject_id` is in
`branch_group_ids` (`pipeline.py:838-839`), and `_top_level_node` writes it as
an `existing` root unless its parent directory was adopted too
(`_adopted_parent_id`, `pipeline.py:785-811`). Two shapes reach the root this
way, and both are "a file's own name":

* *A one-file wrapper directory.* Browsers and Finder's unzip make
  `foo/foo.pdf`; the directory is named after the file. `104` R-87 (`:787`)
  already ruled an adopted folder of one file claims NO expectation ("an
  adopted folder of one file claims nothing; an expected value needs the
  folder's name or two or more files that agree"), but it is still adopted as a
  root: R-87 fixed what the node CLAIMS, not whether it EXISTS.
* *A macOS package.* `.rtfd` is a directory on disk, and `.pages`,
  `.numbers`, `.key` may be (they are packages by option; nothing here can
  check which the corpus holds — the counts query below can).
  `traversal.py:117-125` enqueues every non-excluded directory and
  `record_directory` writes it (`inventory.py:73-85`); the only bundle rule is
  `PROTECTED_BUNDLE_SUFFIXES = (".app",)` (`exclusion.py:121`), so a `.pages`
  package is walked, its innards become `files` rows, and the package is a
  directory the tree adopts under the file's own name. This is a P3 fact, not a
  tree fact; it is named here so the lead can tell the two apart.

**Producer 3 — a protected container, at the root by design.**
`represent_protected_areas` (`freeze.py:261-288`, called at
`pipeline.py:901-905`) writes one `protected` node per area P3 marked, with
`parent_node_id=None` (`candidates.py:240`) and the bundle's display name. A
`.app` in Downloads is a "file" to the person and a root to the outline. It
MUST stay: marked, counted, never opened, never silently omitted
(`candidates.py:193-223`). What it must not do is read as a folder of the
plan — today `structure_rows` prints "0 files" beside it (`cli.py:22414-22415`,
`under()` finds no decision) and nothing says it is protected.

**Which of the three is the one on the owner's corpus** is a counts-only query
the lead can run on the latest plan version (aggregates; no path printed):

```sql
-- roots by producer, latest version
WITH v AS (SELECT plan_version_id FROM plan_versions ORDER BY created_at DESC LIMIT 1)
SELECT n.node_type,
       COUNT(*)                                          AS roots,
       SUM(CASE WHEN d.file_count = 1 AND d.subdirectory_count = 0 THEN 1 ELSE 0 END) AS one_file_no_subdir,
       SUM(CASE WHEN lower(n.display_label) LIKE '%.pages'   OR lower(n.display_label) LIKE '%.numbers'
                  OR lower(n.display_label) LIKE '%.key'     OR lower(n.display_label) LIKE '%.rtfd'
                  OR lower(n.display_label) LIKE '%.app' THEN 1 ELSE 0 END)            AS bundle_shaped
FROM tree_nodes n
JOIN v ON n.plan_version_id = v.plan_version_id
LEFT JOIN directory_inventory d ON d.directory_path = n.existing_path
WHERE n.parent_node_id IS NULL
GROUP BY n.node_type;
```

`one_file_no_subdir > 0` under `existing` is the wrapper; `bundle_shaped > 0`
under `existing` is a package; under `protected` it is producer 3.

**The rule.** *An existing directory becomes a top-level branch only when the
scan saw it as a place the person keeps files: it holds two or more files
directly, or it holds a subdirectory. A directory holding exactly one file and
nothing else is not offered as a branch.* No threshold is invented: "one" is
the same bar R-87 already set for what such a folder may claim, applied to
whether it is a branch at all. The file inside it is still in the roster,
still placed by its own facts (or held and shown in a review set), and the
directory is left where it is — the product moves nothing it did not propose.
The report says so once, as a count: *"N folders holding a single file were
left as they are and not made branches."* A package is the same rule seen from
the scan's side and is Phase 7's to name, not to fix: recording a package as
one FILE is a change to `traversal.py` and to what `files` holds, which is P3's
seam and the owner's call (a `.pages` is one document; its `Index.zip` is not a
file anyone files). Producer 3 is a presentation fix: the outline row says
*"protected: marked and counted, never opened, not a folder of this plan"*
instead of "0 files".

**Where it belongs.** `ExistingFolder` (`upstream.py:83-87`) gains
`subdirectory_count`, read from the inventory row it already reads
(`upstream.py:258-263`; the column exists, `inventory.py:64`);
`candidates.keeps_files(folder)` is the predicate; `cli.adopted_folders()`
applies it beside its three existing filters. Producer 2 is fixed in the
composition root because that is where `branch_group_ids` is chosen — the same
reasoning `adopted_folders`'s own docstring gives for the candidate-root
exclusion (`cli.py:16138-16148`: "a rule about what may be built, so it is
enforced where branches are chosen").

---

## D. Residual homes

**What the product does today with material that matched nothing.** After
placement, `run_corpus` hands every unplaced file and every policy-held
placement to `surface_residual_sets` (`placement/pipeline.py:5240-5256`;
`placement/residual.py:161-244`), which refuses a partition that drops a file
(`:195-204`). The partition is `cli.residual_partition` (`cli.py:16910-17053`),
keyed by the decision's own reason (`REVIEW_SET_REASONS`, `cli.py:15012`) and,
for `no_supported_destination` only, by three of `00`'s characteristics
(`REVIEW_SET_CHARACTERISTICS`, `cli.py:15168-15176`: screenshots, standalone
PDFs and forms, spreadsheets and presentations; `REFINED_BY_CHARACTERISTIC`,
`:15166`). Each set is a `ResidualSet` (`residual.py:74-108`) with a label, a
count, examples, a reason. **And then it has nowhere to go.** No residual area
exists unless the person typed `--residual` (`cli.py:16184-16189`:
`residual_library = ... if residuals or library_actions else {}`), so the
screen prints each set under `Held for review as "<label>": <reason>`
(`_review_note`, `cli.py:21750-21930`), offers `--leave-set` and `--review-set`
(`:21890-21891`), offers `--send-set` only `if areas:` (`:21887-21889`), and
closes with *"This plan has nowhere to put them yet: enable an area with
`--residual "Review Later"`"* (`:21903-21907`). That closing sentence is the
"flag the person must type" the Phase 7 gate names. On the plan's corpus the
majority of files are in this state (221 of 371 carry no destination-eligible
fact).

**The design's promise and the owner's amendment.** `00`:118-121: residual
templates are "safe, intentionally broad destinations"; the library "prevents
the LLM from creating arbitrary folders"; the templates "are not automatically
created" and the person decides each one's disposition — physical, review-only,
or leave in place. Amendment 13 (`00`:366) qualifies `00`:99: the catch-all
"may not be the product's DEFAULT ANSWER ... but it MUST exist, be typed, and
be visible at the root", as `98 Review and Unsorted` and `99 Archive`, with
"the sets inside `98` characteristic and named (screenshots, standalone PDFs,
unsupported or encrypted, possible duplicates, deferred decisions), and every
one is offered to the person before anything moves." Amendment 14 (`00`:370)
ratifies site D so a leftover can be decided one file at a time.

**The offer, designed.**

1. **Two roots, from the owner's closed vocabulary.** `98 Review and Unsorted`
   and `99 Archive` join `tree_design/vocabulary.py` beside §7.3's nine names
   (`:286-296`) — the same footing: fixed by the owner, spelled once. `98` is a
   `proposed` node of `node_role=ordinary` at the root; `99 Archive` is a
   residual home in its own right (a user-defined `ResidualTemplate`,
   `user_defined=True`, built the way `--define-residual` already builds one at
   `cli.py:5060-5075`, treatment `retained`).
2. **Inside `98`, §7.3's own nine — not new names.** `RESIDUAL_DEFAULT_PARENTS`
   (`vocabulary.py:300-305`) puts four of them under `Photos` and `Personal`;
   amendment 13 relocates them under `98`. No template is authored and no slot
   is edited: `ResidualChoice.parent_node_id` (`residuals.py:316`) already
   nests a home under a named node.
3. **A suggestion table, set → home** (`cli.REVIEW_HOME_FOR_SET`), read off
   the set's KEY, which `ResidualSet` gains as a defaulted field so the payload
   round-trips (`residual.py:129-130` is `asdict`; a missing key on an older
   row reads as the default):

   | set key (`cli.py:15000-15176`) | offered home |
   | --- | --- |
   | `SCREENSHOT_REVIEW_SET` | `98 / Temporary Screenshots` |
   | `STANDALONE_PDF_REVIEW_SET` | `98 / Independent Records` |
   | `SPREADSHEET_REVIEW_SET` | `98 / Review Later` |
   | `pv.NO_SUPPORTED_DESTINATION` (the rest) | `98 / Review Later` |
   | `pv.MULTIPLE_SUPPORTED_HOMES`, `pv.LOW_MARGIN` (deferred decisions) | `98 / Review Later` |
   | `WAITING_ON_AN_ANSWER`, `pv.SITUATION_UNANSWERED`, `pv.BUDGET_DEFERRED` | none — a question the report prints, a branch whose situation is not yet answered, a run that stopped short: a branch may still hold these once answered or resumed, and amendment 13 sends a file to `98` only when no branch can |
   | `UNSUPPORTED_REVIEW_SET` (new, from `locked_reasons`, `cli.py:13337`) | `98 / Unsupported or Encrypted` |
   | `DUPLICATES_REVIEW_SET` (new, from `duplicate_family` / `version_family` facts, `families.py:59-60`) | `99 Archive` |
   | `NOT_YET_CLASSIFIED`, `NO_MODEL_ALLOWED`, `NOT_ALLOWED_TO_CROSS`, `PROTECTED_REVIEW_SET` | none — these are blocks, not leftovers; the existing sentence stands |

4. **Minted on demand, after placement — the General's precedent.** The tree
   freezes before placement (`STEPS`, `pipeline.py:84-96`) and the sets exist
   only after it, so "auto-enabled when non-empty" can only follow
   `mint_generals_on_demand` (`cli.py:15349-15425`, called at `:19365`, FIRST
   among the things after the run): open a draft from the frozen version
   (`store.open_draft`, `:326-356`), write `98`, its needed homes and `99`,
   freeze again, `build_destination_index`, `carry_onto` every decision
   (`versions.py:312-337`). A run with no ordinary set writes nothing — the
   same "nothing happens when nothing is demanded" as `:15364-15367`.
   **Verified handoff:** `act_on_residual_sets` records the decision with
   `plan_version=inputs.plan_version` (the post-mint version) and the set's own
   `set_id` (`placement/pipeline.py:5517-5523`), and `require_set_decision`
   reads the same pair (`residual.py:384-400`); `approved_residual_area` reads
   the post-mint index (`:5386-5388`). The General already exercises this
   ordering on every run that mints one.
5. **The screen offers, the person decides, nothing moves.** Under every
   ordinary set `_review_note` prints the offered home and the exact
   `--send-set "<label>=<home>"` line (today's `areas[0]` becomes the table's
   answer for that set), keeps `--leave-set` and `--review-set`, and the
   closing sentence stops saying there is nowhere. **Disposition — the
   decision point.** Five of the nine shipped treatments are `reviewed`
   (`residuals.json`; `_DISPOSITION_BY_TREATMENT`, `residuals.py:101-105`) →
   `review-only` → `mutation/plan.py:189-199` refuses the write at apply, and
   Phase 1.3's `placement_words` (`cli.py`, commit `374ce253`) then says
   "gathered under {where} without being moved". Amendment 13 says files go to
   `98` once offered and accepted. **Recommendation:** the on-demand homes
   under `98` carry `physical-destination` under amendment 13 as the owner's
   own ruling, exactly as `cli.py:16256-16261` picks `MANDATORY_REVIEW` under
   §6.9's rule; every filing into them is `REVIEW_REQUIRED` regardless, because
   `run_residual_file` passes `unique_direct_match=False`
   (`placement/pipeline.py:4833-4837`; `review_policy_for`,
   `privacy.py:334-346`), so nothing moves before `--freeze` and `--apply`.
   This overrides an authored slot for the auto-enabled copies only; a home
   the person enables by `--residual` keeps its authored treatment. **The lead
   should put this one line to the owner before Task 7.9 is built.** If the
   owner keeps `reviewed`, Task 7.9 passes `disposition_for_treatment(...)`
   instead and the screen keeps Phase 1.3's honest words — the design still
   holds, and `98` is then a review queue rather than a destination.
6. **Per file (amendment 14).** `--review-set` runs site D per file once its
   text is ratified (Phase 0.2; `residual_judgement_available`,
   `placement/pipeline.py:5345-5361`), and a file the person disagrees with is
   `--reject`ed by name (the gesture the deleted-line edit already uses,
   `tests/integration/test_the_editable_structure.py:268`). No new per-file
   gesture is built.

**What does not regress.** `review-only` and `leave-in-place` still move
nothing (`moves_files`, `privacy.py:259`); the report's headline still asks
`placement_words(policy, disposition=...)`; a protected set still gets no
command (`cli.py:21870-21880`) and no offer.

---

## E. Phase 7's task list

TDD order throughout: write the test, run it and watch it fail FOR THE STATED
REASON, implement, run it and the named files, commit. `nice -n 15`, `-p
no:randomly`, targeted files, one builder at a time on this machine. No task
touches `src/llm_harness/library/**`, `src/privacy/**` or
`src/tree_design/library/residuals.json`.

### Task 7.1: The flatten recommendation gets a measure it can read

**Files:** Modify `src/tree_design/health.py` (`BranchCounts`, `branch_counts`,
new `separates_files`) · Modify `src/tree_design/candidates.py:463-498`
(`_counts_for_preview` hands the children's members over) · Modify
`src/cli.py:634` · Test `tests/p10/test_p10_health.py` (new tests; the strict
xfail at `:616-663` comes OFF in this task, because adding the field makes it
XPASS and a strict XPASS fails the suite).

- [ ] **Step 1: Write the failing tests** at the end of `tests/p10/test_p10_health.py`:

```python
# --- `106` Phase 7 §B.4: the retrieval measure `00`:99 states no number for -----

from tree_design.health import separates_files  # noqa: E402


def _counts_with_children(nodes, members_by_node):
    return {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node=members_by_node,
        unresolved_by_node={}, evidence_gaps_by_node={},
        sensitive_node_ids=frozenset()) for n in nodes}


def test_branch_counts_carry_the_partition_a_level_makes_of_its_files():
    """The carrier `test_the_flatten_rule_has_a_measure_to_read` named: a field
    about RETRIEVAL on `BranchCounts`. It is the member count of each child,
    largest first -- what a person would see on opening this folder."""
    nodes = (_node("n_root", None, "Academics"),
             _node("n_a", "n_root", "PHYS1401"),
             _node("n_b", "n_root", "CHEM1101"))
    counts = _counts_with_children(nodes, {
        "n_root": ("f1", "f2", "f3"), "n_a": ("f1", "f2"), "n_b": ("f3",)})
    assert counts["n_root"].retrieval_partition == (2, 1)
    assert counts["n_a"].retrieval_partition == ()


def test_a_level_with_one_folder_per_file_does_not_separate():
    """`00`:98: "a two-file application packet may remain a single folder".
    SABOTAGE: return True here and every one-file-per-folder level earns its
    place -- the folder-per-file tree is the one the reference calls noise."""
    nodes = (_node("n_root", None, "Vendors"),
             _node("n_a", "n_root", "Acme"), _node("n_b", "n_root", "Beta"))
    counts = _counts_with_children(nodes, {
        "n_root": ("f1", "f2"), "n_a": ("f1",), "n_b": ("f2",)})
    assert separates_files(counts["n_root"]) is False


def test_a_level_with_one_child_does_not_separate():
    nodes = (_node("n_root", None, "Academics"), _node("n_a", "n_root", "Columbia"))
    counts = _counts_with_children(nodes, {"n_root": ("f1", "f2"), "n_a": ("f1", "f2")})
    assert separates_files(counts["n_root"]) is False


def test_a_level_that_gathers_files_under_more_than_one_child_separates():
    nodes = (_node("n_root", None, "Academics"),
             _node("n_a", "n_root", "PHYS1401"), _node("n_b", "n_root", "CHEM1101"))
    counts = _counts_with_children(nodes, {
        "n_root": ("f1", "f2", "f3"), "n_a": ("f1", "f2"), "n_b": ("f3",)})
    assert separates_files(counts["n_root"]) is True


def test_a_leaf_has_nothing_to_say_and_says_none():
    """`TreeLimits.materially_improves_retrieval` documents `None` as "no
    authored test decides this yet" and that None must never round to False.
    A leaf makes no partition, so the answer is None and no recommendation."""
    nodes = (_node("n_root", None, "Academics"),)
    counts = _counts_with_children(nodes, {"n_root": ("f1",)})
    assert separates_files(counts["n_root"]) is None


def test_the_recommendation_fires_from_the_measure_and_not_from_a_constant(conn):
    """The predicate the composition root supplies is the measure itself."""
    set_ceiling(conn, "tree.max_folder_proposals", 6)
    set_ceiling(conn, "tree.max_depth", 6)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    real = tree_limits(conn, excessive_depth_warning=3, tiny_folder_max_files=2,
                       tiny_folder_count_warning=3,
                       materially_improves_retrieval=separates_files)
    nodes = (_node("n_root", None, "Vendors", dimension="vendor",
                   dimension_role="vendor"),
             _node("n_a", "n_root", "Acme"), _node("n_b", "n_root", "Beta"))
    counts = _counts_with_children(nodes, {
        "n_root": ("f1", "f2"), "n_a": ("f1",), "n_b": ("f2",)})
    fired = warnings_for(nodes, counts, limits=real, parent_concepts={})
    assert RECOMMEND_FLATTEN in {w.kind for w in fired}
```

- [ ] **Step 2: Run** `nice -n 15 python3 -m pytest tests/p10/test_p10_health.py -p no:randomly -q` → `ImportError: cannot import name 'separates_files'`. Any other failure is a wrong test.

- [ ] **Step 3: Implement.** In `health.py`, on `BranchCounts` (after `stale: bool`, `:66`):

```python
    #: `106` Phase 7 §B.4, the carrier `test_the_flatten_rule_has_a_measure_to_
    #: read` named. The member count of each child, largest first: the partition
    #: this level makes of the files a person would open it to find. Empty for
    #: a leaf. It is a FACT about the tree, not a score, and `separates_files`
    #: reads it without a number the design did not state.
    retrieval_partition: tuple[int, ...] = ()
```

In `branch_counts` (`:240-274`), after `members = ...`:

```python
    index = _index(nodes)
    partition = tuple(sorted(
        (len(dict.fromkeys(members_by_node.get(child.node_id, ())))
         for child in index.children.get(node_id, ())), reverse=True))
```

and pass `retrieval_partition=partition` into the constructor. Then, after `branch_counts`:

```python
def separates_files(counts: BranchCounts) -> bool | None:
    """§5.9's "materially improves retrieval", read off the partition.

    `00`:98 gives both ends: `Georgetown Prep` "may remain shallow because it
    contains only a handful of files", and "a two-file application packet may
    remain a single folder". A level separates its files when it puts them
    under more than one child and at least one child gathers more than one --
    one child is a folder opened to find one folder; one file per child is the
    filename restated as a directory. Neither bound is a threshold: they are
    the two degenerate partitions.

    `None` for a leaf. `TreeLimits.materially_improves_retrieval` says None
    "must never round to False", and a folder with no children has made no
    partition to judge.
    """
    parts = counts.retrieval_partition
    if not parts:
        return None
    return len(parts) > 1 and any(part > 1 for part in parts)
```

In `candidates._counts_for_preview` (`:488-497`) pass every node's members, not the one node's:

```python
    members_by_node = {node_id: sorted(files)
                       for node_id, files in preview.members_by_node.items()}
    return {
        node.node_id: branch_counts(
            tree, node_id=node.node_id, members_by_node=members_by_node,
            unresolved_by_node={preview.parent.node_id: unresolved},
            evidence_gaps_by_node={}, sensitive_node_ids=sensitive)
        for node in tree
    }
```

In `cli.py:634` replace `materially_improves_retrieval=lambda option: True)` with
`materially_improves_retrieval=separates_files)` (import from
`tree_design.health` beside `tree_health` at `cli.py:423`), and cut the
comment block above it that argued there was nothing to feed it — the paragraph
is now false and a false paragraph beside a live predicate is the defect `104`
§18.42 named.

- [ ] **Step 4: Remove the xfail marker** at `tests/p10/test_p10_health.py:651-663`
  and keep the test body: it now passes as an ordinary test.
- [ ] **Step 5: Run** `nice -n 15 python3 -m pytest tests/p10/test_p10_health.py tests/p10/test_p10_candidates.py tests/p10/test_p10_no_invention.py -p no:randomly -q`. Expect green; `test_p10_no_invention` is the one that would object to a literal above 1, and none was written.
- [ ] **Step 6: Commit.** `feat(106 Phase 7.1): the flatten recommendation reads the partition a level makes, not a constant`

### Task 7.2: A folder per file is not built beneath a built node, and the option says so

**Files:** Modify `src/tree_design/materialise.py` (`_project`, `BranchPreview`,
new `FoldedLevel`, new `folded_sentence`) · Modify `src/tree_design/vocabulary.py`
(two words) · Modify `src/tree_design/candidates.py:541-638` (the sentence) ·
Test `tests/p10/test_p10_candidates.py` (new tests; two existing fixtures change
and the change is explained on each).

- [ ] **Step 1: Write the failing tests** (append to `tests/p10/test_p10_candidates.py`):

```python
# --- `106` Phase 7 §B.1: a folder per file beneath a built node is not built ----


def test_one_file_per_value_beneath_a_built_node_is_folded_into_it(conn):
    """`00`:98: "a two-file application packet may remain a single folder."
    Three files in one course, each a different kind of work: the course folder
    holds the three files and no kind-of-work folder is built under it.

    SABOTAGE: build the three -- the person opens PHYS1401 to find three folders
    with one file each, which is the filename restated as a directory."""
    every = {"f1", "f2", "f3"}
    evidence = _evidence(
        _level("subject", "subject", 0, {"PHYS1401": every, "CHEM1101": {"f4"}}),
        _level("work_type", "work_type", 1,
               {"Homework": {"f1"}, "Lectures": {"f2"}, "Syllabus": {"f3"},
                "Lab": {"f4"}}))
    option = _options(conn, evidence, "subject", "work_type")[0]
    labels = [child.label_chain[-1] for child in option.children]
    assert "PHYS1401" in labels and "CHEM1101" in labels
    assert not {"Homework", "Lectures", "Syllabus", "Lab"} & set(labels)
    assert option.total_child_branches == 2


def test_a_folded_level_is_said_on_the_option_and_not_promised(conn):
    """`00`:99 puts the counts before the choice, and `104` §18.42's rule is that
    the sentence may not offer folders the shape will not build. SABOTAGE: keep
    `_summarise(counts)` -- the option reads "2 subject, and 4 work_type" and
    builds two folders."""
    every = {"f1", "f2", "f3"}
    evidence = _evidence(
        _level("subject", "subject", 0, {"PHYS1401": every, "CHEM1101": {"f4"}}),
        _level("work_type", "work_type", 1,
               {"Homework": {"f1"}, "Lectures": {"f2"}, "Syllabus": {"f3"},
                "Lab": {"f4"}}))
    option = _options(conn, evidence, "subject", "work_type")[0]
    assert "4 work_type" not in option.summary
    assert "not made a folder under 'PHYS1401'" in option.summary
    assert "each of its 3 files would have had a folder of its own" in option.summary


def test_a_mixed_level_beneath_a_built_node_is_still_built(conn):
    """The negative twin: one child gathering two files earns the level, and
    the single-file siblings beside it stay (they are `WARN_TINY_FOLDERS`'
    business, not this rule's)."""
    every = {"f1", "f2", "f3"}
    evidence = _evidence(
        _level("subject", "subject", 0, {"PHYS1401": every, "CHEM1101": {"f4"}}),
        _level("work_type", "work_type", 1,
               {"Homework": {"f1", "f2"}, "Syllabus": {"f3"}, "Lab": {"f4"}}))
    option = _options(conn, evidence, "subject", "work_type")[0]
    labels = [child.label_chain[-1] for child in option.children]
    assert "Homework" in labels and "Syllabus" in labels


def test_the_rule_does_not_reach_the_branch_root(conn):
    """§A's last paragraph: at the root there is no chain a folded file could
    still be reached by, so three one-file courses under the branch stay three
    folders and the tiny-folder warning speaks. SABOTAGE: fold here and the
    three files have no reachable home -- `104` Q-H's cost, silently."""
    from tree_design.vocabulary import WARN_TINY_FOLDERS

    evidence = _evidence(_level("subject", "subject", 0, {
        "PHYS1401": {"f1"}, "CHEM1101": {"f2"}, "MATH2000": {"f3"}}))
    option = _options(conn, evidence, "subject", tiny_folder_count_warning=2)[0]
    assert option.total_child_branches == 3
    assert WARN_TINY_FOLDERS in {w.kind for w in option.warnings}
```

- [ ] **Step 2: Run** `nice -n 15 python3 -m pytest tests/p10/test_p10_candidates.py -p no:randomly -q -k "folded or mixed_level or branch_root"` → the first two fail on `total_child_branches == 5`/the sentence; the last two pass already (they pin what must not change).

- [ ] **Step 3: Implement.** `vocabulary.py`, beside `RECOMMEND_FLATTEN` (`:497`):

```python
#: `106` Phase 7 §B. Why the projection measured a level under one parent and
#: built no folder for it. Two words, for the two degenerate partitions
#: `00`:98 names: one folder per file, and one folder for every file.
FOLDED_ONE_PER_FILE: str = "one-folder-per-file"
FOLDED_ONE_FOR_ALL: str = "one-folder-for-all"
```

`materialise.py`, after `BranchEvidence` (`:122-133`):

```python
@dataclass(frozen=True)
class FoldedLevel:
    """One level measured under one parent and not built, and why (`00`:98).

    Carried as DATA on the preview so the sentence is composed once, in
    `candidates.vertical_options`, and the node's own explanation says the same
    thing in the same words: two spellings of one fold is how a screen comes to
    promise a folder the tree does not hold.
    """

    parent_node_id: str
    parent_label: str
    dimension_role: str
    label: str
    values: tuple[str, ...]
    file_count: int
    reason: str


def folded_sentence(fold: FoldedLevel) -> str:
    """The one clause both the option and the node say about a fold."""
    if fold.reason == FOLDED_ONE_PER_FILE:
        return (f"{fold.label} was not made a folder under {fold.parent_label!r}: "
                f"each of its {fold.file_count} files would have had a folder of "
                "its own")
    return (f"{fold.label} {' / '.join(repr(v) for v in fold.values)} was not made "
            f"a folder under {fold.parent_label!r}: every file there carries it, "
            "so it would be a folder you open to find one folder")
```

`BranchPreview` (`:535-561`) gains, after `branch_expectations`:

```python
    #: `106` Phase 7 §B. Every level the walk measured under a built node and
    #: did not build, with the reason. Empty is the common case.
    folded: tuple[FoldedLevel, ...] = ()
```

`_project` (`:645-763`) gains two keyword parameters, `under_built: bool` and
`folded_out: list`, threaded through every recursive call unchanged except the
one from a built node (`:727-733`), which passes `under_built=True`. Replace the
loop head (`:661-689`) so the children are known before any is built:

```python
    children: list[tuple[str, frozenset[str]]] = []
    for value in level.values:
        members = level.members_by_value[value] & eligible
        if not members:
            continue
        if members <= evidence.protected_file_ids:
            # (the existing comment block, unchanged)
            continue
        children.append((value, members))

    # `106` Phase 7 §B.1, `00`:98: "a two-file application packet may remain a
    # single folder". Beneath a built node -- and only there, because at the
    # root there is no chain a folded file could still be reached by -- a level
    # that would give every file a folder of its own is measured and not built.
    # The files stay members of `parent`; the fold is recorded so the option
    # and the node both say it. `len(members) == 1` is the degenerate
    # partition, not a threshold.
    if under_built and len(children) > 1 and all(
            len(members) == 1 for _value, members in children):
        folded_out.append(FoldedLevel(
            parent_node_id=parent.node_id, parent_label=parent.display_label,
            dimension_role=level.dimension_role, label=_label_of(level),
            values=tuple(value for value, _members in children),
            file_count=len(children), reason=FOLDED_ONE_PER_FILE))
        _project(evidence, level_index=level_index + 1, parent=parent,
                 eligible=eligible, chain=chain, plan_version_id=plan_version_id,
                 mint_node_id=mint_node_id, handling_class_for=handling_class_for,
                 template_context_for=template_context_for,
                 protected_movement_permitted=protected_movement_permitted,
                 out=out, members_out=members_out, under_built=under_built,
                 folded_out=folded_out)
        return

    ordinal = 0
    for value, members in children:
        node_id = mint_node_id()
        ...  # the existing node construction, unchanged from `:690-733`,
        ...  # with `under_built=True, folded_out=folded_out` on the recursion
```

`project_branch_preview` (`:620-642`): start `folded: list[FoldedLevel] = []`,
pass `under_built=False, folded_out=folded` to the top call, and after the
walk stamp the parent nodes' explanations and carry the folds:

```python
    said = {fold.parent_node_id: fold for fold in folded}
    nodes = [dataclasses.replace(
                 node, explanation=f"{node.explanation} {folded_sentence(said[node.node_id])}.")
             if node.node_id in said else node
             for node in nodes]
    ...
    return BranchPreview(parent=parent, nodes=tuple(nodes),
                         members_by_node={parent.node_id: evidence.member_file_ids, **members},
                         branch_expectations=stated, folded=tuple(folded))
```

(One fold per parent per level; `said` keys on the parent and a parent can fold
at most one level per walk, because the fold recursion continues from the
same parent with the same eligible set and the next level either builds or
folds again — if it folds again, keep BOTH: make `said` a `dict[str, list]`
and join the sentences with a space.)

`candidates.vertical_options` (`:595-612`): the sentence is composed from what
was BUILT, and the folds follow it:

```python
        built_counts: dict[str, int] = {}
        for node in (() if built is None else built.nodes):
            built_counts[node.dimension_role or ""] = built_counts.get(
                node.dimension_role or "", 0) + 1
        summary = f"This option would create {_summarise(built_counts)}."
        for fold in (() if built is None else built.folded):
            summary += f" {folded_sentence(fold)}."
```

and `_summarise` (`:436`) keeps every level that built something: `if count`
instead of `if count > 1` — its input is now built nodes per level, so "one
folder" there is a real folder that something divides beneath, and dropping it
would hide a level from the sentence. Update the docstring's last paragraph to
say the input changed and why. `tests/p10/test_p10_existing_folders.py:475`
(`test_a_level_that_makes_no_folder_is_not_counted_in_the_summary`) passes a
counts mapping directly; change its fixture to the built shape and keep its
assertion.

- [ ] **Step 4: Two existing fixtures change, and each says why.**
  `tests/p10/test_p10_candidates.py:521-545`
  (`test_a_one_child_level_that_makes_a_real_split_readable_stays_silent`) gives
  `work_type` one file per value; under §B.1 that level is folded, the chain
  above it then never divides, and the test would pass for the wrong reason.
  Give `Homework` two files (`{"f1", "f4"}`) and `every = {"f1","f2","f3","f4"}`
  so `00`:78's path is exercised as the design draws it — "many files with
  strong facts". `:548-556` (`test_an_option_that_would_scatter_files_into_tiny_
  folders_warns`) is at the ROOT, which §B.1 does not reach; it passes
  unchanged and the new `test_the_rule_does_not_reach_the_branch_root` pins
  that this is deliberate.
- [ ] **Step 5: Run** `nice -n 15 python3 -m pytest tests/p10/test_p10_candidates.py tests/p10/test_p10_materialise.py tests/p10/test_p10_existing_folders.py tests/p10/test_p10_pipeline.py tests/p10/test_p10_no_invention.py -p no:randomly -q`. Expect green.
- [ ] **Step 6: Commit.** `feat(106 Phase 7.2): a folder per file beneath a built node is not built, and the option says so`

### Task 7.3: A run of single children that never divides folds into its top

**Files:** Modify `src/tree_design/materialise.py` (new `_fold_single_child_runs`,
called from `project_branch_preview`) · Test `tests/p10/test_p10_candidates.py`.

- [ ] **Step 1: Write the failing tests:**

```python
# --- `106` Phase 7 §B.2: a single-child run that never divides folds ------------


def test_a_school_with_one_term_one_course_and_nothing_below_stays_shallow(conn):
    """`00`:98: "Academics/Georgetown Prep may remain shallow because it
    contains only a handful of files." Two schools divide; under Georgetown
    every file shares one term and one course and nothing divides beneath, so
    Georgetown holds its files flat and CLAIMS the term and the course.

    SABOTAGE: skip the fold -- Georgetown/2024-Fall/ENG101 is three folders a
    person opens to find one folder each, on the design's own example."""
    from tree_design.records import ExpectedValue

    georgetown = {"g1", "g2"}
    columbia = {"c1", "c2", "c3"}
    evidence = _evidence(
        _level("school", "school", 0, {"Georgetown Prep": georgetown, "Columbia": columbia}),
        _level("term", "term", 1, {"2024-Fall": georgetown, "2026-Spring": columbia}),
        _level("subject", "subject", 2, {"ENG101": georgetown, "PHYS1401": columbia}),
        _level("work_type", "work_type", 3,
               {"Homework": {"c1", "c2"}, "Syllabus": {"c3"}, "Essays": georgetown}))
    option = _options(conn, evidence, "school", "term", "subject", "work_type")[0]
    chains = {child.label_chain for child in option.children}
    assert ("Academics", "Georgetown Prep") in chains
    assert not any(chain[1] == "Georgetown Prep" and len(chain) > 2 for chain in chains)
    # `00`:78's own path is untouched: something divides beneath Columbia.
    assert ("Academics", "Columbia", "2026-Spring", "PHYS1401", "Homework") in chains
    assert "every file there carries it" in option.summary


def test_the_folded_values_are_claimed_by_the_folder_that_keeps_the_files(conn):
    """A destination that states nothing cannot be reached by a fact
    (`materialise.branch_expectations`); the fold appends the values it folded
    to the top's chain so P11's direct-fact channel still lands there."""
    from tree_design.records import ExpectedValue

    georgetown = {"g1", "g2"}
    columbia = {"c1", "c2", "c3"}
    evidence = _evidence(
        _level("school", "school", 0, {"Georgetown Prep": georgetown, "Columbia": columbia}),
        _level("term", "term", 1, {"2024-Fall": georgetown, "2026-Spring": columbia}),
        _level("subject", "subject", 2, {"ENG101": georgetown, "PHYS1401": columbia}),
        _level("work_type", "work_type", 3,
               {"Homework": {"c1", "c2"}, "Syllabus": {"c3"}, "Essays": georgetown}))
    preview = _preview_binding()(None, evidence)
    top = next(node for node in preview.nodes if node.display_label == "Georgetown Prep")
    assert top.expected_values == (
        ExpectedValue("school", "Georgetown Prep"),
        ExpectedValue("term", "2024-Fall"),
        ExpectedValue("subject", "ENG101"),
        ExpectedValue("work_type", "Essays"))
    assert preview.members_by_node[top.node_id] == frozenset(georgetown)


def test_a_single_child_holding_a_strict_subset_is_a_real_split_and_stays(conn):
    """One child with SOME of the parent's files divides them from the rest.
    SABOTAGE: fold on `len(children) == 1` alone and the parent claims a value
    two of its files do not carry."""
    evidence = _evidence(
        _level("school", "school", 0, {"Georgetown Prep": {"g1", "g2", "g3"}, "Columbia": {"c1"}}),
        _level("term", "term", 1, {"2024-Fall": {"g1"}, "2026-Spring": {"c1"}}))
    preview = _preview_binding()(None, evidence)
    labels = {node.display_label for node in preview.nodes}
    assert "2024-Fall" in labels
```

- [ ] **Step 2: Run** with `-k "stays_shallow or folded_values or strict_subset"` → the first two fail (chains reach `Essays` under Georgetown; expectations stop at `school`); the third passes and pins the boundary.

- [ ] **Step 3: Implement.** In `materialise.py`, after `_project`:

```python
def _fold_single_child_runs(nodes: list[Node], members: dict[str, frozenset[str]],
                            folded: list[FoldedLevel]) -> list[Node]:
    """`106` Phase 7 §B.2, `00`:98: a run of single children that never divides.

    A node with ONE child holding EVERY one of its files, whose child has one
    such child, and so on to a node with no children, is a chain of folders a
    person opens to find one folder each. The chain folds into its top: the
    top keeps the files and gains the folded values on its own chain, so a
    fact still reaches it (`00`:110). A child holding a strict subset divides
    the parent's files from the rest and is NOT folded -- `WARN_ONE_CHILD`
    is the advice about that one. `00`:78's own path is untouched because
    something divides beneath it.

    Post-order by construction: `nodes` is in creation order, so a top is
    visited before anything beneath it, and a run's members are removed
    before a later node could treat one of them as a top.
    """
    kids: dict[str, list[Node]] = {}
    for node in nodes:
        kids.setdefault(node.parent_node_id, []).append(node)
    removed: set[str] = set()
    rewritten: dict[str, Node] = {}
    for top in nodes:
        if top.node_id in removed:
            continue
        run: list[Node] = []
        current = top
        while True:
            below = [k for k in kids.get(current.node_id, ()) if k.node_id not in removed]
            if len(below) != 1 or members[below[0].node_id] != members[current.node_id]:
                break
            run.append(below[0])
            current = below[0]
        if not run or kids.get(current.node_id):
            continue
        extra = run[-1].expected_values[len(top.expected_values):]
        folds = tuple(FoldedLevel(
            parent_node_id=top.node_id, parent_label=top.display_label,
            dimension_role=node.dimension_role or "", label=node.dimension or node.dimension_role or "",
            values=(node.display_label,), file_count=len(members[top.node_id]),
            reason=FOLDED_ONE_FOR_ALL) for node in run)
        folded.extend(folds)
        rewritten[top.node_id] = dataclasses.replace(
            top, expected_values=top.expected_values + extra,
            explanation=top.explanation + "".join(f" {folded_sentence(f)}." for f in folds))
        for node in run:
            removed.add(node.node_id)
            members.pop(node.node_id, None)
    return [rewritten.get(node.node_id, node) for node in nodes
            if node.node_id not in removed]
```

`label=` there reads the level's authored label: keep it honest by carrying
`_label_of(level)` onto the node — `Node` has no such field, so use
`node.dimension_role` and the display label, which is what the outline prints
anyway. Call it in `project_branch_preview` right after `_project` returns:
`nodes = _fold_single_child_runs(nodes, members, folded)`, before `stated` is
computed. `stated` (`:632-635`) still reads `if nodes`; a fold never empties
`nodes` because the top survives.

- [ ] **Step 4: Run** `nice -n 15 python3 -m pytest tests/p10/test_p10_candidates.py tests/p10/test_p10_materialise.py tests/p10/test_p10_pipeline.py tests/p10/test_p10_health.py -p no:randomly -q`. Expect green; `test_a_one_child_level_that_makes_a_real_split_readable_stays_silent` (as amended in 7.2) is the standing proof the fold spares `00`:78's path.
- [ ] **Step 5: Commit.** `feat(106 Phase 7.3): a run of single folders that never divides folds into its top, which claims what it folded`

### Task 7.4: The outline says what a folder holds without a level for it

**Files:** Modify `src/cli.py:22334-22341` (`_node_claim`) and `:22380-22429`
(`structure_rows`) · Test `tests/integration/test_the_editable_structure.py`
(unit-level, no run needed).

- [ ] **Step 1: Write the failing test:**

```python
def test_a_row_names_the_values_folded_into_its_folder():
    """`106` Phase 7 §B.3. A folder that claims more than its own level says so
    on its line, so the person editing the outline sees what is inside without
    a level for it. SABOTAGE: print only the count -- the fold is a decision
    the product made and did not say."""
    from tree_design.records import ExpectedValue, Node

    top = Node(
        node_id="n_g", plan_version_id="p", node_type="proposed",
        display_label="Georgetown Prep", parent_node_id="n_root",
        root_anchor="root_documents", ordinal=0, associated_group_ids=(),
        explanation="x", node_role="ordinary", accepts_placement=True,
        handling_class="personal_non_sensitive", origin_node_id="n_g",
        dimension_role="school", dimension="school",
        expected_values=(ExpectedValue("school", "Georgetown Prep"),
                         ExpectedValue("term", "2024-Fall"),
                         ExpectedValue("subject", "ENG101")))
    assert cli._node_claim(top) == ("school", "Georgetown Prep")
    assert cli._folded_words(top) == "also every file's term 2024-Fall and subject ENG101"
```

- [ ] **Step 2: Run** `nice -n 15 python3 -m pytest tests/integration/test_the_editable_structure.py -p no:randomly -q -k folded_into` → `AttributeError: module 'cli' has no attribute '_folded_words'` (and `_node_claim` returns the LAST value, `("subject", "ENG101")`, which is the bug this task also fixes).

- [ ] **Step 3: Implement.** `_node_claim` reads the node's OWN dimension:

```python
def _node_claim(node) -> tuple[str, str] | None:
    """The one fact value this folder is named by, or `None` for a folder that is
    not named by one at all -- a root, or a level the template owns.

    The value of the node's OWN dimension, not `expected[-1]`: since `106`
    Phase 7 a folder may carry the values of levels folded into it after its
    own, and a rename gesture keyed on the last of those would rename the
    wrong thing."""
    dimension = getattr(node, "dimension", None)
    expected = getattr(node, "expected_values", ())
    if dimension is None:
        # A template-local node (Contract W5) has no dimension and carries only
        # its ancestors' chain; this is what it always answered, kept so the
        # rename gestures over the integration corpus's own template-local
        # branch (`Debate Society`) key on the same row they keyed on before.
        # A failure in `test_the_editable_structure.py` after this task is
        # read against THIS branch first, not against the fold.
        return (expected[-1].field, expected[-1].value) if expected else None
    for one in expected:
        if one.field == dimension:
            return (one.field, one.value)
    return None


def _folded_words(node, ancestor_fields: frozenset[str] = frozenset()) -> str:
    """`106` Phase 7 §B.3: what this folder holds without a level for it.

    Every node's chain carries its ANCESTORS' values too (`materialise.py:
    697-698`), and those are the path, not a fold; the walk hands them over
    so only the values folded INTO this folder are named."""
    own = getattr(node, "dimension", None)
    folded = [expected for expected in getattr(node, "expected_values", ())
              if expected.field != own and expected.field not in ancestor_fields]
    return ("also every file's "
            + " and ".join(f"{e.field} {e.value}" for e in folded)) if folded else ""
```

In `structure_rows`, the walk keeps the set of dimensions its ancestors are
named by (`_outline_walk` yields depth; rebuild the ancestor set from
`by_parent` as `_child_previews` does at `candidates.py:444-460`) and appends
`_folded_words(node, ancestor_fields)` to `said` when it is non-empty.

- [ ] **Step 4: Run** the integration file and `tests/integration/test_the_editable_structure.py` end to end (it drives the CLI over the eleven-file synthetic corpus with the cloud stubbed — allowed, no scan of the owner's disk).
- [ ] **Step 5: Commit.** `feat(106 Phase 7.4): the outline names the values folded into a folder, and a rename keys on the folder's own level`

### Task 7.5: A directory holding one file is not offered as a branch

**Files:** Modify `src/tree_design/upstream.py:83-87, 258-263`
(`ExistingFolder.subdirectory_count`) · Create nothing · Modify
`src/tree_design/candidates.py` (new `keeps_files`) · Modify
`src/cli.py:16171-16182` (`adopted_folders`) and the report (one count line) ·
Test `tests/p10/test_p10_candidates.py`, `tests/p10/test_p10_existing_folders.py`.

- [ ] **Step 1: Write the failing tests:**

```python
# tests/p10/test_p10_candidates.py
from tree_design.candidates import keeps_files  # noqa: E402
from tree_design.upstream import ExistingFolder  # noqa: E402


def test_a_directory_holding_one_file_and_nothing_else_is_not_a_branch():
    """`106` Phase 7 §C. `104` R-87 ruled a one-file adopted folder claims no
    expectation; this is the same bar applied to whether it is a branch at all.
    SABOTAGE: return True -- `Downloads/foo/foo.pdf` becomes a top-level folder
    named after the file, which is the root the lead measured."""
    one = ExistingFolder(directory_path="/d/foo", parent_directory="/d",
                         file_count=1, curation_signal="undetermined",
                         subdirectory_count=0)
    assert keeps_files(one) is False


def test_a_directory_with_two_files_or_a_subdirectory_is_a_branch():
    two = ExistingFolder(directory_path="/d/Uni", parent_directory="/d",
                         file_count=2, curation_signal="undetermined",
                         subdirectory_count=0)
    nested = ExistingFolder(directory_path="/d/Uni", parent_directory="/d",
                            file_count=1, curation_signal="undetermined",
                            subdirectory_count=1)
    assert keeps_files(two) is True and keeps_files(nested) is True


def test_a_folder_read_before_the_field_existed_still_reads():
    """`subdirectory_count` is last and defaulted, `review_policy`'s convention
    (`106` Task 1.1 step 5): a fixture or an older reader that omits it must
    not turn into a traceback."""
    assert ExistingFolder(directory_path="/d/x", parent_directory="/d",
                          file_count=3, curation_signal="undetermined").subdirectory_count == 0
```

- [ ] **Step 2: Run** → `ImportError: cannot import name 'keeps_files'`.

- [ ] **Step 3: Implement.** `upstream.py:83-87`:

```python
@dataclass(frozen=True)
class ExistingFolder:
    directory_path: str
    parent_directory: str | None
    file_count: int
    curation_signal: str
    #: `106` Phase 7 §C. P3 records it (`inventory.py:64`); nothing read it.
    #: Last and defaulted so every caller that predates it is what it was.
    subdirectory_count: int = 0
```

`existing_folders` (`:258-263`) adds `subdirectory_count=row["subdirectory_count"]`.
`candidates.py`, beside `folder_label` (`:169`):

```python
def keeps_files(folder: ExistingFolder) -> bool:
    """`106` Phase 7 §C: is this directory a place the person keeps files?

    Two or more files directly inside, or a subdirectory. A directory holding
    exactly one file and nothing else is a wrapper -- a browser's or Finder's
    `foo/foo.pdf` -- and adopting it put a file's own name at the top of the
    tree. `104` R-87 already ruled such a folder claims no expectation; this
    is the same bar applied one step earlier. Not a threshold: "one" is the
    number below which a folder is not a folder of files. The file inside is
    still in the roster and still placed by its own facts.
    """
    return folder.file_count > 1 or folder.subdirectory_count > 0
```

`cli.py:16171-16182`: add `and keeps_files(folder)` to the comprehension, with
a two-line comment citing this task. In `report`, one line after the structure
block: count `result.tree.candidates` whose `source in EXISTING_FOLDER_SOURCES`,
`supporting_file_count == 1` and whose `subject_id` is no node's
`existing_path` in `result.tree.tree.nodes`, and print *"N folder(s) holding a
single file were left as they are and not made branches."* when N > 0.

- [ ] **Step 4: Run** `nice -n 15 python3 -m pytest tests/p10/test_p10_candidates.py tests/p10/test_p10_existing_folders.py tests/p10/test_p10_upstream.py tests/integration/test_the_editable_structure.py -p no:randomly -q`.
- [ ] **Step 5: Commit.** `fix(106 Phase 7.5): a directory holding one file is not offered as a branch, so a file's own name never tops the tree`

**Left open for the lead, by name:** if the counts query in §C shows
`bundle_shaped > 0` under `existing`, the root is a macOS package and this task
does not remove it — that is P3 recording a package as a directory
(`traversal.py:117-125`, `exclusion.py:121`), a change to what `files` holds,
and the owner's.

### Task 7.6: A protected root reads as what it is in the outline

**Files:** Modify `src/cli.py:22412-22428` (`structure_rows`) · Test
`tests/integration/test_the_editable_structure.py`.

- [ ] **Step 1: Failing test:**

```python
def test_a_protected_root_says_it_is_protected_and_not_a_folder_of_the_plan():
    """`106` Phase 7 §C producer 3. `represent_protected_areas` puts a bundle at
    the root by the standing rule; the outline printed "0 files" beside it.
    SABOTAGE: keep the count -- an app reads as an empty folder of the plan."""
    from tree_design.records import Node

    area = Node(
        node_id="n_app", plan_version_id="p", node_type="protected",
        display_label="Numbers.app", parent_node_id=None,
        root_anchor="root_documents", ordinal=0, associated_group_ids=(),
        explanation="marked and counted", node_role="ordinary",
        accepts_placement=False, handling_class="personal_non_sensitive",
        origin_node_id="n_app")
    rows = cli.structure_rows(_run_with_nodes((area,)), situations={}, words_of=lambda s: "")
    assert rows[0].words == cli.PROTECTED_ROW_WORDS
    assert "0 files" not in rows[0].words
```

(`_run_with_nodes` is a three-line helper building a `ProductionRun` with an
empty placement and these nodes, in the file's own fixture style.)

- [ ] **Step 2: Run** → `AttributeError: PROTECTED_ROW_WORDS`.
- [ ] **Step 3: Implement.** `PROTECTED_ROW_WORDS: str = "protected: marked and counted, never opened; not a folder of this plan"` beside `STRUCTURE_FILENAME` (`cli.py:22348`); in `structure_rows`, `if node.node_type == tv.PROTECTED: said = [PROTECTED_ROW_WORDS]` before the count.
- [ ] **Step 4: Run** the integration file. **Step 5: Commit.** `fix(106 Phase 7.6): a protected root in the outline says what it is instead of "0 files"`

### Task 7.7: Every review set carries its key, and two more of the reference's characteristics exist

**Files:** Modify `src/placement/residual.py:74-108, 217-230` (`ResidualSet.set_key`)
· Modify `src/tree_design/vocabulary.py:296` (two root names) · Modify
`src/cli.py:15000-15200` (characteristics, `REVIEW_HOME_FOR_SET`) and
`:16910-17053` (`residual_partition` carries the key; two new readers) · Test
`tests/p11/test_p11_residual_sets.py`, `tests/test_cli_report_at_scale.py`.

- [ ] **Step 1: Failing tests.** In `tests/p11/test_p11_residual_sets.py`:

```python
def test_a_surfaced_set_carries_the_key_its_partition_gave_it(p11_conn):
    """`106` Phase 7 §D.3: the offer is read off the set's KEY, not its label,
    because the label carries `(i of n)` on a split set and is the person's
    words rather than an address. SABOTAGE: drop the field -- the offer has to
    be re-derived from the label, and a renamed label offers nothing."""
    sets = _surface(p11_conn, partition=lambda ids: (
        _group("Screenshots with no association", tuple(ids), key="screenshots"),))
    assert {item.set_key for item in sets} == {"screenshots"}


def test_a_set_written_before_the_key_existed_reads_back_with_no_key(p11_conn):
    """The payload is `asdict`; a row from an older run has no `set_key` and
    must read as the default, never as a traceback."""
    item = ResidualSet(
        set_id="plan-1:x", plan_version="plan-1", label="x", file_count=1,
        representative_examples=("f",), file_type_distribution=(("png", 1),),
        age_range=("2026-01-01", "2026-01-01"), evidence_availability="ocr",
        sensitivity_status="public_low", protected=False,
        weak_graph_neighbours=(), reason_not_placed="why",
        member_file_ids=("f",))
    assert item.set_key == ""
```

In `tests/test_cli_report_at_scale.py` (that file's own fixture style, which
builds a report from a `ProductionRun`):

```python
def test_every_ordinary_review_set_key_has_an_offered_home_or_is_a_block():
    """`00` amendment 13: every leftover set is offered a home. A set that is a
    BLOCK (not classified, no model allowed, not allowed to cross, protected)
    is not a leftover and is deliberately absent. SABOTAGE: add a key to
    `REVIEW_SET_ORDER` without a row here and it is a set with nowhere."""
    blocks = {cli.NOT_YET_CLASSIFIED, cli.NO_MODEL_ALLOWED, cli.NOT_ALLOWED_TO_CROSS,
              cli.PROTECTED_REVIEW_SET, cli.WAITING_ON_AN_ANSWER,
              pv.SITUATION_UNANSWERED, pv.BUDGET_DEFERRED}
    for key in cli.REVIEW_SET_ORDER:
        assert key in cli.REVIEW_HOME_FOR_SET or key in blocks, key
```

(`WAITING_ON_AN_ANSWER` is a question the report prints; `SITUATION_UNANSWERED`
is a branch whose situation the person has not yet named, and its files may
be held by that branch once it is; `BUDGET_DEFERRED`'s own sentence says "the
next run picks them up". None of the three is a leftover no branch can hold,
so all three stay out of the table and in `blocks`.)

- [ ] **Step 2: Run** → `TypeError` on the `_group(..., key=...)` override until the field exists; `AttributeError: REVIEW_HOME_FOR_SET`.

- [ ] **Step 3: Implement.**

`residual.py`, on `ResidualSet` after `member_file_ids`:

```python
    #: `106` Phase 7 §D.3. The partition's own key for this set -- the reason
    #: code or the characteristic (`cli.REVIEW_SET_ORDER`'s member) -- which is
    #: what the offered home is read off. Last and defaulted: a row an earlier
    #: run wrote carries none and reads as "", which is the truth about it.
    set_key: str = ""
```

and in `surface_residual_sets` (`:217-230`) `set_key=str(group.get("key", ""))`.

`tree_design/vocabulary.py` after `RESIDUAL_TEMPLATE_NAMES` (`:296`):

```python
#: `00` amendment 13 (17 Sep 2026), the owner's: "Root-level 98 and 99, as my
#: reference says." Two root-level homes for what no branch can hold. Closed
#: vocabulary on the same footing as §7.3's nine names above.
REVIEW_AND_UNSORTED: str = "98 Review and Unsorted"
ARCHIVE: str = "99 Archive"
```

`cli.py`: two new characteristic keys beside `SCREENSHOT_REVIEW_SET`:

```python
#: `00` amendment 13's two missing characteristics. Both are read off records
#: this run already wrote and derive nothing: a locked archive is P4's own
#: `unreadable` row (`locked_reasons`), and a duplicate or version is P6's
#: `duplicate_family` / `version_family` fact (`facts.families`).
UNSUPPORTED_REVIEW_SET: str = "unsupported-or-encrypted"
DUPLICATES_REVIEW_SET: str = "possible-duplicates-and-versions"
```

`REVIEW_SET_CHARACTERISTICS` gains the two rows, each with ITS OWN sentence
(the existing three borrow `no_supported_destination`'s):

```python
    (UNSUPPORTED_REVIEW_SET, "Unsupported or encrypted",
     "these could not be read: password-protected, damaged or in a format "
     "nothing here opens. Nothing inside them was opened and nothing moved."),
    (DUPLICATES_REVIEW_SET, "Possible duplicates and versions",
     "each of these is a copy or an earlier version of a file this run also "
     "holds, and nothing matched it on its own."),
```

and `REFINED_BY_CHARACTERISTIC` (`:15166`) becomes a mapping of characteristic
→ the reasons it may divide: the three existing ones over
`{pv.NO_SUPPORTED_DESTINATION}`; `DUPLICATES_REVIEW_SET` over the same;
`UNSUPPORTED_REVIEW_SET` over `{pv.NO_SUPPORTED_DESTINATION, NOT_YET_CLASSIFIED}`
— a locked archive is unread and therefore unclassified, so it stops under
`NOT_YET_CLASSIFIED` today and would never reach the set amendment 13 names
for it. `REVIEW_SET_ORDER` (`:15187-15190`) reads the mapping instead of the
set. `residual_characteristics` (`:15203`) gains two readers, in this
precedence — locked, then family, then the three existing — because "cannot
be read" outranks "is a copy" outranks "is a screenshot" for what a person
can do about it:

```python
    locked = locked_reasons(conn, scan_run_id)          # cli.py:13337
    ...
    for file_id in file_ids:
        if file_id in locked:
            found[file_id] = UNSUPPORTED_REVIEW_SET
            continue
        if any(preferred_fact(conn, file_id=file_id, field_key=field) is not None
               for field in (DUPLICATE_FAMILY_FIELD, VERSION_FAMILY_FIELD)):
            found[file_id] = DUPLICATES_REVIEW_SET
            continue
        ...  # the existing media_type / routing readers
```

(`residual_characteristics` takes `scan_run_id` as a new keyword; its one
caller, `residual_partition`, has `scan_run_id[0]` in scope, `cli.py:16159`.)
`residual_partition._set` (`:17058`) adds `"key": key` to the dict it returns.

The suggestion table, beside `REVIEW_SET_WORDS`:

```python
#: `00` amendment 13: "every one is offered to the person before anything
#: moves". Set key -> the home offered for it. §7.3's own nine under `98`, and
#: `99 Archive` for copies and earlier versions. A key absent here is a BLOCK
#: (not classified, no model allowed, a move not permitted, protected) or a
#: question the report prints, and is offered nothing because there is nothing
#: to offer yet; `test_every_ordinary_review_set_key_has_an_offered_home_or_is_
#: a_block` pins the two lists against each other.
REVIEW_HOME_FOR_SET: Mapping[str, str] = MappingProxyType({
    SCREENSHOT_REVIEW_SET: TEMPORARY_SCREENSHOTS,
    STANDALONE_PDF_REVIEW_SET: INDEPENDENT_RECORDS,
    SPREADSHEET_REVIEW_SET: REVIEW_LATER,
    UNSUPPORTED_REVIEW_SET: UNSUPPORTED_OR_ENCRYPTED,
    DUPLICATES_REVIEW_SET: ARCHIVE,
    pv.NO_SUPPORTED_DESTINATION: REVIEW_LATER,
    pv.MULTIPLE_SUPPORTED_HOMES: REVIEW_LATER,
    pv.LOW_MARGIN: REVIEW_LATER,
    pv.CONFLICTING_FACTS: REVIEW_LATER,
    pv.SEMANTIC_ONLY: REVIEW_LATER,
    pv.GENERIC_HUB_ONLY: REVIEW_LATER,
    pv.NO_SHARED_BRANCH: REVIEW_LATER,
    NOT_YET_PLACED: REVIEW_LATER,
})
```

(Names imported from `tree_design.vocabulary`, which `cli.py:527` already
imports from; the exact member list of `REVIEW_SET_REASONS` past `:15060` is
to be read off the file when the table is written, not from this draft.)

- [ ] **Step 4: Run** `nice -n 15 python3 -m pytest tests/p11/test_p11_residual_sets.py tests/p11/test_p11_residual_send.py tests/test_cli_report_at_scale.py -p no:randomly -q`.
- [ ] **Step 5: Commit.** `feat(106 Phase 7.7): every review set carries its key; unsupported-or-encrypted and possible-duplicates join the characteristics; each key names its offered home`

### Task 7.8: `98 Review and Unsorted` exists in the tree, and residual homes live under it

**Files:** Modify `src/tree_design/pipeline.py:1230-1276` (`_enable_residual_library`
becomes a caller of new `enable_review_homes`) · Modify `src/cli.py:5037-5075`
(`_residual_library` always carries `99 Archive` as a user-defined template) ·
Test `tests/p10/test_p10_pipeline.py`.

- [ ] **Step 1: Failing test** (`tests/p10/test_p10_pipeline.py`, using that file's `design`/`decisions`):

```python
def test_a_residual_home_with_no_parent_lives_under_the_review_root(corpus):
    """`00` amendment 13: "root-level 98 ... visible at the root". A residual
    home the person enabled without a parent used to hang under this run's
    first proposed branch (`_enable_residual_library`); it now hangs under a
    root named `98 Review and Unsorted`, which exists exactly when something
    is under it. SABOTAGE: keep the first-branch parent -- `Review Later`
    sits inside `Coursework`, which is the pollution §7.1 names."""
    from tree_design.vocabulary import RESIDUAL, REVIEW_AND_UNSORTED

    result = design(corpus)
    nodes = {n.node_id: n for n in result.tree.nodes}
    home = next(n for n in nodes.values() if n.node_role == RESIDUAL)
    root = nodes[home.parent_node_id]
    assert root.display_label == REVIEW_AND_UNSORTED
    assert root.parent_node_id is None
    assert root.accepts_placement is True


def test_no_review_root_is_minted_when_nothing_is_under_it(corpus):
    """`00`:121: "These templates are not automatically created." An empty
    `98` would be a folder nobody asked for."""
    from tree_design.vocabulary import REVIEW_AND_UNSORTED

    result = design(corpus, dec=decisions(residual_choices=(), residual_configuration={}))
    assert REVIEW_AND_UNSORTED not in {n.display_label for n in result.tree.nodes}
```

- [ ] **Step 2: Run** → the first fails on `root.display_label` (the parent is the coursework branch).

- [ ] **Step 3: Implement.** In `pipeline.py`, replace the body of
`_enable_residual_library` (`:1239-1276`) with a call, and add the function
it calls:

```python
def _enable_residual_library(conn, authorities, decisions, *, version: str) -> None:
    """§7.4's enabled branches, into the draft that is about to be frozen.
    (docstring's first paragraph unchanged)"""
    if not decisions.residual_choices:
        return
    enable_review_homes(conn, authorities, decisions, version=version,
                        choices=decisions.residual_choices)


def enable_review_homes(conn, authorities, decisions, *, version: str,
                        choices: Sequence[ResidualChoice]) -> tuple[Node, ...]:
    """`00` amendment 13: residual homes live under a root-level `98`.

    The root is minted the first time a home needs it and never otherwise --
    `00`:121's "not automatically created" is kept for the root as for the
    homes. A choice that names its own parent or replaces an existing folder
    keeps that; only a parentless one goes under `98`. `99 Archive` is a home
    of its own at the root: it is in the library as the owner's user-defined
    template (`cli._residual_library`) and its choice names no parent and is
    exempt from `98` by name.

    Published so `mint_review_homes` can call it after placement, on a draft
    opened from the frozen tree -- the same seam `mint_scoped_generals` uses
    for `00`:99's General.
    """
    existing = {node.node_id: node for node in nodes_for_version(conn, version)}
    root = next((node for node in existing.values()
                 if node.parent_node_id is None
                 and node.display_label == REVIEW_AND_UNSORTED), None)
    parentless = [choice for choice in choices
                  if choice.parent_node_id is None
                  and choice.action not in (DISABLE, REPLACE_WITH_EXISTING)
                  and choice.template_name != ARCHIVE]
    if parentless and root is None:
        node_id = authorities.mint_node_id()
        root = _with_refinement(Node(
            node_id=node_id, plan_version_id=version, node_type=PROPOSED,
            display_label=REVIEW_AND_UNSORTED, parent_node_id=None,
            root_anchor=authorities.root_anchor,
            ordinal=sum(1 for node in existing.values() if node.parent_node_id is None),
            associated_group_ids=(),
            explanation=("Files no branch of this plan can hold are gathered "
                         "here, in named sets, and offered to you before "
                         "anything moves (`00` amendment 13)."),
            node_role=ORDINARY,
            accepts_placement=derive_accepts_placement(PROPOSED, protected_movement_permitted=False),
            handling_class=authorities.collapse_handling_classes(frozenset()),
            origin_node_id=node_id),
            lambda _node, _count, *, was_split: decisions.residual_refinement,
            file_count=0, was_split=False)
        write_node(conn, root)
        existing[root.node_id] = root
    rehomed = tuple(
        dataclasses.replace(choice, parent_node_id=root.node_id)
        if choice in parentless else choice
        for choice in choices)
    nodes = project_residual_nodes(
        decisions.residual_library, rehomed, plan_version_id=version,
        handling_class_for_template=decisions.residual_handling_class,
        mint_node_id=authorities.mint_node_id, existing_nodes=existing)
    for node in nodes:
        write_node(conn, _with_refinement(
            node, lambda _node, _count, *, was_split: decisions.residual_refinement,
            file_count=0, was_split=False))
    return nodes
```

(`ResidualChoice` is frozen; `dataclasses.replace` works. `DISABLE`,
`REPLACE_WITH_EXISTING`, `REVIEW_AND_UNSORTED`, `ARCHIVE` join the
`tree_design.vocabulary` import at `pipeline.py:74-77`.) The old comment about
"the parent must be a branch THIS RUN proposed, never a folder the person
already had" (`:1242-1250`) is kept true by construction: `98` is a proposal.

`cli._residual_library` (`:5037-5075`): the user-defined tuple always begins
with `ResidualTemplate(template_name=ARCHIVE, display_name=ARCHIVE, ...,
treatment=TREATMENT_RETAINED, user_defined=True)` under amendment 13, before
the person's own `--define-residual` ones; and `residual_library` at
`cli.py:16188` is built unconditionally (it is a library, not an enablement —
enablement is still `residual_choices`, which stays empty unless typed).

- [ ] **Step 4: Run** `nice -n 15 python3 -m pytest tests/p10/test_p10_pipeline.py tests/p10/test_p10_residuals.py tests/p10/test_p10_freeze.py tests/p11 -p no:randomly -q`. A p10 test pinning the first-branch parent is superseded by amendment 13 and is rewritten to the root, with the amendment cited in its docstring.
- [ ] **Step 5: Commit.** `feat(106 Phase 7.8 × 00 amendment 13): residual homes live under a root-level 98 Review and Unsorted, minted only when something is under it`

### Task 7.9: The homes the sets need are minted after placement, on demand

**Files:** Modify `src/tree_design/pipeline.py` (new `mint_review_homes`, beside
`mint_scoped_generals` `:964-1020`) · Modify `src/cli.py` (new
`mint_review_homes_on_demand` beside `mint_generals_on_demand` `:15349`, called
right after `:19365-19369` and before the `--send-set` block at `:19430`) ·
Test `tests/p10/test_p10_the_general_on_demand.py` (sibling file, same
harness) and `tests/p11/test_p11_residual_send.py`.

**The decision point named in §D.5:** the `disposition` below is
`PHYSICAL_DESTINATION`. If the owner keeps the authored `reviewed` treatment
for the auto-enabled copies, the one line changes to
`disposition_for_treatment(library[name].treatment)` and everything else in
this task stands.

- [ ] **Step 1: Failing tests** (in `tests/p10/test_p10_the_general_on_demand.py`'s own harness — it drives one tree and one set of decisions through the on-demand step, which is the shape this step copies):

```python
def test_a_run_with_leftover_sets_gains_the_homes_they_are_offered(finished_run):
    """`00` amendment 13, minted the way `00`:99's General is: after placement
    proved the need. One set keyed `screenshots` -> `98 / Temporary
    Screenshots` exists in the re-frozen tree, is a residual node, and is a
    legal destination. SABOTAGE: mint nothing -- the screen offers a home
    `approved_residual_area` cannot find, and `--send-set` is refused."""
    from tree_design.vocabulary import RESIDUAL, REVIEW_AND_UNSORTED, TEMPORARY_SCREENSHOTS

    after = cli.mint_review_homes_on_demand(finished_run.conn, finished_run.result, **finished_run.args)
    nodes = {n.node_id: n for n in after.tree.tree.nodes}
    home = next(n for n in nodes.values()
                if n.node_role == RESIDUAL and n.display_label == TEMPORARY_SCREENSHOTS)
    assert nodes[home.parent_node_id].display_label == REVIEW_AND_UNSORTED
    assert home.node_id in after.tree.tree.freeze_record.legal_destination_ids


def test_a_run_with_no_ordinary_set_mints_nothing(finished_run_with_only_a_protected_set):
    """"Nothing happens when nothing is demanded" (`mint_generals_on_demand`)."""
    run = finished_run_with_only_a_protected_set
    after = cli.mint_review_homes_on_demand(run.conn, run.result, **run.args)
    assert after is run.result


def test_every_decision_is_carried_onto_the_re_frozen_version(finished_run):
    """§8.8: the decisions the report joins by node id name the version the
    person is shown. `carry_onto` re-projects them; `into_general` is empty
    because no file moves here -- the homes are OFFERED, not filled."""
    after = cli.mint_review_homes_on_demand(finished_run.conn, finished_run.result, **finished_run.args)
    ids = {n.node_id for n in after.tree.tree.nodes}
    assert all(d.destination is None or d.destination.node_id in ids
               for d in after.placement.decisions)
```

- [ ] **Step 2: Run** → `AttributeError: mint_review_homes_on_demand`.

- [ ] **Step 3: Implement.** `pipeline.py`, after `mint_scoped_generals`:

```python
def mint_review_homes(conn: sqlite3.Connection, *,
                      authorities: TreeDesignAuthorities,
                      decisions: TreeDesignDecisions,
                      tree: TreeDesignResult,
                      homes: Sequence[str],
                      disposition: str) -> TreeDesignResult:
    """`00` amendment 13's homes, minted AFTER placement proved which sets exist.

    The tree freezes before placement (`STEPS`) and §7.5's sets exist only
    after it, so a home a set is offered can only be added the way `00`:99's
    General is: a draft opened from the frozen version, the nodes written,
    the version frozen again. Returns `tree` unchanged, having written
    NOTHING, when `homes` is empty.
    """
    if not homes:
        return tree
    groups, _folders, areas, _moves = _upstream(conn, authorities, decisions)
    version = authorities.mint_version_id()
    open_draft(conn, from_version=tree.tree.plan_version_id,
               new_version_id=version, created_at=decisions.created_at,
               mint_node_id=authorities.mint_node_id)
    choices = tuple(ResidualChoice(
        template_name=name, action=ENABLE, disposition=disposition,
        display_label=None, parent_node_id=None,
        root_anchor=authorities.root_anchor, merge_into=None,
        replaces_node_id=None) for name in homes)
    enable_review_homes(conn, authorities, decisions, version=version, choices=choices)
    profiles = build_profiles(
        conn, plan_version_id=version,
        groups_by_id={group.group_id: group for group in groups},
        document_types_by_node={}, anchor_excerpts_by_node={},
        user_edits_by_node={}, node_scoped_rejections={})
    freeze(
        conn, plan_version_id=version, created_at=decisions.created_at,
        user_id=decisions.user_id, surface=decisions.surface,
        component_version=decisions.component_version,
        residual_configuration={**decisions.residual_configuration,
                                **{name: ENABLE for name in homes}},
        approved_branch_ids=tuple(
            node.node_id for node in nodes_for_version(conn, version)
            if node.accepts_placement),
        profiles=profiles, protected_areas=areas,
        catalogue_release_id=getattr(authorities.catalogue, "release_id", None),
        template_versions=tree.tree.freeze_record.template_versions)
    return dataclasses.replace(
        tree, tree=frozen_tree(conn, plan_version=version),
        plan_version_ids=tree.plan_version_ids + (version,))
```

(`open_draft` joins the `tree_design.store` import at `pipeline.py:61-63`;
`ENABLE` the vocabulary import.) `cli.py`, beside `mint_generals_on_demand`:

```python
def mint_review_homes_on_demand(conn: sqlite3.Connection, finished, *,
                                authorities: TreeDesignAuthorities,
                                decisions: TreeDesignDecisions,
                                placement_inputs,
                                component_version: str, observed_at: str):
    """`00` amendment 13, the step after the General's: the homes the leftover
    sets are offered exist in the tree before the screen offers them.

    NOTHING HAPPENS WHEN NO ORDINARY SET WAS SURFACED, and a home already in
    the tree (the person enabled it by `--residual`) is not minted twice:
    `project_residual_nodes` refuses two decisions for one template, and this
    reads the tree first so it never asks for one.
    """
    have = {node.display_label for node in finished.tree.tree.nodes
            if node.node_role == tv.RESIDUAL}
    homes = tuple(dict.fromkeys(
        REVIEW_HOME_FOR_SET[item.set_key]
        for item in finished.placement.residual_sets
        if not item.protected and item.set_key in REVIEW_HOME_FOR_SET
        and REVIEW_HOME_FOR_SET[item.set_key] not in have))
    if not homes:
        return finished
    before = finished.tree.tree
    tree = mint_review_homes(
        conn, authorities=authorities, decisions=decisions,
        tree=finished.tree, homes=homes,
        # `00` amendment 13: the person is offered the home and nothing moves
        # until they accept -- `run_residual_file` files with
        # `unique_direct_match=False`, so every filing here is REVIEW_REQUIRED
        # (`placement/pipeline.py:4833`). The disposition is the owner's under
        # the amendment; see `106` Phase 7 §D.5 for the alternative.
        disposition=tv.PHYSICAL_DESTINATION)
    inputs = placement_inputs(tree)
    build_destination_index(
        conn, tree.tree, component_version=component_version,
        observed_at=observed_at, canonical=inputs.canonical_value)
    return dataclasses.replace(
        finished, tree=tree,
        placement=dataclasses.replace(
            finished.placement,
            decisions=carry_onto(
                conn, decisions=finished.placement.decisions,
                from_tree=before, to_tree=tree.tree, into_general={},
                component_version=component_version, observed_at=observed_at)))
```

Called at `cli.py:19369`, immediately after `mint_generals_on_demand` returns
and with the same `authorities`/`decisions`, so the version the sets are
answered against (`act_on_residual_sets` at `:19511`, through
`placement_inputs(result.tree)`) is the one that holds the homes — the
handoff §D.4 verified.

- [ ] **Step 4: Run** `nice -n 15 python3 -m pytest tests/p10/test_p10_the_general_on_demand.py tests/p11/test_p11_residual_send.py tests/p11/test_p11_residual_sets.py tests/apply -p no:randomly -q`. Then the eleven-file integration corpus (`tests/integration/test_the_question_at_the_end_and_the_sort.py`), which has two held files and will now mint `98`.
- [ ] **Step 5: Commit.** `feat(106 Phase 7.9 × 00 amendment 13): the homes the leftover sets are offered are minted after placement, on demand, and every decision is carried onto the re-frozen version`

### Task 7.10: The screen offers each set its home, by name and by command

**Files:** Modify `src/cli.py:21750-21930` (`_review_note`) and its callers ·
Test `tests/test_cli_report_at_scale.py`.

- [ ] **Step 1: Failing test:**

```python
def test_a_held_set_is_offered_its_home_and_the_command_that_takes_it():
    """`00` amendment 13: "every one is offered to the person before anything
    moves". SABOTAGE: print `areas[0]` -- every set is offered the same area,
    and the first enabled area is whichever sorted first."""
    screenshots = _set("Screenshots with no accepted project or event", ("f1",),
                       REASON, key=cli.SCREENSHOT_REVIEW_SET)
    locked = _set("Unsupported or encrypted", ("f2",), REASON,
                  key=cli.UNSUPPORTED_REVIEW_SET)
    run = _run(
        nodes=(_node("n_98", "98 Review and Unsorted"),
               _node("n_ts", "Temporary Screenshots", parent="n_98", role="residual"),
               _node("n_ue", "Unsupported or Encrypted", parent="n_98", role="residual")),
        decisions=(_decision(file_id="f1", explanation=REASON),
                   _decision(file_id="f2", explanation=REASON)),
        sets=(screenshots, locked))
    said = _printed(run, {"f1": "a.png", "f2": "b.zip"})
    assert "Offered home: 98 Review and Unsorted / Temporary Screenshots" in said
    assert "--send-set 'Screenshots with no accepted project or event=Temporary Screenshots'" in said
    assert "--send-set 'Unsupported or encrypted=Unsupported or Encrypted'" in said
    assert "nowhere to put them yet" not in said
```

(`_set`, `_node`, `_decision`, `_run`, `_printed` and `REASON` are that file's
own helpers, `tests/test_cli_report_at_scale.py:67-163`; `_set` gains a
`key=""` keyword that it passes through as `set_key`. `_node`'s `role`
keyword already exists at `:75`; a residual node needs a disposition, so the
helper passes `disposition="physical-destination"` when `role == "residual"`.
`test_with_no_area_enabled_the_report_says_how_to_make_one_and_names_the_sets`
(`:389`) pins the closing sentence this task rewrites; it is updated to the
new words with the amendment cited.)

- [ ] **Step 2: Run** → the `Offered home` line is absent and both sets carry `areas[0]`.
- [ ] **Step 3: Implement.** `_review_note` gains `home_for: Callable[[object], str | None]`
(the caller passes `lambda item: REVIEW_HOME_FOR_SET.get(item.set_key)`) and,
where it prints the three commands (`:21880-21891`):

```python
            offered = home_for(item)
            if offered is not None and offered in areas:
                lines.append(f"Offered home: {REVIEW_AND_UNSORTED} / {offered}"
                             if offered != ARCHIVE else f"Offered home: {ARCHIVE}")
                lines.append(f'      --send-set {shlex.quote(f"{item.label}={offered}")}')
            elif areas:
                lines.append(f'      --send-set {shlex.quote(f"{item.label}={areas[0]}")}')
            lines.append(f'      --leave-set {shlex.quote(item.label)}')
            lines.append(f'      --review-set {shlex.quote(item.label)}')
```

The closing sentence `"This plan has nowhere to put them yet..."` (`:21903-21907`)
stays reachable only when no home was minted for any ordinary set, which after
Task 7.9 means a set whose key is a block; its words change to say that:
*"These are waiting on you, not on a folder: answer what is asked above and
they are placed like any other file."*

- [ ] **Step 4: Run** `nice -n 15 python3 -m pytest tests/test_cli_report_at_scale.py tests/p13 -p no:randomly -q`, then the integration corpus.
- [ ] **Step 5: Commit.** `feat(106 Phase 7.10): every leftover set is offered its home on the screen, with the command that takes it`

### Task 7.11: The gate, as a script

**Files:** Create `tools/groundtruth/phase7_gate.py` (read-only over a run
database; prints counts only; no path, no filename, no label from the corpus).

```python
"""`106` Phase 7's gate over one run database. Aggregates only.

Usage: python3 tools/groundtruth/phase7_gate.py ~/.graph-agent/lead/corpus2-gate1/runNN.sqlite
"""
from __future__ import annotations

import sqlite3
import sys

LATEST = ("SELECT plan_version_id FROM plan_versions WHERE state = 'frozen' "
          "ORDER BY created_at DESC LIMIT 1")

DEPTH = """
WITH RECURSIVE walk(node_id, depth) AS (
    SELECT node_id, 0 FROM tree_nodes WHERE plan_version_id = :v AND parent_node_id IS NULL
    UNION ALL
    SELECT n.node_id, w.depth + 1 FROM tree_nodes n JOIN walk w ON n.parent_node_id = w.node_id
    WHERE n.plan_version_id = :v)
SELECT depth, COUNT(*) FROM walk GROUP BY depth ORDER BY depth
"""

SINGLE_FILE_ROOTS = """
SELECT COUNT(*) FROM tree_nodes n
LEFT JOIN directory_inventory d
       ON d.directory_path = n.existing_path
      -- the LATEST scan only: a database rescanned holds one inventory row
      -- per scan per directory, and joining them all would count each root
      -- once per scan
      AND d.scan_run_id = (SELECT scan_run_id FROM scan_runs ORDER BY rowid DESC LIMIT 1)
WHERE n.plan_version_id = :v AND n.parent_node_id IS NULL AND n.node_type = 'existing'
  AND d.file_count = 1 AND d.subdirectory_count = 0
"""

SETS_WITHOUT_A_HOME = """
SELECT COUNT(*) FROM residual_sets s
WHERE json_extract(s.payload, '$.protected') = 0
  AND json_extract(s.payload, '$.set_key') IN (:ordinary_keys)
  AND NOT EXISTS (
      SELECT 1 FROM tree_nodes n
      WHERE n.plan_version_id = :v AND n.node_role = 'residual'
        AND n.display_label = :home_of_key)
"""


def main(path: str) -> int:
    from cli import REVIEW_HOME_FOR_SET  # the one table, not a copy of it

    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    v = conn.execute(LATEST).fetchone()[0]
    print("depth distribution (depth: folders):",
          dict(conn.execute(DEPTH, {"v": v}).fetchall()))
    single = conn.execute(SINGLE_FILE_ROOTS, {"v": v}).fetchone()[0]
    print("single-file roots:", single)
    unhomed = 0
    for key, home in REVIEW_HOME_FOR_SET.items():
        unhomed += conn.execute(
            "SELECT COUNT(*) FROM residual_sets s WHERE json_extract(s.payload,'$.protected')=0 "
            "AND json_extract(s.payload,'$.set_key') = ? AND NOT EXISTS (SELECT 1 FROM tree_nodes n "
            "WHERE n.plan_version_id = ? AND n.node_role = 'residual' AND n.display_label = ?)",
            (key, v, home)).fetchone()[0]
    print("ordinary review sets with no offered home in the tree:", unhomed)
    return 0 if single == 0 and unhomed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
```

(The `SETS_WITHOUT_A_HOME` constant is illustrative; the loop is the query
that runs, one per key, because SQLite has no parameterised `IN`. Written out
so the reviewer sees the shape; delete the constant when the loop is kept.)

- [ ] **Run** `GRAPH_AGENT_NO_DOTENV=1 python3 tools/groundtruth/phase7_gate.py <run>.sqlite`. Commit with the phase.

---

## F. The gate

Measured by `tools/groundtruth/phase7_gate.py` on a re-run of the owner's
corpus (lead only; aggregates only), on the LATEST FROZEN plan version:

1. **Depth distribution matches the reference's shape.** The number to print
   is the histogram `{depth: folders}`. The reference is uneven: a few roots
   (fewer than sixteen — Phase 3's gate), most folders at depth 1-2, some at
   3-4, and NO chain of single folders that ends in a folder holding all of
   its parent's files. The second half is the query below and must be **0**:

   ```sql
   -- single-child runs that never divide: a node with exactly one child whose
   -- child has no children -- the shape Task 7.3 folds
   WITH kids AS (SELECT parent_node_id AS p, COUNT(*) AS n FROM tree_nodes
                 WHERE plan_version_id = :v AND parent_node_id IS NOT NULL GROUP BY parent_node_id)
   SELECT COUNT(*) FROM tree_nodes n JOIN kids ON kids.p = n.node_id AND kids.n = 1
   JOIN tree_nodes c ON c.parent_node_id = n.node_id AND c.plan_version_id = :v
   LEFT JOIN kids gk ON gk.p = c.node_id
   WHERE n.plan_version_id = :v AND n.parent_node_id IS NOT NULL AND gk.n IS NULL;
   ```

   Before Phase 6 the histogram will be nearly flat (`104`:2785-2800 explains
   why) and the query is trivially 0; **the shape half of this gate is
   observable only after Phase 6's gate is met.** Say so on the screen that
   reports it.
2. **No single-file root:** `SINGLE_FILE_ROOTS` = 0, and, from §C's producer
   query, `bundle_shaped` under `existing` = 0 (a package at the root is P3's
   and is reported, not hidden, if it is non-zero).
3. **Every ordinary residual set carries an offered home** that exists as a
   residual node in the frozen tree: `unhomed` = 0. Protected sets are counted
   and offered nothing, by the standing rule.
4. **Nothing moved:** the corpus on disk is byte-identical before and after the
   run (`tests/integration`'s `_on_disk` comparison), because every filing
   into `98`/`99` is `REVIEW_REQUIRED` and the run carried no `--apply`.

---

## G. Ordering — what is unblocked today

| task | needs | buildable before Phases 3, 4, 6? |
| --- | --- | --- |
| 7.1 flatten measure | nothing | **yes** |
| 7.2 folder-per-file fold | nothing | **yes** — but on today's corpus it has almost nothing to fold (3 second-level nodes); its proof is the unit tests, and its effect is visible only after Phase 6 |
| 7.3 single-child-run fold | 7.2 | **yes**, same caveat |
| 7.4 outline words | 7.3 | **yes** |
| 7.5 one-file directory is not a branch | nothing | **yes**, and it removes one of the seven roots on the next run without waiting for anything — unless §C's query says the root is a package (P3, owner's call) |
| 7.6 protected root words | nothing | **yes** |
| 7.7 set keys, two characteristics, offer table | nothing | **yes** |
| 7.8 `98` root, homes under it | 7.7 (the names) | **yes** |
| 7.9 mint on demand | 7.7, 7.8, and the owner's word on the disposition (§D.5) | **yes** once that word is given; it is one line either way |
| 7.10 the offer on the screen | 7.9 | **yes** |
| 7.11 gate script | 7.7 | **yes**; its depth half reports honestly that Phase 6 has not landed |

**What Phases 3 and 4 must respect when they land.** Phase 3 changes root
LABELS (`partition_by_branch` keyed on a life); it changes nothing here.
Phase 4's fold of group cards into areas must exclude the `98` root, the `99`
home and every adopted `existing` folder — they are not group cards — and the
proposed `98` root must not be counted among the "lives" Phase 3's gate
counts against sixteen: it is the reference's own `98`, by the owner's word.

**What only Phase 6 unlocks.** The depth half of the gate. Every fold above
is a rule about levels that exist; Phase 6 is what makes levels exist on this
corpus. This draft claims no depth it cannot show.

---

## What this plan does not claim

- **Only Phase 6 raises depth**, and its ceiling is unmeasured. Phases 3 and 4 fix what branches are called and how many there are; they add no level to any branch. Say so on any screen reporting progress.
- **The 87 files the gate refused are not a bug** (`104` §18.102) and no phase here recovers them. They need a run with a local model, or the owner's release.
- **The classifier is done for now** at 97.7 % key-in-what-it-said. Further prompt work is not where the remaining value is.
- **Sixteen lives is a menu, not a target.** A tree that shows sixteen has failed amendment 12a.

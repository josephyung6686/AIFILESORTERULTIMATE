# 109 — ACTION PLAN, 19 September 2026

Written after reading `108`, `104` §18.115, and the seam itself. **Two claims in
`108` are corrected here by reading the code; they are marked CORRECTION.** Where
a line number is given it was read today at `42d029cf`.

The order is: what can be built with nobody's permission, what is ratified but
blocked on a mechanism, what is the owner's alone. Nothing in Tier A needs an
answer from the owner. Tiers B and C are listed so the work is not re-discovered,
not so it is started.

---

## Tier A — buildable now, no owner input

### A1. The unsettled default must still build the rest of the tree  ← START HERE

`downstream` returns `None` whenever `of_the_run` is empty (`src/cli.py:20296`),
and `of_the_run` is filled at `src/cli.py:18970` **only** when
`partition.default.settled`. So a corpus whose default branch nobody has named
prints the question and yields NO TREE — the settled branches lose their folders
too. This is the whole of what blocks an end-to-end demonstration.

**CORRECTION to `108` §2 — the seam is five call sites over three functions, not
six scattered ones, and most of the pipeline is ALREADY taught.** `src/cli.py:19091`
computes `unsettled = not of_the_run` and guards the fact pass with it
(`19094`, `19105`, `19129`, `19178`, `19519`). The branch-situation readers
(`18511`, `18537`, `18544`, `18650`, `18656`, `18739`) are guarded. Site E/B are
gated behind `going_on` (`20165`), which already includes `bool(of_the_run)`, so
`20193` is safe. What is genuinely unguarded and reached once the early return
lifts:

```
16979   run_signal=said().signal                  _signals_for_branch
17185   group_category=said().schema              draft path, partition.single
17186   label=said().label                                "
17192   group_category=said().schema              draft path, multi-branch
17193   label=said().label                                "
17202   label=said().label                        accept_drafted_groups
20360   group_level_fields=said().group_level_fields   CorpusAuthorities
16765   or (said().schema,)                       DEAD while a partition exists
```

**CORRECTION to the assumption that `said().label` is the closure's `label`.** It
is not: `_the_situation_of_a_run` sets `label=schema if label is None else label`
(`src/cli.py:16513`). With no situation there is no schema to fall back to, so
"what is this draft called" is a real question, not a rename.

**Scope, from `00` amendment 25 and no further.** The ratified text is that the
unjudged default has no folders beneath IT. Building folders for it would overshoot
the ruling; dropping its files would break coverage. The files under an unsettled
default rest visibly at the default node, and the question still prints.

- [ ] **Step 1: read what the draft path already does per branch.** Read
  `draft_for_review` (`src/cli.py:11267`) and its handling of `group_category` and `label` when
  `branch_for=`, `default_branch=` and `schema_of_file=` are passed (they already
  are, `src/cli.py:17192-17203`). If it is per-branch throughout, `said().schema`
  at `17192` is a dead fallback and the fix there is deleting a fallback, not
  inventing a value. Record which of the five sites that leaves.

- [ ] **Step 2: write the failing acceptance test.** A partition with one settled
  branch and an unsettled default. **The fixture already exists** — copy
  `_partition(..., default_situation=None)` from
  `tests/test_branch_situation_lives.py:39`; its line 94 says in words that this
  builds an unsettled default. Do not invent a partition builder. Assert three things, all three in one test so a
  later change cannot satisfy one by breaking another:

```python
def test_a_settled_branch_still_gets_its_tree_while_the_default_is_unsettled():
    result = run(...)                      # partition: one settled branch + unsettled default
    assert result is not None              # the run does not end at the question
    assert tree_paths_under(result, settled_branch_label)     # the settled branch has its levels
    assert files_under(result, default_node) == default_branch_file_ids  # coverage: nothing dropped
    assert folder_levels_under(result, default_node) == ()    # amendment 25: no folders beneath it
    assert the_question_was_printed(out)   # the question is not swallowed by the fix
```

- [ ] **Step 3: run it, confirm it fails** on the `return None` at `20296` (not on a
  fixture error — read the failure text before writing code).

- [ ] **Step 4: lift the early return for the multi-branch case only.** Continue past
  `if not of_the_run:` when the partition has any settled branch; keep returning
  `None` when the partition is `single` and unsettled, because a lone unsettled
  branch genuinely has nothing to build. Print the question in both paths — the
  print already sits above both exits (`20259`'s comment says so; verify it still
  does after the edit).

- [ ] **Step 5: teach the five sites,** each with its own reason written beside it:
  `16979` (signal for an unsettled branch), `17185/17186` and `17192/17193/17202`
  (what a draft under an unsettled default is called — per Step 1 this may be a
  deletion), `20360` (`group_level_fields` for a run with no run-situation).
  `16765` is dead while a partition exists; leave it and say so in the comment.

- [ ] **Step 6: parse-check and run.** `python -m py_compile src/cli.py` — a
  `cli.py` that did not parse has been committed on this branch before. Then the
  new test, then the P11 and branch-situation suites. **One pytest session at a
  time.**

- [ ] **Step 7: P11 — decide what the unsettled default's root node wears.** P11 is
  reached only once `downstream` returns authorities, so it has never run in this
  state. **It is not a sixth `said()` reader** — `the_situation_each_branch_carries`
  (`src/cli.py:7388`) keys off `Branch.folder_name` and P11 matches that against the
  root node's `display_label` (`placement/pipeline.py:1790`), with the situation read
  per file through `situation_of`. Two questions follow, and Step 7 is not done until
  both are answered in a test: what name the unsettled default's root node carries
  when nobody has authored one, and what its entry in that map is — because that map
  is what tells P11 which branches to LEAVE ALONE, and amendment 25 says no folders
  may appear beneath the unjudged default. An absent or empty entry that makes the
  default look placeable is the failure mode to write red first.
  `tests/test_p11_guard_is_keyed_by_the_name_the_root_node_wears.py` exists because
  this guard already went silently inert once (`9b85210f`); a green suite is not
  evidence here.

**A1 leaves one thing worse, and it is named here so it is not discovered later.**
`going_on = stop_after is None and bool(of_the_run)` (`src/cli.py:20165`) gates
sites E and B. Under the minimal fix `of_the_run` stays empty for an untyped
corpus, so **E and B do not run for the SETTLED branches either** — a loss that did
not exist before amendment 25, when site G could settle the default. A1 leaves it
gated deliberately (the deterministic path is a complete path, `20320`), and
re-gating it per branch is the first follow-up after A1 lands.

- [ ] **Step 8: commit per deliverable,** `feat(109-A1): ...`, ending with the
  Co-Authored-By and Claude-Session lines. Never `git add -A`; `.claude/` is
  untracked and holds eleven stale `cli.py` copies — never stage it.

### A1 — MEASURED AND BUILT, 19 Sep. What the run actually did.

Reproduced without a model, on `test_r37_per_branch_situation`'s two-life corpus,
answering ONE branch and leaving the default unsettled
(`--answer situation:career=career.recruiting --accept-groups`):

```
before   tree_nodes 0   group_acceptance 0   placement_decisions  0
after    tree_nodes 4   group_acceptance 4   placement_decisions 20
control  (--situation academic.coursework --accept-groups, same corpus and flags)
         tree_nodes 4 per version, WITH LEVELS: Coursework/{lecture,notes,syllabus}
```

Pinned by `tests/integration/test_an_unsettled_default_still_builds_the_rest.py`
(3 tests: the settled branch is built; the question is still printed; no file is
dropped). The first was red for the right reason before the fix and is green after.

**The seam was FOUR live sites, not five and not `108`'s six.** Two of the five the
plan named turned out to be unreachable or dead, and one the plan did not name was
the one that actually refused:

| site | what it needed |
| --- | --- |
| `_signals_for_branch` | `run_signal` is read only for a group NO branch reaches; an unsettled run has no word to offer there, so that case is `frozenset()` — decided before the call, because Python evaluates the argument either way |
| `draft_for_review`, multi-branch | `group_category`/`label` are **NOT READ** on this path (`_grouped_by_branch` names each draft after its own branch) but are evaluated eagerly — this is the site that refused after the early return was lifted, and the plan had marked it dead rather than dangerous |
| `accept_drafted_groups` | `label` reaches ONE human sentence; the default branch's own name is the honest value |
| `GroupingKnowledge.group_level_fields` | a situation's, so a run with none withholds nothing |
| `partition.single` path | unreachable: a lone unsettled branch still returns `None` |
| `active_domains` | dead while a partition exists — `or` short-circuits on a non-empty dict |

**A lesson worth the line:** the first edit dropped the paren that closed
`GroupingKnowledge(` and `python -m py_compile src/cli.py` caught it in one second.
`108` §7's "parse-check every file you edit" earned its place again.

**TWO THINGS THIS EXPOSED, both real, neither fixed here:**

1. **The disclosure line at `cli.py:22339` is false on an untyped run.** *"What to
   call the top-level folder, and what kind of material this is — taken from
   `--label` and `--situation` exactly as you typed them, and applied to EVERY file
   in the folder"*. Nothing was typed, and each branch now carries its own
   situation. That screen was unreachable on an untyped run before A1 and is
   reachable now, so the fix made a lie visible rather than writing one.
2. **TWO BRANCHES MINT ONE QUESTION ID, AND ONE OF THEM IS SILENTLY DROPPED.**
   Traced in code, not inferred. `cli.py:18921` keys the question
   `branch_label=(branch.label if branch.is_default else branch.schemas[0])`;
   `questions/triggers.py:366` builds `question_id=f"{SITUATION_KIND.kind_id}:{branch_label}"`;
   `questions/store.record_question` is `ON CONFLICT (question_id) DO NOTHING`. On
   an UNTYPED run the default's label is its majority kind, so a default whose
   majority kind is `academic` and a sibling life branch whose `schemas[0]` is
   `academic` both mint `situation:academic`.

   **Both are printed** — they are appended to `asked` in the same loop — **and
   only the first is stored.** The person is shown two questions, one of which does
   not exist in the store; the options printed under it are the OTHER branch's; and
   answering settles whichever branch was recorded first. The second branch's files
   can never be answered for at all. Reproduced on the A1 fixture: the screen asks
   "Which of these is academic?" twice, for a 1-file default and a 4-file branch.

   **NOT FIXED HERE, deliberately.** That key is what every reader of the person's
   answer joins on — `_the_situation_the_person_chose`, the partition's arm 0, the
   resolver loop — and `18921`'s own comment says it is "the key every answer
   already in the person's database was filed under while a kind was a branch".
   Changing it migrates answers the owner has already given. The owner picks: a
   composite key (life + kind), or a branch id no display string can collide with.

---

### A2. The amendment-16 residual regression (`108` §4)

A file under a two-kind life branch, whose kind came from a deterministic ANCHOR
and which site G left silent, gets no question; before the Education ruling it had
its own one-kind branch and was asked. Declared in `e9b7c550`. Needs `kind_of` on
`Branch`. Do it after A1 — A1 changes the same paths.

### A3. The grader, so 97.7 % can be re-claimed (`108` §5)

`106` Phase 2(b) changed the situation fact from holding the KIND to holding the
SITUATION. The grader's prefix fallback would score a real disagreement as a match,
so the number may not be quoted until the grader prefers the fact's own value where
it is already a situation id. Until then **97.7 % is not a current measurement** —
do not print it in any report.

### A4. `test_r37_*` — diff, do not recapture

They were byte-identical to the pre-change baseline when last diffed. A recapture
that is not diffed proves only that the code equals itself.

*(Usage note, not a task: `tools/groundtruth/measure.py` refuses on the owner's
database because it holds two frozen plans. Pass `--plan-version`.)*

---

## Tier B — ratified, blocked on a mechanism, not on a decision

| ruling | the missing mechanism | what unblocks it |
| --- | --- | --- |
| **19** club → its host school | a `school` fact per file; the SHOW and `--confirm` exist (`6bbfae67`), the routing does not | the coursework sheet's `My school` column (`108` §9). Building the routing against a fixture first is buildable but is building ahead of the data — say so before starting. 36 files have no life until it lands. |
| **22** `year` as a folder level | rows cannot do it: `folder_levels_for` (**`src/production.py:564`** — `108` cites `src/tree_design/production.py:610-616`, which does not exist) iterates `definition.default_order.dimensions` alone, so a `role_bindings` entry whose role is not a dimension is silently DROPPED | a dimension in `definitions.json` **and a fork named, not picked**: one default order cannot serve both `employer → year` and `year → organization`. Two templates, or an order that varies by situation. The owner chooses. |
| **21** Health and Travel situations | rows exist at `src/tree_design/library/drafts/health_travel.json`, wired to nothing, with a gate test asserting their absence from the release | the owner ratifying three names. **`travel.trip-records` is a NEW name that would enter the `finance` menu, which goes to the CLOUD.** Do not wire before ratification. |

---

## Tier C — the owner's alone

`108` §9 is the list. `00` amendment 24 is how to put it: separate **preference**
(which level comes first, what a life is called, whether Education holds research)
from **truth** (that `year` and `tax_year` are different ideas, that a derivation
cannot outrank its source, that medical records reach no model). Only the second
kind is the library's to settle; most of 18 Sep's questions should have been a
setting. `107` promises *"every split can be changed before freeze"* and **that
control does not exist** — building it would retire a whole class of question.

The eleven `[TRUNCATED]` lines in `107` stay truncated. Ask; do not reconstruct.

The **111 → 25 over-protected files** narrowing sends more material off-device and
is gated by the privacy classifier: escalate to the owner, never reformulate to pass.

---

## The competitor question, answered (`104` §18.115 extended)

**Sub-second is true per file and false per corpus, and the figure that looks like
a benchmark is about people, not machines.** They publish no latency benchmark at
all. What they publish is whole-corpus: "5 to 30 minutes for thousands of files",
which amortises to roughly **0.06–1.8 s per file** — so a per-file sub-second claim
is defensible, and a "organises your drive in under a second" claim is not. Their
own published numbers:

```
auto-organisation      "5 to 30 minutes for thousands of files"
bulk sort by type/date "2 to 8 hours for thousands of files"
manual                 "20 to 80 hours for thousands of files"
per file               "in seconds"  (no SLA, no benchmark published)
/decide                5 minute timeout, `sync=false` for async
batch limits           /analyze/batch 10 · /extract/batch 20 · /analyze/cross 2-5
accuracy, admitted     "review and adjust 10 to 15 percent of the categorizations"
```

The "under three seconds" in `108` §10 is their post-mortem sentence *"Approvals
cleared in under three seconds each"* — how fast a person clicked approve, which is
their argument that **an approval nobody considered is not a control.** It is a
warning aimed at this product's approve step, not a latency to match.

**Where the speed actually comes from, and it is not infrastructure.** One
`/decide` call per file against folders the PERSON already authored, run
concurrently (`/analyze/batch` 10, `/extract/batch` 20, async jobs with webhook
callbacks), over frontier models they do not own. No tree is invented, so no pass
has to reason about the corpus as a whole — the expensive part of this product is
the part they deleted. Nothing in their stack is faster than what is already wired
here; their pipeline is shorter.

**Their infrastructure, from their own material:** a public HTTP API
(`/extract`, `/analyze`, `/analyze/batch`, `/cross-analyze`, `/decide`,
`/markdown`, `/thumbnails`) with async jobs, polling and webhooks; Python and
TypeScript SDKs; docs in MDX; four public repos, the newest `docs` (Aug 2026).
Models are listed to users as "Multiple (GPT-5, Claude)" — a router over frontier
providers, no model of their own. Hosting is "industry-leading cloud providers"
with SOC 2 Type II / ISO 27001, TLS 1.2+, AES-256 at rest, Stripe for payments;
the provider is not named and no region list is published. Two employees, ~$30K
raised (`104` §18.115). **There is no fast infrastructure secret here to copy.**

**The comparison to make is not speed — it is that a tool which cannot invent the
tree has to ask the person to, and they wrote in public that no tool can do it.**

### The one thing worth building from them

Nothing in this repository measures whether an approval was considered. Their
failure says that is the soft spot in the safety story. It is a small thing —
record what was on the screen when the person approved and how long it was there —
and it is not in Tier A because it is a new measurement, not a repair. Raise it
with the owner before building it.

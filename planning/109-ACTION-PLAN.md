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
   only the first is stored.** Reproduced on the A1 fixture: the screen asks
   "Which of these is academic?" twice, for a 1-file default and a 4-file branch.

   **CORRECTION to this row's first draft, measured.** I wrote that the second
   branch's files "can never be answered for at all". They can: one
   `--answer situation:academic=academic.coursework` clears BOTH questions, because
   the answer is read at the KIND's scope and both branches are that kind. The real
   harm is narrower and still real — **two branches of one kind cannot be given
   DIFFERENT answers.** A default that is coursework beside a sibling branch that is
   teaching is inexpressible: one key, one stored question, one answer for both. The
   options printed under the dropped question are the other branch's, too.

   **NOT FIXED HERE, deliberately.** That key is what every reader of the person's
   answer joins on — `_the_situation_the_person_chose`, the partition's arm 0, the
   resolver loop — and `18921`'s own comment says it is "the key every answer
   already in the person's database was filed under while a kind was a branch".
   Changing it migrates answers the owner has already given. The owner picks: a
   composite key (life + kind), or a branch id no display string can collide with.

3. **THE PLAN RECORD SAYS THE OPPOSITE OF THE SCREEN, about the same folder.** In
   A1's own tree dump, a branch with NO child node beneath it is stored with
   `refinement_disposition: 'refined'` and
   `refinement_reason: 'The rules built the levels beneath this branch from facts
   that were already settled in your files.'` No levels were built beneath it —
   that is amendment 25 working — so the record claims work the run did not do, for
   a folder whose question is still on the screen unanswered.

   This is `cli.py:22339`'s defect one layer down: 22339 lies to the person on the
   screen, this lies to whoever reads the plan database afterwards, and a `refined`
   folder that nobody judged is exactly the state amendment 25 exists to make
   visible. Both are one-line-ish and both are user-facing wording, so they belong
   in one commit once the owner has ruled on the fold (A1.5) — recapturing the
   freeze fixture will touch the same screens.

---

### A1 — VERIFIED CLEAN, and the suite is NOT green on this branch

Baseline-vs-fix, the whole integration directory, one pytest session at a time,
pristine worktree at `03afe9c6` versus the working tree:

```
baseline   15 failed, 1484 passed, 20 skipped, 6 xfailed, 19 errors
A1         15 failed, 1487 passed, 20 skipped, 6 xfailed, 19 errors
```

**The two FAILED/ERROR lists are byte-identical** (34 lines, `diff` empty) and A1
adds exactly the +3 passes of its own tests. **A1 introduces no regression.**

**CORRECTION TO `108`.** Its §1 says main is "green apart from what §4 lists", and
§4 lists the `r37` tree-shape failures. That is not the state. Nine files fail or
error at `03afe9c6`, before any change of today's:

```
19 ERROR   test_the_sort_is_frozen_and_applied_on_a_copy.py   <- the WHOLE file, at setup
 4 FAILED  test_each_file_is_filed_under_its_own_situation.py
 3 FAILED  test_two_courses_keep_two_terms.py
 2 FAILED  test_r37_per_branch_situation.py
 2 FAILED  test_cli_correction_loop.py
 1 FAILED  test_template_levels_wiring.py
 1 FAILED  test_r37_single_branch_is_byte_identical.py
 1 FAILED  test_cli_orphaned_send.py
 1 FAILED  test_cli_agreeing_corpus.py
```

**The 19 errors are one module-scoped fixture, and they matter more than their
count.** `the_morning` chains four pipeline runs and four typed gestures on one
database, and it dies on `KeyError: 'Coursework/Spring2026/PHYS1401/lecture'` —
a tree path the run no longer builds, because `106` Phases 3+4 made the top level
a LIFE. So **every test of freeze, apply, move, collision, journal and undo has
been dark** since the tree shape changed. That is the half of the product that
touches real files, and the walkthrough of 7 Sep called it "the trustworthy half".

A green suite was never the evidence here — `108` §7 says every real defect this
month was found by an agent READING code — but 19 dark tests on the moving half
is a bigger hole than any single item in Tier A. **Reviving them is now A1.5, and
it goes before A2.** `108` §4's rule holds while doing it: diff before recapturing,
because a recapture that is not diffed proves only that the code equals itself.

---

### A1.5 — the 15 failures are `106` Phase 7's flatten rule, and it is NOT a bug

Bisected in a detached worktree, one fast file (`test_two_courses_keep_two_terms`)
at seven commits of 18 Sep:

```
721b75fe Phase 6      7 passed
672b5778 Phase 5      7 passed
c954023d measure.py   7 passed
5dbc9257 Phases 3+4   7 passed
e9b7c550 Phase 3 fix  7 passed
229c7526 Phase 7      3 failed, 4 passed   <- HERE
03afe9c6 (HEAD)       3 failed, 4 passed
```

**The symptom looked like a serious regression** — `assert {} == {'CHEM2100': ...,
'PHYS1401': 'Fall2024'}`, no course nodes at all — and on the freeze fixture it
reads as `KeyError: 'Coursework/Spring2026/PHYS1401/lecture'`. Four test files and
19 setup errors all say the same thing: the course level stopped being built.

**It is `106` §B.2 working as written.** Measured on that fixture's own corpus
(two courses, two terms, TWO files each, so rule B.1 cannot apply):

```
tree            Coursework/{Fall2024, 2023-2024Semester1}      <- the term level IS built
node_expected_values
                node ...10 (Fall2024)            term=Fall2024            subject=PHYS1401
                node ...8  (2023-2024Semester1)  term=2023-2024Semester1  subject=CHEM2100
```

`Fall2024` holds exactly one course and nothing beneath it divides, so the chain
fold removes the course node **and appends its value to the parent**, which is
what §B.2 says it does. **No information is lost**: the invariant those tests
exist for — the term is read PER COURSE and not off the group — is still true and
still observable, at `node_expected_values` instead of at node parentage.

**So the tests are stale against a ratified rule, not evidence of a defect, and I
have NOT rewritten them.** Rewriting an assertion to match new behaviour is how a
bug gets enshrined, and there is a preference underneath this that only the owner
settles (`00` amendment 24):

> **OWNER QUESTION.** When a term holds exactly one course, §B.2 gives you
> `Coursework/Fall2024/` with `PHYS1401` carried as a value, and no `PHYS1401`
> folder. `107` asks for "shallow where files are isolated" and "a single unusual
> file may remain at the closest meaningful parent" — which justifies the fold —
> but two files of one course in one term may not be what you meant by isolated.
> **Is the folded course folder what you want?** If yes, the three assertions are
> rewritten to read the fold and the freeze fixture's paths are recaptured against
> it. If no, §B.2's chain fold needs a floor (fold only a chain whose members are
> below some count), and that floor is yours to set.

Until that is answered the 15 failures and 19 errors stay, and they are understood
rather than mysterious — which is the state `108` §4 should have described.

---

### The whole suite, measured once, with both changes in

```
tests/  (everything)   19 failed, 11068 passed, 20 skipped, 34 xfailed, 19 errors
```

**Every one of the 19 failures and 19 errors is pre-existing**, accounted for
without remainder:

* 15 failures + 19 errors — the integration directory, byte-identical to a pristine
  worktree at `03afe9c6` (34-line `diff`, empty);
* 4 failures elsewhere — `test_cli_review_sets_by_reason` (2),
  `test_d2_glossary_proposal`, `test_d2_draft_templates` — the same four names fail
  at `03afe9c6`. **19 Sep: one of the two is fixed and one is escalated** — see "2
  and 3" below; both bisect to `229c7526`, so "the same four fail at `03afe9c6`"
  reads as it did and the tally is now 3.

So A1 and A2 together regress nothing across 11,068 passing tests. That is the
claim, and the two baseline runs are what backs it.

**Run again after A2's reader change** (`515a57b4`):

```
tests/  (everything)   19 failed, 11072 passed, 20 skipped, 34 xfailed, 19 errors
```

Failure set byte-identical to the run above, +4 passes — the four new tests.
**Everything committed today is verified against a pristine baseline.**

---

### The moving half RUNS, and an untyped run can reach a moveable plan

A smoke on a copy (not a test, nothing committed from it), because 19 tests of
freeze/apply/move/journal/undo have been dark since Phase 7 and nobody had checked
whether the chain still executes at all. The A1 corpus, `ask → answer → accept →
freeze`, three arrangements:

```
typed --situation, --accept-groups, --freeze     3 of 10 frozen   apply line: YES
untyped, ONE branch answered (career)            0 of 10 frozen   apply line: NO
untyped, BOTH branches answered                  3 of 10 frozen   apply line: YES
```

**No crash anywhere.** The 19 errors are the fixture's stale paths, not a broken
chain — the moving half executes.

**And the middle row is the honest limit of A1.** `108` §2 said the product could
not be demonstrated end to end until the unsettled default was taught to build the
rest of the tree. A1 does that — the tree, the groups and 20 placement decisions
all appear — but with the default still unanswered its files are correctly declined
("Nothing here could say where these belong"), which is amendment 25 working, and
on that corpus they are the only files with anywhere to go. So **A1 was necessary
and is not sufficient**: an untyped run reaches a moveable plan only once EVERY
branch has been answered, and the bottom row is the proof that it then does.

That is worth knowing before the next agent reads §2 and expects a demo from A1
alone.

---

### The suite, driven down — 13 failures root-caused, 10 fixed, 3 named

Every one was pre-existing at `03afe9c6`. **Nine of the thirteen bisect to
`229c7526`, `106` Phase 7** — the same commit behind A1.5 — which is worth stating
plainly: one phase moved the tree, the screens and a privacy record together, and
the suite has been describing the world before it ever since.

| what | cause | done |
| --- | --- | --- |
| 2 × `llm_harness` d2 | amendment 20 added a glossary row and left the packet's digests and two proposal copies behind | fixed, `b542646b` |
| 3 × roots list | Phase 7's RESIDUAL HOME is a root; the tests predate it | fixed, `c108668d` |
| `template_levels_wiring` | `d8dd85b1` made `fact_call_stage` ask twice on purpose; the AST guard counted calls | re-argued to check EVERY call, `b6e9bb07` |
| `cli_agreeing_corpus` | **product defect**: Phase 7 keyed the option sentence by `dimension_role`, so a person read "would create 3 artifact_kind" | fixed, `54a26533` |
| `r37_single_branch` | screen legitimately moved: residual home, amendment 26's fold, the role→field fix | recaptured after diffing, `ea37e64d` |
| `cli_correction_loop` | amendment 26: `PHYS1401` holds ONE file, so `notes` folds into the course | re-argued |

**THREE WERE NAMED AND NOT FIXED, each for a stated reason. The first of them is now fixed** — see the measurement under it, which overturns the diagnosis it was left unfixed on.

**1. `cli_orphaned_send` — a real crash, and it is at the privacy boundary.**
A second run with `--send-set` dies:
`PolicyRequired: no P7 policy in force for 'version_2c21deda_0'`. Bisected to
Phase 7. The policy is put in force for `tree.tree.plan_version_id` once
(`production.py:1137`), but a run writes **a plan version per refinement pass** and
the failing id carries the `_0` suffix — an earlier pass than the one the policy
was set on. Phase 7 added passes, which is why it surfaced there.

**THE OWNER RULED IT (19 Sep): record the policy for every version the design
mints.** That is built — `production.py` now loops `TreeDesignResult.
plan_version_ids` — and it widens nothing, because the operation mode and the
consent grants come from the person's command and are identical on every version.

**IT DOES NOT FIX THIS TEST, and the traceback says why.** The crash is not on the
design path at all:

```
cli.run -> placement.pipeline.act_on_residual_sets -> review_residual_sets
        -> _send_set_to_approved_node -> run_residual_file -> _residual_decision
        -> placement.privacy.privacy_state_for  -> PolicyRequired
```

`--send-set` is a GESTURE, acted on early in `run`, **before the design of that
invocation has put any policy in force**. So the version it asks about has no
policy yet no matter how many the design records afterwards. The real question is
which plan a gesture acts under — the plan whose screen printed the set — and that
is a different decision from the one already taken.

**FIXED 19 SEP, AND THE PARAGRAPH ABOVE IS WRONG ABOUT WHERE THE CRASH IS.**
Measured, three runs of the failing corpus with `design_tree`, `set_policy`,
the two on-demand mints and `act_on_residual_sets` all instrumented:

```
[run2] design_tree      minted (version_A_0, version_A_2, version_A_4)
[run2] set_policy       version_A_0 / version_A_2 / version_A_4
[run2] mint_generals_on_demand      version_A_4 -> version_A_4
[run2] mint_review_homes_on_demand  version_A_4 -> version_B_0     <- HERE
[run2] act_on_residual_sets  inputs.plan_version='version_B_0'
                             set_ids=['version_A_4:No folder matched-1', ...]
[run2] CRASH PolicyRequired: no P7 policy in force for 'version_B_0'
```

**THE GESTURE IS NOT ACTED ON BEFORE THE DESIGN.** The design ran, the 19 Sep
ruling put the policy in force for all three versions it minted, and only then
was the gesture handled. **Nor is the failing version an earlier refinement
pass**: its `_0` is the first id of a FRESH `run_token`, because
`design_authorities` mints one per call (`cli.py:16727`) and `cli.run` calls it
again for each on-demand step. `version_B_0` is minted LATER than every version
the policy loop saw, by `mint_review_homes_on_demand` — `00` amendment 13, which
puts the review home in the tree for a person who did not type `--residual`.
With `--residual` typed the home is already there, nothing is minted, and the run
is fine, which is why only one shape of command ever hit this.

**WHICH PLAN A GESTURE ACTS UNDER: the version that holds the homes, and
`cli.run` already says so** beside the call that decides it (§8.4's egress
question is asked about a version, and this run's screen is the one the person
answered). Neither candidate (a) nor (b) as posed: the set is THIS run's set
(`version_A_4:No folder matched-1`), the screen offering it is this run's screen,
and `act_on_residual_sets`'s own standing decision already refuses to carry an
answer across versions. The previous run supplied nothing but the label the
person retyped.

**So it was never a decision about which answer governs a file's egress** — it
was one version of one run with no answer at all. Fixed in `cli.run` by the 19
Sep ruling's own loop, applied to the versions `production.py` cannot see:
`for version in result.tree.plan_version_ids: if current_policy(...) is None:
set_privacy_policy(...)`. **It widens nothing**: same operation mode, same
consent grants, same `--file-held` permissions — `set_privacy_policy` writes the
identical answer for every version of one command, and the new test asserts that
equality rather than taking it on trust. `placement/privacy.py` is untouched; it
was right to refuse.

**AND CASE A OF THAT TEST IS NOW STALE — the lead's call, not fixed here.**
`test_an_unenabled_area_still_gets_the_paste_able_command_and_a_plan` is written
against a world where omitting `--residual` means the area does not exist, so the
refusal's advice ("`--residual` enables an area for the run it is typed in") is
true. Amendment 13 ended that world for every set in `REVIEW_HOME_FOR_SET`:
`No folder matched` maps to `tv.REVIEW_LATER`, the home is minted on demand, and
with the policy in force the send is HONOURED — the screen prints "Would go into
Review Later ... 25 files" and there is no refusal to advise about. Printing the
advice now would tell the person to add a flag the product no longer needs, which
is precisely the defect Case B (the test immediately above) exists to forbid.
The assertion has NOT been rewritten to match: whether Case A should be re-aimed
at an area amendment 13 does not mint, or retired, is the lead's decision.
After the fix the file is **7 passed, 1 failed**, the one failure being that
stale assertion at `AREA_ADVICE` and no longer a crash.

**2 and 3. `test_cli_review_sets_by_reason` — RESOLVED 19 Sep. One is fixed, the
other is the owner's.**

**3. `test_a_blocking_reason_is_still_a_set_of_its_own` — FIXED, and it had been
saying nothing.** `229c7526` (`106` Phase 7 §D.3) re-keyed
`REFINED_BY_CHARACTERISTIC` from a `frozenset` of the REASONS a characteristic may
divide into `characteristic -> frozenset(reason)` (`cli.py:15721`) and did not
touch this file — Phase 7 updated 17 test files and not this one. So four of the
five assertions were asking a mapping of characteristic keys whether it held a
reason word, which is false of every reason there is: they passed because they
could not fail. The test now reads the union of the mapping's values, and pins
`NOT_YET_CLASSIFIED`'s one divider by name: "Unsupported or encrypted", which may
divide a blocking reason because it was given its OWN sentence (`cli.py:15740`)
rather than borrowing `no_supported_destination`'s. Provenance: `00`:368 is the
owner's own amendment text -- "the sets inside `98` are characteristic and named
(screenshots, standalone PDFs, unsupported or encrypted, possible duplicates,
deferred decisions), and every one is offered to the person before anything moves"
-- and `106-SORT-PLAN.md` is where it is numbered amendment 13 and built. The
phrase "amendment 13" appears nowhere in `00` itself.
A second characteristic reaching for a blocking reason now fails there.

**2. `test_files_held_for_four_reasons_are_four_sets_a_person_can_tell_apart` — NOT
FIXED AT THE TIME OF WRITING; BUILT UNDER OPTION (c) AND RENAMED, see the end of
this file.
 A question erases the reason it replaced, and the record contract says it
must. THE OWNER'S, amendment 24.**

**The evidence this document carried was the PRE-Phase-7 record and is withdrawn.**
Measured at `HEAD` on `_three_reason_corpus`, `holiday.jpg` is
`outcome=ask_user, abstention_reason=None, review_policy=review_required`,
classified `personal_non_sensitive`. It does NOT abstain with `privacy_blocked`;
that is `misc.txt`'s shape. So `_why` is faithful, `held[0].label` IS what `_why`
computes, and there is no second grouping: the screen is not lying. Both tests pass
at `229c7526^` and fail at `229c7526`, so both bisect to `106` Phase 7.

**The mechanism, in one sentence.** `placement/pipeline.py:2816-2821`: `_abstention`
asks `inputs.ask_about_file` before it writes, and when a question comes back it
hands the file to `_asking` (`pipeline.py:2856`), which writes `ASK_USER` with
`abstention_reason=None` — so `privacy_blocked` is erased from the record and the
screen can only call the file "Waiting on a question you have been asked". Phase 7
did not touch `placement/pipeline.py` (it added six lines to `placement/residual.py`
and nothing else under `placement/`). It changed the INPUT: the proposed residual
home `98 Review and Unsorted` gave the corpus root a home question to ask, so a
hook that answered `None` for this file before now answers a question.

**TRACED, not inferred.** `ask_about_file` is consulted at exactly two places,
`pipeline.py:2222` (the place-building path, `chosen_node_id is None`) and
`pipeline.py:2817` (inside `_abstention`). Wrapping `_asking` and recording its
caller on this corpus at `HEAD`: `holiday.jpg <- pipeline.py:2820` with
`ask='Where should the files in corpus go?'`, and `credentials.kdbx <-
pipeline.py:2820` with `ask='Where should the files in Private go?'`. Both come
through `_abstention`'s hook, so `holiday.jpg` DID abstain and the question is an
overlay on an abstention that already had its reason.

**AND THE ERASURE IS A RULE, not an oversight.** `placement/records.py:525` refuses
any record where the two disagree: "an abstention names why (§6.10); an unexplained
one is silence, and a reason on any other outcome contradicts the decision". So an
`ask_user` decision may never carry `abstention_reason`, and `_reason_of`'s
`PRIVACY_BLOCKED`-before-`ASK_USER` ordering (`cli.py:17951`) is unreachable for a
question — it can only ever be read by an abstention. Carrying the reason through
`_asking` is not a one-line fix; it is a change to what a placement record means.

**The `66` §4 defect this leaves on the screen, which is NOT a preference.**
`holiday.jpg` was read — Phase 7's own predecessor printed "Available OCR or text
evidence: partial" for it — and it is classified. It now shares one review set AND
one sentence with `credentials.kdbx`, an unopenable vault: "No destination in this
plan was supported well enough to decide, and **nothing this run could read says
what this file is**" (`pipeline.py:2914`). That clause is false of the photo.
"Unreadable" and "no strong match" sharing one message is the pair `66` §4 names.
It is not repaired here because what is true of every file reaching that writer
cannot be known until the question below is answered.

**THE QUESTION FOR THE OWNER.** Now that a residual home exists for every set, a
file that stopped because a model was not allowed to look at it is overlaid with a
folder question and loses its reason. Which does the person read?

* **(a) The question wins, as today.** Then this corpus has three reasons, not
  four, the fourth set is unreachable while any residual home exists, and the test's
  four-set pin is stale — but `pipeline.py:2914`'s sentence must stop claiming
  nothing could be read, because it is now given to files that were.
* **(b) The reason wins.** A `privacy_blocked` abstention is not overlaid with a
  question at all, which is the `229c7526^` behaviour and restores the fourth set.
* **(c) Both.** A question may name what it replaced, which means widening
  `records.py:525` so an `ask_user` record may carry the reason — and every reader
  of `abstention_reason` in the product is a reader of that change.

The test is left failing and unmodified. Rewriting its pin to three would enshrine
(a) without it being chosen.

---

### Amendment 28 — RULED, NOT BUILT, and the reason is in the code's own words

The owner chose `situation:Education/academic` over a branch id. Building it hit a
constraint the design did not know about, and it is stated in `branch_situation.
_asked_of_a_life`:

> `cli._ask_which_situation_each_branch_is` records it at the KIND's scope, **so
> the answer is read where every reader of the person's answer already reads it**
> (arm 0).

Arm 0 is `_life_of_file`, and it derives a file's LIFE from
`_persons_answer_for(kind)` — the kind-scoped answer. **So the life is computed
FROM the answer that amendment 28 would key BY the life.** A composite-keyed answer
cannot be read by the arm that decides which life a file is in, which is the arm
that would put the file under the branch the answer is about.

`_resolved_situation(file_id, kind, life)` already receives the life and is the
clean place to read a composite — but it runs AFTER the life is decided, so it
closes the reading half and not the derivation half.

**AND THE COLLISION ACTUALLY MEASURED IS NARROWER THAN THE RULING.** On the A1
fixture the two questions were the DEFAULT branch (keyed by `branch.label`, which
is its majority kind when nothing is typed) and a sibling life branch (keyed by
`branch.schemas[0]`). Both spelled `academic`. Two branches in two different LIVES
sharing a kind — the case `Education/academic` vs `Research/academic` solves — has
not been observed on any corpus here.

So there is a smaller fix that closes the measured defect without touching the
kind scope every reader depends on: **mark the default's question as the
default's**. It collides with a sibling only because a bare label and a bare kind
can spell the same word.

**NOT CHOSEN BY THE LEAD.** Both options migrate answers already in the owner's
database, and which one is right depends on whether they expect two lives to share
a kind. Put to them with both costs.

---

### A2. The amendment-16 residual regression — HALF BUILT, and the half is the mechanism

`e9b7c550` declared it: `cli._each_kinds_question_under` selects a kind's files by
**the judge's map** — `situation_cell[0].named.get(file_id) == kind` — so a file
whose kind came from a deterministic ANCHOR and which site G left silent is in no
kind's question at all. Before amendment 16 folded the kinds into one life it sat
in a one-kind branch and was asked.

**BUILT: `Branch.kind_of`** (`src/branch_situation.py`). `partition_by_branch` has
always computed the reach's per-file kind map — `kind_of` in its own body, off
`under` — and dropped it on the floor. It is now carried on the record as
`kinds_by_file` (pairs, not a mapping, so the frozen record stays hashable) and
read through `Branch.kind_of(file_id)`, which answers `None` for a file the branch
does not hold. Two tests, red before and green after
(`test_a_life_branch_says_which_kind_its_reach_put_each_file_under`,
`test_a_branch_says_nothing_about_a_file_it_does_not_hold`).

**NOW BUILT TOO: the reader change**, by extraction rather than by fixture.
`files_of_kind_still_open(branch, kind, *, judged_kind_of, situation_under)` is a
module-level function in `cli.py` beside `signals_for_branch`, which is the
codebase's own pattern for exactly this — a rule about one branch and a few
callables, with a two-line binder in the closure. Four tests, red first (the
import did not resolve): the anchor-settled file the judge left silent is asked as
its kind; a judged file is asked exactly as before; **the judge's word outranks
the reach where it spoke** (`104` §17.9 — preferring the reach would discard site
G's reading for every file the reach had placed); and a file already answered for
is not asked twice. 1,052 pass across `tests/p6`, both branch-situation suites, the
optional-situation integration file, A1's own and the P11 guard.

**What the integration fixture would have added**, for the record: proof that a
real corpus produces the shape. The unit tests prove the RULE; a corpus that yields
a two-kind life branch from the deterministic pass alone is still unbuilt, and
r37's loopback stub is still the route.

**The earlier note read:** the reason is a fixture, not a doubt. Switching `_each_kinds_question_under` to the branch's own map needs a test
that can SEE the difference, and that needs a corpus where the deterministic pass
alone produces a **two-kind life branch**. Three attempts did not get one:
`academic`, `college_applications` and `research` all live in Education, and a
corpus of syllabus + admission-form files read as **academic throughout**, so
`_each_kinds_question_under` returned early on `len(branch.schemas) < 2`.

**WHY those files did not anchor to `college_applications` is NOT DETERMINED.** An
earlier draft of this section blamed `file_kind_never_alone: true` on the row. That
is not a finding — `academic` carries the same flag and its syllabus anchors fine,
which is the whole basis of `test_r37_per_branch_situation`. The flag is far more
likely to be about a file's FORMAT not classifying it alone. Whoever takes this
should read `file_facts` for those two files and see whether a `work_type` fact was
written at all, and in what state, before theorising.

**The route that will work, for whoever takes it:** `test_r37_per_branch_situation`
already carries a loopback model stub. Site G naming one file of a two-kind life
branch and staying silent about another, whose kind an anchor settled, is the
residual's exact shape and the stub can produce it. That file has 2 unrelated
failures from Phase 7's fold today (see A1.5), so settle the fold question first.

Making the reader change without that test would be production code with no failing
test behind it — which is how `106` Phase 7 shipped a fold whose consequence nobody
could see until four test files went red.

### A3. The grader — `108` §5's description does not match the file, and the file is untracked

**READ, NOT CHANGED.** Two things have to be said before anyone edits it.

**1. It is outside version control.** The grader is `.groundtruth/grade_gate1.py`,
62 lines, and `.gitignore:32` excludes the whole directory — `git ls-files
.groundtruth/` is empty. The script that produces a headline number quoted in
`106` §0 and `108` §5 **cannot be reviewed, diffed, or handed to the next agent**,
and a fix made to it is invisible the moment the session ends. That is a bigger
problem than the number.

**2. There is no prefix fallback in it.** `108` §5 says the 97.7 % may not be
re-claimed "until the grader prefers the fact's own value where it is already a
situation id", because "the grader's prefix fallback would score a real
disagreement as a match". The file does no prefix matching anywhere. Its bridge is
a literal dict — key-situation → a SET OF KINDS — and the comparison is exact set
membership (`elif ans in MAP[k["situation"]]`). If the answer were a situation id
where the set holds kinds, the effect would be a false MISS, not a false match:
the number would read too LOW. `108` has the direction backwards.

**3. And the premise may not apply at all.** The script grades site G's RAW
RESPONSE payload — it joins `llm_response` and reads `payload["situation"]`. `106`
Phase 2(b) changed what the FACT holds, not what the response carries, so this
script is untouched by that change. What G's payload actually carries is the open
question already on the record: the shortlist is built from SCHEMA ids
(`model_situation.py:602` iterates `question.allowed_situations` as `schema_id`),
which is w2c's measured "shortlist unit mismatch, schemas (23) vs situations (208)"
— an owner question, still unanswered.

**So A3 is not a code task today.** In order: (a) decide whether the grader belongs
in the repo — it prints aggregates only and reads the key by path, so tracking the
SCRIPT while leaving the key and corpus ignored looks possible and is the owner's
call, since it is their harness; (b) answer the shortlist-unit question, because
whether G returns a kind or a situation decides what the bridge must contain; (c)
only then touch the comparison. Changing it now would be editing an untracked file
against a description its own source contradicts.

**Meanwhile 97.7 % stays unquotable** — not for `108`'s reason, but because nobody
has re-run the grader since the vocabulary questions opened.

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

---

## 20 Sep — the four amendments dispatched, and the one measurement a build cannot fake

Amendments 31–34 were ratified on 19–20 Sep and recorded in `00` (`b47940db`).
They are now **in build**, four agents in isolated worktrees plus a fifth on the
`--apply` defect. What follows is what the lead settled before dispatch, because
three of the four had an unknown in them that would have been discovered late.

### Amendment 22 DOES name the fork, so both halves of 33 are buildable

`109` Tier B said binding `year` was blocked because "one default order cannot
serve both `employer → year` and `year → organization`" and the owner had to name
a fork. **Amendment 22 names it in its own first sentence** — Current work
(`employer → year → project → stage`) and Career applications (`year →
organization and role → application stage`), "and nowhere else for now". Two rows,
two orders, no fork to pick. The Tier B entry was written without reading 22 to
its end. It is wrong and this supersedes it.

### `year_of`'s defect, located exactly

`src/cli.py:5026` — `_CALENDAR_YEAR = re.compile(r"(?<!\d)[12]\d{3}(?!\d)")`. A
PDF metadata date is `D:YYYYMMDDHHmmSS` with an optional offset, so the year sits
inside a 14-digit run and **both** guards fail. Not a near-miss: the function
cannot ever answer for the PDF form.

### THE FIRST MEASUREMENT — the producer alone, before any level is bound

Amendment 33 requires that "the build must measure the producer ALONE before the
level is bound — same commit, two measurements — so the middle state exists in the
record even though it never ships." This is that measurement, taken on the real
corpus (47 active `creation_date` facts) with the shipped code:

```
year_of ANSWERS:   4 of 47
year_of REFUSES:  43 of 47

the 43, by masked shape (# a digit, A a letter):
  18   A:##############+##'##'
  17   A:##############-##'##'
   5   A:##############A##'##'
   2   A:##############A
   1   A:##############

the 4 that answer:
   3   AAA ##, ####
   1   ## AAAAAAAA ####
```

**43 of 43 are one family** — `D:` plus a 14-digit prefix, then one of five
endings. The 5-count and 2-count shapes end in a LETTER, so a repair that handles
only `+`/`-` leaves seven files refused and builds a level that is blank on them.
That is why the census was taken before the fix and not after: it decides how many
cases the test table needs, and the number would not have been discovered by
reading the PDF specification alone.

The second measurement is taken on the repaired producer, by the lead, and both
numbers travel in the merge commit. The agent does not measure and was told not to
estimate — an estimate in the record would be indistinguishable from a measurement
later.

### What each agent was told it may NOT do

Because three of the four amendments have an obvious over-build one step past what
was ratified, and the over-build is what a later reader would mistake for the
ruling:

| build | the over-build that was forbidden |
| --- | --- |
| **31** teaching v2 | minting a new situation name; moving `shipped_situations`' output by a byte |
| **32** per-group question | dropping the old key. Answers in the owner's database sit under `situation:<kind>=` and `situation:default:<label>=` and **nothing tests the fallback**, because fixtures write whichever key the code writes |
| **33** `year` | binding the level in the same agent. The producer lands alone and is measured alone |
| **34** reason on a question | a general "any record may carry a reason". Ratified: required on `ABSTAIN`, permitted on `ASK_USER`, forbidden elsewhere — `66` §4 is satisfied by the third clause |
| **`--apply`** | picking a governing plan, writing `superseded`, adding a `--force`. Which plan governs is `110` Decision 5 and is the owner's |

### The `--apply` defect is narrower than "two frozen plans"

`110` §3.3 is right that `--apply` unions every frozen version
(`cli.py:25078-25080`), but a blanket refusal on more than one version would be
wrong: versions are minted per run, `tree.plan_version_ids` is plural, and
`test_one_branch_moves_exactly_the_files_that_branch_froze` **depends** on the
union working. The data-loss shape is **one `file_id` with two different
destinations across the chosen plans** — the only case where the product cannot
know which tree the person meant. That refuses, names both versions, and moves
nothing. It does not resolve the ambiguity, because resolving it is Decision 5.

### THE SECOND MEASUREMENT — the producer repaired, the level still unbound

Amendment 33's middle state, which never ships and now exists in the record:

```
                      BEFORE (shipped)      AFTER (fc48b96c)
year_of ANSWERS            4 of 47              47 of 47
year_of REFUSES           43 of 47               0 of 47
```

**The repair is one alternative, not a date parser.**
`(?<!\d)([12]\d{3})(?!\d)|(?<!\w)D:([12]\d{3})`, with `year_of` reading
`{plain or pdf for plain, pdf in ...findall(...)}`. It reads the four digits
after the `D:` marker and never looks past them, which is why all five measured
endings fall to one branch: none of them touch the year's POSITION, only what
follows it. The lookbehind excludes a preceding letter rather than a digit, so a
value ending `...ID:2024` is not read as a PDF marker.

**THE NUMBER WAS NOT TAKEN ON TRUST, because a producer that answers MORE may be
answering WRONGLY.** `104` §18.108 requires a value carrying two disagreeing
years to stay unread, and a repair that collapsed such a value would show as an
improvement. Checked structurally, on the same 47:

```
values holding exactly ONE date-bearing token   47 of 47
values holding more than one                     0 of 47
  (one `D:` marker, no standalone year)         43   <- the 43 that were refused
  (no marker, one standalone year)               4   <- the 4 that already answered
```

Nothing in this corpus could have been collapsed, and the two measurements
reconcile exactly: 43 refused become 43 answered, and the 4 that answered are
untouched.

**A FIRST ATTEMPT AT THAT CHECK WAS WRONG AND IS RECORDED BECAUSE IT WAS
PLAUSIBLE.** It searched for `[12]\d{3}` anywhere in the value and reported that
42 of 47 held several "years" — an alarming number that was entirely the
checker's own defect: that pattern matches digit runs INSIDE a 14-digit
timestamp (`0115103000` contains `1151`). The measurement rule has to be as
careful as the thing it measures, and an unbounded pattern is not.

**WHAT IS STILL NOT MEASURED.** This says `year` can now be COMPUTED for 47 of
47. It does not say a `year` FOLDER helps anyone — that is the binding, it is
wave 2, and it is the half amendment 33 warns has no measurement between it and
the producer if the producer is wrong. The producer is now measured. The level is
not yet built.

### THE `--apply` DEFECT: THE MECHANISM IN `110` §3.3 IS WRONG, AND SO WAS THIS FILE

**WITHDRAWN — the paragraph earlier in this file that said "the data-loss shape
is one `file_id` with two different destinations ACROSS THE CHOSEN PLANS" names
the right shape and the wrong door.** `110` §3.3's premise — that `--apply`
unions the nodes of every frozen version — does not hold, and both documents
read `cli.py`'s union without reading its input.

```
freeze.latest_freeze   SELECT MAX(created_at) FROM move_plans
                       WHERE superseded_by IS NULL
freeze.frozen_plans    SELECT payload FROM move_plans WHERE created_at = ?
```

**One freeze batch, never two.** The clock (`cli.py`) is
`datetime.now(timezone.utc).isoformat()`, so two invocations cannot share a
`created_at`; `freeze.py`'s own docstring says re-freezing leaves the earlier
plans in place but *"no longer the approved set"*; and
`tests/apply/test_freeze.py:309` has pinned exactly this since it was written —
freeze twice and `frozen_plans` returns the second proposal only. So freeze →
change a control → freeze again → `--apply-everything` applies **batch 2 alone**,
and `plan_versions.state='superseded'` going unwritten is a consequence of the
`created_at` design rather than a gap in it.

**THE SAME SHAPE REACHES THE DISK THROUGH A DIFFERENT DOOR, AND THAT ONE IS
REAL.** `apply_run.freeze.freeze` writes one plan per decision it is handed and
is **the only reader of that decision list that does not first take
`placement.versions._current`**. `_current`'s docstring says what the raw list
can hold: *"a subject decided twice in one pass — a group member placed by its
packet and then resolved again as shared material is the shape that does it."*
`carry_onto` and `scoped_general_demand` take `_current` for that reason. `freeze`
does not. So **one file gets two destinations inside ONE plan version**, which is
why looking across versions found nothing.

**WHAT IT DID BEFORE THE GUARD, measured:**

```
exit 0 — and the SAME file printed twice on one screen:
    PHYS 1401 syllabus.txt  -> .../Coursework/PHYS 1401 syllabus.txt      (moved)
    PHYS 1401 syllabus.txt  "The drive or folder this move needs is not
                             available right now. Reconnect it and try again."
```

The drive was never disconnected. `already_applied` keys on `plan_id`, so a
second PLAN for one file is not an already-applied plan and nothing caught it —
the run moved files and told the person a falsehood about why one did not move.
That is worse than the defect that was briefed.

**CLOSED** by a guard inside the moving arm: a file approved for two places stops
the run, names the file, both destinations and the version, and moves nothing. It
picks no governor, writes no `superseded`, adds no `--force` — Decision 5 is
untouched. It prints no pasteable command, because choosing between two approved
destinations is not something the product can do yet, and `84` §6 forbids
printing a line that is not true. The refusal is gated on the moving arm alone:
an earlier version refused `--undo` as well, which would strand a person whose
files had already moved.

**STILL OPEN, and named rather than fixed:** the root cause is that `freeze()`
does not take `_current`; making it do so drops the withdrawn row, which is a
decision about which plan governs and therefore Decision 5. And a second freeze
that writes NO plans leaves `latest_freeze` pointing at batch 1, so `--apply`
runs the plan the person believed they had replaced — a stale-plan-governs shape,
different from this one, not closed here.

### AMENDMENT 32 IS MERGED AND ITS PREMISE DOES NOT HOLD ON TODAY'S P9

The owner ratified "once per accepted GROUP" on the premise that a group is a
course-term packet and that a role is constant across one. **The code's own
docstring says a group is something else:** `_grouped_by_branch` produces *"one
draft per (branch, schema)"*, and *"a branch is a LIFE ... a life with two kinds
needs two drafts, both wearing the life's name."* So an accepted group is
(life × kind), and one answer would settle every academic file in Education at
once — every course, every term.

**AND ON AN OFFLINE CORPUS THE CHANGE IS INERT, measured.** The same two-life
corpus, run against the shipped tree and against the merged change:

```
before   20 --answer lines, 3 keys   situation:academic · situation:career
                                     situation:default:academic
after    20 --answer lines, 3 keys   identical, and no `/` key at all
```

The per-group ask loops need either a two-kind life branch from the deterministic
pass — a fixture nobody has built, in the code's own words — or site G, which does
not run under `offline`. So the new path is pinned at unit level and its effect on
a real run is **unmeasured**. It is merged because it preserves the old keys, the
coverage arithmetic and the printed question, all tested; not because it has been
shown to do what amendment 32 wanted.

### AMENDMENT 34 — BUILT under option (c), and the four-set pin is now a three-set one

**The gate test was rewritten and the lead ratified it, because this document's own
words require it.** `test_files_held_for_four_reasons_are_four_sets_a_person_can_
tell_apart` is now `test_files_held_for_different_reasons_are_sets_a_person_can_
tell_apart` and pins THREE. Option (a) above says in its own sentence that the
corpus "has three reasons, not four ... and the test's four-set pin is stale";
option **(b)** is the only one that "restores the fourth set"; the owner took
**(c)**. So the fourth set is not lost by this build — it was never reachable
under any ruling but (b).

**AND THE FOURTH SET WAS AN ERASURE WEARING A REASON'S NAME.** "Waiting on a
question you have been asked" held the vault because `_asking` wrote
`abstention_reason=None`. Under 34 the reason survives the question, so no file in
this corpus is left with nothing but the question. The label still exists and is
still reached by the two `ask_user` writers that genuinely replace nothing
(`pipeline.py:2225`, where no abstention was reached, and `pipeline.py:4703`,
where §6.9's selector chooses BETWEEN asking and abstaining so the abstention was
never concluded). **That is why clause two of the amendment is PERMITTED and not
REQUIRED** — a fact discovered by building it, not by ruling it.

The test now pins a PROPERTY rather than a count: the photo and the vault carry
the same question, stopped for different reasons, and land in different sets. A
count can be satisfied by an accident; this cannot.

**ONE CLAIM OF THIS DOCUMENT IS WITHDRAWN.** §2 above says "`holiday.jpg` was
read". Under the product's own predicate it was not —
`_files_something_was_read_out_of` returns the passport and `misc.txt` only — so
the folder question over the photo is legitimate. The false sentence was about
CLASSIFICATION, not readability: the photo IS classified
(`personal_non_sensitive`) and the screen said nothing could say what it is. That
is what 34 fixes, and the repair is narrower than the complaint that produced it.

**THE ROOT CAUSE WAS THE WRITER, NOT THE RENDERER**, which is the opposite of
what §2 predicted. `_reason_of` checks `privacy_blocked` before `ask_user` and was
always written to read this fact; `_asking` never gave it one. `src/cli.py` is
untouched by this change — the fix is that `_reason_of` finally receives the fact
it was written to read.

**ONE READER CHANGED AND IT WAS A REAL DEFECT OF ITS OWN.**
`placement/stage_output.py:87-104` `result_of` asked "no destination and a
reason", which equalled "is this an abstention" only while the record FORBADE the
pair. A question satisfies both halves, so under the widening every question would
have been graded `evidential_abstention` and P2 could score a question the product
put to a person as `abstained_correctly`. It now reads `outcome == ABSTAIN`, which
selected exactly the same records before the widening.

### FOR THE OWNER — one boundary the widening opens, pinned and not closed

§8.6 says a budget deferral is never a question. The OLD biconditional enforced
that as a side effect of forbidding the pair; the new three-clause rule does not,
so `ask_user` + `budget_deferred` is now a record the class would ACCEPT. **Nothing
builds one** — `_abstention` consults the hook only when the reason is not
`BUDGET_DEFERRED` — and `test_where_the_widening_stops_and_the_pipeline_takes_over`
records the boundary rather than closing it.

Closing it means a FOURTH clause in a contract the owner ratified with three, so
it is not built. **The lead's recommendation: ratify it.** It restores an
invariant §8.6 already states and that the old contract enforced by accident, and
the alternative is a rule the record class no longer defends and only the pipeline
does — which is the arrangement that produced this amendment's defect in the first
place.

### AMENDMENT 31 — WIRED, and condition 2 checked by the lead rather than by the agent

`ap.academic.teaching` is v2 and binds `holder_institution → school` ("School I
taught at"). The draft file is gone; its content is the shipped row.

**THE BRIEF WAS WRONG ABOUT CONDITION 2 AND THE AGENT WAS RIGHT TO OVERRIDE IT.**
The brief said to assert `shipped_situations`' output was BYTE-IDENTICAL before
and after — which is impossible for a change whose entire purpose is to add a
level, and which inverted the amendment's actual worry. Amendment 31 fears that
the cloud-bound menu SILENTLY KEEPS THE OLD LABELS while the readers use the new
row; the condition is that a label already shown is not RENAMED, not that the
tuple may not grow. The agent followed the amendment over the brief's paraphrase
and said so. That is the right order of authority.

**MEASURED BY THE LEAD, against `b47940db` through the real loader:**

```
rows before: 208          rows after: 208
situations added:   []    situations removed: []
the one row whose labels differ: academic.teaching
  before: ['Semester I taught', 'Course I taught', 'Kind of teaching material']
  after : ['School I taught at', 'Semester I taught', 'Course I taught',
           'Kind of teaching material']
  OLD LABELS KEPT: 3 of 3        OLD ORDER PRESERVED: True
```

208 both times, nothing added, nothing removed, one row changed, every old label
intact and in its old relative order. That is condition 2 exactly.

**THE CAVEAT THE AGENT FLAGGED RATHER THAN HID, and it is not teaching's.**
`holder_institution` is a GROUP-level role, so `school` resolves once per accepted
group and one `--label` writes one group. A single-course corpus therefore RECORDS
the school on the branch (`node_expected_values`) and does not build a child
FOLDER for it — `00`:57's own rule, a level the files did not divide is measured
and not built. Forcing a two-school folder fails structurally, not for want of a
fixture: two schools in one accepted group make `105` §14.4's scope filter see one
DISAGREEING scope rather than two agreeing ones. **This is equally true of
`academic.coursework` and predates this row.** A real multi-school folder needs
per-course groups, which is `00`'s option B and unratified.

### WAVE 2 — `year` CANNOT BE FULLY BUILT FROM THE SHIPPED ROWS, and here is why

Amendment 22 is right that `year` is wired in NO shipped row: `grep '"field_ref":
"year"'` over the whole library returns nothing. But `107`'s two trees ask for
fields that do not exist:

| `107` §Current work / §Career applications | the shipped row |
| --- | --- |
| `Employer → year → project or activity → stage` | `ap.career.employment-records`: `employer`, `job_title`, `record_type` — **no `project`, no `stage`** |
| `Year → organization and role → application stage` | `ap.career.recruiting`: `target_employer`, `job_title`, `recruiting_cycle`, `work_type` — a close match once `year` leads |

**So Career applications is buildable and Current work is not.** Adding `year` to
the front of `ap.career.recruiting` gives `107`'s shape almost exactly —
`target_employer` + `job_title` ARE "organization and role", `work_type` IS the
"application stage". `ap.career.employment-records` cannot reach `107`'s Current
work without minting `project` and `stage`, **which is closed vocabulary and the
owner's alone.** It is also not obvious that employment-records IS `107`'s
"Current work": `107` lists that row's material as DOCX, PPTX and design files —
work product — where employment-records holds job paperwork.

**AND THE BINDING IS NOT A ROW EDIT ALONE.** `folder_levels_for` iterates
`definition.default_order.dimensions`, so a `role_bindings` entry whose role is
not a DIMENSION is silently dropped (`109` Tier B, still true). `year` therefore
needs a dimension in `def.career-search-and-tenure` — and `_check_orders`
(`templates.py`) requires every candidate order of a definition to cover the SAME
role set, so each of that definition's orders gains the role or the record
refuses. That is the real shape of the work, and it is contained.

---

## 20 Sep — THE FULL SUITE IS GREEN, with all five changes in

```
11162 passed, 20 skipped, 34 xfailed in 1228.58s (0:20:28)
0 failed, 0 errors
```

Run serially, with every agent finished, on the merge of all five. The two
failures this session opened with are both closed: `cli_orphaned_send`'s stale
Case A was re-aimed (`aea5ebc4`) and `test_cli_review_sets_by_reason` fell to
amendment 34.

**READ THE COUNT LINE, NOT THE EXIT CODE.** The first attempt at this run passed
`--timeout=600` with no `pytest-timeout` installed. pytest printed `ERROR:
unrecognized arguments` and **exited 0**, and nothing ran. A green exit code from
pytest is not evidence a test executed; only a count line is.

---

## 20 Sep — A SECOND STALE-PLAN DEFECT, found by reading after the first was closed

The `--apply` agent flagged this and did not fix it; the lead read it and it is
worse than the flag said. **Predicted from the code and dispatched; not yet
reproduced at the time of writing** — recorded in that state deliberately, because
this session has already killed five confident mechanisms that were reasoned from
one file without reading its input.

**THE READING.**

1. `freeze.latest_freeze` = `SELECT MAX(created_at) FROM move_plans WHERE
   superseded_by IS NULL`; `frozen_plans` returns only the rows carrying it.
2. **Nothing in `src/` ever writes `superseded_by` on a move plan** —
   `grep -rn "UPDATE move_plans" src/` returns nothing at all. Replacement is
   entirely an artefact of `created_at` ordering.
3. So a second freeze that writes ZERO `move_plans` rows leaves `MAX(created_at)`
   unchanged, and **batch 1 is still the approved set**.
4. `report.py:231-236` prints *"This replaces the N file(s) you froze on
   <timestamp>. Anything from that plan you had already filed stays filed and can
   still be taken back."* whenever `proposal.replaces is not None` — and
   `_previous` computes that from batch 1 BEFORE this freeze has written anything.
5. `report.py:238-241`, immediately below: if `not total`, *"Nothing was frozen:
   no placement in this run is ready to move."*

**THE TWO SENTENCES PRINT TOGETHER.** The person is told their earlier plan is
replaced AND that nothing was frozen this time, from which the only reasonable
conclusion is that there is nothing to apply. `--apply` then moves batch 1's
files. That is the same shape as the defect just closed — a screen that says
something false while files move — reached through a different door.

**A freeze writes zero plans when every decision is withheld** (`_withheld`:
protected material with no permitting policy, a file not shown, and the other
refusals). It is not an exotic state.

**WHAT THE FIX MAY NOT DO.** It may not decide which plan governs — that is `110`
Decision 5 and the owner's. No `superseded_by` write, no `plan_versions.state`,
no flag. The defect is a `84` §6 defect: the screen says the earlier plan was
replaced when it was not. **Reporting which plan governs is not choosing which
plan governs**, and the honest screen says the plan from <timestamp> is still the
approved set.

**One thing to verify rather than assume:** a freeze that writes FEWER plans than
before is the case that sentence was written for and it is TRUE there — batch 1's
extra files really are no longer approved. The fix must keep that working.

### THE ZERO-PLAN RE-FREEZE — REPRODUCED end to end, and worse than predicted

Predicted above, then reproduced, which is the order this file now insists on.
Every step of the mechanism held: nothing writes `superseded_by`; a second freeze
writing no rows leaves `MAX(created_at)` where it was; `frozen_plans` returned
batch 1; and **`--apply-everything` moved 3 of batch 1's 4 files onto disk** (the
fourth was the passport, refused by the protection gate). The chain reaches the
disk. It is not a string defect.

**AND THE SCREEN WAS WORSE THAN THIS FILE SAID.** Beyond printing both sentences,
the apply line was SUPPRESSED — `if total:` guarded it — so there was no command
on the screen at all:

```
BEFORE
  This replaces the 4 file(s) you froze on 2026-09-02T00:00:00Z. Anything from
  that plan you had already filed stays filed and can still be taken back.

Nothing was frozen: no placement in this run is ready to move.
```

The gesture was **armed and invisible**: a plan the person was told had been
replaced was still the approved set, and nothing on the screen named it or the
command that acts on it.

```
AFTER
Nothing was frozen: no placement in this run is ready to move.

  So this run replaced nothing, and the 4 file(s) you froze on
  2026-09-02T00:00:00Z are still the approved plan. Anything from it you had
  already filed stays filed and can still be taken back, and this line still
  acts on that plan rather than on anything listed below:
    agent-plan ~/Documents --apply-everything
```

**THE ROOT CAUSE IS AN ORDERING, NOT A FALSEHOOD IN `_previous`.** `_previous`
reads the approved set BEFORE the loop, so `replaces` truthfully means "what was
approved when this freeze began" — it cannot know what the loop will write.
`freeze_lines` rendered that fact as the CLAIM "replaced", unconditionally, and
printed it above the count that contradicts it. The fix is the condition and the
order; the `Replaced` record is kept, because dropping it would silently omit a
plan still in force.

**A DOCSTRING THIS FILE CITED AS EVIDENCE WAS ITSELF THE BUG'S REASONING.**
`freeze.py`'s module docstring said re-freezing leaves the earlier plans "simply
no longer the approved set" — quoted here earlier as proof that one batch
governs. That sentence is TRUE of a freeze that writes plans and FALSE of one
that writes none, and it is the reading that produced this defect. Corrected in
the same commit. **A comment is evidence of what someone believed, not of what
the code does**, and this file has now been caught trusting one twice in a day.

Decision 5 is untouched: no `superseded_by` write, no `plan_versions.state`, no
flag, nothing hidden. **Reporting which plan governs is not choosing which plan
governs**, and the screen now reports it.

---

## 20 Sep — "does this apply to everything, or just my files?" — MEASURED

The owner asked whether the product works generally or only on the corpus it was
developed against. Measured through the real loader, not argued:

```
shipped situations                       208
domains                                   19
distinct fields used as folder levels     39

folder levels per situation
    1 level    28 situations
    2 levels   84
    3 levels   78
    4 levels   15
    5 levels    3
situations that build NO tree              0
situations with NO detection signal        0
```

**EVERY shipped situation binds at least one folder level AND is named by a
detection signal.** So none of the 208 is decorative: each can be reached and each
can build. The library is not a handful of real rows beside two hundred names.

**The levels are broadly shared rather than bespoke.** The most-used fields are
`project` (94 situations), `record_type` (64), `work_type` (48), `artifact_type`
(47), `stage` (30), `site` (30), `record_period` (25). Only 8 of the 39 fields are
used by exactly one situation, so the vocabulary is general machinery, not one
row's private key repeated.

### A CLAIM OF THIS FILE AND OF THE LEAD'S REPORT IS WITHDRAWN

Earlier today, on `107`'s Current work tree: *"it wants `project` and `stage`,
which no row has, and minting them is closed vocabulary and the owner's alone."*
**The first half is false.** `project` is the single most-used level field in the
library and `stage` is used by thirty situations:

```
project   declared by 8 schemas   research, code, business_operations,
                                  law_practice, creative,
                                  construction_property, engineering, government
stage     declared by 3 schemas   research, creative, engineering
year      declared by 0 schemas   -- it is UNIVERSAL, not per-schema
```

**What is TRUE is narrower: `career` declares neither.** `DOMAIN_FIELDS["career"]`
is `employer`, `target_employer`, `recruiting_cycle`, `work_type`, `record_type`,
`job_title`.

**AND THAT CHANGES THE DECISION'S SIZE.** Reaching `107`'s Current work is not
minting new closed vocabulary — it is extending an EXISTING field to one more
schema, which is a smaller act with a different rule over it (`60` H6.2: a file
whose key is not declared by the active schema returns unknown and is never
re-routed). It is still the owner's, and it is no longer a phase.

**The error is this session's fifth of one shape:** a mechanism reasoned from the
one place it was being looked at. `career`'s field list was read; the library's
was not.

### DECISION 5 IS RULED AND BUILT — `00` amendment 38

The owner ruled: **the latest freeze governs, and it says so in the database.**
Built in two halves, because it is one ruling read at two scales.

**(a) ACROSS FREEZES.** `tree_design.store.supersede_version` beside
`freeze_version`; `freeze` reads the replaced batch's versions BEFORE its loop
(after it, nothing tells the batches apart but the clock) and supersedes them
after, under `if plans:` — so a freeze that approved nothing still supersedes
nothing, which is the 20 Sep defect's rule, now reached from the database end as
well as the screen end. **Both guards still fire**, and the zero-plan test passes
unedited apart from its docstring.

**(b) INSIDE ONE PASS.** `freeze` now takes `placement.versions._current`. It was
**the only reader of the decision list that did not**, and the reason it went
unnoticed is worth keeping: `cli.py`'s `if not demand: return finished` means
`carry_onto` — which does take `_current` — never runs on an ordinary run. The raw
list reached `freeze` alone, so the defect was invisible on every General-minting
run.

**`_files_approved_for_two_places` IS RE-AIMED, NOT DELETED.** `_current` keys on
`subject_ref` = `file:{file_id}:{content_hash}`, so one file at TWO HASHES is two
subjects, both survive, both freeze, and the guard — keyed on `plan.file_id` —
still refuses. The group-subject door was checked independently and is closed:
`pipeline.py` gives a group subject `file_id=None` and `build_plan` refuses it at
`get_file`.

**ONE CHANGE BEYOND THE RULING, AND IT IS KEPT.** `write_node` refused a node
whose version state `== "frozen"`; it now refuses `in ("frozen", "superseded")`.
Without it the new state **reopened an approved-and-replaced tree to writes** —
approved, replaced and editable at once, the combination §8.8 exists to forbid.
The state was invented by this change, so the hole was too.

**WHAT IS NOT BUILT, AND WHY IT IS NOT A GAP.** `latest_freeze` and
`frozen_plans` still order by `MAX(created_at)` and do not consult
`plan_versions.state`. Making them would pull `create_tree_schema` into
`_move_frozen_files` and P10's tables into `tests/apply/conftest.py`, coupling the
apply package to P10 to learn something the clock already tells it correctly.

**The hazard was never that the reader ignores the state — it is that the two
could DISAGREE, and that is pinned rather than argued.**
`test_freezing_again_supersedes_the_plan_before_it_in_the_database` asserts the
first version reads `superseded`, the second reads `frozen`, `frozen_plans`
returns the second batch ALONE, and the files on disk are the second plan's. The
statement and the clock are proven to agree, end to end, including the disk.

**AND TWO TESTS WERE PINNING THE WRONG COUNT.** `tests/apply/test_freeze.py`'s
`_outcome_decisions` builds one decision per member of `OUTCOMES`, which is longer
than its world has files, so it re-uses four subjects across six decisions — and
both tests asserted one held row per DECISION. A folder holds files, not
decisions, and their own docstring ("compare them to the size of their folder")
argued for the change. Re-aimed to subjects, with the expectation computed from
subjects rather than from `_current`, so they assert WHICH survived and not merely
how many.

### THE TABLE NOW DESCRIBES THE VOLUME — and the lead's reason for building it was wrong

`_constraints_for(destination_root)` reads `case_sensitive` off the destination by
asking it, and leaves the other six fields as declared — a `mkdir` cannot ask a
directory about a path budget. One probe per run: bound in `_move_frozen_files`
after every early refusal (so a refused `--apply` probes nothing) and in `main`
after `if not args.freeze: return 0` (so a report-only run makes no directory).
The local IS the cache and the frame IS its lifetime.

**THE BRIEF SAID THIS WAS A DATA-LOSS DEFECT. IT IS NOT, AND THE AGENT SAID SO.**
The lead wrote that a mis-declared table lets "`find_collision` decide there is no
collision, and the rename that follows overwrite the incumbent". **That stopped
being true of this code.** `mutation/movement.py`'s `move_onto_free_path` moves
with `os.link`, falling back to `O_CREAT|O_EXCL` then rename; `cross_volume.
_copy_bytes` opens `"xb"`. All three fail `EEXIST` under the volume's OWN folding,
whatever the table declared — and `tests/p12/test_p12_file_loss.py` already proves
a mis-declared table on a folding volume does not destroy the incumbent.

**SIXTH ERROR OF ONE SHAPE THIS SESSION:** the claim was reasoned from
`_FILESYSTEM_CONSTRAINTS`' comment without reading the move path it describes.

**WHAT A WRONG VALUE ACTUALLY COSTS, measured.** The twin is invisible to
`find_collision`, the move reaches the syscall, the syscall refuses, and the
person is told *"The destination changed after the preview"* — **false, nothing
changed** — with **no collision record** naming what it hit, and no route by which
re-running says anything else, because the table is just as wrong next time. With
the volume measured the same twin reaches the COLLISION branch: recorded, named,
paused for a decision. `constraints.py` puts it in one line — *measuring makes the
SENTENCE right, the syscall makes the FILE safe.* Still worth building; `84` §6
and `66` §4 are both broken by a false sentence with no record behind it.

**TWO DEPARTURES FROM THE BRIEF, BOTH CORRECT, BOTH FLAGGED RATHER THAN QUIETLY
TAKEN:**

1. **An unaskable volume is treated as folding.** The brief asked for three things
   that agree on darwin and CONTRADICT on linux: fall back to the declared value,
   take the safe error, and do not proceed as sensitive. On linux the declared
   value IS the unsafe direction. The agent took the safe error —
   `VolumeUnmeasurable → case_sensitive=False` — on the authority of
   `_filesystem_constraints`' own ratified sentence: *"the safe error is to see a
   collision that is not there ... every unknown below takes its error the same
   way."* A volume that will not answer is an unknown about that volume. Cost: a
   pause over two capitals-only names on a genuinely case-sensitive disk.
2. **The probe RUNS IN the corpus root, which the brief forbade.** The only
   directory guaranteed to be on the destination volume IS the destination root;
   its parent is the wrong volume exactly when the root is a mount point
   (`/Volumes/STICK`, `/media/usb`) — the motivating case. The repo had already
   ruled this: `tests/p12/test_p12_no_invention.py` says *"The probe runs in the
   person's own corpus root, so leaving it behind was never an option."* It cleans
   up in a `finally` and a test asserts it leaves nothing.

**WHAT IS PROVEN AND WHAT IS REASONED, kept apart.** The fold, the probe and the
bytes are REAL — every volume-touching test runs against a real directory on this
APFS volume and moves real bytes through the real `apply_plan`. Only `sys.platform`
is injected, and the table is built by `cli._filesystem_constraints()` under a
patched platform rather than hand-typed. **`main --freeze`'s call site was never
executed**: a structural test proves `main`'s code object reaches
`_constraints_for` and no longer reaches `_FILESYSTEM_CONSTRAINTS`, which is not
the same as running it. The end-to-end drivers are integration tests the agent was
barred from.

**Verified by the lead:** `tests/p12/`, `tests/apply/`, `tests/test_cli_platform_
table.py` and `test_cli_moves_nothing_without_apply.py` — the mtime-stability test
the agent predicted might go red — **358 passed, 1 xfailed.**

### `--ignore-branch` AND `--omit-level` — `107`'s "every split can be changed before freeze", half built

Measured on screen, not asserted into existence:

```
--ignore-branch 'PHYS1401'
  Coursework   [proposed]
    COMS4995   [proposed]
    PHYS1401   [ignored]   [marked, not a destination]
      notes    [ignored]   [marked, not a destination]

--omit-level 'academic:subject_anchor:subject'
  FIRST :  Coursework / {COMS4995, PHYS1401/{notes, syllabus}}   5 folders
  SECOND:  Coursework / {notes, problem set, syllabus}           4 folders
  both  :  "Files: 3 decided, 3 ready to file"
```

The second is `107`'s sentence happening: the course level gone, the work kept in
the folder above.

### `110` §2.1 IS WRONG IN THREE PLACES, AND ONE OF THEM WOULD HAVE TURNED THE SUITE RED

**1. THE PERSISTENCE SEAM IT NAMES DOES NOT EXIST AND THE SUITE PINS THAT IT MUST
NOT.** §2.1 says an ignored branch persists because "the next run reads it through
`learned_preferences_still_applicable`, which is origin-keyed and survives
re-runs". That function takes PLACEMENT SUPPRESSIONS, not review actions, **and
has no callers by design**: `tests/p11/test_p11_connections.py` asserts
`_callers_of("learned_preferences_still_applicable") == set()`, and
`test_p11_versions.py` carries a strict xfail that XPASSES — turning the suite red
— the moment a caller appears. **The lead's brief repeated §2.1 verbatim.** Had
the agent followed it, the wiring would have broken two pins in files outside its
permitted run set, so the lead's serial suite would have found it, not the agent.
Routed instead through the origin key from `node_key`, read back beside
`actions_for` in `review_surface/store.py`.

**2. Its `--apply` line number is from another base** — `branches_named` is not at
`cli.py:25062`. Cosmetic, and it means §2's line numbers are not this tree's.

**3. "Collect a `review_action` FIRST, then `pipeline._apply(IGNORE)`" cannot be
one moment.** `_apply` needs a tree with the branch in it, and a run opens its own
root draft with `predecessor_id=None`, so editing the previous run's version edits
a plan nothing downstream reads. The ORDER is kept and split across two moments:
the row is the durable fact, and `design_tree` applies it to the tree THIS run
designs, before its final freeze, so `approved_branch_ids` excludes it and P11's
index never sees it.

### NO VOCABULARY WAS MINTED, AND THE OWNER SHOULD CONFIRM THE SUBSTITUTE

`ignore` and `omit` are **not** members of `review_surface.vocabulary.ACTIONS`, and
`81` §14.1 reserves that vocabulary — "they are not minted by whoever notices the
gap". Both gestures therefore collect **`ACTION_REJECT`**, P13's own word for "no
to this proposal", at `branch` scope for the branch and `domain` scope for the
level. P10 keeps its own words (`IGNORE`, `omitted`) — the two-vocabulary shape
`collect_level_relabel` already has.

This is also the right side of amendment 24's line: what is rejected is the NODE or
the LEVEL — a preference about a proposal — never a fact about anybody's files.
**One constant changes if the owner prefers a minted `ignore` member.**

### THE GAP BOTH CONTROLS SHARE, AND IT IS A NEW DECISION

**Neither can be unset, and the screen does not say so.** `--ignore-branch` has no
revocation — re-typing it is a silent no-op that still writes a row. `--omit-level`
can only be undone by renaming over the same triple, which nothing tells anybody.
Their sibling `--rename-level` DOES have a way back, so the asymmetry will be felt.
Nothing on screen is false today, because the help text promises no revoke. **What
takes a v1 control back is a decision the owner has not been asked, and it belongs
beside `110` Decision 3.**

### THE AGENT CORRECTED ITS OWN COMMIT, AND THE CORRECTION IS THE INTERESTING PART

It first wrote that the coverage arithmetic proves the files of an ignored branch
are still accounted for. **It is not that strong.** The coverage block sums ROSTER
buckets — indexed, not asked, protected, unreadable, deferred — and a file's
DESTINATION is not one of them, so no placement change can make it stop closing.
`= N` is a crash guard. The real destination evidence is the "Held for review"
block naming the files and the "Ready to file into X" lines, and those are what the
tests read. Both the commit message and one SABOTAGE docstring overstate it, and
the overstatement is recorded here rather than quietly fixed.

### THE TREE DIFF REACHES THE PERSON — and `110` §0.2 was wrong that it "exists end to end"

**IT RAISED ON THE FIRST REAL REMOVAL AND COULD NEVER HAVE PRINTED.** Measured on
a two-run CLI database, not deduced:

```
v1 nodes:  node_8d63b091_10 | branch:Uni/subject=MATH2010
           node_8d63b091_11 | branch:Uni/subject=PHYS1401
REPROJECT removed_node_ids ('node_8d63b091_10', 'node_8d63b091_11')
```

`placement/versions.py`'s `reproject` builds `removed_node_ids` from
`decision.destination.node_id` — the **from-version's minted id** — and
`review_surface/versions_view.py` compared that set against
`entry.origin_node_id` — the **lineage key**. Under `node_key` those are different
strings for one node, so `RemovedNodeMissingFromDiff` fires on ANY removal.

**NINE GREEN TESTS NEVER SAW IT BECAUSE BOTH SHIPPED FIXTURES BUILD NODES WHERE
`node_id == origin_node_id`.** That is the whole lesson: the fixtures made two
different keys the same string, so every test agreed with a component that could
not run. `110` §0.2 called this machinery "wired to nothing", which was true, and
inferred it was *ready*, which was not — **nothing had ever asked it a question
with a real removal in it.** Fixed by letting the guard accept either spelling,
because the removed entry already carries both.

**This is `110` wrong in a FOURTH place, and `110` is a document the lead wrote.**
The pattern across all four: it read what a function was FOR and not what it does
when called.

### WHAT THE DIFF SAYS, AND THE TWO FALSE SENTENCES THAT DID NOT SHIP

The block names added / removed / renamed / re-parented with undo labels, the
carried-and-renewed arithmetic (`Accounted for: C + R = T`, where `T` is counted
independently from the database rather than summed from the two numbers beside
it), and the three producer gaps `110` §3.2 demanded be named rather than omitted.

**Two sentences were written and removed for being false**, which is the part
worth keeping:
* *"a name on both lists is a folder that was rebuilt, not one that was deleted"*
  — false: the lines carry a display LABEL, and labels repeat under different
  parents.
* `Folders removed: 2` standing alone read as something the PERSON did, when in
  the measured case the corpus lost files and "a folder that separates nothing is
  not a branch" collapsed two. Hence the standing sentence that a folder is on
  those lists "for one of two reasons, and this comparison does not say which".

`66` §4 is what both of those break, and both were caught by reading the rendered
screen rather than the code.

### RESIDUAL PERSISTENCE, AND `110` §2.4 IS WRONG ABOUT WHAT THE RECORD CAN HOLD

§2.4 says to record "each `ResidualChoice`". **Four of §7.4's six actions carry an
argument the person supplied** — rename's name, relocate's anchor, merge's target,
replace's node id — and `residual_action` holds a closed-vocabulary member. The
record's one free-text field is refused beside a chosen option BY NAME
(`questions/records.py`: *"an answer carrying both a chosen option and a sentence
has two answers in it that need never agree"*). So `enable`/`disable` persist and
the other four are **named on the screen as not remembered**, rather than dropped
or smuggled into one string as `action=argument` — a display string is not a key.

### A `node_key` GAP FOUND IN PASSING, PINNED AS A STRICT XFAIL

The review home a residual enablement mints carries its own per-version `node_id`
as its `origin_node_id`, so it has **no lineage across versions**: two IDENTICAL
runs with `--residual` report it removed and added, and the area beneath it
re-parented. The diff reports the record faithfully; the fault is where the node is
minted. `tests/integration/test_the_tree_diff_reaches_the_person.py` carries it as
`xfail(strict=True)`, so it flips to passing the day it is fixed.

### THREE THINGS IN THIS BUILD ARE UNTESTED AND SAID SO

1. The **multi-version frozen branch** is coded and unreachable from the CLI —
   `run_token` mints one version per run.
2. The **`unapplied_user_edits`** block never fired on any corpus run.
3. `_revalidates` with `revalidation_inputs=None` returns True for every
   model-decided placement, so **"carried over unchanged" means the node still
   exists, not that the verdict was re-validated.** The arithmetic is true; the
   word is stronger than what was checked.

### `107`'s THIRTEEN BRANCH TEMPLATES, MEASURED — and the probe that answered three rows wrong

`107` §Branch templates is a table of thirteen rows, each naming a default split
order the product promises. The earlier reading of it reported six BUILT, five
PARTIAL and three UNVERIFIED. **That is fourteen verdicts over a thirteen-row
table**, and enumerating the names settles which count is wrong: six BUILT
(Coursework, Teaching, Career applications, Projects, Taxes, Current work) plus
three UNVERIFIED (Travel, Reference, Residual) is nine, and the remainder is
Family records, Property, Health, Photos — **four**, not five. There is no
missing fifth PARTIAL row to find.

**WHY THE THREE WERE UNVERIFIED, AND IT IS ONE MISTAKE AND NOT THREE.** The probe
searched `facts/fields.py` for the words `107` uses for a level — `trip`, `topic`,
`residual_state` — and found nothing. **None of the three is a field key.**
Neither are `program`, `rendition` or `person`, the other three words `107` uses
for a level, measured against the live vocabulary: 59 field rows, and none of the
six words is among them. The library does not spell `107`'s words as KEYS; it
spells them as LABELS on generic keys, and the label is the half a key-only probe
cannot see:

| `107` says | the library binds | and labels it | on |
| --- | --- | --- | --- |
| trip | `event` | `"Trip"` | `ap.travel.trip-photos` |
| topic | `project` | `"Topic"` | `ap.research.reading-library` |
| function | `record_type` | `"What it is for"` | the Travel draft |
| rendition | `media_type` | `"Photos or videos"` | `ap.photos.social-media-export` |
| residual state | — not a field at all — | a residual TEMPLATE NAME | `tree_design/residuals.py` |

So a key-only probe returns nothing for a row that is fully built, and the
correct response to nothing is to read what the row DOES bind. This is `110`'s
fourth-wrong-place pattern in a new costume: *"it read what a function was FOR
and not what it does when called"* — here, what a column was NAMED and not what
the library binds under it.

#### The thirteen, as `folder_levels_for` answers over the 209 shipped situations

Every order below is `folder_levels_for`'s answer, field keys as bound, read off
a run over the whole release. Verdicts: **BUILT** — some shipped situation builds
`107`'s order; **PARTIAL** — some levels build and named ones do not;
**DELIVERED ELSEWHERE** — the row is real and no library row answers it;
**ABSENT** — nothing delivers it.

| `107` template | `107` promises | the library delivers | verdict |
| --- | --- | --- | --- |
| Current work | Employer → year → project or activity → stage | `career.current-work`: `employer → year → project → stage` | **BUILT** |
| Career applications | Year → organization and role → application stage | `career.recruiting`: `year → target_employer → job_title → recruiting_cycle → work_type` | **BUILT**, caveat below |
| Coursework | Institution → program → term → course → work type | `academic.coursework`: `school → term → subject → work_type` | **PARTIAL** — `program` missing |
| Teaching | Institution → term → course → teaching function | `academic.teaching`: `school → term → subject → work_type` | **BUILT** |
| Family records | Person → context → year or cycle → record type | `academic.k12-schooling`: `school → term → work_type` | **PARTIAL** — person missing |
| Projects | Project → stage or artifact class | `research.thesis-dissertation`: `project → artifact_type → stage` | **BUILT** |
| Taxes | Tax year → record class | `finance.tax-filings`: `tax_year → record_type` | **BUILT** |
| Property | Property → function → project or year | `finance.household-property`: `record_type` alone | **PARTIAL** — property and project-or-year missing |
| Health | Person → year or durable category → record type | `finance.insurance-healthcare`: `institution → record_type` | **PARTIAL** — person and year-or-category missing |
| Travel | Year → trip → function | `travel.trip-photos`: `event("Trip") → location` | **PARTIAL** — year and function missing |
| Photos | Year → event → rendition | `photos.social-media-export`: `capture_year → event → media_type` | **BUILT**, caveat below |
| Reference | Status or topic → subtype | `research.reading-library`: `project("Topic") → artifact_type("Kind of reading")` | **BUILT** |
| Residual | Residual state → optional broad subtype | nine residual TEMPLATE NAMES under `98 Review and Unsorted` | **DELIVERED ELSEWHERE** |

**NO ROW IS ABSENT.** Every one of `107`'s thirteen is reachable today in some
measure, which is the census's headline and is asserted rather than counted by
eye.

#### The three that were unverified, each with what settled it

**REFERENCE — BUILT.** `research.reading-library` binds
`subject_anchor → project` labelled `"Topic"` and `artifact_kind → artifact_type`
labelled `"Kind of reading"`: `107`'s *"Status or topic → subtype"* at `107`'s own
depth of 2. The *"Status or"* half of that alternative is answered on the residual
side — `Reading Inbox` and `Review Later` are two of the nine names below.
**One caveat, recorded rather than buried:** the row sits in the `research` schema
and the Education life, so a person with no research corpus is not offered it.
That is a coverage question for the owner, not a gap in the row.

**TRAVEL — PARTIAL, and the level thought absent is the one that is built.** Two
Travel-life situations ship. `travel.trip-photos` builds `event → location`,
labelled `"Trip"` and `"Where we went"` — **the trip level `107` asks for, built
today**. `travel.bookings-confirmations` builds `record_type → institution`,
`"Kind of booking"` and `"Who I booked with"` — the function level, above its
context, which `113` §3.3 already records as design principle 1 inverted. What is
missing is the year and, on the photos row, the function. `year` is bound on
NEITHER travel row and neither is `capture_year`; `travel.trip-photos` is a
`photos`-schema row and does not bind the `capture_time` role at all, so this is
an unbound role and not a bound-but-unbuilt one.

`drafts/health_travel.json`'s `ap.travel.trip-records` closes it exactly:
`year("Year") → event("Trip") → record_type("What it is for")`. It is wired to
nothing and **gated twice, not once.**

1. The ratification gate, quoted from
   `tests/p10/test_library_health_travel.py::test_the_names_are_not_in_the_shipped_menu_until_the_owner_ratifies`:
   *"DELETE THIS TEST when the owner ratifies the names and the lead appends the
   draft to `src/tree_design/library/` and its name to
   `production.LIBRARY_FILES`. Until then it is the check that no drafted name
   can reach the cloud menu `cli.py` builds."*
2. **The blocker under it.** The same file's
   `test_the_dependencies_are_exactly_the_ones_the_draft_declares` asserts the
   gap by name: `{"travel.trip-records": {"event not referenced at finance"}}`.
   And the draft binds `year` three MORE times — taking the release from two
   bindings to **five** — where `00` amendment 22 licenses two and
   `tests/p10/test_library_year_is_bound_nowhere_else.py` pins those two by
   name over the shipped release. **Ratifying the names does not ship the row**,
   and the day the draft is appended to `LIBRARY_FILES` the year census goes red
   unless amendment 22 is widened in the same motion. Named here so the two are
   read together.

**RESIDUAL — DELIVERED ELSEWHERE, and the framing that called it a library row
was wrong.** `107` §Residual structure is answered by
`src/tree_design/residuals.py` over the nine `RESIDUAL_TEMPLATE_NAMES` of `00`
§7.3 (`src/tree_design/vocabulary.py`:286), projected into the frozen tree by
`project_residual_nodes` (`residuals.py`:193) under `98 Review and Unsorted`
(`vocabulary.py`:301), enabled one at a time by the person. **No situation, no
applicability row, no schema.** The mechanical proof rather than the argument:
`production.read_packaged_library_file("residuals.json")` raises —
*"'residuals.json' is not part of the packaged library release"* — so nothing
that reads the template library can reach the residual library at all. They are
two libraries in one directory.

**AND `107`'s SECOND RESIDUAL LEVEL IS AUTHORED AND UNREACHABLE — a defect, named
and not fixed.** `107` promises *"Residual state → optional broad subtype"* at
depth 1–2. Level one is the template name and is built. Level two is
`optional_shallow_subfolders`, and measured over `residuals.json`: **exactly one
of the nine authors any** — `Reference Clips`, with six (`Recipes`, `Products`,
`Quotes`, `Inspiration`, `Articles`, `Code Snippets`). `ResidualTemplate` carries
the slot (`residuals.py`:55, populated at `:176`) and **nothing in `src/` reads it
after construction** — the only other occurrences are two empty-tuple
constructions in `cli.py` (`:5495`, `:5509`) and one fixture. Beside it,
`RESIDUAL_MAX_DEPTH = 0` (`cli.py`:5461) with the comment *"Zero means the home is
flat"*, and `_residual_library()` builds all ten homes at depth 0. So `107`'s
optional broad subtype is a catalogue slot with an author, a reader that only
stores it, and a depth ceiling of zero.

One thing that is **not** a gap: `107` §Residual structure names SEVEN states and
`00` §7.3 ships NINE, and only `One-Off Images` and `Unsupported or Encrypted`
appear in both. Two ratified vocabularies, not a shortfall — closed vocabulary is
the owner's, and neither list is the other's census.

#### The four PARTIAL rows, re-verified — all four hold, two with sharper reasons

**FAMILY RECORDS and HEALTH — the missing person level is UNBUILDABLE, not
unbound.** Both `107` rows open with a person. Measured over `FIELD_ROWS`: every
person-naming key is live and `destination_eligible=False` — `people`,
`subject_of_record`, `account_holder`, `authored_by`. A level is built from a
destination-eligible key, so no row anywhere in the release can build one. That
is `107` line 120 implemented (*"client, patient, employee, and candidate names
should not be generated as folder levels by default"*), and it means the person
level is not a row that forgot to bind an available key. `client` is
destination-eligible and is not the exception it looks like:
`test_library_year_is_bound_nowhere_else.py` already settles that it is the
counterparty of the `our_firm` split.

Health additionally holds at one row in the whole life, and it is an insurance
row: `institution` is labelled `"Health plan"`, which is not one of `107`'s three
dimensions. `medical` remains field-less with zero shipped situations; the draft
above carries two `medical.*` rows behind the same gate.

**PROPERTY — the missing level is a DECLARATION, not a missing key.** `property`
is a real, destination-eligible field key, declared at `construction_property`
and nowhere else. `construction_property` is a Career-life schema, so the
thirteen rows that build a property level are all somebody's job and none is the
person's home. The Home and Property life ships `finance.household-property`
(`record_type` alone) and `finance.hoa-residents-association`
(`institution → record_type`), neither binding `property`. **This is a different
repair from Coursework's**: extending an existing field to one more schema, which
`109` above already classifies — *"not minting new closed vocabulary … It is
still the owner's, and it is no longer a phase."*

**PHOTOS — overturned, PARTIAL → BUILT.** One of the nine `photos` rows,
`photos.social-media-export`, builds all three of `107`'s levels:
`capture_year("Year I posted them") → event("Occasion") →
media_type("Photos or videos")`. The other eight stop at two. `113` §3.2 already
recorded this row as AGREES; what changes is the row-level verdict, under the
test this census uses — *a shipped situation builds that shape*, the same test
`test_107s_current_work_is_a_shipped_situation` applies. **The caveat is recorded
in the census table rather than hidden**: `media_type` is labelled `"Photos or
videos"` and `107`'s rendition column is HEIC/JPG/RAW/PNG/MOV/edited exports, so
the LEVEL is built and the vocabulary inside it is coarser than `107`'s. A reader
who weighs the vocabulary above the level reads this row as PARTIAL, and that
reading is legitimate; the census picks the level because that is the test the
other twelve rows are measured by.

#### Two verdicts from the earlier reading move

**COURSEWORK — overturned, BUILT → PARTIAL.** `academic.coursework` builds
`school("My school") → term("Semester") → subject("Course") → work_type("Kind of
work")`, which is four of `107`'s five. `program` is missing and there is no
field key for it — the vocabulary has 59 rows and `program` is not one, so the
level cannot be bound to anything. `113` §3.2 recorded the same measurement and
classified it a PREFERENCE; under this census's definition (*some levels, name
which are missing*) it is PARTIAL. The two are not in conflict — one says whose
decision it is, the other says what is built.

**CAREER APPLICATIONS stays BUILT, with the caveat stated.** `career.recruiting`
builds `year("Year") → target_employer("Company I applied to") → job_title("Job I
went for") → recruiting_cycle("My search") → work_type("What I sent them")`.
`107` asks `Year → organization and role → application stage` at depth 3–4; this
is depth 5, spelling *"organization and role"* as two levels and *"application
stage"* as `recruiting_cycle` plus `work_type`. **The `stage` key exists in the
vocabulary and is not bound here.** The order is `107`'s and the arity is not.
`113` §3.2's *"PREFERENCE — right dimensions, inverted order"* is stale: `00`
amendments 33 and 35 put the year first.

Two other `113` §3.2 verdicts are stale for the same reason and are corrected by
this census rather than by argument: **Current work** is no longer a DEFECT —
`ap.career.employment-records` is not the row, `career.current-work` is, under
amendments 41 and 42 — and **Teaching** now binds `school`, so *"§1.6, the memo
already flagged it"* has been answered.

#### What keeps it honest

`tests/p10/test_library_107_thirteen_templates.py` — nine tests, the census
pinned by name AND by exact field order, never by count, for
`test_library_year_is_bound_nowhere_else.py`'s reason. Its tripwire asserts that
`107`'s six non-key words are still absent from `FIELD_ROWS`, with the failure
message saying what red means there: *re-measure the table*, not *something
broke*. Travel's PARTIAL is asserted against the shipped catalogue, so the day
the draft lands the census goes red and forces the row to flip rather than
drifting. Residual's verdict is asserted three ways — no residual situation ships,
`residuals.json` is refused by the packaged loader, and the optional subtype is
authored on exactly one of the nine.

**AND THE SIBLING SETS ARE PINNED, WHICH CAUGHT THE ONE SENTENCE `107` WRITES
ABOUT TWO OF ITS OWN ROWS.** A shape reached by eight rows and a shape reached by
one are different claims, and only one of them survives a row being retired, so
the census records for each pinned row every OTHER situation that builds the same
order. Two results are worth the register's ink. **Coursework and Teaching are
each other's only sibling** — `school → term → subject → work_type`, the same
four keys in the same order — so `107`'s *"Coursework and teaching are visibly
different even when they mention the same institution and course vocabulary"* is
carried by the LABELS and by nothing else ("My school" against "School I taught
at", "Course" against "Course I taught"). A build that normalised those labels
would satisfy every field-order assertion in the file and break `107`'s sentence;
the labels are therefore asserted, and asserted disjoint. **Health has seven
siblings**, all `finance` rows — `institution → record_type` is the generic
financial shape, so the one row in the Health life reaches `107`'s depth by being
an ordinary financial record rather than a health one, which is what makes its
PARTIAL a coverage verdict rather than an order one.

`tests/p10/test_library_107_thirteen_templates.py` — 9 passed. `tests/p10/` —
875 passed, 2 xfailed.

#### What this measurement did NOT settle

* **Whether `107`'s Reference row is reachable by a non-researcher.** The row is
  built, in the `research` schema, under the Education life. Whether a person
  with no research corpus is offered it depends on `cli.signals_for_branch` and
  the judge's kind, which this census did not run. **What would settle it:** a
  run over a corpus with saved articles and manuals and no academic material,
  reading which situations the branch menu offers.
* **Whether `media_type` is `107`'s rendition.** The level is built; the closed
  vocabulary inside it was not enumerated here, and it is the owner's either way.
  **What would settle it:** the owner reading `media_type`'s members against
  `107`'s rendition column and saying whether one is the other.

---

## 21 Sep 2026 — Recognition, diagnosed on a corpus that is nobody's

The owner asked to diagnose and solve recognition. Everything below was measured
on a **synthetic corpus written for the purpose** — nineteen text files and,
separately, twenty-two images written from two byte strings. No personal data
was read: `.groundtruth/` stayed shut, and the classifier refused a copy of one
of its databases, which was the right refusal. The corpus is in the session
scratchpad and is reproducible from this document.

This matters beyond privacy. A synthetic corpus lets **one variable move at a
time**, which the owner's corpus can never do, and it is the owner's standing
instruction of 20 Sep read literally: the corpus is the measuring instrument and
never the spec.

### The baseline nobody could see

The figure carried into this session was "3 of 15 filed offline". It was from a
run no longer on disk, and it is **wrong**. Measured: of nineteen text files,
**eleven were recognised**, six abstained `no_corroboration`, two `ambiguous`.
`no_evidence` was **zero**. Recorded so the next session starts from a number
rather than from anyone's recollection.

**AND THE LIMIT OF THAT NUMBER, stated here rather than discovered later.** This
corpus is fifteen text files, a `.py`, a `.csv` and two images. Every one of them
is trivially extractable, so "`no_evidence` is zero" is a fact about
TEXT-BEARING files and is **not** evidence that extraction is sound generally.
The owner's corpus is 222 PDFs, 40 JPEGs and 16 MP3s; a scanned PDF with no OCR
and an untranscribed recording both land in `no_evidence`, and nothing measured
here touches them. What it does kill is the idea that extraction is what stops
the files this corpus is made of.

### CLOSED — a picture whose own name says photo was not a photo

`96c954a7`. `Detector._capture` was reachable only where a file carried no
authored term at all. A text-less picture whose FILENAME says `photos` therefore
came off **worse than one that says nothing**: the name and the file kind both
said picture, and the two agreeing cancelled each other.

Measured over ten images named the way DEVICES name them — macOS, Android,
Pixel, Nikon, Photo Booth, Image Capture, iOS panorama. Four recognised; six
abstained, and every one of the six had matched a term `photos` itself authored:
`screenshot`, `photo`, `scan`, `panorama`. The pair that states it is one
picture under the two names Apple has shipped:

| filename | source | before | after |
| --- | --- | --- | --- |
| `Screen Shot 2026-…png` | macOS pre-Mojave | photos | photos |
| `Screenshot 2026-…png` | macOS since Mojave | **no_corroboration** | photos |

Apple closed up the space in 2018. A person who upgraded their laptop watched
their screenshots stop being recognised, and no screen the product prints could
have told them why. After: nine of ten, and the holdout raises OTHER schemas
(`cover`, `grid`) so the narrow rule correctly stays out of it.

**The note in the capture test called this "the right answer"** and measured it
at five of the owner's fifty. That ratio is a property of a corpus of
`IMG_*.jpg`. On a machine where screenshots are the most numerous image it
inverts. This is the clearest case yet of the owner's 20 Sep instruction.

`file_kind_never_alone` is untouched: it forbids a KIND from activating a schema
ALONE, and here the kind is not alone. The condition is `leaders == [photos]`.

**It widens nothing, verified rather than argued.** Nine text-less JPEGs named
for safety material, the detector run with the fix reverted and again with it
in: exactly one line moved, the ordinary `photo.jpg`. Six protected before, six
after — passport, HKID, vaccination card, codicil, diagnosis, prescription all
unchanged.

### CLOSED (`87baf2ea`) — the default branch was named by one tally and explained by another

On the nineteen-file corpus the run said:

> The situations offered are **career**'s, because career is the kind this
> folder's own evidence names most often.

There is no career material in that corpus. `career` was **recognised on zero
files**. The sentence is produced by `questions/triggers.py:358`; the value comes
from `cli._the_corpus_names_a_schema`, which votes **twice, in order** — anchors
first, and only if those tie, the recogniser's raised candidates:

| schema | anchor facts | raised | recognised |
| --- | --- | --- | --- |
| **career** | **2** (`meeting notes`, `cover letter`) | 2 | **0** |
| academic | 1 (`syllabus`) | **9** | 2 |
| construction_property | 1 (`invoice`) | 3 | 1 |

`career` wins the ANCHOR vote and returns before the reading vote is consulted.
That is the documented rule — "a fact outranks a reading" — and the rule is not
in question here. **The sentence is.** It describes the reading vote in the case
where the anchor vote decided, so the person is told the folder's evidence
mostly names career when what happened is that two work-type facts did.

**Two things to settle, and they were different sizes.**

1. *The sentence* — **done**. Which vote won now travels with its answer, so the
   screen reads "more of these files carry a kind-of-file word `career` owns"
   where a fact decided and "`career` is the kind this folder's own readings
   raised most often" where a reading did. A caller that names no vote keeps the
   old words: one that has not been taught to say which tally it took should not
   be made to claim one.
2. *The order* — **still the owner's**. Two anchor facts outranking nine raised
   readings produced a visibly wrong default on this corpus. The order's own
   docstring justifies itself with a corpus where the detector recognised
   NOTHING, so the measurement behind it does not cover the case where readings
   are rich. Nothing here changes the rule.

Also visible and the owner's: `WORK_TYPE_OWNER['meeting notes']` is `career`,
and `WORK_TYPE_OWNER['invoice']` is `construction_property`.

### OPEN — the vocabulary is half taxonomy labels, and that is authoring

Structural census of the shipped release: 23 schemas, 8,481 distinct terms.

* **4,096 terms (48%) are three words or more.** `_terms_in` matches a
  contiguous token run, so a five-word term needs five consecutive tokens.
* `government` is **75%** terms of five words or more; `legal` 42%, `hr` 40%.
* Terms like `'risk, issue, or continuity record'` and
  `'draft or redline under review'` are **descriptions of a kind of document**,
  not words a document contains.
* `legal` has **six** sole-owned single words — `attorney-in-fact`, `codicil`,
  `executor`, `grantor`, `settlor`, `testator` — all estate law. A lease, an NDA
  or an employment contract contains none of them. `medical` has eleven.

With `never_alone` requiring TWO distinct terms, this is what the six
`no_corroboration` files are made of. **It is vocabulary authoring and therefore
ratification, not a defect to fix here.**

### RECORDED, NOT FIXED — prose compiled as terms

`recognition/compile.py::_terms` applies no shape rule, so editorial notes in the
research rows compiled as terms. The longest is **77 words**, beginning
`'proposed for r6, not design: …'`; others begin `'proposal note:'` and
`'precondition:'`.

**This changes no outcome.** A 77-word term cannot match a contiguous run, so it
also cannot un-match anything; removing it would not file or unfile one file. It
is compiler hygiene — `_terms` wants a shape gate — and the real term lists
buried inside those notes are unratified vocabulary, so splitting them out is the
owner's. Recorded here so it is not rediscovered as a finding.

### Named and not chased

* `13_readme.md` → `creative` on `install`, `layout`. A README is the most
  common file in a developer's folder and `code` has ten sole-owned single words.
* `12_recipe.txt` → `creative` on `finish`, `stock`; `08_nda.txt` →
  `business_operations` on `shall`. Ordinary English carrying schema weight.
* `construction_property` offers a **22-option** menu for two files.

### The mechanism under both the ties and the false positives

Every abstention on the nineteen-file corpus, with the exact terms that produced
it. This is the useful form of "the vocabulary is thin", because it names what is
actually doing the work:

| file | reason | the terms, and who owns them |
| --- | --- | --- |
| a one-line note | no_corroboration | `curriculum`→academic, `term`→construction_property, `review`→creative |
| ordinary prose | no_corroboration | `before`→**law_practice** |
| meeting notes | no_corroboration | `check in`→finance/construction/retail, `catch up`→business_ops, `round`→creative, `notes`→academic |
| a cover letter | ambiguous | `dear`→**clinical_practice**, `cover`→clinical_practice+creative, `billing`→creative |
| `script.py` | no_corroboration | `script`→**code AND creative**, one each, tie |
| a csv of sales | no_corroboration | `units`→academic AND law_practice |

Two different failures, and they need different remedies:

* **Ordinary English authored as a sole-owned term** — `before` is
  `law_practice`'s, `dear` is `clinical_practice`'s. These do not tie; they WIN,
  and they are what put a recipe and a README into `creative` (`finish`, `stock`,
  `install`, `layout`). An over-recognition is worse than an abstention because
  the file is filed somewhere nobody will look for it.
* **A word two schemas both authored** — 411 of 8,481 terms have more than one
  owner. `script` belongs to `code` (a script) and `creative` (a screenplay), so
  a Python file called `script.py` is structurally unrecognisable: one term each,
  a tie, and `00` requires abstention. `code` has ten sole-owned single words, so
  it has little else to win on.

**Both are vocabulary authoring and therefore the owner's.** What would settle
the first is a frequency list — this project has none, and inventing one here
would be exactly the hardcoding the owner ruled against on 20 Sep. Naming the
measurement that is missing is more useful than guessing at it.

### CLOSED (`87baf2ea`) — a refusal that blamed the recogniser for files it never saw

*(This section is about the REFUSAL. It began as an attempt to test `00`:30's
structural-evidence instruction and found something else on the way; the `00`:30
verdict is the last section of this entry, measured properly on loose files.)*

`00`:30 says code files *"should rely heavily on local structural evidence,
including repository roots and package files"*. The machinery exists:
`extractors/structured_text.STRUCTURAL_MARKER_KINDS` carries §2.4's four classes
and `readers/text_documents._markers_for` produces them by filename stem — so the
plan was to point the product at a repository and watch them arrive.

Measured on a six-file repository — `README.md`, `package.json`,
`pyproject.toml`, `Makefile`, `index.js`, a notebook with kernel metadata — the
run indexed **zero files**. Every path was excluded `software project root
descendant`, subject `package.json`, and all six verdicts are in
`exclusion_verdicts`.

**That exclusion is right** and nobody should want their repository reorganised.
**The screen is not.** The run refused with:

> the folder was read and nothing in it said what kind of material it is: no
> file carries a kind-of-file word one situation owns, and the recogniser raised
> nothing about any of them.

Nothing was read, and the recogniser was never asked. `_print_set_aside` exists
precisely so a refused run still says what it skipped — its own comment reads
*"a refused run that never said what it had skipped is the silent omission the
standing rule forbids"* — but it sits at `cli.py:20953` and this refusal fires at
`cli.py:19410`. **The earliest refusal is upstream of the block that exists to
make refusals honest.** So the six set-aside files are recorded in the database
and named on no screen, and the sentence the person gets blames the recogniser.

**CLOSED (`87baf2ea`).** The empty roster is a different case from a vote that
named nothing, and it now says so itself — the count and the rule, in the
refusal, where `_print_set_aside` cannot reach. A folder that holds no files at
all says that instead, and a folder that WAS read and named nothing keeps the
sentence it already had, which is the negative twin in the test.

### The suite was green by arrangement — three failures were the order it ran in

The full run after the capture fix came back **3 failed / 11,303 passed**. Two of
the three were in HOLD tests, which is the area the capture fix touches, so they
had to be treated as a regression until excluded. **None of them was.** All three
are test isolation, and each reproduces deterministically by forcing an order
rather than by hunting a seed.

**The capture fix is excluded by construction**, not by assertion. The held file
is `Passport syllabus.txt`: `_capture` requires `source_types <=
TEXTLESS_SOURCE_TYPES` and the file carries `text_document`, and the new branch
requires `leaders == [photos]` while its leaders are `identity` and `academic`.
Neither condition is reachable. The glossary test never runs the detector at all.

| failure | cause |
| --- | --- |
| `test_a_decline_leaves_the_hold_exactly_as_the_rules_wrote_it` | a sibling mutates the shared run |
| `test_a_held_file_is_never_offered_a_cloud_target` | the same |
| `test_every_meaning_is_the_library_s_sentence_byte_for_byte` | a global the promptbench never restores |

**The holds.** `test_site_g_lifts_the_hold` shares one `cli.main` run across four
tests through a module-level `_RUNS` cache, because a run is the most expensive
thing in the suite. Three open it `mode=ro`. The fourth WRITES — the person's
lift, then a second scan — which is the whole point of it. Four seeds in five put
the writer first, and the two tests asserting `superseded_by is None` read the
`user_confirmed` row it had just written. In DEFINITION order the writer runs
last, which is the only reason the suite was ever green.

**The glossary.** `tools/promptbench/site_a.use_glossary` assigns
`dossier.GLOSSARY_FILE` process-wide and never restores it — right for the tool,
a script that benches one glossary and exits; wrong inside a suite that goes on
running. The bench runs two candidates and the SECOND wins, so every later test
read `field_glossary_proposal_2026-09-06.json` where the shipped file belongs.
Ordering `tests/tools/` before `tests/p8/` fails it every time.

**Why this is worth its own entry.** A suite whose result depends on the seed
cannot answer the question a suite exists to answer. It nearly cost this session
its own fix: two of the three failures landed in exactly the area the change
touched, and the only thing that separated "pre-existing flake" from "regression
I just shipped" was root-causing all three. A green run that is a property of the
arrangement is not evidence, and 21 Sep's "11,304 passed, 0 failed" was one.

Fixed in `8065524a`. Neither fix touches `src/`.

**A FOURTH, found by the next full run and the same shape again.**
`test_a_silent_file_is_asked_and_filed_under_one_situation` has a module-scoped
`answered` fixture that runs a third `cli.main` against `run`'s database with
`--answer situation:research=…`. That answer RESOLVES the open situation and
places files — which is exactly the state
`test_and_its_folders_are_not_chosen_at_all_while_the_situation_is_open` exists
to assert is absent. Seeds 2 and 3 fail; seed 1 and definition order pass.

**Proven pre-existing in a detached worktree at `29b85d8c`**, this session's
starting commit, where it fails on the same two seeds. And the failing test
passes ALONE on seed 2 — which is the check that separates an ordering fault
from a seeding one, and worth writing down because the two look identical in a
run log. Fixed the same way, on its own `Connection.backup` copy.

**So the family is: a fixture that WRITES into a database its read-only siblings
share.** It arises honestly — a `cli.main` run is the most expensive thing in the
suite, so sharing one is right — and the discipline that makes it safe is one
line: *a fixture that writes takes a copy.* A scan for the shape (`scope="module"`
plus more than one `cli.main`) finds seven modules, and the other six were swept
under three seeds each rather than waited for: `test_seam_census`,
`test_the_sort_is_frozen_and_applied_on_a_copy`,
`test_the_question_at_the_end_and_the_sort`, `test_the_judge_names_the_situation`,
`test_the_gist` and `p7/test_p7_file_released` are all clean. **The family is
contained: four found, four fixed.**

Pinning the seed would hide this family, not fix it. Random ordering is what
found all four.

### THE OWNER'S — `00`:30's instruction for code is built on one side only

`00`:30, in its own words: *"Code-related files should **rely heavily on local
structural evidence, including repository roots and package files**, rather than
forcing semantic analysis to infer a project from arbitrary code text."*

**The producer side is built and works.** `extractors/structured_text`
carries §2.4's four classes as `STRUCTURAL_MARKER_KINDS` and
`readers/text_documents._markers_for` emits them. Measured on three loose files
(outside a project root, so nothing is excluded):

```
metadata:field=README file        README.md
metadata:field=notebook metadata  nbformat: 4
metadata:field=notebook metadata  kernelspec: Python 3
metadata:field=notebook metadata  language_info: python
```

**The consumer side is not.** Same three files, same run:

| file | outcome | schemas raised |
| --- | --- | --- |
| `README.md` | no_corroboration | construction_property, creative |
| `analysis.ipynb` | **no_evidence** | none |
| `notes.txt` | no_corroboration | academic, creative, law_practice |

A Jupyter notebook carrying `kernelspec: Python 3`, `language_info: python` and
an `import` statement raised **nothing at all**, and a README raised
`construction_property`. The four indicators `00` names are in the evidence table
and the `code` schema authors no term that matches any of them — its whole
vocabulary is 41 terms, ten of them sole-owned single words.

It is worse than a gap. The detector *deliberately refuses* the one observation
that did say "notebook": `_matches` skips `metadata:field=language`, and its
comment records why — the reader fills that slot with `Jupyter notebook`, `code`
ships `notebook` as a work type, and every `.ipynb` in existence carried a `code`
term before a word of it was read. That refusal is right. It also means the
honest signal and the dishonest one were the same slot, and only the dishonest
one was ever wired.

**Two ways to close it, and both are the owner's, not mine.**

1. *Vocabulary* — author terms on `code` that the marker VALUES actually spell
   (`nbformat`, `kernelspec`, `package.json`). Ratification.
2. *A rule* — let a marker KIND raise `code`, since §2.4's four classes are a
   closed set and the kind, unlike the value, is the product's own word. That is
   a new recognition signal and therefore a design change, and it would want
   `00`:30 quoted beside it.

**What it would buy:** `code` is the schema a developer's folder is most made of,
and it is currently one of the weakest in the library. Nothing here should be
built before the owner picks one of the two, because both are authorship.

### NOT MEASURED — what a local model does to this corpus

Attempted and **thrown away**, recorded so it is not mistaken for a result and
not repeated the same way.

The run named `qwen2.5:3b` over the same nineteen files and came back after 627
seconds saying `2 Photos and captures`, `1 Academic`, `16 nothing named these
yet` — worse than the 12 of 19 the rules manage alone, which would be a striking
finding if it were one. It is not. The same output carries
`sqlite3.OperationalError: disk I/O error` out of `open_database`, and the report
says *"19 of them had nothing to read — no text came out of them"*. All nineteen,
including the plain `.txt` files that extract fine offline. Extraction produced
nothing, so the counts describe a broken run and say nothing about the model.

**THE CAUSE, AND THE FIRST DIAGNOSIS OF IT WAS WRONG.** I recorded here that the
measurer had broken the run by querying its database with the `sqlite3` CLI
mid-write. That was a guess from a coincidence — my read had returned
`SQLITE_IOERR` around the same time — and it is **false**.

The second attempt carried a validity gate, which caught the same breakage and
printed what the first attempt had buried: a multiprocessing `freeze_support()`
refusal. P5's extraction pool SPAWNS workers, a spawned worker re-imports
`__main__`, and the probe was a script file with no `if __name__ == "__main__":`
guard — so every worker re-ran the whole probe, multiprocessing refused, every
extraction died, and `cli.main` still returned 0 with a plausible report in which
nothing had been read. Adding the guard fixes it: the same corpus offline then
reports `16 of 19 yielded text` in two seconds.

The earlier ad-hoc runs in this entry were `python3 -c` invocations, where there
is no file for a child to re-import, which is why they extracted normally and
this one did not. **A probe that drives `cli.main` from a FILE needs the main
guard**, and that is the rule, not the one about databases.

**What still stands from the first write-up:** the validity gate itself. A run
that exits 0, writes a full report and read nothing is indistinguishable from a
real one at the level of counts. Asking "did any text come out of this corpus"
BEFORE reading a single number is what turned two wasted runs into a diagnosis.
A long unattended model run also still wants the per-file wall-clock ceiling
`tools/groundtruth/_one_run.py` implements and these probes did not.

The question is still open and still worth answering, because the seven files the
rules cannot settle are design-bound — the arity rule and `00`'s requirement to
abstain on a tie — and the design's own answer for them is to ask a model.

### The confirmation number

```
11309 passed, 20 skipped, 34 xfailed in 1271.73s (0:21:11)
```

Zero failed, zero errors, and the output scanned for a traceback before the count
line was read — which is the discipline the thrown-away model run above bought.

Twelve commits stand behind it: one recognition fix, two screen fixes, four test
isolation fixes and the register entries. Five tests were added and each of the
three product fixes was watched failing first.

**Read it against the run that opened this entry, not against the session before.**
That one said `3 failed, 11303 passed`, and the one before it `11304 passed, 0
failed` — a number that was a property of the seed. This one is green because
four modules no longer depend on the order they run in, which was checked by
forcing the orders rather than by drawing seeds.

### MEASURED — all three recognition channels, same corpus, same answer

The question the entry opened with: the rules settle 12 of 19 and the other seven
are design-bound — five fail `never_alone`'s arity and two are ties where `00`
REQUIRES abstention. The design's answer for those is to ask a model. **So the
models were asked.** Three channels, one corpus, and each run's validity checked
before its counts were read.

| channel | recognised | what it cost |
| --- | --- | --- |
| rules alone | **12 of 19** | 2s |
| + local LLM (`qwen2.5:3b`) | **12 of 19** | 379s |
| + encoder (`minilm`) | **12 of 19** | 10s |

**Identical. Not one of the seven moved.**

**The local LLM does not do recognition at all, and this is the answer to a
question the owner has asked more than once.** On this path a model answers FACT
questions (site A) and SITUATION questions (site G) — never "which schema is this
file". That is the deterministic detector's job and nothing else's. Measured:
naming `qwen2.5:3b` asked a model about **1 file of 19**; the other eighteen were
held (14) or sat under a branch whose situation nobody had named (4). Offline
those same files read `no_destination_this_mode_permits`. So the model is not
failing to recognise — **it is barely being consulted, and never about this.**

**The encoder DOES do recognition, it ran, and it settled nothing.** Verified
rather than assumed: `vector_embeddings` holds exactly seven rows, and they are
exactly the seven files the rules abstained on — the one-term note, the tie, the
plain prose, the meeting notes, the cover letter, `script.py` and the csv. The
composed recogniser speaks only where the rules stop, it spoke about precisely
those seven, and every proposal fell below `SemanticFloors`.

**What this settles.** The ceiling on this corpus is 12 of 19 across every
channel the product has. The gap is not machinery, not the model and not
extraction — **it is vocabulary**, which is the owner's authorship and is the
three findings recorded above: ordinary English authored as sole-owned terms,
411 terms with two owners, and `00`:30's structural evidence for `code` with no
term on the consuming side. Nothing built here would move the number. Ratifying
vocabulary would.

### THE BLOCKER TO "NO ABSTENTIONS" IS THE GATE, NOT THE RECOGNISER

The owner, 21 Sep: **"we need 19 of 19."** That is `00` amendment 5 of 15 Sep
restated — *"there should be no abstentions, make sure of that … a decline is no
longer a correct abstention at these two sites; it is a failure to judge."*

**19 of 19 was never the deterministic detector's to deliver.** `00` REQUIRES it
to abstain where two readings are both supported, and two of the nineteen files
are ties built to be ties. The nineteenth file is named by the JUDGE. So the
question is not why the rules stop at 12 — it is why the judge is not asked about
the other seven.

**Measured on the local-model run (`qwen2.5:3b`), from its own database:**

| call site | dossiers built |
| --- | --- |
| `H_restricted_kind` (the gate) | 15 |
| `G_situation_sensitivity` (the judge) | 5 |
| `A_fact` | 1 |

| basis | protected | files |
| --- | --- | --- |
| `local_model_gate` | **1** | **10** |
| `local_model_gate` | 0 | 4 |
| `safety_domain` (deterministic) | 1 | 4 |

**The gate held ten of the fifteen files it examined**, and the four
`safety_domain` holds beside them are the deterministic rules working correctly
(a bank statement, an immunisation record, a will, an invoice). The ten are:

    06_tie.txt  08_nda.txt  09_lease.txt  12_recipe.txt  13_readme.md
    14_cover_letter.txt  15_lecture_notes.txt  16_script.py  17_table.csv
    18_photo.jpg

**A tomato soup recipe was classified `sensitive_personal`.** So was a software
README, a Python script, a sales csv, lecture notes about sorting algorithms, and
a 160-byte blank JPEG. Every file in this corpus is invented; none of it is
anybody's personal material.

**It is not a parse failure and not a code default.**
`restricted_kind_named_by_verdict` returns `None` unless the model NAMES one of
the ten kinds, and the verdicts read `accept_direct` with citations attached for
all ten. The model positively asserted a restricted kind and cited evidence for
it. It abstained on only five.

**And a held file is never asked** (the owner's ruling of 13 Sep: a protected
record is filed by the person). So the gate's ten holds remove ten files from the
judge before the judge exists, which is why one file of nineteen was asked and
why the census with a model is byte-identical to the census without one.

**THE CHAIN TO 19 OF 19, in order.** (1) the gate clears an ordinary file;
(2) its branch's situation is known — four files were `branch_unsettled`, a
second and smaller blocker; (3) the judge names a kind, with no decline allowed.
Step 1 is where nine tenths of the loss is.

**Three levers, and none of them is the recogniser.** A larger local gate model
(this device carries `qwen3:8b`; measured next); the cloud gate, which is what
the deployment is configured for and which this session's sandbox refuses to
let the lead call; or the gate's prompt, which is the owner's ratified text.

### TRIED AND REVERTED — `00`:30's structural evidence cannot be read off notebook metadata

Built, tested, measured, and **thrown away**, because the suite caught a defect in
it that the product had already paid to fix once.

The rule: two or more DISTINCT §2.4 structural markers raise `code`. It worked on
its own terms — `analysis.ipynb`, which returned `no_evidence`, became
`Recognition(code)` on `nbformat`, `kernelspec` and `language_info`, and a lone
`README.md` still activated nothing, so `never_alone` held.

**Then `tests/recognition/test_recognition_serialisation_is_not_evidence.py` went
red on two tests, and both were right.**

* `test_a_notebook_saying_only_a_course_code_is_not_a_code_project` — a notebook
  whose entire content is `PYTHON 1006 Spring 2026` became a code project again.
  That is the defect `_matches` already documents in its own comment: the four
  `Python 1006` notebooks of the owner's corpus, *"the only files that run
  placed"*, were placed on exactly this arithmetic, and the cure was to refuse
  `metadata:field=language` as evidence.
* `test_narrowing_this_does_not_cost_the_honest_code_case` — real Python source
  became a recognition on its container's terms rather than its own.

**THE LESSON, and it is about the instruction rather than the implementation.** A
notebook's `kernelspec` says what language the file is WRITTEN IN. It does not say
what the file is ABOUT, and coursework is written in Python too. Notebook metadata
is the same class of signal as `metadata:field=language` — the reader's word for
the format, not the document's word about itself — and the detector refuses that
slot for a measured reason. Feeding the same fact in through a different door is
the same defect wearing a different locator.

The other three marker classes do not rescue it. A folder holding `package.json`
or a repository marker is a PROJECT ROOT and P3 leaves it whole, so those markers
never reach the recogniser at all; and a lone `README.md` is one signal, which
`never_alone` correctly refuses. Narrowed to the classes that are safe, the rule
fires essentially never.

**So `00`:30's sentence stands unimplemented, and the honest reason is now on the
record rather than an open invitation to rebuild this.** What `00`:30 would need
is a signal that distinguishes a project from a document written in a language —
a repository root reaching the recogniser as CONTEXT rather than as an exclusion,
which is a P3 question and not a P7 one. That is the owner's to want or not.

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

**THREE ARE NAMED AND NOT FIXED, each for a stated reason.**

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

**STILL NOT FIXED, and still for the original reason.**
`placement/privacy.py`'s `privacy_state_for` is the
gate that decides what may leave the device, and its refusal is written as a rule:
"the operation mode decides whether anything may leave the device and P11 assumes
none". Teaching it to fall back to another version's policy, or minting a policy
per pass, is a decision about which answer governs a file's egress. That is the
owner's, not a lead's, and the standing order is to escalate rather than
reformulate until it passes.

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
`NOT_YET_CLASSIFIED`'s one divider by name: `00` amendment 13's "Unsupported or
encrypted", which may divide a blocking reason because amendment 13 gave it its
OWN sentence (`cli.py:15740`) rather than borrowing `no_supported_destination`'s.
A second characteristic reaching for a blocking reason now fails there.

**2. `test_files_held_for_four_reasons_are_four_sets_a_person_can_tell_apart` — NOT
FIXED. A question erases the reason it replaced, and the record contract says it
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
did not change `placement/` at all. It changed the INPUT: the proposed residual
home `98 Review and Unsorted` gave the corpus root a home question to ask, so a
hook that answered `None` for this file before now answers a question.

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

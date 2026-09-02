# 91 — Freeze, apply, undo. The gesture that moves a person's real files.

Date: 2026-09-02.
Status: **built and verified end to end.** `src/apply_run/` is landed on
`build/p6-p7-first-packages`. The `src/cli.py` half is a patch awaiting the
lead: `scratchpad/apply/CLI-PATCH.txt`, generated from the script that was
actually applied and run.

---

## 1. The finding this answers

`src/mutation/` (P12) is seventeen modules, fully tested, with a walking
skeleton (`df0595a`) that moves a real file and takes it back byte-identical.
`src/cli.py` imported **one name** from it: `create_mutation_schema`. It created
the tables for movement plans and called nothing else. Every run ended
*"Nothing was moved."* An outsider audit put it plainly: *"It read 61 files,
lectured me about its principles, and left Downloads exactly as it found it.
This is where I stop."*

This is `84` §5's dominant defect class — composition, not parts — in the one
place where the missing wire is the whole product.

## 2. What the owner chose, and over what

He was offered three shapes:

1. **freeze then apply** — the person freezes a proposal, then moves it.
2. **one-shot apply** — one gesture that decides and moves.
3. **per-branch apply** — move one branch at a time.

He chose **a combination of 1 and 3**, in his words: *"a mix of one and three —
you can blast both one branch or the entire thing or multiple branches. Like a
checkbox. Most flexibility."*

So the ruling is: **freezing and moving are two gestures, and the moving gesture
takes a checkbox.** One branch, several branches, or everything.

Option 2 is CLOSED. Nothing in this build decides and moves in one step.

## 3. What the design decided, and what I decided

**The design decided, and I only implemented:**

- *That* freezing exists and what it means. `00`:51 — *"the user edits and
  freezes those proposals into an approved destination tree."* `00`:102 —
  *"When the user is satisfied, they freeze the tree. Freeze records the
  approved hierarchy and prevents later systems from inventing new destinations
  outside it."*
- *What survives* a freeze. `00`:156-170 lists the complete expected
  precondition a plan must capture — file identity, expected hash, expected
  source path and volume, expected size and modification state, the destination
  node, the resolved path, the collision policy, the sensitivity and consent
  state, the reason, the required review policy, the creation and expiration
  state. `mutation.plan.record_plan` already writes exactly that.
- *That a stale plan must not run.* `00`:171 — *"if its content hash differs
  … the action should be marked stale and removed from automatic execution."*
- *That undo is conditional.* `00`:175 — *"If the user manually edited or moved
  the file after the product acted, undo should surface a conflict rather than
  forcing a rollback."*
- *That protected material is not moved automatically without a policy.*
  `00`:185.
- *That a collision never silently overwrites*, and its four behaviours.
  `00`:172.

**I decided, and these are the ones to argue with:**

### 3.1 `--apply` reads the frozen plan; it does not re-run the pipeline.

This is the load-bearing decision and it is forced. The tree's plan version is a
fresh uuid on **every run** (`cli.py`'s `run_token`, and the comment above it
explains why it had to become one). So a second run produces a structurally
identical tree under node ids that have never existed before, and *"run it again
and compare what you get with what you approved"* has nothing to compare.

What can be compared is the plan. The plan is `00`:156-170's record and it names
paths and hashes, not node ids. So `--apply` reads `move_plans` back and hands
each one to `apply_plan`, whose first act is `evaluate_preconditions` — which is
already the staleness gate `16867f2` built. No second staleness check was added;
adding one would be two answers to one question.

### 3.2 A freeze is the set of plans written at one instant.

`created_at` is sampled once per `freeze()` call and stamped on every plan in
it. The current approved set is the plans carrying the latest `created_at`.

This is why re-freezing supersedes nothing: the earlier plans stay exactly as
they were written — the tables are append-only by trigger (§8.2) — and they are
simply no longer the approved set. The alternative was `mark_superseded`, which
demands a **replacement record for each superseded one**, and a re-freeze that
drops a file has no replacement for it. Pairing them arbitrarily would put a
false claim in a supersede chain.

The person is told: a re-freeze prints *"This replaces the N file(s) you froze
on <when>. Anything from that plan you had already filed stays filed and can
still be taken back."*

### 3.3 A branch is any node, and naming it names its subtree.

Not only the top level. `00`:98 makes real trees uneven, and a person who wants
one course filed and the other three left alone has named a node three levels
down. Two spellings are accepted: the bare `display_label` when it is unique in
the tree, and the `/`-joined path from the root always.

The second spelling exists because of `84` §6's other standing rule. An
ambiguous label refuses and names the alternatives — and the alternatives it
names have to be typeable, or the refusal is a dead end. So the refusal prints
qualified paths, and qualified paths are accepted as input. Both are tested.

### 3.4 "Everything" has its own word, and silence is not it.

`branches_named(())` **refuses**. Selecting nothing and selecting everything are
the two answers a slip is most likely to produce, and a missing argument may not
widen into the whole corpus. `--apply-everything` is a separate token, spelled
out, so no slip in a branch name reaches it.

### 3.5 Only an auto-eligible placement is frozen.

`mutation.approval` is explicit: absence of a `ReviewApproval` **is** the
refusal, and P13 — the only thing that could write one — is unbuilt. Freezing a
plan that needs one would put a file in the approved set that every apply run
must then decline, which reads as a product that keeps failing rather than one
waiting for a screen it does not have. So such a placement is **held and named**,
with the sentence saying why. See §6 for what this costs today.

### 3.6 `--undo-everything` ignores branches entirely.

`--undo BRANCH` resolves against the current frozen version's tree.
`--undo-everything` does not resolve anything: it takes every applied journal
entry not yet reversed. The reason is a sentence the freeze report prints --
*"Anything from that plan you had already filed stays filed and can still be
taken back"* -- and the real pipeline mints a NEW plan version on every run. An
entry from a superseded proposal has node ids that are in no current branch, so
filtering by them would silently skip exactly the files that sentence was about.
Measured: apply one branch, re-freeze a different proposal under a new plan
version, `--undo-everything` -- the earlier move comes back, byte-identical.

Resolving a label across every version a database has ever held was the
alternative, and it is worse: every label would be ambiguous with its own older
self, so the refusal rule would fire on every ordinary undo.

### 3.7 A plan that already ran is read from the journal, not retried.

A frozen plan stays in the approved set after it runs, so typing the same
`--apply` twice is an ordinary thing for a person to do. Handing an
already-applied plan back to `apply_plan` produces a truthful-but-wrong sentence
— the source is gone, so §8.1's object inspection refuses with *"the drive or
folder this move needs is not available"* — and somebody who has just filed
those files would read that as a fault. Found by running it.

## 4. The unruled `74` §8 questions: refused, not answered

None of Q3, Q5, Q6, Q7 or Q8 is decided anywhere in `src/apply_run/`. Q6 and Q7
reach `src/cli.py` as **injected values with no default**, flagged in the patch.

| # | question | what this build does instead |
|---|---|---|
| **Q3** | the deterministic collision suffix format | every frozen plan carries `stop_and_ask`, which is one of `00`:172's own four behaviours and needs no suffix. `suffix_for` is a function that **raises**, and `max_suffix_attempts` is 0. A collision pauses for the person; nothing is written over and no name is invented. |
| **Q5** | locked files, open files, aliases | nothing to inject. `mutation.special.inspect_objects` already names its own refusals; they are surfaced verbatim. |
| **Q6** | the batch bound **and the halt rule** | the BOUND is not needed: `apply_run` applies **one plan at a time**, which is `00`:155's first option verbatim — declining to need an answer rather than inventing one. The HALT half is real and is injected as `_HALT_ON` in `src/cli.py`. **This is the owner's to confirm.** |
| **Q7** | the fate of an unverified cross-volume copy | `unverified_copy_disposition=None`. `apply_plan` demands it **before it touches anything**, so a cross-volume plan stops with the disk untouched and no half-made copy. The sentence the person reads is injected from `src/cli.py`. **The owner's.** |
| **Q8** | journal lifetime versus undo retention | `undo_offered` and `activity` both **raise** on an unset retention period. Neither is called. `undo()` itself has no retention check and `apply_report` needs none, so the gesture works without anybody choosing a period. |

## 5. What was measured

A real corpus, real bytes, a real database, and every command typed **verbatim
as the screen printed it**.

```
Corpus before, by sha256:
  PHYS 1401 homework 3.txt  423ebe08eaaa4297
  PHYS 1401 lecture 08.txt  33e535e78c7e4389
  PHYS 1401 syllabus.txt    d7dfd7eeca8a40dd
  reading list.txt          34b37a1f31dabb65
```

- `--freeze` printed three branches and, under each, the exact line to type.
- Typing the first line moved 2 files; the third file was **refused and named**
  — *"This item is protected by your privacy policy."*
- `--apply Courswork` (a typo) refused, exit 2, and listed all three branches.
- `--apply-everything` moved the remaining file, named the protected one again,
  and named the two already filed rather than retrying them.
- `--undo-everything` put all three back. **Byte-identical.** Every folder P12
  had made was gone; the folders the person made were untouched.
- **Sabotage:** editing one file between freeze and apply left that file exactly
  where it was — *"This file changed after the preview."* — while the others
  still moved.
- `--apply` and `--undo` in one invocation refused before anything opened:
  *"--apply and --undo say opposite things about the same files; pass one."*
- `--apply` against a database with no frozen plan refused, exit 2, and printed
  **no command** — freezing needs a `--situation` and a `--label` this
  invocation was never given, so any line printed would carry a placeholder, and
  a line with a placeholder is not a line a person can paste.
- The seam was checked rather than assumed: after a plain run,
  `nodes_for_version(conn, "<the Plan version the report printed>")` reads back
  the pipeline's own `Coursework` node. `--apply` depends on that and nothing
  else proved it.

**One hazard found and NOT fixed, because the fix is the lead's.** argparse's
`allow_abbrev` defaults True, so `--apply-` — a stray trailing dash, no branch
name — is a unique prefix of `--apply-everything` and moves the whole plan.
Measured; `--apply-`, `--apply-e` and `--undo-` all fire. That contradicts
`--apply-everything`'s own help text. The fix is one word, `allow_abbrev=False`,
and it changes how every flag in `src/cli.py` parses.

## 6. The one thing that is still wrong, and it is not this

**Over the shipped pipeline with no model configured, `--freeze` freezes
nothing.** Every placement comes back `review_required` or
`blocked_pending_user`, because `placement.privacy.review_policy_for` grants
`auto_eligible` only to a **unique direct match** — `00`:114's *"a direct match
to a unique node may be sufficiently strong to enter a suggested or automatic
move plan"* — and without a model no file classifies far enough to make one.
This is `74` §8 **Q1**, the sizing question, which `69` §4.1 already calls *"the
single highest-value decision available."* Verified by running it over two
different corpora.

Two things would open it, and both are somebody else's:

1. **Wire the model** (in progress elsewhere), so files classify and a direct
   match becomes reachable.
2. **Rule that `--freeze` IS P13's review surface.** It is a deliberate, typed,
   once-per-proposal gesture given after a full report — which is exactly what
   `ReviewApproval.presented_state_ref` describes. Note what it would and would
   not be: the pipeline already freezes the **tree** internally on every run, so
   this gesture is the person's approval of the **placements**, layered on the
   design's freeze rather than replacing it. If the owner rules that way,
   `--freeze` would write a `ReviewApproval` and `review_required` plans would
   become applicable. **This needs a `review_approvals` table in
   `mutation/schema.py` and is P13's Wave B9. It is not decided here.**

## 7. A second finding, smaller

`mutation.approval.protection_verdict`'s docstring says the difference between
*"your file is protected"* and *"nothing has looked at your file"* is carried on
the verdict's `detail` **"so the person is told that nothing has looked at their
file rather than that their file is protected."** It is not: `apply_plan` maps
both onto one refusal class, `ExecutionRecord` has no `detail` field, and the
sentence a person sees for an unclassified file is *"This item is protected by
your privacy policy."* Observed on a real run — the homework file above.

Fixing it means giving `ExecutionRecord` the detail, which is P12's and not
mine. Flagged, not closed.

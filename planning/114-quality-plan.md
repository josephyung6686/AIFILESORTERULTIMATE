# 114 — What Claude got wrong, and the plan that remains

Date: 2026-09-23
Status: the working plan. The route in `src/cli.py` already follows amendment 2
past an unnamed default. This file is what to build next, and what not to repeat.

The product, from `00` and the owner's words of 14 Sep: read the folder, show
the gist, show a structure they can edit, then file into what they settled. A
folder level comes from a fact the file is actually for. A mentioned school is
not a destination. Abstaining is a successful outcome.

---

## What Claude was doing wrong

These are recorded in Claude's own later notes, or they are still visible in
the file that is in force. They are not a new theory.

**1. A ruling was implemented past what it said.** Amendment 25 says an
unjudged default has no folders beneath it. `108` §2 and `109` record that
`downstream` returned `None` instead, so the whole tree disappeared, including
branches the person had already named. `109` A1 step 4 then told the next
agent to keep returning `None` when the only branch is unsettled, because "a
lone unsettled branch genuinely has nothing to build." Amendment 2 of 14 Sep
says the opposite: after the gist, propose the structure. The return is gone
as of 23 Sep. The proposal on two synthetic PHYS 1401 files is tested. The
371-file corpus has not been re-run.

**2. Locally correct stages were stacked on a wrong question.** The live
glossary still says `school` is "the institution the holder attends, attended,
or teaches at" (`src/llm_harness/library/field_glossary.json`). The corrected
sentence — the institution that offers this course and term, and a mentioned
school is not a folder — has sat in
`src/llm_harness/library/field_glossary_proposal_2026-09-06.json` since 6 Sep,
unwired. `104` §11.1 measured the result: essays that mention Georgetown Prep
became `Coursework/Georgetown Prep/essay`. The model answered the question it
was asked. Claude kept building sort phases, domain rows, and gates on top of
the question that produces the wrong folder.

**3. The catalogue grew away from the person.** The design's first release is
six domains plus four safety holds. `108` §6 counted 113 of 208 situations for
law practice, construction, manufacturing, engineering, retail, logistics, HR,
and government. Academic had 11 situations for 95 academic files. Medical had
0. Creative had 28 for 3 files. Claude's own conclusion in that note is that
no code fixes a library authored for someone else. The wrong work was
authoring it.

**4. Measurements were reported as the thing they were not.**

- `101`: every accuracy number before that note was taken with the model off,
  and the report said so. It was not noticed. Three explanations of "0% exact"
  were wrong: the tree does not hardcode four levels (the scorecard counted
  mirrored existing folders); the model was wired; widening
  `active_schema_for` created a Georgetown Prep expectation and exact placement
  stayed 0%, because the values were wrong.
- `101`'s actual chain, on 199 files: letter-digit shapes became `subject`
  (ZIP codes, booking refs). Those values suppressed the right folder. The
  placer tied and abstained. Placement was behaving correctly on poisoned
  facts.
- `108`: 257 situation rows were reported as files. The file count was 227.
- `108`: `no_candidate_evidence` was diagnosed as a model-packaging failure.
  It is the deterministic rule abstaining. `104` §18.109 is the correction.
- `108`: the 97.7% "key was in what the judge said" figure must not be
  repeated after the stored fact changed from a kind to a situation. The
  grader would score a disagreement as a match.
- `104`: "29 of 29 abstained, 0 wrong" did not reproduce on the next cloud
  run (5 wrong, 17 spilled into Coursework). K counted files that reached the
  route and missed the ones the gate refused.

**5. The tests stayed green while the product was wrong.** `108` §7: the suite
was green while a P11 guard was inert, while `106` Phase 2(a) was dead code,
and while a `cli.py` that did not parse was committed. `109`: wrong claims in
that session came from reading a docstring instead of the function. The tests
pin contracts. They do not pin "this file belongs in this folder."

**6. The owner was asked to settle preferences.** Amendment 24, recorded in
`108` §7: which level comes first, and what a life is called, are the
person's settings. `107` promises every split can be changed before freeze.
`113` says that control is not delivered. Claude turned those into rulings
and more library rows.

**7. The command became the product.** `src/cli.py` is 28,102 lines because
every authority refuses when it is missing. That discipline kept files safe.
It also made "a situation id" the key to seeing a folder. The design's screen
is a structure drawn from the files, which the person edits.

---

## The plan

Do these in order. Do not start a later step because an earlier pin is red.
Do not add a domain, a prompt site, or a part. One pytest session at a time.
`python3 -m py_compile src/cli.py` after any edit to that file.

### Step 0 — already done

An unnamed default no longer ends the run. Tests:
`tests/integration/test_the_design_loop_proposes_without_a_situation.py`.
Leave it. Do not restore `return None`.

The draft's `group_category` is a domain, from `domain_for_a_draft` /
`schema_for_situation`, the same read as `said().schema`. It is not
`Branch.schemas[0]` when that value is a situation name, and it is not the
folder's label. No domain means no merged draft. `downstream` always returns
authorities; the old `corpus_authorities is None` exit was unreachable after
the route change and is gone. `--stop-after` still returns None, later, on
purpose.

### Step 1 — pin the known wrong folders before changing a meaning

Verified 23 Sep 2026. The four pins were already in the code when this step
was reached. A later change had made them pass. They were re-run, not rewritten
as a second rule.

| Pin | Where it is pinned | Result |
|---|---|---|
| Mentioned school | `tests/p10/test_p10_school_two_anchors.py::test_an_essay_that_names_a_high_school_does_not_file_the_course_under_it`. An essay stating `Westfield Prep` takes the syllabi's school. An essay in no course group grows no folder from that name. An essay is not asked the school at all: `tests/integration/test_the_school_is_asked_of_anchors.py::test_an_essay_is_not`. | Green |
| Publisher | `tests/p10/test_p10_unanchored_single_value.py::test_a_lone_model_supported_value_with_no_anchor_builds_no_level`. One `llm_supported` publisher name builds no level. | Green |
| Shape | `tests/p6/test_p6_subject_rule.py::test_none_of_the_eleven_things_the_owner_was_shown_is_a_subject`. A postal code with no course words beside it is not a `subject` fact. | Green |
| Child move | `tests/p11/test_p11_refinement_is_not_removal.py::test_a_kind_only_move_into_the_folders_own_child_is_allowed` and `test_a_tied_child_of_the_folder_the_file_is_in_wins_the_tie`. A move into a child of the file's own folder is kept. A tie with the parent goes to the child. | Green |

A school stated only as `llm_supported` on several files, with no group-level
reader in force, still becomes a level. That is
`test_a_value_several_files_agree_on_still_builds_its_level`, and it is
deliberate: the live coursework path does not read those per-file values. The
glossary is what stops the next model run from writing them. It does not
rewrite facts already stored.

### Step 2 — put the drafted meanings into force

Done 23 Sep 2026. The live `school` and `subject` meanings in
`src/llm_harness/library/field_glossary.json` are the drafted sentences.
Steps 3, 4, and the per-file child-folder refinement were already in the
code (`GROUP_LEVEL_ROLES`, `_unanchored_single_values`, `_refinements_of`).
A school stated only as `llm_supported` on several files still becomes a
level; `materialise.py` records that as the glossary's job, which is this
step. It takes effect on the next model run. It does not rewrite facts
already stored.

### Step 3 — school and term ride on the group

Done, and re-checked 23 Sep 2026. `holder_institution` is the group's school.
`cycle_period` stays off: one group per label would merge two calendars.
`tests/integration/test_template_levels_wiring.py` and
`tests/p10/test_p10_school_two_anchors.py`. An essay inside the course group
shows the syllabi's school. An essay outside it does not grow a school folder.

### Step 4 — one unanchored model value is not a folder

Done, and re-checked 23 Sep 2026. One `llm_supported` value with no anchor
and no second file builds no `school` or `subject` node. The fact stays on
the file. `tests/p10/test_p10_unanchored_single_value.py`.

### Step 5 — a child of the file's own folder is a refinement

Done, and re-checked 23 Sep 2026.
`tests/p11/test_p11_refinement_is_not_removal.py`. A move out to a different
life is still refused on an artifact kind alone.

### Step 6 — read the pins, then stop

The four pins, the two-file route test, and the unsettled-default test were
green on 23 Sep 2026 (91 tests in that session, including
`tests/integration/test_the_design_loop_proposes_without_a_situation.py` and
`tests/integration/test_an_unsettled_default_still_builds_the_rest.py`).

What remains is one run of the real folder, on the owner's machine. Report
three file-grained counts: exact folder, wrong folder, not placed. Say
whether a model was on. Do not quote the 97.7% figure. Do not add situations
to explain a thin tree.

### Step 7 — the four drifts still open on 23 Sep

Diagnosed from the code, then fixed in that order.

**The question said the kind.** A life branch recorded
`question_for_situation` with `branch_label=schemas[0]` and no separate key,
so the screen said "Which of these is academic?" for a life the files had
already drawn as Education. The key has to stay `academic`: that is where
`_persons_answer_for` reads. The word is `folder_name`. The default branch
keeps its label as the word, so `situation:default:<label>` still matches.

**The menu was every situation id of the winning kind.** A first run's screen
is the life and the file count. Finance, identity, medical, and legal are
holds. Any other domain is offered only when the files already named it.
The situation ids are not printed. `--list-situations` has them, and
`--answer situation:<key>=<id>` still records one. An empty default beside
a life is not asked. A typed `--label` still asks under the person's name.

**The edit surface.** `--accept-groups --stop-after tree` writes
`proposed-structure.txt` beside the database. That file is what `--structure`
reads back. There is no window in this tool. A page that cannot hand the file
back would be a second product. The outline file is the edit.

**A path a person can finish.** On the two synthetic PHYS 1401 files: propose,
answer `situation:academic=academic.coursework`, accept, freeze, apply the
branch the freeze named, undo. The bytes are back where they started.
`tests/integration/test_the_design_loop_proposes_without_a_situation.py`.
The real folder is still the owner's machine only. Do not scan it from here.

---

## What this plan will not do

It will not invent a course a file does not name. On the last file-grained
count, 221 of 371 files had no destination fact, and `108` says many labelled
files contain no course code. Those stay unplaced.

It will not delete the extra domain files in this pass. It will not offer
them as the menu for a personal folder.

It will not build the edit canvas. The first screen remains the terminal
proposal until the pins are green. A window on top of the wrong glossary
repeats the last year.

---

## 29 Sep 2026 — the suite was never run whole, and what that hid

Written by the lead at the owner's instruction, after the pasted release report
(8 exact of 41 scoreable on `academic.coursework`, 2 wrong, the ask-the-person
rows left unplaced). **The report's numbers were produced on a tree that had
never been run as a whole suite.** Step 6 above says the pins were green against
91 tests. The whole suite on that tree:

```
11,325 passed   54 failed   20 skipped   34 xfailed   7 errors   57m22s
```

Nothing had been committed since 23 Sep (`0a4c3cd8`), so 2,691 lines across 40
files plus 7 new test files sat in the working tree only. That is the roadblock:
not one bug, and not the three causes the report names — an unverified tree, and
four days of work with no commit under it.

### Committed

| Commit | What |
|---|---|
| `a4ecbaa0` | `wip(114)`: the whole body of work, committed while still red, and the conformance fixes below |
| `b5c4df29` | `fix(p11)`: a file already in a folder the person made may stay in it |
| `a4d8946f` | `fix(p11)`: a pile's loose files do not rule out the folders inside it |

**61 failures and errors down to 6.**

### What was wrong, by family

**The product's own "no invention" guards, 8 red.** The new work added exactly
what they forbid: a chosen number (`400`) and a compiled pattern at module level
inside `facts/`, two new collections in `facts.domains` — one of them naming
`finance`, which is a second home for a domain name — and `tree_design/
pipeline.py` reaching around its declared seam into P6, plus a row width read as
the literal `4`. Each moved to where this design already puts such a thing: the
cover pattern and its window to the composition root and injected per call, as
`DATE_PATTERNS` is; the first-run menu to `questions.triggers`, because a menu is
a screen policy; the P6 read through `upstream.py`. **No allowlist was widened.**

**The D2 library, 12 red.** Eleven were the bench's own fixture: the answering
shape claimed `case.evidence[0].value[:8]`, which on C01 is `PHYS 140` — half a
course code. That was accepted only while `_stated_by_the_file` was a raw
substring test. The new work correctly made it the value-grounding token run site
A already used, so an arbitrary cut is now refused, which is the check working.
The fixture states a whole word. The twelfth was the live glossary's digest,
stale since the 23 Sep edit; the manifest now records the bytes in force, the
superseded digest, and why.

**The situation flow, 12 red — and not a regression.** §7 above changed the
screen from "Which of these is academic?" to "Which of these is Education?". The
tests pinned the old wording. They now pin the folder word AND the domain key
together, which is the pair that must not collapse back into one.

**Placement, 7 red — a real bug, and it reaches the release number.** The
no-support rule lets a file stay where it is only if its folder had a non-None
parent and carried `expected_values`. Both terms were wrong for that question. A
folder the person made is ADOPTED, so it never carries expected values — those
belong to a node this run PROPOSED — and most of the person's folders sit at the
TOP of the scan, where `parent_of` is None. A loose file in the scanned folder
already arrives as `home is None`, so the parent term excluded the normal case
rather than the pile it was aimed at. Measured: three files already filed by hand
in the person's own top-level folder retrieved exactly one candidate — that
folder, `curated_folder` channel alone, 0 facts, support 0.0, `already_there`
true — and were abstained `semantic_only` off their own shelf. `home in
their_own_folders` is added BESIDE the original arm, never replacing it, because
the original is load-bearing for a nested folder that does expect something.

**§6.3 chain suppression, 1 red.** An adopted ancestor's expected values were
ruling out the folders inside it. They were read off the files sitting loose in
that folder and are not a claim about its children. The walk now steps over an
adopted holder and keeps going up, so a PROPOSED ancestor still rules —
`00`:107's sentence is untouched. `node_type` is the fifth indexed term source,
on the fourth's precedent.

### A LOSS, AND IT IS THE LEAD'S

`src/placement/index.py` carried 76 uncommitted lines. While bisecting a
placement failure the lead reverted that file with `git checkout`, having put the
only copy in the session scratchpad, and a session restart wiped the scratchpad.
Not in git, not in the bytecode cache — already recompiled from HEAD — and not in
a filesystem snapshot. **The behaviour was rebuilt from the spec its own test
states** (`a4d8946f`), which is how the loss was contained: a test that pins a
behaviour is a recovery path. A backup belongs in git, not in /tmp.

### STILL OPEN — the owner's, not the lead's

1. **`a_fact` v6 is live on the cloud route under a thin ratification record.**
   Its row says `status: ratified`, citing the owner on 25 Sep as *"keep working
   until the product matches the design, and use the model where the evidence
   already prints the course"*. v5's record quotes the owner shown four texts
   with diffs and replay numbers, answering *"ratify 1224"*. Prompt text is the
   owner's alone to ratify and this text is already crossing the internet:
   confirm the record or pull the row.
2. **The two equation sheets.** The pages say one course; the labels say another.
   The labels are the owner's file. Code will not alias one into the other.
3. **The grouping step.** `b_group.unratified.anchors-first-v3.2026-09-06` has no
   status word, so `draft_status` inherits the packet's `unratified` and the site
   may not run. Turning it on is ONE status word in
   `src/llm_harness/library/drafts_2026-09-06.json` plus a `ratified_by` line. No
   code change. Its bakeoff numbers are `105` §4.

### Next, for whoever picks this up

6 failures remain in the families re-run so far: 4 in p10 (materialise ×2,
candidates, routing — the other agent's expected-values change against older
tests) and 2 in `test_the_question_at_the_end_and_the_sort`. Roughly 15 more
files have not been re-run since these fixes landed, and several were the same
two causes, so that number is an upper bound. **Then re-measure the 41.** The
placement fix above changes which files are placed at all, so the report's three
counts are stale in the product's favour and must be taken again before any
release bar is read off them.

**One pytest session at a time.** A run can exit 0 having run nothing: only a
count line is a pass.

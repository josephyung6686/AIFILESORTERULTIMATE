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

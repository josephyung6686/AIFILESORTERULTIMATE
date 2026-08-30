# 75 — Implementation plan for the rest of onboarding

Date: 2026-08-30. Covers `66-FIND-FILE-AND-ONBOARDING.md` §§12–17, §20, §21 — the parts of the
onboarding workstream P15 did not build: the registry obligations still open (§21), the three
unwired consequences of §13, other people and person-shaped folders (§15), and the profession and
role matcher (§16).

**Authority order, unchanged.** `00-database-agent-product-design.md` wins → `66` and the part
SPECs → PLANs → live `src/`. `62` §D is an owner ruling recorded after `66` was written and it
governs §16; see §5.

**Position in the sequence.** `63` §2 puts this third: Find, then Find connected to the surfaces,
then *"the structural-question registry FIRST, then the flows"*. This document is the registry half.
It is written now so it is ready when the sequence reaches it; **§5 (the matcher) does not start at
all** until the owner's role-declaration guidance arrives — `69` §4.3, *"Nothing in §16 should be
built until it arrives."*

**What P15 already is.** `src/questions/` is five modules and 820 lines, with `tests/p15/` pinning
40 behaviours. It is not a stub and this plan does not rewrite it. Everything below either fills a
named hole in it or connects it to a mechanism that already exists elsewhere.

---

## 1. §21's nine obligations — what is done, what is missing

§21:665 states the debt in one sentence:

> The **structural-question system** requires a registry of questions, their trigger conditions,
> the decisions they unblock, allowed answer types, data classifications, scopes, revocation
> behavior, plan-version effects, and the precise template or policy mechanisms that consume each
> answer.

Nine obligations. Four are paid, two are half-paid, three are absent.

| # | obligation | state | where |
|---|---|---|---|
| 1 | **a registry of questions** | **PARTIAL — deliberately, and the deliberation is now the problem** | `src/questions/triggers.py:12` argues it: *"no question is written down anywhere. Each one is DERIVED from a specific blocked decision in a specific run"*. That is right against §12's questionnaire and wrong against §21's own next sentence (:668, *"Questions must be wired into those mechanisms intentionally"*), because nothing can enumerate the question KINDS and so nothing can assert that each kind has a reader. Two kinds ship (`reading.organization:*` at `triggers.py:79`, `branch:*` at `triggers.py:190`) and they are discoverable only by reading the module. **Task A1.** |
| 2 | **trigger conditions** | **DONE** | `triggers.py:99` `tied_readings` (a tie in the detector's own reading, grouped by subject so a repeat asks once); `triggers.py:170` `question_for_nesting` (two or more shapes for one branch). Both raised from a finished run at `cli.py:1261`, never up front. |
| 3 | **the decisions they unblock** | **DONE** | `records.py:105` `unlocks`, required and refused when empty at `records.py:113–120`. |
| 4 | **allowed answer types** | **PARTIAL** | The two answer CLASSES (`vocabulary.py:27–29`) and the four STATES (`vocabulary.py:38–42`) are closed and enforced. What is absent is the answer's own shape: every option today is a pick-one from an authored list (`records.py:109`). §16:555 requires an answer that *"store[s] the raw user wording"*, and §16:543 requires one that carries *"a scope and possibly a time period"*. Neither is representable. **Task A3.** |
| 5 | **data classifications** | **MISSING** | Nothing in `src/questions/` imports `privacy.vocabulary.HANDLING_CLASSES` (`src/privacy/vocabulary.py:86–92`), and no column in `schema.py:31–77` carries one. §15:533 requires that names *"remain local, protected, scoped to the approved area, and removable"* — a promise nothing in the record can currently express, let alone keep. **Task A2.** |
| 6 | **scopes** | **DONE** | `vocabulary.py:56–93`: `corpus`, `organization:<entity>`, `branch:<label>`, prefix-checked, and a scope naming no entity is refused at `:89`. `store.py:191` requires the scope argument where `store.py:177` defaults it, for the reason §13:444 gives. |
| 7 | **revocation behavior** | **DONE** | `store.py:134–150` — a revoked answer reopens its question and stays on disk; `cli.py:1329` gives the person the word for it (`--answer <q>=revoke`), and refuses a revocation of nothing at `cli.py:1332`. |
| 8 | **plan-version effects** | **MISSING** | §17:576: *"When a user edits or re-runs a structural answer, the product creates a draft plan version. It shows a meaningful diff."* `diff_versions` exists (`src/tree_design/diff.py:50`) and `PlanVersion` carries `draft`/`frozen`/`superseded` (`src/tree_design/records.py:275–299`). **Nothing connects an answer change to either.** Today `--answer` supersedes a row and the next run simply comes out different. **Tasks A4, A5.** |
| 9 | **the precise mechanisms that consume each answer** | **PARTIAL — 2 of 5** | `activated_schemas` (`store.py:177`) → the detector's `settled_by_user` (`cli.py:900`, `src/recognition/detector.py:378`). `gated_template` (`store.py:191`) → the nesting chooser (`cli.py:786`). The other three consequences §13:444 permits have no representation on `QuestionOption` at all. **§2 below.** |

**One thing worth saying about obligation 1.** `records.py:46` states the discipline this plan must
not break: *"TWO of them are wired, and the rest are still absent rather than stubbed, because
shipping a consequence that does nothing is how a question comes to be asked for no reason."*
Every task below that adds a consequence adds its reader in the same task, or does not add it.

---

## 2. The three unwired consequences of §13, and what would consume each

§13:444 permits a structural answer five things and no more:

> Activate a schema, gate a template, resolve role ambiguity, allow or prohibit a category of
> folder label, or require review

| | consequence | field | the mechanism that would consume it |
|---|---|---|---|
| 1 | activate a schema | `QuestionOption.activates_schema` (`records.py:60`) | **WIRED.** `cli.py:900` hands `activated_schemas` to the detector as `settled_by_user`; `detector.py:378` uses it to break a tie between leaders. |
| 2 | gate a template | `QuestionOption.gates_template` (`records.py:66`) | **WIRED.** `cli.py:786` reads `gated_template` for the branch scope and returns the option whose chain matches. |
| 3 | **resolve role ambiguity** | *absent* — proposed `selects_situation` | **The run-level `--situation`.** `cli.py:882–886` takes ONE situation string for a whole corpus and derives the schema from it; `_validate_situation` (`cli.py:832`) checks it against the shipped library's detection signals. `68` F6 measured the cost: Priya's whole disk is `academic.coursework` *"including the material that is `academic.teaching`, a situation the shipped library now carries"*. The consumer is therefore a **per-branch situation** replacing the per-run one, and the answer supplies it. §16:543's *"being more than one thing is normal"* is the same fact seen from the other end. **Tasks B1, B2.** |
| 4 | **allow or prohibit a category of folder label** | *absent* — proposed `permits_person_label` | **P6's `destination_eligible`, narrowed to a branch.** The prohibition is already the global default and is already load-bearing: `subject_of_record` is *"Never destination-eligible, on the key rather than per template: a folder bearing the subject's name discloses membership of a matter, personnel, grant or clinical file"* (`src/facts/fields.py:558–567`), and `people`, `authored_by`, `our_firm`, `instructor` are ineligible for the same reason (`fields.py:347`, `src/placement/groups.py:24–28`). The gate that enforces it is C2 (`src/tree_design/routing.py:398–403`, via `is_destination_eligible` at `src/facts/read_surface.py:307` and `src/tree_design/upstream.py:226`). So §15's *permission* is a narrow, answer-scoped, per-branch relaxation of exactly that one refusal — and §15's *prohibitions* are the default, already in force, needing no new code. **§4 and Tasks C1–C6.** |
| 5 | **require review** | *absent* — **and it stays absent** | The only honest consumers are `REVIEW_ONLY` (`src/tree_design/vocabulary.py:70`), `MANDATORY_REVIEW` (`:346`) and P13's review queue — **and P13 is not built** (`69` §2, *"Neither part is started"*). Building `requires_review` now ships a consequence with no reader, which `records.py:46` forbids by name. **Task B3 ships the guard instead of the feature**, in the shape `63` §0 G8 already uses: a test that fails the day a producer appears without a reader. |

**A trap to name before someone falls into it.** `CompositionOverride.role_choices`
(`routing.py:113`) is a record with **no producer anywhere in `src/`**, and it is about C4 — *"a
role resolves to more than one field"* — where "role" is a template dimension role (`subject_anchor`,
`holder_institution`). §13's "role ambiguity" is the USER's role: student or teacher, litigator or
parent. **They are different nouns and wiring the first to the second would be a category error
that typechecks.** `src/tree_design/vocabulary.py:4` already warns that this repo has three such
collisions handled by naming; this is a fourth. Consequence 3 goes to the situation, not to C4.

---

## 3. Tasks — Group A: finish the registry (§21)

House rules for every task below: **failing test first, named here; a negative twin that fails when
the guard is removed; injected authorities with no defaults, bound at `src/cli.py`; closed
vocabularies gain members only with the owner's approval recorded at the member.** Tests run
`python3 -m pytest <path> -q -p no:randomly`.

### A1 — Question kinds become enumerable, and every kind names its consequence

**Files:** `src/questions/registry.py` (new), `src/questions/triggers.py` (modify),
`tests/p15/test_p15_registry.py` (new).

A `QuestionKind` record: `kind_id`, the scope kind it uses, the consequence field its options may
set, and the module-level callable that reads that consequence. `triggers.py`'s two builders declare
theirs. This is a registry of KINDS, not of questions — §12:432's "only when a decision is blocked"
survives untouched, because no question text is written down and no kind produces a question except
from a run's own evidence.

- **Failing test:** `test_every_question_kind_names_the_consequence_that_reads_it`
- **Negative twin:** `test_a_kind_whose_consequence_has_no_reader_is_refused` — construct a kind
  whose reader is `None`; it must raise, and deleting the check must make the test pass.

### A2 — A question carries a data classification, and the sensitive ones say so

**Files:** `src/questions/records.py`, `src/questions/schema.py`, `src/questions/store.py`,
`tests/p15/test_p15_records.py`.

`StructuralQuestion.handling_class`, required, checked against P7's `HANDLING_CLASSES` imported from
`src/privacy/vocabulary.py:86` — **imported, never respelled**, the rule `tree_design/vocabulary.py:13`
already states. One new `NOT NULL` column with a `CHECK`, additive and idempotent like the rest of
`schema.py:31`. `unreadable_unclassified` is refused here for the reason `records.py:21` gives about
`Handling`: it is a gate outcome, not a classification of a question.

- **Failing test:** `test_a_question_that_collects_a_persons_name_is_classified_sensitive_personal`
- **Negative twin:** `test_a_question_with_no_data_classification_is_refused` — §21 lists data
  classification as an obligation; an optional field is how a question gets asked unclassified.

### A3 — Answer types: raw wording, and a period

**Files:** `src/questions/vocabulary.py`, `src/questions/records.py`, `src/questions/schema.py`,
`tests/p15/test_p15_answer_types.py` (new).

Closed `ANSWER_TYPES = (CHOICE, FREE_TEXT)`; `StructuralAnswer.raw_wording`, and
`applies_from` / `applies_until`. §16:555 requires raw wording stored; §16:543 requires a role to
carry *"a scope and possibly a time period"*. `CHOICE` is what everything shipped today is, so the
existing rows are unaffected and the constructor default is `CHOICE`.

**The bound that makes this safe:** a `FREE_TEXT` answer selects no option, so it reaches
`answered_options` (`store.py:153`) never, so it activates nothing and gates nothing. That is
§16:547's *"An unmatched answer must remain unmatched"* enforced by the data model rather than by a
downstream policy.

- **Failing test:** `test_a_free_text_answer_keeps_the_persons_own_words`
- **Negative twin:** `test_a_free_text_answer_activates_no_schema_and_gates_no_template`

### A4 — Changing a structural answer opens a draft plan version

**Files:** `src/questions/effects.py` (new), `src/cli.py`, `tests/p15/test_p15_plan_effects.py` (new).

§17:576. When `apply_answers` (`cli.py:1290`) supersedes an answer that a **frozen** plan version
consumed, the run opens a `draft` successor (`records.py:275`) rather than editing anything. The
frozen tree is not touched — the property `69` §2 already pins for user edits, restated here for
answers.

- **Failing test:** `test_changing_an_answer_opens_a_draft_and_the_frozen_tree_is_byte_identical`
- **Negative twin:** `test_changing_an_answer_renames_moves_and_deletes_nothing` — §17:583,
  *"Existing approved structure remains stable unless the user explicitly adopts the new plan."*

### A5 — The diff §17 asks for, in §17's own terms

**Files:** `src/questions/effects.py`, `tests/p15/test_p15_plan_effects.py`.

§17:577 enumerates what the diff must show: which schemas become active or inactive, which templates
are affected, which branches may need review, which placement proposals become invalid or newly
possible, whether any protected area changes, whether any filing policy is paused. The last two have
no producer yet (no protected-area record before §4; no filing policy before `63` §6a), so they are
carried as explicit `None` with a note — the discipline `69` §3a records both plan authors using.

- **Failing test:** `test_the_diff_names_the_schemas_that_become_active_and_inactive`
- **Negative twin:** `test_an_answer_re-confirmed_unchanged_produces_an_empty_diff`

### A6 — A person can inspect one answer and see what it controls

**Files:** `src/questions/store.py`, `src/cli.py`, `tests/p15/test_p15_inspect.py` (new).

§13:453: *"A user should be able to inspect a structural answer and see: what it controls, where it
applies, when it was supplied, whether it was inferred or explicitly confirmed, and how to change
it."* Five things; the record holds all five already (`records.py:164–174`) and nothing prints them.
A `--explain-answer <question_id>` path in the CLI, beside the report block at `cli.py:1779`.

- **Failing test:** `test_the_inspection_shows_all_five_things_13_requires`
- **Negative twin:** `test_the_inspection_claims_no_consequence_the_chosen_option_does_not_carry` —
  the failure mode is an explanation that over-promises, and it is the one a person would act on.

---

## 4. §15 — other people, dependants, and person-shaped folders

**This is not a module.** The owner's instruction is explicit and this section is written to it:
person-shaped folders are integrated into the template, tree and question machinery that exists.
Four reasons it is not merely possible but *better*:

1. **The prohibition is already built and already correct.** §15:519's table says No for client,
   patient, employee, candidate, student and unknown. P6 says the same thing today, on the key, for
   the same stated reason (`fields.py:558–567`), and C2 enforces it at composition
   (`routing.py:398`). A separate person module would be a second opinion about a rule that already
   has one home — the exact defect `placement/groups.py:24–28` declines to commit for `authored_by`.
2. **The permission is a narrowing of one existing refusal**, not a new capability. Nothing new
   decides where a file goes; one branch, under one confirmed answer, is allowed one level from a
   field the product otherwise refuses.
3. **The level itself already has a shape.** Contract W4.3/W5 defines a `template-local` level whose
   *"children are accepted group labels and existing folder names, which are not fact values"* and
   which carries no field (`src/tree_design/templates.py:549–596`). A dependant level is that, and
   `materialise.py:485` already builds a node from a level's `display_labels` without a field.
4. **The rename §15:536 promises is already built.** *"A user may later rename the displayed folder
   label without changing the underlying relationship record"* — that is `UserLevelEdit`
   (`src/tree_design/user_edits.py:71–92`), keyed on the vocabulary triple and deliberately carrying
   no `node_id` or `plan_version_id`. It works for this the day the level exists.

**The seam, in one sentence.** A confirmed relationship answer in a permitting category makes
`subject_of_record` resolvable as a template-local level for that one branch, and for no other
branch, schema, field or scope.

**What the corpus actually needs this for.** `68` F5: Tom's two report cards carry the same school
and the same term, anchor on `SPRING2026`, and become one group. `ap.academic.k12-schooling`
(`src/tree_design/library/applicabilities.json`) binds `holder_institution → school`,
`cycle_period → term`, `artifact_kind` — and there is no role for the child, correctly. *"The one
thing Tom would ask for first — a folder per child — is the one thing the engine cannot express."*

### C1 — The relationship categories, as a closed vocabulary

**Files:** `src/questions/vocabulary.py`, `tests/p15/test_p15_relationships.py` (new).

§15:519's table, as members that each carry whether they permit a person-shaped label and what the
default handling is. **The membership is an owner question (§6, Q1)** — this task writes the
structure and the six-or-eight names the table gives, and the approval is recorded at each member as
the project's rule requires.

- **Failing test:** `test_client_patient_employee_candidate_student_and_unknown_permit_no_label`
- **Negative twin:** `test_a_relationship_category_outside_the_closed_set_is_refused`

### C2 — The household question is raised by the person, never by the files

**Files:** `src/questions/triggers.py`, `src/cli.py`, `tests/p15/test_p15_relationships.py`.

A third question kind, and the only one whose trigger is **not** evidence. §15:496: *"Does anyone
else appear in your files?" should not be a general onboarding question*; §15:499 admits it *"only
within a deliberate protected-family, household, or similar user-created workflow, after the user
has chosen to design that kind of branch."* In today's product that gesture is a CLI flag
(`--household-area <label>`), which is **owner question Q4**. `evidence_refs` is the branch the
person named, not a file.

- **Failing test:** `test_the_household_question_is_raised_only_when_the_person_asks_for_the_area`
- **Negative twin:** `test_no_corpus_of_files_raises_the_household_question` — run the four `68`
  persona corpora through `_raise_blocked_questions` (`cli.py:1261`) and assert zero.

### C3 — The permitting consequence, and its read surface

**Files:** `src/questions/records.py`, `src/questions/store.py`, `tests/p15/test_p15_relationships.py`.

`QuestionOption.permits_person_label: str | None` — the relationship category, checked against C1's
set — and `permitted_person_label(conn, *, scope)`, the fourth sibling of `activated_schemas` and
`gated_template`, scoped and required to be, for §13:444's reason. A contextual question carrying it
is refused in `StructuralQuestion.__post_init__` alongside the two refusals already there
(`records.py:132–149`): a level that exists is folders that exist.

- **Failing test:** `test_a_dependant_answer_permits_a_person_label_in_that_branch_only`
- **Negative twin:** `test_a_client_answer_permits_no_label_in_any_scope`

### C4 — The level resolves only under a permitting answer

**Files:** `src/tree_design/routing.py`, `src/tree_design/pipeline.py`, `src/cli.py`,
`tests/p10/test_p10_person_level.py` (new).

`TreeDesignAuthorities` gains `person_label_permitted: Callable[[str], str | None]` — branch scope in,
category out — **injected with no default**, bound at the composition root from
`questions.store.permitted_person_label`. Where C2 rejects `subject_of_record` today
(`routing.py:398–403`), it now first asks the authority; absent, revoked, or a prohibited category
and the refusal stands exactly as it does now. **Whether this is the right shape, or whether the
level must instead be authored template-locally so C2 is never called at all, is owner question Q3** —
C2 is a REFUSE-class gate and its class was an owner ruling (`tree_design/vocabulary.py:185`).

- **Failing test:** `test_a_household_branch_gets_a_per_child_level_under_a_permitting_answer`
- **Negative twin:** `test_the_same_branch_without_the_answer_builds_exactly_the_tree_it_builds_today` —
  byte-identical against the `68` Tom fixture. If this test cannot be written the feature is not
  additive and the design is wrong.

### C5 — Review-only by default, and the rename that changes nothing underneath

**Files:** `src/tree_design/user_edits.py` (no change expected — this task proves it),
`tests/p10/test_p10_person_level.py`.

§15:521 makes a dependant area *"Review-only by default"*, which is `REVIEW_ONLY`
(`tree_design/vocabulary.py:70`) on the node. §15:536's rename is `UserLevelEdit`; this task asserts
the two halves rather than building anything, which is the honest outcome when a seam already exists.

- **Failing test:** `test_renaming_the_child_folder_leaves_the_relationship_answer_unchanged`
- **Negative twin:** `test_revoking_the_relationship_answer_removes_the_level_from_future_proposals_and_leaves_the_frozen_tree_alone`

### C6 — The name never leaves the machine

**Files:** `tests/p15/test_p15_relationships.py`, `tests/integration/`.

§15:534: names *"must not be sent to cloud models by default, used as global search expansion terms,
treated as evidence that an unrelated file concerns that person, or used to train a shared model."*
Four prohibitions, and P7/P8's egress guard is where the first is testable.

- **Failing test:** `test_a_relationship_name_never_appears_in_a_model_payload`
- **Negative twin:** `test_the_egress_guard_fires_when_a_name_is_put_in_a_payload` — a guard that
  cannot be made to fire is not a guard.

---

## 5. §16 — the profession and role matcher. **GATED. Do not start §5 without §6 Q2.**

Two documents govern this and they must be read together.

`66` §16:539 asks for a matcher: multiple roles with scope and period, four outcomes (§16:553), raw
wording stored, an explicit Other / Not listed / Skip path, and — §16:547 — *"'I'm a sound engineer'
must not silently activate an engineering or software-project schema merely because the words are
superficially similar."*

`62` §D records an owner ruling made 2026-08-29 that **overturns the matcher as a mechanism**:

> *"These should not just be directly matched — the LLM uses that information to judge. This cannot
> be rule based and that simplified in this sense."*

and closes with *"Fuller guidance is owed and was promised. Nothing here should be built until it
arrives."* `69` §4.3 repeats it as an open owner item.

**The split this plan takes.** The two documents disagree about the *proposal step* — how wording
becomes candidate schemas — and agree about everything on either side of it. So:

- **Buildable now** (they agree): the record, the four outcomes, multi-role, scope and period, raw
  wording, and the bound that a role never becomes a folder name or a filing permission (§16:557).
- **Not buildable** (they disagree, and the owner owes the ruling): anything that turns wording into
  a candidate schema — rule, model, or otherwise.

### D1 — The role declaration record

**Files:** `src/questions/roles.py` (new), `src/questions/schema.py`,
`tests/p15/test_p15_roles.py` (new).

Built on A3's `FREE_TEXT` answer, not beside it. A declaration is raw wording plus scope plus
optional period plus confirmation state. Several may be live at once — §16:543, *"The system must
support multiple roles, each with a scope and possibly a time period, rather than forcing one
permanent profession."*

- **Failing test:** `test_a_person_may_hold_a_student_role_and_a_teaching_role_at_once`
- **Negative twin:** `test_a_second_role_does_not_supersede_the_first` — supersession is P15's
  correction mechanism (`store.py:116`) and using it for a second simultaneous role would encode
  "one profession" in the storage layer.

### D2 — The four outcomes, closed

**Files:** `src/questions/vocabulary.py`, `tests/p15/test_p15_roles.py`.

§16:553: an exact confirmed schema activation; a confirmed multiple-role activation; an unmatched
answer preserved without activating a schema; a skipped answer leaving the decision unresolved.

- **Failing test:** `test_an_unmatched_declaration_is_stored_and_activates_no_schema`
- **Negative twin:** `test_a_declaration_may_not_be_stored_in_a_fifth_outcome`

### D3 — A confirmed role activates through the one activation surface

**Files:** `src/questions/roles.py`, `tests/p15/test_p15_roles.py`.

The activation goes through `activates_schema` and `activated_schemas` (`store.py:177`) — the
existing seam — so `store.py:181`'s promise stays true: *"a reader can see every schema the user
turned on and where it came from."* A second activation path would falsify that docstring.

- **Failing test:** `test_a_confirmed_role_activates_its_schema_through_activated_schemas`
- **Negative twin:** `test_a_role_declaration_never_becomes_a_folder_name_or_a_filing_permission` —
  §16:557 verbatim.

### D4 — The guard that holds the gate shut

**Files:** `tests/p15/test_p15_roles.py`.

- **Failing test:** `test_nothing_maps_free_text_to_a_schema_without_an_explicit_confirmation` — an
  executable statement of §16:547 and of `62` §D, which fails the day someone adds a mapping.

### B1/B2 — the situation, per branch (consequence 3, and §16's real consumption)

Listed here rather than in §3 because it is where §13's third consequence and §16 meet.

**B1 — the trigger.** Two applicability rows in one schema both fire on one branch's evidence — for
Priya, `academic.coursework` and `academic.teaching`, both carried by the shipped library
(`68` F6). `catalogue.rows_for_schema` (`src/tree_design/catalogue.py:47`) already returns them.
- **Failing test:** `test_two_situations_firing_on_one_branch_raise_one_question`
- **Negative twin:** `test_one_situation_is_not_an_ambiguity_and_asks_nothing` — the shape
  `triggers.py:74` and `:185` already use.

**B2 — the consequence and its consumer.** `QuestionOption.selects_situation`, read per branch, so
`run(..., situation=...)` (`cli.py:882`) stops being one value for a whole disk.
- **Failing test:** `test_a_confirmed_answer_selects_the_situation_for_that_branch_only`
- **Negative twin:** `test_an_unanswered_branch_keeps_the_run_situation_and_the_tree_is_unchanged` —
  asking must stay free, the property `store.py:205` states for the nesting question.

**B3 — `requires_review` is guarded, not built.**
- **Failing test:** `test_no_question_option_requires_review_while_nothing_reads_it` — it fails the
  day someone adds the field, and it is deleted in the same commit that adds P13's reader.

---

## 6. Owner questions — Joseph's, and this plan invents no answers

**Q1. The relationship-category vocabulary.** §15:519's table has seven rows, one of which
(*"Employee, candidate, or student"*) names three relationships in one cell and another
(*"Dependant or child whose records the user manages"*) two. Is that six members, eight, or ten? A
closed vocabulary gains a member only with approval recorded at the member, so the list cannot be
inferred from the table's formatting. **Blocks C1, and C2–C6 through it.**

**Q2. The role-declaration guidance, still owed.** `62` §D and `69` §4.3. Specifically: is the
declaration read by a model (§D says yes), what is it allowed to conclude, and how does the person
see what it concluded? **Blocks all of §5 beyond D1–D4's records and guards.**

**Q3. May a confirmed answer narrow C2 for one branch?** C2 is REFUSE-class and the classes were an
owner ruling (`tree_design/vocabulary.py:185`, *"a uniform warning makes privacy overridable by a
click"*). The alternative is to author the dependant level as template-local so C2 is never
consulted — no field, no relaxation, and the permission checked where the level's children are
resolved instead. Both honour §15; they differ in which existing guarantee absorbs the change.
**Blocks C4.**

**Q4. What counts as §15's "deliberate protected-family workflow" in a command-line product?**
§15:502's flow is a screen with two buttons. This plan proposes a flag. A flag is deliberate and
explicit; it is not obviously the same as a person choosing to design that kind of branch.
**Blocks C2.**

**Q5. Does an edited answer open a draft automatically?** §17:576 reads *"the product creates a
draft plan version"* — created without asking, or offered? The difference is whether a person who
corrects a typo in an answer finds a draft waiting. **Blocks A4.**

**Q6. How long is a revoked name kept?** §12:433 requires answers to remain editable and revocable
and the store keeps revoked rows deliberately (`vocabulary.py:44–48`, `store.py:134–150`); §15:533 says names are *"removable"*.
For a NAME specifically those pull against each other, and the answer decides whether revocation
deletes the wording or only stops it deciding. **Blocks C5's negative twin.**

**Q7. Does a new question KIND require approval the way a vocabulary member does?** A1 makes kinds
enumerable, which makes the question askable for the first time. §21:668's *"must not be introduced
as recurring engagement prompts"* suggests yes.

---

## 7. Count, order, and what this plan does not do

**Nineteen tasks.** A1–A6 (registry, 6) · B1–B3 (consequences 3 and 5, 3) · C1–C6 (§15, 6) ·
D1–D4 (§16's buildable half, 4).

**Order.** A1–A3 first: A2 and A3 are records that C1–C6 and D1–D4 both build on, and doing them
after would mean two migrations of the same table. Then B1–B3, which need nothing new. Then C1–C6,
**held on Q1, Q3 and Q4**. D1–D4 last and **held on Q2**. A4–A6 may run in parallel with B and C;
they touch `effects.py` and the CLI report and nothing else touches those.

**What this plan does not do.** It does not build the first-run experience — §14:461 says the
product *"supports local search and indexing immediately"*, and that is Find, which ships first
(`63` §2). It does not touch automatic filing, which `66` §22 puts last. It answers none of §6's
seven questions, and every task blocked by one says so at the task rather than in a footnote.

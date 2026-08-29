# 9. Designed and not built

Sections 1–8 describe a machine that exists: eleven parts, 5232 passing tests, a command that
runs over a folder on disk and prints a report. This section describes the other thing the repo
contains — a body of design, some of it canonical, some of it dated *after* the machine was
built, whose implementation is zero or nearly zero.

The distinction matters more than any other in this document. A reader who takes `planning/` as
a description of the product will conclude that the product finds files, files files, and asks
the user structural questions. It does none of those. A reader who takes `src/` as a description
of the product will conclude that the design does not exist. Both readings are wrong, and the
gap between them is the subject here.

**Rule followed throughout:** every claim that something is *not* built was verified by search
against the live tree, and the verification command is stated beside the claim. Every quotation
from `00`, `66`, `68`, `69` or either PLAN was grepped before it was quoted.

---

## 9.0 How the absences were verified

Six searches, run against the checkout at commit `dfdc015` (branch
`build/p6-p7-first-packages`), working tree clean except for `planning/70-mechanism/` and
`.superpowers/`:

| Question | Command | Result |
|---|---|---|
| Is there a search entry point? | `grep -rn "def search" src/` | no matches |
| Is there any query/find surface? | `grep -rln "def find(\|def query(\|def search_\|class Search\|SearchResult\|search_index" src/` | two files, both false positives — `src/facts/families.py:209`, `:262` and `src/facts/photo_event.py:191` are union-find `find` helpers with body `while parent[file_id] != file_id` |
| Does anything move, copy, rename or delete? | `grep -rn "shutil\.\|os\.rename\|os\.replace\|os\.remove\|os\.unlink\|Path\.rename\|\.unlink(\|rmtree\|copyfile\|copy2" src/` | **no matches** |
| Does anything write a file at all? | `grep -rn "open(.*['\"][wax]\|write_text\|write_bytes\|subprocess\|os\.system\|os\.symlink\|os\.link\|touch(" src/` | **no matches** |
| Does anything create a directory? | `grep -rn "mkdir\|makedirs" src/` | one hit, `src/database_agent/db.py:44` — `path.parent.mkdir(parents=True, exist_ok=True)`, creating the parent of the SQLite file |
| Do the P12/P13 packages exist? | `ls src/mutation src/review_surface` | `No such file or directory`, both |

Two further checks bear on Find and on onboarding specifically:

- **No function in `src/` accepts a user query string.** The two modules named `retrieval.py`
  take structured inputs, not text. `grouping/retrieval.py:361` is
  `retrieve_neighbors(conn, *, seed, limits, knowledge, embeddings_enabled)` — a seed is a fact
  or a user-designated file, not a phrase. `placement/retrieval.py:86` is
  `retrieve(conn, *, subject, plan_version, limits, facts, group_ids, curated_folder_labels,
  semantic_neighbours, …)` — it retrieves *destination nodes* for a file, the inverse of what a
  person searching wants. `placement/index.py:282` `reachable_entries` indexes tree nodes, not
  file content.
- **The CLI has no verb.** `pyproject.toml` has no `[project.scripts]`; `src/cli.py:988–1016`
  builds one `ArgumentParser` over a positional `directory` plus `--situation`, `--label`,
  `--user`, `--list-situations`. There is no `find`, no `search`, no `apply`, no `undo`, no
  `review` subcommand, because there is nothing for them to call.

---

## 9.1 `planning/66-FIND-FILE-AND-ONBOARDING.md` — canonical, supplied 2026-08-29, implemented nowhere

`66` is 736 lines. Its own header says `**Implementation:** No code written`, and that header is
still accurate. It arrived by commit `b57590d`, one commit before the P12/P13 plans. It is not a
proposal: `69-HANDOFF.md` puts it second in the authority order — *"`00-database-agent-product-design.md`
wins → `66` and the part SPECs → PLANs → live `src/`"* — and both new PLANs restate that, with P13's
version adding the reason: *"`66` is dated 2026-08-29 and the SPEC 2026-08-20."*

So `66` outranks the eleven SPECs the built machine was built from, and none of it is built. That
is the single largest fact in this section.

### 9.1.1 Find (§1–§6) — nothing

**§1, local read-only retrieval.** `66` requires that Find operate on the local index and that
the product *"does not send a user's query, filenames, paths, extracted text, OCR output,
embeddings, file facts, destination tree, or search-result set to a cloud model in order to
return ordinary search results."* It gives the reason as a threat model, not a preference: *"A
file search query can disclose as much as the file itself."*

There is no Find. `grep -rn "def search" src/` returns nothing; no module accepts a query
string; there is no CLI verb. The privacy property §1 protects is currently satisfied
vacuously — nothing leaks a query because nothing accepts one.

**§2, one retrieval model not two rankings.** The requirement is that Find reuse the existing
evidence and retrieval model and *"must not create a second, unrelated ranking system whose
results disagree with the model used for group retrieval or destination-node retrieval"*, and
that raw scores stay out of the primary result in favour of an explanation
(*"Matched in document text," "Part of accepted group: 2026 Job Search"*).

The two retrieval modules that would have to be reused answer different questions from the one
Find asks. `grouping/retrieval.py` finds *neighbouring files for a seed*; its own docstring says
its channels find candidates and *"none of them decides anything."* `placement/retrieval.py`
finds *candidate destination nodes for a file*. Neither ranks files against a phrase. A future
Find that honours §2 has to derive a third use from these two, and no design document says how.
This is not merely unbuilt; the reuse §2 mandates is undemonstrated.

**§3, the six location states.** §3 is the most specific thing in Part I. It gives a table of
six distinct result elements that *"must not be collapsed into one ambiguous list of paths"*:

| State | What `66` says it means |
|---|---|
| Current location | *"The actual path where the file exists now"* |
| Filed home | *"A user-approved physical destination in the active organization plan"* |
| Also related to | an accepted relationship *"that does not imply another physical copy"* |
| Shared-material relationship | *"used by several packets or branches under an approved shared-material policy"* |
| Historical location | *"A prior path recorded in provenance"* — details, not a current home |
| Possible placement | a candidate *"never presented as a home"* |

Nothing in `src/` distinguishes them. The nearest thing is the P13 PLAN's file-structure entry
`src/review_surface/locations.py   \`66\` §3's six-state result element` (P13 PLAN:98) — a
filename in a plan for a package that does not exist. Note the direction of the dependency: §3 is
a *Find* requirement, but the only code slotted to satisfy it lives in P13, the review surface.
Nothing owns it on the Find side.

**§4, protected material present-but-unopened, with a separate unlock.** Two states are
required: standard search shows a *"privacy-preserving indicator"*; unlocked protected search
*"requires explicit local re-authentication or an equivalent deliberate unlock action."* And five
absence states must never share one message — protected, unreadable, still indexing, unsupported
format, no strong match.

The privacy machinery for the first half is partly live: `src/privacy/display.py` publishes
`RedactionSettings`, `DISPLAY_FACETS`, `REDACTION_VALUES == ("shown", "redacted")` and
`ProtectedSummary(count, scope_total, class_breakdown)`, and `privacy.gate.Gate.summarize_protected`
exists. The **unlock** does not: `grep -rn "def undo\|def revoke" src/` returns
`privacy/policy.py`, `privacy/gate.py`, `privacy/revocation.py`, all of which concern *model
consent* revocation, not a local re-authentication gate over search results. There is no
authentication of any kind in `src/`.

The five distinct states are, again, a P13 filename: `src/review_surface/states.py   \`66\` §4's
five distinct absence states` (P13 PLAN:99). Unbuilt.

**§5, index completeness and no-result behaviour.** `66` gives a worked status block
(*"Searching 18,432 indexed files locally / 89 files are still processing / 14 protected items
are hidden in standard search / 27 unreadable or unsupported files are not text-searchable"*).
The counting machinery exists in fragments — `scan_agent.summary.scan_run_summary`,
`evidence_shape.runs.COMPLETENESS`, `database_agent.budget.all_ceilings` — and P13's Task 15
would assemble them into a `progress_line`. But that is the *review* progress line, not the
*search* status line, and §5's specific requirement (*"a no-result response should say…"*) has no
consumer at all, because there is no result set to be empty.

**§6, the first-run screen that asks nothing.** *"The first-run screen should offer local index
setup, not a profile interview."* There is no first-run screen. `src/cli.py:984` `main` parses
argv and runs the whole engine; the only interactive affordance in the repo is
`--list-situations`, which prints 208 situation ids.

**Verdict on Part I: no search capability exists anywhere in `src/`.** Verified by
`grep -rn "def search" src/` (empty), by inspecting the two `retrieval.py` signatures (neither
takes a query), and by reading the full argparse surface at `src/cli.py:988–1016` (no search
verb, no `[project.scripts]` entry point).

### 9.1.2 File (§7–§11) — nothing

**§8's nine policy dimensions.** `66` §8 gives a table binding all nine before a filing policy
may exist: source scope, destination scope, file eligibility, evidence standard, review cadence,
exclusions, collision policy, undo period, pause-and-revoke control. Its governing sentence is
*"A branch permission alone is not an automatic-filing policy"* — source scope is treated as
equal in weight to destination scope.

`grep -rin "filing_policy" src/` returns nothing. There is no policy record, no policy table, no
policy vocabulary. **Both new PLANs record this as a hole in their own coverage rather than
working around it.** P12's "not built" table lists *"a filing policy"* under ratified decision
**A7** (no invented authorities). P13's is blunter:

> A dry-run surface (`66` §9) — *"There is no filing-policy record in any part's Contract-out and
> no `src/` package for automatic filing… Task 11's `ActivityEntry` carries the gap explicitly.
> This is a real hole in P13's coverage of `66`, not an omission of convenience."*

**§9's dry run and progressive authorisation.** *"The first run of every filing policy is a dry
run."* The escalation ladder — narrow policy → dry preview → user review → approve → reviewable
plans → *"Only after repeated successful review may the user enable direct moves"* — has no
implementation and no record to hold the trust state that would gate it. `grep -rin "dry_run" src/`
returns nothing.

**§10's required declines with distinct language.** `66` enumerates roughly a dozen conditions
that must produce a decline, each with its own sentence (*"This file has two approved homes,"*
*"I could not read this file,"* *"This item is protected by your privacy policy,"* *"This file
changed after the preview,"* *"No approved destination fits"*). P13's "not built" table divides
these honestly: some map onto records that exist (`placement.vocabulary.ABSTENTION_REASONS`'
nine, the five staleness triggers P12 would publish), and *"the rest — 'This file has two
approved homes', 'No approved destination fits' — are **filing-policy refusals with no
producer**."*

**§11's 90-day conditional undo and stale plans.** *"The recommended default undo retention
period is 90 days"* with 30 / 90 / one year / until-cleared as alternatives; every move
*"remains conditionally undoable"* subject to five verification conditions; a plan whose inputs
changed *"becomes stale"* and must be refreshed rather than applied.

None of it exists. The undo journal is P12's Task 8 and Task 11; the retention period is P12's
Task 13.

**Verdict on Part II: nothing in `src/` moves, copies, renames or deletes a file.** Verified by
`grep -rn "shutil\.\|os\.rename\|os\.replace\|os\.remove\|os\.unlink\|Path\.rename\|\.unlink(\|
rmtree\|copyfile\|copy2" src/` → **no matches**, and by
`grep -rn "open(.*['\"][wax]\|write_text\|write_bytes\|subprocess\|os\.system\|os\.symlink\|os\.link" src/`
→ **no matches**. The only `mkdir` in the tree creates the parent directory of the SQLite
database (`src/database_agent/db.py:44`). The product is, at this commit, incapable of touching a
user's files, and every "materialise" in `src/tree_design/materialise.py` composes records, not
directories.

### 9.1.3 Onboarding (§12–§17) — one thing, and it is the storage half of one section

**§12, not a profile questionnaire.** *"Onboarding must therefore be redesigned as a
structural-question system embedded in the relevant product mechanisms. It is not a weekly
questionnaire, a generic profile, a growth loop, or a casual conversational feature."* The
mechanism must ask *"only when a specific decision is blocked."*

`grep -rin "onboarding\|questionnaire\|structural_question\|question_registry" src/` returns
nothing that is a mechanism. The hits are: `src/cli.py:182`, a comment quoting `63` §10's rule
(*"No onboarding answer could have…"*); library JSON rows about HR onboarding-offboarding as a
*domain*; and `applicabilities.json` ids. There is no question, no registry, no trigger, no
answer store.

**§13, structural versus contextual.** The table is a safety boundary, not a nicety. A
contextual answer *"must not… Create, remove, hide, or rename folders; gate placement; authorize
movement; change privacy state; or silently become a structural rule."* Since there are no
answers of either class, the boundary is unenforced but also unviolated — there is nothing to
enforce it against, and nothing in `src/` records an answer class.

**§14, ask only when needed.** The Columbia example (*"We found files connected to Columbia. /
Which describes your relationship to Columbia?"* with `I study there` / `I teach or work there` /
`Both` / `It is not about me` / `Skip for now`, and the closing line *"It will not create or move
folders by itself"*) is the design's model of a good question. Nothing asks it. `src/cli.py` is
explicitly a no-questions deployment: its `ask_or_abstain` seam is
`lambda node_ids: pv.ABSTAIN` (`src/cli.py:724`).

**§15, other people and person-shaped folders.** The permission table — person-shaped folders
permitted for self, for a *"dependant or child whose records the user manages"* (protected family
area, review-only by default), optional for a household member; **prohibited** for client,
patient, employee, candidate, student, and unknown — has no code. There is no relationship
category, no protected family area, no name store.

The engine has a *negative* alignment here that is real and worth stating: `people` is a declared
field with `destination_eligible=False`, so no person's name can currently become a folder level.
`68` F5 records the consequence honestly — Tom's two children's report cards form one group,
because *"no field names a person in a way a destination may use"* — and adds *"No code should
guess at it in the meantime, and none does."* That is correct behaviour and it is also the
absence of the feature.

**§16, the profession and role matcher.** `66` calls it *"an open design problem"* requiring a
dedicated subsystem, multi-role support, an unmatched state that stays unmatched (`66` §16 uses the
example verbatim: *I'm a sound engineer* *"must not silently activate an engineering or
software-project schema merely because the words are superficially similar"*), and four possible
outcomes. Nothing. `69` §4 item 3 lists *"The role-declaration guidance he still owes
(`66` §16). Nothing in §16 should be built until it arrives."*

**§17, re-running structural questions with a versioned draft plan — the one implemented thing.**
§17 requires that changing a structural answer *"creates a draft plan version"* showing a diff
across six dimensions, and that it *"must not silently rename folders, reclassify files, reveal
protected records, or move anything as a consequence of a changed answer."*

The **storage half** of that shipped in `dfdc015`, the tip commit:

- `src/tree_design/user_edits.py` (286 lines) stores a user's rename durably, keyed on
  `(uses_schema, role_ref, field_ref)` rather than on a node id or a template version. Its
  docstring argues the key choice at length: *"`node_id` fails. §8.8 mints a new one per plan
  version"*; *"`template_id@version` fails. It is the PACKAGING"*; the vocabulary triple *"stays
  true across a re-route, a re-version and an upgrade."* It publishes `UserLevelEdit`,
  `UnappliedUserEdit`, `user_level_edits`, `describe_applied_edits`,
  `OVERLAY_ACTIONS_WITH_A_WRITER`. Four of six dimension actions are refused by name at the
  writer, because *"A stored edit nothing can apply is a silent no-op that outlives every
  session."*
- A test pins the non-mutation property:
  `tests/p10/test_p10_user_edits.py:509`
  `test_an_edit_is_readable_as_the_users_own_assertion_before_any_plan_adopts_it`. Its two
  assertions are the edit's readability by vocabulary key, and, at lines 538–541:
  *"the approved structure did not move because the answer changed. The edit is stored; the
  frozen tree is untouched until something designs again and the user adopts what comes back"* —
  asserted as `frozen_tree(...) == before`.

The test's own docstring names what is missing: *"The presentation half — a draft the user adopts,
with a diff — is P13's and is not built."*

**So the exact answer to "which of §12–§17 has any code" is: §17's storage half, and only that.**
One module and one test. Everything else in Part III — the question registry, the ask-when-blocked
trigger, the structural/contextual split, the family workflow, the relationship categories, the
profession matcher, the draft-plan presentation — is unbuilt.

And even the built half is partial in a way the P13 plan quantifies: **three of `66` §17's six
diff dimensions have no producer anywhere** (P13 PLAN:7464). *"Which schemas become active or
inactive"* — none, because `UserLevelEdit.uses_schema` is *"a schema name on an edit, not a schema
activation delta."* *"Whether any protected area changes"* — none, because
`tree_design.freeze.represent_protected_areas` builds protected nodes and *"nothing diffs them
across versions."* *"Whether any filing policy is paused"* — none, same missing filing-policy
record as everywhere else. The plan carries all three as `None` with a note *"never faked and
never quietly dropped."*

### 9.1.4 §21's open design work and §22's release order

**§21** names five cross-cutting contracts that *"are not minor interface details"* and must be
designed before implementation: the **profession and role matcher**; the **structural-question
system** (*"a registry of questions, their trigger conditions, the decisions they unblock, allowed
answer types, data classifications, scopes, revocation behavior, plan-version effects"*);
**protected search** (unlock behaviour, re-authentication, search-history controls, shared-screen
behaviour, *"test cases for metadata leakage"*); **automatic filing** (policy schema, dry-run
contract, stale-plan detection, cloud-sync behaviour, conditional undo, *"an evaluation suite
built around harmful misfiling cases"*); and **multi-home organization** (the §3 six states).

Of those five, one has a written implementation plan (automatic filing's execution half, as P12),
none has code, and three have not been designed at all.

**§22's release order, reproduced:**

1. **Find first** — *"Find should ship first as a local, read-only capability,"* with local
   indexing, unprotected retrieval, current locations, accepted relationships, match explanations,
   index-status language and protected-presence indicators.
2. **Connect Find to the review surfaces** — *"to the existing evidence inspector, accepted groups,
   destination-tree canvas, and review surfaces so that users can move from 'I found this' to 'I
   understand why this is related' without any hidden state change."*
3. **The onboarding question registry** — *"The team should first define the structural-question
   registry and how each answer connects to a specific schema, template, privacy rule, or policy
   gate. Only then should product design implement the task-triggered interaction flows."*
4. **P12** — not named as "P12" in §22, but the mutation layer everything after Find depends on.
5. **Automatic filing last** — *"It should not be scheduled until P1–P11 are verified and the team
   can demonstrate that the product declines unsafe cases reliably."*

**Where the project actually stands against that order:** at step **zero**. `69-HANDOFF.md` §4
lists the next actions and its item 5 restates the sequence verbatim — *"Then `66` §22's sequence,
unchanged: **Find** (local, read-only) → connect Find to the review surfaces → the onboarding
question registry → P12 → automatic filing"* — and immediately adds:

> **Do not start P12 or P13 from their new PLANs yet.** They exist so that the work is ready when
> the sequence reaches it.

Three of `69` §4's four preceding items are decisions owed by Joseph, not work: the classifier
sizing question, confirmation of `66` §24's judgement repair, and the §16 role guidance. The
fourth is an unanswered scoping question about Find itself — *"What subset of P1–P11 does Find
actually need? Find needs the index, evidence, retrieval and privacy. It does not obviously need
frozen trees or placement, in which case it ships earlier than the full gate. Still open from `67`
§6."*

So the first item in the release order does not yet have an answer to *what it is built on*, let
alone a plan or code.

---

## 9.2 P12 and P13 — full plans, written 2026-08-29, no code

Commit `93b788d`, `docs(p12,p13): implementation plans for apply/undo and the review surface`.
Two PLAN documents of 8592 and 8607 lines. `ls src/mutation src/review_surface` →
`No such file or directory`, both.

### 9.2.1 P12 apply/undo — 14 tasks

**What it would build**, in its own words: *"a deterministic transaction layer over P1's file
record, verification points and event log. It resolves a P10 frozen-tree `node_id` to a filesystem
path, builds a §8.3 move plan, evaluates preconditions twice, applies one action at a time, and
appends a journal entry."* Twenty-one source modules under `src/mutation/`, six tables inside P1's
single database, append-only by SQL trigger.

**Move plans.** `src/mutation/plan.py` would build the §8.3 record and refuse to build one where
the design says so. Four of the ten refusal classes are evaluated at construction —
`node_not_in_frozen_tree`, `node_refuses_placement`, `node_path_collision`,
`cross_folder_not_permitted` — and `review_policy_unsatisfied` is *deliberately* excluded from
that set, because §8.3 requires the plan to be built so it can be shown to the user.

**The five staleness triggers** (P12 PLAN:631, `vocabulary.py`): `content_hash_differs`,
`source_path_changed`, `destination_changed`, `source_vanished`, `permission_lost`. Task 5's
done-means is that each *"is independently reproducible against a fixture and yields
`stale:<trigger>`, no mutation, an `external modification detection` event, and a refresh prompt —
never an automatic apply."* The plan draws one distinction worth flagging: an occupied destination
is a *collision*, not staleness; `destination_changed` means occupancy changed **between the two
checkpoints**, *"which is why `evaluate_preconditions` takes `occupant_at_prepare` from the V1
verdict rather than reading it off the plan."*

**The four collision behaviours** (P12 PLAN:668): `preserve_both_deterministic_suffix`,
`merge_only_if_hashes_identical`, `retain_newer_older_to_version_family_review`, `stop_and_ask` —
each with its own outcome constant, and no path that overwrites. The suffix *format* is
unspecified by the SPEC (flag F4) and is injected with no default.

**The four verification points** already exist in P1 and P12 would be their only caller:
`database_agent.verify.VerificationPoint` publishes V1 *"before preparing a filesystem action"*,
V2 *"immediately before executing a move or copy"*, V3 *"after completing the action"*, V4
*"cross-volume copy-and-delete destination confirmation"*. The plan documents two traps it found
by reading P1's source: `verify_content` hashes `files.current_path` rather than a path passed in,
so the correct order is *"move → `observe_path(destination)` → `verify_content(V3)`"*; and
`verify_content` swallows `OSError` and returns `"mismatch"`, so P12 must test existence and
readability *before* calling it or `source_vanished` and `permission_lost` *"can never fire and
both collapse into `content_hash_differs`."*

**The journal** (`src/mutation/journal.py`) is append-only; **conditional undo**
(`src/mutation/undo.py`) reverses or surfaces a conflict and touches nothing, with five undo
verdicts; `src/mutation/directories.py` reverses the directories one action created on the same
conditional terms; `src/mutation/retention.py` implements `66` §11's retention period. Task 13 is
the one task whose done-means are entirely `66`'s rather than the SPEC's.

**Seventeen conflicts are flagged and none resolved.** The rule is stated at the top: *"An
implementer who hits one should build what the task says and leave the flag standing."* F1 —
`root_anchor` *"has a consumer and no producer"*, nothing in `src/` maps a `root_anchor` string to
a filesystem path. F15 — §8.4's *"user policy that explicitly permits it"* has no producer, so
*"with none present, every protected file is refused."* F10 — `66` §8 puts the undo period inside
a filing policy, which is item 5 of §22's order, *after* P12, so *"P12 therefore owns a
corpus-wide retention setting that a later per-policy setting will have to reconcile with."*

### 9.2.2 P13 review/approval surface — 20 tasks

**What it would build:** twenty-four modules under `src/review_surface/`, and explicitly *not* a
GUI. *"There is no framework, no HTML, no TUI, no template engine and no rendering loop anywhere
in this plan. Every 'renders' in the SPEC becomes 'is reachable as a field on a frozen dataclass,
and a negative test proves the forbidden thing is not reachable.'"*

**Review items.** Task 5 builds the placement review item (*"trust is not uniform, and a deferral
is not an abstention"*), Task 6 the group-plan item carrying `66` §4's five absence states, Task 7
the residual screen with seven attributes where *"a missing one is a failure"*, Task 11 the apply
item, the five staleness triggers and the undo-conflict item.

**The one `review_action` record.** The SPEC publishes it at `SPEC:246-280`: `action_id`,
`surface` (eleven values), `subject_ref`, `plan_version`, `session_id`, `action` (seventeen
values), `bulk_member_refs[]`, `bulk_basis`, `correction_scope`, `routed_to[]`,
`presented_state_ref`, `user_id`, `acted_at`. *"Routing is the whole contract"* — P13 collects the
gesture and hands it to the owning part; placement and residual to P11, tree edits to P10, consent
and redaction to P7, refresh and apply approval to P12, group changes to P9, a reclassification to
P7 and P6, a reset to P1. *"An action may route to more than one part; it is still **one**
collected gesture."*

**The progress line.** Task 15: completed and deferred never merged, and no indexed file absent
from every entry, assembled from `scan_agent.summary`, `evidence_shape.runs` and
`database_agent.budget.all_ceilings`.

**The review approval.** Task 12 builds `ReviewApproval(approval_id, plan_id,
placement_decision_ref, plan_version, required_review_policy, verdict, …)` — *"§8.3's gate,
finally consumed."* P12's side of that seam is deliberately hollow: P12's "not built" table says
*"A `review_approvals` table — P13 owns the producer. P12 publishes the typed record and reads
through an injected callable, so no source module impersonates P13."*

**The plan-version diff.** Task 18 consumes `tree_design.diff.diff_versions`,
`tree_design.user_edits` and `placement.versions.reproject`, and covers three of `66` §17's six
dimensions with the other three carried as `None` (see 9.1.3).

**P13 flags six conflicts plus ten still-open SPEC questions.** The sharpest is the one that
cannot be resolved without Joseph: **B3 forbids P13 a path and §8.3 demands four** (P13 PLAN:4550).
The Explicitly-not-owned table says P13 *"shows a **node and its ancestor labels**, never a
resolved path"*, but the apply item requires all thirteen §8.3 precondition fields, two of which
are paths, and the undo-conflict item requires *"the original source path, destination path,
expected content hash and observed content hash."* The plan's resolution: *"P13 CARRIES paths that
P12 composed and P13 COMPOSES none"* — and it adds *"Under the second reading, Done-means 13 is
unsatisfiable as written."*

Also unresolved and consequential: `evidence_shape.runs.COMPLETENESS` has **nine** members live
and the SPEC lists **eight** — `dataless` is missing — so *"a file whose only run is `dataless`
therefore has no bucket, which the SPEC's own rule that 'no indexed file may be absent from every
entry' forbids."* The plan gives `dataless` its own entry rather than folding it in.

---

## 9.3 Two conflicts that are about the repo as it stands — both verified here

`69` §3a separates the plans' flags into *"an authority with no producer yet"* (which stay in the
plans) and *"claims about the repo as it stands today."* There are two of the second kind. I
verified both by reading the files.

### 9.3.1 Three incompatible `review_action` fixtures already exist, and only one matches the SPEC

Three test-only files publish a class named `ReviewActionFixture`, each shaped by the part that
expects to *receive* the action. All three exist and are shipped:

| File | Identity field | Timestamp | How the subject is named | Actions |
|---|---|---|---|---|
| `tests/p9/p13_fixtures.py:35-60` | **none** — the record has no id of its own | `decided_at` (:56) | `group_id` + `membership_id` (:52-53) | 7: `accept, edit, reject, defer, restore, reset-suggestion, exclude-from-packet` (:18-26) |
| `tests/p10/p13_fixtures.py:13-24` | `review_action_id` (:15) | `observed_at` (:23) | `subject_ref` (:17) | 6, by function: `accept, rename, ignore, restore_version, add-scoped-general, set-shared-material-policy` |
| `tests/p11/p13_fixtures.py:32-46` | `action_id` (:34) | `acted_at` (:45) | `subject_ref` + `session_id` (:36, :38) | 11, in `ACTIONS` (:25-29) |
| **P13 SPEC:246-280** | `action_id` | `acted_at` | `subject_ref` | **17** |

**Only `tests/p11` matches.** Its own docstring states the provenance: *"The field list is P13
SPEC:247-279 restricted to the four surfaces P13 routes to P11 (P13 SPEC:294)."*

The other two carry field names and action values the SPEC's record cannot supply. `edit`,
`restore`, `reset-suggestion`, `exclude-from-packet`, `rename`, `ignore`, `add-scoped-general`
and `set-shared-material-policy` are not among the SPEC's seventeen actions; `review_action_id`,
`plan_version_id`, `group_id`, `membership_id`, `basis`, `user_edited_label`, `decided_at` and
`observed_at` are not among its fields.

Three further wrinkles, all verified:

- **They differ in strictness, not only in shape.** `tests/p9` validates its action against
  `REVIEW_ACTIONS` and requires seven fields non-empty (`__post_init__`, :62-71). `tests/p11`
  validates surface, action and six required fields (:48-56). `tests/p10` has **no
  `__post_init__` at all** — it validates nothing.
- **Two of the three have live consumers in `src/`.** P13's plan records that
  `tree_design.store.apply_review_action` reads `.action` against `TREE_EDIT_ACTIONS` (fifteen
  values, none of them in the SPEC's list) and `grouping` reads `.basis`, `.group_id` and
  `.membership_id`. So these are not idle fixtures; source modules are written against two of
  these three vocabularies.
- **All three declare themselves stand-ins and forbid `src/` from importing them**, and each says
  a test enforces that. `tests/p9`'s docstring: *"No source stub impersonates P13 — a stub in
  `src/` would be P9 deciding what a user action looks like, which is P13's to say."*
  `tests/p11`'s: *"`src/placement/` may never import this module and a test asserts it does not."*

P13's plan refuses to fix it: *"Reconciling the four vocabularies is a decision for Joseph, not for
a plan author. Do not widen P13's `ACTIONS` to absorb P10's or P9's; do not narrow P10's or P9's;
do not write a translation table."* Task 9 ships a compatibility **report** — a test that prints
every field and action value P13 cannot supply and fails with that list — rather than a shim. The
plan names the defect class: *"Three parts each guessed at a record its owner had not published…
here it has produced three producers and no consumer."*

One incidental finding: `tests/p11/p13_fixtures.py:4` cites `database_agent/events.py:59-61` for
P13's registered event names. Those line numbers are still correct at this commit — `"review
presentation"`, `"review action routed"`, `"apply review approval"` are at exactly 59–61 — but the
P13 PLAN:48 warns *"the line numbers have moved — do not propagate the citation."* Either the plan
was written against a different checkout or it is defensively wrong; either way the citation is a
fragile one and the plan is right about the risk.

### 9.3.2 §8.2's event vocabulary has `failed move` and nothing for a refusal

Verified at `src/database_agent/events.py:30-37`. `RESERVED_EVENT_TYPES` is a frozenset of
nineteen names taken verbatim from `00`'s provenance sentence
(`planning/00-database-agent-product-design.md:136`), which lists *"…placement recommendation,
filename-collision resolution, planned move, executed move, failed move, external modification
detection, and undo."*

The six P12 would author are all present: `planned move`, `executed move`, `failed move`,
`filename-collision resolution`, `external modification detection`, `undo`. **There is no name
for an action that was refused, or paused, before it was attempted.**

Registration cannot supply one at run time. `events.py:39-41`: *"Registration is a spec-level act
(rule 4), so this table is compiled from the declaring SPECs and frozen at import. There is no
run-time registration call."* An import-time check at :82-84 raises `ImportError` if a registered
name shadows a reserved one.

P12's Done-means 13 requires that *"Every applied, refused, stale, paused, and undone action
appended its §8.2 events"* — five result kinds against six event names that cover four of them.
P12's plan resolves it under protest at PLAN:4260: it appends **`failed move`** for a refused or
paused attempt, carries the exact result string in the structured explanation, and states plainly
*"**A refusal is not a failure and calling it one is wrong.**"* The durable, correctly-named record
is P12's own `execution_records` row; the event is the trace. The code it plans to write carries
the note inline (PLAN:5053): `"note": "not a failure -- §8.2 has no refused/paused type (F13)"`.

`69` §3a states the ownership: *"Adding an event type is Joseph's, not a part's."*

The distinction being lost here is one the project already enforces elsewhere. `69` §3 records
fixing exactly this class of error at the report layer — *"The refusal blamed the step that
worked. Every file said 'nothing has been able to read enough of it' when `file_facts` held a
`direct` fact and `classifications` held nothing. Read, not classified."* The same conflation is
about to be written into the permanent, append-only event log.

---

## 9.4 The stand-ins that exist because the real thing does not

`src/cli.py` is 1078 lines and is not part of P1–P11. It is a composition root, and four of its
components are stand-ins for parts that were never built. Each one says so.

**1. `review_and_accept` (`src/cli.py:429`) stands in for P13's review screen.** Its docstring:
*"The review screen, non-interactively: keep everything, as one named group."* It supplies two
things the engine cannot produce for itself and which are *"both the user's"*: a **name** (because
`grouping/pipeline.py` writes `display_label=None` on every group and `tree_design.upstream`
refuses an unlabelled group) and a **category** (because `group_category` is `None` and an
accepted group with no category *"is eligible for no applicability row at all"*). `--label` and
`--situation` are those two answers.

The cost is that it merges. Lines 452-470 build one `Group` whose `group_id` is
`f"{PLAN_VERSION}:{label}"`, whose `anchor_facts` are every group's facts concatenated, and whose
`coherence_verdict` is hardcoded `COHERENT`; every membership is then carried onto that one id.
P10 receives exactly one accepted group. This is `68` F3, below.

**2. `AcceptedGroupEnumeration` (`src/cli.py:246`) stands in for an enumeration P9 never
published.** Its docstring: *"Three of its four methods delegate straight to P9. The fourth,
`accepted(plan_version_id)`, has NO live P9 implementation: P9 publishes `group_state_as_of` for
ONE group and nothing that enumerates the groups a plan version accepted (`src/tree_design/
upstream.py` records this as SPEC corrections row 17). P10 deliberately does not work around it,
because 'an enumeration P10 wrote itself would be P10 deciding which groups a plan version
contains.' So it is written HERE, by the composition root that created the acceptances in the
first place."* It runs a raw `SELECT` against `group_acceptance` (:265-288) — the composition root
reaching into P9's table because P9 published no reader.

**3. `residual_partition` (`src/cli.py:700`) stands in for §7.5's review-set taxonomy.** Its
docstring: *"§7.5's review sets. SPEC Open question 10 leaves the taxonomy open, so this deployment
surfaces ONE set holding everything §6 could not place — the smallest partition that still shows
every file with a reason."* It returns a single dict labelled `"Not yet placed"` with hardcoded
`file_type_distribution: ()`, `age_range: ()`, `evidence_availability: "partial"`,
`sensitivity_status: "none"`, `protected: False`. Five of the seven attributes P13's Task 7
requires are stubbed constants here.

**4. `ask_or_abstain` (`src/cli.py:724`) stands in for the multi-home question.** It is
`lambda node_ids: pv.ABSTAIN`, with the reason stated inline: *"§6.9, when a file has two homes.
This deployment abstains rather than asking, because there is no screen here to ask on and
choosing one institution is the failure §6.9 exists to prevent."* `66` §10 names the same case as
one requiring its own refusal sentence — *"This file has two approved homes"* — and there is no
screen to say it on.

Two more, for completeness. `RESIDUAL_LIBRARY` is `{}` (`src/cli.py:222`) — §7.3's nine residual
template names are all disabled, because enabling one would mean inventing its eight attribute
slots. And `DIRECT_SLOTS` (`src/cli.py:206`) contains exactly one slot,
`cli.text.identifier → subject`, which is `68` F2's finding: a litigator's case number, a
household's claim number and a passport number all become the academic field `subject`.

---

## 9.5 The three blockers a real person hits

`planning/68-PERSONA-RERUN.md` ran the shipped command over four corpora on disk — a litigator, a
PhD student who TAs, a two-child household, and one person who is all three — and recorded the
output. Its §2 table: 26 files, four corpora, **1 folder proposed each, 0 files ready to file
each**. Its §5 verdict: *"G10 does not close, and it should not be recorded as closing."*

**Blocker 1 — no classifier ships, so every file for every person stops unclassified (F1).**
26 of 26 files returned the same sentence:

> *"This file has not been classified — nothing has yet said what kind of material it is — so it
> was not shown to a model and nothing moved. It is waiting for you to say what it is, not marked
> sensitive and not judged on thin evidence."*

The database confirms which step stopped: `file_facts` holds a `direct` fact for every file and
`classifications` holds **zero rows** in all four databases. Reading worked; classification
declined *correctly*, because no detector is supplied and P7 refuses to default an absent
classification to a public class. `68` frames the cost rather than the mechanism: *"it is not one
persona's problem or an edge case, it is the terminal state of the product for **everyone**, and
no other improvement is visible to a user until it is decided."* `69` assigns it: **Joseph**,
`65` §2.2's sizing question, open by decision.

**Blocker 2 — the review merge means the tree is one folder (F3).** Described in 9.4 above as a
mechanism; `68` calls it *"the largest user-visible defect and it is a **deployment** defect, not
an engine one."* The engine's own records are better than the report:

| | groups P9 formed | what the person was shown |
|---|---|---|
| Priya | `PHYS1401` (2 files), `PHYS2801` (2) | one folder, `Coursework` |
| Mara | `CV20261234` (4), `X12345678` (1) | one folder, `Matters` |
| Tom | `SPRING2026` (2), `CLM88213` (1), `PR20264410` (1) | one folder, `Household` |
| multi-life | `CV20261234`, `PHYS1401`, `PHYS2801`, `SPRING2026` | one folder, `Coursework` |

Verified by experiment, not argument: patching the review to accept each group as itself gave
Priya `PHYS1401` and `PHYS2801` as two folders. The patch was reverted, and `68` explains why it
is not a proposed fix — *"it also **drops the branch name the user asked for** (`Coursework`
disappears entirely) and it is not this command's place to decide whether a person's two courses
are two top-level folders or two children of one. That decision is a review screen, and the review
screen is **P13**."*

**Blocker 3 — a client's passport number became a group label and would become a folder name
(F4).** Mara's corpus produced a group whose `display_label` is **`X12345678`** — a passport number
printed in a client identity document. Under the shipped merge it stays in the database; under the
per-group experiment, the run printed a proposed folder named `X12345678`.

`68`: *"Two gaps compound to produce it: nothing classified the file as protected (F1), and nothing
anywhere says that an identifier lifted from an identity document may not name a folder."* It cites
`66` §4's governing sentence — that on a shared screen *"even 'Identity documents' may reveal more
than the user wants"* — and `66` §15, which prohibits person-shaped folders for clients and patients
on exactly this reasoning. Its instruction: *"This must be closed before anything materialises a
folder from a group label. It is upstream of P12 (which composes paths) and belongs in P13's review
contract (which is where a label is approved)."*

Two further findings are recorded as design work already owed rather than implementation gaps.
**F5**: no field names the child, so Tom's two report cards are one group — `66` §15's territory,
and *"No code should guess at it in the meantime, and none does."* **F6**: `--situation` is one
value per run, so Priya's teaching material is labelled `academic.coursework` — `66` §13's
structural-versus-contextual question in its sharpest form.

`68` also records a withdrawn finding rather than deleting it: F7's two review blocks were first
reported as two placement passes and are actually `00` §8.6's review-batch ceiling
(`residual.max_files_per_review_batch` = 8; 13 unplaced files → 8 + 5). *"A re-run that silently
drops a claim it made is not a record anyone can check."*

---

## What looks wrong here

Flagged, not resolved.

1. **The canonical user-facing design outranks eleven SPECs that eleven built parts were built
   from.** `69`'s authority order puts `66` above the part SPECs, and `66` is nine days newer.
   Nobody has audited P1–P11 *against* `66`. The two new PLANs each found `66`-versus-SPEC
   conflicts in their own part within days of `66` landing (P12's F9 and F10, P13's four
   `66`-binding tasks and its B3 path conflict). There is no reason to expect the eight parts
   nobody re-read are clean.

2. **`66` §3's six location states are a Find requirement whose only planned implementation is in
   P13.** `src/review_surface/locations.py` sits in a plan for the review surface, which §22's
   release order puts *second*, behind Find. If Find ships first as §22 requires, either it ships
   without the six states — the thing §21 says *"Without this model, Find will either hide genuine
   organizational context or present a confusing list of paths that users cannot interpret"* — or
   the ordering is wrong.

3. **Find has a release position and no scope.** `69` §4 item 4 is still asking *"What subset of
   P1–P11 does Find actually need?"* Step 1 of the release order has no answer to what it is built
   on, no SPEC, and no plan, while steps 4 and 5 have 17,199 lines of plan between them. The work
   that exists is the work the sequence says to do last.

4. **`66` §2 mandates reusing "the same local evidence and retrieval model," and the two modules
   named `retrieval.py` answer different questions from the one Find asks.** `grouping/retrieval`
   finds neighbouring files for a seed; `placement/retrieval` finds destination nodes for a file.
   Neither ranks files against a phrase. The prohibition on a second ranking system is clear; the
   claim that the first one is reusable for search is unexamined.

5. **P12's plan will write `failed move` for a refusal, into an append-only log, while stating
   that doing so is wrong.** The event log is the one artefact that cannot be corrected later. The
   plan is right that minting a name is Joseph's call, and right that the `execution_records` row
   carries the truth — but the §8.2 trace is what §8.2 exists to be, and it will be permanently
   miscategorised for every refused action until a nineteenth name is added and old rows cannot be
   rewritten.

6. **Three fixtures, two live consumers, no producer.** `tree_design.store.apply_review_action`
   and `grouping` are written against two vocabularies that the SPEC's `review_action` does not
   contain. When P13 ships the real record, those two source modules break — and the P13 plan
   forbids itself from writing the translation table. Who fixes P9's and P10's consumers, and in
   which plan, is unassigned. `tests/p10/p13_fixtures.py` also validates nothing at all
   (no `__post_init__`), so P10's guesses are the least constrained of the three.

7. **P12 will own a corpus-wide undo retention setting that `66` §8 says belongs to a filing
   policy** (F10). Building the narrower thing's setting on the wider thing's schedule, four
   release steps early, is a reconciliation debt taken on deliberately.

8. **`66` §17's diff is half-built, and the built half is the half nobody sees.** The storage
   exists and is tested; the presentation is P13's. A user who edits a structural answer today
   gets a durable record and no diff, no draft plan, and no adoption gesture — the exact
   *"silently"* §17 prohibits, minus the silent mutation, which is prevented only because nothing
   mutates anything.

9. **Three of §17's six diff dimensions have no producer and two of the three are blocked on the
   same missing record** — the filing policy, which is also what `66` §9's dry run, `66` §10's
   distinct refusals, and P13's activity list are all blocked on. One unbuilt record is load-bearing
   for four separate design promises across three sections.

10. **`68` F4's passport-number folder is assigned to "P13 + P12," both unbuilt and both scheduled
    late.** It is the only finding in `68` with a disclosure consequence rather than a usability
    one, and nothing in the release order brings it forward. Meanwhile the label is already written
    to the database on every run of the shipped command; only the merge is hiding it, and `68` §6
    notes the merge *"is now hiding four correct, distinct, populated groups"* — the hiding is an
    accident of a stand-in, not a control.

11. **The security invariant is currently satisfied by absence, not by design.** Protected material
    is never opened because *nothing opens anything*: the tree contains no write, no move, and no
    file-create. Every guard described in sections 1–8 will face its first real test on the day
    `src/mutation/` exists. `grep` proving the absence today proves nothing about that day.

12. **`68` §5's honest verdict and `69` §1's scoreboard sit uneasily together.** Nine of ten gates
    green, and the tenth is *"whether a person can use it"* — which is the whole product. A reader
    who scans the gate table sees 90%; a reader who reads `68` sees four people, four disks, zero
    files filed. The scoreboard's shape invites the first reading.

# Context onboarding — design only

Date: 2026-09-30. Status: proposal. This change adds no code, no migration, and no new behaviour.

Base: `cursor/sorting-pipeline-29aa` at `48cc0ac2`. The founder's measured run is that build, on a copy of Downloads (1,833 files, macOS).

This document uses the writing-plans shape for the staged work in section (e). It does not implement that work.

## What was not verified

- The Downloads tree itself. No file-name list and no file contents were in this checkout. Every sample sentence in section (b) was written for this note. None of them is a file from that folder.
- The database from the macOS run. Which authored terms fired on the 736 / 237 / 170 / 18 / 11 files is not in the repo.
- Whether that run passed `--semantic-model`. Section (b) says what that flag can and cannot change.
- Which of the two gist printings was counted. `cli._print_gist` prints the rules' reading after the scan, and prints again at the end with the judge's names only when the two differ (`src/cli.py` around `_print_gist`). The words the founder reported are schema names either way (see (a)).
- Whether an edited structural answer now creates a draft plan version. `planning/75-PLAN-ONBOARDING.md` (2026-08-30) records that link as missing. This pass did not re-audit every later commit for it.
- A line-by-line audit of all ~9,600 authored terms. Counts and the sample match in (b) come from one read-only pass over `src/recognition/library/recognition.json`, using the same whole-word phrase rule as `Detector._terms_in` / `_tokens`. That pass did not call `Detector.explain`, so it did not apply the file-kind veto, the corroborating-identifier rule, or safety holds.
- `planning/investor-overview.md` has no proactive-agent design. Domain research notes mention deadlines inside particular document types. That is not a product agent.

## (a) How situations, recognition, questions, and onboarding work today

### Schemas and situations

The product recognises twenty-three schemas, closed in `src/facts/domains.py` `SCHEMA_IDS`. The first ten are the launch and safety set: `academic`, `college_applications`, `research`, `career`, `photos`, `code`, `finance`, `identity`, `medical`, `legal`. Thirteen professional schemas are appended, including `business_operations`, `clinical_practice`, `construction_property`, `creative`, `engineering`, `law_practice`.

`facts/domains.py` states the rule in its module docstring: activation adds; it never chooses. `active_domains` returns a set. No domain suppresses another.

Situations live under each schema in `src/recognition/library/recognition.json`. Academic has eleven, including `academic.coursework` ("Coursework (taking a course)") and `academic.teaching`. Business operations has twenty-two. Construction has twenty-two. Creative has thirty-two. Law practice has twenty-eight. Clinical practice has six. None of the twenty-three schemas has exactly one situation (`src/branch_situation.py` records that measurement).

The strings the founder saw are schema names, not situation names:

| Schema id | `name` in the library | Gloss stripped by `folder_name_for_schema` |
|---|---|---|
| `academic` | Academic | Academic |
| `business_operations` | Business operations (the organisation's own running record) | Business operations |
| `construction_property` | Construction, trades and property (the professional record of a site, a job and a building) | Construction, trades and property |
| `creative` | Creative and media practice (the making record of a work) | Creative and media practice |
| `clinical_practice` | Clinical practice (clinician side) | Clinical practice |
| `law_practice` | Law practice (practitioner side) | Law practice |

`branch_situation.folder_name_for_schema` strips a parenthetical gloss (`_GLOSS_OPENS = "("`). The gist does not. `cli._kind_words` returns `schema.name` whole, and `_print_gist` prints `kind.count` plus that name. A person reading `736 Business operations (the organisation's own running record)` will report "Business operations". "Academic" has no gloss, so it prints as Academic. Forty Academic against hundreds of professional schemas matches a gist of schema ids, not a count of the situation `academic.coursework`.

`the_gist` / `_the_kind_the_rules_read` (`src/cli.py`) count a `Recognition` only. An abstention's near-miss schema is not printed as a kind. Unnamed files are their own bucket.

Within a schema, `branch_situation` does not pick a situation alphabetically. One situation in the library means that one. Exactly one situation raised for the file means that one. Otherwise the result is `None` and the person is asked. `partition_by_branch` treats the top of the tree as a life, not a file kind.

### The term detector

`src/recognition/detector.py` `Detector.explain` is the recogniser the gist reads when no semantic model is composed in front of it.

It matches authored phrases as whole tokens. A shorter term inside a longer one still counts. Arity is a count of distinct terms per schema, not a weight. The module docstring says the detector holds no score and no threshold.

Decision, in order:

1. No term at all: abstain `no_evidence` (a text-less picture or recording can still be `photos`).
2. One term, or a tie at one term: abstain `no_corroboration`, unless exactly one of the tied leaders is in `settled_by_user`, or a single leader is seconded by a corroborating identifier that is not the same observation counted twice.
3. Two or more schemas tied at the best arity, and the file kind is plausible: abstain `ambiguous`. Nothing breaks that tie except the settled-by-user rule above, and that rule runs only among leaders.
4. One schema strictly ahead, file kind plausible, handling assigned: `Recognition`.

`settled_by_user` is injected from `questions.store.activated_schemas`. The detector comments state the limits: exactly one settled schema among the leaders; only among leaders; never from nothing. A confirmed schema cannot suppress a unique winner, and cannot label a file that never matched it.

Path observations are not evidence (`_matches` skips `locator == "path"`). Two words in a parent folder name must not activate a schema for every file inside it. The file's own name still counts.

### Semantic recognition

`src/recognition/semantic.py` runs only under `--semantic-model`. It calls the term detector first and returns that answer untouched when the rules recognised the file. A vector may fill an abstention. It may not replace a `Recognition`. So if the 736 business files were real recognitions, a semantic model does not explain them. It could only have added names where the rules abstained. This pass could not see whether the flag was on.

### Questions, roles, and what is already called onboarding

Questions are structural answers in `src/questions/`, stored and revoked, not a hidden prior.

Wired readers in `src/questions/store.py`:

- `activated_schemas` — corpus- or scope-wide schemas a confirmed answer turns on. `READING_KIND` and `ROLE_KIND` in `src/questions/registry.py` both write this field. The detector sees the set as `settled_by_user`.
- `gated_template` — nesting for one branch.
- `selected_situation` — one situation for one branch. Consumed from `src/cli.py` (`selected_situation` around the situation-already-settled path). This chooses among situations of a schema the file already sits in. It does not choose the schema.
- `chosen_destination` — a destination for one unreadable folder.

`src/questions/roles.py` `question_for_role_declaration` offers the whole closed schema list, unfiltered. The CLI flags are `--describe-role` and `--declare-role` (`src/cli.py`). Declaring a role activates a schema. It does not turn the others off. The prompt text says answering will not move, rename, or delete anything.

`planning/75-PLAN-ONBOARDING.md` describes the design intent: questions are derived from a blocked decision in a run, not asked up front. As of that plan, two of five consequences of `planning/66` §13 were wired (activate a schema, gate a template). The code has since grown a situation reader and a role reader. Both still add. Neither restricts the catalogue.

`planning/80-ROLE-MATCHER-RULING.md` (2026-08-31) is the binding ruling on how a person's description may be used:

- Option 2: a local model may propose a shortlist from a closed list; the person confirms. Option 1 (ask, no model) is the fallback when no local model is present. Option 5 (ask only when one decision is blocked) runs underneath.
- Option 3 is closed: do not send onboarding to the cloud by default. Revocation cannot retract what has left the device.
- Option 4 is closed: do not let a standing self-description shade every later judgement with no line from a misfile back to the sentence that caused it. The recorded failure is a whole disk filed as coursework because one role was applied as ambient gravity.
- A typed self-description is a user edit. `src/privacy/vocabulary.py` `ALWAYS_LOCAL` includes `user_edits`. The comment there says a self-description never leaves the device, and consent does not unlock it. An enforcement suspension dated 2026-08-31 is scoped to development on fixture corpora and is written to revert before anyone other than the repo owner uses it. A product used on the founder's Downloads does not get to rely on that suspension.

`planning/104-DIAGNOSIS-FINAL.md` puts onboarding, the role matcher, and automatic filing in Release 2. Release 1 is the engine. There is no first-run profile screen.

### Correction memory

`review_actions.correction_scope` (`src/review_surface/schema.py`, written from `src/tree_design/pipeline.py` and `src/review_surface/collect.py`) records how wide a review action applies (a node, a branch, a corpus). `src/recognition/` does not read `review_actions`. A correction does not become a prior on the next file's schema. There is no user-profile table.

### What the investor overview already promises

`planning/investor-overview.md`: the filesystem stays the system of record; a cloud model may not invent a destination the person has not approved; an unplaced file is a correct result when the match is weak; nothing moves until freeze and then apply. Launch domains named there are academic coursework, college applications, research, career, photos, and code. The thirteen professional schemas are not launch domains. They are still in `SCHEMA_IDS` and in the term index, so they compete on every file.

## (b) Why coursework was labelled as business, construction, creative, clinical, and law

### The mechanism

A file is labelled with a professional schema when that schema has strictly more distinct authored terms than any other schema, at least two, on observations that are not the absolute path.

Academic's compiled list is small: 124 context terms and 124 work-type terms. The professional lists are much larger:

| Schema | Context terms | Work-type terms |
|---|---:|---:|
| academic | 124 | 124 |
| business_operations | 541 | 277 |
| construction_property | 687 | 335 |
| creative | 397 | 430 |
| clinical_practice | 126 | 85 |
| law_practice | 754 | 389 |

Overlap with academic on short phrases (three tokens or fewer) is thin: business shares 7 terms in total (among them `assignment`); construction shares 4 (`attendance`, `completion certificate`, `progress report`, `section`); creative shares 2; clinical shares 3; law shares 4. Academic uniquely authors `homework`, `lecture`, `notes`, `problem set`, `syllabus`, `exam`, `quiz`, `project`, `lab report`, `worksheet`. Those words are not why business wins. Business wins when the body contains two or more phrases the professional catalogue authored, and those outnumber the academic phrases.

The professional catalogues include ordinary words. Confirmed by the phrase index, not by a guess: `law_practice` authors `before`, `given`, `volume`, and `assumptions`. `business_operations` authors `assumptions`, `plan`, `minutes`, `policy`. `clinical_practice` authors the one-token term `practice`. `creative` authors `brief`, `export`, `layout`, `render`.

A read-only replay of the phrase index on made-up text (not the founder's files):

- `Lecture 12 Distillation Notes.pptx` — academic 2 (`lecture`, `notes`). That file would be Academic. A filename that already says lecture and notes is the easy case, and it is not the case that produced 736 business files.
- `Thermo Practice Set 3.pdf` with no body — clinical 1 (`practice`) only. Arity 1 abstains. It is not, by itself, Construction. The founder's example of a thermodynamics practice set labelled Construction therefore depends on words inside the file, or on a second construction term this filename does not contain. This pass cannot see those words.
- A short thermodynamics-style paragraph ("Practice Problem Set", piston-cylinder, pressure, temperature, "Assumptions", "Control volume", "due date") — law_practice 4 (`assumptions`, `before`, `given`, `volume`), business_operations 3, construction_property 2, academic 1 (`problem set`). Unique leader: law practice. That is the failure mode: common words authored as professional terms outvote the one real coursework phrase.
- A lecture-notes paragraph that also says "action items", "agenda", and "assumptions" — academic and business tied at 3. That tie abstains. It does not become Business operations unless business picks up one more term, or the person has settled business and not academic.

`planning/domains/nodes/business_operations.json` already says the central judgement is purpose, not topic, and that a course case study or textbook exercise must be separated from a real operating record, with abstention when the evidence does not settle it. The term detector does not implement that distinction. It counts phrases.

The project-root refusal is a separate bug and happens earlier. See (d). Until it is fixed, a top-level `requirements.txt` means the detector never sees the 1,833 files.

### Would a context step fix it?

A context step that only does what the code does today would not.

Today's use of "who the user is" is `activated_schemas` → `settled_by_user`. That fires only when the file's own terms already tied that schema with others. It cannot:

- remove law_practice when law_practice is the unique leader at 4 and academic is at 1;
- put academic onto a file that matched no academic term;
- stop a scan-root `requirements.txt` from refusing the walk;
- create a course fact, a term folder, or a work-type leaf.

A bias or a weight would also not fix the unique-wrong-winner case. Four law terms still beat one academic term if both schemas are allowed to win. `planning/80` forbids that kind of ambient weight anyway: a sentence about the person must not quietly shade every judgement with no attribution.

What would change the 736 / 237 / 170 / 18 / 11 counts is a gate, not a bias: schemas the person has not declared cannot be the winner. On the sample paragraph, if law, business, construction, and clinical are not declared lives, those leaders are dropped. Academic remains at one term and the file abstains, unless a corroborating course code seconds it. Unplaced is the correct result. Wrong is not.

That gate is still not sufficient on its own:

- If "I am a ChemE student" is mapped onto `engineering` or `construction_property`, the same count starts again inside the allow-list. A major is not a filing life. The lives that match this folder are coursework, recruiting and applications, named projects, design work the person claims, and leave-alone. Engineering-as-a-schema is how a thermodynamics set becomes a professional record.
- If the person does declare business or creative, a file that uniquely matches that schema still goes there. Design exports that say `export` and `layout` become creative on purpose only when creative was declared. A Power BI file with no authored term stays unnamed (`Sales Dashboard Power BI.pbix` matched nothing in the replay).
- Declaring academic does not invent `CHEN 3120` as a subject fact, and does not stop a one-file work-type leaf from folding into the course. Those are tree and fact bugs, already partly addressed on the PR-1 branch for calendar-year subjects and for folding a course away. They are not this design.
- The gate does not read file contents the person has not already extracted. It only stops undeclared schemas from winning on terms that were extracted.

Honest summary: context fixes this mislabelling only as a closed allow-list that can force abstention. It does not fix it as a questionnaire that activates the user's schemas on top of the full catalogue. Activation-adds is the current rule, and it is the wrong direction for this folder.

## (c) The user-context profile, and where it gates

### What it is

One record per corpus, attributable, editable, revocable. It is a structural answer, the same class as `src/questions/`, not a new hidden table and not a weight inside `Detector`.

It answers "what is this folder for?", not "what is this person in the abstract?". `planning/80` uses the case of someone who is both a teacher and a student: knowing both roles does not say which PDF is which. The profile narrows the catalogue. A blocked file still gets Option 5, a question about that file or that branch.

### Fields

All ids are from `SCHEMA_IDS` or from situation ids in the shipped library. Free text never becomes a folder name by itself.

| Field | Shape | Example for this founder | Used for |
|---|---|---|---|
| `lives` | Confirmed subset of schema ids. Empty is not "all schemas". | `academic`, `career`, `college_applications` | The allow-list the detector may win with |
| `situations` | Optional, per declared schema, situation ids | `academic.coursework` rather than `academic.teaching` | Branch situation when the schema has already won; does not nominate a schema |
| `school` | Short local string | Columbia | Display and later deadline context. Not a term that scores every file |
| `courses` | Confirmed list of code, name, term | Courses the person confirms, not a list invented here | Corroborating identifiers and folder labels already in the fact rules. Not a new gazetteer in the detector |
| `projects` | Folder names treated as one unit | `treehacks2026-main` | Leave the subtree as a unit; do not file each source file |
| `leave_alone` | Folder names or top-level names the person marked | LinkedIn export, anything they point at | Excluded from placement proposals |
| `raw_wording` | The sentence they typed, if any | "Columbia ChemE junior, AI minor, recruiting" | Stored as `user_edits`. Not parsed into schemas by a cloud model. A local shortlist may read it only to propose options the person then confirms |
| `not_lives` | Explicit refusals | business, construction, clinical, law, engineering-as-a-profession | So "ChemE" cannot be read later as `construction_property` |

`career` and `college_applications` are the existing schemas for recruiting and applications. This design does not add a schema.

Unknown and leave-alone are outcomes, not failures. A file that matches no declared life abstains. The reason should be a new abstention distinct from `no_evidence`, so a later screen can say "none of the lives you named" rather than "no words".

### How it is collected

A few questions at the start of a run on a folder that has no confirmed profile. Skipping is recorded and leaves today's detector unchanged, so local-only and "just scan" still work. A skip is not a declaration of academic.

Proposed questions, in order, each with a closed list plus "none of these":

1. What should this folder be sorted into? Options drawn from the launch schemas in the investor overview (coursework, applications, research, career, photos, code) plus "something else" which then shows the rest of `SCHEMA_IDS`. Default highlight for a student is coursework, applications, career. Nothing is pre-confirmed.
2. Are you taking courses, teaching them, or both? This sets `academic.coursework` and/or `academic.teaching` only if academic was declared. It is the per-branch question `planning/80` already requires, asked once up front for the corpus and overridable per branch later.
3. Name the school and the courses if you want course folders. Optional. The person can leave this blank; files can still land on Academic and abstain at the course leaf.
4. What should be left alone? Optional. Projects and exports.

Optional read-only quick scan, off unless they ask: list directory names under the scan root, no file bytes. Propose folders that look like course codes or like the named repo, as a shortlist. The person confirms or deletes each line. Directory names are paths. They stay on device (`ALWAYS_LOCAL` includes `paths`). This scan does not call the term detector and does not classify files.

No cloud call in this step. If a local model is present it may only propose from the closed list (ruling 80, option 2). If it is absent, the questions above are the whole mechanism (option 1).

### Where it is stored and how it is edited

Store it as structural questions at corpus scope, beside `ROLE_KIND`, with a new consequence. Do not reuse `activates_schema`.

`activates_schema` means "this schema may break a tie". The new reader, proposed name `declared_lives`, means "only these schemas may win". One field cannot mean both, or a role declaration would silently become an allow-list and an allow-list would silently become a tie-break.

Revocation uses the existing answer states: confirmed, skip, not-about-me, revoke (`questions.store` already treats only confirmed answers as binding). Editing replaces the answer under the same question id. The raw sentence stays a `user_edits` item.

The profile is shown back in the words the person confirmed, with the schema id available but not used as the folder name.

### Where it gates the recogniser

One place: `Detector.explain`, after `by_schema` is built and before a unique leader becomes a `Recognition`.

When `declared_lives` is present and non-empty:

- Drop any schema not in the set from the leader calculation. Do not drop them from the citation. The abstention or the recognition should still be able to say which undeclared schema would have won, so a misfile can be traced to the sentence (the requirement option 4 failed).
- If no declared schema remains, abstain. Do not fall through to the catalogue winner.
- If the best remaining declared schema has arity 1, keep `never_alone`. A declared life is not a second signal. The existing corroborating-identifier path may still second that one term. A course code the person confirmed is a valid corroborator for `academic` only, not for every declared schema.
- `settled_by_user` stays a tie-break among leaders that survived the gate. It does not add schemas.
- Safety schemas (`finance`, `identity`, `medical`, `legal`) are not filing lives. A hold still happens when the term detector's safety path says so. The allow-list must not be a way to switch holds off, and must not be required before a hold. This matches the product rule that cloud AI and any later agent cannot bypass a sensitive-file hold.

When `declared_lives` is absent (skipped onboarding, or an old database), `explain` is unchanged.

`branch_situation` and `selected_situation` stay as they are for the situation inside a schema that won. The profile's `situations` field is a default for that choice, overridable per branch, and never a reason to force a schema.

Cloud classification, if a later stage calls a model, receives only schemas and situations that survived this gate, inside the frozen tree. It does not receive `raw_wording`. It does not receive permission to invent a folder.

## (d) Software project folders inside Downloads

### What the code does

`planning/00-database-agent-product-design.md` says the engine should reject descendants of software project roots indicated by files such as `package.json`, `requirements.txt`, `Cargo.toml`, or `go.mod`, so a dependency tree is not proposed as a personal destination.

`src/scan_agent/exclusion.py`:

- `PROJECT_ROOT_MARKERS` is that list plus `library.properties`, `pyproject.toml`, `setup.py`, and `CMakeLists.txt`, each added from measured trees on a disk, not from a guess.
- `project_root_markers_in` returns markers that are files in one directory. A non-empty result means that directory is a project root. SPEC Q9 is open in the docstring: the design says "descendants", and the code does not decide whether the marker-bearing directory itself is excluded.
- `exclusion_for` returns `software project root descendant` for every entry whose parent marker tuple is non-empty, file or directory.

`src/scan_agent/traversal.py` `_walk_root` lists a directory, computes that directory's markers, and passes them into `exclusion_for` for every child. A child with a verdict is not enqueued and not read.

So a `requirements.txt` sitting in Downloads marks Downloads. Every child of Downloads is a descendant. Nothing is read. Deleting the file clears the marker. That matches the founder's report exactly. The marker file itself is also a child, so it is excluded as a descendant of the directory that contains it.

Nested projects are the case the rule was written for. `tests/p3/test_p3_composition.py` describes `myproject/package.json` and `myproject/index.js` set aside while a sibling folder of personal files remains. That behaviour should stay.

Literal directory names (`node_modules`, `.git`, `venv`, …) and category members (`.venv`, `.next`, …) are a separate rule. They do not depend on a marker in the parent.

### Proposed rule

Do not treat the scan root as a project root merely because a marker file is one of its direct children.

- Children of the scan root are walked even if the scan root contains `requirements.txt`.
- A nested directory that contains a marker still excludes its descendants. `Downloads/treehacks2026-main/src/main.py` stays unread if `treehacks2026-main` contains a marker. `Downloads/some-course/homework.pdf` is read.
- The stray `requirements.txt` in Downloads is an ordinary file (Q9 already refuses to exclude the marker directory itself; this proposal also refuses to exclude the scan root's other children).
- Dependency directory names stay excluded wherever they sit.

Pointing the tool at a repository root would then read that repo's source files, because the root is the scan root. Dependency directories would still be skipped. The owner approved this narrowing of §1.1 on 2026-09-30. The rule is the scan-root exception plus unchanged nested roots, not a longer marker list. The approval is also recorded on the exclusion paragraph in `planning/00-database-agent-product-design.md`.

A nested project directory should be one unit on the plan ("this looks like a software project; leave it together"), not a set of source files and not a silent disappearance. `tests/p3/test_p3_composition.py` already records that set-aside paths for this rule do not reach the screen the person reads (`cli` prints protected containers only). Telling the person the repo was left aside is part of this stage, using the existing exclusion verdicts, not a new exclusion.

`projects` in the profile can name `treehacks2026-main` even before the marker rule is right, but the profile cannot fix a walk that never enqueues the siblings. Stage 1 below is independent of the profile and should land first.

## (e) Staged implementation

No stage starts from this document. Thresholds in the evaluation section are proposals for the founder to accept or replace. They are not the investor-overview bar (30 of 41 exact, 0 wrong on the pinned corpus), which measures a different folder and stays in force for that corpus.

### Stage 1 — scan root is not a project root

Touch:

- `src/scan_agent/traversal.py` — when listing the scan root, pass an empty marker tuple into `exclusion_for` for its children. Still record the markers on the `ObservedDirectory` so the report can say they were seen.
- `src/scan_agent/exclusion.py` — docstring on SPEC Q9 updated to the ruling, once there is a ruling. No new marker names.
- `src/cli.py` — the set-aside report already specified by `tests/p3/test_p3_composition.py`, if that hunk is still unprinted: say that a nested project was left unread, by path and rule.

Tests:

- Extend `tests/p3/test_p3_traversal.py` or `tests/p3/test_p3_exclusion.py`: a root containing `requirements.txt`, `notes.pdf`, and `course/homework.pdf` observes both pdfs.
- The same root containing `treehacks2026-main/requirements.txt` and `treehacks2026-main/src/main.py` still yields `software project root descendant` for `main.py`, and still observes `notes.pdf`.
- Existing nested-project expectations in `tests/p3/test_p3_composition.py` stay. Do not weaken `node_modules` or `.venv`.

Done when those tests pass and a fixture shaped like Downloads is no longer an empty scan.

### Stage 2 — profile record, no effect on recognition

Touch:

- `src/questions/records.py` — a new option field, proposed `declares_life`, distinct from `activates_schema` and `selects_situation`.
- `src/questions/registry.py` — a new kind, corpus scope, reader `declared_lives`.
- `src/questions/store.py` — `declared_lives(conn) -> frozenset[str]`, confirmed answers only.
- `src/cli.py` — a way to answer and revoke it without a cloud call. Reuse `--answer` / the role flags' pattern rather than a second store.
- `src/privacy/vocabulary.py` — no new `ALWAYS_LOCAL` member. The sentence is already `user_edits`.

Tests in `tests/p15/`: a confirmed life is returned; a skip, a revoke, and "not about me" return an empty set; the set is not visible to `activated_schemas`; raw wording is not required for the closed-list answer.

Done when recognition output is byte-identical with and without a stored profile, because nothing reads it yet.

### Stage 3 — the gate

Touch:

- `src/recognition/detector.py` `explain` — the drop-undeclared-schemas step in section (c). New abstention reason in `src/recognition/vocabulary.py` if the reason vocabulary is closed (it is checked by `check_abstention_reason`).
- `src/cli.py` — pass `declared_lives` in beside `settled_by_user`. Do not overload `settled_by_user`.
- Gist copy: unnamed-because-not-your-life is still the unnamed bucket or its own line, and it is not counted as a professional schema.

Tests, new file `tests/recognition/test_declared_lives_gate.py`, using the shipped library rather than a private term list:

- With no declaration, a text that uniquely matches a professional schema still recognises as today.
- With `declared_lives={academic}`, that same text abstains, and the abstention cites the professional schema that would have won.
- With academic and career declared, a resume-shaped text can still be career, and a lecture-and-notes filename can still be academic.
- A declaration of academic does not label a file that matched no academic term.
- A tie between two declared schemas still abstains unless `settled_by_user` names exactly one of them.
- Safety hold tests in `tests/recognition/` stay green: an identity document is still held if its terms say so, even when identity is not a declared life.

Done when those tests pass. Not done when a Downloads run "looks better" without this fixture.

### Stage 4 — the questions and the optional folder-name scan

Touch:

- `src/questions/triggers.py` or a sibling module — the four questions in section (c), asked when `declared_lives` is empty and the person has not skipped.
- A small read-only directory listing, names only, proposing candidates. Person confirms. No extractor, no detector.
- Local model, if used, proposes only ids from `SCHEMA_IDS` and the library's situation ids. Absent model: the questions alone.

Tests: declining the scan classifies nothing extra; a proposed folder the person deletes is not stored; a confirmed course code is a course entry, not a schema activation.

### Stage 5 — evaluation set from file names

The founder supplies a list of relative paths. This repo must not gain file contents. Do not invent the 1,833 names in the test file.

Label file, one row per path, columns:

- `relative_path`
- `expected` — `place`, `unplaced`, or `leave_alone`
- `expected_schema` — a `SCHEMA_IDS` value, or empty when `expected` is not `place`
- `expected_situation` — optional
- `forbidden_schemas` — schemas that count as wrong if they win, even when `expected` is `unplaced`

Metrics, computed separately:

- `wrong` — placed, and the schema is not `expected_schema`, or the schema is forbidden, or a `leave_alone` path was placed or had its descendants read when it was a declared project unit
- `unplaced` — `expected=place` and the run abstained or made no decision
- `correct_place`
- `correct_left` — `unplaced` or `leave_alone`, and the run did not place it

Do not add `wrong` and `unplaced` into one error rate. Unplaced on a weak name is a success when `expected` is `unplaced`. Unplaced on a file labelled `place` is a miss, reported on its own line.

Two layers, because names cannot reproduce section (b):

1. Name-only, in CI, once the list exists. Asserts the scan-root marker does not zero the walk, `treehacks2026-main` is one left-alone unit, and filenames that are only a name (no body in the fixture) follow the phrase index. A fixture file may be empty bytes with a real name. That will not show law_practice beating academic on the word "volume".
2. Founder-run, on their machine, contents never committed. Join their label file to the run's schema per path. The detector already cites terms on a recognition; a sample of citations for files counted `wrong` is the debug path `planning/80` requires. The report is counts of `wrong` and `unplaced` side by side.

Proposed continue / kill lines, not rulings:

- Continue past stage 1 only if the Downloads-shaped fixture observes sibling coursework and still excludes a nested repo's descendants.
- Continue past stage 3 only if, on the founder-run layer, `wrong` among rows labelled coursework is under 10 percent of those rows. `unplaced` may rise. That rise is not a kill.
- Kill the claim that the profile fixed sorting if, after a confirmed allow-list that does not include business, construction, creative, clinical, or law, `wrong` on coursework rows is still above 25 percent. That result means the gate is not what the run is using, or declared lives still include the winning schema. Stop and report the cited terms. Do not add weights.
- Do not ship a threshold that treats unplaced as wrong. That is the incentive that filled Business operations.

### Stage 6 — not in the first implementation

The proactive agent in section (f). No code until stages 1–3 are measured.

## (f) The same profile as the base for a later agent

There is no agent module in `src/` and no agent design in `planning/investor-overview.md`. The overview already fixes the bounds: the model may not invent a destination; nothing moves until the person freezes and applies; sensitive material is held before a cloud call. `planning/104` calls automatic filing Release 2.

The profile is the closed world the agent is allowed to talk about. Correction memory becomes useful here only once a correction is stored as a scoped structural answer ("this file is coursework"), revocable, and readable by the agent as an attribution. Today's `correction_scope` is the width of a review action. It is not that memory. Do not train a weight from it.

Autonomy ladder, each step a strict subset of the next:

1. Suggest. A sentence on screen. No file write, no database plan. Examples: a declared course has a date fact and the packet looks short; two filenames look like versions of one declared project; a new file in Downloads matches a declared life by the gated recogniser. If it matches no declared life, the suggestion is to leave it, or to ask, not to pick a catalogue schema.
2. Prepare. A preview the person can read: a proposed grouping, a draft packet list, a proposed destination that already exists in the frozen tree. This uses the existing freeze / preview path. It does not call apply.
3. Act with approval. The existing apply, one explicit gesture, then undo. Still only into the frozen tree.

Never a fourth step that moves files because the profile was confident.

Cloud calls inside the agent stay inside the ratified prompt and privacy gate. They do not see `raw_wording`. They do not clear a hold. They do not name a folder that is not in the frozen tree. Local-only means stages 1 and 2 still run from dates and facts already on disk when no model is configured.

Deadline-aware packet readiness is a suggest/prepare behaviour over facts the extractor already stored (a date, a course the person confirmed), not a new reason to classify a file as business because the document says "due".

## (g) Risks and open questions

- Mapping the major onto a professional schema recreates the bug inside the allow-list. The open question for the founder: confirm the filing lives (coursework, recruiting, applications, named projects, design if wanted, leave-alone) and explicitly refuse construction, clinical, law, and business for this folder even where a ChemE document uses those words.
- Power BI files and the LinkedIn export have no honest schema in the launch set unless the person declares one. The proposal is leave-alone or unplaced until they say otherwise. Which they want is unanswered.
- SPEC Q9 and §1.1's literal sentence both treat a directory that contains `requirements.txt` as a project root. The scan-root exception is a narrowing of that sentence. It should be an owner ruling before stage 1 is coded. Scanning a repo as the root would start reading source files.
- A confirmed allow-list that includes creative will label design exports as creative. That is correct only if they declared it.
- The gate cites the schema that would have won. That citation must not be printed as the gist kind, or the 736 line comes back as a "near miss" the screen still treats as a label.
- Skipping onboarding leaves the current catalogue, so the bad labels remain for anyone who skips. The product should say that in the skip line. Forcing abstention on skip would make local-only look broken.
- Name-only evaluation cannot see the body-term failure. A green name-only suite is not evidence the 736 are fixed.
- Course list in the profile can become a private gazetteer if later code matches those strings as terms on every file. The proposal is corroboration for `academic` only, after a term already matched.
- `planning/75`'s missing link from an edited answer to a draft plan diff was not re-verified. If it is still missing, changing lives will change the next run with no diff. Stage 2 should not claim a diff it does not write.
- Ruling 80's enforcement suspension for self-description must not be the privacy story for this product. The classification (`user_edits`, always local) stands.
- This note did not re-run the 1,833-file corpus and did not re-run the full test suite. It is a reading of the code plus one local phrase-index replay.

## (h) The provider step, after the profile questions

The profile questions in this note stay the first step. The implemented step that follows them, and that runs before a scan is the moment a model is chosen, is `filesorter providers`. It is documented in `docs/model-providers.md`. A folder can finish that step with "no cloud model". DeepSeek remains the default when its key is set and no other choice is stored. The provider step does not skip the profile questions and does not send a file.

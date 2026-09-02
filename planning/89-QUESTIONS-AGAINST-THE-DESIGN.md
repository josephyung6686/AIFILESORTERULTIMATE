# 89 — Seven questions, put back to the design

Date: 2026-09-02
Status: **A reading of documents that already exist. It changes no code, no test, no
manifest and no vocabulary.** Every verdict below is a quotation plus what the quotation
decides. Where the design does not decide, this document says so and names the smallest
question the owner would have to answer.

The occasion: the owner said *"look at the design, I think it answers your questions"*,
and that the north star is the original design plus a few patches — the onboarding and
questions phase. So the sources, in order of authority, are:

1. `planning/00-database-agent-product-design.md` — the design. `01-product-design-structured.md`
   is the same text sectioned; where a section number is cited (§8.3, §8.7) it is `01`'s
   numbering of `00`'s own words.
2. `planning/66-FIND-FILE-AND-ONBOARDING.md` — the patch. Part III is the onboarding and
   structural-question system; `75-PLAN-ONBOARDING.md` is its implementation plan.
3. The part SPECs, for the mechanism only.

---

## 0. The verdicts, at a glance

| # | question | verdict |
|---|---|---|
| **Q1** | the sizing question | **DECIDED IN SUBSTANCE.** Ask. Do not widen the pattern the way it was prototyped. Cap the asking and leave a tail unresolved. One piece genuinely open: the SCOPE of an answer. |
| **Q3** | collision suffix format | **SHAPE DECIDED, STRING OPEN — and not blocking.** The design's own fourth branch is *stop and ask*, which is what an unbound suffix already produces. |
| **Q5** | locked and open files | **DECIDED.** Excluded by default, with a distinct refusal message. Manual apply already detects it through the staleness recheck; a pre-check for automatic filing is a new mechanism, and that is the owner's — but not until automatic filing is built. |
| **Q6** | the batch bound and halt rule | **DECIDED, AND NOT BLOCKING.** Absent a bound the design says *one action at a time*. The halt rule is stated and is not the engineering default. The number is `cli.py`'s. |
| **Q7** | the unverified cross-volume copy | **HALF DECIDED.** The source stays, the failure is a logged event, the paths and hashes are shown. Where the copy lives and what it is called is genuinely not decided. |
| **Q8** | journal lifetime | **DECIDED.** The journal is append-only and does not expire. Undo has a period — 90 days by default. Adopting a new plan version does not end undo. |
| **—** | `--undo-reject` | **SHAPE DECIDED, NAME OPEN.** The design names two verbs, *inspect* and *reset*, and `66` §17 names the revoke pattern. It does not name a gesture. It also rules out the one-shot form. |

Four of the seven were being carried as blocking and are not. That is the main result.

---

## 1. Q1 — the sizing question

`87` measured all three options and recommended the third, re-keyed from an identifier to
a folder, with `Detector.explain`'s `settled_by_user` branch opened to the single-leader
case. The question here is whether the design supports that reading.

### 1.1 It does support asking, and it names when

`66` §14, in the section titled *Ask only when needed*:

> *"When the engine encounters a **repeated ambiguity** that prevents a useful template,
> group interpretation, or destination proposal, it asks a narrow, evidence-linked
> question. The question should name the visible context and the precise consequence."*

That is option 3, decided, with three conditions attached: the ambiguity must be
**repeated**, the question must be **evidence-linked**, and it must name **the visible
context and the precise consequence**. §14 also requires that *"'not about me' and 'skip
for now'"* remain first-class answers.

`66` §13 says what such an answer is allowed to do. A **structural** answer

> *"Resolves a user relationship or policy fact that file evidence cannot safely
> determine"*

and may

> *"Activate a schema, gate a template, resolve role ambiguity, allow or prohibit a
> category of folder label, or require review"*

but must not

> *"Be inferred silently from weak evidence or reused outside its stated scope"*.

So a confirmation activating a schema is not a concession the design makes reluctantly —
it is the first item on the list of what a structural answer is for.

### 1.2 It supports the folder as the key, and `66`'s own word does 87's arithmetic

`87` §8 worried that 21 questions may be over `80` R2's friction budget. The design
settles that without needing a budget number, because §14's trigger is **repeated**
ambiguity, and 21 questions over 74 files is not one ambiguity repeating — it is 21
separate ones. A question keyed on a folder collapses the repeats into the thing that
recurs. That is `66`'s own word doing the work, not an inference.

The folder is also, independently, the design's strongest non-file signal:

> *"A carefully curated existing folder should be treated as a strong expression of user
> intent."*

> *"Purpose may be supported strongly by an existing user-created folder name or explicit
> language in a form or portal."*

> *"Existing curated folders and user-entered labels should influence retrieval because
> they represent the user's vocabulary."*

**But the design does not say the key must be a folder.** §14's own worked example is
keyed on an entity lifted out of documents — *"We found files connected to Columbia. Which
describes your relationship to Columbia?"* — and it is a good question, because Columbia is
also a thing the person recognises. `87`'s own phrase is *"a folder (**or another thing the
person recognises**)"*, so the example is not a counter-case; it is the same test met by a
different key. What the design settles is the test, not the key: the question must be
evidence-linked and must name the visible context and the precise consequence. **87's re-key
is compatible with the design and supported by the folder-as-intent paragraphs; it is not
required by it, and an entity key that a person recognises is equally permitted.**

### 1.3 One constraint `87` does not carry, and it bites the hardest corpus

A folder-keyed question is **permitted** about a person-shaped folder. What §15 constrains
is what may be offered in it and what may be built from it. `66` §15:

> *"The question 'Does anyone else appear in your files?' should not be a general
> onboarding question. … It must appear only within a deliberate protected-family,
> household, or similar user-created workflow, **after the user has chosen to design that
> kind of branch**."*

> *"The user must explicitly identify the relationship category; **the system must not infer
> dependent status from a name or from documents**."*

`75` C2 states the same rule as an implementation obligation: *"The household question is
raised by the person, never by the files."*

Three separate prohibitions, and it is worth keeping them apart:

| what §15 forbids | what it does not forbid |
|---|---|
| the general onboarding question *"does anyone else appear in your files?"* | a narrow, evidence-linked question about one folder |
| **inferring** a relationship from a name or a document | asking what kind of material is in a folder |
| a person-named folder **label** outside a protected family or household area (§15's table) | recording the answer as a fact |

So *"What kind of material is in `Emma/`? [coursework · legal · household · skip]"* is
allowed: it asks for no name, offers no relationship category, and infers nothing. What is
**not** allowed is offering the relationship categories in the option list — those come only
from a workflow the person opened — or letting the answer produce `Academics/Emma/…` as a
proposed label.

There is also a practical tell that the stronger reading is wrong. To decline to ask about
person-shaped folders, the product would first have to work out that `Emma` is a person's
name, which is precisely the inference §15 forbids.

`87`'s corpus A is Dana — a paralegal, a part-time law student, a single parent with her own
custody matter and her kid's school. The folder-keyed question reaches her folders. What it
may not do is turn her child's name into a branch, or ask her who the child is.

### 1.4 Widening the pattern: the design constrains how, and 87's prototype broke it

The design does not forbid a wider extractor. It constrains one:

> *"It should use word-boundary matching rather than substring matching. Without this rule,
> names such as MIT can be found inside 'submit,' and UNC can be found inside
> 'uncertainty,' producing polished but completely false filing paths."*

> *"It should rank candidate matches instead of accepting the first match, and it should
> require both a minimum score and a minimum margin over the second-best candidate before
> it fills a facet."*

and the adversarial suite must already contain *"course-code patterns that are actually ZIP
codes or device models"*. On top of that, §8.4:

> *"A scanned passport, tax statement, medical document, authentication key, or account
> record should enter a protected state immediately."*

> *"Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits,
> group memberships, and raw sensitive values should remain local."*

`87` §7 records that its option-1 prototype *"put a passport number into the observation
store"*. That is a violation of the constraint, not of the option. **Verdict: option 1 as
prototyped is non-compliant and measured at zero. A compliant widening is not forbidden by
the design; it is simply the thing nobody has built and nobody has measured.**

### 1.5 The paragraph the lead flagged says what a confirmation must NOT be turned into

The node-local classification paragraph:

> *"the engine can propose the PHYS1401 Homework node with an explanation that reflects the
> full context **rather than falsely claiming that the course code was found inside the
> homework itself**."*

Read plainly, this is not an argument against asking. It is an argument about **where the
answer is recorded**. A confirmation must be recorded as a confirmation, on its own
evidence line, and must never be written back into the file's observation store as though
the extractor had read it there. The design has a reliability state built for exactly this,
and it ranks it first:

> *"A **user confirmed** fact has been explicitly accepted, entered, renamed, merged, or
> corrected by the user."*

It is listed above *direct* and above *validated*. Nothing in `00` requires a user-confirmed
fact to be corroborated by machine signals — the corroboration requirement is stated only
for rule-created facts (*"Rules create validated facts when a candidate passes strict
context checks"*). So opening `Detector.explain`'s `settled_by_user` branch to the
single-leader case does not weaken `never_alone`; it recognises that a confirmation is a
different class of thing from a signal. The code's own comment at
`src/recognition/detector.py:416` already says so, and the branch is **already built and
already wired** for the ambiguous case (`src/cli.py`, the `settled_by_user=` argument —
the line moves, the lead is editing that file) — it fires only when `len(leaders) > 1`
(`detector.py:419`). The single-leader `no_corroboration` return at
`detector.py:491–519` never consults it. That is a one-branch change, not a new mechanism.

### 1.6 It supports leaving a tail

> *"A branch can be accepted even if some files remain unresolved; those files may later be
> represented by a scoped General folder, a review queue, or an additional user-created
> branch. The goal is to give the user a good enough structural gist of the corpus so that
> only a limited number of high-leverage changes remain, not to force perfection before the
> user can see the proposed tree."*

> *"Correct abstention is a successful outcome because the product's goal is reliable
> organization, not maximum file movement."*

So `87` §8's fear — that if the budget is six questions the tail stays unclassified — is
not a failure mode under this design. It is the design's stated intent.

### 1.7 Verdict

**DECIDED IN SUBSTANCE.** Ask, on repeated ambiguity, evidence-linked, with the visible
context and the precise consequence named, and with *skip* and *not about me* kept. Record
the answer as a user-confirmed fact on its own evidence line, never as an in-file
observation. Never ask about a person-shaped folder. Leave the tail. Do not ship option 1
as prototyped.

**The one piece the design does not decide, and it matters: the SCOPE of an answer.**
`66` §13 says a structural answer must not be *"reused outside its stated scope"* and `00`
§8.7 says corrections carry scope — *"only to one file, to one group, to one destination
node, to one template, to one domain, or to the entire corpus"* — but neither says which
scope a folder confirmation takes. Corpus-wide, a single confirmation applied at the
single-leader case reaches every file on the disk carrying one matching term, including a
receipt. Folder-scoped, it reaches only the folder that raised it.

> **Owner question Q1.** *When you confirm that a folder is your coursework, should that
> also settle a file elsewhere on the disk that carries one course-shaped word, or only
> files inside that folder?*

---

## 2. `74` §8 Q3 — the deterministic collision suffix format

### 2.1 What the design decides

§8.3, in full:

> *"Filename collisions require an explicit policy. The engine should never silently
> overwrite an existing file. It may propose one of several user-approved behaviors:
> preserve both files using a deterministic suffix, merge only when hashes prove the files
> are identical, retain the newer file while placing an older version into a version family
> review, **or stop and ask the user**. The collision rule must distinguish exact duplicates
> from different files that happen to share a filename. A content-hash match supports
> deduplication review; a filename match alone does not."*

and:

> *"The system should record the intended display name separately from the final
> filesystem-safe name, so that collision and normalization changes remain explainable."*

`66` §8 makes collision policy one of the nine dimensions a filing policy must bind:
*"Collision policy — The user-approved handling of same-name destinations and exact
duplicate cases."*

So the design decides: it is a **user-approved policy choice among four named behaviours**,
not an engineering constant; it never overwrites; a filename match alone is not a duplicate;
and the display name is kept separately from the filesystem-safe name so the suffix is
explainable.

### 2.2 Why this is not blocking

**The suffix string is needed only under the first of the four behaviours**, and all four
are built: `src/mutation/vocabulary.py` names `PRESERVE_BOTH_DETERMINISTIC_SUFFIX`,
`MERGE_ONLY_IF_HASHES_IDENTICAL`, `RETAIN_NEWER_OLDER_TO_VERSION_FAMILY_REVIEW` and
`STOP_AND_ASK`, and `collision.py` implements each. `suffix_for` and `max_suffix_attempts`
are injected with no default *only on the first path* (`collision.py:20-23`).

So an unbound suffix does not stall the product; it removes one of four behaviours. The
design's fourth is the one to select in the meantime, and selecting it is `cli.py`'s —
which is a wiring check for the lead, not a decision for the owner. The standing rule
"absent means refuse, never guess" and the design agree here rather than collide.

### 2.3 Verdict

**SHAPE DECIDED, STRING OPEN, NOT BLOCKING.**

> **Owner question Q3.** *When you tell it to keep both files, what should the second one be
> called — `name (2).pdf`, `name-2.pdf`, or the content hash's first characters?*

---

## 3. `74` §8 Q5 — locked files, open files, aliases and shortcuts

### 3.1 The design does define the behaviour; it declines to define the detection

§8.3:

> *"The product needs defined behavior for locked files, files currently open in another
> application, permission failures, aliases, shortcuts, symbolic links, macOS packages,
> application bundles, network-mounted folders, removable storage, and cloud-synchronized
> directories. The safe default is to avoid following symbolic links during mutation, avoid
> moving package bundles unless explicitly approved, and refuse a move if the source or
> destination is unavailable."*

P12 SPEC OQ3 reads this as supplying defaults for symlinks, bundles and unavailability only.
That is right about §8.3 — but the patch supplies the rest. `66` §10:

> *"Protected material, system files, project dependency trees, package bundles, application
> bundles, symlinks, inaccessible locations, encrypted containers, cloud-conflicted
> material, **files open in another application**, and unsupported files are excluded by
> default."*

and `66` §8's Exclusions dimension names *"…cloud conflicts, **locked files**, and other
named exceptions"*, with §8's worked policy screen printing them to the person in ordinary
language: *"Never include … **open files**, cloud-conflicted files, or files changed after
review."*

And §10 requires the refusal to be legible rather than generic: *"The product should use
distinct refusal messages."*

So the behaviour is decided: **excluded by default, named to the person as an exclusion in
the policy, and refused with a message of its own.**

### 3.2 What remains, and it is an engineering question rather than the owner's

Only the mechanism. And for the manual path the design already supplies one, because
§8.3 requires the recheck immediately before execution and enumerates its triggers:

> *"If its content hash differs, if the source path has changed, if the destination changed,
> if the file disappeared, **or if permission is no longer available**, the action should be
> marked stale and removed from automatic execution."*

The operating system refusing the rename **is** the detection for a manual apply. It is only
automatic filing, where `66` §8 requires the exclusion to be stated to the person *before*
the run, that needs a pre-check — and automatic filing is item last in `66` §22's release
order.

### 3.3 Verdict

**DECIDED for the behaviour. The split on detection is by path, not by seniority.**

- **Manual apply: nothing is owed.** Staleness trigger five — *"if permission is no longer
  available"* — already is the detection, and it is already built.
- **Automatic filing: a pre-check is a new MECHANISM**, because `66` §8 requires the
  exclusion to be stated to the person before the run rather than discovered during it. `84`
  §1 puts mechanisms with the owner, so this is his after all — just not yet. Automatic
  filing is last in `66` §22's release order.

> **Owner question Q5, when automatic filing is built and not before.** *Before it files
> anything automatically, should it check whether a file is open, or is it enough that the
> move fails when it is?*

---

## 4. `74` §8 Q6 — the batch bound and the halt rule

### 4.1 The bound

§8.3:

> *"The product must first create a plan, show it to the user where policy requires review,
> validate that the plan is still current, **apply one action at a time or in a safely
> bounded batch**, verify the resulting state, and record enough information to undo the
> action later."*

The disjunction is the answer to the blocking half. **With no bound supplied, the design's
own first alternative applies: one action at a time.**

Precisely, in the code: `mutation.execute.apply_batch` raises `BatchPolicyRequired` when
`batch_bound` is `None` (`execute.py:565`), which is right — it refuses rather than guessing.
But `apply_plan` beside it is the one-at-a-time path and needs no bound at all. So the
product is not stalled on Q6; it is running the design's first alternative and cannot run
the second. And `cli.py` may pass `batch_bound=1` today without waiting for anything,
because **1 is one of the two literals `84` §1 permits**, and 1 is exactly what the design's
first alternative means.

§8.6 then lists *"Maximum residual files in one review batch"* among the configurable
ceilings, which is where a number lives when there is one; and `66` §8 makes *"approval per
batch"* a review cadence a person picks. So a bound above 1 is user-visible and `cli.py`'s
to supply, exactly as `84` §1 requires.

### 4.2 The halt rule is stated, and it is not the engineering default

`74` Q6 says only a sync conflict is named as pause-worthy. That is true, and it is the
point — the design gives three different outcomes for three different failures, and only one
of them halts anything:

| what happens | what the design says | does the batch stop? |
|---|---|---|
| the source or destination changed | *"the action should be marked stale and removed from automatic execution"* (§8.3) | **no** — that one action is removed |
| a cloud sync conflict appears | *"treat cloud-synced paths as externally mutable, verify them immediately before and after action, and **pause when sync conflicts appear**"* (§8.3) | **yes** |
| the budget is exhausted | *"retain extracted evidence, mark the deferred stage, and **leave the file or group in review rather than guessing**. Cost exhaustion must never turn into lower-quality automatic classification."* (§8.6) | **no** — the remainder defers, it does not fail |

A refusal is not a halt. `66` §10 is explicit: *"A refusal is a result, not an error."*

### 4.3 Verdict

**DECIDED, AND NOT BLOCKING.** One at a time absent a bound; halt on sync conflict only;
stale removes one action; budget exhaustion defers to review.

> **Owner question Q6.** *When it applies a batch and shows you the result, how many moves
> should it do before it stops and shows you — or should it always do one at a time?*

---

## 5. `74` §8 Q7 — the fate of an unverified cross-volume copy

### 5.1 What the design decides

§8.2:

> *"If a cross-volume move uses copy-and-delete rather than an atomic rename, the destination
> copy must be hashed and confirmed before the source can be removed. This establishes file
> fixity: the system can show that a file at its destination is byte-identical to the file it
> intended to move."*

§8.2 also requires the event: the append-only provenance log covers *"planned move, executed
move, **failed move**, external modification detection, and undo"*.

And §8.3 supplies the pattern for exactly this class of half-finished state, in the undo
paragraph:

> *"The product should be able to say, 'This action cannot be undone automatically because
> the file changed after it was moved,' and **provide the relevant paths and hashes for
> manual resolution**."*

So three things are decided. **The source is not removed.** **A `failed move` event is
appended.** **The person is shown both paths and both hashes and is left to resolve it.**
That is more than P12 SPEC OQ6 credits the design with.

### 5.2 What is genuinely not decided

Whether the product may remove the copy it made itself. §7.11's *"it must not delete files"*
is written about the user's residual files and their lifecycle — *"the product must never
delete or automatically expire them"* — not about an artefact the product created seconds
ago and has just proved is not the file it meant to write. The two readings are:

- the copy is a file on the person's disk, so §7.11 binds and it stays, named and explained;
- the copy is the product's own failed output, so removing it is cleanup rather than deletion.

The design does not adjudicate between them, and neither does `66`. **Do not reach for the
created-directory precedent** (P12 OQ5 / `04-resolutions` B3, where undo removes a directory
it created only when still empty): that rule is about undo reversing a completed action, and
this is a failure inside an action that never completed.

Where the copy lives and what it is called is unstated in both documents.

### 5.3 Verdict

**HALF DECIDED.**

> **Owner question Q7.** *When it copies a file to another drive and the copy comes out
> wrong, may it delete the bad copy it just made, or must it leave it there and tell you
> where it is?*

---

## 6. `74` §8 Q8 — journal lifetime versus undo retention

### 6.1 Two different objects, and the design treats them differently

**The journal does not expire.** §8.2: *"Every significant event affecting a file should be
preserved in an **append-only** provenance log."* And *"The product must never overwrite the
evidence record merely because a later extractor or model produces a different answer. A
newer result should supersede an earlier result while retaining the old observation and the
reason it was superseded."* No expiry is stated anywhere in `00` for the log, and its whole
stated purpose is reconstruction: *"the system must be able to reconstruct what it knew, what
it proposed, what the user approved, what changed on disk, and why every change occurred."*

**Undo has a period, and the patch names it.** `66` §11:

> *"The recommended default undo retention period is **90 days**. The user should be able to
> select 30 days, 90 days, one year, or retention until manually cleared, subject to local
> storage limits that are clearly explained. The product should never silently purge
> active-policy history in a way that makes a recent move impossible to understand or
> review."*

So the elapsed-time half of P12 OQ9 is answered outright, and `74` Q8 already noticed it.

### 6.2 Does adopting a new plan version end undo? No.

The undo preconditions are enumerated twice, as closed lists, and a plan version is in
neither.

§8.3:

> *"Before reversing a move, the system checks that the file at the destination is still the
> expected content and that restoring it will not overwrite a newer or unrelated file."*

`66` §11:

> *"**Every move remains conditionally undoable.** Before reversing a move, the system
> verifies that the item at the destination is still the expected content, that its content
> hash has not changed, that restoring it will not overwrite another file, that the source
> location is available, and that no later user or external process has made the reversal
> unsafe."*

Every condition is about the bytes and the filesystem. None is about which plan is current.
§8.8 then says what a new plan does and does not touch:

> *"A new plan should never silently reclassify or move old files. It creates a new set of
> placement recommendations subject to review. The evidence database remains shared across
> plan versions, but the destination tree and user policy define which projections are valid
> in each version."*

Undo of an already-executed move is not a projection; it is a filesystem action reversing a
filesystem action. And the operational promise closes it: the product must *"never silently
change an approved organization plan"* — a plan adoption that quietly removed a person's
ability to reverse last week's move would be that.

### 6.3 The corpus-wide versus per-policy tension `74` raises

`74` Q8 worries that P12 owns a corpus-wide setting a later per-policy setting must reconcile
with. The plain reading resolves it. `66` §11 calls 90 days *"the recommended **default**"*
and offers a menu of four — 30 days, 90 days, one year, until manually cleared — and `66` §8
lists *"Undo period"* as a dimension a named policy binds. **A policy chooses from the same
four**, not necessarily a shorter one: *one year* is on the menu and is longer than the
default. And because §11 states the menu inside Part II, which is about automatic filing,
the corpus-wide setting P12 needs for a manual apply is `cli.py` picking from that same menu.
Nothing needs adjudicating and nothing is invented.

### 6.4 Verdict

**DECIDED.** Journal append-only, no expiry. Undo period 90 days by default, choosable from
{30 days, 90 days, one year, until manually cleared}, narrowable per filing policy. Adopting
a new plan version does not end undo. No owner question is owed.

---

## 7. `--undo-reject` — the gesture a person does not have

The mechanism is built and tested and has no caller: `review_surface.learning_view.learning_view`,
`learning_view.collect_reset` with its `EvidenceNotShown` guard
(`src/review_surface/learning_view.py:107`, `:152`, `:55`), and
`database_agent.learning.reset_preferences` / `reset_cutoff`
(`src/database_agent/learning.py:65`, `:35`). What is owed is the gesture.

### 7.1 The design names the shape, in two verbs

§8.7:

> *"The correction system should include explicit **negative** feedback. Rejected groups,
> rejected destination matches, rejected labels, and rejected residual recommendations must
> be stored with the evidence that produced them. Otherwise the system will repeatedly
> resurface the same attractive but incorrect grouping. **The user should be able to inspect
> or reset learned preferences, so personalization remains understandable and reversible.**"*

Two verbs, and they are a pair: **inspect** and **reset**. `--reject` today delivers the
storing and none of the inspecting or resetting, which is precisely the half §8.7 says makes
personalization opaque and irreversible. So the missing gesture is not an enhancement — it is
the second half of a sentence the product implements the first half of.

§8.4 says the same in the privacy register: *"The user should be able to review and delete
local derived data, revoke a policy for future runs, and reclassify a file as private."*

### 7.2 `66` §17 names what "taking it back" must mean

> *"If an answer becomes unavailable or is **revoked**, the system should **retain historical
> provenance but stop using the answer for future decisions**."*

That is `reset_cutoff`'s behaviour exactly — the docstring at `learning.py:67` reads *"Append
a scoped reset and record the cutoff it establishes. Deletes nothing"* — and it is why
`learning_view.delete()` raises rather than deleting. The design's word for the operation is
**revoke**, and `--answer Q=OPT/=skip/=revoke` already uses it for the same idea on a
different record. That is house vocabulary, not an invention.

### 7.3 The design rules out the one-shot form

This is the part that constrains the gesture's shape rather than just its meaning. §8.7's
word is *understandable*, and `collect_reset` encodes it as a refusal: a reset whose producing
evidence the recorded presentation does not carry raises `EvidenceNotShown`, because
*"a reset made against a view that did not show what produced them is indistinguishable
afterwards from one"* made blind. `collect_reset` requires `presented_state_ref`,
`session_id` and `plan_version` for that reason.

**So a one-shot `--undo-reject "file:field=value"` cannot be built on the designed path.**
The gesture must be *list, then revoke against what was listed* — two commands, or one
command in two runs. This is not a limitation of the code; it is §8.7's *inspect or reset*
appearing as a precondition.

### 7.4 Verdict

**SHAPE DECIDED, NAME OPEN.** The design decides: there must be a way to see what has been
rejected, and a way to take a rejection back; the taking-back keeps the provenance and stops
future use; and it must be made against a presented state, not blind. It does not name a
gesture. `84` §1 puts gesture names with the owner, so the name is his.

**What I would propose, and it is mine and not the design's:** `--list-rejections` prints the
learning view — the scoped preferences and the negative examples with their evidence — and
records the presentation; `--reject "file:field=value" --revoke` (or `=revoke`, matching
`--answer`) collects the reset against it. A proposed hunk is at
`scratchpad/design89/CLI-PATCH.txt`, **marked do-not-apply**: it is a gesture name, and the
lead owns `src/cli.py`.

One thing the hunk turned up that is worth having outside it. `collect_reset` reads back a
`review_presentations` row, and the writer for that row —
`review_surface.presentation.record_presentation` (`presentation.py:87`) — **has no caller
anywhere outside `review_surface/` either.** So the listing half of §8.7 is not merely
unwired: the record that makes an informed reset provable is minted by nothing a person
runs. Whoever wires the gesture wires that too, and `SURFACE_LEARNING` is already a member
of `review_surface.vocabulary.SURFACES` (`vocabulary.py:53`), so no vocabulary member is
added by doing it.

> **Owner question.** *What should the two commands be called — the one that shows you
> everything you have told it was wrong, and the one that takes one of those back?*

---

## 8. The questions, collected

One sentence each. Two of the seven need nothing.

1. **Q1, scope.** *When you confirm that a folder is your coursework, should that also settle
   a file elsewhere on the disk that carries one course-shaped word, or only files inside
   that folder?*
2. **Q3, the suffix.** *When you tell it to keep both files, what should the second one be
   called — `name (2).pdf`, `name-2.pdf`, or the content hash's first characters?*
3. **Q5.** Nothing owed now. When automatic filing is built: *Before it files anything
   automatically, should it check whether a file is open, or is it enough that the move
   fails when it is?*
4. **Q6, the batch.** *When it applies a batch, how many moves should it do before it stops
   and shows you — or should it always do one at a time?*
5. **Q7, the bad copy.** *When it copies a file to another drive and the copy comes out
   wrong, may it delete the bad copy it just made, or must it leave it and tell you where it
   is?*
6. **Q8.** Nothing owed.
7. **The gesture.** *What should the two commands be called — the one that shows you
   everything you have told it was wrong, and the one that takes one of those back?*

---

## 9. What this document did not do

It did not change `src/cli.py`, edit a part package, add a vocabulary member, author prompt
text, choose a gesture name, or pick a number. It answered none of `74` §8's Q2, Q4, Q9, Q10
or Q11, which were not in scope. Where it says the design decides something, the quotation is
above the claim; where it says the design does not, it says so rather than stretching a
sentence to cover it.

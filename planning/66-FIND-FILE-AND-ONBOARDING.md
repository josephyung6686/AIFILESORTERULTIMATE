# 66 — Design Extension · Find, File, and Onboarding Redesign

**Status:** For review
**Scheduling:** Not scheduled until P1–P11 is verified
**Implementation:** No code written
**Extends:** `planning/00-database-agent-product-design.md`, which remains canonical
**Replaces and consolidates:** the Find, automatic filing, and onboarding design portions of
`planning/61-ONBOARDING-AND-SEARCH.md` and `planning/62-DESIGN-EXTENSION.md`

Supplied by Joseph, 2026-08-29. Reproduced as written. Five spans arrived corrupted in
transit and were repaired; §24 lists every one, with the single repair that required
judgement marked. Nothing else was altered — no headings added, no prose tightened.

---

## Purpose

Find and File are user-facing capabilities built on the local index, evidence, fact, grouping,
destination-tree, placement, privacy, and provenance systems already defined in the canonical
design. They are not independent features and must not introduce a second understanding of the
user's files.

Find is a local, read-only retrieval capability. It helps a person locate files, understand why
they appeared, see their real location and accepted organizational relationships, and learn what
the product has protected or could not read. It ships before any mutation capability and remains
useful even for users who never allow the product to move a file.

File is optional, narrowly scoped automation. It allows a user to authorize movements only within
source folders, approved branches of a frozen destination tree, file classes, evidence standards,
exclusions, review cadence, and undo conditions that the user explicitly chose. It is the most
dangerous capability in the product because a wrong move can make a file effectively disappear
from the user's working memory even when the file remains intact on disk.

Onboarding is not a separate questionnaire layered on top of the engine. It is a core design
dependency of templates, schemas, group interpretation, destination-tree design, placement
policy, privacy policy, and automatic-filing controls. Some questions cannot be resolved from
evidence in files because they concern the user's role, the user's relationship to other people,
or the user's purpose for using the product. Those questions must be deliberately wired into the
relevant template and policy flows. They cannot be added casually, asked weekly, or treated as a
generic profile form.

The governing principle is:

> Find makes the local index legible. File creates only authority the user explicitly granted.
> Onboarding collects only the structural information required to resolve a specific product
> decision, and it must show the user what that information will and will not affect.

---

# Part I — Find

## 1. Find is local, read-only retrieval

Find operates on the local index the product already builds. The product does not send a user's
query, filenames, paths, extracted text, OCR output, embeddings, file facts, destination tree, or
search-result set to a cloud model in order to return ordinary search results. Search matching,
ranking, filtering, grouping, and explanation are performed locally against the SQLite-backed
evidence and retrieval indexes.

This local requirement is fundamental rather than an implementation preference. A file search
query can disclose as much as the file itself: a person searching for "passport," "diagnosis,"
"offer letter," "divorce," "Stripe," "tax," or a child's name reveals private intent. Local
search avoids making the act of looking for a document another source of cloud disclosure. It
also makes basic retrieval available in fully offline mode and preserves consistent behavior when
cloud access is unavailable.

Cloud-assisted reasoning may exist elsewhere in the product under explicit consent, but it is not
part of ordinary Find. The only circumstances in which a cloud model could be relevant to search
are an explicitly separate, consented, and clearly labeled optional feature, such as "Ask about
selected files," where the user chooses named files or excerpts after receiving search results.
That feature is not Find, must not be silently invoked by Find, and must follow the existing
privacy and model-consent policy.

Find is read-only. It never moves, renames, copies, deletes, opens, uploads, freezes, edits, or
otherwise mutates a file, a folder, a destination tree, a policy, a fact, a group, or a plan. It
may record a local search history only if the user enables it, and search-history retention must
be separately controllable because queries may be sensitive.

Find should ship before any automatic movement capability. Many users will derive their main
value from finding material again, understanding what the system knows, and navigating accepted
relationships. Those users must never be required to build a destination tree, enable a filing
policy, or grant movement authority in order to search their own local index.

## 2. One retrieval model, not two rankings

The system already scores files and groups using evidence, facts, conflicts, structural
relationships, accepted memberships, destination context, and semantic retrieval. Find uses this
same local evidence and retrieval model. It must not create a second, unrelated ranking system
whose results disagree with the model used for group retrieval or destination-node retrieval.

The user should not normally see raw internal scores such as 0.91 or 0.88. Those values may
combine several technical signals and are not meaningful confidence statements to most people. A
high score can mean a strong text match, a strong accepted-group relationship, a strong filename
match, or a combination of signals. A lower score can still represent a real and useful related
file. Raw scores belong in the evidence inspector or developer diagnostics, not in the primary
search result.

Find presents results in the local retrieval order and gives a concise explanation of why each
result appeared. Examples include "Matched in document text," "Matched in filename," "Part of
accepted group: 2026 Job Search," "Related through PHYS1401 course materials," or "Matches an
approved alias." The explanation is more useful than a number because it lets the user judge
whether the system found the right thing.

The system may allow an advanced evidence view to show the matching fields, evidence excerpts,
accepted group relationships, conflicting signals, and internal score components. This advanced
view must explain that the number is a ranking signal rather than a statement of truth or a
promise that a file belongs in a particular folder.

## 3. Physical location, homes, relationships, and candidates

The phrase "show every home" needs a precise product model. A normal file has one current
physical location in the filesystem. It may also have several genuine organizational
relationships: it can belong to a course, a research project, a lab, an application packet, a job
search, a photo event, or a shared-material collection. It may have several approved destinations
in different plan versions. It may also have speculative candidate destinations that have not
been accepted.

These must not be collapsed into one ambiguous list of paths.

A search result should distinguish the following states:

| Result element | Meaning | User-facing treatment |
|---|---|---|
| Current location | The actual path where the file exists now | Always shown when the user is allowed to view it |
| Filed home | A user-approved physical destination in the active organization plan | Shown as an approved location, if different from current location or useful as context |
| Also related to | An accepted group, project, course, packet, event, or other organizational relationship that does not imply another physical copy | Shown as a relationship, not as uncertainty |
| Shared-material relationship | A file intentionally used by several packets or branches under an approved shared-material policy | Shown with the relevant shared policy and relationship labels |
| Historical location | A prior path recorded in provenance | Available in details, not treated as a current home |
| Possible placement | A candidate that has not been accepted or lacks sufficient evidence | Available only in review or evidence details; never presented as a home |

The product should say "also related to" when the file genuinely serves more than one purpose. It
should not describe a valid multi-purpose relationship as a confidence failure. For example, a
paper written for a course and submitted to a lab may have one current physical location under
Research while also being related to PHYS1401 — Spring 2026. A transcript may have one physical
location in Applications/Shared Application Materials and accepted relationships to more than one
university application packet.

If the user has explicitly enabled aliases, shortcuts, or duplicate copies as a storage policy,
Find may show each actual physical representation. It must clearly identify which item is the
canonical file, which are aliases or shortcuts, and which are independent duplicate copies. It
must not make a user infer this distinction from paths alone.

A primary result should read like this:

```text
Offer letter.pdf
Career › Stripe
Current location: Documents › Job Search › Offer letter.pdf
Also related to: 2026 Job Search
Matched in document text: "Stripe offer letter"
```

This tells the user where the file is, how the system understands it, and why it appeared without
exposing an implementation score or suggesting that multiple relationships are an error.

## 4. Protected material is present, not silently absent

Protected material must never be silently removed from a result set. A search system that quietly
excludes protected files tells the user that the file does not exist, which is a trust failure. At
the same time, standard search must not leak sensitive metadata through filenames, snippets, exact
match indicators, file paths, previews, or overly specific categories.

Find therefore has two explicit local privacy states.

**Standard search** searches ordinary indexed material and represents protected material as
present but unopened. It may show a privacy-preserving indicator such as "Protected items may be
related" or "1 protected item is not shown in standard search." The product must provide a
reachable explanation of what protected material means, why it is not opened, and how the user can
change their protected-search policy. The wording and visible level of detail must follow the
user's protected-display policy. On a shared screen, even "Identity documents" may reveal more
than the user wants; a generic protected count may be safer.

**Unlocked protected search** is a separate local action. It requires explicit local
re-authentication or an equivalent deliberate unlock action. Only after unlock may the system
reveal protected filenames, locations, previews, snippets, exact matching logic, or searchable
protected evidence, and only within the user's selected protected-search policy. Unlocking search
does not grant permission to send the protected material to a cloud model, move it automatically,
or open protected containers for automatic filing.

A protected result is different from an unreadable, deferred, unsupported, excluded, or
low-confidence result. Find must name the state that actually applies. "Protected by your privacy
policy" means the product deliberately did not reveal more. "Unreadable" means the product could
not obtain usable content. "Still indexing" means the product has not completed analysis.
"Unsupported format" means no approved extractor exists. "No strong match" means the local
retrieval system found no result that satisfies the query. These states should never share one
vague message such as "could not find."

## 5. Index completeness and no-result behavior

A user reads "no results" as a strong claim about the filesystem. Find must therefore make the
index's completeness visible. It should show a compact, reachable status such as:

```text
Searching 18,432 indexed files locally
89 files are still processing
14 protected items are hidden in standard search
27 unreadable or unsupported files are not text-searchable
```

The interface should not overwhelm every ordinary result page with implementation details, but
status must be available in the results view and especially in no-result states. A no-result
response should say that no readable indexed match was found, then identify whether files are
still processing, protected, excluded, unreadable, unsupported, or not text-searchable. It must
not imply that an item cannot exist merely because the engine cannot currently retrieve readable
evidence for it.

Find should also explain when a search domain is intentionally narrow. If the user searches only a
selected corpus, only one source root, only documents, or only ordinary unprotected material, the
active scope must be visible and editable. A hidden scope filter is functionally similar to
silently omitting protected content: both make an absence look like a fact about the filesystem
instead of a property of the product's current view.

## 6. Find user journey

A person should be able to use Find with almost no onboarding. The first-run screen should offer
local index setup, not a profile interview:

```text
Find documents you already have.

Choose folders to index locally:
[Downloads] [Documents] [Desktop] [Choose folders]

Your index stays on this device.
Protected material stays local.
You can change indexed folders at any time.
```

Once indexing begins, the user can search before deep analysis, tree design, or filing is
complete. Find should show available results immediately and make progress visible. It should not
make the user wait for OCR of every screenshot, LLM review of every ambiguous document, or a
completed folder proposal before the first useful search interaction.

The normal Find flow is: type a natural-language or keyword query; see local results in the
existing retrieval order; inspect current locations, accepted relationships, and match
explanations; open a file using the operating system; navigate to its current folder; inspect why
a result appeared; optionally unlock protected search locally; and optionally enter a separate
review flow if the user wants to organize the file. Search itself changes nothing.

---

# Part II — File

## 7. Automatic filing is the dangerous capability

Automatic filing is the most dangerous feature in the product. A user can ignore a mistaken search
result, a weak group suggestion, or an unhelpful template. A file moved without the user's
understanding can vanish from their working memory, create conflict, or cause the user to lose
trust in the entire system.

The product's residual design already recognizes that a plausible-sounding wrong destination is
worse than an honest unsorted item. The same principle governs automatic filing. The correct
response to a file the product does not understand is to say so, leave it in place, or route it to
the user's chosen review flow. It is not to place the file somewhere that sounds reasonable.

The user-facing name should not be "automatic filing mode." The product should describe the
capability in terms of the user's goal: "Keep this folder organized" or "File new matching
documents." A user does not want to grant broad authority to an automation system; they want a
particular inbox, download folder, or narrow branch handled predictably.

## 8. A filing policy is more than a threshold

Automatic filing is never enabled globally and never inferred from a model score. It is created by
the user as a named policy. A policy must bind all of the following dimensions:

| Policy dimension | Required decision |
|---|---|
| Source scope | The named source folders or inboxes from which the policy may observe and move files |
| Destination scope | The named, already approved branches in the frozen destination tree that are legal destinations |
| File eligibility | Eligible formats, file states, sensitivity classes, and other file-class restrictions |
| Evidence standard | The evidence that is sufficient, such as direct unique facts only or direct facts plus specified accepted group context |
| Review cadence | Dry run, approval per batch, scheduled review, or direct movement only after demonstrated user trust |
| Exclusions | Protected material, applications, system files, packages, archives, multi-home cases, cloud conflicts, locked files, and other named exceptions |
| Collision policy | The user-approved handling of same-name destinations and exact duplicate cases |
| Undo period | The visible period during which the system retains a conditional undo action and journal |
| Pause and revoke control | How the user suspends, edits, disables, or permanently deletes the policy |

A branch permission alone is not an automatic-filing policy. A user who approves Career/Stripe has
not necessarily authorized the system to search their entire disk for Stripe-related material,
move old archived documents, inspect protected attachments, or act on incoming files from every
cloud drive. Source scope is as important as destination scope.

A policy should be created from a visible source and visible destination branch, not from a
generic global settings screen. A useful first creation flow is:

```text
Keep this folder organized

Source
Downloads

Allowed destinations
Career › Stripe
Career › 2026 Job Search › Offers
Career › 2026 Job Search › General

Eligible files
New PDFs and DOCX files only

Evidence required
Direct unique match only

Never include
Protected files, application packets, system files, archives,
packages, files with unresolved multiple homes, open files,
cloud-conflicted files, or files changed after review

First action
Preview only — show exactly what would move
```

The policy must show the user exactly what it can do in ordinary language. It should not bury the
critical scope in advanced settings or use a raw confidence threshold as its main control. The
engine may use numerical thresholds internally, but the user grants authority through
comprehensible boundaries.

## 9. Dry run, progressive authorization, and review

The first run of every filing policy is a dry run. It shows exactly which files would move, from
where, to where, why the policy considered them eligible, what evidence established the
destination, what files were declined, and why they were declined. A dry run makes the policy
legible before it has consequences.

The default operational sequence should be progressive:

```text
Create a narrow policy
→ Run a dry preview
→ User reviews the proposed batch
→ User approves or changes the policy
→ Product runs further batches as reviewable plans
→ Only after repeated successful review may the user enable direct moves
→ Direct moves remain limited to that exact policy
```

The system must never expand a policy by itself. It may not add sources, destinations, file types,
weaker evidence classes, broader group context, or a longer active period because prior moves were
accepted. If the product believes a useful expansion exists, it should present a new draft policy
and ask the user to review it.

Every completed action appears in a reviewable activity list with the source path, destination
path, evidence summary, policy that authorized it, collision behavior, move time, current status,
and undo availability. The product must not present automatic movement as an invisible background
fact. A user must be able to see what moved today, this week, or under a particular policy, and
pause the policy from the same screen.

## 10. Required declines and distinct language

Automatic filing declines whenever the evidence is insufficient, conflicted, outside policy, or
unsafe to act upon. A refusal is a result, not an error. It should use language that describes
what occurred and tells the user what action is available.

The product must decline when there is no clear legal leader, when the best and second-best
destinations are too close, when evidence is thin, when a required fact is missing, when the file
has unresolved multiple homes, when direct facts conflict with group context, when the file is
protected, when the source or destination has changed, when the file is unreadable, when a
container is encrypted or unsupported, when the file is a system or project artifact, or when any
other policy exclusion applies.

The product should use distinct refusal messages. "This file has two approved homes" means the
user may choose a primary home, shared-material policy, alias policy, or leave-in-place
preference. "I could not read this file" means extraction must be improved, the file should be
manually reviewed, or it should remain in place. "This item is protected by your privacy policy"
means automatic filing was deliberately prohibited. "This file changed after the preview" means
the plan is stale and must be regenerated. "No approved destination fits" means the destination
tree lacks a legal home; the product must not create one automatically.

Protected material, system files, project dependency trees, package bundles, application bundles,
symlinks, inaccessible locations, encrypted containers, cloud-conflicted material, files open in
another application, and unsupported files are excluded by default. The system must never open a
protected container merely to decide whether automatic filing should be allowed. It remains marked
and counted according to policy, but automatic filing creates no exception.

Applications require an explicit product decision. In the initial release, applications should be
suggest-and-review only. The product may understand and group college, job, grant, or other
application materials, but it should not automatically move them under P1 because the cost of
misfiling or exposing a purpose packet is high. A later version may offer a narrow explicit
application policy only after the user has reviewed the branch, source, privacy boundaries,
shared-material rules, and destination structure. This is a roadmap decision, not a reason to
pretend applications are permanently unorganizable.

## 11. Reversibility, undo, and stale plans

"Individually reversible" must become a concrete user promise before automatic filing ships. The
recommended default undo retention period is 90 days. The user should be able to select 30 days,
90 days, one year, or retention until manually cleared, subject to local storage limits that are
clearly explained. The product should never silently purge active-policy history in a way that
makes a recent move impossible to understand or review.

Every move remains conditionally undoable. Before reversing a move, the system verifies that the
item at the destination is still the expected content, that its content hash has not changed, that
restoring it will not overwrite another file, that the source location is available, and that no
later user or external process has made the reversal unsafe. If a file was changed or relocated
after the move, the system must not force an undo. It should say that the move requires review
because the file changed after it was filed, show the relevant paths and hashes, and let the user
resolve the conflict deliberately.

The normal plan lifecycle is: create plan; record expected file identity and source state; verify
immediately before execution; execute using the approved collision policy; verify the result;
append a provenance event; retain the action in the review history; and expose conditional undo
until the stated expiration. If a source file, destination, permission state, cloud-sync state, or
content hash changes between plan generation and execution, the plan becomes stale. The system
must refresh the plan rather than applying an old decision to a changed file.

---

# Part III — Onboarding and Structural Questions

## 12. Onboarding is not a profile questionnaire

The product needs some information that cannot be learned safely from file evidence alone. A file
may identify a school without telling the system whether the user attends, teaches at, works for,
or applied to that school. A lease may be the user's lease or a client document. A report card may
concern the user, their child, a student, a patient, or an employee. File evidence can identify
names, institutions, topics, and possible roles, but it cannot safely decide the user's
relationship to them.

The current onboarding problem is not solved by a generic list of questions such as "What do you
do?" or "Does anyone else appear in your files?" Those questions are broad, intimate, and
disconnected from an immediate visible benefit. A user opening a product to find a document should
not need to reveal their profession, age, family structure, or other people's names before they
can search locally. Asking for that information too early can feel like profiling, especially in a
product that already indexes highly personal records.

Onboarding must therefore be redesigned as a structural-question system embedded in the relevant
product mechanisms. It is not a weekly questionnaire, a generic profile, a growth loop, or a
casual conversational feature. It is a significant product and engineering workstream because the
answers affect schema activation, template availability, role resolution, safety constraints,
privacy policy, destination-tree options, placement validation, residual behavior, and
automatic-filing eligibility.

The system should ask a question only when a specific decision is blocked, explain the exact
decision it unlocks, state what it will not affect, allow the user to skip it, record the scope of
the answer, and allow the answer to be edited, revoked, or re-run through versioned plan changes.
It should not turn a contextual answer into a hidden structural rule.

## 13. Structural versus contextual answers

The product must distinguish answers that resolve an otherwise impossible decision from answers
that merely improve judgement.

| Answer class | Meaning | What it may do | What it must not do |
|---|---|---|---|
| Structural | Resolves a user relationship or policy fact that file evidence cannot safely determine | Activate a schema, gate a template, resolve role ambiguity, allow or prohibit a category of folder label, or require review | Be inferred silently from weak evidence or reused outside its stated scope |
| Contextual | Helps the product decide what to offer, explain, or prioritize | Influence ordering, examples, wording, and non-binding recommendations | Create, remove, hide, or rename folders; gate placement; authorize movement; change privacy state; or silently become a structural rule |

A structural answer may have a direct effect because it resolves a real ambiguity. A contextual
answer must not become a hidden input into a filesystem outcome. If age range, time availability,
broad profession description, or a similar contextual answer ever determines whether a folder
exists, what a file is called, where a file is placed, or what data is exposed, that is a defect
rather than a feature.

The product must make these boundaries visible. A user should be able to inspect a structural
answer and see: what it controls, where it applies, when it was supplied, whether it was inferred
or explicitly confirmed, and how to change it. A contextual answer should state that it changes
only the experience of suggestions, not the underlying tree, file facts, privacy protections, or
movement permissions.

## 14. Ask only when needed

The first-run experience supports local search and indexing immediately. It asks the user to
choose folders, review privacy defaults, and begin using Find. It does not ask for a profession,
age range, household members, dependants, clients, patients, employees, or names before the user
has a reason to provide them.

When the engine encounters a repeated ambiguity that prevents a useful template, group
interpretation, or destination proposal, it asks a narrow, evidence-linked question. The question
should name the visible context and the precise consequence. For example:

```text
We found files connected to Columbia.

Which describes your relationship to Columbia?
[ I study there ]
[ I teach or work there ]
[ Both ]
[ It is not about me ]
[ Skip for now ]

This helps distinguish coursework from professional material.
It will not create or move folders by itself.
```

This is materially better than asking "What do you do?" because the user can see why the question
arose, what it changes, and how to decline. The answer can activate or disambiguate an Academic or
professional schema, but it does not directly move files or create an unreviewed folder.

A later example may arise when the user builds a consulting, legal, recruiting, education,
research, or household template. The product can ask whether a named organization is the user's
employer, client, school, target institution, research venue, or merely a mentioned entity. It
should do so only where the answer changes an allowed template or safety rule. It must preserve
"not about me" and "skip for now" as first-class answers.

## 15. Other people, dependants, and person-shaped folders

The question "Does anyone else appear in your files?" should not be a general onboarding question.
It requests some of the most sensitive information in the product: names of people who may be
children, dependants, clients, patients, employees, candidates, family members, or other private
contacts. It must appear only within a deliberate protected-family, household, or similar
user-created workflow, after the user has chosen to design that kind of branch.

A suitable flow is:

```text
Create a private family area?

You can optionally add names for people whose records you manage.
Names remain on this device and are used only to label folders you approve.

[ Add a person ] [ Not now ]
```

The user must explicitly identify the relationship category; the system must not infer dependent
status from a name or from documents. A person-shaped folder is allowed only where the user's
relationship makes that organization appropriate and where the user explicitly approves the folder
label.

| User-selected relationship | May become a folder label? | Default behavior |
|---|---|---|
| Self | Yes | User-controlled |
| Dependant or child whose records the user manages | Yes, only in a protected family or household area | Review-only by default |
| Household member | Optional and user-controlled | Protected by default |
| Client | No | Use project, matter, engagement, or an approved non-identifying code |
| Patient | No | Do not create person-named folder suggestions |
| Employee, candidate, or student | No | Use role, case, requisition, cohort, or other approved non-identifying structure |
| Unknown or unspecified | No | Do not infer a person folder |

The ethical distinction is deliberate. A folder named for a child whose records the user manages
may make retrieval kinder and safer. A folder named for a client, patient, candidate, employee, or
student can expose the fact that a named person has a matter, record, application, or
relationship. The product should not create that disclosure as a side effect of organization.

Names supplied by the user remain local, protected, scoped to the approved area, and removable.
They must not be sent to cloud models by default, used as global search expansion terms, treated
as evidence that an unrelated file concerns that person, or used to train a shared model. A user
may later rename the displayed folder label without changing the underlying relationship record,
or delete the relationship record and re-run affected proposals.

## 16. The profession and role matcher

The profession matcher is an open design problem and must be treated as a dedicated subsystem, not
as an informal free-text field. A user may describe themselves as a sound engineer, teacher,
researcher, consultant, parent, student, physician, artist, administrator, founder, recruiter, or
several things at once. Being more than one thing is normal. The system must support multiple
roles, each with a scope and possibly a time period, rather than forcing one permanent profession.

Free text must map to a closed list of product schemas cautiously. An unmatched answer must remain
unmatched. "I'm a sound engineer" must not silently activate an engineering or software-project
schema merely because the words are superficially similar. The matcher may propose interpretations
and ask the user to confirm them, but it cannot snap an unfamiliar description to the nearest
neighbor. An explicit "Other," "Not listed," and "Skip for now" path is required.

The matcher should produce one of four outcomes: an exact confirmed schema activation; a confirmed
multiple-role activation; an unmatched answer preserved without activating a schema; or a skipped
answer that leaves the related organizational decisions unresolved. It should store the raw user
wording, proposed mappings, user confirmation state, applicable scope, plan version, and
explanation of what each activated schema enables. It should never convert a role answer directly
into a folder name or automatic-filing permission.

This is significant work because it must connect safely to the template library. The template
system needs to know which templates are available, what role-dependent fields are meaningful,
which person-shaped labels are prohibited, what protected handling applies, and which workflows
need review. The onboarding system needs to explain those effects without making the user
understand the internal schema graph. The design, data model, template contracts, policy engine,
privacy model, user interface, versioning, and evaluation suite must all agree. This cannot be
added randomly or as a weekly product change.

## 17. Re-running structural questions and versioned plans

Structural answers affect proposals and policies, so changing them after a tree is frozen must be
governed by versioning. The interaction cannot remain unexamined. A user may change roles, take on
a new client, stop teaching, become responsible for a dependant's records, decide that a former
household member's files should no longer be grouped by name, or realize that an earlier answer
was incorrect.

When a user edits or re-runs a structural answer, the product creates a draft plan version. It
shows a meaningful diff: which schemas become active or inactive, which templates are affected,
which branches may need review, which placement proposals become invalid or newly possible,
whether any protected area changes, and whether any filing policy is paused. It must not silently
rename folders, reclassify files, reveal protected records, or move anything as a consequence of a
changed answer.

Existing approved structure remains stable unless the user explicitly adopts the new plan. New
answers generate new proposals subject to review. If an answer becomes unavailable or is revoked,
the system should retain historical provenance but stop using the answer for future decisions. It
should identify affected policies and suggestions so the user can decide whether to keep the
existing structure, update it, or return to a less-specific organization view.

---

# Part IV — User-Facing Contracts

## 18. Find contract

Find is local and read-only. It searches the local index and never sends ordinary search queries,
search-result sets, paths, filenames, extracted content, OCR, embeddings, or file facts to a cloud
provider. It never moves, renames, copies, deletes, opens, uploads, freezes, or edits anything.

Find shows the current physical location first, then accepted organizational relationships. It
does not represent an accepted relationship as a second physical copy, and it does not represent a
speculative destination as a home. It uses the product's existing local evidence and retrieval
model, not a second ranking system. It explains why a result appeared rather than showing raw
internal scores by default.

Find never silently omits protected material. Standard search represents protected material as
present but unopened. Explicit local unlock is required before protected filenames, paths,
content, previews, snippets, exact matching logic, or locations can be revealed. Protected,
unreadable, unsupported, deferred, excluded, and no-match states use distinct language. Index
completeness and active search scope are reachable from the result view and visible in no-result
states.

## 19. Filing contract

**Keep this folder organized** is optional automation. It is always enabled by the user for named
sources and named approved destinations in a frozen tree. A filing policy also specifies eligible
file classes, evidence standard, review cadence, exclusions, collision policy, undo period, and
pause or revocation controls. The product never enables it globally, never generalizes it to
another branch, and never broadens it because earlier moves were accepted.

The first run of every policy is a dry run. Direct automatic movement becomes available only after
the user has reviewed successful batches and explicitly enables it for that exact policy. The
product declines rather than guesses whenever evidence is insufficient, conflicted, protected,
unsafe, unreadable, outside scope, or without a clear approved destination. It never creates a
destination, opens protected containers to seek permission, touches system material, or treats a
plausible folder as proof.

Every movement action is visible afterward with its reason, source and destination, policy,
evidence, collision behavior, and undo status. The default undo retention period is 90 days, with
visible user-controlled alternatives. Undo is conditional and does not overwrite later changes.

## 20. Onboarding contract

The product begins with local indexing and Find, not a personal profile interview. It asks
person-level questions only when a concrete template, role resolution, safety rule, or
organization decision cannot be resolved from file evidence. Each question names the decision it
unlocks, states what it will not change, offers skip and not-applicable paths, records its scope,
and remains editable and revocable.

Structural answers may activate schemas, resolve roles, gate safety-sensitive template options, or
prohibit unsafe folder labels. Contextual answers may affect only suggestion order, examples,
wording, and other non-binding presentation decisions. Contextual data must never silently create,
suppress, rename, place, expose, or move files.

Other people's names are collected only in an explicit protected family or household workflow and
only with a user-selected relationship category. Person-named folders are permitted only for self,
dependants, or other explicitly approved household cases. They are prohibited for clients,
patients, employees, candidates, students, and unknown relationships. The profession matcher
supports multiple roles and unmatched answers; it cannot silently map free text to the nearest
schema.

---

# Part V — Open Design Work

## 21. Work that must be designed before implementation

The following are not minor interface details. They are cross-cutting contracts that affect the
template system, local database schema, evidence model, privacy system, policy engine, provenance,
plan versioning, review experience, and evaluation harness.

The **profession and role matcher** requires a closed schema vocabulary, multi-role support, an
unmatched state, confirmation rules, scope rules, persistence rules, schema activation contracts,
evaluation cases, and a user experience that explains consequences without pressuring disclosure.

The **structural-question system** requires a registry of questions, their trigger conditions, the
decisions they unblock, allowed answer types, data classifications, scopes, revocation behavior,
plan-version effects, and the precise template or policy mechanisms that consume each answer.
Questions must be wired into those mechanisms intentionally. They must not be introduced as
recurring engagement prompts or asked weekly because the product wants more profile data.

**Protected search** requires explicit display policies, local unlock behavior, re-authentication
design, search-history controls, accessibility considerations, shared-screen behavior, no-result
language, and test cases for metadata leakage. It also requires a clear distinction between
discovering that protected material may be relevant and exposing why it is relevant.

**Automatic filing** requires a formal policy schema, dry-run contract, evidence thresholds
expressed in user language, source and destination scoping, explicit exclusions, collision
handling, stale-plan detection, cloud-sync behavior, activity history, undo retention, conditional
undo, policy pause and revocation, and an evaluation suite built around harmful misfiling cases.

**Multi-home organization** requires a user-visible distinction among one current physical path,
accepted relationships, shared-material policies, aliases, shortcuts, duplicate copies,
active-plan destinations, historical locations, and speculative candidates. Without this model,
Find will either hide genuine organizational context or present a confusing list of paths that
users cannot interpret.

## 22. Release order

Find should ship first as a local, read-only capability. The initial version should provide local
indexing, ordinary unprotected retrieval, clear current locations, accepted relationships, match
explanations, index-status language, protected-result presence indicators, and a protected-search
design that is safe even before every advanced organization feature is complete.

The next work should connect Find to the existing evidence inspector, accepted groups,
destination-tree canvas, and review surfaces so that users can move from "I found this" to "I
understand why this is related" without any hidden state change. Search should remain useful
whether or not the user ever creates a tree or grants filing authority.

Onboarding redesign should be planned as part of template and policy architecture, not added
independently. The team should first define the structural-question registry and how each answer
connects to a specific schema, template, privacy rule, or policy gate. Only then should product
design implement the task-triggered interaction flows.

Automatic filing should be last. It depends on verified extraction, fact reliability, protected
handling, group and placement validation, frozen-tree behavior, policy scoping, provenance,
collision handling, cloud-sync safeguards, review experience, stale-plan checks, conditional undo,
and replay evaluation. It should not be scheduled until P1–P11 are verified and the team can
demonstrate that the product declines unsafe cases reliably.

## 23. Final principle

Find, File, and onboarding must make the product more useful without making its authority
ambiguous. Find should let a person recover their own information locally and understand the
product's view of it. File should act only inside boundaries the person can name and inspect.
Onboarding should resolve real structural ambiguities only when needed, without turning personal
disclosure into an invisible input to filesystem behavior.

The product succeeds when a user can say: "I can find my files again; I can see what the system
knows and what it protected; I can understand why it suggested a relationship; I can choose
exactly where automation is allowed; and I can stop, inspect, reverse, or change that automation
without losing control of my filesystem."

---

## 24. Transit repairs — editorial note, not part of the design

Five spans arrived corrupted. Four repairs are mechanical and unambiguous. The fifth required
judgement and is flagged so it can be corrected.

| § | Received | Repaired to | Basis |
|---|---|---|---|
| Purpose | "remains useful even fors who never allow" | "even for users who never allow" | dropped word |
| Purpose | "policy flowsannot be added casually" | "policy flows. They cannot be added casually" | run-together sentence boundary |
| 1 | "searching for \"passpodiagnosis,\"" | "searching for \"passport,\" \"diagnosis,\"" | two list items collided |
| 13 | "answers that resolve an otherwise impossiblent." | "...an otherwise impossible decision from answers that merely improve judgement." | completed from the table's own two classes |
| **7** | **"A file moved without the useconflict, or cause the user to lose trust"** | **"A file moved without the user's understanding can vanish from their working memory, create conflict, or cause the user to lose trust"** | **JUDGEMENT. A clause was lost. Reconstructed from §7's own opening, which states the same harm: "a wrong move can make a file effectively disappear from the user's working memory even when the file remains intact on disk." Correct this if the original said something else.** |

# 78 — How a person's words about themselves become folders: one decision, for an adviser

Date: 2026-08-31
Status: **Decision brief. No code, no test, no manifest and no vocabulary was changed by this
document.** It exists so the owner can take one question to a professional and then rule.
Reads: `planning/00-database-agent-product-design.md`, `planning/66-FIND-FILE-AND-ONBOARDING.md`,
`planning/62-DESIGN-EXTENSION.md`, `planning/69-HANDOFF.md`, `planning/75-PLAN-ONBOARDING.md`,
`src/`, `tests/p15/`, and four live runs of the shipped command over a real temporary corpus.

**Written to be read by somebody who has never seen this codebase.** §2 explains the product from
nothing. Every factual claim about behaviour carries a file and line and was checked by reading the
code or by running it; where a claim is a reading rather than a fact it says so.

---

## 1. The question, in one paragraph

This product reads a folder of somebody's files and proposes a folder tree for them. To do that it
must decide what kind of material it is looking at, because the same three files become a different
tree depending on the answer — the product carries 23 named "schemas" (academic, legal, creative,
engineering, and nineteen more) and 208 named "situations" under them, and each one builds a
different shape of folder. Some of that can be read off the files. Some of it cannot, because it is
a fact about the *person* and not about the file: the same syllabus belongs in a different place
depending on whether you took the course or taught it. So the product needs to ask. The design says
it should ask in the person's own words — "tell us what you do" — and support several answers at
once, because being more than one thing is normal. **The open question is the single step in the
middle: how does a sentence a person types about themselves become the small set of schemas the
product then offers to turn on?** The design's first answer was a matcher — map the free text onto
the closed list, and record an answer that matches nothing as unmatched rather than snapping it to
the nearest neighbour. The owner overturned that on 2026-08-29: a model should read the sentence and
judge, not a rule. He owes fuller guidance, and nothing is being built until it arrives. This brief
sets out what is at stake in that step, what the design already forbids around it, and five ways it
could be done.

---

## 2. What the product does with the answer

### 2.1 What the product is

It is a command-line tool. You point it at a folder. It reads every file, extracts evidence
(filenames, headings, dates, course codes), turns that evidence into *facts*, groups the files,
proposes a folder tree, and says which file would go where. **It moves nothing.** Every run ends
with "Nothing was moved."

The product ships a library of 208 **situations** grouped under 23 **schemas**
(`src/facts/domains.py:59-64`). A situation is a kind of life a folder can be: `academic.coursework`,
`academic.teaching`, `creative.sound-design`, `engineering.drawing-package`. The shipped command
prints all 208 with the folders each would build:

```
academic.coursework      My school / Semester / Course / Kind of work
academic.teaching        Semester I taught / Course I taught / Kind of teaching material
creative.sound-design    Picture it belongs to / Where the mix got to / Kind of audio file
engineering.drawing-package   Item on the title block / Kind of drawing
```

*(verbatim from `python3 -m cli --list-situations`, run 2026-08-31; the command prints
"208 situations. Pass one to --situation. The words beside each are the folders it would build.")*

### 2.2 What "activating a schema" actually does — the chain, traced

There are three distinct mechanisms, and they matter differently. Confusing them is easy and the
brief's reader should not.

**(a) The situation chooses which folder shapes are even eligible.** This is the big one.
`--situation` on the command line resolves to exactly one of the 23 schemas
(`src/production.py:237-262`), and that one schema is handed to the whole tree designer as
`active_domains=(schema,)` (`src/cli.py:1172`). It becomes `BranchContext.domains`
(`src/tree_design/routing.py:72`), which selects the applicability rows the template library carries
for that schema (`src/tree_design/routing.py:217-225` calling
`src/tree_design/catalogue.py:47-57`), and those rows are what decide which folder levels a branch
may have. **Schema → eligible templates → proposed folder levels → where files are said to go.**

**(b) The person's confirmed answer can break a tie in how one file is read.** `activated_schemas`
(`src/questions/store.py:246-257`) is handed to the file classifier as `settled_by_user`
(`src/cli.py:1138`, consumed at `src/recognition/detector.py:419-425`). This one is deliberately
narrow, and the code states its three limits (`detector.py:403-413`): it applies only when the
file's own words already support two readings equally; only among those readings; and never to a
file whose words named no schema at all. **A confirmed answer cannot put a reading into a file that
suggested none.**

**(c) An active schema bounds what a model is allowed to propose about a file.**
`active_field_allowlist` (`src/facts/domains.py:137-176`) is the list of fields a model may fill in,
and it is derived from the active schemas. This implements the design's rule that the model "can
only propose facts that belong to the active domain schema"
(`planning/00-database-agent-product-design.md:41`). It is not reached in the shipped command
today, because no model is wired — see §3.4.

### 2.3 A worked example

**Maya.** She is a graduate student who also teaches two undergraduate sections; she is a tenant in
a housing dispute with her landlord; she manages her son's school paperwork; and at weekends she
does live sound for a small theatre. Five lives on one laptop. She is the product's stated north
star — "not the lawyer OR the parent OR the researcher, but the person who is several of those at
once" (`planning/69-HANDOFF.md:15-16`).

If asked what she does, she might type: **"I'm a sound engineer."** That is the design's own worked
example, and it carries the bound the whole question turns on
(`planning/66-FIND-FILE-AND-ONBOARDING.md:547-551`):

> Free text must map to a closed list of product schemas cautiously. An unmatched answer must remain
> unmatched. "I'm a sound engineer" must not silently activate an engineering or software-project
> schema merely because the words are superficially similar.

The product's 23 schemas contain both `creative` and `engineering` (`src/facts/domains.py:59-64`).
Under `creative` there is `creative.sound-design`. Under `engineering` there are fifteen situations
about CAD models, PCB layouts and drawing packages. The words overlap and the lives do not.

### 2.4 What a right match and a wrong match produce — run, not asserted

I created three files in a temporary folder — a syllabus, a homework sheet and lecture notes, all
naming `PHYS 1401` and `Spring 2026` — and ran the shipped command three times over the same three
files, changing only the situation. Verbatim from the reports:

| what was declared | the folder shape the product then offered |
|---|---|
| `academic.coursework` | `--answer 'branch:Coursework=school>term>subject>work_type'` |
| `academic.teaching` | `--answer 'branch:Teaching=term>subject>work_type'` |
| `engineering.drawing-package` | `--answer 'branch:Drawings=design_item>artifact_type'` — *"This option would create no child branches."* |

Three things follow, and they are the whole stake:

1. **A right match and a nearly-right match differ by a whole folder level.** Coursework has a
   *school* level; teaching does not. Maya's teaching material filed as coursework acquires a folder
   for a school she teaches at rather than attends — quietly wrong, and wrong in a way she would only
   notice by going looking.
2. **A wrong-schema match does not produce a wrong tree. It produces no tree.** Under
   `engineering.drawing-package` the product offered a shape that "would create no child branches",
   because the fields `design_item` and `artifact_type` are not facts her files carry. Her coursework
   would sit in one undifferentiated folder. This is the safer failure and it is still a failure.
3. **This is not hypothetical and it has already happened to a real corpus.** The project's own
   persona re-run recorded it: a graduate student who also teaches had her *entire disk* filed as
   `academic.coursework`, "including the material that is `academic.teaching`, a situation the
   shipped library now carries" (quoted at `src/questions/records.py:73-76` from
   `planning/68-PERSONA-RERUN.md` F6). One command-line string made her choose which of her two
   lives to file.

### 2.5 What a wrong match cannot do

Two harms are already structurally closed, and the adviser should know they are off the table:

- **A role answer can never become a folder name.** §16 requires it
  (`planning/66-FIND-FILE-AND-ONBOARDING.md:557-558`: "It should never convert a role answer directly
  into a folder name or automatic-filing permission"). In the code, a free-text answer selects no
  option, so it never reaches the readers that feed folder construction
  (`src/questions/records.py:250-258`; test at
  `tests/p15/test_p15_answer_types.py:134-148`). I ran that test: it passes.
- **Nothing moves.** The shipped command has no mutation path enabled; every run ends "Nothing was
  moved." A wrong match costs a bad *proposal*, which the person is shown and can overrule, not a
  lost file.

---

## 3. What actually exists today, verified

### 3.1 The question-and-answer machinery is real and is not a stub

`src/questions/` is nine modules (plus an empty `__init__.py`). It stores questions, answers, scopes, periods, revocations, and
what each answer controls. Ten commits landed on it in the last two days
(`git log --oneline --grep=onboarding`). `tests/p15/` holds 118 tests; I ran them
(`python3 -m pytest tests/p15 -q -p no:randomly`) — **118 passed**.

What a person can already declare, and what happens to it:

| | mechanism | where |
|---|---|---|
| An answer is recorded with a **scope** and cannot act outside it | `src/questions/vocabulary.py:74-90`, `store.py:260-280` |
| An answer may carry a **time period** (from / until) | `src/questions/records.py:224-227`, refused if it ends before it starts at `:268-273` |
| An answer may be **skipped**, **"not about me"**, **revoked**, or **corrected**, each a distinct state | `src/questions/vocabulary.py:38-48` |
| A **structural** answer may activate a schema, gate a template or select a situation; a **contextual** one may not, and the record refuses it | `src/questions/records.py:168-195` |
| An answer may **never be inferred** — the record refuses a row claiming it was | `src/questions/records.py:244-248` |
| A person can ask **what one of their answers actually did**, in five parts | `src/questions/explanation.py:70-193` |
| Only three question **kinds** ship, and each must name the function that reads its consequence | `src/questions/registry.py:96-125` |
| No question text is written down anywhere; every question is derived from a specific blocked decision in a specific run | `src/questions/triggers.py:12-15` |

### 3.2 The safety bound, checked rather than repeated

The claim I was asked to verify: *a free-text answer names no option, so it reaches
`activated_schemas` and `gated_template` never.*

**It holds, and it holds in the data model rather than in a policy somebody has to remember.**
`answered_options` (`src/questions/store.py:222-243`) walks answers and returns the option each one
*selected*; `activated_schemas` and `gated_template` are both built on it
(`:246-257`, `:260-280`). A `FREE_TEXT` answer that names an option is refused at construction
(`src/questions/records.py:250-258`) with the reason stated in the code: an answer that selected
something "would reach `answered_options`, and from there a schema activation nobody confirmed".

There is a second guard, and it is unusual enough to be worth describing to the adviser. A test
parses every module in `src/questions/` as a syntax tree and fails if any single function both reads
a person's wording and names a schema activation
(`tests/p15/test_p15_gates_held_shut.py:128-144`). It ships with a deliberately sabotaged fixture —
a nine-line function that maps "engineer" to a software schema — and a test asserting the guard
catches it (`:147-161`), plus a third asserting the guard does *not* fire on prose that merely
mentions the rule (`:164-174`). **The document's ruling is executable: the day somebody writes a
matcher, the suite goes red.** I ran it. It passes.

### 3.3 What does *not* exist

- **Nothing in the shipped command asks a person who they are.** The only way to answer anything is
  `--answer <question>=<option>` (`src/cli.py:1591-1651`), which always writes a *choice*; the code
  path that would write free text is not reachable from the command line.
- **The two questions the product does ask are both about files, not about the person**: which of two
  readings a course code is, and which of two shapes a branch should take
  (`src/questions/triggers.py:81-115`, `:189-226`), plus a third about which situation a branch is
  (`:247-291`).
- **No classifier ships.** This is the project's own recorded blocker
  (`planning/69-HANDOFF.md:115`). In my four runs today, every file ended "Waiting for you to say
  what these are." The tree is one folder deep for everyone.

### 3.4 No model call happens today, at all

The command runs in **offline** mode by choice, not by default (`src/cli.py:176-180`): *"it is the
only mode under which nothing about any file can leave the device, and a first run on somebody's home
directory is not the moment to ask for less."* And the model path is not merely disabled by policy —
it is not wired: `gate=None, model_client=None, prompt=None, call_dependencies=None,
model_call_request=None` (`src/cli.py:1480-1482`). The placement engine asks whether the model path
is available before assembling anything (`src/placement/pipeline.py:318-328`) and, finding it
absent, abstains.

One correction to the run output quoted above, so the reader is not misled: the abstention prints
*"Deciding this file needed a model, and §8.4 did not clear this file for a model call"*
(`src/placement/pipeline.py:728-732`). In these runs §8.4 refused nothing; there was no model to
refuse. The wording is imprecise for the no-model-wired case. That is a separate finding and not
this brief's subject.

### 3.5 Work that landed while this brief was being written

A second agent built §16's *buildable half* during this investigation. I first read it as untracked
files in the working tree; it landed mid-document as
**`6b46571` — `feat(onboarding-D1,D2,D3): a person can be more than one thing, and the matcher is
still not built`**, adding `src/questions/roles.py` and `tests/p15/test_p15_roles.py` and modifying
`src/questions/registry.py` and `src/questions/vocabulary.py`. What it adds:

- A role declaration built on the existing answer record, with several roles live at once, each with
  its own scope and optional period (`roles.py:99-151`, `:180-227`).
- §16:553's four outcomes as a closed vocabulary — exact activation, multiple-role activation,
  unmatched, skipped (`vocabulary.py`, appended).
- A fourth question kind, `ROLE_KIND`, routed through the **existing** activation surface rather
  than a second one (`registry.py`).
- **And, crucially, no proposal step.** The declaration question offers the product's *entire* closed
  schema list, unfiltered, handed in by the caller, and the module says so in as many words:
  *"Nothing here reads a person's wording, ranks a schema against it, shortens the offered list, or
  scores anything… Narrowing it IS the proposal step"* (`roles.py:11-15`, `:108-112`).

I re-ran `tests/p15` with this work present: **118 passed**, the free-text guard included. So the
step this brief is about is still shut. Two things in that work are owner questions in their own
right and are listed in §7: the declaration's handling class, which the module itself flags as
needing confirmation (`roles.py:70-74`), and the four new vocabulary members, which under this
project's rules gain approval recorded at the member.

---

## 4. The two documents, and exactly where they disagree

**`66` §16** (`planning/66-FIND-FILE-AND-ONBOARDING.md:539-566`) asks for a *matcher* as a dedicated
subsystem: multiple simultaneous roles each with a scope and possibly a period (`:543-545`); free
text mapped to the closed list "cautiously", never snapped to the nearest neighbour, with an explicit
Other / Not listed / Skip path (`:547-551`); four outcomes, raw wording stored, and a role answer
that never becomes a folder name (`:553-558`).

**`62` §D** (`planning/62-DESIGN-EXTENSION.md:148-192`) records the owner's ruling of 2026-08-29 and
overturns the matcher as a mechanism:

> *"These should not just be directly matched — the LLM uses that information to judge. This cannot be
> rule based and that simplified in this sense."* (`:152-153`)

and the reasoning (`:159-165`):

> What the user says about themselves is **evidence a model reasons with**, in the same way a file's
> text is. "I'm a sound engineer" is not a failed lookup against a 23-item list; it is a sentence that
> bears on how every ambiguous file in that corpus should be read… A matcher would flatten it into one
> of twenty-three tokens and discard everything else in it.

It then says exactly what survives and what does not (`:169-181`): the four bounds survive (no
inventing a schema, no minting a field, no lowering a privacy floor, no acting unconfirmed) and so
does the structural/contextual split; what does not survive is "never snap" *as a mechanism*, because
"the mechanism was a matcher and there is no matcher". It closes: *"Fuller guidance is owed and was
promised. Nothing here should be built until it arrives."* (`:191-192`). `69` §4.3
(`planning/69-HANDOFF.md:173-174`) repeats it as an open owner item.

**They agree on everything except one step.** The record, the four outcomes, multi-role, scope and
period, the raw wording, the explicit Skip path, and the bound that a role never becomes a folder
name — both documents want all of it. The disagreement is *how wording becomes candidate schemas*.
`planning/75-PLAN-ONBOARDING.md:309-315` draws exactly that line and marks the step **GATED**.

### 4.1 A tension inside `66` itself, which the adviser should see

This is a reading, marked as such, and it is not resolved anywhere I could find.

`66` §13 sorts every answer into two classes. A **structural** answer may activate a schema; a
**contextual** answer may not create, remove, hide or rename folders (`:442-445`). Then §13:447-451
gives examples of the contextual class:

> If **age range, time availability, broad profession description**, or a similar contextual answer
> ever determines whether a folder exists, what a file is called, where a file is placed, or what data
> is exposed, that is a defect rather than a feature.

"I'm a sound engineer" is a broad profession description. §16 asks for exactly such a description to
activate a schema, which changes which templates exist, which changes which folders exist. §13 names
that outcome a defect. The two sections can be reconciled — §13's sentence is conditioned on the
answer *being* contextual, and §16's declaration is meant to be structural — but nothing states
which side of the line a free-text self-description falls on, or what makes it structural rather than
contextual. **That is a second thing the owner's ruling has to settle**, and it is independent of
whether a model is involved.

---

## 5. The options

Five, each genuinely distinct in the one step. For each: what a model would be shown, what it could
return, what happens to an answer it cannot match, what leaves the device, what it costs, and how a
wrong answer is caught.

> **On prompt text.** Where an option involves what a model is shown, this document describes the
> **shape and content requirements** only. **Every such description is a proposal requiring the
> owner's approval.** No wording is drafted, proposed or settled here. Prompt text is a mechanism, and
> in this project a mechanism is approved manually (`planning/69-HANDOFF.md:17`); it is also close to
> permanent, because the prompt bytes are fingerprinted into every audit record and every cache key it
> produces (`planning/76-PROMPT-RESEARCH.md:5-9`).

### Option 1 — No model. The person picks from the product's own list.

**The step:** there is no wording-to-schema step, because the person does the mapping. The product
shows its closed list and the person taps one, or several, or "None of these", or skips.

- **Shown to a model:** nothing.
- **Returned:** nothing.
- **Unmatchable answer:** there is no matching, so the case does not arise as a failure. A person who
  finds nothing that fits takes the explicit "None of these" path, which is a real option carrying no
  consequence, and their typed words are kept unmatched.
- **Leaves the device:** nothing.
- **Cost:** zero.
- **A wrong answer is caught by:** the person, who chose it; and the inspection surface, which prints
  what the answer turned on, where it applies, how it was settled and how to change it
  (`src/questions/explanation.py:176-193`).

**This is what the uncommitted work in §3.5 builds**, and it is the *status quo ante* rather than a
straw man: it is safe, cheap, already implemented, and fully compliant with every bound. Stated
fairly, its weaknesses are two and they are real. First, the 23 schema ids are the product's internal
vocabulary — `resource_operations`, `retail_hospitality`, `business_operations` — and are not words a
person recognises about themselves; the useful choice actually lives one level down among the 208
situations, and a list of 208 is not a thing a person reads. Second, it is precisely the flattening
`62` §D objects to: Maya's sentence becomes one token and everything else in it is discarded — the
part that says *sound*, the part that says *engineer*, and the fact that together they describe work
the schema list has no single name for.

**Note carefully: a picker is not a matcher.** `62` §D overturns a *mapping mechanism*. A list the
person chooses from performs no mapping — the person does, visibly, and can see and undo it. Whether
§D's ruling reaches this option is itself a question for the owner (§8, Q1).

### Option 2 — A local model proposes a shortlist; the person confirms.

**The step:** the model is shown the person's sentence and the product's closed list, and returns a
shortlist. Nothing activates until the person taps one.

- **Shown to the model (proposal, requires approval):** the person's own sentence, verbatim; the
  closed candidate list — either the 23 schema ids or the 208 situation names with the folder chain
  each would build; and the instruction that it may return only ids drawn from the list it was shown,
  never a new one, with an explicit "none of these" as a first-class answer.
- **May return:** an ordered subset of the ids it was shown, each with a short reason drawn from the
  person's own words, plus "none of these". Nothing else. The return is validated against the closed
  list before it is displayed, exactly as the existing fact path validates a model's proposed field
  against the closed catalogue (`planning/00-database-agent-product-design.md:42`,
  `src/facts/domains.py:179-183` raising on an unrecognised schema).
- **Unmatchable answer:** the model returns "none of these", or returns ids the person rejects. Either
  way the answer is stored as free text, activating nothing — the outcome §16:553 calls "an unmatched
  answer preserved without activating a schema", which the record already supports.
- **Leaves the device:** nothing. The shipped local transport is loopback and not configurable
  (`src/readers/model_ollama.py:38-42`), and it is the design's second operation mode verbatim —
  *"Local extraction plus a user-installed local LLM for eligible dossiers"*
  (`src/privacy/vocabulary.py:122-123`).
- **Cost:** no API cost. It costs the person installing a local model; and a model that is not running
  must be a refusal rather than an empty answer (`src/readers/model_ollama.py:23-27`), so the product
  has to degrade cleanly to Option 1 whenever it is absent.
- **A wrong answer is caught by:** three layers — the closed return vocabulary (a returned id outside
  the list is rejected before display), the person's confirmation (nothing activates otherwise), and
  the inspection surface afterwards.

### Option 3 — A cloud model proposes a shortlist; the person confirms.

Identical in shape to Option 2; the difference is that the person's sentence leaves the device.

- **Shown / returned / unmatchable:** as Option 2.
- **Leaves the device:** the person's own description of themselves, plus the closed candidate list.
  This requires operation mode `hybrid` or `cloud_assisted` (`src/privacy/vocabulary.py:112-114`),
  explicit consent, and an audit record naming the authorising policy, the model, and the prompt
  fingerprint (`planning/00-database-agent-product-design.md:200`,
  `src/privacy/audit.py:90-114`).
- **Cost:** one model call per declaration — a handful per person, once, not per file and not per run.
  In money that is negligible. **But the existing cost machinery cannot express it**: the budget is
  per-scan and scaled by corpus size, `floor(file_count × rate / 1000)`
  (`src/llm_harness/budgets.py:166-179`), which is the wrong shape for a once-per-person call. The
  deployment currently sets every ceiling to 8 (`src/cli.py:149-153`, applied at `:1018-1019`), and
  constructs no budget object at all in production — `ScanBudget` has no caller in `src/` outside the
  harness that defines it.
- **A wrong answer is caught by:** as Option 2.

**This option carries a structural obstacle that the adviser must be told about, because it is not a
matter of policy but of what the code can express.** The product's privacy gate is entirely
*file-shaped*, and a declaration is not about a file:

| the gate requires | where | why a declaration does not fit |
|---|---|---|
| a target naming at least one file | `src/privacy/release.py:98-105` — *"a release decision is about file versions; a target with no files has nothing to classify and nothing to audit"* | a role declaration is about the person |
| requested items drawn from six closed kinds, every one a *reference* into stored file evidence | `src/privacy/items.py:110-197` | a typed sentence is none of the six; there is no item kind that carries a person's own words |
| an audit record carrying file sensitivity, file ids and content hashes | `src/privacy/audit.py:93-111` | there is no file, no hash, and no per-file sensitivity |
| a call site from a closed set of five | `src/llm_harness/vocabulary.py:20-28` | a declaration call would be a sixth |

So Option 3 (and Option 2, which uses the same gate) requires either extending the release model to
subjects that are not files — a change to the product's central privacy mechanism — or routing the
declaration through the file-shaped path it does not fit. **This is the largest hidden cost in the
decision and it is invisible from the design documents.**

There is one further point the design already anticipated in a neighbouring case: names a person
supplies about *other people* "must not be sent to cloud models by default"
(`planning/66-FIND-FILE-AND-ONBOARDING.md:533-535`). A self-description is not a third party's name,
but it is the same kind of input — supplied by the person rather than extracted from a file — and the
design says nothing about it either way.

### Option 4 — No proposal step at all. The declaration becomes standing context for judgements the product already makes.

**The step:** it is deleted. Wording never becomes candidate schemas. Instead the sentence is carried
as one more input into the model calls the product already makes about *ambiguous files*, and schemas
continue to be activated by each file's own evidence.

This is the reading closest to `62` §D's own words — the declaration is *"context the whole
interpretation path can read"*, and *"the user's answer is another input to the same judgement, not a
substitute for reading"* (`planning/62-DESIGN-EXTENSION.md:183-189`).

- **Shown to the model (proposal, requires approval):** the existing per-file evidence packet, plus
  the person's declaration as context. No candidate-schema list, because the model is not being asked
  to choose a schema.
- **May return:** exactly what it may return today — facts drawn from the active schema's field
  allowlist, each citing evidence actually present in the file
  (`planning/00-database-agent-product-design.md:41`, enforced at `src/facts/domains.py:137-176`).
  Nothing about the person.
- **Unmatchable answer:** the case does not arise. A declaration that bears on nothing changes nothing.
- **Leaves the device:** the sentence, attached to every file-level call it is relevant to. **That is
  many calls, not one** — which inverts Option 3's cost profile and, more importantly, inverts its
  exposure profile: the same sentence goes out repeatedly rather than once.
- **Cost:** no new call, so no new call cost. But it changes the text of an existing prompt, and the
  prompt bytes are fingerprinted into every audit record, every fact row and every cache key
  (`planning/76-PROMPT-RESEARCH.md:5-9`). A word changed is a new prompt and a new fingerprint, and the
  old records point at a digest whose text no longer exists. **Effectively permanent.**
- **A wrong answer is caught by:** the existing validator — the model must cite evidence found in the
  file, and a declaration cannot supply that citation
  (`planning/00-database-agent-product-design.md:42`). This is a genuinely strong catch and it is
  already built.

Its weakness is the one the design cares most about. §13:453-457 requires that a person be able to
inspect a structural answer and see *what it controls*, and `src/questions/explanation.py` implements
exactly that. **A declaration that is standing context controls nothing in particular and everything
in general.** There is no sentence to print. The product would be unable to answer the question its
own design says it must answer, and §16's four outcomes and confirmation state would have nothing to
attach to. Whether that is acceptable — and if so what the person is shown instead — is the second
half of owner question Q2 in `planning/75-PLAN-ONBOARDING.md:392-394`.

### Option 5 — Do not ask who the person is. Ask what *this folder* is, where the product already asks.

**The step:** there is no declaration, so there is no wording. The product already asks a narrow,
evidence-linked question when two situations both fire on one branch's evidence — *"Which of these is
Coursework?"* (`src/questions/triggers.py:247-291`), scoped to that branch only, with the answer
consumed per-branch (`src/questions/store.py:283-304`). Maya's roles are never declared; they are
read off the answers she gives about her own folders, one folder at a time.

- **Shown to a model / returned / leaves the device:** nothing.
- **Unmatchable answer:** she skips, and the branch keeps whatever situation the run was given —
  which is what makes asking free (`src/questions/store.py:296-299`).
- **Cost:** zero.
- **A wrong answer is caught by:** the same inspection surface, and by the fact that the answer is
  scoped to one branch and cannot reach another.

Stated fairly, this is the option most in keeping with the product's own stated discipline: ask only
when a decision is blocked, from evidence the person can see
(`planning/66-FIND-FILE-AND-ONBOARDING.md:432-434`; `src/questions/triggers.py:12-15`). It also
already exists and already works. Its weakness is exactly the one `62` §A was written to fix: it can
resolve nothing for a corpus the product cannot read in the first place, which is today's state for
every persona tested (`planning/69-HANDOFF.md:109-111`); and it never gives the product the standing
fact that "this person teaches" — so it must ask again for every branch, forever.

**Options 5 and 1/2/3 are not mutually exclusive.** A declaration could supply a default that the
per-branch question overrides. That combination is the shape `62` §A originally argued for, and it is
worth putting to the adviser as such.

---

## 6. The risks, by option

### Risk A — a confident wrong match

The model returns `engineering` for "I'm a sound engineer" and it looks plausible enough that the
person taps it.

| | exposure |
|---|---|
| 1 | Low. No model to be confident. The person may still misread the list — `creative` is not an obvious word for sound work — but the error is theirs and visible. |
| 2, 3 | **The central risk.** A shortlist is an endorsement: a list of three with `engineering` first is read by most people as the product's opinion. The confirmation step is the only defence, and confirmation is weak against a plausible-looking first item. Mitigations available: no ranking (present candidates unordered), always include "none of these" at the same visual weight, show what each candidate *would build* — the situation list already prints exactly that — and forbid the model from returning fewer than N or more than M. All are proposals requiring approval. |
| 4 | Different in kind and harder to see. There is no match to be wrong, but the declaration tints every ambiguous file. A person who says "I'm a sound engineer" may find that their unrelated files are being read through it, with nothing on screen connecting the two. |
| 5 | Low, and bounded: a wrong answer affects one branch. |

### Risk B — a match that leaks something about the person into a folder name

| | exposure |
|---|---|
| all | **Structurally closed for the declaration itself.** §16:557 forbids it, and a free-text answer selects no option and so reaches no folder-building reader (`src/questions/records.py:250-258`, test at `tests/p15/test_p15_answer_types.py:134-148`, passing). Option 1's confirmed choice does activate a schema — but a schema id is the product's own word, not the person's, and it names a template, not a folder label. |

**One caveat the adviser should have.** The general risk of a private value becoming a folder name is
*not* hypothetical in this product — the project's own persona re-run recorded a client's passport
number becoming a group's display label and printing as a proposed folder name
(`planning/69-HANDOFF.md:117`). That defect is in a different mechanism (labels derived from file
evidence) and is recorded as blocking. It matters here only as evidence that this class of leak is
live in the product, so the declaration's exemption should be verified rather than assumed whenever
the declaration path is wired to anything new.

### Risk C — a person's words being sent off-device when they did not expect it

| | exposure |
|---|---|
| 1, 5 | None. |
| 2 | None off-device. The residual risk is a person who does not distinguish "a model" from "the internet" and assumes the worse. |
| 3 | **The real one.** The sentence is the most identifying free text in the whole interaction: it is what somebody *is*. And revocation cannot retract it — the design says so and requires the product to say so too (`planning/00-database-agent-product-design.md:200`: *"Revocation cannot necessarily retract data already sent to an external provider, so the product must communicate that distinction clearly."*) |
| 4 | **Worse than 3 in exposure and better in salience.** The same sentence goes out with many file-level calls rather than once, so the volume is higher; but it travels inside a mechanism that is already audited per call and already requires consent, so the person is at least being asked at a moment they understand. |

**An unresolved point of law-of-the-document, worth putting to the adviser.** §8.4 lists nine kinds of
data that are always local and may never be named in a model request. The seventh is **"user
edits"** (`planning/00-database-agent-product-design.md:186`, encoded verbatim at
`src/privacy/vocabulary.py:142-145`). Whether a person's typed self-description is a "user edit" in
that sense is **not settled anywhere I could find**. If it is, Options 3 and 4 are closed by the
design as written and no consent can open them. If it is not, the design is silent about a category
of data it never anticipated. This is not a gap I can fill.

---

## 7. What the design already forbids, and what is genuinely open

### Fixed. A ruling has to live inside these.

1. **A role answer never becomes a folder name or an automatic-filing permission.**
   `66` §16:557-558.
2. **An unmatched answer stays unmatched; nothing snaps to the nearest neighbour.** `66` §16:547-551.
   Currently enforced by a syntax-tree guard with a sabotage fixture
   (`tests/p15/test_p15_gates_held_shut.py:128-174`).
3. **The schema vocabulary is closed at 23 and a model may not invent a member.**
   `src/facts/domains.py:59-64`; option-level refusal at `src/questions/records.py:94-99`; `62`
   §D:169-171 confirms this survives the ruling.
4. **A structural answer may not be inferred.** `66` §12; the record refuses a row claiming it was
   (`src/questions/records.py:244-248`).
5. **Nothing acts unconfirmed.** `62` §D:169-171.
6. **Privacy policy is enforced before content reaches any model or external connector**, and data is
   classified into handling classes *before* escalation.
   `planning/00-database-agent-product-design.md:177-178`.
7. **Nine kinds of data are always local** and are not expressible as a releasable item — the request
   is not constructible rather than merely denied. `src/privacy/vocabulary.py:142-145`,
   `src/privacy/items.py:95-107`.
8. **Every model call is audited** with the authorising policy, whether the material was sensitive,
   which excerpts, whether redacted, which model, and the prompt fingerprint.
   `planning/00-database-agent-product-design.md:200`, `src/privacy/audit.py:90-133`.
9. **Under `offline` and `local_model`, no content may go to a cloud target** — refused at the
   target's locality (`src/privacy/denial.py:151-157`). The shipped deployment is `offline`
   (`src/cli.py:176-180`).
10. **Protected material is marked and counted, never opened, and never silently omitted.**
    `planning/69-HANDOFF.md:12-14`; enforced before any evidence is read at
    `src/recognition/detector.py:362-372`.
11. **A contextual answer may never create, remove, hide or rename a folder.** `66` §13:445; the
    record refuses such a question at `src/questions/records.py:168-195`.
12. **Prompt text and template membership are approved manually**, and a closed vocabulary gains a
    member only with the approval recorded at the member. `planning/69-HANDOFF.md:17`;
    `planning/75-PLAN-ONBOARDING.md:82-83`.

### Open. The design is silent, and this document does not fill it.

- Whether a role declaration may go to a model at all, and under which operation mode.
- Whether a person's typed self-description falls inside §8.4's always-local "user edits". **Silent.**
- Whether a sixth model call site may exist, and whether P7's release model may address a subject that
  is not a file. **Silent.** The code makes it impossible today (§5, Option 3).
- Whether a free-text self-description is a *structural* answer or the *"broad profession
  description"* §13:449 places in the contextual column. **Unresolved inside `66` itself** (§4.1).
- The declaration's handling class. The in-flight module proposes `sensitive_personal` and says the
  owner should confirm (`src/questions/roles.py:70-74`).
- Whether the choice is offered against the 23 schemas or the 208 situations.
- The four new outcome vocabulary members now in the working tree, which need approval recorded at the
  member (§3.5).

---

## 8. The questions the owner must answer

Narrow enough to act on. Q1–Q3 are the ruling; Q4–Q7 are what an implementer needs immediately after
it.

**Q1. Is a model involved in this step at all — and if so, may its output ever be anything other than
a proposal the person confirms before something activates?**
This is the whole ruling. Answering "no model" selects Option 1 or 5 and closes the rest. Answering
"yes, proposal only" selects Option 2 or 3. Answering "yes, and not as a proposal" selects Option 4
and requires Q5.

**Q2. If a model is involved, may the person's own sentence leave the device — never, only under
explicit consent in `hybrid`/`cloud_assisted`, or freely?**
This is the difference between Option 2 and Option 3, and it is the only question in this brief whose
wrong answer cannot be undone: a sentence sent cannot be recalled, and the design already requires the
product to say so (`00`:200).

**Q3. Is a person's typed description of themselves a "user edit" under §8.4's always-local nine?**
If yes, Q2 is already answered — never — and Options 3 and 4 are closed by the design as written. This
is a reading of `00`:186 that only the author can settle.

**Q4. Structural or contextual?** §16 wants the declaration to activate schemas, which only a
structural answer may do. §13:449 names "broad profession description" among the contextual answers
that must not determine whether a folder exists. Which is it, and what makes it so?

**Q5. If the declaration is standing context rather than a proposal (Option 4), what does the product
show a person who asks what their answer did?** §13:453 requires an answer to be inspectable and the
product already implements that surface. Standing context has nothing to put in it.

**Q6. Is the list a person chooses from the 23 schemas or the 208 situations?** 23 is short enough to
read and too coarse to be useful — `creative` does not tell Maya it contains sound design. 208 is
useful and unreadable. This decides whether Option 1 is viable on its own.

**Q7. What does the product say to a person whose words match nothing?** §16:553 requires the outcome
to exist and §16:551 requires the path to be explicit. What is *said* is not specified anywhere, and
it is the sentence most likely to be read as rejection.

---

## 9. My judgement, kept separate from the evidence above

The owner asked for a report to take to an adviser, not a decision, and nothing below is one.

**The strongest option on the evidence I gathered is Option 2 — a local model proposing a shortlist
the person confirms — with Option 5 kept alongside it, and with Option 1 as the guaranteed fallback
whenever no local model is present.** Three reasons.

First, it is the only option that honours both documents without straining either. `62` §D's actual
objection is that a matcher *discards* everything in the sentence except one token; a model reading
the sentence and proposing candidates discards nothing, and the person still does the deciding, so
§16's "an unmatched answer must remain unmatched" survives intact and the four outcomes still have
something to attach to.

Second, it answers Q2 and Q3 by making them not arise. Nothing leaves the device, so the unresolved
question about "user edits" does not have to be settled before anything can be built — which matters,
because that question is a reading of the canonical design that only the owner can give, and holding
the whole workstream on it is expensive.

Third, its failure mode is the one this product handles best. Every other option fails silently; this
one fails as a visible list the person can reject.

**The strongest argument against it**, which I want on the record because it is not weak: Option 2 and
Option 3 both require the privacy gate to release something that is not about a file, and that gate is
the most load-bearing mechanism in the product. Extending it is not a small change and it is not
visible from any design document. If that cost is judged too high, **Option 5 plus Option 1 is a real
answer and not a retreat** — it ships, it costs nothing, it breaks no bound, and it is the shape the
product's own §12 discipline argues for.

**The option I would most want the adviser to scrutinise is Option 4**, because it is the most
faithful reading of the owner's actual sentence and the one whose consequences are hardest to see. It
sends more, more often, than Option 3 does; it makes the prompt change permanent; and it leaves the
product unable to answer "what did my answer do?" — a question its own design says it must answer.
Those three things do not appear on its face.

---

## 10. What this document did not do

It changed no code, no test, no manifest and no vocabulary. It answers none of §8's seven questions.
It drafts no prompt text and proposes no new schema id. It does not touch the work in flight described
in §3.5 and it does not unblock `planning/75-PLAN-ONBOARDING.md` §5, which stays gated until the
owner rules.

# 71 — Why nothing files, diagnosed

Date: 2026-08-29. Written after `68`'s persona re-run found that four different people got the
same nothing, and after Joseph asked for a systematic diagnosis rather than a list of symptoms.

**Read `70-HOW-IT-WORKS.md` first if you have not.** This document assumes the mechanism and only
explains where it breaks.

---

## 0. First, a correction about a document that is not this one

Joseph supplied a critique of a design called **FileGraph** — facets keyed on `(file_id, dim_id)`,
`same_session_as` edges, tier 0/1/1.5/2/3, Bergman et al., a "Locked Decisions" table, 480k
characters of research journal.

**None of that is in this repository.** `grep` finds no `filegraph`, no `facet`, no `dim_id`, no
`same_session_as`, no `MEASURED_LOCAL`, no `Bergman`. It is a different project, or a parallel
design track. **Its fixes must not be applied here literally** — there is no facet table to add a
`status` column to, and no session-clique edge type to threshold.

What it IS good for, and the reason it is worth the attention, is that it names **failure classes**.
A critique of one system is a checklist for another. Section 4 runs its nine findings against this
machine and reports which ones land. Two land hard, three land partly, four do not apply.

---

## 1. The one-sentence answer

**Nothing files because a file is never classified, and a file is never classified for two
independent reasons that are both in the composition root, not in any of the eleven parts.**

Neither reason is a design flaw, a hard trade-off, or a decision anyone has been avoiding. Both are
gaps where two correct components were sized against different assumptions and never introduced to
each other — the same failure class as the `scan_state` defect fixed earlier today, in which the
composition root wrote one word and P9 read another, so every live run had an empty neighbourhood
and no group could ever hold two files.

This project's failures are not in its parts. **They are all at seams**, and they are invisible to
the test suite because each side of every seam is correct and tested in its own vocabulary.

---

## 2. The blocker, proved

The recognition subsystem exists, is wired, and runs on every file. It holds **8,907 authored terms**
across 23 schemas — `problem set`, `syllabus`, `lab report`, `office hours`, `Columbia University`.
On the four-file coursework corpus it returns `None` for every file, and `classifications` holds
zero rows.

Asked to explain itself, it does — twice, and the second answer only appears once the first is
fixed.

### Cause A — the document's words never reach it

Every observation the detector can see for `Lab Report.txt`:

```
[filesystem.record ] possible   'Lab Report.txt'
[filesystem.record ] possible   '/…/scratchpad/demo'
[filesystem.record ] direct     'Lab Report.txt'
[filesystem.record ] direct     '.txt'
[filesystem.record ] direct     'text/plain'
[text.structured   ] possible   'PHYS 1401'
```

The filename, the path, the extension, the MIME type, and one identifier. **The body of the document
is never recorded as an observation at all**, because the only thing in the shipped deployment that
reads body text is a single regular expression looking for identifier tokens.

The detector's own words:

> `Abstention(reason='no_corroboration', … "academic matched one authored term ('lab report') and
> every node row carries a `never_alone` rule; one signal does not activate a schema")`

It matched `lab report` — **from the filename** — and refused to classify on one signal. That refusal
is correct and deliberate: a filename is not a fact, and one term is not a finding. The corroborating
signal it wants is a *context term* — `office hours`, `assignment due`, `problem set` — and those
live in the body text it is never shown.

**So the detector cannot succeed for any file, ever.** Not because it is weak, but because it is
never given the half of the evidence its own rule requires.

### Cause B — and when it does succeed, there is no class to assign

Proved by experiment on a copy of a real plan database: add the body text as observations, change
nothing else, and re-ask. The abstention reason **changes**:

> `Abstention(reason='unassigned_handling', … "academic was recognised from 2 authored terms and the
> caller's handling policy states no class for it; recognition is not classification")`

Recognition now works. Classification still does not, because the handling policy the deployment
passes in covers **4 of the product's 23 schemas**:

| | schemas |
|---|---|
| **have a handling class** | `finance`, `identity`, `legal`, `medical` |
| **have none** | `academic`, `research`, `career`, `photos`, `code`, `college_applications`, `law_practice`, `business_operations`, and eleven more |

`SAFETY_DOMAIN_HANDLING` was written to do one job — mark safety-domain material as **protected** —
and it does that job correctly. It was never a general classification policy, and nothing else was
ever supplied. So an ordinary coursework file, recognised perfectly, still has no class to be given.

### The chain, and why it stayed hidden

```
body text is never observed        →  recognition sees 1 signal   →  no_corroboration
   ↓ (supply body observations)
recognition sees 2+ signals        →  no class for `academic`     →  unassigned_handling
   ↓ (supply handling for ordinary schemas)
classified                          →  the privacy gate opens     →  placement can decide
```

Cause B was **invisible while Cause A stood**, because the run never got far enough to hit it. This
is why "why does nothing file" has been answered three times this month with three different
plausible half-answers.

### What this dissolves

`65` §2.2 recorded this as a genuine trade-off requiring the owner's ruling:

> *"Widening the extractor trades privacy posture for recall on a first run. Narrowing the detector
> wastes the research. … Whichever way it goes, it is the owner's call."*

**The trade-off was mis-stated, and the measurement shows why.** There are two knobs, not one:

| knob | what it changes | privacy cost |
|---|---|---|
| **observations** — what gets recorded as seen | what the detector can recognise | stays on the device, and filenames and paths are already recorded this way |
| **facts** — what the product asserts about a file | **what a folder gets named after** | this is the real one |

Verified: an observation carrying body text gets the locator `body:field=prose`, and the shipped
deployment's direct slot — which claims only `body#…` and `heading…` — returns **False** for it. So
the document's words can reach the detector **without becoming folder names**.

The thing the project was afraid to widen is not the thing that needs widening.

### Cause C — the templates need a hierarchy the deployment cannot fill

The classification chain is only half the story. The tree has its own collapse, and it is the same
shape.

Priya's corpus: four files, two courses, `PHYS1401` and `PHYS2801`, both known to the engine. The
picker was offered a split and here is what it said:

```
BRANCH: Coursework
   opt_0          children=0   ACCEPTED
   opt_no_split   children=0   no report
   -> chose opt_no_split
```

The split **passed validation** — it is a legal, accepted option — and was discarded anyway,
because it reports **zero child branches**. Asked what it contains:

```
summary      : This option would create 0 school, 0 term, 2 subject, and 0 work_type.
               4 file(s) would stay unresolved and visible.
child counts : {'school': 0, 'term': 0, 'subject': 2, 'work_type': 0}
children     : 0
```

The option knows there are **two subjects**. It produces no folders and leaves all four files
unresolved, because the `academic.coursework` template is four levels — school → term → subject →
work_type — and the deployment can fill exactly one of them. A level with no settled value truncates
everything beneath it, which is correct and deliberate and has a test named after it. The
consequence on a real disk is that the level the product COULD fill is never proposed, because a
level above it is empty.

**The machine is not broken; it is starved.** The integration suite supplies four fields and the
same code builds `Columbia / Fall2026 / PHYS1401 / Syllabus`, four levels deep. The shipped
deployment supplies one:

```
direct slots: [('cli.text.identifier', 'subject')]
```

Every template in the 208-row catalogue whose first dimension is not `subject` therefore cannot
produce a folder on this deployment, ever.

**This corrects `68` F3.** That finding blamed the one-folder tree on the review step merging every
group into one. The merge is real and it does move where structure would appear — but it is not the
main reason. Even with the merge, the split was offered and ACCEPTED; it died on the missing levels.
A person would still get one folder with the merge removed.

### Cause D — the folders the person already made are read, then discarded

From the audit in `71-diagnosis/audit-existing-folders.md`, measured on a corpus with four levels of
real nested structure:

| | nested corpus | flat control |
|---|---|---|
| directories on disk | 8 | 1 |
| existing folders P3 recorded | 8 | 1 |
| branch candidates derived from them | 8 | 1 |
| **branch candidates chosen** | **0** | **0** |
| nodes in the proposed tree | 1 | 1 |

**The two proposed trees are identical.** Flattening a four-level hierarchy into one directory
changed the proposal not at all. The library reads the person's folders and offers every one as a
branch card; the shipped command discards all of them one line later, and no code in `src/` can
write a node of type `existing` in any case — so even a chosen folder would enter as a fresh
proposal wearing the folder's name.

For a person who has already organised half their disk, the product currently cannot see that they
did.

### And one independent defect worth its own line

From `71-diagnosis/audit-override-and-multivalue.md`: `preferred_fact` counts **rows**, not distinct
values. So when the product's own two producers write the same fact and **agree**, the slot resolves
to "unresolvable" and the file's folder level is deleted. Agreement causing failure is the least
intuitive bug in the codebase. The `preferred` column that would distinguish an override from a
genuine multi-relationship is inert — its only writer has zero callers — and `fields.multiplicity`,
the declared home for "may this field hold two values at once", is NULL on all 56 catalogue rows.

---

## 2a. The root cause, stated once

Four symptoms, one cause:

> **The shipped deployment feeds the machine one fact from one regular expression and observes no
> body text, while every consumer downstream of it was built for a rich fact set.**

| symptom | consumer | what it was built for | what it gets |
|---|---|---|---|
| nothing is classified | the detector, 8,907 authored terms | words from documents | one identifier + a filename |
| still nothing, after that | the handling policy | a class per schema | four of twenty-three |
| no folders are proposed | the 208-row template catalogue | school, term, subject, work_type | `subject` |
| your own folders ignored | the branch picker | existing folders as candidates | offered, then discarded |

This is why the product's behaviour is identical for a litigator, a student, a parent and a person
who is all three: **none of the differences between them survive the front door.**

---

## 3. Why the test suite never caught any of this

5,234 tests pass, in fixed and randomised order, and they have been green through every defect
described here and in `70`. That is not an indictment of the tests; it is a fact about what they
test.

Every one of these defects has the same shape:

| defect | side A, correct | side B, correct | the seam |
|---|---|---|---|
| empty neighbourhood (fixed today) | `cli.py` writes `scan_state="scanned"` | P9 admits `"included"` | one word |
| nothing classifies (this document) | the detector demands corroboration | the extractor emits identifiers | two vocabularies |
| nothing classifies, part 2 | recognition names a schema | the handling map covers 4 of 23 | a mapping's coverage |
| command crashed on rerun (fixed today) | the store refuses a changed record | the clock changes every run | a timestamp |
| one course, four groups (fixed today) | the group id is an address | the address was the file | what the address was OF |

**A part's tests are written in that part's own vocabulary, so they agree with the part.** Both sides
pass. The seam is what fails, and nothing owns a seam.

Every one of these was found by **pointing the command at a folder and reading the output.** None was
found by the suite. That is the single most reusable fact in this document.

---

## 4. The FileGraph critique's nine findings, scored against this machine

| # | its finding | lands here? | what is actually true |
|---|---|---|---|
| 1 | research journal, not a spec | **YES** | `planning/` is 71 numbered documents in which later ones supersede earlier ones. Managed by banners and handoffs, but a newcomer still reconstructs current truth from a debate. §5 proposes the fix. |
| 2 | "existing folders are the label space" vs 96% proposals | **being measured** | `00` says the top level is built from accepted groups, existing folders and user labels. Whether the shipped command uses existing folders at all is under audit; the CLI appears to pass none. |
| 3 | two incompatible tier numbering schemes | **no** | one analysis-tier vocabulary (`filesystem/native/ocr/llm`), used consistently. |
| 4 | override vs multi-value indistinguishable | **partly** | `file_facts` has no uniqueness on `(file_id, content_hash, field_key)` — the same shape. But it carries `active`, the supersede columns and `preferred`, and `proposal_eligible` filters two of the three. Under audit; the open question is whether `preferred` is inert. |
| 5 | session edges are both the best signal and the worst | **no** | already answered by design: the bounded-session channel is retrieval-only and may never anchor a group. P9's anchor bar is narrower than P6's proposal bar for exactly this reason. |
| 6 | thresholds not tagged by evidence class | **YES** | every number is chosen in one file with a stated reason, which is better than the critiqued project — but the reasons are of different kinds and are not distinguished. Under audit. |
| 7 | the model's evidence packet is not capped | **probably no** | `max_dossier_tokens`, `max_candidate_members` and `max_excerpt_characters` are all injected ceilings. Under audit for a gap. |
| 8 | engine and product layer don't name their shared interface | **YES, hard** | this is exactly the P12/P13/Find/onboarding gap. Under audit; the seam inventory is the deliverable. |
| 9 | decisions locked before their evidence | **YES, mildly** | same class as 1. |

---

## 5. What to do, in order — and why it is small

**The anti-overbuilding argument, first.** Four symptoms, one cause, means this is **one change of
shape at the composition root**, not four projects. Nothing below adds a part, a table, a threshold
or an abstraction. Every fix is the deployment supplying something the parts already ask for and
already know how to consume. The parts are not touched.

### Step 1 — let the product see the words in the document

Emit the readable text of a file as observations. Verified above: the locator is `body:field=prose`,
the deployment's direct slot returns `False` for it, so **this does not widen what a folder can be
named after.** Cost: one reader change. Effect: recognition starts working on every file.

Guardrails that ship with it, or it is a privacy regression:
- the observation stays local, exactly as filename and path observations already do;
- a test pins that a prose observation does **not** become a `subject` fact;
- protected containers are untouched — nothing inside one is read, enforced by path before this.

### Step 2 — give the ordinary schemas a handling class

One table. `SAFETY_DOMAIN_HANDLING` covers four safety schemas and marks them protected, correctly.
The other nineteen need an ordinary class so a recognised file can be classified at all.

**This unlocks step 3 for free**, which is the part worth noticing: while the schema has no class,
`explain()` returns an `Abstention` and the term matches it computed are **not published**. Once a
class exists it returns a `Recognition`, which carries `matches` — each with the term and the
observation key that evidences it. So step 2 turns already-computed work into usable output.

**Joseph's ruling needed:** which class ordinary material gets. It is a mechanism.

### Step 3 — get a second folder level from work already done, not from a new extractor

The tree needs more than one dimension or every template collapses. The tempting fix is to author
more extractor slots — more regexes, more fields, more decisions about what to read. **Do not.**

The recognition pass **already** matches authored `work_type` terms per schema (96 for `academic`
alone: `syllabus`, `assignment`, `transcript`, `certificate`) and already returns, per match, the
term and the observation that carries it. That is a `work_type` fact with its evidence attached,
computed on every run today and thrown away.

Wire recognition's matches into P6 as facts, at a reliability the evidence supports. Result:
`subject` + `work_type` → two settled levels → `Coursework / PHYS1401 / Syllabus`. No new extractor,
no new vocabulary, no new threshold.

### Step 4 — stop discarding the folders the person already made

The branch picker is offered every existing folder and chooses none, and no code can write a node of
type `existing`. Two things are needed and only the first is code: a selection path that can keep an
existing folder, and a ruling on when it should. **Joseph's ruling needed:** does an existing folder
the person made outrank a proposal, always, or only when it holds enough files?

### Step 5 — re-run the four personas

`68`'s corpora, re-run after steps 1–3. Minutes, and it is the only measurement that says whether a
person is now served. **Do not skip it and do not replace it with the test suite** — every defect in
this document was invisible to 5,234 passing tests.

### Step 6 — the three defects that stand on their own

Not caused by the root cause, each small, each already located:
- `preferred_fact` counts rows rather than distinct values, so **two producers that agree delete the
  file's folder level**;
- the standing protection rule covers one file extension (`.app`) and the deployment supplies no
  widening predicate — **Joseph's ruling needed** on the list;
- five of nine `completeness` values are unreachable, so a file that could not be read is recorded
  as read-and-empty — **Joseph's ruling needed** on which value a text-less document gets.

### Step 7 — then, and only then, the review screen

With classification and two levels working, `68`'s remaining finding is real: the shipped command
merges every group because there is nobody at the screen. That is P13, planned and unbuilt. It is
step 7 and not step 1 because a review screen showing today's output would show one folder and four
unclassified files.

### What is deliberately NOT on this list

- No new part, table, threshold or abstraction.
- No widening of what becomes a folder name beyond the one dimension step 3 adds.
- No changes to P1–P11 contracts.
- No work on Find, filing or onboarding — `66` §22 sequences those after this, and none of them
  improves while the front door starves the machine.

## 6. The structural gap: work with no owner

Everything in `66` — Find, filing policies, onboarding questions — has a design, a release order,
and **no part number**. Work without a part number in this project has no SPEC, no PLAN, no tests
and no gate, which is why it has stayed unbuilt while P12 and P13 got 17,000 lines of plan.

The proposal is in §7 and is the thing Joseph should rule on first.

---

## 7. Proposed: the parts that do not exist yet

| | part | owns | why it is its own part |
|---|---|---|---|
| **P14** | **Find** — local, read-only retrieval | the text index, query matching, the six location states of `66` §3, the five distinct no-result states of `66` §4-§5, protected-present-not-absent, and the unlock | `66` §22 ships it FIRST, and it is the only capability a person can use having granted no authority at all. It needs a text index, which nothing in P1–P11 provides. |
| **P15** | **the structural-question registry** — onboarding | the question record, its trigger condition, the decision it unblocks, its scope, the structural-versus-contextual split of `66` §13, revocation, and the plan-version effect of `66` §17 | `66` §12 is explicit that this is "a significant product and engineering workstream", not a screen. It is consumed by templates, schemas, privacy, tree design, placement and filing — six parts — so it cannot live inside any one of them. |
| **P16** | **filing policies** — the "File" half of `66` | the nine policy dimensions of `66` §8, the dry run, progressive authorisation, the activity list | P12 owns *moving a file safely*; this owns *whether this file may be moved at all, under whose authority*. `66` §7 calls it the most dangerous capability in the product, and P12's plan already flags that it is being asked to own a corpus-wide undo period that `66` §8 says belongs to a policy. |

**And the repairs are not a part.** Steps 1, 2 and 5 above are fixes to P5/P6/P7's deployment and to
P3's protection list. Giving them a part number would make a permanent home for what should be a
short, closed list of corrections. They belong in a repair plan with a gate, not in the part
numbering.

**This section is a proposal and nothing has been built from it.** The part boundaries are the thing
to rule on: they decide what gets a SPEC, and a SPEC is what makes work real in this project.

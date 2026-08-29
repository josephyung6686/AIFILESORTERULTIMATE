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

## 5. What to do, in order

Ordered by what unblocks the most for a person, not by what is most interesting.

### Step 1 — give the detector the words (small, safe, unblocks everything)

Emit the document's readable text as observations under a locator the deployment's direct slot does
not claim. **Verified above to reach the detector without becoming folder names.** This is a change
to what the composition root supplies, not to any part's contract.

Guardrails that must come with it, or it is a privacy regression:
- the observation stays local, exactly as filename and path observations already do;
- the direct slot's `names` predicate stays narrow, and a test pins that a prose observation does
  not become a `subject` fact;
- protected containers are unaffected — nothing inside one is read, and that is enforced by path
  before any of this.

### Step 2 — give the ordinary schemas a handling class

`SAFETY_DOMAIN_HANDLING` covers the four safety domains and marks them protected. The other
nineteen need an ordinary class so that a recognised file can be classified at all. **This is a
deployment policy and a mechanism, so it wants Joseph's approval rather than an agent's invention** —
but it is one small table, and the recognition side is already correct.

### Step 3 — re-run the personas

`68`'s four corpora, re-run after steps 1 and 2. This is the measurement that says whether the
product now does its job, and it costs minutes.

### Step 4 — the review screen, which is the next wall

Even with classification working, `68` F3 stands: the shipped command **merges every group into one**
because there is nobody at the screen to review them, so the tree is one folder deep. That is P13,
and it is planned but unbuilt.

### Step 5 — the two safety findings from `70`

The standing rule protects one file extension (`.app`), and five of nine `completeness` values are
unreachable so a file that could not be read is recorded as read-and-empty. Both are one-line
changes once the values are chosen, and both choices are Joseph's.

### Step 6 — split the planning corpus

Adopt the FileGraph critique's first fix, which lands here: one **frozen decisions** table that
states the current answer once, with a pointer to the document that earned it, and the numbered
documents kept as the evidence appendix. `69` and `70` are already close to this; the missing piece
is a single index that says, per subsystem, what the current answer is.

---

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

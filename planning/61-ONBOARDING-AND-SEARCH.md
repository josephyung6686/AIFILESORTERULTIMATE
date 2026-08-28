# 61 — §4.5 Corpus role declaration (onboarding), and the search surface

Date: 2026-08-28. **Approved by Joseph, this session.** Two additions to `00`, both argued
in `planning/59-FINAL-UX-EVALUATION.md` §6.1 and §6.2, both ratified here with his framing.

Authority: `00-database-agent-product-design.md` remains canonical. This document AMENDS it
with the owner's explicit approval; where it and `00` conflict on anything not stated here,
`00` still wins.

---

## Part A — §4.5 Corpus role declaration

### A.0 Joseph's framing, verbatim

> *"Yes we should ask a little about the user, like maybe an onboarding guide — like it asks
> your age range, if you have kids or something, what your profession is and what's your
> purpose of using. We use that for everything else and the intention and stuff."*

That is broader than `59` §6.1's "role declaration" and the broadening is right: it gives the
mechanism a front door a person recognises. An onboarding guide is a thing users already
understand; a "corpus role declaration" is not.

### A.1 The problem it exists to solve

`00` derives everything from files, and §4's stop rules correctly abstain where a role is
unevidenced. But four of the hardest cases in the product **are not in the files at all**:

- Is this course one you **take** or one you **teach**? (`canonical_fields.json` collapses both
  into `school`, deliberately)
- Is this lease **yours** or your **client's**?
- Is this résumé **yours** or a **candidate's**? — where the wrong answer is a *privacy*
  failure, not a tidiness one
- **Which of your two children** is this about?

Every one is a fact about the **person**, not the file. Every one is answerable in one
question. Because `00` provides nowhere to ask and nowhere to store the answer, the product
abstains on the entire professional and multi-life half of a real disk — **correctly, by its
own rules, and uselessly.**

`53` §3 reached a narrower version (a corpus-share threshold flipping `legal` between a drawer
and a matter tree) and `53` §7.6 proposed it as a first-run question. The general form is
stronger and cheaper. It is also the input that makes `subject_of_record` safe to make
destination-eligible for a parent and unsafe for a lawyer — **exactly the decision `49` §2.4
correctly refused to make unilaterally**, because nothing in the corpus could settle it.

### A.2 Where it sits

**Between grouping (P9) and tree design (P10).** Not at install, not before the scan: the
questions are cheaper to answer and easier to trust when the user has already been shown what
was found. It runs once per corpus and is re-openable.

### A.3 The two kinds of answer, and why the distinction is load-bearing

**This is the core of the design. An answer is either STRUCTURAL or CONTEXTUAL, never both.**

**STRUCTURAL answers may gate a decision.** They resolve a role inversion or an eligibility
question that no evidence can settle. They are stored as **user-confirmed corpus facts**, carry
`basis: "user"` (already a live `CLASSIFICATION_BASES` member alongside `detector` and
`safety_domain`), and outrank an inferred fact of any reliability — `00`'s existing rule that a
user correction supersedes.

**CONTEXTUAL answers may only inform interpretation.** They are a prior for what to surface
first and context a P8 prompt may carry. **A contextual answer must never silently gate a
structural decision.** If age range ever decides whether a folder level exists, that is a
defect, not a feature — because the user was never told it would, and cannot see it happening.

The failure this separation prevents: a person answers a friendly onboarding question and,
three screens later, a folder they expected is missing with no explanation reachable. That is
the same harm as a silently omitted protected area, arriving through a nicer door.

### A.4 The questions

| # | question | kind | what it may do |
|---|---|---|---|
| 1 | **What do you do?** (multi-select, free text allowed; "or I am multiple" is the normal case, not an edge case) | **STRUCTURAL** | Activates schemas. Resolves `school` take-vs-teach, `our_firm`↔`client`, `employer`↔`target_employer`, `subject_of_record` self-vs-other. |
| 2 | **Does anyone else appear in your files?** (e.g. children, dependants, clients — names optional) | **STRUCTURAL** | Makes `subject_of_record` destination-eligible **only** when the named others are the user's own dependants, and supplies the values. Never eligible for third parties — a folder named for a client or an employee discloses membership (`60` §2, J-5). |
| 3 | **What are you here to do?** (find things again · tidy up · archive · not sure) | **STRUCTURAL for depth, CONTEXTUAL otherwise** | *Find things again* means the search surface (Part B) is the product and no move need ever be proposed. |
| 4 | **Age range** (optional, skippable) | **CONTEXTUAL ONLY** | A prior on which schemas to surface first, and context a P8 prompt may carry. **Gates nothing.** Skipping it changes no tree. |

**Every question is skippable and the product must work with all four skipped** — that is the
`00`-conformant baseline it has today. Onboarding only ever *adds* resolving power.

### A.5 Bounds — what it may never do

Carried verbatim in spirit from `59` §6.1: *"explicitly bounded so it cannot invent schemas or
dimensions, only resolve role inversions and eligibility."*

1. **It may not invent a schema.** `SCHEMA_IDS` stays a closed vocabulary; an answer selects
   from it or is recorded as unmatched. §3.12's rule stands: values may auto-create, fields and
   schemas may not.
2. **It may not invent a dimension or a field key.** Answer 2 supplies *values* for
   `subject_of_record`; it does not mint a key.
3. **It may not lower a privacy floor.** Onboarding can make a level eligible; it can never
   make protected material placeable. The standing rule is untouched: a protected container is
   **marked and counted, never opened**, and never silently omitted.
4. **It may not act unconfirmed.** Every stored fact is user-confirmed and re-openable, and the
   user can see what each answer changed. An answer that quietly rewrote a tree the user could
   not trace is the defect this whole design exists to avoid.
5. **A contextual answer may not gate anything.** §A.3.

### A.6 Privacy — question 2 needs care, and the care is specific

Question 2 collects **names of other people, including children.** That is the most sensitive
input the product ever takes, and it is taken from the user rather than extracted from a file.

- Stored as ordinary corpus facts under the same P7 protections as extracted personal data,
  never egressed by default (`00`: *"Protected material should not be included in cloud-model
  prompts by default"*).
- **Dependant names may become folder levels; third-party names may not.** The discriminator is
  question 1's answer, which is why the two questions are one mechanism.
- The question is skippable, and skipping it returns the product to today's behaviour: abstain
  on which-child, file by whatever else is evidenced.

---

## Part B — The search surface

### B.0 The finding

`59` §6.2: **`00` builds a retrieval index and never lets the user search it.** Every file is
already scored against every candidate folder, with suppression, margins and a two-condition
verdict. All of it exists so files can be **moved**. For several of the personas tested, the
thing that would change their week is *find it again*, not *reorganise it*.

### B.1 Ruling

**Ship read-only search first.** It is usable with **no P12 (apply/undo) and no P13 (review
canvas)**, and it is the shortest path to something a real person can run on their real disk.
It reads the index that already exists; it writes nothing and moves nothing.

### B.2 Contract

- **Read-only.** No file is moved, renamed, or written. No tree is frozen.
- **Answers show every home, not the best one.** The two-home case is the normal case, and
  `59` §3a is explicit that reporting a genuine tie as low-confidence is the wrong sentence.
- **Protected areas appear in results as present-but-unopened, counted, with a reachable
  explanation** — never silently absent from a result set. The standing constraint applies to
  search exactly as it applies to the tree.
- **An abstention is a result.** "I found this and declined to place it, because it is a
  passport" is an answer, not a failure. `00`: *"sensitive personal material is not the same
  thing as `Numbers.app`."*
- **It reuses P11's scoring**, and does not fork a second ranking. Two rankings would be two
  products.

---

## C. What this document does NOT settle

- The onboarding surface's visual design. This is the contract; the UI is `P13`'s.
- Whether question 1's profession list is closed or free text with a matcher. **The matcher is
  the interesting problem** — it must map free text onto `SCHEMA_IDS` and record an unmatched
  answer honestly rather than snapping it to the nearest schema, which is `00`'s abstention
  rule applied to a person instead of a file.
- Re-running onboarding after the tree is frozen. §8.8's versioning governs; the interaction
  is unexamined.

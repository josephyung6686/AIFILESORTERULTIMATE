# 68 — G10, the persona re-run

Date: 2026-08-29. `63` §0's tenth gate: *"the persona re-run — `59`'s persona evaluation redone
against the current state."* `67` §4 calls it "the north star condition… The other nine measure
whether the machine works. G10 asks whether a person can use it."

**Method, and how it differs from `59`.** `59` could not report what a person sees, and said so in
its own first section: there was no CLI, no caller for `run_corpus`, and *"the product's questions
are currently error messages."* That is no longer true. So this document does not read the code and
infer an experience — **it runs the shipped command over four corpora on disk and writes down what
came out.** Every quoted line below is real output; every count was queried from the plan database
the run wrote. Where a claim is about code rather than a run, it says so.

The four corpora are `59`'s own three people plus the one `59` §2 says every persona document
assumed away.

| | who | corpus | flags |
|---|---|---|---|
| Mara | litigator | motion, deposition, privilege log, e-filing receipt, a client's passport | `--situation law_practice.discovery --label Matters` |
| Priya | PhD student who TAs | her PHYS1401 problem set and notes; the PHYS2801 solution set and rubric she wrote for her students | `--situation academic.coursework --label Coursework` |
| Tom | two-child household | Ada's report card, Sam's report card, a lease, an insurance claim | `--situation finance.household-property --label Household` |
| all three | one person, three lives | the union of the above, 13 files | `--situation academic.coursework --label Coursework` |

---

## 1. What has genuinely changed since `59`

Stated first, because four of `59`'s structural complaints are answered and a re-run that buried
that would be as misleading as one that claimed the rest were fixed.

1. **There is a product to run.** `59` §0: no `[project.scripts]`, no caller for
   `horizontal_candidates`, `vertical_options` or `run_corpus` anywhere in `src/`, eighteen
   `RuntimeError` classes and no function that *offers* a choice. `src/cli.py` and
   `production.run_production_corpus` now compose P1–P11 into one command, and it prints a report
   in sentences rather than raising at the caller.
2. **`law_practice` exists at runtime.** `59` 1a's central finding — ten flat schema ids, four of
   them with zero fields, no `law_practice` at all — is gone: `--list-situations` prints **208**
   situations, including `law_practice.discovery`, `.depositions-testimony`, `.privilege-review`
   and eighteen more. Mara's situation is now nameable.
3. **The standing rule is something a person reads.** Every run leads with the protected containers,
   by count, by name, by path, and with the sentence *"Nothing inside these was read, indexed,
   classified or moved, and none of them is a place anything can be filed."* `65` §1 recorded this
   arriving; it held on all four corpora here.
4. **One course is one group** (commit `53c41d1`, today). `65` §4.2's four-singletons defect and the
   `scan_state` seam beneath it are fixed, and the fix shows up in these runs: Priya's two courses
   are two groups of two, not four groups of one.

---

## 2. What every persona actually got

The four runs are more alike than the four people are, and that is the finding.

| | files | folders proposed | ready to file | what the person is told |
|---|---|---|---|---|
| Mara | 5 | 1 (`Matters`) | **0** | "Waiting for you to say what these are — 5 files" |
| Priya | 4 | 1 (`Coursework`) | **0** | same, 4 files |
| Tom | 4 | 1 (`Household`) | **0** | same, 4 files |
| multi-life | 13 | 1 (`Coursework`) | **0** | same, in two sets of 8 and 5 |

Four people, four disks, one outcome. Nothing was misfiled and nothing was lost — the product is
honest at every step — but nobody got an organisation, and nobody got a single file placed.

---

## 3. The findings, in the order they hurt

### F1 — No classifier ships, so every file for every person stops at the same sentence

**Blocking, and it is the whole experience.** 26 of 26 files across four corpora came back:

> *"This file has not been classified — nothing has yet said what kind of material it is — so it was
> not shown to a model and nothing moved. It is waiting for you to say what it is, not marked
> sensitive and not judged on thin evidence."*

The database agrees and says which step stopped: `file_facts` holds a `direct` fact for every file
and `classifications` holds **zero rows** in all four databases. Reading worked. Classification
declined, correctly, because no detector is supplied and P7 refuses to default an absent
classification to a public class.

This is `65` §2.2's sizing question — a 5,072-term recognition vocabulary on one side, a
deployment feeding P4 from one regular expression on the other — and `65` records it as **the
owner's call**, deliberately open. What this re-run adds is the price: it is not one persona's
problem or an edge case, it is the terminal state of the product for **everyone**, and no other
improvement is visible to a user until it is decided.

### F2 — One extractor slot makes every person's material academic

The deployment writes exactly one direct fact, `cli.text.identifier → subject`
(`src/cli.py`, `DIRECT_SLOTS`), and `subject` is an academic field. So on real corpora:

| the file | the identifier | the fact the product holds |
|---|---|---|
| Mara's motion to compel | `CV20261234` | `subject = CV20261234` |
| Tom's insurance dispute | `CLM88213` | `subject = CLM88213` |
| Tom's lease | `PR20264410` | `subject = PR20264410` |
| a client's passport | `X12345678` | `subject = X12345678` |

Because `group_category` is the domain the anchoring field belongs to, **every engine group in all
four databases came out `academic`** — the litigator's matter, the household's insurance claim and
the property reference included. For the multi-life person, three lives arrive as one category.

`cli.py` declares this posture and its reason honestly (*"A wider pattern would put more of the
file's text into P4's observations, and a first run on somebody's disk is not the place to widen
what gets read"*). It is defensible for a first run. It is also why `--situation` is doing all the
categorising work, and why one flag per run is not enough for a person with more than one life
(F6).

### F3 — The tree is one folder for everyone, because the non-interactive review merges every group

This is the largest user-visible defect and it is a **deployment** defect, not an engine one.

`review_and_accept` (`src/cli.py`) is the stand-in for the review screen, and it says what it does:
*"the review screen, non-interactively: keep everything, as one named group."* It takes every group
P9 formed, merges them into a single group under `--label`, categorises it from `--situation`, and
accepts that one. P10 then has exactly one accepted group to build a branch from, so the tree is one
folder deep, every time, for every corpus.

The engine's own records are better than that. Measured, in the same databases:

| | groups P9 formed | what the person was shown |
|---|---|---|
| Priya | `PHYS1401` (2 files), `PHYS2801` (2 files) | one folder, `Coursework` |
| Mara | `CV20261234` (4 files), `X12345678` (1) | one folder, `Matters` |
| Tom | `SPRING2026` (2), `CLM88213` (1), `PR20264410` (1) | one folder, `Household` |
| multi-life | `CV20261234`, `PHYS1401`, `PHYS2801`, `SPRING2026` | one folder, `Coursework` |

**Verified by experiment, not by argument.** Patching the review to accept each engine group as
itself and re-running Priya's corpus produced:

```
Proposed folders: 2. 2 of them are somewhere a file can go.
  PHYS1401
  PHYS2801
```

— which is the structure a person would expect, and which the shipped merge discards. The patch was
reverted; it is not a proposed fix, because it also **drops the branch name the user asked for**
(`Coursework` disappears entirely) and it is not this command's place to decide whether a person's
two courses are two top-level folders or two children of one.

That decision is a review screen, and the review screen is **P13**. So: until P13 exists, no
deployment default can produce a tree better than one folder without inventing the user's answer.
This is independent evidence for `66` §22's sequencing, and it is why the merge should not be
"fixed" in `cli.py` by a session with nobody to ask.

### F4 — A passport number became a group label, and would become a folder name

Mara's corpus produced a group whose `display_label` is **`X12345678`** — the passport number
printed in a client identity document. Under the shipped merge it stays inside the database. Under
the per-group experiment above, Mara's run printed:

```
Proposed folders: 2. 2 of them are somewhere a file can go.
  X12345678
  CV20261234
```

**A folder named after a passport number.** Two gaps compound to produce it: nothing classified the
file as protected (F1), and nothing anywhere says that an identifier lifted from an identity
document may not name a folder. `66` §4 is the governing sentence — *"even 'Identity' may say more
than the user wants"* — and §15 already prohibits person-shaped folders for clients and patients on
exactly this reasoning: a folder name is a disclosure to everyone who can see the disk.

**This must be closed before anything materialises a folder from a group label.** It is upstream of
P12 (which composes paths) and belongs in P13's review contract (which is where a label is
approved).

### F5 — Still true: no field names the child

`59` 1c found it and it is unchanged. Tom's two report cards carry the same school and the same
term, so they anchored on `SPRING2026` and became **one group of two files**. The product cannot say
that one is Ada's and one is Sam's, because no field names a person in a way a destination may use
(`people` exists and is `destination_eligible=False`, correctly).

The one thing Tom would ask for first — a folder per child — is the one thing the engine cannot
express. `66` §15 is where it belongs: names collected only inside a deliberate protected-family
workflow, with a user-selected relationship category, and person-shaped folders permitted for a
dependant whose records the user manages. None of that is built, and `66` §21 lists it as design
work owed. **No code should guess at it in the meantime**, and none does.

### F6 — Priya's two lives now separate, and one flag still mislabels half her disk

An improvement worth recording: her PHYS1401 material and the PHYS2801 solution sets she wrote for
her students formed **two distinct groups**, where `59` 1b found them landing in one folder. The
grouping fix (F3's table) is why.

What remains is above the engine. `--situation` is one value for the whole run, so her whole corpus
is `academic.coursework` — including the material that is `academic.teaching`, a situation the
shipped library now carries. The marking-integrity problem `59` named is therefore still reachable:
nothing marks the solution set as material that must not sit beside student submissions. This is
`66` §13's structural-versus-contextual question in its sharpest form — *which* of her two roles a
file belongs to is exactly the sort of thing evidence cannot safely decide and a narrow,
evidence-linked question can.

### F7 — The multi-life run split its review into two blocks, and the reason is a ceiling

The 13-file run printed two blocks:

```
  Waiting for you to say what these are -- 8 files
    ... Held for review as "Not yet placed (1 of 2)": no destination in this tree
    matched them well enough to decide without asking you.

  Waiting for you to say what these are -- 5 files
    ... Held for review as "Not yet placed (2 of 2)": no destination in this tree
    matched them well enough to decide without asking you.
```

**Correction, recorded rather than quietly edited.** The first version of this section reported the
cause as two placement passes each returning their own set. That was wrong, and the database says
so: `residual_sets` holds `version_2:Not yet placed-1` and `-2`, and
`residual.max_files_per_review_batch` is **8**. Thirteen unplaced files, a review batch bounded at
eight, so 8 + 5. `residual.py` is explicit about why it splits rather than shortens — *"Split, never
truncate: §8.6 reduces work and never drops files"* — and that is `00` §8.6 working, not failing.

So this is not a defect. What remains is a small legibility question: `(1 of 2)` is honest but does
not say that the person's review was divided into batches, or why the batch is eight. A person
reading it can reasonably think the product found two different kinds of problem. One clause would
settle it — *"your review is split into batches of 8"* — and it belongs with P13's `progress_line`
rather than in this command.

---

## 4. What went right, stated once and specifically

- **Nothing was misfiled anywhere.** Across 26 files and four corpora the product placed nothing it
  could not justify, invented no destination, and moved nothing. `00`'s residual principle — a
  plausible-sounding wrong destination is worse than an honest unsorted item — held under every
  run.
- **The protected bundle was marked, counted, named and explained** on the corpus that had one, and
  a query for its interior text returned zero rows.
- **The refusals are legible.** A person reading the report knows what stopped, that nothing moved,
  and that the product is waiting on them rather than confused. That is the difference between
  abstaining and failing, and it survived four corpora.
- **The engine refused to mislabel when pushed.** The per-group experiment tried to write a category
  onto a group whose coherence verdict was not `coherent`, and `MalformedGroupRecord` stopped it:
  *"display_label and group_category are set only when coherence_verdict is 'coherent'; an
  uncoherent group carries no label rather than an empty one."* The invariant did its job against a
  caller doing something careless.

---

## 5. Verdict on G10

**G10 does not close, and it should not be recorded as closing.** A person cannot yet use this
product to organise their files: every persona ends with zero files ready to file and a one-folder
tree.

But the gate now fails for **three enumerable reasons with owners**, where `59` found a product that
could not be run at all:

| | what blocks a usable outcome | whose it is |
|---|---|---|
| 1 | No classifier ships, so every file stops unclassified (F1) | **Joseph** — `65` §2.2's sizing question, open by decision |
| 2 | The non-interactive review merges every group, so the tree is one folder (F3) | **P13** — a review screen is the answer; no default can substitute |
| 3 | An identifier from an identity document can name a group and would name a folder (F4) | **P13 + P12** — must close before any folder is materialised |

F7 was reported as a fourth and withdrawn on the evidence: the split is `00` §8.6's review-batch
ceiling doing its job. The withdrawal is left in §3 rather than deleted, because a re-run that
silently drops a claim it made is not a record anyone can check.

F5 (no field names the child) and F6 (one situation per run) are real and are `66` §15 and §13
design work already owed, not implementation gaps.

**The shortest path to a person getting value** is unchanged from what `66` §22 already sequences,
and this re-run is independent evidence for it: F1 is a decision, and F3 is the review surface. Find
— local, read-only, nothing moved — is reachable *before* either, which is exactly why `66` puts it
first.

---

## 6. What this re-run adds to the record

Two things `59` could not have found, because they only appear on a real run:

1. **Every persona ends in the same place.** The differences between a litigator, a student, a
   parent and a person who is all three are invisible in the output, because the one blocking cause
   is upstream of everything that distinguishes them.
2. **The engine's records are now better than the report shows.** Before today's grouping fix the
   merge was hiding four identically-named singletons — arguably an improvement on what lay beneath
   it. It is now hiding four correct, distinct, populated groups. **The value of building P13 went
   up today**, and it went up because the layer under it started telling the truth.

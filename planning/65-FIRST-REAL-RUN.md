# 65 — The first run on a real directory, and the one thing it found that no test could

Date: 2026-08-29. Not an audit and not a plan: a record of pointing the shipped command at
an actual folder on an actual disk and writing down what happened.

```
python3 src/cli.py demo --situation academic.coursework --label Coursework
```

Five files: four coursework documents and one inside a `Notes.app` bundle.

---

## 1. What it did

```
Protected containers: 1 marked, none opened
  Notes.app  (untouched_protected)
  Nothing inside these was read, indexed, classified or moved, and none of them
  is a place anything can be filed.

Plan version_2: 2 folders, 1 of them places a file can go
  Coursework
  Notes.app   [marked, not a destination]

Files: 4 decided, 0 placed
```

**The standing rule is now something a person reads rather than something a test asserts.**
Marked, counted, explained in plain words, and named as not-a-destination. Confirmed in the
database: `exclusion_verdicts` holds one row with `label = untouched_protected`, and a query
for the bundle's interior text returns **0**.

`group_category`, `display_label` and `coherence_verdict` are all written on a live run —
`academic` / `PHYS1401` / `coherent` — which is what makes the 208-row catalogue reachable at
all.

---

## 2. Two findings the suite could not have produced

### 2.1 The corpus that could not be read, and why that was correct

The first attempt produced `NothingToDesign` and **the fault was the corpus, not the product.**
The files said `PHYS 1401`; the deployment's one structured-string pattern is
`\b[A-Z][A-Z0-9]*[0-9]{3,}\b`, which wants `PHYS1401`. No match, no fact, no group, no tree.

Worth recording because the failure was *legible*: a named refusal citing §5.3 and stating what
a top-level branch is built from. A person could act on it. That is the difference between
abstaining and failing, and it held on the first contact with reality.

### 2.2 The detector and the extractor were sized by different passes and never against each other

**This is the finding, and it is `00`-level rather than a bug.**

`src/recognition/` compiles **5,072 context terms** and 3,835 work-type terms out of the 358
research rows — "problem set", "syllabus", "office hours", "Columbia University". That is the
vocabulary the product uses to decide what a file is.

The deployment feeds P4 observations from **one regular expression**. `cli.py` says so, and
says why:

> *"ONE, and deliberately narrow: an identifier token — letters then digits, like PHYS1401 —
> which is §2.2's own 'identifiers' class. A wider pattern would put more of the file's text
> into P4's observations, and a first run on somebody's disk is not the place to widen what
> gets read."*

That is a defensible privacy posture and it is honestly declared. **Its consequence is that the
detector has almost nothing to match against**, so it declines, so every file comes back:

> *"This file has not been classified — nothing has been able to read enough of it to say what
> kind of material it is — so it was not shown to a model and nothing moved. It is waiting for
> you to say what it is, not marked sensitive and not judged on thin evidence."*

Four files, four abstentions, on a corpus that is unambiguously coursework to any human reading
it. **Nothing is broken. The two halves have simply never been sized against one another** —
one pass researched a 5,072-term vocabulary, another chose one pattern, and no test compares
them because each is correct on its own terms.

**This is the question `63` §0's G10 exists to surface**, and it surfaced on the first real run
rather than in any of 5,100 passing tests.

It is genuinely open, not merely unfixed. Widening the extractor trades privacy posture for
recall on a first run. Narrowing the detector wastes the research. Leaving it means an offline
deterministic run abstains on nearly everything and the product's honesty becomes its main
visible behaviour. The third option is the one `62` §A already argues: **ask the user**, which
is what `--situation` is already doing and what the role declaration would extend. Whichever
way it goes, it is the owner's call and it should be made deliberately rather than inherited.

### 2.3 Smaller, and worth a look

Four files carrying the same `PHYS1401` became **four groups**, each `strongly-identified-file`,
rather than one group of four — same category, same label. `00` warns about "a large number of
tiny folders" at the tree; this is the same shape one layer earlier, at grouping.

---

## 3. What this run does not show

- Nothing was moved, because nothing moves: P12 does not exist.
- One corpus, five files, one situation, offline mode. It is an existence proof, not a
  measurement.
- The persona work `59` did — a lawyer, a parent, a researcher, someone who is several at once —
  is still owed, and this run is one file-shape against one of them.

---

## 4. Second run, 2026-08-29 — after the output was made readable

`fix-cli-output` (commit `bb898ce`) landed and the same corpus was run again. The four defects
§3 recorded are gone: names instead of UUIDs, one reason for four files instead of four copies
of it, the plan version demoted to a self-explaining footnote, and the review set folded into
the block whose files it covers rather than counted a second time in its own vocabulary.

Two findings came out of the second run that the first could not produce, because the first
run's output was too unreadable to notice them.

### 4.1 The refusal describes the one step that worked

The report says, for all four files:

> *"This file has not been classified — nothing has been able to read enough of it to say what
> kind of material it is."*

The database says otherwise:

| table | rows | meaning |
|---|---|---|
| `file_facts` | **4** — one `subject` per file, all `direct` | **reading worked** |
| `classifications` | **0** | the detector declined |
| `placement_decisions` | 4, all `abstain`, `node_id` NULL | placement had no class to route on |

Extraction is the step that succeeded, and it is the step the sentence blames. The honest
sentence is that the file was read and **not classified** — P7's detector abstained, correctly,
under the rule that an unrecognised file must reach P11 unclassified rather than be written up
as something it is not (commit `6be2ada`).

**`66` §4 already forbids this.** "Protected," "unreadable," "unsupported format," "still
indexing" and "no strong match" are five states that *"should never share one vague message."*
This is two of them sharing one: an **unclassified** file described as an **unreadable** one.
The requirement was written for Find; it applies to this report today.

### 4.2 Four files from one course became four groups — §2.3's question, answered

`65` §2 left open why four files sharing `PHYS1401` did not become one group. The grouping rows
answer it:

```
group:e46ba371-…:strongly-identified-file   academic   PHYS1401   coherent   engine
group:84d59bfc-…:strongly-identified-file   academic   PHYS1401   coherent   engine
group:96020a5e-…:strongly-identified-file   academic   PHYS1401   coherent   engine
group:9db8361f-…:strongly-identified-file   academic   PHYS1401   coherent   engine
```

**Every group id is keyed on a FILE id**, and the strategy is `strongly-identified-file`. A file
that identifies itself strongly enough becomes its own group. Four files that each strongly
identify as PHYS1401 therefore produce four one-file groups carrying the same `display_label`,
rather than one group of four. `memberships` holds 8 rows for 4 files: each file is in its own
singleton and in the plan's `Coursework` group.

This is why `Coursework` is proposed and then left empty, and why all four placements abstain.

**It is a north-star defect, not a cosmetic one.** A person with four files from one course
expects one course folder containing four files. They are shown four identically-named groups
and an empty folder. And it is upstream of everything: `66` §3's six-state model — current
location, filed home, also-related-to, shared-material, historical, possible placement — has
nothing to present if the engine cannot say that four files belong to one course in the first
place. Find inherits this, it does not fix it.

The strategy is not wrong in general: a strongly self-identifying file *should* be able to stand
alone when nothing else shares its identity. The defect is that the strategy does not check
whether anything else resolved to the same identity before minting a singleton for it.

### 4.3 What this changes about the order of work

`63` §5's list has "widen the extractor" at step 5. §4.2 above should sit next to it, because
they are the same class of problem seen from two sides: the product's understanding of a course
is assembled from a course code, and both the reading of that code and the grouping on it are
one-shot. Neither is a question for the user, and `66` §14 is what says so.

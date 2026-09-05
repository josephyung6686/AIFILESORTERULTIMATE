# 102 — Why `subject` is still zero, and it is not the schema

**For the owner.** `101` traced why nothing was placed and ended at a poisoned `subject`.
The poisoning is fixed — 110 values including five ZIP codes became 8 that pass a context
check. This document is what that uncovered, and **§1 is a correction to my own first
answer**, which was committed before it was run.

Scored against your labels: `subject` is **0 correct out of 43**. The reason is not the
schema plumbing. It is that the course is written one way in the file and another way on
the folder, and that two thirds of the files do not name it at all.

---

## 1. CORRECTED — the schema tuple is not what stops the level

**The first version of this document was wrong and it was committed wrong.** It said
`subject` could no longer become a folder because `fd68cb6` dropped it out of
`active_schema_for`. That was reasoned from the code and never run. Run, it is false:

    proposed  dim=subject  role=subject_anchor  'PHYS1401'
    proposed  dim=subject  role=subject_anchor  'ECON2105'

— a live `academic.coursework` run on a six-file corpus, on the current tree. Levels are
built from `folder_levels_for`, which reads the applicability row and **does** carry
`subject`. `active_schema_for` is P9's *grouping* schema, a different seam. The `subject`
level was never unbuildable.

`fd68cb6` is still the right commit and the tuple is still a hand-kept copy. Neither claim
about the level survives.

## 1b. What actually stops it, measured against the labels

The producer's own numbers on the owner's corpus, scored against `labels.json`:

| | |
|---|---|
| files whose label carries a `subject` | **43** |
| values the producer wrote | 8 |
| **correct** | **0** |
| missed | 35 |

The eight are not hallucinations. They are **the right course under a different spelling**:

| file | produced | label |
|---|---|---|
| `Desktop/Python 1006/lecture01_introduction.ipynb` | `E1006` | `PYTHON1006` |
| `Downloads/Essay 2 Final Draft.pdf` | `ELTU3017` | `University Writing` |

The document says `E1006`. The folder the owner made says `Python 1006`. Both name one
course, and the label follows the folder — which is the owner telling us that **the folder
he made is the naming authority**, not the string inside the file. `values` already carries
`aliases` and `merged_into`; nothing populates them for this.

The thirty-five are the harder half and they are the design's own example. `problem1.ipynb`,
`homework0.py`, `es1_written.txt`, `fractions.py` — **they contain no course code at all**.
Twenty-four of the thirty-five sit in a folder where a sibling states the course
(`Desktop/Python 1006`: 21 files, 5 state `E1006`). Eleven have no sibling that knows either.

**And copying the sibling's fact onto them is forbidden by name.** `00`:55:

> A file named HW 3.pdf may contain only equations and the phrase "Homework 3," while a
> related syllabus, lecture deck, problem set, and midterm contain the missing anchors
> PHYS1401, Columbia, and Spring 2026. **The graph does not automatically copy those missing
> facts onto sparse files.** Instead, it assembles an evidence-rich local neighborhood…

`00`:108 says what happens instead: the sparse file is compared against the node's syllabus,
lectures and accepted problem sets and placed there "**rather than falsely claiming that the
course code was found inside the homework itself**." The file never acquires the fact. It
acquires a destination.

The channel that finds it is named at `00`:56, and it is off:

> Embeddings are useful at this stage because they can find files such as HW 3.pdf that lack
> the course code but resemble lecture notes and earlier problem sets

`cli.py` ships `EmbeddingsOff()` and `retrieval=RetrievalKnowledge(similarity=None, …)`, so
retrieval is by shared validated fact alone — and a file with no fact shares nothing and is
never retrieved. `readers/embedding_minilm.py` exists; `100` measured the encoder at 9.3–10
docs/s, fully on-device.

**So the ranking changed.** The schema tuple is tidy-up. The two things that move `subject`
off zero are an alias between what the file says and what the folder is called, and the
retrieval channel the design already specifies for files that say nothing.

## 2. Four situations of 208 can have their required folders built

169 of 208 applicabilities declare at least one REQUIRED, non-metadata level.

| | rows | |
|---|---|---|
| every required field has a **producer** | 11 | 6.5% |
| every required field can become a **folder** | **4** | **2.4%** |

The four: `academic.recommendation-letters`, `photos.screenshot-captures`,
`photos.scanned-documents`, `law_practice.precedent-bank`.

What the other 165 are waiting on:

| required field | rows blocked | producer | in `active_schema_for` |
|---|---|---|---|
| `project` | 67 | none | no |
| `record_type` | 45 | none | no |
| `work_type` | 30 | `facts/kind.py` | **yes** |
| `institution` | 13 | none | no |
| `event` | 13 | none | no |
| `site` | 12 | none | no |
| `artifact_type` | 8 | none | no |
| `subject` | 7 | `SUBJECT_RULE` | **no — §1** |
| `term` | 3 | `facts/dates.py` | **yes** |

165 rows are blocked. **101 of them are blocked by nothing but `project`, `record_type`,
`institution`, `event` and `site`** — 55 by `project` alone. The other 64 want one of those
*and* something else. (The table above counts field demand, so it double-counts a row that
wants two; 101 and 64 are distinct rows.)

None of the five is a shape. "Which project is this" is a reading, not a pattern, and no
regex will ever answer it — which is the whole of the case against widening the rule set.

---

## 3. Three things the library already ships that nothing reads

This is the part worth acting on. The semantic layer is **authored and compiled**; it is
not connected.

**`needs_llm` — 314 rows, one per situation, and it never reaches a prompt.** Each row
names, in prose, exactly what the model must decide and when it must abstain, quoting `00`.
`academic.coursework`'s own entry includes:

> a course identified in prose by programme or module name rather than by a code-shaped
> token (an Introduction to Organic Chemistry tutorial sheet, a Michaelmas problem sheet),
> which the deterministic course-code rule cannot reach

`recognition/rules.py:101` loads these into `deferred_readings`. `deferred_readings` appears
**nowhere outside `src/recognition/`**. The research that says what the model is for was
done, ratified and shipped, and the model has never been shown a word of it.

**`role_bindings` — the real per-situation schema.** Every applicability already states its
own active schema: each dimension's `role_ref` resolved through `role_bindings` to a
`field_ref`, with `requirement` and `metadata_only` on it. `active_schema_for` is a
hand-maintained tuple that duplicates this by hand for one situation and applies it to all
208. §1 is the proof that a hand-kept copy drifts silently.

**`field_glossary.json` — 55 entries, and every blocked field is already in it.** All nine
of `project`, `record_type`, `institution`, `event`, `site`, `artifact_type`,
`capture_year`, `record_period`, `people_cycle` have an authored definition the model is
handed. The model is never asked for any of them.

---

## 4. What this makes the extractor question

Not "better rules". Three tiers, and only one of them is new work:

| tier | for | state |
|---|---|---|
| closed vocabulary + zone | `work_type`, `media_type` — classifications drawn from a fixed list | **shipped**, `facts/kind.py`; the library ships `work_type_terms` (4,031 terms) and it is the ONLY field vocabulary it ships |
| the model, schema-bound | `project`, `record_type`, `institution`, `event`, `site` — identities that require reading | harness **shipped and wired** (`model_facts.fact_call_stage`, `cli.py:2261`); asked for the wrong fields |
| embeddings | grouping two files about one project that share no vocabulary | `EmbeddingsOff()`, `retrieval.similarity=None`; `readers/embedding_minilm.py` exists, `100` measured the encoder at 9.3–10 docs/s, fully offline |

**The mechanism has two halves and they are different seams.** Deriving `active_schema_for`
from the chosen applicability's `role_bindings` instead of a literal tuple makes the field
*groupable* — it is what lets an answer become a folder. Sending the situation's `needs_llm`
readings with the dossier is what *steers the ask* — the model can already be offered
`project` today (`active_field_allowlist` allows it wherever `research` or `code` is active)
and answers `file_type` and `authored_by` instead, which is `101` §"the model was never
wired up" measured.

Together they make all 169 rows *reachable*. How many the model then fills *correctly* is
unmeasured and is the real question. Neither half adds a rule, a threshold or a vocabulary;
neither is built, and neither is proposed as built — a schema derivation is a mechanism, and
mechanisms are the owner's to approve.

## 5. One defect seen on the way

The fresh run proposed `work_type = 'resume'` **inside the Coursework tree**. The vocabulary
is the union over the four schemas that declare the field, so `career`'s terms are live in an
academic situation — which is the same re-route `_work_type_vocabulary`'s own comment says it
forbids for `medical`'s `discharge summary`. A `resume` folder under `Coursework` fails the
north star. Flagged, not fixed.

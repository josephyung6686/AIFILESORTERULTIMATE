# 102 — The schema is a hand-kept tuple, and it drifted

**For the owner.** Two findings, both measured today on your 199 files. The first is a
regression `fd68cb6` introduced last night — the same commit that fixed a real defect.
The second is why the product can only ever build three kinds of folder, and it is the
answer to "how do we make the extractor better than rules".

`101` traced why nothing was placed and ended at a poisoned `subject`. That poisoning is
fixed. This document is what the fix uncovered underneath it.

---

## 1. `subject` is produced correctly and can no longer become a folder

**Before `fd68cb6`** (`.groundtruth/rebaseline-coursework`, the run recorded at 21:54):

```
proposed  dim='subject'  role='subject_anchor'  label='E1006'
proposed  dim='term'     role='cycle_period'    label='Spring2023'
```

**After, measured today** — fresh `academic.coursework` run, all 199 files carrying
evidence:

| | before | after |
|---|---|---|
| `subject` facts | 110, `direct` | **8, `validated`** |
| `subject` tree nodes | `E1006` present | **zero** |
| `term` nodes | present | 4 |
| `work_type` nodes | none | 4 |

The fact side got *better*: 110 shape-matches that included five ZIP codes became 8
values that passed a context check. That was the intended fix and it worked. **Their
precision against the labels is not measured here** — what is measured is that the
producer stopped firing on 102 readings it had no business claiming.

**The tree side lost the level entirely**, and it is one line:

```python
active_schema_for=lambda db, file_id, content_hash: (
    tuple(slot.field_key for slot in DIRECT_SLOTS.slots)
    + (TERM_FIELD, MEDIA_TYPE_FIELD, WORK_TYPE_FIELD))     # cli.py:4055
DIRECT_SLOTS = DirectSlots(slots=())                        # cli.py:1527
```

`subject` reached that tuple *only* by being a direct slot. `fd68cb6` emptied the slots —
correctly, `101` §"three explanations" names the slot as its second ceiling — and extended
the tuple with two fields, without putting `SUBJECT_FIELD` back. The lambda's own comment
states the consequence: **"a field missing here is a field P9 will not group on."**

`ap.academic.coursework` binds `subject_anchor → subject` as **required**. A required level
that cannot be built is a stronger explanation of that situation's 0% than the tie analysis,
and it supersedes the "fourth candidate" theory: proposed nodes under adopted folders were
being diagnosed in a tree that was missing its load-bearing level.

---

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

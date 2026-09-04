# 97 — Recognition by meaning, measured

The instruction was that term matching "is probably 99% not going to work since
each document is so different and we need to develop a new way". That is right
about the diagnosis. This note is what happened when the new way was built and
measured, and the headline is mixed on purpose: **the method works better than
the thing it replaces and worse than a constant, and on the one question that
matters most — is this file sensitive — it does not work at all.**

Everything below is measured on `.groundtruth/corpus`: 215 real files of the
owner's, 199 of which reach a `files` row, hand-labelled, 8 of them protected.

---

## 1. The encoder

**Chosen: `all-MiniLM-L6-v2`, as ONNX, run by `onnxruntime`.** 6 layers, 384
dimensions, Apache-2.0, 90.4 MB.

| | measured |
|---|---|
| download | 13.4 s, **once**, from `huggingface.co`, repo `sentence-transformers/all-MiniLM-L6-v2`, snapshot `1110a243fdf4706b3f48f1d95db1a4f5529b4d41` |
| model load | 3.4–5.8 s per process |
| document encode | **9.3–10.0 docs/s** (199 real files in 21.4 s, 4 threads) |
| 10,000 files | **≈ 18 minutes** |
| anchor encode | 4,700 anchors in ~30 s, cached to `anchors.npz`; **0.4 s** on every process after the first |
| at inference | opens no socket; weights read from a local directory the deployment names |

**Nothing leaves the device.** `onnxruntime` has no network path. The 90.4 MB was
fetched once, by hand, and `cli.py` names no download — `--semantic-model DIR`
points at the folder or the feature is off.

**Rejected, and why:**

* **`sentence-transformers`** — pulls `torch`, a ~2.5 GB install to run the same
  90 MB of weights this does. `onnxruntime`, `tokenizers`, `numpy` and
  `huggingface_hub` were already on the machine; `torch` was not.
* **`spacy` `en_core_web_md`** — averaged GloVe word vectors: no word order, no
  sub-word units. The case this exists to fix is `HW 9.pdf`, and `HW` is not a
  GloVe token.
* **TF-IDF / hashing + SVD** (`scikit-learn`, installed) — lexical matching with a
  rotation applied. `HW` and `homework` share no useful character n-gram, so it
  fails the one file that motivates the work.

Compare the local generative model already ruled out: **320.9 s for one dossier**
on qwen2.5:3b, ≈890 hours for 10,000 files. This is ~3,000× faster.

---

## 2. What the method gets right

Two things had to be fixed before it worked at all, and both were found by
measurement rather than by reasoning.

**Max-over-anchors is a count bias, not a nearest neighbour.** Scoring a schema by
its single nearest authored term gives **15.6%** top-1 accuracy. The schemas are
wildly unequal — `law_practice` has 1,143 anchors, `code` has 41 — and a maximum
over more draws is bigger for reasons that have nothing to do with the file. It
predicted `law_practice` and `construction_property` most often, on a corpus that
is mostly coursework.

**Do not normalise the centroid.** The unnormalised per-schema centroid scores
**29.1%**; dividing it by its own length drops it to **18.6%**. The length carries
real signal: a schema whose authored terms all point one way has a long centroid,
and one whose terms point everywhere has a short one. Normalising deletes exactly
the information that says which schemas are coherent enough to trust.

| scorer | top-1 schema |
|---|---|
| max over anchors | 15.6% |
| mean of top-10 anchors | 14.1% |
| normalised centroid | 18.6% |
| z-score against foreign anchors | 21.6% |
| **unnormalised centroid** | **29.1%** |
| **unnormalised centroid, anchors ≤ 6 words** | **32.2%** |

### The premise about prose was wrong

The brief's insight was that the 38.9% of authored terms that are prose are
"literally authoring notes… an excellent SEMANTIC ANCHOR", and that lexical
matching "throws away exactly the richest part of the library". Measured, they are
the **worst** anchors: dropping every term of 7+ words (13.5% of the 8,925
compiled) moves accuracy from 29.1% to 32.2%.

The reason is visible once stated. These entries are prose *about the research*,
not about a document — one `government` row is a 77-word aside beginning
*"proposed for r6, not design"*, another *"proposal note: none of these terms
appears in 00"*. Generic English sits near every document and drags a schema's
centroid toward the middle of the space. The insight was right that they are
unmatchable and right that embedding is the only way to use them; it was wrong
that they say anything about files.

---

## 3. What the method gets wrong, and it is the important half

**The four safety domains do not separate. At all.**

| the 8 hand-labelled protected files | safety score | percentile in corpus |
|---|---|---|
| OTC trading authorisation (Chinese) | 0.087 | 48.2 |
| BOC credit-card welcome pack | 0.138 | 84.9 |
| **the owner's HKID card** | 0.146 | 88.9 |
| medical record | 0.151 | 93.5 |
| Covid vaccination record | 0.092 | 54.3 |
| Covid booster photo | 0.110 | 69.3 |
| vaccination screenshot | 0.098 | 58.3 |
| vaccination records PDF | 0.084 | **43.2** |

Two of the eight sit **below the median**. Meanwhile the single highest
safety-domain score in all 199 files belongs to `Red Cross Certificate.pdf` — a
first-aid course certificate — and an open-source `LICENSE` file outranks the
owner's actual HKID.

There is no protect floor. Catching all eight requires a threshold that protects
**142 of 199 files**, which is the over-protection collapse `cli.py` already
records in `classifier`'s docstring: it "made an unreadable scan and a passport
identical in P7's store".

**And the release risk is real.** Left to classify freely, the path files two of
the eight protected files as ordinary `personal_non_sensitive, protected=False` —
making them auto-eligible and cloud-eligible. That is the HKID→DeepSeek path.

### But the RANKING works, and that is a different claim from the threshold

Asked the question the other way round — not "is the score high enough" but
"where does the right safety domain RANK among 23" — the encoder does what the
approach promised:

| protected file | best safety rank | own text |
|---|---|---|
| BOC credit-card welcome pack | **1** of 23 (`identity`) | 40 ch |
| medical record | **1** (`medical`) | 24 ch |
| Covid vaccination record | **1** (`medical`) | 1,659 ch |
| vaccination records PDF | **1** (`medical`) | 4,000 ch |
| **the owner's HKID card** | **2** (`identity`) | 782 ch |
| OTC trading authorisation (Chinese) | **2** (`finance`) | 4,000 ch |
| Covid booster photo | **3** (`medical`) | 22 ch |
| vaccination screenshot | 16 (`finance`) | 84 ch |

**Seven of eight put the correct safety domain in the top three of twenty-three,
on files that carry NO authored safety term anywhere in their content.** The
detector agent measured that separately: `vaccination`, `medical record`,
`identity card`, `hkid`, `credit card` and `bank statement` are authored by no
schema, and `immunization` exists in US spelling only. Lexical matching cannot
reach these files at all. The embedding puts them next to the right schema anyway,
across a language barrier in one case.

**And it is still not a decision rule.** Take "the nearest schema is a safety
domain" as the rule and it fires on **34 of 199 files, 4 of them right — 12%
precision**. The false alarms are a resume, three drafts of an essay, COVID
research notebooks, a `LICENSE-CC-BY-NC-SA`, an Adobe Premiere config file, and
the Red Cross certificate again. The centroids conflate *about medicine* with *is
my medical record*, which is exactly the distinction that matters.

Against today's detector — which marks 2 of the 8 and over-marks 10 — that is
better recall (50% vs 25%) bought with worse precision (12% vs 17%) and three
times the false alarms.

**So the finding is: the encoder locates these documents correctly and the schema
centroids are too broad to act on it.** The fix that follows is not a bigger
model. It is that the six or so missing terms are extremely specific — a file
containing "vaccination record" or "identity card" is not ambiguous — so authoring
them would catch these files lexically with near-zero false alarms. The semantic
ranking is the evidence that they are findable, and a triage list for authoring
them: 34 candidates, not 199.

### The two rules that make it safe

1. **`min_chars`.** The two files it released carry **22 and 84 characters** of
   their own text — a vaccination-record photograph and a screenshot. Mean pooling
   hides how much was pooled: a vector over 22 characters has the same shape and
   the same magnitude as a vector over four pages. This is `never_alone` in the
   form a vector can state it, and at 100 characters it releases neither, while
   costing almost nothing it was getting right.

2. **The safety veto replaces the protect floor.** Near one of `00`'s four
   domains — leading, or merely within the caution line — the path says
   **nothing**, and the file keeps exactly what the term detector gave it. It
   neither protects nor releases. That is the only move a signal this poor is
   entitled to make, and `SemanticRecogniser.__call__` raises rather than emit a
   record naming a safety domain, so the invariant is structural.

---

## 4. The numbers that decide

Detector versus semantic, on the same 199 files, where "correct" is the
ground-truth schema:

| | coverage | schema correct where it fires | correct overall |
|---|---|---|---|
| term detector | 79/199 (39.7%) | **20.3%** | 8.0% |
| semantic (best) | 199/199 | **32.2%** | 32.2% |
| always answer `academic` | 199/199 | 38.7% | **38.7%** |

So it is **better than the term matching it supplements** — 32.2% against 20.3%,
at 2.5× the coverage — and **worse than a constant**. Both halves are true and
both belong in any decision about it.

The saving grace is that schema accuracy barely reaches the shipped metric.
`HANDLING_POLICY` gives all nineteen ordinary schemas the same
`personal_non_sensitive`, so `research` mistaken for `academic` changes no
handling class. Only a safety domain changes the outcome — and those are vetoed.

---

## 4b. End to end, on the real harness

Both arms run from ONE snapshot of the tree (`af359fe`, 17:48), so they differ by
this change and nothing else — six other agents were editing the tree tonight and
a live before/after would have measured them too. 17 situations × 215 files, twice.

| | before | after |
|---|---|---|
| **CLASSIFY** | **90 of 199 (45.2%)** | **103 of 199 (51.8%)** |
| `personal_non_sensitive` | 78 | 91 |
| `sensitive_personal` | 12 | **12** |
| protected files not marked | 8 of 8 | **8 of 8** |
| files over-marked protected | 10 | **10** |
| `protected-breaches.txt` | — | **byte-identical** |
| sorting: exact / right-parent / wrong | 0 / 6 / 5 | **0 / 6 / 5** |

Per file, comparing each file against the run whose situation its label names:

* **13 gained** a handling class, every one `personal_non_sensitive` — lecture
  PDFs, lab-protocol notes, a penguin dataset, an AP Lang essay, a YAB application.
* **0 lost** one. **0 changed** class. The union property is not just tested in
  `tests/recognition/`, it is verified on 199 real files.
* **0** of the 13 is protected-labelled. **0** was marked protected.

**Protection is unchanged in both directions — measured, not argued.** It did not
get stronger either: this path cannot protect, by construction (§3).

**The gate opened and nothing came through it yet.** Not one of the 13 produced a
new placement, right or wrong. `no decision` fell by 2 and `not placed` rose by 2,
and those two files are PNG screenshots whose OCR happened to recover in one run
and not the other — nondeterminism, not this change; neither is among the 13.
So CLASSIFY rose 6.6 points and the sorting block did not move. A handling class
is a precondition of the next stage, not a substitute for it.

## 5. Ship state

Wired, tested, and **off unless `--semantic-model DIR` names the weights**.
Absent means the product behaves exactly as before: `_semantic_classifier` hands
the detector straight back.

* `src/recognition/semantic.py` — stdlib only. Every rule, no vector arithmetic.
* `src/readers/embedding_minilm.py` — the deployment layer, the only file that
  imports `onnxruntime`, `tokenizers` or `numpy`, matching `pyproject.toml`'s
  standing rule that `dependencies` stays empty.
* `tests/recognition/test_recognition_semantic.py` — 29 tests. Every guard was
  sabotaged and watched go red; two were found to be passing under sabotage and
  rewritten (the path-locator branch, and the safety-leader door).

**P9 is now connected.** `grouping/embeddings.py` was written, tested and used by
nothing. The document vector goes through `ensure_file_embedding`, so it is a
versioned P1 record keyed on the file version, and `vector_embeddings` carries
rows on such a run. P9's *grouping* retrieval channel stays off: §4.4's similarity
retrieval needs a threshold, channel weights and a compatibility predicate that
nothing has measured, and turning it on would be a different change.

**An embedding is not releasable.** It is derived from the document's text, and
mean-pooled MiniLM vectors are invertible enough to recover the gist of a short
document. A vector of a payslip is a payslip in a lossier coat. It is computed
locally, stored by P1 beside the observations it came from, scored locally, and
never sent. The nine `ALWAYS_LOCAL` kinds are as local in 384 floats as in words.

---

## 5b. Found on the way, and it is not mine: the HKID is not protected TODAY

Reading the classification rows for the eight labelled-protected files, before and
after, identically:

| file | handling class today |
|---|---|
| `2025209423_Joseph_Yung_HKID.pdf` | **`personal_non_sensitive, protected=False`** |
| `Covid -19 vaccination record (1).pdf` | **`personal_non_sensitive, protected=False`** |
| `joseph Yung Vaccination Records.pdf` | `sensitive_personal, protected=True` |
| `148268M000 FUND Trading OTC商品交易授權書_0226 sell.pdf` | `sensitive_personal, protected=True` |
| `Covid- 19 booster.jpeg` | unclassified |
| `Screenshot 2025-10-22 at 1.38.18 PM.png` | unclassified |
| `DisplayMedicalRecord.pdf` | unclassified |
| `eWelcome_Pack_TC_BOC_Credit_Card_TPA.zip` | unclassified |

Two numbers in this note disagree and the disagreement is not resolved here. §4b
reports the harness's `PROTECTED` line as "8 of 8 not marked"; the table above
shows two of the eight carrying `sensitive_personal, protected=True` in the
`classifications` table. The harness's `protected_marked` reads a different signal
than the classification row. Which is the right one to score is
ground-truth-judge's question, not this note's — what §8.4's gate actually reads is
the row, and the rows are identical before and after.

**The owner's Hong Kong identity card is classified as ordinary personal material
with `protected=False`, by the term detector, today.** That makes it
auto-eligible for placement and eligible for cloud escalation — §8.4's gate is a
handling class, and it has one. It is the exact path the brief names as the thing
that must never happen, and it is open right now.

This is a PRE-EXISTING defect. It is byte-identical before and after this change,
which changes nothing about the four safety domains by construction, and the two
unclassified vaccination images are the ones the `min_chars` rule exists to keep
this path away from. It is recorded here because it was found here, and it is a
larger and more urgent finding than anything else in this note.

## 6. Recommendation

Turn it on only if 13 more files in 199 are worth a 90 MB model and ~18 minutes
per 10,000 files, and never on the strength of the schema it proposes. The honest
summary is that **semantic similarity over this library is a mild improvement to
coverage and no help whatever with sensitivity**, and the second half is the one
the product's safety rests on.

The obvious next thing is not a bigger encoder. It is that four of the eight
protected files carry under 100 characters of extractable text — a photograph of
a vaccination card, a screenshot. No text-only method of any kind will read them.
That is an extraction problem, and it is where the next measured gain is.

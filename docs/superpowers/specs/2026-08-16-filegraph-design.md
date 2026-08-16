# FileGraph — graph-first file organizer (design)

**Date:** 2026-08-16
**Status:** Design complete, awaiting user review
**Repo:** `/Users/jy/Desktop/Database agent/filegraph` (new, standalone)
**Relationship to FileSort:** fully separate tool, no shared code
**Working name:** `filegraph` — rename freely, nothing depends on it

---

## Thesis

Every AI file organizer on the market asks a model the same question once per file. That is the
bug. **FileGraph builds a graph of the corpus first, from signals that cost nothing, and spends
the model only on naming the groups it finds.** Model cost drops from O(files) to O(clusters) —
roughly a 40–55× reduction — and because the graph persists, a new file arriving later is a
kNN query, not a classification.

The design principle is taken from graphify, the one tool in this space that is genuinely good at
connecting things:

> **Resolve exactly, or drop silently. Never guess, never half-commit.**

Its source repeats that rule in at least six independent places. It has no embeddings, no vector
store, and no cosine similarity anywhere; 96% of its edges are parsed facts at confidence 1.0.
We add semantic similarity because our domain has no import statements — but it enters as a
clearly-labelled lower-confidence tier that **never overrides a provable edge**.

---

## Evidence this is better

All numbers measured on the target machine (Apple M2, 8 cores) against the real corpus
(`~/Downloads`: 1,993 top-level files, 4,886 recursive) or a labelled synthetic corpus where
ground truth was required. Synthetic-derived numbers are marked.

### The graph layer is free

| Stage | 1,993 real files |
|---|---|
| Build mutual-kNN graph | **0.13 s** (5,047 edges, avg degree 5.06) |
| Leiden partition | **1.64 s** (284 communities, 6.1% singletons) |
| **Graph layer total** | **1.8 s** |

Baseline for comparison: AI File Sorter, local model, 300 files — **>1 hour, did not finish.**

### Where the time actually goes

| Scale | Embed | Cluster | Label | Total |
|---|---|---|---|---|
| 300 files | 2–6 s | 0.05 s | ~11 clusters | **~2.3 min** (vs >60 min) |
| 100,000 files | 12–44 min | ~15 s | ~1,400 clusters, batched | **~1 hr** (vs ~14 days) |

**Labeling is 90–95% of runtime at every scale.** Embedding is not the thing to optimise;
batching ~20 clusters per LLM call is.

### Corpus characterisation (real, `~/Downloads`)

| Property | Value | Consequence |
|---|---|---|
| Documents (PDF+DOCX) | 1,142 / 1,993 = **56%** | Extension rules are useless where the mass is |
| Opaque filenames | 369 = **18%** | Only this slice needs deep analysis |
| — of which images | 270 = **73% of opaque** | EXIF answers it for free |
| — of which PDFs | 52 | First-page text, milliseconds |
| — of which archives | 21 | List the manifest, don't extract |
| `(n)` duplicate suffixes | 488 = **24%** | Highest-value feature, needs zero AI |
| Non-ASCII filenames | 55 | Multilingual model is mandatory |

**This resolves depth-vs-speed.** Depth is not all-or-nothing: 82% of files carry filename signal,
and 73% of the remainder is served by EXIF at zero cost. Tier by what the file needs.

---

## Locked decisions

| Decision | Choice |
|---|---|
| Graph role | **Persists; disk layout is a projection of it.** Re-render the tree with no new model calls |
| Source of truth | **The filesystem.** Graph is a rebuildable derived cache, never the system of record |
| Scale | Ship for one folder (~2k); pick structures that survive 100k |
| Interface | **CLI engine + thin local web UI** over a shared library. Daemon only if Phase 4 measurement justifies it |
| Nodes | **Files + concepts**, correlated, both used for grouping |
| Existing folders | **Learn from them** as ground truth; do not propose reorgs of curated trees |
| Placement policy | **Per-folder: auto / suggest / off.** Graph ingest is always on |
| Learning loop | Record corrections from day one; **act on them later** |
| Taxonomy | **The user's existing folders are the label space.** New folders are *proposed* only for coherent groups that fit nowhere, and are frozen once accepted |
| Automation target | Graph decides ~90%, model handles the rest |
| Relationship to FileSort | Fully separate tool |

---

## Non-goals

- Owning the namespace. No FUSE, no virtual filesystem, no database-as-filesystem. Emit real
  directories and real filenames that Finder, `ls`, Dropbox and Time Machine already understand.
- Asking the user to tag anything. The graph is 100% inferred.
- Autonomous movement without review, outside folders explicitly set to `auto`.
- LLM entity extraction per file.
- Reorganising already-curated directory trees.

---

## Architecture

```text
                    ┌─────────── daemon (resident) ───────────┐
  scan ──▶ tier 0   │  cache: stat → hash → per-tier results   │
           tier 1   │  embed session (loaded once)             │
           tier 2   │  graph + index (in memory, persisted)    │
                    └──────────────────────────────────────────┘
                                     │
   graph build ──▶ cluster ──▶ label (LLM, batched) ──▶ taxonomy (frozen)
                                     │
                          placement ──▶ plan ──▶ review ──▶ apply ──▶ undo
                                     │
   new file ──▶ embed(1) ──▶ kNN ──▶ inherit placement   [~10–20 ms]
```

### The daemon is an optimisation, not a requirement — decide in Phase 4

An earlier draft of this spec called a resident daemon architecturally mandatory. **That was
true of a stack we are no longer building**, and it is recorded here because the reasoning is
instructive.

The argument rested on two costs that the component choices above eliminated:

| Cost | With the rejected stack | With the chosen stack |
|---|---|---|
| Model session init | `onnxruntime` **2.3–12.8 s** | `model2vec` import 0.46 s + vendored model load ≈ **0.6–2.8 s** |
| Loading the graph | parse node-link JSON **410 ms** (graphify measured 8.4 s on a 44 MB graph) | SQLite open + targeted lookup **1.6 ms** |
| Single-file kNN | — | **9.8 ms** brute force at 100k, no index |

A one-shot CLI invocation now costs roughly **0.6–2.8 s** end to end, essentially all of it
fixed startup. For batch operations that is irrelevant. For per-file watch-mode it is wasteful
but not disqualifying.

**Therefore: build the engine as a library with a one-shot CLI on top. Add the daemon in Phase 4
only if watch-mode measurement justifies it.** This is also the safer product position — the
prior-art record is unambiguous that a background process moving a user's files is what people
uninstall over, and a tool that only runs when invoked is easier to trust.

The lesson worth keeping: **cold start, not compute, is the dominant cost in a CLI that exits
between runs.** Any dependency added later must be measured on import time, not just throughput.
`sentence-transformers` costs 9.75 s on import alone; `lancedb` 2.0 s; `chromadb` 1.1 s. Those
are the numbers that would resurrect the daemon requirement.

---

## The graph model

### Nodes

`file` nodes carry what a file organizer actually needs — the fields graphify notably lacks:

```json
{
  "id": "sha256:3f9a…",  "kind": "file",
  "path": "/Users/jy/Downloads/Syllabus BUSIB 4300 Spring 2026.pdf",
  "name": "Syllabus BUSIB 4300 Spring 2026.pdf",
  "norm_name": "syllabus busib 4300 spring 2026",
  "ext": "pdf", "mime": "application/pdf",
  "size": 284119, "mtime_ns": 1786…, "ctime_ns": 1786…,
  "content_hash": "sha256:…", "simhash": "…", "phash": null,
  "depth_tier": 1
}
```

**A file node stores no placement.** Where a file goes is *derived* — from its facets under the
active template, from classification into an existing folder, or from a proposed cluster. Storing
a `community` or a `path` on the node would freeze one projection into the record and defeat
re-rendering. Placement lives in the plan and the journal, never on the node.

`concept` nodes are projects, people, organisations, courses, topics. **They are the `val` rows
of the facet schema** — see *Facet storage* below, which supersedes any separate concept-node
table. A concept is a dimension value; a file attaches to it through a `facet` row; two files
sharing a `val_id` are neighbours with no extra edge.

Read the two together: **this section defines what a node knows about itself; the facet schema
defines how nodes relate and how the tree is projected.**

### Edges — the signal ladder

Every edge carries `relation`, `confidence` tier, discrete `confidence_score`, and **provenance**:
the specific evidence that justifies it. This is what makes every proposed move explainable, and
it is the single most valuable thing in graphify's design.

| Tier | Score | Relations | Evidence |
|---|---|---|---|
| **EXTRACTED** | 1.0 | `duplicate_of`, `version_of`, `in_folder`, `same_session_as`, `references`, `attachment_of`, **`shares_code`**, **`same_author`**, **`same_event`** | Content hash equality; `(n)` suffix + hash; directory containment; mtime window; **in-document citation/DOI/URL**; **identical course or ID code extracted from both bodies** (`CC1010.628`); **identical document author**; **same camera + same day + same GPS** |
| **INFERRED** | 0.5 | `near_duplicate_of`, `same_project_as`, `shares_entity_with` | MinHash/LSH on extracted text, pHash on images, shared concept node, shared client/organisation name |
| **AMBIGUOUS** | 0.2 | `similar_to` | Embedding cosine over extracted content — **and nothing else** |

The strongest edges now come from **content**, not from the filesystem. `shares_code`,
`same_author` and `references` are the direct analogue of graphify's `imports_from`: two files
independently yield the same string from their own bodies, so the edge is an identity match, not
a similarity score.

#### Measured on the real corpus — and the guards this requires

396 of 400 real PDFs/DOCXs extracted at **24 ms/file**, producing **770 fact edges** from 82
shared entities; **47% of files gained at least one fact edge.** Genuine, and unreachable from
filenames:

| Shared fact | Links | What it caught |
|---|---|---|
| `PHYS1401` | 10 files | Every lecture, template and practice final for one course |
| `hjy2114` (student ID) | 8 | The whole resume/cover-letter family |
| `redcross.org` | 6 | Volunteer guide + board application + registration links — **no shared filename tokens at all** |
| `Joseph_Yung_Resume.docx` (title) | 6 | A version chain across renamed exports |

**But roughly half the raw shared entities were noise hubs**, and the design must suppress them:

| Junk hub | Links | Why it is worthless |
|---|---|---|
| `gmail.com` | 21 | Everyone has one |
| `Mozilla/5.0 (Macintosh…)` (creator) | 17 | Means "printed from a browser" |
| `LaTeX with hyperref` (creator) | 15 | Means "made in LaTeX" |
| `about:blank` / `(anonymous)` / `(unspecified)` | 5–6 each | Null values with a name |

Plus one **false positive worth remembering**: a naive `[A-Z]{2,5}\d{4}` course-code pattern
matched `VHX7000` — a *Keyence microscope model number* — and linked resumes to a materials
science abstract. The regex found a string; it did not find a fact.

**Three mandatory guards, all borrowed from graphify's hub suppression:**

1. **IDF-weight every entity.** Document frequency above ~half the corpus ⇒ never links
   (graphify's `_df_cap`). Entities shared by 3–10 files carry the signal.
2. **Reject entity classes that describe the tool, not the content.** PDF `producer`/`creator`
   are excluded outright. Only `author`, `title`, `company` are candidates, behind a null-value
   blacklist (`about:blank`, `(anonymous)`, `(unspecified)`, `python-docx`, `Word Document`).
3. **Type-diversity ban.** An entity spanning too many distinct document kinds is a hub, not a
   topic (graphify's `_type_diverse_ban`). This is what catches `VHX7000`.

**And entities must be validated, not merely matched.** A candidate course code is confirmed by
surrounding context (`Section`, `Syllabus`, `Lecture`, `Spring 2026`) before it is trusted. This
is the direct analogue of graphify resolving an import to a real path on disk before minting an
edge: **resolve exactly, or drop.** Pattern matching alone is the guessing we are trying to
eliminate.

Confidence scores are **discrete**, drawn from a fixed rubric. `0.5` is never a default for an
unknown — models collapse continuous ranges into a binary when allowed to.

### Two rules that are not negotiable

**1. Embedding similarity alone never creates an edge.** A `similar_to` edge requires at least
one non-embedding corroborator to be promoted into the graph used for clustering.

This is not theoretical. On the real corpus, every incoherent cluster came from bare cosine
similarity. Cluster [0], 73 files: `repo inspo.pdf`, `problem4.py`, `Article info.pdf`,
`Additional information.docx`, `Comment 6.docx` — these grouped together **because their names
are equally uninformative**, and generic names sit near each other in embedding space. The
identical failure appeared independently in the synthetic benchmark (`document (8367).pdf` +
`final.pdf` merged academic papers with tax documents). An LLM asked to name such a cluster
will invent something confident and wrong.

**2. When a signal cannot be resolved, drop it. Never dangle, never guess.** graphify's
governing discipline, and the reason its graphs stay clean.

### Photos are grouped by EXIF, never by filename

`IMG_7009.HEIC` carries no signal, and in the real test photos fragmented across four separate
clusters. Date, GPS and camera are deterministic, free, and correct. 270 of the 369 opaque files
are images — this single rule covers 14% of the entire corpus at zero cost.

### AMBIGUOUS needs a UI affordance nobody has built

graphify defines the `AMBIGUOUS` tier and its deterministic engine **never emits it** — there are
zero AMBIGUOUS edges in a real 31k-node graph. Our riskiest signals live exactly there. We are the
first real user of that tier, so it needs a confirm/reject surface that graphify never had to build.

---

## Pipeline

### Tier 0 — cache (free)

Copied verbatim from graphify, the best thing in its codebase:

1. **Stat fastpath.** Persisted index maps path → `{size, mtime_ns, hashes}`. If size *and*
   `mtime_ns` match, return the cached hash **without reading the file**.
2. **Content hash** only when stat moved. Compared with `!=`, not `>`, so restoring an older
   file still invalidates.
3. **Per-file result cache** keyed by content hash.
4. **Separate hash per tier** (`cheap_hash`, `deep_hash`) so free and paid work invalidate
   **independently**. Bumping the cheap tier leaves the deep tier legitimately stale and *recorded
   as owed*.
5. **The paid tier's cache is deliberately unversioned.** Re-extraction costs money, so money
   changes the invalidation policy. Namespace it by prompt fingerprint so a prompt edit doesn't
   replay stale results.

**The key must include what produced the answer, not only which file it was about.** Minimum:
`(content_hash, extractor_version, analysis_tier, model_id, prompt_fingerprint)`.

AI File Sorter keys its categorisation cache on `(dir_path, file_name, file_type)` and nothing
else — `DatabaseManager.cpp:1629-1631`, `UNIQUE` constraint at `:296`. No content hash, no mtime,
no model id, no content-analysis flag. The consequences are instructive:

- rewrite a file's contents entirely, keep the name → the stale category is served forever
- rename or move an unchanged file → total cache miss, full re-analysis
- switch model → cache still hits
- **turn on content analysis → cache still hits.** Enabling the product's headline feature
  invalidates nothing, so on an already-scanned folder the user gets the filename-only answers
  back and concludes the feature does nothing.

### Tier 1 — filesystem facts (all files)

Name, extension, MIME, size, mtime/ctime, directory position, content hash, `(n)` duplicate
detection. No model, no parsing. Resolves exact and near duplicates outright.

### Tier 1.5 — CONTENT FACT EXTRACTION (all files) — the core of the design

**This is our equivalent of graphify's AST pass, and it is not optional.** graphify is accurate
because it *parses* files and extracts declared facts; it never infers a relationship from a
name. A folder of documents has no import statements, so we manufacture the declared-structure
layer by reading each file with a type-specific extractor.

**Read the WHOLE file, not a peek.** Measured on the real corpus — doubling the cost returns
eight times the information, so there is no trade to make:

| | Cost | Text recovered |
|---|---|---|
| PDF, page 1 only | 30.2 ms | 1,578 chars |
| **PDF, all pages** | **59.8 ms** | **13,168 chars** |
| DOCX, first 25 paragraphs | 12.1 ms | 3,162 chars |
| **DOCX, full body + tables** | **18.9 ms** | **7,350 chars** |

| Type | ms/file | Corpus cost | Facts extracted |
|---|---|---|---|
| PDF (full) | **59.8** | 811 files → 48 s | Title, author, dates, **complete text**, headings, DOIs, codes |
| DOCX (full + tables) | **18.9** | 331 → 6 s | Core properties, headings, **complete body and table contents** |
| PNG | 14.7 | 128 → 2 s | Dimensions, EXIF, screenshot signals |
| JPEG | 92.3 | 115 → 11 s | EXIF: camera, timestamp, GPS |
| JPG/WEBP/TIF | 2–4 | ~130 → <1 s | as above |

**Whole-corpus full extraction ≈ 55 seconds for ~2,000 files** (vs 28 s for a peek). Roughly the
cost of a single AI File Sorter LLM call, for the entire folder.

**A peek is not enough, and this was measured, not assumed.** With page-1-only extraction just
47% of files gained any fact edge at all. PDFs in this corpus have a **median of 3 pages but a
mean of 12.1 and a maximum of 281** — page 1 misses most of the document.

**11.0% of PDFs have no extractable text even after reading every page** — 89 files, 616 pages,
measured across the full corpus of 808. Only 2 of 120 sampled files were rescued by reading past
page 1, so the empty ones are empty throughout: they are scans, and they need OCR regardless of
extraction depth. A bounded, known cost rather than a surprise. See *OCR* below for the 3.4-minute
figure.

Real examples from the target corpus, showing why this beats filenames outright:

- `trade_sections_form-fall_0 (1).pdf` → author `John R Stobo II`, and text yielding `CC1010.628`
  and `hjy2114` — a **course code** and a **student ID**. Two files sharing `CC1010` is a *fact*.
- `Wash U .docx` → heading *"Please tell us what you are interested in studying at college and
  why. (200 words)"* — unambiguously a college application essay. Invisible from the filename.
- `氢能企业IPO主营业务梳理_EY_2026.docx` → headings `一、执行摘要`, `核心结论`; text naming
  `EY-Parthenon` and the client engagement.
- `Hw 5 .pdf` → **zero extractable text**, producer `iOS Quartz PDFContext` ⇒ a photographed
  page. Detected by *empty text + iOS producer*, routed to OCR.

#### Photos vs screenshots — the case that proves content is mandatory

Both may be named `IMG_4821.PNG`. They are not the same kind of object and must not be grouped
together.

| Signal | Real photo | Screenshot |
|---|---|---|
| Camera EXIF (`Make`/`Model`) | present | absent |
| GPS | often | never |
| Dimensions | sensor sizes | **exact screen sizes** |
| Grouping key | event = timestamp + location | **OCR'd text content** |

**Measured trap: absence of EXIF does NOT imply screenshot.** WhatsApp and most messaging apps
strip metadata — `WhatsApp Image 2026-07-13.jpeg` has no EXIF and is a photo. A naive
no-EXIF heuristic misclassified it, and misclassified a 1080×1080 social graphic too.

**Correction — OCR text density is NOT a discriminator.** An earlier draft proposed deciding by
text density; that is wrong. Receipt photos, document scans and whiteboard shots are text-dense
*genuine camera photos*. Density separates nothing.

**No published benchmark or standard technique for screenshot detection exists.** Real products
avoid the problem with provenance rather than solving it: iOS flags screenshots *at capture
time* and its "Screenshots" album is a metadata lookup, not a classifier; Android writes them to
a `Screenshots/` directory. We have no provenance for loose imported files, so we use a signal
stack, in confidence order:

1. **Camera EXIF present** (`Make`, `Model`, `ISO`, `FocalLength`) ⇒ photo. Highest confidence.
2. **Exact match to a known screen resolution** (1170×2532, 1920×1080, 2560×1440…) vs
   sensor-shaped dimensions (4032×3024, 6000×4000). Requires a maintained device table —
   a real ongoing maintenance cost, and it should be a data file, not code.
3. **PNG** — the default screenshot format on macOS, Windows, iOS and most Android; plus the
   `Software` EXIF tag.
4. **Sensor noise** — screenshots are mathematically flat; real sensor output has grain.

Signals 1–3 are free and get most of the way. **Where they disagree, abstain and ask** rather
than guessing — this is exactly the two-condition abstention rule applied to a file-type
question.

OCR still runs on confirmed screenshots, because a screenshot's *text is its content* — it is
just not how we identify one.

Worth noting: Google Photos classifies images into Screenshots, Receipts, Identity Documents,
Notes and similar — and in March 2024 added **multiple categories per image** plus manual
recategorisation. That is a tacit admission that one category per item is the wrong data model
and that auto-classification is wrong often enough to need a correction UI.

**HEIC requires `pillow_heif.register_heif_opener()`.** Without it all 87 HEIC files in the
corpus fail to open — measured 40/40 `UnidentifiedImageError`. Silent blindness to 4% of the
corpus.

**Caveat measured on real files:** document metadata is a signal, not gospel — several files
report `author: python-docx` because a script last touched them. Metadata corroborates; it never
decides alone.

### Tier 2 — embeddings (demoted to a fallback)

**Embeddings are the last resort, not the primary signal.** They run over the *full extracted
content* (complete document text, headings, OCR output, title) — the filename is a minor
additional input, never the main one.

An embedding-only relationship is `AMBIGUOUS`, confidence 0.2, and **can never form an edge by
itself**. It exists to link files whose extraction produced nothing usable, and to break ties
between fact-based candidates.

The reason is measured, not theoretical: clustering on filenames alone produced a 73-file
cluster of `repo inspo.pdf` + `problem4.py` + `Comment 6.docx` — files grouped **because their
names are equally uninformative.** Generic names sit near each other in embedding space. That
failure disappears when the graph is built from extracted facts, because two files either share
a course code, an author, an event timestamp or a citation, or they do not.

#### 2a. Normalise the filename first — when a filename is used at all

This outranks every model choice. Measured end-to-end cluster purity on a multilingual corpus:

| Input | Purity | Cross-lingual acc@1 |
|---|---|---|
| Raw filename (`年度報告書(1)_2024_0.xlsx`) | **0.328** | 0.15 |
| Cleaned (`年度報告書`) | **1.00** | 0.725 |

```python
s = re.sub(r'\.[A-Za-z0-9]{1,5}$', '', s)                               # extension
s = re.sub(r'(?i)[_\-\s]*(v\d+|final|old|copy|draft|最終|副本)', '', s)   # version markers
s = re.sub(r'\d', '', s)                                                # dates / digits
s = re.sub(r'[_\-\(\)\.]+', ' ', s).strip()                             # separators
```

Dates and version markers are a large fraction of the tokens in a short filename, so they average
into the vector and swamp the two words that carry meaning.

**Keep the original filename** — for display, and because `_v2`/`_final` is precisely how
Tier 1 detects `version_of`. Normalise only what is fed to the embedder.

#### 2b. Input text

Normalised filename **plus a content peek by default**: first ~2 KB of text files, page 1 of
PDFs, archive manifest listings, document title/author metadata.

#### 2c. Model — multilingual static embedder, shipped in-tree

**`minishlab/potion-multilingual-128M`** (MIT, 101 languages), quantised
`int8 / dimensionality=128`. `save_pretrained` produces **~50 MB** — vendored in the repo, so
there is no download and no network dependency at first run.

Measured head-to-head, same pipeline, cleaned input:

| Model | Size | Throughput | Cluster purity |
|---|---|---|---|
| **potion int8/d128** | **64 MB** | **27,467/s** | **1.00** |
| potion fp32/d256 | 512 MB | 14,643/s | 1.00 |
| MiniLM-L12 multilingual | 220 MB | 87/s | 1.00 |

**315× faster at identical clustering outcome.** 100k files embed in **~3.6 seconds**.

The transformer is genuinely better at raw cross-lingual *retrieval* (ZH→EN acc@1 0.85 vs 0.625),
but that advantage does not survive into the clustering result, which is what we ship.

**Non-negotiable regardless of model: it must be multilingual.** English-only models are a
**correctness bug** here, not a quality preference — they tokenise the 55 CJK filenames to
`[UNK]` fragments, so those files cluster together *because they are unrepresented*, and the
labeller names that false cluster plausibly.

Rejected: `sentence-transformers` (**9.75 s import**, disqualifying for a CLI);
fastembed's `multilingual-e5-small` (not offered — only MiniLM-L12 and e5-large at 2.24 GB).

**Because embedding is now effectively free, spend the budget on richer input text rather than a
better embedder.** That is why content peek is a default rather than an option — and it attacks
the grab-bag clusters directly, since those exist precisely because filenames carry no signal.

**Phase 2 must still A/B both embedders through the Phase 0 scorer before committing.** Purity on
a synthetic multilingual corpus is not the same as ARI on the user's real files.

### OCR — Apple Vision, not Tesseract

Measured on real scanned pages from the corpus, same metric (word recall against the PDF's own
text layer):

| | ms/page | Recall | Install |
|---|---|---|---|
| **Apple Vision** (ACCURATE, correction off) | **739** | **99.7%** | **13 MB** (pyobjc; framework ships with macOS) |
| Tesseract 5.5.3 | 2,891 | 99.6% | 694 MB |

**3.9× faster at tied accuracy and 53× lighter.** Both non-obvious settings must be set
explicitly, because both defaults are wrong:

| Setting | Default | Use |
|---|---|---|
| `usesLanguageCorrection` | **on** — 1,621 ms, 99.1% | **off** — 650 ms, 99.7%. Faster *and* more accurate |
| `recognitionLanguages` | unset — **0.0% CJK recall, silently** | `["en-US","zh-Hans", …]` — 99.0% CJK |

Adding languages is free on documents that don't contain that script and costs 2–3× on ones that
do — which is exactly when it is needed. Render at **200 DPI** (recall plateaus there; DPI barely
affects time). `FAST` recognition is Latin-only and drops to 94.9% — not usable here.

**Cost on this corpus: 89 zero-text PDFs (11.0%, not the 8% estimated earlier), 616 pages.**
5.9 min single-process, **3.4 min across 4 processes**, one-time, offline, $0.

**Two operational traps, both measured:**

- **`ThreadPoolExecutor` and `ProcessPoolExecutor` both hang** around pyobjc + Vision — 0% CPU,
  never return. Shard by spawning **independent processes**.
- **Parallelism plateaus at 1.86×** (Vision's ANE is shared). Use 4 workers; building for 8 buys
  nothing.

**Scan detection:** probe only the **first 3 pages** for extractable text — 1 false positive in
808 files, and a full sweep of the corpus costs 52.7 s.

### Bad text layers — the failure that zero-text detection misses

A PDF can have a text layer that is *garbage*. Real example from this corpus:

```
Adobe Scan Jun 16, 2025.pdf
  text layer: "Manht1Ut1nvrlle, c1ncl Tc,c1clwr<:, Coll('qp"
  actual     : "Manhattanville, and Teachers College"
```

Zero-text detection passes this file, and the pipeline indexes mojibake as clean content.

Two global detectors were tried and **both are unreliable**: dictionary-hit-rate flags Spanish
and Chinese documents as garbage and scored this file *above* the corpus median; a dirty-token
rate catches it but false-alarms on math-heavy exams.

**Rule: do not pre-screen globally. Use field-level fallback — if a document has a text layer but
yields zero facts, re-OCR that one file.** The extraction result is the detector, and it costs
nothing on documents that work.

### Tier 3 — expensive interpretation (escalated only)

Everything a parser cannot reach: **OCR** for scanned PDFs and screenshots, **vision captioning**
for photos whose EXIF says nothing useful, and LLM concept extraction for documents whose text
yielded no entities.

Triggered by the escalation rule, never run wholesale. Note that Tier 1.5 already routes the
obvious cases — a PDF with zero extractable text and an iOS producer string is a photographed
page and goes straight to OCR without consuming the escalation budget.

### Cluster

- **Leiden** (`RBConfigurationVertexPartition`), mutual-kNN k≈15. Measured: ARI 0.440 vs
  agglomerative 0.375, HDBSCAN 0.222, extension baseline 0.321 *(synthetic)*.
- **Not HDBSCAN.** It labelled 21–100% of files as noise depending on configuration, and an
  independent benchmark found it worst on 5 of 6 datasets with >30% noise. A third of files
  landing in Unsorted defeats the whole product.
- **Pull super-hubs out before partitioning**, then reattach by majority vote of neighbours'
  communities. This is the direct fix for generic-name grab-bag clusters, and for `Downloads/`
  itself behaving as a hub.
- **Determinism is a correctness requirement.** Sort edges before insertion; total-order
  tiebreak on partition output. Without this, CPython's per-process string-hash seed permutes
  community IDs run to run — and a tool that reshuffles the user's folders on every rebuild is
  unusable.

### Nested folders — build the hierarchy graphify discards

graphify splits oversized and low-cohesion communities, then **flattens the result** into
`{int: [nodes]}` with no parent pointers. Its tree view comes from filesystem paths, not
communities. We keep what it throws away:

- Make splitting **recursive**, recording `{cid: {parent, depth, nodes}}`.
- Recurse while `len(nodes) > max_size` **or** `cohesion < threshold`; stop at a depth cap and a
  `min_split_size` floor. That floor is what prevents 400 folders of 3 files.
- `cohesion = intra_edges / (n(n-1)/2)`.
- Apply community remapping **per level**, or folder IDs permute across rebuilds.

### Label

- **10–20 centroid-nearest members** plus top c-TF-IDF terms per cluster. Centroid-nearest beats
  random selection substantially.
- **Batch ~20 clusters per LLM call.** Labeling is 90–95% of runtime; this is the single highest-
  leverage optimisation in the system. 1,400 calls → 70.
- **`community_member_sigs`**: SHA-256 of sorted member IDs in a sidecar, so a folder whose
  contents changed loses its stale name rather than laundering it forward. Essential once the
  user hand-names folders.

---

## Canonical taxonomy + alias table — build this on day one

Adopted from AI File Sorter (`DatabaseManager.cpp:372-402`), the single highest-leverage idea in
its codebase. Two tables:

```sql
CREATE TABLE category_taxonomy (
  id, canonical_category, canonical_subcategory,
  normalized_category, normalized_subcategory, frequency,
  UNIQUE(normalized_category, normalized_subcategory));
CREATE TABLE category_alias (
  alias_category_norm, alias_subcategory_norm, taxonomy_id,
  PRIMARY KEY(alias_category_norm, alias_subcategory_norm));
```

**Every label — from a model, a rule, or the user — passes through `resolve_category()` before it
can become a folder on disk.** It canonicalises onto an existing row or creates a new one.

This solves the failure that actually destroys trust in a file organizer: one concept spawning
`Docs`, `Documents`, `documents`, `Document`, `Doc Files` as five sibling folders. It needs no
model call, no embedding, and no configuration; it degrades gracefully; and it works
retroactively because aliases accumulate. The taxonomy stabilises as a side effect of use.

Improve on their version in one respect: their `normalize_label` is naive string normalisation.
Key the canonical form on something stronger (case/space/punctuation folding **plus**
lemmatisation and a stopword-stripped token set), and record every alias observation with its
provenance.

---

## Determinism in the model call

**Temperature 0, fixed seed, for every classification and labeling call.**

AI File Sorter ships `temp 0.8` with a default random seed on a classification task
(`LocalLLMClient.cpp:141-142`) — the same file categorised twice can land in different folders,
and their cache hides it because you only ever observe the first roll. Their entire consistency
pass exists largely to repair sampling noise they introduced themselves.

Do not create the problem and then build a subsystem to fix it.

---

## Proposed folders freeze once accepted

Scope note: this applies **only to folders the system proposed** from the cluster-and-propose
path. The user's pre-existing folders were never ours to re-partition — they are the label space,
per the placement section above.

Measured two ways, independently. Adding 50 files to 300 churns **~28% of Leiden's assignments**
(ARI 0.715 across 5 trials). On 2,000 files + 40 new, cold re-clustering moved **350 of 2,000
files into different folders**. If proposed clusters became folders and we re-clustered on every
change, files would re-file themselves constantly. That alone would make the product unusable.

| Strategy | Churn on existing files |
|---|---|
| Cold rerun *(naive)* | **17.5%** — 350 of 2,000 files change folder |
| Warm start (`initial_membership`) | 2.8% |
| **Frozen labels** | **0.0%** — and all 40 new files still placed correctly |

**Therefore:**

1. Cluster and label **once** to establish the taxonomy.
2. Persist `file_id → community_id` plus a stable human name and member signature. **Community
   IDs are ours forever — never let the algorithm renumber them.**
3. Assign new files by **similarity-weighted majority vote of their k nearest already-assigned
   neighbours** — label propagation with frozen labels, ~15 lines of numpy given the kNN we
   already have. No re-partition.
4. Below the confidence threshold, hold the file in a review bucket rather than guessing.
5. Accumulate unassigned and low-confidence files. **Only when that pool exceeds ~10% of the
   corpus**, offer an explicit opt-in reorganise that re-runs full clustering warm-started from
   current assignments — shown as a reviewable diff.
6. **Fixed RNG seed everywhere.** A meaningful share of the measured 17.5% is pure RNG, free to
   eliminate.

This makes stickiness a **product guarantee, not an algorithmic hope**: existing folders are
immutable unless the user asks for a reorganise.

**Licensing note.** `leidenalg` supports true freezing natively via `is_membership_fixed`
(measured 0.0% churn) but is **GPL-3.0**, which would force GPL on the whole tool. We use
**`graspologic-native` (MIT, 0.7 MB wheel)** and implement freezing in the ~30 lines above.
Warm start alone also degrades gracefully — repeated rescans measured 5.5% → 1.0% → 2.2% → 0.2%
churn — so this is a safe fallback, not a cliff.

This also makes incremental ingest trivial: single-file kNN is 0.79 ms at 20k vectors and
9.8 ms brute-force even at 100k. **Per-file queries need no ANN index at all.**

An ANN index is only relevant to the initial bulk graph build above ~20k vectors — and
**`hnswlib` ships no arm64 wheel** (compiles from source in 281 s, requires Xcode CLT), so it is
disqualified as a default dependency. Chunked brute-force numpy covers the target scale; revisit
only if a real corpus exceeds ~50k files.

---

## Component stack

| Purpose | Pick | Why | License |
|---|---|---|---|
| **Filename normalisation** | 4-line regex | purity 0.328 → **1.00**. Highest-leverage step in the pipeline | — |
| Embeddings | `model2vec` + `potion-multilingual-128M` int8/d128, vendored | **27,467/s**, 101 languages, no torch, no download | MIT |
| Community detection | `graspologic-native` + ~30-line freeze layer | `hierarchical_leiden`, 0.7 MB wheel, py3.9–3.13 | MIT |
| Graph build | numpy chunked mutual-kNN | 0.13 s at 2k, measured | — |
| Vector storage | numpy `.npy` | 2k × 128 dims = 1 MB. A vector DB is pure overhead here | — |
| **Graph persistence** | **SQLite** | open + targeted lookup **1.6 ms** vs **410 ms** to parse equivalent JSON | public domain |
| PDF text | `pypdfium2` | comparable to PyMuPDF and **not AGPL** | BSD-3/Apache-2.0 |
| **OCR** | **Apple Vision** via `pyobjc-framework-Vision` | 739 ms/page at 99.7%, **13 MB** vs Tesseract's 694 MB | OS framework |
| **Gazetteer matching** | **`pyahocorasick`** + hand-rolled boundary check | 0.047 ms/doc vs 102 ms for regex-per-key | BSD-3 |
| Named entities (`school`/`person`/`client` only) | `gliner_small-v2.1` | +20 pts recall where rules abstain | **Apache-2.0 (v2.1+ only)** |
| Date parsing | `dateutil`, **never `fuzzy=True`** | 0.016 ms/call, no fabrication | Apache-2.0 |
| Photo near-dup | `imagehash` | pHash/dHash | BSD-2 |
| Doc near-dup | `datasketch` MinHash-LSH | | MIT |

Budget: **~120 MB installed, ~0.6 s CLI cold start, 100k files embedded in under 4 seconds.**

**Rejected with cause, measured:** `dateutil.parse(fuzzy=True)` (**fabricates dates from our own
field values** — highest-severity item here) · spaCy statistical NER (its entire label set lacks
school/course/term/doc-type; `lg` is *slower* than `sm` for zero gain — but its **EntityRuler at
0.80 ms/doc is worth having**) · a local LLM on the bulk path (**12,204 ms/doc, 4.2 hours per
1,000 files, 20% invalid JSON** even with constrained decoding — viable only as a last-resort
fallback on the ~2% where everything else abstains) · Tesseract (3.9× slower, 53× heavier than
Vision) · FlashText (4× slower than pyahocorasick, unmaintained since Apr 2025) · PaddleOCR on
Apple Silicon (segfaults) · GLiNER v0/v1 (CC-BY-NC).

**Rejected with cause:** `PyMuPDF` (AGPL-3.0 or paid) · `leidenalg` / `python-igraph` (GPL) ·
`graspologic` full (514 MB, 16.3 s import, caps at py<3.13 — use `graspologic-native`) ·
`hnswlib` (no arm64 wheel) · `sentence-transformers` (9.75 s import) · `lancedb` (2.0 s import) ·
`chromadb` (1.1 s import) · `kuzu` (archived 2025-10-10) · NetworkX `leiden_communities`
(dispatch-only stub, raises `NotImplementedError`) · `rustworkx` (no community detection at all).

---

## Structure templates — the user declares the shape, the system fills it in

**This is the primary answer to cold start, and it is better than both alternatives.** Learning
from an organized folder requires the user to already have one. Inventing categories from content
is the feature DEVONthink shipped and removed. The third way: **ask the user for the shape once,
in a gist, and offer boilerplate templates to choose from and adapt.**

### A template is a schema of dimensions, not a list of folder names

```
Academic   :  school / year-term / subject / work-type
              → Columbia/2026-Spring/PHYS1401/Problem Sets/
Client work:  client / project / phase / doc-type
Personal   :  category / year            → Taxes/2025/, Medical/2026/
Photos     :  year / event               → 2025/Japan Trip/
Research   :  project / stage / artifact-type
```

The user picks one, edits the dimension order, or writes their own in a sentence.

### A dimension must encode a ROLE, not a topic

**Measured failure that produced this rule.** A hold-out propagation test on the real corpus
recovered `school` at 92% precision — and every error was the same error:

```
U Chicago Supplemental Essay 2.docx   true = UChicago   → predicted Columbia (w=26.7)
_U Chicago Supplemental essays.docx   true = UChicago   → predicted Columbia (w=26.7)
```

The prediction was not wrong about the *connection* — the user attends Columbia, so
`columbia.edu` and their student ID appear in almost every document they write, **including
essays addressed to other universities.** It was wrong about the *role*.

An application essay contains two schools:

| Role | Value | Source |
|---|---|---|
| `authored_by` | Columbia | the author's own affiliation — appears everywhere |
| `addressed_to` | UChicago | the actual subject of the document |

Collapsing both into one slot called `school` guarantees that the user's dominant affiliation
becomes a hub that swallows everything connected to it.

**Bliss BC2's citation order already separates these**: `Thing–Kind–Part–Property–Material–
Process–Operation–**Patient**–Product–Byproduct–**Agent**–Place–Time`. Agent and Patient have
been distinct facets for a century of classification theory.

**Apply to every template:**

| Template | Wrong | Right |
|---|---|---|
| Applications | `institution` | `applicant_school` / `target_school` |
| Client work | `client` | `our_firm` / `client` |
| Research | `institution` | `authoring_lab` / `funding_body` / `venue` |
| Finance | `institution` | `account_holder` / `issuing_bank` |

A dimension whose values can be produced by two different roles is not one dimension.

**Measured on the real corpus:** 89 files have a filename school that differs from their
in-content school, and **59 of those carry application-prompt language** — the role split is real
and common, not a corner case.

### Corpus-constant vs per-file dimensions — ask the first, extract the second

The same test showed `addressed_to` is reliably recoverable from the filename
(`Duke Supplemental.docx` → Duke, `U Chicago Supplemental Essay 2.docx` → UChicago), while
`authored_by` extracted per-file was **noise** — it returned whichever school sat near an email
address, giving `Georgetown shorts.docx` an `authored_by` of Johns Hopkins.

**Because `authored_by` is not a per-file property at all.** The user is one person; their
authoring institution is a property of *them and a time period*. Re-deriving it from 2,000
documents is how it became noise.

| Dimension type | How it is filled | Examples |
|---|---|---|
| **Corpus-constant** | **Asked once during template setup** | `authored_by`, `our_firm`, `account_holder`, `primary_affiliation` |
| **Per-file** | Extracted from content | `addressed_to`, `subject`, `term`, `doc_type`, `event` |

**This makes the setup questions a correctness mechanism, not a UX nicety.** One question —
"where do you study?" — permanently eliminates an entire class of extraction error across every
file, at zero per-file cost.

Template definitions therefore declare, per dimension, whether it is constant or extracted.

### Gazetteers need entity disambiguation

The same test resolved **Georgetown Preparatory School** (the user's high school) to **Georgetown
University**. Two distinct institutions, one name.

Gazetteer entries must be **type-qualified** (`university` / `secondary_school` / `hospital` /
`company`), and a match must be consistent with the dimension being filled — a `school` slot in
an academic template should prefer the university sense unless context says otherwise. Every
university with an affiliated prep school, hospital or press has this collision.

### Facet propagation — measured, and insufficient alone

Hold-out test on the real corpus: hide a confidently-extracted `school`, recover it from graph
neighbours by IDF-weighted vote with a margin gate.

| | |
|---|---|
| Precision | **92%** (35 correct, 3 wrong) |
| Coverage | **31%** — 84 of 122 correctly abstained |
| Graph density | 331 edges / 396 files, **average degree 1.7** |

**Propagation is validated as a mechanism and is not sufficient on its own.** The coverage limit
is graph sparsity, not the voting rule — the hub cap that correctly suppresses `gmail.com` also
thins the graph. Thresholds from 0.5 to 2.0 changed nothing, confirming the **margin gate** is
what produces the precision, not the weight cutoff.

This is the specific gap that **embeddings-as-retrieval** fill: they densify the candidate set,
and a bad retrieved candidate is rejected by the judge rather than silently creating an edge.

### Dimension order follows the Wall-Picture Principle

Ranganathan's rule, from faceted classification theory: **A precedes B if B cannot be understood
without A.** No mural without a wall.

`school / term / subject / work-type` is correct because `PHYS1401` does not identify a course
without knowing the school, and `Problem Set 4` is meaningless without the course. `subject /
term / school` fails the test. This gives a principled default for templates nobody has written
yet, rather than an intuition per template.

Corollary from the same theory: **time is structurally terminal** — Space and Time occur only in
the last round. A `year` dimension placed first fights the theory and, in practice, scatters
related work across years.

Freezing the order matters as much as choosing it: with *n* dimensions there are *n!* orders,
only one can be materialised, and **the choice determines what collocates**. UDC's own guidance
warns that inconsistent citation order across a collection destroys collocation. Changing a
template is therefore an explicit, reviewable operation, never a silent re-render.

### Template validator — hard limits from measured practice

Bergman et al. (JASIST 2010, n=296, 1,131 real files, 5,035 navigation steps) measured actual
personal folder structures: **mean depth 2.86, 82% of files at depth ≤4, mean 11.82 files per
folder.** Their regression `RetrievalTime = 4.956 + 2.236·Depth + 0.106·Size` gives a
depth/size exchange rate of **21.09**.

**Reject or warn on any template where:**

| Check | Limit | Why |
|---|---|---|
| Depth | **≤ 4 dimensions** | 82% of real retrievals happen at depth ≤4; no surviving personal method uses 5 |
| Branches per level | **≥ 3** | Fewer means the level earns nothing — delete the dimension |
| Files per leaf | **≤ ~21** | Past this, adding a level is measurably faster than scanning |

All three are one query against `facet`. Practitioner guidance independently converges: a
workable facet count is **3–7**, and every surviving personal method (PARA, Johnny.Decimal) uses
**1–3 dimensions with a hard cap**. Our 4-dimension examples sit at the outer edge of observed
practice — the fourth dimension must earn its place against the ≤21 check.

### Per-folder templates, and a first-class "matches nothing" path

**Heterogeneous corpora break faceting outright**, and `~/Downloads` is maximally heterogeneous —
there is no single template that applies to all of it. Templates are therefore scoped per folder,
and "this file matches no template" is a designed outcome routed to the review queue, not a
failure.

### The resolver contract — measured, and it matters more than the model

Naive slot extraction produces **confident, well-formed, completely wrong paths**. Measured on
300 real files, a first implementation returned `Georgetown/2024-Fall/SWCD5660/Exam` for a WashU
essay and `UNC/2026/Exam` for `Probability For Engineers.pdf` — because `unc` matched inside
"uncertainty" and `mit` inside "submit".

**Four rules, no machine learning, fixed 8 of 8 observed errors:**

1. **Word-boundary matching.** Never substring. This one bug alone produced most of the failures.
2. **Positional weighting.** Filename ×10, first ~1,200 chars ×3, remaining body ×0.4. A word in
   the title is not equal to a word on page 9.
3. **Rank candidates, never take the first match.** A document mentioning three schools must
   score them and pick the best, not whichever the dictionary reached first.
4. **Minimum score AND minimum margin before a slot fills.** Below either, the slot stays empty.

Effect on fill rates:

| Slot | naive | disciplined |
|---|---|---|
| school | 75% | **32%** |
| term | 70% | **32%** |
| work_type | 70% | **21%** |
| subject | 12% | **6%** |

**The lower numbers are the correct ones.** The naive rates were inflated by false positives;
most files genuinely have no school. This yields **high precision, low recall** — usually right,
often silent — which is recoverable by a better extractor. The inverse, high recall with low
precision, destroys trust and cannot be fixed by adding anything.

**Corollary: a neural extractor is a recall enhancement, not a correctness dependency.** If it is
slow, heavy or unavailable, disciplined gazetteer matching alone produces a correct-but-quiet
system. That is a shippable failure mode.

**An empty slot is a good outcome. A guessed slot is a bug.** The 6% subject fill rate is correct
behaviour — most files have no course code. The number to distrust is always the high one.

### Matching engine: Aho-Corasick, with the boundary check re-added by hand

Regex-per-gazetteer-key costs **102 ms/file** at our list sizes. `pyahocorasick` over 18,169
terms costs **0.047 ms/doc** — a **2,170× speedup**, 47 ms build, 100 KB install, BSD-3.

**Aho-Corasick matches substrings.** It will happily find `MIT` inside `SUMMIT` and `RH` inside
`NORTH` — the exact bug that produced `UNC` from "uncertainty". The boundary check is four lines
and the 0.047 ms figure *includes* it:

```python
for end, term in A.iter(low):
    start = end - len(term) + 1
    if (start == 0 or not low[start-1].isalnum()) and \
       (end + 1 >= len(low) or not low[end+1].isalnum()):
        yield term
```

Also **drop or context-gate gazetteer entries shorter than ~6 characters** (`RH`, `3M CO`,
`42 US`) — pure false-positive fuel. Use `pyahocorasick`, not FlashText (4× slower, unmaintained
since April 2025).

### Four validation layers — measured 20% → 75% precision at 0.037 ms/doc

A naive course-code pattern on real files matched **ZIP codes** (`NY 10172`, `MD 20852`),
**flight numbers** (`UA872`), and a **US visa form** (`DS-2019`) — 3 true of 15, **20% precision**.
Applied in this order, the layers reject 73% of matches and raise precision to **75%** with
recall unchanged:

1. **Negative structural gazetteer** — reject by shape: `US_STATE + 5 digits` = ZIP,
   `airline code + 3–4 digits` = flight, known form prefixes (`DS`, `I-`, `W-`).
2. **Context window** — require a positive cue within ±60 chars
   (`course|syllabus|credits|instructor|semester|prerequisite`) and reject on negative cues
   (`street|suite|zip|flight|visa|serial|model`). **This is what kills `VHX7000`**: a microscope
   model number sits near "magnification", never near "prerequisite".
3. **Positive gazetteer confirmation** for closed sets.
4. **Cross-extractor agreement** — accept when ≥2 of {rules, gazetteer, GLiNER, **filename**}
   agree. The filename is free and surprisingly good.

Cue lists need curation — one false positive survived because `SECTION` matched an academic cue.
Cap the residue with a confidence band: auto-accept above 0.85, queue 0.5–0.85 for review.

### Dates: never use fuzzy parsing

`dateutil.parse(fuzzy=True)` **fabricates dates out of our own field values**:

```
"APMA E2000 Final Exam"   → 2000-08-16     ← the course code became a year
"IEOR E4004"              → 4004-08-16
"Version 3.2 build 41"    → 2041-03-16
```

Use regex to find candidates, then `dateutil.parse(candidate)` **without fuzzy** — 0.016 ms/call,
zero fabrications. `dateparser` is 226× slower and only worth it for CJK dates (`2025年4月27日`),
which dateutil cannot parse at all.

**Academic terms defeat both libraries — 0 of 8 forms parsed.** `Spring 2025`, `AY 2024-25`,
`Michaelmas Term 2024` are regex-only territory; a purpose-built pattern gets 6/8 at 4.8 µs.

### GLiNER — scoped to `school`, `person`, `client` only

Measured against the disciplined gazetteer on 40 real documents: school fill **28% → 45%**, union
**48%** — **+20 points of recall at 75% precision on the increment**. It correctly found
`Stony Brook University`, `Tehran University`, `Georgetown Preparatory School` where rules
abstained.

**But it cannot do our other dimensions, at any phrasing:**

| Label | Score |
|---|---|
| `school` / `university` | **0.88 – 0.96** ✓ |
| `subject code` / `course code` | 0.30 – 0.38 ✗ |
| `document type` (every phrasing tried) | **returns nothing** ✗ |

So GLiNER will **not** fix the 6% subject or 21% work-type fill rates. Those stay on rules.

**Rules win ties.** Where both fired they disagreed on 4 of 10 — on a résumé the gazetteer said
`Columbia University` and GLiNER said `Georgetown Preparatory School`; both strings are in the
document. **Never let GLiNER overwrite a gazetteer hit; use it only where rules abstain**, and
apply the same positional weighting to its spans.

Costs and traps: 153M params, 610 MB weights, needs torch (560 MB venv), **261 ms/doc**.
**Silent truncation at 384 tokens** — no exception, no warning, so chunk explicitly. Threshold
**≥0.7** or quality collapses on forms (`person: '.'` at 0.73). **Apache-2.0 only from v2.1** —
v0/v1 are CC-BY-NC.

### Gazetteer sources — verified downloadable

| Set | Source | Size | Licence |
|---|---|---|---|
| Universities | `Hipo/university-domains-list` | 10,172 names, 2.2 MB | MIT |
| US public companies | SEC `company_tickers.json` | 7,997 names | US public domain |
| Names | US SSA baby-name files | — | public domain |
| Places | GeoNames | 10M+ | CC-BY |

### Expect a visible residual error rate

Berkeley's Flamenco study derived facet values semi-automatically and **roughly one quarter of
participants spontaneously commented on a confusing or misfiled classification** — the same
failure as our `VHX7000` and `Georgetown/Wash U` errors, found independently in 2003. IDF
weighting, type-diversity bans and context validation reduce it; they do not eliminate it.
**Budget the correction UI as a core feature, not a fallback.**

### Why this changes the technical problem, not just the UX

It converts **open-ended classification into structured slot-filling.**

| Without a template | With a template |
|---|---|
| "Invent a category for this file" | "Find the school, year, subject, work type" |
| Unverifiable — no ground truth exists | Verifiable — a slot is filled or it isn't |
| Confidence is a single opaque number | Confidence is per-slot and inspectable |
| Failure is a wrong folder | Failure is a named missing field |

This is the easier problem, and it is the one every incumbent avoids. It also plugs directly into
the fact extraction: **the template tells the extractor which facts matter.** `PHYS1401` stops
being an arbitrary shared string and becomes the *subject* slot; `Spring 2026` becomes the
*term* slot.

Every placement then carries a readable justification:

> `Columbia / 2026-Spring / PHYS1401 / Problem Sets`
> — document text contains `PHYS1401`, `Spring 2026`, `Problem Set 4`

And abstention becomes specific rather than numeric: *"I know the school, year and subject; I
could not determine the work type"* — a question the user can actually answer, instead of a
confidence score they have to interpret.

### How templates interact with the other two paths

Precedence, highest first:

1. **Template slots** — if a template is active and slots can be filled from extracted facts
2. **Existing folders** — classify into the teacher tree where a template slot is unfilled or no
   template is active
3. **Cluster and propose** — only for files that neither path can place

A template does not have to be complete. Unfilled dimensions collapse (no `Unknown/` folders in
the path), and the file is placed at the deepest level it has evidence for.

**Collapsing makes the path non-expressive, so the mapping must be persisted.** `Columbia/
PHYS1401/Problem Sets/` cannot be decomposed — is `PHYS1401` the term slot or the subject slot?
Since the filesystem is our source of truth and the graph is a rebuildable cache, a
rebuild-from-disk would silently lose every slot assignment. With *k* dimensions at per-slot fill
rate *p*, the ambiguous fraction is `1 − pᵏ` — at our measured fill rates, most of the corpus.

**Rule: persist `path_component → (dim, val)` in SQLite alongside every applied move.** The
pretty path stays pretty and stays decomposable. The alternative — expressive folder names like
`Columbia/subject=PHYS1401/` — is what the 1991 Semantic File System shipped, and it is ugly
enough that we take the sidecar instead.

---

## Facet storage — one table subsumes concept nodes and entity edges

Do not build a facet subsystem beside the graph. **A facet *is* a typed edge from a file to a
value node**, and modelling it that way collapses three earlier designs into one.

```sql
CREATE TABLE dim(id INTEGER PRIMARY KEY, name TEXT UNIQUE, ord INT);  -- citation order
CREATE TABLE val(id INTEGER PRIMARY KEY, dim_id INT, label TEXT,
                 canonical_id INT,                    -- → category_taxonomy
                 UNIQUE(dim_id, label));
CREATE TABLE facet(file_id INT, dim_id INT, val_id INT,
                   conf REAL, provenance TEXT,
                   PRIMARY KEY(file_id, dim_id, val_id)) WITHOUT ROWID;
CREATE INDEX ix_fv ON facet(dim_id, val_id, file_id);
CREATE INDEX ix_vf ON facet(val_id, file_id);
```

- **`val` rows are the concept nodes.** Two files sharing a `val_id` are graph neighbours with no
  extra edge table.
- **`facet` rows are the `shares_entity_with` edges, now typed by dimension.** `PHYS1401` stops
  being an untyped shared string and becomes `(subject, PHYS1401)` — the upgrade the fact-edge
  section argues for, delivered structurally.
- **Every `val.label` routes through the canonical taxonomy + alias table**, not just folder names.
- **Never add a uniqueness constraint on `(file_id, dim_id)`.** Multi-valued dimensions are real —
  Google Photos conceded exactly this in 2024 by allowing multiple categories per image.

**Measured at 100k files × 5 dimensions (425k facet rows, 18.2 MB):**

| Operation | Time |
|---|---|
| All files where `subject=X` | **0.81 ms** |
| Render `school/term/subject/work-type` | 175 ms → 18,675 leaves |
| **Re-render under a different dimension order** | **175–300 ms, zero re-analysis** |
| Query preview (counts for next dimension) | 45 ms |

At the v1 target of ~2k files this is sub-10 ms. **"Disk is a projection of the graph" is now a
measured property, not an aspiration.**

A denormalised wide table is ~1.8× faster and 7× smaller but cannot hold multi-valued dimensions,
per-slot confidence, or provenance, and adding a dimension becomes a schema migration. If that
1.8× is ever needed, materialise the wide table as a derived cache — a cache, not a store.

### One order materialised, N virtual

**Exactly one dimension order is written to disk at a time. All other orders are views computed
from `facet`.** Switching the materialised order is an explicit, journaled `plan → review →
apply`, like any other move.

This is where the 1991 Semantic File System failed: with field directories visible the tree is
*infinite*, and hiding them breaks `pwd`. Our "no FUSE, no virtual filesystem" non-goal already
dodges it; this rule makes the dodge explicit.

### Hand edits must survive re-projection

Adopted from Xerox PARC's Presto/Placeless (TOIS 2000): a collection is
**query + inclusion list + exclusion list**. Pure-query collections lose manual edits on
re-evaluation; pure-static collections never update. The three-part form is exactly *"the user
dragged this file out of `Problem Sets` — never put it back."*

### Facets are descriptive; fact edges are explanatory. Keep them separate.

Faceted classification lacks intra-facet relationships by design. **Do not express `version_of`,
`references`, `duplicate_of` or `same_event` as facets** — they are edges, they answer a
different question, and forcing them into dimensions loses both.

**Templates are inferred back, too.** If the teacher tree already looks like
`School/Year/Subject/`, the system proposes that as a detected template for confirmation rather
than making the user describe it. Detection is a proposal; the user confirms.

---

## The two-corpus model — how v1 avoids cold start

**Decided.** v1 runs over two folders with different roles:

| Role | What it is | What we do to it |
|---|---|---|
| **Teacher** | Any folder already organized sensibly — **including flat ones** | Extract facts, build folder profiles. **Never modified. Never moved. Read-only, always.** |
| **Student** | The messy folder (e.g. `~/Downloads`) | Every loose file scored against the teacher's folders, then placed |

**A flat folder is still a labelled set — the folder name is the label.** Confirmed on the real
machine: `Desktop/Python 1006` (36 files, no subfolders), `Desktop/SAT Tests` (19),
`Desktop/research` (28), `Desktop/OMNIGENE GUT` (21), `Desktop/外泌體` (50),
`Desktop/Chinese University Application Materials` (11).

Every file in `Python 1006` carries `subject = Python 1006`; every file in `SAT Tests` carries
`work_type = Test`. That is ~165 perfectly labelled examples at **zero extraction cost**, and it
is what teaches the system what a `Python 1006` document actually looks like. **Path depth is
irrelevant — coherence is what matters**, which is also DEVONthink's documented finding.

Folder coherence is measured before a folder is trusted as a teacher: a dumping ground with no
consistent content teaches nothing and is excluded, per-folder.

This is the direct answer to the cold-start problem. DEVONthink's own manual concedes the
approach *"works best with a large database that is structured somewhat accurately"* and that with
an empty group *"the AI doesn't know what belongs in there."* A 2,000-file unstructured Downloads
folder has nothing to learn from — **so we learn from a folder that does, and spend nothing
inventing a taxonomy the user already built.**

**Destination policy (default):** the learned folder structure is **replicated under the student
root**, e.g. `~/Downloads/Academics/Syllabi/`. Files are never moved into the teacher tree, and
the teacher tree is never written to. This keeps a curated folder safe from a tool that is still
earning trust, and it keeps every move reversible inside one root. Moving directly into the
teacher tree is a later opt-in, not a default.

The teacher folder is also the honest source of folder *names*: they are the user's own words,
already proven to make sense to them, and they need no LLM to invent.

---

## The decision architecture — rules build the base, the LLM judges on top

**This supersedes any earlier framing of rules *versus* model.** Disciplined rules alone reach
only ~32% recall, because most files simply do not contain the fact being looked for. A model
alone reproduces AI File Sorter: a filename in, an invented category out, slow and inconsistent.

**Rules, the graph and learned profiles assemble an evidence base. The LLM makes the judgment
inside it.**

```
DETERMINISTIC BASE (fast, high precision, never hallucinates)
    rules + gazetteers   → facts with text-span provenance
    graph propagation    → what this file's neighbours are, and where they went
    embeddings           → RETRIEVE candidates (never create edges)
    learned profiles     → what each existing folder's contents look like
        ↓  assemble
EVIDENCE PACKET  (per group)
    · member files, each with its facts and the span that produced them
    · the fact this group SHARES — the stated reason the group exists
    · weakly-attached members, flagged
    · candidate destination folders, scored, with profiles
    · sibling groups already judged
        ↓
LLM JUDGMENT (batched, per group)
    → { coherent? · label · split_into[] · placements[] · overrides[] }
        ↓
PLACEMENT + the model's reason + the evidence beneath it
```

**The difference from every incumbent is the input.** AI File Sorter hands a model a filename and
asks it to invent a category. We hand it a short list of evidenced candidates and ask it to
choose. A constrained judgment is more accurate, far cheaper, explainable, and consistent across
runs — because the candidate list comes from the corpus, not from the model's imagination.

### Each component finally does what it is good at

| Layer | Job | Why it belongs here |
|---|---|---|
| Rules + gazetteers | Produce facts with provenance | 0.047 ms, high precision, cannot hallucinate |
| Graph propagation | Supply a file with its neighbours' context | Recovers files that contain nothing themselves |
| Embeddings | **Retrieve candidates** | Safe here — a bad candidate is rejected by the judge rather than silently welding two clusters together |
| Learned profiles | Score candidate folders | 36 files in `Python 1006` define what belongs there |
| **LLM** | **Weigh conflicting evidence** | The only component that can |

Embeddings caused the 73-file grab-bag when they were allowed to *create edges*. Used for
retrieval into an evidence packet, that failure mode disappears.

### Groups overlap — the template, not the clustering, builds the hierarchy

A file belongs to many groups at once: `Probability For Engineers.pdf` is in the Columbia set,
the probability set, and the Fall-2024 set. Leiden forces every file into exactly one community,
which is precisely how the 73-file grab-bag formed — it had to put those files *somewhere*.

**The citation order turns overlapping facet sets into one hierarchy:**

```
template: school / term / subject / work-type
  level 1 = files sharing school     → {Columbia: 340}, {Yale: 12} …
  level 2 = within Columbia, sharing term
  level 3 = within that, sharing subject
```

Every node in that hierarchy is coherent **by construction** — its members share a *fact*, not a
similarity score.

**This demotes clustering substantially, and it should be demoted.** Leiden's remaining jobs are:
discovering candidate *values* for an unknown facet ("these 30 files clearly belong together —
what is this?"), and grouping the remainder that matches no template. It is no longer what builds
the folder tree, which is the role in which it repeatedly failed.

### Judgment runs bottom-up, and splitting is well-posed

Deepest groups first, then parents judged with their children's labels as evidence — the
bottom-up order GraphRAG uses for community reports.

**Splitting works here because every group has a stated reason for existing.** The model is not
asked to re-partition the corpus from nothing; it is asked *"these 12 files all contain
`PHYS1401` — do they belong together?"* and can answer *"11 do; the 12th only cites it in a
bibliography."* That is a judgment on evidence.

Groups and subgroups are both first-class: a split produces new leaves which are re-judged, and
the resulting label hierarchy is the folder tree.

### Override authority — granted, with three constraints

The LLM may overrule an extracted fact. This is how `Wash U .docx` is rescued when a rule latched
onto a passing mention of Georgetown. It stays safe because:

1. **The original fact is never deleted** — it is marked *superseded by judgment*, with the
   model's reason stored beside it. Both remain visible.
2. **Overrides are file-local.** Overruling `school` for one document never changes that fact for
   any other file, so a bad judgment cannot cascade.
3. **Overrides sort to the top of the review queue** — they are the highest-information items in
   the run, the exact points where deterministic evidence and judgment disagree.

**An override is also the best training signal available.** A model repeatedly overruling the
same rule is reporting that the rule is wrong — which is how gazetteers and cue lists improve
without hand-tuning.

---

## Placement: classify into EXISTING folders first, cluster only for the remainder

**This is the most important correction in the spec, and it comes from the incumbents.**

Every long-lived product derives its label space from the user's own filing, never from content
alone:

| Product | Label space source | Shipping since |
|---|---|---|
| DEVONthink | the user's existing groups | 2002 |
| Paperless-ngx | documents the user filed out of the inbox | 2020 |
| OpenText (US11893031B2) | *"documents previously filed to folders"* | 2021 |
| Google Drive | *"your organizing patterns"* | 2026 |

**DEVONthink shipped the opposite approach — "Auto Group", inventing groups from content — and
removed it.** The developer's reason: *"almost unused"* and it generated *"support requests as it
didn't work the way people would like/assume."* That is the 24-year incumbent, with the best
engine in the category, reporting that automatic category *invention* fails as a product while
automatic *assignment into user-defined categories* succeeds.

**Therefore the order of operations is:**

1. **Classify into an existing folder** — the primary path, for every file.
2. **Abstain** when the answer is not clear (below).
3. **Cluster only what abstained**, and propose new folders *only* for coherent leftover groups —
   presented as proposals, never applied silently.

Clustering is demoted from "how the taxonomy is invented" to "how we handle what doesn't fit."

### The scoring function — adopted from DEVONthink

```
score(folder) = f( mean similarity to ALL members of the folder,
                   max  similarity to the single best member )
```

The mean term lets a large coherent folder win; the max term lets a small folder holding one
near-duplicate win. It handles both regimes in a few lines, requires no training and no persisted
model, and therefore reacts instantly to refiling and can never go stale. Our similarity is the
fact-edge weight plus the embedding fallback, not raw cosine.

### Abstain on TWO conditions, not one

```
place    if  top_score ≥ P10(top_score over this corpus)
         AND (top_score − second_score) ≥ margin
abstain  otherwise
```

DEVONthink abstains when *"multiple suggestions have almost the same score **OR** the top score is
too weak."* A margin test is not a threshold test, and both are required.

The counter-example is decisive: **Paperless-ngx ships plain argmax with no abstention at all**
(`if correspondent_id != -1: return correspondent_id` — no `predict_proba`, no threshold, no
margin). A user with 464 documents and 78 correspondents reported *the exact same correspondent
and two tags assigned to every single document*, with no diagnostic. DEVONthink fails silently
and frustratingly; paperless-ngx fails loudly and confidently wrong. **Silence is the better
failure**, provided it is visible — surface abstentions as a review queue, never as nothing
happening.

When multiple folders fit nearly equally, DEVONthink files the document into **all** of them as
replicants. Our equivalent: present the top-N as a choice rather than picking one.

### Cold start — state it honestly

With no existing folders, this approach does not work, and DEVONthink says so in its own manual:
*"works best with a large database that is structured somewhat accurately."* Their guidance is
that **group coherence and mutual distinctness are everything, and hierarchy depth is
irrelevant** — *"since [the group] is empty, the AI doesn't know what belongs in there."*

So an unorganised folder falls back to the cluster-and-propose path, and the product must say
which mode it is in rather than silently producing worse results.

---

## Escalation is not abstention — they are different decisions

These were conflated in an earlier draft. They answer different questions and have different
consequences:

| | Question | Trigger | Consequence |
|---|---|---|---|
| **Escalation** | *Do we have enough information yet?* | Tier 1.5 extraction produced too few facts to score confidently | Run Tier 3 (OCR / vision / LLM), then **re-score**. A cost decision |
| **Abstention** | *Do we know which folder, now that we have the information?* | Weak top score **or** narrow top-2 margin, after all available analysis | Route to the review queue or the cluster-and-propose path. A confidence decision |

A file may escalate and then place cleanly. A file may never escalate — plenty of information,
genuinely ambiguous destination — and still abstain. **Escalation spends money to reduce
uncertainty; abstention admits uncertainty that money did not remove.**

### Thresholds are quantiles of the user's own distribution, never constants

Both gates calibrate against the corpus in front of them:

- escalation threshold = fact-count / score percentile that targets the configured spend
- abstention threshold = `P10(top_score)` plus a margin requirement

Measured on 8,080 unique filenames *(synthetic)*: a fixed `top-1 cosine ≥ 0.90` rule placed
**89.5% at 99.9% accuracy** and escalated 10.5%, with accuracy on the escalated slice at 81.6% —
so the rule does route genuinely harder cases rather than escalating at random. **But the
constant will not transfer**, which is why it ships as a quantile with one honest knob
(`--automation-target 0.90`).

This is the same principle as Meta's event-clustering patent, which groups photos when
displacement is within **1 SD of that camera roll's own average movement** rather than a
hardcoded radius — a user who shoots in one apartment and one who shoots on road trips get
different effective thresholds for free.

**Not every file receives a placement.** Abstaining is a valid, visible outcome — surfaced as a
review queue, never as silence. DEVONthink's most common bug report is *"nothing happens when I
click Classify"*, which is abstention working correctly and being invisible.

---

## Safety

- **Analysis never moves files.** It produces a plan.
- **Single mutation chokepoint.** All moves and renames go through one function.
- **Journal before move**: `(run_id, scan_root, src, dst, content_hash, status)`.
- Runs carry status `in_progress | complete | reversed`, so an **interrupted run is still
  undoable** — the case where undo matters most.
- **No overwrite.** Collisions resolve to `name (1).ext`; `dst` in the plan is a proposal and
  apply computes and journals the final path.
- **Every `dst` must resolve inside `scan_root`** after symlink resolution. Plans are
  user-editable, therefore user-controlled input.
- **Undo** removes destination directories only if empty after restore, marks the run reversed,
  and is idempotent.
- Destination directories are marked, so re-scanning never re-ingests an already-sorted tree.
- **Protected zones**: git repos, app bundles, `node_modules`, system directories — never
  traversed, never moved.
- Files only. Directories are never moved; symlinks skipped.

---

## The fitness function is built first

**Before any placement code.** Two metrics, and the second one is the one the market actually
uses.

**1. Acceptance rate — the primary metric.** The fraction of proposed placements the user accepts
without editing, plus per-folder recall. This is what Google instruments for its Gemini
organiser ("User acceptance" tracked over 180 days) instead of accuracy, and it is the honest
measure for a task where there is no single right answer.

**The absence of published accuracy is itself the finding:** DEVONthink (24 years) and
paperless-ngx (6 years) — the two products closest to this one — have **never published an
accuracy number**, because for open-ended "which folder does this belong in", accuracy against
fixed ground truth is not meaningful.

**2. ARI and pairwise co-location** on a hand-labelled sample, as the offline regression metric —
scoring *whether files that belong together end up together*, not destination-equality. A
discovered taxonomy scores 0% against fixed labels by construction, which tells you nothing.

**Report per-folder recall, never an aggregate.** Google's published deployment bar for its own
Drive classifier is **>80% recall per class** (50–80% medium, <50% low) — the only fully
documented threshold in the category, and it is per-class for a reason.

Calibration warning that recurs across vendors: models are miscalibrated, and a reported 95%
confidence may be right ~80% of the time. **Threshold to the cost of the error, not to average
accuracy.** Misfiling a tax document costs more than misfiling a meme.

Without this harness you cannot tell whether content extraction helped, whether hub-exclusion
fixed the grab-bag clusters, or whether a model swap made things worse. Every performance number
in this document measures speed and tree shape. **None of them measure whether the placements
are right.**

---

## What we reference, and what we cannot

### Reference directly

| Source | What we take |
|---|---|
| **graphify** | Two-level dirty detection; per-tier independent cache invalidation; unversioned cache for the paid tier; provenance + discrete confidence on every edge; hyperedges for "these N form one group"; MinHash+LSH near-duplicate detection (no scipy); hub-exclusion + majority-vote reattachment; community member signatures; determinism discipline; trigram+IDF lexical prefilter. **Not** its node-link JSON persistence — SQLite is 1.6 ms vs 410 ms for the equivalent parse |
| **`organize`** (MIT) | The safe-move layer: conflict resolution, dry-run. Worth reading before writing our own |
| **AI File Sorter** | **The canonical taxonomy + alias table** (its best idea). Product loop shape: preview → approve → undo. Its OOXML extraction approach (unzip → parse XML → strip tags) validates our format list. *(Clean-room only — AGPL-3.0.)* |
| **DEVONthink** (2002–) | **The Classify score**: mean similarity to all group members + max similarity to the best member. **Two-condition abstention**: weak top score OR narrow top-2 margin. **No persisted model** — recomputed from the corpus, so refiling takes effect instantly and nothing goes stale. Per-item "exclude from classification" as a shipped feature. Rare-term weighting (their Concordance exposes frequency, group count, length, and a corpus-relative weight) |
| **Google Drive "Organize My Files"** | The shipped review UX: suggest → per-item checkboxes → edit destination inline → approve batch. **The rejection ledger**: a declined (file, folder) pair is not suggested again for 30 days — cheap negative feedback with no retraining. **Asymmetric undo**: undoing moves never deletes folders it created |
| **Apple Photos** | **Two-pass clustering**: a conservative precision-first pass that deliberately over-fragments, then a merge pass — strictly better than one-shot clustering at a single threshold. Assign new items by sparse coding rather than nearest-neighbour, which Apple notes wins *"when the size of each cluster is relatively small"* — i.e. cold start. **Schedule expensive work for idle time**; structure by free metadata immediately |
| **Meta / Microsoft event-clustering patents** | Derive thresholds from **the user's own data distribution** (Meta: group photos if displacement is within 1 SD of that camera roll's average movement) rather than hardcoding. Same principle as our P10 quantile |
| **Hazel** (~2006–, no ML ever) | **Explainability is the trust mechanism, not accuracy.** Every signal is previewable before a rule fires — users can see exactly what text was extracted and why it matched. A rule written in 2015 still works in 2026 |
| **OpenText** (US11893031B2) | Stage cheap→expensive: **tolerate false positives** in rare-indicator extraction because a weighted scoring stage cleans up. Weight positive and negative evidence differently |
| **CMU Connections (SOSP '05)** | Co-access/temporal edges: no model, no embeddings, measurably better retrieval at <1% index size |
| **BERTopic / GraphRAG** | Centroid-nearest representative selection; frozen community reports; batched community summarisation |

### Cannot reference

| Source | Why |
|---|---|
| **graphify's extractors, edge logic, node schema, clustering** | Wrong domain. Its whitelist admits only **65.7%** of the real `~/Downloads` — 1,677 of 4,896 files silently dropped (extensionless, `.csv`, `.heic`, `.zip`, `.pptx`). Of what it *does* admit, `.json`/`.py`/`.js` route to the AST path and become import graphs of random downloaded source files. Its nodes carry no path, size, mtime, MIME, or content hash |
| **graphify's non-code cost model** | ~1.5K tokens/file → the real corpus would be **~7M tokens per full build** |
| **graphify's update path** | O(whole graph), not O(delta): 9.3–12.5 s for *zero* changed files, 15.8 s for one, because it re-runs Leiden globally and rewrites the entire graph plus HTML on every change. **This is the specific failure we must not inherit** |
| **AI File Sorter source** | AGPL-3.0 |
| **GraphRAG's per-chunk LLM extraction** | $20–500 per corpus, ~4,000 calls per textbook. Microsoft retreated within 7 months (LazyGraphRAG: 0.1% of index cost) |
| **Any design requiring the user to tag files** | macOS Finder tags: 56% of users never use them. The most consistently replicated finding in the literature |
| **Inventing categories from content as the primary mechanism** | **DEVONthink shipped "Auto Group" and removed it** — *"almost unused"*, and it generated *"support requests as it didn't work the way people would like/assume."* No shipping incumbent invents a label space from content. Clustering is for the remainder, not the main path |
| **Argmax with no abstention** | Paperless-ngx returns its top prediction unconditionally — no threshold, no margin, no `predict_proba`. Real report: 464 documents, 78 correspondents, **the same correspondent assigned to every single document**, with no diagnostic |
| **A classifier that cannot say its training set is degenerate** | Paperless-ngx's `min_df=0.01` silently drops any label appearing in <1% of documents, and its own docs warn that a two-class corpus assigns one of those two to *any* new document. It never tells the user. **Detect and report a degenerate state explicitly** |

### Historical failure modes we design around

| Mechanism | Casualties | Our rule |
|---|---|---|
| Central store as system of record | WinFS (cancelled), Nepomuk (3.4 GB DB, >1 GB RAM idle, removed from KDE), Tagsistant (corruption → total metadata loss) | Graph is a disposable derived cache with a hard resource ceiling |
| Requiring user curation | Finder tags, every tag-filesystem | 100% inferred |
| Autonomy without review | llama-fs trust backlash; vendors call it "silent damage" | Reviewable diff, per-item opt-out, undo |
| **A component promising semantics it cannot deliver** | AI File Sorter's `local-hash-v1`: a 128-dim signed FNV-1a hash presented through a `taxonomy_embeddings` table, an `embedding_model` column and a `cosine_similarity` function. Purely lexical, collision-saturated, scored up to **100** against an exact category match worth **6** — and its top-1 result **silently overrides the model's answer for every file** (`CategorizationService.cpp:1298`) | If we cannot afford real semantics, ship honest lexical retrieval with honest weights and name it that. **No component may override a stronger signal, and no override may be invisible to the user.** The schema will otherwise convince us it works, and its noise is indistinguishable from bad model output |
| **Feeding a model's own output back as ground truth** | AI File Sorter's learning store records every *confirmed* row with no comparison against what was originally suggested, and has **no negative signal anywhere in its schema** — a reinforcement loop that amplifies early mistakes | Record the original suggestion **alongside** the user's final choice, so a correction is distinguishable from a confirmation. An unedited approval and a rejection are different facts |
| Similarity-graph hairball | Documented in note-graph tools | Mutual-kNN, not top-k; measured avg degree 5.06 on the real corpus |

---

## Risks

| Risk | Evidence | Mitigation |
|---|---|---|
| **Filenames alone barely beat `GROUP BY extension`** | ARI 0.440 vs 0.321 — +0.12 for ~1000× compute | The cascade *is* the product. Cheap path for the confident ~90%, real content extraction for the escalated ~10%. If we ship filenames-only we ship a prettier `GROUP BY extension` with an LLM writing folder names |
| Leiden's resolution knob stops working above ~5k | 352 clusters at res=0.1 vs 374 at res=1.5 — the kNN graph fragments into ~350 near-disconnected components Leiden cannot merge | Accept 40–55× reduction, not 30×. Batch labeling absorbs the cost |
| Clusters may not be nameable at all | Independent finding: items far from a centroid carry mixed intent; TnT-LLM refuses to let clusters become taxonomy categories | Cohesion threshold gates naming; low-cohesion clusters split or route to review rather than receiving an invented name |
| Daemon is a background process touching files | The trust wall is emotional, not technical | Default `suggest`, not `auto`. Daemon reads and plans; it never moves without the configured policy |
| Benchmark corpus was synthetic | Stated by the benchmarking agent | The fitness function re-measures everything on real labelled files before any threshold is trusted |

---

## Build phases

**Scope discipline: one small folder, done properly, before anything scales.** Phases 0–2 target
a single folder of a few hundred files — hand-checkable in one sitting. Multi-root, whole-drive
and cross-tree work does not start until placement quality on that one folder is proven by the
Phase 0 scorer. Accuracy first; scale is a later problem and an easier one.

**Phase 0 — fitness function.** Hand-label a small real folder. Build the ARI + pairwise
co-location scorer and a reproducible harness. Nothing else starts until this runs.

**Phase 1 — content extraction and the fact graph. No embeddings at all.** Scan, cache chain,
Tier-1 filesystem facts, **Tier-1.5 content extraction for every file** (PDF/DOCX text +
metadata, EXIF, screenshot detection, OCR routing, HEIC support), entity extraction (codes,
authors, organisations, events), EXTRACTED edges only, graph persistence, and `explain` for any
edge. Score it.

This is the whole thesis in one phase: a graph built entirely from **facts read out of the
files**, with zero guessing and zero model calls. It already collapses the 488 duplicates, groups
the 270 photos by event, and links documents that share a course code or an author. **Everything
later must beat this baseline or it does not ship.**

**Phase 2 — classify into existing folders, then cluster the remainder.** The DEVONthink-style
scorer (mean + max similarity to folder members) over the Phase 1 fact graph, with two-condition
abstention. Then, for abstained files only: mutual-kNN, Leiden with hub exclusion, recursive
splitting for nesting, batched labeling of *proposed* folders, frozen once accepted. Embeddings
enter here as `AMBIGUOUS` fallback edges for files whose extraction came up empty.

Score against Phase 1 at every step — **if embeddings do not measurably improve on the fact
graph, they do not go in.** Same test for clustering: if classify-into-existing plus a review
queue scores as well as clustering the remainder, the cluster path stays off by default. The
incumbent that shipped automatic group invention removed it.

**Phase 3 — placement and safety.** Escalation rule, plan/review/apply/undo, per-folder policy,
protected zones.

**Phase 4 — incremental ingest.** New-file attachment via frozen-label kNN vote. Measure
one-shot CLI cold start against watch-mode need; **add a resident daemon only if the measurement
justifies it**, not by default.

**Phase 5 — web UI.** Preview, streaming results, the graph view, AMBIGUOUS confirm/reject,
ETA before analysis begins.

**Later — learning loop.** Corrections are recorded from Phase 3 onward; acting on them comes
after placement quality is proven.

---

## Open questions

1. **Project name.** `filegraph` is a placeholder.
2. **Concept-node extraction depth.** Cheap signals only is locked; whether document *titles* and
   *authors* count as cheap depends on extraction cost per format — measure in Phase 1.
3. ~~Static embeddings.~~ **Resolved** — measured 230× faster on the real corpus and modestly
   worse at clustering. Folded into Tier 2: static embedder by default, content peek promoted to
   default with the savings, both embedders A/B'd through the Phase 0 scorer before committing.
4. **Cloud/local/hybrid mode selection and the ETA estimator.** Required by the product brief,
   not yet designed. Needs a per-device calibration run.

5. **Cross-language grouping — needs a product decision before Phase 2.** After normalisation,
   files about the same concept in different languages land in **separate communities**:
   `invoice` / `請求書` / `发票` becomes three folders, not one. Pairwise similarity between them
   is high (0.85–0.91), but mutual-kNN with k=10 connects a Japanese file to its ten nearest
   Japanese files long before it reaches the English twin. Measured: 121 communities for 40
   ground-truth topics ≈ 40 × 3 languages, at purity 1.00 — every community is *pure*, there are
   simply three per concept. Options: accept language-separated subfolders (arguably correct for
   a real person's files), add explicit top-1 cross-language edges, or raise k. **This is
   invisible in pairwise-similarity testing and only appears end-to-end.**

6. **Apple Vision in a headless context is unverified.** It was benchmarked in a normal desktop
   session. Whether `VNRecognizeTextRequest` works over SSH with no window server is **untested**,
   and it gates any future daemon or scheduled-run design. Check before relying on it.

7. **Contradictory measurement to resolve in Phase 2.** One agent measured fastembed padding
   every input to a fixed length (**19× penalty**, 512 three-token strings costing the same as
   512 360-token strings); another measured throughput tracking real token count (48/s at
   ~10 tokens vs 7/s at ~500), concluding no padding waste. Both cannot be right. It does not
   block the design — the static embedder makes it moot — but it must be settled before any
   neural fallback is used, and it is a reminder that a single benchmark run is not evidence.

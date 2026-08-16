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
| Taxonomy | **Discovered**, not whitelisted. Frozen once labelled |
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
  "depth_tier": 1,
  "community": 47, "community_path": ["Academics", "Syllabi"],
  "confidence": 0.94
}
```

`concept` nodes are projects, people, organisations, courses, topics — extracted **only from
cheap signals** (filename tokens, folder names, document title/author metadata, EXIF). Files
attach to them; concepts also link to each other. Both node types participate in clustering.

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

Measured on the real corpus:

| Type | ms/file | Corpus cost | Facts extracted |
|---|---|---|---|
| PDF | **30.9** | 811 files → 25 s | Title, author, producer, dates, first-page text, headings, DOIs, course/ID codes |
| DOCX | **12.5** | 331 → 4 s | Core properties (author, company, title), headings, body text |
| PNG | 14.7 | 128 → 2 s | Dimensions, EXIF, screenshot detection |
| JPEG | 92.3 | 115 → 11 s | EXIF: camera, timestamp, GPS |
| JPG/WEBP/TIF | 2–4 | ~130 → <1 s | as above |

**Whole-corpus content extraction ≈ 45 seconds for ~2,000 files.** Content-first is not a
speed sacrifice — it is roughly the cost of one AI File Sorter LLM call, for the entire folder.

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

Reliable rule: camera EXIF ⇒ photo. Otherwise match against a table of known screen resolutions,
and **OCR to decide** — UI chrome and dense text ⇒ screenshot; a scene ⇒ photo with stripped
metadata. A screenshot's *text is its content*; grouping screenshots by anything else discards
the only information they carry.

**HEIC requires `pillow_heif.register_heif_opener()`.** Without it all 87 HEIC files in the
corpus fail to open — measured 40/40 `UnidentifiedImageError`. Silent blindness to 4% of the
corpus.

**Caveat measured on real files:** document metadata is a signal, not gospel — several files
report `author: python-docx` because a script last touched them. Metadata corroborates; it never
decides alone.

### Tier 2 — embeddings (demoted to a fallback)

**Embeddings are the last resort, not the primary signal.** They run over *extracted content*
(headings, first-page text, OCR output, document title) — the filename is a minor additional
input, never the main one.

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

## Taxonomy is frozen after first labeling

Measured two ways, independently. Adding 50 files to 300 churns **~28% of Leiden's assignments**
(ARI 0.715 across 5 trials). On 2,000 files + 40 new, cold re-clustering moved **350 of 2,000
files into different folders**. If clusters are folders and we re-cluster on every change, files
re-file themselves constantly. That alone would make the product unusable.

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
| Photo near-dup | `imagehash` | pHash/dHash | BSD-2 |
| Doc near-dup | `datasketch` MinHash-LSH | | MIT |

Budget: **~120 MB installed, ~0.6 s CLI cold start, 100k files embedded in under 4 seconds.**

**Rejected with cause:** `PyMuPDF` (AGPL-3.0 or paid) · `leidenalg` / `python-igraph` (GPL) ·
`graspologic` full (514 MB, 16.3 s import, caps at py<3.13 — use `graspologic-native`) ·
`hnswlib` (no arm64 wheel) · `sentence-transformers` (9.75 s import) · `lancedb` (2.0 s import) ·
`chromadb` (1.1 s import) · `kuzu` (archived 2025-10-10) · NetworkX `leiden_communities`
(dispatch-only stub, raises `NotImplementedError`) · `rustworkx` (no community detection at all).

---

## Placement and escalation

```
auto-place  if  top1_sim ≥ P10(top1_sim)  AND  neighbor_agreement ≥ 0.6
escalate    otherwise
```

Measured on 8,080 unique filenames *(synthetic)*: a `top-1 cosine ≥ 0.90` rule auto-placed
**89.5% at 99.9% accuracy**, escalating 10.5%. Accuracy on the escalated slice was 81.6% —
confirming the rule routes genuinely hard cases rather than escalating at random.

**The constant will not transfer between corpora.** Ship the threshold as a **quantile of the
user's own similarity distribution**, not a magic number. That auto-targets the automation rate
on any corpus and exposes exactly one honest knob (`--automation-target 0.90`).

Escalated files go to Tier 3 deep extraction, then to the LLM. Every file still receives a
placement — **this is a cost tier, not an abstention gate.**

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

**Before any placement code.** A scoring harness over a hand-labelled sample of the user's own
files, reporting **Adjusted Rand Index and pairwise co-location precision/recall**.

Not destination-equality: a discovered taxonomy scores 0% against fixed labels by construction,
which tells you nothing. We are scoring *whether files that belong together end up together*.

Without this you cannot tell whether content extraction helped, whether hub-exclusion fixed the
grab-bag clusters, or whether a model swap made things worse. Every performance number in this
document measures speed and tree shape. **None of them measure whether the placements are right.**

---

## What we reference, and what we cannot

### Reference directly

| Source | What we take |
|---|---|
| **graphify** | Two-level dirty detection; per-tier independent cache invalidation; unversioned cache for the paid tier; provenance + discrete confidence on every edge; hyperedges for "these N form one group"; MinHash+LSH near-duplicate detection (no scipy); hub-exclusion + majority-vote reattachment; community member signatures; determinism discipline; trigram+IDF lexical prefilter. **Not** its node-link JSON persistence — SQLite is 1.6 ms vs 410 ms for the equivalent parse |
| **`organize`** (MIT) | The safe-move layer: conflict resolution, dry-run. Worth reading before writing our own |
| **AI File Sorter** | **The canonical taxonomy + alias table** (its best idea). Product loop shape: preview → approve → undo. Its OOXML extraction approach (unzip → parse XML → strip tags) validates our format list. *(Clean-room only — AGPL-3.0.)* |
| **Google Drive "Organize My Files"** | The shipped review UX: suggest → per-item checkboxes → edit destination inline → approve batch |
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

**Phase 2 — clustering, and embeddings only where extraction came up empty.** Mutual-kNN over
extracted content, Leiden with hub exclusion, recursive splitting for nesting, batched cluster
labeling, frozen taxonomy. Embeddings enter here as `AMBIGUOUS` fallback edges. Score against
Phase 1 — **if embeddings do not measurably improve on the fact graph, they do not go in.**

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

6. **Contradictory measurement to resolve in Phase 2.** One agent measured fastembed padding
   every input to a fixed length (**19× penalty**, 512 three-token strings costing the same as
   512 360-token strings); another measured throughput tracking real token count (48/s at
   ~10 tokens vs 7/s at ~500), concluding no padding waste. Both cannot be right. It does not
   block the design — the static embedder makes it moot — but it must be settled before any
   neural fallback is used, and it is a reminder that a single benchmark run is not evidence.

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
| Interface | **CLI engine + thin local web UI**, both talking to a resident daemon |
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

### Why a daemon is not optional

| | per new file |
|---|---|
| Warm process | **10–20 ms** → 50–100 files/sec |
| Cold process (imports + ONNX session init) | **2.3–12.8 s** → 0.1–0.4 files/sec |

Cold start dominates the actual work by 100–1000×. A one-shot CLI would spend longer importing
`onnxruntime` than a small local model takes to answer, and the entire architectural advantage
evaporates. The CLI and web UI are clients; the daemon holds the model session, the graph, and
the index.

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
| **EXTRACTED** | 1.0 | `duplicate_of`, `version_of`, `in_folder`, `same_session_as`, `references`, `attachment_of` | Content hash equality, `(n)` suffix + hash, directory containment, mtime window, in-document URL/citation, EXIF |
| **INFERRED** | 0.5 | `near_duplicate_of`, `same_project_as`, `shares_entity_with` | MinHash/LSH, pHash, shared concept node, shared metadata author |
| **AMBIGUOUS** | 0.2 | `similar_to` | Embedding cosine — **and nothing else** |

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

### Tier 1 — free signals (all files)

Name, extension, MIME, size, mtime/ctime, directory position, content hash, `(n)` duplicate
detection, EXIF for images, embedded document metadata (title, author, created-by). No model,
no embedding. Resolves duplicates and photo grouping outright.

### Tier 2 — embeddings (all files)

Normalised filename plus, where cheap, a content peek: first ~2 KB of text files, page 1 of
PDFs, archive manifest listings.

- **Model: `multilingual-e5-small`** (384-dim). English-only models are a **correctness bug**
  here, not a quality preference — they tokenise the 55 CJK filenames to `[UNK]` fragments, so
  those files cluster together *because they are unrepresented*, and the labeller names that
  false cluster plausibly.
- **Drive `tokenizers` + `onnxruntime` directly with dynamic padding.** fastembed pads every
  input to a fixed length — measured **19× penalty** on short strings (140 texts/s vs 38–55).
- Use the `passage: ` prefix consistently.

### Tier 3 — deep extraction (escalated ~10% only)

PDF/DOCX text, OCR, vision captions. Triggered by the escalation rule, never run wholesale.

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

## Taxonomy is frozen after first labeling

Measured: adding 50 files to 300 churns **~28% of Leiden's existing assignments**
(ARI 0.715, consistent across 5 trials, min 0.685). If clusters are folders and we re-cluster on
every change, files re-file themselves constantly. That alone would make the product unusable.

**Therefore:**

1. Cluster and label **once** to establish the taxonomy.
2. Persist labels, centroids, and member signatures.
3. Assign new files by **kNN vote into the frozen set** — an O(1) query, no re-partition.
4. Re-cluster **only** on an explicit user-triggered reorganise.

This also makes incremental ingest trivial: single-file kNN is 0.79 ms at 20k vectors and
9.8 ms brute-force even at 100k. **Per-file queries need no ANN index at all.** hnswlib is
needed only for the initial bulk graph build, above ~20k vectors.

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
| **graphify** | Two-level dirty detection; per-tier independent cache invalidation; unversioned cache for the paid tier; provenance + discrete confidence on every edge; hyperedges for "these N form one group"; MinHash+LSH near-duplicate detection (no scipy); hub-exclusion + majority-vote reattachment; community member signatures; determinism discipline; node-link JSON serialisation; trigram+IDF lexical prefilter |
| **AI File Sorter** | Product loop shape: preview → approve → undo. Categorisation cache. *(Clean-room only — AGPL-3.0.)* |
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

**Phase 0 — fitness function.** Labelled sample of real files, ARI + pairwise co-location
scorer, reproducible harness. Nothing else starts until this runs.

**Phase 1 — deterministic spine, no embeddings at all.** Scan, cache chain, Tier-1 free signals,
EXTRACTED edges only (duplicates, versions, folder containment, sessions, EXIF), graph
persistence, `explain` for any edge. Score it. This alone collapses the 488 duplicates and groups
the 270 photos — a visible win with zero model calls, and it establishes the baseline every later
tier must beat.

**Phase 2 — embeddings and clustering.** Tier-2 embeddings, mutual-kNN, Leiden with hub
exclusion, recursive splitting for nesting, batched cluster labeling, frozen taxonomy. Score
against Phase 1.

**Phase 3 — placement and safety.** Escalation rule, plan/review/apply/undo, per-folder policy,
protected zones.

**Phase 4 — daemon and incremental ingest.** Resident process, persisted index, new-file
attachment at ~10–20 ms.

**Phase 5 — web UI.** Preview, streaming results, the graph view, AMBIGUOUS confirm/reject,
ETA before analysis begins.

**Later — learning loop.** Corrections are recorded from Phase 3 onward; acting on them comes
after placement quality is proven.

---

## Open questions

1. **Project name.** `filegraph` is a placeholder.
2. **Concept-node extraction depth.** Cheap signals only is locked; whether document *titles* and
   *authors* count as cheap depends on extraction cost per format — measure in Phase 1.
3. **Static embeddings.** A Model2Vec-class multilingual static model could remove the embedding
   cost entirely (claimed 100–500× faster). Benchmark was still running when this was written;
   if quality holds on short filenames it changes Tier 2's implementation, not its design.
4. **Cloud/local/hybrid mode selection and the ETA estimator.** Required by the product brief,
   not yet designed. Needs a per-device calibration run.

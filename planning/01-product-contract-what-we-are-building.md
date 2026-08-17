# Product contract — what we are building (v2.1)

Date: 2026-08-17  
Status: **canonical** — short contract for Alana and Joseph  
Remote: [josephyung6686/AIFILESORTERULTIMATE](https://github.com/josephyung6686/AIFILESORTERULTIMATE)

This file is the product contract. The long engine design is
[`02-filegraph-engine-how-extractors-templates-and-scoring-work.md`](02-filegraph-engine-how-extractors-templates-and-scoring-work.md);
the scripts behind its numbers are in
[`filegraph-corpus-measurements/`](filegraph-corpus-measurements/).
Those subsystems are in scope. Do not treat the engine design as “research we declined.”

Freeze still matters: after you approve the tree, nothing new appears anywhere you did not put
it. The canvas is **boilerplate for that freeze**, not an aesthetics project. Function first.

---

## Product

A **personal file intelligence system**. The core is a **knowledge graph of files** — people,
courses, events, “same session,” duplicates, versions — built from facts read out of the files.
The folder tree on disk is a **projection** of that graph. You can re-render a different tree
without new model calls.

It is not a lab-only regex sorter, and it is not an LLM inventing `Images/Science`.

**What the user sees:** pick sources and destination roots, optional profile card, a functional
canvas of existing folders plus template-fitted proposals, freeze, then files land only on
frozen nodes. Unmatched stay put.

**What the system is:** graph first. Disk layout second.

---

## Locked decisions

| Decision | Choice |
|---|---|
| Core | Knowledge graph of files (people, courses, events, same-session, duplicates). Disk is a projection |
| Graph storage | Persistent cache, rebuildable from the filesystem. Filesystem stays the system of record |
| Interface | **CLI engine first**, thin local web UI over the same library. Canvas is functional freeze/edit, not visual polish |
| Split of labour | Graph decides ~90%. Model names, merges, and judges the rest — never invents structure |
| Phase order | **Fitness scorer first**, then content extraction, then classify/cluster, then apply/undo, then a thin UI |
| Destinations | Frozen tree. Never invent `Downloads/Work/Misc` silently |
| Destination roots | A file may land in any **chosen destination root** (Downloads → Desktop is required) |
| Default roots | **None.** Warn if a chosen root is iCloud/OneDrive synced or TCC-empty |
| New folders | You add them on the canvas, or accept a **proposal** (templates + leftovers). Then freeze |
| Profile card | Optional role card before the canvas. Skip allowed. May rank existing nodes. May not invent a path or skip freeze |
| Filename baseline | `Counter` of tokens from files already in a folder (contents, not the folder name) |
| Placement scorer | **Mean + max similarity** to every file already in the folder (DEVONthink-style), over **fact edges** |
| Name collision | Never overwrite, **never silently rename**. Identical bytes → skip. Same name, different bytes → `ask`; file stays. Measured: 27 cases in 2,281 files (1.18%), and they are version conflicts where `(1)` destroys which copy is current |
| Delete | Never. Duplicates go to quarantine with a manifest |
| What may move | Loose files only. Directories are never moved as units |
| Sensitive content | ID / medical / tax / legal / keys **never leave the machine**. Detection failure fails closed |
| Cloud model | Allowed only for non-sensitive files, per run, explicit. **Show the exact text spans before sending** |
| Lab rules | Later profile, not the first vertical |
| Templates | **First-class.** Hand-written school / work / photos schemas. Model fills values, does not invent dimensions |

---

## Build order

Accuracy first. The canvas is not the first artefact.

0. **Fitness scorer.** Hand-label a small real folder. ARI + pairwise co-location + acceptance
   rate. Nothing else starts until this runs. Later stages must beat this baseline or they do
   not ship.
1. **Content extraction and the fact graph.** No embeddings required yet. Read whole files
   (PDF/DOCX text, EXIF, OCR, screenshots, HEIC). EXTRACTED edges only. `explain` for any edge.
2. **Classify into existing folders**, then cluster only the remainder. Mean+max scorer over
   the fact graph. Two-condition abstention. Embeddings enter only as `AMBIGUOUS` fallback.
3. **Placement and safety.** Plan / review / apply / undo. Collision rename. Protected zones.
4. **Incremental ingest.** New file → kNN against frozen labels. Resident **daemon** only if
   a measurement says one-shot CLI is too slow.
5. **Thin UI.** Functional canvas: freeze, split-by, accept/reject proposals. Boilerplate, not
   aesthetics.

A filename `Counter` classifier is the **cheap baseline** the fitness scorer can beat, and
the hold-out sentence for the UI. It is not the final placement engine. Keep any prototype
of it local until the plan is locked.

---

## Architecture

```text
scan
  → cache (stat → hash → per-tier results)
  → filesystem facts (name, size, hash, duplicates)
  → content extraction (whole file: PDF/DOCX, EXIF, OCR, HEIC, screenshots)
  → fact graph (people, courses, events, same-session, versions)
  → sensitivity classify (forced local vs eligible for cloud)
  → fit hand-written templates to THIS corpus
  → instantiate dimension values from the files
  → model may merge/name/order (never invent a dimension)
  → canvas (functional): existing folders + proposals; per-node split-by; freeze
  → classify onto frozen nodes (mean+max over folder members; filename Counter as baseline)
  → leftovers: cluster (Leiden, mutual-kNN, hub exclusion) → more proposals, not silent mkdir
  → plan → confirm → apply with undo
  → graph persists; a new file is a kNN attach, not a full re-classify
```

The graph is the data. The canvas is a view (`GROUP BY` in citation order). Freeze writes a
constraint back. Reordering dimensions re-renders; it does not rebuild the graph.

---

## Knowledge graph (core)

Nodes are files and concepts. Edges are **provable** first:

- same content hash (duplicate)
- version chain
- same EXIF event (photos: timestamp + location — never group photos by filename)
- same extracted course code, author, organisation, client
- same download session (“same session”) — purpose, not topic
- parent/child of existing folders

Inferred similarity (embeddings) is `AMBIGUOUS`, low confidence, and **cannot form an edge by
itself**. It exists to link files whose extraction produced nothing, and to break ties.

Hubs are a known failure. Identity tokens (`joseph`, student IDs, `columbia.edu`) must not
become folders or dominate a cluster. **Hub exclusion** on Leiden. Type tokens (`screenshot`,
`resume`) may be categories even when common.

GLiNER is scoped to `school`, `person`, `client` — not a general entity dump.

A resident daemon is an optimisation for incremental ingest, not a requirement on day one.

Detail, edge list, and measurements: FileGraph spec, “The graph model” and “Pipeline.”

---

## Reading file insides (required, not later)

Filenames are a sweep. The product reads **whole files**.

| Work | Why it is in |
|---|---|
| Full PDF text (all pages, not page 1) | Page 1 misses most of this corpus |
| Full DOCX body + tables | Headings and tables carry the facts |
| EXIF | Photos group by event, not `IMG_4821` |
| Screenshot vs photo | Camera EXIF vs screen-sized PNG; abstain when signals disagree |
| OCR (Apple Vision, not Tesseract) | Scans and screenshots; 11% of PDFs have no text layer |
| Bad text layer | A PDF can have a text layer that is garbage; empty-or-junk → OCR |
| HEIC | Register HEIF or ~4% of a photo corpus is invisible |
| Archive manifests | What is inside the zip, without treating the zip as a mystery blob |

Embeddings run over **extracted content**, not the filename. Filename-only clustering produced
a 73-file junk hub. That is why extraction is Phase 1 of the engine, not a nicety.

---

## Templates (first-class — do not drop)

Existing organised folders absorb little of a messy Downloads (~4% measured). **Most of the
canvas is proposals.** Those proposals come from **hand-written templates**, not from a model
inventing a taxonomy.

Templates are data files (school / work / photos / applications / career / finance / …). Each
declares:

- **citation order** (Wall-Picture: big picture first, except photos which put time first)
- which dimensions are **constant** (asked once: school, applicant) vs **per-file** (extracted)
- **detection signals** (course-code pattern, EXIF camera, `syllabus|lecture|hw`, …)

**Fit** scores which templates this corpus actually needs. Templates that match nothing are
never shown.

**Instantiate** fills slots with values from the files (`subject ∈ {PHYS1401, BUSIB 4300, …}`).

**Per node, you pick the split:** subject vs term vs work-type vs don’t split — with live
branch counts *before* you commit. Branches may be uneven (`Columbia/PHYS1401/Lectures/` next
to a flat `Columbia/ENGIE1006/`). Wall-Picture orders the options; you override per node.

**Aho-Corasick gazetteers** (plus a hand-added boundary check) match course codes, orgs, and
cues in extracted text. Four validation layers exist in the FileGraph spec; keep them. Dates
are never fuzzy-parsed.

**The model may** merge near-duplicate proposals, name branches in your vocabulary (prefer an
existing folder name), order dimensions where the citation rule leaves a choice, drop proposals
too small to earn a folder.

**The model may not** create a dimension, invent a template, or place a file.

Identity & finance templates detect for the **sensitivity path first**, not for filing.

Canonical value vs display label: renaming `BUSIB4300` to `Managerial Economics` must not break
matching. Two fields; neither overwrites the other.

---

## Folder creation — you add a node, the graph proposes what goes under it

The canvas lets you add a folder by hand. The question this answers is what happens *underneath*
it, because "the user typed a name" is where an organizer is most tempted to invent.

**1 — BIND (provable, no model).** Resolve the typed name against the fact graph: exact match on
`label` / `display_label` → alias table (`Columbia` → `Columbia University` → `columbia.edu`) →
dimension-value match → fuzzy, shown as *"did you mean"*, never silent. The node's file set is a
`SELECT` — exact, not estimated.

**Bind only to dimension values, never to raw tokens.** This is where the identity rule becomes
structural rather than statistical: `joseph`, `hjy2114` and `columbia.edu` are values of no
declared dimension, so they cannot bind, so they cannot become a 400-file folder. We measured that
frequency cannot separate identity from type — it correctly flagged `joseph` but also killed
`screenshot` and `resume`. The schema does what a stoplist could not.

**2 — FIT, scoped to this node.** Run template detection over *this node's members only*.
`Columbia` binds 201 files → Academic coursework fits, supplying the default next split (citation
order says `term`), the candidate dimensions, and the validators. Two templates fitting is a real
choice to offer, not ambiguity to resolve silently.

**3 — OFFER.** Every option is a `GROUP BY` with exact counts:

```
Columbia/  (201 files)   split by?
    ○ term        3 branches   2026-Spring (89) · 2024-Fall (72) · 2021-Spring (40)
    ○ subject     5 branches   PHYS1401 (12) · BUSIB 4300 (8) · ENGIE1006 (6) …
    ○ work-type   4 branches   Lecture (58) · Homework (44) · Exam (31) · Syllabus (12)
    ○ don't split

Columbia/PHYS1401/  (12 files)   split by?
    ○ work-type   4 branches   Lecture (5) · Homework (4) · Practice (2) · Notes (1)
    ○ term        1 branch     ⚠ wasted level
    ○ don't split
```

Branches may differ in depth — `Columbia/PHYS1401/Lectures/` beside a flat `Columbia/ENGIE1006/`
holding four files. Real file plans are uneven by design; one global citation order cannot say
that. Validators surface here as inline warnings, not hidden rules.

**4 — THE MODEL, bounded.** Same permissions as everywhere else — rank which split to default to,
name branches in your vocabulary, merge near-duplicates, drop branches too small to earn a folder.
It may not create a dimension, invent a value, place a file, or **propose a branch with no files
behind it**: every proposed subfolder needs **≥ 3 files that provably carry that value**. That is
the freeze rule applied one level down.

**5 — THE EMPTY INTENT NODE.** You type `Clients` and nothing binds. That is legitimate — you are
declaring intent ahead of evidence. Two legal outcomes:

- **Targeted extraction** — the template declaring `client` says what evidence would fill it (org
  names in extracted text). Run that extractor over unplaced files; if values appear, return to 3.
- **Stay empty and frozen** — a legal destination with no children, which you drag onto.

Never fabricate `Clients/Active` and `Clients/Archive` because they sound like what a person would
want. **An empty node is a correct answer. A node with invented children is the failure this whole
contract exists to prevent.**

**Overlap.** A file carrying `school=Columbia` and `work-type=homework` matches two hand-added
top-level nodes. Each branch's parent chain is its own citation order; the file goes where its
facet path matches deepest, and equal depth → `ask`. The abstention rule applied to the tree, so
it needs no new machinery.

---

## Classifier

Two layers. Both only land on **frozen** nodes.

### Filename baseline (shipped)

A node’s profile is a `Counter` of tokens from files already in it, **not** the folder name.
`Work` is empty of meaning; the files inside it are the model.

Hold-out on already-filed files is the right regression metric — free labels, runs today, catches
a change that makes things worse. **But it must not be quoted over loose files.**

> ~~I'd place 6 in 10 of your loose files, and on your own filed data I get 97% of those right.~~

**Those are two different populations, and the numbers do not transfer.** Already-filed files are,
by selection, files that *fit a folder*. Loose files are the ones that did not — measured, existing
folders absorb only **4%** of them. Hold-out precision is therefore an optimistic bound, not an
estimate of what the user will see.

This exact mistake is already documented in the FileGraph spec: semantic propagation passed a
hold-out test at **92%** and delivered **~50%** in practice, and was cut for that reason. The
populations differed the same way.

**So report two numbers and never merge them:** hold-out precision on filed data (regression), and
placement precision on a hand-labelled sample of *loose* files (the honest one). If only one can
be shown in the UI, show the loose-file number.

Unknown class tokens (`cs3157` vs a `CS3134` folder) abstain and, if they recur, become a
canvas proposal — not a silent folder.

Prototype code stays off this remote until the plan is locked.

### Placement scorer (the real engine)

```
score(folder) = f( mean similarity to ALL members of the folder,
                   max  similarity to the single best member )
```

Similarity is **fact-edge weight**, plus embedding fallback only when facts are missing. Mean
lets a large coherent folder win; max lets a small folder holding one near-duplicate win. No
trained model to go stale; refiling updates scores immediately.

**Abstain on two conditions**, not one:

- top score too weak (quantile of *this* machine’s distribution, not a global constant)
- top two folders too close

Silence (stay put + review list) beats a confident wrong folder. When two folders fit equally,
show both — do not pick.

Escalation (run OCR / vision / LLM, then re-score) is **not** abstention. Different questions.

---

## Clustering leftovers

Only for files that abstained. Mutual-kNN, Leiden with **hub exclusion**, recursive split for
nesting, batched labels for *proposed* folders, frozen once accepted. If this path does not
beat “classify into existing + review queue” on the fitness scorer, it stays **off by default**.

**The same gate covers embeddings and GLiNER, and it is a build gate, not just a runtime
default.** They are in the design; they ship only if a harness run says they beat the fact graph.
The evidence for gating rather than assuming: embeddings allowed to form edges produced a
measured **73-file grab-bag**, and semantic propagation measured **+3% coverage at ~50%
precision** and was cut. The fitness scorer is build-order 0, so the gate costs nothing to
enforce — it is one run before the work starts.

---

## Cloud, sensitivity, and “never leaves the machine”

These are one policy, not two slogans.

**Forced local, no override:** government ID, medical, financial, tax, legal/contractual,
credentials. Detect on **already-extracted local text**. If detection is unsure, treat as
sensitive.

**Cloud is allowed** for everything else, and only then:

- per run, explicit, never a silent default
- **show the exact file list and the exact text spans** that would be sent — not a summary —
  before anything leaves
- evidence packets are facts and short spans, never whole documents, never a sensitive
  neighbour “because it’s in the same group”
- log every egress: which files, which spans, which provider, when

iCloud/OneDrive: filing into Desktop/Documents often **uploads**. The picker warns. We do not
default those roots. TCC-empty Desktop is “grant access,” not “0 files found.” Dataless
`.icloud` placeholders are not files.

---

## Apply, collisions, safety

- Analysis never moves files. It produces a plan.
- Dry-run default. Confirm to apply. Journal **before** each move. Undo the run.
- **No overwrite, and no silent rename.** Identical bytes at the destination → skip, already
  filed. **Same name, different bytes → `ask`; the file stays put.**

  **Measured on the real corpus, which settles this.** Of 2,281 loose files, 62 share a name with
  something already filed — 35 identical (skip) and **27 different (1.18%)**. A review screen of
  27 items once per run is not a stall. And the cases are exactly the ones auto-rename ruins:

  ```
  problem4.py              loose ~/Downloads  vs  filed ~/Desktop/Python 1006
  project1_analysis.ipynb  loose ~/Downloads  vs  filed ~/Desktop/Project 1 python/GroupProject1
  ```

  These are version conflicts. `problem4 (1).py` preserves both files and destroys the only fact
  the user needs — **which one is current**. Producing mystery duplicates is the problem this
  product exists to fix.

  The plan’s `dst` remains a proposal; apply computes and journals the final path.
- Destination must resolve inside a **chosen destination root** after symlink resolution
  (cross-root is allowed; escaping the chosen roots is not).
- Project-skip on **destinations** (`node_modules`, `.git`, `venv`, `package.json` ancestors, …).
- Files only. Symlinks skipped. Empty dirs pruned only if journalled.
- Interrupted run stays undoable.

---

## Profile (thin)

Role: student / business / engineer / researcher / mixed. Optional tags. Skip allowed.

Effect: bias which existing folders and which **templates** are promoted. Still freeze.

Not: tagging every file; age; inventing paths.

---

## Error handling

- Fitness scorer red → do not ship that stage.
- Extraction failure on one file → mark it, continue, do not abort the corpus.
- Bad or empty text layer → OCR path, then re-score.
- HEIC without HEIF support → visible error (“photos you cannot see”), not silent skip of the
  corpus.
- Sensitive + cloud requested → refuse that file, continue the rest locally.
- User dismisses the “exact text” preview → nothing is sent.
- Frozen node deleted before apply → that file becomes ask, not silent create.
- Permission / in use / disk full → stop apply, keep journal, undo what moved.
- Offline works. Cloud is optional.

---

## Testing

Keep the filename-engine tests locally until the plan is locked and code is allowed on
GitHub (content profiles, hold-out 100% / 62%, `cs3157` abstain, project-skip, TCC/iCloud
flags).

Add, as each build phase lands:

- Fitness scorer runs on a hand-labelled fixture before placement code.
- Full PDF vs page-1: facts exist past page 1.
- EXIF event groups photos; two `IMG_*` without shared event do not.
- HEIC opens.
- Empty/junk PDF text layer routes to OCR.
- Mean+max places a file with a shared course code into the folder whose members share that
  code, even when filenames are opaque.
- Two-condition abstention: close top-two → stay put.
- Template fit hides templates with 0 hits; instantiate uses corpus values, not placeholders.
- Per-node split preview counts match the files.
- Gazetteer does not match `cs` inside `discs`.
- Collision: existing `a.pdf` + incoming `a.pdf` (different bytes) → `a (1).pdf`, original
  untouched.
- Sensitive fixture never appears in a cloud payload.
- Cloud preview lists the exact spans; cancel sends nothing.
- Leiden hub exclusion: identity token does not swallow the cluster.

---

## Out of scope

- Lab Nutrigene schema as the first vertical (later profile).
- Copying [hyperfield/ai-file-sorter](https://github.com/hyperfield/ai-file-sorter) source (AGPL).
- FUSE / virtual filesystem. Emit real folders Finder already understands.
- Reorganising a folder the user already curated (only loose files move).
- Canvas visual polish ahead of the scorer and extractors.
- Feeding a model’s own labels back as ground truth without a negative signal.
- GPL stacks if a non-GPL equivalent exists (`leidenalg` / PyMuPDF — prefer Apple Vision and a
  non-GPL community detection path, or isolate).

---

## Deferred only in time, not in product

These are in the contract. They are sequenced, not dropped.

1. Fitness scorer on a real labelled folder.
2. Whole-file extraction + fact graph + sensitivity classifier.
3. Mean+max placement + two-condition abstention + hold-out gates.
4. Hand-written templates, Wall-Picture split-by, gazetteers.
5. Leftover clustering (Leiden / mutual-kNN / hub exclusion) behind the scorer.
6. Cloud path with exact-text consent.
7. Apply / `file (1).ext` / undo / daemon-if-measured.
8. Thin canvas UI (freeze, proposals, split-by).
9. Lab profile; act on the decision log; “what I need next.”

---

## North star

What a file is, what work it belongs to, how *this* user handles similar material, what is
useful now. The graph is the memory. Templates plus freeze keep it from inventing junk. The
model personalises names. Sensitive text never leaves unless you saw it and said so.

---

## Repository layout

This GitHub remote is **planning specs only** until the plan is locked with Joseph. Do not
push application code here in the meantime.

```text
planning/README.md                                              start here — what each file is
planning/01-product-contract-what-we-are-building.md            THIS FILE — product contract
planning/02-filegraph-engine-how-extractors-templates-and-scoring-work.md
                                                                long engine design + measurements
planning/filegraph-corpus-measurements/                         scripts that produced those numbers
README.md                                                       repo home; points at planning/
```

A filename `Counter` baseline may exist locally. It is not part of this remote.

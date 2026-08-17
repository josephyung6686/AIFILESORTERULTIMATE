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
| Extraction depth | Per-format tiers. **A** text-bearing (64%) full text → facts · **B** media (31%) metadata + OCR, never decipher the payload · **C** containers, the manifest · **D** opaque, name + session |
| Extraction scope | **Every Tier-A format**, not just PDF/DOCX. OOXML is a ZIP of XML — no library needed |
| Fact extraction | Rules find **candidates**, never decide. Naive regex turned "Ernst & Young Global" into "Young Global". Gazetteers + validation layers + a judge |
| What the model reads | A **~1,000-word head** of each file (≈1.5 M tokens/corpus, 8× less than full text), escalating to full text only on abstention or conflict |
| Images | **Classify locally first** (`VNClassifyImageRequest`, 110 ms, free) → content-kind facet + faces, then OCR. OCR everything that is not a confirmed camera photo; text → content path, no text → photo, group by event. 46% of images cannot be typed by metadata at all |
| Pixels / vision | Opt-in per run, never default. Same sensitivity gate as text |
| Egress order | Extract locally → classify sensitivity locally → **then** send heads of non-sensitive files. Not negotiable |
| Activity axis | Purpose groups (sessions + constellations) surfaced **before** the tree, named by the model, confirmed by you. 36% of sessions span 2+ file families |

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
  → content extraction, tiered by format
        A text-bearing (64%) full text · B media (31%) metadata + OCR
        C containers, manifest       · D opaque, name + session
  → fact graph (people, courses, events, same-session, versions)
  → sensitivity classify (forced local vs eligible for cloud)   ← BEFORE any egress
  → model reads a ~1,000-word head per file; escalates on conflict
  → surface ACTIVITY groups (sessions + constellations) → you confirm
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

Filenames are a sweep. The product reads **whole files** — and "whole" means every format that
can yield text, not the two that are easiest.

**Measured, whole corpus, all formats: 86.5 s for 2,281 files, recovering 46.4 M characters from
1,371 files.** An earlier run that handled only PDF and DOCX reported 68 s and 36.5 M — it had
silently skipped 19% of the corpus, including every `.xlsx`.

### Extraction tiers — depth follows what the format can actually yield

| Tier | Count | Formats | What we take |
|---|---|---|---|
| **A — text-bearing** | **1,468 (64%)** | `pdf docx xlsx pptx txt md csv ipynb html json py js` | Full text, then facts |
| **B — media** | **705 (31%)** | `png jpg jpeg heic webp tif mov mp4 wav mp3 m4a` | EXIF / container metadata, OCR where there is text. **Never decipher the payload** |
| **C — containers** | 57 | `zip` and friends | The manifest. It is text, and it is often the most informative thing about the file |
| **D — opaque** | 108 (5%) | `stl gcode dmg indd` | Filename, mtime, session. `gcode` header comments and the `stl` ASCII header are cheap and sometimes carry a model name |

**OOXML needs no library.** `docx` / `xlsx` / `pptx` are ZIPs of XML — unzip, strip tags. That is
how `Personal Data Form_Intern_HK_2026.xlsx` goes from invisible to 1,649 characters of
extracted text.

Other required specifics, all measured: full PDF text (page 1 misses most of this corpus, median
3 pages against a mean of 16); full DOCX body **and tables**; a PDF text layer can be present and
garbage, so empty-or-junk routes to OCR; HEIC needs `register_heif_opener()` or ~4% of a photo
corpus is silently invisible.

### Rules find candidates. Rules do not decide.

This is the layer that was under-built, and it is worth stating exactly how it failed. Naive
regex over the EY offer letter produced:

```
company      Young Global, Young Transactions     ← "Ernst & Young Global Limited"
course_code  VHX7000                              ← not a course code
course_code  USD2026                              ← this is "USD 2026"
```

The spaces around ` & ` broke the token run, so **the single most important fact in that session —
the employer — came out wrong**, from a file whose own name says `EYHK`. Corpus-wide that layer
emitted 730 "course codes", a real fraction of them junk of the `USD2026` kind.

The failure is not that a regex produced a wrong candidate. It is that **nothing checked it.**
Rules are correct on what is genuinely regular — dates, money, emails, hashes, EXIF, version
chains — and those extracted cleanly in the same run. Everything else is a *candidate* that a
judge must confirm, with gazetteers and the four validation layers in the engine spec.

### The model reads document heads, not documents

Training a model for this is not merely hard, it is the wrong shape: there are no labels, and the
vocabulary is one person's. `PHYS1401`, `VHX7000` and `EYHK` mean something in this corpus and
nothing in anyone else's. That argues for a general model reading a small slice, not a trained
one.

**Identity lives in the head, by document design.** Letterheads, titles, form captions,
salutations. Measured on the internship session, the first 600 characters carried the employer,
the date, the document kind and the event — 7% of the offer letter, 21% of the collection
statement, 36% of the data form.

| What we send | Chars | Tokens |
|---|---|---|
| Full text of every file | 46.4 M | **~11.6 M** |
| 1,000-word head | 6.0 M | **~1.5 M** |
| 600-char head | 0.77 M | **~193 K** |

**61% of documents are shorter than 1,000 words**, so at that size the "head" is simply the whole
document for most of the corpus.

**Locked:** a ~1,000-word head as the default judged slice, escalating to full text only on
abstention or conflict. ~1.5 M tokens is a one-time cost for a whole corpus, cached thereafter,
and it is still **8× less than sending everything**. The fitness scorer settles whether the
shorter 600-char head buys the same accuracy for an eighth of that; if it does, it wins.

This corrects an over-broad earlier claim that "the model never sees individual files." It sees a
**bounded slice of every file**, plus full evidence packets per group. Two granularities, one
budget.

### Images: do not classify them, just try to read them

Measured on 657 images, the signal stack does **not** hold up on its own:

| | Count |
|---|---|
| Camera EXIF present → real photo | **43 (6.5%)** |
| Screenshot by name or exact screen size | 227 |
| PNG without EXIF → likely capture | 82 |
| **Ambiguous — no EXIF, not screen-sized** | **305 (46%)** |

Messaging apps strip metadata, so nearly half of images cannot be typed by metadata at all. An
earlier draft resolved this by abstaining, which abandons 46% of the image corpus.

**Better: stop trying to decide what the image is from metadata, and ask the machine to look at
it — locally.**

#### macOS classifies images for free, on-device

`VNClassifyImageRequest` returns labels from a built-in taxonomy with confidence scores, and
`VNDetectFaceRectanglesRequest` returns face counts. Both are local, free, and need no network.
**Measured on the ambiguous set: 110 ms/image — about 72 s for all 657 images.**

```
IMG_7009.JPG                    people 0.88 · adult 0.78 · crowd 0.77
IMG_8436.HEIC                   document 0.93 · screenshot 0.93
IMG_8461.HEIC                   consumer_electronics 0.80 · machine 0.80 · computer 0.80
WhatsApp Image …23.08.13.jpeg   container 0.70 · carton 0.70 · cardboard_box 0.15
download.jpeg                   people 0.75 · adult 0.75 · clothing 0.70   1 face
```

Across a 45-image sample the top labels were **document 36%** and **people 20%** — so the
"ambiguous" pile is mostly photographed paper and photographs of people, and both have obvious
handling.

**What this is, precisely: a coarse `content-kind` facet, not meaning.** "document" does not say
*lecture handout*; "people" does not say *graduation*. The label routes the file and contributes
one fact. Naming still comes from filename, session and the model.

**Be honest about the miss rate.** Roughly half the sample scored ≥0.5; the rest came back as
`material 0.19` or `document 0.18`, which is the model saying it does not know.
**Facts require ≥0.5; below that there is no label**, and the file falls back to filename plus
session — which is frequently the better signal anyway
(`Georgetown Prep Red Cross Club.png` needs no classifier).

#### The image path, in order

1. **Vision classify** (110 ms, local, free) → `content-kind` facet + face count.
2. **OCR** anything labelled document / screenshot / chart / sign, and anything unlabelled.
   Text back → **that text is the content** and it enters the ordinary head path.
3. **No text and no confident label** → it is a photograph. Group by EXIF event and session; the
   model receives metadata and filename, never pixels.
4. **Cloud vision** — the only thing that yields real semantics — is **opt-in per run**, priced
   and explained, under the same sensitivity gate as text.

Vision runs **before** the OCR/event decision, because it is what routes it: `IMG_8436.HEIC`
scores `document 0.93` and would otherwise have been filed as a holiday snap.

**Faces are a privacy signal, not just a grouping one.** 9 of 45 sampled images contain faces.
Images of people are treated as sensitive-by-default for egress.

The screenshot-versus-photo question still matters for *grouping* (event versus content), but it
no longer gates *extraction*. Nothing is abandoned for being ambiguous.

### What non-text files send

| Type | Sent to the model |
|---|---|
| `zip` | The manifest. `figma-implement-design.zip` says more than most documents |
| `mp4 mov` | Duration, creation date, resolution, camera. Frame extraction is opt-in, never default |
| `wav mp3` | Duration, ID3 tags, filename, session. The measured game-audio session — `jump.wav`, `hardpunch.wav`, `Voicy_Game Over.wav`, eleven files in 14 minutes — is nameable from exactly this |
| `stl gcode indd dmg` | Filename, mtime, session, and any cheap header text |

### Order of operations, which is not negotiable

**Extract locally → classify sensitivity locally → only then send heads of non-sensitive files.**

The same test that proved the head strategy also surfaced `Mar.pdf`: a BOCHK consolidated
statement carrying account numbers, balances and fund holdings, which the naive extractor had
labelled `course_code: USD2026`. Head-reading and never-leaves-the-machine compose correctly, but
only in that order.

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

## The activity axis — what a file was FOR, not what it IS

Templates answer *what is this document*. They cannot answer *what was this for*, and the second
question is usually the one a person is actually asking.

**Measured: 36% of download sessions span two or more file families** — and those are exactly the
cases where every content-based method has nothing to work with.

```
[2026-04-24]  11 files / 14 min   jump.wav · jumplanding.wav · hardpunch.wav
                                  normalpunch.wav · Voicy_Game Over.wav + png
[2026-03-19]   9 files / 25 min   EY offer letter · Personal Data Form.xlsx
                                  Fit and Proper Questionnaire · PIC Statement
[2026-04-15]  11 files / 70 min   strategy_round1.py · _v2.py · _v3.py + 4 zips
```

The first is decisive. A `.wav` yields no text, so extraction produces nothing, embeddings have
no input, and every content template is blind. The only things binding those eleven files are
**downloaded together in 14 minutes** and **a human recognising what they are for**.

The second is the same point in a different key. The Career template sees a resume and files it
under `Career/`. What a person looks for is *the EY internship paperwork from March* — an event,
not a document type.

**So the model's job here is recognition from a constellation**: given a session's filenames,
types, timespan and extracted facts, name the activity — "game sound assets", "internship
onboarding", "strategy competition round 1". This needs world knowledge, which is what a model
has and rules do not. It remains naming and judging, never inventing.

**Surfaced before the tree is built:**

```
Found 39 groups of files made or collected together. Which deserve a folder?
  ☐ Game sound assets            11 files   24 Apr 2026, 14 min
  ☐ EY internship onboarding      9 files   19 Mar 2026, 25 min
  ☐ Strategy competition round 1 11 files   15 Apr 2026, 70 min
```

You tick; the model names; content templates then structure *inside* what you picked. That
yields `EY Internship – Mar 2026/` rather than `Career/forms/`.

**Two constraints, both measured.**

*Sessions have a false-positive mode.* One group is a resume plus nine WhatsApp images in six
minutes — almost certainly two unrelated things that co-occurred. Activity groups are therefore
**proposals you confirm**, never auto-created. Same freeze rule as everywhere else.

*Eras do not come from the filesystem.* The year histogram runs 2023→2026 with smooth growth and
no boundaries, because mtime is *download* time: a high-school essay downloaded last week reads
as 2026. Grouping by life period requires dates extracted from document **content**, which the
Tier-A pass already recovers.

**How the two axes compose.** Activity is a coarse partition of *purpose*; templates are a fine
partition of *content* within it. A file can carry both, and where two branches match at equal
depth the answer is `ask` — the abstention rule, applied to the tree.

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

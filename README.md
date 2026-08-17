# FileGraph

A file organizer that reads your files, proposes a folder structure you approve, and then files
only what it is confident about — leaving everything else exactly where it is.

**Status: design complete, not implemented.** Every significant claim in the spec is backed by a
measurement against a real 2,281-file corpus on the target machine. The scripts that produced
those numbers are in `research/`.

---

## The problem with existing tools

Every AI file organizer asks a model the same question once per file. On a 300-file folder with a
local model that took **over an hour and did not finish**.

Reading the incumbent's source explains why: it creates and destroys a full inference context per
file, and both of its content-reading paths — document text and image vision — **ship disabled by
default**, because enabling them doubles the model calls. It categorises `IMG_7009.JPG` from the
filename while the EXIF sitting in the file goes unused.

## What this does instead

```
1. SWEEP        filename detectors over every file              seconds
2. EXTRACT      full document text, EXIF, archive manifests      ~55 s / 2,000 files
   + OCR        scanned PDFs, screenshots, opaque images         ~6 min
3. FIT          which hand-written templates does this corpus need?
4. INSTANTIATE  fill their dimensions with values from the corpus
5. PERSONALISE  a model merges, names and orders the proposals
6. CANVAS       you edit the tree and FREEZE it
7. CLASSIFY     files may only land on a frozen node — unmatched stays put
8. APPLY        plan → dry run → confirm → move, with undo
```

**Freezing is the core idea.** It converts an open-ended generation problem ("what categories
should exist?") into a closed-set assignment problem ("which of these does this file belong
to?"). The second is verifiable, bounded, and explainable. The first is what every competitor
gets wrong.

## What the measurements found

| Finding | Number |
|---|---|
| Full content extraction, whole corpus | **55 s** (2× the cost of a first-page peek, 8× the text) |
| OCR everything unreadable (89 scans + 200 screenshots) | **~6 min**, offline, free |
| Apple Vision vs Tesseract | **3.9× faster, 99.7% recall, 53× lighter** |
| Structural relationships (duplicates, versions, events) | **68% of files, zero AI, ~5 s** |
| Exact duplicates | 137 sets, **128 MB reclaimable** |
| Version chains | 263 chains covering **51% of the corpus** |
| Disciplined extraction vs naive | fixed **8 of 8** errors with no ML |
| Semantic propagation | **+3% coverage at ~50% precision — cut** |
| Existing folders absorbing loose files | **4%** — the canvas is 96% proposals |

## The one constraint everything follows from

Confirmed by four independent experiments:

> **Provable relationships work. Inferred relationships produce hubs — and the hub is always the
> user's own identity.**

`columbia.edu`, `hjy2114`, `joseph`, `yung` each swallowed unrelated files in a different
mechanism. Duplicates, version chains, sessions and EXIF events never did.

So: the graph is built from what can be *proven*. A model judges what must be *judged*. Nothing
infers a topic from a neighbour.

## Design decisions worth knowing

- **Unmatched files stay put.** 32% high-precision placement is a good first run; the rest waits
  on a short worklist. This is what makes low recall acceptable rather than fatal.
- **The graph is over folders, not files.** Parent/child containment is provable; file similarity
  is not. A file graph produced hubs in every experiment.
- **Purpose is separate from topic.** A download session says nothing about what a file is
  *about* and everything about what it was *for*.
- **Never delete.** Duplicates move to quarantine with a manifest.
- **Never touch anything already inside a folder.** Only loose files move.
- **Templates are hand-written data files**, fitted to the corpus. The model may merge, name and
  order — never invent a dimension or create a folder.

## Repository

```
docs/superpowers/specs/2026-08-16-filegraph-design.md   the full design (~2,300 lines)
research/                                               the scripts behind every number
```

Prior art examined in depth: AI File Sorter (source), graphify (source), DEVONthink,
Paperless-ngx, Hazel, Google Drive "Organize My Files", the TMF Reference Model, published
government and university file plans, and faceted classification theory.

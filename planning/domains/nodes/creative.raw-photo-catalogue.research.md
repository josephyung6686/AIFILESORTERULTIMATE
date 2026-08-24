# `creative.raw-photo-catalogue` — lab notes

Row: template on `creative` · `launch: placeholder` · `refuse_node: false`, on a **narrowed scope**
Absorbs: `photo.raw-catalogue` (ROSTER.md Appendix A, ROW)
Depth: full R1b (J-DEPTH, ratified 2026-08-24). The `Depth: GIST` label is retired and was not used.

---

## 1. Sources actually used

- `planning/00-database-agent-product-design.md` — every quotation in the node and in this memo was
  matched back into this file mechanically before either was written (33 quoted spans checked; the
  only non-`00` quotations are two spans taken verbatim from landed sibling nodes and attributed to
  them by name, see §7).
- `planning/domains/CONNECTION.md` §1–§3 — the four graphs, the node test, and the binding statement
  that the browse tree is not load-bearing. CONNECTION wins over the dispatch prompt where they
  differ; they did not differ on anything this row needed.
- `planning/domains/ROSTER.md` §1b, §4 table row `creative`, Appendix A line for `photo.raw-catalogue`,
  and the NJ-R1a-1 / NJ-R1a-5 entries.
- `planning/domains/roster.json` — this row's own entry, the `creative` schema's `one_line_hint`,
  and the `one_line_hint` of all 40 sibling `creative.*` rows (read in full, because the boundary
  work here is almost entirely against siblings).
- `planning/domains/canonical_fields.json` — checked for a day-grained capture key. There is none;
  see §4.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`. Every `source_type` written is on that list.
- Landed neighbour nodes, read before writing: `photos.json`, `photos.camera-events.json`,
  `photos.family-archive.json`, `photos.scanned-documents.json`, and
  `construction_property.progress-photos.json` + its memo.
- Calibration rows, read for depth and idiom: `finance.crypto-assets.research.md`,
  `medical.wearable-health-exports.research.md`. `clinical_practice*` and `business_operations*`
  were used for JSON key set only, per the brief.

---

## 2. The refusal that nearly happened, and why the row survived narrowed

The dispatch brief was right to warn that this row might be "photos' own situation wearing a
creative label", and for the majority of the bytes it names, it is. `photos.camera-events` already
lists `.dng`, `.cr2`, `.cr3`, `.nef`, `.arw`, `.raf` in its own `file_kinds`, already joins "a RAW
and JPEG pair" into a single capture, and already owns the year-then-event recommendation `00`
wrote for photographic material. A row whose content was "photographers keep RAW files" would be
the 574's original mistake and this memo would be a refusal.

What stopped the refusal is an evidence-class fact, not an industry fact: **this row's defining
evidence items are not images and never reach the image extractor at all.** `00` routes them
somewhere else by name:

> Compressed archives should yield their manifests without extraction, while disk images,
> executables, databases, encrypted containers, damaged files, and unknown binary formats should
> default to safe metadata-only indexing unless a dedicated extractor has been explicitly approved.

A Lightroom catalogue is a database. A sidecar contains no pixels. A previews bundle is derived
application data. `photos.camera-events` cannot claim any of the three, because everything it runs
on is read out of a decoded image —

> The system should therefore use a hierarchy of signals: camera EXIF is strong photo evidence;
> capture time, GPS, and sensor-shaped dimensions reinforce it; exact display resolutions, PNG
> format, and software metadata may support a screenshot hypothesis; conflicting signals should
> lead to abstention rather than an invented classification.

— and none of those bands can be evaluated on a `.lrcat`. `00` also licenses reading the reference
layer of a creative file without opening its proprietary body, which is exactly the operation this
row depends on:

> Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should
> at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or
> artboards where accessible, linked asset names, and preview text; unsupported proprietary formats
> should be recorded as indexed-but-unreadable rather than silently treated as empty.

"linked asset names" is the sentence this row stands on.

So the scope was cut to what is genuinely unclaimed: **the index layer and the archive-as-a-whole
that layer implies.** The loose camera originals stay `photos.camera-events`'. That cession is
written into the node's `collides_with` entry in both directions, and the alternative reading — that
a professional's whole archive including its originals is one situation, which would make the two
rows rivals rather than co-holders — is logged as open question (2) rather than argued away.

### The node test, all three legs

**Leg 1 — detection signals.** Differ, and differ in class, as above. The catalogue database, the
basename-paired sidecar, the previews bundle and the catalogue backup are four signals no sibling on
either schema can evaluate. This is the leg the row is kept on.

**Leg 2 — recommended dimensions.** *Cannot be used here, and the node says so rather than
pretending.* The `creative` schema declares no field rows (PR-6; D1's deferral stands), so
`dimension_order` is `[]` by binding contract — a dimension naming an undeclared field opens a tree
level no fact could fill. The recommendation is held as prose in `template.why`: capture date first,
one slug level at most, then nothing. `time_first: true` is recorded, and it is the *only* creative
row where `00`'s exception legitimately applies:

> For document and record domains, project, function, or subject usually comes before time because
> putting year first scatters related work across calendar folders. Photos and capture-based media
> are the major exception: time often belongs first because capture date is a defining aspect of the
> material.

The reason it applies to this row and not to its creative siblings is the roster hint's own and it is
an argued inference, marked as such: a client exists for some frames of an archive and not others, a
project exists for some and not others, and a capture moment exists for every single frame. A
dimension that is absent on half the material cannot be its top level.

**Leg 3 — privacy and handling rules.** Differ, in a way no sibling shares, and this is the leg that
makes the row interesting rather than merely admissible. A catalogue is a database *of other files'
paths*. `00` already knows paths are unstable —

> A path can change when a file is renamed, moved, synchronized through cloud storage, restored from
> backup, copied to another volume, or reorganized by the user outside the product.

— and the product survives that because

> The stable identity for a file version should therefore be the content hash, with a separate
> internal file record that retains path history and observed filesystem state.

The user's Lightroom catalogue has no such protection. A move proposal on a catalogued original is
therefore not just a filing choice: it silently breaks a third-party index the product did not
write and cannot repair. That is a constraint on **action**, not on facts, and it belongs to this
row alone. `00` states no rule for a file another application indexes, so the node **recommends**
stability and logs the decision as open question (1) rather than enforcing it.

---

## 3. Files considered and rejected

The row is only honest if it names the tempting false positives. These were considered and are
**not** this row's evidence:

| File | Why it is not this row's |
|---|---|
| `IMG_4821.HEIC` (phone capture beside RAWs) | **The collision fixture.** Deliberately `photos.camera-events`' own fixture. It has camera EXIF, a GPS fix and a run around it, and none of the index layer. Proximity to raw files is a directory accident, and the node's `never_alone` forbids taking it. |
| Any file on a raw extension alone (`.nef`, `.cr3`, `.arw`, `.dng`) | Extension is a `SOURCE_TYPES` fact, not a domain. `00` forbids extension-alone conclusions, and every one of these appears in `photos.camera-events`' own `file_kinds`. |
| A lone `.xmp` with no paired original | XMP is a general metadata container written by PDF producers, InDesign, scanners and stock tools. The **pairing** is the signal; the extension is nothing. |
| `2026-03-14/` as a folder name | A bare date is a name. `00`'s standing rule for tokens of this shape — a bare 4-digit number is never a fact — applies unchanged. Only a *repeated* naming discipline across many folders is evidence. |
| A bounded card ingest, treated as a topic | `00`: "A session should never be treated as proof of topic, and it should not carry the same confidence as a hash match or a directly extracted document fact." A card offload looks exactly like a bounded session and must not be promoted by it. |
| An unreadable catalogue, read by its filename | `00`: "Unreadable, encrypted, corrupted, or unsupported files should retain basic metadata and remain eligible for manual attachment to a user-created group, but the system should not infer a purpose from their filename alone." |
| A scanner-made TIFF of a print | `photos.family-archive`'s. Scanner Make/Model, a scanner resolution slot and print-proportioned dimensions with no exposure slots; and its whole problem is that no true capture date survives, which is the opposite of this row's premise. |
| `Scan_2026-04-03_0001.pdf` | `photos.scanned-documents`'. A capture whose subject is a document. Shares nothing with this row but the word "capture". |
| A photographer's name or studio in author metadata | Never alone and never a destination: `00`, "Author and creator fields may be stale, generic, or generated by a tool rather than a person". Authorship is never a destination dimension. |
| `web_export/DSC_0342-2.jpg` | Recorded as a *derived* export at the archive's outbound edge, not as an original. It is also the case `00`'s adversarial suite names — duplicate suffixes on unrelated files — so the `-2` may mean nothing at all. |
| `model_release_signed.pdf` | `creative.licensing-rights`'. It sits inside a capture folder and is about the originals, which is why it is `also_holds_with` and a narrow `Independent Records` fall-through — but it is not this row's evidence. |
| A previews bundle read as thousands of photographs | Application-derived data. Reading it as photographs would flood the corpus with near-duplicates of files that already exist, and could drive a duplicate action against a real original. `00`'s structural vocabulary already has the right name for it: a "derived document set". |

---

## 4. `proposed_fields` — one, and it is a second, not a new one

`capture_date` (date, ceiling `direct`, `destination_eligible: false`).

**This is a reuse, not a mint.** `photos.camera-events` already proposed this key for R1c; the brief's
rule is to reuse an existing proposal rather than open a variant, and a second independent situation
needing the same key is *evidence for* that proposal. `00` names the fact in its own words —
"an EXIF field called `DateTimeOriginal` is raw metadata; capture date = 2026-07-17 is the file fact
derived from it" — and `canonical_fields.json` has no day-grained key: `capture_year` is year-grained
by construction and `creation_date` is the filesystem/document timestamp `00` explicitly distrusts
across restores and migrations.

This row's *reason* for needing the day grain differs from camera-events' and is worth recording
separately for R1c: camera-events needs the day to bound a run into an occasion; this row needs it
because a managed archive's natural unit is the **card or shoot day**, and the sidecar-to-original
pairing that defines the row is verified within a day. `destination_eligible` stays `false` and this
row does not widen it — a per-day folder level is `00`'s own warning case, a tree that "creates a
large number of tiny folders".

**No other field is proposed, deliberately.** Two candidates were considered and dropped:

- an `asset_role`-shaped key (original / sidecar / derivative / index) — this is `media_type`'s job
  on the photos schema and would be a synonym; on `creative` it is unauthorised until NJ-R1a-1 is
  answered.
- a `catalogue`-shaped key naming the index a file belongs to — a **value**, not a field, per
  CONNECTION.md §2: values auto-create at runtime, and `00` says the system "may create new values
  when it sees a new course, project, company, university, or event, but it should not invent new
  fields automatically".

No canonical key was minted. Nothing was written into `canonical_fields.json`.

---

## 5. `proposed_context_terms`

None proposed. This row's recognition is structural — file pairing, directory position, archive
manifests, database bytes — not lexical, and inventing a term list ("catalog", "raw", "selects")
would be a detector regex dressed as research, which R2 owns and this row may not pre-empt.

---

## 6. Reciprocal boundaries — stated in both directions

Every edge in the node names the discriminator **and** what the other side keeps. Summarised:

- **`photos.camera-events` (collision, the defining one).** Same bytes, same EXIF, same extensions.
  Discriminator: the index layer — a basename-paired sidecar, a catalogue above it, or a previews
  bundle referencing it. *Other direction:* where a catalogue sits over a personal camera roll,
  camera-events keeps the occasion and the year-then-event proposal; this row keeps only the index
  layer and the stability constraint. Same fixtures on both sides: `IMG_4821.HEIC` is theirs;
  `DSC_0342.NEF` + `DSC_0342.xmp` is this row's.
- **`creative.shoot-day-media` (collision, sibling, stated reciprocally rather than assumed since it
  is being written in parallel).** Discriminator is the **time axis of the situation**: that row is
  the *day* — one production, cards and sound rolls as they arrived, an event that ends — and this
  row is the *persistent store* those days accumulate into, whose defining artefacts exist only
  because the material outlives the day. Fixture on the seam: `20260314_cardB.zip`, which this row
  can only call an ingest. Where both readings hold they hold together, per `00`: "One file may hold
  facts from more than one domain without losing information."
- **`creative.commissioned-shoot` (collision).** Discriminator: what the files have in common. A job
  (brief, client, selection, delivery, including files with no pixels) versus the archive's own
  machinery, which would exist with no client at all. This row must not read a client out of a
  folder slug — it has no field to put one in.
- **`creative.stock-asset-library` (collision).** Provenance and use: acquired-to-be-reused finished
  assets with licence paperwork, versus unedited camera masters with a sidecar layer.
- **`creative.post-production` (collision).** The shared pattern is `00`'s own "linked asset names" —
  a working file referencing media it does not contain. A `.lrcat` and an editorial project file are
  the same *shape*. Discriminator: the referenced media class and the operation — assembling moving
  image and sound into a new work, versus indexing and rating existing frames. Neither row may claim
  a referencing database on the reference pattern alone.
- **`photos.family-archive` (collision).** Where the pixels came from: digitization versus camera
  original. The two rows recommend opposite tree orders for the same underlying reason, which is the
  cleanest evidence they are different situations.
- **`photos` (also_holds_with, not a collision).** The originals legitimately carry the photos
  schema's declared facts — "Photos may use capture year, event, location, people, camera
  information, and media type" — and this row declares none and cannot compete. The collision is with
  the camera-events *template* over which situation is being organised, not with the photos *schema*
  over which facts are true. CONNECTION.md's set-valued activation makes both plausible without
  either winning.
- **`construction_property.progress-photos` (also_holds_with).** **This row does not contradict that
  row's landed argument and says so explicitly.** That row argued its distinctness on capture rhythm
  — verbatim from its node, "a camera roll goes to many places once, a site walk goes to one place
  many times" — and recorded `photos` as `also_schema` rather than as a rival, citing the same `00`
  sentence about one file holding facts from more than one domain. Both halves stand. A builder or
  architectural photographer who catalogues their site walks produces files that are progress
  photographs *by rhythm and subject* and catalogued originals *by storage*, simultaneously. The one
  thing this row adds runs in that row's favour: **being catalogued must never be read as evidence
  about subject matter**, because a catalogue indexes whatever was imported. Fixture named on both
  sides: `Marsh Lane week 14/IMG_2044.HEIC` — that row's `IMG_2044.HEIC`, inside a catalogued tree.
  This memo also notes the direction of the tree recommendation is *not* a contradiction: that row
  puts site first because one place recurs; this row puts capture date first because no place, client
  or project recurs across a general archive. Same rule, different material.
- **`creative.licensing-rights` (also_holds_with).** Releases and grants live physically inside dated
  capture folders and are legally about the originals stored there. Paperwork theirs, originals this
  row's, one folder holds both.

### Neighbours considered that got **no** edge, and why

- **`code`** (a `must_consider_neighbors` entry). A `.lrcat` is SQLite, and a repository also
  contains databases and generated artefacts. No edge: `code`'s recognition is repository structure —
  manifests, source trees, version-control layout — and nothing about an archive resembles it. The
  shared fact is "contains a database", which is a `SOURCE_TYPES` observation, not a confusion.
- **`career`** (a `must_consider_neighbors` entry). Considered because a photographer's archive is
  their professional output. No edge: `career` is the individual's employment record and this row
  produces no employment evidence. A portfolio built *from* the archive is
  `creative.self-initiated-work`'s or the portfolio row's problem, not `career`'s and not this row's.
- **`photos.screenshot-captures`, `photos.scanned-documents`, `photos.home-video`,
  `photos.drone-captures`.** All considered; none confusable with the index layer. Drone captures was
  the closest call — drone stills land in exactly these catalogues — but the confusion there is with
  `photos.camera-events`, which already holds that edge, and adding a second hop would be edge
  inflation rather than a real discriminator.
- **`creative.deliverable-handoff`.** Named in the node's recognition as a *boundary* (the derived
  export set) but given no edge: the boundary is clean — an export folder named for a use is theirs
  the moment it exists — and a `collides_with` would imply confusion that does not occur.

---

## 7. Non-`00` quotations used

Two, both taken verbatim from landed sibling nodes and attributed to them by name in the JSON rather
than presented as `00`:

1. "a camera roll goes to many places once, a site walk goes to one place many times" —
   `construction_property.progress-photos.json`, its `recognition.deterministic`.
2. "a RAW and JPEG pair" — `photos.camera-events.json`, its `recognition.deterministic`.

Both were greped back out of those files before this memo was written. Every other quoted span in
the node and in this memo is verbatim `00`.

---

## 8. NEEDS-JOSEPH

**NJ-CRPC-1 — The move question (the row's sharpest, and genuinely a product decision).**
A photo catalogue is a database of *paths*, and `00` makes paths unstable by design while making the
product safe via the content hash. A third-party catalogue has no such protection, so a move proposal
on a catalogued original can silently break something the user values. `00` states no rule for a file
another application indexes. Alternatives, spelled out:
(a) the product detects catalogue-referenced originals and **refuses** to propose moves for them;
(b) it proposes moves **with an explicit warning** on the proposal canvas;
(c) it treats the catalogue as an ordinary file and says nothing.
The three differ in whether the product can break a user's working tool without telling them. The
node records (a)/(b) as its recommendation in prose and enforces neither.

**NJ-CRPC-2 — Scope fork: index layer only, or the whole archive?**
This row survived by claiming the index layer and ceding loose camera originals to
`photos.camera-events`. The alternative — a professional's whole archive, originals included, as one
situation — would make the two rows genuine rivals needing a mutex rather than co-holders. R1c may
prefer it. Recorded, not settled.

**NJ-CRPC-3 — The professional/amateur line.**
A serious amateur's catalogued archive is byte-identical to a working photographer's. This row sits
on `creative`, whose premise is professional practice. No signal distinguishes the two, and inventing
one would be the worst kind of guess. Either `creative` activates for amateurs too, or this situation
also needs a home on the `photos` schema.

**NJ-CRPC-4 — Dependency on NJ-R1a-1 (open; recorded, not resolved).**
The `creative` schema question is open and its row is being written in parallel. Its field set decides
whether `dimension_order` here can ever be non-empty and whether the capture-date-first, stay-shallow
recommendation becomes a real template order or stays prose. This row resolves nothing about
NJ-R1a-1 and did not touch the schema row.

**NJ-CRPC-5 — Previews bundles and the duplicate machinery.**
A previews bundle contains perceptually-matching thumbnails of everything in the archive, including
anything protected that was imported by accident. `00` gives the duplicate machinery — "Exact hashes
and perceptual hashes can identify duplicates and near-duplicates" — but no rule excluding
application-derived data from it. Whether derived bundles are excluded from perceptual duplicate
detection wholesale, or handled case by case, changes what the product does to real archives.

---

## 9. Self-verification

- `python3 -m json.tool` parses the node. ✔
- Key set compared against `photos.camera-events.json` and
  `construction_property.progress-photos.json`: identical to camera-events' minus its four
  `*_note` extras that it added for its own arguments, plus `node_test_note` which camera-events
  also carries. No key invented. ✔
- 33 quoted spans extracted mechanically and matched: all `00` spans found verbatim in
  `00-database-agent-product-design.md`; the two sibling-node spans found verbatim in their nodes and
  attributed. No fabricated quote. ✔
- `fields: []` — no field row written, as PR-6 requires. `proposed_fields` holds one key, and it is a
  **reuse** of camera-events' existing proposal, not a mint. ✔
- Every `file_examples.source_type` (`image`, `text_document`, `opaque_binary`, `filesystem`,
  `archive`) is in `SOURCE_TYPES`. ✔
- 12 file examples; observations and facts split; `facts_legal` is empty on every one of them, which
  is correct for a field-less placeholder row; no example writes a folder path as a fact. ✔
- Every edge id checked against `roster.json`: `photos`, `photos.camera-events`,
  `photos.family-archive`, `creative.shoot-day-media`, `creative.commissioned-shoot`,
  `creative.stock-asset-library`, `creative.post-production`, `creative.licensing-rights`,
  `construction_property.progress-photos` — all present. Every `falls_through_to` name is one of
  `00`'s nine residuals. ✔
- `never_alone` entries are true of tempting **real** files, not strawmen — the raw extension, the
  lone `.xmp`, the date folder name, the camera make, the bounded ingest, the unreadable catalogue's
  filename, the author field. ✔
- No threshold, statistic, confidence score, handling class, or file count invented anywhere. ✔
- Files written: `planning/domains/nodes/creative.raw-photo-catalogue.json` and this memo. Nothing
  else — no roster edit, no other node, no `src/`, no `check.py`. ✔

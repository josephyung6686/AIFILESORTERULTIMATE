# photos.screenshot-captures — lab notes

Node: `kind: template`, `schema_id: photos`, `launch: full`, `refuse_node: false`.
Output: [`photos.screenshot-captures.json`](photos.screenshot-captures.json).

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full; the authority. Every quoted span in
  the node was grep-verified against this file before it was written (52 spans, 0 misses; the
  check was re-run against the finished JSON).
- `planning/prompts/ALIGNMENT.md` — the node test, and this node's own licence: "photo-event vs
  screenshot-capture" is ALIGNMENT's example of a second template on one schema.
- `planning/domains/CONNECTION.md` + `CONNECTION-EXAMPLES.md` — closed edge vocabulary, activation
  ≠ grouping, browse-only `parent_id`, and fixture 8's shape (several templates, one schema).
- `planning/domains/_CONTRACT.md` — entry shape; rule 6's `{"residual_template": …}` spelling.
- `planning/domains/canonical_fields.json` — every field named in the node resolves here; nothing
  minted.
- `planning/domains/roster.json` — id, kind, schema, neighbours; every edge target re-checked
  against the roster ids programmatically.
- `planning/domains/nodes/photos.json` — the landed schema row. This node reuses its fields, its
  never-alone rules and its `media_type` open question rather than restating them.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`; all twelve file examples check out against
  it.
- `planning/deferred-catalogues/02-screen-resolutions.md` — the one catalogue this node's
  recognition genuinely consumes (`screen_resolutions`, exact-match, orientation-insensitive, and
  by its own rules never sufficient alone). Referenced by list id only; no resolutions copied, no
  regexes written, no tolerance invented.
- `planning/deferred-catalogues/01-tool-producer-strings.md` — read and **not** used as a
  screenshot signal: it is P6's *suppression* list for authorship metadata. See the gap below.

## The node test — why this is a node and not the schema's default template

Three independent differences from `photos`'s default template, any one of which would be thin
on its own:

1. **Detection signals are metadata-shaped in a different way.** The schema's deterministic list
   is led by camera EXIF, GPS and capture-time clustering. This template's is led by an exact
   display resolution + PNG format + a screen-capture software slot, and by OCR being *routed at
   all* — `00`: "It is the main way screenshots and opaque loose images become understandable to
   the pre-sorting engine."
2. **Recommended dimensions differ in both levels.** Schema default: `capture_year → event`. Here:
   `media_type → capture_year`. `event` is precisely the fact this material cannot supply, and a
   capture that *does* acquire one leaves this template.
3. **Privacy rules differ.** For a camera photo the sensitive parts are GPS and faces — metadata
   and pixels. For a screenshot the sensitive part is the OCR text, which is the only channel that
   makes the file legible at all. That is a different rule, not a stronger one.

`00` also separates the two situations in its own canvas sentence: "Photos supported by image
events and screenshot groups" — which is why `provenance` is `design` rather than `inference`, and
why the `design_cite` is that span and not one of the detection quotes (those support signals, not
the row's existence).

## Dimension order — the reasoning, including what argues against it

`media_type` first, `capture_year` second, `time_first: false`.

The uncomfortable part is that `00` makes capture media the time-first exception, and it gives a
reason: capture date is "a defining aspect of the material". For a screenshot that reason weakens —
what defines the file is what was on the screen — so I did not inherit the exception mechanically.
The counter-argument I could not dismiss is `00`'s one-child warning: inside an already-accepted
screenshot branch, a `media_type` level has exactly one child and should be flattened, leaving
`capture_year` leading. Both readings are written into `template.why` rather than one being hidden,
because which one applies depends on where Joseph puts the branch — which is the first half of the
node's `open_question`.

`location` and `people` were considered and rejected as dimensions: a screenshot has no GPS fix,
a place name on a captured map is where the *map* was pointing, and a name in a message thread is
on the screen rather than in the capture. Both appear as `never_alone` / `must_not_conclude` items
instead.

## Files considered and rejected

- **A `.ics`, a `.vcf`, an `.eml`.** This template never receives these source types. A screenshot
  *of* a calendar is an `image`; the calendar file itself is `SOURCE_TYPE = calendar`, which
  `CONNECTION-EXAMPLES` fixture 5 already settles (format is not a domain). Including one would
  have been the format-as-schema bug in fixture form.
- **A stitched "scrolling capture" PDF.** Real, but its evidence is a no-text-layer PDF routed to
  OCR, which is `photos.scanned-documents`'s fixture shape, not this one. Kept as a `work_types`
  value only.
- **A meme / saved social image.** It is an image with no screen-origin metadata at all — that is
  One-Off Images or Reference Clips reached from the *schema*, not a screenshot fixture. Including
  it would have padded the list with a file whose only claim to being here is that it is small and
  square.
- **A duplicate-family pair.** Perceptual-hash duplicate handling is universal (`duplicate_family`),
  not this template's; it survives as a `grouping_reasons` entry instead of a twelfth file.

The twelve that stayed cover: labelled-metadata vs OCR-only; the same content as capture vs as
record (the receipt pair); an archive manifest (`screenshots-2026-01.zip`); a file that looks like
this node's and belongs to a neighbour (`docs/img/error-state.png`, and `IMG_5120.HEIC` the
photograph of a screen); a file that is also another domain (`Screen Shot … .png`, the admissions
portal, `also_schema: college_applications`); and the abstention fixture `IMG_4821.png`, which is
`00`'s own file and produces **no** facts.

`docs/img/error-state.png` is the only example with `falls_through_if_inactive: null`. That is
deliberate rather than an omission: `00` excludes descendants of software project roots from
organization, so the correct outcome is *left in place*, and naming a residual there would have
manufactured a destination for a file the design says not to touch.

## proposed_fields — none, and why that is the right answer

Nothing was proposed. Every fact this material can carry is already a `photos` field
(`media_type`, `capture_year`), a neighbour schema's field reached through its own evidence
(`target_university`, `application_document_type`, `institution`), or a universal
(`duplicate_family`, `sensitivity_status`, `download_session`). Two temptations were refused:

- a `source_application` / `captured_app` field for "which program was on screen". It would be
  filled from OCR chrome or a window title — exactly the kind of per-template private key that
  produced the 574 — and `00` gives no sentence for it. If it is ever wanted it is a canonical
  field decision, not this row's.
- a `capture_origin` field to hold *screen vs lens*. That is `media_type` with a different name.

`proposed_context_terms` is likewise empty. The academic floor exists because a course code needs
academic *words* beside it; screen-origin evidence is metadata-shaped, not term-shaped. Term lists
for what a capture is **of** (admissions wording, receipt wording) belong to the neighbour domains'
own signals and to R2, and inventing them here would have been detector content in a catalogue row.

## Neighbours considered that got no edge

- **`photos.family-archive`** — shares "unreliable or absent EXIF" with this node, but the absence
  is never the signal on either side, so there is no evidence item to be mutex about.
- **`travel.bookings-confirmations`** — `00`'s boarding-gate capture is its most famous screenshot,
  and it still is not a collision: `00` explicitly refuses to let the capture identify a trip, and
  the honest routing is the Receipts and Confirmations residual, which the node already names. An
  edge would have implied a discrimination that the design says not to attempt.
- **`identity.*` / `medical.*`** — a capture of a passport or a lab result is real, but the
  discrimination is `photos`↔`identity` / `photos`↔`medical` at the *schema* level, and the landed
  `photos.json` row already authors both collisions. Repeating them at template level would have
  been a second copy of an edge that exists, which is the duplication `shares_field` is
  derived-only to prevent.
- **`code.notebooks-experiments`, `code.scratch-prototypes`** — closer in spirit to a captured
  traceback than `code.software-project`, but the discriminating evidence `00` names is repository
  roots and package manifests, which is `code.software-project`'s. One edge, on the row that owns
  the discriminator.

## Contract points where I followed CONNECTION over the dispatch prompt

- **`also_holds_with` is empty.** The dispatch prompt offers it to any node; `CONNECTION.md` §5
  restricts it to schema↔schema. The genuine also-holds facts here (a capture that is also an
  application portal record, also a financial record, also a project asset) are recorded per-file in
  `file_examples[].also_schema`, which is where a template can carry them honestly.
- **`collides_with` names templates, not schemas.** `must_consider_neighbors` on the roster row
  lists `code`, `finance`, `college_applications` — schema ids. §5 requires same-kind pairs, so each
  became the template on that schema that actually owns the discriminating evidence
  (`code.software-project`, `finance.receipts-expenses`, `applications.undergraduate-packet`), and
  two same-schema siblings were added (`photos.camera-events`, `photos.scanned-documents`) because
  the sharpest confusion in this node is with its own neighbours. Reciprocity is R1c's.
- **`parent_id` is null and was never authored** (PR-5: R1b never authors it).

## Gap noticed, recorded rather than filled

`00` makes "software metadata" one of the three screenshot signals, and catalogue 02 supplies the
resolutions half — but there is **no catalogue of screen-capture tool strings** to match the
EXIF/PNG `Software` slot against. Catalogue 01 is the opposite object (a suppression list that
discards tool strings so they never become `authored_by`). So one of `00`'s three named signals
currently has no injected content. I did not write one: naming tool strings is R2/R6's job and
`00` names none. Recorded here for R1c and for whoever owns the detector catalogues.

## NEEDS-JOSEPH (this node only)

1. **Where does an accepted screenshot branch live, and how deep?** `00` gives a location for the
   *residual* (Photos/Temporary Screenshots) and none for a non-residual screenshot branch. The
   three live options — `Photos/Screenshots/<year>`, a top-level `Screenshots` root, or no branch at
   all with every capture left in place and merely searchable (which `00` records as a real user
   preference: "If the user repeatedly keeps temporary screenshots in Downloads or Desktop, the
   system learns that their preferred policy is searchability without movement") — differ in what
   they do to someone's actual filesystem, not in what the evidence supports. This is the same fork
   the `photos` schema row recorded — whether `media_type` may open a folder level in that schema's
   default template; answering it there answers it here.
2. **Is `00`'s "approved Screenshot Inbox" a tenth residual, a user-defined residual area, or
   Temporary Screenshots under another name?** `00` names it once, beside the nine. The node routes
   to Temporary Screenshots and flags the ambiguity; R3 owns the residual library and will need the
   answer before it defines the slot.

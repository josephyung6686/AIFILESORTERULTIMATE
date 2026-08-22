# photos.drone-captures — lab notes

Node: `photos.drone-captures` · kind `template` · schema `photos` · launch `placeholder` ·
provenance `proposal`. Verdict: **built, not refused.**

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every span inside quote marks in
  the node file was grep-verified against this file before it was written; a mechanical re-check of
  the finished JSON found 48 quoted spans and 0 unverified.
- `planning/01-product-design-structured.md` — only §2.6 (Images) and §7.3 (the initial residual
  library), to confirm the residual names are spelled `00`'s way. `00` wins and nothing here rests
  on the numbered rendering.
- `planning/domains/_CONTRACT.md`, `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md` — the closed edge vocabulary, the node test, the
  activation-is-not-grouping firewall, PR-6 (career writes no field rows).
- `planning/domains/canonical_fields.json` — every `facts_legal` entry and both dimensions resolve
  to a key in it. Nothing minted.
- `planning/domains/roster.json` — confirmed the id, kind, `schema_id`, and that all four
  `collides_with` targets are roster rows.
- `src/evidence_shape/vocabulary.py` — the fourteen `SOURCE_TYPES`, checked mechanically against
  the six on `file_kinds` and the twelve on `file_examples`.
- Sibling nodes already on disk: `photos.json` (the schema), `photos.camera-events.json`,
  `travel.trip-photos.json` — read to align edges, not to rewrite. `photos.camera-events` already
  carries the reciprocal `collides_with photos.drone-captures`, so that pair is closed from both
  ends; the other three are one-way pending R1c.
- `planning/deferred-catalogues/04-camera-filename-patterns.json` — consumed genuinely, not
  decoratively. It already holds `fnp-dji` and `fnp-dji-timestamp`, and its own rules supply this
  node's best `never_alone`: a pattern names a naming convention rather than a media type, a
  filename carries no signal tier, and `fnp-dji`'s rationale records that the same convention is
  written by the vendor's handheld gimbal cameras. No regex was authored here (R2's) and no device
  gazetteer contents were invented (R4's).

## The node test, worked

The row survives on two limbs of three and the JSON says which.

- **Dimensions: no.** `capture_year → event`, identical to `photos.json`'s default. `00` states one
  order for capture material and says nothing about aerial work. This limb earns nothing and the
  node file does not pretend otherwise.
- **Detection signals: yes.** Two signals appear on no sibling: flight-attitude metadata in a vendor
  XMP block (aircraft and gimbal orientation, an altitude relative to the takeoff point), and a
  per-flight telemetry sidecar or log that brackets the media run. The bracket plays the anchor role
  a syllabus plays for a course.
- **File kinds: yes, and this is the sharpest one.** A flight deposits `text_document`,
  `spreadsheet` and `opaque_binary` members that the camera-roll, screenshot, scan, print, trip and
  export siblings never encounter. A situation whose member set includes non-capture files with
  their own `SOURCE_TYPES` is a different organizational situation, not a narrowing.
- **Privacy: yes, in kind.** A still discloses a point; a log discloses a path with a takeoff
  location that is normally a home or a client's premises.

**What would have refused it:** if the only difference were the word "drone" — a `media_type` value,
or a camera make — this would be a value and the correct output would be `refuse_node: true`. The
roster's own hint ("`media_type` distinguishes them inside photo events") is exactly the reading
that would make it a value, and it was tested against the sidecar and the log before being rejected.

## Files considered and rejected

- **A flight-app export receipt / subscription invoice.** Real, and a finance situation, not this
  one. No capture evidence, so it would never activate the photos schema.
- **Aircraft registration, insurance or remote-pilot certificate documents.** Genuinely part of an
  operator's corpus and genuinely not this node: they are `text_document` records with no capture
  metadata, belonging to the credentials and finance situations. Including them would have made this
  row "everything a drone owner keeps", which is an industry label, not an organizational situation.
- **Photogrammetry outputs (mesh, point cloud, orthomosaic raster).** Left off the `file_kinds` list
  after hesitating. The stitched composite is present as a `media_type` value because it is an
  image, but a mesh or point cloud is a `design_creative`/`opaque_binary` project artifact whose
  organizing unit is the deliverable, not the flight. Claiming it here would overstate what this row
  can recognise from evidence.
- **A calendar `.ics`, a `.vcf`, an email.** This situation never sees them; a flight writes no
  invitation and no contact card. CONNECTION.md's own worked files already show `.ics` and `.vcf`
  activating nothing on content grounds, and adding them here would have been the format-as-domain
  bug wearing a rotor.
- **A messaging-app re-encode of an aerial still.** Considered as a fixture and folded into
  `never_alone` instead: once the platform strips EXIF, no flight evidence survives, and the correct
  outcome is the camera-roll sibling or a residual home — never an asserted flight.

## proposed_fields — three candidates, all refused

`proposed_fields` is empty on purpose.

1. **A day-grained capture time** is genuinely needed here: the flight rule family brackets a run
   against a log's contiguous timestamps, and `capture_year` cannot bound a run.
   `photos.camera-events` already proposes `capture_date` for the same reason with `00`'s own
   wording behind it. Re-minting it would be the D6 defect (one concept, two columns) at the exact
   moment the catalogue is trying to kill it. **R1c note: this row depends on that proposal being
   accepted; if it is dropped, this row's event bracketing loses its time grain and the dependency
   should surface rather than be re-invented locally.**
2. **An altitude / flight-attitude field.** Refused. It is evidence that makes the situation
   recognisable; it never becomes a folder level, and inventing a field to hold a detection signal is
   how the 574 got 2,295 field names.
3. **A flight or sortie identifier.** Refused. A flight is a *value* of `event`, exactly as `00`'s
   values rule describes.

## Neighbours considered that got no edge

- **`research` (a `must_consider_neighbors` row).** Real overlap — a survey or mapping flight is a
  capture and a research artifact on disjoint evidence — but `also_holds_with` joins **schemas
  only** (CONNECTION.md §5) and this is a template row. The pair is already authored on
  `photos.json` as photos ↔ research; carried here as `also_schema: "research"` on `DJI_0221.JPG`.
- **`career` (the other `must_consider_neighbors` row).** Also real — an inspection or real-estate
  flight is a client deliverable — and also schema-level, so no edge from here. Additionally the
  career schema is a placeholder that writes no field rows (PR-6), so the career reading
  co-activates for protection and grouping and asserts nothing. Carried as
  `also_schema: "career"` on `north_elevation_roof_2026-06-12.jpg`, with a `must_not_conclude`
  saying exactly that.
- **`research.dataset-analysis`.** Tempting as a template↔template collision: a georeferenced raster
  from a mapping flight looks like a dataset. Refused, because the relationship is disjoint evidence
  (capture metadata versus analysis context), which is *also-holds* in shape, and `collides_with`
  must mean one evidence item confusing two rows. Writing it as a collision would be exactly the
  "`collides_with` used to mean `also_holds_with`" failure CONNECTION.md forbids.
- **`photos.social-media-export`.** Considered, since both can arrive as an archive. Refused: the
  manifest layouts genuinely differ (a card tree with RAW/JPG pairs and a log, versus an export
  tool's per-file sidecars), and `photos.camera-events` already carries that collision. Adding a
  third party to it would duplicate a discriminator that is already authored where it belongs.
- **`photos.family-archive`, `photos.scanned-documents`.** No confusion in either direction; a
  rephotographed print and a photographed page carry no flight evidence and this row claims none of
  their signals.
- **`identity.*`, `medical.*`.** The camera-roll sibling carries those collisions because a handheld
  camera is how protected content enters a corpus. An aircraft does not photograph passports, so
  claiming the same collisions here would be padding a row with borrowed hazard.

## The role_split near-case, recorded rather than authored

`00`: "The system must separate roles that happen to contain the same entity type." This situation
has one: **the place the aircraft launched from** versus **the place it photographed**. In a mapping
flight they are different places. It is not authored because `role_split` lives on the canonical
field list and a template row may not add to it; because the takeoff point is telemetry evidence
rather than something anyone files by; and because promoting it would create a destination-eligible
field whose values are usually somebody's home address. Flagged here for R1c, not resolved.

## NEEDS-JOSEPH (this node only)

1. **What does an `event` value denote for aerial work — a sortie, a flying day, or a job across
   several sorties?** A survey operator flying one site repeatedly and a hobbyist flying many sites
   once each want opposite answers. `00` offers the menu ("whether photographs should branch by
   year, event, location, or remain mostly flat") without choosing, and this is a decision about
   someone's real filesystem. Carried in the node's `open_question`.
2. **Where do the non-capture members live once a branch is frozen** — beside the media in the
   flight's folder, or in a scoped subfolder under it? `00` gives no sentence; the nearest mechanism
   is its scoped-`General` fallback, and its warning against "a large number of tiny folders" is why
   a per-flight subfolder is not recommended by default here. Carried in `open_question`.
3. **Inherited, not re-opened:** whether `media_type` may open a folder level at all is
   `photos.json`'s recorded question. This row branches on nothing that pre-empts it, and a
   photos-vs-aerial split at the top of the Photos branch would be an answer to that question rather
   than to this node's.

## Contract notes

- Where the dispatch prompt says "if present" about `CONNECTION.md` / `CONNECTION-EXAMPLES.md`, both
  are present and were treated as binding. No disagreement between them and the prompt arose in this
  node; the one place the prompt is looser (it lists `also_holds_with` as available to any row)
  yields to CONNECTION.md §5's schemas-only rule, which is why that array is empty here with a note.
- `parent_id` is `null` and was never a candidate: R1b does not author browse shelving (PR-5).
- `shares_field` is not serialized anywhere in this node; it is derived.
- No numeric threshold, no confidence score, and no handling class appears in either output file.

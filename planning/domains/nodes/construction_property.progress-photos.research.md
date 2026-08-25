# construction_property.progress-photos — lab notes (template row)

**Depth: J-DEPTH.** Deepening pass over a verified gist draft.

Row: `kind: template`, `schema_id: construction_property`, `launch: placeholder`. Verdict: **kept,
but materially narrowed**. `fields: []`; `proposed_fields: []`.

## Sources and comparison set

Authority read: `00-database-agent-product-design.md`, `01-product-design-structured.md`,
`ALIGNMENT.md`, `_CONTRACT.md`, `CONNECTION.md`, `CONNECTION-EXAMPLES.md`, `roster.json`,
`canonical_fields.json`, `DECISION-BRIEF.md`, `ROSTER.md`, the legacy catalogue row, and
`src/evidence_shape/vocabulary.py`. The stamped prompt was generated before editing with
`python3 planning/domains/dispatch/make_prompt.py construction_property.progress-photos`.

The comparison set was the deepened `construction_property` anchor and the complete JSON/memos for
`construction_property.construction-project`, `site-diary`, `snagging-defects`, `site-survey`, and
`materials-delivery`; plus `photos.camera-events`, `screenshot-captures`, `scanned-documents`, and
`drone-captures`. The source-type boundary was checked against the vocabulary itself. The absorbed
legacy id remains `cons.progress-photos` (ROW), one-to-one.

## The correction this pass makes

The gist draft said the row stood because other construction rows used document structure while this
one used capture metadata, rhythm, and place. The observation is true; the conclusion was too quick.
EXIF, GPS, capture time, sensor dimensions, HEIC decoding, and bursts prove camera-capture
provenance. They do **not** establish the organizational situation *progress photography*. `image`
is a `SOURCE_TYPE`; `.jpg`, `.heic`, `.png`, and `.dng` are formats. Neither is a template. The
authoritative routing rule is: “The engine should treat the file extension as a routing signal rather
than an assumption about meaning, inspect the real MIME type or file signature where possible, and
dispatch each file to a type-specific extractor.”

Site, date, and work stage are values. A GPS point can be a site; a timestamp can be a capture date;
*pre-pour* can describe a stage. None says why an image was kept. The same bytes may be an ordinary
camera event, diary attachment, defect item, delivery record, survey observation, or project
evidence. “Topic answers what a file is about, while purpose answers what the file was for.” The row
therefore survives only as a deliberately repeated, annotated, captioned, or issued photographic
record of changing works, or sparse captures whose record purpose is supported by an accepted
project/diary relationship. Capture metadata corroborates that situation; it cannot create it.

The accepted relationship supports membership without copying facts. “The graph does not
automatically copy those missing facts onto sparse files.” A photograph can join a Marsh Lane
project without acquiring a site, diary date, or work stage merely because its neighbours have them.

## Node test, leg by leg

### Detection signals

The construction schema default is property or asset first, then instruction/job or document
function, and not time-first. Its activation posture is professional apparatus around an instruction:
a site or property plus a job, contract, report, statutory, valuation, or management structure. The
anchor expressly makes a site name, organization, document-type word, source type, and format
never-alone.

This row differs only on purpose-bearing photographic-record evidence: comparable viewpoints
repeated across accepted site walks; burned-in date/site/reference annotations from a site-record
application; a generated photo report with dated captions and an issue identity; an archive manifest
describing progress sets; or an accepted project/diary relationship around changing-work captures.
A loose `IMG_2044.HEIC` with EXIF and reinforcement in frame is insufficient. It first supports the
`photos` schema and supports this template only when record purpose is evidenced.

The construction-project row owns contract envelope, award, programme, completion, and handover.
The site-diary row owns dated narrative or daily-report structure. Neither default describes an
issued photographic schedule or repeated comparable-viewpoint record. Conversely, a project or
diary containing images does not automatically activate this row.

### Recommended dimensions

The binding JSON order is empty because the placeholder schema declares no fields. No key may be
minted to make prose executable. If suitable fields are later licensed, the practical recommendation
is project/site context first and capture date beneath it. It is not year-first: “For document and
record domains, project, function, or subject usually comes before time because putting year first
scatters related work across calendar folders.” A date is unintelligible without the site/job whose
changing state it records.

This differs from `photos.camera-events` (`capture_year → event`, `time_first: true`) but not enough
by itself from project or diary, both of which can browse photos under job and date. Dimension order
supports the camera-roll boundary; it is not an independent licence against construction neighbours.

### Privacy rules

Site photography is incidental surveillance: faces, registrations, neighbouring property, home
interiors, security-relevant layouts, and GPS can appear without consent. `00` names GPS metadata
among potentially protected content and says: “Protected material should not be included in
cloud-model prompts by default, should not display raw content in general group summaries, and
should not be moved automatically without a user policy that explicitly permits it.” This is more
capture-specific than the project envelope and diary text, but does not differ from photos merely
because the captures happen at work. NJ-CP-10 remains open.

**Verdict.** Keep only on purpose-bearing record evidence. If implementation cannot express that
separately from project/diary grouping, refusal is preferable to firing on image bytes. The JSON
records that product choice instead of pretending the test eliminated it.

## Concrete files and rejected conclusions

The JSON keeps nine fixtures, spanning the actual evidence without padding.

- `IMG_2044.HEIC`: forty Tuesday captures repeated at a supported site, showing reinforcement. EXIF
  proves a camera capture, not progress. Comparable-series or accepted project/diary evidence is
  required; otherwise it is camera-events or One-Off Images.
- `20260311_0812_MarshLane_stamped.jpg`: burned-in date, coordinates, compass, and site label.
  A site-record tool supplies purpose evidence, but OCR remains an observation and no label alone
  becomes a site fact.
- `Photo report - week 14.pdf`: the clearest positive—an issued grid of dated captions with site
  header and report reference. It is `text_document`, proving the situation is not the image source
  type. Embedded thumbnails are derivatives, not hash duplicates of loose originals.
- `IMG-20260311-WA0009.jpg`: messaging stripped its EXIF. The design says the system “must not mistake the absence of
  EXIF for proof that an image is a screenshot.” Missing EXIF neither disproves nor proves progress.
- `IMG_2051.HEIC`: snagging collision—same burst, crack and measuring tape. A marker, statused list,
  or accepted defect group supports snagging; interval record purpose supports this row.
- `IMG_2077.HEIC`: the site manager's lunch. Device, day, work-hours rhythm, and nearby GPS all agree
  with the walk. It defeats every detector based only on metadata, time, or place.
- `site_walk_20260311.mp4`: the situation can use `audio_video`; duration and codec are extraction
  facts, while narration or accepted walkthrough context supplies purpose.
- `progress_photos_week14.zip`: manifest evidence may support the set without unpacking. `.zip` alone
  never does; unreadable archives fall through safely.
- `IMG_1148.HEIC`: pallet and photographed delivery note. Delivery grouping or legible document
  structure supports that sibling; capture on site does not make it progress photography.

Rejected: a screenshot of a plan/message (Temporary Screenshots unless OCR activates another
schema); thermal survey output (`site-survey` when instrument/report purpose is supported); a buyer's
condition schedule (`inventory-inspection`); plant damage claim close-up (`plant-hire`/claim group);
a drone mapping sortie (`photos.drone-captures`, possibly also this purpose); and one attractive
completed-room image (camera event, marketing, or One-Off Image absent record purpose).

## Reciprocal boundaries and shared bytes

### construction_property.construction-project

Shared bytes: `IMG_2044.HEIC` inside the Marsh Lane project. From project toward this row: the branch
root gives job context, but contract envelope or folder membership does not turn every image into
progress evidence. From this row toward project: a repeated photo set proves no award, sum,
programme, completion, or handover. The relationship may be accepted while this row supplies the
photographic-record reading. This pass adds the previously missing reciprocal on this side only.

### construction_property.site-diary

Shared bytes: dated images embedded in `Site Diary 2026-03-11.pdf` and retained loose. Labour,
weather, plant, events, and daily structure support diary; attachments do not automatically support
progress. A captioned/repeated set has no labour-weather narrative and must not be called a diary. A
minimal photo-led diary may support both; date, site, and stage are shared values and discriminate
neither.

### construction_property.snagging-defects

Shared bytes: `IMG_2051.HEIC`. A measure, fault caption, item/status/trade, or accepted register
supports snagging. Visible damage alone is not a defect fact, and burst adjacency cannot copy
progress meaning. The neighbour correctly states that its photos are grouped register members,
never activation evidence; this row cannot absorb them merely because it understands captures.

### photos.camera-events and SOURCE_TYPE/format

Shared bytes: `IMG_2044.HEIC`. EXIF Make/Model, DateTimeOriginal, GPS, sensor shape, HEIC decoding,
bursts, and RAW/JPEG pairs support camera provenance and event clustering; they never prove progress.
A PDF report can activate here without being a camera event, while loose originals may still carry
photos facts. “One file may hold facts from more than one domain without losing information.” The
relationship is capture facts plus, only when supported, record purpose—not bytes versus bytes.

`photos.scanned-documents` wins on page geometry, OCR structure, and labelled slots; photographed
paperwork is not a scene record. `screenshot-captures` wins on display resolution, PNG/software
metadata, and screen-origin evidence; construction subject does not make it progress. `drone-captures`
wins on aircraft, gimbal, altitude, and flight-log structure. A construction overflight may carry
both drone provenance and progress purpose, so purpose must not overwrite provenance.

The repository's camera hierarchy is the guardrail: “EXIF is strong photo evidence; capture time,
GPS, and sensor-shaped dimensions reinforce it; exact display resolutions, PNG format, and software
metadata may support a screenshot hypothesis; conflicting signals should lead to abstention rather
than an invented classification.” Every clause concerns photographic origin, not construction
situation.

## Fields, work types, and values

`fields` and `proposed_fields` are empty. PR-6 and the placeholder contract forbid field rows. The
photos schema already owns `capture_year`, `event`, `location`, `people`, `camera_information`, and
`media_type`; do not mint `site_capture_date`, `progress_location`, or construction copies. Work
stage is a value, not a child node or key.

The JSON `work_types` are values: capture set, before/after sequence, pre-cover-up record, generated
report, marked-up capture, panorama, walkthrough, overflight, supplied set, and photographed-document
boundary case. None activates by its label alone.

## NEEDS-JOSEPH

- **NJ-CP-9 — independent template or project/diary evidence profile?** Alternatives: independent
  template; detector/grouping profile nested under project; diary evidence only; or refusal with
  photos plus graph relationships. Independent form risks parallel-tree duplication; the others may
  lose a reusable photographic-record situation.
- **NJ-CP-10 — work photographs and photos protection.** Decide whether faces, homes, registrations,
  and GPS in professional records receive the photos protective posture. Work context is not consent.
- **NJ-CP-11 — one set, three browse contexts.** When originals support camera events, a project, and
  a diary entry, choose project, diary date, photos, or leave-in-place graph links. No answer may copy
  missing facts or turn site/date/stage values into keys.

## What changed in this pass

Preserved: nine fixtures, empty fields/proposals, residuals, sensitivity, lunch false positive,
snagging/delivery seams, site-first/date-second prose, and `time_first: false`.

Changed: removed retired GIST framing; rejected *different evidence class* as sufficient; rewrote
definition and activation around purpose-bearing records; made EXIF, repetition, structural subject,
site, date, and stage insufficient alone; added the construction-project reciprocal; deepened diary,
snagging, SOURCE_TYPE/format, and photographic-neighbour boundaries; and expanded the unresolved
existence question.

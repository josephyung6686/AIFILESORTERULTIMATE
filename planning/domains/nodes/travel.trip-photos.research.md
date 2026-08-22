# `travel.trip-photos` — lab notes (R1b)

Row: `kind: template`, `schema_id: photos`, `launch: placeholder`, provenance `inference`.
Verdict: **node stands** (`refuse_node: false`). Reasoning below.

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every span in quote marks in the
  node file was grep-verified against it (`grep -qF`) **before** it was written; 39 candidate
  spans were checked, 39 matched, none was written from memory.
- `planning/01-product-design-structured.md` — **not opened.** Nothing in this node needed a
  section number, and `00` is the authority. Recorded rather than skipped silently.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`,
  `planning/domains/CONNECTION.md` (full), `CONNECTION-EXAMPLES.md` (headings + the binding
  lines).
- `planning/domains/roster.json` — my row, plus `photos`, `photos.camera-events`,
  `photos.screenshot-captures`, `photos.scanned-documents`, `photos.family-archive`,
  `travel.bookings-confirmations`, `identity`, `finance`, and the full id list (edge targets
  checked against it).
- `planning/domains/canonical_fields.json` — the six photos keys and their
  `destination_eligible` seeds. No new key was needed; `proposed_fields` is empty.
- `planning/domains/nodes/photos.json` — the landed schema node. My detection vocabulary,
  never-alone list and example style deliberately align with it rather than restating it.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` checked mechanically against every
  `file_examples[].source_type` and `file_kinds.source_types`.
- `planning/deferred-catalogues/04-camera-filename-patterns.md` (the `camera_filename_patterns`
  list, cited by id for the filename-convention observation — no regex reproduced here) and
  `planning/deferred-catalogues/10-gazetteers/` (inspected; see the gap below).

## Node test — why this is not the Photos schema's default template

`photos.camera-events` is the default (`capture_year` → `event`, camera/time/GPS event
clustering). This row differs on all three of the things the node test asks about:

1. **Detection signals.** A camera event is a burst: one camera identity, one bounded session.
   A trip is a *sustained displacement* — consecutive days whose resolved places stay away from
   the corpus's habitual capture cluster, usually across two or more devices. `IMG_8890.jpg`
   (the wedding one afternoon two hours from home) is the fixture that separates them: identical
   per-file evidence, opposite reading.
2. **Dimension order.** `event` → `location`, `time_first: false` — a deliberate departure from
   `00`'s stated photos exception, argued in the node's `template.why` from `00`'s own canvas
   warnings (a level that repeats the parent; a level that produces one child) plus the fact that
   trip values carry their own year. The New Year fixture (`20260101_004512.jpg`) is what makes
   year-first actively wrong for this situation.
3. **Privacy rules.** Stricter than the schema default: a trip run is a dated record of when a
   household was away, and trip corpora routinely contain photographed passports, boarding passes
   and bills sitting inside an ordinary photo run. The rule recorded is that a member whose OCR
   carries document-identity or account wording leaves the trip reading and enters protection.

If any one of those had been the only difference I would still have kept the row; all three is
comfortable. What I did **not** do is claim a distinct field set — templates reuse
`schema_id: photos`, `fields` is empty, `proposed_fields` is empty.

## The honest weakness: this situation is mostly a cross-file signal

Per-file schema activation (CONNECTION §4) sees one file's own evidence and explicitly excludes
"P9 group membership, embeddings, any folder path, any other file's facts". A trip is a property
of a *run*. So the deterministic signal that actually identifies this situation — consecutive
days, displaced place cluster, second device — cannot run at activation time at all. It is P9
neighbourhood evidence and P10 template fit, after grouping.

I wrote that into the signal itself rather than hiding it, and the consequence is visible in the
file examples: `DSC_0771.JPG` (no GPS, inside the span) is `group_without_copying_facts: true`,
not a file that gets a location from its neighbours. That is `00`'s own rule applied to this
node: "The graph does not automatically copy those missing facts onto sparse files."

Practical reading for R1c: at activation this template's members are simply `{photos}` files;
the trip is a grouping and a template choice, never an activation output.

## Files considered and rejected

- **`trip-itinerary.pdf`, `boarding-pass.pdf`, `airbnb-receipt.pdf`** — the records half. They
  belong to `travel.bookings-confirmations` (finance schema). One survives in my list *as a
  collision fixture only* (`Hotel confirmation - Kyoto - 2025-12-29.pdf`, `facts_legal: []`),
  precisely to show that a place name in a filename does not activate photos.
- **`.gpx` / Strava export / a phone location history JSON** — tempting for a "trip" node and
  rejected: they are `code_structured` route data with no capture, no roster schema that
  legitimises a track, and inventing one would be the format-as-schema bug. Their isolated files
  are residual material.
- **A passport photo *for* a visa application** (studio headshot) — looks travel-adjacent, is
  `identity` material; not a trip capture at all, so it is not in the list.
- **Study-abroad photographs** — a real overlap with `academic.study-abroad`, deliberately left
  out of the list and off the edges: the discriminator is whether the *documents* of a study
  period exist, and that is a judgement about the neighbour's evidence, not about a capture.
  Recorded here rather than asserted as an edge.
- **A scanned print from a 1990s family holiday** — that is `photos.family-archive`'s situation
  (unreliable EXIF, decade-level dating), not this one.

## `proposed_fields`

None. Every fact this situation needs already exists as a canonical key: `event` holds the trip
(`Japan Trip 2025` is `00`'s own value example), `location` holds where it went, `capture_year`
and `camera_information` and `media_type` and `people` are inherited unchanged. A `trip_start` /
`trip_end` pair was considered and rejected — a date span is derived from the run's
`DateTimeOriginal` values and would be a second spelling of information the fact rows already
carry, which is exactly the defect D6's ratification exists to kill.

## Neighbours considered that got **no** edge, and why

- **`photos.scanned-documents`** — overlaps on the photographed-receipt and photographed-passport
  fixtures, but the discriminating evidence is the same one I already wrote against
  `identity.immigration-visa` and `photos.screenshot-captures`; a third edge on the same evidence
  item would be noise, not information.
- **`academic.study-abroad`**, **`career.consulting-client-engagement`** (business travel),
  **`medical.personal-health-records`** (a hospital stay produces the same displaced multi-day
  metadata shape) — all three are real confusions, but the confusion lives in the *interpretation*
  of a displaced run, which is why they are `needs_llm` entries rather than edges. An edge asserts
  a discriminating evidence item; I could not name one for these without inventing it.
- **`finance` / `identity` as named in `must_consider_neighbors`** — both are **schemas**, and
  `collides_with` joins same-kind pairs only (CONNECTION §5). I collided with their template rows
  instead: `travel.bookings-confirmations` (finance) and `identity.immigration-visa`. The
  neighbour concern is answered; the edge shape follows the contract.
- **`also_holds_with` is empty on purpose.** The dispatch prompt offers it to any node; CONNECTION
  §5 restricts it to schema ↔ schema. **CONNECTION wins**, as the prompt itself instructs, so a
  template row authors none. The genuine two-schema files are still recorded where a template can
  record them — `file_examples[].also_schema` (`identity`, `finance`) — and the schema-level
  edges that would express them belong to the `photos` schema row, which already carries the
  `research` one.
- **`shares_field`** was never authored (derived-only), and `parent_id` is left `null` — R1b never
  authors browse sugar (PR-5).

## Residual and fallthrough

`falls_through_to: ["One-Off Images"]` — the roster's own `must_consider_residuals` for this row,
and the right one: a capture that is not part of an accepted trip is still a capture. Per-file
fallthroughs in the examples reach four other `00` names where the file itself is a different kind
of thing (Protected Records, Receipts and Confirmations, Temporary Screenshots, Review Later).

Note on CONNECTION §5 invariant 5 (a residual home that shadows a domain template): none of
`00`'s nine residual names is "Travel". `00` mentions `Personal/Travel/Confirmations` only as an
example of a *user-approved* branch in the Gate B12 passage, not as a residual template, so no
shadowing edge is owed from this node. The Receipts-and-Confirmations connection is
`travel.bookings-confirmations`'s to carry.

## Gap found while working

**There is no place gazetteer.** `location` is the second dimension of this template and one of
its two strongest signals, and `planning/deferred-catalogues/10-gazetteers/` currently holds
schools, orgs-and-roles, research venues and course-code formats only. Everything place-shaped in
this node is therefore written as "resolved to a place name" with the rule family named and no
list behind it, and the never-alone entry says so explicitly. R4 owns the content; I did not
invent gazetteer contents, and no regex or pattern appears anywhere in the node file.

## NEEDS-JOSEPH (this node only)

- **NJ-travel.trip-photos-1 · Does the trip template override `00`'s time-first exception?**
  Recorded in the node's `open_question` and repeated here because it is the one decision in this
  row that touches someone's real filesystem. This node recommends `event` → `location`; the
  schema default is `capture_year` → `event`; `00` licenses the user to reverse either way. The
  fork is whether a corpus spanning many years should default back to year-first browsing.

Already open upstream and **not** re-opened here: **NJ-R1a-2** (does travel deserve its own small
schema — neither photos nor finance can express *trip → record type*, and this node holds only the
capture half), and **NJ-R1a-4** (`people` seeded `destination_eligible: false`; trip photographs
are one of the places users most often want a person level, and widening it is a canonical-list
edit only Joseph should make).

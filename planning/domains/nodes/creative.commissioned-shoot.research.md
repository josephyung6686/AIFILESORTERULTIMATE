# R1b research memo — `creative.commissioned-shoot`

**Depth: J-DEPTH**

## Verdict and scope

The node survives, narrowly. It does not mean “professional-looking photograph” and it does not
own a camera roll. It means a photographic commission whose own files expose a chain: brief,
production-day apparatus, captures, selection, review/retouch, rights paperwork, and delivery.
The chain contains documents that have no pixels, and that is the decisive difference from a
Photos camera event. The row absorbs legacy `photo.commissioned-shoot`.

The node test was applied on all three legs. Detection differs because the commission chain is
role- and reference-bearing evidence rather than camera metadata. Privacy differs because a shoot
packet carries releases, private contacts, precise locations, unreleased subjects, usage limits
and embargoed outputs. Dimensions cannot distinguish the row today: the creative schema declares
no fields, so `dimension_order` is correctly empty. The deferred recommendation—client, then
project/shoot, then stage or artifact type—does not count as a currently executable difference.

## Authority and sources used

- `planning/00-database-agent-product-design.md`: authoritative evidence/extraction, observation
  versus fact, image, archive, graph, privacy, template and residual rules. The JSON's
  `design_cite` is a verbatim span from this file.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/CONNECTION.md`,
  `CONNECTION-EXAMPLES.md`, and `_CONTRACT.md`: schema/template separation, node test,
  set-valued activation, edge vocabulary, reciprocal collision discipline and empty-field rule.
- `planning/domains/canonical_fields.json`: no key was minted. The creative schema already parks
  `project`, `stage`, `artifact_type`, and `client` as adoption proposals.
- `planning/domains/roster.json` and `ROSTER.md`: assignment, absorbed legacy id, neighbours and
  output ownership confirmed.
- `src/evidence_shape/vocabulary.py`: every example uses one of the closed `SOURCE_TYPES`.
- `planning/domains/nodes/creative.json`, `photos.json`, `career.json`, `code.json`,
  `identity.core-documents.json`, `creative.raw-photo-catalogue.json`, and the landed neighbour
  rows: shape, refusal discipline, legal fact boundaries and edge idiom.
- `planning/domains/nodes/finance.crypto-assets.research.md`: full-depth launch calibration only;
  none of its domain claims were imported.

## Bottom-up file findings

Ten concrete fixtures are encoded in JSON. They cover a labelled brief, production paperwork,
camera original, selection spreadsheet, layered retouch file, OCR release, native email, archive
manifest, the product-catalogue collision, and a sparse personal-looking camera file. Together
they expose three useful joins:

1. Brief/call-sheet labels can be direct observations, but a counterparty fact is still illegal
   while the creative schema has no fields.
2. A generic RAW filename may join a shoot group through explicit references, yet the graph may
   not copy client or project facts onto it.
3. The release and delivered product image show that a file can have legal or retail evidence of
   its own. Those are candidate schema co-activations, not permission for this template to author
   `also_holds_with`.

The collision fixture is `DSC_4821.NEF`. The bytes are the same on both sides. Camera EXIF and an
event-shaped run support Photos; a brief, call sheet, selects sheet and delivery chain support the
commissioned-shoot situation. Neither side gets to reinterpret the other's evidence item. Every
JSON collision uses the explicit `SAME FIXTURE BOTH SIDES` wording because P6 activation step 3
and P8 consume the signal to decide which side a shared evidence item counts toward.

## Files considered and rejected

- A lone RAW, JPEG or HEIC with EXIF: Photos evidence, not commission evidence.
- A personal portrait made with studio lights: subject and technique do not state purpose.
- A downloaded stock photograph: no making chain; stock/library handling or an image residual.
- A moodboard of reference images: potentially creative-project context, but not a shoot unless a
  brief and production chain connect it.
- A photographer's invoice: finance/business evidence. It may corroborate a counterparty but is
  not the photographic work and was excluded from the kept examples to avoid widening this row.
- A wedding guest's camera roll: an event collection without a commissioning chain.
- CCTV/security stills and machine-vision captures: capture media for another operational
  purpose, not a photographic creative job.
- A portfolio PDF containing the final image: Career owns self-presentation context; the image's
  original job provenance remains a separate group.
- A website repository that displays the gallery: Code owns the rooted source structure. The
  photographs do not turn package files into creative-shoot evidence.
- A client-named folder with no brief, call sheet, release, select reference or delivery record:
  a name-alone false positive and therefore insufficient.

## Reciprocal boundaries

- `photos.camera-events`: camera/event structure versus commission/production apparatus. Same
  RAW bytes; neither side copies its facts across the group boundary.
- `creative.raw-photo-catalogue`: archive machinery versus job chain. A catalogue can index the
  same RAW files, but its storage purpose remains distinct from why the images were made.
- `career.portfolio-work-samples`: client delivery versus self-presentation. The same final image
  may participate in both accepted groups; its polished appearance proves neither purpose.
- `code.software-project`: repository structure versus photographic delivery. A web gallery's
  package manifest stays Code evidence even inside a shoot directory.
- `retail_hospitality.product-catalogue`: selected item-keyed selling asset versus the full making
  chain. The product row already carries the reciprocal fixture, and this side now names the same
  bytes and discriminator.

Neighbours considered without an edge:

- `creative.shoot-day-media`: a commissioned shoot may contain that row's capture-day packet, but
  the landed sibling explicitly declines an edge because the packet can serve personal or
  documentary production too. No reciprocal same-evidence mutex is established.
- `creative.client-engagement`: broader engagement context can contain several shoots. It is a
  browse/group relationship, not evidence-item competition, and the closed vocabulary has no
  broader/narrower edge.
- `creative.deliverable-handoff`: this row includes a photographic handoff, but the neighbour is
  the reusable handoff situation. Shared group membership is not a schema co-activation and no
  same-fixture mutex was justified.
- `legal.*`: the release fixture carries legal intent, recorded on the example and NJ-CS-3. A
  template-to-template `also_holds_with` would violate CONNECTION's schema↔schema intent rule.

## Fields and dimension recommendation

`fields: []` and `proposed_fields: []` are deliberate. This template does not copy the creative
schema's proposals and does not mint `shoot`, `commission`, `deliverable_type`, `shoot_date`, or
`subject`. If R1c adopts the creative schema's existing proposal set, `client → project → stage →
artifact_type` becomes expressible. Capture date is useful inside the shoot, but putting time
first would scatter one client job across days when prep, shoot, review and delivery span time.
The user may flatten a one-client or one-project branch.

## Sensitivity and salvage discipline

This was a fresh row; no partial draft existed. The potentially-sensitive posture is driven by
the packet rather than by every delivered photograph: identities and contacts on call sheets,
precise private locations, releases, usage restrictions, unpublished portraits and embargoed
assets. A public delivered image does not downgrade its production packet.

## NEEDS-JOSEPH

- **NJ-CS-1 — deferred fields.** Adopt the creative schema's existing canonical-key proposals;
  keep this row recognition-only; or refuse templates whose dimension distinction cannot yet be
  serialized.
- **NJ-CS-2 — Creative plus Photos.** A commissioned RAW independently supports Photos through
  EXIF and Creative through job apparatus. Confirm whether R1c authors a creative↔photos
  schema-level `also_holds_with` intent.
- **NJ-CS-3 — releases.** Decide whether model/property releases always fall through to Protected
  Records until explicit user attachment, or may remain attached to a locally protected shoot
  group without cloud/model exposure.
- **NJ-CS-4 — delivered product image.** Confirm shared-material policy when the same physical
  image is both a catalogue selling asset and the shoot's output. The reciprocal collision
  distinguishes evidence ownership but cannot choose one physical path.

## Self-verification target

The owned JSON must parse; its id and paths must match the assignment; fields remain empty; all
source types and edge targets must resolve; all edge values are objects; every collision names
the same fixture on both sides and its discriminator; no thresholds, scores or handling classes
are introduced; and no file beyond this row's two assigned outputs may be written.

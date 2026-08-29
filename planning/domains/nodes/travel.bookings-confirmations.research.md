# `travel.bookings-confirmations` — R1b lab notes

Status: complete; `refuse_node: false`.

This row is a placeholder template over the `finance` schema. It describes the records half of
travel, not a Travel category and not a trip fact. A trip remains an accepted P9 group or a
user-created branch until NJ-R1a-2 is decided.

## Sources used

Repository authorities, in precedence order:

- `planning/00-database-agent-product-design.md`, read in full. This supplies the observation/fact
  split, the small schema rule, travel as a template-library situation, conservative extraction,
  group membership without fact propagation, residual behavior, and privacy boundaries.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/CONNECTION.md`, and
  `planning/domains/CONNECTION-EXAMPLES.md`. These supply the two roster kinds, set-valued schema
  activation, browse-only `parent_id`, closed edge vocabulary, template-to-schema join, and the
  grouping firewall.
- `planning/domains/_CONTRACT.md`, `planning/domains/roster.json`,
  `planning/domains/canonical_fields.json`, and `src/evidence_shape/vocabulary.py`. These confirm
  the assignment, snake_case/D6, the Finance field set, destination eligibility, residual names,
  and the fourteen legal `SOURCE_TYPES`.
- `planning/01-product-design-structured.md` only for the relevant facts/facets, template-library,
  residual, and privacy renderings. It was used as a locator; `00` remained authoritative.
- `planning/overnight/council/DECISION-BRIEF.md` for ratified D2, D6, and J-IND, and
  `planning/domains/ROSTER.md` for NJ-R1a-2.
- Landed neighbors: `finance.json`, `finance.receipts-expenses.json`,
  `travel.trip-photos.json`, `photos.json`, `identity.json`,
  `photos.screenshot-captures.json`, `academic.study-abroad.json`,
  `research.conference-presentation.json`, and `career.recruiting.json` plus their relevant
  research notes.

Primary format references used only to fact-check concrete file shapes, not as product-design
authority:

- [IATA Bar Coded Boarding Pass Implementation Guide, version 7](https://www.iata.org/contentassets/1dccc9ed041b4f3bbdcf8ee8682e75c4/2021_03_02-bcbp-implementation-guide-version-7-.pdf).
  It confirms structured boarding-pass and e-ticket itinerary-receipt data such as passenger,
  operating carrier, flight, travel date, origin, seat/check-in data, and document kind, while
  also showing that visual layouts vary.
- [Apple Wallet Passes documentation](https://developer.apple.com/documentation/walletpasses) and
  [airline boarding-pass semantic tags](https://developer.apple.com/documentation/walletpasses/creating-an-airline-boarding-pass-using-semantic-tags).
  These confirm that a Wallet boarding pass is a structured pass package and may carry provider,
  passenger, origin/destination, departure, gate, boarding, seat, and related-leg grouping data.
- [RFC 5545, iCalendar](https://www.rfc-editor.org/info/rfc5545/). It confirms the structured
  `VEVENT` slots used in the `.ics` fixture: `UID`, `SUMMARY`, `DTSTART`, `DTEND`, `LOCATION`,
  `ORGANIZER`, and `URL`/description fields. Those generic slots do not make every calendar event
  a booking.
- Schema.org's canonical
  [FlightReservation](https://schema.org/FlightReservation),
  [LodgingReservation](https://schema.org/LodgingReservation), and
  [RentalCarReservation](https://schema.org/RentalCarReservation) types. They confirm that real
  confirmation email/HTML structures commonly distinguish a reservation identifier, status,
  named traveler or guest, provider, and type-specific route, stay, or pickup/drop-off slots.

No source was used to import private field names or detector thresholds. The external references
only checked that the examples and proposed context terms describe real artifacts.

## Node test

The row passes honestly.

- The Finance schema's default template is `institution -> account_type -> record_type` and is
  recognized from account-, statement-, invoice-, or ledger-shaped evidence.
- This situation has different recognition evidence: a named passenger/guest/renter, a booking or
  ticket identifier, and a route, stay, or pickup/drop-off structure. Those signals are not a file
  extension and are not ordinary Finance-account evidence.
- The recommended dimensions differ: `record_type -> institution`. `account_type` is deliberately
  absent because a booking is not proof of a financial account; `tax_year` is absent because travel
  and purchase dates are not tax years.
- Privacy differs from a generic account template in what must be redacted: booking records expose
  future schedules, routes, properties, passenger/guest names, and reservation identifiers.
- The row also differs from `finance.receipts-expenses`: an ordinary receipt is anchored by a
  seller/order/line-item/total structure; this row is anchored by journey or stay slots. Their
  genuine boundary is represented by a reciprocal `collides_with` edge.

The template remains intentionally shallow. The ideal first dimension is the accepted trip, but
Finance cannot legalize a trip field. Saving the id by writing a private `trip` field would fail the
node test more seriously than refusing it; the recorded compromise is a useful placeholder plus an
open schema decision.

## Bottom-up file survey

The JSON contains fifteen full observation/fact fixtures. The set covers:

- a labelled airline e-ticket itinerary receipt (`text_document`);
- a structured `.pkpass` boarding pass inspected as an `archive`;
- a labelled hotel confirmation email (`email`);
- a rail e-ticket (`text_document`);
- a rental-car confirmation with embedded reservation data (`text_document`);
- a lodging calendar event (`calendar`) whose source type is never sufficient alone;
- OCR of a boarding pass shown in an airline app (`ocr`);
- a camera photograph of a paper boarding pass (`image`), legally Finance and Photos on disjoint
  evidence;
- the sparse Gate B12 capture (`ocr`), which gets no Finance fact and may join a neighborhood
  without copying a trip;
- a mixed travel-document archive containing bookings and a passport scan (`archive`), legally
  also Identity and protected;
- a conference-rate hotel reservation, collision fixture for Research;
- interview travel, collision fixture for Career;
- exchange-period travel, collision fixture for Study Abroad;
- a restaurant reservation confirmation, the tempting false file for the words reservation and
  confirmation;
- an unlabelled prose host email, which remains unresolved or LLM-bounded rather than being forced.

Each fixture separates raw observations from legal facts. No `facts_legal` value is a path, and
every sparse or group-supported file explicitly refuses neighbor fact propagation.

## Fields and field proposals

`fields` is empty because this is a template. It references the landed Finance schema rather than
copying its field rows.

Only two inherited fields are normally useful here:

- `institution` is the record issuer in its labelled role. An operating carrier, hotel property,
  booking broker, or seller mentioned elsewhere is not automatically the issuer.
- `record_type` holds values such as boarding pass, lodging reservation, rail e-ticket, itinerary
  receipt, or schedule-change notice.

`account_type` stays unknown unless a separate Finance-account record says it directly. Loyalty
program membership is not a financial account type. `tax_year` stays unknown unless a record has an
explicit tax-year slot; travel, purchase, departure, and stay dates are not substitutes.

No canonical field is proposed:

- `trip` was rejected as a new key because canonical `event` already aliases trip and is described
  as an occasion or trip a capture or record belongs to. The actual problem is that Finance does
  not reference that key; that is NJ-R1a-2's schema-set decision, not a license to mint a synonym.
- booking reference, ticket number, PNR, Wallet serial, and calendar `UID` remain structured
  observations and group anchors. They are valuable for identity/version/group joins, but the
  design does not authorize a new destination field for them.
- passenger/guest/renter names remain sensitive evidence or search-side data. This template does
  not duplicate Finance's pending `account_holder` proposal and never makes a person's name a
  folder dimension.
- route, gate, seat, room, check-in, check-out, pickup, and drop-off values remain observations
  unless a future Travel schema legally defines where they land. They must not be squeezed into
  `account_type`, `tax_year`, or `institution`.

The `proposed_context_terms` list is explicitly proposal provenance. It extends the named travel
situation and is not presented as a term list from `00`; R2/R6, not this row, own detector content
and patterns.

## Recognition and reliability

The deterministic cases use labelled or machine-structured slots. A structured provider/issuer,
reservation identifier, traveler role, and route/stay/rental structure can support direct or
validated Finance facts. Filename, free text, OCR, and unlabelled positions remain possible until a
rule or bounded, evidence-citing LLM path validates them.

The LLM cases are bounded to issuer-role interpretation, unusual prose, multilingual vouchers,
capture-vs-record ambiguity, cancellation/rebooking references, and trip-group coherence. The LLM
may not create a trip field, identify a trip from a gate, or copy fields from a rich booking onto a
sparse reminder.

No regex, score, margin, group-size rule, or numeric threshold is authored here.

## Edges

`collides_with` contains reciprocal template-to-template edges already authored toward this row:

- `finance.receipts-expenses`: transaction total/order structure versus passenger/route/stay
  structure;
- `travel.trip-photos`: an image of a transactional record versus a scene capture, while Finance
  and Photos may still co-activate on disjoint evidence;
- `academic.study-abroad`: booking structure versus enrollment/exchange structure;
- `research.conference-presentation`: reservation structure versus research deliverable/session
  structure;
- `career.recruiting`: booking structure versus employer/role/recruiting-process structure.

All five targets exist on the roster and are `kind: template`, matching the same-kind edge rule.

`also_holds_with` is empty by contract: CONNECTION restricts that edge to schema-to-schema pairs.
The real co-activations are still represented in `file_examples[].also_schema`: photographed or
screen-captured boarding passes can be Finance plus Photos, and a mixed archive can be Finance plus
Identity. The landed Finance schema owns the relevant schema-level relationships.

`role_split` is empty. Issuer versus carrier/property/broker and traveler versus issuer are real
roles, but there is no canonical field pair for this template to reference; inventing one here
would be the private-field failure mode.

`parent_id` remains `null` because R1b never authors browse shelving. `shares_field` is not
serialized because it is derived-only.

## Neighbors considered that did not get an edge

- `photos` and `identity` were required considerations, but they are schemas and this row is a
  template, so a direct `collides_with` edge would violate the same-kind rule. Co-activation and
  privacy are handled by the Finance schema and the per-file `also_schema` fixtures.
- `photos.screenshot-captures` deliberately gets no edge. Its landed research already records the
  sparse boarding-gate case as a residual decision rather than a discriminable travel template.
  Rich OCR can activate Finance on its own evidence while Photos retains capture facts; sparse OCR
  goes to Temporary Screenshots without a trip.
- `identity.immigration-visa` gets no edge. A passport or visa authorizes identity/status, while a
  booking records transport or lodging. A passport member inside an archive activates Identity on
  its own evidence; a passenger name or booking reference never does.
- `finance.insurance-personal` gets no edge. Travel insurance may sit beside a booking, but policy,
  coverage, premium, and claim structure is not confusable with itinerary/stay structure.
- `medical` gets no edge. Vaccination or appointment material may be needed for travel, but that is
  purpose/group context, not booking evidence.

## Residuals and privacy

`Receipts and Confirmations` is the primary fallthrough for recognized but isolated transactional
travel records or for records whose trip grouping never lands. `Temporary Screenshots` is the
fallthrough for Gate B12-style captures that remain time-sensitive and sparse. Per-file fixtures
also use `One-Off Images`, `Protected Records`, `Independent Records`, or `Review Later` when the
file's actual residual reason demands it.

Sensitivity is `potentially_sensitive`, not a handling class. Passenger and guest names,
reservation identifiers, exact future schedules, routes, properties, and OCR are redaction/local
processing concerns. D2 makes P7's `(file_id, content_hash)` `ClassificationRecord` authoritative;
this node does not publish a second sensitivity vocabulary or classification writer.

## Contract precedence notes

- CONNECTION wins over the dispatch output sketch on `also_holds_with`: a template authors none.
- Activation returns the `finance` schema, never this template id. Template selection is later.
- The trip group is not an activation input and never propagates facts.
- `parent_id` is browse-only and intentionally null; no folder dimension or schema is inherited.
- All source types use the closed P5 vocabulary; extensions are never sufficient.
- The two attributed `00` quotations in the JSON were checked verbatim before completion.

## NEEDS-JOSEPH — this node only

**NJ-R1a-2: does Travel deserve its own small schema?** The canonical list already has plausible
keys (`event`, `location`, `record_type`, `capture_year`), but neither Photos nor Finance can express
trip then record type for the full travel-record situation. The current v1 compromise is the two
templates (`travel.trip-photos` and this row), an accepted P9 trip group or user branch, and
Receipts and Confirmations fallthrough. This research does not silently resolve the schema-set
decision, add `event` to Finance, or mint `trip`.

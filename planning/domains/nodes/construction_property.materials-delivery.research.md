# construction_property.materials-delivery — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

`00-database-agent-product-design.md` (quotations machine-verified verbatim), `ALIGNMENT.md`,
`_CONTRACT.md`, `CONNECTION.md`, `roster.json`, `canonical_fields.json`, `DECISION-BRIEF.md`
(J-IND, D1, PR-6), `ROSTER.md` §4 → `13-trades-property-logistics.json` (line 916),
`src/evidence_shape/vocabulary.py` for `SOURCE_TYPES`. Reference standard: the landed
`business_operations.*` files. Neighbours read first: `business_operations.procurement-sourcing`
(purchase orders), `finance.household-property`, `photos.camera-events` (the EXIF fixtures).

## What it is for, and what it holds

Physical arrival. Delivery and advice notes, signed proofs of delivery, goods-received sheets,
shortage and damage annotations, purchase orders and call-offs with a site delivery address,
materials take-offs, batch and conformity certificates that travelled with a load, waste transfer
notes running the other way, and phone photographs of all of the above.

## Node test — passes, on the deliver-to/invoice-to split

1. **Signals differ:** the structural fingerprint is a **deliver-to address that is not the
   invoice-to address**, plus ordered-versus-delivered quantity columns, plus a received-by
   signature. No other row in this family has it. The second fingerprint is stranger and more
   useful: a **correction made at the moment of handover** — a struck-through quantity, "2 pallets
   short", "received unchecked". A document that carries a contemporaneous annotation is its own
   evidence class.
2. **Dimensions differ:** site → order → delivery date, with supplier deliberately *below* site.
3. **Privacy differs:** signatures, receiver names and — on phone photos and carrier PODs — GPS.

## Legacy id absorbed (ROSTER.md §4)

`cons.materials-delivery` (ROW), 1:1.

## The hardest thing about this row

**One document type, three claimants.** A purchase order is authored into
`business_operations.procurement-sourcing` (which carries its own open question about it), is the
front half of this row's situation, and is a bookkeeping input. The row keeps orders because a site
compares the order against the note or keeps neither — but it says so as an `open_question` and as
a reciprocal collision rather than quietly annexing them.

**The second hardest: the photograph.** `IMG_1148.HEIC` of a delivery note is simultaneously a
capture-metadata file (the `photos` schema's evidence class), delivery evidence, and — if it shows
the pallet rather than the paper — `construction_property.progress-photos`. It is authored as a
fixture with `One-Off Images` as its fallthrough, and the collision with `progress-photos` is
written from this side in the same terms that row should use.

## Files considered and rejected

- **`Jewson statement - March.pdf`** — kept as the bookkeeping collision fixture; a statement quoting
  note numbers is still accounting.
- **`DoP - steel batch 8841.pdf`** — kept because it is an *honest shared file*, not a mistake: both
  this row and `construction_property.compliance-certificate` should retrieve it, and the collision
  says so rather than pretending one wins.
- **A supplier's PDF price list** — rejected: no arrival, no receipt; a catalogue.
- **A skip-hire booking confirmation** — rejected: a booking, and `Receipts and Confirmations` handles
  it without a fixture.
- **A merchant loyalty/account-application form** — rejected as neighbour material (bookkeeping).

## proposed_fields

**None.** PR-6 forbids field rows on this schema. Candidate dimensions (site/job, order, delivery
date) are prose in `template.why` for R1c.

## Neighbours considered that did NOT get an edge

- **`manufacturing.*`** — goods-in and inspection at a factory is the same act in a different world;
  the `logistics.shipment` and `retail_hospitality.supplier-order` edges already carry the shape at
  gist depth.
- **`construction_property.site-diary`** — deliveries are logged in the diary, but the diary owns the
  narrative of a day and this row owns the note; the seam is real but thin, and the diary row's own
  agent is better placed to author it.
- **`finance.receipts-expenses`** — a trade-counter till receipt for materials bought personally is
  genuinely that row's; not doubled here.

## NEEDS-JOSEPH

- **NJ-CP-5 · Who owns the purchase order?** Three rows have a claim:
  `business_operations.procurement-sourcing` (a competitively sourced PO), this row (a site call-off
  against a materials schedule), and `finance.small-business-bookkeeping` (the commitment behind the
  invoice). Stated reciprocally: this row's collision on `procurement-sourcing` names the
  discriminator from this side, and that row already carries the mirrored question as its own
  `open_question`. Joseph's, because it turns on how the user's business buys, not on the documents.
- **NJ-CP-6 · The photographed document.** Whether a phone photo of a delivery note is handled as a
  document (this row), as a capture (`photos`), or as both, is `00`'s one-file-many-facts question in
  its most literal form; the fixture records both readings rather than choosing.

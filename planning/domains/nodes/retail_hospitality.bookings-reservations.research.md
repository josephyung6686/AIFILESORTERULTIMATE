# Research memo — `retail_hospitality.bookings-reservations`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/retail_hospitality.bookings-reservations.json`
Roster row: template on the fieldless `retail_hospitality` schema, `parent_id: null`, placeholder launch

## Result

**Accept.** The row passes decisively on **detection** and on **privacy**. It passes only **narrowly** on **dimensions**, where its recommended order is a specialisation of the schema default rather than a dramatic reorder. That thinness is written as `NJ-BR-1` rather than smoothed. A refusal was argued seriously — the schema already names capacity-against-dated-demand, and the customer-side confirmation is a residual — and defeated on operator-side apparatus, status/requirements structure, and the travel mutex.

## The charge — the strongest case that this row should not exist

Six prosecutions. The fourth was the dangerous one.

**1. A work-type value on its own schema.** The schema's `work_types[]` already contains *"booking record - reservation, confirmation, deposit, requirements and dietary note, cancellation or no-show record."* *Defeated by the node test proper:* `work_types` is the family's browse vocabulary, not a claim that each entry is already a situation. If enum membership defeated this row it would defeat all fourteen siblings and leave the schema childless, which is not the ratified shape. The test is whether detection, dimensions or privacy differ from the default — answered below.

**2. A document-type word — `booking`, `reservation`, `confirmation`.** Not invented here: the schema's own `never_alone` list forbids document-type words as sole proof and says a row resting on one is the default wearing a name. *Defeated,* and the defeat is this node's first `never_alone` cluster: those tokens also name travel vouchers, medical appointments, meeting invites, software holds, and Residual Receipts and Confirmations material. `Booking.pdf` is nothing. Nothing in recognition fires on the word; it fires on capacity-against-dated-demand with a status slot, a population diary, or a reservation-lifecycle chain.

**3. A lifecycle stage of `retail_hospitality.event-production`.** Booking before the day, production on the day — "before" is a stage in the plainest sense. *Defeated:* a Tuesday covers diary, a hotel PMS night export and a spa waitlist are bookings with no event-production apparatus anywhere; a run sheet can exist for a free community festival that was never "reserved" as sellable capacity. Neither necessary nor sufficient. The reciprocal collision on `Ashcroft 06.06.26 - confirmation and deposit.pdf` states both sides: this row owns reservation of the date; event-production owns production of the day.

**4. A duplicate of the schema's default template — specifically of CAPACITY-AGAINST-DATED-DEMAND.** *This one partly succeeded and is the honest strain.* The schema already lists that structure in its recognition union, and its default prose already puts "booking" inside the trading-occasion level. A row that only re-labels that paragraph fails the node test.

*Survives on three positive differences, not on subtraction.* (a) **Operator-side determination** is load-bearing here in a way it is not for stocktake or catalogue: the same PDF bytes are either this row or travel / Receipts and Confirmations depending on holder role and apparatus. (b) **Status-plus-requirements apparatus** — provisional / confirmed / cancelled / no-show, dietary, accessibility, cot, late checkout — is operational structure a bare "party of four on 14 Mar" voucher lacks. (c) **Population diary vs single transaction** — a covers book or PMS export is not the same organisational situation as one confirmation email. The schema's recognition union names what its children collectively recognise; it is not already doing this template's work. Honest verdict: dimensions are thin (`NJ-BR-1`); detection and privacy carry the node.

**5. Defined only by an absence — "not the customer's confirmation."** *Defeated:* the positive fixtures are operator populations, status grids, requirements blocks and lifecycle chains. The customer confirmation is the collision fixture that proves the boundary, not the definition of the row.

**6. A duplicate of `travel.bookings-confirmations`.** *Defeated on schema and on fixture:* that row is a finance-schema template for the traveller's transactional voucher (issuer institution, record_type). This row is a retail_hospitality template for the operator's capacity diary. Same filename, opposite holder role — mutex, not identity.

**Verdict: `refuse_node: false`, dimensional leg flagged contested as `NJ-BR-1`.**

## The node test, argued in full

**Leg 1 — detection differs from the schema default. PASSES.** Signals specialised beyond the family union:

- capacity-against-dated-demand **with a reservation-status slot**;
- requirements / special-requests co-located with the demand;
- population diary or PMS / covers export (many occasions, one site, one period);
- reservation-lifecycle chain sharing one booking reference;
- waitlist / reallocation against an explicit capacity cap;
- deposit or guarantee instrument whose slots name the reservation, not merely a merchant and an amount.

None of tender-reconciliation, count-against-book, permission-to-trade, daily-signed-check, ingredient-and-yield, order-cycle, catalogue-and-price, or guest-voice produces these. Event-production's minute-keyed delivery is adjacent and deliberately collided, not identical.

**Leg 2 — dimensions differ. PASSES NARROWLY; CONTESTED.** Recommendation held as prose because PR-6 leaves the schema fieldless: **site** (only where the corpus spans more than one) → **the booking as trading_occasion** → **booking record function** (confirmation, deposit, amendment, cancellation, no-show, waitlist). Not time-first — “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” — and the time-first licence is capture media only: “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.” Absolute prohibitions: guest name never a dimension; booking-reference forests of one-child branches rejected under the tiny-folders warning. The strain is that this order *is* the family default with a specialised trailing function — thinner than guest-feedback's channel substitution. Recorded as `NJ-BR-1`.

**Leg 3 — privacy differs. PASSES DECISIVELY.** Stocktake and catalogue siblings are operationally sensitive; this row's ordinary activating artefact *is* third-party personal data. Population exports route toward Protected Records when ungrouped; guest names are never destination-eligible; cloud prompts are barred by default — “Protected material should not be included in cloud-model prompts by default, should not display raw content in general group summaries, and should not be moved automatically without a user policy that explicitly permits it.” That posture is stricter than the family's generic potentially_sensitive inheritance and is a real template difference.

## Binding material read

Stamped assignment via `make_prompt.py retail_hospitality.bookings-reservations`. Read RESEARCH-BRIEF, CONNECTION node test, `_CONTRACT` shape by idiom from landed siblings, canonical field ownership (no mint), SOURCE_TYPES vocabulary, roster neighbours, and **only** `retail_hospitality.json` as the schema anchor (not its memo). Calibrated depth against `legal.practice-matter-file.research.md` (~13 KB target). Did not imitate the oversized business_operations / clinical_practice / construction_property memos.

Design consequences that bind:

- D1 / PR-6: `fields: []`, `proposed_fields: []`, empty `dimension_order`.
- J-IND: placeholder launch, full J-DEPTH research.
- `also_holds_with` is schema ↔ schema only — left empty on this template; co-activation with finance / photos is recorded on file examples via `also_schema`.
- Activation ≠ grouping; residual routing is separate; no fabricated `00` quotations (every span grepped before write).

## External artifact research

Used only to establish that the proposed shapes occur in real operator practice — not to import rules.

- Property-management and restaurant-diary practice: reservation number, arrival/departure or service time, status, rate or covers, special requests — ordinary PMS / diary export columns.
- Channel / OTA operator downloads: population exports keyed to a property and a date window, distinct from a guest's single voucher PDF.
- Deposit / guarantee instruments: hold pending payment against a booking reference — common before large covers or peak dates.
- Waitlist sheets: ranked party size against a covers cap — capacity constraint made explicit.

No retention period, consumer-cancellation statute, PCI rule, or accessibility-law conclusion is derived.

## Bottom-up file set

The JSON carries full observations, prohibited conclusions, grouping flags and residuals. Why each fixture exists:

1. `Covers diary - dinner 14 Mar 2026 - The Bell.xlsx` — operator population with status and dietary columns; primary positive.
2. `PMS reservations export - Harbour Hotel - 2026-03-14.csv` — hotel-shaped population; discriminates travel traveler vouchers.
3. `Confirmation - booking 88231 - 8 covers - 14 Mar 19:30.pdf` — operator confirmation with requirements and status.
4. `Deposit request - Ashcroft wedding 06.06.26 - booking 4401.pdf` — deposit bound to reservation; also_schema finance; event-production seam.
5. `No-shows and cancellations - week 12 2026.xlsx` — lifecycle close; not POS.
6. `Waitlist - Saturday dinner 14 Mar.xlsx` — capacity-cap structure.
7. `RE Dietary note - booking 88231.eml` — requirements member of a packet; not clinical.
8. `Harbour Hotel - arrivals 14 Mar.ics` — calendar content that is still capacity-status, not a meeting.
9. `Night audit reservations packet - 14 Mar 2026.zip` — archive manifest only.
10. `Screenshot 2026-03-14 at 19.02 - OpenTable diary.png` — OCR diary; also_schema photos.
11. `Booking confirmation - Le Petit Jardin 14 Mar.pdf` — **primary collision fixture** (schema anchor's customer-side false friend).
12. `Appointments_2026-03.csv` — clinical collision fixture.
13. `Ashcroft 06.06.26 - confirmation and deposit.pdf` — reciprocal fixture with event-production.
14. `Q3 all-hands - agenda and timings.docx` — meeting-record false friend.
15. `Guest reservations export - password protected.zip` — unreadable; filename manufactures nothing.

## Files considered and rejected

- A live PMS database or cloud reservations console — a source system, not a file node. Bounded exports with readable manifests are in scope; live connectors are not.
- A guest's Apple Wallet hotel pass or boarding pass — travel.bookings-confirmations / finance territory.
- A Banqueting Event Order / function sheet with supplier call times — event-production (and possibly catering-contract); this row keeps only the hold/deposit half.
- A till Z-read that mentions covers sold — pos-reporting.
- A platform review mentioning "our booking" — guest-feedback.
- A supplier delivery booking / timeslot for goods-in — logistics or supplier-order.
- Contact exports that merely list diners — names without capacity-status structure do not activate.
- Blank booking-form templates and vendor sample PDFs — purpose is training or sales, not a live diary.
- Medical appointment CSVs — clinical_practice, even when columns look like a diary.

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `template.dimension_order: []`, `time_first: false` — intentional under PR-6.

Candidates rejected rather than minted:

- `guest`, `diner`, `party_lead`, `covers`, `booking_status`, `reservation_id` — either non-canonical, destination-hostile (guest), or values rather than organising facts.
- `channel` / `booking_source` — guest-feedback already proposed `channel` for review platforms. This pass **reuses nothing by minting a synonym**; if OTA vs phone vs walk-in must be a dimension, R1c should widen that existing proposal (`NJ-BR-2`).
- Schema proposals `site`, `trading_occasion`, `record_period` — referenced in prose recommendation only; not re-declared as field rows on this template.

## Recognition boundary

Strong evidence combines operator role with structure: population diary or PMS export; confirmation with status and requirements retained in the house cycle; deposit/guarantee keyed to a booking reference and occasion; cancellation/no-show log; waitlist against a covers cap; lifecycle chain sharing one reference.

Weak evidence stays weak: the words booking/reservation/confirmation; a venue trade name; a guest name; a bare reference-shaped token; a date; a party size; money; file kind; a Downloads session beside boarding passes.

Holder role is essential. Identical confirmation bytes may be the operator's record, the guest's voucher, a travel lodging confirmation, or a meeting-room hold. Where side is unsettled, abstain — “A model that cannot cite sufficient evidence must return unknown.” — and prefer Review Later over a wrong activation.

## Edges and deliberate non-edges

**Mutex collisions authored** (SAME FIXTURE BOTH SIDES on every entry):

- `travel.bookings-confirmations` — `Booking confirmation - Le Petit Jardin 14 Mar.pdf`
- `retail_hospitality.event-production` — `Ashcroft 06.06.26 - confirmation and deposit.pdf` (reciprocal)
- `clinical_practice` — `Appointments_2026-03.csv`
- `business_operations.meeting-record` — `Q3 all-hands - agenda and timings.docx`
- `finance` — deposit PDF when money slots appear without capacity-status apparatus (and co-activation on disjoint evidence noted separately)
- `retail_hospitality.pos-reporting` — covers number appearing in both a diary and an end-of-day pack

**`also_holds_with`: []** — schema ↔ schema only; this template does not author schema coactivation. Finance and photos coactivation appear as `also_schema` on deposit and screenshot fixtures.

**Deliberate non-edges:**

- `retail_hospitality.catering-contract` — roster neighbour, files not yet landed in this pass's read set for a same-fixture signal; progression rule deferred to `NJ-BR-3` rather than inventing an edge against an unread neighbour body.
- `retail_hospitality.guest-feedback` — a complaint that cites a booking reference may group with the booking packet without mutex; not same-evidence confusion.
- `logistics` — delivery timeslots are movement records, not guest capacity.
- `hr` — staff rotas against forecast covers are store-operations / hr seams, not this row's centre.
- Bare `business_operations` schema — too coarse; meeting-record carries the concrete fixture.

## Residuals

Receipts and Confirmations (customer-side isolated booking records — named by `00`), Protected Records (ungrouped guest exports), Review Later (unresolved side), Independent Records (narrow durable one-offs), Temporary Screenshots (single diary tile), Unsupported or Encrypted (password-protected guest dump).

## Neighbours considered that did not get an edge

`business_operations` (schema-level already owned by the anchor), `logistics`, `hr`, `retail_hospitality.store-operations`, `retail_hospitality.catering-contract` (unread body; see NJ-BR-3), `retail_hospitality.guest-feedback`, `creative` — examined for theft risk; no same-evidence mutex requiring an entry on this row.

## NEEDS-JOSEPH

- **NJ-BR-1 — dimensional thinness.** Keep on detection+privacy; require a second dimension (source/channel); or refuse and fold into schema default.
- **NJ-BR-2 — booking source key.** Widen guest-feedback's `channel`, leave unkeyed, or (rejected here) mint a synonym.
- **NJ-BR-3 — hold → contract → run sheet progression.** One rule shared with catering-contract and event-production once those bodies are aligned at R1c.
- **NJ-BR-4 — dual-role B&B corpora.** Operator who is also sometimes a guest on the same machine; Review Later vs force population evidence vs Joseph ruling.

## Self-verification

- Output paths match assignment; only these two files written; no commit.
- JSON parses; `fields: []`; `also_holds_with: []`; every `collides_with` entry is a `{domain, signal}` object with SAME FIXTURE BOTH SIDES.
- Edge ids checked against roster.
- Every `00` quotation in both files grepped verbatim before write.
- Memo carries `Depth: J-DEPTH`.

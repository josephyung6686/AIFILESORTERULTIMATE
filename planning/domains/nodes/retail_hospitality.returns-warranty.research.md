# Research memo — `retail_hospitality.returns-warranty`

Depth: J-DEPTH
Date: 2026-08-27
Kind: template on the fieldless `retail_hospitality` schema · `parent_id: null` · `launch: placeholder`
Output: `planning/domains/nodes/retail_hospitality.returns-warranty.json`

## Result

**Accept, but narrowly and on one argument only.** This row survives because its difference from its
schema's default template is at the **occasion** level, not the function level. If the difference had
been at the function level it would have been a `work_type` value and I would have refused it — and
the schema anchor itself lists `"returns and claims record - return authorisation, refund decision,
warranty claim, chargeback file"` in `work_types[]`, which is the most damaging single fact against
this row's existence. The rest of this memo is the attempt to defeat that fact.

## Sources actually read

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (in full).
- The stamped assignment from `make_prompt.py retail_hospitality.returns-warranty`.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — one landed launch row, for depth
  calibration only.
- `planning/domains/nodes/retail_hospitality.json` — my schema anchor, in full. This is the document
  my node test is measured against.
- `planning/00-database-agent-product-design.md` — by targeted `grep -c` verification of every span I
  quote. Ten spans checked, ten returned exactly one match. No span in either output file is
  paraphrased inside quote marks.
- Four landed neighbour nodes, read only at the `collides_with` entries that name me:
  `manufacturing.warranty-claim.json`, `retail_hospitality.guest-feedback.json`,
  `retail_hospitality.ecommerce-ops.json`, `logistics.json`.
- `planning/domains/roster.json` — every neighbour id in my edges confirmed present as a
  `domain_id`. `retail_hospitality.supplier-order` (singular, not `supplier-ordering`) and
  `retail_hospitality.stocktake` were checked by name because I nearly wrote them wrong.

## THE CHARGE — the strongest case that this row should not exist

I put six charges. Five are serious.

**1. It is a work_type value of its own schema's default template.** The schema anchor's `work_types[]`
names this row almost word for word. Its `never_alone` list says a document-type word is *"a value of
a function dimension, and a row resting on one is the schema's default template wearing a name."*
Return, refund, credit, warranty and claim are all such words. On this charge alone the row should
die.

**2. It is a lifecycle stage.** A return is the last stage of an order — the sale run backwards. The
schema's default already puts the ORDER CYCLE at the occasion level. Returns would then be the
cycle's tail, and a tail is not a node.

**3. It is defined by an absence.** A return is a sale that did not stick. Rows defined by the absence
of something are exactly what the brief warns against.

**4. It is a duplicate of neighbours that have already landed.** Four of them: `manufacturing.warranty-claim`
takes warranty, `retail_hospitality.guest-feedback` takes the complaint, `retail_hospitality.ecommerce-ops`
takes the refund-as-order-state, `logistics` takes the return leg's movement. If each takes its half,
is there a remainder at all?

**5. It is three rows wearing one name** — consumer returns, warranty claims, payment disputes — and a
row that is really three is not a row.

**6.** (Weak, listed for completeness.) It is a medium or a format. It is not: the fixtures span
spreadsheet, text_document, email, image, ocr and archive.

## Defeating the charge

### Against charge 1 and 2 — the occasion, not the function

The schema anchor's default template is held as prose because PR-6 leaves the schema fieldless. Its
exact words: the TRADING UNIT where the corpus spans more than one, then the TRADING OCCASION —
*"the session, count, order cycle, booking, function or licensed premises the material belongs to"* —
then the OPERATIONAL RECORD FUNCTION.

That sentence enumerates five occasion shapes. **A return case is none of them**, and it differs from
all five in the same four ways:

- **It is opened by the customer.** Every other occasion in this family is operator-initiated: the
  operator opens a till session, calls a count, raises a purchase order, takes a booking, applies for
  a licence. A return case begins when someone outside the business asserts a right.
- **It carries an authorisation identity of its own** — an RMA or claim reference that is issued
  separately from, and outlives, the sale reference. In `RMA register 2026-Q1 - Camden.xlsx` the
  RMA ref column and the Order ref column are two different columns.
- **Its centre is an adjudication.** A booking has a status (confirmed, cancelled, no-show); a count
  has a variance. Neither *decides a right*. This occasion has approved / rejected / partial, an
  approver, and an entitlement basis it was decided under.
- **It settles two ledgers with one decision.** The parent schema is built on pairings — *counted
  reality against recorded belief*, *finite capacity against dated demand*. This row is a third
  pairing the anchor does not name: **an asserted right against a granted remedy**, resolving money
  and stock together.

The decisive evidence is the **orderless case**. A warranty claim on a gift, on transferred goods, or
on a unit bought through a different channel has no order to be filed under. Under the default
template that material has no home at all. In my register fixture I deliberately wrote the Order ref
column with empty cells and marked in `must_not_conclude` that those blanks are not a data-quality
defect — they are this row's strongest evidence. A tail cannot exist without its body; this occasion
routinely does. Charges 1 and 2 fail.

### Against charge 3 — it is defined by a presence

The row is not "sales that failed". It is the presence of an entitlement-against-disposition
structure. A change-of-mind return with a full refund is an entirely successful transaction for
everyone involved and is still squarely this row. Charge 3 fails.

### Against charge 4 — the remainder is what four researchers each declined to take

This is the charge I expected to lose and did not, because the neighbours argued my side for me.
Each landed row states its boundary in words that leave a coherent, non-empty remainder, and — this
is the part that matters — **each names the same discriminator independently**: a return-authorisation
identity plus an entitlement plus a disposition.

- `manufacturing.warranty-claim` on its own node: *"RECIPROCAL: retail returns must not claim a
  failure-analysis dossier because a refund was issued, and this row must not claim a change-of-mind
  return because the policy document says warranty."* It concedes the merchant transaction to me
  explicitly, and it resolves the merchant-is-also-manufacturer case by evidence grammar rather than
  organisation identity. I follow that ruling rather than restate it differently.
- `retail_hospitality.guest-feedback`: *"RETAIL_HOSPITALITY.GUEST-FEEDBACK MUST NOT TAKE an RA
  register, a refunds ledger or a warranty claim file"*.
- `retail_hospitality.ecommerce-ops`: *"this row MUST NOT take an RMA file because the sale was
  online"*.
- `logistics`: *"`retail_hospitality.returns-warranty` likewise keeps the customer's return
  entitlement; this schema keeps only the return leg's movement."*

Four independent researchers drawing the same line around the same remainder is the strongest
available evidence that the remainder is a real object and not a gap I invented to save an id. All
four are written into `collides_with` in both directions, naming the same fixture on each side.

### Against charge 5 — one structure, tested

Consumer return, warranty claim and chargeback all instantiate: right asserted → condition assessed →
disposition decided → money and stock settled together. The chargeback's counterparty is an acquirer
rather than a customer and its "right" is scheme rules rather than statute or policy, but the shape
holds. I do not think this is certain, and I have **not** smoothed it: it is NJ-RW-3, with the
alternative spelled out (the warranty leg collapsing into `manufacturing.warranty-claim`).

### The three legs of the node test

Applying CONNECTION §2 — a template exists only where its detection signals, recommended dimensions,
or privacy rules differ from its schema's default.

**Leg 1 — detection signals: PASS, and this is the cleanest leg.** The schema anchor lists ten
deterministic structures: tender-and-drawer reconciliation, count-against-book,
capacity-against-dated-demand, permission-to-trade, daily-signed-check, ingredient-and-yield,
order-cycle, guest-voice, catalogue-and-price, plus folder/email/archive clues. **None is
entitlement-against-disposition.** The nearest is order-cycle, which does include "a credit note" —
but that is a *supplier* credit note, money flowing *to* the operator *from* a supplier against an
inbound shortage. My credit note flows the other way, against outbound goods, to a buyer. Opposite
direction, different party, different entitlement. That near-miss is why
`retail_hospitality.supplier-order` gets an edge and why `Credit note CN-4471 - Harlow Foods.pdf` is
in my file examples as a second collision fixture.

**Leg 2 — recommended dimensions: PASS, at the occasion level.** Argued above. `dimension_order` is
`[]` by contract (a dimension may only branch on a field its schema declares, and this schema
declares none), so the difference lives in `template.why` as prose, exactly as the anchor's own
default does. Not time-first: *"For document and record domains, project, function, or subject
usually comes before time because putting year first scatters related work across calendar folders."*
The return date identifies the case; it does not root the tree.

**Leg 3 — privacy rules: PASS, with a delta I can name rather than a restatement.** The parent's
posture rests on the *volume* of ordinary third-party data. This row adds three things no sibling
template produces: it joins a named consumer to a **payment instrument and a dispute** (cardholder
correspondence, evidence uploads often photographed inside the customer's home); it produces
**suspicion records about customers** — repeat-returner lists with free-text characterisations, a
category the parent names for *staff* in till exception reports but not for the public; and it holds
**proof-of-purchase evidence belonging to somebody else**. All three are in `sensitivity_why`.

Three legs pass; two of them by a clear margin. The row stands.

## Files considered and rejected

The tempting false positives, and why each is not my evidence:

1. **`Returns and refunds policy v3 - in-store and online.docx`** — the nearest miss of all, and the
   one I nearly admitted. It is the *entitlement basis a case cites*, not a case: second person,
   general windows and exclusions, a document-control block, and no unit, customer, reference or
   decision anywhere. Governance material. *"Topic answers what a file is about, while purpose
   answers what the file was for."* It is in `file_examples` marked "THIS ROW DOES NOT ACTIVATE" and
   drives the `business_operations` edge. Its grouping consequence is unresolved and is NJ-RW-5.
2. **`Credit note CN-4471 - Harlow Foods.pdf`** — a supplier credit. Looks like a refund; is
   inbound-goods. Discriminated by which party is owed. `retail_hospitality.supplier-order`'s.
3. **A warranty certificate with no claim against it** — an entitlement waiting to be used. Durable,
   standalone, no case: Independent Records. It is in `never_alone` as the warranty-term test's
   negative case.
4. **A refunds column inside a Z-read or an end-of-day report** — the parent's own POS structure.
   Refunds counted as a session exception, not adjudicated as cases. `retail_hospitality.pos-reporting`.
5. **A goodwill credit issued to close a complaint with no goods coming back** — same money movement,
   no entitlement and no stock consequence. `retail_hospitality.guest-feedback`'s.
6. **A photograph of a broken item** — image evidence until a case structure claims it. Named in
   `never_alone` as the reason-word rule.
7. **A shrinkage line in a stock count** — a variance with an unknown cause. My write-offs carry a
   known cause and a case reference. Drives the `retail_hospitality.stocktake` edge.
8. **A reverse-logistics carrier rate card and a proof-of-delivery file** — movement, not
   entitlement. `logistics`', by that row's own words.
9. **A teardown or failure-analysis dossier** — `manufacturing.warranty-claim`'s, by its own words,
   even where I issued the refund that started it.

## The collision fixture

**`Return label - 112-4457889-3325061.pdf`.** It carries an RMA-shaped authorisation reference, a
barcode, a reason code reading "no longer needed", one item, and a returns-policy paragraph. On a
filename and a first page it is indistinguishable from my evidence.

It is not mine. **What discriminates it: there is no adjudication anywhere in it** — no decision, no
approver, no condition assessment, and above all no stock consequence. It instructs a *customer* what
to do; my documents record what an *operator decided*. This is the parent schema's central
determination — the operator's side only — in its sharpest form, because returns is the one place in
the whole family where both copies legitimately carry the same class of reference. It falls to
Receipts and Confirmations, and 00 names its exact material: *"Receipts and Confirmations may hold
isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event
tickets, and similar transactional documents."*

`Credit note CN-4471` serves as a second, lower-stakes collision fixture on the supplier side.

## Reciprocal boundaries

Eight `collides_with` entries, every one an object carrying the SAME FIXTURE BOTH SIDES construction
and a named discriminating evidence item. Four are *agreed* — the neighbour authored its half first
and I matched its wording rather than inventing a second version of the seam:
`retail_hospitality.guest-feedback` (fixture: the split complaint thread; discriminator: the return
authorisation and its stock movement), `manufacturing.warranty-claim` (fixture: `Order 88421 return
request - defective.pdf`; discriminator: whether a failure investigation exists),
`retail_hospitality.ecommerce-ops` (fixture: a refund line in the period order export; discriminator:
whether a return-authorisation identity exists separately from the order identity), and `logistics`
(fixture: the return leg's consignment paperwork; discriminator: consignment versus authorisation).

Four are authored one-way here and R1c owes the reciprocal: `retail_hospitality.supplier-order`
(fixture: `Credit note CN-4471`), `finance` (fixture: `Refunds and credits March 2026.csv`;
discriminator: account identity and posting structure versus authorisation identity and a paired
stock consequence — the restock column is literally the deciding cell), `business_operations`
(fixture: the returns policy), and `retail_hospitality.stocktake` (fixture: a write-off line).

`also_holds_with` is **empty**. Per CONNECTION §5 it is schema↔schema only and this row is a
template. The intent is recorded here for R1c instead: **`retail_hospitality` ↔ `finance` genuinely
co-hold on disjoint evidence** in this row's material — a returns folder carrying both a case file
and the merchant settlement statement the outcome posted into — and the schema anchor has already
authored that join. Nothing needs to change; I am recording that I found the same join from below.

`role_split` is empty. The schema anchor already carries the family's defining operator/guest split
and states that neither side gets a key. The merchant/manufacturer seam is a genuine role difference
but neither side proposes a key for it, so expressing it as a `role_split` would be decorative; it is
the `manufacturing.warranty-claim` collision instead.

## Fields

`fields: []` (the schema owns the fields; it declares none) and **`proposed_fields: []`**, which is a
deliberate refusal to mint.

The one concept this row genuinely needs and cannot key is **the return case as an occasion**. The
disciplined move is to ask R1c to *widen* the schema's already-proposed `trading_occasion` rather
than mint `return_case`, `rma`, `claim` or `case_id` — four synonyms for one fact is exactly what the
canonical list exists to prevent, and the anchor's own `trading_occasion` argument makes the same
move against `batch_lot` and `project`. That request is NJ-RW-1. Note the interaction: the anchor
already worries that `trading_occasion` may be three concepts wearing one name; I make it four, so
R1c should rule on the whole set at once rather than on my addition alone.

Three further candidates were considered and rejected as **values, not keys**: `reason_code` (faulty,
wrong size, change of mind — a bounded enum, a facet value); `disposition` (refund, exchange, RTV,
write-off — likewise); and `entitlement_basis` (statutory, policy, warranty, scheme rules). The last
is the only arguable one, because you could imagine branching a tree on Warranty versus Policy
returns. I still declined: it would be a two-or-three-child level under a case level that already
exists, and the anchor's validator quotation rejects meaningless levels. If R1c disagrees it is a
cheap addition later; minting it now would be overbuilding.

## Open questions — NEEDS-JOSEPH

All six are in the node's `open_question` in full. In brief:

- **NJ-RW-1** — is the return case a `trading_occasion` value or its own key? *Alternatives:* widen
  the existing proposal (my reading); mint a new key; or concede that returns file under the order,
  which I argue fails on the orderless warranty claim. **This is the question the node test turns
  on.**
- **NJ-RW-2** — the chargeback: split at the acquirer boundary (my reading) or give the whole dispute
  world to `finance` and narrow this row's name.
- **NJ-RW-3** — three rows wearing one name. Test the single-structure claim hard; if it fails, the
  warranty leg most likely collapses into `manufacturing.warranty-claim`.
- **NJ-RW-4** — recall execution. A merchant taking units back under a safety notice produces a
  structurally identical record and **no landed row claims it**. *Alternatives:* admit here as a
  work_type value (my provisional position); route food cases to `retail_hospitality.food-safety`; or
  leave to the schema default.
- **NJ-RW-5** — may a `retail_hospitality` case group legitimately contain the `business_operations`
  policy version it relied on? A cross-schema group membership question the design docs do not settle.
- **NJ-RW-6** — does the mechanism that forces P7 ahead of a model path reach third-party personal
  data in a row without `is_safety_domain`? This is the parent's NJ-RH-4, sharper here because the
  data subjects are consumers in dispute with the holder.

## Recommendations for R1c (not applied — I edited no file but my own two)

1. Add the reciprocal halves on `retail_hospitality.supplier-order`, `finance`,
   `business_operations` and `retail_hospitality.stocktake`, using the fixtures named above so both
   sides cite the same bytes.
2. When ruling on `trading_occasion`, rule on four shapes, not three (NJ-RW-1).
3. Decide NJ-RW-4 before any row claims recall execution by default; it is currently unowned.

## Self-verification

- `python3 -m json.tool` on the node: **parses**.
- Every `00` span quoted in either file grep-verified with `grep -c` against
  `planning/00-database-agent-product-design.md`: **ten spans, ten single matches, zero fabrications**.
- Every neighbour id in `collides_with` confirmed as a `domain_id` in `planning/domains/roster.json`:
  **eight of eight**.
- Every `falls_through_to` name is one of 00's nine residual homes: **five of five**.
- Every `file_examples.source_type` is in `SOURCE_TYPES`: spreadsheet, text_document, archive, image,
  email — **all five present in the vocabulary**.
- Every `collides_with` entry is an **object** with `domain` + `signal` + `provenance`, and every
  signal names one shared fixture and the discriminating evidence item. No bare id strings.
- `also_holds_with: []` — schema↔schema only, and this row is a template.
- No threshold numbers, no handling classes, no `public_low`, no invented catalogue contents, no
  regexes.
- Files written: exactly `planning/domains/nodes/retail_hospitality.returns-warranty.json` and this
  memo. Nothing else touched.

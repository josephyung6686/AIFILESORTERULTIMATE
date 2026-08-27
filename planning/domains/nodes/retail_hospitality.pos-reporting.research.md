# Research memo — `retail_hospitality.pos-reporting`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/retail_hospitality.pos-reporting.json`
Roster row: template on the fieldless `retail_hospitality` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accept the node**, and rename its working sense to **trading session and till reconciliation** — because the charge is largely won by showing the anchor is a *closed drawer*, not a *report* and not a *period*, and the roster id's own wording invites both mistakes.

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `also_holds_with: []`. Nine `collides_with` entries, each an object naming one fixture on both sides. One `role_split` entry — this row's own discovery, not the schema's. Five NEEDS-JOSEPH items.

## The charge — the strongest case that this row should not exist

Five prosecutions. Three are serious; one nearly succeeded.

**1. It is a document-type word promoted to a node.** Made by the schema against itself. `retail_hospitality.json` lists in `work_types[]`, verbatim: `"trading period report - end-of-day or Z read, tender and cash reconciliation, department sales mix, hourly trade"`. Every artefact I would claim is enumerated there as a *value*. The schema also wrote the rule that convicts me: *"A DOCUMENT-TYPE WORD, standing alone - invoice, rota, log, price list, order, review. These are values of a function dimension, and a row resting on one is the schema's default template wearing a name."* "Z read" is such a word, and the roster name — "Point-of-sale and trading **reporting**" — is a document-type word with a system name in front of it.

**Defeat.** That entry enumerates *four structurally dissimilar documents*, and a `work_type` value carries exactly one per file. What the row recognises is the thing that emits all four at once: a **session that closes**. A drawer is opened with a float, run for a bounded interval, and shut by physically counting the money against what the machine believed — producing, in one motion, a Z-report, a cash-up line, an exception list and a department cut. Several are unintelligible alone: an X-read is a mid-session snapshot meaning nothing without the Z-read that later clears the same counters; a banking slip is a number with no referent until set against the declared cash. The schema's `grouping_reasons` concedes the shape — *"ONE TRADING PERIOD at one site: the end-of-day reads, the banking record and the exception report for one day or one week."* A field value cannot express that a thermal spool, a spreadsheet column and a photographed paying-in slip are one record.

**2. It is a length of time — a calendar level wearing a name.** The sharpest charge, and the row's own name makes it. "Trading period" is a *period*; `record_period` is a field candidate, not a node.

**Defeat, and it is the load-bearing argument of this memo.** The anchor is the **terminal**, and three tests separate it from an interval. (i) *Two closes on one date are two records* — a three-till store's Tuesday produces three independent reconciliations with three floats and three over/short figures, and a period cannot be three things at once. (ii) *One close across two dates is one record* — a bar opening at 21:00 and cashing up at 04:00 has one session, which any period-first reading tears in half. (iii) *The discriminating datum has no time axis at all* — the over/short is the difference between two counts of the same money, a physical fact about a drawer. The date *identifies* the session; it does not root the tree — *"For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."*

**3. It is a duplicate of the schema's default template.** The gravest charge, and worse here than for any sibling. The schema's **first and strongest** deterministic signal is this row in this row's terms — *"A RECONCILIATION-OF-COUNTED-AGAINST-RECORDED structure … a gross or net takings figure BROKEN OUT BY TENDER (cash, card, voucher, account) together with at least two of a declared-cash or banked figure, an over/short or discrepancy figure…"* — and the schema's **first `file_example`** is `EOD 2026-03-14 Till 2 - Camden.pdf`, my fixture in my structure. When the family's headline signal and flagship exemplar are both mine, the honest suspicion is that I *am* the default.

**Defeat, argued in full in the node test below.** Short form: owning one branch of a family-level OR is not a template, and the row differs on all three legs anyway — two detection signals the schema never names, one inserted dimensional level plus one narrowed, and a privacy rule that is *inverted* relative to the family's. The last is the strongest and the least expected.

**4. It is a duplicate of `finance.small-business-bookkeeping`.** Takings are accounting; a sales summary posts to a ledger.

**Defeat.** Gross takings and tender split both post. The **over/short does not** — a close with zero variance and a close with a fifty-pound shortage post *identically* to the accounts and are completely different operational facts. A row whose defining datum is structurally invisible to the neighbour is not a duplicate of it.

**5. It is a row defined by absence** — "no account identity, no posting code, no merchant ID". Rejected quickly: those are the *negative half* of a discriminator. The positive evidence is two cash figures and their difference, plus a monotonic sequence number beside a non-resetting grand total. A fingerprint, not a hole.

## The node test, all three legs

CONNECTION §2: a template exists only where its **detection signals**, **recommended dimensions**, or **privacy rules** differ from its schema's default.

**The schema's default, stated so the difference is measurable.** Held as prose because PR-6 leaves the family fieldless: *"the TRADING UNIT - site, venue or channel - ONLY where the corpus genuinely spans more than one, then the TRADING OCCASION - the session, count, order cycle, booking, function or licensed premises the material belongs to, then the OPERATIONAL RECORD FUNCTION. Trading period sits INSIDE the occasion level, never above the site. NOT TIME-FIRST."*

**Leg 1 — detection. Differs by two additions.** The family signal is *counted-against-recorded, keyed to a till*. This row adds:

- **The sequence fingerprint.** A Z-report carries a monotonically incrementing report number issued once and never reissued, printed beside a **non-resetting grand total** — a lifetime total of the terminal — alongside session totals that *do* clear. A token that only increments next to a total that never clears is the signature of a clearing register close and appears nowhere else on the roster. It is also the only clean Z-vs-X discriminator, which the schema does not draw.
- **The float-and-drop chain.** Opening float → mid-session pickups → banked, reconciling arithmetically with the counted cash. The row's most reliable *spreadsheet* signal precisely because it is arithmetic rather than vocabulary — which matters when the row's constitutional never-alone is the word "till".

It also *narrows* the family signal by requiring both halves — the counted/expected pair **and** a till identity — because the pair alone is also a stocktake. Passed, not decisive alone.

**Leg 2 — dimensions. Differs by one inserted level and one narrowed one.** Trading unit (conditional, on the schema's terms) → **terminal or service point** (conditional) → **session** → function.

The **terminal** level is the difference, and its justification is unique here: a trading day at a site does not produce one record, it produces *N parallel independent* ones, and the question a user brings to this material is *which till was short*. No sibling occasion behaves this way — a count subdivides by room but is one event; a booking is one party; a licence is one premises. The **session** narrowing is that this row needs sub-daily occasions (a lunch service, a morning till session) and needs a midnight-crossing close to be one occasion — the schema's own strain on `record_period` (NJ-RH-5) arriving as a concrete requirement rather than a theory.

Both levels are conditional, for the reason `00` gives: *"The engine validates that the proposed template does not repeat a parent dimension, create meaningless one-child levels, exceed practical depth limits, use an author or organization merely as a collector, expose protected information, or produce empty branches when tested against the accepted group."* Two levels are forbidden outright and both are specifically tempting here: the **operator identity** (a per-employee shortage branch — the plainest "expose protected information" case in the family) and **department/category** (a cut *inside* a close, which would shred one session's evidence across a dozen branches). `time_first: false`; the order stays advisory — *"The system recommends an order based on the domain template, but the user can reverse, remove, add, or flatten dimensions."*

**Leg 3 — privacy. Differs by inversion, and this is the cleanest pass.** The family's posture exists because its highest-volume output is personal data about **members of the public**. A trading-session corpus has essentially none: a Z-read names no customer, an hourly trade profile is an aggregate. Inheriting the family posture unchanged would protect this row for a reason untrue of it and leave unprotected the reason that is true.

What it carries instead is **staff-facing, allegation-adjacent data** — and the schema names the artefact without noticing it belongs to a different subject: *"till exception and cash-variance reports are, in substance, suspicion records about named staff."* An exception listing attributed to a clerk, a shortage ranked by operator, a manager-authorisation column — these concern people in a **continuing employment relationship** with the holder, who can be harmed by a tree that groups them by shortage. That is a different risk from a one-visit guest's phone number. Secondarily it carries commercial-security data the family does not otherwise meet: a year of cash-up sheets documents when cash sits on the premises and in what quantity.

Three operative consequences follow that the schema's statement does not produce: an operator identity is never a folder level or group anchor; an exception ranking is never restated as a finding in a summary; and an operator-attributed exception report routes to **Protected Records** rather than Review Later when the row does not fire.

**Verdict: one decisive leg (privacy), one strong (dimensions, conditional on NJ-POS-1), one supporting (detection). Accept.**

## Sources used

`RESEARCH-BRIEF.md`; the stamped assignment via `make_prompt.py`; `retail_hospitality.json` (the anchor — `template`, `recognition`, `work_types`, `grouping_reasons`, `never_alone`, `sensitivity_why`, `falls_through_to`, `collides_with`); `retail_hospitality.stocktake.research.md` as the depth and idiom calibration, chosen over a launch row because it is the closest structural relative — it too reconciles a counted reality against a recorded belief; `roster.json` (all nine neighbour ids verified present); and the five landed rows already carrying a boundary against this id, found with one `grep -rl` — `ecommerce-ops`, `event-production`, `menu-recipe-costing`, `stocktake`, `guest-feedback`. `00` was reached **only by targeted grep**; all sixteen quotations `grep -c`-verified verbatim. The anchor's `.research.md` was **not** opened; the JSON settled the node test without it.

## Files considered and rejected

- **`Merchant settlement 2026-03 - Camden.pdf`** — the headline rejection and the row's collision fixture (below). A card acquirer's statement splits gross volume by scheme exactly as a Z-read splits tender. `finance`'s.
- **`Restaurant receipt - Le Petit Jardin 14 Mar.pdf`** — the *customer's* copy, printed by the same machine, same font, same paper, same 40-column layout. One transaction, no float, no sequence, no reconciliation. Receipts and Confirmations.
- **`Daily Sales Report - specimen.pdf`** — an EPOS vendor's sample. A *perfect* Z-read by construction, round numbers, "Demo Store 001". This is why "separating a real close from a specimen" is a `needs_llm` entry and not a deterministic one.
- **`Z-Report.png`** in a repo's `docs/` or `fixtures/` — a screenshot of an EPOS UI held as software documentation. The token is the row's constitutional never-alone precisely because of files like this.
- **`Weekly sales league - all franchisees.pdf`** — a franchisor's benchmark table. Takings, sites, dates, no drawer: the franchisor running *itself*, which the schema's existential-seam entry already assigns to `business_operations`.
- **`Till variance - J Okoro - 14 Mar.docx`** — an investigation file. The variance is the *evidence*; the document is about the *person*. `hr.employee-relations`.
- **`Refund authorisation RA-4471 - customer copy.pdf`** — a decision with a customer, a reason and an authorisation. `retail_hospitality.returns-warranty`. A refund *line inside an exception block* is mine; a refund *decision* is not.
- **`Stock count W12 2026 - counted vs system.xlsx`** — my nearest structural relative: two quantities and their difference. It counts *goods against a book*; I count *money against a machine*. `retail_hospitality.stocktake`, which said the same from its side.
- **`Hotel night audit 2026-03-14.pdf`** — genuinely undecided, surfaced as NJ-POS-5. A close, but keyed to a *property and a business date* with no drawer at all.
- **A live EPOS or till database** — a source system, not a file node. Only a bounded export with a readable manifest is represented.

## `proposed_fields` justification

None, deliberately. The schema owns the fields and declares none under PR-6 as D1 narrowed it; a template may reuse only what its schema declares. Minting `terminal`, `till`, `session`, `tender_type` or `variance_kind` would create exactly the second copy of the schema the contract forbids — and `till_operator`, the key the material most obviously suggests, must never be minted **at all**, for the reason set out in `role_split`. The intent is recorded for R1c in NJ-POS-1 and NJ-POS-2 as **concepts, not keys**: if PR-6 is lifted this row would want the schema's already-proposed `site`, plus a terminal/service-point concept and a session concept capable of sub-daily granularity.

## Reciprocal boundaries

Each is written into the node as an object naming one fixture on both sides. Four were authored first by the neighbour and are endorsed rather than re-argued.

| Neighbour | Same fixture both sides | This row owns | Neighbour owns | Discriminator |
|---|---|---|---|---|
| `finance.small-business-bookkeeping` | `Merchant settlement 2026-03.pdf` | the operational close | the account and the ledger | till identity + physical count vs account identity + posting structure |
| `retail_hospitality.ecommerce-ops` *(theirs, endorsed verbatim)* | `Sales by day March 2026.xlsx` | the trading-session read | the channel read | drawer reconciliation present vs orders-against-sessions |
| `retail_hospitality.menu-recipe-costing` *(theirs, endorsed)* | `Menu engineering - March 2026.xlsx` | the dated trading-period read | the cost side | dated period + site vs component build-up present |
| `retail_hospitality.event-production` *(theirs, endorsed verbatim)* | `6 Jun - festival bar takings.xlsx` | counted-vs-believed | planned-vs-spent, promised-vs-present | which pair the variance compares |
| `business_operations.budget-forecast` | `March trading review - Camden.xlsx` | the counted-against-believed close | forecast-against-actual over fiscal periods | whether the second number is a **count** or a **plan** |
| `hr.employee-relations` | `Till variance - J Okoro - 14 Mar.docx` | the exception record as a trading artefact | the case about the person | person as **column value** vs person as **subject** |
| `retail_hospitality.returns-warranty` | `Refunds 2026-03-14.csv` | the refund as a tender-affecting count | the refund as a decision | operator + transaction no. vs customer + reason + authorisation |
| `retail_hospitality.store-operations` | `Camden - March site pack.pdf` | the closes themselves | the pack as an assembly | containment is not confusion |
| `retail_hospitality.bookings-reservations` | `Covers by service - March.xlsx` | covers as a **divisor** | covers as a **commitment** | count attached to a period vs to a party |

Four are authored one-way and R1c owes the reciprocal: `finance.small-business-bookkeeping`, `business_operations.budget-forecast`, `hr.employee-relations`, `retail_hospitality.returns-warranty`.

## Neighbours considered that did NOT get an edge

- **`retail_hospitality.stocktake`** — the sibling declined an edge with me first (*"one counts money in a drawer against a till, the other counts goods on a shelf against a book"*). **I agree and record no edge**, rather than half-opening a seam the neighbour closed. Its revisit condition is carried into NJ-POS-5's tail so a combined cash-and-stock pack opens the seam on *both* rows at once.
- **`retail_hospitality.guest-feedback`** — declined first: *"A Z-read has no author and no utterance; a review has no tender split."* Accepted unchanged.
- **`logistics`** *(a `must_consider` neighbour)* — no shared fixture exists. A close is keyed to a drawer and a session; every logistics structure is keyed to a consignment or a facility's work. An edge would be true-and-useless.
- **`retail_hospitality.food-safety` / `premises-licensing`** — share the site and the habit of photographing paper, nothing else. Reading-against-tolerance and permission-keyed-to-premises are evidentially disjoint from a close.
- **`government`** — a licensing authority never sees a Z-read; the schema's custody boundary settles the seam and duplicating it here would be noise.

## The collision fixture

**`Merchant settlement 2026-03 - Camden.pdf`.** It carries a tender breakdown split by card scheme — one of this row's headline signals, in full and in the same vocabulary — for the same site, month and money. It is not this row's file. What discriminates, both ways: it is keyed to a **merchant ID and a settlement date** and terminates in a **net amount paid to a named bank account**, and it contains **no float, no declared cash, no over/short, no till identity**. The rule generalises to a testable pair — an account identity with a posting or settlement structure decides for `finance`; a till identity with a physical count decides for this row. Where one workbook carries both, both worlds are genuinely true and finance's protective ordering runs first.

A second and harder one is inside the family, and it is why the row's `needs_llm` list is not shorter: **`Daily Sales Report - specimen.pdf`**, a structurally perfect Z-read deliberately engineered by an EPOS vendor to look exactly like a live one. No deterministic signal separates it; only the round numbers, the demo store name and the brochures beside it can, and that is a judgement, not a rule.

## Recommendations for R1c (not applied — no neighbour file was touched)

1. **Rename the roster row.** "Point-of-sale and trading reporting" names a *system* and a *document type* over a *period* — three of the five things a row must not be — and is why this memo's longest section is the calendar charge. The row's name should be its anchor: *trading session and till reconciliation*.
2. `finance.small-business-bookkeeping` should carry `Merchant settlement 2026-03.pdf` as its **positive** fixture and name the promotion condition to this row, mirroring what `logistics.warehouse-ops` did for the stocktake valuation file.
3. `hr.employee-relations` should state the till-variance seam in the same words this row does. It is the seam most likely to cause real harm if the two rows disagree.
4. The `retail_hospitality` ↔ `finance` co-activation intent (a trading-period archive holding both a Z-read set and a settlement statement) belongs on the **schema pair**, not here — `also_holds_with` is schema-to-schema only under CONNECTION §5 and this row is a template, so it is left empty; the anchor already records the intent.

## NEEDS-JOSEPH

- **NJ-POS-1** *(sharpest)* — **the terminal level**, this row's entire dimensional difference and simultaneously the level most likely to be a one-child branch. *A:* recommend it conditionally, on the terms the schema conditions the site level, firing only where a session set shows two or more terminals — **this row proposes A**. *B:* drop it and let the session hold every close flat; then the dimensional leg fails and the row rests on detection and privacy alone. It would still stand, but by a thinner margin than this memo would like.
- **NJ-POS-2** — **sub-daily sessions.** This row needs a lunch service and a morning till session as first-class occasions, and a midnight-crossing close to be one occasion. The schema's NJ-RH-5 as a concrete requirement: both existing proposals of `record_period` are multi-day ranges. *A:* widen `record_period`. *B:* mint a session concept at schema level. *C:* accept the close has no level and is identified only by its date — which silently reintroduces the time-first shape the family forbids.
- **NJ-POS-3** — **the menu-engineering workbook**, carried so both rows say the same thing. `menu-recipe-costing` proposed the component build-up as the discriminator (its NJ-MRC-1) and this row adopts it verbatim; R1c must ratify one wording and both rows must carry it.
- **NJ-POS-4** — whether the mechanism forcing P7 ahead of a model path reaches **employee-identifying** operational data in a row without `is_safety_domain`. `business_operations` and the `retail_hospitality` schema recorded this gap for third-party data; this row records it for staff data, where the subject has an *ongoing* relationship with the holder and the material is allegation-adjacent.
- **NJ-POS-5** — whether a **hospitality service point** is the same concept as a **retail terminal**. A restaurant's close is often keyed to a service across several handhelds; a hotel's night audit to a property and a business date with no drawer at all. This row reads them as one level wearing two names; the alternative is that hotel night-audit material is not this row's and needs a home the roster does not have. *Tail:* if a combined cash-and-stock period-end pack appears, open the `stocktake` seam on both rows at once — that row and this one currently agree there is none.

## Self-verification

`python3 -m json.tool` parses the node. Key set is **identical and in the same order** as the landed sibling `retail_hospitality.stocktake.json` (checked programmatically). All nine `collides_with` entries are objects carrying `domain`, `signal` and `provenance`, every `domain` confirmed present in `roster.json` (checked programmatically; zero missing). Every `file_kinds.source_types` entry and every `file_examples.source_type` is drawn from `SOURCE_TYPES`. Every `falls_through_to.residual_template` and `falls_through_if_inactive` is one of `00`'s nine residual names. All sixteen `00` quotations were `grep -c`-verified verbatim before use, plus the anchor quotations against `retail_hospitality.json`. `design_cite` is `null` throughout: no span of `00` names this situation, and a decorative cite is worse than none. No thresholds, statistics, file counts, handling classes, confidence scores or regexes. `fields`, `proposed_fields`, `dimension_order` and `also_holds_with` are empty by contract; `also_holds_with` specifically because this is a template and CONNECTION §5 restricts it to schema-to-schema. Only the two assigned files were written.

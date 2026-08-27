# nonprofit.fundraising-donor — lab notes (R1b)

Depth: J-DEPTH
Date: 2026-08-27
Roster row: `kind: template`, `schema_id: nonprofit`, `launch: placeholder`, `parent_id: null`.
Output: [`nonprofit.fundraising-donor.json`](nonprofit.fundraising-donor.json).
Salvage: none — no prior draft existed for either file. Both are new and this pass owns them.
Verdict: **`refuse_node: false`** — the row survives, on all three legs, and the argument for
refusing it was strong enough that it is written out in full below before it is defeated.

## Sources actually used

- `RESEARCH-BRIEF.md` (in full) and the stamped assignment from
  `make_prompt.py nonprofit.fundraising-donor`.
- `planning/domains/nodes/nonprofit.json` — **the schema anchor, read in full.** Every difference
  claimed below is a difference from a specific sentence in that file.
- `planning/00-database-agent-product-design.md` — reached by targeted `grep -n`, never streamed.
  Every span quoted in the JSON was grep-verified verbatim before it was written.
- `canonical_fields.json` (36 keys, read mechanically — nothing minted) and `roster.json`
  (this id, its nine `nonprofit.*` siblings, and every edge endpoint; 11/11 resolve).
- `finance.crypto-assets.research.md` — the one landed launch row read for depth calibration. Its
  `role_split` refusal and `NJ-CRYPTO-1` are the models for the `campaign`/`project` argument here.
- Two neighbours that already argued a boundary against this id, found with one grep and read only
  at the matched span: `business_operations.partnerships-bd.json` and
  `government.grant-programme-administration.json`. Both reciprocated from this side using
  **their** fixture. Neither file was edited.

**No external sources.** The document structures named below — the printed no-goods-or-services
acknowledgement sentence, the fair-market-value/deductible-portion split on an event ticket, the
signed tax-relief declaration carrying the giver's home address, and the campaign/appeal/fund
gift-coding triple in fundraising database exports — come from domain knowledge and are marked
**inference** throughout the JSON. They create no gazetteer content, regex, threshold or field.

## THE CHARGE — the strongest case that this row should not exist

Written first and honestly, because the brief is right that inventing a filing world to save an
id is the recorded failure mode. Six attacks, in ascending order of force.

1. **It is a work_type value.** The nonprofit schema's own `work_types[]` already contains
   "donation record, gift declaration, pledge schedule, legacy file, and appeal performance
   record" and "donor or supporter register and its exports". This row is, on its face, two
   entries of an enum promoted to a node. ALIGNMENT is explicit that work types are values.
2. **It is a lifecycle stage.** Fundraising is the money-**in** phase of an association's cycle;
   `nonprofit.grant-reporting` is the money-**in-with-strings** phase and business_operations
   holds the spending phase. Phases of one cycle are not separate filing worlds.
3. **It is a document type.** Strip the row to its files and you get "receipt", "letter",
   "declaration", "spreadsheet of people". The schema itself strikes a document-type word as
   never-alone.
4. **It is a duplicate of its own schema's default template.** The schema's fourth deterministic
   signal is *already* "A DONATION or GIFT structure pairing a named or explicitly anonymised
   donor slot with a recipient association and a TAX or RELIEF declaration". Its default
   dimension prose *already* names "the appeal" as a permitted counterparty-or-fund level. Its
   privacy paragraph *already* argues third-party exposure. What is left for a template to add?
5. **It is a duplicate of neighbours.** `business_operations.partnerships-bd` already claims the
   funder-approach pipeline in its own landed edge. `finance` owns the giver's copy of every
   receipt. `business_operations.customer-account-management` owns CRM. `nonprofit.member-
   association` owns dues. Subtract all four and the residue may be empty.
6. **It is defined by an ABSENCE — the strongest attack.** A gift is "a payment with no
   deliverable". The schema's own `open_question` marks its volunteer-programme candidate WEAK
   precisely because "its discriminator is an absence of payroll structure". If this row's
   discriminator is an absent invoice, it is the same weak row and should be refused for the same
   reason, with coverage routed to finance and Receipts and Confirmations.

## Defeating the charge

Attack 6 is the one that decides the row, and it fails on a fact about the documents.

**The non-exchange in this world is PRINTED, not absent.** A charitable acknowledgement carries,
as a required element of a contemporaneous written acknowledgement, an explicit statement of
whether any goods or services were provided in return and, where they were, a good-faith estimate
of their value. A tax-relief declaration is a signed form on which the giver states in the first
person that they are a taxpayer, names the recipient charity, gives their full name and home
address, and states which past, present and future gifts the declaration covers. An event ticket
prints three numbers: paid, fair market value received, deductible portion. In every case the
"nothing was given in return" is an affirmative labelled element on the page. That is the exact
opposite of the volunteer row's missing gross-to-net column, and it is why this row can carry a
deterministic gate — encoded as the first `never_alone` rule, which strikes the absence of an
invoice or a deliverable outright and is the single most important sentence in the node.

Attacks 1 and 3 fail together because the row's signature is a **structure**, not a word or a
value: the campaign / appeal / fund gift-coding triple held with acknowledgement status, soft
credit, matching gift, recognition level and pledge balance. That column set exists in no other
roster row's register — customer-account-management's has orders and renewals,
member-association's has classes and join dates, and the schema's own restricted-fund signal has a
fund partition and no gift coding at all.

Attack 2 fails because the phases differ by *evidence*, not timing: the report-back obligation
that separates this row from `nonprofit.grant-reporting` is a property of the instrument, so an
unrestricted foundation grant received in January is this row's and a major-gift pledge carrying
an impact-reporting clause received the same day is the neighbour's.

Attack 5 fails on residue. After ceding sponsorship to partnerships-bd, the giver's copy to
finance, customer CRM to customer-account-management and dues to member-association, seven
structures remain and no other row claims any of them: the appeal package with its gift
instrument, the declaration and its register, the recipient-side acknowledgement, the pledge with
its instalment schedule, the event's declared benefit split, the legacy notification, and the
prospect dossier.

Attack 4 — the duplicate-of-default attack — is the node test proper, answered next.

## The node test, all three legs

CONNECTION §2: a template exists only when its **detection signals**, **recommended dimensions**,
or **privacy rules** differ from its schema's default. This row differs on all three, and would
be worth writing on any one.

**Leg 1 — detection signals differ.** The schema's DONATION/GIFT signal is one sentence pairing a
donor slot, a recipient and a relief declaration. This row adds four structures that sentence does
not reach and could not: (a) the **campaign/appeal/fund coding triple** with acknowledgement
status and soft credit — a register column set, not a donor slot; (b) the **quid-pro-quo split**,
the only place in the entire roster where a document declares on its own face that a payment is
*partly* an exchange; (c) the **appeal package** signal, which requires an ask paired with a gift
instrument (reply device, pledge card, coded donate address, mandate) and explicitly refuses to
fire on an ask alone; (d) the **prospect-research dossier**, which has no gift, no declaration and
no acknowledgement anywhere in it and is therefore invisible to every one of the schema's signals.
The row also adds a gate the schema does not have — the printed-not-absent rule above.

**Leg 2 — recommended dimensions differ, and differ by a prohibition.** Both are `[]` under PR-6,
so the comparison is between the two prose paragraphs. The schema recommends
ASSOCIATION → COUNTERPARTY-OR-FUND → PERIOD → FUNCTION. This row recommends
APPEAL-OR-CAMPAIGN → PERIOD → FUNCTION, and the difference is not cosmetic:

- The schema **permits** a counterparty level (a grant, a fund, a membership class are all
  legitimate folder levels). This row **forbids** its counterparty level, because this row's
  counterparty is a named living person. The schema forbids person-levels for beneficiaries on
  grounds of vulnerability; this row extends the prohibition to donors, prospects, pledgors and
  legators on grounds of disclosure alone — people who are neither vulnerable nor served. A row
  that turns one of its schema's permitted levels into a ban is not a copy of it.
- The appeal is a different first level from the fund. A fund is an accounting destination that
  outlives everything; an appeal is a bounded effort. Putting the fund first — which the schema's
  paragraph allows — scatters one appeal's letter, reply device, artwork and results across
  accounting buckets, which is precisely the failure 00 warns about for time-first ordering.

**Leg 3 — privacy rules differ in kind, not degree.** The schema's paragraph is argued about a
third party who "frequently disclosed under need, harm or vulnerability". This row's protected
party is a **donor or a prospect**, typically neither, exposed through three mechanisms the
schema's paragraph does not name: **non-consent** (a wealth-screening dossier is compiled about a
living person who does not know it exists — not a party who failed to consent but one who cannot);
**self-declared disclosure rules** (a gift record prints its own confidentiality — anonymous and
do not publish, a recognition name differing from the legal name, an in-memoriam attribution, a
do-not-solicit flag — so the artefact states a rule the filesystem can violate, which no other
roster row's material does); and **inference from the fact of the record** (what a person gives to
discloses belief, politics, health history and family bereavement before an amount is read). Full
argument in `sensitivity_why`.

Nothing was invented to keep the row: `fields: []`, `also_holds_with: []` by contract, one
proposed field that argues for its own non-adoption, and the two questions that would have been
tempting to answer are parked in `open_question` instead.

## Files considered and REJECTED — the tempting false positives

- **Trustee minutes / a charity budget / a charity annual report.** The schema's own collision
  fixture. A charitable footer never promotes a business_operations file.
- **A charity's bank statement whose every line is a donation.** Donation lines do not make it
  fundraising: an institution-and-account header is finance's custodial record. This row claims
  the gift record, never the account.
- **A restricted-fund statement (SOFA, fund-balance table).** The schema's, not this row's — a
  fund partition with no gift or appeal coding is struck in `never_alone`. The single easiest way
  for this row to over-reach.
- **A corporate sponsorship deck with tiered packages.** To `partnerships-bd`: a named, valued
  benefit package is an exchange. Kept only as a collision, discriminated by *naming* the benefit
  rather than failing to find one — the row does not fire on absence.
- **A gala's venue contract, catering invoice and AV quote.** Same event, same folder, same date,
  none of them this row's: they share the event's *name* and no evidence.
- **A fundraising newsletter and a giving-day calendar entry.** Association branding, no gift
  instrument, no coding, no declaration. They fire nothing.
- **Another charity's appeal letter as a swipe file; a regulator's code of practice; a sector
  benchmarking study.** Reading material — routed to Reading Inbox and kept as a `needs_llm` case
  (operative record versus downloaded exemplar), because topic cannot separate them: "Topic
  answers what a file is about, while purpose answers what the file was for."
- **A crowdfunding page for an individual's medical bills.** Money given without return and still
  not this row's: no association, no declaration, no register.
- **A payroll-giving deduction on an employee's payslip.** The payslip is `hr`'s and the deduction
  is a line on someone else's record. The *employer's* remittance schedule is kept, as a value.
- **A donation-platform notification email.** Kept, but as a *negative* fixture: its
  gross-fee-net breakdown is a processor settlement line, not this row's evidence.

## `proposed_fields` — one entry, arguing for its own rejection

`campaign`, and the entry's first stated preference is that R1c **not adopt it** and reuse
canonical `project` instead. The gift-coding triple has two nested named levels (campaign, appeal)
plus an accounting destination (fund); canonical has one key for a bounded named effort
(`project`); and the danger is not that one key is missing but that a later template author,
finding nothing, mints three synonyms. The proposal exists to pre-empt that mint — the
`finance.crypto-assets` pattern of parking a temptation rather than acting on it.

Keys deliberately **not** proposed:

- **`donor`.** The first thing a key does is raise whether it may be a folder level, and the
  answer here is an absolute no. The need is already covered by the schema's `subject_of_record`
  proposal, which the schema asks be adjudicated **destination-ineligible** for this family. This
  row endorses that and adds a reason the schema does not have: the ineligibility must hold even
  for a donor who is not vulnerable, because the disclosure is of what they gave, not of what
  happened to them.
- **`appeal`, `fund`, `source_code`, `solicitation`, `giving_level`, `pledge_status`** — the
  synonym mint above, plus two that are plainly enum values.
- **`sponsor` / `organization`** — referenced, not re-proposed. Both are the schema's proposals
  and `sponsor` is contested with `research.grants-funding`; this row adds evidence to that
  adjudication through `role_split` and mints nothing.

`proposed_context_terms` (42) are R6 candidates marked PROPOSED, never design; 00 states the
pattern-plus-context *shape* for course codes only and lists none of them.

## Reciprocal boundaries — same fixture named on both sides

Nine collisions, every one written as an object with a `signal` that names the shared fixture and
both owners, per the edge-shape repair. The four that decide the row:

| Neighbour | Shared fixture | This row owns | They own | Discriminator |
|---|---|---|---|---|
| `nonprofit.grant-reporting` | `Community Trust - award letter 2026.pdf` — carries a no-goods sentence **and** a report-back clause | the unconditional transfer whose only obligation is acknowledgement | the conditional accountable transfer with restricted purpose, milestone reporting, expenditure reconciliation | a reporting-and-reconciliation obligation flowing back to the giver — never the word *grant*, never the funder being a foundation, never the size |
| `finance` | `Acknowledgement - 2026 Annual Fund - APR26-DM - 500.pdf` — byte-identical on both disks | the recipient association's copy | the giver's copy, as their own tax substantiation | side evidence **outside** the page (batch position, covering email, accompanying register); letterhead, charity number and the no-goods sentence are on both and discriminate neither |
| `nonprofit.member-association` | one combined renewal form: dues **plus** a voluntary gift with a relief tick | the gift line | the dues line and the register it updates | whether the payment confers rights — dues do, gifts do not; both rows fire on one page, on disjoint lines |
| `business_operations.partnerships-bd` | a corporate sponsorship deck with tiered packages | the unconditional corporate gift | the sold sponsorship | a named, **valued** benefit package on the page — the model must be able to name the benefit, not merely fail to find one |

The other five, each with the same fixture named on both sides in the JSON:
`business_operations.customer-account-management` (a CRM export — acknowledgement status, soft
credit and the coding triple against orders, renewals and entitlements);
`business_operations.corporate-regulatory-filings` (a tax-relief claim schedule — the declaration
register here, the filed submission there); `nonprofit.political-campaign` (a contributor listing
— discriminated by the captured occupation-and-employer pair and a disclosure schedule, with the
privacy inversion that this row's register is compiled to be kept private and theirs to be
published); `nonprofit.religious-institution` (a congregational giving statement — anchored on a
campaign here, on a household's standing there); `government.grant-programme-administration`
(their fixture, the call for applications, used from this side to surface NJ-FD-1).

Two of the nine reciprocate edges the neighbours wrote first (`partnerships-bd` and
`government.grant-programme-administration`). Both were read at the matched span only, neither
file was touched, and the reciprocals extend **their** fixture and discriminator rather than
replacing them.

## The collision fixture, and sparse-file discipline

`Community Trust - award letter 2026.pdf` is the file that looks exactly like this row's evidence
and is not. It **satisfies this row's own gate** — the non-exchange sentence is printed on it —
and the row still loses, because a restricted purpose clause, conditional instalments and a
report-back obligation make it a conditional accountable transfer, which is
`nonprofit.grant-reporting`'s. It is the sharpest available test precisely because the gate passes
and the answer is still no. Two secondary collision fixtures: `IMG_4417.jpg`, the novelty cheque
photograph whose OCR yields a charity name, an amount and the word *donation* and which is a
picture of a prop; and `constituent_gift_export_FY26.csv` read as a generic CRM export.

`Thank you.pdf` is this row's `HW 3.pdf` — one page, a signature block, no amount, no code, no
declaration, sitting beside a coded acknowledgement batch. `group_without_copying_facts: true`,
universals only, and its `must_not_conclude` quotes 00: "The graph does not automatically copy
those missing facts onto sparse files." Three fixtures carry the flag; the others are the platform
notification and the cheque photograph.

## Neighbours considered that did NOT get an edge

- **`hr`** — payroll giving is real, but the payslip deduction is a line on `hr`'s record, not a
  shared fixture. No discriminating evidence competes.
- **`legal`** — a naming-rights pledge agreement and a deed of covenant are instruments, and the
  temptation was real. Not a collision: the executed instrument is legal's and protects first, the
  drawdown and stewardship that follow are this row's, and the schema already states that seam.
  Carried as `also_schema: "legal"` on the award-letter fixture and as a `needs_llm` line asking
  whether a recognition clause has turned a gift into an exchange.
- **`research.grants-funding`** — the schema owns that seam and argues it at length; a second
  claimant from a template would give one evidence item three homes.
- **`clinical_practice`** — a disease charity's donor may also be a service user, but no fixture
  competes and the schema already holds the beneficiary seam.
- **`photos`** — carried as `also_schema` on the cheque photograph, because the correct outcome
  there is that this row does **not** fire.
- **`also_holds_with`, empty by contract.** CONNECTION §5 restricts it to schema ↔ schema and this
  row is a template. The co-activations are expressed where a template may express them, in
  `file_examples.also_schema`. **Recommendation for R1c, not an edit:** the nonprofit schema's
  `also_holds_with` already carries `finance` and `legal`; nothing needs adding for this row.

## Audits run before returning

- `python3 -m json.tool` — parses.
- **Every 00 quotation grep-verified verbatim** with `grep -c -F` before it was written into the
  JSON — the six residual definitions (line 120), the spreadsheet and archive extraction paths and
  the no-unpacking rule, "a labeled form field", the page-one-position and tables sentences, the
  Columbia role-ambiguity sentence, the return-unknown, correct-abstention, topic-versus-purpose,
  content-incoherent, sparse-file, not-time-first, recommend-not-freeze, collector and
  one-child-level, data-minimizing, corpus-contents, four-safety-domains and
  sensitive-prompt-consent spans. Each returned exactly one match. **No 00 quotation in this node
  is fabricated or paraphrased inside quote marks.**
- Every `file_examples.source_type` is in `SOURCE_TYPES` (10/10). Every edge id resolves on the
  roster (11/11, including the `also_schema` targets `finance`, `legal`, `photos`). Every
  `falls_through_to.residual_template` is one of 00's nine names (6/6).
- `also_holds_with` empty by contract; `fields` empty under PR-6; one `role_split` that mints
  nothing. No threshold, score, confidence or evidence count anywhere; no handling class;
  `sensitivity` is `potentially_sensitive` only.
- Only the two assigned files were written. `29-DOMAIN-OWNERSHIP.md`, the roster,
  `canonical_fields.json`, `check.py`, `src/`, the SPECs and every neighbour node are untouched.

## NEEDS-JOSEPH (this node only)

Stated in full in the JSON's `open_question`; summarised here with their alternatives.

- **NJ-FD-1 — the grantmaker gap.** Nobody on the roster holds the **private funder's** own side
  of philanthropy: `government.grant-programme-administration` pushes a private foundation's
  call/scoring/award corpus away as "private-association material", `nonprofit.grant-reporting` is
  the grantee's side, and this row is the recipient's fundraising side. Alternatives: (a) widen
  grant-reporting to both sides with a role_split; (b) add a grantmaking row; (c) route it to
  business_operations. This row did **not** absorb it and recommends against — a grantmaker's
  records are close to the mirror image of this row's, and absorbing them would make the row's
  donor-privacy argument incoherent.
- **NJ-FD-2 — declaration versus claim.** The roster hint gives "tax-relief claims" to this row,
  but the schema cedes authority returns to `business_operations.corporate-regulatory-filings`.
  This row splits at submission: declarations and their register here, the filed claim there.
  Confirm or invert; if inverted, amend the hint.
- **NJ-FD-3 — `campaign` versus `project`.** Adjudicate once, roster-wide: (a) reuse canonical
  `project`, this row's preference; (b) adopt `campaign` once; (c) in all cases forbid `appeal`,
  `fund`, `fund_code`, `source_code`, `solicitation`.
- **NJ-FD-4 — the quid-pro-quo problem, a genuine widening of the schema's gate.** The schema's
  gate is a **non-exchange** relation, but a gala ticket, a table sponsorship, an auction lot and a
  naming-rights pledge are **partial** exchanges that print their own split. Read strictly, the
  gate excludes them and this row loses its entire event and major-gift coverage. This row reads
  the printed split as an affirmative declaration that a gift portion exists; only R1c can ratify
  that. If rejected, the row shrinks to declarations, acknowledgements, appeals, pledges and
  registers — still a node on all three legs, but the event fixture and one work_type must go.
- **NJ-FD-5 — protection without a flag.** A donor register export is a bulk file of named living
  people with addresses and giving histories; a prospect dossier is a non-consensual profile of
  one. Both must be detected to be protected and neither can carry `is_safety_domain`, whose four
  members 00 names and closes. The schema's NJ-NP-3 on grounds it does not cover — bulk personal
  data and non-consent rather than vulnerability — needing the same substitute mechanism named.

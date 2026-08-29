# Research memo — `retail_hospitality.guest-feedback`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/retail_hospitality.guest-feedback.json`
Roster row: template on the fieldless `retail_hospitality` schema, `parent_id: null`, placeholder launch

## Result

**Accept** — but not on the leg one would expect, and not cleanly. The row passes decisively on
**detection** and on **privacy**; it passes only **partially** on **dimensions**, where its difference
from the schema default is half a subtraction. That weakness is written into the node as `NJ-GF-1`
rather than smoothed, because it is the finding most likely to change the row's shape at R1c.

The one thing that makes this a situation rather than a label: it is the **only template of the
fourteen whose characteristic artefact is authored by a member of the public**. Every sibling holds
what the operator wrote about a guest. This holds what a guest wrote about the operator, plus the
reply. That inversion is structural, not thematic, and the detection signals are built on it.

## The charge — the strongest case that this row should not exist

Five prosecutions. The fourth nearly landed.

**1. A lifecycle stage.** The hint says "what guests said *afterwards*", and "after the transaction" is
a stage in the plainest sense. *Defeated:* the row is not recognised by lateness. A post-event
reconciliation, a final account and a closing stock count are all "afterwards" and none is this row;
a complaint that arrives mid-stay, before the occasion ends, *is*. Neither necessary nor sufficient,
so not the definition.

**2. A document type — the word `review`.** Not a prosecution I invented: the schema anchor's own
`never_alone` list reads *"A DOCUMENT-TYPE WORD, standing alone - invoice, rota, log, price list,
order, review… a row resting on one is the schema's default template wearing a name."* The schema
wrote the charge against its own child. *Defeated,* and the defeat is the node's first `never_alone`
entry: `review` is the most overloaded token this row could rest on — licence review, performance
review, code review, design review, literature review, management review, and `Review Later`, a
residual home in the design's own library. `Review.docx` is nothing. Nothing in the node's recognition
fires on the word; it fires on the paired utterance-and-response slot, the dual date, and the
subject-is-my-site-author-is-not-me test. A row unchanged if the word never appeared is not built on
it.

**3. A work-type value on its own schema.** The schema's `work_types[]` already contains, verbatim,
*"guest voice record - platform review export, direct complaint, survey result, operator response."*
*Defeated by the node test proper:* `work_types` is the family's browse vocabulary, not a claim that
each entry is a situation. The test is whether detection, dimensions or privacy differ from the
default — answered on two of three below. If enum membership defeated this row it would defeat all
fourteen siblings, leaving the schema childless, which is not the ratified shape.

**4. A duplicate of its schema's default template.** *This one partly succeeded.* The default (prose,
since PR-6 leaves the schema fieldless) is trading unit → trading occasion → record function, not
time-first. For this row's highest-volume artefact — the platform export — the middle level **is
unrecoverable**: platforms anonymise, a Google review returns no booking reference and cannot be tied
to the stay that produced it. Half this row's material therefore differs from the default by *dropping*
a level, and a row whose only difference is an absence is a forbidden shape.

*Survives narrowly, and conditionally.* (a) The other half — the direct complaint — arrives *with* an
occasion reference (order, booking, case) and keeps the level, so the row is not uniformly a
subtraction. (b) Something positive replaces the collapsed level rather than leaving a hole: the
**channel**, which governs the operator's real workflow because response obligation, right of reply,
moderation and takedown are properties of the platform and of nothing else. (c) Legs 1 and 3 pass on
their own merits and the test is disjunctive. Honest verdict: this leg is *contested*, and it is
`NJ-GF-1` with three alternatives, one of which splits the row.

**5. A duplicate of `business_operations.customer-account-management`,** which landed first and already
edged this row over NPS and satisfaction exports. *Defeated on the fixture:* their discriminator
("a named business customer with a subscription relationship") and mine ("a one-visit or anonymous
consumer keyed to a site, stay, table or order") are disjoint and both testable on the same file. Two
rows that can be tested on one file and give opposite answers are not duplicates.

**Verdict: `refuse_node: false`, leg 2 flagged contested.**

## The node test, argued in full

**Leg 1 — detection differs from the schema default. PASSES DECISIVELY.** Four signals appear nowhere
in the schema's other structures.

- *The paired utterance-and-response slot.* A free-text passage attributed to a named or display-named
  third party set beside an operator reply in its own column (`Management response`, `Owner response`,
  `Response date`). The reply column does the work: **a survey tool collects, it does not answer.** No
  sibling produces a record with a reply slot attached to a third party's own words.
- *The dual date.* Two labelled dates that are not a created/modified pair — date of experience (stay,
  visit, dined on, order date) and date of writing (posted, submitted, received). Every other record
  in this family carries **one** operative date, because a trading record is made at the moment it
  records. This is the cleanest deterministic tell and it survives a useless filename, because both
  are labelled cells and the design licenses reading "dates or identifiers from labeled cells."
- *The bounded-scale rating with its maximum stated* — out of five, a 1–5 legend sheet, a Likert anchor
  row, a 0–10 with a promoter/detractor derivation. The stated maximum is load-bearing: an unbounded
  numeric column is a quantity or a price and belongs to a sibling.
- *The escalation-and-closure chain*: grievance → dated acknowledgement → internal account of events →
  redress decision with a value and an authoriser → final response. The chain fires, never a member; a
  single apology email is not this structure.

None of the schema's default structures — tender reconciliation, count-against-book, capacity-against-
dated-demand, permission-to-trade, daily-signed-check, ingredient-and-yield, order-cycle,
catalogue-and-price — produces any of the four. The schema does list a "GUEST-VOICE structure" in its
recognition union; that is the schema naming what its children collectively recognise, not a default
template already doing this work.

**Leg 2 — dimensions differ. PASSES PARTIALLY; CONTESTED.** Argued under prosecution 4, recorded as
`NJ-GF-1`. Recommendation: **site** (only where the corpus spans more than one) → **channel** →
**feedback record function**, reporting period *inside*, never above. Not time-first, and this row is
more tempted than any sibling because its artefacts carry two dates each — the answer being that both
dates *identify* the utterance rather than *root* the tree: *"For document and record domains, project,
function, or subject usually comes before time because putting year first scatters related work across
calendar folders,"* with the exception reserved for capture: *"Photos and capture-based media are the
major exception…"* A review is not a capture. Serialised as `dimension_order: []`, because a dimension
may only branch on a field the schema declares and the schema declares none.

**Leg 3 — privacy differs. PASSES DECISIVELY; the row's strongest leg.** Three things the schema's own
family posture does not contain:

1. **The linkage trap.** This is the family's only material whose third-party personal data is
   *self-published*, which makes the local copy look low-risk. Wrong, and the row must block it: the
   operator's export is not the public page — it **joins** the public utterance to data that was never
   published (which booking, which staff member, which internal category, what redress, authorised by
   whom). *Public source, private linkage; this row's copy is the linkage.* The identical trap is
   already on record here — `legal.practice-matter-file` warns against concluding "whether a public
   filing makes the local file or neighboring packet low sensitivity" — and transfers exactly.
2. **The allegation against a named colleague.** A complaint is an untested accusation about an
   identified employee, held in a trading folder rather than a personnel system. Never a fact about
   that person, never a grouping anchor, never a dimension.
3. **Special-category leakage through the ordinary door.** Grievances routinely carry an accessibility
   need, an allergic reaction, illness after a meal, a bereavement behind a cancellation, or an
   allegation of discriminatory treatment — health and protected-characteristic data about named
   private individuals, arriving inside a routine export nobody flagged.

Binding design, quoted in the node: privacy policy enforced before any model or external connector,
and protected material excluded from cloud prompts, from raw display in general group summaries, and
from automatic movement. Value stays `potentially_sensitive`; no handling class is invented, since P7
owns those and this phase offers only `none` and `potentially_sensitive`.

## Files considered and rejected

- **`Mystery shopper report - Store 214 - Feb 2026.pdf` — the collision fixture.** A visit date, a site
  the holder operates, a numeric score, a first-person narrative, annotated shop-floor photographs. On
  those observations it is guest feedback almost exactly. *Discriminated by the rubric and who
  instructed the assessor:* it carries a scoring framework of operator-defined standards with points
  available and a pass mark, an `Assessor` block and an assignment reference — and no reviewer display
  name, no channel, no response column, no request for redress. A guest evaluates against their own
  expectation; an assessor evaluates against a document the operator wrote. → `store-operations`.
- **`Employee engagement survey 2026 - results.xlsx`** — same Likert instrument, same free-text column.
  Respondents are the workforce, columns read `Department` / `Line manager`, no visit or stay date. → `hr`.
- **`Reviews - competitor set - Q1 2026.xlsx`** — ratings, comments, dates, platform column, all correct.
  Subject sites are not the holder's, and there is no response column *because you cannot answer a
  rival's reviewer*. → `business_operations.market-research`.
- **`Food hygiene rating certificate.pdf`** — a rating about the premises, issued by an authority. A
  determination, not a voice. → `premises-licensing`.
- **`My review of Le Petit Jardin - draft.docx`** — the holder wrote it, about somewhere else. Fails the
  operator-side test the whole schema rests on. Not this schema at all.
- **`Testimonials page copy v3.docx`** — marketing copy quoting reviews: production apparatus, not a
  feedback record. → `creative`, per the schema's existing boundary.
- **`Chargeback - case 88231 - evidence pack.pdf`** — a scheme reference and a representment deadline.
  → `returns-warranty` / `finance`.
- **`Contacts export - loyalty members.vcf`** — a guest list, not a guest voice. Nobody said anything in it.
- **`App Store reviews - our booking app.csv`** — genuinely hard, deliberately unclaimed. Every signal
  present (ratings, dual dates, developer-response column), but the subject is a *software product* and
  the responder a product team. No roster row plausibly owns it and I will not invent one.

## Reciprocal boundaries — same fixture named on both sides

Nine mutex edges, each an object whose `signal` opens `SAME FIXTURE BOTH SIDES:` and names one real
file plus the discriminating evidence. Summary; the node carries them in full.

| Neighbour | Same fixture | This row owns | They own | Discriminated by |
|---|---|---|---|---|
| `business_operations.customer-account-management` | `Satisfaction and NPS export Q1 2026.csv` | one-visit / anonymous consumers keyed to a stay or order | named B2B counterparties with an account and a renewal | the respondent-identity column |
| `business_operations.market-research` | `Reviews - competitor set - Q1 2026.xlsx` | subject site is the holder's; a response slot exists | a market question, a sampled population, no reply column | subject site + presence of a response slot |
| `retail_hospitality.returns-warranty` | `Re FW Complaint - order 55120 wrong size.eml` | the utterance and the reply; goodwill as reputational act | the RA number, inspection, restock, refund, warranty claim | the return authorisation and its stock movement |
| `retail_hospitality.bookings-reservations` | `Guest history - Ashcroft.pdf` | the post-hoc evaluation and its answer | capacity against dated demand — the held slot | forward to a slot vs backward at an experience |
| `retail_hospitality.store-operations` | `Mystery shopper report - Store 214 - Feb 2026.pdf` | a customer's free evaluation, with a channel and a right of reply | an instructed assessor scoring an operator-written rubric | the rubric and who instructed the assessor |
| `hr` | `Complaint - rude service, table 12, 14 Mar.pdf` | the guest-facing half: grievance, redress, reply to the guest | the personnel process: investigation, statements, outcome | whose process the document belongs to |
| `retail_hospitality.food-safety` | `Allergen incident - 6 Jun - guest reaction.docx` | the complaint and the response to the complainant | the batch trace and the corrective-action chain | facing the guest vs facing the process |
| `finance` | `Goodwill log 2026.xlsx` | redress as service recovery, keyed to grievance category and case ref | the account, the posting, the credit-note run | account identity + posting structure |
| `logistics` | `Complaint - parcel arrived late and damaged - order 55120.eml` | the customer-facing grievance and the reply | consignment, carrier claim, POD dispute, SLA credit | keyed to a consignment vs to a customer case |

Only the `customer-account-management` edge is genuinely reciprocal today — that row landed first and
authored its half. The other eight are marked **AUTHORED ONE-WAY HERE; R1c owes the reciprocal** in the
node text. The `hr` edge is not a byte but a **moment**: one folder holds the guest's letter and the
outcome letter, and nothing in the design decides moments — `NJ-GF-4`.

## Neighbours considered that did NOT get an edge

- **`retail_hospitality.pos-reporting`** — no shared fixture. A Z-read has no author and no utterance; a
  review has no tender split. True-and-useless.
- **`retail_hospitality.ecommerce-ops`** — both name a platform, but the `market-research` and
  `returns-warranty` edges already carry every contested fixture; a third would restate them.
- **`creative`** — testimonials in campaigns. The schema row's production-vs-commercial-apparatus
  boundary decides this unchanged; duplicating it at template level would be noise.
- **`government`** — an ombudsman escalation or a licensing objection. Real, but the schema's
  `government` edge turns on *custody*, which decides this case identically.

## `also_holds_with` — deliberately empty

CONNECTION §5 makes `also_holds_with` **schema ↔ schema only**; this row is a template, so it is `[]`.
Intent recorded for R1c: the schema-level joins this row's material creates are `retail_hospitality ↔
finance` (a redress packet holding a goodwill log and the credit note posted for it), `↔ hr` (a
complaint folder holding the guest's letter and the employee-relations members), and `↔ photos`
(guest-attached photographs, scanned comment cards). All three already exist on the schema row; none
needs adding. Per-file coactivation rides on the fixtures' `also_schema` instead, which is where the
screenshot example records `photos`.

`role_split` is `[]` for the fieldless reason. The schema already carries the family's `operator`/`guest`
split; this row adds only the observation that it is the one place where the guest is the **author**
rather than the subject — which strengthens the schema's rule that `guest` must never be a key.

## `proposed_fields` — one, with its counter-case

**`channel`.** The schema's `site` proposal explicitly folds an e-commerce channel in (`Shopify - UK
store`) on the reading that a channel is a trading unit. That holds for selling — the operator *does*
trade from Shopify — and fails for feedback, because **the operator does not trade from Tripadvisor**. A
single-site hotel has one trading unit and five review channels; folding them merges the only dimension
the workflow turns on, since response obligation, right of reply, moderation and takedown are properties
of the platform alone. No canonical key covers it: `venue` and `institution` are places and bodies,
`record_type` and `work_type` are function values, `download_session` is a retrieval clue, `authored_by`
is the reviewer and is never destination-eligible.

**Counter-case, kept inside the proposal:** `channel` could be read as a **medium**, and a medium is one
of the things a row may not be built on. Answer: the key is not the row's identity — the paired
utterance-and-response structure is — and a platform is a counterparty with rules, not a file format. If
R1c disagrees, the consequence is that this row recommends `site` alone and has no second dimension
(`NJ-GF-2`), **not** that `site` is stretched.

Not minted alongside it: `rating`, `sentiment`, `nps_score`, `complaint_category`, `platform`, `reviewer`
— derived measures, a `work_type` value, a synonym, and a member of the public.

## Incidental finding, recorded and not acted on

`venue` **is already a canonical key**, while `retail_hospitality` proposes `site` (reused from
`manufacturing`) and `construction_property` proposes `property`. Three keys for closely related place
concepts, one already canonical. This row relitigates nothing and proposes nothing about it, but R1c is
already adjudicating `site` against `property` and `venue` belongs in that same adjudication rather than
being discovered afterwards.

## Self-verification

- Both output paths match the ASSIGNMENT; nothing else written or edited (`git status` confirms the other
  changed files under `planning/domains/nodes/` are CODEX's, untouched here).
- `python3 -m json.tool` parses the node cleanly.
- All **22** quoted spans grep back verbatim out of `planning/00-database-agent-product-design.md`,
  checked programmatically by whole-string containment, not by eye.
- Every edge id verified present in `planning/domains/roster.json`.
- Every `collides_with` entry is an **object** with `domain` / `signal` / `provenance`; no bare id
  strings; no `design_cite` written anywhere, decorative or otherwise.
- `also_holds_with: []`, `fields: []`, `dimension_order: []`, `role_split: []`, `time_first: false`.
- Every `file_examples.source_type` is in `SOURCE_TYPES`; every example splits observations from facts;
  none asserts a folder path; three set `group_without_copying_facts: false` where membership would be
  invented.
- Every `falls_through_to.residual_template` is one of `00`'s nine residual homes.
- No threshold numbers, no confidence scores, no handling classes; `sensitivity` is
  `potentially_sensitive` only.
- Key set matches the landed `retail_hospitality` schema sibling, including `proposed_context_terms`.

## NEEDS-JOSEPH

1. **`NJ-GF-1` — the collapsed occasion level (sharpest; this row's own weak point).** For the platform
   export the schema default's middle level is unrecoverable. Alternatives: (a) site → channel →
   function, occasion optional — this pass's reading; (b) split the row into an export-shaped and a
   case-shaped situation; (c) declare the occasion level optional family-wide.
2. **`NJ-GF-2` — is `channel` a key or a medium?** If a medium, this row recommends `site` alone and has
   no second dimension. Must not be resolved by stretching `site` to swallow platforms.
3. **`NJ-GF-3` — the rubric test as a general rule.** Guest voice vs standards audit is discriminated
   here by an operator-authored rubric and an instructed assessor. The shape recurs as a supplier
   scorecard, a franchise brand-standards visit and a secret-diner programme. Decide whether the rule
   belongs to this row, to `store-operations`, or to `business_operations.compliance-audit` — and make
   all three say the same thing.
4. **`NJ-GF-4` — the moment a complaint becomes an HR matter.** Alternatives: hr claims every file naming
   an employee in an allegation (safe, but strips the guest's own letter out of its case); this row keeps
   the guest-facing half with hr's posture governing employee-identifying members (this pass's reading);
   or the packet routes wholesale to Protected Records and neither row groups it.
5. **`NJ-GF-5` — the public-source paradox.** Nothing in this phase can express *public content, private
   linkage*, and this row needs it more than any other in the family. Alternatives: P7 gains a
   linkage-aware class; the blanket `potentially_sensitive` stands and over-protects an anonymised score
   summary (this pass's reading); or the export is treated as ordinary, which this row recommends against.

## Final recommendation

Keep `retail_hospitality.guest-feedback` as a placeholder template with no fields, no serialised
dimensions and no schema coactivation. Recognise it by the paired utterance-and-response slot, the dual
date, the bounded-scale rating with its maximum stated, and the escalation-and-closure chain — never by
the word `review`, a star count, a platform name, or a person. Treat the collapsed occasion level as an
open structural question rather than a settled recommendation, and treat the public review as a linkage
risk rather than as public information.

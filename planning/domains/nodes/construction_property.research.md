# construction_property — gist research memo

Depth: GIST
Row: `construction_property` · kind `schema` · launch `placeholder` · absorbs the 27 legacy
`construction_property.*` rows listed at ROSTER.md Appendix A (`trade.*`, `cons.*`, `prop.*`).

## What this family is, in one paragraph

An OCCUPATION, not a topic. Somebody is instructed about a property that is not (necessarily) their
own: to price it, design it, build it, approve it, certify it, value it, sell it, let it or manage
it. The record that occupation leaves is unusually well-structured — a title block, a measured
works table, a valuation cycle, a conditions schedule, an apportionment schedule — and that
structure, not the vocabulary of buildings, is what makes the schema detectable. Any row on this
schema that cannot point at a structure of that kind is a document type wearing a domain's clothes.

## The posture this row sets for the family

The two parallel agents covering the rest of this schema inherit four decisions:

1. **The anchor is PROPERTY + INSTRUCTION.** Not property alone (that is the householder's world),
   not instruction alone (that is any professional's engagement). Both, in labelled slots, in one
   document.
2. **The default prose dimension order is property → instruction → document function**, with a
   period level only where the situation genuinely cycles. A sibling row whose whole life is one
   job may reverse the first two and should say so. No row declares a `dimension_order`: the schema
   declares no fields, so a dimension would branch on nothing (_CONTRACT rule 8 second half).
3. **The address is constitutionally never-alone**, on 00's own university-name reasoning. So is a
   firm name, a document-type word, a bare 4-digit number, an extension, and a money figure. A
   sibling row whose only evidence is one of those cannot activate and should be refused.
4. **Two boundaries are stated reciprocally and must not be re-litigated per row:**
   `finance.household-property` holds the householder's own home; `legal.leases-agreements` holds
   the operative instrument as protected legal material. This family holds the professional
   instruction around both.

## What this family deliberately does NOT cover

- A person's own home, its purchase, its tax, its improvements and its warranties —
  `finance.household-property`, which landed first and whose fixture
  `Kitchen Remodel - Bright Plumbing - Invoice 7841.pdf` is reproduced here as a negative example.
- An executed agreement held as the holder's own agreement record — `legal.leases-agreements`,
  whose fixture `Lease Agreement - 18 River Court - Signed.pdf` is likewise reproduced as a
  negative example. Legal protects first; this schema holds the management apparatus around it.
- A residents' or owners' association's own records — `finance.hoa-residents-association`. The
  professional managing agent's side is `construction_property.block-management`.
- An organisation's occupation of its own premises as part of running itself —
  `business_operations.facilities-workplace`.
- The authority's own side of a planning or permit decision — `government.planning-application`,
  `government.permit-licensing`.
- Rendered persuasion images about a building — `creative.architectural-visualisation`.
- A mortgage or a property loan as a serviced debt — `finance.loans-mortgage`.

## Sources used

`00-database-agent-product-design.md` (all quotations; every one matched mechanically before this
memo was written), `prompts/ALIGNMENT.md`, `domains/CONNECTION.md` (§2 node test, §4 activation,
§5 closed edges, §6 field identity, PR-6), `domains/_CONTRACT.md` (rules 6, 8, 10, 11–15),
`domains/canonical_fields.json` (37 keys, all `design` provenance), `overnight/council/DECISION-BRIEF.md`
(D1/D6/J-IND ratified), `domains/ROSTER.md` §4 + Appendix A, `domains/roster.json`, and the landed
sibling files `business_operations.json` (house standard), `business_operations.organisational-records.json`
(refusal standard), `business_operations.contract-administration.json` (template standard),
`finance.household-property.json` and `legal.leases-agreements.json` (nearest neighbours).

## proposed_fields justification

- **`property`** — new. The load-bearing hole. Argued in the JSON against `location`, `institution`,
  `venue`, `client` and `project`. Ceiling `possible`; destination-eligible proposed true with the
  privacy tension stated rather than resolved.
- **`instruction`** — new, and proposed *with its own alternative*: reuse canonical `project`. R1c
  should take the reuse if it can bear lettings and standing appointments, and drop this proposal
  entirely rather than ship both. Shipping both is D6's defect.
- **`organization`** — **not a new proposal.** Explicitly a reuse of the key the landed
  `business_operations` row already proposed, adjudicated once, there. Recorded here only to add
  the construction-side datum (one job, three custodies).

No other key is proposed by this row. `work_type`, `client`, `our_firm`, `location`, `event` and
`capture_year` are canonical and are referenced, never respelled.

## Files considered and rejected as examples

- A CV of a site manager (career), a payroll run for site operatives (hr), a CIS or subcontractor
  tax return (finance) — all real files in a builder's folder, none of them evidence of this schema.
- A structural engineer's calculation package: genuinely this world, but its detection is the title
  block and the specification already listed, so it added no new signal.
- A `.vcf` of site contacts: 00 requires contact data be privacy-protected rather than used to
  create folder proposals, so it can only ever be a file-kind signal here and would have been a
  misleading example.

## Neighbours considered that did NOT get an edge

- `career` / `hr` — the people who do this work are a different world entirely; no document family
  is genuinely confusable at the schema level, only at the row level (a site timesheet), and the
  row that owns timesheets is not mine.
- `academic` / `research` — an architecture dissertation shares vocabulary and nothing else; no
  shared evidence item, so no collision.
- `code` — BIM and parametric model files are structured data by format, but `design_creative` and
  `code_structured` are already separated by the file-kind list and no document is confusable.
- `photos.drone-captures` — a real overlap with site progress capture, but the row that owns
  progress photographs is not mine and authoring a one-way edge from the schema would pre-empt it.
  Recorded here for whoever writes it.

## NEEDS-JOSEPH (this node only)

- **NJ-CP-1** — does `property` become a canonical field key? Blocks every dimension order in this
  family.
- **NJ-CP-2** — construction job: reuse canonical `project`, or mint `instruction`? Pick one.
- **NJ-CP-3** — the professional/householder line is drawn on INSTRUCTION by this pass, not by
  `00`. A self-builder and a small landlord sit on it.
- **NJ-CP-4** — no `is_safety_domain` (correctly, `00` names four and this is not one), but the
  material carries third-party personal data routinely; the substitute mechanism that forces P7
  ahead of a model path needs a home. Same gap the landed `business_operations` row records.

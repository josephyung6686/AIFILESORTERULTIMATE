# Research memo — `government.international-development`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.international-development.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accepted, but only after the charge nearly landed.** The node survives on three legs that the domestic
government templates do not carry: a distinct results-chain-and-evaluation-criteria document grammar,
a four-cornered holder-role problem (funder / implementer / coordinator / host counterpart) where the
domestic rows have two corners, and a privacy rule that *inverts* the schema's dimension intuition by
forbidding delivery geography from ever becoming a folder level. `fields`, `proposed_fields`,
`dimension_order`, `also_holds_with` and `role_split` are all empty by contract.

## The charge — the strongest case that this row should not exist

I state it before the defence, at full strength.

**1. It is a work_type value that already exists on its own schema.** This is the sharpest attack.
`government.json` already enumerates, in `work_types[]`, the string *"intergovernmental agreement,
programme design, implementation, monitoring, evaluation, or public-accountability report"*. That is
this row's entire contents, already correctly filed as a **value** of a work-type field, not a node.
The dispatch prompt is explicit: "Work types are values. Do not ask R1a for a child node per work
type." On its face this row is exactly the 574's original mistake — promoting an enum member to an id.

**2. It is a duplicate of `government.grant-programme-administration`.** That row is defined as "A
funder's record of running a grant programme — the call, the applications received, assessment, award
and monitoring of the money it gives out." A development programme's lifecycle is design → appraisal →
award → implementing agreement → monitoring → evaluation → closure. Every stage maps. If two templates'
detection signals differ only by the *destination of the money*, one of them should not exist.

**3. The only difference is geography, and geography is a value.** "Delivered in another country" is a
value of a location concept. The schema's own `never_alone` already rejects place as evidence and its
`open_question` records that jurisdiction was not admitted as a field. A row whose differentia is a
country name is a row built on never-alone evidence.

**4. It is a row defined by an ABSENCE — "not domestic."** International development is what is left of
public administration once you subtract the funder's own territory. Rows defined by the absence of
something are the forbidden shape.

**5. It is an organisation-name row.** USAID, FCDO, GIZ, UNDP, the World Bank, ICRC. If the honest
detection signal is "a donor agency's letterhead", the row can never activate, because the schema's
`never_alone` already says a public body's name alone proves nothing.

**6. It is the mirror of `nonprofit.grant-reporting` seen from the other side** — and the roster already
has that row, so the coverage is not orphaned if this one is refused.

## The defence — leg by leg, and where it is weakest

### Leg 1 — detection signals differ from the government default template

This is the leg that actually carries the node, and it does so on **document grammar**, not on topic
words or place names. Four real, named artefact structures exist in this world and in no other roster row:

- **The results matrix.** A logframe or results framework is a spreadsheet whose axis labels are a
  closed vocabulary: impact/goal, outcome, output, activity on one axis; indicator, baseline, milestone,
  target, means of verification, assumptions on the other. This is a *structural* signal — the shape of
  the sheet, readable without reading the content, and without knowing which country is involved.
- **The DAC evaluation-criteria heading set.** An evaluation report whose top-level headings are
  relevance, coherence, effectiveness, efficiency, impact, sustainability — accompanied by terms of
  reference and a management-response matrix. No domestic template on the roster carries that heading set.
- **The transparency publication.** An IATI activity file is XML against a published open standard whose
  element vocabulary (activity, activity identifier, reporting organisation, recipient country, sector,
  transaction, result) is documented externally. This is a `validated` rule family in the sense the
  prompt means — a documented element set to check against, not a regex I invent. `government.json`
  has no `code_structured` fixture at all; this row does. That is a difference in `file_kinds`, not
  only in prose.
- **The DAC/CRS statistical return** — columns for purpose code, channel of delivery, aid type, tied
  status, flow class, commitment and disbursement.

None of these are extensions, none are work-type words, and none is a country. That defeats charge 3
and charge 5 directly: the row's activation floor is a *matrix shape and a heading set*, and the
`never_alone` list I wrote explicitly forbids donor name, country name, and aid vocabulary from firing
anything on their own.

**Where this leg is weak, stated honestly.** The results-matrix grammar leaks. Domestic foundations,
public-sector strategy units and charities use theories of change and results frameworks freely. I
handled this by requiring the matrix to carry a programme anchor that repeats elsewhere, and by making
`Theory of Change - Youth Employment - draft.pptx` a fixture that must NOT fire. The grammar alone is
insufficient; the grammar plus a cross-border delivery instrument or a funder-side programme anchor is
the actual floor.

### Leg 2 — the recommended dimension recommendation differs, by prohibition

The government schema's `template.why` says the order should be "authority-side function or bounded
proceeding/case/programme first". For a cross-border portfolio, the *obvious* first cut is country —
that is how aid agencies genuinely organise shared drives. This template says **no**, and says so as a
standing prohibition: delivery country, administrative area, site, camp, community and beneficiary
identity must never become folder levels. That is not the schema default restated; it is the schema
default with a carve-out that reverses the intuitive answer, and it survives even if a location concept
is later made canonical for other rows. A recommendation that contradicts what the world's practitioners
actually do is a real template difference, not a restatement.

Both the schema and this row keep `dimension_order: []` because PR-6 leaves the schema fieldless. So this
leg differs in *content* while being identical in *serialization* — a genuine weakness I record rather
than hide. It is why leg 3 has to do work.

### Leg 3 — the privacy rule differs materially

The government schema's `sensitivity_why` protects citizen casework: people who hold a legal relationship
with, and a remedy against, the authority holding their file. This row's protected population is
different in kind — assisted households, local partner staff, safeguarding complainants and evaluation
respondents, typically non-nationals of the funder's state, frequently in conflict- or repression-affected
settings, and typically with no remedy against the funder at all. The concrete consequences are three
that the domestic rows do not need:

1. **Location is a threat vector, not a convenience.** A settlement name in a branch label, or a GPS
   column in a registration sheet, can locate an assisted population. Hence the dimension prohibition.
2. **Small-denominator aggregates are not anonymous.** "Aggregate it before summarising" is a safe
   instinct domestically and an unsafe one here; the fixture `Post-Distribution Monitoring Report` records
   that site codes must not be resolved and that anonymised quotes are not licences.
3. **Association is itself sensitive.** Partner affiliation, assistance status and complainant status can
   be dangerous facts independent of content. `Safeguarding Incident Report` and
   `Security Incident and Duty of Care Log` exist as fixtures for exactly this.

The binding design constraint is quoted verbatim in the node: "Privacy policy must be enforced before
content reaches any model or external connector," and protected material "should normally remain
local-only and must not cause filenames or content to be exposed in model prompts."

### Answering charge 1 and charge 2 directly

**Charge 1 (work-type value).** Conceded in part, and it is why the row is *narrower* than its name.
"Programme design", "monitoring", "evaluation" ARE work types and are serialized as such in
`work_types[]`. The node is not those words. The node is the **bounded funded programme as a filing
situation** — one anchor binding a design, an instrument, a results chain, delivery reporting, an
evaluation and a closure into one packet whose members must not inherit each other's facts. That is an
organisational situation, which is what a template is. The test I applied: if I deleted every work-type
word from the row, would anything remain? Yes — the matrix grammar, the criteria heading set, the
transparency element vocabulary, the role triangle and the geography prohibition all remain.

**Charge 2 (duplicate of grant-programme-administration).** This is the one I came closest to refusing on,
and the boundary is stated reciprocally below on shared fixture bytes. The discriminator that survived is
**not** geography: it is that grant administration owns the *competition* (call, received applications,
scoring against published criteria, award letter, standard monitoring return) while this row owns the
*delivery instrument and its accountability chain* (results annex, drawdown profile, safeguarding and
duty-of-care schedules, criteria-based independent evaluation, transparency and DAC statistical return).
The proof that geography is not doing the work: a **domestic** grant with a logframe attached stays with
grant administration, and a **direct contribution** to a multilateral with no competition at all still
belongs here.

**Charges 4 and 6.** Charge 4 fails once the row is defined positively by artefact grammar rather than by
"not domestic". Charge 6 fails because `nonprofit.grant-reporting` is the *recipient's obligation* to a
funder — it cannot hold the funder's appraisal, its due-diligence assessment of that same partner, its
review scoring of that partner, or its statistical return; those files have no home under it.

## Files considered and REJECTED — the tempting false positives

Each of these was a candidate for this row and is not this row's evidence.

1. **`Evaluation of the Country Programme - Republic of X - published.pdf`** — the **collision fixture**
   (below). Kept as a fixture precisely so the row cannot claim it.
2. **`Theory of Change - Youth Employment - draft.pptx`** — a domestic charity's results chain. Same
   grammar, no instrument, no cross-border party, no transparency identifier. Not this row.
3. **`Grant Award Letter - Community Resilience Fund 2026 - Ref CRF-118.pdf`** — domestic funder-side
   grant administration. The reciprocal fixture against `government.grant-programme-administration`.
4. **`Offer of appointment - Programme Manager, Country Office.pdf`** — aid sector as *employer*. The
   schema's `never_alone` already rejects "a public-sector employer name on a person's resume, payslip,
   contract, or calendar"; this row extends the same rule to duty stations, deployment letters, R&R
   schedules, per-diem claims and mission visas.
5. **A bidder's tender response for an aid contract** — held by the bidding consultancy or NGO. That is
   the supplier side; the buyer side is `government.public-procurement`. Not represented as a fixture
   because it would have duplicated the procurement row's own collision work.
6. **A researcher's field-study dataset from a development evaluation** — same countries, same indicators,
   same respondents. Research owns knowledge production; this row owns funded delivery. An evaluation
   commissioned by the funder with a management response is mine; the same team's journal article is not.
7. **A published Humanitarian Needs Overview or Response Plan downloaded for reading** — falls to
   Reading Inbox. Publication by a coordination body is not custody.
8. **An SDG-branded corporate sustainability report** — same vocabulary, entirely different world.
   Rejected by the `never_alone` clause on aid vocabulary.
9. **A blank logframe template or reporting-form workbook** — grammar with no programme is stationery.
10. **A country-office live case-management or grants database** — a source system, not a file node. A
    bounded export with a readable manifest is represented (`Programme closure and asset disposal.zip`);
    live ingestion is a later connector and security decision.

## The collision fixture

**`Evaluation of the Country Programme - Republic of X - published.pdf`.**

This file looks *exactly* like this row's strongest positive fixture. It carries the full DAC criteria
heading set, a donor's name and branding, a delivery country, indicator tables and recommendations. A
naive detector fires on it with high confidence.

It is not this row's evidence. **What discriminates it:** the commissioned evaluation carries a
commissioning block naming the funder's evaluation function, terms of reference, a draft-and-comment
history, and a **management-response matrix with named owners and dates** — the artefact by which the
funder accepts or rejects each recommendation. The published copy has an ISBN-style publication block and
an open-licence notice, and has none of the commissioning or response furniture. It also arrived in a
browser download folder with unrelated PDFs, and "A session should never be treated as proof of topic."
It routes to Reading Inbox.

Two supporting collision fixtures do the same work in other directions: the domestic
`Grant Award Letter` (against grant administration) and the
`Country political and economic reporting` cable (against diplomatic-consular).

## Reciprocal boundaries — both directions, same fixture bytes

Five collisions are authored. Each names the fixture that competes.

**`government.grant-programme-administration`** — shared bytes: an award/grant instrument plus a
monitoring calendar. *Toward them:* a funder-side award with conditions, payment profile and standard
returns, no results annex and no safeguarding or duty-of-care schedule, is theirs even if the grantee
works overseas. *Toward me:* an instrument whose schedules carry a results annex, drawdown profile,
safeguarding/PSEA and duty-of-care clauses and a cross-border delivery party is mine even if there was
no competition. Fixture on both sides: `Grant Award Letter - Community Resilience Fund 2026` (theirs)
versus `Accountable Grant Arrangement - Partner Consortium - 300412 - signed.pdf` (mine).

**`nonprofit.grant-reporting`** — shared bytes: the agreement and the quarterly financial report /
drawdown claim. *Toward them:* the same `Quarterly Financial Report and Drawdown Claim Q2 - 300412.xlsx`
held by the reporting partner, alongside its variation request and monitoring-visit response, is theirs.
*Toward me:* the same bytes held by the funder, alongside its due-diligence assessment of that partner
and its annual review scoring, are mine. Where an implementing partner is itself a public body passing
money downstream, both roles are genuinely present — see NJ-3.

**`government.emergency-management`** — shared bytes: a numbered situation report with affected-population,
response and gaps sections. *Toward them:* a domestic authority's civil-protection response over its own
territory, with statutory responder roles. *Toward me:* externally funded assistance into another state
via an appeal or contribution instrument, cluster/sector coordination and international funding-status
reporting. Fixture: `Situation Report 14 - Flood Response - 2026-08-19.pdf` is genuinely ambiguous on its
face and is resolved only by the instrument and the coordination structure.

**`government.diplomatic-consular`** — shared bytes: a country-strategy or portfolio document produced at
post. *Toward them:* representation, host-state engagement, political/economic reporting, assistance to
nationals. *Toward me:* the spend and its accountability. Fixture:
`Country political and economic reporting - Republic of X - Q3.docx` mentions the aid portfolio and is
still theirs.

**`business_operations.project-delivery`** — shared bytes: a risk register and a milestone report carrying
one programme reference. *Toward them:* artefacts terminating internally, an organisation controlling its
own work. *Toward me:* artefacts terminating outward at a funder or the public — results-chain reporting,
criteria-based independent evaluation, transparency publication, DAC return. A management contractor
running an aid programme holds both; neither erases the other.

## Neighbours considered that did NOT get an edge

- **`legal`** — implementing agreements, MOUs and host-country agreements are legal instruments, and the
  `Accountable Grant Arrangement` fixture records `also_schema: legal`. The schema already collides with
  `legal`; restating it here would add nothing and would drift toward a treaty taxonomy.
- **`government.public-procurement`** — aid is delivered by contract as often as by grant, so a supplier
  contract for an aid programme is genuinely both. I did not author the edge because the discriminator
  would be identical to the grant-administration one (competition versus delivery instrument), and
  duplicating it inflates the row without adding a distinction. **Recommendation to R1c:** if the
  procurement row's own research finds the same-bytes overlap, add the reciprocal edge there.
- **`government.public-health-administration`** — immunisation and outbreak programmes delivered as aid
  overlap, but the discriminator is the same funder/implementer role question already carried against
  `nonprofit.grant-reporting`.
- **`nonprofit.advocacy-campaign`** and **`nonprofit.fundraising-donor`** — development-sector charities do
  both, but neither shares this row's artefact grammar.
- **`finance`, `career`, `photos`** — recorded as `also_schema` on individual fixtures (the drawdown claim,
  the offer of appointment, the portal screenshot) rather than as schema-level coactivation, following the
  `legal.practice-matter-file` precedent that a template on a fieldless schema cannot author
  `also_holds_with`.

## Fields, dimensions and proposed_fields

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false` — all intentional under
PR-6 and D1. Candidates considered and rejected rather than minted: a programme or activity identifier, a
funding instrument, a delivery country, an implementing partner, a lifecycle phase, a results level, a
sector or purpose code. Every one of them is a genuine organising concept in this world and **none** is
canonical. The location candidates are refused twice over — once because they are not canonical, and once
because this template affirmatively argues they must never be destination-eligible even if they later become
canonical for other rows. That prohibition is carried in `template.why` and in NJ-1 so it survives adjudication.

`also_holds_with: []` and `role_split: []` for the same fieldless reason. The funder/implementer split is a
textbook `role_split` and cannot be written; see NJ-2.

## Honest limitations

`00` contains **no** occurrence of the words "humanitarian", "monitoring" or "logframe" — I grep-verified
this. The design document says nothing about international development. Every substantive claim in this row
is therefore `proposal` provenance, resting on named real artefact types rather than on design text, and the
only verbatim `00` spans used are the general ones about evidence, sessions, EXIF, extensions, dimension
order, privacy enforcement and the residual definitions. I have not smoothed that over: the row's
`provenance` is `proposal`, and `design_cite` is `null`.

Practice varies enormously between bilateral donors, multilaterals, development banks and humanitarian
actors. The artefact grammars named here (results matrix, DAC criteria set, transparency element
vocabulary, DAC/CRS columns) are the ones that recur across all of them; I deliberately did not enumerate
any single donor's house templates, which would have turned a placeholder into the industry catalogue
J-IND forbids this round.

## NEEDS-JOSEPH

**NJ-1.** If PR-6 is lifted, adjudicate centrally whether a bounded programme/response reference may exist
and be destination-eligible. *Alternatives:* (a) admit a programme anchor as a destination dimension and
explicitly blacklist delivery country, administrative area, site and beneficiary community from ever being
destination-eligible for this template; (b) admit a location concept generally for other rows and rely on
per-template suppression; (c) admit nothing. This row recommends (a) and considers (b) unsafe, because a
general location dimension will be applied here by default unless the prohibition is written at
adjudication time rather than left to the template.

**NJ-2.** `role_split` requires differing field keys and the schema has none, so the funder/implementer
split — the single most important structural fact about this world — is expressible only as a
`collides_with` against `nonprofit.grant-reporting`. *Alternatives:* (a) R1c defines a fieldless
`role_split` idiom usable across placeholder schemas; (b) the split stays as reciprocal collisions and is
revisited when fields land. Whichever is chosen should be applied uniformly, since `legal.practice-matter-file`
hit the same wall independently.

**NJ-3.** Decide the delegated-cooperation case: a public body that implements another donor's programme is
simultaneously an authority and a grantee. *Alternatives:* (a) both this row and `nonprofit.grant-reporting`
activate, with the packet protected under the stricter posture; (b) holder-role evidence picks exactly one;
(c) the case routes to Review Later until a user confirms. This row's fixtures assume (a) is at least
permissible but do not serialize it, because a template cannot author schema coactivation.

## Self-verification

- `python3 -m json.tool` parses the node; key set matches `government.json` and the landed launch rows.
- Every `design_cite` and every quoted span in the JSON and this memo was grep-verified verbatim against
  `planning/00-database-agent-product-design.md` before being written, including the Temporary Screenshots
  residual sentence (an initially mismatched cite was corrected).
- All five `collides_with` ids confirmed present in `planning/domains/roster.json`; all
  `falls_through_to` names are `00` residual homes.
- Every `file_examples.source_type` is in `SOURCE_TYPES`; no file example writes a folder path as a fact;
  no threshold number, confidence score or handling class appears.
- At least one `never_alone` is true of a tempting false file (country name → the published country
  evaluation; results-chain grammar → the domestic theory of change; aid-sector employer → the offer of
  appointment).
- Files written: only `government.international-development.json` and this memo.

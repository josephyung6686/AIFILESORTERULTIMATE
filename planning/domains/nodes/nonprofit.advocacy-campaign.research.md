# Research memo — `nonprofit.advocacy-campaign`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/nonprofit.advocacy-campaign.json`
Roster row: template on the fieldless `nonprofit` schema, `parent_id: null`, placeholder launch
Result: **REFUSED** (`refuse_node: true`) — JSON already argued; this memo completes the pair. Refusal **not** reversed.

## Result in one paragraph

Refuse, and keep the refusal. An organised effort to change a decision or policy is a **purpose** and an enumerated `work_types[]` value on the `nonprofit` schema, not a filing structure that differs from that schema's default. Every artefact the roster hint named — strategy, briefings, submissions, media, supporter mobilisation, outcome — is either byte-for-byte a `business_operations.go-to-market` / strategy-plan / meeting-record shape with different nouns, a registrant-to-regulator filing already owned by `business_operations.corporate-regulatory-filings`, a creative production asset already owned by `creative.ad-campaign` / `creative.content-marketing`, a register the parent schema already claims for donor-and-supporter and membership structures, or a grant report that fires the schema's own restricted-grant lifecycle on the grant reference. Critically, the characteristic campaign packet evidences **no non-exchange party** — no funder–grantee relation, no donor, no member, no volunteer, no named beneficiary in its own right — which is the entire activation precondition of the `nonprofit` schema. The row therefore fails the schema's activation gate **and** duplicates the schema's default **and** is a value of the schema's own work-type enum. Coverage routes to named neighbours and five residual templates; nothing is lost by refusing.

## Status of this salvage

The JSON already existed with `refuse_node: true` and a long `refuse_reason`. There was no `.research.md`. This pass writes the matching J-DEPTH memo only. The JSON was parse-checked and contract-checked; **no JSON edit was required**. The refusal is documented, not re-litigated into a keep. Padding the row to save the absorbed legacy id `civic.community-organising` is explicitly rejected — inventing a node to save a legacy id is the 574's original mistake, and the brief names it as such.

**Family context (handoff Step 4).** `nonprofit` has refused 5 of 9 templates on the same anchor-precondition issue (advocacy-campaign, governance, political-campaign, standards-body, volunteer-management). The schema's non-exchange two-party gate is load-bearing; siblings that cannot name such a party fail the same way. **R1c settles the anchor once** — either it is drawn correctly and these refusals stand, or it is too tight and coverage belongs on `business_operations` plus residuals. This memo does not re-fire the five; it completes the pair for this refused id and surfaces the family question as NJ-AC-FAMILY below.

## Sources used

- `planning/42-HANDOFF-FINISH-THE-CATALOGUE.md` § Step 4 (family-level question, not five row failures) and failure-mode warning against re-firing refused ids without settling the anchor.
- `planning/domains/dispatch/RESEARCH-BRIEF.md` (in full) and the stamped R1b prompt from `make_prompt.py nonprofit.advocacy-campaign`.
- `planning/domains/nodes/nonprofit.advocacy-campaign.json` — the existing refused JSON; this memo argues from it, not against it.
- `planning/domains/nodes/nonprofit.json` — the schema anchor, read for `recognition` precondition, `work_types[]` (including the campaign/advocacy/lobbying value), default template prose, `grouping_reasons`, NJ-NP-4 (campaigning-advocacy named WEAK), and residual ordering.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — landed launch row for depth calibration.
- `planning/domains/nodes/business_operations.organisational-records.research.md` — exemplary refusal quality (charge first, three legs, collision fixture, residual routing).
- Sibling refused memos in this family, for idiom and for the shared precondition failure: `nonprofit.standards-body.research.md`, `nonprofit.governance.research.md`, `nonprofit.political-campaign.research.md`, `nonprofit.volunteer-management.research.md`.
- Neighbours named in fixtures / must_consider: `business_operations.go-to-market`, `business_operations.corporate-regulatory-filings`, `business_operations.meeting-record`, `government.public-consultation`, `creative.ad-campaign`, `creative.content-marketing`, `finance` — ids confirmed on `planning/domains/roster.json`.
- `planning/00-database-agent-product-design.md` — reached by targeted grep. Quotations embedded in the JSON were checked; residual-template and purpose/packet spans match verbatim. Two short spans in the JSON ("campaign, advocacy and lobbying…" and CONNECTION's work-type ban) are from the schema / CONNECTION, not from `00`, and are not presented as `00` quotes.

`CONNECTION.md` §2 (node test), §5 (`also_holds_with` is schema ↔ schema only), and `_CONTRACT` fieldless rules applied as in the dispatch.

---

## The charge — the strongest case that this row should not exist

Stated first. It is the finding.

**(1) It is a work_type value, not a node.** The schema anchor already enumerates *"campaign, advocacy and lobbying record where a registration or disclosure structure exists"* inside its own `work_types[]`. CONNECTION §2 closes promotion of values to nodes: a value is not a roster node, and the design forbids "never a schema per work type." `advocacy campaign` is what a campaign plan's own purpose field would say — Homework 3, not academic.

**(2) It fails the schema's activation precondition outright.** The `nonprofit` schema states its precondition as "the whole schema": every accepted signal must evidence a **non-exchange relation between two labelled parties** — money or labour given without commensurate return, or service to a named non-paying person. A campaign strategy deck, a placard kit, a consultation response, a lobbying return, and a flyer name at most an organisation and a policy target. They name no funder, donor, member, volunteer, or beneficiary *as parties to a non-exchange relation*. A row whose flagship evidence cannot fire its own schema is not a template on that schema. This is the same harder-than-leg-1 failure `nonprofit.standards-body` recorded: distinctive-looking evidence that cannot activate the parent.

**(3) It duplicates landed neighbours and the schema default with nothing left over.** Campaign strategy section grids → `business_operations.go-to-market` (objectives, audiences, messaging, channels, timeline, metrics — `decision-maker` substituted for `buyer`). Lobbying registrations / quarterly activity returns → `business_operations.corporate-regulatory-filings` (registrant → regulator). Consultation responses → respondent-side instruments against `government.public-consultation`. Press and social kits → `creative.content-marketing` / `creative.ad-campaign`. Supporter / petition exports → the register structure the parent schema already claims. Grant-funded campaign outcomes → the schema's restricted-grant lifecycle on the grant reference. Meeting notes with officials → `business_operations.meeting-record`. Invoices for agency retainers → `finance` (exchange). Nothing remains that is both nonprofit-activable and structurally distinct.

**(4) The schema already pre-registered the weakness.** NJ-NP-4: *"campaigning-advocacy is WEAK because a campaign plan is go-to-market with different nouns and a lobbying registration is a regulator filing"* and *"If ten rows are required, the three weak ones should be refused rather than invented."* This pass treats that as corroboration, not as a substitute for the node test — and the node test fails independently.

**(5) Topic and audience are not structure.** The only residue after neighbours take their share is the word `campaign` and a political-rather-than-commercial target audience. Topic is not purpose (`00`: documents can be content-incoherent but purpose-coherent). Audience identity is a value. Neither saves a node.

**Can the charge be defeated?** Three survival candidates were run. All failed. See below.

---

## Survival candidates — attempted, and each fails

**1. The campaign strategy deck as a distinct structure.** Tempting: a real artefact with a stable section grid. Failed because the collision fixture (`Campaign plan - Q3 product launch.pptx`) carries the **identical** grid under a commercial logo. Nothing structural separates Right-to-Repair advocacy from a product launch except audience identity and the presence or absence of pricing slides — and audience is a value. Activating nonprofit on that shape would pull every corporate go-to-market plan onto the nonprofit schema on the word `campaign` alone. That is the expensive error the refusal avoids.

**2. Lobbying registration / disclosure as the nonprofit-shaped residue.** Tempting because the schema's work_types clause mentions "where a registration or disclosure structure exists." Failed because that structure is registrant-to-regulator — the whole of `business_operations.corporate-regulatory-filings`. Charitable registrant status is tax status, which the schema strikes as never-alone. The work_types clause describes a *value of work*, not a licence to steal a neighbour's relation.

**3. The petition / supporter register as the non-exchange party.** Tempting because a named-person register looks like the family's donor/member structures. Failed because (a) the register is already the schema's default for supporter and membership rows — a template cannot differ from a default by being that default; (b) a petition export alone does not evidence gift, subscription, unpaid labour agreement, or beneficiary service — it evidences a list; (c) the campaign *label* on the register is the never-alone token, not a second structure. The register is the evidence; the campaign is the label on it.

Three candidates, three failures. The charge stands. Refuse.

---

## The node test, all three legs

CONNECTION §2: a **template** row exists only if its detection signals, recommended dimensions, or privacy rules differ from its schema's default template. Disjunctive: one pass would save it. A refusal must fail all three.

**The schema's default, stated so difference can be measured.** Detection: non-exchange precondition plus named structures (restricted grant, restricted fund, donation-with-declaration, membership register, beneficiary case, safeguarding, volunteer programme, faith rite). Dimensions: empty `dimension_order` under PR-6; prose order is association → non-exchange counterparty or fund (grant, restricted fund, appeal, membership class, case, register) → period → document function; never a named vulnerable person as a folder level; `time_first: false`. Privacy: `potentially_sensitive` at maximum catalogue strictness, argued on third-party exposure and affiliation disclosed by the record's mere existence.

### Leg 1 — detection signals. FAILS (twice)

**Fails as identity with the default** wherever a campaign artefact can fire the schema at all: a supporter CRM export is the register structure; a grant report with a repeated grant reference is the restricted-grant lifecycle; a volunteer mobilisation rota (if one existed as unpaid labour with a non-employment agreement) would be the volunteer default. Those are schema defaults / sibling territory, not a distinct advocacy template.

**Fails harder — cannot reach the precondition —** for the artefacts that actually make "advocacy" look like a world: strategy decks, briefings, placards, press releases, consultation responses, lobbying returns, flyers. None labels two parties in a non-exchange relation. An organisation name + campaign vocabulary + a named politician or bill is exactly the never-alone set the schema and this row both strike. Same shape as governance minutes and standards drafts in sibling refusals: what looks distinctive cannot activate `nonprofit` at all.

### Leg 2 — recommended dimensions. FAILS (twice)

Formally: schema declares no fields; this row declares none; both serialise `dimension_order: []`. Two empty orders cannot differ (_CONTRACT rules 10 and 15, PR-6).

Substantively: even if fields existed, the order a campaign corpus wants is organisation → initiative/campaign name → period → document function — the parent schema's prose with *"the grant, the restricted fund, the appeal"* replaced by *"the campaign"*. That is a **value substitution inside an existing order**, which CONNECTION §2 names as not-a-node. Campaign-first is also period/initiative-first without a non-exchange counterparty at level two — the load-bearing level of the family default is unfillable. Not time-first: `00` prefers project/function/subject before time for document domains, and campaign periods are content periods, never capture dates. Adopting `business_operations.go-to-market`'s order instead would be the standards-body finding again: differing from your parent by adopting another schema's default is evidence of being on the wrong schema, not of being a node.

### Leg 3 — privacy rules. FAILS (same or weaker, not stricter)

A supporter, signatory, or petition list is a register of named third parties whose political affiliation is disclosed by the record's existence — exactly the third-party-exposure argument the parent schema already makes at full strength for donor, member, and beneficiary registers. Meeting notes naming officials and internal strategy about opponents can harm identifiable people if exposed; `00`'s default posture applies unchanged ("The default posture must therefore be local-first and data-minimizing."). The posture is **identical to or inherited from** the schema default, not stricter than it. A privacy rule that only applies to files the schema cannot activate on (or that the schema already covers as registers) is a residual-routing concern (Protected Records), not a leg-3 pass. The JSON correctly keeps `potentially_sensitive` so the refusal does not downgrade material it routes away.

Three legs, three failures. Refuse.

---

## Files considered and rejected

Twelve fixtures are in the JSON with full observations. What each taught:

1. `Campaign strategy - Right to Repair - v3.docx` — the flagship candidate. Section grid + charity footer + legislator Ask table. **Must not conclude** nonprofit activation: no funder, donor, member, volunteer, or named beneficiary appears. Falls to Independent Records if alone.
2. `Campaign plan - Q3 product launch.pptx` — **THE COLLISION FIXTURE.** Identical grid under a company logo. Discriminator is audience identity / revenue slides — values, not structure. Also `business_operations`. Review Later when side is unresolved.
3. `LD-2 Q2 2026 lobbying activity report.pdf` — registrant-to-regulator labelled slots. Whole relation is `business_operations.corporate-regulatory-filings`. Charitable registrant does not relocate it.
4. `Consultation response - waste strategy - FINAL.docx` — respondent-side instrument; same shape filed by companies and councils. `government.public-consultation` seam (see NJ-AC-1). Charitable respondent status is never-alone.
5. `Petition signatures export - 2026-07-14.csv` — register of named third parties. Schema's own register structure / Protected Records. Not a reason to mint a campaign node.
6. `Press release - embargoed 00-01 12 Aug 2026.docx` — embargo, dateline, boilerplate, press contact. `creative.content-marketing` owns the production structure regardless of political message.
7. `Campaign social kit - placards and story frames.zip` — archive inspected by manifest only; `creative.ad-campaign`. Slogan inside an asset is not a campaign fact on the archive.
8. `Meeting note - 2026-06-03 - Cllr Adeyemi.docx` — Attendees / Actions structure. `business_operations.meeting-record`. Meeting a politician is not a distinct filing world.
9. `Grant report - GT-2024-118 - campaign outcomes - final.docx` — grant reference + outcome-against-agreement. Schema's restricted-grant lifecycle; "campaign" in the narrative is a label, not the structure.
10. `Save Elm Street Library - public meeting flyer.pdf` — date, venue, CTA; no second party. Absorbed legacy `civic.community-organising` does not rescue it; Independent Records.
11. `Public affairs agency retainer - invoice 2026-041.pdf` — exchange (value for value). Exactly what the nonprofit schema excludes. `finance` / Receipts and Confirmations.
12. `Coalition briefing - clause 12 - for MPs.pdf` — logo strip of several charities is a set of organisation names (canonical never-alone). Structure is a position paper / Reading Inbox, not a non-exchange relation.

**Additional false friends considered, not given JSON slots:** manifesto or policy paper as topic reading (Reading Inbox); downloaded think-tank report co-located in a "Campaign" folder (`00` forbids download-session-as-topic; folder label is user structure); password-protected CRM export (Unsupported or Encrypted — filename manufactures no side); corporate ESG "advocacy" slide in an annual report (`business_operations`, mission vocabulary never-alone).

---

## The collision fixture (decisive)

`Campaign plan - Q3 product launch.pptx` beside `Campaign strategy - Right to Repair - v3.docx`.

Same headings: Objectives, Target audiences, Key messages, Channels, Timeline, Success measures. Same "Ask" column habit against named targets. One has a company logo and account list; the other has a charity number and legislator list.

**What discriminates them is not a filing structure.** It is the identity of the audience and whether pricing/revenue slides appear. Audience is a value; commercial vs political topic is a topic. A detection rule that fired nonprofit on the charity-numbered copy would be one never-alone token away from firing on the product-launch copy. Refusing is cheaper than inventing: an activated advocacy node would pull corporate go-to-market plans onto the nonprofit schema on the word `campaign` alone.

Secondary collision: `LD-2 Q2 2026 lobbying activity report.pdf` looks like "advocacy evidence" and is not — it is a periodic statutory disclosure. Discriminator: labelled registrant/client/period/agency slots and a certification block = regulator relation, not non-exchange.

---

## Reciprocal boundaries (recorded for R1c; JSON edges empty)

A refused row authors no `collides_with` / `also_holds_with` edges, following the organisational-records exemplar and CONNECTION §5 (also_holds is schema ↔ schema; this is a template). Boundaries stated here with the same fixture on both sides:

- **`business_operations.go-to-market`** — `Campaign strategy - Right to Repair - v3.docx` / `Campaign plan - Q3 product launch.pptx`. Neighbour owns the grid in both directions; this refusal removes the competing claim. Reverse: go-to-market must not treat a charity footer as out-of-scope for the same grid.
- **`business_operations.corporate-regulatory-filings`** — `LD-2 Q2 2026 lobbying activity report.pdf`. Owns registrant→regulator for charitable registrants too (NJ-AC-2). Reverse: already the schema's stated cession.
- **`business_operations.meeting-record`** — `Meeting note - 2026-06-03 - Cllr Adeyemi.docx`. Owns meeting structure; politician-as-attendee is a value.
- **`government.public-consultation`** — `Consultation response - waste strategy - FINAL.docx`. Authority-side rows were written from the authority; respondent copy seam is NJ-AC-1. This refusal does not annex the respondent copy.
- **`creative.ad-campaign` / `creative.content-marketing`** — social kit / press release. Political message does not relocate production structure.
- **`nonprofit` (schema default) / fundraising & membership siblings** — petition export and grant-funded outcome report. Register and grant lifecycle stay on the schema / landed siblings; this row adds no third structure.
- **`finance`** — agency retainer invoice. Exchange relation; schema excludes it by construction.
- **`nonprofit.political-campaign`** (also refused) — electoral statutory machinery vs issue advocacy. Two refused rows cannot hold each other up; both route lobbying disclosure and campaign plans to the same business_operations / creative / residual homes. Sibling political-campaign memo already noted advocacy as weak on go-to-market grounds.

Intent that would have been `also_holds_with` if this were a schema: none that the parent `nonprofit.json` does not already carry. Nothing lost by empty edges on this template.

---

## Grouping and fallthrough

No grouping axis survives that is not a neighbour's. A campaign group formed by a repeated campaign **name** is never-alone organisation/label evidence — it merges a company's product campaign with a charity's policy campaign when words coincide, and merges unrelated coalitions that share a slogan. Where a real group exists, a landed neighbour forms it on stronger evidence: one GRANT on a repeated grant reference; one go-to-market MOTION on a launch identifier; one CONSULTATION on consultation reference and closing date; one REGISTRATION PERIOD on registrant and quarter; one CREATIVE JOB on brief and revision chain.

`00` stop rule: "The graph does not automatically copy those missing facts onto sparse files." A campaign name read off a strategy deck must not be copied onto the press release, invoice, placard, or signature export beside it. Once it cannot be copied, the only binder is the user's folder — user structure, not a node.

**`falls_through_to` (five residuals, all from `00`):** Independent Records (principal home for standalone purposeful documents); Reading Inbox (sector papers, model briefings, cuttings); Review Later (side-unresolved campaign-shaped plans — the collision); Protected Records (supporter/signatory lists); Receipts and Confirmations (agency invoices, venue bookings, print receipts). Ordering differs from the schema's Protected-first default because the *characteristic* refused advocacy artefact is a standalone purposeful document, not an isolated vulnerable case note — but Protected remains named so register exposure is not downgraded.

---

## Fields

`fields: []` and `proposed_fields: []`. Schema declares none under PR-6. A refused row must not leave field proposals for R1c to adjudicate on behalf of a node that should not exist. Keys this corpus might want (`campaign_name`, `policy_target`) would be purpose/topic labels or synonym mints of `organization` / existing proposals; not proposed.

---

## Absorbed legacy coverage

Roster hint absorbs `civic.community-organising`. Coverage after refusal: `business_operations.meeting-record` (organiser meetings), Independent Records (flyers and standalone notices), Reading Inbox (downloaded organising guides), Protected Records (sign-up sheets with named people), Receipts and Confirmations (venue/print receipts). That is sufficient; reopening the row solely to retain the legacy id is NJ-AC-3's rejected alternative (b).

---

## NEEDS-JOSEPH

**NJ-AC-FAMILY — family-anchor question (handoff Step 4; settle once).** `nonprofit` has refused five of nine templates (advocacy-campaign, governance, political-campaign, standards-body, volunteer-management) on the same structural point: the schema's activation precondition requires a non-exchange relation between two labelled parties, and those five worlds' distinctive artefacts either cannot name such a party or only activate by being the schema's own default structures. Alternatives for R1c: **(a)** affirm the anchor as drawn — the five refusals stand, and coverage stays on `business_operations` templates plus residual fallthrough (this row's recommendation, and each refusal's own routing); **(b)** loosen the anchor so governance minutes, volunteer rosters, standards ballots, electoral machinery, or advocacy plans can activate `nonprofit` without a non-exchange counterparty — which would require rewriting the schema's existential collision with `business_operations` and re-opening all five rows with a new discriminator. **Do not re-fire the five without choosing (a) or (b).** Re-firing without settling the anchor produces either the same refusals or five rows padded to avoid repeating them.

**NJ-AC-1 — respondent-side seam.** A consultation response, a written submission to a committee, and a petition delivered to an authority are RESPONDENT-side instruments; landed government rows (`public-consultation`, legislative-record, policy-development) were written from the authority side. Alternatives: (a) `government.public-consultation` names the respondent copy as also-holding and takes it — this row's recommendation; (b) it stays with `business_operations.corporate-regulatory-filings` where a registration exists and Independent Records where none does. This row cannot enact either.

**NJ-AC-2 — lobbying-register fork.** Confirm `business_operations.corporate-regulatory-filings` owns LD-1/LD-2, EU Transparency Register, and consultant-lobbyist entries for **charitable** registrants as well as corporate ones, so this refusal leaves no orphan. If R1c instead judges lobbying disclosure a distinct relation, the correct home is a template on `business_operations`, **never** on `nonprofit`.

**NJ-AC-3 — reversal / legacy-id condition.** This refusal would be wrong only if J-IND later requires a row per absorbed legacy id regardless of structure (`civic.community-organising`). Alternatives: (a) accept the refusal and record the legacy id as covered by `business_operations.meeting-record` plus Independent Records plus Reading Inbox — recommended; (b) re-open with a discriminator nobody has yet found. The parent schema's NJ-NP-4 reached the same conclusion independently and asked for refusal rather than invention.

**NJ-AC-4 — cross-check with political-campaign refusal.** Sibling `nonprofit.political-campaign` is also refused and routes campaign plans / lobbying disclosure to the same neighbours. R1c should treat advocacy and political-campaign as one family decision under NJ-AC-FAMILY, not as two independent keep/refuse flips — a keep of one while refusing the other would need a discriminator stronger than "issue vs electoral," and neither refusal found one that clears the nonprofit precondition.

---

## Self-verification

- JSON already present; `python3 -m json.tool` parses it. **No JSON edit in this salvage.**
- `refuse_node: true` kept; refusal not reversed; no padding to save the id.
- Memo written only: `planning/domains/nodes/nonprofit.advocacy-campaign.research.md` with **Depth: J-DEPTH**.
- `fields: []`, `proposed_fields: []`, `collides_with: []`, `also_holds_with: []`, `role_split: []` — refused-row shape; CONNECTION §5 respected.
- Every `file_examples.source_type` in SOURCE_TYPES; every `falls_through_to.residual_template` is one of `00`'s nine residual homes.
- Every `also_schema` id named in fixtures is present on `planning/domains/roster.json`.
- Residual and purpose/`00` quotations in the JSON checked against `planning/00-database-agent-product-design.md`; schema/CONNECTION spans not mis-attributed as `00` in this memo.
- No thresholds, confidence scores, handling classes, or folder paths as facts.
- Only the assigned memo file written; no neighbour, roster, canonical fields, `check.py`, `src/`, or shared file touched. **No commit.**

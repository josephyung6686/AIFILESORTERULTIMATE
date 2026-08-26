# Research memo — `government.constituent-casework`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.constituent-casework.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, placeholder launch

## Result

Accept the node, on a narrow and specific ground: it is the only situation in the `government` family where **the office holding the file has no power over the outcome it is filing**. Everything else on that schema — rulemaking, permits, procurement, FOI, elections, statistics, municipal administration, social-services casework — is held by the body that decides. This row is held by a body that can only *ask*, on the individual's written authority, and whose file closes with somebody else's answer.

That inversion is not cosmetic. It produces a discriminating artifact no sibling requires (an authority-to-act naming a third body), a correspondence shape no sibling produces (two public authorities in different roles on one letter, with a chase cadence and no determination by the holder), and a privacy posture materially stricter than the schema's (a corpus of many unrelated named private individuals rather than one authority's own function, which flips the default residual from Independent Records to Protected Records).

`fields`, `proposed_fields`, and `template.dimension_order` are all empty, and `time_first` is false.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` — the standing brief, read in full.
- The stamped assignment from `planning/domains/dispatch/make_prompt.py government.constituent-casework`.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — depth calibration, and a directly competing neighbour.
- `planning/domains/nodes/government.json` — my schema anchor, read for the default template, `never_alone`, `work_types`, `grouping_reasons`, `collides_with`, `falls_through_to`, `sensitivity_why`, and its casework fixture.
- `planning/domains/roster.json` — my row's hint, and the id list I checked every edge against.
- `planning/domains/nodes/business_operations.support-operations.json` — read only for its `one_line` and collision list, to state a reciprocal boundary in its own terms.
- `planning/00-database-agent-product-design.md` — reached by targeted grep only, per the token discipline in the brief. Every span I put in quote marks was verified verbatim against it before it was written into either file (seven spans, plus the Temporary Screenshots and Unsupported or Encrypted residual sentences, all confirmed present exactly once or more).

## THE CHARGE — the strongest case that this row should not exist

I built the case against the row before writing anything, and it is genuinely strong. Four separate arguments:

**1. It is a `work_type` value already declared by its own schema.** `government.json` lists, verbatim in its `work_types`: `"constituent, ombudsman, complaint, benefit, or service casework held by the public office"`. The 574's recorded failure mode is promoting a value of an enum into a node. On its face this row is exactly that.

**2. It is a duplicate of its schema's default template.** The schema does not merely mention casework in passing — it already *carries the fixture*. `government.json` file example 8 is `Casework 8841 - consent and agency chase.eml`, with observations "public-office mailbox in sender and recipient slots", "case reference in subject and attachment name", "message discusses a named person's problem, authorization, and contact with an agency", and `falls_through_if_inactive: "Protected Records"`. The schema also already declares the grouping rule `"one citizen or regulated-party case, but only inside a protected, locally processed group with exact case anchors and no cross-person semantic joining"`, already declares `sensitivity: potentially_sensitive` with citizen casework named in the reason, and already routes casework material to Protected Records. The schema's `template.dimension_order` is `[]` and mine would be `[]` too. On the strict reading, my three legs are: dimensions identical, privacy label identical, and detection signals already present in the parent. That is a refusal.

**3. It is a duplicate of a sibling.** `government.social-services-casework` is on the roster. Both rows are "a public office's file about one named individual's welfare problem". If they cannot be told apart, one of them is a synonym.

**4. It is an organisation name, which is never-alone evidence.** Strip away the word "casework" and what is left is "files kept by a Member of Parliament's / councillor's / Ombudsman's office". A body's name cannot activate a schema — `government.json`'s own first `never_alone` entry says so. And there is a fifth, weaker form of the charge: the row could be defined by *absence* — "the government casework that isn't a permit case, an FOI case, or a statutory social-care case."

### Defeating the charge

**Against (1) and (2) — the value-versus-situation test.** A work_type value is a document function; this row is a *party structure*. The distinguishing fact is not that a document is called casework, it is that the file has **three parties in fixed roles**: a petitioner who signs, a holder office that acts only on that signature, and a **separately named respondent authority** that is asked rather than instructed. No other government template has a third party in the respondent role. In `government.public-records-foi` the holder *is* the respondent. In `government.permit-licensing` and `government.planning-application` the holder *is* the decider. In `government.public-procurement` the third party is a bidder the holder can bind. Here the holder can bind nobody. That is why the recognition rule that actually fires — an authority-to-act naming a third body, plus an outgoing letter from one public office addressed to a *different* public authority on behalf of a named individual — is false for every sibling and false for the schema default read on its own terms.

The schema's own casework fixture does not defeat this; it *depends* on it. Its observations name "authorization" and "contact with an agency" — the three-party structure — without stating the rule that makes them decisive, because a schema fixture is an existence proof, not a detection contract. This row supplies the contract. That is what a template is for under CONNECTION's node test: the test is disjunctive (detection signals, recommended dimensions, **or** privacy rules), and I differ on two of the three. I differ on detection signals as argued. I differ on privacy rules in a way that changes routing, not just labelling: the schema's `falls_through_to` puts Independent Records first and describes it as the home for "a readable standalone notice, public report, confirmation, permit, licence, published decision, or civic document"; this row's default residual is **Protected Records**, because a single unattached letter about a named person's eviction or benefit refusal is disclosive standing alone in a way a permit notice is not. Same label, opposite default destination. I do **not** claim a difference on dimension order — it is empty here for the same PR-6 reason it is empty everywhere on this schema, and I say so in the JSON rather than manufacturing a difference.

**Against (3) — the sibling test, stated as a reciprocal boundary.** `government.social-services-casework` is the deciding authority's own statutory file: it assesses, it owes the duty, its own determination closes the record, and it needs no authorisation from the subject to open a file. This row's holder has no duty and no determination. The same fixture on both sides: *a letter about Ms A's housing*. On the allocating authority's letterhead, deciding her application → social-services casework. Written by an outside office on Ms A's signed authority, asking that authority to reconsider → this row. The test is power over the outcome, and it is decidable from the letterhead-plus-addressee pair on a single page.

**Against (4) — never-alone.** I accepted this argument rather than arguing around it, and encoded it. The JSON's `never_alone` list explicitly refuses activation on an elected member's, councillor's, ombudsman's, or public-advocate office name, letterhead, seal, crest, or mailbox domain, and separately refuses activation on the words *constituent, casework, caseworker, ombudsman, complaint, advocate, surgery, enquiry* — each of which has a real false friend in my file list. What activates is the three-party structure, which no office name supplies. The absence-defined form of the charge fails for the same reason: I am not defining the row as "the leftover casework", I am defining it by a positive structure that the leftovers do not have.

**Verdict: accept.** The row survives, but only in the narrowed form written into `one_line`. If R1c later finds that `government.social-services-casework` was written to include intermediary offices, or that a mandate-or-authorisation recognition family is adjudicated centrally (see NJ-1), this row's independent ground shrinks and it should be re-examined.

## Files considered and rejected

Naming what is *not* mine was the more useful half of this pass.

- **`Complaint CC-2026-0442 - final response - Council Complaints Team.pdf`** — the collision fixture proper, carried in the JSON. It has everything the row appears to need: complaint vocabulary, a reference token, a named individual, a public letterhead, findings, a remedy offer, and a chase history behind it. It is not mine because the letterhead body is the **respondent**, the reference belongs to the respondent's own two-stage complaints scheme, and there is no third office and no authorisation anywhere in it. Discriminator: count the public bodies and check their roles. One body plus one citizen is the respondent's own record (`government.public-authority-record`); two bodies in different roles plus a signed authority is this row.
- **`Ward 7 constituent mailing list - autumn newsletter.csv`** — the false friend that trips on vocabulary. It contains the word *constituent*, hundreds of named residents, and their addresses. It has no case, no authorisation, and no respondent. A population of names is not a population of cases. → `nonprofit.political-campaign`.
- **`Service desk ticket export - Q3 - IT and facilities.xlsx`** — the false friend that trips on structure. Ticket id, requester, assignee, SLA, resolution time: a casework register looks identical. Rejected because the requesters are the organisation's own staff and the holder resolves. It stays support operations even when the organisation is a council.
- **`Petition - save the Elmfield bus route - signatures.csv`** — many people, one shared grievance, no per-person matter and no authorisation for any signatory. Advocacy, not casework. The inverse case — one person's authorised complaint about their own bus pass — is mine.
- **`Casework themes 2026 - housing repairs and benefit delays.pdf`** — the hardest rejection, and I only half-rejected it. It is *derived from* protected cases but written for publication, with no individual reference. I carried it as a fixture with `group_without_copying_facts: true` and routed it to Independent Records, because derivation is not membership: joining it to a case group would let an aggregate pull disclosive members toward a publishable artifact. It is surfaced as NJ-3 because I cannot settle whether it is operating record, advocacy output, or both.
- **`Casework CMS nightly backup.bak`** — carried, but only as an unreadable object. The filename mentions a case-management system and nothing may be concluded from that; it is not opened to classify it.
- **A live case-management system, a shared office mailbox, or a CRM account** — rejected as source systems rather than file nodes, following the same reasoning as `legal.practice-matter-file`. A bounded export with a readable manifest is represented; ingestion is a later connector and security decision.
- **Contact exports and address books** — rejected as activators even when they contain petitioners, caseworkers, and agency contacts. `SOURCE_TYPES` includes `contacts` and I list it under `file_kinds`, but the design says contact formats "should normally be privacy-protected rather than used to create folder proposals", and a relationship role needs evidence in a workflow.
- **The petitioner's own evidence bundle** — not rejected but deliberately *not absorbed*. A benefit award notice supplied by a constituent keeps its own schema evidence (`also_schema: "finance"` on the fixture). Membership in a case does not convert an agency's award into a fact of this domain, and the office must not be read as holding a benefits record of its own.
- **Practice-area, agency, issue-category, jurisdiction and remedy taxonomies** — rejected outright. Enumerating them would rebuild the industry-depth catalogue J-IND defers, and every one of them is a value.

## Reciprocal boundaries

Eight mutex edges are authored. Each names the same fixture on both sides; I state them here in both directions.

| Neighbour | Mine when | Theirs when | Shared fixture |
|---|---|---|---|
| `government.social-services-casework` | outside office acting on the individual's authority, asking the deciding body | the deciding authority's own statutory assessment and duty file | a letter about Ms A's housing |
| `government.public-authority-record` | holder is the intermediary, with its own separate reference | holder is the respondent answering under its own scheme | `Complaint CC-2026-0442 - final response.pdf` |
| `government.public-records-foi` | request is about one named person's own matter, on their authority | holder is the answering authority running a disclosure process | `RE Case 8841 - third chase.eml` |
| `legal.personal-legal-matters` | office's outgoing file copies, many unrelated individuals, one case each | the individual's inbound copies, one person's matter | `Case 8841 - outcome letter` |
| `legal.practice-matter-file` | non-legal mandate, no fee basis, no standing in proceedings | retainer for legal services, fee terms, counsel role | `Authority to Act - A Rahman.pdf` |
| `business_operations.support-operations` | respondent-authority column per row, authorisation behind it | continuous queue of the holder's own users or staff, holder resolves | a case-queue spreadsheet |
| `nonprofit.political-campaign` | a case: authorisation, approach, respondent | a contact: canvass, mailing, opt-out, leaflet | `Ward 7 constituent mailing list.csv` |
| `nonprofit.advocacy-campaign` | one named individual is the subject | one shared issue is the subject, many signatories | `Petition - Elmfield bus route.csv` |

Two of these are notable. `business_operations.support-operations` has already landed and its `one_line` anchors on "the SUPPORT FUNCTION AS A CONTINUOUS QUEUE - a stream of individually small third-party interactions". That is close enough to be dangerous, and I wrote my side of the boundary in its own vocabulary rather than mine. It does not currently list any `government.*` id in its `collides_with`; adding the reciprocal is a **recommendation to R1c**, not something I may write. The same applies to all eight — I edited no neighbour file.

`legal.practice-matter-file` landed before me and argued a holder-role boundary against `legal.personal-legal-matters` in almost the same terms I need. I aligned to its framing deliberately rather than inventing a competing vocabulary.

`also_holds_with` is empty and `role_split` is empty. Both are schema-level constructs: coactivation cannot be authored by a template, and a role split needs two field keys to point at, which a fieldless schema cannot supply. The genuine coactivation cases are recorded per-fixture as `also_schema` (finance for a supplied award notice, photos for a portal capture) exactly as the landed launch rows do.

## Deliberate non-edges

- `identity.core-documents` — a petitioner's passport copy in an evidence bundle independently activates identity. That is coactivation, not a same-evidence mutex, and it is already handled by the fixture-level rule that membership never converts evidence into a fact of this domain.
- `government.permit-licensing`, `government.planning-application`, `government.housing-authority`, `government.municipal-administration` — all are deciding-side rows and all are already covered by the `government.public-authority-record` edge on the holder-role axis. Adding four more would turn the row into a directory of agencies rather than a boundary.
- `medical.personal-health-records` — a supporting medical letter in a case retains its own schema. Not a mutex. Worth noting that the word *surgery* is the one live confusion, and it is handled in `never_alone` and `needs_llm` rather than as an edge, because a clinic rota shares a word with an advice session and nothing else.
- `finance.receipts-expenses` — an office's own travel and stationery costs are its operating record, not casework; no same-evidence competition.

## Fields and dimensions

`fields: []` and `proposed_fields: []` are intentional and required: `inherited_field_keys` is empty, PR-6 leaves the `government` schema fieldless, and D1's deferral stands.

Candidates I considered and did not mint:

- **A case reference.** The strongest candidate on the schema, and the one this row needs most — it is the only anchor that can bound a group without naming a person. I did not propose it, because `government.json`'s own `open_question` already asks Joseph to adjudicate a "bounded proceeding/programme/case reference" **centrally rather than in children**, and minting a variant here is exactly the duplicated-proposal failure the brief warns against. I restate it as NJ-2 with the extra constraint this row adds.
- **A respondent or acting-office concept.** Rejected. It is the row's discriminator, but as a *recognition* rule, not a stored fact — and as a folder dimension it would build a browsable index of which agencies a named individual is in dispute with.
- **`institution`, `record_type`, `client`, `work_type`** — canonical keys scoped to other schemas. Reusing them here would either be a synonym or would import a foreign schema's meaning.

The dimension prose in `template.why` records what the order *would* be if PR-6 lifts — case first, then document function — and states two things that must hold regardless: the petitioner may never be a dimension even if a person-shaped field is ratified, and the respondent authority may not be first because escalation from a department to an ombudsman would split one person's case at the moment the chase matters. Time is not first, per the design's rule that "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."

## Recognition and grouping notes

Strong evidence is always a pair: an authorisation-shaped artifact **plus** a cross-authority approach, or a register **plus** a populated respondent column. Nothing on the single-signal list activates. Activation is also separated from grouping in the intended way — a surgery list and a calendar event are marked `group_without_copying_facts: true`, because one row's case reference must not be smeared across every named attendee, and an appointment does not prove a case exists.

Cross-petitioner similarity is suppressed as a grouping reason rather than merely discouraged, because in this corpus the similarity is guaranteed: unrelated individuals share the same respondent agency, the same issue category, the same ward, and the same template letter text. This is the one place where the ordinary "semantic neighbourhood" heuristic is actively harmful.

## NEEDS-JOSEPH

- **NJ-1 — the mandate recognition family.** This row's discriminating artifact is a signed authority-to-act. That is the same document shape as a solicitor's retainer (`legal.practice-matter-file`), a medical records release, an insurance claims mandate, and a power of attorney. Alternatives: (a) adjudicate one mandate-or-authorisation recognition family centrally, with per-domain discriminators hanging off it; or (b) let each row argue it locally, which is what I did, and accept that four rows will carry four near-copies of one rule. I recommend (a) and flag that this memo may be creating the fourth copy.
- **NJ-2 — a bounded case reference.** Restating the schema's open question with this row's extra constraint. If PR-6 lifts: may a bounded, opaque case reference exist as a `government` field, and may it ever be destination-eligible? This row needs it more than any government sibling — it is the only safe group anchor available — and can least afford a person-shaped field beside it. Alternatives: reference-only and destination-eligible; reference-only and search-only with redacted display labels; or no field at all, leaving casework groups unanchored and therefore ungroupable.
- **NJ-3 — the aggregate themes report.** An office's published casework-themes report is derived from protected cases but written for publication. Alternatives: (a) government operating record, routed to Independent Records with no case membership — what I wrote; (b) advocacy output, belonging with `nonprofit.advocacy-campaign`; (c) both, via a coactivation the schema cannot currently express. I could not settle it and did not smooth it.
- **NJ-4 — overlap risk with `government.social-services-casework`.** My acceptance rests on that sibling being the deciding authority's own statutory file. That row is not yet written. If its author defines it to include intermediary or advocacy offices, the two rows collide on their core and R1c should merge them rather than keep both. Recommendation, not an edit: R1c should read both rows together before ratifying either.

## Self-verification

- Both output files written; nothing else touched. No neighbour node, roster, `canonical_fields.json`, `check.py`, `src/`, SPEC, or ownership register was modified.
- JSON parses; its key set is identical to the landed `government.json` sibling, including `proposed_context_terms`.
- All eight `collides_with` ids checked programmatically against `roster.json` — zero unknown ids.
- All `falls_through_to` names and all 16 `falls_through_if_inactive` values checked against 00's nine residual homes — zero invalid.
- All 16 `file_examples.source_type` values checked against `SOURCE_TYPES` — zero invalid.
- Every quoted span verified verbatim against `planning/00-database-agent-product-design.md` before use: the extension-routing clause, the session clause, the absent-EXIF clause, the dimension-order rule, the user-may-reverse clause, "Purpose must be a first-class facet.", the privacy-enforcement sentence, the protected-material sentence, and the Independent Records / Protected Records / Review Later / Temporary Screenshots / Unsupported or Encrypted residual sentences.
- `fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false`, `sensitivity: potentially_sensitive`. No threshold numbers, no confidence scores, no handling classes.
- At least one `never_alone` entry is true of a tempting false file: the *constituent / casework / surgery* vocabulary entry is exactly what `Ward 7 constituent mailing list.csv` and a clinical surgery rota would otherwise trip.

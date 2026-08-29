# 52 — Corpus coverage audit

Date: 2026-08-27
Status: **audit**. Nothing here edits `src/`, `planning/domains/**.json`, or the roster.
Author: `audit-corpus-coverage`
Question asked: does the completed 358-row domain corpus actually cover what a real user's
disk holds — measured against `planning/00-database-agent-product-design.md` (canonical,
wins on conflict), not against the roster's own roll-call.

Standing constraint honoured throughout: **"reports, apps and system files MUST NOT BE MOVED
OR READ OR ANYTHING SYSTEM OR SENSITIVE IN THAT SENSE."** Nothing below recommends organizing
material that rule protects, and nothing below recommends hiding it either.

---

## 0. Numbers, re-derived

Derived from `planning/domains/nodes/*.json` at the time of writing, not carried forward.

| Fact | Value |
|---|---|
| Node files | 358 |
| `kind: schema` / `kind: template` | 23 / 335 |
| `refuse_node: true` | 44 (all templates; zero schemas) |
| `launch` split | 325 `placeholder` · 17 `full` · 16 `safety` |
| Schemas declaring live `fields` | **6** — `academic`, `code`, `college_applications`, `finance`, `photos`, `research` |
| Schemas with `fields: []` **and** `proposed_fields: []` | **5** — `career`, `government`, `identity`, `legal`, `medical` |
| Schemas with `fields: []` but proposals on record | 12 |
| Templates with a non-empty `dimension_order` | **54** of 335 |
| Refusals sitting on field-less schemas | 41 of 44 |
| Refused rows that still carry `recognition` | 44 of 44 |
| Refused rows that still carry `falls_through_to` | 41 of 44 |

**Two corrections to the brief I was given.**

1. The brief said *three* schemas propose no fields at all. It is **five**. `career` and
   `government` also carry `fields: []` **and** `proposed_fields: []`. `career` is the one
   that matters: it is one of §3.15's six named launch domains, it is stamped
   `launch: "full"`, and it can propose no folder level at all. See §3, gap **G1**.
2. Only **54 of 335 templates (16%)** can propose a folder shape. The other 281 have an empty
   `dimension_order` by contract, because a dimension may only branch on a field its own
   schema declares. This is the single most important number in this audit and it is not a
   defect — it is `00` §3.15 working as written — but it changes what "358 rows of coverage"
   means. 358 rows is **recognition** coverage. 54 rows is **filing** coverage.

---

## 1. The 44 refusals — are they principled, or did the research give up?

**Verdict: principled. None is a give-up. None is a privacy refusal either — which is itself
the finding.**

I read all 44 `refuse_reason` values in full. Mechanical scan for surrender language
(`could not work out / unable to / unclear how / not enough information to decide`) returns
**0 of 44**. 37 of 44 cite the CONNECTION.md §2 node test by name. All 44 retain their
`recognition` block, their `file_examples`, and their `template` block; 41 retain
`falls_through_to`. The evidence work survives the refusal — the row is retired, the detection
knowledge is not.

They group into four kinds, and only the fourth is a coverage gap.

### 1a. "This IS the schema's default template" — 13 rows. Correct, and costs nothing.

The row restates its own schema's activation spine.

- `code.software-project` — `code.json` already carries `dimension_order: [project, repository, artifact_type]`.
- `research.project-workspace` — `research.json` already carries `[project, stage, artifact_type]`.
- `engineering.requirements-specification` — the schema's deterministic list carries this row's whole recogniser *verbatim*, and the schema's first fixture is this row's fixture.
- `engineering.project`, `engineering.automotive-program`, `government.public-authority-record`, `government.municipal-administration`, `business_operations.organisational-records`, `nonprofit.volunteer-management`, `nonprofit.grant-reporting`, `law_practice.engagement-terms`, `law_practice.legal-research`, `law_practice.matter-correspondence`.

`code.software-project` and `research.project-workspace` are the two that cost literally
nothing: their schemas have live fields and non-empty `dimension_order`, so the files land on a
real folder proposal anyway. Correct refusals.

### 1b. "This is a VALUE, not a node" — 9 rows. Correct.

The row is a work type, artifact type, medium, or document kind — i.e. a value of a dimension,
not a situation.

`engineering.bill-of-materials` (a value of `artifact_type`; the schema's deterministic signal
five already *is* the BOM table), `creative.screenplay` (`script` is already in the creative
schema's own `artifact_type` enum **and** already the first `work_type` of
`creative.film-production`), `creative.illustration`, `creative.graphic-design-project`,
`creative.typeface-font`, `creative.revision-round` (a version-family fact, which `00` makes
universal), `construction_property.compliance-certificate`,
`clinical_practice.protocol-guideline`, `nonprofit.advocacy-campaign`.

### 1c. "A neighbour already owns this, and one evidence item must not count twice" — 19 rows. Correct.

The strongest reasoning in the corpus. `law_practice.pleadings` and
`law_practice.orders-and-judgments` refuse into the `legal` safety schema, on the ground that a
sealed order carries a tribunal caption and a party pair — which is `legal`'s proceeding
signal — and *not* the practitioner/client role split that `law_practice` requires. The schema
anchor had already conceded this in writing on that exact fixture (`Order - Hartley v Nash -
sealed.pdf`) before the row was dispatched. Same shape:
`construction_property.mortgage-brokering` → `finance.loans-mortgage`;
`construction_property.sale-purchase` → `law_practice.conveyancing` + `finance.household-property`;
`clinical_practice.licensure-credentialing` and `law_practice.admission-cle` →
`career.credentials-licenses`; `construction_property.timesheet` split across three existing
owners; plus `creative.creative-brief`, `creative.licensing-rights`, `creative.deliverable-*`
boundaries, `nonprofit.political-campaign`, `nonprofit.standards-body`,
`business_operations.user-research`, `clinical_practice.teaching-material`,
`construction_property.service-charge`, `engineering.electrical-schematic`,
`nonprofit.governance`, `law_practice.settlement`, `law_practice.deadlines-diary`,
`code.scratch-prototypes`.

### 1d. "The row is defined by an ABSENCE" — 3 rows. Correct reasoning, real coverage cost.

`creative.self-initiated-work` ("work made with no client"), `code.scratch-prototypes` (the
complement of a project root), `creative.performing-practice`. The reasoning is right — an
absence cannot activate, and `00` requires that "a model that cannot cite sufficient evidence
must return unknown". But see **G4**: two of these three were the landing sites the roster
assigned to *personal* creative material, and refusing them broke that trail.

### 1e. What is NOT in the 44

**No refusal in the corpus says "this is sensitive and must never be organized."** 43 of the 44
mention privacy somewhere in their reasoning, but always as one leg of the node test ("privacy
rules do not differ from the schema's default"), never as the ground of refusal. The
sensitive-material decision is not made at the row level at all — it is made at the schema
level, by `launch: "safety"`, and that is architecturally correct: a safety posture that lived
in 44 scattered refusals would be far weaker than one that lives on `identity`, `legal`,
`medical` and `finance` and inherits to everything on them.

**Bottom line on Q1: 44 for 44 are good refusals.** One of them (`clinical_practice.veterinary-practice`)
has a downstream consequence the refusal itself could not see — §3, **G3**.

---

## 2. `identity`, `legal`, `medical` — deliberate, and the most important answer in this audit

**Verdict: deliberate, correct, and traceable to `00` by direct quotation. Their silence is a
privacy decision, not an omission. Do not "fix" it.**

This was the question I was asked to answer above all others, so here is the evidence rather
than the conclusion.

### 2a. `00` instructs exactly this outcome

§3.15, verbatim:

> Finance, identity, medical, and legal material should be implemented first as **safety
> domains**, meaning the system detects and protects them before any cloud or automated
> placement decision is allowed.

Detect and protect. Not file. The three schemas do exactly that: 10 templates across them
(`identity` 3, `legal` 4, `medical` 3), all with `recognition` blocks, all with `sensitivity:
potentially_sensitive`, all with `dimension_order: []`.

### 2b. Each row argues its own silence, and argues it twice

These are not blank rows. `identity.json`'s `template.why` runs to a full paragraph and makes
the argument on two independent grounds:

> EMPTY BY CONTRACT AND BY SAFETY, not by refusal, and this is the one node where those are
> the same argument. […] for identity, **THE FOLDER NAME IS THE DISCLOSURE**. A tree of
> document kinds under a protected area publishes its contents in the path itself.

`medical.json`: "EMPTY TWICE OVER, and neither reason is a refusal. […] the dimensions a
medical tree would naturally take — a condition, a specialty, a provider, a person — become
visible folder LABELS, publishing in the namespace exactly what the protection exists to hide."

`legal.json`: "EMPTY BY CONTRACT AND BY SAFETY […] A folder tree whose branch labels are matter
names is itself a disclosure."

All three cite the same `00` sentence from §8.4 for the leak argument: *"A summary such as
'11 protected identity records' may be safe to show, while a visible list of passport filenames
on a shared screen may not be."*

This is precisely the standing security rule expressed as tree design: **counted, explained,
never opened.** The material is recognised (so it can be protected and surfaced as a count), it
is never given a descriptive folder path (so the namespace does not leak it), and §7.3's
`Protected Records` residual is its named home — `identity.falls_through_to` is
`["Protected Records", "Unsupported or Encrypted"]`, `medical.falls_through_to` is
`["Protected Records"]`.

### 2c. Each row records the unresolved half as a question for the owner

None of the three pretends the question is closed. Each carries an explicit `open_question`
addressed to Joseph:

- `identity.open_question` (3 forks) — *"MAY THE PROTECTED AREA CARRY ANY DEPTH? For identity the
  folder name is itself a disclosure — a path ending in Passport or Visa Denial publishes its
  contents to anyone who can see the tree, sync it, or back it up […] 00 draws the line at the
  UI but says nothing about the filesystem shape, so the depth question is Joseph's and is not
  resolvable from 00."*
- `medical.open_question` (2 forks) — *"when medical material is detected, may the matched
  clinical text be stored in the local evidence table like any other observation, or should
  detection store only a protected marker plus a location? […] a stored diagnosis string is a
  larger local surface than a stored 'this is medical' flag, and every later dossier builder
  reads that table."*
- `legal.open_question` (3 forks) — which canonical field keys legal gets if `D1`'s narrowing
  ever lifts, and whether the party-of-record / counterparty role split can be authored at all
  while the schema declares no fields.

An omission does not write itself a three-fork open question naming the exact decision it is
deferring and the exact person who owns it. This is a deferral with a paper trail.

### 2d. The one thing that is genuinely missing here, and it is small

`identity`, `legal` and `medical` do the right thing. What is *not* written anywhere is the
**UI contract for the count**. The standing rule requires that a protected container be
"present-but-untouched in the UI, with a reachable explanation, never silently omitted." The
schemas make the filesystem side of that promise (flat area, no descriptive labels) and `00`
§8.4 makes the display side ("configurable redaction in the canvas and review screens"), but no
node, no SPEC, and no built module states what the user actually *sees* for the 10 safety
templates: how many, under what heading, with what explanation, and what the "show me" gesture
does. `src/grouping/dossier.py:200` gets this right for the unreadable/unclassified class
("Marked and counted, never opened […] named in `omissions`, so a later reader shows it as
present-but-untouched"). Nothing does the equivalent for the safety domains.

That is a **P13 surfacing gap, not a corpus gap**, and it is the only action item this section
produces.

**Bottom line on Q2: deliberate. Leave all three field-less. The gap is downstream, in what the
UI says about them.**

---

## 3. What a real disk holds that 358 rows do not name

I worked from `00`'s purpose and from the categories in the brief, then checked each against
the roster and against `planning/domains/ROSTER.md` §4–5 and Appendix A, which is where the
574 legacy ids were triaged. ROSTER.md is unusually honest here — it names every drop with a
reason, so most of what follows is *confirming a documented decision*, not discovering a
surprise. Coverage is genuinely good. Six real gaps, ranked.

### Coverage table

| Real-disk material | Roster coverage | Can propose a folder? |
|---|---|---|
| Education records for children | `academic.k12-schooling` `[school, term, work_type]`, `academic.iep-accommodation-plans` `[school, term]`, `academic.homeschool` `[term, subject, work_type]`, `applications.k12-admission` `[target_university, application_document_type]` | **Yes** — all four carry dimensions. Best-covered category in the audit. |
| Tax paperwork | `finance.tax-filings` `[tax_year, record_type]` | **Yes** |
| Insurance | `finance.insurance-personal`, `-healthcare`, `-corporate` | **Yes** |
| Vehicles | `finance.vehicle-records` `[record_type]` | **Yes** |
| Subscriptions & utilities | `finance.subscriptions-utilities` `[institution, record_type]` | **Yes** |
| Receipts | `finance.receipts-expenses` `[institution, record_type]` | **Yes** |
| Warranties | `finance.receipts-expenses` (`warranty registration`) + `finance.household-property` (`property-system warranty`) | **Yes**, partial — consumer product warranties/manuals are thinner than property warranties |
| Property & tenancy (owner/tenant) | `finance.household-property` `[record_type]`, `legal.leases-agreements` (safety) | **Partial** — one dimension, and the executed lease is deliberately on the protected side |
| Travel | `travel.bookings-confirmations` `[record_type, institution]`, `travel.trip-photos` `[event, location]` | **Yes**, split across two schemas; the *trip* is an accepted group, not a row (ROSTER.md §5.3 — still refused) |
| Family & estate documents | `legal.estate-planning` (safety), `photos.family-archive` `[event, capture_year]` | **Partial by design** |
| Immigration | `identity.immigration-visa` (safety), `law_practice.immigration-casework` (professional side) | **No, by design** — §2 |
| Medical records | `medical.personal-health-records`, `.dependant-child-health`, `.wearable-health-exports` | **No, by design** — §2 |
| Personal correspondence | **none** | **No** — G2 |
| Pets | **none** | **No** — G3 |
| Hobbies, journals, genealogy, gift occasions, personal faith | **none** (7 legacy ids dropped to residual) | **No** — G5 |
| Citizen-side government paperwork | **none** on `government` (authority-side only) | **No** — G6 |
| Career: resumes, offers, employment records, portfolio | `career.*` — 6 rows, all recognised | **No** — G1, and this one is unintended |

### G1 — `career` is a launch domain that cannot file anything. **Highest priority.**

`career.json`: `launch: "full"`, `fields: []`, `proposed_fields: []`, `template.dimension_order: []`.
All six templates (`career.recruiting`, `career.employment-records`,
`career.credentials-licenses`, `career.portfolio-work-samples`,
`career.consulting-client-engagement`, `career.employer-side-hiring`) inherit the empty order.

`00` §3.15 names career among the six domains the initial release should **fully support**, and
§5.4 states the template outright: *"a Career template may define company → role or recruiting
cycle → document type."* `career.json`'s `template.why` records that sentence verbatim and
explains why it cannot use it: *"a dimension may only branch on a field the schema declares,
and this placeholder declares none (D1 as narrowed)."* Its `open_question` says the field keys
are *"owed before P10"*. P10 is built.

This is not a research gap and not a refusal. It is one unanswered adjudication — do `company`,
`role`/`recruiting_cycle` and `document_type` reuse canonical keys or mint new ones — standing
between a launch domain and every resume, offer letter, employment contract, performance review
and portfolio file on a real disk.

**Needs:** an existing row extended — specifically, the `career` schema's field rows decided.
Nothing else in this audit unblocks as much for as little.

### G2 — Personal correspondence has no home, and the reason it was dropped over-reaches.

ROSTER.md:504 and §4 "Dropped as formats": `pers.correspondence` → **DROP·format**, reason
*"personal correspondence is an email SOURCE_TYPE, never a domain (the .ics fixture rule)."*
All 14 `calendar.*` / `comms.*` ids dropped on the same ground (ROSTER.md:964–977), including
`comms.mailbox-archive` and `comms.email-thread`.

The format argument is correct about *email as a container*, and I agree with it: an `.eml`
parser is an extractor, not a domain, exactly as `.ics` is. But it does not dispose of the
**content**. A saved letter as `letter to grandma.docx`, a printed email thread as
`Re - deposit dispute.pdf`, a scanned handwritten letter, a legal notice received by post — none
of these is an email source type, and none has a row. The survivors named in the drop reason,
`photos.messenger-export` `[capture_year]` and `photos.social-media-export`
`[capture_year, event, media_type]`, are *export-shaped* rows on the **photos** schema: they
file a WhatsApp dump by capture year. They do not file a letter.

`00` §8.4 lists *"private correspondence"* among the material the corpus contains and the
privacy layer must handle, so correspondence is in scope as content even though it is not a
format.

**Needs:** a decision, not necessarily a row. Either (a) a residual destination — none of the
nine names covers correspondence today, so this would be the strongest candidate for a
**user-defined residual area** under §7.3's final paragraph, or (b) a narrow row if a
letter-shaped structure (salutation / body / sign-off, or a sender-and-recipient pair in a
non-email document) proves detectable. I lean (a): a letter that is genuinely unattached is the
textbook residual, and inventing a `correspondence` schema to hold it would be the
"format-as-schema" error in a new coat.

### G3 — Pets: dropped to residual, and then the vet-side row was refused too.

`pers.pet` → **DROP·residual** (ROSTER.md:494), with §5.6's reason: *"Pets/veterinary as an
owner's record […] still no honest schema; their isolated files are what the residual library
exists for."* ROSTER.md §5.6 explicitly frames this as a **role split, not a reversal** — the
owner side stays refused while `med.veterinary-practice` became
`clinical_practice.veterinary-practice`, "a practice", which is a real record set.

That framing no longer holds: **`clinical_practice.veterinary-practice` is `refuse_node: true`.**
Both sides of the role split are now gone. Its refusal is well-argued on its own terms (the
schema declares no fields, so `animal`/`owner`/`species` cannot become dimensions or facts, and
species is a runtime value not a roster node) and it does route onward — it names six residual
destinations, more than any other refused row. But the *stated justification* for refusing the
owner side has been silently invalidated.

The user-facing cost is concrete: a pet is one of the clearest "coherent real-world unit" cases
on a household disk — vet invoices, vaccination card, microchip registration, insurance policy,
adoption papers, prescription, photos — and the corpus now scatters it across
`finance.receipts-expenses`, `finance.insurance-personal`, `Independent Records`,
`Protected Records` and `photos.*`, with nothing holding it together.

**Needs:** ROSTER.md §5.6's reasoning re-stated now that its premise is gone, and a call on
whether the owner side earns a row. If the answer stays no, that is defensible — but it should
be re-argued, not inherited.

### G4 — Three personal situations were routed to rows that were then refused. **Broken trail.**

ROSTER.md Appendix A marks these **ROW** (i.e. covered, not dropped):

| Legacy id | Routed to | Status now |
|---|---|---|
| `pers.music-practice` | `creative.performing-practice` | **REFUSED** |
| `pers.creative-project` | `creative.self-initiated-work` | **REFUSED** |
| `pers.volunteering` | `nonprofit.volunteer-management` | **REFUSED** |

Each refusal is individually sound (§1d and §1a above). Together they mean three ids the
roster's own accounting reports as *covered by a row* are covered by nothing. ROSTER.md's
headline promise — *"every one of the 574 legacy ids is now accounted for […] Nothing is
silently dropped"* — is, for these three, no longer true.

Of the three, `creative.self-initiated-work` names residual destinations (`One-Off Images`,
`Reference Clips`, `Review Later`); the other two name none for the personal reading.

**Needs:** an accounting fix, not a build. Re-classify all three in Appendix A as
**DROP·residual** with a named residual home, or reopen one of them. Cheap, and it restores the
roster's central claim.

### G5 — The seven personal drops: right call, uneven residual fit.

ROSTER.md §5.6 refuses seven legacy ids to the residual library: `pers.genealogy`, `pers.pet`,
`pers.recipe-meal`, `pers.hobby-collection`, `pers.journal`, `pers.gift-occasion`,
`pers.faith-community`. The reasoning — *"no honest schema"* — is the right one, and it is the
same discipline that produced the 44 good refusals. `00` §3.15 explicitly blesses it:
*"Other domains remain placeholders until user demand and corpus evidence justify detailed
templates."*

The fit is uneven, and §4 assesses it file-by-file. In short: recipes and hobby *references* are
handled well; journals, genealogy documents and hobby *projects* are not.

**Needs:** no new rows. Residual destinations, plus the user-defined-area path. See §4.

### G6 — Citizen-side government paperwork.

`government.json`'s `one_line` is explicit: the schema *"is not activated by a government name,
public-sector industry, legal or regulatory vocabulary, or **receipt of an authority-issued
document**."* All 31 `government.*` templates are authority-side. This is deliberate and
correct — a council's own casework file and a citizen's letter *from* the council are genuinely
different situations, and conflating them would let any official letterhead activate a
31-template schema.

The remainder after subtracting what *is* covered is smaller than it first appears:
`finance.tax-filings` takes tax; `identity.immigration-visa` takes visas; `legal.personal-legal-matters`
takes proceedings; `finance.household-property` takes `property tax bill or assessment notice`
and `permit or building approval`; `finance.subscriptions-utilities` takes utility billing.
What is left with no row: benefits and pension correspondence, licence renewals (driving,
firearms, TV, professional-to-citizen), voter registration, jury summons, school-place
allocation letters, civic notices.

`government.falls_through_to` handles this deliberately and well — it is one of the few rows in
the corpus that gives a full five-destination fallthrough with a `when` clause and a
`design_cite` for each, routing durable notices to `Independent Records`, personal/casework
material to `Protected Records`, and reading material to `Reading Inbox`.

**Needs:** nothing new. This is a **deliberate refusal with a working residual answer.** I am
naming it only so it is not later mistaken for an oversight.

### One thing that is not a gap

**Travel.** ROSTER.md §5.3 still refuses travel as a schema, "it needs no field `00` does not
already have." Two rows carry it (`travel.bookings-confirmations`, `travel.trip-photos`) and
`00` §7.8 blesses the residual answer by worked example — `Personal/Travel/Confirmations` as a
user-approved branch, and an explicit prohibition on inventing `Travel/Flight Gate B12`. The
trip itself is an accepted P9 group, which is the right mechanism: a trip is discovered from
evidence, not declared by a template. This is coverage working as designed.

---

## 4. The residual path — is it a good answer, or a junk drawer?

I read `src/tree_design/residuals.py` (271 lines, 32 tests passing —
`pytest -k residual` → `32 passed`) and
`planning/deferred-catalogues/09-residual-library/01-nine-templates.json`, which authors the
eight §7.2 slots for all nine §7.3 names.

**Verdict: the residual layer is a genuinely good answer for roughly half the gaps in §3, an
adequate answer for a quarter, and a bad answer for the rest — and the reason it goes bad is
always the same one, so it is fixable.**

### 4a. Three structural properties that make it much better than a `Misc` folder

1. **A disabled template has no node at all.** `project_residual_nodes` skips `DISABLE` and
   every non-creating action, so no node is minted. The docstring states the enforcement
   plainly: *"a template the user did not enable has no node at all"* — and §7.4's rule that the
   LLM "may not create additional generic destinations" is enforced by the destination simply
   not existing, not by a check the model could argue past. This is the whole answer to
   `Random PDF Things`.
2. **Three dispositions, and two of them move nothing.** `RESIDUAL_DISPOSITIONS = ('physical-destination',
   'review-only', 'leave-in-place')`. A user can accept the *recognition* of a residual set
   without accepting any movement. `ResidualChoice` refuses to construct without one:
   *"§7.4 makes the user decide whether a residual template is a real physical destination, a
   review-only category, or a policy to leave files in place, and the three behave differently
   in P11."*
3. **`REPLACE_WITH_EXISTING` maps a template onto a folder the user already has.** §7.4's
   `To Sort` case. The node keeps the existing `node_id`, `parent_node_id`, `existing_path` and
   `handling_class`; only the explanation changes. The product does not invent a second
   inbox beside the one the user already made.

Depth is capped per template (`max_permitted_depth`), subfolders are opt-in and shallow
(`optional_shallow_subfolders`), and `default_parent_location` is validated to be a
`display_label` chain rather than a disk path — a residual node cannot smuggle in a filesystem
location.

### 4b. Gaps the residual layer handles WELL

| Gap | Residual | Why it works |
|---|---|---|
| Recipes (`pers.recipe-meal`) | **Reference Clips** | §7.3 names recipes in the holds sentence, literally. A saved recipe is exactly "useful for later retrieval but not part of a current project." Correct home, not a compromise. |
| Hobby *references* — saved inspiration, product listings, tutorials, sheet-music PDFs | **Reference Clips** | Same sentence: "saved visual inspiration, product references, quotes, recipes, short article captures, code snippets." |
| Citizen government notices (**G6**) | **Independent Records** | `01-nine-templates.json` gives it the `standalone-durable-document` pattern: "issuer block, labeled fields, table cells, formal headings" plus `required-absence` ("no broader group"). A council letter is precisely a standalone notice with a durable purpose. `government.falls_through_to` already routes it there with a `design_cite`. |
| Consumer warranties and product registrations (**§3 table**) | **Independent Records** + `finance.receipts-expenses` | Split is right: the purchase receipt is transactional (Receipts and Confirmations / `finance.receipts-expenses`), the warranty card is durable (Independent Records). `do_not_claim_when` encodes the boundary explicitly. |
| Travel confirmations and boarding gates | **Receipts and Confirmations** + user-defined `Travel` | `00` §7.8 works this exact case end to end, including the `Travel/Gate B12` prohibition. |
| Identity / medical / legal isolated records (**§2**) | **Protected Records** | The one residual whose sensitivity restriction is structural rather than advisory. This is the "counted, explained, never opened" destination and it is the correct answer, not a fallback. |
| Encrypted vaults, `.kdbx`, damaged archives | **Unsupported or Encrypted** | §7.3 offers "or, more safely, represented without moving" — the `leave-in-place` disposition. |

### 4c. Gaps the residual layer handles BADLY — and the single reason why

Every bad case has the same shape: **the residual library is deliberately flat, so it destroys
coherent multi-file real-world units.** `Independent Records` ships
`optional_shallow_subfolders: []`, with the reason stated:
*"Splitting by record kind rebuilds the records taxonomy that finance, legal, and personal-administration
domain templates own."* That is correct reasoning for a records taxonomy. It is the wrong
outcome for a *thing in the user's life* that happens to have no schema.

| Gap | What the residual layer does | Why it is bad |
|---|---|---|
| **Pets (G3)** | Vet invoice → Receipts and Confirmations. Vaccination card → Independent Records. Insurance → `finance.insurance-personal`. Photos → `photos.*`. Microchip registration → Independent Records. | Five destinations for one animal. The user's mental unit is "Rocket"; the product's output is five flat piles with the pet's name nowhere in the tree. This is not a junk drawer — it is worse, it is a *tidy* dispersal, which is harder to notice and harder to undo. |
| **Personal correspondence (G2)** | **No residual names it.** Not Independent Records (a letter is not a certificate/notice/form and is not "non-transactional durable document" shaped). Not Reference Clips (not saved reference material). Realistic outcome: `Review Later` or `leave-in-place`. | `Review Later` is §7.3's *"partly understood but final location requires a future decision"* — an honest holding pen, but correspondence is not undecided, it is unmodelled. A decade of letters landing in Review Later is the failure §7.1 warns about wearing a better name. |
| **Journals and diaries** (`pers.journal`) | Same as correspondence — no residual names them. `Review Later`. | A journal is the most durable, least ambiguous personal document there is. Routing it to "decide later" is the single worst residual outcome in the corpus. |
| **Genealogy** (`pers.genealogy`) | Certificates → Independent Records (flat); ancestor photos → `photos.family-archive`; research notes → Reference Clips or Reading Inbox. | Genealogy is inherently a *set* — the whole value is the linkage. Flat dispersal removes exactly the property that made it worth keeping. |
| **Hobby *projects*** (as distinct from hobby references) | Reference Clips (flat) or `Review Later`. | A hobby project (a build log, plans, parts list, photos, receipts) has the same multi-file shape as an `engineering.prototype-build` — which ROSTER.md §5.7 correctly refuses to lend it, since that row is a professional build record. But refusing the professional row does not supply an amateur answer. |
| **Gift occasions** (`pers.gift-occasion`) | Receipts and Confirmations (the receipt) + One-Off Images (the photo). | Minor, and honestly borderline — a gift occasion may not deserve a home. Listed for completeness only. |

### 4d. The design already contains the fix, and it is not a new schema

§7.3's closing paragraph:

> the library must support user-defined residual areas such as Things to Read, Ideas, Shopping
> Research, Memes, Travel, Receipts to Process, Clips, or Stuff to Sort, because residual
> organization is highly personal and should not be dictated by a universal taxonomy.

`residuals.py` implements this — `build_library(..., user_defined=...)`, with
`ResidualTemplate.user_defined` as a required flag and `ConfigurationRequired` raised if a row
is offered as user-authored without it. The catalogue's
`02-user-defined-shape.json` defines the collection form, and `check.py` asserts that **zero**
of `00`'s example names ship as templates — correctly, since they are illustrations of user
freedom, not a shipped taxonomy.

So the honest answer to pets, correspondence, journals, genealogy and hobby projects is not
nine more schemas. It is: **the user creates `Pets`, `Letters`, `Journal` as their own residual
areas, with real (if shallow) structure**, and the product proposes them because it can see the
files. What is missing is the *proposal*: today a user-defined area exists only if the user
thinks of it unprompted. Nothing in the surfacing screen (§7.5) or the set-level decision (§7.6)
says "we found 34 files that look like they belong together but match no domain — would you
like an area for them?"

That is the highest-leverage single change this audit found for question 4, and it is a P11
surfacing behaviour, not a corpus change.

### 4e. One data-hygiene finding

`falls_through_to` has drifted into six shapes across the 358 rows: 1183 use
`{residual_template, why, provenance}`, 176 are plain strings, 164 use
`{residual_template, when, design_cite}`, 123 add `design_cite`, 54 drop `provenance`, **39 use
the key `template` instead of `residual_template`** (every one on the `hr` family — the `hr`
schema row itself plus `employee-relations`, `engagement-survey`, `onboarding-offboarding`,
`org-design-headcount`, `payroll-benefits-administration`, `performance-cycle`,
`training-development`, `workforce-analytics`, `workplace-health-safety`), and 4 use `residual`
(all on `law_practice.deadlines-diary`). Any
consumer that reads `residual_template` silently loses the 43 entries keyed otherwise. Not a
coverage gap; a parsing hazard for whoever builds the residual-candidate ordering
(CONNECTION.md §8).

---

## 5. Prioritized gap list

Ordered by user-facing cost per unit of work. "Needs" uses the four categories asked for.

| # | Gap | Evidence | Needs | Priority |
|---|---|---|---|---|
| **1** | `career` — a §3.15 launch domain at `launch: "full"` with `fields: []`, `proposed_fields: []`, and 6 templates that can propose no folder level. Resumes, offers, employment records, portfolios. | `career.json` `template.why` + `open_question` ("owed before P10"); `00` §3.15 and §5.4 | **Existing rows extended** — decide the `career` field keys (`company`, `role`/`recruiting_cycle`, `document_type`; reuse vs mint) | **P0** |
| **2** | Safety-domain UI contract. `identity`/`legal`/`medical` correctly file nothing; nothing states what the user *sees* — the count, the heading, the explanation, the reveal gesture. The standing rule requires "present-but-untouched, with a reachable explanation." | §2d; `00` §8.4; the working precedent at `src/grouping/dossier.py:200` | **Deliberate refusal, made visible** — a P13 surfacing contract. No corpus change. | **P0** |
| **3** | Personal correspondence has no domain row *and* no residual name. Dropped as a format, but the format argument does not reach non-email correspondence. | ROSTER.md:504 and §4 "Dropped as formats"; `00` §8.4 lists "private correspondence" | **Residual destination** — the strongest case for a *proposed* user-defined area (§4d). A row only if letter-structure detection proves out. | **P1** |
| **4** | Journals and diaries have no domain row and no residual that names them; realistic landing is `Review Later`. | ROSTER.md:503 (`pers.journal` DROP·residual); §7.3's nine names | **Residual destination** — same proposed-user-area mechanism as #3 | **P1** |
| **5** | Pets: `pers.pet` refused to residual on a stated role split whose other half, `clinical_practice.veterinary-practice`, is now itself `refuse_node: true`. One animal disperses across five destinations. | ROSTER.md:494 and §5.6; `clinical_practice.veterinary-practice.refuse_reason` | **Deliberate refusal, re-argued** — §5.6's premise is gone; re-decide the owner side explicitly | **P1** |
| **6** | Three legacy ids marked **ROW** in Appendix A point at rows that were subsequently refused (`pers.music-practice`, `pers.creative-project`, `pers.volunteering`). ROSTER.md's "nothing is silently dropped" no longer holds for them. | ROSTER.md:501, 502, 511 vs `refuse_node` on `creative.performing-practice`, `creative.self-initiated-work`, `nonprofit.volunteer-management` | **Accounting fix** — re-classify as DROP·residual with a named home, or reopen one | **P1** |
| **7** | §7.5/§7.6 never *propose* a user-defined residual area. The mechanism is built (`residuals.py` `user_defined`, `02-user-defined-shape.json`) but only fires if the user thinks of it unprompted — so pets, hobby projects and genealogy stay dispersed by default. | §4d; `00` §7.3 closing paragraph; `residuals.py:build_library` | **Residual destination** — a P11 surfacing behaviour: offer an area when a residual set coheres | **P2** |
| **8** | Genealogy and hobby *projects*: coherent multi-file sets dispersed flat by `Independent Records` (`optional_shallow_subfolders: []`). | `01-nine-templates.json` Independent Records `why_empty`; ROSTER.md §5.6, §5.7 | **Residual destination** — resolved by #7; no new rows | **P2** |
| **9** | `falls_through_to` key drift — 6 shapes across 358 rows; 39 `hr.*` entries key it `template` not `residual_template`, 4 use `residual`. A `residual_template`-only reader loses 43 entries. | §4e | **Data hygiene** — normalize the key (roster edit, not a coverage change) | **P2** |
| **10** | Protected-container membership is one literal. `PROTECTED_BUNDLE_SUFFIXES = (".app",)`; system locations are deferred to a caller-supplied `extra` predicate nothing authors. `.framework`, `.bundle`, `.pkg`, `/System` get no `untouched_protected` label; `Library` is excluded under the weaker `literal directory name` rule with `label=None`, so it is skipped without being *explained*. | `src/scan_agent/exclusion.py:55–135` | **Deliberate deferral, made explicit** — flagged under the standing security rule, not proposed for organizing. Author the deployment list, or state that unlabeled exclusions still surface. | **P2** (security-adjacent; the rule holds correctly for `.app` today) |

### What I am explicitly NOT calling a gap

- The 44 refusals. All principled; §1.
- `identity`, `legal`, `medical` filing nothing. Correct, and `00` instructs it; §2.
- Travel having no schema. Documented refusal with a working residual answer; §3.
- Citizen-side government paperwork. Documented boundary with the corpus's most careful
  five-destination fallthrough; §3 G6.
- 281 of 335 templates having an empty `dimension_order`. That is `00` §3.15's staged rollout
  working as written, not a hole — with the single exception of `career` (#1), where the stage
  was supposed to have completed.

---

## 6. The honest summary

The corpus is better than its own headline numbers suggest in one direction and worse in
another.

**Better:** the refusal discipline is real. 44 rows were killed for stated, checkable reasons,
every one kept its detection knowledge, and 41 kept a route onward. The three safety domains
make the hardest call in the product — *file nothing, protect everything, and say so in writing*
— and each argues it on two independent grounds with `00` quoted. That is not a corpus that gave
up on hard domains; it is a corpus that refused to fake them.

**Worse:** "358 rows" is recognition coverage, not filing coverage. **54 rows can propose a
folder.** Of those 54, the ones that serve an ordinary household disk are almost entirely
`finance` (17), `photos` (8) and `travel` (2). A user whose disk is resumes, letters, a pet, a
hobby and a journal gets recognition, protection, and a residual — which is honest, and which is
much better than a fabricated folder — but not structure.

The product owner's concern — *"we cannot be limited to the ones in my computer"* — is answered
correctly at the schema layer: 23 schemas and 335 templates reach far past any one person's
disk. The limitation that remains is not breadth of *domains*. It is that the personal, everyday
half of a disk is served by six fielded schemas, one of which (`career`) is a launch domain
still waiting on a field-key decision, and the rest of that half is served by a residual library
that is deliberately flat and never offers to become less flat.

Fix #1 and #7 and the shape of the answer changes materially. Everything else on the list is
bookkeeping by comparison.

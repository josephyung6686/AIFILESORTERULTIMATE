# 48 — Entity / custody field-key adjudication

Date: 2026-08-27
Status: **PROPOSAL for the product owner.** Nothing here is adopted. No `src/` file and no
`planning/domains/**/*.json` was edited to produce it.
Canonical on intent: [`00-database-agent-product-design.md`](00-database-agent-product-design.md).
Shape contract: [`domains/_CONTRACT.md`](domains/_CONTRACT.md).

---

## 0. Counts, re-derived in this document

Run against `planning/domains/nodes/*.json` at commit `b2dbb08`:

| Quantity | Value |
|---|---|
| node files | 358 |
| `kind: template` | 335 |
| `kind: schema` | 23 |
| `refuse_node: true` | 44 |
| rows carrying ≥1 `proposed_fields` entry | 87 |
| distinct proposed keys | 80 |
| proposed-field instances (seconding included) | 170 |
| **live `fields[]` entries across all 23 schemas** | **30** |

**Correction to the brief.** The binding ceiling is **30 live fields, not 31.** Commit `b2dbb08`
(landed during this session) removed `account_holder` from `finance.fields[]` and left it in
`proposed_fields`, because it was the only key in the whole corpus that was declared live without
appearing in `canonical_fields.json`, and P8's `FIELD_NOT_IN_ACTIVE_SCHEMA` reads that file. The
live sets are now: academic 5, code 4, college_applications 5, finance 4, photos 6, research 6.

**The gate every recommendation below must clear.** After `b2dbb08` the invariant
`fields[] ⊆ canonical_fields.json` holds corpus-wide. So no key in this cluster can be declared on
any schema until it is first written into `canonical_fields.json`. Adjudication is therefore a
canonical-list act, exactly as 60-odd rows in this cluster say it is.

**The second gate, which no row in this cluster mentions.** `src/facts/domains.py:52` declares
`SCHEMA_IDS` = academic, college_applications, research, career, photos, code, finance, identity,
medical, legal — **ten**. Every schema this cluster's proposals sit on except four is outside that
tuple. Of the 67 proposal instances I read for this cluster, **61 sit on schemas the product does
not recognise** (business_operations, construction_property, manufacturing, resource_operations,
retail_hospitality, logistics, nonprofit, law_practice, hr, clinical_practice, engineering,
creative). Six sit on recognised schemas: `academic.study-abroad::host_school`,
`career.employment-records::employer`, `finance::account_holder`,
`finance.household-property::property`, `finance.vehicle-records::vehicle`,
`research.grants-funding::sponsor`. **Adopting `organization` or `site` today changes nothing the
product can run**; adopting `property` on `finance` or `employer` on `career` does.

---

## 1. Every row proposing a key in this cluster, and the exact role it needs named

### 1a. `organization` — 14 rows

| `domain_id` | The role the row actually needs named |
| --- | --- |
| `business_operations` (schema) | **Custodian of the record.** "the legal entity or internal unit whose own record this is" — the fact that separates a person's employer's board pack from their own limited company's board pack in one Downloads folder |
| `business_operations.compliance-audit` | **The assessed subject.** "the entity whose conformity is being tested — one employer's ISO pack among the supplier assurance packs kept beside it" |
| `business_operations.contract-administration` | **Custodian.** "the legal entity whose own contract register this is" |
| `business_operations.corporate-regulatory-filings` | **The obligated entity.** "the legal entity whose obligation the filing is — one of the two companies a person is a director of" |
| `business_operations.facilities-workplace` | **Occupier / custodian of the premises.** "the entity or internal unit whose premises this site record concerns" |
| `business_operations.it-asset-inventory` | **Custodian of the estate.** "the entity or internal unit whose estate this register describes" |
| `business_operations.meeting-record` | **Custodian of the series.** "the entity whose meeting series this is" |
| `business_operations.policy-handbook` | **The issuing entity — including third parties.** "the entity whose rules these are"; the row's own case is three *different* employers' handbooks plus "every supplier who sent them a copy" |
| `business_operations.risk-register` | **Custodian of the register.** "the entity or internal unit whose standing register and continuity plans these are" |
| `business_operations.support-operations` | **Custodian of the desk**, internal or external |
| `construction_property` (schema) | **Custodian.** "the practice, contractor, agency or managing agent whose own working record this is" |
| `construction_property.subcontract` | **Counterparty firm — the supplier.** "the counterparty firm an engagement record is about — Meridian Groundworks Ltd" |
| `construction_property.variation-claim` | **Custodian / which side.** "the party whose own claim file this is — the contractor, the employer, or the consultant advising one of them" |
| `nonprofit` (schema) | **Custodian.** "the association whose own record this is", where a person is trustee of one charity, member of a union, volunteer for a third |

**The 14 rows are not asking for the same thing.** Eleven mean *custody* — whose drawer. Three do
not: `business_operations.compliance-audit` means the **assessed subject**,
`business_operations.policy-handbook` means the **issuing entity** (two of its three values are
other people's companies), and `construction_property.subcontract` means the **buy-side
counterparty**. That is the first evidence that one key cannot carry the concept.

*(Minor corpus error: `nonprofit`'s own text says "Thirteen rows already propose `organization`
(business_operations and its siblings, construction_property, **hr**)". The 13 are the ten
`business_operations` rows plus the three `construction_property` rows. `hr` proposes
`workforce_unit`, not `organization`. The count is right; the attribution is not.)*

### 1b. `site` — 10 rows

| `domain_id` | The role the row actually needs named |
| --- | --- |
| `manufacturing` (schema, originator) | The facility that **performs production or controls an asset** — "Plant 2 - Kowloon" |
| `manufacturing.asset-register` | The facility that **controls** the asset — "Plant 2 - Kowloon / Line 4" |
| `manufacturing.production-planning` | The **planning plant** |
| `resource_operations` (schema) | The **operating place a record is about** — "North Quarry / Solar Farm A / Field 12" |
| `resource_operations.grid-connection` | The **installation site** of the connection |
| `resource_operations.mining-operations` | Mine, quarry, pit, lease area, processing site |
| `resource_operations.oil-gas-operations` | Field, lease area, block, platform |
| `logistics` | The **facility holding the goods** — depot, warehouse, terminal, cross-dock. Warns that one page carries **four** place roles: place of receipt, place of delivery, depot of custody, capture location |
| `retail_hospitality` (schema) | The **trading unit** — "`Store 214 - Camden`, `The Bell, Wharf Street`", and asks whether a non-physical channel ("`Shopify - UK store`") is admissible — **unresolved, and `retail_hospitality.ecommerce-ops` depends on it** |
| `retail_hospitality.supplier-order` | The **deliver-to** unit, which for a head-office corpus is *not* the unit that placed the order |

### 1c. `property` — 5 rows

| `domain_id` | The role the row actually needs named |
| --- | --- |
| `construction_property` (schema, originator) | **The thing built or managed** — "the site, premises, plot, block or unit the record is about — 18 River Court, Plot 4 Kilnfield, Unit 3B Harbour Works". Calls it "the single most load-bearing unheld concept in the family" |
| `construction_property.development-appraisal` | The **land that outlives the scheme** — "a site outlives every scheme ever appraised on it" |
| `construction_property.subcontract` | The site an engagement is carried out at — **and says it is the sibling where `property` is *least* often the right root**, because the compliance half of the row has no property at all |
| `construction_property.variation-claim` | The unit a change is instructed at — **and grades its own datum "weak"**: a variation anchors to a contract far more reliably, and multi-plot instructions carry several properties or none |
| `finance.household-property` | The **durable household subject** — "42 Oak Street"; the thing that holds a title register, closing packet, tax bill, inspection, improvement invoice and warranty together while their issuers change |

### 1d. `operating_authority` — 4 rows

| `domain_id` | The role the row actually needs named |
| --- | --- |
| `resource_operations` (schema) | "the right, tenure, licence, concession, quota or connection agreement under which the holder operates" — "Mining Lease ML-2048 / Water Abstraction Permit WA-73" |
| `resource_operations.grid-connection` | "Connection Agreement CA-SS03-2048" |
| `resource_operations.mining-operations` | "Mines Act Permit M-2048 / Quarry Permission QP-73" |
| `resource_operations.oil-gas-operations` | "Lease OCS-G 12345 / approved drilling consent WONS-DRL-0042" |

**`operating_authority` is not an entity key and does not belong in this cluster.** All four values
are *instrument identifiers*, not organisations, and `resource_operations` says so explicitly:
"Government may hold the same identifier in its issuer-side case, but this key represents the
operator's enduring authority and its conditions, **not the issuing agency**." See §6.

### 1e. Other keys in the corpus naming an entity, institution, firm or custodian

Found by reading all 170 proposal instances, not by keyword.

| `domain_id` | key | Role |
| --- | --- | --- |
| `law_practice` (schema) | `our_firm` | **Holder-as-author.** Reuse of the canonical key; wanted only so the *side* is resolvable, never as a level |
| `law_practice` (schema) | `client` | **Sell-side counterparty.** Canonical already; asks that eligibility be conditioned to FALSE-unless-approved for this family |
| `creative` (schema) | `client` | **Commissioning organisation**, counterparty role, "never the maker's own studio" |
| `manufacturing.supplier-qualification` | `supplier` | **Buy-side counterparty.** "here the holder is the customer and the counterparty is the seller, so reusing `client` would invert the relationship on every file" |
| `retail_hospitality.supplier-order` | `supplier` | Trading counterparty bought from; "`client` is the opposite role" |
| `logistics` | `carrier` | **Bailee in transit.** A consignment note "routinely names three organizations — consignor, consignee and carrier — in three different roles on one page" |
| `engineering.standards-library` | `issuing_body` | **Publisher of a normative document the holder merely holds.** "ASME". Proposed TRUE *and first* |
| `research.grants-funding` | `sponsor` | **Funder.** Row's own preference is (a) declare canonical `institution` on research, not (b) mint `sponsor` |
| `nonprofit` | `sponsor` | Funder, from the grantee side; adds that funder and grantee are **both nonprofits in one corpus**, so the same gazetteer string occupies both roles |
| `career.employment-records` | `employer` | **Employer of record.** `our_firm` is the nearest key and is correctly ineligible, so a destination-eligible employer key is genuinely new |
| `law_practice.corporate-secretarial` | `legal_entity` | **A registered legal person inside a group.** `organization` "would be exactly that [collector] for the parent while losing the subsidiary distinction that is the entire point" |
| `law_practice.corporate-secretarial` | `entity_registration_number` | Registry identifier; proposed "precisely so that it can be forbidden as a folder level in the same breath" |
| `law_practice.opinions-advice` | `addressee` | **The party entitled to rely** — an agent bank, a syndicate, an audit firm, a regulator; routinely *not* the client. Row's own first preference is to **decline** and keep it a literal observation |
| `finance` (schema) | `account_holder` | Person-side counterpart of `institution`; 00's own finance role split |
| `clinical_practice` | `subject_of_record` | The person a record is **about** |
| `nonprofit` | `subject_of_record` | Beneficiary, service user, safeguarded person |
| `law_practice` (schema) | `subject_of_record` | "HERE THE SUBJECT IS ROUTINELY NOT THE CLIENT" |
| `law_practice.depositions-testimony` | `subject_of_record` | A deponent — "frequently a NON-PARTY with no relationship to the holder… at all" |
| `law_practice.estates-administration` | `subject_of_record` | A **deceased** person, who is not the client (the executor is) |
| `law_practice.expert-materials` | `subject_of_record` | A producing non-party — "neither the holder, nor the holder's client, nor an adverse party, nor a subject at all" |
| `hr` | `workforce_unit` | **Internal unit** — "`organization` … cannot also mean a department, legal entity, cost centre, location, or reporting population without becoming a giant ambiguous field" |
| `academic.study-abroad` | `host_school` | Host institution vs home institution — the academic instance of the same shape |

**Custody-of-things keys, adjacent and load-bearing** (8 `asset` rows: `manufacturing`,
`manufacturing.asset-register`, `engineering.commissioning-handover`, `logistics`,
`resource_operations`, `resource_operations.grid-connection`,
`resource_operations.mining-operations`, `resource_operations.oil-gas-operations`;
plus `finance.vehicle-records::vehicle` and `law_practice.conveyancing::title_reference`).
All 8 `asset` rows are `destination_eligible: true`, `reliability_ceiling: validated`, and every one
after the first says SECOND-DO-NOT-MINT. **`asset` is the cleanest, most disciplined proposal in
this cluster and needs no adjudication beyond a yes.**

---

## 2. How many distinct entity ROLES the corpus actually contains

### Plainly: one key does not suffice, and it is not close.

`organization` as a single key would answer *whose drawer the file is in* and nothing else.
`business_operations.contract-administration` states the consequence in its own words: it "would
still not disambiguate a supplier contract from a customer contract; it would only say whose drawer
the file is in. That is worth having, and this row says plainly that it is less than it looks."

The corpus names **nine distinct organisation roles**. Two have canonical keys, one has a canonical
key scoped to the wrong domain, four have proposals, and **two have no key and no proposal at all**.

| # | Role | Status | Rows |
| --- | --- | --- | --- |
| 1 | **Holder-as-author** — the firm producing the document | canonical `our_firm`, dest=false | `law_practice`; role_split on `business_operations`, `construction_property`, `construction_property.subcontract`, `business_operations.contract-administration` |
| 2 | **Holder-as-custodian** — whose operating record this is | **proposed** `organization` | 11 of the 14 §1a rows |
| 3 | **Sell-side counterparty** — who the holder acts for | canonical `client`, dest=true | `law_practice`, `creative` |
| 4 | **Buy-side counterparty** — who the holder buys from | **proposed** `supplier` | `manufacturing.supplier-qualification`, `retail_hospitality.supplier-order`; hole recorded at `business_operations`, `business_operations.contract-administration`, `construction_property`, `construction_property.subcontract` |
| 5 | **Bailee in transit** | **proposed** `carrier` | `logistics` |
| 6 | **Funder / sponsor** | **proposed** `sponsor` (both proposers prefer reusing `institution`) | `research.grants-funding`, `nonprofit` |
| 7 | **Third-party assessor / certifier / publisher / regulator** | **NO KEY, NO PROPOSAL** for the assessor sense; `issuing_body` proposes the publisher sense only | `business_operations.compliance-audit` (open_question 3), `business_operations.facilities-workplace`, `engineering.standards-library` |
| 8 | **Assessed / obligated subject entity** | **NO KEY**; two rows try to borrow `organization` for it | `business_operations.compliance-audit`, `business_operations.corporate-regulatory-filings` |
| 9 | **Registered legal person inside a group** — subsidiary vs parent | **proposed** `legal_entity` | `law_practice.corporate-secretarial` |

Adjacent but genuinely separate families, not counted in the nine:

- **Employer of the holder as an individual** — `employer` (`career.employment-records`). It is not
  role 2: an employer is not a corpus custodian, and 00 gives it a folder level by name (§4).
- **Internal sub-unit** — `workforce_unit` (`hr`). Five of the fourteen `organization` rows write
  "the entity **or internal unit**", which is exactly the conflation `hr` refuses: a key that means
  entity-or-department-or-cost-centre-or-location "becom[es] a giant ambiguous field".
- **Person-side roles**, which the same evidence surfaces and which must not be folded into an
  organisation key: `subject_of_record` (6 rows), `account_holder` (`finance`), `addressee`
  (`law_practice.opinions-advice`).

### The design's own pair is two of nine, and the corpus proves it

00 line 44: *"The agent should model these as distinct facets, such as authored_by and
target_school, or our_firm and client."* That pair covers roles 1 and 3. Roles 4, 7, 8 and 9 are
each independently evidenced as neither, by rows that state it as a refusal rather than a wish:

- Role 4: `manufacturing.supplier-qualification` — "reusing `client` would invert the relationship
  on every file."
- Role 7: `business_operations.compliance-audit` open_question — "THE ASSESSOR ROLE HAS NO KEY.
  This row's documents carry two organisation roles at once — the party assessing and the party
  assessed — and one `organization` key cannot hold both."
- Role 8: same row, the other half.
- Role 9: `law_practice.corporate-secretarial` — `client` fails because "a corporate group hands one
  engagement fifty subsidiaries, most of them dormant, none of them separately instructing."

**This is a gap in the design, not a contradiction of it.** 00 is canonical on intent, and the
intent is the rule at line 44 — separate roles of the same entity type. The design gave two
worked examples (`our_firm`/`client`, `school`/`target_university`) and did not claim the list was
closed. Nine roles is what applying 00's own rule to the corpus produces.

### The three roles worth minting, and the four worth refusing

The north star is retrieval, not completeness. A role earns a key when it changes where a file goes
or what protects it. On that test:

**MINT (3):**
- `organization` (role 2) — custody. Nothing else separates two entities' papers on one machine.
- `supplier` (role 4) — the only cluster key whose proposers both call it *the browse level*:
  `manufacturing.supplier-qualification` — "the level a person actually reaches for when asked
  whether a supplier may still be used."
- `issuing_body` (role 7), **widened** from `engineering.standards-library`'s publisher sense to
  cover assessor, certifier and publisher. This closes the corpus's loudest named hole without
  minting a key no row proposed — `issuing_body` is proposed, and the assessor is an issuer of a
  document about someone else. If it is refused, `business_operations.compliance-audit` loses the
  only fact separating its own audits from its suppliers' evidence packs.

**REFUSE or defer (4):**
- Role 8 (assessed subject) — it is `organization` read on a document the holder did not author.
  Once role 7 exists, the assessor is named and the remaining entity token is the assessed one.
  Two keys, three roles, no third mint.
- Role 5 `carrier` — one row, and `logistics` itself invites refusal: "R1c may reasonably seed it
  ineligible and let a template validator promote it." It is a value of `supplier` in the sense that
  matters for filing.
- Role 6 `sponsor` — **both** proposers prefer reuse. `research.grants-funding`: "the
  recommendation to R1c is (a) declare the existing canonical key `institution` on the research
  schema… rather than (b) minting `sponsor`. Reuse is preferred because a second organization key
  that means what an existing key already means is exactly the 574's failure mode." Take (a).
- Role 9 `legal_entity` — real, but it is a subsidiary-resolution problem, and the row supplies its
  own fallback: "if a fifth key is refused, the honest fallback is `organization` carrying an entity
  value plus a note that subsidiaries and their parent collapse; do not mint a second entity
  synonym."

---

## 3. `destination_eligible`, per key

The prohibition, quoted so it can be argued with rather than restated: 00 line 44 — *"It should
avoid using authorship or creator identity as a destination dimension. A folder should not become
a collection point for everything produced by the same person or organization."* And line 97's
validator: *"The engine validates that the proposed template does not repeat a parent dimension,
create meaningless one-child levels, exceed practical depth limits, **use an author or organization
merely as a collector**, expose protected information, or produce empty branches when tested against
the accepted group."*

**The prohibition is narrower than the corpus has been reading it, on three counts.**

1. It is scoped to **produced by**. "everything *produced by* the same person or organization" is
   authorship. Custody is not authorship: a person keeping their employer's board pack did not
   produce it. `business_operations` makes this distinction correctly and then applies the
   prohibition anyway.
2. The validator's word is **merely**. "use an author or organization *merely* as a collector" is
   not a ban on organisation levels; it is a ban on organisation levels that do no separating work.
   That is a test against the accepted group, and 00 says where it runs: *"produce empty branches
   when tested against the accepted group"* — template time, not field time.
3. **00 itself places a company first in a folder template.** Line 70: *"a Career template may
   define **company → role or recruiting cycle → document type**."* An organisation is the first
   folder level in one of the six launch domains, written by the design. Any reading of line 44
   that forbids all organisation levels contradicts line 70. The reading that satisfies both is:
   authorship-side identity is banned; an entity in a non-authorship role is eligible when it
   separates.

### Recommendation per key

| Key | `destination_eligible` | Reasoning |
| --- | --- | --- |
| `organization` | **false**, template-time promotable | Correct as the 11 custody rows seed it. In a single-entity corpus it is the "merely a collector" level *and* a "meaningless one-child level" — both validator failures at once, as `business_operations.facilities-workplace` says. But false must mean *seeded* false, not banned: promotion is licensed by 00's own *"The system recommends an order based on the domain template, but the user can reverse, remove, add, or flatten dimensions."* |
| `supplier` | **true** | It is a counterparty, not authorship; the prohibition does not reach it. Both proposers seed it true, and `manufacturing.supplier-qualification` gives the retrieval reason. Same standing as canonical `client`. |
| `issuing_body` | **true** | `engineering.standards-library`: "It is a publisher, not authorship and not a person, so 00's ban on authorship as a destination does not reach it," and every real standards shelf is shelved by body. Extend with one condition: eligible **only** in the publisher/certifier sense, never as a re-entry for the holder's own name. |
| `site` | **true** | A place, not a person, not an author. Nine of ten rows seed true. |
| `property` | **true** | Same. `construction_property`: "It is a place and a subject, not a person and not an author, so 00's own prohibition… does not reach it." |
| `asset` | **true** | All 8 rows. With `manufacturing.asset-register`'s restriction: a *multi*-asset register export has no single value and must sit at site level. |
| `employer` | **true** | 00 line 70 licenses it by name. |
| `our_firm` | **false** | Unchanged. Canonical, correct. |
| `client` | **true**, with a per-family FALSE-unless-approved override | Canonical true. `law_practice` asks for the override with a disclosure reason: a client-named folder "publishes that a named person or company is in a legal matter". `creative` asks for no override. **`canonical_fields.json` cannot express a per-schema eligibility difference today; that shape gap is the real finding and both rows say so.** |
| `subject_of_record` | **false, on the key, never per-template** | Four rows ask for exactly this and give the reason: `nonprofit` — a folder named for a vulnerable third party "writes their identity into the filesystem, which is the opposite of *'The default posture must therefore be local-first and data-minimizing.'*"; `law_practice.estates-administration` adds that it must not become eligible on user approval either, because a folder named for a dead person "writes a bereavement, and the surviving family who share the machine did not choose that label." |
| `account_holder`, `entity_registration_number`, `addressee`, `workforce_unit` | **false** | Search/privacy/join only. `entity_registration_number`'s own text: proposed "precisely so that it can be forbidden as a folder level in the same breath". |
| `legal_entity` | **conditional — user-approved only, never automatic**, as proposed | If minted at all; §2 recommends the fallback instead |

### The dissent, weighed

`business_operations.corporate-regulatory-filings` is the one row that argues a concrete
multi-entity case against the seeded-false default: one person who is a director of two companies,
whose confirmation statements sit in the same Downloads folder, where the obligated entity is the
only separating fact. The row asks that its vote be weighed "ABOVE the family's average".

**The dissent is right about the facts and does not require a different seed.** Its own case is a
multi-entity corpus, which is exactly the condition under which the template-time promotion fires.
Seeded-false plus promotion gives that user the level; seeded-true would give every single-entity
user a one-child vanity level. The dissent's real complaint is not about the seed — it is that
without the key existing *at all*, "this row loses the only fact that separates two entities'
returns from each other." That is an argument for **minting the key**, which §2 accepts, not for
seeding it eligible.

*(The brief names this row `business_operations.statutory-filings`. No such row exists; the
corpus row is `business_operations.corporate-regulatory-filings`, and its argument is as
described.)*

---

## 4. `reliability_ceiling`, per key, and what would raise it

Contract rule 4: the states are §3.13's only, an extractor may only ever write `direct` or
`possible`, and "a field claiming `validated` is claiming a RULE will confirm it, which means the
`recognition.deterministic` entry must actually support that."

| Key | Recommended ceiling | What would raise it |
| --- | --- | --- |
| `organization` | **`possible`** | A labelled entity slot — a certificate's scope-of-certification block, an audit report's "entity audited" line, a statutory form's registered-number field, a document-control block's owner-organisation cell — would license `direct` on that document. `validated` needs a gazetteer-plus-context rule family (R4 owns the gazetteer, R2 the rule) that does not exist. |
| `site` | **`possible`** | A labelled Plant / Site / Facility / Depot / Warehouse / Store / Branch / Outlet / Field / Lease / Mine slot licenses `direct`. `validated` needs `retail_hospitality`'s stated family: a trade-name-plus-location gazetteer hit backed by a literally-labelled header or export column. |
| `property` | **`possible`** for the construction sense; **`direct`** for `finance.household-property` | `finance.household-property` names its own rule: "an explicit Subject Property, Property Address, Premises, Parcel, Title Number or equivalent labelled slot on the record itself; filename and free-text mentions remain possible". `validated` needs `construction_property`'s address-plus-role family — a postal-address pattern co-occurring with a role term in the same labelled zone, the same pattern-plus-context shape 00 uses for a course code. |
| `supplier` | **`possible`**, `direct` from a labelled slot | `manufacturing.supplier-qualification`: `direct` "only from a labelled Supplier, Vendor, Supplier Code or Manufacturer slot inside an assessment, submission or approval structure"; `validated` "would require a local supplier-master or approved-list cross-check plus that labelled-role context". |
| `issuing_body` | **`possible`** | `engineering.standards-library` claims `direct` from a labelled cover or foreword slot, and `validated` from a body-name or designation-prefix token co-occurring with one normative-document structure. That is a real family for *standards*. It does not transfer to the assessor sense, where nothing labels the assessor. |
| `asset` | **`validated`** — the only key in this cluster that earns it | An asset tag is a structured identifier in a labelled slot inside a maintenance/calibration/handover structure, not a name in prose. All 8 rows claim it and their `recognition.deterministic` entries carry the structure. |
| `carrier` | **`possible`** | `direct` only from a labelled Carrier / Haulier / Forwarder / Shipping Line / Airline slot. |
| `employer` | **`possible`** | Claimed `validated` by `career.employment-records`; unsupported today because the career schema declares no `recognition` that confirms an employer name, and D1 defers career fields entirely. |

### Three declared ceilings that their own rows contradict — flag for the owner

1. **`business_operations.compliance-audit::organization` declares `validated`** while its own
   `reliability_why` says "A letterhead or a filename yields `possible` at best; an entity name is
   constitutionally never-alone here **and is worse than usual, because an audit report's letterhead
   is the ASSESSOR's, not the assessed's**." Its `recognition.deterministic` confirms an *audit*,
   not an entity name — entry 5 reads "a named auditor or firm **distinct from the entity being
   audited**", i.e. the rules see two firms and do not say which is which. Under contract rule 4
   this is a `validated` claim with no rule behind it. **Should read `possible`.**
2. **`business_operations.policy-handbook::organization` declares `validated`** with the same
   `possible`-at-best prose. Its strongest deterministic signal is a document-control block, which
   confirms a policy, not whose policy. **Should read `possible`.**
3. **`retail_hospitality::site` declares `validated`** while its own sibling
   `retail_hospitality.supplier-order` and all eight other `site` rows declare `possible`. Retail's
   `rule_family` is genuinely stronger than the others' — it names a labelled-column rule — but a
   family cannot carry two ceilings for one key. **Resolve to `possible` with a documented
   promotion path**, or accept `validated` and raise all ten.

**Read across the whole cluster: every entity-name key belongs at `possible` and every
labelled-identifier key (`asset`, and the instrument family in §6) belongs at `validated`.** That
line is the cluster's real signal, and 00 states why at line 63: *"A university name alone should
not create a group because Columbia can appear as an authoring school, course provider, target
institution, employer, research venue, or merely a cited organization."* Read across to a company
name and the roles multiply, which is exactly what §2 enumerates.

### The failure mode four rows independently predict

A rule that reads the strongest entity token on the page will name **the wrong role**, and the
error is systematic, not random:

- `business_operations.facilities-workplace` — "the entity name most reliably present on this row's
  files is the CONTRACTOR's or the certifying body's… not the occupier's. A rule reading the
  strongest entity token would systematically name the supplier as the holder."
- `business_operations.it-asset-inventory` — "the entity name most reliably present on an asset
  register is often the VENDOR's… Reading the strongest entity token would systematically read the
  wrong role."
- `business_operations.risk-register` — "the entity names most reliably present… are the SUBJECTS
  of the risks — a named supplier, a named regulator, a named competitor… A rule that read the
  strongest entity token would systematically read a threat as the owner."
- `business_operations.contract-administration` — "its own richest source of entity strings — the
  parties block — is the WORST one for this key, because it yields two entity names of equal
  prominence and no role marker."

**This is the strongest single argument in the cluster for minting role 7 (`issuing_body` widened).**
The most-present entity name on these files is real and extractable; it is simply the *assessor's*.
Give that name a key and it stops competing for the custody slot. Refuse the key and every one of
these four rows is left telling the extractor to ignore its best evidence.

---

## 5. `site` vs `property` vs `organization` — three keys, and one hierarchy that is not the one being asked about

### Not one hierarchy. Three keys, of which two are role-split against each other.

**`site` and `property` are the same entity type in different roles** — a place — and 00's line-44
test therefore requires them to be distinct facets:

- **`site` = a place the holder OPERATES FROM.** `manufacturing`: "the facility that performs
  production or controls an asset". `logistics`: "the *facility holding the goods*, never as any
  address printed on the document". `retail_hospitality`: "ONE physical operating location inside
  one entity, at which work happens and against which records are keyed".
- **`property` = a place the record is ABOUT.** `construction_property`: "THE THING BUILT OR
  MANAGED". `finance.household-property`: the durable subject a title register, tax bill and
  warranty all concern.

They collide on the same string: a shop's address is a `site`; the same address in a lease being
transacted is a `property`. `resource_operations.mining-operations` already draws the line —
"`construction_property` `property` is a project or property role" — as does
`construction_property` when it refuses `location` for carrying a *capture* reading. **Two keys,
role_split against each other, is the answer the corpus's own logic forces.** Folding them gives one
key with three readings (operate-from, be-about, was-captured-at), and the third is already a
separate canonical key.

### The facilities claim that site outranks entity is correct, and stronger than stated

`business_operations.facilities-workplace`: "the level a facilities corpus actually wants above
everything is the SITE, not the entity. A multi-site single-entity corpus gets one meaningless child
from `organization` and loses nothing."

`retail_hospitality` makes the same claim from the other side and generalises it: "A trading corpus,
by contrast, genuinely spans several sites and channels under ONE entity, which is precisely why
`site` is eligible where `organization` is not."

**Both are right, and the reason is structural rather than domain-specific.** The normal shape of an
operating corpus is *one entity, many sites*. Putting `organization` above `site` therefore produces
a one-child level in the ordinary case — 00's *"It should recommend flattening when a dimension does
not materially improve retrieval."* applies directly. **`organization` is not a parent of `site`.
It is orthogonal**: it separates *whose corpus*, which in a single-entity machine is a constant.

### The hierarchy that IS real

The operational rows do describe a containment hierarchy, and it does not include `organization`:

**`site` → `asset`**, with the instrument family (§6) hanging off either.

- `resource_operations::asset` — "It is optional beneath site."
- `resource_operations.mining-operations::asset` — "Useful beneath site when several pits, faces,
  benches or fixed plant units coexist."
- `resource_operations.oil-gas-operations::asset` — "normally the intelligible parent below site".
- `manufacturing.asset-register::asset` — the constraint that proves the direction: a *multi*-asset
  register export "has no single value and must not be forced under an asset level; it belongs at
  the **site** level as the site's population document."

That is 00's parent-makes-child-intelligible rule satisfied at every step, and it is the folder
shape an operational user actually wants.

### Recommended shape

```
site        (place operated from)   dest=true   possible    role_split ↔ property, location
property    (place recorded about)  dest=true   possible    role_split ↔ site, location
asset       (unit within a site)    dest=true   validated   optional beneath site
organization(whose corpus)          dest=false  possible    NOT a parent of site; template-time promotable
```

### Two open items inside `site` the corpus has not settled

- **Is a non-physical channel a `site`?** `retail_hospitality` reads yes ("`Shopify - UK store`") and
  says explicitly "NOT YET SETTLED… R1c owes the ruling and `retail_hospitality.ecommerce-ops`
  depends on it." Recommend **yes**: the key's real content is *trading unit against which records
  are keyed*, and a channel satisfies it. The alternative strands a whole template.
- **Which site, when a file names several?** `retail_hospitality.supplier-order`'s value is the
  **deliver-to** unit, which "for a head-office corpus is not the same unit as the one that placed
  the order"; `logistics` counts four place roles on one page. The definition must be pinned to the
  facility *whose record this is*, not to any address printed on the document — `logistics`' own
  words — or `site` acquires the ambiguity `organization` already suffers from.

---

## 6. Two findings the brief did not ask for, inside the cluster it did

### 6a. `operating_authority` is a permit key, and it is one concept under three names

All four `operating_authority` rows define an *instrument*, not an entity. So do two more rows under
different spellings:

| `domain_id` | key | Value shape |
| --- | --- | --- |
| `resource_operations` + 3 children | `operating_authority` | "Mining Lease ML-2048 / Water Abstraction Permit WA-73" |
| `manufacturing.environmental-compliance` | `authorisation` | "EPR-AB1234"; "should hold a labelled Permit, Licence, Consent, Authorisation or Registration number, **never a regulator's name**" |
| `engineering.aerospace-airworthiness` | `approval_instrument` | "Supplemental Type Certificate ST-0442-AV" |

Six rows, three schemas, three spellings, one concept: *the externally issued permission, carrying
numbered conditions, under which the holder may operate.* All six are `destination_eligible: true`
and `reliability_ceiling: validated`, and all three definitions are interchangeable.

**This is precisely the near-duplicate defect D6 exists to kill, and it survived because the three
rows are in three different families and each one checked only its own neighbours.** Recommend
adjudicating them as **one key**. On the merits `authorisation` is the best of the three names —
`operating_authority` reads as an *organisation* (it misled this brief), and `approval_instrument`
is narrower than the concept. `manufacturing.environmental-compliance`'s "never a regulator's name"
should become part of the key's definition.

`engineering.aerospace-airworthiness` names its own alternative honestly — widening the proposed
`revision_or_baseline` — and that is worth considering before minting anything.

### 6b. The supply-side hole in `business_operations` is wider than the corpus believes

`business_operations`'s role_split says the buy-side role has no key "which is why `supplier` is
proposed on the contract-administration template rather than smuggled in here."

**`business_operations.contract-administration` proposes no such key.** Its `proposed_fields` are
`organization` and `fiscal_period` only, and its own role_split says the opposite: "This row
deliberately does NOT mint a `supplier` key."

So the buy-side role is proposed **nowhere** in `business_operations` or `construction_property`.
The only `supplier` proposals in the corpus are in `manufacturing` and `retail_hospitality`. Four
rows record the hole in `role_split` prose — `business_operations`,
`business_operations.contract-administration`, `construction_property`,
`construction_property.subcontract` — and each believes another row is carrying it. None is.

Consequence for §2: adopting `supplier` is not a manufacturing/retail convenience. It closes a hole
that four business_operations and construction_property rows independently identified and each
deferred to a proposal that does not exist.

---

## 7. What I recommend, in one place

**Mint into `canonical_fields.json` (7 keys):**

| key | dest | ceiling | role_split with |
| --- | --- | --- | --- |
| `organization` | false (template-time promotable) | possible | `our_firm`, `client`, `issuing_body` |
| `supplier` | true | possible | `client` |
| `issuing_body` (widened to assessor/certifier/publisher) | true | possible | `organization` |
| `site` | true | possible | `property`, `location` |
| `property` | true | possible (direct on `finance.household-property`) | `site`, `location` |
| `asset` | true | validated | `site` |
| `employer` | true | possible | `our_firm`, `organization` |

**Adjudicate as one key, not three:** `operating_authority` / `authorisation` /
`approval_instrument` → recommend `authorisation`, dest=true, validated.

**Reuse, do not mint:** `sponsor` → declare canonical `institution` on `research` and `nonprofit`,
per both proposers' own first preference.

**Fallback, do not mint:** `legal_entity` → `organization` carrying an entity value, with the
subsidiary-collapse note the row itself offers.

**Decline, per the proposing row's own first preference:** `addressee`.

**Adopt as search/privacy-only, `destination_eligible: false` on the key:** `subject_of_record`,
`account_holder`, `entity_registration_number`, `workforce_unit`, `carrier`.

**Three things this adjudication cannot decide, which are the owner's:**

1. **`canonical_fields.json` has no way to express a per-schema `destination_eligible`.**
   `law_practice::client` and `law_practice.estates-administration::subject_of_record` both need
   one and both say so. Either the canonical shape grows a per-schema override, or the ban moves
   into the template contract. This blocks `client` on `law_practice` regardless of what is minted.
2. **Nothing here is reachable until `SCHEMA_IDS` grows.** 61 of the 67 proposals in this cluster
   sit on schemas `src/facts/domains.py:52` does not know. `property` on `finance` and `employer`
   on `career` are the two exceptions worth landing first — and `employer` additionally requires
   reversing D1's career deferral, which `_CONTRACT.md` rule 10 says must "arrive… explicitly rather
   than as a plan edit".
3. **Is a non-physical channel a `site`?** `retail_hospitality.ecommerce-ops` depends on the answer.

# law_practice.corporate-secretarial — research notes

Row: `law_practice.corporate-secretarial` · kind: template · schema: `law_practice` · launch: placeholder
Depth: J-DEPTH
Verdict: **node stands** (`refuse_node: false`), on three independent differences from the schema default.
Status: **SALVAGE.** A killed agent left the `.json` with no memo. I verified it line by line, repaired
four things, and own the result. Repairs are listed at the end under *What I changed in the salvaged draft*.

---

## 1. The charge against this row, stated at its strongest

Before anything else, the case for deleting this id. I take it in six forms, because five of them are
this project's recorded failure modes and one of them is the hard one.

**(a) It is a work_type value, not a node.** "Corporate secretarial" is a *practice area* — the thing a
firm prints on a capability statement next to "litigation" and "conveyancing". Practice areas are what a
practitioner sells, and the dispatch is unambiguous that `work_types[]` is an enum of values for a field,
never a request for a child node. The salvaged draft's own fifteen-item `work_types` list reads exactly
like a service catalogue, which is precisely what a service-line row would look like.

**(b) It is a bundle of document types.** Enumerate the members: register, minute, resolution, articles,
memorandum, certificate, consent. Every one is a document-type word. A row whose extension is a list of
document types is a document-type row wearing a collective noun.

**(c) It is `business_operations.board-governance` rotated by custody.** The same minute, the same
register page, the same confirmation statement exist in two hands. Custody is not a property of the
bytes. If the only difference is *who is holding it*, there is one node and a field, not two nodes.

**(d) It duplicates its own schema's default template.** This is the serious one. The `law_practice`
schema anchor declares no field rows, an empty `dimension_order`, `time_first: false`, and a
`potentially_sensitive` posture built on protecting a third party. This row declares no field rows, an
empty `dimension_order`, `time_first: false`, and `potentially_sensitive`. On the face of the JSON the
two are identical, and CONNECTION §2's node test says a template exists only when its detection signals,
recommended dimensions, or privacy rules differ from the schema's default.

**(e) Its only evidence is never-alone.** The anchor is a company name and a company number. Both are
struck in this row's own `never_alone` list. A row whose anchor it has itself disqualified cannot
activate — which is the exact shape `business_operations.organisational-records` refused on.

**(f) It is defined by an absence.** "Unexecuted", "unadopted", "draft", "blank execution block". A row
whose members are characterised by the *missing signature* is a row defined by absence, and absence is
struck by name in the design's own reasoning about missing EXIF.

That is the case. Below is why I think it loses, leg by leg — and where it comes closest to winning.

---

## 2. Defeating the charge

**(a) fails on the deletion test.** Nothing in this row's activation runs on the words "corporate
secretarial", "company secretary", or a chartered-secretary post-nominal; all three are struck in
`never_alone`. What fires are structures: a columnar ledger whose column set pairs a holder or officer
identity with an **entry** date *and* a **cessation / transfer-out** column; a formation packet of two or
more members under one entity identifier with at least one execution block blank; a multi-entity calendar
whose recurrence keys to an incorporation anniversary; an entity inventory whose *rows are legal persons*.
The consequence is the right one for a practice-area objection: a litigation-only practitioner who happens
to keep one client's register **fires this row**, and a firm advertising "corporate secretarial services"
on its letterhead **does not**. A practice-area label cannot do that; a structure can.

**(b) fails on the same test.** Delete every document-type word from a register page and what remains is
the paired entry/exit column structure and a repeated labelled identifier slot. Delete them from a
compliance calendar and what remains is anniversary-keyed recurrence across more than one entity. The
document-type word is never the discriminator — it is struck explicitly, in the terms
`business_operations.organisational-records` established: delete every entity name and every document-type
word, and if nothing structural survives, nothing fires.

**(c) fails structurally, not merely by custody.** This matters, because a custody-only seam would be
untestable. `business_operations.board-governance`'s anchor is **a body and its cycle**: a notice, an
agenda, a numbered pack, attendance, quorum, a minute of a meeting that *happened*. This row's
characteristic artefacts have no cycle at all. A register of members is a **running state**, not an event.
A formation packet **precedes the existence of any body**. A resolution draft is a meeting that has not
occurred, with the attendance and quorum lines still placeholders. An entity inventory contains no meeting
of any kind. There is no custody under which `board-governance`'s signals produce a register of members —
so the two rows are not the same row seen from two sides.

**(d) is defeated three times over, and each leg is independent.** CONNECTION §2 needs one; there are
three.

1. **Detection signals differ — and this is the strongest leg, because without the difference the family
   does not activate at all.** The `law_practice` schema default requires BOTH of two legs: (i) an exact
   matter, file or engagement reference repeated across two or more artefacts, and (ii) at least one
   artefact whose own labelled slots separate a **practitioner or firm** role from a **client** role.
   **Leg (ii) does not fire on this family's characteristic file.** A register of members has columns for
   *holders*; a register of directors has columns for *officers*; a formation packet names *subscribers
   and incorporators*. None carries a practitioner slot or a client slot anywhere on the page — the
   practitioner is invisible on the artefact they maintain. Under the schema default alone, this entire
   family fails the second leg and falls to Protected Records or Review Later. This template earns its
   existence by **substituting leg (ii)** with an entity-registration-number-shaped token in a *labelled
   slot*, repeated across two or more artefacts, with leg (i) held unchanged. That is a different
   activation test, not a decoration on the same one.
2. **Recommended dimensions differ structurally.** The schema default's prose recommendation is: client
   (only where the corpus genuinely spans more than one and the user has approved it) → **matter** →
   document function → period. This row **inverts the second level and drops the matter entirely**:
   entity → function → period. The reason is a fact about the work, not a preference. Corporate
   secretarial is a **perpetual retainer**, not a matter with a start and an end; one engagement routinely
   spans fifty entities and one entity routinely outlives a dozen matters. A matter level here would hold
   one child forever, which is what 00's template validator strikes when it checks a proposal does not
   "create meaningless one-child levels". Period is genuinely load-bearing here, unlike in the schema
   default, because the world is anniversary-cyclical — the same four functions recur every year per
   entity — and still **not** `time_first`, on 00's own rule that "For document and record domains,
   project, function, or subject usually comes before time because putting year first scatters related
   work across calendar folders."
3. **Privacy rules differ in a specific, nameable direction.** The `law_practice` schema's privacy premise
   is a third-party **client** who never chose this filesystem. This row's protected subjects are not the
   client and often have no relationship with anyone in the engagement: **registered members, beneficial
   owners, and directors whose residential addresses the register carries**. The asymmetry is sharp and
   easy to get backwards, so state it: a register of directors' residential addresses and a
   significant-control register carry precisely the column that the *public registry copy deliberately
   suppresses*. The public twin is therefore never an argument for a permissive default — the private copy
   holds strictly more, and its existence additionally discloses a service relationship that no registry
   publishes. That is a privacy rule the schema default does not state.

**(e) fails because the anchor is a join, not the evidence.** Entity name and entity number are both
struck; what activates is the **structure** plus a labelled-slot identifier **repeated across two or more
artefacts**. The number's job is to join a register page, a formation packet, a calendar row and an
inventory row whose filenames share nothing — which is what 00's grouping stop rule demands, since "It
should not form a supported group when there is no valid anchor". A join token that is insufficient alone
and necessary for grouping is not the same thing as evidence.

**(f) is conceded in part and then defeated.** "Missing execution block" is struck **by name** in
`never_alone`, precisely because a scanned register page has no execution block either, and neither does a
compliance calendar or an entity inventory. What fires is **positive** structure: open **[DATE] / [NAME]
attendance and signature placeholders co-occurring with a filled entity recital and a version marker**.
That is a document that says what it is, not a document missing something.

**Where the charge comes closest to winning, stated honestly.** If R1c refuses `legal_entity`, leg 2 of
the (d) defence weakens — the dimension argument becomes advisory prose with no key to branch on. The row
would then rest on legs 1 and 3, which is enough under CONNECTION §2 but is a thinner row than this memo
describes. That fragility is recorded as NJ-LP-CORPSEC-2 rather than smoothed over.

---

## 3. Files considered and rejected

Named false positives. Each shares real tokens with this row's evidence and is not this row's evidence.

| File | Why it is tempting | Why it is not this row |
|---|---|---|
| `ACME Holdings Ltd - Invoice 04821.pdf` | Carries the entity name *and* the company number in the footer | The number is in the footer of every invoice, T&C page and privacy notice any company on earth produces. Structure is issuer + billed-to + line items → `finance`. |
| `Certificate of Good Standing - ACME Holdings Ltd.pdf` | Registry seal, entity number, official-looking | Purchasable by anyone for a small fee. Evidence about the **registry**, never about custody. → Independent Records. |
| `ACME Holdings Ltd - Annual Report and Accounts 2025.pdf` | Entity id + anniversary-derived date + statutory filing obligation | A financial statement. No register structure, no constitutional state. → `finance` / `business_operations`; the *filing* of it → `business_operations.corporate-regulatory-filings`. |
| `Board pack - March 2026 - ACME.pdf` | Resolutions inside it, entity named throughout | Numbered pack + agenda + attendance + a meeting that happened → `business_operations.board-governance`. |
| `Cap table - ACME - fully diluted.xlsx` | Names, share counts, percentages — looks like a register of members | Rows are **holders with instrument counts and amounts**, plus option pool, preference stack, round pricing → `finance.cap-table-equity`. |
| `Articles of Association - [COMPANY NAME] template.docx` | An unexecuted constitutional document, exactly this row's shape | Entity slots blank **by design across all entities** → `law_practice.precedent-bank`. |
| `Shareholders Agreement - executed.pdf` | Constitutional in substance | Bound party pair + execution block → `legal`, whose safety protection runs first. |
| `Confirmation statement CS01 - filed - receipt.pdf` | Produced by the same provider, from this row's register | Filing reference + authority acknowledgement + a deadline → `business_operations.corporate-regulatory-filings` (or `law_practice.regulatory-submission` on the practitioner side). |
| `Employment Contract - J. Smith - ACME Holdings Ltd.docx` | Entity name + a named officer | An employment instrument; the entity is the employer role, not the subject → `hr` / `career`. |
| A `Terms and Conditions.pdf` with a company number in the footer | Contains the family's join token verbatim | Nothing else. The clean demonstration that the join token alone is worth zero. |

Also rejected as a *family*: the whole "look, a company word" class — `Company documents/`,
`Corporate/`, `Statutory/` folders whose contents survive on nothing but an entity name and a
document-type word. Neither this row nor `business_operations.organisational-records` should activate
there, and naming it prevents the failure where a folder name is read as a corpus.

---

## 4. The collision fixture

**`Companies House - ACME Holdings Ltd - filing history and officers (downloaded).pdf`.**

It looks exactly like this row's best evidence: an officer list, appointment dates, resignation dates, the
entity name, the registration number in a labelled slot. It is not this row's evidence, and it is the
family's headline false positive because it is *cheap* — anyone may buy the registry record of any company,
so its presence is equally consistent with diligence on a counterparty, a KYC pack, or idle curiosity.

**What discriminates it:** the **maintained ledger has paired entry AND cessation columns and unfilled
future rows** — it is a running state awaiting the next entry. The **extract has a registry retrieval
timestamp, a document-purchase or transaction reference, and a snapshot date**, and no columns awaiting
anything: it is a rendering, not a ledger. Where the extract stands alone it falls through to Independent
Records; a registry stamp is struck absolutely in `never_alone`.

A second, subtler collision worth recording because it is the one an LLM will get wrong: **a multi-entity
schedule that is an entity inventory vs. one that is a cap table.** Both are workbooks of names, dates and
percentages with near-identical filenames. The discriminator is the **row-identity test** — rows that are
people make it an HR chart, rows that are **holders with amounts** make it a cap table, rows that are
**legal persons with jurisdictions and status tokens** make it this row's.

---

## 5. Reciprocal boundaries

Each stated in both directions, with the **same fixture named on both sides**.

Full signal text lives in the JSON's `collides_with`; this section records the *added* reasoning and the
shared fixture, not a second copy.

- **`business_operations.board-governance`** — the neighbour's landed row already writes this seam as a
  custody test (matter/engagement anchor → this row; the same minute held by the entity it is ABOUT → the
  neighbour). Adopted unchanged, plus the structural half §2(c) adds, which the custody test cannot reach:
  body-and-cycle vs. running state. **Same fixture:** `Written Resolution of the Sole Shareholder - [DATE]
  - DRAFT v3.docx` — provider-held with a service reference and open placeholders → this row; entity-held,
  signed, minuted into the board's own numbered sequence with attendance → the neighbour.
- **`business_operations.corporate-regulatory-filings`** — the neighbour asserts the same
  matter-and-engagement anchor. Sharpened in the other direction: its anchor is **an obligation to an
  authority with a deadline and a filing reference**, compelled from outside; the register it is derived
  from is compelled by nobody and would exist with no registry at all. **Same fixture:** `RE_ Confirmation
  statement due 14 May - please approve.msg` — approval thread and underlying register state → this row;
  submitted statement, filing reference and acknowledgement → the neighbour, even when one provider
  produced both.
- **`legal`** — inherited from the schema and conceded in full: every **executed** constitutional
  instrument is `legal`'s on its own execution-block evidence, and `legal`'s safety protection runs first.
  What is left here is the unexecuted and the non-instrumental. **Same fixture:** `Incorporation pack -
  Newco 3 - 2026.zip` — signed certificate member → `legal`; unsigned formation members → this row.
- **`finance.cap-table-equity`** — constitutional/determinative record vs. economic model. **Same fixture:**
  `Group entity list - jurisdictions and status - Q1 2026.xlsx`, discriminated by the row-identity test in
  §4. A workbook carrying both a members sheet and a fully-diluted sheet is a two-schema file, not a
  contest, and the more protective reading governs.
- **`law_practice.regulatory-submission`** (sibling seam, must be drawn or the rows duplicate) — the
  sibling holds the **act of filing** on a client's behalf and its response; this row holds the entity
  record the filing is drawn from and **stops at the point of submission**. Where a registry filing is the
  only artefact, the sibling has it; where the register, resolution and calendar are present and the filing
  is one member of that set, the set is this row's and the filing artefact is the sibling's.
- **`law_practice.precedent-bank`** — both hold unexecuted constitutional documents. **Same fixture:** an
  `Articles of Association` DOCX — `[COMPANY NAME]` throughout → precedent bank; `ACME Holdings Ltd
  (12345678)` in the recitals with only the execution page open → this row.
- **`law_practice.transactional-deal`** — the landed sibling already routes a signing-authority pack's
  permanent register consequence here. Reciprocated: deal-generated corporate-action documents are the
  sibling's **while the deal is live**; the register entries they cause are this row's **permanently**.
- **`career`** — **added by me; the salvaged draft ignored a `must_consider` neighbour.** **Same fixture:**
  `Letter of Appointment - Non-Executive Director - J. Smith.pdf`. This row owns the appointment as an
  event in one legal person's constitutional state; `career` owns it as one line in one natural person's
  work history. Discriminated by **the join axis of the surrounding set**: an entity identifier repeated
  across artefacts with different *people* on them → this row; a person identifier repeated across
  artefacts with different *entities* on them → `career`. Corollary that matters more than the edge: a
  directorship listed on a CV is `career`'s and is never an officer record, because an entity name in a
  career document is the collector role 00 strikes.
- **`business_operations.organisational-records`** — the refusal-adjacent neighbour, edged so the mutual
  *non*-activation case is recorded: where a corporate-shaped file survives on nothing but an entity name
  and a document-type word, **neither** row fires.

### Neighbours considered and deliberately not edged

- **`finance` (schema, `must_consider`)** — reached through `finance.cap-table-equity`, which is where the
  only real contest lives. A bare schema edge would add nothing the child edge does not already carry.
- **`nonprofit.governance`** — a charity's trustee register and constitution are structurally identical to
  this row's evidence, and a provider running a charity's secretarial work is a real world. I did not mint
  the edge because the seam is already drawn at `business_operations.board-governance`, which
  `nonprofit.governance` collides with, and a third path risks a mutex triangle no row can adjudicate.
  **Recommendation to R1c:** consider `law_practice.corporate-secretarial` ↔ `nonprofit.governance` with
  the same keeper-for-another discriminator.
- **`identity`** — a formation or KYC packet routinely carries certified passport pages and proof of
  address. This is genuine co-activation, not a contest, so a collision would be wrong; and
  `also_holds_with` is barred here (see below). Handled instead as a `must_not_conclude` line on the
  archive example and as an R1c recommendation at schema level.
- **`hr`** — a directors' service contract and a secretary's employment terms are HR's. No fixture where
  both would claim the same bytes: HR's anchor is an employment relationship, this row's is constitutional
  state. Adjacency, not contest.
- **`law_practice.deadlines-diary`** — discriminated inside recognition rather than by an edge, because the
  test is clean and one-directional: recurrence keyed to an **incorporation anniversary** is this row's;
  dates running off a **limitation period or a listing** are the sibling's. Recorded here so R1c can
  promote it to an edge if it disagrees.

---

## 6. proposed_fields — justification

The row writes **no field rows** (`fields: []`); `law_practice` declares none under PR-6 / D1-as-narrowed.
Two keys are proposed for R1c, and neither is a synonym of an existing canonical key.

- **`legal_entity`** — the grouping axis is a **registered legal person**, which no canonical key holds.
  `client` is a *role in a representation*, and the entity here is routinely **not** the client: a corporate
  group hands one engagement fifty subsidiaries, most dormant, none separately instructing. `organization`
  (itself only a proposal elsewhere) is the collector sense 00's validator strikes — it rejects a template
  that would "use an author or organization merely as a collector" — and branching on it would collapse
  subsidiary into parent, losing the one distinction the row exists for. `institution` is the academic key.
  Ceiling `validated` via registry-identifier-plus-context; R2 owns the pattern, R4 any gazetteer.
  Destination-eligible **only** with user approval. *Fallback if refused:* `organization` carrying an entity
  value with an explicit note that subsidiaries and parent collapse — do not mint a second entity synonym.
- **`entity_registration_number`** — proposed for **search and join only, and proposed precisely so it can
  be forbidden as a folder level in the same breath**. It is the one exact token joining a register page, a
  formation packet, a calendar row and an inventory row whose filenames share nothing; without it the
  family has no anchor and 00's stop rule bites. But a folder named for eight digits is unintelligible, and
  a registration number is a **stable public handle** that would make a path externally resolvable to a
  named legal person, against "The default posture must therefore be local-first and data-minimizing."
  Ceiling `possible`; promotion to `validated` requires a labelled slot. No existing key holds a registry
  identifier — `account_type` is a finance shape, `record_type` is a document-function enum.

---

## 7. What I changed in the salvaged draft

The draft was strong and I kept the great majority of it. Four repairs, all of which I own:

1. **`also_holds_with` emptied.** It carried `{domain: "legal"}`. CONNECTION's edge table states
   `also_holds_with` is "schema <-> schema only" and this row is a **template**. The co-activation is real,
   so it is not discarded — it is re-routed to R1c as a schema-level assertion (NJ-LP-CORPSEC-4), together
   with a second one the draft had missed (`identity`).
2. **`role_split` emptied.** The draft's two entries used an unattested `{domain, signal, provenance}`
   shape *and*, more importantly, were not role splits: a role split is the same entity type held under
   **two different field keys**, and here it is the **same** subject key with an engagement anchor present
   or absent. That is a collision, and both entries duplicated `collides_with` content already present in
   full. The landed neighbour `business_operations.board-governance` is symmetric — it carries this row in
   `collides_with` with an empty `role_split`.
3. **`career` collision added.** A roster `must_consider` neighbour the draft never addressed, with a
   same-fixture-both-sides signal (the director appointment letter) and a join-axis discriminator.
4. **`identity` handling added** to the incorporation-packet example: a certified passport member inside a
   formation packet stays `identity`'s, on `identity`'s own evidence and its safety precedence.

**Verified and left unchanged:** all nine `collides_with` ids exist on the roster (**no dangling id** —
the sibling-salvage defect was checked for and is not present here); all fifteen `00` quotations grep back
**verbatim**; every `facts_legal` key is canonical (`file_type`, `creation_date`, `language`,
`version_family`, `sensitivity_status`, `duplicate_family`); every `source_type` is in `SOURCE_TYPES`; all
four `falls_through_to` names are among 00's nine residuals; `fields: []`; the key set matches the landed
sibling `law_practice.transactional-deal.json` exactly; no thresholds, no handling classes, no
`public_low`; ten file examples, each splitting observations from facts and none writing a path as a fact.

---

## 8. Sources used

`planning/domains/dispatch/RESEARCH-BRIEF.md`; the stamped assignment from `make_prompt.py`;
`planning/domains/nodes/law_practice.json` (schema anchor — fields, default template, recognition);
`planning/domains/roster.json` (every edge id and this row's own stamp); `planning/domains/canonical_fields.json`;
`planning/domains/CONNECTION.md` (edge table, §2 node test, PR-6); targeted greps of
`planning/00-database-agent-product-design.md` for each quotation; landed neighbours
`business_operations.board-governance.json`, `business_operations.corporate-regulatory-filings.json`,
`law_practice.transactional-deal.json`, `law_practice.closing-binder.json` (boundary text and house shape).

## 9. NEEDS-JOSEPH

- **NJ-LP-CORPSEC-1 — the conformed copy.** Does an adopted constitutional document reproduced *without*
  signatures and marked a true copy read as `legal` (an executed instrument, rendered) or as this row (an
  unexecuted document in the entity record)? Common file; the two readings give different protection.
  (a) `legal` — safest, consistent with safety-first ordering, but pulls most of a statutory book into a
  safety domain. (b) this row with `also_schema: legal` — preserves the corporate record's integrity but
  relies on a conformed-copy-vs-scanned-original distinction no filename supports. (c) Protected Records —
  cheap and reversible, but hollows out the row's best-populated function.
- **NJ-LP-CORPSEC-2 — may `legal_entity` ever be an automatic folder level once D1 lifts?** The entity's
  *existence* is public at a registry; the fact that this filesystem holds its constitutional record is not,
  and discloses a service relationship. (a) user-approved entity level (this row's provisional posture);
  (b) no entity level, entity search-only; (c) entity level permitted only where the corpus provably spans
  more than one entity.
- **NJ-LP-CORPSEC-3 — reciprocity.** Asserted here from two landed neighbours' own words, but this row may
  not edit them. R1c to confirm return edges on `business_operations.board-governance`,
  `business_operations.corporate-regulatory-filings`, `finance.cap-table-equity`,
  `law_practice.regulatory-submission`, `law_practice.precedent-bank`, `law_practice.transactional-deal`
  and `career`.
- **NJ-LP-CORPSEC-4 — `also_holds_with` on templates: the corpus is inconsistent.** CONNECTION says
  schema ↔ schema only, but landed sibling templates `law_practice.transactional-deal` and
  `law_practice.closing-binder` both carry schema ids in their own `also_holds_with`. This row took the
  stricter reading and emptied the field. (a) R1c lifts `law_practice ↔ legal` and `law_practice ↔ identity`
  to the schema anchor and normalises the sibling templates down; (b) the rule is relaxed for templates and
  this row's entry is restored. Needs one ruling, not two conventions.
- **NJ-LP-CORPSEC-5 — `nonprofit.governance` edge.** Deliberately not minted here to avoid a mutex triangle
  through `business_operations.board-governance`. R1c to decide whether the keeper-for-another
  discriminator warrants a direct edge.

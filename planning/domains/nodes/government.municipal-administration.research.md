# Research memo — `government.municipal-administration`

Depth: J-DEPTH
Date: 2026-08-26
Output: `planning/domains/nodes/government.municipal-administration.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, placeholder launch
Result: **REFUSED** (`refuse_node: true`)

## Result in one paragraph

The row names a tier of government, not a filing world. Everything in its `one_line_hint` —
"meeting agendas and minutes, reports to committee, local budgets, service performance reports and
local notices" — is already written into the `government` schema anchor as its own default
template: the anchor's deterministic list contains the governance-cycle recognizer, its
`work_types` contain "public-body agenda, committee report, budget, performance report, minute,
resolution, or public notice", its `grouping_reasons` contain "one public-body governance cycle",
and its `file_examples` already use a **council agenda pack** as the exemplar of that default. What
this row would add on top is the word *municipal*, and the same anchor's `never_alone` list already
forbids "a government department, regulator, **municipality**, legislature, court, public school,
archive, museum, or official-looking seal alone". A row whose entire increment over its schema is
never-alone evidence can never activate. It would be a row that never fires — and worse, a row that
attracts the council-tax bill in a resident's downloads folder for exactly the wrong reason.

## The charge — the strongest case that this row should not exist

I made this case before writing anything, in the six shapes the brief names.

1. **It is an organisation attribute (never-alone evidence).** "Municipal" is the *level* at which a
   body sits. The design's reasoning about organisation names transfers directly: *"A university
   name alone should not create a group because Columbia can appear as an authoring school, course
   provider, target institution, employer, research venue, or merely a cited organization."* A
   council likewise appears as issuer, counterparty, landlord, employer, grant funder, planning
   authority, or a name mentioned inside a housing association's board pack. Tier inherits the whole
   ambiguity and adds nothing to resolve it.
2. **It is a duplicate of its own schema's default template.** Verified, leg by leg, in the node test
   below. This is the decisive one.
3. **It is a duplicate of a neighbour.** `government.public-authority-record` sits on the same roster
   and is, by its id, the authority-side record row. Whatever corporate-spine residue survives after
   the function siblings take their share lands there or on the schema default, not here.
4. **It is a set of document types.** Agenda, minutes, report, budget, performance report, notice are
   document-type words. The brief and the stamped prompt both say document types are `work_type`
   values, and the anchor has already enumerated them as such.
5. **It is defined by breadth, i.e. by the absence of a single function.** The honest description of a
   municipality is "the authority that does *many* functions". Every one of those functions is a
   landed sibling. A row defined as "the rest of a council" is a row defined by what other rows do
   not take.
6. **It is a browse convenience.** A user may well want a Council folder. `parent_id` is browse-only
   and explicitly "Ignore it for activation"; wanting a folder label is not evidence that a template
   exists.

### The strongest case FOR the row, stated fairly

Two arguments are real and I tested both.

**(a) The multi-service document.** `Quarterly Service Performance Report Q1 2026-27.xlsx` has one
column naming waste, housing, planning, libraries and revenues in adjacent rows. No single function
sibling owns a document that spans all of them, and a general-purpose local authority is the only
kind of body that routinely produces one. **Defeated:** breadth is a property of the producing
organisation, not a detection signal. The anchor's governance-cycle recognizer already accepts an
authority-side performance report without asking how many services the body runs, and the resulting
facts (`file_type`, `creation_date`, `language`, `duplicate_family`, `version_family`,
`sensitivity_status`) are identical either way. Nothing downstream reads differently.

**(b) The half-exempt meeting pack.** `Item 12 - APPENDIX B - EXEMPT - Part II - Named Tenancy
Cases.pdf` sits in the same pack as publishable reports, and a rule that the publishable half must
never lower the exempt half's posture is a genuine privacy rule. **Defeated:** the anchor already
owns it. Its council fixture's `must_not_conclude` reads *"that every municipal agenda is
non-sensitive"*, and its `sensitivity_why` already names citizen casework, complaints, submissions
and pre-decisional work as the reason the schema default is `potentially_sensitive`. The rule exists;
it is one level up.

## The node test, argued in full

**The schema's default template, stated exactly** (from `planning/domains/nodes/government.json`):

- `template.dimension_order: []`, `time_first: false`, with the reason "Empty by contract: PR-6
  leaves this placeholder schema with no fields, and a template cannot branch on undeclared fields."
- Detection: role-structural. The relevant deterministic entry is *"a public-body governance cycle
  carrying an authority or statutory-body name, meeting date, agenda or committee identifier,
  attendance or apologies, numbered papers, and a minute, resolution, or decision section; a private
  company, charity, union, standards body, or member association with the same furniture is excluded
  by owner role"*.
- Privacy: `potentially_sensitive` by default, authority-side holdings protected, exempt/casework
  material to Protected Records.
- Its exemplar fixture for all of the above: `Council Housing Committee - Agenda Pack - 18 August
  2026.pdf`.

**Leg 1 — do the detection signals differ?** No. I attempted to write one that would survive. Every
draft reduced to *[anchor's governance-cycle signal] + [municipal / council / borough / county /
parish / town hall token]*. The added token is precisely what the anchor's `never_alone` list
excludes, so the composite signal has the same truth conditions as the anchor's signal alone. The
only other candidate — "a document naming three or more distinct public services" — is a heuristic
about organisational breadth, not about the file, and would fire on a national department's annual
report just as readily.

**Leg 2 — does the recommended dimension order differ?** No, and it cannot. `government` declares no
field rows under PR-6 (D1's deferral), so the schema's order is `[]` and any template's order is
`[]`. The identity is not merely an artefact of the empty-fields regime, which is why I did not treat
it as a technicality: even if government fields were ratified tomorrow, a council's agenda pack and a
ministry's board pack want the same organising anchor — bounded proceeding, then exact reference,
then work type — and differ only in whose letterhead is on the cover. `time_first` is false on both
sides for the same reason the anchor gives, quoting the design: *"For document and record domains,
project, function, or subject usually comes before time because putting year first scatters related
work across calendar folders."*

**Leg 3 — do the privacy rules differ?** No. Same default posture, same protected classes, same
residual. The one nuance I hoped would carry the row — the mixed public/exempt pack — is already in
the anchor's council fixture. There is nothing left to differ on.

Three legs, three identities. Under CONNECTION.md's node test a template exists only when at least
one of the three differs from its schema's default. This one differs on none.

## Files considered and rejected

These are the tempting false positives — files that would have made the row look inhabited.

- **`Council Tax Bill 2026-27 - 14 Elm Road.pdf`** — the most municipal-looking file on an ordinary
  drive, and not this row's evidence, nor the schema's. The addressee is the holder; the authority is
  the counterparty. The anchor excludes it explicitly: *"an authority-issued permit, licence, tax
  notice, benefit letter, identity card, visa, voting confirmation, filing acknowledgement, or
  registry extract held by the recipient"*. Kept in the JSON as the **collision fixture**.
- **`Board Pack - Riverside Housing Association - September 2026.pdf`** — identical governance
  furniture, non-public owner, and the word Council appears inside it as a stakeholder. Discriminated
  by owner role, which the anchor already tests. Second collision fixture, in the opposite direction.
- **A parking-penalty notice, a garden-waste renewal, a school-place offer** — all recipient-custody
  personal administration. Municipal letterhead, zero authority-side custody.
- **A published local plan or budget-consultation PDF downloaded by a resident** — publication by
  government is not custody. Reading Inbox.
- **A planning decision notice, a premises licence, a FOI disclosure log, a tender notice, a
  polling-station list** — each is a *sibling's* fixture (`government.planning-application`,
  `government.permit-licensing`, `government.public-records-foi`, `government.public-procurement`,
  `government.elections-administration`). Claiming them here would have created a second claimant
  deciding by the word *council* instead of by role.
- **A council employee's payslip, contract or work calendar** — the anchor's "government as industry
  or employer is not this schema".
- **A committee-management-system (modgov/Legistar-shaped) export** — already accepted by the anchor,
  which also already says manifests are inspected without unpacking.

What survived rejection was: agenda packs, officer reports, minutes, accounts, performance reports,
public notices, the constitution and scheme of delegation, and the exempt appendix. Every one of them
is an anchor `work_type` or the anchor's own fixture.

## The collision fixture

`Council Tax Bill 2026-27 - 14 Elm Road.pdf`. It carries an authority letterhead, a council-tax
account number, a band, an annual charge and an instalment schedule. **What discriminates it:**
custody and role — the named addressee is the file's holder, so the body is counterparty, not
producer. The `government` schema abstains; standalone the file is Independent Records. The concrete
harm this refusal avoids is that a row named for a *tier* would pull this file in on the strength of
the word *Council*, which is the never-alone token, and would do so in a personal drive where the
authority-side reading is essentially never correct.

## Reciprocal boundaries

Stated in both directions, naming the same fixture on each side. Because the row is refused, these
are recorded as recommendations for R1c rather than authored as edges (a refused node holds no
mutex); `collides_with`, `also_holds_with` and `role_split` are all empty in the JSON.

| Fixture | Comes to `government` (default template) when | Goes to the neighbour when |
|---|---|---|
| `Full Council - Agenda and Reports Pack - 2026-09-15.pdf` | the pack is held by the public body that produced it — issuing block, committee-system provenance, numbered papers, minute section | `business_operations.meeting-record` when the same furniture belongs to a company or a private board; `nonprofit.governance` when it belongs to a charity, union, association or standards body. Owner role decides, never vocabulary |
| `Board Pack - Riverside Housing Association - September 2026.pdf` | never — the anchor excludes "a private company, charity, union, standards body, or member association with the same furniture … by owner role", even though a local authority is named inside as nominating stakeholder | `business_operations.meeting-record` / `nonprofit.governance`. Reciprocally, those rows must not claim a genuine council pack merely because it has apologies and numbered papers |
| `Cabinet Report - Housing Revenue Account Budget 2026-27 - Item 7.docx` | when it is the authority's own report to its own committee — report author, portfolio holder, implications sections, recommendation | `business_operations.budget-forecast` only if the same numbers appear in a non-public organisation's internal planning pack. Reciprocally, budget-forecast must not claim a public body's statement of accounts |
| `Public Notice - Temporary Road Closure - High Street.pdf` | held by the issuing authority | `legal` as a coactivation (`also_schema`) for the statutory instrument reading; and to the recipient's personal administration when a resident or contractor holds a copy — recipient custody, Independent Records |
| A planning committee agenda item and its officer report | the authority holds the case file, the officer's report, the delegated report, the committee agenda, the register entry — the boundary the landed `construction_property.building-control` memo already argued against `government` | `construction_property.building-control` when the holder is the applicant: an acknowledgement or validation letter **addressed to** the holder, condition-discharge material the holder **assembled and submitted**, the authority's confirmation **back** to them. That memo names `government.municipal-administration` as a possible target for "statutory power exercised — an enforcement notice issued, a committee agenda, a register entry, a scheme of delegation". **This refusal redirects that pointer**: those bytes belong to `government.planning-application` or to the `government` default template, and R1c should retarget the reference |

The `construction_property.building-control` memo's own warning applies verbatim here and is the
best one-line summary of why the tier is worthless: *"the application reference is on both copies and
discriminates nothing."* Substitute "the council's name" and the sentence is this row's epitaph.

## Where the coverage goes

Nothing is dropped. Routing, with the design's own words:

- **The `government` schema's default template** takes the real authority-side governance cycle —
  agendas, officer reports, minutes, accounts, performance reports, notices, constitution, exports.
  This is not a residual; it is the correct home and it already exists.
- **Function-specific material** goes to the landed siblings: `government.planning-application`,
  `government.permit-licensing`, `government.housing-authority`,
  `government.school-district-administration`, `government.library-administration`,
  `government.parks-public-lands`, `government.elections-administration`,
  `government.public-records-foi`, `government.constituent-casework`,
  `government.public-procurement`, `government.public-consultation`,
  `government.policy-development`, `government.archives-recordkeeping`.
- **Independent Records** — *"Independent Records may live under Personal/Independent Records and
  hold standalone certificates, notices, confirmations, forms, and PDFs that have a durable purpose
  but no broader group."* The single public notice, the unattached accounts, the resident's
  council-tax bill.
- **Protected Records** — *"Protected Records may represent sensitive isolated material such as
  passport scans, medical documents, account statements, visas, legal forms, or credentials; it
  should normally remain local-only and must not cause filenames or content to be exposed in model
  prompts."* The exempt appendix, the named-tenancy schedule, the mixed export.
- **Review Later** — *"Review Later may hold files whose meaning is partly understood but whose final
  location requires a future decision."* Governance-shaped files whose owner role is unresolved.
- **Reading Inbox** — *"Reading Inbox may hold papers, articles, reports, and saved PDFs that appear
  to be reading material but have no active research, course, or project association."* Published
  council documents held by a reader.

Abstention over all of these is a designed outcome: *"Correct abstention is a successful outcome
because the product’s goal is reliable organization, not maximum file movement."*

## Fields

`fields: []` and `proposed_fields: []`. The row is a placeholder template on a schema that declares
no field rows (PR-6, D1's deferral), so it may not mint any; and the refusal makes the question moot.
Candidates I considered and did **not** propose: a body or authority key (would be the organisation
name the design forbids as sole evidence), a meeting or committee key, a tier key (the refusal's own
subject), and `record_type` (canonical but scoped to Finance). None is licensed, and proposing a
field to justify a refused row would be the 574's mistake in a new costume.

## Neighbours considered that got no edge

- `government.public-authority-record` — not an edge but the likely true home of the corporate-spine
  residue. Recorded in `open_question` rather than as a mutex, because asserting a collision against
  a row I did not read would be a guess.
- `government.legislative-record` — proceedings, votes and bill packets have their own anchor signal;
  a council's minutes are not legislative proceedings and the confusion is not same-evidence.
- `finance.*` — a statement of accounts is not a personal or business financial record; no canonical
  finance key is available to this row, and the recipient's council-tax bill is handled by the
  recipient-custody exclusion, not by a finance mutex.
- `legal` — recorded as a fixture-level `also_schema` on the statutory notice, not as a node edge.

## NEEDS-JOSEPH

- **NJ-1 — the cross-service corporate document.** The refusal takes with it the one artifact no
  function sibling owns: a general-purpose authority's own accountability spine (multi-service
  performance report, statement of accounts, constitution and scheme of delegation, forward plan).
  Alternatives: (a) accept that the `government` default template covers it — my recommendation,
  since it already lists budget, performance report and public notice as work types; (b) confirm
  `government.public-authority-record` as its explicit home; (c) mint a **new narrowly named row for
  the situation** ("a public body's own corporate governance and accountability cycle") which would
  then have to win the same three-leg test against the default template. Option (c) is only honest if
  the row is named for the situation, never for the tier. Minting an id is outside a node agent's
  remit, so this row creates nothing.
- **NJ-2 — retarget the `construction_property.building-control` pointer.** That landed memo routes
  "statutory power exercised — an enforcement notice issued, a committee agenda, a register entry, a
  scheme of delegation" to `government.planning-application` **or**
  `government.municipal-administration`. The second target no longer exists. R1c should decide
  between `government.planning-application` and the `government` default template. I did not edit the
  neighbour's file.
- **NJ-3 — the browse question.** Users plausibly want a Council branch even though no template fires
  there. Confirm that browse-only parents can carry an organisational label the activation path never
  uses, and that a browse label can never be read back as evidence.

## Self-verification

- JSON parses (`python3 -m json.tool`): pass.
- Key set matches the landed refusal exemplar `business_operations.organisational-records.json`
  exactly (27 keys, same order), which itself matches the `government.json` anchor.
- Every quoted span was grep-verified verbatim before use: the four residual sentences and the
  abstention sentence from `planning/00-database-agent-product-design.md` lines 114 and 120; the
  organisation-name sentence from line 63; the dimension-order sentence from line 95. Quotes
  attributed to the `government` anchor were read from that file, not from memory.
- No thresholds, no counts, no handling classes, no confidence scores.
- Edges: `collides_with`, `also_holds_with`, `role_split` empty; `falls_through_to` names only
  residual templates from the design's residual library.
- Files written: exactly the two assigned. No roster, canonical-fields, neighbour, `src/` or SPEC
  edit.

## Final recommendation

Refuse `government.municipal-administration`. Keep the coverage where it already lives — on the
`government` schema's default template and on the function siblings — and resolve NJ-1 before anyone
is tempted to reinstate the id under a better name.

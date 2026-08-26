# Research memo — `government.planning-application`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.planning-application.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, `launch: placeholder`

## Result

Accept the node, on two of the three node-test legs, and concede the third openly.

The row survives because its organizing anchor is **a parcel of land**. Every other government child is
anchored to a person (casework), an organisation (procurement, grants), an instrument (rulemaking,
legislation), or a proceeding (elections, FOI). This one is anchored to an immovable site that outlives the
applicant, the agent, the owner and often the authority, and that recurs across unrelated applications
decades apart. That anchor produces a detection signature the `government` schema's default template cannot
express, and a privacy rule that inverts the schema's default. It does **not** produce different dimensions,
because there are none to differ.

## The charge — the strongest case that this row should not exist

I put the case against the row first, because it is a strong one and it nearly won.

**Charge 1 — it is a `work_type` value, and its own schema says so.** This is the sharpest form of the
charge and it is evidenced, not speculative. `government.json` already carries, in `work_types[]`, the
string *"planning application, permit or licence case, inspection, enforcement record, reasons, decision,
variation, suspension, or revocation on the deciding side"*. The schema author enumerated my entire row as a
value on a field that does not exist. CONNECTION §2 is explicit that work types are values, and the dispatch
prompt repeats it: *"Work types are values."* By the letter, this row is a value that was promoted.

*Defeat.* Two things. First, that enum string bundles planning with permits, licensing, inspection and
enforcement — and `government.permit-licensing` is a separate landed roster row. So the string is a coverage
note written to keep the schema honest about its span, not a claim that the span is one value. Second, and
decisively: a work_type value cannot carry a **grouping anchor**. "Decision notice" is a work type. The
proceeding that binds `Proposed Elevations - 1042-P-104 Rev C.pdf`, `Arboricultural Impact Assessment - Mill
Lane - BS5837 tree schedule.pdf`, `Objection - 12 Mill Lane - overlooking and loss of light.pdf` and
`Consultee response - Highways - 26-01847-FUL.eml` into one packet is not a value on any of those files; it
is the site plus the reference. `00` licenses exactly this distinction: *"The documents are content-incoherent
but purpose-coherent."* Those four files share no topic. A work_type enum has nothing to say about them.

**Charge 2 — it is a lifecycle stage of a construction project.** Planning looks like phase one of building
something, and lifecycle stages are not nodes.

*Defeat, using a neighbour's own published words.* `construction_property.building-control.json` already
argued the point against `construction_property.construction-project` and I adopt it verbatim in substance:
"a planning permission routinely exists years before any contractor and often produces no job at all (a
refusal, a lapsed consent, a lawful-development certificate obtained only to sell), while a job routinely
runs under a consent obtained by somebody else." A refusal produces a complete, well-populated file and no
project ever. A stage that can terminate the thing it is a stage of is not a stage.

**Charge 3 — it is a duplicate of `construction_property.building-control`.** The most dangerous charge,
because that row landed first, claimed the side collision, and even claimed the numbered-condition sequence.

*Partial defeat, partial concession.* Two discriminators, and I state both reciprocally in the JSON. (a)
Side: authority letterhead, validation record, officer report and delegated-authority block versus an
applicant's submission and the conditions the holder must discharge. (b) **Regime**, which that row did not
name: building control decides whether construction complies technically with building regulations, through
inspection stages and a completion certificate; planning decides whether a use or a form of development is
acceptable at all, through consultation, amenity, design and heritage assessment. A householder can obtain
planning permission and never approach building control, and can serve a building notice for works that need
no planning permission. The concession is that on the applicant's side these two collapse into one folder,
which is the substance of NEEDS-JOSEPH NJ-1 below.

**Charge 4 — it is a duplicate of `government.permit-licensing`.** Same authority, same application form
furniture, same conditions, same appeal paragraph.

*Defeat, again using a landed neighbour's published discriminator rather than minting my own:*
building-control's edge against permit-licensing says the tell is whether the instrument "approves BUILDING
WORKS under a planning or building-regulations regime … or licenses an activity or occupation of the public
realm." A scaffold licence, a skip permit and a hoarding licence for my own Mill Lane fixture are that row's.
The consent for the building is mine. I write the collision anyway, because the seam is real.

**Charge 5 — it is an organisation name, a document type, a medium, a length, a format, or a row defined by
absence.** Rejected quickly but genuinely. It is not an organisation name — "a local authority, council,
borough, county or planning-department NAME alone" is the first entry on my `never_alone` list, and a
council-tax bill trips it. It is not a document type — the row holds `.dwg`, `.xlsx`, `.eml`, `.jpg`, `.zip`
and prose, and no single document type spans them. It is not a format — `design_creative` and `.dwg` appear
in my `file_kinds` and are absent from the schema's, but that is a *consequence* of the world, not the
argument for it. It is not defined by absence: every activation clause I wrote is a positive structure.

**Charge 6 — it is a duplicate of its own schema's default template.** Answered in full below.

## The node test, all three legs

CONNECTION §2, verbatim: *"A **template** row exists only if its detection signals, recommended dimensions,
or privacy rules differ from its schema's default template."* The test is disjunctive. I take each leg
separately rather than reporting a verdict.

**Leg 1 — detection signals. DIFFER, and this is the load-bearing leg.**

The `government` schema's deterministic list contains one clause that reaches my world: *"an authority-side
decision record with labelled applicant or regulated-party slots, an application or case reference, a
decision status, reasons, and an authorized-officer or office block."* That clause recognises exactly one of
my eighteen fixtures — the decision notice — and it recognises it as a generic permit. It cannot see any of
the others. Concretely:

- It has no clause for a **scaled drawing sheet**. `Proposed Elevations - 1042-P-104 Rev C - 1_100 @ A1.pdf`
  has no applicant slot, no case reference, no decision status and no officer block. Under the schema
  default it is invisible. Under this row it is recognised by a title-block signature — drawing number,
  revision letter, ratio scale, sheet size, status word — conditioned on a validated application reference
  for the same site existing elsewhere in the corpus.
- It has no clause for the **consultation apparatus** — a neighbour-notification schedule addressed to
  properties *around* a site, a dated site-notice display record, a press-notice instruction. No other
  government function notifies the neighbours of a parcel.
- It has no clause for the **land anchor** itself: one site address or plot description repeated across
  members whose contents are mutually unrelated. The schema's grouping vocabulary anchors on "an exact bill,
  rulemaking, consultation, application, permit, case, request, procurement, election, or programme
  reference" — all of them abstract identifiers. None of them is a place.
- It has no clause for a **condition-discharge sequence** keyed to a numbered condition of an earlier
  instrument, which is a second proceeding hanging off the first years later.

That is four positive detection structures the default cannot express. The leg passes on evidence.

**Leg 2 — recommended dimensions. DO NOT DIFFER. Conceded.**

PR-6 leaves `government` fieldless, so `template.dimension_order` is `[]` on the schema default and `[]`
here. A template may only name fields its schema declares. There is no honest way to claim this leg and I
do not claim it. I recorded the structure the world would want as prose in `template.why` — site, then
proceeding, then function — and explicitly barred the applicant's and agent's names from becoming the
organizing level, on `00`'s rule: *"It should avoid using authorship or creator identity as a destination
dimension."* Time is not first, on `00`'s rule that *"For document and record domains, project, function, or
subject usually comes before time because putting year first scatters related work across calendar
folders"* — a case that validates in one year, decides in the next and discharges a condition two years
later is scattered by any time-first order. The recommendation is not frozen: *"The system recommends an
order based on the domain template, but the user can reverse, remove, add, or flatten dimensions."*

**Leg 3 — privacy rules. DIFFER in rule, though not in class label.**

`sensitivity` is `potentially_sensitive` on both, because the phase vocabulary offers only `none` and
`potentially_sensitive` and handling classes are P7's. But the schema's stated default is that *submissions
and named-person case material are protected by default* — and here that is backwards for the largest
member class. The applicant's submission, the officer's report and the decision are prepared **for
publication on a statutory public register**. The protected residue is a non-party: the neighbour whose
objection letter carries a home address, a description of their own bedroom windows, and sometimes a health
or safeguarding reason. `Objection - 12 Mill Lane - overlooking and loss of light.pdf` is the fixture.

That inversion produces a positive rule this row must carry and the default would not think to state:
**register publication must never lower the posture of the packet.** It sits on `never_alone`. The
justification is `00`: *"Privacy policy must be enforced before content reaches any model or external
connector"*, and *"Protected material should not be included in cloud-model prompts by default, should not
display raw content in general group summaries, and should not be moved automatically without a user policy
that explicitly permits it."* A group summary for a planning case must not enumerate objector names or
addresses even though every byte is publicly downloadable. Two further inversions: a disability-adaptation
or household-need application puts protected material back on the applicant's side, and a viability
appraisal is commercially sensitive while the case around it is public.

Two legs pass, one is conceded. The node stands.

## Files considered and rejected

A row that only lists what it holds has not been researched. These were tempting and are not this row's
evidence.

- **`Land Registry title plan - TT123456.pdf` — THE COLLISION FIXTURE.** It is visually indistinguishable
  from `Site Location Plan - 1_1250 - 14 Mill Lane.pdf`: an ordnance base, a red edging, a north arrow, a
  scale bar, a licence attribution strip, and the same street. It is not a planning document at all; it is a
  land-ownership record. **What discriminates it:** a title number and a proprietorship reference where the
  planning plan has a proposal description and an application reference; and the absence of the red-line /
  blue-line development convention. This fixture is why "a red boundary line drawn on an ordnance-survey
  base alone" is on `never_alone` — the most seductive signal in this world is a shared one. It routes to
  Protected Records, not to me.
- **`Local Plan - Policy H3 Housing Allocations - adopted version.pdf`.** A development plan names my site
  in an allocations schedule and carries an examination reference. Rejected: policy-making is rule-making,
  not determination. It belongs to the `government` schema's own rulemaking clause, or to Reading Inbox. I
  kept it as a fixture precisely to mark the seam, because "names the site" is exactly the kind of signal
  that would otherwise leak files into this row.
- **A council-tax bill, a bin-collection letter, an electoral-registration confirmation.** All carry the
  local authority name and a site address — my two most prominent tokens — and none is a planning file. They
  are the reason both tokens are on `never_alone`. The schema's own never-alone posture is the precedent.
- **An estate agent's particulars and a home-insurance schedule.** Both carry a site address, a floor plan
  and photographs of the property. Neither has an application reference or a receiving slot.
- **A business plan, a financial-planning pack, a lesson plan.** The word "planning" alone, which is on
  `never_alone` for this reason.
- **A GIS or mapping export of a whole district.** Tempting because planning authorities produce them, but
  a constraints layer covering thousands of parcels has no determination and no anchor site. Unsupported or
  Encrypted, or the schema's own statistics clause.
- **A live case-management system or portal account.** A source system, not a file node. Only a bounded
  export with a readable manifest is represented, and `00` requires the manifest be read without unpacking.
- **Planning legislation, national policy guidance, appeal digests and practice textbooks.** Reading Inbox.
  Legal vocabulary about planning is not a planning case.
- **A petition with two hundred signatures.** Retained inside the representation class rather than given its
  own treatment; a signature list is a member, not a structure.

## Reciprocal boundaries

Ten collisions are authored. Four of them restate a seam a landed neighbour already published, and I state
them **in that neighbour's own terms** so the seam reads the same from both ends rather than two agents
describing one wall differently.

| Neighbour | Shared fixture, named identically on both sides | Discriminator |
|---|---|---|
| `construction_property.building-control` | `Decision Notice - 26-01847-FUL - Grant with Conditions.pdf`; `Condition 4 discharge - drainage details.pdf` | Side (issuing authority vs applicant/agent) and regime (land use vs technical building compliance). The application reference is on both copies and discriminates nothing. |
| `construction_property.site-survey` | a topographic survey of Mill Lane | An authority-side receiving slot, validation letter, consultee response or officer report → me; the survey deliverable with its instructing client and methodology → them. Their wording, restated. |
| `engineering.civil-structural` | the structural calculation appended to a submission pack | An application reference / validation letter / officer report → me; the calculation deliverable with its design-responsibility statement → them. Their wording, restated. |
| `government.environmental-regulation` | `Environmental Statement - Mill Lane redevelopment - Chapter 8 Air Quality.pdf` | Planning reference + prospective mitigation → me; environmental permit reference + assessment against an existing numbered condition → them. Their fixture, their wording. |
| `government.permit-licensing` | a scaffold / hoarding / skip permit for the same site | Approves building works or a change of land use → me; licenses an activity or occupation of the public realm → them. |
| `construction_property.development-appraisal` | `Viability Appraisal - Mill Lane - residual land value.xlsx` | Addressed to an investment decision → them; submitted to a determining authority with a receiving slot and an independent reviewer's tab → me. |
| `construction_property.construction-project` | `Condition 4 discharge - drainage details.pdf` | Which counterparty is addressed: a negotiable contract party → them; a statutory body that is not a party to any contract → me. Neither is a stage of the other. |
| `legal` | `Appeal APP-X1234-W-26-3312345 - Statement of Case and Questionnaire.pdf` | The authority's questionnaire and consultee schedule → me; a practitioner's matter file for a client appellant, or a private party's own record → Legal. The tribunal reference is on every copy. |
| `business_operations` | the developer's complete planning file — same drawings, same decision notice | Owner role: receiving/assessing/determining → me; preparing/submitting/tracking/complying → them. This is where most real corpora sit. |
| `nonprofit` | `Objection - 12 Mill Lane - overlooking and loss of light.pdf` | The residents' association holds it as its own campaign output; I hold it as a received representation with a date-received stamp and a log number. The stamp is the discriminator; the text is byte-identical. |

**Neighbours considered that got no edge.** `government.constituent-casework` — a councillor forwarding a
constituent's planning complaint is casework about a case, and the seam is holder-office, already covered by
the schema's own role precondition; no same-bytes mutex. `government.archives-recordkeeping` — an FOI
disclosure of a planning file is a genuine dual reading, but both rows sit on the `government` schema, so
schema coactivation is vacuous; the seam belongs to R1c if it proves real. `creative.architectural-
visualisation` — `construction_property.json` already published the title-block discriminator against it and
a persuasive render is never submitted with a receiving slot. `photos` and `identity` are coactivation cases
recorded per-fixture as `also_schema`, not mutexes.

`also_holds_with` is **empty**, following the `legal.practice-matter-file` precedent: a fieldless template
cannot author schema-level coactivation, and the honest dual readings are recorded as `also_schema` on
individual fixtures (`construction_property` on the drawing sheet, the condition discharge and the
appraisal; `legal` on the appeal; `photos` on the site-notice photograph). `role_split` is empty for the
same reason — there are no field keys to split.

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false` — all intentional under
PR-6 and D1, matching the `government` schema anchor, which also carries empty `proposed_fields`.

Candidates considered and **not** minted:

- A **site / parcel** concept is the one this row genuinely wants, and no canonical key covers it. `location`
  is a photos-scoped capture-place key and would be a synonym-mint, not a reuse. `project` is Research-scoped.
  It goes to NJ-2 rather than into `proposed_fields`, because minting the row's own anchor key would be
  exactly the unilateral move the brief forbids, and because a site address is a private home address —
  destination-eligibility is a privacy decision, not a naming one.
- `application_cycle`, `application_document_type`, `target_university` and `purpose` are College-Applications
  role-split keys. The shape rhymes (a packet submitted to a deciding body) and that rhyme is a trap; reusing
  them here would put university-application semantics on a land-use case.
- `record_type`, `institution` — Finance-scoped. `work_type` — declared on the academic set, not on
  `government`; my `work_types[]` enumerates values for a field that does not yet exist, which is what the
  contract asks for.
- `application_reference`, `case_officer`, `decision_status`, `condition_number`, `authority` — not canonical,
  not minted here.

## Grouping without copied facts

The anchor is an exact application reference appearing on an **authority-side** receiving, portal or
case-system slot — not in an author's own header, which any consultant can write. Members join without
acquiring facts. `Proposed Elevations Rev C.pdf` with no reference inside it may sit in the group and gets
no application, site or authority fact written onto it: the `HW 3.pdf` rule, marked
`group_without_copying_facts: true` on that fixture and on the site plan, the supporting statement, the tree
survey and the portal screenshot.

A site's planning history across separate applications by different owners over decades is a legitimate
review *neighbourhood* and never an automatic merge — separate determinations are separate proceedings.
Drawing revisions are a universal version family, not a government fact. Archive manifests are read without
unpacking, on `00`'s archive rule; the packet-purpose reading is licensed by *"A ZIP file named
submission.zip may contain a transcript, personal statement, resume, certificate, and form, which is
meaningful evidence of a purpose-defined application packet even when the outer archive name is vague."*
A download session that gathered several site documents in one sitting proves nothing: *"A session should
never be treated as proof of topic."*

## What this row must never conclude

Planning determinations have legal effect, and the catalogue has none. It must not conclude that a consent
is extant, implemented, lapsed or lawful; that a condition is discharged before the authority's letter
exists; that an application is valid or complete; that a proposal complies with any policy; that permitted-
development rights apply; that a breach has occurred; or which regime imposed a bare numbered condition.
Where side and regime both fail to settle, neither this row nor building-control activates: *"Correct
abstention is a successful outcome because the product’s goal is reliable organization, not maximum file
movement."*

## NEEDS-JOSEPH

- **NJ-1 — the mass is on the wrong side of the schema.** The row is named for planning applications, but
  the `government` schema's role precondition admits only the deciding authority, and
  `construction_property.building-control` already holds the applicant/agent side. Most private corpora that
  contain a planning file are the applicant's. Alternatives: (a) keep this row authority-side-only and
  accept that its name oversells it — rename in R1c; (b) narrow this row to determination and let a
  land-use-consent template exist on `construction_property` for the applicant side, splitting a world that
  users experience as one folder; (c) let both activate on the same bytes as a licensed dual reading, which
  the current `collides_with` mutex forbids. My recommendation to R1c is (a) plus a rename.
- **NJ-2 — is a LAND anchor a field?** If PR-6 lifts, decide centrally whether a site/parcel concept may
  exist. It is the only anchor type no other `government` child uses, and no canonical key covers it.
  Sub-decision: it must not be destination-eligible by default, because a site address is a private home
  address and a branch label would expose it.
- **NJ-3 — where does planning enforcement live?** The same notice furniture — an alleged breach, a numbered
  notice with steps and a compliance period, a site visit — serves this row, `government.permit-licensing`
  and `government.environmental-regulation`. Alternatives: keep it with the consent regime that was
  breached (my provisional placement); give it to permit-licensing as the generic enforcement holder; or
  create a shared enforcement row, which risks being a lifecycle-stage node and I do not recommend.
- **NJ-4 — public register versus P7.** The bytes are published; the packet is not. No handling class exists
  yet to express "publicly available and still must not be summarised with names." P7 must own it. Until
  then this row keeps a blanket `potentially_sensitive` and the never-alone rule that publication does not
  lower posture.

## Self-verification

- `python3 -m json.tool` parses the node file. Key set matches the `government` schema anchor exactly,
  including `proposed_context_terms`.
- Every `file_examples.source_type` is in `SOURCE_TYPES`. Every `facts_legal` entry is a canonical universal
  key (`file_type`, `creation_date`, `language`, `duplicate_family`, `version_family`, `sensitivity_status`,
  `capture_year`). No file example writes a folder path as a fact.
- Every edge id was confirmed present in `planning/domains/roster.json`:
  `construction_property.building-control`, `construction_property.site-survey`,
  `construction_property.construction-project`, `construction_property.development-appraisal`,
  `engineering.civil-structural`, `government.environmental-regulation`, `government.permit-licensing`,
  `legal`, `nonprofit`, `business_operations`, plus `construction_property` and `photos` used as
  `also_schema`. Every `falls_through_to` name is one of `00`'s residual templates.
- Every quoted span was grep-verified verbatim against `planning/00-database-agent-product-design.md` before
  being written, including the curly apostrophe in "product’s". No thresholds, no counts, no handling
  classes, no confidence scores.
- Files written: only `government.planning-application.json` and this memo. No neighbour, roster, contract,
  `canonical_fields.json`, `check.py` or `src/` file was touched.

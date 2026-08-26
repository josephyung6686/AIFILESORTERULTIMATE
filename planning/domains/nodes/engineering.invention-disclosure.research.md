# Research memo — `engineering.invention-disclosure`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/engineering.invention-disclosure.json`
Roster row: template on the fieldless `engineering` schema, `parent_id: null`, placeholder launch
Absorbs (ROSTER Appendix A, per `one_line_hint`): `res.patent-disclosure`, `legal.ip-registration`

## Result

Accept the node. It survives the charge because its organizing entity is not the engineering
schema's organizing entity: the default relation requires an identified, configuration-controlled
design item, and an invention frequently has no such item at the moment the material is created.
The row's detection signals are disjoint from the schema default's, and it carries a privacy and
abstention rule — pre-filing novelty exposure, and refusal to determine inventorship — that the
default never has to state. Its dimension leg is honestly weak and is not claimed to carry the node.

## The charge against this row, argued before anything else

Six ways this id could be a mistake. Five of them are real risks and one of them nearly succeeds.

**1. It is a document type.** "Invention disclosure form" is literally a form. Forms are values of
an artifact-type field, not nodes, and the engineering schema already proposes
`engineering_artifact_type` with values such as "engineering drawing" and "verification report".
Adding a node per document type is exactly the 574's failure.

*Defeated.* The row does not hold one document type; it holds a family of unlike artifacts — a
signed disclosure record, a purchased search report, a claim draft, reference-numeral figures, an
office letter, a docket table, an assignment instrument — that share no format, no producer and no
extension. What binds them is a relation: each one is evidence about one claimed invention and its
filings. A document-type node would hold `Invention-Disclosure-Record_*.pdf` and nothing else. This
row holds sixteen fixtures of ten different shapes. If the row were collapsed into a value of
`engineering_artifact_type`, the office action, the docket table, the assignment and the figure
sheet would each need their own value and would still not group together.

**2. It is a lifecycle stage.** The `one_line_hint` says "around the moment of filing". That phrase
is the strongest weapon against this row: a moment in a lifecycle is a `lifecycle_stage` value, and
the engineering schema already proposes that key with values concept, preliminary design, detailed
design, qualification, released.

*Defeated, but the hint's phrasing should not be trusted.* The test is whether the same files appear
under the schema default at other stages. They do not. A disclosure record never matures into a
drawing package; a claim set never becomes a requirements matrix; an office action has no position
on any design lifecycle at all. Conversely, a released design at the "released" stage generates a
technical data package and produces no inventorship instrument. Filing is also not a point: the
material begins years before it (conception evidence, search reports) and continues years after it
(office actions, annuities, granted copies), so the row is not time-bounded and its template sets
`time_first: false`. I recommend R1c reword the roster hint away from "moment of filing"; it invites
exactly this misreading. That is a recommendation, not an edit — I did not touch the roster.

**3. It duplicates the schema default.** Patent material has identifiers, drafts, drawings,
approvals and revisions, which sounds isomorphic to item + drawing + revision + approval.

*Defeated on evidence.* The schema's deterministic list is quoted in `engineering.json` and keys on
"a controlled drawing/title-block structure with an identified item or assembly, drawing identifier,
revision/issue slot", on "stable requirement identifiers" with "verification method and verification
status", on a BOM "parent assembly identifier, child item/part identifiers", and on a change that
"identifies an affected design item and current/replacement revision". Not one of those structures
appears on any fixture in this row, and the row's own structures — an inventorship block, a
conception slot, a prior-public-disclosure slot, a numbered claim set, reference numerals with no
title block, an office letterhead with an application identifier — appear nowhere in the default.
Two disjoint signal sets on one schema is precisely what a template is for.

**4. It is never-alone evidence: an organisation name.** USPTO, EPO, WIPO, Patent Center. A row
whose only evidence is an organisation name can never activate.

*Defeated by construction, and the risk is encoded rather than argued away.* Every office name is in
`never_alone`, alongside the observation that a downloaded third-party patent carries the same
names, the same front-page layout and the same claim structure. The row's activation always requires
a holder-side structure: an inventorship block, a receipt in the holder's name, a docket row, or a
citation statement the holder filed.

**5. It is defined by an absence.** A tempting shortcut is "a drawing with no title block is a
patent figure". That would make the row an absence-defined node, which cannot activate.

*Defeated, and the shortcut is explicitly banned.* `never_alone` forbids using the missing title
block as proof, mirroring 00's rule that missing EXIF is not screenshot proof. The positive
observation is reference numerals keyed to a description plus sheet-of-sheets numbering. The absence
of a title block is recorded in the fixture's observations only as a discriminator once the positive
structure is present.

**6. It duplicates `legal.practice-matter-file`.** That landed row already holds professional
prosecution files, engagement records and office correspondence.

*Defeated by the holder-role seam, and the boundary is written reciprocally in both directions.*
See the boundary section. The landed legal row's own discriminator is "practitioner-side
representation workflow versus the holder as a personal party with no practitioner anchor"; an
inventor with a docket and a filing receipt and no engagement record is neither of its two cases,
which is why the coverage needs somewhere to go.

## Node test, three legs

**Leg 1 — detection signals: PASSES, and carries the node.** Argued in item 3 above. The schema
default and this row share the engineering schema and share nothing else in their deterministic
lists. `needs_llm` here is about a different set of confusions than the schema's: the schema asks
whether a BOM is authoritative or a pick list; this row asks whether a patent document is the
holder's own filing, a reference the holder submitted, or reading material — a question the schema
default never faces because the default's artifacts are not published by anyone else.

**Leg 2 — dimensions: WEAK, and not claimed.** PR-6 keeps engineering fieldless, so both the schema
and this row must serialize `dimension_order: []`. The difference exists only at the conditional
level: the schema's researched order is project → design_item → lifecycle_stage →
engineering_artifact_type; this row's is invention_family → prosecution status → artifact role. The
difference is real in kind — the intelligibility parent is the invention rather than the item,
because one design item can embody several unrelated inventions and one invention can exist with no
item at all — but a leg that cannot be serialized should not be counted as passing. It is recorded
in `node_test.dimensions` as conditional and raised as NJ-IDF-1 and NJ-IDF-3.

**Leg 3 — privacy rules: PASSES.** The schema's `sensitivity_why` is about proprietary, supplier,
safety and export-controlled data. This row adds two rules that the default has no reason to hold.
First, before a filing exists the description is the asset, so its existence and content must not be
surfaced remotely or in a visible folder label — which is why NJ-IDF-2 asks whether a docket may be
a branch label at all. Second, the row must abstain from four determinations the default never
encounters: who the inventors are, whether anything is novel or patentable, whether a cited
reference is material, and any computed date (response period, priority, annuity). All four are
written into fixtures' `must_not_conclude`. Both rows land on `potentially_sensitive`, since that is
the only non-`none` value available in this phase; the difference is in the abstention rules, not
the label.

Verdict: two legs pass on their own strength. `refuse_node: false`.

## Files considered and rejected

Naming what this row does not hold was the larger half of the work.

- **`US11234567B2.pdf` — a third-party granted patent.** The collision fixture; see below.
- **`Freedom-to-Operate-Opinion_counsel_privileged.pdf`.** A practitioner opinion addressed to a
  client. It is about inventions but it is advice, not the inventors' technical record. It routes to
  `legal.practice-matter-file`, and this row must not conclude privilege, clearance or infringement.
  Patentability opinions are excluded from `work_types` for the same reason.
- **`Licence-Agreement_actuator-patent_executed.pdf`.** Commercialisation of a granted right is
  contract evidence, not invention material. It belongs with `business_operations.contract-administration`
  or `legal.leases-agreements` on executed-agreement structure. This row stops at the technical and
  prosecution record; a licence names a patent the way an invoice names a project.
- **`Employment-Agreement_IP-assignment-clause.pdf`.** An employment contract containing an
  invention-assignment clause is an employment record. Only a standalone assignment instrument
  naming an identified invention title is this row's evidence.
- **`BPA-210-001_Brake-Pedal-Assembly_RevC.dwg`.** The controlled drawing of the very product the
  disclosure describes. Product identity is not invention-family membership.
- **`Sprint-14-Project-Status.xlsx` with an "IP" column.** A project status report that mentions
  filings is `business_operations.project-delivery`; the schema already names this file as its own
  collision fixture and the same reasoning applies one level down.
- **An `Espacenet` or `Patent Center` search-results export.** A results list is a search session
  artifact, not a holder-side citation statement. Without the citation-statement form or a docket
  reference it is reading material; 00 forbids treating a download session as a topic.
- **Trademark and design-registration certificates.** They are registration instruments with no
  inventorship, no claims and no technical description. They are `Independent Records` unless a
  landed brand or design row claims them; I did not extend this row to cover all IP registration
  merely because the absorbed legacy id was called `legal.ip-registration`. That absorbed id's
  patent portion is covered here; its trademark portion is flagged as unhomed in NJ-IDF-5's
  neighbourhood and left for R1c rather than annexed.
- **A live patent-management system or docketing database.** A source system is not one file node.
  The bounded `Patent-Family-Docket.xlsx` export is represented; connector ingestion is a later
  security decision, following the treatment in the landed `legal.practice-matter-file`.
- **`Screenshot 2026-05-12 at 09.14.31 - Patent Center status.png`.** Positive screen-origin
  evidence activates the screenshot world; OCR may reveal an application identifier, but a status
  screen with no other holder-side structure is `Temporary Screenshots`, not this row.

## The collision fixture

`US11234567B2.pdf`. It is byte-for-byte the same kind of document as the holder's own granted
patent: bibliographic front page, abstract, reference-numeral figures, numbered claims, office
identifiers. Filename, structure, vocabulary and origin all point at this row.

What discriminates it is holder-side relation, and nothing else. The row activates only if a
holder-side instrument connects to it: the same invention title on a disclosure record, an
application identifier matching a filing receipt in the holder's name, a docket row, or membership
in a citation statement the holder submitted. Absent all of those, the inventors and assignee on the
front page are simply other people, and the file is reading material routed to `Reading Inbox` under
00's rule for saved PDFs with no active research, course, or project association. The dangerous
failure mode is the reverse of the usual one: the false positive here is *more* patent-shaped than
the true positive, because a granted third-party patent is a polished published document while a
real disclosure record is often an unsigned Word file.

A second, quieter collision is `IDS-and-cited-references.zip`, whose members are third-party patents
that *are* this row's evidence — because a holder-side citation statement enumerates them. Same
bytes, opposite verdicts, decided by an exact identifier match against a holder-side form. This is
why `grouping_reasons` joins citation sets by exact publication identifier and never by subject
similarity.

## Reciprocal boundaries

Each of these is stated in both directions and names the same fixture on both sides.

**`legal.practice-matter-file`** — the seam the engineering schema memo explicitly delegated here
("the invention-disclosure child should research this edge"). Fixture:
`Office-Action_2026-05-12_App-18-123456.pdf`. → This row when the holder is the inventor or
applicant: a docket row, a filing receipt in the holder's name, a disclosure record with matching
title. → The legal row when practitioner-side representation evidence is present: an engagement
record, a client block, a matter reference, practitioner docketing. Where the holder is both — an
in-house counsel who is also an inventor — the two coactivate on two independently observed
relations, which is why `legal.practice-matter-file` appears in both `collides_with` and
`also_holds_with`. `Freedom-to-Operate-Opinion_counsel_privileged.pdf` is never ambiguous: it is the
legal row in every reading.

**`engineering.drawing-package`** — Fixture: `FIG1-FIG7_patent-drawings.pdf` versus
`BPA-210-001_Brake-Pedal-Assembly_RevC.dwg`. → This row for sheets with reference numerals keyed to
a description and sheet-of-sheets numbering. → The drawing package for sheets whose title block
joins item, drawing number, revision and approval. Neither may claim the other because both depict
assembly BPA-210.

**`engineering.prototype-build`** — Fixture: `Lab-notebook_p114_witnessed_2026-02-27.jpg`. → This
row when the page is kept as conception or reduction-to-practice evidence against a claim. → The
prototype row when it records build steps, configuration and deviations against the design
definition. One page can carry both structures; neither infers the other, hence the `also_holds_with`
entry as well.

**`research.lab-notebook-protocols`** — Same fixture, third claimant. → The notebook row for
protocol, procedure, run and observation structure inside a research workflow. → This row for
invention title, claim reference, or witness attestation tied to a disclosure. A witness signature
alone decides nothing, because witnessing is ordinary practice in both worlds; that is the trap this
boundary exists to catch.

**`research.manuscript-publication`** — Fixture: the abstract attached to
`RE Hold the abstract until we file - actuator.eml`. → The manuscript row owns venue, submission and
authorship structure. → This row owns the thread's docket reference and pre-filing hold. The same
technical prose sits in both; neither copies the other's facts, and the pair is also the cleanest
`also_holds_with` case in this row, matching 00's abstract-that-is-also-an-application-document
pattern.

**`code.software-project`** — Fixture: `appendix-source-listing.txt`. → Code on repository roots,
manifests and source structure. → This row on docket or receipt reference to a filed appendix. A
repository is not invention material because its owner filed a patent; a filed listing does not stop
being repository content.

**`manufacturing.work-instruction`** — Fixture: `Process-Improvement-Writeup.docx`. → Manufacturing
when the structure is steps, parameters, equipment and operator signoff for the line. → This row
when the same process carries an inventorship block and a novelty statement, or when a trade-secret
election record names it. This is the seam where a small team most often files the same document
twice under two names.

## Neighbours considered that got no edge

- `government.public-authority-record` and `government.permit-licensing`. A patent office is a
  government authority and an office action is authority correspondence, so the temptation is real.
  But the government schema is the authority's own side of a record; the applicant's copy of a
  letter is not the registry's record, and a patent is not a permit to do anything. No edge.
- `business_operations.contract-administration` and `legal.leases-agreements`. Licences and
  assignments are adjacent, but the genuinely confusable bytes are the executed-agreement structure,
  which neither competes with a disclosure record nor with prosecution correspondence. Recorded as a
  rejected artifact rather than a mutex, so R1c can add it if a landed sibling disagrees.
- `career.employment-records`. Invention-assignment clauses live in employment agreements. The
  discriminator is standalone-instrument versus employment-contract structure, which is not a
  same-evidence mutex; the fixture never sits between them.
- `creative.licensing-rights`. That row is about creative-work rights, not patent prosecution. No
  shared fixture.
- `engineering.requirements-specification` and `engineering.simulation-analysis`. Both are the
  schema default's home ground and neither produces inventorship, claim or office structure. The
  drawing-package and prototype-build edges already carry the intra-schema confusion that is real.
- `business_operations.project-delivery`. Already handled at schema level; adding it here would
  duplicate the schema's own collision without a distinct fixture.

## Fields and dimensions

`fields: []` — PR-6 and D1 leave engineering fieldless; a template may reuse only what its schema
declares, so there is nothing to reuse.

`proposed_fields` carries exactly one candidate, `invention_family`, with the argument that no
canonical key names the invention-plus-family entity: `project` is an undertaking (one project spawns
several unrelated inventions; one invention outlives its project), `design_item` — itself only a
schema-level proposal — names the item whose *definition* a file controls, and a disclosure controls
no definition, `subject` is the academic course key, `repository` is a code container, and
`version_family` is the universal version-graph key rather than an entity. The family relation is
structurally real and not reducible to versioning: a provisional, a national filing and a PCT record
are siblings of one invention, not versions of one document.

I deliberately did **not** mint a second key for prosecution status. Widening the schema's proposed
`lifecycle_stage` is a live alternative and shipping both spellings is the failure mode the schema
memo already warns about, so the choice is exposed as NJ-IDF-3 rather than pre-empted. No other
candidates (inventor, application identifier, jurisdiction, filing date, docket) are proposed:
inventor is authorship and is never destination-eligible under 00, jurisdiction is unavailable under
the current decision brief, and the rest are observations that belong in the version graph and the
search index rather than in a folder level.

`template.dimension_order: []` and `time_first: false`. A date-first tree would scatter one
invention across five different meanings of "date" — conception, priority, filing, receipt,
filesystem — which is the same argument the landed legal row makes about matter dates.

## Recognition boundary in one paragraph

Strong evidence is always a relation between a holder and an invention: an inventorship block with a
conception or public-disclosure slot; a claim set under specification headings; office correspondence
or a receipt bearing an identifier that a holder-side instrument also bears; a citation statement
plus its enumerated references; a docket table whose rows share one invention title across
jurisdictions; reference-numeral figure sheets tied to a description. Weak evidence stays weak in
any quantity: office names, patent vocabulary, bare identifiers, inventor names, download origin,
extensions, folder names, and the absence of a title block. A filename may retrieve a candidate for
local review; it may never create an invention, an inventor, a date or a family fact.

## Grouping without copied facts

Groups are bounded by exact docket, application, publication or priority identifiers, or by an
identical invention title plus inventor set. A sparse `FIG3.tif` may join an accepted invention
neighbourhood without acquiring an invention, inventor, date or family fact — the P9 graph assembles
context and does not propagate labels. Archive manifests are read without extraction. Nothing joins
a group through product name, technology topic, employer, inventor name alone, or a shared download
session.

## NEEDS-JOSEPH

1. **NJ-IDF-1** — is `invention_family` a real key, or should R1c widen `project` and accept that
   one project may then span unrelated inventions? Alternatives: mint the key; widen `project`;
   defer entirely and leave the row anchor-less.
2. **NJ-IDF-2** — may an invention or docket identifier appear as a visible folder label at all? The
   label itself can disclose that an unfiled invention exists. Alternatives: allow it; allow a
   local-only alias with a redacted display label, as the landed legal row proposes for matters;
   forbid any invention-named branch.
3. **NJ-IDF-3** — should prosecution status widen the proposed `lifecycle_stage`, or remain an
   observation only? A design gate and a legal position before an office are different things, and
   shipping both as synonyms is the duplication the schema memo warns against.
4. **NJ-IDF-4** — with engineering fieldless, may this row author a `role_split` against
   `legal.practice-matter-file` naming the inventor and practitioner roles? `role_split` requires
   different field keys and neither schema declares any, so I left it empty following the landed
   legal row's precedent. The seam is genuinely a role split and deserves the edge once keys exist.
5. **NJ-IDF-5** — do defensive publications and trade-secret election records — material created to
   *prevent* a patent rather than obtain one — stay in this row? They share inventorship and novelty
   structure and share nothing with any other row, so I included them in `work_types`; if they stay,
   the row's name should stop saying "disclosure". Related and left unhomed: the trademark and
   design-registration half of the absorbed `legal.ip-registration`, which this row deliberately did
   not annex.

## Self-verification

- JSON parses; key set matches the landed `engineering` and `legal.practice-matter-file` siblings.
- All five `falls_through_to` `design_cite` spans were grep-verified verbatim against
  `planning/00-database-agent-product-design.md` before being written; no other span is quoted.
- Every `file_examples.source_type` is in `SOURCE_TYPES`; no example writes a folder path as a fact.
- Every edge id was confirmed present in `planning/domains/roster.json`; every
  `falls_through_to.residual_template` is one of 00's named residual templates.
- `never_alone` contains entries true of the collision fixture `US11234567B2.pdf` (office names,
  bare identifiers, inventor names) and of the sparse fixture `IDF-2026-0142 disclosure memo.docx`
  (docket-shaped filename token).
- No threshold numbers, no confidence scores, no handling classes, no regexes.
- Files written: only the two assigned. The roster, `29-DOMAIN-OWNERSHIP.md`, canonical fields,
  `check.py`, `src/` and all neighbour nodes were read-only or untouched.

# engineering.product-certification — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: engineering`, `launch: placeholder`, `parent_id: null`.
Output: [`engineering.product-certification.json`](engineering.product-certification.json).
Verdict: **node kept**, carried on two of the three node-test legs with the third conceded. One
field proposed (`conformity_scheme`). Both files are new; nothing was salvaged.

## Sources actually used

- The stamped assignment (`make_prompt.py engineering.product-certification`) and
  `planning/domains/dispatch/RESEARCH-BRIEF.md`.
- `planning/00-database-agent-product-design.md` — reached by targeted grep, never streamed. Eight
  spans quoted; all eight re-matched verbatim (audit below).
- `planning/domains/nodes/engineering.json` — the schema anchor and the file this row is measured
  against; read for `node_test`, `proposed_fields`, `recognition`, `work_types`, `template`, edges,
  `sensitivity_why`, `open_question`. Its `.research.md` was **not** opened: the JSON states the
  default template's discriminating structures explicitly, so the node test was decidable without it.
- The four landed rows that already argued a boundary against this id, found with one `grep -rl`:
  `engineering.aerospace-airworthiness`, `engineering.embedded-firmware`,
  `engineering.automotive-program`, `engineering.material-specification`. Every boundary claim they
  made is reciprocated in the JSON using **their** fixture names, unchanged.
- `planning/domains/roster.json` (all twelve edge endpoints confirmed) and
  `planning/domains/canonical_fields.json` (all 37 keys checked before proposing anything).
- `finance.crypto-assets.research.md` for depth calibration, and for three habits reused here:
  apostrophe-artifact-aware quote auditing, `also_holds_with` left empty **by contract** with a
  note, and `role_split` refused in prose rather than minted.

## THE CHARGE — the strongest case that this row should not exist

Written before anything else, in five independent lines.

**(a) It is a lifecycle stage.** The schema already proposes `lifecycle_stage` with values concept,
preliminary design, detailed design, qualification, released design. "Certification" reads as the
next value in that list — making this row a *value* of a field the schema already has.

**(b) It is a document type.** "Certificate" is a document-type word, which 00 treats as never-alone
evidence — and the residual library's own definition of Independent Records names "standalone
certificates" as the thing that residual exists to catch.

**(c) It is an organisation name in disguise.** Certification is what notified bodies, test houses
and regulators do. If the recognisable thing is a body's letterhead, 00's Columbia rule kills it.

**(d) It duplicates `engineering.verification-validation`.** Both hold test reports on a product with
pass/fail results against criteria. If the only difference is who wrote the criteria, that is a value
on the report, not a node.

**(e) It duplicates the schema's own default template.** The default is project → design_item →
lifecycle_stage → engineering_artifact_type. Certification files have all four. Rendered into that
order they disappear — the exact finding that refused `engineering.automotive-program`, three rows
away, on this same schema, this month.

### Defeating it

**(a) fails on containment, both directions.** A stage is a position the whole definition occupies
at one moment. A certification obligation is not: a durable listing or type approval is issued,
surveilled, extended and superseded on a clock owned outside the organisation, and one product can
hold a live certificate for the shipping variant while the same design item sits in detailed design
for the next. The indices are orthogonal, not nested, so certification cannot be a `lifecycle_stage`
value without making that field mean two things. That is also why the JSON *drops* `lifecycle_stage`
from its order: within this corpus the level would carry one value, and a level whose facts cannot
vary is a level the facts cannot fill.

**(b) fails because the row cuts across document types.** This is the finding that carried the node.
A test report belongs here or to `verification-validation` depending on whether its acceptance column
holds clauses of an externally published rule or the organisation's own requirement identifiers —
same document type, same layout, opposite homes. Checklists, declarations and dossiers behave
identically. No enumeration of document kinds can make that cut, which proves the cut is not a
document kind. The document-type words themselves are written into `never_alone`; nine of the eleven
entries there exist to refuse exactly this reading.

**(c) is accepted, then defused.** The charge is right that a body's name proves nothing, so the row
is built so no body name ever fires it. `never_alone` refuses certification bodies, notified bodies,
laboratories, chambers of commerce and regulators by name, quoting 00's Columbia sentence and then
arguing a body name is *weaker* than a university name — it appears as issuer, as subcontracted test
house, as a competitor's certifier, or as a bare citation. No organisation key is proposed and
`role_split` is refused. What fires the row is a relation in which the attestor is one term.

**(d) fails on the criterion owner**, and the boundary is written reciprocally on one fixture:
`EMC_Test_Report_XR-400_EN55032_2026-02-18.pdf` is this row's because its acceptance criteria are
clause references of an external standard designation and its cover carries an equipment-under-test
description and a laboratory accreditation identity; the identical layout with a `SYS-REQ` column
and no external designation is verification-validation's.

**(e) fails because two of the four default levels are wrong here and a needed one is missing.**
`project` is dropped — an issued instrument routinely outlives the project that produced it and is
re-cited by later ones, so a project level scatters one product's conformity file across
undertakings that no longer exist. `lifecycle_stage` is dropped per (a). The level the row actually
needs — the external rule — has no representation in the schema's set at all, hence one proposed
field. The result, design_item → conformity_scheme → engineering_artifact_type, shares one level and
one ordering principle with the default. That is a different order, not a re-spelling — which is
what `automotive-program` could not show, and why it was right to refuse where this row stands.

## The node test

**Leg 1 — detection signals: differ.** The anchor lists its default's structures explicitly (drawing
title block with item and revision; requirements table with stable requirement identifiers and a
verification-method column; BOM parent/child; engineering change naming an affected item and its
current/replacement revision; analysis against named requirements; verification matrix; TDP
manifest). Every one of those criteria is authored inside the organisation and revisable by it.
This row's are not: the criterion is a clause of an externally published rule with its own
designation and its own owner. The surviving structure is a four-way relation — identified product
model or type × external rule designation(s) × a role claim (declarant under own responsibility, or
body attesting on its own accreditation) × an issued instrument with its own identifier and
validity. The anchor's default has no slot for that relation and no fixture containing it; its
worked corpus is a brake-pedal requirements/drawing/BOM/change/verification/TDP set.

**Leg 2 — dimensions: differ.** Argued under (e). `time_first` stays false on 00's rule that "For
document and record domains, project, function, or subject usually comes before time because putting
year first scatters related work across calendar folders." — notable because certificates carry the
strongest labelled expiry dates in the schema and this is the one row where the year-first
temptation is real. A year-first tree would split a product's live certificate from the superseded
one it replaced.

**Leg 3 — privacy: does NOT differ.** Conceded rather than claimed. The schema is already
`potentially_sensitive` for proprietary design definition, supplier data, safety analyses,
export-controlled information, signatures and test evidence; a technical construction file is more
of that. The one property that looks different — an issued declaration is often meant to be handed
to customers and authorities while the technical file behind it is the most protected material in
the schema — is the maker's intent, not a rule this row may encode, since handling classes are P7's.
CONNECTION.md's test is disjunctive; `distinct_privacy_rules: false` says so in the JSON.

## Files considered and rejected

- **`ISO9001_Certificate_Acme-Ltd_2026-2029.pdf`** — kept, as the collision fixture (below).
- **`Calibration-Certificate_Fluke-87V_SN-30215442_2026-01-15.pdf`** — kept as a second collision.
  Accredited body, certificate number, standard designation, validity, traceability, pass; certified
  object is a *measuring instrument held as an asset* → `manufacturing.calibration-record`. It earns
  its place because an instrument model token and a product model token are indistinguishable at the
  token level — the evidence behind the "a model designation alone" never_alone rule.
- **`Certificate-of-Origin_INV-88421.pdf`** — third collision. *Certificate of conformity* means two
  unrelated things in the product-regulatory and freight worlds; this one has a consignor/consignee
  block, goods marks and an invoice reference → `logistics.customs-export`.
- **`EN-62368-1_2014.pdf`, the standard itself** — rejected from the corpus, edged to
  `engineering.standards-library`. It contains the strongest token this row recognises and is
  nonetheless the *rule*: clause structure, normative-references section, scope-and-definitions front
  matter, the standards body's copyright notice, naming no product and no declarant. A certification
  folder is where people keep it, and folder location is not evidence.
- **`EPC_Certificate_12-Acacia-Ave.pdf` / a gas-safety record** — the certified object is a premises
  at an address and the certificate travels with the property →
  `construction_property.compliance-certificate`. The appliance *model's* type certificate is mine;
  the single installed unit's commissioning certificate is `engineering.commissioning-handover`'s.
- **A first-aid, forklift or welder-qualification certificate** — rejected without an edge; the
  certified object is a person's competence and it never reaches this schema. Claiming it would have
  been the clearest possible case of chasing a document-type word.
- **A warranty certificate / certificate of authenticity from a product box** — a commercial promise
  to a buyer, not an assessment against a rule.
- **A CE/UKCA marking artwork file (`.ai`, `.svg`)** — rejected as an example, kept as a
  `never_alone` entry. The glyph appears on packaging files, marketing renders and competitor
  teardowns. Its approval record is a work type; the artwork is a design asset.
- **A certification-body invoice or annual-fee confirmation** — routed to `Receipts and
  Confirmations`, which is why that fourth residual is on the row.
- **A training deck about a directive** — cites the rule, assesses no product.

## Reciprocal boundaries, same fixture bytes both ways

Twelve `collides_with` entries, each written in both directions. The four that matter most:

| Neighbour | Shared fixture | Discriminator |
|---|---|---|
| `engineering.aerospace-airworthiness` | `Compliance-Checklist_Cabin-Interiors_Rev-D.xlsx` | continuing operating approval with effectivity/serial-range and a directive trail → theirs; point-in-time conformity ending at issue → mine |
| `engineering.embedded-firmware` | `SW-PN-40012-003_Software-Configuration-Index.pdf` | the released image and its configuration index → theirs, even though certification produces that document type; the granted certificate citing it → mine |
| `engineering.automotive-program` | `e11r-2018-858-00234-03_Whole-Vehicle-Type-Approval_XJ.pdf` | that row refused and asked R1c that this coverage be visibly absorbed; it is now `file_examples[4]`, with conformity-of-production routed to `manufacturing.quality-management-system` |
| `engineering.material-specification` | `RoHS-REACH-Declaration_PN-40012_supplier.pdf` | material-content evidence → theirs; regulatory-conformance evidence → mine; **same schema**, so a two-group question in `grouping_reasons`, never an `also_holds` edge |

The aerospace, firmware and automotive boundaries are transcribed from those rows' own wording so
the two sides cannot drift. No neighbour file was edited.

## The collision fixture

`ISO9001_Certificate_Acme-Ltd_2026-2029.pdf`. The best false positive on the node because **every
surface signal matches**: accredited certification body, accreditation mark, certificate number in
its own slot, standard designation with edition year, issue/revision/expiry dates, surveillance
clause. A row built on the word "certificate", on a body's letterhead, or on a standard designation
takes it every time.

One slot discriminates: the **scope clause names activities and site addresses of a legal person**,
and no product model, type designation, serial or batch effectivity appears anywhere. The certified
object is an organisation's management system → `manufacturing.quality-management-system`. Its
`facts_legal` in the JSON is the universals only — asserting `design_item` or `conformity_scheme`
there would be inventing facts not in the file — and its `must_not_conclude` quotes 00's Columbia
sentence to say why the organisation name settled nothing.

## `proposed_fields` — one key

**`conformity_scheme`**, string, `destination_eligible: true`, `reliability_ceiling: validated`,
adjudicate R1c. All 37 canonical keys were checked and none fits: `subject` is academic;
`record_type` and `artifact_type` name what a document *is*, the one thing that cannot decide this
row; the schema's proposed `engineering_artifact_type` has the same defect; `institution` would put
the attestor where the rule belongs, which is 00's role-ambiguity error made structural; `project`
names the undertaking; `stage` is a workflow position. The role needed is *the identity of a
criterion owned outside the organisation*.

Three disciplines applied. Under **D4** the values come from regulators' and standards bodies'
catalogues — a catalogue supplies values, never a node, which is the finding that refused
`automotive-program` and routed its type approval here; no catalogue is embedded and R4 owns
gazetteer contents. The ceiling names a rule *family* only (a rule-designation token confirmed by a
conformity-role structure in the same file); R2 owns the pattern, and this row writes no regex, no
complete term list, no threshold. And it is proposed at the **second** level, not the first, on 00's
parent-makes-child-intelligible rule: a certificate number, a clause checklist and a test report are
unintelligible without the product.

**Three keys were deliberately not proposed**, each of which would mint shared vocabulary to solve
one template's problem: an attestor/body key (NJ-CERT-2); a certificate-identifier key (a search
fact, like the schema's own `revision_or_baseline`, never a folder level); and any market or
jurisdiction key — **D4** already settles that `jurisdiction` is a value, never a field name and
never a destination dimension.

## Neighbours considered that did not get an edge

- **`business_operations.corporate-regulatory-filings`** — statutory filings are about the legal
  person, not a product; `business_operations.compliance-audit` already carries that seam.
- **`manufacturing.inspection-record` / `nonconformance-capa`** — real pass/fail overlap, but the
  engineering **schema row** already states the design-versus-execution boundary against
  manufacturing, and duplicating it here would give one evidence item a third claimant. The two
  manufacturing edges written are `quality-management-system` and `calibration-record`, because those
  contest *certificates* specifically, which the schema-level edge does not cover.
- **`manufacturing.environmental-compliance`** — a permit or emissions return is about a site's
  operation; left unedged to avoid a third claimant on declaration-shaped files.
- **`medical.*`** — the roster's medical rows are a person's own health records. The device
  submission fixture states it is *not* medical in `must_not_conclude` rather than taking an edge
  that would imply the two ever compete.
- **`legal.*`** — a regulatory notice is adjacent, but executed-agreement and matter-file evidence
  never collides with a conformity assessment.
- **`also_holds_with`: empty by contract.** Rule 14 restricts it to schema rows, and the engineering
  schema already declares co-holding with manufacturing, code, research, business_operations and
  construction_property. Every genuine multi-membership found here is *same-schema*
  (material-specification on the declaration; verification-validation on a dual-criteria report), so
  it is a two-group question. Adding one at template level would silently widen the schema's edges.
- **`role_split`: refused.** The split this material wants is attesting body vs declaring
  manufacturer — two organisations, different roles, often one page. No canonical key exists for
  either, and minting one for a single template is what produced thousands of private field names in
  the overnight pass. The distinction is carried where it is safe: the deterministic signals describe
  the declarant structure and the attestation structure separately, and `never_alone` refuses both
  names as proof. Recorded as NJ-CERT-2.

## Sparse-file discipline

`scan0007.pdf` is this node's `HW 3.pdf`: a flatbed scan whose OCR recovers a stamp, an illegible
signature and a partial date, sitting beside two accepted certificate files. No model designation,
no rule designation, no body identity survives. `group_without_copying_facts: true`, `facts_legal`
is universals only, and `must_not_conclude` quotes 00 — "A session should never be treated as proof
of topic". Activation and grouping stay separate: P9 may place it in the neighbourhood while this
row does not fire on it.

## Recommendations to R1c (nothing was written outside this row's two files)

1. `engineering.automotive-program`'s request is satisfied — its type-approval fixture is now
   `file_examples[4]` here with the absorption stated. No change needed on their side.
2. Reciprocate three edges on the neighbours' files: `engineering.verification-validation`,
   `manufacturing.quality-management-system` and `manufacturing.calibration-record` do not yet name
   this row from their side. Wording is ready in this row's `collides_with`, written both ways.
3. Adjudicate `conformity_scheme` (NJ-CERT-1). If it is refused, this row's dimension leg collapses
   and the node should be re-examined honestly rather than kept on leg one alone.

## NEEDS-JOSEPH (this node only)

- **NJ-CERT-1 — does `conformity_scheme` become canonical, or does an existing key widen?**
  (a) mint it as proposed; (b) widen `record_type`; (c) widen the schema's proposed
  `engineering_artifact_type`. (b) and (c) both collapse this row's only real dimension, because the
  whole finding is that one document kind lands on both sides of the seam depending on whose
  criteria it cites.
- **NJ-CERT-2 — the two-organisation problem.** Attestor and declarant are different roles on one
  page with no canonical key for either, so no `role_split` can be written. Alternatives:
  recognition-only structure (recommended); reuse canonical `institution` for the attestor, importing
  finance's issuer semantics into engineering; or mint an attestor key, which immediately raises
  whether a body's name may ever be a folder level (this row's answer: no).
- **NJ-CERT-3 — marketing type vs internal item.** Certification identifies a model or type placed on
  a market; the schema's proposed `design_item` identifies an internal configuration item. When one
  corpus carries both, is that one `design_item` fact, two, or a role_split that cannot be written
  until the keys exist? Related to the schema's own NJ-ENG-1.
- **NJ-CERT-4 — expiry-driven views.** Certificates carry the strongest labelled expiry dates in the
  schema and drive renewal behaviour no other engineering row has. This row keeps `time_first: false`
  and treats issue/expiry as search and reminder facts. If the product ever surfaces expiry-driven
  views, confirm these stay facts and never become a dimension.

## Audits run before returning

- `python3 -m json.tool` — parses.
- All eight spans quoted from 00 re-matched **verbatim** under whitespace/curly-quote normalisation:
  the Columbia sentence, the archive-manifest and no-extraction rules, the session rule, the
  filename-purpose rule, the extension-routing-signal rule, the project-before-time rule, and the
  Receipts and Confirmations definition. All four `falls_through_to.design_cite` values matched. The
  ~55 spans the extractor flagged were apostrophe artifacts (it split on `'s`) and were read by
  hand — the same artifact the crypto row documented. **No 00 quotation here is fabricated or
  paraphrased inside quote marks.**
- Every `file_examples.source_type` is in `SOURCE_TYPES` (12/12); every `file_kinds.source_type`
  likewise (9/9).
- Every `collides_with.domain` resolves to a `roster.json` `domain_id` (12/12). Every
  `falls_through_to.residual_template` and `falls_through_if_inactive` is one of 00's nine residual
  names.
- `fields: []` per PR-6; `proposed_fields` has exactly one entry with `adjudicate: R1c`;
  `template.dimension_order` is `[]` with the conditional order argued in `why`.
- `also_schema` is `null` on all twelve examples, by rule 14. No example writes a folder path as a
  fact.
- No number in the file is a threshold, score or evidence count; no handling class is assigned;
  `sensitivity` is `potentially_sensitive`, inherited and explicitly not widened.
- Only the two assigned files were written. `planning/29-DOMAIN-OWNERSHIP.md`, the roster,
  `canonical_fields.json`, `check.py`, `src/` and every neighbour node are untouched.

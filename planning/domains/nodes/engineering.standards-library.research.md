# engineering.standards-library — lab notes (R1b)

Depth: J-DEPTH
Date: 2026-08-26
Roster row: `kind: template`, `schema_id: engineering`, `launch: placeholder`, `parent_id: null`.
Output: [`engineering.standards-library.json`](engineering.standards-library.json).
Salvage: none — no prior draft of either file existed.
Verdict: **node survives**, `refuse_node: false`, on all three legs — but it survives on a
definition I had to replace, and that replacement is the main product of this pass.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` — the standing brief and its six requirements.
- `python3 planning/domains/dispatch/make_prompt.py engineering.standards-library` — the stamped
  assignment: neighbours `manufacturing`, `code`, `research`; residuals `Independent Records`,
  `Review Later`; `inherited_field_keys: []`; the node test; the output shape.
- `planning/00-database-agent-product-design.md` — read by targeted `grep -n`, never streamed.
  Four spans were pulled and every one of them greps back verbatim (audit below): the residual
  library paragraph, the narrow-date-extraction rule, the extension-as-routing-signal rule, and
  the grouping stop-rule on irreconcilable facts.
- `planning/domains/nodes/finance.crypto-assets.research.md` — the one launch row read for
  calibration, per the brief. It set the shape of this memo: charge first, three legs argued
  separately, files considered and rejected as a first-class section, reciprocal fixtures named
  on both sides, NEEDS-JOSEPH left open rather than smoothed.
- `planning/domains/nodes/engineering.json` — the schema anchor. Read for its `proposed_fields`
  (`design_item`, `lifecycle_stage`, `engineering_artifact_type`, `revision_or_baseline`), its
  `recognition`, and its `template.why`, which states the researched default order
  `project → design_item → lifecycle_stage → engineering_artifact_type` and the PR-6 rule that
  keeps `dimension_order` empty. That default is what this row is measured against.
- `planning/domains/nodes/engineering.material-specification.json` — read in full for its
  collision text against me, its `template` idiom, `falls_through_to` shape, and NJ-MS-2.
- One grep (`grep -rn "engineering.standards-library" planning/domains/nodes/*.json`) returned the
  four neighbours that had already argued a boundary against this row:
  `engineering.cad-model`, `engineering.drawing-package`, `engineering.civil-structural`,
  `engineering.aerospace-airworthiness`. Only the matched spans were read.
- `planning/domains/roster.json` — every edge endpoint confirmed programmatically (0 bad ids).
- `planning/domains/canonical_fields.json` — full key list read once; no key minted.
- `src/evidence_shape/vocabulary.py` `SOURCE_TYPES` — checked mechanically against all twelve
  file examples and the `file_kinds` list.

Not read, deliberately: `01-product-design-structured.md`, `CONNECTION.md` in full, other rows'
memos, `research.reading-library`'s full node (one targeted grep only). Token budget.

## THE CHARGE — the strongest case that this row should not exist

I built the case before writing anything, and it is a strong one. Five limbs:

**(a) It is defined by an absence.** The roster hint says "received documents, usually licensed,
**never authored here**." Absence of the holder's authorship is not a property of the bytes. A
received PDF and an authored PDF are the same object on disk; nothing in a file says "somebody
else wrote this." The brief names *a row defined only by the ABSENCE of something* as a refusal
condition, and on the hint's own wording that is exactly what this is.

**(b) It rests on an organisation name.** "Issued by ISO / ASME / IEC / SAE" is the natural
second answer, and it is never-alone evidence of the purest kind. Those names appear on the
reseller's invoice, on marketing PDFs, on certificates of conformity, in a note on every drawing,
and in every civil-structural calculation. `engineering.material-specification` states the
boundary against me as *"The discriminator is issuer role, not content"* — and if issuer role
is genuinely the only discriminator, then this row's entire activation rests on evidence the
design forbids as sole proof, and it can never fire.

**(c) "A standard" is a document-type word.** Like "invoice", "syllabus" or "receipt". Those are
values of a kind field, not nodes. The engineering schema already proposes an
`engineering_artifact_type` enum spanning requirement, drawing, model, schematic, calculation,
interface definition, change request and verification record; "published standard" could simply
be one more member of it, and the row dissolves.

**(d) It duplicates a neighbour.** `engineering.material-specification` already owns "the
normative definition of a substance, a bought component or a process step … held as a document
with its own identifier and issue, invoked by many design items and outliving all of them." That
sentence is a complete description of a standards shelf. Two rows, one description.

**(e) It duplicates a residual.** `00`'s Reading Inbox is defined as holding *"papers, articles,
reports, and saved PDFs that appear to be reading material but have no active research, course,
or project association."* Received reference PDFs with no project association is the whole row.
`research.reading-library` makes the same claim at node level.

Any one of (a), (b) or (d) alone would be enough to refuse. I take the charge as decisive unless
answered with structure that is visible on the page.

## Defeating the charge — and what had to change to defeat it

The row survives, but **not on the hint's terms**. It survives only after the definition is
replaced, and I replaced it in `one_line`.

The activating fact is not provenance. It is a **document architecture** that is present in the
bytes and that no other engineering row has: a designation-shaped token co-occurring with

- a **foreword or preface naming a technical committee** (and, on ISO/EN-family documents, the
  national member bodies that balloted it),
- a **numbered clause hierarchy opening at a Scope clause**,
- a **normative-references clause** listing other designations,
- a **terms-and-definitions clause**,
- a **reproduction / licence notice**,

and, used only alongside one of those positives, an **absence set**: no title block, no approval
or signature slot, no affected-item slot, no effectivity list.

That constellation answers each limb:

- **(a)** falls, because nothing above is "not authored here." I went further and encoded the
  hint's own phrase on `never_alone`: *absence of the holder's authorship* is listed as forbidden
  evidence. The row explicitly refuses the definition it was assigned.
- **(b)** is conceded and split rather than argued away. The issuing body is `never_alone` as
  **evidence** and is simultaneously the recommended first dimension as a **fact**. That is
  ALIGNMENT's observation/fact distinction doing real work: a body name on a page is an
  observation that proves nothing; `issuing_body = ASME` is a fact that may only be written after
  the architecture has fired. Both are true at once, and the row is coherent.
- **(c)** falls, because the row is not activated by the word. "Standard", "Specification",
  "Code", "Norm" and "Regulation" in a filename are all on `never_alone`. What makes it a node is
  a corpus whose retrieval key is a publisher's catalogue rather than any designed item.
- **(d)** required the sharpest work and produced the row's real contribution: a discriminator
  against `material-specification` that is **not the issuer's name**. It is the
  **consensus-process fingerprint** — the committee foreword plus the mandatory
  normative-references clause. A producer's product datasheet has neither (one company describes
  its own part; there is no ballot and no committee). An in-house `MS-4120 Rev D` has neither,
  and additionally carries an **approval slot**, which a published standard structurally cannot
  have because it is addressed to every reader rather than to one organisation. That is structure,
  not provenance, so limb (d) fails and the two rows are genuinely distinct.
- **(e)** falls on architecture too: a paper is argued and cited (abstract, methods, bibliography);
  a standard is normative and clause-numbered (shall-clauses, normative references, scope). The
  honest residue is the **handbook / design manual**, which really does sit between us — it is on
  `needs_llm` and is NJ-SL-3, not smoothed over.

## The node test, all three legs

**Leg 1 — detection signals differ from the engineering default.** The schema activates on *a
relation among an identified design item, a lifecycle/design state, and controlled technical
artifacts*: title blocks with item and revision, requirement rows with verification columns,
change structures naming an affected item and its current/replacement revision. A published
standard has **none** of those relations and cannot acquire them — it names no design item,
carries no approval by the holder, and has no effectivity list, because it is addressed to
everybody. Its discriminators are a wholly different structure, listed above. This is not a
variation on the default; it is a disjoint signal set.

**Leg 2 — dimensions differ, maximally.** The schema's researched default is
`project → design_item → lifecycle_stage → engineering_artifact_type`. This row rejects **all
four levels**, which is a stronger result than the reordering most template rows produce:

- `project` — a standard is invoked by every project and outlives all of them. Filing it under the
  project that first cited it is the observed failure mode (`material-specification` reached the
  same conclusion independently for its own material, which corroborates it).
- `design_item` — a standard is what many items are built **to**, never what one item **is**.
  Worse, opening this level would fan **one licensed copy** into N item folders.
- `lifecycle_stage` — a standard has an **edition**, not a design gate. Reading a gate word out
  of a "Draft International Standard" marking would import the *publisher's* balloting stage as
  if it were the *holder's* design maturity. That is a fabricated fact and is refused explicitly.
- `engineering_artifact_type` — subsumed: every member of this row would take the same value.

The researched order is `issuing_body → standard_designation`, with edition deliberately **not**
promoted to a level (see below). A row that can fill none of its schema's default levels is the
opposite of a duplicate of that default.

**Leg 3 — privacy differs in kind, not degree.** This is the only engineering row whose corpus is
**licensed third-party copyright**. Single-seat standards PDFs are watermarked with the licensee's
personal name on every page and frequently in the filename, and many ship DRM-encrypted. Two rules
follow that no sibling needs: the licensee's name is a **person's name in the bytes** that must
never be written as `authored_by` nor surfaced by a filing decision; and the corpus must not be
duplicated across the tree, because the schema's default order would multiply a document the
holder is licensed to hold **once**. `sensitivity: potentially_sensitive` is set for that reason
and no other — not because standards are secret; most are purchasable.

## The collision fixture

**`Your standards order is complete - 3 documents.eml`** — a reseller's order confirmation. It
carries a publisher name, three designations and three editions, which is **more designation
evidence than several genuine members of this row show**. It is not this row's file.

The discriminator is the slot set. Transactional architecture — sender, order number, line item,
total, payment, download links — versus normative architecture — foreword, scope clause,
normative references, shall-clauses. The designations here are **line items of a transaction**,
not the identity of the document. It is `finance.receipts-expenses`'s from both directions, and
falls through to `Receipts and Confirmations`.

A second, harder one is kept as a file example: **`QMS Manual Rev 12 - AS9100D.docx`**, which
carries a standard's designation in its filename and a clause-by-clause cross-reference table.
Discriminator: an **approval block naming the holder's quality manager** and an **effective
date** — exactly the two slots a published standard structurally cannot have. It is
`manufacturing.quality-management-system`'s.

## Files considered and rejected

Beyond the two above, which were kept as fixtures precisely because they are false positives:

- **`91251A537.STEP`** — a vendor-catalogue component model. `engineering.cad-model` wrote the
  collision and placed it **here**, "because the identifier belongs to a vendor catalogue." I
  reciprocated the edge so the two rows are not mutually silent, but I **dispute the placement**
  in the edge text rather than quietly accepting it: a supplier part model has no clause
  hierarchy, no foreword, no normative references and no licence notice, so admitting it reopens
  the "anything received" definition the node test just rejected. It is NJ-SL-1 and it is not in
  `recognition`.
- **A producer's component datasheet (`LM317T`)** — rejected, and placed with
  `engineering.material-specification` from both sides. One company describing its own part runs
  no consensus process. That row's NJ-MS-2 calls the placement contested; I reciprocate it as
  NJ-SL-2 rather than claiming the file.
- **A Certificate of Conformity citing `IEC 60601-1`** — rejected. A certificate names a certified
  product, a holder, a certificate number and a validity period; a standard names none of them.
  `engineering.product-certification`.
- **A compliance checklist or gap-analysis spreadsheet against `ISO 13485`** — rejected. Its rows
  are the holder's assessments; the designation is the axis, not the identity. It is the QMS row's.
- **A training deck quoting clause text at length** — rejected. Presentation structure, authored
  by the holder. On `needs_llm` because the quoted text is genuinely dense in this row's
  vocabulary; `Reference Clips` if nothing fires.
- **A statutory instrument that adopts a code by reference** — rejected as a *member*. The
  enacting instrument is a different document from the code it adopts. Handled instead as
  `also_holds_with: government` on the code itself.
- **An in-house "Standards Deviation Note DN-14 against ASME B31.3"** — rejected, and kept as a
  member of the `standards_pack_2026.zip` manifest so the archive fixture has a mixed-role
  member. It is authored, it has an approval slot, and it is the change / specification side.
- **A textbook PDF (`Roark's Formulas for Stress and Strain`)** — rejected. No designation, no
  clause architecture, an ISBN rather than a designation. `research.reading-library`.

## `proposed_fields` — two, and one deliberate non-proposal

`fields: []` by contract (a template references its schema's fields and never copies them; PR-6
leaves the engineering schema with none declared). The honest position is stronger than that
formality: **none of the schema's four proposed keys can be filled by a published standard**,
which is why two keys are proposed and why NJ-SL-4 exists.

1. **`issuing_body`** — the organisation that *published* a normative document the holder merely
   holds. No canonical key covers it: `institution` is scoped to *the financial or record-issuing
   institution a record belongs to* and carries an account/ownership relation this material has
   none of; `venue` is research's journal or conference, i.e. where the *holder's own* artifact is
   published — the opposite direction; `school`, `our_firm`, `client`, `target_university` are all
   holder- or engagement-side. Destination-eligible **true and first**: every real standards shelf
   is shelved by body, because designation format, licence terms and amendment cadence are all
   properties of the body. It is a publisher, not authorship and not a person, so `00`'s ban on
   authorship as a destination does not reach it. `reliability_ceiling: validated` — rule family:
   a body-name or designation-prefix token co-occurring with one normative-document structure.
   No regex, no list, no threshold; R2 owns the pattern.

2. **`standard_designation`** — the document's own catalogue identity, the string a user searches
   and browses by. Not `design_item` (a standard is not a designed item), not `record_type` /
   `work_type` / `artifact_type` (enums of *kinds*; a designation is an *identifier*), not
   `project` or `subject`. Destination-eligible **true**, as the designation **family**.

3. **The non-proposal, which is the more interesting decision: I did not propose an `edition` or
   `issue` key.** Canonical `version_family` is already *membership in a draft/revision family of
   one logical document*, and the 2009 and 2018 editions of `ASME Y14.5` are exactly that family.
   Minting an edition key would be a synonym. I also declined a tempting third proposal,
   `adoption_status` (current / superseded / withdrawn): that is a fact about the world, not about
   the bytes — it changes without the file changing — and it would collide with the schema's
   already-contested `lifecycle_stage`.

`proposed_context_terms` (twelve) are marked PROPOSED for R6. `00` states the
pattern-plus-context *shape* for course codes only and lists none of these; no completeness is
claimed.

## Dimension order, and why edition is not a level

`issuing_body → standard_designation`, `time_first: false`, serialized as `dimension_order: []`
per PR-6 with the conditional order stated in `template.why` — the same idiom
`engineering.material-specification` and the schema anchor use, so the order is recorded in prose
rather than silently encoded before its keys are legal.

Edition stays metadata. A folder per edition scatters one document's series across the tree, and
the failure this world actually suffers is **working to a superseded edition** — which is fixed by
keeping the superseded copy *beside* the current one, not in a separate branch. `time_first` is
false for the same reason: a standard's conspicuous date is an edition, and time-first would file
`ASME Y14.5-2018` under 2018 and its predecessor under 2009, splitting the series. That is the
exact opposite of what a reference shelf is for.

## Reciprocal boundaries, with the same fixture bytes on both sides

Ten collisions. The four that neighbours wrote first are reciprocated in the wording they chose,
using **their** fixture filenames verbatim so the two sides name the same bytes:

| Neighbour | Shared fixture bytes | Where it lands | Discriminator |
|---|---|---|---|
| `engineering.drawing-package` | `Drawing standards - ASME Y14.5-2018.pdf` | **here**, both sides | title block vs committee foreword |
| `engineering.aerospace-airworthiness` | `Airworthiness-Code_Large-Aeroplanes_Amendment-27.pdf` | **here**, both sides | finding column / effectivity list / holder slot |
| `engineering.material-specification` | `AMS2750G-Pyrometry.pdf` here; `MS-4120 Rev D` and the `LM317T` datasheet there | split, both sides agree | consensus-process fingerprint, not issuer name |
| `engineering.civil-structural` | any `EN 1993` designation | code document here, calculation there | a calculation names a member, a load case, a result |
| `engineering.cad-model` | `91251A537.STEP` | **disputed** — see NJ-SL-1 | no normative architecture in a part model |
| `engineering.requirements-specification` | `ISO 2768-1_1989_General tolerances.pdf` vs a `Product Specification.docx` citing it | citation never relocates the standard | allocation/verification columns |
| `manufacturing.quality-management-system` | `QMS Manual Rev 12 - AS9100D.docx` | **there**, both sides | approval block + effective date |
| `finance.receipts-expenses` | `Your standards order is complete - 3 documents.eml` | **there**, both sides | transactional slot set |
| `engineering.product-certification` | a CoC citing `IEC 60601-1` | **there** | certified product, holder, validity period |
| `research.reading-library` | a downloaded design manual PDF | grey zone | argued/cited vs normative/clause-numbered |

`also_holds_with` carries only `government` — schema ids only, per the contract's restriction, and
matching `material-specification`'s idiom. `legal` was considered and rejected: a code adopted by
reference is not an executed instrument in a matter. No engineering-to-engineering relation is an
`also_holds` case; same-schema competition is a collision and a grouping question, never
co-activation.

## Neighbours considered that got no edge

- **`code.software-project`** — an assignment neighbour. Rejected: standards-as-code repositories
  and linter rule packs are repositories with manifests, and nothing in a published standard's
  architecture competes with repository evidence. No shared discriminating evidence.
- **`manufacturing`** generally, beyond the QMS row — a work instruction cites standards, but so
  does everything; citation is not competition.
- **`construction_property.compliance-certificate`** — a certificate again, already covered in
  kind by the `product-certification` edge; a second claimant on the same evidence shape would
  give one fixture three homes.
- **`academic`** — a standard used in a course is a course reading; `academic`'s own signals fire
  or they do not, and nothing here is contested.
- **`legal`** — see above, in `also_holds_with_note`.

## Sparse-file and grouping discipline

Four of twelve fixtures carry `group_without_copying_facts: true`, and each for a different
reason worth stating: the **standards register** is a catalogue, so no single row's designation
becomes the sheet's own fact; the **OCR'd clause photo** yields a partial running header and must
not be promoted to a full designation; the **archive** has members with three different roles and
one purchase reference that must not be smeared onto the standards members; the **order email**
carries designations that belong to line items. `grouping_reasons` names the cite-relation
explicitly as grouping-only, because copying a citing document's project and item facts onto a
standard produces precisely `00`'s stop-rule case of members carrying *"irreconcilable course,
institution, project, term, or purpose facts."*

## Audits run before returning

- `python3 -m json.tool` — parses.
- Nine quoted spans of fifteen characters or more (four inline, five `design_cite`) extracted
  mechanically and matched against `00` under whitespace/curly-quote normalisation: **9/9
  verbatim, 0 failures.** No fabricated quotation.
- All twelve `file_examples.source_type` values in `SOURCE_TYPES`; `file_kinds.source_types`
  a subset of it.
- All twelve `collides_with` / `also_holds_with` / `role_split` endpoints resolve to roster
  `domain_id`s: **0 bad ids.**
- All six `falls_through_to` names and all twelve `falls_through_if_inactive` values are among
  `00`'s nine residual names.
- `fields: []`; `proposed_fields` = `issuing_body`, `standard_designation`, both `adjudicate: R1c`.
- No threshold, score, count or handling class anywhere. `sensitivity` is
  `potentially_sensitive` only.
- No file example writes a folder path as a fact — every one carries `"a folder path"` in
  `must_not_conclude`.
- Only the two assigned files were written. No neighbour node, roster, canonical_fields, check.py,
  src/, SPEC or ownership register was touched.

## NEEDS-JOSEPH (this node only)

- **NJ-SL-1 — the vendor part model.** `engineering.cad-model` places `91251A537.STEP` in this
  row; this row reciprocates the edge but disputes the placement. (a) Vendor reference geometry
  stays with `cad-model` as reference-role files — this row's preference, because a part model has
  none of the normative architecture the row is defined by. (b) This row widens to "received
  reference material", which costs it its detection signals and re-admits the absence-definition
  the node test rejected. (c) A distinct reference-component row, which R1a would have to create
  and nobody has argued for. **Recorded, not resolved unilaterally.**
- **NJ-SL-2 — the producer's datasheet**, reciprocating `material-specification`'s NJ-MS-2. Placed
  with that row from both sides here, on the consensus-process ground. If R1c reverses it, this
  row's `material-specification` collision text changes and no other line moves.
- **NJ-SL-3 — `research.reading-library` has not reciprocated.** The design-manual / handbook case
  genuinely sits between us and this row currently claims the grey zone alone, which is exactly
  the asymmetry CONNECTION warns about. Recommend R1c ask that row to write the boundary back.
- **NJ-SL-4 — the deepest one, and the one I would most like adjudicated.** This row can fill
  **none** of the engineering schema's four proposed levels, and both keys it needs are its own
  proposals. Either R1c ratifies `issuing_body` and `standard_designation` — in which case this is
  a well-formed engineering template whose whole job is to be the one item-free shelf in an
  item-centred schema — or the honest conclusion is that a **reference library is not an
  engineering-schema situation at all** and the row should be re-parented to a reference-holding
  schema alongside `research.reading-library`. The row is written on the first reading. The second
  is not dismissed, and a reader of this memo should be able to act on it.
- **NJ-SL-5 — the roster hint should be amended.** "Received documents, usually licensed, never
  authored here" defines the row by an absence and by a licence status, neither of which is
  observable in the bytes. It is the single most likely cause of a future agent building an
  unactivatable row here. Recommend R1c replace the hint with the architecture definition this
  node's `one_line` now carries. **Recommendation only — the register was not edited.**

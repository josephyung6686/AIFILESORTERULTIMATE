# Research memo — `government.archives-recordkeeping`

Depth: J-DEPTH
Date: 2026-08-26
Output: `planning/domains/nodes/government.archives-recordkeeping.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, `launch: placeholder`
Verdict: **accept** (`refuse_node: false`), on two of the three node-test legs, argued below.

## Result in one paragraph

The row survives because its evidence is not a record of what a public body did. It is a **representation of custody over records the body did not author** — a transfer instrument, a multilevel description, a retention schedule, a fixity manifest, a closure review. Every other `government.*` row's evidence is the trace of an action: a rulemaking file records rulemaking, a planning file records a planning decision, an FOI file records a request being answered. This row's evidence is metadata about files that are *not in hand*. That single structural inversion produces detection signals the government schema's default does not have, and a privacy rule that runs *inside* one packet rather than across it. It does not produce dimensions — `dimension_order` is empty by contract — so the row wins on legs 1 and 3 and explicitly loses leg 2.

## Sources actually read

The standing brief in full; the stamped assignment; `legal.practice-matter-file.research.md` as the depth calibrator; `government.json` (the schema anchor — its default template, `work_types`, `never_alone`, `collides_with`, `falls_through_to`, `sensitivity_why`, `open_question`); `roster.json` to confirm my id and every edge id; and `business_operations.organisational-records.json` for its `refuse_reason` only, because it is both the reference refusal and the corporate-retention neighbour. `00` was read by targeted `grep -n` per the brief's token discipline — the archive-inspection, extension-routing, EXIF/screenshot, session, dimension-order, residual-library, protected-material, and non-destructive-lifecycle lines — and every span I put in quote marks was grep-verified verbatim before it was written.

One `grep -rl "archives-recordkeeping" planning/domains/nodes/` returned nothing, and none of `government.public-records-foi`, `government.museum-collection`, `government.library-administration`, `government.public-authority-record` exists yet. **No landed row has argued a boundary against me**, so every reciprocal boundary below is a recommendation for R1c rather than an alignment with landed text.

## THE CHARGE — the strongest case that this row should not exist

I put six arguments against the row before writing anything. Four of them are real and two are decisive-looking.

**(1) It is a lifecycle stage.** This is the strongest attack. "Records management" is literally the disposal end of every other government row's records. A retention schedule governs planning files, casework files, FOI files, procurement files. If the row is just *what happens to other rows' records when they get old*, it is a stage in a lifecycle, and the charge names lifecycle stages as a disqualifier — correctly, because a stage is a property of a record, not an organizational situation, and stages produce no evidence of their own.

**(2) It is an organisation name.** A national or municipal archives is an institution. The schema anchor's own `never_alone` already says a "government department, regulator, municipality, legislature, court, public school, archive, museum, or official-looking seal alone" cannot activate. A row whose whole content is "this file came from an archives" is exactly the `business_operations.organisational-records` failure: "an organisation name is constitutionally never-alone".

**(3) It duplicates its own schema's enumeration.** The `government` schema's `work_types` already contains "public education, accreditation, cultural-service, museum, library, archive, or records-management administration where the body sits inside the state". My entire world is one bullet in a list the schema already declares. Work types are values, not nodes.

**(4) It duplicates neighbours.** `government.public-records-foi` already owns "information request, search record, disclosure schedule, redaction record, refusal, review, or appeal response on the records-holder side" — access control over held records is arguably entirely theirs. `government.museum-collection` owns accessioning, donor instruments, and catalogue description. Between them there may be nothing left.

**(5) It is defined by an absence.** "Closed material" is a row defined by the absence of access, the way `business_operations.organisational-records` was a row defined by the absence of a more specific situation.

**(6) It is a file format.** EAD XML, BagIt, PREMIS, PUIDs. And `archive` is *literally one of the fourteen `SOURCE_TYPES`*. A row keyed to container formats is a `SOURCE_TYPES` row wearing a domain costume.

### Why the charge fails — the one fact that defeats it

Arguments (1)–(6) all assume the row's evidence is *the records held*. It is not. The row's evidence is **the custody apparatus**, and that apparatus is a distinct, physically separate set of documents that exist nowhere else in the catalogue.

Take the retention schedule attack (1). A retention schedule is not a stage of a planning file; it is a *different document from* a planning file, sitting in a different place, with rows whose subject is a series rather than a case. When a disposal certificate destroys series PL/07, the certificate is the only artifact left. A lifecycle stage leaves no artifact; this leaves a shelf of them. `Deed of Gift`, `Accession Register`, `Finding Aid`, `Retention and Disposal Schedule`, `Disposal Certificate`, `Preservation Action Log`, `Format profile`, `Access Review`, `Reading Room Production Request`, `Box List` — ten named document types, none of which is a member of the corpus it governs.

That also answers (3) and (4). The schema's work-type bullet names the *administration* of an archive as an authority function; it does not describe the description/described seam, which is the thing that changes classifier behaviour. And the FOI row's shared bytes are genuinely shared, which is why the JSON carries a mutex edge naming the same fixture on both sides — but an FOI disclosure schedule answers an external requester on a statutory clock, while an access review governs an already-accessioned item toward an opening date decades out. Different workflow, different anchor, different residual.

(2) and (6) are answered by the `never_alone` list, which was written specifically to make them fail: an archives institution's name cannot activate this row, and neither can `source_type: archive` or a `.zip` — because the design says to "treat the file extension as a routing signal rather than an assumption about meaning". `Site Photos Archive.zip` is in the fixture list precisely so this trap is visible.

(5) is simply wrong on inspection: closure is not the row's definition, it is one of eleven signals, and a wholly open repository produces the same accession, description, and preservation records.

## The node test, all three legs

CONNECTION's rule is that a template exists only where its **detection signals**, its **recommended dimensions**, or its **privacy rules** differ from the schema's default template. The `government` default template is the anchor's: `dimension_order: []`, `time_first: false`, with the prose recommendation "authority-side function or bounded proceeding/case/programme first, then an exact reference or cycle, then work type", a blanket `potentially_sensitive` posture over mixed authority packets, and recognition that keys on *an evidenced public body exercising a public function*.

**Leg 1 — detection signals: DIFFERENT, decisively.** The schema activates on evidence that a body *acted* in an authority role: a bill identifier repeated across a legislative packet, a rulemaking docket, a decision record. None of those signals fire on a finding aid, and the schema's signals would not recognise the eleven listed in this row's `deterministic` block. Four of them have no counterpart anywhere in the anchor: (a) a **prefix-extending hierarchical reference code** across nested description levels — the child code contains the parent's, which is a structural relation no other government artifact has; (b) a table whose **rows are other records** (series title, covering dates, extent, closure flag) rather than actions; (c) a **fixity/preservation event shape** — event type, agent, outcome, object identifier — read from a bag manifest without unpacking, per "Archives should be inspected without being unpacked to disk"; (d) a **custody handover instrument** with a depositor on one side and a receiving repository on the other. If this row did not exist, a finding aid would either fail to activate the schema at all or, worse, activate it and invite the classifier to read the *described* series' facts off the description — which is the `HW 3.pdf` error at collection scale.

**Leg 2 — recommended dimensions: IDENTICAL. This leg fails and I am saying so.** PR-6 leaves `government` fieldless, D1's deferral stands, and a template cannot branch on undeclared fields. My `dimension_order` is `[]` and so is the schema's; `time_first` is `false` on both. I record the intended order as prose in `template.why` and nothing more. Had I dressed that prose up as a difference, the row would be padded. One honest leg-2 loss is worth more than an invented dimension.

**Leg 3 — privacy rules: DIFFERENT, and differently-shaped.** The schema's default is a single blanket posture over a mixed authority packet: any protected member raises the whole. This row's seam runs *inside* one packet and runs in two directions at once. The finding aid is often written **for publication** while the item it describes is **closed for decades**; simultaneously the donor agreement, the closure justification (which names the living people the closure protects), and the reader production record (which reveals who consulted what) are **more sensitive than either**. A blanket rule gets this wrong in both directions — it over-protects a description meant to be public, and it under-protects a donor file sitting beside it. The row's `sensitivity_why` states that explicitly and still resolves to `potentially_sensitive`, because that is the only value available in this phase and P7 owns handling classes.

Two of three legs, one of them decisive. Accept.

## Files considered and rejected

- **`Site Photos Archive.zip`** — the word Archive, `source_type: archive`, a container. Rejected: no descriptor, no checksum manifest, no reference codes, flat dated JPEGs. Kept as a fixture because it is the cheapest false positive in the row.
- **`Grandma letters and photos - sorted by year.zip`** — scanned historic material, typed contents list, chronological arrangement. Rejected: the custody is the holder's family's, and careful private arrangement is not a repository. `photos.family-archive`.
- **`Records Retention Policy - Acme Ltd - 2026.pdf`** — full retention vocabulary. Rejected: no evidenced public body, no custody of another body's records. `business_operations.organisational-records` **refused**, so this routes to the `business_operations` schema default or Independent Records; it is not pulled here to fill a gap a refusal left.
- **`Planning Application 2019-0442 - Officer Report.pdf`** — a described item named in a box list held in the same corpus. Rejected: being *listed* by an archival description does not make a file archival. Marked `group_without_copying_facts: true`.
- **A repository's own board minutes, staff rota, and budget** — rejected to `government.public-authority-record`. This was the temptation to annex an institution rather than a situation, and refusing it is what keeps charge (2) defeated.
- **A catalogue or collections-management database, or a live records-management system** — rejected as nodes; a source system is not a file. A bounded export with a readable manifest is represented (`AIP_MS-0412_2026-05-02.zip`); live ingestion is a connector decision.
- **Published archival standards, cataloguing manuals, repository annual reports, preservation papers** — reading material with no custody workflow; `Reading Inbox`.
- **Genealogy downloads, digitised census images, old maps saved from a catalogue site** — the most common way archive-shaped bytes reach a personal corpus, and they are the *reader's* material, not the repository's. A shared download session cannot rescue them: "A session should never be treated as proof of topic".
- **A "dedicated archive location" chosen as a filesystem root** — rejected explicitly, because `00` uses that exact phrasing for a storage root in the source-selection step. A storage tier named Archive is the likeliest path-based false positive in a real corpus.
- **A backup checksum manifest** — fixity files are ubiquitous. Only a manifest bound to a package descriptor over a heterogeneous records payload counts.

## The collision fixture

**`FOI Request 2026-118 - Disclosure Schedule.pdf`.** It looks exactly like this row's evidence: it is held by a public body, it is *about* records rather than being one, it lists documents one by one, it applies exemptions, it withholds. A naive rule keyed on "a document that decides access to other documents" would take it.

What discriminates it is the **workflow anchor and the direction of the clock**. The FOI schedule is anchored to an *external requester and a request reference*, and its horizon is a statutory response deadline measured in days. `Access Review - MS-0603-14 - closed until 2059.docx` is anchored to an *archival reference code for an already-accessioned, already-described item*, and its horizon is an opening date measured in decades. Neither is decided by exemption vocabulary, redaction marks, or the presence of a public body — both have all three.

Stated reciprocally, as R1c will need it:

- **This row → `government.public-records-foi`:** if the deciding document names a requester and a request reference and runs to a response, it is theirs even when the records at issue are archived.
- **`government.public-records-foi` → this row:** if the deciding document names an archival reference for accessioned material and runs to an opening or review date under a custody function, it is this row's even when exemption language is identical.
- **Undecidable case, named on both sides:** a redaction record carrying both a request reference and an archival reference. Neither row takes it; `Review Later`.

## Reciprocal boundaries

Six mutex edges are authored, each naming the same fixture on both sides.

- **`government.museum-collection`** — the closest neighbour and the one most likely to want my fixtures. Same deed-of-gift shape, same accession register, same condition/preservation records, often the same institution. **Mine when** the described unit is a *series or file* arising from an activity and the description is hierarchical with prefix-extending codes. **Theirs when** the described unit is an *object* catalogued individually with material, dimension, condition, and display slots. Shared fixture: `Deed of Gift - Halloran Family Papers`. A collection-level record with neither hierarchy nor object slots is undecidable and both sides abstain.
- **`government.library-administration`** — same cataloguing, same digitisation batches, same reading room, frequently the same building. **Mine when** the material is unique and keyed to provenance. **Theirs when** the material is published, exists in many copies, and is keyed to bibliographic identifiers and holdings counts. Shared fixture: `Digitisation Master - MS-0412-3-11 - 600dpi.tif` — it follows whichever description system its reference code belongs to, and a bare reading-room production request follows the same rule.
- **`government.public-authority-record`** — competes over every retention schedule, file plan, and records-management policy, and over the repository's own corporate paperwork. **Theirs when** the schedule governs the authority's live files in its own business use. **Mine when** the same schedule is cited by a transfer instrument or a disposal certificate moving or destroying a series under a custodial function. Shared fixture: `Retention and Disposal Schedule - Planning Function - v4.xlsx`, which is theirs on its own and mine when `Disposal Certificate - Series PL-07` cites it.
- **`photos.family-archive`** — shared fixture `Grandma letters and photos - sorted by year.zip`, as above. Age, arrangement quality, and the word archive are worthless on both sides.
- **`legal.practice-matter-file`** — a closed-file store or deeds packet has box lists, retention periods, destruction certificates, and is routinely called an archive. **Theirs when** the custody is a practitioner holding client files under a representation. **Mine when** a public repository holds transferred records under a custodial function. Shared fixture: a destruction certificate, which decides nothing by itself; the holder-role evidence decides.
- **`government.public-records-foi`** — above.

## Neighbours deliberately given no edge

- **`government.constituent-casework`, `government.social-services-casework`, `government.elections-administration`** — their records are frequently *what an archive holds*, but holding is not competing. Being described never transfers a row's evidence. Adding these would rebuild the lifecycle-stage mistake the charge warned about.
- **`business_operations.organisational-records`** — refused, so there is nothing to collide with. Its coverage routes to the `business_operations` schema default and Independent Records, and this row does not inherit that vacancy. Recorded here so R1c does not read the absence of an edge as an oversight.
- **`nonprofit.governance` / `nonprofit.religious-institution`** — a diocesan, union, or charity archive behaves identically to a public one. This is not a mutex but a **status question**, and it is NEEDS-JOSEPH item 4 rather than an edge, because the discriminator is public-body status, which the anchor already owns at schema level.
- **`research.reading-library`** — archival standards and preservation literature go to `Reading Inbox` by residual, not by an edge.
- **`photos.scanned-documents`** — genuine coactivation, not a collision. The digitisation-master fixture carries `also_schema: "photos"`.

`also_holds_with` is empty and `role_split` is empty for the same reason `legal.practice-matter-file` left them empty: a template cannot author schema-level coactivation, and with no declared field keys there is nothing to split a role across. That is a real loss here, because this row has the clearest role split in the government tree — the **depositing body** and the **receiving repository** are the same entity type in different roles, and a transfer instrument names both on one page. It stays prose until PR-6 is adjudicated.

## Fields

`fields: []` and `proposed_fields: []`, both deliberate.

The anchor's `open_question` instructs that future government vocabulary be adjudicated "centrally rather than in children". Three concepts genuinely have no canonical home — a custody unit (collection or accession), a description level, and an archival reference code — and I considered proposing them. I did not: PR-6 forbids government fields outright; a child minting vocabulary for its schema inverts the adjudication order the anchor set; and a reference code is the *last* thing that should become a folder level, since a hierarchical code exposes collection structure in a path while telling a human nothing. NEEDS-JOSEPH item 2 instead. Canonical `institution`, `record_type`, `project`, and `purpose` were checked and are all scoped elsewhere; none means custody.

## Grouping without copied facts

The defining grouping rule is negative: **the description and the described item stay in different groups even when they share a reference code exactly.** Every other grouping mechanism in the product treats an exact shared identifier as a strong join; here it is a trap, and it is why four fixtures carry `group_without_copying_facts: true` — the finding aid, the box list, the transfer email, and the officer report named in the box list.

Positive groups are bounded by an exact accession or transfer reference across instrument, box list, appraisal note, format report and preservation log; by a hierarchical prefix within one collection; by a bag or object identifier read from a manifest; and by a schedule-row-to-certificate link. Donor, closure and reader files stay in a protected group of their own rather than joining the public description group they point at. A package is never unpacked to strengthen recognition.

## Tensions I could not resolve

The row's best structure is a hierarchy and the contract forbids it from expressing one, so leg 2 is lost for a reason about PR-6 rather than about the world. Public availability of a description does not lower the posture of what it describes, and the reverse also holds, but there is no representation for a per-member privacy seam inside one packet in this phase. Retention scheduling is simultaneously the row's most recognisable vocabulary and its least reliable signal. And repositories that behave archivally without being public bodies — university, diocesan, corporate — are a large real population this schema cannot claim.

## NEEDS-JOSEPH

1. **The description/described-item seam has no representation.** P9 needs a way to record that file A *describes* corpus B without the exact-reference join copying facts between them. Alternatives: (a) a typed non-propagating edge in the graph; (b) suppress exact-reference joins entirely for this row and rely on lifecycle references only, losing real structure; (c) leave it to per-file abstention, which is the status quo and silently wrong. This row cannot author any of them.
2. **If PR-6 is lifted**, decide centrally whether a custody-unit concept, a description level, and an archival reference code may exist as `government` fields, and whether any is destination-eligible. My recommendation, non-binding: custody unit yes, level yes, reference code searchable but **not** destination-eligible. This row proposes none of them.
3. **Retention periods and the residual lifecycle.** `00` already permits user-defined review policies while forbidding deletion or disposability marking without explicit user action. Decide whether a retention period read out of a *document* may ever seed a review suggestion (it would be useful and it would also mean acting on another organisation's policy), or whether such periods stay inert observations. Default if unanswered: inert.
4. **Public-repository status for hybrid bodies.** University, diocesan, corporate, and community archives behave identically to public ones. Alternatives: deployment-specific gazetteer; user confirmation; or abstention to `Review Later`. This interacts directly with the anchor's own open question about quasi-public bodies and should be answered once, there, not here.

## Self-verification

- `python3 -m json.tool` parses the node; key set matches `government.json` and `legal.practice-matter-file.json` (plus `proposed_context_terms`, which the anchor also carries).
- Every quoted span was grep-verified verbatim against `planning/00-database-agent-product-design.md` before being written: the extension-routing clause, the EXIF clause, the session clause, the dimension-order clause, the archive-inspection clause, the protected-material clause, and all six residual definitions.
- Every edge id (`government.public-records-foi`, `government.museum-collection`, `government.library-administration`, `government.public-authority-record`, `photos.family-archive`, `legal.practice-matter-file`) was confirmed present in `planning/domains/roster.json`. Every `falls_through_to` name and every `falls_through_if_inactive` value is one of `00`'s residual homes.
- Every `file_examples.source_type` is in `SOURCE_TYPES`. No file example writes a folder path as a fact. `fields` and `proposed_fields` are empty. No threshold number, no confidence score, no handling class appears anywhere in either file.
- I wrote only my two assigned files and edited nothing else.

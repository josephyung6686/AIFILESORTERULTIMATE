# Research memo — `law_practice.discovery`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.discovery.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, `launch: placeholder`
Absorbed legacy ids (from `one_line_hint`): `law.document-review`, `law.ediscovery-production`

## Result

**Accepted, narrowly, and the narrowing is the whole result.** The row does not stand on the litigation stage called discovery, on the word disclosure, on a Bates stamp, or on the fact that a document was produced. It stands on two structures its schema's default template cannot see: the **reproduce-then-answer demand instrument pair**, and the **produced-corpus apparatus** — preservation notice, custodian collection log, review-coding log, withholding schedule, redaction log, load file, image cross-reference, production volume manifest. Everything else that ordinary speech calls discovery is ceded by name to a named sibling.

## The charge — the strongest case that this row should not exist

I put five arguments against the row before writing anything. Three are serious.

**1. Discovery is a LIFECYCLE STAGE.** This is the strongest attack and the brief names the category explicitly. In civil procedure, discovery *is* the phase between the close of pleadings and trial. A stage is not a node: it is a position in a timeline, and the roster already has `law_practice.pleadings` before it and `law_practice.trial-preparation` after it. If the row's only content were "the files that exist during this phase," it would be a calendar slice wearing a filing label, and it would swallow depositions, expert exchange, motions to compel and interim orders purely because they happen in the same months.

**2. It duplicates its own schema's default template.** The `law_practice` schema anchor already carries, as the sixth of its twelve deterministic signals, "A DISCLOSURE-REVIEW structure: a review or coding log with one row per document carrying a document or control identifier, a reviewer, a coding decision (responsive, not responsive, further review), and an issue or category tag; or a PRIVILEGE LOG with one row per withheld document…". The node test in CONNECTION is that a template exists only where its detection signals, dimensions or privacy rules **differ** from the schema default. If the review log and the privilege log are already the schema's signals, half this row is a copy.

**3. It is a document-type word.** "Request for Production", "Interrogatories", "Privilege Log" are names of document types, and the schema strikes a document-type word — even beside a firm or client name — as never-alone. A row assembled out of document-type words is a form-book table of contents, not an organisational situation.

**4. It is an organisation-shaped / role-shaped id.** Weaker. The row does not depend on a law-firm name or a practising certificate, so the schema's existential strike does not land here.

**5. It is defined by absence.** Weakest, but worth naming: "documents we have not produced" (the privilege log) is a row defined by what is *not* there. That is a real hazard and it is why the withholding schedule is not permitted to activate the row alone.

### Why the charge is defeated (and exactly how far)

Attack 1 is defeated by **conceding it entirely**. The row makes no stage claim. It cedes:

- oral discovery — depositions and transcripts — to `law_practice.depositions-testimony`, recorded as a mutex so the cession is enforceable rather than polite;
- discovery motion practice — motions to compel, protective-order applications — to `law_practice.motions-and-briefs`, and the resulting orders to `law_practice.orders-and-judgments`;
- exhibit and bundle organisation to `law_practice.evidence-exhibits`;
- prose correspondence about disclosure to `law_practice.matter-correspondence`.

What remains after those cessions is not a stage. It is a pair of **document grammars** and a **machine artefact family**, and both are testable on bytes.

Attack 2 is defeated by evidence the schema itself supplies. The schema's twelve signals contain the review log and the privilege log — and **nothing else** from this world. It has no signal for a numbered demand instrument, no signal for the reproduce-then-answer counterpart, no signal for a load file or an image cross-reference, no signal for a contiguous control-number volume manifest, and no signal for a preservation-and-custodian structure. More decisively, the schema's *precondition* forbids it from seeing them: the default requires "an exact matter, file or engagement reference repeated" as one leg of every signal, and a load file, a native member and a production archive routinely carry **no matter reference anywhere in their bytes** — the volume designation is the only anchor they have. This row narrows that precondition for exactly three signals (D5, D6, D9) and that narrowing is a real, argued difference from the default, not a restatement of it.

Attack 3 is defeated by the observation that the row's signals are **not** the document-type words. D1 does not fire on the title "Requests for Production"; it fires on the two-party propounding/responding designation plus a definitions-and-instructions block plus either the reproduce-then-answer counterpart or a certificate of service. The words are struck by name in `never_alone` — including the row's own name, because a procedure-course handout titled with every one of them trips nothing else.

Attack 5 is answered by rule rather than argument: `A WITHHOLDING OR EXEMPTION SCHEDULE ALONE` is struck, precisely because the same table with a statutory basis column is an information-rights response.

**The honest residue.** If R1c decides that D1, D5 and D6 belong directly on the schema's own signal list, the correct outcome is **refusal**, and NJ-LPD-1 says so in the node file with the routing spelled out. I would rather this row be refused than kept to save an id.

## The node test, all three legs

**Leg 1 — detection signals differ from the schema default.** Yes, and this is the strongest leg. Nine signals are authored. D1 (reproduce-then-answer instrument pair), D2 (disclosure list partitioned by control status plus a search certificate), D5 (load file / image cross-reference header vocabulary and document-break flag), D6 (volume manifest with sibling image/native/text/data directories and a contiguous identifier run), D7 (custodian-and-source collection structure) and D8 (item-by-item deficiency enumeration) have **no counterpart** among the schema's twelve. D3 and D4 overlap the schema's sixth signal and are refined here — D3 adds the closed decision set and the batch anchor, D4 adds the asserted-basis column as the slot and the literal-preservation rule. D9 is the schema's email/calendar signal re-anchored on a volume designation instead of a matter reference. Twelve `never_alone` entries are authored; four of them are this row's own rather than the schema's, and the third — a numbered list of document demands — is the strike that keeps the row from eating due diligence and audit.

**Leg 2 — recommended dimensions differ.** `dimension_order` is `[]`, as it must be on a fieldless schema, so the difference has to be argued in the recommendation prose, and it is. The schema default's prose recommends *client → matter → document function → period*, with the client level seeded ineligible. This row's prose recommends *matter → exercise (demand set / review tranche / production volume) → period*, and it **permanently seeds two additional levels ineligible that the schema never had to consider**: the control-number level (one folder per document — the meaningless-one-child-level failure at industrial scale) and the **custodian** level, which would name real third parties, usually the client's own employees, as permanent directory labels. Those two exclusions are peculiar to this row and do not follow from anything the schema says.

**Leg 3 — privacy rules differ.** Yes, and on different grounds from the schema's, which matters. The schema's privacy claim is that a matter file holds documents *about* named third parties. This row's claim is that a production or collection **is the wholesale contents of other people's mailboxes, drives and devices**, that the review log and load file **concentrate the readable substance of thousands of those documents into a single spreadsheet column**, that a withholding schedule leaks precisely by being summarised because it describes what was *not* handed over, and that a control-range label discloses volumetrics. Different mechanism, different failure mode, stricter posture. All four are argued in `sensitivity_why` against 00's corpus sentence and its protected-summary sentence.

Verdict: three legs, three differences. `refuse_node: false`.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md`; the stamped assignment from `make_prompt.py law_practice.discovery`.
- `planning/00-database-agent-product-design.md` — grepped, not streamed. Every span in quote marks in the node JSON was verified against the source with an exact substring test before the file was finalised; one candidate quote failed and was corrected to the verbatim text (`A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.`).
- `planning/domains/nodes/law_practice.json` — the schema anchor and my default template. Read as extracted structure: `one_line`, all twelve `deterministic`, nine `needs_llm`, fifteen `never_alone`, `template.why`, `work_types`, `grouping_reasons`, `collides_with`, `also_holds_with`, `falls_through_to`, `role_split`, `sensitivity_why`, `open_question`, and its thirteen fixture names.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — read in full as the depth calibration, per the brief.
- `planning/domains/roster.json` — confirmed my row, and confirmed by lookup that every neighbour id I cite exists (all thirty-seven `law_practice` rows, `legal`, `finance`, `medical.personal-health-records`, `identity.core-documents`, `government.public-records-foi`, `business_operations.compliance-audit`, `career.consulting-client-engagement`).
- `grep -rl "law_practice.discovery" planning/domains/nodes/` returned **nothing**: no landed row has argued a boundary against this id, so every edge here is one-way and R1c owes all the reciprocals.

## Files considered and rejected

These are the tempting false positives. Naming them is the point; a row that lists only what it holds has not been researched.

- **`Due diligence request list - Project Hartley - v4.xlsx`** — numbered demands for another organisation's documents with a per-item status column. Rejected: buyer/seller roles rather than a propounding/responding pair, category grouping by corporate function, a *provided / outstanding / in data room* vocabulary, and a data-room index rather than a load file. Goes to `law_practice.due-diligence`. This fixture is the reason D1 requires the party-role pair.
- **`Audit prepared-by-client list`** — the same shape again, with an audit-period header and an auditor/auditee pair. Goes to `business_operations.compliance-audit`.
- **`Subject access request response - J Marsh - redacted bundle and exemption schedule.zip`** — the **collision fixture of record**, treated at length below.
- **`Motion to Compel Production - FILED 2026-08-20.pdf`** — recites this row's numbered requests for pages. Rejected on structure: caption, argument-and-authorities, relief requested, filing mark. Reciting item numbers does not move a filed motion here.
- **`Bates HN0004512.pdf`** — a single produced page. Rejected because the stamp is struck by name; a contiguous run across several files is struck too. This is the row's own hardest concession: the control number is simultaneously its best grouping anchor and its worst activation evidence.
- **`Disclosure and Discovery - Part 31 lecture handout.pdf`** — reproduces a specimen list of documents and a specimen privilege log as illustrations. Rejected on purpose, not topic. Reading Inbox.
- **A deposition transcript, an exhibit bundle index, a trial bundle.** Rejected by cession: `law_practice.depositions-testimony`, `law_practice.evidence-exhibits`, `law_practice.trial-preparation`. The temptation is real because in one procedural tradition a deposition *is* discovery.
- **A generic litigation-hold policy template with blank party slots.** Rejected: an unexecuted template with deliberately empty slots is the schema's own precedent-bank inverse-recognition signal, and belongs to `law_practice.precedent-bank` or `business_operations.policy-handbook`.
- **A discovery vendor's invoice or SOW.** Rejected: `finance` on issuer/billed-to slots, or `career.consulting-client-engagement`. A vendor name appears on its marketing, its invoices, its installers and its output alike.
- **A raw `.pst` mailbox export with no collection log.** Rejected as insufficient on its own — it is a mail container, not evidence of a collection exercise; the schema's session rule governs.
- **A regulator's information request served on the client.** Rejected here and pointed at `law_practice.regulatory-submission` / `government.public-records-foi` depending on side; the second-request shape is genuinely close and is flagged, not smoothed.

## The collision fixture

**`Subject access request response - J Marsh - redacted bundle and exemption schedule.zip`.**

Its manifest holds a request letter, a redacted document bundle, and a schedule of withheld material. That schedule's columns — author, recipient, date, description, asserted basis — are **column-for-column identical to a privilege log**. It is a request-and-response pair over documents, with redactions applied, produced as a bundle. Everything an unsophisticated signal would look for is present.

What discriminates it: the requester is a **single named individual acting for themselves**, there is no second adverse party and no set designation, the basis column cites **statutory access exemptions** rather than professional or litigation grounds, and the response carries statutory-deadline slots and a public-authority sender. Toward this row instead: two adverse parties, a set designation, and a professional or litigation basis vocabulary.

The fixture also carries a third possibility that neither side may claim by default — **in the individual requester's own hands the same bundle is `legal.personal-legal-matters` material**, not a practitioner artefact at all. That is why the boundary is written as three-way rather than two-way.

## Reciprocal boundaries

Eight mutexes are authored, each with the boundary stated in both directions and the same fixture named on both sides. Summarised here; argued in the JSON.

| Neighbour | Shared fixture | Toward this row | Toward the neighbour |
|---|---|---|---|
| `law_practice.due-diligence` | `Due diligence request list - Project Hartley - v4.xlsx` | propounding/responding pair + definitions-and-instructions + reproduce-then-answer or certificate of service | buyer/seller roles, corporate-function categories, provided/outstanding status, data-room index |
| `government.public-records-foi` | `Subject access request response … .zip` | two adverse parties, set designation, professional/litigation basis | single self-representing requester, statutory reference, exemption vocabulary, authority sender |
| `business_operations.compliance-audit` | an audit PBC list / an internal-investigation review log | control identifier from a declared production or collection; or an adverse-party demand | engagement-and-period header, control/finding reference, auditor/auditee pair, no adverse party |
| `law_practice.evidence-exhibits` | a produced page bearing both a production stamp and an exhibit label | cited by a load file, cover instrument or review log; identifier inside a declared bounded range | exhibit designation in a bundle index organised by hearing or witness |
| `law_practice.depositions-testimony` | the word *discovery* on both | written demands and written answers | reporter's certificate, appearances, Q-and-A pagination, errata, proceeding recording |
| `law_practice.motions-and-briefs` | `Motion to Compel Production - FILED …pdf` | the recited demand set and responses themselves, served not filed | caption, argument-and-authorities, relief requested, filing mark |
| `law_practice.matter-correspondence` | `Deficiency letter re Requests for Production Set One …pdf` | enumerates another instrument's items **by number** *and* that instrument is evidenced | any other letter about disclosure, chasing, or scope in prose |
| `legal` | a produced executed contract inside a volume | the apparatus — demand instrument, review log, withholding schedule, load file, manifest | the executed-instrument or proceeding structure, which runs first as a safety domain |

`also_holds_with`: `legal`, `finance`, `medical.personal-health-records`, `identity.core-documents` — four co-activations on disjoint evidence, all expressing the same rule: **being inside a production range is a relationship, not a reclassification.**

`falls_through_to`: Protected Records (primary), Review Later, Unsupported or Encrypted, Reading Inbox — each with a verified 00 quotation.

## Neighbours considered that did NOT get an edge

- `law_practice.investigation` — named inside the compliance-audit collision text as the row that sits between them, but not given its own mutex. An internal investigation review log with no demand instrument is its case, not a same-evidence contest with this row.
- `law_practice.legal-research` and `research.reading-library` — a practice note on disclosure is reading material. That is a residual routing decision (Reading Inbox), not a mutex.
- `career.consulting-client-engagement` — the consulting seam is the schema's, already argued there. A discovery vendor's SOW does not create a *second* contest at this row.
- `photos.screenshot-captures` — a screen capture of a review platform is Photos on positive screen-origin evidence, a co-activation case at most, and the schema already handles it.
- `law_practice.court-filing-record` — named in `never_alone` (a filing mark is its signal, not this row's) rather than as a mutex, because discovery instruments are typically served and not filed, so the two rarely contest the same bytes.
- `law_practice.time-and-billing` — a review-hours export shares a spreadsheet shape but its columns are timekeeper/rate/duration, which is the schema's own third signal. No contest.

## Fields and dimensions

`fields: []` and `proposed_fields: []`, both deliberate. The schema declares no fields (D1 as narrowed, PR-6), so a template on it may declare none. Candidates were considered and **all rejected rather than proposed**:

- `requesting_party` / `responding_party` — the row's central distinction, and it has no canonical keys. The canonical `our_firm`/`client` pair does not fit: these are two **adverse** parties and the holder may act for either. Recorded as NJ-LPD-3 rather than minted, and `role_split` is `[]` for exactly that reason.
- `production_volume` and `control_number_range` — real, bounded, and genuinely useful as **grouping anchors**, which is precisely why they must not become fields: destination-eligibility is the leak. A visible range label announces how many of another party's documents are held.
- `custodian` — the most tempting person-fact in the family, and forbidden. Promoting a processing attribution to a fact and then to a directory level would name non-consenting third parties permanently. NJ-LPD-5.
- `review_batch`, `document_control_number` — one-child levels at industrial scale.
- `matter_id`, `case_number`, `practice_area`, `jurisdiction` — not canonical, and the schema already refuses them. Jurisdiction is neither a field nor a dimension anywhere in this family.

`time_first: false`: production dates, service dates, collection date ranges, document dates and filesystem dates are five different clocks and a time-first tree interleaves four of them wrongly.

## Cross-row recommendations for R1c (no neighbour file was touched)

1. **The schema's sixth deterministic signal now overlaps this row.** `law_practice`'s disclosure-review structure and this template's D3/D4 describe the same shapes. R1c should decide whether the schema keeps it as a general activator with this row as the refinement, or delegates it here entirely. Recorded as NJ-LPD-2 in the node.
2. **All eight mutexes and all four co-activations are one-way.** No landed row has argued against `law_practice.discovery`. R1c owes the reciprocals, in particular on `law_practice.due-diligence` and `government.public-records-foi`, where the shared fixture is named on this side only.
3. **`law_practice.depositions-testimony` should state the cession back.** In one procedural tradition depositions are discovery; if that sibling does not say so, the two rows will contest transcripts by vocabulary.

## NEEDS-JOSEPH

- **NJ-LPD-1 — the existence question.** Answered as a narrow yes and reversible. If the reproduce-then-answer grammar, the load file and the volume manifest belong on the schema's own signal list, this row should be **refused** and its coverage routed to `law_practice`, `law_practice.evidence-exhibits`, `law_practice.matter-correspondence`, `legal` and Protected Records. Alternatives are exactly those two: keep as a refinement, or fold into the schema default.
- **NJ-LPD-2 — signal ownership.** Schema keeps signal six as a general activator with this row refining it, or delegates it here entirely. This row has not edited the schema file.
- **NJ-LPD-3 — the adverse-party role pair has no canonical keys.** If D1 lifts, decide whether an adverse-party role pair is expressible at all, or whether it is inherently destination-ineligible. Alternatives: mint a pair; reuse `our_firm`/`client` (rejected here as a category error); or rule the pair permanently search-only.
- **NJ-LPD-4 — range-containment grouping needs a P9 ruling.** Every other group in this family joins on a repeated literal reference; this one joins on numeric containment within a declared bounded range. P9 must decide how containment is recorded as candidate membership without copying the volume, custodian or matter label onto the member, and what happens when a range is later extended or superseded.
- **NJ-LPD-5 — the custodian column.** Any future permission for custodian-level structure must be taken as an explicit privacy decision about naming non-consenting third parties, not as a filing convenience.

## Self-verification

- `planning/domains/nodes/law_practice.discovery.json` parses (`json.load`).
- Every quoted span was substring-tested against `planning/00-database-agent-product-design.md`; eleven candidates tested, one failed and was corrected to verbatim, ten passed unchanged. No quote is attributed to 00 that was not tested.
- Key set matches the `law_practice` schema anchor exactly, including `proposed_context_terms`.
- `fields: []`, `proposed_fields: []`, `dimension_order: []`, `role_split: []` — all argued above.
- Every edge target verified present in `planning/domains/roster.json`; every `falls_through_to` name is one of 00's nine residual homes.
- Every `file_examples.source_type` is drawn from `SOURCE_TYPES`; no file example writes a folder path as a fact; `facts_legal` is `[]` on every fixture because the schema declares no fields.
- Eighteen fixtures, covering labelled instruments, unlabelled correspondence, spreadsheets, a delimited machine artefact, email, an archive read without unpacking, OCR, an image, three collision fixtures, four co-activation cases, and an unreadable-item report.
- At least one `never_alone` trips a tempting false file: the numbered-demand-list strike trips `Due diligence request list …xlsx`; the withholding-schedule strike trips the subject-access bundle; the control-token strike trips `Bates HN0004512.pdf`; the row's-own-vocabulary strike trips the lecture handout.
- No thresholds, no counts, no confidence scores, no handling classes. `sensitivity` is `potentially_sensitive`.
- Files written: exactly the two assigned. No roster, canonical-fields, `check.py`, `src/`, SPEC or neighbour file was touched.

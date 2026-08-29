# Research memo — `government.policy-development`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.policy-development.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, placeholder launch
Absorbed legacy row: `gov.intergovernmental-agreement`

## Result

Accept, on two of three node-test legs, with the third leg conceded openly rather than argued into existence.

The row survives because it holds a corpus with its own recognizer and its own privacy shape: the **pre-decision appraisal corpus** of an executive or administrative body — a numbered option set including an appraised do-nothing baseline, the impact and distributional assessments and models behind it, the submission that carries a recommendation to a decision-maker, the clearance write-round, and the minute that closes the exercise. It does **not** survive on its dimension recommendation, which is empty on both sides under PR-6 and therefore identical to its schema's default. That concession is written into `template.why` and into `open_question` item (1) rather than hidden.

## The charge — the strongest case that this row should not exist

I built the prosecution before writing anything, and it is strong enough that I nearly refused.

**(a) It is a lifecycle stage.** "Policy development" names the phase before a bill, a rule or a decision exists. Lifecycle stage is an explicitly named refusal category, and the phrasing of the row's own `one_line_hint` — "the working papers by which a public body develops a policy position … and the decision that closes them" — reads as the front half of somebody else's lifecycle.

**(b) It is a work_type value, and its own schema already says so.** The `government` anchor's `work_types[0]` is, verbatim from the anchor JSON: `"policy options paper, impact assessment, briefing, consultation, response analysis, or decision record"`. That single enum value is this row's hint restated almost word for word. This is exactly the argument that killed `government.municipal-administration`, whose refusal reads: "A row whose whole increment over its schema is never-alone evidence can never clear activation; it would be a row that never fires."

**(c) It is a duplicate of its neighbours, four ways.** The consultation half is `government.public-consultation`. The appraisal-attached-to-a-proposal half is `government.regulatory-rulemaking`. The bill-briefing half is `government.legislative-record`, which has already landed a boundary against me. The governing-document half is `business_operations.policy-handbook`, which has also already landed one. Subtract all four and the sceptic's claim is that nothing remains.

**(d) It is defined by absence.** "The papers that are not yet a bill, not yet a rule, not yet a determination" is a row defined by what it lacks.

**(e) The absorbed legacy row is a document type.** `gov.intergovernmental-agreement` is, on its face, an agreement — a document type, and a never-alone one, since a memorandum of understanding exists in every sector.

## Defeating the charge

**Against (a) and (d).** A lifecycle stage of X only holds files when X exists. This corpus routinely exists where no instrument, proposal, application or proceeding was ever created — most options papers terminate in "do nothing", and the appraisal, the model, the submission and the minute that recorded that outcome are all still real, still kept, and belong to no downstream identifier. That is the decisive test and it is positive: a world that produces a complete, coherent, retained file set **with the downstream instrument absent** is a world, not a stage of another one. Conversely, this is why the row is not defined by absence — it is defined by the presence of an appraisal structure, not by the absence of a bill.

**Against (b).** The anchor's enum value names the *artefacts*; it does not carry a *recognizer* for them. Every one of the anchor's ten deterministic signals keys on an identifier that names a thing that already exists — bill identifier, proposal or consultation identifier, application or case reference, procurement reference, agenda or committee identifier, collection-round identifier, election operations, case-management export path, workflow-tied mail. None of them can fire on a corpus whose only anchor is a free-text policy question. So the increment here is not "the anchor's signal plus a token" — the failure mode that sank `municipal-administration` — it is a set of activation paths the anchor cannot express. Named concretely, and each is true of the file list: the **option set with an appraised do-nothing baseline** scored against shared criteria and closing on a preferred option; the **mandated appraisal spine** (problem under consideration → rationale for intervention → policy objective → options considered → costs and benefits → preferred option) with a sign-off and an **independent scrutiny opinion issued by a body other than the author**; the **decision-box submission** (Issue / Timing / Recommendation / Annexes, terminating in discrete responses, returned initialled); the **clearance write-round** (dated circulation to named other offices, clearance deadline, returned positions); the **model whose sheets are keyed to the same option numbers** with a QA log naming a reviewer distinct from the modeller. Provenance on all five: inference from named real document structures, not from `00`.

**Against (c).** The four neighbours each take a slice, and I authored the boundary in both directions for all four (below). What remains after the subtraction is not residue: it is the unpublished analytical spine — options, appraisal, model, submission, clearance, minute — which none of the four claims, because rulemaking's docket needs a proposal identifier, consultation's corpus is the received responses, the legislative row's unit is an instrument by coordinate, and the handbook binds one organisation's own staff.

**Against (e).** I accept this partially and surfaced it rather than smoothing it — `open_question` item (4). I absorbed `gov.intergovernmental-agreement` on the argument that a memorandum of understanding between public bodies is the negotiated *output* of exactly this appraisal corpus (a co-operation option was appraised, chosen, cleared and signed), and that its `never_alone` risk is handled by requiring **public bodies in the signature blocks** plus the co-operation-scope-and-joint-governance spine. But if Joseph reads it as machinery belonging with `government.diplomatic-consular` or `government.international-development`, the row should **shed it** rather than keep a weakly related second world. I wrote reciprocal collisions to both of those neighbours so that the seam is already argued whichever way he rules.

## The node test, leg by leg

**Leg 1 — detection signals: DIFFER.** Argued above. The schema's default cannot recognise a policy-question-anchored corpus; this row can, through five structures the anchor does not carry. It also adds `never_alone` entries the anchor does not have and could not have, because they are specific to appraisal furniture: a numbered option list alone, a cost-benefit table or NPV alone, a preferred-option statement alone, a draft watermark or status legend alone, an MoU alone. The sharpest of these is the option-list entry, because it is the one a naive implementation would get wrong — `Options Appraisal - Depot Network Consolidation - Board Paper 12.pptx` has numbered options, a do-nothing base case, appraisal criteria and a recommended option, and is a private company's.

**Leg 2 — dimensions: DO NOT DIFFER. Conceded.** PR-6 leaves `government` with no field rows; a template cannot branch on undeclared fields; the schema's default `dimension_order` is `[]` and `time_first` is false, and so are mine, character for character. I refuse to dress this up. The world's structure is recorded as prose in `template.why` for later adjudication (policy question → appraisal or submission family → work type; option number is an ordering inside a family, never a folder level; named officials never a dimension). Time is not first, on the design's own reasoning: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” — a single policy question routinely spans several years, and a year-first order would separate the options paper from the minute that answered it. Whatever is recommended stays the user's: “The system recommends an order based on the domain template, but the user can reverse, remove, add, or flatten dimensions.”

**Leg 3 — privacy rules: DIFFER, and in kind.** The schema's default protects **named-person case material and received submissions**. This corpus often contains no private individual and is still the schema's most disclosure-sensitive holding, for three structural reasons: the harm attaches to what was **not** chosen (a rejected option or an unpublished cost estimate is damaging *because* it was discarded, so member sensitivity cannot be read off member content the way a case file's can); the harm is **version-state-dependent** (an unreleased draft and its published final can be the same bytes minus a watermark, so resemblance to a government publication is never evidence that the local copy is public); and the sensitivity **decays on announcement**, which the catalogue cannot represent and must therefore not compute. None of that is expressible as the anchor's named-person rule. The node records only `potentially_sensitive`, assigns no handling class, and keeps status legends, protective markings and scrutiny ratings as literal observations.

CONNECTION.md's test is disjunctive — signals **or** dimensions **or** privacy. Two legs differ, so the node stands. If that reading is wrong, `open_question` (1) says exactly where the coverage goes instead.

## Files considered and rejected

- **`Green Paper - Future of Adult Social Care - CP 1102.pdf` downloaded for reading.** Published discussion documents are the visible tip of this corpus and the most tempting false positive of all, because the *title* matches the row perfectly. Publication by a government is not authority-side custody of its development. Routed to Reading Inbox, and covered by a `never_alone` entry.
- **`The Green Book - appraisal guidance.pdf` (an appraisal manual).** It teaches the option-set method and therefore contains every deterministic phrase this row keys on, as instruction rather than as instance. Reading Inbox.
- **`Impact Assessment - CRM Migration.docx`.** A corporate project's impact assessment. Trips the title, misses the spine and the authority-side role.
- **`Remote Working Policy v3.docx`.** Written into the JSON as a fixture precisely because it is the file that proves the word *Policy* is never-alone evidence — including when the employer is a public body, since employer role is not authority-side function. Goes to `business_operations.policy-handbook`.
- **A minister's or official's diary and contact export.** Rejected: appearing in a policy-team address book is never-alone evidence; the anchor already forbids activating on a public-office name.
- **A departmental HR, finance or estates record.** Public-body internal administration is not authority-side policy work.
- **A think tank's or consultancy's report commissioned by the department.** Kept only when a commissioning statement or terms-of-reference reference ties it to a live question; otherwise Review Later. Named in `needs_llm`.
- **A live document-management or case-management system.** A source system, not a file node. Only a bounded export with a readable manifest is represented, and it is not unpacked to strengthen recognition.
- **A practice taxonomy of policy areas** (health, transport, tax, education). Deliberately not enumerated. That would rebuild the 574 inside one row and is the failure J-IND forbids.
- **Post-implementation reviews of an operating grant scheme.** Ceded to `government.grant-programme-administration` where they carry that programme's own reference.

## The collision fixture

`Regulatory Impact Analysis - Proposed Rule RIN 1234-AB56.pdf`. It has the mandated spine, the alternatives-including-no-action set, the quantified costs and benefits and the preferred alternative — every deterministic structure this row keys on, in order. It is not this row's evidence. **What discriminates it:** the front matter binds it to a rulemaking identifier and it is held as a supporting document inside a proposal docket. Identifier and custody beat structure. Stated reciprocally in the JSON: an appraisal whose only anchor is a workstream label is this row's *even if a rule later emerges*, and an appraisal bound to a docket is rulemaking's *even though it is the same document genre*.

A second, harder collision is `Options Appraisal - Depot Network Consolidation - Board Paper 12.pptx`, because it defeats the do-nothing-baseline discriminator on its own. What discriminates it is the **appraisal criteria and the approver**: payback, NPV and board approval versus public value, statutory objective, distributional effect, officer or ministerial sign-off, and an independent scrutiny opinion.

## Reciprocal boundaries

Nine collisions, each stated in both directions, and where a neighbour has already landed I adopted its wording rather than inventing a competing one.

- **`government.legislative-record`** — already argued against me from its side, naming `Government response to the Committee's Third Report - CP 1194.pdf`. I adopted that fixture and that split verbatim in substance: my side owns the departmental product, its side owns the same response held inside the proceedings as a reply to numbered recommendations, and drafting instructions follow the drafting or clerk's office.
- **`business_operations.policy-handbook`** — already argued against me from its side (consultation / legislative or rulemaking anchor / external audience versus a document binding one organisation's own people). Adopted, and strengthened from my side with a positive discriminator that row does not have: a handbook has no option set and no baseline. Shared fixture: `Remote Working Policy v3.docx`.
- **`government.regulatory-rulemaking`** — the RIA fixture, both directions, as above.
- **`government.public-consultation`** — split by producer. Its side owns the call and the received responses keyed to a consultation identifier; mine owns the authority's own coding frame and response analysis. Shared fixture: `Consultation Response Analysis - coding frame and theme counts.xlsx`. Reciprocal statement: a response bundle with no authority-side analysis is never mine, and an options paper revised after a consultation is never its.
- **`business_operations.board-governance`** — the depot fixture, both directions.
- **`government.diplomatic-consular`** — MoU versus treaty. Public-body signature blocks plus a non-binding clause keep it here; a head-of-state signature or a treaty-series number moves it.
- **`government.international-development`** — a funded-programme spine (disbursement schedule, results framework, implementing partner, reporting cycle) moves it there; pure co-operation scope with a joint committee keeps it here. Reciprocal: I do not claim an arrangement merely because both parties are public.
- **`nonprofit.advocacy-campaign`** — an external body's paper imitating a ministerial submission is a submission *into* government, not government's own appraisal. Reciprocal: my options paper is not its merely because a campaign is named in it.
- **`government.grant-programme-administration`** — scheme design appraisal is mine, the operating scheme's call/applications/awards/monitoring are its.

Neighbours considered and **not** given an edge: `government.constituent-casework` and `government.public-records-foi` (a policy paper caught in a disclosure schedule is a member of the request workflow, not a rival claim on the same bytes); `government.public-procurement` (a procured evaluation study is procurement's on the buyer-side spine, and this is already covered by the grant-programme boundary's logic); `government.planning-application` and `government.permit-licensing` (determination-side, keyed to case references, no shared evidence); `research.reading-library` (published policy documents fall to Reading Inbox by residual, which is the correct mechanism, not a mutex); `career.consulting-client-engagement` (a consultancy's engagement letter for policy work is Career's on the prepared-for / prepared-by spine, and the substantive overlap is already carried by the board-governance and advocacy collisions).

`also_holds_with` is empty and `role_split` is empty for the same reason the landed `legal.practice-matter-file` left them empty: a template cannot author schema-level coactivation, and a fieldless schema exposes no role field to split. Genuine coactivation is recorded per fixture in `also_schema` — `legal` for the statutory-duty annex and the signed arrangement, `photos` for the screen capture.

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false` — all intentional under PR-6 and D1's standing deferral. Candidates considered and **not** minted: a policy question or workstream key (the one field this world genuinely wants, deferred to `open_question` (5)); option number and draft stage (rejected as fields — they are orderings on the universal **version family** relation, which `00` already lists among the universal facts: "file type, creation date, language, duplicate family, version family, and sensitivity status"); a release-state key (deferred, `open_question` (3)); `purpose` (canonically scoped to College Applications); `institution`, `record_type`, `project`, `artifact_type` (scoped to Finance, Research and Code). Every fixture's `facts_legal` is therefore the universal set only.

## NEEDS-JOSEPH

1. **Is the node test disjunctive?** This row differs on signals and privacy but concedes dimensions. If all three legs are required, refuse it and redistribute to `government.regulatory-rulemaking`, `government.public-consultation`, `government.legislative-record` and `business_operations.policy-handbook`.
2. **May P9 group on a free-text anchor?** Every other government sibling anchors on an identifier. This one anchors on a policy question. If free-text anchoring is disallowed, terminated policy work becomes permanently ungroupable, which is precisely the material the row exists to hold.
3. **Release state has no representation.** Literal observation only (this row's assumption), a universal fact alongside version family, or a P7 concern?
4. **Does `gov.intergovernmental-agreement` belong here?** Absorbed on an output-of-this-corpus argument; both alternative homes already have reciprocal collisions written, so the row can shed it cleanly.
5. **If PR-6 lifts,** decide whether a policy question or workstream may be a `government` field and whether it is destination-eligible. This row proposes none.

## Recommendations to R1c (no cross-row edits made)

- Add the reciprocal of my consultation boundary to `government.public-consultation` when it lands, naming `Consultation Response Analysis - coding frame and theme counts.xlsx` on both sides.
- Add the reciprocal of my RIA boundary to `government.regulatory-rulemaking`, naming `Regulatory Impact Analysis - Proposed Rule RIN 1234-AB56.pdf` on both sides.
- `government.legislative-record` and `business_operations.policy-handbook` already carry their halves; no change needed there.

## Self-verification

`python3 -m json.tool` passes. Key set is identical to `government.legislative-record.json` (checked programmatically: no missing, no extra keys). All nine `collides_with` ids confirmed present in `planning/domains/roster.json`. All five `falls_through_to` names are `00` §7.3 residuals with grep-verified design cites. Every quoted span was grep-verified verbatim against `planning/00-database-agent-product-design.md` before use. Every `file_examples.source_type` is in `SOURCE_TYPES`. No thresholds, no handling classes, no folder paths as facts, no fields minted. Only the two assigned files were written.

# Research memo — `government.school-district-administration`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.school-district-administration.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, `launch: placeholder`

## Result

Accept the node. Its distinct job is to recognize the **administering tier over a set of schools** — the district, school board, local education authority or education-ministry office that runs admissions, statutory returns, funding allocation, cross-school staffing, school-organisation planning and improvement for institutions it does not itself teach in — and to keep the resulting material protected by default because its ordinary operative artifact is a named-minor record at population scale.

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false`. PR-6 leaves the government schema fieldless; a template cannot branch on undeclared fields. The row's value is entirely in recognition, privacy posture, grouping anchors, reciprocal boundaries and residual routing.

## THE CHARGE — the strongest case that this row should not exist

Stated before any evidence was gathered in the row's favour, then answered.

**Charge 1 — it is an organisation name, and organisation names are never-alone evidence.** "School district" is a kind of organisation. A district letterhead, a `.k12` domain, a superintendent's signature block and a school name are all exactly the evidence `00` forbids as sole proof. A row whose only evidence is an organisation name can never activate, and the brief says so.

*Answer: conceded on the evidence, defeated on the definition.* The row is not defined by whose name is on the paper; it is defined by a structural shape — an operative record whose repeated row key is an **institution identifier** and whose scope is **many institutions under one body**. A funding allocation statement with one row per school, a place-allocation round spanning many allocated school codes, a certification tracker with an assigned-school column spanning several sites: none of these can be produced by an entity that is not administering a set of schools, and none of them is produced by a school about itself. The district's name is the weakest signal in the row and is written into `never_alone` for that reason; the multi-institution row key is the strongest and is deterministic.

**Charge 2 — it is a duplicate of `government.education-institution-governance`.** Both hold admissions data, enrolment returns, funding records, staffing files and inspection correspondence. Two rows over the same document types is exactly the 574's failure mode.

*Answer: defeated, and the neighbour agrees.* `government.education-institution-governance.json` already authored the seam against this id, unprompted, in its own `collides_with`: "The deciding evidence is the administrative tier: a district, board, ministry or local education authority administering many institutions it does not itself teach in, versus one institution administering itself under its own governing instrument. Same fixture both ways — an enrolment census by programme and mode: held by the district office as one school's row inside a multi-school aggregation it belongs to that row; produced by the institution's own registry about its own registered students it belongs here." A landed neighbour independently naming the same fixture and the same discriminator, in both directions, is the strongest available evidence that the seam is real rather than invented to save an id. I have mirrored it verbatim in intent and named the same fixture on my side.

**Charge 3 — it is a lifecycle stage or sub-function of `government.municipal-administration`.** A school board is a local public body; its agendas, budgets, capital programmes and public notices are municipal artifacts. Folding education into local government would lose nothing.

*Answer: defeated by a fixture municipal administration cannot produce.* A statutory pupil census return addressed **upward** from the authority to a state, provincial or national education department, with a collection reference, per-school response rows and an officer sign-off, is an education-specific reporting line that a general-purpose municipality does not sit inside. So is a per-school funding formula allocation statement. In many jurisdictions the school board is separately elected and fiscally independent of the municipality; where a combined municipality has an internal education directorate, the JSON routes by the directorate evidence rather than the corporate name, and abstains where neither is evidenced. The boundary is written reciprocally.

**Charge 4 — it is a work_type value on the `government` schema, not a node.** This is the sharpest charge, because it is literally true in the anchor. `government.json`'s `work_types[]` already contains: "public education, accreditation, cultural-service, museum, library, archive, or records-management administration where the body sits inside the state". My entire row is one clause inside one enum value.

*Answer: defeated on two grounds.* First, a work_type value cannot carry a different **privacy default** or a different **recommended dimension**, and this row carries both (below). Values are what a field can hold; they cannot change the posture of the schema that holds them. Second, R1a has already split that single enum clause into four separate rows on the roster — `government.library-administration`, `government.education-accreditation`, `government.education-institution-governance` and this one — and three of the four have landed as accepted nodes with mutually reciprocal boundaries. Consistency requires either that the district tier is also a row, or that all four collapse back into the anchor. Collapsing them would destroy four already-argued seams. This is an argued inference, not a design cite.

**Charge 5 — it is defined by the absence of something** ("not a single school", "not a household"). A row defined by a negation cannot activate.

*Answer: defeated.* The activation conditions in `recognition.deterministic` are all positive and structural: the multi-institution row key, the upward statutory return with sign-off, the allocation round with an offer date and ranked preferences, the issuer→school direction of an improvement notice, the cross-school assigned-school column. The negations appear only in `never_alone`, where they belong.

**Charge 6 — it is a document type or a file format.** Answered by the file set: the row spans spreadsheets, prose reports, notices, email, calendar, screenshots, an encrypted archive and a published PDF, and two of those fixtures are explicitly *not* this row. No extension or source_type appears as a discriminator anywhere in the node.

**Verdict: accept.** `refuse_node: false`.

## The node test, three legs, argued

CONNECTION.md §2: a template row exists only when its detection signals, recommended dimensions, or privacy rules differ from its schema's default. I read `government.json`'s default and argue each leg separately. All three differ; any one would have sufficed.

**Leg 1 — detection signals differ.** The government default's deterministic signals are organized around a **bounded proceeding or instrument**: an official bill identifier repeated across a bill packet, a rulemaking docket, a permit case, an information request, an election operation. Its unit of account is one proceeding. This row's unit of account is a **set of institutions**, and its discriminating shape is an operative table whose repeated key is an institution identifier — a shape the anchor never describes and could not, because most public functions have no institutional estate underneath them. The second row-specific signal, the upward statutory return with a census date and an officer declaration, is likewise absent from the anchor: the anchor's statistics clause covers a body producing official statistics about a population, not a body *responding* to a collection about its own estate. The third, the issuer→recipient direction of an intervention notice where both parties are public education bodies, has no analogue in a schema whose regulator clause assumes a private regulated party.

**Leg 2 — recommended dimensions differ.** The anchor's prose order is: authority-side function or bounded proceeding/case/programme first, then an exact reference or cycle, then work type. That order is unintelligible here. A per-school allocation line, an improvement notice or an attendance return is meaningless without knowing **which school** — and `00` says "a parent dimension should provide the context required to understand the child." This row therefore needs an **institution** dimension inserted between function and cycle, which the anchor's order does not contain and which no other government child needs (a bill has no institution, a permit case has no institution). Under PR-6 the serialized `dimension_order` stays empty and the difference lives in `template.why` as prose. That is a real recommendation difference, deferred in serialization only. Time stays non-first for the anchor's reason — "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders" — and additionally because the cycles here are school years, admissions rounds and census points, not calendar years.

**Leg 3 — privacy rules differ.** The anchor's posture is "public availability is not the schema default", with citizen casework as one protected slice among legislative, statistical, procurement and election material. This row inverts the ratio: the *ordinary* artifact is a named-minor record at population scale — pupil censuses, allocations carrying home addresses and distance measures, attendance and exclusion returns, meal-eligibility flags, special-education caseloads, safeguarding chronologies. Two rules follow that the anchor does not state: (a) a published performance table, board minute or allocation statement in the same folder must never lower the posture of the underlying per-pupil extract; (b) small per-school counts remain disclosive even where the published district aggregate is not, so a per-school breakdown is not treated as "already public" because a national release exists. Both are enforced under "Privacy policy must be enforced before content reaches any model or external connector" and "Protected material should not be included in cloud-model prompts by default, should not display raw content in general group summaries, and should not be moved automatically without a user policy that explicitly permits it."

## Files considered and rejected

Named tempting false positives, and why each is not this row's evidence.

- **`School Performance Tables 2025 - District 12.pdf`** — the primary collision fixture; see below.
- **`Report Card - Jordan Lee - Spring 2026.pdf`** — carries a school name, a district crest, a term, a pupil and grades. It is the household's schooling record (`academic.k12-schooling`). It has no operative slot, no addressee authority, no aggregation. The district issued it; the household holds it, and `never_alone` says the issuer never crosses that seam.
- **`IEP - Jordan Lee - Annual Review 2026.pdf`** — kept in the file set precisely as a false friend with a real crossing condition. Alone it is `academic.iep-accommodation-plans`; only an authority caseload roster, an assessment or case reference and neighbouring cases move it here.
- **A teacher's `Lesson Plans - Year 4 - Autumn.docx`, gradebook and observation feedback** — `academic.teaching`. A district employer name on a teacher's file is employment evidence. Rejected.
- **`Teaching Certificate - Elementary K-6.pdf` held by the teacher** — `career.credentials-licenses`. The same certification appears here only as a row inside a district-scale tracker.
- **A vendor's `Proposal - School Bus Services - Northgate Transit.pdf`** — the seller's copy. Counterparty value does not activate the schema; the anchor's `never_alone` already forbids it. The *buyer-side* evaluation report is in the set and coactivates procurement.
- **A parent-teacher association's fundraiser accounts, and a school's own booster-club records** — `nonprofit.governance` / `nonprofit.fundraising-donor`. Neither body administers a set of schools.
- **A charter or academy management organisation's cross-school operations pack** — genuinely ambiguous and deliberately *not* claimed; it is NEEDS-JOSEPH item 2. The private-group case may not be a public authority at all, and guessing would import a jurisdiction rule the catalogue must not hold.
- **Published education-policy papers, ministry consultations, union research reports, education-spending comparisons** — Reading Inbox. Publication by an education authority is not authority-side custody.
- **A live student information system, admissions portal or finance system** — a source system, not a file node. Only a bounded export with a readable manifest is represented, and it is kept shallow.
- **Contacts exports containing head teachers, governors, clerks and case officers** — a name list is never-alone evidence in both the anchor and this row. `contacts` stays in `file_kinds` because an authority contact export can be a group member, never an activator.
- **School-year, term, key-stage and grade-level taxonomies; per-jurisdiction return names; funding-formula factor catalogues** — deferred. Enumerating them would turn a placeholder into the industry-depth catalogue J-IND defers, and they are values, not nodes.

## The collision fixture

**`School Performance Tables 2025 - District 12.pdf`.** It is per-school, district-scoped, education-administrative in every word, and carries a table whose repeated key is an institution identifier — the exact deterministic shape this row is built on. It is not this row's evidence.

What discriminates it: **the absence of an operative slot in a file that would require one.** An authority-side per-school table always carries at least one of an addressee or issuing block, a sign-off or declaration, a version marker distinguishing indicative from final, a collection or allocation reference, or a decision line. A published statistics table carries instead a release date, a national source attribution and a statistics-release footer, and nothing that anyone acts on. A parent comparing schools, a journalist and a researcher all hold this file, and so does the district — and even in the district's hands it is a downloaded output about itself, not a record of its own administration. It routes to Reading Inbox. This is the discriminator the row would most easily get wrong, because the multi-institution row key is otherwise its strongest positive signal; the deterministic clause is worded to require the row key **plus** an addressee or issuing block for exactly this reason.

## Reciprocal boundaries

Seven mutex collisions, each stating both directions and naming the same fixture on both sides. Two are mirrors of boundaries a landed neighbour already authored against this id.

1. `government.education-institution-governance` — administering tier. Fixture both ways: an enrolment/roll census. Mirror of the neighbour's own text.
2. `government.education-accreditation` — the neighbour authored it first: "A district's evaluation of a school it operates is administration of its own system, not external accreditation." Fixture both ways: a rated visit report on Northgate Primary. External standards edition and outside-the-line-of-management reviewer → accreditation; own-system improvement cycle → here.
3. `government.municipal-administration` — general local estate vs education-specific remit, statutory education reporting line and funding formula. Fixture both ways: a governing-body agenda packet with per-site capital items.
4. `academic.k12-schooling` — issuer vs household holder. Fixture both ways: an admissions offer letter naming one child and one school.
5. `academic.iep-accommodation-plans` — family's plan vs authority caseload. Fixture both ways: `IEP - Jordan Lee - Annual Review 2026.pdf`.
6. `business_operations.board-governance` — corporate/charity board vs public education board with statutory open-meeting structure and decisions about institutions it does not run. Fixture both ways: an agenda packet with a consent calendar and closed session.
7. `nonprofit.trade-union` — one document, two holders. Fixture both ways: `Collective Agreement - District 12 and Teachers Association 2026-2029.pdf`. Union-side membership, mandate and ratification-ballot material vs employer-side staffing, deployment and cross-school payroll administration.

Two `also_holds_with`: `business_operations.procurement-sourcing` (a transport or catering tender is legitimately both) and `career.employer-side-hiring` (a district teacher recruitment campaign is legitimately both). These are coactivations, not mutexes — `00`'s abstract-that-is-also-an-application-document case.

`role_split` is empty. The pattern would fit the district-employer / union-member seam exactly, but `role_split` points at neighbours holding *different field keys*, and the government schema declares none. `legal.practice-matter-file` left it empty for the same fieldless reason. Recorded as a recommendation for R1c if PR-6 is lifted.

Neighbours considered and deliberately **not** given an edge: `government.library-administration` (a school library service overlaps only where a library is the administered unit; its research file mentions this id, but no same-evidence mutex survives — the district's fixtures are pupil- and school-keyed, the library row's are collection- and lending-keyed); `finance.small-business-bookkeeping` (a district general ledger is public finance, not small-business bookkeeping); `business_operations.contract-administration` (already covered through the procurement coactivation; adding it would duplicate one seam); `nonprofit.governance` (PTAs and booster clubs fail the administering-tier precondition outright, so there is no confusable fixture); `identity.core-documents` (a proof-of-address or birth certificate submitted with an admissions application is an independent coactivation on the *applicant's* side, not a mutex here).

## `proposed_fields` justification

Empty, deliberately. Candidates were considered and rejected:

- `institution` / `school` — the one concept this row would most want as a dimension. `government` declares no fields, and minting an education-specific key in a template is exactly what the brief forbids. It is NEEDS-JOSEPH item 1 instead.
- `school` exists in `canonical_fields.json` scoped to academic coursework; reusing it here would silently re-scope a canonical key from "the school the learner attends" to "the school the authority administers". Those are different referents on the same word, and quietly merging them would corrupt the academic rows. Flagged for R1c rather than proposed.
- `work_type` — the row's `work_types[]` are values, and the field would have to be declared by the schema, not by a child.
- `record_type`, `institution`, `purpose` — scoped to Finance and College Applications under the current canonical record.
- `cycle`, `round`, `census_date`, `allocation_reference`, `case_reference` — none canonical, none minted here.

## Grouping without copied facts

Candidate groups are bounded by exact anchors: a round or offer-date reference, a collection or census reference, an allocation reference, a notice or case reference, a meeting date with numbered papers, or an export manifest. Membership never creates a school, pupil, cycle, date or outcome fact on a member. `RE Place appeal Ref A-2026-0417 - hearing arrangements.eml` and the admissions-portal screenshot are marked `group_without_copying_facts: true` for this reason: the exact reference supports a reviewable candidate edge without writing the appeal onto the mail, and the screenshot may join a neighbourhood without the row activating from its filename. An archive manifest is read; the archive is not unpacked to strengthen recognition. No cross-person or cross-family semantic joining is permitted in either direction.

## Sources used

`planning/domains/dispatch/RESEARCH-BRIEF.md`; the stamped assignment from `make_prompt.py`; `planning/domains/nodes/legal.practice-matter-file.research.md` as the depth calibrator; `planning/domains/nodes/government.json` (the schema anchor — its default template, `never_alone`, `needs_llm`, `work_types`, `grouping_reasons`, residuals and sensitivity clause, read directly); the `collides_with` entries naming this id in `government.education-institution-governance.json` and `government.education-accreditation.json`; `planning/domains/roster.json` for every neighbour id used; and eight targeted verbatim greps of `planning/00-database-agent-product-design.md`. No external web research was performed; every artifact shape in the file set is a document type I can name from ordinary education-administration practice, and each is marked as observation rather than as a design cite. `provenance: "inference"` records that this row extends the named `government` schema rather than quoting a design clause that describes it.

## NEEDS-JOSEPH

1. **Institution as a destination dimension.** If PR-6 is lifted, decide whether an institution concept may be destination-eligible here. It is the only dimension that makes an allocation line or an improvement notice intelligible, and `00`'s parent-context rule argues for it. Against: a visible school branch under an authority folder can itself disclose which school a case or family concerns, the same disclosure risk `legal.practice-matter-file` raised for client-named branches. Alternatives: (a) allow it, (b) forbid it and keep function→cycle only, (c) allow it with redacted display labels and local-only aliases.
2. **Boundary of "authority".** Decide where a single-school authority, a charter or academy management organisation, and a combined municipality with an education directorate belong: this row, `government.education-institution-governance`, or explicit abstain. The JSON currently abstains on the single-school district and routes the combined municipality by directorate evidence. This is the row's largest unresolved edge and it is jurisdiction-shaped, which is precisely why the catalogue should not guess.
3. **`school` key collision.** `school` exists as a canonical key scoped to academic coursework. Decide whether the administered-institution referent may reuse it, must have a distinct key, or must wait. This row minted nothing and recommends R1c adjudicate centrally rather than per-row.
4. **Small-cell disclosure.** Decide whether "a published aggregate exists" may ever lower the posture of a per-school or per-pupil breakdown. This row says no. The alternative — treating anything with a published counterpart as low-risk — would be simpler but would expose disclosive small counts, and no threshold may be written into the catalogue in any case.

## Self-verification

JSON parses (`python3 -m json.tool`). All eight `00` spans in quote marks grep back verbatim with `grep -c -F`, each returning exactly 1. Key set matches the landed sibling shape from the stamped contract. Every `file_examples.source_type` is in `SOURCE_TYPES`. Every edge id is on `planning/domains/roster.json`; every `falls_through_to` name is one of `00`'s residual homes. `fields`, `proposed_fields` and `dimension_order` are empty; no field key was minted. No thresholds, no handling classes, no confidence scores, no folder paths as facts. At least one `never_alone` clause is true of the collision fixture (the school-identifier clause and the published-table clause both trip `School Performance Tables 2025 - District 12.pdf`). Only the two assigned files were written.

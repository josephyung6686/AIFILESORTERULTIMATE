# Research memo — `government.education-institution-governance`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.education-institution-governance.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, placeholder launch

## Result

Accept the node, **narrowed**, and record the narrowing as a live open question rather than a resolved one.

The row survives as *the institution's own side of running itself as an academic body*. Its non-negotiable discriminator is an **academic-cycle administrative anchor held on the producing institution's own side** — academic year plus a programme identifier, module code, cohort, assessment-board session, conferral round, collection round, or committee-and-meeting reference — together with a governing instrument that gives an academic body (senate, academic board) authority separate from the corporate board. The parts of the one_line_hint that are pure board-and-policy shape do **not** belong here on their own; without the academic anchor they are `business_operations.board-governance` and `business_operations.policy-handbook`.

I did not refuse, but I came close, and the charge below is why the row is narrow.

## The charge — the strongest case that this row should not exist

I state it before the defence, at full strength.

**1. It is a work_type value of its own schema.** The `government` anchor already enumerates, verbatim in its `work_types`, "public education, accreditation, cultural-service, museum, library, archive, or records-management administration where the body sits inside the state". Under the ratified rule that work types are values of a field and never nodes, this row reads as one enum member promoted to a template.

**2. Its only added token is an organisation name — never-alone evidence.** Strip "education" from the one_line_hint and what remains is "governing-body business, statutes and policy, registry operations, quality assurance and institutional reporting", which is exactly `business_operations.board-governance` + `business_operations.policy-handbook` + `business_operations.corporate-regulatory-filings` + `business_operations.compliance-audit`. The differentiating token is the *sector of the organisation*, and the `government` anchor's own `never_alone` list already refuses that shape, naming a "public school" among entities that may be "issuer, counterparty, subject, employer, cited authority, research venue, or service provider".

**3. It duplicates two landed government siblings.** `government.school-district-administration` covers "admissions, statutory returns, funding allocation, staffing, inspection and school performance". `government.education-accreditation` covers institutional and programme review. Between them they already hold the statutory-return, admissions and quality-review artifacts. A node whose contents are the union of two neighbours plus a tier distinction is a scale difference, not a filing world.

**4. Its schema is arguably wrong, which would make it a duplicate of a *third* neighbour.** The `government` schema demands an evidenced public authority. Most institutions that have a governing body, statutes and a registry are not public authorities — independent schools, private colleges, charitable university foundations. Those are `nonprofit.governance`. If the row's real coverage is "any educational institution", the row is mostly a copy of `nonprofit.governance`; if it is only "publicly constituted educational institutions", the row is a thin slice already reachable from `government.school-district-administration` and the government default.

**5. Registry operations may be a duplicate of `academic.transcripts-credentials`.** Transcripts, results and award records already have a home on a schema with real fields (`school`, `term`, `subject`, `instructor`, `work_type`) — richer than this fieldless one.

### The defence

Points 1, 2 and 5 fail. Points 3 and 4 succeed partially, and the node is narrowed to survive them.

**Against 1 (work_type).** A work_type is a value the *same* detection signals produce. These detection signals are not the schema's. The `government` anchor's deterministic list is entirely proceeding-shaped: a bill identifier, a rulemaking or consultation identifier, an application or case reference, a procurement notice with a bid-receipt register, a collection round, an election ballot account, a records-request reference. Not one of those fires on `Programme Specification - MSc Data Science - validated 2026 - conditions.docx`, on `External Examiner Report 2025-26 - Law - and School response.pdf`, or on `Assessment Board - BSc Computer Science - June 2026 - ratified results.xlsx`. Conversely the signals I authored — programme validation with credit values and conditions, an external-examiner-report-plus-institutional-response pair, an assessment board's ratified schedule, a census-date headcount, a conferral round — do not fire on any of the anchor's own sixteen fixtures. Two disjoint signal sets is the node test's first leg passing, not a value.

**Against 2 (organisation name).** I agree that the sector name is never-alone, and I encoded that: the JSON refuses a university, college, school, faculty, campus or academy name, crest, seal, letterhead, institutional mail domain, portal URL, and the whole academic vocabulary set including *registrar* and *senate*. What activates is not the sector but a **structure**: a two-tier constitution in which corporate authority and academic authority are held by different bodies under one governing instrument. No company, charity, union or standards body has that shape. `nonprofit.governance` describes a single governing document and a single trustee board; a validation panel, an external examiner, an assessment board and a conferral round have no analogue there.

**Against 5 (transcripts).** The bytes collide, the roles do not. `academic.transcripts-credentials` is the *named person's own* record: one subject, held by that subject, with `school` and `term` legal as facts. This row is the *producing registry's* workflow: many subjects at once, keyed by an award round or a verification request, with no field legal at all. The privacy shapes are opposite — one document about oneself versus a cohort spreadsheet of other people. I authored that boundary reciprocally with the same fixture (`Official Transcript - J Yung - issued 2019.pdf`) named on both sides.

**Partly conceding 3 (sibling duplication).** The tier boundary is real but thin, and I narrowed the row rather than assert it away. A district aggregating many schools' returns is not the same actor as one institution returning its own; but a single school's row inside a district aggregation and that school's own census extract can be byte-identical. I named the enrolment census as the shared fixture on both sides of the `government.school-district-administration` edge, and pushed the unresolvable case to Review Later rather than to a guess. Against `government.education-accreditation` the seam is authorship, not content, and I named the self-evaluation document on both sides — including a fixture (`Self-Evaluation Document - Example College - received for review 2026.pdf`) that is deliberately *not* this row's evidence.

**Conceding 4 (schema mismatch) — this is NJ-1 and I did not smooth it.** I could not settle it from the design docs. `00` says nothing about which educational institutions are public bodies, and the `government` anchor's own open question already asks "whether public-authority status comes only from deployment-specific gazetteers or may be user-confirmed for hybrid and quasi-public bodies" — the identical difficulty, unresolved upstream. My pass narrows to publicly constituted institutions and abstains to `nonprofit.governance` otherwise. That abstention may be wide enough to hollow the row out, which is exactly why it goes to Joseph rather than into a confident sentence.

## Node test, three legs, argued

**Leg 1 — detection signals differ from the schema's default template.** Yes, and disjointly, as argued above. The government default keys on proceeding, case and collection identifiers held in an authority-side role. This template keys on an academic-cycle object — programme, module, cohort, board session, conferral round, academic year — plus institution-side production. A second, structural signal is unique to it: the corporate/academic two-tier split. The `needs_llm` set is also different in kind; the default's hard judgement is *is this a public authority or a contractor*, while this row's hard judgements are *which administrative tier* and *reviewer or reviewed*, neither of which the default describes.

**Leg 2 — recommended dimensions differ.** Both orders are empty on the page, because PR-6 leaves the schema fieldless and a template cannot branch on undeclared fields. But the *prose* latent orders differ and I recorded both. The default's is "authority-side function or bounded proceeding/case/programme first, then an exact reference or cycle, then work type". This row's is institution, then governing function or bounded academic object, then **academic year or cycle**, then work type. The academic year is a real recurring dimension with no counterpart in the default, and it is deliberately *not* first, because `00` says "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders" — putting the year first would split one programme's validation-to-revalidation record and one committee's continuous business. I note honestly that an empty `dimension_order` makes this leg argumentative rather than demonstrable, and that R1c should treat leg 1 and leg 3 as the load-bearing ones.

**Leg 3 — privacy rules differ.** Yes, and this is the strongest leg. The government default's protective posture is built around *casework*: one named person per case, plus unsuccessful bids, evaluator declarations and restricted statistics. This row's characteristic artifact is a **mass named-person education record** — one spreadsheet whose rows are an entire cohort with marks, classifications, progression outcomes, fee status and mitigating-circumstances flags; one conferral list of every graduand; one records-system export of five years of registrations. `00` names the category directly in its privacy paragraph: the corpus "can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and **educational records**". At school level the subjects may be minors. That produces a rule the default does not state: no named student or staff member may become a folder level or a display label, and a cohort file's sensitivity is not lowered by the fact that a ceremony programme or a published statistics table derived from it is public.

Three legs, three separate arguments, two of them decisive. The node stands.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md`, in full.
- The stamped assignment from `make_prompt.py`, in full.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — the depth calibrator named in the brief. I followed its precedent on two structural points: `role_split: []` and `also_holds_with: []` are correct for a fieldless schema, and per-fixture `also_schema` carries coactivation instead.
- `planning/domains/nodes/government.json` — the schema anchor, read for its full recognition, work_types, grouping_reasons, template prose, edges, sensitivity and open question. It is my measured-against default template.
- `planning/domains/roster.json` — confirmed my id, kind, schema, and every neighbour id I used.
- `planning/00-database-agent-product-design.md` — reached by targeted grep only, per the token rule. Every quotation below was grep-verified verbatim before use.

### Quotations verified against `00`

All six spans I used grep back out of `planning/00-database-agent-product-design.md` verbatim:

- "treat the file extension as a routing signal rather than an assumption about meaning" (line 35)
- "A session should never be treated as proof of topic" (line 45)
- "the system must not mistake the absence of EXIF for proof that an image is a screenshot" (line 32)
- "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." / "The system recommends an order based on the domain template, but the user can reverse, remove, add, or flatten dimensions." (line 95)
- the residual definitions for Independent Records, Reading Inbox, Review Later, Unsupported or Encrypted, Protected Records (line 120)
- "Privacy policy must be enforced before content reaches any model or external connector." and the educational-records list (line 177); "Protected material should not be included in cloud-model prompts by default, should not display raw content in general group summaries, and should not be moved automatically without a user policy that explicitly permits it." (line 185)

No quotation is attributed to `00` that is not on that list. No threshold, count or score appears anywhere in the node.

## The collision fixture

`Board of Governors - Minutes - 9 February 2026.pdf`, collected as one of forty near-identical packs from many named institutions, sitting beside a coding frame, an interview schedule and a literature matrix.

Every surface signal this row could want is present: an institution block, a governing body, a meeting date, numbered papers, attendance, resolutions. It is not this row's evidence. What discriminates it is **role plus corpus shape**: the holder has no employment, enrolment or governance relationship with any institution in the set, and the set spans many institutions rather than repeating one. Governance vocabulary is topic here, not custody. It routes to Reading Inbox with `also_schema: research`, and the JSON marks `group_without_copying_facts: false` because there is no legitimate governance group to join.

A second collision fixture is carried deliberately for the accreditation seam: `Self-Evaluation Document - Example College - received for review 2026.pdf` is byte-shaped exactly like the institution-authored self-study, and belongs to `government.education-accreditation` because a transmittal, a review reference, reviewer annotations and a panel worksheet place custody on the reviewer's side.

## Files considered and rejected

Named false positives, and why each is not this row's evidence.

1. **`Official Transcript - J Yung - issued 2019.pdf`** — registrar language, seal, verification code. Rejected: the holder is the subject. Registrar language proves who *issued* it, never who *holds* it. → `academic.transcripts-credentials`.
2. **`Enrolment Confirmation Letter 2025-26.pdf`, `Tuition Invoice - Semester 1.pdf`, student-card scans** — issued by the registry, held by the student. Rejected for the same reason; they land in `academic`, `finance` or Protected Records.
3. **`BUSIB 4300 - Module Gradebook - Spring 2026.xlsx`** — student names, module code, mark columns. Rejected: one instructor, one module, no board apparatus. The presence of an assessment-board session reference, a moderation sheet and an external examiner report is what moves the same shape here. → `academic.teaching`.
4. **`Syllabus BUSIB 4300 Spring 2026.pdf`** — the prompt's own canonical example. Rejected outright: a course-code token with academic context evidences a *course*, which is Academic's world with `school`, `term`, `subject` and `instructor` legal. Nothing about running an institution.
5. **`University of Example - Prospectus 2027.pdf`, published inspection reports, league tables, annual reports** — institutional publications. Rejected: "publication by government is not authority-side custody", as the anchor's own never_alone puts it; the same logic applies to institutions. → Reading Inbox.
6. **`Contract of Employment - Lecturer - University of Example.pdf`, a university payslip, a university job advert** — an institution as employer. Rejected: employer identity is never-alone; → `career.employment-records` / `hr.*`.
7. **`Ethics Application - HREC 2026-118.pdf`, a grant application submitted through an institution's research office** — a research venue, not an administered institution. Rejected; → `research`.
8. **`Student Union AGM Minutes 2026.pdf`** — governance furniture, campus setting. Rejected: a member association is not the institution. → `nonprofit.member-association`.
9. **`Campus Estates Masterplan - Phase 2.pdf`, a capital works contract** — held by the institution, genuinely institutional business. Rejected here because the artifacts are construction and facilities in shape with no academic anchor; → `construction_property` / `business_operations.facilities-workplace`.
10. **`Audit Committee - papers - 26-02.pdf` (investments and estates only)** — the hardest rejection. It is a university committee under the university's instrument, but nothing on the page is academic. The JSON routes this case to Review Later rather than claiming it, because claiming it would re-open the "sector name activates" failure the charge identified.
11. **A live student-records system, a virtual learning environment, or an institutional mail account** — a source system, not a file node. Only a bounded export with a readable manifest is represented, and it is not unpacked.
12. **Deployment-specific gazetteers of institution names** — deliberately not consumed. Naming an institution does not decide custody, and `00` gives no institution list. Inventing gazetteer contents is R4's forbidden ground.

## Reciprocal boundaries

Every edge names the same fixture on both sides. The full text is in the JSON; the seams in one line each:

| Neighbour | Shared fixture | Here when | There when |
|---|---|---|---|
| `government.school-district-administration` | enrolment census by programme and mode | one institution's own registry about its own registered students | a district/board/authority aggregating many institutions it does not teach in |
| `government.education-accreditation` | the self-evaluation document | authored and held by the reviewed institution's quality office | received into a reviewing body's inbox with a review reference and panel worksheet |
| `business_operations.board-governance` | a governing-body minute | authority derives from statutes/instrument of government, with a separate academic-authority tier | a corporate or unit board under articles, no academic tier |
| `nonprofit.governance` | statutes with a scheme of delegation | the institution is independently evidenced as publicly constituted | a charity, trust or private company runs it — or public status cannot be evidenced at all |
| `academic.teaching` | a cohort marks spreadsheet | board session, moderation, external examiner, ratification | one instructor's working gradebook for one module |
| `academic.transcripts-credentials` | an official transcript with seal and verification code | inside a registry conferral/reissue/verification workflow keyed by an award round | held by the named person beside their own identity and application material |

Two of these six are *reversals of a landed neighbour's own argument*, and I have written this side to match: `government.education-accreditation` is the reviewer, this row is the reviewed; `academic.transcripts-credentials` is the subject, this row is the producer. R1c should confirm both neighbours carry the mirrored sentence.

## Deliberate non-edges

- `business_operations.policy-handbook` — academic regulations and an employee handbook overlap in shape, but the collision is already carried by `business_operations.board-governance` at the level that matters (authority source). Adding a second business_operations mutex would restate one seam twice.
- `business_operations.corporate-regulatory-filings` — a statutory student-record return is a filing, but the discriminating structure is the academic collection round, and the fixture already records `also_schema: business_operations` rather than a mutex.
- `hr.*` — staff appointments, promotions and pay committees appear inside governance packs. That is coactivation on a member, not same-evidence confusion at the node level.
- `government.public-records-foi` and `legal` — an information request or a misconduct appeal held by an institution is genuinely both; the fixtures carry `also_schema: legal` and the anchor's own collisions already cover the Legal seam schema-wide.
- `government.library-administration`, `government.archives-recordkeeping`, `government.museum-collection` — sibling public-service administrations. A university library or archive is a real overlap, but it is a *unit inside* an institution rather than confusable evidence for the institution's governance. No mutex proposed; flagged for R1c only if a landed sibling disagrees.
- `applications.*` — admissions on the institution's side touches application packets, but purpose-coherent applicant packets are the applicant's world. The `must_not_conclude` lists forbid inferring an application purpose from admissions administration.

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `template.dimension_order: []`, `time_first: false`. All intentional under PR-6 and D1, which leave the `government` schema fieldless.

Candidates considered and **not** proposed:

- `school` and `term` are canonical Academic keys. They are tempting here — an institution and an academic year are exactly what this row would branch on — but they are scoped to Academic, where they mean *the school the holder attends* and *the holder's term*. Reusing them for *the institution as self-administering entity* would silently overload a landed key and cross a schema boundary this row has no authority to cross. Recorded as a recommendation for R1c, not minted.
- `institution` is a canonical Finance key and means a financial institution. Not reused.
- `work_type` is Academic-scoped; this row's work types are serialized as `work_types[]` values in prose, which is where the ratified rule puts them.
- `programme`, `module`, `cohort`, `academic_year`, `governing_body`, `committee_reference`, `board_session`, `collection_round`, `review_reference` — all genuinely useful, none canonical, and minting any of them here would be exactly the industry-depth expansion J-IND defers. NJ-2 asks whether a bounded academic-cycle anchor may ever be a stored fact.

The physical recommendation is one shallow, user-approved structure with redacted display labels for anything that touches a named student.

## Grouping without copied facts

Groups are bounded by an exact committee-and-meeting, programme, board-session, collection-round or review reference. A sparse member — an unlabelled appendix, a diagram, an untitled spreadsheet attached to a governance email — may join the neighbourhood without acquiring a body, meeting, programme or year fact; three fixtures set `group_without_copying_facts: true` for precisely that case. Cohort files never propagate a mark, classification or award onto anything, and cross-cohort semantic similarity is suppressed because programme titles, module codes and committee names recur every single year by design.

## NEEDS-JOSEPH

**NJ-1 — schema placement (blocking).** The roster puts this row on `government`, whose schema requires an evidenced public authority, while much of the world the one_line_hint names is not one. Alternatives: (a) keep this pass's narrowing to publicly constituted institutions, accepting that independent-school and private-college governance is covered only by `nonprofit.governance` and `business_operations.board-governance`; (b) reassign the row to a schema that does not presuppose public status; (c) split into a public sibling and an independent sibling. This pass wrote (a) and flagged it. The `government` anchor's own open question — whether public-authority status comes from deployment gazetteers or user confirmation — must be settled first, because it decides how often this row can fire at all.

**NJ-2 — may an academic-cycle anchor ever be a fact and a destination?** An academic year plus a programme or committee reference is a safe display label; a student identifier is not. If PR-6 lifts, decide whether the safe half may become destination-eligible while the unsafe half is barred, or whether Government stays fieldless throughout.

**NJ-3 — tier ambiguity between this row and `government.school-district-administration`.** For a maintained school inside a district, one enrolment return may be simultaneously the school's own record and a row in the district's aggregation. Decide whether that is a genuine mutex, a coactivation, or a case that must always abstain to Review Later. This pass wrote the mutex and the abstention; it did not write coactivation, because a fieldless schema cannot author it.

**NJ-4 — minors.** School-level registry and misconduct records concern children. `00`'s privacy paragraph names educational records but says nothing about a stricter posture for minors, and `academic.k12-schooling` and `academic.iep-accommodation-plans` already face the same question from the other side. P7 should decide whether age of subject changes handling, and it should decide it once, centrally.

## Final recommendation

Keep `government.education-institution-governance` as a placeholder template with no fields, no dimensions, no schema coactivation edge and no time-first hierarchy. Activate only on an academic-cycle administrative anchor held on the producing institution's own side; refuse the sector name, the academic vocabulary, the academic year and the module code as sole proof; treat the registry side as mass named-person data by default; and resolve NJ-1 before anyone builds field vocabulary on top of this row.

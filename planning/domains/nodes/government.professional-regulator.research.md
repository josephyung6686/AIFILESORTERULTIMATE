# Research memo — `government.professional-regulator`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.professional-regulator.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, `launch: placeholder`
Verdict: **ACCEPT** — `refuse_node: false`, `fields: []`, `proposed_fields: []`

---

## 1. The charge against this row, stated at its strongest

Before writing anything I built the case that this id should not exist. Four forms of it are live, and the first is genuinely dangerous.

**(a) It is a duplicate of `government.permit-licensing`.** That row's roster hint reads: *"An authority's record of granting, refusing, varying or revoking permissions to individuals and businesses, and the inspection and enforcement that follows."* Registration of a professional **is** a permission granted to an individual. Refusing an application, imposing conditions, suspending, and erasing **are** varying and revoking. Investigating a complaint **is** the enforcement that follows. On its face this row is `permit-licensing` with the subject dimension set to `person` — and a subject is a **value**, not a node. This is the strongest charge and it nearly carried.

**(b) It is a duplicate of its own schema's default template.** The `government` schema's `work_types` already contains, verbatim, `"planning application, permit or licence case, inspection, enforcement record, reasons, decision, variation, suspension, or revocation on the deciding side"`. Every act this row performs is inside that one string. If the schema's default already enumerates my work, my row is a work_type value wearing a node's clothes.

**(c) It is an organisation name.** "Professional regulator" names a kind of body. The schema's own `never_alone` list already forbids activation from *"a government department, regulator, municipality, legislature, court, public school, archive, museum, or official-looking seal alone"*. A row whose only evidence is the body's identity can never activate — that is the brief's never-alone disqualifier.

**(d) It is a lifecycle.** Registration → renewal → competence audit → complaint → discipline is one permission's life story. Lifecycle stages are not nodes; splitting them would be exactly the 574's mistake.

### Defeating the charge

**(d) is conceded and absorbed, not defeated.** Those five things are stages, and this row does **not** split them. They are `work_types` values inside one row. The row is the standing situation — a body maintaining a register of persons — not any stage of it. No child nodes are proposed.

**(c) is defeated by construction.** The node refuses to activate on a regulator's name, and says so in `never_alone`: a board, council, college, or institute name alone is inert, because it may be issuer, employer, letterhead on the holder's copy, or a footer gazetteer hit. Activation comes from structure — a status-bearing register entry, a cross-registrant sampling table, a panel determination — never from who produced it.

**(a) and (b) are defeated by three structures that exist in this row's file list and cannot exist in a premises-permit file list.** This is the whole argument, so I state each with its fixture:

1. **A persistent register of natural persons with a status history.** `Register Entry - PR-2019-004821 - Hall, Devika - status history.pdf` is a dated table moving one named person through registered → conditions of practice → restored, under a single reference that outlives every individual case and spans a career. A premises permit is issued, varied, and expires; it does not carry a lifetime status ledger for a human, and it is not continuously *published as a statutory list* the way `Public Register Extract - registered practitioners as at 2026-08-01.csv` is. The detection signal — a closed status set with effective dates keyed to a registrant reference — has no analogue on the permit side.

2. **A periodic continuing-competence audit of the same person, over and over.** `CPD Audit 2026 - sample selection and outcomes.xlsx` has a sampling stratum, a claimed-activity total per registrant, a verifier, and a remediation ladder. Nothing anywhere in permit-licensing samples its permit-holders and audits their ongoing learning. This is a second, independent signal family, and it is the one signal that can *only* live on the regulating side — a practitioner's own CPD log has the claims and none of the sampling, verification, or referral apparatus.

3. **A quasi-judicial proceeding whose respondent is a named human being.** `Fitness to Practise Panel - FTP-2025-0899 - determination and sanction.pdf` composites panel composition, findings of fact, an impairment finding, a sanction from a statutory ladder ending in removal from the register, a publication direction, and an appeal route. An enforcement notice against a café is an administrative act; this is an adjudication that ends a person's livelihood and is published under their name.

Those three produce three detection-signal families the schema's `deterministic` list does not carry — I checked it directly: the schema's only registration-adjacent bullet concerns **election administration**, and nothing in it mentions a register of persons, a competence cycle, or a panel determination. So the row's signals genuinely differ from the schema default.

**And one privacy rule differs, not merely one privacy level.** The schema is already `potentially_sensitive`, so a level is not a difference. The *rule* is: on this row alone, the same named person is simultaneously in a lawfully **published** statutory list and in a **protected** conduct or health file, keyed by the same reference. That forces three constraints the schema default does not imply — a published extract or sanction notice must not lower the posture of the packet around it; the registrant's name must never become a visible branch or group label, because on this row a label *is* the allegation; and cross-case grouping by name must be suppressed. 00 supplies the backstop: *"Privacy policy must be enforced before content reaches any model or external connector."*

**Verdict on the charge: the row survives (a), (b), (c); it concedes (d) and encodes it as values.** But (a) is close enough that it is written into the node as **NJ-1**, with the honest alternative spelled out: if R1c judges register + competence-audit + fitness-to-practise insufficient, the correct outcome is to **delete this row into `government.permit-licensing`** as a subject value — not to keep two thin rows.

---

## 2. The node test, all three legs

CONNECTION.md's test: a template exists only when its **detection signals**, its **recommended dimensions**, or its **privacy rules** differ from its schema's default.

**Leg 1 — detection signals. PASS.** Stated above. Three signal families (register status-history; cross-registrant competence sampling; panel determination with a statutory sanction ladder) are absent from the `government` schema's `deterministic` list, and each is true of at least one fixture in the file list. Two more are role-directional rather than topical: a renewal **run** table can only exist on the administering side, and a casework email whose *sender* slot is the regulator's own address is the mirror image of the same notice sitting in the registrant's mailbox.

**Leg 2 — recommended dimensions. FAIL, and honestly so.** The `government` schema's default template reads `dimension_order: []`, because PR-6 leaves the schema fieldless and D1's deferral stands. A template cannot branch on undeclared fields, so my `dimension_order` is `[]` too — **identical to the default**. This leg does not carry the node. I record one prose refinement for R1c that the default only states generally: `government.json`'s own template prose says *"named people must not become the organizing dimension"* (verified verbatim in the anchor, not in 00); on this row that is not a preference but a disclosure rule, because a branch labelled with a registrant's name publishes an allegation about them before any finding exists. Time is not first — 00: *"project, function, or subject usually comes before time"* — and any later order stays editable: *"the user can reverse, remove, add, or flatten dimensions."*

**Leg 3 — privacy rules. PASS.** Not the level (`potentially_sensitive` on both) but the rule, stated above: published-register-alongside-protected-case is unique to this row among the government siblings, and it generates a suppression rule for labels and for cross-case grouping that the schema default does not generate. 00 again: *"Protected material should not be included in cloud-model prompts by default, should not display raw content in general group summaries, and should not be moved automatically without a user policy that explicitly permits it."*

Two of three legs pass. The test requires one. Accept.

---

## 3. Sources actually read

`RESEARCH-BRIEF.md` (full); the stamped assignment; `legal.practice-matter-file.research.md` as the depth calibration and as the direct precedent for a fieldless professional row leaving `role_split` empty; `government.json` (its `template`, `recognition.*`, `work_types`, `sensitivity_why`, `falls_through_to`); `roster.json` for id confirmation; targeted greps of the four landed neighbours that already named this id, plus `career.credentials-licenses.json`.

`planning/00-database-agent-product-design.md` was read **by grep only**, never streamed, per the token instruction; 01 and CONNECTION.md were not opened. Every span quoted from 00 in the node and here was confirmed with `grep -c -F` before use, each returning 1. Two further quoted spans belong to `government.json`, not 00, and are labelled as such where they appear.

---

## 4. Neighbours that already argued against me — reciprocated

Four landed rows name this id. I aligned to all four and rewrote nothing of theirs.

- **`government.education-accreditation.json`** says: *"A professional regulator's subject is a named individual practitioner — registration, fitness to practise, discipline — with staff investigators, and its case files are person-keyed. A file naming a person as the regulated party is not this row."* I reciprocate with the same shared fixtures — a criterion-keyed inspection report and a sanction letter — and the same discriminator: their reviewed party is an institution or programme, mine is a person.
- **`clinical_practice.practice-administration.json`** says: *"an inspection report held by the inspected party is this row, while the regulator's own casework is government.professional-regulator"*, and separately that *"clinical_practice.licensure-credentialing is refused"*, routing personal credentials to `career.credentials-licenses`. I reciprocate the custody discriminator and record the refusal consequence as **NJ-5**: if that refusal stands, my `clinical_practice.licensure-credentialing` edge should be retargeted, and the `career.credentials-licenses` edge already carries the discriminator so nothing is lost.
- **`government.environmental-regulation.research.md`** declines an edge: *"regulates persons and professions; this row regulates sites, installations and discharges. A fitness-to-practise file and a permit condition file share no fixture. No edge."* Agreed and reciprocated as a non-edge. Their subject is a discharge point; mine is a human.
- **`business_operations.compliance-audit.research.md`** declines an edge, saying the holder-side discriminator is already carried by `corporate-regulatory-filings` and the schema-level `government` collision, and that *"Tripling it adds nothing."* Agreed; no edge added.

---

## 5. Reciprocal boundaries authored, with the shared fixture named on both sides

Six `collides_with`, each stating the boundary in both directions and naming the same bytes.

| Neighbour | Shared fixture | Falls to them | Falls to me |
|---|---|---|---|
| `government.permit-licensing` | grant/refuse decision letter; enforcement notice | `Food Business Registration - Riverbend Cafe - approval FBR-2026-0771.pdf` — regulated unit is a business at a premises | `Fitness to Practise Panel - FTP-2025-0899 - determination and sanction.pdf` — regulated unit is a named person, with register, audit, and panel apparatus |
| `career.credentials-licenses` | one renewal notice; one registration certificate | `Screenshot ... my registration renewed.png` — a standing stated **about its own keeper** | `Renewal Run 2026-Q2 ... .xlsx` — a standing **decided about others**, in bulk |
| `nonprofit.member-association` | `Institute of Facilities Managers - Membership Certificate 2026 - M-88214.pdf` and its renewal ledger | voluntary institute: member list, member number, code of conduct, expulsion | statutory register: protected title or entry control, plus fitness-to-practise with an external appeal route |
| `clinical_practice.licensure-credentialing` | a revalidation return with responsible-officer confirmation | the practitioner's packet assembled to prove standing to employers and payers | `CPD Audit 2026 ... .xlsx` — sampling across registrants, which cannot exist practitioner-side |
| `government.education-accreditation` | criterion-keyed inspection report; sanction letter | reviewed party is a programme or institution, peer reviewers, standards edition, cycle | regulated party is a person, staff investigators, person-keyed case |
| `law_practice.regulatory-submission` | the response letter to a regulator's notice, and its enclosure bundle | the regulated firm preparing and sending it | the regulator issuing the notice, receiving it into a case, and deciding |

One `also_holds_with`: **`medical.personal-health-records`**, on `Health Assessor Report - Registrant PR-2011-000714 - confidential.pdf`. This is 00's abstract-that-is-also-an-application shape — the file is genuinely both regulator-held case evidence and health information about an identified person. Coactivation, not collision: neither schema erases the other, and the medical reading must not be suppressed merely because the file sits in a case bundle. Neither side gains a clinical conclusion or an impairment inference.

`role_split` is **empty**. The seam with `career.credentials-licenses` is a textbook role split — the regulator holds the register, the practitioner holds the certificate — but the edge is defined as *same entity type, different field keys*, and `government` declares no field keys at all. `legal.practice-matter-file` left `role_split` empty for exactly this reason and I follow that precedent. The seam is fully carried by the `collides_with` entry instead. **Recommendation to R1c:** if government fields are ever ratified, convert that entry to a `role_split`.

---

## 6. The collision fixture

**`Institute of Facilities Managers - Membership Certificate 2026 - M-88214.pdf`** is the sharpest false positive in the set. It carries a registration-number-shaped token (`M-88214`), a grade of membership, a validity year, a crest, a code-of-conduct reference, and a renewal line. Every lexical cue a naive matcher would use for "professional registration" is present.

**What discriminates it:** there is no protected title, no statutory entry control, and no fitness-to-practise apparatus with an external appeal route. It states one standing about the person keeping it — the holder-side signature — and it is issued by a voluntary institute anyone in the trade may join. It is `nonprofit.member-association` / `career.credentials-licenses`, and it falls to **Independent Records** if neither fires. The `never_alone` bullet that trips it is explicit: *a registration number, membership number, PIN-shaped token, or registrant reference alone* — and it names this fixture.

The honest residue is that a document rarely states its own statutory basis. That is **NJ-2**, and the node's instruction is to abstain to Review Later rather than guess.

A second collision worth naming: **`Food Business Registration - Riverbend Cafe - approval FBR-2026-0771.pdf`**, which shares grant/vary/suspend/revoke vocabulary wholesale. Discriminator: the regulated party is a business at a premises. A named proprietor *inside* the document does not make the proprietor the regulated party — that is written into its `must_not_conclude`.

---

## 7. Files considered and rejected

- **A published sanction notice or register extract downloaded by an employer, verifier, or journalist.** Same bytes as my `Public Register Extract`, but publication by a regulator is not regulator-side custody. → Reading Inbox or Independent Records. The schema's own never_alone already forbids this activation and I inherit it.
- **The same regulator's other functions, on the same disk.** Rulemaking — consultation, responses, final instrument — is `government.regulatory-rulemaking`. An FOI disclosure log and its redaction records are `government.public-records-foi`. HR, board, budget and procurement records are `business_operations.*` / `government.public-procurement`; that last is `government.json`'s own *"government as industry or employer is not this schema"* trap in miniature. A regulator does several distinct things and only person-regulation is this row.
- **An ombudsman file about a complaint against a public body** → `government.constituent-casework`. Identical casework machinery — complaint, investigation, determination — but the respondent is an institution, not a registrant.
- **An employer's credentialing file on its own staff** (verification enquiries, primary-source checks, privileging) → `career.employment-records` / `clinical_practice.practice-administration`. Employer-side, not regulator-side.
- **A university's professional-programme accreditation file** → `government.education-accreditation`, per their stated boundary.
- **A live registration or case-management database, or a regulator mailbox.** A source system is not a file node. A bounded export with a readable manifest is represented; live ingestion is a later connector and security decision.
- **Contact exports and staff address books.** Not activated merely because they contain registrants, panel members, investigators, or complainants. A name is never a case.
- **A law firm's advice to a registrant facing a hearing** → `legal.practice-matter-file`. This row is the deciding body, never the defence.
- **A profession list, allegation taxonomy, sanction ladder, or register-status vocabulary as data.** These are values; enumerating them would rebuild the industry catalogue J-IND defers.

---

## 8. Fields and dimensions

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false` — all intentional, all forced by PR-6 and D1's standing deferral. The row is `launch: placeholder` and the schema declares nothing.

Candidates I considered and rejected rather than proposing:

- `registrant_ref`, `case_ref`, `register_status`, `sanction`, `profession`, `regulated_party_role` — none is canonical, and minting six new keys on a placeholder row is precisely what the brief forbids. They are recorded here as concepts for R1c under NJ-1/NJ-4, not proposed.
- `institution` and `record_type` are canonical but scoped to Finance; `purpose` is scoped to College Applications. Borrowing a key across its scope is the synonym failure the prompt names.
- `work_type` exists canonically and the values in `work_types[]` are shaped for it, but `government` does not declare it, so this template cannot reference it. If the schema ever gains one field, `work_type` is the cheapest and I would put it **second**, never first.

A chronological first level would scatter one registrant's career across calendar folders — application year, admission date, each renewal, each audit cycle, each case, each publication date all differ in meaning. Hence `time_first: false`.

---

## 9. Recognition boundary, and grouping without copied facts

Strong evidence is always **structure plus custody direction**, never vocabulary: a status history keyed to a registrant reference; an application carrying a verification *result* and a decision-maker sign-off; a table spanning many registrants; a competence sample with a verifier and a referral outcome; a case reference recurring across triage, investigation, notice, listing and determination with a named human as respondent; a panel determination composite; a casework email whose *sender* is the regulator. Weak evidence stays weak in any combination — regulator names, registration numbers, licensing vocabulary, protected titles quoted in prose, folder names, extensions, download sessions, dense OCR, a person's name beside a profession. A filename may surface a candidate for local review; it may never create a registrant, case, allegation, status, or outcome fact.

`Statement - witness 2 - unsigned draft.docx` proves the grouping rule: first-person prose with no header, no case reference and no registrant name, tied to `FTP-2025-0899` only because its filename appears in a bundle index. It joins the bounded case group — `group_without_copying_facts: true` — and acquires **no** case, registrant, allegation, date or outcome fact. The same holds for every member of `CPD Portfolio - PR-2019-004821 ... .zip`, whose manifest is read without unpacking on 00's licence that a manifest is *"meaningful evidence of a purpose-defined application packet even when the outer archive name is vague."* Cross-case grouping by registrant name, profession, allegation type or semantic similarity is suppressed outright: those recur across unrelated cases, and a merged view would itself assert a pattern about a person that the product cannot support and must not display.

---

## 10. NEEDS-JOSEPH

**NJ-1 — the permit-licensing merge.** Is person-regulation a distinct situation or a subject value of `government.permit-licensing`? Alternatives: **(i)** keep both, as written, with the register / competence-audit / fitness-to-practise triad as the discriminator; **(ii)** delete this row into `permit-licensing` and carry `subject = person` as a value, accepting that CPD sampling and panel determinations then have no dedicated signal family; **(iii)** invert — make `permit-licensing` the person row and move premises permissions to a business-permission row. I recommend (i) and would accept (ii) as honest; I reject (iii). This is the one open question that could still refuse this node.

**NJ-2 — statutory regulator vs voluntary institute.** Documents seldom state their statutory basis, and both sides use identical register/renewal/discipline vocabulary. Alternatives: **(a)** treat both as this row and accept that voluntary institutes are over-protected; **(b)** route voluntary bodies to `nonprofit.member-association` and accept silent misfiling of small statutory regulators; **(c)** abstain to Review Later whenever the basis is unstated. The node currently encodes (c). R4's gazetteer could later distinguish, but the node writes no list.

**NJ-3 — the publication paradox.** A regulator's sanction notice is deliberately published; the case file behind it is not. May the published notice ever be treated as low-risk while its packet is protected? The node refuses to decide and assigns no handling class — P7 owns this. Alternatives: uniform protection for the whole packet (current posture), or a per-file exception that risks leaking the packet's existence through a summary.

**NJ-4 — name-keyed membership without name-keyed labels.** P9 needs registrant and case references to group, but exposing either in a label discloses an allegation. Alternatives: local-only aliases with redacted display labels; group-by-reference with labels suppressed entirely; or no automatic grouping on this row at all.

**NJ-5 — `clinical_practice.licensure-credentialing`'s refusal.** `clinical_practice.practice-administration` records it as refused, routing personal credentials to `career.credentials-licenses`. If that stands, retarget this row's edge; if it is revived, keep it. R1c should settle it in one place rather than letting three rows each guess.

---

## 11. Self-verification

`python3 -m json.tool` parses the node JSON; its key set matches the landed siblings. All thirteen 00 spans quoted here and in the node returned `grep -c -F` = 1 against `planning/00-database-agent-product-design.md`; the two `government.json` spans returned 1 against the anchor and are labelled as anchor quotes, not 00 quotes. No paraphrase sits inside quote marks. Every edge id — `government.permit-licensing`, `career.credentials-licenses`, `nonprofit.member-association`, `clinical_practice.licensure-credentialing`, `government.education-accreditation`, `law_practice.regulatory-submission`, `medical.personal-health-records` — was confirmed present in `roster.json`. Every `falls_through_to` name is one of 00's residual homes (Protected Records, Independent Records, Review Later, Unsupported or Encrypted); fixture-level fallthroughs additionally use Temporary Screenshots. Every `file_examples.source_type` is in `SOURCE_TYPES`. No thresholds, counts, confidence scores, or handling classes; `sensitivity` is `potentially_sensitive` only. `fields: []` and `proposed_fields: []` — no canonical key referenced or minted. Only the two assigned files were written: no roster, canonical-fields, neighbour-node, `src/`, `check.py`, or SPEC edit. Cross-row changes appear as recommendations under NJ-1 and NJ-5 only.

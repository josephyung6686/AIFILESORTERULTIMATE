# `clinical_practice.protocol-guideline` — J-DEPTH refusal memo

**Depth: J-DEPTH.** This pass reverses the gist draft's “passes cleanly” verdict.

Node: `clinical_practice.protocol-guideline`, template row, `launch: placeholder`, `fields: []`.
Verdict: **REFUSED** because protocol/guideline is a genre or `work_type`, not a situation.

## Sources and procedure

I read `RESEARCH-BRIEF.md`, `DEEPEN-ADDENDUM.md`, and the stamped output of
`python3 planning/domains/dispatch/make_prompt.py clinical_practice.protocol-guideline` before
editing. Binding sources were `planning/00-database-agent-product-design.md`, `ALIGNMENT.md`,
`_CONTRACT.md`, `CONNECTION.md`, `CONNECTION-EXAMPLES.md`, `canonical_fields.json`, the ratified
`DECISION-BRIEF.md`, `ROSTER.md`, `roster.json`, and `src/evidence_shape/vocabulary.py`.

The comparison set was deliberately broader than the roster's old gist hint:

- `clinical_practice.json` and its J-DEPTH memo, because its stated default is the test this template
  must beat;
- `clinical_practice.practice-administration`, because it already lists a “standard operating
  procedure or practice protocol” as a work type and owns the administrative register around local
  procedures;
- `clinical_practice.teaching-material`, because a guideline quoted inside a session deck does not
  turn the deck into a protocol situation;
- `business_operations.policy-handbook`, because its filled owner/version/effective/review block is
  exactly the structure the old draft claimed was unique here;
- `business_operations.corporate-regulatory-filings`, because authority identity and prescriptive
  language do not distinguish published filing guidance from an actual compelled submission;
- `business_operations.compliance-audit`, because a controlled policy inside an evidence request is
  organized by the audit purpose without becoming a new kind of governed document;
- `business_operations.organisational-records`, for the repository's refusal standard.

Every design quotation attributed to `00` was checked verbatim after whitespace normalization.
Short quoted labels from the gist draft and neighboring rows are identified as such; claims about
those rows are observations from their landed JSON/memos or are marked here as inference.

## The correction: topic, issuer, and genre are not a situation

The gist draft defined the anchor as “the governed document and its version.” That sounds concrete,
but full comparison exposes two independent collapses.

First, **governed document** is already sector-neutral. The deepened `policy-handbook` row makes a
filled control block — owner, version, effective date, review date — its one passing detection leg.
The old protocol draft proposed the same slots, with “issuing body” or “approved by” substituted for
owner. That substitution does not create a new relation. A hospital infection-control policy, a
laboratory SOP, a public body's staff code, and a manufacturer's quality procedure may carry the same
control footer byte for byte. The clinical topic tells what the text discusses. It does not tell
what organizational situation the holder has.

Second, **protocol/guideline/pathway** names a genre. The same guidance can be:

- a published PDF saved for reading;
- an adopted local rule that binds staff;
- a teaching source quoted in a grand-rounds deck;
- an evidence item requested by an auditor;
- a consultation draft being authored;
- a research protocol governing a study;
- a blank care form awaiting completion;
- a completed record about one patient.

Those are not edge cases around one situation. They are different purposes with different grouping,
privacy, and collision rules. The old row attempted to own them by expanding `work_types` until the
list crossed every purpose boundary. That is the exact symptom of a genre bucket.

`00` supplies the values/fields discipline directly: “The system may create new values when it sees
a new course, project, company, university, or event, but it should not invent new fields
automatically.” Read across here, NICE, a hospital trust, oncology, sepsis, and antimicrobial
stewardship may all be discovered values or observations. None turns “guideline” into a situation,
and none licenses one node per issuer or clinical topic.

## Node test, argued leg by leg

### Leg 1 — detection signals: fails

The old draft offered eight deterministic patterns. Each fails uniqueness.

1. **Governance block.** Version + approved-by + effective + review-due is the strongest candidate,
   but it is the already-landed `policy-handbook` discriminator. Its shape is intentionally
   sector-neutral. Adding a clinical logo is a topic/issuer overlay, not a new structural signal.
2. **Population scope.** Scope/applies-to/intended-audience blocks occur in staff policies, research
   protocols, standards, regulator guidance, consent material, and teaching plans. A class of people
   rather than an individual describes prose scope; it does not establish holder purpose.
3. **Decision algorithm.** Branches, numbered steps, escalation, and flow diagrams also occur in
   incident response, customer support, safety procedures, research methods, and technical runbooks.
   Form is not situation.
4. **Evidence grades and recommendations.** These distinguish a guideline genre from some other
   prose genres. They do not distinguish saved reading from adopted governance or teaching use.
5. **Blank order set or proforma.** Blankness is file state. Once filled, the same bytes plus entries
   are a patient record. A detector for state may be valuable, but its output belongs upstream of
   situation selection and does not justify a node.
6. **Safety alert.** Issuer reference + required action + action-by date is shared by regulator
   notices, internal compliance actions, product recalls, cyber advisories, and workplace safety
   notices. Clinical subject matter remains a value.
7. **Controlled-document register.** A spreadsheet of title/owner/version/review rows is a register
   used in practice administration, compliance, quality, or policy governance. The objects listed do
   not determine the register's situation.
8. **Absence of a person.** The old memo correctly said absence is not evidence, but then made
   personlessness part of the row's distinction. Blank templates, redacted files, de-identified
   teaching cases, cropped images, and OCR failures all produce the same absence.

The deletion test makes the failure visible: remove clinical terms, issuer names, and genre words.
What remains is either a generic controlled policy, an audit or filing apparatus, a teaching frame,
a completed record, or no activation evidence. No protocol-specific relation survives.

### Leg 2 — dimensions: fails

The contractual answer is simple: `clinical_practice` declares no fields, so this template must have
`dimension_order: []`. It cannot differ from the schema default on published dimensions.

The old memo tried to preserve a future order in prose: issuing body or specialty, then document,
then versions. That does not rescue the leg:

- issuing body and specialty are values, not situations or licensed fields;
- document is a genre/work-type value;
- version is already represented by the universal `version_family` fact;
- situation/function before time is the schema default: “For document and record domains, project,
  function, or subject usually comes before time because putting year first scatters related work
  across calendar folders.”

The order is therefore neither publishable nor unique. A superseded edition may remain a valid
member of a version family without requiring a template that owns every versioned document.

### Leg 3 — privacy rules: fails

The gist draft called this the family's only `sensitivity: none` branch. That conclusion depended on
the genre being uniformly population-level. The concrete files disprove it:

- a published national guideline may be non-sensitive reading;
- a local SOP may expose committee names and internal controls;
- a consultation draft may carry reviewer identities and comments;
- an audit evidence copy may expose deficiencies;
- a blank order set may be non-sensitive;
- the same order set completed for a named patient is protected clinical material;
- a guideline archive may contain both blank and completed forms.

There is no stable row-wide privacy rule. The sharp blank/completed distinction belongs to file-level
sensitivity and receiving-purpose classification. It cannot both prove a protocol node and disappear
when the form is completed. The JSON therefore uses `potentially_sensitive` conservatively on the
refused entry so retirement cannot weaken P7, while explicitly stating that the live receiver owns
the final privacy treatment.

**Overall verdict: refusal.** All three legs fail. This reverses, rather than silently rewrites, the
gist memo's verdict.

## Concrete files, routing, and rejected ownership

The JSON keeps eight examples because refusal must demonstrate where coverage goes.

### `Sepsis pathway v4.2 - ratified 2026-01.pdf`

The control band and decision tree strongly identify a guideline genre. They do not show adoption by
the holder. A NICE download and a locally ratified pathway can share those visible structures. When
the holder's relationship is absent, the honest destination is Reading Inbox. When adoption evidence
exists, the governed-document purpose belongs to the sector-neutral policy situation or to a specific
practice-administration group. Rejected claim: clinical topic + control band activates this row.

### `Infection prevention SOP - local approved copy.docx`

This is the file the old row most wanted. It has the strongest possible local governance evidence:
filled controls and a distribution register. That makes the refusal clearer, not weaker. The same
facts are precisely `policy-handbook`'s passing signal. “Infection prevention” is policy area. The
organization's clinical sector does not require a duplicate template.

### `Practice protocol review register.xlsx`

The spreadsheet is organized by administrative function: maintaining approvals and review dates.
`practice-administration` already lists procedures/protocols as work types and owns practice-level
registers. A row in the register may support a candidate relationship to a document, but it must not
copy owner or review facts onto the member without evidence. This follows `00`: “The graph does not
automatically copy those missing facts onto sparse files.”

### `Grand rounds - applying NICE NG51.pptx`

Learning objectives, audience, session date, presenter, questions, and answer reveals make this
teaching material. The quoted recommendations remain observations from a source. They do not become
product instructions and do not change the deck's situation. This is the same-byte boundary from the
teaching side: a guideline page embedded in a deck is source content, while the session frame owns
the artifact.

### `Sepsis screening tool - COMPLETED - BROWN A.pdf`

This is the primary clinical collision fixture. Printed matter is identical to the blank form,
including its control footer; handwriting and the patient label change its role completely. It is a
record made **on** a governed document, not a version **of** that document. OCR may preserve every
printed protocol signal while losing the handwritten entries, so deterministic genre recognition is
dangerous in the false-safe direction. The receiving candidates are `patient-chart` and Protected
Records, never this row.

### `Companies House filing guidance.pdf`

This non-clinical control proves the issuer fallacy. Authority letterhead, numbered instructions,
scope, dates, and mandatory language still do not create a corporate filing. The filings row requires
the entity/obligation/submission relation: entity identifier, return period, filing reference,
deadline, or acknowledgement. Published instructions about the obligation are Reading Inbox. The
same rule applies to a medical regulator's published guidance.

### `ISMS evidence request 07 - antimicrobial policy.pdf`

The underlying policy has its own controlled-document purpose; the cover sheet and request number
place this copy in an audit evidence chain. `compliance-audit` owns the request/finding/closure
situation. A member can be connected without copying audit facts onto an independent policy copy.
Clinical vocabulary does no organizational work.

### `guidelines_library_backup.zip`

The manifest mixes published reading, local policies, teaching slides, blank forms, a completed
return, and opaque members. Treating “guidelines” in the archive name as a single situation would
erase the most important safety boundary. Members require separate extraction and routing; encrypted
or unreadable members remain Unsupported or Encrypted.

## Collision fixture in both directions

The deepest collision is not between two live nodes. It is between the refused genre and every live
purpose that can contain it.

**Over-fire direction:** `Sepsis pathway v4.2 - ratified 2026-01.pdf` presents the full proposed
signature — clinical topic, scope, branches, owner, version, approval, effective date, review date.
Those bytes still cannot distinguish a downloaded publication from an adopted local rule. Firing the
row would manufacture holder purpose from issuer-side apparatus.

**Theft direction:** `Sepsis screening tool - COMPLETED - BROWN A.pdf` retains the same printed
signature but adds a named patient's entries. Taking it for the genre loses it from `patient-chart`
and risks treating protected material as population guidance. The discriminator is completed
person-specific content, including evidence OCR may miss.

The pair also demonstrates why an “applicability/version/authority” structure cannot rescue the row.
Both files can show applicability, version, and authority. Those slots describe the form, not the
holder's relationship to this instance.

## Reciprocal boundaries

Because the row is refused, the JSON authors no `collides_with` edges from a non-existent situation.
The boundaries still matter for R1c and for work-type routing.

### `clinical_practice.practice-administration`

- It takes the **register or operational cycle**: protocol review schedule, committee action,
  distribution log, implementation checklist, and practice-specific SOP management.
- It does not take a detached published guideline merely because a practice downloaded it.
- This refused row takes nothing. “Protocol” remains a work type within the administrative purpose.

Same bytes: `Practice protocol review register.xlsx` and its linked local SOP. The register's purpose
is administration; the SOP's adopted governance may be policy-handbook. A group link does not copy
register facts onto the SOP.

### `clinical_practice.teaching-material`

- It takes an audience-facing session artifact with objectives, level, presenter, case questions,
  assessment, or attendance.
- It does not take the source guideline as teaching material merely because it appears in references.
- This refused row takes nothing; unattached source material remains reading.

Same bytes: NICE recommendation pages embedded in `Grand rounds - applying NICE NG51.pptx`.

### `business_operations.policy-handbook`

- It takes an adopted controlled document that binds an organization's people and carries the filled
  control apparatus.
- It does not take an authority's public guidance or a downloaded template without adoption evidence.
- Clinical topic is a policy-area value, not a reason for a second controlled-document template.

Same bytes: `Infection prevention SOP - local approved copy.docx`. This is the decisive comparison
that reverses the gist verdict.

### `business_operations.corporate-regulatory-filings`

- It takes compelled submissions and authority responses anchored by entity, obligation, deadline,
  filing reference, submission, or acknowledgement.
- It does not take the authority's published instructions about how entities should comply.
- A regulator's issuer identity alone discriminates neither clinical nor corporate purpose.

Same bytes: `Companies House filing guidance.pdf`; its medical-regulator analogue resolves the same
way.

### `business_operations.compliance-audit`

- It takes the evidence-request/finding/remediation/closure chain and copies of documents assembled
  to answer it.
- It does not turn every underlying policy into an audit artifact outside that evidence relation.
- Clinical topic does not override the audit purpose of a particular copy.

Same bytes: `ISMS evidence request 07 - antimicrobial policy.pdf` inside and outside the pack.

### `clinical_practice.patient-chart`

- It takes completed person-specific care forms, order sets, checklists, and pathways.
- It does not take a demonstrably blank master template as a patient record.
- Uncertain blankness must protect and abstain; it must not fall into a supposedly safe genre node.

Same bytes: blank and completed sepsis screening tools with the same printed footer.

### Research protocols and legal/regulatory use

A trial protocol anchored by study identifiers, ethics approval, amendments, and study conduct is a
research situation. A guideline exhibited in litigation is evidence in a legal matter. A public
authority's own drafting and issuance file is government work. These comparisons were considered but
not encoded as edges: one refused genre node should not enumerate every purpose capable of holding a
document genre.

## Why the controlled applicability/version/authority rescue fails

The dispatch charge asked for a structure unique enough to stand or an honest refusal. I tested the
strongest possible version:

1. a labelled applicability population or setting;
2. a document identity and version;
3. an issuing or approving authority;
4. an effective date and review/supersession state;
5. normative recommendations or decision branches.

This structure is excellent **genre recognition**. It is not situation recognition.

- Policy-handbook matches all five with “employees and contractors” in place of a patient class.
- A research protocol matches all five with participants and investigators.
- Regulator guidance matches all five but is reading for the recipient and authority work for the
  issuer.
- A technical standard matches all five without clinical content.
- A completed clinical form inherits four of five from its master while changing privacy completely.

The structure would therefore create a cross-purpose controlled-document schema if promoted. That
may be a legitimate future architectural question, but the roster already has `policy-handbook` as
the sector-neutral candidate. Duplicating it under clinical topic is not legitimate. If R1c wants a
broader controlled-document template, it should generalize or rename the existing row once, not
clone it for every sector.

## `proposed_fields`

**None.** The draft correctly declined to mint `issuing_body` and `document_version`; this pass
preserves that restraint but changes the reason's consequence.

- Issuer can be observed without becoming a unique protocol field. It is role-ambiguous and may be
  relevant to policy, research, government, filings, and reading.
- `version_family` already handles edition relationships universally.
- Specialty, condition, population, and setting are values or content observations. Promoting them
  merely to rescue a refused node would reverse the node test.
- Adopted-by may be a future **relationship**, not a folder field. It needs P9/R1c adjudication.

## Neighbors considered that did not get edges

- `medical.personal-health-records`: a patient's saved guideline may be personally useful reading,
  but the file carries no personal-health fact merely because the topic is medical.
- `research.lab-notebook-protocols` and `research.ethics-compliance`: a study protocol is routed by
  study purpose and approvals. A refused genre node should not compete with it.
- `legal.practice-matter-file`: a guideline used as an exhibit is grouped through the matter without
  copying legal facts onto an unattached publication.
- government policy and professional-regulator rows: issuer-side work is a different custody role;
  published output on a recipient's disk remains reading unless another active purpose is evidenced.
- pharmacy operations: antimicrobial policy text does not establish dispensing, inventory, custody,
  or a controlled-drug register.

No edge is better than an exhaustive star from a refused genre to every real situation.

## Residual coverage

The refusal does not discard files.

- Reading Inbox handles unattached published guidelines, standards, and regulator instructions:
  “Reading Inbox may hold papers, articles, reports, and saved PDFs that appear to be reading material
  but have no active research, course, or project association.”
- Independent Records handles a durable standalone adopted/local document without a broader accepted
  group: “Independent Records may live under Personal/Independent Records and hold standalone
  certificates, notices, confirmations, forms, and PDFs that have a durable purpose but no broader
  group.”
- Review Later handles unresolved purpose: “Review Later may hold files whose meaning is partly
  understood but whose final location requires a future decision.”
- Protected Records handles person-specific completed forms and sensitive consultation/audit copies:
  “Protected Records may represent sensitive isolated material such as passport scans, medical
  documents, account statements, visas, legal forms, or credentials; it should normally remain
  local-only and must not cause filenames or content to be exposed in model prompts.”
- Unsupported or Encrypted handles unreadable libraries and proprietary exports.

## NEEDS-JOSEPH

### NJ-CP-PG-1 — retire the id and preserve the genres as values

Recommended: retire this roster id and retain protocol, guideline, pathway, SOP, order set, checklist,
safety alert, and controlled register as `work_type` values on receiving situations. Alternative:
keep the node, which duplicates policy-handbook and forces purpose-diverse files into one bucket. Cost
of recommendation: R1c must ensure the useful genre vocabulary remains available after retirement.

### NJ-CP-PG-2 — universal blank/completed observation

Alternative A: a local deterministic observation records that fields/signatures/person blocks appear
completed, with uncertainty explicit. Alternative B: bounded model review after P7 determines state.
The first is safer and reusable but requires detector design; the second handles messy scans but
cannot run before protection. Neither alternative is a reason to keep this node.

### NJ-CP-PG-3 — adopted-copy relationship

`version_family` answers which editions are related, not whether the holder's organization adopted
one. Alternative A: add an explicit adopted-by/controlled-copy relationship in P9. Alternative B:
leave adoption as group-level reasoning around policy/practice administration. A relation would
prevent issuer identity from being misused as adoption evidence, but this pass cannot mint it.

## What changed in this pass

1. Reversed `refuse_node` from false to true and replaced the gist “governed document is unique”
   claim with the full comparison showing it duplicates `policy-handbook`.
2. Kept `fields: []` and `proposed_fields: []`; removed the genre list from `work_types` because a
   refused row owns no values.
3. Replaced affirmative recognition with one explicit no-signal finding, purpose-routing model
   judgements, and eight never-alone categories.
4. Rebuilt the file examples around eight purpose-diverse files, including the same-byte
   blank/completed collision and non-clinical controls.
5. Removed live-node collision edges from the refused row and documented reciprocal boundaries in
   this memo instead.
6. Expanded fallthrough coverage to Reading Inbox, Independent Records, Review Later, Protected
   Records, and Unsupported or Encrypted.
7. Changed sensitivity from `none` to conservative `potentially_sensitive` so refusal cannot weaken
   protection for completed forms or mixed archives.
8. Replaced the old version-retention questions with the three architectural decisions actually
   exposed by refusal: genre-value preservation, universal form state, and adoption relationships.

This memo is shorter than the schema anchors because the conclusion is deletion, not a new filing
world. Its depth comes from testing every proposed discriminator against concrete neighboring
situations, not from padding a refused genre into a pseudo-industry.

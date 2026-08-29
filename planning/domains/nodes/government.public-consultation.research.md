# government.public-consultation — lab notes (R1b)

Depth: J-DEPTH
Date: 2026-08-26
Roster row: `kind: template`, `schema_id: government`, `launch: placeholder`, `parent_id: null`.
Output: [`government.public-consultation.json`](government.public-consultation.json).
Salvage: none. No prior draft of either file existed; both are new.

## Sources actually used

### Binding local sources

- `planning/domains/dispatch/RESEARCH-BRIEF.md` — the standing brief. It supplied the six depth
  requirements this memo is audited against, and the instruction that a refusal is a success.
- `python3 planning/domains/dispatch/make_prompt.py government.public-consultation` — the stamped
  assignment: node test, research procedure, output shape, done-when list, and the three
  `must_consider_neighbors` (`legal`, `nonprofit`, `business_operations`) and two
  `must_consider_residuals` (`Independent Records`, `Protected Records`).
- `planning/00-database-agent-product-design.md` — authoritative, read by targeted grep rather than
  in full. Every span in quote marks in the JSON was matched back against this file mechanically
  (audit below). **`00` never uses the word consultation.** A grep for `consultation`,
  `public comment`, and `comment period` returns nothing. That absence is itself a finding: this
  row cannot claim `provenance: design`, and it is written `inference` — an extension of the
  government schema row's own argued world, not a design mandate.
- `planning/domains/nodes/government.json` — the schema anchor and the default template this row
  is measured against. Its `template.dimension_order` is `[]`; its `work_types[]` includes
  `"policy options paper, impact assessment, briefing, consultation, response analysis, or decision
  record"` and `"proposed rule, supporting analysis, public comment, response to comments, final
  instrument, or guidance"`. Those two strings are the whole case against this row's existence and
  are dealt with head-on below.
- `planning/domains/CONNECTION.md` — the node test, and the verbatim clause that decided the shape
  of the template block: “detection signals, recommended `dimension_order`, optional branch
  patterns, privacy rules, validation constraints”. Also the never-alone invariant: file-kind
  evidence is *constitutionally* never-alone, so no `SOURCE_TYPE` or extension appears in this
  row's `deterministic` list.
- `planning/domains/roster.json` — every edge endpoint resolved. All ten `collides_with` targets
  are roster ids; all six `falls_through_to` names are §7.3 residual names.
- `src/evidence_shape/vocabulary.py` — the fourteen `SOURCE_TYPES`, checked mechanically against
  all fourteen file examples.
- Landed siblings read for edge alignment and house idiom:
  `government.legislative-record.json` (which already names this row in a collision, with the
  fixture `Written evidence HSB0037 - anonymised at submitter request.pdf` — reciprocated from this
  side using that exact filename), `government.library-administration.json` (which names this row
  with `Library strategy consultation - responses export.zip` — likewise reciprocated by filename),
  and `finance.crypto-assets.research.md` as the launch-row depth calibration.

### Bottom-up reality checks

These establish that the named document types and labelled structures are real. They create no
canonical field, no gazetteer content, no regex, and no threshold.

- Government consultation documents in the Westminster and EU idiom publish a **consecutively
  numbered question set**, a **stated closing date**, a **how to respond** section naming a channel,
  and a **consultation reference**. That structure — not the topic — is what recurs across the
  corpus and is what the deterministic signals key on.
- The **response form** is the sharpest real artifact on this node. Real consultation response
  forms carry, beside the numbered answer boxes, a block asking the respondent to elect how their
  own answer may be disclosed: publish with my name / publish anonymously / do not publish. I have
  found no other filing world in the 23 schemas where the disclosure permission on a file is
  declared by someone who is not the file's holder, and where members of one packet routinely carry
  *different* permissions.
- **Campaign or template responses** are a real and well-documented feature of large consultations:
  a campaigning organisation circulates a template text and many independent people submit it
  under their own names. The bytes are near-identical; the authors are not.
- The **summary of responses / government response** pair is a real, named document type: the first
  reports what respondents said, keyed to the question numbers; the second states what the
  authority will do.

## THE CHARGE — the strongest case that this row should not exist

I ran this before writing anything, because on a fieldless placeholder schema a template row is
cheap to invent and expensive to keep.

**Charge 1 — it is a work_type value, and its own schema already says so.** This is the strongest
form of the charge and it is not rhetorical: `government.json`'s `work_types[]` literally contains
the token `consultation` inside the policy band and `public comment` inside the rulemaking band.
Under ALIGNMENT and the assignment's §4, work types are **values** of a field, never nodes. On its
face, `government.public-consultation` is the 574's original mistake in miniature — a value
promoted to an id.

**Charge 2 — it is a lifecycle stage.** A comment period sits between a draft proposal and a
decision. `government.legislative-record` already refused *stage* as a dimension on exactly this
reasoning ("a bill's stages are an authoritative ordering on the universal version-family relation
that already exists, not a new fact"). A consultation is the same shape: open → closed → analysed
→ responded. Stages are orderings, not nodes.

**Charge 3 — it is a duplicate of neighbours.** `government.policy-development` consults on a
policy. `government.regulatory-rulemaking` runs notice-and-comment. `government.planning-application`
collects neighbour representations. `government.legislative-record` issues calls for written
evidence. `government.statistical-programme` fields survey instruments. Subtract all five and it is
not obvious anything remains.

**Charge 4 — it is a medium or a length.** A consultation is prose in PDFs and spreadsheets. If the
only difference is "lots of documents about one topic", that is a group, not a template.

**Charge 5 — it is defined by absence.** A weak version of this row would say: material about a
public proposal that is *not yet* a decision. A row whose evidence is the absence of a decision can
never activate.

**Charge 6 — never-alone evidence only.** The word *consultation*, the name of a department, the
name of a responding association, a numbered question set, a closing date. Every one of these is
never-alone. If that is the whole evidence base, the row is a label.

### Defeating the charge

Charges 4, 5 and 6 are defeated cleanly and Charges 1, 2 and 3 are defeated only after the row is
narrowed. The narrowing is the real work of this pass, and I state it plainly: **this row is not
"documents about a consultation". Its evidence is the many-to-one received corpus and its
permissions.**

- **Against Charge 1.** The work-type value `consultation` names the *invitation document*, and I
  concede it entirely: the consultation document is `government.policy-development`'s or
  `government.regulatory-rulemaking`'s work-type value, and this row's `collides_with` says so on
  the shared fixture `Consultation on the draft Housing Standards Code - consultation document.pdf`.
  What is left over is not a value: it is a **corpus of files by hundreds of unrelated authors,
  content-incoherent, joined by one reference, each carrying its own disclosure election.** No
  enum value can describe a many-to-one structure across independent authors. A work type is a
  property of one file; this is a property of a *set*.
- **Against Charge 2.** A stage is an ordering over material that already has a home. Here the
  received corpus has no home in the proposal's lifecycle: the proposal document and the received
  responses have different authors, different holders-of-origin, different privacy postures, and
  different grouping rules. The stage framing collapses the moment you ask who wrote the bytes.
- **Against Charge 3.** After the subtraction, what remains is exactly the exercise that is a
  consultation *of its own* — a published invitation with its own reference and question set, not a
  comment window docketed inside another proceeding. The JSON encodes this as the rule that decides
  each competing edge, and where it is genuinely unsettled (rulemaking) it is carried as
  **NJ-CONSULT-1** rather than guessed.
- **Against Charge 4.** The discriminators named in `deterministic` are structural, not medial:
  question-numbered answer slots, a respondent-declared publication-permission block, a rows-are-
  respondents / columns-are-question-numbers export, a near-identical text cluster with *different*
  authors. None of these is a format.
- **Against Charge 5.** Nothing in the recognition list is an absence. Every signal is a positive
  labelled structure.
- **Against Charge 6.** Twelve `never_alone` rules encode precisely the tempting evidence, including
  the word *consultation* itself, the authority's name, the responding organisation's name, a
  numbered question set alone, a closing date alone, and — the one that matters most — a
  rows-are-people, columns-are-questions spreadsheet alone.

**Verdict: the row survives, narrowed.** `refuse_node: false`. Had I been unable to defeat Charge 1,
the honest outcome was a refusal routing the coverage to `government.policy-development`,
`government.regulatory-rulemaking`, and `Protected Records` / `Reading Inbox`.

## The node test, argued in full

CONNECTION.md's test: a template row exists only when its **detection signals**, **recommended
dimensions**, or **privacy rules** differ from its schema's default. Three legs, each argued
separately. Two differ decisively; one does not, and I say so rather than manufacturing it.

**Leg 1 — detection signals. DIFFERS, decisively.** The government schema's default detection is
role-structural: it asks whether an evidenced public body is acting in an authority-side role. It
recognises a bill packet by an official bill identifier, a rulemaking by a proposal identifier, a
procurement by a notice. **None of those is a many-to-one structure.** Every one of the schema
default's recognitions is a document or a docket produced *by the authority*. This row's core
signals are the opposite: a set whose members were produced by parties who are not the holder, and
whose only shared anchor is the call they answer. The single sharpest discriminator — the
respondent-declared publication-permission block — appears nowhere in the schema default and could
not, because it is a slot filled in by a member of the public.

**Leg 2 — recommended dimensions. DOES NOT DIFFER, and this is not fudged.** PR-6 leaves the
government schema fieldless. The schema default's `dimension_order` is `[]` and this row's is `[]`.
A template may only branch on a field its schema declares (`_CONTRACT.md` rule 8), so no other
answer is contract-compliant. This leg contributes nothing to the row's survival. What the row does
contribute here is two **refusals** recorded for the day fields land: respondent identity must never
be a dimension (it is authorship, `00` forbids authorship as a destination, and it would publish
members of the public as directory entries); and consultation stage must never be a dimension (it
would scatter one exercise across open and closed branches, against `00`'s reason for putting
function before time). If fields are ratified, the recommended first level is the consultation
reference and the second the document function.

**Leg 3 — privacy rules. DIFFERS in kind, not degree.** The schema default is a uniform posture:
"submissions and named-person case material are protected by default." Uniform protection is
sufficient for a casework file, an FOI case, or a procurement bid, because one party's material is
governed by one rule. It is **not** sufficient here, for a reason specific to this world: inside a
single received-responses packet, members carry *different, third-party-declared* disclosure
elections. A packet-level judgement is therefore always wrong in one direction or the other — it
either publishes someone who asked not to be published, or it withholds the material the exercise
promised to publish. This row's privacy rule is per-member and holder-external, and the schema
default has no such concept. A second rule follows: the published outcome is genuinely public
bytes, and its presence must not lower the posture of the corpus it summarises.

**Two of three legs differ; the test is disjunctive; the node stands.** Nothing was invented to keep
it: `fields: []`, `proposed_fields: []`, `also_holds_with: []`, `role_split: []`, no new dimension,
and the one key that was genuinely tempting is parked in `open_question`.

## The collision fixture

`Customer satisfaction survey results Q1.xlsx` — a company's customer-experience export. It has
rows that are people, columns that are numbered questions, free-text opinion columns, and a
provider export banner. Structurally it is nearly identical to `HSC-0417 responses.xlsx`, and it is
the file most likely to drag this template onto material it must never touch.

Three discriminators, in strength order:

1. **No publication-permission column.** The consultation export asks each respondent to license
   disclosure of their own answer. A satisfaction survey treats confidentiality as the researcher's
   standing policy — the participant is never asked, because the answers were never going to be
   published under their name.
2. **Recruitment direction.** Consultation respondents *self-select* from a published invitation
   with a closing date. Survey participants are *recruited* by the holder from a customer list or a
   panel. The presence of a customer-account column is positive evidence of the wrong direction.
3. **No published call.** There is no consultation document, no reference token recurring on other
   corpus members, no closing date on a public notice.

It routes to `Review Later` if the holder role is unclear, and is claimed by
`business_operations.user-research` in `collides_with` by exactly this filename.

A second, quieter collision fixture is `Riverside Park redesign - have your say - comments.csv`. It
carries the phrase most associated with this row and is not this row: its rows key to a planning
application reference, there is no numbered question set, and the comment window is a statutory
notice period inside one case.

## Reciprocal boundaries

Ten `collides_with` edges, each stating the boundary in both directions and naming the same fixture
on both sides where a landed row already argued it.

- **`government.policy-development`** — fixture: the consultation document itself. *Theirs:* the
  proposal, the options, the reasoning, and the invitation; their work-type enum already owns the
  value `consultation`. *Mine:* what came back and what was made of it. Where nothing was received,
  policy holds both halves.
- **`government.regulatory-rulemaking`** — fixture: a proposed instrument published for comment
  carrying a docket identifier *and* a consultation reference. *Theirs:* a docketed step in a
  legally structured proceeding ending in a made instrument and a response-to-comments. *Mine:* a
  discretionary invitation ending in a summary of responses and an outcome statement. Provisional
  rule: the docket wins when it binds the comment to an instrument. **Least settled edge on the
  node — NJ-CONSULT-1.**
- **`government.legislative-record`** — fixture `Written evidence HSB0037 - anonymised at submitter
  request.pdf`, named identically by that row. *Theirs:* inquiry-series numbering, custody by a body
  that reports rather than decides, publication as a report appendix. *Mine:* a consultation
  reference and a body that will decide. Both sides hold it protected regardless — that is stated on
  both sides and neither may relax on the other's account.
- **`government.planning-application`** — fixture `Riverside Park redesign - have your say -
  comments.csv`. *Theirs:* representations keyed to one application or scheme reference. *Mine:* a
  policy-wide consultation with its own question set. A council consulting on planning *rules* is
  mine; a council collecting comments on one *application* is theirs.
- **`government.statistical-programme`** — fixture: a numbered instrument plus a respondent-level
  export. *Theirs:* collection to measure, with a sample, a methodology note, and disclosure
  control. *Mine:* collection to consider views, from a self-selecting public, with per-respondent
  publication permission and no sampling frame. Neither side may treat the other's export as its
  own: a consultation response sheet is not microdata.
- **`government.public-records-foi`** — fixture: a redaction schedule over received responses.
  *Theirs:* disclosure driven by a request, with a request reference and a refusal or review route.
  *Mine:* publication driven by the exercise's own promise and the respondents' own elections. A
  request *for* unpublished responses is theirs even though its subject is my corpus.
- **`nonprofit.advocacy-campaign`** — fixture `HSC-0417 - campaign text cluster - identical
  submissions.docx`. *Theirs:* the toolkit, the circulated template text, and the campaign's own
  filed submission. *Mine:* the authority's many received copies attributed to different submitters.
  Identical bytes, opposite roles.
- **`business_operations.user-research`** — fixture `Customer satisfaction survey results Q1.xlsx`,
  discriminated above in both directions.
- **`nonprofit.member-association`** — fixture: a consultation on rule changes circulated to members.
  *Theirs:* respondents drawn from a membership roll. *Mine:* an undetermined public. Membership
  scoping is the discriminator, not the vocabulary.
- **`government.library-administration`** — fixture `Library strategy consultation - responses
  export.zip`, named identically by that row. *Mine:* the consultation identifier across
  content-incoherent members anchors the packet. *Theirs:* the service's own operational
  contribution inside it — service-point data, opening-hours schedules — which I never claim merely
  because it sits in my packet. Their file already states this from their side; I reciprocate
  without editing it.

## Files considered and rejected

Tempting false positives that are **not** this row's evidence:

- **A downloaded consultation document held by anyone at all.** It is the single most common
  consultation-shaped file on any real disk and it is a publication, not custody. Kept as a file
  example precisely so its `must_not_conclude` can say so; routes to `Reading Inbox`.
- **A petition with signatures.** Many names, one text, a public cause. It is not a response to a
  published question set, there is no invitation, and no one elected a publication preference. It
  belongs with advocacy material, and admitting it would let this row swallow every mass-signature
  document.
- **An opinion poll or a market-research panel report.** Numbers about public views, but the
  respondents were sampled, not invited, and the report is a finding, not a corpus.
- **A public meeting sign-in sheet and a room-booking confirmation.** Engagement logistics that
  happen to sit in a consultation folder. They are facilities and administrative records; they
  carry no question set and no permission. The row lists engagement logistics as a *work type*, not
  as an activating signal, deliberately.
- **A parliamentary petition response or a ministerial correspondence reply.** A named person wrote
  in and the authority replied — that is `government.constituent-casework`, a one-to-one exchange,
  not a many-to-one corpus.
- **A staff engagement or internal-consultation survey run by a public body on its own employees.**
  The most seductive rejection: the holder *is* a public authority, and the artifact is a numbered
  question set with responses. It fails on the audience test — an employer surveying its own staff
  is HR material, the invitation was never public, and admitting it would make "public body plus
  survey" sufficient, which is exactly the never-alone failure.
- **A standards body's public review of a draft standard.** Structurally almost perfect: a published
  draft, numbered comments, a disposition-of-comments table. It fails only on public-body status,
  which is why `nonprofit.standards-body`'s claim is real and why the public-authority evidence
  requirement is written into the PRECONDITION rather than assumed.
- **An `.ics` invitation to a consultation event and a `.vcf` for a stakeholder contact.** These are
  `SOURCE_TYPES` and neighbourhood furniture. Neither carries the invite-and-receive structure;
  `calendar` and `contacts` are consequently absent from this row's `file_kinds.source_types`, which
  is a deliberate narrowing against the schema default's fourteen.
- **A `legal.*` framing of the whole row.** Considered because consultation duties are frequently
  statutory and because a failure-to-consult challenge is litigation. Rejected: the discriminating
  evidence never collides. `legal` covers a person's legal record, a practitioner's matter, and
  public legal material; a judicial-review bundle *about* a consultation is a matter file whose
  anchor is a claim number. No edge written — the government schema row already carries the `legal`
  collision at schema level, and duplicating it here would give one evidence item two claimants.
- **`business_operations.market-research` as a second commercial edge.** Rejected as redundant:
  `business_operations.user-research` already carries the identical discriminator on the identical
  fixture, and a second edge would split one boundary across two rows.

## Sparse-file discipline

`Screenshot 2026-03-02 at 11.04.13.png` is the `HW 3.pdf` of this node. It OCRs to a
response-received confirmation with a reference-shaped token, it has no EXIF, and it sits beside two
consultation PDFs. It is marked `group_without_copying_facts: true`; its `facts_legal` is the
universals only; and its `must_not_conclude` covers both halves — the neighbourhood may retrieve it
without the schema activating from it, and the absence of EXIF is not proof of a screenshot. Its
residual is `Temporary Screenshots`.

## Field decisions and `proposed_fields`

**`proposed_fields` is empty, deliberately**, matching both landed government siblings. `fields` is
empty because PR-6 leaves the schema fieldless and rule 12 forbids a template copying its schema's
list. The legal set on any file this row recognises is the universals: file type, creation date,
language, duplicate family, version family, sensitivity status.

Three strings this material is saturated with are deliberately **not** proposed as fields:

- **the consultation reference.** The strongest candidate on the node and still not proposed. It is
  a template-local anchor, and minting a key for it would immediately raise whether it may be a
  folder level — a question that belongs to the central adjudication PR-6 defers, not to one child.
- **the respondent.** It is authorship. `00` forbids authorship as a destination, and here it names
  a member of the public; a directory tree of respondent names would publish exactly the identities
  the exercise promised to control.
- **the publication permission.** The most interesting refusal in this row. It is load-bearing for
  detection *and* for privacy, and it is the one attribute in this world that no other schema has.
  It is still not proposed, because the honest question is prior to the key: is a third-party
  disclosure election a *fact* at all, or purely a privacy attribute that must never reach the tree?
  Raised as **NJ-CONSULT-2**; this row's own recommendation is that it never be a folder level.

`proposed_context_terms` carries a single entry marked PROPOSED listing seven candidate phrases for
R6, each of which must co-occur with a second signal. `00` states the pattern-plus-context shape for
course codes only and lists none of these; the entry says so in its own text.

## Neighbours considered that did **not** get an edge

- **`legal.practice-matter-file` / `legal.personal-legal-matters`** — a judicial review of a
  consultation is a matter file anchored on a claim number. No shared discriminating evidence; the
  schema-level `legal` collision already covers it.
- **`nonprofit.governance`** — a charity's members' consultation on its constitution. Covered by the
  `nonprofit.member-association` edge; a second nonprofit edge on the same discriminator would be
  duplication.
- **`government.elections-administration`** — a referendum or a ballot is a *vote*, not a comment.
  The many-to-one shape is superficially similar and the discriminator is total (a vote is counted;
  a response is read), so there is no confusable evidence to write an edge about.
- **`academic.*`** — a research ethics consultation, a university's course-feedback round. The first
  is research administration, the second is teaching feedback; neither has a public invitation.
- **`also_holds_with`** — empty by contract. It is a schema-row property and the government schema
  declares none, so every `file_examples.also_schema` on this node is `null`. The dual-membership
  case that *looks* real here — a respondent organisation's submission, which is both that body's
  operating record and, in the authority's copy, my evidence — is not co-activation: the two copies
  have different holders. It is a role split, written as a collision.
- **`role_split`** — empty, and the emptiness is the finding. Two real splits exist (inviting
  authority vs respondent; analysing office vs deciding office) and `role_split` requires different
  **field keys** to split against. PR-6 leaves none. Minting one to solve a single template's
  problem is the move that produced thousands of private field names in the overnight pass.
  Recorded as NJ-CONSULT-2 instead.

## Audits run before returning

- `python3 -m json.tool` — parses.
- Every span in quote marks in the JSON was extracted mechanically and matched, under whitespace and
  curly-quote normalisation, against `00` or `CONNECTION.md`. **All matched verbatim.** Two
  originally did not and were corrected rather than kept: the `Temporary Screenshots` residual cite
  was a paraphrase and was replaced with the real clause, and one `must_not_conclude` line put quote
  marks around the token `00` in a way that read as an attributed span — rewritten as plain prose.
  **No `00` quotation in this node is fabricated or paraphrased inside quote marks.**
- Every `file_examples.source_type` is in `SOURCE_TYPES` (14/14).
- Every `collides_with.domain` is a roster id (10/10). Every `falls_through_to.residual_template`
  and every `falls_through_if_inactive` is one of §7.3's nine residual names.
- Every `file_examples.also_schema` is `null` (14/14), as the schema's empty `also_holds_with`
  requires.
- `fields`, `proposed_fields`, `also_holds_with` and `role_split` are all empty; the last two carry
  notes saying why.
- No number in the file is a threshold, a score, or a count of evidence — the digits present are
  filenames, reference tokens inside fixture names, and question numbers quoted from a fixture.
- No handling class is assigned; `sensitivity` is `potentially_sensitive` only.
- Only the two assigned files were written. `planning/29-DOMAIN-OWNERSHIP.md`, the roster,
  `canonical_fields.json`, `check.py`, `src/`, and every neighbour node are untouched.

## NEEDS-JOSEPH (this node only)

- **NJ-CONSULT-1 — who owns a comment period that is a stage of another proceeding.** Rulemaking
  dockets, planning applications, and committee inquiries all collect public comment under their own
  identifier. Three answers: (a) the proceeding's row holds its own comment corpus and this row owns
  only exercises with a consultation reference of their own — what the node recommends today, and
  what its four competing edges encode; (b) this row holds every received-comment corpus in
  government and the proceeding rows hold only their own produced documents, which centralises the
  per-member permission rule in one place but strips the rulemaking and planning rows of material
  that is legally part of their case; (c) both fire and the group is shared, which the fieldless
  schema cannot express. **Recorded, not resolved.** Reciprocal edits to
  `government.regulatory-rulemaking`, `government.planning-application`, and
  `government.legislative-record` are RECOMMENDATIONS to R1c; I edited none of them.
- **NJ-CONSULT-2 — the respondent-declared disclosure permission.** This is the one thing this row
  found that the product may not have anywhere else: an attribute of a file whose value is set by a
  third party and which varies between members of one packet. Three answers: (a) it stays prose in
  recognition and privacy, as it is today; (b) it becomes a privacy attribute on the shared
  vocabulary, never destination-eligible, which is this row's preference; (c) it becomes an ordinary
  field, which would make a folder level named for a disclosure election possible and is the outcome
  this row argues against. Also unresolved with it: whether a consultation-exercise reference and a
  document-function concept may exist, and whether either may be destination-eligible. **No field
  proposed.**
- **NJ-CONSULT-3 — campaign clusters versus the universal duplicate-family relation.** Near-identical
  submissions from different named authors are simultaneously a duplicate family (by bytes) and many
  independent acts (by authorship). Collapsing them loses independent submissions; keeping every
  member loses the fact that they are one coordinated act. This row keeps every member and records
  the coordination as a grouping reason. This is a decision about a **universal** relation, so it
  cannot be settled by one template — confirm centrally, or invert.

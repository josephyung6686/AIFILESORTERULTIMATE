# career.employment-records — lab notes (R1b)

Row: `kind: template`, `schema_id: career`, `launch: placeholder`, `provenance: inference`.
Verdict: **node stands** (`refuse_node: false`). Reasoning under "Node test" below.

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every span I put inside quote
  marks was grep-verified with `grep -qF` against this file **before** it was written into the
  node; 57 candidate spans were checked and all 57 matched. Nothing is quoted that I did not
  match mechanically.
- `planning/domains/_CONTRACT.md` — entry shape; rules 8 (snake_case + a dimension may only
  branch on a field the schema declares), 10 (no career field rows), 12 (`uses_schema` /
  `schema_id`, a template never copies the field list), 14 (closed edge vocabulary), 15
  (placeholder schema may carry an empty field list).
- `planning/domains/CONNECTION.md` — §2 node test, §3 no schema inheritance, §4 activation
  (never-alone, grouping firewall), §5 the closed edge table, §6 field identity, §7 four objects,
  §11 PR-6 (career fields deferred; the Career dimension recommendation is "held as prose until
  the schema lands").
- `planning/domains/CONNECTION-EXAMPLES.md` — fixtures 1 (facts are not a path), 3 (`HW 3.pdf`
  sparse-file rule), 5 (`.ics` fires on content, never on `source_type`).
- `planning/prompts/ALIGNMENT.md` — two roster kinds; a template that only repeats its schema's
  fields and dimension order is not a node; work types are values.
- `planning/domains/roster.json` — confirmed my id, kind, `schema_id`, the two
  `must_consider_neighbors` (finance, legal) and the two `must_consider_residuals` (Independent
  Records, Protected Records). Every neighbour id I cite was checked against the roster's 83 ids.
- `planning/domains/canonical_fields.json` — the 37 canonical keys. Checked mechanically that
  every `facts_legal` entry in every file example resolves to one of them, and that neither
  proposed key already exists under another spelling.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`, verified by script against every
  `file_examples.source_type` and every `file_kinds.source_types` member.
- `planning/domains/nodes/career.json` — my schema row. I follow its deferral exactly rather
  than working around it.
- `planning/domains/nodes/academic.teaching.json` — it already states a `collides_with` toward
  this row; I reciprocated it in its own terms rather than re-deciding the seam.
- `planning/domains/nodes/finance.json`, `legal.json` — read to check what the two named
  neighbour schemas already assert (finance already collides with `career`; legal already
  also-holds with `career` at the schema level, which is where that edge belongs).
- I did **not** open `planning/deferred-catalogues/` — recognition here consumes an organization
  gazetteer whose contents are R4's, and I have no legitimate need to read or invent its members.
- `planning/01-product-design-structured.md` — not read. Its only role is as a numbered rendering
  of `00`, `00` wins on conflict, and I had `00` in full.

## Node test — why this is not the career schema's default template

The prompt refuses a template whose detection signals, dimension order **and** privacy rules are
identical to the schema's default. `career.recruiting` is that default. Two of the three differ
substantively, and the third differs in prose:

1. **Detection signals differ at a nameable seam.** Recruiting is evidenced by candidacy language
   about a process still open — application, interview, requisition, an unsigned offer. This
   template is evidenced by an *executed* signature or countersignature block together with a
   labelled effective-or-start-date slot, and by everything downstream of it (reviews, benefits,
   leave, equity granted as pay, separation). The offer letter is the single document that sits on
   the line, and the countersignature is the discriminator. That is a real, testable seam, not a
   relabelling.
2. **Privacy rules differ, and this is the strongest reason the row exists.** Recruiting material
   is mostly the holder's own outbound self-presentation. This template's material is executed
   compensation terms, work-authorization paperwork carrying identity numbers, disciplinary and
   separation records, and leave paperwork carrying a clinician's certification. The roster's own
   `must_consider_residuals` records the split: recruiting gets Independent Records / Review
   Later, this row gets Independent Records / **Protected Records**. `Protected Records` is this
   row's *default* fallthrough, not an edge case, and the template records a protected-first
   optional branch pattern that recruiting has no use for.
3. **Dimension order:** both are empty by contract (below), but the recorded prose recommendation
   diverges at the middle level. `00`'s Career order offers "role or recruiting cycle"; a job held
   has no recruiting cycle — the tenure is bounded by an agreement and a separation, not an
   application season — so this template takes the role half and recruiting takes the cycle half.
   That divergence is in `00`'s own sentence; I did not invent it.

## Why `fields` and `dimension_order` are both empty

Not a refusal and not laziness. `_CONTRACT` rule 10 / D1-as-narrowed defers the career field rows
(owed before P10), PR-6 says the placeholder schema carries an empty field list, and rule 8's
second half says a dimension may only branch on a field the schema declares. The career schema
declares none, so a non-empty `dimension_order` here would open tree levels no fact could ever
fill — the exact defect `_CONTRACT` rule 8 records at scale (566 of 1,648 legacy dimensions). The
recommendation is therefore carried as prose in `template.why`, in the form CONNECTION PR-6
prescribes, so R1c/P10 can restore it mechanically the moment the keys land. `career.json` made
the same call and I matched it deliberately rather than diverging.

## proposed_fields — justification, and what I refused to propose

Two proposals, both explicitly marked as proposals and neither written as a field row:

- **`employer`** (string, destination_eligible, ceiling `validated` via an organization gazetteer
  matched at word boundary plus employment-relationship context). No canonical key can carry it.
  `institution` is scoped to a financial or record-issuing institution. `client` is the
  counterparty of an engagement — the opposite side of `00`'s "the author’s firm and the client
  organization" pair. `school` is the holder's own educational institution. `our_firm`, the
  nearest existing key, is recorded as authorship-side identity and is **not**
  `destination_eligible` — and `00` requires it not be. Since `00`'s recorded Career order puts
  the company *first as a folder level*, the key that carries it must be destination-eligible, so
  no reuse works. That constraint is the one concrete thing this row adds to `career.json`'s open
  question.
- **`role`** (string, destination_eligible, ceiling `direct` from a labelled Position/Title slot,
  `possible` from free text). `00` names this level in its own words. No canonical key holds a
  position a person held: `work_type`, `artifact_type`, `record_type` and
  `application_document_type` all answer *what kind of document*, and `stage` is a research
  workflow position. I flagged the naming risk explicitly — `role` as a field key sits beside
  `role_split` as an edge name in CONNECTION §5, and a different spelling may be better.

**What I deliberately did not propose:** a career document-type key. Minting a fourth scoped
spelling of *what kind of document is this* beside `work_type`, `record_type` and
`application_document_type` is precisely the 574's fragmentation failure. The honest fork —
widen an existing enum's role across domains, or accept that a career-scoped key is warranted —
is a decision about the product's shared vocabulary, so it went into `open_question` instead of
being resolved by a swarm agent. This is the one place I could have made the node look more
complete and chose not to.

## Files considered and rejected

- **`Resume - 2026.pdf`** — the resume is a version family and a recruiting artifact, not an
  employment record. It belongs to `career.recruiting` (and `career.json` already uses it as a
  fixture). Rejected to avoid duplicating the schema row's example set.
- **`Job Description - Analyst.pdf`** — pre-hire, recruiting's.
- **`LinkedIn export.zip` / `profile.json`** — a platform export is a `SOURCE_TYPE` question and a
  social-export situation, not employment-record evidence.
- **`Benefits Guide 2025.pdf` routed to Reading Inbox** — I considered adding Reading Inbox to
  `falls_through_to` on the grounds that a benefits guide reads like "papers, articles, reports,
  and saved PDFs". Rejected: a handbook or benefits guide the employer issued to *this* person is
  a durable record with a purpose, which is Independent Records' own definition. Adding a sixth
  residual would have been padding.
- **`Expenses Q3.xlsx` / reimbursement claims** — real, and genuinely the finance neighbour's
  (`finance.receipts-expenses`). Kept out of the file list; the timesheet already carries the
  hours-and-money seam.
- **A `.vcf` of a colleague** — `00` keeps contact data privacy-protected rather than a folder
  proposal basis, and `career.json` already carries that fixture. Not repeated.
- **`W-4 2024.pdf` as a named fixture** — I wanted a real onboarding form but a jurisdiction's
  form name is a **value**, never a field (D4 / `_CONTRACT` rule 9). It survives inside
  `recognition.deterministic` as an explicitly value-level aside; it is not a filename fixture and
  no jurisdiction-specific key was proposed.

Thirteen file examples landed, covering the ugly cases the prompt asks for: a labelled form
(`Mid-Year Review 2025.docx`) against unlabelled prose (`Review.docx`); an OCR of a portal page; an
archive read from its manifest (`onboarding.zip`) and an encrypted archive that cannot be read at
all (`HR docs.zip`); a calendar file that must **not** fire; a spreadsheet; a neighbour's file that
looks like mine (`ADP Pay Statement Mar 2026.pdf`); and a file that is legitimately two domains at
once on disjoint evidence (`Leave of absence - medical certification.pdf`).

`Review.docx` is this node's `HW 3.pdf`: `group_without_copying_facts: true`, no employer fact
invented from the filename token, no employer fact copied from the two neighbouring files that do
name one. `Offer letter - countersigned.pdf`, `onboarding.zip`, `Timesheet Q1.xlsx`,
`Screenshot ....png` and `HR docs.zip` carry the same flag for the same reason.

## Neighbours considered that did **not** get an edge, and why

- **`also_holds_with` — empty, on purpose.** CONNECTION §5 restricts it to **schema ↔ schema**;
  the dispatch prompt lists it as available to me without that restriction, and CONNECTION wins
  (the prompt's own tiebreak says so). The real also-holds joins for this material — career ↔
  legal on an executed agreement, career ↔ medical on leave paperwork, career ↔ identity on
  work-authorization forms — belong on `career.json`, and two of the three are already asserted
  there. I recorded the co-activation inside `file_examples[].also_schema` instead, which is where
  a template may legitimately say it. **Noted per the prompt's instruction to flag a
  CONNECTION/prompt disagreement.**
- **`role_split` — empty.** The split this template genuinely needs is *employer of record* vs
  *client* vs *the holder's own school*, and the employer key does not exist yet. Authoring a
  `role_split` against a key that is only a proposal would mint the thing D1 defers. `role_split`
  is also flagged in `check.py`'s `FORBIDDEN_EDGE_KEYS` (canonical-field-list only), which is a
  second reason not to serialize one here. The split is recorded in `open_question` instead.
- **`parent_id` — null.** PR-5: R1b never authors it; a per-template agent cannot see the shelf.
- **`finance.tax-filings`** — considered as a collision (a withholding election form looks
  tax-shaped). Rejected as a separate edge: the discriminator is identical to the
  `finance.payroll-received` one already written (a labelled pay/withholding table vs employment
  terms), and a second edge restating one signal is noise.
- **`identity.immigration-visa`** — considered, because a verification letter addressed to a
  consulate and a work-authorization form both touch it. Rejected in favour of the single
  `identity.core-documents` edge: the discriminating evidence I would write is the same one
  (whose purpose is to establish who a person is), and the immigration situation's own row is
  better placed to state the visa-specific side.
- **`academic.continuing-education` / `career.credentials-licenses`** — employer-paid training
  certificates sit near both. Rejected: a training-completion record inside an employment file is
  a *value* of the document-kind level, and `career.credentials-licenses` already owns the
  credential-record situation. Adding the edge would assert a seam I could not discriminate with
  evidence better than "which folder the person kept it in", which is not evidence.
- **`legal.practice-matter-file`** — an employment dispute file. Rejected: that is a lawyer's
  matter file about someone's employment, a different holder and a different situation; the
  `legal.leases-agreements` edge already carries the executed-agreement shape.
- **`photos.scanned-documents`** — a phone photo of a signed page. Rejected as an edge: that is a
  `media_type` question about the same document, handled by `00`'s screenshot/EXIF abstention rule
  which I encoded in `never_alone` and in the screenshot fixture.

Nine collisions were written, each with a fixture in `file_examples` that actually sits on the
seam. `academic.teaching` reciprocates an edge that already exists; the other eight will need
reciprocation by R1c or by the neighbours' own agents.

## NEEDS-JOSEPH (this node only)

- **NJ-EMP-1 · The employer key must be destination-eligible.** When D1's career deferral lifts,
  the key that carries the employer of record cannot be `our_firm` (authorship-side, never a
  destination) or `client` (counterparty role). `00` puts the company first as a folder level, so
  either a new destination-eligible key is minted or `00`'s recorded Career order cannot be built.
  This is the concrete constraint this row contributes to `career.json`'s open question.
- **NJ-EMP-2 · How the document-kind level is spelled.** Widen an existing enum's role across
  domains, or mint a career-scoped document-type key? Four scoped spellings of one concept is the
  574's failure mode; three already exist. Not resolved here.
- **NJ-EMP-3 · Own file vs a direct report's file.** This row provisionally splits the
  other-person case to `career.employer-side-hiring` and records the discriminator as a subject
  slot. If Joseph would rather keep a manager's personnel files in the same template, this row's
  privacy rules must become materially stronger than what is written — the material stops being
  the holder's own and becomes a third party's.
- **NJ-EMP-4 · Whether "employment period" is a level at all.** A tenure with promotions has
  several roles under one employer; a tenure with one role has none. The template currently
  recommends employer → role → document type with an explicit flatten-to-two option. If tenure
  (rather than role) is the level Joseph wants, that is a different proposed key again, and it is
  a filing-structure decision about someone's real working life, so I did not make it.

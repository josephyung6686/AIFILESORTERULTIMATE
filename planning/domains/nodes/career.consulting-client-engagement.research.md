# career.consulting-client-engagement — lab notes (R1b)

Roster row: `kind: template`, `schema_id: career`, `parent_id: null`, `launch: placeholder`,
`inherited_field_keys: []`, neighbours `finance` + `code`, residuals `Independent Records` +
`Review Later`.

Outcome: **built, not refused.** `refuse_node: false`.

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every quoted span in the node
  JSON was grep-matched against this file before it was written; the two spans that failed the
  check were removed rather than repaired into something plausible (see "Quotes I dropped").
- `planning/01-product-design-structured.md` — read only §3.7–3.8 (roles / conservative facet
  extraction), §5.4 and §5.7 (templates as controlled schemas; the template library), §7.2–7.3
  (residual library and its nine names). Used as a locator, never as authority; `00` wins.
- `planning/domains/_CONTRACT.md` — entry shape, rules 8, 10, 11–15.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/CONNECTION.md`,
  `planning/domains/CONNECTION-EXAMPLES.md` (fixtures 3, 5, 6 are the ones this node leans on).
- `planning/domains/roster.json` — confirmed my id, kind, schema_id, and that every edge target
  I wrote is a real roster id.
- `planning/domains/canonical_fields.json` — the whole table.
- `planning/domains/nodes/career.json` — the schema node this template points at. Aligned to it;
  did not rewrite it.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` (fourteen) and `RELIABILITY_STATES` (six).

Deferred catalogues: **not consulted.** This node's recognition needs an organization gazetteer
(R4's contents) and scope-of-work term patterns (R6's), and it names both as owed rather than
inventing either. No regex, no gazetteer member, no threshold is written anywhere in the node.

## Why this row survives the node test

The test refuses a template whose detection signals, dimension order and privacy rules are all
identical to its schema's default. Two of the three differ decisively here, and the two that
differ are the load-bearing ones:

- **Detection signals.** The career default situation (`career.recruiting`) reads documents
  *about the holder* — resume structure, offer language, interview terms. This situation reads a
  **two-organization role pair**: one org in a recipient position, a *different* org in a producer
  position, inside a scope-shaped document. That is a different rule family, not a different
  vocabulary, and `00` supplies it directly: "A consulting document may mention the author’s firm
  and the client organization."
- **Privacy rules.** Recruiting material is the holder's own. Engagement material is largely a
  third party's confidential work product held under a signed obligation, which changes what may
  enter a cloud dossier before it changes any folder.
- **Dimension order** differs only *in prose* (client-first with `our_firm` barred, against
  company-first). Both serialize empty today, so this ground is recorded and then explicitly not
  relied on.

## The empty `dimension_order` — deliberate, not a gap

`client` is a canonical key with `destination_eligible: true`. It was tempting to write
`dimension_order: ["client", "project"]` and have a template that looks finished. That would be a
**gate bypass**: `_CONTRACT` rule 12 (and CONNECTION §3.1) allow a dimension only on a field the
template's schema declares, and the career schema declares none under D1-as-narrowed / PR-6.
Serializing it would open a tree level no fact can fill — the 566-finding defect the contract
exists to stop. So `dimension_order: []`, with the full recommendation held as prose in
`template.why`, exactly as `career.json` does. R1c or P10 can restore it in one edit the moment
career's field rows land.

## The finding worth carrying forward

Three of the four concepts this situation needs **already exist as canonical keys with `design`
provenance**, which makes this template closer to buildable than the career default is:

| concept | canonical key | state |
|---|---|---|
| the client | `client` | exists; `destination_eligible: true`; `role_split_with: [our_firm]`; gazetteer `orgs` |
| the holder's own firm | `our_firm` | exists; `destination_eligible: false` — which is exactly right, see below |
| the engagement | `project` | exists; an engagement is a value, per `00`'s values rule |
| the document type | **none** | `work_type` is coursework, `record_type` is finance, `artifact_type` is research/code, `application_document_type` is admissions |

That fourth row is the same gap `career.json`'s `open_question` records from the recruiting side.
This node corroborates it from the consulting side and **mints nothing** — proposing a career-
scoped key here would reverse S3 as a side effect of a template row.

`our_firm` being destination-ineligible is the single most useful thing the canonical table does
for this node. The holder's own firm name is the *most* reliably extractable organization on these
files (letterhead, every page footer, producer metadata), and it is exactly the value that must
never become a level: `00` bars it as a field ("It should avoid using authorship or creator
identity as a destination dimension"), as a shape ("A folder should not become a collection point
for everything produced by the same person or organization."), and again in the validation rules
for generated templates ("use an author or organization merely as a collector").

## `proposed_fields`: empty, on purpose

No new canonical key is needed by this node. The role split it lives on is already in the table;
the engagement rides `project`; the document-type gap belongs to the career schema decision, not
to a template. Recorded in `open_question` instead.

## Files considered and rejected as examples

- **A pay statement / payslip.** Carries an employer name and employment context, so it looks like
  a career-adjacent trap — but it is `career.json`'s collision fixture already, and it is about
  employment, not an engagement. Replaced with the **invoice**, which is this node's real finance
  collision: same client name, same phase reference, often the same filename stem.
- **A résumé / CV.** Belongs to `career.recruiting`. A consulting engagement does produce
  bio/credentials pages, but they arrive inside a proposal, not as standalone résumés.
- **A timesheet.** Real, but its discriminating evidence is a labelled hours/rate grid, which is
  the bookkeeping neighbour's shape; including it would have argued for a collision the invoice
  already makes better. Kept as a `work_types` value only.
- **A `.vcf` for a client contact.** `00` keeps contact data "privacy-protected rather than used
  to create folder proposals", so it adds nothing this node can act on; `career.json` already
  carries that fixture.
- **A password-protected client data archive.** Would only have restated the
  Unsupported-or-Encrypted residual, which is not this node's fallthrough.

Kept, and why each earns its place: labelled SOW (labelled-form case) · unlabelled proposal draft
(prose case, plus the duplicate-suffix trap) · kickoff deck (the footer-is-authorship case) ·
client workbook (spreadsheet slots, and a filename token that must **not** become a client fact) ·
scope-change email (the cross-organization sender/recipient pair — the role split in its most
machine-readable form) · engagement ZIP (manifest without unpacking) · portal screenshot (OCR, and
the no-EXIF rule) · `Notes 3.docx` (the `HW 3` analogue) · invoice (finance collision) · downloaded
industry report (**the** false-positive fixture) · delivered analysis repo (code) · executed NDA
(legal) · recurring status `.ics` (calendar is a SOURCE_TYPE, not a domain).

## The never-alone that matters

A downloaded industry report published **by** a large consulting firm carries that firm's name in
the title, the letterhead, every page footer and the copyright line, plus scope, methodology and
deliverable vocabulary throughout — and it is reading material, not an engagement. `00` names the
exact failure: "Columbia can appear as an authoring school, course provider, target institution,
employer, research venue, or merely a cited organization." Here the firm is *merely a cited* —
indeed the publishing — organization. What is missing is the **role pair**: no second organization
stands in a recipient position. Its home is the Reading Inbox residual, which is why that residual
is on this node's `falls_through_to` even though the roster row did not list it.

## Neighbours considered that did NOT get an edge

- **`finance` / `code` as schema ids.** They are this row's `must_consider_neighbors`, but
  `collides_with` joins **same-kind** pairs (CONNECTION §5), and this row is a template. The
  collisions were therefore written against the *template* rows that actually hold the confusable
  evidence — `finance.small-business-bookkeeping` and `code.software-project` — which is the same
  neighbourhood, expressed legally.
- **`legal` (also-holds).** An executed MSA or NDA is genuinely both. But `also_holds_with` joins
  **schemas only**, and a template may not author it. Recorded in
  `file_examples[].also_schema` instead, and in `also_holds_note`. **Where the dispatch prompt's
  edge table and CONNECTION.md disagree on this, CONNECTION wins — noted as instructed.**
- **`career.employment-records`.** A contractor's engagement and an employee's job look adjacent
  from outside, but their documents share no confusable evidence item: employment records name one
  organization in an employer role with the holder inside it; an engagement names two organizations
  across a boundary. Adjacency is not a collision, and `related_to` does not exist.
- **`finance.cap-table-equity`.** An advisory engagement paid partly in equity touches it, but the
  discriminating evidence (a grant/valuation instrument) is unambiguous. No edge.
- **`research.*`.** A commissioned research report resembles a deliverable, but the research schema
  activates on project/venue/lab evidence that an engagement document does not carry. No edge.
- **A "creative agency work" node.** Does not exist on the roster;
  `career.portfolio-work-samples` owns `design_creative` per its `file_kind_owner`. This node
  therefore does **not** claim `design_creative` in `file_kinds`, and takes the collision with that
  sibling instead.

## Quotes I dropped rather than repair

1. I had written `00`'s five academic context terms inline with straight quotation marks. `00`
   uses curly quotation marks, so the span was **not verbatim**. Replaced with the verified
   fragment "a course-code pattern together with academic context" plus a plain statement that
   `00` lists the terms itself.
2. A scare-quoted phrase of my own in `open_question` was un-quoted, because a reader scanning for
   citations must never find quote marks around words `00` did not write.

Every remaining quoted span was matched against `00` by script. `00`'s curly apostrophes are
preserved where a quoted span contains one (`the author’s firm`).

## NEEDS-JOSEPH (this node only)

- **NJ-C1 · Does an engagement branch default to protected handling?** The material is largely a
  third party's confidential work product, and the holder is usually under a signed obligation
  about it — a stronger claim than a preference for privacy. Defaulting the situation to protected
  would suppress the very model interpretation this node depends on (assigning the two
  organizations to their roles is exactly what rules cannot do). Defaulting it to ordinary sends
  client material into cloud dossiers by policy. This is a decision about someone's real
  professional obligations, so it is recorded, not resolved. It is *not* a handling class — P7's
  vocabulary is untouched here.
- **NJ-C2 · The career document-type key** — restated in the node's `open_question` as
  corroboration of `career.json`'s existing question, from the consulting side, with the finding
  that three of the four needed concepts already exist canonically.
- **Not reopened:** CONNECTION's NJ-3 names "a consulting proposal packet" as the purpose-coherent
  packet outside admissions that no schema legitimises `purpose` for. PR-1 holds; this node mints
  no `purpose` clone and takes no position.

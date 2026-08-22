# career.recruiting — lab notes

Row: `kind: template`, `schema_id: career`, `launch: full`, `file_kind_owner: ["email"]`.
Result: **node stands** (`refuse_node: false`). No fields proposed.

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every span this node quotes was
  `grep -c -F` verified against it before it was written; twenty-eight spans checked, twenty-eight
  matched. No section numbers are asserted anywhere (00 has none).
- `planning/01-product-design-structured.md` — §5.4 only (the template/dimension table, which
  renders the Career line as `company → role or recruiting cycle → document type`), plus the
  locator grep that confirmed 00 and 01 agree on it. 00 wins everywhere; nothing was taken from 01
  that 00 does not also say.
- `planning/domains/_CONTRACT.md` (rules 5, 6, 8, 10–15), `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md` (§§1–7, PR-1, PR-6), `CONNECTION-EXAMPLES.md` (fixtures 1 and 5
  — the syllabus join and the `.ics` refusal).
- `planning/domains/roster.json` — confirmed id, kind, schema_id, neighbours, and the `email`
  ownership; every edge target checked against the roster's 83 node ids.
- `planning/domains/canonical_fields.json` — every key this row names resolves there.
- `planning/domains/nodes/career.json` (the parent schema row) and the six landed neighbour nodes
  that already point an edge at `career.recruiting`.

## The node test, applied honestly

The roster hint calls this "the Career default situation", and ALIGNMENT says a template that
would only repeat its schema's fields and dimension order **is not a node**. That is the refusal
this row had to survive, so the reasoning is recorded rather than assumed:

- **Dimensions do not distinguish it.** `dimension_order` is `[]` here and `[]` on the schema row,
  for the same contractual reason (PR-6 / D1: the career schema declares no fields, so no
  dimension may branch). Nothing was gained on this axis and nothing was invented to fake a gain.
- **Detection signals do distinguish it.** The schema row's signals are the *union* across all six
  career situations (resume shape, offer letterhead, recruiting mail, interview calendar, packet
  manifest). This row adds two that exist in no other career situation and could not sit on the
  union without being wrong there: the **saved job posting's labelled structure** (role title +
  responsibilities/qualifications/employment-type sections + requisition slot), and the
  **application-stage pair** (stage term in a high-weight zone + organization hit in the employer
  position), which is what separates a process still being decided from an employment relationship
  already in force.
- **Privacy rules distinguish it.** This is the row that owns `email`, and 00 attaches its caution
  to that extractor directly ("while treating addresses and message content as potentially
  sensitive"), plus the third-party contact rule ("should normally be privacy-protected rather than
  used to create folder proposals"). The schema row's sensitivity paragraph is about employment
  materials generally; this one is about other people's correspondence and about two forms
  (an offer awaiting countersignature, a background-check authorization) that carry compensation
  and a government identifier.

  Alignment note: `career.employment-records` landed mid-pass and authored the sharper version of
  our shared seam (unsigned offer = recruiting; countersigned = employment record). I adopted its
  discriminator verbatim in my reciprocal edge and renamed my fixture to
  `Offer letter - Deloitte.pdf` (awaiting countersignature) so the two rows point at two copies of
  one version family rather than fighting over one file.

Two of the three axes differ, which is what the node test asks for. Recorded so a merge reviewer
can disagree with the judgement rather than guess at it.

## Files considered and rejected

- `ADP Pay Statement Mar 2026.pdf` — already the schema row's collision fixture, and it belongs to
  `finance.payroll-received`. Kept as a *named fixture inside the collision signal* rather than as
  a twelfth file example, so the two rows point at one file instead of describing two.
- `recruiter.vcf` — the schema row already works it, and its answer is "activates nothing for
  placement". Repeating it here would have added a `contacts` source_type to this template's
  `file_kinds` that must never fire, which is the opposite of useful.
- `LinkedIn export/` (a folder of CSVs) — rejected: it is a platform export, and the interesting
  facts in it are contact data that 00 keeps out of folder proposals entirely.
- `Resume.pdf` in isolation — rejected as an *example* because it carries no recruiting evidence
  at all; it survives as the never-alone rule ("a resume LISTS employers; it belongs to none of
  them"), which is where it does real work.
- `Salary research - levels.xlsx` — rejected: a spreadsheet of market pay is reading/reference
  material with no process anchor. `spreadsheet` stays in `file_kinds` (offer comparison sheets are
  real) without a worked example, since I could not make one whose facts differ from the
  posting's.
- Job-search tracker spreadsheets — genuinely common, genuinely a file people keep, but the
  organizational question they raise is "does a tracker belong inside the process branch or above
  it", which is P10's and would have been a folder-shaped claim in a fact row.

## proposed_fields — deliberately empty, and why

The obvious three (`company`/employer, role-or-cycle, document type) are exactly what 00's Career
template line names, and it would have been easy to propose them. I did not, for three reasons:

1. **D1 as narrowed forbids career field rows**, and CONNECTION PR-6 holds this template's
   recommendation "as prose until the schema lands". Career fields are owed *before P10*; adding
   one from a template row would be reversing S3 as a side effect of a per-node research pass.
2. **The parent schema row already filed the question** and named the hard part: reuse is not
   obviously safe, because `institution` is scoped to a finance record issuer, `client` is the
   counterparty half of the `our_firm` role split rather than an employer of record, and
   `application_cycle` is an admissions cycle. A template proposing keys under the schema that
   declined to would create exactly the two-vocabularies defect D6 exists to kill.
3. **This row found a fourth complication worth recording rather than resolving**: 00 writes the
   middle level as a disjunction ("role or recruiting cycle"), and those are not one field. That is
   in `open_question`, not in `proposed_fields`, because it is a decision about the product's
   shared vocabulary.

Consequence, stated plainly: every `facts_legal` list in this row's file examples contains only
universal fields, or fields of a *different* schema that activates on its own disjoint evidence
(academic on the transcript, finance on the payslip fixture, identity on the background-check
form). That is not padding around a hole — it is what a field-less placeholder schema actually
legitimises today, and the row says so on every example.

## Neighbours considered that did NOT get an edge

- **`career` (the schema)** — the `uses_schema` join is the roster's `schema_id`, not an authored
  edge, and `collides_with` joins same-kind pairs only.
- **`also_holds_with` anywhere** — CONNECTION §5: it joins **schemas only**. The career schema row
  already authors the real ones (college_applications, academic, legal). At file level the same
  truth appears as `also_schema` on `Official Transcript.pdf`, `CV_2026.pdf`,
  `Offer letter - Deloitte.pdf`, `Take-home - data challenge.zip` and
  `Background check authorization.pdf`. Every landed template node has `also_holds_with: []`;
  this one matches.
- **`academic.transcripts-credentials`** — a transcript inside a recruiting packet is the
  also-holds case, not a collision: both fact sets stand on disjoint evidence. That row already
  collides with `career.credentials-licenses`, which is the genuine confusion (a certificate that
  is a credential versus a course record), and it is not mine to reciprocate.
- **`career.consulting-client-engagement`** — considered and dropped. A proposal or SOW and a
  cover letter are both persuasive documents addressed to an organization, but the discriminator
  (`our_firm` vs `client`, an engagement already won) is clean enough that no single evidence item
  realistically supports both. Adding the edge would have been decorative.
- **`career.portfolio-work-samples`** — a work sample attached to an application is a shared
  document, not a mutex. Its home is a multi-membership question (00: "a resume may support
  multiple recruiting processes"), which is P9's, not an edge here.
- **`finance.receipts-expenses`** — interview travel receipts route to `travel.bookings-
  confirmations`, which I did author; adding the expense row too would have split one seam across
  two edges.
- **`identity.core-documents`** — the background-check form touches it, but the routing that
  matters is `falls_through_to: Protected Records`, which is authored. A collision edge would have
  claimed the two rows compete for the same file, and they do not: protection runs first.
- **`legal.leases-agreements`** — an employment agreement is legal material, but that is the
  schema-level `also_holds_with` the career row already carries; a template-to-template collision
  would misdescribe it as a mutex.

## Notes on discipline

- No regex, no gazetteer contents, no numeric threshold, no confidence score, no handling class
  appears anywhere in the node. Where context terms are named, they are marked **PROPOSED** and
  the row says plainly that 00 states the pattern-plus-context *shape* only for course codes.
- `Interview prep - behavioral questions.docx` is this situation's `HW 3.pdf`: it carries
  `group_without_copying_facts: true` and an explicit `must_not_conclude` against borrowing an
  employer from its retrieval neighbours, quoting 00's firewall sentence.
- No file example writes a folder path as a fact; five say so explicitly.
- Where the dispatch prompt and CONNECTION.md could be read as disagreeing — the prompt lists
  `also_holds_with` as an edge this row may write, CONNECTION restricts it to schema↔schema —
  **CONNECTION wins** and the field is empty. Noted here as the prompt requires.

## NEEDS-JOSEPH (this node only)

1. **The middle dimension is a disjunction, not a field.** 00: "a Career template may define
   company → role or recruiting cycle → document type". *Role* and *recruiting cycle* build
   different trees from the same facts — role suits one company running several processes, cycle
   suits one person running a search season. Two keys with an optional level, or one key whose
   values are process labels?
2. **What is the branch unit — the company, or the process?** 00's group label names the process
   ("a career packet EY Internship Application"); 00's template line names company first. A real
   job search makes most companies one-child branches, and 00 itself warns the interface to "warn
   when a level produces only one child". This decides the default shape of someone's real
   job-search folder, so it is not mine.
3. **Inherited, and blocking:** which canonical keys the employer / role-or-cycle / document-type
   concepts get when S3/D1's deferral lifts (owed before P10). Until then this template's
   `dimension_order` is empty by contract, and its file examples can legitimise universal facts
   only.

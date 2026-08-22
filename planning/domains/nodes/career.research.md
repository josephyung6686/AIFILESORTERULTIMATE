# career — lab notes (R1b, `kind: schema`)

Node: `planning/domains/nodes/career.json`. Roster row: `career`, `kind: schema`, `launch: full`,
`inherited_field_keys: []`.

## Sources used

- `planning/00-database-agent-product-design.md` — read in full. Every quotation in the node was
  `grep -c -F` verified against this file before it was written. The career-bearing spans are:
  the launch-domain sentence ("academic coursework, college applications, research and lab work,
  career and recruiting, photos and captures, and code projects"), the template sentence
  ("a Career template may define company → role or recruiting cycle → document type"), the group
  label ("a career packet EY Internship Application"), the LLM's allowed determinations
  ("recruiting document"), the shared-material sentence ("a resume may support multiple recruiting
  processes"), the adversarial-suite entry ("shared resumes across applications"), the coherence
  question ("one course, project, application, recruiting process, photo event, or submission
  packet"), and the privacy corpus list ("employment materials").
- `planning/01-product-design-structured.md` — only §3.15 (launch scope) and §5.4 (the template
  dimension table, where the Career row reads `company → role or recruiting cycle → document
  type`). Locators only; `00` is what is quoted.
- `planning/domains/_CONTRACT.md` (rules 5, 6, 8, 10, 11, 14, 15), `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md` (§2 node test, §4 activation, §5 edge vocabulary, PR-1, PR-6),
  `planning/domains/CONNECTION-EXAMPLES.md` (fixtures 3, 5, 6, 8 are the ones that bite here),
  `planning/domains/roster.json`, `planning/domains/canonical_fields.json`,
  `src/evidence_shape/vocabulary.py` (`SOURCE_TYPES`).
- No neighbour node file existed under `planning/domains/nodes/` when this was written (the
  directory was empty), so every edge names a roster id and nothing was aligned against a landed
  neighbour. R1c owns reciprocity.

## Why this node is not refused

The node test refuses a `kind: schema` row that cannot name a distinct 3–6 field set. This row
names **zero** fields — but not because the domain collapses into a neighbour. It is field-less by
a recorded decision: `_CONTRACT` rule 10 (D1 as narrowed) forbids career field rows, rule 15
explicitly permits `schema: []` on exactly this row, and CONNECTION PR-6 names career among the
placeholder schemas whose dimension recommendation is "held as prose until the schema lands".
`00` names career and recruiting as a launch domain and gives it template dimensions that are not
academic, application, research, photo, code or finance fields. Refusing the id would delete a
launch domain of `00`, and `00` wins over the prompt. So: `refuse_node: false`, and the row does
the work a placeholder can honestly do — detection signals, file examples, values, grouping
reasons, edges, sensitivity — while writing no field rows and no `proposed_fields`.

**The consequence worth stating loudly for R1c/P6/P10:** because the allow-list is a union over
active schemas' fields (CONNECTION §3), activating `career` today legitimises the **universal
facts only**. Every file example's `facts_legal` reflects that — the career column is empty, and
the only canonical keys that appear come from a co-active neighbour (`school`/`term`/`subject` on
the transcript, `institution`/`record_type`/`tax_year` on the pay statement, and the
college-applications keys on a shared resume). A career file is currently recognisable, groupable,
and un-describable. That is exactly why the field rows are owed before P10.

## `launch: full` vs "placeholder schema"

Kept `full`, matching the roster row and the ASSIGNMENT. These are two axes, and conflating them
would misreport the domain: `launch` is `00`'s release-scope flag (career and recruiting is on the
fully-supported list), while "placeholder" in the roster's `one_line_hint` and in PR-6 describes
the D1 deferral of the **field rows**. The dispatch prompt's "Placeholder launch: still write
detection signals + recommended dimensions" is honoured anyway — the signals are written, and the
dimensions are written as prose in `template.why` rather than as `dimension_order`, because a
dimension may only branch on a declared field (rule 8, second half). An array there would open a
tree level no fact could ever fill, which is the 566-finding defect the contract was tightened to
stop.

## Files considered and rejected

- **`linkedin_connections.csv` / a profile export archive.** Rejected as an example: the useful
  facts in it are other people's contact rows, which `00` keeps privacy-protected rather than a
  proposal basis, and the file would have taught nothing the `.vcf` example does not.
- **A photographed conference badge / business card (HEIC).** Rejected: the interesting question in
  it is photo-vs-scan media typing, which belongs to the photos node, not here.
- **A job-search tracker spreadsheet.** Kept `spreadsheet` in `file_kinds` (labelled column headers
  like Company / Role / Status are real evidence) but not written as an example — its facts would be
  about many processes at once, and a per-file fact row is the wrong shape for it. Flagged here
  because R1c may want it on the `career.recruiting` template instead.
- **A performance review and a separation letter.** Left as `work_types` values only; they are the
  `career.employment-records` template's territory, and this row must not pre-empt its sibling.
- **`.vcf` was deliberately kept as an example but deliberately left OUT of
  `file_kinds.source_types`.** It is the case that must *not* activate. Listing `contacts` as
  plausible would have contradicted `00` ("should normally be privacy-protected rather than used to
  create folder proposals") and CONNECTION-EXAMPLES fixture 6.

## `proposed_fields` justification

**None proposed, deliberately.** Naming `company`, `role`, `recruiting_cycle` or
`career_document_type` as `proposed_fields` would be writing the career field rows through the side
door — `_CONTRACT` rule 10 says adding one earlier "is reversing S3 and must say so explicitly
rather than arriving as a plan edit", and a swarm node is not the place to say so. The three
concepts are recorded as prose in `template.why` and as the node's `open_question`, which is what
PR-6 itself does with the same three words.

The substance R1c should carry into that decision, recorded once here: reusing an existing key for
the employer is not obviously safe. `institution` is scoped by its canonical `role` to a
financial/record-issuing institution; `client` is the counterparty half of the `our_firm ↔ client`
role split (an engagement counterparty, not an employer of record); `application_cycle` is an
admissions cycle by its `00` sentence. A recruiting process at an employer is a fourth role for the
same entity type — which is precisely the situation §3.8's role-split mechanism exists for, and it
is a vocabulary decision, not a node's.

## `role_split: []` — why empty

The career-side split (employer of record vs prospective employer vs the client organization an
engagement serves) cannot be authored: `role_split` joins **field keys**, and career has none. The
half that already exists is canonical and untouched here — `our_firm ↔ client`, which the
`career.consulting-client-engagement` template rides on. When the career field rows land, the
employer key almost certainly needs a `role_split` against `client` and against `school`; recording
that as an edge today would mean inventing the key first.

## Neighbours considered that did not get an edge

- **`identity`** — a passport scan or work-authorisation document genuinely travels inside an
  onboarding packet. No edge: identity is a safety schema whose activation unlocks protection plus
  its own field-less schema (PR-2), and a career↔identity `also_holds_with` would suggest the
  packet reading can pull an identity document into a career branch. `00` already routes that file
  by its own evidence. Left for R1c if the onboarding template asks for it.
- **`research`** — a portfolio case study can restate research work. No edge from this row: the
  overlap lives on `career.portfolio-work-samples`, which is where the purpose-vs-source
  distinction is the whole point. A schema-level edge would over-claim.
- **`code`** — same reasoning; a take-home coding exercise is the `career.recruiting` template's
  problem, not the schema's.
- **`photos`** — collides only through the screenshot, and that is handled by the never-alone rule
  plus the `Temporary Screenshots` fallthrough, not by an edge.
- **`Protected Records` as a node-level `falls_through_to`** — deliberately not added, even though
  the `.vcf` example names it. That fallthrough is the privacy path (PR-4, safety-activated files),
  not "career did not fire". Career is not a safety domain, and claiming that residual would put
  P7's job on this row. `Temporary Screenshots` *was* added, because a job-portal screenshot that
  fails to fire genuinely lands there.

## Two prompt/CONNECTION disagreements, resolved CONNECTION's way

1. The dispatch prompt says a placeholder should still write "recommended dimensions"; CONNECTION
   PR-6 and `_CONTRACT` rule 8 say a dimension may only name a declared field. Resolved as prose in
   `template.why`, `dimension_order: []`. Noted per the prompt's own tie-break rule.
2. The prompt says `kind: schema` "fills `fields`"; `_CONTRACT` rule 15 says a placeholder schema
   may carry an empty list. Rule 15 wins and names career explicitly.

## Context terms are PROPOSED, not `00`'s

`00` gives a design floor of context terms for **course codes** only ("syllabus", "lecture",
"credits", "instructor", "semester"). Every career-side context term in `recognition` (offer,
acceptance, start date, interview, requisition, resume/CV headings) is marked PROPOSED in the
signal text itself. This row writes no regex, no gazetteer contents, and no term list as if `00`
had published one — R2, R4 and R6 own those.

## NEEDS-JOSEPH (this node only)

- **NJ-career-1 · The owed field keys.** Which canonical keys the career schema gets, and whether
  the employer / role-or-cycle / document-type concepts reuse `institution`, `client`,
  `application_cycle`, `work_type` and `record_type` or need new keys with role splits. This is the
  node's `open_question` and it blocks P10, because `00`'s Career template dimensions cannot become
  a branch order until a fact can fill them. Nothing else in this row depends on the answer.
- **NJ-career-2 · Does the offer-letter compensation figure make employment material
  protected-by-default?** `00` puts "employment materials" in the same sensitive-corpus sentence as
  account statements, and its Protected Records residual covers "account statements". This row
  asserts only `potentially_sensitive` (the contract's two-value vocabulary) and sets no handling
  class — but whether an offer letter or a signed agreement enters the protected state at detection,
  the way a passport does, is P7's call and is currently unstated. It changes whether
  `career.employment-records` may ever be a cloud dossier.

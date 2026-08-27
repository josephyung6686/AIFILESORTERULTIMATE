# Research memo — `nonprofit.volunteer-management`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/nonprofit.volunteer-management.json`
Roster row: template on the fieldless `nonprofit` schema, `parent_id: null`, placeholder launch

## Result

**REFUSED.** The row fails all three legs of CONNECTION §2's template test against its own schema,
and it fails them on the schema's own text rather than on an argument I had to construct. The
coverage is real, is already owned, and is routed below by name.

The single most damaging fact I found is not an argument at all. The best file this template could
possibly name — `Volunteer rota - summer 2026.xlsx` — is already sitting in
`nonprofit.json`'s own `file_examples`, worked through there as an illustration of the schema's
default behaviour. A template whose strongest fixture is its schema's demonstration that no such
template is needed has nothing left to be.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (full).
- The stamped assignment from `make_prompt.py nonprofit.volunteer-management`.
- `planning/domains/nodes/nonprofit.json` — my schema anchor, read in full. It is the primary
  evidence for the refusal.
- `planning/domains/CONNECTION.md` §2 — the node test, read in full.
- `planning/00-database-agent-product-design.md` — reached by targeted grep only, per the token
  instruction. Every span quoted in the JSON and here was extracted verbatim from `00` by a script
  that printed the whole sentence around each match; none is paraphrased.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — one landed launch row, read
  for depth calibration.
- One grep for landed rows naming me: `nonprofit.religious-institution` (JSON + memo),
  `nonprofit.political-campaign` (JSON + memo), `government.parks-public-lands` (memo). Read only
  the matched lines.

I did not read `01`, the other nonprofit siblings, or any row not returned by that grep.

## The charge, stated at its strongest

Before writing anything I put the case against the row as hard as I could. It came out in five
forms, and three of them are fatal.

**1. It is a row defined by the ABSENCE of something.** The proposed discriminator that separates a
volunteer packet from an `hr` packet is: no gross pay, no tax code, no deduction lines. My schema
anchor states this in its own deterministic signal 8 and then concedes the weakness in its
`collides_with` for `hr`: *"The discriminating evidence is payroll structure and it is largely an
ABSENCE… An absence is weak evidence."* Its open question NJ-NP-4 goes further and pre-judges this
row: *"Volunteer-programme is WEAK because its discriminator is an absence of payroll structure."*
An absence cannot be cited to a user in an explanation, cannot be quoted back as evidence, and is
indistinguishable from a payroll workbook whose deduction sheet was not exported. `00`'s rule bites
directly: **"A model that cannot cite sufficient evidence must return unknown."** The asymmetry the
schema already states is the whole of the useful rule and it runs one way only — any gross-to-net
structure makes the file `hr`; no absence anywhere makes a file mine.

**2. It is a duplicate of its own schema's default template.** This is the leg that ends the
argument. `nonprofit.json`'s default `recognition.deterministic` list contains, as item eight, *"A
VOLUNTEER-PROGRAMME structure: a volunteer agreement whose own clauses state that it is NOT a
contract of employment and creates no binding obligation, held together with a rota or shift roster
of named volunteers, an induction or training record, and an out-of-pocket expense claim with no
gross pay, no tax code and no deduction lines."* That is the entire content this template was
commissioned to research, already declared as the schema's default. There is no signal I could add.
CONNECTION §2 names the consequence: *"a template that would only repeat its schema's fields and
dimension order **is not a node** — it is the schema's default template."*

**3. It is a value, not a node.** Strip the word *volunteer* from every fixture I assembled and each
one lands unambiguously somewhere else — a role description becomes a job description (`hr`), an
application-and-references packet becomes recruitment (`hr`), a rota becomes a staff roster (`hr`),
a disclosure certificate becomes an identity document (`identity.core-documents`) or a safeguarding
check (the schema's own signal). *Volunteer* is occupying an employment-type or role slot.
CONNECTION §2's value row is explicit that runtime-created things cannot be hand-authored roster
rows.

**4. Duplicate of a neighbour.** `hr` already owns the recruit → check → induct → train → schedule →
reimburse → recognise lifecycle. This row is that lifecycle with one noun changed.

**5. A lifecycle stage.** Weaker but worth stating: "recruiting, checking, deploying and supporting"
is a sequence of stages within a relationship, and stages are `work_type` values.

### Attempts to defeat the charge, and why each failed

I did not refuse on the first pass. I looked for a positive structure with no home, and found four
candidates.

- **The non-employment clause.** *"This agreement is binding in honour only and is not a contract of
  employment"* is a real clause in real model agreements (NCVO's model volunteer agreement,
  Volunteering Australia's), and it is a *positive* textual structure, not an absence. This is the
  strongest thing the row has. It fails anyway, because the clause is the schema's own signal 8,
  written out there verbatim. A positive clause is real evidence and it activates the **schema**; it
  does not create a second node under that schema which recognises the same clause a second time.
- **The vetting record.** A disclosure certificate, barred-list check or working-with-children check
  looked distinctive. The schema had already taken it: its safeguarding signal names *"a
  background-check or barred-list record tied to a named person and a role."* And the position line
  on the certificate reads volunteer, employee, contractor or trustee with no change of structure.
- **The three-party hours ledger.** Court-ordered community service and school service-hour logs
  (CAS, President's Volunteer Service Award) have a genuine third party — a court, a school, an
  award body — certifying hours through a supervisor. This is the only structurally novel thing I
  found, and it routes *away*: in both cases labour is given in exchange for discharge of a sentence
  or a graduation credit, which fails the nonprofit schema's own NON-EXCHANGE precondition outright.
  It belongs to `legal`/`government` and to the education family respectively.
- **A volunteer-first dimension order.** The only order that would differ from the schema's is one
  that puts the named individual at a level, and the schema forbids exactly that: a named third
  party may never be a folder level, because a path writes their identity where every later process
  reads it — against **"The default posture must therefore be local-first and data-minimizing."**

## The node test, all three legs

**Leg 1 — detection signals.** *Fails.* The schema's default deterministic list already contains
this row's entire signal set, item 8, in full sentences. My signals would be a verbatim subset. This
is not a near miss; it is a copy.

**Leg 2 — recommended dimensions.** *Fails.* `dimension_order` is `[]` here because the schema
declares no fields under PR-6, as it is for every template in this family — that much is shared and
proves nothing either way. The test therefore has to run on the *prose* recommendation, and the
schema's prose is: the association, then the non-exchange counterparty or fund, then the period,
then the document function. Mine would be: the association, then the volunteer (forbidden — see
above), then the period, then the document function. Remove the forbidden level and my
recommendation is the schema's sentence with the counterparty slot filled by a value. Identical.
Neither is time-first; a volunteer programme's periods are content periods, never capture dates.

**Leg 3 — privacy rules.** *Fails, and this one surprised me.* The material genuinely is exposing —
a rota is a list of named third parties with availability and often phone numbers; a reference is
one person's written opinion of another; a self-declaration of unspent convictions is among the most
protected things a small association holds. But a template earns a node on privacy only by being
**stricter** than its schema's default, and the schema is already at `potentially_sensitive` — the
strictest value available at this row — with a `sensitivity_why` that names volunteer files
explicitly. Worse for the row: the schema's posture was argued for a *safeguarded child*, a *service
user*, a person disclosing under need. A volunteer is an adult who chose the relationship. My
posture is the same or looser, never stricter.

Three legs, three failures. Refusal is not a judgement call here.

## Files considered and rejected

Twelve fixtures are in the JSON with full observations. What each one was tempting *as*, and why it
is not this row's evidence:

1. `Volunteer rota - summer 2026.xlsx` — the strongest candidate, and it is my schema's own worked
   example. Dispositive.
2. `Volunteer agreement - Sam Okoro - signed 2026-03-04.pdf` — the non-employment clause; the
   schema's signal 8.
3. `Volunteer role description - Befriending Volunteer.docx` — a job description. `hr` recruitment.
4. `Volunteer application form and reference request.pdf` — `hr` recruitment, and
   `applications.scholarship-fellowship`'s individual-applicant shape at once.
5. `Disclosure certificate - 001234567890.pdf` — the schema's safeguarding signal on the association
   side, `identity.core-documents` on the subject's side.
6. `Volunteer expenses claim - mileage - March 2026.pdf` — **not even nonprofit.** A reimbursement is
   repayment of a cost actually incurred: value for value, so the schema's non-exchange precondition
   is not met at all. `Receipts and Confirmations` or `finance`.
7. `Certificate of appreciation - 200 hours.pdf` — the legacy `pers.volunteering` coverage. Excluded
   from this schema by role (see below). `Independent Records`.
8. `Casual staff rota - summer 2026.xlsx` — the collision fixture. See below.
9. `Sunday service rota - Advent 2026.xlsx` — `nonprofit.religious-institution`, by its rite column.
10. `CAS hours log - Spring 2026.xlsx` — unpaid hours in exchange for a graduation credit; fails the
    non-exchange precondition. Education family.
11. `Volunteer programme 2026 - handover.zip` — a coordinator's directory name is not a fact schema.
    The manifest, inspected without unpacking, reveals a *mixture* whose members route separately.
12. `Task day - Compartment 12 coppicing.ics` — `government.parks-public-lands`' own fixture.

## The collision fixture

`Casual staff rota - summer 2026.xlsx` sitting in the same folder as `Volunteer rota - summer
2026.xlsx`. Same association letterhead, same charity number in the footer, same visible sheet: one
row per named person, one column per dated shift, a role column. The staff file carries a hidden
sheet with hourly rate, gross, tax code and net; the volunteer file does not.

**What discriminates them:** the presence of a gross-to-net structure in one of them — and *only*
its presence. If that sheet had been dropped on export the two files would be indistinguishable, and
the product would have no evidence to cite for either verdict. That is the refusal in one folder.
`hr` owns the first outright. The nonprofit schema's default owns the second. There is no third
thing for a volunteer-management template to be.

## Reciprocal boundaries

Five are authored in `collides_with`, every one as an object naming the same fixture on both sides.

- **`nonprofit` (my own schema)** — `Volunteer rota - summer 2026.xlsx`. Not a collision so much as
  the refusal itself: the schema's file, the schema's signal 8, the schema's default template.
- **`hr`** — `Volunteer rota` against `Casual staff rota`. `hr` cites a payroll structure; this row
  cites its absence. One-directional rule survives the refusal: payroll anywhere ⇒ `hr`, and `hr`'s
  privacy posture governs.
- **`nonprofit.religious-institution`** — `Sunday service rota - Advent 2026.xlsx`. That landed row
  owns it by the rite/occasion column. **Reciprocal direction, from its own text:** a rota with
  names and shifts and no rite column is *"nonprofit.volunteer-management or hr"* — a pointer that
  now dangles. See NJ-VM-1.
- **`government.parks-public-lands`** — `Task day - Compartment 12 coppicing.ics`. That row's memo
  records it *"nearly authored an eighth collision"* against me and declined, on the owner-role test
  (public authority managing its own land vs a private association). The refusal confirms its
  judgement and cancels the reciprocal it offered R1c.
- **`identity.core-documents`** — `Disclosure certificate`. Discriminated by whose filesystem holds
  it, not by the certificate, which is byte-identical in both hands.

## Neighbours considered that got no edge

- **`business_operations`** — the schema already fights this war at schema level and concedes most
  of it. Repeating it at template level would inflate the row without adding a decision.
- **`finance`** — reached only through the expense claim, which is `Receipts and Confirmations`
  first; a claim is a transaction, not a relation, so there is nothing here to confuse.
- **`nonprofit.member-association` / `nonprofit.governance`** — a volunteer is not a member and not a
  trustee; the register and the board structures are theirs and do not overlap a rota.
- **`nonprofit.political-campaign`** — refused itself, and it routed canvasser rotas *to* this row
  while noting in the same breath that this row is weak. Two refused rows cannot hold each other up.
- **`clinical_practice`** — a volunteer befriender's contact note looks like a case note, but the
  file that matters there is about the *beneficiary*, which is the schema's beneficiary structure,
  not a volunteer-management artefact.

## `also_holds_with` — empty, deliberately

`also_holds_with` is schema ↔ schema only (CONNECTION §5) and this row is a template, so it is `[]`.
The intent is recorded here for R1c instead: the co-activations that would have been worth stating —
`nonprofit` ↔ `hr` on a combined staff-and-volunteer rota, and `nonprofit` ↔ `identity` on a
disclosure certificate held by its subject — belong on the `nonprofit` schema row, which already
carries the `hr` one. Nothing is owed by this row.

## Proposed fields

`fields: []` and `proposed_fields: []`. The schema anchor owns the fields and declares none under
PR-6. I considered and rejected minting anything: a `volunteer_role` key would be a synonym of the
`work_type`/role slot `hr` already needs, and `hours` would be a quantity, not a destination-eligible
fact. A refused row must not leave a field proposal behind for R1c to adjudicate on behalf of a node
that does not exist.

## Where the coverage goes

Routed by name, so nothing is lost by the refusal:

| Artefact | Home |
|---|---|
| Volunteer agreement, rota, induction, hours, recognition — **association side** | `nonprofit` schema default (its own signal 8) |
| Anything with a gross-to-net line; role descriptions, applications, references, training records | `hr` |
| Background checks, barred-list records, safeguarding concerns | `nonprofit` schema safeguarding signal; `identity.core-documents` on the subject's side |
| Expense claims, reimbursements, sign-up confirmations | `Receipts and Confirmations` / `finance` |
| Legacy `pers.volunteering` — certificate, hours log, reference, thank-you (**individual side**) | `Independent Records` |
| Isolated named-person lists, references, conviction declarations | `Protected Records` |
| Rota or agreement whose side or paid status is unresolved | `Review Later` |
| Model agreements, sector toolkits, good-practice guidance | `Reading Inbox` |

The `pers.volunteering` routing deserves its own sentence because the roster hint folds it in here.
The nonprofit schema is the **association's** side and excludes giver-side copies by role — its own
words, about donations: *"A donor-side receipt held by the giver is finance and is excluded by
role."* A volunteer's certificate is the identical structure on the identical seam. It is the
individual's record, it has a durable purpose and no group, and `00` names its home: **"Independent
Records may live under Personal/Independent Records and hold standalone certificates, notices,
confirmations, forms, and PDFs that have a durable purpose but no broader group."**

Refusing is the correct disposition rather than a loss, on `00`'s own standard: **"Correct abstention
is a successful outcome because the product's goal is reliable organization, not maximum file
movement."**

## NEEDS-JOSEPH

**NJ-VM-1 — two landed rows now point at a refused id.**
`nonprofit.religious-institution` routes a rite-less rota to *"nonprofit.volunteer-management or
hr"*; `nonprofit.political-campaign` routes canvasser rotas here. Both pointers dangle.
*Alternatives:* (a) R1c redirects both to `hr`-or-schema-default, which is what this refusal implies
and what I believe correct; (b) R1c resurrects the row, in which case both pointers stand and this
refusal must be reversed with an argument that answers the absence-discriminator problem — which I
could not construct. I edited neither neighbour.

**NJ-VM-2 — the legacy id `pers.volunteering` has no owner after this.**
The roster hint folds an *individual's* volunteering record into an *association-side* row, and the
two sides cannot share a node. *Alternatives:* (a) accept residual routing to `Independent Records`
plus the career family where an award reaches a CV — what this refusal does; (b) if R1c judges that
an individual's accumulated volunteering record is a genuine filing world, it belongs on a
**personal** schema, proposed there as a new row, not salvaged onto `nonprofit`. I take no position
beyond noting (b) is a new-row question, not a rescue of this id.

**NJ-VM-3 — the absence-discriminator problem is general, and this row should be its precedent.**
Unpaid-vs-paid is not the only seam in the roster whose discriminator is a missing structure; the
shape recurs wherever a family is defined by what a document does *not* contain. *Alternatives:* (a)
rule such rows inadmissible unless positive evidence is named that stands in for the absence — my
recommendation; (b) admit them with an explicit weak-evidence marker, which would require a
mechanism P6 does not have. Until R1c decides, treat this refusal as the precedent.

## Self-verification

- `python3 -m json.tool` parses the JSON. Key set matches the landed sibling shape from the stamped
  prompt.
- Every `00` span quoted here and in the JSON was extracted verbatim by script from
  `planning/00-database-agent-product-design.md`; each matched exactly once. No fabricated quotes.
- Every `file_examples.source_type` is in `SOURCE_TYPES` (`text_document`, `spreadsheet`, `archive`,
  `calendar`).
- Every edge id exists on the roster: `nonprofit`, `hr`, `nonprofit.religious-institution`,
  `government.parks-public-lands`, `identity.core-documents`. Every `falls_through_to` names one of
  `00`'s nine residuals.
- Every `collides_with` entry is an object with `domain`, `signal`, `provenance`, and every signal
  names the same fixture on both sides. `also_holds_with` is empty (template row, CONNECTION §5).
- No threshold numbers, no handling classes, no `design_cite`, no folder path written as a fact.
- I wrote only my two assigned files.

# Research memo — `nonprofit.member-association`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/nonprofit.member-association.json`
Roster row: template on the fieldless `nonprofit` schema, `parent_id: null`, `launch: placeholder`
Absorbed legacy id: `acad.student-organization` (ROSTER.md Appendix A, line 375)

## Result

**Accepted, narrowly, and with its weakest leg left standing as NJ-MA-1.**

The row owns one thing: **the record whose row unit is a person's STANDING IN THE BODY**, and the
instrument by which those persons act collectively. Concretely — the roll or register (number, class,
join date, lapse date, subscription status, voting eligibility), the subscription run made across it,
the members' general meeting and its notice, resolutions, proxies, ballot and scrutineer return, and
the affiliation record where the member is itself an organisation.

It does not own the association's constitution, its board, its budget, its policies, its regulator
returns, its gifts, its grants, its beneficiaries, its volunteers or its rites. Those are landed
elsewhere and the row cedes each of them by name.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the stamped assignment.
- `planning/00-database-agent-product-design.md` — reached by targeted `grep -F` only. Every quotation
  in the JSON was verified with `grep -c -F` before it was written; all returned 1. One draft quote
  returned **0** — *"Correct abstention is a successful outcome because the product's goal…"*, a
  straight apostrophe where `00` has a curly one — and was cut back to the span that verifies. That is
  the reason to run the check rather than trust the neighbour that quoted it.
- `planning/domains/nodes/nonprofit.json` — the schema anchor, read in full; its eleven deterministic
  structures, its default-template prose and its privacy paragraph are what this row is measured
  against.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — one landed launch row, for depth.
- The eight landed rows that already name this row in a `collides_with` signal, read as signal text
  only: `nonprofit.fundraising-donor`, `nonprofit.religious-institution`, `nonprofit.political-campaign`,
  `government.professional-regulator`, `government.elections-administration`,
  `government.public-consultation`, `government.parks-public-lands`, `government.defence-veterans`.
- `planning/domains/roster.json` for the eleven `nonprofit.*` rows and every neighbour id used.

`00` says **nothing** about membership, subscriptions or registers of members — both greps returned
empty. Every substantive claim below is therefore marked `inference`; `00` is quoted only for the
rules the row obeys (residuals, collector levels, dimension order, abstention, archives, privacy).

## THE CHARGE — the strongest case that this row should not exist

Stated at full strength first, because four of the five sub-charges are conceded in part and one of
them may yet kill the row.

**(a) It is an organisation type, which the schema names as a forbidden sole activator.**
"Member association" describes a *kind of body*, not a *kind of record*. Every association the
`nonprofit` schema recognises — charity, union, church, club, institute, federation — has members.
A row named after that universal property is the schema wearing a hat. This is exactly the reasoning
that produced the landed refusal at `nonprofit.political-campaign`: *"the only proposed difference is
that the association is a party, an organisation type the schema names as a forbidden sole
activator."*

**(b) The subtraction argument, run on the roster name.** The roster row is named *"Student
organisations and clubs"* and its hint is *"officer records, events, budgets and recognition
paperwork."* Subtract what already has an owner: a club constitution → `nonprofit.governance`; a club
budget → `business_operations.budget-forecast`; an event poster → creative/marketing; a room booking →
Receipts and Confirmations; an officer handover pack → `business_operations.organisational-records`;
a fundraiser's takings → `nonprofit.fundraising-donor`. On the roster's own description the residue
looks like nothing, which is the shape that emptied the political-campaign row.

**(c) Duplicate of its own schema's default.** The `nonprofit` schema already lists, verbatim in its
deterministic array, *"A MEMBERSHIP-REGISTER structure held on the ASSOCIATION's side"* including the
members' meeting instrument. It already forbids a named member as a folder level. If the schema
detects the structure and states the privacy rule, the template restates both and adds nothing.

**(d) It fails the schema's own precondition, because dues are an EXCHANGE.** The schema activates on
a *non-exchange* relation — "money or labour given without a commensurate return." A subscription buys
rights, benefits and a vote. The landed `nonprofit.fundraising-donor` row says so against this row in
its own signal: *"Discriminated by whether the payment confers rights: dues do, gifts do not."* If
dues confer rights, the roll is a customer list and belongs to `business_operations`.

**(e) Its evidence is a never-alone word.** Member, club, society, association, subscription, AGM —
role words and document-type words, every one struck by the schema's own never-alone array.

## Defeating it — the node test, three legs, each argued

The schema's DEFAULT is: fire on any of eleven non-exchange structures; order by association →
non-exchange counterparty or fund → period → document function; forbid a named beneficiary, donor,
member or safeguarded person as a folder level. That is the paragraph this row must differ from.

### Leg 1 — detection signals differ from the schema's default

The schema's gate is *what relation is evidenced*. This row adds a **second, orthogonal gate: what the
artefact's ROW UNIT is.** The row fires only where the unit is one person's standing — not a payment,
a case, a gift, a fund or a rite. That gate produces three signals the schema does not state and no
sibling claims:

1. **The roll-quorum tie.** A members' meeting instrument states its quorum, notice entitlement or
   vote denominator *as a function of the register*: "a quorum of X members entitled to vote", an
   electorate size on a scrutineer's return quoted from the roll, a requisition signed by N members.
   No other structure in this family has a cross-artefact dependency of that kind — a grant report, a
   fund statement, a case note and a rite register each stand alone. This is the row's single most
   distinctive detection signal and it is the answer to charge (c).
2. **Revision in place.** A roll carries a status that *changes* — current, in arrears, lapsed,
   resigned, expelled, reinstated — and two dated snapshots differ by a set of joiners and leavers.
   Everything else in the schema accumulates. `nonprofit.religious-institution` supplies the contrast
   from its own side: a rite register *"is never revised, only annotated."*
3. **A class column that carries differential rights.** Full / associate / student / honorary / life
   exists precisely to attach *different rights* to different people. A customer tier attaches
   different *goods*. This is the discriminator that answers charge (d) and it is a positive signal,
   not an absence — which matters, because the schema's own volunteer signal is criticised inside the
   schema for resting on an absence.

Answer to charge (a) and (e): the row does not fire on the body being a membership body, and the JSON's
first never-alone entry strikes exactly that token — "THE ORGANISATION TYPE" — before any other.

Answer to charge (b): the subtraction leaves a real residue, and the *affiliation/recognition* record
is it. A students' union re-registration form is not a constitution and not a budget: it carries
office-holder slots, a **member headcount**, a fee scaled to that headcount, and a condition that a
roll and an AGM exist. That is this row's structure with the row unit promoted from a person to a
body. The campus club's *roll of who is in the society* is the same artefact at smaller scale. So the
absorbed `acad.student-organization` coverage lands here honestly rather than being invented to save
an id.

### Leg 2 — the dimension recommendation differs, and the difference is FORCED

This is the leg I did not expect and it is the strongest.

The schema's default branches, after the association, on the **non-exchange counterparty or fund**:
the grant, the restricted fund, the appeal, the case, the register. Every sibling has something to put
in that slot. **This row has nothing that may go there.** Its counterparty is a natural person, and the
schema's own privacy rule forbids a named member as a folder level. The counterparty level therefore
*collapses*, and the membership year or governance cycle is promoted into the vacated slot. The
resulting order — association (rarely) → membership year → document function — is materially different
from the schema's default and is derived from a privacy rule rather than from a preference.

Two constraints kept this honest. It is **not** time-first: a membership year is a content period that
says *which roll this is*, not a capture date, and `00` holds — *"For document and record domains,
project, function, or subject usually comes before time because putting year first scatters related
work across calendar folders."* And `dimension_order` stays `[]` under PR-6, so the recommendation is
prose; the association level is seeded ineligible in a single-association corpus, where it would be
*"use an author or organization merely as a collector"* and would *"create meaningless one-child
levels"*.

### Leg 3 — the privacy rule differs in kind, not in degree

The schema's protected party is disclosed under **need** — a beneficiary, a safeguarded child. This
row's is disclosed by **affiliation**, which differs in kind on three counts argued in full in the
JSON's `sensitivity_why`: **cardinality** (a case file exposes one person; a roll exposes the whole
membership in one spreadsheet), **inference from mere membership** (a row's existence, before any
content is read, can disclose belief, political opinion, union membership, sexual orientation,
immigration or health status — associations form around exactly those things), and **no consent path**
(these people gave their details to an association, not to a file-organiser on a volunteer secretary's
laptop).

The row therefore adds three operative rules the schema does not have: a roll is protected **on its
column set alone**, before any row is read; a roll is **never excerpted row-wise** into a model prompt;
and a **member class** is forbidden as a folder level in addition to a member's name. The last one
matters practically — class has a small, tidy branching factor and will look attractive to whoever
edits the canvas.

### Charge (d) is conceded and answered, and the answer may fail

The honest position: **the row's evidence is not the payment, it is the register of standing.** A
member is part of the association's constitutional person, votes on its motions and can requisition a
meeting; that is a status relation, not a purchase. And the schema itself admits the membership
register by name as one of its deterministic structures, so the precondition as written already covers
it.

But `nonprofit.fundraising-donor` is landed and says the opposite in one clause, and I have not
resolved it — see NJ-MA-1. If R1c rejects the standing-not-payment argument, the correct outcome is
refusal, and this row would rather be refused than kept.

## Files considered and REJECTED — the tempting false positives

Each of these looked like this row's evidence during the pass and is not.

1. **`members.vcf`** — a contacts export with several hundred cards, an organisation field naming the
   association, and a category label reading "Members". Rejected: no standing column anywhere. A
   category label is a document-type word beside an organisation name, which the row's own never-alone
   rules strike. Carried in `file_examples` as a negative fixture.
2. **`Committee handover - Secretary - 2026.docx`** — the roster hint's "officer records". Rejected:
   this is a role-continuity document about running the office, which is
   `business_operations.organisational-records`' world. An officer is not a member *qua* member.
3. **`Society budget 2026-27.xlsx`** — the hint's "budgets". Rejected outright: a period column set
   with no fund partition and no standing axis is `business_operations.budget-forecast`, exactly as the
   schema states for its own fund fixture.
4. **`Constitution as amended at the AGM 2026.pdf`** — tempting because it *defines* membership
   classes and quorum. Rejected: the artefact STATES the rule; this row holds artefacts that APPLY it.
   The seam is carried as a `collides_with` against `nonprofit.governance`.
5. **`Freshers' Fair signup sheet.jpg`** — names, emails, a society name. Rejected: an expression of
   interest is not standing. No number, no class, no join date, no dues.
6. **`Model constitution for unincorporated associations.pdf`** and **`Specimen affiliation form`** —
   downloaded exemplars. Rejected: they are reading material and route to Reading Inbox. Topic will not
   separate them from operative documents; `00`'s *"purpose answers what the file was for"* is the only
   test that works, and it is a `needs_llm` item, not a rule.
7. **`Gift Aid declaration - A Okafor.pdf`** — a named person, an association, a tax-relief tick.
   Rejected: the row unit is a *gift*, and `nonprofit.fundraising-donor` owns it.
8. **`Attendance sheet - branch meeting.pdf`** — kept only as the OCR fixture, and even there marked
   weak: **attendance records who came, a roll records who belongs.** The membership-number column is
   what makes it evidence at all.
9. **A membership-database live connector.** A CRM or membership system is a source system, not a
   file node. Only a bounded export with a readable manifest is represented.

## The collision fixture

Two are carried, because they fail in different directions.

**Headline: `Subscribers 2026 - active.csv`.** Name, email, plan, renewal date, amount, delivery
address. It is one-row-per-named-person, it is annual, it is money paid to an organisation, and at a
glance it is indistinguishable from a roll. **It is not this row's** — it is `business_operations`.
What discriminates: a *plan carrying entitlements* against a *class carrying rights*, and any
reference to a constitution or a general meeting. The row concedes this fixture in the JSON with
`also_schema: "business_operations"` and a `must_not_conclude` that names it as the collision.

**Second: `Institute of Facilities Managers - Membership Certificate 2026 - M-88214.pdf`.** Taken
verbatim from `government.professional-regulator`'s landed signal so that both sides name the same
bytes. A voluntary institute and a statutory register issue identical-looking certificates and
renewal ledgers. What discriminates is a **protected title plus statutory entry control plus a
fitness-to-practise route with external appeal** — and, as that row itself records, statutory status
is usually not printed on the document, so **both sides abstain to Review Later** rather than guess.

## Reciprocal boundaries — twelve, each naming one fixture on both sides

Four were already authored *against* this row by landed neighbours; those entries were written to
match the existing wording rather than to reopen a settled seam.

| Neighbour | Shared fixture | This row owns | They own |
|---|---|---|---|
| `business_operations` | `Subscribers 2026 - active.csv` | payment confers standing (class, number, vote) | payment confers goods (plan, price, delivery) |
| `business_operations.board-governance` | `AGM 2026 - Notice, agenda and resolutions.pdf` | constituency = the membership; quorum on the roll | constituency = directors/trustees; board pack |
| `nonprofit.fundraising-donor` ✓landed | `Annual renewal 2026 - subscription and gift.pdf` | the DUES line + the register it updates | the GIFT line + its declaration |
| `nonprofit.religious-institution` ✓landed | `Electoral roll 2026.xlsx` | a roll (revised in place) | a rite register (entry no. + officiant + witness) |
| `nonprofit.trade-union` | `Branch membership and check-off 2026.xlsx` | ordinary constitutional life | employer as counterparty: casework, bargaining, ballots |
| `nonprofit.governance` | `Constitution as amended at the AGM 2026.pdf` | applying the membership clauses | stating them |
| `nonprofit.standards-body` | `Committee ballot - closing 2026-04-30.pdf` | a vote on a motion or an office | a vote on a technical draft |
| `finance.hoa-residents-association` | `Annual subscription notice 2026 - M-4471.pdf` | the roll and the run (association side) | the one notice (member side) |
| `government.professional-regulator` ✓landed | the membership certificate above | voluntary body, sanction = loss of membership | statutory entry control + FTP + appeal |
| `government.elections-administration` ✓landed | `Committee election 2026 - scrutineers' return.pdf` | electorate = private membership | electorate = public electoral roll |
| `government.public-consultation` ✓landed | rule-change consultation with a closing date | respondents scoped to the roll | authority consulting an undetermined public |
| `hr` | `People 2026.xlsx` | status = standing | status = employment (gross-to-net anywhere wins) |

Each is written in the JSON in the SAME FIXTURE BOTH SIDES object form, with the reverse direction
stated inside the same signal.

## Neighbours considered that did NOT get an edge

- **`nonprofit.political-campaign`** — it names this row in its own `collides_with`, but it is a
  **refused** node; its member-roll coverage routes here by its own argument. An edge to a refused row
  records nothing actionable, so the inheritance is recorded here instead.
- **`government.parks-public-lands`** and **`government.defence-veterans`** — both name this row from
  their side, but the competing fixture in each case is an estate management plan and a veterans'
  benefit claim respectively. Neither is a roll, a run or a meeting instrument, so neither is *this
  row's* evidence; the seam they describe is really against the `nonprofit` schema at large. Recorded
  for R1c rather than edged.
- **`clinical_practice`**, **`nonprofit.volunteer-management`**, **`nonprofit.grant-reporting`**,
  **`nonprofit.advocacy-campaign`** — no shared row unit. A volunteer rota's unit is a shift, a grant
  report's is an output, a case file's is a person-under-need. None competes for a roll.
- **`academic`** — deliberately excluded despite the absorbed `acad.student-organization` id. A
  students' union or university on an affiliation form is a HOST, not a school fact; `00`'s own
  role-ambiguity warning about a university name applies directly and is quoted in that fixture's
  `must_not_conclude`.

## `proposed_fields` — empty, deliberately

Two candidates were considered and both rejected:

- **`membership_year`** — rejected as a synonym mint. The schema's own `fiscal_period` proposal already
  asks R1c to *"permit a named non-calendar award or appeal period"*; a membership year is exactly such
  a period and is evidence *for* that ask, not a second key. Recorded here for R1c.
- **`member_class`** — rejected twice over. It is a VALUE (of a work-type-shaped enum), and it is
  actively dangerous as a dimension for the disclosure reason argued above. A key minted to be
  forbidden is worse than no key.

`fields: []` and `dimension_order: []` follow from PR-6 and the schema declaring none. `role_split` is
empty because the schema already authored both role pairs (`sponsor`/`organization`,
`organization`/`subject_of_record`); this row adds only the argument that `subject_of_record` must be
destination-**ineligible** here, which is the schema's NJ-NP-5 and belongs there.

## `also_holds_with` — empty, and why

`also_holds_with` is schema↔schema only (CONNECTION §5). This row is a template, so the array is `[]`
even though the co-activations are real. Recorded for R1c as intent, not as edges:

- **finance** — a subscription run reconciled against a bank statement in one workbook: the
  institution-and-account header for finance, the class-derived rate for this row. finance is a safety
  schema, so protective ordering runs first.
- **business_operations** — one archive of a society's year holds the budget and the board minutes
  beside the roll and the AGM papers. Disjoint evidence, one corpus, neither promoting the other.
- **hr** — a combined staff-and-member table.

## NEEDS-JOSEPH

**NJ-MA-1 — Are membership dues an exchange, and does that kill this row?**
The `nonprofit` schema's precondition is a NON-EXCHANGE relation; dues confer rights, and the landed
`nonprofit.fundraising-donor` says so in a clause aimed at this row. Alternatives: **(a)** keep the row
on the *standing-not-payment* argument made above — the register records constitutional membership of
the body, not a purchase, and the schema already admits the membership register by name; **(b)** narrow
the schema's precondition to admit a *status* relation alongside a non-exchange one, which is cleaner
but touches the schema; **(c)** refuse this row — the roll and the run become `business_operations`
customer material and the general meeting joins `business_operations.board-governance`. This row
prefers (a), would accept (c) without complaint, and cannot settle it alone.

**NJ-MA-2 — Whose is a trade union's plain branch roll?**
This pass gives it to `nonprofit.trade-union`, on the principle that the more specific situation takes
the artefact whole. The opposite rule — this row owns *every* roll, the union row owns only
representation, bargaining and industrial-action material — is equally coherent and changes what both
rows detect. The one thing that must not happen is a single register split between two rows. The union
row is not yet landed, so the reciprocal is owed either way.

**NJ-MA-3 — The affiliation direction.**
An affiliation record's "member" is an organisation, and the *host* body's file of all its affiliated
societies is this row's roll with the unit promoted. Are the host side and the affiliated side one row
or two? And does `nonprofit.governance` reasonably claim the recognition-and-constitution half? This
is where the absorbed `acad.student-organization` coverage actually lives, so it needs an answer.

**NJ-MA-4 — Ban member CLASS as a folder level.**
The schema bans a member's *name*; this row argues the ban must extend to *class*, because class is
disclosive of everyone filed beneath it and has an attractively small branching factor. If accepted,
the ban has to live in the template contract rather than in one row's prose, and someone has to write
it there. This is the schema's NJ-NP-5 in a second instance.

## Self-verification

- `python3 -m json.tool` on the node file: **passes**.
- Key set compared against the landed sibling `nonprofit.fundraising-donor.json`: **identical**, all 27
  keys in order, `template` and `file_examples` sub-keys matching.
- Every `00` quotation checked with `grep -c -F` against `planning/00-database-agent-product-design.md`:
  **all return 1**. One draft quote returned 0 (straight vs curly apostrophe) and was cut back.
- Every `collides_with` entry is an object with `domain`, `signal`, `provenance`; every signal opens
  SAME FIXTURE BOTH SIDES and names one file on both sides. `also_holds_with: []` per CONNECTION §5.
- Every neighbour id checked against `planning/domains/roster.json`: all twelve present.
- Every `file_examples.source_type` is in `SOURCE_TYPES`; no file example writes a folder path as a
  fact; no threshold number, statistic, file count or handling class appears anywhere.
- `falls_through_to` names only §7.3 residuals: Protected Records, Independent Records, Review Later,
  Receipts and Confirmations, Unsupported or Encrypted.
- Files written: exactly the two assigned. No neighbour node, roster, canonical-fields, `check.py`,
  `src/` or SPEC file was touched.

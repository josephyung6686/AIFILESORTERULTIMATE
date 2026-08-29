# Research memo — `nonprofit.governance`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/nonprofit.governance.json`
Roster row: template on the fieldless `nonprofit` schema, `parent_id: null`, placeholder launch
Result: **REFUSED** (`refuse_node: true`)

## Result in one paragraph

The row is refused. Its roster hint — "governing document, registration, trustee or board business, policies,
annual reporting and regulatory returns" — reproduces, nearly item for item, the exclusion list the `nonprofit`
schema row wrote against itself: "It deliberately does NOT hold the association's self-running record: trustee
minutes, budgets, contracts, policies, procurement, audits, projects, IT and statutory returns are
business_operations with a different tax status, and are routed there by name." A template cannot differ from a
default it cannot reach, and this row cannot reach it: the schema fires only on a **non-exchange relation between
two labelled parties**, and no artefact in this row's scope names one. What is left after every landed neighbour
takes its share is the assertion that the organisation is a charity rather than a company — an organisation type,
which the schema strikes in terms ("tax status is a FIELD VALUE, not a structure"). The coverage is routed to
five landed rows and four residual homes, not lost.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (in full) and the stamped assignment from `make_prompt.py`.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — one landed launch row, read for depth calibration.
- `planning/domains/nodes/nonprofit.json` — my schema anchor, read in full. It is decisive and is quoted throughout.
- `planning/domains/roster.json` — confirmed every edge id; enumerated the eleven `nonprofit.*` and
  twenty-five `business_operations.*` rows.
- Landed neighbours, read only at `one_line` and at their `collides_with` entries naming me:
  `business_operations.board-governance`, `business_operations.corporate-regulatory-filings`,
  `business_operations.policy-handbook`, `business_operations.organisational-records` (the exemplary refusal),
  `law_practice.corporate-secretarial`, `nonprofit.religious-institution`, `nonprofit.political-campaign`.
- `planning/00-database-agent-product-design.md` — reached by targeted grep only. Every quotation below was
  grep-verified verbatim before use; line numbers are from that grep (00 lines 42, 45, 63, 97, 114, 120).

## THE CHARGE — the strongest case that this row should not exist

I state it first because it is the finding, not a hurdle.

**(a) It is an organisation type.** Strip the row of everything a landed neighbour owns and the residue is one
proposition: *the entity is a charity/union/church rather than a company*. That is a value of an entity-type or
tax-status attribute. The schema names this as the charge it was itself written to answer and concedes it in full:
"tax status is a FIELD VALUE, not a structure. It says what an entity is; it says nothing about what the artefact
records or which side holds it."

**(b) It is a list of document types.** "Governing document, registration, minutes, policies, annual report,
returns" is a document-type enumeration with an association name in front of it. The schema strikes exactly this
shape: "A document-type word alone, and a document-type word beside an association name. This is the two-role
escape route business_operations.organisational-records closed."

**(c) It is a duplicate of neighbours.** Every artefact maps onto a landed row: the constituted body's cycle →
`business_operations.board-governance`; the compelled submission → `business_operations.corporate-regulatory-filings`;
the controlled document → `business_operations.policy-handbook`; the constitutional register kept on an entity's
behalf → `law_practice.corporate-secretarial`; the members' meeting instrument → `nonprofit.member-association`.

**(d) Its own schema already refused it in advance.** NJ-NP-4 enumerates the seven templates the schema believes
defensible — grant-funding-received, restricted-fund-accounting, donor-and-fundraising, membership-register,
beneficiary-service-record, safeguarding-record, faith-rite-register. Governance is absent. And it instructs
directly: "a charity-regulator-return row should NOT be built, because business_operations.corporate-regulatory-filings
already owns that relation."

**Can the charge be defeated?** I tried three defences and all three failed. They are in "Survival candidates" below.
The charge stands. Refuse.

## The node test, all three legs

CONNECTION §2: a template row exists only when its **detection signals**, **recommended dimensions**, or
**privacy rules** differ from its schema's default.

**The schema's default template, stated so the difference can be measured.** The `nonprofit` schema declares no
field rows under PR-6, so its `dimension_order` is `[]` and its recommendation is held as prose: "the ASSOCIATION
only where the corpus genuinely spans more than one, then the NON-EXCHANGE COUNTERPARTY OR FUND — the grant, the
restricted fund, the appeal, the membership class, the case, the register — then the PERIOD ... then the DOCUMENT
FUNCTION." Its default activation is the non-exchange precondition. Its default privacy posture is stricter than
business_operations' because "the exposed party is a THIRD PARTY who is neither the user, an employee, nor a
customer, and who frequently disclosed under need, harm or vulnerability."

**Leg 1 — detection signals. FAILS, and fails in an unusual way: not by matching the default but by never
reaching it.** The default requires evidence of a non-exchange relation between two labelled parties. Take each
artefact in scope and ask which two parties it labels:

| Artefact | Parties it labels | Non-exchange? |
|---|---|---|
| Constitution / trust deed | the entity and its objects | no second party |
| Trustee minutes | officers of the entity | officers, not counterparties |
| Policy | the entity and a governed population | a population is not a party |
| Annual report narrative | the entity and its readers | no relation |
| Regulator return | the entity and an authority | statutory, i.e. compliance for authority |
| Registration certificate | the entity and a registrar | statutory |

None qualifies. The candidate signals that remain are a charity or union registration number, a trustee role word,
mission and public-benefit vocabulary, and an association name — and the schema lists **all four** in `never_alone`.
A detection set assembled entirely from a schema's forbidden sole activators is not a different default; it is no
activation.

**Leg 2 — recommended dimensions. FAILS twice.** First formally: the schema declares no fields, so both orders are
`[]` by `_CONTRACT` rules 10 and 15 and PR-6, and two empty orders cannot differ. Second substantively, which
matters because it would still hold if PR-6 lifted: the schema's prose order needs a **non-exchange counterparty or
fund** at level two, and this row has neither. The only level it could offer is the association itself, which 00's
own validator rejects — a proposal must not "use an author or organization merely as a collector" or "create
meaningless one-child levels" (00 line 97), and the single-association corpus is this world's normal case.

**Leg 3 — privacy rules. FAILS, and in the wrong direction.** The schema's stricter posture rests on the exposed
party being a vulnerable non-party third person. This row exposes **trustees and officers**, and the schema
disposes of them by name: "Trustee and officer records are hr's or business_operations' by the same logic; **a
trustee is not a beneficiary.**" Officer particulars are published by the same regulator these returns are filed
with. So the posture here is business_operations', i.e. *less* strict than the default — a difference that argues
the material belongs to business_operations, not that this row needs to exist. I still recorded
`potentially_sensitive` rather than `none`, for carried payloads only (a board pack encloses personnel matters,
legal advice, safeguarding summaries, donor schedules), and said so explicitly in `sensitivity_why` so it is not
mistaken for a leg-3 pass.

Three legs, three failures. Refuse.

## Survival candidates — the three defences I ran, and why each failed

**1. The constitutional instrument.** The best candidate: a constitution or trust deed with a labelled Objects
clause is a real structure with a real document-control apparatus, and no company has a charitable-objects clause.
It failed on two grounds. *Party versus class*: an objects clause names a benefit **class** ("persons in need in
the parish of X"), not a labelled party; the precondition needs a party. *The schema already routed it*: the
`nonprofit` schema's Independent Records argument names "a constitution, a certificate of registration" as residual
material. My own schema sent my best fixture to a residual home before I researched it. Beyond that,
`law_practice.corporate-secretarial` holds the constitutional record when it is kept on an entity's behalf, and
`legal` holds the executed-instrument reading.

**2. The members' meeting instrument (AGM notice, motions, proxy, vote count).** This one is genuinely a
non-exchange relation — member to association — and it is the reason the refusal is narrow rather than sweeping.
It failed because it is a **sibling's**, not a residue: the schema files it under its MEMBERSHIP-REGISTER signal
verbatim ("a members' meeting instrument carrying a notice period, a motion, a proxy or ballot form and a
member-vote count"), and the roster gives that structure to `nonprofit.member-association`. I recorded the
seam as a reciprocal collision and as NJ-NPG-2 rather than quietly annexing it.

**3. The charity annual report as a composite.** A trustees' report + governance section + fund-partitioned SOFA +
examiner's report looks like one coherent nonprofit governance artefact. It failed because it decomposes cleanly
with nothing left over: narrative → business_operations, filed copy → corporate-regulatory-filings, and the SOFA's
restricted-fund column partition fires the **schema's own** RESTRICTED-FUND signal — a default activation, which is
the definition of a template that does not differ from its default.

## Files considered and rejected

Eight fixtures are in the JSON with full observations. What each one taught, and the tempting false positives:

1. `Trustee board minutes - 12 March 2026.pdf` — **rejected as mine.** It is the `nonprofit` schema's own declared
   collision fixture and the schema already conceded it to `business_operations.board-governance`. The charity
   number in the footer is the never-alone token.
2. `Constitution and rules - adopted 2019 - as amended 2024.pdf` — **rejected**; survival candidate 1 above.
3. `Annual Report and Accounts year ended 31 March 2026 - trustees signed.pdf` — **rejected**; the collision
   fixture proper, below.
4. `Charity annual return 2025-26 - submission receipt.pdf` — **rejected.** "An OBLIGATION TO AN AUTHORITY with a
   deadline and a filing reference" is `business_operations.corporate-regulatory-filings`' stated anchor. A
   different registry is not a different structure, and NJ-NP-4 says so.
5. `Safeguarding policy v4.2 ... next review March 2028.docx` — **rejected, and this is the most instructive
   rejection.** Safeguarding *subject-matter* is enormously tempting, and the `nonprofit` schema does own
   safeguarding — but it owns the **concern/allegation/incident form naming a reporting person and a named
   subject**. A policy names a population and no party, and carries the document-control block that is
   `business_operations.policy-handbook`'s anchor. Subject-matter does not route; structure does.
6. `AGM 2026 - notice, motions and proxy form.pdf` — **rejected as a sibling's**; survival candidate 2.
7. `Model constitution for charitable incorporated organisations - regulator guidance.pdf` — **rejected as an
   exemplar.** Bracketed blanks and no adoption date. This is the schema's own needs_llm case; 00 line 45 gives the
   only test that works: "purpose answers what the file was for."
8. `Board pack March 2026.zip` — **rejected on manifest.** Read without unpacking; the *absence* of any grant, fund,
   case or register reference in the member paths is the answer.

Also considered and not written up as fixtures: a conflict-of-interest register (an officer disclosure, → Independent
Records or board-governance); a delegated-authority matrix (named in board-governance's own one_line); a risk
register (`business_operations.risk-register`); an audit or independent examination file
(`business_operations.compliance-audit`); a charity's employment contracts and trustee indemnity insurance
(`hr`, `legal`); a strategic plan or theory-of-change deck (`business_operations.strategy-plan`, and mission
vocabulary is a never-alone token).

## The collision fixture

`Annual Report and Accounts year ended 31 March 2026 - trustees signed.pdf`. It is the file that looks most like
this row's evidence and is not. Every surface signal points here: charity registration number on the cover,
trustees named, a public-benefit statement, an objects recital, restricted-fund columns. **What discriminates it is
that it decomposes into three landed owners with no residue.** The trustees' report narrative and governance
section are business_operations (the cycle to board-governance, the objectives account to strategy-plan); the copy
bearing a filing reference is corporate-regulatory-filings'; and the only part that activates the `nonprofit`
schema at all is the SOFA's fund-class partition — which fires the schema's **default** RESTRICTED-FUND signal, not
a template. A file that activates a schema only through its default is proof that the template is unnecessary,
which is precisely what CONNECTION §2 asks.

Secondary collision, in the other direction: `Safeguarding policy v4.2`. It looks like the `nonprofit` schema's
most protected material and is a controlled document. Discriminated by party versus population.

## Reciprocal boundaries — both directions, same fixture on both sides

Seven `collides_with` entries, all written as objects with a SAME FIXTURE BOTH SIDES clause. The two that matter
most:

**`business_operations.board-governance` — and I decline the seam as landed.** That row authored a boundary
against this id offering "a trustee or member-body vocabulary, a charity or union registration slot, and a
purpose-of-the-association framing" as evidence *for* this row. All three tokens are on the `nonprofit` schema's
`never_alone` list; the registration slot is the token the schema says it "was written to answer." *This direction:*
this row owns nothing in `Trustee board minutes - 12 March 2026.pdf`. *That direction:* board-governance owns the
whole file, because nothing in the pack names a non-exchange party. I did not edit that node — the retarget is
NJ-NPG-1 for R1c.

**`business_operations.corporate-regulatory-filings`** proposed the same owner-type discriminator and inherits the
same answer. *This direction:* nothing. *That direction:* the whole obligation structure, on the same fixture,
`Charity annual return 2025-26 - submission receipt.pdf`. The only residue worth naming — a restricted-fund note
travelling with a return — fires the schema's own fund signal.

Also written reciprocally: `business_operations.policy-handbook` (party vs population, on the safeguarding policy);
`law_practice.corporate-secretarial` (with vs without a service reference, on the constitution); `nonprofit.member-association`
(the AGM instrument, the load-bearing narrowing); `government` (authority-side vs filer-side copy of the return);
`finance` (institution-and-account header vs fund partition inside the annual accounts).

**`also_holds_with` is empty and deliberately so.** CONNECTION §5 restricts it to schema ↔ schema, and this row is
a template; and a refused row cannot co-hold anything. The `nonprofit` schema already carries the co-activations
this material would want (business_operations, finance, hr, government, legal). Recorded here for R1c rather than
serialized.

## Neighbours considered that got no edge

- `hr` — a trustee is an officer, not a beneficiary, so trustee records route to hr or business_operations without
  passing through this row. No same-evidence mutex against a refused row.
- `nonprofit.trade-union`, `nonprofit.standards-body`, `nonprofit.religious-institution` — each will meet the same
  governance material and each should cede it the same way. `nonprofit.religious-institution` already has:
  it narrowed itself to a rite register and states "its word 'governance' is already nonprofit.governance's and
  business_operations.board-governance's, and this row cedes it by name." That cession now lands on a refused row
  and is folded into NJ-NPG-4; I did not touch that file.
- `business_operations.meeting-record`, `business_operations.organisational-records` — the first is board-governance's
  own neighbour, the second is itself refused. Adding edges from a refused row to a refused row records nothing.
- `research.grants-funding`, `clinical_practice`, `applications.scholarship-fellowship` — the schema's collisions,
  not this row's; none touches governance material.

## proposed_fields

**Empty.** Nothing is proposed. A refused row must not mint or even second a key, and the four proposals the
`nonprofit` schema already carries (`organization`, `fiscal_period`, `sponsor`, `subject_of_record`) are all
attached to non-exchange structures this row does not hold. In particular I did **not** second `organization`,
even though the association is the one entity this row could name — seconding it here would be evidence that the
row is an organisation-name row, which is the charge.

## NEEDS-JOSEPH

**NJ-NPG-1 — the inherited seam (highest priority).** Two landed business_operations rows point `collides_with`
entries at this now-refused id, and their discriminator is built from tokens the `nonprofit` schema forbids as sole
activators. Alternatives: (a) retarget both at the `nonprofit` schema itself, so they fire only when a non-exchange
party appears in the pack — **my preference**; (b) delete both entries and let owner type be a field value as the
schema says; (c) overturn this refusal, which requires overturning the schema row's own scope sentence. I edited
neither neighbour.

**NJ-NPG-2 — the AGM instrument.** Assigned here to `nonprofit.member-association`, but that sibling may read
itself as owning the roll rather than the meeting. Alternatives: (a) member-association owns roll and meeting
together, since the meeting is the roll exercising itself — my preference; (b) split, convening cycle to
board-governance and proxy/vote count to member-association. If neither holds, the residue is a candidate for a
narrow members-meeting row — which would still not be this row.

**NJ-NPG-3 — the objects clause.** This refusal turns on benefit **class** vs labelled **party**. If R1c judges
that a charitable-objects clause naming a defined beneficiary class satisfies the two-party precondition, a narrow
constitutional-instrument row becomes arguable — but it would not be the roster hint's governance row, and it would
still have to defeat `law_practice.corporate-secretarial`, `legal`, and the schema's own routing of a constitution
to Independent Records. Stated so it can be overturned deliberately rather than eroded.

**NJ-NPG-4 — how the ten nonprofit templates were derived.** The hint's phrase reproduces the schema's exclusion
list nearly item for item, which suggests the sibling set was derived from the *industry* rather than from the
schema's *structures*. `nonprofit.political-campaign` has already refused on a closely related ground and
`nonprofit.religious-institution` narrowed to a rite register for the same reason — three of eleven. R1c should
check the rest. I did not touch them.

## Self-verification

- `python3 -m json.tool` parses the node file. Key set matches the landed siblings' shape.
- Every `collides_with` / `also_holds_with` entry is an object with `domain`, `signal`, `provenance`; every signal
  carries a SAME FIXTURE BOTH SIDES clause. `also_holds_with` is empty (schema ↔ schema only, CONNECTION §5).
- All seven edge ids checked against `roster.json` programmatically — zero unknown ids.
- All five `falls_through_to` names checked against 00's nine residual homes — zero unknown names.
- All eight `file_examples.source_type` values checked against `SOURCE_TYPES` — zero unknown types.
- Every 00 quotation grep-verified verbatim before use (00 lines 42, 45, 63, 97, 114, 120). Quotations from
  `nonprofit.json`, `business_operations.board-governance.json`, `business_operations.corporate-regulatory-filings.json`,
  `business_operations.policy-handbook.json`, `law_practice.corporate-secretarial.json` and
  `nonprofit.religious-institution.json` are copied from the files themselves.
- `fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false`. No thresholds, no counts, no
  handling classes, no `is_safety_domain` claim.
- `never_alone` carries five entries, the first of which is explicitly true of the tempting false file
  `Trustee board minutes - 12 March 2026.pdf`.
- Files written: exactly `planning/domains/nodes/nonprofit.governance.json` and this memo. Nothing else.

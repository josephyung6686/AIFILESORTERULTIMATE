# Research memo — `government.social-services-casework`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.social-services-casework.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accept the node.** It is the only row in the government family whose bounding anchor is a *person
carried through an open-ended duty cycle* rather than a *proceeding with a docket*, and that difference
forces both a different dimension recommendation and a strictly harder privacy posture than the schema
default. Five landed neighbours had already argued a boundary against this id before I wrote a line;
each named a shared fixture, and each survives scrutiny as a genuine two-sided contest. Fields stay
empty — PR-6 leaves `government` fieldless — so the row's whole substance is recognition, grouping,
privacy and residual routing.

## THE CHARGE — the strongest case that this row should not exist

**(a) It is a work_type value.** Not hypothetical: the `government` anchor's own `work_types[]` already
contains *"constituent, ombudsman, complaint, benefit, or service casework held by the public office."*
"Social services casework" reads as one more value in that enum, beside housing, permits and elections.
**(b) It duplicates a neighbour** — `government.constituent-casework` is a landed row about a public
office's file on one named person's welfare problem; `government.public-authority-record` is the generic
authority-side sibling. **(c) It duplicates its own schema's default template**, whose role-structural
one-line already names a "citizen-casework office" with named-person material protected by default.
**(d) It is an organisation name** — "social services" is a department, and a row whose only evidence is
a letterhead can never activate. **(e) It is a document type or lifecycle stage** — assessment, plan,
review are three documents and three stages wearing a node's clothes. **(f) It is defined by absence** —
"government casework that is not housing, not veterans, not emergency, not constituent."

### Defeating it

**(a).** A value becomes a node only when detection, dimensions or privacy differ from the default. All
three do, structurally rather than topically. The default's second dimension is *an exact bounded
proceeding or docket reference*. This world has no docket. Its spine is a **statutory duty owed to a
person**, and the file re-opens: a case closed in March is re-referred in October under the same token
and re-assessed against the same headings. "Benefit casework" as a work type names a subject; this row
names a *shape* — referral → threshold → assessment → determination → plan → review → closure →
re-referral. `government.emergency-management` made exactly this argument from the other direction and
it was accepted: *"An activation has no docket, which is precisely why the schema default's second
dimension does not fit it."*

**(b).** Answered by the neighbours in their own landed words. `government.constituent-casework` wrote
against me: *"The deciding evidence is POWER OVER THE OUTCOME. Social-services casework is the deciding
authority's own statutory file — it assesses, it owes the duty, and its own determination closes the
record. This row's holder can only ask … Shared fixture: a letter about Ms A's housing."* That is one
world seen from the desk that decides and one from the desk that asks; the same bytes land differently.
Against `government.public-authority-record` the discriminator is docket-versus-duty, and the shared
fixture is the SAR bundle: the disclosure schedule and redaction log inside it are the records-holder
function's work product, the case members they enumerate are mine.

**(c).** The default explicitly *forbids* what this world needs. Its `template.why` says: *"named people
must not become the organizing dimension."* This row's true anchor is a named person. That is a
collision with the default, not agreement, and resolving it is the row's job: recommend the pseudonymous
case token as the bounding dimension precisely so the person never becomes a folder name.

**(d).** Correct as stated, and encoded as the row's first `never_alone`: a social services /
children's services / safeguarding department name, letterhead or footer alone is not evidence, because
the same block appears on the recipient's copy, a provider's subcontract, an inspection report and a job
advert. The row activates on duty-cycle structure plus holder evidence, so the charge kills only a naive
version of it.

**(e).** Any single one of assessment, plan or review would indeed be a document type. The node is the
*cycle binding them under one recurring token*, which is why the deterministic signals are written as
relations between members ("repeated across members that are themselves different stages of one duty
cycle — rather than repeated across drafts of a single document") rather than as document names. A lone
assessment with no case around it does not activate; it falls to Protected Records.

**(f).** This nearly landed and I record it rather than smooth it. The government family is dense (32
rows) and the residue framing is tempting. I rejected it and wrote a positive premise: *the holder owes
the duty and can close the case*. That is testable on a file — does it contain an eligibility or duty
determination with reasons and a closure authority? — and it independently excludes a commissioned
charity, an advocate, a provider and the person themself, none of which "took" anything. The row would
exist if housing, veterans and emergency management did not.

**Verdict: accepted** — not because the id existed, but because the duty-cycle shape and the
person-as-forbidden-dimension problem are real and unowned.

## The node test, three legs

**Leg 1 — detection differs.** The default fires on role evidence tied to a bounded proceeding: a bill
identifier across a packet, a rulemaking docket, an application reference, a governance cycle with
numbered papers, an election operation — each a proceeding that opens and closes once. Mine fire on a
different object: a per-person case token recurring across *stages*; a threshold or eligibility
determination with reasons on the deciding body's letterhead; a plan naming arranged services and an
allocated worker with a review-due date; a convening authority's multi-agency conference record; a means
assessment resolving to a client contribution. I added one signal the default has no analogue for: an
email or calendar record whose structured slots carry the case token into an *already evidenced* case —
extending a case, never opening one. That is 00's activation-≠-grouping rule applied to a world where
sparse members (an undated visit note, a `.ics` home visit) outnumber labelled ones.

**Leg 2 — the dimension recommendation differs by overruling the default.** Default: function → docket →
work type, people forbidden. Mine: duty or service area → case token → review cycle → work type, with
the person *still* forbidden even though the person is the anchor. Substituting a pseudonymous case
token for a docket is not cosmetic: a docket is public and a case token is not, so the same dimension
slot carries opposite disclosure consequences. `dimension_order` is nonetheless empty — PR-6 leaves the
schema fieldless and a template cannot branch on undeclared fields — so the recommendation stays prose.
Time is not first: *"For document and record domains, project, function, or subject usually comes before
time because putting year first scatters related work across calendar folders."* Parent-makes-child-
intelligible applies directly — *"A work type such as Homework 3 is meaningful only after the course is
known"* — a review note is meaningless without the case it reviews. And the order is a recommendation:
*"The system recommends an order based on the domain template, but the user can reverse, remove, add, or
flatten dimensions."*

**Leg 3 — privacy differs in kind, not degree.** The schema is already `potentially_sensitive`, so
"sensitive" alone distinguishes nothing. Three specifics do. (i) **No low-risk residue.** The anchor
contemplates packets containing published laws and reports whose bytes are low risk; this row has none —
every member concerns a named living individual, disproportionately a child, a vulnerable adult or a
person in crisis, plus third parties (family, neighbours, referrers, sometimes protected referrers) who
never consented. No member's openness could justify relaxing the group. (ii) **Existence is the
disclosure.** For a child-protection case the fact that a case exists is the harmful fact, before any
content is read — hence the person may not become a folder name, group title or surfaced filename, which
inverts the normal instinct to anchor on the most meaningful entity. (iii) **Cross-person joining is
forbidden as a grouping rule**, not merely discouraged: a caseload extract must not be split into
per-person groups, and two cases sharing a worker, address or school must not be merged. The design's
floor applies throughout — *"Privacy policy must be enforced before content reaches any model or
external connector."* Where this row meets a neighbour, the stricter side governs the merged posture.

All three legs differ. The node stands.

## Sources

The standing brief; the stamped assignment; `legal.practice-matter-file.research.md` as depth
calibration; `government.json` (anchor: default template, `never_alone`, `work_types`,
`grouping_reasons`, examples); `roster.json`; `canonical_fields.json` (key list only — to confirm which
universal keys are legal as `facts_legal`, and that `people` is not destination-eligible); and the five
landed neighbours below, read only at the lines naming my id.
`00` was reached by targeted grep, not streamed. Every quoted span in the JSON and this memo was
grep-verified verbatim first: the residual-library sentences (Independent Records, Protected Records,
Review Later, Unsupported or Encrypted); the three dimension-ordering spans quoted in Leg 2;
*"A session should never be treated as proof of topic"*; and *"Privacy policy must be enforced before
content reaches any model or external connector."* Nothing else is in quote marks.

## Files considered and REJECTED as this row's evidence

1. **`Assessment and Support Plan - J. Rivera - Bright Futures Family Services.pdf`** — *the collision
   fixture.* Section-for-section identical to a statutory assessment: needs, plan, outcomes, key worker,
   review date, often on a template the council supplied. **What discriminates it:** no eligibility or
   duty determination and no closure authority — the plan is *delivered*, not *decided*. The council
   reference on the footer is a commissioning trace, not a transfer of custody. Kept in `file_examples`
   as a rejected fixture so the discriminator travels with the node.
2. **`Homelessness HL-2026-0912 - duty decision letter.pdf`** — a real duty determination, real
   authority letterhead, named household, safeguarding referral annexed. Not mine: the duty decided is
   accommodation. The annexed referral is a member that keeps its own evidence, not a conversion.
3. **`Rating Decision - file 12-345-678 - 2026-06-19.pdf`** — intake, evidence development, assessment,
   reasons, appeal. Not mine when the reasoning cites a service period or character-of-service plus a
   personnel identifier. The agency name decides nothing; the *eligibility premise* does.
4. **`Shelter Registration - Northgate High School - 2026-11-04.csv`** — person-level welfare data held
   by a public body, my exact surface. Not mine: one activation at one centre, closed at stand-down, no
   case token, no allocated worker, no review cycle.
5. **A benefit award letter or care-charge invoice held by the person it names** — the commonest false
   positive in a real personal corpus, and the reason the recipient rule is a `never_alone`.
6. **`Complaint CC-2026-0442 - final response - Council Complaints Team.pdf`** — the intermediary side
   is `constituent-casework`'s, the respondent side `public-authority-record`'s; mine only if the
   complaint is about this authority's own casework decision and sits inside the evidenced case (hence a
   `work_types` value, not an activation signal).
7. **A caseload dashboard or unit-cost model with only aggregate columns** — describes casework without
   being casework; person-level rows are the discriminator.
8. **A managing-allegations file about a staff member** — my shape exactly, but the subject is an
   employee and the apparatus is employment.
9. **A hospital discharge summary in a social-care handover pack** — clinical authorship, episode and
   custody. The needs assessment that *follows* is mine; the summary is not, however it arrived.
10. **A blank assessment form, a published eligibility policy, a charging schedule** — this world's
    paperwork with nobody in it → Independent Records.

## Reciprocal boundaries — both directions, same fixture on both sides

| Neighbour | Their side | My side | Shared fixture |
|---|---|---|---|
| `government.constituent-casework` | can only ask; acts on the individual's written authority; files someone else's answer as its outcome, under its own reference | assesses, owes the duty, and its own determination opens/changes/closes the record | a letter about Ms A's housing |
| `government.public-authority-record` | a bounded proceeding/request/programme closing when the proceeding closes; the disclosure schedule and redaction log | an enduring case token attached to a person, re-opening and re-reviewing; the case members that schedule enumerates | `Case file bundle - SW-2026-4471 - subject access request.zip` |
| `government.housing-authority` | duty, decision and remedy are accommodation — priority need, allocation, tenancy, rent account | care, protection or support duties that survive regardless of where the person lives | `Homelessness HL-2026-0912 - duty decision letter.pdf` |
| `government.defence-veterans` | reasoning cites a service period/event or character-of-service, plus a personnel identifier | determination rests on means, household, residency, capacity or a disability with no service premise | `Rating Decision - file 12-345-678 - 2026-06-19.pdf` |
| `government.emergency-management` | a roster against ONE activation at ONE centre, closed at stand-down | an enduring case with a token, an allocated worker and a review cycle | `Shelter Registration - Northgate High School - 2026-11-04.csv` |
| `clinical_practice.case-conference` | the clinician's OWN report prepared for the conference | the convening authority's minutes, plan category and review record; the clinician is one attendance line | `Child Protection Conference - Minutes - CP-2026-0188 - 14 May 2026.docx` |
| `nonprofit` | delivers against a referral or contract; spine is delivery, attendance and outcome reporting to a commissioner | determines eligibility/duty and can close the case | `Assessment and Support Plan - J. Rivera - Bright Futures Family Services.pdf` |
| `medical` | care given to a patient in a clinical episode, in clinical custody | statutory duty determination or arranged social-care service, authored by a non-clinical team | a hospital discharge and social-care handover pack |
| `hr.employee-relations` | subject is an employee; apparatus is employment; outcome is an employment sanction | subject is a service user or child owed a duty; outcome is a protection or support decision | a managing-allegations file |
| `business_operations` | counts, budgets, staff, KPIs; no named service user | person-level rows or a single named case | `Case notes export - Adults Team 4 - Q3.csv` vs its aggregate twin |

The first five are **reciprocals I owed and have now paid** — those rows authored their side and flagged
the debt. `public-authority-record`, `nonprofit`, `hr.employee-relations` and `business_operations` are
authored **one-way here**; R1c owes the reciprocal. `medical` is authored against the schema-level id
because no medical child row was consulted.

**`also_holds_with: legal`** — the one genuine dual-custody case. When an authority takes protection
proceedings, one packet is legitimately both: the statutory case's own evidence *and* a legal matter
file with a court reference, bundle index, statements and orders. This is 00's abstract-that-is-also-an-
application situation — purpose-coherent in two worlds at once — so it is dual custody, not a collision.
Split for the reciprocal: bundle index, pleadings, instructions and counsel's advice are the
practitioner side's (`legal.practice-matter-file` when the holder is the in-house or instructed lawyer);
the assessments, chronology and plan exhibited within them stay mine. Neither side may strip the other's
protection.

## Neighbours considered that did NOT get an edge

- **`finance`** — the means assessment totals income and capital, but the person's own statements are
  *referenced* by my file, never members of my group, and the authority's charging calculation is not
  the person's financial record. Handled in the example's `must_not_conclude`, not as a collision.
- **`government.public-records-foi`** — folded into the `public-authority-record` edge; the same
  records-holder-function discriminator does the work and a second edge would say it twice.
- **`government.public-health-administration`**, **`government.school-district-administration`** — both
  hold person-level records about vulnerable people, but neither contested a fixture I could name
  concretely, and I declined to invent one to manufacture an edge.
- **personal identity/record rows** — the recipient's-copy problem is a `never_alone` rule and a residual
  routing decision, not a node-to-node contest; an edge would imply the rows compete for one holder.

## `role_split` — deliberately empty

There is a real role split: the same human is the *subject* of the authority's record and the *holder*
of their own copy; the same human is a *service user* to the commissioner and a *client* to the
provider. But `role_split` requires naming the **different field keys** carrying the two roles, and
under PR-6 `government` declares no fields — writing the edge would mean inventing the vocabulary this
pass is forbidden to mint. The substance is recorded in `collides_with` (nonprofit) and in the
recipient `never_alone`. If PR-6 is lifted, revisit this edge first.

## `proposed_fields` — none, and why

The only field this row wants is a bounding case reference. Minting `case_reference` here would
contradict the placeholder-row rule, create a variant of a concept that `constituent-casework`,
`permit-licensing` and `public-records-foi` each need in slightly different shapes, and put a
person-identifying token into a destination-eligible slot without central adjudication of whether that
is safe. The landed casework sibling proposed nothing; the family's only proposal is `programme` on
`government.grant-programme-administration`, which does not fit a person-anchored case. Recorded as
NJ-SSC-1 instead of minted.

## NEEDS-JOSEPH

**NJ-SSC-1 — the case token has no home.** The bounding anchor is a per-person case reference and the
schema declares no field able to hold it, so grouping is asserted in prose nothing can bind.
(a) Keep PR-6 intact — group only via universal duplicate/version relationships plus recognition, and
accept that a case can never be a dimension. (b) Adjudicate one bounded holder-side reference concept
centrally on the `government` schema, usable by this row, `constituent-casework`, `permit-licensing` and
`public-records-foi` alike, explicitly pseudonymous and destination-eligible, with a person's name never
destination-eligible. (c) Route all person-anchored authority casework to Protected Records at launch
and defer the dimension entirely. I would pick (b) — (a) leaves grouping unenforceable and (c) discards
recognition work that is already correct — but this is a schema-level decision, not mine.

**NJ-SSC-2 — is "the holder owes the duty" a precondition or a fact?** Written here as a recognition
precondition, matching how the anchor treats holder role. If recordable it would be the single most
useful discriminator in the government family, settling nonprofit, provider, advocate, recipient and
lawyer in one move. Coupled to NJ-SSC-1.

**NJ-SSC-3 — the stricter-side merge rule should be stated once, centrally.** Three of my edges
(`emergency-management`, `case-conference`, `medical`) each restate "the stricter side governs the merged
posture" in their own words. That is a product-wide rule about protected groups meeting less-protected
ones and belongs in CONNECTION or `00`, not re-derived per row. Flagged, not edited — shared files are
out of scope for me.

## Self-verification

- `python3 -m json.tool` parses the node cleanly.
- Key set matches the landed government siblings; `collides_with` entries carry `provenance` alongside
  `design_cite` as those siblings do.
- Every quoted span grep-verified verbatim against `00` before writing; nothing else is in quote marks;
  no thresholds, counts, scores or handling classes anywhere.
- All 12 `file_examples.source_type` values are in `SOURCE_TYPES` (checked programmatically); no example
  writes a folder path as a fact; the two sparse fixtures (`Case notes export`, the `.ics` home visit)
  are marked `group_without_copying_facts: true`.
- Every edge target confirmed present in `roster.json` (checked programmatically, zero misses); every
  `falls_through_to` and `falls_through_if_inactive` value is one of `00`'s nine residual names.
- `fields` and `proposed_fields` both empty, as required for a placeholder row on a fieldless schema.
- Each rejected fixture is tripped by at least one `never_alone`: the department-name rule trips the
  Bright Futures plan, the recipient rule the benefit letter, the bare-token rule the veterans decision,
  the calendar rule the `.ics`.
- Files written: only the two assigned. No neighbour node, roster, canonical-fields, `check.py`, `src/`,
  SPEC or ownership-register file was touched.

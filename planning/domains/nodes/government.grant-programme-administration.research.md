# Research memo — `government.grant-programme-administration`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.grant-programme-administration.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, `launch: placeholder`

## Result

Accept the node. It survives the charge because its decisive detection shape and its privacy posture
both differ from the government schema's default template, and neither difference is a work type, a
document type, a lifecycle stage, or a restatement of the schema.

`fields: []` and `template.dimension_order: []` stand under PR-6. One `proposed_fields` candidate is
recorded for R1c, not minted.

## The charge — the strongest case that this row should not exist

Stated first and at full strength, because it is close to winning.

The government schema anchor lists, verbatim in its own `work_types` array, the string
`"grant call, received application, assessment, award, monitoring report, or closure record on the
funder side"`. That is this entire row, compressed into one enum value on the schema that owns it.
The brief's own refusal rule says a row whose only difference is work types is not a node — it is
values. On that reading, `government.grant-programme-administration` is a lifecycle stage sequence
(call → apply → assess → award → monitor → close) wearing a node's clothes, and the honest move is
to delete it and let the schema's default template carry the coverage.

Three further prongs sharpen the charge:

1. **Duplicate of a sibling.** `government.public-procurement` is the same six-stage sequence with
   the same artifacts — a notice, inbound third-party submissions, an evaluation panel, an award, a
   managed instrument, and returns. If two rows differ only in what the money buys, one of them is
   a value of the other.
2. **Duplicate of the default template.** The schema's `template.dimension_order` is empty and mine
   is empty. Its `never_alone` list already forbids `"legal, policy, regulatory, compliance,
   public-interest, civic, election, procurement, permit, licence, grant, or statistical vocabulary
   alone"` — the word *grant* is already handled upstream. If dimensions match and the vocabulary
   guard is already written, what is left?
3. **Never-alone-only evidence.** Every obvious signal is on the forbidden list: a funder name is an
   organisation name, `.gov` is a domain, "Grant" is a word, `CRF3-0147` is a bare reference token.
   A row whose entire evidence base is never-alone can never activate, and the brief says so.

### Defeating it

Prong 3 falls first, and its fall carries the rest. The activating evidence here is not a token; it
is a **structural relation between files that no single file can carry**: one issuing document that
begets *N* inbound documents authored by *different third parties*, each bearing a reference token
whose prefix the issuing document defines, held on the holder's own disk. That fan-in is a fact about
the corpus, not about any filename, and it is unavailable to every false positive in this memo. The
grantee's disk has exactly one application and one award. The reader's disk has a call and nothing
else. Only the funder holds the many-to-one.

Two further shapes are equally structural and equally unavailable elsewhere: **evaluative documents
written about non-holders** (a scoresheet whose rows are other organisations' references and whose
columns are named assessors), and **an outbound money instrument with conditions and recovery but no
acceptance clause**. Neither is a word, an extension, or a stage label.

Prong 1 fails on the instrument. A procurement award and a grant award are not two stages of one
thing; they are opposite directions of value. Procurement buys something *for the authority* and
therefore always terminates in deliverables, service levels, and acceptance. A grant funds the
*recipient's own* stated purposes and therefore always terminates in conditions of funding, eligible
expenditure headings, and a recovery clause. That is a discriminator a classifier can actually read
off the executed document, and the JSON states it reciprocally on both rows' side of the shared
scoresheet fixture. The two rows also differ in privacy: a losing bidder and a rejected applicant are
not the same disclosure risk, because an unsuccessful application often reveals the applicant's
financial position and beneficiary population, which a losing tender does not.

Prong 2 fails on privacy, which the node test accepts as sufficient on its own — CONNECTION.md §2:
"A **template** row exists only if its detection signals, recommended dimensions, or privacy rules
differ from its schema's default template." The schema's default posture is that authority-side
holdings may contain sensitive material and are protected by default. This row's posture is
differently *shaped*, not merely stricter: it needs **two firewalls in opposite directions** within
one programme (applicant material must not disclose assessor identity; assessor declarations must not
disclose applicant standing), and it needs a **split-publicity rule** the default does not have — an
award may be lawfully published in a transparency register while the application behind it and every
unsuccessful application beside it are not, so published award data must never lower the sensitivity
of its group neighbours. No other government child needs that rule, because no other child holds
winners and losers in one folder.

Prong 2 also fails on the vocabulary guard, but only partly, and the memo should be honest about it:
the schema already forbids the word *grant*. What the schema does not do is name the **homographs**.
`Grant of Probate`, `grant of planning permission`, a grant deed, a land grant, and a place named
Grants are five distinct false friends that share the token, and the first of them appears as a
fixture here. That is refinement of an existing guard, not a new node, and it is not load-bearing —
the fan-in argument is.

Two prongs of the charge therefore fail and one is conceded as partial. Verdict: **accept**, with
the concession recorded that a reader who weighs the anchor's `work_types` string heavily could
reasonably have refused, and that this row's whole claim to existence rests on corpus structure and
privacy shape rather than on anything a single file says.

## The node test, argued in three legs

**The schema's default template**, quoted from the anchor: `dimension_order: []`, `time_first: false`,
empty by PR-6, with prose order "authority-side function or bounded proceeding/case/programme first,
then an exact reference or cycle, then work type; named people must not become the organizing
dimension." Recognition activates on evidenced authority-side role. Sensitivity is
`potentially_sensitive`.

*Leg 1 — detection signals: DIFFER.* The anchor's deterministic list is production-shaped: a bill
packet with an official identifier, a rulemaking response, a public-body governance cycle. Every one
of them recognises the authority's *own output*. This row's decisive signals recognise an *inbound
third-party corpus keyed to one issuance*: the many-to-one applicant fan-in, evaluative documents
written about non-holders, assessor declarations naming applicants, and an outbound instrument
discriminated by conditions-and-recovery against acceptance-of-deliverables. None of those five is on
the anchor's list, and the anchor's list would not fire on any of this row's core fixtures.

*Leg 2 — recommended dimensions: IDENTICAL, and conceded.* Both are empty. This leg contributes
nothing. Saying otherwise would be padding: no government field exists, so no dimension can exist,
and the prose ordering this row would want (programme → reference → work type) is a specialisation of
the anchor's prose, not a difference from it. The one genuine addition is negative — applicant and
assessor names must not become branch labels, because a visible folder named for an organisation
discloses that it applied and usually that it failed. That is a privacy rule, so it is counted in
leg 3 and not double-counted here.

*Leg 3 — privacy rules: DIFFER.* The two-directional firewall and the split-publicity rule are stated
above. Both are specific to a corpus that holds evaluations of many third parties, and neither is
derivable from "protected by default."

Two of three legs differ, and the test requires one.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md`, and the stamped assignment from
  `make_prompt.py government.grant-programme-administration`.
- `planning/00-database-agent-product-design.md` — grep-verified only, never streamed. Five spans
  were verified verbatim before use and all five appear in the JSON: the extension-as-routing-signal
  span (line 35), the archive-manifest span (line 35), the session-is-not-topic span (line 45), the
  dimension-recommendation and project-before-time spans (line 95), and the privacy-before-model span
  (line 177). The two residual definitions quoted in `falls_through_to` were re-grepped out of `00`
  independently rather than trusted from the anchor.
- `planning/domains/CONNECTION.md` §2 — the node test, quoted above.
- `planning/domains/nodes/government.json` — the schema anchor and the default template this row is
  measured against. Read via targeted extraction of `template`, `sensitivity_why`, `collides_with`,
  `falls_through_to`, `work_types`, and `recognition.never_alone`, not in full.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — depth calibration.
- `planning/domains/roster.json` — every edge id below was confirmed present.
- `planning/domains/canonical_fields.json` — the full key list was checked before proposing anything.
- Landed neighbours that already argued a boundary against this id:
  `business_operations.budget-forecast.research.md` and `research.grants-funding.json`.

No external web research was done; the fixtures are drawn from document structures that the design
docs and the landed neighbours already treat as real, and every one is marked as what it is.

## Files considered and rejected

The tempting false positives, and why each is not this row's evidence:

- **`Grant Report - Q2 - Northside Community Trust.docx`** — the collision fixture. See below.
- **`Tender CRF-SVC-11 - Evaluation Panel Scoresheet.xlsx`** — structurally indistinguishable from
  the grant scoresheet. Rejected on the linked instrument: a specification with deliverables and
  acceptance puts it on `government.public-procurement`.
- **`Grant of Probate - estate of A Whitfield.pdf`** — pure homograph. A court registry is not a
  funding authority and there is no call, round, criteria, or expenditure heading. Rejected to
  `legal` and Protected Records.
- **`Grants Programme Budget FY26 v4.xlsx`** — the authority's planning round for the money it
  intends to give away. Rejected because it contains no application, applicant, assessor, or award
  reference; it is scenario columns. `business_operations.budget-forecast` reached the same verdict
  from its side and declined the edge (see reciprocity note below).
- **A downloaded call for applications with nothing else on the disk** — the single most tempting
  false positive, because it is a genuine funder document. Rejected: with no inbound fan-in the
  holder is a *reader or prospective applicant*, and the file goes to Independent Records or Reading
  Inbox. This is why the call alone is not on the deterministic list without the fan-in.
- **An award letter the holder received** — same bytes as the award letter the holder issued, minus
  direction. Rejected wherever the issuing block is not the holder.
- **A contacts export of panel members and applicant leads** — rejected outright. `00` says contact
  formats "should normally be privacy-protected rather than used to create folder proposals," and a
  name list evidences no workflow.
- **A grants-management database or live portal account** — a source system, not a file node. Only
  a bounded export with a readable manifest is represented.
- **A published transparency register of awards made** — a government publication. Rejected as
  activation evidence: publication by an authority is not custody, and the anchor already forbids it.
- **Grant taxonomies** — programme types, funding streams, sector codes, thematic priorities, and
  applicant categories were all considered and deliberately not enumerated. They are values, and
  J-IND forbids the industry-depth catalogue.

## The collision fixture

`Grant Report - Q2 - Northside Community Trust.docx`.

It looks exactly like this row's evidence: grant vocabulary throughout, a named funder, a reporting
period, expenditure against budget headings, output counts. It is not this row's evidence, and the
same is true of the harder version — `CRF3 - Payment Claim and Monitoring Report - Q2 2026.xlsx`,
which is *byte-for-byte the same document* on the other disk.

What discriminates it is direction, readable in three places: the funder appears as an **addressee
block** rather than an issuing block; the project described is the **holder's own**; and the funder
is addressed in the second person. Where all three are absent or ambiguous, neither row activates and
the file goes to Review Later — a shared-fixture ambiguity must not be resolved by guessing.

The weaker discriminator that must *not* be used is possession. Both sides hold both copies, so
holding a monitoring report proves nothing.

## Reciprocal boundaries

Stated in both directions, naming the same fixture on each side. Four collisions are authored.

1. **`government.public-procurement`** — shared fixture: an evaluation panel scoresheet.
   *Toward me:* the winning instrument gives money for the recipient's own purposes, with conditions
   of funding, eligible expenditure and recovery, and no acceptance clause.
   *Toward them:* the winning instrument buys goods or services for the authority, with a
   specification, deliverables and acceptance.
   *Neither:* scoresheet alone, no instrument.
2. **`nonprofit.grant-reporting`** — shared fixture: the quarterly claim and monitoring workbook.
   *Toward me:* the holder issued the call and the award and is receiving the return; issuing block
   plus inbound fan-in.
   *Toward them:* the holder is the funded body reporting outward; funder as addressee, project is
   the holder's own.
3. **`nonprofit.fundraising-donor`** — shared fixture: the call for applications.
   *Toward me:* the awarding body's public-authority status is independently evidenced.
   *Toward them:* a private foundation, trust, or corporate giving programme runs the identical
   workflow and stays private-association material.
   The anchor already states this direction at family level; this row names the fixture.
4. **`research.grants-funding`** — shared fixture: a notice of award.
   *Toward me:* the notice the authority issued, held with the applications it received.
   *Toward them:* the single notice a principal investigator received, anchored on that project.
   That row's own JSON independently frames its world around "who is being funded," which is the same
   seam read from the other end.

`also_holds_with: legal` for an executed grant agreement — one file legitimately carrying both, per
`00`'s abstract-that-is-also-an-application-document pattern. Not a collision.

## Neighbours considered that did not get an edge

- **`business_operations.budget-forecast`** — reciprocity note. That row explicitly considered this
  id and declined: "a public programme budget is the same tables. Unedged: the discriminator (a
  public grant programme with an issuing authority) is stated at family level and adding a per-row
  edge would duplicate it." I mirror the decision so the pair stays symmetric, and record the
  planning-workbook fixture on my side instead. If R1c prefers explicit pairs over family-level
  discriminators, both rows should change together.
- **`government.public-authority-record`** — the generic authority-side sibling. Not edged: it is
  the fallback for authority material with no bounded workflow, so it is a *residual relationship*
  within the schema rather than a same-evidence mutex. Every fixture here carries a programme
  reference; without one, nothing on this row activates anyway.
- **`business_operations.contract-administration`** and **`business_operations.procurement-sourcing`**
  — the company-side equivalents. The anchor already holds the authority-versus-company seam at
  family level and this row would only restate it.
- **`government.constituent-casework`** — named-person case handling overlaps in privacy shape, but
  the evidence does not compete: casework is one person's matter with the authority, grants are
  organisations' bids for money.
- **`finance.small-business-bookkeeping`** — the disbursement ledger side. Recorded as an
  `also_schema` on the claim fixture rather than as a mutex; Finance owns the financial slots.

## Proposed fields

One candidate, `programme` (string). Every canonical key was checked and none fits: `project` is
Research/Code-scoped and would misread an applicant's project as the holder's; `purpose` is College
Applications-scoped; `institution` names an organisation, not a cycle, and the funder here is the
holder rather than a counterparty; `record_type` is Finance-scoped; `event` is capture-based;
`our_firm`/`client` are engagement roles the government schema does not declare. Without one anchor
no dimension can exist at all, because `00` requires that "a parent dimension should provide the
context required to understand the child" and `CRF3-0147` is unintelligible without its programme.

Reuse over minting: `research.grants-funding` already asked Joseph whether an existing organisation
key may be declared to carry the funding role. R1c should decide both together — one key covering
both sides of the same money, not two variants.

## `role_split`

Empty, and deliberately so. Funder and applicant are a textbook `role_split` pair — the same entity
type in two roles, exactly the shape `00` licenses for `target_university` against `school`. It
cannot be authored here because a role split is expressed in *field keys*, and the government schema
declares none. This is the sharpest concrete cost of PR-6 on this row and is recorded as such rather
than smoothed into a collision that would misstate the relationship.

## NEEDS-JOSEPH

**NJ-1 — the programme anchor.** May a `programme` key be declared on the government schema, or
should an existing organisation key be extended to carry the funding role? Alternatives: (a) declare
`programme`, unlocking a programme → reference → work_type order; (b) reuse an existing key and
accept that it names the body rather than the cycle, which will branch three unrelated rounds into
one folder; (c) hold the line at PR-6 and leave all government children dimensionless. This row
recommends nothing and takes (c) as the current state.

**NJ-2 — re-granting bodies.** An authority that receives money from above and awards it below holds
both sides in one folder. Alternatives: (a) coactivate this row and `nonprofit.grant-reporting` on
the same programme; (b) treat it as a role-decided mutex resolved per document by direction; (c)
route the whole corpus to Review Later until a user confirms the direction. The JSON currently
implies (b) at document level, which will split one human folder across two rows.

**NJ-3 — split publicity.** An award published in a transparency register sits beside unsuccessful
applications that are not public. Does P7 need a rule that published status attaches to a *file* and
never propagates to its group, or is per-file sensitivity sufficient? This row assumes the former and
states it in `sensitivity_why`, but it cannot enforce it.

**NJ-4 — the conceded prong.** The anchor's `work_types` array already contains this row as one
string. If R1c holds that a row named by its schema's own enum is a value, this node should be
refused and its coverage returned to the default template plus Protected Records. The argument above
is that corpus structure and privacy shape defeat that reading; it is recorded here so the decision
is visible rather than buried.

## Self-verification

`python3 -m json.tool` parses the node. Key set matches the `government` anchor exactly, including
`proposed_context_terms`. `fields: []`. Every `source_type` is in `SOURCE_TYPES`. Every edge id
(`government.public-procurement`, `nonprofit.grant-reporting`, `nonprofit.fundraising-donor`,
`research.grants-funding`, `legal`) was confirmed on `roster.json`. Every `falls_through_to` name is
one of `00`'s nine residuals, and both quoted residual definitions were grepped verbatim. No
threshold numbers, no handling classes, no fabricated quotation. No file outside the two assigned
outputs was written or modified.

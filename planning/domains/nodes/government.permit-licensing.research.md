# Research memo — `government.permit-licensing`

Depth: J-DEPTH
Date: 2026-08-26
Row: `kind: template` on the fieldless `government` schema, `parent_id: null`, `launch: placeholder`
Output: `planning/domains/nodes/government.permit-licensing.json`

## Result

**Accepted, and narrowed.** The row survives, but not as "the government row for permits". It survives as the
authority's file for a **continuing permission** — one that persists after the decision, appears in a public
register, expires, renews, and can be reviewed, suspended and revoked. That continuity is the whole of its
claim. I removed spent one-off determinations from it and gave them back to
`government.public-authority-record`, and I removed the post-determination monitoring stream and gave it to
`government.environmental-regulation`, which had already authored that seam against me.

## The charge — the strongest case that this row should not exist

I ran the charge before writing anything, and three of its four legs landed hard enough to change the row.

**Charge 1 — it is a work_type value.** This is the most damaging version and it is nearly proven by the
schema anchor itself. `government.json` already carries, as a single string in its `work_types[]` array:

> "planning application, permit or licence case, inspection, enforcement record, reasons, decision,
> variation, suspension, or revocation on the deciding side"

That one enum value covers, word for word, everything a naive version of this row would have said. If the
row's content is a value that the schema already enumerates, the row is a value dressed as a node, and the
574's original mistake repeats.

*Defeated, but only partly.* A work_type value is a **document function**. "Permit case" is a function.
What this row actually holds is not a function but a **relationship with a duration**: a named holder has a
permission that continues to exist between documents, and an office maintains a live entry for it. The
observable consequence is a group property, not a document property — the group is a **serial with no
terminal event**, reopened by every renewal, variation, inspection and review, whereas every other
enumerated function in that anchor string is an event inside a proceeding that ends. That distinction is
recorded in `grouping_reasons` as the row's first entry, and it is why the row is not a synonym for the
enum value. I concede the residue: any *individual* licensing document, read alone, is that work_type value
and nothing more. The row therefore refuses to activate on a single document (see `never_alone`).

**Charge 2 — it is a duplicate of its own schema's default template.** Also nearly proven. The government
anchor's third deterministic signal is:

> "an authority-side decision record with labelled applicant or regulated-party slots, an application or
> case reference, a decision status, reasons, and an authorized-officer or office block; the same decision
> held only by its recipient does not satisfy the role precondition"

That is a licensing determination described in full. The anchor's own `file_examples` include
`Permit Case PL-2026-184 - Officer Report and Decision.docx` and `Inspection visit - Licensing Case
LC-1198.ics`. The schema was written with my evidence in its pocket.

*Defeated on two of the node test's three legs, and I state the failing leg plainly.*

- **Dimension order — NO DIFFERENCE, and I do not pretend otherwise.** Both this row and the schema default
  have `dimension_order: []`. PR-6 leaves `government` fieldless and a template cannot branch on undeclared
  fields, so this leg cannot distinguish anything for any government child in this pass. Any row claiming a
  dimension difference here would be inventing one.
- **Detection signals — REAL DIFFERENCE.** The anchor's ten deterministic signals recognise nine authority
  *products* (bill packet, rulemaking packet, decision record, procurement record, governance cycle,
  statistics packet, election packet, case export, office mail). Not one of them is **register-shaped** and
  not one is **adverse-power-shaped**. Four of my ten signals have no analogue in the anchor at all: the
  register extract (repeated rows about many unrelated holders, produced by the granting body); the
  suitability file (disclosure, medical, competency and right-to-work evidence *received for adjudication*);
  the expiry/renewal run; and the review or show-cause proceeding, which is initiated **by** the authority or
  by an objector rather than by an applicant — the opposite direction of travel from the anchor's decision
  record. A representations bundle addressed *to* the office from unrelated third parties is also structurally
  absent from the anchor. These are detection-signal differences, not vocabulary differences.
- **Privacy rule — REAL DIFFERENCE, and it runs in an unusual direction.** The schema default is
  protect-by-default because its worry is casework and unsuccessful bids. My worry is the opposite shape: my
  corpus is **deliberately mixed**, half of it statutorily published and half of it protected, *about the same
  people*. The register entry, the public notice of application and the issued licence are meant to be public;
  the suitability file, the neighbours' representations, the review witness statements and the enforcement
  papers behind the same reference are not. The rule this row needs and the schema does not is: **publication
  of the register row must not lower the posture of the case file that produced it**, and the register is
  itself a linkage hazard because sole-trader entries carry residential addresses. That is written into
  `sensitivity_why` rather than asserted as a class. The design floor is
  `00`: "Privacy policy must be enforced before content reaches any model or external connector."

Two of three legs differ with argued evidence, and CONNECTION.md §2's node test asks whether "detection
signals, recommended dimensions, or privacy rules differ". It does not require all three. Charge 2 fails.

**Charge 3 — it is a document type.** "Permit" and "licence" are words on documents, and an internal permit
to work, a software licence file, a parental consent form and a marriage licence all carry them. *Defeated
by construction*: the word is the first entry in `never_alone`, and the collision fixture
`Permit to Work - Hot Works - 14 Mill Lane - 2026-08-12.pdf` is authored specifically so the row trips on it.
The row activates on a proceeding plus a custody, never on a word.

**Charge 4 — it is a duplicate of a neighbour.** Four neighbours compete for the same bytes and I take this
charge as the most serious surviving one; it is answered in the reciprocal boundaries section below rather
than here. The honest summary: against `government.public-authority-record` the seam is thin enough that I
narrowed my own claim to keep it real, and against `government.diplomatic-consular` I do not think the seam
is settled at all (NJ-3).

**Charge 5 — it is defined by an absence.** Considered and dismissed quickly. The row is not "government
decisions that aren't planning applications". Every one of its ten deterministic signals is a positive
structure, and its distinguishing property (a permission that outlives its decision) is a presence.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md`; the stamped assignment from `make_prompt.py`.
- `planning/00-database-agent-product-design.md` — targeted greps only. Every span I put in quote marks was
  grep-verified verbatim against this file before it was written. One did not verify on the first pass (a
  paraphrase of the Temporary Screenshots residual) and was replaced with the real sentence from line 120.
- `planning/domains/CONNECTION.md` §2 — the node test table and the schema/template/value/group/residual
  split.
- `planning/domains/nodes/government.json` — my schema anchor, read for its default template, recognition
  signals, work types, grouping reasons, edges, residuals and file examples.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — depth calibration only.
- `planning/domains/roster.json` — confirmed my id and `kind`, listed the 31 government siblings, and
  verified every edge target before writing it.
- The five landed rows that had already argued a boundary against me, read at their edge blocks only:
  `construction_property.building-control`, `construction_property.site-health-safety`,
  `business_operations.corporate-regulatory-filings`, `government.environmental-regulation`,
  `government.diplomatic-consular`, plus the prose deferrals in `government.constituent-casework` and
  `government.education-accreditation`.

External artefact grounding is by named real document type rather than by URL: premises licence application
and operating schedule; representations from responsible authorities; licensing sub-committee decision notice
with a numbered conditions schedule; public licensing register; taxi/private-hire driver suitability file
(criminal-record disclosure, medical fitness form, knowledge test); food business inspection report and
hygiene rating; improvement notice; licence review and suspension papers; street trading consent renewal run;
scaffold and street-works licence. These are ordinary artefacts of municipal licensing practice. I use them
for **shape and custody**, not for legal rules, and the node derives no validity, deadline, retention period
or jurisdiction from any of them.

## Files considered and rejected

The row is measured by what it refuses.

| File | Why it is not this row's evidence |
|---|---|
| `Premises Licence - The Mill Tavern - certificate and summary.pdf` (the licensee's copy) | **The collision fixture.** Same reference, same conditions, same authority block as the file in my determination — byte-identical in the parts that matter. Discriminator: the **case apparatus around it**. Mine sits beside an application, representations, an officer report, a register entry and a renewal run; the licensee's copy sits alone or beside their own operating records. Possession of a permission is the recipient side and is enumerated in the schema anchor's own `never_alone`. |
| `Permit to Work - Hot Works - 14 Mill Lane.pdf` | The word "permit" and a numbered-authorisation shape, at the same site address as my scaffold licence. Discriminator: issuer and acceptor are both inside one contractor, validity is same-day, and there is a hand-back signature — no authority block, no statutory power, no applicant. `construction_property.site-health-safety`. |
| `Annual Return 2026 - Example Holdings - filing acknowledgement.pdf` | An authority reference, a deadline and a receipt. Discriminator: **no permission is sought** — it is a periodic compelled return about an entity that already exists. `business_operations.corporate-regulatory-filings`, which authored this seam first. |
| `Permit EPR-AB1234 - Quarterly Monitoring Return Q2 2026 - Outfall 001.xlsx` | Carries my permit reference. Discriminator: it is a result the operator generated *against* a condition I imposed, produced after determination. `government.environmental-regulation`. |
| `Planning Application 26/01144/FUL - Officer Report.pdf` | Identical apparatus — application, officer report, conditions, appeal route. Discriminator: it permits **development**, is spent when built, and runs with the land rather than with a holder. `government.planning-application`. |
| A fitness-to-practise panel determination for a registered professional | Application, assessment, conditions, register, removal power, disclosure and health evidence — every structural feature I claim. Discriminator: the permission attaches to a **titled profession** assessed against a standards edition, not to an activity, premises or vehicle. `government.professional-regulator`. |
| A person's driving licence, food hygiene certificate, firearms certificate, visa or fishing permit | Recipient-side personal records. They belong to identity, legal, finance or Protected Records; the schema anchor's `never_alone` already forbids activating government on them. |
| A licence fee invoice or card receipt naming the council | Evidences a transaction, not custody of a case. Finance. |
| A council's licensing policy statement adopted at full council | Genuinely tempting, and I **kept** it as a work type but not as an activation signal: a policy statement is a governance-cycle artefact and fires `government.municipal-administration` or the policy row on its own furniture. It joins here only through an exact licensing-regime reference. |
| A live licensing case-management system or portal account | A source system, not a file node. Only a bounded export with a readable manifest is represented, and manifests are read without unpacking. |
| A contacts export of licence holders | Names in a directory are not a licensing case. Excluded; `contacts` is deliberately absent from `file_kinds.source_types` for this row even though the schema anchor allows it, because a contact record can never carry the proceeding evidence this row requires. |

## Reciprocal boundaries

Seven mutexes are authored, each stated in both directions with the same fixture named on both sides. Four
of them reciprocate an edge a landed row already pointed at me; I did not edit those rows, and where their
wording needs to change that is a recommendation to R1c, recorded below.

1. **`government.public-authority-record`** — *the edge that nearly killed this row.* Mine: an authorisation
   that persists after the decision, with a register or expiry apparatus and an adverse-power sequence.
   Theirs: spent one-off determinations, certifications and registrations the office does not maintain a live
   entry for. Fixture on both sides: `Licensing Sub-Committee - 14 Mill Lane - Decision Notice and
   Reasons.docx` — mine when its neighbourhood contains a register entry, an expiry date and a later
   variation; theirs when the determination is the last thing the office ever writes about it. **Where
   continuity cannot be evidenced, theirs is the safer home and I abstain.** `government.constituent-casework`
   already routes all deciding-side rows, mine included, through this row on the holder-role axis; this edge
   is the reciprocal it was owed.
2. **`government.planning-application`** — mine: activity, public realm, premises, vehicle or person, held by
   a named holder, renewable. Theirs: land-use development, spent once built, running with the land. Fixture
   on both sides: `Scaffold Licence SC-4471 - 14 Mill Lane - conditions.pdf` against a planning consent for
   the same address. One address, one authority and one reference shape decide nothing.
3. **`government.environmental-regulation`** — reciprocating verbatim the seam that row authored: I own the
   lifecycle *up to and including* the determination for any licensable activity; they own what the granted
   conditions then generate. Fixture named identically on both sides: `Permit EPR-AB1234 - Consolidated
   Variation V3 - Schedule 3 Emission Limits.pdf`. Their memo asked whether I should carry the
   terminates-at-determination seam. **I do, and this is the answer to their open item.**
4. **`government.professional-regulator`** — mine: permission to an activity or premises. Theirs: standing in
   a titled profession. Fixture on both sides: a disclosure-and-health suitability bundle — mine when it is
   `Driver Licence Application 2026 - Suitability File - DVR-8817.zip`, theirs when the same bundle is
   assessed against a standards edition for a registrant. A register and a disclosure certificate exist on
   both sides and discriminate nothing.
5. **`construction_property.building-control`** — reciprocating their edge in their own terms: building works
   under a planning or building-regulations regime is theirs; an activity or occupation of the public realm is
   mine. Same fixture, same wording, both directions: the scaffold licence at the consented site.
6. **`construction_property.site-health-safety`** — reciprocating their edge. Authority + statutory power +
   applicant is mine; internal issuer/acceptor + same-day hand-back is theirs. Fixture on both sides:
   `Permit to Work - Hot Works - 14 Mill Lane - 2026-08-12.pdf`. Their memo flags this as authored one-way
   pending the government side (NJ-CP-HS-3); **this is that side.**
7. **`business_operations.corporate-regulatory-filings`** — reciprocating their edge and extending it to the
   custody axis they already state. Function seam: permission sought is mine, compelled periodic return is
   theirs. Custody seam: the licensee's own certificate is theirs, the case apparatus around it is mine.
   Fixture on both sides: `Premises Licence - The Mill Tavern - certificate and summary.pdf`.

## Neighbours considered that did NOT get an edge

- **`legal`, `nonprofit`, `business_operations` at schema level** (my `must_consider_neighbors`). The
  government **schema anchor already authors all three** as schema-level collisions, on precisely the axes
  that would apply here: government as party/issuer/cited authority does not decide the legal edge; a company
  filing with or regulated by an authority stays with the company; a charity or membership body is private
  association material. Repeating them at template level would be three copies of an argument that is already
  binding on me by inheritance, and would inflate the row without adding a discriminator. I instead authored
  the one place where the schema-level argument is *not* sufficient — `business_operations.corporate-regulatory-filings`,
  where the seam is function (permission vs return) rather than owner role.
- **`legal.practice-matter-file` / `legal.personal-legal-matters`.** A licensing appeal reaches a tribunal and
  generates byte-identical papers. But the practitioner's matter file and the appellant's personal record are
  both **recipient or representative** custodies, which the schema-level legal edge already resolves. No
  template-level mutex is added.
- **`government.education-accreditation`.** Their memo names me as "the strongest omission and a deliberate
  one" and gives the discriminator: accreditation has a volunteer peer team, a self-study authored by the
  applicant against a numbered standards edition, and a draft/response/final embargo, none of which licensing
  casework has. **I accept their reasoning and do not author the reciprocal.** Recording the concession here
  is the reciprocity; a fifth mutex on their row would be noise.
- **`government.municipal-administration`, `government.housing-authority`, `government.transport-authority`,
  `government.parks-public-lands`.** These are *venues* for licensing, not competitors for it. Adding them
  would turn the row into a directory of agencies, which is exactly the failure
  `government.constituent-casework` refused. If a taxi licensing file sits inside a transport authority, both
  readings are about the same permission and the seam is the agency's name — a never-alone signal.
- **`government.public-procurement` and `government.grant-programme-administration`.** Both receive
  applications, evaluate them and issue awards with conditions, so they were candidates. Rejected: an award
  creates a **contract or a funding relationship with a counterparty**, terminating in delivery; a licence
  creates a **standing permission enforceable against its holder**. Different terminal structure, and the
  schema anchor already separates buyer-side and funder-side custody in its own signals.
- **`identity` and `medical`** are `also_holds_with`, not collisions. A disclosure certificate or a
  medical-fitness form inside a suitability file legitimately carries both readings; membership must not
  convert either into a licensing fact, and the licensing case must not erase the underlying evidence. This
  follows `00`'s abstract-that-is-also-an-application-document pattern.

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false` — all deliberate.

The `government` schema declares no field rows under PR-6, and a template may reuse only fields its schema
declares. **I propose no fields**, including the one I most wanted. A permission-reference concept is the
single anchor that would make this row's serial group tractable, and it is exactly the concept that must be
adjudicated centrally rather than minted by a child (NJ-1). `record_type`, `institution`, `purpose` and
`work_type` were all checked as reuse candidates and all are scoped elsewhere in the canonical record or
would require a government field row this schema does not have.

The prose recommendation, for whenever fields exist: the **permission**, not the person and not the year, is
the organising level — it is the only anchor stable across application, grant, renewal, inspection and
revocation. Function second, cycle third. Time is not first because
`00`: "For document and record domains, project, function, or subject usually comes before time because
putting year first scatters related work across calendar folders." And nothing here is frozen:
`00`: "The system recommends an order based on the domain template, but the user can reverse, remove, add, or
flatten dimensions." A named-person or named-premises branch is specifically discouraged even though the
register publishes those very names — a folder tree that publishes a licensing relationship is a different
disclosure from a register a person must look someone up in.

## Residual routing

Protected Records takes representations, suitability evidence, review and enforcement papers and register
extracts carrying residential addresses. Independent Records takes a standalone issued licence or public
notice with no case apparatus. Review Later takes the permission-shaped file whose custody or continuity will
not settle — the internal permit to work, the unattributed inspection report, the orphan renewal run.
Temporary Screenshots takes a positively evidenced portal capture whose OCR establishes no accepted case.
Unsupported or Encrypted takes the case-system export. All five design cites grep back verbatim. No residual
is a schema fact or a permanent destination.

## NEEDS-JOSEPH

1. **NJ-1 — the permission reference.** If PR-6 is lifted, decide centrally whether a permission-reference
   concept may exist and whether it may be destination-eligible. The tension is unusual: the value is
   *published* in a statutory register, yet it resolves to a named person and often a residential address, so
   the ordinary "public means safe" reasoning fails. Alternatives: (a) no such field, and this row's serial
   grouping stays prose forever; (b) the field exists but is search-only and never a branch; (c) the field is
   destination-eligible with a mandatory redacted display label and a local-only alias. I recommend (b) or
   (c), and this row mints nothing.
2. **NJ-2 — the seam with `government.public-authority-record`.** I claim only permissions with continuity and
   abstain on the rest. That leaves one-off registrations and certifications that *do* have a register entry
   but no renewal and no adverse-power sequence in a genuinely ambiguous band. Alternatives: (a) the generic
   row takes all of them (current position, and the safer one); (b) a register entry alone is enough to bring
   them here, which would widen this row toward the "any authority decision" duplicate that Charge 2 alleged.
   I do not think R1b can settle this without the generic row's own research landing.
3. **NJ-3 — visa and consular adjudication.** `government.diplomatic-consular` claims visa adjudication on the
   extraterritorial-post argument and records the same doubt in its own NJ-2, naming this row as the
   alternative. Two live options: (a) function-first, in which case visa issuance is licensing decided at a
   post and comes here, leaving that row with representation, protocol and consular assistance; (b)
   venue-first, its current claim. **Neither row should take it unilaterally**, and I have not. This item is
   stated identically on both sides.
4. **NJ-4 — the mixed publication posture.** P7 should own the rule that a statutorily published register
   entry cannot lower the handling posture of the protected case file behind the same reference, and that
   register rows about many unrelated holders must not be joined into person-level dossiers on name
   similarity. This row records the requirement observationally in `sensitivity_why` and assigns no handling
   class.

## Recommendations to R1c (no neighbour file was touched)

- `government.environmental-regulation` asked whether this row should carry the terminates-at-determination
  seam. It now does, in their wording. Their edge can stand unchanged.
- `construction_property.site-health-safety` marks its government edge as authored one-way pending this side
  (NJ-CP-HS-3). The reciprocal exists now and uses the same fixture and the same discriminator; that open item
  can be closed.
- `government.public-authority-record`, when it lands, owes this row the reciprocal of the
  permission-continuity seam, and should decide NJ-2 with it.

## Self-verification

`python3 -m json.tool` passes. Every `source_type` is in `SOURCE_TYPES`; `contacts` was deliberately dropped
from the schema anchor's list for this row. Every edge target was checked against `roster.json['nodes']`
before writing (`government.public-authority-record`, `government.planning-application`,
`government.environmental-regulation`, `government.professional-regulator`,
`construction_property.building-control`, `construction_property.site-health-safety`,
`business_operations.corporate-regulatory-filings`, `identity`, `medical` — all present). Every
`falls_through_to` name is one of `00`'s nine residuals. Every quoted span was grep-counted in
`00-database-agent-product-design.md`; the one that returned 0 was replaced with the verbatim sentence. No
thresholds, no handling classes, no fields, no path written as a fact. Two files written, both mine.

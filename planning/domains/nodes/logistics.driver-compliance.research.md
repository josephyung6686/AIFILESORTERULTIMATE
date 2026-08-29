# Research memo — `logistics.driver-compliance`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/logistics.driver-compliance.json`
Roster row: template on the fieldless `logistics` schema, `parent_id: null`, placeholder launch

## Result

ACCEPT. The row survives a hostile node test on all three legs. It is the only member of the
`logistics` family whose subject is a natural person, whose operative date points forward rather than
backward, and whose payload includes health data and worker-surveillance data. Its recommendation
differs from the schema default by a **double deletion** — no counterparty level and, uniquely in the
family, **no subject level** — and the second deletion is the row's own argument, not an inheritance.

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `role_split: []`, `also_holds_with: []`.
Seven collisions, each an object naming one fixture, both owners and the discriminating evidence.

Sources: the standing brief; the stamped assignment; `planning/00-database-agent-product-design.md`
by targeted grep; `logistics.json`; `logistics.fleet-vehicle.json`; the driver-compliance mentions in
`manufacturing.environmental-compliance.json`; `construction_property.site-health-safety.json` edges;
`roster.json`; `canonical_fields.json`; `legal.practice-matter-file.research.md` for calibration.

## The charge — the strongest case that this row should not exist

**C1 It is a list of document types.** Licence, medical, training certificate, tachograph are four
unrelated forms glued by the word *driver*; document kinds are `work_type` values and the schema
already carries five of them in its own array.
**C2 It is the mirror of `logistics.fleet-vehicle`** — same schema, same continuing operator duty,
same `.ddd` downloads, only the subject differs. CONNECTION gives that situation an edge,
`role_split`, and an edge is cheaper than a row.
**C3 It is `hr` for one occupation.** A driver is a job title; job titles are values.
`hr.training-development`, `hr.workplace-health-safety` and `hr.employee-relations` already exist.
**C4 Its evidence is never-alone all the way down** — a person's name plus a document-type word, the
brief's canonical example of evidence that can never activate.
**C5 The schema default already covers it** — its third level is *document function*, and licence,
medical and training are functions.
**C6 It is defined by an absence.** "Compliance" names files that are *not* operational — not a
consignment, not a run sheet, not a stock movement. A row defined by what its files are not is a
residual home.

## The answers

**C4 and C6 first, because they are fatal if true.** They fail on the same ground: the fingerprint is
a co-occurring structure, not a vocabulary. Four items carry it. The **per-category expiry matrix** —
a driving entitlement is not one permission with one expiry but a set of vehicle categories each with
its own valid-from and valid-to date from a licensing authority; no certificate, membership card,
insurance schedule or passport has that shape. The **activity-interval structure** — intervals
labelled driving, other work, availability and rest attributed to one cardholder across *changing*
vehicle identifiers, with daily and weekly aggregates. The **cycle-and-card relation** — hours that
only make sense as a fraction of a stated cycle total terminating in a card with its own expiry. The
**fitness-against-a-licence-group** conclusion — a clinical statement tied to a permission rather
than to a job. None is a word, a name or an absence.

The charge is nonetheless right about what does *not* fire, which is why `never_alone` runs to nine
entries: the occupation word, a person's name in any position, the words licence/medical/CPC/
compliance, a licence-number-shaped token, a bare expiry date, a photograph of a card, an issuing
authority's name, a folder called Drivers, and — running the other way — any amount due, rate,
pay-hours total or tax treatment, whose *presence* is evidence against this row. Every one is true of
at least one fixture in the file list.

**C1.** Four document types would be a list. What makes them a situation is that they are not
independent: the medical renews the entitlement, the training hours redeem into the card, the
activity download produces the infringement, and the expiry register's columns are the other three
artefacts' due dates. That referential closure is the same test `fleet-vehicle` used ("a defect
reference closed by a rectification record"), satisfied here by a longer chain. A list of forms has
no such chain.

**C5.** The default's first level is the carrier or counterparty and its second the custody subject.
This row has neither — no consignment, no quantity of goods, no place of delivery, no acknowledgement
of receipt, i.e. none of the four elements the schema names as the family fingerprint. Under the
default a driver dossier would scatter across issuer-shaped branches (licensing authority, clinician,
training provider, analysis bureau — none a counterparty to anything) or land homeless.

**C2, the hardest limb.** The mirror test fails in both directions. Substituting *driver* for *asset*
in `fleet-vehicle`'s template breaks that row's stated argument, that a destination named for the
asset "is acceptable here — unlike the consignee, an operated vehicle is the filer's own subject". A
person is not the filer's own subject: the permission is conferred by a state on the person, is
portable across employers and survives the job; the operator holds a copy, not the thing. So the
level `fleet-vehicle` keeps is exactly the level this row must delete. Substituting *asset* for
*driver* here breaks this row: a vehicle has no medical fitness, no entitlement categories, no
training cycle, no penalty points, and an inspection sheet has no subject who can be harmed by
aggregation. Formally, `role_split` requires *different field keys*; `logistics` declares none under
PR-6, so the edge is unavailable and the difference has to live in detection and privacy — where it
genuinely does. `fleet-vehicle` reached the same conclusion independently and wrote a `collides_with`
against this row rather than a `role_split`.

**C3.** The decisive fixture is the owner-driver. A self-employed courier or an agency driver holds
the complete set — entitlement summary, medical, periodic training, card, activity download — with no
employer, no HR function, no learning provision and no health-surveillance programme. The evidence
proves permission from a state, not participation in an employer's programme. Where an employer *is*
present the files genuinely double, and the boundary is drawn on structure rather than holder:
cycle-and-card versus curriculum-and-register; licence-group fitness versus hazard-and-exposure
surveillance; computed-from-intervals versus stage-of-a-procedure.

## The node test against the schema default

The `logistics` default is prose because the schema declares no fields: *carrier or trading
counterparty only where the corpus spans more than one → the custody subject (consignment or
container; or vehicle, depot, working day) → document function → time as a leaf*, not time-first, with
the family principle **the consignee is a party, never a folder**.

**Leg 1, detection — differs.** As above. The schema's own file already names two structures no
consignment-shaped detector can produce, and names them as distinct rather than as consignment
variants: *"a driving-hours or tachograph structure: repeated activity intervals (driving, other
work, availability, rest) attributed to one named driver and one vehicle across a stated period, with
statutory limits or infringement flags"* and *"a driver-entitlement structure pairing a named person
with licence categories, expiry dates, a medical-fitness statement or certificate, and
periodic-training or qualification-card evidence"*. (Those are the schema's words, not `00`'s;
provenance inference.) The schema anticipated this row; this memo supplies the evidence and the
boundaries it did not.

**Leg 2, dimensions — differs by a deletion no sibling makes.** `fleet-vehicle` deletes the
counterparty level and keeps its subject. This row deletes both. The counterparty deletion is
borrowed reasoning and is not claimed as novel. The subject deletion is this row's own and is the
uncomfortable one, because the driver dossier is the *most* coherent grouping in the family and is
exactly what a transport manager asks for. It must still not be built: `00` — *"A folder should not
become a collection point for everything produced by the same person or organization"* — and the
family principle already refuses a person-shaped level for a mere counterparty, so a person under the
filer's authority deserves at least that much. What remains is function → expiry or covered period as
a leaf, function first because `00`: *"For document and record domains, project, function, or subject
usually comes before time because putting year first scatters related work across calendar folders."*
A person's checks, medicals and modules interleave across every year they drive, and a year-first
tree separates an infringement from the acknowledgement that closed it.

The row also contributes a distinction the family did not have: **the operative date inverts.**
Elsewhere in `logistics` the date records a past custody event; here it records a future lapse, so a
time level built from issue dates would bury the only date the file is retained for. `time_first:
false` is therefore right here for a *different* reason than in the default — a template difference,
not an agreement.

**Leg 3, privacy — differs, and is the strongest leg.** The default's concern is third-party
*transactional* data. This row adds health data about a person other than the filer (a medical
examination report is vision, cardiac, neurological, diabetes and substance-use findings; a
drug-and-alcohol result is the same) and granular worker surveillance (a driver-card download is a
minute-by-minute activity history across every vehicle the person drove, and its printed reports
state where the working day began and ended). It adds adverse findings — endorsements, penalty points
— and quasi-disciplinary artefacts, and it inverts the holder-subject relation: the third party is a
person under the filer's authority, not a counterparty to a bargain. Four rules follow in
`sensitivity_why` that the default does not state: no person-shaped destination despite the dossier's
coherence; no cross-driver aggregation, including no reconstruction of a per-person profile from
vehicle-unit records; no default remote or model path; and no clinical, entitlement or compliance
verdicts of the product's own.

Three legs, three differences. Accept.

## Files considered and rejected

- **`Counterbalance forklift operator certificate - accrediting body.pdf`** — the most tempting false
  positive: same layout, same expiry, same named person, and it sits in the same folder because both
  are "driver tickets" colloquially. Not this row's — the class named is workplace equipment rather
  than a road-vehicle category, there is no licensing-authority block and no per-category expiry
  matrix, and the sponsoring organisation is an employer rather than an issuer. Goes to
  `hr.training-development`. Carried as a file example so the discriminator is testable.
- **Payslips, agency invoices, driver-engagement contracts** — a payslip names a driver, states hours
  and sits in the same drawer. It proves payment, not permission; the engagement contract proves a
  bargain. `never_alone` encodes this as a reverse rule.
- **A rota, a run sheet, a holiday tracker** — all are people-against-dates spreadsheets that look
  like an expiry register. Discriminator is direction: a register's date columns are *future* and
  carry a due or overdue disposition; a rota's are past or present and carry a shift.
- **Vehicle insurance schedules with named drivers** — the named-driver list pairs people with
  entitlement-shaped facts, but the document is about an asset and a policy. `fleet-vehicle`'s.
- **Licence-renewal payment confirmations, course booking receipts, medical invoices** — Receipts and
  Confirmations. Building a dossier out of payment history is what that residual exists to prevent.
- **Contact exports containing drivers** — not activated; `00` holds that contact material *"should
  normally be privacy-protected rather than used to create folder proposals"*.
- **A live tachograph-analysis account or fleet-compliance SaaS** — a source system, not a file node.
  A bounded export with a readable manifest is represented; connector ingestion is a later decision.
- **Jurisdiction-specific category letters, cycle totals, medical intervals** — deliberately not
  enumerated; see NJ-DC-4.

## The collision fixture

**`Driving licence photocard - front and back.jpg`.** Identical bytes in two corpora: a person's own
documents folder beside a passport, and an operator's driver file inside a per-person subfolder.
Everything visible is shared — portrait, name, date of birth, address, category strip, expiry. What
discriminates is **holder-versus-subject plus an operator anchor**: a check reference, a per-category
expiry matrix, a counterpart medical or training record, or an expiry-register row. Absent an anchor
`identity.core-documents` wins, and it wins by default rather than by tie-break, because a card image
alone can never establish that a third party holds a duty record about its subject. This is the
concrete form of C4, and conceding it is what makes the rest of the row honest. A second is carried:
**`Vehicle unit download - YJ19 KXR - 2026-07.ddd`**, identical in extension, period and producing
operator to the driver-card download.

## Reciprocal boundaries

1. **`logistics.fleet-vehicle`** — the two `.ddd` downloads. Mine: the driver-card download, one
   person across changing vehicles, plus entitlement, fitness and training. Theirs: the vehicle-unit
   download, one asset across changing cardholders. Discriminator: which subject the records are
   attributed to. That row wrote this seam first; this row confirms it independently and endorses its
   prohibition on reconstructing one from the other. The **daily walkaround sheet** is left
   unresolved by both sides — the asset's defect record and the person's discharge of a check duty in
   the same bytes, no honest discriminator — and both carry it as a file example.
2. **`hr.workplace-health-safety`** — the completed driver medical. Mine: fitness stated against a
   licence group, renewing a state permission, existing for an owner-driver with no employer. Theirs:
   health surveillance as the employer's administered duty, keyed on a hazard and an exposure
   population. Discriminator: the authority the fitness is stated against.
3. **`hr.training-development`** — the seven-hour module certificate. Mine: hours accumulating toward
   a stated cycle terminating in a card. Theirs: a delivery record inside a learning provision —
   catalogue entry, provider contract, completion register. Discriminator: the cycle-and-card
   relation.
4. **`identity.core-documents`** — the photocard scan; directions and discriminator as above.
5. **`career.credentials-licenses`** — the ADR certificate or a qualification card. Mine: an operator
   holding it *about a worker*. Theirs: the credential's own subject keeping the record of their own
   standing. Discriminator: whose dossier it sits in.
6. **`hr.employee-relations`** — the infringement packet. Mine: the analysis artefact computed from
   intervals. Theirs: the invitation, hearing note, outcome, appeal. Discriminator:
   derived-from-recorded-activity versus stage-of-a-procedure.
7. **`business_operations.compliance-audit`** — an audit sampling driver files. Mine: the sampled
   evidence. Theirs: the instrument and its findings. Discriminator: about a person's permission
   versus about a system's conformity.

## Neighbours considered that got no edge

- **`manufacturing`** (`must_consider`) — the in-plant operator ticket is the forklift fixture, which
  routes to `hr.training-development`; `manufacturing`'s rows anchor on transformation, release and
  asset maintenance, not on a person's state-conferred permission. The schema-level seam already
  exists and is not sharpened here.
- **`retail_hospitality`** (`must_consider`) — its licensing row is `premises-licensing`, whose
  subject is a venue's permission to trade. Venue permission and person permission share the word
  *licence* and nothing else, and `never_alone` already refuses the word. No same-evidence mutex.
- **`construction_property.site-health-safety`** — anchors on *a hazard and its controls*, written
  for an inspector, and does not name this row in its own edges. A toolbox-talk register signed by
  drivers is many people against one hazard. Recorded as a `needs_llm` ambiguity, not an edge.
- **`government.permit-licensing`** — the authority's side of the same permissions. Arguable, but its
  artefacts (application files, decision notices, enforcement registers) are not this row's fixtures,
  and `manufacturing.environmental-compliance`'s NJ-MEC-1 already raises a global `authorisation` key
  touching all of these. Deferred to R1c rather than guessed.
- **`medical`** — a coactivation this row cannot author. See NJ-DC-2.

## Fields

`fields: []` and `proposed_fields: []` are required: the schema declares none under PR-6 and a
template may not mint them. `record_type` is the schema's own proposal and would carry the function
level. A record-subject key is the real gap and is raised as NJ-DC-1 rather than minted — minting a
person key in a row whose entire privacy argument is that a person must not become a folder would be
self-contradicting. `authorisation` is `manufacturing.environmental-compliance`'s proposal and is not
re-proposed as a variant here, per that row's own note to R1c. `people` is canonical but is the
Photos depicted-persons role and carries no subject-of-record reading; borrowing it would silently
authorise the aggregation this row forbids.

## Open questions — NEEDS-JOSEPH

**NJ-DC-1 — should the driver dossier be foldered after all?** The family forbids a person level, but
this is the one case where the person is the record's *subject* rather than a counterparty, as a
patient is in `medical`. Alternatives: (a) never foldered, held as a group with a display alias, this
row's recommendation; (b) a protected-area exception mirroring whatever `medical.personal-health-
records` is granted for its own subject; (c) a canonical record-subject key adjudicated globally.
This is `logistics`'s NJ-LOG-4 seen from the row that generates it; R1c should answer it once.

**NJ-DC-2 — the missing `medical` coactivation.** A driver medical holds `logistics` and `medical`
facts in the same bytes on disjoint evidence. This row cannot say so: `also_holds_with` is
schema-to-schema only under CONNECTION §5 and this row is a template. `logistics` lists `government`,
`legal`, `manufacturing`, `construction_property.materials-delivery` and `photos` there but **not**
`medical`. Recommendation for R1c: add it at the schema level on this row's evidence. Recorded as a
recommendation, not an edit — the schema file is not this row's to touch.

**NJ-DC-3 — the `career.credentials-licenses` role split.** Same certificate, holder-is-subject
versus operator-holds-about-worker: textbook `role_split`, but the edge needs different field keys
and this schema declares none, so it is carried as a collision. If PR-6 is lifted, R1c should decide
whether the split is expressed by a record-subject key or by keeping two rows.

**NJ-DC-4 — jurisdiction.** Entitlement regimes, category letters, cycle totals and medical intervals
vary by country. This row recognises structure only and names none of them. If R6 builds a rule
family for entitlement tokens it will need a gazetteer decision; this row writes no pattern.

**NJ-DC-5 — `fleet-vehicle`'s `also_holds_with` entry naming this row.** That row lists
`logistics.driver-compliance` under `also_holds_with` for the walkaround sheet. Under CONNECTION §5
as this dispatch states it, `also_holds_with` is schema-to-schema only, so a template-to-template
entry there may be a defect. This row leaves its own `also_holds_with` empty and records the intent
here instead. R1c should normalise the entry or relax §5; the substance — that the sheet is honestly
both and neither may copy the other's facts — is agreed by both sides either way.

## Self-verification

- `python3 -m json.tool` parses the node file.
- Key set matches the landed sibling `logistics.fleet-vehicle.json`, including its `node_test` and
  `proposed_context_terms` keys.
- Six `00` quotations grep-verified verbatim, each returning exactly one match: project-function-
  before-time; protected-records; collection-point; address-book privacy-protection;
  archives-without-unpacking; university-name-alone. The two structure quotations in `node_test` are
  verbatim from `logistics.json`, marked as the schema's words, provenance inference.
- Every `collides_with` entry is an object with a `SAME FIXTURE BOTH SIDES` signal naming one file,
  both owners and a discriminating evidence item. No bare id strings. `also_holds_with` empty.
- All seven neighbour ids confirmed present in `roster.json`; `medical` and `photos` confirmed for
  the `also_schema` references in file examples. All six `falls_through_to` names are `00` §7.3
  residuals.
- Every `file_examples.source_type` is in `SOURCE_TYPES`; no file example writes a folder path as a
  fact; every one carries `"a folder path"` in `must_not_conclude`.
- No threshold numbers, no confidence scores, no handling classes, no jurisdiction names, no category
  letters, no regexes, no fabricated quotations.
- Files written: exactly the two assigned. No roster, schema, sibling, canonical-fields, `src/` or
  SPEC file was modified.

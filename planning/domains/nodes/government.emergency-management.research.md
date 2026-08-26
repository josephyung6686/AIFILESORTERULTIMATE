# Research memo — `government.emergency-management`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.emergency-management.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accept.** The row survives a serious attempt to kill it. Its distinct job is the *coordinating* side of a
civil-protection activation and the standing preparedness apparatus around it. It differs from the
`government` schema's default template on all three legs of the node test, not one — and the privacy leg
is a difference the schema anchor's own sensitivity paragraph does not contain.

It stays fieldless, dimensionless, and deliberately shallow. It does not become a hazard taxonomy, a
doctrine catalogue, or a per-jurisdiction filing tree.

---

## The charge — the strongest case that this row should not exist

I wrote the prosecution first. Five counts, and the third is the dangerous one.

**Count 1 — it is a work_type list wearing a node costume.** The `one_line_hint` reads like an enumeration:
"risk assessments, plans, exercises, live incident logs, situation reports and post-incident review." Those
are six document types. The `government` anchor already carries thirteen `work_types` strings, each one a
comma-list of exactly this shape — "grant call, received application, assessment, award, monitoring report,
or closure record on the funder side". The obvious disposal is a fourteenth string: *"risk assessment,
emergency plan, exercise report, activation log, situation report, or after-action report on the
civil-protection side"*. Under the brief's own rule that **work types are values**, that would close the id.

**Count 2 — it is a lifecycle.** Prepare → respond → recover → review is a stage sequence. Stages are not
filing worlds; the schema's `work_types` already absorb lifecycle stages of every other government function
(rulemaking, procurement, FOI) without minting a node per stage.

**Count 3 — it duplicates a landed neighbour, and that neighbour said so first.** `business_operations.risk-register`
already folded business continuity into itself and authored the boundary against this id *before this row
existed*, in its own words: "A public authority's flood or major-incident plan is structurally identical to
a corporate continuity plan." If a landed row can already name the fixture and state the discriminator, the
seam may be adequately covered from that side alone, and this row is the redundant half.

**Count 4 — its evidence is never-alone.** An emergency-management agency letterhead is an organisation name.
The word *emergency* is a token that appears on `Emergency Contacts.xlsx`, on an emergency-department
discharge summary, and on an SRE `Incident 4471` postmortem. A hazard scoring grid is a shape shared with
corporate risk, project prioritisation, and supplier ratings. Strip all of those and the residue may be
nothing.

**Count 5 — it is defined by absence.** "Records about things that have not happened yet" is not a situation.

### Defeating the charge

**Against Count 1 and Count 2.** The decisive test is not whether the row *contains* work types — every row
does — but whether it brings something a value cannot bring. A `work_type` value cannot carry its own
grouping anchor, and it cannot carry its own privacy rule. "Consultation response analysis" needs neither:
it groups on the consultation reference the schema's `grouping_reasons` already names, and it inherits the
schema's posture unchanged. This row brings **both**.

Its grouping anchor is a **named activation bounded by declaration and stand-down, subdivided into
operational periods**. Read the schema anchor's `grouping_reasons` list: every entry is anchored by "an
exact bill, rulemaking, consultation, application, permit, case, request, procurement, election, or
programme reference". *An activation has no docket.* `ICS-209 Incident Status Summary - Ridgeline Fire - OP 6`
carries an incident name and an operational period with a start and end clock time, and no case, docket, or
application reference anywhere on the form. The schema's anchor vocabulary cannot address it. That is a
structural gap, not a stylistic one, and it is why I put the six tempting document types **into
`work_types` in the JSON deliberately** — conceding Count 1's premise while denying its conclusion.

**Against Count 3.** I read the neighbour and I am writing the return leg it explicitly asked for
(it filed the gap as NJ-BO-RR-4: "Six boundaries here are authored one-way … `government.emergency-management`.
None names `business_operations.risk-register`."). Two rows that each need the other named is the definition
of a reciprocal boundary, not of a duplicate. But I do not adopt its wording unchanged: it discriminates on
"a **statutory emergency duty**, a public-body issuing authority and a plan addressed to the public". A
statutory duty is frequently not legible in the bytes, and "addressed to the public" fails on the restricted
annex. I refine the discriminator to the **protected subject** — a population or geography with a
role-by-agency responsibility matrix and a lead agency per hazard row (this row) versus one organisation's
own services with recovery time objectives, critical-activity analysis and internal treatment owners (that
row) — and I name the same fixture on both sides. The refinement is recorded below as a recommendation to
R1c, not as an edit to that row.

**Against Count 4.** Conceded entirely, and encoded. Eleven `never_alone` entries, each written against a
file that would otherwise trip it. What survives the strip is not a word but a **structure**: a numbered
command form carrying an incident name *and* an operational period *and* a command-position prepared-by
slot; a sequentially numbered situation report with an as-at time *and* a next-report time; an inject list
with a delivering controller *and* an evaluated capability. None of those is a word, an extension, an
organisation, or a length.

**Against Count 5.** Refuted by the live half. An activation log, a shelter roster and a damage assessment
are records of things that unambiguously happened.

**Verdict: accept.** But note what the charge cost the row — the entire preparedness half (plans, registers,
exercises) is genuinely close to being work types on the schema, and it is the *activation* half that carries
the node. If R1c ever narrows this row, narrow it toward the activation, not away from it.

---

## The node test, argued in full

CONNECTION's test: a template row exists only when its **detection signals**, **recommended dimensions**, or
**privacy rules** differ from its schema's default. All three differ here; I argue each separately.

**The schema's default template, stated.** The `government` anchor's `template.why` is explicit even though
its `dimension_order` is empty under PR-6: *"authority-side function or bounded proceeding/case/programme
first, then an exact reference or cycle, then work type; named people must not become the organizing
dimension."* `time_first: false`, on the design's own reasoning: "For document and record domains, project,
function, or subject usually comes before time because putting year first scatters related work across
calendar folders." Its recognition gate is "an evidenced public body acts as legislature, regulator,
decision-maker, programme administrator, records holder, statistical authority, election administrator, or
citizen-casework office". Its sensitivity is `potentially_sensitive` on a list of citizen casework,
submissions, unsuccessful bids, investigations, restricted statistics and election operations.

**Leg 1 — detection signals differ.** The schema's deterministic list is uniformly *issuer-role plus
proceeding structure*: a bill identifier plus an issuing-legislature block, an election packet plus an
administering-office block. Mine is *command-and-coordination structure*, and it works when the issuing
block is illegible — which matters, because activation documents are produced at speed on shared templates.
The eight signals in the JSON turn on form-series identifiers, operational-period boundaries, activation
levels, role-by-agency matrices, timed injects with delivering controllers, and lead-agency-per-hazard-row
registers. Not one of those appears anywhere in the schema anchor. Conversely the schema's nine
role-signals do not fire on `SitRep 007 - Storm Bronagh` at all. The overlap is close to nil, which is a
stronger differentiation than most template rows can claim.

**Leg 2 — recommended dimensions differ, in a specific and limited way.** First level: same *kind* as the
default (a bounded thing before time) but different *nature* — an activation, plan, or exercise family, not
a docketed proceeding, because there is no docket to order on. Second level: **operational period**, a clock
slice, where the schema default puts "an exact reference or cycle". This is the row's most contestable claim
and I will not overstate it. `ICS-209 … OP 6` and `SitRep 007` are unintelligible outside the period they
report on — the same relation the design draws when it says Homework 3 is meaningless without the course —
so the period is a genuine parent dimension, not a timestamp. But it *is* time-shaped, and the schema
default deliberately keeps time off the front. I resolve it honestly rather than smoothly: `time_first`
stays **false**, because the preparedness half (plans, annexes, registers, exercise libraries) is long-lived
and function-primary and would be scattered by a year-first tree. The departure is at level two only.
Third level: work type, as in the default.

**Leg 3 — privacy rules differ, and this is the strongest leg.** The schema's posture is *uniformly*
protective: authority holdings may contain sensitive material, therefore treat them carefully. This row's
posture is **split inside one version family**, which the schema has no way to express. A multi-agency flood
plan body carries a public-publication footer — publishing it is the point, since an evacuation plan works
only if people read it — while `Annex C` of the *same versioned document* lists named residents with
street addresses, mobility needs, power-dependent medical equipment and next-of-kin contacts. Same version
number, same folder, opposite posture. The rule this row adds, which the schema does not contain, is that
**a publishable parent must never lower the posture of a co-versioned annex**, and that a live activation's
name is itself disclosive as a branch label. The design's constraint applies throughout: "Privacy policy
must be enforced before content reaches any model or external connector." The schema's sensitivity list
names casework, submissions, bids, investigations and ballots; it names no vulnerable-persons register, no
shelter roster, and no critical-infrastructure single-point-of-failure annex. Those are this row's classes.

Three legs, three differences. The node stands.

---

## Files considered and rejected

A row that only lists what it holds has not been researched. These are the tempting false positives, each
with its discriminator.

| Considered | Why it is not this row's evidence |
|---|---|
| **`Emergency Contacts.xlsx`** (HR onboarding, school form, gym membership) | The token `emergency` appears only as a **field label**. Name/relationship/phone columns, no event, no activation, no coordinating body. A field label is not a situation. → `never_alone`; **Protected Records**. |
| **`Emergency Department Discharge Summary - 2026-05-02.pdf`** | Pure word collision, and the one a filename-first classifier gets wrong most often. Discriminator: a **patient encounter** — clinician, diagnosis, treatment. `medical.personal-health-records`; edge authored. |
| **`Incident 4471 - Sev1 postmortem - checkout API.md`** | The **collision fixture**; see below. |
| **`Fire Risk Assessment - 14 Mill Street - 2026.pdf`** | Fires hazard, plan, drill, evacuation, muster. Discriminator: **scope of duty** — one premises, one responsible person, a duty owed to occupants. `hr.workplace-health-safety`; edge authored. |
| **A corporate Business Continuity Plan / DR runbook** | Triggers, call trees, roles, recovery steps — structurally near-identical. Discriminator: **protected subject** — one organisation's own services versus a population. `business_operations.risk-register`; reciprocal edge authored. |
| **`Prepare Your Household - Emergency Kit Checklist.pdf`** | Agency logo, seal, publication footer, hazard vocabulary, and *zero* holder-side workflow. The schema anchor's own rule disposes of it: publication by government is not authority-side custody. → **Reading Inbox**. |
| **A news article or press photo of a flood** | Topic, not custody. No coordinating posture. → Reading Inbox / One-Off Images. |
| **A charity's disaster-appeal fundraising pack and donor report** | Same event name throughout. Discriminator: the artifact's **purpose is solicitation and stewardship**, not coordination. `nonprofit` alone — this is the case where the `also_holds_with` edge does *not* apply. |
| **A school lockdown-drill notice received by a parent** | Recipient-side receipt of an institutional notice. → **Independent Records**. |
| **A first-aid or incident-command training certificate** | A credential about a person, not a coordination record. → Identity/education; Independent Records. |
| **An emergency-powers statutory instrument, downloaded** | Legal vocabulary plus the event name. Discriminator: a **forum and an instrument**, not a coordination artifact. `legal`; Reading Inbox if merely held. |
| **A published public-inquiry report into a disaster** | Contains the activation logs verbatim, quoted as evidence. Discriminator: it is a **proceeding's output**, held for reading. → Reading Inbox; the quoting does not convert the logs. |
| **A blank ICS form pack or plan template** | Fires every structural signal with every slot empty. It is a `work_type`, not a record, and must never produce an incident, agency, or person fact. → `never_alone`; Independent Records. |
| **An insurance claim after a disaster** | Policy number, loss adjuster, schedule of cover. `finance.insurance-*`. Left **unedged** — the confusion is about the event name, not about the document. |
| **A military unit's deployment order under aid-to-civil-authority** | Genuinely adjacent, and `government.defence-veterans` is on the roster. Left **unedged deliberately**: I could not name a fixture whose *bytes* are contested, only a scenario in which both rows hold different documents. Recorded as NJ-GEM-4 rather than guessed. |

---

## The collision fixture

**`Incident 4471 - Sev1 postmortem - checkout API.md`.**

It is the best false positive this row has because the resemblance is not accidental — software and service
operations **borrowed** incident-command vocabulary wholesale. The file carries an incident number, a
severity level, an **Incident Commander** role, a timestamped chronological timeline, an *IC handoff*, and a
heading reading *post-incident review*. Every one of those tokens is in this row's hint line. A
vocabulary-driven classifier fires on it with high confidence.

**What discriminates it: the impacted entity.** Here it is a named *service* with an error rate, a rollback,
a customer-facing status page, and action items assigned to engineers with ticket references. This row's
impacted entity is a *population, geography, or multi-agency arrangement*, with responders, shelters,
casualties, mutual-aid requests, and a lead agency per hazard. Neither document's vocabulary distinguishes
them; only the object of the harm does. The pair is edged to `business_operations.support-operations`, and
the same fixture is named on both sides.

The mirror case — a file that is genuinely **both** — is `Damage Assessment - Project Worksheet PW-0142`,
which carries the declared-event reference *and* a recovery-grant programme reference in one header. That is
`also_holds_with government.grant-programme-administration`, not a contest: coactivation, per the design's
abstract-that-is-also-an-application pattern.

---

## Reciprocal boundaries

Ten `collides_with` edges and two `also_holds_with`. Every one is stated in **both** directions in the JSON's
`signal` text, with the same fixture named on both sides. Summarised:

| Neighbour | Theirs | Mine | Contested fixture |
|---|---|---|---|
| `business_operations.risk-register` | one organisation's own continuity, RTOs, internal treatment owners | a population/geography, role-by-agency matrix, lead agency per hazard | `Community Risk Register 2026` vs a corporate register. **Reciprocal** — that row authored the first leg |
| `business_operations.support-operations` | a service with an error rate, rollback, status page | a population with responders, shelters, mutual aid | `Incident 4471 - Sev1 postmortem` |
| `hr.workplace-health-safety` | one premises, one responsible person, duty to occupants | a jurisdiction, duty to a population | `Fire Risk Assessment - 14 Mill Street` |
| `government.public-health-administration` | a standing programme with a reporting cycle | a declared activation with levels, operational periods, sitreps | a mass-vaccination clinic plan, run either way |
| `government.municipal-administration` | a numbered committee paper with agenda pagination and a resolution | the plan, its annexes, its activation records | `Emergency Plan adoption - Cabinet paper 12` vs `Multi-Agency Flood Plan v4.2` |
| `government.public-authority-record` | a bounded proceeding with an exact reference | an activation bounded by declaration and stand-down | any activation packet on public-body letterhead |
| `government.social-services-casework` | an enduring case for one household, case reference, caseworker | a roster registered against one activation, closed at stand-down | `Shelter Registration - Northgate High School` |
| `manufacturing.hse-incident` | one injury or release at one facility, root cause, regulator notification | the multi-agency coordination record | a major industrial accident, which triggers both |
| `medical.personal-health-records` | a patient encounter — clinician, diagnosis, treatment | a coordination record with no encounter | `Emergency Department discharge summary` |
| `legal` | a forum, parties, an instrument | the artifact produced to run or review the response | an inquiry bundle quoting the activation logs |
| `government.grant-programme-administration` *(also_holds)* | the funder's programme record | the recovery family member | `Project Worksheet PW-0142` — both, legally |
| `nonprofit` *(also_holds)* | the organisation's own record | the coordinated response member | a shelter activation log; becomes a contest only for a fundraising appeal |

**Nine of these are one-way from my side and R1c owes the reciprocal.** Only `business_operations.risk-register`
is now mutual. Two of them — `government.social-services-casework` and `medical.personal-health-records` —
are **protected on both sides**, so per CONNECTION's stricter-side-wins principle R1c should state the merged
wording from the protected side and neither row may pull the other's material toward a less protected group.

---

## Deliberate non-edges

- **`government.elections-administration`** — its own deterministic list already contains an "incident log",
  and I nearly edged it. Rejected: an election incident log is anchored to a polling place and a ballot
  account, and that row named it first. No contested bytes.
- **`government.environmental-regulation`** — flood-risk mapping is produced there and consumed here.
  Production/consumption is not an evidence contest.
- **`government.transport-authority`, `government.housing-authority`, `government.parks-public-lands`** —
  each has an emergency annex. Edging all of them would turn this row into a hub and say nothing. The
  `government.public-authority-record` edge covers the general case.
- **`government.defence-veterans`** — see NJ-GEM-4.
- **`engineering.risk-analysis-fmea`** — an FMEA scores a part or process step into an RPN against a design
  revision. Genuinely different unit; `business_operations.risk-register` already holds that seam.
- **`business_operations.policy-handbook`** — a controlled-document header on an emergency plan is real, but
  the plan's working content is operational, not governing. Thin; left unedged.

---

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `role_split: []` — all intentional.

`proposed_fields` is empty **on the schema anchor's own instruction**, not from lack of candidates. Its
`open_question` states that if PR-6 is lifted, a minimal role-safe vocabulary should be adjudicated
"centrally rather than in children". The two concepts this row would need are argued here and not minted:

- an **activation anchor** (a named incident with declaration and stand-down boundaries) — no canonical key
  covers it; a proceeding or case reference is the wrong shape because an activation has no docket;
- an **operational period** — not a date and not a fiscal period; a clock slice with a start and an end,
  internal to one activation. `fiscal_period` (already proposed and seconded by
  `business_operations.risk-register`) is the wrong granularity and the wrong calendar; I do not propose a
  variant of it, per the brief's reuse-don't-mint rule.

Rejected outright: `organization` (the lead-agency column is a *row value* in a register, not a holder
fact, and the schema's never-alone rule forbids activating on an agency name), `record_type` and
`artifact_type` (scoped elsewhere, and they would only re-encode `work_types`), `purpose` (scoped to
College Applications under the current canonical record), and any hazard, activation-level, or
jurisdiction key.

`role_split` is empty because the schema declares no field keys to split on. The genuine role question —
coordinating body versus participating agency versus affected member of the public — is currently carried
by recognition prose and by NJ-GEM-1 rather than by a field.

---

## Sparse-file discipline

This row needs it more than most, because activation documents are produced **in bursts under duress**. One
hour of a real response yields `sitrep7.docx` with empty header slots, `log.txt`, `whiteboard 0430.jpg`, and
three phone photos of a map. Every one of them is adjacent to correctly-recognised members and every one of
them is bare.

The rule, encoded on the fixtures with `group_without_copying_facts: true`: those files may **join** an
accepted activation group and must **not** acquire an incident name, event, agency, timestamp, location, or
activation-level fact from it. Activation is not grouping. Adjacency in one save burst is explicitly not
proof — "A session should never be treated as proof of topic" — and a status-board photo re-saved through a
messaging app loses its capture metadata, which proves nothing either: "the system must not mistake the
absence of EXIF for proof that an image is a screenshot".

---

## NEEDS-JOSEPH

- **NJ-GEM-1 · Non-government holders.** Hospitals, utilities, ports, school districts, faith groups and
  relief charities produce genuine multi-agency response records under command-structure vocabulary — a
  hospital's incident-command forms are the same forms. But this row sits on a schema whose gate is "an
  evidenced public body acts … in an authority-side role", and whose never-alone list excludes private
  organisations. Alternatives: **(a)** participation in an evidenced multi-agency arrangement is itself
  sufficient to activate the `government` schema for a private holder — cost: it punctures the schema's
  owner gate, which is the anchor's central discipline; **(b)** those files route to
  `business_operations` / `nonprofit` with only a coactivation edge here — cost: the response packet is
  split by holder type, and the hospital's ICS-214 lands somewhere other than the coordination file it
  belongs to; **(c)** user-confirmed, per the anchor's existing hybrid-body question. My inclination is
  (b) with a strong coactivation edge, but this is a schema-level decision and I have not guessed it.
- **NJ-GEM-2 · The split-posture annex.** The catalogue can record `potentially_sensitive` for a file but
  has no way to say that one member of a *version family* must not inherit its parent's publicity.
  Alternatives: **(a)** leave it as prose in `sensitivity_why` — cost: the row's sharpest privacy rule is
  unenforceable; **(b)** make it a group-level rule (a family may hold mixed postures and the strictest
  member governs export, not display) — cost: new machinery; **(c)** hand it to P7 — cost: P7 owns handling
  classes, and this is a *relationship* rule, not a class. This is the same class of defect
  `business_operations.risk-register` filed as NJ-BO-RR-5 about theme-named branches, and the two should
  probably be decided together.
- **NJ-GEM-3 · Exercise versus real.** Exercise artifacts imitate real activation artifacts down to the form
  numbers, and their scenarios deliberately borrow real event names and real geography. Alternatives:
  **(a)** an exercise marker is a hard grouping barrier the catalogue enforces — cost: markers are often only
  in a footer, and a missed marker silently merges a drill into a real response; **(b)** it is a
  user-review prompt only — cost: the merge happens and the user must catch it. Consequence either way:
  never summarise an exercise scenario as though it described events.
- **NJ-GEM-4 · Aid to civil authority.** `government.defence-veterans` is on the roster and military support
  to civil emergencies is real, but I could not name a fixture whose *bytes* are contested — only scenarios
  where both rows hold different documents. Left unedged rather than guessed. R1c should decide whether a
  mission-tasking record crossing that boundary is one.

---

## Recommendations to R1c (cross-row; I edited nothing)

1. `business_operations.risk-register` filed NJ-BO-RR-4 noting no reciprocal existed here. **It now exists**
   and that row can be marked mutual rather than one-way.
2. Its discriminator wording — "a statutory emergency duty, a public-body issuing authority and a plan
   addressed to the public" — should be **refined on both sides** to the protected-subject test above: a
   statutory duty is rarely legible in the bytes, and "addressed to the public" is falsified by the
   restricted annex. My side is written to the refined wording; theirs is untouched.
3. Nine one-way edges need return legs; the two protected-on-both-sides pairs
   (`government.social-services-casework`, `medical.personal-health-records`) should be stated from the
   protected side first.

## Self-verification

`python3 -m json.tool` passes. Every quoted span was grep-verified verbatim against `00` before being
written (the residual-template definitions, the session clause, the extension-as-routing-signal clause, the
EXIF clause, the project-before-time clause, the reversible-dimensions clause, and the privacy-enforcement
clause). All twelve edge ids were confirmed present in `planning/domains/ROSTER.md`. Every
`falls_through_to` name is one of `00`'s residual homes; every `source_type` is in `SOURCE_TYPES`; no file
example writes a path as a fact; no threshold, score, or handling class appears. I wrote only
`government.emergency-management.json` and this memo — no neighbour node, roster, canonical-fields,
`check.py`, `src/`, or SPEC file was touched.

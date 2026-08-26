# Research memo — `government.environmental-regulation`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.environmental-regulation.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accept the node.** `refuse_node: false`. It survives the charge because its evidence is not a decision
record with environmental words in it — it is a perpetual measured-return stream keyed to a permit
condition and a sampling point, which nothing else on the government schema produces. Its detection
signals and its privacy rules both differ from the schema default. Its dimensions do not, and cannot,
because PR-6 leaves the schema fieldless; two of three legs is what the node test asks for, and this
memo argues each leg separately rather than asserting a verdict.

## The charge, stated at its strongest, before anything else

I had to argue this row out of a hole, because three of the standard refusal grounds land on it hard.

**Charge 1 — this row is a work_type value of its own schema.** The `government` anchor's `work_types`
already contains, verbatim, *"planning application, permit or licence case, inspection, enforcement
record, reasons, decision, variation, suspension, or revocation on the deciding side."* That sentence
is a complete description of environmental permitting. If the anchor already enumerates the work,
then "environmental" is an adjective applied to an existing value — a topic, not a filing world — and
the row is the 574's original mistake wearing a subject-matter label.

**Charge 2 — this row is a duplicate of `government.permit-licensing`.** That row exists on the roster.
It owns authority-side permits and licences generically. A liquor licence case and an environmental
permit case have the same furniture: an application, an assessment, a numbered condition schedule, a
determination, a variation, a revocation. Splitting one out by subject matter is exactly the
duplicate-of-a-neighbour failure.

**Charge 3 — this row is a duplicate of its schema's default template.** Both have
`dimension_order: []`, both are `potentially_sensitive`, both use the whole SOURCE_TYPES spread. If the
only difference is which nouns appear in the deterministic list, that is vocabulary, not a node.

A fourth and fifth reading are weaker but worth killing outright. This is not an **organisation name**
row — no environment agency name activates it, and the never-alone list says so first. It is not a row
defined by an **absence** — its positive evidence is a numeric structure, not the lack of one.

## Defeating the charge

**Against Charge 1 — the mass of the evidence is not where the work_type says it is.** Enumerate what a
regulator's environmental file physically contains and the decision documents are a small minority.
The bulk is: recurring monitoring returns filed by the regulated party on a schedule the permit itself
sets; accredited laboratory certificates with chain-of-custody; continuous instrument exports with
validity and calibration-drift flags; pollutant release and transfer inventory submissions; sampling
field sheets; incident notifications that arrive out of band. Those are not the outputs of a decision.
They are the outputs of a *condition*, and they keep arriving for as long as the installation operates.

The structural consequence is what makes it a node rather than a value: this world's central artifact
places a **measured result, its unit, and a permitted limit in adjacent labelled slots, repeated over
dated rows, under a permit reference and a sampling-point identifier**. Check that against the
anchor's ten deterministic signals — bill packet, rulemaking packet, decision record, procurement
record, governance cycle, statistics packet, election packet, case export, office mail and calendar.
Not one of them is result-against-limit shaped. The nearest, the official-statistics signal, is about
an authority *producing* data from a survey instrument it designed; here the authority *receives*
numbers it did not generate, from a party with an interest in them, against a threshold it imposed.
Different producer, different trust posture, different structure. That is a detection-signal
difference, and it is why Charge 1 fails.

**Against Charge 2 — permit-licensing terminates and this row does not.** The clean way to state the
seam: `government.permit-licensing` owns the lifecycle *up to and including* the determination, for any
licensable activity; this row owns what the granted conditions then *generate*. Licensing's group has a
terminal event. This row's group is open-ended and has no terminal event, which is recorded in
`grouping_reasons` as the distinguishing property, not as a slogan. The reciprocal fixture is named on
both sides in the JSON: `Permit EPR-AB1234 - Consolidated Variation V3 - Schedule 3 Emission Limits.pdf`
sits with permit-licensing when its neighbourhood is application, assessment and determination, and
sits here when its neighbourhood is returns and certificates keyed to its condition identifiers. Same
bytes, decided by what surrounds them. That is a real mutex and it is authored.

**Against Charge 3 — the privacy rule genuinely differs, and it differs in an unexpected direction.**
The schema anchor is protect-by-default because its worry is citizen casework, submissions and
unsuccessful bids. This row's worry is the opposite shape. Much of its corpus is destined for a
**statutory public register** — permits, condition schedules and many returns are published by design,
and pretending otherwise would be wrong about the world. But the same permit reference also gathers
complainant names and addresses, whistleblower reports, pre-enforcement investigation material,
prosecution referrals, and commercially confidential process detail excluded from the register. So the
rule this row needs is not "protect everything" and not "this is public" but a third thing:
**publication of one member never lowers the posture of the packet that shares its permit reference**,
and complainant identity in particular never reaches a branch label, a group summary, or a model
prompt. That last clause is why a complainant is excluded from the dimension prose even hypothetically.
The design's binding requirement is quoted in `sensitivity_why`: *"Privacy policy must be enforced
before content reaches any model or external connector."* A split posture is a different privacy rule
from a uniform one, so Charge 3 fails on leg three as well as leg one.

**Where the charge partly lands, honestly.** Leg two — recommended dimensions — I cannot claim. PR-6
leaves the schema fieldless, so `dimension_order` is `[]` here exactly as it is on the anchor and on
`legal.practice-matter-file`. I record the structure as prose and refuse to serialize it. If a future
reader thinks two legs out of three is insufficient, the row should be re-tested after PR-6 is
adjudicated, not padded now.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` — the standing brief, in full.
- The stamped assignment from `make_prompt.py government.environmental-regulation`.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — depth calibration.
- `planning/domains/nodes/government.json` — my schema anchor: its `recognition`, `work_types`,
  `grouping_reasons`, `template`, `file_kinds`, `collides_with`, `falls_through_to`, `sensitivity_why`
  and key set. This is the default template I am measured against.
- `planning/00-database-agent-product-design.md` — reached by targeted grep only. Every span I put in
  quote marks was matched verbatim before use: the extension-routing sentence and the session sentence
  (line 35 / line 45 region), the EXIF sentence (line 32), the two dimension-order sentences (line 95),
  and the residual-library definitions for Independent Records, Protected Records, Reading Inbox,
  Review Later, Unsupported or Encrypted and Temporary Screenshots (line 120). No quotation in either
  output file is paraphrased.
- `planning/domains/roster.json` — id existence check for every edge target.
- `planning/domains/nodes/business_operations.compliance-audit.research.md` — the one landed row that
  had already argued a boundary against me.

## Files considered and rejected

A row that only lists what it holds has not been researched. These are the tempting false positives,
each with the discriminator.

- **An ISO 14001 internal audit report for the same site.** The strongest false friend and the reason
  it is a collision fixture in the JSON. It has environmental vocabulary, the same operator, the same
  site, numeric objectives, and nonconformities. It is not mine because its findings index to
  **management-system clause numbers, not permit condition identifiers**, and its prepared-for is the
  operator's own management review. Conformity to a voluntary standard is not a statutory
  authorisation, whoever holds it. Encoded as a `never_alone` clause.
- **A published open-data water quality dataset.** The second collision fixture, and the harder one,
  because its columns are *exactly* my strongest signal: determinand, result, unit, sampling point,
  dated rows. What discriminates it is what is missing and what is added — no permit reference, no
  operator, **no limit column**, no return-register slot, plus a licence-and-attribution header and row
  coverage spanning many unrelated points. The result-against-limit pairing, not the result column, is
  the signal. A regulator's name in the attribution header is explicitly not custody.
- **An Environmental Statement chapter from an EIA.** Modelling, receptors, thresholds, monitoring
  proposals, regulator-facing language — but every page carries a **planning application number, not a
  permit reference**, and the mitigation is prospective rather than assessed against an existing
  numbered condition. Goes to `government.planning-application`.
- **A corporate sustainability, ESG, or carbon-disclosure report.** Numeric environmental returns
  addressed to a regulator or an investor. Counterparty value does not activate this schema — the
  anchor's never-alone list already says so for government generally and I restate it for this row.
- **An environmental campaign objection or a charity's consultation response**, even one quoting permit
  conditions verbatim. That is `nonprofit.advocacy-campaign` or `government.public-consultation`
  depending on custody.
- **A waste transfer note, exemption certificate, or abatement notice held by the operator or by a
  householder.** Authority-issued and held by the recipient — the anchor's rule, applied.
- **A drinking-water or bathing-water result downloaded to read.** Reading Inbox.
- **A live monitoring database or telemetry system.** A source system, not a file node. A bounded
  export with a readable manifest is represented; ingestion is a later connector decision.
- **Site photographs.** A camera image of an outfall carries no permit fact. It joins a sampling event
  only through an exact sample or point identifier, and never through the absence of EXIF.
- **A contaminated-land Phase 1/Phase 2 investigation prepared for a developer.** Same analytes, same
  chain-of-custody, same laboratory. Prepared-for is a purchaser or developer and the frame is
  transactional; it belongs with the property survey world, not with a regulator's site file.

## Reciprocal boundaries

Four mutexes are authored, each stated in both directions with the same fixture named on both sides.

1. **`government.permit-licensing`** — argued above. Fixture: the consolidated permit PDF. Licensing
   holds it when surrounded by application and determination; this row holds it when surrounded by
   returns keyed to its conditions.
2. **`manufacturing.environmental-compliance`** — the true reciprocal, and the most important edge on
   this row. The operator's compliance folder and the regulator's site file contain *identical bytes*:
   the same permit copy, the same quarterly return, the same laboratory certificate. Fixture:
   `EPR-AB1234 - Quarterly Monitoring Return Q2 2026 - Outfall 001.xlsx`. Mine requires a
   **date-received / receiving-officer slot**, an officer assessment, an issued instrument, or an
   authority case-system export. Theirs owns the same spreadsheet when the evidence shows the operator
   preparing or submitting it. **When neither marker is present the file goes to Review Later, not to a
   guess** — this is the single most common real-world case and I would rather abstain than steal it.
3. **`government.planning-application`** — fixture: the Environmental Statement chapter. Planning
   reference and prospective mitigation → planning; permit reference and assessment against an existing
   condition → here.
4. **`government.public-health-administration`** — one municipal office frequently runs both. Fixture:
   the odour complaint. Traced to a permitted installation's abatement conditions → here; pursued as a
   health-protection investigation of exposed persons → public health.

## The collision fixture

Requirement 5 asks for at least one file that looks like my evidence and is not. I supply two, because
they fail for opposite reasons and a single one would leave a hole.

`ISO 14001 Internal Audit Report 2026 - Riverside Works.docx` fails on **custody and referent** — right
site, right vocabulary, wrong clause namespace and wrong producer.

`River Ash water quality dataset 2020-2026 - open data download.csv` fails on **structure** — it is the
only file in this memo whose columns match my headline signal almost exactly, and it is still not mine,
because it has no limit to measure against and no register of receipt. If a future implementer
remembers one thing from this row, it should be that *determinand plus unit is not the signal; the
result-against-permitted-limit pairing under a permit reference is*.

## Neighbours considered that did not get an edge

- **`business_operations.compliance-audit`** — this row's only landed neighbour, and it deliberately
  declined an edge to me, reasoning that "the which-side-is-the-holder discriminator is already carried
  by `corporate-regulatory-filings` and by the schema row's `government` collision. Tripling it adds
  nothing." I agree and reciprocate the non-edge rather than authoring a one-sided mutex against a row
  that has already reasoned it through. The ISO 14001 fixture is where we would compete; the
  `manufacturing.environmental-compliance` edge already carries that discriminator on my side.
- **`government.professional-regulator`** — regulates *persons and professions*; this row regulates
  *sites, installations and discharges*. A fitness-to-practise file and a permit condition file share
  no fixture. No edge.
- **`government.emergency-management`** — pollution incident response touches it, but a major-incident
  command record is organized around an emergency activation, not around a permit reference. Left as a
  non-edge; R1c may revisit if their fixtures collide.
- **`government.parks-public-lands`** — land the authority *manages*, not activity it *regulates*.
- **`resource_operations.mining-operations`** and **`retail_hospitality.food-safety`** — both are
  regulated-party or different-statute worlds. `manufacturing.environmental-compliance` already carries
  the operator-side seam generically and I do not want three parallel copies of one boundary.
- **`construction_property.site-survey`** — the contaminated-land investigation is a real near-miss,
  recorded above as a rejected file rather than as an edge, because the competing custody is a
  developer's, not a neighbour regulator's.
- **`research.ethics-compliance`** — different compliance world entirely.

## also_holds_with, role_split, fields

All three are empty, and each for a stated reason rather than by omission.

`also_holds_with` is empty because a template cannot author schema-level coactivation and the
`government` schema exposes no field to carry a second role. Genuine dual-schema cases are recorded
per fixture instead, on `also_schema` — the portal screenshot is the live one, which is independently
Photos evidence while OCR may or may not recover a permit token. This mirrors the landed
`legal.practice-matter-file` treatment.

`role_split` is empty for the same structural reason: it requires different **field keys** on the two
sides, and this schema declares none. The operator/regulator split, which is exactly what `role_split`
was designed for, is therefore carried as a `collides_with` against
`manufacturing.environmental-compliance` and flagged in NEEDS-JOSEPH as the thing to reconsider if
PR-6 is lifted.

`fields: []` and `proposed_fields: []` are deliberate. Candidate concepts were considered and are
recorded here for R1c rather than minted: an authorisation or permit reference; a regulated site or
installation; a sampling point, outfall, or stack; a reporting period; an environmental medium
(air / water / land / waste); a determinand. None of these is a canonical key today, PR-6 forbids
government field rows, and minting a variant of an existing key would be worse than proposing nothing.
`institution`, `record_type`, `project` and `purpose` were checked and rejected as scoped elsewhere.

## Recommendations to R1c (I did not edit any neighbour)

1. Author the reciprocal side of the `manufacturing.environmental-compliance` mutex, naming the same
   quarterly-return fixture, so the operator-side row abstains symmetrically.
2. Consider whether `government.permit-licensing` should carry the terminates-at-determination seam
   explicitly, since it is the property that keeps the two rows apart.
3. If `government.emergency-management` lands with pollution-incident fixtures, adjudicate the incident
   seam then rather than pre-emptively now.

## NEEDS-JOSEPH

- **NJ-1 — PR-6 and this row's structure.** This row can describe a site-and-permit organizing
  structure but cannot serialize one. If PR-6 is lifted, adjudicate centrally — not in children —
  whether a bounded authorisation reference, a regulated site or installation, a reporting period, and
  an environmental medium may exist as government fields, and which if any are destination-eligible.
  Alternatives: (a) stay fieldless and accept that this row's recommendation is prose; (b) mint a
  role-safe minimum of site + authorisation reference only; (c) mint the full set including medium and
  determinand, which risks recreating an industry taxonomy J-IND deferred.
- **NJ-2 — the public-register question, as policy.** Alternatives: (a) packet posture always dominates
  and a published permit inherits the protection of the complaint that shares its reference — the
  conservative choice this row currently assumes; (b) a member provably on a statutory public register
  may be treated separately from its packet, which is more truthful about the world but requires the
  product to decide register membership, which it cannot reliably do; (c) let the user declare it per
  corpus. This is not settleable from the design docs.
- **NJ-3 — operator side versus regulator side.** A large share of real corpora will contain returns
  and certificates with no custody marker at all. Alternatives: (a) evidence only, which routes heavily
  to Review Later — the current behaviour; (b) a user-declared corpus role ("I am the regulator" / "I am
  the operator") that biases the seam; (c) a P9 group-level inference from the surrounding packet, which
  risks copying a custody fact onto sparse members. Option (b) is outside this row's authority to add.

## Self-verification

- `python3 -m json.tool` parses the node file.
- Key set matches `government.json` exactly, including `proposed_context_terms`.
- Every `file_examples.source_type` is in `SOURCE_TYPES`; `code_structured` is used for the XML
  inventory submission and is present in `file_kinds.source_types`.
- Every quotation was grep-matched verbatim in `00` before being written. No fabricated span.
- No threshold numbers, no confidence scores, no handling classes, no `public_low`.
- Every edge target exists on the roster: `government.permit-licensing`,
  `government.planning-application`, `manufacturing.environmental-compliance`,
  `government.public-health-administration`. Every `falls_through_to` name is one of `00`'s nine
  residual homes.
- `fields`, `proposed_fields`, `dimension_order`, `also_holds_with` and `role_split` are empty by
  argument, not by omission. `time_first: false`.
- Only the two assigned files were written. No neighbour, roster, canonical-field, `check.py`, `src/`
  or SPEC file was touched.

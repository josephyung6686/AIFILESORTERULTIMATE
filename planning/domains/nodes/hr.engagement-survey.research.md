# Research memo — `hr.engagement-survey`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/hr.engagement-survey.json`
Roster row: template on the fieldless `hr` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accept**, narrowly, and for one reason that is worth stating before anything else: this template exists
to catch files the `hr` schema default would **miss**, not files it would already catch. The `hr` anchor's
dominant deterministic signal is "a structured personnel form whose labelled slots jointly identify an
employee or workforce cohort AND a personnel process". An engagement response export deliberately
identifies **no employee**. It would fail the schema's own primary test. A template whose job is to
correct an under-detection in its parent schema is the clearest possible case for a template existing.

## Sources read

`planning/domains/dispatch/RESEARCH-BRIEF.md`; the stamped assignment from `make_prompt.py`;
`planning/domains/nodes/hr.json` (the schema anchor, in full — it is the default template I am measured
against); `planning/domains/nodes/legal.practice-matter-file.research.md` as the depth calibration;
`planning/domains/roster.json` for every edge id used; `planning/00-database-agent-product-design.md` by
targeted grep only, for the purpose facet and the five residual definitions. Every span in quote marks in
the JSON and in this memo was grep-verified verbatim against `00` before it was written; the five residual
sentences and the purpose passage each returned exactly one match.

I also read `business_operations.user-research.json`'s refusal, because that row named
`hr.engagement-survey` as required reading and its refusal is the strongest precedent against me.

## THE CHARGE — the strongest case that this row should not exist

I owe this in full, because four separate refusal theories fit this row and one of them nearly won.

**1. It is a work_type value.** This is the strongest charge. `hr.json`'s `work_types[]` contains, verbatim,
`"employee engagement instrument, response dataset, report, or action plan"`. My row is that string. The
project's stated failure mode is minting a node for a value of a field. If the schema already enumerates
this as one of eleven work types, promoting it to a row looks exactly like the 574's mistake.

**2. It is a duplicate of the schema default.** `hr.json` already carries a deterministic bullet for
"an engagement, DEI, or workforce-analytics export", already carries the fixture
`Employee engagement survey raw responses.csv` with the correct `must_not_conclude` about aggregation,
and already carries `NJ-HR-4` asking whether aggregated engagement data stays protected without a
de-identification rule. The anchor appears to have done my job.

**3. `business_operations.user-research` refused on exactly these facts.** Its refuse_reason says
"guides, consent forms, transcripts, survey exports and findings decks identify methods or artifact
shapes, not product user research" and that once you "delete those labels and document-type words … no
unique structure remains." An engagement wave is guides, consent language, exports, and findings decks.
The deletion test that killed that row is pointed straight at mine.

**4. It is defined by an absence.** My sharpest distinguishing feature — no employee identifier — is the
absence of something. `00` explicitly refuses absence-as-proof ("missing EXIF as screenshot proof" is
the anchor's paraphrase of that rule). A row whose identity rests on a missing column cannot activate.

**5. Lesser charges, dismissed quickly.** It is not a lifecycle stage (a wave is a whole artefact family,
not a phase of workforce-analytics). It is not a medium, length, format, or organisation name. It is not
an organisation-name row: nothing here activates on the employer's identity, and the JSON says so in
`never_alone`.

### Defeating the charge

**Against (4), the absence charge — this is the one I had to fix, not argue away.** I accept it. The
absence of an identifier column is now written into `never_alone` as a thing that is *forbidden* to
activate: "the ABSENCE of an employee identifier column as proof that a spreadsheet is an anonymous
survey export. This mirrors the design's refusal to treat missing EXIF as proof of a screenshot." The
activating evidence is entirely positive: a repeated ordinal scale over first-person statements; two or
more **employment-attribute** cut columns; a free-text comment column; a suppression statement. The
missing identifier is corroborating and never activating. Charge answered by constraint, not by argument.

**Against (1), the work_type charge — the deletion test.** Delete every label: "engagement", "survey",
"pulse", "listening", "eNPS", "feedback". What survives? A dataset whose rows are drawn from the
employer's own workforce, whose columns are a repeated ordinal instrument plus employment-attribute cuts
plus open text, which carries no subject identifier, and which arrives with a companion report that
suppresses cells below a reporting minimum. That is a structure, and it survives the deletion of every
document-type word. This is precisely where I diverge from `business_operations.user-research`: there,
deleting "user", "participant" and "study" left only generic interview and deck shapes that occur in
academic, workforce, market, sales and support contexts. Here, deleting the labels leaves a column
grammar — employment cuts — that occurs nowhere else. A work_type value cannot survive its own deletion.
This structure does.

**Against (2), the duplicate charge — the three legs, argued separately below.** The short form: the
anchor's single engagement bullet is shared across engagement, DEI and workforce-analytics and therefore
discriminates none of the three from each other; it describes only the export, not the instrument, the
fielding record, the report, or the action plan; and it inherits the schema's identity-based privacy
rationale, which is the wrong rationale for this material.

**Against (3), the user-research precedent.** That refusal is correct and I am not contradicting it. The
distinction is the respondent population. `user-research` could not name who its respondents were in a
way that showed up in bytes — a customer, a user, a participant, and an employee all look the same in a
response export unless the cut columns say otherwise. My row's whole content is that the cut columns say
otherwise. Read reciprocally, the two rows agree: user-research refused because survey shape is not a
world; this row is accepted because *workforce* respondent structure is.

## The node test, all three legs

CONNECTION.md §2 requires a template to differ from its schema's default in detection signals, recommended
dimensions, **or** privacy rules. Two legs carry independently; the third carries as an argued inversion.

**Leg 1 — Detection signals: differs, decisively.** The `hr` default keys on the joint presence of employee
identity and a personnel process. Every core engagement artefact lacks the first half. This row supplies
signals the default cannot express: an instrument whose structure is *a repeated scale with no subject
slot*; an export whose *cut columns are employment attributes*; a report carrying a *minimum-reporting-group
suppression statement* — which no customer, market, or product report has any reason to contain, making it
the single most discriminating artefact in the family; a participation tracker whose *rows are populations,
not people*; and an action plan whose *parent is a wave*, not a review period or a case. The default would
route most of these to Protected Records unrecognised. That is a real, non-cosmetic difference.

**Leg 2 — Recommended dimensions: differs as prose, is identical as serialization. I state this honestly.**
Both `dimension_order` arrays are empty and must be, because PR-6 leaves `hr` fieldless. This leg does not
carry the row on its own. But the *recommendation* inverts the anchor's stated rule. `hr.json` says the
people cycle "should follow a programme or workforce unit rather than lead merely because it contains a
year." For engagement listening the wave must **lead**: a unit's favourability page is unreadable without
knowing which wave produced it, wave-over-wave comparison is the entire purpose of the family, and the same
unit recurs in every wave, so unit-first scatters each wave across the tree. Recommended order for R1c:
`people_cycle` (the wave) → work type → `workforce_unit` only where a genuine multi-unit corpus exists.
Never a respondent level — there are no respondents to name. `time_first: false`: a wave is a named process
instance, not a date, and two waves can close in one quarter.

**Leg 3 — Privacy rules: differs in mechanism, which changes the operative rules.** The `hr` default protects
because identity is joined to pay, performance, allegations or health. Strip the identity and that rationale
evaporates — yet this material stays sensitive, for three reasons the default does not state: an anonymity
undertaking is recorded *inside the instrument itself*, so exposing the bytes breaks a promise the file
documents; intersecting small cuts with free text re-identifies a respondent, so aggregation is not a safety
proof; and the comment column can contain individual grievance, health or safety content that attracts the
employee-relations posture on its own. Those produce four operative rules the default does not have: never
join a response row to a roster or payroll file to recover identity; never treat de-identification or a
suppression note as making the file safe; never reconstruct a suppressed cell from the export; prefer local
header-and-manifest recognition over sending comment text remotely. `NJ-HR-4` asked whether aggregate
listening stays protected; this row answers *why*, and the why generates rules. No threshold is stated.

## Files considered and rejected

The tempting false positives, and why each is not my evidence:

- `Q3 NPS - responses.csv` — **the collision fixture**; treated in full below.
- `360 feedback report - J Patel - FY26.pdf` — a Likert instrument fielded on the workforce with rater
  confidentiality, and still not mine: one named subject, feeding a rating outcome. → `hr.performance-cycle`.
- `Utrecht Work Engagement Scale - validation study.pdf` — reproduces the item bank verbatim, with the
  identical first-person statements. Item wording is shared across the entire field and is never ownership
  evidence; the sample is another organisation's employees. → Reading Inbox.
- `Culture Amp - Master Services Agreement.pdf` and `Survey platform invoice Q1.pdf` — the vendor's name is
  the most survey-sounding token in the corpus and neither file contains a wave.
  → `business_operations.vendor-management` / `finance`.
- `All-hands deck May 2026.pptx` with one engagement results slide — a citation of the wave, not the wave.
  → `business_operations.meeting-record`.
- `Glassdoor reviews export.csv` — anonymous, free-text, about this employer, from employees. Rejected: the
  organisation did not field it and gave no undertaking; there is no instrument, no population definition,
  and no cut columns. This one is genuinely close and I flag it as the weakest rejection in the set.
- `Attrition and headcount dashboard.xlsx` with an engagement index tile — HRIS-derived, identified
  population. → `hr.workforce-analytics`.
- `Course evaluation - Manager Essentials cohort 3.xlsx` — survey-shaped, workforce respondents, but bound
  to one session and one cohort roster. → `hr.training-development`, with co-activation where it is fielded
  as part of a listening programme.
- `Diversity self-identification campaign return.csv` — questionnaire-collected, workforce respondents,
  and still primarily a monitoring return. → `hr.dei-program`, co-activating where one wave serves both.
- `Employee Handbook v4.2.pdf` — the anchor already routes governing policy to `business_operations`;
  named here only to confirm this row does not reach for policy.

## The collision fixture

`Q3 NPS - responses.csv`. A 0-to-10 recommendation column, a "why did you give this score" free-text
column, no identifier, cut columns for region, plan tier, account size band, and **months since signup** —
a tenure-shaped column that reads as workforce tenure at a glance. Byte-for-byte this is the closest thing
in any corpus to `engagement_2026_wave1_responses_deidentified.csv`.

What discriminates it: the cut columns are **commercial account attributes**, not employment attributes.
There is no grade, no manager level, no business unit, no employment type, no joiner cohort. And there is
no suppression note, because a customer report has no anonymity undertaking to honour. The discriminator is
the column grammar, never the word "survey", never the Likert shape, never the comment column — all three
of which are present on both sides and are written into `never_alone` for exactly that reason.

## Reciprocal boundaries

Five, each naming the same fixture on both sides; the JSON carries them in full. In summary:

- **`business_operations.market-research`** — fixtures `Q3 NPS - responses.csv` / `engagement_2026_wave1_
  responses_deidentified.csv`. Market-research must not take an export with employment cut columns or a
  suppression note; this row must not take a customer or event survey because it is anonymous and Likert-shaped.
- **`hr.performance-cycle`** — fixture `360 feedback report - J Patel - FY26.pdf`. Performance-cycle must not
  take an aggregate wave export because engagement items mention managers; this row must not take any
  instrument attributable to one named subject, however anonymous its raters.
- **`hr.workforce-analytics`** — fixture `2026 Engagement Results - Group Report.pdf`. Analytics must not take
  the instrument, export, tracker or wave report; this row must not take HRIS-derived headcount, attrition or
  absence because an engagement figure sits beside it. Provenance decides: volunteered under an undertaking
  versus already held about identified people.
- **`hr.dei-program`** — fixture the inclusion item block and its demographic cut. Neither takes the whole of
  the other; a wave serving both co-activates.
- **`business_operations.meeting-record`** — fixture the all-hands deck with one results slide.

Neighbours considered that got **no** edge: `career.employment-records` (an individual's copy of a survey
invite carries nothing; the anchor already draws the employer-side/individual seam and duplicating it here
would add noise); `hr.employee-relations` (comment content can attract its handling posture, but a comment
is not case membership — this is a handling interaction, not an edge); `hr.compensation-planning` (pay
satisfaction items do not make a wave a pay review); `business_operations.strategy-plan` (engagement targets
in a strategy document are a citation); `research` (appears only as an `also_schema` on the validation-study
fixture, not as a row-level edge).

## Fields and dimensions

`fields: []` and `proposed_fields: []`, both deliberate. `hr` declares no canonical field rows under PR-6, so
a template on it can serialize none. I considered and rejected minting `survey_wave`: `hr.json` already
proposes `people_cycle` for "the named or bounded HR process instance that joins otherwise heterogeneous
members", with `"FY2026 annual review, 2026 graduate intake, or March 2026 payroll run"` as its example. A
wave is that, exactly. The brief says reuse an existing proposal rather than mint a variant, and minting
`survey_wave` would be a synonym of the kind D6 warns about. Likewise the cut is `workforce_unit`, not a new
`population_cut`. The anonymity property and the reporting minimum are **privacy rules**, not fields, and
recording a minimum as a value would be a threshold this contract forbids — hence NJ-ENG-3.

## Recommendations to R1c (I edited no neighbour file)

1. Add the reciprocal half of the `business_operations.market-research` boundary to that row when it lands,
   naming `Q3 NPS - responses.csv` on both sides.
2. Add the reciprocal half of the `hr.performance-cycle` boundary naming the 360 fixture.
3. `hr.workforce-analytics` and `hr.dei-program` should carry the mirrored text already drafted in this row's
   `collides_with`; I did not write into their files.
4. Consider whether `hr.json`'s single "engagement, DEI, or workforce-analytics export" bullet should be
   narrowed now that three templates split it, since as written it discriminates none of the three.

## NEEDS-JOSEPH

- **NJ-ENG-1** — This row is downstream of NJ-HR-1 and does not assume its own survival. If `hr` is refused,
  either (a) the listening family goes to `business_operations` as a programme with the exports in Protected
  Records, or (b) listening is promoted to a standalone row on another schema. I recommend (a).
- **NJ-ENG-2** — The exit-survey seam. Exit responses are frequently attributable to one leaver, which
  destroys the anonymity property that justifies this row. Either attributable exit responses are
  `hr.onboarding-offboarding` members with only the aggregated exit dataset here, or the whole exit
  instrument sits here under a mixed privacy rule. I recommend the former.
- **NJ-ENG-3** — May the minimum-reporting-group statement be recorded at all? It is the single most
  discriminating artefact of employee listening, and recording its *value* would be storing a threshold.
  Alternatives: record presence only, or record nothing and lose the strongest signal. This row records
  presence only.
- **NJ-ENG-4** — May verbatim comment text ever enter a remote prompt for classification? This row says no by
  default and accepts the resulting under-detection of comment-only extracts, which fall to Protected Records.

## Self-verification

`python3 -m json.tool` parses the node. Key set matches the landed `hr` anchor and the launch-row idiom.
Every edge id (`hr.performance-cycle`, `hr.workforce-analytics`, `hr.dei-program`, `hr.onboarding-offboarding`,
`hr.training-development`, `business_operations.market-research`, `business_operations.meeting-record`,
`business_operations.vendor-management`) was confirmed present in `roster.json`. Every `falls_through_to`
template is one of `00`'s nine residual homes. Every `file_examples.source_type` is in `SOURCE_TYPES`. No
file example writes a folder path as a fact. Every quoted span greps back verbatim. No threshold number, no
confidence score, no handling class. I wrote only my two assigned files.

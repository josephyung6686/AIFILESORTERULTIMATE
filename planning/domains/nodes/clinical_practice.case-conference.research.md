# clinical_practice.case-conference — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `clinical_practice.research.md`; all quotations machine-verified verbatim
against `00-database-agent-product-design.md`. Landed siblings read for key set and idiom:
`medical.personal-health-records.json`, `medical.json`, `legal.practice-matter-file.json`.
Legacy row absorbed per `ROSTER.md` Appendix A line 592: `med.clinician-case-conference` (ROW).

## What it is for, and what it holds

Material prepared for, presented at, or produced by a recurring meeting where **several named cases**
are discussed across services: tumour boards and MDTs, morbidity-and-mortality and significant-event
reviews, safeguarding conferences, documented ward rounds. It holds agendas and case lists, per-case
presentation decks with imaging, supporting exports, outcomes-and-actions records, attendance and
quorum records, invitations, recordings, and terms of reference.

## Node test — passes, on the anchor

The organizing anchor is the **meeting**, not any one patient. That is a genuinely different
organizational situation from a chart, and it is how clinicians actually file this material. Detection
signals differ (agenda + attendance + a multi-subject case list; an outcomes-and-actions table).
Privacy rules differ in an interesting direction: a meeting-named branch discloses a service and a
cadence rather than a person, so this is the **least** exposing anchor on the family — which is why
its `open_question` asks whether it could carry a shallow non-redacted level as a deliberate
exception. Dimensions do not differ, and cannot, for the family-wide reason recorded above.

## Files considered and rejected

- **`Journal club - May.pptx`** — kept as the collision fixture. Same agenda/attendance shape, no
  cases; this is the tempting false file.
- **`Team meeting minutes`** — kept as a second fixture against
  `clinical_practice.practice-administration`; the discriminator is simply whether named cases are
  discussed.
- **A trial management meeting / data monitoring committee pack** — considered and left as a
  `collides_with` signal against `research` rather than a file example; at gist depth one fixture per
  confusion is enough.
- **A safeguarding strategy meeting record** — real and in scope, but it is the same shape as the MDT
  agenda with a different service, so it earns a `work_type` value, not a file example.

## proposed_fields

**None** — deferred to the schema row's single `subject_of_record` proposal.

## Neighbours considered that did NOT get an edge

- **`academic`** — a grand round is teaching and academic at once, but the three-cornered confusion is
  already stated at schema level and against `clinical_practice.teaching-material` here. Not tripled.
- **`hr`** — case conferences about *staff* (performance, occupational health) share the shape
  exactly. Left unedged at gist depth rather than guessed; flagged below.

## NEEDS-JOSEPH

- **NJ-CP-4 · Is a MEETING an acceptable branch anchor in v1 when a patient is not?** A meeting name
  discloses a service and a cadence, not a person, and meeting-first is how this material is really
  filed. If yes, this row is the only one on the family that could carry a shallow non-redacted level,
  and that should be a stated exception rather than an accidental drift.
- **NJ-CP-5 · Staff-subject conferences.** A conference about an employee rather than a patient looks
  identical and arguably belongs to `hr`. No edge was authored; R1c should decide whether the pair is
  real.
- Carries **NJ-CP-1** (the clinician-authored versus patient-held boundary) by inheritance from the
  schema row; not restated as an edge here because this row's confusions are internal to the family.

# clinical_practice.patient-chart — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `clinical_practice.research.md` (that memo lists it and the verbatim-quote
verification method; every quotation here and in the JSON was machine-checked against
`00-database-agent-product-design.md`). Landed siblings read for key set and idiom:
`medical.personal-health-records.json` (the direct counterpart), `medical.json`,
`legal.practice-matter-file.json`. Absorbed legacy rows per `ROSTER.md` Appendix A lines 589–591:
`med.clinician-patient-chart` (ROW), `med.clinician-clinical-note` (FOLD),
`med.clinician-treatment-plan` (FOLD).

## What it is for, and what it holds

The longitudinal record a practice keeps **about one other person**: dated entries, consultation and
admission records, treatment and care plans, results filed against orders the holder placed, consent
forms the holder took, letters filed inward, discharge summaries, and the export or subject-access
packet the whole thing becomes when it is requested. Notes and plans are the chart's own contents,
which is why the two legacy rows fold in rather than standing beside it — a note is a `work_type`
value, not a world.

## Node test — passes

Detection signals differ from the schema's default: this row is evidenced by **longitudinal
accumulation about a single named subject** plus a two-role author/subject structure, which no other
row on the family requires. Privacy rules differ: it is the densest third-party aggregation on the
roster and it is the row whose natural dimension (the patient) is the one dimension that must never
become a folder label. Dimensions do **not** differ and could not — `clinical_practice` declares no
fields, so every template on it has an empty `dimension_order` by contract, and the node test's third
leg is unsatisfiable for every row in this family. Recorded here rather than papered over.

## Files considered and rejected

- **`SOAP template blank.docx`** — kept, but as the collision fixture, not as evidence. Documentation
  headings alone are the tempting false file for this row and appear in blank forms, teaching
  handouts, exam scripts, and software docs.
- **`After Visit Summary.pdf`** — kept as the *reciprocal* fixture. It is `medical.json`'s own file
  example, deliberately reused so both sides of the boundary point at the same bytes.
- **`case 4 - 68yo with chest pain.docx`** — rejected as this row's evidence; belongs to the sibling
  `clinical_practice.teaching-material`.
- **A DICOM study** — rejected: already carried honestly on `medical.json`, and imaging belongs to a
  chart only by filing, not by structure.

## proposed_fields

**None.** The one field this world needs (`subject_of_record`) is proposed once, on the schema row,
for R1c. Proposing it again here would be this row answering a decision that is not its own.

## Neighbours considered that did NOT get an edge

- **`legal`** — appears as `also_schema` on the subject-access-request archive (a records request is a
  legal instrument) but gets no edge row: `also_holds_with` joins **schemas only** (CONNECTION §5) and
  this is a template, so the pair is carried on `clinical_practice.json` where it belongs.
- **`academic`** — a student's clinical logbook is chart-adjacent, but the discriminating evidence is
  academic context, and the collision is already stated at schema level. Not duplicated.
- **`identity`** — a chart contains identity data but is not an identity document; the confusion lives
  on `licensure-credentialing`, where the card-shaped files actually are.

## NEEDS-JOSEPH

- **NJ-CP-1 · The clinician-authored versus patient-held boundary, stated reciprocally.**
  This row's `collides_with` names `medical.personal-health-records` and gives the discriminator: the
  holder's **role** (author sign-off / responsible-clinician / printed-by, beside a differently named
  subject) versus the holder in the patient slot. The landed `medical.personal-health-records.json`
  **does not name `clinical_practice`** — I verified this by grep and I did not edit that file, since
  it is outside my twelve. **R1c owes the reciprocal edge on the medical side**, and until it lands
  the boundary is asserted from one side only. The same NJ applies to
  `clinical_practice.referral-correspondence`, which carries the same pair.
- **NJ-CP-3 · May a chart be offered a physical destination at all in v1?** Any branch that groups
  chart material is a branch whose existence discloses a caseload; any branch that does not group it
  is not a chart. Represent-in-place under Protected Records is a defensible permanent answer here,
  and unlike the other placeholder rows this question does **not** depend on whether the schema ever
  gets field rows. Joseph's call.

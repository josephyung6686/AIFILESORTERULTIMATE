# clinical_practice.teaching-material — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `clinical_practice.research.md`; all quotations machine-verified verbatim
against `00-database-agent-product-design.md` after whitespace and curly-quote normalisation, and
every edge id checked against `roster.json`. Landed siblings read for key set and idiom: the
`clinical_practice` schema row and all five landed templates, with `.patient-chart` and
`.case-conference` read closely because both already state a `collides_with` **against this id** —
their discriminators are reproduced here rather than reinvented. Legacy row absorbed per `ROSTER.md`
Appendix A line 598: `med.medical-teaching-material` (ROW).

## What it is for, and what it holds

A clinician **teaching**. Lecture and grand-rounds decks, case presentations built for an audience,
journal club, M&M teaching records, bedside and small-group plans, simulation scenarios with faculty
scripts and debrief guides, handouts and summary cards, assessment item banks and examination papers
with answer keys, station briefs and marking schemes, attendance sheets and certificates, feedback
returns, lecture-capture recordings, and teaching-portfolio evidence. The organizing anchor is the
**session and its audience** — a date, a room, a title, and learners.

## Node test — passes; the strong leg is privacy, not detection

Detection differs: the **learning-objectives-plus-intended-audience pair**, and the de-identified case
shape (age-and-sex descriptor or initials standing where a name and record number would be, with
discussion questions interleaved). Neither a chart nor a guideline carries either.

The stronger leg is privacy, and it is the reason this row is worth having rather than folding into
`case-conference`. Teaching material is **patient-derived material whose anonymisation is asserted,
not verified**. The predictable failure is a name that survived the edit — burnt into an exported
image, left in a speaker note, in a file property, in a chart entry pasted whole and only topped and
tailed. So this row's `never_alone` says the thing that matters: *an age-and-sex descriptor read as
proof of anonymisation is the row's most characteristic signal and its most dangerous one.* The
`IM-0001-0007.jpg` fixture exists solely to carry that: burnt-in identifiers in pixel data survive
every de-identification the surrounding prose received.

A separate, real, secondary case: attendance sheets, feedback returns, and portfolio material identify
**staff**, not patients.

Dimensions do **not** differ and could not — `clinical_practice` declares no fields, so every template
on it has an empty `dimension_order` by contract, and **the node test's third leg is unsatisfiable for
every row in this family** (recorded identically in `clinical_practice.patient-chart.research.md`).
Recorded rather than papered over.

## Files considered and rejected

- **`case 4 - 68yo with chest pain.docx`** — taken deliberately from
  `clinical_practice.patient-chart.research.md`, which names it as belonging *here*. Reusing the same
  file on both sides means the boundary points at the same bytes from both directions.
- **`Sepsis pathway v4.2 - ratified 2026-01.pdf`** — reused verbatim from the sibling
  `protocol-guideline` row, as this row's collision fixture. Same file, opposite verdict, stated on
  both sides.
- **`IM-0001-0007.jpg`** — kept as the row's danger fixture, not as evidence.
- **`MRCP practice questions with answers.docx`** — kept for the learner-versus-teacher inversion, and
  kept honestly: the file itself frequently says *neither*, and the JSON says so rather than pretending
  a discriminator exists.
- **`Teaching portfolio 2026.zip`** — kept, and resolved via 00's shared-material policy rather than by
  forcing an owner against `licensure-credentialing`.
- **A conference abstract** — rejected as an example; folded into the `research.conference-presentation`
  collision instead, because a fixture would have duplicated the deck.
- **A student's submitted assignment** — rejected: it is academic-side material and not this row's, and
  keeping it would have implied this row claims learner output.

## proposed_fields

**None** — deferred to the schema row's single `subject_of_record` proposal, reused rather than varied.
Two keys were tempting and I minted neither. `audience` is genuinely this row's discriminating
property, and inventing a canonical key from inside a placeholder template is precisely what the
contract most forbids; `session` would have collided conceptually with the existing `event` key and
would have been a D6 synonym. Both are recorded as prose in `template.why`.

## Neighbours considered that did NOT get an edge

- **`hr.training-development`** — mandatory staff training records overlap with taught sessions, and
  attendance sheets are the shared artifact. Left unasserted at gist depth: the `hr` node file has not
  landed, and the `practice-administration` row already carries the whole clinical-versus-hr argument
  for this family. A second assertion of the same shape would be padding.
- **`business_operations.meeting-record`** — a taught session leaves an attendance sheet and an agenda,
  but the meeting-record collision is already carried by `case-conference` and
  `practice-administration`; a third assertion adds nothing.
- **`medical`** — a clinician's own learning material about their own condition is a real but marginal
  case, and it is the schema row's holder-versus-subject question rather than this row's.
- **`legal`** — an M&M teaching record can be discoverable, but that is
  `clinical_practice.malpractice-incident`'s world and already edged from there.

## NEEDS-JOSEPH

- **NJ-CP-15 · Two reciprocals owed, both authored one-way here.** Verified by grep that the landed
  `academic.teaching.json` and `research.conference-presentation.json` do **not** name
  `clinical_practice`; both are outside my five and I did not edit them.
  - The **academic** one is substantive: a clinician is a teacher and a learner in the same corpus,
    often in the same week, and the identical artifact — deck, handout, item bank, feedback — sits on
    both sides. Slide structure, learning objectives and an answer key discriminate *neither*. R1c
    should decide whether this is a collision, a co-activation, or a `role_split` on a field that does
    not exist yet.
  - The **research** one is narrower: a grand-rounds deck and a conference presentation are the same
    artifact for two audiences.
- **NJ-CP-16 · Should a teaching case whose de-identification cannot be VERIFIED be treated as
  protected by default?** My answer is yes, and it is written into `sensitivity` and into the Protected
  Records fallthrough. But it makes the product more cautious than the user's own belief about their
  files: a clinician who has carefully anonymised a teaching set will experience it as the system
  disbelieving them. That trade is Joseph's to confirm, and it does not depend on whether
  `clinical_practice` ever gets field rows.

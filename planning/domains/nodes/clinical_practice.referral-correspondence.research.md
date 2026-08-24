# clinical_practice.referral-correspondence — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `clinical_practice.research.md`; all quotations machine-verified verbatim.
Landed siblings read for key set and idiom: `medical.personal-health-records.json` (the direct
counterpart — this row shares its hardest boundary), `medical.json`, `legal.practice-matter-file.json`.
Legacy row absorbed per `ROSTER.md` Appendix A line 596: `med.clinician-referral-sent` (ROW).

## What it is for, and what it holds

A clinician's **outbound letter file**, plus the replies that answer it. Referrals made, clinic and
discharge letters written to other clinicians, acknowledgements and appointment offers received back,
onward and tertiary referrals, reports issued to insurers/employers/schools/agencies on a patient's
behalf, records-request responses, secure-message threads, dictations awaiting typing, and the
**correspondence register** that tracks whether each item was sent and answered. The organizing anchor
is the correspondence **item and its direction of address**, not the patient's accumulated record.

## Node test — passes, and the memo records the doubt

Detection signals differ from every sibling: **three distinct person-shaped roles in three labelled
positions** (addressee clinician / subject / signing holder), plus reply-pairing and a sent-or-answered
register. That register is a workflow the chart simply does not contain, and a real clinician keeps a
sent-letters file separate from charts.

The doubt, stated rather than hidden: **the same letter is routinely in both this row and
`clinical_practice.patient-chart`, often byte-identical** — the universal `duplicate_family` fact will
join the two copies. So a large fraction of real files will legitimately evidence both rows, and
neither has dimensions today. My position is that they stay two rows; the question belongs to R1c with
the whole family in view, and it is in the JSON's `open_question`.

## Files considered and rejected

- **`Referral letter template.docx`** — kept as the collision fixture. Letter structure alone is the
  tempting false file: an addressee, a greeting, a body and a sign-off describe every letter ever
  written.
- **`Your appointment - outpatient cardiology.pdf`** — kept as the *reciprocal* fixture against
  `medical.personal-health-records`. This is the most confusable pair on the roster, because the
  patient is routinely copied in on the very same document.
- **`Letter from cardiology re Mr Smith.pdf`** — kept deliberately as an **inbound** file that still
  belongs here, because a reply received against a referral the holder made is part of the same
  correspondence item. Direction of address is the signal; direction alone is not the rule.
- **A fax cover sheet** — rejected as a standalone example; folded into the scanned-letter fixture as a
  fax header strip observation.
- **A patient's own copy of the same clinic letter** — rejected: same bytes, different world, and that
  is exactly the boundary NJ-CP-1 is about.

## proposed_fields

**None** — deferred to the schema row's single `subject_of_record` proposal. A "direction" key was
tempting (sent versus received is the property this situation is really organized by) and I did **not**
mint it: it would be a new canonical field invented by a placeholder template, which is the thing the
contract most forbids. It is recorded as prose in `template.why` so R1c can act on it if fields land.

## Neighbours considered that did NOT get an edge

- **`photos`** — no `also_schema` case arose here that the chart row does not already carry.
- **`legal`** — a records-request response is a legal instrument, but the disclosure/production world
  is `clinical_practice.malpractice-incident`'s and `legal.practice-matter-file`'s; edging it here
  would be a third assertion of the same pair.
- **`hr`** — occupational-health reports to an employer sit close to the third-party-report work type.
  Left unasserted at gist depth; the `hr` row has not landed.

## NEEDS-JOSEPH

- **NJ-CP-1 (reciprocal, restated here because this row shares it).** The **clinician-authored versus
  patient-held** boundary. This row's `collides_with` names `medical.personal-health-records` and gives
  the discriminator: the holder in the sign-off / referred-by block with a differently named subject
  (this row) versus the holder in the patient or re slot, or second-person prose addressed to the
  holder (`medical`). Letterhead, headings and record numbers discriminate neither. The landed
  `medical.personal-health-records.json` **does not name `clinical_practice`** — verified by grep, and
  not edited, since it is outside my twelve. **R1c owes the reciprocal on the medical side.**
- **NJ-CP-9 · Should this row and `clinical_practice.patient-chart` remain two rows?** Argued both ways
  in the JSON `open_question`; my answer is yes, on the strength of the correspondence register, but it
  is R1c's to settle with the family in view.
- **NJ-CP-10 · Is a clinician's fee-bearing report to a third party correspondence at all**, or a
  deliverable belonging with `clinical_practice.practice-administration` (or, on its commercial
  evidence, `career.consulting-client-engagement`)?

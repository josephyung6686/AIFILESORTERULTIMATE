# clinical_practice.malpractice-incident — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `clinical_practice.research.md`; all quotations machine-verified verbatim.
Landed siblings read for key set and idiom, and specifically for how a professional row abstains from
legal conclusions: **`legal.practice-matter-file.json`** (its `sensitivity_why` and `never_alone` set
the precedent I followed), plus `medical.json`, `medical.personal-health-records.json`. Legacy row
absorbed per `ROSTER.md` Appendix A line 595: `med.clinician-malpractice-incident` (ROW).

## What it is for, and what it holds

Something has gone wrong, or is alleged to have gone wrong, in the holder's clinical care — and the
indemnity cover standing behind it. The lifecycle runs internal incident report → complaint →
duty-of-candour letter → investigation → claim → expert report → disclosure → outcome. It holds
incident and near-miss reports, complaints and their formal responses, open-disclosure letters,
root-cause analyses, clinician statements, indemnity policy schedules and premium invoices, letters of
claim and claims correspondence, medico-legal and expert reports, disclosure bundles, regulatory and
disciplinary notices, settlement and closure records, and learning/action-plan returns.

## Node test — passes clearly

Detection signals are specific and unlike anything else on the family: an incident-reference plus
date-and-time-of-incident structure; a complaint-and-response-deadline structure; a
letter-of-claim-plus-claims-handler structure; an indemnity policy structure. Privacy rules differ
sharply, in a way I want on the record: **the exposure runs in two directions at once.** The material
concerns a named patient's care *and* an allegation against the holder personally, so a leak harms
someone who is not the user and someone who is. That is stated in the JSON as inference, not as a `00`
claim.

This is also the row where the **folder label is more dangerous than the folder contents** — a branch
named for an incident or a claim discloses, from the namespace alone, that an allegation exists. That
is disclosure by structure, and it is the strongest argument on the whole roster for an empty
`dimension_order`.

## The abstention discipline

Three-schema world (clinical + legal + finance), and the product must adjudicate none of it. Written
into `never_alone`: **no inference of fault, causation, breach, liability, privilege, or
admissibility**, and a source system's own harm or severity designation is a **raw observation**, never
this product's sensitivity classification. An apology is not an admission. An allegation is not a
finding. A claim is not a liability. `legal.practice-matter-file.json` sets exactly this discipline and
I copied it deliberately rather than reinventing a weaker version.

## Files considered and rejected

- **`Incident reporting policy v7.pdf`** — kept as the collision fixture. A policy is *about* incidents
  and is not one; it belongs to the sibling `clinical_practice.protocol-guideline`.
- **`Premium invoice`** — kept, to make the point that the invoice alone is a finance record and the
  indemnity context comes from the policy number, not the amount.
- **A coroner's inquest bundle** — real and in scope, but structurally the same as the disclosure
  bundle already used; earns a `work_type` value rather than a second archive fixture.
- **A patient's own complaint letter held by the patient** — rejected; that is `medical` /
  `legal.personal-legal-matters` material, and the role reversal is the schema row's business.

## proposed_fields

**None** — deferred to the schema row's single `subject_of_record` proposal. An incident-reference key
would have been tempting and I did not mint one: it is a *value* of a document reference, and minting
per-situation identifier keys is precisely the 574's failure mode.

## Neighbours considered that did NOT get an edge

- **`hr`** — disciplinary process against a clinician-employee overlaps heavily. Left unedged: the
  discriminator (is the allegation about clinical care or about employment conduct?) is real but the
  `hr` row has not landed and I did not want to author its half of a pair blind.
- **`government`** — regulator investigations are statutory. Same reasoning; unasserted, not denied.

## NEEDS-JOSEPH

- **NJ-CP-7 · May an incident or claim packet be MOVED at all, even inside a frozen tree?** Moving a
  claim bundle changes paths other people's processes may depend on, and the existence of a
  differently-named branch is itself a disclosure. Represent-in-place is a defensible permanent answer
  here, independently of whether the schema ever gets fields.
- **NJ-CP-8 · The boundary against `legal.practice-matter-file` when the holder is BOTH clinician and
  instructing party** — a clinician-director receiving a claim about a colleague's care. Evidence
  supports both rows; the roster gives no rule. R1c should decide whether this needs a reciprocal edge
  on the legal side or is simply an unresolved-outcome case.

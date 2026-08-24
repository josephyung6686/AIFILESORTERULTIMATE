# clinical_practice.licensure-credentialing — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.
**This is the weakest of my six rows and the memo says so plainly.**

## Sources

Same authority stack as `clinical_practice.research.md`; all quotations machine-verified verbatim.
Landed siblings read closely for this row in particular: **`career.credentials-licenses.json`** (the
overlap), plus `medical.personal-health-records.json`, `medical.json`,
`legal.practice-matter-file.json`. Legacy rows absorbed per `ROSTER.md` Appendix A lines 593–594:
`med.clinician-licensure-credentialing` (ROW), `med.clinician-cme` (FOLD — CME is the evidence a
registration consumes).

## What it is for, and what it holds

Proving, repeatedly and to several different bodies, that the holder may **treat patients**: statutory
registration and revalidation, hospital privileging, payer or panel enrolment, scope-of-practice
authorisations, and the continuing-education, audit and logbook evidence those cycles consume. It
holds certificates, good-standing letters, privileging applications and grants, enrolment records,
appraisal and revalidation portfolios (usually as archives), CPD certificates and logs, procedure
logbooks, primary-source-verification correspondence, renewal notices and fee receipts, and
disciplinary or conditions notices.

## Node test — passes, but weakly, and the weakness is recorded as an edge

**Kept, not refused.** Reasoning: the refusal test for a template asks whether its signals, dimensions
and privacy rules are identical to *its own schema's default* — they are not. The overlap that
actually worries me is with a template on a **different** schema (`career.credentials-licenses`), and
the closed vocabulary handles that with `collides_with`, not with a refusal. So I kept the row and
made the overlap explicit and prominent rather than quietly asserting a distinction I do not fully
believe.

What this row can honestly claim as its own: a **requested-privileges / scope-of-practice list**, a
**payer or panel enrolment designation**, a **revalidation cycle with required-evidence sections**, and
**case-log evidence about patients**. None of those appears on a general professional licence, and the
last is why the row sits on the `clinical_practice` schema at all — it is the one situation on this
family where the holder's *own* professional evidence carries third-party case material.

What it cannot claim: on the single most common file — **a certificate** — the two rows are not
distinguishable, and neither should win on that evidence alone.

## Files considered and rejected

- **`Employment contract - consultant post.pdf`** — kept as the collision fixture against
  `career.employment-records`. A clause requiring registration is not a credential.
- **`Revalidation guidance for doctors.pdf`** — kept as a second fixture: guidance is *about* the
  process, not evidence of it. This is the mistake I most expect a detector to make.
- **A medical school degree certificate** — rejected. It is an academic credential; the row is about
  the right to practise, not the qualification behind it.
- **A conference attendance badge photo / hotel receipt from a CPD trip** — rejected as noise; the
  receipt is `Receipts and Confirmations` and the badge is `One-Off Images`.

## proposed_fields

**None.** Deferred to the schema row's single `subject_of_record` proposal. Note that
`career.credentials-licenses` made a matching judgement call — it proposed only the one concept no
other row had claimed — and duplicating an issuing-authority or credential-title key here would put
two rows in competition over the same unminted vocabulary.

## Neighbours considered that did NOT get an edge

- **`finance.subscriptions-utilities`** — renewal fees are recurring payments, but a regulator fee is
  not a subscription and the confusion is thin. Left unasserted.
- **`government`** — a health regulator is a statutory body and the roster has a `government` schema.
  I did not author the edge at gist depth: the discriminator (does the body license clinical practice
  specifically?) is real but needs the `government` row's own view, which has not landed.

## NEEDS-JOSEPH

- **NJ-CP-2 · Should this row exist at all, or fold into `career.credentials-licenses`?** This is a
  genuine fold question, not a formality.
  **For keeping:** the credentialing *workflow* (privileging, enrolment, revalidation cycles) has
  detection signals and privacy rules a general licence row does not have, and it is the only place on
  this family where the holder's own evidence carries patient material.
  **For folding:** on a bare certificate the two rows are indistinguishable, and *neither* has any
  dimensions today because both schemas are field-less — so the node test's third leg cannot separate
  them in either direction.
  This row does not settle it and does not pretend the overlap is smaller than it is.
- **NJ-CP-6 · Where does continuing education live?** Here, as evidence a registration cycle consumes
  (which is how `med.clinician-cme` was folded by R1a), or on `academic.continuing-education`? Both
  readings are defensible and the same certificate satisfies both.

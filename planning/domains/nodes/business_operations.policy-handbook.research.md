# business_operations.policy-handbook — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

`00-database-agent-product-design.md` (all quotations machine-verified verbatim), `ALIGNMENT.md`,
`_CONTRACT.md`, `CONNECTION.md`, `CONNECTION-EXAMPLES.md`, `roster.json`, `canonical_fields.json`,
`DECISION-BRIEF.md` (J-IND, D1, PR-6), `ROSTER.md` §4 + Appendix A lines 818–819. Reference standard
for depth, idiom and key set: the landed `clinical_practice.*` files.

## What it is for, and what it holds

Documents that state binding rules for an organisation's people, and then govern themselves. Policies,
employee handbooks, codes of conduct, standard operating procedures and work instructions, plus the
apparatus that makes them controlled documents: revision histories, approvals, effective and review
dates, and the acknowledgements that prove people received them.

## Node test — passes, on the control block

The anchor is the **governing document as a controlled thing** — an owner, a version, an effective
date, a review date. That block is the row's strongest signal and it exists in no neighbouring
situation: contracts have parties and signatures, standards have issuing bodies, specifications have
requirement identifiers. Privacy rules also differ, in one direction only: the acknowledgement half is
a personnel roster, and that is what drives the row's `potentially_sensitive` value. Dimensions do not
differ, and cannot, because the schema declares no fields.

## Legacy ids absorbed (ROSTER.md Appendix A)

`ops.policy-handbook` (ROW, line 818) and `ops.process-documentation` (FOLD, line 819). The fold is
correct and worth stating: a policy says what must happen and a procedure says how, and organisations
keep them as one controlled set with one control block format.

## Files considered and rejected

- **`Home insurance policy 2026.pdf`** — kept as the primary collision fixture and, I think, the single
  most likely false positive anywhere in my nine rows. The word *policy* names a contract of insurance
  as readily as a governing document, and both are numbered clause documents with exclusions.
- **`Supplier - code of conduct signed.pdf`** — kept as the second fixture: a countersigned code is a
  contractual instrument, not this row.
- **A privacy policy scraped from a website** — same false-positive family as the insurance case;
  covered by the `never_alone` entry rather than given a fixture.
- **A regulator's guidance note** — real and common, and it routes to `Reading Inbox`; recorded there
  rather than as a fixture, since the downloaded-template example already carries the not-ours case.

## proposed_fields

**None.** PR-6 forbids field rows on this schema.

## Neighbours considered that did NOT get an edge

- **`nonprofit.governance`** and **`government.public-authority-record`** — both keep policy libraries
  in exactly this shape. Left unedged at gist depth; `government.policy-development` already carries
  the public-body confusion and one edge per confusion is enough here.
- **`clinical_practice.practice-administration`** — clinical protocols are governing documents too, but
  the discriminator is the same one `manufacturing.work-instruction` already states.
- **`research.ethics-compliance`** — SOPs under a protocol; same reasoning.

## NEEDS-JOSEPH

- **NJ-BO-6 · Do acknowledgements stay with the policy or move to HR?** Keeping them here makes the
  situation whole — a rule and the proof it was received are one controlled set, which is how compliance
  functions actually file — but it means a row about rule documents carries a roster of named staff, and
  that half alone drives the row's sensitivity value. Splitting them would give the governing documents
  a much lighter posture at the cost of breaking the set. Reciprocally stated: the
  `hr.onboarding-offboarding` side should carry the same question. Not resolved here, because the answer
  decides whether a real user's policy folder is ordinary or protected material.

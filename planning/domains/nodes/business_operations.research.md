# business_operations — lab notes (schema row)

**Depth: GIST** (J-IND). Honest map of the family, not deep per-industry research. Not padded.
This row was **salvaged**: a structurally complete but unverified draft existed with no memo. It was
verified line-by-line rather than discarded or trusted; what changed is recorded under *Salvage* below.

## Sources

`planning/00-database-agent-product-design.md` (source of truth; all 40 quotations in the JSON were
machine-verified verbatim against it), `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`
(rules 8, 10, 11–15), `planning/domains/CONNECTION.md` (§2 node test, §4 activation, §5 closed edge
vocabulary, §6 field identity), `CONNECTION-EXAMPLES.md` (the `.ics` fixture in particular),
`planning/domains/canonical_fields.json`, `planning/domains/roster.json`,
`planning/overnight/council/DECISION-BRIEF.md` (D1, D4, D6, PR-2, PR-6 taken as ratified and not
re-debated), `ROSTER.md` §4 and Appendix A (this family absorbs slice 11's 45 legacy ids as 20
`business_operations.*` rows plus 10 `hr.*` rows, with `corp.regulatory-filings`,
`corp.compliance-audit` and `soft.tech-compliance-evidence` arriving from other slices).
Landed siblings read for key set and idiom: `clinical_practice.json`,
`clinical_practice.case-conference.json`, `finance.small-business-bookkeeping.json`,
`legal.leases-agreements.json`, `career.consulting-client-engagement.json`.

## Salvage — what was verified, and what changed

Verified and kept: the key set matches the landed `clinical_practice.json` exactly (27 keys, no
extras, no omissions); every one of the 40 quoted spans appears verbatim in `00`; every
`collides_with` and `also_holds_with` target is a real roster **schema** id (correct for a schema
row); every `falls_through_to` target is one of `00`'s nine residual names spelled `00`'s way; every
`file_examples.source_type` is in P5's fourteen; `fields: []` and `dimension_order: []` hold, as PR-6
requires; no threshold, score, or P7 handling class appears anywhere.

Changed: **nothing substantive.** The draft was correct. Two things are recorded rather than edited:

- Its `role_split` entry spells the neighbour key `other_domain`. The landed corpus is inconsistent
  here — `academic.*` and `career.*` use `neighbor`, `research.*` uses `other_domain`, `finance.json`
  uses `domain` with `our_field`/`their_field`. This is a **catalogue-wide normalisation for R1c**,
  not a defect of this row, and the row was left in the spelling a landed sibling already uses.
- The draft author's own arithmetic in `open_question` (4) says "24 templates on a field-less schema";
  the roster carries 25 `business_operations.*` rows including this schema row, i.e. 24 templates.
  Correct as written.

The memo it lacked is this file, and ownership of the row is now taken.

## What this family is FOR

How an organisation runs **itself** — as opposed to what it sells, who works there, or what a
professional does for a client. Its anchor is an organisational unit running a **cycle** or a
**project** and producing a document with a **function**. That triple is what keeps it apart from
`career` (a person's own record), `finance` (custodial and statutory money), `hr` (people-identifying
material), `legal` and `law_practice` (instruments and matters), `government` and `nonprofit` (the
other side, and the other owner type).

## Node test — passes, as a placeholder schema

It passes as the **schema** the 24 template rows point at, not because it declares a distinct field
set — under D1 as narrowed it declares none. That is the honest reading of PR-6: a row may describe a
domain and write no field rows. The two things it does carry are load-bearing: a recognition contract
that separates this world from six adjacent ones, and the `proposed_fields` argument that names the
field-shaped holes.

## proposed_fields (both for R1c, neither minted)

- **`organization`** — the CUSTODY role: whose operating record this is. Unheld today. `our_firm` is
  the authorship role and is correctly never destination-eligible; `client` is its counterparty
  partner; `institution` is the finance-side issuer. Proposed `destination_eligible: false`, because
  inside a single-entity corpus an organisation level is exactly the collector `00`'s template
  validator rejects — and the tension is stated rather than resolved, because a corpus spanning two
  entities genuinely needs it.
- **`fiscal_period`** — the management calendar. `tax_year` is a jurisdiction's statutory year and
  reusing it would assert a coincidence that routinely does not hold. Four rows in this family want
  this key (budget, board, filings, audit) and none can have it. This is the clearest field-shaped
  hole the pass found.

A **third** hole is named but deliberately not proposed here: the **supplier / buying-side** role.
`00`'s pair is `our_firm` / `client`; a supplier in a buy-side register and a subscription customer
are two further roles with no key. Raised on `contract-administration` and
`customer-account-management` rather than smuggled onto the schema.

## Files considered and rejected

- **An org chart** — real, and it went to `hr.org-design-headcount` rather than here the moment it
  names people; the role-only version stays and earns a `work_type`, not an example.
- **A supplier invoice** — kept only as the `Receipts and Confirmations` fallthrough, because on its
  own it is a transactional document and this schema does not own transactions.
- **A CRM export** — considered and dropped: it is a system dump, and its interesting members are the
  contacts data `00` already rules out of folder proposals.

## Neighbours considered that did NOT get an edge

- **`retail_hospitality`, `logistics`, `resource_operations`, `manufacturing`, `construction_property`** —
  each runs governance, budgets and procurement, so a `collides_with` to all five would be true and
  useless. The sector confusions are stated where they actually bite: on the template rows.
- **`academic`** — an MBA case study and a university's own administration both look like this. Left
  to the `never_alone` entry on business vocabulary rather than an edge, at gist depth.
- **`identity`, `medical`** — no honest confusion at schema level.

## NEEDS-JOSEPH

- **NJ-J-IND-3 (carried, and this family's most load-bearing)** — where does an *organisation's*
  money live? The roster's reading is statutory-and-custodial to the `finance` safety schema,
  forward-looking-management to `business_operations`. Defensible; drawn by the roster pass, not by
  `00`. `budget-forecast` and `corporate-regulatory-filings` both break if it is wrong.
- **NJ-J-IND-4 (carried, this row's variant)** — this row correctly does **not** carry
  `is_safety_domain`, and should not; but its material is frequently confidential to a **third
  party** who is not the user. If the flag stays with `00`'s four, the substitute mechanism that
  forces P7 ahead of a model path for confidential commercial material must be named somewhere.
- **NJ-BO-1 · Are `organization` and `fiscal_period` allowed to become canonical keys?** For R1c.
- **NJ-BO-2 · Is 24 templates on a field-less schema the right shape?** This pass examined nine of
  them. Eight pass the node test comfortably; `go-to-market` is the weakest and states its own fold
  question. The commercial cluster (`customer-account-management`, `partnerships-bd`,
  `go-to-market`, `market-research`) is where a trim would be cheapest if one is wanted.
- **NJ-BO-3 · `role_split` key spelling is inconsistent across the landed catalogue** (`neighbor` /
  `other_domain` / `domain` + `our_field` / `their_field`). Mechanical, but it is a stored join
  handle and D6's reasoning applies to it. R1c's to normalise; no row should do it unilaterally.

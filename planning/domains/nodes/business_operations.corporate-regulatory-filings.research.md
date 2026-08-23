# business_operations.corporate-regulatory-filings — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `business_operations.research.md`; all quotations machine-verified verbatim
against `00-database-agent-product-design.md`. Landed siblings read for key set and idiom:
`business_operations.json`, `finance.tax-filings.json`, `finance.cap-table-equity.json`,
`identity.core-documents.json`. Legacy row absorbed per `ROSTER.md` Appendix A line 542:
`corp.regulatory-filings` (ROW). D4 (jurisdiction is a value, never a field name and never a
destination dimension) is taken as ratified and shaped this row more than any other.

## What it is for, and what it holds

Documents an entity — or a person acting for one — is **required** to submit to an authority or
registry, and the authority's responses. Annual confirmations and returns, registry change
notifications, beneficial-ownership statements, sector returns, submission receipts,
acknowledgements, registry certificates and searches, reminder and penalty notices, filing calendars,
and agent authorisations.

## Node test — passes, on compulsion

The anchor is an **obligation to an authority** with a deadline and a filing reference: a document
whose existence is compelled from outside. Detection signals are strong and unlike any sibling's — a
machine-issued submission receipt, a registry certificate with a seal and a registered number, a
statutory form with a labelled entity-identifier and period pair, a compelled notice with a statutory
deadline and a consequence statement.

The discriminator that had to be stated explicitly is **obligation versus request**: a permit
application, a grant application and a tender are also addressed to authorities and are not returns.
That is the `Planning application` fixture.

## The D4 consequence, stated plainly

This is the most jurisdiction-shaped row in the family, and the correct response under D4 is that it
names **no authority and no return name of its own**. Every one belongs in R4's gazetteers and R5's
one jurisdiction's values. The row's `proposed_context_terms` are deliberately generic filing
vocabulary, not a jurisdiction's form numbers. Whether v1's gazetteer covers enough authorities for
the row to fire at all is a P10 planning question and is recorded as such.

## Files considered and rejected

- **`Companies House filing guidance.pdf`** — kept as the collision fixture. An authority's published
  guidance is reading material, not the entity's filing.
- **`Planning application - 26-00412-FUL.pdf`** — kept as the obligation-versus-request fixture.
- **`CT600-2025-2026.xml`** — kept deliberately as the format fixture: the `.xml` extension fires
  nothing; the root element and labelled period elements do.
- **`AP01 - appointment of director.pdf`** — kept because it is the row's sharpest sensitivity case: a
  corporate filing carrying an individual's date of birth and address.
- **A personal self-assessment return** — considered and rejected. It is the person's own record and
  belongs with `finance.tax-filings` under the safety schema; keeping it here would have quietly
  claimed safety-domain material.

## proposed_fields

**None** — deferred to the schema row. This row wants `organization` (a person filing for two
entities is its defining hard case) and `fiscal_period`, and mints neither. Note the row's own
`must_not_conclude` refuses `tax_year` on a registry period for exactly the reason the schema row's
`fiscal_period` argument gives.

## Neighbours considered that did NOT get an edge

- **`identity.core-documents`** — a certificate of incorporation is the entity's identity document,
  and the parallel is real. Not edged, because `identity` is a safety schema whose subject is a
  *person*, and asserting the pair would blur that; noted for R1c.
- **`government.public-records-foi`**, **`government.statistical-programme`** — authority-side rows
  with returns of their own. The which-side discriminator is already carried by the
  `government.public-authority-record` collision.
- **`logistics.customs-export`** — customs declarations are compelled returns with references and
  deadlines. Genuinely close; left unedged at gist depth and flagged for R1c.

## NEEDS-JOSEPH

- **NJ-J-IND-3 (carried, in its most literal form)** — a corporate tax return is simultaneously this
  row's compelled filing and the finance safety schema's custodial record. The roster's split sends
  `corp.regulatory-filings` here and corporate accounting to `finance`. This row cannot settle it.
- **NJ-BO-10 · Gazetteer coverage gates this row.** Under D4 the row names no authorities, so it fires
  only as far as R4/R5 reach. If v1 ships one jurisdiction's gazetteers, this row is effectively
  one-jurisdiction at launch, and that should be a stated consequence rather than a surprise.

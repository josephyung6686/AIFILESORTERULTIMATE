# Field hygiene — jurisdiction smuggled into field names

The dispatch mandate: mark catalogue entries that already baked a jurisdiction into a **field
name**, list them for deletion/rename, and re-check D4's "none of 560" claim at 574. Scanned
2026-08-22, mechanically, over all 14 `planning/domains/*.json` slices — 574 entries, 3,706
schema-field rows plus 1,648 `dimension_order` members (5,354 names scanned; the 1,648 matches
`_CONTRACT.md` rule 8's own dimension count).

## Result 1 — the class D4 checked: still zero

**No field name bakes in a jurisdiction-specific artifact.** Zero fields of the `w2_tax_year`
class (tokenized scan over every field and dimension name for jurisdiction-specific tokens:
form codes, agency acronyms, national-scheme names — `w2`, `1099`, `p60`, `vat`, `irs`, `hmrc`,
`nhs`, `ssn`, `nino`, `fafsa`, `medicare`, and several dozen more, split on underscores so
`vat_number` cannot hide). D4's recorded claim — "A jurisdiction-specific **field** name
(`w2_tax_year`) is the thing that would make it one-way; none of the 574 entries has done that,
and none may" (`_CONTRACT.md` rule 9) — **re-confirmed at 574.**

The catalogue authors held the altitude line the seat record describes: form names appear only
as *examples and recognition strings* (`VAT`, `grant of probate`, `council tax banding`,
`explanation of benefits`, `superbill`, `Companies House`), and the 574's own field prose says
so out loud — `tax.filing`'s `return_type` is "described functionally, never by a
jurisdiction's form name", `admin.licences-permits`' `licence_type` is "written functionally;
permission regimes are wholly local". Those strings are exactly the values this catalogue's
packs exist to hold.

## Result 2 — the class D4 did not scan: 35 rows name jurisdiction itself

D4's ratified sentence has three clauses: a value, **never a field name**, never a destination
dimension. The `w2_tax_year` check covers baked-in *artifacts*; a second class bakes in the
*concept*: **29 fields literally named `jurisdiction`, 4 `*_jurisdiction` variants, and 2
`governing_law` fields — 35 rows across 34 entries.** Two counts follow, and they differ:
**4 of the 35 field rows also appear by name inside their entry's `dimension_order`**, and a
direct scan of all 1,648 `dimension_order` members under the same name predicate finds **6
jurisdiction-named dimension members** — the 4 that mirror field rows, plus 2 compound
dimension names that exist only in a `dimension_order` and match no schema field name. All 6
are the destination-dimension clause violated as written. (The risk seat counted the 29 —
"29 field rows carry a `jurisdiction` field outright" — before the ratification made them
illegal; the brief's "none of 560/574" sentence is about the `w2_tax_year` class only. The
two claims coexist; this file is where the second class is finally listed.)

### The six destination-dimension hits — P10's one-way door, expressed in legacy data

| slice | entry | dimension_order |
|---|---|---|
| `02-career-recruiting` | `career.professional-license` | `licence_type` → **`jurisdiction`** |
| `03-research-science` | `res.patent-disclosure` | `docket` → **`jurisdiction`** → `status` |
| `05-finance-legal-admin` | `tax.filing` | `filing_entity` → **`jurisdiction`** → `tax_year` → `document_type` |
| `05-finance-legal-admin` | `admin.immigration` | `applicant` → **`destination_jurisdiction`** → `application` → `document_type` |
| `06-healthcare-medicine` | `med.clinician-licensure-credentialing` | `practitioner` → `licence_type` → **`issuing_board_or_jurisdiction`** |
| `13-trades-property-logistics` | `log.customs-export` | **`jurisdiction_or_route`** → `shipment` → `document_type` |

The last two are the dimension-only compounds, invisible to a scan that only cross-references
schema-field hits against dims (the first pass of this scan — see Method): the
`med.clinician-licensure-credentialing` schema declares `issuing_board` and `jurisdiction` as
two separate fields (hence its row below marks the field named `jurisdiction` as not itself a
dims member, with the fusion noted) and its template fuses them into one jurisdiction-named
dimension; the
`log.customs-export` schema declares **no** jurisdiction-named field at all — its
`jurisdiction_or_route` exists nowhere but the `dimension_order`, which is why the entry has
no row in the 35-row list below.

### The full list, for deletion/rename

| slice | entry | field | in dims | example value |
|---|---|---|---|---|
| `02-career-recruiting` | `career.onboarding-paperwork` | `tax_jurisdiction` | no | California |
| `02-career-recruiting` | `career.employment-contract` | `governing_law` | no | England and Wales |
| `02-career-recruiting` | `career.professional-license` | `jurisdiction` | **YES** | California |
| `03-research-science` | `res.patent-disclosure` | `jurisdiction` | **YES** | US; EP |
| `05-finance-legal-admin` | `tax.filing` | `jurisdiction` | **YES** | United Kingdom |
| `05-finance-legal-admin` | `tax.supporting-documents` | `jurisdiction` | no | Canada |
| `05-finance-legal-admin` | `biz.payroll-employer` | `jurisdiction` | no | Ireland |
| `05-finance-legal-admin` | `corp.business-formation` | `jurisdiction_of_incorporation` | no | England and Wales |
| `05-finance-legal-admin` | `fin.loan-mortgage` | `jurisdiction` | no | United Kingdom |
| `05-finance-legal-admin` | `legal.contracts` | `governing_law` | no | England and Wales |
| `05-finance-legal-admin` | `legal.lease` | `jurisdiction` | no | England and Wales |
| `05-finance-legal-admin` | `legal.litigation-dispute` | `jurisdiction` | no | England and Wales |
| `05-finance-legal-admin` | `legal.wills-trusts-estates` | `jurisdiction` | no | Scotland |
| `05-finance-legal-admin` | `legal.power-of-attorney` | `jurisdiction` | no | England and Wales |
| `05-finance-legal-admin` | `corp.regulatory-filings` | `jurisdiction` | no | United Kingdom |
| `05-finance-legal-admin` | `admin.licences-permits` | `jurisdiction` | no | United Kingdom |
| `05-finance-legal-admin` | `admin.immigration` | `destination_jurisdiction` | **YES** | Canada |
| `05-finance-legal-admin` | `admin.immigration` | `nationality_jurisdiction` | no | United Kingdom |
| `05-finance-legal-admin` | `legal.court-records` | `jurisdiction` | no | England and Wales |
| `05-finance-legal-admin` | `legal.notarised-documents` | `jurisdiction` | no | Nigeria |
| `05-finance-legal-admin` | `legal.debt-collection` | `jurisdiction` | no | United Kingdom |
| `05-finance-legal-admin` | `legal.bankruptcy-insolvency` | `jurisdiction` | no | England and Wales |
| `06-healthcare-medicine` | `med.advance-directive` | `jurisdiction` | no | (functional prose) |
| `06-healthcare-medicine` | `med.clinician-licensure-credentialing` | `jurisdiction` | no — but dims carry the fused **`issuing_board_or_jurisdiction`** (see dims table) | (functional prose) |
| `06-healthcare-medicine` | `med.public-health-reporting` | `jurisdiction` | no | (functional prose) |
| `07-law-legal-practice` | `law.matter-file` | `jurisdiction` | no | (functional prose) |
| `07-law-legal-practice` | `law.pleadings` | `jurisdiction` | no | (functional prose) |
| `07-law-legal-practice` | `law.legal-research` | `jurisdiction` | no | (functional prose) |
| `07-law-legal-practice` | `law.opinions` | `jurisdiction` | no | (functional prose) |
| `07-law-legal-practice` | `law.knowhow-precedents` | `jurisdiction` | no | (functional prose) |
| `12-government-civic` | `gov.public-authority-record` | `jurisdiction` | no | (functional prose) |
| `12-government-civic` | `gov.intergovernmental-agreement` | `jurisdiction` | no | (functional prose) |
| `12-government-civic` | `gov.elections-administration` | `jurisdiction` | no | (functional prose) |
| `12-government-civic` | `gov.defence-veterans-administration` | `jurisdiction` | no | (functional prose) |
| `12-government-civic` | `npo.governance` | `jurisdiction` | no | (functional prose) |

## Disposition

**The 574 are superseded, not migrated** (`_CONTRACT.md` R0 delta: the pre-R0 entries "are
superseded by R1's roster, not migrated in place"), so the deletion is R1 declining to carry
these forward rather than an edit to the legacy slices. Three facts make the debt contained:

1. **`planning/domains/canonical_fields.json` is clean.** None of its 37 keys is
   jurisdiction-named (this catalogue's `check.py` asserts it on every run, so it stays clean).
   No jurisdiction field can reach P6's `fields` table, §3.4's cache key, or a template's
   branch order through the canonical list.
2. **The six `dimension_order` hits die with their entries.** R1 templates may only branch on
   canonical fields (`_CONTRACT.md` rules 8 and 12); with no canonical `jurisdiction` key, the
   dimension is inexpressible in the new roster — and inexpressible in this directory by
   construction. The two dimension-only compounds die the same way: neither
   `issuing_board_or_jurisdiction` nor `jurisdiction_or_route` resolves to any canonical key.
3. **What the field was doing is absorbed by the pack.** In a one-jurisdiction deployment
   (D4), "which jurisdiction is this record from" is deployment metadata — the loaded pack's
   tag — not a per-file fact. Rows in this catalogue carry `jurisdiction` as a value tag, which
   is the ratified sentence realized.

**Rename candidates rather than deletions — flagged, not decided:**

- `governing_law` (2 rows). The field name is not the word `jurisdiction` and "governing law"
  is a real clause on real contracts; but its values are polities, so it is a jurisdiction
  field in function. Its future is D1's question — contract/legal fields are deferred to
  Joseph — and the D4-clean respelling, if he wants one, is a value of a functional field
  rather than a dedicated column.
- `admin.immigration`'s pair (`destination_jurisdiction`, `nationality_jurisdiction`). The
  entry's own why-text argues the domain "is inherently two-jurisdiction and cannot be written
  with a single jurisdiction field" — the one place in the 574 where a per-file jurisdiction
  fact is arguably load-bearing rather than decorative. D4's letter still forbids the field
  names; whether a future Joseph-authored immigration schema carries the *information* under
  functional names is recorded as NEEDS-JOSEPH (NJ-R5-2 in `RESEARCH.md`), not resolved here.

**Adjacent, below the line** (value-like words inside field names, not jurisdiction-specific;
listed for completeness, no action proposed): `apostille_reference`
(`legal.notarised-documents`) and `witness_or_notary` (`med.advance-directive`) bake a
document-type word into a field name; the ~40 `*_state` fields (`approval_state`,
`decision_state`, …) are workflow states, not polities — a scan for "state" must tokenize, or
it drowns in false positives.

## Method

Underscore-tokenized scan of every `schema[].field` (3,706) and every
`template.dimension_order` member (1,648) across the 14 slices: (a) membership of any token in a
jurisdiction-specific token set (form codes, agencies, national schemes — the `w2_tax_year`
class); (b) field names equal to `jurisdiction`, ending `_jurisdiction`, starting
`jurisdiction_`, or equal to `governing_law`; (c) predicates (a) and (b) applied **directly to
every `dimension_order` member**, not only to schema-field names — the first pass of this scan
only cross-referenced schema-field hits against dims, which is exactly the method that misses
a jurisdiction-named dimension member that is not also a schema field name, and it missed both
compounds (`issuing_board_or_jurisdiction`, `jurisdiction_or_route`) until an adversarial audit
caught them; (d) cross-reference of every schema-field hit against its entry's
`dimension_order`, which is what the 35-row table's "in dims" column records. (`governing_law`
appears in no `dimension_order`; the nearest dims string is `governing_body` on
`edadmin.institution-governance`, an organisation, not a polity — so the six is complete under
predicate (b) with `governing_law` included.) Prose references (the risk seat's "124 of 560" — 124 of 574 on this
scan, matching) are jurisdiction-*dependence*, which is pack business, not field hygiene; the
counts and per-slice breakdown are in `RESEARCH.md` section 3.

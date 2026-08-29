# finance — R1b lab notes

Row: `finance`, `kind: schema`, `launch: safety`, `is_safety_domain: true` (roster).
Output: [`finance.json`](finance.json). Node test: **passed** — refuse_node is false.

## Node test, applied first

`00` states this schema's field set outright: *"Finance files may use institution, account type,
tax year, and record type"*. Four keys, all already canonical, none a respelling of another
schema's. `institution` is not `school` and not `client`; `record_type` is not `work_type` or
`artifact_type` (those are coursework and research artifacts); `tax_year` is not `term` and not
`capture_year`. So the row is a genuine schema, not a template on someone else's fields, and not
an empty industry label. It also needed no giant form: the schema stays at `00`'s four
destination-eligible fields plus **one** privacy/search field.

## Sources used

- `planning/00-database-agent-product-design.md` — read in full. Every quotation in
  `finance.json` was grep-verified against this file before it was written (54 candidate spans
  extracted from the finished JSON and re-checked; the load-bearing ones are listed below).
- `planning/01-product-design-structured.md` — §3.8 (roles, not just entity types), §3.10 (narrow
  dates), §3.11 (domain-scoped schemas, the Finance row of the table), §3.15 (safety domains),
  §5.2 (`Finance and Administration` as a canvas area and the protected-area rule), §5.6
  (template library situations). `00` wins on every point; 01 was used only as a locator.
- `planning/domains/_CONTRACT.md` (rules 4, 5, 6, 8, 9, 10, 11, 14, 15),
  `planning/prompts/ALIGNMENT.md`, `planning/domains/CONNECTION.md` (sections 2, 4, 5, 6; PR-2,
  PR-6, PR-8), `planning/domains/CONNECTION-EXAMPLES.md` (fixtures 4 and 8 are binding on this
  row).
- `planning/domains/roster.json` — confirmed the id, the kind, the four inherited keys, the
  safety flag, the four must-consider neighbours, the two must-consider residuals, and the
  eighteen `kind: template` rows that point at this schema.
- `planning/domains/canonical_fields.json` — all five schema keys resolve here except
  `account_holder` (see below). No synonym was minted: `bank`, `issuer`, `provider`,
  `fiscal_year`, `account type` and `record type` are all already recorded as **aliases** of
  existing keys and were deliberately not used as keys.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` (all twelve file examples and all seven
  `file_kinds.source_types` members check out) and `RELIABILITY_STATES`.
- Neighbour node that had already landed: `nodes/career.json`. Its `collides_with: finance` edge
  (pay statement vs offer letter) is reciprocated here with a compatible signal, and its
  `ADP Pay Statement Mar 2026.pdf` example is re-used deliberately as the mirror fixture so the
  two rows agree on which side owns it. `academic.json`, `code.json`, `photos.json` and
  `college_applications.json` were read for edge alignment; none names finance, so nothing was
  rewritten.
- No `planning/deferred-catalogues/` content was consumed. This row names **rule families**
  (organization gazetteer at word boundary, explicit tax-year pattern, labelled-slot structure)
  and writes no gazetteer contents (R4), no jurisdiction values (R5) and no regex (R2/R6).

## Files considered and rejected

Kept twelve. Rejected:

- **`budget.numbers` / `ledger.ods`** — the same evidence as `Expenses 2026.xlsx`, only a
  different extension. Extensions are `file_kinds` examples, never nodes and never separate
  fixtures.
- **A `.qfx` / `.ofx` bank export** — real, and genuinely finance-shaped, but I could not place
  it in `SOURCE_TYPES` honestly without asserting a routing decision that is P5's
  (`code_structured`? `spreadsheet`? `opaque_binary`?). Dropped rather than guessed; `.csv`
  transaction exports cover the same organizational case under `spreadsheet`.
- **A billing-reminder `.ics`** — calendar was left out of `file_kinds` entirely. CONNECTION
  fixture 5 makes calendar a `SOURCE_TYPE` that fires only on content, and a due-date event's
  content carries an amount and a payee at best. That is the never-alone money figure, so the
  example would have taught the wrong lesson.
- **A `.vcf` for a bank branch** — `00` keeps contact data "privacy-protected rather than used to
  create folder proposals"; `career.json` already carries that fixture and repeating it here adds
  nothing.
- **A passport scan** — CONNECTION-EXAMPLES fixture 4 owns it, and it belongs to `identity`. It
  appears here only inside `Tax2025.zip`'s manifest, which is the more interesting case: an
  identity page arriving inside a finance packet must activate identity on **its own** evidence,
  not inherit finance's.
- **A crypto wallet seed-phrase file** — the roster's `finance.crypto-assets` template hint says
  outright that wallet credentials are identity-safety material, never filed as finance records.
  That belongs to that template's agent and to `identity`, not to this schema row.

## `proposed_fields` justification — `account_holder`

One proposal, and it is `00`'s, not mine. §3.8's paragraph opens *"The system must separate roles
that happen to contain the same entity type."* and names this domain's instance directly: *"A
finance document may mention an account holder and an issuing bank. The agent should model these
as distinct facets"*. `canonical_fields.json` seeds the issuing side (`institution`) and seeds no
counterpart at all.

Why no existing key works:

| Candidate | Why it fails |
|---|---|
| `institution` | it *is* the other half of the split; using it for both collapses the thing `00` says to preserve, and lets a person's name be read as a record issuer |
| `authored_by` | who produced the file. A bank authors the statement; the holder does not |
| `our_firm` | the holder's own organization **on an engagement**. An individual's savings account is not an engagement |
| `client` | an engagement counterparty, the target side of the `our_firm` split |
| `people` | seeded for people appearing in a **capture**, with a photos-scoped `00_cite` |

Recorded with `destination_eligible: false` and used as a search/privacy field only — a safety
domain has to know *whose* record this is in order to protect it and to keep another household
member's statement out of a group, and `00` forbids the folder use directly: *"It should avoid
using authorship or creator identity as a destination dimension."* The `role_split` edge that
binds `account_holder` to `institution` lives in `canonical_fields.json`, which is R1a/R1c's file,
not this node's — so the pairing is recorded in `proposed_fields.role_split_with` and left
unauthored. The open question on the node is the same fork stated honestly rather than resolved.

No other field was proposed. `purpose` was considered and rejected: PR-1 keeps it exactly where
`00`'s sentence puts it (College applications), and a per-domain `purpose` clone is the named
anti-pattern. A `currency` or `amount` field was considered and rejected: an amount is content,
not an organization language, and it would be a giant-form move on a safety domain.

## Template — why `tax_year` is not in the default order

Recommended: `institution → account_type → record_type`, `time_first: false`.

`tax_year` is destination-eligible on the canonical row and is deliberately **absent** from this
schema's default order, on `00`'s own rule: *"For document and record domains, project, function,
or subject usually comes before time because putting year first scatters related work across
calendar folders."* Year-first is honest for **tax filings**, which is a separate organizational
situation on this same schema (`finance.tax-filings` on the roster) — that is precisely what
licenses that template row rather than folding it in here. `account_holder` is never a dimension.

Depth was kept shallow on purpose. The dispatch rule for a safety launch is *small schema +
protect; do not design a deep filing tree that would leak*, and `00` shows Finance to the user as
a protected area with filenames hidden by default. Three levels, with `00`'s uneven-depth licence
meaning a single-institution branch can stay flat. CONNECTION-EXAMPLES fixture 8's insurance
templates use the shallower `institution → record_type`; this default adds `account_type` because
one institution routinely runs several accounts for the same person and a single Statements
folder would mix them — which is a difference from the fixture's *templates*, not a contradiction
of it.

## Neighbours considered that did NOT get an edge

- **`college_applications`** — no `collides_with`. An application-fee receipt and an admissions
  packet share a university name, but the discriminating evidence is already carried by the
  `academic`/`college_applications` role split and by this row's own never-alone rule on a bare
  organization name. It **did** get a `role_split` entry (`institution` vs `target_university`),
  because the finance issuer is a genuine third role on the same entity type and folding it into
  either existing key would be the silent vocabulary collapse.
- **`career`, as `also_holds_with`** — deliberately not written. `career.json` states that a pay
  statement "is the finance neighbour's record" and lists `college_applications`, `academic` and
  `legal` in its own `also_holds_with`, not finance. Writing a one-way edge here would create a
  reciprocity failure against a landed neighbour that has explicitly disclaimed the file. The
  `collides_with` edge is the correct and reciprocal one.
- **`medical`, as `collides_with`** — considered and rejected. An explanation of benefits carries
  a provider name that could be read either way, but co-activation is the **desired** outcome for
  two safety domains: it means P7 classification runs on both readings before any model path.
  There is no evidence item that must count for one side only, so the pair carries
  `also_holds_with` alone (CONNECTION-EXAMPLES fixture 8, binding).
- **`identity`** — my first pass wrote `collides_with` only and rejected `also_holds_with` as
  speculative, on the grounds that a statement used as proof of address is a *use*, not a fact the
  file carries. `identity.json` landed mid-task with a stronger case that I accepted and
  reciprocated: a tax filing or a payer-issued tax form carries an institution's labelled
  statement structure **and** a taxpayer or national identification number in its own labelled
  slot — disjoint evidence, both readings correct, and `00` names "identity documents, account
  statements, tax records" in one breath. `1099-INT 2025.pdf` is the fixture and already showed
  masked identification numbers in its observations. Both edges now stand on the pair, which
  CONNECTION invariant 1 licenses because the collision entry names discriminating evidence.
- **`research`, `code`** — no plausible shared evidence item. A grant budget spreadsheet was the
  tempting case; it is a `project`-anchored research artifact whose money content is the
  never-alone figure, so no edge.
- **`photos`** — got **both** `collides_with` and `also_holds_with`, which CONNECTION invariant 1
  explicitly licenses provided the collision names discriminating evidence (it does: the OCR
  content, never the EXIF or its absence). `IMG_9931.jpg` is the also-holds fixture and
  `Screenshot 2026-04-02...png` is the collision fixture.
- **`legal`** — same both-edges pattern, for the same licensed reason: a signed loan agreement is
  genuinely both, while a single evidence item (the institution name, the amount) must not count
  twice. legal is a field-less placeholder, so the join carries protection, not fields.

Four residual homes rather than the roster's two. `Receipts and Confirmations` and
`Protected Records` are the must-consider pair. `Independent Records` was added for `00`'s
"standalone certificates, notices, confirmations, forms, and PDFs that have a durable purpose but
no broader group" — a one-off utility notice is exactly that. `Unsupported or Encrypted` was
added because password-protected statement PDFs are the single most common unreadable file in
this domain and `eStatement_protected.pdf` is the fixture for it.

## Things this row deliberately did NOT write

- No numeric threshold, no confidence score, no handling class. Sensitivity is `00`'s phrase and
  nothing more; `min_activation_score` and `min_margin` are injected slots named nowhere here.
- No jurisdiction field and no field named after a tax form (D4). `1099-INT` appears once, as a
  **filename observation**, and the note on that example says the form name resolves to a
  `record_type` **value** from R5's one-jurisdiction catalogue.
- No folder path in any fact. Every example's `must_not_conclude` says so where a path was the
  tempting output.
- No `parent_id`, no `shares_field`, no invented edge. `parent_id` is null and browse-only;
  `shares_field` between finance and any other schema is derived from the canonical references
  and was not authored.
- No context-term list attributed to `00`. `00` states the pattern-plus-context **shape** for
  course codes only; the ten finance terms are in `recognition.proposed_context_terms`, marked
  PROPOSED, and R6 owns the patterns.

## NEEDS-JOSEPH (this node only)

**`account_holder`: mint it, or leave finance with only the issuing half of a role split `00`
requires by name?** `00` says to model the account holder and the issuing bank as distinct
facets; the canonical list has only `institution`. Minting is a decision about the product's
shared vocabulary rather than one schema's, and it has two sub-parts Joseph should see:

1. It is a **person-name field on a safety domain**. It must be destination-ineligible and
   privacy-scoped, or it becomes exactly the "collection point for everything produced by the
   same person" that `00` forbids.
2. **Joint and household accounts are unsettled.** Does one record carry one holder fact or
   several? A spouse's statement in a shared Downloads folder is the case that decides whether
   the field protects a person or merely labels a document.

Until answered, `finance.json` references the key and lists it in `proposed_fields`, so the
question is visible in the catalogue rather than silently closed in either direction.

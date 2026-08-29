# finance.subscriptions-utilities — lab notes (R1b)

Roster row: `kind: template`, `schema_id: finance`, `launch: placeholder`, `provenance: inference`.
Verdict: **node accepted** (`refuse_node: false`).

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. It is the authority for the
  observation/fact split, the four Finance keys, safety-before-model posture, template semantics,
  residual names, privacy rules and abstention behavior. Curly double quotes in the JSON are
  reserved for verbatim spans from this file and were mechanically matched after authoring.
- `planning/01-product-design-structured.md` — only the relevant renderings: facts and domain
  schemas (§3), tree/template design (§5), the residual library (§7.3), and privacy (§8.4). It was
  used as a locator; `00` wins.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`,
  `planning/domains/CONNECTION.md`, and `planning/domains/CONNECTION-EXAMPLES.md` — node test,
  schema/template distinction, closed edges, activation/grouping firewall, browse-only parent,
  and the Finance/Legal/Photos co-activation rules.
- `planning/domains/roster.json`, `planning/domains/canonical_fields.json`, and
  `src/evidence_shape/vocabulary.py` — exact assignment, target ids, canonical key roles,
  destination eligibility, and `SOURCE_TYPES`.
- Landed nodes read but not changed: `finance.json`, `finance.personal-records.json`,
  `finance.receipts-expenses.json`, `finance.insurance-personal.json`,
  `finance.loans-mortgage.json`, and `legal.json`. The first two Finance templates already had
  collision edges toward this row; this node reciprocates them. `finance.household-property`
  landed during verification with a concrete property-lifecycle-versus-metered-service edge, so
  this node reciprocates that edge too.
- `planning/overnight/council/DECISION-BRIEF.md` — D6 keeps `snake_case`; D2 keeps sensitivity
  authority in P7's `(file_id, content_hash)` classification rather than in this catalogue; J-IND
  reinforces honest placeholder depth plus gist-level research rather than field inflation.

Primary domain sources were used to test whether the invented fixtures resemble real issued
records. They do not override the product design, and none of their wording is attributed to
`00`:

- [PG&E — Understand Your Bill](https://www.pge.com/en/account/billing-and-assistance/understand-your-bill.html)
  documents a real energy statement's account number, statement and due dates, service location,
  billing dates, service-agreement identifier, rate plan, usage and charge summary. This supports
  the utility-statement fixture and the distinction between a service identifier and the provider's
  own account number.
- [Verizon — Home bill overview](https://www.verizon.com/support/residential/account/understand-bill/overview)
  separates current and previous-period charges, balance due, recurring bundle charges and
  one-time activity. This supports the telecom fixture and the rule that one-time line items inside
  a recurring bill do not each become subscription accounts.
- [Apple Support — Purchases and subscriptions](https://support.apple.com/en-gb/guide/iphone/iph4e3e7324f/26/ios/26)
  confirms that renewal receipts can arrive by email and that subscription history has order-level
  records. This supports the renewal-receipt email fixture without turning every Apple receipt into
  a recurring record.
- [Google Play Help — Cancel, pause, or change a subscription](https://support.google.com/googleplay/answer/7018481?hl=EN)
  distinguishes billing cycles, next-renewal dates, paid-through access after cancellation, plan
  changes and email receipts. This supports the lifecycle signals and the cancellation fixture.

## Committed history and what survived it

`git blame` ties this roster row to commit `13bff36`: one template on the Finance schema, with the
hint `institution` then `record_type`, Legal as the required neighbour, and Receipts and
Confirmations plus Independent Records as required residuals. The row follows that shape exactly.

The superseded catalogue entry `admin.subscriptions-recurring` came from commit `15d2b3d` and was
later spelling-normalized in commit `1082384`. It was the old failure mode: a private schema with
`vendor`, `service_or_plan`, `billing_period`, `renewal_date`, `subscription_identifier`,
`payment_method`, and `subscription_status`. I used its concrete lifecycle vocabulary as a harvest
of plausible files and collisions only. I did **not** carry its schema forward:

- `vendor` is the Finance field `institution` in the issuing-provider role.
- `service_or_plan` is a value of `account_type`, not a key.
- renewal, cancellation, invoice and usage-summary states are values of `record_type`.
- masked payment methods and account/subscription identifiers remain sensitive observations for
  now; one template does not get to add a private identifier vocabulary.
- `renewal_date` remains an evidence and review signal. This product is organizing files, not
  silently becoming a subscription-management database.
- the real cross-record gap is the **covered interval**, not a private subscription-only period.
  That is why the one proposal is the broader `record_period` rather than `billing_period`.

## Node test — why this is not Finance's default template

The row differs from `finance.json` on the two load-bearing limbs and does not manufacture a
privacy difference:

- **Detection differs.** The Finance schema's default is a union over statements, receipts,
  ledgers, tax records and other account records. This template requires a standing paid-service
  relationship: service/account plus covered period or usage for utilities; plan/subscription plus
  renewal, paid-through, cancellation or next-billing state for subscriptions. Those signals also
  discriminate the row from its same-schema siblings.
- **Recommended dimensions differ.** Finance defaults to
  `institution → account_type → record_type`. This row follows the committed roster hint and drops
  `account_type` from the default, recommending `institution → record_type`. Bundled provider bills
  may carry several service types; single-service providers make the level one-child. It remains an
  optional user-added level when labelled values materially split a provider's accounts.
- **Privacy is inherited honestly.** This is still a Finance safety situation. Utility and telecom
  statements expose account, address and usage data; subscription receipts may be milder, but the
  catalogue does not assign P7's handling class or override D2. `launch: placeholder` also means
  safety activation does not unlock this deeper template automatically.

The result is useful even if `record_period` is rejected: the row still has distinct recognition,
the committed dimension order, collision fixtures and safe fallthroughs.

## Bottom-up file coverage

The JSON carries thirteen concrete fixtures:

- utility statement with labelled account, service period, usage and amount;
- photographed water bill with both Finance and Photos evidence;
- telecom bundle bill that separates recurring and one-time charges;
- subscription-renewal email receipt;
- cancellation email with paid-through access;
- signed service agreement that is also Legal;
- sparse usage CSV that may join a group without copying its institution;
- mixed archive manifest inspected without unpacking;
- provider-app screenshot recovered through OCR and also held by Photos;
- bank statement whose recurring merchant row must **not** activate this template;
- one-time purchase receipt from a vendor that also sells subscriptions;
- user-created recurring calendar reminder that is not a provider record; and
- encrypted bill-shaped PDF whose filename cannot establish purpose.

Together they cover labelled form versus prose, photograph and screenshot/OCR, spreadsheet,
archive, email and calendar, a same-schema collision, a cross-schema file, sparse grouping without
fact propagation, and unsupported/encrypted fallthrough.

## proposed_fields

One proposal: `record_period` (`string`, direct only from an explicit labelled interval,
destination-ineligible).

Why it is real: the covered interval is the discriminating observation on utility, telecom and
statement series and is the natural join between a bill and its usage export. No existing key has
that role. `creation_date` is a file-version timestamp; `tax_year` is a tax role; academic `term`
and admissions `application_cycle` cannot be reused. Keeping it destination-ineligible prevents a
folder per month or billing cycle.

Why it is not silently minted: `finance.personal-records` already records the adjacent period-year
tension, so the gap is shared-vocabulary work for R1c/Joseph. A broader name may still be too broad;
R1c may decide periods should remain observations. No `dimension_order`, field row or activation
outcome depends on adoption.

## Edges and reciprocity

- `finance.personal-records` — reciprocal now. A service account period/usage structure is not a
  bank or card account's period/balance structure, and a merchant row never becomes this template's
  issuer.
- `finance.receipts-expenses` — reciprocal now. Standing-account lifecycle evidence separates a
  renewal from a one-time order; a bare seller and charge do not.
- `legal.leases-agreements` — required Legal neighbour made concrete. Party recitals, obligations
  and execution identify the agreement reading; an account/service period and usage or bill state
  identify the running-account reading. A signed ISP agreement may carry both schemas on disjoint
  evidence.
- `finance.hoa-residents-association` — prevents recurring property assessments from being absorbed
  as utilities merely because they repeat and show an address.
- `finance.household-property` — reciprocal now. A service address, account reference and amount
  can occur on either side; metered-service and billing-cycle structure points here, while title,
  ownership, inspection, improvement, permit or warranty structure points to household property.
- `finance.insurance-personal` — prevents premium renewal language from being mistaken for an
  ordinary subscription lifecycle.

`also_holds_with` is empty because CONNECTION restricts it to schema↔schema. The real co-activations
are carried by `finance.json` and surfaced per fixture through `also_schema` (`photos`, `legal`).
`role_split` is empty because that edge lives between canonical field keys; the provider/customer
split is already represented by `institution` and the Finance schema's proposed `account_holder`.

## Neighbours considered that did not get an edge

- **`finance`** — `schema_id`/`uses_schema` is the join. A template cannot collide with its schema.
- **`legal`** — same reason for no direct edge: collision edges are same-kind. The specific
  `legal.leases-agreements` template gets the evidence-backed edge instead; Finance↔Legal
  co-activation already exists at schema level.
- **`photos.screenshot-captures` and `photos.scanned-documents`** — no collision. A screenshot or
  photo of a bill legitimately carries Photos and Finance evidence at once; capture evidence and
  OCR content are disjoint. Treating that as mutex would erase the CONNECTION worked join.
- **`finance.small-business-bookkeeping`** — a business utility bill may join a bookkeeping group,
  but that is P9 context and later template choice, not same-evidence confusion. The bill remains a
  recurring-service record; the bookkeeping packet does not write facts onto it.
- **`career.credentials-licenses`** — both can say renewal, but a credential's issuer, registry and
  validity structure is distinct. A fee-only receipt routes through `finance.receipts-expenses`,
  which already carries the transactional boundary.
- **Contacts (`.vcf`)** — rejected as both a fixture and file kind. Provider contact data is not a
  recurring financial record and `00` keeps contact data privacy-protected rather than using it as
  a folder-proposal basis.

## Other files considered and rejected

- newsletter unsubscribe messages and free content subscriptions — no paid standing account;
- generic terms-of-service or privacy-policy PDFs — no evidence the holder accepted them or has an
  account; boilerplate language alone activates neither this template nor Legal;
- price-comparison screenshots and trial offer pages — solicitations, not records of an existing
  service;
- a card statement full of monthly merchants — kept only as the negative collision fixture;
- one-time purchase and delivery emails — represented by the Adobe negative fixture and the
  Receipts and Confirmations residual;
- provider contact cards and payment-due calendar events — source types, not domains.

## Contract tension and NEEDS-JOSEPH

The dispatch skeleton makes `also_holds_with` and `role_split` look available on every node;
CONNECTION narrows them to schema↔schema and canonical-field edges respectively. CONNECTION wins,
so both arrays are empty here and the research notes say why.

- **NJ-fin-subutil-1 · Does `record_period` become a canonical field?** Adopt one shared,
  destination-ineligible key for labelled billing/statement/coverage intervals, or retain those
  intervals as raw evidence only. The template remains complete either way; the answer controls
  whether P9 can share a validated period fact across recurring-record families.

No other blocker remains for this row.

# R1b lab notes — `finance.vehicle-records`

Date: 2026-08-22  
Assignment: `kind: template` · `schema_id: finance` · `launch: placeholder`  
Result: **keep the node** (`refuse_node: false`).

## Node test

This is not the Finance schema's default template under another label. Its file-level recognition is vehicle-specific: official ownership/registration blocks, repeated labelled vehicle identity, repair orders with odometer and itemized-work structure, recall owner letters, inspection reports, and transfer/lien records. Its useful organization unit is one vehicle across issuers and record roles, not one account at one institution. Its privacy boundary is also sharper than the Finance default because titles and registrations concentrate owner identity, address, legal-interest and vehicle-identifier data.

The node therefore passes on all three permitted differences:

- detection signals differ from the Finance default;
- the honest current order is `record_type` only inside an accepted one-vehicle group, rather than `institution → account_type → record_type`;
- its records repeatedly cross the legal, identity, loan and insurance seams and require redacted/local treatment.

The row remains a **template**. It does not recreate the pre-R0 `pers.vehicle` or `fleet.vehicle` private schemas, does not copy the Finance field list, and does not turn title, registration, service, insurance or inspection into child nodes. Those are `record_type` values.

## Authority and repository sources read

- `planning/00-database-agent-product-design.md` — read in full; authoritative.
- `README.md` — product goals and standing constraints.
- `planning/01-product-design-structured.md` — only the relevant Finance/schema, template, residual and privacy sections; `00` wins.
- `planning/prompts/ALIGNMENT.md`.
- `planning/domains/_CONTRACT.md`.
- `planning/domains/CONNECTION.md` and all eight fixtures in `CONNECTION-EXAMPLES.md`.
- `planning/26-research-dispatch-state.md` and `planning/domains/dispatch/r1b-swarm.workflow.js`.
- the stamped output of `python3 planning/domains/dispatch/make_prompt.py finance.vehicle-records`.
- `planning/overnight/council/DECISION-BRIEF.md`: the ratified D6, D2 and J-IND rulings. Consequences here: snake_case; no handling class in a catalogue row; placeholder/gist research is valid coverage and must not invent a field-bearing professional schema.
- `planning/domains/roster.json`, `canonical_fields.json`, and `src/evidence_shape/vocabulary.py`.
- committed landed nodes: `finance`, `finance.personal-records`, `finance.receipts-expenses`, `finance.insurance-personal`, `finance.insurance-corporate` (partial/untrusted beyond its committed edge), `finance.investment-brokerage`, `finance.loans-mortgage`, `identity`, and `legal`.
- committed pre-R0 history: `pers.vehicle` proposed `vehicle`; `fleet.vehicle` proposed `vehicle_identifier`. Both old rows were superseded as schemas, but their disagreement is useful evidence for R1c's field-clustering decision and must not be silently erased.

## External evidence used

These are authoritative U.S. examples used to verify recurring **document structures**, not to make the node U.S.-only. The JSON deliberately encodes no state form number, filing deadline, VIN-length rule, inspection interval, retention period, regex or jurisdiction-specific threshold.

- [California DMV — Title Transfers and Changes](https://www.dmv.ca.gov/portal/vehicle-registration/titles/title-transfers-and-changes/) confirms the recurring packet: title, ownership transfer, lienholder release, bill of sale, vehicle verification and replacement/transfer records. It also confirms that title and lien interests are distinct roles.
- [California DMV — Lien Satisfied/Title Holder Release](https://www.dmv.ca.gov/portal/uploads/2020/06/reg166.pdf) supplies a concrete labelled form: plate, make, model year, vehicle identification, registered owner, lienholder/titleholder and signature sections.
- [California DMV — Notice of Transfer and Release of Liability](https://www.dmv.ca.gov/portal/vehicle-registration/titles/title-transfers-and-changes/notice-of-transfer-and-release-of-liability-nrl/) confirms a real retained confirmation and the transfer record's vehicle description, owner, odometer and sale-date roles.
- [FTC — Used Car Buyers Guide](https://search.ftc.gov/system/files/documents/plain-language/pdf-0083-buyers-guide.pdf) supplies a concrete purchase/warranty artifact with make, model, year, VIN and warranty/service-contract sections.
- [FTC — Buying a Used Car From a Dealer](https://consumer.ftc.gov/articles/buying-used-car-dealer) confirms that buyers retain the Buyers Guide, warranty documents, inspection report and written transaction terms; it also distinguishes a mechanical inspection from generic shopping material.
- [FTC — Auto Repair Basics](https://consumer.ftc.gov/articles/0211-auto-repair-basics) confirms the completed repair-order shape: each repair, parts and costs, labor, and odometer observations at intake/completion.
- [California Bureau of Automotive Repair — Write It Right](https://www.bar.ca.gov/wir) confirms estimate, work-order, customer authorization, odometer and itemized final-invoice records, including electronic email/text authorization as part of the same repair transaction.
- [FTC — Auto Warranties and Auto Service Contracts](https://consumer.ftc.gov/articles/auto-warranties-and-auto-service-contracts) confirms that owners keep maintenance/repair records and receipts for warranty support and distinguishes a service contract from a warranty.
- [NAIC — Consumer Auto](https://content.naic.org/consumer/auto-insurance.htm) confirms the declarations-page structure: policy number/term, insured, coverages, covered vehicles and loss payee.
- [NHTSA — Check for Recalls](https://www.nhtsa.gov/recalls) confirms that VIN/plate search is vehicle-specific while year/make/model produces general results; completed repairs are not shown by the open-recall search, which is why notice and completion are separate record types.
- [FTC — Used Cars](https://consumer.ftc.gov/features/feature-0040-used-cars) confirms the vehicle-history-report artifact and that it may include ownership, loss/salvage, accident and repair history without itself being an official title.

## Bottom-up file set

The JSON carries the full observation/fact split for these files. The table records why each belongs in the test set.

| Concrete file | Why it matters |
|---|---|
| `Certificate of Title - 2021 Corolla.pdf` | labelled title, owner, lienholder and vehicle blocks; legal and identity-loaded |
| `Vehicle Registration Renewal 2026.pdf` | registration period is not `tax_year`; owner/address privacy |
| `Bill of Sale - Corolla.pdf` | private seller is not `institution`; signed/draft distinction |
| `Retail Installment Contract - Corolla.pdf` | exact collision with `finance.loans-mortgage`; also legal |
| `Lien Satisfaction - Corolla.pdf` | title/loan seam; release date is not tax year |
| `Auto Insurance Declarations - Corolla.pdf` | exact collision with `finance.insurance-personal`; covered-vehicle block does not decide the template |
| `Repair Order 004812 - 48000mi.pdf` | labelled vehicle + odometer + work/parts/labor structure |
| `oil-change-receipt.jpg` | OCR of the same repair situation; capture and finance can co-activate |
| `Annual Safety Inspection Report.pdf` | structured regulatory/service record; no invented due date |
| `Safety Recall Owner Letter 23V123.pdf` | specific VIN + campaign + remedy; notice does not prove completion |
| `Vehicle Maintenance Log.xlsx` | labelled service-history spreadsheet; planned rows must not become completed work |
| `Your Service Is Complete - Corolla.eml` | native mail slots + attached invoice; separates completion from reminders/promotions |
| `service-appointment.ics` | calendar source type and a tempting nickname; group clue only |
| `Vehicle Records Export.zip` | mixed archive manifest; conflicting member VINs must split/abstain |
| `IMG_4912.jpg` | sparse dashboard photo; group membership without copied vehicle fact |
| `2021 Corolla Owner Manual.pdf` | generic reference false positive; make/model/year alone is insufficient |
| `Driver License.jpg` | identity collision fixture; person credential is not a vehicle record |
| `Vehicle History Report - VIN ending 1234.pdf` | useful record, but not ownership/title proof |
| `Commercial Auto Policy Fleet Schedule.pdf` | small-team/fleet case; multiple vehicles must not collapse to one group |
| `dealer-service-history.bin` | unsupported proprietary export; filename cannot rescue unreadable content |

The set covers native text, OCR, a photographed document, a native image, email-capable repair authorization in the recognition rules, calendar, archive and an opaque/locked fallback. It includes labelled forms, unlabelled/handwritten candidates, a screenshot/OCR path, a mixed archive, a collision file, multi-schema files, sparse context-only members and files that must remain outside the node.

## Facets against the Finance schema

### `institution`

Legal when a record identifies an issuing authority, lender, insurer, dealer, report provider, inspection station or repair provider in a labelled issuer/provider role. A private seller, registered owner, driver or customer is not `institution`. A manufacturer named in generic manual metadata is authorship evidence only.

### `account_type`

Legal for the account-bearing subset: auto loan, auto lease account, auto-insurance policy or service-contract account when the record labels that role. It is not a vehicle identifier, registration class, trim, ownership type or service category. Most title, registration, inspection and repair files leave it unknown.

### `tax_year`

Usually unknown. Model year, registration year, policy period, inspection date, service date, recall date and sale date are not tax-year facts. A vehicle-related tax/duty record may fill `tax_year` only from its own labelled tax-year slot under the Finance schema's existing narrow rule. This template adds no date field and invents no fuzzy parsing.

### `record_type`

The strongest existing field and the only honest current destination level. Values include title, registration, bill of sale, loan agreement, lien release, declarations page, repair order, service invoice, inspection report, recall notice and vehicle-history report. These are values, not nodes.

### Existing `account_holder` proposal

The landed Finance schema already proposes `account_holder`. This node does not duplicate it. A borrower or named insured may eventually fill it when directly labelled, but a registered owner, legal owner, lessee, driver and service customer are not automatically the same role. Expanding `account_holder` to mean every person named on a vehicle record would collapse the role discipline the product requires.

## Proposed field — `vehicle`

One proposal is necessary for genuine organization usefulness:

```text
vehicle  string  destination-eligible (proposed)
```

It means the evidence-backed vehicle entity, not one raw identifier scheme. A labelled VIN/chassis identifier is the strongest cross-record observation; a plate, year/make/model and user-confirmed nickname can support resolution/display. A full identifier does not need to become a folder name. This lets one value join a title issued by an authority, a policy issued by an insurer and a repair order issued by a garage without misusing `institution`, `account_type`, `project` or `event`.

Why `vehicle`, not `vehicle_identifier`:

- the committed pre-R0 personal row already used `vehicle` for the asset and the fleet row used `vehicle_identifier` for an identifier slot;
- a vehicle can have several identifier observations and a user-facing alias, while a field named `vehicle_identifier` invites VIN, plate and fleet nickname into one undifferentiated string;
- the destination dimension is the asset a person recognizes, not necessarily the raw VIN;
- raw VIN/plate stays in local evidence and can be redacted in summaries.

Why no other fields were proposed:

- `service_date`, `odometer_reading`, `next_due_date`, `registered_owner` and `repair_item` are all useful search/history candidates, but landing them from one template would expand the shared Finance schema before R1c has evidence across nodes.
- None is required for this placeholder's minimum useful tree. An accepted one-vehicle group plus `record_type` is usable; `vehicle` is the only missing field that determines whether multiple vehicles can remain coherent.
- Odometer, service date and due date remain observations; no due date is computed from a jurisdiction-specific interval.

R1c should cluster this with any asset/entity proposals from household-property, fleet, equipment or maintenance research. It should not mechanically fold `vehicle` into a generic `asset` unless the role and value resolver remain intelligible across those worlds.

## Recognition boundary

The common deterministic shape is **labelled vehicle identity plus a real record structure**:

- ownership/registration roles;
- repair-order/work-order/invoice roles;
- purchase/transfer/signature roles;
- loan/lien/payoff roles;
- policy/coverage roles;
- recall/campaign/remedy roles.

The identifier, organization, amount, date, file format and vehicle vocabulary are all never-alone signals. A generic manual, brochure, listing, public recall result, car photograph, calendar appointment or dashboard odometer image may be retrieved toward an accepted vehicle group but does not write `vehicle` or `record_type` by itself. The sparse image and calendar examples deliberately use `group_without_copying_facts: true`.

The proposed context terms are provenance `proposal`; no source is misrepresented as if `00` listed them. No jurisdiction-specific form vocabulary or detector regex was invented.

## Template decision

Current order:

```text
accepted one-vehicle group → record_type
```

Only `record_type` is serialized because templates may branch only on fields their schema declares. `institution` first would split one vehicle across authority/lender/insurer/dealer/garage. `account_type` applies to only a subset. `tax_year` is almost always the wrong date concept. The group label supplies vehicle context without writing a vehicle fact onto sparse members.

If R1c accepts `vehicle`, the recommended order becomes:

```text
vehicle → record_type
```

Time remains last or metadata-only. The user may flatten the record-type level when it creates no useful split. No path is stored as a fact.

## Edges authored

- `finance.insurance-personal` — reciprocal to the committed edge; declarations/coverage structure vs service/ownership structure.
- `finance.insurance-corporate` — reciprocal to its committed partial edge; one fleet policy schedule vs one vehicle lifecycle.
- `finance.loans-mortgage` — reciprocal to the committed edge; loan/payment/payoff structure vs title/registration/service structure.
- `legal.leases-agreements` — same-kind template collision for signed purchase/lease/service agreements; the file may still join both accepted groups.
- `identity.core-documents` — same-kind template collision for government-issued person credentials vs government-issued vehicle title/registration cards.

At verification time, the first three edges were already reciprocal in their landed node files. The `legal.leases-agreements` and `identity.core-documents` ids are roster-valid template rows, but their R1b node files had not landed, so these two are recorded as outward discovery obligations rather than described as reciprocal. R1c must require the counterpart edge or remove the pair after cross-node evidence review.

No direct edge was written to schema ids `legal` or `identity`: CONNECTION requires `collides_with` to join same-kind rows and `also_holds_with` to join schemas only. The co-activation mechanism already lives on the Finance schema's committed `legal`/`identity` edges. This template's `also_holds_with` therefore stays empty.

## Neighbours considered but not edged

- **`finance.receipts-expenses`** — a service invoice can belong to both accepted groups. Merchant + amount is not a vehicle signal after the never-alone rule, so this row did not add a one-way collision merely for topical overlap. R1c may revisit if the receipt node reciprocates a sharper evidence-item collision.
- **`photos.scanned-documents` / `photos.screenshot-captures`** — the file can carry both Finance and Photos schemas. That is schema co-activation and the committed Finance↔Photos relationship, not a reason to force a template collision for every captured vehicle record.
- **`finance.personal-records`** — generic account statements are separated by the same never-alone discipline; vehicle records need a vehicle-specific block or lifecycle structure. An auto-loan statement is handled by the loans collision.
- **`finance.household-property`** — both concern owned assets, but property address/title structures and vehicle identifier/registration/service structures do not share a sufficiently tempting evidence item once identifier context is required.
- **`legal.personal-legal-matters`** — a dispute over a vehicle may join that group, but ordinary title/service records are not court or dispute files. `legal.leases-agreements` is the sharper template neighbor.
- **`identity.core-documents` contact ownership** — the roster says that row owns VCF evidence, but a contact card for a garage is neither a vehicle record nor a vehicle fact; no `contacts` source type was added here.
- **`Independent Records`** is a fallthrough, not a domain collision. The assignment-required residual is present, alongside more protective/specific fallthroughs.

## Files considered and rejected from activation

- generic owner manual or maintenance schedule — reference material unless attached as a context-supported group member;
- dealer brochure, online listing or price quote — make/model/VIN vocabulary can be shopping evidence, not ownership/service proof;
- car photograph with EXIF — Photos evidence; no vehicle fact without labelled content;
- dashboard odometer photograph — useful group evidence, not identity;
- service appointment in ICS — a planned event is not completed service and source type never proves domain;
- driver licence — Identity material about a person, not a vehicle record;
- public recall bulletin keyed only by year/make/model — reference material, unlike a VIN-specific owner notice;
- unreadable `vehicle_docs.zip` — filename alone cannot rescue it; `Unsupported or Encrypted`.

## Provenance and safety

The node and `vehicle` are proposals. No sentence in `00` names vehicle ownership records or a vehicle field. Design authority is used only for general mechanisms: Finance's four-field vocabulary and safety posture, observations/facts separation, bounded/grounded model use, template reversibility, grouping without label copying, residual handling, and privacy.

The JSON assigns only `potentially_sensitive`; it assigns no P7 handling class. The concrete record set justifies caution: owner/address data on title and registration; signatures and legal interest on transfers; account and policy data on loans/insurance; location metadata on images. Finance safety activation protects first, and placeholder launch does not unlock a deep folder proposal.

## NEEDS-JOSEPH / merge tension

1. **Canonical `vehicle` field.** R1c can cluster and recommend it, but accepting it changes the shared organization language. If accepted, should it be destination-eligible with a user-safe display alias while raw VIN/plate remains evidence? This node recommends yes. If rejected, keep the template shallow and group-based; do not repurpose `institution`, `account_type`, `project` or `event`.
2. **No jurisdiction decision is newly opened here.** Which forms, identifier formats, title regimes and inspection systems ship belongs to the existing jurisdiction-pack work. This node remains structural and therefore unblocked.
3. **Registered-owner role is intentionally unresolved.** It is not silently folded into the Finance schema's proposed `account_holder`. If later product use needs owner/keeper/lessee/driver distinctions as facts, that is shared-schema research, not a field minted by this template.

There is no blocker to landing the placeholder node. The only v1 limitation is explicit: without a canonical `vehicle` field, multi-vehicle folder depth must remain group-labelled or flat.

# Research memo — `law_practice.estates-administration`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/law_practice.estates-administration.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, `launch: placeholder`
Salvage: JSON already landed (~45KB, `refuse_node: false`); this memo argues that draft. No row identity invented.

## Result

**Node accepted.** It is not “the probate practice area,” not “files that say estate,” and not a duplicate of the schema’s default matter file. It is accepted because an estates-administration corpus is organised around a **deceased-and-instant** anchor that the schema’s default **client-and-matter** template cannot see: the person the file is about is dead and is never the client; every characteristic asset is valued at one frozen death date rather than over a period; and many of the sharpest artefacts (bank valuation letters, cross-institution schedules) carry **no matter reference and no practitioner–client role pair**. Those three differences land on all three legs of the node test.

## Binding material read

Stamped assignment via `make_prompt.py law_practice.estates-administration`. Authority stack: `00`, ALIGNMENT, CONNECTION / CONNECTION-EXAMPLES, `_CONTRACT`, RESEARCH-BRIEF, DECISION-BRIEF (D1–D6, J-IND), roster, `canonical_fields.json`, SOURCE_TYPES vocabulary. Calibrated depth on `legal.practice-matter-file.research.md` and house idiom on `law_practice.conveyancing.research.md`. Schema default measured against `law_practice.json` (not its memo). Neighbours consulted for edges only: `legal.estate-planning`, `legal.personal-legal-matters`, `finance.personal-records`, `finance.tax-filings`, `law_practice.conveyancing`, plus co-activation partners `legal`, `identity.core-documents`, `finance.investment-brokerage`. External artefact existence only (not imported as rules): HMRC IHT400 family / US Form 706 shape; sealed grants of representation; Gazette-style creditor notices; capital / income / distribution estate accounts.

Controlling design consequences:

- D1 / PR-6 leave `law_practice` fieldless; `fields: []` and `dimension_order: []` are contract, not under-research.
- Templates may propose keys only in `proposed_fields`; this row reuses the existing `subject_of_record` proposal rather than minting `deceased` / `estate_of`.
- `legal` and `finance` are safety domains — “Finance, identity, medical, and legal material should be implemented first as safety domains” — so co-activation never unlocks a deep filing tree.
- Observation ≠ fact; membership never copies anchors onto members; no folder path is a fact.

## The charge — strongest case that this row should not exist

Stated before defending the JSON, as the handoff requires.

1. **Practice-area label / never-alone.** “Probate,” “estates,” “wills and probate,” “trusts and estates” are exactly the struck tokens the schema forbids. The word *estate* is three-way ambiguous (estate agent, real estate, living settlement accounts). If the row’s only claim were vocabulary, it would fail.
2. **Work-type value, not a node.** The schema already lists registry submissions, transaction sets, and file-closure records as `work_types` values. A grant application and an assent look like those values with death as the subject.
3. **Duplicates the schema default.** Practitioner matter file + matter reference + client/fee-earner slots = default. An estates matter would just be another matter.
4. **Duplicates `legal.estate-planning` or `legal.personal-legal-matters`.** Wills, grants, and death certificates are `legal` / identity artefacts; a lay executor’s IHT pack is personal-legal. Strip those and nothing distinct remains.
5. **Duplicates `finance`.** Bank letters, tax accounts, and distribution payments are finance/tax evidence; finance’s protection runs first.
6. **Lifecycle stage.** Pre-grant → grant → collection → distribution → closure is a stage ladder, and rows defined by stages are not nodes.
7. **Time-first photo exception.** The corpus is saturated with one agreeing date (the death date); a naive detector would make that the first dimension.

Charges 1–3 and 6–7 fail on one finding. Charges 4–5 fail on reciprocal fixtures already in the JSON. Both are argued below.

### Why the charge fails — the finding

**The characteristic files of an administration carry a third role the schema default does not have, and many of them fail the default’s two-leg precondition outright.**

The `law_practice` default requires both: (i) an exact matter or file reference repeated across artefacts, and (ii) at least one artefact whose labelled slots separate a practitioner or firm role from a client role. Look at what actually arrives:

- a **date-of-death balance letter** from a bank addressed to “the personal representatives’ solicitors,” stating a balance *as at* a named death date — **no matter reference, no client/practitioner pair on the page**;
- a **cross-institution schedule of assets and liabilities as at date of death** — one row per holding, a single valuation-instant column, a funeral-account liability block — readable through 00’s spreadsheet path (“Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells”);
- a **death-tax account** (IHT400 / Form 706 family) whose schedules are keyed to a death date and have **no tax year**;
- **estate accounts** whose section grammar separates capital, income, and distribution ledgers, opening from the date-of-death total and closing to fractional residue among beneficiaries;
- a **creditor notice** pairing deceased name, last address, death date, claim deadline, and proof of publication;
- a **distribution schedule** with share-of-residue columns, not a finance payment-run shape.

Those structures are not “matter correspondence about probate.” They are a **deceased-and-instant apparatus**. The client is the personal representative (alive, plural, substitutable, sometimes a beneficiary). The subject of the record is the deceased (dead, cannot consent). 00 licenses the separation: “The system must separate roles that happen to contain the same entity type.” That split is definitional here and only occasional on other siblings — which is why the row is not the default with a narrower filename filter.

Charge 6 (stage) fails with the template’s explicit refusal of an administration-stage dimension: stages move as the matter progresses; destinations must not. Charge 7 (time-first) fails because the agreeing date is a **valuation instant**, not a capture time, and 00’s document rule holds: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

## Node test, three legs

**Leg 1 — detection signals differ from the schema’s default.** The default’s two-leg precondition still binds and is not weakened (a lay executor’s rich probate pack still fails it — see collision fixture below). What this row adds is the death-and-authority pair (deceased slot with date of death + personal-representative / grant slot), the date-of-death valuation slot (including letters that fail the default’s matter/role legs), the single-instant asset-and-liability schedule, the no-tax-year death-tax account, the three-ledger estate-account grammar, the creditor-notice structure, the fractional distribution-and-release structure, and the intestacy-entitlement structure. Never-alone tokens are struck in the JSON: the word *estate*, a death certificate alone, a will alone, probate/executor/deceased vocabulary, a deceased person’s ordinary bank statement, a shared surname, a practice-area department name, a merely old date. The deletion test inherited from the schema applies unchanged.

**Leg 2 — recommended dimensions differ.** Schema default prose (held where `dimension_order` must stay empty under PR-6): client (seeded ineligible, relaxable on explicit approval in a multi-client corpus) → matter → document function → period. This row’s prose differs in three ways the JSON already records: (1) the **client level is struck, not seeded-ineligible** — personal representatives are plural and substitutable, so a client branch scatters one estate and files a dead person’s affairs under a living person who is not the subject; (2) the **anchor is subject-of-record (deceased + death date), not matter** — many valuation letters carry no matter reference at all; the allocated file reference remains the safe *display* label precisely because it names nobody; (3) **no period level** — an administration is one bounded episode measured from one instant; a year cut separates the valuation from the distribution it feeds. Function (valuation, tax, collection, creditors, accounts, distribution, closure) follows the estate on 00’s parent rule: "A work type such as Homework 3 is meaningful only after the course is known". Administration stage is refused as a dimension. `time_first: false`. `dimension_order: []` remains contract-compliant emptiness, not a claim of identity with the default.

**Leg 3 — privacy rules differ.** Schema default: existence of a representation is disclosive; third parties cannot consent. This row’s `sensitivity_why` adds three grounds that are not the default’s: (a) **existence is often public** (grant register, Gazette notice) while **contents never are** (who was left out, residue figures, shares) — so publicity cannot relax the posture; (b) the **subject cannot consent and never will**; (c) one file is a deliberate household financial X-ray — 00’s corpus sentence (“can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”) describes the estate folder’s job. Operative rules: no name may become a folder level (deceased, executor, or beneficiary), and unlike the schema default this does not relax on user approval, against "The default posture must therefore be local-first and data-minimizing."; no legal status inferred; share/value figures not summarised out of the file — "A summary such as “11 protected identity records” may be safe to show, while a visible list of passport filenames on a shared screen may not be."; model use only with user choice per "If a model needs text containing sensitive content, the user should see that requirement and choose whether to allow a local model, a cloud model, a redacted prompt, or no model use."

Three legs, three differences. The node stands. `refuse_node: false`.

## Bottom-up file set (why each fixture exists)

Full observations / residuals live in the JSON. Memo records purpose:

1. `Schedule of assets and liabilities as at date of death - Ellis dec'd.xlsx` — flagship single-instant schedule; schema-blind without the death-date column.
2. `Barclays - date of death balance - E Ellis - 14 March 2026.pdf` — valuation letter that fails the default’s matter/role legs; also finance-shaped (`also_schema: finance`); groups without copying facts.
3. `IHT400 and schedules - Ellis dec'd - submitted.pdf` — death-tax account with no tax year (discriminates `finance.tax-filings`).
4. `Grant of Probate - Ellis dec'd - sealed.pdf` — sealed instrument co-activates `legal`; does not displace this row’s apparatus.
5. `Will and codicil - Margaret Ellis - 2019 - office copy.pdf` — shared fixture with `legal.estate-planning`; death neighbourhood decides.
6. `Estate accounts - Ellis dec'd - final for approval.pdf` — three-ledger grammar closing to residue fractions.
7. `Notice to creditors - Gazette - Ellis dec'd.pdf` — creditor-notice structure; Independent Records if isolated.
8. `Distribution schedule and receipts - residuary beneficiaries.xlsx` — fractional-share grammar; shared surname is not a bridge.
9. `RE Interim distribution - Ellis estate - executors' approval.eml` — practitioner/executor role email with exact file reference.
10. `Death certificate - Margaret Ellis.jpg` — identity co-member; never an activator alone.
11. `Photo of jewellery for probate valuation - item 14.jpg` — photos co-member only with matching schedule item; else One-Off Images.
12. `Estate accounts - Ellis Family Settlement - year ended 5 April 2026.pdf` — **collision fixture**: identical three-ledger grammar, period + prior-year + trust deed discriminate living settlement.
13. `Probate application and IHT205 - Mum's estate - my copy.pdf` — **second collision fixture**: every structural signal, no practitioner — `legal.personal-legal-matters`.
14. `Estate papers - scanned by executor.zip` — archive name carries *estate* alone; Unsupported or Encrypted; no purpose from the container name.

Ugly cases covered: labelled forms, unlabelled bank prose, spreadsheet, email, image/OCR, archive without manifest, safety co-activation, and two collision fixtures.

## Files considered and rejected

- **Lifetime will / letter of wishes / lasting power of attorney pack with no death date** — `legal.estate-planning`; instrument alone never activates this row.
- **Deceased person’s ordinary monthly bank / brokerage / pension statements** — finance on institution-and-account structure; death invisible in the statement.
- **Final income-tax return to date of death / administration-period return** — those carry a tax year / period; `finance.tax-filings`, even when they sit in the estate folder.
- **Sale of the deceased’s house (contract, searches, completion statement)** — `law_practice.conveyancing`; assent to a beneficiary (no buyer, no price) stays here; death valuation of the same parcel stays here.
- **Living family settlement / will-trust annual accounts with prior-year comparative** — collision fixture above; first period from death date may also_hold with continuing-trust work (NJ-EA-3).
- **Estate-agent particulars / “estate” marketing PDF** — word alone; never-alone.
- **Practice-area folder “Private Client / Wills & Probate”** — organisation/department name; never-alone.
- **Chattels photograph without schedule item reference** — photos / One-Off Images.
- **Contentious probate claim with tribunal caption** — `legal` on caption/execution; sibling proceeding rows for practitioner-side litigation apparatus.
- **Live practice-management database** — source system, not a file node; bounded export with readable manifest only.
- **Minting `deceased`, `estate_of`, `testator`, `date_of_death`, `grant_ref`** — synonym mint / uncanonical keys; death date deliberately left as evidence pending NJ-EA-2.

## Proposed fields

One reuse, not a mint:

| key | why |
|---|---|
| `subject_of_record` | Already proposed by `clinical_practice` and carried on the schema anchor’s role_split. Canonical `client` cannot hold the deceased: the client is the personal representative. Destination eligibility must stay FALSE (and must not relax on user approval) because a folder named for a dead person writes a bereavement into a machine the surviving family share. R1c adjudicates once across clinical / nonprofit / law_practice. |

No other proposed keys. Date of death is deliberately not minted (NJ-EA-2).

## Edges — same fixture both sides

All edges are objects (no bare strings). Reciprocals owed at R1c where one-way.

| Edge | Neighbour | Shared fixture | Discriminator |
|---|---|---|---|
| `collides_with` | `legal.estate-planning` | `Will and codicil - Margaret Ellis - 2019 - office copy.pdf` | Lifetime planning neighbourhood vs death certificate + grant + DoD schedule |
| `collides_with` | `legal.personal-legal-matters` | `Probate application and IHT205 - Mum's estate - my copy.pdf` | Practitioner–client structure present vs absent |
| `collides_with` | `finance.personal-records` | `Barclays - date of death balance - E Ellis - 14 March 2026.pdf` (+ ordinary statement run) | Valuation-instant + PR addressee / cross-institution schedule vs institution-and-account |
| `collides_with` | `finance.tax-filings` | `IHT400 and schedules` beside final personal return to DoD | No tax year (death-tax account) vs tax_year / period return |
| `collides_with` | `law_practice.conveyancing` | the deceased’s house | Assent / DoD valuation vs sale file to a buyer |
| `also_holds_with` | `legal` | sealed grant + executed will + deed of variation beside valuation/tax/accounts set | Caption/execution vs deceased-and-instant apparatus |
| `also_holds_with` | `identity.core-documents` | death certificate / surrendered passport in the estate file | Identity slots vs membership in administration apparatus |
| `also_holds_with` | `finance.investment-brokerage` | registrar/broker DoD holding valuation | Holding/security structure vs valuation-instant + PR addressee |

**R1c note (not edited here):** handoff §7 prefers `also_holds_with` as schema↔schema. The landed draft points at `identity.core-documents` and `finance.investment-brokerage` (templates). Recommendation: lift those two to `identity` / `finance` schemas or convert the template-level cases to fixture notes under schema co-activation — do not silently rewrite mid-salvage.

**Deliberate non-edges.** `career` (must_consider neighbour) — no same-evidence mutex; consulting SOWs are already the schema’s career seam. `photos` — co-activation via schedule-linked chattels photo, not collision. Sibling `law_practice` rows (matter-correspondence, time-and-billing, conveyancing already edged) are not restated as practice-area collisions. Residuals: Protected Records (principal), Review Later (unresolved date / trust-vs-admin), Independent Records (standalone notices), Receipts and Confirmations (registry fee / Gazette invoice), Unsupported or Encrypted (passworded / unmanifested scans) — each with grepped `00` spans in the JSON.

## Grouping without copied facts

Anchors: deceased-and-instant pair; allocated matter/file reference; grant/registry reference; estate bank account number; schedule item identifier across valuation → tax schedule → distribution row. "It should not form a supported group when there is no valid anchor". Membership writes no deceased, death date, share, value, entitlement, or folder path onto a member. Shared surname is never a bridge (Columbia-shaped role ambiguity).

## Residual routing

Matches assignment residuals: Protected Records first for dead-third-party material; Review Later for unresolved date meaning and the trust/admin accounts seam; Independent Records for standalone notices; Receipts and Confirmations for isolated fee/invoice members; Unsupported or Encrypted for forced-open refusal. Temporary Screenshots / Reading Inbox / One-Off Images appear only as fixture fallthroughs where OCR/photos/public reading apply, not as primary estate residuals.

## Open questions — NEEDS-JOSEPH

- **NJ-EA-1 (lay executor).** Bereaved person administering personally produces every structural signal and fails the practitioner precondition → `legal.personal-legal-matters`, where estate-specific signals are invisible. Alternatives: (a) leave and accept generic recognition for the commonest consumer corpus; (b) let personal-legal adopt these deterministic signals by reference; (c) mint a personal-side sibling under `legal` (this row does **not** propose (c)).
- **NJ-EA-2 (death date as fact vs evidence).** No canonical key; `creation_date` and `tax_year` are wrong by role. If death date stays permanently evidence, the anchor is `subject_of_record` alone and is weaker than assumed.
- **NJ-EA-3 (will trust on death).** First accounting period runs from the death date; administration and continuing trust overlap. Collision fixture cannot resolve whether one family or two.
- **NJ-EA-4 (also_holds_with lift).** Whether identity/finance co-activation should be schema-level only (see edge note above).

## Final recommendation

Keep `law_practice.estates-administration` as a placeholder template: `refuse_node: false`, empty `fields` / `dimension_order`, one reused `proposed_fields` entry (`subject_of_record`), `time_first: false`, `sensitivity: potentially_sensitive`. Recognition rides the deceased-and-instant apparatus under the schema’s practitioner precondition; legal status stays uninferred; grouping uses exact anchors without copied facts; unmatched material routes conservatively through Protected Records and Review Later. Salvage writes this memo only; the landed JSON is kept.

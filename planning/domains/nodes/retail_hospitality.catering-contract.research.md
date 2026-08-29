# Research memo — `retail_hospitality.catering-contract`

**Depth: J-DEPTH**
Date: 2026-08-27
Output: `planning/domains/nodes/retail_hospitality.catering-contract.json`
Roster row: template on the fieldless `retail_hospitality` schema, `parent_id: null`, placeholder launch

## Result

Accept the node. Its distinct job is to recognise a caterer's or banqueting team's **client-facing commercial engagement for one dated function** — proposal, signed function contract, Banqueting Event Order commercial apparatus, occasion-keyed named-guest allergen sheet, final account — and to keep that packet's guest dietary material protected. It does not recreate a hospitality taxonomy, invent fields the schema forbids, or claim the clock-keyed delivery day that `retail_hospitality.event-production` already owns.

## The charge first

The strongest case that this row should **not** exist, stated before any defence:

1. **Work-type value.** The schema's own `work_types` already lists `catering engagement record - proposal, function contract, function sheet, allergen sheet, final account`. CONNECTION §2: work types are values, not nodes. Padding a template to save that value would repeat the 574 failure.
2. **Document lifecycle.** Proposal → contract → sheet → invoice is a lifecycle of document types, not an organisational situation. Document-type words are never-alone.
3. **NJ-RH-3 (schema open question).** The schema anchor itself doubts the row: it may be a duplicate of `bookings-reservations` plus `event-production` plus `business_operations.contract-administration`, with nothing structural left of its own, and survives only if the FUNCTION SHEET plus allergen sheet plus final account chain is shown to be a structure none of the three holds.
4. **Schema already describes the packet.** The schema `needs_llm` line already names a function file carrying a signed proposal, a floor plan image, a run sheet, an allergen grid, a bar stock sheet and a final invoice as a purpose-coherent trading packet. If the default template already holds that packet, a child that only renames it fails the node test.
5. **Sector vocabulary.** Catering / banquet / wedding / function are never-alone hospitality words — the family's own rule against sector labels wearing structure.

If those five cannot be defeated with evidence, the correct outcome is `refuse_node: true`.

## Binding material read

Stamped assignment via `make_prompt.py retail_hospitality.catering-contract`. Read: `RESEARCH-BRIEF.md`; handoff §6–§7; `CONNECTION.md` §2 node test and §5 edge shape; `_CONTRACT.md`; `ALIGNMENT.md`; roster row; **`retail_hospitality.json` only** as the schema anchor (not its memo); calibration on `legal.practice-matter-file.research.md`; greps into sibling JSON for reciprocal edges already authored toward this id (`event-production`, `menu-recipe-costing`); `00` quotations matched with `grep -F` before use. Neighbours considered from the assignment: `business_operations`, `finance`, `logistics`. No neighbour file was edited.

## External artifact research

Used only to establish that the proposed shapes exist in real practice — not to import rules into the node.

- Banqueting Event Order / function sheet practice in hotel and catering operations (commercial face: priced courses, guarantees, client blocks; delivery face: timings and responsibilities).
- UK allergen information duties for non-prepacked food at catered events — supports the *existence* of occasion-keyed guest dietary sheets as ordinary commercial deliverables; does not create a medical claim.
- Standard catering contract clauses (deposit, cancellation, minimum numbers, corkage) as observable instrument structure.

These sources span trade practice and regulatory disclosure shape. The node derives no retention period, food-hygiene outcome, contract validity, or allergy-management finding from them.

## Node-test analysis — defeating the charge

CONNECTION §2: a template exists only if its detection signals, recommended dimensions, **or** privacy rules differ from its schema's default template. One leg is enough. This pass claims all three.

### Leg 1 — detection signals

The schema's default recognition is built on five structures a generic company never files: tender-and-drawer reconciliation; count-against-book; capacity-against-dated-demand; premises-keyed permission; operative-signed daily check diary. **None of those five is this row's activator.**

This row's activator is a sixth shape the schema only gestured at as a purpose-coherent packet and as a work_type value: the **client-facing commercial engagement chain for food service on one occasion**.

| Charge fragment | Defeat |
|---|---|
| Work-type value | The work_type names the documents; the node names the **situation** — selling food service under commercial terms to a client for one dated function. Same move `legal.practice-matter-file` makes for one representation. |
| Document lifecycle | Lifecycle alone fails. What fires is the **pairing**: per-head/package price + occasion + client instrument + (usually) named-guest dietary deliverable + final account against the same engagement reference. |
| Duplicate of bookings | Bookings is capacity-against-dated-demand without the commercial chain. Fixture: `Table reservation - Smith party of 8 - 14 Mar 2026.pdf` — covers, status, dietary note, **no** per-head package, **no** signed function terms. |
| Duplicate of event-production | Event-production is clock-against-responsibility delivery (run sheet, many-suppliers-one-date, load-in/strike). Fixture: `Run sheet - Ashcroft wedding 06.06.26 v4.xlsx` has the clock and WHO column and **none** of the commercial slots. Shared BEO fixture is section-split, not identity. |
| Duplicate of contract-administration | Contract-admin is a **portfolio** register with notice-date and internal-owner columns across many agreements. Fixture: `Contract register - live agreements Q1 2026.xlsx`. One Banqueting row inside a register is not a function engagement packet. |
| Schema already holds the packet | The schema's packet example **mixes** commercial (proposal, invoice) with delivery (run sheet) and stock (bar sheet). Landed siblings already split that mixture: event-production took delivery; menu-recipe-costing took standing allergen grids and deferred occasion-keyed guest sheets **to this id**. The schema gesture is not a finished default template for the commercial chain. |

### Leg 2 — recommended dimensions

Schema default (held as prose): trading unit → trading occasion → operational record function.

This row **inverts the top** and replaces the second level:

1. **Client engagement / occasion first; site presumptively off.** Off-premise catering happens at the client's marquee, office or hired hall — not at the operator's kitchen as a useful root. Rooting at the operator's site creates the one-child branch the validator rejects when it checks that the proposed template does not “create meaningless one-child levels”, exceed practical depth limits, use an author or organization merely as a collector, or produce empty branches — citing the design's full validation sentence rather than a clipped fragment.
2. **Commercial phase below the engagement** — proposal / contracted / function-sheet / account — because a final account is unintelligible above its parent engagement.

Not time-first. “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” The occasion date identifies the engagement; it does not root the tree. “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.” Plated-food photos beside a function sheet are that exception; the sheet is not.

`dimension_order: []` by PR-6 contract; the deviation is real and recorded as prose.

### Leg 3 — privacy rules

Value matches the schema (`potentially_sensitive`); **reason differs in kind**. The schema's ordinary sensitivity argument is bulk guest exports. This row's **ordinary core chain** produces named individuals and health-adjacent dietary requirements as a **commercial deliverable** — the allergen sheet and the function sheet are what the client bought, not incidental export columns. Guest names must never become folder levels. That posture difference affects residual routing (Protected Records more often) even though the serialized sensitivity enum cannot go finer than `potentially_sensitive`.

## Bottom-up file set

The JSON carries full observations. Why each fixture exists:

1. `Catering proposal - Ashcroft wedding 06.06.26.pdf` — priced packages, per-head, covers, client block. Commercial offer without yet proving a signature.
2. `Function contract - Ashcroft wedding - signed.pdf` — two-party instrument, guarantees, deposit, cancellation. Discriminator against contract-admin (no portfolio).
3. `Function sheet - Ashcroft wedding 06.06.26.docx` — **collision fixture** with event-production (schema's own fixture). Commercial slots vs delivery timeline.
4. `Function allergen sheet - Ashcroft wedding 06.06.26.docx` — **collision fixture** with menu-recipe-costing. Named guests + occasion vs standing dish grid.
5. `Final account - Ashcroft wedding 06.06.26.pdf` — engagement-joined invoice; `also_schema: finance` for money slots. “One file may hold facts from more than one domain without losing information.”
6. `RE Ashcroft wedding - menu change and deposit received.eml` — engagement-plus-attachment email signal.
7. `Catering pack - Ashcroft wedding 06.06.26.zip` — purpose-coherent archive; manifest only. “However, the normal scan should never extract archive contents to the filesystem, because doing so creates security, storage, and side-effect risks.”
8. `Screenshot 2026-05-02 - signed function contract.png` — OCR + photos coactivation; filename alone insufficient.
9. `Table reservation - Smith party of 8 - 14 Mar 2026.pdf` — **bookings collision / rejected activator**.
10. `Run sheet - Ashcroft wedding 06.06.26 v4.xlsx` — **event-production false friend**.
11. `Allergen matrix - Spring 2026 menu.xlsx` — **menu-recipe false friend**.
12. `Contract register - live agreements Q1 2026.xlsx` — **contract-admin collision**.
13. `Statement of Work - Acme Market Entry - executed.pdf` — consulting engagement false friend (`career.consulting-client-engagement`).
14. `My wedding catering quote - Garden Kitchen.pdf` — **customer-side** false friend; operator/buyer determination fails.
15. `Invoice 88231.pdf` — schema's lone-transaction residual fixture; Receipts and Confirmations.
16. `Catering contracts 2024-2026 - locked.zip` — unsupported/encrypted; no facts from the name.

## Files considered and rejected

- Standing recipe specs and GP costings → `menu-recipe-costing`.
- Temperature logs, cleaning schedules, batch traceability → `food-safety`.
- Table/room reservation exports without commercial terms → `bookings-reservations` (owed row; roster id used).
- Run sheets, supplier call schedules, on-the-day logs, post-event headcount reconciliations → `event-production`.
- Trade POs and goods-in for the kitchen → `supplier-order`.
- Consignment notes and PODs for hire drops → `logistics`.
- RFP / evaluation matrices awarding catering → `business_operations.procurement-sourcing`.
- Premises licences and TENs → `premises-licensing` / event-production seam (not this row).
- Customer-side quotes and restaurant receipts → Receipts and Confirmations; never this world.
- Live catering CRM / banquet-management databases → source systems, not file nodes; bounded exports with manifests only.
- Practice-area or cuisine taxonomies, per-guest folder trees, numeric covers thresholds → deferred / forbidden.

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `template.dimension_order: []` intentional under PR-6 / D1. No minting of `client`, `function`, `covers`, `package`, `allergen_status`, or similar. Candidates rejected:

- `client` / `counterparty` — canonical engagement keys exist elsewhere; this schema does not declare them; proposing them here would jump R1c's field gate.
- `trading_occasion` / `site` — already proposed on the schema anchor; templates do not re-propose.
- `purpose` — scoped elsewhere in the canonical record.
- Cuisine, package-tier, and covers as fields — values or thresholds, not catalogue keys.

## Edges

Nine `collides_with` objects, each `{"domain","signal"}` with **SAME FIXTURE BOTH SIDES** and a reciprocal must-not-take. `also_holds_with: []` — handoff rule is **schema ↔ schema only**; this is a template. Finance coactivation is recorded on the final-account fixture via `also_schema: finance`, not as a template↔schema also_holds edge.

### Deliberate non-edges

- `retail_hospitality.food-safety` — allergen *topic* overlaps; purpose differs (composition checks vs guest dietary deliverable). Menu-recipe already holds the standing-grid seam; this row does not need a third allergen mutex.
- `retail_hospitality.pos-reporting` — no till/session apparatus in the engagement chain.
- `legal.leases-agreements` / `legal.practice-matter-file` — a function contract is not a premises lease and not a legal-practice matter file; career consulting already covers the signed-engagement false friend.
- `business_operations.vendor-management` — supplier relationship scorecards are not one-function client engagements.
- `creative` — menu design sources stay creative; a priced BEO is commercial apparatus.

## Residual routing

Receipts and Confirmations (lone invoices, customer quotes, deposited booking slips); Protected Records (named-guest allergen sheets and signed personal client details without an accepted group); Review Later (unresolved operator/buyer side); Independent Records (specimen packs); Unsupported or Encrypted (locked archives); Temporary Screenshots (screen-origin captures without established commercial slots).

## NEEDS-JOSEPH

1. **NJ-CC-1** — BEO / function sheet dual ownership with `event-production` (align with NJ-RH-3 and NJ-EP-1). Prefer (a): this row owns the file; event-production groups the timeline without claiming the file.
2. **NJ-CC-2** — large-party restaurant booking with a deposit but no full function contract. Structural discriminator required; no numeric covers threshold.
3. **NJ-CC-3** — off-premise caterer vs in-house banqueting as one situation or two. This pass keeps one; a split would revive the refuse charge for the in-house half.
4. **NJ-CC-4** — final-account money slots always coactivate `finance` vs ever becoming retail_hospitality fields if D1/PR-6 lifts. This pass assumes coactivation and proposes no fields.

## R1c recommendations (do not edit neighbours here)

- Confirm reciprocal signal text with `event-production` and `menu-recipe-costing` (both already authored edges **to** this id).
- When `bookings-reservations` lands, require the same `Table reservation - Smith…` fixture and discriminator.
- Schema NJ-RH-3 can close as **survives**, citing the commercial engagement chain as the structure none of the three neighbours holds alone.

## Final recommendation

Keep `retail_hospitality.catering-contract` as a placeholder template with no fields, no dimensions, no `also_holds_with`, and `refuse_node: false`. Activate on the client-facing commercial engagement chain; leave delivery clocks to event-production, capacity holds to bookings, portfolio registers to contract-administration, standing allergen grids to menu-recipe-costing, and money facts to finance. Route unmatched and customer-side material conservatively.

# Research memo — `retail_hospitality.menu-recipe-costing`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/retail_hospitality.menu-recipe-costing.json`
Roster row: template on the fieldless `retail_hospitality` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accepted.** `refuse_node: false`. `fields: []`, `proposed_fields: []`, `dimension_order: []`, `also_holds_with: []`.

The row survives on one structure and three consequences of it. The structure is a **one-to-many
decomposition with a rollup and a derived margin**: one named finished item exploding into many bought
components, each with a quantity in a physical unit and a unit cost, rolled through a yield or portion
count into a cost per portion, set against a menu selling price. Nothing else in this schema and
nothing in the neighbouring schemas carries it, because every competing artefact — a catalogue line, a
trade price list line, a printed menu line — is **atomic**.

I came close to refusing. The case against was strong enough that most of this memo is spent on it.

## The charge — the strongest case that this row should not exist

I put five accusations to the row, in descending order of how nearly they killed it.

**1. It is a work_type value.** This is the accusation that came closest to succeeding, because the
evidence for it is in the row's own schema. `retail_hospitality.json` lists, verbatim, the work type
`"menu and costing record - recipe specification, ingredient cost build-up, gross-profit calculation,
allergen matrix, printed menu"`. That single string is the whole of this row's roster hint. The schema's
own `never_alone` then convicts it: *"A DOCUMENT-TYPE WORD, standing alone - invoice, rota, log, price
list, order, review. These are values of a function dimension, and a row resting on one is the schema's
default template wearing a name."* A menu is a document type. A recipe is a document type. A costing
sheet is a document type. On the face of it the row is a function-dimension value that has been promoted
to a node — which is precisely the 574's recorded failure.

**Defeated, but only partly and only by structure.** The work-type string names five artefacts, and the
node argument does not rest on any of them being a document type; it rests on two of the five sharing a
structure the other three cannot produce. The specification and the cost build-up decompose; the printed
menu, the price list and (as argued below) most of the allergen material do not. So the correct reading
is that the roster's work type is *wider than the node*, and the node is the decomposing subset. I have
written the row so that the printed menu is explicitly **not** its activating evidence — see the
`product-catalogue` edge — which is the only way this defence is honest rather than convenient.

**2. It is a duplicate of `retail_hospitality.product-catalogue`.** A menu is a catalogue of priced
selling lines; the schema's own catalogue-and-price recognition entry says so in terms, ending *"or a
menu document whose structure is course sections, dish names and prices with a statutory allergen or
calorie footnote."* The schema's `product` key example already includes a dish (`Confit duck leg`). If
the catalogue signal already names menus, this row is the catalogue with a food vocabulary.

**Defeated by the decomposition, and by nothing else.** I tested a second discriminator first —
occasion-freedom — and it failed, which is worth recording. This row *is* the family's only
occasion-free row in the sense that it has no session, count, cycle, booking or function; but
`product-catalogue` is standing too, so occasion-freedom separates this row from the schema default and
**not** from its nearest sibling. The surviving discriminator is that a catalogue line is atomic and a
costing line is not. I have written that limitation into the edge signal rather than letting the
stronger-sounding argument stand unqualified.

**3. It is a lifecycle stage.** "Menu *development*" reads as the design phase of `product-catalogue`:
first you develop a menu, then you publish it. Stages are not nodes.

**Defeated.** The cost model is not a phase that ends at publication — it is re-run every time a supplier
price moves, and its output (a GP percentage per dish) is consulted for as long as the dish is sold. The
row's own version apparatus is the evidence: `supersedes v2`, `re-cost April`. A stage produces a
document once; this produces a version line.

**4. It is a duplicate of `manufacturing`'s bill of materials.** The schema anchor concedes the point at
schema level: *"RECIPE AGAINST BILL OF MATERIALS, and the two are structurally near-identical."* If they
are near-identical, one of them is redundant.

**Defeated by the issued lot, following the anchor.** A BOM terminates in goods that leave the premises
carrying a lot identity the operator issued; a recipe terminates in a portion consumed on site, priced
against a menu. A batch code the operator *receives* is an ingredient attribute; one it *issues* is
manufacturing's. That is a real, checkable difference in the bytes, not a sector label.

**5. The allergen half belongs to `retail_hospitality.food-safety`.** Allergens are a statutory food-safety
duty. Assigning them here looks like the roster hint pasting two unrelated things together.

**Not fully defeated — routed to NJ-MRC-2.** The structural argument works: the grid is a projection of
the component list onto a fixed external attribute set, with one review date for the whole sheet and no
per-row date, no signature and no corrective-action slot, whereas everything in food-safety is a dated,
self-signed diary. But the *duty* discharged is a safety duty, and I do not think the design docs settle
which of structure and duty should decide. I have recorded the alternative openly, including the
consequence that this row's name would have to change if R1c moves the grid.

## The node test, argued in full

**The schema's default template, stated first, because the row is measured against it.** The
`retail_hospitality` schema declares no field rows and no dimensions; its default is held as prose in
`template.why`: *the TRADING UNIT — site, venue or channel — only where the corpus genuinely spans more
than one, then the TRADING OCCASION — the session, count, order cycle, booking, function or licensed
premises the material belongs to, then the OPERATIONAL RECORD FUNCTION.* Not time-first.

**Leg 1 — detection signals differ.** The schema's recognition list already separates the
ingredient-and-yield structure from the catalogue-and-price structure, so the difference is not one I
invented; the row's job is to specialise it. The specialisation is the one-to-many explosion with a
rollup and a derived margin, plus the closed-column ternary grid. Neither appears in the other twelve
sibling hints, and each is stated as a structure paired with labelled slots, which is what the schema's
own never-alone rule demands. The row also adds two signals the schema does not have: a
version-and-effective-date apparatus treated as *positive* evidence (elsewhere in this family a version
family is usually an export artefact), and the requirement that a commercial side be present at all.

**Leg 2 — the recommended shape differs, and this is the leg the row wins most cleanly.** The default's
second level is the trading occasion. **This row has no trading occasion.** A dish specification is not
keyed to a session, a count date, an order cycle or a booking; it is standing until superseded. Filing it
under the default would give every occasion branch nothing in it, which is exactly the defect the
validator sentence names: *"The engine validates that the proposed template does not repeat a parent
dimension, create meaningless one-child levels, exceed practical depth limits, use an author or
organization merely as a collector, expose protected information, or produce empty branches when tested
against the accepted group."* What the row recommends instead is a standing product-line level — the menu,
range or season — between the conditional site level and the record function. The site level is *weaker*
here than elsewhere in the family, because a multi-site operator usually runs one menu across the estate,
so branching by site would produce the one-child level the same sentence forbids. Time stays out of the
top: *"For document and record domains, project, function, or subject usually comes before time because
putting year first scatters related work across calendar folders."* A season is a content period, not a
capture date, and the photos exception is not available to a spreadsheet. `dimension_order` is
nonetheless `[]` by contract (PR-6), so all of this is a recommendation for R1c, not a serialized shape.

**Leg 3 — the privacy rule differs, with the same value for a different reason.** The schema is
`potentially_sensitive` because its everyday output is personal data about members of the public. This
row's everyday output **names no data subject at all** — dishes and ingredients, and at most an internal
reviewer in a labelled slot. What needs protecting is commercial: negotiated supplier unit costs, a
dish-by-dish pricing strategy, and the specification itself. The schema's rule therefore fails in both
directions here. It **under**-protects, because a costing workbook with nobody named in it would not trip
a rule that keys on a data subject. And it **over**-protects, because this row holds the family's only
routinely public artefact — a printed menu is handed to every member of the public who sits down — and
treating that as guest data suppresses a document the operator publishes on purpose. The row proposes a
split on the *cost side*, not on the presence of a person. It keeps the cautious value because the two
halves arrive in the same folder and often the same workbook, and it records the tension as NJ-MRC-3
rather than claiming `none`. The binding constraint is unchanged: *"Privacy policy must be enforced
before content reaches any model or external connector."*

All three legs pass, and the row does not rest on any one of them alone.

## Files considered and rejected

Named because each is a tempting false positive, not because it is obscure.

- **`Spring menu 2026 - print final.pdf`** — the priced, allergen-footnoted menu. Rejected as activating
  evidence and given to `product-catalogue`. It is atomic: no component list, no cost column, no margin.
  This row may hold it as a *member* of a season group and never as its reason.
- **`Recipe card - Sourdough focaccia.jpg`** — a photographed handwritten card with quantities and a
  method and no commercial side. Rejected outright. A quantified ingredient list is a recipe, and a
  recipe is not a trading record. *"Topic answers what a file is about, while purpose answers what the
  file was for."* Cooking is the topic in a cookbook page, a blog draft, a culinary-school exercise and a
  kitchen's live spec; only one of the four has a menu price as its purpose.
- **`Harlow Foods trade price list Mar 2026.xlsx`** — the sheet the unit costs were read *from*. Rejected;
  it is keyed to a supplier account with order codes and pack sizes, and belongs to `supplier-order`.
- **`GP calculator - BLANK template.xlsx`** — every header, every formula, no values, a wholesaler's logo.
  Rejected. Structural completeness is not trading evidence; a blank costing sheet and a live one are the
  same workbook with the numbers removed.
- **`Function allergen sheet - Ashcroft wedding 06.06.26.docx`** — an allergen document keyed to a booked
  occasion and naming two guests. Rejected; `catering-contract`'s.
- **`Menu_Spring2026_v7.indd`** — the design source with linked assets and a proof round. Rejected;
  `creative`'s. Note this row is the *third* party to the spring menu and takes it on neither edge.
- **`Gross profit March 2026.xlsx`** where GP is computed from opening stock plus purchases minus closing
  stock against turnover. Rejected; that is a ledger outcome for a period, not a per-item design
  parameter, and it is `finance`'s.
- **`Kitchen fridge temps March.jpg`** and traceability records carrying received batch codes and use-by
  dates. Rejected despite being about ingredients; dated rows with initials are `food-safety`'s diary.
- **Plated-dish photography.** Rejected as `photos`/`creative` evidence. Inherited from the schema: a
  picture of food is not a record about food.

## The collision fixtures

Two, because the row has two distinct ways of being wrong.

**`Spring menu 2026 - print final.pdf`** is the collision that decides whether the row exists. It looks
exactly like this row's evidence — dishes, prices, an allergen footnote, sitting in the costing folder —
and it is not. **Discriminated by the component explosion**: nothing in it decomposes. If this row were
allowed to take it, the row would be `product-catalogue` with a food vocabulary and should be refused.

**`Recipe card - Sourdough focaccia.jpg`** is the collision that decides what the row is *about*. It is a
recipe, in a kitchen, with quantities — and it is not this row, because there is no cost, no portion
count and no price. **Discriminated by the commercial side.** This fixture matters because it defeats the
lay reading of the row's name: the row is not "recipes", it is the arithmetic that sets a price.

## Reciprocal boundaries

Nine edges are authored, each naming the same fixture on both sides. Summarised here; the full text is in
`collides_with`.

| Neighbour | Same fixture | This row owns | Neighbour owns | Discriminator |
|---|---|---|---|---|
| `retail_hospitality.product-catalogue` | `Spring menu 2026 - print final.pdf` | the cost model | the atomic priced selling line | component explosion |
| `retail_hospitality.food-safety` | `Allergen matrix - Spring 2026 menu.xlsx` | the standing item×attribute grid | the dated self-signed diary | per-row date + signature |
| `retail_hospitality.supplier-order` | `Harlow Foods trade price list Mar 2026.xlsx` | records keyed to a sold item | records keyed to a bought-from account | sold item vs supplier account |
| `retail_hospitality.pos-reporting` | `Menu engineering - March 2026.xlsx` | the cost side | the dated trading-period read | build-up present vs period + site |
| `retail_hospitality.catering-contract` | `Function allergen sheet - Ashcroft…docx` | the grid keyed to a dish set | the sheet keyed to a booked occasion | a guest is named |
| `manufacturing` | `Product build - unit cost and yield.xlsx` | costing a dish for a menu | production for onward sale | the issued lot |
| `creative` | the spring menu, twice | the commercial apparatus | the making | production vs commercial apparatus |
| `finance` | `Gross profit March 2026.xlsx` | GP as a design parameter | GP as a ledger outcome | build-up vs stock movement |
| `business_operations` | `Spring 2026 menu launch - plan v4.pptx` | the arithmetic behind one price | the initiative and the forecast line | decomposition vs schedule |

Every one is stated in both directions in the JSON, including what **this row must not take** — which is
the half that a row arguing for its own existence is most tempted to leave out.

**Deliberate non-edge: `logistics`.** The dispatch named it a must-consider neighbour and I considered it
and refused the edge. A costing sheet contains no consignment, no carrier, no manifest and no movement;
the only path from a recipe to a logistics record runs through the ingredient's purchase, and that path
is already owned by `supplier-order`, which authors the logistics seam itself. Adding a decorative
logistics edge here would record a collision that cannot happen.

**`also_holds_with` is empty.** CONNECTION §5 makes it schema↔schema only and this row is a template, so
it cannot author one. Recorded for R1c: at schema level, `retail_hospitality` genuinely co-holds with
`manufacturing` (a food producer that both manufactures for wholesale and runs a café will hold BOMs and
dish specs in one place, on disjoint evidence) and with `creative` (a season pack carrying design sources
and costing workbooks). The schema anchor already authors the `creative` collision but no co-hold; that is
a gap R1c may want to close.

## Fields and dimensions

`fields: []` — the schema owns the fields and declares none (D1 as narrowed, `_CONTRACT` rules 10 and 15,
PR-6). `proposed_fields: []` — **this row mints nothing and proposes nothing.** Rejected candidates, with
the reason each was not proposed rather than merely omitted:

- `dish`, `menu_item`, `recipe`, `sku` — synonym family for the schema's existing `product` proposal.
  Minting any of them is exactly what the canonical list exists to prevent.
- `menu`, `season`, `range` — the standing product-line level the template argument recommends. This is
  the one place I was genuinely tempted, because the row argues for a level and then supplies no key for
  it. I did not mint, because a template may not mint against a schema that declares nothing, and because
  `record_period` (already proposed twice on `finance` rows and once by this schema) is the wrong shape —
  a season is not a period a record *covers*. The gap is recorded at the end of `open_question` as a
  direct ask to R1c: if the template argument is ratified, the level needs a key.
- `cost`, `selling_price`, `gp_percentage`, `allergen` — these are *values inside* the artefact, not
  organizing dimensions. A branch per GP percentage is absurd; a branch per allergen would be a
  fourteen-way split of the same forty dishes.

`time_first: false`. A season is a content period; the photos exception belongs to capture-based media.

## Role split

One entry, and it is unusual enough to flag: the **same** canonical concept appears **twice in one file in
two roles**. A dish specification names one product *as sold* (the finished item, with a portion count and
a menu price) and eleven products *as bought* (the components, with purchase units and unit costs). This
is 00's facet pattern applied inside a cost model rather than across a counter. Neither facet gets a key
here. The consequence if R1c leaves it unsplit is concrete: an extractor reading component rows would
write eleven `product` values per dish, the dish's own identity would be one value among twelve, and the
dish-life grouping reason this row depends on would lose its join.

## Residual routing

`Independent Records` is the **primary** fallthrough and the reason is structural rather than incidental:
this row's artefacts are standing documents with a durable purpose, so a lone one has no cycle around it
to make a group — *"standalone certificates, notices, confirmations, forms, and PDFs that have a durable
purpose but no broader group."* `Review Later` takes the unresolved: blank templates, unreadable
handwriting, the NJ-MRC-1 workbook. `Receipts and Confirmations` was considered as directed and accepted
**narrowly** — it takes the wholesaler invoice a unit cost was read from, because *"Receipts and
Confirmations may hold isolated invoices, delivery confirmations, booking records, boarding passes,
purchase receipts, event tickets, and similar transactional documents"* — but a priced menu is **not** a
transactional document, since no transaction has occurred, and it routes to Independent Records instead.
That boundary is easy to get wrong and is written into the JSON. `Protected Records` takes the one
personal-data path (a dietary sheet that names individuals); this row reaches it far less often than its
schema does, and that asymmetry is itself part of the node argument.

## NEEDS-JOSEPH

- **NJ-MRC-1 (sharpest) — the menu-engineering workbook.** `Menu engineering - March 2026.xlsx`, carrying
  dish-level GP beside period sales volume, is undecidable between this row and `pos-reporting` on its own
  bytes. *Alternatives:* (a) this row's proposal — the component build-up present in the same workbook
  decides for this row; (b) `pos-reporting` takes every workbook containing a dated sales figure and this
  row keeps only the specifications feeding it. Both rows must say the same thing.
- **NJ-MRC-2 — the allergen grid's home.** Structure says this row (standing projection, no dated rows);
  the statutory duty says `food-safety`. *Alternatives:* keep it here (this pass's reading, following the
  roster hint), or move it and rename this row, since "plus the allergen information the dish carries" is
  a third of the hint.
- **NJ-MRC-3 — is a printed menu `none`?** It is published to the public, and it is the only artefact in
  the family of which that is true. *Alternatives:* keep the cautious family value (this pass's choice);
  give this row `none` and rely on cost-side files activating differently; or let P7 split on the cost
  side directly.
- **NJ-MRC-4 — can `product` carry the sold facet and the bought facet at once?** If not, this row has no
  key for a dish and the schema's own recorded strain about `product` stretching from a SKU to a dish
  becomes acute. See `role_split`.
- **Open, no id — the standing product-line level has no key.** The template argument recommends a menu /
  range / season level and this row deliberately did not mint one. If R1c ratifies the argument it must
  supply the key; `record_period` is the wrong shape for it.

## Recommendations for R1c (cross-row, not applied here)

1. `retail_hospitality.product-catalogue` must author the reciprocal of this row's first edge, in the same
   words: the atomic priced selling line versus the component explosion. If it instead claims menus
   wholesale, this row should be re-examined for refusal.
2. `retail_hospitality.food-safety` should state the allergen boundary explicitly whichever way NJ-MRC-2
   is decided, so the grid is not silently claimed twice or dropped by both.
3. The `retail_hospitality` schema's `work_types` entry "menu and costing record" is **wider than this
   node**. R1c may want to note on the schema that the printed menu inside that string is
   `product-catalogue`'s, so the work-type list is not read as a node list.
4. The schema's `finance` and `logistics` edges are marked authored one-way; this row's `finance` edge is
   too. The reciprocals are still owed on the landed finance rows.

## Self-verification

- `python3 -m json.tool` — parses.
- Top-level key set compared programmatically against `legal.practice-matter-file.json`: identical apart
  from `proposed_context_terms`, which landed templates such as `academic.coursework.json` also carry.
- `collides_with` entry key set is `{domain, provenance, signal}`, matching `identity.core-documents.json`
  and `legal.practice-matter-file.json`; every entry is an object, none is a bare string, and every
  signal names the same fixture on both sides.
- Every neighbour id is on the roster: five `retail_hospitality.*` siblings taken from `roster.json`, and
  four bare schema ids (`manufacturing`, `creative`, `finance`, `business_operations`) of the kind the
  schema anchor itself uses.
- All ten `00` quotations used in the JSON and this memo were grep-verified verbatim with `grep -c -F`
  against `planning/00-database-agent-product-design.md`; each returned exactly 1.
- `fields`, `proposed_fields`, `dimension_order` and `also_holds_with` are all empty; `time_first` is
  false; no threshold, statistic, file count, handling class or regex appears anywhere.
- Files written: only the two assigned. No roster, canonical-field, `src/`, `check.py`, SPEC or
  neighbour-node edit.
- **Not verified:** the row was not run against `check.py` (out of scope for this agent), and the
  `retail_hospitality.*` siblings it authors edges against have not landed, so all five sibling
  reciprocals are owed rather than confirmed.

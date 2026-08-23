# clinical_practice.veterinary-practice — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `clinical_practice.research.md`; all quotations machine-verified verbatim
against `00-database-agent-product-design.md`, every edge id checked against `roster.json`. Landed
siblings read for key set and idiom: the `clinical_practice` schema row and all five landed templates,
plus the two salvaged drafts in this wave. **`ROSTER.md` §5.6 read closely and treated as binding** —
it is the ruling that put this row here at all.

Legacy rows per `ROSTER.md` Appendix A: line 603 `med.veterinary-practice` → this id (ROW); line 604
`med.veterinary-pet-owner` → **DROP·residual**, because "an owner's pet records have no honest schema
… the practice-side situation survives as clinical_practice.veterinary-practice". §5.6 calls that "a
role split, not a reversal". So this row is the **practice face of a split whose other face is
deliberately empty**, which is the single most important fact about it and the reason two of its file
examples exist to be *declined*.

## What it is for, and what it holds

A veterinary surgery's working files. Consultations, estimates and treatment authorisations,
vaccination and preventive records, prescriptions and dispensing, lab and imaging results, surgical
and anaesthetic records, client invoices and accounts, insurance claims, specialist referrals,
health/export/travel certificates, herd and holding health plans and testing records, movement and
identification records, euthanasia and cremation records, practice registration and standards-scheme
material, the controlled-drug register, and client correspondence.

## The fold question — argued both ways, because I was asked to

**The argument for refusal is strong and I want it on the record first.** Every work type above
already has a home: an animal's chart is `patient-chart` with a different subject; the dispensary is
`pharmacy-operations`; specialist referrals are `referral-correspondence`; registration and rotas are
`practice-administration`; the surgeon's own registration is `licensure-credentialing`; complaints and
claims are `malpractice-incident`. On that reading, "veterinary" is the **species of the subject** — a
*value* — and minting a node for a value is the 574 failure exactly. `refuse_node: true` would have
been a defensible, honest outcome.

**I did not refuse, and here is what decided it.** The node test licenses a template whose *detection
signals* or *privacy rules* differ from its schema's default, and **both differ here in ways no
human-side row can express**:

1. **Detection — a tri-party record.** A veterinary file binds practice, **animal patient**, and
   **human client** in two labelled blocks *of different kinds*. It carries species/signalment and
   permanent-identifier slots. And it **fuses the clinical entry with the priced chargeable line in a
   single row** — in human practice those are two systems and two files. No sibling has any of this.
2. **Privacy — inverted.** Everywhere else in this family the protected party is the patient. Here the
   patient is an animal and the protected party is the **client**: a named human whose address,
   spending, aged debt, insurance history, and consent decisions about an animal's life and death are
   in the same file. A rule tuned to find a patient block finds the **wrong block** here. That is a
   difference in kind, not degree.
3. **The food-animal face has no individual patient at all.** Herds, holdings, movement and testing
   records, withdrawal periods — no human-side analogue whatsoever, and fatal to the "it's just a
   species value" reading.
4. **§5.6 already ruled.** Folding this row would leave veterinary practice with *no* face, since the
   owner-side row is refused. That is a bigger change than a template edit.

Recorded as **NJ-CP-17** and argued both ways in the JSON `open_question`, because folding a row is a
roster edit this agent may not make.

Dimensions do **not** differ and could not — `clinical_practice` declares no fields, so every template
on it has an empty `dimension_order` by contract, and **the node test's third leg is unsatisfiable for
every row in this family** (recorded identically in `clinical_practice.patient-chart.research.md`).

## Files considered and rejected

- **`Bella vaccination card.jpg`** — kept as **the holder fixture**, and kept in order to be *declined*.
  In any real personal corpus, an owner photographing their own pet's card is far more likely than a
  practice record, and the owner-side row is refused — so the correct outcome is a residual, not this
  row. A row that could not say this would be dangerous.
- **`IMG_0912.jpg`** — a dog in a garden beside a practice invoice. Kept as the second decline fixture:
  neighbourhood copies nothing.
- **`herd health plan 2026 - holding 12-345-6789.docx`** — kept because it is the file the fold
  argument cannot absorb.
- **`CD register - practice.pdf`** — kept deliberately as a file this row does **not** claim outright:
  a dispensary register is a dispensary register whichever species it serves.
- **`export health certificate - signed.pdf`** — kept for the D4 trap. A country block on a certificate
  is the single most likely place someone mints `jurisdiction` as a field; the JSON forbids it inline.
- **A boarding/kennel record, a grooming record, a breeder's pedigree** — all rejected as examples.
  They share the animal-and-owner shape with no veterinary act in them; folded into `needs_llm` instead
  of given fixtures they do not deserve.
- **A pet-food invoice** — rejected: retail, and already carried by the `retail_hospitality.store-operations`
  edge.

## proposed_fields

**None** — deferred to the schema row's single `subject_of_record` proposal, which this row reuses
rather than varying. That proposal is a *better* fit here than anywhere: the subject of record is
plainly not the holder and plainly not the client either.

Three keys were tempting and I minted none. **`species`** is the obvious one and is exactly the trap —
species is a **value in a slot**, and 00 is explicit that the system "may create new values … but it
should not invent new fields automatically". The recognition therefore uses the *slot's existence*,
never its contents, and `template.why` states outright that species is not a dimension. **`owner`** /
**`client`** — `client` already exists in `canonical_fields.json` with `our_firm` as its `role_split`
partner, and reusing it here would import a commercial-engagement meaning that is only half right,
while minting `owner` would be a D6 synonym. Left as prose.

## Neighbours considered that did NOT get an edge

- **`medical`** — no honest case. The medical safety domain is about the holder's own health; an animal
  is not the holder, and asserting the edge would blur the one boundary this family is clearest about.
- **`legal` / `law_practice`** — export certification and euthanasia authorisation have legal weight,
  but the disclosure and claim world is `clinical_practice.malpractice-incident`'s and is already edged
  from there.
- **`government.permit-licensing`** — animal movement and holding registration are permit records on
  the issuer's side; left unasserted at gist depth, and the holder-side discriminator is identical to
  the one `practice-administration` already carries against `government.professional-regulator`.
- **`resource_operations` / agriculture** — the farm face touches production records, but the roster
  row has not landed and the discriminator ("is there a veterinary act in it") is already stated in
  `needs_llm`. Asserting an edge to an unlanded id at gist depth would be padding.

## NEEDS-JOSEPH

- **NJ-CP-17 · The fold question. Should this row exist, or is `veterinary` a value?** Argued both ways
  above and in the JSON `open_question`; my answer is that it should stay, on the strength of the
  tri-party structure, the inverted privacy party, and the food-animal face. A one-sentence ruling
  settles it. It belongs to R1c/Joseph, not to this row.
- **NJ-CP-17a · Two reciprocals ride along, both authored one-way here.**
  - Against **`clinical_practice.pharmacy-operations`** — a sibling landed in this same wave and
    outside my authored-fresh three; I verified it does not name this id and did not edit it.
  - Against **`photos.camera-events`** — verified by grep that the landed `photos.camera-events.json`
    does **not** name `clinical_practice`, and it is outside my five. This is the reciprocal I most
    want R1c to actually write, because on a normal machine pet photographs will outnumber genuine
    veterinary practice records by orders of magnitude, and the photos side is where the false positive
    will be caught.

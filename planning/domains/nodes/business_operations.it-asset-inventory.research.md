# business_operations.it-asset-inventory — lab notes (template row)

**Depth: J-DEPTH.** Deepened from the gist-era draft. Preserved where the draft was right, argued
where it was thin, and one gist-era judgement is explicitly reversed (the `support-operations`
non-edge, below). The gist verdict on the node test is **not** reversed, and the reason it survives
a genuinely hostile reading is the substance of this memo.

`launch: "placeholder"`, `fields: []`, `proposed_fields` seconds two existing family proposals and
mints nothing.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — the source of truth. Every `“…”` span in the JSON
  and in this memo was machine-matched against it after writing; 26 of 27 quoted spans match `00`
  verbatim, and the 27th is an explicitly attributed quotation of a sibling row
  (`construction_property.json`, verified verbatim there).
- `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`,
  `planning/domains/CONNECTION.md` (§2 node test, §4 activation — step 2 never-alone and step 5
  safety split are both load-bearing here), `CONNECTION-EXAMPLES.md`.
- `planning/domains/canonical_fields.json` — checked before proposing anything, and the reason this
  row proposes nothing new.
- `planning/domains/roster.json` — every `collides_with.domain` and `also_holds_with.domain` in the
  JSON was re-checked against it after the deepening edits. All exist.
- `src/evidence_shape/vocabulary.py` — every `source_type` in the JSON is in `SOURCE_TYPES`.

### The schema anchor, read first and read as binding

`business_operations.research.md` (46KB) is now a real anchor and this row is measured against it,
not against its own intuitions. Three of its rulings govern this file and are quoted or paraphrased
where used:

1. **The default template**, which a sibling must differ from — organisational unit (conditional) →
   governance body / project / contract / account → fiscal period → document function, **not
   time-first**.
2. **The never-alone principle for all 24 siblings** — *"No sibling may rest its activation on an
   entity name, a business vocabulary word, or a document shape alone."*
3. **The function-words-are-values rule**, which the anchor calls the single most important sentence
   in the memo for sibling authors, and which names this row by name: what earns a row like this its
   node is *"a distinct **structure** — a tender evaluation matrix, an asset register with serials
   and lifecycle dates, a risk register with likelihood/impact scoring columns — not the topic
   word."*

### Siblings and neighbours read before writing

- `business_operations.organisational-records.json` — read **first**, on the dispatch's instruction
  that this row might be heading the same way. It is not, and §"Why this row is not
  organisational-records" below says exactly where the two arguments diverge.
- `business_operations.vendor-management.research.md` and `.procurement-sourcing.research.md` — the
  two siblings whose documents travel with asset purchases. `vendor-management` explicitly routes
  *"reciprocal-facing procurement and contract signals"* through this row, so its boundary language
  is adopted rather than contradicted.
- `identity.credentials-passwords.json` — read for its privacy posture, which is stricter than this
  family's and which this row now defers to explicitly on the credential seam.
- `finance.crypto-assets.research.md` — read as the depth calibration target, for shape only.

---

## Provenance of this file: SALVAGE, then DEEPEN

The JSON was written by an agent killed mid-wave, then verified and completed by a second agent
which mechanically checked every quotation, every roster id, every `source_type` and every residual
name, compared the key set against `clinical_practice.case-conference.json`, and split two run-on
`never_alone` entries into one-invariant-per-entry. That verification stands and was **not** redone
from scratch; it was spot-checked (all quotes and all ids re-verified after my edits) and found
sound.

The dispatch warned to read the draft critically rather than assume every line was deliberate. Read
that way, one line was **not** deliberate, and it is corrected below: the gist memo's decision to
leave `business_operations.support-operations` unedged.

---

## What it is for, and what it holds

Keeping a **maintained record of the IT estate**: what hardware and software exist, who holds each
item, what each is entitled or licensed to run, and how the estate is wired together. Asset
registers and inventory exports, software licence and entitlement records, device-management and
directory exports, network/system/estate diagrams, device handover and return forms, warranty and
support-cover records, disposal and secure-destruction certificates, refresh and lifecycle plans,
stocktake reconciliations.

**The anchor is the estate as a standing inventory** — not a purchase, and not a contract. That
sentence is doing all the work, and every boundary below is a corollary of it.

---

## The node test, argued leg by leg

CONNECTION §2: *"A **template** row exists only if its detection signals, recommended dimensions, or
privacy rules differ from its schema's default template."* Three legs. I argue each separately,
because two of them pass on real evidence and one **cannot pass at all** — and saying which is which
is the point of running the test rather than announcing a verdict.

### The hostile reading, stated first

The dispatch's warning is correct as far as it goes: an asset inventory is *plausibly* a spreadsheet
shape rather than a filing world, and its two most obvious candidate signals — an organisation name,
a table of devices — are **each individually never-alone** under the anchor's rule and under `00`'s
own sentence, *"A university name alone should not create a group because Columbia can appear as an
authoring school, course provider, target institution, employer, research venue, or merely a cited
organization."* If those two were the whole of this row's support, it would be a row that never
fires, and refusing would be correct.

They are not the whole of its support, and the anchor's rule says precisely why: it does not forbid
a structure, it forbids an **unpaired** one. *"Every detection signal a sibling writes must pair a
**structure** with a **labelled slot**."* This row can name that pair, several times over, and the
anchor names this row's structure as an example of one that earns its node.

### Leg 1 — detection signals. **Passes, and this is the strong leg.**

Four signal shapes, each a structure paired with a labelled slot, none of which is the schema's
default template and none of which is a topic word:

1. **The identity-plus-custody header.** A tabular structure whose header row carries asset-identity
   columns — asset tag, serial number, hostname, model — *together with* an assignment or location
   column naming a person, a team or a site. Neither half alone qualifies: a serial column alone is a
   parts list, an assignment column alone is a rota. **Identity and custody in one header row** is
   the shape, and `00` licenses reading it — *"Tables matter because resumes, forms, applications,
   invoices, and administrative documents often place their most useful information in cells rather
   than body paragraphs."* This is the signal the anchor was describing when it wrote *"an asset
   register with serials and lifecycle dates."*
2. **The entitlement-plus-count structure.** A named software product paired with a seat or quantity
   count and a renewal or expiry date, usually with an assigned-versus-purchased comparison. The
   variance between two counts is the tell; a licence certificate alone has no counts to reconcile.
3. **The estate diagram text layer.** Subnet or CIDR notation, VLAN identifiers, hostnames, rack or
   switch labels — as opposed to the dimensioned geometry of an engineering drawing or the names in
   an org chart. Note carefully what is *not* claimed: the diagram **extension** is not evidence, and
   the JSON's `never_alone` says so.
4. **The custody-transfer structure.** One named individual, one asset identifier, one date of issue
   or return — the handover/acceptance form, and its terminal cousin the disposal certificate naming
   an asset identifier and a destruction method.

None of these four appears in the schema's default template, which is a governance/period/function
shape built around cycles and controlled documents. An estate register is not a cycle artefact; it
is a **living document** that is re-saved rather than re-issued.

### Leg 2 — recommended dimensions. **Cannot pass, and does not need to.**

`template.dimension_order` is `[]` and must be: `business_operations` declares **no field rows**
(PR-6, D1's deferral as narrowed, `_CONTRACT` rules 10 and 15), and a dimension naming an undeclared
field opens a tree level no fact could ever fill. This leg is therefore **unavailable to every one of
the 24 siblings**, not failed by this one. §2 requires signals *or* dimensions *or* privacy rules to
differ, so the row is entitled to pass on the other two. Stating this plainly matters: a sibling that
claims a dimension difference on this schema is claiming something the contract forbids it to have.

Held as prose, for the pass that may license fields, and **differing from the anchor's paragraph**:
the natural anchor is the organisation or site whose estate this is, then the **asset class**
(end-user device, server, network, software entitlement), then the document function; a snapshot date
sits **last**. That middle level is this row's genuine divergence from the family default — the
family's second level is *governance body / project / contract / account*, and an estate has none of
those. Its second level is a taxonomy of **things owned**. Not time-first, and the anchor forbids any
sibling from claiming otherwise: *"For document and record domains, project, function, or subject
usually comes before time because putting year first scatters related work across calendar folders."*
On this row that rule has extra force, because the register is one artefact re-saved quarterly — a
period-first tree would shatter a single version family across four folders.

### Leg 3 — privacy rules. **Passes, and it is stricter than the family default.**

The dispatch asked for this leg to be considered carefully and it repays the attention. The anchor's
family-level privacy argument is that *the exposed party is usually not the user* — a third party
who cannot consent, appearing as a counterparty or in an appendix. On this row that property is not
occasional; it is the register's **primary axis**. An asset register is a staff roster joined to an
equipment list: it names every member of staff beside the device they carry and often where they sit.
There is no version of this document that does not do that, which is a stronger claim than the family
makes and is the reason the posture is stricter rather than equal.

Two further grounds specific to this row:

- **Operational exploitability.** A network diagram is a description of how to *reach* the systems the
  register lists. This is not "documents can be sensitive"; it is a distinct harm shape that the rest
  of the family does not have.
- **The credential seam.** Device-management exports, build sheets and licence records routinely carry
  recovery keys, local administrator passwords, product keys or certificate material in a column
  nobody looked at. `00` is unambiguous about that material: *"A scanned passport, tax statement,
  medical document, authentication key, or account record should enter a protected state
  immediately."* `identity.credentials-passwords` owns that span and its protection runs first
  (CONNECTION §4 step 5). This row **defers**, and the JSON now carries both a `collides_with` and an
  `also_holds_with` to `identity` saying so.

The operative limit this row leans on is `00`'s local-only sentence: *"Paths, complete extracted text,
OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values
should remain local."* Concretely, the recommendation now written into `sensitivity_why` is that a
register or diagram be summarised **by structure** (a device table of N columns; a topology diagram)
rather than by contents, that no custodian name and no address token reach a cloud prompt or a general
group summary, and that this row never acquire automatic internal depth — the redaction hook is
`00`'s own, *"Protected branches should have configurable redaction in the canvas and review
screens"*.

The row still assigns only the catalogue value `potentially_sensitive`, carries **no**
`is_safety_domain`, and authors **no** P7 handling class. Whether the third-party posture is
expressible at all in a catalogue with no handling class is a real gap and is filed as **NJ-BO-IT-2**
rather than smoothed.

### Overall

**Stands, on legs 1 and 3.** Leg 2 is structurally unavailable to the whole family. The gist verdict
is confirmed rather than reversed, on evidence rather than on inertia.

---

## Why this row is not `organisational-records`

Read first, as instructed, because the refusal is the family's best argument and the fastest way to
find out whether a row is hollow. The refusal's reasoning: that row's hint described *material
carrying an organisation name and a document type but no more specific operational sub-domain* —
which is not a situation but **the absence of one**, and the absence of a situation already has homes
(the schema's own default template, and Independent Records).

This row fails that description at the only point that matters. Its support is not "an organisation
name plus a document-type word"; it is a **specific header-row shape** that can be described without
naming any organisation at all, and that a P4 extractor could evaluate on a file whose entity is
unknown. The test that separates them is mechanical: *could this row's detection signals fire on a
file that names no organisation?* For `organisational-records`, no — nothing would be left.
For this row, **yes**: `intune_device_export_20260301.csv` names no entity anywhere and still fires
cleanly on its header structure. That asymmetry is the whole difference, and it is why one refusal is
correct and this one would not be.

The `market-research` row handled the same risk the same way and reached the opposite verdict for the
same kind of reason; that precedent is followed here, not copied.

---

## Files considered and rejected

A row that only lists what it holds has not been researched. The tempting false positives, and what
discriminates each.

| File | Why it is **not** this row's evidence |
|---|---|
| `Dell invoice INV-88213.pdf` (**kept as the primary collision fixture**) | Line items name laptop models and serial numbers — every signal an untrained reader would call an inventory. It is a **transaction**, not an inventory: an invoice header, a total, a tax line, payment terms. Purchase is a moment; an estate is a standing state. **Receipts and Confirmations**, or `finance`. |
| `Fixed asset register FY26.xlsx` (**kept as the second fixture, and the file that must not be lost TO this row**) | The same machines, the same serials, in the same table shape — but its columns are acquisition cost, depreciation method, accumulated depreciation, net book value, and a nominal code. It is the accounting book's. The discriminator is **which columns join the serial**: custody and configuration → this row; cost and depreciation → the book. |
| A **plant and equipment register** | Identical identity-plus-custody table. Discriminator: machine numbers, calibration due dates, maintenance intervals and criticality ratings → `manufacturing.asset-register`; hostnames, operating systems, entitlements and network addressing → this row. |
| A **stocktake of goods held for sale** | Quantity-and-location table, often with the same software producing it. Goods for sale have a unit price, a reorder level and no custodian. Not an estate. |
| A **shipping manifest / packing list** | Serials and quantities, and it arrives *with* the fleet. It records a movement, not a holding. |
| A **warranty card or repair receipt** | Carries a serial, which is exactly why the JSON's first `never_alone` entry names serial-shaped tokens. One asset identifier with no register or custody structure around it is **Independent Records**. |
| An **architecture or infrastructure diagram in a repository** | Same diagram vocabulary. Discriminator: residence under a preserved repo root, and service-level rather than device-level naming → `code.software-project`. The schema anchor already forbids this family from re-filing anything inside a repo. |
| A **floor plan or an org chart** in `.vsdx` / `.drawio` | The single most seductive false positive in this row, because the *file type* is the same and the file type is not evidence. `00`: the engine should *"treat the file extension as a routing signal rather than an assumption about meaning"*. Only the text layer's estate tokens discriminate. |
| An **access-badge list** or a keys register | Identity-plus-custody, and often the same site name. Rooms, desks, keys and premises → `business_operations.facilities-workplace`. |
| A **vendor's product catalogue or datasheet** | Dense in hardware model names and specifications, and often filed beside the register. It is marketing material about things nobody owns yet. **Reading Inbox**. |
| A **blank handover form template** | Real, common, and it fires the custody-transfer structure with every slot empty. The anchor's real-versus-exemplar rule governs: *"purpose answers what the file was for"*. A blank form is a `work_type`, not a custody event, and it must never produce a person fact. |
| An **IT policy or acceptable-use handbook** | Same function word, entirely different structure — a controlled-document header, which is `policy-handbook`'s signal, not this row's. Function words are values. |
| A **screenshot of a device list in a web console** | OCR yields device-shaped rows and no header semantics. **Temporary Screenshots** unless a register or accepted group is around it. |

---

## The collision fixture, in both directions

**Direction one — a file that would wrongly fire this row:** `Dell invoice INV-88213.pdf`. Serial
numbers, hardware models, a supplier, a delivery address that looks like a location column. Every
lexical signal fires. **What discriminates:** the invoice's structure is a *demand* — invoice number,
total, tax line, terms — and there is no custody column anywhere on it, because at the moment of
purchase nobody has been issued anything. What emphatically does **not** discriminate: the presence
of serials, the vendor name, or the folder it sits in.

**Direction two — a file that must not be lost *to* this row:** `Fixed asset register FY26.xlsx`.
Here the risk runs the other way: the file is a register, it is about assets, and if this row is
allowed to read a register plus a serial as sufficient it swallows the accounting book whole.
`finance.small-business-bookkeeping` names the same bytes from its side, and this row's
`collides_with` entry to it now names them from this one. **The discriminating evidence is the
adjacent columns, not the serial**, and the JSON's fixture says so in `must_not_conclude`.

**The bytes both neighbours must name:** a workbook containing *both* a custody sheet and a
depreciation sheet. That is disjoint-evidence co-activation, not a contest — and it is the case where
the `never_alone` discipline earns its keep, because neither side may claim the other's sheet.

---

## Reciprocal boundaries, both directions

Every neighbour read before its boundary was written. Where a neighbour has not been written yet, or
does not name this row, that is stated rather than assumed.

| Neighbour | This row must not take | The neighbour must not take | Shared fixture bytes |
|---|---|---|---|
| **`business_operations.procurement-sourcing`** (gist) | the **sourcing event** — solicitation, specification, clarification log, evaluation matrix, award or regret letter, purchase order. That row's anchor is a bounded competition and its clarification log *"exists in no other situation in the catalogue"* | the **standing register** that lists what the competition eventually bought, and the custody columns it grew afterwards | an award letter naming laptop models, filed next to the register of those laptops |
| **`business_operations.vendor-management`** (gist) | onboarding forms, diligence questionnaires, insurance certificates, scorecards, supplier codes, exit records — anything anchored on the **relationship** | the **per-device** register. A supplier register's row is an organisation with a relationship owner; this row's row is a machine with a custodian | an approved-supplier list naming the hardware reseller who also appears on the estate export header. That row already routes procurement/contract signals through this one; this boundary is written to agree with it |
| **`business_operations.contract-administration`** (gist) | the **instrument and its obligations** — the executed agreement, notice periods, an obligations register keyed to clauses | the **seat count reconciled against assignments**. An entitlement is an inventory line as well as a contractual one | `Adobe licence certificate.pdf` — genuinely both, and the JSON's fixture says `must_not_conclude` which row owns it |
| **`business_operations.facilities-workplace`** (gist) | rooms, desks, keys, premises, maintenance contracts, building plans | hostnames, entitlements, device custody | a site record naming the same office as the network diagram's title block |
| **`business_operations.support-operations`** (gist) | a **case anchor** — ticket or case identifier, status/priority/assignee, a chronological thread | a **standing register with no case anchor**, and a device export that a support tool merely happens to have produced | a device list exported from a service-desk tool. **See the reversal below** |
| **`finance.small-business-bookkeeping`** (landed) | journals, ledgers, invoices, reconciliations, statements — and the **fixed-asset register kept for depreciation**, which is the working book's | the **custody and configuration** view of the same machines | `Fixed asset register FY26.xlsx`; the both-sheets workbook above. **One-way here — the landed finance row does not name `business_operations`; R1c owes the reciprocal** |
| **`manufacturing.asset-register`** (roster row, not yet written) | machine numbers, calibration due dates, maintenance intervals, criticality ratings | hostnames, operating systems, licence entitlements, network addressing | a register of shop-floor machines that are *also* networked. Written here for that row's author to write against |
| **`hr.onboarding-offboarding`** (roster row, `hr` schema not yet written) | a checklist spanning accounts, payroll, induction and access, and anything identifying a named employee as an employee | a form anchored on **one asset identifier** with no employment content | `Laptop handover form - signed.pdf`. Both anchors genuinely present; **co-activation, and the hr side governs the person-identifying members** per the schema anchor's stricter-side-wins rule. `also_holds_with: hr` added in this pass. One-way; R1c owes the reciprocal |
| **`identity.credentials-passwords`** (landed, safety) | an exact recognized credential format, a key or password export structure, a vault container — **and identity's protection runs first** | an estate table whose columns are identity and custody, merely because a key-shaped token appears in one cell | a device export with a recovery-key column. `collides_with` **and** `also_holds_with` added in this pass. One-way; that landed row does not name this family |
| **`code.software-project`** (roster) | anything inside a preserved repository root; service-level architecture naming | an **asset tag, a custodian, a warranty or purchase anchor** merely because IT produced the file | an infrastructure diagram committed beside source |
| **`business_operations.compliance-audit`** (gist) | the audit's own apparatus — findings, corrective actions, evidence indexes | the register that an audit **requests as evidence**. Being cited as evidence does not transfer ownership | an asset register attached to an ISO evidence pack |
| **`government.public-authority-record`** (roster) | a public body's issuing letterhead, case reference or statutory power | a public body's asset register, which is this shape under a records regime | a council's device register. Left unedged at gist depth; **still unedged**, and now with a reason: the confusion is about the *owner type*, which the schema anchor already handles at family level |

---

## The gist judgement I am reversing

The gist memo listed `business_operations.support-operations` under "neighbours considered that did
NOT get an edge", on the grounds that *"asset records are pulled into ticket handling constantly, but
the confusion is about lookup, not about which situation a file belongs to."*

**That is too generous and I am reversing it.** The lookup framing is true of an agent *consulting*
the register mid-ticket, which is not a filing question. But a service-desk platform exports device
and user lists in exactly this row's shape, and those exports are files that must land somewhere.
Those bytes are genuinely contested, so the edge exists and the discriminator is the **case anchor**.
A `collides_with` entry has been added saying so. Stated explicitly rather than changed quietly, per
the addendum.

The gist memo's other non-edge (`government.public-authority-record`) is **kept**, with the reason
upgraded from the gist memo's *"left unedged at gist depth rather than guessed"* to the argued owner-type reason above.

---

## `proposed_fields` — two, both seconded, none minted

`fields: []` by contract. The dispatch's instruction was to second the family's existing
`organization` / `fiscal_period` proposals rather than mint variants, and that is what the JSON now
does — with an argument on each, for R1c.

- **`organization`** — seconded, not proposed anew. R1c must read this as **one decision across three
  rows**: the `business_operations` schema row proposes it, `construction_property` seconds it with
  the instruction that it *"should be adjudicated once, there, for both,"* and this row seconds it a
  third time. Seconded `destination_eligible: false`, and this row **strengthens** the schema's reason
  rather than merely repeating it: an IT estate corpus is almost always single-entity, so an
  `organization` level here is precisely the level `00` forbids — *"A folder should not become a
  collection point for everything produced by the same person or organization."* Seconded ceiling
  `possible`, with one estate-specific reason it cannot rise: **the entity name most reliably present
  on this row's files is the vendor's**, printed on an export header or a licence certificate, not the
  custodian's. A rule that read the strongest entity token would systematically read the wrong role.
- **`fiscal_period`** — seconded. This row's own reason for wanting it: a licence reconciliation and a
  stocktake are period artefacts of a management calendar, and a renewal or true-up date is set by a
  **subscription term**, which no statutory year governs. Seconded `destination_eligible: true` and
  explicitly **not first**, for a reason sharper here than on the schema (the register is a living
  document; a period level above it scatters one version family). One caution recorded for R1c: the
  most common date token on this row's files is a machine-generated **export** date in a filename,
  which is a snapshot timestamp and not a fiscal period at all — a rule family that cannot separate
  the two belongs at `possible`, not `validated`.

**Deliberately not proposed:** any asset-identity key (`asset_tag`, `serial`, `hostname`). The
temptation is enormous and the anchor named exactly this trap — minting a key on a field-less
placeholder at the point of maximum temptation would be the 574's mistake performed knowingly. Worse,
a serial is a **device identifier**, and the anchor's authorship prohibition reads across: a machine
is no more a destination than its custodian is. Also not proposed: `supplier`, which
`vendor-management` correctly routes to `contract-administration`.

---

## Sparse-file discipline

Eight of ten fixtures carry `group_without_copying_facts: true`, and this row needs the rule more than
most because its sparse members are the normal case — a photograph of a rack label, a blank form, an
archive read from its manifest, a diagram binary. The estate folder is the archetypal place where a
hundred files sit beside one that names everything, and `00` settles it: *"The graph does not
automatically copy those missing facts onto sparse files."* Concretely: `IMG_4471.jpg` may be grouped
with the register beside it and must acquire **no** asset fact from it, and the archive's manifest
produces no domain for its members.

The purpose-coherence licence for grouping at all is `00`'s: a register, two diagrams, a licence PDF
and a blank form are *"content-incoherent but purpose-coherent."* And **no group is a valid outcome**
— a lone licence certificate is Independent Records.

---

## Legacy ids absorbed (ROSTER.md Appendix A, lines 693–694)

`soft.it-asset-inventory` (ROW) and `soft.network-diagram` (FOLD). The fold is correct and worth
defending explicitly, because a diagram *looks* like a different world: a network diagram and an
asset register describe **the same estate** at different resolutions, they are produced and revised
by the same function on the same review cycle, and they are the same purpose-coherent packet. Splitting
them would have produced a row whose only content was a file format — which CONNECTION §2 forbids by
name ("never a schema per file format").

---

## NEEDS-JOSEPH

- **NJ-BO-1 · The single-person estate.** Carried from the draft and endorsed again. A freelancer's
  list of their own laptops, warranties and software subscriptions has exactly this shape and none of
  the organisational anchor. Alternatives and costs: (a) let it fall to personal administration /
  Independent Records — cost: a real recurring situation gets no template; (b) let this row take it —
  cost: someone's personal device list is filed under a work branch on evidence that never mentioned
  work. This row recommends (a) and refuses to decide it silently. **Same question as NJ-BO-8** from
  `partnerships-bd`; R1c should notice it is one question asked twice.
- **NJ-BO-IT-2 · Third-party concentration has no catalogue expression.** The privacy leg above is the
  strictest thing about this row and it is currently prose, which nothing enforces. (a) Leave it as
  prose — cost: the strictest fact about the row is the one the machine cannot read. (b) Let R1c mint
  a catalogue-level marker for third-party-personal-data concentration, covering this row, `hr` and
  the parts of `business_operations` that carry staff appendices — cost: new vocabulary on a
  field-less placeholder. This row recommends (b). Related to the schema anchor's **NJ-J-IND-4**,
  which raised the same need from the family side.
- **NJ-BO-IT-3 · The credential-column seam.** When an estate export carries a real key column, does
  `identity` activate on the file (protecting the whole export) or on the span? `identity` runs first
  by CONNECTION §4 step 5, but that step describes schema activation, not sub-file scoping. (a)
  Whole-file protection — cost: an ordinary device inventory becomes Protected Records because of one
  column. (b) Span-level — cost: it presumes a sub-file protection mechanism the design does not yet
  name. This row states the dependency and does not choose. `identity.credentials-passwords` carries
  an adjacent open question about metadata-only format identification; R1c should read them together.
- **NJ-BO-IT-4 · Reciprocals owed.** Four boundaries here are authored **one-way**: to
  `finance.small-business-bookkeeping`, `identity.credentials-passwords`, `hr.*` and
  `manufacturing.asset-register`. None of those rows names `business_operations`. This is a catalogue
  defect for R1c, not a judgement about the seams.

---

## What changed in this pass

**Preserved unchanged** (verified, not rewritten): the 27-key key set and its order; `fields: []`,
`dimension_order: []`, `time_first: false`; the whole `recognition` block as written (7 deterministic,
5 needs_llm, 9 never_alone — two entries appended, none altered); all 20 `proposed_context_terms`; all
9 `work_types`; all 4 `grouping_reasons`; the `template.why` prose; `file_kinds`; the 9 original
fixtures verbatim; the 7 original `collides_with` entries; all 5 `falls_through_to` entries;
`sensitivity`; the original `open_question`; and the gist memo's node-test **verdict**, which this
pass confirms rather than reverses. Every previously-verified quotation was re-checked and re-passed.

**Changed in the JSON** (six edits, nothing rewritten):

1. `one_line` — retired `Gist-level placeholder (J-IND)` label replaced with *"A PLACEHOLDER TEMPLATE
   ROW written to J-DEPTH"*. Substance unchanged.
2. `proposed_fields` — was `[]`; now two **seconding** entries (`organization`, `fiscal_period`), each
   marked `SECONDING, NOT MINTING`, each carrying this row's own added argument, and each telling R1c
   this is one adjudication across the family rather than a competing proposal.
3. `collides_with` — three entries added: `business_operations.vendor-management`,
   `identity.credentials-passwords`, and `business_operations.support-operations` (the reversal).
4. `also_holds_with` — was `[]`; two entries added (`hr`, `identity`), both disjoint-evidence
   co-activation, both flagged one-way.
5. `never_alone` — two invariants appended: the licence-key-shaped token, and the business-function
   word (applying the anchor's function-words-are-values rule to this row by name).
6. `sensitivity_why` and `open_question` — extended with the third-party-primary-axis argument, the
   local-only quotation and the concrete structure-not-contents recommendation, and with NJ-BO-IT-2's
   alternatives.

**Added in this memo** (the deepening proper): the sources section naming what was read and why; the
hostile reading stated before the verdict; the three-leg node test argued separately, including the
statement that leg 2 is unavailable to the whole family rather than failed by this row; the
"why this row is not `organisational-records`" section with its mechanical separating test; the
thirteen-row rejected-files table; the collision fixture in **both** directions with the
both-sheets-workbook bytes; twelve reciprocal boundaries with the one-way ones flagged; the explicit
reversal of the `support-operations` non-edge; the defence of the `soft.network-diagram` fold; the
sparse-file discipline section; the seconding arguments and the deliberate non-proposals; and four
NEEDS-JOSEPH items with alternatives and costs rather than one.

**Depth note, stated honestly:** this memo is shorter than the 40–46KB schema anchors and sits at the
lower end of the landed launch band. That is deliberate. A placeholder template row on a field-less
schema has one leg of the node test permanently unavailable and no field decisions of its own to make,
so two of the sections that carry the most weight on a launch row have less to say here. Everything
this row genuinely has to say is above; none of it is padding.

# finance.insurance-corporate — lab notes (R1b)

Roster row: `kind: template`, `schema_id: finance`, `launch: placeholder`, `parent_id: null`.
Output: `planning/domains/nodes/finance.insurance-corporate.json`. No other file written.

**Salvage disclosure.** The JSON existed as an untrusted partial draft from an interrupted
session. It was not accepted on sight. Every quoted span was re-verified mechanically, every edge
id was re-checked against the roster, every `facts_legal` key was re-checked against
`canonical_fields.json`, and four substantive defects were found and fixed (listed under
"What changed in the draft"). The remainder of the draft survived verification and this node takes
full ownership of it. The memo did not exist and is written here.

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — the source of truth, read in full.
  **`00` never uses the word "insurance"** (grep: 0 hits), and never names a corporate,
  commercial or business insurance situation. That is why `provenance` is `inference` and
  `design_cite` is `null`. What `00` does supply, and what the node leans on:
  the Finance field sentence, the safety-domain sentence, the template-definition sentence, the
  parent-dimension rule, the narrow-date rule, the labelled-slot / direct-fact rule, the table and
  spreadsheet extractor slots, the archive-inspection rule, the never-alone rules, the
  grouping firewall, the dossier rule, and the nine residual definitions.
- **Quote verification, mechanically.** Every `'…'` span in the node file was extracted with a
  regex that excludes possessive apostrophes (opening quote preceded by a non-alphanumeric,
  closing quote followed by a non-alphanumeric), whitespace-normalised, and substring-matched
  against a whitespace-normalised `00`. **51 of 51 design quotations matched verbatim.** Exactly
  three quoted spans are not from `00`, and each is intentional and labelled as such in place:
  `a labelled account-descriptor slot or table cell on the record itself` (quoted from
  `nodes/finance.json`, verified there), `This endorsement modifies insurance provided under the
  following:` (prose printed on the file being described, not a citation), and
  `the 2026-27 general liability policy` (scare quotes in `open_question`, not a citation).
- `planning/01-product-design-structured.md` — locator only. No quotation in the node is taken
  from `01`'s rendering.
- `planning/domains/_CONTRACT.md`, `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md`, `planning/domains/CONNECTION-EXAMPLES.md` (fixture 8 read in
  full — see the disagreement recorded below),
  `planning/overnight/council/DECISION-BRIEF.md` (D1–D6 and J-IND treated as binding, not
  re-debated: D1 keeps this row writing no career/legal/medical field rows, D4 keeps jurisdiction
  and form names as **values**, D6 keeps keys snake_case).
- `planning/domains/roster.json` — confirmed the row, and confirmed **every** id used on an edge
  exists as a `domain_id`.
- `planning/domains/canonical_fields.json` — nothing minted. `institution`, `account_type`,
  `record_type`, `tax_year`, `client`, `our_firm`, `school` all resolve; the universals used in
  `file_examples` (`file_type`, `creation_date`, `duplicate_family`, `media_type`) resolve.
  **`account_holder` does not resolve** — it is a `proposed_fields` entry on the `finance` schema
  row, not canonical yet. The node therefore never writes it into a `facts_legal` list; it names
  it in prose only, and seconds the proposal below rather than re-minting it.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` checked mechanically against
  `file_kinds.source_types` and all fourteen `file_examples[].source_type`. Clean.
- Landed neighbours read for edge alignment, **not rewritten**:
  `nodes/finance.json` (the schema row and its default template),
  `nodes/finance.insurance-personal.json` (the mirror sibling, read in full),
  `nodes/finance.small-business-bookkeeping.json`, `nodes/finance.cap-table-equity.json`,
  `nodes/finance.household-property.json` (shape and house style).

**CONNECTION.md is binding and present.** Two places where it beats the dispatch prompt's looser
wording, noted as instructed:

1. `also_holds_with` is **schema-to-schema only** (CONNECTION §5). This is a template row, so
   `also_holds_with` is `[]` — empty by contract, not by omission. The per-file co-activations are
   carried in `file_examples[].also_schema` and the missing schema-level join is filed as NJ-3.
2. `parent_id` is browse-only and R1b never authors it. Left `null`.

---

## The node test — applied honestly, including the half it fails

CONNECTION §2's test is disjunctive: signals, dimensions, **or** privacy rules must differ from the
schema's default template.

**Dimensions do NOT differ.** The recommended order here — `institution → account_type →
record_type` — is character-for-character the `finance` schema node's default. That is stated first
in the node's `node_test` field rather than hidden, because dressing it up as a novel
recommendation would be exactly the padding the test exists to catch.

**Signals differ, decisively.** Three structures in this situation exist nowhere on the finance
schema's union of signals and nowhere in the personal sibling:

- the **ACORD certificate** — three organization roles on one page (producer, insured, certificate
  holder), an insurers-affording-coverage legend, a row-per-coverage table whose leftmost column is
  a labelled coverage descriptor, and a confers-no-rights disclaimer;
- the **workers-compensation** classification-code / estimated-payroll / experience-modification
  table;
- the **loss run** — a repeating claim register (date of loss, claim number, status, paid, reserve)
  under a policy header.

A bank statement, a bookkeeping ledger, a tax form and a household declarations page fire none of
them.

**Privacy rules differ.** The finance schema reads its material as the user's own account records.
A firm's insurance file is substantially **third-party** data: loss runs carry claimant names and
injury descriptions, workers-compensation records carry employee names and payrolls, a renewal
submission carries an employee census, a claim file carries allegations under an open matter. The
people in that data never handed the firm anything. This is the single finding the node is most
confident about, and it is why the node adds **Protected Records** beyond the one residual
(`Independent Records`) its roster row names.

**Not refused**, and the reason is organizational rather than lexical: a **certificate of
insurance** is a document the firm *produces for a third party*, and a **renewal submission** is a
purpose-coherent, content-incoherent packet assembled once a year. Neither shape exists in the
personal situation. Neither is a work type and neither is a file extension.

---

## What changed in the draft

1. **`design_cite` → `null`.** The draft carried a long prose `design_cite` containing a quotation
   of CONNECTION.md's PR-8 compressed with an ellipsis across markdown emphasis
   (`'…is templates over the Finance schema vocabulary ... three organizational situations, not
   three schema slugs'`). The real text is *"insurance (personal / corporate / healthcare) is
   **templates over the Finance schema vocabulary** (`institution`, `account_type`, `record_type`,
   `tax_year`) — three organizational situations, not three schema slugs."* An ellipsis-compressed
   span inside quote marks is the fabricated-quotation failure `_CONTRACT` rule 2 exists to
   prevent, even when the compression is honest. Since `provenance` is `inference` and the citation
   was to CONNECTION rather than to `00`, the correct value is `null` — which is also what the
   landed sibling `finance.insurance-personal` carries. The reasoning moved here.
2. **Missing reciprocity: `finance.hoa-residents-association`.** That row already authored a
   `collides_with` naming this node; this node did not name it back. Added, with the
   discriminator argued rather than asserted: an association master policy and a firm's policy have
   the *same* labelled structure, so the discriminator is what the named-insured organization **is**
   and what the surrounding packet holds (governing documents, reserve study, minutes, assessments →
   association; class codes, a client certificate holder, a renewal submission → this row). A unit
   owner's own walls-in policy is neither and is `finance.insurance-personal`.
3. **Added `node_test`.** The draft never stated that its `dimension_order` is the schema default.
   It now does, first.
4. **`template.why` de-overclaimed.** The draft called `account_type` second "this template's
   substantive recommendation." It is the schema's default. Reworded to say what is actually new —
   the *reason* the default is right here (the policy **is** the account, so the coverage line fills
   from a labelled descriptor slot on nearly every member document) — rather than claiming novelty.
5. **The fixture-8 disagreement surfaced.** See the next section; it was buried mid-paragraph and is
   now named in `template.why` and leads `open_question`.

Everything else in the draft was verified and kept: fourteen file examples, ten collisions, six
residual fallthroughs, three role splits, the recognition triple, the work-type value list.

---

## The one place this row disagrees with a binding document

`CONNECTION-EXAMPLES.md` fixture 8 sketches this template as
`"dimension_order": ["institution", "record_type", "tax_year"]`, and the roster row's
`one_line_hint` repeats it: *"institution, then record_type, then tax_year."*

This row recommends `["institution", "account_type", "record_type"]` — it **inserts** `account_type`
and **drops** `tax_year` from the default order, keeping `tax_year` as an optional level.

Reasoning, stated so it can be overruled cheaply:

- **Why `account_type` is inserted.** For insurance the policy *is* the account, and `account_type`
  carries the **line of coverage** (general liability, professional liability, workers
  compensation, property, cyber, D&O, commercial auto). It is filled from a labelled
  coverage-descriptor slot — "Type of Insurance", "Coverage Part", "Policy Type" — which sits on
  nearly every member document, including the certificate's leftmost table column. Without the
  level, a firm's General Liability and Workers Compensation endorsements land in one
  undifferentiated pile under the carrier. Fixture 8's own sketch for the *healthcare* and
  *personal* siblings omits it for the opposite and correct reason: a household usually holds one
  line per carrier, so the level would open single-child branches.
- **Why `tax_year` is dropped from the default.** A corporate insurance record's own time scope is
  the **policy period**, which commonly straddles two calendar years and which the Finance schema
  has no key for. `tax_year` answers a different question. A `tax_year` level would be empty for
  declarations, endorsements, certificates, loss runs, claim files and schedules — everything
  except a premium record retained for a filing, which is `finance.tax-filings`' situation — and
  `00` tells the canvas to warn about exactly that outcome ("It should warn when a level produces
  only one child…"; "It should recommend flattening when a dimension does not materially improve
  retrieval"). It stays available as an optional level for a firm that genuinely files premium and
  audit records by filing year.
- **Why this is a disagreement and not a violation.** Fixture 8's `dimension_order` values are an
  illustration of the *one-schema-three-templates* point — the fixture's own `forbidden` block is
  about schema slugs, not about ordering — and researching `dimension_order` is precisely what R1b
  was dispatched to do. But the prompt says CONNECTION wins on conflict, so this is filed as
  **NJ-1** rather than treated as settled.

---

## Files considered and rejected

- **A blank/unfilled insurance application form downloaded from a broker.** Rejected as an example
  because it is genuinely *not* this node's — it carries no named insured, no policy number and no
  period. It survives only inside `never_alone` ("a parent folder named for insurance"), which is
  where it does useful work: an `Insurance/` folder full of blanks is the reason a curated folder
  name is not proof about a member file.
- **A carrier's marketing mailer / a broker's capability brochure.** Rejected as an example, kept as
  the `never_alone` case for a carrier name. A deck naming ten carriers is issued by none of them —
  which is why `Broker presentation - 2027 renewal strategy.pptx` **is** an example: it is the same
  trap with a real reason to be in the corpus.
- **A surety bond.** Kept as a `work_types` value, rejected as a file example: it is issued by a
  surety, has a penal sum rather than a limit, and its own structure would need a discriminator
  paragraph that adds nothing this node does not already say about labelled slots.
- **A cyber-incident forensic report received during a claim.** Rejected: it activates on its own
  evidence and would have invited a `security` or `incident` field that does not exist. The claim
  group reaches it through P9 membership without any fact being copied — which is already the
  `Endorsement 007.pdf` lesson.
- **A `.ics` renewal reminder and a broker's `.vcf`.** Rejected deliberately. Calendar and contacts
  are `SOURCE_TYPES`, and CONNECTION §4's worked files settle both: a `.ics` yields `{}` unless
  *content* evidences a roster schema, and `00` keeps VCF data privacy-protected rather than
  proposal-side. Putting either in `file_kinds.source_types` would have been the format-as-domain
  bug.
- **A COI tracking spreadsheet a firm keeps about its *subcontractors'* insurance.** Genuinely
  interesting and genuinely rejected: it is a record of *other* organizations' coverage, so
  `institution` has no single correct filler and the file is closer to vendor management than to
  the firm's own coverage. It is covered obliquely by the
  `Premium Audit Worksheet FY2026.xlsx` must-not-conclude ("a worksheet REFERENCES many
  organizations and is issued by none") and is not worth its own fixture.

Two examples were kept **specifically** as collision fixtures with `facts_legal` deliberately empty
or contested: `Homeowners Policy Declarations 2026-2027.pdf` (empty `facts_legal` — it is the
personal sibling's, even when it arrives in a firm's folder) and
`Group Health Plan - Summary of Benefits and Coverage 2026.pdf` (the healthcare seam). One example,
`Endorsement 007.pdf`, is the `HW 3.pdf` shape: `group_without_copying_facts: true`, no institution
and no account_type invented from the group's declarations page.

---

## `proposed_fields` — none, and why

`proposed_fields` is **empty**. Two candidates were considered and both were refused:

- **`policy_period` / a term-scope field.** Real, and the node's sharpest gap: every document here
  is scoped by a term rather than a date, and it is the thing a firm actually files by. It was not
  minted because the same shape recurs across situations this node does not own — a plan year, a
  lease term, a fiscal year, an academic term — so a key invented on an insurance template would
  either be insurance-specific (the one-way move D4 forbids in spirit) or would be a product-wide
  vocabulary decision taken by the wrong node. Filed as **NJ-2**.
- **`certificate_holder`.** Refused for a better reason: it already has a canonical counterpart.
  The certificate holder is an engagement counterparty, which is `client`, and the split against
  `institution` is authored in `role_split` rather than as a new key.

**One existing proposal is seconded, not re-minted:** `account_holder`, proposed on the `finance`
schema row (`role_split_with: institution`, `destination_eligible: false`), on `00`'s "A finance
document may mention an account holder and an issuing bank". This situation is arguably the
strongest case for it in the whole finance family, because the named-insured / issuer inversion is
the most damaging single error available on these files. Until it is canonical, this node writes it
nowhere in `facts_legal`.

`proposed_context_terms` **is** populated (twelve terms) and is explicitly marked in the node as
proposed, not design: `00` writes a context-term list for course codes only, and this row copies
that *shape*. R6 owns the term patterns, R4 the organization gazetteer, R5 the one jurisdiction's
coverage-line and form-name values. **No regex and no catalogue contents are written here.**

---

## Neighbours considered that did **not** get an edge

- **`finance.tax-filings`** — no edge. A premium is deductible and an audit result lands in a
  return's workpapers, so the temptation is real. But the two never contest the *same evidence
  item*: a labelled policy-number slot is never on a return, and a labelled tax-year slot is never
  what a declarations page carries. This is a `tax_year`-level question about a *retained copy*,
  and it is the reason `tax_year` is offered as an optional level rather than the reason for a
  collision. Recorded here so R1c does not read the absence as an oversight.
- **`finance.payroll-received`** — no edge. Workers-compensation payroll is an *estimate by class
  code* produced by the firm for a carrier; a payslip is a record an individual receives. No shared
  evidence item, no collision. The employment-side confusion is already carried by
  `career.employment-records`.
- **`legal.practice-matter-file`** — no edge, and this one was close. A law firm's own coverage is
  this node's; a *client's* insurance dispute inside a matter file is that node's. The reason no
  edge was authored is that the contested item is the same one already carried on
  `legal.personal-legal-matters` (carrier + claim number + amount on obligation-shaped prose), and
  duplicating the collision on a second legal row would state the same discriminator twice while
  giving R1c two reciprocals to maintain. If R1c prefers the practice-side row, this is the note
  that says the omission was a choice.
- **`identity`**, **`medical`**, **`legal`** as *schemas* — no edge, by contract. Those joins are
  `also_holds_with`, which is schema-to-schema only; they are recorded per file in
  `file_examples[].also_schema` (`identity` on the renewal submission's employee census,
  `medical` on the loss run and the group health plan, `legal` on the settlement agreement,
  `career` on the certificate and the COI request, `photos` on the portal screenshot).
- **`photos.camera-events`** — no edge, unlike the personal sibling, which needs one for loss
  photographs. A firm's insurance file rarely holds photographs that are not already inside a claim
  group, and inventing the collision to mirror the sibling would be symmetry for its own sake. If
  claim photography turns out to be common, this is the edge to add.

---

## NEEDS-JOSEPH (this node only)

- **NJ-1 — the fixture-8 dimension_order disagreement.** `CONNECTION-EXAMPLES.md` fixture 8 and the
  roster hint both say `institution → record_type → tax_year`. This row recommends
  `institution → account_type → record_type`. Both halves of the change are argued above. Because
  the dispatch prompt says CONNECTION wins on conflict, this needs a ruling: either the fixture's
  ordering is illustrative and R1b's researched order stands, or the fixture is binding on ordering
  too and this row conforms. It is a one-line change either way, and it should be decided **once**
  for all three insurance templates — the personal sibling followed its fixture ordering exactly,
  so the family is currently inconsistent in its treatment of the fixture.
- **NJ-2 — the product has no key for a term scope.** `tax_year` is the only time key on the Finance
  schema and it answers a different question than a policy period, a plan year, a lease term or a
  fiscal year. Three exits exist and none is a template row's to take: mint a shared period-scope
  field (a product-vocabulary decision), encode the term inside `record_type` values (a date inside
  an enum — the D4 shape done badly), or accept that a firm files by carrier and coverage line and
  reads the year off the declarations (what this row recommends today). This is the same gap the
  personal sibling recorded from the household side; it is one decision, not two.
- **NJ-3 — `finance` and `career` need an `also_holds_with`, and currently have only
  `collides_with`.** A certificate of insurance is a coverage record **and** an engagement
  deliverable on genuinely disjoint evidence: the insurers-affording-coverage legend on one side,
  the certificate-holder block and the contract clause on the other. That is `00`'s abstract /
  application shape exactly. It is a schema-to-schema edge, so it cannot be authored on this
  template row; it is R1c's to add reciprocally on `nodes/finance.json` and `nodes/career.json`.
  Recorded here and in the node's `also_holds_with_note` rather than smuggled onto a template.
- **NJ-4 — multi-issuer records: one fact per row, or abstain?** An ACORD certificate names several
  carriers in one labelled legend, so `institution` is genuinely multi-valued on a single file. The
  node refuses to rank the most frequent name (the polished-but-false move) and refuses to invent a
  rule, so it says "one fact per coverage row **or** abstention" and leaves the choice open. This is
  not insurance-specific — it is true of any record issued jointly — and it belongs to P6's values
  table rather than to a template.
- **NJ-5 — is `account_holder` canonical or not?** The `finance` schema row proposes it; the
  canonical list does not carry it. Until it lands, this situation cannot record the named-insured
  role as a fact at all, which means the inversion its `never_alone` list warns about is currently
  prevented only by prohibition rather than by having somewhere correct to put the value. Not this
  node's to resolve; flagged because this situation is where the absence bites hardest.

---

## Refusal

**Not refused.** `refuse_node: false`. The reasoning is in "The node test" above: the row fails the
dimensions half of the test and clears the signals and privacy halves decisively, and the
organizational situation — a document produced *for* a third party, and an annual purpose-coherent
submission packet — is one the personal sibling structurally cannot hold.

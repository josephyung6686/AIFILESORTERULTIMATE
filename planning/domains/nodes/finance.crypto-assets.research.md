# finance.crypto-assets — lab notes (R1b)

Date: 2026-08-23
Roster row: `kind: template`, `schema_id: finance`, `launch: placeholder`, `parent_id: null`.
Output: [`finance.crypto-assets.json`](finance.crypto-assets.json).
Salvage: the JSON existed as an untrusted partial from an interrupted session and had no memo.
This pass verified it line by line, corrected four things, and takes ownership of both files.

## Sources actually used

### Binding local sources

- `planning/domains/dispatch/make_prompt.py finance.crypto-assets` — the stamped assignment.
  It supplied the row metadata, the node test, the research procedure, the output shape, and the
  done-when list this memo is audited against.
- `planning/00-database-agent-product-design.md` — authoritative. Every phrase attributed to `00`
  in the JSON was extracted mechanically and re-matched against this file (see the audit below).
- `planning/prompts/ALIGNMENT.md` — the rule that decided this row's shape twice: work types are
  **values** of `record_type`, never nodes; and a template that would only repeat the Finance
  schema's default is not a node.
- `planning/domains/_CONTRACT.md` — entry shape, D6 snake_case, rule 8's "a template may only
  branch on a field the same entry's schema declares", rule 10 (identity/legal/medical write no
  field rows), rule 12 (a template references its schema's fields and never copies them),
  rule 14's closed edge vocabulary and its schema-only restriction on `also_holds_with`.
- `planning/domains/CONNECTION.md` and `CONNECTION-EXAMPLES.md` — node test, browse-only
  `parent_id`, the activation/grouping firewall, same-kind collisions, residual names.
- `planning/overnight/council/DECISION-BRIEF.md` — **D6** (snake_case), **D4** (`jurisdiction` is
  a value, never a field name and never a destination dimension — the reason no venue form name
  became a key here), **D1** (identity carries protection and no field rows, which is exactly
  what this row's credential refusal relies on), **J-IND** (a `launch: placeholder` row still
  gets real gist-depth research, not hollow coverage). Not re-debated.
- `planning/domains/roster.json` — confirmed the row and every edge endpoint. All seven
  `collides_with` targets resolve to roster ids; all four `also_schema` values resolve to roster
  schema ids; all six `falls_through_to` names are §7.3 residual names.
- `planning/domains/canonical_fields.json` — no key was minted. `account_holder` is referenced,
  not re-declared: it is the Finance **schema row's** proposed search-and-privacy key and is not
  in canonical_fields yet, which is stated in `fields_note` rather than papered over.
- `src/evidence_shape/vocabulary.py` — every `source_type` checked against the fourteen-member
  `SOURCE_TYPES` list mechanically.
- Sibling nodes read for shape and edge alignment: `finance.json`,
  `finance.investment-brokerage.json` (which already names this row in a collision — the edge is
  reciprocated from this side using the same fixture), `finance.tax-filings.json`,
  `finance.receipts-expenses.json`, `identity.credentials-passwords.json` (which carries the
  **same** `recovery phrase backup.jpg` fixture — the two rows now agree on it),
  `photos.screenshot-captures.json`, `finance.small-business-bookkeeping.json`,
  `finance.cap-table-equity.json` and `finance.household-property.json` for house style.

### External, bottom-up reality checks

These establish that the listed files and labelled structures are real. They create no canonical
field, no gazetteer content, no regex, and no threshold.

- Coinbase, [You Can Now Export Your Transaction History](https://www.coinbase.com/blog/you-can-now-export-your-transaction-history)
  — a user-downloadable transaction-history CSV reached through a Statements → Transactions path
  is a real, ordinary artifact. Grounds `exchange_transactions_2025.csv`.
- Uniswap Labs support, [How to download transaction history on Etherscan](https://support.uniswap.org/hc/en-us/articles/29802839428365-How-to-download-transaction-history-on-Etherscan)
  and [Ethereum-Wallet-Transaction-Exporter](https://github.com/imPatidar/Ethereum-Wallet-Transaction-Exporter)
  — an on-chain export is address-scoped and its columns are transaction hash, date/time, from,
  to, transaction type, asset symbol, value and gas fee. This is the evidence behind the
  ON-CHAIN TRANSFER deterministic signal: a **transfer vocabulary in a labelled type column**
  beside a **labelled destination/hash slot holding an opaque string**. Neither half alone.
- [Solscan CSV export](https://info.solscan.io/export-csv-report-on-solscan) — the same export
  shape exists per chain with venue-specific tab names, which is why the recognition rules name
  slot structures and not vendor column spellings.
- Coinbase Help, [IRS Form 1099-DA](https://help.coinbase.com/en/coinbase/taxes/forms-reports/1099da)
  and Kraken, [How to Read Your 2025 Combined Form 1099](https://support.kraken.com/articles/how-to-read-your-2025-combined-form-1099)
  — venues issue a year-end form carrying an explicit labelled tax year, distinct from an
  export's date range. Grounds the tax-year deterministic signal and the "year-end tax form
  issued by a venue" work type. Under **D4** the form's name is a `record_type` **value** from
  one jurisdiction's catalogue; it is never a field name and never a dimension.
- [Ethereum Web3 Secret Storage / keystore format](https://cryptobook.nakov.com/symmetric-key-ciphers/ethereum-wallet-encryption)
  and [keythereum](https://github.com/ethereumjs/keythereum) — geth's keystore filename is an ISO
  timestamp concatenated with the derived address, and the file is JSON whose `version` and
  `address` members are **plaintext** while the secret sits in an encrypted `crypto` object.
  This changed a file example (below): it is the sharpest fixture on the node precisely because
  a stable address-shaped string is readable in both the filename and a labelled slot.

## Did this row survive the node test?

Yes, on all three clauses of CONNECTION.md's test rather than one — which matters, because a
thinner "crypto is a kind of money" framing would have failed it and should have been refused.

1. **Detection signals differ from the Finance default.** The discriminators are the labelled
   destination/transaction-hash slot holding an opaque string, a transfer vocabulary in a
   labelled type column, and the **absence** of the settlement-date + securities-identifier pair
   that every statement-shaped Finance sibling has.
2. **Recommended dimensions differ.** `account_type` is dropped from the standing levels; the
   schema's default order is `institution → account_type → record_type`, this row recommends
   `institution → record_type`. The reason is evidential, not aesthetic: most of this material
   carries no labelled account-descriptor slot, so the level opens a branch the facts cannot
   fill.
3. **Privacy rules differ in kind, not degree.** The neighbouring material is seed phrases,
   recovery sheets and keystores — not weaker finance records but a *different domain's*
   protected material. This row's defining rule is a refusal.

Nothing was invented to keep the row: `fields: []`, `proposed_fields: []`, no new dimension, and
the one place a new key was genuinely tempting is parked in `open_question` instead.

## What I changed in the salvaged draft

The draft was substantially correct and well-evidenced; the corrections are four, and three of
them are contract compliance rather than prose.

1. **`hardhat.config.ts` had `also_schema: "code"`.** Wrong, and wrong in a way the contract
   cares about: `code` is **not** on the finance schema row's `also_holds_with`
   (`medical, academic, legal, identity, photos`), and a Hardhat config is not simultaneously a
   finance record — it is the *collision* fixture, which the row already states in
   `collides_with → code.software-project`. Set to `null`. A co-activation claim and a collision
   claim on the same file are contradictory, and this is exactly the seam where a template row
   quietly widens its schema's edges.
2. **`Crypto Tax Report 2025.pdf` had `also_schema: "identity"`.** Not argued anywhere in the
   file's own `must_not_conclude`, and not what is actually going on: the report's real
   multi-membership is with `finance.tax-filings`, which is the **same schema**, so it is a
   two-group question (`grouping_reasons`) and a collision — never an `also_holds` edge. Set to
   `null`.
3. **`recovery phrase backup.jpg` had `also_schema: "identity"` with photos-schema facts
   (`camera_information`, `capture_year`) in `facts_legal`.** Two problems. The facts asserted
   belong to the Photos schema and are not universals (ALIGNMENT's universal list is file type,
   creation date, language, duplicate family, version family, sensitivity status), so the
   co-activation named had to be the one supplying them. And `identity.credentials-passwords`
   carries this **exact filename** as its own fixture with `also_schema: "photos"`. Aligned to
   `photos`, added `media_type`, and rewrote the fourth `must_not_conclude` line so the photos
   co-activation cannot be read as making the file filable. Identity's claim on it is expressed
   where it belongs — in `collides_with`, as a refusal.
4. **The keystore fixture was factually thin.** It was `keystore-UTC--2026-02-11.json` observed
   as "every value field is an encrypted blob; no readable text". A real V3 keystore is not that:
   its filename is `UTC--<ISO timestamp>--<address>` and `version` and `address` are readable
   plaintext. Renamed to `UTC--2026-02-11T14-22-08.331Z--3f5c...9ad1.json` and rewritten so the
   observations say what is actually on disk, with a new `must_not_conclude` covering the
   plaintext address in both the filename and the labelled member. The corrected fixture is
   strictly harder and strictly more useful: the tempting evidence is now labelled, stable and
   readable, and the correct outcome is still that this row does not fire.

`also_holds_with_note` was rewritten to match (1) and (2) — it had listed both files as
co-activations.

Everything else in the draft was verified and kept: seven collisions, six residual routes, the
`institution → record_type` order with its three optional branch patterns, the eleven
`never_alone` rules, the credential refusal written as a deterministic signal, and
`sensitivity: potentially_sensitive`.

## The organizational situation, bottom up

Twelve file examples, covering the ugly cases the prompt names rather than the happy statement:

| Fixture | Why it is in the list |
|---|---|
| `Exchange Account Statement 2026-Q1.pdf` | the labelled happy case; also the one that must not yield `tax_year` from a quarter token |
| `exchange_transactions_2025.csv` | labelled structure, **no venue string anywhere** — `record_type` resolves, `institution` does not |
| `recovery phrase backup.jpg` | the refusal fixture: OCR'd prose, no labelled record structure, credential-bearing |
| `UTC--2026-02-11T14-22-08.331Z--3f5c...9ad1.json` | encrypted container with a *readable* address; refusal again, harder |
| `Crypto Tax Report 2025.pdf` | the strongest positional evidence is the **wrong role** (a tax tool's letterhead is not an issuer) |
| `Screenshot ….png` | OCR of the same thing a statement says; media-type discipline |
| `Your withdrawal is complete.eml` | mail, labelled slots, one transfer |
| `hardhat.config.ts` | the neighbour's file that looks like ours — code collision |
| `wallet_backup.zip` | the archive packet with mixed members, manifest read without unpacking |
| `Holdings.xlsx` | unlabelled-ish hand-kept sheet referencing many venues and belonging to none |
| `IMG_5502.png` | the sparse file where the correct activation set is **empty** |
| `Order confirmation - hardware wallet.eml` | the wallet-word false positive that is a retail receipt |

Two of the twelve carry `group_without_copying_facts: true` for the reason `00` gives directly —
`exchange_transactions_2025.csv` may sit in the account neighbourhood without receiving the
statement's `institution`, and `IMG_5502.png` sits beside two wallet screenshots and receives
nothing at all.

## Field decisions and `proposed_fields`

**`proposed_fields` is empty, deliberately.** `fields` is empty because rule 12 forbids a
template copying its schema's list. The legal set on any file this row recognizes is the Finance
schema's `institution`, `account_type`, `tax_year`, `record_type`, plus that row's proposed
`account_holder`, plus the universals.

The two strings this material is saturated with are deliberately **not** fields:

- **a wallet address.** There is no canonical key, and minting one would immediately raise
  whether it may be a folder level — where the answer is no, because a directory named for an
  address publishes an identifier on the filesystem of a domain `00` requires to be protected.
- **an asset ticker.** It is the single worst `never_alone` on the node: the same three-to-five
  character uppercase shape is an airport code, a gene symbol, a currency code, a standards
  abbreviation and a filename stub. It is evidence, and at most a value inside content — never a
  key.

`proposed_context_terms` (ten of them) are candidates for R6 and are marked PROPOSED, not design.
`00` states the pattern-plus-context **shape** for course codes only; it does not list these.
The last term, `recovery phrase`, is listed because its correct outcome is a refusal to fire.

## Dimension order and the three optional branch patterns

`institution → record_type`, `time_first: false`.

Recommended, not frozen — `00` lets the user reverse, remove, add or flatten. `account_type` is
dropped and `tax_year` is not a standing level; the tax-year-first ordering belongs to the
`finance.tax-filings` sibling, and duplicating it here would scatter one venue's series across
calendar folders. The three optional branches are (a) a `tax_year` leaf **under** `record_type`
for the year-scoped subset that carries its own labelled tax-year slot; (b) `account_type`
restored, returning to the schema's default, where a labelled account-descriptor slot genuinely
exists; (c) **no `institution` level at all** for the self-custody subset, because there is no
issuing organization and inventing one would be a fabricated fact.

Every level named is a field the Finance schema declares (rule 8's second half). `account_holder`
is never a dimension — `00` forbids authorship or creator identity as a destination.

## Neighbours considered that did **not** get an edge

- **`identity.core-documents`** — the masked taxpayer-identification block on a year-end form and
  a gain-loss report is identity-adjacent, but the discriminating evidence never collides: core
  documents are the *document itself*, not a slot on someone else's record. The protection
  outcome that matters is already carried by the `identity.credentials-passwords` collision.
- **`career.*`** — a token grant or a crypto-denominated payroll line is real, but it is
  `finance.payroll-received` and `finance.cap-table-equity`'s evidence, both of which already
  have their own rows; adding a third claimant would give one evidence item three homes.
- **`legal.*`** — an exchange's terms notice is a notice, not an executed agreement. No shared
  discriminating evidence.
- **`finance.investment-brokerage` as `also_holds_with`** — rejected. A file is a securities
  record **or** a digital-asset record on the discriminating pair; it is not both at once, so it
  is a collision, and a collision it already is from both sides.
- **`travel.*`, `photos.camera-events`** — no shared evidence beyond capture properties that
  `photos.screenshot-captures` already covers.
- **`role_split`** — empty, and this is the interesting refusal. The split this material most
  wants is *the venue that ISSUED a record* against *the tax tool that PRODUCED it*, both sitting
  in a page-one letterhead. There is no canonical producer-side key to split against, and minting
  one to solve a single template's problem is precisely the move that produced thousands of
  private field names in the overnight pass. Recorded in `must_not_conclude` on the tax report
  instead.

## Files considered and rejected from the kept corpus

- **an NFT image file (`.png` from a collection)** — the image is a picture; the *record* is the
  purchase or transfer document, which is already covered. Adding the artwork would have made
  this row a photo domain by the back door.
- **a hardware-wallet firmware binary / installer** — `opaque_binary` with no record structure.
  It is software, and `Unsupported or Encrypted` handles it without this row.
- **a blockchain node's chaindata directory** — bulk machine state, not a personal record; it is
  the kind of thing `00` routes to metadata-only indexing.
- **a `.ics` calendar entry for a token unlock** — a `SOURCE_TYPE`, and an event, not a record of
  an account. Nothing here would fire on it that the schema's default would not.
- **a Discord/Telegram export from a project community** — messaging material; it belongs to the
  messenger-export row and carries no account or transfer structure.
- **a whitepaper or research note about an asset** — kept, but as a `needs_llm` case
  (a document that *discusses* an asset rather than reporting a holding), not as a file example,
  because its correct destination is a reading residual and it teaches nothing this row owns.

## Sparse-file discipline

`IMG_5502.png` is the `HW 3.pdf` of this node: it sits beside two wallet screenshots, it has no
EXIF, and the neighbourhood is the *only* thing suggesting a domain. It is marked
`group_without_copying_facts: true`, its `facts_legal` is the universals only, and its
`must_not_conclude` quotes `00` on both halves — the graph does not copy missing facts onto
sparse files, and the absence of EXIF is not proof of a screenshot.

## Audits run before returning

- `python3 -m json.tool` — parses.
- All fifty-nine quoted spans of fifteen characters or more were extracted from the JSON and
  matched against `00` under whitespace/curly-quote normalization. Fifty-seven matched verbatim.
  The two non-matches are artifacts of the extractor splitting on nested quotation marks (they
  are the connective prose *between* two quoted spans, not quotations); both were read by hand.
  **No `00` quotation in this node is fabricated or paraphrased inside quote marks.**
- Every `file_examples.source_type` is in `SOURCE_TYPES` (12/12).
- Every `collides_with.domain` is a roster id (7/7); every `also_schema` is a roster schema id;
  every `falls_through_to.residual_template` is one of §7.3's nine names (6/6).
- `also_holds_with` and `role_split` are empty **by contract**, each with a note saying why.
- No number in the file is a threshold, a score or a count of evidence — the digits present are
  filenames, years inside fixture names, and prose references.
- No handling class is assigned; `sensitivity` is `potentially_sensitive` only.
- Only the two assigned files were written.

## NEEDS-JOSEPH (this node only)

- **NJ-CRYPTO-1 — self-custody has no `institution`, and nothing in the canonical vocabulary can
  say so.** The Finance schema gives `institution` the issuer role. A person holding assets in
  their own wallet has no issuing organization, so a real and common half of this material cannot
  open the first recommended level while the exchange half opens it cleanly. Three answers, three
  different products: (a) the self-custody subset carries no `institution` and sits at
  `record_type` or under a scoped fallback — what the row recommends today, encoded as optional
  branch (c); (b) a custody-mode distinction is read into `account_type`, which loads that field
  with a meaning it was not defined to carry; (c) an account-identity or custody key is minted on
  the shared vocabulary — a decision about the product's field table that one template row must
  not make, and one that immediately raises whether a wallet identifier may ever be a folder
  level (this row's answer: no). **Recorded, not resolved. No field was proposed.**
- **NJ-CRYPTO-2 — which residual owns an encrypted wallet container.** `Protected Records` names
  "credentials" outright; `Unsupported or Encrypted` names the format. Both fit a keystore. The
  row states a preference (Protected Records, because the credential nature is the load-bearing
  fact and the format is incidental) and routes merely-unreadable containers with no credential
  evidence to `Unsupported or Encrypted`. Confirm, or invert.
- **NJ-CRYPTO-3 — `account_holder` is referenced by this row but is not in
  `canonical_fields.json`.** It is the Finance schema row's proposal. Three file examples list it
  in `facts_legal`. If R1c does not promote it, those three lines must change. Flagged rather
  than silently depended on; not this row's decision to make.

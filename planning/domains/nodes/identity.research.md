# identity — lab notes (R1b, kind: schema)

Date: 2026-08-22
Output: [`identity.json`](identity.json). Roster row: `identity`, `kind: schema`, `launch: safety`,
`is_safety_domain: true`, `inherited_field_keys: []`.

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. It is the only thing quoted.
  Every quoted span in `identity.json` was matched mechanically against this file before the file
  was written, and again after each edit (56 spans, 0 unverified). The one non-`00` quotation
  (`Crosses identity and legal safety domains`) is attributed in-line to `roster.json` and was
  verified against it.
- `planning/01-product-design-structured.md` — §3.15 (domain library scope at launch) and
  §7.2–7.3 (residual library, the nine names and their `00` spellings). Nothing quoted from it;
  `00` wins and `00` carries the same sentences.
- `planning/domains/_CONTRACT.md` — rules 5, 10, 14, 15 are the ones that shaped this row.
- `planning/domains/CONNECTION.md` — §2 node test, §4 activation (steps 2 and 5 especially),
  §5 closed edge vocabulary and its invariants, §11 PR-1/PR-2/PR-4/PR-6/PR-8.
- `planning/domains/CONNECTION-EXAMPLES.md` — fixture 4 (passport scan) is this node's spine;
  fixtures 3, 5 and 6 supplied never-alone material.
- `planning/prompts/ALIGNMENT.md`.
- `planning/domains/canonical_fields.json` — every `facts_legal` entry in every file example
  resolves to a key in it (checked mechanically; 0 non-canonical).
- `src/evidence_shape/vocabulary.py` `SOURCE_TYPES` — every `source_type` used is a member
  (checked mechanically).
- Landed neighbour nodes: `photos.json`, `college_applications.json`, `code.json`, `career.json`,
  `academic.json`. Read for edge alignment only; none rewritten.

## The node test — why this row is NOT refused despite declaring zero fields

The dispatch prompt says to refuse a `kind: schema` row that cannot name a distinct 3–6 field set.
Read alone, that would refuse `identity`. It is overridden, and the override is recorded rather
than assumed:

- `_CONTRACT.md` rule 15: *"A placeholder schema (career, identity, medical, legal) may carry
  `schema: []` — a row may describe the domain and still write no field rows (rule 10 stands)."*
- `CONNECTION.md` PR-6 names identity in the same breath.
- `CONNECTION-EXAMPLES.md` fixture 4 pins the row itself as binding data:
  `{"id": "identity", "kind": "schema", "is_safety_domain": true, "schema": [],
  "note": "placeholder — writes no field rows (D1 as narrowed)"}`.

CONNECTION beats the dispatch prompt by its own precedence clause, and a refusal would make a
binding fixture inexpressible — the explicit test of a wrong roster. So: `refuse_node: false`,
`fields: []`, `proposed_fields: []`. **This is the recorded conflict the prompt asked me to note.**

`proposed_fields` is deliberately empty. Minting `document_number` / `nationality` /
`issuing_authority` would reverse S3/D1 as a plan edit, which rule 10 forbids in terms. The
question of whether identity ever gets fields is in `open_question` instead — where career put the
same question.

## Files considered and rejected

Twelve file examples shipped. Rejected candidates and why:

- **A tax return (1040 / W-2).** Genuinely identity-adjacent (it carries a national ID number) but
  it is the finance node's file, and using it here would have made the finance collision argument
  from the wrong side. The join survives as `also_holds_with: finance` instead, argued from
  `00`'s two list sentences that name identity documents, account statements and tax records
  together.
- **A health insurance card.** Carries a member ID and a photo, so it is a real identity/medical
  crossing — but both sides are field-less placeholders, so the edge would carry nothing but a
  second copy of the protection statement. Left out; see "neighbours with no edge" below.
- **A `.eml` with a passport scan attached.** `email` stayed in `file_kinds.source_types`
  (`00` treats mail content as potentially sensitive, and an emailed ID is common) but the example
  would have repeated the scan example with an envelope around it, and the interesting evidence
  (the attachment) is already covered.
- **A selfie holding an ID up to camera** (a KYC liveness photo). Real, and a nasty case, but it is
  the `IMG_2231.jpg` collision argument again with a worse OCR story.
- **A `Travel/Gate B12`-shaped boarding pass.** That is `00`'s named residual anti-pattern and
  belongs to Receipts and Confirmations, not here. A boarding pass carries a passenger name and a
  document-number-shaped run, which makes it a *never_alone* argument — folded into the
  "person's full name" and "bare number" entries rather than given a row.

The twelve that shipped deliberately cover: a labelled form (`I-20`), unlabelled prose-free card
OCR (`IMG_2231.jpg`), the scan-of-the-same-thing case (`passport scan.pdf`), an archive-shaped
opaque container (`backup.kdbx`), a contacts file, a spreadsheet, a `code_structured` file, a
packet member (`ID.pdf`), an abstain case (`Scan_20260412_0001.jpg`), and **two collision
fixtures that look like this domain and are not** (`Statement Mar 2026.pdf` → finance,
`Nursing License 2026.pdf` → career).

## proposed_fields justification

None proposed — see above. One thing was proposed that is *not* a field and is labelled as such
in the JSON: two **detector families** under `recognition.deterministic`, marked `PROPOSED`
in-line — the machine-readable travel-document band, and the credential-cluster column header row.
`00` names neither. They are named as families so R2/R6 can decide whether they ship; no regex,
no term list, no gazetteer contents are written here (R2/R4/R6 own those).

## Neighbours considered that got NO edge

- **`medical` — `also_holds_with` refused, `collides_with` written.** The health-insurance-card
  crossing is real, but an also-holds between two field-less placeholders would assert only "both
  are protected", which `is_safety_domain` already says; PR-8 routes healthcare insurance through
  the finance templates anyway. The **collision** is different and does carry weight:
  `medical.json` landed mid-task naming identity on exactly the item this node's first
  `never_alone` is about — a person's name beside an identifier number. That edge was one-way, so
  it is reciprocated here.
- **`academic`** — an `I-20` names a school and a transcript names a person; both are
  name-plus-institution shapes. But `00`'s discriminating rule for academic is the course-code +
  academic-context pair, which never appears on identity material, so there is no evidence item
  the two could fight over. The university-name-alone trap is already handled inside the file
  example's `must_not_conclude` and in `never_alone`, which is where it belongs — that is a
  never-alone rule, not a collision.
- **`research`, `photos.*` templates, `travel.*`** — no shared evidence item.
- **`career`** got `collides_with` but **not** `also_holds_with`. A professional licence is one or
  the other, not both; the file is career material with an identity-document *shape*. Writing
  also-holds there would have licensed one evidence item to count twice, which is the exact thing
  the collision edge exists to stop.

## Reciprocity status (for R1c)

Re-scanned every landed node file at the end of the task. Already reciprocal:

- `photos` → `identity` `collides_with`. ✔
- `college_applications` → `identity` `also_holds_with`. ✔
- `code` → `identity` `also_holds_with`. ✔
- `finance` → `identity` **both** edges — written independently by that node's author and landing
  on the same discriminator (an account record issued by an institution about an account vs a
  document that identifies a person). ✔
- `legal` → `identity` **both** edges, likewise independently converged. ✔
- `medical` → `identity` `collides_with` — landed mid-task and was one-way; reciprocated here. ✔

Both pairs that carry `collides_with` **and** `also_holds_with` (finance, legal) have a non-empty
`signal` on the collision side, as CONNECTION §5 invariant 1 requires.

**Owed by the other side, R1c to reconcile:**

- `career` ↔ `identity`: `collides_with` (professional licence vs government ID). `career.json`
  was already written without it and must not be rewritten by me — this is the one one-way edge
  this node leaves behind.

## Two findings worth carrying up, not just filing

1. **For identity, the folder name is the disclosure.** Every other domain's template debate is
   about retrieval. Here, a path ending in `Passport` or `Visa Denial` publishes its contents to
   anything that can read the tree — Finder, Spotlight, a sync agent, a backup, a shared screen —
   without ever opening the file. `00` draws this line at the UI (*"a visible list of passport
   filenames on a shared screen may not be"*, and Protected Records *"must not cause filenames or
   content to be exposed in model prompts"*) but says nothing about the filesystem shape. That is
   why `template.dimension_order` is empty here for two independent reasons, and why the
   recommendation is recorded as prose: one flat protected area, depth only by explicit user
   action. **The depth question is Joseph's** — see NEEDS-JOSEPH below.
2. **The `needs_llm` list is written against a closed door.** `00` keeps protected material out of
   cloud prompts by default and PR-2 puts P7 classification before any model path — yet the
   hardest recognition problems in this domain (an unlabelled OCR'd card, a foreign-language civil
   record, a photographed recovery phrase) are exactly the ones that want a model. Each entry
   therefore carries a standing constraint: local-model or explicit consent, never a cloud
   dossier. If that constraint is wrong, every `needs_llm` entry on this node changes meaning.

## Contract compliance, mechanically checked

- 12 file examples; every `source_type` ∈ `SOURCE_TYPES`; every `facts_legal` key ∈
  `canonical_fields.json`; no filename contains a path separator; no file example asserts a folder
  path (each one lists "a folder path" under `must_not_conclude`).
- Every `collides_with` / `also_holds_with` / `also_schema` id exists in `roster.json`.
- Every `falls_through_to` and `falls_through_if_inactive` value is one of §7.3's nine names in
  `00`'s spelling.
- No thresholds, no scores, no handling class. The only digits in the file are document references
  (`00`, `_CONTRACT` rule 15, CONNECTION §5, PR-n, D1, and the `(1)(2)(3)` enumerators in
  `open_question`).
- `sensitivity: potentially_sensitive` — `00`'s phrase only.
- `role_split: []` — role_split joins *field keys*, and this schema declares none.
- `parent_id: null`; not authored (PR-5: R1b never authors it).
- `is_safety_domain` is **not** written on the node. It is a `_CONTRACT` rule-15 row attribute,
  `roster.json` already carries it for this id, and the dispatch output shape does not include it.
  `career.json` set the same precedent. Flagged so R1c folds it in from the roster rather than
  reading its absence as a denial.

## NEEDS-JOSEPH — identity only

1. **May the protected area carry any folder depth at all?** For this material the path itself
   discloses content, so the usual "the user can add levels later" answer has a privacy cost no
   other domain pays. `00` is silent on the filesystem shape and explicit about the UI, so this is
   not derivable from the design. This row recommends one flat area and writes no
   `dimension_order`; it does not decide the question.
2. **Does identity ever get field rows when D1's deferral lifts** (career's fields are owed before
   P10; identity's are not owed at all)? A `document_number` or `nationality` field would store the
   single most sensitive value in the corpus in a queryable column — an argument against extraction
   that no other domain has to make. This is NJ-2 landing on the one domain where the answer might
   legitimately be "never".
3. **May a local model ever see this material, and under which of `00`'s four operation modes?**
   The whole `needs_llm` list depends on the answer.

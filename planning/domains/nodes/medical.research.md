# medical — R1b lab notes

Node: `medical`, `kind: schema`, `launch: safety`, `is_safety_domain` (roster).
Output: [`medical.json`](medical.json). No other file was written.

---

## Sources used

- `planning/00-database-agent-product-design.md` — read in full; authority. Every span in quote
  marks in `medical.json` was `grep -cF` verified against it before it was written, then the
  finished file was re-scanned mechanically: 39 distinct quoted spans, all present verbatim, zero
  misses. No quotation is paraphrased inside quote marks, and the one PR-8 sentence that comes
  from `CONNECTION.md` rather than `00` was rewritten as plain prose so no quote mark can imply
  the wrong source.
- `planning/01-product-design-structured.md` — §3.15 only (the safety-domain sentence's numbered
  rendering, lines 555–573), used as a locator. Nothing is quoted from it.
- `planning/domains/_CONTRACT.md` — rules 5, 8, 10, 11, 14, 15 are the ones that bind this row.
- `planning/domains/CONNECTION.md` — §2 node test, §4 steps 2/3/5/9, §5 edge table + invariants,
  §7, PR-2, PR-4, PR-6, PR-8.
- `planning/domains/CONNECTION-EXAMPLES.md` — fixtures 4 (passport / safety split), 5 (`.ics`),
  8 (insurance: one field vocabulary, three templates, and the `finance ↔ medical`
  `also_holds_with` this node reciprocates).
- `planning/prompts/ALIGNMENT.md`; `planning/domains/roster.json` (row confirmed, plus the three
  `schema_id: medical` template rows and the `finance.insurance-healthcare` row that names this
  edge); `planning/domains/canonical_fields.json` (no medical key exists — correct);
  `src/evidence_shape/vocabulary.py` (`SOURCE_TYPES`).
- Landed neighbours read for edge alignment, not rewritten: `nodes/academic.json`,
  `nodes/career.json`, and — landing mid-task — `nodes/finance.json`, `nodes/identity.json`,
  `nodes/legal.json` (see the reciprocity table below). `career.json` is the precedent this row follows most closely — the other
  field-less placeholder schema that still carries recognition, work types and a stated-empty
  template.

## The node test, and why this is not a refusal

The dispatch prompt says refuse a `kind: schema` row when you cannot name a distinct 3–6 field
set. Taken alone that would refuse this row. It does not, because three documents that outrank the
prompt require the row to exist **with no fields**:

- `_CONTRACT.md` rule 15: "A placeholder schema (career, identity, medical, legal) may carry
  `schema: []` — a row may describe the domain and still write no field rows."
- `CONNECTION.md` PR-6: placeholder schemas exist as `kind: schema` rows with an empty field list.
- `00` itself makes the row load-bearing: safety domains are what the product "detects and
  protects … before any cloud or automated placement decision is allowed", and
  `CONNECTION.md` §4 step 5 makes `is_safety_domain` activation the thing that runs P7 first.

So the row's content is **detection and protection**, which is a genuinely distinct job, not an
empty industry label (the thing §2 actually forbids). What is refused instead is the field set:
`fields: []`, `proposed_fields: []`, `role_split: []`, `template.dimension_order: []`. Nothing was
padded to make the node look full.

## `proposed_fields` — deliberately empty

I considered proposing `subject_of_record` (whose body the record is about), `provider`,
`record_type` reuse, and `date_of_service`. All four were dropped:

- D1 as narrowed forbids medical field rows, and PR-6 repeats it. A "proposal" that names four
  keys is the same reversal arriving as a plan edit — `_CONTRACT.md` rule 10 says that must be
  explicit, not smuggled.
- `record_type` reuse is not obviously safe: its canonical row is scoped to a *financial* record
  kind ("statement, receipt, invoice, policy, claim"). Reusing it would make one column mean two
  things, which is the D6 defect in a different costume.
- The one field that most distinguishes this material — the person the record is about — is a
  person, and `00` warns off person-identity as a destination dimension. That is a design
  decision, not a research finding.

The question is recorded in `open_question` instead.

## Files considered and rejected

Kept 15 examples; these were considered and left out:

- **Veterinary records** (`Fluffy - discharge instructions.pdf`). A real drawer in real corpora and
  a perfect false positive for every clinical structure signal — but the subject is not a person,
  no roster neighbour holds it, and inventing a "who is the patient" test here would be authoring
  a detector (R2's job). Flagged for R2/R3 rather than fixtured.
- **A gym / fitness plan PDF and a nutrition label photo.** Same false-positive family as the
  anatomy deck; the deck is the stronger fixture because its clinical density is total and it
  still must not activate. Covered by `never_alone` item 1 instead of a 16th example.
- **A password-protected medical ZIP.** Tempting for `falls_through_to: Unsupported or Encrypted`,
  but if it cannot be read, medical never activates, so it is not this node's file — it is a
  residual case. Excluded on purpose; see the residual note below.
- **A `.vcf` for a physician.** `00` settles it already ("should normally be privacy-protected
  rather than used to create folder proposals") and `career.json` already fixtures the shape.
  Nothing medical-specific would be learned.
- **A pharmacy loyalty receipt.** Folded into the `never_alone` drug-token line rather than given
  its own row; the EOB is the better finance-collision fixture because both sides genuinely fire.
- **An audio consultation recording** (`audio_video`). Real, but `00` gates transcripts behind "an
  explicit privacy and compute policy", so without a transcript there is nothing but duration —
  the file would teach only "abstain", which `BP log.csv` already teaches more sharply. I therefore
  did **not** declare `audio_video` in `file_kinds`.

## `falls_through_if_inactive` on a safety node — a semantics note for R1c

For an ordinary domain that field records a designed home. For this node it records the **cost of
a miss**: if medical does *not* fire on `Explanation of Benefits - Feb 2026.pdf`, the file lands in
`Receipts and Confirmations`; a missed portal screenshot lands in `Temporary Screenshots`; a missed
lab result lands in `Independent Records`. Each of those is an *unprotected* home, which is exactly
the leak `is_safety_domain` exists to prevent. The designed home when medical **does** fire is the
single `falls_through_to` entry, `Protected Records` (PR-4). I did not list a second
`falls_through_to`: adding `Independent Records`, `Receipts and Confirmations` or `Review Later`
there would authorise moving protected material into a home `00` does not keep local-only.

## Neighbours considered that did NOT get an edge

- **`photos`** — appears as `also_schema` on the medication-bottle photo, but no schema-level
  `also_holds_with` was authored. The join there is one file carrying camera EXIF *and* an OCR'd
  label; that is the photos schema doing its own job on its own evidence, and `photos.json`
  already lists `medical` nowhere. Asserting the pair would claim a standing co-activation that
  only holds when OCR happens to find a label. Left to R1c if the merge wants it.
- **`college_applications`** — a health form inside an admissions packet is real, but the packet is
  a *purpose* join (PR-1 keeps `purpose` inside applications), and the medical side contributes
  protection, not facts. `academic` already carries the school-form crossing, so a second edge
  would be the same claim twice.
- **`code`** — a health-app export is `code_structured` by `SOURCE_TYPE` only. Format is not a
  domain (fixture 5); no edge.
- **`identity`** — collision only, no `also_holds_with`. A coverage card is a coverage artifact
  that happens to identify someone; the identity roster row's remit is core documents,
  credentials, immigration. If `identity.core-documents` disagrees, that is R1c's reciprocity
  pass, and I did not pre-empt it.
- **`travel.bookings-confirmations`** — medical travel / vaccination-for-travel was considered and
  rejected as a values-level coincidence, not a schema join.

## Edges authored one-way — R1c owes reciprocity

`_CONTRACT.md` rule 14 makes `collides_with` and `also_holds_with` reciprocal on kind-bearing
entries. Of my edges, only one already exists on the other side:

`finance.json`, `identity.json` and `legal.json` landed while this node was being written; I read
their edges after writing mine and did not edit them. Three of my edges reciprocate exactly, with
no coordination:

| My edge | Other side, as landed | State |
|---|---|---|
| `also_holds_with: finance` | `finance.also_holds_with: medical` ✔ | reciprocal |
| `also_holds_with: legal` | `legal.also_holds_with: medical` ✔ | reciprocal |
| `collides_with: identity` | `identity.collides_with: medical` ✔ | reciprocal |
| `collides_with: finance` | `finance` collides with career/identity/legal/photos, **not** medical | one-way — R1c decides |
| `also_holds_with: academic` | `academic.json` landed without it | one-way — R1c decides |
| `collides_with: academic`, `collides_with: research`, `also_holds_with: research` | neighbours landed/not-landed without it | one-way — R1c decides |

On the one that matters: I kept `collides_with: finance` **and** `also_holds_with: finance` on the
same pair. `CONNECTION.md` §5 invariant 1 explicitly permits both, at the price of a non-empty
discriminating `signal` on the collision — which this row carries. They answer different questions:
the EOB co-activates (disjoint evidence, both readings true), while the insurer NAME on it is a
single evidence item that must not count for both sides. Dropping the collision would let one
gazetteer hit activate finance and medical at once, which is the thing §4 step 3 exists to stop.

## Two claims marked `inference`, not `design`

1. **The never-alone rule for a hospital or insurer name.** `00` writes its name-alone sentence
   about a *university* ("Columbia can appear as an authoring school, course provider, target institution,
   employer, research venue, or merely a cited organization"). The six-role ambiguity plainly
   transfers — a hospital is an employer, a research site, a teaching institution, a billing
   counterparty — but `00` does not say so, so the entry says the quote is about a university and
   labels the extension.
2. **`also_holds_with: finance`.** This is CONNECTION's PR-8, a *provisional* rule, not a sentence
   in `00`. Recorded as `inference` with PR-8 named, so a reversal is traceable.

Every `deterministic` entry names a *structure* (a labelled slot set, a table row shape, a manifest
shape). None names a regex, a gazetteer's contents, a score, or a threshold. The proposed clinical
vocabulary is isolated in `proposed_context_terms` and explicitly not attributed to `00` — `00`'s
only literal term list is the five academic context words.

## NEEDS-JOSEPH — medical

- **NJ-medical-1 (a sharpening of NJ-2).** When the medical detector fires, may the matched
  clinical text be stored in the local evidence table like any other observation, or should
  detection store only a protected marker plus a location? `00` keeps everything local either way,
  but a stored diagnosis string is a much larger local surface than a "this is medical" flag, and
  every later dossier builder reads that table. This is the one decision that changes what the
  detector is allowed to *be*, and it is upstream of any field question.
- **NJ-medical-2.** If D1's deferral lifts, which canonical keys does medical get, and does it need
  a holder-versus-subject `role_split`? The distinguishing fact of this material is whose body it
  concerns, and `00` disfavours person-identity as a destination dimension. Until this is answered
  the row's `role_split` stays empty rather than guessed.
- **NJ-medical-3.** `template.dimension_order` is empty for two independent reasons (no declared
  fields; and a medical branch's own labels would leak). Confirm the second reason is policy: if
  medical fields ever land, is a medical folder branch permitted at all, or does this material stay
  in a flat protected area regardless of what facts exist? Answering "flat regardless" would make
  this the first schema whose fields are deliberately never destination-eligible.

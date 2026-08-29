# `legal` — R1b lab notes (schema row)

Date: 2026-08-22 · Roster row: `legal`, `kind: schema`, `launch: safety`, `is_safety_domain: true`
Output: [`legal.json`](legal.json)

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every span in quote marks in
  `legal.json` was grep-verified against this file before it was written; a mechanical re-check of
  all 42 quoted spans passes with zero non-verbatim hits. Two spans I had originally quoted came
  from CONNECTION.md, not `00` (PR-6's empty-field-list clause, PR-8's medical co-activation
  clause); both failed verbatim matching because of markdown backticks, and both were rewritten as
  unquoted attributions rather than left inside quote marks.
- `planning/01-product-design-structured.md` — §3.15 (safety-domain launch scope), §7.3 (the nine
  residual names and Protected Records' row), §8.4 (privacy/consent) as locators only. `00` wins.
- `planning/domains/_CONTRACT.md` — rules 5 (sensitivity phrase only), 8 (snake_case; D6
  ratified), 10 (**no career, identity, medical or legal field rows**), 11–15, and specifically
  rule 15's sentence, which begins "A placeholder schema (career, identity, medical, legal) may
  carry" and goes on to permit an empty `schema` field list.
- `planning/prompts/ALIGNMENT.md` — "Identity / medical / legal are **safety domains first**."
- `planning/domains/CONNECTION.md` (§1, §2 node test, §4 activation steps 2/5/9, §5 closed edge
  vocabulary + invariant 1, §6 fields, PR-2, PR-6, PR-8) and
  `CONNECTION-EXAMPLES.md` (fixtures 3, 4, 5, 6, 8).
- `planning/domains/roster.json` — confirmed my row and the four **legal templates** that are other
  agents' rows: `legal.personal-legal-matters`, `legal.estate-planning`, `legal.leases-agreements`,
  `legal.practice-matter-file`. I wrote none of their content.
- `planning/domains/canonical_fields.json` — 37 keys. **No legal-ish key exists** (no matter,
  counterparty, instrument kind, party). That is consistent with D1, not an oversight to fix.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` (all 14 checked against my file examples).
- Landed neighbour nodes: `career.json` (authors `also_holds_with: legal` — I reciprocate),
  `code.json`, `photos.json`, `academic.json`, `college_applications.json`, `research.json`.
  `finance.json`, `identity.json` and `medical.json` landed while I was writing, and I re-checked
  against them: **every edge I authored is already reciprocal except one.** finance names
  `collides_with: legal` + `also_holds_with: legal`; identity names both; medical names
  `also_holds_with: legal` and no collision (I likewise author no `collides_with: medical`);
  career names `also_holds_with: legal`. Their discriminators converged independently on the same
  structural test I wrote — finance's "a labelled account / period / balance structure reporting on
  an existing account is finance; parties, recitals, numbered clauses and an execution block
  creating an obligation is legal", identity's prove-your-identity-to-a-checkpoint versus
  records-a-proceeding. The one **one-way** edge is `collides_with: code`, since `code.json`
  landed earlier without a legal edge; R1c owns that reciprocity.
- `planning/deferred-catalogues/` — **not consumed.** My recognition does not need an existing
  catalogue: there is no court/firm gazetteer to cite, and inventing one would be R4's job (and a
  jurisdiction commitment D4 forbids). Instrument-kind terms are marked PROPOSED and left to R6.

## Why this node is not refused

The prompt's node test refuses a `kind: schema` row that cannot name a distinct 3–6 field set.
Taken alone that would refuse `legal`. It does not, because the contract answers the question
above the prompt's head: `_CONTRACT.md` rule 15 — "A placeholder schema (career, identity, medical,
legal) may carry `schema: []`" — and rule 10/PR-6, under which this catalogue writes **no** career,
identity, medical or legal field rows. `career.json` is the landed precedent: `refuse_node: false`,
`fields: []`. The row is not hollow: it carries eight detection signals, ten never-alone rules,
fourteen worked files, three collisions, four also-holds joins, five residual fallthroughs and a
sensitivity basis. What it does not carry is fields, and that is the recorded decision, not a gap
I filled.

I deliberately wrote **`proposed_fields: []`**. Proposing legal field keys is how D1's narrowing
gets reversed by accident — a `proposed_fields` row reads as a plan edit rather than as the
explicit reversal `_CONTRACT.md` rule 10 demands. The substance of what fields would be needed, and
why none of the 36 canonical keys can be reused for them, is recorded in `open_question` instead.

## Files considered and rejected

| Considered | Verdict |
|---|---|
| `Marriage Certificate.jpg` | Cut as an example; kept as the *reason* for the `also_holds_with: identity` join. It would have duplicated the passport fixture's lesson with a weaker discriminator. |
| `Power of Attorney.pdf`, `Trust Deed.pdf` | Cut — same structure as the will scan and the lease. They are `legal.estate-planning`'s and `legal.leases-agreements`' material to work through, not the schema row's. |
| `matter-2019-0087/` folder of practice files | Cut — that is `legal.practice-matter-file`'s row, and a schema-level fixture there would pre-empt another agent. |
| Court-reporter audio, deposition video (`audio_video`) | Cut — real, but the honest answer is that `00` gates transcripts behind "an explicit privacy and compute policy", so the file would activate on nothing today. Leaving `audio_video` out of `file_kinds` is more truthful than listing it. |
| `contacts` / `.vcf` for opposing counsel | Cut — `00` keeps contact data privacy-protected rather than a proposal basis, and `identity.core-documents` already owns `contacts` as `file_kind_owner` in the roster. |
| A notarized document as `design_creative` or `presentation` | Rejected as format-fishing; the extension list already carries the never-alone flag. |

**Files kept because they are the ugly cases:** the will as a text-layerless scan (`ocr`), the
e-filing screenshot (`ocr`, missing EXIF), the encrypted estate archive (`archive`, unreadable),
the unlabelled `letter to landlord.docx` (needs_llm), the closing packet (`archive` manifest),
and the three false friends below.

## The three false friends — this node's real research

A schema whose whole job is protection is worth exactly as much as its false-positive discipline.
Instrument vocabulary is everywhere in a normal corpus, so most of my work went here:

1. **`LICENSE.txt` at a repository root.** Grant-and-warranty language, no bound party pair, no
   execution. At corpus scale this is the single largest false-positive class. The discriminator is
   already in `00` — reject descendants of software project roots indicated by `package.json`,
   `requirements.txt`, `Cargo.toml`, `go.mod`. Authored as `collides_with: code` (one-way today;
   `code.json` is landed and does not name `legal` — R1c's reciprocity work) and as never-alone
   rule 1. Its `falls_through_if_inactive` is `null`, not a residual name: the file belongs with its
   repository, so no residual home is ever reached. That is the only null in the fourteen.
2. **`Terms of Service.pdf`.** Boilerplate the holder merely saved. Clause numbering, governing law,
   limitation of liability — and the reader addressed as "you" rather than named as a party. Kept
   as a file example with `download_session` as its only interesting universal fact, so the session
   rule gets a fixture too.
3. **`Mortgage Statement - Mar 2026.pdf`.** The finance collision fixture: a mortgage *is* a legal
   instrument, and the periodic statement it generates is not. Structural discriminator — a
   labelled account/statement table versus a party recital plus execution block. This pair carries
   both `collides_with` and `also_holds_with`, which CONNECTION §5 invariant 1 permits **only** with
   a non-empty `signal` on the collision; it has one.

The identity collision uses `00`'s own passport fixture (CONNECTION-EXAMPLES 4) so the two safety
domains do not drift apart on the same bytes.

## proposed_fields justification

None proposed — see "Why this node is not refused". The justification for *not* proposing is
recorded as `open_question` part (1): `institution` is a finance record issuer, `client` is the
counterparty half of the `our_firm` role split rather than a party of record, `record_type` is a
finance enum, and nothing in the canonical table holds a matter, a counterparty or an instrument
kind. Reuse would be a vocabulary decision disguised as a field mapping.

`work_types[]` **is** populated (eighteen values) even though no `work_type`-shaped legal field
exists. This follows `career.json`'s precedent and CONNECTION §2: values are values whether or not
a field is declared yet, and `00` is explicit on the asymmetry: "The system may create new values
when it sees a new course, project, company, university, or event, but it should not invent new
fields automatically." (That sentence wraps in `_CONTRACT.md` rule 9's rendering of it; the span
above is `00`'s own single line.) They are research output for whoever settles (1),
not a smuggled field.

## Neighbours considered that did NOT get an edge

- **`career` as a collision.** Rejected. An employment or separation agreement is the textbook
  also-holds case, and the landed `career.json` authored `also_holds_with: legal` and *not*
  `collides_with: legal`. Authoring a collision from my side would have created a one-way mutex the
  landed node contradicts. Reciprocal `also_holds_with` only.
- **`academic`.** Considered for IEP/accommodation and student-conduct material. Rejected at the
  schema level: the roster already routes that through `academic.iep-accommodation-plans`, whose
  own row names `medical` and `legal` as neighbours. A schema-level edge would duplicate a template
  agent's finding.
- **`college_applications`.** Considered because an immigration/visa packet looks like an
  application packet. Rejected: the roster puts that at `identity.immigration-visa`, and PR-1
  forbids minting a `purpose` clone outside admissions. The join, if any, is that template's.
- **`research`.** Considered for IRB/consent forms — genuinely instrument-shaped. Rejected: the
  roster gives it `research.ethics-compliance`, which names `medical` and `legal` itself. Left to
  it, and noted here so R1c can see the decision was made rather than missed.
- **`photos`.** Rejected. A photographed document is not a capture; `photos.json` already collides
  with `identity` and `medical`, and adding a third safety collision on the same "someone
  photographed a document" evidence would over-fire. The lesson is carried instead by the
  never-alone rule about absent EXIF.
- **A residual `Legal` home.** There is none among `00`'s nine, so CONNECTION §5 invariant 5 does
  not apply. Protected Records is the correct terminal, per fixture 4's shape.

## Deviations, and one place the prompt and the contract disagreed

- The dispatch prompt's node test says refuse a schema row without 3–6 fields; `_CONTRACT.md`
  rules 10/15 and CONNECTION PR-6 say a placeholder safety schema carries none. Per ALIGNMENT's
  precedence (`00` → ALIGNMENT → CONNECTION → prompt), the contract wins and the row stands with
  `fields: []`. Flagged here as instructed.
- I added one key the prompt's node shape does not list: **`is_safety_domain: true`**. It is
  `_CONTRACT.md` rule 15's named key for schema rows, it is the replacement for the dropped
  `safety_for` edge, and my roster row already carries it. Omitting it would have dropped the
  single attribute that makes this a safety domain rather than a quiet placeholder. R1c should
  keep it.
- `falls_through_if_inactive` is `null` on exactly one example (`LICENSE.txt`) where no residual is
  reached. Every other value is one of `00`'s nine names, spelled `00`'s way.
- `role_split: []` — the natural split (party of record vs counterparty; counsel vs opposing
  counsel) cannot be authored, because `role_split` joins canonical *field keys* and this schema
  declares none. Recorded as `open_question` part (2) instead of invented.
- No thresholds, no confidence scores, no handling class. `sensitivity` is `potentially_sensitive`
  and `sensitivity_why` asserts only `00`'s own phrasing.

## NEEDS-JOSEPH — for this node only

1. **What the legal schema legitimises when D1's narrowing lifts.** Not "does legal get fields" but
   *which* — and whether a matter identifier, a counterparty and an instrument kind reuse canonical
   keys or mint new ones. Four legal template rows already exist on the roster and none of them can
   carry a `dimension_order` until this is answered. (Mirrors career's owed-before-P10 question;
   legal's is not owed on the same clock, because no legal destination dimension is planned.)
2. **NJ-2, restated where it actually bites: is a matter-named folder branch acceptable at all?**
   Finance answers the protect-vs-extract fork one way (PR-2: its four fields extract at launch).
   Legal has nothing to extract either way today, so nothing is blocked — but the deeper question
   is disclosure by *structure*, not by content. `00` makes the point next door: a summary such as
   "11 protected identity records" may be safe to show while a visible list of passport filenames
   may not be. A branch labelled with a counterparty or a matter name is the second thing, and it
   leaks on a shared screen even when every file inside it is protected. Joseph should decide
   whether legal material is ever allowed a labelled folder level, or whether it is
   protected-flat-only for good.
3. **Does a single legal instrument surface without a group?** `00` says legal documents "may be
   surfaced as protected records even when they do not meet a normal group-size threshold" — but
   NJ-4 leaves *which part* surfaces it open (P9, P7, or P11 residual routing). Nothing in this row
   depends on the answer; recording it because legal is the domain where a lone file with no
   neighbours is the common case rather than the exception.

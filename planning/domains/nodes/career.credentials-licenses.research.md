# R1b lab notes — `career.credentials-licenses`

Roster row: `kind: template`, `schema_id: career`, `launch: placeholder`, `provenance: inference`.
Verdict: **kept** (`refuse_node: false`). Output: `career.credentials-licenses.json`.

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full (three passes over the whole file,
  not a section skim). Every span in quote marks in the node was grep-verified against this file
  **before** it was written, and again mechanically after: a script extracted every single-quoted
  span longer than fifteen characters from the emitted JSON and checked each for verbatim presence.
  Three failed on the first run and all three were fixed rather than kept: `domain’s` needed 00's
  curly apostrophe; two spans were CONNECTION's wording, not 00's — one re-attributed, one
  de-quoted because CONNECTION line-wraps it and it is therefore not literal anywhere.
- `planning/domains/CONNECTION.md` (sections 2, 3, 5, 6, 7, 11) and `CONNECTION-EXAMPLES.md`
  (fixtures 3, 4, 5, 6, 7, 8). Both exist and were treated as binding, per the orchestrator note.
- `planning/domains/_CONTRACT.md` (rules 5, 6, 8, 10–15).
- `planning/prompts/ALIGNMENT.md`.
- `planning/domains/roster.json` — confirmed id, kind, `schema_id`, neighbours; also used to
  confirm that every edge target is a real roster id and a `kind: template` row.
- `planning/domains/canonical_fields.json` — read in full before proposing anything.
- `src/evidence_shape/vocabulary.py`'s `SOURCE_TYPES` as quoted in the dispatch prompt; every
  `file_examples.source_type` and every `file_kinds.source_types` member was checked against the
  closed fourteen mechanically.
- Landed neighbour nodes, read but **not** rewritten: `career.json` (my schema),
  `academic.transcripts-credentials.json`, `academic.continuing-education.json`,
  `academic.online-course.json`, `academic.standardized-testing.json`,
  `applications.graduate-professional.json`, `research.ethics-compliance.json`.

## The node test, done honestly

Six landed nodes already point `collides_with` at this id. That is a reason to look hard at the
row, not a reason to keep it: a node can be a popular label and still be hollow.

It survives on **two** of the three licences and explicitly fails the third:

- **Detection signals differ** from the career schema's default recruiting situation. Recruiting is
  evidenced by an employer + a role + process language. This row is evidenced by a granting
  authority + a credential title + a labelled validity window, and a licence certificate names no
  role and belongs to no process. That is a different evidence shape, not a different vocabulary.
- **Privacy rules differ.** 00 names `credentials` inside its sensitive-corpus sentence *and*
  inside the Protected Records definition. So this row's residual preference inverts relative to
  every other career template: Protected Records before Independent Records. A job description
  never does that.
- **Dimensions do NOT differ, and could not.** The career schema declares no field rows (D1 as
  narrowed / PR-6), so `dimension_order` is empty by contract on *every* career template. I wrote
  this into `node_test` explicitly rather than leaving a reader to infer that the empty array was a
  refusal or an oversight. The recommendation (issuing authority → credential → document type,
  time never first, flatten for a one-credential holder) is recorded as prose in `template.why`
  so R1c/P10 can restore it whole.

Padding check I ran on myself: if the only difference had been "different work types" (licence vs
offer letter) I would have refused, because work types are values. It is not — the validity window
is a *structure*, and it is the discriminator three neighbouring templates independently reached
for when they wrote their collision signals toward this id.

## Files considered and rejected

Twelve made the list. These did not:

- **`Diploma - BA Economics.pdf`** — the degree parchment. Rejected: it is
  `academic.transcripts-credentials`' material outright (school in the issuer position, academic
  credit conferred, no expiry). Including it would have blurred the very seam that row already
  wrote toward me. It survives only as the *contrast* inside that collision signal.
- **`Resume 2026.pdf` with a Certifications section** — rejected as a file example. A résumé that
  *lists* credentials is a résumé; the section is not a credential document, and treating it as one
  is the same error as reading an employer list off a CV. `career.json` already holds the résumé.
- **`Passport.jpg`** — rejected. Pure `identity`. It carries an expiry, which is exactly why the
  expiry-alone `never_alone` rule exists; but a passport is not a professional standing, and
  putting it here would have smuggled a safety domain's file into a non-safety template.
- **`Employee handbook acknowledgement.pdf`** — rejected as `career.employment-records`.
- **`LinkedIn certifications export.csv`** — rejected as thin: a platform export of self-asserted
  strings, with no issuer position and no verification affordance. It would have been a fourth
  spreadsheet-shaped example teaching nothing the tracker does not already teach.
- **`recruiter.vcf`** — already `career.json`'s fixture; contacts material is privacy-protected and
  not a proposal basis, and nothing about this situation changes that.

Cases I deliberately **kept** because they are ugly: the decorative certificate whose dates are
unlabelled (deterministic signals do *not* fire; it is a `needs_llm` case, and I said so rather
than pretending rule coverage); the photographed wallet card with EXIF and no OCR yet; the
registry screenshot; the locked archive; the ledger spreadsheet that enumerates many credentials
and therefore may never carry one credential's value; and the sparse `license.pdf` whose filename
token proves nothing (`group_without_copying_facts: true`, the `HW 3.pdf` discipline applied to a
credential neighbourhood).

## `proposed_fields` justification

One field, `credential_expiry` (date, `direct`, **not** destination-eligible, `proposal`).

- **Why it is needed:** the validity window is the whole substance of this situation and the stated
  discriminator in `academic.online-course`'s, `academic.transcripts-credentials`' and
  `academic.standardized-testing`'s collision signals toward this row. Three other authors reached
  for the concept before I did.
- **Why no canonical key works:** `creation_date` is this file version's timestamp; `term` is an
  academic term from dedicated term patterns; `tax_year` is a finance year; `application_cycle` is
  an admissions cycle. None of them is "the date this standing stops holding."
- **Why not destination-eligible:** a folder per expiry date scatters one credential's own
  lifecycle across date folders — the scattering 00 names when it says year-first scatters related
  work across calendar folders. It is a search / review / lifecycle field, which is the shape 00
  already uses for surfacing confirmations whose date has passed.
- **What it is not:** it is not a field row. `fields` stays `[]`. D1 as narrowed is not reversed
  here and this note says so on the record; the proposal is for the moment S3/D1's deferral lifts.

I deliberately proposed **only** this one. The other three concepts the situation wants — the
issuing authority, the credential itself, the document type — are precisely `career.json`'s
recorded open question (reuse `institution` / `client` / `application_cycle`, or mint?). Answering
that from a template row would be a leaf node closing the trunk's decision.

## Neighbours considered that did **not** get an edge, and why

- **`career` (schema), `academic`, `finance`, `identity`, `research`, `legal` (schemas)** — no edge
  possible from here. `collides_with` joins same-kind pairs and `also_holds_with` joins *schemas
  only* (CONNECTION §5). This row is a template, so `also_holds_with` is `[]` **by contract**, and
  I recorded that in `also_holds_with_note` rather than leaving an empty array that reads like
  laziness. The genuine co-activation cases this situation produces (a training certificate that is
  also a research artifact; a licence scan that is also identity material; an employment agreement
  that is also legal material) already live on `career.json`'s schema row or belong to the research
  and identity schema rows. **Note for R1c:** my roster row's `must_consider_neighbors` are
  `academic` and `finance`, both *schemas*; the dispatch prompt invites edges to them, CONNECTION
  forbids them from a template row. **CONNECTION wins**, and I discharged both neighbours by
  edging their template rows instead (`academic.continuing-education`,
  `academic.transcripts-credentials`, `academic.online-course`,
  `academic.standardized-testing`; `finance.insurance-personal`, `finance.receipts-expenses`).
- **`career.recruiting`** — no edge. A credential inside a job application is a *packet
  membership*, not an evidence-item confusion: the certificate itself never looks like an offer
  letter or an interview invite. Multi-membership is P9's, and the node records it as a
  `grouping_reason` instead. Writing a collision here would have been "these topics are adjacent",
  which is the misuse of `collides_with` CONNECTION explicitly narrowed away.
- **`career.portfolio-work-samples`** — no edge. A certificate can appear in a portfolio, but the
  document shapes do not confuse a detector.
- **`academic.continuing-education` vs `finance.subscriptions-utilities`** — I looked at the
  subscriptions row for the recurring-dues reading and chose `finance.receipts-expenses` instead:
  the concrete confusion is a *renewal fee receipt / dues invoice*, which is a transaction, and
  that is the row whose stated material it is. Adding both would have been an edge without a
  fixture.
- **`legal.personal-legal-matters`** — considered for disciplinary and status notices (a board
  action against a licence is arguably a legal matter). No edge: I could not name a single evidence
  item that would confuse the two without also inventing what that row's detection signals are,
  and that row has not landed. Left for R1c rather than guessed.

Ten edges were authored. Six are **reciprocations** of edges the landed neighbours already wrote at
me (I re-read each of their signals and answered in matching terms rather than restating my side
only). Four are new and outbound — `finance.insurance-personal`, `finance.receipts-expenses`,
`career.employment-records`, `identity.credentials-passwords` — each carrying a named fixture, and
each awaiting R1c reciprocity.

The `identity.credentials-passwords` edge deserves its own sentence: the two rows share the *word*
credential and nothing else. That is not evidence, and an edge exists there precisely to stop a
merge on a shared name — the filename `credentials.zip` is live on that seam and is also
`academic.transcripts-credentials`' fixture, which is the cleanest demonstration in this node that
an outer archive name decides nothing.

## Things I checked and did not write

- No folder path appears as a fact in any file example.
- No numeric threshold, score, or ceiling anywhere (mechanically checked: every digit in the file
  is a filename, a date inside a fixture, or a rule/part reference such as `_CONTRACT rule 15`).
- No handling class. `sensitivity` is `potentially_sensitive` and `sensitivity_why` asserts only
  00's own phrases; the five classes stay P7's.
- No `parent_id` (null, never authored here — PR-5).
- No `shares_field`, no `related_to`, no invented edge.
- No gazetteer contents (R4's) and no regex (R2/R6's). `proposed_context_terms` is marked PROPOSED
  and says outright that 00 wrote a literal context-term list for one pattern family only and that
  this row copies the shape, not the list.
- `work_types` is marked as values, with the note that no career field exists to hold any of them
  today — so R1a cannot read it as a request for a node per credential kind.

## NEEDS-JOSEPH (this node only)

**NJ-`career.credentials-licenses`-1 — is a credential's lifecycle an optional branch pattern, or
only a group?** One folder per credential, holding its certificate, renewals, wallet card and
compliance records, versus a flat set of credential documents where the lifecycle exists only as a
P9 group. 00 makes optional branch patterns part of what a template defines, and its worked example
of one (the purpose-defined packet held beside institution-first organization) is exactly this
shape. This is a decision about how someone actually files their own professional life, so it is
not mine; and it is unanswerable today in any case, because both readings need career field rows
that S3/D1 defer. Recorded verbatim in the node's `open_question`.

Deliberately **not** raised as a second question: which canonical keys the career schema gets. That
is already `career.json`'s recorded open question, and duplicating it here would inflate the
NEEDS-JOSEPH list without adding a fork.

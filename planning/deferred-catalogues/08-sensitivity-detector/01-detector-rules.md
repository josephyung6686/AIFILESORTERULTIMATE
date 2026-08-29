# 08/01 — Sensitivity detector rules

Companion to [`01-detector-rules.json`](01-detector-rules.json) — the JSON is the source of
truth; this file is the readable map and the reasoning. Checked by `check.py` (ids, kinds,
never-alone, evidence shapes, ceilings, quotes).

**What this is.** The hand-authored rule content behind P7's injected detector (D2, ratified:
the detector is P7's, injected, and unwritten until this content is wired). Rules are evaluated
per file version over that file's own P4 observations, P5's stored sensitivity-signal rows, and
P6's activation output — never over group membership. A fired rule proposes: `kind`, `basis`,
`protected`, a handling-class **ceiling** (P7 assigns the class), and `evidence_refs` as P4
`observation_key`s.

**The discipline, in one line each:**

- Every detector rule is a conjunction — no bare pattern, filename, extension, or gazetteer hit
  ever fires alone (`00`'s course-code shape: pattern **plus** context).
- Absence of a classification never becomes Public/low — that resolution is P7's
  (`unreadable_unclassified`), not any rule's.
- Format is never a class: carrier signals (`source_type`, extension) appear only as conjuncts.
- Counts are injected slots (`min_label_hits`, `min_value_bearing_labels`, `min_code_lines`,
  `min_populated_rows`, `min_secret_assignments`) — no defaults anywhere.
- Patterns are data; a later caller compiles them; nothing lands in `src/`.
- Rules still fire on isolated files — `00` surfaces rare sensitive files as protected records
  below any group threshold, and the gate must be able to deny cloud for a file P10 never
  placed (the Protected Records residual).

## The rules

### `basis: detector` — evidence-backed, non-empty `evidence_refs`

| id | kind | ceiling | fires when (summary) | protected | provenance |
|---|---|---|---|---|---|
| `det-passport-mrz` | passport | highly_sensitive_credential_bearing | an ICAO-shaped MRZ line pair in OCR/extracted text AND a scanned/photographed carrier | true | design |
| `det-passport-biodata-labels` | passport | highly_sensitive_credential_bearing | biodata label cluster ≥ `min_label_hits` AND populated adjacent values ≥ `min_value_bearing_labels` | true | design |
| `det-tax-form-completed` | tax_statement | sensitive_personal | a jurisdiction form identifier (R5 gazetteer) AND tax context terms AND populated labeled values | true | design |
| `det-tax-statement-labels` | tax_statement | sensitive_personal | year-scoped tax/pay labels AND populated values AND a document carrier | true | design |
| `det-medical-clinical-document` | medical_document | sensitive_personal | patient-identity labels AND clinical-content labels AND populated values | true | design |
| `det-medical-eob` | medical_document | sensitive_personal | EOB/claim labels AND populated values | true | design |
| `det-auth-key-material` | authentication_key | highly_sensitive_credential_bearing | a private-key armor header AND a key body | true | design |
| `det-env-secret-assignments` | authentication_key | highly_sensitive_credential_bearing | secret-named assignments with non-placeholder values ≥ `min_secret_assignments` | true | inference |
| `det-account-statement` | account_record | sensitive_personal | statement labels AND an account-locator value (R5 shapes); transaction table strengthens | true | design |
| `det-id-drivers-licence` | identity_document | highly_sensitive_credential_bearing | licence labels incl. physical descriptors AND an image/scan carrier | true | proposal |
| `det-id-travel-visa` | identity_document | highly_sensitive_credential_bearing | visa labels AND carrier AND NOT the payment-card suppressor | true | proposal |
| `det-id-national-id-labeled` | identity_document | highly_sensitive_credential_bearing | a national-ID label (R5) AND an adjacent value of that label's shape | true | proposal |
| `det-id-civil-certificate` | identity_document | sensitive_personal | a civil-certificate title AND registrar labels AND NOT the award suppressor | true | proposal |
| `det-legal-court-filing` | legal_record | sensitive_personal | a court caption in heading position AND case-structure labels | true | proposal |
| `det-legal-notarized-instrument` | legal_record | sensitive_personal | a notary block AND populated party/date values | true | proposal |
| `det-credential-2fa-backup-codes` | credential_store | highly_sensitive_credential_bearing | recovery-code vocabulary AND a code grid ≥ `min_code_lines` | true | inference |
| `det-credential-password-export` | credential_store | highly_sensitive_credential_bearing | a credential header set AND populated rows ≥ `min_populated_rows` | true | inference |
| `det-correspondence-email-content` | private_correspondence | sensitive_personal | source_type email AND at least one stored P5 sensitivity-signal row | **false** | design |
| `det-contact-directory` | contact_record | sensitive_personal | source_type contacts AND at least one stored P5 signal row | true | design |

The five `kind` values `00` names directly (passport, tax_statement, medical_document,
authentication_key, account_record) are the design set; identity_document, legal_record,
credential_store, private_correspondence and contact_record are **proposed kinds**, listed
separately in the JSON's `kinds.proposed` with their defenses, so Joseph can refuse any of them
without touching the design five. `det-correspondence-email-content` is the one rule with
`protected: false` — `00` does not put correspondence in the immediate-protected five, so the
rule classifies without protecting, and whether it should also protect is NEEDS-JOSEPH.

### `basis: safety_domain` — activation is the evidence

| id | domain | fires when | evidence |
|---|---|---|---|
| `saf-finance-activation` | finance | finance ∈ `active_domains(content_hash)` | the activation itself; P6 holds its supporting evidence. `evidence_refs` may be empty — P7 requires non-emptiness only for `basis: detector` |
| `saf-identity-activation` | identity | identity ∈ active set | same |
| `saf-medical-activation` | medical | medical ∈ active set | same |
| `saf-legal-activation` | legal | legal ∈ active set | same |

These four are the P7-side reading of `00`'s safety-domain sentence and CONNECTION's PR-2:
activation unlocks protection plus the small schema only; the never-alone discipline is
inherited from activation step 2 (a schema whose entire support is never-alone evidence is
struck upstream, so no bank name, `.pdf`, or bare gazetteer hit ever reaches these rules). The
passport worked example (CONNECTION-EXAMPLES §4) is `saf-identity-activation` plus the
`det-passport-*` rules: safety-only activation leaves `residual_candidate` true and the
fallthrough home is Protected Records.

## The never-alone corpus — what must NOT fire

Every rule carries its own `never_alone`; the recurring cases:

| Must not fire | Why | Guarded by |
|---|---|---|
| the word "passport" in a novel or travel article | prose is not an MRZ or a biodata page | shape + carrier conjuncts |
| a blank W-9-shaped or biodata-shaped form/template | labels present, values absent | `min_value_bearing_labels` |
| a textbook "Social Security" chapter | label without an adjacent personal value | label-AND-adjacent-value pairing |
| `.pdf`, `.csv`, `.vcf`-as-format, any extension | format is a routing signal, never meaning | `ref-format-as-class` |
| a filename alone (`passport.jpg`, `id_rsa`, `taxes 2025.pdf`) | `00` forbids inferring purpose from a filename alone | `ref-filename-only` |
| "Visa ending 1234" on receipts/statements | the payment network, not a travel document | `payment_card_suppressor` |
| award/course certificates | Independent Records residual material | `award_suppressor` |
| an invoice with the seller's IBAN in the footer | transactional document — Receipts and Confirmations residual | statement-scoped label requirement |
| a medical journal article or pathology lecture notes | reading material — Reading Inbox residual | patient-identity conjunct |
| `-----BEGIN PUBLIC KEY-----`, certificates | public material, not a secret | armor-header alternation |
| `.env.example` and templates | placeholder values do not count | `non_placeholder_value` |
| discount/gift/licence-key code lists | grid without recovery vocabulary | `recovery_heading` conjunct |
| a bare 4-digit number, a currency amount, a university name | `00`'s number-ambiguity and generic-hub warnings | never-alone lists + upstream activation step 2 |

## Refused

| id | refuses |
|---|---|
| `ref-format-as-class` | extension/source_type → class or protection (`.pdf` → medical) |
| `ref-filename-only` | any rule firing on a filename alone |
| `ref-protected-characteristics-gazetteer` | a detection gazetteer of protected characteristics — the question goes to NEEDS-JOSEPH, the list stays unfilled |
| `ref-ocr-density-as-signal` | text density / OCR volume as a sensitivity signal |
| `ref-unauthorized-transcription-as-signal` | consuming P5's `UnauthorizedTranscription` as a detector input — live code makes it a propagating exception about the *call*; nothing is persisted for a rule to cite. A deliberate, documented divergence from the dispatch prompt |
| `ref-money-amounts` | currency symbols or amount columns as finance-protection evidence |

## Uncertain (arguments on both sides in the JSON)

`unc-safety-activation-breadth` (protect every finance-activated receipt, or the protectable
core? — the NJ-2 seam) · `unc-employment-educational-kinds` (the §8.4 corpus list names them;
protecting them wholesale would gate the product's launch material) · `unc-archive-manifest-names`
(a manifest name is a filename) · `unc-localized-labels` (English-only lists; fold into R5?) ·
`unc-chat-exports` (no honest conjunction found without a corpus) ·
`unc-partially-completed-forms` (why the completed-form count is an injected slot).

All are mirrored in [`RESEARCH.md`](RESEARCH.md)'s NEEDS-JOSEPH.

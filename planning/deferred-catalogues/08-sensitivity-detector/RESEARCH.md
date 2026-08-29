# 08 — Research record

Sources, false-positive analysis, and the open questions. Written to disk deliberately: agent
final reports have been lost on this project before, and a decision list that exists only in a
chat message is a decision list that dies.

---

## Provenance of this deliverable

The catalogue was begun by an R2 agent on 2026-08-21 whose session was killed mid-run: the three
JSON files and `check.py` existed; the README, the three markdown companions, and this file did
not. A second R2 pass on 2026-08-22 treated everything on disk as an untrusted draft and
re-verified it against the sources before completing the set:

- **Every structured quote re-verified mechanically** — 68 `design_cite`/anchor spans across the
  three JSONs, 0 failures, via `check.py`'s corpus check against the eight named sources.
- **The checker itself negative-tested** — six defects seeded into a scratch copy (a fabricated
  `00` quote, a numeric threshold, a near-miss handling-class respelling, an undeclared slot
  reference, a duplicate id, an out-of-vocabulary ceiling); all six were reported.
- **One checker defect found and fixed in the salvage audit:** the near-miss respelling check
  used substring matching, so the legitimate token `highly_sensitive_credential_bearing` tripped
  its own prefix `highly_sensitive_credential`. The check now matches at token boundaries; the
  seeded-defect test confirms a real bare respelling is still caught.
- Live-code claims re-checked against `src/extractors/long_tail.py` as it stands: the
  `extraction_sensitivity_signal` table, `sensitivity_signals_for(conn, run_id)`,
  keying by P4 `observation_key`, the single signal value, and `UnauthorizedTranscription` being
  a propagating exception (nothing persisted) — the last is why the catalogue *refuses* it as a
  detector input even though the dispatch prompt listed it beside the consumable signals.

## Decision state, and where the dispatch prompt predates it

The dispatch prompt was written while D2 was open. Between its writing and this authoring,
Joseph ratified D2 (2026-08-21; `planning/overnight/council/DECISION-BRIEF.md`, RATIFIED table;
applied in `planning/22-p1-p7-connection-contract.md` §3):

- P7's `ClassificationRecord`, keyed `(file_id, content_hash)`, is authoritative;
  `files.sensitivity_state` is its projection, written via P1's `set_sensitivity_state`.
- The fifth class is a gate outcome, not a file fact.
- The detector is P7's, injected, and unwritten — no fourteenth part.

This catalogue follows the recorded state. The prompt's instruction to author rules that can
write through either home was kept anyway — the `write_shape` in catalogue 01 is
storage-agnostic, so a reversal would change no rule content. R0's CONNECTION.md also landed
before this authoring and is obeyed: `is_safety_domain` is a schema-row attribute (no
`safety_for` edge), PR-2's safety split (protection plus the small schema only), the never-alone
invariant, and the Protected Records fallthrough in the passport worked example
(CONNECTION-EXAMPLES §4).

## Sources

**Design and contract documents, read in full during authoring and re-read during the salvage
audit:** `planning/00-database-agent-product-design.md` (the only source quoted for product
constraints), `planning/01-product-design-structured.md` (§ locators only — its own header says
`00`'s wording is authoritative), `planning/prompts/ALIGNMENT.md`,
`planning/domains/CONNECTION.md` + `CONNECTION-EXAMPLES.md` + `_CONTRACT.md`,
`planning/parts/P7-privacy-consent-gate/SPEC.md`, `planning/parts/P5-extractors/SPEC.md`,
`planning/22-p1-p7-connection-contract.md`, `planning/overnight/council/DECISION-BRIEF.md`,
`planning/overnight/NEEDS-JOSEPH.md` (B6.10), `planning/deferred-catalogues/README.md`, and
`src/extractors/long_tail.py` (live code).

**Document-type knowledge** (what a biodata page, MRZ, EOB, notary block, court caption,
password-manager export, 2FA code sheet, or PEM armor looks like): drawn from the authoring
model's own knowledge of public document formats. Following the top-level catalogue README's
sourcing discipline — where a page nobody opened must not be cited as read — **no web page was
opened during authoring or audit, and no row here claims a retrieved citation.** Format names
(ICAO 9303 TD3 for the MRZ shape, RFC 7468 for PEM textual encoding, ISO/IEC 7812 for card
numbers) identify the format; they are not citations. Every row that would be harmful if this
knowledge were wrong is conjunction-guarded, over-protects rather than exposes when it
misfires, and is user-revisable — `00`: "The classification is itself evidence-backed and can
be revised by the user." Rows worth upgrading with an opened source before launch: the MRZ
length band, the OpenSSH armor variants, and the password-export header sets.

## False-positive analysis — the false-friend corpus

The direction of every residual error is chosen deliberately: **a false positive over-protects
and costs a user revision; a false negative exposes.** Where a case is genuinely undecidable
from content, the rules land on protection.

| False friend | Rule at risk | Discriminator |
|---|---|---|
| blank agency tax templates, W-9-style downloads | `det-tax-form-completed` | `min_value_bearing_labels` — labels without populated values never fire; producer metadata deliberately unused (catalogue 01 of the P6 set owns the tool-string discount) |
| "Instructions for …" agency documents | `det-tax-form-completed` | identifier and context terms present, populated labeled values scarce |
| textbook "Social Security" chapter | `det-id-national-id-labeled` | label with no adjacent personal value |
| blank passport-application or intake forms | `det-passport-biodata-labels`, `det-medical-clinical-document` | the populated-values conjunct |
| museum/news photo of a passport, film prop licences | `det-passport-mrz`, `det-id-drivers-licence` | fires — accepted over-protection, user-revisable |
| "Visa" the payment network on receipts | `det-id-travel-visa` | `payment_card_suppressor`, a block-only negative conjunct |
| award and course certificates | `det-id-civil-certificate` | `award_suppressor`; Independent Records residual material |
| invoices carrying the seller's IBAN | `det-account-statement` | statement-scoped labels (period, balances) required beyond the locator; isolated invoices are Receipts-and-Confirmations residual material |
| medical journal articles, pathology notes | `det-medical-clinical-document` | patient-identity conjunct; reading material is Reading Inbox residual material |
| appointment-reminder email | `det-medical-clinical-document` | patient identity without clinical content — falls to the correspondence rule instead |
| cryptography textbooks, key-format blog posts | `det-auth-key-material` | armor header AND body required; prose never carries both |
| `.env.example`, CI secret *references* | `det-env-secret-assignments` | `non_placeholder_value` — placeholder markers do not count |
| bookmarks exports, signup-tracking sheets | `det-credential-password-export` | password column required and populated |
| licence-key and gift-code sheets | `det-credential-2fa-backup-codes` | recovery vocabulary required beside the grid |
| newsletters and mailing-list mail | `det-correspondence-email-content` | fires by design; the ceiling and `protected: false` keep the consequence proportionate |
| server logs vs chat exports | (none — gap) | no honest conjunction found; recorded as `unc-chat-exports` rather than papered over |
| genealogy scans of historical certificates | `det-id-civil-certificate` | unresolvable from content; fires; user revision is the designed remedy |

Two structural mitigations sit outside any single rule: P3's exclusion of software project roots
pre-filters the repository copies of keys and `.env` files, and P7's negative-feedback record
(observation keys stored with a user's downgrade) keeps a revised false positive from
resurfacing.

## Why the rule set is small

Nineteen detector rules and four safety-domain rules. The dispatch's stop rule was applied: a
rule was added only where a document type has a recognizable evidence shape *and* `00` names the
material (or the proposed kind defends itself from `00`'s corpus list). Padding the set with
per-format or per-topic rules is exactly how `.pdf` → medical happens; breadth beyond this list
belongs to safety-domain activation (which inherits P6's evidence discipline), to R5's
jurisdiction values plugging the slots already named here, and to user reclassification.

## Digits in pattern strings vs the no-numbers rule

`check.py` proves no JSON **value** is numeric — every decision count is a named injected slot
with no default. Regex quantifiers inside pattern *strings* (an MRZ line's length band, a backup
code's chunk shape) describe document formats, the same way catalogue 02 of the P6 set records
`1920x1080` as data; they are facts about documents, not thresholds about decisions. Any reader
who disagrees moves the quantifier into a slot without touching the rule structure.

---

## NEEDS-JOSEPH

Twelve items. None blocks the build: the catalogue loads and every check passes with all of
them unresolved. The first three are the entries the dispatch requires by name; recorded state
is stated as recorded, and nothing open is closed here.

1. **Detector owner — the remainder after D2.** Recorded state: the detector is P7's, injected,
   no fourteenth part, and until it is wired every real file resolves to `Denied(unclassified)`.
   Still open: **which caller loads this catalogue and injects it** — the orchestrator wave that
   already injects catalogues 02–07 into P5, or a P7 build task — and where the classification
   pass sits relative to P6's activation pass (the `saf-*` rules consume `active_domains`, so
   the pass cannot run before P6's deterministic pass for that content hash). The seam contract's
   standing rule applies until then: a part that does not own the concept passes `None`.
2. **The fifth handling class — the remainder after D2.** Recorded state: a gate outcome, not a
   file fact; it lives on the release decision, never in the column. Still open (the
   DECISION-BRIEF's own F-9 seam): the mapping from P4's nine `completeness` values onto
   `unreadable_unclassified` has no design source. This catalogue deliberately writes **no**
   rule producing `unreadable_unclassified` — no detector recognizes unreadability; it is the
   gate's resolution of absence — so the F-9 question stays visibly Joseph's.
3. **Protected characteristics** (carried from overnight B6.10, quoted in the refusals): whether
   the product should detect such material in order to protect it, or decline to model it and
   let it fall to Protected Records. Enumerating the categories would instruct the extractor to
   look for them; all three files refuse the gazetteer and this question stays open. An
   identifier class for characteristics is refused for the same reason.
4. **Safety-activation breadth** (`unc-safety-activation-breadth`, the NJ-2 seam): does
   "detects and protects" protect *every* file that activates a safety schema — every receipt
   that legitimately activates finance — or the protectable core the detector rules name? The
   `saf-*` rules implement BROAD until ruled; the cost is revisions on receipts, never exposure.
5. **Employment materials and educational records** (`unc-employment-educational-kinds`): the
   §8.4 corpus list names both; no rule protects either, because coursework and recruiting are
   the product's launch domains and wholesale protection would gate the material the product
   exists to organize. Should they get proposed kinds?
6. **Correspondence protection** (`det-correspondence-email-content`): the rule classifies
   (`sensitive_personal` ceiling) without protecting, because `00` does not put correspondence
   in the immediate-protected five. Should it also protect?
7. **Archive manifests naming protected-looking members** (`unc-archive-manifest-names`):
   `passport.jpg` inside `submission.zip` — manifest names are filenames, and filename-only
   inference is refused; the conservative outcome (unreadable archives stay unclassified, which
   the gate denies) stands until ruled.
8. **Localized label lists** (`unc-localized-labels`): every label list is English; the OCR
   ratification (English + CJK + Western European) says which languages will produce text.
   Likely folds into R5's jurisdiction work.
9. **Chat exports** (`unc-chat-exports`): private correspondence with no email `source_type` and
   no P5 signal rows; no honest conjunction found without a corpus.
10. **Partially-completed forms** (`unc-partially-completed-forms`): where
    `min_value_bearing_labels` should sit — protect-on-one-value is the safe direction; the
    value is a deployment decision, which is why it is a slot.
11. **Organization names as identifiers** (`unc-organization-as-identifier`): a provider's name
    can identify a condition by implication; waits on item 3.
12. **Transform uniformity** (`unc-partial-vs-token-for-accounts`): `keep_last_n` for account
    locators vs full token replacement for government IDs is deliberate (statement convention;
    prefix/tail entropy) — Joseph may prefer uniformity.

Two further items are implementer notes rather than Joseph questions, kept in catalogue 03's
`uncertain`: token-shaped source text (`unc-token-collision-with-source`) and overlapping span
order (`unc-overlapping-spans`).

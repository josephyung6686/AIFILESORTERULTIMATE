# 08/03 — Redaction transforms

Companion to [`03-redaction-transforms.json`](03-redaction-transforms.json) — the JSON is the
source of truth. Each transform is a **named procedure with no default in P7**: a
`redacted_identifier` item whose class's transform is not injected is a load error, never a
passthrough. Catalogue 02 names which transform each identifier class uses.

**The boundary that shapes everything here:** redaction removes a value; it never rewrites a
document. Reduction — summarizing, shortening, choosing what the model sees — is a dossier
decision made by P8 *before* the gate is called; P7's own contract states the gate never
truncates and never reduces, and its only content operations are resolution and redaction.
The transforms below operate on single spans and nothing else.

**Context always survives.** P4 publishes `context_before` / `context_after` /
`context_truncated` as three fields precisely so §8.4 can redact a value without dropping its
context (M5). Every transform leaves both context fields byte-identical; a transform that
touches context is malformed by definition.

**Locally reversible, in the only sense `00` permits:** the original value remains in local
SQLite (complete extracted text and raw sensitive values are always-local) and the dossier
carries the redacted form. Nothing is reversible *from* the dossier; reversibility means the
local record can always reconstruct exactly what left, which is the audit record's stated
obligation.

## The transforms

| transform_id | does | span becomes | provenance |
|---|---|---|---|
| `replace_with_class_token` | replace span with the literal class token | `[government_id_number]` — length deliberately not preserved | design |
| `keep_last_n` | class token plus the span's final `redaction_keep_n` characters | `[financial_account_number …6819]` | inference |
| `drop_span` | remove the span entirely; the manifest, not the text, records the drop | nothing — for `always_local` classes even the class's presence-in-text is withheld | design |
| `drop_gps` | remove a coordinate pair entirely; never coarsen, never resolve to a place name | nothing | design |

`keep_last_n` exists because a tail is sometimes the discriminating evidence (which of two
accounts a statement belongs to) and statement conventions already display trailing digits; it
never retains a leading prefix (prefixes carry issuer/type information), never derives the count
from the value, and never applies to an `always_local` class — a dropping transform is mandatory
there. `redaction_keep_n` is the file's single injected slot, with no default.

`drop_gps` is the backstop for coordinates embedded in releasable *text* (maps-screenshot OCR, a
caption); the EXIF/GPS *metadata* path is already refused at the item-kind level by the gate.
Coarsening to a city would manufacture a value nobody observed, so it is forbidden, not offered.

## Refused

| id | refuses | why, in one line |
|---|---|---|
| `ref-llm-rewrite` | model-assisted "smart" redaction or paraphrase | reduction is P8's dossier decision; the gate never truncates and never reduces — and sanitizing a model input with a model call is circular |
| `ref-hash-pseudonym` | stable per-value pseudonyms | a stable pseudonym is a join key an external provider could correlate across files and dossiers — the exact linkage redaction exists to prevent |
| `ref-generalization` | coordinates→city, birth date→age band, account→institution | every generalization manufactures an unobserved value; where the general fact is legitimate it already exists as a fact and travels as `candidate_label` or `metadata_field` |
| `ref-format-preserving-masking` | length/format-preserving masks | shape and length are real information for short identifier spaces; the class token conveys the kind without the shape |

## Uncertain

- `unc-token-collision-with-source` — a document can itself contain token-shaped text; the
  manifest disambiguates for the audit trail, the model cannot. Escaping would alter bytes
  outside the span (forbidden); the ambiguity is accepted and recorded as deliberate.
- `unc-overlapping-spans` — apply order for overlapping identifier spans is gate mechanics,
  P7's to build; flagged for the implementer rather than resolved here.

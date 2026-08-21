# 08/02 — Identifier classes

Companion to [`02-identifier-classes.json`](02-identifier-classes.json) — the JSON is the source
of truth. This is the closed list behind the `identifier_class` string P7 already stores on the
`redacted_identifier` item kind and in `redaction_manifest`; `00`'s compact-dossier allowance
names the category this file defines: selected excerpts, **redacted identifiers**, candidate
labels, non-sensitive metadata, and evidence references.

**The test that decides membership:** an identifier names a *person or an instrument*; a fact
describes the *file*. A course code is a fact; a Social Security number is an identifier.
Redacting a fact would delete the very evidence a dossier exists to carry, which is why the
`non_members` array is as binding as the entries.

**Locality:** `always_local: true` means the value cannot appear in a cloud dossier even
redacted — its transform must be a dropping transform, and the `redaction_manifest` (not the
text) records that the drop happened, which is how the audit record stays able to answer what
left the device.

**Jurisdiction:** `jurisdiction_dependent: true` means R5 owns the value patterns — shapes,
checksums, label wordings per jurisdiction. This file owns the class, its transform, and its
locality only.

## The classes

| class_id | display name | transform | always_local | jurisdiction | provenance |
|---|---|---|---|---|---|
| `government_id_number` | Government-issued identifier | `replace_with_class_token` | no | yes | design |
| `financial_account_number` | Financial account locator | `keep_last_n` | no | yes | design |
| `payment_card_number` | Payment card number | `keep_last_n` | no | no | proposal |
| `authentication_secret` | Authentication secret | `drop_span` | **yes** | no | design |
| `email_address` | Email address | `replace_with_class_token` | no | no | design |
| `phone_number` | Telephone number | `replace_with_class_token` | no | yes | design |
| `person_name` | Personal name | `replace_with_class_token` | no | no | inference |
| `postal_address` | Postal address | `replace_with_class_token` | no | yes | inference |
| `date_of_birth` | Date of birth | `replace_with_class_token` | no | no | proposal |
| `medical_record_number` | Medical record number | `replace_with_class_token` | no | yes | proposal |
| `gps_coordinates` | GPS coordinates | `drop_gps` | **yes** | no | design |

Three rows are **proposals** with empty `design_cites` — payment cards, birth dates and medical
record numbers have no naming design sentence, and each row says so, so Joseph can refuse them
individually. The rest anchor on `00`'s own sentences (the protected five, the always-local set,
the VCF field list, the display-facet list).

**No free-text mining.** `person_name`, `postal_address` and `date_of_birth` are applied only on
spans a detector rule or the caller has already located (a patient-name label's adjacent value,
a VCF value, a labeled birth-date field). No name gazetteer, address miner, or date sweep exists
or is wanted — bare dates stay under §3.10's narrow-date discipline, and free-text name
recognition is out of scope by design.

## Non-members — never identifier classes

| Value kind | Why it stays |
|---|---|
| course codes (`BUSIB 4300`, `PHYS1401`) | facts — `00`'s own worked validated fact |
| university / institution names | facts and candidate labels; their ambiguity is a role question (`role_split`), not an identity question |
| company, lab, venue, project identifiers | domain-schema facts the dossier exists to carry |
| work types, document types, terms | values of schema fields |
| camera make/model, capture year, media type | Photos-domain facts; the EXIF *block* is already always-local as an item kind — a different mechanism |
| group labels and display names | `candidate_label` item kind, already user-visible vocabulary |
| paths, complete extracted text, OCR output, hashes, EXIF blocks, user edits, group memberships | the always-local **set** is enforced at the item-kind level by the gate; listing them as classes would wrongly imply an excerpt could carry them redacted |
| protected characteristics | refused as a detection vocabulary entirely — see NEEDS-JOSEPH; a class here would require exactly the gazetteer the refusal forbids |

## Refused / uncertain

- `ref-characteristic-classes` — no identifier classes for protected characteristics; the
  detect-to-protect versus decline-to-model question is Joseph's and stays open.
- `ref-ip-and-device-identifiers` — real identifiers, but nothing in v1 locates them; a class
  nothing produces is dead vocabulary.
- `unc-organization-as-identifier` — a provider's name can be sensitive by implication; waits on
  the characteristic-category decision.
- `unc-partial-vs-token-for-accounts` — the deliberate split between `keep_last_n` (accounts)
  and full token replacement (government IDs); Joseph may prefer uniformity.

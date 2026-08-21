# Dispatch prompt — R2 · sensitivity detector, identifier classes, redaction transforms

Copy everything below the line into a new agent. The agent should not need this chat.

Give it read access to the repo. It writes under `planning/deferred-catalogues/08-sensitivity-detector/` as **data + reasoning**, injected later. It does **not** edit `src/privacy/` or implement P7. It does **not** close D2 (which record is authoritative).

---

You are authoring the **sensitivity detector catalogue** for a local-first file-organization agent.

## Why you are here

P7 (privacy gate) is specified in detail and can be built as a door. **Nothing classifies a file.** After P7 ships:

- `files.sensitivity_state` stays NULL (the column exists; no writer)
- `Gate.release` returns `Denied(unclassified)` for every real file
- P9/P10/P11/P12 rows that say "carried from P7, never re-derived" carry nothing

P7's own SPEC Deferred: *"The design states what is protected and never how it is recognised. The detector rule set, its signals, and its thresholds are hand-authored. P7 publishes the vocabulary the detectors write into."*

No part in `planning/02-segmentation-map.md`'s thirteen claims the detector. A deferral needs a part to be deferred to. You will **not** assign that part (Joseph / D2). You will author the **rule contents** so whoever owns it has something to inject, the same way P5 injects `dimension_signal` rather than hard-coding screen sizes.

Second half of the same hole: §8.4 permits **"redacted identifiers"** in cloud dossiers. P7 carries `identifier_class` as an **opaque string** with no list and **no default transform**. A shipped product cannot redact what it cannot name.

## Product constraint (quote only from `00`)

Read:

- `planning/00-database-agent-product-design.md`
- `planning/01-product-design-structured.md` §8.4, §3.15, §2.9, §7.3 Protected Records
- `planning/parts/P7-privacy-consent-gate/SPEC.md` — Deferred table, five handling classes, always-local nine, `basis = detector | safety_domain | user`
- `planning/parts/P5-extractors/SPEC.md` / `src/extractors/long_tail.py` — already emits `POTENTIALLY_SENSITIVE` on email addresses, message content, every VCF value. That is a **signal**, not a handling class.
- `planning/22-p1-p7-connection-contract.md` §3 — four homes, no producer
- `planning/overnight/council/DECISION-BRIEF.md` D2 — recommendation only
- `planning/domains/CONNECTION.md` if it exists (R0) — whether safety is per-domain or per-file
- `src/extractors/long_tail.py` `sensitivity_signals_for`

`00` states, and you must not paraphrase inside quote marks:

- Privacy is enforced **before** content reaches any model or external connector.
- Default posture **must** be local-first and data-minimizing.
- Five handling classes: Public or low sensitivity; Personal but non-sensitive; Sensitive personal; Highly sensitive or credential-bearing; Unreadable or unclassified.
- **"A scanned passport, tax statement, medical document, authentication key, or account record should enter a protected state immediately."**
- Protected material: not in cloud prompts by default; not raw in group summaries; not moved automatically without an explicit permitting policy.
- Always local: paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, raw sensitive values.
- Cloud dossier may include: selected excerpts, redacted identifiers, candidate labels, non-sensitive metadata, evidence references.
- Safety domains first (`00`): finance, identity, medical, legal — detect and protect before cloud or automated placement.
- §2.9 already marks addresses and message content as potentially sensitive; contacts as fully sensitive at emission. P5 **assigns no handling class**.

Absence of a classification must **never** become Public/low. That is P7's job. Yours is: when a detector *does* fire, what evidence it cites.

## What to research

You are building **three catalogues that plug into P7's injected protocols**.

### A. Detector rules (what enters a protected state, and how we know)

For each rule:

- `id`
- `kind` — one of the `00` five: passport / tax statement / medical document / authentication key / account record — **plus** proposed kinds you can defend from `00`'s longer corpus list (identity documents, employment materials, educational records, GPS, private correspondence, legal records, credentials). Proposed kinds are `proposal` and listed separately so Joseph can refuse them.
- `basis` — `detector` (evidence-backed) or `safety_domain` (domain activation is the evidence)
- `signals[]` — what P4 observations / P5 source_types / gazetteer hits / filename patterns **together** fire. Never a bare pattern. Model on §3.5: course code **plus** academic context.
- `never_alone[]` — university name, `.pdf`, a 4-digit number, the word "passport" in a novel
- `evidence_refs_shape` — which observation keys would be stored (P7 requires non-empty `evidence_refs` for `basis=detector`)
- `handling_class_ceiling` — which of the five classes this rule may write at most. Detector does not have to pick the class if D2 is unset; it may write `protected: true` + kind and leave class to P7. **Say which.** If CONNECTION.md exists, obey it.
- `false_positive_notes` — receipts that say "account", photos of a passport in a museum, W-9 templates from the IRS website vs a completed W-9
- `provenance`

**P5 signals already exist.** Consume them: email `address` in body/link zones, contacts VCF values, `UnauthorizedTranscription`. Do not re-derive. Add rules for what P5 does **not** mark: passports, tax forms, medical record types, PEM/SSH keys, bank statements.

**No numeric thresholds.** "How many hits" is injected (`min_hits` slot, no default), like every other ceiling.

**No regex in `src/`.** Patterns live in this catalogue as data. A later caller compiles them.

### B. Identifier classes (what "redacted identifiers" means)

Closed list, each:

- `class_id` (opaque token P7 already stores as a string)
- `display_name`
- `examples` (fake, never real PII)
- `why_this_is_an_identifier_not_a_fact` — a course code is a fact; a Social Security number is an identifier
- `transform_id` — which transform from catalogue C applies
- `always_local` — if true, it cannot appear even redacted in a cloud dossier (GPS, full EXIF, raw hashes — `00` already always-local)
- `jurisdiction_dependent` — true/false; if true, R5 owns the value patterns, you own the class

Start from what `00` actually names: identity numbers, account numbers, credentials, GPS, names in protected summaries, medical record numbers if you can cite a design sentence or mark `proposal`.

Do **not** build a gazetteer of protected characteristics (race, religion, etc.). `00` does not ask the product to detect those in order to file them. Overnight NEEDS-JOSEPH already flagged that enumerating them would instruct the extractor to look for them. Put that question in `NEEDS-JOSEPH`, do not fill the list.

### C. Redaction transforms

Each transform is a **named procedure with no default in P7**:

- `transform_id`
- `input` / `output` shape
- `preserves` — P4's `context_before` / `context_after` must survive (`00`/M5: redact the value without dropping context)
- `reversible_locally` — true only if the original remains in local SQLite and the dossier carries the redacted form
- `never_does` — truncate, summarize, hash into a different identifier that could be joined across files unless `00` allows it

Propose a small set: `replace_with_class_token` (`[account]`), `keep_last_n` (injected n), `drop_span`, `drop_gps`. No "smart" LLM rewrite — reduction is a dossier decision, P8's, not the gate's. P7 SPEC: the gate never truncates and never reduces.

## How to research

- Real document types: passport biodata page, US/UK tax forms as **types not values** (R5 fills jurisdiction values), discharge summaries, `.pem` / `id_rsa`, bank PDF statements, EOB, visa, driver's licence, 2FA backup codes, `.env` files, password-manager exports.
- False-friend corpus: IRS blank forms, textbook "Social Security" chapter, movie stills, scanned homework with a student ID that is a course number.
- P5's existing signal table — extend, do not duplicate.
- Residual Protected Records (`00` §7.3) — isolated sensitive material with no group. Detector must still fire so the gate denies cloud even when P10 has not placed it.

## What you must not do

- Do not pick D2 (fact layer vs P7 ClassificationRecord). Author rules that can write **through** either.
- Do not assign handling classes from format (`.pdf` is not medical).
- Do not invent P7 event types or columns.
- Do not put thresholds in the JSON as numbers.
- Do not enumerate protected characteristics as a detection gazetteer.
- Do not edit `src/`.

## Output

```text
planning/deferred-catalogues/08-sensitivity-detector/
  README.md                 how P7 injects this (mirror deferred-catalogues/README.md)
  01-detector-rules.json    + .md
  02-identifier-classes.json + .md
  03-redaction-transforms.json + .md
  RESEARCH.md               sources, false-positive analysis, NEEDS-JOSEPH
  check.py                  ids unique, every detector rule has never_alone,
                            every identifier_class names a transform that exists,
                            no handling-class vocabulary except the five §8.4 names,
                            no fabricated 00 quotes
```

## Done when

- Every `00` protected example (passport, tax statement, medical document, authentication key, account record) has at least one rule that could fire on a realistic file **and** a never_alone case that must not fire.
- Identifier classes cover "redacted identifiers" without swallowing course codes, university names, or work types.
- Transforms preserve context fields.
- Injection story is the same pattern as catalogues 02–07 (caller loads JSON, passes a protocol, no module-level list in `src/privacy/`).
- `NEEDS-JOSEPH` includes: detector owner (part name), fifth handling class as extraction outcome vs file property, characteristic-category question.

If the honest rule set is small (dozens, not thousands), **stop**. Padding detector rules is how you get `.pdf` → medical.

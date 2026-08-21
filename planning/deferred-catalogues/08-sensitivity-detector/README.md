# 08 — Sensitivity detector, identifier classes, redaction transforms

Hand-authored content **P7 needs and must not invent**. This directory fills two rows of P7's
*Deferred — manual design required* table at once — the row for the detection rules (P7's SPEC:
the design states *what* is protected and never *how it is recognised*; the rule set is
hand-authored and P7 publishes the vocabulary the detectors write into) and the row for
identifier classes and the redaction transform (P7 stores `identifier_class` as an opaque string
until this content exists). Nothing here is a plan, a schema, or an implementation; each file is
data plus the reasoning and sourcing behind it.

Authored 2026-08-21 (R2), salvage-audited and completed 2026-08-22. Nothing is committed by the
authoring agent — Joseph reviews and commits.

---

## The three catalogues

| # | File | Consumed by | Rows |
|---|---|---|---|
| 01 | `01-detector-rules.json` | the classification pass injected into P7 — what enters a protected state, and what evidence it cites | 23 entries (19 `basis: detector` + 4 `basis: safety_domain`) · 6 refused · 6 uncertain |
| 02 | `02-identifier-classes.json` | the gate's redaction step — the closed list behind P7's opaque `identifier_class` string | 11 classes · 8 non-members · 2 refused · 2 uncertain |
| 03 | `03-redaction-transforms.json` | the same step — the named procedure each class applies; P7 ships **no default transform** | 4 transforms · 4 refused · 2 uncertain |

Every catalogue is a pair: `NN-name.json` is the source of truth; `NN-name.md` is a hand-written
companion (the top-level `render.py` does not cover this directory — its glob stops at the
top-level files — so **there is no generated markdown here**; `check.py` audits quotes in both
the JSON and the markdown).

---

## Decision state this catalogue is written against

- **D2 is RATIFIED** (2026-08-21, `overnight/council/DECISION-BRIEF.md` RATIFIED table, applied in
  `22-p1-p7-connection-contract.md` §3): P7's `ClassificationRecord`, keyed
  `(file_id, content_hash)`, is authoritative; `files.sensitivity_state` is its projection via
  P1's `set_sensitivity_state`; the fifth class is a gate outcome, not a file fact; and the
  detector is **P7's, injected, and unwritten** — no fourteenth part. This directory is that
  injected content. The dispatch prompt for this catalogue predates the ratification; its
  "if D2 is unset" branch is moot, and the rules were still authored storage-agnostic (the
  `write_shape` in catalogue 01) so they write through either home unchanged if the decision is
  ever revisited.
- **`basis` vocabulary** is P7's: `detector | safety_domain | user`. A catalogue rule is never
  `user` — user reclassification is a `user_confirmed` fact that outranks every rule here.
- **Safety domains** follow CONNECTION.md: `is_safety_domain` is a schema-row attribute (there is
  no `safety_for` edge), and under PR-2 a safety activation unlocks protection plus the small
  schema only. The four `saf-*` rules in catalogue 01 are the P7-side reading of that contract.
- **Handling classes are P7's five snake_case tokens and nothing else.** A ceiling in catalogue
  01 proposes at most a class; P7 assigns it. Absence of a classification resolves to
  `unreadable_unclassified`, never to `public_low` — that resolution is P7's own contract and no
  rule here restates or overrides it.

---

## How P7 consumes these — never as module-level constants

The same discipline as catalogues 01–07: **no module under `src/privacy/` may hold these rules,
label lists, patterns, or class tables at module level.** They are data the caller loads and
injects, through required keywords with no defaults — a default would be a place for an invented
value to hide. No regex in this directory is compiled in `src/`; a later caller compiles the
pattern strings it loads from here.

### The injection points

| Catalogue | Injected as | Into |
|---|---|---|
| 01 | the compiled rule set behind a classification callable — evaluated per file version over P4 observations, P5's stored sensitivity-signal rows, and P6's `active_domains` output | P7's classification path (the detector that D2 names as P7's, injected) |
| 02 | a class lookup: `class_id -> (transform_id, always_local, jurisdiction_dependent)` | `Gate.release`'s redaction step; `redaction_manifest` records the `class_id` per item |
| 03 | the named transform procedures, with `redaction_keep_n` injected | the same step; a class whose transform is not injected is a load error, never a passthrough |

Sketch, for the injection site (in the CALLER — never in `src/privacy/`):

```python
rules      = load('planning/deferred-catalogues/08-sensitivity-detector/01-detector-rules.json')
classes    = load('planning/deferred-catalogues/08-sensitivity-detector/02-identifier-classes.json')
transforms = load('planning/deferred-catalogues/08-sensitivity-detector/03-redaction-transforms.json')

classify = make_classifier(rules, slots=injected_slots)      # required kwarg, no default
redact   = make_redactor(classes, transforms,
                         redaction_keep_n=injected_keep_n)   # required kwarg, no default
```

A fired rule emits the `write_shape` catalogue 01 states: rule id, kind, basis, the protected
boolean, a handling-class **ceiling** (a proposal — P7 assigns the class), and `evidence_refs`
as P4 `observation_key`s — non-empty whenever `basis = detector`, per P7's own contract. The
write path is D2's: through P7's `ClassificationRecord`, projected to `files.sensitivity_state`
by P1's `set_sensitivity_state`. This catalogue invents no P7 column and no event type.

### Injected slots — every count is named, none has a default

| Slot | File | Meaning |
|---|---|---|
| `min_label_hits` | 01 | distinct labels from a rule's list that must be observed, at word boundaries |
| `min_value_bearing_labels` | 01 | matched labels that must sit beside a populated value — the completed-vs-blank-form discriminator |
| `min_code_lines` | 01 | consecutive code-shaped lines that make a backup-code grid |
| `min_populated_rows` | 01 | populated data rows a tabular signal requires |
| `min_secret_assignments` | 01 | secret-named assignments with non-placeholder values an env-style file requires |
| `tax_form_identifier_gazetteer` | 01 | jurisdiction tax-form identifiers as values — R5 owns the values |
| `national_id_label_gazetteer` | 01 | jurisdiction labels (and per-label value shapes) for national identifiers — R5 |
| `account_locator_patterns` | 01 | jurisdiction account-locator value shapes — R5 |
| `legal_caption_gazetteer` | 01 | jurisdiction court-caption wordings extending the generic markers held here — R5 |
| `redaction_keep_n` | 03 | trailing characters `keep_last_n` retains |

---

## What `check.py` asserts

Not that the files parse — that every entry behaves:

1. **No numeric value anywhere in the three JSONs** (booleans excepted) — every count is a named
   injected slot. Digits inside pattern *strings* describe document formats (an MRZ line's
   length band, a backup code's shape), never a decision threshold; the distinction is argued in
   `RESEARCH.md`.
2. Ids unique across all three files; every detector rule has a non-empty `never_alone`;
   `basis` closed to `detector | safety_domain`; `basis: detector` requires a kind from the
   closed kind vocabulary and non-empty `evidence_refs_shape`; `basis: safety_domain` requires
   kind `null`, one of the four safety domains, and `protected: true`.
3. Every one of `00`'s five protected kinds has at least one rule.
4. Handling-class vocabulary is exactly P7's five tokens; near-miss respellings fail at token
   boundaries.
5. Every identifier class names a transform that exists; `always_local` classes use a dropping
   transform; every transform names both context fields in `preserves` and is
   `reversible_locally`.
6. Provenance vocabulary is exactly `design | inference | proposal`.
7. Every referenced injected slot resolves to a declared one.
8. **No fabricated quotes**: every structured `design_cite` and every long double-quoted span in
   the JSONs *and* in these markdown files exists verbatim (whitespace-normalized) in its named
   source. The checker was negative-tested during the salvage audit: six seeded defects
   (fabricated quote, numeric threshold, near-miss respelling, undeclared slot, duplicate id,
   out-of-vocabulary ceiling) were each reported.

Run it:

```bash
cd 'planning/deferred-catalogues/08-sensitivity-detector'
python3 check.py
```

---

## What these files deliberately do not contain

- **Jurisdiction values** — tax-form identifiers, national-ID label wordings and value shapes,
  account-locator shapes, localized captions. This catalogue holds the *types*; R5 holds one
  jurisdiction's *values*, injected per deployment (D4: `jurisdiction` is a value, never a
  field).
- **A protected-characteristics gazetteer** — refused on principle in all three files; the
  detect-to-protect versus decline-to-model question is Joseph's and stays open
  (`RESEARCH.md`, NEEDS-JOSEPH).
- **Gazetteer contents** for institutions and courses (R4/P6), **date and term patterns** (P6),
  and **personal-data patterns on the extraction side** (catalogue 06 refused them; these
  classes exist on the *gate* side, where the span is located in order not to send it).
- **P7 mechanics** — no new columns, no event types, no gate signatures, no numeric ceilings.
- **Handling-class assignments on domain-catalogue rows** — `_CONTRACT.md` rule 5 stands; the
  ceilings here are P7-side proposals inside P7's own injected content, which is the one place
  the five tokens legitimately appear as data.

## NEEDS JOSEPH

Lives in [`RESEARCH.md`](RESEARCH.md), on disk deliberately. Twelve open items, three of them
required by the dispatch (detector caller/owner remainder, the fifth-class remainder after D2,
the characteristic-category question). None blocks the build: every catalogue loads and every
check passes with all of them unresolved.

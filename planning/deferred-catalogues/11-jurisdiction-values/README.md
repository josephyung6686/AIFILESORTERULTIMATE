# Catalogue 11 — jurisdiction-dependent values (R5)

One jurisdiction's names for tax forms, identity documents, courts, permits and healthcare
record types — as **values** of jurisdiction-neutral fields, packed per deployment. This
catalogue exists because the design deliberately never descends to this level: `00` contains
zero occurrences of jurisdiction, country, locale, GDPR, HIPAA, or United States (verified
mechanically 2026-08-22), while recognition in finance/legal/government cannot complete without
somebody naming the forms.

Authored 2026-08-22 by R5. Nothing is committed by the authoring agent — Joseph reviews and
commits.

Authority on conflict: `planning/00-database-agent-product-design.md` (`00`) wins, then
`planning/prompts/ALIGNMENT.md`, then `planning/domains/CONNECTION.md`, then the R5 dispatch
prompt (`planning/prompts/05-jurisdiction-values.md`).

Quote convention: every `quote` in this directory's JSONs is verbatim in its named source file
and `check.py` verifies that mechanically on every run (whitespace-normalized for wrapped
markdown). Fabricated quotations are a test failure here.

---

## The decision state this catalogue is built on

**D4 is ratified in shape and open in member.** The RATIFIED table
(`planning/overnight/council/DECISION-BRIEF.md`, applied at `planning/domains/_CONTRACT.md`
rule 9): "`jurisdiction` is a **value, never a field name and never a destination dimension**.
One jurisdiction's gazetteers in v1, injected." The same brief leaves *which* jurisdiction to
Joseph — "v1 ships one jurisdiction's gazetteers, injected per deployment; the list is decided
when P10 is planned" — and the two bodies of evidence point opposite ways (the design's worked
examples are US-shaped; the overnight catalogue's prose is UK-shaped; `RESEARCH.md` section 3
holds the recounts). **This catalogue therefore ships the file shape, a two-row shape-example
seed, and two pack sketches — and no deployable pack.** Picking silently is the one move the
dispatch prompt forbids. See `PACKS.md` for the registry and the ratification protocol, and
`RESEARCH.md` NEEDS-JOSEPH for the question as put to Joseph.

## The field/value split, which is the whole design basis

`00` §3.12: "The system may create new values when it sees a new course, project, company,
university, or event, but it should not invent new fields automatically." And: "Fields define
the long-term organization language of the product; values are the changing, user-specific
content discovered from files."

What varies by jurisdiction is **values**. `record_type` is a field and is jurisdiction-neutral;
`W-2`, `P60`, `VAT return` are values of it, loaded per deployment. The seat record states the
altitude rule precisely: "the design says `record type`, the catalogue wants to know whether
that record is a W-2 or a P60" (`seat-design-reading.md`) — this catalogue is the one place in
the repo allowed to descend below the design's altitude, and the descent produces **data**, not
schema. Fields stay in `planning/domains/canonical_fields.json`; nothing here mints one, and
`field_pending_R1` files (for values of D1-deferred identity/medical/legal fields) explicitly
cannot land fact-side until Joseph authors those fields (`_SCHEMA.md`).

## Never a dimension — enforced, not promised

A tree that branches on country is P10's one-way door (D4's only deadline). Three mechanical
guards in `check.py`:

- no `field_key` in this directory is `jurisdiction`, ends `_jurisdiction`, or starts
  `jurisdiction_` — and neither is any key in `canonical_fields.json`, so P10 cannot discover a
  jurisdiction dimension through the canonical table either;
- no JSON in this directory contains a `dimension_order` key at all — the concept is
  inexpressible here;
- `jurisdiction` appears only as a lowercase **tag on rows and packs** — a value, exactly as
  ratified.

The legacy 574 did smuggle jurisdiction into field names — 29 fields literally named
`jurisdiction`, 6 variants, and 6 jurisdiction-named `dimension_order` members (4 mirroring
those fields, 2 compound names existing only in a `dimension_order`) — all catalogued for
deletion/rename in `field-hygiene.md`. They are superseded by R1's roster (`_CONTRACT.md` R0
delta) and none survives into the canonical list (verified).

## How a pack is consumed — never as module-level constants

Same injection discipline as catalogues 01–10: packs are **data the caller loads and injects**;
required argument, no default — a default is where an invented list would hide. One pack per
deployment (D4). Two consumers:

- **P6 fact resolution** (value rows): injected at fact-resolver construction beside R4's
  gazetteers; word-boundary matched; a hit is a ranked §3.7 candidate, never a fact alone, and
  constitutionally never-alone for schema activation (CONNECTION.md section 4, step 2). Never
  P5's — P5 observes text; naming a form is a fact-layer job.
- **P7's injected detector set** (gate projections): catalogue 08 declares four slots it
  assigns to R5 — `tax_form_identifier_gazetteer`, `national_id_label_gazetteer`,
  `account_locator_patterns`, `legal_caption_gazetteer`. The pack loader projects them from
  rows' `gate_slots` declarations. Catalogue 08 owns every rule, signal, threshold and regex;
  this catalogue owns one jurisdiction's names. A row's `detector_hook` is a pointer into
  catalogue 08, never a rule of its own.

## Safety does not depend on the pack

Binding, and the reason an unshipped pack is a quality problem rather than a safety problem:

- `00`: "Finance, identity, medical, and legal material should be implemented first as safety
  domains, meaning the system detects and protects them before any cloud or automated placement
  decision is allowed." Safety activation runs on catalogue 08's shape detectors (MRZ lines,
  caption structure, label-plus-populated-value conjunctions, generic English markers) — none of
  which waits on a jurisdiction's form name.
- `00`: "Rare but sensitive files such as passports, visas, and legal documents may be surfaced
  as protected records even when they do not meet a normal group-size threshold." Protected
  Records is reachable with an empty pack.
- P7's SPEC: "Absence of a classification resolves to `unreadable_unclassified`, never to
  `public_low`." A UK user with a US-only list gets refusal-shaped failure, not exposure — the
  risk seat's verdict verbatim: "An unsupported jurisdiction fails toward refusal, not toward
  exposure." Its own caveat is preserved with it: that reassurance rests on P7 Task 3's absence
  rule, which is contract but not yet built; if a classifier ever defaulted unrecognised
  document types to `public_low`, this catalogue's absence would become dangerous instead of
  merely lossy.

What absence *does* cost is honesty at the residual surface — which is `unsupported-region.md`'s
one string.

## Boundaries with the neighbouring catalogues

- **R4 (`../10-gazetteers/`)** owns institution *names* (schools, orgs, financial institutions
  behind Finance's `institution`). This catalogue owns **form types, court names, statute
  labels, permit names** — the R4 README records the same boundary from the other side. The
  jurisdiction fork is one decision governing both: Joseph's answer picks R4's register and
  this catalogue's pack together.
- **R6 (`../12-academic-capture-patterns/`)** owns academic calendar tokens. R6 has landed with
  twelve term-pattern families — including `Michaelmas Term 2024`, which is **design** (`00`
  §3.10: "Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024 require
  dedicated patterns rather than generic parsing") and survives any pack choice, US included.
  This catalogue adds **no** calendar tokens; `check.py` guards the Michaelmas pattern's
  survival and this ownership. (The dispatch prompt's "beyond R6's three" predates R6's
  landing; the recorded state is followed.)
- **R2 (`../08-sensitivity-detector/`)** owns detection: rules, signals, thresholds, redaction.
  Its `jurisdiction_dependent: true` identifier classes name R5 as owner of label wordings and
  value shapes per jurisdiction; those arrive with the chosen pack as `gate_label` rows.
- **R3 (`../09-residual-library/`)** owns the nine residual templates and their slots. The
  `unsupported_region_copy` string is carried here (it is jurisdiction data — it exists because
  a pack is a partial map of the world) and surfaced through P10/P11's residual machinery.

## Files

| file | what |
|---|---|
| `_SCHEMA.md` | pack, value-row and gate-label-row shapes; `field_pending_R1`; what is inexpressible |
| `PACKS.md` | registry — v1 **awaiting Joseph**; `00-example` shape seed; us/uk sketched; ratification protocol |
| `00-example/` | the shape-example pack: `_pack.json` + `record_type.json` (W-2 / P60, both `proposal`) |
| `unsupported-region.md` | the one honesty string for unmodelled regions — slot contract + proposed wording (`proposal`) |
| `field-hygiene.md` | the 574 scan: field names that smuggled a jurisdiction, listed for deletion/rename |
| `RESEARCH.md` | the situation, sources, recounts, the six value categories, the two pack sketches, NEEDS-JOSEPH, audit record |
| `check.py` | the gate — run `python3 check.py`; non-zero on any failure |

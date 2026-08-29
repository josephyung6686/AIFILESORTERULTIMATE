# Catalogue 10 — research record: sources, universe choices, CJK slot, NEEDS-JOSEPH

First authored 2026-08-21 by R4; that run was killed mid-task by a session limit before this file
was written. A second R4 pass (2026-08-22) treated everything already on disk as an untrusted
draft, re-verified all of it (the audit record is at the bottom), fixed what had gone stale, and
wrote this file. Nothing is committed by the authoring agent — Joseph reviews and commits.

---

## 1. Sources

**Everything in the four JSONs is design-derived. No external source was opened.** Every entry's
`source_kind` is `design_example`; every `quote` is mechanically verified verbatim against its
named file by `check.py`. This is deliberate and worth stating the way `../README.md` states its
sourcing discipline: the external registers named below as candidate universes (DAPIP, IPEDS, the
OfS register, FDIC BankFind, the FCA register, DOAJ, the ISSN registry, CORE, DBLP) are
**candidates recorded for a decision, not sources consulted** — no page was retrieved, nothing
from them is quoted, and no row depends on them. A v1 seed built only from the design's own worked
examples needs no external evidence; the moment a real register backs a file, its rows carry
`source_kind: official_list` and the register citation comes with them.

Design sources read and cited:

| source | what it contributed |
|---|---|
| `planning/00-database-agent-product-design.md` | every quoted span; the word-boundary rule and the MIT/UNC adversarial pair; the `U Chicago` alias triple; the Columbia six-role sentence; the §3.5 context requirement; §3.12 value auto-creation; §2.7 CJK OCR; the worked entities (Columbia, UChicago, Wash U, Duke, Cornell, Georgetown Prep, EY, BUSIB 4300, PHYS1401) |
| `planning/01-product-design-structured.md` | § locators only (per CONNECTION.md's convention: § numbers locate topics in 01's rendering; quotes are verbatim from 00) |
| `planning/parts/P6-facts-facets/SPEC.md` | the deferred row this catalogue fills; §8.5's adversarial suite naming submit/uncertainty; `unresolved` as the abstention row |
| `planning/domains/CONNECTION.md` | sections 4 (activation steps 1–2; gazetteer hits as word-boundary inputs; never-alone), 5 (`role_split` edge), 6 (one canonical field list; value-level aliases only) |
| `planning/domains/canonical_fields.json` | R1a's landed table — every `backs_fields` key verified resolving (see seams below) |
| `planning/domains/_CONTRACT.md` | rules 1 (provenance), 3 (no numbers), 4 (`validated` claims a rule will confirm), 9 (D4 ratified: jurisdiction is a value) |
| `planning/overnight/council/DECISION-BRIEF.md` | D4's two-part state: ratified that jurisdiction is a value never a field never a destination dimension, one jurisdiction's gazetteers injected in v1; **which** jurisdiction is recorded open ("design's examples are US, the catalogue authors wrote UK") |
| `planning/04-resolutions.md` | S3: Career fields stay deferred — why file 02 must not name a company field |
| `planning/deferred-catalogues/README.md` | the injection pattern (catalogue 01's row is the precedent: P6-only, never P5, never module-level constants) |
| `planning/deferred-catalogues/12-academic-capture-patterns/` | R6's landed files — the course-code seam is now concrete (section 4) |

## 2. Universe choices, per file

The validation procedure's first condition is a **stated universe** (PROCEDURE.md). What each file
chose and why:

- **01-schools** — `design_examples` in v1: only institutions the design names or implies (eight
  rows). The complete version is **one jurisdiction's official institution register, injected**
  (D4's ratified shape). Which register is the open half of D4: US candidates are the Dept. of
  Education's accreditation database (DAPIP) or the IPEDS institution list; the UK candidate is
  the OfS register. The design's worked examples are US-shaped; the overnight catalogue's prose
  was UK-shaped — that is exactly DECISION-BRIEF D4's recorded fork, not this catalogue's to
  close. Secondary schools are in scope (`00` names Georgetown Prep as course-material context) but
  have no clean single register anywhere; user-add is the expected main route for them.
- **02-orgs-roles** — `design_examples` in v1: one row (EY, the design's only named firm).
  **There is no honest complete universe for employers and clients** — they are user-specific by
  nature, and `00`'s mechanism for them is §3.12 value auto-creation plus user confirmation. The
  one bounded org sub-universe worth a decision is a national register of regulated financial
  institutions backing Finance's `institution` (FDIC BankFind / FCA register — the same
  jurisdiction fork as file 01). Shipping no employer list at all in v1 is a live option and is
  recorded as such, not decided.
- **03-research-venues** — `UNDECIDED`, and the seed is **empty on purpose**. `00` names the
  fields (`lab`, `venue`) and zero values. Candidate venue universes exist with stated selection
  rules (DOAJ; the ISSN registry filtered by a distinctiveness rule; CORE/DBLP for conferences),
  but every one of them requires a decision about single-common-word journal titles (`Cell`,
  `Nature`, `Science`, `Blood`) that word-boundary matching cannot make safe. Labs likely have no
  shippable universe at all (they are named after PIs — the refused person-name class — or are
  internal names). The stronger route to `venue` may be identifier metadata (catalogue 06's DOIs
  and ISSNs) rather than name matching; that fork is `unc-venue-via-identifiers`.
- **04-course-code-formats** — format families the design's own examples exhibit (`DEPT NNNN`
  from `BUSIB 4300`; `DEPTNNNN` from `PHYS1401`). Explicitly **not** a list of courses (§3.12:
  courses auto-create) and not a survey of every registrar's convention on earth: families are
  added when a corpus shows them. R6's landed sibling file admits a third family (`1234.DEPT`);
  see the seam in section 4.

The refusals — person names, every company on earth, every GitHub org, unfiltered Wikidata, NAICS,
email/web domains, generic institution nouns, bare `Georgetown` — each carry their false-positive
argument in the `refused[]` array of their own file, per this directory's convention.

## 3. The CJK slot

`00` requires OCR "including CJK where required" (§2.7) and its own worked corpus contains "an
existing Chinese University Application Materials directory" (§5.2) — so CJK institution names
**will** appear in real evidence, and a Latin-only gazetteer silently misses them. What v1 does
about that, and what it leaves open:

- **Representable today:** every alias carries `script`; every row carries `scripts`. A CJK alias
  (`清华大学`) needs no schema change, and `check.py` proves it with a fixture.
- **Matchable when the slot fills:** word-boundary semantics are Latin-script — undelimited CJK
  prose has no word boundaries — so CJK aliases require a segmentation-aware matcher. That matcher
  is a **named, unfilled injection slot** (`cjk_matcher`) in every file's `match_rule`, exactly
  parallel to the numeric threshold slots: naming the hole rather than papering over it.
- **Open:** which CJK alias sets ship, and when the matcher slot is filled (`unc-cjk-aliases`).
  Guessing transliterations without a corpus would be padding — the failure mode this directory
  exists to avoid.

## 4. Seams with concurrent workstreams (state as of 2026-08-22)

- **R1a (`planning/domains/canonical_fields.json`) — LANDED.** The first draft was written before
  it existed and said so; this pass verified every `backs_fields` key resolves in the table and
  made `check.py` assert it permanently. Confirmations: `school`/`target_university`/
  `target_school` carry `gazetteer: "schools"`; `our_firm`/`client`/`institution` carry
  `gazetteer: "orgs"`. Two seams, recorded but not resolved here: (a) R1a tags `lab` and `venue`
  `gazetteer: "orgs"` while this catalogue keeps them in a separate research-spine file
  (03's `unc-r1a-gazetteer-tag`); (b) R1a holds `target_school` as a key referenced by no schema,
  with a recorded recommendation to fold it into `target_university` — this gazetteer backs
  whichever keys survive. One clarification to prevent a false alarm: R1a's field rows carry an
  `aliases` array of *spellings that must NOT become new keys* — that is a key-hygiene record, not
  the field-level aliasing CONNECTION.md forbids; the value-level aliases (`U Chicago` →
  `University of Chicago`) live only here and in P6's values table.
- **R6 (`12-academic-capture-patterns/`) — LANDED**, including its own
  `02-course-code-formats.json`. Both dispatch briefs assigned course-code formats, and both
  agents delivered, so the product currently has **two** course-code-format catalogues. They agree
  on the core families and the HW/ZIP/year refusals; the concrete deltas and the merge
  recommendation (R6's file is the stronger design — unconditional dept stoplist, per-entry
  context requirement, `context_check_failed` as the unresolved reason) are recorded in file 04's
  `unc-r6-merge-owner`. At re-verification this catalogue's `term_collision_guard` gained the
  all-caps season/month tokens so the known gap (`FALL 2025` matching `DEPT NNNN`'s shape) is
  closed on this side too pending the merge. File 04 consumes R6's context-term catalogue by
  reference and authors none of its own.
- **R5 (`11-jurisdiction-values/`) — NOT LANDED** at re-verification. The boundary stands as its
  dispatch brief states it: R5 owns jurisdiction-varying form types, court names, statute labels
  and permit names, and does not duplicate institution lists; institution *names* live here.
- **Catalogues 01–07** — untouched, and the boundary holds mechanically: `BUSIB 4300` matches
  nothing there, and nothing there can name a school.

## 5. NEEDS-JOSEPH

Every open item lives in the `uncertain[]` array of its own JSON file with the argument on both
sides; this is the consolidated index. None blocks the build — `check.py` passes with all of them
unresolved. **The headline question is the first row: which lists actually ship in v1.**

| # | id (file) | question |
|---|---|---|
| 1 | `unc-v1-universe` (01) | Which jurisdiction's official institution register backs the schools file in v1 — DAPIP/IPEDS (US) or the OfS register (UK)? D4 is ratified in shape (one jurisdiction, injected); this is the open half. Decides more than any other row what "ship" means for this catalogue. |
| 2 | `unc-org-list-at-all` (02) | Ship any employer/client list beyond user-add at all? The recorded lean: ship none; let repeated user-approved values become the user's own gazetteer (PROCEDURE.md condition 8). |
| 3 | `unc-bank-register` (02) | Does a national register of regulated financial institutions back Finance's `institution` in v1 (FDIC BankFind / FCA register — same fork as #1)? |
| 4 | `unc-journal-universe` (03) | Ship a bounded journal slice for `venue`, or ship nothing and rely on identifiers plus user-add? Any slice needs a rule for single-common-word titles (`Cell`). |
| 5 | `unc-conference-universe` (03) | Ship a conference list (CORE/DBLP)? Acronym-heavy; every entry needs the case rule plus a homonym record. |
| 6 | `unc-venue-via-identifiers` (03) | Is the primary `venue` route catalogue-06 identifier metadata rather than name matching? Affects whether a venue gazetteer ever needs to be big. |
| 7 | `unc-lab-ceiling` (03) | With the labs list empty, `lab` cannot carry `reliability_ceiling: validated` via the gazetteer route — R1b must not stamp it. Standing constraint until a rule exists. |
| 8 | `unc-r6-merge-owner` (04) | Two course-code-format catalogues exist (10/04 and R6's 12/02). One owner must win at merge; recommendation recorded: R6's. |
| 9 | `unc-r1a-gazetteer-tag` (03) | R1a tags `lab`/`venue` as `gazetteer: "orgs"`; this catalogue splits them into a research file. Merge 03 into 02, or extend R1a's tag vocabulary? |
| 10 | `unc-cjk-aliases` (01) | Which CJK alias sets ship, and when is the `cjk_matcher` slot filled? |
| 11 | `unc-secondary-schools` (01) | Stated universe for secondary schools (no clean register exists; user-add is the likely main route). |
| 12 | `unc-programmes` (01) | Are degree programmes gazetteer content? No canonical field takes them today; gazetteering them would mint a field by the back door. Flagged for R1a. |
| 13 | `unc-georgetown-university` (01) | Seed Georgetown University so bare `Georgetown` can be ranked instead of refused? |
| 14 | `unc-career-company-field` (02) | When Career fields land (04-resolutions S3; owed before P10), which key does the orgs gazetteer back? |
| 15 | `unc-number-dot-forms`, `unc-hyphenated-forms`, `unc-lowercase-forms`, `unc-uk-module-codes` (04) | Candidate course-code families deliberately not admitted in v1 — each waits on a corpus sighting, not a guess. Largely subsumed by #8 if R6's file becomes the owner. |

## 6. Verification record (the salvage audit, 2026-08-22)

What the second pass verified before touching anything, per the salvage instruction to treat the
draft as untrusted:

- **Quote authenticity, mechanical:** `check.py` walks every `quote` in the four JSONs and
  asserts the span exists verbatim in its named source (`00`, `P6-SPEC`, `CONNECTION`) — passing
  before and after this pass's edits. Quoted spans in the markdown files and in JSON prose fields
  (notes, reasons), which the checker does not walk, were each grep-verified against their sources
  by hand this pass — fourteen spans against `00`, the deferred-row wording against P6 SPEC line
  633, the D4 fork wording against DECISION-BRIEF, the injection-precedent wording against
  `../README.md`, and R5's boundary wording against its brief. No fabricated quotation was found.
- **§ locator audit:** every claimed § number was located in `01-product-design-structured.md`'s
  rendering and confirmed to contain its quote or topic (including the two non-obvious ones:
  §4.3 for the generic-hubs sentence, §3.12 for value auto-creation).
- **Decision-state claims:** D4 (ratified shape + open jurisdiction) and D6 (`subject`) verified
  against DECISION-BRIEF.md and `_CONTRACT.md` rules 8–9 as recorded — nothing re-opened, nothing
  closed.
- **Checker liveness, by mutation:** a bogus `backs_fields` key makes `check.py` fail with the
  intended message and the tree restores clean; the season/month guard additions were proven
  load-bearing by showing `FALL 2025` / `MAY 2024` / `SPRING 2026` / `WS 2024` match the raw
  `DEPT NNNN` shape and are excluded only by the guard.
- **What changed in the salvage pass:** this file written; stale "canonical_fields.json does not
  exist yet" claims replaced with verified-resolving statements in all four JSONs, `README.md` and
  `_SCHEMA.md`; the R6 seam updated from "R6's brief lists…" to the landed reality with concrete
  deltas (`unc-r6-merge-owner` added); `unc-r1a-gazetteer-tag` added; the term-collision guard
  extended with season/month/German-semester tokens; `check.py` gained the `backs_fields`
  resolution check and seven course-format negatives. Everything else in the draft survived its
  audit unchanged.

# What "validated gazetteer" means operationally

`00` §3.7: facet extraction uses "rules, metadata, validated gazetteers, and document structure"
before heavyweight models. P6's SPEC defers exactly this: "Gazetteer contents and the validation
procedure that makes them \"validated\"". This file is that procedure — a definition a test can
run, not an adjective.

Authored 2026-08-21 by R4. Joseph reviews and commits.

---

## The definition

A gazetteer in this directory is **validated** when all nine conditions below hold. Conditions
marked **[mechanical]** are enforced by `check.py` today; conditions marked **[consumer]** are
contract on P6's use of the data and are testable in P6's §8.5 suite once P6 exists. None is
aspirational — each names its test.

### 1. Stated universe — [mechanical]

Every file carries a non-empty `universe` naming what a complete version would contain. v1 seeds
state `design_examples`. "Some organizations I thought of" is not a universe; "one jurisdiction's
official institution register, injected (D4)" is. The check asserts the key exists and is
non-empty; review asserts it is honest.

### 2. Per-row provenance, mechanically verified — [mechanical]

Every row carries `provenance ∈ {design, inference, proposal}` (the repo vocabulary, `_CONTRACT.md`
rule 1) and `source_kind ∈ {design_example, official_list, wikidata, user_approved, proposal}`
(the sourcing question the dispatch brief asks — kept as a separate key so the two vocabularies
never blur). Every `design_cite.quote` — and every `quote` anywhere in the file — must exist
verbatim in its named source file. `check.py` loads the sources and fails on any missing span.
A fabricated quotation is this repo's worst recorded failure; here it is a test failure, not a
review finding.

### 3. Word-boundary matching, as an invariant — [mechanical + consumer]

Every file's `match_rule.matching` is `word_boundary`, and no row may carry substring semantics.
The reference matcher in `check.py` implements the boundary (non-word-character lookaround over
`[A-Za-z0-9_]`) and the design's own adversarial pair is asserted against **live rows**: the
`MIT` alias finds nothing in "please submit" or "SUBMIT", the `UNC` alias nothing in
"uncertainty". §3.7: "It should use word-boundary matching rather than substring matching."
Consumers inherit the invariant: an injected matcher that substring-matches fails P6's §8.5
adversarial suite (MIT-in-submit is a named case there).

### 4. Value-level alias sets that round-trip — [mechanical]

Aliases are aliases of a **value**, never of a field (CONNECTION.md section 6: there are no field
aliases). Each alias, matched in context by the reference matcher, resolves to its row's
`canonical`. The design's worked triple is the acceptance case and `check.py` runs it: raw
`U Chicago` → canonical `University of Chicago`, with `UChicago` a display alias — "If a document
says U Chicago, the raw observation remains exactly that wording, while a resolver may normalize
it to University of Chicago and the user may later choose to display it as UChicago." The raw
observation is never rewritten (P4's contract); the canonical is the resolver's normalized value.

### 5. Collision honesty — [mechanical]

An alias that resolves to more than one canonical (across all entity files, folded per its case
rule) must be covered by a `homonyms` row naming the readings, or the check fails. An alias marked
`ambiguous` must name its homonym record. This is the guard the dispatch brief asks for: "aliases
don't collide across canonicals without a recorded homonym." A homonym record also covers the
class word-boundary cannot fix — `Columbia` inside `British Columbia`, `MIT` inside `MIT License`
— where the hit is clean and the entity is wrong; the containment there is condition 7, and
recording it is what keeps the list honest about its own limits.

### 6. Case rule per alias — [mechanical]

Name aliases match case-insensitively. Acronym aliases (`MIT`, `UNC`, `EY`, `WUSTL`) are
`case_sensitive: true` — lowercase `mit` is a German preposition, not a school, and the check
asserts the German sentence produces no hit.

### 7. A match is not a fact — [consumer]

A gazetteer hit is a **candidate**, exactly parallel to `00` §3.5's course-code shape: match
**plus** context, or no fact.

- It enters §3.7's ranking with positional weighting, and fills a facet only past the injected
  `min_score` **and** `min_margin` slots. Failing either leaves the facet unfilled — a clue, never
  a fill.
- It is constitutionally **never-alone** for activation: "A university name alone should not
  create a group because Columbia can appear as an authoring school, course provider, target
  institution, employer, research venue, or merely a cited organization." CONNECTION.md's
  activation step 2 strikes any schema whose entire support is a gazetteer hit.
- **Which field it may fill is the field's decision, not the row's.** One entity list backs
  role-split fields (`school` / `target_university`; `our_firm` / `client`); the row carries no
  role, and the field's own context rule decides. A schools hit in an essay's addressee context
  supports `target_university`; the same name in a transcript header supports `school`.
- A format hit (file 04) yields a `subject` fact **only** with §3.5 context — the five quoted
  literals as floor, R6's catalogue as the extension.

This is what licenses a schema row to stamp `reliability_ceiling: validated` on a
gazetteer-backed field: the rule that will confirm it actually exists (gazetteer + context +
ranking). Where the gazetteer is empty (03, labs), that licence does not exist and R1b must not
claim it — recorded in 03's `unc-lab-ceiling`.

### 8. Gazetteer misses never block stronger evidence — [consumer]

`00` §3.12: "The system may create new values when it sees a new course, project, company,
university, or event, but it should not invent new fields automatically." Consequences, in order
of strength:

- A **user** entry, rename, merge, or correction is `user_confirmed` regardless of any list.
- A **labeled form field** ("University: …") or document title naming an institution is `direct`
  regardless of any list.
- The gazetteer feeds only the `validated` path. Absence from the list caps nothing above it and
  a hit proves nothing by itself.
- **User-add lifecycle:** a new value auto-creates in P6's `values` table on first sight
  (`source_kind: user_approved` once confirmed). Repeated user-approved values are candidates for
  admission into the deployed gazetteer at review time — admission is a review act (Joseph or the
  user), never automatic, because a shipped list is a precision instrument and auto-admission
  would erode exactly the property that makes `validated` mean something.

### 9. Scripts declared; CJK representable today, matchable when the slot fills — [mechanical + consumer]

Every alias carries `script`; every row carries `scripts`. v1 rows are Latin. `00` §2.7 requires
OCR "including CJK where required", so CJK institution names **will** appear in evidence; a
Latin-only gazetteer silently misses them. The schema therefore admits a CJK alias with no shape
change, and the matcher gap is a named slot (`cjk_matcher` — word boundaries are meaningless in
undelimited CJK text and a segmentation-aware matcher must be injected). `check.py` proves the
representability half with a fixture row exercised through the schema; the matcher half is open
and flagged (RESEARCH.md, NEEDS-JOSEPH).

---

## What is deliberately NOT part of the definition

- **Numbers.** No minimum score, margin, weight, or list-size target appears anywhere in this
  directory. §3.7 requires the thresholds; their values are P6's deferred rows, injected. The
  check walks every JSON and fails on any numeric value at all.
- **Completeness.** A validated gazetteer may be tiny. `03-research-venues.json` is validated
  with zero entries: its universe question is stated, its refusals are argued, and it claims
  nothing it cannot confirm. Padding a list to look finished is the failure mode; `status: seed`
  and `schema_only` are the honest states.
- **Role.** Never on a row (condition 7).
- **Jurisdiction.** A value, never a field, never a destination dimension (D4, ratified). The
  jurisdiction fork changes which rows a deployment injects; it never changes this procedure.

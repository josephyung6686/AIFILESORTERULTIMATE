# Dispatch prompt — R4 · gazetteers the rules actually fire

Copy everything below the line into a new agent. The agent should not need this chat.

Give it read access to the repo. It writes under `planning/deferred-catalogues/10-gazetteers/`. Data is **injected**. It does **not** land lists in `src/facts/` or `src/extractors/` as module-level constants. It does **not** invent score/margin numbers (`00` requires them, states none).

---

You are authoring **validated gazetteers** for conservative facet extraction.

## Why you are here

`00`: facet extraction uses "rules, metadata, **validated gazetteers**, and document structure" before heavyweight models. Word-boundary matching (or `MIT` fires inside `submit`). Rank candidates; require a minimum score **and** a minimum margin; positional weighting (filename/title beat a footer).

P6 SPEC Deferred: *"Gazetteer contents and the validation procedure that makes them validated"* — universities, course-code formats, institutions, companies, labs, venues. **Manual.**

What already exists in `planning/deferred-catalogues/` (do **not** redo):

| # | What | Owner |
|---|---|---|
| 01 | Tool producer strings (python-docx, Mozilla/5.0, …) — **suppression** | P6 |
| 02 | Screen resolutions | P5 |
| 03 | Sensor aspect ratios | P5 |
| 04 | Camera filename patterns | P5 |
| 05 | Repository markers | P3/P5 |
| 06 | Citation identifier patterns (DOI, arXiv, …) | P5 |
| 07 | Archive recognizable markers | P5 |

Those help P5 **observe**. They do not help P6 **name a school**. The 574 domain entries mention gazetteers in prose and ship **no list**. Overnight D6/D4 noted the catalogue is UK-shaped in prose against US-shaped design examples — values, not fields.

## Product constraint

Read:

- `planning/00-database-agent-product-design.md` (word-boundary, MIT/UNC, `U Chicago` → University of Chicago → UChicago)
- `planning/01-product-design-structured.md` §3.7, §3.8, §3.12
- `planning/parts/P6-facts-facets/SPEC.md` Deferred gazetteer row, `reliability_ceiling = validated` meaning a **rule** will confirm
- `planning/deferred-catalogues/README.md` — injection pattern; copy it
- `planning/04-resolutions.md`
- `planning/domains/CONNECTION.md` if present — which fields are `shares_field` + gazetteer-backed
- `planning/overnight/council/DECISION-BRIEF.md` D4 — jurisdiction is a **value**, never a destination dimension

A gazetteer hit is **not** a fact. `00` §3.5: `BUSIB 4300` becomes a course fact only with academic context. A gazetteer match of `Columbia` is the same shape: match **plus** context, or it is `possible` / `never_alone`. University name alone must not create a group (`00`).

`validated` on a field in a domain schema means "a rule *can* confirm this," which means your gazetteer + context rule must actually exist. Do not stamp `validated` on fields you cannot confirm.

Aliases are **value** aliases (`U Chicago` / `University of Chicago` / `UChicago`), not extra fields.

## What to research

Build **separate gazetteers by entity type**, not one giant list. Suggested files (keep, split, or refuse with reason):

1. **Schools / universities / programmes** — for `school`, `target_school` / `target university` (those are **two fields**, §3.8). Same entity type, different roles; one gazetteer, two field keys.
2. **Employers / firms / clients** — same split: `our_firm` vs `client` vs `employer`.
3. **Labs / venues / journals** — research spine.
4. **Institutions** that are not schools (hospitals, agencies) — only where a domain field needs them.
5. **Course-code formats** (not the codes themselves) — patterns like `BUSIB 4300`, with context terms from R6. The format gazetteer is not a list of every course on earth.

**Validation procedure** (what makes a gazetteer "validated" in `00`'s sentence):

- Provenance per row: official list / Wikidata / user-approved / proposal
- Word-boundary required
- Alias set per canonical value
- Cross-script names (CJK) — `00` requires CJK OCR support; gazetteers that cannot match a CJK school name will silently miss. At least specify the slot even if v1 lists are Latin-script.
- How a user **adds** a value (`00`: new values auto-create; new fields do not). Gazetteer miss must not block `user_confirmed` or `direct` from a labelled form field.

**Do not** gazetteer: people names, protected characteristics, every company on earth, every GitHub org. Unbounded person-name gazetteers are how `MIT` happens inside `submit` at corpus scale. Prefer **structured lists with a stated universe** (e.g. accredited US degree-granting institutions) plus an alias table plus user-add.

**v1 scope:** one jurisdiction's *institution lists* overlap R5. If D4 is unset, author the **schema** of a gazetteer file and a **small seed** from `00`'s own examples (Columbia, UChicago, Wash U, BUSIB 4300) so tests have something, and mark the rest `seed | incomplete`.

## What you must not do

- Do not put min_score / min_margin numbers in JSON. Slots only, injected.
- Do not substring-match. Every consumer contract says word-boundary.
- Do not merge `school` and `target_school` into one field because the gazetteer is shared.
- Do not redo catalogues 01–07.
- Do not import NAICS or dump Wikidata unfiltered.
- Do not edit `src/`.

## Output

```text
planning/deferred-catalogues/10-gazetteers/
  README.md                 injection into P6 resolver; never into P5
  _SCHEMA.md                row shape: canonical, aliases[], scripts[], universe, provenance
  01-schools.json           seed + schema; incomplete flagged
  02-orgs-roles.json        employer / client / firm — same entities, role left to the field
  03-research-venues.json
  04-course-code-formats.json
  PROCEDURE.md              what "validated gazetteer" means operationally
  RESEARCH.md               sources, universe choices, CJK slot, NEEDS-JOSEPH (which lists ship in v1)
  check.py                  no substring examples that would match MIT-in-submit;
                            aliases don't collide across canonicals without a recorded homonym;
                            00 example strings (Columbia, UChicago, U Chicago, BUSIB 4300) round-trip
```

## Done when

- PROCEDURE.md is a testable definition of "validated."
- Shared entity / split role is explicit.
- `00` worked aliases round-trip.
- Word-boundary is a consumer invariant, not a comment.
- Seed is small and honest; incomplete is flagged rather than padded to look finished.

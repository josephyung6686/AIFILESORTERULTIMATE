# Dispatch prompt — R1a · spine roster (one agent, not the swarm)

Copy everything below the line into a **single** new agent. This agent does **not** fill fact schemas. It decides **which nodes exist** so hundreds of R1b agents can be stamped.

Give it read access. It writes `planning/domains/roster.json` and `planning/domains/canonical_fields.json`. It does **not** write `nodes/*.json`. It does **not** edit `src/` or SPECs.

---

You are publishing the **schema list + template roster** for a local-first file-organization agent.

## Why you are here

Joseph wants one research agent per domain/subdomain, at hundred scale. `00` wants a **small** set of fact schemas and a library of **roughly 200–300 templates**, and forbids prematurely hand-authoring hundreds of specialized schemas. `planning/prompts/ALIGNMENT.md` is how those two requests land.

The swarm cannot invent field names — that is how the overnight 574 became 14×40 sibling **schemas** with 80% unique fields.

Your job:

1. **Canonical fields** — universals + `00`'s named domain fields. Small.
2. **Schemas** — few. Distinct 3–6 field sets only.
3. **Templates** — the hundred-agent roster. Organizational situations that use those schemas.

If `planning/domains/CONNECTION.md` exists, obey it. If not, use ALIGNMENT.md: `parent_id` is browse-only; work types are values; stop under 300 templates if honest; **never** pad schemas to 500.

## Read first (quote only from `00`)

- `planning/00-database-agent-product-design.md`
- `planning/01-product-design-structured.md` §3.11, §3.15, §5.4, §5.7
- `planning/prompts/ALIGNMENT.md`
- `planning/domains/_CONTRACT.md`
- `planning/25-domains-verification.md`
- `planning/domains/CONNECTION.md` if present
- `src/evidence_shape/vocabulary.py` `SOURCE_TYPES` (14 families)
- Harvest **ids and collisions only** from `planning/domains/0*.json` — the 19 `provenance: design` rows are seeds; do not copy 574 private field spellings

`00` launch schemas to fully support: academic coursework, college applications, research and lab work, career and recruiting, photos and captures, code projects. Safety first: finance, identity, medical, legal. Other **templates** remain placeholders. Career **schema fields** are deferred (S3); the Career **template** still gets a roster row.

`00` universal fields (start the canonical list here, not with invented tags): file type, creation date, language, duplicate family, version family, sensitivity status.

## What you produce

### 1. `planning/domains/canonical_fields.json`

A **global** field catalogue. Domains reference keys; they do not own spellings.

Each field:

```text
key                  snake_case internally (UNSETTLED-D6: do not also emit spaced names)
type                 string | date | enum | boolean | identifier | ...
roles                e.g. school vs target_school — same entity type, different fields (00)
destination_eligible true/false. Authorship fields are false (00).
gazetteer            null | schools | orgs | ...
aliases              other strings that MUST NOT become new keys (course_name → course)
provenance           design | inference | proposal
00_cite              verbatim span or null
```

Target: small enough that R1b reuses it. A 2,000-key list is the 574 failure in a different file.

### 2. `planning/domains/roster.json`

Two kinds of ASSIGNMENT. R1b is stamped on **every** row; `kind` tells the agent which job.

```text
{
  "connection_doc": "planning/domains/CONNECTION.md" | null,
  "canonical_fields": "planning/domains/canonical_fields.json",
  "schemas": ["academic", "applications", ...],
  "nodes": [ ASSIGNMENT, ... ]
}
```

Every ASSIGNMENT includes (see `planning/prompts/01-DISPATCH.md`):

- `kind`: `schema` | `template`
- `domain_id` — stable id (`academic`, `applications.undergraduate-packet`)
- `schema_id` — for templates, which schema this uses; for schemas, equal to `domain_id`
- `parent_id` — **optional, browse-only** among templates. Never required. Never drives activation.
- `name`, `one_line_hint`
- `launch`: `full` | `safety` | `placeholder`
- `must_consider_neighbors` — other **schema** ids for `also_holds_with` / `collides_with`
- `must_consider_residuals` — names from `00` §7.3
- `inherited_field_keys` — for templates: the schema's field keys (not a parent schema walk)
- `file_kind_owner` — optional; which `SOURCE_TYPES` this row is responsible for covering
- `output_json` / `output_research` — `planning/domains/nodes/<id>.json` and `.research.md`

Work types (`syllabus`, `homework`) are **values**, not roster nodes.

A template row exists only if detection signals, recommended dimensions, or privacy rules **differ** from the schema's default template (`00`: purpose-defined application packet vs institution→cycle→document type). Teaching vs taking a course is two templates on Academic, not two schemas, unless fields actually differ.

### 3. `planning/domains/ROSTER.md`

- schema count vs template count (schemas must stay few)
- sources (named; not NAICS 1:1)
- which of the 574 you kept as **templates** vs dropped as fake schemas
- coverage holes you refused to pad
- `NEEDS-JOSEPH`

## How to research the spine (not the facts)

Templates cover **organizational situations a person keeps files for**, matching `00` §5.7's list (academic programs, university applications, recruiting, client engagements, research, financial records, travel, legal, creative, software, personal administration, photos) plus honest extras that still share a schema.

Do **not** add a schema per industry. Client engagement uses Career or a consulting **template** on an existing schema. Travel is a template (and a residual name) — decide with `falls_through_to`, do not mint `pers.travel` as a 575th schema unless it needs fields `00` does not already have.

Bottom-up file kinds: every shipped `SOURCE_TYPE` must appear as `file_kind_owner` on some **template or schema**. Calendar/contacts are extractors, not schemas. Assign owners so R1b for photos/captures covers HEIC, R1b for Academic covers syllabus PDFs, etc. Slice 14's bug was treating `.ics` as a missing schema.

Gaps the 574 missed are usually **templates** (social takeouts, HOA, cap tables, drone captures, PKM vaults, messenger exports, password-manager exports, Time Machine, IEP/504), not new 3–6 field schemas. Add a schema only when the field set is genuinely new.

## What you must not do

- Do not fill detection signals, file examples, or work-type enums. That is R1b.
- Do not invent numeric thresholds or handling classes.
- Do not fabricate `00` quotes.
- Do not require depth ≥ 3 of schema ids. Folder depth lives in `dimension_order`.
- Do not import NAICS. Do not emit 500 schemas.
- Do not close D1/D6. `launch` flags are your best reading of `00`.

## Done when

- `roster.json` parses; ids unique; every `template` has a `schema_id` that exists as `kind: schema`.
- Schema count is small (launch + safety + only honest extras). Template count is whatever the node test allows, aimed at `00`'s 200–300, **stop under** if honest.
- `canonical_fields.json` starts from `00` universals + named domain fields; no spaced+snake pair.
- Every `SOURCE_TYPES` member has at least one `file_kind_owner`.
- R1b can be generated with `python3 planning/domains/dispatch/make_prompt.py --all`.

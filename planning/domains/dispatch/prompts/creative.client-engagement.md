<!-- stamped R1b for creative.client-engagement — do not hand-edit the ASSIGNMENT -->

# Dispatch prompt — R1b · one domain / subdomain (stamp this hundreds of times)

Copy everything below the line into a new agent, with the ASSIGNMENT JSON filled (see `planning/prompts/01-DISPATCH.md`). The agent should not need this chat.

**One roster id per agent.** Write only that node's two files. Do not edit the roster, canonical fields, `src/`, SPECs, or any other node.

This prompt is the same for every domain after the tree is decided. Only the ASSIGNMENT changes.

---

You are researching **one roster row** — either one **schema** or one **template** — for a local-first file-organization agent.

Read `planning/prompts/ALIGNMENT.md`. You are not classifying files into a category. You are fact-checking **observations vs facts** for this row: real files, which 3–6 fields become legal, detection signals, recommended folder dimensions (not a path).

## ASSIGNMENT

Dispatcher replaces this object. If it is still the placeholder, **stop**.

```json
{
  "kind": "template",
  "domain_id": "creative.client-engagement",
  "schema_id": "creative",
  "parent_id": null,
  "name": "Client creative engagement (branch root)",
  "one_line_hint": "Creative work made for a paying client under a brief, where the client and the job — not the file format — are what the files have in common. PLACEHOLDER ROW (J-IND): gist/purpose-depth research only, and it writes NO field rows - the creative schema declares none (PR-6; D1's deferral stands).",
  "launch": "placeholder",
  "must_consider_neighbors": [
    "career",
    "code",
    "photos"
  ],
  "must_consider_residuals": [
    "Independent Records",
    "Review Later"
  ],
  "inherited_field_keys": [],
  "output_json": "planning/domains/nodes/creative.client-engagement.json",
  "output_research": "planning/domains/nodes/creative.client-engagement.research.md"
}
```

`kind: schema` — confirm/refine the 3–6 fields and the default template. Do not invent child schemas for work types.
`kind: template` — this organizational situation on `schema_id`. Reuse that schema's fields. Research detection signals, recommended `dimension_order`, file examples, collisions.

`parent_id` is browse-only. Ignore it for activation.

You may `refuse_node` if this id fails the node test.

## Why this exists

You were assigned **one** of `00`'s two definitions:

1. `kind: schema` — which fields are legal when this domain is plausible (usually three to six that may become folder levels)
2. `kind: template` — recommended dimension order + detection signals for one organizational situation, using `schema_id`

The LLM may only propose facts in the **active schema**. Facts are **not** a folder path (`00`: the user may later choose school-first or course-first; the facts have not changed). Residual templates are a **different** library.

Observation ≠ fact (`00`): filename `Syllabus BUSIB 4300 Spring 2026.pdf` is evidence; `course = BUSIB 4300` is a fact. EXIF `DateTimeOriginal` is evidence; `capture date` is a fact. Do not write paths as facts. Do not copy a course fact onto `HW 3.pdf` because a group exists.

## Read (quote only from `00`)

Required:

- `planning/00-database-agent-product-design.md` — authoritative. No tables. No section numbers.
- `planning/01-product-design-structured.md` — numbered rendering; `00` wins.
- `planning/domains/_CONTRACT.md` — entry shape.
- `planning/prompts/ALIGNMENT.md`
- `planning/domains/roster.json` — confirm your id, `kind`, `schema_id`, neighbours.
- `planning/domains/canonical_fields.json` — **reuse these keys**. Do not mint synonyms (`course_name` if `course` exists; spaced `work type` if `work_type` exists). D6 is unset; stay snake_case internally.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` is exactly:

```text
filesystem, text_document, spreadsheet, presentation, image, ocr,
email, calendar, contacts, code_structured, audio_video,
design_creative, archive, opaque_binary
```

If present:

- `planning/domains/CONNECTION.md` — `also_holds_with` vs `collides_with`, activation ≠ grouping, browse-only parent
- Neighbour files under `planning/domains/nodes/` if they already landed — align edges; do not rewrite them
- `planning/deferred-catalogues/` only if your recognition genuinely consumes an existing catalogue (citation ids, camera patterns). Do not invent gazetteer contents (R4) or detector regexes (R2).

Extractor reliability (`00` / P4): an extractor may write `direct` (labelled / structured slot) or `possible` (filename, free text, OCR). A field with `reliability_ceiling: validated` means a **rule** (gazetteer + context, term pattern, etc.) will confirm it later — say which rule family, do not write the regex or a score.

Sensitivity here is only `none` | `potentially_sensitive`. Handling classes are P7's. Do not assign `public_low`.

## Node test (refuse rather than pad)

Refuse (`refuse_node: true`) if:

- `kind: schema` and you cannot name a distinct 3–6 field set (you would only repeat another schema, or you would need a giant form)
- `kind: template` and detection signals, dimension order, and privacy rules are identical to the schema's default template
- the only “difference” is work types or file extensions — those are values and `SOURCE_TYPES`, not nodes

A refused node is a success. Inventing a schema to save the id is the 574 failure.

## Research procedure (do this before JSON)

### 1. Files — bottom-up, concrete

List **at least eight** (or all that exist, if fewer, and say so) **specific files** a person or small team actually keeps in this domain. Not “PDFs.” Filenames + what is inside:

```text
filename / typical name
source_type          one of SOURCE_TYPES
extensions           examples; never sufficient alone (00)
what is inside       one sentence
facts that should become legal if this domain is active
facts that must stay unknown / possible / not this domain
residual if this domain does not fire
```

Cover the ugly cases, not only the happy syllabus:

- labelled form vs unlabelled prose
- screenshot / OCR of the same thing
- archive packet (`submission.zip` with mixed members — `00`)
- calendar/contact/mail if this domain ever sees them
- a file that **looks** like yours but belongs to a neighbour (collision fixture)
- a file that is **also** another domain (`00`: academic abstract that is also an application document) — that is `also_holds_with`, not a collision

If you cannot name eight real files, you probably should refuse or shrink the schema.

### 2. Facets / facts — against canonical keys

For every field you put on the schema:

| Need | Rule |
|---|---|
| `field` | Must be a `canonical_fields.json` `key`, **or** listed in `proposed_fields` with why no existing key works |
| `type` | Match canonical |
| `example` | A value that would appear on one of your file examples |
| `reliability_ceiling` | One of: `direct`, `possible`, `validated`, `llm_supported`, `user_confirmed`, `rejected`. If `validated`, name the rule family (gazetteer schools, term pattern, course-code+context). |
| `destination_eligible` | Inherit canonical unless this domain forbids a folder level. Authorship is never a destination (`00`). |
| `why` | `00` cite if design; else no quote marks, `provenance` inference/proposal |

Start from `inherited_field_keys` (the **schema's** fields). Templates add fields only with `proposed_fields` and a reason no existing key works. Do not copy a parent schema via `parent_id`.

Purpose is a first-class facet when files are purpose-coherent but content-incoherent (`00`: application packet). Topic ≠ purpose.

### 3. Recognition — fact-check, not slogans

`deterministic` / `needs_llm` / `never_alone` must be **true of your file list**.

`00` forbids as sole proof (encode in `never_alone` when relevant): university name alone; bare 4-digit number; extension alone; download session as topic; missing EXIF as screenshot proof.

Course-shaped tokens need academic context (`syllabus`, `lecture`, `credits`, `instructor`, `semester` are the design floor — you may propose more in `proposed_context_terms`, you may not pretend `00` listed them).

Activation ≠ grouping: a file may join a P9 group (same course neighbourhood) without this schema activating from the filename (`HW 3.pdf` with no course code). Say so if it applies.

### 4. Work types are values

`work_types[]` is an enum of values for a `work_type` (or equivalent) field. Do not ask R1a for a child node per work type.

### 5. Template

`dimension_order` uses only destination-eligible fields. Parent **dimension** must make the child intelligible (`00`: Homework 3 is meaningless without the course). That is template order, not schema `parent_id`. `time_first` only when this situation is time-primary (photos), not as a default.

The user may reverse or flatten this order later. You are recommending, not freezing a filesystem.

Placeholder launch: still write detection signals + recommended dimensions, marked `launch: placeholder`.

Safety launch: small schema + protect; do not design a deep filing tree that would leak.

### 6. Edges (closed vocabulary)

You may use **only**:

| Edge | Write when |
|---|---|
| `collides_with` | Same evidence would confuse this node with a neighbour. Mutex. Reciprocal later (R1c). |
| `also_holds_with` | One file may legally carry **both** schemas (`00` abstract / application). Not a collision. |
| `file_kinds` | Plausible `SOURCE_TYPES` + extension examples. `never_alone: true` almost always. |
| `falls_through_to` | Residual template **name** from `00` §7.3 if this domain does not fire: Temporary Screenshots, One-Off Images, Reference Clips, Independent Records, Receipts and Confirmations, Reading Inbox, Review Later, Unsupported or Encrypted, Protected Records. |
| `role_split` | Same entity type, different field keys, pointing at the neighbour that holds the other role. |

Do **not** invent `related_to`. Neighbour ids must exist in the **roster** (not necessarily as finished node files). Prefer `must_consider_neighbors`; you may add other **roster** ids you looked up. Inventing an id is a fail.

### 7. Provenance

`design` only with a verbatim `00` span. `inference` if extending a named domain. `proposal` if new. No fabricated quotes — previous work invented clauses inside quote marks.

No numeric thresholds, no confidence scores, no handling classes.

## Output (only these two files)

### `output_json` — one node object (not wrapped in `entries`)

```json
{
  "id": "<domain_id>",
  "kind": "schema | template",
  "schema_id": "<schema this uses or is>",
  "parent_id": null,
  "name": "<researched name>",
  "one_line": "<researched>",
  "launch": "full | safety | placeholder",
  "provenance": "design | inference | proposal",
  "design_cite": null,
  "refuse_node": false,
  "refuse_reason": null,
  "fields": [],
  "proposed_fields": [],
  "recognition": {
    "deterministic": [],
    "needs_llm": [],
    "never_alone": []
  },
  "work_types": [],
  "grouping_reasons": [],
  "template": {
    "dimension_order": [],
    "why": "",
    "time_first": false
  },
  "file_kinds": {
    "source_types": [],
    "extensions": [],
    "never_alone": true
  },
  "file_examples": [],
  "collides_with": [],
  "also_holds_with": [],
  "falls_through_to": [],
  "role_split": [],
  "sensitivity": "none | potentially_sensitive",
  "sensitivity_why": "",
  "open_question": null
}
```

`kind: template` may leave `fields` empty and rely on `schema_id`. `kind: schema` fills `fields` (3–6 destination-eligible plus search/privacy extras).

`file_examples[]` items:

```json
{
  "filename": "Syllabus BUSIB 4300 Spring 2026.pdf",
  "source_type": "text_document",
  "observations": ["filename contains course-code-shaped token and 'Syllabus'", "page-one heading Spring 2026"],
  "facts_legal": ["school", "term", "course", "work_type"],
  "must_not_conclude": ["a folder path", "purpose = university application without packet evidence"],
  "also_schema": null,
  "group_without_copying_facts": false,
  "falls_through_if_inactive": "Independent Records"
}
```

If `refuse_node` is true, still write the file with reason, empty schema, and any file_examples that showed the id was a label.

### `output_research` — short lab notes

- sources you used (named)
- files you considered and rejected
- proposed_fields justification
- neighbours you considered that did **not** get an edge, and why
- `NEEDS-JOSEPH` for this node only

## Done when

- Output paths match ASSIGNMENT.
- You did not write any other file.
- Every `fields.field` is canonical or in `proposed_fields`.
- Templates do not invent a second copy of the schema's fields.
- File examples split **observations** from **facts**.
- No file example writes a folder path as a fact.
- `HW 3`-style sparse files, if relevant, mark `group_without_copying_facts` rather than inventing a course fact.
- Every `file_examples.source_type` is in `SOURCE_TYPES`.
- Every edge id is on the roster (or a §7.3 residual name in `falls_through_to`).
- At least one `never_alone` that is true of a tempting false file.
- No fabricated `00` quote.
- No threshold numbers.

If CONNECTION.md and this prompt disagree, CONNECTION wins; note it in research.md. ALIGNMENT.md wins over both if they reintroduce a schema tree `00` does not contain.

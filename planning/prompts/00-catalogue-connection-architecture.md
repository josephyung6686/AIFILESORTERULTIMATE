# Dispatch prompt — R0 · catalogue connection architecture

Copy everything below the line into a new agent. The agent should not need this chat.

Give it read access to the repo. It writes `planning/domains/CONNECTION.md` and extends `planning/domains/_CONTRACT.md` + `check.py` with the **edge types and invariants only**. It does **not** fill the template library (that is R1). It does **not** edit `src/` or SPECs.

This is the first research dispatch. R1–R6 consume it.

Read `planning/prompts/ALIGNMENT.md` first. `00` already specifies the join. You are writing it down so a hundred R1b agents cannot each invent a second one.

R1a publishes a **small schema list** plus a **template roster**. R1b is one agent per template (the hundred-fire) and per schema. R1c merges.

---

You are specifying **how `00`'s objects join**, for a local-first file-organization agent.

## Why you are here

Joseph asked for 500+ domains **and subdomains connected to each other**. An overnight pass produced 574 **flat schemas** joined only by `collides_with`. That is not a connection model, and it is also **not what `00` asked for**.

`00` already names the join. Nobody wrote it as a contract the swarm can obey. Your job is that contract — **not** an industry taxonomy.

Objects `00` requires to be true at once (quote only from `00`):

- A file is a record with **many facts**, not one category. Placement is later.
- **Universal fields** always: file type, creation date, language, duplicate family, version family, sensitivity status.
- Activate a **small domain schema** (usually three to six folder-proposal fields) only when evidence makes that domain plausible.
- **One file may hold facts from more than one domain** — worked example: academic abstract that is also a university-application document.
- Roles that share an entity type are **different fields** (`authored_by` vs `target_school`; `our_firm` vs `client`).
- The LLM may only propose facts in the **active domain schema**; it must not invent a new schema or unsupported field.
- Each domain is a **fact schema** plus a **folder template** (the subset of those facts that may become folder levels). The user can reorder/flatten the template; facts do not change.
- Library size: **roughly 200–300 templates** for organizational situations. Do **not** prematurely hand-author hundreds of specialized **schemas**. Launch: six full domains; finance/identity/medical/legal as **safety first**; others placeholders.
- **Grouping** is a file-neighborhood graph. `HW 3.pdf` does not receive a course fact by propagation. A file may belong to two groups. A university name alone must not create a group.
- **Residual** templates are a different library (nine named homes) for files with no reliable deeper association.
- P6 SPEC Deferred: which evidence makes a domain plausible is unauthored — you specify the **algorithm shape**, not every signal.

`planning/prompts/ALIGNMENT.md` is the reading of “500+ connected subdomains” that does not contradict the above. Obey it.

If R1 builds a parent/child **schema** tree and treats activation as walking that tree, P6/P8/P10/P11 will each invent a second reading of “parent.” The parent that `00` actually uses is a **folder dimension** (school before term before course), not a schema id.

## Read first (quote only from `00`)

- `planning/00-database-agent-product-design.md` — authoritative. No tables, no section numbers.
- `planning/01-product-design-structured.md` — numbered rendering; `00` wins on conflict.
- `planning/domains/_CONTRACT.md` — current entry shape.
- `planning/25-domains-verification.md` — audit of the 574.
- `planning/02-segmentation-map.md` — which part consumes what.
- `planning/parts/P6-facts-facets/SPEC.md` — `active_field_allowlist`, domain activation deferred.
- `planning/parts/P8-llm-harness-validator/SPEC.md` — validator "field in active schema".
- `planning/parts/P10-tree-design-freeze/SPEC.md` — domain templates vs residual templates (M10).
- `planning/parts/P7-privacy-consent-gate/SPEC.md` — classification is per file; detector unowned.
- `planning/parts/P9-grouping/SPEC.md` — grouping reasons, purpose-coherent packets.
- `src/evidence_shape/vocabulary.py` `SOURCE_TYPES` — 14 extraction families already shipped.
- `planning/overnight/council/DECISION-BRIEF.md` D1 / D2 — recommendations, not ratified. Do not close them.

## The questions you must answer

Write them as a contract, with **worked examples from `00`**, not as essays. If the design does not settle a question, mark `NEEDS-JOSEPH` and still pick a **provisional rule** so R1 can build, labelled `provisional`.

### 1. What is load-bearing vs browse-only?

`00` already uses **four** graphs. Pick how they relate; do **not** collapse them into one industry DAG.

| Graph | What the nodes are | Load-bearing? |
|---|---|---|
| **fields** | global field keys; schemas are subsets | yes — P6 `fields` table |
| **schema activation** | a **set** of plausible domains on a file | yes — allow-list for LLM/rules |
| **file neighborhood** | files, facts, versions, retrieval (P9) | yes — grouping; not domain ids |
| **folder dimensions** | values of destination-eligible fields, user-frozen | yes — after P10 freeze |
| **template library browse** | optional parent_id among templates | **no** — sugar so humans can find “travel” next to “receipts”. Must not drive activation |

`00` requires that a *file* can carry two schemas. It does **not** require that a schema have a parent schema. Academic is not a child of Education; Homework is not a child schema of Academic.

If you keep `parent_id` on templates, state: **activating a template does not activate a parent schema by walking the browse tree.** Plausible schemas are independently evidenced.

### 2. Schema vs template vs value vs group vs residual

Closed. R1a emits `kind: schema | template`. R1b refuses anything else.

- **Schema** — 3–6 folder-proposal fields + optional search/privacy fields. `00` names the launch set. A new schema exists only when those fields are genuinely different (`target university` is not `school`).
- **Template** — organizational situation: detection signals, recommended dimension **order**, optional branch patterns, privacy rules. Points at one schema. `00` sizes this library at ~200–300.
- **Value** — `syllabus`, `BUSIB 4300`, `Spring 2026`. Never a roster node.
- **Group** — files that belong together (one course-term, one application packet). P9. Overlap is allowed.
- **Residual** — nine `00` names. Not a domain.

**Subdomain** in Joseph’s request = template depth (school/term/course/work type) or an optional branch pattern (purpose-defined packet vs institution-first). **Not** a fourth schema.

Node test: a **schema** row exists only if it has a distinct field set. A **template** row exists only if its detection signals or recommended dimensions or privacy rules differ from the schema’s default template. Empty industry labels are forbidden.

### 3. Inheritance (do not invent schema-tree inheritance)

`00` does not define schema inheritance. Provisional unless Joseph says otherwise:

- Templates **reference** a schema; they do not copy-paste its fields.
- Folder “parent” is a **dimension**: work type is intelligible only after course (`00`). That is template order, not `parent_id`.
- Launch flags do not inherit down a browse tree. A placeholder template can sit next to a `full` schema.
- `active_field_allowlist(file)` = universal fields ∪ union of fields of **independently plausible schemas**. No walk.

If you believe `00` cannot work without schema inheritance, that is a `NEEDS-JOSEPH`, not a silent tree.

### 4. Activation (the missing algorithm)

P6 Deferred: which evidence makes a domain plausible is unauthored. You will not fill every signal (R1/R6 do). You **will** specify:

- Inputs: P4 observations, P5 `source_type` / extension, gazetteer hits, parent-folder context, P3 session clue (possible only).
- Output: a **set of schema ids** (not template ids, not folder paths), plus `unresolved` if none, plus residual-candidate if the set is empty or only safety-domain. Templates are chosen later by P10 from accepted groups + this schema set.
- Grouping must **not** be an input that writes facts. Session is `possible` only (`00`).
- **Never-alone:** extension, university name, bare 4-digit number — `00` already forbids these as sole proof. Encode that as a rule on edges, not a comment.
- **Safety domains** (finance, identity, medical, legal) may activate **without** unlocking a deep template — they unlock protection and a small schema. State that split.
- **Order:** deterministic signals first, LLM only for remaining ambiguity (`00`). Activation is not an LLM clustering job.
- **Cache / identity:** activation is per `(content_hash)`, same as facts. Two live copies share it.

Write the algorithm as numbered steps a later implementer can test. Use the `00` worked files: `Syllabus BUSIB 4300 Spring 2026.pdf`, `Wash U.docx`, `HW 3.pdf`, a passport scan, a `.ics`, a `.vcf`, a HEIC with EXIF.

### 5. Edge types — a closed vocabulary

Today there is one edge: `collides_with`. That is the wrong one to do all jobs. Publish a **closed list**. Suggested starting set; keep, drop, or split with reasons:

| Edge | Means | Consumer |
|---|---|---|
| `parent_of` / `child_of` | **browse-only** among templates, if kept. Never schema inheritance, never activation | UI, optional |
| `collides_with` | mutex given the same evidence — do not treat as the other | P6 activation, P8 validator |
| `also_holds_with` | both **schemas** may be active on one file (`00` abstract + application) | P6, P8, P9 |
| `file_kind_plausible` | this `SOURCE_TYPE` / extension *may* make a schema plausible, never proves | P5→P6 |
| `falls_through_to` | if no schema is reliable, consider this residual template | P10/P11 |
| `safety_for` | this schema, when plausible, is a safety domain (protect before place) | P7, P11 |
| `uses_schema` | this template points at this schema | R1, P10 |
| `shares_field` | same `field_key` | P6 field catalogue |
| `role_split` | same entity type, different fields (`school` vs `target_school`) | P6, P8 |

**Closed** means R1 cannot invent `related_to`. If a new edge is needed, it is a revision of `CONNECTION.md`.

For each edge: directed or not, required reciprocal or not, whether it may cross launch flags, whether it may cross safety/non-safety, cycle rule.

### 6. Field identity

A field is a global token. `school` on coursework is `school` on teaching. `target_school` is a different field (`00` §3.8).

Specify:

- Where the **canonical field list** lives (one table, domains *reference* it — not 574 private schemas that happen to share strings).
- How aliases work (`U Chicago` is a value alias, not a field alias).
- Spaced vs snake_case: **internally consistent** even if D6 is unset; record `UNSETTLED-D6`.
- `destination_eligible` is per field, not per domain, except where a domain forbids a field as a folder level. Authorship fields are never destination-eligible (`00`).

### 7. Templates vs schemas vs residuals vs groups

Four objects people keep collapsing:

| Object | Owner | Job |
|---|---|---|
| Domain **schema** | P6 | legal fact fields when active |
| Domain **template** | P10 | which of those fields may become folder levels, and in what order. `00` §5.7: ~200–300, each with detection signals, privacy rules, validation constraints |
| **Residual** template | P10 | broad destination when **no** domain association is reliable. Nine named in `00`. Not a domain. |
| **Group** | P9 | files that belong together (one course-term, one application packet). Purpose-coherent, not always content-coherent |

State:

- A template **points at** one schema (`uses_schema`). It does not duplicate the field list.
- A group does **not** create a schema. Accepted groups are what P10 fits templates to.
- Residual is the complement of "reliable domain association", not a 575th schema.
- Custom LLM templates (`00`) must use **existing field types** and cannot silently create a new high-level domain.
- Facts remain separate from the destination tree (`00`). `dimension_order` is a recommendation the user may reverse.

### 8. What P6/P8/P9/P10/P11 each read

A table: function name (even if unbuilt), which graph, what it returns, what it must not re-derive. This is how we stop a second vocabulary.

Include: `active_domains(content_hash) -> frozenset[id]`, `active_field_allowlist(...)`, `destination_dimensions(domain_id)`, `residual_candidates(content_hash)`, `collides(a,b) -> bool`.

### 9. Worked joins the 574 never encoded

Write each as a graph snippet + activation set:

1. Syllabus PDF → Academic schema plausible; facts `school`, `term`, `course`/`subject`, `work type`. Recommended template school→term→course→work type. **Not** a path yet.
2. Academic abstract in an application packet → **Research + Applications** schemas both plausible (`also_holds_with`). Placement later; both fact sets kept.
3. University name alone → **no** schema (`00`: Columbia can be school, target, employer, venue, citation). **No** group.
4. Passport scan → safety/identity schema + residual Protected Records if no deeper group; never a cloud prompt.
5. `.ics` → calendar is a `SOURCE_TYPE`. It makes some schema *plausible* only with content; it is not itself a domain. Slice 14's calendar-as-domain was the format-as-schema bug — reject unless `00` names a calendar schema (it does not).
6. `HW 3.pdf` with no course code → **does not** write `course` from filename; grouping (P9) may still attach it to a course neighbourhood **without copying the course fact onto the file**. Activation ≠ grouping. **State that split.**
7. Teaching a course vs taking a course — if they need different fields, that is `role_split` or a second template on the **same Academic schema**, not two schemas that each reinvent `school`.
8. Insurance: personal vs corporate vs healthcare — same field vocabulary (`institution`, `record type`, …) on Finance or a safety schema; different **templates**, not three unrelated schema slugs.

### 10. Failure modes to forbid by construction

- Schema-tree inheritance used to make `school` legal on a syllabus (the field is on the Academic schema; no child required).
- Treating work types or extensions as schemas.
- `collides_with` used to mean `also_holds_with`.
- Format-only activation (`.pdf` → Independent Records; `.ics` → a Calendar schema).
- A second field named `course_name` beside `course`/`subject`.
- Residual `Travel` duplicating a travel **template** without `falls_through_to`.
- 500+ **schemas**. `00` forbids prematurely hand-authoring hundreds of specialized schemas.
- Copying a course fact onto `HW 3.pdf` because a group exists.
- Writing a folder path as a fact.

## What you must not do

- Do not rebuild the 574. Do not invent gazetteer contents, detector regexes, or residual slot values. Those are R1–R6.
- Do not close D1 (how far the launch catalogue opens), D2 (authoritative sensitivity record), D6 (spelling).
- Do not invent numeric score/margin thresholds (`00` requires them, states no numbers). Name the **slot** (`min_score`, `min_margin`) as injected.
- Do not put this graph in SQLite yet. This is a catalogue contract. P1/P6 will store **activation facts** later; the library is data.

## Output

### 1. `planning/domains/CONNECTION.md`

Sections, in this order:

1. The four `00` graphs (fields, schema-activation set, file neighborhood, folder dimensions) and that browse `parent_id` is not load-bearing
2. Schema vs template vs value vs group vs residual (node test)
3. No schema-tree inheritance (`active_field_allowlist` = universals ∪ plausible schemas)
4. Activation algorithm (numbered, with the eight worked files)
5. Closed edge vocabulary (table + invariants)
6. Canonical field list (where it lives; schemas reference it)
7. How P10 uses templates without treating them as categories
8. Consumer table (P6/P8/P9/P10/P11)
9. Failure modes forbidden
10. `NEEDS-JOSEPH` (only real forks)
11. `provisional` list R1 may use until Joseph answers

Every `00` quotation matched verbatim. No fabricated quotes.

### 2. Contract delta

Patch `planning/domains/_CONTRACT.md` with `kind: schema | template` and `uses_schema` on templates. `parent_id` is optional browse-only. Do not require a forest.

### 3. Gate delta

`planning/domains/check.py` grows checks for: unknown edge names, missing inverse on reciprocal edges, cycles in `parent_of`, `also_holds_with` and `collides_with` on the same pair (illegal unless you explicitly allow), `shares_field` pointing at unknown field keys **once the canonical list exists** (skip until R1 lands the list).

### 4. `planning/domains/CONNECTION-EXAMPLES.md`

The eight worked joins as tiny JSON graphs. These are fixtures R1 must remain compatible with.

## Done when

- `CONNECTION.md` answers all ten questions with a pick, not a menu, **and does not introduce an industry schema-tree `00` does not contain**.
- Activation is an algorithm over **plausible schemas**, not a walk of `parent_id`.
- Edge vocabulary is closed; `parent_of` if present is marked browse-only.
- Activation ≠ grouping is explicit (`HW 3.pdf`).
- Schema ≠ template ≠ residual ≠ group is explicit.
- Facts ≠ path is explicit.
- The eight `00` files have a snippet.
- `check.py` still passes on the current 574 **or** you document which current fields would fail once R1 migrates.

If you find that Joseph's "500+ connected subdomains" cannot land without hundreds of schemas, **that is the headline**: the landing is 200–300 **templates** on a small schema list (`ALIGNMENT.md`). Put any remaining fork in `NEEDS-JOSEPH` and still ship a provisional so R1 is not blocked.

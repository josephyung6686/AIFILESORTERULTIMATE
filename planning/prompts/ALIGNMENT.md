# Does the research pack land on the original design?

Date: 2026-08-21
Status: **alignment contract.** If a prompt and this file disagree, `00` wins, then this file, then the prompt.
Source of truth: [`00-database-agent-product-design.md`](../00-database-agent-product-design.md)

The overnight 574, the “500+ domains and subdomains” request, and `00` were three different objects. This file says which object the swarm is allowed to build.

---

## What `00` actually specifies

A file is **a record with many facts**, not one permanent category. A syllabus can also be a course member, a term member, a university-related file, an application supporting document, a version-family member, and potentially sensitive — **separate facts**. Placement is later. Extraction does not decide the domain or the path.

**Universal fields** (always available): file type, creation date, language, duplicate family, version family, sensitivity status.

**Domain schemas** activate only when evidence makes that domain plausible. Each schema is **small**: usually three to six fields that may become folder levels, plus some search/privacy/review fields. Named in `00`:

| Schema | Fields (`00`) |
|---|---|
| Academic | school, term, course, instructor, work type |
| College applications | target university, application cycle, application document type, purpose |
| Research | project, stage, artifact type, lab, venue |
| Finance | institution, account type, tax year, record type |
| Photos | capture year, event, location, people, camera information, media type |
| Code | project, repository, programming language, artifact type |

Career has a **template** (company → role or recruiting cycle → document type) and is a launch domain, but those fields are **not** in the Academic-style field list. Identity / medical / legal are **safety domains first**. `00`: do **not** prematurely hand-author hundreds of specialized **schemas**.

**Folder templates** are a different object. A template is not a list of folder names. It is recommended **dimensions** and their order, populated from **validated facts and accepted groups**. Academic: school → term → course → work type. The user can reverse, remove, flatten. Syllabus / Homework / Lectures are **values of work type**, not extra schemas.

The library `00` actually sizes: **roughly 200–300 domain-specific templates**, covering organizational situations (academic programs, applications, recruiting, client engagements, research, financial records, travel, legal, creative, software, personal administration, photos). Each template defines: allowed fact fields, **detection signals**, recommended dimensions, preferred order, optional branch patterns, privacy rules, validation constraints. Launch implements the core; the rest stay placeholders.

**Grouping** is a third object. `HW 3.pdf` does not get `course = PHYS1401` written onto it because the neighborhood contains a syllabus. The graph assembles context; membership is reviewable; a file may belong to **more than one group** (PVA/RDP abstract = research artifact **and** application supporting document). A university name alone must not create a group.

**Residual** is a fourth object: nine named broad destinations when there is **no reliable deeper association**. Not the 200–300.

**The graph in `00` is a file-neighborhood graph** (facts, versions, retrieval) for grouping and later placement. It is **not** a parent/child taxonomy of industry domains.

---

## What Joseph asked for later

500+ **domains and subdomains connected to each other**, then one research agent per node, fact-checking files and facets.

That request is real. It does **not** override `00`. The reading that satisfies both:

| Phrase | Lands on |
|---|---|
| “domain” | a **schema** (small field set) **or** a **template** (organizational situation using that schema) |
| “subdomain” | **folder depth inside a template** (school / term / course / work type) **or** an optional branch pattern (purpose-defined packet vs institution-first). **Not** a new schema per work type or per industry code |
| “connected” | shared **fields** table; one file **many facts / two schemas**; groups that overlap; detection signals; residual fallthrough; role-split fields (`school` vs `target_school`). **Not** `parent_id` as the activation engine |
| “500+” | the **template library** (`00` says 200–300). Stop under that if honest. **Do not** mint 500 schemas |
| “one agent per node” | one agent per **template** (the hundred-fire), plus one agent per **schema** (a handful) |

The 574 failed because it built 574 **schemas** with private field names. Doing that again in parallel is the same bug.

---

## What the swarm must not rebuild

- An industry taxonomy (NAICS, 14 supercategories of 40 siblings).
- A schema per work type (`acad.syllabus` vs `acad.homework`).
- A schema per file format (`.ics` is a `SOURCE_TYPE`, not a domain).
- `parent_id` as “activating the child activates the parent schema.” Activation is **which schemas are plausible**, independently, as a set. Browse-tree parent is optional sugar for the template library.
- Domain membership as the file’s category. Facts stay; the user later picks a path; one physical path vs many facts is already in `00` (shared material policy).
- Residual templates as extra domains.
- Handling classes (`public_low`, …) on catalogue rows.

---

## Two roster kinds (R1a must emit both)

```text
kind: schema     small; 00's named set + safety + a placeholder only when it needs
                 a distinct 3–6 field set. Career schema fields remain deferred (S3)
                 but the Career template still gets a roster row of kind: template.

kind: template   the 200–300 organizational situations. Each points at one schema_id.
                 Detection signals, recommended dimension_order, file examples live here.
                 This is what you stamp R1b onto hundreds of times.
```

A template that would only repeat its schema’s fields and dimension_order **is not a node** — it is the schema’s default template. Extra templates exist when the **organizational situation** differs: purpose-defined application packet vs institution→cycle→document type (`00`); client engagement vs recruiting; photo-event vs screenshot-capture.

---

## Pipeline, restated so it lands

```text
R0   how 00's objects join (schema, template, group, residual, fields, facts)
     — not “what kind of industry DAG”
R1a  small schema list + template roster + canonical fields (universals + named domain fields)
R1b  one agent per template (and per schema): real files → observations vs facts,
     3–6 fields, detection signals, recommended dimensions, collisions / also-holds
R1c  merge: templates reuse fields; schemas stay few; reciprocity; SOURCE_TYPES coverage
R2–R6 as before (detector, residual nine, gazetteers, one jurisdiction's values, patterns)
```

R1b fact-check means: this filename, this `SOURCE_TYPE`, these **observations** (raw), these **facts** (conclusions, with reliability), these facts that must **not** be written (university name alone, session as topic, `HW 3` as a course code, missing EXIF as screenshot). That is `00`’s observation/fact split, not a new questionnaire.

---

## Scorecard (prompt pack vs `00`)

| Mechanism | Lands? | Note |
|---|---|---|
| File = many facts | after this refine | R1b must not treat domain as a category |
| Universal vs domain fields | after this refine | R1a starts from `00`’s lists, not 2,000 keys |
| Schema small (3–6) | after this refine | refuse a node that needs a giant form |
| One file, two schemas | yes | `also_holds_with` = abstract + application |
| Template ≠ schema | after this refine | two roster kinds |
| 200–300 templates | after this refine | not 500 schemas |
| Work types are values | yes | already in R1b |
| Grouping ≠ label copy | yes | keep; R0 must not replace P9 with domain fire |
| Residual nine | yes | R3 |
| Safety before cloud/place | yes | R2; not a folder tree |
| Gazetteer + word-boundary | yes | R4 |
| Narrow dates / term patterns | yes | R6 |
| Fields global, values new | yes | canonical_fields |
| Facts ≠ path | after this refine | template order is a recommendation |
| Industry forest as activation | **no — removed** | was the miss |

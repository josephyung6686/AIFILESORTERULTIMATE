# Connection architecture — how `00`'s objects join

Date: 2026-08-21
Status: **connection contract (R0).** R1a/R1b/R1c build against this; P6/P8/P9/P10/P11 read it.
Source of truth: [`00-database-agent-product-design.md`](../00-database-agent-product-design.md) —
every quotation below appears verbatim in that file and was matched mechanically before this
document was written. § numbers are locators into
[`01-product-design-structured.md`](../01-product-design-structured.md)'s rendering, never a claim
that `00` contains numbered sections.
Alignment: [`prompts/ALIGNMENT.md`](../prompts/ALIGNMENT.md). On conflict: `00` wins, then
ALIGNMENT, then this document, then any dispatch prompt.
Fixtures: [`CONNECTION-EXAMPLES.md`](CONNECTION-EXAMPLES.md) — the eight worked joins, binding on
R1.

Why this exists: Joseph asked for 500+ domains and subdomains connected to each other. The
overnight pass produced 574 flat schemas joined only by `collides_with` — neither what was asked
for nor what `00` specifies. `00` already names the join; nobody had written it down as a contract,
so fourteen authors invented fourteen private vocabularies. This document writes the join down.
**It is not an industry taxonomy and must never become one.**

The headline, stated once and early: **Joseph's request — 500+ domains and subdomains connected
to each other — lands as roughly 200–300 templates over a small schema list, not as 500
schemas.** `00`: "The product should eventually
maintain a library of roughly 200–300 domain-specific templates", and the same design forbids the
alternative — the placeholder approach exists precisely so the product gets "broad long-term
coverage without prematurely hand-authoring hundreds of specialized schemas". The count Joseph
asked for is reached by the *connected whole* — schemas, templates, residual homes, and the folder
depth inside templates — not by minting schema rows. The remaining counting fork is NEEDS-JOSEPH
(NJ-1); the provisional rule (PR-3) lets R1 build now.

---

## 1. The four load-bearing graphs — and the one that is not

`00` uses four different graphs. They stay four. Collapsing them into one industry DAG is the
failure this contract exists to prevent.

| Graph | Nodes | Edges / structure | Load-bearing consumer |
|---|---|---|---|
| **fields** | global field keys (one canonical table, section 6) | `role_split` between field keys; schemas *reference* keys; `shares_field` between schemas is derived from these references | P6 `fields` table; P8 `FIELD_NOT_IN_ACTIVE_SCHEMA` |
| **schema activation** | schema ids | a **set-valued function per file version**: `active_domains(content_hash) -> frozenset[schema_id]`. Not a walk of anything; each member is independently evidenced (section 4) | P6 (which fields are legal), P8 (validator allow-list) |
| **file neighborhood** | files, facts, versions, retrieval links | P9's typed edges (`shared-validated-fact`, `duplicate`, `version-family`, `compatible-document-type`, `existing-related-folder`, `bounded-session`, `mutual-semantic-retrieval`) | P9 grouping; P11 node-local graphs. Carries **file ids, never schema or template ids** |
| **folder dimensions** | values of destination-eligible fields, arranged by a template's `dimension_order`, then user-edited and frozen | parent/child *within one branch of the tree* — `Columbia` before `2026-Spring` before `BUSIB 4300` before `Syllabus` | P10 freeze; P11 placement against frozen nodes |
| template library **browse** | template rows | optional `parent_id` among templates | **none.** UI sugar so a human can find "travel" next to "receipts". Not load-bearing |

The relations between the four are exactly these, and no others:

- Schemas are **subsets of the fields table** — a schema row lists field keys it legitimises; it
  defines no key of its own (section 6).
- The activation set is computed **per file version from that file's own evidence** and outputs
  schema ids. It never outputs template ids, folder paths, or group ids.
- The file neighborhood is **P9's and only P9's**. It assembles context; it does not write facts
  and it does not activate schemas. `00`: "The graph is used as a context-assembly mechanism
  rather than an automatic label-propagation system."
- Folder dimensions exist only after P10: "Templates use validated facts to create folder
  proposals, and the user edits and freezes those proposals into an approved destination tree."
  The parent that `00` actually uses — school before term before course — is a **dimension order
  inside a template**, not a `parent_id` between roster rows.

**The browse tree is not load-bearing — the binding statement.** A template row may carry
`parent_id` (another template) so the library is browsable. Nothing else may read it:

- Activating a template does **not** activate a parent schema, a parent template, or anything
  else by walking the browse tree. Plausible schemas are independently evidenced.
- `00` requires that a *file* can carry two schemas ("One file may hold facts from more than one
  domain without losing information"). It nowhere requires that a *schema* have a parent schema.
  Academic is not a child of Education; Homework is not a child schema of Academic — Homework is a
  **value of `work_type`**.
- P6, P8, P9, P10 and P11 are forbidden from importing, traversing, or conditioning on
  `parent_id`. A build in which any of them reads it fails this contract.

## 2. Schema vs template vs value vs group vs residual — the node test

Closed. R1a emits exactly two roster kinds — `kind: "schema" | "template"` — and R1b refuses
anything else. The other three objects are **not roster nodes**.

| Object | Roster node? | What it is | Owner |
|---|---|---|---|
| **Schema** | yes, `kind: schema` | a small fact schema: the fields legal when the domain is plausible. `00`: "Each domain activates only a small set of relevant fields, usually three to six that may help build a future folder proposal and several additional fields used only for search, privacy protection, explanation, or later review" | P6 (fact half of §3.15's pair) |
| **Template** | yes, `kind: template` | an organizational situation: detection signals, recommended `dimension_order`, optional branch patterns, privacy rules, validation constraints. Points at exactly one schema via `uses_schema`. `00` sizes this library: "roughly 200–300 domain-specific templates" | P10 (folder half of §3.15's pair) |
| **Value** | **no** | `syllabus`, `BUSIB 4300`, `Spring 2026`, `UChicago`. Values auto-create at runtime (`00`: "The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically") — a runtime-created thing cannot be a hand-authored roster row | P6 `values` table |
| **Group** | **no** | files that belong together — one course-term, one application packet. Overlap allowed: "A file may validly belong to more than one accepted group, such as a PVA/RDP abstract that is both a Research artifact and a supporting document in a UChicago application packet" | P9 |
| **Residual** | **no** (a separate nine-name library) | broad destination when there is no reliable deeper association: "Residual templates provide safe, intentionally broad destinations for files that have no reliable deeper association." The nine `00` names: Temporary Screenshots, One-Off Images, Reference Clips, Independent Records, Receipts and Confirmations, Reading Inbox, Review Later, Unsupported or Encrypted, Protected Records | P10 definitions (M10), P11 workflow, R3 slot values |

**The node test** — R1b applies it to every proposed row and refuses rows that fail:

- A **schema** row exists only if its field set is genuinely distinct. `target_university` is not
  `school` — that is §3.8's role split, and it is the *only* licence for a near-duplicate field.
  A schema whose fields are a subset or respelling of an existing schema's is not a schema; it is
  a template on the existing schema, or nothing.
- A **template** row exists only if its detection signals, recommended dimensions, or privacy
  rules differ from its schema's default template. ALIGNMENT: a template that would only repeat
  its schema's fields and dimension order **is not a node** — it is the schema's default template.
- An **empty industry label** — a row whose only content is a name and a one-liner — is forbidden
  in both kinds.

**"Subdomain", resolved.** In Joseph's request, a subdomain is (a) folder depth inside a template
— school / term / course / work type — or (b) an optional branch pattern on a template — the
purpose-defined packet ("a purpose-defined packet, such as Chinese University Application
Materials") versus institution-first. It is **never** a third roster kind, never a schema per work
type, never a schema per file format.

## 3. No schema-tree inheritance

`00` defines no schema inheritance, so none exists. Binding rules (provisional only in the sense
that Joseph could overrule; R1 builds on them as stated):

1. **Templates reference a schema; they never copy its fields.** `uses_schema` is a pointer. A
   template's `dimension_order` may only name fields its schema declares (already enforced by the
   gate for the same reason: a dimension on an undeclared field opens a tree level no fact can
   fill).
2. **The folder "parent" is a dimension, not a schema id.** `00`: "A work type such as Homework 3
   is meaningful only after the course is known, and a course code may require the school or term
   to disambiguate it." That sentence is about template order. It licenses no `parent_id`
   semantics.
3. **Launch flags do not inherit down the browse tree.** A placeholder template can sit next to a
   `full` schema; a `full` template can point at a schema whose deeper cousins are placeholders.
   (What the launch flag vocabulary is remains R1a's to emit under the narrowed D1 — see PR-6.)
4. **The allow-list is a union, not a walk:**

   ```text
   active_field_allowlist(content_hash) =
       universal_fields
       ∪ ⋃ { schema.fields : schema_id ∈ active_domains(content_hash) }
   ```

   Universal fields are `00`'s: "a small shared set of universal file facts, such as file type,
   creation date, language, duplicate family, version family, and sensitivity status" (plus P6's
   one recorded addition, `download_session`). Nothing else reaches the allow-list. No parent is
   consulted because there is no parent.

If a later part believes `00` cannot work without schema inheritance, that belief is a
NEEDS-JOSEPH entry filed against this document — never a silently built tree.

## 4. Activation — the algorithm shape

P6's SPEC defers "Domain activation signals"; this section specifies the **algorithm shape** the
signals plug into. R1b authors per-schema signals; R6 authors pattern catalogues; the numbered
steps below are what a later implementer builds and tests. All thresholds are **injected slots**
(`min_activation_score`, `min_margin`, …) — this product writes no numbers into catalogues.

**Inputs** (all per file version): P4-shaped observations for that `content_hash`; P5's
`source_type` and the extension (routing signals only — `00`: the engine should "treat the file
extension as a routing signal rather than an assumption about meaning"); gazetteer hits
(word-boundary matched, R4's content); P3 parent-folder context; P6's `download_session` fact
(`possible` only). **Not an input:** P9 group membership, embeddings, any folder path, any other
file's facts.

**Output:** a set of **schema ids** — never template ids, never folder paths — plus two flags:

```text
activate(content_hash) ->
    schemas            frozenset[schema_id]     may be empty; members independently evidenced
    unresolved         true when the set is empty
    residual_candidate true when the set is empty, or contains only safety-domain schemas
```

Templates are chosen later, by P10, from accepted groups plus this schema set. Activation never
picks a template.

**The steps:**

1. **Collect deterministic signals.** For each roster schema, evaluate its authored detection
   signals against the file's own observations: pattern-plus-context rules (the §3.5 shape — "a
   course-code pattern together with academic context such as" the five literal terms), gazetteer
   hits at word boundaries with positional weighting, `file_kind_plausible` membership for the
   file's `source_type`/extension, parent-folder context, labeled metadata slots. This is `00`'s
   second stage: "rules and structural extractors create the reusable evidence database and
   identify obvious candidate domains."
2. **Apply the never-alone rule** (an edge invariant, not a comment — see section 5). Strike any
   schema whose entire support is never-alone evidence: a `file_kind_plausible` hit alone, a
   university-gazetteer hit alone ("A university name alone should not create a group because
   Columbia can appear as an authoring school, course provider, target institution, employer,
   research venue, or merely a cited organization" — the same ambiguity forbids it as sole schema
   proof), a bare 4-digit number alone ("numbers that look like years but are course identifiers,
   version numbers, build numbers, ZIP codes, or other unrelated values").
3. **Resolve collisions per evidence item.** Where one evidence item supports two schemas joined
   by `collides_with`, the item counts toward the better-supported side only if that side beats
   the other by injected `min_margin` for that item; otherwise the item counts toward neither.
   This is §3.7's margin discipline applied at the evidence-item level. It disambiguates *items*;
   it never caps the *set* — two schemas may both clear activation on disjoint evidence (that is
   `also_holds_with`).
4. **Admit every schema that clears its injected `min_activation_score`.** Activation is a set:
   there is no margin requirement *between* admitted schemas, because `00` requires co-activation
   ("One file may hold facts from more than one domain without losing information").
5. **Safety split.** A schema marked `is_safety_domain` (finance, identity, medical, legal —
   "Finance, identity, medical, and legal material should be implemented first as safety domains,
   meaning the system detects and protects them before any cloud or automated placement decision
   is allowed") activates like any other, but its activation unlocks **protection plus its small
   schema only**: P7 classification runs before any model or placement path, and no deep template
   is unlocked by safety activation. Protection-versus-extraction ordering inside the safety
   domains is NJ-2; the provisional split above (PR-2) is what R1 builds.
6. **LLM step, last and bounded.** Only for files still unresolved or multi-plausible after steps
   1–5 — `00`'s own eligibility: "an LLM receives only compact evidence packets for files or
   groups that remain ambiguous, have multiple plausible domains, or contain language that
   requires interpretation." The call goes through P8 site A; the model may propose plausibility
   only for roster schemas, must cite evidence, and its proposal passes P8's validator. Activation
   is not an LLM clustering job: deterministic signals always run first, and a model may never
   *remove* a deterministically activated schema.
7. **Emit.** `schemas` = the admitted set; `unresolved` when empty; `residual_candidate` when
   empty or safety-only. An empty set is a correct outcome, not a failure — the file routes to
   residual review (section 7), and its universal facts stand.
8. **Cache and identity.** Activation is per `content_hash`, cached under §3.4's composition
   (content hash + detector/roster version + analysis tier + model identifier + prompt
   fingerprint where the LLM step ran). Two live copies of the same bytes share one activation. A
   rename recomputes nothing; new bytes recompute everything.
9. **The grouping firewall.** Grouping is never an activation input and activation is never a fact
   writer by proxy: "The graph does not automatically copy those missing facts onto sparse
   files." A group conclusion can reach a file's facts only through P8's validated site-A path
   under P6's rules. Session membership enters only as the `possible`-grade clue `00` allows ("It
   may be supported more weakly by a tightly bounded download session" … "A session should never
   be treated as proof of topic").

**The eight worked files** (fixture-form in [`CONNECTION-EXAMPLES.md`](CONNECTION-EXAMPLES.md)):

| File | Steps that fire | Result |
|---|---|---|
| `Syllabus BUSIB 4300 Spring 2026.pdf` | 1 (course-code + "Syllabus" context; term pattern) | `{academic}`; facts `subject`, `term`, `work_type` become extractable |
| `Wash U.docx` | 1 finds nothing decisive in the filename; 6 fires on the heading ("A file called Wash U.docx may contain an unmistakable university application prompt"; "That heading is strong evidence for the College Applications domain") | `{college_applications}` via P8-validated LLM proposal |
| `HW 3.pdf` | 1 finds a homework-shaped name, no course code, no context terms; 2 strikes nothing because nothing was admitted | `{}` or `{academic}` only if its own evidence clears the bar; **no course fact from the filename**; P9 may still attach it to a course neighborhood without copying the course fact |
| passport scan | 1 (identity-document detector, R2's content); 5 | `{identity}` — protection + small schema; `residual_candidate = true` (safety-only); falls through to Protected Records if no deeper accepted group; never a cloud prompt ("A scanned passport, tax statement, medical document, authentication key, or account record should enter a protected state immediately") |
| a `.ics` | 1: `source_type = calendar` is a `file_kind_plausible` signal only; 2 strikes any schema supported by nothing else | `{}` unless *content* evidences a roster schema. Calendar is a `SOURCE_TYPE`, not a domain — slice 14's calendar-as-domain was the format-as-schema bug |
| a `.vcf` | 1; 2; plus `00`'s own rule: VCF data "should normally be privacy-protected rather than used to create folder proposals" | `{}` for placement purposes; contact facts stay search/privacy-side |
| HEIC with EXIF | 1 (camera EXIF is tier-1 photo evidence; "HEIC support must be included explicitly") | `{photos}`; `capture_year`, `event`, `camera_information` extractable; media-type conflicts abstain ("conflicting signals should lead to abstention rather than an invented classification") |
| `IMG_4821.png`, no EXIF, OCR pending | 1 finds only a format and a name; 2 strikes everything ("the system must not mistake the absence of EXIF for proof that an image is a screenshot"); OCR text, when it exists, re-runs the algorithm under a new cache key | `{}` → `unresolved`, `residual_candidate` — `00`: it "may be a screenshot of a receipt, application portal, conversation, code error, or research figure", and only evidence decides which |

## 5. The closed edge vocabulary

Today there is one edge, `collides_with`, doing every job badly. The closed list is below.
**Closed means closed:** R1 cannot invent `related_to`, `broader`, `narrower`, `similar_to`, or
any other edge. A new edge is a revision of this document, reviewed as such.

| Edge | Between | Means | Directed | Reciprocal required | Crosses launch flags | Crosses safety / non-safety | Cycle rule | Consumer |
|---|---|---|---|---|---|---|---|---|
| `uses_schema` | template → schema | this template's facts are this schema's fields; exactly one per template | yes | no (a schema does not list its templates; derived) | yes | yes (a safety schema may have templates) | impossible (bipartite, single hop) | R1, P10 |
| `parent_id` | template → template | **browse-only** shelving. Never schema inheritance, never activation, never a folder dimension | yes | no (child list derived) | yes — a placeholder may sit under anything | yes | **cycles forbidden**; forest not required (roots may be many, parent optional) | UI only |
| `collides_with` | schema ↔ schema, or template ↔ template (same kind only) | mutex **given the same evidence item** — do not treat one as the other. Must carry `signal`: the discriminating evidence | symmetric | **yes** (post-migration; see Gate status) | yes | yes (finance-safety vs a business template is a real confusion) | n/a (not hierarchical) | P6 activation step 3, P8 validator |
| `also_holds_with` | schema ↔ schema only | both schemas may be active on one file, on disjoint evidence — `00`'s abstract that is Research *and* Applications | symmetric | **yes** | yes | yes (an application packet legitimately contains an identity document) | n/a | P6, P8, P9 |
| `file_kind_plausible` | source_type or extension → schema (serialized as a list on the schema row) | this `SOURCE_TYPE` (P5's closed fourteen) or extension *may* make the schema plausible; **never proves** — the never-alone invariant is part of the edge | yes | no | yes | yes | n/a | P5 → P6 (activation step 1–2) |
| `falls_through_to` | schema or template → residual template **name** (one of `00`'s nine; residuals are not roster nodes) | when no reliable association lands, this is the broad home to consider | yes | no | yes | yes (identity → Protected Records) | terminal by construction (residual names are not sources) | P10, P11 |
| `role_split` | field ↔ field (lives in the canonical field list, section 6) | same entity type, different fields — "distinct facets, such as authored_by and target_school, or our_firm and client" | symmetric | **yes**, once the canonical list exists | n/a | n/a | n/a | P6, P8 |
| `shares_field` | schema ↔ schema | both schemas reference the same canonical `field_key` | symmetric | n/a — **derived, never authored** | n/a | n/a | n/a | P6 field catalogue, R1c merge checks |

**Kept, dropped, split — the reasons:**

- **Kept:** `collides_with` (narrowed to its real meaning: evidence-item mutex, not *these are
  different topics*), `uses_schema`, `falls_through_to`, `also_holds_with`, `file_kind_plausible`,
  `role_split`, `parent_id`.
- **Split:** the suggested `parent_of`/`child_of` pair collapses to a single serialized
  `parent_id` field; "parent_of"/"child_of" are the two derived readings of it. One stored form
  means no missing-inverse class of bug for the browse tree.
- **Dropped:** `safety_for` as an edge. An edge needs a second node; the target of
  *protect before place* is P7's gate, which has no node in this namespace, and giving it one
  would put P7's vocabulary into the catalogue (the same violation as handling classes on rows).
  It becomes the row attribute `is_safety_domain: true` on schema rows — provenance `design`,
  because `00` names the four safety domains outright.
- **Derived, never authored:** `shares_field`. It is computable from canonical field references;
  an authored copy would drift from the truth it duplicates. The gate rejects a serialized one.

**Invariants that ride on the vocabulary:**

1. `collides_with` and `also_holds_with` **may coexist on one schema pair** — explicitly allowed,
   because they answer different questions. Academic and College-applications collide on a bare
   university name (one evidence item must not activate both) *and* also-hold on the abstract in
   an application packet (disjoint evidence activates both: "An academic abstract submitted as
   part of a university application can retain project = PVA/RDP and document type = abstract
   while also carrying purpose = university application and target university = UChicago"). The
   licence has a price the gate enforces: when both edges exist on a pair, the `collides_with`
   side must carry a non-empty `signal` naming the discriminating evidence.
2. `file_kind_plausible` is constitutionally never-alone. No schema may activate on it as sole
   support (activation step 2). `.pdf → Independent Records` and `.ics → Calendar` are the two
   canonical violations; both are forbidden by construction.
3. `uses_schema` is total and unique on templates: every template names exactly one schema.
   A template with zero or two is malformed.
4. `parent_id` chains must be acyclic; a `parent_id` may only name another `kind: template` row.
   A `parent_id` naming a schema is the smuggled schema-tree and is rejected.
5. A `falls_through_to` target must be one of the nine `00` residual names, spelled `00`'s way.
   A residual home that shadows a domain template (a residual `Travel` beside a travel template)
   must be connected by `falls_through_to` from that template or it is a duplicate, not a
   fallback.

## 6. Field identity — one canonical list

A field is a **global token**. `school` on coursework is `school` on teaching. `target_university`
is a different field — not because the entity differs (both are universities) but because the
role differs (§3.8). `00`: "Fields define the long-term organization language of the product;
values are the changing, user-specific content discovered from files."

- **Where the list lives:** `planning/domains/canonical_fields.json` — one table, emitted by R1a.
  Schemas **reference** keys from it; no schema declares a private field. The 574's failure mode —
  2,295 distinct names for what should have been one shared vocabulary, 80% used by exactly one
  schema — is impossible under this rule, because a `schema[].field` that does not resolve to the
  canonical list is a gate failure (enforced once the list lands; see Gate status).
- **Seed contents:** the six universal fields as `00` names them (file type, creation date,
  language, duplicate family, version family, sensitivity status), P6's recorded
  `download_session`, and the six domain rows `00` states — "Academic files may use school, term,
  course, instructor, and work type", "College application files may use target university,
  application cycle, application document type, and purpose", "Research files may use project,
  stage, artifact type, lab, and venue", "Finance files may use institution, account type, tax
  year, and record type", "Photos may use capture year, event, location, people, camera
  information, and media type", "Code files may use project, repository, programming language,
  and artifact type" — plus §3.8's four role fields. Everything further is R1a's, marked by
  provenance.
- **Aliases are value-level, not field-level.** "If a document says U Chicago, the raw
  observation remains exactly that wording" while a resolver normalizes and the user re-displays.
  `U Chicago` → `University of Chicago` is a **value** alias inside one field. There are no field
  aliases: two spellings of a field key are two columns, which is the defect D6's ratification
  exists to kill.
- **Spelling:** snake_case, per the ratification already recorded in `_CONTRACT.md` rule 8
  ("D6, ratified 2026-08-21") and enforced by the gate. The stored academic key is `subject`;
  "course" is `00`'s prose for the same concept and survives inside quotations only. This
  document closes nothing itself — it follows the recorded ratification, and R1 output is
  internally snake_case-consistent either way. `UNSETTLED-D6` applies only in the sense that if
  Joseph reverses the recorded ratification, the fold in `check.py` is the single place spelling
  is enforced and the catalogue re-normalizes mechanically.
- **`destination_eligible` is per field**, recorded on the canonical row, with two overrides:
  authorship and creator-identity fields are never destination-eligible ("It should avoid using
  authorship or creator identity as a destination dimension"), and a schema may additionally
  forbid one of its fields as a folder level for its own domain (`metadata_only` on the
  template's dimension entry, P10's mechanism). A field's eligibility is never widened by a
  schema.
- **`role_split` lives here** (section 5): `authored_by ↔ target_school`, `our_firm ↔ client`,
  `school ↔ target_university`. Reciprocal, checked by the gate once the list exists.

## 7. Templates, schemas, residuals, groups — four objects, four owners

The table people keep collapsing, uncollapsed:

| Object | Owner | Job |
|---|---|---|
| Domain **schema** | P6 | which fact fields are legal when the domain is active — the §3.6 validator's allow-list |
| Domain **template** | P10 | which of those fields may become folder levels, and in what recommended order; detection signals; privacy rules; validation constraints ("Each template should define the domain’s allowed fact fields, detection signals, recommended folder dimensions, preferred dimension order, optional branch patterns, privacy rules, and validation constraints") |
| **Residual** template | P10 definitions, P11 workflow | broad destination when **no** domain association is reliable. Nine `00` names. Not a domain, not a 575th schema — the complement of reliable domain association: it exists exactly for files with "no reliable deeper association" |
| **Group** | P9 | files that belong together — one course-term, one application packet. Purpose-coherent, not always content-coherent ("The documents are content-incoherent but purpose-coherent") |

Binding statements:

- A template **points at** one schema (`uses_schema`); it does not duplicate the field list. Its
  `dimension_order` is a **recommendation**: "The system recommends an order based on the domain
  template, but the user can reverse, remove, add, or flatten dimensions."
- **A group does not create a schema.** Accepted groups are what P10 fits templates to; a group
  label (`PHYS1401 — Spring 2026`) is never a roster id.
- **Residual is not a domain.** A residual home never carries a schema, never activates, and is
  reached by `falls_through_to` or by the empty activation set — never by detection signals of
  its own beyond `00`'s "accepted evidence patterns" slot (R3's content).
- **Custom LLM templates** must "use existing field types wherever possible" and a generated
  template "cannot invent unsupported facts, silently create new high-level domains, or become
  active merely because it is syntactically valid". Concretely: a custom template's `uses_schema`
  must name an existing roster schema, and its dimensions must name canonical fields. It can add
  a template row (after user approval, P10's flow); it can never add a schema row.
- **Facts are not paths.** "The user may later organize the same facts as
  Academics/Columbia/2026-Spring/BUSIB 4300/Syllabus or as Academics/BUSIB 4300/Spring
  2026/Syllabus" — "The facts have not changed; only the user’s preferred organization view has
  changed." A folder path appears in no fact row, no roster row, no activation output.
- **P10 uses templates without treating them as categories.** A template is a proposal generator
  over an accepted branch — it "determines how those real values could be arranged as branches" —
  not a class the file belongs to. Template choice happens per accepted branch, after grouping,
  from `active_domains` ∪ accepted `group_category`; it is never written onto a file as a fact,
  and "Freeze records the approved hierarchy and prevents later systems from inventing new
  destinations outside it."

## 8. What P6 / P8 / P9 / P10 / P11 each read

The single-vocabulary table. Function names are contract even where unbuilt; a part that
re-derives a column below has built the second vocabulary this document exists to prevent.

| Function | Reads (which graph) | Returns | Must NOT re-derive |
|---|---|---|---|
| `active_domains(content_hash) -> frozenset[schema_id]` (P6 computes; P8/P9/P10 read) | schema-activation over the file's own evidence | set of schema ids + `unresolved` + `residual_candidate` | anything from `parent_id`; anything from group membership |
| `active_field_allowlist(content_hash) -> frozenset[field_key]` (P6 → P8) | fields graph + activation set | universals ∪ fields of plausible schemas | a per-format or per-template field list; any field not in the canonical table |
| `collides(a, b) -> bool` (P6 activation step 3; P8 validator) | roster `collides_with` edges | whether one evidence item may count for both | topic similarity; anything beyond the authored edge |
| `also_holds(a, b) -> bool` (P6, P8, P9) | roster `also_holds_with` edges | whether two schemas may co-activate on one file | a default of false for unlisted pairs being read as *same file may never hold both facts* — unlisted just means unasserted; the gate keeps the authored list honest |
| `destination_dimensions(domain_id) -> ordered field_keys` (P10; P11 reads frozen result) | folder-dimension graph via the template (`domain_id` is a template id, or a schema id resolving through the schema's default template) | recommended `dimension_order`, user-editable | field definitions; activation; a category for the file |
| `residual_candidates(content_hash) -> [residual_name]` (P11) | activation flags + `falls_through_to` edges | the ordered broad homes worth offering | new residual names; a schema; any destination outside the frozen tree |
| P9 grouping reads | file-neighborhood graph + P6 facts (`direct`/`validated` anchors) | groups + memberships (`direct-anchor` / `context-supported` / `user-attached`) | schema activation (groups never activate schemas); facts onto members |
| P10 tree design reads | accepted groups + `active_domains` + templates + residual library | frozen nodes + destination profiles | fields; facts; activation; paths (P12 composes paths) |
| P11 placement reads | frozen tree + profiles + facts + groups + `falls_through_to` | placement decisions incl. abstention | destinations (invent none); activation; sensitivity (P7's) |

## 9. Failure modes forbidden by construction

Each of these is expressible only by violating a named rule above, which is what *by construction*
means here. The gate catches the mechanical ones; review catches the rest.

1. **Schema-tree inheritance used to make `school` legal on a syllabus.** The field is on the
   Academic schema; the allow-list is a union (section 3); no child schema is required and no
   parent walk exists.
2. **Work types or extensions as schemas.** `syllabus` is a value of `work_type`; `.ics` is a
   `SOURCE_TYPE`. Node test (section 2) refuses both.
3. **`collides_with` used to mean `also_holds_with`.** They are different edges with different
   invariants; a pair may carry both only with a discriminating `signal` (section 5).
4. **Format-only activation.** `.pdf → Independent Records`, `.ics → Calendar schema`.
   `file_kind_plausible` is never-alone (sections 4–5), and no calendar schema exists unless `00`
   names one (it does not).
5. **A second field named `course_name` beside `subject`.** Fields resolve to one canonical list
   (section 6); an unresolvable field key is a gate failure once the list lands.
6. **Residual `Travel` duplicating a travel template without `falls_through_to`.** Section 5,
   invariant 5.
7. **500+ schemas.** The roster targets `00`'s "roughly 200–300" templates over a small schema
   list, and stops under that if honest (ALIGNMENT's rule). Hundreds of hand-authored schemas is
   the named anti-goal.
8. **Copying a course fact onto `HW 3.pdf` because a group exists.** The grouping firewall
   (section 4, step 9): "The graph does not automatically copy those missing facts onto sparse
   files." Activation ≠ grouping; membership ≠ fact.
9. **Writing a folder path as a fact.** Section 7: facts are not paths; `file_facts` carries no
   path column (P6's negative contract), and no roster row carries a filesystem path.

## 10. NEEDS-JOSEPH

Only real forks. Each carries a labelled provisional rule in section 11 so R1 is not blocked.
D1, D2 and D6 are **not re-opened and not extended here**: their ratified/narrowed state as
recorded in `DECISION-BRIEF.md` and `_CONTRACT.md` is carried as-is.

- **NJ-1 · The counting rule for "500+".** `00` sizes the template library at "roughly 200–300
  domain-specific templates". Joseph's later request says 500+ domains and subdomains. Fork: is
  "500+" satisfied by the connected whole (schemas + templates + residual homes + the folder
  depth inside templates), or must the template roster itself exceed 500 (which contradicts `00`
  and re-creates the quota-writing that produced the 574)?
- **NJ-2 · Safety-domain ordering: protect-then-extract, or extract-under-protection?** `00`
  gives Finance a fact schema *and* names it a safety domain ("detects and protects them before
  any cloud or automated placement decision is allowed"). Does the Finance/identity/medical/legal
  small schema extract at launch under local-only rules, or does detection-and-protection precede
  any field extraction at all? (P6 open question 5's seam with P7, surfaced here because the
  `is_safety_domain` attribute makes it a roster-visible split.)
- **NJ-3 · `purpose`: universal or Applications-scoped?** `00` makes purpose "a first-class
  facet" yet lists it only inside the College-applications sentence. A purpose-defined packet
  outside admissions (a visa application, a consulting proposal packet) has no schema that
  legitimises `purpose` under the literal reading. (P6 open question 3, restated as a connection
  question because `also_holds_with` joins hang on where `purpose` lives.)
- **NJ-4 · Where does protected-record surfacing land?** A passport with no deeper group: P9
  group, P7 surface, or P11 residual routing into Protected Records? (P9 open question 9;
  affects whether `falls_through_to identity → Protected Records` is the whole story.)
- **NJ-5 · Does the browse `parent_id` ship at all in v1?** It is load-bearing for nothing; its
  only cost is the temptation this document forbids. Ship as UI sugar, or omit until a browse
  surface exists?

## 11. Provisional rules (R1 builds on these until Joseph answers)

Each is labelled `provisional` and reversible; none is a ratification.

- **PR-1** (for NJ-3): `purpose` stays exactly where `00`'s sentence puts it — a
  College-applications field ("It is a field available only when the Applications domain is
  plausibly active" is the pattern sentence for every domain field). A purpose-coherent packet
  outside admissions activates the nearest roster schema on its own evidence, or falls through to
  residual; R1b must not mint per-domain `purpose` clones.
- **PR-2** (for NJ-2): safety schemas activate for **protection plus the small schema**; the four
  Finance fields extract at launch under local-only rules; no deep template unlocks from safety
  activation; P7 classification always precedes any model path. Identity/medical/legal remain
  field-less placeholders (D1 as narrowed — no field rows written).
- **PR-3** (for NJ-1): the roster targets 200–300 `kind: template` rows over a schema list small
  enough to read in one sitting ("Stop under that if honest" — ALIGNMENT, verbatim). "500+" is reported to
  Joseph as the connected-catalogue count, never manufactured by minting schema rows.
- **PR-4** (for NJ-4): a safety-activated file with no accepted deeper group is offered its
  `falls_through_to` residual home (passport → Protected Records), which "should normally remain
  local-only and must not cause filenames or content to be exposed in model prompts"; which part
  *surfaces* it stays open and nothing in the roster depends on the answer.
- **PR-5** (for NJ-5): R1c **may** author `parent_id` on templates as browse sugar; R1b never
  authors it (per-template agents cannot see the shelf); nothing reads it except a future browse
  UI; the gate enforces acyclicity and template-only endpoints either way.
- **PR-6**: placeholder schemas (career, identity, medical, legal) exist as `kind: schema` rows
  with an **empty `schema` field list** — a row may describe the domain, and it may not write
  field rows (D1 as narrowed; career fields are owed before P10). The Career *template* row
  exists and `uses_schema` points at the placeholder ("a Career template may define company →
  role or recruiting cycle → document type" is its recorded dimension recommendation, held as
  prose until the schema lands).
- **PR-7**: teaching-a-course vs taking-a-course is **one Academic schema**. If distinct fields
  are ever genuinely needed, that is a `role_split` on the field level or a second template on
  the same schema — never a second schema that reinvents `school`.
- **PR-8**: insurance (personal / corporate / healthcare) is **templates over the Finance schema
  vocabulary** (`institution`, `account_type`, `record_type`, `tax_year`) — three organizational
  situations, not three schema slugs. Where healthcare insurance touches medical material, the
  medical safety placeholder co-activates via `also_holds_with`; it still writes no fields (PR-6).

---

## Appendix — Gate status and the migration debt

Recorded so the done-when clause — check.py passes on the current 574, or the fields that would
fail once R1 migrates are documented — is discharged honestly, by documenting:

- **Today**, `python3 planning/domains/check.py` reports **14 files, 574 entries, 566 in-file
  problems, 0 cross-file problems**. All 566 are the tightened dimension rule (a template
  branching on a field its schema does not declare) plus snake_case findings on the legacy
  slices. They pre-date this document, they are the audited debt of the overnight 574, and this
  delta neither fixes nor hides them: the 574 are superseded by R1's roster, not repaired.
- **The R0 delta adds checks that fire only on the new shape** (entries carrying `kind`, or
  carrying a new edge key), so the legacy count is unchanged by construction — verified by
  running the gate before and after the delta.
- **What fails on migration, by design.** When R1 re-emits the catalogue: every entry must carry
  `kind` (all 574 lack it); every `kind: template` must carry `uses_schema` (none has it);
  `collides_with` reciprocity becomes enforced (the audit found 1,103 of 1,977 directed collision
  edges one-way); every schema field key and every dimension must resolve to
  `canonical_fields.json` once R1a lands it (the 574 carry 2,295 distinct field names, most of
  which will not and should not survive); `shares_field`, if anyone serializes it, is rejected as
  derived-only. These are not gate bugs; they are the contract doing what the 574's gate did not.

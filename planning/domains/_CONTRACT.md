# Domain catalogue — the entry contract

Date: 2026-08-21
Status: **shape contract.** Every catalogue file conforms to this or it is not merged.
Source of truth: [`00-database-agent-product-design.md`](../00-database-agent-product-design.md)

P10 reuse clarification (2026-08-26): this catalogue's `kind: template` row remains bound to exactly
one `uses_schema`. It is an authored applicability source, not proof that its organization recipe is
owned by that schema. The later template-building pass may link several one-schema applicability
records to one shared P10 template definition or fragment. Current agents must not add keys to the
closed JSON shape. See [`TEMPLATE-BUILDING-HANDOFF.md`](TEMPLATE-BUILDING-HANDOFF.md).

## What a "domain" is, in this product

Not an industry label. The design makes it a load-bearing mechanism in three places:

- **§3.3** — rules do "routing obvious files into plausible domains"; the LLM handles files
  that "have multiple plausible domains", and "may extract only fields **allowed by the relevant
  schema**".
- **§3.5** — the LLM "can only propose facts that belong to the **active domain schema**".
- **§3.6 / §4.8** — the validator checks "that each fact or label belongs to an **allowed domain
  schema**".
- **§5.3** — the tree proposes "one or more **domain templates** based on the groups and facts
  that already belong inside it".

So a domain is **a schema (which fact fields are legal) plus a template (how its branch is
shaped)**. The domain catalogue is therefore the allow-list the §3.6 validator enforces and the
menu §5 draws its branch proposals from. It is not decoration.

The design names these exemplars and no others: **Academic, Applications, Research, Career /
Recruiting, Photos, Travel, Financial.** Everything beyond that list is an ADDITION, and every
addition must be marked as such (see `provenance` below). The design's own words are the ceiling
on what may be asserted; the rest is a proposal for Joseph.

## Required fields, per entry

```json
{
  "id": "acad.course-enrollment",
  "name": "Course enrollment and coursework",
  "supercategory": "education-academia",
  "one_line": "Files produced by taking a specific course in a specific term.",

  "provenance": "design | inference | proposal",
  "design_cite": "§3.2 'subject = BUSIB 4300', 'term = Spring 2026', 'work type = syllabus'",

  "schema": [
    {"field": "subject", "type": "string", "example": "BUSIB 4300",
     "reliability_ceiling": "validated",
     "why": "§3.5: 'BUSIB 4300 becomes a course fact only when the engine finds a course-code
             pattern together with academic context'"}
  ],

  "recognition": {
    "deterministic": ["a course-code pattern co-occurring with 'syllabus' | 'lecture' |
                      'credits' | 'instructor' | 'semester'"],
    "needs_llm": ["an unlabeled essay whose only course signal is the prose topic"],
    "never_alone": ["a bare 4-digit number", "a university name with no course context"]
  },

  "work_types": ["syllabus", "problem set", "lecture slides", "exam", "lab report"],

  "grouping_reasons": ["one course in one term", "one assignment across its drafts"],

  "template": {
    "dimension_order": ["school", "term", "course", "work type"],
    "why": "§5.7: 'a parent dimension should provide the context required to understand the
            child. A work type such as Homework 3 is meaningful only after the course is known'",
    "time_first": false
  },

  "collides_with": [
    {"domain": "acad.admissions-application",
     "signal": "both carry a university name; only the application carries a target-institution
                + cycle pair",
     "design_cite": "§4.8: 'an application packet does not silently absorb a document with a
                     conflicting target institution'"}
  ],

  "sensitivity": "none | potentially_sensitive",
  "sensitivity_why": "§2.9's own phrase only; a handling CLASS is P7's and is never set here",

  "open_question": null
}
```

## Rules

1. **`provenance` is mandatory and honest.** `design` only when a design sentence names the
   domain or its fields; `inference` when you are extending a named one; `proposal` when it is
   new. A `design` claim with a `design_cite` that does not say what you claim is the worst
   possible failure here.
2. **Never fabricate a quotation.** Quote `00-database-agent-product-design.md` exactly, or write
   no quote and mark the row `inference`. A previous review in this project invented three of
   four clauses inside quote marks. That must not recur.
3. **No thresholds, no numbers, no confidence scores.** §8.6's ceilings are P1's and every
   threshold in this product is injected. A catalogue entry that holds a number is wrong.
4. **`reliability_ceiling` uses §3.13's states only** — `direct`, `possible`, `validated`,
   `llm_supported`, `user_confirmed`, `rejected`. An extractor may only ever write the first two
   (P4 D11), so a field claiming `validated` is claiming a RULE will confirm it, which means the
   `recognition.deterministic` entry must actually support that.
5. **`sensitivity` is §2.9's phrase and nothing more.** Handling classes are P7's (§8.4).
   A catalogue that assigns one is inventing P7's vocabulary.
6. **A collision names a domain OR a residual template, never both in one field.**
   `{"domain": "<a real id from any catalogue>"}` for a fact-schema collision;
   `{"residual_template": "<§7's own name for it>"}` when the thing a file might be confused with
   is one of §7.2–7.4's residual templates, which are P10/P11's and have no id in this namespace.
   The first version of this contract had only `domain`, so two authors put a template description
   there and the gate read it as a broken id. **A `domain` value that is not a real id is an error;
   the gate enforces it.**
7. **Anything genuinely undecidable goes in `open_question`** and gets copied into
   `NEEDS-JOSEPH.md`. Do not resolve a question that is Joseph's — especially where a domain
   implies a default folder structure for someone's real life.
8. **Field keys are `snake_case`, and a template may only branch on a field the same entry's
   schema declares (D6, ratified 2026-08-21).** Both halves are enforced by the gate.

   The key is a **stored join handle**: it lands in a fact row, in §3.4's cache key, and in a
   template's branch order. Two spellings are two columns. This catalogue shipped with 966 spaced
   keys and 959 snake_case ones, **131 of them the same key spelled two ways** — one concept in two
   vocabularies, at scale, in a catalogue whose own gate reported "0 problems".

   The academic field is **`subject`**, not `course`. The design names it both ways — `subject =
   BUSIB 4300` in §3.1, "course" in §3.11's list and §5.4's template order — so one is the stored
   key and the other is prose. **Design quotations keep the design's wording**; only keys change.

   The second half is the one that failed: **566 of 1,648 dimensions branch on a field the schema
   does not declare.** A domain is a schema *plus* a template — the allow-list §3.6 validates
   against and the menu §5.3 draws branches from — so a dimension naming an undeclared field opens
   a tree level no fact can ever fill. Fixing these is not mechanical: 305 have no related field at
   all and need a decision about what the domain legitimises. **Do not invent fields to make the
   gate green.**
9. **`jurisdiction` is a value, never a field name and never a destination dimension (D4, ratified
   2026-08-21).** §3.12: *"The system may create new values when it sees a new course, project,
   company, university, or event, but it should not invent new fields automatically."* What varies
   by jurisdiction is values; that is what keeps this two-way. v1 ships **one** jurisdiction's
   gazetteers, injected per deployment, and the list is decided when P10 is planned. A
   jurisdiction-specific **field** name (`w2_tax_year`) is the thing that would make it one-way;
   none of the 574 entries has done that, and none may.
10. **No career, identity, medical or legal field rows (D1, narrowed 2026-08-21).** S3 deferred
   that schema and the deferral stands. This catalogue is a **placeholder that writes no field
   rows** — it may describe those domains, and it may not turn them into `fields` catalogue
   entries. **Career is owed before P10**, where a destination dimension first needs one. Adding
   one earlier is reversing S3 and must say so explicitly rather than arriving as a plan edit.

## R0 delta — two roster kinds and the closed edge vocabulary (2026-08-21)

The connection architecture lives in [`CONNECTION.md`](CONNECTION.md); this section records only
what changes about the **entry shape**. The pre-R0 entries above (the 574) predate these rules
and are superseded by R1's roster, not migrated in place.

11. **`kind` is mandatory on every new entry: `"schema" | "template"`.** R1a emits both kinds;
    R1b refuses anything else. A schema row exists only for a genuinely distinct field set; a
    template row exists only when its detection signals, recommended dimensions, or privacy rules
    differ from its schema's default (the node test, CONNECTION.md §2). The gate applies the
    kind-scoped checks below only to entries that carry `kind`, so the legacy 574 gain no new
    findings before R1 replaces them.

> ⚙️ **CORRECTION 2026-08-27 — rule 12's key name below is STALE. The corpus is right; this rule is
> wrong.** The serialized key is **`schema_id`**, not `uses_schema`. All 358 node files, `roster.json`
> itself, and R1c's own brief (`planning/prompts/01c-merge-and-gate.md`:42, *"Every template has
> `schema_id` that exists"*) use `schema_id`; **0 files anywhere contain `uses_schema`**. Read every
> "`uses_schema`" below as "`schema_id`". `01c`:56 authorises this correction ("`_CONTRACT.md`
> required keys to match R1b's object"); R1c should make it properly and update `check.py`'s key
> sets with it. The same drift affects rule 14's `file_kind_plausible`, serialized as **`file_kinds`**
> and present on template rows as well as schema rows.
>
> **Do NOT "fix" this by renaming 358 node files.** The contract text is the outlier, not the data.

12. **Every `kind: template` entry carries `uses_schema: "<schema id>"` — exactly one.** At this
    catalogue layer the row is one applicability source. A row references its schema's fields; it never copies the field list, and its
    `template.dimension_order` may only branch on fields that schema declares (rule 8's second
    half, now checked across the `uses_schema` join for templates). This one-schema safety rule does
    not impose one-domain ownership on P10's later reusable definition: several independently valid
    catalogue rows may compile to applicability records referencing the same definition/fragment, as
    specified by `TEMPLATE-BUILDING-HANDOFF.md`.

13. **`parent_id` is optional and browse-only, on `kind: template` entries only.** It shelves the
    library for humans. It is never schema inheritance, never an activation input, never a folder
    dimension; activating a template activates nothing by walking it. A forest is **not**
    required — parents are optional and roots may be many — but chains must be acyclic and a
    `parent_id` may not name a schema.

14. **The edge vocabulary is closed** (CONNECTION.md §5): `uses_schema`, `parent_id`,
    `collides_with`, `also_holds_with`, `file_kind_plausible`, `falls_through_to`, `role_split`
    (canonical field list only), plus derived-only `shares_field`. `related_to` and every other
    invented edge is a gate failure. On kind-bearing entries, `collides_with` and
    `also_holds_with` are reciprocal (both sides name each other), `also_holds_with` joins
    schemas only, `collides_with` joins same-kind pairs, and a pair carrying both must have a
    non-empty `signal` on the collision. `falls_through_to` targets one of §7.3's nine residual
    template names — residuals are still not entries in this namespace (rule 6 stands).
    `file_kind_plausible` lists P5 `SOURCE_TYPES` members or literal extensions on schema rows,
    and is never sufficient alone. **`shares_field` is computed from canonical field references
    and may never be authored.** Closed is enforced by construction, not by a blocklist: on
    kind-bearing entries the gate accepts only the entry keys this contract names (the shape
    above plus rules 11–15's keys) and reports **any** unrecognized key as a finding — so a
    novel spelling (`similar_to`, `activates_with`, …) fails the same way `related_to` does.

15. **`is_safety_domain: true` marks §3.15's four safety domains on schema rows.** It is the
    replacement for a `safety_for` edge and it is not P7's handling-class vocabulary (rule 5
    stands untouched). A placeholder schema (career, identity, medical, legal) may carry
    `schema: []` — a row may describe the domain and still write no field rows (rule 10 stands).

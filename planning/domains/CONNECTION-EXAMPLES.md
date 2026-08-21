# Connection examples — the eight worked joins

Date: 2026-08-21
Status: **fixtures (R0).** These are the joins the 574 never encoded, drawn from
[`00-database-agent-product-design.md`](../00-database-agent-product-design.md)'s own worked
files. **R1 output must remain compatible with every one of them**: the ids below are
illustrative (R1a mints the real roster and may rename), but the *kinds*, the *edges*, the
*activation sets*, and the *refusals* are binding. A roster on which any example below becomes
inexpressible — or on which any forbidden write becomes expressible — is wrong.
Contract: [`CONNECTION.md`](CONNECTION.md). Vocabulary notes: fields are snake_case canonical
keys; reliability states are §3.13's six; every threshold is an injected slot, so no fixture
carries a number as a value.

These live in a `.md` deliberately: they are not catalogue entries and must not be scanned by
`check.py` as one.

---

## 1 · Syllabus PDF — one schema, facts, a recommended order, and no path

`Syllabus BUSIB 4300 Spring 2026.pdf`. Activation is one schema; the template is a
recommendation P10 surfaces later; nothing here is a folder path.

```json
{
  "file": {"name": "Syllabus BUSIB 4300 Spring 2026.pdf", "source_type": "text_document"},
  "activation": {"schemas": ["academic"], "unresolved": false, "residual_candidate": false},
  "why": [
    {"schema": "academic", "signal": "course-code pattern + context term 'Syllabus' (§3.5 shape)"},
    {"schema": "academic", "signal": "dedicated term pattern 'Spring 2026' (§3.10 shape)"}
  ],
  "facts": [
    {"field": "subject", "value": "BUSIB 4300", "reliability": "validated"},
    {"field": "term", "value": "Spring 2026", "reliability": "validated"},
    {"field": "work_type", "value": "syllabus", "reliability": "validated"},
    {"field": "school", "value": null,
     "note": "unfilled until its own evidence clears the injected min_activation_score; no walk supplies it"}
  ],
  "roster_edges": [
    {"edge": "uses_schema", "from": "tpl.academic-coursework", "to": "academic"}
  ],
  "template_recommendation": {
    "template": "tpl.academic-coursework",
    "dimension_order": ["school", "term", "subject", "work_type"],
    "binding": "recommendation only — the user can reverse, remove, add, or flatten"
  },
  "not_written": [
    "any folder path — facts are not paths",
    "a template id as a fact on the file"
  ]
}
```

## 2 · Academic abstract inside an application packet — two schemas at once

`00`'s own case: the abstract keeps `project = PVA/RDP` and `document type = abstract` while also
carrying `purpose = university application` and `target university = UChicago`. This is
`also_holds_with`, not a merge and not a collision-resolution.

```json
{
  "file": {"name": "PVA-RDP Abstract.pdf", "source_type": "text_document"},
  "activation": {"schemas": ["research", "college_applications"],
                 "unresolved": false, "residual_candidate": false},
  "why": [
    {"schema": "research", "signal": "project identifier + abstract structure, from the file's own text"},
    {"schema": "college_applications", "signal": "application language / packet context, from the file's own evidence"}
  ],
  "roster_edges": [
    {"edge": "also_holds_with", "from": "research", "to": "college_applications",
     "reciprocal": true}
  ],
  "facts": [
    {"field": "project", "value": "PVA/RDP", "reliability": "validated"},
    {"field": "artifact_type", "value": "abstract", "reliability": "validated"},
    {"field": "purpose", "value": "university application", "reliability": "llm_supported"},
    {"field": "target_university", "value": "UChicago", "reliability": "llm_supported"}
  ],
  "groups": [
    {"group": "research PVA/RDP", "membership": "included"},
    {"group": "UChicago application packet", "membership": "included"}
  ],
  "binding": "both fact sets kept; placement decided later; neither schema drops the other's fields"
}
```

## 3 · University name alone — no schema, no group

`00`: Columbia can be an authoring school, course provider, target institution, employer,
research venue, or merely a cited organization. A gazetteer hit alone activates nothing and
groups nothing.

```json
{
  "file": {"name": "notes.txt", "source_type": "text_document",
           "evidence": [{"zone": "body", "raw_value": "Columbia"}]},
  "activation": {"schemas": [], "unresolved": true, "residual_candidate": true},
  "why_not": [
    {"rule": "never_alone",
     "signal": "university gazetteer hit with no role context",
     "blocked_schemas": ["academic", "college_applications", "research", "career"]}
  ],
  "groups_formed": [],
  "binding": "a university name alone must not create a group and must not activate a schema"
}
```

## 4 · Passport scan — safety activation, protection, residual fallthrough

Safety split: the identity schema activates for protection plus its (placeholder, field-less)
small schema; no deep template unlocks; the residual home is Protected Records; content never
reaches a cloud prompt.

```json
{
  "file": {"name": "IMG_2231.jpg", "source_type": "image",
           "evidence": [{"zone": "ocr", "raw_value": "PASSPORT / PASSEPORT ..."}]},
  "activation": {"schemas": ["identity"], "unresolved": false, "residual_candidate": true},
  "roster_rows": [
    {"id": "identity", "kind": "schema", "is_safety_domain": true,
     "schema": [], "note": "placeholder — writes no field rows (D1 as narrowed)"}
  ],
  "roster_edges": [
    {"edge": "falls_through_to", "from": "identity", "to": "Protected Records"}
  ],
  "consequences": [
    "P7 classification precedes any model path",
    "no deep template unlocks from safety activation",
    "if no deeper accepted group exists, the offered home is the Protected Records residual",
    "filenames and content are never exposed in model prompts for this material"
  ],
  "not_written": ["a cloud dossier", "a deep folder proposal", "an invented trip/application association"]
}
```

## 5 · A `.ics` — a SOURCE_TYPE is not a domain

Slice 14's calendar-as-domain was the format-as-schema bug. `calendar` is one of P5's fourteen
`SOURCE_TYPES`; it may make a roster schema plausible only together with content, and `00` names
no calendar schema.

```json
{
  "file": {"name": "invite.ics", "source_type": "calendar",
           "evidence": [{"zone": "field", "raw_value": "SUMMARY: PHYS1401 Midterm Review"}]},
  "activation": {"schemas": ["academic"], "unresolved": false, "residual_candidate": false},
  "why": [
    {"schema": "academic",
     "signal": "content evidence (course code + academic context in the event title)"},
    {"note": "source_type=calendar contributed only as file_kind_plausible — never alone"}
  ],
  "counterfactual": {
    "file": {"name": "invite.ics", "evidence": [{"zone": "field", "raw_value": "SUMMARY: lunch"}]},
    "activation": {"schemas": [], "unresolved": true, "residual_candidate": true}
  },
  "forbidden": [
    {"roster_row": {"id": "calendar.events", "kind": "schema"},
     "why": "a file format as a schema — rejected unless 00 names a calendar schema (it does not)"}
  ]
}
```

## 6 · `HW 3.pdf` — activation ≠ grouping, stated as data

The filename writes no course fact. P9 may attach the file to the course neighborhood as a
context-supported member **without copying the course fact onto the file**. Two different
records; only one of them mentions a course.

```json
{
  "file": {"name": "HW 3.pdf", "source_type": "text_document",
           "evidence": [{"zone": "body", "raw_value": "Homework 3"},
                        {"zone": "filename", "raw_value": "HW 3"}]},
  "activation": {"schemas": ["academic"], "unresolved": false, "residual_candidate": false,
                 "note": "homework-shaped evidence from the file itself; nothing supplies a course"},
  "facts": [
    {"field": "work_type", "value": "homework", "reliability": "validated"},
    {"field": "subject", "value": null,
     "note": "REFUSED from filename; unresolved row, not a fact"}
  ],
  "neighborhood": {
    "group": "PHYS1401 course materials",
    "membership": {"file": "HW 3.pdf", "basis": "context-supported",
                   "decision": "uncertain", "review": "pending-review"},
    "support": ["mutual-semantic-retrieval with course anchors", "compatible work type"]
  },
  "binding": [
    "the membership record may exist while the subject fact does not",
    "no P9 record ever writes a fact onto the file; the graph assembles context, it does not propagate labels"
  ]
}
```

## 7 · Teaching a course vs taking a course — one schema, split by role or template

Not two schemas that each reinvent `school`. If the fields genuinely differ, the difference is a
`role_split` between canonical field keys, or a second template on the same Academic schema.

```json
{
  "roster_rows": [
    {"id": "academic", "kind": "schema",
     "schema": ["school", "term", "subject", "instructor", "work_type"]},
    {"id": "tpl.academic-coursework", "kind": "template", "uses_schema": "academic",
     "situation": "taking a course",
     "dimension_order": ["school", "term", "subject", "work_type"]},
    {"id": "tpl.academic-teaching", "kind": "template", "uses_schema": "academic",
     "situation": "teaching a course",
     "dimension_order": ["term", "subject", "work_type"],
     "note": "differs in detection signals and recommended dimensions — that difference is what licenses the second template row"}
  ],
  "field_edges": [
    {"edge": "role_split", "between": ["authored_by", "target_school"], "home": "canonical_fields"},
    {"note": "if a teaching-specific role field is ever needed, it is a canonical field with a role_split — never a second schema"}
  ],
  "forbidden": [
    {"roster_row": {"id": "acad.teaching", "kind": "schema", "schema": ["school", "term"]},
     "why": "a second schema whose fields are a respelling of academic's fails the node test"}
  ]
}
```

## 8 · Insurance — one field vocabulary, three templates

Personal, corporate, and healthcare insurance share the Finance field vocabulary
(`institution`, `account_type`, `record_type`, `tax_year`). Three organizational situations,
three template rows, one schema — never three unrelated schema slugs.

```json
{
  "roster_rows": [
    {"id": "finance", "kind": "schema", "is_safety_domain": true,
     "schema": ["institution", "account_type", "tax_year", "record_type"]},
    {"id": "tpl.insurance-personal", "kind": "template", "uses_schema": "finance",
     "situation": "an individual's policies and claims",
     "dimension_order": ["institution", "record_type"]},
    {"id": "tpl.insurance-corporate", "kind": "template", "uses_schema": "finance",
     "situation": "a firm's coverage, certificates, claims",
     "dimension_order": ["institution", "record_type", "tax_year"]},
    {"id": "tpl.insurance-healthcare", "kind": "template", "uses_schema": "finance",
     "situation": "health coverage: cards, EOBs, claims",
     "dimension_order": ["institution", "record_type"],
     "roster_edges": [
       {"edge": "also_holds_with", "from": "finance", "to": "medical", "reciprocal": true,
        "note": "an EOB can carry medical-domain facts once the medical schema has fields; today medical is a field-less safety placeholder"}
     ]}
  ],
  "forbidden": [
    {"roster_rows": ["ins.personal", "ins.corporate", "ins.healthcare"],
     "why": "three schema slugs with private field names — the 574's defining failure"}
  ]
}
```

# Domain catalogue — the entry contract

Date: 2026-08-21
Status: **shape contract.** Every catalogue file conforms to this or it is not merged.
Source of truth: [`00-database-agent-product-design.md`](../00-database-agent-product-design.md)

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

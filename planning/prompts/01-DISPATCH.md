# How to dispatch R1b at hundred-agent scale

Stamp [`01b-per-domain-research.md`](01b-per-domain-research.md) onto **every row** in `planning/domains/roster.json`. Same prompt body. Different ASSIGNMENT. Different output file.

Do this **after** R0 (`CONNECTION.md` / [`ALIGNMENT.md`](ALIGNMENT.md)) and R1a (`roster.json` + `canonical_fields.json`). Do not fire R1b against the old 574 slice files. Those were 574 schemas; you are dispatching **templates** plus a handful of schemas.

## Isolation (non-negotiable)

Each swarm agent:

| May | Must not |
|---|---|
| Read `00`, `01`, CONNECTION, `_CONTRACT`, roster, canonical_fields, `SOURCE_TYPES`, already-written neighbour `nodes/*.json` | Edit `src/`, SPECs, `00`, roster, canonical_fields, another node's file |
| Write `planning/domains/nodes/<id>.json` | Create children ids |
| Write `planning/domains/nodes/<id>.research.md` | Rename its id |
| Propose a new field in `proposed_fields[]` | Silently add a field that is a synonym of a canonical key |

If two agents write the same path, you get a lost node. The dispatcher is responsible for **one agent per id**.

## Fill the ASSIGNMENT

Every R1b session starts with this block **above** the copied prompt, or spliced into the ASSIGNMENT section. Generate it from the roster; do not let the agent invent it.

```json
{
  "kind": "template",
  "domain_id": "academic.coursework",
  "schema_id": "academic",
  "parent_id": null,
  "name": "Coursework (taking a course)",
  "one_line_hint": "Files a student produces or receives by taking one course in one term.",
  "launch": "full",
  "must_consider_neighbors": ["applications", "research"],
  "must_consider_residuals": ["Independent Records", "Reading Inbox"],
  "inherited_field_keys": ["school", "term", "course", "instructor", "work_type"],
  "output_json": "planning/domains/nodes/academic.coursework.json",
  "output_research": "planning/domains/nodes/academic.coursework.research.md"
}
```

Dots in ids are the filename. Do not slash them.

## Generate the stamped prompt

From the repo root:

```text
python3 planning/domains/dispatch/make_prompt.py acad.coursework.enrollment
```

prints the full R1b prompt with ASSIGNMENT filled. Redirect to a file and paste that into a new agent.

All ids:

```text
python3 planning/domains/dispatch/make_prompt.py --all --out-dir /tmp/r1b-prompts
```

writes one `.md` per roster row.

## Batching

Most harnesses will not run 500 concurrent agents. Use the roster in waves:

1. **Schema rows first** (handful) — so templates can reuse `inherited_field_keys`.
2. **Template rows in parallel** — this is the hundred-agent fire. Waves of 20–40.
3. **R1c merge** after the roster is landed or refused.

Do **not** wait for neighbour JSON. `must_consider_neighbors` is roster **schema** ids. R1c makes edges reciprocal.

## What “research / fact-check” means per agent

Not a paraphrase of the roster hint. For that one domain they must:

- Name **real files** (filenames + what’s inside).
- Split **observations** (raw) from **facts** (conclusions, with reliability).
- Keep the schema to **3–6** destination fields; templates reuse them.
- Mark facts that must **abstain** (university name alone, session as topic, `HW 3` as a course code).
- Recommend `dimension_order`; do not write a path as a fact.
- Point leftovers at a **residual** template, not a fake schema.

If they cannot find distinct files and distinct facts, they `refuse_node` rather than pad.

## After the swarm

Run R1c ([`01c-merge-and-gate.md`](01c-merge-and-gate.md)). Missing node files, refuse_node without reason, one-way collisions, and synonym fields are merge failures, not “close enough.”

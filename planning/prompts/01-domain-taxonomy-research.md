# R1 pipeline — small schemas, then one research agent per template

This is the **orchestrator** page. Do not paste this whole file into a swarm agent.

Read [`ALIGNMENT.md`](ALIGNMENT.md) first. `00` wants few **schemas** and ~200–300 **templates**. Joseph wants one research agent per node. Those land if the swarm is stamped on **templates** (plus a handful of schema rows), not on 500 industry schemas.

The overnight 574 failed because it built 574 schemas with private field names. Parallel research only works if:

1. **R0** writes how `00`'s objects join (schema, template, group, residual, fields). Not an industry DAG.
2. **R1a** publishes canonical fields, a **small schema list**, and the **template roster**.
3. **R1b** one agent per roster row — fact-checks files, observations vs facts, detection signals.
4. **R1c** merges (shared fields, reciprocal edges, file-kind coverage).

Without ALIGNMENT, a hundred agents reproduce the 574.

## Waves

```text
R0   CONNECTION.md          one agent     how 00's objects join (not an industry DAG)
R1a  schemas + templates    one agent     small schema list; 200–300 template roster; canonical fields
R1b  per-row research       ONE AGENT PER ROSTER ROW
                            hundreds of dispatches on templates; a handful on schemas
R1c  merge + fact-check     one agent     reuse of fields; reciprocity; SOURCE_TYPES; refuse padding
```

R1b is the prompt you fire at scale. It is written so that **after the roster exists**, every domain and subdomain gets the same research job: real files, facts/facets, recognition, template, edges.

## Files in this pack

| Wave | Prompt | Writes |
|---|---|---|
| R1a | [`01a-spine-roster.md`](01a-spine-roster.md) | `planning/domains/roster.json`, `canonical_fields.json` |
| R1b | [`01b-per-domain-research.md`](01b-per-domain-research.md) | **only** `planning/domains/nodes/<id>.json` + `.research.md` |
| R1c | [`01c-merge-and-gate.md`](01c-merge-and-gate.md) | gate extensions, FOREST-REPORT, reciprocity |
| how | [`01-DISPATCH.md`](01-DISPATCH.md) | how to stamp R1b onto every roster row |

Helper: `python3 planning/domains/dispatch/make_prompt.py <domain_id>` prints R1b with that row's ASSIGNMENT filled.

## Why not one agent for the whole catalogue

A domain here is a **fact schema + folder template**. Filling that honestly means looking at actual files (a syllabus PDF is not a W-2, is not a HEIC, is not a `.ics`). That work does not share writable state across nodes **if** each agent:

- may **read** `00`, CONNECTION, roster, canonical fields, neighbour node files if they already landed
- may **write** only `nodes/<its-id>.*`
- must **reuse** canonical field keys instead of minting `course_name` beside `course`
- must **not** add children or rename ids (the roster is closed)

That is the parallel-agents rule: independent problem domains, no shared writes.

## Stop conditions (whole pipeline)

- Roster splits `kind: schema` (few) and `kind: template` (~200–300, stop under if honest).
- Every roster id has a node file (R1b), or an explicit `refuse_node`.
- `python3 planning/domains/check.py` is green on `nodes/` (R1c).
- Templates reuse schema fields; schemas stay small (3–6 destination fields).
- Every `SOURCE_TYPES` member appears on some file_example / file_kinds.
- Honest stop **under** 300 templates if further rows would be empty labels. Padding schemas to 500 is the failure mode.

The old monolithic rebuild prompt is retired. Do not dispatch it.

export const meta = {
  name: 'r1b-swarm',
  description: 'R1b per-domain research: one Opus agent per roster row, schema rows first',
  phases: [
    { title: 'Schemas', detail: '10 schema rows', model: 'opus' },
    { title: 'Templates', detail: '73 template rows', model: 'opus' },
  ],
}

const REPO = '/Users/jy/GRAPH AGENT'

const NODE_SCHEMA = {
  type: 'object',
  required: ['status', 'refuse_node', 'files_written'],
  properties: {
    status: { type: 'string', enum: ['complete', 'blocked'] },
    refuse_node: { type: 'boolean' },
    files_written: { type: 'array', items: { type: 'string' } },
    proposed_fields: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string' },
  },
}

function rowPrompt(row) {
  return `You are one R1b swarm agent for the GRAPH AGENT repo at ${REPO} (space in the path — always quote it in shell commands). Your roster row: ${row.id} (kind: ${row.kind}).

STEP 1 — get your task. Run:
  cd "${REPO}" && python3 planning/domains/dispatch/make_prompt.py ${row.id}
Its stdout is your complete task prompt with your ASSIGNMENT filled. Follow it exactly and completely — its Read list, node test, research procedure, output spec, and Done-when list are all binding.

BINDING CONTEXT on top of that prompt (from the orchestrator; the prompt was written slightly before these landed):
- planning/domains/CONNECTION.md and CONNECTION-EXAMPLES.md EXIST and are binding — wherever the prompt says "if present", it is present. Closed edge vocabulary only; activation != grouping; parent_id is browse-only and you never author it; shares_field is never authored.
- D6 and D2 are RATIFIED (recorded in planning/overnight/council/DECISION-BRIEF.md and _CONTRACT.md): snake_case keys, the academic key is subject. Where the prompt says "D6 unset", follow the recorded ratification.
- Reading economy: read planning/00-database-agent-product-design.md IN FULL (it is the authority); for planning/01-product-design-structured.md read ONLY the sections the prompt cites plus those covering your domain area — 00 wins on any conflict.
- NEVER fabricate a quotation: any span in quote marks attributed to 00 must exist verbatim there — grep to verify BEFORE writing it. No numeric thresholds. Provenance: design | inference | proposal.
- Write ONLY your two output files: planning/domains/nodes/${row.id}.json and planning/domains/nodes/${row.id}.research.md. Never touch the roster, canonical_fields.json, other nodes, src/, SPECs, or check.py.
- refuse_node on a failed node test is a SUCCESS; padding a hollow node is the recorded failure mode.
- Concurrent unrelated workstreams churn src/ and tests/ — ignore them entirely.

Structured output: status, refuse_node, files_written, proposed_fields (canonical-key proposals you recorded, if any), notes (max 5 sentences: what you built or why you refused).`
}

const rows = args.rows
const schemas = rows.filter(r => r.kind === 'schema')
const templates = rows.filter(r => r.kind === 'template')
log(`Dispatching ${schemas.length} schema rows, then ${templates.length} template rows — one Opus agent per row`)

phase('Schemas')
const schemaResults = await parallel(schemas.map(r => () =>
  agent(rowPrompt(r), { label: `R1b:${r.id}`, phase: 'Schemas', model: 'opus', effort: 'high', schema: NODE_SCHEMA })
    .then(res => ({ id: r.id, kind: r.kind, ...res }))
))

phase('Templates')
const templateResults = await parallel(templates.map(r => () =>
  agent(rowPrompt(r), { label: `R1b:${r.id}`, phase: 'Templates', model: 'opus', effort: 'high', schema: NODE_SCHEMA })
    .then(res => ({ id: r.id, kind: r.kind, ...res }))
))

const all = [...schemaResults, ...templateResults]
const done = all.filter(Boolean)
const missing = rows.filter(r => !done.some(d => d && d.id === r.id)).map(r => r.id)
const refused = done.filter(d => d.refuse_node).map(d => d.id)
const blocked = done.filter(d => d.status === 'blocked').map(d => d.id)
const proposed = done.flatMap(d => (d.proposed_fields || []).map(f => `${d.id}: ${f}`))
return {
  dispatched: rows.length,
  landed: done.filter(d => d.status === 'complete' && !d.refuse_node).length,
  refused,
  blocked,
  missing,
  proposed_fields: proposed,
}
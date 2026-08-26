# Domain research → composable template building handoff

Date: 2026-08-26  
Status: required handoff for the later template-building pass; no runtime implementation

Read first:

1. `planning/00-database-agent-product-design.md` — authority;
2. `planning/domains/_CONTRACT.md` and `planning/domains/CONNECTION.md` — current R1 catalogue;
3. `docs/superpowers/specs/2026-08-26-composable-template-scaffolding-design.md` — P10
   composition and user-flow contract;
4. `planning/parts/P10-tree-design-freeze/SPEC.md` — frozen output contract.

## The key distinction

The current domain catalogue intentionally requires every `kind: template` row to name exactly one
`uses_schema`. Keep that rule. It protects P6/P8's per-schema fact allow-list and keeps the active
domain-research swarm on one closed JSON shape.

It does **not** mean an organization recipe belongs to only one domain.

In the later template-building pass, treat a ratified domain template row as an **applicability
source**. Compile shared organization logic into separate P10 objects:

```text
domain kind:template row --uses_schema--> one fact schema
             |
             +--> TemplateApplicability --ref--> shared TemplateDefinition
                                                    |
                                                    +--> shared TemplateFragment versions
```

Many `TemplateApplicability` rows may reference one `TemplateDefinition`. One domain/schema may have
many applicability rows. A purpose packet spanning domains composes several one-schema bindings; it
does not erase or union their fact-authority boundaries.

## What current domain agents do

- Continue following the closed node JSON contract.
- Keep one `uses_schema` per template row.
- Do not add `fragment_ref`, `template_definition_ref`, inheritance, or cross-domain activation keys.
- Explain the template's actual dimensions, ordering rationale, optional patterns, collisions,
  privacy constraints, and node-test differences in its existing JSON/research fields.
- Record cross-domain analogies in research prose when evidence supports them, without claiming they
  are already a canonical shared fragment.

Current research completion does not activate a template and does not create folders.

## What the later template-building pass does

### 1. Normalize semantic roles

Map ratified dimension fields to organization-layer roles such as subject, counterpart, lifecycle
stage, artifact kind, or time period. Roles are not P6 facts. Every applicability binding still maps
each selected role back to an existing field in its one `uses_schema` schema.

### 2. Find reuse candidates

Compare templates by semantic role sequence, ordering constraints, optionality, branch patterns,
privacy constraints, and retrieval purpose—not by matching labels alone. Candidate examples:

- project → stage → artifact kind across research, software, client, and creative work;
- counterpart → cycle → document kind across applications, recruiting, procurement, and claims;
- event → capture time across photos, media production, travel, and field work.

A similarity is only a candidate. Different meanings, privacy rules, or ordering requirements keep
the definitions separate.

### 3. Extract shared fragments

Create a fragment only when at least two reviewed contexts share stable semantics and compatible
constraints. Give it one stable ID and immutable version. Domain-specific labels, field mappings,
and evidence remain in applicability rows; they are not copied into the fragment.

### 4. Assemble template definitions

Build thin, versioned definitions from exact fragment versions plus local dimensions and constraints.
Definitions carry recommended order, not mandatory depth. Fragment imports must be acyclic and exact-
version pinned.

### 5. Emit one-schema applicability records

For every valid template/domain pairing, emit a separate binding containing:

- `template_id` and exact `template_version`;
- exactly one `uses_schema`;
- role-to-live-P6-field mappings;
- required evidence and exclusions;
- privacy constraints and purpose context where relevant;
- an authored/versioned `purpose_profile_ref` where relevant, distinct from both P6 purpose values and
  runtime P9 group IDs;
- provenance back to ratified domain rows and research evidence.

Missing or ambiguous mappings produce a configuration gap. The compiler must not invent a field or
copy a field from another schema.

### 6. Validate composition

Run P10 composition gates C1–C8, then materialize against real/fixture branch evidence and run V1–V6.
Constraint conflicts, cyclic order, weaker privacy, ambiguous roles, or silent member loss create a
deterministic report and no nodes.

### 7. Test the user flow

At minimum prove:

- one definition serves two domains through two independent one-schema bindings;
- one domain offers two different recipes;
- a mixed-domain purpose packet combines compatible fragments without losing a member;
- an incompatible combination fails closed;
- top-level-only approval, partial application, uneven depth, shallow-by-choice, and later new-version
  refinement all work;
- changing a shared definition never silently changes an approved branch.

## What prompts may and may not do

P8 Site E prompt content may propose a structured `TemplateDefinition` or composition from a bounded
dossier. It may reference published fragments by exact ID/version and may include template-local
semantic dimensions, but it cannot publish or propose a new canonical fragment. Repeated local
dimensions become fragment candidates only in the later human-reviewed synthesis pass. The model may
not invent missing schema mappings, domain truth, privacy policy, thresholds, or activation. P10
validates the proposal; the user approves the branch-local result.

## Publication boundary

`planning/domains/` is research and authorship input. P10 runtime code must not import its Markdown or
draft JSON. A later plan must name a deterministic compiler/publisher that consumes ratified catalogue
records and emits versioned runtime `TemplateFragment`, `TemplateDefinition`, and
`TemplateApplicability` records with provenance and validation reports.

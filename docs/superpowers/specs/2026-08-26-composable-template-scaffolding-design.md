# Composable Template Scaffolding Design

Date: 2026-08-26  
Status: planning clarification for P10; no runtime implementation

## Goal and authority

This design makes the template layer explicit without changing the product mission. The product first
helps the user recognise and approve the few major areas of their corpus, then helps them refine each
area only as far as the evidence and their retrieval needs justify. A template is a reusable recipe for
that refinement. It is not a prebuilt folder tree, a domain classifier, or an authority that can create
folders by itself.

Authority remains, in order:

1. `planning/00-database-agent-product-design.md`, especially §5.1–§5.12 and §8.8;
2. ratified resolutions and the P10 SPEC;
3. this clarification for the composable-template seam;
4. later domain and prompt content, which must conform to these contracts.

This design does not implement P10, author domain content, write prompts, or choose numeric defaults.

## North-star user experience

The user should never be asked to design a complete taxonomy before receiving value. The interaction
is progressive and reversible:

1. P10 proposes a shallow top-level scaffold from accepted P9 groups, active P6 domain memberships,
   existing curated folders, and the user's own labels.
2. The user accepts, renames, merges, moves, removes, or creates those major branches.
3. The accepted scaffold may be saved while some branches remain intentionally shallow or unrefined.
4. The user opens one branch. P10 shows applicable template recipes and reusable fragments, why each
   applies, and what each would create from the branch's actual facts.
5. The user may apply all, some, or none of a recipe; reorder, rename, flatten, or extend its levels;
   and combine compatible fragments.
6. P10 previews counts, representative items, unresolved items, privacy effects, warnings, and the
   structural diff before the change is accepted.
7. The same loop can continue inside any child branch. Different branches may stop at different
   depths. “Not refined yet” and “shallow by design” are both valid states.
8. Freeze makes only the approved nodes legal destinations. Later refinement opens a new draft plan
   version; it never mutates the frozen version or the underlying facts and groups.

Completeness means every included node is legal, explainable, and explicitly approved or deferred. It
does not mean every branch has the same depth or that every available template dimension was used.

## Research basis

The architecture follows four stable findings:

- [W3C SKOS](https://www.w3.org/TR/skos-reference/) separates concepts, concept schemes, ordered
  collections, and mappings between schemes. That supports stable reusable semantic parts without
  forcing one universal hierarchy or one label set.
- [Dublin Core application-profile guidance](https://www.dublincore.org/specifications/dublin-core/application-profile-guidelines/)
  shows how application-specific profiles can select and constrain terms from shared vocabularies
  while preserving their source identities. That is the model for binding reusable template roles to
  live P6 fields instead of duplicating facts.
- [W3C SHACL](https://www.w3.org/TR/shacl/) distinguishes reusable constraint modules from the data
  they validate and produces explicit validation results without mutating the inputs. P10 follows the
  same principle: composition is validated, reported, and kept inert until approval.
- Research on incremental formalisation and information architecture supports starting with a small
  provisional structure, refining it over time, previewing real consequences, and allowing irregular
  depth rather than demanding a complete symmetric taxonomy. Relevant sources include
  [Shipman and Marshall](https://people.engr.tamu.edu/shipman/formality-paper/harmful.html),
  [Microsoft Research on breadth and depth](https://www.microsoft.com/en-us/research/?p=331895), and
  [W3C's accessible tree-view pattern](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/).

These sources inform the architecture; they do not override the original product design.

## The four distinct objects

P10 must not collapse these objects into a single “template” row.

### 1. Template fragment

A `TemplateFragment` is a small reusable organization recipe such as subject → lifecycle stage →
artifact kind, counterpart → cycle → document kind, or event → capture time. It defines semantic
dimension roles, recommended relative order, optionality, metadata-only roles, safety constraints,
and its own identity/version. It contains no user values and creates no nodes.

Fragments are useful because one stable organization pattern can recur across domains. For example,
“project → stage → artifact kind” can help organize a research project, a client engagement, a
software project, or a creative production without claiming those domains share all facts or labels.

### 2. Template definition

A `TemplateDefinition` is the exact P10 record name for a versioned recipe composed from one or more fragment references plus any
template-local dimensions and constraints. It describes a useful default ordering, not a mandatory
tree. Built-in, LLM-generated, and user-authored templates share this shape. `origin_kind` records
that origin, `scope_kind` separately records domain/cross-domain/purpose/personal scope, and
`publication_state` records draft/published/retired lifecycle.

A definition may be:

- domain-focused, when its evidence and terminology belong to one domain;
- cross-domain, when the same semantic recipe has valid bindings in several domains;
- purpose-focused, when a coherent packet spans document types or domains;
- personal, when the user saves an approved composition for later reuse.

### 3. Template applicability binding

A `TemplateApplicability` record connects a template version to one fact schema in one authored
context. It is the join row in the many-to-many routing seam and contains:

- exactly one `uses_schema`, corresponding to one active schema/domain context carried into P10 from
  P6/P9, preserving the catalogue's one-schema-per-binding allow-list rule;
- an optional purpose-packet context shared with other applicability records;
- the facts/signals required to consider the template;
- a binding from each semantic dimension role to existing P6 field references for that context;
- exclusions and privacy constraints;
- provenance and version.

Domains do not own templates. A domain may have several applicability rows; one template definition
may be referenced by applicability rows for several domains; a mixed-domain branch may combine
compatible fragments through several rows. Every individual row still resolves against one schema,
so reuse never turns the P6 fact allow-list into a cross-domain union by accident. Applicability only
makes a recipe eligible to preview. It never activates the recipe.

### 4. Branch template binding

A `BranchTemplateBinding` records what one branch in one draft plan actually chose:

- branch and plan-version identity;
- exact selected applicability IDs/versions and the template/fragment versions they resolve;
- resolved role-to-P6-field bindings;
- selected, omitted, reordered, flattened, renamed, or added dimensions;
- groups and evidence that justified the choice;
- validation report and user approval action;
- workflow state: `draft`, `reviewed`, or `approved`;
- depth disposition: `refined`, `shallow-by-choice`, or `refine-later`, plus a required reason.

Every materialized node points to this `binding_id` and records the exact template and optional
fragment version that supplied its semantic role. The node also records the resolved P6 field
separately. Destination profiles carry `domains[]` plus the binding rather than forcing a mixed
purpose branch to invent one primary domain.

This is branch-local. Applying or changing a template in one branch cannot silently change another
branch, even when both originated from the same reusable definition. A later library version is a new
candidate, never an automatic migration. The same is true of a newer applicability version: its role
mapping or privacy policy cannot alter a recorded branch until a new draft explicitly adopts it.

## Many-to-many routing

The routing sequence is deterministic and evidence-bound:

```text
accepted scaffold branch
  -> branch context (groups, domains, facts, existing folders, purpose, privacy)
  -> eligible applicability bindings
  -> candidate template/fragment compositions
  -> semantic validation against actual branch evidence
  -> live structural preview
  -> user selection/edit/approval
  -> branch-local binding in the draft plan
```

Rules:

1. Top-level branches are derived before template routing. A template cannot silently create a new
   high-level domain or replace the user's vocabulary.
2. Domain is one applicability signal, not a one-template ownership key.
3. Purpose may cross domains. An accepted purpose packet may remain flat, use one cross-domain
   recipe, or combine compatible fragments; heterogeneity alone is never a rejection reason.
4. Exact template reuse is allowed when the same definition has independently valid applicability
   bindings in several domains. Fragment reuse is preferred when only part of a recipe transfers.
5. A branch can use multiple templates only through an explicit composition whose order and conflicts
   validate. P10 never concatenates two hierarchies silently.
6. Missing domain bindings, field mappings, constraints, or privacy rules produce
   `ConfigurationRequired` or a review-only proposal. No generic fallback is invented.
7. The router returns a small explained candidate set, not every superficially matching template.
   Candidate ceilings and ranking weights remain injected configuration.

An optional purpose applicability uses a versioned authored `purpose_profile_ref`. That identifier is
neither P6's Applications-only `purpose` field nor a runtime P9 group ID and creates no universal
purpose taxonomy. The branch binding separately pins the actual accepted P9 group IDs; C3 requires
their evidence to satisfy the profile, binding by binding, without unioning schemas.

## Composition and validation

The existing P10 V1–V6 checks remain authoritative for the materialized candidate tree. Composition
adds gates before those checks:

| Gate | Requirement |
|---|---|
| C1 identity | Every referenced template, fragment, applicability binding, and version exists. |
| C2 live fields | Every resolved dimension maps to a P6 field; template roles never become facts. |
| C3 applicability | The branch's accepted groups/facts satisfy the selected binding; domain name alone is insufficient. |
| C4 unambiguous binding | A required role resolves once; competing mappings are surfaced as a conflict, not picked silently. |
| C5 coherent order | Combined relative-order constraints are acyclic and produce one explicit preview order. |
| C6 coverage | Composition does not silently lose groups/files; unresolved items remain visible. |
| C7 privacy | The combined sensitivity policy is no weaker than any included fragment or P7 restriction. |
| C8 activation | A valid preview remains inert until the branch-specific user approval is recorded. |

After C1–C8, P10 materializes the candidate against the branch's real values and runs V1–V6. A
syntax-valid or model-approved template can therefore still abstain, fail validation, or remain a
proposal.

Conflict handling is fail-closed and explanatory. The report names the fragments, role/order/policy
that conflict, affected items, and available user choices: omit one fragment, change the order,
flatten a level, keep the branch shallow, or defer. There is no hidden precedence rule.

## Domain and prompt work

The concurrent domain research and prompt folders supply authored content later; they do not define
the runtime architecture. The current R1 domain-node contract remains closed while that swarm is
running: each `kind: template` row keeps exactly one `uses_schema`, and agents must not add fragment
or cross-domain keys to its JSON.

The later template-building/synthesis pass may author:

- applicability bindings from semantic roles to live P6 fields;
- evidence requirements, exclusions, aliases, examples, and privacy constraints;
- domain-focused complete templates and reusable fragments;
- evaluation fixtures that show both correct use and abstention.

The compiler treats each ratified domain `kind: template` row as an applicability source, not proof
that the organizational recipe is owned by that schema. It extracts or links shared definitions and
fragments, then emits separate one-schema `TemplateApplicability` records. The same definition or
fragment may therefore be referenced by several bindings without copying it into each domain package.
A domain can have several bindings. A cross-domain purpose packet composes bindings from several
domains while each binding retains its own schema boundary.

Prompt work may teach P8 to propose a candidate `TemplateDefinition` or composition using only the
published schema and bounded dossier. Prompt text cannot supply missing fields, bindings, domain
truth, thresholds, consent, or activation. P10 owns semantic validation and the user owns approval.

`planning/domains/` remains a research/authorship surface, not a runtime import target. Later build
plans must name the compilation/publishing step that turns ratified content into versioned runtime
records; P10 must never read research Markdown or node drafts directly.

## Required preview and interaction data

For the top-level scaffold and every branch refinement, the UI contract must expose:

- current branch path and the compact whole-tree context;
- branch workflow state plus the persisted depth disposition `refined`, `shallow-by-choice`, or
  `refine-later` and its reason;
- candidate source/version, applicability reason, assumptions, and conflicting alternatives;
- proposed child count, descendant count, member count, representative examples, unresolved items,
  evidence gaps, and protected-item summary;
- the selected/omitted/reordered/flattened fragments and dimensions;
- a before/after structural diff and the effect on visible ancestors and siblings;
- explicit stale/loading state while counts recompute;
- semantic undo/redo for the current draft and durable plan-version history.

Aliases and alternate views point to canonical node/item identities and do not duplicate counts or
facts. Existing folders remain visually and structurally distinct from proposed nodes.

## Failure cases this contract forbids

- one monolithic tree template per domain;
- one universal template forced across all domains;
- copying the same fragment into several domain packages until the copies drift;
- selecting a template from a domain label without checking branch evidence;
- forcing a cross-domain purpose packet into one domain to satisfy a schema;
- auto-applying library updates to existing branches;
- completing or padding shallow branches to make the tree symmetrical;
- treating an unrefined branch as invalid or blocking a useful scaffold;
- hiding dropped or unresolved files in a “successful” preview;
- letting the LLM invent a field, binding, value, domain, constraint, or destination;
- activating a valid candidate without branch-specific user approval;
- letting a branch-local edit silently alter another branch;
- importing `planning/domains/` or prompt content into P10 runtime code.

## Acceptance criteria for the later P10 build

1. One template version can be bound to two domains through two one-schema applicability records
   without duplicating the definition, and each binding resolves to valid P6 fields.
2. One domain can offer two structurally different templates with explained applicability.
3. One mixed-domain purpose packet can combine two compatible fragments and preserve every member.
4. An incompatible composition returns a deterministic report and creates no nodes.
5. The user can approve only the top-level scaffold, keep one branch shallow, and refine another to
   several levels; freeze accepts the legal partial-depth design.
6. Applying a template to one branch cannot alter another branch using the same definition.
7. A new template/fragment version does not migrate an approved branch automatically.
   A new applicability version is equally inert until a new draft adopts it.
8. Every preview recomputes counts and shows examples, unresolved items, privacy effects, and a diff
   before approval.
9. Required missing knowledge fails closed without invented defaults.
10. Facts, groups, original files, and prior frozen plan versions remain unchanged through all edits.

## Non-goals

- authoring the full 200–300 template library;
- choosing the final domain taxonomy or prompt wording;
- making folder trees the only retrieval view;
- automatic template activation or automatic post-freeze migration;
- implementing P10, P11, P12, or P13 in this planning pass.

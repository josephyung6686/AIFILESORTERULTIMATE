# P10 plan gap audit

Date: 2026-08-27
Scope: `planning/parts/P10-tree-design-freeze/PLAN.md` (186 lines) against
`planning/parts/P10-tree-design-freeze/SPEC.md` (964 lines), the two `docs/superpowers/`
composable-template documents, `planning/domains/TEMPLATE-BUILDING-HANDOFF.md`,
`planning/30-p8-p9-connection-contract.md`, and the live `src/` APIs.

Every quotation below was confirmed by `grep -n` before it was written. Where a string could not
be found, the row says so instead of paraphrasing.

---

## 0. The headline, before the tables

`planning/parts/P10-tree-design-freeze/PLAN.md` is **not a plan in this project's sense**. It is a
186-line prose restatement of the SPEC's chapter titles. Measured against
`planning/parts/P9-grouping/PLAN.md`, the stated quality bar:

| Measure | P9 PLAN.md | P10 PLAN.md |
|---|---|---|
| `^```python` blocks | 17 | **0** |
| `Step [0-9]` occurrences | 75 | **0** |
| `^**Files:**` blocks | 15 | 0 (inline `**Files:**` only) |
| `**Produces:**` / `**Consumes:**` blocks | 13 / 4 | **0 / 0** |
| `Done-means` references | 0 in P9's own text, but a 13-row `## Requirement coverage map` at :1043 | **0**; a 6-row `## Coverage` at :179 |
| `## Required execution order` | present at :56 | **absent** |
| checkbox steps | 75 | 51 |

`planning/parts/_PLAN-AUTHORING-BRIEF.md:42-53` states the format every task needs:

```
- `**Files:**` — exact create / modify / test paths
- `**Interfaces:**` — `Consumes:` and `Produces:` with exact signatures
- `**Done-means:**` — which numbered Done-means items this task satisfies
- Numbered `- [ ] **Step N: ...**` steps, each 2–5 minutes
- **Complete runnable test code** in a fenced `python` block
```

and `:54-56`: **"NO PLACEHOLDERS, EVER.** No stubs, no ellipses, no 'similar to Task N', no 'add
appropriate error handling'." P10's PLAN satisfies none of the seven bullets. Its 51 checkboxes are
each one sentence of restated requirement — e.g. `:129` "Implement live counts before commit: child
count, member count, examples, unresolved files, evidence gaps, sensitive isolation, and
accepted-group coverage." — which is `SPEC.md:635-637` with the verbs changed.

Note: `docs/superpowers/plans/2026-08-25-p10-tree-design-freeze.md` is **byte-identical** to
`planning/parts/P10-tree-design-freeze/PLAN.md` (verified by `diff`). There is one plan, stored twice.

---

## A. SPEC-to-PLAN coverage

117 requirement rows. **38 MISSING** (37 distinct defects; A103 restates A19), **36 PARTIAL**,
**43 COVERED**.

### A.1 Contract in (SPEC:76-164)

| # | SPEC requirement | PLAN task | Verdict |
|---|---|---|---|
| A1 | `:84` `group_id`, user-approved `label` | `:114` "accepted P9 groups" | PARTIAL — no field names; live P9 has `Group.display_label` (`src/grouping/records.py:159`) and `GroupAcceptance.user_edited_label` (`:354`), **no `label`** |
| A2 | `:85` `group_category` | none — `grep -c group_category PLAN.md` → **0** | **MISSING** |
| A3 | `:86` `members[]` with `membership_kind ∈ {direct-anchor, context-supported, user-attached}` | none — `grep -c membership_kind` → **0** | **MISSING** — live P9 names it `Membership.basis` (`src/grouping/records.py:222`) over `MEMBERSHIP_BASES` (`src/grouping/vocabulary.py:55`) |
| A4 | `:87` `anchor_facts[]` | `:65` "representative/rich-anchor evidence" | PARTIAL |
| A5 | `:96-99` a `user-attached` member must not be presented as evidence-derived in an `explanation` | none | **MISSING** |
| A6 | `:103-105` derived `excluded_members[]` from `Membership.decision = excluded` | `:65` "exclusions" | PARTIAL |
| A7 | `:106-107` derived `rejected_proposals[]` from `Group.state = rejected` | `:114` "rejected groups cannot resurface" | PARTIAL — and the SPEC's stated derivation is **impossible against the live API**: `src/grouping/records.py:180` runs `check(self.state, GROUP_STATES, ...)` and `GROUP_STATES` (`src/grouping/vocabulary.py:27-29`) is `(candidate, supported, tentative-discovery, unresolved)`. `src/grouping/vocabulary.py:20` says outright: "`accepted` and `rejected` are resolved as of a plan version from `group_acceptance` and are **never stored on a group**." |
| A8 | `:109-110` a file may belong to more than one accepted group | `:122`, `:157` "accepted group multi-home" | COVERED |
| A9 | `:113-117` P6 facts, six reliability states, normalisation/aliases, no new field | `:95` "live P6 field" | PARTIAL — reliability states and §2.8 aliases have no carrier |
| A10 | `:119-126` P3: candidate roots, cross-root movement permission, exclusion decisions, existing-folder inventory with counts and directory position, curated-vs-incidental computed by P3 | `:114` "curated existing folders" only | **MISSING** — no P3 seam, no roots, no `cross_folder_moves` |
| A11 | `:128-134` P7 handling class **and** the four §8.4 operation-mode literals "spelled P7's way: `offline`, `local_model`, `hybrid`, `cloud_assisted`" | `:9` tech-stack mention only; Task 1's enum list `:52` omits both | **MISSING** |
| A12 | `:136-143` P10 supplies the §5.7 dossier contents and the template JSON schema | `:22` G-P8 "P10 supplies the schema and dossier contents" | PARTIAL — see §C.2; zero mentions of `DossierRequest`, `allowed_vocabulary`, `TemplateDependencies`, `SiteDependencies`, `E_TEMPLATE` |
| A13 | `:152-155` P1 append-only event log; durable plan-version and node records | `:53` "Add append-only SQLite tables" (P10's own) | **MISSING** — no P1 event append anywhere |
| A14 | `:157-164` P13 `review_action` carrying `surface = canvas \| plan_version`, `subject_ref`, `plan_version`, `action` incl. `adopt_version`/`restore_version`, `correction_scope`, `presented_state_ref` | `:23`, `:139`, `:141` | PARTIAL — adopt/restore covered at `:141`; `surface`, `correction_scope`, `presented_state_ref` absent |

### A.2 Contract out — P2 stage output (SPEC:170-202, 787-788)

| # | SPEC requirement | PLAN task | Verdict |
|---|---|---|---|
| A15 | `:175-177` the two `stage_id`s | `:149` | COVERED |
| A16 | `:181` `inputs[]` — the `subject_ref`s of the `grouping` and `factual_validation` stage outputs consumed | none — `grep -c "inputs\[\]"` → **0** | **MISSING** — and `record_stage_output` (`src/eval_harness/stage_output.py:96-100`) takes `inputs: Sequence[str]` as a **required** keyword. Following the plan literally produces a `TypeError`. |
| A17 | `:185-195` outcome mapping including `not_implemented`, paired with `budget_state` | `:149` "Map produced/abstained/deferred/error distinctly" | PARTIAL — `not_implemented` and `budget_state` absent; `budget_state` is also a **required** keyword at `src/eval_harness/stage_output.py:99` |
| A18 | `:197-202` a ceiling-truncated pass is `deferred`+`ceiling_reached`, **never** `abstained` | `:149` | PARTIAL — the pairing rule is not stated; it is enforced at `src/eval_harness/stage_output.py:103-110` |
| A19 | `:787-788` (DM10) P2 scores **tree quality and template quality** | none | **MISSING** — the `template` and `tree` dimensions exist at `src/eval_harness/vocabulary.py:39-40`; the plan never emits a `DimensionValue` |

### A.3 Contract out §1 — the node record (SPEC:204-302)

| # | SPEC requirement | PLAN task | Verdict |
|---|---|---|---|
| A20 | `:210-231` the 22 mandatory node fields | `:52` names enums only | **MISSING** — the field list has no carrier. Grep count in PLAN.md: `node_id` 0, `plan_version_id` 0, `display_label` 0, `parent_node_id` 0, `root_anchor` 0, `ordinal` 0, `associated_group_ids` 0, `template_context` 0, `dimension_role` 0, `expected_values` 0, `explanation` 3 (generic), `handling_class` 0 |
| A21 | `:214` `node_type` five values | `:52` "five node types" | COVERED |
| A22 | `:227` `node_role` four values | `:52` "four node roles" | COVERED |
| A23 | `:228` `disposition` three values | `:52`, `:107` | COVERED |
| A24 | `:230-231` `refinement_disposition` + `refinement_reason` | `:117-118` | COVERED |
| A25 | `:233-240` `accepts_placement` derivation, incl. `protected` → true only under explicit policy | `:63` | COVERED |
| A26 | `:242-243` renaming rewrites `display_label` only | `:141` | PARTIAL |
| A27 | `:245-254` P10 holds no path strings; what it publishes is `root_anchor` + the ancestor label chain | `:25`, `:52`, `:150`, `:162` | PARTIAL — the prohibition is covered; **`root_anchor` is never named** (`:25` says only "node IDs and label ancestry") |
| A28 | `:256-261` the five fields P11 consumes rather than re-derives | `accepts_placement` ✓ `:63`; `disposition` ✓ `:107`; `node_role`/`expected_values`/`handling_class` → 0 hits | PARTIAL |
| A29 | `:263-266` `node_role` is the single vocabulary | `:52` | COVERED |
| A30 | `:268-270` uneven depth legal by construction | `:115`, `:132`, `:148`, `:159` | COVERED |

### A.4 Contract out §2 — the destination profile (SPEC:304-338)

| # | SPEC requirement | PLAN task | Verdict |
|---|---|---|---|
| A31 | `:322-334` the 12 profile fields | `:65` | PARTIAL |
| A32 | `:330` `anchor_excerpts[]`, "each excerpt cited by **`observation_key`**" | none — `grep -c observation_key` → **0** | **MISSING** |
| A33 | `:331` `known_document_types[]` | none — 0 hits | **MISSING** |
| A34 | `:336-338` "Protected profiles are redacted at the boundary, not at the renderer" | none — `grep -ci redact` → **0** | **MISSING** |
| A35 | `:325` `domains[]` plural on a purpose branch | `:66` | COVERED |

### A.5 Contract out §3 — the template schema (SPEC:340-520)

| # | SPEC requirement | PLAN task | Verdict |
|---|---|---|---|
| A36 | `:350-358` four distinct records | `:51`, `:74-77` | COVERED |
| A37 | `:360-363` only an approved branch-local binding creates nodes; exact versions pinned | `:94`, `:98` | COVERED |
| A38 | `:367-438` the four JSON schemas | `:74-77` | PARTIAL — no carrier for `detection_signal_refs`, `optional_branch_patterns`, `validation_constraints`, `example_label_chains`, `retrieval_rationale` (all 0 hits in PLAN) |
| A39 | `:442-444` every `allowed_fields` entry and `field_ref` resolves to a P6 field; a template may not mint a field | `:95` | COVERED |
| A40 | `:445-448` many-to-many join rows, one `uses_schema` each, reuse by ID/version never copied JSON | `:93`, `:163` | COVERED |
| A41 | `:449-453` `purpose_profile_ref` is authored/versioned, is not a P6 field, is not a P9 `group_id`; C3 proves applicability from actual accepted groups; "never unions the rows' schema allow-lists" | none — `grep -c purpose_profile_ref` → **0** in PLAN (2 in SPEC) | **MISSING** |
| A42 | `:454-456` acyclic fragment imports; intersection; conflict is reported, not last-writer-wins | `:78-81` | COVERED |
| A43 | `:457-458` `metadata_only: true` means the role may never become a folder level | none — 0 hits | **MISSING** |
| A44 | `:459-460` order is a recommendation | `:120` | COVERED |
| A45 | `:461-464` "Values are never invented" | `:121` | PARTIAL |
| A46 | `:465-467` `retrieval_rationale` in the definition; `justification_fact_refs` in the report/binding, "never in the immutable reusable definition" | none — 0 hits | **MISSING** |
| A47 | `:468-470` `example_label_chains` "are not path strings, do not contain separators, and cannot be resolved or emitted as destinations" | none — 0 hits | **MISSING** — this is the one place a label chain could leak into a path and there is no guard |
| A48 | `:472-479` the ordering doctrine: parent provides context; project/subject before time; **photos are the explicit exception** | none — `grep -ci photo` → **0**, `subject-before-time` → 0 | **MISSING** |
| A49 | `:481-494` P10 runs all six V1–V6 | `:82-84` | COVERED |
| A50 | `:496-497` P10's V1–V6 have no relation to P1's separately numbered V1–V4 | none | **MISSING** — a live name collision left unflagged |
| A51 | `:499-505` C1–C8 precede V1–V6; failure returns a deterministic report and creates no nodes | `:94`, `:95` | PARTIAL — the eight gates are never individually named or given a fixture (see A106) |
| A52 | `:507-512` validity is not activation | `:86` | COVERED |
| A53 | `:514-520` purpose packets are not a template failure; flat / nested / split-by-institution / hybrid all supported; no check rejects for heterogeneity alone | `:118-119` | PARTIAL — the four handling options are absent |

### A.6 Contract out §4 — the freeze record (SPEC:522-580)

| # | SPEC requirement | PLAN task | Verdict |
|---|---|---|---|
| A54 | `:527-538` the ten freeze-record rows (plan ID/version/time, tree, node classification, template versions and ordering choices, group memberships by reference, **user labels and aliases**, **residual-library configuration**, privacy policies by reference, **placement policy settings**, review decisions by reference) | `:148` validates nodes only | **MISSING** — freeze-record *contents* are never enumerated |
| A55 | `:542-545` shared-material policy captured at freeze: "a shared branch, a primary-home convention, a reference or alias convention, or mandatory review" | `:52` lists "shared-material policies" as an enum; `:157` a fixture | PARTIAL — the four values are never enumerated and no task writes the policy at freeze. `planning/parts/P11-placement-residual/PLAN.md:60` already requires it: "no frozen plan, stale version, missing profile, or **missing shared-material policy** fails closed." |
| A56 | `:546-548` scoped fallback; "A global catch-all folder should not become the product's default answer to ambiguity" | `:132` | PARTIAL — no guard against a global catch-all |
| A57 | `:550-552` freeze records no facts or evidence | `:141` | COVERED |
| A58 | `:554-558` legality is ID membership; not-in-set → P11 abstains | `:64`, `:150` | COVERED |
| A59 | `:560-564` a useful shallow scaffold is freezeable | `:148` | COVERED |
| A60 | `:566-571` frozen version immutable; edit opens a draft with a diff; P11 computes the file-level consequence; adoption explicit; earlier versions restorable | `:139-141` | COVERED |
| A61 | `:573-580` the user may create a folder after freeze; routed to P10; P11 mints no node | `:139` "create custom residual branch" | PARTIAL — the general post-freeze user-created node is narrower in the plan than in the SPEC |
| A62 | `:537` + `:894` cross-root movement permission recorded by P10 at freeze | none — `grep -c cross_folder` → **0** in both SPEC and PLAN; `grep -c "cross-root"` → 0 in PLAN | **MISSING** — the field is **live** at `src/scan_agent/selection.py:22,31,43,60,116` as `cross_folder_moves`, and `planning/parts/P12-apply-undo/SPEC.md:154-156` says "P3 records it and **P10 stores it**; P12 is where it is enforced" |

### A.7 Contract out §5 — canvas data contracts (SPEC:582-640)

| # | SPEC requirement | PLAN task | Verdict |
|---|---|---|---|
| A63 | `:587-591` the eight branch-candidate card fields; explanation "rather than a technical confidence score" | `:121`, `:158` | PARTIAL — the no-score rule is covered; the field list is not |
| A64 | `:593-597` candidates are derived; the nine §5.1 names "are illustrative and must not be shipped as a fixed set" | none — `grep -ci "fixed set"` → 0, `illustrative` → 0 | **MISSING** — this is the guard that stops P10 shipping a universal taxonomy, and it has no test |
| A65 | `:599-601` the full action set | `:139` carries 10 of them | PARTIAL — `accept`, `move under an existing root`, `defer`, `create manually`, `drag an accepted group into a branch`, `delete a suggested area` absent |
| A66 | `:603-606` protected areas: no sensitive filenames, no cloud by default; §8.4's five configurable redaction axes | `:107`, `:122`, `:157` | PARTIAL — the redaction axes (names, previews, thumbnails, OCR text, location data) are absent |
| A67 | `:608-614` existing folders: six actions, curated/incidental, the §5.10 hard prohibition, visual distinctness | `:114`, `:122`, `:158` | PARTIAL — the six actions and the prohibition guard are absent (see A99) |
| A68 | `:616-622` vertical pass | `:116-120` | COVERED |
| A69 | `:624-628` live feedback **and the whole-option preview** — "Option A would create three schools, five terms, and twelve course branches" | `:129-130` | PARTIAL — the whole-option comparison is absent |
| A70 | `:630-633` four warnings **plus** a flattening recommendation "when a dimension does not materially improve retrieval" | `:131` | PARTIAL — the flattening recommendation is absent |
| A71 | `:635-640` six tree-health measures + the "good enough structural gist" framing constraint | `:129`, `:132` | PARTIAL |

### A.8 Contract out §6 — the residual library (SPEC:642-736)

| # | SPEC requirement | PLAN task | Verdict |
|---|---|---|---|
| A72 | `:656-667` the eight slots | `:105` | COVERED |
| A73 | `:669-683` the nine names; only the first four have a stated default parent, "the remaining five have none stated and none is invented here" | `:105`, `:157` | PARTIAL — the plan never records that five defaults must stay unset |
| A74 | `:685-689` user-defined residual areas supported; the product ships none of the eight examples | `:139` "create custom residual branch" | PARTIAL |
| A75 | `:691-695` Unsupported-or-Encrypted "represent without moving"; Protected Records local-only and never in model prompts | `:107` "protected/unsupported behavior" | PARTIAL |
| A76 | `:697-701` `default_parent_location` is a `display_label` chain, not a path | `:106` | COVERED |
| A77 | `:703-717` the six enablement actions; **each is a `destination-tree edit` event and a §8.7 learning record at node scope**; enablement is plan-version state | `:106` (actions only) | PARTIAL — the event and learning record are absent |
| A78 | `:719-729` three dispositions and their P11/P12 consequences | `:107` | COVERED |
| A79 | `:731-736` disabled → no node; enabled → ordinary legality path | `:150`, `:157` | COVERED |

### A.9 Cross-cutting (SPEC:812-907)

| # | SPEC requirement | PLAN task | Verdict |
|---|---|---|---|
| A80 | `:816-823` P10 appends `template application` and `destination-tree edit`; the 14 named actions; each event carries acting user, time, node ID, before/after state, evidence ref; an LLM-generated template additionally carries model version and prompt fingerprint | none — `grep -c "template application"` → **0**, `"destination-tree edit"` → **0**, `"prompt fingerprint"` → **0** | **MISSING** — both names are **already reserved** at `src/database_agent/events.py:33-34`. A P10 that appends neither leaves two §8.2 event names with no producer |
| A81 | `:824-825` freeze appends a plan-version adoption record | none | **MISSING** |
| A82 | `:827-832` supersession retains the predecessor and the reason; a rejected branch candidate keeps the evidence that produced it | `:56`, `:140` | PARTIAL |
| A83 | `:836-841` the ceiling P10 owns (`Maximum folder proposals and maximum depth`); shared model ceilings enforced by P8; feedback/health involve no model call | none — `grep -ci budget` → **0** | **MISSING** |
| A84 | `:847-849` template budget exhausted → branch marked `template-deferred`, stays in review, no cheaper substitute | none — `grep -c template-deferred` → **0** | **MISSING** |
| A85 | `:850-852` proposal/depth ceiling → surplus shown as deferred, never silently dropped | none | **MISSING** |
| A86 | `:853-856` freeze is never auto-completed | `:148` | COVERED |
| A87 | `:857-858` an over-budget dossier is summarised/split/deferred, "never silent truncation" | none | **MISSING** |
| A88 | `:862-866` the five §8.7 actions this stage produces plus six more P10 records | none — `grep -ci learning` → **0** | **MISSING** |
| A89 | `:868-877` scope explicit on every record, one of six; the five characteristic scopes | none | **MISSING** — the six-value vocabulary is live at `src/database_agent/events.py:99` as `CORRECTION_SCOPES` |
| A90 | `:879-886` negative feedback stored; **"Before proposing a branch candidate, P10 queries P1 `learning_records` for `proposal_class = branch` and `basis_key = (parent_node_id, dimension_or_label)`"** | `:114` "rejected groups cannot resurface" | **MISSING** — no query, no keys. The callable is live: `database_agent.learning.learning_records(conn, scope, subject_id)` at `src/database_agent/learning.py:46-47` |
| A91 | `:890-894` the seven things belonging to the plan version | `:55` | PARTIAL |
| A92 | `:896-899` what belongs to the shared evidence database | `:56`, `:141` | COVERED |
| A93 | `:901-907` versioning behaviour; bindings pin all three exact version pairs | `:98`, `:139-141` | COVERED |

### A.10 Done-means (SPEC:751-810)

| # | Done-means | PLAN task | Verdict |
|---|---|---|---|
| A94 | DM1 `:753-756` | `:51-56` | COVERED |
| A95 | DM2 `:757-771` fixtures (a)–(e) | `:157` | PARTIAL — 2(a)'s stated *reason* (B8(b): two nodes so §6.10's `margin_over_next` has a value) and 2(e)'s six-state residual fixture are compressed to the phrase "residual library fixtures" |
| A96 | DM3 `:772-774` | `:64` | COVERED |
| A97 | DM4 `:775-776` | `:141` | COVERED |
| A98 | DM5 `:777-778` | `:132`, `:158` | COVERED |
| A99 | DM6 `:779-780` "**No code path** renames, flattens, re-parents or reorganises an `existing` node without an explicit user action recorded as such" | none | **MISSING** — `:158` asserts only that existing structure "is visibly distinct"; the §5.10 prohibition has no test |
| A100 | DM7 `:781` | `:115`, `:159` | COVERED |
| A101 | DM8 `:782-783` | `:86` | COVERED |
| A102 | DM9 `:784-786` | `:131` | COVERED |
| A103 | DM10 `:787-788` | none | **MISSING** (same defect as A19) |
| A104 | DM11 `:789-791` | `:150`, `:162` | COVERED |
| A105 | DM12 `:792-795` | `:150` | COVERED |
| A106 | DM13 `:796-797` "**C1–C8 are independently falsifiable.** One failing fixture per composition gate" | `:157` lists "deterministic conflict" — **one**, singular | **MISSING** — eight required fixtures, one planned |
| A107 | DM14 `:798-800` | `:93` | COVERED |
| A108 | DM15 `:801-804` | `:93` | PARTIAL — the authored/versioned purpose profile bound through C3 is absent (A41) |
| A109 | DM16 `:805-807` | `:96-98` | COVERED |
| A110 | DM17 `:808-810` | `:148`, `:159` | COVERED |

### A.11 Open questions (SPEC:909-964)

The PLAN has **zero** occurrences of "open question", "OQ", or any of the five unresolved
questions. `planning/parts/P9-grouping/PLAN.md:1061-1070` shows the required treatment
("`## Explicitly unresolved after this plan`", ending "These are dependency gates, not invitations
to invent defaults."). P10's `## Explicitly deferred` (`:173-175`) covers *authored content* only.

| # | Open question | Verdict |
|---|---|---|
| A111 | OQ1 `:922-924` depth limit unset; "Check V3 cannot be implemented until it is set" | PARTIAL — `:24` G-KNOWLEDGE covers thresholds generically; `:83` schedules V3 as if buildable |
| A112 | OQ2 `:925-927` §5.9 thresholds | COVERED at `:131` |
| A113 | OQ3 `:928-932` is `protected` a node type or an orthogonal flag — "**Affects P11 directly**" | **MISSING** |
| A114 | OQ5 `:940-943` node identity across plan versions — "**Affects P11 and P12**" | **MISSING** — and `:140` plans a node-level diff that cannot be specified without the answer |
| A115 | OQ8 `:951-953` is the scoped `General` auto-proposed or opt-in per parent | **MISSING** |
| A116 | OQ9 `:954-956` is the shared-material policy tree-global or per-branch — "**Affects P11's abstention behaviour**" | **MISSING** |
| A117 | OQ10 `:957-959` default redaction settings for protected branches | **MISSING** |

---

## B. Composable / nested template research absorption

### B.1 What IS absorbed

Absorbed into **both** SPEC and PLAN:

- The four distinct objects. Design doc `:71` "P10 must not collapse these objects into a single
  'template' row" → SPEC `:350` "The schema is composable, not domain-owned. Four records stay
  distinct:" → PLAN `:74-77`.
- The three separate axes. Design `:88-90` "`origin_kind` records that origin, `scope_kind`
  separately records domain/cross-domain/purpose/personal scope, and `publication_state` records
  draft/published/retired lifecycle" → SPEC `:382-384` → PLAN `:76-77` "Split `origin_kind`,
  `scope_kind`, and `publication_state`".
- One `uses_schema` per applicability row. Handoff `:16-17` "The current domain catalogue
  intentionally requires every `kind: template` row to name exactly one `uses_schema`. Keep that
  rule." → SPEC `:446-447` → PLAN `:93`.
- C1–C8 before V1–V6. Design `:179-193` → SPEC `:499-505` → PLAN `:94-95`.
- Branch-local isolation and no automatic migration. Design `:136-139` → SPEC `:805-807` →
  PLAN `:96-98`, `:161`.
- The publication boundary. Handoff `:126-127` "`planning/domains/` is research and authorship
  input. P10 runtime code must not import its Markdown or draft JSON." → PLAN `:162`, `:164`. Note:
  the SPEC has **zero** occurrences of "planning/domains" — this concept lives in the PLAN only.
- All 13 forbidden failure cases (design `:250-262`) have a carrier somewhere in SPEC or PLAN.

### B.2 Concepts with NO carrier in the SPEC **or** the PLAN — 13

| # | Research concept | Exact source | SPEC | PLAN | Consequence |
|---|---|---|---|---|---|
| B1 | The research basis itself — SKOS / Dublin Core / SHACL / incremental formalisation | design `:50-65` | `grep -c SKOS` → 0 | 0 | Low severity: the *principles* survive as C1–C8. The citations do not, so no later reader can check the derivation |
| B2 | The three concrete reuse patterns — "project → stage → artifact kind", "counterpart → cycle → document kind", "event → capture time" | design `:75-77`, `:80-82`; handoff `:61-64` | `grep -ci counterpart` → 0; `lifecycle stage` → 0 | 0 | The only fragment the SPEC names is `artifact-kind` (`SPEC:369`). Nothing seeds the reuse inventory |
| B3 | **Applicability provenance** | handoff `:92` "provenance back to ratified domain rows and research evidence"; design `:110` "provenance and version" | the `TemplateApplicability` JSON at `SPEC:402-418` has **no provenance key** (`grep -n provenance SPEC.md` → only `:374` inside the *fragment* JSON, and `:814` the §8.2 heading) | `:67`, `:95` mention "provenance" for nodes/roles, not for applicability rows | A compiled applicability row cannot be traced back to the domain row that justified it |
| B4 | The closed action set for `resolved_dimensions` — "selected, omitted, reordered, flattened, **renamed, or added** dimensions" | design `:124` | `SPEC:429` shows one example value, `"action": "selected"`, and never enumerates | `:96` has four of six | Two legal user edits (`renamed`, `added`) have no representable value |
| B5 | Candidate-set bounding — "The router returns a small explained candidate set, not every superficially matching template. Candidate ceilings and ranking weights remain injected configuration." | design `:169-170` | `grep -ci "candidate ceiling"` → 0; `ranking` → 0 | 0 | PLAN `:94` says "bounded candidate compositions" with no bound source. Nothing stops the router returning every match |
| B6 | The five conflict-resolution user choices — "omit one fragment, change the order, flatten a level, keep the branch shallow, or defer" | design `:198-199` | `:504-505` requires only "a deterministic report naming the conflicting inputs" | `:95` "create no nodes on conflict" | A conflict report with no offered actions is a dead end |
| B7 | **Descendant count** in every preview | design `:239` "proposed child count, descendant count, member count…" | `grep -c "descendant count"` → 0 | 0 | The SPEC's live-feedback list (`:624-628`) has child count and member count but no subtree total |
| B8 | Semantic **redo** | design `:243` "semantic undo/redo for the current draft" | `grep -ci undo` → **0** in the whole SPEC | `:140` "semantic undo labels" only | Redo has no carrier anywhere |
| B9 | A published **role vocabulary** artifact | handoff `:51-55` "Normalize semantic roles… Roles are not P6 facts"; library plan `:45` `planning/templates/role-vocabulary.json` | `SPEC:444` states the *principle*; no vocabulary artifact | `grep -ci "role vocabulary"` → 0; Task 1's enum list `:52` omits it | `role_ref` appears 4× in the SPEC and 0× in the PLAN; nothing publishes the legal role names |
| B10 | The reuse-judgment vocabulary — `share-definition`, `share-fragment`, `keep-separate`, `insufficient-evidence` | handoff `:84-85`; library plan `:84-85` | 0 | 0 | Delegated to the library plan. Acceptable **only** if P10 records why a fragment exists; it does not |
| B11 | The two-context rule — "Create a fragment only when at least two reviewed contexts share stable semantics and compatible constraints" | handoff `:71-72` | 0 | 0 | Delegated to library plan Task 2 (`:87`). No P10 validation rejects a one-context fragment |
| B12 | **Site E's fragment boundary** — "it may reference published fragments by exact ID/version… but **it cannot publish or propose a new canonical fragment**" | handoff `:117-120` | 0 | 0 | See §C.3. This is the load-bearing gap |
| B13 | "Repeated local dimensions become fragment candidates **only in the later human-reviewed synthesis pass**" | handoff `:120-121` | 0 | 0 | Nothing stops an implementer promoting a repeated dimension to a fragment automatically |

### B.3 Concepts in exactly one of SPEC / PLAN — 4 more

| Concept | Source | In SPEC | In PLAN |
|---|---|---|---|
| Workflow state `draft \| reviewed \| approved` | design `:128` | **no** — `SPEC:432` shows only `"state": "approved"` and never enumerates | yes, `:118` |
| Explicit stale/loading state during recompute | design `:242` | **no** — `grep -ci stale` → 0 | yes, `:130` |
| "Aliases and alternate views point to canonical node/item identities and do not duplicate counts or facts" | design `:245-246` | **no** — `grep -ci "canonical node"` → 0 | yes, `:132` |
| A named deterministic compiler/publisher | handoff `:127-129`; design `:226-228` | **no** — `grep -ci compiler` → 0, `compilation` → 0 in SPEC | half: `:175` "a named later compilation step" — but it **names nothing**, and the PLAN's File structure (`:29-45`) omits `src/tree_design/catalogue.py`, which `docs/superpowers/plans/2026-08-26-composable-template-library.md:51,143,152` requires P10 to own |

---

## C. Upstream / downstream seams

### C.1 What P10 must receive from P9 — and the state of P9

P9 is **partially built**. `ls src/grouping` → `config.py, embeddings.py, fixtures.py, records.py,
retrieval.py, schema.py, seeds.py, vocabulary.py`. Absent: `store.py`, `acceptance.py`, `graph.py`,
`dossier.py`, `p8_seam.py`, `learning.py`, `stage_output.py`, `failure_points.py`, `pipeline.py`.
There is **no read surface for accepted groups yet**.

P10's PLAN names the seam once, at `:21`: "**G-P9:** deterministic fixtures may drive Tasks 1–9;
accepted P9 groups and labels are required before a production freeze." It names **no module, no
callable, no record**. Compare `planning/parts/P9-grouping/PLAN.md:34-46`, a seven-row
"current-state ledger" giving live evidence and plan treatment per prerequisite, and `:41` which
cites the exact P6 read surfaces by name.

Three field-name mismatches the plan does not reconcile:

| P10 SPEC says | Live P9 API | Evidence |
|---|---|---|
| `label` (`SPEC:84`) | `Group.display_label`, and the user-approved form is `GroupAcceptance.user_edited_label` | `src/grouping/records.py:159`, `:354` |
| `membership_kind` (`SPEC:86`) | `Membership.basis` over `MEMBERSHIP_BASES` | `src/grouping/records.py:222`; `src/grouping/vocabulary.py:51-55` |
| `Group.state = rejected` (`SPEC:106-107`) | impossible — `Group.state` is checked against `GROUP_STATES` only; rejection is `GroupAcceptance.acceptance` resolved per plan version | `src/grouping/records.py:180`; `src/grouping/vocabulary.py:20`, `:27-35`, `:186` |

Also: `Group.display_label` and `group_category` are `None` unless `coherence_verdict == COHERENT`
(`src/grouping/records.py:205-211`). P10 `:114` builds horizontal candidates from "accepted P9
groups, active P6 domains" with no handling for a coherent-but-uncategorised group.

### C.2 What P10 must receive from P8 — Site E

`SPEC:136-143` makes P10 the supplier of the template dossier and the response schema. The live
Site E surface is:

- `validate_template_response(dossier, response_bytes, *, evidence_resolver, contradicts,
  dependencies: TemplateDependencies | None, model_id, prompt_fingerprint, dossier_builder,
  release_audit_id)` — `src/llm_harness/template_validation.py:153-164`
- `TemplateDependencies(schema_validator: Callable[[object], bool])` — `:25-27`. **P10 supplies
  this callable.** Omitting it returns `ValidationUnavailable(missing=("schema_validator",))`
  (`:165-166`, asserted at `tests/p8/test_p8_template_validation.py:115-129`).
- `SiteDependencies(fact=None, placement=None, residual=None, template=…)` —
  `src/llm_harness/sites.py:80-87`.
- `Dossier.allowed_vocabulary: tuple[str, ...]` — `src/llm_harness/records.py:335`. Site E rejects
  any proposed dimension whose `name` is outside it (`template_validation.py:101-111`, asserted at
  `tests/p8/test_p8_template_validation.py:103-112`). **P10 populates that closure.**
- Site E also requires a citation per proposed dimension (`:112-121`,
  `tests/p8/test_p8_template_validation.py:92-100`) and downgrades a level with no
  `retrieval_justification` to `WEAK`/`UNRESOLVED` (`:122-135`).

P10's PLAN mentions **none** of these names. Grep counts in `PLAN.md`: `allowed_vocabulary` 0,
`DossierRequest` 0, `TemplateDependencies` 0, `SiteDependencies` 0, `E_TEMPLATE` 0, `P8Verdict` 0,
`ValidationUnavailable` 0, `schema_validator` 0, `Site E` 0. The only P8 reference is `:22`
"template-generation model calls use only P8's frozen `run_call`".

### C.3 The `fragment` grep — the prior audit's claim is confirmed and is worse than stated

```
$ grep -rn "fragment" src/
src/facts/session.py:34:path fragment inside a value, which is §3.14's mistake one layer down. The canonical
```

**One hit in the entire source tree, and it is about filesystem path fragments, not template
fragments.** `grep -rn fragment planning/parts/P8-llm-harness-validator/ planning/parts/P9-grouping/`
returns nothing either.

So: the composable-template fragment concept exists in `docs/superpowers/specs/2026-08-26-…`,
`planning/domains/TEMPLATE-BUILDING-HANDOFF.md`, `planning/parts/P10-tree-design-freeze/SPEC.md`
and `PLAN.md` — and **nowhere in shipped code or shipped tests**. Handoff `:117-120` — "It may
reference published fragments by exact ID/version… but it cannot publish or propose a new canonical
fragment" — is enforced by nothing. `src/llm_harness/template_validation.py` checks schema validity,
vocabulary closure, per-dimension citation and per-level justification; it has **no notion of a
fragment**, so a model response that proposes a new canonical fragment passes Site E unremarked.

`docs/superpowers/plans/2026-08-26-composable-template-library.md:170-173` assigns the boundary to
**that plan's** Task 7 ("Freeze Site E: a custom proposal may reference published fragments by
exact ID/version…"), i.e. to a pass gated behind `G-DOMAINS` and `G-P10`. P10's own PLAN does not
name it. Net effect: the boundary is owned by a plan that cannot start until P10 finishes, and P10
does not carry it forward. **It is currently owned by nobody who can act.**

### C.4 What P10 must hand downstream

**To P11** — `planning/parts/P11-placement-residual/SPEC.md:119-128` names 12 node fields plus the
five B6 fields in bold. P10's PLAN names 3 of the 12 (`accepts_placement` `:63-64`, `disposition`
`:107`, `existing_path` `:52`). `P11 SPEC:102` also requires the **§6.1 destination profile** and
the **shared-material policy selection** from P10, and `planning/parts/P11-placement-residual/PLAN.md:60`
already tests for "missing shared-material policy fails closed" — a P10 output with no producing task.

**To P12** — `planning/parts/P12-apply-undo/SPEC.md:136-156` names `node_id, node_type,
display_label, parent_node_id, root_anchor, existing_path, accepts_placement, node_role,
disposition, handling_class`, plus the shared-material policy and, explicitly, "the **cross-folder
movement permission** — §1.1's 'whether files may move across high-level folders', recorded by P3 as
`cross_folder_moves` and stored by P10 at freeze under Placement policy settings… **P3 records it and
P10 stores it**". `cross_folder_moves` is live at `src/scan_agent/selection.py:22`. P10's PLAN and
SPEC both contain **zero** occurrences of `cross_folder`.

**To P13** — the back-edge. `SPEC:157-164`; PLAN `:23` uses "recorded review-action fixtures". P13's
three event names are already registered at `src/database_agent/events.py:59-61` ("review
presentation", "review action routed", "apply review approval"). P10's plan defines no receiver
signature — compare `planning/parts/P9-grouping/PLAN.md:772`, which publishes
`apply_review_action(conn, action) -> tuple[str, ...]` and names the fixture file.

**To P2** — `record_stage_output` (`src/eval_harness/stage_output.py:96-100`) requires `inputs` and
`budget_state` as keyword arguments; the plan supplies neither (A16, A17).

**To P1** — `"template application"` and `"destination-tree edit"` are reserved at
`src/database_agent/events.py:33-34` and have no producer. P10's PLAN adds none (A80).

---

## D. Ordering

**The PLAN states no task ordering and no gates.** There is no `## Required execution order`
section; `grep -n "before Task"` returns nothing. The five gates at `:21-26` are *dependency*
gates on other parts, not *intra-plan* ordering. Compare `planning/parts/P9-grouping/PLAN.md:56-58`:
"Execute Tasks 1–8, then **Task 9 before Task 10**. Task 10 is a hard dependency gate: it must not
begin until Task 9's `record_context_review_pending` is green…"

Two concrete ordering defects visible in the file as written:

1. **Task 2 writes `src/tree_design/freeze.py` (`:61`) before Task 9 defines what freeze is
   (`:146`).** Task 2 puts `legal_destination_ids(frozen_tree)` into `freeze.py`; Task 9 then adds
   freeze validation to the same module. Either `legal_destination_ids` belongs in `store.py` or
   Task 9 must precede Task 2 for that symbol.
2. **Task 8 names `src/tree_design/diff.py` (`:137`), which is absent from the File structure block
   (`:29-45`).** The block lists twelve modules; `diff.py` is not one of them. `catalogue.py`
   — required by `docs/superpowers/plans/2026-08-26-composable-template-library.md:51,143,152` —
   is also absent, as are `__init__.py` and any config module.

### Proposed ordering, derived from the data dependencies in the SPEC

```
1  vocabulary + records + schema           (SPEC:210-231, 350-438, 656-667, 719-729)
     └ gate: every closed vocabulary in §E below is published as named constant + tuple,
       both, per _PLAN-AUTHORING-BRIEF.md:232-234. Nothing else may spell one.
2  P1 event + learning adapters            (SPEC:816-825, 879-886)
     └ MUST precede 6 and 8: SPEC:882-885 requires a learning_records query *before* a branch
       candidate is proposed, and SPEC:820-821 requires every draft-altering action to append
       an event. Building candidates first produces an unrecorded proposal path.
3  upstream read adapters (P9 groups, P6 fields, P3 folders/roots, P7 class+mode)
     └ MUST precede 4, 5, 6: C2 (SPEC:500) resolves roles to live P6 fields; horizontal
       candidates (SPEC:47) read P9 groups + P3 folders; V5 (SPEC:493) reads P7.
     └ gate: reconcile the three P9 name mismatches in §C.1 before any fixture is authored.
4  templates: fragment/definition/applicability/binding schemas + V1–V6
     └ V3 gated on OQ1 (SPEC:922-924): it raises ConfigurationRequired until a depth limit exists.
5  routing: C1–C8 + branch-local binding   (SPEC:499-505)
     └ MUST precede 6: SPEC:499 "Composition gates precede V1–V6"; a candidate cannot be
       previewed before its composition validates.
6  residual library                        (SPEC:642-736)
     └ MUST precede 9: SPEC:66-67 "P10 cannot freeze a *complete* tree without the library
       that produces those nodes."
7  horizontal then vertical candidates     (SPEC:47, 49)
     └ SPEC:616 "one branch at a time" — the horizontal pass MUST complete before any
       vertical recipe activates (design doc :158 "Top-level branches are derived before
       template routing").
8  health + warnings                       (SPEC:624-640)
     └ depends on 7 for counts; thresholds injected, per OQ2.
9  edits, diffs, plan-version supersession (SPEC:566-571, 888-907)
     └ depends on 2 for the event append and on 1 for supersession columns.
10 freeze + P2 stage output                (SPEC:522-580, 170-202)
     └ depends on 6 (residual nodes), 9 (versions), 3 (P3 cross_folder_moves for the
       placement-policy row at SPEC:537).
11 fixtures for P11 + no-invention guards  (SPEC:757-771, 789-791)
12 final verification
```

---

## E. Closed vocabularies P10 must publish

P9 puts all of these in one `src/grouping/vocabulary.py`; the required publication form is
`_PLAN-AUTHORING-BRIEF.md:232-234`: "**Task 1 publishes the six states BOTH ways: `STATES:
tuple[str, ...]` for iteration and membership, AND one named constant per state… Every other module
imports the NAMED CONSTANT.** Never a bare string, never an index." `src/grouping/vocabulary.py:22-35`
is the live precedent.

P10's PLAN `:52` asks for six of the sets below ("five node types, four node roles, three residual
dispositions, shared-material policies, template dimensions, and P10 stage outcomes"). The complete
list is **32**.

### P10 owns and must define

| # | Vocabulary | Values | SPEC line |
|---|---|---|---|
| E1 | `node_type` | `existing` \| `proposed` \| `user-created` \| `protected` \| `ignored` | `:214` (quoted from §5.12 at `:206-207`) |
| E2 | `node_role` | `ordinary` \| `scoped-general` \| `residual` \| `shared-material` | `:227` |
| E3 | `disposition` (residual only) | `physical-destination` \| `review-only` \| `leave-in-place` | `:228`; table `:723-727` |
| E4 | `refinement_disposition` | `refined` \| `shallow-by-choice` \| `refine-later` | `:230` |
| E5 | `origin_kind` | `built-in` \| `llm-generated` \| `user-authored` | `:382` |
| E6 | `scope_kind` | `domain-focused` \| `cross-domain` \| `purpose-focused` \| `personal` | `:383` |
| E7 | `publication_state` | `draft` \| `published` \| `retired` | `:384` |
| E8 | dimension `requirement` | `required` \| `optional` | `:390` |
| E9 | `BranchTemplateBinding.state` | `approved` is the only value the SPEC shows (`:432`). The closed set `draft \| reviewed \| approved` is in `docs/…scaffolding-design.md:128` and `PLAN.md:118` — **the SPEC never enumerates it** | `:432` / design `:128` |
| E10 | `resolved_dimensions[].action` | `selected` is the only value the SPEC shows (`:429`). The closed set `selected \| omitted \| reordered \| flattened \| renamed \| added` is in design `:124`; `PLAN:96` carries four of six — **the SPEC never enumerates it** | `:429` / design `:124` |
| E11 | composition gates | `C1` identity \| `C2` live fields \| `C3` applicability \| `C4` unambiguous binding \| `C5` coherent order \| `C6` coverage \| `C7` privacy \| `C8` activation | `:499-505` (gate names from design `:184-191`) |
| E12 | validation checks | `V1` repeated parent dimension \| `V2` meaningless one-child level \| `V3` exceeds practical depth \| `V4` author/organization as collector \| `V5` exposes protected information \| `V6` empty branches | `:488-494` |
| E13 | residual template names (nine, fixed) | `Temporary Screenshots` \| `One-Off Images` \| `Reference Clips` \| `Independent Records` \| `Receipts and Confirmations` \| `Reading Inbox` \| `Review Later` \| `Unsupported or Encrypted` \| `Protected Records` | `:675-683` |
| E14 | residual attribute slots (eight) | `display_name` \| `default_parent_location` \| `accepted_evidence_patterns[]` \| `expected_file_types[]` \| `sensitivity_restrictions` \| `optional_shallow_subfolders[]` \| `max_permitted_depth` \| `treatment` | `:660-667` |
| E15 | residual `treatment` | `reviewed` \| `retained` \| `merely kept searchable` | `:667` |
| E16 | residual enablement actions (six) | `enable` \| `disable` \| `rename` \| `relocate` \| `merge` \| `replace with an existing folder` | `:708-713` |
| E17 | shared-material policy | `a shared branch` \| `a primary-home convention` \| `a reference or alias convention` \| `mandatory review` | `:542-544` |
| E18 | branch-candidate actions | `accept` \| `rename` \| `merge into another branch` \| `move under an existing root` \| `defer` \| `create manually`; plus `add` \| `remove` \| `rename` \| `merge` \| `split` \| `nest` \| `reorder` \| `ignore`; plus `drag an accepted group into a branch` \| `delete a suggested area` | `:599-601` |
| E19 | existing-folder actions (six) | `preserve` \| `adopt as a branch` \| `merge with a proposal` \| `attach a proposed branch beneath it` \| `rename the proposal to match it` \| `leave it untouched` | `:610-611` |
| E20 | `destination-tree edit` action set (14, for the §8.2 event) | `accept` \| `rename` \| `merge` \| `split` \| `nest` \| `re-parent` \| `reorder` \| `ignore` \| `delete` \| `create-manually` \| `adopt-existing` \| `enable/disable residual branch` \| `add scoped General` \| `set shared-material policy` | `:818-821` |
| E21 | node-diff kinds (seven) | `added` \| `removed` \| `renamed` \| `re-parented` \| `re-templated` \| `re-ordered` \| `type-changed` | `:568-569` |
| E22 | §5.9 warning kinds | `a level producing only one child` \| `a level repeating a concept already expressed in the parent` \| `excessive depth` \| `a large number of tiny folders`; plus a `flattening recommendation` | `:630-632` |
| E23 | events P10 appends | `template application` \| `destination-tree edit`; plus a plan-version adoption record at freeze | `:816-817`, `:824` — both live at `src/database_agent/events.py:33-34` |
| E24 | `ConfigurationRequired` / review outcome names | named only in `PLAN:24`; **the SPEC defines no such vocabulary** — needs a ruling | PLAN `:24` |

### Vocabularies P10 carries verbatim from another part (must be imported, never re-spelled)

| # | Vocabulary | Values | SPEC line | Live owner |
|---|---|---|---|---|
| E25 | `membership_kind` (P9) | `direct-anchor` \| `context-supported` \| `user-attached` | `:86` | `src/grouping/vocabulary.py:51-55` as `MEMBERSHIP_BASES`; the field is `Membership.basis` |
| E26 | P7 operation mode | `offline` \| `local_model` \| `hybrid` \| `cloud_assisted` — `:132-133` "P7 owns that vocabulary — *'a value outside this set is a load error, not a fallback'* — so P10 carries the literals verbatim and coins no display variants" | `:131-133` | P7 |
| E27 | P7 handling class | `Public or low sensitivity` … `Unreadable or unclassified` | `:130` | P7 |
| E28 | P2 `stage_id` (P10's two) | `template_generation` \| `tree_design` | `:175-177` | `src/eval_harness/vocabulary.py:25-26` |
| E29 | P2 `outcome` | `produced` \| `abstained` \| `deferred` \| `not_implemented` \| `error` | `:185-186` | `src/eval_harness/vocabulary.py:52` |
| E30 | P2 `budget_state` | `within_ceiling` \| `ceiling_reached` | `:186` | `src/eval_harness/vocabulary.py:53` |
| E31 | §8.7 correction scope | `file` \| `group` \| `node` \| `template` \| `domain` \| `corpus` | `:868` | `src/database_agent/events.py:99` as `CORRECTION_SCOPES` |
| E32 | P13 `surface` | `canvas` \| `plan_version` | `:159` | P13 (unbuilt) |

Also carried, not a closed set but a two-value signal: **curated / incidental** per existing folder,
computed by P3 (`:124-126`, resolution G9), rendered by P10.

---

## F. The three most serious gaps

**F1 — P10 has no provenance layer at all, so two reserved §8.2 event names would ship with no
producer.** `SPEC:816-825` is explicit that every draft-altering canvas action appends
`destination-tree edit` and every template application appends `template application`, each carrying
acting user, time, node ID, before/after state and evidence reference, with an LLM template adding
model version and prompt fingerprint. Both names are already reserved at
`src/database_agent/events.py:33-34`. `PLAN.md` contains zero occurrences of either string, zero of
"prompt fingerprint", zero of "learning", and no task appends a P1 event. The same absence takes
down `SPEC:879-886`'s no-resurfacing rule — "Before proposing a branch candidate, P10 queries P1
`learning_records` for `proposal_class = branch` and `basis_key = (parent_node_id,
dimension_or_label)`" — which `PLAN:114` compresses to five words, "rejected groups cannot
resurface", with no query and no keys. `database_agent.learning.learning_records(conn, scope,
subject_id)` is live at `src/database_agent/learning.py:46-47`. This is the project's own
"column with no writer" defect class, in its most expensive form: a whole cross-cutting section.

**F2 — the seams to P9, P8, P11, P12 and P2 are named as parts, never as symbols, and three of the
names the SPEC does give are wrong against the live code.** `PLAN:21-26` lists five gates and no
signatures; grep counts in the plan are `allowed_vocabulary` 0, `DossierRequest` 0,
`TemplateDependencies` 0, `SiteDependencies` 0, `E_TEMPLATE` 0, `group_category` 0, `membership_kind`
0, `observation_key` 0, `handling_class` 0, `node_role` 0, `expected_values` 0, `root_anchor` 0,
`cross_folder` 0. Meanwhile `record_stage_output` requires `inputs` and `budget_state`
(`src/eval_harness/stage_output.py:96-100`) and the plan supplies neither; `validate_template_response`
requires a `TemplateDependencies.schema_validator` from P10
(`src/llm_harness/template_validation.py:165-166`) and the plan never mentions it; P12's SPEC states
that P10 stores `cross_folder_moves` at freeze (`planning/parts/P12-apply-undo/SPEC.md:154-156`) and
neither the P10 SPEC nor PLAN contains the string. On top of that the P10 SPEC's own P9 contract-in
names `label`, `membership_kind` and `Group.state = rejected`, none of which exists in
`src/grouping/` — the third is *structurally impossible*, since `src/grouping/vocabulary.py:20`
states that `rejected` is "never stored on a group". A plan executed as written produces a part that
cannot be called by its neighbours.

**F3 — the composable-fragment layer is a paper concept: `grep -rn "fragment" src/` returns exactly
one hit, and it is about filesystem paths.** `src/facts/session.py:34` is the only match in the
entire source tree. Nothing in `src/llm_harness/template_validation.py` knows what a fragment is, so
handoff `:117-120`'s boundary — Site E "cannot publish or propose a new canonical fragment" — is
enforced nowhere, exactly as the prior audit claimed. Worse, it is *assigned* nowhere reachable:
`docs/superpowers/plans/2026-08-26-composable-template-library.md:170-173` puts it in a plan gated
behind `G-P10` (`:26`), i.e. behind the P10 build that does not carry it. Around that hole sit
twelve more unabsorbed research concepts (§B.2), of which the load-bearing ones are the missing
**applicability provenance** (the `TemplateApplicability` JSON at `SPEC:402-418` has no provenance
key, though handoff `:92` and design `:110` both require one), the missing **candidate ceiling and
ranking configuration** (design `:169-170`), and the missing **role vocabulary artifact** — `role_ref`
appears 4× in the SPEC and 0× in the PLAN, so nothing publishes the legal semantic role names that
C2 and C4 are supposed to resolve.

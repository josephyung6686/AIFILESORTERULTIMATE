# 46 — Novel-domain handling: the three layers, the widening contract, and what placement does with a label

Date: 2026-08-27
Status: design requirement. Executable. Supersedes `planning/43-ROLE-VOCABULARY-AND-RECUT.md` §9 (see §0.2).
Scope: **design only.** No `src/`, `tests/` or `planning/domains/` change is made here.

Authority order used throughout: `planning/00-database-agent-product-design.md` (canonical, wins on
conflict) → `planning/domains/TEMPLATE-BUILDING-HANDOFF.md` → `planning/parts/P10-*/SPEC.md`,
`planning/parts/P11-*/SPEC.md` → live `src/`. Section numbers (§) index the sectioned mirror
`planning/01-product-design-structured.md`; every quoted string was checked by exact substring
against `00` before being written here. The re-verification script is §13.

---

## 0. What this document settles

The owner's ruling, verbatim: *"do 2 and 3, we need residual but also we need to widen vocab and also
the domains are supposed to encapsulate everything."*

Three layers, all of them, in a fixed order. §3 is the decision procedure. §4 is the widening
contract. §8 is the residual floor. §9 is how layer 2 and layer 3 feed layer 1 over time, which is
the only way "domains encapsulate everything" is ever actually reached.

### 0.1 The one-sentence answer

A group that matches no template gets a **template-local level** — a folder level with a semantic
role, an evidence citation and a display label, but **no P6 field, no `expected_values`, and no
automatic placement**; its children come from accepted P9 groups rather than from fact values; and
whatever still does not fit falls to §7's residual stage, counted and visible.

### 0.2 How this supersedes 43 §9

43 §9 requires `allowed_vocabulary` to carry *"the canonical roles plus template-local dimension
names"*. That is wrong in three separate ways and is withdrawn:

1. **Wrong container.** `allowed_vocabulary` is one field on one `Dossier` record shared by five call
   sites, and it holds a different kind of thing at each (`planning/45-ROLE-GROWTH-PROJECTION.md`
   §5.2, verified below in §1.3). Putting role names in it globally would offer them as placement
   destinations at Site C and as target node ids at Site D.
2. **Wrong widening.** Site E's closure is P10's, and P10's own docstring
   (`planning/parts/P10-tree-design-freeze/PLAN.md:5548`) forbids widening it, for a reason that is
   correct: it is a P6 allow-list at the dossier boundary.
3. **Wrong layer.** Even if Site E accepted the name, the level would die at C2
   (`PLAN.md:2530`, `PLAN.md:8009`), which refuses any *selected* dimension whose `field_ref` is not
   a live destination-eligible P6 field. 43 §9 never reaches the wall that actually binds.

This document keeps `allowed_vocabulary_for` **exactly as P10 planned it** and widens somewhere else
— see §4.

---

## 1. The verified finding chain

Everything in this section was read out of the named file, not recalled.

### 1.1 The gate, live

`src/llm_harness/template_validation.py:101-103`:

```python
    vocab = set(dossier.allowed_vocabulary)
    dimensions = _dimensions(payload)
    if any(item.get("name") not in vocab for item in dimensions):
```

`_dimensions` (`:83-88`) reads `payload["dimensions"]`; each item's `name` must be in the closure or
the **whole proposal** is `REJECT` / `REJECTED` with `may_propose=False`.

### 1.2 The closure P10 plans to supply

`planning/parts/P10-tree-design-freeze/PLAN.md:5548`:

> ```python
> def allowed_vocabulary_for(catalogue: TemplateCatalogue, *,
>                            uses_schema: str) -> tuple[str, ...]:
>     """The closure P8's Site E checks every proposed dimension name against.
>
>     It is the union of the allowed fields of the rows for ONE schema. Unioning
>     across schemas here would widen a P6 allow-list at the dossier boundary,
>     which is the one thing the one-row-one-schema rule exists to prevent.
>     """
> ```

and its test at `PLAN.md:5117`, `test_the_allowed_vocabulary_is_the_rows_fields_and_nothing_wider`.

### 1.3 There are four `allowed_vocabulary` gates, not one

Confirmed by `grep -rn "allowed_vocabulary" src/`:

| Site | Code | Members are |
|---|---|---|
| B group | `src/llm_harness/group_validation.py:132` | fact **values** |
| C placement | `src/llm_harness/placement_validation.py:208` | destination **node ids** and dimension values |
| D residual | `src/llm_harness/placement_validation.py:324` | target **node ids** |
| **E template** | `src/llm_harness/template_validation.py:101` | dimension **names** |

Any change must be stated per site. This document changes **Site E only**.

### 1.4 The corpus fact

`planning/domains/roster.json` declares **23 schemas**. Counting `fields` on the 23 `kind: schema`
node files under `planning/domains/nodes/`:

```text
academic 5 · code 4 · college_applications 5 · finance 5 · photos 6 · research 6
business_operations 0 · career 0 · clinical_practice 0 · construction_property 0 · creative 0
engineering 0 · government 0 · hr 0 · identity 0 · law_practice 0 · legal 0 · logistics 0
manufacturing 0 · medical 0 · nonprofit 0 · resource_operations 0 · retail_hospitality 0
```

**6 of 23 carry fields; 17 declare zero.** For those 17, `allowed_vocabulary_for` returns `()`,
`any(name not in set())` is true for any non-empty dimension list, and **every** proposal is
rejected. §5.7's custom-template path is not narrow for 17 of 23 domains — it is **closed**.

Live P6 is narrower still and consistent with this: `src/facts/domains.py` names ten `SCHEMA_IDS`
and derives `FIELD_LESS_SCHEMA_IDS` for the four with no field rows, and its own docstring records
that **"This module reads `planning/domains/` never."** The catalogue and P6 are two separate
vocabularies; the 17 is a statement about the catalogue that P10 will compile from.

### 1.5 The wall nobody had reached: C2

`PLAN.md:2530`:

> ```python
> def resolve_role_to_field(conn, *, role_ref: str, field_ref: str) -> str:
>     """C2: an organization-layer role resolves to a LIVE, destination-eligible
>     P6 field, or the composition fails closed.
> ```

and it is called **again at node-build time**, `PLAN.md:8009`, with the comment:

> `# C2 again, at the point of USE. ... a candidate reaching here with a field P6 does not define`
> `# would produce an empty level and a silently missing folder rather than a refusal`

P10 SPEC:500 states it as a gate: *"C2 resolves every selected role to a live P6 field."*

**Consequence.** Widening Site E alone buys nothing. A template-local dimension would pass Site E,
pass P10's schema validator, and then raise `UpstreamUnavailable` at composition — a spent model
call and an opaque upstream error, which is strictly worse than a clean rejection.

### 1.6 Two more live facts that decide the design

**(a) The P10 node record already admits a level with no field.** SPEC:224-226:

| `dimension_role` | *"the organization-layer semantic role this level realises, **if any**; never a fact key"* |
| `dimension` | *"the live P6 field to which `dimension_role` resolved for this branch, **if any**"* |
| `expected_values[]` | *"`field = value` this level asserts"* |

Both carry **"if any"**. `dimension = null` is already expressible, already published, and already in
P11's Contract-in (P11 SPEC:124). **No new field is needed to declare a template-local level.**

**(b) P10 already plans to accept template-local dimensions — inconsistently.** `PLAN.md:5055`:

```python
def test_template_local_dimensions_are_allowed_and_are_not_fragments():
    """A local dimension is the model saying "this branch also splits by lens".
    That is a proposal about ONE branch. It becomes a canonical fragment only in
    the later human-reviewed synthesis pass, never here."""
```

It passes because `_dimensions_are_well_formed` (`PLAN.md:5401`) checks each `name` against the
**payload's own** `allowed_fields`, which the test appends `"lens"` to. So the same proposal is
**accepted** by P10's schema validator and **rejected** by P8's Site E gate, whose closure is the
catalogue's fields and does not contain `lens`. That contradiction is live in the plan today; §11
resolves it.

**(c) The live Site-E fixture already treats the closure as dimension names, not field keys.**
`src/llm_harness/fixtures.py:592`: `_E_VOCAB = ("year", "event")`. §5.4's Photos **template**
dimensions are `year → event`; §3.11's Photos **fields** are `capture year, event`.
`allowed_vocabulary_for` would return `("capture_year", "event")` (`PLAN.md:5121`). P10's plan
therefore also **changes the meaning** of a field the harness already ships fixtures for.

---

## 2. The attack on "a folder dimension is not a P6 fact"

Instruction was to attack it. Result: **the argument survives as a statement about naming and about
the P6 boundary. It fails as stated about levels, and it is silent on the two things that actually
decide the mechanism.** Point by point.

### 2.1 It survives on the P6 boundary — traced, not assumed

`planning/domains/TEMPLATE-BUILDING-HANDOFF.md`: *"Roles are not P6 facts."* And §3.14, canonical:

> *"Facts remain separate from the future destination tree. A fact such as `subject = BUSIB 4300`
> does not itself dictate one permanent folder path."*

Traced in code. Nothing at Site E can write a P6 fact:

- Fact proposals are validated by a **different function** with a **different allow-list**:
  `src/llm_harness/fact_validation.py:204`, `if proposal.field_key not in allowlist:` →
  `FIELD_NOT_IN_ACTIVE_SCHEMA`. That allowlist is built from the file's activated schemas, not from
  the Site-E dossier.
- `Dossier.call_site` is constrained by `ELIGIBILITY_BY_SITE`
  (`src/llm_harness/vocabulary.py:150`); Site E's only eligibility is
  `accepted_group_fits_no_existing_template` (`:137`). A Site-E dossier cannot be presented at Site A.
- Site E's verdict carries `may_propose`, and the only consumer of `may_propose` outside the
  validators is `src/grouping/p8_seam.py:330` — P9's grouping seam. No fact writer reads it.

So widening Site E's closure **cannot** widen a P6 allow-list. The mechanism is two disjoint
allow-lists at two disjoint call sites. **This half of the argument is sound and is the reason the
widening is safe.**

### 2.2 It fails as stated about *levels* — C2 is the real boundary

"Nothing new becomes assertable, something new becomes organizable" is the claim. The second half is
false under the plan as written. C2 (§1.5) refuses to *select* a dimension without a live
destination-eligible P6 field, at routing and again at node build. Under today's plan a
template-local dimension can be **named**, **justified** and **metadata-only**, but it can never
**become a folder level**. Nothing new becomes organizable.

**The widening must therefore be two-sited: Site E's name gate AND C2's field requirement.** Anyone
who changes only the first has shipped a bug that costs a model call to discover.

C2 is also carrying two separate duties, and only one of them may be relaxed:

- *"A template may not mint a field (§3.12)"* — this is the P6 boundary and it is **kept in full**.
- *"which P6 marks not destination-eligible. §3.8 keeps an authoring role out of the tree"* — this
  is §3.8's collector-folder rule. When C2 stops running for a level, §3.8 loses its guard. **V4 —
  *"uses an author or organization merely as a collector"* (P10 SPEC:492, §5.7) — becomes
  load-bearing for template-local levels and must have its own failing fixture for one.**

### 2.3 The argument is silent on where a template-local level's *children* come from — and that is fatal unless answered

`PLAN.md:8009-8025` builds a level by reading each member's value for `dimension.field_ref`
(`preferred_value_for(conn, file_id=..., field_ref=...)`). **With `field_ref = null` there is nothing
to read.** The level materialises zero children, which V6 — *"produces empty branches when tested
against the accepted group"* — correctly kills. A naive widening therefore produces no nodes anyway.

The answer is in §5.4, canonical, and it is the pivot of this whole design:

> *"The system does not invent PHYS1401, UChicago, Spring 2026, or PVA/RDP; those names emerge from
> **validated facts, user-confirmed groups, and accepted labels**. The template simply determines how
> those real values could be arranged as branches."*

Three named sources, not one. A fact-backed level uses the first. **A template-local level may use
only the second and the third**: one child per accepted P9 group, labelled by §5.7's
*"user-approved group label"*, or one child adopted from an existing folder's own name (§5.10).

This is not a workaround. It is the same sentence the design already uses to forbid invented values,
read for its other two clauses.

### 2.4 The argument is silent on placement — §5 answers it, and the answer constrains §4

Covered in full in §5. The short version: the partition in §2.3 is *also* the only thing placement
can match against, so the two constraints converge on one rule instead of fighting.

### 2.5 Verdict

Accept the argument's **naming/authority** half without qualification. Reject its **"becomes
organizable"** half as under-specified, and replace it with:

> A template-local dimension is an **organizing label over an accepted-group partition**. It asserts
> nothing about any file. It never becomes a P6 field, never appears in `expected_values`, never
> produces a `values` row, and never yields an automatic placement. It buys exactly one thing: the
> user sees a *proposed shape* for material from a domain nobody researched, at review time, instead
> of seeing nothing.

---

## 3. The three layers and the decision procedure

Given an accepted P9 group `G` that is about to be given a branch design.

### Layer 1 — Schema (the goal: "domains encapsulate everything")

**Fires when** at least one published `TemplateApplicability` row matches: its `uses_schema` is
active on `G`'s members (§3.11 activation), C3 proves applicability from `G`'s accepted groups and
facts rather than the domain label alone (P10 SPEC:501), and its `role_bindings` resolve through C2
to live destination-eligible P6 fields.

**Produces** ordinary fact-backed levels: `dimension_role` set, `dimension` set, `expected_values[]`
populated. This is the **only** layer whose nodes can reach `confidence_class = exact fact match`
and `review_policy = auto_eligible` at their own level (§5.3).

**Falls through to layer 2 when** no applicability row matches — which is exactly the live Site-E
eligibility reason, `accepted_group_fits_no_existing_template`
(`src/llm_harness/vocabulary.py:137`). No new trigger is invented.

Note: a *partial* match is layer 1, not layer 2. If one dimension of a matching row resolves and
another does not, the row still applies at reduced depth — §5.8's uneven depth is legal by
construction, and `refinement_disposition = shallow-by-choice | refine-later` records why.

### Layer 2 — Widened vocabulary (template-local levels)

**Fires when** layer 1 found no applicable row, §5.7's custom-template call is eligible, and the
group is not privacy-blocked from a model call (§8.4, P7 gate).

**Produces** a `TemplateDefinition` proposal whose dimensions are a mix of `schema-field` and
`template-local` tiers (§4). Approved template-local levels become nodes with `dimension = null`,
`expected_values = []`, and one child per accepted group in the partition (§2.3).

**Falls through to layer 3 when any of:**

- Site E returns `ABSTAIN` (`Unknown` claim) or `WEAK`;
- Site E returns `REJECT` (schema invalid, uncited dimension, borrowed field key — §4.3);
- P8 is unavailable (`ValidationUnavailable`) or the call was budget-deferred (§8.6 — which must
  render as `deferred`, **never** `divergent`, per P10 SPEC:192);
- any C-gate or V-check fails, producing *"a deterministic report and no nodes"*
  (`TEMPLATE-BUILDING-HANDOFF.md` step 6);
- the proposal materialises but the user declines it — §5.7: a valid template *"cannot ... become
  active merely because it is syntactically valid"*, and P10 Done-means 8: *"A valid template is
  inert until approved."*

### Layer 3 — Residual (§7)

**Fires for** every file not resolved by layers 1–2, plus every file that reaches placement and
abstains. §7.1, canonical: *"These files should not be treated as errors, and they should not be
thrown into one global Misc, Other, or Unsorted folder."* Detail in §8.

### 3.1 The procedure, ordered

```text
INPUT: accepted group G, plan version V

L1  applicable_rows := published TemplateApplicability rows where
        uses_schema is active on G  AND  C3 proves applicability from G's evidence
    if applicable_rows non-empty:
        compose (C1–C8), materialise, V1–V6, present for approval
        -> approved  => LAYER 1 nodes (dimension set, expected_values populated)
        -> declined  => go to L3           # user said no; do not retry with a model
        -> C/V fail  => go to L2           # a real recipe exists but does not fit this branch
    else:
        go to L2

L2  if G is model-eligible under P7's gate at the current operation mode:
        build Site-E dossier   (allowed_vocabulary = allowed_vocabulary_for(catalogue, uses_schema))
        run P8 run_call
        -> ACCEPT_DIRECT | ACCEPT_CONTEXT_SUPPORTED:
               classify each dimension into schema-field / template-local  (§4.2)
               compose: C2 for schema-field dimensions only               (§4.4)
               materialise: fact values for schema-field levels;
                            accepted-group partition for template-local   (§2.3)
               V1–V6, with V4 and V6 load-bearing for template-local      (§2.2, §2.3)
               present for approval; a template-local level is presented
                 with its "accepts no automatic placement" declaration    (§5.5)
               -> approved => LAYER 2 nodes
               -> declined or V-fail => go to L3
        -> WEAK | REJECT | ABSTAIN | ValidationUnavailable | deferred => go to L3
    else:
        go to L3                                                          # privacy_blocked

L3  every unresolved member of G enters the §7.5 residual surfacing screen,
    counted in a named review set, with the reason it arrived               (§8)
```

**One rule binds the whole procedure:** a layer never re-runs after the user declines its output.
Declining is a §8.7 negative example, not a retry signal.

---

## 4. The widening contract

### 4.1 What `allowed_vocabulary` contains at Site E — **unchanged**

> **Contract W1.** `Dossier.allowed_vocabulary` at `call_site = E_template` is, and remains, the
> union of the `allowed_fields` of the published `TemplateApplicability` rows for **exactly one**
> `uses_schema`. It is computed by **P10** (`allowed_vocabulary_for`), never unioned across schemas,
> and never extended with role names, node ids or model-authored strings.

P10's docstring stays true word for word. `test_the_allowed_vocabulary_is_the_rows_fields_and_nothing_wider`
stays, unedited (§11).

### 4.2 What changes: the gate stops being a rejection and becomes a **classifier**

> **Contract W2.** Site E no longer rejects a proposal because a dimension name is outside the
> closure. It **classifies** each dimension:
>
> | condition | tier |
> |---|---|
> | `name ∈ dossier.allowed_vocabulary` | `schema-field` — fact-backed, C2 applies |
> | `name ∉ allowed_vocabulary` and `name` is a live P6 field key | **REJECT** — a borrowed field (§4.3) |
> | `name ∉ allowed_vocabulary` and `name` is not any P6 field key | `template-local` — label only |
>
> The payload must carry the tier explicitly, per dimension: `"scope": "schema-field" | "template-local"`.
> **A dimension claiming `"scope": "schema-field"` whose name is outside `allowed_vocabulary` is a
> REJECT.** That is the model asserting a field it was not given, and it is exactly the failure the
> old whole-payload gate existed to catch. The old gate's protective force is preserved intact; only
> its blast radius changes.

### 4.3 The borrowed-field guard, and where it lives

A model must not write `target_school` as a "template-local" dimension inside a `photos` branch. That
is not a novel label; it is a field belonging to another schema, and admitting it would let the
one-row-one-schema rule be evaded by relabelling.

> **Contract W3.** The borrowed-field check is performed by **P10's own injected
> `TemplateDependencies.schema_validator`** (`PLAN.md:5466`), which already holds the
> `TemplateCatalogue` and can reach P6's field catalogue. A `template-local` dimension whose name is
> a live P6 field key returns `False` → P8 emits `SCHEMA_INVALID`.
>
> **This adds no field to `Dossier` and no change to P8's frozen record.** It is a deny check inside
> an authority P10 already owns, which is the correct home: P8 owns the harness, P10 owns the
> catalogue (`PLAN.md:5535-5545`, and P10 SPEC G-P8).

### 4.4 What evidence a template-local dimension must carry

All four already exist; only the fourth is new.

| # | Requirement | Enforced by |
|---|---|---|
| E1 | Its `evidence_ref` is in the response's own `citations`, and those citations resolve to released dossier evidence | `template_validation.py:112-113` + `check_citations` — **live, unchanged** |
| E2 | Its `name` is in the payload's own `allowed_fields` | `_dimensions_are_well_formed`, `PLAN.md:5401` — **live in plan, unchanged** |
| E3 | Its level carries a `retrieval_justification` | `template_validation.py:120-135` — **live, unchanged** |
| E4 | It names an **accepted-group partition**: every child it proposes corresponds to an accepted P9 group id or an existing folder adopted under §5.10 | **new**, P10 materialisation (§2.3) |

§5.7, canonical, requires the generated template to *"cite the file facts that justify each proposed
dimension, and explain why each level improves retrieval."* E1 and E3 are that sentence. E4 is
§5.4's *"user-confirmed groups, and accepted labels."*

### 4.5 What a template-local dimension may **never** do — the P6 boundary statement

> **Contract W4 — what remains unassertable.** A template-local dimension:
>
> 1. **never becomes a P6 field.** `fields` rows are added only by the §9 promotion path. §3.12,
>    canonical: *"The system may create new values when it sees a new course, project, company,
>    university, or event, but it should not invent new fields automatically."*
> 2. **never produces a `values` row.** Its child labels are group labels and existing folder names,
>    which are not fact values.
> 3. **never appears in `expected_values[]`.** There is no `field` to write, so the node's
>    `expected_values` is `[]` and its `dimension` is `null`.
> 4. **never widens any other Site's `allowed_vocabulary`** (§1.3). Site A's fact allow-list, Site
>    B's value closure, Site C/D's node-id sets are untouched.
> 5. **never becomes a canonical fragment from inside a model call.**
>    `TEMPLATE-BUILDING-HANDOFF.md`: *"it cannot publish or propose a new canonical fragment.
>    Repeated local dimensions become fragment candidates only in the later human-reviewed synthesis
>    pass."* Enforced today by `FORBIDDEN_PUBLISHING_KEYS` (`PLAN.md:5352`+) →
>    `FRAGMENT_PUBLICATION_ATTEMPTED`.
> 6. **never yields an automatic placement at its own level** (§5.3).
> 7. **never bypasses V1–V6.** V4 (author-as-collector) and V6 (empty branches) are specifically
>    load-bearing for it, because C2 no longer guards it (§2.2, §2.3).

### 4.6 C2, restated

> **Contract W5.** C2 runs for every `schema-field` dimension, unchanged, both at routing and at node
> build. For a `template-local` dimension, `ResolvedDimension.field_ref` is `null` and C2 is **not
> called** — calling it would be asking P6 to define something that is deliberately not a field. A
> `ResolvedDimension` with `field_ref = null` and `scope != "template-local"` is a composition
> failure, so the null can only arrive through the declared path.

---

## 5. What placement does with a template-local dimension (§6)

This is the hard question. The honest answer, stated plainly, is that such a node **can** be placed
into — but only through one specific signal, and where that signal is absent it accepts nothing and
must say so at freeze rather than at placement time.

### 5.1 What is actually matched

P11 SPEC:127 — `expected_values[]` is *"the `field = value` assertions a node makes, matched against
`matching_facts`"*, and `matching_facts[]` is `{file_fact_id, field, value, reliability,
evidence_ref}` (P11 SPEC, placement decision record) — P6 facts. A template-local node's
`expected_values` is `[]`, so **it contributes zero `matching_facts`**.

It is not thereby invisible. Three things still hold:

1. **It inherits its ancestors.** The §6.1 profile carries `parent_context[]` — *"ancestor + child
   labels, dimensions and expected values"* (P10 SPEC profile table). A template-local node retrieves
   everything its parent retrieves. It is never *worse* than the parent.
2. **§6.3 lists six retrieval drivers and only the first is facts.** Canonical: *"Accepted group
   membership should retrieve the branch that was created from that group. Graph relationships should
   retrieve nodes containing the group's anchor files or related accepted members. Structural
   relationships should retrieve nodes that contain a version family, duplicate family, archive
   family, photo event, or derived document set. Full-text and OCR embeddings should retrieve
   semantically compatible node profiles ... Existing curated folders and user-entered labels should
   influence retrieval because they represent the user's vocabulary."*
3. **The index is built over the profile, not over `expected_values`.** P11 SPEC Contract-out §2
   lists the entry fields literally from §6.2: *"template fields, accepted group labels,
   user-approved display name, representative member files, anchor excerpts, known document types,
   parent and child context, and explicit user edits."* A template-local node has accepted group
   labels, representative files and anchor excerpts. It indexes.

### 5.2 The sibling problem — the thing that actually decides it

Retrieval is not the binding constraint. **Discrimination between siblings is.**

Every sibling under a template-local level asserts the same ancestor facts and no fact of its own. So
facts cannot separate them, and `two_condition.margin_over_next` is measured over non-fact signals
alone. Exactly one non-fact signal can separate siblings reliably, and the design names it:

- **Accepted group membership.** §6.3: *"Accepted group membership should retrieve the branch that was
  created from that group."* If the level's siblings are one-per-accepted-group — which E4 (§4.4)
  requires — then a file that is a member of group *g* retrieves the sibling built from *g* and not
  its neighbours. This is a real, recorded, non-semantic signal.

And exactly one cannot, and the design says so:

- **Embeddings.** §6.5, canonical: *"The group must still be supported by multiple independent
  signals. **A semantic embedding alone is insufficient.**"* and *"A target file connected only by
  generic similarity or one high-frequency entity must remain uncertain rather than being absorbed
  into an approved node."* P11's record already carries the outcome for this:
  `abstention_reason = semantic_only`.

### 5.3 The rule

> **Contract P1 — placement into a template-local level.**
>
> **(a)** A file that is an accepted member of the P9 group a sibling was built from places into that
> sibling. `group_support.membership` carries the basis; `confidence_class = context-supported group
> match`; `evidence_type` is at best `context-supported`.
>
> **(b)** Such a placement is **never** `confidence_class = exact fact match` and **never**
> `evidence_type = direct | validated` *at that level*, because there is no fact at that level. It is
> therefore never `review_policy = auto_eligible` at that level. This is derived, not invented: P8's
> own machinery sets `requires_review = True` on every `ACCEPT_CONTEXT_SUPPORTED`
> (`src/llm_harness/template_validation.py:49-50`, `_rewrite`), and P11 already applies the same
> shape to `user-attached` memberships — *"a decision resting on a `user-attached` membership is never
> `review_policy = auto_eligible`"* (P11 SPEC).
>
> **(c)** A file that is **not** a member of any of the siblings' groups has no signal that
> discriminates them. Retrieval returns the parent and every sibling with equal support. Per §6.7 the
> engine takes the **approved shallower path** — canonical: *"If the only available deeper path would
> require inventing a term, it should choose an approved General fallback under the meaningful parent,
> or abstain"* and *"The model should never fill a missing slot merely because a complete-looking path
> is aesthetically preferable"* — recording the template-local level in
> `decision_depth.unsupported_levels[]`. If no parent is legal, it abstains with
> `abstention_reason = semantic_only` (or `low_margin`).
>
> **(d)** **A template-local level therefore accepts new files essentially never.** It organises the
> group it was built from; it is not a magnet for future material. That is the honest behaviour and it
> must be stated in the UI, not discovered.

### 5.4 The degenerate case, named

If a template-local level's siblings are **not** a group partition — if the model cut the branch by a
distinction that exists only in its reading of the text — then E4 (§4.4) rejects it at proposal time,
and if it somehow materialises, V6 (*"produces empty branches"*) or V2 (*"creates meaningless
one-child levels"*) kills it. **A semantic-only cut never becomes a node.** This is the single most
important consequence of §2.3 and it is why the design does not need a new placement rule.

### 5.5 The declaration — a node that accepts nothing must say so

The lead's framing is right: *a node that quietly accepts nothing is worse than one that declares it.*
The declaration needs **no new field**:

> **Contract P2.** `dimension = null` together with `expected_values = []` **is** the declaration. It
> is already in P10's published node record (SPEC:224-227) and already in P11's Contract-in
> (P11 SPEC:124). Two obligations follow:
>
> - **P10, at review time**, renders a template-local level distinguishably in the canvas and states
>   in its `explanation` that the level organises the named accepted groups and will not receive
>   automatic placements. §5.2 fixes the form: an explanation, never a confidence score. P10
>   Done-means 5 already requires every node to carry a non-empty `explanation`.
> - **P11, at placement time**, treats `dimension = null` as sufficient to refuse
>   `review_policy = auto_eligible` at that level, without re-deriving anything from
>   `expected_values`.

### 5.6 Freeze (§5.12) and re-projection (§8.8) — survives, with no special case

**Freeze.** A template-local node is an ordinary node record. It has `node_id`, `node_type =
proposed`, `display_label`, `parent_node_id`, `associated_group_ids[]` (non-empty by E4),
`template_context` pinning `{template_id, template_version, dimension_index}`, `dimension_role` set,
`dimension = null`, `expected_values = []`, `explanation`, `accepts_placement = true`. §5.12's
mandatory field list is satisfied. Freeze legality is *"enforceable by ID lookup alone"* (P10
Done-means 3) and an ID lookup does not consult `dimension`. **Freeze needs no change.**

**Re-projection.** The template-local *role name* lives in `TemplateDefinition.dimensions[].role_ref`
at a pinned version, and P10 Done-means 16 already guarantees *"New template, fragment, or
applicability versions never migrate an approved binding."* On a new plan version, P11's rule applies
unchanged: *"Decisions whose destination node no longer exists are marked as requiring renewed review
and appear in the version diff"* and *"Decisions are never silently remapped onto a renamed or
relocated node"* (P11 SPEC, Plan versioning). **Re-projection needs no change.**

The one thing to check and it already holds: §8.8 requires the evidence database to be shared across
versions while *"the destination tree and user policy define which projections are valid in each
version."* A template-local level writes nothing to the evidence database (Contract W4.1–W4.3), so
dropping it in version *n+1* loses no evidence. That is precisely why the widening is cheap to undo.

---

## 6. Privacy (§8.4) and the protected-container rule

A template-local dimension name is **model-authored from cited file content**. `Oncology-Referral` is
a realistic output. Four rules, three of them already present.

**PR1 — V5 already applies.** §5.7: the engine validates that the template does not *"expose
protected information"*; P10 SPEC:493 is V5. A template-local dimension name, and every child label
derived from a group label, is subject to V5 against the handling classes of the evidence it cites
and of the members beneath it. A failing fixture for V5 driven by a **template-local** name is
required (§10, T9).

**PR2 — the dossier boundary already applies.** §8.4, canonical: protected material *"should not be
included in cloud-model prompts by default, should not display raw content in general group
summaries"*. P7's gate decides what reaches the Site-E dossier at all; a name the model never saw
evidence for cannot be produced, and E1 (§4.4) ties every dimension to released evidence. P10 SPEC
states the boundary rule: *"Protected profiles are redacted at the boundary, not at the renderer."*

**PR3 — the UI rule already applies.** §8.4: *"A summary such as '11 protected identity records' may
be safe to show, while a visible list of passport filenames on a shared screen may not be. Protected
branches should have configurable redaction in the canvas and review screens."* A template-local
level under a protected branch inherits that redaction; nothing here weakens it.

**PR4 — the new one, and it is narrow.** A branch **label is written to disk** by P12 (P10 publishes
`root_anchor` + the `display_label` chain; P12 composes the path). Every rule above governs prompts
and screens. Disk is a third surface with a different threat model: a folder name is visible to
anyone with the volume, to backup software, and to sync clients, with no redaction layer available.

> **Contract PR4.** A `template-local` dimension name, and any child label a template-local level
> derives, must not be produced from evidence whose handling class is `sensitive personal` or
> `highly sensitive or credential-bearing`. Where the level's members carry such a class, the level
> is either named by the user or not proposed. Enforced at proposal validation (P10's
> `schema_validator` can read the released evidence's handling class) and again at V5.

Whether the design *intends* disk-visible folder names to be governed by §8.4 at all is **OPEN-3**
(§12) — PR4 is stated as a requirement because the safe reading is cheap and the unsafe reading is
irreversible, but the design does not decide it.

---

## 7. What the user actually sees

The owner's ruling only pays off if a template-local branch is *legible* at review time. Three
surfaces, all governed by rules the design already fixes.

**At tree design (§5.10, §5.2).** A template-local level renders as an ordinary proposed branch with
one difference: its `explanation` names the accepted groups it organises and states that it will not
receive automatic placements later. §5.2 fixes the form — an explanation, never a confidence score —
and P10 Done-means 5 already requires *"Every node carries a non-empty `explanation`, and no canvas
surface exposes a confidence score."* §5.10's rule that existing nodes render in one style and
uncommitted suggestions in another applies unchanged.

**At freeze (§5.12).** §5.11 already licenses an incomplete tree: *"A branch can be accepted even if
some files remain unresolved"* and *"The goal is to give the user a good enough structural gist of
the corpus so that only a limited number of high-leverage changes remain, not to force perfection
before the user can see the proposed tree."* A template-local branch is exactly that — a good-enough
gist for material nobody has modelled. It must not be presented as more.

**At placement review (§6.11, §7.5).** A file that could not enter a template-local sibling appears
with the reason, not silently. §7.5 requires each residual set to show *"the reason the system could
not safely place the files through the normal pipeline"*, and §6.4 requires the explanation to
reflect the actual basis *"rather than falsely claiming that the course code was found inside the
homework itself"* — the same discipline applies here: the explanation for a template-local placement
says *member of the accepted group this branch was built from*, never *matches this folder*.

**What is NOT decided here:** the phrasing. P10 SPEC defers *"Default warning copy and explanation
phrasing"* — *"§5.2 fixes the form ... the phrasing set is hand-authored."* This section fixes what
must be conveyed, not the words.


---

## 8. The residual floor (layer 3)

### 8.1 What reaches §7

Everything listed in §3's fall-through conditions, plus every placement that abstained. §7.1 fixes
the posture, canonical: *"These files should not be treated as errors, and they should not be thrown
into one global Misc, Other, or Unsorted folder."*

**The floor is a counting obligation, not a folder.** §7.5, canonical:

> *"Your main structure is ready. We found 146 files that do not fit a confirmed group or approved
> destination."*

and the sets are named by *reliable characteristics* — canonical gives eight examples including
*"20 files with no extractable text, usable metadata, or graph relationship"* and *"16 files with
multiple plausible destinations."* Each set *"should display representative examples, file-type
distribution, age range, available OCR or text evidence, sensitivity status, any weak graph
neighbors, and **the reason the system could not safely place the files through the normal
pipeline**."*

> **Contract R1.** That last clause is where layer-2 failure becomes visible. A file that reached
> §7 because the custom-template path failed carries that as its reason — distinguishing
> *"no template existed and the proposal was rejected"* from *"the proposal was approved but this
> file did not fit any sibling"* from *"budget deferred"*. P11's `abstention_reason` and
> `deferred_stage` already carry the vocabulary; `deferred_stage` *"must render differently from an
> evidential abstention"* (P11 SPEC).

### 8.2 What the residual stage may and may not do with novel material

§7.2: the residual library *"prevents the LLM from creating arbitrary folders such as `Random PDF
Things`, `Important Screenshot`, `Miscellaneous Documents`, or `Travel/Gate B12`."* §7.7: the model
*"is not asked to invent a folder. It is asked to choose from a controlled action set"* of eight
actions. §7.4: enabled residual branches *"become legal nodes in the frozen destination tree. The LLM
may choose among them later, but it may not create additional generic destinations."*

**Layer 3 is deliberately not adaptive.** Layer 2 is where novelty is expressed; layer 3 is where
unexpressible material is *held safely and counted*. Conflating them would reintroduce the invented
folder the residual library exists to prevent.

§7.3's ninth template, **user-defined residual areas** — *"Things to Read, Ideas, Shopping Research,
Memes, Travel, Receipts to Process, Clips, or Stuff to Sort, because residual organization is highly
personal and should not be dictated by a universal taxonomy"* — is the user's own escape hatch and is
authored by the user, not the model (P10 SPEC Deferred: *"User-defined residual areas (§7.3) are
authored by the user, not shipped."*).

### 8.3 How a recurring residual pattern becomes a real domain

This is where *"domains encapsulate everything"* is actually achieved, and §5.7 authorises it in one
clause, canonical:

> *"expand the library as recurring user needs and corpus evidence justify additional coverage"*

The mechanism the design already has is §8.7 correction learning, which is explicitly scoped:

> *"These actions should become local learning records **with scope**. A correction can apply only to
> one file, to one group, to one destination node, to one template, to one domain, or to the entire
> corpus."* and *"if the user repeatedly places product screenshots under Reference Clips, the
> product can learn a corpus-level preference for that residual destination."*

> **Contract R2.** A residual set whose members repeatedly receive the same user-authored destination
> is a **domain candidate**, surfaced to the owner (not the user) as evidence for §9's promotion path.
> It is never automatic. §8.7 also fixes the limit: *"The product should not silently train a global
> model on a user's private corpus. Any cross-user learning should be opt-in, privacy-preserving, and
> limited to template-level or rule-level improvements rather than raw personal documents."*

---

## 9. The promotion path — human-reviewed, never automatic

Three distinct promotions, three distinct authorities. Nothing here runs at runtime.

| # | From | To | Authorised by | Reviewer |
|---|---|---|---|---|
| **PM1** | a recurring `template-local` dimension | a **canonical `TemplateFragment`** | `TEMPLATE-BUILDING-HANDOFF.md`: *"Repeated local dimensions become fragment candidates only in the later human-reviewed synthesis pass."* and step 3: *"Create a fragment only when at least two reviewed contexts share stable semantics and compatible constraints."* | template-building pass |
| **PM2** | a `template-local` dimension that needs to carry fact values | a **declared P6 field** on a schema | §3.12: *"it should not invent new fields automatically"* — **"automatically" is the operative word; a reviewed addition is not forbidden** | P6 field-catalogue owner |
| **PM3** | a recurring residual pattern | a **new domain schema + template rows** | §5.7: *"expand the library as recurring user needs and corpus evidence justify additional coverage"* | owner, via `planning/domains/` |

Sequencing matters and it is one-directional: **PM2 is what moves material from layer 2 to layer 1.**
A template-local level becomes fact-backed only when a field exists for it; then C2 resolves, the
level gets `expected_values`, and placement into it becomes automatic-eligible for the first time.
PM1 without PM2 gives reuse but no placement. **PM2 is the promotion that matters for the owner's
"encapsulate everything" goal**, and the 17 field-less schemas (§1.4) are its standing backlog.

> **Contract PR-A — nothing is promoted without a recorded human action.** Each of PM1/PM2/PM3
> requires a review artefact, and none may be triggered by a threshold crossing alone. §5.7's
> governing sentence applies to all three: *"Structured output constraints and schema validation
> should enforce the required template shape, but semantic validation and user approval remain
> necessary because a technically valid LLM-generated template can still be a poor organization
> design."*

> **Contract PR-B — promotion never rewrites a frozen tree.** P10 Done-means 16: *"New template,
> fragment, or applicability versions never migrate an approved binding; adoption requires a new
> draft and explicit approval."* When PM2 gives a template-local level a real field, existing frozen
> nodes keep `dimension = null` until the user adopts a new plan version. §8.8: *"A new plan should
> never silently reclassify or move old files."*

---

## 10. Test obligations

Phrased as assertions. Each names the module that should own it. These are **obligations on the
implementing agents**, not tests written here.

**Widening**

- **T1** — *an evidence-backed novel dimension is accepted.* Given a Site-E dossier whose
  `allowed_vocabulary` is `()` (a field-less schema) and a proposal whose single dimension is
  `{"name": "matter_number", "scope": "template-local", "evidence_ref": <cited>}`, the verdict is
  `ACCEPT_DIRECT` or `ACCEPT_CONTEXT_SUPPORTED`, **not** `REJECT`. *(P8 Site E.)*
- **T2** — *a claimed schema-field outside the closure is still rejected.* The same proposal with
  `"scope": "schema-field"` is `REJECT` / `REJECTED` / `may_propose=False`. *(P8 Site E.)*
- **T3** — *a borrowed field key is rejected.* A `template-local` dimension named `target_school`
  inside a `photos` proposal fails `template_schema_validator`, and P8 reports `SCHEMA_INVALID`.
  *(P10 schema validator + P8.)*
- **T4** — *an uncited template-local dimension is still rejected.* Removing its `evidence_ref` from
  the response's citations reproduces today's `REJECT` at `template_validation.py:112-113`,
  unchanged. *(P8 Site E — a regression guard on a gate that must not be relaxed.)*

**The P6 boundary**

- **T5** — *nothing becomes a P6 fact by this route.* Running the accepted layer-2 path end to end
  over a fixture corpus leaves `fields`, `values` and `file_facts` byte-identical. This is P10
  Done-means 4 (*"Freeze mutates no evidence"*) extended to cover the template-local path
  explicitly. *(P10 integration.)*
- **T6** — *Site A's allow-list is unmoved.* With a template-local dimension accepted at Site E, a
  Site-A fact proposal for the same key is still `REJECT` with `FIELD_NOT_IN_ACTIVE_SCHEMA`
  (`fact_validation.py:204`). *(Cross-site — the single most important test in this document.)*
- **T7** — *the node carries no assertion.* A materialised template-local node has
  `dimension is None` and `expected_values == []`. *(P10 node build.)*
- **T8** — *no fragment is published from a branch call.* A payload carrying any
  `FORBIDDEN_PUBLISHING_KEYS` key alongside a template-local dimension yields
  `FRAGMENT_PUBLICATION_ATTEMPTED`. *(P8 / P10 — existing gate, new companion fixture.)*

**Privacy**

- **T9** — *protected material never appears in a dimension name.* A template-local dimension whose
  cited evidence carries a sensitive handling class fails validation (PR4) and, independently, fails
  V5. Two assertions, because two layers must both hold. *(P10 schema validator; P10 V5 fixture.)*

**Materialisation**

- **T10** — *a semantic-only cut produces no nodes.* A template-local dimension whose proposed
  children do not correspond to accepted group ids fails E4, and a fixture that reaches
  materialisation anyway is killed by V6 with an explained report and zero nodes. *(P10 — E4 gate
  and the V6 fixture.)*
- **T11** — *V4 still guards §3.8 without C2.* A template-local dimension that partitions by author
  or producing organisation fails V4. *(P10 V4 fixture — required because C2 no longer runs for
  this level.)*
- **T12** — *C2 is unweakened for schema-field dimensions.* A `schema-field` dimension whose
  `field_ref` P6 does not define, or marks not destination-eligible, still raises through
  `resolve_role_to_field` at both call sites (`PLAN.md:2530`, `PLAN.md:8009`). *(P10 — regression
  guard.)*

**Placement**

- **T13** — *a node with an unmatched dimension declares itself review-required.* A placement whose
  chosen node has `dimension is None` has `review_policy != "auto_eligible"` and
  `confidence_class != "exact fact match"`. *(P11.)*
- **T14** — *a non-member abstains or places shallow.* A file that is a member of none of the
  siblings' groups either places at the parent with the template-local level listed in
  `decision_depth.unsupported_levels[]`, or abstains with
  `abstention_reason in ("semantic_only", "low_margin")`. It never lands in a sibling. *(P11.)*
- **T15** — *a member does place, with the right basis.* A file that is an accepted member of the
  group a sibling was built from places into that sibling with
  `confidence_class == "context-supported group match"` and `group_support.group_id` naming it.
  *(P11.)*

**Freeze and versioning**

- **T16** — *a template-local node freezes and re-projects.* It survives freeze, appears in the
  §8.8 node-level diff, and on a new plan version that drops it, every decision naming it is marked
  for renewed review rather than remapped. *(P10 + P11.)*

**Promotion**

- **T17** — *nothing is promoted to canonical without review.* No runtime code path creates a
  `TemplateFragment`, a `fields` row, or a `planning/domains/` schema row. Assert by absence: a grep
  over the runtime packages finds no writer for any of the three, and P10 runtime imports nothing
  from `planning/domains/` (the existing P6 Task-25 assertion pattern in `src/facts/domains.py`).
  *(Architecture test.)*

---

## 11. What changes in the P10 plan, by grep anchor

| # | Anchor | Change |
|---|---|---|
| **A** | `planning/parts/P10-tree-design-freeze/PLAN.md:5548` — `def allowed_vocabulary_for` | **No change.** Docstring stays true: it is still one schema's fields, still never unioned. Contract W1. |
| **B** | `PLAN.md:5117` — `test_the_allowed_vocabulary_is_the_rows_fields_and_nothing_wider` | **Stays, unedited, with a companion.** It tests `allowed_vocabulary_for`'s *closure*, which does not change. Its docstring's second sentence — *"P8's Site E rejects any dimension whose `name` is outside `Dossier.allowed_vocabulary`"* — becomes false and must be corrected to *"P8's Site E classifies each dimension by whether its `name` is inside `Dossier.allowed_vocabulary`."* Companion test: `test_a_schema_with_no_declared_fields_still_admits_a_template_local_dimension`. **Do not narrow or delete it** — it is the guard against the widening 43 §9 asked for, and that guard is still needed. |
| **C** | `src/llm_harness/template_validation.py:101-103` | The whole-payload rejection becomes the Contract-W2 classifier. Reject only when a dimension claims `"scope": "schema-field"` and its name is outside the closure. **P8 record shapes are untouched** — `scope` is a payload key, not a `Dossier` field. |
| **D** | `PLAN.md:5401` — `_dimensions_are_well_formed` | Require `scope ∈ {"schema-field","template-local"}` on every dimension. Add the Contract-W3 borrowed-field deny check. Keep the existing `name ∈ payload["allowed_fields"]` check (E2). |
| **E** | `PLAN.md:5055` — `test_template_local_dimensions_are_allowed_and_are_not_fragments` | **Keep the intent, fix the fixture.** It must add `"scope": "template-local"` to the `lens` dimension, and must gain an assertion that the same payload is now also accepted at P8's Site E — which is what makes the plan self-consistent. As written today it passes P10's validator and would be rejected by P8, and that contradiction is live (§1.6b). |
| **F** | `PLAN.md:5081` — `test_a_dimension_that_is_not_in_allowed_fields_is_rejected` | **Stays.** Its subject is the payload's *own* `allowed_fields` self-consistency (E2), not the dossier closure. Its docstring's claim — *"A dimension the row does not allow is a field the model minted"* — should be narrowed to say it is an *internally inconsistent payload*, since minting is now caught by W3 instead. |
| **G** | `PLAN.md:2530` — `resolve_role_to_field` | **No change to the function.** Its callers change: it is called only for `scope = "schema-field"` dimensions (Contract W5). Its two error messages remain exactly right for what it still guards. |
| **H** | `PLAN.md:8009` — the node-build C2 call | Guard the call on `dimension.field_ref is not None`. For a template-local dimension, skip the value read (`preferred_value_for`) entirely and build the level's children from `associated_group_ids` + group labels (§2.3, E4). Emit `LevelEvidence` with `field_ref = None`. |
| **I** | `PLAN.md:5352` — `TEMPLATE_PAYLOAD_KEYS` / `FORBIDDEN_PUBLISHING_KEYS` | `TEMPLATE_PAYLOAD_KEYS` unchanged — §5.7's nine keys are still the payload. `FORBIDDEN_PUBLISHING_KEYS` unchanged and now explicitly load-bearing for layer 2 (Contract W4.5, test T8). |
| **J** | `src/llm_harness/fixtures.py:592` — `_E_VOCAB = ("year", "event")` | Flagged, not changed here. The live fixture's members are *dimension* names; `allowed_vocabulary_for` would supply *field* keys (`capture_year`). Someone must reconcile them, and under Contract W2 the mismatch is no longer fatal (an unrecognised name becomes `template-local` rather than a rejection) — but a fixture whose Photos dimensions silently reclassify as template-local would be a misleading fixture. **OPEN-1.** |
| **K** | P10 SPEC:224-227 (node record), :500 (C2), :489-494 (V1–V6) | SPEC text needs three sentences added, not restructured: that `dimension = null` is the declared template-local form; that C2 applies to schema-field dimensions only; that V4 and V6 are load-bearing for template-local levels. |
| **L** | P10 Done-means | Add: *"A field-less schema can still produce a reviewable branch design."* This is the owner's ruling stated as an acceptance criterion, and without it the widening has no completion test. |

Nothing in P11's plan changes. Every consequence in §5 falls out of `expected_values = []` and
machinery P11 already has (`confidence_class`, `group_support`, `abstention_reason`,
`decision_depth.unsupported_levels[]`). **That is the strongest evidence the design is right:** the
correct widening required no new placement concept.

---

## 12. OPEN

Items the design does not decide. Each names what would settle it.

- **OPEN-1 — Site E's payload contract: dimension names or field keys?**
  `src/llm_harness/fixtures.py:592` uses `("year", "event")` (§5.4 template dimensions);
  `allowed_vocabulary_for` would supply `("capture_year", "event")` (§3.11 fields). §5.7 lists both
  *"allowed fields"* and *"recommended folder dimensions"* as separate payload keys and never says
  the dimension names must equal the field keys. **Settled by:** P10 and P8 agreeing one answer, and
  reconciling `_E_VOCAB` with `allowed_vocabulary_for`. Under Contract W2 a mismatch is no longer a
  crash, which makes it *easier* to leave wrong — so it must be settled deliberately.

- **OPEN-2 — May a template-local level ever be promoted *within one plan version*?**
  If the user, reviewing a template-local level, tells the product "this is really a `matter_number`",
  §8.7 records it as a scoped correction — but §3.12 forbids inventing a field automatically and §9's
  PM2 requires a reviewed catalogue change. Whether the user's own statement counts as that review,
  for their own local corpus only, is undecided. **Settled by:** the owner ruling on whether P6's
  field catalogue is per-install extensible by the user. Note §8.7 leans toward yes for
  *preferences* (*"aliases, user vocabulary, destination preferences"*) and says nothing about
  fields.

- **OPEN-3 — Does §8.4 govern folder names on disk?**
  Every §8.4 protection is stated for prompts, group summaries, and the canvas/review screens. A
  branch label reaches disk via P12 with no redaction layer. §6 states PR4 as a requirement on the
  precautionary reading. **Settled by:** an owner ruling, or a design sentence extending §8.4's
  redaction rule to composed paths.

- **OPEN-4 — How many template-local levels may one branch carry?**
  §5.7's V3 (*"exceed practical depth limits"*) is depth, not composition. A branch that is
  *entirely* template-local is a branch with no fact-backed level anywhere — organisable, placeable
  only by group membership, and arguably a signal that the domain needs PM3 rather than a template.
  The design gives no cap and no warning threshold. **Settled by:** a §5.9 warning threshold
  (P10 Done-means 9 already requires thresholds to be configuration, not code), or an explicit
  "at least one fact-backed level per branch" rule. **Recommendation, not a ruling:** surface it as a
  §5.9 warning, do not forbid it — forbidding it would re-close the path for the 17 field-less
  schemas, which is the thing this document exists to open.

- **OPEN-5 — Does a template-local level count toward V2's "meaningless one-child levels"?**
  A template-local level over a single accepted group produces exactly one child. V2 would kill it.
  Whether that is correct (a one-child level *is* meaningless) or wrong (the single group is the
  whole point for a novel domain) is undecided. **Settled by:** P10 stating whether V2 counts
  children or counts *distinct partition sources*. **Note:** this is the most likely place for the
  widening to silently fail in practice — a novel domain often has exactly one accepted group.

- **OPEN-6 — Which of the 17 field-less schemas get fields, and when?**
  Layer 1 is the goal; PM2 is the path; the backlog is 17 schemas. `roster.json`'s own comment
  records that the J-IND expansion rows *"write NO field rows (PR-6, D1 unchanged) and mint NO
  canonical field keys; proposed fields belong to the R1c backlog."* **Settled by:** the owner
  sequencing R1c. Until then, layer 2 is the only path for 17 of 23 domains, which is exactly the
  condition that makes this document load-bearing rather than theoretical.

- **OPEN-7 — Does `metadata_only: true` interact with template-local?**
  `PLAN.md:5055`'s existing fixture marks `lens` as `metadata_only: True` *and* lists it in `levels`.
  §5.4 says metadata-only *"may never become a folder level"*, so the fixture is internally
  inconsistent. A metadata-only template-local dimension is harmless (it never materialises, so §2.3
  and §5 do not apply) but the fixture as written does not test what its name says. **Settled by:**
  P10 deciding whether `levels` means "folder levels" or "dimensions with justification"; the P8
  gate at `template_validation.py:120-135` reads it as the latter.

---

## 13. Re-verification

Every citation above is reproducible from these commands.

```bash
cd "/Users/jy/GRAPH AGENT"

# §1.1 the live gate
sed -n '99,120p' src/llm_harness/template_validation.py

# §1.2 the planned closure and its test
sed -n '5117,5124p;5548,5560p' planning/parts/P10-tree-design-freeze/PLAN.md

# §1.3 four gates, not one
grep -rn "allowed_vocabulary" src/llm_harness/*.py

# §1.4 six of twenty-three
python3 - <<'PY'
import json,glob,collections
c=collections.Counter()
for p in sorted(glob.glob('planning/domains/nodes/*.json')):
    d=json.load(open(p))
    if d.get('kind')=='schema': c[d['id']]=len(d.get('fields') or [])
print(sum(1 for v in c.values() if v), 'with fields of', len(c))
PY

# §1.5 C2, both call sites
sed -n '2530,2556p;8005,8012p' planning/parts/P10-tree-design-freeze/PLAN.md

# §1.6a "if any" on dimension and dimension_role
grep -n "the live P6 field to which" planning/parts/P10-tree-design-freeze/SPEC.md

# §1.6b/c the two live inconsistencies
sed -n '5055,5072p' planning/parts/P10-tree-design-freeze/PLAN.md
grep -n "_E_VOCAB = " src/llm_harness/fixtures.py

# §2.1 the disjoint allow-list
grep -n "field_key not in allowlist" src/llm_harness/fact_validation.py
grep -n "ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE" src/llm_harness/vocabulary.py

# §2.3 / §5.2 the two canonical sentences the design turns on
grep -c "those names emerge from validated facts, user-confirmed groups, and accepted labels" \
  planning/00-database-agent-product-design.md
grep -c "A semantic embedding alone is insufficient" \
  planning/00-database-agent-product-design.md
```

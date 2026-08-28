# 64 — What happens to the user's own work when the library changes underneath it

Date: 2026-08-28. Raised by the owner: *"the situation where the user changes the labels
and names and the template, and you need to reason and develop how that interacts with the
database and template and saved work — for the future, and make it dynamic."*

He is right that this is not handled, and it is a bigger hole than it looks.

Authority: `00-database-agent-product-design.md` remains canonical. Nothing here amends it;
`00` already requires that *"the user can reverse, remove, add, or flatten dimensions"* and
that labels *"reflect the user's vocabulary"*. This document works out what that costs once
the shipped library is allowed to change.

---

## 1. What exists today, verified

**A rename works, once.** `TREE_EDIT_ACTIONS` has fifteen members; `apply_review_action`
writes five of them — `accept`, `rename`, `ignore`, `add-scoped-general`,
`set-shared-material-policy` — and refuses the other ten **by name**, before writing anything,
because *"a silent no-op still opens a draft, and the user would see a new plan version that
changed nothing."* That refusal design is right and should not change.

**But four things are missing, and together they mean the user's work is not durable.**

| # | hole | evidence |
|---|---|---|
| 1 | `display_label` is assigned **from the catalogue** during routing; the rename lands afterwards, on the binding. Re-run routing and the catalogue's label is reassigned over it. | `routing.py`: `display_label=labels[role]`, where `labels` comes from the applicability rows' `RoleBinding.label`. Its own comment: *"the edit actions (`reordered`, `renamed`, …) belong to the binding, after the branch exists."* |
| 2 | There is no user-preference layer for **labels**. The one preference mechanism that survives versions covers **suppressions** only — "do not place here". | `placement/versions.py: learned_preferences_still_applicable` |
| 3 | The live chain feeds **no** user labels into candidate generation. | `tree_design/pipeline.py:481` — `user_labels=()` |
| 4 | **A frozen tree does not record which catalogue release built it.** A library upgrade is therefore not merely unhandled — it is *undetectable*. | `FrozenTree` = `plan_version_id · freeze_record · nodes · profiles · shared_material_policy · shared_material_policy_scope`. No `release_id`, no template-version set. No file in the repo mentions a catalogue upgrade path. |

(The `release_id` in `src/privacy/` is the **egress ledger** — which model call was authorised.
It is a different concept and is not this.)

**The failure a user would actually hit:** they rename *Course* to *Class*, because that is
what they call it. Later they edit one unrelated folder, or a library update ships. Routing
re-runs. The level is called *Course* again. Nothing tells them, and nothing recorded that
they had ever said otherwise.

---

## 2. The principle

**The catalogue is a proposal. The user's edits are facts.**

A proposal may be re-derived at any time; a fact may not be overwritten by re-derivation. This
is not a new idea in this product — P7 already carries it, where a record with
`basis="user"` outranks an inferred one of any reliability. The same precedence should govern
the tree, and for the same reason: the system's confidence in its own inference is irrelevant
against something the person actually said.

---

## 3. The stable key — the part everything else depends on

An overlay is only durable if it is keyed to something that survives the events that would
otherwise destroy it. Three candidate keys, two of which fail:

- **`node_id` — fails.** §8.8 mints a new one per plan version. This is precisely the bug the
  seam pass found in `learned_preferences_still_applicable`, where filtering on `node_id` made
  every preference silently stop applying at the first tree edit.
- **`template_id@version` — fails.** It is the packaging, and packaging is what an upgrade
  changes.
- **`(schema, role_ref, field_ref)` — holds.** It is the *vocabulary*, and the vocabulary is
  what both the catalogue and the user are talking about. A rename keyed this way means:
  *"whatever level shows my `subject` field in an `academic` context, I call it Class."* That
  sentence stays true across a re-route, a re-version, and a library upgrade, because none of
  those change what a `subject` is.

Structural edits (omit, reorder, flatten) take the same triple plus the branch's **origin
lineage** — the same identity `reproject` and the fixed `learned_preferences` already use.

**Consequence worth stating plainly:** a label overlay is per-schema, not global. Renaming
*Course* to *Class* in an academic context does not rename anything in a research context,
which is correct, and is the same reason `RoleBinding.label` lives on the applicability row
rather than on the definition.

---

## 4. Where the overlay applies

**At the end of routing, never at the start.**

Routing composes from the catalogue and the C1–C8 gates check that composition — that every
referenced record exists, that every dimension maps to a live field, that the order is acyclic,
that nothing is silently dropped. Those gates must go on judging **the recipe**, not the
recipe-as-the-user-rewrote-it, or a user rename could make a broken composition look valid.

So: compose, gate, then apply the overlay to the resolved dimensions as the last step. The
user's edit is the last word about presentation and never a way to smuggle a change past a
gate. A rename is already constrained to a display label and never a path fragment
(`templates.py`: *"a renamed level is a display label, never a path fragment"*), which is the
same instinct and should be preserved literally.

---

## 5. The upgrade contract

**5a. A frozen tree must record what built it** — the catalogue `release_id` and the
`(template_id, template_version)` set it actually used. Without this, an upgrade cannot be
detected, so nothing else in this section is possible. This is the smallest change in the
document and the one everything else waits on.

**5b. An upgrade never silently re-derives a level the user touched.** Where the new library
renames a level the user also renamed, **the user wins**, and the fact that the library
proposed something different is recorded, not discarded.

**5c. A structural conflict is surfaced, not resolved.** If the new library removes a level the
user had kept, or adds one that changes an order the user had set, that is a question for the
user, not a decision for the product. `00`'s own posture throughout is that a conflicting
signal produces abstention rather than an invented answer; an upgrade is the same situation
with a different source.

**5d. The explanation vocabulary already exists.** `diff.py` emits *added, removed, renamed,
re-parented, re-templated, re-ordered*. An upgrade should be presented in exactly those terms,
so that "what changed when I updated" and "what changed when I edited" read the same way.

**5e. Nothing moves because of an upgrade.** A library update changes proposals. It does not
move a file, and it does not silently re-freeze a tree.

---

## 6. Recording the honest limits

- **This does not make the user's edits a second catalogue.** The overlay holds what the user
  said about levels the catalogue offered. It is not a place to author new templates; that is
  `create-manually` and `adopt-existing`, two of the ten actions with no writer.
- **Ten of fifteen edit actions still have no writer** — `merge`, `split`, `nest`, `re-parent`,
  `reorder`, `delete`, `create-manually`, `adopt-existing`, `enable-residual`,
  `disable-residual`. Making renames durable does not make those exist. Every one of them will
  need the same overlay treatment when it is built, and the overlay should be designed to hold
  them rather than retrofitted per action.
- **The interaction between an upgrade and a *frozen* tree that P12 has already applied to disk
  is out of scope here.** Once folders exist on disk, a changed proposal is a migration
  question, not a design question, and P12 does not exist yet.

---

## 7. Where this sits in the plan

It is engine work, not post-engine work: it belongs with P10, before `63` §0's gate, because a
product that loses the user's renames is not a product whose engine is finished. **5a** (record
the catalogue release on the frozen tree) should land immediately — it is small, and every
other part of this document is blocked on it.
